#!/usr/bin/env python3
"""v055: SimC-owned item effects, no static-stat/effect verification gate.

Build a representative SimC profile with user-selected crafted equipment,
up to two embellishments, and either trinket (including zero/no-reported
static-CHMV items). This builder does NOT simulate or judge proc semantics.

Static item cache is for G arithmetic only. A trinket is excluded from G,
so a cache miss on any trinket must NOT disable selection or force zero.
Names and recipe catalogs are advisory; a well-formed user item ID is valid
even when the crafting catalog has not yet been exhaustively populated.
"""
from __future__ import annotations
import json,pathlib,re
import v046_static_item_cache as cache

SCHEMA="v055_simc_owned_effect_selection_v1"
# SimC's equipment keywords, not invented WoW item identity.
SLOTS={"head","neck","shoulders","back","chest","wrists","hands",
       "waist","legs","feet","finger1","finger2","trinket1","trinket2",
       "main_hand","off_hand"}
CRAFT_SLOTS=SLOTS-{"trinket1","trinket2"} # restricted by caller's actual item type/recipe
GEAR_PREFIX=("gear_crit_rating=","gear_haste_rating=","gear_mastery_rating=","gear_versatility_rating=")
OPTIONS={"gem_id","bonus_id","enchant","enchant_id","crafted_stats",
         "embellishment","content_tuning","context"}
EXCLUDED_DEFAULT={250244} # opt-in can still be passed by explicit user id
ADVISORY_CRAFTED_IDS=pathlib.Path(__file__).resolve().parents[1]/"integration_probes/catalog/v057_crafted_gear_51_recipe_ids.json"

def require(ok,reason):
    if not ok:raise cache.CacheBlocked(reason)

def checked_id(v):
    require(type(v) is int and 0<v<10**10,"ITEM_ID_INVALID")
    return v

def checked_level(v):
    require(type(v) is int and 1<=v<=1000,"ITEM_LEVEL_INVALID")
    return v

def checked_options(options):
    require(type(options) is dict and set(options)<=OPTIONS,"ITEM_OPTIONS_NOT_SUPPORTED")
    out={}
    for name,value in sorted(options.items()):
        require(type(value) is str and bool(re.fullmatch(r"[a-zA-Z0-9_/:]{1,140}",value)),
                "ITEM_OPTION_VALUE_INVALID:"+name)
        if name=="crafted_stats":
            a=value.split("/")
            require(len(a)==2 and all(x.isdigit() for x in a) and
                    len(set(a))==2,"CRAFTED_STATS_TOKEN_INVALID")
        out[name]=value
    return out

def equipment_line(slot,item_id,ilevel,options=None):
    require(slot in SLOTS,"EQUIPMENT_SLOT_UNKNOWN")
    checked_id(item_id);checked_level(ilevel)
    kv=checked_options(options or {})
    # Only exactly the user-selected ID, ilvl and options. No synthetic proc value.
    segments=[f"{slot}=selected_{item_id}",f"id={item_id}",
              f"ilevel={ilevel}","source=local"]
    segments.extend(f"{k}={v}" for k,v in kv.items())
    return ",".join(segments)

def load_advisory_catalog(path=ADVISORY_CRAFTED_IDS):
    doc=json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    require(doc.get("schema")=="v057_midnight_s2_crafted_equipment_ids_v1" and
            doc.get("season")==cache.SEASON,"CRAFT_CATALOG_CHANGED")
    return {x["item_id"]:x for x in doc["items"]}

def inspect_selection(changes,reserved_tier_slots=(),reserved_special_slots=(),excluded_default=EXCLUDED_DEFAULT):
    """No DBC/stat-gate. Enforce bounded profile slots and <=2 embellishments."""
    require(type(changes) is list and 1<=len(changes)<=len(SLOTS),"SELECTION_COUNT_INVALID")
    blocked=set(reserved_tier_slots)|set(reserved_special_slots)
    require(blocked<=SLOTS,"RESERVED_SLOT_INVALID")
    seen=set();effect_count=0;unlisted=[]
    catalog=load_advisory_catalog()
    checked=[]
    for item in changes:
        require(type(item) is dict and set(item)=={"slot","item_id","ilevel","options"},
                "SELECTED_FIELDS_INVALID")
        slot=item["slot"];id_=checked_id(item["item_id"])
        require(slot in SLOTS and slot not in seen,"SLOT_DUPLICATE_OR_UNSUPPORTED")
        seen.add(slot);checked_level(item["ilevel"])
        opts=checked_options(item["options"])
        if "crafted_stats" in opts or "embellishment" in opts:
            require(slot not in blocked,"CRAFTED_PIECE_REPLACES_RESERVED_TIER_OR_SPECIAL")
        # A non-catalogued crafted ID may still be used: SimC will resolve it.
        if id_ not in catalog and "crafted_stats" in opts:unlisted.append(id_)
        effect_count+=int("embellishment" in opts)
        # A trinket can have no reported static values and remain fully usable.
        if slot.startswith("trinket"):
            require("crafted_stats" not in opts and "embellishment" not in opts,
                    "TRINKET_CRAFT_OPTION_NOT_THIS_CONTRACT")
        checked.append({"item_id":id_,"slot":slot,"ilevel":item["ilevel"],
                        "reported_static_chmv_required_for_selection":False,
                        "passes_item_to_simc_unmodified":True,
                        "selected_even_if_not_catalogued":id_ not in catalog,
                        "excluded_default_but_user_explicit_selection":id_ in excluded_default})
    require(effect_count<=2,"EMBELLISHMENT_LIMIT_EXCEEDED")
    return {"schema":SCHEMA,"status":"SELECTION_INPUT_READY_NO_EFFECT_GATE",
      "selected":checked,"user_selected_embellishment_count":effect_count,
      "unlisted_crafted_ids_allowed":sorted(set(unlisted)),
      "trinket_static_cache_required":False,
      "simc_effect_mechanics_owned_by_simc":True,
      "effect_support_prior_screen_not_required":True,
      "gear_optimization_not_performed":True,
      "product_code_integrated":False,"official_policy_promoted":False}

def apply_selection(reference,changes,reserved_tier_slots=(),reserved_special_slots=()):
    """Replace only equipment rows named in changes; leave APL/other gear alone.

    This adapter does not modify candidate gear_rating overrides; the separate
    CHMV injection stage must still reconcile budget and actual SimC output.
    """
    summary=inspect_selection(changes,reserved_tier_slots,reserved_special_slots)
    replacements={a["slot"]:equipment_line(a["slot"],a["item_id"],a["ilevel"],
                                           a["options"]) for a in changes}
    source=reference.splitlines()
    line_positions={}
    for i,line in enumerate(source):
        if line.startswith("#") or "=" not in line:continue
        key=line.split("=",1)[0]
        if key in replacements:
            line_positions.setdefault(key,[]).append(i)
    for key,pos in line_positions.items():
        require(len(pos)==1,"DUPLICATE_EXISTING_GEAR_SLOT:"+key)
        source[pos[0]]=replacements[key]
    for key in replacements:
        if key not in line_positions:source.append(replacements[key])
    final="\n".join(source)+"\n"
    for key in replacements:
        require(sum(s.startswith(key+"=") for s in final.splitlines())==1,
                "SELECTED_SLOT_DUPLICATED:"+key)
    return final,summary

def static_budget_lookup(c,slot,item_id,ilevel,options=None):
    """Report static value only if exact Native variant exists.

    Trinkets are ALWAYS outside CHMV pool G. Null means unobserved, NOT
    demonstrated 0, and does not affect either selection or SimC execution.
    """
    require(slot in SLOTS,"SLOT_UNKNOWN")
    checked_id(item_id);checked_level(ilevel);opts=checked_options(options or {})
    identity={"season":cache.SEASON,"item_id":item_id,"ilevel":ilevel,
              "slot":cache.normalize_slot(slot),"options":opts}
    item=c.get("variants",{}).get(cache.digest(identity))
    if slot.startswith("trinket"):
        v=item["static"]["secondary"] if item is not None else None
        return {"budget_category":"EXTERNAL_FIXED_TRINKET_NOT_G",
            "static_chmv_if_native":v,
            "static_chmv_status":"NATIVE_STATIC_PRESENT" if v is not None else "NOT_REPORTED_UNKNOWN_NOT_ZERO",
            "G_contribution":0,"selection_allowed":True,
            "simc_effect_calculation":"SIMC_OWNED_NOT_A_GATE"}
    require(item is not None,"NON_TRINKET_G_MISSING_NATIVE_STATIC")
    return {"budget_category":"G_NON_TRINKET",
            "G_contribution":sum(item["static"]["secondary"].values()),
            "static_chmv_if_native":item["static"]["secondary"],
            "static_chmv_status":"NATIVE_STATIC_PRESENT",
            "selection_allowed":True}
