#!/usr/bin/env python3
"""Real saved-evidence v155 + v163 + v162 -> v158 zero-seed acceptance.

This stage reads three pre-existing JSON reports only. Never fetches the
network, uses an old item DB, or launches SimulationCraft. Source artifacts
are ephemeral; a small receipt can be kept without persisting the full pool.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v158_source_first_season_catalog as catalog

SCHEMA = "v164_saved_evidence_season_index_acceptance_v1"
MAX_SOURCE_BYTES = 5_000_000

class AcceptanceBlocked(ValueError):
    pass

def require(ok, code):
    if not ok:
        raise AcceptanceBlocked(code)

def load(path):
    require(path.is_file() and 0 < path.stat().st_size <= MAX_SOURCE_BYTES,
            "SOURCE_FILE_MISSING_OR_TOO_LARGE")
    raw = path.read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()

def compose(season, db2, delve, *, sha256=None):
    require(season.get("schema") == "v155_season_discovery_provider_probe_v1"
            and season.get("mode") == "LIVE_AUTHENTICATED_BOUNDED",
            "ACTUAL_SEASON_EVIDENCE_REQUIRED")
    require(db2.get("schema") == "v163_zero_seed_db2_join_v1"
            and db2.get("source_provider") == "WAGO_TOOLS_PINNED_DB2_WCL_LIVE",
            "DB2_JOIN_REPORT_REQUIRED")
    require(delve.get("schema") == "v162_localbots_delve_source_v1"
            and delve.get("source_provider") == "Localbots / balovich-matje/localbots",
            "TRUSTED_DELVE_REPORT_REQUIRED")
    require(db2.get("build") == delve.get("db2_build") and
            isinstance(db2.get("build"), str) and db2["build"],
            "PROVIDER_BUILD_MISMATCH")
    require(type(db2.get("db2_expansion_id")) is int
            and db2["db2_expansion_id"] == delve.get("db2_expansion_id"),
            "PROVIDER_EXPANSION_MISMATCH")
    require(type(db2.get("mapped_raid_bosses")) is int
            and db2["mapped_raid_bosses"] == db2.get("wcl_raid_bosses"),
            "RAID_MAPPING_PARTIAL")
    require(type(db2.get("mapped_mplus_dungeons")) is int
            and db2["mapped_mplus_dungeons"] == db2.get("wcl_mplus_dungeons"),
            "MPLUS_MAPPING_PARTIAL")
    require(type(db2.get("items")) is list
            and type(delve.get("items")) is list,
            "PROVIDER_ITEMS_INVALID")
    result = catalog.ingest([season, db2, delve])

    db2_ids = {x["item_id"] for x in db2["items"]}
    delve_ids = {x["item_id"] for x in delve["items"]}
    require(len(db2_ids) == len(db2["items"]), "DB2_DUPLICATE_ITEM_ROW")
    require(len(delve_ids) == len(delve["items"]), "DELVE_DUPLICATE_ITEM_ROW")
    require(result["item_ids"] == sorted(db2_ids | delve_ids),
            "INTEGRATED_ITEM_IDS_MISMATCH")
    require(result.get("simc_native_calls") == 0
            and result.get("old_item_catalog_imported") is False
            and result.get("full_season_completeness_confirmed") is False,
            "INDEX_BOUNDARY_VIOLATED")

    by_id = {x["item_id"]: x["acquisition_sources"] for x in result["items"]}
    for item in db2["items"]:
        for source in item["acquisition_sources"]:
            matches = [p for p in by_id[item["item_id"]]
                       if p["source"] == "wago_db2_" + source["source"]
                       and p["season_evidence"] ==
                           source.get("season_evidence", source.get("classification"))]
            require(matches, "DB2_SEASON_EVIDENCE_LOST")
    for item in delve["items"]:
        require(any(p["source"] == "localbots_delve_pool"
                    and p["kind"] == "delve" for p in by_id[item["item_id"]]),
                "DELVE_PROVENANCE_LOST")

    evidence = Counter(p["season_evidence"]
        for item in result["items"] for p in item["acquisition_sources"]
        if p["source"].startswith("wago_db2_"))
    kinds = Counter(p["source"]
        for item in result["items"] for p in item["acquisition_sources"])
    receipt = {
        "schema": SCHEMA,
        "status": "REAL_SAVED_PROVIDER_REPORTS_COMPOSED",
        "db2_build": db2["build"],
        "db2_expansion_id": db2["db2_expansion_id"],
        "blizzard_keystone_season_id":
            result["season_data"].get("blizzard_keystone_season_id"),
        "db2_display_season_id": db2["db2_display_season_id"],
        "wcl_raid_bosses": db2["mapped_raid_bosses"],
        "wcl_mplus_dungeons": db2["mapped_mplus_dungeons"],
        "source_unique_item_ids": {"wago_db2": len(db2_ids),
                                   "localbots_delve": len(delve_ids)},
        "cross_source_overlap_ids": len(db2_ids & delve_ids),
        "integrated_unique_item_ids": result["observed_unique_item_ids"],
        "source_provenance_records": dict(sorted(kinds.items())),
        "db2_season_evidence_records": dict(sorted(evidence.items())),
        "unknown_provider_fields": len(result["unresolved_provider_fields"]),
        "full_season_completeness_confirmed": False,
        "wse_meaning_certified": False,
        "special_effects_classified": False,
        "old_item_catalog_imported": False,
        "new_api_calls": 0,
        "simc_native_calls": 0
    }
    if sha256 is not None:
        receipt["source_report_sha256"] = dict(sorted(sha256.items()))
    return result, receipt

def main(argv=None):
    p = argparse.ArgumentParser(description="Compose saved v155/v163/v162 provider evidence without new queries")
    p.add_argument("--season", type=Path, required=True)
    p.add_argument("--db2", type=Path, required=True)
    p.add_argument("--delve", type=Path, required=True)
    p.add_argument("--out-index", type=Path, required=True)
    p.add_argument("--out-receipt", type=Path, required=True)
    a = p.parse_args(argv)
    try:
        require(a.out_index.resolve() != a.out_receipt.resolve(),
                "OUTPUT_PATHS_MUST_DIFFER")
        season, s_sha = load(a.season)
        db2, w_sha = load(a.db2)
        delve, d_sha = load(a.delve)
        index, receipt = compose(season, db2, delve,
                                 sha256={"v155": s_sha, "v163": w_sha, "v162": d_sha})
        for path, value in ((a.out_index, index), (a.out_receipt, receipt)):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value, ensure_ascii=False,
                            sort_keys=True, indent=2) + "\n", encoding="utf8")
        print(json.dumps({"status": receipt["status"],
                          "item_ids": receipt["integrated_unique_item_ids"],
                          "overlap": receipt["cross_source_overlap_ids"],
                          "native": 0, "api": 0}, sort_keys=True))
        return 0
    except (AcceptanceBlocked, catalog.CatalogBlocked, ValueError,
            OSError, KeyError, TypeError) as e:
        code = str(e) if isinstance(e, (AcceptanceBlocked,catalog.CatalogBlocked)) else type(e).__name__
        print(json.dumps({"status": "BLOCKED", "code": code}), file=sys.stderr)
        return 3

if __name__ == "__main__":
    raise SystemExit(main())
