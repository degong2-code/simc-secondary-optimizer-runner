#!/usr/bin/env python3
"""IDEA-001: verified journal time-to-CHMV metric; NOT noisy peak DPS ranking.

Reference is a post-hoc observed CHMV, never a proven global optimum.
Do not combine distinct SimC run hosts or resumed process clocks.
"""
from __future__ import annotations
import math
SCHEMA="v322_first_chmv_arrival_original_trace_v1"
STATS=("crit_rating","haste_rating","mastery_rating","versatility_rating")
class ArrivalBlocked(ValueError): pass
def need(ok, reason):
    if not ok: raise ArrivalBlocked("V322_"+reason)
def vector(row):
    x=row["target"]
    need(type(x) is dict and set(x)==set(STATS)
         and all(type(x[k]) is int and x[k]>=0 for k in STATS),
         "TARGET_CHMV_INVALID")
    return tuple(x[k] for k in STATS)
def distance(x,y):
    return sum(abs(a-b) for a,b in zip(x,y))
def evaluate(journal,trace,reference,*,tolerance=2,confirm_iterations=320):
    need(type(journal) is list and bool(journal) and type(trace) is list
         and type(reference) is dict and set(reference)==set(STATS)
         and type(tolerance) is int and tolerance>=0
         and type(confirm_iterations) is int and confirm_iterations>0,
         "SOURCE_JOURNAL_REFERENCE_REQUIRED")
    ref=vector({"target":reference})
    cumul=0;iterations=[]
    for i,r in enumerate(journal):
        need(type(r) is dict and r.get("index")==i
             and type(r.get("iterations")) is int and r["iterations"]>0
             and r.get("phase") in ("scout","precision")
             and r.get("source")=="NEW_NATIVE"
             and type(r.get("dps_mean")) in (float,int)
             and type(r.get("dps_sem")) in (float,int)
             and math.isfinite(r["dps_mean"]) and math.isfinite(r["dps_sem"])
             and r["dps_sem"]>=0, "EXACT_NATIVE_JOURNAL_REQUIRED")
        vector(r)
        cumul+=r["iterations"]
        iterations.append(cumul)
    complete=(len(trace)==len(journal)
              and [r.get("index") for r in trace]==list(range(len(journal)))
              and len({r.get("invocation_id") for r in trace})==1
              and all(t.get("source")=="NEW_NATIVE"
                      and t.get("case_key")==r.get("case_key")
                      and t.get("native_sha256")==r.get("native_sha256")
                      and t.get("iterations")==r.get("iterations")
                      for t,r in zip(trace,journal))
              and all(type(t.get("invocation_elapsed_seconds")) in (int,float)
                      and math.isfinite(t["invocation_elapsed_seconds"])
                      and t["invocation_elapsed_seconds"]>=0 for t in trace)
              and all(a["invocation_elapsed_seconds"]<=b["invocation_elapsed_seconds"]
                      for a,b in zip(trace,trace[1:])))
    def hit(phase, threshold):
        found=[r for r in journal if r["phase"]==phase
               and (phase!="precision" or r["iterations"]==confirm_iterations)
               and distance(vector(r),ref)<=threshold]
        if not found: return None
        row=found[0];i=row["index"]
        return {"index_0_based":i,"cases_completed":i+1,
                "iterations_through_hit":iterations[i],
                "wall_seconds":(round(trace[i]["invocation_elapsed_seconds"],6)
                                if complete else None),
                "CHMV":dict(row["target"]),
                "L1_rating_distance":distance(vector(row),ref),
                "DPS_observed":row["dps_mean"],"SEM_observed":row["dps_sem"]}
    return {"schema":SCHEMA,"reference_posthoc_CHMV":dict(reference),
            "reference_global_optimum_proven":False,
            "one_process_original_trace":complete,
            "near_L1_rating_tolerance":tolerance,
            "near_not_a_DPS_equivalence_proof":True,
            "total_native_iterations":cumul,
            "exact":{"scout":hit("scout",0),"confirm":hit("precision",0)},
            "near":{"scout":hit("scout",tolerance),
                    "confirm":hit("precision",tolerance)}}
