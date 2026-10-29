#!/usr/bin/env python3
"""P1 source-independent SimC representative PROFILE composer.

The SEASON CATALOG (not a downloaded, complete BiS/SimC profile) provides
item IDs and four-tier choices. User data provides character/trinkets/combat.
SimC owns default_actions, primary stat/item effects and DPS; there is NO
class-specific APL implementation here. This is an *internal stage*, NOT
v098 production readiness, exact CHMV B, 95% DPS or Native acceptance.

A future season replaces catalog data. The algorithm has no MID2 fixture,
v132 profile or v133 draft dependency and calls no SimC executable.
"""
from __future__ import annotations
import hashlib
import json
import pathlib

import v108_native_consumable_inputs as consumer

import v055_simc_item_selection as items
import v061_scenario_contract as scenario
import v143_specialization_contracts as contracts

ROOT=pathlib.Path(__file__).resolve().parents[1]
DEFAULT_CATALOG=(ROOT/"integration_probes/catalog/"
                 "v144_mid2_season_items.json")
SCHEMA="v139_source_independent_representative_stage_v1"
# Backward-compatible constants; these are stable contracts, not season IDs.
CLASS_ARMOR={info["simc_class"]:info["family"]
             for info in contracts.CONTRACTS.values()}
TIER_SLOTS=contracts.TIER_SLOTS
SLOT_ORDER=contracts.SLOT_ORDER
FIXED_STATES=contracts.RATING_STATS

class ProfileStageBlocked(ValueError):
    pass

def need(ok,why):
    if not ok:
        raise ProfileStageBlocked(why)

def validate_season(doc):
    """No stable class/spec contract fields may leak into replaceable data."""
    need(type(doc) is dict and
         doc.get("schema")=="v144_representative_season_items_v1" and
         type(doc.get("specializations")) is dict and
         type(doc.get("common_gear")) is dict and
         type(doc.get("gems")) is dict and
         type(doc.get("target_ilevel")) is int and
         type(doc.get("season")) is str and
         type(doc.get("character_level")) is int and
         1<=doc["character_level"]<=100 and
         type(doc.get("default_consumables")) is dict and
         set(doc["default_consumables"])=={
            "flask","food","potion","augmentation","omnium_talents",
            "gem_budget_J","flask_budget_F","flask_fixed_stat"},
         "SEASON_DATA_SCHEMA")
    # On future season snapshots, explicitly ask the *same SimC binary*
    # to resolve item ID/ilevel/options from its bundled local item DB.
    # Optional to keep established 334 profile bytes and Native caches stable.
    # No fallback to external item sources or homemade stat/effect model.
    need("simc_item_db_source" not in doc or
         doc["simc_item_db_source"]=="local",
         "ONLY_SIMC_LOCAL_ITEM_DATA_SOURCE_SUPPORTED")
    allowed={"tier_ids","four_tier_slots","ordinary","weapons"}
    for key,info in doc["specializations"].items():
        need(contracts.lookup(*key.split("/")) is not None,
             "SEASON_SPEC_HAS_NO_STABLE_CONTRACT")
        need(type(info) is dict and set(info) in (allowed,allowed|{"item_options"}),
             "SEASON_CONTAINS_STABLE_CONTRACT_FIELDS")
    return doc

def catalog(path=DEFAULT_CATALOG):
    """Replaceable season IDs/levels/consumables; NO official profile read."""
    return validate_season(json.loads(pathlib.Path(path).read_text(encoding="utf8")))

def compose(character,trinkets,*,target_ilevel=334,
            combat=None,season=None):
    """Return (profile text, stage metadata, rows, tier group) without Native.

    This is deliberately independent of the 24 source-backed ARCHETYPES.
    It is NOT registered as user-ready until actual SimC acceptance and the
    existing v098 CHMV budget/consumable/cache/95% path are verified.
    """
    season=catalog() if season is None else validate_season(season)
    need(type(character) is dict and
         set(character)=={"class","spec","race","talents"},
         "CHARACTER_FIELDS")
    cl=character["class"];spec=character["spec"]
    contract=(contracts.lookup(cl,spec)
              if type(cl) is str and type(spec) is str else None)
    need(contract is not None and cl+"/"+spec in season["specializations"],
         "SOURCE_INDEPENDENT_SPEC_NOT_STAGED")
    need(type(target_ilevel) is int and
         target_ilevel==season["target_ilevel"],
         "SEASON_TARGET_LEVEL_NOT_GROUNDED")
    need(type(trinkets) is list and len(trinkets)==2 and
         {x.get("slot") for x in trinkets if type(x) is dict}==
         {"trinket1","trinket2"},
         "EXACT_TWO_USER_TRINKETS")
    for name in ("race","talents"):
        scenario.text_token(character[name],"USER_"+name.upper())
    if contract["allowed_races"] is not None:
        need(character["race"] in contract["allowed_races"],
             "EVOKER_RACE_NOT_VERIFIED" if cl=="evoker" else
             "SPEC_RACE_NOT_VERIFIED")
    combat={"targets":1,"duration_seconds":300,"raid_buffs":True} if combat is None else combat
    need(type(combat) is dict and
         set(combat)=={"targets","duration_seconds","raid_buffs"} and
         type(combat["targets"]) is int and 1<=combat["targets"]<=40 and
         type(combat["duration_seconds"]) is int and
         1<=combat["duration_seconds"]<=3600 and
         type(combat["raid_buffs"]) is bool,"COMBAT_FIELDS_OR_LIMITS")
    info=season["specializations"][cl+"/"+spec]
    need(contracts.validate_contracts() and
         contract["weapon_form"] in contracts.WEAPON_FORMS,
         "CLASS_PHYSICAL_CONTRACT")
    need(set(info["tier_ids"])==set(TIER_SLOTS) and
         len(info["four_tier_slots"])==4 and
         set(info["four_tier_slots"])<=set(TIER_SLOTS) and
         set(info["ordinary"])==
           ((set(TIER_SLOTS)-set(info["four_tier_slots"])) |
            contracts.NON_TIER_ORDINARY),
         "FOUR_TIER_LAYOUT_OR_ORDINARY_MISSING")
    # First four-piece is selected from actual current-season class-tier IDs;
    # the fifth can be swapped later without changing the engine.
    ids={**season["common_gear"],**info["ordinary"],**info["weapons"]}
    ids.update({slot:info["tier_ids"][slot]
                for slot in info["four_tier_slots"]})
    weapon_slots=set(contracts.WEAPON_FORMS[contract["weapon_form"]])
    physical_slots=(set(SLOT_ORDER)-{"trinket1","trinket2"}-
                    (contracts.WEAPON_SLOTS-weapon_slots))
    need(set(ids)==physical_slots and
         set(info["weapons"])==weapon_slots and
         all(type(v) is int and v>0 for v in ids.values()),
         "INTERNAL_REPRESENTATIVE_SLOT_OR_ITEM_ID")
    options={slot:{"gem_id":value}
             for slot,value in season["gems"].items()}
    # Only item-specific serialization options belong in the replaceable
    # season record (e.g., an observed crafted 2H offhand secondary pair).
    # Reject overlapping gem settings instead of silently double applying.
    seasonal_options=info.get("item_options",{})
    need(type(seasonal_options) is dict and
         set(seasonal_options)<=set(ids) and
         all(type(v) is dict and not (set(v)&set(options.get(k,{})))
             for k,v in seasonal_options.items()),
         "SEASON_ITEM_OPTIONS_INVALID_OR_DUPLICATED")
    for slot,opts in seasonal_options.items():
        options.setdefault(slot,{}).update(items.checked_options(opts))
    need(set(options)<=set(ids) and
         "head" in options and
         sum(len(v["gem_id"].split("/")) for slot,v in options.items()
             if slot!="head" and "gem_id" in v)==6,
         "PHYSICAL_GEM_LAYOUT_NOT_STAGED")
    rows={slot:{"slot":slot,"item_id":item_id,
                "ilevel":target_ilevel,
                "options":items.checked_options(options.get(slot,{}))}
          for slot,item_id in ids.items()}
    for raw in trinkets:
        need(type(raw) is dict and
             set(raw)=={"slot","item_id","options"} and
             raw["slot"] in ("trinket1","trinket2"),
             "USER_TRINKET_FIELDS")
        rows[raw["slot"]]={
            "slot":raw["slot"],"item_id":items.checked_id(raw["item_id"]),
            "ilevel":target_ilevel,
            "options":items.checked_options(raw["options"])}
    required_slots=physical_slots|{"trinket1","trinket2"}
    need(set(rows)==required_slots and len(rows) in (15,16),
         "COMPLETE_FIFTEEN_OR_SIXTEEN_PHYSICAL_SLOTS")
    # Explicit default_actions lets SimulationCraft select its built-in APL;
    # no season profile, copied class action list or proprietary rotation.
    settings=[
      # Absent on legacy v144: preserve byte-identical input/cache identity.
      *(["item_db_source=local"] if
        season.get("simc_item_db_source")=="local" else []),
      contract["simc_class"]+"=target_"+contract["simc_spec"],
      "level="+str(season["character_level"]),
      "spec="+contract["simc_spec"],
      "race="+character["race"],
      "talents="+character["talents"],
      "role="+contract["role"],
      "position="+contract["position"],
      "default_actions=1",
      *(name+"="+season["default_consumables"][name] for name in
        ("flask","food","potion","augmentation","omnium_talents")),
      "fight_style=Patchwerk",
      "desired_targets="+str(combat["targets"]),
      "max_time="+str(combat["duration_seconds"]),
      "vary_combat_length=0",
      "fixed_time=1",
      "optimal_raid="+("1" if combat["raid_buffs"] else "0"),
      "iterations=35",
      "threads=1",
      # v098 will replace these preliminary placeholders when the path
      # is integrated; do not interpret them as the target's true B/T.
      *( "gear_"+stat+"=700" for stat in FIXED_STATES)
    ]
    profile="\n".join(settings+[items.equipment_line(
        slot,rows[slot]["item_id"],rows[slot]["ilevel"],
        rows[slot]["options"]) for slot in SLOT_ORDER if slot in rows])+"\n"
    receipt={"schema":SCHEMA,"status":"STAGED_NOT_USER_READY",
             "season":season["season"],"spec":cl+"/"+spec,
             "primary":contract["primary"],"family":contract["family"],
             "weapon_form":contract["weapon_form"],
             "four_tier_slots":list(info["four_tier_slots"]),
             "four_tier_item_ids":{s:rows[s]["item_id"]
                                   for s in info["four_tier_slots"]},
             "physical_slots":len(rows),
             "ordinary_gems":6,"source_profile_read":False,
             "simc_default_apl":True,"native_calls":0,
             "exact_static_rating_verified":False,
             "physical_socket_and_weapon_compatibility_verified":False,
             "chmv_budget_ready":False,"user_optimizer_ready":False}
    return profile,receipt,rows,set(info["four_tier_slots"])

def v098_inputs(character,trinkets,*,target_ilevel=334,combat=None,
                level_preview=False):
    """Translate season-built profile to the established v061/v098 tuple.

    No v132/v133 fixture, no per-spec APL, no second budget algorithm.
    The caller retains strict plan-only execution status until Native accepts
    the physical item/socket/weapon choices.
    """
    # One immutable season snapshot per build: avoid duplicate disk JSON
    # reads and prevent a mixed-season profile if data changes mid-run.
    season=catalog()
    need(type(level_preview) is bool,"LEVEL_PREVIEW_BOOL_REQUIRED")
    if level_preview:
        # Same-season candidate roster, but SimC must accept its IDs at
        # this selected ilvl. The 79-row reference B does not prove gear
        # compatibility. Never mutate the approved 334 catalog or cache.
        need(type(target_ilevel) is int and
             266<=target_ilevel<=344 and
             target_ilevel!=season["target_ilevel"],
             "NONDEFAULT_LEVEL_PREVIEW_OUTSIDE_REFERENCE")
        season={**season,"target_ilevel":target_ilevel}
    profile,receipt,rows,tier=compose(
        character,trinkets,target_ilevel=target_ilevel,combat=combat,
        season=season)
    cl,spec=character["class"],character["spec"]
    info=season["specializations"][cl+"/"+spec]
    contract=contracts.lookup(cl,spec)
    defaults=season["default_consumables"]
    gem=int(rows["head"]["options"]["gem_id"])
    need(gem in consumer.DIAMONDS,"STAGED_PRIMARY_DIAMOND_REQUIRED")
    # v108 consumes these exact SimC-native settings, not another effect model.
    consumer.default_choice(profile,rows["head"])
    fields=("crit_rating","haste_rating","mastery_rating","versatility_rating")
    need(defaults["flask_fixed_stat"] in fields and
         type(defaults["flask_budget_F"]) is int and
         defaults["flask_budget_F"]>=0 and
         type(defaults["gem_budget_J"]) is int and
         defaults["gem_budget_J"]>=0,
         "SEASON_CONSUMABLE_BUDGET_INVALID")
    flask_F={stat:(defaults["flask_budget_F"]
                   if stat==defaults["flask_fixed_stat"] else 0)
             for stat in fields}
    groups={slot:"tier" for slot in tier}
    groups.update({"trinket1":"trinkets","trinket2":"trinkets"})
    fifth=next(slot for slot in TIER_SLOTS if slot not in tier)
    tier_map=info["tier_ids"]
    cfg={"schema":scenario.SCHEMA,
         "character":{"class":cl,"spec":spec,"race":character["race"],
                      "role":contract["role"],"talents":character["talents"]},
         "source":{"kind":"user_supplied",
                   "profile_sha256":hashlib.sha256(profile.encode("utf8")).hexdigest()},
         "target":{"mode":"derived_ilevel","ilevel":target_ilevel,
                   "manual_total":None,"manual_total_scope":None},
         "equipment":{"tier":[rows[slot] for slot in TIER_SLOTS if slot in tier],
                      "special":[],"crafted":[],
                      "trinkets":[rows[slot] for slot in ("trinket1","trinket2")]},
         "consumables":{"gem_budget_J":defaults["gem_budget_J"],
                        "flask_budget_F":defaults["flask_budget_F"],
                        "special_gem_id":gem,
                        "flask":defaults["flask"],
                        "food":defaults["food"],"potion":defaults["potion"],
                        "weapon_temporary":None,
                        "weapon_temporary_fixed_rating":{stat:0 for stat in fields}},
         "combat":{"fight_style":"Patchwerk","targets":1,"duration_seconds":300,
                   "vary_combat_length_pct":0.0,"raid_buffs":True,
                   "bloodlust":"on_pull","external_buffs":[],"events":[]},
         "constraints":{"min_fraction":{stat:0.0 for stat in fields},
                        "max_fraction":{stat:1.0 for stat in fields},
                        "minimum_rating":{stat:0 for stat in fields}},
         "runtime":{"scout_iterations":35,"confirm_iterations":320,
                    "max_native_calls":6,"threads":1,"resume":True,"seed":1}}
    scenario.normalize(cfg)
    return (profile,cfg,rows,groups,contract["weapon_form"],flask_F,
            tier_map,(fifth,tier_map[fifth],rows[fifth]["item_id"]))
