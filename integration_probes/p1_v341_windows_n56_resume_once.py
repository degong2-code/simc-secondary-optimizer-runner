#!/usr/bin/env python3
"""v341: exactly one real Windows v293 N56 partial/cancel/resume/replay proof.
Historical source-pinned 710c240 is NOT the 70783 live retail build.
"""
from __future__ import annotations
import argparse, hashlib, json, math, pathlib, sys, tempfile, zipfile
from fastapi.testclient import TestClient
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v106_user_session_controller as sessions
import v113_local_web_api as web
import v293_local_longrun_session as longrun

SCHEMA="p1_v341_windows_n56_12_native_one_user_v1"
EXE_SHA="0ad16368cd1effb19c793dbce63518ccb72fec89c72f6ef75d9afca239a039e8"
REVISION="710c2408bf"
CAP=12
TOKEN="v341-ephemeral-test-token"

def need(ok,label):
    if not ok: raise RuntimeError("V341_"+label)

def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def client(root):
    app=web.create_app(root=root,token=TOKEN)
    return app,TestClient(app,base_url="http://127.0.0.1:8765")

def call(client,route,payload=None):
    headers={"x-simc-local-token":TOKEN,"origin":"http://127.0.0.1:8765"}
    res=(client.get(route,headers=headers) if payload is None else
         client.post(route,headers=headers,json=payload))
    need(res.status_code==200,"HTTP_"+str(res.status_code)+"_"+str(
        res.json().get("detail",{}).get("code","UNKNOWN")))
    return res.json()

def wait(app,sid,phase):
    need(app.state.jobs.children[sid].wait(timeout=600)==0,phase+"_WORKER_EXIT")

def inspect(client,uri,count=None):
    x=call(client,uri+"/status")
    need(x["enabled"] and not x["active"] and
         x["scout_iterations_per_CHMV"]==56 and x["native_budget"]==CAP,
         "STATUS_OR_N56_INVALID")
    if count is not None:
        need(x["progress"]["completed_jobs"]==count,"CANDIDATE_COUNT")
    return x

def run(binary,out):
    need(sys.platform=="win32","WINDOWS_ONLY")
    binary=pathlib.Path(binary).resolve(strict=True)
    need(binary.name.lower()=="simc.exe" and sha(binary)==EXE_SHA,
         "PINNED_SIMC_EXE_SHA")
    out=pathlib.Path(out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="v341-",dir=out) as temp:
        runs=pathlib.Path(temp)/"runs"
        app1,first=client(runs)
        controls=sessions.standard_controls(("paladin","retribution"))
        need(controls["ilevel"]==334 and controls["final_T"] is None,
             "CONTROL_DRIFT")
        payload={"controls":controls,"binary":str(binary),"revision":REVISION,
                 "current_season_product":True,"static_cache":None,
                 "max_native_calls":CAP,"max_new_native_this_invocation":2,
                 "max_elapsed_seconds":900}
        started=call(first,"/api/v1/longrun/start",payload)
        sid=started["session_id"]
        uri="/api/v1/sessions/"+sid+"/longrun"
        folder=runs/sid
        need(started["status"]=="LONGRUN_WORKER_STARTED" and
             longrun.config(folder)["scout_iterations"]==56,
             "N56_NOT_SEALED")
        wait(app1,sid,"SCOUT_TWO")
        first_status=inspect(first,uri,count=2)
        need(first_status["progress"]["worker"]["status"]==
             "PAUSED_INVOCATION_NATIVE_BUDGET" and
             first_status["progress"]["native_attempts"]==2,
             "SCOUT_TWO_PAUSE")
        proof_paths=[longrun.config_path(folder),
                     longrun.worker_state_path(folder),
                     longrun.stage_path(folder,CAP)/"simc_results"/"V291_JOURNAL.jsonl"]
        before={p.name:sha(p) for p in proof_paths}
        app2,restarted=client(runs)
        saved=inspect(restarted,uri,count=2)
        restored=call(restarted,"/api/v1/sessions/"+sid+"/inputs")
        need(saved["progress"]["native_attempts"]==2 and
             restored["user"]["target"]["ilevel"]==334 and
             restored["revision"]==REVISION and
             before=={p.name:sha(p) for p in proof_paths},
             "READONLY_SERVER_RESTART_DRIFT")
        partial=call(restarted,uri+"/resume",
                     {"max_new_native_this_invocation":8})
        need(partial["max_new_native_this_invocation"]==8,"RESUME_BOUND")
        cancelled=call(restarted,uri+"/cancel",{})
        need(cancelled["status"]==
             "LONGRUN_CANCEL_REQUESTED_AFTER_CURRENT_NATIVE",
             "CANCEL_REQUEST_NOT_ACCEPTED")
        wait(app2,sid,"USER_CANCEL")
        paused=inspect(restarted,uri)
        need(paused["progress"]["worker"]["status"]=="PAUSED_USER_CANCEL" and
             paused["cancel_requested"] and
             2<=paused["progress"]["native_attempts"]<CAP,
             "PARTIAL_NOT_PRESERVED_AFTER_CANCEL")
        at_cancel=paused["progress"]["native_attempts"]
        continued=call(restarted,uri+"/resume",{"continuous":True})
        need(continued["native_attempt_ceiling_cumulative"]==CAP,
             "CONTINUOUS_RESTART_CEILING")
        wait(app2,sid,"FINISH")
        done=inspect(restarted,uri,count=CAP)
        need(done["progress"]["worker"]["status"]=="BUDGET_EXHAUSTED" and
             done["progress"]["native_attempts"]==CAP and
             done["result_ready"] and not done["cancel_requested"],
             "FINAL_12_NOT_COMPLETE")
        result=call(restarted,uri+"/result")
        user=result["user_result"]
        best=user["observed_first_choice"]
        need(result["scout_iterations_per_CHMV"]==56 and
             result["native_calls_cumulative"]==CAP and
             user["confidence_level"]==0.95 and
             user["global_optimum_proven"] is False and
             math.isfinite(best["observed_dps_mean"]) and
             best["observed_dps_mean"]>0 and
             math.isfinite(best["simc_sem"]) and best["simc_sem"]>=0 and
             sum(best["absolute_rating_T"].values())==user["final_T"],
             "REAL_DPS_SEM_CHMV_95_INVALID")
        stage=longrun.stage_path(folder,CAP)/"simc_results"
        originals=sorted(stage.glob("cases/case_*/native/result.json"))
        need(len(originals)==CAP,"ORIGINAL_NATIVE_JSON2_COUNT")
        source_sha=[sha(f) for f in originals]
        zip_path=out/"V341_ORIGINAL_NATIVE_JSON2.zip"
        with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as z:
            for p in originals:
                z.write(p,arcname=str(p.relative_to(stage)))
        cache=call(restarted,uri+"/cache-only",{})
        need(cache["new_native_execution_permitted"] is False and
             cache["max_new_native_this_invocation"]==0,
             "CACHE_ONLY_NATIVES_NOT_ZERO")
        wait(app2,sid,"SHA_REPLAY")
        replay=call(restarted,uri+"/result")
        need(replay["native_calls_cumulative"]==CAP and
             replay["cache_hits_this_run"]==CAP and
             replay["user_result"]==user and
             [sha(f) for f in originals]==source_sha,
             "CACHE_REPLAY_CHANGED_NATIVE")
        app3,reopened=client(runs)
        need(inspect(reopened,uri,count=CAP)["result_ready"] and
             call(reopened,uri+"/result")["user_result"]==user,
             "CLOSED_REOPENED_RESULT")
        receipt={
            "schema":SCHEMA,"status":"PASS_ONE_REAL_WINDOWS_N56_START_CANCEL_RESUME_CACHE",
            "source_build_scope":"historical_710c240_not_current_70783",
            "spec":"paladin/retribution","target_ilevel":334,
            "scout_iterations":56,"native_budget":CAP,
            "attempts_before_cancel":2,"attempts_after_cancel":at_cancel,
            "native_attempts_final":CAP,"cache_hits":CAP,"cache_new_native":0,
            "binary_sha256":EXE_SHA,"revision":REVISION,
            "original_native_json2_sha256":source_sha,
            "original_zip_sha256":sha(zip_path),
            "dps":best["observed_dps_mean"],"sem":best["simc_sem"],
            "confidence_level":0.95,"global_optimum_proven":False,
            "actual_windows_process_workers":True,
            "http_testclient_not_human_browser":True,
            "future_season_proven":False,"full_64_budget_proven":False}
        (out/"V341_WINDOWS_N56_COMPACT.json").write_text(
            json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
            encoding="utf8")
        print("V341_REAL_WINDOWS_N56",json.dumps({
            k:receipt[k] for k in ("status","attempts_after_cancel",
                "native_attempts_final","cache_hits","cache_new_native")},
            sort_keys=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--simc",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    a=p.parse_args()
    run(a.simc,a.out)
