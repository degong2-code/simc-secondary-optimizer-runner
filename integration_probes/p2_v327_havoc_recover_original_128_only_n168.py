#!/usr/bin/env python3
"""v327 only continue new Havoc N research from SHA-verified prior original 128."""
from __future__ import annotations
import os,json,hashlib,zipfile,pathlib,shutil
from integration_probes import p2_v327_havoc_new_user_three_seed_n_real_once as study
from runner import v291_durable_multiscale_native_runner as native

PRE=pathlib.Path("out/v327_original_actions").resolve()
ROOT=study.ROOT
RECEIPT_SHA="2737b8933c18b2a99f7daa8f77c6bcd9dfaa139e102c4e639c878881f2740b4d"
PROFILE_SHA="6536559211045e6574cb80c66d651a7976777be863a448891ac437882435ef05"
ZIPS={
"v290_original":"0e00b79f75e6840984d4e50dba77b5ba92f547d8699748ad0ca5fcd4e9cc1c0c",
"v318_idea001":"6b88f3f0fb450367e47d8e9510155507937f8a8197705aecb00e8c7d6d6a3b18"}
EXPECTED={"v290_original":(57,7,4235),"v318_idea001":(58,6,3950)}
class RecoveryBlocked(ValueError):pass
def need(ok,msg):
    if not ok:raise RecoveryBlocked("V327_RECOVERY_"+msg)
def sha_bytes(v):return hashlib.sha256(v).hexdigest()
def sha_file(p):return sha_bytes(pathlib.Path(p).read_bytes())

def original_receipt(raw):
    need(sha_bytes(raw)==RECEIPT_SHA,"ORIGINAL_ACTION_RECEIPT_SHA")
    d=json.loads(raw)
    need(d["status"]=="BLOCKED_OR_PARTIAL_V326Blocked"
         and d["first_error_code"]==
             "V326_FRESH_DEVASTATION_SOURCE_IDENTITY_AUTO_T_REQUIRED"
         and d["case"]==study.CASE
         and d["character"]["character_class"]=="demonhunter"
         and d["character"]["character_spec"]=="havoc"
         and d["manual_final_T"] is None
         and d["source_profile_sha256"]==PROFILE_SHA
         and d["fresh_profile_generated_once_for_both_arms"] is True
         and d["source_from_old_completed_simc_profile"] is False
         and d["historical_dps_native_cache_imported"] is False
         and d["environment_native_calls"]==3
         and d["auto_final_T"]==3107
         and d["environment_budget"]["B"]==
             d["environment_budget"]["G"]+d["environment_budget"]["J"]+
             d["environment_budget"]["F"]
         and d["pairwise"]["same_fresh_user_profile"] is True
         and d["pairwise"]["equal_native_calls"] is True
         and d["pairwise"]["equal_simc_iterations"] is False,
         "ORIGINAL_FRESH_HAVOC_AUTO_T_CONTRACT")
    return d

def restore(d):
    need(not ROOT.exists(),"RECOVERY_WORKSPACE_MUST_START_EMPTY")
    ROOT.mkdir(parents=True)
    shutil.copyfile(PRE/"receipt.json",ROOT/"original_failed_action_receipt.json")
    for arm,zip_sha in ZIPS.items():
        original=PRE/(arm+"_original_native.zip")
        need(original.is_file() and sha_file(original)==zip_sha
             and d["arms"][arm]["original_native_archive_sha256"]==zip_sha
             and d["arms"][arm]["same_source_profile_sha256"]==PROFILE_SHA
             and d["arms"][arm]["native_calls"]==64
             and d["arms"][arm]["actual_total_simc_iterations"]==EXPECTED[arm][2],
             "SOURCE_SEALED_ORIGINAL_ARCHIVE_REQUIRED")
        dest=ROOT/arm
        dest.mkdir()
        with zipfile.ZipFile(original) as archive:
            for name in archive.namelist():
                p=pathlib.PurePosixPath(name)
                need(not p.is_absolute() and ".." not in p.parts,
                     "ZIP_PATH_UNSAFE")
            archive.extractall(dest)
        shutil.copyfile(original,ROOT/(arm+"_original_native.zip"))
        jf=dest/"V291_JOURNAL.jsonl"
        need(sha_file(jf)==d["arms"][arm]["journal_sha256"],
             "JOURNAL_BYTE_SHA_MISMATCH")
        rows=native._load_journal(jf)
        need(len(rows)==64 and
             [r["index"] for r in rows]==list(range(64)) and
             sum(r["iterations"]==35 for r in rows)==EXPECTED[arm][0] and
             sum(r["iterations"]==320 for r in rows)==EXPECTED[arm][1] and
             sum(r["iterations"] for r in rows)==EXPECTED[arm][2],
             "ORIGINAL_64_CASE_ITERATION_IDENTITY")
        for r in rows:
            folder=dest/"cases"/("case_%05d"%r["index"])/"native"
            inp=folder/"input.simc"
            output=folder/"result.json"
            need(r["source"]=="NEW_NATIVE"
                 and r["final_T"]==3107
                 and sha_file(inp)==r["input_sha256"]
                 and sha_file(output)==r["native_sha256"],
                 "EXACT_ORIGINAL_NATIVE_INPUT_JSON_SHA")
            sim=(json.loads(output.read_bytes()).get("sim") or {})
            players=sim.get("players") or []
            opts=sim.get("options") or {}
            need(len(players)==1
                 and str(players[0].get("specialization","")).lower().startswith("havoc")
                 and opts.get("iterations")==r["iterations"]
                 and opts.get("seed")==r["simc_seed"],
                 "ACTUAL_ORIGINAL_NATIVE_SEED_SPEC_ITERATIONS")
    return True

def main():
    need(os.getenv("P2_V327_REUSE_ORIGINAL_128_NATIVE_ONLY")=="1",
         "EXPLICIT_RECOVERY_NATIVE_ONCE")
    binary=pathlib.Path("out/binary/simc").resolve(strict=True)
    raw=(PRE/"receipt.json").read_bytes()
    d=original_receipt(raw)
    need(sha_file(binary)==d["simc_binary_sha256"]==
         study.fresh.fresh.BINARY_SHA,"EXACT_ORIGINAL_BINARY_REQUIRED")
    restore(d)
    # Only the in-memory derived status changes; original failed Action bytes
    # are preserved and never relabelled as success.
    recovered=dict(d)
    recovered["status"]="COMPLETE_TWO_ARMS_EQUAL_CALLS_ITERATIONS_UNEQUAL"
    result=study.callback(recovered,binary,ROOT)
    need(result["research_native_count"]==168,"ONLY_168_NEW_RESEARCH_NATIVE")
    receipt={
       "schema":"p2_v327_original128_verified_only_new168_research_v1",
       "status":"RECOVERY_RESEARCH_168_COMPLETE",
       "original_failed_actions_run":42955908381,
       "original_failed_receipt_sha256":RECEIPT_SHA,
       "old_native_redone":0,
       "new_research_native":168,
       "source_profile_sha256":PROFILE_SHA,
       "auto_final_T":3107,
       "original_precisions":{"v290_original":7,"v318_idea001":6},
       "original_total_iterations":{"v290_original":4235,"v318_idea001":3950},
       "original_research_zip_sha256":result["original_research_zip_sha256"],
       "quality_replay":result["quality_replay"],
       "no_global_optimum_or_95_equivalence_claim":True}
    (ROOT/"recovery_receipt.json").write_text(json.dumps(
       receipt,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf8")
    print("V327_RECOVERED_N168_NATIVE_SUCCESS",json.dumps({
       "previous_native_reexecuted":0,"new_native":168,
       "source_sha":PROFILE_SHA,
       "by_N":{k:x["final_success_fraction"] for k,x in
               receipt["quality_replay"]["by_N"].items()}},sort_keys=True),flush=True)
    return receipt
if __name__=="__main__":main()
