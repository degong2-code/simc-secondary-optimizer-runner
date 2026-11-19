#!/usr/bin/env python3
"""One source-pinned real-current-build v216/v212 enchant M1/M2 attempt.

Reuse the v610 production admission diagnostic, but use a **new** Windows
CLI binary built from the exact same-build upstream SimC source in CI.
No historical G/J/F/O values or prior 70783 Native cache can be promoted.
The initial binary has no published official SHA; bind the *observed* binary
digest to its independently checked exact source Git commit in this run.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner"),str(ROOT/"integration_probes")]
import p1_v610_real_installed_enchant_one_build as reused

BUILD="12.1.5.70961"
REV="9933ffb946fb55b1fa66657b848f519ac19006e1"
SCHEMA="p1_v611_real_new_simc_70961_original_enchant_build_v1"


def digest(path):
    obj=hashlib.sha256()
    with pathlib.Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            obj.update(block)
    return obj.hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--simc",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--source-commit-file",required=True)
    arg=ap.parse_args()
    folder=pathlib.Path(arg.out).resolve()
    folder.mkdir(parents=True,exist_ok=True)
    commit_file=pathlib.Path(arg.source_commit_file).resolve(strict=True)
    commit=commit_file.read_text(encoding="utf8").strip()
    if commit!=REV:
        raise SystemExit("V611_EXACT_SIMC_70961_SOURCE_COMMIT_REQUIRED")
    binary=pathlib.Path(arg.simc).resolve(strict=True)
    if binary.name.lower()!="simc.exe":
        raise SystemExit("V611_SOURCE_BUILT_WINDOWS_CLI_REQUIRED")
    observed=digest(binary)
    # Producer code checks game build from independent retail discovery,
    # SimC CLI banner and this source-bound binary SHA before any new stage.
    reused.BUILD=BUILD
    reused.REV=REV
    reused.EXE_SHA=observed
    reused.SCHEMA=SCHEMA
    result=reused.run(binary,folder)
    output=folder/"V610_REAL_ENCHANT_ADMISSION_ONE_BUILD.json"
    target=folder/"V611_REAL_70961_ENCHANT_ADMISSION_ONE_BUILD.json"
    if output.is_file():
        details=json.loads(output.read_text("utf8"))
        details["schema"]=SCHEMA
        details["simc_binary_source"]="COMPILED_THIS_RUN_FROM_EXACT_PINNED_UPSTREAM_GIT_HEAD"
        details["simc_source_git_commit_verified"]=commit
        details["simc_binary_sha256_observed_this_run"]=observed
        details["not_a_previously_published_official_binary"]=True
        target.write_text(json.dumps(details,ensure_ascii=False,indent=2,
                           sort_keys=True,allow_nan=False)+"\n",encoding="utf8")
        output.unlink()
    return result


if __name__=="__main__":
    sys.exit(main())
