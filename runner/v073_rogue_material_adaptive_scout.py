#!/usr/bin/env python3
"""v073: at most two material-distance v015-guided Rogue Native scouts.

Uses two independently confirmed v072 320-iteration measurements as anchors;
v069 numeric witnesses, v070 and v071 old 35-iteration data are only provenance.
Existing v065 policy/executor and v064 exact JSON2 ingest/cache are reused.
New 60-iteration scouts are proposals, NEVER fresh 320-iteration confirmations.
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
import v072_rogue_high_iteration_confirm as prior

SCHEMA = "v073_rogue_material_distance_two_bounded_native_scouts_v1"
SCOUT_ITERATIONS = 60
SCOUT_MAX = 2
STEP = 350
MIN_MATERIAL_DISTANCE = 0.10
NEAR_LOSS = 0.01

class Blocked(ValueError):
    pass

def need(ok, reason):
    if not ok:
        raise Blocked(reason)

def load(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def validate_prior_confirmations(prepared, official_root, scout_root, prior_native_root):
    """Archive relocation-safe, byte-hash based verification of BOTH v072 cases."""
    root = pathlib.Path(prior_native_root)
    a, b, vectors, normalized, static, requests = prior.choose_requests(
        prepared, official_root, scout_root, root)
    summary = load(root / "V072_RECEIPT.json")
    need(summary.get("status") == "PASS_TWO_ROGUE_FRESH_320_NATIVE_CONFIRMATIONS"
         and summary.get("T") == 3150
         and summary.get("historical_native_results_reused") == 4
         and len(summary.get("fresh", [])) == 2
         and summary.get("native_attempts_total_durable") == 2
         and summary.get("cache_replay_all_verified") is True,
         "V072_TWO_HIGH_NATIVE_ACCEPTANCE_REQUIRED")
    observed = []
    for i, request in enumerate(requests):
        folder = root / ("confirm_%02d" % i)
        source = (folder / "input.simc").read_bytes()
        raw = (folder / "result.json").read_bytes()
        receipt_raw = (folder / "native_receipt.json").read_bytes()
        receipt = json.loads(receipt_raw)
        old = summary["fresh"][i]
        source_part = numeric.input_parts(source.decode("utf8"))
        prepared_part = numeric.input_parts(request["input"])
        need(source_part["stable_sha256"] == prepared_part["stable_sha256"] ==
             prepared["calibration"]["stable_profile_sha256"] and
             source_part["gear_override"] == prepared_part["gear_override"] and
             source.decode("utf8").splitlines().count("iterations=320") == 1,
             "V072_RELOCATED_INPUT_PROFILE_OR_ITERATIONS_CHANGED")
        need(digest(source) == receipt.get("input_sha256") ==
             old.get("input_sha256"), "V072_ORIGINAL_INPUT_SHA_CHANGED")
        need(digest(raw) == receipt.get("native_json_sha256") ==
             old.get("native_json_sha256"), "V072_NATIVE_BYTES_SHA_CHANGED")
        need(digest(receipt_raw) == old.get("native_receipt_sha256"),
             "V072_NATIVE_RECEIPT_BYTES_CHANGED")
        for field in ("case_key", "target", "iterations", "simc_binary_sha256",
                      "scenario_digest", "native_revision"):
            need(receipt.get(field) == request.get(field),
                 "V072_NATIVE_CASE_IDENTITY_CHANGED:" + field)
        need(receipt.get("status") == "PASS_NATIVE_DPS_AND_RATING"
             and receipt.get("simc_seed") == old.get("seed")
             and old.get("rating_actual") == request["target"],
             "V072_RECEIPT_OR_FINAL_RATING_CHANGED")
        obs = port.ingest_native(request, json.loads(raw),
                                 prepared["calibration"], raw)
        for field in ("dps_mean", "dps_sem", "dps_samples", "rating_actual",
                      "native_json_sha256"):
            need(obs.get(field) == receipt.get(field) == old.get(field),
                 "V072_VERIFIED_NATIVE_MEASUREMENT_CHANGED:" + field)
        need(obs["dps_samples"] >= 300 and obs["iterations"] == 320,
             "V072_HIGH_ITERATION_SAMPLES_NOT_VALID")
        obs["simc_seed"] = receipt.get("simc_seed")
        observed.append(obs)
    need(set(scheduler.key(o["target"]) for o in observed) ==
         {scheduler.key(a["target"]), scheduler.key(b["target"])},
         "V072_PAIR_NOT_THE_SAME_USER_PROFILE")
    return normalized, static, observed

def moved(a, b):
    return sum(abs(a[k] - b[k]) for k in a) // 2

def scout_summary(anchors, scouts, total):
    """Observations only; cross-iteration ranking has not been confirmed."""
    leader = max(anchors, key=lambda x: x["dps_mean"])
    rows = []
    for obs in scouts:
        delta = obs["dps_mean"] - leader["dps_mean"]
        half = 1.9599639854 * math.hypot(
            obs["dps_sem"], leader["dps_sem"])
        distance = moved(obs["target"], leader["target"])
        observed_loss = (leader["dps_mean"] - obs["dps_mean"]) / leader["dps_mean"]
        rows.append({"target": obs["target"], "rating_moved_from_high_precision_A": distance,
                     "moved_fraction": distance / total,
                     "scout_minus_anchor_dps": delta,
                     "approx_95pct_ci": [delta - half, delta + half],
                     "near_1pct_by_observed_means_only": observed_loss <= NEAR_LOSS,
                     "materially_different_by_rating": distance >=
                       math.ceil(MIN_MATERIAL_DISTANCE * total),
                     "may_warrant_fresh_confirmation": distance >=
                       math.ceil(MIN_MATERIAL_DISTANCE * total) and
                       observed_loss <= NEAR_LOSS,
                     "statistically_proven_near_best_alternative": False})
    return {"high_precision_anchor": {"target": leader["target"],
              "dps_mean": leader["dps_mean"], "dps_sem": leader["dps_sem"],
              "samples": leader["dps_samples"]},
            "exploratory_results": rows,
            "global_optimum_proven": False,
            "material_alternative_proven": False,
            "different_iteration_counts_not_pooled": True}

def run(witness_root, official_root, scout_root, prior_native_root,
        output, binary=None, cache_only=False, cancel_file=None):
    output = pathlib.Path(output)
    output.mkdir(parents=True, exist_ok=True)
    receipt_path = output / "V073_RECEIPT.json"
    result = {"schema": SCHEMA, "status": "BLOCKED",
              "new_native_calls_this_invocation": 0,
              "new_attempts_started_this_invocation": 0,
              "historical_native_reused": 0,
              "scout_iterations": SCOUT_ITERATIONS, "scout_cap": SCOUT_MAX,
              "scout_step_rating": STEP,
              "official_formula": "T=G+J+F",
              "global_optimum_proven": False}
    try:
        prepared = official.prepare(witness_root, probe.BIN_SHA)
        normalized, static, anchors = validate_prior_confirmations(
            prepared, official_root, scout_root, prior_native_root)
        leader = max(anchors, key=lambda x: x["dps_mean"])
        need(leader["target"] == {"crit_rating":813,"haste_rating":913,
                 "mastery_rating":712,"versatility_rating":712},
             "V072_OBSERVED_LEADER_CHANGED")
        total = static["budget"]["T_official"]
        need(total == 3150 and static["G_if_complete"] == 2847 and
             static["budget"]["J"] == 138 and static["budget"]["F"] == 165,
             "OFFICIAL_GJF_BUDGET_CHANGED")
        state = scheduler.initial_state(normalized, static, anchors, step=STEP,
                                         scout_max=SCOUT_MAX, confirmation_runs=2)
        seal_data = {"schema": SCHEMA,
           "scenario_digest": normalized["scenario_digest"],
           "stable_profile_sha256": prepared["calibration"]["stable_profile_sha256"],
           "simc_revision": prepared["calibration"]["native_revision"],
           "binary_sha256": probe.BIN_SHA,
           "prior_native_sha256s": [x["native_json_sha256"] for x in anchors],
           "step": STEP, "iterations": SCOUT_ITERATIONS, "cap": SCOUT_MAX}
        result.update({"status": "PASS_MATERIAL_DISTANCE_PLAN_READY_ZERO_NATIVE",
             "historical_native_reused": 6,
             "historical_breakdown": {"v069_calibration": 2,
                  "v070_official_seed": 1, "v071_initial_scout": 1,
                  "v072_high_precision": 2},
             "G": 2847, "J": 138, "F": 165, "T": total,
             "special_L": static["locked_L_when_all_specials_observed"],
             "numeric_offset": prepared["calibration"]["net_input_to_json2_rating_offset"],
             "scoped_scenario_digest": normalized["scenario_digest"],
             "two_independent_high_precision_anchors":
               [{"target": x["target"], "dps_mean": x["dps_mean"],
                 "dps_sem": x["dps_sem"], "native_json_sha256": x["native_json_sha256"],
                 "samples": x["dps_samples"]} for x in anchors]})
        if binary is None:
            proposal = scheduler.next_scout(state, normalized, static,
                        prepared["calibration"], prepared["reference"],
                        probe.BIN_SHA, output / "scout_00" / "result.json",
                        SCOUT_ITERATIONS)
            need(moved(proposal["case"]["target"], leader["target"]) >=
                 math.ceil(total * MIN_MATERIAL_DISTANCE),
                 "FIRST_SCOUT_NOT_MATERIAL_DISTANCE")
            result["first_scout_target"] = proposal["case"]["target"]
            result["first_scout_distance"] = moved(proposal["case"]["target"],
                                                   leader["target"])
        else:
            binary = pathlib.Path(binary).resolve()
            need(binary.is_file() and digest(binary.read_bytes()) == probe.BIN_SHA,
                 "PINNED_SIMC_BINARY_CHANGED")
            seal = output / "V073_IDENTITY.json"
            if seal.exists():
                need(load(seal) == seal_data, "RESUME_PROFILE_OR_POLICY_CHANGED")
            else:
                need(not any((output / ("scout_%02d" % i)).exists()
                             for i in range(SCOUT_MAX)),
                     "PREEXISTING_SCOUT_WITHOUT_SEAL")
                engine.write_atomic(seal, seal_data)
            progress_file = output / "V065_PROGRESS.json"
            progress = {"schema": SCHEMA,
                        "scenario_digest": normalized["scenario_digest"],
                        "prior_native_sha256s": seal_data["prior_native_sha256s"],
                        "scout_step_rating": STEP, "scout_iterations": SCOUT_ITERATIONS,
                        "native_attempts": 0, "new_native_max": SCOUT_MAX,
                        "status": "READY"}
            if progress_file.exists():
                previous = load(progress_file)
                need(all(previous.get(k) == progress[k] for k in
                         ("schema", "scenario_digest", "prior_native_sha256s",
                          "scout_step_rating", "scout_iterations", "new_native_max"))
                     and type(previous.get("native_attempts")) is int
                     and 0 <= previous["native_attempts"] <= SCOUT_MAX,
                     "RESUME_PROGRESS_OR_ATTEMPT_LIMIT_CHANGED")
                progress["native_attempts"] = previous["native_attempts"]
            else:
                engine.write_atomic(progress_file, progress)
            scouts = []
            for i in range(SCOUT_MAX):
                folder = output / ("scout_%02d" % i)
                offer = scheduler.next_scout(state, normalized, static,
                    prepared["calibration"], prepared["reference"], probe.BIN_SHA,
                    folder / "result.json", SCOUT_ITERATIONS)
                request = offer["case"]
                distance = moved(request["target"], leader["target"])
                need(distance >= math.ceil(MIN_MATERIAL_DISTANCE * total),
                     "SCHEDULER_SCOUT_BELOW_MATERIAL_DISTANCE")
                need(request["case_key"] not in
                     {r["case_key"] for r in anchors + scouts},
                     "DUPLICATE_SCOUT_NATIVE_CASE")
                if cancel_file is not None:
                    need(not pathlib.Path(cancel_file).exists(), "USER_CANCEL_FILE")
                if not ((folder / "result.json").exists() or
                        (folder / "native_receipt.json").exists()):
                    need(not (folder / "input.simc").exists(),
                         "INCOMPLETE_PREVIOUS_NATIVE_ATTEMPT_MANUAL_RECOVERY")
                    need(not cache_only, "CACHE_ONLY_REFUSES_NEW_NATIVE")
                    need(progress["native_attempts"] < SCOUT_MAX,
                         "BOUND_NATIVE_ATTEMPTS_EXHAUSTED")
                    result["new_attempts_started_this_invocation"] += 1
                obs = engine.execute_one(request, prepared["calibration"],
                      binary, folder, progress, cancel_file=cancel_file,
                      cache_only=cache_only)
                need(obs["iterations"] == SCOUT_ITERATIONS and
                     obs["dps_samples"] >= 40 and
                     obs["rating_actual"] == request["target"],
                     "NATIVE_SCOUT_NOT_FULL_ITERATION_OR_RATING_MATCH")
                result["new_native_calls_this_invocation"] += int(
                     obs.get("source") == "NEW_NATIVE")
                state = scheduler.accept_scout(state, request, obs)
                scouts.append(obs)
                result["scout_completed"] = len(scouts)
                result["status"] = "PARTIAL_SCOUT_RECORDED"
                engine.write_atomic(receipt_path, result)
            result.update({"status": "PASS_TWO_MATERIAL_DISTANCE_ROGUE_NATIVE_SCOUTS",
              "scouts": [{"target": r["target"], "source": r["source"],
                          "dps_mean": r["dps_mean"], "dps_sem": r["dps_sem"],
                          "dps_samples": r["dps_samples"],
                          "rating_actual": r["rating_actual"],
                          "native_json_sha256": r["native_json_sha256"],
                          "simc_seed": r.get("simc_seed")} for r in scouts],
              "comparison": scout_summary(anchors, scouts, total),
              "native_attempts_total_durable": progress["native_attempts"],
              "all_cached_sha_verified": all(r["source"] ==
                        "CACHED_VERIFIED_NATIVE" for r in scouts)})
    except Exception as exc:
        result["status"] = "BLOCKED_OR_PARTIAL"
        result["error"] = type(exc).__name__ + ":" + str(exc)
        f = output / "V065_PROGRESS.json"
        if f.is_file():
            try:
                result["native_attempts_total_durable"] = load(f).get("native_attempts")
            except (OSError, ValueError):
                result["durable_progress_unreadable"] = True
    engine.write_atomic(receipt_path, result)
    print("V073", result["status"], "new_native",
          result["new_native_calls_this_invocation"], flush=True)
    return 0 if result["status"].startswith("PASS") else 3

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--witness-root", required=True, type=pathlib.Path)
    p.add_argument("--prior-official", required=True, type=pathlib.Path)
    p.add_argument("--prior-scout", required=True, type=pathlib.Path)
    p.add_argument("--prior-native", required=True, type=pathlib.Path)
    p.add_argument("--out", required=True, type=pathlib.Path)
    p.add_argument("--binary", type=pathlib.Path)
    p.add_argument("--cache-only", action="store_true")
    p.add_argument("--cancel-file", type=pathlib.Path)
    a = p.parse_args(argv)
    return run(a.witness_root, a.prior_official, a.prior_scout, a.prior_native,
               a.out, a.binary, a.cache_only, a.cancel_file)

if __name__ == "__main__":
    sys.exit(main())
