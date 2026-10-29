#!/usr/bin/env python3
"""Source-first Blizzard encounter item-ID collector.

Requires ONLY discovered encounter references and Blizzard JSON. No legacy
WEQUIP catalog, previous-season list, inferred effect support, or SimC calls.
An absent loot field means UNKNOWN, never an empty loot pool.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys
from urllib.parse import urlencode
import v155_season_api_probe as api

SCHEMA = "v154_source_first_blizzard_encounter_loot_v2"
MAX_ENCOUNTERS = 48
KINDS = {"raid", "mplus", "delve"}


class LootBlocked(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise LootBlocked(reason)


def read_json(path):
    p = Path(path)
    need(p.is_file() and p.stat().st_size <= 8_000_000,
         "JSON_FILE_MISSING_OR_TOO_LARGE")
    return json.loads(p.read_text(encoding="utf8"))


def selected_encounters(selection):
    need(type(selection) is dict and type(selection.get("encounters")) is list,
         "ENCOUNTER_SELECTION_REQUIRED")
    raw = selection["encounters"]
    need(1 <= len(raw) <= MAX_ENCOUNTERS, "ENCOUNTER_COUNT_LIMIT")
    rows, seen = [], set()
    for item in raw:
        need(type(item) is dict and set(item) ==
             {"encounter_id", "instance_id", "kind"}, "ENCOUNTER_FIELDS")
        eid, inst, kind = item["encounter_id"], item["instance_id"], item["kind"]
        need(type(eid) is int and eid > 0 and type(inst) is int and
             inst > 0 and kind in KINDS, "ENCOUNTER_ID_OR_KIND")
        need(eid not in seen, "DUPLICATE_ENCOUNTER_ID")
        seen.add(eid)
        rows.append(dict(item))
    return rows


def encounter_loot(document, expected_id):
    need(type(document) is dict, "JOURNAL_ENCOUNTER_OBJECT")
    need(document.get("id") == expected_id, "JOURNAL_ENCOUNTER_ID_MISMATCH")
    fields = [name for name in ("items", "loot") if name in document]
    if not fields:
        return None
    need(len(fields) == 1, "JOURNAL_LOOT_FIELD_AMBIGUOUS")
    values = document[fields[0]]
    need(type(values) is list and len(values) <= 400, "JOURNAL_LOOT_SHAPE")
    result = set()
    for row in values:
        need(type(row) is dict, "JOURNAL_LOOT_ROW")
        item = row.get("item", row)
        need(type(item) is dict and type(item.get("id")) is int and
             item["id"] > 0, "JOURNAL_LOOT_ITEM_ID_NOT_EXPLICIT")
        result.add(item["id"])
    return sorted(result)


def collect(encounters, documents, *, source_mode="saved_unverified_json"):
    """Create a fresh acquired-ID index exclusively from provider responses."""
    observed, source_rows, unknown = {}, [], []
    for row in encounters:
        eid = row["encounter_id"]
        need(eid in documents, "ENCOUNTER_RESPONSE_MISSING")
        loot = encounter_loot(documents[eid], eid)
        if loot is None:
            unknown.append(eid)
        source_rows.append({
            "instance_id": row["instance_id"], "encounter_id": eid,
            "kind": row["kind"],
            "loot_state": "UNKNOWN_FIELD_ABSENT" if loot is None
                          else "EXPLICIT_API_LIST",
            "observed_item_ids": loot})
        if loot is None:
            continue
        for item_id in loot:
            item = observed.setdefault(item_id, {
                "item_id": item_id, "source_encounter_ids": [],
                "source_kinds": []})
            item["source_encounter_ids"].append(eid)
            if row["kind"] not in item["source_kinds"]:
                item["source_kinds"].append(row["kind"])
    for item in observed.values():
        item["source_encounter_ids"].sort()
        item["source_kinds"].sort()
    need(len(observed) <= MAX_ENCOUNTERS * 400, "ITEM_CAP")
    return {
        "schema": SCHEMA,
        "status": "PARTIAL_UNKNOWN_LOOT" if unknown else
                  "SELECTED_ENCOUNTERS_COLLECTED_NOT_FULL_SEASON",
        "source_mode": source_mode,
        "source_authority": "BLIZZARD_API_RESPONSE" if
            source_mode == "blizzard_authenticated_live" else
            "UNVERIFIED_SAVED_INPUT",
        "encounters_requested": len(encounters),
        "encounters_with_explicit_loot": len(encounters) - len(unknown),
        "encounters_missing_loot_field": sorted(unknown),
        "encounter_sources": source_rows,
        "unique_item_ids": sorted(observed),
        "items": [observed[i] for i in sorted(observed)],
        "legacy_item_data_used": False,
        "season_complete": False,
        "simc_native_calls": 0,
        "static_L_generated": False,
        "effect_support_verified": False}


def fetch_encounter(encounter_id, token, region="kr"):
    need(region in ("us", "eu", "kr", "tw"), "REGION_NOT_ALLOWED")
    need(type(token) is str and bool(token), "BLIZZARD_TOKEN_REQUIRED")
    url = ("https://" + region +
           ".api.blizzard.com/data/wow/journal-encounter/" +
           str(encounter_id) + "?" +
           urlencode({"namespace": "static-" + region,
                      "locale": "en_US"}))
    # Only a fixed official host and route, with bounded JSON size/timeout.
    return api.request_json(url, headers={
        "Authorization": "Bearer " + token})


def main(argv=None):
    p = argparse.ArgumentParser(description="Collect official encounter item IDs; zero legacy sources")
    p.add_argument("--encounters", required=True, type=Path,
                   help="Season-selected encounter IDs discovered from providers")
    p.add_argument("--journal-dir", type=Path,
                   help="Saved Blizzard encounter_<id>.json responses (unverified)")
    p.add_argument("--live", action="store_true",
                   help="Use Github Secrets/local environment Blizzard credentials")
    p.add_argument("--region", choices=("us", "eu", "kr", "tw"), default="kr")
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args(argv)
    try:
        need(bool(args.live) != bool(args.journal_dir),
             "PICK_LIVE_OR_SAVED_JOURNAL_NOT_BOTH")
        rows = selected_encounters(read_json(args.encounters))
        if args.live:
            token = os.environ.get("BLIZZARD_ACCESS_TOKEN")
            if not token:
                client_id = os.environ.get("BLIZZARD_CLIENT_ID", "")
                secret = os.environ.get("BLIZZARD_CLIENT_SECRET", "")
                need(bool(client_id) and bool(secret),
                     "BLIZZARD_CREDENTIALS_REQUIRED")
                token = api.oauth_token(api.BLIZZARD_TOKEN_URL,
                                        client_id, secret)
            docs = {r["encounter_id"]:
                    fetch_encounter(r["encounter_id"], token, args.region)
                    for r in rows}
        else:
            docs = {r["encounter_id"]:
                    read_json(args.journal_dir /
                              ("encounter_%d.json" % r["encounter_id"]))
                    for r in rows}
        result = collect(rows, docs, source_mode=(
            "blizzard_authenticated_live" if args.live
            else "saved_unverified_json"))
        result["blizzard_game_data_requests"] = len(rows) if args.live else 0
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, sort_keys=True,
                                       ensure_ascii=False, indent=2) + "\n",
                            encoding="utf8")
        print(json.dumps({"status": result["status"],
                          "items": len(result["unique_item_ids"]),
                          "encounters": len(rows),
                          "native_calls": 0}, sort_keys=True))
        return 0
    except Exception as exc:
        code = str(exc) if isinstance(exc, LootBlocked) else type(exc).__name__
        print(json.dumps({"status": "BLOCKED", "code": code}),
              file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
