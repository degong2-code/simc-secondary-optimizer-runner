#!/usr/bin/env python3
"""ONE 21-grid 25% coverage milestone with 11-grid historical SHA anchor.

Prior 2800 raw JSON2/inputs/receipts verified from GitHub artifacts; only
2,169 NEW level-21 scout vectors and 16 NEW confirmed vectors are executed.
New v291 session has one fixed 17,076-call lifetime cap, allowing follow-on
milestones without altering its source/SHA. This one shot invokes <=2,185.
The previous original11 run is REFERENCE evidence, not new v291 case cache.
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
from runner import v309_prior_anchored_level21_progressive as progressive
from integration_probes import p2_new_profile_product_e2e_once as fresh
from integration_probes import p3_haj_real_local_web_native_e2e as web_probe

SCHEMA="p2_v309_new21_25pct_historical11_verified_v1"
ROOT=pathlib.Path("out/p2_v309_21_progressive_once").resolve()
REPORT=ROOT/"receipt.json"
CAP=17076
FIRST=2185
RAW_SHA="faefc35a52607bd947ec4ca93dcd86806e2012849f116d768c0dea1ff0069b40"
OLD_RAW=pathlib.Path("out/v309_origin11_raw/full_original_v291_cases.zip").resolve()
OLD_COMPACT_DIR=pathlib.Path("out/v309_origin11_compact").resolve()
OLD_COMPACT=ROOT/"origin11_compact_bundle.zip"


class StudyBlocked(RuntimeError):
    pass


def need(ok,code):
    if not ok:
        raise StudyBlocked(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(doc):
    path=REPORT.with_suffix(".tmp")
    path.write_text(json.dumps(doc,sort_keys=True,indent=2,
                         ensure_ascii=False,allow_nan=False)+"\n",encoding="utf8")
    path.replace(REPORT)


def ensure_prior_compact():
    need(OLD_RAW.is_file() and
         all((OLD_COMPACT_DIR/n).is_file()
             for n in ("receipt.json","all_accepted_compact_cases.jsonl")),
         "V309_REQUIRED_ORIGINAL_2800_NATIVE_ARTIFACTS_NOT_DOWNLOADED")
    need(not OLD_COMPACT.exists(),"V309_ORIGIN_COMPACT_BUNDLE_NOT_FRESH")
    with zipfile.ZipFile(OLD_COMPACT,"x",zipfile.ZIP_DEFLATED,
                         compresslevel=4) as writer:
        for name in ("receipt.json","all_accepted_compact_cases.jsonl"):
            writer.write(OLD_COMPACT_DIR/name,name)


def main():
    need(os.getenv("P2_V309_NEW21_25_REAL_ONCE")=="1",
         "V309_EXPLICIT_25_PERCENT_REAL_NATIVE_REQUIRED")
    case,controls=fresh.selected_case("destruction_warlock_4ordinary_T3400")
    need((case["character_class"],case["character_spec"],
          case["character_race"],case["target_ilevel"],
          case["final_T"],case["sockets"],case["special_gem"])==
         ("warlock","destruction","human",334,3400,4,None),
         "V309_NEW_USER_WARLOCK_CASE_DRIFT")
    binary=pathlib.Path("out/binary/simc").resolve(strict=True)
    need(sha(binary.read_bytes())==fresh.BINARY_SHA,
         "V309_ORIGINAL_APPROVED_BINARY_SHA_DRIFT")
    ROOT.mkdir(parents=True,exist_ok=True)
    need(not REPORT.exists(),"V309_ONE_SHOT_ALREADY_STARTED")
    doc={
        "schema":SCHEMA,"status":"STARTED",
        "new_profile":case,
        "new_environment_native":0,
        "new_dps_native":0,
        "old_original_raw_checkpoint_expected_sha256":RAW_SHA,
        "old_original11_cases_prior_verified":False,
        "old_native_reexecuted":False,
        "old_original11_exact_cache_imported_into_new_session":False,
        "first_milestone_percent":25,
        "future_milestones_not_yet_executed":True,
        "familywise_95_proven":False,
        "global_optimum_proven":False,
        "main_or_default_policy_changed":False,
        "native_binary_sha256":fresh.BINARY_SHA,
        "game_build":fresh.BUILD,
        "revision":fresh.REVISION}
    save(doc)
    try:
        ensure_prior_compact()
        prior=progressive.load_original_prior(OLD_COMPACT,OLD_RAW,RAW_SHA)
        need(prior["prior_level11_count"]==2784 and
             prior["B"]==3400 and
             prior["source_profile_sha256"]==
               "e193aacef751b81dcdb8b06abbedf7aa458c0ae46eeb23898b501cf3314d7f8c"
             and prior["binary_sha256"]==fresh.BINARY_SHA and
             prior["revision"]==fresh.REVISION and
             prior["season_build"]==fresh.BUILD,
             "V309_ORIGINAL11_EXACT_PROFILE_REVISION_OR_BUDGET_DRIFT")
        geo=progressive.geometry(prior["B"],prior["lower"],prior["upper"])
        need(geo["size_old"]==2784 and geo["size_fine"]==19812
             and geo["new_counts"]==(2169,7122,17028)
             and geo["total_calls"]==CAP
             and geo["milestone_calls"][0]==FIRST,
             "V309_EXACT_25_PERCENT_21_GRID_MILESTONE_DRIFT")
        doc.update(
            prior_verified_raw_archive_sha256=prior["raw_archive_sha256"],
            prior_compact_journal_sha256=prior[
                "original_compact_journal_sha256"],
            old_original11_cases_prior_verified=True,
            prior_source_profile_sha256=prior["source_profile_sha256"],
            prior_source_scenario_digest=prior["original_scenario_digest"],
            prior_verified_scout_targets=prior["prior_level11_count"],
            origin_best_320_mean=prior["confirmed_baseline"][0]["dps_mean"],
            origin_best_320_sem=prior["confirmed_baseline"][0]["dps_sem"],
            sealed_total_new_session_calls=CAP,
            max_new_native_this_invocation=FIRST,
            target_level21_milestone_25=geo["milestone_targets"][0])
        save(doc)
        live=retail.discover(region="KR")
        need(live["game_build"]==fresh.BUILD,
             "V309_RETAIL_LIVE_BUILD_DRIFT")
        need(all(os.getenv(k) for k in
                 ("BLIZZARD_CLIENT_ID","BLIZZARD_CLIENT_SECRET",
                  "WCL_CLIENT_ID","WCL_CLIENT_SECRET")),
             "V309_SEASON_SOURCE_SECRETS_REQUIRED")
        root=ROOT/"product_workspace"
        need(not root.exists(),"V309_PRODUCT_WORKSPACE_MUST_BE_NEW")
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
        doc["new_environment_native"]=env.get("native_calls",0)
        need(env.get("environment_ready") is True and
             env.get("environment_installed") is True and
             installed.get("status")==
               "FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY" and
             type(doc["new_environment_native"]) is int and
             0<=doc["new_environment_native"]<=3 and
             layout.get("socket_total")==4 and
             layout.get("special_gem_id") is None and
             len(layout.get("ordinary_gem_ids") or [])==4 and
             len(set(layout["ordinary_gem_ids"]))==4 and
             env["B"]==env["G"]+env["J"]+env["F"] and
             env["T"]==env["B"] and sum(env["O"].values())==0,
             "V309_FRESH_ENVIRONMENT_GJFO_OR_ORDINARY_GEM_DRIFT")
        doc["new_environment_budget"]={k:env.get(k)
                                        for k in ("G","J","F","O","B","T")}
        doc["installed_manifest_sha256"]=installed["manifest_sha256"]
        save(doc)
        with web_probe.verified_current_catalog(
                comp["source_catalog_path"],fresh.BUILD):
            app=web.create_app(root=root,token="v309-experimental-local")
            app.state.jobs.remember_verified_fresh_environment(env)
            controls["oil_hands"]=[]
            payload={
                "controls":controls,"binary":str(binary),
                "revision":fresh.REVISION,"current_season_product":True,
                "max_native_calls":12,
                "max_new_native_this_invocation":1,
                "max_elapsed_seconds":360}
            with TestClient(app,base_url="http://127.0.0.1:8765") as client:
                headers={"x-simc-local-token":"v309-experimental-local",
                         "origin":"http://127.0.0.1:8765"}
                resp=client.post("/api/v1/longrun/prepare",
                                 headers=headers,json=payload)
                if resp.status_code!=200:
                    try:
                        err=resp.json().get("detail",{})
                        err=err.get("code") if type(err) is dict else str(err)
                    except (ValueError,TypeError):
                        err="UNREADABLE_DETAIL"
                    raise StudyBlocked("V309_PRODUCT_PREPARE_HTTP_%d_%s"%(
                        resp.status_code,str(err)[:90]))
                prepared=resp.json()
                need(prepared["status"]==
                     "LONGRUN_SOURCE_PREPARED_NO_DPS_NATIVE",
                     "V309_PREPARE_MUST_RUN_ZERO_DPS_NATIVE")
                inputs=client.get("/api/v1/sessions/%s/inputs"%
                    prepared["session_id"],headers=headers)
                need(inputs.status_code==200 and
                     inputs.json()["user"]["target"]["final_T"]==3400,
                     "V309_ACTUAL_WEB_USER_MANUAL_T_CHANGED")
                origin=root/prepared["session_id"]
                source_manifest=longrun.source_manifest(origin)
                baseline=longrun.entry.source(source_manifest)
                staged,_=durable.stage_extended_manifest(
                    baseline,source_manifest,CAP,
                    source_loader=longrun.entry.source)
                ctx,flask=staged["context"],staged["flask"]
                ident=ctx["identity"]
                scenario=ctx["bundle"]["prepared"]["scenario"]
                B,lo,hi=durable.constraints.bounds(
                    scenario,durable.adaptive.feasible_budget(ctx,flask))
                need(B==3400 and tuple(lo)==tuple(prior["lower"])
                     and tuple(hi)==tuple(prior["upper"])
                     and ident["source_profile_sha256"]==
                           prior["source_profile_sha256"]
                     and ident["approved_final_T"]==3400
                     and ident["binary_sha256"]==prior["binary_sha256"]
                     and ident["revision"]==prior["revision"]
                     and ident["scout_iterations"]==35
                     and ident["confirm_iterations"]==320
                     and sum(ident["oil_vector"].values())==0,
                     "V309_NEW_USER_PROFILE_BOUNDS_COMBAT_OR_SOURCE_DRIFT")
                doc.update(
                    new_source_profile_sha256=ident["source_profile_sha256"],
                    new_source_scenario_digest=ident["scenario_digest"],
                    old_and_new_scenario_runtime_seals_differ=(
                        ident["scenario_digest"]!=
                        prior["original_scenario_digest"]),
                    stage_output_dir=str(staged["paths"]["output_dir"]),
                    scenario_annual_source_pinned=True)
                need(doc["old_and_new_scenario_runtime_seals_differ"],
                     "V309_NEW_SESSION_RUNTIME_IDENTITY_NOT_SEPARATE")
                save(doc)
                t0=time.perf_counter()
                report=durable.run(
                    ctx,flask,binary,staged["paths"]["output_dir"],
                    max_native_calls=CAP,
                    max_new_native_this_invocation=FIRST,
                    max_elapsed_seconds=1180,
                    v309_prior_compact_artifact_zip=str(OLD_COMPACT),
                    v309_prior_raw_checkpoint_zip=str(OLD_RAW),
                    v309_prior_raw_checkpoint_sha256=RAW_SHA,
                    open_folder=False)
                doc.update(
                    native_runner_status=report["status"],
                    new_dps_native=report["new_native_this_invocation"],
                    new_native_elapsed_seconds=round(
                        time.perf_counter()-t0,3),
                    milestone_coverage=report[
                        "progressive_level21_coverage"])
                journal=staged["paths"]["output_dir"]/"V291_JOURNAL.jsonl"
                rows=durable._load_journal(journal)
                doc["new_compact_journal_sha256"]=sha(
                    journal.read_bytes())
                doc["new_compact_journal_rows"]=len(rows)
                need(report["status"]=="PAUSED_INVOCATION_NATIVE_BUDGET"
                     and report["completed_cases"]==FIRST
                     and report["new_native_this_invocation"]==FIRST
                     and doc["milestone_coverage"][
                         "combined_observed_geometric_coverage"]==4953
                     and doc["milestone_coverage"][
                         "new_confirmation_vectors"]==16,
                     "V309_FIRST_25_PERCENT_NATIVE_MILESTONE_INCOMPLETE")
                prior_confirmed=prior["confirmed_baseline"]
                new_confirmed=sorted(
                    [r for r in rows if r["phase"]=="precision"],
                    key=lambda r:(-r["dps_mean"],r["case_key"]))
                need(len(new_confirmed)==16,
                     "V309_FIRST_25_PERCENT_CONFIRM_COUNT")
                doc["new_top_confirmed"]=[{
                    "target":r["target"],"dps_mean":r["dps_mean"],
                    "dps_sem":r["dps_sem"],"iterations":r["iterations"],
                    "native_sha256":r["native_sha256"],
                    "case_key":r["case_key"]}
                    for r in new_confirmed[:3]]
                doc["prior_11_best_confirmed"]=prior_confirmed[0]
                delta=(new_confirmed[0]["dps_mean"]-
                       prior_confirmed[0]["dps_mean"])
                halfwidth=1.96*math.hypot(
                    new_confirmed[0]["dps_sem"],
                    prior_confirmed[0]["dps_sem"])
                doc["new25_minus_old11_selected_dps"]=delta
                doc["nominal_95_selected_two_halfwidth"]=halfwidth
                doc["nominal_selected_pair_separated"]=abs(delta)>halfwidth
                doc["multiple_selection_95_superiority_proven"]=False
                # Re-auth every newly accepted v291 original input/JSON2
                # before declaring this 25% milestone as durable evidence.
                replay=durable.run(
                    ctx,flask,binary,staged["paths"]["output_dir"],
                    max_native_calls=CAP,
                    max_new_native_this_invocation=0,cache_only=True,
                    v309_prior_compact_artifact_zip=str(OLD_COMPACT),
                    v309_prior_raw_checkpoint_zip=str(OLD_RAW),
                    v309_prior_raw_checkpoint_sha256=RAW_SHA,
                    open_folder=False)
                need(replay["new_native_this_invocation"]==0
                     and replay["completed_cases"]==FIRST
                     and replay["progressive_level21_coverage"]==
                         report["progressive_level21_coverage"],
                     "V309_FIRST_MILESTONE_ORIGINAL_NATIVE_REPLAY_FAILED")
                doc["cache_only_replay_new_native"]=0
                doc["status"]="PASS_REAL_21_GRID_25_PERCENT_OLD11_ANCHORED"
                save(doc)
                print("V309_21_GRID_25_PERCENT_REAL_PASS",json.dumps({
                    k:doc[k] for k in (
                    "status","new_environment_native","new_dps_native",
                    "new_native_elapsed_seconds","milestone_coverage",
                    "new_top_confirmed","prior_11_best_confirmed",
                    "new25_minus_old11_selected_dps",
                    "nominal_95_selected_two_halfwidth")},
                    sort_keys=True,ensure_ascii=False),flush=True)
        return doc
    except BaseException as exc:
        doc["status"]="BLOCKED_OR_PARTIAL_"+type(exc).__name__
        msg=str(exc)
        doc["first_error_code"]=msg if re.fullmatch(
            r"[A-Z][A-Z0-9_]{3,110}",msg) else type(exc).__name__
        save(doc)
        raise


if __name__=="__main__":
    main()
