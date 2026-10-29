#!/usr/bin/env python3
"""v176: current-season physical SimC smoke for all 26 DPS specs, NO optimization.

One existing v145 physical Native at most per spec; reuses exact v174 Paladin
receipt when present. No new item, APL, rating, or effect validation logic.
Per-spec original stdout/JSON2/receipt retained; one compact latest summary.
"""
from __future__ import annotations
import argparse,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"integration_probes")]
import v106_user_session_controller as sessions
import v143_specialization_contracts as contracts
import v145_targeted_pure_physical_native as physical
import v167_product_season_gear_adapter as gear

SCHEMA="v176_current_season_all_26_physical_smoke_v1"
ALL=tuple(sorted(contracts.CONTRACTS))
PRIOR="paladin/retribution"
REVISION="7bc10711b5"
BINARY_SHA="64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e"

class BatchBlocked(ValueError):pass
def need(condition,reason):
    if not condition:raise BatchBlocked(reason)
def save(path,doc):
    path.write_text(json.dumps(doc,sort_keys=True,ensure_ascii=False,
                               indent=2)+"\n",encoding="utf8")

def user_for(key,allowed):
    cl,sp=key.split("/")
    controls=sessions.standard_controls((cl,sp))
    controls["oil_hands"]=[]
    user=sessions.user_scenario(controls)
    need(len(user["trinkets"])==2 and
         all(x["item_id"] in allowed for x in user["trinkets"]),
         "NON_SEASON_TRINKET_IN_DEFAULT:"+key)
    need(user["target"]=={"ilevel":334,"final_T":None}
         and user["special_items"]==[]
         and user["embellishments"]==[],
         "NON_STANDARD_PHYSICAL_SMOKE_USER:"+key)
    return user

def run(binary,out,*,execute=False,max_new=0,iterations=35,revision=REVISION,
        reuse_paladin=True):
    need(len(ALL)==26 and set(ALL)=={"/".join(x) for x in sessions.SUPPORTED},
         "EXPECTED_26_DPS_CONTRACT_DRIFT")
    need(type(execute) is bool and type(max_new) is int
         and 0<=max_new<=26 and
         (execute or max_new==0) and
         type(iterations) is int and 1<=iterations<=35,
         "PHYSICAL_ONLY_NATIVE_BOUNDS")
    need(revision==REVISION,"PINNED_SIMC_REVISION_CHANGED")
    binary=pathlib.Path(binary).resolve()
    need(binary.is_file(),"SIMC_BINARY_NOT_PRESENT")
    if execute:
        need(physical.sha(binary.read_bytes())==BINARY_SHA,
             "PINNED_SIMC_BINARY_SHA_CHANGED")
        need(reuse_paladin and max_new==25,
             "EXACT_25_NEW_WITH_V174_PALADIN_REPLAY_REQUIRED")
    out=pathlib.Path(out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    summary_path=out/"V176_ALL_26_SUMMARY.json"
    allowed={x["item_id"] for x in gear.read()["items"]
             if x["category"]=="trinket"}
    users={key:user_for(key,allowed) for key in ALL}
    # Before spending any Native budget, verify the existing Paladin receipt.
    # It carries a profile/json2 hash and same binary/absolute input paths.
    if execute:
        prior=physical.run(users[PRIOR],binary,out,revision,
                           iterations=iterations,max_new=0,
                           source_first_stage=True)
        need(prior["status"]=="CACHED_VERIFIED_PHYSICAL_SIMC"
             and prior["new_native_calls"]==0,
             "V174_ACTUAL_PALADIN_PROOF_MUST_BE_REUSABLE")
    summary={"schema":SCHEMA,"status":"RUNNING","spec_count":len(ALL),
      "spec_order":list(ALL),"purpose":"PHYSICAL_SIMC_NATIVE_ONLY_NOT_OPTIMIZATION",
      "source_first_current_season":True,"ilevel":334,
      "iterations_requested_per_spec":iterations,
      "binary_revision":revision,
      "simc_binary_sha256":physical.sha(binary.read_bytes()),
      "new_native_calls_confirmed":0,
      "new_native_permits_reserved":0,"new_native_outcomes_uncertain":0,
      "v174_paladin_reused":False,
      "adaptive_optimizer_native_calls":0,"results":[]}
    def checkpoint():
        status={}
        for row in summary["results"]:
            status[row["status"]]=status.get(row["status"],0)+1
        summary["counts"]=status
        save(summary_path,summary)
    checkpoint()
    for key in ALL:
        row={"spec":key,"status":"PREPARING",
             "native_calls_confirmed":0,"physical_profile_only":True}
        summary["results"].append(row)
        checkpoint()
        try:
            user=users[key]
            if execute and key==PRIOR:
                may_call=False
            else:
                may_call=execute
            # Explicit per-spec reservation, no hidden retry after errors.
            if may_call:
                need(summary["new_native_permits_reserved"]<max_new,
                     "NATIVE_MAX_SPEC_BUDGET_EXCEEDED")
                summary["new_native_permits_reserved"]+=1
                checkpoint()
            actual=physical.run(user,binary,out,revision,
                     iterations=iterations,timeout_seconds=180,
                     max_new=int(may_call),
                     source_first_stage=True)
            row["physical_receipt"]=actual["receipt"]
            row["raw_simc_log"]=actual["raw_log"]
            row["output_dir"]=actual["output_dir"]
            n=actual["new_native_calls"]
            need(type(n) is int and n in (0,1),"SPEC_NATIVE_CALL_COUNT_INVALID")
            row["native_calls_confirmed"]=n
            summary["new_native_calls_confirmed"]+=n
            row["dps_mean"]=(actual.get("native_json2") or {}).get("json2",{}).get("dps_mean")
            if key==PRIOR and execute:
                need(actual["status"]=="CACHED_VERIFIED_PHYSICAL_SIMC" and n==0,
                     "PRIOR_PALADIN_CACHED_STATUS_DRIFT")
                summary["v174_paladin_reused"]=True
            if actual["status"] in ("PASS_PHYSICAL_SIMC",
                                   "CACHED_VERIFIED_PHYSICAL_SIMC"):
                row["status"]="PASS_PHYSICAL_NATIVE"
                row["source"]="v174_SHA_REUSED" if key==PRIOR and execute else (
                     "NEW_NATIVE" if n==1 else "CACHED_SHA_REUSED")
            elif actual["status"]=="PREPARED_NO_NATIVE":
                row["status"]="PLAN_READY_ZERO_NATIVE"
            elif actual["status"]=="PRIOR_FAILURE_RETAINED" or actual["status"].startswith("FAIL_"):
                row["status"]="FAIL_REAL_SIMC"
            else:
                row["status"]="BLOCKED_UNEXPECTED_STATUS"
                row["error"]="physical.status="+actual["status"]
        except Exception as exc:
            row["status"]="BLOCKED_PREPARATION_OR_NATIVE"
            row["error"]=type(exc).__name__+":"+str(exc)
            if execute and key!=PRIOR:
                # A failed call may have started before its output receipt.
                # The cap is on *reserved* calls, not just confirmed success.
                summary["new_native_outcomes_uncertain"]+=1
        finally:
            checkpoint()
    completed=summary["results"]
    summary["status"]="FINISHED_ALL_26_PHYSICAL_PASS" if (
        execute and len(completed)==26 and
        all(x["status"]=="PASS_PHYSICAL_NATIVE" for x in completed)
        and summary["new_native_calls_confirmed"]==25
        and summary["v174_paladin_reused"]) else (
        "PREFLIGHT_26_READY" if not execute and
        all(x["status"] in ("PLAN_READY_ZERO_NATIVE","PASS_PHYSICAL_NATIVE")
            for x in completed) else "FINISHED_WITH_PER_SPEC_BLOCKERS")
    checkpoint()
    return summary

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--simc",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    p.add_argument("--execute",action="store_true")
    p.add_argument("--max-new",type=int,default=0)
    p.add_argument("--iterations",type=int,default=35)
    a=p.parse_args(argv)
    try:
        result=run(a.simc,a.out,execute=a.execute,
                   max_new=a.max_new,iterations=a.iterations)
        print("V176_STATUS:",result["status"])
        print("V176_COUNTS:",json.dumps(result["counts"],sort_keys=True))
        print("V176_CONFIRMED_NEW_NATIVE:",result["new_native_calls_confirmed"])
        print("V176_RESERVED_NEW_NATIVE:",result["new_native_permits_reserved"])
        for row in result["results"]:
            print(row["spec"],row["status"],row.get("dps_mean"),
                  row.get("error",""),row.get("raw_simc_log",""))
        print("V176_SUMMARY:",str(pathlib.Path(a.out).resolve()/"V176_ALL_26_SUMMARY.json"))
        return 0 if result["status"] in (
            "PREFLIGHT_26_READY","FINISHED_ALL_26_PHYSICAL_PASS") else 3
    except Exception as exc:
        print("V176_BLOCKED:",type(exc).__name__,str(exc),file=sys.stderr)
        return 3
if __name__=="__main__":raise SystemExit(main())
