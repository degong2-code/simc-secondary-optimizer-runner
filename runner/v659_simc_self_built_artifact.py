"""Explicit import of a local self-built upstream SimC Windows Actions artifact.

The ZIP and its JSON receipts are USER-SUPPLIED, NOT a cryptographic
attestation of GitHub origin. Strongly validate internal consistency, then
let the existing v193 safe 7z extractor and CLI probe authorize installation.
No network, no auto-build, no SimC DPS simulation.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import shutil
import stat
import zipfile

from v193_simc_local_updater import MAGIC, MAX_ARCHIVE, nightly_identity

MAX_ARTIFACT=MAX_ARCHIVE+8*1024*1024
MAX_DOCUMENT=16*1024
SHA256=re.compile(r"[a-f0-9]{64}\Z")
SHA40=re.compile(r"[a-f0-9]{40}\Z")
VERSION=re.compile(r"\d+(?:\.\d+){3}\Z")
SMOKE_BUILD=re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{5,6}\b")
FIXED={"build_receipt.json","source_proof.json","display_build.txt"}

class ArtifactBlocked(ValueError):pass
def need(value,code):
    if not value:raise ArtifactBlocked(code)
def digest(path):
    h=hashlib.sha256()
    with pathlib.Path(path).open("rb") as f:
        for piece in iter(lambda:f.read(1024*1024),b""):
            h.update(piece)
    return h.hexdigest()

def _document(z,member):
    info=z.getinfo(member)
    need(0<info.file_size<=MAX_DOCUMENT,"SIMC_ARTIFACT_DOCUMENT_SIZE_INVALID")
    with z.open(info) as f: data=f.read(MAX_DOCUMENT+1)
    need(0<len(data)<=MAX_DOCUMENT,"SIMC_ARTIFACT_DOCUMENT_SIZE_INVALID")
    try: return json.loads(data)
    except (ValueError,UnicodeError) as exc:
        raise ArtifactBlocked("SIMC_ARTIFACT_DOCUMENT_JSON_INVALID") from exc

def _members(z):
    members=z.infolist()
    need(len(members)==4,"SIMC_ARTIFACT_MEMBERS_INVALID")
    names=[i.filename for i in members]
    need(len(set(names))==4 and all("/" not in n and "\\" not in n
                                  and not n.startswith(".") and "\x00" not in n
                                  for n in names),"SIMC_ARTIFACT_MEMBER_PATH_INVALID")
    archives=[n for n in names if nightly_identity(n)]
    need(len(archives)==1 and set(names)==FIXED|set(archives),
         "SIMC_ARTIFACT_MEMBERS_INVALID")
    for info in members:
        mode=stat.S_IFMT(info.external_attr>>16)
        need(not info.is_dir() and mode in (0,stat.S_IFREG)
             and not info.flag_bits&1 and
             info.compress_type in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED),
             "SIMC_ARTIFACT_MEMBER_TYPE_INVALID")
        bound=MAX_ARCHIVE if info.filename==archives[0] else MAX_DOCUMENT
        need(0<info.file_size<=bound,"SIMC_ARTIFACT_MEMBER_SIZE_INVALID")
    return archives[0]

def inspect_artifact(path):
    path=pathlib.Path(path).expanduser()
    need(path.is_file() and not path.is_symlink() and
         path.suffix.lower()==".zip" and
         100000<path.stat().st_size<=MAX_ARTIFACT,
         "SIMC_ARTIFACT_ZIP_INVALID")
    try:
        with zipfile.ZipFile(path) as z:
            archive_name=_members(z)
            receipt=_document(z,"build_receipt.json")
            proof=_document(z,"source_proof.json")
            need(type(receipt) is dict and
                 receipt.get("schema")=="p3_v658_windows_cli_build_receipt_v1"
                 and receipt.get("origin")=="SELF_BUILT_UPSTREAM_SIMC_NOT_OFFICIAL_BINARY"
                 and receipt.get("source_repo")=="simulationcraft/simc"
                 and receipt.get("official_release") is False
                 and receipt.get("season_environment_ready") is False
                 and receipt.get("cli_smoke")=="PASS"
                 and receipt.get("binary_embedded_build_verified") is True
                 and receipt.get("native_dps_calls")==0,
                 "SIMC_ARTIFACT_RECEIPT_INVALID")
            source_sha=receipt.get("source_sha")
            game_build=receipt.get("source_game_build")
            need(type(source_sha) is str and SHA40.fullmatch(source_sha) and
                 type(game_build) is str and VERSION.fullmatch(game_build),
                 "SIMC_ARTIFACT_SOURCE_IDENTITY_INVALID")
            ident=nightly_identity(archive_name)
            need(ident is not None and ident["revision_short"]==source_sha[:7]
                 and receipt.get("archive_name")==archive_name,
                 "SIMC_ARTIFACT_ARCHIVE_IDENTITY_MISMATCH")
            need(type(proof) is dict and
                 proof.get("schema")=="p3_v658_source_proof_v1"
                 and proof.get("source_sha")==source_sha
                 and proof.get("game_build")==game_build
                 and proof.get("source_headers_checked")==4
                 and proof.get("source_verified") is True
                 and proof.get("binary_verified") is False
                 and proof.get("environment_ready") is False
                 and ident["series"]==proof.get("series"),
                 "SIMC_ARTIFACT_SOURCE_PROOF_INVALID")
            archive_sha=receipt.get("archive_sha256")
            cli_sha=receipt.get("cli_sha256")
            need(type(archive_sha) is str and SHA256.fullmatch(archive_sha)
                 and type(cli_sha) is str and SHA256.fullmatch(cli_sha)
                 and type(receipt.get("archive_bytes")) is int
                 and receipt["archive_bytes"]==z.getinfo(archive_name).file_size
                 and type(receipt.get("cli_bytes")) is int
                 and receipt["cli_bytes"]>=100000
                 and receipt.get("observed_game_build")==game_build,
                 "SIMC_ARTIFACT_RECEIPT_DIGEST_INVALID")
            smoke=z.read("display_build.txt").decode("utf8",errors="replace")
            need("simulationcraft" in smoke.lower()
                 and game_build in SMOKE_BUILD.findall(smoke),
                 "SIMC_ARTIFACT_SMOKE_MISMATCH")
            h=hashlib.sha256();count=0;start=b""
            with z.open(archive_name) as stream:
                for chunk in iter(lambda:stream.read(1024*1024),b""):
                    if not count:start=chunk[:6]
                    count+=len(chunk)
                    need(count<=MAX_ARCHIVE,"SIMC_ARTIFACT_ARCHIVE_TOO_LARGE")
                    h.update(chunk)
            need(start==MAGIC and count==receipt["archive_bytes"]
                 and h.hexdigest()==archive_sha,
                 "SIMC_ARTIFACT_ARCHIVE_DIGEST_MISMATCH")
            return {"archive_name":archive_name,"archive_sha256":archive_sha,
                    "archive_bytes":count,"cli_sha256":cli_sha,
                    "source_sha":source_sha,"game_build":game_build,
                    "artifact_sha256":digest(path),
                    "receipt_sha256":hashlib.sha256(
                        z.read("build_receipt.json")).hexdigest(),
                    "origin_authenticated":False,
                    "binary_embedded_build_checked_by_installer":False}
    except (zipfile.BadZipFile,zipfile.LargeZipFile,RuntimeError,EOFError) as exc:
        raise ArtifactBlocked("SIMC_ARTIFACT_ZIP_UNREADABLE") from exc

def copy_inner_archive(artifact_path,target,info):
    artifact_path=pathlib.Path(artifact_path)
    need(artifact_path.is_file() and not artifact_path.is_symlink() and
         digest(artifact_path)==info["artifact_sha256"],
         "SIMC_ARTIFACT_ZIP_CHANGED")
    h=hashlib.sha256();size=0
    with zipfile.ZipFile(artifact_path) as z:
        need(_members(z)==info["archive_name"],
             "SIMC_ARTIFACT_MEMBERS_CHANGED")
        with z.open(info["archive_name"]) as src,open(target,"wb") as dst:
            for chunk in iter(lambda:src.read(1024*1024),b""):
                size+=len(chunk)
                need(size<=MAX_ARCHIVE,"SIMC_ARTIFACT_ARCHIVE_TOO_LARGE")
                h.update(chunk);dst.write(chunk)
    need(size==info["archive_bytes"] and
         h.hexdigest()==info["archive_sha256"],
         "SIMC_ARTIFACT_ARCHIVE_CHANGED")
    with pathlib.Path(target).open("rb") as f:
        need(f.read(6)==MAGIC,"SIMC_ARTIFACT_MAGIC_CHANGED")
    return {"sha256":h.hexdigest(),"bytes":size}
