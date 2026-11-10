#!/usr/bin/env python3
"""Real same-profile 1008 Native-call v312-v290 A/B (explicit one-shot).

Compare actual 35/320 SimC DPS, 95 selected-pair and measured elapsed,
NOT predictions and NOT an unverified history transplant. Each experimental
policy has the same source-bound v291 staged context, fixed Native-call cap
and independent output dir. Each run has <=540s Native/coordinator budget;
source/environment preflight and checkpoint work are reported separately.
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
from runner import v308_dense_native_checkpoint as checkpoint
from runner import v312_model_guided_multiregion_policy as v312
from integration_probes import p2_new_profile_product_e2e_once as fresh
from integration_probes import p3_haj_real_local_web_native_e2e as web_probe

SCHEMA="p2_v312_same_profile_equal_1008_native_calls_real_ab_v1"
ROOT=pathlib.Path("out/p2_v312_real_equal_1008_once").resolve()
RECEIPT=ROOT/"receipt.json"
BUDGET=1008
TIME_CAP=540
PROFILE_SHA="e193aacef751b81dcdb8b06abbedf7aa458c0ae46eeb23898b501cf3314d7f8c"


class ProbeBlocked(RuntimeError):
    pass


def need(ok,why):
    if not ok:
        raise ProbeBlocked(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(doc):
    tmp=RECEIPT.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc,sort_keys=True,indent=2,
                              ensure_ascii=False,allow_nan=False)+"\n")
    tmp.replace(RECEIPT)


def selected(rows,iteration):
    return sorted(
        (r for r in rows if r["phase"]=="precision" and
         r["iterations"]==iteration),
        key=lambda r:(-r["dps_mean"],r["case_key"]))


def trial(label,*,ctx,flask,binary,output,experiment,doc):
    output=pathlib.Path(output).parent/("v312_real_ab_"+label)
    doc["paths"][label]=str(output)
    save(doc)
    start=time.perf_counter()
    report=durable.run(
        ctx,flask,binary,output,max_native_calls=BUDGET,
        max_new_native_this_invocation=BUDGET,
        max_elapsed_seconds=TIME_CAP,
        model_guided_multiregion=experiment,
        open_folder=False)
    elapsed=round(time.perf_counter()-start,3)
    journal=output/"V291_JOURNAL.jsonl"
    cases=durable._load_journal(journal) if journal.is_file() else []
    result={
        "policy":report["policy"],
        "status":report["status"],
        "native_attempts":report["native_attempts_cumulative"],
        "new_native":report["new_native_this_invocation"],
        "elapsed_simc_and_planner_seconds":elapsed,
        "journal_original_sha256":sha(journal.read_bytes()),
        "scout_rows":sum(r["phase"]=="scout" for r in cases),
        "precision_rows":sum(r["phase"]=="precision" for r in cases),
        "original_source_profile_sha256":ctx["identity"]["source_profile_sha256"],
        "original_binary_sha256":ctx["identity"]["binary_sha256"],
        "best_confirmed":None,
        "selected_pair_95":report["confirmed_selected_pair_95"],
        "model_predictions_never_native_proof":True,
        "global_optimum_proven":False}
    real_confirm=selected(cases,ctx["identity"]["confirm_iterations"])
    if real_confirm:
        r=real_confirm[0]
        result["best_confirmed"]={
            "target":r["target"],"dps_mean":r["dps_mean"],
            "dps_sem":r["dps_sem"],"iterations":r["iterations"],
            "native_sha256":r["native_sha256"],"case_key":r["case_key"]}
    doc["trials"][label]=result
    save(doc)
    # This checks the session SHA, original input.simc, JSON2 and receipt
    # without one additional SimC call.
    replay=durable.run(
        ctx,flask,binary,output,max_native_calls=BUDGET,
        max_new_native_this_invocation=0,cache_only=True,
        model_guided_multiregion=experiment,open_folder=False)
    need(replay["new_native_this_invocation"]==0 and
         replay["completed_cases"]==len(cases),
         "V312_"+label.upper()+"_CACHE_ONLY_REPLAY_DRIFT")
    result["same_job_cache_only_replay_new_native"]=0
    save(doc)
    return result


def main():
    need(os.getenv("P2_V312_EQUAL_NATIVE_ONCE")=="1",
         "V312_EXPLICIT_REAL_AB_SOURCE_REQUIRED")
    case,controls=fresh.selected_case("destruction_warlock_4ordinary_T3400")
    need((case["character_class"],case["character_spec"],
          case["character_race"],case["target_ilevel"],
          case["final_T"],case["sockets"],case["special_gem"])==
         ("warlock","destruction","human",334,3400,4,None),
         "V312_REAL_USER_CASE_NOT_SAME_AS_ORIGINAL_HISTORY")
    binary=pathlib.Path("out/binary/simc").resolve(strict=True)
    need(sha(binary.read_bytes())==fresh.BINARY_SHA,
         "V312_BINARY_SHA_NOT_PINNED_APPROVED_SIMC")
    ROOT.mkdir(parents=True,exist_ok=True)
    need(not RECEIPT.exists(),"V312_EXPERIMENT_NOT_ONE_SHOT")
    doc={
        "schema":SCHEMA,"status":"STARTED",
        "same_exact_new_user_scenario":True,
        "new_environment_native":0,
        "source_profile_sha256":PROFILE_SHA,
        "binary_sha256":fresh.BINARY_SHA,
        "revision":fresh.REVISION,
        "game_build":fresh.BUILD,
        "max_native_calls_per_algorithm":BUDGET,
        "max_elapsed_seconds_per_algorithm":TIME_CAP,
        "trials":{},"paths":{},
        "multiple_comparisons_corrected_95":False,
        "global_optimum_proven":False,
        "v290_default_policy_changed":False,
        "no_old_native_case_imported":True}
    save(doc)
    try:
        need(v312.options(BUDGET)["global_scouts"]==128 and
             v312.options(BUDGET)["adaptive_scouts"]==864 and
             v312.options(BUDGET)["precision_calls"]==16,
             "V312_EXACT_1008_POLICY_CAP_DRIFT")
        build=retail.discover(region="KR")
        need(build["game_build"]==fresh.BUILD,
             "V312_CURRENT_KOREA_RETAIL_BUILD_NOT_PINNED")
        need(all(os.getenv(k) for k in (
             "BLIZZARD_CLIENT_ID","BLIZZARD_CLIENT_SECRET",
             "WCL_CLIENT_ID","WCL_CLIENT_SECRET")),
             "V312_SOURCE_CREDENTIALS_REQUIRED")
        root=ROOT/"product_workspace"
        need(not root.exists(),"V312_FRESH_PRODUCT_WORKSPACE_REQUIRED")
        root.mkdir()
        environment=web.LocalJobs(root).build_season_environment(
            game_build=fresh.BUILD,target_ilevel=case["target_ilevel"],
            auto_initial_core_build=True,
            auto_initial_core_simc_binary=str(binary),
            simc_revision_hint=fresh.REVISION,
            existing_special_gem_id=None,
            source_target_socket_count=case["sockets"])
        compilation=environment.get("source_compilation") or {}
        install=compilation.get("verified_environment_install") or {}
        layout=compilation.get("physical_gem_layout_unadmitted") or {}
        doc["new_environment_native"]=environment.get("native_calls",0)
        doc["installed_environment_sha256"]=install.get("manifest_sha256")
        doc["environment_budget"]={key:environment.get(key)
                                    for key in ("G","J","F","O","B","T")}
        need(environment.get("environment_ready") is True and
             environment.get("environment_installed") is True and
             install.get("status")==
               "FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY" and
             type(doc["new_environment_native"]) is int and
             0<=doc["new_environment_native"]<=3 and
             layout.get("socket_total")==4 and
             layout.get("special_gem_id") is None and
             len(set(layout.get("ordinary_gem_ids") or []))==4 and
             environment["B"]==environment["G"]+environment["J"]+
                environment["F"] and
             environment["T"]==environment["B"] and
             sum(environment["O"].values())==0,
             "V312_FRESH_GJFO_INSTALLED_OPTION_SOURCES_NOT_VALID")
        save(doc)
        with web_probe.verified_current_catalog(
                compilation["source_catalog_path"],fresh.BUILD):
            app=web.create_app(root=root,token="v312-local-equal-once")
            app.state.jobs.remember_verified_fresh_environment(environment)
            controls["oil_hands"]=[]
            payload={
                "controls":controls,"binary":str(binary),
                "revision":fresh.REVISION,"current_season_product":True,
                "max_native_calls":12,
                "max_new_native_this_invocation":1,
                "max_elapsed_seconds":360}
            with TestClient(app,base_url="http://127.0.0.1:8765") as client:
                headers={"x-simc-local-token":"v312-local-equal-once",
                         "origin":"http://127.0.0.1:8765"}
                response=client.post("/api/v1/longrun/prepare",
                                     headers=headers,json=payload)
                if response.status_code!=200:
                    try:
                        detail=response.json().get("detail",{})
                        code=detail.get("code") if type(detail) is dict else str(detail)
                    except (ValueError,TypeError):
                        code="UNKNOWN_WEB_ERROR"
                    raise ProbeBlocked("V312_PRODUCT_PREPARE_HTTP_%d_%s"%(
                        response.status_code,str(code)[:100]))
                session=response.json()
                need(session.get("status")==
                     "LONGRUN_SOURCE_PREPARED_NO_DPS_NATIVE",
                     "V312_ZERO_DPS_WEB_PROFILE_PREPARE_REQUIRED")
                inputs=client.get("/api/v1/sessions/%s/inputs"%
                     session["session_id"],headers=headers)
                need(inputs.status_code==200 and
                     inputs.json()["user"]["target"]["final_T"]==3400,
                     "V312_WEB_MANUAL_FINAL_T_DRIFT")
                source_manifest=longrun.source_manifest(
                    root/session["session_id"])
                base=longrun.entry.source(source_manifest)
                staged,_=durable.stage_extended_manifest(
                    base,source_manifest,BUDGET,
                    source_loader=longrun.entry.source)
                ctx,flask=staged["context"],staged["flask"]
                identity=ctx["identity"]
                normalized=ctx["bundle"]["prepared"]["scenario"]
                B,lo,hi=durable.constraints.bounds(
                    normalized,durable.adaptive.feasible_budget(ctx,flask))
                need(B==3400 and lo==(0,0,0,165) and
                     hi==(2040,2040,2040,2040) and
                     identity["approved_final_T"]==3400 and
                     identity["source_profile_sha256"]==PROFILE_SHA and
                     identity["binary_sha256"]==fresh.BINARY_SHA and
                     identity["revision"]==fresh.REVISION and
                     identity["scout_iterations"]==35 and
                     identity["confirm_iterations"]==320 and
                     sum(identity["oil_vector"].values())==0,
                     "V312_ORIGINAL_SAME_PROFILE_BOUNDS_ITERATIONS_DRIFT")
                doc["new_source_scenario_digest"]=identity["scenario_digest"]
                doc["user_profile_source_sha256"]=identity["source_profile_sha256"]
                save(doc)
                path=staged["paths"]["output_dir"]
                # Run new policy first; independent v290 retains its original
                # unmodified default policy + exact-same staged source.
                m=trial("v312_model_guided",ctx=ctx,flask=flask,binary=binary,
                        output=path,experiment=True,doc=doc)
                b=trial("v290_original",ctx=ctx,flask=flask,binary=binary,
                        output=path,experiment=False,doc=doc)
                doc["equal_budget_completed"]=(
                    m["native_attempts"]==b["native_attempts"]==BUDGET and
                    m["status"]==b["status"]=="BUDGET_EXHAUSTED")
                if m["best_confirmed"] and b["best_confirmed"]:
                    first=m["best_confirmed"]
                    second=b["best_confirmed"]
                    doc["model_minus_original_confirmed_mean_dps"]=(
                        first["dps_mean"]-second["dps_mean"])
                    doc["nominal_two_candidate_95_halfwidth"]=(1.95996398454*
                        (first["dps_sem"]**2+second["dps_sem"]**2)**.5)
                else:
                    doc["model_minus_original_confirmed_mean_dps"]=None
                    doc["nominal_two_candidate_95_halfwidth"]=None
                doc["winner_selection_bias_corrected"]=False
                doc["status"]=(
                    "PASS_REAL_EQUAL_1008_NATIVE_SAME_PROFILE" if
                    doc["equal_budget_completed"] else
                    "PASS_REAL_TIME_CAPPED_PARTIAL_COMPARISON")
                save(doc)
                print("P2_V312_V290_REAL_AB_NATIVE_COMPLETED",
                    json.dumps({"status":doc["status"],
                        "trials":doc["trials"],
                        "equal_budget_completed":doc["equal_budget_completed"],
                        "model_minus_original_confirmed_mean_dps":
                           doc["model_minus_original_confirmed_mean_dps"]},
                               sort_keys=True,ensure_ascii=False),flush=True)
        return doc
    except BaseException as exc:
        doc["status"]="BLOCKED_OR_PARTIAL_"+type(exc).__name__
        msg=str(exc)
        doc["first_error_code"]=(msg if re.fullmatch(
            r"[A-Z][A-Z0-9_]{3,120}",msg) else type(exc).__name__)
        save(doc)
        raise


if __name__=="__main__":
    main()
