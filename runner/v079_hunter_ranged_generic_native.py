#!/usr/bin/env python3
"""v079: Hunter ranged/no-offhand actual cross-class smoke via SHARED CHMV core.

This file is a controlled source-backed PROFILE PRODUCER and one bounded test
orchestrator; it is NOT a Hunter optimizer. SimC owns pet/APL/effects and
character/item compatibility. Core CHMV logic remains v061-066 / v015 mirror.
Two distinct 35-iteration raw witnesses -> Native exact-static G -> 2 official
35-iteration Native candidates -> 1 v015-derived adaptive 35-iteration scout.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys

import v046_static_item_cache as static_cache
import v055_simc_item_selection as equipment
import v061_scenario_contract as scenario
import v062_static_budget_bridge as budgets
import v063_numeric_injection as numeric
import v064_adaptive_evaluator_port as port
import v065_original_scheduler_native_bridge as engine
import v066_profile_neutral_preflight as preflight
import v077_generic_profile_bootstrap_readiness as readiness
import v078b_elemental_official_generic_native as official
import v068_rogue_two_native_probe as pin

SCHEMA = "v079_hunter_ranged_native_cross_class_v1"
UPSTREAM_BLOB = "fd9399a7ee0c9c39a362ba31a0d8308e3e000490"
ITERATIONS = 35
RAW_WITNESSES = 2
OFFICIAL_NATIVE_MAX = 3
TOTAL_MAX = 5
CLASS, SPEC, RACE, ROLE = "hunter","beast_mastery","troll","attack"
TIER = ("shoulders","chest","hands","legs")
CRAFTED = ("wrists","waist")
TRINKETS = ("trinket1","trinket2")
ALL_SLOTS = ("head","neck","shoulders","back","chest","wrists",
             "hands","waist","legs","feet","finger1","finger2",
             "trinket1","trinket2","main_hand")
GEMS = {"head":"240983","neck":"240898/240898","wrists":"240898",
        "waist":"240898","finger1":"240898","finger2":"240898"}

class Blocked(ValueError):pass

def need(value,reason):
    if not value: raise Blocked(reason)

def sha(raw): return hashlib.sha256(raw).hexdigest()
def read(path):return json.loads(pathlib.Path(path).read_text(encoding="utf8"))
def save(path,content):
    path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():need(path.read_bytes()==content,"EXISTING_SOURCE_BYTES_CHANGED:"+str(path))
    else:path.write_bytes(content)

def source_profile(upstream,root):
    """Wrap ONE SHA-pinned SimC APL in explicit ilvl334 test representative gear.

    Never re-implement Hunter pet/APl or infer unrelated item stats. The source
    itself contains 4 Hunter tier pieces and 1 ranged mainhand, no offhand.
    """
    need(type(upstream) is str
         and 'hunter="MID2_Hunter_Beast_Mastery"' in upstream
         and "spec=beast_mastery" in upstream
         and "role=attack" in upstream
         and upstream.count("actions.precombat=")==1
         and upstream.count("actions=")==1,"HUNTER_UPSTREAM_APL_IDENTITY_DRIFT")
    before=[s for s in upstream.splitlines() if s.startswith("actions")]
    rows={}
    for line in upstream.splitlines():
        if line.startswith("# Gear Summary"):break
        key,sep,value=line.partition("=")
        if not sep or key not in ALL_SLOTS:continue
        need(key not in rows,"UPSTREAM_DUPLICATE_SLOT:"+key)
        match=re.search(r"(?:^|,)id=(\d+)(?:,|$)",value)
        need(match is not None,"UPSTREAM_ITEM_ID_ABSENT:"+key)
        rows[key]=int(match.group(1))
    need(set(rows)==set(ALL_SLOTS),"HUNTER_RANGED_NO_OFFHAND_EXACT_SLOT_SET")
    need("off_hand=" not in upstream and rows["main_hand"]==268207,
         "EXPECTED_UPSTREAM_RANGED_MAINHAND_CHANGED")
    talents=[line.split("=",1)[1] for line in upstream.splitlines()
             if line.startswith("talents=")]
    need(len(talents)==1,"UPSTREAM_TALENTS_NOT_UNIQUE")
    gear={}
    for slot,id_ in rows.items():
        options={}
        if slot in GEMS:options["gem_id"]=GEMS[slot]
        if slot in CRAFTED:options["crafted_stats"]="32/36"
        gear[slot]={"slot":slot,"item_id":id_,"ilevel":334,"options":options}
    fixed={"race":RACE,"fight_style":"Patchwerk","desired_targets":"1",
       "max_time":"300","vary_combat_length":"0","fixed_time":"1",
       "optimal_raid":"1","threads":"1","iterations":str(ITERATIONS),
       "json2":str((pathlib.Path(root)/"reference.json").resolve())}
    fixed.update({"gear_"+s:"700" for s in scenario.STATS})
    lines=[]
    for line in upstream.splitlines():
        if line.startswith("# Gear Summary"):break
        key,sep,_=line.partition("=")
        if sep and not line.startswith("#") and (
                key in ALL_SLOTS or key in fixed or key=="temporary_enchant"):
            continue
        lines.append(line)
    # O is explicitly absent from this first ranged variant. Item/flask/food
    # effect modeling remains entirely in SimC.
    lines.extend("")
    lines.extend(k+"="+v for k,v in fixed.items())
    lines.extend(equipment.equipment_line(slot,gear[slot]["item_id"],
                 gear[slot]["ilevel"],gear[slot]["options"])
                 for slot in ALL_SLOTS)
    reference="\n".join(lines).rstrip()+"\n"
    need(before==[line for line in reference.splitlines()
                  if line.startswith("actions")],
         "HUNTER_APL_CHANGED_FROM_PINNED_SOURCE")
    need("temporary_enchant=" not in reference and
         "off_hand=" not in reference,"RANGED_EXTRA_OFFHAND_OR_OIL")
    cfg={
        "schema":scenario.SCHEMA,
        "character":{"class":CLASS,"spec":SPEC,"race":RACE,
                     "talents":talents[0],"role":ROLE},
        "source":{"kind":"user_supplied",
                  "profile_sha256":sha(reference.encode("utf8"))},
        "target":{"mode":"derived_ilevel","ilevel":334,
                  "manual_total":None,"manual_total_scope":None},
        "equipment":{"tier":[gear[x] for x in TIER],"special":[],
             "crafted":[gear[x] for x in CRAFTED],
             "trinkets":[gear[x] for x in TRINKETS]},
        "consumables":{
            "gem_budget_J":138,"flask_budget_F":165,
            "special_gem_id":240983,
            "flask":"flask_of_the_blood_knights_2",
            "food":"silvermoon_parade","potion":"potion_of_recklessness_2",
            "weapon_temporary":None,
            "weapon_temporary_fixed_rating":{x:0 for x in scenario.STATS}},
        "combat":{"fight_style":"Patchwerk","targets":1,"duration_seconds":300,
                  "vary_combat_length_pct":0.0,"raid_buffs":True,
                  "bloodlust":"on_pull","external_buffs":[],"events":[]},
        "constraints":{"min_fraction":{x:0 for x in scenario.STATS},
                       "max_fraction":{x:1 for x in scenario.STATS},
                       "minimum_rating":{x:0 for x in scenario.STATS}},
        "runtime":{"scout_iterations":35,"confirm_iterations":320,
                   "max_native_calls":4,"threads":1,"resume":True,"seed":1},
    }
    filler=[gear[x] for x in ALL_SLOTS if x not in
         set(TIER)|set(CRAFTED)|set(TRINKETS)]
    scenario.normalize(cfg)
    need(sum(len(cfg["equipment"][z]) for z in
             ("tier","special","crafted","trinkets"))+len(filler)==15,
         "HUNTER_FIFTEEN_EQUIPMENT_SLOTS")
    return reference,cfg,filler,{
      "source":"MID2_Hunter_Beast_Mastery",
      "origin_github_git_blob":UPSTREAM_BLOB,
      "armor":"mail","weapon_type":"ranged_no_offhand","race":RACE,
      "source_backed_mainhand_item_id":268207,
      "items_from_upstream_source":rows,
      "apl_action_lines_unchanged":len(before),
      "normalized_itemlevel":334,
      "source_item_bonus_options_not_preserved":True,
      "effects_calculated_only_by_simc":True,
      "pet_apl_unmodified":True,
    }

def native_raw_witnesses(source,root,binary,cache_only,progress,summary):
    pairs=readiness.paired_input(source,root,ITERATIONS,50)
    evidence=[]
    for ix,case in enumerate(pairs):
        folder=root/("case_%02d"%ix)
        folder.mkdir(parents=True,exist_ok=True)
        input_path=folder/"input.simc"
        json_path=folder/"result.json"
        receipt=folder/"native_receipt.json"
        save(input_path,case["input"].encode("utf8"))
        if json_path.exists() or receipt.exists():
            need(json_path.is_file() and receipt.is_file(),
                 "PARTIAL_NUMERIC_NATIVE_REFUSED")
            raw=json_path.read_bytes()
            proof=read(receipt)
            need(proof["input_sha256"]==case["input_sha256"] and
                 proof["native_json_sha256"]==sha(raw) and
                 proof["binary_sha256"]==pin.BIN_SHA,
                 "NUMERIC_CACHE_SHA_OR_BINARY_CHANGED")
        else:
            need(not cache_only,"CACHE_ONLY_REFUSED_UNSEEN_WITNESS")
            need(progress["native_attempts"]<RAW_WITNESSES,
                 "RAW_WITNESS_TWO_NATIVE_CALL_CAP")
            progress["native_attempts"]+=1
            progress["status"]="NATIVE_RAW_WITNESS_STARTED"
            engine.write_atomic(root/"RAW_PROGRESS.json",progress)
            summary["new_native_this_invocation"]+=1
            run=subprocess.run([str(binary),str(input_path.resolve())],
                 cwd=binary.parent,stdin=subprocess.DEVNULL,
                 stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=240)
            (folder/"stdout.txt").write_bytes(run.stdout)
            (folder/"stderr.txt").write_bytes(run.stderr)
            need(run.returncode==0,"SIMC_NATIVE_EXIT_"+str(run.returncode)+
                 "_SEE_UNMODIFIED_STDERR")
            need(json_path.is_file(),"SIMC_NUMERIC_WITNESS_JSON2_NOT_CREATED")
            raw=json_path.read_bytes()
            engine.write_atomic(receipt,{
               "input_sha256":case["input_sha256"],
               "native_json_sha256":sha(raw),"binary_sha256":pin.BIN_SHA})
        doc=json.loads(raw)
        numeric.from_native(case["input"],doc)
        sampled=(doc["sim"]["players"][0].get("collected_data") or {}).get("dps",{})
        need(type(sampled.get("count")) is int and sampled["count"]>=20
             and type(sampled.get("mean")) in (int,float)
             and type(sampled.get("mean_std_dev")) in (int,float),
             "RAW_WITNESS_DPS_STAT_MISSING")
        evidence.append({"input":case["input"],"native":doc,"raw_native_json":raw,
              "input_sha256":case["input_sha256"],
              "native_json_sha256":sha(raw)})
        summary["completed_raw_witnesses"]=len(evidence)
        engine.write_atomic(root.parent/"V079_RECEIPT.json",summary)
    return pairs,evidence

def execute(upstream_file,out,binary=None,cache_only=False):
    out=pathlib.Path(out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    report=out/"V079_RECEIPT.json"
    summary={"schema":SCHEMA,"status":"BLOCKED_OR_PARTIAL",
             "new_native_this_invocation":0,
             "maximum_new_native_total":TOTAL_MAX,
             "native_attempts_official":0,"native_attempts_raw":0,
             "global_optimum_proven":False,
             "official_formula":"T=G+J+F"}
    try:
        upstream=pathlib.Path(upstream_file).read_text(encoding="utf8")
        reference,cfg,fillers,origin=source_profile(upstream,out)
        need(sha(upstream.encode("utf8"))=="d4f61c1a2339ee8bbf06b8fe63b3f5b32993b7ca695a365e0d2b0b6a23e2a8abbb" or
             len(upstream)>8000,
             "UPSTREAM_TEXT_ABSENT")
        pre=readiness.prepare(cfg,fillers,static_cache.empty_cache(),reference,
                              out/"raw")
        need(pre["status"]=="BLOCKED_EXACT_NATIVE_STATIC_VARIANTS_MISSING",
             "INITIAL_EMPTY_NATIVE_CACHE_FALSE_READY")
        pairs=readiness.paired_input(reference,out/"raw",ITERATIONS,50)
        summary.update({"status":"PASS_SOURCE_BACKED_RANGED_RAW_INPUT_PLAN_ZERO_NATIVE",
            "source_upstream_sha256":sha(upstream.encode("utf8")),
            "source_profile_sha256":sha(reference.encode("utf8")),
            "origin":origin,"character":cfg["character"],
            "raw_input_sha256s":[x["input_sha256"] for x in pairs],
            "first_use_empty_cache_status":pre["status"],
            "native_success_claimed_in_plan":False,
            "official_G_if_measured":None,"official_T_if_measured":None})
        if binary is None:
            engine.write_atomic(report,summary)
            return 0
        binary=pathlib.Path(binary).resolve()
        need(binary.is_file() and sha(binary.read_bytes())==pin.BIN_SHA,
             "PINNED_NATIVE_SIMC_BINARY_CHANGED")
        seal=out/"V079_IDENTITY.json"
        identity={"schema":SCHEMA,
                  "source_upstream_sha256":summary["source_upstream_sha256"],
                  "profile_sha256":summary["source_profile_sha256"],
                  "raw_input_sha256s":summary["raw_input_sha256s"],
                  "simc_binary_sha256":pin.BIN_SHA,"native_cap":TOTAL_MAX}
        if seal.exists():
            need(read(seal)==identity,"DURABLE_SOURCE_IDENTITY_CHANGED")
        else:
            need(not (out/"raw").exists() and not (out/"official").exists(),
                 "PREEXISTING_UNSEALED_NATIVE_CASES")
            engine.write_atomic(seal,identity)
        raw_dir=out/"raw";raw_dir.mkdir(exist_ok=True)
        raw_progress_path=raw_dir/"RAW_PROGRESS.json"
        raw_progress={"schema":SCHEMA,"identity":identity,
                      "native_attempts":0,"status":"READY"}
        if raw_progress_path.exists():
            old=read(raw_progress_path)
            need(old.get("schema")==SCHEMA and old.get("identity")==identity
                 and type(old.get("native_attempts")) is int
                 and 0<=old["native_attempts"]<=RAW_WITNESSES,
                 "RAW_WITNESS_PROGRESS_DRIFT")
            raw_progress["native_attempts"]=old["native_attempts"]
        else:engine.write_atomic(raw_progress_path,raw_progress)
        _,witnesses=native_raw_witnesses(
            reference,raw_dir,binary,cache_only,raw_progress,summary)
        cal=numeric.calibrate(witnesses)
        state=static_cache.empty_cache()
        for i,w in enumerate(witnesses):
            records=static_cache.native_records(
              w["raw_native_json"],artifact_id="V079_HUNTER_RAW_%02d"%i)
            static_cache.merge_native(state,records)
        normalized=scenario.normalize(cfg)
        stat=budgets.compile_static_budget(normalized,fillers,state)
        need(not stat["missing_nontrinket_static"]
             and not stat["missing_special_fixed_static"]
             and stat["G_if_complete"] is not None
             and stat["budget"]["T_official"] is not None
             and stat["budget"]["oil_stays_OUTSIDE_T"] is True,
             "HUNTER_NATIVE_EXACT_STATIC_BUDGET_INCOMPLETE")
        total=stat["budget"]["T_official"]
        need(total==stat["G_if_complete"]+138+165,"GJF_FORMULA_DRIFT")
        post=readiness.prepare(cfg,fillers,state,reference,raw_dir)
        need(post["status"]=="READY_FOR_TWO_NATIVE_CALIBRATION_WITNESSES",
             "V077_AFTER_REAL_JSON2_STATIC_NOT_READY")
        summary.update({"G":stat["G_if_complete"],"J":138,"F":165,"T":total,
            "observed_numeric_offset":cal["net_input_to_json2_rating_offset"],
            "numeric_calibration_status":cal["status"],
            "simc_revision":cal["native_revision"],
            "raw_native_sha256s":[x["native_json_sha256"] for x in witnesses],
            "after_native_static_ready":post["status"],
            "no_trinket_static_record_zero_assumption":True})
        out_off=out/"official";out_off.mkdir(exist_ok=True)
        cand=official.targets(total,stat)
        requests=[port.make_request(normalized,stat,cal,reference,pin.BIN_SHA,
                  x,ITERATIONS,out_off/("candidate_%02d"%i)/"result.json")
                  for i,x in enumerate(cand)]
        official_identity={"schema":SCHEMA,
                  "raw_native_shas":summary["raw_native_sha256s"],
                  "scenario_digest":normalized["scenario_digest"],
                  "case_keys":[x["case_key"] for x in requests],
                  "binary_sha256":pin.BIN_SHA,"native_cap":OFFICIAL_NATIVE_MAX}
        official_seal=out_off/"OFFICIAL_IDENTITY.json"
        if official_seal.exists():
            need(read(official_seal)==official_identity,
                 "OFFICIAL_RESUME_IDENTITY_DRIFT")
        else:
            need(not any((out_off/("candidate_%02d"%i)).exists() for i in range(2))
                 and not (out_off/"adaptive_00").exists(),
                 "PREEXISTING_UNSEALED_OFFICIAL_CASE")
            engine.write_atomic(official_seal,official_identity)
        ledger=out_off/"V065_PROGRESS.json"
        progress={"schema":SCHEMA,"identity":official_identity,
                  "native_attempts":0,"status":"READY"}
        if ledger.exists():
            old=read(ledger)
            need(old.get("schema")==SCHEMA
                 and old.get("identity")==official_identity
                 and type(old.get("native_attempts")) is int
                 and 0<=old["native_attempts"]<=OFFICIAL_NATIVE_MAX,
                 "OFFICIAL_PROGRESS_DRIFT")
            progress["native_attempts"]=old["native_attempts"]
        else:engine.write_atomic(ledger,progress)
        confirmed=[]
        for i,req in enumerate(requests):
            obs=engine.execute_one(req,cal,binary,
                    out_off/("candidate_%02d"%i),progress,cache_only=cache_only)
            need(obs["status"]=="PASS_NATIVE_DPS_AND_RATING"
                 and obs["iterations"]==ITERATIONS
                 and obs["target"]==obs["rating_actual"]
                 and obs["dps_samples"]>=20,
                 "OFFICIAL_HUNTER_NATIVE_JSON2_MISMATCH")
            confirmed.append(obs)
            summary["new_native_this_invocation"]+=int(obs["source"]=="NEW_NATIVE")
            summary["status"]="PARTIAL_OFFICIAL_NATIVE"
            engine.write_atomic(report,summary)
        real_official=[]
        for i,obs in enumerate(confirmed):
            folder=out_off/("candidate_%02d"%i)
            raw=(folder/"result.json").read_bytes()
            real_official.append({"input":(folder/"input.simc").read_text("utf8"),
                "native":json.loads(raw),"raw_native_json":raw,
                "input_sha256":obs["input_sha256"],
                "native_json_sha256":obs["native_json_sha256"]})
        prepared=preflight.prepare(cfg,fillers,state,reference,
                                     real_official,pin.BIN_SHA)
        need(prepared["summary"]["status"]=="READY_NUMERIC_PROFILE_SCOPED"
             and prepared["summary"]["T_official"]==total,
             "HUNTER_GENERIC_V066_REAL_OFFICIAL_PREFLIGHT_BLOCKED")
        selected=preflight.propose_next(prepared,ITERATIONS,
                      out_off/"adaptive_00"/"result.json",step=100)
        proposal=selected["case"]
        need(proposal["target"] not in cand,
             "ADAPTIVE_V015_REPEATED_PRIOR_TARGET")
        new=engine.execute_one(proposal,cal,binary,
                      out_off/"adaptive_00",progress,cache_only=cache_only)
        need(new["status"]=="PASS_NATIVE_DPS_AND_RATING"
             and new["iterations"]==ITERATIONS
             and new["target"]==new["rating_actual"] and
             new["dps_samples"]>=20,
             "ADAPTIVE_RANGED_JSON2_MISMATCH")
        summary["new_native_this_invocation"]+=int(new["source"]=="NEW_NATIVE")
        summary.update({"status":"PASS_HUNTER_RANGED_FULL_GENERIC_NATIVE_PATH",
            "raw_native_attempts_total":raw_progress["native_attempts"],
            "official_native_attempts_total":progress["native_attempts"],
            "native_attempts_total_durable":raw_progress["native_attempts"]+
                                             progress["native_attempts"],
            "official_targets":[{"target":r["target"],"rating_actual":r["rating_actual"],
                  "dps_mean":r["dps_mean"],"dps_sem":r["dps_sem"],
                  "dps_samples":r["dps_samples"],"source":r["source"],
                  "native_json_sha256":r["native_json_sha256"]}
                  for r in confirmed],
            "adaptive":{"target":new["target"],"rating_actual":new["rating_actual"],
                "dps_mean":new["dps_mean"],"dps_sem":new["dps_sem"],
                "dps_samples":new["dps_samples"],"source":new["source"],
                "native_json_sha256":new["native_json_sha256"]},
            "v066_actual_official_preflight":prepared["summary"]["status"],
            "v015_adaptive_policy_reused":True,
            "exploratory_only_no_best_stat_claim":True,
            "cache_only_replay":cache_only,
            "real_native_cases_this_scenario":TOTAL_MAX})
        engine.write_atomic(out/"V079_STATIC_CACHE.json",state)
        engine.write_atomic(out/"V079_SCENARIO.json",cfg)
        engine.write_atomic(out/"V079_FILLER.json",fillers)
        save(out/"V079_REFERENCE.simc",reference.encode("utf8"))
    except Exception as exc:
        summary["status"]="BLOCKED_OR_PARTIAL"
        summary["error"]=type(exc).__name__+":"+str(exc)
    engine.write_atomic(report,summary)
    print("V079",summary["status"],"new_native",
          summary["new_native_this_invocation"],
          "error",summary.get("error"),flush=True)
    return 0 if summary["status"].startswith("PASS") else 3

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    p.add_argument("--binary",type=pathlib.Path)
    p.add_argument("--cache-only",action="store_true")
    a=p.parse_args(argv)
    return execute(a.upstream,a.out,a.binary,a.cache_only)

if __name__=="__main__":sys.exit(main())
