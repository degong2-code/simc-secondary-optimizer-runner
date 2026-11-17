#!/usr/bin/env python3
"""v581: one real Windows Chrome user positive-O/T=3500 to 2 actual
adaptive SimC DPS candidates and cache-only replay, then stop.

Uses v580's ORIGINAL v216/v212/v217/Chrome/HTTP source-and-plan once;
no new optimizer logic, no second season source Build, no 64-case sweep.
Retains only SHA/ratings/DPS/SEM/95% summary, never private profile
bytes, credentials or SimC executable in the public compact receipt.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import re
import time

import v293_local_longrun_session as longrun
from p1_v580_windows_real_oil_chrome_manual_t_once import run as source_chrome
from p1_v580_windows_real_oil_chrome_manual_t_once import MANUAL_T, OIL_ITEM, BUILD

SCHEMA="p1_v581_actual_positive_oil_manual_T_two_dps_native_and_cache_v1"
STATUS="PASS_ACTUAL_CHROME_POSITIVE_O_TWO_NATIVE_RESUME_CACHE_ONLY_95_UNRESOLVED"
MAX_DPS_NATIVE=2

class FocusedBlocked(RuntimeError):
    pass

def need(ok,code):
    if not ok:raise FocusedBlocked("V581_"+code)

def sha(path):
    h=hashlib.sha256()
    with pathlib.Path(path).open("rb") as f:
        for buf in iter(lambda:f.read(1<<20),b""):
            h.update(buf)
    return h.hexdigest()

def browser_api(browser,method,path,payload=None):
    browser.set_script_timeout(35)
    return browser.execute_async_script("""
        const method=arguments[0],path=arguments[1],
              payload=arguments[2],done=arguments[arguments.length-1];
        api(path,{method,payload})
          .then(value=>done({ok:true,value}))
          .catch(error=>done({ok:false,error:String(error?.message||error)}));
    """,method,path,payload)

def original_request(browser):
    return browser.execute_script("""
        const request=buildRequest();
        return {...request,max_native_calls:12,
                max_new_native_this_invocation:1,
                max_elapsed_seconds:360};
    """)

def native_receipt_files(root,sid):
    folder=pathlib.Path(root)/sid
    cfg=longrun.config(folder)
    need(type(cfg) is dict and cfg.get("native_budget")==12,
         "EXISTING_TWELVE_CASE_BUDGET_NOT_SEALED")
    output=longrun.stage_path(folder,cfg["native_budget"])/"simc_results"
    cases=sorted(output.glob("cases/case_*/native/"))
    found=[]
    for case in cases:
        inp,js,rec=[case/name for name in (
            "input.simc","result.json","native_receipt.json")]
        if not (inp.is_file() and js.is_file() and rec.is_file()):
            continue
        raw=inp.read_text(encoding="utf8")
        need("temporary_enchant=main_hand:thalassian_phoenix_oil_2" in raw,
             "NATIVE_INPUT_MISSING_ACTUAL_SELECTED_OIL")
        need("spec=retribution" in raw,
             "ACTUAL_USER_DPS_SPEC_WAS_NOT_APPLIED")
        found.append({
            "case_name":case.parent.name,
            "input_sha256":sha(inp),
            "simc_json2_sha256":sha(js),
            "native_receipt_sha256":sha(rec),
            "all_files_nonempty":all(x.stat().st_size>0 for x in (inp,js,rec))
        })
    return found

def wait_quiet(browser,sid,*,timeout=420):
    deadline=time.monotonic()+timeout
    target="/api/v1/sessions/"+sid+"/longrun/status"
    while time.monotonic()<deadline:
        reply=browser_api(browser,"GET",target)
        need(reply.get("ok"),"ORIGINAL_STATUS_HTTP_"+str(reply.get("error",""))[:70])
        status=reply["value"]
        if not status.get("active"):
            worker=(status.get("progress") or {}).get("worker") or {}
            need(worker.get("status") not in (
                "BLOCKED_OR_PARTIAL","QUEUED","RUNNING"),
                "ORIGINAL_LONGRUN_WORKER_NOT_SUCCESSFUL_"+
                str(worker.get("status")))
            return status
        time.sleep(.45)
    raise FocusedBlocked("V581_SIMC_NATIVE_BATCH_TIMEOUT")

def continue_one_user(*,browser,root,sha,
                      installed_doc,original_plan,report,save):
    installed_sha=sha
    need(original_plan.get("native_calls")==0 and
         original_plan.get("status")=="READY_ZERO_NATIVE",
         "ORIGINAL_CHROME_PLAN_PRECONDITION_FAILED")
    need(sum(installed_doc["official_O"].values())==32,
         "ORIGINAL_PHYSICAL_O_POSITIVE_RATING_DRIFT")
    request=original_request(browser)
    need(request.get("installed_manifest_sha256")==installed_sha and
         request["controls"]["final_T"]==MANUAL_T and
         request.get("selected_oil_item_ids_by_hand")=={"main_hand":OIL_ITEM} and
         request["controls"]["oil_hands"]==["main_hand"] and
         request["controls"]["ilevel"]==334 and
         request["installed_season_game_build"]==BUILD,
         "CHROME_REAL_SEALED_USER_REQUEST_DRIFT")
    report["v581_focus"]={
      "schema":SCHEMA,"dps_native_cap":MAX_DPS_NATIVE,
      "selected_oil_item_id":OIL_ITEM,
      "exact_installed_manifest_sha256":installed_sha,
      "user_final_T":MANUAL_T,
      "physical_fixed_O":installed_doc["official_O"],
      "existing_longrun_engine":True,"new_engine":False,
      "new_source_after_v580":False,"dps_native_attempts":0,
      "global_optimum_proven":False,
      "95_percent_statistical_winner_not_assumed":True}
    save()
    prepare=browser_api(browser,"POST","/api/v1/longrun/prepare",request)
    need(prepare.get("ok"),"ORIGINAL_LONGRUN_PREPARE_HTTP_"+
         str(prepare.get("error",""))[:80])
    response=prepare["value"]
    need(response.get("status")=="LONGRUN_SOURCE_PREPARED_NO_DPS_NATIVE" and
         response.get("static_L_native_calls_this_start",0)==0,
         "SOURCE_PREPARE_NEW_NATIVE_OR_STATUS_INVALID")
    sid=response.get("session_id")
    need(type(sid) is str and re.fullmatch(r"[a-f0-9]{20}",sid),
         "LONGRUN_SEALED_SESSION_ID_INVALID")
    report["v581_focus"]["session_id_sha256"]=hashlib.sha256(
        sid.encode("ascii")).hexdigest()
    report["v581_focus"]["prepared_without_dps_native"]=True
    save()
    url="/api/v1/sessions/"+sid
    native_before=[]
    for expected in (1,2):
        trigger=browser_api(browser,"POST",url+"/longrun/resume",
            {"max_new_native_this_invocation":1,"max_elapsed_seconds":360})
        need(trigger.get("ok"),"ORIGINAL_NATIVE_RESUME_HTTP_"+
             str(trigger.get("error",""))[:70])
        started=trigger["value"]
        need(started.get("max_new_native_this_invocation")==1,
             "EXISTING_NATIVE_BATCH_NOT_CAPPED_ONE")
        status=wait_quiet(browser,sid)
        prog=status["progress"]
        need(prog["native_attempts"]==expected and
             prog["completed_jobs"]==expected,
             "NATIVE_PROGRESS_NOT_EXACTLY_ONE_NEW_CASE")
        current=native_receipt_files(root,sid)
        need(len(current)==expected and
             all(item["all_files_nonempty"] for item in current),
             "NATIVE_JSON2_PROFILE_RECEIPTS_INCOMPLETE")
        if native_before:
            need(current[:len(native_before)]==native_before,
                 "FIRST_NATIVE_INPUT_RESULT_RECEIPT_CHANGED_ON_RESUME")
        native_before=current
        report["v581_focus"]["dps_native_attempts"]=expected
        report["actual_user_dps_native"]=expected
        report["v581_focus"]["cases"]=current
        save()
    before=native_before
    cache=browser_api(browser,"POST",url+"/longrun/cache-only",{})
    need(cache.get("ok"),"CACHE_ONLY_HTTP_"+str(cache.get("error",""))[:70])
    need(cache["value"].get("max_new_native_this_invocation")==0,
         "CACHE_ONLY_REQUEST_NATIVE_BUDGET_NOT_ZERO")
    cached=wait_quiet(browser,sid)
    need(cached["progress"]["native_attempts"]==MAX_DPS_NATIVE and
         cached["progress"]["completed_jobs"]==MAX_DPS_NATIVE and
         native_receipt_files(root,sid)==before,
         "CACHE_REPLAY_RAN_NATIVE_OR_CHANGED_NATIVE_BYTES")
    result=browser_api(browser,"GET",url+"/longrun/result")
    need(result.get("ok"),"ORIGINAL_USER_RESULT_HTTP_"+
         str(result.get("error",""))[:70])
    output=result["value"]
    user=output.get("user_result") or {}
    first=user.get("observed_first_choice") or {}
    vector=first.get("absolute_rating_T") or {}
    need(output.get("native_calls_cumulative")==MAX_DPS_NATIVE and
         user.get("final_T")==MANUAL_T and
         user.get("base_B")==MANUAL_T-32 and
         user.get("confidence_level")==0.95 and
         user.get("global_optimum_proven") is False and
         type(vector) is dict and len(vector)==4 and
         sum(vector.values())==MANUAL_T and
         isinstance(first.get("observed_dps_mean"),(int,float)) and
         first["observed_dps_mean"]>0 and
         isinstance(first.get("simc_sem"),(int,float)) and
         first["simc_sem"]>=0,
         "REAL_DPS_SEM_95_CHMV_BUDGET_OR_BEST_CANDIDATE_DRIFT")
    report["v581_focus"]["first_observed"]={
        "rating":vector,
        "dps":first["observed_dps_mean"],
        "sem":first["simc_sem"],
        "confidence_level":user["confidence_level"],
        "confirmation_pair_direction_supported_at_95":
            user.get("confirmation_pair_direction_supported_at_95"),
        "global_optimum_proven":False,
        "not_full_optimization":True}
    report["v581_focus"]["cache_only_native_delta"]=0
    report["v581_focus"]["result_status"]=cached.get("progress",{}).get(
        "worker",{}).get("status")
    need(report["actual_user_dps_native"]==2,
         "POSITIVE_O_NATIVE_LIMIT_EXCEEDED")
    save()
    return STATUS

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--simc",required=True)
    parser.add_argument("--out",required=True)
    args=parser.parse_args(argv)
    return source_chrome(args.simc,args.out,post_plan_hook=continue_one_user)

if __name__=="__main__":
    raise SystemExit(main())
