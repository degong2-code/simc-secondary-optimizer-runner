#!/usr/bin/env python3
"""v316 opt-in per-native-case wall trace, ONLY original source-bound telemetry.

This is NOT a Native receipt, SimC stopwatch, DPS model, or new cache key.
Recorded after the immutable V291 journal/progress commit; a crash between
commits may leave gaps. Gaps are reported, NEVER reconstructed from averages.
No timestamps from previous process invocations can make a total 5/10-minute
checkpoint without an additional explicit cumulative clock.
"""
from __future__ import annotations
import hashlib
import json
import math
import os
import pathlib

SCHEMA="v316_original_native_case_wall_trace_v1"
NAME="V316_CASE_WALL_TRACE.jsonl"
PARTS=("plan_pending_seconds","engine_execute_seconds",
       "native_json_ingest_seconds","journal_checkpoint_seconds",
       "invocation_elapsed_seconds")


class TraceBlocked(ValueError):
    pass


def need(ok,why):
    if not ok:
        raise TraceBlocked("V316_"+why)


def identity_hash(seal_path):
    data=pathlib.Path(seal_path).read_bytes()
    need(data and len(data)<300000,"SOURCE_SESSION_SEAL_NOT_PRESENT")
    return hashlib.sha256(data).hexdigest()


def number(x):
    return type(x) in (float,int) and math.isfinite(x) and x>=0


def record(row, *, session_sha256, plan_pending_seconds,
           engine_execute_seconds, native_json_ingest_seconds,
           journal_checkpoint_seconds, invocation_elapsed_seconds,
           resumed_pending, invocation_id):
    need(type(row) is dict and type(row.get("index")) is int
         and type(row.get("iterations")) is int,
         "ORIGINAL_JOURNAL_ROW_REQUIRED")
    payload={
        "schema":SCHEMA,"index":row["index"],
        "session_sha256":session_sha256,
        "invocation_id":invocation_id,
        "case_key":row["case_key"],
        "input_sha256":row["input_sha256"],
        "native_sha256":row["native_sha256"],
        "phase":row["phase"],
        "iterations":row["iterations"],
        "source":row["source"],
        "pending_existed_at_invocation":bool(resumed_pending),
        "plan_pending_seconds":float(plan_pending_seconds),
        "engine_execute_seconds":float(engine_execute_seconds),
        "native_json_ingest_seconds":float(native_json_ingest_seconds),
        "journal_checkpoint_seconds":float(journal_checkpoint_seconds),
        "invocation_elapsed_seconds":float(invocation_elapsed_seconds),
        "timer_clock":"monotonic_elapsed_in_this_process_only",
        "engine_execute_includes_simc_spawn_and_cache_handling":True,
        "no_separately_identified_simc_iteration_slope":True,
        "from_real_simc":row["source"]=="NEW_NATIVE",
        "not_dps_or_sem_receipt":True,
    }
    need(type(session_sha256) is str and len(session_sha256)==64
         and type(invocation_id) is str and len(invocation_id)==32
         and all(c in "0123456789abcdef" for c in invocation_id)
         and all(number(payload[k]) for k in PARTS),
         "NONFINITE_OR_UNBOUND_TIME")
    return payload


def load(path,journal,session_sha256):
    path=pathlib.Path(path)
    if not path.exists():
        return []
    need(path.is_file() and not path.is_symlink() and
         path.stat().st_size<=3_000_000,
         "TRACE_PATH_MUST_BE_SMALL_REGULAR_FILE")
    collected=[]
    last=-1
    with path.open("rb") as reader:
        for line in reader:
            need(line.endswith(b"\n") and len(line)<3500,
                 "TORN_OR_OVERSIZED_TRACE_LINE")
            entry=json.loads(line)
            idx=entry.get("index")
            need(type(idx) is int and last<idx<len(journal),
                 "TRACE_INDEX_MONOTONIC_AND_COMMITTED")
            last=idx
            row=journal[idx]
            need(entry.get("schema")==SCHEMA
                 and entry.get("session_sha256")==session_sha256
                 and type(entry.get("invocation_id")) is str
                 and len(entry["invocation_id"])==32
                 and all(entry.get(x)==row.get(x) for x in (
                     "index","case_key","input_sha256","native_sha256",
                     "phase","iterations","source"))
                 and all(number(entry.get(x)) for x in PARTS)
                 and entry.get("timer_clock")==
                     "monotonic_elapsed_in_this_process_only"
                 and entry.get("not_dps_or_sem_receipt") is True,
                 "ORIGINAL_NATIVE_TRACE_INTEGRITY_OR_SESSION_DRIFT")
            collected.append(entry)
    return collected


def append(path,entry):
    path=pathlib.Path(path)
    need(path.name==NAME,"EXACT_OPTIONAL_TELEMETRY_FILENAME")
    payload=(json.dumps(entry,sort_keys=True,separators=(",",":"),
                        allow_nan=False)+"\n").encode()
    need(len(payload)<3500,"OVERLONG_TELEMETRY_RECORD")
    with path.open("ab") as out:
        out.write(payload)
        out.flush()
        os.fsync(out.fileno())


def summary(trace,journal):
    measured={x["index"] for x in trace}
    new=[x for x in trace if x["source"]=="NEW_NATIVE"]
    phases={phase:{
        "traced_cases":sum(x["phase"]==phase for x in new),
        "iterations":sum(x["iterations"] for x in new if x["phase"]==phase),
        "engine_execute_seconds":round(sum(
            x["engine_execute_seconds"] for x in new
            if x["phase"]==phase),6),
    } for phase in ("scout","precision")}
    return {
        "schema":SCHEMA,
        "journal_cases":len(journal),
        "case_time_trace_rows":len(trace),
        "new_native_traced":len(new),
        "untraced_journal_indices":[i for i in range(len(journal))
                                    if i not in measured],
        "complete_original_journal_trace":len(trace)==len(journal),
        "observed_process_invocations":len({x["invocation_id"] for x in trace}),
        "per_phase":phases,
        "not_a_new_native_execution":True,
        "not_a_source_of_simc_dps":True,
        "cannot_claim_total_wall_checkpoint_across_process_resumes":True,
        "engine_elapsed_includes_spawn_and_cache_miss_overhead":True,
        "per_iteration_simc_cost_not_identified":True,
        "global_optimum_proven":False,
    }


def checkpoints(trace,journal,confirmation_iterations,thresholds=(300,600)):
    """Valid within one uninterrupted measured policy run, NOT cached/resumed.

    Original Native case trace must be source-verified by load() before this.
    Selection bias and multiplicity of chosen pairs are NOT corrected.
    This measures optimiser run() wall from its in-process start, not product
    environment/profile preparation or end-user click-to-result latency.
    """
    need(type(confirmation_iterations) is int
         and confirmation_iterations>0,
         "EXACT_CONFIRMED_ITERATION_IDENTITY")
    need(type(thresholds) is tuple and len(thresholds)>0
         and all(number(x) and x>0 for x in thresholds)
         and list(thresholds)==sorted(set(thresholds)),
         "FIXED_ASCENDING_WALL_CHECKPOINTS")
    valid=(len(trace)==len(journal) and bool(trace)
           and [x["index"] for x in trace]==list(range(len(journal)))
           and len({x["invocation_id"] for x in trace})==1
           and all(x["source"]=="NEW_NATIVE" for x in trace)
           and all(a["invocation_elapsed_seconds"]<=b["invocation_elapsed_seconds"]
                   for a,b in zip(trace,trace[1:])))
    if not valid:
        return {
            "schema":"v316_wall_confirmed_checkpoint_v1",
            "status":"UNAVAILABLE_PARTIAL_OR_RESUMED_OR_CACHE_TIMINGS",
            "exact_5_10_minute_result_available":False,
            "missing_or_multiple_process_invocations_not_extrapolated":True,
            "global_optimum_proven":False}
    result={}
    for threshold in thresholds:
        accepted=[(journal[t["index"]],t)
                  for t in trace if t["invocation_elapsed_seconds"]<=threshold]
        confirmed=[(row,t) for row,t in accepted
                   if row["phase"]=="precision" and
                   row["iterations"]==confirmation_iterations]
        top=sorted(confirmed,key=lambda item:(
            -item[0]["dps_mean"],item[0]["case_key"]))
        best=(top[0][0] if top else None)
        pair=None
        if len(top)>=2:
            one,two=top[0][0],top[1][0]
            half=1.959963984540054*math.hypot(
                one["dps_sem"],two["dps_sem"])
            seeds=(one.get("simc_seed"),two.get("simc_seed"))
            pair={
                "observed_gap_dps":one["dps_mean"]-two["dps_mean"],
                "selected_nominal_95_halfwidth_dps":half,
                "distinct_native_simc_seeds":(
                    all(type(v) is int for v in seeds) and seeds[0]!=seeds[1]),
                "multiplicity_and_selection_bias_not_corrected":True,
                "globally_best_not_proven":True,
            }
            pair["selected_pair_nominal_95_separated"]=(
                pair["distinct_native_simc_seeds"] and
                pair["observed_gap_dps"]>half)
        result[str(int(threshold))]={
            "wall_threshold_seconds":threshold,
            "cases_completed_by_threshold":len(accepted),
            "original_simc_iterations_by_threshold":
                sum(row["iterations"] for row,_ in accepted),
            "confirmed_320_or_configured_iteration_candidates":len(top),
            "highest_observed_confirmed_dps":(
                best["dps_mean"] if best is not None else None),
            "highest_observed_confirmed_sem":(
                best["dps_sem"] if best is not None else None),
            "best_exact_case_key":best["case_key"] if best else None,
            "selected_pair_95":pair,
            "not_from_surrogate_prediction":True,
        }
    return {
        "schema":"v316_wall_confirmed_checkpoint_v1",
        "status":"SINGLE_PROCESS_RECORDED_COMPLETE_JOURNAL",
        "exact_5_10_minute_result_available":True,
        "source_only_native_timings_verified":True,
        "checkpoints":result,
        "environment_profile_build_wall_excluded":True,
        "global_optimum_proven":False}
