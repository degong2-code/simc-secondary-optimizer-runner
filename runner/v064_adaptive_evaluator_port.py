#!/usr/bin/env python3
"""v064: adaptive-scheduler-neutral candidate evaluation port.

A scheduler proposes (CHMV, iterations); this class only checks against the
v061/v062 official rating contract, feeds the v063 measured-input adapter,
accepts native JSON2 and returns DPS/SEM. No item/proc/APL internals, no new
search optimizer. The absent v015/v016 original source is NOT claimed merged.

Native result receipts are keyed by full profile/SimC binary/version/scenario/
candidate/iterations. Reusing a receipt requires actual native JSON2 bytes,
matching SHA256 and numerical rating validation; no guessed cache HIT.
"""
from __future__ import annotations
import hashlib,json,math,pathlib

import v046_static_item_cache as cache
import v061_scenario_contract as scenario
import v063_numeric_injection as numerical

SCHEMA="v064_external_adaptive_evaluator_port_v1"
STATS=scenario.STATS
BINARY_HASH_LEN=64
class PortBlocked(ValueError):pass

def need(ok,reason):
    if not ok: raise PortBlocked(reason)

def stable_case_key(normalized,budget,calibration,reference,binary_sha,target,iterations):
    need(type(binary_sha) is str and len(binary_sha)==BINARY_HASH_LEN
         and all(ch in "0123456789abcdef" for ch in binary_sha),
         "SIMC_BINARY_SHA_REQUIRED")
    # Exclude variable json2 file path, include relevant input and runtime values.
    part=numerical.input_parts(reference)
    obj={"contract_schema":SCHEMA,
         "scenario":normalized["scenario_digest"],
         "total_rating":budget["budget"]["T_official"],
         "calibrated_stable_profile":calibration["stable_profile_sha256"],
         "simc_binary_sha256":binary_sha,
         "simc_revision":calibration["native_revision"],
         "measured_net_offset":calibration["net_input_to_json2_rating_offset"],
         "profile_normalized_sha":part["stable_sha256"],
         "target_rating":target,
         "iterations":iterations,
         "threads":normalized["scenario"]["runtime"]["threads"]}
    if "empirical_affine_transfer" in calibration:
        obj["empirical_affine_transfer"]=calibration["empirical_affine_transfer"]
    return cache.digest(obj)

def verify_profile_binding(normalized,budget,reference):
    """Prevent a valid numeric calibration from being paired with other gear/settings.

    Verifies only our own scenario-to-SimC input identity, not the suitability
    or mechanics of any selected gear/trinket/embellishment effect.
    """
    need(type(reference) is str,"PROFILE_TEXT")
    cfg=normalized["scenario"]
    parsed={}
    slots=set()
    import v055_simc_item_selection as selected
    for line in reference.splitlines():
        key,sep,val=line.partition("=")
        if not sep or line.startswith("#"):continue
        # SimC APL contains intentionally repeated actions.list+= lines.
        # They are action append commands, not duplicate top-level settings.
        # Entire APL bytes are already protected by the profile stable hash.
        if key=="actions" or key.startswith("actions."):
            continue
        if key.endswith("+") and key.startswith("actions"):
            continue
        if key in parsed:need(False,"DUPLICATE_PROFILE_SETTING:"+key)
        parsed[key]=val
        if key in selected.SLOTS:slots.add(key)
    char=cfg["character"]
    for k,field in (("spec","spec"),("race","race"),("talents","talents"),
                    ("role","role")):
        need(parsed.get(k)==char[field],"PROFILE_CHARACTER_DRIFT:"+k)
    # A standard SimC source starts with a one-word class declaration.
    need(any(line.startswith(char["class"]+"=") for line in reference.splitlines()),
         "PROFILE_CLASS_DRIFT")
    combat=cfg["combat"]; consumables=cfg["consumables"]
    need(parsed.get("fight_style")==combat["fight_style"],
         "PROFILE_FIGHT_STYLE_DRIFT")
    need(parsed.get("desired_targets")==str(combat["targets"]),
         "PROFILE_TARGETS_DRIFT")
    need(parsed.get("max_time")==str(combat["duration_seconds"]),
         "PROFILE_DURATION_DRIFT")
    need(parsed.get("optimal_raid")==("1" if combat["raid_buffs"] else "0"),
         "PROFILE_RAID_BUFFS_DRIFT")
    for name in ("flask","food"):
        if consumables[name] is not None:
            need(parsed.get(name)==consumables[name],
                 "PROFILE_CONSUMABLE_DRIFT:"+name)
    temp=consumables["weapon_temporary"]
    if temp is not None:
        single="main_hand:"+temp
        dual=single+"/off_hand:"+temp
        off="off_hand:"+temp
        # v091 may deliberately apply oil only to the off-hand weapon.
        # Weapon eligibility itself is checked by the v091 exact layout
        # adapter, not by the mere presence of an off_hand slot.
        need(parsed.get("temporary_enchant") in ({single,off,dual} if
             "off_hand" in slots else {single}),
             "PROFILE_TEMPORARY_DRIFT")
    gear=cfg["equipment"]
    expected={}
    for kind in ("tier","special","crafted","trinkets"):
        for row in gear[kind]:
            expected[row["slot"]]={"item_id":row["item_id"],
                "ilevel":row["ilevel"],
                "options":row["options"]}
    for slot,row in budget["native_gear_stats"].items():
        ident=row["identity"]
        need(slot not in expected or expected[slot]=={
            "item_id":ident["item_id"],"ilevel":ident["ilevel"],
            "options":ident["options"]},"PROFILE_SELECTED_GEAR_CONFLICT:"+slot)
        expected[slot]={"item_id":ident["item_id"],
            "ilevel":ident["ilevel"],"options":ident["options"]}
    # v090 reference-T input path: ordinary gear's static CHMV may remain
    # UNOBSERVED, but its exact item/ilevel/option identity is NEVER optional.
    # Do not manufacture Native gear stat records to bypass this identity gate.
    optional=budget.get("reference_exact_slot_identity")
    if optional is not None:
        need(budget.get("reference_budget_provenance",{}).get("schema")==
             "v090_reference_budget_provenance_v1",
             "REFERENCE_SLOT_IDENTITIES_WITHOUT_PROVENANCE")
        need(type(optional) is dict and 13<=len(optional)<=16,
             "REFERENCE_EXACT_SLOT_IDENTITY_COUNT")
        for slot,identity in optional.items():
            need(type(identity) is dict and
                 set(identity)=={"item_id","ilevel","options"} and
                 type(identity["item_id"]) is int and
                 type(identity["ilevel"]) is int and
                 type(identity["options"]) is dict,
                 "REFERENCE_SLOT_IDENTITY_INVALID:"+str(slot))
            need(slot not in expected or expected[slot]==identity,
                 "REFERENCE_SELECTED_SLOT_IDENTITY_DRIFT:"+str(slot))
            expected[slot]=identity
    # The Native gear cache may lack a trinket record, but its exact ID must
    # still be present in the SimC input.
    need(slots==set(expected),"PROFILE_GEAR_SLOT_SET_DRIFT")
    for slot,row in expected.items():
        _,options=cache.parse_encoded(parsed[slot])
        actual={"item_id":int(options["id"]),"ilevel":int(options["ilevel"]),
                "options":{k:v for k,v in options.items()
                           if k not in ("id","ilevel","source")}}
        need(actual==row,"PROFILE_GEAR_ID_LEVEL_OPTIONS_DRIFT:"+slot)
    return {"slots_bound":len(expected),
            "two_trinkets_bound":all(k in expected for k in ("trinket1","trinket2")),
            "character_and_combat_bound":True,
            "no_effect_mechanics_interpreted":True}

def make_request(normalized,budget,calibration,reference,binary_sha,
                 target,iterations,output_json2_path):
    """Validate one externally proposed candidate; no SimC execution."""
    need(normalized.get("schema")==scenario.SCHEMA,"SCENARIO_SCHEMA")
    need(budget.get("schema")=="v062_representative_static_budget_v1",
         "BUDGET_SCHEMA")
    need(calibration.get("schema")==numerical.SCHEMA,"CALIBRATION_SCHEMA")
    need(type(iterations) is int and
         normalized["scenario"]["runtime"]["scout_iterations"]<=iterations<=
         normalized["scenario"]["runtime"]["confirm_iterations"],
         "ITERATION_OUTSIDE_SCENARIO_POLICY")
    need(budget["budget"]["official_formula"]=="T=G+J+F" and
         budget["budget"]["oil_stays_OUTSIDE_T"] is True,
         "OFFICIAL_GJF_POLICY_CHANGED")
    numerical.check_target(normalized,budget,target)
    binding=verify_profile_binding(normalized,budget,reference)
    generated=numerical.render_candidate(
        reference,calibration,target,pathlib.Path(output_json2_path),iterations)
    identity=stable_case_key(normalized,budget,calibration,reference,binary_sha,
                             target,iterations)
    return {"schema":SCHEMA,"status":"PROPOSED_VALID_NO_NATIVE_YET",
       "case_key":identity,"target":dict(target),"iterations":iterations,
       "simc_binary_sha256":binary_sha,
       "native_revision":calibration["native_revision"],
       "profile_stable_sha256":calibration["stable_profile_sha256"],
       "scenario_digest":normalized["scenario_digest"],
       "official_total":budget["budget"]["T_official"],
       "input":generated["input"],"input_sha256":generated["input_sha256"],
       "raw_gear_override":generated["raw_gear_override"],
       "json2_location":str(pathlib.Path(output_json2_path).resolve()),
       "profile_binding":binding,
       "global_optimum_proven":False,"item_effects_owned_by":"SimC"}

def make_static_chmv_request(normalized,budget,reference,binary_sha,
                             native_revision,target,flask_vector,
                             iterations,output_json2_path):
    """Distinct real-Native static c target, never conflated with buffed_stats."""
    numerical.check_target(normalized,budget,target)
    scenario.vector(flask_vector,"FLASK_F_STATIC_COMPONENT")
    need(sum(flask_vector.values())==normalized["budget"]["F"],
         "DECLARED_STATIC_FLASK_VECTOR_SUM_NOT_F")
    need(type(native_revision) is str and len(native_revision)>=7,
         "NATIVE_REVISION_MISSING")
    need(type(iterations) is int and
         normalized["scenario"]["runtime"]["scout_iterations"]<=iterations<=
         normalized["scenario"]["runtime"]["confirm_iterations"],
         "ITERATION_OUTSIDE_SCENARIO_POLICY")
    binding=verify_profile_binding(normalized,budget,reference)
    generated=numerical.render_static_chmv_candidate(
        reference,target,flask_vector,output_json2_path,iterations)
    identity=cache.digest({"schema":SCHEMA,"rating_semantics":"STATIC_CHMV_C_V1",
        "scenario":normalized["scenario_digest"],
        "target":target,"static_flask_F_vector":flask_vector,
        "static_gear_plus_gems_rating":generated["raw_gear_override"],
        "simc_binary_sha256":binary_sha,
        "native_revision":native_revision,
        "stable_profile_sha256":generated["stable_profile_sha256"],
        "iterations":iterations,
        "threads":normalized["scenario"]["runtime"]["threads"]})
    return {"schema":SCHEMA,"status":"PROPOSED_STATIC_C_NO_NATIVE",
        "rating_semantics":"STATIC_CHMV_C_V1",
        "case_key":identity,"target":dict(target),"iterations":iterations,
        "input":generated["input"],"input_sha256":generated["input_sha256"],
        "raw_gear_override":generated["raw_gear_override"],
        "static_flask_F_vector":dict(flask_vector),
        "simc_binary_sha256":binary_sha,
        "native_revision":native_revision,
        "scenario_digest":normalized["scenario_digest"],
        "profile_stable_sha256":generated["stable_profile_sha256"],
        "json2_location":str(pathlib.Path(output_json2_path).resolve()),
        "official_total":budget["budget"]["T_official"],
        "profile_binding":binding,
        "buffed_rating_exact_target_required":False,
        "global_optimum_proven":False}

def ingest_native(request,native_doc,calibration,raw_native_bytes=None):
    """Accept an actual JSON2 report; no separate proc-fidelity check."""
    need(request.get("schema")==SCHEMA,"PORT_REQUEST_SCHEMA")
    if raw_native_bytes is not None:
        need(type(raw_native_bytes) is bytes,"RAW_NATIVE_JSON_BYTES")
        need(json.loads(raw_native_bytes)==native_doc,
             "NATIVE_BYTES_AND_PARSED_JSON_DIFFER")
    if request.get("rating_semantics")=="STATIC_CHMV_C_V1":
        output=numerical.validate_static_native(native_doc,{
          "raw_gear_override":request["raw_gear_override"],
          "flask_component_in_T":request["static_flask_F_vector"],
          "expected_static_rating":request["target"]},
          request["native_revision"])
        return {"schema":SCHEMA,"status":"PASS_NATIVE_DPS_AND_STATIC_CHMV_INPUT",
          "rating_semantics":"STATIC_CHMV_C_V1",
          "case_key":request["case_key"],"target":request["target"],
          "iterations":request["iterations"],
          "input_sha256":request["input_sha256"],
          "simc_binary_sha256":request["simc_binary_sha256"],
          "scenario_digest":request["scenario_digest"],
          "native_json_sha256":hashlib.sha256(
              raw_native_bytes if raw_native_bytes is not None
              else cache.canonical(native_doc).encode("utf8")).hexdigest(),
          "native_revision":output["native_revision"],
          "static_rating_verified":output["verified_static_CHMV_c"],
          "rating_actual":output["actual_buffed_stats_rating"],
          "flask_F_component":output["flask_F_component"],
          "raw_gear_override":output["raw_gear_override"],
          "dps_mean":output["dps_mean"],"dps_sem":output["dps_sem"],
          "dps_samples":output["dps_samples"],
          "no_talent_adjustment_in_injected_static_CHMV":True,
          "item_effects_owned_by":"SimC"}
    rendered={"expected_json2_rating":request["target"],
              "raw_gear_override":request["raw_gear_override"]}
    result=numerical.validate_native(native_doc,rendered,calibration)
    return {"schema":SCHEMA,"status":"PASS_NATIVE_DPS_AND_RATING",
      "case_key":request["case_key"],
      "target":request["target"],
      "iterations":request["iterations"],
      "input_sha256":request["input_sha256"],
      "simc_binary_sha256":request["simc_binary_sha256"],
      "scenario_digest":request["scenario_digest"],
      "native_json_sha256":hashlib.sha256(
          raw_native_bytes if raw_native_bytes is not None
          else cache.canonical(native_doc).encode("utf8")).hexdigest(),
      "native_revision":result["native_revision"],
      "rating_actual":result["actual_buffed_stats_rating"],
      "dps_mean":result["dps_mean"],"dps_sem":result["dps_sem"],
      "dps_samples":result["dps_samples"],
      "no_simc_effect_independent_validation":True,
      "original_v015_v016_merged":False}

def verify_disk_cache(request,calibration,receipt,raw_native_bytes):
    need(type(receipt) is dict and
         receipt.get("status")==("PASS_NATIVE_DPS_AND_STATIC_CHMV_INPUT"
             if request.get("rating_semantics")=="STATIC_CHMV_C_V1"
             else "PASS_NATIVE_DPS_AND_RATING"),
         "CACHE_RECEIPT_NOT_SUCCESS")
    for key in ("case_key","target","iterations","input_sha256",
                "simc_binary_sha256","scenario_digest"):
        need(receipt.get(key)==request[key],"CACHE_IDENTITY_MISMATCH:"+key)
    need(type(raw_native_bytes) is bytes and
         hashlib.sha256(raw_native_bytes).hexdigest()==receipt.get("native_json_sha256"),
         "CACHE_NATIVE_BYTES_DIGEST_MISMATCH")
    native=json.loads(raw_native_bytes)
    new=ingest_native(request,native,calibration,raw_native_bytes)
    need(all(receipt.get(k)==new[k] for k in new),"CACHE_RESULT_CHANGED")
    return new

def plan_queue(proposals,normalized,budget,calibration,reference,binary_sha,
               output_dir):
    """Pure proposed work list; scheduler policy and guided-choice algorithm external."""
    need(type(proposals) is list and
         1<=len(proposals)<=normalized["scenario"]["runtime"]["max_native_calls"],
         "PROPOSALS_EXCEED_CONFIGURED_NATIVE_BUDGET")
    out=[];seen=set()
    for i,proposal in enumerate(proposals):
        need(type(proposal) is dict and set(proposal)=={"target","iterations"},
             "SCHEDULER_PROPOSAL_FIELDS")
        path=pathlib.Path(output_dir)/("case_%02d"%i)/"result.json"
        req=make_request(normalized,budget,calibration,reference,binary_sha,
                         proposal["target"],proposal["iterations"],path)
        need(req["case_key"] not in seen,"DUPLICATE_PROPOSED_EVALUATION")
        seen.add(req["case_key"]);out.append(req)
    return out

def summarize(observations,official_total,material_distance_fraction=0.10,
              near_loss_fraction=0.01):
    """Observed ranking only. No global-optimum or statistically-proven-best label."""
    need(type(observations) is list and len(observations)>0,"NO_NATIVE_RESULTS")
    need(type(official_total) is int and official_total>0,"INVALID_TOTAL")
    need(0<=material_distance_fraction<=1 and 0<=near_loss_fraction<=1,
         "INVALID_NEARBY_THRESHOLDS")
    seen=set()
    for x in observations:
        need(x.get("status")=="PASS_NATIVE_DPS_AND_RATING","INVALID_OBSERVATION")
        need(sum(x["target"].values())==official_total,"OBSERVATION_TOTAL_MISMATCH")
        need(x["case_key"] not in seen,"DUPLICATE_NATIVE_OBSERVATION")
        seen.add(x["case_key"])
    ranked=sorted(observations,key=lambda x:(-x["dps_mean"],x["case_key"]))
    leader=ranked[0];alts=[]
    for cand in ranked[1:]:
        # Half L1 is number of rating points transferred among stats.
        moved=sum(abs(leader["target"][k]-cand["target"][k])
                  for k in STATS)/2
        relative_drop=(leader["dps_mean"]-cand["dps_mean"])/leader["dps_mean"]
        diff=leader["dps_mean"]-cand["dps_mean"]
        half=1.96*math.hypot(leader["dps_sem"],cand["dps_sem"])
        if moved>=official_total*material_distance_fraction and \
           relative_drop<=near_loss_fraction:
            alts.append({"case_key":cand["case_key"],"target":cand["target"],
                "dps_mean":cand["dps_mean"],"dps_sem":cand["dps_sem"],
                "rating_moved":moved,"observed_loss_fraction":relative_drop,
                "difference_95pct_halfwidth_approx":half,
                "statistically_separated_approx95":diff>half})
    return {"schema":"v064_observed_statistical_summary_v1",
       "status":"BOUNDED_OBSERVED_RANKING_NOT_GLOBAL_OPTIMUM",
       "evaluated":len(ranked),"observed_best_case_key":leader["case_key"],
       "observed_best_target":leader["target"],
       "observed_best_dps":leader["dps_mean"],
       "observed_best_dps_sem":leader["dps_sem"],
       "materially_distinct_near_performing":alts,
       "global_optimum_proven":False,
       "selection_engine_connected":False,
       "uncertain_pairwise_dps_must_not_be_declared_optimal":True}
