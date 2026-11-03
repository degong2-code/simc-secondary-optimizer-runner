#!/usr/bin/env python3
"""v167: one replaceable, small season gear DB for product input and previews.

From v166 saved evidence only. No HTTP, Native SimC, WCL or old item DB.
Offers IDs/names for current candidates; does not change any user scenario,
session identity, static-L cache, gear options or v139/v098 profiles.
Unverified tier and weapon rows are deliberately NOT auto-selected.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

SCHEMA = "v167_product_season_gear_db_v1"
SOURCE_SCHEMA = "v166_current_season_product_gear_db_v1"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "data" / "current_season_product_gear_db.json"
MAX_BYTES = 2_000_000
CATEGORIES = (
    "trinket", "special_effect_gear_candidate", "selectable_stat_craft",
    "plain_representative_candidate"
)
# Retail inventory type to unambiguous SimC equipment slot. Ring, weapon and
# two-hand slots cannot safely be guessed from InventoryType alone.
SLOTS = {
    1: "head", 2: "neck", 3: "shoulders", 5: "chest",
    6: "waist", 7: "legs", 8: "feet", 9: "wrists",
    10: "hands", 16: "back"
}
ARMOR_SUBCLASS = {"cloth": 1, "leather": 2, "mail": 3, "plate": 4}
# Only true armor slots need the matching subclass; neck/cloak/rings do not.
ARMOR_SLOTS = frozenset(("head","shoulders","chest","waist","legs",
                         "feet","wrists","hands"))
COMMON_SLOTS = frozenset(("neck","back"))
REPRESENTATIVE_SLOTS = frozenset(("neck","back","wrists","waist","feet"))
# ItemSlot 12 is a trinket in Retail; never map it to a nontrinket name.
TRINKET_INVENTORY_TYPE = 12

class GearBlocked(ValueError):
    pass

def need(condition, reason):
    if not condition:
        raise GearBlocked(reason)

def read(path=DEFAULT):
    path = Path(path)
    need(path.is_file() and 0 < path.stat().st_size <= MAX_BYTES,
         "SEASON_PRODUCT_DB_MISSING_OR_TOO_LARGE")
    return validate(json.loads(path.read_text(encoding="utf8")))

def from_v166(source):
    need(type(source) is dict and
         source.get("schema") == SOURCE_SCHEMA and
         source.get("status") == "COMPACT_CANDIDATE_DB_WITH_PENDING_GAPS" and
         source.get("no_old_catalog_seed") is True and
         source.get("native_calls") == 0,
         "REAL_V166_SOURCE_REQUIRED")
    rows = source.get("current_candidates")
    # A fresh season may have only WSE-conditional physical candidates.
    # Keep them internal while the public current-candidate list is empty.
    pending_count=source.get("internal_conditional_mplus_plain_count",0)
    need(type(rows) is list and
         len(rows) == source.get("current_candidate_count") and
         len(rows) <= 2000 and
         (bool(rows) or type(pending_count) is int and pending_count>0),
         "CURRENT_ITEM_COUNT_MISMATCH")
    result = []
    for entry in rows:
        need(type(entry) is dict and
             entry.get("selection_evidence") == "CURRENT_CANDIDATE" and
             entry.get("category") in CATEGORIES,
             "ONLY_CURRENT_SEASON_ROLE_CANDIDATES_ALLOWED")
        iid = entry.get("item_id")
        inventory_type = entry.get("slot")
        name = entry.get("name")
        cls = entry.get("class_id")
        sub = entry.get("subclass_id")
        need(type(iid) is int and iid > 0 and
             type(inventory_type) is int and inventory_type > 0 and
             type(cls) is int and cls in (2,4) and
             type(sub) is int and sub >= 0 and
             type(name) is str and 0 < len(name) <= 200,
             "PRODUCT_ITEM_METADATA_INVALID")
        if entry["category"] == "trinket":
            need(inventory_type == TRINKET_INVENTORY_TYPE,
                 "TRINKET_SLOT_MISMATCH")
        else:
            need(inventory_type != TRINKET_INVENTORY_TYPE,
                 "NONTRINKET_SLOT_MISMATCH")
        result.append({
            "item_id": iid, "name": name, "category": entry["category"],
            "inventory_type": inventory_type, "class_id": cls,
            "subclass_id": sub,
            "allowed_class_mask": entry.get("allowed_class_mask"),
            "stat_modifier_codes": entry.get("stat_modifier_codes"),
            "item_set_id": entry.get("item_set_id", 0),
            "slot_hint": SLOTS.get(inventory_type),
            "source_kinds": entry.get("source_kinds", []),
            "source_evidence":entry.get("source_evidence", []),
        })
    result.sort(key=lambda x:x["item_id"])
    pending=source.get("internal_conditional_mplus_plain_candidates",[])
    need(type(pending) is list and len(pending)<=2000 and
         len(pending)==source.get("internal_conditional_mplus_plain_count",
                                 len(pending)),
         "CONDITIONAL_MPLUS_SOURCE_COUNT_INVALID")
    internal=[]; seen={r["item_id"] for r in result}
    for entry in pending:
        need(type(entry) is dict
             and entry.get("selection_evidence")==
                 "CONDITIONAL_SEASON_NOT_ESTABLISHED"
             and entry.get("category")=="plain_representative_candidate"
             and entry.get("direct_item_effect_record") is False
             and entry.get("item_set_id")==0
             and type(entry.get("item_id")) is int
             and entry["item_id"]>0 and entry["item_id"] not in seen
             and type(entry.get("slot")) is int and entry["slot"]>0
             and entry["slot"]!=12
             and type(entry.get("class_id")) is int
             and entry["class_id"] in (2,4)
             and type(entry.get("subclass_id")) is int
             and type(entry.get("source_evidence")) is list
             and any(e.get("source")=="mplus_journal"
                 and e.get("season_evidence")==
                     "UNKNOWN_WORLD_STATE_EXPRESSION"
                 and e.get("display_season_id")==source.get("display_season_id")
                 and type(e.get("world_state_expression_id")) is int
                 and e["world_state_expression_id"]>0
                 and type(e.get("journal_encounter_id")) is int
                 and e["journal_encounter_id"]>0
                 and type(e.get("journal_instance_id")) is int
                 and e["journal_instance_id"]>0
                 for e in entry["source_evidence"]),
             "CONDITIONAL_MPLUS_SOURCE_NOT_JUSTIFIED")
        seen.add(entry["item_id"])
        internal.append({
            "item_id":entry["item_id"],"name":entry["name"],
            "category":"plain_representative_candidate",
            "inventory_type":entry["slot"],
            "class_id":entry["class_id"],"subclass_id":entry["subclass_id"],
            "allowed_class_mask":entry["allowed_class_mask"],
            "stat_modifier_codes":entry["stat_modifier_codes"],
            "item_set_id":0,
            "source_kinds":entry["source_kinds"],
            "source_evidence":entry["source_evidence"],
            "provisional_mplus_world_state_only":True,
            "season_membership_verified":False,"ui_selectable":False})
    internal.sort(key=lambda x:x["item_id"])
    summary = {
        "schema": SCHEMA, "status": "CURRENT_SEASON_CANDIDATE_SELECTION_ONLY",
        "season_build": source["season_build"],
        "expansion_id": source["expansion_id"],
        "db2_display_season_id": source["display_season_id"],
        "item_count": len(result),
        "role_counts": dict(sorted(Counter(x["category"] for x in result).items())),
        "items": result,
        "internal_conditional_mplus_plain_candidates":internal,
        "internal_conditional_mplus_plain_count":len(internal),
        "conditional_ids_excluded": source.get("conditional_count"),
        "consumable_budget_source_mode": source.get(
            "consumable_budget_source_mode","LEGACY_UNRECORDED_SOURCE_MODE"),
        "J_F_NUMERIC_AUTHENTICATION_NOT_IN_GEAR_COLLECTOR": True,
        "no_old_catalog_seed": True,
        "not_certified": {
            "simc_item_effects": True, "tier_four_set": True,
            "full_mplus_world_state": True,
            "representative_physical_profile": True,
        },
        "new_api_calls": 0, "new_native_calls": 0
    }
    return validate(summary)

def validate(payload):
    need(type(payload) is dict and
         payload.get("schema") == SCHEMA and
         payload.get("status") == "CURRENT_SEASON_CANDIDATE_SELECTION_ONLY"
         and payload.get("no_old_catalog_seed") is True and
         payload.get("new_native_calls") == 0 and
         payload.get("new_api_calls") == 0,
         "PRODUCT_SEASON_DB_STATUS_INVALID")
    items = payload.get("items")
    need(type(items) is list and
         type(payload.get("item_count")) is int and
         len(items) == payload["item_count"] <= 2000 and
         (bool(items) or payload.get(
             "internal_conditional_mplus_plain_count",0)>0),
         "PRODUCT_SEASON_DB_COUNT_INVALID")
    ids = set()
    for x in items:
        need(type(x) is dict and
             type(x.get("item_id")) is int and x["item_id"] > 0
             and x["item_id"] not in ids
             and x.get("category") in CATEGORIES
             and type(x.get("name")) is str
             and type(x.get("inventory_type")) is int,
             "PRODUCT_SEASON_ITEM_INVALID")
        ids.add(x["item_id"])
        evidence=x.get("source_evidence",[])
        need(type(evidence) is list and len(evidence)<=64 and
             all(type(r) is dict and
                 type(r.get("source")) is str and
                 r["source"] in (
                     "raid_journal","mplus_journal",
                     "selectable_stat_craft","localbots_delve_pool")
                 and all(k in (
                     "source","season_evidence","display_season_id",
                     "world_state_expression_id","journal_encounter_id",
                     "journal_instance_id","challenge_mode_id",
                     "expansion_id") for k in r)
                 for r in evidence),
             "PRODUCT_SOURCE_EVIDENCE_INVALID")
        # Older already-sealed v166 catalogs contain source kinds but not
        # per-item DB2 conditions. Keep them as UNKNOWN provenance rather
        # than inventing evidence or rejecting compatible old source data.
        if evidence:
            need({r["source"] for r in evidence}==
                 set(x.get("source_kinds",[])),
                 "PRODUCT_SOURCE_EVIDENCE_KINDS_DISAGREE")
        if x["category"] == "trinket":
            need(x["inventory_type"] == TRINKET_INVENTORY_TYPE,
                 "PRODUCT_TRINKET_SLOT")
        else:
            need(x["inventory_type"] != TRINKET_INVENTORY_TYPE,
                 "PRODUCT_OTHER_SLOT")
    need(dict(sorted(Counter(x["category"] for x in items).items())) ==
         payload.get("role_counts"), "PRODUCT_ROLE_COUNTS_INVALID")
    pending=payload.get("internal_conditional_mplus_plain_candidates",[])
    need(type(pending) is list
         and len(pending)==payload.get("internal_conditional_mplus_plain_count",
                                       len(pending))
         and len(pending)<=2000,
         "PRODUCT_INTERNAL_MPLUS_SOURCE_COUNT_INVALID")
    for x in pending:
        ev=x.get("source_evidence",[]) if type(x) is dict else []
        need(type(x) is dict and type(x.get("item_id")) is int
             and x["item_id"]>0 and x["item_id"] not in ids
             and type(x.get("inventory_type")) is int
             and x["inventory_type"]!=12
             and x.get("category")=="plain_representative_candidate"
             and x.get("item_set_id")==0
             and x.get("provisional_mplus_world_state_only") is True
             and x.get("season_membership_verified") is False
             and x.get("ui_selectable") is False and type(ev) is list
             and any(type(e) is dict
                 and e.get("source")=="mplus_journal"
                 and e.get("season_evidence")==
                     "UNKNOWN_WORLD_STATE_EXPRESSION"
                 and e.get("display_season_id")==
                     payload.get("db2_display_season_id")
                 and type(e.get("world_state_expression_id")) is int
                 and e["world_state_expression_id"]>0 for e in ev),
             "PRODUCT_INTERNAL_MPLUS_SOURCE_NOT_PENDING")
        ids.add(x["item_id"])
    need(payload.get("not_certified", {}).get("tier_four_set") is True and
         payload["not_certified"].get("simc_item_effects") is True,
         "PRODUCT_EFFECT_OR_TIER_OVERCLAIM")
    return payload

def public_options(payload):
    """Selection-only public roles. Plain equipment remains an internal DB input."""
    db = validate(payload)
    visible = ("trinket","special_effect_gear_candidate","selectable_stat_craft")
    choices = {key: [] for key in visible}
    for x in db["items"]:
        if x["category"] not in choices:
            continue
        choices[x["category"]].append({
            "item_id": x["item_id"],
            "name": x["name"],
            "inventory_type": x["inventory_type"],
            "slot_hint": x["slot_hint"],
            # ItemClass and subclass are current-season source metadata;
            # UI selects a deterministic compatible crafted base privately.
            "class_id": x["class_id"],
            "subclass_id": x["subclass_id"],
            "season_list_basis": x.get("season_list_basis")
        })
    for rows in choices.values():
        rows.sort(key=lambda x:(x["name"].casefold(), x["item_id"]))
    # Stable contract metadata, not a new equipment recommendation.
    import v143_specialization_contracts as specs
    weapon_forms={"/".join(key.split("/")):specs.lookup(*key.split("/"))["weapon_form"]
                  for key in sorted(specs.CONTRACTS)}
    return {
        "schema": SCHEMA,
        "status": db["status"],
        "season_build": db["season_build"],
        "choices": choices,
        "weapon_forms": weapon_forms,
        "count": db["item_count"],
        "manual_exact_id_allowed": False,
        "manual_exact_id_exception": "CRAFTED_EQUIPMENT_VARIANTS_ONLY",
        "ordinary_equipment_user_selectable": False,
        "full_season_completeness_confirmed": False,
        "native_calls_now": 0,
    }

def ordinary_candidates(payload, family, *, slots=REPRESENTATIVE_SLOTS):
    """Small class-family-compatible interior candidate preview; no gear swap.

    Does not choose class/spec tier, weapon or bonus/embellishment. Item class,
    subclass and inventory type are only a prefilter, NOT Native acceptance.
    """
    db = validate(payload)
    need(family in ARMOR_SUBCLASS, "REPRESENTATIVE_ARMOR_FAMILY_UNKNOWN")
    need(set(slots) <= REPRESENTATIVE_SLOTS, "REPRESENTATIVE_SLOT_UNSUPPORTED")
    result = {slot:[] for slot in slots}
    for x in db["items"]:
        if x["category"] != "plain_representative_candidate":
            continue
        slot = x["slot_hint"]
        if slot not in result:
            continue
        if slot in ARMOR_SLOTS and (
            x["class_id"] != 4 or x["subclass_id"] != ARMOR_SUBCLASS[family]):
            continue
        result[slot].append({"item_id":x["item_id"],"name":x["name"]})
    for candidates in result.values():
        candidates.sort(key=lambda x:x["item_id"])
    return {"schema": SCHEMA, "status":"PREVIEW_ONLY_NOT_A_PROFILE",
            "season_build":db["season_build"],"armor_family":family,
            "candidate_slots":result,"tier_four_piece_id_confirmed":False,
            "weapon_profile_confirmed":False,"native_calls_now":0}

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--source-v166",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args(argv)
    try:
        source=json.loads(args.source_v166.read_text(encoding="utf8"))
        value=from_v166(source)
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,
            separators=(",",":"),allow_nan=False)+"\n",encoding="utf8")
        print(json.dumps({"status":value["status"],"count":value["item_count"],
                          "roles":value["role_counts"],"native":0},sort_keys=True))
        return 0
    except (GearBlocked,KeyError,ValueError,TypeError,OSError) as e:
        print(json.dumps({"status":"BLOCKED",
                          "code":str(e) if isinstance(e,GearBlocked) else type(e).__name__}))
        return 3

if __name__ == "__main__":
    raise SystemExit(main())
