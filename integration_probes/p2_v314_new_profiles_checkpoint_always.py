#!/usr/bin/env python3
"""Always export exact original v290/v312 native checkpoint per v314 case.

No new SimC. Each zip is an independent v291 source-bound object;
cross-job restoring the session as cache is NOT established by export.
"""
from __future__ import annotations

import json
import os
import pathlib

from runner import v308_dense_native_checkpoint as checkpoint
from runner import v314_fresh_eight_spec_matrix_contract as matrix

ROOT=pathlib.Path("out/p2_v314_multispec_matrix").resolve()


def main():
    case_id=os.getenv("P2_V314_CASE_ID","")
    case,_=matrix.select(case_id)
    folder=ROOT/case["id"]
    receipt=folder/"receipt.json"
    if not receipt.is_file():
        print("P2_V314_NO_NATIVE_RECEIPT_TO_CHECKPOINT",flush=True)
        return
    document=json.loads(receipt.read_text())
    output={}
    for label in ("v290_original","v312_model_guided"):
        original=document.get("original_output_paths",{}).get(label)
        if not original:
            continue
        output_dir=pathlib.Path(original)
        journal=output_dir/"V291_JOURNAL.jsonl"
        if not journal.is_file() or not journal.stat().st_size:
            continue
        archive=folder/("v314_"+label+"_original_native.zip")
        item=checkpoint.export_checkpoint(output_dir,archive)
        verified=checkpoint.verify_checkpoint(archive,item["sha256"])
        if verified["committed_cases"]!=item["committed_cases"]:
            raise ValueError("V314_ORIGINAL_SOURCE_CASES_NOT_VERIFIED")
        output[label]={
            "zip_sha256":item["sha256"],"case_count":item["committed_cases"],
            "zip_bytes":item["zip_bytes"],
            "all_original_case_member_sha_verified":True,
            "new_native_generated_for_checkpoint":0,
            "cross_session_exact_cache_reuse_authorized":False}
    record={
        "schema":"p2_v314_multispec_original_native_checkpoint_v1",
        "case_id":case_id,"status":document["status"],
        "source_profile_sha256":document.get("source_profile_sha256"),
        "no_historical_dps_cache_reused":True,
        "original_case_sources":output}
    if output:
        (folder/"checkpoint_proof.json").write_text(
            json.dumps(record,sort_keys=True,indent=2)+"\n")
    print("P2_V314_ORIGINAL_NATIVE_CHECKPOINT",json.dumps(
        record,sort_keys=True),flush=True)


if __name__=="__main__":
    main()
