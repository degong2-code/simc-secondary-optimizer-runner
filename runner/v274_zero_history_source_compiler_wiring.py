#!/usr/bin/env python3
"""P3-CC: wire real v216 collected files to ORIGINAL v241 compilers.

This is a tiny path/identity adapter, NOT a second Environment Build, source
collector, effect model, certification engine or fallback to old-season data.
Every optional input comes from the current v216 source-stage result; absent
sources remain PENDING. v241 performs the full source-byte checks when ready.
"""
from __future__ import annotations

import json
from pathlib import Path

import v191_unified_season_data_update as season_compiler
import v168_current_season_tier_discovery as tier_compiler
import v211_enchant_source_effect_classification as enchant_classifier

SCHEMA = "v274_v216_collected_to_v241_fresh_compile_inputs_v1"
STAGED = frozenset(("EXECUTED_AND_SEALED", "REUSED_VERIFIED",
                    "RECOVERED_VERIFIED"))
NEEDED = ("GEAR_V167", "TIER_V168", "V189", "V190",
          "GENERATED_PERMANENT", "GENERATED_TEMPORARY", "GENERATED_GEM",
          "SIMC_V211_SIX_SOURCE_FILES_AND_MANIFEST", "PINNED_SIMC_REVISION")


def _safe_file(value, stage_root):
    if not isinstance(value, (str, Path)):
        return None
    path = Path(value).expanduser()
    if not path.is_file() or path.is_symlink():
        return None
    if not path.resolve().is_relative_to(stage_root):
        return None
    return path.resolve()


def _exact_schema(path, schema):
    if path is None or path.stat().st_size > season_compiler.MAX_FILE:
        return False
    try:
        with path.open(encoding="utf8") as stream:
            doc = json.load(stream)
    except (OSError, ValueError, UnicodeError):
        return False
    return isinstance(doc, dict) and doc.get("schema") == schema


def _from_sealed_candidate(row, stage_root, schema):
    if not isinstance(row, dict) or not isinstance(row.get("source_stage"), dict):
        return None
    stage = row["source_stage"]
    if stage.get("status") not in STAGED:
        return None
    file = _safe_file(row.get("candidate_path"), stage_root)
    return file if _exact_schema(file, schema) else None


def _stage_output(row, stage_root, output_key, schema):
    if not isinstance(row, dict):
        return None
    stage = row.get("source_stage")
    if not isinstance(stage, dict) or stage.get("status") not in STAGED:
        return None
    rel = stage.get("output_paths", {}).get(output_key)
    if not isinstance(rel, str):
        return None
    path = Path(rel)
    if path.is_absolute() or ".." in path.parts:
        return None
    file = _safe_file(stage_root / path, stage_root)
    return file if _exact_schema(file, schema) else None


def discover(collected):
    """Find compiler inputs with NO user file paths or historical seed files.

    v229 currently collects two of v191's generated files; permanent and
    v211's six-file manifest still require their original source producers.
    The v260 structural tier output is NOT silently rebranded as v168.
    """
    if not isinstance(collected, dict) or collected.get("schema") != (
        "v216_fresh_source_stage_v1"):
        return {"schema": SCHEMA, "status": "COLLECTED_SOURCE_REQUIRED",
                "missing": list(NEEDED), "inputs": None, "network_calls": 0}
    snapshot = collected.get("snapshot_receipt_path")
    if not isinstance(snapshot, str):
        return {"schema": SCHEMA, "status": "COLLECTED_SOURCE_ROOT_PENDING",
                "missing": list(NEEDED), "inputs": None, "network_calls": 0}
    receipt = Path(snapshot).expanduser()
    if (receipt.name != "receipt.json" or receipt.parent.name != "wago" or
            not receipt.is_file() or receipt.is_symlink() or
            receipt.parent.is_symlink()):
        return {"schema": SCHEMA, "status": "COLLECTED_SOURCE_ROOT_PENDING",
                "missing": list(NEEDED), "inputs": None, "network_calls": 0}
    root = receipt.parent.parent.resolve()
    if not root.is_dir() or root.is_symlink():
        return {"schema": SCHEMA, "status": "COLLECTED_SOURCE_ROOT_PENDING",
                "missing": list(NEEDED), "inputs": None, "network_calls": 0}

    gear = _from_sealed_candidate(collected.get("fresh_ordinary_gear"),
                                  root, "v167_product_season_gear_db_v1")
    tier = _from_sealed_candidate(collected.get("fresh_tier"), root,
                                  tier_compiler.SCHEMA)
    consumable = collected.get("fresh_food_potion_item_sources")
    v189 = _stage_output(consumable, root, "v189",
             "v189_pinned_simc_effect_registration_candidates_v1")
    v190 = _from_sealed_candidate(consumable, root,
             "v190_same_build_consumable_item_candidates_v1")

    simc = collected.get("fresh_pinned_first_party_simc_source")
    source_dir = simc.get("source_dir") if isinstance(simc, dict) else None
    generated = Path(source_dir).expanduser() if isinstance(source_dir, str) else None
    if generated is not None:
        if (not generated.is_dir() or generated.is_symlink() or
                not generated.resolve().is_relative_to(root)):
            generated = None
    generated_files = {
        key: (_safe_file(generated / filename, root)
              if generated is not None else None)
        for key, filename in season_compiler.GENERATED.items()
    }
    # Read the ORIGINAL v229 receipt (small metadata only) for its exact
    # 40-char pinned revision; don't use a 7-char UI hint or historical build.
    revision = None
    if (generated is not None and isinstance(simc, dict) and
            isinstance(simc.get("source_stage"), dict) and
            simc["source_stage"].get("status") in STAGED):
        receipt_file = _safe_file(generated / "simc_seed_receipt.json", root)
        if receipt_file is not None and receipt_file.stat().st_size <= 200000:
            try:
                doc = json.loads(receipt_file.read_text(encoding="utf8"))
            except (OSError, ValueError, UnicodeError):
                doc = {}
            candidate = doc.get("simc_revision")
            if (doc.get("schema") ==
                    "v229_simc_only_first_party_source_seed_v1" and
                    doc.get("simc_generated_build") ==
                    collected.get("expected_game_build") and
                    doc.get("receipt_sha256") ==
                    simc.get("simc_receipt_sha256") and
                    isinstance(candidate, str) and len(candidate) == 40 and
                    all(ch in "0123456789abcdef" for ch in candidate)):
                revision = candidate
    v211 = collected.get("fresh_pinned_v211_source")
    v211_dir = (v211.get("source_dir") if isinstance(v211, dict)
                else None)
    v211_manifest = (v211.get("manifest_path") if isinstance(v211, dict)
                     else None)
    v211_manifest = _safe_file(v211_manifest, root)
    if (not isinstance(v211_dir, str) or not Path(v211_dir).is_dir() or
            Path(v211_dir).is_symlink() or
            not Path(v211_dir).resolve().is_relative_to(root)):
        v211_dir = None
    if (v211_dir is None or v211_manifest is None or
            not isinstance(v211, dict) or
            not isinstance(v211.get("source_stage"), dict) or
            v211["source_stage"].get("status") not in STAGED or
            any(_safe_file(Path(v211_dir) / name, root) is None
                for name in enchant_classifier.FRESH_REQUIRED)):
        v211_dir = None

    files = {"GEAR_V167": gear, "TIER_V168": tier,
             "V189": v189, "V190": v190,
             "GENERATED_PERMANENT": generated_files["permanent_enchant"],
             "GENERATED_TEMPORARY": generated_files["temporary_enchant"],
             "GENERATED_GEM": generated_files["gem_property"],
             "SIMC_V211_SIX_SOURCE_FILES_AND_MANIFEST": v211_manifest
                 if v211_dir is not None else None,
             "PINNED_SIMC_REVISION": revision}
    missing = [key for key in NEEDED if files[key] is None]
    if missing:
        return {
            "schema": SCHEMA, "status": "COLLECTED_COMPILER_INPUTS_PENDING",
            "missing": missing,
            "available": [key for key in NEEDED if key not in missing],
            "inputs": None, "network_calls": 0,
            "environment_ready": False,
        }
    return {
        "schema": SCHEMA, "status": "COLLECTED_COMPILER_INPUTS_COMPLETE",
        "missing": [], "available": list(NEEDED),
        "inputs": {
            "stage_root": root,
            "fresh_v191_inputs": {
                "gear": gear, "tier": tier, "v189": v189, "v190": v190,
                "simc_generated_folder": generated,
                "event": collected.get("simc_source_collection_context", {})
                          .get("requested_game_event", "season_change")},
            "simc_source_dir": Path(v211_dir).resolve(),
            "simc_manifest_path": v211_manifest,
            "expected_game_build": collected["expected_game_build"],
            "expected_simc_revision": revision,
        },
        "network_calls": 0, "environment_ready": False,
    }


def compile_collected(collected, *, compiler):
    """Run the EXISTING v241 once only when all original source types exist."""
    plan = discover(collected)
    if plan["inputs"] is None:
        return {k: v for k, v in plan.items() if k != "inputs"}
    compiled = compiler(**plan["inputs"])
    return {"schema": SCHEMA,
            "status": "FRESH_V191_V211_V213_COMPILED_UNADMITTED",
            "missing": [], "available": list(NEEDED),
            "source_catalog_path": compiled["source_catalog_path"],
            "stage_root": str(plan["inputs"]["stage_root"]),
            "v191_stage": compiled["v191_stage"],
            "v211_stage": compiled["v211_stage"],
            "v213_stage": compiled["v213_stage"],
            "simc_revision": plan["inputs"]["expected_simc_revision"],
            "environment_ready": False,
            "environment_installed": False,
            "additional_network_calls": 0, "native_calls": 0}
