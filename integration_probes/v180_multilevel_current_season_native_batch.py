#!/usr/bin/env python3
"""v180: six diverse non334 CURRENT season product full adaptive Native sessions.

Explicit bounded one-time matrix, not a new engine. Each uses unchanged v106
user worker -> v098/v096 -> v094 six Native candidates + exact cache-only replay.
All six errors remain isolated; original stdout/JSON2/errors stay in out.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,sys,traceback

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v106_user_session_controller as user

SCHEMA="v180_non334_current_season_six_adaptive_native_v1"
REV="7bc10711b5"
BINARY_SHA="64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e"
CASES=(
 ("warrior","fury",266,"titan_grip_low"),
 ("hunter","beast_mastery",300,"ranged_mid"),
 ("paladin","retribution",321,"two_hand_manual_T"),
 ("rogue","outlaw",330,"dual_one_hand_two_targets"),
 ("evoker","devastation",340,"caster_no_oil"),
 ("mage","frost",344,"caster_upper_edge"),
)
def need(ok,reason):
    if not ok:raise AssertionError("V180_"+reason)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(pathlib.Path(path).read_text(encoding="utf8"))
def save(path,obj):
    path=pathlib.Path(path)
    path.write_text(json.dumps(obj,sort_keys=True,indent=2,
                               ensure_ascii=False)+"\n",encoding="utf8")

def run(binary,out):
    binary=pathlib.Path(binary).resolve()
    need(binary.is_file() and digest(binary.read_bytes())==BINARY_SHA,
         "PINNED_BINARY_SHA_MISMATCH")
    out=pathlib.Path(out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    result={"schema":SCHEMA,"status":"IN_PROGRESS","native_max_total":36,
        "case_count":6,"new_native_calls_confirmed":0,
        "new_native_attempts_reserved":0,
        "cases":[],"no_new_optimizer":True,"v176_physical_reexecution":False}
    path=out/"V180_MULTILEVEL_ADAPTIVE_SUMMARY.json"
    save(path,result)
    for cls,spec,level,label in CASES:
        controls=user.standard_controls((cls,spec))
        controls["ilevel"]=level
        if label=="two_hand_manual_T":
            controls["final_T"]=3500
        if label=="dual_one_hand_two_targets":
            controls["targets"]=2
            controls["duration_seconds"]=180
        if label=="caster_no_oil":
            controls["oil_hands"]=[]
        scenario=user.user_scenario(controls)
        row={"key":cls+"/"+spec,"level":level,"label":label,
             "status":"PREPARED","new_native_reserved":6,
             "manual_final_T":controls["final_T"],"oil_hands":controls["oil_hands"]}
        result["cases"].append(row)
        # Conservative full reservation before each possible worker invocation.
        # A failing Native case cannot cause an automatic retry on this batch.
        result["new_native_attempts_reserved"]+=6
        save(path,result)
        try:
            folder=user.store_session(scenario,out,binary,REV,
                                  current_season_product=True)
            row["session_id"]=folder.name
            row["session_folder"]=str(folder)
            row["status"]="RUNNING_NATIVE"
            save(path,result)
            code=user.worker(folder,binary,REV)
            row["worker_exit"]=code
            progress=user.progress(folder)
            row["progress"]=progress
            row["new_native_confirmed"]=progress.get("native_attempts",0)
            result["new_native_calls_confirmed"]+=row["new_native_confirmed"]
            if code:
                row["status"]="FAIL_REAL_NATIVE_OR_USER_WORKER"
                row["raw_error_log"]=str(user.paths(folder)["log"])
                row["error"]="V106_WORKER_EXIT_"+str(code)+";state="+str(
                    progress.get("worker",{}).get("reason"))
                continue
            p=user.paths(folder)
            final=load(p["final"])
            need(final["status"].startswith("PASS") and
                 final["native_calls_cumulative"]==6 and
                 row["new_native_confirmed"]==6,
                 "SIX_REAL_NATIVE_NOT_COMPLETE:"+label)
            need(final["user_result"]["confidence_level"]==0.95
                 and final["user_result"]["global_optimum_proven"] is False,
                 "RESULT_95_OR_GLOBAL_STATISTICS_DRIFT:"+label)
            r=final["user_result"]
            need(r["final_T"]==r["base_B"]+sum(r["fixed_O"].values()),
                 "O_AND_B_BUDGET_DRIFT:"+label)
            if controls["final_T"] is not None:
                need(r["final_T"]==controls["final_T"],
                     "MANUAL_T_CHANGED:"+label)
            before=user.native_json2_hashes(folder)
            need(len(before)==6,"REAL_SIX_RECEIPTS_MISSING:"+label)
            row.update({"base_B":r["base_B"],"fixed_O":r["fixed_O"],
                        "final_T":r["final_T"],
                        "observed_dps":r["observed_first_choice"]["observed_dps_mean"],
                        "observed_sem":r["observed_first_choice"]["simc_sem"],
                        "observed_first_choice_rating":
                            r["observed_first_choice"]["absolute_rating_T"],
                        "confirmation_direction_supported_at_95":
                            r["confirmation_pair_direction_supported_at_95"],
                        "original_result_sha256":digest(p["native_result"].read_bytes()),
                        "original_six_json2_sha256":before})
            row["status"]="RUNNING_CACHE_ONLY_REPLAY"
            save(path,result)
            # Same identity, exact original six native bytes: no new calls.
            cache_code=user.worker(folder,binary,REV,cache_only=True)
            reread=load(p["final"])
            need(cache_code==0 and
                 reread["cache_hits_this_run"]==6 and
                 reread["native_calls_cumulative"]==6 and
                 reread["user_result"]==r and
                 user.native_json2_hashes(folder)==before,
                 "SIX_CACHE_SHA_REPLAY_DRIFT:"+label)
            row["status"]="PASS_REAL_NATIVE_6_AND_CACHE_6"
            row["verified_cache_hits"]=6
            row["cache_only_new_native"]=0
        except Exception as ex:
            row["status"]="FAIL_PREPARE_OR_VALIDATION"
            row["error"]=type(ex).__name__+":"+str(ex)
            row["traceback"]=traceback.format_exc(limit=4)
        finally:
            save(path,result)
    pass_count=sum(c["status"]=="PASS_REAL_NATIVE_6_AND_CACHE_6"
                   for c in result["cases"])
    result["passed"]=pass_count
    result["failed"]=len(result["cases"])-pass_count
    result["status"]=("PASS_SIX_DIVERSE_NON334_FULL_ADAPTIVE_NATIVE" if
         pass_count==6 and result["new_native_calls_confirmed"]==36 else
         "FINISHED_WITH_PER_CASE_FAILS_OR_BLOCKERS")
    save(path,result)
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--simc",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    args=p.parse_args()
    try:
        result=run(args.simc,args.out)
        for item in result["cases"]:
            print("V180_CASE",item["key"],item["level"],item["status"],
                  item.get("observed_dps"),item.get("error",""),flush=True)
        print("V180_BATCH_STATUS",result["status"],
              "PASS",result["passed"],"FAIL",result["failed"],
              "CONFIRMED_NEW_NATIVE",result["new_native_calls_confirmed"],
              flush=True)
        return 0 if result["status"]=="PASS_SIX_DIVERSE_NON334_FULL_ADAPTIVE_NATIVE" else 3
    except Exception as exc:
        print("V180_BLOCKED",type(exc).__name__,str(exc),file=sys.stderr)
        return 3
if __name__=="__main__":raise SystemExit(main())
