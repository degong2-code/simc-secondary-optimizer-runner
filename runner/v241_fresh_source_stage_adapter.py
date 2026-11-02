#!/usr/bin/env python3
"""v241: receipt-backed bridge for EXISTING fresh v191 -> v211 -> v213.

Only a stage adapter inside the original v216 Build coordinator. This does
not collect source bytes, authorize old J/F/E, install an environment or
run Native. Source fetch/identity is owned by the normal upstream collectors.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import v191_unified_season_data_update as v191
import v211_enchant_source_effect_classification as v211
import v213_source_to_catalog as v213
import v217_stage_execution_engine as stages

MAX_V191_BYTES = 25_000_000
MAX_MANIFEST_BYTES = 1_000_000


def require(ok, code):
    if not ok:
        raise stages.StageExecutionBlocked(code)


def raw_file(path, limit):
    path = Path(path).expanduser()
    require(path.is_file() and not path.is_symlink()
            and 0 < path.stat().st_size <= limit,
            "FRESH_STAGE_INPUT_MISSING_OR_TOO_LARGE")
    return path.read_bytes()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(doc):
    return json.dumps(doc, ensure_ascii=False, sort_keys=True,
                      indent=2, allow_nan=False) + "\n"


def source_inputs(v191_path, simc_source_dir, simc_manifest_path,
                  *, expected_game_build, expected_simc_revision):
    """Pin all input bytes BEFORE any stage receipt/output is written."""
    season_raw = raw_file(v191_path, MAX_V191_BYTES)
    manifest_raw = raw_file(simc_manifest_path, MAX_MANIFEST_BYTES)
    season = json.loads(season_raw)
    manifest = json.loads(manifest_raw)
    require(type(season) is dict and type(manifest) is dict,
            "FRESH_STAGE_INPUT_OBJECT_REQUIRED")
    require(season.get("game_build") == expected_game_build
            and season.get("simc_revision") == expected_simc_revision
            and manifest.get("game_build") == expected_game_build
            and manifest.get("simc_revision") == expected_simc_revision,
            "FRESH_STAGE_INDEPENDENT_BUILD_MISMATCH")
    inp = season.get("sha256_by_input")
    consumables = season.get("consumables", {})
    require(season.get("source_budget_state")
            == "NEW_SEASON_J_F_EVIDENCE_PENDING"
            and type(inp) is dict and inp.get("budget", "MISSING") is None
            and consumables.get("flask", {}).get("reference", "MISSING") is None
            and consumables.get("general_gems", {}).get(
                "reference", "MISSING") is None,
            "FRESH_STAGE_HISTORIC_BUDGET_FORBIDDEN")
    require(manifest.get("schema") == v211.FRESH_SOURCE_SCHEMA
            and type(manifest.get("files")) is dict
            and set(manifest["files"]) == set(v211.FRESH_REQUIRED),
            "FRESH_STAGE_SIMC_MANIFEST_INVALID")
    folder = Path(simc_source_dir).expanduser()
    require(folder.is_dir() and not folder.is_symlink(),
            "FRESH_STAGE_SIMC_SOURCE_DIR_REQUIRED")
    file_shas = {}
    for name in v211.FRESH_REQUIRED:
        raw = raw_file(folder / name, v211.MAX_SOURCE)
        row = manifest["files"][name]
        require(type(row) is dict and row.get("sha256") == sha(raw)
                and row.get("size_bytes") == len(raw),
                "FRESH_STAGE_SOURCE_SHA_MISMATCH:" + name)
        file_shas[name] = sha(raw)
    return season, manifest, {
        "v191_sha256": sha(season_raw),
        "manifest_sha256": sha(manifest_raw),
        "source_sha256": file_shas,
        "expected_build": expected_game_build,
        "expected_revision": expected_simc_revision,
    }



def compile_fresh_v191_stage(*, stage_root, fresh_v191_inputs,
                            expected_game_build, expected_simc_revision):
    """Run the ORIGINAL v191 compiler from explicit new-source files.

    No legacy --budget/default-source fallback: --fresh-budget-pending is
    mandatory. This stage never downloads anything or reads installed season
    references; normal upstream collectors must supply these inputs.
    """
    require(type(fresh_v191_inputs) is dict
            and set(fresh_v191_inputs) == {
                "gear", "tier", "v189", "v190",
                "simc_generated_folder", "event"},
            "FRESH_V191_INPUT_CONTRACT_INVALID")
    event = fresh_v191_inputs["event"]
    require(event in ("season_change", "expansion_change", "mid_patch"),
            "FRESH_V191_EVENT_INVALID")
    root = Path(stage_root).expanduser()
    require(root.is_dir() and not root.is_symlink(),
            "FRESH_STAGE_WORKSPACE_REQUIRED")
    pinned = {}
    for key in ("gear", "tier", "v189", "v190"):
        pinned[key] = sha(raw_file(fresh_v191_inputs[key], v191.MAX_FILE))
    generated = Path(fresh_v191_inputs["simc_generated_folder"]).expanduser()
    require(generated.is_dir() and not generated.is_symlink(),
            "FRESH_V191_GENERATED_SOURCE_DIR_REQUIRED")
    for key, filename in v191.GENERATED.items():
        pinned["generated_" + key] = sha(
            raw_file(generated / filename, v191.MAX_FILE))
    code = stages.module_dependency_fingerprint(
        [Path(__file__), Path(v191.__file__)])
    output = "fresh_source/v191_candidate.json"
    target = root / output

    def execute():
        arguments = []
        for key in ("gear", "tier", "v189", "v190"):
            arguments.extend(["--" + key, str(fresh_v191_inputs[key])])
        arguments.extend([
            "--simc-generated-folder", str(generated),
            "--fresh-budget-pending", "--event", event,
            "--out", str(target)])
        require(v191.main(arguments) == 0, "FRESH_V191_COMPILER_BLOCKED")

    def validate(paths):
        doc = json.loads(paths["candidate"].read_text(encoding="utf8"))
        budget = doc.get("sha256_by_input", {})
        cons = doc.get("consumables", {})
        return (
            doc.get("schema") == v191.SCHEMA
            and doc.get("game_build") == expected_game_build
            and doc.get("simc_revision") == expected_simc_revision
            and doc.get("source_budget_state") ==
                "NEW_SEASON_J_F_EVIDENCE_PENDING"
            and type(budget) is dict
            and budget.get("budget", "MISSING") is None
            and all(budget.get(k) == pinned[k]
                    for k in ("gear", "tier", "v189", "v190"))
            and cons.get("flask", {}).get("reference", "MISSING") is None
            and cons.get("general_gems", {}).get(
                "reference", "MISSING") is None
            and doc.get("environment_ready") is False)
    result = stages.execute_stage(
        root=root, stage_id="fresh-v191", stage_version="1",
        inputs={**pinned, "event": event,
                "expected_build": expected_game_build,
                "expected_revision": expected_simc_revision,
                "code_sha256": code["sha256"]},
        outputs={"candidate": output}, execute=execute, validate=validate)
    return str(target.resolve()), {
        k: v for k, v in result.items() if k != "result"}


def compile_fresh_candidate(*, stage_root, simc_source_dir,
                            simc_manifest_path, expected_game_build,
                            expected_simc_revision, v191_path=None,
                            fresh_v191_inputs=None):
    """Reuse v217 stages; never read installed-season data or caches.

    root must be an existing, dedicated build-source workspace outside the
    product session/cache root. Input identity changes fail closed; a new
    season must use a distinct stage root rather than overwriting receipts.
    """
    root = Path(stage_root).expanduser()
    require(root.is_dir() and not root.is_symlink(),
            "FRESH_STAGE_WORKSPACE_REQUIRED")
    require((v191_path is None) != (fresh_v191_inputs is None),
            "FRESH_V191_EXACTLY_ONE_INPUT_MODE_REQUIRED")
    first_stage = None
    if fresh_v191_inputs is not None:
        v191_path, first_stage = compile_fresh_v191_stage(
            stage_root=root, fresh_v191_inputs=fresh_v191_inputs,
            expected_game_build=expected_game_build,
            expected_simc_revision=expected_simc_revision)
    season, manifest, identity = source_inputs(
        v191_path, simc_source_dir, simc_manifest_path,
        expected_game_build=expected_game_build,
        expected_simc_revision=expected_simc_revision)
    code_identity = stages.module_dependency_fingerprint(
        [Path(__file__), Path(v211.__file__), Path(v213.__file__)])
    base_inputs = {**identity, "code_sha256": code_identity["sha256"]}
    first_rel = "fresh_source/v211_classification.json"
    second_rel = "fresh_source/v213_candidate_catalog.json"
    first = root / first_rel
    second = root / second_rel

    def execute_v211():
        classified = v211.compile_fresh_season(
            season, simc_source_dir, manifest)
        first.parent.mkdir(parents=True, exist_ok=True)
        first.write_text(encode(classified), encoding="utf8")

    def validate_v211(paths):
        doc = json.loads(paths["classification"].read_text(encoding="utf8"))
        return (doc.get("source_manifest_sha256") ==
                v211.sha256(v211.canonical(manifest).encode("utf8"))
                and doc.get("season_game_build") == expected_game_build
                and doc.get("simc_commit") == expected_simc_revision
                and doc.get("counts", {}).get("user_selectable_existing_scope") == 0
                and doc.get("counts", {}).get("native_E_measured") == 0)

    one = stages.execute_stage(
        root=root, stage_id="fresh-v211", stage_version="1",
        inputs=base_inputs, outputs={"classification": first_rel},
        execute=execute_v211, validate=validate_v211)
    classified_raw = raw_file(first, MAX_V191_BYTES)
    classified = json.loads(classified_raw)

    def execute_v213():
        joined = v213.compile_catalog(
            season, identity["v191_sha256"], classified, sha(classified_raw))
        v213.verify_catalog(joined)
        second.parent.mkdir(parents=True, exist_ok=True)
        second.write_text(encode(joined), encoding="utf8")

    def validate_v213(paths):
        artifact = json.loads(paths["candidate"].read_text(encoding="utf8"))
        return v213.verify_catalog(artifact) is True

    two = stages.execute_stage(
        root=root, stage_id="fresh-v213", stage_version="1",
        inputs={**base_inputs, "v211_output_sha256": sha(classified_raw)},
        outputs={"candidate": second_rel},
        execute=execute_v213, validate=validate_v213)
    return {
        "source_catalog_path": str(second.resolve()),
        "v191_stage": first_stage,
        "v211_stage": {k: v for k, v in one.items() if k != "result"},
        "v213_stage": {k: v for k, v in two.items() if k != "result"},
        "status": "FRESH_SOURCE_CANDIDATE_UNAPPROVED_GJFO_PENDING",
        "network_calls_by_adapter": 0,
        "native_calls_by_adapter": 0,
        "environment_installed": False,
        "upstream_fetch_authenticated_by_adapter": False,
    }
