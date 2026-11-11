#!/usr/bin/env python3
"""v319 one-shot: first fresh Monk/Windwalker user profile, v290 vs v318.

User mandate: new specialization profile from the real v113/v216/v212/v098
product source path EACH experiment. Same generated profile shared by both
policy arms. No historical DPS cache or old completed profiles are imported.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import pathlib
import re
import time
import zipfile

from fastapi.testclient import TestClient

from runner import v113_local_web_api as web
from runner import v289_retail_live_build_source as retail
from runner import v291_durable_multiscale_native_runner as durable
from runner import v293_local_longrun_session as longrun
from runner import v316_optin_case_time_trace as trace
from runner import v318_sem_distance_precision_priority as sem_policy
from integration_probes import p2_new_profile_product_e2e_once as fresh
from integration_probes import p3_haj_real_local_web_native_e2e as web_probe

ROOT = pathlib.Path("out/p2_v319_windwalker_auto_T_new_user_AB").resolve()
RECEIPT = ROOT / "receipt.json"
CASE_ID = "windwalker_monk_4ordinary_auto_T"
MAX_NATIVE_PER_ARM = 64
WEB_PREPARE_BATCH_LIMIT = 32  # v113 FastAPI LongRunPrepareRequest cap
ITER_SCOUT = 35
ITER_CONFIRM = 320
EXPECTED_POLICIES = {
    "v290_original": "v290_multiscale_noisy_simplex_policy_v1",
    "v318_idea001": sem_policy.SCHEMA,
}
STATS = ("crit_rating","haste_rating","mastery_rating","versatility_rating")

class V319Blocked(RuntimeError):
    pass

def need(ok, reason):
    if not ok:
        raise V319Blocked(reason)

def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def save(doc):
    ROOT.mkdir(parents=True,exist_ok=True)
    temp = RECEIPT.with_suffix(".tmp")
    temp.write_text(json.dumps(doc,sort_keys=True,ensure_ascii=False,
                               indent=2,allow_nan=False)+"\n",encoding="utf8")
    temp.replace(RECEIPT)

def new_user_case(case_id=CASE_ID, expected_spec=("monk","windwalker")):
    from runner import v313_multispec_matrix_contract as former313
    from runner import v314_fresh_eight_spec_matrix_contract as former314
    case, controls = fresh.selected_case(case_id)
    key = (case["character_class"],case["character_spec"])
    need(key==expected_spec and
         all(key!=(row["class"],row["spec"]) for previous in (
             former313.CASES,former314.CASES)
             for row in previous.values()),
         "V319_MUST_USE_NEW_UNTESTED_DPS_SPECIALIZATION")
    need(case["target_ilevel"]==334 and case["final_T"] is None
         and case["special_gem"] is None and case["sockets"]==4,
         "V319_SELECTED_NEW_CASE_CHANGED")
    controls.update({"max_single_stat_percent":45,"oil_hands":[]})
    need(not controls.get("import_simc_profile")
         and not controls.get("profile_path")
         and not controls.get("simc_profile"),
         "V319_NO_OLD_COMPLETED_PROFILE_ALLOWED")
    need(controls["final_T"] is None, "V319_PRODUCT_CONTROLS_MUST_USE_AUTO_T")
    return case,controls

def verified_automatic_T(environment, controls):
    """Use season-engine G/J/F/O, never a manually inflated test budget."""
    need(controls.get("final_T") is None,
         "V319_MANUAL_FINAL_T_NOT_ALLOWED")
    numbers=("G","J","F","B","T")
    need(type(environment) is dict and all(
         type(environment.get(k)) is int and environment[k]>=0
         for k in numbers),
         "V319_AUTO_SEASON_BUDGET_NUMERIC_REQUIRED")
    oil=environment.get("O")
    need(type(oil) is dict and set(oil)==set(STATS)
         and all(type(x) is int and x>=0 for x in oil.values()),
         "V319_AUTO_SEASON_O_VECTOR_REQUIRED")
    need(environment["B"]==sum(environment[k] for k in ("G","J","F"))
         and environment["T"]==environment["B"]+sum(oil.values())
         and environment["T"]>0,
         "V319_AUTO_SEASON_GJFO_FORMULA_DRIFT")
    return environment["T"]

def main(*, case_id=CASE_ID, expected_spec=("monk","windwalker"),
         output_root=ROOT, receipt_path=RECEIPT,
         required_env="P2_V319_ONE_FRESH_SPEC_AB_ONCE",
         campaign_schema="p2_v319_one_new_windwalker_user_native_v290_v318_ab_v1",
         post_run_hook=None, post_run_context_hook=None,
         source_only_context_hook=None, research_scout_floor=None):
    # Previously verified v319 defaults stay intact; new campaigns must
    # supply new specialization, output folder and one-shot env guard.
    def save(doc):
        output_root.mkdir(parents=True,exist_ok=True)
        temp=receipt_path.with_suffix(".tmp")
        temp.write_text(json.dumps(doc,sort_keys=True,ensure_ascii=False,
                                   indent=2,allow_nan=False)+"\n",encoding="utf8")
        temp.replace(receipt_path)
    need(os.getenv(required_env)=="1",
         "V319_EXPLICIT_ONE_SHOT_NATIVE_OPT_IN_REQUIRED")
    need(research_scout_floor is None or
         (type(research_scout_floor) is int and research_scout_floor==32
          and callable(source_only_context_hook)
          and post_run_hook is None and post_run_context_hook is None),
         "V331_RESEARCH_RUNTIME_ONLY_WITH_SOURCE_ONLY_HOOK")
    case, controls = new_user_case(case_id,expected_spec)
    need(not output_root.exists(),"V319_NO_REUSE_OF_COMPLETED_WORKSPACE")
    doc={
        "schema":campaign_schema,
        "status":"STARTED","case":case_id,"character":case,
        "source_build":fresh.BUILD,"revision":fresh.REVISION,
        "simc_binary_sha256":fresh.BINARY_SHA,
        "manual_final_T":None,
        "target_budget_mode":"VERIFIED_AUTO_GJFO_NO_MANUAL_OVERRIDE",
        "auto_final_T":None,
        "scout_iterations":research_scout_floor or ITER_SCOUT,
        "confirmation_iterations":ITER_CONFIRM,
        "native_cap_each_arm":MAX_NATIVE_PER_ARM,
        "fresh_profile_generated_once_for_both_arms":False,
        "source_from_old_completed_simc_profile":False,
        "historical_dps_native_cache_imported":False,
        "v290_default_changed":False,"global_optimum_proven":False,
        "winner_bias_and_multiplicity_corrected":False,
        "arms":{},
    }
    save(doc)
    try:
        binary=pathlib.Path("out/binary/simc").resolve(strict=True)
        need(sha(binary)==fresh.BINARY_SHA,
             "V319_VERIFIED_SIMC_BINARY_SHA_MISMATCH")
        live=retail.discover(region="KR")
        need(live["game_build"]==fresh.BUILD,
             "V319_LIVE_GAME_BUILD_NOT_MATCH_PINNED_SIMC")
        need(all(os.getenv(k) for k in (
             "BLIZZARD_CLIENT_ID","BLIZZARD_CLIENT_SECRET",
             "WCL_CLIENT_ID","WCL_CLIENT_SECRET")),
             "V319_SOURCE_CREDENTIALS_REQUIRED")
        root=output_root/"fresh_user_workspace"
        root.mkdir()
        env=web.LocalJobs(root).build_season_environment(
            game_build=fresh.BUILD,
            target_ilevel=case["target_ilevel"],
            auto_initial_core_build=True,
            auto_initial_core_simc_binary=str(binary),
            simc_revision_hint=fresh.REVISION,
            existing_special_gem_id=None,
            source_target_socket_count=case["sockets"])
        source=env.get("source_compilation") or {}
        installed=source.get("verified_environment_install") or {}
        layout=source.get("physical_gem_layout_unadmitted") or {}
        doc["environment_native_calls"]=env.get("native_calls")
        doc["environment_budget"]={k:env.get(k)
                                   for k in ("G","J","F","O","B","T")}
        doc["environment_manifest_sha256"]=installed.get("manifest_sha256")
        doc["auto_final_T"]=verified_automatic_T(env,controls)
        save(doc)
        need(env.get("environment_ready") is True
             and env.get("environment_installed") is True
             and installed.get("status")==
               "FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY"
             and type(doc["environment_native_calls"]) is int
             and 0<=doc["environment_native_calls"]<=3
             and layout.get("special_gem_id") is None
             and layout.get("socket_total")==4
             and len(set(layout.get("ordinary_gem_ids") or []))==4
             and env["B"]==env["G"]+env["J"]+env["F"]
             and env["T"]==env["B"] and sum(env["O"].values())==0,
             "V319_NEW_SPEC_GJFO_OR_GEMS_NOT_VERIFIED")
        with web_probe.verified_current_catalog(
                source["source_catalog_path"],fresh.BUILD):
            app=web.create_app(root=root,token="v319-new-spec-only")
            app.state.jobs.remember_verified_fresh_environment(env)
            payload={
                "controls":controls, "binary":str(binary),
                "revision":fresh.REVISION,
                "current_season_product":True,
                "max_native_calls":MAX_NATIVE_PER_ARM,
                "max_new_native_this_invocation":min(
                    MAX_NATIVE_PER_ARM,WEB_PREPARE_BATCH_LIMIT),
                "max_elapsed_seconds":1200}
            with TestClient(app,base_url="http://127.0.0.1:8765") as client:
                headers={"x-simc-local-token":"v319-new-spec-only",
                         "origin":"http://127.0.0.1:8765"}
                response=client.post("/api/v1/longrun/prepare",
                                     headers=headers,json=payload)
                if response.status_code!=200:
                    raise V319Blocked(
                        "V319_NEW_SPEC_WEB_PREPARE_"+str(response.status_code)
                        +"_"+str(response.json().get("detail","NO_DETAIL"))[:180])
                prepared=response.json()
                need(prepared.get("status")==
                     "LONGRUN_SOURCE_PREPARED_NO_DPS_NATIVE",
                     "V319_USER_SOURCE_ONLY_BEFORE_SIMC")
                session=root/prepared["session_id"]
                confirmation=client.get(
                    f"/api/v1/sessions/{prepared['session_id']}/inputs",
                    headers=headers)
                need(confirmation.status_code==200
                     and confirmation.json()["user"]["target"]["final_T"]
                        is None
                     and confirmation.json()["user"]["character"]["class"]==expected_spec[0]
                     and confirmation.json()["user"]["character"]["spec"]==expected_spec[1],
                     "V319_PRODUCT_USER_INPUT_LOST")
                manifest=longrun.source_manifest(session)
                original=longrun.entry.source(manifest)
                staged,_=durable.stage_extended_manifest(
                    original,manifest,MAX_NATIVE_PER_ARM,
                    source_loader=longrun.entry.source,
                    research_scout_floor=research_scout_floor)
                context,flask=staged["context"],staged["flask"]
                identity=context["identity"]
                need(identity["approved_final_T"]==doc["auto_final_T"]
                     and identity["base_B"]==env["B"]
                     and identity["scout_iterations"]==(research_scout_floor or ITER_SCOUT)
                     and identity["confirm_iterations"]==ITER_CONFIRM
                     and identity["binary_sha256"]==fresh.BINARY_SHA
                     and identity["revision"]==fresh.REVISION
                     and sum(flask.values())==env["F"]
                     and sum(identity["oil_vector"].values())==0,
                     "V319_NEW_USER_CONTEXT_BUDGET_OR_EXACT_IDENTITY")
                profile=context["bundle"]["oil"]["profile"]
                need(re.search(r"(?m)^"+re.escape(expected_spec[0])+r"=",profile) is not None
                     and re.search(r"(?m)^spec="+re.escape(expected_spec[1])+r"$",profile) is not None,
                     "V319_NEW_SPEC_SIMC_PROFILE_NOT_ACTUALLY_CREATED")
                doc["verified_auto_T_matches_v291_profile"]=True
                doc["source_profile_sha256"]=identity["source_profile_sha256"]
                doc["source_profile_raw_sha256"]=hashlib.sha256(
                    profile.encode("utf8")).hexdigest()
                doc["source_scenario_digest"]=identity["scenario_digest"]
                doc["flask_F"]=flask
                doc["fresh_profile_generated_once_for_both_arms"]=True
                save(doc)
                # New independent research campaigns can use the actual
                # fresh product context directly, without repeating an
                # irrelevant v290/v318 comparator pair.
                if source_only_context_hook is not None:
                    need(callable(source_only_context_hook)
                         and post_run_hook is None
                         and post_run_context_hook is None,
                         "EXCLUSIVE_FRESH_SOURCE_ONLY_HOOK")
                    doc["status"]="FRESH_PRODUCT_SOURCE_READY_NO_DPS_NATIVE"
                    save(doc)
                    doc["new_native_policy_ab"]=source_only_context_hook(
                        doc,binary,output_root,context,flask)
                    doc["status"]="FRESH_SOURCE_RESEARCH_CAMPAIGN_COMPLETE"
                    save(doc)
                    return doc
                for name,flag in (
                        ("v290_original",False),("v318_idea001",True)):
                    output=output_root/name
                    start=time.monotonic()
                    result=durable.run(
                        context,flask,binary,output,
                        max_native_calls=MAX_NATIVE_PER_ARM,
                        max_new_native_this_invocation=MAX_NATIVE_PER_ARM,
                        max_elapsed_seconds=1200,cache_only=False,
                        case_timing_trace=True,
                        sem_precision_priority_optin=flag,open_folder=False)
                    elapsed=round(time.monotonic()-start,6)
                    rows=durable._load_journal(
                        output/"V291_JOURNAL.jsonl")
                    confirmed=[r for r in rows
                               if r["phase"]=="precision"
                               and r["iterations"]==ITER_CONFIRM]
                    selected=sorted(confirmed,key=lambda r:(
                        -r["dps_mean"],r["case_key"]))
                    need(result["policy"]==EXPECTED_POLICIES[name]
                         and len(rows)==MAX_NATIVE_PER_ARM
                         and result["new_native_this_invocation"]==
                             MAX_NATIVE_PER_ARM
                         and all(r["source"]=="NEW_NATIVE" for r in rows)
                         and confirmed,
                         "V319_NATIVE_ARM_NOT_COMPLETE_OR_NO_CONFIRMATION")
                    tdata=trace.load(
                        output/trace.NAME,rows,
                        trace.identity_hash(output/"V291_SESSION.json"))
                    cks=trace.checkpoints(tdata,rows,ITER_CONFIRM)
                    replay=durable.run(
                        context,flask,binary,output,
                        max_native_calls=MAX_NATIVE_PER_ARM,
                        max_new_native_this_invocation=0,
                        cache_only=True,case_timing_trace=True,
                        sem_precision_priority_optin=flag,open_folder=False)
                    need(replay["new_native_this_invocation"]==0,
                         "V319_IDENTICAL_SESSION_CACHE_ONLY_REPLAY_NEEDS_NATIVE")
                    best=selected[0]
                    arm={
                        "policy":result["policy"],"status":result["status"],
                        "native_calls":len(rows),
                        "actual_total_simc_iterations":sum(
                            r["iterations"] for r in rows),
                        "scouts":len(rows)-len(confirmed),
                        "precision_320":len(confirmed),
                        "measured_elapsed_seconds":elapsed,
                        "same_source_profile_sha256":identity["source_profile_sha256"],
                        "best_confirmed_320":{
                            "CHMV":best["target"],
                            "dps":best["dps_mean"],"SEM":best["dps_sem"],
                            "seed":best.get("simc_seed"),
                            "native_json_sha256":best["native_sha256"],
                            "case_key":best["case_key"]},
                        "selected_pair_nominal_95":result.get(
                            "confirmed_selected_pair_95"),
                        "v316_time_checkpoints":cks,
                        "journal_sha256":sha(output/"V291_JOURNAL.jsonl"),
                        "session_seal_sha256":sha(output/"V291_SESSION.json"),
                        "timing_sha256":sha(output/trace.NAME),
                        "cache_only_new_native":0,
                    }
                    # Retain exact 35/320 original inputs, Native JSON2,
                    # journal, session seal and timing, not just rounded DPS.
                    archive=output_root/(name+"_original_native.zip")
                    with zipfile.ZipFile(
                            archive,"w",compression=zipfile.ZIP_DEFLATED,
                            compresslevel=5) as z:
                        for path in sorted(output.rglob("*")):
                            if path.is_file() and not path.is_symlink():
                                z.write(path,arcname=path.relative_to(output))
                    arm["original_native_archive_sha256"]=sha(archive)
                    doc["arms"][name]=arm
                    save(doc)
                    print("P2_V319_FRESH_NEW_SPEC_ARM_REAL",json.dumps({
                        "arm":name,"source_profile_sha256":
                            identity["source_profile_sha256"],
                        "native_calls":len(rows),
                        "total_iterations":arm["actual_total_simc_iterations"],
                        "precision_320":len(confirmed),
                        "elapsed_seconds":elapsed,
                        "best_confirmed_320":arm["best_confirmed_320"],
                    },sort_keys=True),flush=True)
                a,b=doc["arms"]["v290_original"],doc["arms"]["v318_idea001"]
                need(a["same_source_profile_sha256"]==
                     b["same_source_profile_sha256"]==
                     identity["source_profile_sha256"]
                     and a["native_calls"]==b["native_calls"]==
                     MAX_NATIVE_PER_ARM,
                     "V319_NOT_SAME_NEW_PROFILE_OR_NATIVE_COUNT")
                best_a,best_b=a["best_confirmed_320"],b["best_confirmed_320"]
                gap=best_b["dps"]-best_a["dps"]
                half=1.959963984540054*math.hypot(
                    best_a["SEM"],best_b["SEM"])
                distinct=(best_a["seed"] is not None
                          and best_b["seed"] is not None
                          and best_a["seed"]!=best_b["seed"])
                equal_iterations=(a["actual_total_simc_iterations"]==
                                  b["actual_total_simc_iterations"])
                doc["pairwise"]={
                    "same_fresh_user_profile":True,
                    "equal_native_calls":True,
                    "equal_simc_iterations":equal_iterations,
                    "equal_wall_clock":False,
                    "different_wall_seconds":
                        round(b["measured_elapsed_seconds"]-
                              a["measured_elapsed_seconds"],6),
                    "v318_minus_v290_confirmed_dps":round(gap,6),
                    "nominal_95_halfwidth":round(half,6),
                    "nominal_95_different_seeds":distinct,
                    "selected_pair_nominal_95_separated":
                        bool(distinct and abs(gap)>half),
                    "winner_selection_bias_corrected":False,
                    "familywise_95_proven":False,
                    "global_optimum_proven":False,
                    "performance_win_proven":False,
                    "equal_budget_eligible_for_comparison":equal_iterations,
                }
                doc["status"]=(
                    "COMPLETE_TWO_ARMS_EQUAL_CALLS_AND_ITERATIONS"
                    if equal_iterations else
                    "COMPLETE_TWO_ARMS_EQUAL_CALLS_ITERATIONS_UNEQUAL")
                save(doc)
                print("P2_V319_REAL_FRESH_WINDWALKER_AB",json.dumps({
                    "status":doc["status"],
                    "same_new_source_sha256":identity["source_profile_sha256"],
                    "A":a["best_confirmed_320"],
                    "B":b["best_confirmed_320"],
                    "pairwise":doc["pairwise"],
                    "environment_native":doc["environment_native_calls"],
                },sort_keys=True),flush=True)
                if post_run_hook is not None:
                    need(callable(post_run_hook),"V320_POST_RUN_HOOK_REQUIRED")
                    doc["new_native_research_tier_120"]=post_run_hook(doc,binary,output_root)
                    save(doc)
                if post_run_context_hook is not None:
                    need(callable(post_run_context_hook),
                         "V329_CONTEXT_HOOK_MUST_BE_EXPLICIT")
                    doc["new_native_policy_ab"]=post_run_context_hook(
                        doc,binary,output_root,context,flask)
                    save(doc)
                return doc
    except BaseException as exc:
        doc["status"]="BLOCKED_OR_PARTIAL_"+type(exc).__name__
        x=str(exc)
        doc["first_error_code"]=(x if re.fullmatch(
            r"[A-Z][A-Z0-9_]{3,160}",x) else type(exc).__name__)
        save(doc)
        raise

if __name__=="__main__":
    main()
