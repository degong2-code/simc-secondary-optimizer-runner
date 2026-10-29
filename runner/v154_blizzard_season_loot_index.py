#!/usr/bin/env python3
"""Bounded Blizzard encounter loot-ID discovery vs existing MID2 evidence.

Data-adapter ONLY, separate from the P1 user optimization runtime.
An encounter's boss-loot IDs are not a season-complete catalog or SimC L.
The Blizzard credential, when used, is read from the environment and never
written to disk. Missing JSON loot fields are UNKNOWN, not an empty drop pool.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request

SCHEMA = "v154_bounded_blizzard_loot_to_existing_reference_v1"
ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "integration_probes/catalog/v047_wequip_20260920_395_metadata_only.json"
DELTA = ROOT / "integration_probes/catalog/v046_mids2_1215_partial_10.json"
MAX_ENCOUNTERS = 48
KINDS = {"raid", "mplus", "delve"}

class LootBlocked(ValueError):
    pass

def need(ok, reason):
    if not ok:
        raise LootBlocked(reason)

def read_json(path):
    p = Path(path)
    need(p.is_file() and p.stat().st_size <= 8_000_000, "JSON_FILE_MISSING_OR_TOO_LARGE")
    return json.loads(p.read_text(encoding="utf8"))

def existing_reference(master, delta):
    """Only real checked-in item IDs and hints; never promote spell candidates."""
    need(master.get("schema") == "v047_wequip_snapshot_identity_census_v1"
         and master.get("scaled_stats_imported") is False,
         "EXISTING_MASTER_SCHEMA")
    need(delta.get("completeness") == "PARTIAL_10_ONLY_NOT_WEQUIP_MASTER_EXPORT"
         and delta.get("item_stats_from_source") == "NOT_INCLUDED_NOT_SIMC_VERIFIED",
         "EXISTING_DELTA_SCHEMA")
    by_id = {}
    source_count = 0
    for entry in master["source_records"]:
        item_id = entry["item_id"]
        need(type(item_id) is int and item_id > 0, "REFERENCE_ITEM_ID")
        ref = by_id.setdefault(item_id, {
            "item_id": item_id, "name": entry["name"], "source_classes": [],
            "known_effect_candidate": False, "delta_special_armor": False})
        kind = entry["record_id"].partition(":")[0]
        if kind not in ref["source_classes"]:
            ref["source_classes"].append(kind)
        ref["known_effect_candidate"] |= (entry["spell_bearing_candidate"] is True)
        source_count += 1
    need(source_count == master["source_qualified_count"]
         and len(by_id) == master["distinct_item_ids"],
         "REFERENCE_COUNTS_DRIFT")
    for entry in delta["items"]:
        item_id = entry["item_id"]
        need(type(item_id) is int and item_id > 0, "DELTA_ITEM_ID")
        ref = by_id.setdefault(item_id, {
            "item_id": item_id, "name": entry["name_en"],
            "source_classes": [], "known_effect_candidate": False,
            "delta_special_armor": False})
        kind = entry["source_type"].lower()
        if kind not in ref["source_classes"]:
            ref["source_classes"].append(kind)
        if entry.get("category") == "SPECIAL_EFFECT_ARMOR":
            ref["delta_special_armor"] = True
    for item in by_id.values():
        item["source_classes"].sort()
    return {"source_rows": source_count, "master_distinct_ids":
            master["distinct_item_ids"], "delta_rows": len(delta["items"]),
            "known": by_id}

def selected_encounters(selection):
    need(type(selection) is dict and type(selection.get("encounters")) is list,
         "ENCOUNTER_SELECTION_REQUIRED")
    raw = selection["encounters"]
    need(1 <= len(raw) <= MAX_ENCOUNTERS, "ENCOUNTER_COUNT_LIMIT")
    rows = []
    seen = set()
    for item in raw:
        need(type(item) is dict and set(item) ==
             {"encounter_id", "instance_id", "kind"}, "ENCOUNTER_FIELDS")
        eid, inst, kind = item["encounter_id"], item["instance_id"], item["kind"]
        need(type(eid) is int and eid > 0 and
             type(inst) is int and inst > 0 and kind in KINDS,
             "ENCOUNTER_ID_OR_KIND")
        need(eid not in seen, "DUPLICATE_ENCOUNTER_ID")
        seen.add(eid)
        rows.append(dict(item))
    return rows

def encounter_loot(document, expected_id):
    """Return None if API does not expose loot, never turn absence into 0."""
    need(type(document) is dict, "JOURNAL_ENCOUNTER_OBJECT")
    need(document.get("id") == expected_id, "JOURNAL_ENCOUNTER_ID_MISMATCH")
    # The public API may present encounter item references in either field.
    # Do not recursively scan descriptions, spells, hrefs or arbitrary IDs.
    fields = [name for name in ("items", "loot") if name in document]
    if not fields:
        return None
    need(len(fields) == 1, "JOURNAL_LOOT_FIELD_AMBIGUOUS")
    values = document[fields[0]]
    need(type(values) is list and len(values) <= 400, "JOURNAL_LOOT_SHAPE")
    result = set()
    for row in values:
        need(type(row) is dict, "JOURNAL_LOOT_ROW")
        # Only explicitly item-scoped IDs; do not treat encounter ID,
        # spell ID or boss ID as loot.
        item = row.get("item", row)
        need(type(item) is dict and type(item.get("id")) is int
             and item["id"] > 0, "JOURNAL_LOOT_ITEM_ID_NOT_EXPLICIT")
        result.add(item["id"])
    return sorted(result)

def fetch_encounter(encounter_id, token, region="us"):
    need(region in ("us", "eu", "kr", "tw"), "REGION_NOT_ALLOWED")
    need(type(token) is str and bool(token.strip()), "BLIZZARD_TOKEN_REQUIRED")
    url = ("https://" + region + ".api.blizzard.com/data/wow/journal-encounter/"
           + str(encounter_id) + "?" +
           urllib.parse.urlencode({"namespace": "static-" + region,
                                   "locale": "en_US"}))
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + token, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as response:
        need(response.status == 200, "BLIZZARD_HTTP_STATUS")
        raw = response.read(1_000_001)
    need(len(raw) <= 1_000_000, "BLIZZARD_JSON_TOO_LARGE")
    return json.loads(raw)

def reconcile(reference, encounters, documents, *, fetch_mode="offline"):
    """Compare actual provider IDs with existing sources; no stats, no Native."""
    known = reference["known"]
    observed = {}
    unknown = []
    checked = 0
    for e in encounters:
        eid = e["encounter_id"]
        loot = encounter_loot(documents[eid], eid)
        if loot is None:
            unknown.append(eid)
            continue
        checked += 1
        for item_id in loot:
            r = observed.setdefault(item_id, {"item_id": item_id,
                   "encounters": [], "kinds": []})
            if eid not in r["encounters"]:
                r["encounters"].append(eid)
            if e["kind"] not in r["kinds"]:
                r["kinds"].append(e["kind"])
    rows = []
    for item_id in sorted(observed):
        row = observed[item_id]
        old = known.get(item_id)
        row["matched_existing"] = old is not None
        row["prior_spell_bearing_candidate"] = bool(
            old and old["known_effect_candidate"])
        row["prior_delta_special_armor"] = bool(
            old and old["delta_special_armor"])
        row["special_status"] = ("KNOWN_CANDIDATE_NEEDS_SIMC_EFFECT_HANDLING"
                  if row["prior_spell_bearing_candidate"] or
                  row["prior_delta_special_armor"] else
                  "UNCLASSIFIED_NOT_ASSERTED_NON_SPECIAL")
        row["name_if_existing"] = old["name"] if old else None
        row["encounters"].sort()
        row["kinds"].sort()
        rows.append(row)
    seen = set(observed)
    missing = sorted(set(known) - seen)
    return {
        "schema": SCHEMA,
        "status": "PROVIDER_BOUNDED_COMPARISON_PARTIAL" if unknown else
                  "PROVIDER_SELECTED_ENCOUNTERS_CHECKED_NOT_SEASON_COMPLETE",
        "source_mode": fetch_mode,
        "simc_native_calls": 0, "simc_effects_certified": False,
        "static_L_populated": False,
        "season_loot_complete": False,
        "reference": {"master_source_rows": reference["source_rows"],
                     "master_distinct_ids": reference["master_distinct_ids"],
                     "delta_source_rows": reference["delta_rows"],
                     "known_unique_ids_combined": len(known),
                     "known_effect_candidates": sum(
                        r["known_effect_candidate"] for r in known.values()),
                     "delta_special_armor_ids": sum(
                        r["delta_special_armor"] for r in known.values())},
        "provider": {"requested_encounters": len(encounters),
                     "checked_encounters_with_explicit_loot": checked,
                     "loot_field_unavailable_encounters": sorted(unknown),
                     "observed_unique_item_ids": len(rows),
                     "matched_existing_ids": len(seen & set(known)),
                     "not_in_existing_ids": len(seen - set(known)),
                     "prior_effect_candidates_found": sum(
                         r["prior_spell_bearing_candidate"] for r in rows),
                     "prior_delta_special_armor_found": sum(
                         r["prior_delta_special_armor"] for r in rows),
                     "existing_ids_not_observed_in_selected_encounters":
                         len(missing)},
        "observed_items": rows,
        "existing_not_observed_in_bounded_query": missing,
        "limitations": [
            "Only explicitly selected encounters, not the complete season",
            "Non-observation does NOT establish absence from current loot",
            "Missing encounter loot field means unknown, never empty loot",
            "Spell-bearing candidates are hints, not SimC effect certifications",
            "No itemlevel/options static L, trinket stat authority or DPS derived"]
    }

def reference_only(reference):
    return {"schema": SCHEMA, "status": "EXISTING_REFERENCE_ONLY_BLIZZARD_UNQUERIED",
            "simc_native_calls": 0, "blizzard_requests": 0,
            "master_source_rows": reference["source_rows"],
            "master_distinct_ids": reference["master_distinct_ids"],
            "delta_source_rows": reference["delta_rows"],
            "known_unique_ids_combined": len(reference["known"]),
            "known_effect_candidates": sum(
                r["known_effect_candidate"] for r in reference["known"].values()),
            "delta_special_armor_ids": sum(
                r["delta_special_armor"] for r in reference["known"].values()),
            "known_ids": sorted(reference["known"]),
            "loot_coverage": "NOT_EVALUATED_NO_BLIZZARD_RESPONSE"}

def main(argv=None):
    p = argparse.ArgumentParser(description="Blizzard encounter ID vs existing MID2 reference; NO SimC")
    p.add_argument("--master", type=Path, default=MASTER)
    p.add_argument("--delta", type=Path, default=DELTA)
    p.add_argument("--encounters", type=Path,
                   help="Explicit bounded season encounter IDs and kinds JSON")
    p.add_argument("--journal-dir", type=Path,
                   help="Saved actual Blizzard encounter JSON, encounter_<id>.json")
    p.add_argument("--live", action="store_true",
                   help="Opt-in Blizzard Game Data requests with environment token")
    p.add_argument("--region", choices=("us", "eu", "kr", "tw"), default="us")
    p.add_argument("--out", type=Path)
    args = p.parse_args(argv)
    try:
        ref = existing_reference(read_json(args.master), read_json(args.delta))
        if not args.encounters:
            need(not args.live and args.journal_dir is None,
                 "ENCOUNTER_LIST_REQUIRED_FOR_PROVIDER_QUERY")
            result = reference_only(ref)
        else:
            need(bool(args.live) != bool(args.journal_dir),
                 "PICK_LIVE_OR_SAVED_JOURNAL_NOT_BOTH")
            rows = selected_encounters(read_json(args.encounters))
            if args.live:
                token = os.environ.get("BLIZZARD_ACCESS_TOKEN", "")
                need(bool(token), "BLIZZARD_ACCESS_TOKEN_ENV_REQUIRED")
                documents = {e["encounter_id"]:
                             fetch_encounter(e["encounter_id"], token, args.region)
                             for e in rows}
            else:
                documents = {e["encounter_id"]: read_json(
                    args.journal_dir / ("encounter_%d.json" % e["encounter_id"]))
                    for e in rows}
            result = reconcile(ref, rows, documents, fetch_mode=(
                "blizzard_authenticated_live" if args.live else
                "saved_blizzard_json_unverified_provenance"))
            result["blizzard_requests"] = len(rows) if args.live else 0
        output = json.dumps(result, ensure_ascii=False, sort_keys=True,
                            indent=2) + "\n"
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(output, encoding="utf8")
        print(json.dumps({"status": result["status"], "item_count": (
                  result.get("provider", {}).get("observed_unique_item_ids")
                  if args.encounters else result["known_unique_ids_combined"]),
                  "simc_native_calls": 0, "blizzard_requests":
                   result["blizzard_requests"]}, sort_keys=True))
        return 0
    except Exception as exc:
        # Avoid leaking local paths, token or full HTTP exception bodies.
        code = (str(exc) if isinstance(exc, LootBlocked)
                else type(exc).__name__)
        print(json.dumps({"status": "BLOCKED", "code": code}), file=sys.stderr)
        return 3

if __name__ == "__main__":
    raise SystemExit(main())
