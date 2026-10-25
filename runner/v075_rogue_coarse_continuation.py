#!/usr/bin/env python3
"""v075: bounded 350-rating coarse scouts after independently confirmed D.

No new scheduler. Native JSON2 historical authentication via v072/v073/v074.
Two 60-iteration v065 scouts are *exploratory only*. A/B/D 320-iteration
results remain the high-precision reference and are never re-run or overwritten.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import pathlib
import sys

import v063_numeric_injection as numeric
import v064_adaptive_evaluator_port as port
import v065_original_scheduler_native_bridge as engine
import v065_v015_scheduler_adapter as scheduler
import v068_rogue_two_native_probe as probe
import v069_rogue_official_budget_native as official
import v073_rogue_material_adaptive_scout as v073
import v074_rogue_selected_D_high_confirmation as v074

SCHEMA = "v075_rogue_coarse_continuation_two_native_v1"
COARSE_STEP = 350
FINE_STEP_PLANNED_ONLY = 100
ITERATIONS = 60
NATIVE_CAP = 2

def need(x, reason):
    if not x:
        raise ValueError(reason)

def load(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf8"))

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def checked_history(witness, official_root, first_root, high_root,
                    material_root, confirmed_root):
    prepared = official.prepare(witness, probe.BIN_SHA)
    normalized, static, high_pair = v073.validate_prior_confirmations(
        prepared, official_root, first_root, high_root)
    coarse = v074.replay_prior_scouts(prepared, normalized, static,
                                      high_pair, material_root)
    root=pathlib.Path(confirmed_root)
    summary=load(root/"V074_RECEIPT.json")
    need(summary.get("status")=="PASS_ONE_SELECTED_D_FRESH_320_NATIVE_CONFIRMATION"
         and summary.get("T")==3150
         and summary.get("historical_native_results_attested")==8
         and summary.get("native_attempts_total_durable")==1
         and summary.get("sha_checked_cache_replay") is True
         and summary.get("new_native_calls_this_invocation")==0
         and summary.get("confirmed_D",{}).get("target")==v074.EXPECTED_D,
         "PRIOR_V074_HOLDOUT_CONFIRMED_AND_CACHED_REQUIRED")
    folder=root/"confirm_D"
    req=port.make_request(normalized,static,prepared["calibration"],
             prepared["reference"],probe.BIN_SHA,v074.EXPECTED_D,320,
             folder/"result.json")
    source=(folder/"input.simc").read_bytes()
    raw=(folder/"result.json").read_bytes()
    receipt_raw=(folder/"native_receipt.json").read_bytes()
    receipt=json.loads(receipt_raw)
    same=numeric.input_parts(source.decode("utf8"))
    intended=numeric.input_parts(req["input"])
    need(same["stable_sha256"]==intended["stable_sha256"]==
         prepared["calibration"]["stable_profile_sha256"]
         and same["gear_override"]==intended["gear_override"]
         and source.decode("utf8").splitlines().count("iterations=320")==1,
         "V074_ORIGINAL_PROFILE_OR_ITERATION_DRIFT")
    # The historical SimC input serializes its ORIGINAL absolute JSON2
    # destination. On artifact relocation only the stable profile and gear
    # injection must match a regenerated request; the historical full input
    # SHA must match its saved Native receipt (not a relocated request).
    need(sha(source)==receipt.get("input_sha256")==
         summary["confirmed_D"]["input_sha256"]
         and sha(raw)==receipt.get("native_json_sha256")==
         summary["confirmed_D"]["native_json_sha256"]
         and sha(receipt_raw)==summary["confirmed_D"]["native_receipt_sha256"],
         "V074_HIGH_INPUT_JSON2_OR_RECEIPT_SHA_CHANGED")
    need(receipt.get("status")=="PASS_NATIVE_DPS_AND_RATING"
         and receipt.get("case_key")==req["case_key"]
         and receipt.get("scenario_digest")==req["scenario_digest"]
         and receipt.get("simc_binary_sha256")==probe.BIN_SHA
         and receipt.get("iterations")==320
         and receipt.get("target")==v074.EXPECTED_D,
         "V074_HIGH_RECEIPT_NOT_SAME_CASE")
    high_D=port.ingest_native(req,json.loads(raw),prepared["calibration"],raw)
    for k in ("dps_mean","dps_sem","dps_samples","rating_actual",
              "native_json_sha256"):
        need(high_D[k]==receipt.get(k)==summary["confirmed_D"].get(k),
             "V074_HIGH_MEASUREMENT_CHANGED:"+k)
    high_D["simc_seed"]=receipt.get("simc_seed")
    need(high_D["simc_seed"]==summary["confirmed_D"]["seed"]
         and high_D["dps_samples"]>=300
         and high_D["rating_actual"]==v074.EXPECTED_D,
         "V074_HIGH_D_SEED_OR_RATING_CHANGED")
    high=[high_pair[0],high_pair[1],high_D]
    need(len({scheduler.key(x["target"]) for x in high})==3
         and all(x["dps_samples"]>=300 for x in high),
         "THREE_HIGH_PRECISION_ANCHORS_NOT_DISTINCT")
    total, low, upper=scheduler.bounds(normalized,static)
    need(total==3150 and static["G_if_complete"]==2847
         and static["budget"]["J"]==138 and static["budget"]["F"]==165
         and static["budget"]["oil_stays_OUTSIDE_T"] is True
         and static["locked_L_when_all_specials_observed"]==
           {"crit_rating":100,"haste_rating":201,
            "mastery_rating":0,"versatility_rating":0},
         "OFFICIAL_GJF_OR_FIXED_L_DRIFT")
    return prepared,normalized,static,high,coarse

def preferred_high(high):
    """Only independent 320-iteration DPS means may define the reference."""
    return max(high,key=lambda x:x["dps_mean"])

def report_exploration(high, historical_scouts, fresh, normalized, static):
    leader=preferred_high(high)
    total=static["budget"]["T_official"]
    all_scouts=list(historical_scouts)+list(fresh)
    unique={scheduler.key(o["target"]) for o in all_scouts}
    items=[]
    for x in fresh:
        delta=x["dps_mean"]-leader["dps_mean"]
        half=1.9599639854*math.hypot(x["dps_sem"],leader["dps_sem"])
        distance=v073.moved(x["target"],leader["target"])
        items.append({"target":x["target"],"scout_dps_mean":x["dps_mean"],
               "scout_dps_sem":x["dps_sem"],"high_reference":leader["target"],
               "scout_minus_high_reference_dps":delta,
               "approx_unadjusted_95pct_ci":[delta-half,delta+half],
               "rating_moved_from_high_reference":distance,
               "observed_mean_within_1pct_loss":delta >=
                              -0.01*leader["dps_mean"],
               "material_distance_at_least_10pct":distance>=math.ceil(0.1*total),
               "statistically_confirmed_best":False,
               "global_near_best_alternative_proven":False})
    # Test/provisional switching rule, NOT a locked product policy. Coarse
    # search remains open while v015 feasible unobserved neighbors exist.
    high_keys={scheduler.key(x["target"]) for x in high}
    all_observed=high+[x for x in all_scouts
                       if scheduler.key(x["target"]) not in high_keys]
    rows=scheduler.observations_by_vector(all_observed,
                 *scheduler.bounds(normalized,static))
    try:
        anchor,candidate,hint=scheduler.choose_next(rows,COARSE_STEP,
                                    *scheduler.bounds(normalized,static))
        next_step=COARSE_STEP
        next_reason="UNTESTED_COARSE_NEIGHBORS_REMAIN"
        next_candidate=scheduler.to_target(candidate)
    except scheduler.SchedulerBlocked as exc:
        need(str(exc)=="NO_MORE_FEASIBLE_NEIGHBORS","COARSE_PLANNER_FAILED:"+str(exc))
        # No unobserved 350-step neighbors from explored anchors: only
        # now offer the existing v015 100-step neighborhood.
        anchor,candidate,hint=scheduler.choose_next(rows,FINE_STEP_PLANNED_ONLY,
                                    *scheduler.bounds(normalized,static))
        next_step=FINE_STEP_PLANNED_ONLY
        next_reason="COARSE_NEIGHBORS_EXHAUSTED_FINER_STEP_ONLY_PROPOSED"
        next_candidate=scheduler.to_target(candidate)
    return {
       "measured_high_precision_reference":{"target":leader["target"],
          "dps_mean":leader["dps_mean"],"dps_sem":leader["dps_sem"],
          "dps_samples":leader["dps_samples"]},
       "all_coarse_scouts_unique":len(unique),
       "new_scouts":items,
       "next_step_proposal_only":next_step,
       "next_step_reason":next_reason,
       "next_target_proposal_only":next_candidate,
       "step_change_requires_future_separate_request":True,
       "low_and_high_iterations_never_pooled":True,
       "global_optimum_proven":False,
       "convergence_proven":False,
       "material_near_best_alternative_proven":False,
       "original_v015_policy_reused":True,
       "provisional_rule_not_user_final_policy":True}

def run(witness,official_root,first_root,high_root,material_root,confirmed_root,
        out,binary=None,cache_only=False,cancel_file=None):
    out=pathlib.Path(out)
    out.mkdir(parents=True,exist_ok=True)
    report=out/"V075_RECEIPT.json"
    result={"schema":SCHEMA,"status":"BLOCKED","official_formula":"T=G+J+F",
         "coarse_step":COARSE_STEP,"fine_step_proposal_only":FINE_STEP_PLANNED_ONLY,
         "scout_iterations":ITERATIONS,"native_cap":NATIVE_CAP,
         "new_native_calls_this_invocation":0,
         "new_attempts_started_this_invocation":0,
         "historical_native_results_reused":0,"global_optimum_proven":False}
    try:
        prepared,normalized,static,high,coarse=checked_history(
             witness,official_root,first_root,high_root,material_root,confirmed_root)
        anchor=preferred_high(high)
        need(anchor["target"]==v074.EXPECTED_D,
             "CONFIRMED_HIGH_PRECISION_D_NOT_LEADER")
        # v073 exploratory D shares a target with v074 confirmed D.
        # Keep the 320-iteration measurement as the only scheduler value
        # for that target; retain scout D's real SHA in provenance/identity.
        high_keys={scheduler.key(x["target"]) for x in high}
        coarse_unique=[x for x in coarse
                       if scheduler.key(x["target"]) not in high_keys]
        state=scheduler.initial_state(normalized,static,high+coarse_unique,
                           step=COARSE_STEP,scout_max=NATIVE_CAP,
                           confirmation_runs=2)
        result.update({"status":"PASS_COARSE_CONTINUATION_PLAN_ZERO_NATIVE",
           "T":3150,"G":2847,"J":138,"F":165,
           "historical_native_results_reused":9,
           "history":{"v069_calibration":2,"v070_official":1,"v071_scout":1,
                      "v072_high":2,"v073_coarse":2,"v074_selected_D_high":1},
           "high_precision_reference_D":{
             "target":anchor["target"],"dps_mean":anchor["dps_mean"],
             "dps_sem":anchor["dps_sem"],"dps_samples":anchor["dps_samples"],
             "native_json_sha256":anchor["native_json_sha256"]},
           "prior_coarse_targets":[x["target"] for x in coarse],
           "scenario_digest":normalized["scenario_digest"],
           "profile_sha256":prepared["calibration"]["stable_profile_sha256"]})
        if binary is None:
            next_one=scheduler.next_scout(state,normalized,static,
                 prepared["calibration"],prepared["reference"],probe.BIN_SHA,
                 out/"scout_00"/"result.json",ITERATIONS)
            result["first_scout_target"]=next_one["case"]["target"]
            result["first_scout_selection"]=next_one["decision"]
        else:
            binary=pathlib.Path(binary).resolve()
            need(binary.is_file() and sha(binary.read_bytes())==probe.BIN_SHA,
                 "PINNED_SIMC_BINARY_DRIFT")
            identity={"schema":SCHEMA,
                "scenario_digest":normalized["scenario_digest"],
                "stable_profile_sha256":prepared["calibration"]["stable_profile_sha256"],
                "binary_sha256":probe.BIN_SHA,
                "simc_revision":prepared["calibration"]["native_revision"],
                "prior_high_native_sha256s":[x["native_json_sha256"] for x in high],
                "prior_scout_sha256s":[x["native_json_sha256"] for x in coarse],
                "step":COARSE_STEP,"iterations":ITERATIONS,"native_cap":NATIVE_CAP}
            seal=out/"V075_IDENTITY.json"
            if seal.exists():
                need(load(seal)==identity,"RESUME_IDENTITY_CHANGED")
            else:
                need(not any((out/("scout_%02d"%i)).exists()
                             for i in range(NATIVE_CAP)),
                     "UNSEALED_NATIVE_CASE_FOLDER_PRESENT")
                engine.write_atomic(seal,identity)
            progress_file=out/"V065_PROGRESS.json"
            progress={"schema":SCHEMA,"scenario_digest":normalized["scenario_digest"],
                      "prior_high_native_sha256s":identity["prior_high_native_sha256s"],
                      "prior_scout_sha256s":identity["prior_scout_sha256s"],
                      "step":COARSE_STEP,"iterations":ITERATIONS,
                      "native_cap":NATIVE_CAP,"native_attempts":0,"status":"READY"}
            if progress_file.exists():
                previous=load(progress_file)
                need(all(previous.get(k)==progress[k] for k in
                     ("schema","scenario_digest","prior_high_native_sha256s",
                      "prior_scout_sha256s","step","iterations","native_cap"))
                     and type(previous.get("native_attempts")) is int
                     and 0<=previous["native_attempts"]<=NATIVE_CAP,
                     "DURABLE_PROGRESS_IDENTITY_DRIFT")
                progress["native_attempts"]=previous["native_attempts"]
            else:
                engine.write_atomic(progress_file,progress)
            fresh=[]
            for i in range(NATIVE_CAP):
                folder=out/("scout_%02d"%i)
                proposal=scheduler.next_scout(state,normalized,static,
                     prepared["calibration"],prepared["reference"],probe.BIN_SHA,
                     folder/"result.json",ITERATIONS)
                request=proposal["case"]
                need(request["target"]!=anchor["target"]
                     and scheduler.key(request["target"]) not in
                        {scheduler.key(x["target"]) for x in high+coarse+fresh},
                     "REPEATED_HISTORICAL_OR_SAME_COARSE_TARGET")
                if cancel_file is not None:
                    need(not pathlib.Path(cancel_file).exists(),"USER_CANCEL_FILE")
                if not ((folder/"result.json").exists()
                        or (folder/"native_receipt.json").exists()):
                    need(not (folder/"input.simc").exists(),
                         "INCOMPLETE_PRIOR_NATIVE_REQUIRES_MANUAL_RECOVERY")
                    need(not cache_only,"CACHE_ONLY_REFUSES_NEW_NATIVE")
                    need(progress["native_attempts"]<NATIVE_CAP,
                         "NATIVE_ATTEMPT_LIMIT_EXHAUSTED")
                    result["new_attempts_started_this_invocation"]+=1
                obs=engine.execute_one(request,prepared["calibration"],binary,
                      folder,progress,cancel_file=cancel_file,
                      cache_only=cache_only)
                need(obs["iterations"]==ITERATIONS and obs["dps_samples"]>=40
                     and obs["rating_actual"]==request["target"],
                     "NEW_SCOUT_JSON2_RATING_OR_SAMPLE_MISMATCH")
                result["new_native_calls_this_invocation"]+=int(
                          obs.get("source")=="NEW_NATIVE")
                state=scheduler.accept_scout(state,request,obs)
                fresh.append(obs)
                result["completed_scouts"]=len(fresh)
                result["status"]="PARTIAL_REAL_SCOUTS"
                engine.write_atomic(report,result)
            review=report_exploration(high,coarse,fresh,normalized,static)
            result.update({"status":"PASS_TWO_MORE_COARSE_ROGUE_NATIVE_SCOUTS",
                "scouts":[{"target":r["target"],"source":r["source"],
                           "dps_mean":r["dps_mean"],"dps_sem":r["dps_sem"],
                           "dps_samples":r["dps_samples"],"rating_actual":r["rating_actual"],
                           "simc_seed":r.get("simc_seed"),
                           "native_json_sha256":r["native_json_sha256"]}
                          for r in fresh],
                "exploration":review,
                "native_attempts_total_durable":progress["native_attempts"],
                "sha_checked_cache_replay":all(r["source"]=="CACHED_VERIFIED_NATIVE"
                                              for r in fresh)})
    except Exception as exc:
        result["status"]="BLOCKED_OR_PARTIAL"
        result["error"]=type(exc).__name__+":"+str(exc)
        f=out/"V065_PROGRESS.json"
        if f.exists():
            try:
                result["native_attempts_total_durable"]=load(f).get("native_attempts")
            except (OSError,ValueError):
                result["progress_unreadable"]=True
    engine.write_atomic(report,result)
    print("V075",result["status"],"new_native",
          result["new_native_calls_this_invocation"],
          "error",result.get("error"),flush=True)
    return 0 if result["status"].startswith("PASS") else 3

def main(argv=None):
    p=argparse.ArgumentParser()
    for flag in ("witness-root","prior-official","prior-scout","prior-high",
                 "prior-material","prior-confirmed","out"):
        p.add_argument("--"+flag,required=True,type=pathlib.Path)
    p.add_argument("--binary",type=pathlib.Path)
    p.add_argument("--cache-only",action="store_true")
    p.add_argument("--cancel-file",type=pathlib.Path)
    x=p.parse_args(argv)
    return run(x.witness_root,x.prior_official,x.prior_scout,x.prior_high,
               x.prior_material,x.prior_confirmed,x.out,x.binary,
               x.cache_only,x.cancel_file)

if __name__=="__main__":
    sys.exit(main())
