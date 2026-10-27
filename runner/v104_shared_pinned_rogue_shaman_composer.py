#!/usr/bin/env python3
"""v104: two NEW source-pinned generic representative input builders, no Native.

Subtlety Rogue / Elemental Shaman share ONE composer. Original SimC APL and
character scripts remain untouched; currently equipped source items are NOT
copied as a user's target baseline. Only explicitly pinned season IDs plus
corrected ordinary armor and verified source weapon layouts are retained.

These are limited first-use representative inputs (not a certification that
every default ordinary item has no proc or that all target-level variants are
Native tested). All effects and DPS belong to SimC.
"""
from __future__ import annotations
import hashlib,pathlib,re

import v055_simc_item_selection as item_mod
import v061_scenario_contract as scenario
import v102_ordinary_armor_seed_pool as ordinary
import v103_source_observed_weapon_types as weapons

STATS=scenario.STATS
# A set has process-specific iteration order under Python hash randomization.
# v106 replays a plan in a different Python process; byte-stable gear rows are mandatory.
ALL_SLOTS=tuple(sorted(item_mod.SLOTS))
TIER_ORDER=("head","shoulders","chest","hands","legs")
# Source class IDs are independently validated by the existing original
# fixture, original v068 Rogue class-tier contract and v078 Shaman fixture.
TIERS={
    "rogue":{"head":271510,"shoulders":271508,"chest":271513,
             "hands":271511,"legs":271509},
    "shaman":{"head":271483,"shoulders":271481,"chest":271486,
              "hands":271484,"legs":271482}}
# Per-spec minimal profile input blueprint only, no copied full equipment
# file, no optimizer, no parallel DPS driver. The 5th is ordinary gear.
PROFILES={
    ("rogue","subtlety"):{
        "filename":"v068_upstream_mid2_rogue_subtlety_reference.simc",
        "source_sha":"b704e6326959432a82d14a6b774c79183d5b2af4",
        "race":"dwarf","role":"attack",
        "tier":("head","shoulders","hands","legs"),
        "fifth":("chest",251159),
        "replace":{"back":268253,"wrists":268240},
        "gem":"240983","F":"crit_rating"},
    ("shaman","elemental"):{
        "filename":"v078_upstream_mid2_shaman_elemental_reference.simc",
        "source_sha":"c92d111e37bd684647e4637dcfef3ccb92864cde",
        "race":"tauren","role":"spell",
        "tier":("shoulders","chest","hands","legs"),
        "fifth":("head",249317),
        "replace":{"head":249317,"wrists":273775,"feet":249320},
        "gem":"240983","F":"crit_rating"}}
ROOT=pathlib.Path(__file__).resolve().parents[1]
FIXTURES=ROOT/"integration_probes"/"fixtures"

class SourceBlocked(ValueError):pass
def need(ok,why):
    if not ok:raise SourceBlocked(why)
def git_blob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+b"\0"+data).hexdigest()
def extract_gear(raw):
    ids={};options={}
    for line in raw.splitlines():
        if line.startswith("# Gear Summary"):break
        slot,sep,body=line.partition("=")
        if not sep or slot not in ALL_SLOTS:continue
        need(slot not in ids,"SOURCE_DUPLICATE_GEAR_SLOT:"+slot)
        fields=body.split(",")
        identifiers=[x[3:] for x in fields[1:] if x.startswith("id=")]
        need(len(identifiers)==1 and identifiers[0].isdigit(),
             "SOURCE_ITEM_ID_ABSENT:"+slot)
        ids[slot]=int(identifiers[0])
        options[slot]={}
        for field in fields[1:]:
            k,_,v=field.partition("=")
            if k in ("gem_id","enchant","enchant_id") and v:
                options[slot][k]=v
    return ids,options

def create_from_source(source,folder,key):
    need(key in PROFILES,"NEW_SOURCE_SPEC_UNSUPPORTED")
    spec=PROFILES[key]
    raw=source.encode("utf8")
    need(git_blob(raw)==spec["source_sha"],
         "SOURCE_PROFILE_GIT_BLOB_MISMATCH:"+"/".join(key))
    need(''+key[0]+'="' in source and
         "spec="+key[1] in source and
         "role="+spec["role"] in source,
         "SOURCE_CHARACTER_APL_IDENTITY_MISMATCH")
    lines=source.splitlines()
    names={}
    for line in lines:
        k,sep,v=line.partition("=")
        if sep and k in ("race","role","spec","talents","flask",
                         "food","potion","augmentation"):
            need(k not in names,"SOURCE_DUPLICATE_SETTING:"+k)
            names[k]=v
    need(all(k in names for k in ("race","role","spec","talents","flask",
                                  "food","potion")),"SOURCE_REQUIRED_CHARACTER_OR_BUFF_MISSING")
    actions=[l for l in lines if l.startswith("actions")]
    need(len(actions)>=15 and sum(l.startswith("actions=") for l in actions)==1,
         "SOURCE_APL_MISSING_OR_CHANGED")
    ids,mods=extract_gear(source)
    need(set(ids)==set(ALL_SLOTS),"SOURCE_SIXTEEN_PHYSICAL_GEAR_ITEMS_REQUIRED")
    observed=weapons.source_shape(key)
    need(set(observed["weapons"])==set(ids)&{"main_hand","off_hand"},
         "SOURCE_WEAPON_HAND_SET_MISMATCH")
    for hand,v in observed["weapons"].items():
        need(ids[hand]==v["item_id"],"SOURCE_WEAPON_ID_DRIFT:"+hand)
    tier=TIERS[key[0]]
    need(all(ids[slot]==tier[slot] for slot in spec["tier"])
         and all(slot in TIER_ORDER for slot in spec["tier"])
         and len(spec["tier"])==4,"FOUR_CLASS_TIER_SOURCE_ID_DRIFT")
    fifth,ordinary_id=spec["fifth"]
    need(fifth not in spec["tier"] and fifth in TIER_ORDER
         and set(spec["tier"])|{fifth}==set(TIER_ORDER),
         "FIFTH_CLASS_TIER_LAYOUT_DRIFT")
    need(ordinary_id==ordinary.row(
          "leather" if key[0]=="rogue" else "mail",fifth,334)["item_id"],
         "FIFTH_ORDINARY_MATERIAL_SLOT_ID_NOT_READY")
    material="leather" if key[0]=="rogue" else "mail"
    for slot,id_ in spec["replace"].items():
        # Ordinary replacements must be precisely from the source-checked pool,
        # except the independently source-shared cloak (cross-class back).
        if slot=="back":
            need(id_==268253 and
                 "back=silken_voodoo_drape,id=268253," in
                 (FIXTURES/"v078_upstream_mid2_shaman_elemental_reference.simc").read_text("utf8"),
                 "SHARED_CLOAK_SOURCE_MISSING")
        else:
            need(ordinary.row(material,slot,334)["item_id"]==id_,
                 "REPLACEMENT_ARMOR_MATERIAL_OR_SLOT_MISMATCH:"+slot)
        ids[slot]=id_
        # Do not copy bonus/random-stat modifiers from a discarded item.
        mods[slot]={}
    # Standardized representative items: preserve source-proven gem/enchant
    # only for unchanged items; no source bonus_id/proc redirect leakage.
    # Item after a substitution has no inherited crafted/random modifiers.
    for slot,id_ in ids.items():
        if slot in spec["tier"]:
            need(id_==tier[slot],"REPRESENTATIVE_FOUR_CLASS_TIERS_REQUIRED")
            mods[slot]={k:v for k,v in mods[slot].items()
                        if k in ("gem_id","enchant","enchant_id")}
    # Reapply one special head gem for corrected Hunter mail head, same as v086.
    if key==("shaman","elemental"):
        mods["head"]={"gem_id":"240983"}
    # Source-supplied Rogue dual-wield offhand is a crafted dagger; its
    # exact recipe is a source variant, not a locked special L.
    if key==("rogue","subtlety"):
        mods["off_hand"]["crafted_stats"]="36/49"
    eq={slot:{"slot":slot,"item_id":item_id,"ilevel":334,
              "options":item_mod.checked_options(mods[slot])}
        for slot,item_id in ids.items()}
    # Ensure the profile has exactly one target assignment for replace_assignments.
    settings={"fight_style":"Patchwerk","desired_targets":"1",
              "max_time":"300","optimal_raid":"1","threads":"1",
              "iterations":"35","vary_combat_length":"0",
              "fixed_time":"1","race":spec["race"]}
    settings.update({"gear_"+stat:"700" for stat in STATS})
    output=[];seen=set()
    for line in lines:
        if line.startswith("# Gear Summary"):break
        k,sep,_=line.partition("=")
        if sep and (k in ALL_SLOTS or k=="temporary_enchant"):
            continue
        if sep and k in settings:
            need(k not in seen,"DUPLICATE_SOURCE_OVERRIDE:"+k)
            seen.add(k)
            continue
        output.append(line)
    output.extend(k+"="+v for k,v in settings.items())
    output.extend(item_mod.equipment_line(
         slot,eq[slot]["item_id"],334,eq[slot]["options"])
         for slot in ALL_SLOTS)
    profile="\n".join(output).rstrip()+"\n"
    need([s for s in profile.splitlines() if s.startswith("actions")]==actions,
         "ORIGINAL_APL_CONTENT_CHANGED")
    need("temporary_enchant=" not in profile,
         "SOURCE_OIL_DOUBLE_APPLIED")
    normal={"schema":scenario.SCHEMA,
         "character":{"class":key[0],"spec":key[1],"race":spec["race"],
                      "role":spec["role"],"talents":names["talents"]},
         "source":{"kind":"user_supplied",
                   "profile_sha256":hashlib.sha256(profile.encode("utf8")).hexdigest()},
         "target":{"mode":"derived_ilevel","ilevel":334,
                   "manual_total":None,"manual_total_scope":None},
         "equipment":{"tier":[eq[s] for s in spec["tier"]],
                      "special":[],"crafted":[],
                      "trinkets":[eq[s] for s in ("trinket1","trinket2")]},
         "consumables":{"gem_budget_J":138,"flask_budget_F":165,
                        "special_gem_id":int(spec["gem"]),
                        "flask":names["flask"],"food":names["food"],
                        "potion":names["potion"],
                        "weapon_temporary":None,
                        "weapon_temporary_fixed_rating":{stat:0 for stat in STATS}},
         "combat":{"fight_style":"Patchwerk","targets":1,
                   "duration_seconds":300,"vary_combat_length_pct":0.0,
                   "raid_buffs":True,"bloodlust":"on_pull",
                   "external_buffs":[],"events":[]},
         "constraints":{"min_fraction":{stat:0.0 for stat in STATS},
                        "max_fraction":{stat:1.0 for stat in STATS},
                        "minimum_rating":{stat:0 for stat in STATS}},
         "runtime":{"scout_iterations":35,"confirm_iterations":320,
                    "max_native_calls":4,"threads":1,"resume":True,"seed":1}}
    included=set(spec["tier"])|{"trinket1","trinket2"}
    fillers=[eq[s] for s in ALL_SLOTS if s not in included]
    need(len(fillers)==10 and
         len({s for s in eq})==16,"PHYSICAL_GEAR_COUNTS_CHANGED")
    scenario.normalize(normal)
    meta={"source_class":key[0],"source_spec":key[1],
          "original_apl_line_count":len(actions),
          "four_tier_slots":list(spec["tier"]),
          "fifth_non_tier_slot":fifth,
          "ordinary_replacements":dict(spec["replace"]),
          "new_native_calls":0,
          "new_exact_static_variant_verified":False}
    return profile,normal,fillers,meta

def producer(key):
    """Reusable lightweight closure, no per-spec whole equipment factory."""
    def produce(source,folder):
        return create_from_source(source,folder,key)
    return produce

F_DECLARED={"crit_rating":165,"haste_rating":0,
            "mastery_rating":0,"versatility_rating":0}
