#!/usr/bin/env python3
"""Reusable representative-tier source selection from EXISTING v251 receipts.

Source-only and in-memory: zero extra network/Native and NO additional season
certification Gate. Keep v251 source-stage code bytes unchanged to preserve its
already-sealed same-season cache identity.
"""
from __future__ import annotations
try:
    from . import v251_db2_raid_tier_simc_bridge as bridge
except ImportError:
    import v251_db2_raid_tier_simc_bridge as bridge

SCHEMA=bridge.SCHEMA
SLOTS=bridge.SLOTS
physical=bridge.physical
simc_tier=bridge.simc_tier
specs=bridge.specs
need=bridge.need


def reuse_existing_tier_source(*,physical_candidate,exact_match,
                               cls=None,spec=None):
    """Select from already-sealed raid/DB2 and exact SimC source evidence.

    This is a small in-memory reuse decision, not another season certification,
    HTTP lookup, item handler or Native call. In particular, corroboration of
    one active raid is not proof of every obtainable item or production READY.
    """
    # Caller must use v217-checked v251 source stage outputs. Their upstream
    # receipt already binds the exact first-party join to the physical source.
    need(type(physical_candidate) is dict and
         physical_candidate.get("schema")==SCHEMA and
         physical_candidate.get("status")==
           "OBSERVED_CURRENT_RAID_CORRELATED_65_PIECE_TIER_CANDIDATE" and
         physical_candidate.get("class_count")==13 and
         physical_candidate.get("piece_count")==65 and
         physical_candidate.get("raid_bonus_overlap_count",0)>0 and
         type(physical_candidate.get("observed_base_item_level")) is int and
         physical_candidate["observed_base_item_level"]>0 and
         physical_candidate.get("used_tier_name_matching") is False and
         physical_candidate.get("used_previous_season_item_id_seed") is False and
         physical_candidate.get("season_membership_verified") is False and
         physical_candidate.get("environment_ready") is False,
         "V251_REUSE_EXISTING_RAID_CORRELATED_TIER_REQUIRED")
    need(type(exact_match) is dict and
         exact_match.get("schema")==SCHEMA and
         exact_match.get("status")==
           "EXACT_13_CLASS_SIMC_SET_OPTIONS_MATCHED_SEASON_PENDING" and
         exact_match.get("game_build")==physical_candidate["game_build"] and
         exact_match.get("class_count")==13 and
         exact_match.get("piece_count")==65 and
         exact_match.get("simc_set_option_verified_by_exact_physical_ids")
             is True and
         exact_match.get("season_membership_verified") is False and
         exact_match.get("environment_ready") is False and
         type(exact_match.get("simc_seed_receipt_sha256")) is str and
         len(exact_match["simc_seed_receipt_sha256"])==64,
         "V251_REUSE_EXACT_SIMC_SOURCE_PROOF_REQUIRED")
    byclass=physical_candidate.get("classes")
    matched=exact_match.get("classes")
    need(type(byclass) is dict and type(matched) is dict and
         set(byclass)==set(physical.FAMILY) and
         set(matched)==set(byclass),
         "V251_REUSE_13_CLASS_ROSTER_REQUIRED")
    all_ids=set()
    for key,entry in byclass.items():
        other=matched[key]
        ids=entry.get("tier_piece_ids")
        need(type(ids) is dict and set(ids)==set(SLOTS) and
             all(type(item) is int and item>0 for item in ids.values()) and
             len(set(ids.values()))==5 and
             other.get("item_set_id")==entry.get("item_set_id") and
             other.get("tier_piece_ids")==ids and
             other.get("observed_base_item_level")==
                 physical_candidate["observed_base_item_level"] and
             other.get("source_set_bonus_sizes")==[2,4] and
             type(other.get("simc_set_option")) is str and
             simc_tier.TOKEN.fullmatch(other["simc_set_option"]) is not None,
             "V251_REUSE_EXACT_CLASS_PHYSICAL_OR_BONUS_DRIFT")
        need(not (all_ids & set(ids.values())),
             "V251_REUSE_SHARED_CLASS_ITEM_IDS")
        all_ids.update(ids.values())
    need(len(all_ids)==65,"V251_REUSE_65_PHYSICAL_ITEMS_REQUIRED")
    requested=None
    if cls is not None or spec is not None:
        need(type(cls) is str and type(spec) is str and
             specs.lookup(cls,spec) is not None and cls in byclass,
             "V251_REUSE_26_DPS_REQUEST_REQUIRED")
        entry=byclass[cls];matched_entry=matched[cls]
        four=entry["four_piece_slots"]
        need(type(four) is list and len(four)==4 and
             len(set(four))==4 and set(four)<=set(SLOTS),
             "V251_REUSE_FOUR_PIECE_SLOTS_INVALID")
        requested={
            "class":cls,"spec":spec,
            "item_set_id":entry["item_set_id"],
            "simc_set_option":matched_entry["simc_set_option"],
            "tier_piece_ids":dict(entry["tier_piece_ids"]),
            "four_piece_slots":list(four),
            "four_piece_item_ids":{s:entry["tier_piece_ids"][s] for s in four},
        }
    return {
        "status":"EXISTING_ACTIVE_RAID_SIMC_EXACT_TIER_SOURCE_REUSED",
        "game_build":physical_candidate["game_build"],
        "simc_revision":exact_match["simc_revision"],
        "observed_base_item_level":physical_candidate["observed_base_item_level"],
        "observed_raid_bonus_group_ids":
            list(physical_candidate["observed_raid_bonus_group_ids"]),
        "observed_raid_loot_overlap_count":
            physical_candidate["raid_bonus_overlap_count"],
        "class_count":13,"piece_count":65,
        "source_evidence_reused":True,
        "tier_reidentification_or_extra_source_authentication_required":False,
        "selected_for_request":requested,
        "simc_seed_receipt_sha256":exact_match["simc_seed_receipt_sha256"],
        "season_membership_verified":False,
        "G":None,"environment_ready":False,
        "native_calls":0,"network_calls":0,
    }


