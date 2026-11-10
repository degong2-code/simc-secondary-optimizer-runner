#!/usr/bin/env python3
"""v314 8 DPS-specialization x 2 CHMV-domain validation matrix.

Pure experimental research contract. No current-equipment redistribution,
equipment recommendation, global-optimum proof, or SimC effects model.
Strictly source-first: no historical DPS seed or old 9906 Warlock cache
allowed in a new candidate-policy session.
"""
from __future__ import annotations
import hashlib
import json
import math
import statistics

import v106_user_session_controller as users

SCHEMA="p2_v314_cross_spec_8x2_distribution_native_matrix_v1"
ITER_SCOUT=35
ITER_CONFIRM=320
NATIVE_CAP=1008
TIME_CAP_SECONDS=540
KEYS=("crit_rating","haste_rating","mastery_rating","versatility_rating")
SOURCE_BUILD="12.1.5.70783"
BINARY_SHA256="6b83e4d5d2216faf91511fb00ae712cdf4cc0224b0c83107e8c9c7358c24bfc6"

# Distinct source-backed roles/armor and genuinely different optimization
# domains. Variants also alter a user-visible stat cap, not merely display
# labels. Both algorithms are allowed only this case's same newly built
# profile and exactly the same 1008-call and 540-sec caps.
_SPECS=(
    ("marksmanship_hunter","hunter","marksmanship",3120,3640),
    ("beast_mastery_hunter","hunter","beast_mastery",3260,3680),
    ("arcane_mage","mage","arcane",3180,3620),
    ("frost_mage","mage","frost",3280,3710),
    ("fire_mage","mage","fire",3320,3730),
    ("frost_death_knight","death_knight","frost",3220,3660),
    ("subtlety_rogue","rogue","subtlety",3350,3770),
    ("assassination_rogue","rogue","assassination",3210,3590),
)
CASES={
    f"{key}__{variant}":{
        "id":f"{key}__{variant}",
        "class":cl,"spec":sp,"race":("dwarf" if sp=="elemental" else "human"),"ilevel":334,
        "final_T":low if variant=="wide" else high,
        "max_single_stat_percent":60 if variant=="wide" else 45,
        "ordinary_gems":4,"special_gem_id":None,"weapon_oil":None,
        "trinkets":"new_profile_user_choices_from_current_verified_default",
        "talents":"new_profile_user_choices_from_current_verified_default",
        "raid_targets":1,
        "raid_seconds":300,
        "source_build":SOURCE_BUILD,
    }
    for key,cl,sp,low,high in _SPECS
    for variant in ("wide","narrow")
}


def need(ok,why):
    if not ok:
        raise ValueError("V314_"+why)


def select(case_id):
    need(type(case_id) is str and case_id in CASES,
         "EXACT_APPROVED_CROSS_SPEC_CASE_REQUIRED")
    data=dict(CASES[case_id])
    need((data["class"],data["spec"]) in users.SUPPORTED,
         "ONLY_26_DPS_SUPPORTED_SPECS")
    control=users.standard_controls((data["class"],data["spec"]))
    need(type(control.get("talents")) is str and bool(control["talents"])
         and len(control["trinket_ids"])==2 and
         control["consumable_choices"]["diamond_id"]==0,
         "PRODUCT_DEFAULT_CHARACTER_AND_TRINKETS_REQUIRED")
    need(not control.get("import_simc_profile") and
         not control.get("profile_path") and
         not control.get("simc_profile"),
         "NO_IMPORTED_OR_HISTORICAL_COMPLETE_SIMC_PROFILE")
    control.update({
        "race":data["race"],"final_T":data["final_T"],
        "max_single_stat_percent":data["max_single_stat_percent"],
        "oil_hands":[]})
    need(control["targets"]==1 and control["duration_seconds"]==300
         and control["raid_buffs"] is True,
         "SAME_COMBAT_CONDITIONS_REQUIRED")
    return data,control


def validate_matrix():
    need(len(CASES)==16 and len(_SPECS)==8 and
         len({(d["class"],d["spec"]) for d in CASES.values()})==8,
         "MATRIX_8_SPECS_16_CASES")
    for key,cl,sp,low,high in _SPECS:
        a,_=select(key+"__wide")
        b,_=select(key+"__narrow")
        need(low!=high and a["final_T"]!=b["final_T"]
             and a["max_single_stat_percent"]==60
             and b["max_single_stat_percent"]==45,
             "EACH_SPEC_MUST_HAVE_TWO_REAL_STAT_DOMAINS")
    return {"schema":SCHEMA,"cases":len(CASES),
            "specializations":len(_SPECS),
            "two_conditions_per_spec":True,
            "one_scenario_shared_by_both_arms":True}


def original_iterations(rows):
    need(type(rows) is list and all(
         type(r.get("iterations")) is int and r["iterations"]>0
         for r in rows),"NATIVE_ITERATION_JOURNAL_REQUIRED")
    return sum(r["iterations"] for r in rows)


def trial_summary(report,rows,elapsed_seconds,*,policy_name,
                  original_profile_sha256):
    need(policy_name in ("v290_original","v312_model_guided"),
         "UNKNOWN_OPTIMIZER_POLICY")
    need(type(rows) is list and len(rows)<=NATIVE_CAP and
         len(rows)==report["completed_cases"]==
             report["native_attempts_cumulative"] and
         report["new_native_this_invocation"]==len(rows),
         "REAL_NATIVE_JOURNAL_AND_CALL_COUNT")
    need(type(elapsed_seconds) in (int,float) and
         math.isfinite(elapsed_seconds) and elapsed_seconds>=0,
         "MEASURED_ELAPSED_SECONDS_REQUIRED")
    need(type(original_profile_sha256) is str and
         len(original_profile_sha256)==64,
         "SOURCE_PROFILE_SHA256_REQUIRED")
    precision=[r for r in rows
               if r["phase"]=="precision" and
               r["iterations"]==ITER_CONFIRM]
    selected=sorted(precision,key=lambda r:(
        -r["dps_mean"],r["case_key"]))
    result={
        "policy":report["policy"],
        "status":report["status"],
        "native_calls":len(rows),
        "unique_scouts":len({tuple(r["target"][k] for k in KEYS)
                           for r in rows if r["phase"]=="scout"}),
        "confirmed_candidates":len(selected),
        "actual_simc_iterations":original_iterations(rows),
        "measured_seconds":round(elapsed_seconds,3),
        "input_profile_sha256":original_profile_sha256,
        "no_historical_native_results_imported":True,
        "best_confirmed_320":({
            "target":selected[0]["target"],
            "dps":selected[0]["dps_mean"],
            "sem":selected[0]["dps_sem"],
            "seed":selected[0].get("simc_seed"),
            "native_json_sha256":selected[0]["native_sha256"],
        } if selected else None),
        "selected_pair_95":report.get("confirmed_selected_pair_95"),
        "global_optimum_proven":False}
    need(result["unique_scouts"]<=len(rows) and
         result["actual_simc_iterations"]>=35*len(rows),
         "V314_NATIVE_BUDGET_ACCOUNTING")
    return result


def paired_result(case,old,new):
    need(old["input_profile_sha256"]==
         new["input_profile_sha256"] and
         old["policy"]=="v290_multiscale_noisy_simplex_policy_v1" and
         new["policy"]=="v312_model_guided_multiregion_native_proposal_v1",
         "NOT_SAME_PROFILE_AND_TWO_EXPECTED_ALGORITHMS")
    a,b=old["best_confirmed_320"],new["best_confirmed_320"]
    if not (a and b):
        return {"case_id":case["id"],"status":"INCOMPLETE_CONFIRMATIONS",
                "relative_dps_difference_pct":None,
                "95_pairwise_separated":False,
                "global_optimum_proven":False}
    gap=b["dps"]-a["dps"]
    half=1.959963984540054*math.hypot(a["sem"],b["sem"])
    seeds=(a["seed"],b["seed"])
    distinct=all(x is not None for x in seeds) and seeds[0]!=seeds[1]
    return {
        "case_id":case["id"],"specialization":case["class"]+"/"+case["spec"],
        "stat_distribution":{
            "final_T":case["final_T"],
            "max_single_stat_percent":case["max_single_stat_percent"]},
        "status":("COMPLETE_EQUAL_NATIVE_CALLS" if
                  old["native_calls"]==new["native_calls"]==NATIVE_CAP
                  else "PARTIAL_OR_TIME_CAPPED"),
        "v312_minus_v290_confirmed_dps":round(gap,6),
        "relative_dps_difference_pct":round(100*gap/a["dps"],6),
        "selected_nominal_95_halfwidth_dps":round(half,6),
        "95_pairwise_separated":bool(distinct and abs(gap)>half),
        "distinct_simc_seeds_observed":bool(distinct),
        "different_simc_iteration_budgets":(
            old["actual_simc_iterations"]!=new["actual_simc_iterations"]),
        "v290_total_iterations":old["actual_simc_iterations"],
        "v312_total_iterations":new["actual_simc_iterations"],
        "v290_elapsed_seconds":old["measured_seconds"],
        "v312_elapsed_seconds":new["measured_seconds"],
        "winner_selection_bias_corrected":False,
        "familywise_multiple_comparisons_95_proven":False,
        "global_optimum_proven":False,
    }


def aggregate(paired_cases):
    rows=[r for r in paired_cases if
          r.get("status")=="COMPLETE_EQUAL_NATIVE_CALLS"
          and r.get("relative_dps_difference_pct") is not None]
    distinct={r["case_id"] for r in rows}
    need(len(distinct)==len(rows),"DUPLICATE_CROSS_SPEC_CASE")
    gains=[r["relative_dps_difference_pct"] for r in rows]
    return {
        "schema":SCHEMA,"total_planned":16,"completed":len(rows),
        "all_sixteen_complete":len(rows)==16,
        "coverage_specializations":len({
            r["specialization"] for r in rows}),
        "v312_observed_win_count":sum(x>0 for x in gains),
        "v290_observed_win_count":sum(x<0 for x in gains),
        "median_v312_relative_dps_gain_pct":(
            round(statistics.median(gains),6) if gains else None),
        "v312_faster_count":sum(
            r["v312_elapsed_seconds"]<r["v290_elapsed_seconds"] for r in rows),
        "native_call_equal_not_simc_iteration_equal":True,
        "one_case_not_a_cross_spec_conclusion":True,
        "must_not_promote_new_policy_from_single_class":True,
        "familywise_95_proven":False,
        "global_optimum_proven":False}
