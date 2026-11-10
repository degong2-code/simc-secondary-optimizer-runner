"""v308 isolated raw Native checkpoint archive for dense v307 experiments.

Preserves every v291 journal case's ORIGINAL input.simc, JSON2, receipt,
attempt marker and session seal. Unlike compact CSV/JSONL, these exact bytes
can be reauthenticated when the original source/profile/binary/path are
available. Export and restore do not certify SimC themselves: v291.run()
MUST validate the restored original Native case bytes before further Native.

Restoration is deliberately SAME-ABSOLUTE-OUTPUT-PATH ONLY. Arbitrary
relocation of SimC json2 destinations requires v292-style case-by-case
source/path rewrite and validator re-ingestion, not zip extraction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import tempfile
import zipfile

SCHEMA="v308_exact_path_v291_raw_native_checkpoint_v1"
MAX_CASES=10000
MAX_MEMBER_BYTES=40_000_000
MAX_EXPANDED_BYTES=5_000_000_000
MAX_ZIP_BYTES=1_500_000_000
SHA=re.compile(r"[0-9a-f]{64}\Z")
CASE=re.compile(r"cases/case_[0-9]{5}/(V065_PROGRESS.json|V292_ORIGIN.json|native/(input.simc|result.json|native_receipt.json))\Z")
ROOT_FILES=("V291_SESSION.json","V291_JOURNAL.jsonl","V291_PROGRESS.json",
            "V291_RESULT.json","V291_PENDING.json")
STAGE_FILES=("manifest.json","profile.simc","scenario.json","fillers.json")


class CheckpointBlocked(ValueError):
    pass


def need(ok,reason):
    if not ok:
        raise CheckpointBlocked(reason)


def sha256(path):
    digest=hashlib.sha256()
    with pathlib.Path(path).open("rb") as inp:
        for block in iter(lambda:inp.read(1024*1024),b""):
            digest.update(block)
    return digest.hexdigest()


def archive_members(output):
    output=pathlib.Path(output).resolve(strict=True)
    need(output.is_dir() and not output.is_symlink() and
         (output/"V291_SESSION.json").is_file() and
         (output/"V291_JOURNAL.jsonl").is_file(),
         "V308_VERIFIED_V291_OUTPUT_REQUIRED")
    journal=(output/"V291_JOURNAL.jsonl").read_bytes().splitlines()
    need(1<=len(journal)<=MAX_CASES,"V308_ORIGINAL_JOURNAL_CASE_COUNT")
    records=[json.loads(line) for line in journal]
    need(all(type(r) is dict and r.get("index")==i
             for i,r in enumerate(records)),
         "V308_ORIGINAL_JOURNAL_INDEX_DRIFT")
    paths=[]
    for name in ROOT_FILES:
        path=output/name
        if path.is_file():
            paths.append((name,path))
    for i in range(len(records)):
        root="cases/case_%05d/"%i
        for name in ("V065_PROGRESS.json",
                     "native/input.simc","native/result.json",
                     "native/native_receipt.json"):
            p=output/root/name
            need(p.is_file(),"V308_ORIGINAL_CASE_RAW_PROOF_MISSING")
            paths.append((root+name,p))
    # A recorded-but-uncommitted Native attempt must remain fail-closed.
    partial=output/"cases"/("case_%05d"%len(records))
    if partial.is_dir():
        for name in ("V065_PROGRESS.json","native/input.simc",
                     "native/result.json","native/native_receipt.json"):
            p=partial/name
            if p.is_file():
                paths.append(("cases/"+partial.name+"/"+name,p))
    for name in STAGE_FILES:
        p=output.parent/name
        if p.is_file():
            paths.append(("stage/"+name,p))
    need(len(paths)==len({x[0] for x in paths}),
         "V308_DUPLICATE_ARCHIVE_PATH")
    return output,records,paths


def _metadata_path(archive):
    return pathlib.Path(str(archive)+".sha256")


def export_checkpoint(output,archive):
    output,rows,paths=archive_members(output)
    archive=pathlib.Path(archive).resolve()
    need(not archive.exists() and
         archive != output and not output in archive.parents,
         "V308_ARCHIVE_MUST_BE_NEW_OUTSIDE_CASE_ROOT")
    archive.parent.mkdir(parents=True,exist_ok=True)
    temp=archive.parent/("."+archive.name+".partial")
    need(not temp.exists(),"V308_UNFINISHED_ARCHIVE_ALREADY_EXISTS")
    entries=[]
    total_bytes=0
    try:
        with zipfile.ZipFile(temp,"x",zipfile.ZIP_DEFLATED,
                             compresslevel=5,allowZip64=True) as zipout:
            for key,p in paths:
                need(p.is_file() and not p.is_symlink() and
                     p.stat().st_size<=MAX_MEMBER_BYTES,
                     "V308_NONREGULAR_OR_OVERSIZED_FILE")
                size=p.stat().st_size
                total_bytes+=size
                need(total_bytes<=MAX_EXPANDED_BYTES,
                     "V308_EXPANSION_LIMIT")
                digest=sha256(p)
                zipout.write(p,key)
                entries.append({"name":key,"size":size,
                                "sha256":digest})
            envelope={"schema":SCHEMA,
                      "original_output_path":str(output),
                      "session_sha256":sha256(
                          output/"V291_SESSION.json"),
                      "journal_sha256":sha256(
                          output/"V291_JOURNAL.jsonl"),
                      "committed_cases":len(rows),
                      "expanded_bytes":total_bytes,
                      "entries":entries,
                      "restore_requires_exact_original_output_path":True,
                      "restore_never_proves_native_without_v291_replay":True}
            zipout.writestr("V308_CHECKPOINT_MANIFEST.json",
                            json.dumps(envelope,sort_keys=True,
                                       separators=(",",":"),allow_nan=False))
        need(temp.stat().st_size<=MAX_ZIP_BYTES,
             "V308_COMPRESSED_ARCHIVE_OVERSIZE")
        os.replace(temp,archive)
        digest=sha256(archive)
        _metadata_path(archive).write_text(digest+"  "+archive.name+"\n")
        return {"schema":SCHEMA,"archive":str(archive),
                "sha256":digest,"committed_cases":len(rows),
                "archived_files":len(entries),
                "zip_bytes":archive.stat().st_size,
                "expanded_bytes":total_bytes}
    finally:
        if temp.exists():
            temp.unlink()


def verify_checkpoint(archive,expected_sha256):
    archive=pathlib.Path(archive).resolve(strict=True)
    need(type(expected_sha256) is str and SHA.fullmatch(expected_sha256) and
         archive.is_file() and not archive.is_symlink() and
         0<archive.stat().st_size<=MAX_ZIP_BYTES and
         sha256(archive)==expected_sha256,
         "V308_ORIGINAL_ARCHIVE_SHA_DRIFT")
    with zipfile.ZipFile(archive) as z:
        infos=z.infolist()
        names=[x.filename for x in infos]
        need(len(names)==len(set(names)) and
             "V308_CHECKPOINT_MANIFEST.json" in names,
             "V308_DUPLICATE_OR_MISSING_MANIFEST")
        meta=z.getinfo("V308_CHECKPOINT_MANIFEST.json")
        need(meta.file_size<=5_000_000,"V308_MANIFEST_SIZE_CAP")
        raw=z.read("V308_CHECKPOINT_MANIFEST.json")
        doc=json.loads(raw)
        need(doc.get("schema")==SCHEMA and
             type(doc.get("committed_cases")) is int and
             1<=doc["committed_cases"]<=MAX_CASES and
             type(doc.get("expanded_bytes")) is int and
             doc["expanded_bytes"]<=MAX_EXPANDED_BYTES and
             type(doc.get("entries")) is list,
             "V308_MANIFEST_SCHEMA")
        member={x["name"]:x for x in doc["entries"]}
        need(len(member)==len(doc["entries"]) and
             set(names)==set(member)|{"V308_CHECKPOINT_MANIFEST.json"} and
             {"V291_SESSION.json","V291_JOURNAL.jsonl"}<=set(member),
             "V308_MISSING_OR_FOREIGN_MEMBERS")
        # The manifest is not a self-authenticating certificate that all
        # Native cases exist: bind its declared case count to the original
        # journal and insist on ALL raw case input/JSON2/receipt/progress
        # members before accepting a re-packed SHA-correct but incomplete ZIP.
        journal_info=z.getinfo("V291_JOURNAL.jsonl")
        need(journal_info.file_size<=20_000_000,
             "V308_JOURNAL_SIZE_CAP")
        lines=z.read("V291_JOURNAL.jsonl").splitlines()
        need(len(lines)==doc["committed_cases"],
             "V308_MANIFEST_CASE_COUNT_JOURNAL_DRIFT")
        required={
            "cases/case_%05d/%s"%(i,p)
            for i in range(doc["committed_cases"])
            for p in ("V065_PROGRESS.json","native/input.simc",
                      "native/result.json","native/native_receipt.json")
        }
        need(required <= set(member),
             "V308_MISSING_COMPLETE_ORIGINAL_RAW_CASE")
        need(type(doc.get("original_output_path")) is str and
             pathlib.Path(doc["original_output_path"]).is_absolute(),
             "V308_ORIGINAL_OUTPUT_ABSOLUTE_REQUIRED")
        expanded=0
        for item in infos:
            path=item.filename
            mode=item.external_attr>>16 & 0o170000
            need(not item.is_dir() and mode in (0,0o100000) and
                 (path=="V308_CHECKPOINT_MANIFEST.json" or
                  path in ROOT_FILES or
                  (path.startswith("stage/") and
                   path.removeprefix("stage/") in STAGE_FILES) or
                  CASE.fullmatch(path) is not None),
                 "V308_INVALID_ARCHIVE_PATH_OR_TYPE")
            if path not in member:
                continue
            saved=member[path]
            need(type(saved.get("size")) is int and
                 0<=saved["size"]<=MAX_MEMBER_BYTES and
                 saved["size"]==item.file_size and
                 type(saved.get("sha256")) is str and
                 SHA.fullmatch(saved["sha256"]),
                 "V308_MEMBER_BOUND_OR_IDENTITY")
            expanded+=item.file_size
            need(expanded<=MAX_EXPANDED_BYTES,"V308_ARCHIVE_EXPANSION_LIMIT")
            h=hashlib.sha256()
            with z.open(item) as data:
                for block in iter(lambda:data.read(1024*1024),b""):
                    h.update(block)
            need(h.hexdigest()==saved["sha256"],
                 "V308_MEMBER_SHA_DRIFT")
        need(expanded==doc["expanded_bytes"],
             "V308_MANIFEST_EXPANDED_TOTAL_DRIFT")
        need(doc["session_sha256"]==member["V291_SESSION.json"]["sha256"]
             and doc["journal_sha256"]==
                    member["V291_JOURNAL.jsonl"]["sha256"],
             "V308_SESSION_OR_JOURNAL_SHA_DRIFT")
        return {"schema":SCHEMA,
                "original_output_path":doc["original_output_path"],
                "committed_cases":doc["committed_cases"],
                "archive_sha256":expected_sha256,
                "expanded_bytes":expanded,
                "files_verified":len(member),
                "native_reexecuted":False,
                "native_cases_reauthenticated_by_v291":False}


def restore_same_absolute_path(archive,sha,output):
    """Restore verified original bytes only to their original sealed path.

    Caller MUST then invoke runner.run(cache_only=True) with EXACT original
    source/profile/binary/policy, which authenticates every Native case.
    """
    report=verify_checkpoint(archive,sha)
    target=pathlib.Path(output).resolve()
    need(str(target)==report["original_output_path"] and
         not target.exists(),"V308_RESTORE_EXACT_EMPTY_OUTPUT_REQUIRED")
    need(not target.is_symlink(),"V308_RESTORE_SYMLINK_OUTPUT")
    tmp=pathlib.Path(tempfile.mkdtemp(
        prefix=".v308-restore-",dir=target.parent))
    try:
        with zipfile.ZipFile(archive) as src:
            for info in src.infolist():
                if info.filename=="V308_CHECKPOINT_MANIFEST.json" or \
                   info.filename.startswith("stage/"):
                    continue
                filename=tmp/info.filename
                filename.parent.mkdir(parents=True,exist_ok=True)
                with src.open(info) as inp,filename.open("wb") as out:
                    shutil.copyfileobj(inp,out,1024*1024)
        need(not target.exists(),"V308_RESTORE_TARGET_RACE")
        os.replace(tmp,target)
    finally:
        if tmp.exists():
            shutil.rmtree(tmp)
    return {"schema":SCHEMA,"restored_path":str(target),
            "committed_cases":report["committed_cases"],
            "native_reexecuted":False,
            "v291_reauthentication_required":True}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True)
    parser.add_argument("--archive",required=True)
    args=parser.parse_args()
    report=export_checkpoint(args.output,args.archive)
    checked=verify_checkpoint(args.archive,report["sha256"])
    need(checked["committed_cases"]==report["committed_cases"],
         "V308_POST_EXPORT_SELF_VERIFICATION_FAILED")
    print("V308_EXACT_NATIVE_CHECKPOINT_READY",
          json.dumps(report,sort_keys=True),flush=True)


if __name__=="__main__":
    main()
