#!/usr/bin/env python3
"""v051 — bounded crafted armor/weapon scaffolding for two embellishments.

A representative gear input bridge, NOT an equipment optimizer, crafted item
enumerator, or promotion of the unapproved Developer Notes v1.1 candidate.
The native item's static CHMV *sum* is a flexible budget; an observed pair
(e.g. crafted_stats=49/36) is NOT a lower-bound or fixed optimization split.
Inherent effects, class-compatibility, gear slots and weapon performance must
be verified in actual SimC input before calling an optimization product-ready.
"""
from __future__ import annotations
import argparse,json,pathlib,re,sys
import v046_static_item_cache as cache

SCHEMA="v051_crafted_embellishment_bridge_v1"
REF_SCHEMA="v051_crafted_slots_and_weapon_id_reference_v1"
STATS=cache.STATS
ARMORS=frozenset(("cloth","leather","mail","plate"))
SIMC_SLOTS=frozenset(("head","shoulders","back","chest","wrists","hands","waist",
                     "legs","feet","neck","finger1","finger2",
                     "main_hand","off_hand","trinket1","trinket2"))
FORBIDDEN_BASE_FIELDS=frozenset(("gear_crit_rating","gear_haste_rating","gear_mastery_rating",
                                "gear_versatility_rating"))

def need(ok,reason):
    if not ok:raise cache.CacheBlocked(reason)

def load_reference(path):
    data=json.loads(path.read_text(encoding="utf-8"))
    need(data.get("schema")==REF_SCHEMA and data.get("season")==cache.SEASON,
         "REFERENCE_SCHEMA_CHANGED")
    rows=data.get("item_records")
    need(type(rows) is list and 8<=len(rows)<=500,"REFERENCE_SIZE")
    by_id={}
    armors=set();weapons=0
    for row in rows:
        id_=row["item_id"]
        need(type(id_) is int and id_>0 and id_ not in by_id,"DUPLICATE_OR_INVALID_ID")
        need(row["slot"] in SIMC_SLOTS and row["kind"] in ("armor","weapon"),
             "UNSUPPORTED_SLOT_OR_KIND")
        need(type(row.get("source_url")) is str and row["source_url"].startswith("https://"),
             "MISSING_SOURCE")
        by_id[id_]=row
        if row["kind"]=="weapon":weapons+=1
        elif row["armor_family"] in ARMORS:armors.add(row["armor_family"])
    need(armors==ARMORS and weapons>=3,"MISSING_CRAFT_CATEGORY")
    return data,by_id

def crafted_token(value):
    # These are two SimC secondary-stat IDENTIFIERS, not amounts of rating.
    need(type(value) is str and re.fullmatch(r"[0-9]{1,3}/[0-9]{1,3}",value),
         "CRAFTED_STAT_TOKEN_INVALID")
    a,b=(int(x) for x in value.split("/"))
    need(a!=b and {a,b}.issubset({32,36,40,49}),
         "CRAFTED_STAT_PAIR_UNSUPPORTED")
    return value

def validate_two_slots(pieces,armour_type,reference,tier_slots=(),special_slots=()):
    need(armour_type in ARMORS,"UNSUPPORTED_ARMOR_FAMILY")
    need(type(pieces) is list and len(pieces)==2,"EXACTLY_TWO_EMBELLISHED_PIECES")
    by_id=reference[1]
    blocked=set(tier_slots)|set(special_slots)
    need(all(k in SIMC_SLOTS for k in blocked),"BLOCKED_SLOT_INVALID")
    used=set();checked=[]
    for p in pieces:
        need(type(p) is dict and set(p)==
            {"item_id","item_level","slot","crafted_stats","embellishment"},
            "PIECE_CONTRACT_FIELDS")
        ref=by_id.get(p["item_id"])
        need(ref is not None,"CRAFTED_ITEM_NOT_IN_CATALOG")
        need(type(p["item_level"]) is int and p["item_level"]>0,
             "ITEM_LEVEL_INVALID")
        need(p["slot"]==ref["slot"] and p["slot"] not in blocked and
             p["slot"] not in used,"CRAFT_SLOT_OVERLAP")
        if ref["kind"]=="armor":
            need(ref["armor_family"] in (armour_type,"any"),
                 "WRONG_ARMOR_CLASS")
        crafted_token(p["crafted_stats"])
        need(type(p["embellishment"]) is str and
             re.fullmatch(r"[a-z][a-z0-9_]{1,80}",p["embellishment"]),
             "EMBELLISHMENT_INVALID")
        used.add(p["slot"])
        checked.append({"item_id":p["item_id"],"slot":p["slot"],
                        "requested_itemlevel":p["item_level"],
                        "crafted_stats_token":p["crafted_stats"],
                        "embellishment_name":p["embellishment"],
                        "effect_native_verified":False,
                        "slot_applicability_verified":False})
    return {"schema":SCHEMA,"status":"PLAN_ONLY_NEEDS_SIMC_EFFECT_VALIDATION",
            "pieces":checked,"embellishment_count":2,
            "selected_slots":sorted(used),
            "tier_slots_preserved":sorted(blocked&set(tier_slots)),
            "secondary_pair_treated_as_fixed_floor":False,
            "crafted_total_secondary_flexible":True,
            "gear_combo_optimization":False,
            "product_code_integrated":False,
            "official_policy_promoted":False}

def native_crafted_budget(data,item_id,item_level,slot,crafted_stats):
    """Exact base crafted variant, fail on miss; NO math from WEQUIP scaling."""
    crafted_token(crafted_stats)
    identity={"season":cache.SEASON,"item_id":item_id,
      "ilevel":item_level,"slot":cache.normalize_slot(slot),
      "options":{"crafted_stats":crafted_stats}}
    key=cache.digest(identity)
    found=data["variants"].get(key)
    need(found is not None,"SIMC_NATIVE_CRAFTED_VARIANT_NOT_COLLECTED")
    need(found["source_kind"]=="NATIVE_JSON2_RESOLVED_VARIANT"
         or found["source_kind"]=="USER_REQUESTED_MANUAL_CORRECTION",
         "NON_NATIVE_CRAFTED_STAT_SOURCE")
    need(found["static_digest"]==cache.digest(found["static"]),"TAMPERED_STAT")
    secondary=found["static"]["secondary"]
    need(set(secondary)==set(STATS) and
         all(type(x) is int and x>=0 for x in secondary.values()),
         "INVALID_CRAFTED_STATS")
    vals=[x for x in secondary.values() if x>0]
    need(len(vals)==2 and abs(vals[0]-vals[1])<=1,
         "CRAFTED_50_50_NATIVE_ASSUMPTION_NOT_MET")
    return {"status":"NATIVE_STATIC_SECONDARY_BUDGET_ONLY",
      "item_id":item_id,"ilevel":item_level,
      "crafted_token_is_STAT_ID_PAIR_not_rating":crafted_stats,
      "native_static_CHMV_total":sum(vals),
      "observed_base_split_for_DIAGNOSTICS_ONLY":secondary,
      "free_allocation_floor_from_base_split":{s:0 for s in STATS},
      "locked_derived_only_from_special_effect_items_not_this_base_pair":True,
      "primary_stats_from_native":found["static"]["primary_other"],
      "weapon_if_native":found["static"]["weapon_if_native"],
      "requires_real_SimC_item_embl_effect_check":True,
      "native_itemlevel_reachability_attested":False}

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("--catalog",type=pathlib.Path,required=True)
    ap.add_argument("--cache",type=pathlib.Path,required=True)
    ap.add_argument("--out",type=pathlib.Path,required=True)
    opt=ap.parse_args(argv)
    try:
        ref=load_reference(opt.catalog)
        native=cache.load(opt.cache)
        already=[]
        for id_ in (239648,239656):
            for level in (331,334):
                try:
                    slot="wrists" if id_==239648 else "back"
                    already.append(native_crafted_budget(native,id_,level,slot,"49/36"))
                except cache.CacheBlocked as e:
                    already.append({"id":id_,"ilevel":level,"status":"NOT_POPULATED",
                                    "reason":str(e)})
        summary={"schema":SCHEMA,"status":"REFERENCES_AND_NATIVE_BUDGET_INSPECTED_ONLY",
                 "references":len(ref[1]),"native_baseline_samples":already,
                 "all_four_armor_types_present":True,
                 "crafting_weapons_present":True,"all_recipies_complete":False,
                 "source_native_itemlevel_reachability_verified":False,
                 "product_code_integrated":False,"official_policy_promoted":False}
        opt.out.parent.mkdir(parents=True,exist_ok=True)
        opt.out.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print("V051",summary["status"],len(ref[1]),"examples",len(already))
        return 0
    except Exception as err:
        print("V051 BLOCKED",type(err).__name__,str(err),file=sys.stderr)
        return 3
if __name__=="__main__":sys.exit(main())
