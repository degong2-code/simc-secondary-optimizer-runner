#!/usr/bin/env python3
"""v204: selected, Native-proven permanent-enchant rating on an ilvl reference.

No modification to the 79x2 source reference, v061 schema, search algorithm or
manual final T. An E addition is permitted only for the existing exact v202
developer pilot, whose v203 source/profile/binary SHA gates remain mandatory.
"""
from __future__ import annotations
import copy
import v061_scenario_contract as scenario
import v089_ilvl_chmv_budget_selector as reference
import v197_verified_effect_budget as rating
import v202_one_enchant_admission as evidence

KEY="v204_selected_verified_enchant_reference_addition_v1"

class EnchantReferenceBlocked(ValueError):
    pass

def need(condition, reason):
    if not condition:
        raise EnchantReferenceBlocked(reason)

def verified_vector(selected_E):
    record, digest=evidence.read()
    E=rating.vector(selected_E,"SELECTED_VERIFIED_ENCHANT_E")
    need(E==record["static_enchant_E"] and sum(E.values())>0,
         "SELECTED_ENCHANT_E_NOT_EXACT_NATIVE_EVIDENCE")
    return E,digest

def selected_reference(selection, selected_E=None, *, manual_final_T=None):
    """Adjust only a derived-ilvl B. Manual final T already includes E.

    The new target is B0+E; E stays non-fungible in the existing v065 floor.
    Existing absent-choice path returns the ORIGINAL selection object unchanged.
    """
    if selected_E is None:
        return selection
    E,digest=verified_vector(selected_E)
    need(type(selection) is dict and selection.get("schema")==reference.SCHEMA,
         "ENCHANT_REQUIRES_TYPED_REFERENCE_SELECTION")
    if manual_final_T is not None:
        need(selection.get("source_mode")=="user_manual_total" and
             selection.get("resolved_T")==manual_final_T-
                    sum(selection["external_O"].values()),
             "MANUAL_FINAL_T_MUST_REMAIN_FIXED")
        return selection
    need(selection.get("source_mode")==reference.REFERENCE_MODE and
         selection.get("status")=="READY_OPT_IN_REFERENCE_TOTAL_NOT_FULL_P3" and
         selection.get("selected_track")==reference.TRACK_COMMON and
         selection["scenario"]["target"]["ilevel"]==334 and
         (selection["scenario"]["character"]["class"],
          selection["scenario"]["character"]["spec"])==("mage","frost"),
         "ENCHANT_ADDITIVE_REFERENCE_ONLY_NATIVE_PINNED_FROST_334")
    original=selection["reference_row"][selection["selected_track"]]
    need(type(original) is int and selection["resolved_T"]==original,
         "ENCHANT_ORIGINAL_REFERENCE_B_CHANGED")
    added=sum(E.values())
    shifted=copy.deepcopy(selection)
    shifted["scenario"]["target"]["manual_total"]=original+added
    shifted["scenario_plan"]=scenario.normalize(shifted["scenario"])
    need(shifted["scenario_plan"]["budget"]["T"]==original+added,
         "ENCHANT_REFERENCE_RECALCULATION_FAILED")
    shifted["resolved_T"]=original+added
    shifted[KEY]={"base_reference_B":original,"additive_E":E,
                  "additional_B":added,"evidence_sha256":digest}
    return shifted

def expected_reference_B(selection, reference_B):
    """Validate explicit additive provenance at the v090 compilation boundary."""
    proof=selection.get(KEY)
    if proof is None:
        return reference_B
    need(type(proof) is dict,
         "ENCHANT_REFERENCE_PROVENANCE_DRIFT")
    need(selection.get("source_mode")==reference.REFERENCE_MODE and
         selection.get("selected_track")==reference.TRACK_COMMON and
         selection["scenario"]["target"]["ilevel"]==334 and
         (selection["scenario"]["character"]["class"],
          selection["scenario"]["character"]["spec"])==("mage","frost"),
         "ENCHANT_ADDITIVE_REFERENCE_SCOPE_DRIFT")
    E,digest=verified_vector(proof.get("additive_E"))
    need(type(proof) is dict and
         set(proof)=={"base_reference_B","additive_E",
                      "additional_B","evidence_sha256"} and
         proof["base_reference_B"]==reference_B and
         type(proof["additional_B"]) is int and
         proof["additional_B"]==sum(E.values()) and
         proof["evidence_sha256"]==digest,
         "ENCHANT_REFERENCE_PROVENANCE_DRIFT")
    return reference_B+proof["additional_B"]
