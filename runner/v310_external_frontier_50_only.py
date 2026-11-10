#!/usr/bin/env python3
"""v310 opt-in: NEW level21 frontier 25->50, never resimulate old 11 or 25.

Two independent historical source-verified Native corpuses (original11 +
v309 first25) are verified from exact pinned raw checkpoint+compact bytes.
Their coordinates are EXCLUDED, not transplanted as current-session v291 cache.
Run 4,953 NEW 35-iteration scouts + 16 NEW 320-iteration confirmations.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import zipfile
from functools import lru_cache

import v290_multiscale_adaptive_policy as base
import v308_dense_native_checkpoint as raw_checkpoint
import v309_prior_anchored_level21_progressive as previous

SCHEMA="v310_sha_anchored_new21_25_to_50_experiment_v1"
METADATA=("frontier_stage","new21_cursor","target_fraction")
SURVEY="new_only_25_to_50_scout"
CONFIRM="new_only_50_confirm"
FRACTION=50
COMPACT_SCHEMA="v310_original11_plus_25_proof_paths_v1"


class FrontierBlocked(ValueError):
    pass


def need(ok,code):
    if not ok:
        raise FrontierBlocked(code)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def _vec(row):
    return tuple(base.legacy.key(row["target"]))


@lru_cache(maxsize=4)
def geometry(total,lower,upper):
    p=previous.geometry(total,lower,upper)
    start,end=p["new_counts"][:2]
    need(0<start<end<p["new_only_count"] and
         p["size_old"]+end==p["milestone_targets"][1],
         "V310_FRONTIER_25_50_GEOMETRY")
    return {
        "B":total,"lower":tuple(lower),"upper":tuple(upper),
        "old_11":p["size_old"],"original25_new":start,
        "new_50_count":end-start,
        "existing_combined":p["size_old"]+start,
        "combined_50":p["size_old"]+end,
        "level21_total":p["size_fine"],
        "new_targets":p["new"][start:end],
        "native_cap":end-start+16,
        "start_new21_cursor":start,
        "stop_new21_cursor":end,
        "remaining_after_50":p["size_fine"]-(p["size_old"]+end),
    }


def next_plan(rows, *, total,lower,upper,max_native_calls,
              scout_iterations,confirmation_iterations):
    geo=geometry(total,tuple(lower),tuple(upper))
    need(type(rows) is list and type(max_native_calls) is int and
         max_native_calls==geo["native_cap"] and
         type(scout_iterations) is int and
         type(confirmation_iterations) is int and
         1<=scout_iterations<confirmation_iterations,
         "V310_FRONTIER_EXACT_NEW_NATIVE_CAP")
    i=len(rows)
    if i>=max_native_calls:
        return {"schema":SCHEMA,"status":"BUDGET_EXHAUSTED",
                "next_request":None,"global_optimum_proven":False}
    if i<geo["new_50_count"]:
        stage,cursor=SURVEY,geo["start_new21_cursor"]+i
        vector=geo["new_targets"][i]
        phase,iters="scout",scout_iterations
        reason="V310_NEW21_25_TO_50_UNSEEN_SURVEY"
    else:
        stage,cursor=CONFIRM,None
        prior={_vec(row) for row in rows
               if row["frontier_stage"]==CONFIRM}
        ranked=sorted(
            (r for r in rows if r["frontier_stage"]==SURVEY),
            key=lambda r:(-(r["dps_mean"]-.5*r["dps_sem"]),_vec(r)))
        best=next((r for r in ranked if _vec(r) not in prior),None)
        need(best is not None,"V310_NEW_CONFIRMED_TARGET_UNAVAILABLE")
        vector=_vec(best)
        phase,iters="precision",confirmation_iterations
        reason="V310_NEW_ONLY_50_MILESTONE_CONFIRM"
    return {"schema":SCHEMA,"status":"NEXT_NATIVE_PROPOSED",
            "decision":reason,
            "next_request":{
                "phase":phase,"target":base.legacy.to_target(vector),
                "iterations":iters,"frontier_stage":stage,
                "new21_cursor":cursor,"target_fraction":FRACTION},
            "global_optimum_proven":False}


def audit_recorded_history(rows, *, total,lower,upper,max_native_calls,
                           scout_iterations,confirmation_iterations):
    geo=geometry(total,tuple(lower),tuple(upper))
    need(type(rows) is list and len(rows)<=geo["native_cap"] and
         max_native_calls==geo["native_cap"],
         "V310_RECORDED_FRONTIER_BUDGET")
    seen,confirmed=set(),set()
    for i,row in enumerate(rows):
        vec=_vec(row)
        need(all(k in row for k in METADATA) and
             row["target_fraction"]==50 and
             base.legacy.eligible(vec,total,lower,upper),
             "V310_RECORDED_FRONTIER_FIELDS")
        if i<geo["new_50_count"]:
            need(row["frontier_stage"]==SURVEY and
                 row["new21_cursor"]==geo["start_new21_cursor"]+i and
                 row["iterations"]==scout_iterations and
                 row["phase"]=="scout" and
                 vec==geo["new_targets"][i] and vec not in seen,
                 "V310_RECORDED_NEW21_CURSOR_OR_REPEATED_CASE")
            seen.add(vec)
        else:
            need(row["frontier_stage"]==CONFIRM and
                 row["new21_cursor"] is None and
                 row["iterations"]==confirmation_iterations and
                 row["phase"]=="precision" and
                 vec in seen and vec not in confirmed,
                 "V310_RECORDED_50_CONFIRM_DRIFT")
            confirmed.add(vec)
    return {"new_scouts_authenticated_in_current_session":len(seen),
            "new_confirms_authenticated_in_current_session":len(confirmed),
            "old_cases_not_imported_as_exact_current_cache":True}


def coverage(rows, *,total,lower,upper,frontier):
    geo=geometry(total,tuple(lower),tuple(upper))
    need(frontier["prior_total_scouts"]==geo["existing_combined"],
         "V310_25_PERCENT_PROOFS_REQUIRED")
    scouts={_vec(r) for r in rows if r["frontier_stage"]==SURVEY}
    confirms={_vec(r) for r in rows if r["frontier_stage"]==CONFIRM}
    need(scouts.issubset(set(geo["new_targets"])),
         "V310_NEW_SCOUTS_OUTSIDE_UNSEEN_FRONTIER")
    return {"schema":SCHEMA,
            "finite_21_grid_total":geo["level21_total"],
            "origin11_source_verified_scouts":geo["old_11"],
            "origin25_source_verified_scouts":geo["original25_new"],
            "already_observed_historical_scouts":geo["existing_combined"],
            "new50_scouts_this_native_session":len(scouts),
            "combined_observed":geo["existing_combined"]+len(scouts),
            "remaining_unmeasured":geo["level21_total"]-
                geo["existing_combined"]-len(scouts),
            "new50_precision_confirmations":len(confirms),
            "target_50_scouts":geo["combined_50"],
            "historical_scouts_exact_current_native_cache":False,
            "global_optimum_proven":False,
            "familywise_95_proven":False}


def load_frontier(manifest):
    """Require BOTH fully SHA-verified source corpuses, no current cache claims."""
    manifest=pathlib.Path(manifest).resolve(strict=True)
    m=json.loads(manifest.read_text())
    required={"schema","original11_compact_zip","original11_raw_zip",
              "original11_sha256","prior25_receipt","prior25_compact_journal",
              "prior25_raw_zip","prior25_sha256"}
    need(type(m) is dict and set(m)==required and
         m["schema"]==COMPACT_SCHEMA,
         "V310_STRICT_ORIGINAL_FRONTIER_MANIFEST_REQUIRED")
    old=previous.load_original_prior(
        m["original11_compact_zip"],m["original11_raw_zip"],
        m["original11_sha256"])
    proof=raw_checkpoint.verify_checkpoint(
        m["prior25_raw_zip"],m["prior25_sha256"])
    receipt=json.loads(pathlib.Path(m["prior25_receipt"]).read_text())
    raw=pathlib.Path(m["prior25_compact_journal"]).read_bytes()
    need(digest(raw)==receipt["new_compact_journal_sha256"],
         "V310_ORIGINAL25_COMPACT_JOURNAL_SHA_DRIFT")
    with zipfile.ZipFile(m["prior25_raw_zip"]) as z:
        need(z.read("V291_JOURNAL.jsonl")==raw,
             "V310_ORIGINAL25_RAW_COMPACT_JOURNAL_DISAGREES")
        seal=json.loads(z.read("V291_SESSION.json"))
    rows=[json.loads(x) for x in raw.splitlines()]
    geo=geometry(old["B"],old["lower"],old["upper"])
    need(len(rows)==receipt["new_compact_journal_rows"]==
         proof["committed_cases"]==2185 and
         receipt["status"]=="PASS_REAL_21_GRID_25_PERCENT_OLD11_ANCHORED" and
         receipt["new_dps_native"]==2185 and
         receipt["cache_only_replay_new_native"]==0 and
         receipt["new_source_profile_sha256"]==
           old["source_profile_sha256"]==
           seal["context"]["source_profile_sha256"] and
         receipt["native_binary_sha256"]==
           old["binary_sha256"]==
           seal["context"]["binary_sha256"] and
         receipt["revision"]==old["revision"] and
         seal["context"]["revision"]==old["revision"] and
         seal["B"]==old["B"] and
         tuple(base.legacy.key(seal["lower"]))==old["lower"] and
         tuple(base.legacy.key(seal["upper"]))==old["upper"] and
         seal["scout_iterations"]==old["scout_iterations"] and
         seal["confirm_iterations"]==old["confirm_iterations"] and
         seal["experimental_prior_anchored_21"]["origin"][
             "raw_archive_sha256"]==old["raw_archive_sha256"],
         "V310_ORIGINAL25_SOURCE_IDENTITY_OR_SCENARIO_DRIFT")
    audited=previous.audit_committed_history(
        rows,total=old["B"],lower=old["lower"],upper=old["upper"],
        max_native_calls=previous.geometry(
            old["B"],old["lower"],old["upper"])["total_calls"],
        scout_iterations=old["scout_iterations"],
        confirmation_iterations=old["confirm_iterations"])
    need(audited["observed_new_unique"]==geo["original25_new"] and
         audited["confirmed_new_unique"]==16 and
         receipt["milestone_coverage"][
             "combined_observed_geometric_coverage"]==
             geo["existing_combined"],
         "V310_25_PERCENT_EXACT_ADDITIONAL_FRONTIER_NOT_AUTHENTICATED")
    candidates=list(old["confirmed_baseline"])+[
        {"target":r["target"],"dps_mean":r["dps_mean"],
         "dps_sem":r["dps_sem"],"iterations":r["iterations"],
         "native_sha256":r["native_sha256"]}
        for r in rows if r["phase"]=="precision"]
    best=max(candidates,key=lambda r:r["dps_mean"])
    return {"schema":"v310_external_sha_attested_first50_frontier_v1",
            "old11_raw_archive_sha256":old["raw_archive_sha256"],
            "old11_compact_sha256":old["original_compact_journal_sha256"],
            "old25_raw_archive_sha256":proof["archive_sha256"],
            "old25_compact_sha256":digest(raw),
            "source_profile_sha256":old["source_profile_sha256"],
            "binary_sha256":old["binary_sha256"],
            "revision":old["revision"],
            "season_build":old["season_build"],
            "B":old["B"],"lower":old["lower"],"upper":old["upper"],
            "scout_iterations":old["scout_iterations"],
            "confirm_iterations":old["confirm_iterations"],
            "prior_total_scouts":geo["existing_combined"],
            "expected_new50_scouts":geo["new_50_count"],
            "expected_new50_native_calls":geo["native_cap"],
            "old_best_confirmed":best,
            "previously_proven_raw_native_in_origin_sessions":True,
            "cross_session_exact_native_case_imported":False}
