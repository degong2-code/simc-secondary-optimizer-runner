#!/usr/bin/env python3
"""v081: real static-c common v066 preflight -> v015-derived scout -> Native.

Uses TWO SHA-verified preexisting real v080 STATIC Native candidates as
anchors and their exact Native static item rows. One NEW bounded 35-iteration
SimC Native scout; replay requires zero calls. NO item or talent effect model.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,sys
import v046_static_item_cache as static_cache
import v061_scenario_contract as scenario
import v062_static_budget_bridge as budget
import v063_numeric_injection as numeric
import v064_adaptive_evaluator_port as port
import v065_original_scheduler_native_bridge as engine
import v065_v015_scheduler_adapter as scheduler
import v066_profile_neutral_preflight as preflight
import v079_hunter_ranged_generic_native as hunter
import v068_rogue_two_native_probe as pinned

SCHEMA="v081_generic_static_native_scout_v1"
ITERATIONS=35
MAX_NEW_NATIVE=1

class Blocked(ValueError):pass
def need(x,msg):
    if not x:raise Blocked(msg)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(p):return json.loads(pathlib.Path(p).read_text("utf8"))

def verified_v080(parent):
    root=pathlib.Path(parent)
    receipt=read(root/"V080_RECEIPT.json")
    need(receipt["status"]=="PASS_TWO_REAL_HUNTER_STATIC_CHMV_NATIVE"
         and receipt["T"]==2797 and receipt["G"]==2494
         and receipt["F"]==165 and receipt["J"]==138
         and receipt.get("new_native_total_durable")==2,
         "V080_TWO_REAL_STATIC_NATIVE_ANCHORS_REQUIRED")
    need(receipt["legacy_buffed_field_not_static_target"]
         and receipt["strict_buffed_equals_c_assertion_removed"],
         "V080_STATIC_SEMANTICS_NOT_CONFIRMED")
    F=receipt["F_declared_static_vector"]
    need(F=={"crit_rating":0,"haste_rating":165,
             "mastery_rating":0,"versatility_rating":0},
         "V080_DECLARED_FLASK_F_CHANGED")
    evidence=[];native_cache=static_cache.empty_cache()
    for i,summary in enumerate(receipt["official_results"]):
        case=root/("static_%02d"%i)
        source=(case/"input.simc").read_bytes()
        raw=(case/"result.json").read_bytes()
        r=read(case/"native_receipt.json")
        need(sha(source)==r["input_sha256"] and
             sha(raw)==r["native_json_sha256"]==
                         summary["native_json_sha256"] and
             r["simc_binary_sha256"]==pinned.BIN_SHA and
             r["target"]==summary["target_static_c"] and
             r["static_rating_verified"]==summary["verified_static_c"] and
             r["rating_semantics"]=="STATIC_CHMV_C_V1",
             "V080_NATIVE_SHA_OR_SOURCE_PROVENANCE_DRIFT")
        doc=json.loads(raw)
        parsed=numeric.input_parts(source.decode("utf8"))
        need(all(parsed["gear_override"][k]+F[k]==r["target"][k]
                 for k in scenario.STATS),
             "V080_STATIC_TARGET_NOT_RECONSTRUCTIBLE")
        evidence.append({"input":source.decode("utf8"),"native":doc,
            "raw_native_json":raw,"input_sha256":sha(source),
            "native_json_sha256":sha(raw)})
        static_cache.merge_native(native_cache,static_cache.native_records(
           raw,artifact_id="V081_REUSED_REAL_V080_%02d"%i))
    return evidence,native_cache,receipt,F

def run(upstream,source_v080,out,binary=None,cache_only=False):
    out=pathlib.Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    target=out/"V081_RECEIPT.json"
    summary={"schema":SCHEMA,"status":"BLOCKED_OR_PARTIAL",
        "new_native_this_invocation":0,"max_new_native":MAX_NEW_NATIVE,
        "global_optimum_proven":False,
        "original_v015_v016_product_integrated":False}
    try:
        original=pathlib.Path(upstream).read_text("utf8")
        ref,contract,fill,meta=hunter.source_profile(original,out)
        witnesses,rows,prior_receipt,F=verified_v080(source_v080)
        prepared=preflight.prepare_static(
            contract,fill,rows,ref,witnesses,pinned.BIN_SHA,F)
        need(prepared["summary"]["status"]=="READY_STATIC_CHMV_PROFILE_SCOPED"
             and prepared["summary"]["T_official"]==2797 and
             prepared["summary"]["G_native"]==2494,
             "NEW_GENERIC_STATIC_NATIVE_PREFLIGHT_FAILED")
        proposal=preflight.propose_next_static(prepared,ITERATIONS,
                   out/"native"/"adaptive_00"/"result.json",step=100)
        request=proposal["case"]
        need(request["rating_semantics"]=="STATIC_CHMV_C_V1"
             and request["target"] not in
                  [r["target"] for r in prepared["prior_observations"]]
             and sum(request["target"].values())==2797 and
             sum(request["raw_gear_override"].values())==2632,
             "STATIC_V015_SCOUT_NOT_AN_UNSEEN_OFFICIAL_TARGET")
        summary.update({"status":"PASS_STATIC_PREPARATION_AND_V015_SCOUT_PLAN",
            "v066_status":prepared["summary"]["status"],
            "two_existing_actual_static_json2_sha256":[
               r["native_json_sha256"] for r in witnesses],
            "source_armor":"mail","source_weapon":"ranged_no_offhand",
            "source_race":"troll","class":"hunter","spec":"beast_mastery",
            "G":2494,"J":138,"F":165,"T":2797,
            "F_declared_vector":F,
            "source_flask_vector_independently_proven":False,
            "new_proposal_static_CHMV_c":request["target"],
            "new_proposal_injected_raw_GJ":request["raw_gear_override"],
            "v015_derived_scout_hint":proposal["decision"],
            "no_talent_inversion_or_APL_implementation":True})
        if binary is not None:
            binary=pathlib.Path(binary).resolve()
            need(binary.is_file() and sha(binary.read_bytes())==pinned.BIN_SHA,
                 "SIMC_BINARY_SHA_DRIFT")
            seal=out/"V081_IDENTITY.json"
            identity={"schema":SCHEMA,
                 "historical_json2_sha256":summary["two_existing_actual_static_json2_sha256"],
                 "case_key":request["case_key"],"input_sha256":request["input_sha256"],
                 "source_rev":prepared["summary"]["simc_revision"],
                 "binary_sha256":pinned.BIN_SHA,
                 "rating_semantics":"STATIC_CHMV_C_V1"}
            if seal.exists():need(read(seal)==identity,"SCOUT_RESUME_IDENTITY_CHANGED")
            else:
                need(not (out/"native"/"adaptive_00").exists(),
                     "UNSEALED_PREEXISTING_NATIVE_RESULT")
                engine.write_atomic(seal,identity)
            progress_file=out/"native"/"V065_PROGRESS.json"
            progress={"schema":SCHEMA,"identity":identity,"native_attempts":0}
            if progress_file.exists():
                old=read(progress_file)
                need(old.get("schema")==SCHEMA and old.get("identity")==identity
                     and type(old.get("native_attempts")) is int and
                     0<=old["native_attempts"]<=1,
                     "SCOUT_NATIVE_ATTEMPTS_REPLAY_DRIFT")
                progress["native_attempts"]=old["native_attempts"]
            else:engine.write_atomic(progress_file,progress)
            folder=out/"native"/"adaptive_00"
            cached=(folder/"result.json").exists() or (
                folder/"native_receipt.json").exists()
            if not cached:need(progress["native_attempts"]<MAX_NEW_NATIVE,
                               "MAX_ONE_FRESH_NATIVE_CALL")
            result=engine.execute_one(request,prepared["calibration"],binary,
                 folder,progress,cache_only=cache_only)
            need(result["status"]=="PASS_NATIVE_DPS_AND_STATIC_CHMV_INPUT"
                 and result["rating_semantics"]=="STATIC_CHMV_C_V1"
                 and result["static_rating_verified"]==request["target"] and
                 result["dps_samples"]>=20,
                 "SIMC_NATIVE_STATIC_C_AND_DPS_NOT_VALID")
            summary["new_native_this_invocation"]=int(result["source"]=="NEW_NATIVE")
            state=scheduler.initial_state(prepared["normalized"],prepared["budget"],
                prepared["prior_observations"],step=100,scout_max=2)
            advanced=scheduler.accept_scout(state,request,result)
            need(advanced["completed_new_scouts"]==1 and
                 len(advanced["observations"])==3,
                 "V015_SCOUT_PROGRESS_STATIC_NOT_ACCEPTED")
            summary.update({"status":"PASS_STATIC_GENERIC_V066_V015_SCOUT_NATIVE",
                 "new_native_total_durable":progress["native_attempts"],
                 "cache_only_replay":cache_only,
                 "scout_acceptance_status":"V015_DERIVED_ORDER_ACCEPTED_STATIC_C",
                 "native_observation":{
                    "static_c":result["target"],
                    "verified_static_c":result["static_rating_verified"],
                    "simc_buffed_rating":result["rating_actual"],
                    "dps_mean":result["dps_mean"],"dps_sem":result["dps_sem"],
                    "dps_samples":result["dps_samples"],
                    "native_json_sha256":result["native_json_sha256"],
                    "source":result["source"]}})
    except Exception as ex:
        summary["status"]="BLOCKED_OR_PARTIAL"
        summary["error"]=type(ex).__name__+":"+str(ex)
    engine.write_atomic(target,summary)
    print("V081",summary["status"],"new_native",summary["new_native_this_invocation"],
          "error",summary.get("error"),flush=True)
    return 0 if summary["status"].startswith("PASS") else 3

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",required=True,type=pathlib.Path)
    p.add_argument("--prior-static",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    p.add_argument("--binary",type=pathlib.Path)
    p.add_argument("--cache-only",action="store_true")
    x=p.parse_args(argv)
    return run(x.upstream,x.prior_static,x.out,x.binary,x.cache_only)

if __name__=="__main__":sys.exit(main())
