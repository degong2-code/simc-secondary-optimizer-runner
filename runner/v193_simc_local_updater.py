#!/usr/bin/env python3
"""v193: explicit, loopback-authorized Windows SimC nightly manager.

Separate managed install directory; NEVER replace user's existing simc.exe,
session JSON/Native cache or season item database. Offer -> consent -> download
official HTTPS Windows nightly -> bounded safe 7z -> atomic pointer update.
The upstream nightly supplies a git short hash, NOT a separately signed hash.
"""
from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request

SCHEMA="v193_explicit_local_simc_nightly_manager_v1"
BASE="https://downloads.simulationcraft.org/nightly/"
NIGHTLY=re.compile(r"simc-(\d{3,5}(?:-\d{1,3})?)-win64-([a-f0-9]{7,12})\.7z\Z",re.I)
MAX_ARCHIVE=250*1024*1024
MAX_EXPANDED=1100*1024*1024
MAX_ENTRIES=5000
MAX_INDEX=2*1024*1024
MAGIC=b"7z\xbc\xaf\x27\x1c"
class UpdateBlocked(ValueError):pass
def need(cond,code):
    if not cond:raise UpdateBlocked(code)
def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as stream:
        for buf in iter(lambda:stream.read(1024*1024),b""):h.update(buf)
    return h.hexdigest()
class Links(HTMLParser):
    def __init__(self):
        super().__init__();self.urls=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a":
            dest=dict(attrs).get("href")
            if dest:self.urls.append(dest)

def candidate_urls(html):
    """Accept only official same-host Windows 64bit .7z entries."""
    p=Links();p.feed(html)
    choices={}
    for href in p.urls:
        url=urllib.parse.urljoin(BASE,href)
        parts=urllib.parse.urlsplit(url)
        if (parts.scheme!="https" or parts.hostname!="downloads.simulationcraft.org"
            or parts.username or parts.password or parts.query or parts.fragment
            or parts.port not in (None,443)
            or not parts.path.startswith("/nightly/")):
            continue
        name=pathlib.PurePosixPath(parts.path).name
        m=NIGHTLY.fullmatch(name)
        if m and urllib.parse.unquote(parts.path).endswith("/"+name):
            choices[name]={"filename":name,"revision_short":m.group(2).lower(),
               "series":m.group(1),"url":url}
    return sorted(choices.values(),key=lambda x:
        (tuple(int(p) for p in x["series"].split("-")),x["filename"]),reverse=True)

def verify_inventory(listing):
    """Parse 7z -slt records, fail closed before any extraction."""
    need("----------" in listing,"ARCHIVE_LIST_FORMAT_UNKNOWN")
    entries=[];keys=set();total=0
    for block in listing.split("----------",1)[1].split("\n\n"):
        fields={}
        for line in block.splitlines():
            if " = " in line:
                k,v=line.split(" = ",1);fields[k.strip()]=v.strip()
        if not fields:continue
        name=fields.get("Path","").replace("\\","/")
        parts=name.split("/")
        need(bool(name) and all(x not in ("",".","..") for x in parts)
             and not name.startswith(("/","\\"))
             and ":" not in name and "\x00" not in name,
             "UNSAFE_ARCHIVE_ENTRY")
        folded=name.casefold()
        need(folded not in keys,"DUPLICATE_ARCHIVE_ENTRY")
        keys.add(folded)
        attrs=fields.get("Attributes","")
        need("l" not in attrs.lower() and "r" not in attrs.lower()
             and fields.get("Encrypted","-")=="-",
             "ARCHIVE_LINK_OR_ENCRYPTION_REFUSED")
        size=fields.get("Size","0")
        need(size.isdecimal() and int(size)<=MAX_EXPANDED,
             "ARCHIVE_ENTRY_SIZE_INVALID")
        total+=int(size)
        need(total<=MAX_EXPANDED,"ARCHIVE_EXPANDED_SIZE_EXCESS")
        entries.append(name)
        need(len(entries)<=MAX_ENTRIES,"ARCHIVE_TOO_MANY_ENTRIES")
    need(any(pathlib.PurePosixPath(x).name.casefold()=="simc.exe"
             for x in entries),"SIMC_CLI_MISSING_FROM_ARCHIVE")
    return entries

def extract_safe(archive,folder,sevenzip):
    args=[sevenzip,"l","-slt",str(archive)]
    p=subprocess.run(args,capture_output=True,text=True,timeout=35,
                     errors="replace",creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
    need(p.returncode==0,"SEVEN_ZIP_LIST_FAILED")
    verify_inventory(p.stdout)
    p=subprocess.run([sevenzip,"x","-y","-bd","-bb0",str(archive),
                      "-o"+str(folder)],capture_output=True,text=True,
                     timeout=180,errors="replace",
                     creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
    need(p.returncode==0,"SEVEN_ZIP_EXTRACT_FAILED")
    files=[]
    for sub in folder.rglob("*"):
        need(not sub.is_symlink(),"ARCHIVE_EXTRACTED_SYMLINK_REFUSED")
        need(sub.resolve().is_relative_to(folder.resolve()),
             "ARCHIVE_EXTRACTED_PATH_ESCAPE")
        if sub.is_file() and sub.name.casefold()=="simc.exe":
            files.append(sub)
    need(len(files)==1,"EXACTLY_ONE_SIMC_CLI_REQUIRED")
    exe=files[0]
    need(exe.stat().st_size>=100000 and exe.open("rb").read(2)==b"MZ",
         "SIMC_WINDOWS_BINARY_NOT_PE")
    return exe

def find_sevenzip():
    if sys.platform!="win32":
        return shutil.which("7z") or shutil.which("7zz")
    candidates=[shutil.which("7z"),shutil.which("7z.exe")]
    for key in ("ProgramFiles","ProgramFiles(x86)"):
        if os.environ.get(key):candidates.append(str(pathlib.Path(os.environ[key])/"7-Zip/7z.exe"))
    return next((x for x in candidates if x and pathlib.Path(x).is_file()),None)

def fetch_index():
    req=urllib.request.Request(BASE,headers={"User-Agent":"SIMC-Secondary-Local-Update/1.0",
                                             "Accept":"text/html"})
    with urllib.request.urlopen(req,timeout=20) as res:
        need(res.status==200 and urllib.parse.urlsplit(res.geturl()).hostname==
             "downloads.simulationcraft.org","OFFICIAL_INDEX_SOURCE_INVALID")
        raw=res.read(MAX_INDEX+1)
    need(0<len(raw)<=MAX_INDEX,"OFFICIAL_INDEX_SIZE_INVALID")
    return raw.decode("utf8","replace")

def fetch_archive(url,target):
    need(url.startswith(BASE) and NIGHTLY.fullmatch(url.split("/")[-1]),
         "NIGHTLY_URL_NOT_OFFICIAL")
    req=urllib.request.Request(url,headers={"User-Agent":"SIMC-Secondary-Local-Update/1.0"})
    h=hashlib.sha256();size=0
    with urllib.request.urlopen(req,timeout=60) as src,open(target,"wb") as dst:
        need(src.status==200 and urllib.parse.urlsplit(src.geturl()).hostname==
             "downloads.simulationcraft.org",
             "OFFICIAL_ARCHIVE_REDIRECT_REFUSED")
        while True:
            block=src.read(1024*1024)
            if not block:break
            size+=len(block);need(size<=MAX_ARCHIVE,"NIGHTLY_DOWNLOAD_TOO_LARGE")
            h.update(block);dst.write(block)
    need(size>100000 and pathlib.Path(target).open("rb").read(6)==MAGIC,
         "NIGHTLY_ARCHIVE_FORMAT_INVALID")
    return {"sha256":h.hexdigest(),"bytes":size}

class SimCManager:
    def __init__(self,root,*,platform=None):
        self.root=pathlib.Path(root).expanduser().resolve()
        self.platform=platform or sys.platform
        self.lock=threading.RLock()
        self.offer=None
        self.offered_at=0.0

    def _read(self):
        file=self.root/"installed.json"
        if not file.is_file():
            return {"schema":SCHEMA,"active":None,"previous":None}
        need(not file.is_symlink() and file.stat().st_size<10000,
             "INSTALL_MANIFEST_INVALID")
        data=json.loads(file.read_text("utf8"))
        need(data.get("schema")==SCHEMA,"INSTALL_MANIFEST_SCHEMA_INVALID")
        return data

    def _binary(self,entry):
        if entry is None:return None
        need(type(entry) is dict and re.fullmatch(r"[a-f0-9]{64}",entry.get("sha256",""))
             and NIGHTLY.fullmatch(entry.get("filename","")) is not None,
             "MANAGED_BINARY_ID_INVALID")
        path=self.root/"versions"/(entry["sha256"][:24])/"simc.exe"
        # Distribution often includes a top-level version directory:
        # store CLI in the stable root of its own managed installation.
        need(path.is_file() and not path.is_symlink() and sha256(path)==entry["sha256"],
             "MANAGED_BINARY_SHA_CHANGED")
        return str(path)

    def status(self):
        with self.lock:
            data=self._read()
            active=self._binary(data["active"])
            previous=self._binary(data["previous"])
            return {"schema":SCHEMA,"windows_supported":self.platform=="win32",
                    "archive_extractor_available":bool(find_sevenzip()) if
                       self.platform=="win32" else False,
                    "installed":data["active"],"active_binary":active,
                    "previous":data["previous"],"can_rollback":bool(active),
                    "manual_binary_never_modified":True,
                    "native_calls_now":0,"season_database_unchanged":True}

    def check(self,index=None):
        need(self.platform=="win32","SIMC_UPDATER_WINDOWS_ONLY")
        candidates=candidate_urls(index if index is not None else fetch_index())
        need(candidates,"NO_OFFICIAL_WIN64_NIGHTLY_FOUND")
        with self.lock:
            self.offer=candidates[0];self.offered_at=time.monotonic()
            return {"schema":SCHEMA,"candidate":{"filename":self.offer["filename"],
                    "revision_short":self.offer["revision_short"],
                    "official_download_url":self.offer["url"]},
                    "installation_requires_confirmation":True,
                    "archive_extractor_available":bool(find_sevenzip()),
                    "native_calls_now":0}

    def _write_state(self,data):
        self.root.mkdir(parents=True,exist_ok=True)
        dest=self.root/"installed.json"
        with tempfile.NamedTemporaryFile(mode="w",encoding="utf8",dir=self.root,
                                          prefix=".state-",delete=False) as f:
            tmp=pathlib.Path(f.name)
            json.dump(data,f,sort_keys=True)
            f.write("\n");f.flush();os.fsync(f.fileno())
        try:os.replace(tmp,dest)
        finally:tmp.unlink(missing_ok=True)

    def install(self,filename,*,downloader=fetch_archive,extractor=extract_safe,
                sevenzip=None):
        need(self.platform=="win32","SIMC_UPDATER_WINDOWS_ONLY")
        with self.lock:
            offered=self.offer
            need(offered and filename==offered["filename"]
                 and time.monotonic()-self.offered_at<900,
                 "EXPLICIT_RECENT_OFFICIAL_OFFER_REQUIRED")
            tool=sevenzip or find_sevenzip()
            need(tool,"SEVEN_ZIP_REQUIRED")
            self.root.mkdir(parents=True,exist_ok=True)
            with tempfile.TemporaryDirectory(prefix=".install-",dir=self.root) as td:
                scratch=pathlib.Path(td);archive=scratch/"nightly.7z"
                proof=downloader(offered["url"],archive)
                need(proof.get("sha256")==sha256(archive) and
                     100000<proof.get("bytes",0)<=MAX_ARCHIVE,
                     "ARCHIVE_DOWNLOAD_DIGEST_INVALID")
                stage=scratch/"extracted";stage.mkdir()
                exe=extractor(archive,stage,tool)
                need(exe.is_file() and exe.resolve().is_relative_to(stage.resolve()),
                     "SIMC_STAGED_EXE_UNSAFE")
                bin_sha=sha256(exe)
                dest=self.root/"versions"/bin_sha[:24]
                # Atomic managed tree; never overwrite user's manual installation.
                if not dest.exists():
                    dest.parent.mkdir(parents=True,exist_ok=True)
                    ready=scratch/"ready";ready.mkdir()
                    shutil.copy2(exe,ready/"simc.exe")
                    need(sha256(ready/"simc.exe")==bin_sha,"STAGED_BINARY_SHA_DRIFT")
                    os.replace(ready,dest)
                need(sha256(dest/"simc.exe")==bin_sha,"MANAGED_BINARY_SHA_DRIFT")
                state=self._read()
                entry={"filename":offered["filename"],
                       "revision_short":offered["revision_short"],
                       "sha256":bin_sha,"archive_sha256":proof["sha256"],
                       "archive_bytes":proof["bytes"]}
                self._write_state({"schema":SCHEMA,"active":entry,
                                   "previous":state["active"]})
                self.offer=None
                result=self.status()
                result["status"]="NEW_MANAGED_SIMC_ACTIVATED"
                result["hash_kind"]="LOCAL_SHA256_OF_DOWNLOADED_BYTES_NOT_UPSTREAM_SIGNATURE"
                return result

    def rollback(self):
        need(self.platform=="win32","SIMC_UPDATER_WINDOWS_ONLY")
        with self.lock:
            old=self._read()
            need(old["active"] is not None,"NO_MANAGED_SIMC_TO_ROLL_BACK")
            if old["previous"] is not None:self._binary(old["previous"])
            self._write_state({"schema":SCHEMA,"active":old["previous"],
                               "previous":old["active"]})
            result=self.status();result["status"]=(
                "PREVIOUS_MANAGED_SIMC_RESTORED" if old["previous"] is not None
                else "MANAGED_SIMC_DEACTIVATED_USE_PREVIOUS_MANUAL_BINARY")
            return result
