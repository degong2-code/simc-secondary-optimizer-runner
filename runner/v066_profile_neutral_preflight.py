#!/usr/bin/env python3
"""v066: profile-neutral native CHMV preflight and two-witness adapter.

Inputs: explicit v061 scenario JSON, exact nontrinket filler, v046 season
static cache, full SimC profile text, and TWO real Native SimC numerical
witnesses with original exact input.simc and result.json bytes.

No class, item ID, target ilvl, G, numeric offset, SimC revision, iteration
count, or full-profile path is fixed in this module. Missing native static
records or calibration witnesses yield a precise BLOCKED result, never a zero
guess or an independent SimC item/proc gate. Does not run Native itself.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import sys

import v046_static_item_cache as cache
import v061_scenario_contract as scenario
import v062_static_budget_bridge as budget
import v063_numeric_injection as numeric
import v064_adaptive_evaluator_port as port
import v065_v015_scheduler_adapter as scheduler

SCHEMA="v066_profile_neutral_preflight_v1"

class PreflightBlocked(ValueError):
    pass

def need(ok, why):
    if not ok:
        raise PreflightBlocked(why)

def digest_bytes(raw):
    return hashlib.sha256(raw).hexdigest()

def load_witnesses(root):
    """Read actual witness input/JSON2 bytes without interpreting proc data."""
    root=pathlib.Path(root)
    found=[]
    for idx in range(2):
        case=root/("case_%02d"%idx)
        raw_input=(case/"input.simc").read_bytes()
        raw_json=(case/"result.json").read_bytes()
        need(len(raw_input)<1000000 and 0<len(raw_json)<50_000_000,
             "WITNESS_INPUT_OR_RESULT_TOO_LARGE")
        found.append({"input":raw_input.decode("utf-8"),
                      "native":json.loads(raw_json),
                      "input_sha256":digest_bytes(raw_input),
                      "native_json_sha256":digest_bytes(raw_json),
                      "raw_native_json":raw_json})
    return found

def prepare(request,fillers,static_records,reference,witnesses,binary_sha,
            calibration_override=None):
    """Return reusable context and small serializable receipt.

    A Native witness is genuine only with supplied provenance; this validates
    internal JSON2 consistency, not independent provenance of arbitrary JSON.
    """
    need(type(binary_sha) is str and scenario.HASH_RE.fullmatch(binary_sha),
         "BINARY_SHA256_REQUIRED")
    normalized=scenario.normalize(request)
    if request["source"]["kind"]=="user_supplied":
        need(digest_bytes(reference.encode("utf-8"))==
             request["source"]["profile_sha256"],
             "USER_PROFILE_EXACT_INPUT_HASH_CHANGED")
    static=budget.compile_static_budget(normalized,fillers,static_records)
    missing=static["missing_nontrinket_static"]
    missing_special=static["missing_special_fixed_static"]
    total=static["budget"]["T_official"]
    need(not missing_special,"MISSING_NATIVE_SELECTED_SPECIAL_L:"+
         ",".join(str(i["item_id"]) for i in missing_special))
    need(not missing,"MISSING_EXACT_NONTRINKET_STATIC_VARIANTS:"+
         ",".join(str(i["item_id"]) for i in missing))
    need(total is not None and static["G_if_complete"] is not None,
         "NATIVE_G_AND_T_REQUIRED_FOR_P3_NUMERIC_VALIDATION")
    need(type(witnesses) is list and len(witnesses)==2,
         "TWO_PROFILE_SCOPED_NATIVE_WITNESSES_REQUIRED")
    part=numeric.input_parts(reference)
    cal=(numeric.calibrate(witnesses) if calibration_override is None
         else calibration_override)
    need(cal.get("schema")==numeric.SCHEMA and
         cal.get("status") in (
           "TWO_NATIVE_NUMERIC_OFFSET_WITNESSES_AGREE",
           "EMPIRICAL_PER_PROFILE_NUMERIC_AFFINE_WITNESSES"),
         "NATIVE_NUMERIC_CALIBRATION_CONTRACT")
    need(part["stable_sha256"]==cal["stable_profile_sha256"],
         "NATIVE_NUMERIC_WITNESSES_FOR_OTHER_PROFILE")
    if calibration_override is not None:
        need(cal.get("status")==
             "EMPIRICAL_PER_PROFILE_NUMERIC_AFFINE_WITNESSES" and
             cal.get("witnesses",0)>=3,
             "AFFINE_OVERRIDE_REQUIRES_THREE_NATIVE_WITNESSES")
    bound=port.verify_profile_binding(normalized,static,reference)
    observations=[]
    for idx,ev in enumerate(witnesses):
        source_parts=numeric.input_parts(ev["input"])
        need(source_parts["stable_sha256"]==part["stable_sha256"],
             "WITNESS_PROFILE_DRIFT")
        target=numeric.read_rating(ev["native"]["sim"]["players"][0])
        # Construct an evaluation request with exactly the same profile,
        # target and original per-witness iterations; never substitute
        # Mage-derived +165 or a hard-coded 60 for other profiles.
        candidates=[line.partition("=")[2] for line in ev["input"].splitlines()
                    if line.startswith("iterations=")]
        need(len(candidates)==1 and candidates[0].isdigit(),
             "WITNESS_ITERATIONS_UNOBSERVED")
        iterations=int(candidates[0])
        destination="/tmp/v066_replay_%02d.json"%idx
        proposal=port.make_request(normalized,static,cal,reference,binary_sha,
                                   target,iterations,destination)
        replay=numeric.input_parts(proposal["input"])
        need(replay["stable_sha256"]==source_parts["stable_sha256"] and
             replay["gear_override"]==source_parts["gear_override"],
             "WITNESS_NOT_REPRODUCED_FROM_MEASURED_OFFSET")
        raw=ev.get("raw_native_json")
        if raw is not None:
            need(type(raw) is bytes and json.loads(raw)==ev["native"],
                 "WITNESS_NATIVE_JSON_BYTES_MISMATCH")
        observation=port.ingest_native(proposal,ev["native"],cal,raw)
        observations.append(observation)
    total_rating,low,high=scheduler.bounds(normalized,static)
    need(total_rating==total,"P3_TO_SCHEDULER_BUDGET_DRIFT")
    source_ids=[ev.get("native_json_sha256") for ev in witnesses]
    summary={"schema":SCHEMA,"status":"READY_NUMERIC_PROFILE_SCOPED",
        "class":normalized["scenario"]["character"]["class"],
        "spec":normalized["scenario"]["character"]["spec"],
        "role":normalized["scenario"]["character"]["role"],
        "target_ilevel":normalized["scenario"]["target"]["ilevel"],
        "T_official":total,"G_native":static["G_if_complete"],
        "J":normalized["budget"]["J"],"F":normalized["budget"]["F"],
        "profile_sha256":digest_bytes(reference.encode("utf-8")),
        "scenario_digest":normalized["scenario_digest"],
        "simc_binary_sha256":binary_sha,
        "simc_revision":cal["native_revision"],
        "measured_net_gear_to_rating_offset":cal[
            "net_input_to_json2_rating_offset"],
        "two_numeric_witnesses":"VALIDATED_JSON2_NO_INDEPENDENT_EFFECT_GATE",
        "two_prior_samples":[{"input_sha256":ev.get("input_sha256"),
                              "json_sha256":source_ids[i],
                              "target":observations[i]["target"],
                              "dps_mean":observations[i]["dps_mean"],
                              "dps_sem":observations[i]["dps_sem"]}
                             for i,ev in enumerate(witnesses)],
        "profile_binding":bound,
        "effective_floor":dict(zip(scenario.STATS,low)),
        "effective_cap":dict(zip(scenario.STATS,high)),
        "missing_nontrinket_static_variants":[],
        "trinket_static_required":False,
        "item_effects_and_APL_owned_by":"SimC",
        "new_simc_calls":0,
        "original_product_v016_integrated":False,
        "cross_class_native_acceptance_claimed":False}
    return {"normalized":normalized,"budget":static,"calibration":cal,
            "profile":reference,"prior_observations":observations,
            "summary":summary}

def prepare_static(request,fillers,static_records,reference,witnesses,
                   binary_sha,declared_F_vector):
    """Static-c two-Native preflight; talent-buffed stats are observations only.

    The F vector is an explicit scenario-scoped, caller-supplied static
    attribution. This verifies its declared sum and exact input application;
    does not independently certify a consumable's in-game effect.
    """
    need(type(binary_sha) is str and scenario.HASH_RE.fullmatch(binary_sha),
         "BINARY_SHA256_REQUIRED")
    normalized=scenario.normalize(request)
    static=budget.compile_static_budget(normalized,fillers,static_records)
    need(not static["missing_nontrinket_static"] and
         not static["missing_special_fixed_static"] and
         static["G_if_complete"] is not None and
         static["budget"]["T_official"] is not None,
         "NATIVE_EXACT_G_STATIC_BUDGET_REQUIRED")
    scenario.vector(declared_F_vector,"EXPLICIT_F_STATIC_VECTOR")
    need(sum(declared_F_vector.values())==normalized["budget"]["F"],
         "DECLARED_F_STATIC_SUM_DOES_NOT_MATCH_BUDGET")
    if request["source"]["kind"]=="user_supplied":
        need(digest_bytes(reference.encode("utf8"))==
             request["source"]["profile_sha256"],
             "STATIC_PROFILE_SOURCE_SHA_DRIFT")
    binding=port.verify_profile_binding(normalized,static,reference)
    need(type(witnesses) is list and len(witnesses)==2,
         "TWO_REAL_STATIC_NATIVE_WITNESSES_REQUIRED")
    stable=numeric.input_parts(reference)["stable_sha256"]
    revision=None
    observations=[]
    for i,ev in enumerate(witnesses):
        input_text=ev["input"]
        source_parts=numeric.input_parts(input_text)
        need(source_parts["stable_sha256"]==stable,
             "STATIC_WITNESS_OTHER_PROFILE")
        doc=ev["native"]
        need(doc.get("report_version")=="2.0.0",
             "NATIVE_JSON2_REPORT_REQUIRED")
        cur_revision=doc.get("git_revision")
        need(type(cur_revision) is str and len(cur_revision)>=7,
             "NATIVE_REVISION_REQUIRED")
        if revision is None:revision=cur_revision
        need(cur_revision==revision,"STATIC_WITNESSES_SIMC_REVISION_DRIFT")
        need(ev.get("input_sha256")==digest_bytes(input_text.encode("utf8")),
             "STATIC_WITNESS_INPUT_SHA_MISMATCH")
        raw_bytes=ev.get("raw_native_json")
        need(type(raw_bytes) is bytes and json.loads(raw_bytes)==doc and
             digest_bytes(raw_bytes)==ev.get("native_json_sha256"),
             "STATIC_WITNESS_JSON2_BYTES_SHA_MISMATCH")
        lines=[line.partition("=")[2] for line in input_text.splitlines()
               if line.startswith("iterations=")]
        destinations=[line.partition("=")[2] for line in input_text.splitlines()
                      if line.startswith("json2=")]
        need(len(lines)==len(destinations)==1 and lines[0].isdigit(),
             "WITNESS_ITERATIONS_OR_JSON2_REQUIRED")
        target={k:source_parts["gear_override"][k]+declared_F_vector[k]
                for k in scenario.STATS}
        path=pathlib.Path(destinations[0])
        proposal=port.make_static_chmv_request(
            normalized,static,reference,binary_sha,revision,target,
            declared_F_vector,int(lines[0]),path)
        need(proposal["input_sha256"]==ev["input_sha256"] and
             proposal["input"]==input_text and
             proposal["raw_gear_override"]==source_parts["gear_override"],
             "STATIC_NATIVE_WITNESS_INPUT_CANNOT_REPRODUCE")
        observation=port.ingest_native(proposal,doc,
                 {"native_revision":revision},raw_bytes)
        need(observation["status"]=="PASS_NATIVE_DPS_AND_STATIC_CHMV_INPUT"
             and observation["static_rating_verified"]==target,
             "STATIC_NATIVE_C_NOT_VERIFIED")
        observations.append(observation)
    need(observations[0]["target"]!=observations[1]["target"],
         "TWO_DISTINCT_STATIC_C_WITNESSES_REQUIRED")
    total,low,high=scheduler.bounds(normalized,static)
    need(total==static["budget"]["T_official"],
         "STATIC_TO_V015_SCHEDULER_TOTAL_CHANGED")
    summary={"schema":SCHEMA,"status":"READY_STATIC_CHMV_PROFILE_SCOPED",
        "class":normalized["scenario"]["character"]["class"],
        "spec":normalized["scenario"]["character"]["spec"],
        "rating_semantics":"STATIC_CHMV_C_V1",
        "T_official":total,"G_native":static["G_if_complete"],
        "J":normalized["budget"]["J"],"F":normalized["budget"]["F"],
        "declared_F_vector":dict(declared_F_vector),
        "F_vector_attribution_independently_verified":False,
        "simc_binary_sha256":binary_sha,"simc_revision":revision,
        "profile_stable_sha256":stable,
        "two_native_static_witnesses":"REAL_JSON2_SHA_AND_INPUT_REPLAYED",
        "talent_inflated_buffed_stats_are_separate_observations":True,
        "item_effects_and_APL_owned_by":"SimC",
        "new_native_calls":0,
        "original_product_v016_integrated":False}
    return {"normalized":normalized,"budget":static,
        "calibration":{"native_revision":revision},
        "static_flask_vector":dict(declared_F_vector),
        "profile":reference,"prior_observations":observations,"summary":summary}

def propose_next_static(prepared,iterations,output_json2_path,step=100):
    """Same existing v015-derived order, now with explicit static-c semantics."""
    need(prepared.get("summary",{}).get("status")==
         "READY_STATIC_CHMV_PROFILE_SCOPED",
         "STATIC_NATIVE_PREFLIGHT_REQUIRED")
    state=scheduler.initial_state(prepared["normalized"],prepared["budget"],
            prepared["prior_observations"],step=step,scout_max=2)
    return scheduler.next_scout(state,prepared["normalized"],
         prepared["budget"],prepared["calibration"],
         prepared["profile"],prepared["summary"]["simc_binary_sha256"],
         output_json2_path,iterations,
         static_flask_vector=prepared["static_flask_vector"])

def propose_next(prepared,iterations,output_json2_path,step=100):
    """Reuse exactly v065 search policy, do not fork another scheduler."""
    normalized=prepared["normalized"]
    stat=prepared["budget"]
    cal=prepared["calibration"]
    start=scheduler.initial_state(normalized,stat,
                                  prepared["prior_observations"],
                                  step=step,scout_max=2)
    return scheduler.next_scout(start,normalized,stat,cal,
          prepared["profile"],prepared["summary"]["simc_binary_sha256"],
          output_json2_path,iterations)

def main(argv=None):
    cli=argparse.ArgumentParser()
    cli.add_argument("--scenario",type=pathlib.Path,required=True)
    cli.add_argument("--filler",type=pathlib.Path,required=True)
    cli.add_argument("--static-cache",type=pathlib.Path,required=True)
    cli.add_argument("--profile",type=pathlib.Path,required=True)
    cli.add_argument("--witness-root",type=pathlib.Path,required=True)
    cli.add_argument("--binary-sha256",required=True)
    cli.add_argument("--output",type=pathlib.Path,required=True)
    cli.add_argument("--step",type=int,default=100)
    a=cli.parse_args(argv)
    report={"schema":SCHEMA,"status":"BLOCKED","new_simc_calls":0}
    try:
        user=json.loads(a.scenario.read_text(encoding="utf8"))
        filler=json.loads(a.filler.read_text(encoding="utf8"))
        static=cache.load(a.static_cache)
        reference=a.profile.read_text(encoding="utf8")
        witnesses=load_witnesses(a.witness_root)
        prepared=prepare(user,filler,static,reference,witnesses,
                         a.binary_sha256)
        nxt=propose_next(prepared,
                 prepared["normalized"]["scenario"]["runtime"]["scout_iterations"],
                 a.output.parent/"candidate"/"result.json",step=a.step)
        report=prepared["summary"]|{"status":"READY_NEXT_SCOUT_NOT_EXECUTED",
                   "next_target":nxt["case"]["target"],
                   "next_case_key":nxt["case"]["case_key"],
                   "scout_decision":nxt["decision"]}
    except Exception as e:
        report["error"]=type(e).__name__+":"+str(e)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,sort_keys=True,indent=2,
                                   ensure_ascii=False)+"\n",encoding="utf8")
    print("V066",report["status"],"NativeCalls",0,flush=True)
    return 0 if report["status"].startswith("READY") else 3

if __name__=="__main__":
    sys.exit(main())
