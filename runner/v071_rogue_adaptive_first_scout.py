#!/usr/bin/env python3
"""v071 bounded FIRST genuine adaptive scout for real user Subtlety Rogue.

Three prior actual v068/v070 Native JSON2 files are reused; only v070
official-T sample is a scout anchor. v068 numeric-witness samples are NOT
silently promoted into official-T points. The original v015-derived v065
scheduler chooses the next official-3150 rating vector, and the existing
v065/v064 Native executor checks exact final rating, DPS/SEM and cache.

One additional real Native scout maximum, 35 requested iterations.
No global optimum or new gear/proc/APL engine. No v015/v016 source edit.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,sys,math
import v063_numeric_injection as numeric
import v064_adaptive_evaluator_port as port
import v065_v015_scheduler_adapter as scheduler
import v065_original_scheduler_native_bridge as native_engine
import v068_rogue_two_native_probe as probe
import v069_rogue_official_budget_native as official

SCHEMA="v071_real_user_rogue_adaptive_first_native_scout_v1"
class V071Blocked(ValueError):pass
def need(ok,why):
    if not ok:raise V071Blocked(why)

def verified_anchor(prepared,prior):
    """Read untouched v070 official JSON2 and verify against recalibrated P1-P3."""
    prior=pathlib.Path(prior)
    inputfile=prior/"input.simc"
    jsonfile=prior/"result.json"
    receiptfile=prior/"V069_RECEIPT.json"
    previous=json.loads(receiptfile.read_text("utf-8"))
    need(previous.get("status")=="PASS_ONE_ROGUE_OFFICIAL_T_NATIVE_DPS_RATING",
         "PREVIOUS_REAL_OFFICIAL_PASS_RECEIPT_REQUIRED")
    need(previous.get("T_official")==prepared["budget"]["budget"]["T_official"],
         "PREVIOUS_OFFICIAL_T_CHANGED")
    raw=inputfile.read_bytes()
    native_bytes=jsonfile.read_bytes()
    need(hashlib.sha256(native_bytes).hexdigest()==previous["result"]["native_json_sha256"],
         "PREVIOUS_JSON2_SHA_CHANGED")
    src=raw.decode("utf-8")
    stable=numeric.input_parts(src)
    ref=numeric.input_parts(prepared["reference"])
    need(stable["stable_sha256"]==ref["stable_sha256"],
         "PREVIOUS_OBSERVED_PROFILE_CHANGED")
    target=previous["candidate_target"]
    numeric.check_target(prepared["normalized"],prepared["budget"],target)
    req=port.make_request(prepared["normalized"],prepared["budget"],
         prepared["calibration"],prepared["reference"],probe.BIN_SHA,
         target,35,prior/"result.json")
    expected=numeric.input_parts(req["input"])
    need(stable["gear_override"]==expected["gear_override"],
         "PREVIOUS_OFFICIAL_GEAR_OVERRIDE_NOT_REPRODUCED")
    # JSON2 destination is necessarily different when an archived workflow
    # artifact is unpacked in this new run. Compare all STABLE profile lines
    # and actual four gear overrides, then separately pin 35 iterations.
    # Never fake raw full-byte parity across two distinct output directories.
    need(sum(line=="iterations=35" for line in src.splitlines())==1,
         "PREVIOUS_OFFICIAL_ITERATIONS_CHANGED")
    doc=json.loads(native_bytes)
    obs=port.ingest_native(req,doc,prepared["calibration"],native_bytes)
    need(obs["dps_mean"]==previous["result"]["dps_mean"] and
         obs["dps_sem"]==previous["result"]["dps_sem"] and
         obs["dps_samples"]==previous["result"]["dps_samples"],
         "PREVIOUS_NATIVE_DPS_SEM_RECEIPT_DRIFT")
    return obs

def run(witness_root,prior_official,out,binary=None,cache_only=False):
    out=pathlib.Path(out)
    out.mkdir(parents=True,exist_ok=True)
    summary={"schema":SCHEMA,"status":"BLOCKED",
      "new_native_calls":0,"native_call_cap":1,
      "official_formula":"T=G+J+F",
      "all_gear_effects_owned_by":"SimC",
      "original_v015_v016_tests_rerun":False,
      "rogue_global_optimum_proven":False}
    receipt=out/"V071_RECEIPT.json"
    try:
        prepared=official.prepare(witness_root,probe.BIN_SHA)
        normalized=prepared["normalized"]
        calibrated=prepared["calibration"]
        static=prepared["budget"]
        anchor=verified_anchor(prepared,prior_official)
        state=scheduler.initial_state(normalized,static,[anchor],step=100,
                                      scout_max=1,confirmation_runs=2)
        folder=out/"scout_00"
        offer=scheduler.next_scout(state,normalized,static,calibrated,
             prepared["reference"],probe.BIN_SHA,
             folder/"result.json",35)
        new=offer["case"]
        need(new["case_key"]!=anchor["case_key"],"NEW_CANDIDATE_CACHE_KEY_COLLISION")
        summary.update({
           "status":"NEXT_ADAPTIVE_CHMV_READY",
           "official_T":static["budget"]["T_official"],
           "G":static["G_if_complete"],
           "J":static["budget"]["J"],"F":static["budget"]["F"],
           "special_fixed_L":static["locked_L_when_all_specials_observed"],
           "numeric_offset":calibrated["net_input_to_json2_rating_offset"],
           "prior_official_anchor":{"target":anchor["target"],
              "dps_mean":anchor["dps_mean"],"dps_sem":anchor["dps_sem"],
              "dps_samples":anchor["dps_samples"],
              "native_json_sha256":anchor["native_json_sha256"]},
           "next_target":new["target"],
           "candidate_case_key":new["case_key"],
           "next_decision":offer["decision"],
           "original_two_numeric_witnesses_reused":2,
           "old_official_target_reused":1})
        if binary is None:
            summary["status"]="PASS_NEXT_SCOUT_PLAN_NO_NATIVE"
        else:
            binary=pathlib.Path(binary)
            need(binary.is_file() and
                 hashlib.sha256(binary.read_bytes()).hexdigest()==probe.BIN_SHA,
                 "PINNED_SIMC_BINARY_CHANGED")
            # Important: pre-existing cached Native result must be SHA-validated
            # by v065 before declaring a hit. Any partial file blocks, not reruns.
            already=(folder/"result.json").is_file()
            if not already:
                need(not cache_only,"CACHE_ONLY_WITHOUT_RESULT")
                summary["new_native_calls"]=1
                native_engine.write_atomic(receipt,summary)
            progress={"native_attempts":0 if not already else 1,
                      "status":"START","schema":SCHEMA}
            obs=native_engine.execute_one(new,calibrated,binary,folder,progress,
                       cache_only=cache_only)
            state=scheduler.accept_scout(state,new,obs)
            summary.update({
              "status":"PASS_ONE_ROGUE_ADAPTIVE_REAL_NATIVE_DPS_AND_CHMV",
              "new_native_calls":int(obs.get("source")=="NEW_NATIVE"),
              "new_scout":{"source":obs.get("source"),
                "target":obs["target"],"rating_actual":obs["rating_actual"],
                "dps_mean":obs["dps_mean"],"dps_sem":obs["dps_sem"],
                "dps_samples":obs["dps_samples"],
                "native_json_sha256":obs["native_json_sha256"]},
              "one_real_adaptive_step_complete":state["completed_new_scouts"]==1})
            delta=obs["dps_mean"]-anchor["dps_mean"]
            ci=1.9599639854*math.hypot(obs["dps_sem"],anchor["dps_sem"])
            summary["comparison"]={"new_minus_old_dps":delta,
                "normal_approx_ci95_halfwidth":ci,
                "unconfirmed_direction":abs(delta)<=ci,
                "independent_confirmations_needed":True}
    except Exception as e:
        summary["status"]="BLOCKED_OR_PARTIAL"
        summary["error"]=type(e).__name__+":"+str(e)
    native_engine.write_atomic(receipt,summary)
    print("V071",summary["status"],"new_native",summary["new_native_calls"],flush=True)
    return 0 if summary["status"].startswith("PASS") else 3

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--witness-root",required=True,type=pathlib.Path)
    p.add_argument("--prior-official",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    p.add_argument("--binary",type=pathlib.Path)
    p.add_argument("--cache-only",action="store_true")
    a=p.parse_args(argv)
    return run(a.witness_root,a.prior_official,a.out,a.binary,a.cache_only)

if __name__=="__main__":sys.exit(main())
