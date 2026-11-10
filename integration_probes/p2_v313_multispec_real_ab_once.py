#!/usr/bin/env python3
"""v313 multi-spec real source-first v290/v312 matched-time/call probe.

No historical winner/Native JSON2 re-use in independent new 26-DPS product
profiles. Each chosen condition gets a newly built v113/v216/v212 verified
season environment and source-first v098 user gear. Runtime is capped at
540sec/1008 cases per arm; iterations are tracked but NOT claimed equal.
The experiment is NOT Windows user-click proof or optimizer promotion.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import time

from fastapi.testclient import TestClient

from runner import v113_local_web_api as web
from runner import v289_retail_live_build_source as retail
from runner import v291_durable_multiscale_native_runner as durable
from runner import v293_local_longrun_session as longrun
from runner import v313_multispec_matrix_contract as matrix
from integration_probes import p2_new_profile_product_e2e_once as fresh
from integration_probes import p3_haj_real_local_web_native_e2e as web_probe

SCHEMA="p2_v313_source_first_4spec_x2_distribution_real_AB_v1"
ROOT=pathlib.Path("out/p2_v313_multispec_matrix").resolve()
RECEIPT_NAME="receipt.json"


class V313Blocked(RuntimeError):
    pass


def need(ok,why):
    if not ok:
        raise V313Blocked(why)


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def write(path,doc):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(".tmp")
    temp.write_text(json.dumps(
        doc,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
    temp.replace(path)


def _trial(label,*,context,flask,binary,base_output,case_root,
           receipt,doc,experimental):
    result_dir=pathlib.Path(base_output).parent/("v313_"+label)
    doc["original_output_paths"][label]=str(result_dir)
    write(receipt,doc)
    start=time.monotonic()
    report=durable.run(
        context,flask,binary,result_dir,max_native_calls=matrix.NATIVE_CAP,
        max_new_native_this_invocation=matrix.NATIVE_CAP,
        max_elapsed_seconds=matrix.TIME_CAP_SECONDS,
        model_guided_multiregion=experimental,
        open_folder=False)
    elapsed=time.monotonic()-start
    journal=result_dir/"V291_JOURNAL.jsonl"
    rows=durable._load_journal(journal)
    summary=matrix.trial_summary(
        report,rows,elapsed,policy_name=label,
        original_profile_sha256=context["identity"]["source_profile_sha256"])
    summary["original_v291_journal_sha256"]=sha(journal)
    summary["native_file_bytes_rechecked_cache_only"]=False
    doc["trials"][label]=summary
    write(receipt,doc)
    replay=durable.run(
        context,flask,binary,result_dir,max_native_calls=matrix.NATIVE_CAP,
        max_new_native_this_invocation=0,cache_only=True,
        model_guided_multiregion=experimental,
        open_folder=False)
    need(replay["new_native_this_invocation"]==0
         and replay["completed_cases"]==len(rows),
         "V313_"+label.upper()+"_ORIGINAL_NATIVE_CACHE_ONLY_REPLAY")
    doc["trials"][label]["native_file_bytes_rechecked_cache_only"]=True
    write(receipt,doc)
    print("P2_V313_REAL_ARM_COMPLETE",json.dumps({
        "case_id":doc["case"]["id"],"arm":label,"native_calls":len(rows),
        "total_iterations":summary["actual_simc_iterations"],
        "measured_seconds":summary["measured_seconds"],
        "best_confirmed":summary["best_confirmed_320"]},
        sort_keys=True),flush=True)
    return summary


def main():
    need(os.getenv("P2_V313_MULTISPEC_ONCE")=="1",
         "EXPLICIT_V313_ACTUAL_SIMC_OPT_IN_REQUIRED")
    case_id=os.getenv("P2_V313_CASE_ID","")
    case,controls=matrix.select(case_id)
    need(matrix.validate_matrix()["cases"]==8,
         "V313_EIGHT_CASE_CONTRACT_REQUIRED")
    need(fresh.BUILD==matrix.SOURCE_BUILD and
         fresh.BINARY_SHA==matrix.BINARY_SHA256,
         "V313_SOURCE_BINARY_OR_BUILD_DRIFT")
    case_root=ROOT/case_id
    need(not case_root.exists(),"V313_ONE_SHOT_CASE_DIRECTORY_ALREADY_EXISTS")
    case_root.mkdir(parents=True)
    receipt=case_root/RECEIPT_NAME
    doc={
        "schema":SCHEMA,"case":case,
        "status":"STARTED",
        "source_build":matrix.SOURCE_BUILD,
        "simc_revision":fresh.REVISION,
        "binary_sha256":matrix.BINARY_SHA256,
        "native_call_cap_per_policy":matrix.NATIVE_CAP,
        "elapsed_cap_per_policy_seconds":matrix.TIME_CAP_SECONDS,
        "scout_iterations":matrix.ITER_SCOUT,
        "confirmation_iterations":matrix.ITER_CONFIRM,
        "source_profile_sha256":None,
        "scenario_digest":None,
        "environment_native_calls":None,
        "environment_ready":False,
        "trials":{},"original_output_paths":{},
        "pairwise_result":None,
        "scenario_from_existing_native_winner":False,
        "prior_dps_cache_reused":False,
        "familywise_95_proven":False,
        "global_optimum_proven":False,
        "default_v290_changed":False,
        "user_windows_click_tested":False,
        "same_native_call_cap_not_equal_iterations":True}
    write(receipt,doc)
    try:
        binary=pathlib.Path("out/binary/simc").resolve(strict=True)
        need(sha(binary)==matrix.BINARY_SHA256,
             "V313_PINNED_ORIGINAL_SIMC_BINARY_SHA_DRIFT")
        build=retail.discover(region="KR")
        need(build["game_build"]==matrix.SOURCE_BUILD,
             "V313_CURRENT_SEASON_GAME_BUILD_CHANGED")
        need(all(os.getenv(key) for key in (
             "BLIZZARD_CLIENT_ID","BLIZZARD_CLIENT_SECRET",
             "WCL_CLIENT_ID","WCL_CLIENT_SECRET")),
             "V313_LIVE_SEASON_SOURCE_CREDENTIALS_REQUIRED")
        workspace=case_root/"product_workspace"
        workspace.mkdir()
        environment=web.LocalJobs(workspace).build_season_environment(
            game_build=matrix.SOURCE_BUILD,
            target_ilevel=case["ilevel"],
            auto_initial_core_build=True,
            auto_initial_core_simc_binary=str(binary),
            simc_revision_hint=fresh.REVISION,
            existing_special_gem_id=None,
            source_target_socket_count=case["ordinary_gems"])
        source=environment.get("source_compilation") or {}
        installed=source.get("verified_environment_install") or {}
        layout=source.get("physical_gem_layout_unadmitted") or {}
        doc["environment_native_calls"]=environment.get("native_calls")
        doc["environment_ready"]=bool(environment.get("environment_ready"))
        doc["environment_budget"]={key:environment.get(key)
                                    for key in ("G","J","F","O","B","T")}
        doc["installed_manifest_sha256"]=installed.get("manifest_sha256")
        write(receipt,doc)
        need(environment.get("environment_ready") is True and
             environment.get("environment_installed") is True and
             installed.get("status")==
                 "FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY" and
             type(doc["environment_native_calls"]) is int and
             0<=doc["environment_native_calls"]<=3 and
             layout.get("special_gem_id") is None and
             layout.get("socket_total")==4 and
             len(set(layout.get("ordinary_gem_ids") or []))==4 and
             environment["B"]==environment["G"]+environment["J"]+
                 environment["F"] and
             environment["T"]==environment["B"] and
             sum(environment["O"].values())==0,
             "V313_SEASON_GJFO_OR_SOURCE_LAYOUT_NOT_VERIFIED")
        with web_probe.verified_current_catalog(
                source["source_catalog_path"],matrix.SOURCE_BUILD):
            app=web.create_app(root=workspace,token="v313-multispec-test")
            app.state.jobs.remember_verified_fresh_environment(environment)
            payload={
                "controls":controls,"binary":str(binary),
                "revision":fresh.REVISION,"current_season_product":True,
                "max_native_calls":12,
                "max_new_native_this_invocation":1,
                "max_elapsed_seconds":360}
            with TestClient(app,base_url="http://127.0.0.1:8765") as client:
                headers={"x-simc-local-token":"v313-multispec-test",
                         "origin":"http://127.0.0.1:8765"}
                response=client.post("/api/v1/longrun/prepare",
                                     headers=headers,json=payload)
                if response.status_code!=200:
                    try:
                        d=response.json().get("detail",{})
                        code=d.get("code") if isinstance(d,dict) else str(d)
                    except (ValueError,TypeError):
                        code="UNKNOWN_WEB_PREPARE_ERROR"
                    raise V313Blocked(
                        "V313_PRODUCT_PREPARE_HTTP_"+str(response.status_code)+
                        "_"+str(code)[:100])
                prepared=response.json()
                need(prepared.get("status")==
                     "LONGRUN_SOURCE_PREPARED_NO_DPS_NATIVE",
                     "V313_ZERO_DPS_FRESH_WEB_PREPARE_REQUIRED")
                sid=prepared["session_id"]
                actual=client.get(
                    f"/api/v1/sessions/{sid}/inputs",headers=headers)
                need(actual.status_code==200 and
                     actual.json()["user"]["target"]["final_T"]==
                     case["final_T"],
                     "V313_USER_MANUAL_T_NOT_IN_PRODUCT_PROFILE")
                manifest=longrun.source_manifest(workspace/sid)
                base=longrun.entry.source(manifest)
                staged,_=durable.stage_extended_manifest(
                    base,manifest,matrix.NATIVE_CAP,
                    source_loader=longrun.entry.source)
                context,flask=staged["context"],staged["flask"]
                identity=context["identity"]
                normalized=context["bundle"]["prepared"]["scenario"]
                budget,lo,hi=durable.constraints.bounds(
                    normalized,durable.adaptive.feasible_budget(
                        context,flask))
                need(budget==case["final_T"] and
                     identity["approved_final_T"]==case["final_T"] and
                     len(lo)==len(hi)==4 and
                     all(0<=x<=y<=budget for x,y in zip(lo,hi)) and
                     all(y<=math.floor(budget*
                         case["max_single_stat_percent"]/100)+1
                         for y in hi) and
                     identity["binary_sha256"]==matrix.BINARY_SHA256 and
                     identity["revision"]==fresh.REVISION and
                     identity["scout_iterations"]==matrix.ITER_SCOUT and
                     identity["confirm_iterations"]==matrix.ITER_CONFIRM and
                     sum(identity["oil_vector"].values())==0,
                     "V313_POLICY_SOURCE_BOUNDS_OR_SAME_35_320_ITER_DRIFT")
                doc["source_profile_sha256"]=identity["source_profile_sha256"]
                doc["scenario_digest"]=identity["scenario_digest"]
                doc["base_B"]=budget
                doc["bounds_lower"]=list(lo)
                doc["bounds_upper"]=list(hi)
                write(receipt,doc)
                output=staged["paths"]["output_dir"]
                # Alternate execution order by distribution to reduce the
                # possibility of systematic first-arm host/thermal bias.
                order=(("v290_original",False),
                       ("v312_model_guided",True)) if
                       case_id.endswith("__wide") else (
                       ("v312_model_guided",True),
                       ("v290_original",False))
                for label,experiment in order:
                    _trial(label,context=context,flask=flask,
                           binary=binary,base_output=output,
                           case_root=case_root,receipt=receipt,
                           doc=doc,experimental=experiment)
                doc["pairwise_result"]=matrix.paired_result(
                    case,doc["trials"]["v290_original"],
                    doc["trials"]["v312_model_guided"])
                doc["status"]=(
                    "PASS_REAL_TWO_ALGORITHMS_FULL_CAP" if
                    doc["pairwise_result"]["status"]==
                    "COMPLETE_EQUAL_NATIVE_CALLS" else
                    "PASS_REAL_TWO_ALGORITHMS_TIME_CAPPED_PARTIAL")
                write(receipt,doc)
                print("P2_V313_MULTISPEC_NATIVE_CASE_DONE",json.dumps({
                    "case_id":case_id,"status":doc["status"],
                    "pairwise_result":doc["pairwise_result"]},
                    sort_keys=True),flush=True)
                return doc
    except BaseException as exc:
        doc["status"]="BLOCKED_OR_PARTIAL_"+type(exc).__name__
        message=str(exc)
        doc["first_error_code"]=(message if re.fullmatch(
            r"[A-Z][A-Z0-9_]{3,150}",message)
            else type(exc).__name__)
        write(receipt,doc)
        raise


if __name__=="__main__":
    import math
    main()
