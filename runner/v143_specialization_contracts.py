#!/usr/bin/env python3
"""Season-independent SimC profile contracts for source-free DPS migration.

This contains stable class/spec syntax, armor and weapon semantics, primary
stat, and tier slot rules. NO season item IDs, talents, APL, SimC executable,
official full-profile fixtures, DPS weights or Native calls.

The 24 source-backed DPS profiles remain on their existing execution path.
Add their contracts only as the common catalog route becomes ready; presence
here is not itself evidence of SimC Native acceptance for a new season.
"""
from __future__ import annotations

TIER_SLOTS=("head","shoulders","chest","hands","legs")
SLOT_ORDER=("head","neck","shoulders","back","chest","wrists",
            "hands","waist","legs","feet","finger1","finger2",
            "trinket1","trinket2","main_hand","off_hand")
RATING_STATS=("crit_rating","haste_rating","mastery_rating",
              "versatility_rating")
NON_TIER_ORDINARY=frozenset(("wrists","waist","feet"))
WEAPON_SLOTS=frozenset(("main_hand","off_hand"))
WEAPON_FORMS={
    "one_hand_frill":("main_hand","off_hand"),
    "one_hand_shield":("main_hand","off_hand"),
    "dual_one_hand":("main_hand","off_hand"),
    "dual_two_hand":("main_hand","off_hand"),
    "single_one_hand":("main_hand",),
    "single_two_hand":("main_hand",),
    "ranged":("main_hand",),
}

# Explicitly product-proven source-independent P1 cases; not yet 26 native-
# verified profile compiler contracts. Season IDs must not appear here.
CONTRACTS={
    "druid/balance":{
        "simc_class":"druid","simc_spec":"balance","family":"leather",
        "primary":"intellect","role":"spell","position":"back",
        "weapon_form":"one_hand_frill","allowed_races":None,
    },
    "evoker/devastation":{
        "simc_class":"evoker","simc_spec":"devastation","family":"mail",
        "primary":"intellect","role":"spell","position":"back",
        "weapon_form":"one_hand_frill",
        "allowed_races":("dracthyr","dracthyr_visage"),
    },
    # Migrating first legacy source-backed case. The default v098/v106
    # execution and existing 24-spec Native caches are NOT promoted/changed.
    "mage/frost":{
        "simc_class":"mage","simc_spec":"frost","family":"cloth",
        "primary":"intellect","role":"spell","position":"back",
        "weapon_form":"one_hand_frill","allowed_races":None,
    },
    "paladin/retribution":{
        "simc_class":"paladin","simc_spec":"retribution","family":"plate",
        "primary":"strength","role":"attack","position":"back",
        "weapon_form":"single_two_hand","allowed_races":None,
    },
    # Catalog-only migration previews; NOT source-free Native-approved.
    "warrior/fury":{
        "simc_class":"warrior","simc_spec":"fury","family":"plate",
        "primary":"strength","role":"attack","position":"back",
        "weapon_form":"dual_two_hand","allowed_races":None,
    },
    "hunter/beast_mastery":{
        "simc_class":"hunter","simc_spec":"beast_mastery","family":"mail",
        "primary":"agility","role":"attack","position":"ranged_back",
        "weapon_form":"ranged","allowed_races":None,
    },
    "rogue/outlaw":{
        "simc_class":"rogue","simc_spec":"outlaw","family":"leather",
        "primary":"agility","role":"attack","position":"back",
        "weapon_form":"dual_one_hand","allowed_races":None,
    },
    "rogue/subtlety":{
        "simc_class":"rogue","simc_spec":"subtlety","family":"leather",
        "primary":"agility","role":"attack","position":"back",
        "weapon_form":"dual_one_hand","allowed_races":None,
    },
    "shaman/elemental":{
        "simc_class":"shaman","simc_spec":"elemental","family":"mail",
        "primary":"intellect","role":"spell","position":"back",
        "weapon_form":"one_hand_shield","allowed_races":None,
    },
    "mage/arcane":{
        "simc_class":"mage","simc_spec":"arcane","family":"cloth",
        "primary":"intellect","role":"spell","position":"back",
        "weapon_form":"one_hand_frill","allowed_races":None,
    },
    "mage/fire":{
        "simc_class":"mage","simc_spec":"fire","family":"cloth",
        "primary":"intellect","role":"spell","position":"ranged_back",
        "weapon_form":"one_hand_frill","allowed_races":None,
    },
    "priest/shadow":{
        "simc_class":"priest","simc_spec":"shadow","family":"cloth",
        "primary":"intellect","role":"spell","position":"ranged_back",
        "weapon_form":"one_hand_frill","allowed_races":None,
    },
    "warlock/affliction":{
        "simc_class":"warlock","simc_spec":"affliction","family":"cloth",
        "primary":"intellect","role":"spell","position":"ranged_back",
        "weapon_form":"one_hand_frill","allowed_races":None,
    },
    "warlock/demonology":{
        "simc_class":"warlock","simc_spec":"demonology","family":"cloth",
        "primary":"intellect","role":"spell","position":"ranged_back",
        "weapon_form":"one_hand_frill","allowed_races":None,
    },
    "warlock/destruction":{
        "simc_class":"warlock","simc_spec":"destruction","family":"cloth",
        "primary":"intellect","role":"spell","position":"back",
        "weapon_form":"one_hand_frill","allowed_races":None,
    },
}

def lookup(class_name,specialization):
    """Return a stable contract, or None for a not-yet-migrated spec."""
    return CONTRACTS.get(class_name+"/"+specialization)

def validate_contracts():
    """Cheap offline invariant, without season records or external sources."""
    expected={"simc_class","simc_spec","family","primary","role",
              "position","weapon_form","allowed_races"}
    for key,info in CONTRACTS.items():
        assert set(info)==expected and key==(
            info["simc_class"]+"/"+info["simc_spec"])
        assert info["family"] in ("leather","mail","plate","cloth")
        assert info["primary"] in ("intellect","strength","agility")
        assert info["role"] in ("spell","attack","tank","heal")
        assert info["weapon_form"] in WEAPON_FORMS
    return True
