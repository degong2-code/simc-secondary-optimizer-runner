#!/usr/bin/env python3
"""v309 opt-in: historical level11 anchor + ONLY NEW level21 integer CHMV.

Prior level11 raw Native cases are an independently source-verified historical
cohort, NOT an exact-case cache of the new v291 runtime identity. They are
excluded geometrically; the new session journal contains only NEW accepted
Native cases. Three sealed milestones each confirm 16 fresh distinct targets:
25%, 50%, 100% of the finite 21-level CHMV lattice. No effect/DPS model.
"""
from __future__ import annotations

import hashlib
import json
import math
import pathlib
import zipfile
from functools import lru_cache

import v290_multiscale_adaptive_policy as base
import v307_dense_nested_coverage_grid as grid
import v308_dense_native_checkpoint as raw_checkpoint

SCHEMA="v309_prior_anchored_level21_progressive_probe_v1"
METADATA=("new_level_stage","new_level_cursor","milestone_fraction")
SURVEY="level21_only_scout"
CONFIRM="milestone_confirm"
FRACTIONS=(25,50,100)
CONFIRM_PER_MILESTONE=16


class PilotBlocked(ValueError):
    pass


def need(ok,reason):
    if not ok:
        raise PilotBlocked(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def _vector(doc):
    return tuple(base.legacy.key(doc["target"]))


@lru_cache(maxsize=6)
def geometry(total,lower,upper):
    lower,upper=grid._params(total,lower,upper,21)
    old=grid.lattice(total,lower,upper,11)
    fine=grid.lattice(total,lower,upper,21)
    fresh=grid.ordered_new_level(total,lower,upper,21)
    need(len(old)+len(fresh)==len(fine) and
         len(old)==len(set(old)) and
         len(fresh)==len(set(fresh)) and
         set(old).isdisjoint(set(fresh)),
         "V309_NESTED_EXACT_GRID_PARTITION_DRIFT")
    targets=tuple(len(fine)*fraction//100 for fraction in FRACTIONS)
    need(targets[2]==len(fine) and targets[0]>len(old) and
         targets[0]<targets[1]<targets[2],
         "V309_MILESTONES_OUTSIDE_NEW21_GRID")
    new_counts=tuple(t-len(old) for t in targets)
    calls=tuple(count+(i+1)*CONFIRM_PER_MILESTONE
                for i,count in enumerate(new_counts))
    return {
        "old":old, "fine":fine, "new":fresh,
        "size_old":len(old),"size_fine":len(fine),
        "new_counts":new_counts,"total_calls":calls[-1],
        "milestone_calls":calls,"milestone_targets":targets,
        "new_only_count":len(fresh),
    }


def milestone_for_index(index,geo):
    need(type(index) is int and 0<=index<geo["total_calls"],
         "V309_INDEX_OUTSIDE_SEALED_CALL_BUDGET")
    previously_scouted=0
    previously_confirmed=0
    for j,goal in enumerate(geo["new_counts"]):
        new_start=previously_scouted+previously_confirmed
        new_count=goal-previously_scouted
        if index<new_start+new_count:
            return SURVEY,previously_scouted+(index-new_start),FRACTIONS[j]
        precision_start=new_start+new_count
        if index<precision_start+CONFIRM_PER_MILESTONE:
            return CONFIRM,None,FRACTIONS[j]
        previously_scouted=goal
        previously_confirmed+=(CONFIRM_PER_MILESTONE)
    raise PilotBlocked("V309_NO_MORE_NEW_CASES")


def _confirmed_vectors(rows):
    return {_vector(r) for r in rows if r["new_level_stage"]==CONFIRM}


def next_plan(observations, *, total,lower,upper,max_native_calls,
              scout_iterations,confirmation_iterations):
    lower,upper=grid._params(total,lower,upper,21)
    geo=geometry(total,lower,upper)
    need(type(observations) is list and
         type(max_native_calls) is int and
         max_native_calls==geo["total_calls"] and
         type(scout_iterations) is int and
         type(confirmation_iterations) is int and
         1<=scout_iterations<confirmation_iterations,
         "V309_EXACT_MILESTONE_BUDGET_OR_ITERATIONS_REQUIRED")
    idx=len(observations)
    if idx>=max_native_calls:
        return {"schema":SCHEMA,"status":"BUDGET_EXHAUSTED",
                "next_request":None,"global_optimum_proven":False}
    stage,cursor,percent=milestone_for_index(idx,geo)
    if stage==SURVEY:
        target=geo["new"][cursor]
        phase,iters="scout",scout_iterations
        reason="V309_NEXT_NEW_LEVEL21_SPATIALLY_INTERLEAVED"
    else:
        # Confirm only newly measured 21-exclusive candidates, NEVER copy or
        # recertify old v307 11-level results under a changed runtime SHA.
        seen=_confirmed_vectors(observations)
        scouts=(r for r in observations
                if r["new_level_stage"]==SURVEY)
        ranked=sorted(scouts,key=lambda r:(
            -(r["dps_mean"]-.5*r["dps_sem"]),_vector(r)))
        chosen=next((r for r in ranked if _vector(r) not in seen),None)
        need(chosen is not None,"V309_NO_NEW_DISTINCT_CONFIRM_TARGET")
        target=_vector(chosen)
        phase,iters="precision",confirmation_iterations
        reason="V309_NEW_ONLY_MILESTONE_TOP_CONFIRMED"
    return {"schema":SCHEMA,"status":"NEXT_NATIVE_PROPOSED",
            "decision":reason,"next_request":{
                "phase":phase,"target":base.legacy.to_target(target),
                "iterations":iters,"new_level_stage":stage,
                "new_level_cursor":cursor,"milestone_fraction":percent},
            "global_optimum_proven":False}


def audit_committed_history(rows, *, total,lower,upper,max_native_calls,
                            scout_iterations,confirmation_iterations):
    geo=geometry(total,tuple(lower),tuple(upper))
    need(type(max_native_calls) is int and
         max_native_calls==geo["total_calls"] and
         type(rows) is list and len(rows)<=max_native_calls,
         "V309_RECORDED_SOURCE_POLICY_BUDGET_DRIFT")
    seen,confirmed=set(),set()
    counts={25:0,50:0,100:0}
    for idx,r in enumerate(rows):
        stage,cursor,percent=milestone_for_index(idx,geo)
        vec=_vector(r)
        need(all(k in r for k in METADATA) and
             r["new_level_stage"]==stage and
             r["new_level_cursor"]==cursor and
             r["milestone_fraction"]==percent and
             base.legacy.eligible(vec,total,lower,upper),
             "V309_RECORDED_SCHEDULE_METADATA_DRIFT")
        if stage==SURVEY:
            need(r["phase"]=="scout" and
                 r["iterations"]==scout_iterations and
                 vec==geo["new"][cursor] and vec not in seen,
                 "V309_RECORDED_NEW21_SCOUT_CURSOR_DRIFT")
            seen.add(vec)
            counts[percent]+=1
        else:
            need(r["phase"]=="precision" and
                 r["iterations"]==confirmation_iterations and
                 vec in seen and vec not in confirmed,
                 "V309_RECORDED_NEW_ONLY_CONFIRM_DRIFT")
            confirmed.add(vec)
    return {"observed_new_unique":len(seen),
            "confirmed_new_unique":len(confirmed),
            "milestone_new_scouts":counts,
            "rows_authenticated_by_v291_separately":True}


def coverage(rows, *,total,lower,upper,prior_count):
    geo=geometry(total,tuple(lower),tuple(upper))
    need(type(prior_count) is int and
         prior_count==geo["size_old"],
         "V309_ORIGINAL_LEVEL11_COMPLETE_ANCHOR_REQUIRED")
    new_scouts={_vector(r) for r in rows
                if r["new_level_stage"]==SURVEY}
    new_confirm={_vector(r) for r in rows
                 if r["new_level_stage"]==CONFIRM}
    need(new_scouts.isdisjoint(set(geo["old"])) and
         new_scouts.issubset(set(geo["new"])),
         "V309_NEW21_OVERLAPS_PRIOR11_OR_OUTSIDE")
    prior=geo["size_old"]
    return {"schema":SCHEMA,
            "finite_level21_total":geo["size_fine"],
            "prior_level11_observed_elsewhere":prior,
            "new_level21_scouts_this_session":len(new_scouts),
            "combined_observed_geometric_coverage":prior+len(new_scouts),
            "combined_unobserved":geo["size_fine"]-prior-len(new_scouts),
            "new_confirmation_vectors":len(new_confirm),
            "milestone_targets":dict(zip(FRACTIONS,geo["milestone_targets"])),
            "milestone_session_call_indices":dict(zip(FRACTIONS,geo["milestone_calls"])),
            "prior_native_source_session_different_from_current":True,
            "prior_cases_not_current_v291_exact_cache":True,
            "familywise_95_proven":False,
            "global_optimum_proven":False}


def load_original_prior(compact_zip,raw_original_zip,expected_raw_sha):
    """Read finite level11 historical evidence without transplanting as cache.

    v308 hashes every ZIP member. Pin the entire original raw ZIP to the prior
    run's independent receipt SHA and the entire compact journal to that same
    original byte-stream. This does NOT replace old v291's real Native proof,
    already demonstrated in original run; cross-runtime native reauthentication
    is intentionally *not* claimed.
    """
    compact_zip=pathlib.Path(compact_zip).resolve(strict=True)
    raw_original_zip=pathlib.Path(raw_original_zip).resolve(strict=True)
    verified=raw_checkpoint.verify_checkpoint(
        raw_original_zip,expected_raw_sha)
    with zipfile.ZipFile(compact_zip) as z:
        need({"receipt.json","all_accepted_compact_cases.jsonl"}<=
             set(z.namelist()),"V309_ORIGINAL_COMPACT_ARTIFACT_FILES")
        receipt=json.loads(z.read("receipt.json"))
        raw=z.read("all_accepted_compact_cases.jsonl")
    need(digest(raw)==receipt["all_compact_cases_sha256"],
         "V309_ORIGINAL_COMPACT_JOURNAL_SHA_DRIFT")
    with zipfile.ZipFile(raw_original_zip) as z:
        need(z.read("V291_JOURNAL.jsonl")==raw,
             "V309_RAW_AND_COMPACT_ORIGINAL_JOURNAL_DISAGREE")
        seal=json.loads(z.read("V291_SESSION.json"))
    rows=[json.loads(x) for x in raw.splitlines()]
    need(len(rows)==receipt["all_compact_cases_count"]==
         verified["committed_cases"]==2800 and
         receipt.get("status")=="PASS_REAL_PRODUCT_FULL_LEVEL11_GRID" and
         receipt["new_dps_native"]==2800 and
         receipt["cache_only_replay_new_native"]==0 and
         receipt["source_profile_sha256"]==
             seal["context"]["source_profile_sha256"] and
         receipt["source_scenario_sha256"]==
             seal["context"]["scenario_digest"] and
         receipt["binary_sha256"]==seal["context"]["binary_sha256"] and
         seal["experimental_dense_nested_grid"]["max_level"]==11 and
         seal["experimental_dense_nested_grid"]["complete_grid_first"],
         "V309_ORIGINAL_SOURCE_NATIVE_OR_LEVEL11_SEAL_DRIFT")
    B=seal["B"]
    lower=tuple(base.legacy.key(seal["lower"]))
    upper=tuple(base.legacy.key(seal["upper"]))
    geo=geometry(B,lower,upper)
    scouts=[r for r in rows if r["phase"]=="scout"]
    unique={_vector(r) for r in scouts}
    need(len(unique)==len(scouts)==geo["size_old"] and
         unique==set(geo["old"]) and
         len([r for r in rows if r["phase"]=="precision"])==16 and
         receipt["coverage"]["levels"]["11"][
             "complete_at_this_resolution"] is True,
         "V309_ORIGINAL_LEVEL11_FULL_COVERAGE_NOT_PROVEN")
    return {"schema":"v309_external_original11_historical_anchor_v1",
            "raw_archive_sha256":expected_raw_sha,
            "original_compact_journal_sha256":digest(raw),
            "source_profile_sha256":receipt["source_profile_sha256"],
            "original_scenario_digest":receipt["source_scenario_sha256"],
            "binary_sha256":receipt["binary_sha256"],
            "revision":receipt["revision"],"season_build":receipt["season_build"],
            "B":B,"lower":lower,"upper":upper,
            "scout_iterations":receipt["scout_iterations"],
            "confirm_iterations":receipt["confirmation_iterations"],
            "confirmed_baseline":tuple(sorted(
                (dict(target=r["target"],dps_mean=r["dps_mean"],
                      dps_sem=r["dps_sem"],iterations=r["iterations"],
                      native_sha256=r["native_sha256"])
                 for r in rows if r["phase"]=="precision"),
                key=lambda r:(-r["dps_mean"],tuple(r["target"].values())))),
            "prior_level11_count":len(unique),
            "verified_origin_zip_member_shas":True,
            "old_original_v291_cache_only_authenticated_in_origin_run":True,
            "cross_runtime_cache_import_authenticated":False}
