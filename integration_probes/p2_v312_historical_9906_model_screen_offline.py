#!/usr/bin/env python3
"""Offline v312 model screen from three independently verified SimC cohorts.

Uses ONLY existing original 9906 scout and 48 precision records (35/320 iter).
No new Native, no simulated DPS, no reauthentication across session identities.
The 48 genuine 320-iteration outcomes are held OUT of model training.
A lower out-of-sample RMSE is model quality, NOT a demonstrated optimization
speedup, not an independent 95% superiority test, not global optimality.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import pathlib
import statistics
import zipfile
from collections import defaultdict

from runner import v307_dense_nested_coverage_grid as grid
from runner import v312_model_guided_multiregion_policy as model

SCHEMA="p2_v312_original9906_scout_48precision_holdout_screen_v1"
STATS=("crit_rating","haste_rating","mastery_rating","versatility_rating")
LOWER=(0,0,0,165)
UPPER=(2040,2040,2040,2040)
PROFILE="e193aacef751b81dcdb8b06abbedf7aa458c0ae46eeb23898b501cf3314d7f8c"
BINARY="6b83e4d5d2216faf91511fb00ae712cdf4cc0224b0c83107e8c9c7358c24bfc6"
REVISION="c20e2ad52e4c33711f74272309a5748125175fe8"


def need(ok,reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def v(row):
    return tuple(row["target"][k] for k in STATS)


def source(zip_path,index):
    zip_path=pathlib.Path(zip_path).resolve(strict=True)
    with zipfile.ZipFile(zip_path) as z:
        names=z.namelist()
        need("receipt.json" in names and
             len([n for n in names if n.endswith("V291_JOURNAL.jsonl") or
                  n=="all_accepted_compact_cases.jsonl"])==1,
             "V312_ACCEPTED_COMPACT_SOURCE_MISSING")
        name=next(n for n in names if n.endswith("V291_JOURNAL.jsonl")
                  or n=="all_accepted_compact_cases.jsonl")
        receipt=json.loads(z.read("receipt.json"))
        raw=z.read(name)
    hashkey=("all_compact_cases_sha256" if index==0 else
             "new_compact_journal_sha256")
    need(sha(raw)==receipt[hashkey],
         "V312_HISTORIC_ACCEPTED_JOURNAL_BYTES_SHA_CHANGED")
    actual_profile=receipt.get(
        "source_profile_sha256",receipt.get("new_source_profile_sha256"))
    actual_binary=(receipt.get("binary_sha256") or
                   receipt.get("native_binary_sha256") or
                   receipt.get("new_simc_binary_sha256"))
    need(actual_profile==PROFILE and actual_binary==BINARY and
         (receipt.get("revision") in (None,REVISION)) and
         receipt["new_dps_native"]==(2800,2185,4969)[index] and
         receipt["status"]==(
             "PASS_REAL_PRODUCT_FULL_LEVEL11_GRID",
             "PASS_REAL_21_GRID_25_PERCENT_OLD11_ANCHORED",
             "PASS_V310_REAL_21GRID_50PCT_NEW_ONLY")[index],
         "V312_ORIGINAL_NATIVE_SOURCE_OR_STATUS_IDENTITY_CHANGED")
    rows=[json.loads(line) for line in raw.splitlines()]
    need(len(rows)==(2800,2185,4969)[index] and
         all(v(row) and sum(v(row))==3400 and
             grid.base.legacy.eligible(v(row),3400,LOWER,UPPER)
             for row in rows),
         "V312_ORIGINAL_NATIVE_CHMV_ROW_INVALID")
    scout=[r for r in rows if r["phase"]=="scout"]
    precision=[r for r in rows if r["phase"]=="precision"]
    need(len(scout)==(2784,2169,4953)[index] and
         len(precision)==16 and
         all(r["iterations"]==35 for r in scout) and
         all(r["iterations"]==320 for r in precision),
         "V312_REAL_SCOUT_PRECISION_ITERATIONS_DRIFT")
    return receipt,scout,precision,sha(raw)


def spatial_interleaved_pool(rows):
    buckets=defaultdict(list)
    for r in rows:
        buckets[grid._cell(v(r),LOWER,UPPER)].append(r)
    for group in buckets.values():
        group.sort(key=lambda r:(grid._hash(v(r)),v(r)))
    result=[]
    for pack in itertools.zip_longest(*(buckets[key]
                                         for key in sorted(buckets))):
        result.extend(r for r in pack if r is not None)
    need(len(result)==len(rows) and
         len({v(r) for r in result})==len(rows),
         "V312_OFFLINE_HISTORIC_INTERLEAVE_NOT_BIJECTION")
    return result


def rmse(xs,ys):
    return math.sqrt(statistics.fmean(
        (a-b)**2 for a,b in zip(xs,ys)))


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--original11-compact",required=True)
    p.add_argument("--original25-compact",required=True)
    p.add_argument("--original50-compact",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args(argv)
    cohorts=[
        source(path,i) for i,path in enumerate(
            (args.original11_compact,args.original25_compact,
             args.original50_compact))]
    scouts=[r for _,s,_,_ in cohorts for r in s]
    precision=[r for _,_,c,_ in cohorts for r in c]
    unique={v(r) for r in scouts}
    heldout={v(r) for r in precision}
    need(len(scouts)==len(unique)==9906 and
         len(precision)==len(heldout)==48 and
         heldout.issubset(unique),
         "V312_HISTORIC_ORIGINAL9906_48_COHORTS_NOT_UNIQUE")
    original_scouts={v(r):r for r in scouts}
    holdout_truth=[r["dps_mean"] for r in precision]
    baseline=[original_scouts[v(r)]["dps_mean"] for r in precision]
    baseline_rmse=rmse(baseline,holdout_truth)
    training=[r for r in scouts if v(r) not in heldout]
    need(len(training)==9858,"V312_HOLDOUT_ORIGINAL35_NOT_REMOVED")
    ordered=spatial_interleaved_pool(training)
    results=[]
    for budget in (128,256,400,800,1200):
        prefix=ordered[:budget]
        rec=tuple((v(r),float(r["dps_mean"]),float(r["dps_sem"]))
                  for r in prefix)
        fitted=model._fit(rec,3400)
        pred=[model._predict(fitted,v(r),3400) for r in precision]
        scores=sorted(range(48),key=lambda i:(-pred[i],v(precision[i])))
        top1=next(i for i,r in enumerate(precision)
                  if r["dps_mean"]==max(holdout_truth))
        results.append({
            "native_history_scouts_available_for_model":budget,
            "precision_holdout_rmse_dps":round(rmse(pred,holdout_truth),3),
            "best_real_320_candidate_in_model_top8_of48":top1 in scores[:8],
            "absolute_error_on_actual_320_best":round(
                abs(pred[top1]-holdout_truth[top1]),3),
            "original_320_precision_holdout_rows":48,
            "model_predictions_are_not_simc_native":True})
    evidence={
        "schema":SCHEMA,"status":"OFFLINE_HISTORIC_MODEL_SCREEN_PASS",
        "source_profile_sha256":PROFILE,
        "simc_binary_sha256":BINARY,
        "revision":REVISION,
        "verified_existing_native_calls":[2800,2185,4969],
        "verified_historical_journal_sha256":[item[3] for item in cohorts],
        "total_unique_real_scouts_35":9906,
        "original_precision_320_holdout":48,
        "excluded_holdout_scouts_from_training":48,
        "scout35_direct_vs_precision320_rmse_dps":round(baseline_rmse,3),
        "result_by_training_budget":results,
        "new_real_native_executed":0,
        "source_effects_reimplemented":False,
        "proves_better_optimizer_than_v290":False,
        "proves_global_optimum":False,
        "proves_familywise_95":False,
        "note":"Source-attested compact historical cohorts; original full Native JSON2 checked in original runs; offline model ranking is not an accepted Native or 95% result",
    }
    destination=pathlib.Path(args.output)
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(
        evidence,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V312_EXISTING_REAL_9906_MODEL_HOLDOUT_PASS",
          json.dumps({"scout35_direct_rmse":baseline_rmse,
            "fit_rmse_by_budget":{r[
              "native_history_scouts_available_for_model"]:
              r["precision_holdout_rmse_dps"] for r in results}},
              sort_keys=True),flush=True)
    return evidence


if __name__=="__main__":
    main()
