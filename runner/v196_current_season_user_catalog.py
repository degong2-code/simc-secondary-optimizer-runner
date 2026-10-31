#!/usr/bin/env python3
"""v196: small, versioned season option manifest for the local UI.

This is a UI/data bridge, NOT another collection engine. It reads an exact
v191 derived snapshot with SimC highest-source-rank enchant IDs. A collection
candidate MUST NOT become a selectable SimC/user option without budget and
per-item evidence. Already authorized v108/v188 choices remain unchanged.
"""
from __future__ import annotations
from collections import Counter
import json
from pathlib import Path

import v108_native_consumable_inputs as v108
import v188_user_choice_metadata as v188
import v197_enchant_effect_families as effect_groups
import v197_verified_effect_budget as fixed_budget
import v202_one_enchant_admission as observed_enchant

SCHEMA="v196_current_season_ui_catalog_v1"
SOURCE_SCHEMA="v196_source_first_enchant_candidates_v1"
DEFAULT=Path(__file__).resolve().parents[1]/"data/current_season_simc_enchant_candidates.json"
SLOTS={1:"head",3:"shoulders",5:"chest",20:"chest",8:"feet",11:"finger1/finger2"}

class CatalogBlocked(ValueError):
    pass
def need(condition,code):
    if not condition:
        raise CatalogBlocked(code)

def read(path=DEFAULT):
    path=Path(path)
    need(path.is_file() and 0<path.stat().st_size<=100_000,
         "SEASON_ENCHANT_CANDIDATES_ABSENT")
    document=json.loads(path.read_text("utf8"))
    need(type(document) is dict and
         document.get("schema")==SOURCE_SCHEMA and
         document.get("status")=="SOURCE_OBSERVED_NOT_NATIVE_BUDGET_VERIFIED" and
         document.get("season_game_build")=="12.1.5.70575" and
         document.get("simc_commit")==
             "710c2408bfd3ae4df71b8cd55cdf01f63fd6c926" and
         document.get("user_selectable") is False and
         document.get("source_artifact_id")==12961140046,
         "SOURCE_FIRST_ENCHANT_PROVENANCE_INVALID")
    related=document.get("related_source_counts")
    need(type(related) is dict and
         related=={
           "gear_item_candidates":511,"tier_piece_ids":65,
           "food_raw_item_candidates":192,"potion_raw_item_candidates":61,
           "food_handler_registrations":37,"potion_handler_registrations":5,
           "embellishment_darkmoon_registrations":20,
           "temporary_enchant_entries":117,"gem_property_records":2409}
         and document.get("related_source_status")==
             "EVIDENCE_ONLY_NO_NEW_USER_OPTIONS",
         "PINNED_SEASON_SOURCE_COUNTS_MISMATCH")
    rows=document.get("rows")
    need(type(rows) is list and len(rows)==38,
         "CURRENT_SEASON_ENCHANT_COUNT_INVALID")
    names=set();ids=set();group_counts=Counter();clean=[]
    for r in rows:
        need(type(r) is dict and
             set(r)=={"token","enchant_id","quality_rank","item_class",
                      "inventory_type_mask","item_subclass_mask","approved"},
             "SOURCE_FIRST_ENCHANT_ROW_FIELDS")
        name=r["token"];item_id=r["enchant_id"]
        need(type(name) is str and name.startswith("enchant_")
             and name not in names and
             type(item_id) is int and item_id>0 and item_id not in ids and
             r["approved"] is False and r["quality_rank"]==2,
             "SOURCE_FIRST_ENCHANT_ROW_INVALID")
        names.add(name);ids.add(item_id)
        mask=r["inventory_type_mask"]
        need(type(mask) is int and mask>=0 and
             type(r["item_subclass_mask"]) is int and
             r["item_subclass_mask"]>=0,"SOURCE_ENCHANT_MASK_INVALID")
        category=name.split("__")[0].replace("enchant_","")
        allowed={"boots","chest","helm","ring","shoulders","weapon"}
        need(category in allowed,"UNKNOWN_ENCHANT_CATEGORY")
        if category=="weapon":
            need(r["item_class"]==2 and mask==0,
                 "WEAPON_ENCHANT_SUBCLASS_REQUIRES_SEPARATE_CHECK")
            slots=["WEAPON_SUBCLASS_NOT_YET_USER_SLOT_CERTIFIED"]
        else:
            need(r["item_class"]==4 and mask>0,
                 "ARMOR_ENCHANT_INVENTORY_MASK_INVALID")
            types=[n for n in range(1,31) if mask&(1<<n)]
            need(types and all(t in SLOTS for t in types),
                 "UNRECOGNIZED_ARMOR_ENCHANT_INVENTORY_TYPE")
            slots=sorted(set(SLOTS[t] for t in types))
        group_counts[category]+=1
        clean.append({"token":name,"enchant_id":item_id,
                      "highest_source_quality_rank":r["quality_rank"],
                      "source_slots":slots,"kind":category,
                      "ui_selectable":False,
                      "blocked_reason":"EFFECT_STATIC_RATING_AND_NATIVE_INPUT_UNVERIFIED"})
    need(dict(group_counts)=={"boots":3,"chest":4,"helm":6,"ring":9,
                              "shoulders":6,"weapon":10},
         "CURRENT_SEASON_ENCHANT_CATEGORY_COUNTS_INVALID")
    return document,clean,dict(sorted(group_counts.items()))

def public_options(path=DEFAULT):
    source,enchants,counts=read(path)
    enchants=effect_groups.decorate(enchants)
    # A single source-classified nonCHMV choice has a separate two-Native
    # Windows E=0 witness. Do not generalize its rating classification to
    # unknown enchants, nor unlock the numeric rating-family choices.
    eagle_selectable=False
    try:
        import v206_nonchmv_eagle_selection as eagle
        eagle.evidence()
        eagle.source()
        matching=[r for r in enchants
                  if r["token"]=="enchant_ring__eyes_of_the_eagle"
                  and r["enchant_id"]==7967
                  and r["effect_family"]=="crit_effectiveness"]
        need(len(matching)==1,"EAGLE_SOURCE_EFFECT_CATALOG_DRIFT")
        matching[0]["ui_selectable"]=True
        matching[0]["blocked_reason"]=None
        matching[0]["static_CHMV_budget_impact"]="NO_INCREMENT_FROM_NONCHMV_EFFECT"
        matching[0]["native_E_zero_scope"]="WINDOWS_PALADIN_334_2_NATIVE_ONLY"
        eagle_selectable=True
    except (OSError,ValueError,KeyError):
        # Degraded catalog still lists the same 38 items without claiming
        # independent acceptance, budget numbers or broader Native proof.
        eagle_selectable=False
    # Optional v202 observation must never make the *existing* 38-entry
    # read-only catalog disappear if its separate evidence file is absent
    # or mismatched. Missing proof never unlocks any enchant.
    try:
        data,proof_sha=observed_enchant.read()
    except (observed_enchant.EnchantAdmissionBlocked,OSError,
            ValueError,KeyError):
        data=None
        proof_sha=None
    if data is not None:
        matching=[r for r in enchants if r["enchant_id"]==data["enchant_id"]]
        need(len(matching)==1 and matching[0]["ui_selectable"] is False,
             "NATIVE_EVIDENCE_ENCHANT_CATALOG_MISMATCH")
        matching[0]["measured_E_in_one_simc_native_scope"]=dict(data["static_enchant_E"])
        matching[0]["native_scope"]="mage/frost ilvl334 Linux 710c240 finger1"
        matching[0]["same_gear_override_delta_zero"]=True
        matching[0]["evidence_sha256"]=proof_sha
    labels=v188.labels()
    # The only actual user choices in this first stage are exactly the
    # legacy Native/source-verified tokens. Do not enable 192/61 raw DB2
    # food/potion candidates or new 38 enchant IDs.
    approved={
        k:[{"value":token,"label":label,"ui_selectable":True}
           for token,label in sorted(labels[k].items())]
        for k in ("food","potion","augmentation","diamond_id")}
    need(set(labels["food"])==set(v108.SUPPORTED["food"])|{"source_default"}
         and set(labels["potion"])==set(v108.SUPPORTED["potion"])|{"source_default"}
         and set(labels["augmentation"])==
             set(v108.SUPPORTED["augmentation"])|{"source_default"}
         and set(labels["diamond_id"])==
             {"0",*(str(x) for x in v108.DIAMONDS)},
         "V108_USER_APPROVED_CHOICES_DRIFT")
    source_classified=sum("source_effect_classification" in x for x in enchants)
    source_classification_counts={
        "static_chmv_rating":sum(bool(x.get("source_static_chmv_rating_present"))
                                  for x in enchants),
        "static_nonchmv_only_or_mixed":sum(
            bool(x.get("source_effect_classification",{}).get("static_components"))
            and not x.get("source_static_chmv_rating_present",False)
            for x in enchants),
        "spell_effects":sum(bool(x.get("source_effect_classification",{}).get("driver_spell_ids"))
                            for x in enchants),
        "native_E_measured":sum(x.get("source_native_E_status") not in
                                (None,"NOT_MEASURED") for x in enchants)
    }
    return {
        "schema":SCHEMA,"status":"SOURCE_COMBINED_WITH_CLEAR_APPROVAL_BOUNDARY",
        "season_build":source["season_game_build"],
        "one_enchant_native_evidence_status":(
            "EXACT_SCOPE_OBSERVED_READ_ONLY" if data is not None
            else ("OPTIONAL_RATING_EVIDENCE_UNAVAILABLE_EAGLE_SEPARATE"
                  if eagle_selectable else
                  "OPTIONAL_EVIDENCE_UNAVAILABLE_ALL_ENCHANT_CHOICES_LOCKED")),
        "simc_revision":source["simc_commit"],
        "source_artifact_id":source["source_artifact_id"],
        "related_source_counts":dict(source["related_source_counts"]),
        "related_source_status":source["related_source_status"],
        "existing_allowed_input_choices":approved,
        "proven_armor_embellishments":v188.public_embellishments(),
        "enchant_candidates":{"total":len(enchants),"groups":counts,
                              "items":enchants,"selectable_count":int(eagle_selectable),
                              "same_effect_stronger_ring_enchants":sum(
                               x["preferred_if_same_effect_source"]==
                                  "STRONGER_VARIANT_REPORTED" for x in enchants),
                              "effect_family_sources":list(
                                  effect_groups.SOURCE_REFERENCES),
                              "source_classified_count":source_classified,
                              "source_classification_counts":source_classification_counts,
                              "effect_classification_status":(
                                  "PINNED_SIMC_DBC_SPELLTEXT_AND_HANDLER_CLASSIFIED_NOT_NATIVE_GENERALIZED"
                                  if source_classified==38 else
                                  "SOURCE_CLASSIFICATION_INCOMPLETE")},
        "budget_effect_contract":{"schema":fixed_budget.SCHEMA,
              "fixed_enchant_E_part_of":"GEAR_G_ALREADY_INSIDE_FINAL_T",
              "requires_exact_companion_native_receipt":True,
              "no_extra_T_or_O_increment":True,
              "status":"NO_VERIFIED_ENCHANT_E_VECTOR_PROVIDED"},
        "future_categories":{
            "flask":"CURRENT_F_165_FIXED_NOT_ALTERNATIVE_VALIDATED",
            "ordinary_gems":"CURRENT_J_138_FIXED_NOT_ALTERNATIVE_VALIDATED",
            "special_diamonds":"TWO_PRIMARY_ONLY_ITEMS_ALREADY_ALLOWED",
            "temporary_enchants":"SOURCE_CANDIDATES_NOT_SLOT_BUDGET_CONNECTED",
            "additional_embellishments":"SIMC_EFFECTS_SOURCE_DISCOVERED_ITEM_SLOT_JOIN_PENDING",
            "food_potions_expanded":"DB2_RAW_192_FOOD_61_POTION_NOT_NATIVE_MATCHED",
        },
        "native_calls_now":0,"game_db_recollection_now":0,
        "new_approval_granted":eagle_selectable,
        "optimizer_or_cache_mutated":False
    }
