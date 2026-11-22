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
import ssl
import urllib.error
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
GITHUB_RUNS="https://api.github.com/repos/simulationcraft/simc-publish/actions/runs?per_page=4"
GITHUB_HOME="https://github.com/simulationcraft/simc-publish/actions"
MAX_GITHUB_JSON=500_000
# The official GitHub CPack archive uses `simc-1210.01.710c240-win64.7z`.
# Older standalone nightly archives may use `simc-1210-01-win64-710c240.7z`.
NIGHTLY=re.compile(
    r"simc-(?:(?P<legacy_series>\d{3,5}(?:-\d{1,3})?)-win64-(?P<legacy_revision>[a-f0-9]{7,12})|"
    r"(?P<official_series>\d{3,5}\.\d{1,3})\.(?P<official_revision>[a-f0-9]{7,12})-win64)\.7z\Z",re.I)
def nightly_identity(filename):
    match=NIGHTLY.fullmatch(filename)
    if match is None:return None
    series=match.group("official_series") or match.group("legacy_series")
    revision=match.group("official_revision") or match.group("legacy_revision")
    return {"filename":filename,"series":series,"revision_short":revision.lower()}

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


def index_error_code(exc):
    """No SSL bypass, no private paths or arbitrary exception text in UI."""
    reason=getattr(exc,"reason",exc)
    if isinstance(reason,(ssl.SSLCertVerificationError,ssl.CertificateError)):
        return "OFFICIAL_NIGHTLY_TLS_CERTIFICATE_INVALID"
    if isinstance(reason,TimeoutError):
        return "OFFICIAL_NIGHTLY_CONNECTION_TIMEOUT"
    if isinstance(exc,urllib.error.HTTPError):
        return "OFFICIAL_NIGHTLY_HTTP_"+str(exc.code)
    if isinstance(exc,urllib.error.URLError):
        return "OFFICIAL_NIGHTLY_CONNECTION_UNAVAILABLE"
    return "OFFICIAL_NIGHTLY_INDEX_UNAVAILABLE"

def fetch_github_json(url):
    """Query *public metadata only* over verified TLS, never a binary URL."""
    assert url.startswith("https://api.github.com/repos/simulationcraft/simc-publish/actions/")
    req=urllib.request.Request(url,headers={
        "Accept":"application/vnd.github+json",
        "User-Agent":"SIMC-Secondary-Official-GitHub-Discovery/1.0"})
    with urllib.request.urlopen(req,timeout=12) as response:
        actual=urllib.parse.urlsplit(response.geturl())
        need(response.status==200 and actual.scheme=="https" and
             actual.hostname=="api.github.com",
             "OFFICIAL_GITHUB_METADATA_SOURCE_INVALID")
        raw=response.read(MAX_GITHUB_JSON+1)
    need(0<len(raw)<=MAX_GITHUB_JSON,"OFFICIAL_GITHUB_METADATA_SIZE_INVALID")
    return json.loads(raw)

def fetch_github_nightly():
    """Official SimC-publish artifact *discovery*, no auto download or token."""
    response=fetch_github_json(GITHUB_RUNS)
    runs=response.get("workflow_runs",[])
    need(type(runs) is list,"OFFICIAL_GITHUB_RUNS_SCHEMA_INVALID")
    for run in runs[:4]:
        rid=run.get("id")
        if type(rid) is not int or rid<=0 or run.get("name")!="Nightly":
            continue
        data=fetch_github_json(
            f"https://api.github.com/repos/simulationcraft/simc-publish/actions/runs/{rid}/artifacts")
        artifacts=data.get("artifacts",[])
        need(type(artifacts) is list,"OFFICIAL_GITHUB_ARTIFACT_SCHEMA_INVALID")
        for entry in artifacts:
            aid=entry.get("id")
            if (entry.get("name")=="simc-nightly-win64-midnight" and
                entry.get("expired") is False and type(aid) is int and aid>0):
                return {"source":"OFFICIAL_SIMC_GITHUB_ACTIONS",
                    "run_id":rid,"artifact_id":aid,
                    "name":"simc-nightly-win64-midnight",
                    # Link to the workflow run's Artifacts section, not the
                    # /runs/{id}/artifacts/{id} page which can show a 404 when
                    # unauthenticated even while the API reports unexpired.
                    "run_url":f"https://github.com/simulationcraft/simc-publish/actions/runs/{rid}",
                    "artifact_expired":False,
                    "created_at":run.get("created_at",""),
                    "direct_install_available":False}
    return None

GENERATED_SOURCE_FILES=(
    ("item_set_bonus.inc","// Set bonus data, wow build "),
    ("gem_data.inc","// Gem properties, wow build "),
    ("temporary_enchant.inc","// Temporary item enchants, wow build "),
)
SOURCE_BASE="https://raw.githubusercontent.com/simulationcraft/simc/"
SOURCE_HEAD_REF="https://api.github.com/repos/simulationcraft/simc/git/ref/heads/midnight"
EXACT_BUILD=re.compile(r"\d+(?:\.\d+){3}\Z")
MAX_COMPATIBILITY_CANDIDATES=12
MAX_SOURCE_CACHE_ENTRIES=32


def generated_source_build(revision, *, open_url=None):
    """Confirm one pinned SimC *source* revision's three generated data builds.

    This proves source-header agreement, NOT that a downloadable binary was
    produced from the revision or that its current built-in data matches.
    No generic web crawling, no unverified redirect or unauthenticated TLS.
    """
    need(type(revision) is str and re.fullmatch(r"[0-9a-f]{7,40}",revision),
         "SIMC_SOURCE_REVISION_INVALID")
    getter=open_url or urllib.request.urlopen
    observed=[]
    for filename,prefix in GENERATED_SOURCE_FILES:
        url=SOURCE_BASE+revision+"/engine/dbc/generated/"+filename
        req=urllib.request.Request(url,headers={
            "User-Agent":"SIMC-Secondary-Official-Source-Check/1.0",
            "Accept":"text/plain"})
        with getter(req,timeout=8) as response:
            endpoint=urllib.parse.urlsplit(response.geturl())
            need(response.status==200 and endpoint.scheme=="https"
                 and endpoint.hostname=="raw.githubusercontent.com"
                 and response.geturl()==url,
                 "SIMC_SOURCE_REDIRECT_OR_HOST_INVALID")
            line=response.read(512).split(b"\n",1)[0]
        try:
            header=line.decode("utf8")
        except UnicodeError as exc:
            raise UpdateBlocked("SIMC_SOURCE_HEADER_UNVERIFIED") from exc
        need(header.startswith(prefix) and
             EXACT_BUILD.fullmatch(header[len(prefix):]) is not None,
             "SIMC_SOURCE_HEADER_UNVERIFIED")
        observed.append(header[len(prefix):])
    need(len(set(observed))==1,"SIMC_SOURCE_GENERATED_BUILDS_CONFLICT")
    return {"source_build":observed[0],"source_headers_checked":len(observed),
            "source_revision":revision,
            "source_identity":"GITHUB_REVISION_GENERATED_HEADERS_ONLY",
            "binary_embedded_build_verified":False}



def quick_source_build(revision, *, open_url=None):
    """Cheap pinned official Live data prefilter, never binary attestation.

    Positive matches MUST also pass all three generated_source_build headers.
    A negative answer saves three remote header requests per old archive.
    """
    need(type(revision) is str and re.fullmatch(r"[0-9a-f]{7,40}",revision),
         "SIMC_SOURCE_REVISION_INVALID")
    url=SOURCE_BASE+revision+"/engine/dbc/generated/client_data_version.inc"
    req=urllib.request.Request(url,headers={
        "User-Agent":"SIMC-Secondary-Source-Discovery/1.0",
        "Accept":"text/plain"})
    with (open_url or urllib.request.urlopen)(req,timeout=8) as response:
        need(response.status==200 and response.geturl()==url,
             "SIMC_SOURCE_REDIRECT_OR_HOST_INVALID")
        raw=response.read(4097)
    need(0<len(raw)<=4096,"SIMC_SOURCE_VERSION_BYTES_INVALID")
    try:
        value=raw.decode("utf8")
    except UnicodeError as exc:
        raise UpdateBlocked("SIMC_SOURCE_VERSION_INVALID") from exc
    matches=re.findall(
        r'^#define CLIENT_DATA_WOW_VERSION "(\d+(?:\.\d+){3})"$',
        value,re.M)
    need(len(matches)==1 and EXACT_BUILD.fullmatch(matches[0]) is not None,
         "SIMC_SOURCE_VERSION_INVALID")
    return matches[0]


def official_source_head_revision(*, open_url=None):
    """Resolve the official branch HEAD to an immutable full Git SHA.

    Source-only discovery never constructs or claims a downloadable binary.
    """
    req=urllib.request.Request(SOURCE_HEAD_REF,headers={
        "User-Agent":"SIMC-Secondary-Source-Discovery/1.0",
        "Accept":"application/vnd.github+json"})
    with (open_url or urllib.request.urlopen)(req,timeout=12) as response:
        need(response.status==200 and response.geturl()==SOURCE_HEAD_REF,
             "SIMC_HEAD_SOURCE_UNVERIFIED")
        raw=response.read(65537)
    need(0<len(raw)<=65536,"SIMC_HEAD_SOURCE_SIZE_INVALID")
    try:
        record=json.loads(raw)
        full=record["object"]["sha"]
        need(record["ref"]=="refs/heads/midnight"
             and record["object"]["type"]=="commit"
             and type(full) is str
             and re.fullmatch(r"[0-9a-f]{40}",full) is not None,
             "SIMC_HEAD_SOURCE_UNVERIFIED")
    except (ValueError,TypeError,KeyError) as exc:
        raise UpdateBlocked("SIMC_HEAD_SOURCE_UNVERIFIED") from exc
    return full


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
        identity=nightly_identity(name)
        if identity and urllib.parse.unquote(parts.path).endswith("/"+name):
            choices[name]={**identity,"url":url}
    # Sort version *series* only; Git short SHA alphabetical order is not
    # chronological. Preserve the official listing order within a series.
    return sorted(choices.values(),key=lambda x:
        tuple(int(p) for p in re.split(r"[.\-]",x["series"])),reverse=True)

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
        # 7-Zip -slt uses 'R' for a normal Windows read-only file and
        # '-rw-r--r--' for a normal POSIX file. Checking for any 'r'
        # incorrectly rejected both. Recognize the entire mode instead:
        # deny reparse/link entries, devices and unfamiliar modes closed.
        unix_mode=re.fullmatch(r"[-dlbcps][rwxstST-]{9}[.+@]?",attrs)
        win_mode=re.fullmatch(r"[A-Z.]{1,16}",attrs)
        if unix_mode:
            need(attrs[0] in ("-","d"),"ARCHIVE_LINK_OR_ENCRYPTION_REFUSED")
        elif win_mode:
            need("L" not in attrs,"ARCHIVE_LINK_OR_ENCRYPTION_REFUSED")
            need(set(attrs)<=set("DARHSI."),"ARCHIVE_ATTRIBUTES_UNRECOGNIZED")
        else:
            need(False,"ARCHIVE_ATTRIBUTES_UNRECOGNIZED")
        need(fields.get("Symbolic Link","") in ("","-") and
             fields.get("Hard Link","") in ("","-"),
             "ARCHIVE_LINK_OR_ENCRYPTION_REFUSED")
        need(fields.get("Encrypted","-")=="-",
             "ARCHIVE_ENCRYPTION_REFUSED")
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
    need(exe.stat().st_size>=100000,"SIMC_WINDOWS_BINARY_TOO_SMALL")
    with exe.open("rb") as binary:
        header=binary.read(64)
        need(len(header)==64 and header[:2]==b"MZ",
             "SIMC_WINDOWS_BINARY_NOT_PE")
        offset=int.from_bytes(header[0x3c:0x40],"little")
        need(64<=offset<exe.stat().st_size-6 and offset<65536,
             "SIMC_WINDOWS_BINARY_PE_OFFSET_INVALID")
        binary.seek(offset)
        need(binary.read(6)==b"PE"+bytes((0,0,0x64,0x86)),
             "SIMC_WINDOWS_BINARY_NOT_AMD64")
    return exe

def probe_cli(exe,*,expected_build=None):
    """Bounded non-DPS SimC start check. Upstream display_build=2 returns before execute()."""
    try:
        result=subprocess.run([str(exe),"display_build=2"],
              cwd=str(pathlib.Path(exe).parent),capture_output=True,
              timeout=20,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
    except subprocess.TimeoutExpired:
        raise UpdateBlocked("SIMC_CLI_SMOKE_TIMEOUT") from None
    except OSError:
        raise UpdateBlocked("SIMC_CLI_LAUNCH_FAILED") from None
    output=(result.stdout or b"")+(result.stderr or b"")
    need(result.returncode==0,"SIMC_CLI_SMOKE_FAILED")
    need(0<len(output)<=16384 and b"simulationcraft" in output.lower(),
         "SIMC_CLI_SMOKE_OUTPUT_INVALID")
    if expected_build is not None:
        need(type(expected_build) is str and EXACT_BUILD.fullmatch(expected_build),
             "SIMC_CLI_EXPECTED_BUILD_INVALID")
        observed=re.findall(
            r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{5,6}\b",
            output.decode("utf8","replace"))
        need(expected_build in observed,
             "SIMC_CLI_EMBEDDED_BUILD_NOT_MATCHED")
    return True


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
        target=urllib.parse.urlsplit(res.geturl())
        need(res.status==200 and target.scheme=="https" and target.hostname==
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
        endpoint=urllib.parse.urlsplit(src.geturl())
        need(src.status==200 and endpoint.scheme=="https" and endpoint.hostname==
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
        self.discovery_generation=0
        # Git sources are immutable by revision; bounded process-local cache
        # avoids redundant GETs without writing new season/cache files.
        self.source_cache={}

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

    def check(self,index=None,*,retain_offer=True,include_candidates=False):
        need(self.platform=="win32","SIMC_UPDATER_WINDOWS_ONLY")
        # Prefer the publisher's own HTTPS index. If TLS fails, use the
        # upstream-owned GitHub Actions *metadata* as a safe manual fallback.
        try:
            candidates=candidate_urls(index if index is not None else fetch_index())
            need(candidates,"NO_OFFICIAL_WIN64_NIGHTLY_FOUND")
        except (urllib.error.URLError,TimeoutError,OSError,UpdateBlocked) as exc:
            reason=str(exc) if isinstance(exc,UpdateBlocked) else index_error_code(exc)
            try:
                alternative=fetch_github_nightly()
            except (urllib.error.URLError,TimeoutError,OSError,ValueError,
                    UpdateBlocked,KeyError,TypeError):
                alternative=None
            with self.lock:
                self.offer=None
                return {"schema":SCHEMA,"candidate":None,
                    "direct_install_available":False,
                    "official_index_problem":reason,
                    "github_alternative":alternative,
                    "github_actions_url":GITHUB_HOME,
                    "manual_archive_required":True,
                    "installation_requires_confirmation":True,
                    "archive_extractor_available":bool(find_sevenzip()),
                    "native_calls_now":0}
        with self.lock:
            selected=candidates[0]
            if retain_offer:
                self.offer=selected;self.offered_at=time.monotonic()
            result={"schema":SCHEMA,"candidate":{"filename":selected["filename"],
                    "revision_short":selected["revision_short"],
                    "official_download_url":selected["url"]},
                    "direct_install_available":True,
                    "github_alternative":None,
                    "official_index_problem":None,
                    "installation_requires_confirmation":True,
                    "archive_extractor_available":bool(find_sevenzip()),
                    "native_calls_now":0}
            if include_candidates:
                result["_official_candidates"]=candidates[:MAX_COMPATIBILITY_CANDIDATES]
                result["official_candidate_total"]=len(candidates)
            return result

    def _candidate_source_proof(self,revision,target_build,source_loader=None):
        """Use 1 cheap read for mismatches and 3 extra reads only for matches."""
        if source_loader is not None:
            # Injectable offline tests do not write into the real provenance cache.
            proof=source_loader(revision)
        else:
            with self.lock:
                proof=self.source_cache.get(revision)
            if proof is None or (proof.get("source_build")==target_build and
                                 proof.get("source_headers_checked")!=3):
                quick=quick_source_build(revision)
                if quick==target_build:
                    proof=generated_source_build(revision)
                    need(proof.get("source_build")==quick,
                         "SIMC_SOURCE_VERSION_CONFLICT")
                else:
                    proof={"source_revision":revision,"source_build":quick,
                           "source_headers_checked":0,
                           "binary_embedded_build_verified":False}
                with self.lock:
                    if len(self.source_cache)>=MAX_SOURCE_CACHE_ENTRIES:
                        self.source_cache.pop(next(iter(self.source_cache)))
                    self.source_cache[revision]=proof
        need(type(proof) is dict
             and proof.get("source_revision")==revision
             and type(proof.get("source_headers_checked")) is int
             and proof["source_headers_checked"] in (0,3)
             and EXACT_BUILD.fullmatch(str(proof.get("source_build",""))) is not None,
             "SIMC_SOURCE_HEADER_UNVERIFIED")
        if proof["source_build"]==target_build:
            need(proof["source_headers_checked"]==3,
                 "SIMC_SOURCE_HEADER_UNVERIFIED")
        return proof

    def check_for_retail_compatibility(self,*,live_loader=None,
                                       source_loader=None,head_loader=None):
        """Generic official binary discovery, then *source-only* fallback.

        Never infer Git commit chronology from filename. A Live match needs
        all three generated headers; a HEAD source is never an install offer.
        No update may change a user-provided binary, season cache, or session.
        """
        from v289_retail_live_build_source import discover
        with self.lock:
            self.discovery_generation+=1
            generation=self.discovery_generation
            self.offer=None
            self.offered_at=0.0
        live=None
        live_problem=None
        try:
            live=(live_loader or discover)(region="KR")
            need(type(live) is dict and
                 live.get("status")=="LIVE_RETAIL_BUILD_SOURCE_OBSERVED"
                 and live.get("region")=="KR"
                 and EXACT_BUILD.fullmatch(str(live.get("game_build",""))) is not None,
                 "RETAIL_BUILD_SOURCE_UNVERIFIED")
        except (OSError,TimeoutError,ValueError,KeyError,TypeError) as exc:
            live_problem=(str(exc) if isinstance(exc,UpdateBlocked)
                          else "RETAIL_BUILD_SOURCE_UNAVAILABLE")
            live=None

        result=self.check(retain_offer=False,include_candidates=True)
        candidates=result.pop("_official_candidates",[])
        result["official_candidate_total"]=result.get("official_candidate_total",0)
        compatibility={
            "status":"LIVE_BUILD_UNKNOWN" if live is None else
                     "NO_VERIFIED_MATCHING_DOWNLOAD",
            "kr_game_build":live["game_build"] if live else None,
            "game_build_source":live.get("source_url") if live else None,
            "game_build_source_sha256":live.get("source_sha256") if live else None,
            "game_build_problem":live_problem,
            "simc_generated_build":None,
            "simc_revision":None,
            "source_headers_checked":0,
            "binary_embedded_build_verified":False,
            "season_ready":False,
            "dps_native_calls_now":0,
            "official_candidates_checked":0,
            "official_candidates_total":result["official_candidate_total"],
            "official_candidate_check_limit":MAX_COMPATIBILITY_CANDIDATES,
            "selection_rule":"OFFICIAL_LIST_SERIES_THEN_LISTING_ORDER_NO_GIT_SHA_AGE",
            "source_only_candidate":None,
        }
        if candidates:
            compatibility["simc_revision"]=candidates[0]["revision_short"]
        matched=None
        mismatches=0
        failures=0
        if live:
            for candidate in candidates:
                compatibility["official_candidates_checked"]+=1
                revision=candidate["revision_short"]
                try:
                    proof=self._candidate_source_proof(
                        revision,live["game_build"],source_loader=source_loader)
                    if compatibility["simc_generated_build"] is None:
                        compatibility["simc_generated_build"]=proof["source_build"]
                        compatibility["source_headers_checked"]=proof["source_headers_checked"]
                    if proof["source_build"]==live["game_build"]:
                        matched=candidate
                        compatibility["simc_revision"]=revision
                        compatibility["simc_generated_build"]=proof["source_build"]
                        compatibility["source_headers_checked"]=3
                        compatibility["status"]="SOURCE_BUILD_MATCHED_BINARY_UNVERIFIED"
                        break
                    mismatches+=1
                except (OSError,TimeoutError,ValueError,TypeError,KeyError):
                    failures+=1
            if not matched and candidates:
                compatibility["status"]=(
                    "SIMC_SOURCE_BUILD_UNVERIFIED" if failures else
                    "SIMC_SOURCE_BUILD_MISMATCH")

        if matched:
            result["candidate"]={
                "filename":matched["filename"],
                "revision_short":matched["revision_short"],
                "official_download_url":matched["url"]}
            result["matching_download_url"]=matched["url"]
            result["direct_install_available"]=True
        else:
            if result.get("candidate"):
                result["unverified_candidate"]=result["candidate"]
            result["candidate"]=None
            result["matching_download_url"]=None
            result["direct_install_available"]=False

        # Last resort discovery: a pinned official source *may* be buildable,
        # but it is never treated as a published .7z or an installed binary.
        # Offline injected loaders never trigger incidental live GitHub calls.
        if live and not matched and (
                head_loader is not None or (
                    live_loader is None and source_loader is None)):
            try:
                head=(head_loader or official_source_head_revision)()
                need(type(head) is str and
                     re.fullmatch(r"[a-f0-9]{40}",head) is not None,
                     "SIMC_HEAD_SOURCE_UNVERIFIED")
                proof=self._candidate_source_proof(
                    head,live["game_build"],source_loader=source_loader)
                if proof["source_build"]==live["game_build"]:
                    compatibility["source_only_candidate"]={
                        "revision_full":head,"source_build":proof["source_build"],
                        "source_headers_checked":3,
                        "downloadable_binary_verified":False,
                        "requires_separate_build":True}
                    compatibility["status"]="MATCHING_SOURCE_REQUIRES_BUILD"
            except (OSError,TimeoutError,ValueError,TypeError,KeyError):
                pass

        with self.lock:
            if generation!=self.discovery_generation:
                # Another newer check superseded this one: no stale offer.
                compatibility["status"]="SIMC_UPDATE_CHECK_SUPERSEDED"
                result["candidate"]=None
                result["matching_download_url"]=None
                result["direct_install_available"]=False
            elif matched:
                self.offer={**nightly_identity(matched["filename"]),
                            "url":matched["url"]}
                self.offered_at=time.monotonic()
            else:
                self.offer=None
                self.offered_at=0.0
        result["retail_compatibility"]=compatibility
        return result

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
                sevenzip=None,archive_source="OFFICIAL_HTTPS_NIGHTLY",probe=None,
                expected_cli_sha=None,receipt_record=None):
        need(self.platform=="win32","SIMC_UPDATER_WINDOWS_ONLY")
        with self.lock:
            offered=self.offer
            need(offered and filename==offered["filename"]
                 and time.monotonic()-self.offered_at<900,
                 "EXPLICIT_RECENT_OFFICIAL_OFFER_REQUIRED")
            # Filename identifies a published Git revision, not a local unverified
            # archive. Only skip a previously verified official managed install.
            state=self._read()
            active=state["active"]
            if (archive_source=="OFFICIAL_HTTPS_NIGHTLY" and active and
                active["filename"]==filename and
                active.get("archive_source")=="OFFICIAL_HTTPS_NIGHTLY"):
                self._binary(active)  # refuse a modified/missing executable
                self.offer=None
                result=self.status()
                result["status"]="MANAGED_SIMC_ALREADY_CURRENT"
                result["non_dps_cli_smoke_calls"]=0
                return result
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
                if expected_cli_sha is not None:
                    need(type(expected_cli_sha) is str
                         and re.fullmatch(r"[0-9a-f]{64}",expected_cli_sha)
                         and bin_sha==expected_cli_sha,
                         "SELF_BUILT_CLI_SHA_MISMATCH")
                dest=self.root/"versions"/bin_sha[:24]
                # Atomic managed tree; never overwrite user's manual installation.
                created=False
                if not dest.exists():
                    dest.parent.mkdir(parents=True,exist_ok=True)
                    ready=scratch/"ready";ready.mkdir()
                    shutil.copy2(exe,ready/"simc.exe")
                    need(sha256(ready/"simc.exe")==bin_sha,"STAGED_BINARY_SHA_DRIFT")
                    os.replace(ready,dest)
                    created=True
                try:
                    need(sha256(dest/"simc.exe")==bin_sha,"MANAGED_BINARY_SHA_DRIFT")
                    # Do not activate an executable that cannot start in its final
                    # managed directory. Never use a DPS simulation as installer QA.
                    (probe or probe_cli)(dest/"simc.exe")
                except Exception:
                    # Failed updates must not accumulate newly created orphan
                    # executables; never delete a pre-existing managed version.
                    if created:shutil.rmtree(dest,ignore_errors=True)
                    raise
                entry={"filename":offered["filename"],
                       "revision_short":offered["revision_short"],
                       "sha256":bin_sha,"archive_sha256":proof["sha256"],
                       "archive_bytes":proof["bytes"],
                       "archive_source":archive_source,
                       "upstream_signature_verified":False}
                if receipt_record is not None:
                    need(type(receipt_record) is dict and set(receipt_record)=={
                         "source_revision_full","source_game_build",
                         "artifact_sha256","receipt_sha256",
                         "source_origin_authenticated"}
                         and receipt_record["source_origin_authenticated"] is False,
                         "SELF_BUILT_RECORD_INVALID")
                    entry.update(receipt_record)
                self._write_state({"schema":SCHEMA,"active":entry,
                                   "previous":state["active"]})
                self.offer=None
                result=self.status()
                result["status"]="NEW_MANAGED_SIMC_ACTIVATED"
                # One real CLI process started for display_build=2; zero DPS.
                result["native_calls_now"]=1
                result["non_dps_cli_smoke_calls"]=1
                result["dps_native_calls_now"]=0
                result["hash_kind"]="LOCAL_SHA256_OF_DOWNLOADED_BYTES_NOT_UPSTREAM_SIGNATURE"
                return result

    def install_local(self,archive_path,*,extractor=extract_safe,sevenzip=None,probe=None):
        """User-selected local archive fallback for unavailable TLS nightlies.

        An archive renamed to an official-looking file is NOT provenance:
        do not claim the user file came from SimC's server or was signed.
        """
        need(self.platform=="win32","SIMC_UPDATER_WINDOWS_ONLY")
        need(type(archive_path) is str and len(archive_path)<=4096,
             "LOCAL_ARCHIVE_PATH_INVALID")
        path=pathlib.Path(archive_path).expanduser()
        need(path.is_file() and not path.is_symlink(),
             "LOCAL_NIGHTLY_FILE_NOT_FOUND")
        need(path.suffix.lower()!=".zip",
             "LOCAL_GITHUB_ARTIFACT_ZIP_EXTRACT_7Z_FIRST")
        identity=nightly_identity(path.name)
        need(identity is not None,"LOCAL_NIGHTLY_FILENAME_UNSUPPORTED")
        need(100000<path.stat().st_size<=MAX_ARCHIVE,
             "LOCAL_NIGHTLY_ARCHIVE_SIZE_INVALID")
        resolved=path.resolve()
        with self.lock:
            self.offer={**identity,"url":"LOCAL_ARCHIVE_SELECTED"}
            self.offered_at=time.monotonic()
            def local_copy(_url,dest):
                shutil.copyfile(resolved,dest)
                need(pathlib.Path(dest).stat().st_size==resolved.stat().st_size,
                     "LOCAL_ARCHIVE_COPY_SIZE_CHANGED")
                need(pathlib.Path(dest).open("rb").read(6)==MAGIC,
                     "LOCAL_ARCHIVE_MAGIC_INVALID")
                return {"sha256":sha256(dest),
                        "bytes":pathlib.Path(dest).stat().st_size}
            return self.install(resolved.name,downloader=local_copy,
                       extractor=extractor,sevenzip=sevenzip,probe=probe,
                       archive_source="USER_LOCAL_FILE_ORIGIN_NOT_AUTHENTICATED")

    def install_self_built(self,artifact_path,*,extractor=extract_safe,
                           sevenzip=None,probe=None):
        """User-approved local Actions ZIP, not an authenticated release.

        The enclosed receipt is self-asserted; validate actual 7z, executable
        digest and the observed CLI game build before switching the pointer.
        Never treat this as an official SimC binary or a season READY signal.
        """
        from v659_simc_self_built_artifact import (
            ArtifactBlocked,inspect_artifact,copy_inner_archive)
        need(self.platform=="win32","SIMC_UPDATER_WINDOWS_ONLY")
        need(type(artifact_path) is str and 0<len(artifact_path)<=4096,
             "SELF_BUILT_ARTIFACT_PATH_INVALID")
        path=pathlib.Path(artifact_path).expanduser()
        with self.lock:
            self.offer=None
            self.offered_at=0.0
            try:
                info=inspect_artifact(path)
                identity=nightly_identity(info["archive_name"])
                need(identity is not None,"SELF_BUILT_ARCHIVE_NAME_INVALID")
                self.offer={**identity,"url":"USER_SELECTED_SELF_BUILT_ZIP"}
                self.offered_at=time.monotonic()
                def copy_local(_url,dest):
                    return copy_inner_archive(path,dest,info)
                def check_cli(exe):
                    need(sha256(exe)==info["cli_sha256"],
                         "SELF_BUILT_CLI_SHA_MISMATCH")
                    if probe is not None:
                        return probe(exe)  # offline fixture only
                    return probe_cli(exe,expected_build=info["game_build"])
                record={
                    "source_revision_full":info["source_sha"],
                    "source_game_build":info["game_build"],
                    "artifact_sha256":info["artifact_sha256"],
                    "receipt_sha256":info["receipt_sha256"],
                    "source_origin_authenticated":False}
                return self.install(info["archive_name"],
                     downloader=copy_local,extractor=extractor,
                     sevenzip=sevenzip,probe=check_cli,
                     archive_source="USER_SELECTED_SELF_BUILT_RECEIPT_UNAUTHENTICATED",
                     expected_cli_sha=info["cli_sha256"],
                     receipt_record=record)
            except ArtifactBlocked as exc:
                raise UpdateBlocked(str(exc)) from None
            finally:
                self.offer=None
                self.offered_at=0.0

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
