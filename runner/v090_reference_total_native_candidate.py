#!/usr/bin/env python3
"""v090 opt-in reference-T static-c Native candidate path without ordinary G.

Uses existing v089->v061 input, v062 exact special L and slot assembly,
v063 static gear override, v064 exact item/profile verification+Native result,
and v065 floor/target bounds. No synthetic Native ordinary stat values; no
new effects/proc/APL calculations, no replacement for exact-G mode.
"""
from __future__ import annotations
import copy,hashlib,json,math,pathlib
import v046_static_item_cache as items
import v061_scenario_contract as scenario
import v062_static_budget_bridge as statics
import v063_numeric_injection as numeric
import v064_adaptive_evaluator_port as port
import v065_v015_scheduler_adapter as search
import v089_ilvl_chmv_budget_selector as selected

SCHEMA="v090_reference_total_native_candidate_v1"
PROVENANCE="v090_reference_budget_provenance_v1"
class ReferenceNativeBlocked(ValueError):pass
def need(ok,why):
    if not ok:raise ReferenceNativeBlocked(why)

def _exact_rows(normalized,fillers):
    cfg=normalized["scenario"]
    fixed=sum((cfg["equipment"][group] for group in
               ("tier","special","crafted","trinkets")),[])
    ordinary=statics.check_filler(fillers,fixed)
    all_rows=fixed+ordinary
    out={}
    for row in all_rows:
        slot=row["slot"]
        need(slot not in out,"DUPLICATE_EXACT_ITEM_SLOT")
        out[slot]={"item_id":row["item_id"],"ilevel":row["ilevel"],
                   "options":dict(row["options"])}
    need(len(out) in (15,16) and {"main_hand","trinket1","trinket2"}<=set(out),
         "EXACT_PROFILE_SLOT_STRUCTURE")
    return out

def prepare(selection, fillers, native_cache, reference):
    """Reuse v062 on a v089 opt-in selection. Never invent missing gear G."""
    need(type(selection) is dict and selection.get("schema")==selected.SCHEMA
         and selection.get("native_G_required_for_T") is False,
         "REFERENCE_SELECTION_REQUIRED")
    is_reference=(selection.get("source_mode")==selected.REFERENCE_MODE
                  and selection.get("status")=="READY_OPT_IN_REFERENCE_TOTAL_NOT_FULL_P3")
    is_manual=(selection.get("source_mode")=="user_manual_total"
               and selection.get("status")=="READY_USER_MANUAL_TOTAL")
    need(is_reference or is_manual,"REFERENCE_SELECTION_REQUIRED")
    if is_reference:
        reference_level=selection["scenario"]["target"]["ilevel"]
        track=selection["selected_track"]
        reg,live_sha=selected.load_registry()
        need(266<=reference_level<=344
             and selection["reference_sha256"]==live_sha
             and type(selection.get("reference_row")) is dict
             and selection["reference_row"]==reg["values"][reference_level-266]
             and selection["resolved_T"]==selection["reference_row"][track],
             "REFERENCE_PROVENANCE_TAMPERED")
    else:
        live_sha=None
        track=None
        need(selection.get("reference_sha256") is None
             and selection.get("reference_row") is None
             and selection.get("selected_track") is None
             and selection["scenario"]["target"]["mode"]=="manual_total"
             and selection["scenario"]["target"]["manual_total"]==selection["resolved_T"],
             "MANUAL_BASE_B_SELECTION_DRIFT")
    normalized=scenario.normalize(selection["scenario"])
    need(normalized["scenario_digest"]==
         selection["scenario_plan"]["scenario_digest"],
         "EFFECTIVE_SCENARIO_IDENTITY_CHANGED")
    need(normalized["budget"]["T"]==selection["resolved_T"]
         and normalized["scenario"]["target"]["mode"]=="manual_total",
         "REFERENCE_TYPED_TOTAL_DRIFT")
    if is_reference:
        need(normalized["budget"]["J"]==reg["J"]
             and normalized["budget"]["F"]==reg["F"],
             "REFERENCE_CONSUMABLE_CONTRACT_DRIFT")
    if normalized["scenario"]["source"]["kind"]=="user_supplied":
        require_hash=normalized["scenario"]["source"]["profile_sha256"]
        need(hashlib.sha256(reference.encode("utf8")).hexdigest()==require_hash,
             "USER_SOURCE_PROFILE_SHA_DRIFT")
    exact=_exact_rows(normalized,fillers)
    native_budget=statics.compile_static_budget(normalized,fillers,native_cache)
    need(native_budget["budget"]["T_official"]==selection["resolved_T"],
         "COMPILED_T_NOT_REFERENCE_T")
    need(not native_budget["missing_special_fixed_static"]
         and native_budget["locked_L_when_all_specials_observed"] is not None,
         "SPECIAL_L_REQUIRES_EXACT_NATIVE_STATIC_VARIANT")
    need(native_budget["effective_floor_if_possible"] is not None,
         "REFERENCE_FIXED_L_CONSTRAINT_UNRESOLVED")
    # Distinguish unmeasured ordinary gear G from a real observed 0 rating.
    # Missing trinket gear stats stay allowed and unknown, never assumed zero.
    native_budget=copy.deepcopy(native_budget)
    native_budget["reference_exact_slot_identity"]=exact
    native_budget["reference_budget_provenance"]={
        "schema":PROVENANCE,"source":selection["source_mode"],
        "reference_sha256":live_sha,"reference_row":selection["reference_row"],
        "reference_track":track,"total_T":selection["resolved_T"],
        "budget_entry_mode":"OPT_IN_REFERENCE_B" if is_reference else "USER_MANUAL_FINAL_T_CONVERTED_TO_B",
        "G_is_not_required_for_reference_T":True,
        "ordinary_missing_G_records_not_fabricated":True}
    inventory=port.verify_profile_binding(normalized,native_budget,reference)
    total,low,high=search.bounds(normalized,native_budget)
    need(total==selection["resolved_T"],"SCHEDULER_REFERENCE_TOTAL_DRIFT")
    return {"schema":SCHEMA,
        "status":"READY_TO_PROPOSE_REFERENCE_STATIC_NATIVE_CANDIDATE",
        "scenario":normalized,"static_budget":native_budget,
        "reference_source":selection["source_mode"],
        "reference_sha256":live_sha,"reference_track":track,
        "prepared_profile_sha256":hashlib.sha256(reference.encode("utf8")).hexdigest(),
        "T":total,"floor_L":native_budget["locked_L_when_all_specials_observed"],
        "minimum":low,"maximum":high,
        "items_bound":inventory["slots_bound"],
        "missing_ordinary_G_observed_not_zero":
          len(native_budget["missing_nontrinket_static"]),
        "native_calls":0,"original_product_integrated":False}

def propose(prepared,reference,target,declared_F_vector,binary_sha,revision,
            iterations,output_json2_path,*,oil_precredit=None):
    """One offline candidate proposal; existing v064 JSON2 ingest owns DPS/SEM.

    Only the oil-inclusive adapter may opt in to a precredited intermediate
    request when B < F on a stat but B + fixed O >= F. This prevents creating
    an impossible negative temporary gear override; actual final input is
    still validated by the same strict v063 renderer and v092 bridge.
    """
    need(prepared.get("schema")==SCHEMA and
         prepared.get("status")=="READY_TO_PROPOSE_REFERENCE_STATIC_NATIVE_CANDIDATE",
         "REFERENCE_BUDGET_NOT_PREPARED")
    scenario.vector(target,"REFERENCE_STATIC_C")
    scenario.vector(declared_F_vector,"DECLARED_STATIC_F")
    normalized=prepared["scenario"]
    budget=prepared["static_budget"]
    need(hashlib.sha256(reference.encode("utf8")).hexdigest()==
         prepared["prepared_profile_sha256"],
         "SOURCE_PROFILE_CHANGED_AFTER_REFERENCE_PREPARATION")
    need(sum(declared_F_vector.values())==normalized["budget"]["F"],
         "FLASK_F_VECTOR_SUM_MISMATCH")
    total,lower,upper=search.bounds(normalized,budget)
    need(search.eligible(tuple(target[k] for k in scenario.STATS),
                         total,lower,upper),
         "REFERENCE_CANDIDATE_T_OR_LOCKED_L_CONSTRAINT")
    need(type(binary_sha) is str and
         scenario.HASH_RE.fullmatch(binary_sha) is not None,
         "SIMC_BINARY_SHA_REQUIRED")
    need(type(revision) is str and len(revision)>=7,
         "SIMC_REVISION_REQUIRED")
    need(type(iterations) is int and
         normalized["scenario"]["runtime"]["scout_iterations"]<=iterations<=
         normalized["scenario"]["runtime"]["confirm_iterations"],
         "ITERATIONS_OUTSIDE_SCENARIO_BOUNDS")
    binding=port.verify_profile_binding(normalized,budget,reference)
    precredit=None
    render_target=target
    if oil_precredit is not None:
        precredit=scenario.vector(oil_precredit,"EXACT_FIXED_O_PRE_CREDIT")
        need(precredit==normalized["budget"]["external_temporary_rating"]
             and any(target[k]<declared_F_vector[k] for k in scenario.STATS),
             "OIL_PRECREDIT_ONLY_WHEN_BASE_TARGET_BELOW_F")
        render_target={k:target[k]+precredit[k] for k in scenario.STATS}
        need(all(render_target[k]>=declared_F_vector[k]
                 for k in scenario.STATS),
             "OIL_PRECREDIT_FINAL_TARGET_BELOW_F")
    generated=numeric.render_static_chmv_candidate(
        reference,render_target,declared_F_vector,output_json2_path,iterations)
    key=items.digest({"schema":SCHEMA,
        "rating_semantics":"STATIC_CHMV_C_V1",
        "scenario":normalized["scenario_digest"],
        "source_reference_sha256":prepared["reference_sha256"],
        "reference_track":prepared["reference_track"],
        "exact_slot_identity":budget["reference_exact_slot_identity"],
        "target_static_c":target,
        "declared_F_vector":declared_F_vector,
        "raw_gear_override":generated["raw_gear_override"],
        "stable_profile_sha256":generated["stable_profile_sha256"],
        "binary_sha256":binary_sha,"revision":revision,
        "iterations":iterations,
        "threads":normalized["scenario"]["runtime"]["threads"]})
    result={"schema":port.SCHEMA,"status":"PROPOSED_STATIC_C_NO_NATIVE",
        "v090_reference_budget":prepared["reference_source"]==selected.REFERENCE_MODE,
        "v090_schema":SCHEMA,
        "rating_semantics":"STATIC_CHMV_C_V1",
        "case_key":key,"target":dict(target),"iterations":iterations,
        "input":generated["input"],
        "input_sha256":generated["input_sha256"],
        "raw_gear_override":generated["raw_gear_override"],
        "static_flask_F_vector":dict(declared_F_vector),
        "simc_binary_sha256":binary_sha,"native_revision":revision,
        "scenario_digest":normalized["scenario_digest"],
        "profile_stable_sha256":generated["stable_profile_sha256"],
        "json2_location":str(pathlib.Path(output_json2_path).resolve()),
        "official_total":total,
        "profile_binding":binding,
        "reference_source_sha256":prepared["reference_sha256"],
        "G_was_required_for_candidate":False,
        "locked_L_not_double_added":True,
        "external_oil_only":normalized["budget"]["external_temporary_rating"],
        "buffed_rating_exact_target_required":False,
        "global_optimum_proven":False}
    if precredit is not None:
        result["v090_oil_precredit"]=dict(precredit)
    return result
