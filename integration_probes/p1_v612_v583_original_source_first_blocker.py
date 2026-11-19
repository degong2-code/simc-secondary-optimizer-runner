#!/usr/bin/env python3
"""v612: one real 70961 source-only v583 first-blocker diagnosis; NO Native.

Reuse original v216.collect_wago_new_season_source and all its stage seals.
Fresh workspace because prior one-shot Windows M1/M2 ephemeral stage bytes
were not included in artifact. Do not forge product_input or E=0.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner"),str(ROOT/"integration_probes")]
import v216_environment_build_coordinator as build
from p1_v524_m1_m2_source_owner_once import EphemeralActionsCredentials,bounded_code

BUILD="12.1.5.70961"
REV="9933ffb946fb55b1fa66657b848f519ac19006e1"
SCHEMA="p1_v612_real_70961_v583_original_first_missing_dependency_v1"
DEPS={
    "wago":"source_stage",
    "v254_gear":"fresh_ordinary_gear",
    "v280_item_effect":"fresh_consumable_item_spell_source",
    "v281_spell_effect":"fresh_consumable_simc_effect_relation",
    "v275_simc_compiler":"fresh_pinned_v211_source",
    "v256_full_simc":"fresh_lazy_full_pinned_simc_item_source",
    "v583_permanent_quality":"fresh_permanent_enchant_item_source",
    "season_join":"season_join",
}


def run(out):
    folder=Path(out).resolve()
    folder.mkdir(parents=True,exist_ok=True)
    target=folder/"V612_REAL_70961_V583_SOURCE_BLOCKER.json"
    doc={"schema":SCHEMA,"status":"STARTED",
        "game_build":BUILD,"simc_revision":REV,
        "normal_v216_source_collector_used":False,
        "exact_Policy_A_product_input_not_fabricated":True,
        "actual_enchant_ui_promotion":False,
        "actual_enchant_native_calls":0,
        "user_dps_native_calls":0,
        "source_only_not_user_environment_installed":True}
    def save():
        target.write_text(json.dumps(doc,ensure_ascii=False,indent=2,
            sort_keys=True,default=str,allow_nan=False)+"\n",encoding="utf8")
    save()
    try:
        if (os.getenv("SIMC_PINNED_SOURCE_COMMIT")!=REV
            or os.getenv("SIMC_PINNED_GAME_BUILD")!=BUILD):
            raise RuntimeError("V612_SOURCE_BUILD_REVISION_PIN_MISMATCH")
        cred=EphemeralActionsCredentials().load()
        if cred is None:
            doc["status"]="PENDING_SEASON_SOURCE_CREDENTIALS"
            save()
            return 2
        with tempfile.TemporaryDirectory(prefix="v612-wago-",dir=folder) as temp:
            result=build.collect_wago_new_season_source(
                sessions_root=Path(temp)/"runs",
                expected_game_build=BUILD,
                credentials=cred,
                simc_revision_hint=REV,
                representative_request={
                    "class":"paladin","spec":"retribution","target_ilevel":334},
                g_probe_character={"race":"dwarf"})
            doc["normal_v216_source_collector_used"]=True
            doc["collector_status"]=result.get("status")
            doc["network_calls_by_stage"]=result.get("network_calls_by_stage")
            doc["native_calls"]=result.get("native_calls")
            for label,key in DEPS.items():
                val=result.get(key) or {}
                if key=="source_stage":
                    val=result.get("source_stage") or {}
                row={"status":val.get("status"),"reason":val.get("reason"),
                     "stage_status":(val.get("source_stage") or {}).get("status"),
                     "source_stage_receipt_sha256":
                         (val.get("source_stage") or {}).get("receipt_sha256"),
                     "network_calls_by_stage":val.get("network_calls_by_stage")}
                if label=="season_join":
                    # v163's signed candidate has auto_source_scope INSIDE
                    # the file; its outward collection result exposes
                    # the same authenticated data as source_scope.
                    row["expansion_id"]=(
                        val.get("source_scope") or {}).get("expansion_id")
                    row["season_source_scope"]=(
                        val.get("source_scope") or {}).get("source_basis")
                doc[label]=row
            v583=result.get("fresh_permanent_enchant_item_source") or {}
            doc["v583_first_blocker"]=v583.get("reason")
            doc["v583_source_counts"]=v583.get("counts")
            doc["v583_exact_candidate_present"]=(
                v583.get("status")==
                    "PERMANENT_ENCHANT_EXACT_WAGO_SIMC_SOURCE_ONLY"
                and type(v583.get("candidate_path")) is str)
            if doc["v583_exact_candidate_present"]:
                # Verify exact original stage output is genuinely sealed; do
                # not convert SOURCE_ONLY to a published user option.
                p=Path(v583["candidate_path"])
                data=json.loads(p.read_text("utf8"))
                doc["v583_exact_game_build"]=data.get("game_build")
                doc["v583_original_match_count"]=len(data.get("matches") or [])
                # v615 diagnostic: use the ORIGINAL zero-Native Build/compilers
                # on the SAME source root. Sealed v217 stages are reused; do
                # not promote the synthetic review into product approval.
                try:
                    reread=build.build_environment(
                        sessions_root=Path(temp)/"runs",
                        session_folder=None,user=None,binary=None,
                        revision=None,static_cache=None,
                        source_catalog_path=None,bootstrap_result=None,
                        fresh_collection_inputs={
                            "expected_game_build":BUILD,
                            "representative_request":{
                                "class":"paladin","spec":"retribution",
                                "target_ilevel":334},
                            "g_probe_character":{"race":"dwarf"},
                            "simc_revision_hint":REV,"credentials":cred})
                    comp=reread.get("source_compilation") or {}
                    doc["v615_compilation_status"]=comp.get("status")
                    doc["v615_compilation_missing"]=comp.get("missing")
                    doc["v615_reused_network_calls"]=(reread.get(
                        "network_calls_by_stage"))
                    doc["v615_native_calls"]=reread.get("native_calls")
                    if (type(comp.get("source_catalog_path")) is str
                        and type(comp.get("stage_root")) is str
                        and all(type(comp.get(n)) is dict for n in (
                                "v191_stage","v211_stage","v213_stage"))):
                        stage_root=Path(comp["stage_root"])
                        catalog,_=build.environment_manifest.read_json(
                            comp["source_catalog_path"])
                        original,v191_hash=build.environment_manifest.read_json(
                            stage_root/"fresh_source"/"v191_candidate.json")
                        doc["v615_v191_sha_matches_catalog"]=(
                            v191_hash==catalog["source_provenance"]["v191"][
                                "sha256"])
                        doc["v615_v583_revision_matches_catalog"]=(
                            data.get("simc_revision")==catalog.get("simc_revision"))
                        doc["v615_v583_build_matches_catalog"]=(
                            data.get("game_build")==catalog.get("game_build"))
                        doc["v615_v191_record_count"]=len(
                            original.get("enchants",{}).get("permanent",{})
                                .get("source_records") or [])
                        doc["v615_catalog_enchant_candidate_count"]=len(
                            catalog.get("v196_enchant_source",{}).get("rows") or [])
                        direct=build._v607_sealed_highest_crafting_quality(
                            catalog=catalog,original_v191=original,
                            physical_v583=data,
                            v191_sha=comp["v191_stage"]["receipt_sha256"],
                            v583_sha=v583["source_stage"]["receipt_sha256"])
                        doc["v615_direct_sealed_quality_owner_count"]=len(direct)
                        doc["v615_direct_sealed_quality_owner_first_ids"]=(
                            sorted(direct)[:10])
                        # The actual published Policy A producer is reused
                        # unchanged; count only real original receipts.
                        pre=build.preflight_new_season_source(
                            source_catalog_path=comp["source_catalog_path"],
                            expected_game_build=BUILD,
                            expected_simc_revision=REV,
                            policy_A_v217_stages={
                                "stage_root":comp["stage_root"],
                                "v191_stage":comp["v191_stage"],
                                "v211_stage":comp["v211_stage"],
                                "v213_stage":comp["v213_stage"]},
                            policy_A_v583_physical_source=v583)
                        meta=pre.get("optional_policy_A_evidence_unadmitted") or {}
                        receipts=meta.get(
                            "original_v217_source_relation_receipts_internal") or {}
                        doc["v615_product_receipt_production_count"]=sum(
                            "product_input" in proof for proof in receipts.values())
                        doc["v615_static_E_receipt_production_count"]=sum(
                            "chmv_budget" in proof for proof in receipts.values())
                        doc["v615_replay_stage_statuses"]={
                            k:comp[k].get("status") for k in (
                                "v191_stage","v211_stage","v213_stage")}
                        if not direct:
                            doc["v615_first_quality_boundary"] = (
                                "V607_SOURCE_PROJECTION_RETURNED_ZERO")
                        elif not doc["v615_product_receipt_production_count"]:
                            doc["v615_first_quality_boundary"] = (
                                "V607_STAGE_ATTESTATION_OR_SHA_CHECK_PENDING")
                        else:
                            doc["v615_first_quality_boundary"] = None
                    else:
                        doc["v615_first_quality_boundary"] = (
                            "V191_V211_V213_ORIGINAL_STAGE_COMPILATION_PENDING")
                except Exception as exp:
                    doc["v615_diagnostic_status"]="BLOCKED_"+type(exp).__name__
                    doc["v615_diagnostic_first_blocker"]=bounded_code(exp)
                doc["status"]="PASS_REAL_V583_SOURCE_ONLY"
            else:
                doc["status"]="PENDING_REAL_V583_SOURCE_FIRST_BLOCKER_IDENTIFIED"
            save()
            return 0
    except Exception as exc:
        doc["status"]="BLOCKED_"+type(exc).__name__
        doc["first_blocker"]=bounded_code(exc)
        save()
        return 2


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    sys.exit(run(args.out))


if __name__=="__main__":
    main()
