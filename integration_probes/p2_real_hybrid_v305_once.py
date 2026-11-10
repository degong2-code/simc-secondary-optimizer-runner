#!/usr/bin/env python3
"""One-shot ACTUAL SimC v305 hybrid vs previously sealed equal-cost pilot.

Previous 127 new Native measurements and 32 shared initial globals are loaded
as compact historical observations (NOT v291 raw JSON2 receipts). New SimC
calls are made ONLY for missing exact (vector,iterations) identities.
No product default change, no source compilation, no background scheduling.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import pathlib
import subprocess
import sys
import time

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"integration_probes")]
import p2_real_equal_v304_once as old_study
import v305_grid_pairwise_adaptive_hybrid as v305
import v290_multiscale_adaptive_policy as v290

SCHEMA="p2_v305_hybrid_actual_simc_equal_4520_v1"
PREVIOUS_COMPACT_SHA="1dfcafd734d673edf956b247d4118359b081b2bb3cc3787ca1c04d0e4356878f"
PRIOR_100_SHA="eaa608b3612a81daed7e33e4032793b43dc5fff3e07ed9b797157708f7d60799"
BINARY_SHA=old_study.prior.BINARY_SHA
PROFILE_SHA="1b576a21ce0d70e2915ae9bbb7e122efbebf212e0df0f587ecfcf85dd21cfb1d"
HISTORY_127=pathlib.Path("out/previous_v304/receipt.json").resolve()
HISTORY_100=pathlib.Path("out/previous_100/receipt.json").resolve()
BINARY=pathlib.Path("out/binary/simc").resolve()
OUT=pathlib.Path("out/p2_v305_real_hybrid_once").resolve()
MAX_NEW_NATIVE=40
MAX_SECONDS=180.0


def need(ok,reason):
    if not ok:
        raise RuntimeError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def validate_old(doc,stable):
    """Strict prior source/initial experiment identity, fail before Native."""
    need(doc.get("schema")==old_study.SCHEMA and
         doc.get("status")=="PASS_REAL_SIMC_EXPLORATORY_NO_GLOBAL_PROOF" and
         doc.get("binary_sha256")==BINARY_SHA and
         doc.get("source_archive_sha256")==old_study.prior.INNER_SHA and
         doc.get("source_commit")==old_study.KNOWN_SOURCE_COMMIT and
         doc.get("stable_profile_sha256")==stable==PROFILE_SHA and
         doc.get("historical_compact_sha256")==PRIOR_100_SHA and
         doc.get("new_native")==127 and
         doc.get("historical_exact_observation_reuses")==3 and
         doc.get("same_run_cache_reuses")==13 and
         doc.get("budget",{}).get("requested_iterations_per_arm")==4520 and
         len(doc.get("initial_global",[]))==old_study.GLOBAL and
         set(doc.get("arms",{}))==set(old_study.ARMS),
         "HISTORICAL_127_EXACT_PROFILE_BUDGET_PROOF_DRIFT")
    for index,row in enumerate(doc["initial_global"]):
        measured=old_study.row_to_native(row)
        expected=old_study.v304._global_order(
            old_study.B,tuple(old_study.LOWER),
            tuple(old_study.UPPER),old_study.GLOBAL)[index]
        need(tuple(measured["vector"])==expected and
             measured["iterations"]==old_study.SCOUT_ITERS and
             type(measured["json2_sha256"]) is str and
             len(measured["json2_sha256"])==64,
             "HISTORICAL_SHARED_GLOBAL_ORDER_DRIFT")
    for arm in old_study.ARMS:
        rows=doc["arms"][arm]
        need(len(rows)==old_study.POST+old_study.CONFIRM+1 and
             sum(x["iterations"] for x in rows)==
             old_study.POST*old_study.SCOUT_ITERS+
             old_study.CONFIRM*old_study.CONFIRM_ITERS+
             old_study.RECHECK_ITERS,
             "HISTORICAL_ARM_REQUEST_COUNT_OR_ITERATIONS_DRIFT")
        for row in rows:
            parsed=old_study.row_to_native(row)
            need(type(parsed["json2_sha256"]) is str and
                 len(parsed["json2_sha256"])==64,
                 "HISTORICAL_ARM_JSON2_SHA_MISSING")
    return True


def historical_cache(old,prior100):
    cache=old_study.historical_cache(prior100,PROFILE_SHA)
    known=len(cache)
    reused=0
    for row in old["initial_global"]+sum(
            (old["arms"][arm] for arm in old_study.ARMS), []):
        native=old_study.row_to_native(row)
        key=(tuple(native["vector"]), native["iterations"])
        old_row=cache.get(key)
        if old_row is not None:
            need(old_row["dps_mean"]==native["dps_mean"] and
                 old_row["dps_sem"]==native["dps_sem"] and
                 old_row["json2_sha256"]==native["json2_sha256"],
                 "HISTORICAL_SAME_EXACT_NATIVE_DRIFT")
            reused+=1
        else:
            cache[key]=native
    need(known==100 and reused>=0 and len(cache)>known,
         "HISTORICAL_CROSS_STUDY_CACHE_MISSING")
    return cache,{"old100_unique":known, "old127_added_unique":len(cache)-known,
                  "overlap_records":reused,
                  "old127_real_new_native":old["new_native"]}


def row_for_plan(measured,req):
    native=old_study.to_v304_row(measured,req)
    native["hybrid_method"]=req["hybrid_method"]
    return native


def plan(hist):
    return v305.next_plan(
        hist,total=old_study.B,lower=old_study.LOWER,
        upper=old_study.UPPER,
        max_native_calls=old_study.GLOBAL+old_study.POST+old_study.CONFIRM,
        scout_iterations=old_study.SCOUT_ITERS,
        confirmation_iterations=old_study.CONFIRM_ITERS,
        initial_global_calls=old_study.GLOBAL,
        confirmation_calls=old_study.CONFIRM)


def comparison(hybrid,old):
    rows={}
    rows["hybrid_v305"]=hybrid
    for arm in old_study.ARMS:
        rows[arm]=old["summaries"][arm]["observed_best_1000"]
    result={}
    for method,datum in rows.items():
        result[method]=dict(
            vector=datum["vector"],
            dps_mean=datum["dps_mean"],
            dps_sem=datum["dps_sem"],
            iterations=datum["iterations"])
    pair={}
    for arm in old_study.ARMS:
        pair["v305_vs_"+arm]=old_study.mean_sem_pair(hybrid,rows[arm])
    return result,pair


def main():
    need(os.getenv("P2_V305_HYBRID_REAL_ONCE")=="1",
         "EXPLICIT_V305_ONE_SHOT_NATIVE_OPT_IN_REQUIRED")
    need(BINARY.is_file() and digest(BINARY.read_bytes())==BINARY_SHA,
         "V305_PINNED_BINARY_SHA_MISMATCH")
    need(HISTORY_127.is_file() and
         digest(HISTORY_127.read_bytes())==PREVIOUS_COMPACT_SHA,
         "V305_HISTORICAL_127_COMPACT_SHA_MISMATCH")
    need(HISTORY_100.is_file() and
         digest(HISTORY_100.read_bytes())==PRIOR_100_SHA,
         "V305_HISTORICAL_100_COMPACT_SHA_MISMATCH")
    template,stable=old_study.prior.read_archived_profile()
    old=json.loads(HISTORY_127.read_text())
    validate_old(old,stable)
    cache, history_counters=historical_cache(old,HISTORY_100)
    OUT.mkdir(parents=True,exist_ok=True)
    dest=OUT/"receipt.json"
    report={
        "schema":SCHEMA, "status":"STARTED",
        "historical_127_compact_sha256":PREVIOUS_COMPACT_SHA,
        "historical_100_compact_sha256":PRIOR_100_SHA,
        "profile_sha256":stable,
        "binary_sha256":BINARY_SHA,
        "source_archive_sha256":old_study.prior.INNER_SHA,
        "previous_real_actions_run_id":42772775449,
        "study_current_historical_special_gem_not_product_default":True,
        "historical_cache_raw_json2_not_present":True,
        "same_initial_global_32_sha_scope":True,
        "max_new_native":MAX_NEW_NATIVE,
        "max_native_wall_seconds":MAX_SECONDS,
        "requested_iterations_per_arm":4520,
        "new_native_attempts":0,
        "old_compact_observation_reuses":0,
        "same_run_observation_reuses":0,
        "initial_global":[],
        "hybrid_arm":[],
        "comparisons":{},
        "historical_counts":history_counters,
        "global_optimum_proven":False,
        "familywise_95_proven":False,
    }
    def save():
        tmp=dest.with_suffix(".tmp")
        tmp.write_text(json.dumps(report,sort_keys=True,indent=2,
                                  ensure_ascii=False)+"\n",encoding="utf8")
        tmp.replace(dest)
    save()
    clock=time.perf_counter()
    observed_keys=set()
    def evaluate(vec,iters):
        vec=tuple(vec)
        key=(vec,iters)
        need(v290.legacy.eligible(vec,old_study.B,
                                  old_study.LOWER,old_study.UPPER),
             "V305_CANDIDATE_INFEASIBLE")
        need(time.perf_counter()-clock<MAX_SECONDS,
             "V305_WALL_CLOCK_CAP")
        if key in cache:
            result=dict(cache[key])
            if key in observed_keys:
                report["same_run_observation_reuses"]+=1
                result["source"]="SAME_RUN_COMPACT_OBSERVATION_REUSE"
            else:
                report["old_compact_observation_reuses"]+=1
                result["source"]="HISTORICAL_COMPACT_NOT_RAW_JSON2_CACHE"
            observed_keys.add(key)
            return result
        need(report["new_native_attempts"]<MAX_NEW_NATIVE,
             "V305_NEW_NATIVE_CAP_EXHAUSTED")
        idx=report["new_native_attempts"]
        case=OUT/"cases"/("case_%03d"%idx)
        case.mkdir(parents=True,exist_ok=False)
        outfile=case/"result.json"
        inp=old_study.prior.encode_candidate(
            template,stable,vec,iters,outfile)
        inputfile=case/"input.simc"
        inputfile.write_text(inp,encoding="utf8")
        start=time.perf_counter()
        report["new_native_attempts"]+=1
        save()
        try:
            p=subprocess.run(
                [str(BINARY),str(inputfile)],cwd=BINARY.parent,
                stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,timeout=45)
        except subprocess.TimeoutExpired as exc:
            report["simc_error_original"]=str(exc)
            save()
            raise
        elapsed=time.perf_counter()-start
        if p.returncode:
            report["simc_error_original"]=p.stderr.decode(
                "utf8",errors="replace")[-2400:]
            save()
            raise RuntimeError("V305_REAL_SIMC_EXIT_"+str(p.returncode))
        need(outfile.is_file(),"SIMC_JSON2_NOT_WRITTEN")
        native=old_study.prior.extract_simc(outfile,vec,iters)
        result=old_study.row_to_native({
            **native,"vector":list(vec),"iterations":iters})
        result.update(source="NEW_NATIVE",
                      input_sha256=digest(inputfile.read_bytes()),
                      wall_seconds=round(elapsed,6))
        cache[key]=dict(result)
        observed_keys.add(key)
        # Restrict uploaded proof to compact report; no huge JSON2 storage.
        inputfile.unlink()
        outfile.unlink()
        save()
        return result
    try:
        history=[]
        for i,measured in enumerate(old["initial_global"]):
            proposed=plan(history)
            need(proposed["next_request"] is not None,
                 "V305_SHARED_INITIAL_PLAN_MISSING")
            req=proposed["next_request"]
            vec=tuple(v290.legacy.key(req["target"]))
            need(req["adaptive_stage"]=="global_initial" and
                 vec==tuple(measured["vector"]),
                 "V305_SHARED_GLOBAL_VECTOR_DRIFT")
            row=dict(evaluate(vec,old_study.SCOUT_ITERS),
                     hybrid_method=req["hybrid_method"],
                     index=i)
            history.append(row_for_plan(row,req))
            report["initial_global"].append(row)
            save()
        for i in range(old_study.POST+old_study.CONFIRM):
            proposed=plan(history)
            need(proposed["next_request"] is not None,
                 "V305_PROPOSAL_NO_NEW_CANDIDATE")
            req=proposed["next_request"]
            wanted_stage=("confirmation" if i>=old_study.POST else None)
            need((wanted_stage is None and req["phase"]=="scout") or
                 (wanted_stage=="confirmation" and
                  req["adaptive_stage"]=="confirmation" and
                  req["phase"]=="precision"),
                 "V305_BUDGET_STAGE_MISMATCH")
            vec=tuple(v290.legacy.key(req["target"]))
            measured=evaluate(vec,req["iterations"])
            row=dict(measured,hybrid_method=req["hybrid_method"],
                     region_id=req["region_id"],
                     region_center=req["region_center"],
                     region_radius_fraction=req["region_radius_fraction"],
                     adaptive_stage=req["adaptive_stage"],
                     phase=req["phase"],policy_decision=proposed["decision"],
                     policy_request_index=len(history))
            history.append(row_for_plan(measured,req))
            report["hybrid_arm"].append(row)
            save()
            if (i+1)%8==0:
                print("P2_V305_REAL_PROGRESS",json.dumps({
                    "completed_post":i+1,
                    "new_native":report["new_native_attempts"],
                    "reused_compact":report["old_compact_observation_reuses"],
                    "elapsed_seconds":round(time.perf_counter()-clock,3),
                },sort_keys=True),flush=True)
        confirmations=[r for r in report["hybrid_arm"]
                       if r["iterations"]==old_study.CONFIRM_ITERS]
        need(len(confirmations)==old_study.CONFIRM,
             "V305_NOT_FOUR_CONFIRMATIONS")
        best=max(confirmations,key=lambda x:(x["dps_mean"],-x["dps_sem"]))
        recheck=evaluate(best["vector"],old_study.RECHECK_ITERS)
        report["selected_1000"]=dict(recheck,selected_from_320=best["vector"])
        allrows=report["initial_global"]+report["hybrid_arm"]+[recheck]
        need(len(allrows)==69 and
             sum(r["iterations"] for r in allrows)==4520 and
             len({_key(r) for r in allrows})==69,
             "V305_EXACT_BUDGET_OR_DUPLICATE_REQUEST")
        table,pairs=comparison(recheck,old)
        report["comparison_1000"]=table
        report["comparisons"]=pairs
        report["local_methods"]={
            name:sum(r["hybrid_method"]==name for r in
                     report["hybrid_arm"])
            for name in (v305.GRID,v305.PAIR,v305.FALLBACK,v305.RESERVE,v305.CONFIRM)}
        report["actual_elapsed_seconds"]=round(time.perf_counter()-clock,4)
        report["historical_three_arm_wall_seconds_aggregate"]=old["elapsed_seconds_total"]
        report["wall_clock_comparison_not_equal_run"]=True
        report["status"]="PASS_REAL_SIMC_EXPLORATORY_NO_GLOBAL_PROOF"
        save()
        print("P2_V305_REAL_FINAL",json.dumps({
            "status":report["status"],
            "new_native":report["new_native_attempts"],
            "reused_compact":report["old_compact_observation_reuses"],
            "actual_elapsed_seconds":report["actual_elapsed_seconds"],
            "local_methods":report["local_methods"],
            "best_1000":report["comparison_1000"],
            "nominal_pairs":report["comparisons"],
        },sort_keys=True),flush=True)
    except BaseException as e:
        report["status"]="BLOCKED_OR_PARTIAL_"+type(e).__name__
        report["first_error"]=str(e)[:500]
        report["actual_elapsed_seconds"]=round(time.perf_counter()-clock,4)
        save()
        print("P2_V305_REAL_BLOCKED",repr(e),flush=True)
        raise


def _key(row):
    return tuple(row["vector"]),row["iterations"]


if __name__=="__main__":
    main()
