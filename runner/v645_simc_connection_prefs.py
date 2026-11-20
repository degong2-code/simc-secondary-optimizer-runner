"""Explicit local SimC connection check + user settings persistence (v645).

No credentials, environment admissions, DPS calculation, or browser storage.
The user's path and declared revision survive a ZIP upgrade in the same
local runs parent. A saved revision is NEVER proof of SimC source identity.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import subprocess
import tempfile

SCHEMA="v645_user_confirmed_simc_connection_v1"
FILE="simc-user-connection.json"
REV=re.compile(r"(?:[0-9a-f]{7,12}|[0-9a-f]{40})\Z")
BUILD=re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{5,6}\b")
GIT_TEXT=re.compile(r"\b(?:git\s+(?:rev(?:ision)?|commit)|revision|commit)\s*[:=# ]\s*([0-9a-f]{7,40})\b",re.I)


class SimCConnectionBlocked(ValueError):
    pass


def need(condition,code):
    if not condition:raise SimCConnectionBlocked(code)


def _sha(path):
    hasher=hashlib.sha256()
    with path.open("rb") as stream:
        for piece in iter(lambda:stream.read(1024*1024),b""):
            hasher.update(piece)
    return hasher.hexdigest()


class LocalSimCConnectionPrefs:
    def __init__(self,root):
        self.root=pathlib.Path(root).expanduser()
        self.path=self.root/FILE

    def status(self):
        need(not self.root.is_symlink() and not self.path.is_symlink(),
             "SIMC_SETTINGS_UNSAFE_PATH")
        if not self.path.exists():
            return {"schema":SCHEMA,"saved":None,"verified_now":False,
                    "native_calls_now":0}
        need(self.path.is_file() and self.path.stat().st_size<=16000,
             "SIMC_SETTINGS_FILE_INVALID")
        try:
            d=json.loads(self.path.read_text(encoding="utf8"))
            need(type(d) is dict and d.get("schema")==SCHEMA
                 and type(d.get("binary")) is str
                 and 0<len(d["binary"])<=4096
                 and type(d.get("revision")) is str and REV.fullmatch(d["revision"])
                 and type(d.get("static_cache")) is str
                 and len(d["static_cache"])<=4096
                 and type(d.get("binary_sha256")) is str
                 and re.fullmatch(r"[0-9a-f]{64}",d["binary_sha256"]) is not None,
                 "SIMC_SETTINGS_FILE_INVALID")
        except (ValueError,UnicodeError,OSError,TypeError) as exc:
            raise SimCConnectionBlocked("SIMC_SETTINGS_FILE_INVALID") from exc
        return {"schema":SCHEMA,"saved":{k:d.get(k) for k in (
                    "binary","revision","static_cache","binary_sha256",
                    "observed_game_build","revision_identity")},
                "verified_now":False,"native_calls_now":0}

    def confirm(self,*,binary,revision,static_cache="",run=None,
                managed=None):
        need(type(binary) is str and 0<len(binary)<=4096 and
             not any(c in binary for c in "\x00\r\n"),
             "SIMC_CONNECTION_BINARY_INVALID")
        need(type(revision) is str and REV.fullmatch(revision) is not None,
             "SIMC_CONNECTION_REVISION_INVALID")
        need(type(static_cache) is str and len(static_cache)<=4096,
             "SIMC_CONNECTION_STATIC_CACHE_INVALID")
        p=pathlib.Path(binary).expanduser()
        need(p.name.lower()=="simc.exe" and not p.is_symlink() and p.is_file(),
             "SIMC_CONNECTION_BINARY_NOT_FOUND")
        if static_cache:
            cache=pathlib.Path(static_cache).expanduser()
            need(cache.suffix.lower()==".json" and not cache.is_symlink()
                 and cache.is_file(),"SIMC_CONNECTION_STATIC_CACHE_NOT_FOUND")
        actual_sha=_sha(p)
        controlled=False
        if isinstance(managed,dict) and managed.get("active_binary"):
            try:
                same=p.resolve()==pathlib.Path(managed["active_binary"]).resolve()
            except OSError:
                same=False
            if same:
                entry=managed.get("installed") or {}
                need(entry.get("sha256")==actual_sha and
                     isinstance(entry.get("revision_short"),str) and
                     (entry["revision_short"].startswith(revision) or
                      revision.startswith(entry["revision_short"])),
                     "SIMC_CONNECTION_MANAGED_REVISION_MISMATCH")
                controlled=True
        try:
            proc=(run or subprocess.run)([str(p),"display_build=2"],cwd=str(p.parent),
                     capture_output=True,timeout=20,
                     creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
        except subprocess.TimeoutExpired as exc:
            raise SimCConnectionBlocked("SIMC_CONNECTION_CLI_TIMEOUT") from exc
        except (OSError,subprocess.SubprocessError) as exc:
            raise SimCConnectionBlocked("SIMC_CONNECTION_CLI_LAUNCH_FAILED") from exc
        raw=(proc.stdout or b"")+(proc.stderr or b"")
        need(proc.returncode==0 and 0<len(raw)<=16384 and
             b"simulationcraft" in raw.lower(),
             "SIMC_CONNECTION_CLI_SMOKE_FAILED")
        output=raw.decode("utf8","replace")
        embedded=GIT_TEXT.search(output)
        if embedded:
            found=embedded.group(1).lower()
            need(found.startswith(revision) or revision.startswith(found),
                 "SIMC_CONNECTION_REVISION_MISMATCH")
        builds=BUILD.findall(output)
        observed=builds[0] if builds else None
        identity=("SIMC_CLI_PRINTED_REVISION_VERIFIED" if embedded else
                  "MANAGED_OFFICIAL_FILENAME_SHA_ONLY"
                  if controlled and isinstance(managed,dict)
                  and (managed.get("installed") or {}).get("archive_source")==
                      "OFFICIAL_HTTPS_NIGHTLY" else
                  "MANAGED_LOCAL_ARCHIVE_REVISION_NOT_ATTESTED"
                  if controlled else
                  "USER_ENTERED_REVISION_NOT_ATTESTED")
        doc={"schema":SCHEMA,"binary":str(p),"revision":revision,
             "static_cache":static_cache,"binary_sha256":actual_sha,
             "observed_game_build":observed,"revision_identity":identity}
        self.root.mkdir(parents=True,exist_ok=True)
        need(not self.root.is_symlink() and not self.path.is_symlink(),
             "SIMC_SETTINGS_UNSAFE_PATH")
        tmp=None
        try:
            with tempfile.NamedTemporaryFile(mode="w",encoding="utf8",
                    dir=str(self.root),prefix=".simc-connection-",suffix=".tmp",
                    delete=False) as dest:
                tmp=pathlib.Path(dest.name)
                json.dump(doc,dest,ensure_ascii=False,sort_keys=True)
                dest.write("\n")
                dest.flush()
                os.fsync(dest.fileno())
            os.chmod(tmp,0o600)
            os.replace(tmp,self.path)
        finally:
            if tmp and tmp.exists():tmp.unlink()
        return {"schema":SCHEMA,"saved":{k:doc[k] for k in (
                   "binary","revision","static_cache","binary_sha256",
                   "observed_game_build","revision_identity")},
                "verified_now":True,"native_calls_now":1,
                "dps_native_calls_now":0}
