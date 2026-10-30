#!/usr/bin/env python3
"""v091: explicit per-weapon Thalassian Phoenix Oil input identity.

Small adapter around v089/v090/v064 and approved v092 inclusive-T policy.
SimC handles oil mechanics. Fixed O adds once to gear_* override because that
numeric override replaces the oil's natural secondary rating; O is not a
freely distributable stat budget, and is not separately added to JSON2 again.
"""
from __future__ import annotations
import copy,hashlib,pathlib
import v061_scenario_contract as scenario
import v064_adaptive_evaluator_port as port
import v089_ilvl_chmv_budget_selector as chooser
import v090_reference_total_native_candidate as reference_path
import v092_approved_inclusive_CHMV_policy as total_policy
import v204_selected_enchant_reference_budget as selected_enchant

SCHEMA="v091_oil_per_actual_weapon_external_v1"
OIL="thalassian_phoenix_oil_2"
HANDS=frozenset(("main_hand","off_hand"))
SINGLE_LAYOUTS=frozenset(("single_one_hand","single_two_hand",
                          "one_hand_shield","one_hand_frill","ranged","other"))
DUAL_LAYOUTS=frozenset(("dual_one_hand","dual_two_hand"))
PER_WEAPON={"crit_rating":16,"haste_rating":16,
            "mastery_rating":0,"versatility_rating":0}

class OilInputBlocked(ValueError):pass
def need(ok,reason):
    if not ok:raise OilInputBlocked(reason)

def _profile_slots(profile):
    result={}
    for line in profile.splitlines():
        name,sep,val=line.partition("=")
        if sep and name in ("main_hand","off_hand"):
            need(name not in result,"DUPLICATE_WEAPON_SLOT:"+name)
            result[name]=val
    need("main_hand" in result,"MAIN_HAND_ITEM_REQUIRED")
    return result

def configure(profile,doc,weapon_layout,applied_hands):
    """Return exact selected oil input + updated user-supplied SHA v061 doc.

    Crucial: never rely on the absence of temporary_enchant. SimC supplies
    a class-specific default oil if it is omitted, even when requested O=0.
    Use explicit 'disabled' for no oil.
    """
    need(type(profile) is str and type(doc) is dict,"PROFILE_AND_SCENARIO")
    normalized=scenario.normalize(doc)
    need(weapon_layout in SINGLE_LAYOUTS|DUAL_LAYOUTS,"WEAPON_LAYOUT_UNKNOWN")
    need(type(applied_hands) in (tuple,list)
         and len(applied_hands)<=2
         and all(type(x) is str and x in HANDS for x in applied_hands)
         and len(set(applied_hands))==len(applied_hands),
         "OIL_HAND_SET_INVALID")
    applied=frozenset(applied_hands)
    original_slots=_profile_slots(profile)
    need("main_hand" in original_slots,"MAIN_WEAPON_REQUIRED")
    if weapon_layout in SINGLE_LAYOUTS:
        need("off_hand" not in applied,"NONWEAPON_OFFHAND_CANNOT_RECEIVE_OIL")
    if weapon_layout in DUAL_LAYOUTS:
        need("off_hand" in original_slots,
             "DUAL_WIELD_OFFHAND_ITEM_ABSENT")
    # Strong user-provided source provenance; profile can only change
    # temporary_enchant once, not arbitrary equipment/APL/consumables.
    source=normalized["scenario"]["source"]
    if source["kind"]=="user_supplied":
        need(hashlib.sha256(profile.encode("utf8")).hexdigest()==
             source["profile_sha256"],
             "USER_SOURCE_PROFILE_SHA_MISMATCH")
    need(len([l for l in profile.splitlines()
              if l.startswith("temporary_enchant=")])<=1,
         "MULTIPLE_TEMPORARY_ENCHANT_ASSIGNMENTS")
    ordered=[s for s in ("main_hand","off_hand") if s in applied]
    declared_O={k:PER_WEAPON[k]*len(ordered) for k in scenario.STATS}
    literal=("/".join(s+":"+OIL for s in ordered) if ordered else "disabled")
    token="temporary_enchant="+literal
    out=[]
    replaced=False
    for line in profile.splitlines():
        if line.startswith("temporary_enchant="):
            need(not replaced,"MULTIPLE_TEMPORARY_ENCHANT_ASSIGNMENTS")
            out.append(token)
            replaced=True
        else:
            out.append(line)
    if not replaced:out.append(token)
    new_profile="\n".join(out).rstrip()+"\n"
    need(sum(x.startswith("temporary_enchant=")
             for x in new_profile.splitlines())==1,
         "OIL_MUST_BE_EXPLICIT_ONCE")
    cfg=copy.deepcopy(doc)
    cfg["consumables"]["weapon_temporary"]=OIL if ordered else None
    cfg["consumables"]["weapon_temporary_fixed_rating"]=declared_O
    if cfg["source"]["kind"]=="user_supplied":
        cfg["source"]["profile_sha256"]=hashlib.sha256(
            new_profile.encode("utf8")).hexdigest()
    effective=scenario.normalize(cfg)
    need(effective["budget"]["T"]==normalized["budget"]["T"],
         "OIL_ALTERED_OFFICIAL_T")
    need(effective["budget"]["external_temporary_rating"]==declared_O,
         "OIL_EXTERNAL_VECTOR_DRIFT")
    return {"schema":SCHEMA,"status":"EXPLICIT_OIL_INPUT_CONFIGURED",
        "profile":new_profile,"scenario":cfg,
        "original_sha256":hashlib.sha256(profile.encode("utf8")).hexdigest(),
        "profile_sha256":hashlib.sha256(new_profile.encode("utf8")).hexdigest(),
        "weapon_layout":weapon_layout,"applied_hands":ordered,
        "oil_token":OIL if ordered else None,
        "expected_simc_temporary_enchant":literal,
        "declared_O":declared_O,"oil_outside_legacy_B":True,
        "oil_in_approved_final_T":True,
        "legacy_B_unchanged":True,"native_calls":0,
        "mechanics_owner":"SimC",
        "buffed_O_addition_independently_proven":False}

def prepare(profile,doc,fillers,static_cache,weapon_layout,applied_hands,
            *,manual_final_T=None,verified_enchant_E=None):
    # Source-locked oil is configured ONCE. A final-inclusive user T is
    # converted explicitly to legacy free B by the approved v092 policy.
    if manual_final_T is not None:
        need(type(manual_final_T) is int and 1<=manual_final_T<=100000,
             "MANUAL_FINAL_T_REQUIRED")
        need(doc["target"]["mode"]=="derived_ilevel",
             "MANUAL_FINAL_T_REQUIRES_UNSET_LEGACY_TARGET")
    oil=configure(profile,doc,weapon_layout,applied_hands)
    if manual_final_T is not None:
        converted=total_policy.approved_manual_total_to_legacy_B(
            oil["scenario"],manual_final_T,oil["declared_O"])
        oil["scenario"]=converted["scenario"]
    if verified_enchant_E is not None:
        # Even the lower-level budget helper must not admit an E for an
        # arbitrary profile. v096 additionally checks the exact binary/revision.
        need(oil["profile_sha256"]==
             selected_enchant.evidence.EXACT_SOURCE_PROFILE_SHA256,
             "SELECTED_ENCHANT_FULL_PROFILE_SHA_NOT_VERIFIED")
    selection=chooser.resolve(oil["scenario"],mode=chooser.REFERENCE_MODE,
                              weapon_layout=weapon_layout)
    # Only an explicitly selected, exact Native-proven E can extend the
    # unenchanted ilvl reference. Manual final T is authoritative and fixed.
    selection=selected_enchant.selected_reference(
        selection,verified_enchant_E,manual_final_T=manual_final_T)
    prepared=reference_path.prepare(selection,fillers,static_cache,oil["profile"])
    need(prepared["T"]==selection["resolved_T"] and
         prepared["scenario"]["budget"]["external_temporary_rating"]==
         oil["declared_O"],
         "OIL_TOTAL_OR_EXTERNAL_VECTOR_MISMATCH")
    accounting=total_policy.calculate(prepared["T"],oil["declared_O"])
    if manual_final_T is not None:
        need(accounting["final_T"]==manual_final_T,
             "MANUAL_FINAL_T_B_O_MISMATCH")
    # A source-locked full exact ID/ilevel/option profile with all selected
    # fixed L and no ordinary G cache is required via existing v090.
    return {"schema":SCHEMA,"status":"READY_V091_STATIC_C_CANDIDATE",
        "oil":oil,"prepared":prepared,"approved_total":accounting,
        "native_calls":0,"original_v015_v016_integrated":False}

def propose(bundle,target,flask_vector,binary_sha,revision,iterations,path):
    need(bundle.get("schema")==SCHEMA and
         bundle.get("status")=="READY_V091_STATIC_C_CANDIDATE",
         "V091_PREPARED_BUNDLE_REQUIRED")
    oil=bundle["oil"]
    # The B-only legacy intermediate requires B>=F before oil can be
    # credited. For valid boundary candidates F-O<=B<F, construct the
    # intermediate from final B+O in v090; v092 will not add oil a second
    # time. Typical historical candidates take the unchanged code path
    # and retain their exact Native input/cache case identities.
    boundary=any(target[s]<flask_vector[s] for s in scenario.STATS)
    precredit=oil["declared_O"] if boundary else None
    out=reference_path.propose(bundle["prepared"],oil["profile"],
            target,flask_vector,binary_sha,revision,iterations,path,
            oil_precredit=precredit)
    need(out["official_total"]==bundle["prepared"]["T"] and
         out["external_oil_only"]==oil["declared_O"] and
         all(out["raw_gear_override"][s]+flask_vector[s]==
             target[s]+(precredit[s] if precredit is not None else 0)
             for s in scenario.STATS),
         "LEGACY_BASE_STATIC_C_REFERENCE_DRIFT")
    # Authoritative user-approved final total. SimC gear_* overrides the
    # oil's rating contribution; add its fixed vector exactly once to that
    # override, not to the scheduler's freely distributed B.
    out=total_policy.adjust_native_request(
        out,bundle["approved_total"],target)
    need(out["official_total"]==bundle["approved_total"]["final_T"] and
         all(out["raw_gear_override"][s]+flask_vector[s]==
             out["target"][s] for s in scenario.STATS),
         "FINAL_OIL_INCLUSIVE_STATIC_C_DRIFT")
    out["v091_oil_hands"]=oil["applied_hands"]
    out["v091_expected_temporary_enchant"]=(oil["expected_simc_temporary_enchant"])
    out["v091_declaration_O"]=oil["declared_O"]
    out["v091_stat_effect_simc_owned"]=True
    return out

def ingest_native(request,native,raw_bytes=None):
    """Native acceptance: oil-inclusive static c, parsed oil selection, DPS.

    Does NOT claim that post-talent buffed_stats necessarily equals c+O.
    """
    need(type(request) is dict and
         "v091_expected_temporary_enchant" in request,
         "V091_REQUEST_REQUIRED")
    need(native.get("report_version")=="2.0.0",
         "V091_NATIVE_REPORT_REQUIRED")
    players=(native.get("sim") or {}).get("players") or []
    need(len(players)==1,"V091_SINGLE_NATIVE_PLAYER_REQUIRED")
    got=players[0].get("temporary_enchant")
    expected=request["v091_expected_temporary_enchant"]
    need(got==expected,"NATIVE_OIL_SETTING_DIFFERENT_FROM_USER_CHOICE")
    # v064 uses existing numeric.static-c and DPS/SEM acceptance.
    actual=port.ingest_native(request,native,
                            {"native_revision":request["native_revision"]},
                            raw_bytes)
    actual["oil_reported_by_native"]=got
    actual["oil_hands_declared"]=request["v091_oil_hands"]
    actual["O_external_declared_not_double_injected"]=request["v091_declaration_O"]
    # A single JSON2 buffed_stats snapshot cannot attribute oil's numeric
    # effect separately from gear_*, buffs, talents or other consumables.
    actual["native_oil_static_addition_observed_in_buffed_rating"]="FINAL_STATIC_C_INCLUDES_DECLARED_O;_BUFFED_STATS_REMAINS_SIMC_OBSERVED"
    actual["base_B"]=request["v092_base_B"]
    actual["total_T_including_O"]=request["v092_final_T"]
    actual["final_target_including_fixed_O"]=request["target"]
    actual["independent_proc_effect_certification"]=False
    return actual
