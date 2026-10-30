#!/usr/bin/env python3
"""v178: real current-season v177 user session: stop after 2 Native, resume 4.

A temporary diagnostic callback requests cancellation only AFTER v065 has
sealed two real Native outputs; no optimizer code is replaced or mocked.
Cancellation is enforced by unchanged v094 between candidates, with the
existing v106 worker/state and exact SHA-verified resume/cache path.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,sys
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v106_user_session_controller as sessions
import v094_durable_inclusive_adaptive_runner as durable

SCHEMA="v178_one_current_season_real_cancel_resume_v1"
REVISION="7bc10711b5"
SIMC_SHA="64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e"

def need(condition,code):
    if not condition:raise AssertionError("V178_"+code)
def json_file(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf8"))
def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def cases(folder):
    p=sessions.paths(folder)["native_result"].parent
    return {str(path.relative_to(p)).replace("\\","/"):sha(path)
            for path in sorted(p.rglob("result.json"))
            if (path.parent/"native_receipt.json").is_file()}
def status(folder):
    return json_file(sessions.paths(folder)["state"])["status"]

def run(binary,out):
    binary=pathlib.Path(binary).resolve()
    need(binary.is_file() and sha(binary)==SIMC_SHA,"PINNED_SIMC_BINARY_CHANGED")
    root=pathlib.Path(out).resolve()
    root.mkdir(parents=True,exist_ok=True)
    controls=sessions.standard_controls(("paladin","retribution"))
    user=sessions.user_scenario(controls)
    folder=sessions.store_session(user,root,binary,REVISION,
                                  current_season_product=True)
    need(not sessions.paths(folder)["native_result"].is_file()
         and not cases(folder),"FRESH_USER_SESSION_REQUIRED")
    key_before=json_file(folder/"V106_SESSION_IDENTITY.json")
    underlying=durable.engine.execute_one
    first={"new":0,"cached":0}
    def stop_after_two(req,calibration,binary_arg,case_folder,progress,
                       *args,**kwargs):
        result=underlying(req,calibration,binary_arg,case_folder,progress,
                          *args,**kwargs)
        if result["source"]=="NEW_NATIVE":
            first["new"]+=1
            if first["new"]==2:
                sessions.request_cancel(folder)
        else:
            first["cached"]+=1
        return result
    with mock.patch.object(durable.engine,"execute_one",
                           side_effect=stop_after_two):
        initial_exit=sessions.worker(folder,binary,REVISION)
    need(initial_exit==3 and status(folder)=="CANCELLED_PARTIAL"
         and sessions.paths(folder)["cancel"].exists(),
         "FIRST_RUN_DID_NOT_CANCEL_AT_TWO_COMPLETED_CASES")
    need(first=={"new":2,"cached":0},
         "FIRST_RUN_NATIVE_COUNT_NOT_TWO")
    before=cases(folder)
    need(len(before)==2 and
         set(before)=={"search/seed_00/result.json","search/seed_01/result.json"},
         "FIRST_TWO_SEALED_NATIVE_JSON2_MISSING")
    p=sessions.paths(folder)
    need(not p["final"].is_file(),"CANCELLED_RESULT_WRONGLY_PUBLISHED")
    progress_cancel=json_file(p["progress"])
    need(progress_cancel["new_native_attempts"]==2 and
         progress_cancel["completed_jobs"]==2,
         "CANCELLED_PROGRESS_CUMULATIVE_TWO_DRIFT")
    need(json_file(folder/"V106_SESSION_IDENTITY.json")==key_before,
         "CANCELLED_PRODUCT_SESSION_IDENTITY_DRIFT")
    sessions.clear_cancel(folder)
    resumed={"new":0,"cached":0}
    def observe_resume(req,calibration,binary_arg,case_folder,progress,
                       *args,**kwargs):
        result=underlying(req,calibration,binary_arg,case_folder,progress,
                          *args,**kwargs)
        if result["source"]=="NEW_NATIVE":
            resumed["new"]+=1
        elif result["source"]=="CACHED_VERIFIED_NATIVE":
            resumed["cached"]+=1
        else:
            raise AssertionError("V178_UNEXPECTED_NATIVE_SOURCE:"+str(result["source"]))
        return result
    with mock.patch.object(durable.engine,"execute_one",
                           side_effect=observe_resume):
        resumed_exit=sessions.worker(folder,binary,REVISION)
    need(resumed_exit==0 and status(folder)=="PASS",
         "RESUMED_PRODUCT_DID_NOT_PASS")
    need(resumed=={"new":4,"cached":2},
         "RESUME_DID_NOT_USE_TWO_CACHED_AND_FOUR_NEW")
    after=sessions.native_json2_hashes(folder)
    need(len(after)==6 and
         all(after.get(k)==v for k,v in before.items()),
         "OLD_NATIVE_BYTES_REPLACED_ON_RESUME")
    final=json_file(p["final"])
    report=json_file(p["native_result"])
    need(final["status"]=="PASS_BOUNDED_GENERIC_NATIVE_SEARCH_AND_CACHE"
         and final["native_calls_cumulative"]==6
         and final["cache_hits_this_run"]==2
         and final["user_result"]["confidence_level"]==0.95
         and final["user_result"]["global_optimum_proven"] is False
         and report["new_native_attempts_cumulative"]==6
         and report["verified_cache_hits_this_run"]==2,
         "RESUMED_V094_SIX_CASE_OR_95_RESULT_WRONG")
    original_semantic=final["user_result"]
    replay_exit=sessions.worker(folder,binary,REVISION,cache_only=True)
    need(replay_exit==0 and status(folder)=="PASS_CACHE_ONLY",
         "REPLAY_SIX_VERIFIED_CACHE_FAILED")
    replay=json_file(p["final"])
    proof=json_file(folder/"V112_CACHE_REPLAY_RECEIPT.json")
    need(replay["native_calls_cumulative"]==6
         and replay["cache_hits_this_run"]==6
         and replay["user_result"]==original_semantic
         and proof["additional_native_calls"]==0
         and sessions.native_json2_hashes(folder)==after
         and json_file(folder/"V106_SESSION_IDENTITY.json")==key_before,
         "REPLAY_NATIVE_DATA_OR_SEMANTICS_CHANGED")
    receipt={"schema":SCHEMA,"status":"PASS_REAL_NATIVE_CANCEL_RESUME_CACHE",
        "spec":"paladin/retribution","target_ilvl":334,
        "current_season_product":True,
        "first_worker_exit":initial_exit,"first_worker_state":"CANCELLED_PARTIAL",
        "first_new_native":first["new"],"first_cached_native":first["cached"],
        "cancelled_completed_cases":len(before),
        "resume_worker_exit":resumed_exit,
        "resume_new_native":resumed["new"],
        "resume_existing_SHA_verified_native":resumed["cached"],
        "total_new_native":first["new"]+resumed["new"],
        "cumulative_v094_native":final["native_calls_cumulative"],
        "cache_only_verified":replay["cache_hits_this_run"],
        "cache_only_additional_native":0,
        "unchanged_first_two_result_sha256":before,
        "all_six_native_sha256":after,
        "identity_sha256":sha(folder/"V106_SESSION_IDENTITY.json"),
        "official_final_T":original_semantic["final_T"],
        "observed_first_choice":original_semantic["observed_first_choice"],
        "confirmation_direction_supported_at_95":
           original_semantic["confirmation_pair_direction_supported_at_95"],
        "global_optimum_proven":False,
        "simc_binary_sha256":sha(binary),
        "native_owned_by_original_v094":True}
    (folder/"V178_NATIVE_CANCEL_RESUME_RECEIPT.json").write_text(
         json.dumps(receipt,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
         encoding="utf8")
    return receipt

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--simc",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    args=p.parse_args()
    try:
        receipt=run(args.simc,args.out)
        print("V178_REAL_NATIVE_CANCEL_RESUME_PASS",json.dumps(receipt,
              ensure_ascii=False,sort_keys=True))
        return 0
    except Exception as exc:
        print("V178_BLOCKED:",type(exc).__name__,str(exc),file=sys.stderr)
        return 3

if __name__=="__main__":raise SystemExit(main())
