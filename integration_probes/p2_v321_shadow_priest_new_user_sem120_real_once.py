#!/usr/bin/env python3
"""v321: NEW Shadow Priest auto-T source-first real 35/120/320 SEM calibration.

Reuses *exact* P1/Local Web/v291 source-first product campaign v319 harness,
never copies a prior completed character/profile.  Both policy arms share this
new Shadow profile. Additional n120 samples are independent, research-only
Native observations derived exclusively from exact v291 accepted input.simc
for the SAME new profile / CHMV as current-run scout35+confirmation320.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import pathlib
import re
import subprocess
import time
import zipfile
from collections import Counter

from integration_probes import p2_v319_new_windwalker_v290_v318_real_once as harness
from runner import v320_idea001_sem_tier_advisory as advisory
from runner import v291_durable_multiscale_native_runner as durable

SCHEMA="p2_v321_fresh_shadow_autoT_35_120_320_real_native_calibration_v1"
CASE="shadow_priest_4ordinary_auto_T"
EXPECTED=("priest","shadow")
OUT=pathlib.Path("out/p2_v321_shadow_auto_T_new_user_AB").resolve()
STATS=advisory.STATS
MIDDLE=120
NUM_RESEARCH_120=3

class ShadowTierBlocked(RuntimeError):
    pass

def need(ok, why):
    if not ok:
        raise ShadowTierBlocked(why)

def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def key(row):
    return tuple(row["target"][s] for s in STATS)

def exact_new_simc_120_input(source, json2_path):
    """Only change exact requested iterations and output path of a verified
    current-run v291 320-case input. No flask/gear/filler/item edits.
    """
    need(type(source) is str
         and len(re.findall(r"(?m)^iterations=320$",source))==1
         and len(re.findall(r"(?m)^json2=.+$",source))==1,
         "V321_VERIFIED_320_SOURCE_SYNTAX_REQUIRED")
    source=re.sub(r"(?m)^iterations=320$", "iterations=120", source)
    return re.sub(r"(?m)^json2=.+$", "json2="+str(json2_path), source)

def after_both_arms(doc,binary,root):
    need(doc["status"]=="COMPLETE_TWO_ARMS_EQUAL_CALLS_AND_ITERATIONS"
         and doc["fresh_profile_generated_once_for_both_arms"] is True
         and doc["manual_final_T"] is None
         and doc["auto_final_T"]==doc["environment_budget"]["T"]
         and doc["arms"]["v290_original"]["same_source_profile_sha256"]==
         doc["arms"]["v318_idea001"]["same_source_profile_sha256"],
         "V321_NEW_SHADOW_SAME_SOURCE_AUTO_T_A_B_REQUIRED")
    rows=durable._load_journal(root/"v290_original"/"V291_JOURNAL.jsonl")
    need(len(rows)==64,"V321_VERIFIED_NEW_SHADOW_V290_JOURNAL64")
    scouts={key(r):r for r in rows if r["phase"]=="scout"
            and r["iterations"]==35}
    confirms=[r for r in rows
              if r["phase"]=="precision" and r["iterations"]==320
              and key(r) in scouts]
    need(len(scouts)==56 and len(confirms)==8,
         "V321_NEW_SHADOW_56_SCOUT_8_CONFIRMED_REQUIRED")
    confirms=sorted(confirms,key=lambda r:(-r["dps_mean"],r["case_key"]))
    reference=confirms[0]
    counts=Counter()
    for scout in scouts.values():
        assessed=advisory.recommend(scout,reference)
        counts[assessed["decision"]]+=1
    picked=[confirms[0],confirms[len(confirms)//2],confirms[-1]]
    need(len({key(x) for x in picked})==NUM_RESEARCH_120,
         "V321_DISTINCT_CHMV_RESEARCH_TIERS_REQUIRED")
    study=root/"tier120_original"
    study.mkdir(exist_ok=False)
    results=[]
    for order,confirmed in enumerate(picked):
        scout=scouts[key(confirmed)]
        orig=(root/"v290_original"/"cases"/
              ("case_%05d"%confirmed["index"])/"native"/"input.simc")
        need(sha(orig)==confirmed["input_sha256"],
             "V321_ACCEPTED_320_ORIGINAL_INPUT_SHA_MISMATCH")
        folder=study/("candidate_%02d"%order)
        folder.mkdir()
        output=folder/"result.json"
        converted=exact_new_simc_120_input(orig.read_text(encoding="utf8"),
                                           output.resolve())
        assert sorted(re.findall(r"(?m)^gear_\w+_rating=\d+$",converted))==sorted(
               re.findall(r"(?m)^gear_\w+_rating=\d+$",
                          orig.read_text(encoding="utf8")))
        input_path=folder/"input.simc"
        input_path.write_text(converted,encoding="utf8")
        start=time.monotonic()
        completed=subprocess.run([str(binary),str(input_path.resolve())],
                        cwd=binary.parent,stdin=subprocess.DEVNULL,
                        stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                        timeout=240,check=False)
        elapsed=time.monotonic()-start
        (folder/"stdout.txt").write_bytes(completed.stdout)
        (folder/"stderr.txt").write_bytes(completed.stderr)
        need(completed.returncode==0,
             "V321_NEW_SHADOW_SIMC_NATIVE120_EXIT_"+str(completed.returncode))
        need(output.is_file() and 0<output.stat().st_size<50000000,
             "V321_NEW_SHADOW_NATIVE120_JSON_MISSING")
        native=json.loads(output.read_bytes())
        sim=native.get("sim") or {}
        players=sim.get("players") or []
        opts=sim.get("options") or {}
        need(type(native.get("git_revision")) is str and
             doc["revision"].startswith(native["git_revision"]) and
             len(native["git_revision"])>=10 and
             opts.get("iterations")==MIDDLE and
             len(players)==1 and
             str(players[0].get("specialization","")).lower()=="shadow priest",
             "V321_EXACT_SIMC_REV_SPEC_ITERATIONS_REQUIRED")
        dps=((players[0].get("collected_data") or {}).get("dps") or {})
        need(dps.get("count")==119
             and type(dps.get("mean_std_dev")) in (int,float)
             and math.isfinite(dps["mean_std_dev"])
             and dps["mean_std_dev"]>=0
             and type(dps.get("mean")) in (int,float)
             and math.isfinite(dps["mean"]),
             "V321_NATIVE_DPS_SEM_SAMPLE_COUNT_REQUIRED")
        need(key(scout)==key(confirmed)
             and confirmed["simc_seed"]!=opts.get("seed")
             and scout["simc_seed"]!=opts.get("seed"),
             "V321_DISTINCT_SEED_SAME_CURRENT_PROFILE_CHMV")
        row={
          "CHMV":dict(confirmed["target"]),
          "current_new_profile_sha256":doc["source_profile_sha256"],
          "scout35":{"index":scout["index"],"dps":scout["dps_mean"],
                     "SEM":scout["dps_sem"],"samples":scout["samples"],
                     "original_json_sha256":scout["native_sha256"]},
          "intermediate120":{"dps":dps["mean"],"SEM":dps["mean_std_dev"],
                     "samples":dps["count"],"wall_seconds":round(elapsed,6),
                     "simc_seed":opts["seed"],
                     "input_sha256":sha(input_path),
                     "native_json_sha256":sha(output)},
          "confirm320":{"index":confirmed["index"],"dps":confirmed["dps_mean"],
                     "SEM":confirmed["dps_sem"],"samples":confirmed["samples"],
                     "original_json_sha256":confirmed["native_sha256"]},
          "projected_120_sem_from_35":round(
               scout["dps_sem"]*math.sqrt(scout["samples"]/119),8),
          "observed_35_to_120_sem_ratio":
               scout["dps_sem"]/dps["mean_std_dev"],
          "observed_120_to_320_sem_ratio":
               dps["mean_std_dev"]/confirmed["dps_sem"],
        }
        results.append(row)
        print("V321_SHADOW_NEW_PROFILE_REAL_120",json.dumps({
            "CHMV":row["CHMV"],"samples":dps["count"],
            "DPS":dps["mean"],"SEM":dps["mean_std_dev"],
            "wall_seconds":row["intermediate120"]["wall_seconds"]},
            sort_keys=True),flush=True)
    archive=root/"tier120_original_native.zip"
    with zipfile.ZipFile(archive,"w",
                         compression=zipfile.ZIP_DEFLATED,
                         compresslevel=5) as z:
        for f in sorted(study.rglob("*")):
            if f.is_file() and not f.is_symlink():
                z.write(f,arcname=f.relative_to(study))
    return {
      "schema":"v321_new_shadow_real_120_source_locked_research_v1",
      "status":"REAL_NATIVE_3_INDEPENDENT_120_SAME_NEW_PROFILE",
      "new_native_research_calls":len(results),
      "requested_research_iterations":len(results)*MIDDLE,
      "advisory_counts_all_56_scouts":{
          k:counts[k] for k in sorted(counts)},
      "raw_source_from_same_campaign_320_case":True,
      "used_prior_campaign_profile":False,
      "research_120_not_v291_verified_case_cache":True,
      "research_archive_sha256":sha(archive),
      "observations":results,
      "confidence_claim":"NO_SELECTED_FAMILYWISE_95_NO_OPTIMUM",
    }

def main():
    need(os.getenv("P2_V321_NEW_SHADOW_SEM120_ONCE")=="1",
         "V321_EXPLICIT_NEW_SHADOW_NATIVE_ONCE_REQUIRED")
    return harness.main(
        case_id=CASE,expected_spec=EXPECTED,
        output_root=OUT,receipt_path=OUT/"receipt.json",
        required_env="P2_V321_NEW_SHADOW_SEM120_ONCE",
        campaign_schema=SCHEMA,
        post_run_hook=after_both_arms)

if __name__=="__main__":
    main()
