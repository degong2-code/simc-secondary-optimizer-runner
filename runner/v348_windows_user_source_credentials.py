#!/usr/bin/env python3
"""Local operator-owned Blizzard/WCL credentials in Windows Credential Manager.

One CRED_TYPE_GENERIC entry is atomic for both credential pairs. Secrets are
never returned from the local web API, written to source receipts, printed,
or copied to subprocess environments. Non-Windows hosts have no persistent
fallback; legacy environment-variable discovery remains v216's responsibility.
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import json
import os
import re

SCHEMA="v348_windows_user_source_credentials_v1"
TARGET="SSfindout.SIMCSecondaryOptimizer.SourceAPI.v1"
FIELDS=("BLIZZARD_CLIENT_ID","BLIZZARD_CLIENT_SECRET",
        "WCL_CLIENT_ID","WCL_CLIENT_SECRET")
MAX_UTF8_BLOB=2560
CRED_TYPE_GENERIC=1
CRED_PERSIST_LOCAL_MACHINE=2
ERROR_NOT_FOUND=1168

class CredentialBlocked(ValueError):
    pass

class _FILETIME(ctypes.Structure):
    _fields_=[("dwLowDateTime",wt.DWORD),("dwHighDateTime",wt.DWORD)]

class _CREDENTIALW(ctypes.Structure):
    _fields_=[
        ("Flags",wt.DWORD),("Type",wt.DWORD),
        ("TargetName",wt.LPWSTR),("Comment",wt.LPWSTR),
        ("LastWritten",_FILETIME),
        ("CredentialBlobSize",wt.DWORD),
        ("CredentialBlob",ctypes.POINTER(ctypes.c_ubyte)),
        ("Persist",wt.DWORD),("AttributeCount",wt.DWORD),
        ("Attributes",ctypes.c_void_p),("TargetAlias",wt.LPWSTR),
        ("UserName",wt.LPWSTR)]
PCREDENTIALW=ctypes.POINTER(_CREDENTIALW)

def _validate(values):
    if (type(values) is not dict or set(values)!=set(FIELDS) or
        any(type(values[k]) is not str or
            not 1<=len(values[k])<=500 or
            re.search(r"[\x00-\x1f\x7f]",values[k]) or
            values[k].strip()!=values[k]
            for k in FIELDS)):
        raise CredentialBlocked("SOURCE_API_CREDENTIAL_FIELDS_INVALID")
    raw=json.dumps(values,sort_keys=True,ensure_ascii=False,
                   separators=(",",":"),allow_nan=False).encode("utf8")
    if not 0<len(raw)<=MAX_UTF8_BLOB:
        raise CredentialBlocked("SOURCE_API_CREDENTIAL_BLOB_TOO_LARGE")
    return raw

class WindowsSourceCredentialStore:
    def __init__(self,target=TARGET):
        # Explicitly scoped local target. Tests use isolated names and delete.
        if (type(target) is not str or
            re.fullmatch(r"SSfindout\.SIMCSecondaryOptimizer\.SourceAPI\.v1"
                         r"(?:\.[A-Za-z0-9-]{1,64})?",target) is None):
            raise CredentialBlocked("SOURCE_API_CREDENTIAL_TARGET_INVALID")
        self.target=target

    @staticmethod
    def _api():
        if os.name!="nt":
            raise CredentialBlocked("SOURCE_API_WINDOWS_CREDENTIAL_MANAGER_ONLY")
        api=ctypes.WinDLL("Advapi32.dll",use_last_error=True)
        api.CredWriteW.argtypes=[PCREDENTIALW,wt.DWORD]
        api.CredWriteW.restype=wt.BOOL
        api.CredReadW.argtypes=[wt.LPCWSTR,wt.DWORD,wt.DWORD,
                                ctypes.POINTER(PCREDENTIALW)]
        api.CredReadW.restype=wt.BOOL
        api.CredDeleteW.argtypes=[wt.LPCWSTR,wt.DWORD,wt.DWORD]
        api.CredDeleteW.restype=wt.BOOL
        api.CredFree.argtypes=[ctypes.c_void_p]
        api.CredFree.restype=None
        return api

    def save(self,values):
        raw=_validate(values)
        api=self._api()
        # Windows copies a generic credential blob; no plaintext file created.
        blob=ctypes.create_string_buffer(raw)
        cred=_CREDENTIALW()
        cred.Type=CRED_TYPE_GENERIC
        cred.TargetName=self.target
        cred.Comment="Local SIMC source API (Blizzard/WCL)"
        cred.CredentialBlobSize=len(raw)
        cred.CredentialBlob=ctypes.cast(blob,ctypes.POINTER(ctypes.c_ubyte))
        cred.Persist=CRED_PERSIST_LOCAL_MACHINE
        cred.UserName="Local source owner"
        if not api.CredWriteW(ctypes.byref(cred),0):
            raise CredentialBlocked("SOURCE_API_CREDENTIAL_STORE_WRITE_FAILED")
        return {"schema":SCHEMA,"storage":"WINDOWS_CREDENTIAL_MANAGER",
                "configured":True,"saved":True,"native_calls":0,
                "network_calls":0}

    def load(self):
        if os.name!="nt":
            return None
        api=self._api()
        pointer=PCREDENTIALW()
        if not api.CredReadW(self.target,CRED_TYPE_GENERIC,0,
                             ctypes.byref(pointer)):
            if ctypes.get_last_error()==ERROR_NOT_FOUND:
                return None
            raise CredentialBlocked("SOURCE_API_CREDENTIAL_STORE_READ_FAILED")
        try:
            record=pointer.contents
            size=int(record.CredentialBlobSize)
            if (size<=0 or size>MAX_UTF8_BLOB or
                not bool(record.CredentialBlob)):
                raise CredentialBlocked("SOURCE_API_CREDENTIAL_STORE_INVALID")
            try:
                data=json.loads(ctypes.string_at(
                    record.CredentialBlob,size).decode("utf8"))
            except (UnicodeError,ValueError,TypeError) as exc:
                raise CredentialBlocked(
                    "SOURCE_API_CREDENTIAL_STORE_INVALID") from None
            _validate(data)
            return data
        finally:
            api.CredFree(ctypes.cast(pointer,ctypes.c_void_p))

    def status(self):
        if os.name!="nt":
            return {"schema":SCHEMA,"storage":"UNAVAILABLE_NON_WINDOWS",
                    "configured":False,"supported":False,
                    "native_calls":0,"network_calls":0}
        saved=self.load()
        return {"schema":SCHEMA,"storage":"WINDOWS_CREDENTIAL_MANAGER",
                "configured":saved is not None,"supported":True,
                "native_calls":0,"network_calls":0}

    def clear(self):
        api=self._api()
        if not api.CredDeleteW(self.target,CRED_TYPE_GENERIC,0):
            if ctypes.get_last_error()!=ERROR_NOT_FOUND:
                raise CredentialBlocked(
                    "SOURCE_API_CREDENTIAL_STORE_DELETE_FAILED")
        return {"schema":SCHEMA,"storage":"WINDOWS_CREDENTIAL_MANAGER",
                "configured":False,"deleted":True,"native_calls":0,
                "network_calls":0}
