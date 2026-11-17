#!/usr/bin/env python3
"""One bounded TRUE zero-source current-season → verified v212 → real user SimC.

Does not seed any historical season catalog, nominal gem JSON, cached receipts,
installed environment, old session or old DPS cache.  The existing v113 web
Build, v216/v222/v212, v098/v096/v094 and SimC retain all authority.
Explicit trinket IDs below are USER TEST INPUTS, not season environment seeds.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import zipfile

from fastapi.testclient import TestClient

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner"),str(ROOT/"integration_probes")]
import v113_local_web_api as web
import v289_retail_live_build_source as retail
from integration_probes import p3_haj_real_local_web_native_e2e as real_web

SCHEMA="p1_v552_true_zero_source_user_e2e_once_v1"
REQUIRED_SECRETS=("BLIZZARD_CLIENT_ID","BLIZZARD_CLIENT_SECRET",
                  "WCL_CLIENT_ID","WCL_CLIENT_SECRET")
TRINKETS=(270175,270173)  # Explicit test user choices, NEVER source metadata.
STATS=("crit_rating","haste_rating","mastery_rating","versatility_rating")

def sha(path):
    h=hashlib.sha256()
    with pathlib.Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def fail(condition,code):
    if not condition:
        raise RuntimeError("V552_"+code)

def safe_error(exc):
    code=str(exc).split(":",1)[0].split("\n",1)[0]
    return code if re.fullmatch(r"[A-Z][A-Z0-9_]{3,110}",code) else type(exc).__name__

class SourceCredentials:
    def load(self):
        got={k:os.environ.get(k,"") for k in REQUIRED_SECRETS}
        return got if all(got.values()) else None

def http(client,method,uri,payload=None):
    headers={"x-simc-local-token":"v552-actual-zero-source-test",
             "origin":"http://127.0.0.1:8765"}
    response=(client.get(uri,headers=headers) if method=="GET"
        else client.post(uri,json=payload if payload is not None else {},
                         headers=headers))
    if response.status_code!=200:
        doc=response.json()
        detail=doc.get("detail",{}) if type(doc) is dict else {}
        code=detail.get("code","UNEXPECTED") if type(detail) is dict else "UNEXPECTED"
        raise RuntimeError("V552_HTTP_"+str(response.status_code)+"_"+str(code)[:65])
    return response.json()

def run(binary,output_dir):
    output_dir=pathlib.Path(output_dir).resolve()
    output_dir.mkdir(parents=True,exist_ok=True)
    receipt=output_dir/"V552_TRUE_ZERO_SOURCE_TO_USER.json"
    r={"schema":SCHEMA,"status":"STARTED","zero_source_input":True,
       "prior_stage_receipt_used":False,"prior_static_cache_used":False,
       "prior_dps_cache_used":False,"historical_nominal_J_used":False,
       "product_runtime_AI_calls":0,"new_environment_native":None,
       "new_dps_native":0,"installed":False,
       "full_product_e2e":"PENDING","global_optimum_proven":False,
       "test_user_trinkets":list(TRINKETS)}
    def save():
        receipt.write_text(json.dumps(r,ensure_ascii=False,sort_keys=True,
            allow_nan=False,indent=2,default=str)+"\n",encoding="utf8")
    save()
    try:
        binary=pathlib.Path(binary).resolve(strict=True)
        fail(binary.name.lower()=="simc.exe" and not binary.is_symlink(),
             "OFFICIAL_SIMC_BINARY_REQUIRED")
        expected_sha=os.environ.get("SIMC_PINNED_BINARY_SHA256") or ""
        rev=os.environ.get("SIMC_PINNED_SOURCE_COMMIT") or ""
        binary_build=os.environ.get("SIMC_PINNED_GAME_BUILD") or ""
        fail(re.fullmatch(r"[a-f0-9]{64}",expected_sha) is not None
             and re.fullmatch(r"[a-f0-9]{40}",rev) is not None
             and sha(binary)==expected_sha,
             "SIMC_BINARY_OR_REVISION_IDENTITY")
        fail(SourceCredentials().load() is not None,
             "SEASON_AUTH_CREDENTIALS_MISSING")
        # Program detects the build independently; never inject 70783 as
        # environment data. A different actual build requires corresponding
        # same-build SimC binary (no stale fallback).
        live=retail.discover(region="KR")
        r["live_build"]=live.get("game_build")
        r["live_version_source_sha256"]=live.get("source_sha256")
        r["pinned_native_build"]=binary_build
        if live["game_build"]!=binary_build:
            r["status"]="PENDING_NEW_SAME_BUILD_SIMC_BINARY"
            r["first_blocker"]="LIVE_BUILD_NOT_THE_AVAILABLE_PINNED_SIMC_BUILD"
            save()
            return 2
        fail(binary_build in (
            subprocess.run([str(binary)],input="",capture_output=True,
                           text=True,errors="replace",cwd=binary.parent,
                           timeout=25).stdout),
             "PINNED_SIMC_BANNER_GAME_BUILD_DRIFT")
        # No historical season JSON, catalog, J94 reference or preinstalled
        # environment may be presented as test input by this runner.
        old=ROOT/"data"
        prohibited=list(old.glob("current_season_*.json"))
        prohibited+=list((old/"season_ordinary_gem_nominal").glob("*.json"))
        prohibited+=list(old.glob("v202_*.json"))
        prohibited+=list(old.glob("v206_*.json"))
        fail(not prohibited,"HISTORICAL_SEASON_SOURCE_NOT_QUARANTINED")
        with tempfile.TemporaryDirectory(prefix="v552-new-season-",dir=output_dir) as temp:
            root=pathlib.Path(temp)/"runs"
            root.mkdir()
            fail(not list(root.iterdir()),"ROOT_NOT_EMPTY_BEFORE_FIRST_SOURCE")
            jobs=web.LocalJobs(root,source_credential_store=SourceCredentials())
            # No hard-coded target ilvl. User interface's existing M1 owner.
            myth=jobs.discover_season_myth_target(live["game_build"])
            r["M1"]={k:myth.get(k) for k in (
                "status","reason_code","game_build","target_ilevel",
                "currency_ids","currency_csv_sha256",
                "original_v161_receipt_sha256")}
            save()
            if myth.get("status")!=(
                "MYTH_TARGET_CANDIDATE_FROM_MATCHED_WAGO_V163_SOURCE"):
                r["status"]="PENDING_M1_AUTOMATIC_TARGET_SOURCE"
                r["first_blocker"]=myth.get("reason_code")
                save()
                return 2
            ilvl=myth["target_ilevel"]
            fail(type(ilvl) is int and ilvl>0 and
                 type(myth.get("currency_csv_sha256")) is str,
                 "LIVE_TARGET_ILEVEL_OR_SOURCE_SHA_INVALID")
            # The exact same normal v113 Build, not custom test budget logic.
            env=jobs.build_season_environment(
                game_build=live["game_build"],target_ilevel=ilvl,
                auto_initial_core_build=True,
                auto_initial_core_simc_binary=str(binary),
                simc_revision_hint=rev,
                existing_special_gem_id=None,
                source_target_socket_count=4,
                auto_myth_target_source_build=live["game_build"],
                auto_myth_target_source_sha256=myth["currency_csv_sha256"])
            compilation=env.get("source_compilation") or {}
            progress=env.get("zero_history_build") or {}
            installed=compilation.get("verified_environment_install") or {}
            jf=compilation.get("selected_J_F_source_owner_numeric_unadmitted") or {}
            r["M2"]={
                "source_compilation_status":compilation.get("status"),
                "source_compilation_missing":compilation.get("missing",[]),
                "first_requires":list(progress.get("requires") or [])[:25],
                "required_core_source_owner_report":progress.get(
                    "required_core_source_owner_report"),
                "static_DBC_J_status":(compilation.get(
                    "four_stat_pinned_dbc_j_source_unadmitted") or {}).get("status"),
                "selected_J_numeric_source_owner":(jf.get("J") or {}).get(
                    "numeric_source_owner"),
                "selected_J_numeric_available":type(jf.get("J")) is dict,
                "source_only_j_rating":(jf.get("J") or {}).get("rating"),
                "installed":env.get("environment_installed") is True,
                "ready":env.get("environment_ready") is True,
                "installed_manifest_sha256":installed.get("manifest_sha256"),
                "new_environment_native":env.get("native_calls")}
            r["new_environment_native"]=env.get("native_calls")
            save()
            if not (env.get("environment_ready") is True
                    and env.get("environment_installed") is True):
                r["status"]="PENDING_ACTUAL_ZERO_SOURCE_ENVIRONMENT_INSTALL"
                r["first_blocker"]="M2_EXISTING_SOURCE_OWNER_OR_INSTALL_PENDING"
                save()
                return 2
            r["installed"]=True
            r["official_budget"]={k:env[k] for k in ("G","J","F","O","B","T")}
            fail(env["B"]==env["G"]+env["J"]+env["F"] and
                 env["T"]==env["B"]+sum(env["O"].values()),
                 "OFFICIAL_GJFO_B_T_ARITHMETIC")
            install_sha=installed["manifest_sha256"]
            save()
            # The v113 web layer consumes the new v213 catalog produced in
            # THIS run; never a pre-packaged current_season catalog.
            with real_web.verified_current_catalog(
                compilation["source_catalog_path"],live["game_build"]):
                app=web.create_app(root=root,token="v552-actual-zero-source-test")
                app.state.jobs.remember_verified_fresh_environment(env)
                controls=web.sessions.standard_controls(("hunter","survival"))
                controls["race"]="human"
                controls["ilevel"]=ilvl
                controls["oil_hands"]=[]
                controls["trinket_ids"]=list(TRINKETS)
                controls["special_items"]=[]
                controls["embellishments"]=[]
                controls["final_T"]=None
                payload={
                    "controls":controls,"binary":str(binary),
                    "revision":rev,"current_season_product":True,
                    "installed_season_game_build":live["game_build"],
                    "installed_manifest_sha256":install_sha,
                    "user_socket_total":4}
                with TestClient(app,base_url="http://127.0.0.1:8765") as client:
                    planned=http(client,"POST","/api/v1/sessions/plan",payload)
                    fail(planned.get("status")=="READY_ZERO_NATIVE",
                         "USER_PLAN_NOT_READY")
                    sid=planned["session_id"]
                    r["user_plan_session_id_hash"]=hashlib.sha256(
                        sid.encode()).hexdigest()
                    r["M3_plan_status"]=planned["status"]
                    r["M3_plan_budget"]={k:planned["plan"].get(k)
                        for k in ("base_B","final_T")}
                    fail(planned["plan"]["base_B"]==env["B"] and
                         planned["plan"]["final_T"]==env["T"],
                         "USER_PLAN_B_T_DIFFERS_FROM_INSTALL")
                    profile=(root/sid/"generated"/"profile.simc")
                    fail(profile.is_file(),"USER_GENERATED_PROFILE_MISSING")
                    r["user_profile_sha256"]=sha(profile)
                    save()
                    started=http(client,"POST","/api/v1/sessions/start",payload)
                    fail(started.get("status")=="WORKER_STARTED" and
                         started.get("session_id")==sid,
                         "USER_NATIVE_WORKER_NOT_STARTED")
                    child=app.state.jobs.children[sid]
                    exitcode=child.wait(timeout=700)
                    r["DPS_worker_exit"]=exitcode
                    if exitcode!=0:
                        st=web.sessions.paths(root/sid)["state"]
                        if st.is_file():
                            state=json.loads(st.read_text("utf8"))
                            r["worker_error_code"]=safe_error(
                                RuntimeError(state.get("reason","")))
                        r["status"]="BLOCKED_DPS_NATIVE_WORKER"
                        save()
                        return 2
                    result=http(client,"GET","/api/v1/sessions/"+sid+"/result")
                    user=result["user_result"]
                    top=user["observed_first_choice"]
                    vector=top["absolute_rating_T"]
                    n=result["native_calls_cumulative"]
                    fail(n>0 and n<=6 and user["confidence_level"]==0.95
                         and user["global_optimum_proven"] is False
                         and user["final_T"]==env["T"]
                         and sum(vector.values())==env["T"]
                         and top["observed_dps_mean"]>0
                         and top["simc_sem"]>=0,
                         "DPS_SEM_95_OR_CHMV_RESULT_DRIFT")
                    r["new_dps_native"]=n
                    r["M3_result"]={
                        "native_calls":n,"absolute_CHMV":vector,
                        "observed_dps":top["observed_dps_mean"],
                        "sem":top["simc_sem"],"confidence_level":0.95,
                        "global_optimum_proven":False}
                    result_root=root/sid/"generated"/"simc_results"
                    simc_inputs=sorted(result_root.rglob("input.simc"))
                    json2=sorted(result_root.rglob("result.json"))
                    proofs=sorted(result_root.rglob("native_receipt.json"))
                    fail(len(simc_inputs)==len(json2)==len(proofs)==n,
                         "REAL_DPS_NATIVE_INPUT_JSON2_RECEIPTS_REQUIRED")
                    r["DPS_native_SHA"]={
                        "input":[sha(p) for p in simc_inputs],
                        "json2":[sha(p) for p in json2],
                        "receipt":[sha(p) for p in proofs]}
                    save()
                    replay=http(client,"POST",
                                "/api/v1/sessions/"+sid+"/cache-only",{})
                    fail(replay.get("new_native_execution_permitted") is False,
                         "CACHE_ONLY_NATIVE_PERMISSION")
                    fail(app.state.jobs.children[sid].wait(timeout=240)==0,
                         "CACHE_ONLY_WORKER_FAILED")
                    replay_result=http(client,"GET",
                                       "/api/v1/sessions/"+sid+"/result")
                    fail(replay_result["user_result"]==user and
                         replay_result["cache_hits_this_run"]==n,
                         "CACHE_ONLY_RESULT_OR_HITS_DRIFT")
                    r["cache_only_hits"]=n
                    r["cache_only_new_native"]=0
                    r["status"]="PASS_REAL_ZERO_SOURCE_TO_USER_DPS_SEM_95_CACHE"
                    save()
                    return 0
    except Exception as exc:
        r["status"]="BLOCKED_REAL_ZERO_SOURCE_PATH"
        r["error_type"]=type(exc).__name__
        r["first_blocker"]=safe_error(exc)
        save()
        return 2
    finally:
        print("V552_ZERO_SOURCE_VERDICT "+json.dumps({
            k:r.get(k) for k in ("status","live_build","pinned_native_build",
                "first_blocker","M1","M2","new_environment_native",
                "installed","official_budget","M3_plan_status",
                "new_dps_native","DPS_worker_exit","cache_only_hits")},
            ensure_ascii=False,sort_keys=True,default=str),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--simc",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    a=p.parse_args()
    raise SystemExit(run(a.simc,a.out))
