#!/usr/bin/env python3
"""GitHub Actions always-run checkpoint for full level-11 experimental Native.

No internet or SimC. Exact raw source bytes can be restored only at original
output absolute path and MUST be v291 authenticated with cache_only=True.
"""
import hashlib
import json
import pathlib

from runner import v308_dense_native_checkpoint as raw

OUTPUT=pathlib.Path("out/p2_v307_full11_real_once").resolve()
RECEIPT=OUTPUT/"receipt.json"
ARCHIVE=OUTPUT/"full_original_v291_cases.zip"
PROOF=OUTPUT/"full_original_v291_cases_proof.json"


def main():
    if not RECEIPT.is_file():
        print("P2_V307_CHECKPOINT_NO_PREPARED_SESSION",flush=True)
        return
    doc=json.loads(RECEIPT.read_text(encoding="utf8"))
    stage=doc.get("stage_output_dir")
    if not stage:
        print("P2_V307_CHECKPOINT_NO_NATIVE_STAGE",flush=True)
        return
    out=pathlib.Path(stage)
    journal=out/"V291_JOURNAL.jsonl"
    if not journal.is_file() or journal.stat().st_size==0:
        print("P2_V307_CHECKPOINT_NO_COMMITTED_NATIVE",flush=True)
        return
    result=raw.export_checkpoint(out,ARCHIVE)
    validated=raw.verify_checkpoint(ARCHIVE,result["sha256"])
    if validated["committed_cases"]!=result["committed_cases"]:
        raise RuntimeError("P2_V307_CHECKPOINT_CASE_COUNT_DISAGREES")
    proof={
        "schema":"p2_v307_full11_original_checkpoint_receipt_v1",
        "native_execution_status":doc.get("status"),
        "source_profile_sha256":doc.get("source_profile_sha256"),
        "source_scenario_sha256":doc.get("source_scenario_sha256"),
        "binary_sha256":doc.get("binary_sha256"),
        "season_build":doc.get("season_build"),
        "cases":result["committed_cases"],
        "original_full_raw_sha256":result["sha256"],
        "source_original_output_absolute_path":stage,
        "archive_bytes":result["zip_bytes"],
        "original_raw_json2_and_input_receipts_preserved":True,
        "verified_raw_archive_sha256_and_members":True,
        "portable_to_other_absolute_workspaces_without_revalidation":False,
        "cross_run_replay_verified":False,
        "v291_cache_only_reauthentication_required_after_restore":True,
    }
    PROOF.write_text(json.dumps(proof,sort_keys=True,indent=2)+"\n")
    print("P2_V307_FULL_NATIVE_CHECKPOINT_SAVED",
          json.dumps(proof,sort_keys=True),flush=True)


if __name__=="__main__":
    main()
