#!/usr/bin/env python3
"""v226: request-driven representative gear -> exact Native G work order.

Reuses the existing v169 source-first 26-DPS equipment selector and v225
new-season byte/lineage preflight. Only the requested spec and item level are
staged. A work order is NOT a measured G, an approved baseline or a SimC
profile; the existing SimC/Native path remains responsible for numerical
ratings. This code does no Native, networking, arbitrary item sampling or
full 26-spec sweep.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib

try:
    from . import v169_source_first_representative_stage as representative
    from . import v225_season_source_bundle_intake as bundle
    from . import v224_season_gjfo_evidence_inventory as source
except ImportError:
    import v169_source_first_representative_stage as representative
    import v225_season_source_bundle_intake as bundle
    import v224_season_gjfo_evidence_inventory as source

SCHEMA = "v226_representative_native_G_work_order_v1"
FOUR = ("head", "shoulders", "hands", "legs")
ORDINARY = ("chest", "wrists", "waist", "feet")
COMMON = ("neck", "back", "finger1", "finger2")


class GWorkOrderBlocked(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise GWorkOrderBlocked(code)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf8")).hexdigest()


def make_work_order(*, bundle_dir, event, previous_game_build, target_ilevel,
                    character_class, specialization):
    """Create one source-pinned job; never infer a rating from gear IDs.

    v225 checks the entire bundle (including J/F/O source identities), but G
    work identity is derived from the relevant gear+tier bytes and chosen
    slots. A change to unrelated J/F/O candidates need not force remeasuring
    the identical physical G loadout.
    """
    verified = bundle.verify_bundle(
        folder=bundle_dir, event=event,
        previous_game_build=previous_game_build,
        target_ilevel=target_ilevel)
    need(verified["ready"] is False and
         verified["verified_components"] == [] and
         verified["source_origin_independently_authenticated"] is False,
         "V226_SOURCE_INTAKE_PREVIEW_ONLY")
    root = pathlib.Path(bundle_dir).expanduser()
    gear_doc, gear_sha = source.load(root / bundle.SOURCE_FILES["gear"])
    tier_doc, tier_sha = source.load(root / bundle.SOURCE_FILES["tier"])
    need(gear_sha == verified["source_input_sha256"]["gear"] and
         tier_sha == verified["source_input_sha256"]["tier"],
         "V226_G_SOURCE_INPUT_SHA_DRIFT")
    need(type(character_class) is str and
         type(specialization) is str,
         "V226_CLASS_SPEC_REQUIRED")
    try:
        chosen = representative.select_class_spec(
            gear_doc, tier_doc, character_class, specialization)
    except (representative.RepresentativeBlocked,
            representative.gear.GearBlocked, ValueError,
            KeyError, TypeError) as exc:
        raise GWorkOrderBlocked(
            "V226_REPRESENTATIVE_GEAR_NOT_READY:" + str(exc)) from exc

    need(chosen["weapon_form"] in representative.contracts.WEAPON_FORMS and
         set(chosen["tier_ids"]) == set(representative.contracts.TIER_SLOTS) and
         set(chosen["four_tier_slots"]) == set(FOUR) and
         set(chosen["ordinary"]) == set(ORDINARY) and
         set(chosen["common_gear"]) == set(COMMON) and
         set(chosen["weapons"]) ==
            set(representative.contracts.WEAPON_FORMS[
                chosen["weapon_form"]]),
         "V226_REQUIRED_EQUIPMENT_SHAPE_INVALID")
    slots = {}
    for slot in FOUR:
        slots[slot] = chosen["tier_ids"][slot]
    slots.update(chosen["ordinary"])
    slots.update(chosen["common_gear"])
    slots.update(chosen["weapons"])
    need(len(slots) in (13, 14) and
         all(type(i) is int and i > 0 for i in slots.values()) and
         len(slots) == len(set(slots.values())),
         "V226_REPRESENTATIVE_SLOT_ID_DUPLICATE_OR_MISSING")
    # v169 validates weapons' primary-stat metadata, armor family/class and
    # slot forms. These are source candidates, NOT Native proficiency proof.
    # Tier ids originate from the tier source, not necessarily ordinary DB.
    plain_and_weapon = set(chosen["ordinary"].values()) | set(
        chosen["common_gear"].values()) | set(chosen["weapons"].values()))
    known_plain = {r["item_id"] for r in gear_doc["items"]
                   if r["category"] == "plain_representative_candidate"}
    need(plain_and_weapon <= known_plain,
         "V226_PLAIN_OR_WEAPON_NOT_IN_CURRENT_SOURCE")
    need(all(chosen["tier_ids"][slot] == tier_doc["classes"][
        character_class]["pieces"][slot] for slot in FOUR),
         "V226_TIER_CLASS_ITEM_SOURCE_DRIFT")
    # Exact source/slot/ilevel identity for a future narrowly scoped Native
    # static JSON2 measurement. This is not a new optimizer/SimC engine.
    native_input = {
        "game_build": verified["game_build"],
        "season": verified["season"],
        "target_ilevel": target_ilevel,
        "character": {
            "class": character_class,
            "spec": specialization,
            "primary_stat": representative.contracts.lookup(
                character_class, specialization)["primary"],
            "weapon_form": chosen["weapon_form"],
            "armor_family": chosen["armor_family"],
        },
        "core_source_sha256": {
            "gear": gear_sha,
            "tier": tier_sha,
        },
        "slot_item_ids": {slot: slots[slot] for slot in sorted(slots)},
        "four_tier_slots": list(FOUR),
        "excluded_slot_rules": [
            "TRINKET_FIXED_STATS_OUTSIDE_G",
            "NO_J_F_OR_TEMPORARY_OIL_IN_G",
            "NO_USER_CURRENT_EQUIPMENT",
        ],
    }
    work_hash = digest(native_input)
    result = {
        "schema": SCHEMA,
        "status": "WAIT_EXACT_SOURCE_PROFILE_AND_NATIVE_STATIC_G",
        "game_build": verified["game_build"],
        "season": verified["season"],
        "target_ilevel": target_ilevel,
        "character": native_input["character"],
        "selected_source_slots": native_input["slot_item_ids"],
        "tier_piece_ids": {slot: chosen["tier_ids"][slot]
                            for slot in FOUR},
        "weapon_form": chosen["weapon_form"],
        "weapon_count": len(chosen["weapons"]),
        "source_bundle_receipt_sha256": verified["receipt_sha256"],
        "gear_source_sha256": gear_sha,
        "tier_source_sha256": tier_sha,
        "work_identity_sha256": work_hash,
        "measurement_request": {
            "schema": "v226_static_G_single_spec_ilevel_request_v1",
            "work_identity_sha256": work_hash,
            "native_input": native_input,
            "execute_native_now": False,
            "target_measurement": "CHMV_G_NONTRINKET_REPRESENTATIVE_STATIC",
            "native_json2_static_rating_required": True,
            "missing_evidence": [
                "SOURCE_ITEM_ID_AND_WEAPON_PROFICIENCY_ACCEPTANCE",
                "NATIVE_OR_VERIFIED_SAME_SEASON_G_RATING",
                "STATIC_ENCHANT_E_AND_SPECIAL_L_ACCOUNTING",
                "SCALING_BETWEEN_ILVLS_NOT_ASSUMED",
            ],
        },
        "G": None,
        "G_reference_rounded": False,
        "B": None,
        "T": None,
        "verified_G": False,
        "profile_native_accepted": False,
        "environment_ready": False,
        "new_native_calls": 0,
        "network_calls": 0,
        "cache_mutations": 0,
        "scope": "ONE_REQUESTED_SPEC_AND_ITEM_LEVEL",
    }
    return {**result, "receipt_sha256": digest(result)}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bundle-dir", type=pathlib.Path, required=True)
    p.add_argument("--event", required=True, choices=bundle.EVENTS)
    p.add_argument("--previous-game-build", required=True)
    p.add_argument("--target-ilevel", type=int, required=True)
    p.add_argument("--class", dest="cls", required=True)
    p.add_argument("--spec", required=True)
    p.add_argument("--out", type=pathlib.Path, required=True)
    args = p.parse_args(argv)
    result = make_work_order(
        bundle_dir=args.bundle_dir, event=args.event,
        previous_game_build=args.previous_game_build,
        target_ilevel=args.target_ilevel,
        character_class=args.cls, specialization=args.spec)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(
        result, sort_keys=True, indent=2,
        ensure_ascii=False, allow_nan=False) + "\n", encoding="utf8")
    print("V226_ONE_SPEC_REPRESENTATIVE_G_WORK_ORDER",
          result["character"]["class"], result["character"]["spec"],
          result["target_ilevel"], "G_NOT_MEASURED_NATIVE0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
