#!/usr/bin/env python3
"""P2 IDEA-001 measurement-budget analysis of REAL v313/v314 compact receipts.

This script never executes SimC and NEVER fits an identifiable fixed-per-call
cost / iteration slope from two different policy runs. Separate "same Native"
from "same iterations", "same wall" and 95-selected-pair claims. Source bound
and case bound; no old completed character profile or case Native cache reuse.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import statistics

from runner import v313_multispec_matrix_contract as m313
from runner import v314_fresh_eight_spec_matrix_contract as m314

SCHEMA="p2_v315_idea001_native_iteration_vs_wall_research_only_v1"
SCHEMAS={
    "p2_v313_source_first_4spec_x2_distribution_real_AB_v1":("v313",m313.CASES),
    "p2_v314_source_first_8spec_x2_distribution_real_AB_v1":("v314",m314.CASES),
}
POLICIES={
    "v290_original":"v290_multiscale_noisy_simplex_policy_v1",
    "v312_model_guided":"v312_model_guided_multiregion_native_proposal_v1",
}
ARMS=("v290_original","v312_model_guided")


def need(ok,why):
    if not ok:
        raise ValueError("P2_V315_"+why)


def number(value,nonnegative=False):
    return type(value) in (int,float) and math.isfinite(value) and (
        value>=0 if nonnegative else value>0)


def validate_arm(arm,policy,profile_sha):
    need(type(arm) is dict and arm.get("policy")==POLICIES[policy],
         "EXPECTED_POLICY_AND_RECEIPT_ARM")
    need(arm.get("input_profile_sha256")==profile_sha and
         type(profile_sha) is str and len(profile_sha)==64,
         "NEW_SOURCE_PROFILE_IDENTITY_MISMATCH")
    calls=arm.get("native_calls")
    iterations=arm.get("actual_simc_iterations")
    sec=arm.get("measured_seconds")
    need(type(calls) is int and 1<=calls<=1008
         and type(iterations) is int and iterations>=35*calls
         and number(sec),
         "REAL_MEASURED_NATIVE_ITERATIONS_WALL_REQUIRED")
    need(type(arm.get("confirmed_candidates")) is int
         and 0<=arm["confirmed_candidates"]<=calls,
         "PRECISION_COUNT_REQUIRED")
    need(arm.get("no_historical_native_results_imported") is True,
         "NO_HISTORICAL_DPS_SEED_IMPORT")
    need(arm.get("native_file_bytes_rechecked_cache_only") is True,
         "ORIGINAL_NATIVE_REPLAY_PROOF_REQUIRED")
    best=arm.get("best_confirmed_320")
    need(type(best) is dict and number(best.get("dps"))
         and number(best.get("sem"),nonnegative=True)
         and type(best.get("native_json_sha256")) is str
         and len(best["native_json_sha256"])==64,
         "ORIGINAL_PRECISION_320_DPS_SEM_REQUIRED")
    return {
        "native_calls":calls,
        "total_simc_iterations":iterations,
        "measured_wall_seconds":float(sec),
        "confirmed_320_candidates":arm["confirmed_candidates"],
        "effective_iterations_per_wall_second_including_overheads":
            round(iterations/sec,3),
        "effective_calls_per_wall_second_including_overheads":
            round(calls/sec,5),
        "confirmed_320_dps":best["dps"],
        "confirmed_320_sem":best["sem"],
    }


def evaluate_receipt(report):
    schema=report.get("schema")
    if schema not in SCHEMAS:
        return None
    label,cases=SCHEMAS[schema]
    case=report.get("case")
    need(type(case) is dict and case.get("id") in cases and
         case==cases[case["id"]],"EXACT_NEW_PROFILE_CASE_REQUIRED")
    ident=report["source_profile_sha256"]
    arms=report.get("trials",{})
    need(type(arms) is dict and
         set(ARMS).issubset(arms),"BOTH_POLICY_ARMS_REQUIRED")
    validated={policy:validate_arm(arms[policy],policy,ident)
               for policy in ARMS}
    p=report.get("pairwise_result")
    need(type(p) is dict and p.get("case_id")==case["id"],
         "ORIGINAL_CASE_PAIRWISE_REQUIRED")
    need(p.get("status")=="COMPLETE_EQUAL_NATIVE_CALLS" and
         p.get("different_simc_iteration_budgets")==(
             validated[ARMS[0]]["total_simc_iterations"]!=
             validated[ARMS[1]]["total_simc_iterations"]),
         "PAIRWISE_ITERATION_IDENTITY_DRIFT")
    need(report.get("scenario_from_existing_native_winner") is False and
         report.get("prior_dps_cache_reused") is False and
         report.get("default_v290_changed") is False,
         "MUST_USE_INDEPENDENT_FRESH_NEW_PROFILE")
    if label=="v314":
        need(report.get("new_profile_generated_in_this_case_workspace") is True
             and report.get("historical_completed_profile_imported") is False,
             "V314_NEW_PROFILE_CONFIRMED_REQUIRED")
    a,b=validated[ARMS[0]],validated[ARMS[1]]
    need(a["native_calls"]==b["native_calls"]==1008,
         "NEED_EXACT_EQUAL_NATIVE_CALLS")
    p2_iterations=b["total_simc_iterations"]/a["total_simc_iterations"]
    p2_wall=b["measured_wall_seconds"]/a["measured_wall_seconds"]
    return {
        "cohort":label,"case_id":case["id"],
        "specialization":case["class"]+"/"+case["spec"],
        "manual_final_T":case["final_T"],
        "stat_cap_percent":case["max_single_stat_percent"],
        "arms":validated,
        "v312_iteration_ratio_to_v290":round(p2_iterations,6),
        "v312_wall_ratio_to_v290":round(p2_wall,6),
        "v312_iteration_reduction_pct":round(100*(1-p2_iterations),4),
        "v312_wall_reduction_pct":round(100*(1-p2_wall),4),
        "v312_lower_iterations":p2_iterations<1,
        "v312_faster_wall":p2_wall<1,
        "iteration_reduction_not_equal_wall_reduction":True,
        "native_calls_equal":True,
        "simc_iterations_equal":a["total_simc_iterations"]==
                                 b["total_simc_iterations"],
        "v312_relative_confirmed_dps_pct":
            p["relative_dps_difference_pct"],
        "selected_pair_95_separated":p["95_pairwise_separated"],
        "selected_pair_unadjusted_95_only":True,
        "actual_time_to_best_320_by_checkpoint_available":False,
        "can_fit_per_native_startup_cost_from_these_two_arms":False,
        "can_fit_simc_seconds_per_iteration_from_these_two_arms":False,
        "non_identifiability_reason":
            "One aggregate timing per differing algorithm at equal Native calls "
            "does not separate initialization, IO, planning, timing order or "
            "SimC per-iteration costs; no per-call elapsed ledger here.",
        "global_optimum_proven":False,
    }


def aggregate(receipts):
    data={}
    for report in receipts:
        evaluation=evaluate_receipt(report)
        if evaluation is None:
            continue
        key=(evaluation["cohort"],evaluation["case_id"])
        need(key not in data,"DUPLICATED_NEW_PROFILE_RECEIPT")
        data[key]=evaluation
    ordered=[data[k] for k in sorted(data)]
    ratios=[x["v312_wall_ratio_to_v290"] for x in ordered]
    iter_ratios=[x["v312_iteration_ratio_to_v290"] for x in ordered]
    return {
        "schema":SCHEMA,
        "status":"OFFLINE_ORIGINAL_REAL_NATIVE_RECEIPT_COST_DESCRIPTION_ONLY",
        "recorded_cases":len(ordered),
        "v313_cases":sum(x["cohort"]=="v313" for x in ordered),
        "v314_cases":sum(x["cohort"]=="v314" for x in ordered),
        "v312_iteration_lower_cases":sum(x["v312_lower_iterations"] for x in ordered),
        "v312_wall_faster_cases":sum(x["v312_faster_wall"] for x in ordered),
        "v312_wall_slower_or_equal_cases":sum(
            not x["v312_faster_wall"] for x in ordered),
        "v312_median_iterations_ratio_to_v290":(
            round(statistics.median(iter_ratios),6) if ordered else None),
        "v312_median_wall_ratio_to_v290":(
            round(statistics.median(ratios),6) if ordered else None),
        "median_relative_confirmed_dps_pct":(
            round(statistics.median(x["v312_relative_confirmed_dps_pct"]
                                    for x in ordered),6) if ordered else None),
        "selected_pair_95_separated_cases":sum(
            x["selected_pair_95_separated"] for x in ordered),
        "cases":ordered,
        "missing_case_is_not_loss":True,
        "no_direct_cross_specialization_absolute_dps_comparison":True,
        "no_equal_iteration_comparison_performed":True,
        "no_equal_wall_clock_comparison_performed":True,
        "no_per_native_timing_trace_available":True,
        "fixed_cost_and_iteration_slope_not_identifiable":True,
        "planner_cost_model_not_calibrated":True,
        "new_real_native_calls":0,
        "algorithms_changed":False,
        "default_v290_changed":False,
        "global_optimum_proven":False,
        "familywise_95_proven":False,
        "next_required_evidence":[
            "per-request start/end elapsed time from the SAME new profile",
            "per-phase scout/precision Native timing and iteration count",
            "planner, subprocess startup, JSON2/IO, checkpoint time separately",
            "independent repetitions and fair equal-iteration or equal-wall arms",
        ]
    }


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",required=True)
    parser.add_argument("--output",required=True)
    parser.add_argument("--min-v313",type=int,default=8)
    parser.add_argument("--min-v314",type=int,default=2)
    args=parser.parse_args(argv)
    root=pathlib.Path(args.root).resolve(strict=True)
    docs=[]
    for path in sorted(root.rglob("receipt.json")):
        doc=json.loads(path.read_text())
        if doc.get("schema") in SCHEMAS:
            docs.append(doc)
    result=aggregate(docs)
    need(result["v313_cases"]>=args.min_v313 and
         result["v314_cases"]>=args.min_v314,
         "INSUFFICIENT_ORIGINAL_COMPLETE_CONDITIONS")
    destination=pathlib.Path(args.output)
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(
        result,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
    print("P2_V315_ITERATIONS_VS_WALL_REAL_SOURCE_COST_ANALYSIS",
          json.dumps({k:result[k] for k in (
              "recorded_cases","v313_cases","v314_cases",
              "v312_iteration_lower_cases","v312_wall_faster_cases",
              "v312_median_iterations_ratio_to_v290",
              "v312_median_wall_ratio_to_v290",
              "selected_pair_95_separated_cases",
              "fixed_cost_and_iteration_slope_not_identifiable",
              "new_real_native_calls")},sort_keys=True),flush=True)
    return result


if __name__=="__main__":
    main()
