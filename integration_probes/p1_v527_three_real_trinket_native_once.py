#!/usr/bin/env python3
"""v527: exactly three actual default/alternate trinket six-case SimC sessions.

Same source-verified v212 ilvl334 environment, fixed public hunter/survival,
NO AI or simulated proc effects. Verify original JSON2/inputs, per-session
identity, SEM/95, and Native0 cache replay. Never carry DPS caches across
different trinket ItemIDs.
"""
from __future__ import annotations
import argparse,hashlib,json,os,pathlib,re,sys,tempfile
from fastapi.testclient import TestClient
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner"),str(ROOT/"integration_probes")]
import v113_local_web_api as web
import p1_v524_m1_m2_source_owner_once as v524
import p1_v525_real_option_matrix_once as v525
from integration_probes import p3_haj_real_local_web_native_e2e as web_native

SCHEMA="p1_v527_70783_three_trinket_real_native_95_cache_v1"
PAIRS=((270175,270173),(270169,270174),(270166,270170))
MAX_DPS=18
def need(ok,code):
    if not ok:raise RuntimeError("V527_"+code)
def sha(path):
    with pathlib.Path(path).open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()
def save(p,doc):
    p.write_text(json.dumps(doc,ensure_ascii=False,sort_keys=True,
      indent=2,allow_nan=False)+"\n",encoding="utf8")
def http(c,method,uri,body=None):
    h={"x-simc-local-token":"v527-trinkets-test-token",
       "origin":"http://127.0.0.1:8765"}
    r=(c.get(uri,headers=h) if method=="GET"
       else c.post(uri,headers=h,json=body or {}))
    if r.status_code!=200:
        data=r.json().get("detail",{})
        code=data.get("code") if type(data) is dict else str(data)
        raise RuntimeError("V527_HTTP_"+str(r.status_code)+"_"+
                           str(code)[:110])
    return r.json()
def native_files(folder):
    d=folder/"generated"/"simc_results"
    result={}
    for name in ("input.simc","result.json","native_receipt.json"):
        files=sorted(d.rglob(name))
        need(len(files)==6,"NATIVE_"+name.replace(".","_")+"_SIX_REQUIRED")
        result[name]=files
    return result
def run(binary,out):
    out=pathlib.Path(out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    receipt=out/"V527_ACTUAL_TRINKET_NATIVE_RESULT.json"
    record={"schema":SCHEMA,"status":"NOT_STARTED",
      "game_build":v524.BUILD,"revision":v524.REV,
      "simc_exe_sha256":v524.EXE_SHA,"AI_calls":0,
      "AI_effect_interpretation":False,"effect_owner":"EXISTING_SIMC",
      "new_environment_native":None,"new_dps_native_confirmed":0,
      "native_ceiling":21,"cases":{},"full_product_e2e":"PENDING",
      "global_optimum_proven":False}
    def checkpoint():save(receipt,record)
    checkpoint()
    try:
        need(sys.platform=="win32","REAL_WINDOWS_ONLY")
        binary=pathlib.Path(binary).resolve(strict=True)
        need(binary.name.lower()=="simc.exe" and
             sha(binary)==v524.EXE_SHA and
             os.environ.get("SIMC_PINNED_SOURCE_COMMIT")==v524.REV and
             os.environ.get("SIMC_PINNED_GAME_BUILD")==v524.BUILD,
             "OFFICIAL_SIMC_OR_PIN_DRIFT")
        need(v524.EphemeralActionsCredentials().load() is not None,
             "ORIGINAL_SOURCE_CREDENTIALS_MISSING")
        with tempfile.TemporaryDirectory(prefix="v527-three-trinkets-",
                                         dir=out) as t:
            root=pathlib.Path(t)/"runs";root.mkdir()
            jobs=web.LocalJobs(root,source_credential_store=
                v524.EphemeralActionsCredentials())
            myth=jobs.discover_season_myth_target(v524.BUILD)
            need(myth.get("target_ilevel")==334 and
                 myth.get("status")==
                   "MYTH_TARGET_CANDIDATE_FROM_MATCHED_WAGO_V163_SOURCE",
                 "M1_SOURCE_NOT_MATCHED")
            env=jobs.build_season_environment(
                 game_build=v524.BUILD,target_ilevel=334,
                 auto_initial_core_build=True,
                 auto_initial_core_simc_binary=str(binary),
                 simc_revision_hint=v524.REV,
                 existing_special_gem_id=None,source_target_socket_count=4,
                 auto_myth_target_source_build=v524.BUILD,
                 auto_myth_target_source_sha256=myth["currency_csv_sha256"])
            record["new_environment_native"]=env.get("native_calls")
            need(type(record["new_environment_native"]) is int and
                 0<=record["new_environment_native"]<=3 and
                 env.get("environment_installed") is True and
                 env.get("environment_ready") is True and
                 env.get("G")==2850 and env.get("J")==92 and
                 env.get("F")==165 and env.get("B")==3107 and
                 env.get("T")==3107 and sum(env["O"].values())==0,
                 "M2_EXACT_BASE_INSTALLED_REQUIRED")
            compilation=env["source_compilation"]
            need(compilation.get("missing")==[] and
                 compilation["required_core_source_owner_report"][
                   "original_source_owner_missing_for_selected_request"]==[],
                 "M2_REQUIRED_SOURCE_OWNER_MISSING")
            installed=compilation["verified_environment_install"][
                "manifest_sha256"]
            record["v212_installed_manifest_sha256"]=installed
            record["M1_currency_csv_sha256"]=myth["currency_csv_sha256"]
            checkpoint()
            with web_native.verified_current_catalog(
                    compilation["source_catalog_path"],v524.BUILD):
                app=web.create_app(root=root,token="v527-trinkets-test-token")
                app.state.jobs.remember_verified_fresh_environment(env)
                sessions=[]
                with TestClient(app,base_url="http://127.0.0.1:8765") as c:
                    for index,pair in enumerate(PAIRS):
                        label="trinkets_%d"%index
                        row={"selected_trinket_ids":list(pair),
                             "status":"NOT_STARTED"}
                        record["cases"][label]=row;checkpoint()
                        controls=v525.controls(pair)
                        request={"controls":controls,"binary":str(binary),
                                 "revision":v524.REV,
                                 "current_season_product":True,
                                 "installed_season_game_build":v524.BUILD,
                                 "installed_manifest_sha256":installed,
                                 "user_socket_total":4}
                        plan=http(c,"POST","/api/v1/sessions/plan",request)
                        need(plan.get("status")=="READY_ZERO_NATIVE" and
                             plan.get("native_calls")==0,
                             "ORDINARY_V212_PLAN_NOT_READY")
                        sid=plan["session_id"]
                        row["session_key"]=sid
                        row["base_B"]=plan["plan"]["base_B"]
                        row["final_T"]=plan["plan"]["final_T"]
                        need(row["base_B"]==row["final_T"]==3107,
                             "TRINKET_CHANGED_FREE_G_BUDGET")
                        need(sid not in sessions,
                             "DIFFERENT_TRINKETS_REUSED_SAME_SESSION")
                        sessions.append(sid)
                        folder=root/sid
                        selected=json.loads((folder/"user.json").read_text("utf8"))
                        need([r["item_id"] for r in selected["trinkets"]]
                             ==list(pair),"USER_TRINKET_ITEM_IDS_DRIFT")
                        started=http(c,"POST","/api/v1/sessions/start",request)
                        need(started["status"]=="WORKER_STARTED" and
                             started["session_id"]==sid and
                             started.get("static_L_native_calls_this_start",0)==0,
                             "TRINKETS_WORKER_OR_UNEXPECTED_STATIC_NATIVE")
                        exit_code=app.state.jobs.children[sid].wait(timeout=660)
                        row["worker_exit"]=exit_code
                        if exit_code!=0:
                            state=web.sessions.paths(folder)["state"]
                            if state.is_file():
                                doc=json.loads(state.read_text("utf8"))
                                reason=doc.get("reason","")
                                row["original_error_code"]=re.findall(
                                    r"[A-Z][A-Z0-9_]{4,120}",reason)[:4]
                            row["status"]="FAILED_ACTUAL_SIMC_WORKER"
                            checkpoint()
                            return 2
                        result=http(c,"GET",f"/api/v1/sessions/{sid}/result")
                        need(result["native_calls_cumulative"]==6 and
                             result["base_B"]==result["final_T"]==3107,
                             "DPS_SIX_OR_BUDGET_DRIFT")
                        user=result["user_result"]
                        best=user["observed_first_choice"]
                        need(user["confidence_level"]==0.95 and
                             user["global_optimum_proven"] is False and
                             best["observed_dps_mean"]>0 and
                             best["simc_sem"]>=0 and
                             sum(best["absolute_rating_T"].values())==3107,
                             "REAL_NATIVE_DPS_SEM_95_T_MISMATCH")
                        files=native_files(folder)
                        for f in files["input.simc"]:
                            text=f.read_text("utf8")
                            for slot,item in zip(("trinket1","trinket2"),pair):
                                matches=[line for line in text.splitlines()
                                         if line.startswith(slot+"=")]
                                need(len(matches)==1 and
                                     "id="+str(item) in matches[0],
                                     "SIMC_TRINKET_ITEM_ID_NOT_SERIALIZED")
                        row["observed_dps_mean"]=best["observed_dps_mean"]
                        row["simc_sem"]=best["simc_sem"]
                        row["final_absolute_T"]=best["absolute_rating_T"]
                        row["input_sha256"]=[sha(f) for f in files["input.simc"]]
                        row["json2_sha256"]=[sha(f) for f in files["result.json"]]
                        row["native_receipt_sha256"]=[sha(f) for f in
                                                       files["native_receipt.json"]]
                        row["native_calls"]=6
                        record["new_dps_native_confirmed"]+=6
                        row["status"]="PASS_REAL_SIX_SIMC_NATIVE"
                        checkpoint()
                    # Cache-only only on final trinket pair; no extra SimC
                    sid=sessions[-1]
                    replay=http(c,"POST",f"/api/v1/sessions/{sid}/cache-only",{})
                    need(replay["new_native_execution_permitted"] is False,
                         "CACHE_REPLAY_ALLOWED_NATIVE")
                    need(app.state.jobs.children[sid].wait(timeout=180)==0,
                         "CACHE_REPLAY_WORKER_FAILED")
                    restored=http(c,"GET",f"/api/v1/sessions/{sid}/result")
                    last=record["cases"]["trinkets_2"]
                    need(restored["cache_hits_this_run"]==6 and
                         restored["native_calls_cumulative"]==6 and
                         restored["user_result"]["observed_first_choice"][
                           "observed_dps_mean"]==last["observed_dps_mean"],
                         "REPLAY_CACHE_IDENTITY_OR_DPS_DRIFT")
                    last["cache_replay_verified_hits"]=6
                    last["cache_replay_new_native"]=0
                    need(record["new_dps_native_confirmed"]==MAX_DPS and
                         len(set(sessions))==len(PAIRS),
                         "TRINKET_DISJOINT_SESSION_OR_DPS_NATIVE_COUNT")
                    record["status"]="PASS_REAL_THREE_TRINKET_SIX_DPS_AND_CACHE"
                    checkpoint()
                    return 0
    except Exception as exc:
        record["status"]="BLOCKED_OR_PARTIAL_REAL_TRINKETS"
        record["error_kind"]=type(exc).__name__
        record["stable_error_tokens"]=re.findall(
            r"[A-Z][A-Z0-9_]{4,120}",str(exc))[:6]
        checkpoint()
        return 3
    finally:
        print("V527_THREE_TRINKET_RESULT "+json.dumps({
           "status":record["status"],
           "environment_native":record["new_environment_native"],
           "dps_native_confirmed":record["new_dps_native_confirmed"],
           "cases":{k:v.get("status") for k,v in record["cases"].items()}},
           ensure_ascii=False,sort_keys=True),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--binary",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    a=p.parse_args();sys.exit(run(a.binary,a.out))
