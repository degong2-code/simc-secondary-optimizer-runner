#!/usr/bin/env python3
"""v082: actual Fury plate / dual TWO-HANDED source-backed static CHMV smoke.

This is a bounded archetype-fixture wrapper for the SHARED v061-v066 and
v015-derived v065 engines, not a Fury optimizer or item DB.

One Native for new exact-static G, TWO official-T static-c Native witnesses,
ONE original v015-derived adaptive scout (at most four NEW Native calls).
A talent-adjusted buffed_stats field NEVER replaces the target static c.
"""
from __future__ import annotations
import v128_common_source_profile_emitter as common_emitter
import v129_common_source_fields as common_fields
import v130_source_identity_contract as source_identity

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys

import v046_static_item_cache as static_cache
import v055_simc_item_selection as items
import v061_scenario_contract as scenario
import v062_static_budget_bridge as budgets
import v063_numeric_injection as numeric
import v064_adaptive_evaluator_port as port
import v065_original_scheduler_native_bridge as engine
import v065_v015_scheduler_adapter as scheduler
import v066_profile_neutral_preflight as preflight
import v068_rogue_two_native_probe as pinned
import v078b_elemental_official_generic_native as target_builder

SCHEMA = "v082_fury_dual_twohand_static_CHMV_generic_native_v1"
UPSTREAM_GIT_BLOB = "3225992ed5b754ad5d61e8b785d9d859f1eed1be"
UPSTREAM_CLASS_LINE = 'warrior="MID2_Warrior_Fury"'
ARMOR = "plate"
WEAPON_FORM = "dual_two_handed"
RACE = "dwarf"
SPEC = "fury"
ITERATIONS = 35
NATIVE_MAX = 4
ALL_SLOTS = ("head", "neck", "shoulders", "back", "chest", "wrists",
             "hands", "waist", "legs", "feet", "finger1", "finger2",
             "trinket1", "trinket2", "main_hand", "off_hand")
TIER_SLOTS = ("head", "shoulders", "chest", "hands")
CRAFTED_SLOTS = ("wrists", "off_hand")
TRINKET_SLOTS = ("trinket1", "trinket2")
SOURCE_WEAPON_IDS = {"main_hand":268213, "off_hand":237847}
# This declared F vector is profile fixture-specific; not a generalized
# effect simulator or a conclusion about all flasks.
DECLARED_F = {"crit_rating":0,"haste_rating":165,
              "mastery_rating":0,"versatility_rating":0}
GEM_ID = {"head":"240983", "neck":"240906/240906",
          "wrists":"240906", "waist":"240906",
          "finger1":"240906", "finger2":"240906"}

class Blocked(ValueError): pass

def need(ok, why):
    if not ok:raise Blocked(why)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def read(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf8"))

def persist_if_unchanged(path,data):
    path=pathlib.Path(path)
    if path.exists():
        need(path.read_bytes()==data,"EXISTING_SOURCE_DATA_TAMPERED:"+str(path))
    else:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)

def source_profile(source,folder):
    """Preserve SimC's ORIGINAL Fury APL/talents; use exact source-backed IDs.

    Test fixture normalizes ilvl to 334 and declares fresh options. Does not
    infer full item compatibility, set mechanics, trinket procs or a recipe DB.
    """
    initial_actions,talents=source_identity.verify(
        source,("warrior","fury"),UPSTREAM_GIT_BLOB,
        (UPSTREAM_CLASS_LINE,"spec=fury","race=dwarf","role=attack"),
        min_actions=35,strict_greater=True,
        hash_error="UPSTREAM_FURY_SOURCE_BLOB_DRIFT",
        identity_error="FURY_CLASS_RACE_SPEC_ROLE_DRIFT",
        apl_error="FURY_UPSTREAM_APL_MISSING",
        talents_error="FURY_ONE_TALENT_STRING_REQUIRED",fail=need)
    ids,_=common_fields.equipment(source,ALL_SLOTS,need=need,
        duplicate_prefix="FURY_SOURCE_DUPLICATE_SLOT:",
        missing_id_prefix="FURY_SOURCE_ID_MISSING:")
    need(set(ids)==set(ALL_SLOTS),"FURY_SOURCE_SIXTEEN_SLOTS_REQUIRED")
    need(all(ids[k]==v for k,v in SOURCE_WEAPON_IDS.items()),
         "FURY_SOURCE_DUAL_WEAPON_ID_CHANGED")
    eq={}
    for slot in ALL_SLOTS:
        options={}
        if slot in GEM_ID:options["gem_id"]=GEM_ID[slot]
        if slot in CRAFTED_SLOTS:options["crafted_stats"]="49/36"
        eq[slot]={"slot":slot,"item_id":ids[slot],"ilevel":334,
                  "options":options}
    folder=pathlib.Path(folder).resolve()
    fixed={"race":RACE,"fight_style":"Patchwerk",
           "desired_targets":"1","max_time":"300",
           "vary_combat_length":"0","fixed_time":"1",
           "optimal_raid":"1","threads":"1",
           "iterations":str(ITERATIONS),
           "json2":str(folder/"initial_native"/"result.json"),
           "flask":"flask_of_the_blood_knights_2"}
    fixed.update({"gear_"+key:"700" for key in scenario.STATS})
    reference=common_emitter.emit(
        source,fixed,eq,ALL_SLOTS,
        blank_before_overrides=True)
    need(initial_actions==[line for line in reference.splitlines()
                  if line.startswith("actions")],
         "FURY_ORIGINAL_SIMC_APL_CHANGED")
    need("temporary_enchant=" not in reference,
         "FURY_OIL_EXCLUDED_FROM_FIRST_STRUCTURAL_SMOKE")
    need(len([line for line in reference.splitlines()
              if line.startswith("off_hand=")])==1,
         "FURY_SECOND_TWOHAND_NOT_TRANSMITTED")
    cfg={
      "schema":scenario.SCHEMA,
      "character":{"class":"warrior","spec":SPEC,"race":RACE,
                   "role":"attack","talents":talents[0]},
      "source":{"kind":"user_supplied",
                "profile_sha256":sha(reference.encode("utf8"))},
      "target":{"mode":"derived_ilevel","ilevel":334,
                "manual_total":None,"manual_total_scope":None},
      "equipment":{
          "tier":[eq[x] for x in TIER_SLOTS],
          "special":[],
          "crafted":[eq[x] for x in CRAFTED_SLOTS],
          "trinkets":[eq[x] for x in TRINKET_SLOTS]},
      "consumables":{"gem_budget_J":138,"flask_budget_F":165,
            "special_gem_id":240983,
            "flask":"flask_of_the_blood_knights_2",
            "food":"harandar_celebration",
            "potion":"lights_potential_2",
            "weapon_temporary":None,
            "weapon_temporary_fixed_rating":{k:0 for k in scenario.STATS}},
      "combat":{"fight_style":"Patchwerk","targets":1,
                "duration_seconds":300,"vary_combat_length_pct":0.0,
                "raid_buffs":True,"bloodlust":"on_pull",
                "external_buffs":[],"events":[]},
      "constraints":{
          "min_fraction":{k:0 for k in scenario.STATS},
          "max_fraction":{k:1 for k in scenario.STATS},
          "minimum_rating":{k:0 for k in scenario.STATS}},
      "runtime":{"scout_iterations":35,"confirm_iterations":320,
           "max_native_calls":4,"threads":1,"resume":True,"seed":1}}
    filler=[eq[x] for x in ALL_SLOTS if x not in
                set(TIER_SLOTS)|set(CRAFTED_SLOTS)|set(TRINKET_SLOTS)]
    normalized=scenario.normalize(cfg)
    need(sum(len(cfg["equipment"][kind]) for kind in
             ("tier","special","crafted","trinkets"))+len(filler)==16,
         "EXACT_SIXTEEN_SLOT_SCENARIO_REQUIRED")
    need(sum(DECLARED_F.values())==normalized["budget"]["F"],
         "FIXTURE_STATIC_F_DECLARATION_INCONSISTENT")
    metadata={
       "armor":ARMOR,"race":RACE,"weapon_form":WEAPON_FORM,
       "main_hand_source_id":ids["main_hand"],
       "off_hand_source_id":ids["off_hand"],
       "weapon_types_from_original_simc_profile_not_independently_certified":True,
       "all_equipment_items_source_backed":True,
       "apl_actions_original":len(initial_actions),
       "upstream_profile_git_blob":UPSTREAM_GIT_BLOB,
       "selected_tier_slots":list(TIER_SLOTS),
       "selected_crafted_slots":list(CRAFTED_SLOTS),
       "both_source_weapons_kept":True,
       "ilvl":334,"oil_selected":False,
       "declared_static_F":dict(DECLARED_F),
       "F_attribution_confirmed_independently":False}
    return reference,cfg,filler,metadata

def execute_initial_native(reference,folder,binary,cache_only,summary):
    folder=pathlib.Path(folder)
    folder.mkdir(parents=True,exist_ok=True)
    inp=folder/"input.simc"
    output=folder/"result.json"
    receipt=folder/"native_receipt.json"
    persist_if_unchanged(inp,reference.encode("utf8"))
    if output.exists() or receipt.exists():
        need(output.is_file() and receipt.is_file(),
             "INITIAL_NATIVE_PARTIAL_OR_UNVERIFIED")
        raw=output.read_bytes();proof=read(receipt)
        need(proof["input_sha256"]==sha(inp.read_bytes()) and
             proof["native_json_sha256"]==sha(raw) and
             proof["simc_binary_sha256"]==pinned.BIN_SHA,
             "INITIAL_NATIVE_SHA_IDENTITY_CHANGED")
    else:
        need(not cache_only,"CACHE_ONLY_REFUSES_UNSEEN_INITIAL_NATIVE")
        progress=folder/"INITIAL_ATTEMPT.json"
        if progress.exists():
            need(read(progress).get("attempted")==False,
                 "INITIAL_NATIVE_ALREADY_ATTEMPTED_REQUIRE_EXPLICIT_RECOVERY")
        engine.write_atomic(progress,{"attempted":True,
            "input_sha256":sha(inp.read_bytes()),"binary_sha":pinned.BIN_SHA})
        summary["new_native_this_invocation"]+=1
        process=subprocess.run([str(binary),str(inp.resolve())],
                 cwd=binary.parent,stdin=subprocess.DEVNULL,
                 stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=240)
        (folder/"stdout.txt").write_bytes(process.stdout)
        (folder/"stderr.txt").write_bytes(process.stderr)
        need(process.returncode==0,
             "SIMC_NATIVE_EXIT_"+str(process.returncode)+"_SEE_ORIGINAL_STDERR")
        need(output.is_file(),"INITIAL_NATIVE_JSON2_MISSING")
        raw=output.read_bytes()
        engine.write_atomic(receipt,{
           "input_sha256":sha(inp.read_bytes()),
           "native_json_sha256":sha(raw),
           "simc_binary_sha256":pinned.BIN_SHA})
    doc=json.loads(raw)
    need(doc.get("report_version")=="2.0.0"
         and isinstance(doc.get("git_revision"),str)
         and len(doc["git_revision"])>=7,
         "INITIAL_NATIVE_JSON2_VERSION_OR_REVISION_MISSING")
    numeric.from_native(reference,doc)
    player=doc["sim"]["players"][0]
    dps=(player.get("collected_data") or {}).get("dps",{})
    need(type(dps.get("count")) is int and dps["count"]>=20
         and type(dps.get("mean")) in (int,float)
         and type(dps.get("mean_std_dev")) in (int,float),
         "INITIAL_NATIVE_DPS_OR_SEM_ABSENT")
    summary["first_native_sha256"]=sha(raw)
    summary["first_native_dps_mean"]=dps["mean"]
    summary["first_native_sem"]=dps["mean_std_dev"]
    return raw,doc

def run(upstream,out,binary=None,cache_only=False,*,
        profile_factory=source_profile, expected_slots=16,
        run_schema=SCHEMA,
        plan_status="PASS_UPSTREAM_TWO_WEAPON_STATIC_PLAN_ZERO_NATIVE",
        success_status="PASS_REAL_FURY_TWO_2H_PLATE_FULL_STATIC_GENERIC_NATIVE",
        artifact_prefix="V082",declared_F=None): 
    if declared_F is None:
        declared_F=DECLARED_F
    need(type(declared_F) is dict
         and set(declared_F)==set(scenario.STATS)
         and all(type(v) is int and v>=0 for v in declared_F.values()),
         "DECLARED_STATIC_F_VECTOR_INVALID")
    out=pathlib.Path(out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    target=out/(artifact_prefix+"_RECEIPT.json")
    summary={"schema":run_schema,"status":"BLOCKED_OR_PARTIAL",
       "new_native_this_invocation":0,"maximum_new_native":NATIVE_MAX,
       "global_optimum_proven":False,"new_native_stat_effect_gate":False,
       "official_formula":"T=G+J+F"}
    try:
        source=pathlib.Path(upstream).read_text(encoding="utf8")
        reference,cfg,fillers,origin=profile_factory(source,out)
        normalized=scenario.normalize(cfg)
        need(sum(declared_F.values())==normalized["budget"]["F"],
             "STATIC_F_COMPONENT_SUM_NOT_SCENARIO_F")
        summary.update({"status":plan_status,
            "character":cfg["character"],"origin":origin,
            "scenario_digest":normalized["scenario_digest"],
            "profile_sha256":sha(reference.encode("utf8")),
            "exact_source_backed_item_ids":True,
            "declared_F_vector":declared_F,
            "missing_native_static_expected_before_first_use":True})
        if binary is None:
            engine.write_atomic(target,summary)
            return 0
        binary=pathlib.Path(binary).resolve()
        need(binary.is_file() and sha(binary.read_bytes())==pinned.BIN_SHA,
             "EXACT_SIMC_NATIVE_BINARY_CHANGED")
        seal=out/(artifact_prefix+"_IDENTITY.json")
        identity={"schema":run_schema,"source_sha256":sha(source.encode("utf8")),
            "profile_sha256":sha(reference.encode("utf8")),
            "scenario_digest":normalized["scenario_digest"],
            "simc_binary_sha256":pinned.BIN_SHA,
            "static_F_vector":declared_F,"max_new_native":NATIVE_MAX}
        if seal.exists():
            need(read(seal)==identity,"V082_SOURCE_OR_BINARY_RESUME_DRIFT")
        else:
            need(not (out/"initial_native").exists() and
                 not (out/"official").exists(),
                 "V082_UNSEALED_PREEXISTING_NATIVE_RESULT")
            engine.write_atomic(seal,identity)
        raw,doc=execute_initial_native(reference,out/"initial_native",
                                        binary,cache_only,summary)
        exact=static_cache.empty_cache()
        rows=static_cache.native_records(raw,artifact_id="V082_REAL_FURY_INIT")
        static_cache.merge_native(exact,rows)
        static=budgets.compile_static_budget(normalized,fillers,exact)
        need(static["G_if_complete"] is not None
             and not static["missing_nontrinket_static"]
             and not static["missing_special_fixed_static"]
             and static["budget"]["T_official"] is not None
             and static["budget"]["oil_stays_OUTSIDE_T"] is True,
             "INITIAL_FURY_REAL_NATIVE_EXACT_GJF_INCOMPLETE")
        T=static["budget"]["T_official"]
        G=static["G_if_complete"]
        need(T==G+normalized["budget"]["J"]+normalized["budget"]["F"],
             "FURY_OFFICIAL_T_SUM_OR_POLICY_CHANGED")
        ref_detail=port.verify_profile_binding(normalized,static,reference)
        need(ref_detail["slots_bound"]==expected_slots and ref_detail["two_trinkets_bound"],
             "DUAL_TWOHANDED_SLOTS_OR_TRINKETS_NOT_BOUND")
        summary.update({"status":"PASS_FIRST_REAL_FURY_NATIVE_GJF",
            "G":G,"J":normalized["budget"]["J"],"F":normalized["budget"]["F"],
            "T":T,"initial_native_revision":doc["git_revision"],
            "native_items_ready":True})
        engine.write_atomic(target,summary)
        c1,c2=target_builder.targets(T,static)
        off=out/"official"
        reqs=[port.make_static_chmv_request(normalized,static,reference,
                 pinned.BIN_SHA,doc["git_revision"],x,declared_F,
                 ITERATIONS,off/("candidate_%02d"%i)/"result.json")
               for i,x in enumerate((c1,c2))]
        need(all(sum(req["raw_gear_override"].values())==
                 G+normalized["budget"]["J"] for req in reqs),
             "OFFICIAL_RAW_CHMV_DUPLICATE_F_OR_BUDGET")
        official_id={"schema":SCHEMA,
           "first_native_json2_sha256":summary["first_native_sha256"],
           "requests":[r["case_key"] for r in reqs],
           "rating_semantics":"STATIC_CHMV_C_V1",
           "binary_sha256":pinned.BIN_SHA,"revision":doc["git_revision"]}
        off.mkdir(parents=True,exist_ok=True)
        official_seal=off/"OFFICIAL_IDENTITY.json"
        if official_seal.exists():
            need(read(official_seal)==official_id,
                 "OFFICIAL_FURY_STATIC_C_IDENTITY_DRIFT")
        else:
            need(not any((off/("candidate_%02d"%i)).exists() for i in (0,1))
                 and not (off/"adaptive_00").exists(),
                 "UNSEALED_FURY_OFFICIAL_RESULTS")
            engine.write_atomic(official_seal,official_id)
        progress_path=off/"V065_PROGRESS.json"
        progress={"schema":SCHEMA,"identity":official_id,"native_attempts":0}
        if progress_path.exists():
            old=read(progress_path)
            need(old.get("schema")==SCHEMA and old.get("identity")==official_id
                 and type(old.get("native_attempts")) is int
                 and 0<=old["native_attempts"]<=3,
                 "FURY_NATIVE_PROGRESS_CHANGED")
            progress["native_attempts"]=old["native_attempts"]
        else:engine.write_atomic(progress_path,progress)
        scored=[]
        for i,req in enumerate(reqs):
            result=engine.execute_one(req,{"native_revision":doc["git_revision"]},
                  binary,off/("candidate_%02d"%i),progress,cache_only=cache_only)
            need(result["status"]=="PASS_NATIVE_DPS_AND_STATIC_CHMV_INPUT"
                 and result["target"]==result["static_rating_verified"]
                 and sum(result["target"].values())==T
                 and result["dps_samples"]>=20,
                 "FURY_OFFICIAL_STATIC_C_OR_DPS_NOT_VERIFIED")
            scored.append(result)
            summary["new_native_this_invocation"]+=int(result["source"]=="NEW_NATIVE")
            summary["status"]="PARTIAL_FURY_OFFICIAL_NATIVE"
            summary["official_native_completed"]=len(scored)
            engine.write_atomic(target,summary)
        attest=[]
        for i,obs in enumerate(scored):
            folder=off/("candidate_%02d"%i)
            raw_evidence=(folder/"result.json").read_bytes()
            attest.append({
                "input":(folder/"input.simc").read_text("utf8"),
                "native":json.loads(raw_evidence),
                "raw_native_json":raw_evidence,
                "input_sha256":obs["input_sha256"],
                "native_json_sha256":obs["native_json_sha256"]})
        prepared=preflight.prepare_static(cfg,fillers,exact,reference,attest,
                           pinned.BIN_SHA,declared_F)
        need(prepared["summary"]["status"]=="READY_STATIC_CHMV_PROFILE_SCOPED"
             and prepared["summary"]["T_official"]==T,
             "COMMON_V066_FURY_STATIC_NATIVE_NOT_READY")
        proposal=preflight.propose_next_static(prepared,ITERATIONS,
                 off/"adaptive_00"/"result.json",step=100)
        case=proposal["case"]
        need(case["target"] not in (c1,c2) and
             case["rating_semantics"]=="STATIC_CHMV_C_V1" and
             sum(case["target"].values())==T,
             "FURY_COMMON_V015_ADAPTIVE_TARGET_NOT_DISTINCT")
        result=engine.execute_one(case,prepared["calibration"],binary,
                    off/"adaptive_00",progress,cache_only=cache_only)
        need(result["status"]=="PASS_NATIVE_DPS_AND_STATIC_CHMV_INPUT"
             and result["static_rating_verified"]==case["target"]
             and result["dps_samples"]>=20,
             "FURY_ADAPTIVE_SIMC_STATIC_CHMV_MISMATCH")
        summary["new_native_this_invocation"]+=int(result["source"]=="NEW_NATIVE")
        state=scheduler.initial_state(normalized,static,
              prepared["prior_observations"],step=100,scout_max=2)
        accepted=scheduler.accept_scout(state,case,result)
        need(accepted["completed_new_scouts"]==1,
             "SHARED_ADAPTIVE_POLICY_NOT_ACCEPTED")
        need(progress["native_attempts"]+1<=NATIVE_MAX,
             "FOUR_NATIVE_CAP_EXCEEDED")
        summary.update({
          "status":success_status,
          "native_attempts_total":progress["native_attempts"]+1,
          "cache_only_replay":cache_only,
          "official_native":[{"target_static_c":x["target"],
               "verified_static_c":x["static_rating_verified"],
               "buffed_simc_observed":x["rating_actual"],
               "dps_mean":x["dps_mean"],"dps_sem":x["dps_sem"],
               "dps_samples":x["dps_samples"],"source":x["source"],
               "native_json_sha256":x["native_json_sha256"]}
               for x in scored],
          "adaptive_result":{
               "target_static_c":result["target"],
               "verified_static_c":result["static_rating_verified"],
               "buffed_simc_observed":result["rating_actual"],
               "dps_mean":result["dps_mean"],"dps_sem":result["dps_sem"],
               "dps_samples":result["dps_samples"],"source":result["source"],
               "native_json_sha256":result["native_json_sha256"]},
          "two_weapon_slots_preserved":expected_slots==16,
          "weapon_form":origin.get("weapon_form"),
          "v066_preflight_status":prepared["summary"]["status"],
          "v015_scout_order_reused":True,
          "original_v015_v016_merged":False,
          "global_optimum_proven":False})
        engine.write_atomic(out/(artifact_prefix+"_STATIC_CACHE.json"),exact)
        engine.write_atomic(out/(artifact_prefix+"_SCENARIO.json"),cfg)
        engine.write_atomic(out/(artifact_prefix+"_FILLERS.json"),fillers)
        persist_if_unchanged(out/(artifact_prefix+"_REFERENCE.simc"),reference.encode("utf8"))
    except Exception as exc:
        summary["status"]="BLOCKED_OR_PARTIAL"
        summary["error"]=type(exc).__name__+":"+str(exc)
    engine.write_atomic(target,summary)
    print(artifact_prefix,summary["status"],"new_native",
          summary["new_native_this_invocation"],"error",
          summary.get("error"),flush=True)
    return 0 if summary["status"].startswith("PASS") else 3

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    p.add_argument("--binary",type=pathlib.Path)
    p.add_argument("--cache-only",action="store_true")
    x=p.parse_args(argv)
    return run(x.upstream,x.out,x.binary,x.cache_only)

if __name__=="__main__":sys.exit(main())
