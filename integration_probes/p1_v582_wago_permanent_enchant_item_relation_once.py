#!/usr/bin/env python3
"""P1: one-off same-build Wago physical permanent-enchant source relation.

Read-only research probe, NOT a second Environment Build or product approval.
It reuses v191's SimC parser, v190/v280 CSV parsing and v281 SpellEffect
scanner. Wago chain: Item (class 8) -> ItemSparse (ExpansionID) ->
ItemXItemEffect -> ItemEffect (use SpellID) -> SpellEffect (effect 53,
misc enchant ID) -> SimC permanent_enchant.inc exact enchant ID.
No SimC effect reproduction, Native, DPS, UI publication or cache mutation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))
import v190_consumable_item_snapshot_join as physical
import v191_unified_season_data_update as season
import v280_consumable_item_use_spell_source as use
import v281_consumable_simc_relation as spell

TABLES = ("Item", "ItemSparse", "ItemXItemEffect", "ItemEffect", "SpellEffect")
LIMITS = {"Item": 60_000_000, "ItemSparse": 210_000_000,
          "ItemXItemEffect": 60_000_000, "ItemEffect": 40_000_000,
          "SpellEffect": 150_000_000}
PERM_EFFECT = 53
ITEM_ENHANCEMENT_CLASS = 8
SIMC_MAX = 5_000_000
BUILD = re.compile(r"\d+(?:\.\d+){3}\Z")
REV = re.compile(r"[0-9a-f]{40}\Z")


def need(condition, code):
    if not condition:
        raise ValueError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def fetch_to_file(url, dest, limit):
    request = Request(url, headers={
        "User-Agent": "SIMC-Secondary-P1-Permanent-Enchant-Research/1.0",
        "Accept": "text/csv,text/plain,*/*"})
    count = 0
    h = hashlib.sha256()
    with urlopen(request, timeout=110) as response:
        need(response.status == 200, "SOURCE_HTTP_NON200:" + str(response.status))
        with dest.open("wb") as target:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                count += len(chunk)
                need(count <= limit, "SOURCE_BYTE_LIMIT:" + dest.name)
                h.update(chunk)
                target.write(chunk)
    need(count > 0, "SOURCE_EMPTY:" + dest.name)
    return {"sha256": h.hexdigest(), "bytes": count, "source_url": url}


def catalog(simc_bytes, build):
    source = season.parse_generated("permanent_enchant", simc_bytes)
    need(source["source_build"] == build, "SIMC_GENERATED_BUILD_DRIFT")
    all_rows = [x for x in source["rows"]
                if x["simc_token"].startswith("enchant_")
                and x["item_class"] in (2, 4)]
    highest = season.current_season_enchant_candidates(source)
    need(len(all_rows) >= len(highest) > 0, "SIMC_NO_PERMANENT_CANDIDATES")
    by_id = {}
    for row in all_rows:
        entry = by_id.setdefault(row["enchant_id"], [])
        entry.append({
            "token": row["simc_token"], "quality_rank": row["quality_rank"],
            "item_class": row["item_class"],
            "inventory_type_mask": row["inventory_type_mask"],
            "item_subclass_mask": row["item_subclass_mask"]})
    return by_id, highest, source


def wago_join(directory, simc_by_id, highest, expansion_id):
    root = Path(directory)
    physical_ids = {}
    for row in physical.csvrows(root / "Item.csv", ("ID", "ClassID")):
        if int(row["ClassID"]) == ITEM_ENHANCEMENT_CLASS:
            iid = int(row["ID"])
            need(iid > 0 and iid not in physical_ids, "WAGO_ITEM_ID_DUPLICATE")
            physical_ids[iid] = None
    for row in physical.csvrows(root / "ItemSparse.csv",
                                ("ID", "ExpansionID", "Display_lang")):
        iid = int(row["ID"])
        if iid not in physical_ids:
            continue
        if int(row["ExpansionID"]) == expansion_id:
            physical_ids[iid] = {
                "item_id": iid, "expansion_id": expansion_id,
                "name_enUS": row["Display_lang"].strip()}
        else:
            physical_ids.pop(iid)
    physical_ids = {iid: value for iid, value in physical_ids.items() if value is not None}
    need(physical_ids, "NO_EXPANSION_ITEM_ENHANCEMENT_ITEMS")
    relations = {}
    for row in use._rows((root / "ItemXItemEffect.csv").read_bytes(),
                         ("ItemID", "ItemEffectID"), "RELATION"):
        iid = use._id(row["ItemID"], "ITEM_ID")
        if iid in physical_ids:
            eid = use._id(row["ItemEffectID"], "ITEM_EFFECT_ID", zero=True)
            if eid > 0:
                relations.setdefault(eid, set()).add(iid)
    item_effects = {}
    for row in use._rows((root / "ItemEffect.csv").read_bytes(),
                         ("ID", "SpellID", "TriggerType"), "ITEM_EFFECT"):
        eid = use._id(row["ID"], "ITEM_EFFECT_ID")
        if eid not in relations:
            continue
        need(eid not in item_effects, "WAGO_DUPLICATE_ITEM_EFFECT")
        item_effects[eid] = {
            "spell_id": use._id(row["SpellID"], "SPELL_ID", zero=True),
            "trigger_type": use._id(row["TriggerType"], "TRIGGER_TYPE", zero=True)}
    uses = {}
    for eid, ids in relations.items():
        value = item_effects.get(eid)
        # Enchant scroll ItemEffects may use trigger types other than 0.
        # Keep the observed type; do not borrow v280 food/flask ON_USE=0.
        if value is None or not value["spell_id"]:
            continue
        uses.setdefault(value["spell_id"], []).extend(
            (iid, eid, value["trigger_type"]) for iid in ids)
    observed = spell.scan_spell_effects(root / "SpellEffect.csv", set(uses))
    found = {}
    wago_unmatched = set()
    seen = set()
    for effect in observed:
        if effect["effect"] != PERM_EFFECT or effect["enchant_id"] <= 0:
            continue
        target_id = effect["enchant_id"]
        if target_id not in simc_by_id:
            wago_unmatched.add(target_id)
            continue
        for iid, item_effect_id, trigger_type in uses.get(effect["spell_id"], []):
            unique = (target_id, iid, effect["spell_id"], item_effect_id,
                      trigger_type, effect["effect_index"], effect["difficulty_id"])
            if unique in seen:
                continue
            seen.add(unique)
            found.setdefault(target_id, []).append({
                **physical_ids[iid], "apply_spell_id": effect["spell_id"],
                "item_effect_id": item_effect_id,
                "item_effect_trigger_type": trigger_type,
                "effect_index": effect["effect_index"],
                "difficulty_id": effect["difficulty_id"],
                "exact_join": "WAGO_SPELL_EFFECT_53_MISC_EQUALS_SIMC_ENCHANT_ID"})
    for entries in found.values():
        entries.sort(key=lambda x: (x["item_id"], x["apply_spell_id"],
                                    x["effect_index"], x["difficulty_id"]))
    highest_ids = {x["enchant_id"] for x in highest}
    return {
        "same_expansion_item_enhancement_candidates": len(physical_ids),
        "physical_item_use_spell_count": len(uses),
        "all_simc_permanent_rank_ids": len(simc_by_id),
        "highest_simc_candidate_count": len(highest),
        "highest_source_rank_linked": sum(x in found for x in highest_ids),
        "highest_source_rank_unlinked_ids": sorted(highest_ids - set(found)),
        "any_rank_linked_simc_enchant_ids": len(found),
        "matched_physical_item_ids": len({x["item_id"] for a in found.values()
                                         for x in a}),
        "other_wago_permanent_enchant_ids_not_in_simc_token_source":
            sorted(wago_unmatched),
        "matches": [
            {"enchant_id": eid, "simc_rows": simc_by_id[eid],
             "wago_items": found[eid]}
            for eid in sorted(found)]}


def run(build, revision, expansion_id, out):
    need(BUILD.fullmatch(build) is not None, "EXPLICIT_BUILD_REQUIRED")
    need(REV.fullmatch(revision) is not None, "PINNED_REVISION_REQUIRED")
    need(type(expansion_id) is int and expansion_id > 0,
         "EXPANSION_ID_REQUIRED")
    with TemporaryDirectory(prefix="p1-permanent-enchant-") as temp:
        directory = Path(temp)
        sources = {}
        for name in TABLES:
            url = "https://wago.tools/db2/" + name + "/csv?" + urlencode(
                {"build": build, "locale": "enUS"})
            sources[name] = fetch_to_file(
                url, directory / (name + ".csv"), LIMITS[name])
        simc_url = (
            "https://raw.githubusercontent.com/simulationcraft/simc/"
            + revision + "/engine/dbc/generated/permanent_enchant.inc")
        simc_file = directory / "permanent_enchant.inc"
        sources["simc_permanent"] = fetch_to_file(
            simc_url, simc_file, SIMC_MAX)
        by_id, top, parsed = catalog(simc_file.read_bytes(), build)
        result = wago_join(directory, by_id, top, expansion_id)
    receipt = {
        "schema": "p1_wago_permanent_enchant_physical_relation_diagnostic_v1",
        "status": "SOURCE_ONLY_IDENTITY_RESEARCH_NO_PRODUCT_ADMISSION",
        "game_build": build, "expansion_id": expansion_id,
        "simc_revision": revision, "source_receipts": sources,
        "simc_generated_row_count": parsed["declared_rows"],
        "read_only": True, "native_calls": 0, "new_optimizer": False,
        "physical_item_expansion_match_not_current_season_completeness": True,
        "no_rank_only_quality_approval": True,
        "no_user_ui_or_policy_A_promotion": True,
        **result}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False,
                              sort_keys=True) + "\n", encoding="utf8")
    return receipt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--game-build", required=True)
    p.add_argument("--simc-revision", required=True)
    p.add_argument("--expansion-id", type=int, required=True)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    result = run(args.game_build, args.simc_revision,
                 args.expansion_id, args.out)
    print(json.dumps({
        "status": result["status"], "build": result["game_build"],
        "simc_highest": result["highest_simc_candidate_count"],
        "linked": result["highest_source_rank_linked"],
        "unlinked": len(result["highest_source_rank_unlinked_ids"]),
        "physical": result["matched_physical_item_ids"],
        "no_native": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
