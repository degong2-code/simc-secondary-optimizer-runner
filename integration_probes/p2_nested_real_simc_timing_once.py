#!/usr/bin/env python3
"""One-shot real SimC timing/discovery comparison, exact archived source.

Bounded: at most 156 genuinely new Native subprocesses, 240 seconds of
candidate/Native work, one verified 70783 Enhancement profile, no new SimC
build or item collection. All JSON2/seed/rating/DPS claims are read from the
unmodified SimC output, never from an inferred effect or synthetic surface.
"""
from __future__ import annotations

import hashlib
import io
import json
import math
import pathlib
import re
import statistics
import subprocess
import sys
import time
import zipfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))

import v063_numeric_injection as source
import v290_multiscale_adaptive_policy as v290
import v301_nested_multiregion_policy as v301

BINARY_SHA="6b83e4d5d2216faf91511fb00ae712cdf4cc0224b0c83107e8c9c7358c24bfc6"
INNER_SHA="c53dc09015377ccaf3d53f24bb85950e3999efacecc629be756b9f8856ef5fa9"
B=3107
MAX_NEW_NATIVE=156
MAX_POLICY_CALLS=48
MAX_WORK_SECONDS=240.0
STATS=tuple(v290.STATS)
OFFSET=(0,165,0,0)
LOW=(0,165,0,0)
UP=tuple((B*60)//100 for _ in STATS)

ROOT_OUT=pathlib.Path("out/p2_nested_real_pilot").resolve()
ROOT_OUT.mkdir(parents=True,exist_ok=True)
RECEIPT=ROOT_OUT/"receipt.json"
BIN=pathlib.Path("out/binary/simc").resolve()


def need(condition,code):
    if not condition:
        raise RuntimeError(code)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def commit(receipt):
    temp=RECEIPT.with_suffix(".tmp")
    temp.write_text(json.dumps(receipt,sort_keys=True,indent=2,
                               ensure_ascii=False)+"\n",encoding="utf8")
    temp.replace(RECEIPT)


def read_archived_profile():
    names=list(pathlib.Path("out/previous").rglob(
        "p3_hae_v291_native_evidence.zip"))
    need(len(names)==1,"ARCHIVED_HAE_EVIDENCE_ZIP_NOT_UNIQUE")
    raw=names[0].read_bytes()
    need(sha(raw)==INNER_SHA,"HISTORICAL_INNER_ZIP_SHA_CHANGED")
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        sess=json.loads(archive.read("V291_SESSION.json"))
        need(sess["B"]==B and
             tuple(sess["lower"][k] for k in STATS)==LOW and
             sess["context"]["revision"]==
             "c20e2ad52e4c33711f74272309a5748125175fe8",
             "HISTORICAL_SESSION_IDENTITY_DRIFT")
        inp=archive.read("cases/case_00000/input.simc").decode("utf8")
        native=json.loads(archive.read("cases/case_00000/result.json"))
        ref=source.input_parts(inp)
        seen=source.read_rating(native["sim"]["players"][0])
        need(tuple(seen[k]-ref["gear_override"][k]
                   for k in STATS)==OFFSET,
             "HISTORICAL_NATIVE_OFFSET_DRIFT")
        need("shaman=target_enhancement" in inp and
             "spec=enhancement" in inp and
             "temporary_enchant=disabled" in inp,
             "HISTORICAL_PROFILE_NOT_ENHANCEMENT_NO_OIL")
        # Original profile/options/gear/talents/APl are immutable for pilot.
        return inp,ref["stable_sha256"]


def encode_candidate(template,stable_sha,vector,iterations,output):
    need(v290.legacy.eligible(vector,B,LOW,UP),"TARGET_OUTSIDE_NEW_60_CAP")
    raw={stat:vector[i]-OFFSET[i] for i,stat in enumerate(STATS)}
    need(all(x>=0 for x in raw.values()),"NEGATIVE_RAW_GEAR")
    lines=template.splitlines()
    for i,line in enumerate(lines):
        for stat,value in raw.items():
            if line.startswith("gear_"+stat+"="):
                lines[i]="gear_"+stat+"="+str(value)
        if line.startswith("iterations="):
            lines[i]="iterations="+str(iterations)
        if line.startswith("json2="):
            lines[i]="json2="+str(output.resolve())
    text="\n".join(lines)+"\n"
    parsed=source.input_parts(text)
    need(parsed["stable_sha256"]==stable_sha and
         parsed["gear_override"]==raw,
         "PRE_NATIVE_PROFILE_OR_GEAR_DRIFT")
    return text


def extract_simc(path,expected_vector,expected_iterations):
    raw=path.read_bytes()
    native=json.loads(raw)
    need(native.get("report_version")=="2.0.0","SIMC_JSON2_REPORT_VERSION")
    players=(native.get("sim") or {}).get("players") or []
    need(len(players)==1,"SIMC_UNEXPECTED_PLAYER_COUNT")
    rating=source.read_rating(players[0])
    need(tuple(rating[k] for k in STATS)==expected_vector,
         "SIMC_EXACT_STATIC_RATING_MISMATCH")
    dps=(players[0].get("collected_data") or {}).get("dps") or {}
    mean,sem,samples=(dps.get(k) for k in (
        "mean","mean_std_dev","count"))
    need(all(type(v) in (float,int) and math.isfinite(v)
             and v>0 for v in (mean,sem,samples)),
         "SIMC_REAL_DPS_SEM_MISSING")
    need(type(samples) is int and 1<=samples<=expected_iterations,
         "SIMC_SAMPLES_OUT_OF_BOUNDS")
    sim=(native.get("sim") or {})
    seed=(sim.get("options") or {}).get("seed")
    return dict(dps_mean=mean,dps_sem=sem,samples=samples,
                simc_seed=seed,json2_sha256=sha(raw),
                observed_ratings=rating)


def main():
    receipt={"schema":"p2_nested_real_simc_11_21_comparison_v1",
       "status":"STARTING","profile":"ENHANCEMENT_SHAMAN_334_HISTORIC_70783",
       "not_current_four_ordinary_default":True,
       "source_commit":"c20e2ad52e4c33711f74272309a5748125175fe8",
       "source_archive_sha256":INNER_SHA,
       "binary_sha256":BINARY_SHA,"B":B,
       "final_T_cap_percent":60,
       "oil_fixed":0,"flask_haste_fixed":165,
       "iterations_scout":35,"iterations_confirmation":320,
       "max_physical_native":MAX_NEW_NATIVE,
       "max_policy_calls_per_arm":MAX_POLICY_CALLS,
       "fixed_budget_independent_global_proof":False,
       "requires_95_pairwise_recheck":True,
       "observations":{},"physical_new_native_count":0,
       "cache_reused_between_policy_arms":0}
    commit(receipt)
    need(BIN.is_file() and sha(BIN.read_bytes())==BINARY_SHA,
         "EXACT_70783_BINARY_NOT_REUSED")
    template,stable=read_archived_profile()
    receipt["stable_input_profile_sha256"]=stable
    commit(receipt)
    policies={
        "v290":(v290.next_plan,None),
        "nested_11":(v301.next_plan,11),
        "nested_21":(v301.next_plan,21),
    }
    runs={name:[] for name in policies}
    caches={}
    native_times=[]
    start=time.perf_counter()

    def evaluate(vector,iterations):
        key=(vector,iterations)
        if key in caches:
            receipt["cache_reused_between_policy_arms"]+=1
            return dict(caches[key],source="SHARED_IN_RUN_EXACT_CACHE")
        need(receipt["physical_new_native_count"]<MAX_NEW_NATIVE,
             "PILOT_NATIVE_CAP")
        folder=ROOT_OUT/"cases"/("case_%03d"%
            receipt["physical_new_native_count"])
        folder.mkdir(parents=True,exist_ok=True)
        output=folder/"native.json"
        text=encode_candidate(template,stable,vector,iterations,output)
        inputfile=folder/"input.simc"
        inputfile.write_bytes(text.encode("utf8"))
        begin=time.perf_counter()
        result=subprocess.run(
            [str(BIN),str(inputfile)],
            cwd=BIN.parent,stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60)
        elapsed=time.perf_counter()-begin
        # Every physical subprocess (including a failure) consumes the cap.
        receipt["physical_new_native_count"]+=1
        if result.returncode!=0:
            receipt["last_simc_error"]={
                "exit_code":result.returncode,
                "stderr_original_tail":result.stderr.decode(
                    "utf8",errors="replace")[-2400:]}
            commit(receipt)
            raise RuntimeError("SIMC_NATIVE_EXIT_"+str(result.returncode))
        need(output.is_file() and output.stat().st_size>0,
             "SIMC_JSON2_NOT_WRITTEN")
        parsed=extract_simc(output,vector,iterations)
        row=dict(parsed,vector=list(vector),iterations=iterations,
                 input_sha256=sha(inputfile.read_bytes()),
                 wall_seconds=round(elapsed,6),
                 source="NEW_NATIVE")
        caches[key]=row
        native_times.append((iterations,elapsed))
        # Carry no large output archive; preserve compact SHA receipts.
        commit(receipt)
        return row

    # The run is deliberately interleaved so wall/CPU drift does not
    # systematically favor one strategy. The same exact case is shared
    # without a duplicate Native call, but both arms record the observation.
    active={name:True for name in policies}
    target_calls=MAX_POLICY_CALLS
    for iteration in range(MAX_POLICY_CALLS):
        if iteration>=8 and len([x for i,x in native_times if i==35])>=3:
            med=statistics.median(x for i,x in native_times if i==35)
            if med>2.0:
                target_calls=min(target_calls,12)
        if iteration>=target_calls or (
            time.perf_counter()-start)>MAX_WORK_SECONDS:
            break
        for name,(policy,points) in policies.items():
            if not active[name]:
                continue
            if time.perf_counter()-start>MAX_WORK_SECONDS:
                active[name]=False
                continue
            previous=runs[name]
            state=[{"target":r["target"],"iterations":r["iterations"],
                    "dps_mean":r["dps_mean"],"dps_sem":r["dps_sem"]}
                   for r in previous]
            args=dict(total=B,lower=LOW,upper=UP,
                native_calls_used=len(previous),
                max_native_calls=MAX_POLICY_CALLS,
                scout_iterations=35,confirmation_iterations=320,
                max_iterations=320)
            if points is not None:
                args["reference_points"]=points
            plan=policy(state,**args)
            if (plan["status"]!="NEXT_NATIVE_PROPOSED" or
                    plan["next_request"] is None):
                active[name]=False
                continue
            req=plan["next_request"]
            vec=v290.legacy.key(req["target"])
            measured=evaluate(vec,req["iterations"])
            row=dict(measured,target=req["target"],
                     phase=req["phase"],decision=plan["decision"],
                     policy_request=iteration+1)
            previous.append(row)
            receipt["observations"][name]=previous
            receipt["elapsed_seconds"]=round(
                time.perf_counter()-start,4)
            commit(receipt)
        if (iteration+1)%8==0:
            print("P2_REAL_NATIVE_PROGRESS",json.dumps({
                "round":iteration+1,
                "physical_calls":receipt["physical_new_native_count"],
                "elapsed_seconds":receipt.get("elapsed_seconds"),
                "arms":{name:len(rows) for name,rows in runs.items()},
                "median_new_scout_wall":round(
                    statistics.median(x for i,x in native_times if i==35),4)
                    if any(i==35 for i,x in native_times) else None,
            },sort_keys=True),flush=True)

    # Final rechecks are optional but only if time/call cap allows.
    for name,rows in runs.items():
        best_by={}
        for r in rows:
            vec=tuple(r["vector"])
            if vec not in best_by or r["iterations"]>best_by[vec]["iterations"]:
                best_by[vec]=r
        top=sorted(best_by.values(),key=lambda r:-r["dps_mean"])[:2]
        for r in top:
            vec=tuple(r["vector"])
            if ((vec,320) in caches or
                    (time.perf_counter()-start)>MAX_WORK_SECONDS or
                    receipt["physical_new_native_count"]>=MAX_NEW_NATIVE):
                continue
            confirmed=evaluate(vec,320)
            receipt.setdefault("follow_up_320",[]).append(
                {"arm":name,**confirmed})
            commit(receipt)

    summaries={}
    for name,rows in runs.items():
        by_vec={}
        for r in rows:
            vec=tuple(r["vector"])
            if vec not in by_vec or r["iterations"]>by_vec[vec]["iterations"]:
                by_vec[vec]=r
        best=max(by_vec.values(),key=lambda r:r["dps_mean"]) if by_vec else None
        summaries[name]={
            "candidate_requests":len(rows),
            "unique_vectors":len(by_vec),
            "requested_iterations":sum(r["iterations"] for r in rows),
            "observed_best_target":best["vector"] if best else None,
            "observed_best_mean":best["dps_mean"] if best else None,
            "observed_best_sem":best["dps_sem"] if best else None,
            "observed_best_request_number":best["policy_request"] if best else None,
        }
    receipt["summaries"]=summaries
    receipt["timing"]={
        str(iterations):{
            "count":len([v for it,v in native_times if it==iterations]),
            "median_seconds":statistics.median(
                v for it,v in native_times if it==iterations),
            "mean_seconds":statistics.mean(
                v for it,v in native_times if it==iterations),
            "max_seconds":max(v for it,v in native_times if it==iterations),
        }
        for iterations in (35,320)
        if any(it==iterations for it,_ in native_times)}
    receipt["elapsed_seconds"]=round(time.perf_counter()-start,4)
    receipt["status"]="PASS_REAL_NATIVE_EXPLORATORY_NO_GLOBAL_PROOF"
    commit(receipt)
    print("P2_REAL_NATIVE_FINAL",
          json.dumps({k:receipt[k] for k in (
              "status","physical_new_native_count",
              "cache_reused_between_policy_arms","elapsed_seconds",
              "summaries","timing")},sort_keys=True),flush=True)


if __name__=="__main__":
    try:
        main()
    except Exception as exc:
        path=RECEIPT
        doc=json.loads(path.read_text()) if path.is_file() else {}
        doc["status"]="BLOCKED_REAL_NATIVE_"+type(exc).__name__
        doc["first_error"]=str(exc)[:500]
        commit(doc)
        print("P2_REAL_NATIVE_PILOT_BLOCKED",repr(exc),flush=True)
        raise
