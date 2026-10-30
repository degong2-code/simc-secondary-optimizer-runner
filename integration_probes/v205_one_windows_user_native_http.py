#!/usr/bin/env python3
"""v205 one actual Windows LOCAL API -> six real SimC -> result -> cache replay.

Exactly one source-independent current-season Ret Paladin at ilvl334.
The official Windows executable is provided and SHA-recorded by the workflow,
never built, downloaded, or uploaded by this script.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import pathlib
import sys
import tempfile

from fastapi.testclient import TestClient

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v106_user_session_controller as sessions
import v113_local_web_api as web

SCHEMA="v205_one_real_windows_user_http_native_cache_v1"

def check(ok,reason):
    if not ok:
        raise RuntimeError("V205_"+reason)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def request_ok(response,phase):
    check(response.status_code==200,
          phase+"_HTTP_STATUS_"+str(response.status_code)+"_"+
          str(response.json().get("detail",{}).get("code","UNKNOWN")))
    return response.json()

def run(binary,revision,out,*,selected_eagle=False):
    check(sys.platform=="win32","REAL_WINDOWS_ONLY")
    binary=binary.resolve()
    check(binary.is_file() and binary.name.casefold()=="simc.exe",
          "OFFICIAL_SIMC_EXE_REQUIRED")
    check(type(revision) is str and revision.startswith("710c240") and
          7<=len(revision)<=40,"SIMC_SOURCE_REVISION_SCOPE")
    out=out.resolve()
    out.mkdir(parents=True,exist_ok=True)
    # CI generated sample, not a user profile. Never write passwords/API tokens.
    with tempfile.TemporaryDirectory(prefix="v205-windows-",dir=out) as t:
        root=pathlib.Path(t)
        key="v205-one-process-local-only-token"
        app=web.create_app(root=root/"runs",token=key)
        client=TestClient(app,base_url="http://127.0.0.1:8765")
        h={"x-simc-local-token":key,"origin":"http://127.0.0.1:8765"}
        controls=sessions.standard_controls(("paladin","retribution"))
        if selected_eagle:
            controls["enchant_choices"]={"finger1":7967}
        check(controls["ilevel"]==334 and controls["final_T"] is None,
              "EXACT_DEFAULT_ILVL_B_REQUIRED")
        payload={"controls":controls,"binary":str(binary),
                 "revision":revision,"static_cache":None,
                 "current_season_product":True}
        plan=request_ok(client.post("/api/v1/sessions/plan",
                        headers=h,json=payload),"PLAN")
        check(plan["native_calls"]==0 and
              plan["plan"]["current_season_product"] is True and
              plan["plan"]["native_limit"]==6 and
              plan["plan"]["base_B"]==3150 and
              plan["plan"]["final_T"]==3182,
              "CURRENT_SEASON_PLAN_OR_BUDGET_DRIFT")
        sid=plan["session_id"]
        restored=request_ok(client.get(
             "/api/v1/sessions/"+sid+"/inputs",headers=h),"RESTORE")
        check(restored["current_season_product"] is True and
              restored["user"]["target"]["ilevel"]==334,
              "SEALED_INPUT_RESTORE_DRIFT")
        check((restored["user"].get("selected_season_enchants")==
               {"finger1":7967}) if selected_eagle else
              "selected_season_enchants" not in restored["user"],
              "NONCHMV_ENCHANT_SELECTION_NOT_PRESERVED")
        prof=(root/"runs"/sid/"generated"/"profile.simc").read_text("utf8")
        check(("enchant_id=7967" in prof)==selected_eagle,
              "NONCHMV_ENCHANT_PROFILE_INPUT_DRIFT")
        started=request_ok(client.post("/api/v1/sessions/start",
                         headers=h,json=payload),"START")
        check(started["status"]=="WORKER_STARTED" and
              started["native_attempt_ceiling_cumulative"]==6,
              "WORKER_BOUND_NOT_ENFORCED")
        worker=app.state.jobs.children[sid]
        check(worker.wait(timeout=600)==0,"REAL_WINDOWS_WORKER_NONZERO_EXIT")
        status=request_ok(client.get(
             "/api/v1/sessions/"+sid+"/status",headers=h),"STATUS")
        check(status["result_ready"] is True and status["active"] is False,
              "REAL_WINDOWS_RESULT_NOT_READY")
        result=request_ok(client.get(
             "/api/v1/sessions/"+sid+"/result",headers=h),"RESULT")
        user=result["user_result"]
        check(result["native_calls_cumulative"]==6 and
              result["base_B"]==3150 and result["final_T"]==3182 and
              user["confidence_level"]==0.95 and
              user["global_optimum_proven"] is False,
              "REAL_WINDOWS_NATIVE_OR_95_DRIFT")
        best=user["observed_first_choice"]
        check(math.isfinite(best["observed_dps_mean"]) and
              best["observed_dps_mean"]>0 and
              math.isfinite(best["simc_sem"]) and best["simc_sem"]>=0,
              "DPS_SEM_NONFINITE")
        check(sum(best["absolute_rating_T"].values())==3182,
              "NATIVE_STATIC_CHMV_SUM_DRIFT")
        cache_start=request_ok(client.post(
              "/api/v1/sessions/"+sid+"/cache-only",
              headers=h,json={}),"CACHE_START")
        check(cache_start["status"]=="CACHE_ONLY_WORKER_STARTED" and
              cache_start["new_native_execution_permitted"] is False,
              "CACHE_ONLY_NEW_NATIVE_NOT_FORBIDDEN")
        worker2=app.state.jobs.children[sid]
        check(worker2.wait(timeout=180)==0,"CACHE_ONLY_WORKER_NONZERO_EXIT")
        replay=request_ok(client.get(
             "/api/v1/sessions/"+sid+"/result",headers=h),"CACHE_RESULT")
        check(replay["native_calls_cumulative"]==6 and
              replay["cache_hits_this_run"]==6 and
              replay["user_result"]==user,
              "CACHE_REPLAY_DPS_SEM_CONFIDENCE_DRIFT")
        proof_path=root/"runs"/sid/"V112_CACHE_REPLAY_RECEIPT.json"
        check(proof_path.is_file(),"CACHE_PROOF_MISSING")
        proof=json.loads(proof_path.read_text(encoding="utf8"))
        check(proof["additional_native_calls"]==0 and
              proof["cache_hits_this_run"]==6 and
              len(proof["native_json2_sha256"])==6,
              "CACHE_JSON2_HASH_REPLAY_MISMATCH")
        receipt={
          "schema":("v207_eagle_selected_windows_real_native_http_cache_v1"
                    if selected_eagle else SCHEMA),
          "status":("PASS_WINDOWS_EAGLE_7967_SIX_NATIVE_AND_SIX_CACHE"
                    if selected_eagle else
                    "PASS_WINDOWS_REAL_USER_SIX_NATIVE_AND_SIX_CACHE"),
          "scope":("paladin/retribution current-season 334 finger1 enchant_id=7967"
                   if selected_eagle else
                   "paladin/retribution current-season 334, no selected enchant"),
          "selected_nonchmv_enchant_id":7967 if selected_eagle else None,
          "fixed_CHMV_enchant_E_total":0,
          "binary_sha256":digest(binary),"revision":revision,
          "source_profile_sha256":sessions.sha(
              (root/"runs"/sid/"generated"/"profile.simc").read_bytes()),
          "base_B":3182-32,"final_T":3182,"fixed_O_total":32,
          "native_calls":6,"cached_replay_verified_hits":6,
          "additional_native_calls_on_replay":0,
          "native_json2_sha256":proof["native_json2_sha256"],
          "observed_mean_dps":best["observed_dps_mean"],
          "observed_sem":best["simc_sem"],
          "confidence_level":0.95,"global_optimum_proven":False,
          "local_http_plan_start_status_result_verified":True,
          "existing_v094_optimizer_only":True,
          "generalized_to_other_26_specs":False,
          "no_enchant_selection_promotion":not selected_eagle,
          "only_exact_nonchmv_eagle_enabled":bool(selected_eagle)
        }
        dest=out/("V207_EAGLE_SELECTED_NATIVE_RECEIPT.json" if selected_eagle
                  else "V205_WINDOWS_ONE_USER_NATIVE_RECEIPT.json")
        dest.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n",
                        encoding="utf8")
        print("V205_WINDOWS_LOCAL_HTTP_REAL_NATIVE_AND_CACHE_PASS",json.dumps(
            {k:receipt[k] for k in ("base_B","final_T","native_calls",
              "cached_replay_verified_hits","confidence_level",
              "global_optimum_proven")},sort_keys=True),flush=True)
        return 0

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--simc",type=pathlib.Path,required=True)
    p.add_argument("--revision",default="710c2408bf")
    p.add_argument("--out",type=pathlib.Path,required=True)
    p.add_argument("--selected-eagle",action="store_true",
                   help="v207: same one-user proof with source-classified E0 enchant")
    opts=p.parse_args()
    raise SystemExit(run(opts.simc,opts.revision,opts.out,selected_eagle=opts.selected_eagle))
