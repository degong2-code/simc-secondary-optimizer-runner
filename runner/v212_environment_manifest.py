#!/usr/bin/env python3
"""v212: deterministic, no-Native Environment Manifest assembler.

This is a narrow artifact/provenance join, not a collector, profile generator,
UI publisher, or optimizer. It references existing v191/v211/v196/v098 outputs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

SCHEMA = "v212_simc_environment_manifest_v1"
V191 = "v191_unified_patch_season_expansion_data_candidates_v1"
V211 = "v211_current_season_enchant_effect_classification_v1"
V196 = "v196_current_season_ui_catalog_v1"
V098 = "v098_target_ilevel_user_scenario_v1"


class EnvironmentBlocked(ValueError):
    pass


def need(condition, code):
    if not condition:
        raise EnvironmentBlocked(code)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_json(path, max_bytes=25_000_000):
    path = Path(path).resolve()
    need(path.is_file() and 0 < path.stat().st_size <= max_bytes,
         "INPUT_FILE_MISSING_OR_SIZE_INVALID:" + path.name)
    raw = path.read_bytes()
    try:
        return json.loads(raw.decode("utf8")), sha(raw)
    except (UnicodeError, ValueError) as exc:
        raise EnvironmentBlocked("INPUT_JSON_INVALID:" + path.name) from exc


def sha_file(path):
    path = Path(path).resolve()
    need(path.is_file(), "RUNTIME_BINARY_OR_CACHE_MISSING:" + path.name)
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            size += len(chunk)
            digest.update(chunk)
    return {"basename": path.name, "size_bytes": size,
            "sha256": digest.hexdigest()}


def file_identity(path, root):
    path = Path(path).resolve()
    root = Path(root).resolve()
    need(path.is_file(), "TARGET_PROFILE_FILE_MISSING:" + path.name)
    try:
        relative = path.relative_to(root).as_posix()
    except ValueError as exc:
        raise EnvironmentBlocked("TARGET_PROFILE_FILE_ESCAPES_ROOT") from exc
    raw = path.read_bytes()
    return {"path": relative, "size_bytes": len(raw), "sha256": sha(raw)}


def compile_manifest(season, season_sha, enchants, enchants_sha,
                     ui, ui_sha, bootstrap, bootstrap_sha, target_root):
    need(season.get("schema") == V191 and season.get("source_first") is True
         and season.get("automatic_ui_promotion") is False
         and season.get("native_calls") == 0,
         "V191_SOURCE_CANDIDATE_CONTRACT_INVALID")
    need(enchants.get("schema") == V211
         and enchants.get("automatic_ui_promotion") is False
         and enchants.get("native_calls") == 0
         and enchants.get("simc_effect_reimplemented") is False,
         "V211_SOURCE_CLASSIFICATION_CONTRACT_INVALID")
    need(ui.get("schema") == V196,
         "V196_APPROVED_CATALOG_SCHEMA_INVALID")
    need(bootstrap.get("schema") == V098
         and bootstrap.get("native_calls") == 0
         and bootstrap.get("status") == "READY_INTERNAL_MANIFEST_ZERO_NATIVE",
         "V098_TARGET_PROFILE_NOT_PLAN_READY")
    build = season.get("game_build")
    revision = season.get("simc_revision")
    need(type(build) is str and bool(build)
         and enchants.get("season_game_build") == build
         and ui.get("season_build") == build,
         "ENVIRONMENT_GAME_BUILD_MISMATCH")
    need(type(revision) is str and len(revision) == 40
         and enchants.get("simc_commit") == revision
         and ui.get("simc_revision") == revision,
         "ENVIRONMENT_SIMC_REVISION_MISMATCH")
    need(enchants.get("counts", {}).get("total") == 38
         and len(enchants.get("rows", [])) == 38
         and ui.get("enchant_candidates", {}).get("total") == 38,
         "ENVIRONMENT_ENCHANT_CATALOG_COVERAGE_MISMATCH")
    need(ui.get("enchant_candidates", {}).get("selectable_count") == 1,
         "ENVIRONMENT_UI_APPROVAL_BOUNDARY_CHANGED")
    need(bootstrap.get("all_specs_ready") is False,
         "V098_ARCHETYPE_SCOPE_FLAG_MISSING")
    target_root = Path(target_root).resolve()
    generated = Path(bootstrap.get("generated_manifest", "")).resolve()
    need(generated.parent == target_root and generated.name == "manifest.json",
         "V098_GENERATED_MANIFEST_OUTSIDE_TARGET_ROOT")
    profile_files = {}
    for name in ("manifest.json", "profile.simc", "scenario.json", "fillers.json"):
        profile_files[name] = file_identity(target_root / name, target_root)
    target_manifest, target_manifest_sha = read_json(generated)
    need(target_manifest.get("profile_simc") == "profile.simc"
         and target_manifest.get("scenario_json") == "scenario.json"
         and target_manifest.get("fillers_json") == "fillers.json",
         "V098_PROFILE_MANIFEST_FILE_BINDING_INVALID")
    need(target_manifest.get("native_limit") == 6
         and target_manifest.get("native_revision") == revision,
         "V098_ADAPTIVE_LIMIT_OR_SIMC_REVISION_CHANGED")
    binary = sha_file(target_manifest.get("native_binary", ""))
    static_cache = target_manifest.get("static_cache_json")
    static_cache_identity = (sha_file(static_cache)
                             if static_cache else None)
    # Hash a machine-independent projection; do not leak local absolute paths.
    target_manifest_identity = {
        "profile_simc": target_manifest["profile_simc"],
        "scenario_json": target_manifest["scenario_json"],
        "fillers_json": target_manifest["fillers_json"],
        "native_revision": target_manifest["native_revision"],
        "native_limit": target_manifest["native_limit"],
        "weapon_layout": target_manifest.get("weapon_layout"),
        "oil_hands": target_manifest.get("oil_hands"),
        "flask_F": target_manifest.get("flask_F"),
        "seed_targets_B": target_manifest.get("seed_targets_B"),
        "static_cache_sha256": (static_cache_identity["sha256"]
                                if static_cache_identity else None),
    }
    target_manifest_identity_sha = sha(
        canonical(target_manifest_identity).encode("utf8"))
    plan = bootstrap.get("plan")
    need(type(plan) is dict and type(plan.get("base_B")) is int
         and type(plan.get("final_T")) is int,
         "V098_TARGET_BUDGET_PLAN_MISSING")
    archetype = bootstrap.get("template_archetype")
    target_ilevel = bootstrap.get("target_ilevel")
    need(type(archetype) is str and type(target_ilevel) is int,
         "V098_TARGET_IDENTITY_MISSING")
    bootstrap_identity = {
        "schema": bootstrap["schema"],
        "status": bootstrap["status"],
        "template_archetype": archetype,
        "target_ilevel": target_ilevel,
        "base_B": plan["base_B"],
        "final_T": plan["final_T"],
        "native_calls": bootstrap["native_calls"],
    }
    bootstrap_identity_sha = sha(canonical(bootstrap_identity).encode("utf8"))
    limitations = []
    if bootstrap.get("all_specs_ready") is not True:
        limitations.append("V098_REPRESENTATIVE_ARCHETYPE_COVERAGE_INCOMPLETE")
    if ui.get("enchant_candidates", {}).get("selectable_count") != 38:
        limitations.append("ENCHANT_CATALOG_DISCOVERY_EXCEEDS_USER_APPROVAL")
    if ui.get("enchant_candidates", {}).get("source_classification_counts", {}).get(
            "native_E_measured", 0) < 38:
        limitations.append("ENCHANT_SOURCE_CLASSIFICATION_IS_NOT_GENERAL_NATIVE_E")
    payload = {
        "schema": SCHEMA,
        "status": "READY_WITH_LIMITATIONS" if limitations else "READY",
        "native_calls": 0,
        "network_calls": 0,
        "automatic_ui_promotion": False,
        "season_source": {
            "schema": season["schema"], "game_build": build,
            "simc_revision": revision, "sha256": season_sha,
            "native_calls": season["native_calls"],
        },
        "enchant_source_classification": {
            "schema": enchants["schema"], "season_game_build": build,
            "simc_commit": revision, "sha256": enchants_sha,
            "source_files": enchants.get("source_files"),
            "counts": enchants.get("counts"),
            "native_calls": enchants["native_calls"],
        },
        "approved_ui_catalog": {
            "schema": ui["schema"], "season_build": build,
            "simc_revision": revision, "sha256": ui_sha,
            "selectable_enchant_count":
                ui["enchant_candidates"]["selectable_count"],
            "enchant_count": ui["enchant_candidates"]["total"],
        },
        "target_profile": {
            "schema": bootstrap["schema"],
            "normalized_result_sha256": bootstrap_identity_sha,
            "template_archetype": archetype,
            "target_ilevel": target_ilevel,
            "base_B": plan["base_B"], "final_T": plan["final_T"],
            "generated_manifest_sha256": target_manifest_identity_sha,
            "runtime_binary": binary,
            "static_cache": static_cache_identity,
            "profile_files": profile_files,
            "native_calls": bootstrap["native_calls"],
        },
        "readiness_limitations": limitations,
        "unresolved_dependencies": [
            "V191_TO_V196_SINGLE_VERSIONED_ARTIFACT_HANDOFF",
            "ALL_26_DPS_REPRESENTATIVE_PROFILE_SUPPLIERS",
            "WINDOWS_ONE_CLICK_BUILD_START_PROGRESS_CANCEL_RESUME",
        ],
    }
    digest = sha(canonical(payload).encode("utf8"))
    return {**payload, "manifest_sha256": digest}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("season-catalog", "enchant-classification",
                 "ui-catalog", "bootstrap-result", "target-root", "out"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        season, season_sha = read_json(args.season_catalog)
        enchants, enchants_sha = read_json(args.enchant_classification)
        ui, ui_sha = read_json(args.ui_catalog)
        bootstrap, bootstrap_sha = read_json(args.bootstrap_result)
        result = compile_manifest(
            season, season_sha, enchants, enchants_sha, ui, ui_sha,
            bootstrap, bootstrap_sha, args.target_root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("V212_ENVIRONMENT_BUILD_BLOCKED", type(exc).__name__, str(exc))
        return 3
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(result, sort_keys=True, ensure_ascii=False,
                         indent=2, allow_nan=False) + "\n"
    if out.exists():
        need(out.read_text("utf8") == encoded,
             "EXISTING_ENVIRONMENT_MANIFEST_CHANGED")
    else:
        out.write_text(encoded, encoding="utf8")
    print("V212_ENVIRONMENT_MANIFEST_PASS", result["status"],
          result["manifest_sha256"], "NATIVE_0", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
