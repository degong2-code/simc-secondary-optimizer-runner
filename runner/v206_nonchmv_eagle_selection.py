#!/usr/bin/env python3
"""v206: exact source-classified non-CHMV enchant input, no DPS/effect model.

Only Eyes of the Eagle (enchant_id 7967), already present in the pinned
current-season v191 SimC generated table. The Windows two-Native comparison
shows E=0 in ONE Paladin 334 profile; it does not certify every loadout.
Other known rating rings must keep the separate v202/v204 fixed-E accounting.
Unknown effects and all other enchant choices remain locked.
"""
from __future__ import annotations
import json,pathlib,re
import v196_current_season_user_catalog as catalog
import v197_enchant_effect_families as families

SCHEMA="v206_exact_nonchmv_eagle_selection_v1"
CHOICE={"finger1":7967}
FIELD="selected_season_enchants"
PROOF=pathlib.Path(__file__).resolve().parents[1]/"data/v206_eagle_7967_windows_E0_proof.json"
E_ZERO={s:0 for s in ("crit_rating","haste_rating","mastery_rating","versatility_rating")}
NATIVE_SHA=("b8573662ebb14e2760942667a09b66e1126e685ba3e2a1e91809de20773c1424",
            "55a411f8c0424d2496230880a11777c2a05143086de87aefae189b39f87b9b34")

class EnchantChoiceBlocked(ValueError):pass
def need(ok,label):
    if not ok:raise EnchantChoiceBlocked(label)

def evidence():
    p=json.loads(PROOF.read_text(encoding="utf8"))
    need(type(p) is dict and
         p.get("schema")=="v206_one_eyes_of_eagle_nonchmv_native_rating_scope_v1"
         and p.get("status")=="PASS_EAGLE_7967_ONE_WINDOWS_PROFILE_STATIC_E_ZERO"
         and p.get("binary_sha256")==
             "0ad16368cd1effb19c793dbce63518ccb72fec89c72f6ef75d9afca239a039e8"
         and p.get("source_revision")=="710c2408bf"
         and p.get("source_profile_sha256")==
             "284f22abd98c900d6474d6e9eb2f483d2262be39c78e4ac4af9bf56791a315bb"
         and p.get("native_before_json2_sha256")==NATIVE_SHA[0]
         and p.get("native_after_json2_sha256")==NATIVE_SHA[1]
         and p.get("native_new_calls")==2
         and p.get("static_CHMV_E")==E_ZERO
         and p.get("not_general_26_specs_proof") is True
         and p.get("not_mechanics_or_DPS_proof") is True,
         "EAGLE_WINDOWS_NATIVE_E_ZERO_PROOF_MISSING_OR_DRIFT")
    return p

def source(catalog_path=None):
    raw,rows,_=catalog.read(catalog_path or catalog.DEFAULT)
    selected=[r for r in rows if r["enchant_id"]==7967]
    need(len(selected)==1 and
         selected[0]["token"]=="enchant_ring__eyes_of_the_eagle"
         and selected[0]["source_slots"]==["finger1/finger2"]
         and selected[0]["highest_source_quality_rank"]==2
         and selected[0]["ui_selectable"] is False
         and families.RING_EFFECTS["eyes_of_the_eagle"][0]=="crit_effectiveness"
         and raw["simc_commit"].startswith("710c2408bf"),
         "EAGLE_SOURCE_FAMILY_OR_ID_NOT_VERIFIED")
    return selected[0]

def check_choice(choice,catalog_path=None):
    need(type(choice) is dict and choice==CHOICE,
         "ONLY_VERIFIED_EAGLE_FINGER1_NONCHMV_SELECTION")
    source(catalog_path);evidence()
    return {"schema":SCHEMA,"choice":dict(CHOICE),
            "effect_family":"crit_effectiveness",
            "static_CHMV_E":dict(E_ZERO),
            "budget_policy":"NON_CHMV_NO_CHANGE_TO_REFERENCE_B_OR_FINAL_T",
            "native_static_scope":"ONE_WINDOWS_PALADIN334_STATIC_E_ZERO_NOT_ALL_DPS",
            "mechanics_owner":"SimC"}

def apply(rows,choice,user,*,current_season_product,need_user,
          catalog_path=None):
    result=check_choice(choice,catalog_path)
    need_user(current_season_product is True,
              "V206_ENCHANT_ONLY_CURRENT_SEASON_USER_ROUTE")
    need_user(not any(r.get("slot")=="finger1" for group in
                  ("special_items","embellishments") for r in user.get(group,[])),
              "V206_ENCHANT_OVERLAPS_SELECTED_SPECIAL_OR_CRAFTED")
    ring=rows.get("finger1")
    need_user(type(ring) is dict and type(ring.get("item_id")) is int
              and type(ring.get("ilevel")) is int
              and type(ring.get("options")) is dict,
              "V206_REPRESENTATIVE_FINGER1_RING_MISSING")
    need_user("enchant" not in ring["options"]
              and "enchant_id" not in ring["options"],
              "V206_PREEXISTING_RING_ENCHANT_NOT_OVERWRITTEN")
    ring["options"]["enchant_id"]="7967"
    return result

def admit(choice,profile,normalized,catalog_path=None):
    result=check_choice(choice,catalog_path)
    need(type(profile) is str and type(normalized) is dict,
         "EAGLE_MANIFEST_SOURCE_REQUIRED")
    ring=[line.split("=",1)[1] for line in profile.splitlines()
          if line.startswith("finger1=")]
    need(len(ring)==1,"EAGLE_ONE_FINGER1_REQUIRED")
    parts=ring[0].split(",")
    need(parts.count("enchant_id=7967")==1 and
         not any(x.startswith("enchant=") for x in parts),
         "EAGLE_SIMC_ID_NOT_EXACTLY_ONCE")
    scenario=normalized["scenario"]
    equip=scenario.get("equipment")
    need(type(equip) is dict and
         all(type(equip.get(group)) is list for group in ("special","crafted"))
         and not any(r.get("slot")=="finger1" for group in ("special","crafted")
                     for r in equip[group]),
         "EAGLE_MANIFEST_SELECTED_SPECIAL_OVERLAP")
    ch=scenario["character"]
    target=scenario["target"]
    need((ch["class"],ch["spec"]) in {
         ("paladin","retribution"),("mage","frost")} or
         type(ch["class"]) is str and type(ch["spec"]) is str,
         "EAGLE_CHARACTER_INVALID")
    need(type(target["ilevel"]) is int and
         266<=target["ilevel"]<=344,
         "EAGLE_ILVL_OUTSIDE_CURRENT_SEASON")
    return result
