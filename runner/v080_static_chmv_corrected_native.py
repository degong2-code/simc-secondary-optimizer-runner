#!/usr/bin/env python3
"""v080: correct static CHMV semantics using OLD real Hunter numeric evidence.

Two new 35-iteration Native candidates measure DPS with requested STATIC c,
not by forcing talent-inflated JSON2 buffed_stats to equal c. This route
reuses v061/v062 budget, v063 static render, v064 evaluator and v065
durable Native/cached result execution. No APL/effect/proc modeling.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, sys

import v046_static_item_cache as native_cache
import v061_scenario_contract as scenario
import v062_static_budget_bridge as budget
import v063_numeric_injection as numeric
import v064_adaptive_evaluator_port as evaluator
import v065_original_scheduler_native_bridge as engine
import v079_hunter_ranged_generic_native as hunter
import v079b_hunter_empirical_affine_recovery as previous
import v078b_elemental_official_generic_native as old_targets
import v068_rogue_two_native_probe as pinned

SCHEMA="v080_static_CHMV_pre_talent_native_corrected_contract_v1"
ITERATIONS=35
MAX_NEW_NATIVE=2

class Blocked(ValueError):pass
def need(ok,reason):
    if not ok:raise Blocked(reason)
def read(path):return json.loads(pathlib.Path(path).read_text(encoding="utf8"))
def sha(raw):return hashlib.sha256(raw).hexdigest()

def declared_F_vector(normalized):
    """Explicit consumable fixture attribution, NOT reverse-engineered from buffed.

    This particular Hunter tested flask is represented by a declared +165
    haste. This is caller-supplied per scenario, never class hardcoded
    numeric model. Other flasks require their own declared static vector.
    """
    need(normalized["scenario"]["character"]["class"]=="hunter"
         and normalized["scenario"]["consumables"]["flask"]==
                 "flask_of_the_blood_knights_2",
         "V080_FIXTURE_F_VECTOR_APPLIES_ONLY_TO_DECLARED_HUNTER_FLASK")
    F={k:0 for k in scenario.STATS}
    F["haste_rating"]=165
    need(sum(F.values())==normalized["budget"]["F"],
         "DECLARED_FLASK_COMPONENT_DOES_NOT_MATCH_F")
    return F

def source_and_prior(upstream_file,parent,out):
    content=pathlib.Path(upstream_file).read_text(encoding="utf8")
    ref,cfg,fill,origin=hunter.source_profile(content,out)
    stable=numeric.input_parts(ref)["stable_sha256"]
    real=previous.history(parent,stable)
    rev=real[0]["native"]["git_revision"]
    need(real[1]["native"]["git_revision"]==rev,"OLD_REAL_NATIVE_VERSION_DRIFT")
    records=native_cache.empty_cache()
    for i,w in enumerate(real):
        native_cache.merge_native(records,native_cache.native_records(
          w["raw_native_json"],artifact_id="V080_REUSED_V079_REAL_%02d"%i))
    normalized=scenario.normalize(cfg)
    stat=budget.compile_static_budget(normalized,fill,records)
    need(stat["G_if_complete"] is not None and
         not stat["missing_nontrinket_static"] and
         not stat["missing_special_fixed_static"],
         "EXACT_G_SOURCE_NOT_RESOLVED")
    T=stat["budget"]["T_official"]
    need(T==stat["G_if_complete"]+normalized["budget"]["J"]+
          normalized["budget"]["F"] and
         stat["budget"]["oil_stays_OUTSIDE_T"],
         "OFFICIAL_STATIC_T_FORMULA_BROKEN")
    F=declared_F_vector(normalized)
    need(origin["weapon_type"]=="ranged_no_offhand" and
         origin["pet_apl_unmodified"],
         "HUNTER_SOURCE_PROFILE_DRIFT")
    return ref,cfg,fill,normalized,stat,real,rev,F,origin

def run(upstream,parent,out,binary=None,cache_only=False):
    out=pathlib.Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    receipt=out/"V080_RECEIPT.json"
    state={"schema":SCHEMA,"status":"BLOCKED_OR_PARTIAL",
           "new_native_this_invocation":0,"native_limit":MAX_NEW_NATIVE,
           "global_optimum_proven":False,
           "prior_v079b_buffed_target_claim_withdrawn":True,
           "original_v015_v016_integrated":False}
    try:
        (ref,cfg,fill,normalized,stat,old,rev,F,origin)=source_and_prior(
            upstream,parent,out)
        T=stat["budget"]["T_official"]
        a,b=old_targets.targets(T,stat)
        targets=(a,b)
        reqs=[evaluator.make_static_chmv_request(
              normalized,stat,ref,pinned.BIN_SHA,rev,t,F,
              ITERATIONS,out/("static_%02d"%i)/"result.json")
              for i,t in enumerate(targets)]
        need(all(sum(r["raw_gear_override"].values())==
                 stat["G_if_complete"]+normalized["budget"]["J"]
                 for r in reqs),"RAW_INPUT_G_PLUS_J_BUDGET_DRIFT")
        state.update({"status":"PASS_STATIC_CHMV_SOURCE_PROOF_AND_NEW_INPUT_PLAN",
          "old_native_reused_with_exact_SHA":2,
          "original_native_sha256s":[x["native_json_sha256"] for x in old],
          "class":cfg["character"]["class"],"race":cfg["character"]["race"],
          "weapon":"ranged_no_offhand",
          "G":stat["G_if_complete"],"J":normalized["budget"]["J"],
          "F":normalized["budget"]["F"],"T":T,
          "F_declared_static_vector":F,
          "candidate_static_targets":[r["target"] for r in reqs],
          "candidate_raw_gear_plus_gems":[r["raw_gear_override"] for r in reqs],
          "legacy_buffed_field_not_static_target":True,
          "talent_effects_calculated_only_by_SimC":True,
          "oil_excluded_from_T":True,
          "native_revision":rev})
        if binary is not None:
            binary=pathlib.Path(binary).resolve()
            need(binary.is_file() and sha(binary.read_bytes())==pinned.BIN_SHA,
                 "EXACT_SIMC_BINARY_SHA_CHANGED")
            seal=out/"V080_IDENTITY.json"
            identity={"schema":SCHEMA,
                 "native_revision":rev,
                 "prior_original_real_native_sha":state["original_native_sha256s"],
                 "request_keys":[r["case_key"] for r in reqs],
                 "simc_binary_sha256":pinned.BIN_SHA,
                 "rating_semantics":"STATIC_CHMV_C_V1"}
            if seal.exists():
                need(read(seal)==identity,"V080_NATIVE_RESUME_IDENTITY_CHANGED")
            else:
                need(not any((out/("static_%02d"%i)).exists()
                        for i in range(2)),"NATIVE_CASE_PREEXISTS_WITHOUT_SEAL")
                engine.write_atomic(seal,identity)
            progress_file=out/"V065_PROGRESS.json"
            progress={"schema":SCHEMA,"identity":identity,"native_attempts":0}
            if progress_file.exists():
                old_progress=read(progress_file)
                need(old_progress.get("schema")==SCHEMA
                     and old_progress.get("identity")==identity
                     and type(old_progress.get("native_attempts")) is int
                     and 0<=old_progress["native_attempts"]<=MAX_NEW_NATIVE,
                     "NATIVE_PROGRESS_IDENTITY_OR_CAP_DRIFT")
                progress["native_attempts"]=old_progress["native_attempts"]
            else:engine.write_atomic(progress_file,progress)
            results=[]
            for i,request in enumerate(reqs):
                result=engine.execute_one(request,{"native_revision":rev},
                    binary,out/("static_%02d"%i),progress,
                    cache_only=cache_only)
                need(result["status"]==
                     "PASS_NATIVE_DPS_AND_STATIC_CHMV_INPUT"
                     and result["static_rating_verified"]==request["target"]
                     and result["raw_gear_override"]==
                         request["raw_gear_override"]
                     and result["dps_samples"]>=20,
                     "STATIC_TARGET_INPUT_OR_SIMC_DPS_INVALID")
                state["new_native_this_invocation"]+=int(
                          result["source"]=="NEW_NATIVE")
                results.append(result)
                state["completed"]=len(results)
                state["status"]="PARTIAL_NEW_STATIC_NATIVE"
                engine.write_atomic(receipt,state)
            # Distinguish both dimensions; a talent-induced buffed difference
            # is an expected observation, not a need to reduce static c.
            need(any(result["rating_actual"]["crit_rating"]!=
                     result["target"]["crit_rating"] for result in results),
                 "EXPECTED_HUNTER_BUFFED_CRIT_DISTINCTION_NOT_OBSERVED")
            state.update({"status":"PASS_TWO_REAL_HUNTER_STATIC_CHMV_NATIVE",
              "new_native_total_durable":progress["native_attempts"],
              "cache_only_replay":cache_only,
              "official_results":[{
                "target_static_c":result["target"],
                "verified_static_c":result["static_rating_verified"],
                "simc_buffed_rating_observed":result["rating_actual"],
                "flask_F_component":result["flask_F_component"],
                "raw_input_gear_plus_gems":result["raw_gear_override"],
                "dps_mean":result["dps_mean"],"dps_sem":result["dps_sem"],
                "dps_samples":result["dps_samples"],
                "native_json_sha256":result["native_json_sha256"],
                "source":result["source"]} for result in results],
              "strict_buffed_equals_c_assertion_removed":True,
              "all_nonstat_effects_remain_simc_owned":True})
        else:
            state["new_native_total_durable"]=0
    except Exception as exc:
        state["status"]="BLOCKED_OR_PARTIAL"
        state["error"]=type(exc).__name__+":"+str(exc)
    engine.write_atomic(receipt,state)
    print("V080",state["status"],"new_native",
          state["new_native_this_invocation"],"error",state.get("error"),flush=True)
    return 0 if state["status"].startswith("PASS") else 3

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",required=True,type=pathlib.Path)
    p.add_argument("--prior-failed-native",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    p.add_argument("--binary",type=pathlib.Path)
    p.add_argument("--cache-only",action="store_true")
    x=p.parse_args(argv)
    return run(x.upstream,x.prior_failed_native,x.out,x.binary,x.cache_only)

if __name__=="__main__":sys.exit(main())
