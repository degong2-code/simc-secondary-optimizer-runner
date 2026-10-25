#!/usr/bin/env python3
"""v078B: real official-GJF Elementary Shaman cross-class Native route.

Takes actual two-witness v078 original JSON2 and Native exact static variants,
reuses v063 numeric calibration + v064 evaluator + v066 neutral preflight +
v065 original native executor / v015-derived policy. At most 2 official
35-iteration candidates + 1 v015-guided new 35-iteration scout. Never
invents class rules, proc verification, or historical Native acceptance.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,sys
import v046_static_item_cache as static_cache
import v061_scenario_contract as scenario
import v062_static_budget_bridge as budgets
import v063_numeric_injection as numeric
import v064_adaptive_evaluator_port as port
import v065_original_scheduler_native_bridge as engine
import v065_v015_scheduler_adapter as scheduler
import v066_profile_neutral_preflight as preflight
import v068_rogue_two_native_probe as pin
import v078_elemental_first_native as first

SCHEMA="v078b_elemental_cross_spec_official_GJF_and_adaptive_native_v1"
ITERATIONS=35
NATIVE_CAP=3

class Blocked(ValueError):pass
def need(ok,reason):
    if not ok:raise Blocked(reason)
def read(path):return json.loads(pathlib.Path(path).read_text("utf8"))
def sha(data):return hashlib.sha256(data).hexdigest()

def verified_parent(parent):
    """SHA-check actual v078 Native inputs, JSON2 and persisted static cache."""
    root=pathlib.Path(parent)
    receipt=read(root/"V078_RECEIPT.json")
    need(receipt.get("status")=="PASS_TWO_ELEMENTAL_NATIVE_NUMERIC_WITNESSES"
         and receipt.get("native_attempts_total")==2
         and receipt.get("new_profile_calibration",{}).get("witnesses")==2
         and receipt.get("character",{}).get("class")=="shaman"
         and receipt.get("character",{}).get("spec")=="elemental"
         and receipt.get("full_static_G_if_native")==2645
         and receipt.get("full_official_T_if_native")==2948,
         "PARENT_TWO_REAL_ELEMENTAL_NATIVE_REQUIRED")
    profile=(root/"V078_REFERENCE.simc").read_text("utf8")
    cfg=read(root/"V078_SCENARIO.json")
    filler=read(root/"V078_FILLER.json")
    need(sha(profile.encode("utf8"))==receipt["scenario_profile_sha256"]
         and cfg["character"]["class"]=="shaman"
         and cfg["character"]["spec"]=="elemental"
         and cfg["character"]["race"]=="orc",
         "PARENT_PROFILE_IDENTITY_CHANGED")
    native=preflight.load_witnesses(root/"native")
    need(len(native)==2,"PARENT_TWO_WITNESSES_MISSING")
    for i,e in enumerate(native):
        need(e["input_sha256"]==receipt["witness_input_sha256"][i]
             and e["native_json_sha256"]==
                receipt["actual_native_witnesses"][i]["json2_sha256"],
             "PARENT_NATIVE_INPUT_JSON_SHA_CHANGED")
    calibrated=numeric.calibrate(native)
    need(calibrated==receipt["new_profile_calibration"],
         "PARENT_CALIBRATION_DRIFT")
    new_cache=static_cache.empty_cache()
    for i,e in enumerate(native):
        native_rows=static_cache.native_records(
             e["raw_native_json"],artifact_id="V078_ELEMENTAL_NATIVE_%02d"%i)
        static_cache.merge_native(new_cache,native_rows)
    previous_cache=static_cache.load(root/"V078_STATIC_CACHE.json")
    need(new_cache==previous_cache,"PARENT_STATIC_CACHE_NATIVE_REPLAY_MISMATCH")
    normalized=scenario.normalize(cfg)
    static=budgets.compile_static_budget(normalized,filler,new_cache)
    need(static["G_if_complete"]==2645
         and static["budget"]["T_official"]==2948
         and not static["missing_nontrinket_static"]
         and not static["missing_special_fixed_static"]
         and static["budget"]["oil_stays_OUTSIDE_T"],
         "PARENT_OFFICIAL_GJF_NOT_VERIFIED")
    return cfg,filler,new_cache,profile,calibrated,static,native,normalized

def targets(total,static):
    """Small independent allocation perturbation, NOT an optimizer."""
    base=[total//4]*4
    base[0]+=total-sum(base)
    keys=scenario.STATS
    a=dict(zip(keys,base))
    b=dict(a)
    b["crit_rating"]-=100
    b["haste_rating"]+=100
    minimum=static["effective_floor_if_possible"]
    need(all(a[x]>=minimum[x] and b[x]>=minimum[x] for x in keys),
         "SELECTED_NATIVE_OFFICIAL_TARGET_BELOW_FLOOR")
    need(sum(a.values())==sum(b.values())==total and a!=b,
         "OFFICIAL_T_TARGETS_NOT_DISTINCT")
    return [a,b]

def run(parent,out,binary=None,cache_only=False):
    out=pathlib.Path(out);out.mkdir(parents=True,exist_ok=True)
    receipt_file=out/"V078B_RECEIPT.json"
    result={"schema":SCHEMA,"status":"BLOCKED_OR_PARTIAL",
            "new_native_this_invocation":0,"native_attempts_total":0,
            "native_cap":NATIVE_CAP,"official_formula":"T=G+J+F",
            "global_optimum_proven":False}
    try:
        cfg,filler,exact_cache,reference,cal,static,earlier,normalized=verified_parent(parent)
        total=static["budget"]["T_official"]
        cand=targets(total,static)
        result.update({"status":"PASS_OFFLINE_OFFICIAL_NATIVE_PLAN_ZERO_NEW_SIMC",
              "historical_two_native_sha_verified":True,
              "G":static["G_if_complete"],"J":static["budget"]["J"],
              "F":static["budget"]["F"],"T":total,
              "profile_stable_sha256":cal["stable_profile_sha256"],
              "calibration_offset":cal["net_input_to_json2_rating_offset"],
              "targets":cand,"prior_native_reused":2,
              "source_scenario_digest":normalized["scenario_digest"]})
        requests=[port.make_request(normalized,static,cal,reference,pin.BIN_SHA,
                 target,ITERATIONS,out/("official_%02d"%i)/"result.json")
                 for i,target in enumerate(cand)]
        if binary is not None:
            binary=pathlib.Path(binary).resolve()
            need(binary.is_file() and sha(binary.read_bytes())==pin.BIN_SHA,
                 "PINNED_SIMC_BINARY_CHANGED")
            identity={"schema":SCHEMA,"prior_two_native_shas":
                  [e["native_json_sha256"] for e in earlier],
                  "scenario_digest":normalized["scenario_digest"],
                  "binary_sha":pin.BIN_SHA,
                  "official_requests":[{"case_key":x["case_key"],
                     "input_sha256":x["input_sha256"]} for x in requests],
                  "limit":NATIVE_CAP,"iterations":ITERATIONS}
            seal=out/"V078B_IDENTITY.json"
            if seal.exists():
                need(read(seal)==identity,"RESUME_SOURCE_OR_OFFICIAL_CASE_CHANGED")
            else:
                need(not any((out/("official_%02d"%i)).exists() for i in range(2))
                     and not (out/"adaptive_00").exists(),
                     "OLD_NATIVE_FOLDER_WITHOUT_IDENTITY")
                engine.write_atomic(seal,identity)
            ledger=out/"V065_PROGRESS.json"
            progress={"schema":SCHEMA,"native_attempts":0,"native_limit":NATIVE_CAP,
               "scenario_digest":normalized["scenario_digest"],
               "source_profile_sha256":cal["stable_profile_sha256"],
               "official_request_keys":[x["case_key"] for x in requests]}
            if ledger.exists():
                old=read(ledger)
                need(all(old.get(k)==progress[k] for k in
                    ("schema","native_limit","scenario_digest",
                     "source_profile_sha256","official_request_keys"))
                     and type(old.get("native_attempts")) is int
                     and 0<=old["native_attempts"]<=NATIVE_CAP,
                     "DURABLE_NATIVE_LEDGER_CHANGED")
                progress["native_attempts"]=old["native_attempts"]
            else:
                engine.write_atomic(ledger,progress)
            observed=[]
            for i,req in enumerate(requests):
                folder=out/("official_%02d"%i)
                cached=(folder/"result.json").exists() or
                       (folder/"native_receipt.json").exists()
                if not cached:
                    need(not cache_only,"CACHE_ONLY_BLOCKS_NEW_NATIVE")
                    need(progress["native_attempts"]<2,
                         "TWO_OFFICIAL_NATIVE_LIMIT")
                obs=engine.execute_one(req,cal,binary,folder,progress,
                       cache_only=cache_only)
                need(obs["status"]=="PASS_NATIVE_DPS_AND_RATING"
                     and obs["iterations"]==ITERATIONS
                     and obs["dps_samples"]>=20
                     and obs["rating_actual"]==req["target"],
                     "OFFICIAL_NATIVE_RATING_OR_DPS_INVALID")
                observed.append(obs)
                result["new_native_this_invocation"]+=int(
                      obs["source"]=="NEW_NATIVE")
                result["status"]="OFFICIAL_NATIVE_PARTIAL"
                result["completed_official"]=len(observed)
                engine.write_atomic(receipt_file,result)
            full=[{"input":(out/("official_%02d"%i)/"input.simc").read_text("utf8"),
                   "native":read(out/("official_%02d"%i)/"result.json"),
                   "raw_native_json":(out/("official_%02d"%i)/"result.json").read_bytes(),
                   "input_sha256":observed[i]["input_sha256"],
                   "native_json_sha256":observed[i]["native_json_sha256"]}
                   for i in range(2)]
            prepared=preflight.prepare(cfg,filler,exact_cache,reference,
                                       full,pin.BIN_SHA)
            need(prepared["summary"]["status"]=="READY_NUMERIC_PROFILE_SCOPED"
                 and prepared["summary"]["T_official"]==total,
                 "V066_GENERIC_REAL_TWO_OFFICIAL_WITNESS_FAILED")
            first_scout=preflight.propose_next(prepared,ITERATIONS,
                          out/"adaptive_00"/"result.json",step=100)
            req=first_scout["case"]
            need(req["target"] not in cand,"GENERIC_SCHEDULER_REPEATED_TARGET")
            folder=out/"adaptive_00"
            cached=(folder/"result.json").exists() or
                   (folder/"native_receipt.json").exists()
            if not cached:
                need(not cache_only,"CACHE_ONLY_BLOCKS_NEW_ADAPTIVE")
                need(progress["native_attempts"]<NATIVE_CAP,
                     "THREE_NATIVE_ATTEMPT_CAP")
            new=engine.execute_one(req,cal,binary,folder,progress,
                                   cache_only=cache_only)
            need(new["status"]=="PASS_NATIVE_DPS_AND_RATING"
                 and new["iterations"]==ITERATIONS
                 and new["dps_samples"]>=20
                 and new["rating_actual"]==req["target"],
                 "ADAPTIVE_SHAMAN_NATIVE_NOT_JSON2_PARITY")
            result["new_native_this_invocation"]+=int(
                  new["source"]=="NEW_NATIVE")
            result.update({"status":"PASS_REAL_ELEMENTAL_OFFICIAL_NATIVE_AND_GENERIC_V015_SCOUT",
              "native_attempts_total":progress["native_attempts"],
              "two_real_official_witnesses":[{
                     "target":z["target"],"rating_actual":z["rating_actual"],
                     "dps_mean":z["dps_mean"],"dps_sem":z["dps_sem"],
                     "dps_samples":z["dps_samples"],"source":z["source"],
                     "native_json_sha256":z["native_json_sha256"]}
                     for z in observed],
              "v066_real_profile_status":prepared["summary"]["status"],
              "adaptive_new_candidate":{
                     "target":new["target"],"rating_actual":new["rating_actual"],
                     "dps_mean":new["dps_mean"],"dps_sem":new["dps_sem"],
                     "dps_samples":new["dps_samples"],"source":new["source"],
                     "native_json_sha256":new["native_json_sha256"]},
              "v015_scheduler_hint":first_scout["decision"],
              "four_targets_real_native_total":5,
              "original_v015_v016_direct_product_integrated":False,
              "global_optimum_proven":False})
        else:
            result["status"]="PASS_OFFLINE_OFFICIAL_NATIVE_PLAN_ZERO_NEW_SIMC"
    except Exception as e:
        result["status"]="BLOCKED_OR_PARTIAL"
        result["error"]=type(e).__name__+":"+str(e)
        p=out/"V065_PROGRESS.json"
        if p.exists():
            try:result["native_attempts_total"]=read(p).get("native_attempts")
            except Exception:result["progress_unreadable"]=True
    engine.write_atomic(receipt_file,result)
    print("V078B",result["status"],"new_native",
          result["new_native_this_invocation"],"error",result.get("error"),flush=True)
    return 0 if result["status"].startswith("PASS") else 3

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--prior-native",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    p.add_argument("--binary",type=pathlib.Path)
    p.add_argument("--cache-only",action="store_true")
    a=p.parse_args(argv)
    return run(a.prior_native,a.out,a.binary,a.cache_only)

if __name__=="__main__":
    sys.exit(main())
