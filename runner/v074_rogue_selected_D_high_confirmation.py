#!/usr/bin/env python3
"""v074: one NEW independent 320-iteration confirmation of v073 selected Rogue D.

History: v069/v070/v071 provenance -> v072 A/B fresh 320 -> v073 C/D
fresh 60-iteration scouts. This never relabels a 60-iteration scout as a
confirmation, does not rerun v072 A, or revise the original v015 scheduler.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import pathlib
import sys

import v063_numeric_injection as numeric
import v064_adaptive_evaluator_port as port
import v065_original_scheduler_native_bridge as engine
import v065_v015_scheduler_adapter as scheduler
import v068_rogue_two_native_probe as probe
import v069_rogue_official_budget_native as official
import v073_rogue_material_adaptive_scout as v073

SCHEMA = "v074_rogue_selected_D_independent_320_native_v1"
ITERATIONS = 320
CAP = 1
EXPECTED_D = {"crit_rating": 1163, "haste_rating": 913,
              "mastery_rating": 712, "versatility_rating": 362}
EXPECTED_A = {"crit_rating": 813, "haste_rating": 913,
              "mastery_rating": 712, "versatility_rating": 712}

class Blocked(ValueError):
    pass

def need(condition, reason):
    if not condition:
        raise Blocked(reason)

def load(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf8"))

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def replay_prior_scouts(prepared, normalized, static, anchors, prior_scouts):
    """Verify original v073 Native receipts and replay v015 choice without SimC."""
    root = pathlib.Path(prior_scouts)
    summary = load(root / "V073_RECEIPT.json")
    need(summary.get("status") == "PASS_TWO_MATERIAL_DISTANCE_ROGUE_NATIVE_SCOUTS"
         and summary.get("T") == 3150 and
         summary.get("scout_iterations") == 60 and
         summary.get("scout_cap") == 2 and
         summary.get("scout_step_rating") == 350 and
         summary.get("native_attempts_total_durable") == 2 and
         summary.get("all_cached_sha_verified") is True and
         summary.get("historical_native_reused") == 6 and
         len(summary.get("scouts", [])) == 2,
         "V073_REAL_TWO_SCOUT_ACCEPTANCE_NOT_PRESENT")
    state = scheduler.initial_state(normalized, static, anchors, step=350,
                                   scout_max=2, confirmation_runs=2)
    observations = []
    for index in range(2):
        folder = root / ("scout_%02d" % index)
        offer = scheduler.next_scout(state, normalized, static,
                 prepared["calibration"], prepared["reference"], probe.BIN_SHA,
                 folder / "result.json", 60)
        req = offer["case"]
        source = (folder / "input.simc").read_bytes()
        raw = (folder / "result.json").read_bytes()
        original_receipt_bytes = (folder / "native_receipt.json").read_bytes()
        receipt = json.loads(original_receipt_bytes)
        old = summary["scouts"][index]
        actual_part = numeric.input_parts(source.decode("utf8"))
        req_part = numeric.input_parts(req["input"])
        need(actual_part["stable_sha256"] == req_part["stable_sha256"]
             == prepared["calibration"]["stable_profile_sha256"] and
             actual_part["gear_override"] == req_part["gear_override"] and
             source.decode("utf8").splitlines().count("iterations=60") == 1,
             "V073_SCOUT_INPUT_GEAR_OR_ITERATION_DRIFT")
        need(sha(source) == receipt.get("input_sha256") and
             sha(raw) == receipt.get("native_json_sha256") ==
             old.get("native_json_sha256"),
             "V073_SCOUT_INPUT_OR_JSON2_SHA_MISMATCH")
        need(receipt.get("status") == "PASS_NATIVE_DPS_AND_RATING" and
             receipt.get("case_key") == req["case_key"] and
             receipt.get("scenario_digest") == normalized["scenario_digest"] and
             receipt.get("simc_binary_sha256") == probe.BIN_SHA and
             receipt.get("iterations") == 60 and
             receipt.get("target") == req["target"],
             "V073_SCOUT_NATIVE_RECEIPT_IDENTITY_DRIFT")
        obs = port.ingest_native(req, json.loads(raw),
                                 prepared["calibration"], raw)
        for k in ("dps_mean", "dps_sem", "dps_samples",
                  "rating_actual", "native_json_sha256"):
            need(receipt.get(k) == obs.get(k) == old.get(k),
                 "V073_SCOUT_NUMERIC_CHANGED:" + k)
        need(obs["dps_samples"] >= 40 and
             obs["rating_actual"] == req["target"] ==
             old["target"] and receipt.get("simc_seed") ==
             old.get("simc_seed"),
             "V073_SCOUT_SEED_OR_FINAL_RATING_DRIFT")
        obs["simc_seed"] = receipt.get("simc_seed")
        state = scheduler.accept_scout(state, req, obs)
        observations.append(obs)
    need(observations[0]["target"] ==
         {"crit_rating": 463, "haste_rating": 913,
          "mastery_rating": 712, "versatility_rating": 1062}
         and observations[1]["target"] == EXPECTED_D and
         observations[1]["dps_mean"] > observations[0]["dps_mean"] and
         v073.moved(anchors[0]["target"], EXPECTED_D) == 350,
         "SCOUT_D_SELECTION_OR_MATERIAL_DIFFERENCE_CHANGED")
    return observations

def comparison(anchor, confirmed, total):
    """Fresh held-out D versus the existing high-repeat A. No pooling of scout."""
    need(anchor["target"] == EXPECTED_A and
         confirmed["target"] == EXPECTED_D, "CONFIRMATION_PAIR_DRIFT")
    delta = confirmed["dps_mean"] - anchor["dps_mean"]
    half = 1.9599639854 * math.hypot(
           anchor["dps_sem"], confirmed["dps_sem"])
    seeds_distinct = (anchor.get("simc_seed") is not None
        and confirmed.get("simc_seed") is not None
        and anchor["simc_seed"] != confirmed["simc_seed"])
    former = scheduler.key(anchor["target"])
    latter = scheduler.key(confirmed["target"])
    judgment = scheduler.fresh_confirmation_judgment(
       [former, latter], {former: anchor, latter: confirmed})
    need(judgment["distinct_simc_seeds_observed"] == seeds_distinct
         and judgment["first_minus_second_dps"] == -delta,
         "V015_CONFIRMATION_JUDGMENT_DISAGREES")
    return {
       "comparison_type": "one_selected_candidate_held_out_320_vs_prior_independent_320",
       "selection_basis": "v073_two_60_iteration_scouts_ONLY",
       "v073_scout_data_pooled_with_confirmed_D": False,
       "D_minus_A_dps": delta,
       "D_minus_A_pct_of_A": 100 * delta / anchor["dps_mean"],
       "approx_independent_normal_95pct_ci": [delta-half, delta+half],
       "approx_95pct_halfwidth": half,
       "fresh_high_iterations_D": ITERATIONS,
       "already_high_iterations_A": 320,
       "distinct_native_seeds": seeds_distinct,
       "pairwise_direction_supported_by_fresh_approx95":
           judgment["pairwise_direction_supported"],
       "D_superior_pairwise_unadjusted_approx95":
           seeds_distinct and delta-half > 0,
       "material_rating_transfer": v073.moved(anchor["target"], confirmed["target"]),
       "material_fraction_of_T": v073.moved(anchor["target"],confirmed["target"])/total,
       "preselection_from_two_scouts_disclosed": True,
       "multiple_comparison_adjusted_CI": None,
       "global_optimum_proven": False,
       "material_near_best_alternative_globally_proven": False,
       "v015_pair_judgment": judgment,
    }

def run(witness_root, prior_official, prior_first_scout, prior_high,
        prior_material_scouts, out, binary=None, cache_only=False, cancel_file=None):
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    report = out / "V074_RECEIPT.json"
    summary = {
       "schema": SCHEMA, "status": "BLOCKED",
       "confirm_target": EXPECTED_D, "confirm_iterations": ITERATIONS,
       "new_native_cap": CAP, "new_native_calls_this_invocation": 0,
       "new_attempts_started_this_invocation": 0,
       "historical_native_results_attested": 0,
       "official_formula": "T=G+J+F",
       "global_optimum_proven": False,
    }
    try:
        prepared = official.prepare(witness_root, probe.BIN_SHA)
        normalized, static, anchors = v073.validate_prior_confirmations(
            prepared, prior_official, prior_first_scout, prior_high)
        need(anchors[0]["target"] == EXPECTED_A and
             anchors[1]["target"] == {"crit_rating":713,"haste_rating":913,
                  "mastery_rating":712,"versatility_rating":812},
             "V072_TWO_320_ANCHORS_CHANGED")
        scouts = replay_prior_scouts(prepared, normalized, static,
                                     anchors, prior_material_scouts)
        need(static["budget"]["T_official"] == 3150
             and static["G_if_complete"] == 2847
             and static["budget"]["J"] == 138
             and static["budget"]["F"] == 165 and
             static["locked_L_when_all_specials_observed"] ==
               {"crit_rating":100,"haste_rating":201,
                "mastery_rating":0,"versatility_rating":0} and
             static["budget"]["oil_stays_OUTSIDE_T"] is True,
             "OFFICIAL_RATING_BUDGET_OR_FLOORS_DRIFT")
        request = port.make_request(normalized, static, prepared["calibration"],
                  prepared["reference"], probe.BIN_SHA, EXPECTED_D,
                  ITERATIONS, out / "confirm_D" / "result.json")
        need(request["target"] == EXPECTED_D and
             request["case_key"] not in {x["case_key"] for x in anchors+scouts}
             and request["iterations"] == 320,
             "HIGH_CONFIRM_REQUEST_NOT_DISTINCT")
        anchor = anchors[0]
        summary.update({
           "status": "PASS_SELECTED_D_CONFIRM_PLAN_ZERO_NATIVE",
           "historical_native_results_attested": 8,
           "historical_breakdown": {
              "v069_calibration_numeric":2,"v070_official":1,
              "v071_first_scout":1,"v072_high_iterations":2,
              "v073_material_scouts":2},
           "T":3150,"G":2847,"J":138,"F":165,
           "special_L":static["locked_L_when_all_specials_observed"],
           "profile_offset":prepared["calibration"]["net_input_to_json2_rating_offset"],
           "scenario_digest":normalized["scenario_digest"],
           "simc_binary_sha256":probe.BIN_SHA,
           "prior_v072_A": {"target":anchor["target"],
             "dps_mean":anchor["dps_mean"],"dps_sem":anchor["dps_sem"],
             "dps_samples":anchor["dps_samples"],
             "seed":anchor.get("simc_seed"),
             "native_json_sha256":anchor["native_json_sha256"]},
           "selected_from_v073_two_60_scouts": [{
             "target":x["target"],"dps_mean":x["dps_mean"],
             "dps_sem":x["dps_sem"],"dps_samples":x["dps_samples"],
             "native_json_sha256":x["native_json_sha256"]}
             for x in scouts],
           "confirm_case_key":request["case_key"],
           "confirm_input_sha256":request["input_sha256"],
        })
        if binary is not None:
            binary = pathlib.Path(binary).resolve()
            need(binary.is_file() and sha(binary.read_bytes()) == probe.BIN_SHA,
                 "PINNED_SIMC_BINARY_SHA_CHANGED")
            seal = out / "V074_IDENTITY.json"
            ident = {
               "schema":SCHEMA,"scenario_digest":normalized["scenario_digest"],
               "stable_profile_sha256":prepared["calibration"]["stable_profile_sha256"],
               "simc_revision":prepared["calibration"]["native_revision"],
               "binary_sha256":probe.BIN_SHA,
               "v072_anchor_sha256":anchor["native_json_sha256"],
               "v073_selected_scout_sha256":scouts[1]["native_json_sha256"],
               "target":EXPECTED_D,"input_sha256":request["input_sha256"],
               "case_key":request["case_key"],"iterations":ITERATIONS,"native_cap":CAP
            }
            if seal.exists():
                need(load(seal) == ident, "RESUME_IDENTITY_CONFLICT")
            else:
                need(not (out/"confirm_D").exists(),
                     "PREEXISTING_RESULT_WITHOUT_IDENTITY")
                engine.write_atomic(seal, ident)
            progress_path = out / "V065_PROGRESS.json"
            progress = {
               "schema":SCHEMA,"scenario_digest":normalized["scenario_digest"],
               "case_key":request["case_key"],"input_sha256":request["input_sha256"],
               "native_cap":CAP,"native_attempts":0,"status":"READY"
            }
            if progress_path.exists():
                old = load(progress_path)
                need(all(old.get(k)==progress[k] for k in
                     ("schema","scenario_digest","case_key","input_sha256","native_cap"))
                     and type(old.get("native_attempts")) is int
                     and 0 <= old["native_attempts"] <= CAP,
                     "DURABLE_PROGRESS_IDENTITY_OR_CAP_CONFLICT")
                progress["native_attempts"] = old["native_attempts"]
            else:
                engine.write_atomic(progress_path, progress)
            folder = out/"confirm_D"
            prior_result = ((folder/"result.json").exists()
                         or (folder/"native_receipt.json").exists())
            if not prior_result:
                need(not (folder/"input.simc").exists(),
                     "INCOMPLETE_PRIOR_NATIVE_MANUAL_RECOVERY")
                need(not cache_only, "CACHE_ONLY_REFUSES_NEW_NATIVE")
                need(progress["native_attempts"] < CAP,
                     "ONE_NATIVE_ATTEMPT_ALREADY_EXHAUSTED")
                summary["new_attempts_started_this_invocation"] = 1
            result = engine.execute_one(request, prepared["calibration"], binary,
                     folder, progress, cancel_file=cancel_file,
                     cache_only=cache_only)
            summary["new_native_calls_this_invocation"] = int(
                  result.get("source") == "NEW_NATIVE")
            need(result["iterations"] == ITERATIONS and
                 result["dps_samples"] >= 300 and
                 result["rating_actual"] == EXPECTED_D and
                 result["target"] == EXPECTED_D and
                 result.get("simc_seed") not in {
                   anchors[0].get("simc_seed"),anchors[1].get("simc_seed"),
                   scouts[0].get("simc_seed"),scouts[1].get("simc_seed")},
                 "INDEPENDENT_320_NATIVE_OR_FINAL_RATING_INVALID")
            stats = comparison(anchor, result, 3150)
            summary.update({
                "status":"PASS_ONE_SELECTED_D_FRESH_320_NATIVE_CONFIRMATION",
                "confirmed_D": {"source":result["source"],
                     "target":result["target"],"rating_actual":result["rating_actual"],
                     "iterations":result["iterations"],
                     "dps_mean":result["dps_mean"],"dps_sem":result["dps_sem"],
                     "dps_samples":result["dps_samples"],
                     "seed":result.get("simc_seed"),
                     "input_sha256":result["input_sha256"],
                     "native_json_sha256":result["native_json_sha256"],
                     "native_receipt_sha256":sha(
                        (folder/"native_receipt.json").read_bytes())},
                "comparison":stats,
                "native_attempts_total_durable":progress["native_attempts"],
                "sha_checked_cache_replay":result.get("source")==
                               "CACHED_VERIFIED_NATIVE",
            })
    except Exception as exc:
        summary["status"]="BLOCKED_OR_PARTIAL"
        summary["error"]=type(exc).__name__+":"+str(exc)
        f=out/"V065_PROGRESS.json"
        if f.exists():
            try:
                summary["native_attempts_total_durable"]=load(f).get("native_attempts")
            except (OSError,ValueError):
                summary["progress_read_error"]=True
    engine.write_atomic(report,summary)
    print("V074",summary["status"],"new_native",
          summary["new_native_calls_this_invocation"],flush=True)
    return 0 if summary["status"].startswith("PASS") else 3

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--witness-root",required=True,type=pathlib.Path)
    p.add_argument("--prior-official",required=True,type=pathlib.Path)
    p.add_argument("--prior-scout",required=True,type=pathlib.Path)
    p.add_argument("--prior-high",required=True,type=pathlib.Path)
    p.add_argument("--prior-material",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    p.add_argument("--binary",type=pathlib.Path)
    p.add_argument("--cache-only",action="store_true")
    p.add_argument("--cancel-file",type=pathlib.Path)
    a=p.parse_args(argv)
    return run(a.witness_root,a.prior_official,a.prior_scout,a.prior_high,
               a.prior_material,a.out,a.binary,a.cache_only,a.cancel_file)

if __name__=="__main__":
    sys.exit(main())
