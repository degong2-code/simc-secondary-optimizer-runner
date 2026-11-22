#!/usr/bin/env python3
"""Validate generic source-pinned SimC Windows CLI build requests and receipts.

This module never compiles, downloads or executes SimC by itself. Build and
packaging use the unchanged upstream CMake/CPack via an isolated CI workflow.
"""
import argparse
import hashlib
import json
import pathlib
import re
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
from v193_simc_local_updater import MAGIC,nightly_identity

SCHEMA="p3_v658_generic_windows_cli_build_request_v1"
REPO="simulationcraft/simc"
FULL_SHA=re.compile(r"[a-f0-9]{40}\Z")
GAME_BUILD=re.compile(r"\d+(?:\.\d+){3}\Z")
SOURCE_HEADERS=(
    ("item_set_bonus.inc","// Set bonus data, wow build "),
    ("gem_data.inc","// Gem properties, wow build "),
    ("temporary_enchant.inc","// Temporary item enchants, wow build "),
)
class BuildBlocked(ValueError):pass
def need(valid,reason):
    if not valid:raise BuildBlocked(reason)
def read_request(path):
    p=pathlib.Path(path)
    need(p.is_file() and not p.is_symlink() and 0<p.stat().st_size<2048,
         "BUILD_REQUEST_FILE_INVALID")
    try:d=json.loads(p.read_text("utf8"))
    except (UnicodeError,ValueError) as e:
        raise BuildBlocked("BUILD_REQUEST_JSON_INVALID") from e
    need(type(d) is dict and set(d)=={
        "schema","source_repo","source_sha","game_build","target","reason"},
        "BUILD_REQUEST_FIELDS_INVALID")
    need(d["schema"]==SCHEMA and d["source_repo"]==REPO
         and d["target"]=="windows-x64-cli"
         and d["reason"]=="official_binary_unavailable",
         "BUILD_REQUEST_SCOPE_INVALID")
    need(type(d["source_sha"]) is str and FULL_SHA.fullmatch(d["source_sha"]),
         "BUILD_REQUEST_SHA_INVALID")
    need(type(d["game_build"]) is str and GAME_BUILD.fullmatch(d["game_build"]),
         "BUILD_REQUEST_GAME_BUILD_INVALID")
    return d

def source_identity(root,doc,git_head):
    root=pathlib.Path(root)
    need(root.is_dir() and not root.is_symlink()
         and git_head==doc["source_sha"],"BUILD_SOURCE_GIT_SHA_MISMATCH")
    generated=root/"engine/dbc/generated"
    version=(generated/"client_data_version.inc").open("rb").read(4096).decode("utf8")
    match=re.findall(
      r'^#define CLIENT_DATA_WOW_VERSION "(\d+(?:\.\d+){3})"$',
      version,re.M)
    need(len(match)==1 and match[0]==doc["game_build"],
         "BUILD_SOURCE_CLIENT_DATA_MISMATCH")
    for name,prefix in SOURCE_HEADERS:
        first=(generated/name).open("rb").read(256).split(b"\n",1)[0].decode("utf8")
        need(first==prefix+doc["game_build"],
             "BUILD_SOURCE_GENERATED_HEADER_MISMATCH")
    config=(root/"engine/config.hpp").open("rb").read(20000).decode("utf8")
    major=re.findall(r'^\s*#define SC_MAJOR_VERSION "(\d+)"',config,re.M)
    minor=re.findall(r'^\s*#define SC_MINOR_VERSION "(\d+)"',config,re.M)
    need(len(major)==1 and len(minor)==1,"BUILD_SOURCE_SERIES_UNKNOWN")
    return {"schema":"p3_v658_source_proof_v1","source_sha":doc["source_sha"],
            "game_build":doc["game_build"],"series":major[0]+"."+minor[0],
            "source_headers_checked":4,"source_verified":True,
            "binary_verified":False,"environment_ready":False}

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()

def package_receipt(doc,proof,archive,exe,smoke):
    archive=pathlib.Path(archive);exe=pathlib.Path(exe);smoke=pathlib.Path(smoke)
    need(proof.get("source_sha")==doc["source_sha"]
         and proof.get("game_build")==doc["game_build"]
         and proof.get("source_headers_checked")==4,
         "BUILD_SOURCE_RECEIPT_INVALID")
    identity=nightly_identity(archive.name)
    need(identity is not None
         and identity["revision_short"]==doc["source_sha"][:7]
         and identity["series"]==proof["series"],
         "BUILD_ARCHIVE_NAME_WRONG_REVISION")
    need(archive.is_file() and not archive.is_symlink()
         and 100000<archive.stat().st_size<=250*1024*1024,
         "BUILD_ARCHIVE_INVALID")
    with archive.open("rb") as f:
        need(f.read(6)==MAGIC,"BUILD_ARCHIVE_MAGIC_INVALID")
    need(exe.is_file() and not exe.is_symlink()
         and exe.name.lower()=="simc.exe" and exe.stat().st_size>=100000,
         "BUILD_EXECUTABLE_INVALID")
    with exe.open("rb") as f:
        first=f.read(64)
        need(len(first)==64 and first[:2]==b"MZ","BUILD_PE_HEADER_INVALID")
        off=int.from_bytes(first[0x3c:0x40],"little")
        need(64<=off<min(65536,exe.stat().st_size-6),"BUILD_PE_OFFSET_INVALID")
        f.seek(off)
        need(f.read(6)==b"PE\x00\x00\x64\x86","BUILD_PE_NOT_X64")
    need(smoke.is_file() and smoke.stat().st_size<=32768,"BUILD_SMOKE_MISSING")
    output=smoke.read_text("utf8",errors="replace")
    need("simulationcraft" in output.lower(),"BUILD_SMOKE_OUTPUT_INVALID")
    seen=re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{5,6}\b',output)
    need(not seen or doc["game_build"] in seen,
         "BUILD_CLI_REPORTED_BUILD_CONFLICT")
    return {"schema":"p3_v658_windows_cli_build_receipt_v1",
            "source_repo":REPO,"source_sha":doc["source_sha"],
            "source_game_build":doc["game_build"],
            "archive_name":archive.name,"archive_sha256":sha256(archive),
            "archive_bytes":archive.stat().st_size,
            "cli_sha256":sha256(exe),"cli_bytes":exe.stat().st_size,
            "cli_smoke":"PASS",
            "binary_embedded_build_verified":doc["game_build"] in seen,
            "observed_game_build":doc["game_build"] if doc["game_build"] in seen else None,
            "origin":"SELF_BUILT_UPSTREAM_SIMC_NOT_OFFICIAL_BINARY",
            "build_mode":"MSVC_RELEASE_CLI_NO_GUI_IPO",
            "official_release":False,"season_environment_ready":False,
            "native_dps_calls":0}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=["request","source","package"])
    p.add_argument("--request",required=True)
    p.add_argument("--source")
    p.add_argument("--head")
    p.add_argument("--proof")
    p.add_argument("--archive")
    p.add_argument("--exe")
    p.add_argument("--smoke")
    p.add_argument("--out")
    a=p.parse_args()
    doc=read_request(a.request)
    if a.mode=="request":
        print(json.dumps({"full_sha":doc["source_sha"],
            "short_sha":doc["source_sha"][:7],"game_build":doc["game_build"]}))
        return
    if a.mode=="source":result=source_identity(a.source,doc,a.head)
    else:
        proof=json.loads(pathlib.Path(a.proof).read_text("utf8"))
        result=package_receipt(doc,proof,a.archive,a.exe,a.smoke)
    pathlib.Path(a.out).write_text(json.dumps(result,sort_keys=True,indent=2)+"\n","utf8")
    print("GENERIC_SIMC_"+a.mode.upper()+"_PROOF_PASS")

if __name__=="__main__":
    try:main()
    except (BuildBlocked,OSError,ValueError,TypeError,KeyError,UnicodeError) as exc:
        print(str(exc),file=sys.stderr)
        sys.exit(2)
