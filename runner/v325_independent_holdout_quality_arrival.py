#!/usr/bin/env python3
"""v325: held-out candidate-screening success vs NEW real Native iteration budget.

Pure read-only analysis. 12 CHMV from this NEW source-first campaign only;
an independent 2x640 Native reference is an imperfect benchmark, NOT truth,
95% equivalence or the global optimum. The 0.5% DPS band is predeclared.
"""
from __future__ import annotations
import math
import statistics

SCHEMA="v325_independent_holdout_ranking_arrival_by_N_v1"
STATS=("crit_rating","haste_rating","mastery_rating","versatility_rating")
GRID=(24,48,96,192)
HOLDOUT_N=640
REPS=(0,1)
QUALITY_BAND=0.005
BUDGETS_SECONDS=(2,4,8,12)

class ReplayBlocked(ValueError):pass
def need(ok,reason):
    if not ok: raise ReplayBlocked("V325_"+reason)
def key(chmv):
    need(type(chmv) is dict and set(chmv)==set(STATS)
         and all(type(chmv[x]) is int and chmv[x]>=0 for x in STATS),
         "SOURCE_CHMV_EXACT_REQUIRED")
    return tuple(chmv[x] for x in STATS)

def evaluate(candidates, observations, *, band=QUALITY_BAND,
             grid=GRID, holdout_n=HOLDOUT_N,
             screen_reps=REPS, holdout_reps=REPS):
    need(type(candidates) is list and len(candidates)==12
         and all(type(x) is dict for x in candidates)
         and type(observations) is list
         and type(band) in (float,int) and 0<band<0.05
         and tuple(grid) in (GRID,(32,48,64,96))
         and holdout_n==HOLDOUT_N
         and tuple(screen_reps) in (REPS,(0,1,2))
         and tuple(holdout_reps)==REPS,
         "PRECOMMITTED_NEW_USER_COHORT_REQUIRED")
    order=[key(c) for c in candidates]
    need(len(set(order))==len(order) and
         len({sum(x) for x in order})==1,
         "UNIQUE_SAME_BUDGET_CHMV_REQUIRED")
    grid=tuple(grid)
    screen_reps=tuple(screen_reps)
    holdout_reps=tuple(holdout_reps)
    table={}
    for row in observations:
        need(type(row) is dict
             and row.get("n") in grid+(holdout_n,)
             and type(row.get("rep")) is int
             and row["rep"] in (holdout_reps if row["n"]==holdout_n
                                else screen_reps)
             and type(row.get("samples")) is int
             and row["samples"]==row["n"]-1
             and all(type(row.get(f)) in (int,float)
                     and math.isfinite(row[f]) and row[f]>0
                     for f in ("dps","sem","wall_seconds"))
             and type(row.get("seed")) is int
             and type(row.get("native_sha256")) is str
             and len(row["native_sha256"])==64,
             "ACTUAL_INDEPENDENT_NATIVE_SAMPLE_REQUIRED")
        v=key(row.get("CHMV"))
        need(v in order,"UNSELECTED_CHMV_NATIVE_NOT_ALLOWED")
        ident=(v,row["n"],row["rep"])
        need(ident not in table,"DUPLICATE_EXACT_RESEARCH_IDENTITY")
        table[ident]=row
    expected={(v,n,r) for v in order for n in grid+(holdout_n,)
              for r in (holdout_reps if n==holdout_n else screen_reps)}
    need(set(table)==expected and
         len({x["seed"] for x in table.values()})==len(table),
         "COMPLETE_DISTINCT_NATIVE_SEEDS_AND_ALL_TARGET_N_REQUIRED")
    held={}
    for v in order:
        a,b=(table[(v,holdout_n,r)] for r in holdout_reps)
        held[v]={"mean":(a["dps"]+b["dps"])/2,
                 "independent_sem":math.hypot(a["sem"],b["sem"])/2}
    best=max(x["mean"] for x in held.values())
    threshold=best*(1-band)
    good={v for v in order if held[v]["mean"]>=threshold}
    need(bool(good),"REFERENCE_BAND_EMPTY")
    out={}
    for n in grid:
        runs=[]
        for rep in screen_reps:
            prefix=[]
            elapsed=0.
            history=[]
            for i,v in enumerate(order):
                x=table[(v,n,rep)]
                elapsed+=x["wall_seconds"]
                prefix.append((v,x))
                selected=max(prefix,key=lambda kv:(kv[1]["dps"],
                                                  -order.index(kv[0])))[0]
                passed=selected in good
                leader={"rank":i+1,"selected_CHMV":list(selected),
                        "quality_reference_fraction":
                           held[selected]["mean"]/best,
                        "heldout_reference_mean_dps":held[selected]["mean"],
                        "cumulative_iterations":(i+1)*n,
                        "cumulative_process_wall_seconds":round(elapsed,6),
                        "reference_good_band":passed}
                history.append(leader)
            hits=[h for h in history if h["reference_good_band"]]
            first_good=hits[0] if hits else None
            stable=next((history[k] for k in range(len(history))
                        if all(h["reference_good_band"] for h in history[k:])),
                        None)
            by_budget={}
            for budget in BUDGETS_SECONDS:
                within=[h for h in history
                        if h["cumulative_process_wall_seconds"]<=budget]
                by_budget[str(budget)]=(
                    within[-1]["reference_good_band"] if within else None)
            runs.append({
                "rep":rep,
                "final_selected":history[-1],
                "first_good_selected":first_good,
                "first_persistent_good_selected":stable,
                "prefixes_good_fraction":sum(h["reference_good_band"]
                                             for h in history)/len(history),
                "end_to_end_screen_wall_seconds":history[-1][
                    "cumulative_process_wall_seconds"],
                "screen_iterations":n*len(order),
                "good_at_wall_budget":by_budget,
            })
        out[str(n)]={
            "screen_runs":runs,
            "final_holdout_regret_pct_by_rep":[
                100*(1-x["final_selected"]["quality_reference_fraction"])
                for x in runs],
            "median_final_holdout_regret_pct":statistics.median(
                100*(1-x["final_selected"]["quality_reference_fraction"])
                for x in runs),
            "two_independent_screen_replicates":(runs if len(screen_reps)==2 else None),
            "final_success_fraction":sum(
                x["final_selected"]["reference_good_band"] for x in runs)/len(runs),
            "median_end_to_end_screen_wall_seconds":statistics.median(
                x["end_to_end_screen_wall_seconds"] for x in runs),
            "first_persistent_good_count":sum(
                x["first_persistent_good_selected"] is not None for x in runs)}
    return {
        "schema":SCHEMA,"source_user_candidates":len(order),
        "screen_repetitions":len(screen_reps),
        "actual_independent_Native":len(table),
        "same_current_profile_required":True,
        "quality_band_fraction":band,
        "quality_band_is_operational_not_95_equivalence":True,
        "holdout_N":holdout_n,
        "holdout_replicates":len(holdout_reps),
        "holdout_best_of_only_12_CHMV_dps":best,
        "heldout_good_candidate_count":len(good),
        "first_candidate_already_near_quality":order[0] in good,
        "first_arrival_metric_has_trivial_good_first_candidate":order[0] in good,
        "holdout_selected_best_is_global_optimum":False,
        "raw_holdout":{"/".join(map(str,v)):held[v] for v in order},
        "by_N":out}
