#!/usr/bin/env python3
"""P3-C source-backed v213 -> v196 -> v098 -> v212 handoff, Native0.

A single existing 334 Retribution profile is used as a focused real-source
integration witness. This does not claim all 26 profile suppliers are ready.
The v208 call is a cache-hit plumbing witness; no new Native is performed.
"""
from __future__ import annotations
import argparse
import json
import pathlib
import sys
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))
sys.path.insert(0, str(ROOT / "tests"))

import v098_target_user_scenario_bootstrap as bootstrap
import v196_current_season_user_catalog as ui_catalog
import v206_nonchmv_eagle_selection as eagle
import v208_internal_exact_special_L_hydrator as exact_L
import v212_environment_manifest as environment
from test_v098_target_user_scenario_bootstrap import case


def write_json(path, value):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True,
                               indent=2) + "\n", encoding="utf8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-to-catalog", required=True, type=pathlib.Path)
    parser.add_argument("--out", required=True, type=pathlib.Path)
    parser.add_argument("--work-root", required=True, type=pathlib.Path)
    args = parser.parse_args()

    source_path = args.source_to_catalog.resolve()
    source_catalog, source_sha = environment.read_json(source_path)
    ui = ui_catalog.public_options(source_path)
    approved = [row["enchant_id"] for row in
                ui["enchant_candidates"]["items"]
                if row.get("ui_selectable") is True]
    if approved != [7967]:
        raise RuntimeError("P3C_EXPECTED_EXACT_7967_APPROVAL:" + repr(approved))

    root = args.work_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    binary = root / "simc-placeholder-not-executed.bin"
    binary.write_bytes(b"SIMC_BINARY_PLACEHOLDER_NEVER_EXECUTED")
    revision = source_catalog["simc_revision"]

    # Use the existing v098 user-scenario composer and the one already
    # approved 7967 non-CHMV choice. No user gear inventory or new optimizer.
    user = case("retribution")
    user[eagle.FIELD] = dict(eagle.CHOICE)
    target_root = root / "target-profile"
    result = bootstrap.build(
        user, target_root, binary, revision,
        current_season_product=True,
        source_catalog_path=source_path)
    if result.get("native_calls") != 0 or result.get("status") != (
            "READY_INTERNAL_MANIFEST_ZERO_NATIVE"):
        raise RuntimeError("P3C_V098_PLAN_NOT_NATIVE_ZERO")
    profile = (target_root / "profile.simc").read_text(encoding="utf8")
    if profile.count("enchant_id=7967") != 1:
        raise RuntimeError("P3C_V098_PROFILE_DID_NOT_EMIT_APPROVED_7967")
    if result.get("selected_nonchmv_enchant", {}).get("choice") != {
            "finger1": 7967}:
        raise RuntimeError("P3C_V098_SELECTION_IDENTITY_DRIFT")
    bootstrap_path = root / "v098_bootstrap_result.json"
    write_json(bootstrap_path, result)

    # v212 reads the exact v213 artifact and derives the existing v196
    # approved read model from that same path. No separately maintained UI DB.
    manifest = environment.compile_from_paths(
        source_path, bootstrap_path, target_root)
    if manifest["approved_ui_catalog"]["selectable_enchant_ids"] != [7967]:
        raise RuntimeError("P3C_V212_APPROVAL_IDENTITY_DRIFT")
    if manifest["selected_nonchmv_enchant"]["budget_increment"] != 0:
        raise RuntimeError("P3C_7967_MUST_NOT_CHANGE_CHMV_BUDGET")
    write_json(args.out, manifest)

    # Exercise the existing v208 Start-time pre-budget staging path with the
    # same explicit v213 source path. Force an exact cache hit in this plumbing
    # witness so no physical Native is invoked; real miss behavior remains
    # covered by the existing v208 Native/cache receipts.
    special_user = case("elemental", ilevel=331)
    special_user["special_items"] = [{
        "slot": "back", "item_id": 159288, "options": {}}]
    fake_cache = root / "existing-static-cache.json"
    fake_cache.write_text("{}", encoding="utf8")
    staged_capture = {}
    def capture_stage(*args, **kwargs):
        staged_capture["value"] = bootstrap.build(*args, **kwargs)
        return staged_capture["value"]
    with (mock.patch.object(exact_L.item_cache, "load", return_value={}),
          mock.patch.object(exact_L, "missing_specials", return_value=[]),
          mock.patch.object(exact_L.bootstrap, "build",
                            side_effect=capture_stage) as build_spy):
        hydrated = exact_L.hydrate(
            special_user, root / "v208-runs", binary, revision,
            existing=fake_cache, source_catalog_path=source_path)
    if hydrated.get("native_new_calls") != 0 or not build_spy.called:
        raise RuntimeError("P3C_V208_CACHE_HIT_PLUMBING_FAILED")
    if build_spy.call_args.kwargs.get("source_catalog_path") != source_path:
        raise RuntimeError("P3C_V208_DID_NOT_RECEIVE_EXACT_V213_PATH")

    write_json(root / "v208_prebudget_handoff_receipt.json", {
        "schema": "v208_p3c_source_catalog_path_handoff_v1",
        "source_catalog_manifest_sha256": source_catalog["manifest_sha256"],
        "source_catalog_file_sha256": source_sha,
        "source_profile_sha256": staged_capture["value"]["source_profile_sha256"],
        "selected_special_count": 1,
        "native_calls": hydrated["native_new_calls"],
        "cache_reused": hydrated["cache_reused"],
        "source": hydrated["source"],
        "source_catalog_path_consumed_by_v098": True,
        "no_optimizer_or_budget_produced": True,
    })

    print("P3C_V213_TO_V196_EXACT_7967_APPROVAL_PASS")
    print("P3C_V098_CURRENT_SEASON_RETRIBUTION_PROFILE_PASS_NATIVE0")
    print("P3C_V212_SOURCE_CATALOG_ENVIRONMENT_MANIFEST_PASS_NATIVE0")
    print("P3C_V208_SELECTED_SPECIAL_CACHE_HIT_PATH_PASS_NATIVE0")
    print("P3C_ENVIRONMENT_MANIFEST_SHA256", manifest["manifest_sha256"])
    print("P3C_SOURCE_CATALOG_SHA256", source_sha)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
