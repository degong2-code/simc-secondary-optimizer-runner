#!/usr/bin/env python3
"""One authenticated, zero-seed A7 source-only diagnostic. No SimC/Native.

Uses the SAME normal v216 source stages and local v405 source-consumer audit.
No manual game season, expansion, raid, item ID, gear budget, or AI choice.
Never persists tokens, raw DB2 CSV or individual item names in output.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import sys
import tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v289_retail_live_build_source as retail
import v242_authenticated_season_source_stage as auth
import v161_wago_db2_snapshot as wago
import v216_environment_build_coordinator as coordinator

OUTPUT=pathlib.Path("a7_v405_real_source_receipt.json")

def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def run():
    report={
        "schema":"p1_v405_a7_real_source_choice_receipt_v1",
        "source_root_empty":True,
        "season_or_expansion_id_preseeded":False,
        "manual_item_id_selection":False,
        "preloaded_item_csv_or_budget":False,
        "runtime_ai_used":False,
        "native_calls":0,
        "new_simc_calls":0,
        "environment_installed":False,
        "final_user_e2e":False,
        "status":"STARTED"}
    try:
        found=retail.discover(region="KR")
        game_build=found["game_build"]
        report["retail"]={
            "region":found["region"],"game_build":game_build,
            "bpsv_sha256":found["source_sha256"]}
        credentials={name:os.environ.get(name,"") for name in auth.FIELDS}
        if not all(credentials.values()):
            report["status"]="PENDING_PROVIDER_CREDENTIALS"
            return report
        with tempfile.TemporaryDirectory(prefix="a7_v405_zero_source_") as temp:
            root=pathlib.Path(temp)
            authenticated=auth.collect(
                stage_root=root,expected_game_build=game_build,
                credentials=credentials)
            report["authenticated_source_status"]=authenticated["status"]
            report["authenticated_source_receipt_sha256"]=(
                (authenticated.get("stage") or {}).get("receipt_sha256"))
            report["auth_api_calls"]=authenticated["network_calls_by_stage"]
            if not authenticated.get("season_join_ready"):
                report["status"]="PENDING_AUTHENTICATED_SEASON_SCOPE"
                return report
            folder=root/"wago_10_tables"
            raw=wago.snapshot(folder,build=game_build,make_archive=False)
            report["wago_original_tables"]=len(raw["tables"])
            report["wago_original_bytes"]=raw["total_csv_bytes"]
            report["wago_original_receipt_sha256"]=sha(
                folder/"receipt.json")
            report["wago_original_table_sha256"]={
                table:info["sha256"]
                for table,info in sorted(raw["tables"].items())}
            verified={t:{"sha256":info["sha256"],"bytes":info["bytes"]}
                      for t,info in raw["tables"].items()}
            joined=coordinator._join_authenticated_season_source(
                stage_root=root,output_dir=folder,
                expected_game_build=game_build,discovered=authenticated,
                wago_stage_receipt=report["wago_original_receipt_sha256"],
                verified_tables=verified)
            report["v163_status"]=joined["status"]
            report["v163_stage_receipt_sha256"]=(
                (joined.get("stage") or {}).get("receipt_sha256"))
            if not joined.get("candidate_path"):
                report["status"]="PENDING_UNIQUE_CURRENT_RAID_MPLUS_JOIN"
                return report
            season=json.loads(pathlib.Path(
                joined["candidate_path"]).read_text("utf8"))
            report["scope"]={
                "wcl_raid_id":season["wcl_zone_ids"]["raid"],
                "wcl_mplus_id":season["wcl_zone_ids"]["mplus"],
                "db2_expansion_id":season["db2_expansion_id"],
                "db2_display_season_id":season["db2_display_season_id"],
                "mapped_raid_bosses":season["mapped_raid_bosses"],
                "mapped_mplus_dungeons":season["mapped_mplus_dungeons"]}
            report["joined_item_source_count"]=len(season["items"])
            report["source_unknown_join_count"]=len(season.get("unknown",[]))
            report["wse_is_membership_gate"]=(
                season["world_state_expression_membership_gate"])
            gear=coordinator._fresh_ordinary_gear_source_stage(
                stage_root=root,wago_folder=folder,
                build=game_build,linked=joined)
            report["fresh_gear_status"]=gear["status"]
            report["v254_effect_source_new_requests"]=(
                gear["network_calls_by_stage"])
            report["v254_stage_receipt_sha256"]=(
                (gear.get("source_stage") or {}).get("receipt_sha256"))
            a7=gear.get("a7_auto_source_choice_provenance") or {}
            report["a7_status"]=a7.get("status")
            report["a7_verified_source_to_public_choices"]=a7.get(
                "candidate_provenance_verified",False)
            report["v405_stage_receipt_sha256"]=(
                (a7.get("source_stage") or {}).get("receipt_sha256"))
            if not a7.get("candidate_provenance_verified"):
                report["status"]="PENDING_A7_AUTOMATIC_SOURCE_RECONCILIATION"
                report["first_missing_code"]=a7.get("reason")
                return report
            receipt=json.loads(pathlib.Path(
                a7["receipt_path"]).read_text("utf8"))
            report["public_candidate_count"]=receipt["public_candidate_count"]
            report["public_role_counts"]=receipt["public_role_counts"]
            report["source_reconciled_candidate_count"]=receipt[
                "source_reconciled_candidate_count"]
            report["public_candidate_ids_sha256"]=receipt[
                "public_item_ids_sha256"]
            report["source_reconciled_ids_sha256"]=receipt[
                "source_reconciled_candidate_ids_sha256"]
            report["wse_diagnostic_only"]=(
                receipt["wse_diagnostics_preserved_not_evaluated"]
                and not receipt["item_eligibility_requires_wse"])
            # Same root, exact same input bytes; repeat only local v217
            # validation. ANY extra effect HTTP or Native call is a failure.
            reused=coordinator._fresh_ordinary_gear_source_stage(
                stage_root=root,wago_folder=folder,build=game_build,
                linked=joined,transport=lambda *_: (
                    (_ for _ in ()).throw(
                        AssertionError("A7_SAME_SOURCE_REFETCH_FORBIDDEN"))))
            report["same_source_reused_without_extra_http"]=(
                reused["network_calls_by_stage"]==0
                and reused.get("source_stage",{}).get(
                    "status")=="REUSED_VERIFIED"
                and reused.get("a7_auto_source_choice_provenance",{})
                    .get("source_stage",{}).get("status")=="REUSED_VERIFIED")
            report["status"]=(
                "A7_REAL_ZERO_SEED_SOURCE_PUBLIC_CHOICES_RECONCILED"
                if receipt["source_reconciled_candidate_count"]>0
                   and report["same_source_reused_without_extra_http"]
                else "PENDING_A7_REAL_SOURCE_EMPTY_OR_REUSE_FAILED")
    except Exception as exc:
        report["status"]="A7_REAL_SOURCE_RUNTIME_ERROR"
        report["error_kind"]=type(exc).__name__
        # Do not echo the exception, request path, token or raw body.
        report["first_missing_code"]="SEE_PRIVATE_ACTIONS_LOG_WITHOUT_SECRETS"
    return report

def main():
    summary=run()
    OUTPUT.write_text(json.dumps(
        summary,sort_keys=True,ensure_ascii=False,indent=2,
        allow_nan=False)+"\n",encoding="utf8")
    print("A7_REAL_SOURCE_DIAGNOSTIC",summary["status"],
          "BUILD",summary.get("retail",{}).get("game_build"),
          "AUTO_SOURCE_ITEMS",summary.get("source_reconciled_candidate_count"),
          "PUBLIC_CHOICES",summary.get("public_candidate_count"),
          "REUSE",summary.get("same_source_reused_without_extra_http"),
          "NATIVE_0")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
