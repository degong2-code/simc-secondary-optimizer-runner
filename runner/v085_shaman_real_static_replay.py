#!/usr/bin/env python3
"""v085 — migrate REAL v078B Elemental Shaman Native receipts to STATIC CHMV.

READ ONLY source artifacts. Reuse 2 real first-use numeric witnesses and
3 legacy official/scout SimC input+JSON2 pairs. Do not rerun Native or relabel
anything as static-c unless exact source/rating/JSON2 Sha and v066 static
preflight plus existing v015-derived next-scout policy all agree. Profile-
specific F crit+165 is declared, not independently universal flask research.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,sys
import v061_scenario_contract as scenario
import v063_numeric_injection as numeric
import v064_adaptive_evaluator_port as port
import v065_original_scheduler_native_bridge as engine
import v065_v015_scheduler_adapter as scheduler
import v066_profile_neutral_preflight as preflight
import v078b_elemental_official_generic_native as original
import v068_rogue_two_native_probe as pin

SCHEMA="v085_shaman_actual_legacy_static_chmv_replay_v1"
F={"crit_rating":165,"haste_rating":0,
   "mastery_rating":0,"versatility_rating":0}
class Blocked(ValueError):pass
def need(ok,why):
    if not ok:raise Blocked(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path):return json.loads(pathlib.Path(path).read_text("utf8"))

def real_case(parent,name,observed,reference,normalized,static,revision):
    p=pathlib.Path(parent)/name
    source=(p/"input.simc").read_bytes()
    raw=(p/"result.json").read_bytes()
    saved=read(p/"native_receipt.json")
    # Native source identity is independently reconstructed from JSON2 and
    # the original previous runner's SHA-locked receipt.
    need(saved.get("input_sha256")==sha(source)==observed["input_sha256"],
         "ORIGINAL_NATIVE_INPUT_SHA_CHANGED:"+name)
    need(saved.get("native_json_sha256")==sha(raw)==
         observed["native_json_sha256"],
         "ORIGINAL_NATIVE_JSON2_SHA_CHANGED:"+name)
    need(saved.get("simc_binary_sha256")==pin.BIN_SHA,
         "ORIGINAL_SIMC_BINARY_SHA_CHANGED:"+name)
    doc=json.loads(raw)
    need(doc.get("git_revision")==revision and
         doc.get("report_version")=="2.0.0",
         "ORIGINAL_NATIVE_REVISION_OR_FORMAT_DRIFT:"+name)
    profile_text=source.decode("utf8")
    parsed=numeric.input_parts(profile_text)
    target={k:parsed["gear_override"][k]+F[k] for k in scenario.STATS}
    need(sum(target.values())==static["budget"]["T_official"]
         and target==observed["target"],
         "LEGACY_RESULT_NOT_EQUIVALENT_TO_OFFICIAL_STATIC_C:"+name)
    json2_path=[line.split("=",1)[1] for line in profile_text.splitlines()
                if line.startswith("json2=")]
    iterations=[int(line.split("=",1)[1]) for line in profile_text.splitlines()
                if line.startswith("iterations=")]
    need(len(iterations)==len(json2_path)==1 and iterations[0]==35,
         "ORIGINAL_NATIVE_ITERATION_OR_OUTPUT_UNEXPECTED:"+name)
    request=port.make_static_chmv_request(
        normalized,static,reference,pin.BIN_SHA,revision,target,F,
        iterations[0],pathlib.Path(json2_path[0]))
    need(request["input_sha256"]==sha(source)
         and request["input"]==profile_text,
         "STATIC_C_REQUEST_DIFFERS_FROM_LEGACY_REAL_NATIVE_INPUT:"+name)
    new=port.ingest_native(request,doc,{"native_revision":revision},raw)
    need(new["status"]=="PASS_NATIVE_DPS_AND_STATIC_CHMV_INPUT"
         and new["target"]==new["static_rating_verified"]==target
         and new["dps_samples"]>=20,
         "REINTERPRETED_STATIC_C_NATIVE_OBSERVATION_INVALID:"+name)
    return {
       "evidence":{"input":profile_text,"native":doc,"raw_native_json":raw,
           "input_sha256":sha(source),"native_json_sha256":sha(raw)},
       "request":request,"result":new}

def run(first_native,official_native,out):
    out=pathlib.Path(out)
    out.mkdir(parents=True,exist_ok=True)
    receipt=out/"V085_RECEIPT.json"
    result={"schema":SCHEMA,"status":"BLOCKED_OR_PARTIAL",
        "new_native_this_invocation":0,"official_formula":"T=G+J+F",
        "static_flask_vector_declared":F,
        "flask_static_vector_independently_certified":False,
        "talent_or_proc_emulation":False,
        "global_optimum_proven":False}
    try:
        cfg,filler,cache,reference,cal,static,first,normalized=(
            original.verified_parent(first_native))
        need(cfg["consumables"]["flask"]=="flask_of_the_shattered_sun_2"
             and cal["net_input_to_json2_rating_offset"]==F,
             "PROFILE_SPECIFIC_NATIVE_FLASK_OFFSET_NOT_F_DECLARED")
        need(cal["stable_profile_sha256"]==
             numeric.input_parts(reference)["stable_sha256"],
             "ORIGINAL_FIRST_USE_STABLE_PROFILE_CHANGED")
        parent=pathlib.Path(official_native)
        legacy=read(parent/"V078B_RECEIPT.json")
        need(legacy["status"]==
              "PASS_REAL_ELEMENTAL_OFFICIAL_NATIVE_AND_GENERIC_V015_SCOUT"
             and legacy["native_attempts_total"]==3
             and legacy["G"]==2645 and legacy["T"]==2948,
             "V078B_TWO_OFFICIAL_AND_SCOUT_NATIVE_SOURCE_REQUIRED")
        revision=first[0]["native"]["git_revision"]
        old=legacy["two_real_official_witnesses"]
        need(len(old)==2,"EXACT_TWO_REAL_OFFICIAL_REQUIRED")
        pairs=[real_case(parent,"official_%02d"%i,old[i],
                reference,normalized,static,revision) for i in range(2)]
        prepared=preflight.prepare_static(
             cfg,filler,cache,reference,
             [case["evidence"] for case in pairs],pin.BIN_SHA,F)
        need(prepared["summary"]["status"]==
             "READY_STATIC_CHMV_PROFILE_SCOPED",
             "STATIC_C_V066_NOT_AUTHENTIC_FROM_TWO_LEGACY_REAL_NATIVE")
        previous_scout=legacy["adaptive_new_candidate"]
        scout=real_case(parent,"adaptive_00",previous_scout,
                         reference,normalized,static,revision)
        proposed=preflight.propose_next_static(
             prepared,35,pathlib.Path(
                 [line.partition("=")[2] for line in
                  scout["evidence"]["input"].splitlines()
                  if line.startswith("json2=")][0]),step=100)
        need(proposed["case"]["target"]==scout["result"]["target"] and
             proposed["case"]["input_sha256"]==
                scout["request"]["input_sha256"] and
             proposed["case"]["input"]==scout["request"]["input"],
             "ORIGINAL_V015_ADAPTIVE_NOT_EQUAL_STATIC_V015_PROPOSAL")
        policy=scheduler.initial_state(normalized,static,
                prepared["prior_observations"],step=100,scout_max=2)
        advanced=scheduler.accept_scout(
            policy,proposed["case"],scout["result"])
        need(advanced["completed_new_scouts"]==1,
             "STATIC_C_V015_POLICY_FAILED_TO_ACCEPT_EXISTING_SCOUT")
        result.update({"status":"PASS_THREE_REAL_SHAMAN_STATIC_C_CASES_ZERO_NEW_NATIVE",
           "G":static["G_if_complete"],
           "J":static["budget"]["J"],"F":static["budget"]["F"],
           "T":static["budget"]["T_official"],
           "character":cfg["character"],"profile_stable_sha256":
                 cal["stable_profile_sha256"],
           "real_original_first_witnesses_reused":2,
           "real_original_official_static_witnesses_reused":2,
           "real_original_adaptive_native_reused":1,
           "total_exact_historical_native_reused":5,
           "original_first_json2_sha256s":[x["native_json_sha256"]
                for x in first],
           "replayed_static_official":[{
               "target_static_c":x["result"]["target"],
               "verified_static_c":x["result"]["static_rating_verified"],
               "observed_buffed_stats":x["result"]["rating_actual"],
               "native_json2_sha256":x["result"]["native_json_sha256"],
               "dps_mean":x["result"]["dps_mean"],
               "dps_sem":x["result"]["dps_sem"],
               "dps_samples":x["result"]["dps_samples"]}
                 for x in pairs],
           "replayed_static_scout":{
               "target_static_c":scout["result"]["target"],
               "verified_static_c":scout["result"]["static_rating_verified"],
               "observed_buffed_stats":scout["result"]["rating_actual"],
               "native_json2_sha256":scout["result"]["native_json_sha256"],
               "dps_mean":scout["result"]["dps_mean"],
               "dps_sem":scout["result"]["dps_sem"],
               "dps_samples":scout["result"]["dps_samples"]},
           "v066_static_preflight":prepared["summary"]["status"],
           "v015_derived_static_scout_replay":True,
           "no_duplicate_simc_calls":True,
           "original_v015_v016_product_integrated":False})
    except Exception as exc:
        result["status"]="BLOCKED_OR_PARTIAL"
        result["error"]=type(exc).__name__+":"+str(exc)
    engine.write_atomic(receipt,result)
    print("V085",result["status"],"new_native",0,
          "error",result.get("error"),flush=True)
    return 0 if result["status"].startswith("PASS") else 3

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--prior-first",required=True,type=pathlib.Path)
    p.add_argument("--prior-official",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    a=p.parse_args(argv)
    return run(a.prior_first,a.prior_official,a.out)

if __name__=="__main__":sys.exit(main())
