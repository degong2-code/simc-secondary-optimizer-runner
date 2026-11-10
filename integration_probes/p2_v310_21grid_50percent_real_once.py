#!/usr/bin/env python3
"""ONE source-backed Warlock 21-grid exact 50% experiment; NEW 4953 +16.

Preflight two ORIGINAL raw Native ZIPs with independent v308 SHA and exact
journal evidence: original level11 and first25 21-grid. Never import either
as exact current-session cache; execute ONLY unseen 25->50 new vectors.
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
from runner import v310_external_frontier_50_only as frontier
from integration_probes import p2_new_profile_product_e2e_once as fresh
from integration_probes import p3_haj_real_local_web_native_e2e as web_probe

SCHEMA="p2_v310_new21_50pct_double_historical_raw_v1"
ROOT=pathlib.Path("out/p2_v310_new21_50_once").resolve()
REPORT=ROOT/"receipt.json"
PROOF_MANIFEST=ROOT/"frontier_sources.json"
ORIG11_COMPACT=pathlib.Path("out/v310_old11_compact").resolve()
ORIG11_RAW=pathlib.Path("out/v310_old11_raw/full_original_v291_cases.zip").resolve()
ORIG25_COMPACT=pathlib.Path("out/v310_old25_compact").resolve()
ORIG25_RAW=pathlib.Path("out/v310_old25_raw/new21_original_exact_native_checkpoint.zip").resolve()
ORIG11_ZIP=ROOT/"original11_compact.zip"
RAW11_SHA="faefc35a52607bd947ec4ca93dcd86806e2012849f116d768c0dea1ff0069b40"
RAW25_SHA="e7a0f59c2a183f8eca8229dfa27f80958f02a3b847982fa4fc4fe2a07bbfdccc"
MAX_DPS_NATIVE=4969
MAX_ELAPSED=1650


class StudyBlocked(RuntimeError):
    pass


def need(ok,code):
    if not ok:
        raise StudyBlocked(code)


def save(data):
    temp=REPORT.with_suffix(".tmp")
    temp.write_text(json.dumps(data,sort_keys=True,indent=2,
                              ensure_ascii=False,allow_nan=False)+"\n")
    temp.replace(REPORT)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def initialize_frontier():
    need(ORIG11_RAW.is_file() and ORIG25_RAW.is_file()
         and all((ORIG11_COMPACT/name).is_file()
                 for name in ("receipt.json","all_accepted_compact_cases.jsonl"))
         and (ORIG25_COMPACT/"receipt.json").is_file(),
         "V310_GITHUB_11_AND_25_ORIGINAL_SOURCE_ARTIFACTS_REQUIRED")
    journals=list(ORIG25_COMPACT.glob("**/V291_JOURNAL.jsonl"))
    need(len(journals)==1 and journals[0].is_file(),
         "V310_ORIGINAL25_SINGLE_ACCEPTED_COMPACT_JOURNAL")
    need(not ORIG11_ZIP.exists(),"V310_COMPACT_BUNDLE_MUST_BE_NEW")
    with zipfile.ZipFile(ORIG11_ZIP,"x",zipfile.ZIP_DEFLATED) as z:
        for name in ("receipt.json","all_accepted_compact_cases.jsonl"):
            z.write(ORIG11_COMPACT/name,name)
    doc={"schema":frontier.COMPACT_SCHEMA,
         "original11_compact_zip":str(ORIG11_ZIP),
         "original11_raw_zip":str(ORIG11_RAW),
         "original11_sha256":RAW11_SHA,
         "prior25_receipt":str(ORIG25_COMPACT/"receipt.json"),
         "prior25_compact_journal":str(journals[0]),
         "prior25_raw_zip":str(ORIG25_RAW),
         "prior25_sha256":RAW25_SHA}
    PROOF_MANIFEST.write_text(json.dumps(doc,sort_keys=True,indent=2)+"\n")


def main():
    need(os.environ.get("P2_V310_50_REAL_ONCE")=="1",
         "V310_EXPLICIT_NEW21_50_SIMC_NATIVE_REQUIRED")
    case,controls=fresh.selected_case("destruction_warlock_4ordinary_T3400")
    need((case["character_class"],case["character_spec"],
          case["character_race"],case["target_ilevel"],
          case["final_T"],case["sockets"],case["special_gem"])==
         ("warlock","destruction","human",334,3400,4,None),
         "V310_DIFFERENT_USER_INPUT_DRIFT")
    binary=pathlib.Path("out/binary/simc").resolve(strict=True)
    need(sha(binary.read_bytes())==fresh.BINARY_SHA,
         "V310_APPROVED_SIMC_BINARY_SHA_CHANGED")
    ROOT.mkdir(parents=True,exist_ok=True)
    need(not REPORT.exists(),"V310_ALREADY_EXECUTED_ONE_SHOT")
    result={
        "schema":SCHEMA,"status":"STARTED",
        "old11_raw_sha256":RAW11_SHA,"old25_raw_sha256":RAW25_SHA,
        "existing_historical_cases_imported_as_exact_native_cache":False,
        "new_environment_native":0,"new_dps_native":0,
        "new_simc_binary_sha256":fresh.BINARY_SHA,
        "source_build":fresh.BUILD,
        "same_warlock_character_equipment_options":True,
        "session_v291_out_of_old11_or_old25_identity":True,
        "familywise_95_proven":False,"global_optimum_proven":False,
        "legacy_v290_product_default_unchanged":True}
    save(result)
    try:
        initialize_frontier()
        prior=frontier.load_frontier(PROOF_MANIFEST)
        geo=frontier.geometry(prior["B"],prior["lower"],prior["upper"])
        need(prior["source_profile_sha256"]==
               "e193aacef751b81dcdb8b06abbedf7aa458c0ae46eeb23898b501cf3314d7f8c"
             and prior["revision"]==fresh.REVISION
             and prior["binary_sha256"]==fresh.BINARY_SHA
             and prior["season_build"]==fresh.BUILD
             and prior["B"]==3400
             and geo["native_cap"]==MAX_DPS_NATIVE
             and geo["new_50_count"]==4953
             and geo["combined_50"]==9906
             and geo["level21_total"]==19812,
             "V310_50_PERCENT_ORIGINAL_FULL_FRONTIER_DRIFT")
        result["both_original_raw_cohorts_sha_verified"]=True
        result["prior_historical_scouts"]=prior["prior_total_scouts"]
        result["planned_new21_scouts"]=geo["new_50_count"]
        result["planned_new21_confirmations"]=16
        result["previous_confirmed_best"]=prior["old_best_confirmed"]
        save(result)
        live=retail.discover(region="KR")
        need(live["game_build"]==fresh.BUILD,
             "V310_RETAIL_BUILD_DIFFERS_FROM_PINNED_SOURCE")
        need(all(os.getenv(k) for k in (
             "BLIZZARD_CLIENT_ID","BLIZZARD_CLIENT_SECRET",
             "WCL_CLIENT_ID","WCL_CLIENT_SECRET")),
             "V310_SEASON_SOURCE_CREDENTIALS_MISSING")
        root=ROOT/"product_workspace"
        need(not root.exists(),"V310_FRESH_PRODUCT_WORKSPACE_REQUIRED")
        root.mkdir()
        env=web.LocalJobs(root).build_season_environment(
            game_build=fresh.BUILD,target_ilevel=case["target_ilevel"],
            auto_initial_core_build=True,
            auto_initial_core_simc_binary=str(binary),
            simc_revision_hint=fresh.REVISION,
            existing_special_gem_id=None,
            source_target_socket_count=case["sockets"])
        comp=env.get("source_compilation") or {}
        layout=comp.get("physical_gem_layout_unadmitted") or {}
        installed=comp.get("verified_environment_install") or {}
        result["new_environment_native"]=env.get("native_calls",0)
        result["environment_budget"]={k:env.get(k)
                                       for k in ("G","J","F","O","B","T")}
        need(env.get("environment_ready") is True and
             env.get("environment_installed") is True and
             installed.get("status")==
              "FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY" and
             type(result["new_environment_native"]) is int and
             0<=result["new_environment_native"]<=3
             and layout.get("socket_total")==4 and
             layout.get("special_gem_id") is None and
             len(set(layout.get("ordinary_gem_ids") or []))==4
             and env["B"]==env["G"]+env["J"]+env["F"]
             and env["T"]==env["B"] and sum(env["O"].values())==0,
             "V310_NEW_SEASON_GJFO_GEM_ENVIRONMENT_NOT_ADMITTED")
        save(result)
        with web_probe.verified_current_catalog(
                comp["source_catalog_path"],fresh.BUILD):
            app=web.create_app(root=root,token="v310-local-once")
            app.state.jobs.remember_verified_fresh_environment(env)
            controls["oil_hands"]=[]
            payload={"controls":controls,"binary":str(binary),
                     "revision":fresh.REVISION,
                     "current_season_product":True,
                     "max_native_calls":12,
                     "max_new_native_this_invocation":1,
                     "max_elapsed_seconds":360}
            with TestClient(app,base_url="http://127.0.0.1:8765") as client:
                headers={"x-simc-local-token":"v310-local-once",
                         "origin":"http://127.0.0.1:8765"}
                resp=client.post("/api/v1/longrun/prepare",
                                 headers=headers,json=payload)
                if resp.status_code!=200:
                    try:
                        err=resp.json().get("detail",{})
                        err=err.get("code") if type(err) is dict else str(err)
                    except (ValueError,TypeError):
                        err="UNKNOWN_DETAIL"
                    raise StudyBlocked("V310_WEB_PREPARE_HTTP_%d_%s"%(
                        resp.status_code,str(err)[:110]))
                prepared=resp.json()
                need(prepared.get("status")==
                     "LONGRUN_SOURCE_PREPARED_NO_DPS_NATIVE",
                     "V310_USER_WEB_PREPARE_NOT_ZERO_DPS")
                user=client.get("/api/v1/sessions/%s/inputs"%
                                prepared["session_id"],headers=headers)
                need(user.status_code==200 and
                     user.json()["user"]["target"]["final_T"]==3400,
                     "V310_WEB_MANUAL_T_NOT_EFFECTIVE")
                source_manifest=longrun.source_manifest(
                    root/prepared["session_id"])
                verified=longrun.entry.source(source_manifest)
                staged,_=durable.stage_extended_manifest(
                    verified,source_manifest,MAX_DPS_NATIVE,
                    source_loader=longrun.entry.source)
                ctx,flask=staged["context"],staged["flask"]
                identity=ctx["identity"]
                scenario=ctx["bundle"]["prepared"]["scenario"]
                budget,lo,hi=durable.constraints.bounds(
                    scenario,durable.adaptive.feasible_budget(ctx,flask))
                need(budget==3400
                     and tuple(lo)==tuple(prior["lower"])
                     and tuple(hi)==tuple(prior["upper"])
                     and identity["source_profile_sha256"]==
                         prior["source_profile_sha256"]
                     and identity["binary_sha256"]==
                         prior["binary_sha256"]
                     and identity["revision"]==prior["revision"]
                     and identity["scout_iterations"]==35
                     and identity["confirm_iterations"]==320
                     and identity["approved_final_T"]==3400
                     and sum(identity["oil_vector"].values())==0,
                     "V310_ORIGINAL_11_25_USER_PROFILE_OR_BOUNDS_DRIFT")
                result.update(
                    new_source_profile_sha256=identity["source_profile_sha256"],
                    new_source_scenario_digest=identity["scenario_digest"],
                    stage_output_dir=str(staged["paths"]["output_dir"]),
                    current_native_calls_cap=MAX_DPS_NATIVE)
                save(result)
                start=time.perf_counter()
                actual=durable.run(
                    ctx,flask,binary,staged["paths"]["output_dir"],
                    max_native_calls=MAX_DPS_NATIVE,
                    max_new_native_this_invocation=MAX_DPS_NATIVE,
                    max_elapsed_seconds=MAX_ELAPSED,
                    v310_frontier_manifest_path=str(PROOF_MANIFEST),
                    open_folder=False)
                result["new_dps_native"]=actual[
                    "new_native_this_invocation"]
                result["native_elapsed_seconds"]=round(
                    time.perf_counter()-start,3)
                result["frontier_coverage"]=actual["frontier50_coverage"]
                result["native_runner_status"]=actual["status"]
                journal=staged["paths"]["output_dir"]/"V291_JOURNAL.jsonl"
                rows=durable._load_journal(journal)
                result["new_compact_journal_sha256"]=sha(journal.read_bytes())
                result["new_compact_journal_rows"]=len(rows)
                need(actual["status"]=="BUDGET_EXHAUSTED" and
                     actual["completed_cases"]==MAX_DPS_NATIVE and
                     actual["new_native_this_invocation"]==MAX_DPS_NATIVE and
                     result["frontier_coverage"]["combined_observed"]==9906
                     and result["frontier_coverage"][
                           "new50_scouts_this_native_session"]==4953
                     and result["frontier_coverage"][
                           "new50_precision_confirmations"]==16,
                     "V310_50_PERCENT_EXACT_MILESTONE_NATIVE_MISSING")
                confirms=sorted([r for r in rows if r["phase"]=="precision"],
                                key=lambda r:(-r["dps_mean"],r["case_key"]))
                need(len(confirms)==16,"V310_NEW50_NATIVE_CONFIRM_COUNT")
                result["new_top_confirmed"]=[{
                    "target":r["target"],"dps_mean":r["dps_mean"],
                    "dps_sem":r["dps_sem"],"iterations":r["iterations"],
                    "native_sha256":r["native_sha256"],
                    "case_key":r["case_key"]}
                    for r in confirms[:3]]
                old=prior["old_best_confirmed"]
                delta=confirms[0]["dps_mean"]-old["dps_mean"]
                halfwidth=1.96*math.hypot(
                    confirms[0]["dps_sem"],old["dps_sem"])
                result["new50_minus_best_prior_11or25_dps"]=delta
                result["nominal95_selected_pair_halfwidth"]=halfwidth
                result["nominal_pair_separation"]=abs(delta)>halfwidth
                result["familywise_95_proven"]=False
                cache=durable.run(
                    ctx,flask,binary,staged["paths"]["output_dir"],
                    max_native_calls=MAX_DPS_NATIVE,
                    max_new_native_this_invocation=0,cache_only=True,
                    v310_frontier_manifest_path=str(PROOF_MANIFEST),
                    open_folder=False)
                need(cache["new_native_this_invocation"]==0 and
                     cache["completed_cases"]==MAX_DPS_NATIVE and
                     cache["frontier50_coverage"]==result["frontier_coverage"],
                     "V310_NEW50_CACHE_ONLY_NATIVE_REVALIDATION_FAILED")
                result["same_job_cache_only_replay_new_native"]=0
                result["status"]="PASS_V310_REAL_21GRID_50PCT_NEW_ONLY"
                save(result)
                print("V310_50_PERCENT_REAL_NATIVE_PASS",json.dumps({
                    k:result[k] for k in ("status","new_environment_native",
                    "new_dps_native","native_elapsed_seconds","frontier_coverage",
                    "new_top_confirmed","previous_confirmed_best",
                    "new50_minus_best_prior_11or25_dps",
                    "nominal95_selected_pair_halfwidth")},
                    sort_keys=True,ensure_ascii=False),flush=True)
        return result
    except BaseException as exc:
        result["status"]="BLOCKED_OR_PARTIAL_"+type(exc).__name__
        msg=str(exc)
        result["first_error_code"]=(msg if re.fullmatch(
            r"[A-Z][A-Z0-9_]{3,110}",msg) else type(exc).__name__)
        save(result)
        raise


if __name__=="__main__":
    main()
