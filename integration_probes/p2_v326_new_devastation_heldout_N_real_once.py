#!/usr/bin/env python3
"""v326: new Devastation Evoker auto-T source-first 12-CHMV heldout quality test.

The one new profile is created by existing product P1 Build, v106/v098,
FastAPI source staging, then v291 v290/v318 64 Native per arm. No old profile,
old DPS results, or previous CHMV vector is imported. Research N is isolated
from v291 exact 35/320 caching and remains a bounded one-shot probe.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import pathlib
import random
import re
import subprocess
import time
import zipfile

from integration_probes import p2_v319_new_windwalker_v290_v318_real_once as fresh
from integration_probes import p2_v324_balance_new_user_variable_n_real_once as source_input
from runner import v291_durable_multiscale_native_runner as durable
from runner import v325_independent_holdout_quality_arrival as quality

CASE="devastation_evoker_4ordinary_auto_T"
SPEC=("evoker","devastation")
ROOT=pathlib.Path("out/p2_v326_devastation_fresh_autoT_quality").resolve()
SCHEMA="p2_v326_fresh_devastation_hypothesis_screening_N_holdout_real_v1"
NATIVE_LIMIT_PER_ARM=64
CANDIDATES=12
N_GRID=quality.GRID
HOLDOUT_N=quality.HOLDOUT_N
REPS=quality.REPS
TOTAL_RESEARCH_NATIVE=CANDIDATES*(len(N_GRID)+1)*len(REPS)
SIMC_BINARY_SHA=fresh.fresh.BINARY_SHA

class V326Blocked(RuntimeError):pass
def need(ok,reason):
    if not ok:raise V326Blocked("V326_"+reason)
def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def key(row):
    return quality.key(row["target"])

def select_pooled_candidates(left,right):
    """Precommitted current-run sampling. Winners + distributed chronology.

    Quality reference is never used here: sampling takes place BEFORE any
    640-N holdout. Each exact CHMV has a current-run original scout35 source.
    """
    by_arm={"v290_original":left,"v318_idea001":right}
    sources={}
    for arm,rows in by_arm.items():
        need(len(rows)==64
             and sum(r["phase"]=="scout" and r["iterations"]==35
                     for r in rows)==56
             and sum(r["phase"]=="precision" and r["iterations"]==320
                     for r in rows)==8,
             "EXACT_FULL_NEW_PROFILE_56_8_JOURNAL_REQUIRED")
        for r in rows:
            if r["phase"]=="scout":
                v=key(r)
                if v not in sources or (r["index"],arm)<(
                     sources[v]["index"],sources[v]["arm"]):
                    sources[v]={"vector":v,"row":r,"arm":arm,
                                "index":r["index"]}
    need(len(sources)>=CANDIDATES,"TWELVE_UNIQUE_NEW_USER_SCOUT_CHMV_REQUIRED")
    chosen=[]
    seen=set()
    def add(v):
        if v in sources and v not in seen and len(chosen)<CANDIDATES:
            chosen.append(sources[v]);seen.add(v)
    for arm,rows in by_arm.items():
        best=sorted((r for r in rows if r["phase"]=="precision"
                     and r["iterations"]==320),
                    key=lambda r:(-r["dps_mean"],r["case_key"]))
        for row in best[:3]:add(key(row))
    for step in (0,11,22,33,44,55):
        for arm,rows in by_arm.items():
            scouts=[r for r in rows if r["phase"]=="scout"]
            add(key(scouts[step]))
    if len(chosen)<CANDIDATES:
        # Fill by CHMV distance to already selected samples, not by noisy
        # scout DPS; stable identity tie break.
        for v,source in sorted(sources.items(),key=lambda t:(
                -min(sum(abs(a-b) for a,b in zip(t[0],x["vector"]))
                     for x in chosen),t[0])):
            add(v)
    need(len(chosen)==CANDIDATES and len(seen)==CANDIDATES,
         "TWELVE_DISTINCT_NEW_USER_CHMV_SELECT")
    chosen.sort(key=lambda x:(x["index"],x["vector"]))
    return chosen

def finish_new_profile(doc,binary,root,*,expected_spec=SPEC,
                       screen_ns=N_GRID,screen_reps=REPS,
                       holdout_reps=REPS,selector=select_pooled_candidates,
                       research_schema="v326_new_devastation_original_120_research_native_v1",
                       selection_label="top3_confirm_per_arm_plus_fixed_scout_steps_then_distance",
                       archive_name="research_120_original.zip",
                       shuffle_seed=20261111):
    # Preserve original v326 defaults while enabling new source-first studies.
    screen_ns=tuple(screen_ns)
    screen_reps=tuple(screen_reps)
    holdout_reps=tuple(holdout_reps)
    need(screen_ns in (N_GRID,(32,48,64,96))
         and screen_reps in (REPS,(0,1,2))
         and holdout_reps==REPS
         and callable(selector)
         and type(archive_name) is str and archive_name.endswith(".zip"),
         "EXPLICIT_RESEARCH_GRID_AND_REPLICATION_CONTRACT")
    research_calls=CANDIDATES*(len(screen_ns)*len(screen_reps)
                              +len(holdout_reps))
    need(doc["status"] in ("COMPLETE_TWO_ARMS_EQUAL_CALLS_AND_ITERATIONS",
                "COMPLETE_TWO_ARMS_EQUAL_CALLS_ITERATIONS_UNEQUAL")
         and doc["fresh_profile_generated_once_for_both_arms"] is True
         and doc["manual_final_T"] is None
         and doc["auto_final_T"]==doc["environment_budget"]["T"]
         and doc["character"]["character_class"]==expected_spec[0]
         and doc["character"]["character_spec"]==expected_spec[1]
         and doc["source_from_old_completed_simc_profile"] is False
         and doc["historical_dps_native_cache_imported"] is False
         and sha(binary)==SIMC_BINARY_SHA
         and doc["arms"]["v290_original"]["native_calls"]==NATIVE_LIMIT_PER_ARM
         and doc["arms"]["v318_idea001"]["native_calls"]==NATIVE_LIMIT_PER_ARM,
         "FRESH_DEVASTATION_SOURCE_IDENTITY_AUTO_T_REQUIRED")
    raw={
        arm:durable._load_journal(root/arm/"V291_JOURNAL.jsonl")
        for arm in ("v290_original","v318_idea001")}
    chosen=selector(raw["v290_original"],raw["v318_idea001"])
    T=doc["auto_final_T"]
    need(all(sum(x["vector"])==T for x in chosen),
         "SOURCE_CANDIDATES_NOT_ALL_SAME_AUTO_T")
    dest=root/"research_cases"
    dest.mkdir(exist_ok=False)
    tasks=[(i,n,rep) for i in range(CANDIDATES)
           for n in screen_ns+(HOLDOUT_N,)
           for rep in (holdout_reps if n==HOLDOUT_N else screen_reps)]
    random.Random(shuffle_seed).shuffle(tasks)
    metadata={
        "schema":research_schema,
        "status":"STARTED",
        "new_profile_sha256":doc["source_profile_sha256"],
        "manual_final_T":None,"auto_final_T":T,
        "scenario_revision":doc["revision"],
        "exact_binary_sha256":sha(binary),
        "candidate_selection":selection_label,
        "candidate_order":"ascending_original_earliest_scout_index",
        "selected_candidates":[{
            "CHMV":dict(zip(quality.STATS,x["vector"])),
            "source_arm":x["arm"],
            "source_case_index":x["index"],
            "source_input_sha256":x["row"]["input_sha256"]}
            for x in chosen],
        "screen_N":list(screen_ns),
        "holdout_N":HOLDOUT_N,
        "screen_replicates_per_N":len(screen_reps),
        "holdout_replicates":len(holdout_reps),
        "expected_additional_native":research_calls,
        "measured_native_count":0,
        "native_rows":[],
        "no_global_optimum_proven":True,
        "heldout_quality_band_is_not_95_equivalence":True,
        "v291_new_N_cache_integration":False,
    }
    def checkpoint():
        tmp=root/"research_progress.tmp"
        tmp.write_text(json.dumps(metadata,ensure_ascii=False,
                                  indent=2,sort_keys=True,allow_nan=False)+"\n")
        tmp.replace(root/"research_progress.json")
    checkpoint()
    for job,(i,n,rep) in enumerate(tasks):
        source=chosen[i]
        case=source["row"]
        native_input=root/source["arm"]/"cases"/(
            "case_%05d"%case["index"])/"native"/"input.simc"
        need(native_input.is_file() and sha(native_input)==case["input_sha256"],
             "EXACT_CURRENT_DEVASTATION_SCOUT_INPUT_SHA_REQUIRED")
        outdir=dest/("case_%03d"%job)
        outdir.mkdir()
        output=outdir/"simc.json"
        profile=source_input.update_input(
            native_input.read_text(encoding="utf8"),n,output,
            source_iterations=35,allowed_N=screen_ns+(HOLDOUT_N,))
        input_file=outdir/"input.simc"
        input_file.write_text(profile,encoding="utf8")
        tic=time.monotonic()
        cp=subprocess.run([str(binary),str(input_file.resolve())],
              cwd=binary.parent,stdin=subprocess.DEVNULL,
              stdout=subprocess.PIPE,stderr=subprocess.PIPE,
              check=False,timeout=240)
        elapsed=time.monotonic()-tic
        (outdir/"stdout.txt").write_bytes(cp.stdout)
        (outdir/"stderr.txt").write_bytes(cp.stderr)
        need(cp.returncode==0,"RESEARCH_NATIVE_EXIT_"+str(cp.returncode))
        need(output.is_file() and 0<output.stat().st_size<50_000_000,
             "RESEARCH_JSON2_REQUIRED")
        native=json.loads(output.read_bytes())
        revision=native.get("git_revision")
        sim=native.get("sim") or {}
        players=sim.get("players") or []
        opt=sim.get("options") or {}
        need(type(revision) is str and len(revision)>=10
             and doc["revision"].startswith(revision)
             and len(players)==1 and opt.get("iterations")==n
             and str(players[0].get("specialization","")).lower().startswith(expected_spec[1]),
             "NEW_EVOCATION_SIMC_REV_SPEC_N_DRIFT")
        dps=(players[0].get("collected_data") or {}).get("dps") or {}
        need(dps.get("count")==n-1
             and all(type(dps.get(v)) in (float,int)
                     and math.isfinite(dps[v]) and dps[v]>0
                     for v in ("mean","mean_std_dev"))
             and type(opt.get("seed")) is int
             and opt["seed"]!=case["simc_seed"],
             "DEVASTATION_JSON2_DPS_SEM_SAMPLES_SEED_INVALID")
        row={
            "CHMV":dict(zip(quality.STATS,source["vector"])),
            "n":n,"rep":rep,"samples":dps["count"],
            "dps":dps["mean"],"sem":dps["mean_std_dev"],
            "wall_seconds":round(elapsed,6),
            "seed":opt["seed"],"native_sha256":sha(output),
            "current_profile_scout_input_sha256":case["input_sha256"],
            "current_profile_research_input_sha256":sha(input_file),
        }
        metadata["native_rows"].append(row)
        metadata["measured_native_count"]+=1
        checkpoint()
        if (job+1)%12==0 or job+1==research_calls:
            print("V326_NEW_DEVASTATION_NATIVE_PROGRESS",
                  job+1,"/",research_calls,flush=True)
    need(metadata["measured_native_count"]==research_calls,
         "INCOMPLETE_120_NEW_NATIVE_BUDGET")
    summary=quality.evaluate(
        [dict(zip(quality.STATS,x["vector"])) for x in chosen],
        metadata["native_rows"],grid=screen_ns,
        screen_reps=screen_reps,holdout_reps=holdout_reps)
    metadata["status"]="COMPLETE_CURRENT_PROFILE_120_NEW_NATIVE"
    metadata["quality_replay"]=summary
    z=root/archive_name
    with zipfile.ZipFile(z,"w",compression=zipfile.ZIP_DEFLATED,
                         compresslevel=5) as archive:
        for p in sorted(dest.rglob("*")):
            if p.is_file() and not p.is_symlink():
                archive.write(p,arcname=p.relative_to(dest))
    metadata["original_120_native_zip_sha256"]=sha(z)
    checkpoint()
    print("V326_NEW_DEVASTATION_HOLDOUT_QUALITY_RESULT",
          json.dumps({
              "source_SHA":doc["source_profile_sha256"],
              "auto_T":T,
              "total_new_native":research_calls,
              "good_candidate_count":summary["heldout_good_candidate_count"],
              "by_N":{n:{
                  "final_success_fraction":v["final_success_fraction"],
                  "median_screen_wall":v["median_end_to_end_screen_wall_seconds"],
              } for n,v in summary["by_N"].items()}
          },sort_keys=True),flush=True)
    return {
        "schema":SCHEMA,"status":metadata["status"],
        "source_profile_sha256":doc["source_profile_sha256"],
        "research_native_count":research_calls,
        "original_research_zip_sha256":sha(z),
        "same_new_profile_two_algorithm_arms":True,
        "quality_replay":summary,
        "research_json2_sha256":[x["native_sha256"] for x in
                                    metadata["native_rows"]],
        "not_globally_optimal_or_95_equivalent":True,
    }

def main():
    need(os.getenv("P2_V326_NEW_DEVASTATION_ONCE")=="1",
         "NEW_SPECIALIZATION_NATIVE_EXPLICIT_OPTIN_REQUIRED")
    return fresh.main(
        case_id=CASE,expected_spec=SPEC,output_root=ROOT,
        receipt_path=ROOT/"receipt.json",
        required_env="P2_V326_NEW_DEVASTATION_ONCE",
        campaign_schema=SCHEMA,post_run_hook=finish_new_profile)

if __name__=="__main__":main()
