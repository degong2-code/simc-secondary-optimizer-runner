#!/usr/bin/env python3
"""v311 opt-in NEW-ONLY 50->100% level21 finite-grid SimC planning.

First two historical cohorts are attested by immutable v308 source Native
checkpoint SHA through v310, third v310 first50 cohort separately verified
against its raw v291 journal/Native input/JSON2/receipt with exact source seals.
Historical records are NOT imported as active v291 exact caches; only the
remaining 9,906 35-iteration 21-grid vectors and 16 confirmations execute.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import zipfile
from functools import lru_cache

import v290_multiscale_adaptive_policy as base
import v308_dense_native_checkpoint as raw_checkpoint
import v309_prior_anchored_level21_progressive as geometric
import v310_external_frontier_50_only as previous

SCHEMA="v311_source_anchored_50_to_100_new_only_v1"
METADATA=("frontier100_stage","level21_new_cursor","target_fraction")
SURVEY="new_only_50_to_100_scout"
CONFIRM="new_only_100_confirm"
FRONTIER_SCHEMA="v311_original11_25_50_source_proof_paths_v1"


class FrontierBlocked(ValueError):
    pass


def need(ok,reason):
    if not ok:
        raise FrontierBlocked(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def _vector(row):
    return tuple(base.legacy.key(row["target"]))


@lru_cache(maxsize=4)
def geometry(total,lower,upper):
    p=geometric.geometry(total,tuple(lower),tuple(upper))
    start,end=p["new_counts"][1:]
    need(start<end and end==p["new_only_count"] and
         p["size_old"]+start==p["milestone_targets"][1] and
         p["size_old"]+end==p["size_fine"],
         "V311_SOURCE_ANCHORED_100_GEOMETRY")
    return {
        "total":total,"lower":tuple(lower),"upper":tuple(upper),
        "source11":p["size_old"],"source25":p["new_counts"][0],
        "source50":start-p["new_counts"][0],
        "source_unique":p["size_old"]+start,
        "new_100_count":end-start,"new_total":p["size_fine"],
        "from_cursor":start,"to_cursor":end,
        "targets":p["new"][start:end],
        "calls":end-start+16,
        "scout_iters_required_from_source":True,
    }


def next_plan(observations, *, total,lower,upper,max_native_calls,
              scout_iterations,confirmation_iterations):
    geo=geometry(total,tuple(lower),tuple(upper))
    need(type(observations) is list and
         type(max_native_calls) is int and
         max_native_calls==geo["calls"] and
         type(scout_iterations) is int and
         type(confirmation_iterations) is int and
         1<=scout_iterations<confirmation_iterations,
         "V311_EXACT_NEW_ONLY_100_CALLS_AND_ITERATIONS")
    idx=len(observations)
    if idx>=max_native_calls:
        return {"schema":SCHEMA,"status":"BUDGET_EXHAUSTED",
                "next_request":None,"global_optimum_proven":False}
    if idx<geo["new_100_count"]:
        vector=geo["targets"][idx]
        stage,cursor=SURVEY,geo["from_cursor"]+idx
        phase,iterations="scout",scout_iterations
        decision="V311_UNSEEN_21_GRID_LAST_HALF"
    else:
        confirmed={_vector(r) for r in observations
                   if r["frontier100_stage"]==CONFIRM}
        candidates=sorted(
            (r for r in observations if r["frontier100_stage"]==SURVEY),
            key=lambda r:(-(r["dps_mean"]-.5*r["dps_sem"]),_vector(r)))
        candidate=next((r for r in candidates if _vector(r) not in confirmed),
                       None)
        need(candidate is not None,"V311_UNSEEN_CONFIRM_CANDIDATE_MISSING")
        vector=_vector(candidate)
        stage,cursor=CONFIRM,None
        phase,iterations="precision",confirmation_iterations
        decision="V311_NEW_ONLY_FINAL_100_CONFIRM"
    return {"schema":SCHEMA,"status":"NEXT_NATIVE_PROPOSED",
            "decision":decision,
            "next_request":{
                "phase":phase,"target":base.legacy.to_target(vector),
                "iterations":iterations,"frontier100_stage":stage,
                "level21_new_cursor":cursor,"target_fraction":100},
            "global_optimum_proven":False}


def audit_recorded_history(rows, *, total,lower,upper,max_native_calls,
                           scout_iterations,confirmation_iterations):
    geo=geometry(total,tuple(lower),tuple(upper))
    need(type(rows) is list and len(rows)<=geo["calls"] and
         max_native_calls==geo["calls"],"V311_COMMITTED_BUDGET_DRIFT")
    seen,confirmed=set(),set()
    for idx,row in enumerate(rows):
        v=_vector(row)
        need(all(k in row for k in METADATA) and
             row["target_fraction"]==100 and
             base.legacy.eligible(v,total,lower,upper),
             "V311_COMMITTED_METADATA_DRIFT")
        if idx<geo["new_100_count"]:
            need(row["frontier100_stage"]==SURVEY and
                 row["level21_new_cursor"]==geo["from_cursor"]+idx and
                 row["phase"]=="scout" and
                 row["iterations"]==scout_iterations and
                 v==geo["targets"][idx] and v not in seen,
                 "V311_SCOUT_CURSOR_OR_TARGET_DRIFT")
            seen.add(v)
        else:
            need(row["frontier100_stage"]==CONFIRM and
                 row["level21_new_cursor"] is None and
                 row["phase"]=="precision" and
                 row["iterations"]==confirmation_iterations and
                 v in seen and v not in confirmed,
                 "V311_NEW_100_CONFIRM_DRIFT")
            confirmed.add(v)
    return {"newly_observed_unique":len(seen),
            "newly_confirmed_unique":len(confirmed),
            "historical_native_imported_into_active_cache":False}


def coverage(rows, *, total,lower,upper,prior):
    geo=geometry(total,tuple(lower),tuple(upper))
    need(prior["source_total_unique"]==geo["source_unique"],
         "V311_TRIPLE_SOURCE_FRONTIER_REQUIRED")
    new={_vector(r) for r in rows if r["frontier100_stage"]==SURVEY}
    checked={_vector(r) for r in rows if r["frontier100_stage"]==CONFIRM}
    need(new.issubset(set(geo["targets"])) and
         checked.issubset(new),"V311_OBSERVED_COORDINATES_OUTSIDE_FRONTIER")
    return {"schema":SCHEMA,
            "finite_level21_targets":geo["new_total"],
            "prior11_unique":geo["source11"],
            "prior25_increment_unique":geo["source25"],
            "prior50_increment_unique":geo["source50"],
            "previously_observed_total":geo["source_unique"],
            "new_100_scouts":len(new),
            "combined_observed":geo["source_unique"]+len(new),
            "remaining_unobserved":geo["new_total"]-geo["source_unique"]-len(new),
            "complete_at_level21":len(new)==geo["new_100_count"],
            "new_precision_confirmations":len(checked),
            "historical_native_same_session_cache_verified":False,
            "familywise_95_proven":False,
            "global_optimum_proven":False}


def load_three_original_sources(manifest):
    manifest=pathlib.Path(manifest).resolve(strict=True)
    doc=json.loads(manifest.read_text(encoding="utf8"))
    required={"schema","first50_manifest",
              "third50_receipt","third50_compact_journal",
              "third50_raw_zip","third50_raw_sha256"}
    need(type(doc) is dict and set(doc)==required and
         doc["schema"]==FRONTIER_SCHEMA,
         "V311_STRICT_THREE_SOURCE_MANIFEST")
    older=previous.load_frontier(doc["first50_manifest"])
    checked=raw_checkpoint.verify_checkpoint(
        doc["third50_raw_zip"],doc["third50_raw_sha256"])
    receipt=json.loads(pathlib.Path(
        doc["third50_receipt"]).read_text(encoding="utf8"))
    original_journal=pathlib.Path(
        doc["third50_compact_journal"]).read_bytes()
    need(digest(original_journal)==receipt["new_compact_journal_sha256"],
         "V311_THIRD_SOURCE_ACCEPTED_COMPACT_SHA_DRIFT")
    with zipfile.ZipFile(doc["third50_raw_zip"]) as z:
        need(z.read("V291_JOURNAL.jsonl")==original_journal,
             "V311_THIRD_SOURCE_RAW_COMPACT_DISAGREE")
        seal=json.loads(z.read("V291_SESSION.json"))
    rows=[json.loads(r) for r in original_journal.splitlines()]
    geo=geometry(older["B"],older["lower"],older["upper"])
    need(len(rows)==receipt["new_compact_journal_rows"]==
         checked["committed_cases"]==4969 and
         receipt["status"]=="PASS_V310_REAL_21GRID_50PCT_NEW_ONLY" and
         receipt["new_dps_native"]==4969 and
         receipt["same_job_cache_only_replay_new_native"]==0 and
         receipt["new_source_profile_sha256"]==
             older["source_profile_sha256"]==
             seal["context"]["source_profile_sha256"] and
         receipt["new_simc_binary_sha256"]==
             older["binary_sha256"]==
             seal["context"]["binary_sha256"] and
         seal["context"]["revision"]==older["revision"] and
         receipt["source_build"]==older["season_build"] and
         seal["B"]==older["B"] and
         tuple(base.legacy.key(seal["lower"]))==older["lower"] and
         tuple(base.legacy.key(seal["upper"]))==older["upper"] and
         seal["scout_iterations"]==older["scout_iterations"] and
         seal["confirm_iterations"]==older["confirm_iterations"] and
         seal["experimental_external_frontier50"][
             "verified_historical_frontier"]["old25_raw_archive_sha256"]==
             older["old25_raw_archive_sha256"],
         "V311_THIRD_SOURCE_COMPLETE_NATIVE_SEAL_OR_PROFILE_DRIFT")
    a=previous.audit_recorded_history(
        rows,total=older["B"],lower=older["lower"],upper=older["upper"],
        max_native_calls=4969,
        scout_iterations=older["scout_iterations"],
        confirmation_iterations=older["confirm_iterations"])
    need(a["new_scouts_authenticated_in_current_session"]==
         geo["source50"] and
         a["new_confirms_authenticated_in_current_session"]==16 and
         receipt["frontier_coverage"]["combined_observed"]==
         geo["source_unique"] and
         receipt["frontier_coverage"]["remaining_unmeasured"]==
         geo["new_100_count"],
         "V311_HALF_LEVEL21_COVERAGE_NOT_PROVEN")
    best=list(older["old_best_confirmed"] for _ in range(1))
    best.extend({"target":r["target"],"dps_mean":r["dps_mean"],
                 "dps_sem":r["dps_sem"],"iterations":r["iterations"],
                 "native_sha256":r["native_sha256"]}
                for r in rows if r["phase"]=="precision")
    highest=max(best,key=lambda r:r["dps_mean"])
    return {
        "schema":"v311_external_verified_three_source_frontier_v1",
        "first11_raw_sha256":older["old11_raw_archive_sha256"],
        "first25_raw_sha256":older["old25_raw_archive_sha256"],
        "third50_raw_sha256":checked["archive_sha256"],
        "first11_compact_sha256":older["old11_compact_sha256"],
        "first25_compact_sha256":older["old25_compact_sha256"],
        "third50_compact_sha256":digest(original_journal),
        "source_profile_sha256":older["source_profile_sha256"],
        "binary_sha256":older["binary_sha256"],
        "revision":older["revision"],
        "season_build":older["season_build"],
        "B":older["B"],"lower":older["lower"],"upper":older["upper"],
        "scout_iterations":older["scout_iterations"],
        "confirm_iterations":older["confirm_iterations"],
        "source_total_unique":geo["source_unique"],
        "expected_new_100_calls":geo["calls"],
        "highest_historical_confirmed":highest,
        "previous_original_native_in_each_run_reauthenticated":True,
        "cross_run_import_as_exact_active_native_cache":False,
    }
