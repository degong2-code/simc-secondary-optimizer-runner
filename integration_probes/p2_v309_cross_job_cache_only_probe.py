#!/usr/bin/env python3
"""v309 cross-job exact-cache reauthentication PROBE: ZERO DPS Native.

The original 2,185 exact JSON2/SimC inputs/receipts and v291 session seal
must be restored to their SAME original absolute path. A new same-build v216
environment must reproduce the v212 installation authority before loading
the old stage manifest. If it cannot, block BEFORE any new DPS Native; do
not silently accept historical compact rows as exact-case current cache.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import zipfile

from runner import v113_local_web_api as web
from runner import v289_retail_live_build_source as retail
from runner import v291_durable_multiscale_native_runner as durable
from runner import v293_local_longrun_session as longrun
from runner import v308_dense_native_checkpoint as checkpoint
from runner import v309_prior_anchored_level21_progressive as progressive
from integration_probes import p2_new_profile_product_e2e_once as fresh

SCHEMA="p2_v309_new21_cross_job_original_cache_probe_v1"
ROOT=pathlib.Path("out/p2_v309_21_progressive_once").resolve()
BASE=ROOT/"product_workspace"
REPORT=ROOT/"cross_job_cache_probe_receipt.json"
NEW_RAW=pathlib.Path("out/v309_25_new_raw/new21_original_exact_native_checkpoint.zip").resolve()
NEW_RAW_SHA="e7a0f59c2a183f8eca8229dfa27f80958f02a3b847982fa4fc4fe2a07bbfdccc"
OLD_RAW=pathlib.Path("out/v309_origin11_raw/full_original_v291_cases.zip").resolve()
OLD_RAW_SHA="faefc35a52607bd947ec4ca93dcd86806e2012849f116d768c0dea1ff0069b40"
OLD_COMPACT_PATH=pathlib.Path("out/v309_origin11_compact").resolve()
OLD_COMPACT=ROOT/"origin11_compact_bundle.zip"


def need(ok,code):
    if not ok:
        raise RuntimeError(code)


def save(doc):
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    tmp=REPORT.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc,sort_keys=True,indent=2,
                              ensure_ascii=False,allow_nan=False)+"\n")
    tmp.replace(REPORT)


def main():
    need(os.getenv("P2_V309_CROSS_JOB_CACHE_PROBE")=="1",
         "V309_CROSS_JOB_EXPLICIT_CACHE_ONLY_PROBE_REQUIRED")
    need(not REPORT.exists(),"V309_CROSS_JOB_PROBE_ONE_SHOT_ONLY")
    case,controls=fresh.selected_case("destruction_warlock_4ordinary_T3400")
    binary=pathlib.Path("out/binary/simc").resolve(strict=True)
    need(hashlib.sha256(binary.read_bytes()).hexdigest()==fresh.BINARY_SHA,
         "V309_CROSS_JOB_APPROVED_NATIVE_BINARY_REQUIRED")
    report={"schema":SCHEMA,"status":"STARTED",
            "new_dps_native":0,
            "original11_dps_reexecuted":False,
            "new25_dps_reexecuted":False,
            "original_cache_only_replay_verified":False,
            "fail_closed_if_install_authority_differs":True,
            "full_v309_cap":17076,
            "previous25_committed_cases":2185}
    save(report)
    try:
        prior_zip=OLD_COMPACT
        prior_zip.parent.mkdir(parents=True,exist_ok=True)
        need(not prior_zip.exists() and
             all((OLD_COMPACT_PATH/name).is_file()
                 for name in ("receipt.json","all_accepted_compact_cases.jsonl")),
             "V309_ORIGINAL11_COMPACT_FOR_REPLAY_REQUIRED")
        with zipfile.ZipFile(prior_zip,"x",zipfile.ZIP_DEFLATED) as z:
            for name in ("receipt.json","all_accepted_compact_cases.jsonl"):
                z.write(OLD_COMPACT_PATH/name,name)
        prior=progressive.load_original_prior(
            prior_zip,OLD_RAW,OLD_RAW_SHA)
        newproof=checkpoint.verify_checkpoint(NEW_RAW,NEW_RAW_SHA)
        report["original11_raw_sha256"]=prior["raw_archive_sha256"]
        report["new25_raw_sha256"]=newproof["archive_sha256"]
        report["new25_raw_case_count"]=newproof["committed_cases"]
        need(newproof["committed_cases"]==2185,
             "V309_NEW25_ORIGINAL_RAW_NATIVE_CASES_MISSING")
        with zipfile.ZipFile(NEW_RAW) as z:
            stored=json.loads(z.read("V291_SESSION.json"))
            manifest=json.loads(z.read("stage/manifest.json"))
            required_manifest=manifest[
                "installed_fresh_season_budget_source"]
            original_stage=pathlib.Path(
                newproof["original_output_path"]).parent
            report["original_stage_path"]=str(original_stage)
            report["original_installed_manifest_sha256"]=(
                required_manifest["installed_manifest_sha256"])
            report["original_installed_manifest_path"]=(
                required_manifest["installed_environment_path"])
            need(stored["context"]["source_profile_sha256"]==
                    prior["source_profile_sha256"] and
                 stored["context"]["binary_sha256"]==fresh.BINARY_SHA and
                 stored["max_native_calls"]==17076 and
                 "experimental_prior_anchored_21" in stored,
                 "V309_NEW25_SEAL_SOURCE_PRIOR_MISMATCH")
        save(report)
        # Regenerate the season installed *authority*, not historical DPS.
        # Same-build static source re-collection is intentionally bounded.
        need(not BASE.exists(),"V309_CROSS_JOB_PRODUCT_ROOT_MUST_BE_EMPTY")
        BASE.mkdir()
        live=retail.discover(region="KR")
        need(live["game_build"]==fresh.BUILD,
             "V309_CROSS_JOB_CURRENT_RETAIL_BUILD_DRIFT")
        need(all(os.getenv(k) for k in (
             "BLIZZARD_CLIENT_ID","BLIZZARD_CLIENT_SECRET",
             "WCL_CLIENT_ID","WCL_CLIENT_SECRET")),
             "V309_CROSS_JOB_SOURCE_CREDENTIALS_REQUIRED")
        env=web.LocalJobs(BASE).build_season_environment(
            game_build=fresh.BUILD,target_ilevel=case["target_ilevel"],
            auto_initial_core_build=True,
            auto_initial_core_simc_binary=str(binary),
            simc_revision_hint=fresh.REVISION,
            existing_special_gem_id=None,
            source_target_socket_count=case["sockets"])
        installed=(env.get("source_compilation") or {}).get(
            "verified_environment_install") or {}
        report["new_environment_native"]=env.get("native_calls",0)
        report["regenerated_installed_manifest_sha256"]=installed.get(
            "manifest_sha256")
        save(report)
        if installed.get("manifest_sha256") != required_manifest[
                "installed_manifest_sha256"]:
            report["status"]="BLOCKED_REGENERATED_SEASON_INSTALL_IDENTITY_DIFFERS"
            report["cross_job_raw_native_usable_as_exact_cache"]=False
            report["next_action"]="USE_SEPARATELY_VERIFIED_HISTORICAL_FRONTIER_NOT_UNAUTHENTICATED_V291_CACHE"
            save(report)
            print("V309_CROSS_JOB_CACHE_NOT_PROVEN",
                  json.dumps({"status":report["status"],
                  "original_install":report["original_installed_manifest_sha256"],
                  "new_install":report["regenerated_installed_manifest_sha256"]},
                             sort_keys=True),flush=True)
            return report
        # Only if the full source install identity matches do we reconstruct
        # the EXACT already-sealed original stage and 2,185 original receipts.
        original_stage.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(NEW_RAW) as z:
            for name in checkpoint.STAGE_FILES:
                raw=z.read("stage/"+name)
                destination=original_stage/name
                need(not destination.exists(),
                     "V309_CROSS_JOB_STAGE_PATH_NOT_EMPTY")
                destination.write_bytes(raw)
        restored=checkpoint.restore_same_absolute_path(
            NEW_RAW,NEW_RAW_SHA,
            newproof["original_output_path"])
        need(restored["committed_cases"]==2185,
             "V309_RESTORED_NEW25_CASE_COUNT")
        staged=longrun.entry.source(original_stage/"manifest.json")
        context=staged["context"]
        need(context["identity"]==stored["context"],
             "V309_CROSS_JOB_ADMITTED_SOURCE_IDENTITY_DIFFERS")
        output=staged["paths"]["output_dir"]
        need(str(output)==newproof["original_output_path"],
             "V309_CROSS_JOB_ABSOLUTE_JSON2_PATH_CHANGED")
        cache=durable.run(
            context,staged["flask"],binary,output,
            max_native_calls=17076,
            cache_only=True,max_new_native_this_invocation=0,
            v309_prior_compact_artifact_zip=str(OLD_COMPACT),
            v309_prior_raw_checkpoint_zip=str(OLD_RAW),
            v309_prior_raw_checkpoint_sha256=OLD_RAW_SHA)
        need(cache["new_native_this_invocation"]==0 and
             cache["completed_cases"]==2185 and
             cache["progressive_level21_coverage"][
                 "combined_observed_geometric_coverage"]==4953,
             "V309_CROSS_JOB_ORIGINAL_NATIVE_CACHE_REAUTH_FAILED")
        report["original_cache_only_replay_verified"]=True
        report["cross_job_raw_native_usable_as_exact_cache"]=True
        report["status"]="PASS_V309_CROSS_JOB_ZERO_NEW_DPS_NATIVE_REPLAY"
        save(report)
        print("V309_CROSS_JOB_CACHE_ONLY_REAUTH_PASS",
              json.dumps({"status":report["status"],
                          "old_dps_new_executions":0,
                          "restored_cases":2185,
                          "same_source_sha":context["identity"][
                              "source_profile_sha256"]},sort_keys=True),flush=True)
        return report
    except BaseException as e:
        report["status"]="BLOCKED_OR_PARTIAL_"+type(e).__name__
        report["error"]=str(e)[:200]
        save(report)
        raise


if __name__=="__main__":
    main()
