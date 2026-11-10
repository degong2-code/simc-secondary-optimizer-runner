#!/usr/bin/env python3
"""Always preserve ORIGINAL accepted v312/v290 real Native files per policy.

Independent v291 sessions each store native input.simc/JSON2/receipt and
SHA session/journal. A checkpoint is NOT cross-session cache authorization.
No further SimC is run here; partial sessions are preserved if supported.
"""
from __future__ import annotations

import json
import pathlib

from runner import v308_dense_native_checkpoint as raw

ROOT=pathlib.Path("out/p2_v312_real_equal_1008_once").resolve()
RECEIPT=ROOT/"receipt.json"
PROOF=ROOT/"checkpoint_proof.json"


def main():
    if not RECEIPT.is_file():
        print("P2_V312_NO_REAL_RECEIPT_FOR_ORIGINAL_CHECKPOINT",flush=True)
        return
    doc=json.loads(RECEIPT.read_text())
    proofs={}
    for key,label in (("v312_model_guided","v312_model"),
                      ("v290_original","v290_original")):
        path=doc.get("paths",{}).get(key)
        if not path:
            continue
        output=pathlib.Path(path)
        journal=output/"V291_JOURNAL.jsonl"
        if not journal.is_file() or journal.stat().st_size==0:
            continue
        archive=ROOT/(label+"_exact_original_native_checkpoint.zip")
        result=raw.export_checkpoint(output,archive)
        verified=raw.verify_checkpoint(archive,result["sha256"])
        if verified["committed_cases"]!=result["committed_cases"]:
            raise RuntimeError("V312_ORIGINAL_POLICY_CASE_COUNT_MISMATCH")
        proofs[key]={
            "original_zip_sha256":result["sha256"],
            "committed_original_native_cases":result["committed_cases"],
            "original_output_path":str(output),
            "archive_bytes":result["zip_bytes"],
            "case_member_shas_verified":True,
            "cross_job_cache_only_replay_proven":False}
    if not proofs:
        print("P2_V312_NO_COMMITTED_REAL_NATIVE_TO_CHECKPOINT",flush=True)
        return
    record={
        "schema":"p2_v312_v290_equal_native_original_checkpoint_v1",
        "status_at_checkpoint":doc["status"],
        "source_profile_sha256":doc["source_profile_sha256"],
        "binary_sha256":doc["binary_sha256"],
        "policies":proofs,
        "no_historical_v307_v309_v310_cache_imported":True,
        "cross_run_exact_cache_not_claimed":True}
    PROOF.write_text(json.dumps(record,sort_keys=True,indent=2)+"\n")
    print("P2_V312_REAL_AB_ORIGINAL_NATIVE_CHECKPOINT_SAVED",
          json.dumps(record,sort_keys=True),flush=True)


if __name__=="__main__":
    main()
