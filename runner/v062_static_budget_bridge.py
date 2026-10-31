#!/usr/bin/env python3
"""v062: exact static G and special L from an explicitly assembled gear layout.

Consumes v061 P1 scenario + caller's standard *filler* gear + v046/v058
Native static cache; no item effects/procs/APL modeling or SimC calls.
Trinket stat JSON2 absence never blocks or implies proven 0.

G is a P2 static sum, not yet the FINAL injected CHMV: gem/enchant/consumable
double-addition still requires P3 numeric reconciliation in native JSON2.
"""
from __future__ import annotations
import math
import v046_static_item_cache as static_cache
import v061_scenario_contract as scenario

SCHEMA="v062_representative_static_budget_v1"
STATS=scenario.STATS
REQUIRED_NONTRINKET={"head","neck","shoulders","back","chest","wrists",
                     "hands","waist","legs","feet","finger1","finger2","main_hand"}
EXTRA_ALLOWED={"off_hand"}
MODIFIERS_WITH_BUDGET_AMBIGUITY={"gem_id","enchant","enchant_id"}
# v108 permits these PRIMARY/effect-only head diamonds; neither adds a
# flat secondary rating. The exact undecorated Native item variant may supply
# only its fixed L, never an inferred gem/proc effect or a forged item record.
PRIMARY_ONLY_HEAD_DIAMONDS=frozenset(("240983","240967"))
NATIVE_SOURCES={"NATIVE_JSON2_RESOLVED_VARIANT","USER_REQUESTED_MANUAL_CORRECTION"}

class BudgetBlocked(ValueError):pass
def need(x,reason):
    if not x:raise BudgetBlocked(reason)

def zero():
    return {k:0 for k in STATS}

def exact_identity(raw):
    return {"season":static_cache.SEASON,
            "item_id":raw["item_id"],"ilevel":raw["ilevel"],
            "slot":static_cache.normalize_slot(raw["slot"]),
            "options":raw["options"]}

def check_filler(items,selection):
    need(type(items) is list and len(items)<=len(REQUIRED_NONTRINKET)+1,
         "FILLER_LIST_INVALID")
    seen={r["slot"] for r in selection}
    out=[]
    for row in items:
        v=scenario.entry(row,"filler")
        need(v["slot"] in REQUIRED_NONTRINKET|EXTRA_ALLOWED,
             "FILLER_SLOT_UNKNOWN")
        need(v["slot"] not in seen,"FILLER_OVERWRITES_SELECTED_GEAR")
        seen.add(v["slot"]);out.append(v)
    missing=sorted(REQUIRED_NONTRINKET-seen)
    need(not missing,"REPRESENTATIVE_GEAR_SLOTS_UNFILLED:"+",".join(missing))
    return out

def get_native_secondary(cache,raw):
    key=static_cache.digest(exact_identity(raw))
    record=cache["variants"].get(key)
    if record is None:return None
    need(record.get("source_kind") in NATIVE_SOURCES and
         record.get("static_digest")==static_cache.digest(record.get("static")),
         "NATIVE_VARIANT_TAMPERED_OR_UNVERIFIED")
    stat=record["static"]["secondary"]
    scenario.vector(stat,"NATIVE_SECONDARY")
    return stat

def primary_only_head_gem(row):
    """True only for a head diamond whose flat secondary rating is zero."""
    return (row["slot"]=="head"
            and row["options"].get("gem_id") in PRIMARY_ONLY_HEAD_DIAMONDS
            and not (set(row["options"]) &
                     (MODIFIERS_WITH_BUDGET_AMBIGUITY-{"gem_id"})))

def undecorated_special(row):
    """Exact bare special identity: retain intrinsic options; remove only J/E.

    Never borrow a decorated variant's rating as the permanent special L.
    Native item stats for this bare variant must exist independently.
    """
    need(type(row) is dict and type(row.get("options")) is dict,
         "SPECIAL_BASE_ITEM_ROW_INVALID")
    return {**row,"options":{k:v for k,v in row["options"].items()
            if k not in MODIFIERS_WITH_BUDGET_AMBIGUITY}}

def compile_static_budget(contract,standard_filler,cache):
    need(type(contract) is dict and contract.get("schema")==scenario.SCHEMA
         and contract.get("status")=="VALID_SCENARIO_INPUT_NO_SIMC_EFFECT_GATE",
         "SCENARIO_NOT_NORMALIZED")
    static_cache.check_cache(cache)
    need(cache["season"]==static_cache.SEASON,"CACHE_SEASON_MISMATCH")
    cfg=contract["scenario"]
    eq=cfg["equipment"]
    chosen=sum((eq[k] for k in ("tier","special","crafted","trinkets")),[])
    standard=check_filler(standard_filler,chosen)
    all_items=chosen+standard
    nontrinket=[r for r in all_items if not r["slot"].startswith("trinket")]
    observed={};missing=[];modified=[]
    # A redirected tier item is NOT automatically special: ordinary tier can
    # retain a source-item modifier too. Only user-tagged selected special
    # catalyst slots protect their exact Native static L (one physical slot).
    specials=({r["slot"] for r in eq["special"]} |
              set(eq.get("catalyst_special_tier_slots",[])))
    locked=zero();G_components=zero()
    missing_special=[]
    for row in nontrinket:
        is_special=row["slot"] in specials
        # Special L must be measured in the exact bare item variant.
        # Gem J / enchant E are separate even when their equipped variant
        # has an independently cached SimC static gear record.
        source=undecorated_special(row) if is_special else row
        stat=get_native_secondary(cache,source)
        if stat is None:
            entry={"slot":row["slot"],"item_id":row["item_id"],
                   "ilevel":row["ilevel"],"identity":exact_identity(source)}
            missing.append(entry)
            if is_special:missing_special.append(entry)
            continue
        observed[row["slot"]]={"item_id":row["item_id"],
              "identity":exact_identity(row),"secondary":dict(stat),
              "sum":sum(stat.values())}
        if is_special and source["options"]!=row["options"]:
            # Profile binding always uses the full user's equipped options.
            # Numeric provenance alone points to the exact bare Native L.
            observed[row["slot"]]["numeric_source_identity"]=exact_identity(source)
        for k in STATS:G_components[k]+=stat[k]
        if is_special:
            # This is only the confirmed base L. No J/E enters locked.
            for k in STATS:locked[k]+=stat[k]
            if source["options"]!=row["options"]:
                observed[row["slot"]]["base_item_L_excludes"]=[
                    k for k in sorted(row["options"])
                    if k in MODIFIERS_WITH_BUDGET_AMBIGUITY]
        if MODIFIERS_WITH_BUDGET_AMBIGUITY.intersection(row["options"]):
            modified.append({"slot":row["slot"],"item_id":row["item_id"],
                 "reason":"GEM_ENCHANT_NUMERIC_ATTRIBUTION_REQUIRES_P3"})
    # Trinkets are outside G even if static data is present. Never require
    # such data to use an item or infer the unreported field is truly zero.
    trinket_status=[]
    for raw in eq["trinkets"]:
        external=get_native_secondary(cache,raw)
        trinket_status.append({"slot":raw["slot"],"item_id":raw["item_id"],
            "native_static_if_reported":external,
            "native_static_status":"NATIVE_OBSERVED" if external is not None
                                   else "UNREPORTED_UNKNOWN_NOT_ZERO",
            "included_in_G":False,"selection_allowed":True})
    declared_manual=cfg["target"]["mode"]=="manual_total"
    expected_T=contract["budget"]["T"]
    full_G=(sum(G_components.values()) if not missing else None)
    if not declared_manual and full_G is not None:
        expected_T=scenario.derive_T(full_G,contract["budget"]["J"],
                                     contract["budget"]["F"])
    locked_available=not missing_special
    candidate_possible=(expected_T is not None and locked_available)
    # P1 min bounds + actual selected fixed special stats; do not add L twice.
    effective_floor=None
    if candidate_possible:
        effective_floor={}
        for k in STATS:
            manual=cfg["constraints"]["minimum_rating"][k]
            share=cfg["constraints"]["min_fraction"][k]
            effective_floor[k]=max(locked[k],manual,
                                   math.ceil(share*expected_T-1e-9))
        caps={k:math.floor(expected_T*cfg["constraints"]["max_fraction"][k]+1e-9)
              for k in STATS}
        need(sum(effective_floor.values())<=expected_T<=sum(caps.values())
             and all(effective_floor[k]<=caps[k] for k in STATS),
             "SELECTED_SPECIAL_FLOOR_UNFEASIBLE")
    if not locked_available:
        status="NEEDS_NATIVE_SPECIAL_FIXED_L"
    elif expected_T is None:
        status="NEEDS_NATIVE_G_FOR_DERIVED_TARGET"
    elif missing and declared_manual:
        status="MANUAL_TARGET_READY_G_PARTIALLY_UNOBSERVED"
    else:
        status="STATIC_BUDGET_COMPILED_NEEDS_P3_NATIVE_RECONCILIATION"
    return {"schema":SCHEMA,"status":status,
       "scenario_digest":contract["scenario_digest"],
       "gear_items_total":len(all_items),
       "gear_nontrinket_slots":sorted(x["slot"] for x in nontrinket),
       "standard_filler_count":len(standard),
       "selected_trinkets":trinket_status,
       "native_gear_stats":observed,
       "missing_nontrinket_static":missing,
       "missing_special_fixed_static":missing_special,
       "G_if_complete":full_G,
       "G_partial_observed_vector_NOT_COMPLETE":G_components,
       "locked_L_when_all_specials_observed":locked if locked_available else None,
       "effective_floor_if_possible":effective_floor,
       "budget":{"mode":cfg["target"]["mode"],
          "T_official":expected_T,"J":contract["budget"]["J"],
          "F":contract["budget"]["F"],"official_formula":"T=G+J+F",
          "G_counts_selected_replacement_once":True,
          "external_temporary_rating":contract["budget"]["external_temporary_rating"],
          "oil_stays_OUTSIDE_T":True,
          "native_reconciliation_still_required":True,
          "ambiguous_gem_enchant_gear_rows":modified},
       "item_effects_owned_by_simc":True,
       "native_simc_calls":0,
       "automatically_lookup_only_exact_missing_nontrinket":True,
       "original_product_integrated":False}
