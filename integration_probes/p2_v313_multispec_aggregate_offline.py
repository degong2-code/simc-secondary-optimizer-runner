#!/usr/bin/env python3
"""Aggregate eight independently reported cross-spec real SimC v313 trials.

Read-only, does NOT open old cross-session Native caches, claim a familywise
95% statement, or treat missing/failed cases as optimizer losses. Never
compare absolute DPS across classes; use within-case relative differences.
"""
from __future__ import annotations
import argparse
import json
import pathlib
from runner import v313_multispec_matrix_contract as matrix


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--artifact-folder",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    root=pathlib.Path(args.artifact_folder).resolve(strict=True)
    found=sorted(root.rglob("receipt.json"))
    cases={}
    details={}
    for path in found:
        report=json.loads(path.read_text())
        if report.get("schema")!="p2_v313_source_first_4spec_x2_distribution_real_AB_v1":
            continue
        identifier=report["case"]["id"]
        if identifier in cases or identifier not in matrix.CASES:
            raise ValueError("V313_CROSS_SPEC_DUPLICATE_OR_UNKNOWN_CASE")
        if report["case"]!=matrix.CASES[identifier]:
            raise ValueError("V313_CROSS_SPEC_CONTEXT_DRIFT")
        cases[identifier]=report
        details[identifier]={
            "status":report["status"],
            "native_by_algorithm":{
                label:arm.get("native_calls")
                for label,arm in report.get("trials",{}).items()},
            "total_iterations_by_algorithm":{
                label:arm.get("actual_simc_iterations")
                for label,arm in report.get("trials",{}).items()},
            "seconds_by_algorithm":{
                label:arm.get("measured_seconds")
                for label,arm in report.get("trials",{}).items()},
            "pairwise_result":report.get("pairwise_result"),
            "cross_profile_cache_not_authorized":True,
            "has_full_original_native_archive":None}
        if (report.get("pairwise_result") is not None and
            report["pairwise_result"]["case_id"]!=identifier):
            raise ValueError("V313_PAIRWISE_REPORT_DIFFERENT_CASE")
    paired=[record["pairwise_result"] for record in cases.values()
            if record.get("pairwise_result") is not None]
    result=matrix.aggregate(paired)
    result.update({
        "workflow_case_receipts_found":len(cases),
        "case_statuses":details,
        "expected_case_ids":list(matrix.CASES),
        "missing_or_blocked_case_ids":[key for key in matrix.CASES
                                       if key not in cases or
                                       not cases[key].get("pairwise_result")
                                       or cases[key]["pairwise_result"]["status"]
                                          !="COMPLETE_EQUAL_NATIVE_CALLS"],
        "policy_change_approved":False,
        "default_v290_retained":True,
        "no_global_or_familywise_95_claim":True,
        "statistical_power_not_established_from_eight_cases":True})
    out=pathlib.Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(
        result,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("P2_V313_CROSS_SPEC_CASE_AGGREGATION",json.dumps({
        "found":len(cases),"complete":result["completed"],
        "specializations":result["coverage_specializations"],
        "v312_observed_wins":result["v312_observed_win_count"],
        "median_v312_dps_gain_pct":result[
            "median_v312_relative_dps_gain_pct"],
        "not_global_optimum":True},sort_keys=True),flush=True)
    return result


if __name__=="__main__":
    main()
