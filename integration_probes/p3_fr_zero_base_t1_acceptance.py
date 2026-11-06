"""One real zero-history T1 attempt through the ORIGINAL v216 Build.

No fabricated items, installed season catalog, prior cache, user ItemIDs or
mocked collectors. Public Retail version is fetched at runtime; source HTTP
and the existing SimC Native path are allowed. A successful workflow means
the original v212 installed READY, not merely that a probe script ran.
"""
from __future__ import annotations

import json
import os
import pathlib
import tempfile
from datetime import datetime,timezone

from runner import v216_environment_build_coordinator as engine
from runner import v289_retail_live_build_source as retail
from runner import v242_authenticated_season_source_stage as season_auth
from integration_probes import p3_fs_simc_image_revision as simc_image

OUT=pathlib.Path("p3_fr_zero_base_t1_receipt.json")

def main():
    rec={
        "schema":"p3_fr_real_zero_history_t1_attempt_v1",
        "attempt_utc":datetime.now(timezone.utc).isoformat(),
        "status":"NOT_READY",
        "environment_ready":False,
        "environment_installed":False,
        "target_ilevel":334,
        "previous_item_ids":0,
        "user_selected_gem_ids":0,
        "user_selected_flask_id":None,
        "historical_source_cache_used":False,
        "previous_session_count":0,
        "simc_native_opt_in":False,
        "prerequisite_status":"NOT_CHECKED"}
    try:
        live=retail.discover(region="KR")
        rec["live_retail_version"]=live
        # These four existing v242 source credentials are required by the
        # present v163 raid/season join. Fail before a 100MB+ Wago download
        # when the runner has not received its configured secrets.
        missing=[key for key in season_auth.FIELDS
                 if not os.environ.get(key)]
        rec["missing_credential_names"]=missing  # never values
        if missing:
            rec["status"]="ZERO_BASE_T1_PREREQUISITES_MISSING"
            rec["prerequisite_status"]="AUTH_SEASON_SOURCE_INPUTS_MISSING"
            return 2
        binary=os.environ.get("SIMC_CLI_WRAPPER") or ""
        candidate=pathlib.Path(binary) if binary else None
        if candidate is not None and not candidate.is_file():
            raise RuntimeError("ZERO_BASE_SIMC_BINARY_NOT_AVAILABLE")
        rec["simc_native_opt_in"]=candidate is not None
        image_ref=os.environ.get("SIMC_IMAGE_REF") or ""
        if candidate is None or not image_ref:
            rec["status"]="ZERO_BASE_T1_PREREQUISITES_MISSING"
            rec["prerequisite_status"]="SIMC_BINARY_IMAGE_PIN_MISSING"
            return 2
        # The source SHA hint belongs to the EXACT Docker digest we pulled,
        # never the latest unpinned upstream branch or an older-season value.
        try:
            pin=simc_image.discover(
                image_ref=image_ref,game_build=live["game_build"])
        except simc_image.SimCImageRevisionPending as exc:
            rec["status"]="ZERO_BASE_T1_PREREQUISITES_MISSING"
            rec["prerequisite_status"]=str(exc)
            return 2
        rec["simc_image_source_identity"]=pin
        rec["prerequisite_status"]="SOURCE_POINTERS_PRESENT_UNVERIFIED"
        # No prior files and no sealed source supplied to the program.
        with tempfile.TemporaryDirectory(prefix="simc-zero-base-t1-") as temp:
            root=pathlib.Path(temp)
            assert not list(root.iterdir())
            inputs={
                "expected_game_build":live["game_build"],
                "representative_request":{
                    "class":"paladin","spec":"retribution",
                    "target_ilevel":334},
                "g_probe_character":{"race":"dwarf"},
                "simc_revision_hint":pin["revision_hint"],
                "auto_four_stat_source_requested":True,
                "auto_native_G_requested":candidate is not None,
                "auto_native_F_requested":candidate is not None,
                "auto_native_O_requested":False,
                "auto_select_observed_F_no_oil":candidate is not None,
            }
            result=engine.build_environment(
                sessions_root=root,session_folder=None,user=None,
                binary=candidate,revision=None,static_cache=None,
                source_catalog_path=None,bootstrap_result=None,
                fresh_collection_inputs=inputs)
            # Source-owner causes, not just nine downstream compiler flags.
            # The original rows are unchanged and may be large; record only
            # compact, nonsecret status/receipt reuse information.
            owners=(
                "season_discovery","season_join","fresh_ordinary_gear",
                "fresh_tier","fresh_tier_simc_candidate_bridge",
                "fresh_tier_selected_from_existing_evidence",
                "fresh_compiler_tier_source",
                "fresh_pinned_first_party_simc_source",
                "fresh_pinned_v211_source",
                "fresh_pinned_simc_commit_resolution",
                "fresh_food_potion_item_sources",
                "fresh_consumable_item_spell_source",
                "fresh_consumable_simc_effect_relation",
                "fresh_one_spec_simc_representative",
                "fresh_one_spec_physical_G_probe",
                "fresh_gem_enchant_raw_source")
            rec["source_owner_statuses"]={
                key:{
                    "status":row.get("status"),
                    "source_stage_status":(
                        (row.get("source_stage") or {}).get("status")
                        if type(row.get("source_stage")) is dict else None),
                    "reason":row.get("reason"),
                    "requires":row.get("requires"),
                    "missing":row.get("missing"),
                    "has_candidate":bool(row.get("candidate_path")),
                    "has_pinned_dir":bool(row.get("source_dir")),
                }
                for key in owners
                for row in [result.get(key)]
                if type(row) is dict}
            progress=result.get("zero_history_build") or {}
            compiled=result.get("source_compilation") or {}
            rec.update({
                "source_stage_status":(
                    (result.get("source_stage") or {}).get("status")),
                "source_compilation_status":compiled.get("status"),
                "source_compilation_missing":compiled.get("missing",[]),
                "zero_history_requires":progress.get("requires",[]),
                "current_build_source_identity":(
                    result.get("expected_game_build")==live["game_build"]),
                "simc_native_calls_reported":result.get("native_calls"),
                "environment_ready":result.get("environment_ready") is True,
                "environment_installed":result.get(
                    "environment_installed") is True,
                "budget_evidence":{
                    n:result.get(n) for n in ("G","J","F","O","B","T")},
                "diagnostics":{
                    "J_source":(
                        compiled.get("selected_J_F_source_owner_numeric_unadmitted") or {}
                        ).get("status"),
                    "JF_quality":(
                        compiled.get("selected_J_F_source_owner_quality_unadmitted") or {}
                        ).get("status"),
                    "G_native":(
                        result.get("native_G_numeric_source") or {}).get("status"),
                    "gem_layout":bool(
                        progress.get("default_intrinsic_gem_layout_unadmitted")),
                    "verified_installer":bool(
                        compiled.get("verified_environment_install"))},
            })
            installed=compiled.get("verified_environment_install") or {}
            rec["installed_status"]=installed.get("status")
            ready=(rec["environment_ready"] and
                   rec["environment_installed"] and
                   installed.get("status")==
                       "FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY"
                   and installed.get("stage_output_path"))
            rec["status"]="ZERO_BASE_T1_PASS" if ready else "ZERO_BASE_T1_NOT_READY"
    except Exception as error:
        rec["status"]="ZERO_BASE_T1_BLOCKED"
        rec["exception_type"]=type(error).__name__
        rec["reason"]=str(error)[:500]
    finally:
        OUT.write_text(json.dumps(rec,ensure_ascii=False,sort_keys=True,
                                  indent=2,default=str)+"\n",encoding="utf8")
        print("P3_FR_T1_VERDICT",json.dumps({
            k:rec.get(k) for k in (
                "status","reason","prerequisite_status",
                "missing_credential_names",
                "current_build_source_identity",
                "live_retail_version","source_stage_status",
                "source_compilation_missing","zero_history_requires",
                "simc_native_calls_reported","environment_ready",
                "environment_installed")},ensure_ascii=False,default=str),
            flush=True)
    return 0 if rec["status"]=="ZERO_BASE_T1_PASS" else 2

if __name__=="__main__":
    raise SystemExit(main())
