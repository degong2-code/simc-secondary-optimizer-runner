#!/usr/bin/env python3
"""v610 one actual 70783 M1/M2 build; inspect real v607/608 enchant admission.

No historical JSON injection or isolated admission gate. This probe calls
existing v113 LocalJobs and v216/v212 only, and stops before user DPS.
The original v217 stage workspace is ephemeral; receipt records only exact
observations and negative proof gaps. No credentials or source tables shipped.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner"),str(ROOT/"integration_probes")]
from p1_v524_m1_m2_source_owner_once import (
    BUILD,REV,EXE_SHA,EphemeralActionsCredentials,digest,bounded_code)
import v113_local_web_api as web
import v216_environment_build_coordinator as build
import v212_environment_manifest as installed_manifest
import v289_retail_live_build_source as retail

SCHEMA="p1_v610_real_original_v216_v212_permanent_enchant_admission_once_v1"


def run(binary,output_folder,*,postinstall=None):
    output_folder=pathlib.Path(output_folder).resolve()
    output_folder.mkdir(parents=True,exist_ok=True)
    target=output_folder/"V610_REAL_ENCHANT_ADMISSION_ONE_BUILD.json"
    doc={"schema":SCHEMA,"status":"STARTED",
         "exact_game_build":BUILD,"simc_revision":REV,
         "simc_binary_sha256":EXE_SHA,
         "new_dps_native_calls":0,"full_product_e2e":"PENDING",
         "new_optimizer":False,"source_cached_old_season_used":False,
         "actual_enchant_registration_count":None,
         "actual_user_enchant_native_dps":"NOT_EXECUTED",
         "proofs_fabricated":False,"new_effect_gate":False,
         "actual_installed_enchant_user_profile_tested":False}
    def save():
        target.write_text(json.dumps(
            doc,ensure_ascii=False,sort_keys=True,indent=2,
            allow_nan=False,default=str)+"\n",encoding="utf8")
    save()
    try:
        binary=pathlib.Path(binary).resolve(strict=True)
        if (sys.platform!="win32" or binary.name.lower()!="simc.exe"
            or digest(binary)!=EXE_SHA):
            raise RuntimeError("V610_ORIGINAL_PINNED_WINDOWS_SIMC_IDENTITY_REQUIRED")
        if (os.getenv("SIMC_PINNED_SOURCE_COMMIT")!=REV
            or os.getenv("SIMC_PINNED_GAME_BUILD")!=BUILD):
            raise RuntimeError("V610_PINNED_SOURCE_REVISION_BUILD_MISMATCH")
        if EphemeralActionsCredentials().load() is None:
            doc["status"]="PENDING_SOURCE_AUTH_CREDENTIALS"
            save()
            return 2
        live=retail.discover(region="KR")
        doc["live_game_build"]=live.get("game_build")
        doc["live_build_source_sha256"]=live.get("source_sha256")
        # The game may have advanced since the verified 70783 source snapshot.
        # NEVER copy the previous season's G/J/F/O to a different live build.
        if live.get("game_build")!=BUILD:
            doc["status"]="PENDING_MATCHED_CURRENT_GAME_BUILD_SIMC"
            doc["first_blocker"]="LIVE_BUILD_DIFFERS_FROM_70783_PINNED_BINARY"
            save()
            return 2
        banner=subprocess.run([str(binary)],input="",capture_output=True,
                    text=True,errors="replace",cwd=binary.parent,timeout=25)
        if (banner.returncode!=0 or BUILD not in
            (banner.stdout+"\n"+banner.stderr)):
            raise RuntimeError("V610_SIMC_BANNER_GAME_BUILD_DRIFT")
        with tempfile.TemporaryDirectory(prefix="v610-enchant-",dir=output_folder) as temp:
            root=pathlib.Path(temp)/"runs"
            root.mkdir()
            jobs=web.LocalJobs(root,source_credential_store=EphemeralActionsCredentials())
            myth=jobs.discover_season_myth_target(BUILD)
            doc["M1"]={k:myth.get(k) for k in (
                "status","reason_code","game_build","target_ilevel",
                "currency_csv_sha256","original_v161_receipt_sha256")}
            save()
            if (myth.get("status")!=
                    "MYTH_TARGET_CANDIDATE_FROM_MATCHED_WAGO_V163_SOURCE"
                or myth.get("target_ilevel")!=334):
                doc["status"]="PENDING_ORIGINAL_M1_CURRENT_SEASON_TARGET"
                doc["first_blocker"]=myth.get("reason_code")
                save()
                return 2
            outcome=jobs.build_season_environment(
                game_build=BUILD,target_ilevel=334,
                auto_initial_core_build=True,
                auto_initial_core_simc_binary=str(binary),
                simc_revision_hint=REV,
                existing_special_gem_id=None,
                source_target_socket_count=4,
                auto_myth_target_source_build=BUILD,
                auto_myth_target_source_sha256=myth["currency_csv_sha256"])
            comp=outcome.get("source_compilation") or {}
            progress=outcome.get("zero_history_build") or {}
            initial=comp.get("verified_environment_install") or {}
            physically=outcome.get("fresh_permanent_enchant_item_source") or {}
            doc["actual_source_compilation_status"]=comp.get("status")
            doc["source_missing"]=comp.get("missing")
            # Existing v216 normal-Build recovery plan: exact current
            # source identity and actionable per-option budget gaps, not
            # permission to publish or a new Native/effect certification.
            # Keep only this bounded compact receipt, not stage source tables.
            E_repair=comp.get("optional_enchant_E_repair_plan_unadmitted")
            if type(E_repair) is dict:
                doc["optional_enchant_E_repair_plan_unadmitted"]=E_repair
            measured=comp.get("optional_permanent_enchant_E_native_repair")
            if type(measured) is dict:
                doc["original_v633_E_native_repair"]=measured
            doc["real_v583_source_status"]=physically.get("status")
            doc["real_v583_source_counts"]=physically.get("counts")
            doc["new_core_environment_native_calls"]=outcome.get("native_calls")
            doc["diagnostic_no_new_dps_before_real_registration"]=True
            doc["environment_ready"]=outcome.get("environment_ready") is True
            doc["environment_installed"]=outcome.get("environment_installed") is True
            doc["required_core_source_owner_report"]=progress.get(
                "required_core_source_owner_report")
            doc["core_build_first_requires"]=list(
                progress.get("requires") or [])[:12]
            if outcome.get("environment_ready") is True:
                doc["actual_verified_budget"]={k:outcome.get(k)
                                               for k in ("G","J","F","O","B","T")}
            # Read-only producer diagnostic. This uses the exact SAME
            # source compilation's original stage receipts and redoes no
            # Wago collection, no Native, no new authorization.
            if (type(comp.get("source_catalog_path")) is str
                and type(comp.get("stage_root")) is str
                and all(type(comp.get(n)) is dict
                        for n in ("v191_stage","v211_stage","v213_stage"))):
                try:
                    pre=build.preflight_new_season_source(
                        source_catalog_path=comp["source_catalog_path"],
                        expected_game_build=BUILD,
                        expected_simc_revision=REV,
                        policy_A_v217_stages={
                            "stage_root":comp["stage_root"],
                            "v191_stage":comp["v191_stage"],
                            "v211_stage":comp["v211_stage"],
                            "v213_stage":comp["v213_stage"]},
                        policy_A_v583_physical_source=physically)
                    meta=pre.get("optional_policy_A_evidence_unadmitted") or {}
                    receipts=meta.get("original_v217_source_relation_receipts_internal") or {}
                    missing=meta.get("per_item_missing_reasons") or {}
                    doc["original_producer_inspected"]=True
                    doc["original_receipt_item_count"]=len(receipts)
                    doc["receipt_family_counts"]=dict(Counter(
                        family for parts in receipts.values()
                        for family in parts))
                    doc["four_family_eligible_ids"]=[
                        int(i) for i,parts in receipts.items()
                        if set(parts)=={"source_relation","simc_input",
                                       "product_input","chmv_budget"}]
                    doc["four_family_E0_ids"]=[
                        int(i) for i,parts in receipts.items()
                        if set(parts)=={"source_relation","simc_input",
                                       "product_input","chmv_budget"}
                        and type(parts["chmv_budget"].get("fixed_E")) is dict
                        and all(v==0 for v in parts["chmv_budget"]["fixed_E"].values())]
                    doc["original_producer_missing_reasons"]=dict(
                        list(sorted(missing.items(),key=lambda x:int(x[0])))[:50])
                    doc["missing_reason_totals"]=dict(Counter(
                        reason for reasons in missing.values() for reason in reasons))
                except (ValueError,TypeError,OSError,KeyError) as exc:
                    doc["original_producer_inspected"]=False
                    doc["diagnostic_first_blocker"]=bounded_code(exc)
            else:
                doc["original_producer_inspected"]=False
                doc["diagnostic_first_blocker"]="V191_V211_V213_SOURCE_STAGES_NOT_AVAILABLE"
            if (doc["environment_installed"] and type(initial.get("stage_output_path")) is str):
                path=pathlib.Path(initial["stage_output_path"])
                original,_=installed_manifest.read_json(path)
                installed_manifest.verify_fresh_installed_environment(original)
                # Retain the ACTUAL self-hashed v212 product install as a
                # bounded, non-credential user-consumer artifact for the
                # next stage, not a forged v217 original source receipt.
                # This is never used to independently authorize new seasons.
                product_copy=output_folder/"V618_REAL_INSTALLED_V212.json"
                product_copy.write_text(json.dumps(original,sort_keys=True,
                    ensure_ascii=False,indent=2,allow_nan=False)+"\n",
                    encoding="utf8")
                doc["saved_real_installed_v212_artifact"]=product_copy.name
                doc["saved_real_installed_v212_stage_receipt_sha256"]=initial.get(
                    "stage_receipt_sha256")
                doc["actual_installed_manifest_sha256"]=original["manifest_sha256"]
                installed=original["published_verified_options"]
                doc["actual_enchant_registration_count"]=len(installed)
                doc["actual_enchant_registered_first_12"]=[
                    {k:row.get(k) for k in (
                        "enchant_id","slot","highest_verified_quality_rank",
                        "verified_fixed_E","quality_source_sha256")}
                    for row in installed[:12]]
                if installed:
                    doc["status"]="PASS_REAL_SEASON_V212_ENCHANTS_AUTO_REGISTERED"
                    # Optional downstream verification executes only with a
                    # truly installed original v217/v212 and only AFTER the
                    # exact same source-owner stage. Never use a copied JSON
                    # artifact alone to authorize a user/Native session.
                    if postinstall is not None:
                        follow=postinstall(
                            jobs=jobs,environment_result=outcome,
                            document=original,installed_path=path,
                            binary=binary,revision=REV,
                            output_folder=output_folder)
                        doc["v619_exact_user_stage"]=follow
                        # v610's original field referred only to the base
                        # admission phase (zero user DPS calls). When the
                        # optional real v619 callback executes, the summary
                        # MUST reflect its actual Native attempts too.
                        doc["new_dps_native_calls"]=follow.get(
                            "new_dps_native_calls",0)
                        doc["actual_installed_enchant_user_profile_tested"]=(
                            follow.get("v098_status")==
                            "READY_SOURCE_BOUND_SEASON_MANIFEST_ZERO_NATIVE")
                        doc["actual_user_enchant_native_dps"]=follow.get(
                            "original_v096_run_status","NOT_EXECUTED")
                        if follow.get("status")==(
                                "PASS_ORIGINAL_V098_V096_ENCHANT_NATIVE_DPS"):
                            doc["status"]=(
                                "PASS_REAL_INSTALLED_ENCHANT_USER_DPS")
                        elif follow.get("status")==(
                                "PASS_ORIGINAL_V113_OPTIONAL_PROFILE_ZERO_NATIVE"):
                            # A source-bound profile is NOT DPS/Native PASS.
                            doc["status"]=(
                                "PASS_REAL_INSTALLED_OPTIONAL_USER_PROFILE_NO_NATIVE")
                        else:
                            doc["status"]=(
                                "PENDING_REAL_INSTALLED_ENCHANT_USER_DPS")
                            doc["first_blocker"]=follow.get(
                                "first_blocker","SEE_V619_EXACT_USER_STAGE")
                else:
                    doc["status"]="PENDING_REAL_SEASON_ENCHANT_PRODUCT_A_OR_E"
                    doc["first_blocker"]="SEE_ORIGINAL_PRODUCER_MISSING_REASONS"
            else:
                doc["status"]="PENDING_REAL_SEASON_M2_CORE_INSTALL"
                doc["first_blocker"]=(doc["core_build_first_requires"][0]
                       if doc["core_build_first_requires"] else
                       "UNKNOWN_ORIGINAL_ENVIRONMENT_BLOCKER")
            save()
            return (0 if doc["status"] in (
                "PASS_REAL_SEASON_V212_ENCHANTS_AUTO_REGISTERED",
                "PASS_REAL_INSTALLED_ENCHANT_USER_DPS",
                "PASS_REAL_INSTALLED_OPTIONAL_USER_PROFILE_NO_NATIVE") else 2)
    except Exception as exc:
        # Exceptions are never directly logged with absolute paths/secrets.
        doc["status"]="BLOCKED_"+type(exc).__name__
        doc["first_blocker"]=bounded_code(exc)
        save()
        return 2


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--simc",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    sys.exit(run(a.simc,a.out))


if __name__=="__main__":
    main()
