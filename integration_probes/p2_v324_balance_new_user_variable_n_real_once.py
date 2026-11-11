#!/usr/bin/env python3
"""v324 one-shot new Balance Druid auto-T, same-host variable N SimC study.

NEVER use an old completed user profile. Uses the existing P1 v319 web/
environment/profile path and v291 64+64 DPS comparators. Research samples
new N directly from *current-campaign* exact 320 case inputs, changing
iterations/json2 only. v291 continues allowing only 35/320.
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
from collections import defaultdict

from integration_probes import p2_v319_new_windwalker_v290_v318_real_once as harness
from runner import v291_durable_multiscale_native_runner as durable
from runner import v323_continuous_n_sem_wall_advisory as advisory

SCHEMA="p2_v324_new_balance_druid_autoT_same_host_continuous_N_v1"
CASE_ID="balance_druid_4ordinary_auto_T"
EXPECTED_SPEC=("druid","balance")
ROOT=pathlib.Path("out/p2_v324_balance_auto_T_variable_N").resolve()
STATS=("crit_rating","haste_rating","mastery_rating","versatility_rating")
N_GRID=(20,32,48,80,128,200,480,640)
CONFIRM_RANKS=(0,1,4,7)
EXPECTED_RESEARCH_NATIVE=len(N_GRID)*len(CONFIRM_RANKS)
BINARY_SHA="6b83e4d5d2216faf91511fb00ae712cdf4cc0224b0c83107e8c9c7358c24bfc6"

class VariableNBlocked(RuntimeError): pass

def need(ok,reason):
    if not ok: raise VariableNBlocked("V324_"+reason)

def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def vect(row):
    return tuple(row["target"][k] for k in STATS)

def update_input(original,n,out):
    need(type(original) is str and type(n) is int
         and n in N_GRID
         and len(re.findall(r"(?m)^iterations=320$",original))==1
         and len(re.findall(r"(?m)^json2=.+$",original))==1,
         "EXACT_CURRENT_PROFILE_NATIVE320_INPUT_REQUIRED")
    converted=re.sub(r"(?m)^iterations=320$",
                     "iterations="+str(n),original)
    converted=re.sub(r"(?m)^json2=.+$",
                     lambda _: "json2="+str(out.resolve()),converted)
    # Full source byte-equivalent modulo the only two allowed changes.
    norm=lambda s: re.sub(r"(?m)^json2=.+$","json2=REMOVED",
                           re.sub(r"(?m)^iterations=\\d+$",
                                  "iterations=REMOVED",s))
    need(norm(converted)==norm(original),
         "OTHER_PROFILE_GEAR_FLASK_TALENTS_CHANGED")
    return converted

def finish_current_campaign(doc,binary,root):
    need(doc.get("status")=="COMPLETE_TWO_ARMS_EQUAL_CALLS_AND_ITERATIONS"
         and doc["manual_final_T"] is None
         and doc["auto_final_T"]==doc["environment_budget"]["T"]
         and doc["character"]["character_class"]=="druid"
         and doc["character"]["character_spec"]=="balance"
         and doc["source_from_old_completed_simc_profile"] is False
         and doc["historical_dps_native_cache_imported"] is False
         and sha(binary)==BINARY_SHA,
         "SOURCE_FIRST_NEW_BALANCE_AUTO_T_REQUIRED")
    rows=durable._load_journal(root/"v290_original"/"V291_JOURNAL.jsonl")
    need(len(rows)==64 and len([r for r in rows if r["phase"]=="scout"])==56
         and len([r for r in rows if r["phase"]=="precision"])==8,
         "EXACT_ORIGINAL_64_NATIVE_JOURNAL_REQUIRED")
    scout={vect(r):r for r in rows if r["phase"]=="scout" and
           r["iterations"]==35}
    confirmed=sorted((r for r in rows if r["phase"]=="precision" and
                      r["iterations"]==320 and vect(r) in scout),
                     key=lambda r:(-r["dps_mean"],r["case_key"]))
    need(len(confirmed)==8,"EIGHT_ORIGINAL_PRECISION_CASES_REQUIRED")
    chosen=[confirmed[i] for i in CONFIRM_RANKS]
    need(len({vect(x) for x in chosen})==len(chosen),
         "FOUR_DISTINCT_CONFIRM_TARGETS_REQUIRED")
    batch=[(r,n) for r in chosen for n in N_GRID]
    random.Random(20261111).shuffle(batch)  # reduce systematic time drift
    dest=root/"research_variable_n"
    dest.mkdir(exist_ok=False)
    payload={"schema":"v324_same_host_new_balance_continuous_n_measurements_v1",
             "status":"STARTED","source_profile_sha256":
                 doc["source_profile_sha256"],
             "auto_final_T":doc["auto_final_T"],
             "same_host_as_v290_320":True,
             "new_native_research_count":0,
             "study_N_grid":list(N_GRID),
             "v291_does_not_execute_variable_N":True,
             "research_only":True,"results":[]}
    for j,(case,n) in enumerate(batch):
        source=root/"v290_original"/"cases"/(
            "case_%05d"%case["index"])/"native"/"input.simc"
        need(sha(source)==case["input_sha256"],
             "ORIGINAL_CURRENT_320_INPUT_SHA_CHANGED")
        folder=dest/("sample_%02d"%j)
        folder.mkdir()
        out=folder/"result.json"
        input_text=update_input(source.read_text(encoding="utf8"),n,out)
        input_file=folder/"input.simc"
        input_file.write_text(input_text,encoding="utf8")
        begin=time.monotonic()
        cp=subprocess.run([str(binary),str(input_file.resolve())],
                          cwd=binary.parent,stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                          timeout=240,check=False)
        elapsed=time.monotonic()-begin
        (folder/"stdout.txt").write_bytes(cp.stdout)
        (folder/"stderr.txt").write_bytes(cp.stderr)
        need(cp.returncode==0,
             "SIMC_RESEARCH_NATIVE_N_EXIT_"+str(cp.returncode))
        need(out.is_file() and 0<out.stat().st_size<50_000_000,
             "NATIVE_RESEARCH_JSON2_MISSING")
        raw=out.read_bytes();native=json.loads(raw)
        need(type(native.get("git_revision")) is str and
             doc["revision"].startswith(native["git_revision"]) and
             len(native["git_revision"])>=10,
             "SIMC_REVISION_MUST_MATCH_FULL_SOURCE_PREFIX")
        sim=native.get("sim") or {}
        players=sim.get("players") or []
        opt=sim.get("options") or {}
        need(len(players)==1 and opt.get("iterations")==n
             and str(players[0].get("specialization","")).lower()
                     in ("balance druid","balance"),
             "RESEARCH_SPEC_OR_ITERATION_WRONG")
        dps=(players[0].get("collected_data") or {}).get("dps") or {}
        need(dps.get("count")==n-1
             and type(dps.get("mean")) in (int,float)
             and type(dps.get("mean_std_dev")) in (int,float)
             and math.isfinite(dps["mean"])
             and math.isfinite(dps["mean_std_dev"])
             and dps["mean_std_dev"]>=0
             and type(opt.get("seed")) is int
             and opt["seed"]!=case["simc_seed"],
             "ACTUAL_NATIVE_N_DPS_SEM_SAMPLES_SEED_INVALID")
        item={"sample_index":j,"CHMV":list(vect(case)),
              "source_confirm320_original_index":case["index"],
              "source_confirm320_input_sha256":case["input_sha256"],
              "N":n,"actual_dps_samples":dps["count"],
              "DPS":dps["mean"],"SEM":dps["mean_std_dev"],
              "native_seed":opt["seed"],"process_wall_seconds":round(elapsed,6),
              "exact_research_input_sha256":sha(input_file),
              "exact_native_json_sha256":sha(out)}
        payload["results"].append(item)
        payload["new_native_research_count"]+=1
        (root/"research_progress.json").write_text(
           json.dumps(payload,indent=2,sort_keys=True)+"\n")
        print("V324_NEW_BALANCE_REAL_N",json.dumps({
            "CHMV":item["CHMV"],"N":n,"SEM":item["SEM"],
            "wall":item["process_wall_seconds"]},sort_keys=True),flush=True)
    need(len(payload["results"])==EXPECTED_RESEARCH_NATIVE,
         "NOT_ALL_NEW_NATIVE_N_SAMPLES_RECORDED")
    wall=[{"iterations":x["N"],"wall_seconds":x["process_wall_seconds"]}
          for x in payload["results"]]
    fit=advisory.fit_wall(wall)
    clusters=defaultdict(dict)
    for x in payload["results"]:
        clusters[tuple(x["CHMV"])][x["N"]]=x
    reference=max((cluster[640] for cluster in clusters.values()),
                  key=lambda x:x["DPS"])
    results={}
    for vec,group in clusters.items():
        first=group[32]
        cost_reference={"iterations":640,"samples":639,
                        "dps_mean":reference["DPS"],"dps_sem":reference["SEM"]}
        cost_candidate={"iterations":32,"samples":31,
                        "dps_mean":first["DPS"],"dps_sem":first["SEM"]}
        advice=advisory.recommend(
            cost_candidate,cost_reference,min_n=16,max_n=640,
            step=8,cost=fit)
        results["/".join(map(str,vec))]={
            "recommended_N_from_actual_N32_and_current_campaign_N640":advice,
            "observed_by_N":{str(n):{
                "DPS":x["DPS"],"SEM":x["SEM"],
                "wall_seconds":x["process_wall_seconds"]}
                for n,x in sorted(group.items())}}
    payload.update({
        "status":"REAL_32_SAME_HOST_RESEARCH_N_COMPLETED",
        "same_host_measured_process_wall_fit":fit,
        "comparisons_by_CHMV":results,
        "selected_N640_best_among_only_four_candidates":
            reference["CHMV"],
        "not_global_optimum":True,
        "post_selection_95_not_proven":True,
        "observed_quality_not_causal_policy_proof":True})
    archive=root/"research_variable_N_original.zip"
    with zipfile.ZipFile(archive,"w",
                         compression=zipfile.ZIP_DEFLATED,
                         compresslevel=5) as z:
        for file in sorted(dest.rglob("*")):
            if file.is_file() and not file.is_symlink():
                z.write(file,arcname=file.relative_to(dest))
    payload["original_research_zip_sha256"]=sha(archive)
    (root/"research_progress.json").write_text(
        json.dumps(payload,sort_keys=True,indent=2)+"\n")
    print("V324_NEW_BALANCE_N_SWEEP_COMPLETE",json.dumps({
        "source_sha":doc["source_profile_sha256"],
        "auto_T":doc["auto_final_T"],
        "new_research_native":payload["new_native_research_count"],
        "cost_model":fit},sort_keys=True),flush=True)
    return payload

def main():
    need(os.getenv("P2_V324_NEW_BALANCE_N_SWEEP_ONCE")=="1",
         "EXPLICIT_NEW_USER_NATIVE_OPT_IN_REQUIRED")
    return harness.main(
        case_id=CASE_ID,expected_spec=EXPECTED_SPEC,
        output_root=ROOT,receipt_path=ROOT/"receipt.json",
        required_env="P2_V324_NEW_BALANCE_N_SWEEP_ONCE",
        campaign_schema=SCHEMA,
        post_run_hook=finish_current_campaign)
if __name__=="__main__":main()
