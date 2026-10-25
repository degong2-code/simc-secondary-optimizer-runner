#!/usr/bin/env python3
"""v061 — portable, bounded, class-neutral scenario INPUT contract.

This is a strict normalized input boundary, not a character builder, equipment
optimizer, SimC effect gate, native gear lookup, or original v016 product merge.

Official policy is T=G+J+F. For an ilvl-derived target, G is UNKNOWN until
actual non-trinket representative equipment is assembled/resolved from Native
static cache. Manual T must already include J+F. Weapon-oil or trinket stats
stay external to T; never silently promote v059's oil-inclusive pilot.

SimC alone models all items, gems, procs, APL, combat mechanics and DPS.
"""
from __future__ import annotations
import hashlib,json,math,re
from copy import deepcopy

import v055_simc_item_selection as selector
import v046_static_item_cache as static_cache

SCHEMA="v061_scenario_contract_v1"
STATS=tuple(static_cache.STATS)
ROLE_SET=frozenset(("attack","spell","tank","heal"))
CLASSES=frozenset(("deathknight","demonhunter","druid","evoker","hunter","mage",
    "monk","paladin","priest","rogue","shaman","warlock","warrior"))
TIER_SLOTS=frozenset(("head","shoulders","chest","hands","legs"))
SOURCE_MODES=frozenset(("simc_standard","user_supplied"))
TARGET_MODES=frozenset(("derived_ilevel","manual_total"))
MANUAL_TOTAL_SCOPE="INCLUDES_G_J_F_EXCLUDES_EXTERNAL"
OIL_POLICY="EXTERNAL_FIXED_NO_T_REDEFINITION"
HASH_RE=re.compile(r"[0-9a-f]{64}")
TOKEN_RE=re.compile(r"[a-zA-Z0-9_:'/-]{1,200}")
NAME_RE=re.compile(r"[a-z][a-z0-9_]{1,95}")
KEYS_TOP={"schema","character","source","target","equipment","consumables",
          "combat","constraints","runtime"}

class ScenarioInvalid(ValueError):pass

def need(condition,reason):
    if not condition:raise ScenarioInvalid(reason)

def keys_exact(obj,keys,label):
    need(type(obj) is dict and set(obj)==set(keys),label+"_FIELDS")
    return obj

def text_token(val,label,nullable=False):
    if val is None and nullable:return None
    need(type(val) is str and bool(TOKEN_RE.fullmatch(val)),label+"_TOKEN")
    return val

def positive_int(val,label,lower=1,upper=10000):
    need(type(val) is int and lower<=val<=upper,label+"_INT")
    return val

def vector(v,label):
    keys_exact(v,STATS,label)
    need(all(type(v[k]) is int and 0<=v[k]<=100000 for k in STATS),
         label+"_VALUES")
    return dict(v)

def shares(v,label):
    keys_exact(v,STATS,label)
    need(all(type(v[k]) in (float,int) and math.isfinite(v[k])
          and 0<=v[k]<=1 for k in STATS),label+"_VALUES")
    return dict(v)

def entry(data,kind):
    keys_exact(data,("slot","item_id","ilevel","options"),kind+"_ITEM")
    slot=data["slot"]
    need(slot in selector.SLOTS,kind+"_SLOT_UNKNOWN")
    selector.checked_id(data["item_id"])
    selector.checked_level(data["ilevel"])
    options=selector.checked_options(data["options"])
    if kind=="trinket":
        need(slot in ("trinket1","trinket2"),"TRINKET_WRONG_SLOT")
        need("crafted_stats" not in options and "embellishment" not in options,
             "TRINKET_CRAFTED_NOT_IN_CONTRACT")
    else:
        need(slot not in ("trinket1","trinket2"),kind+"_TRINKET_SLOT")
    if kind=="tier":
        need(slot in TIER_SLOTS,"TIER_INVALID_SLOT")
        need("embellishment" not in options,"TIER_NO_EMBELLISHMENT")
    return {"slot":slot,"item_id":data["item_id"],
            "ilevel":data["ilevel"],"options":options}

def equipment(raw):
    keys_exact(raw,("tier","special","crafted","trinkets"),"EQUIPMENT")
    need(all(type(raw[k]) is list for k in raw),"EQUIPMENT_LISTS")
    need(len(raw["tier"])==4,"TIER_MUST_BE_FOUR")
    need(len(raw["trinkets"])==2,"TWO_TRINKETS_REQUIRED")
    need(len(raw["special"])<=8 and len(raw["crafted"])<=12,
         "SPECIAL_CRAFT_BOUNDS")
    out={kind:[entry(i,"trinket" if kind=="trinkets" else "tier"
                       if kind=="tier" else kind)
               for i in raw[kind]]
         for kind in ("tier","special","crafted","trinkets")}
    need({i["slot"] for i in out["trinkets"]}=={"trinket1","trinket2"},
         "TRINKET_SLOTS_NOT_EXACT")
    all_rows=sum((out[k] for k in ("tier","special","crafted","trinkets")),[])
    used=[i["slot"] for i in all_rows]
    need(len(set(used))==len(used),"GEAR_SLOT_COLLISION")
    need(len({i["item_id"] for i in all_rows})==len(all_rows),
         "DUPLICATE_EQUIPPED_ITEM_ID")
    emb=sum("embellishment" in i["options"] for i in all_rows)
    need(emb<=2,"MORE_THAN_TWO_EMBELLISHMENTS")
    need(all("embellishment" not in i["options"] for i in out["special"]),
         "EMBELLISHMENTS_USE_CRAFTED_GEAR")
    return out,emb

def normalize(doc):
    keys_exact(doc,KEYS_TOP,"SCENARIO")
    need(doc["schema"]==SCHEMA,"SCENARIO_SCHEMA")

    char=keys_exact(doc["character"],
         ("class","spec","race","talents","role"),"CHARACTER")
    need(char["class"] in CLASSES,"UNSUPPORTED_CLASS")
    need(char["role"] in ROLE_SET,"UNSUPPORTED_ROLE")
    for k in ("spec","race","talents"):
        text_token(char[k],"CHARACTER_"+k)

    source=keys_exact(doc["source"],("kind","profile_sha256"),"SOURCE")
    need(source["kind"] in SOURCE_MODES,"PROFILE_SOURCE_KIND")
    sha=source["profile_sha256"]
    need((sha is None and source["kind"]=="simc_standard") or
         (type(sha) is str and bool(HASH_RE.fullmatch(sha))),
         "PROFILE_SHA")
    if source["kind"]=="user_supplied":
        need(sha is not None,"USER_PROFILE_HASH_REQUIRED")

    target=keys_exact(doc["target"],
         ("mode","ilevel","manual_total","manual_total_scope"),"TARGET")
    need(target["mode"] in TARGET_MODES,"TARGET_MODE")
    positive_int(target["ilevel"],"TARGET_ILEVEL",1,1000)
    if target["mode"]=="manual_total":
        positive_int(target["manual_total"],"MANUAL_TOTAL",1,100000)
        need(target["manual_total_scope"]==MANUAL_TOTAL_SCOPE,
             "MANUAL_SCOPE_REQUIRED")
    else:
        need(target["manual_total"] is None and
             target["manual_total_scope"] is None,
             "DERIVED_MODE_MUST_WAIT_FOR_NATIVE_G")

    gear,emb_count=equipment(doc["equipment"])

    consume=keys_exact(doc["consumables"],
        ("gem_budget_J","flask_budget_F","special_gem_id",
         "flask","food","potion","weapon_temporary","weapon_temporary_fixed_rating"),
        "CONSUMABLES")
    J=positive_int(consume["gem_budget_J"],"J",0,100000)
    F=positive_int(consume["flask_budget_F"],"F",0,100000)
    sg=consume["special_gem_id"]
    if sg is not None:selector.checked_id(sg)
    for k in ("flask","food","potion","weapon_temporary"):
        text_token(consume[k],k,nullable=True)
    external_oil=vector(consume["weapon_temporary_fixed_rating"],
                        "WEAPON_TEMPORARY_EXTERNAL")
    if consume["weapon_temporary"] is None:
        need(sum(external_oil.values())==0,
             "TEMPORARY_STATS_REQUIRE_SELECTED_ENCHANT")

    combat=keys_exact(doc["combat"],
         ("fight_style","targets","duration_seconds","vary_combat_length_pct",
          "raid_buffs","bloodlust","external_buffs","events"),"COMBAT")
    text_token(combat["fight_style"],"FIGHT_STYLE")
    positive_int(combat["targets"],"TARGETS",1,40)
    positive_int(combat["duration_seconds"],"DURATION",1,3600)
    need(type(combat["vary_combat_length_pct"]) in (int,float) and
         0<=combat["vary_combat_length_pct"]<=100,
         "COMBAT_VARIATION")
    need(type(combat["raid_buffs"]) is bool,"RAID_BUFFS")
    need(type(combat["bloodlust"]) is str and
         combat["bloodlust"] in ("on_pull","off","simc_default"),
         "BLOODLUST_POLICY")
    need(type(combat["external_buffs"]) is list and
         type(combat["events"]) is list and
         len(combat["external_buffs"])<=30 and len(combat["events"])<=30,
         "COMBAT_EXTRA_LIST")
    for t in combat["external_buffs"]+combat["events"]:
        text_token(t,"EXTRA_COMBAT")

    bounds=keys_exact(doc["constraints"],
        ("min_fraction","max_fraction","minimum_rating"),"CONSTRAINTS")
    lows=shares(bounds["min_fraction"],"LOW_FRACTIONS")
    highs=shares(bounds["max_fraction"],"HIGH_FRACTIONS")
    manual_mins=vector(bounds["minimum_rating"],"MIN_RATING")
    need(all(lows[k]<=highs[k] for k in STATS) and
         sum(lows.values())<=1+1e-9 and sum(highs.values())>=1-1e-9,
         "UNFEASIBLE_FRACTION_BOUNDS")
    total=target["manual_total"]
    if total is not None:
        min_actual={k:max(manual_mins[k],math.ceil(lows[k]*total-1e-9)) for k in STATS}
        cap_actual={k:math.floor(highs[k]*total+1e-9) for k in STATS}
        need(all(min_actual[k]<=cap_actual[k] for k in STATS) and
             sum(min_actual.values())<=total<=sum(cap_actual.values()),
             "UNFEASIBLE_MANUAL_TOTAL_BOUNDS")

    runtime=keys_exact(doc["runtime"],
         ("scout_iterations","confirm_iterations","max_native_calls","threads",
          "resume","seed"),"RUNTIME")
    for k,lo,hi in (("scout_iterations",1,100000),
                    ("confirm_iterations",1,100000),
                    ("max_native_calls",1,100000),
                    ("threads",1,128)):
        positive_int(runtime[k],k.upper(),lo,hi)
    need(type(runtime["resume"]) is bool,"RESUME_BOOLEAN")
    if runtime["seed"] is not None:
        positive_int(runtime["seed"],"SEED",0,2**31-1)

    canonical=deepcopy(doc)
    canonical["equipment"]=gear
    canonical["constraints"]["minimum_rating"]=manual_mins
    canonical["constraints"]["min_fraction"]=lows
    canonical["constraints"]["max_fraction"]=highs
    canonical["consumables"]["weapon_temporary_fixed_rating"]=external_oil
    scenario_key=hashlib.sha256(
      json.dumps(canonical,sort_keys=True,ensure_ascii=False,
                 separators=(",",":"),allow_nan=False).encode("utf8")
    ).hexdigest()
    return {"schema":SCHEMA,"status":"VALID_SCENARIO_INPUT_NO_SIMC_EFFECT_GATE",
        "scenario":canonical,"scenario_digest":scenario_key,
        "equipment_count":sum(len(v) for v in gear.values()),
        "embellishment_count":emb_count,
        "fixed_four_tier_slots":sorted(x["slot"] for x in gear["tier"]),
        "user_trinkets_included_in_simc":True,
        "trinket_static_records_required":False,
        "budget":{"policy":"OFFICIAL_V1_2_T_G_PLUS_J_PLUS_F",
           "mode":target["mode"],"G":None,"J":J,"F":F,
           "T":total,"T_status":"MANUAL_USER_SUPPLIED_INCLUDES_J_F" if total
                 is not None else "WAIT_NATIVE_G",
           "external_oil_policy":OIL_POLICY,
           "external_temporary_rating":external_oil,
           "static_special_item_L":"WAIT_NATIVE_ITEM_STATIC",
           "native_static_stat_record_required_for_trinkets":False},
        "effect_modeling_owner":"SIMC",
        "special_effect_pre_admission_gate":False,
        "gear_combination_search":False,
        "product_v016_integrated":False,
        "official_project_source_modified":False}

def selected_lines(plan):
    """Only explicit selected equipment, not inventing missing ordinary slots."""
    items=plan["scenario"]["equipment"]
    return [selector.equipment_line(r["slot"],r["item_id"],r["ilevel"],r["options"])
            for group in ("tier","special","crafted","trinkets")
            for r in items[group]]

def derive_T(native_G,J,F):
    positive_int(native_G,"NATIVE_G",0,100000)
    positive_int(J,"J",0,100000)
    positive_int(F,"F",0,100000)
    return native_G+J+F

def result_cache_key(plan,simc_binary_sha256,profile_sha256,target_rating,
                     iterations):
    """DPS cache revision-sensitive; static item cache is NOT keyed this way."""
    need(bool(HASH_RE.fullmatch(simc_binary_sha256)) and
         bool(HASH_RE.fullmatch(profile_sha256)),"RESULT_CACHE_SHA")
    vector(target_rating,"RESULT_CANDIDATE")
    positive_int(iterations,"RESULT_ITERATIONS",1,100000)
    identity={"scenario_digest":plan["scenario_digest"],
       "native_binary_sha256":simc_binary_sha256,
       "full_profile_sha256":profile_sha256,
       "candidate":target_rating,
       "iterations":iterations,
       "threads":plan["scenario"]["runtime"]["threads"]}
    return static_cache.digest(identity)
