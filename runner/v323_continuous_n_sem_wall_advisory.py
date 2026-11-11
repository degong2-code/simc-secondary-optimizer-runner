#!/usr/bin/env python3
"""IDEA-001: choose bounded integer N from actual SEM and same-host wall.

Offline planner only. No new v291 SimC phase or product-default change.
"""
from __future__ import annotations
import math
SCHEMA="v323_continuous_candidate_n_sem_wall_advisory_v1"
Z95=1.959963984540054
class NPlanBlocked(ValueError): pass
def need(ok,why):
    if not ok: raise NPlanBlocked("V323_"+why)
def projected_sem(sem,samples,n):
    need(type(samples) is int and samples>=2 and type(n) is int and n>=3
         and type(sem) in (int,float) and math.isfinite(sem) and sem>=0,
         "MEASURED_SEM_SAMPLES_REQUIRED")
    return sem*math.sqrt(samples/(n-1))
def fit_wall(rows):
    need(type(rows) is list and len(rows)>=6,"AT_LEAST_SIX_REAL_WALL_POINTS")
    points=[]
    for r in rows:
        need(type(r) is dict and type(r.get("iterations")) is int
             and 3<=r["iterations"]<=100000
             and type(r.get("wall_seconds")) in (int,float)
             and math.isfinite(r["wall_seconds"]) and r["wall_seconds"]>0,
             "POSITIVE_SAME_HOST_NATIVE_WALL_REQUIRED")
        points.append((r["iterations"],float(r["wall_seconds"])))
    need(len({a for a,b in points})>=3,"THREE_DISTINCT_N_REQUIRED")
    x=sum(a for a,b in points)/len(points)
    y=sum(b for a,b in points)/len(points)
    den=sum((a-x)**2 for a,b in points)
    need(den>0,"NONDEGENERATE_N_REQUIRED")
    slope=sum((a-x)*(b-y) for a,b in points)/den
    intercept=y-slope*x
    need(slope>0,"MEASURED_WALL_NONINCREASING")
    return {"schema":SCHEMA,"real_wall_points":len(points),
            "same_host_same_profile_precondition":True,
            "slope_seconds_per_iteration":slope,
            "intercept_seconds":intercept,
            "intercept_may_be_noisy":True}
def recommend(candidate,reference,*,min_n=16,max_n=640,step=8,
              cost=None,wall_cap=None):
    for row in (candidate,reference):
        need(type(row) is dict
             and type(row.get("iterations")) is int and row["iterations"]>=3
             and type(row.get("samples")) is int
             and 2<=row["samples"]<=row["iterations"]
             and all(type(row.get(k)) in (float,int)
                     and math.isfinite(row[k]) and row[k]>=0
                     for k in ("dps_mean","dps_sem")),
             "MEASURED_DPS_AND_SEM_REQUIRED")
    need(type(min_n) is int and type(max_n) is int and type(step) is int
         and 3<=min_n<max_n<=100000 and step>=1,
         "VALID_INTEGER_N_BOUNDS")
    need(wall_cap is None or (type(wall_cap) in (float,int)
         and math.isfinite(wall_cap) and wall_cap>0
         and type(cost) is dict and "slope_seconds_per_iteration" in cost),
         "WALL_CAP_NEEDS_EMPIRICAL_SAME_HOST_MODEL")
    choices=[n for n in range(min_n,max_n+1,step)
             if wall_cap is None or
             max(0.0,cost["intercept_seconds"]+
                 cost["slope_seconds_per_iteration"]*n)<=wall_cap]
    need(bool(choices),"NO_N_WITHIN_WALL_CAP")
    delta=abs(candidate["dps_mean"]-reference["dps_mean"])
    # Reference SEM is an irreducible floor unless reference is also rerun.
    denom=(delta/Z95)**2-reference["dps_sem"]**2
    if delta==0 or denom<=0:
        estimate=None
        status="CANNOT_RESOLVE_WITH_CANDIDATE_N_ALONE"
    else:
        required=1+math.ceil(
            candidate["samples"]*candidate["dps_sem"]**2/denom)
        feasible=[n for n in choices if n>=required]
        estimate=min(feasible) if feasible else None
        status=("PROJECTED_N_FOR_NOMINAL_GAP" if feasible else
                "N_REQUIRED_EXCEEDS_BUDGET")
    return {"schema":SCHEMA,"status":status,
            "next_direct_N_suggestion":estimate,
            "feasible_highest_N":choices[-1],
            "projected_SEM_at_feasible_highest_N":projected_sem(
                candidate["dps_sem"],candidate["samples"],choices[-1]),
            "observed_absolute_DPS_gap":delta,
            "reference_SEM_floor":reference["dps_sem"],
            "fixed_35_120_320_tiers_required":False,
            "v291_typed_35_320_unchanged":True,
            "only_screening_heuristic_not_familywise_95":True,
            "global_optimum_proven":False}
