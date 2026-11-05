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
        "simc_native_opt_in":False}
    try:
        live=retail.discover(region="KR")
        rec["live_retail_version"]=live
        binary=os.environ.get("SIMC_CLI_WRAPPER") or ""
        candidate=pathlib.Path(binary) if binary else None
        if candidate is not None and not candidate.is_file():
            raise RuntimeError("ZERO_BASE_SIMC_BINARY_NOT_AVAILABLE")
        rec["simc_native_opt_in"]=candidate is not None
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
                "simc_revision_hint":None,
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
                "status","reason","current_build_source_identity",
                "live_retail_version","source_stage_status",
                "source_compilation_missing","zero_history_requires",
                "simc_native_calls_reported","environment_ready",
                "environment_installed")},ensure_ascii=False,default=str),
            flush=True)
    return 0 if rec["status"]=="ZERO_BASE_T1_PASS" else 2

if __name__=="__main__":
    raise SystemExit(main())
