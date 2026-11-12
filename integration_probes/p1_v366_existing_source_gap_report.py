"""Read-only v163/v274 season-gap report from EXISTING local JSON receipts.

Does not collect data, interpret WorldStateExpressionID, approve season
membership, run SimC, or modify inputs. Only explicitly requested equipment
IDs are included. The v163 equipment candidate domain excludes consumables.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

V163_SCHEMA = "v163_zero_seed_db2_join_v1"
V274_SCHEMA = "v274_v216_collected_to_v241_fresh_compile_inputs_v1"
PROGRESS_SCHEMA = "v216_zero_history_normal_build_progress_v1"
MAX_ITEM_IDS = 64
MAX_EVIDENCE_PER_ITEM = 32
MAX_FILE_BYTES = 25_000_000


class DiagnosticInputError(ValueError):
    pass


def read_existing_json(path: str) -> tuple[dict, str]:
    """Read one regular local JSON file, with SHA evidence and no path echo."""
    source = Path(path)
    if not source.is_file() or source.is_symlink():
        raise DiagnosticInputError("LOCAL_SOURCE_FILE_REQUIRED")
    size = source.stat().st_size
    if size <= 0 or size > MAX_FILE_BYTES:
        raise DiagnosticInputError("LOCAL_SOURCE_FILE_SIZE_INVALID")
    raw = source.read_bytes()
    try:
        doc = json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        raise DiagnosticInputError("LOCAL_SOURCE_JSON_INVALID") from exc
    if type(doc) is not dict:
        raise DiagnosticInputError("LOCAL_SOURCE_OBJECT_REQUIRED")
    return doc, hashlib.sha256(raw).hexdigest()


def summarize_gap(v163: dict, equipment_ids: list[int], *,
                  compilation: dict | None = None,
                  progress: dict | None = None) -> dict:
    """Summarize what a selected equipment ID still lacks, never admit it.

    Candidate absence means absent from THIS v163 raid/M+/craft index, not
    proof of absence from the season. J/F/O must be proven separately.
    """
    if type(v163) is not dict or v163.get("schema") != V163_SCHEMA:
        raise DiagnosticInputError("V163_CANDIDATE_SCHEMA_INVALID")
    if (type(equipment_ids) is not list or not equipment_ids or
            len(equipment_ids) > MAX_ITEM_IDS or
            any(type(x) is not int or x <= 0 for x in equipment_ids) or
            len(set(equipment_ids)) != len(equipment_ids)):
        raise DiagnosticInputError("SELECTED_EQUIPMENT_IDS_INVALID")
    if compilation is not None and (
            type(compilation) is not dict or
            compilation.get("schema") != V274_SCHEMA):
        raise DiagnosticInputError("V274_COMPILATION_SCHEMA_INVALID")
    if progress is not None and (
            type(progress) is not dict or
            progress.get("schema") != PROGRESS_SCHEMA):
        raise DiagnosticInputError("V216_PROGRESS_SCHEMA_INVALID")
    source_items = v163.get("items")
    if type(source_items) is not list:
        raise DiagnosticInputError("V163_ITEMS_INVALID")
    wanted = set(equipment_ids)
    indexed = {}
    for item in source_items:
        if type(item) is not dict:
            raise DiagnosticInputError("V163_ITEM_ROW_INVALID")
        iid = item.get("item_id")
        if type(iid) is int and iid in wanted:
            if iid in indexed:
                raise DiagnosticInputError("V163_DUPLICATE_SELECTED_ITEM")
            indexed[iid] = item
    rows = []
    for iid in equipment_ids:
        found = indexed.get(iid)
        proofs = []
        if found is not None:
            origins = found.get("acquisition_sources")
            if type(origins) is not list:
                raise DiagnosticInputError("V163_ACQUISITION_SOURCES_INVALID")
            if len(origins) > MAX_EVIDENCE_PER_ITEM:
                raise DiagnosticInputError("V163_SELECTED_SOURCE_ROWS_EXCEED_LIMIT")
            for origin in origins:
                if type(origin) is not dict:
                    raise DiagnosticInputError("V163_ACQUISITION_ROW_INVALID")
                # Safe allowlist: do not propagate arbitrary original contents.
                proofs.append({k: origin[k] for k in (
                    "source", "season_evidence", "display_season_id",
                    "world_state_expression_id", "classification")
                    if k in origin and type(origin[k]) in (int, str)})
        unresolved = sorted({p["world_state_expression_id"]
            for p in proofs if p.get("season_evidence") ==
            "UNKNOWN_WORLD_STATE_EXPRESSION" and
            type(p.get("world_state_expression_id")) is int and
            p["world_state_expression_id"] > 0})
        rows.append({"item_id": iid,
                     "v163_candidate_present": found is not None,
                     "season_membership_verified": False,
                     "state": ("SOURCE_CANDIDATE_ONLY_MEMBERSHIP_UNVERIFIED"
                               if found is not None else
                               "NOT_IN_V163_EQUIPMENT_CANDIDATE_NOT_ABSENCE_PROOF"),
                     "acquisition_evidence": proofs,
                     "uninterpreted_positive_world_state_ids": unresolved})
    missing = compilation.get("missing") if compilation is not None else None
    if missing is not None and (
            type(missing) is not list or
            any(type(x) is not str for x in missing)):
        raise DiagnosticInputError("V274_MISSING_INPUTS_INVALID")
    requires = progress.get("requires") if progress is not None else None
    if requires is not None and (
            type(requires) is not list or
            any(type(x) is not str for x in requires)):
        raise DiagnosticInputError("V216_PROGRESS_REQUIRES_INVALID")
    return {
        "schema": "p1_v366_existing_season_join_gap_report_v1",
        "status": "SOURCE_GAP_DIAGNOSTIC_ONLY_NOT_ADMITTED",
        "build": v163.get("build") if type(v163.get("build")) is str else None,
        "db2_display_season_id": v163.get("db2_display_season_id"),
        "wcl_zone_ids": {k: v for k, v in
            (v163.get("wcl_zone_ids") or {}).items()
            if k in ("raid", "mplus") and type(v) is int}
            if type(v163.get("wcl_zone_ids")) is dict else {},
        "v163_unverified_world_state_expressions":
            v163.get("unverified_world_state_expressions"),
        "selected_equipment": rows,
        "v274_compiler_input_files_missing": missing,
        "v216_stage_requirements": requires,
        "compiler_missing_is_not_season_membership_evidence": True,
        "v163_candidate_absence_is_not_season_absence": True,
        "consumable_J_F_O_not_in_v163_equipment_scope": True,
        "season_membership_verified": False,
        "environment_ready": False,
        "new_native_calls": 0,
        "new_network_calls": 0,
        "credentials_read": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v163-json", required=True)
    parser.add_argument("--equipment-id", type=int, action="append", required=True)
    parser.add_argument("--v274-json")
    parser.add_argument("--v216-progress-json")
    args = parser.parse_args(argv)
    try:
        v163, v163_sha = read_existing_json(args.v163_json)
        v274, v274_sha = (read_existing_json(args.v274_json)
            if args.v274_json else (None, None))
        progress, progress_sha = (read_existing_json(args.v216_progress_json)
            if args.v216_progress_json else (None, None))
        result = summarize_gap(v163, args.equipment_id,
                               compilation=v274, progress=progress)
        result["existing_input_sha256"] = {
            "v163": v163_sha, "v274": v274_sha, "v216_progress": progress_sha}
    except DiagnosticInputError as exc:
        print(json.dumps({"status": "DIAGNOSTIC_INPUT_BLOCKED",
                          "code": str(exc), "environment_ready": False}))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
