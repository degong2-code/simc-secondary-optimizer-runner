#!/usr/bin/env python3
"""v134 shared v061 source-backed adapter for all newly pinned MID2 specs.

One adapter, no new optimizer or class-specific generators. Converts the v133
four-piece physical representative draft into the SAME tuple contract the v101
composer accepts. A source-native successful smoke is not a CHMV approval:
source-derived consumables and physical gems are checked downstream.
"""
from __future__ import annotations
import hashlib
import pathlib
import re

import v055_simc_item_selection as items
import v061_scenario_contract as scenario
import v132_dps_source_batch_smoke as pins
import v133_mid2_target_representative_preview as draft

STATS=tuple(scenario.STATS)
SLOTS=tuple(sorted(items.SLOTS))
# Both flasks have already been source/profile-Native accepted in historical
# representative families. Keeping a common F=165 avoids inventing unknown
# flask rating mechanics from an unverified different native consumable.
FLASK_F={
    "flask_of_the_shattered_sun_2":("crit_rating",165),
    "flask_of_the_blood_knights_2":("haste_rating",165)}
DEFAULT_FLASK="flask_of_the_shattered_sun_2"
SCHEMA="v134_shared_mid2_profile_adapter_v1"

class SharedAdapterBlocked(ValueError):pass

def need(ok,why):
    if not ok:raise SharedAdapterBlocked(why)

def key_of(pair):
    key="/".join(pair)
    need(key in pins.NEW,"V134_NOT_A_NEW_PINNED_SOURCE")
    return key

def flask_for(source):
    m=re.findall(r"^flask=(.*)$",source,re.M)
    need(len(m)==1,"V134_SOURCE_FLASK_UNIQUE")
    original=m[0]
    # The source may use a primary/effect flask or irregular abbreviated
    # SimC token. For the FREE secondary CHMV budget, always choose a known
    # 165-secondary-rating reference flask, not a guessed alternate F vector.
    flask=original if original in FLASK_F else DEFAULT_FLASK
    stat,amount=FLASK_F[flask]
    return flask,{x:amount if x==stat else 0 for x in STATS},original

def form_for(key,has_offhand):
    cls,sp=key.split("/")
    if has_offhand:
        return ("one_hand_frill" if cls in ("mage","priest","warlock")
                else "dual_one_hand")
    if cls=="hunter" and sp=="marksmanship":return "ranged"
    return "single_two_hand"

def source_metadata(key):
    original=pins.validate_source(key)
    preview,_=draft.draft(key)
    family=preview["material"]
    tier=dict(zip(draft.FIVE,draft.FIVE_TIER[key.split("/")[0]]))
    flask,F,old=flask_for(original["source"])
    return {"key":tuple(key.split("/")),"fixture":original["path"].replace("\\","/").rsplit("/",1)[-1],
            "source_git_blob":original["git_blob"],
            "family":family,"tier":tier,"fifth":(preview["offslot"],
               preview["offslot_item"]),"form":form_for(key,
               len(original["weapon_slots"])==2),
            "F":F,"flask":flask,"original_flask":old,
            "raw_weapons":original["weapon_slots"]}

def build(source,folder,key):
    key_s=key_of(key)
    original=pins.validate_source(key_s)
    need(source==original["source"],
         "V134_SOURCE_BYTES_DIFFER_FROM_OFFICIAL_FIXTURE")
    data,profile=draft.draft(key_s)
    info=source_metadata(key_s)
    slots={}
    for line in profile.splitlines():
        slot,sep,value=line.partition("=")
        if not sep or slot not in items.SLOTS:continue
        need(slot not in slots,"V134_DUPLICATE_REPRESENTATIVE_GEAR")
        fields=value.split(",")
        props={}
        for token in fields:
            a,b,c=token.partition("=")
            if b:props[a]=c
        need(props.get("id","").isdigit() and
             props.get("ilevel","").isdigit(),
             "V134_MISSING_ID_OR_TARGET_ILEVEL:"+slot)
        options={name:props[name] for name in items.OPTIONS if name in props}
        slots[slot]={"slot":slot,"item_id":int(props["id"]),
                     "ilevel":int(props["ilevel"]),"options":items.checked_options(options)}
    need(len(slots) in (15,16) and
         set(slots)==set(items.SLOTS)-(
             {"off_hand"} if "off_hand" not in slots else set()),
         "V134_PHYSICAL_SLOT_COVERAGE")
    chosen=set(data["four_tier_slots"])
    need(len(chosen)==4,"V134_FOUR_TIER_MUST_BE_EXACT")
    for slot in chosen:
        need(slots[slot]["item_id"]==info["tier"][slot],
             "V134_TIER_ITEM_ID_DRIFT:"+slot)
    offslot,ordinary=info["fifth"]
    need(slots[offslot]["item_id"]==ordinary and offslot not in chosen,
         "V134_FIFTH_ORDINARY_DRIFT")
    # Original source-owned APL, talents, weapon layout and trinket data.
    names={}
    for line in source.splitlines():
        a,b,c=line.partition("=")
        if b and a in ("spec","race","role","talents","food",
                       "potion","augmentation","omnium_talents"):
            need(a not in names,"V134_DUPLICATE_SOURCE_SETTING:"+a)
            names[a]=c
    need(all(names.get(k) for k in
         ("race","role","spec","talents","food","potion","augmentation",
          "omnium_talents")),"V134_SOURCE_CHARACTER_OR_CONSUMABLE_NOT_COMPLETE")
    need(names["spec"]==key[1],"V134_SPECIALIZATION_SOURCE_MISMATCH")
    # Keep observed source food/potion/Omnium; normalize only the flask
    # needed for exact fixed F, to the same preset used by existing product.
    output=[]
    for line in profile.splitlines():
        k,sep,_=line.partition("=")
        output.append("flask="+info["flask"]
                      if sep and k=="flask" else line)
    # v098/v122 require exactly four numeric gear_* placeholders before
    # the original v094 Native scheduler replaces them per CHMV candidate.
    # The source's worn-gear secondary total must never become the budget.
    need(not any(line.startswith("gear_"+stat+"=") for line in output
                 for stat in STATS),"V134_SOURCE_GEAR_STAT_OVERRIDE_UNEXPECTED")
    output.extend("gear_"+stat+"=700" for stat in STATS)
    new_profile="\n".join(output).rstrip()+"\n"
    gem=slots["head"]["options"].get("gem_id")
    need(gem is not None and gem.isdigit(),
         "V134_HEAD_DIAMOND_NEEDS_SOURCE_BACKED_SOCKET")
    cfg={"schema":scenario.SCHEMA,
        "character":{"class":key[0],"spec":key[1],
                     "race":names["race"],"role":names["role"],
                     "talents":names["talents"]},
        "source":{"kind":"user_supplied",
            "profile_sha256":hashlib.sha256(new_profile.encode("utf8")).hexdigest()},
        "target":{"mode":"derived_ilevel","ilevel":334,
                  "manual_total":None,"manual_total_scope":None},
        "equipment":{"tier":[slots[k] for k in draft.FIVE if k in chosen],
                     "special":[],"crafted":[],
                     "trinkets":[slots[k] for k in ("trinket1","trinket2")]},
        "consumables":{"gem_budget_J":138,"flask_budget_F":165,
            "special_gem_id":int(gem),"flask":info["flask"],
            "food":names["food"],"potion":names["potion"],
            "weapon_temporary":None,
            "weapon_temporary_fixed_rating":{k:0 for k in STATS}},
        "combat":{"fight_style":"Patchwerk","targets":1,
            "duration_seconds":300,"vary_combat_length_pct":0.0,
            "raid_buffs":True,"bloodlust":"on_pull",
            "external_buffs":[],"events":[]},
        "constraints":{"min_fraction":{k:0.0 for k in STATS},
            "max_fraction":{k:1.0 for k in STATS},
            "minimum_rating":{k:0 for k in STATS}},
        "runtime":{"scout_iterations":35,"confirm_iterations":320,
            "max_native_calls":4,"threads":1,"resume":True,"seed":1}}
    scenario.normalize(cfg)
    excluded=chosen|{"trinket1","trinket2"}
    fillers=[slots[k] for k in SLOTS if k in slots and k not in excluded]
    meta={"schema":SCHEMA,"source_class":key[0],
          "source_spec":key[1],"source_sha256":original["sha256"],
          "source_flask":info["original_flask"],
          "reference_flask_for_exact_F":info["flask"],
          "four_tier_slots":sorted(chosen),
          "fifth_non_tier_slot":offslot,"new_native_calls":0,
          "original_apl_line_count":data["apl_lines"]}
    return new_profile,cfg,fillers,meta

def producer(key):
    key_s=key_of(key)
    def produce(source,folder):
        return build(source,folder,key)
    return produce
