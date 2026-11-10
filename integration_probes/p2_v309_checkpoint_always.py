#!/usr/bin/env python3
"""Always checkpoint all v309 NEW native cases at their exact original path.

Historic original11 remains a separately pinned 2800-case artifact. This
saves NEW v309 25% origin session's original input/JSON2/receipt/session
without pretending that the old run is current-session cache.
"""
import json
import pathlib

from runner import v308_dense_native_checkpoint as raw

ROOT=pathlib.Path("out/p2_v309_21_progressive_once").resolve()
REPORT=ROOT/"receipt.json"
ARCHIVE=ROOT/"new21_original_exact_native_checkpoint.zip"
PROOF=ROOT/"new21_original_exact_checkpoint_proof.json"


def main():
    if not REPORT.is_file():
        print("V309_NO_PREPARED_SESSION_TO_CHECKPOINT",flush=True)
        return
    doc=json.loads(REPORT.read_text(encoding="utf8"))
    path=doc.get("stage_output_dir")
    if not path:
        print("V309_NO_NATIVE_STAGE_TO_CHECKPOINT",flush=True)
        return
    output=pathlib.Path(path)
    journal=output/"V291_JOURNAL.jsonl"
    if not journal.is_file() or journal.stat().st_size==0:
        print("V309_NO_COMMITTED_NEW_NATIVE_TO_CHECKPOINT",flush=True)
        return
    result=raw.export_checkpoint(output,ARCHIVE)
    checked=raw.verify_checkpoint(ARCHIVE,result["sha256"])
    if checked["committed_cases"]!=result["committed_cases"]:
        raise RuntimeError("V309_EXACT_RAW_NATIVE_CHECKPOINT_COUNT_DRIFT")
    record={
        "schema":"p2_v309_new21_exact_raw_checkpoint_v1",
        "original_11_was_current_exact_cache":False,
        "origin11_historical_raw_sha256":
            doc["old_original_raw_checkpoint_expected_sha256"],
        "new21_session_original_raw_sha256":result["sha256"],
        "new21_session_cases":result["committed_cases"],
        "new21_original_stage_path":str(output),
        "new21_archive_bytes":result["zip_bytes"],
        "new21_session_sha256_verified":True,
        "future_cross_job_replay_completed":False,
        "exact_absolute_path_and_source_restoration_required":True,
        "new21_cached_cases_can_be_reauthenticated_by_v291":True,
        "status_at_archive":doc["status"],
        "source_profile_sha256":doc.get("new_source_profile_sha256"),
        "source_scenario_digest":doc.get("new_source_scenario_digest"),
        "policy_sha256_sealed":True,
    }
    PROOF.write_text(json.dumps(record,sort_keys=True,indent=2)+"\n")
    print("V309_NEW21_25_RAW_CHECKPOINT_SAVED",
          json.dumps(record,sort_keys=True),flush=True)


if __name__=="__main__":
    main()
