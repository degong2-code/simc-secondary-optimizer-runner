#!/usr/bin/env python3
"""v072: exactly two fresh high-iteration confirmations of the v071 Rogue pair.

Reuse actual v069/v070/v071 JSON2; no new scheduler or effect engine. Only
the permitted runtime envelope is changed (120 -> 320 confirmation iterations).
Every cached result is checked by the existing v064/v065 executor; historical
artifact relocation is handled by comparing immutable source and numeric data,
not by pretending that a moved json2 output path has the same input SHA.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import pathlib
import sys

import v061_scenario_contract as scenario
import v062_static_budget_bridge as budgets
import v063_numeric_injection as numeric
import v064_adaptive_evaluator_port as port
import v065_original_scheduler_native_bridge as engine
import v065_v015_scheduler_adapter as scheduler
import v068_rogue_two_native_probe as probe
import v069_rogue_official_budget_native as official
import v071_rogue_adaptive_first_scout as v071

SCHEMA = "v072_rogue_two_independent_high_iteration_native_v1"
ITERATIONS = 320
CAP = 2
V071_NEW_JSON_SHA = "6db7cad804a2c01bb855d3063b9c3e6f71653d4484d853c380c4a541649b95b4"

class Blocked(ValueError):
    pass

def need(value, reason):
    if not value:
        raise Blocked(reason)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read_json(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf8"))

def earlier_pair(prepared, prior_official, prior_scout):
    """Independently attest relocated historical bytes with original runtime."""
    anchor = v071.verified_anchor(prepared, prior_official)
    old_normalized = prepared["normalized"]
    static = prepared["budget"]
    cal = prepared["calibration"]
    root = pathlib.Path(prior_scout)
    state = scheduler.initial_state(old_normalized, static, [anchor],
                                    step=100, scout_max=1, confirmation_runs=2)
    request = scheduler.next_scout(
        state, old_normalized, static, cal, prepared["reference"],
        probe.BIN_SHA, root / "scout_00" / "result.json", 35)["case"]
    folder = root / "scout_00"
    prior_source = (folder / "input.simc").read_bytes()
    prior_raw = (folder / "result.json").read_bytes()
    old = read_json(folder / "native_receipt.json")
    summary = read_json(root / "V071_RECEIPT.json")
    old_part = numeric.input_parts(prior_source.decode("utf8"))
    request_part = numeric.input_parts(request["input"])
    need(old_part["stable_sha256"] == request_part["stable_sha256"] ==
         cal["stable_profile_sha256"], "PRIOR_SCOUT_PROFILE_CHANGED")
    need(old_part["gear_override"] == request_part["gear_override"] and
         prior_source.decode("utf8").splitlines().count("iterations=35") == 1,
         "PRIOR_SCOUT_RATING_OR_ITERATIONS_CHANGED")
    need(sha(prior_source) == old.get("input_sha256"), "PRIOR_SCOUT_INPUT_SHA_CHANGED")
    need(sha(prior_raw) == old.get("native_json_sha256") == V071_NEW_JSON_SHA,
         "PRIOR_SCOUT_NATIVE_SHA_CHANGED")
    need(old.get("status") == "PASS_NATIVE_DPS_AND_RATING" and
         old.get("case_key") == request["case_key"] and
         old.get("scenario_digest") == request["scenario_digest"] and
         old.get("simc_binary_sha256") == probe.BIN_SHA and
         old.get("iterations") == 35 and
         old.get("target") == request["target"], "PRIOR_SCOUT_RECEIPT_IDENTITY")
    observed = port.ingest_native(request, json.loads(prior_raw), cal, prior_raw)
    for k in ("dps_mean", "dps_sem", "dps_samples", "rating_actual", "native_revision"):
        need(old.get(k) == observed[k], "PRIOR_SCOUT_RESULT_DRIFT:" + k)
    need(summary.get("status") == "PASS_ONE_ROGUE_ADAPTIVE_REAL_NATIVE_DPS_AND_CHMV"
         and summary.get("new_scout", {}).get("native_json_sha256") == sha(prior_raw)
         and summary["new_scout"]["target"] == observed["target"]
         and summary["new_scout"]["dps_mean"] == observed["dps_mean"]
         and summary["new_scout"]["dps_sem"] == observed["dps_sem"],
         "PRIOR_V071_SUMMARY_NOT_MATCHED")
    need(anchor["target"] == {"crit_rating": 813, "haste_rating": 913,
         "mastery_rating": 712, "versatility_rating": 712} and
         observed["target"] == {"crit_rating": 713, "haste_rating": 913,
         "mastery_rating": 712, "versatility_rating": 812},
         "EXACT_USER_PAIR_CHANGED")
    return anchor, observed

def high_iteration_context(prepared):
    """Only runtime policy changes; recompute P1/P2 scenario-bound identity."""
    old = prepared["normalized"]["scenario"]
    cfg = json.loads(json.dumps(old))
    cfg["runtime"]["confirm_iterations"] = ITERATIONS
    cfg["runtime"]["max_native_calls"] = CAP
    normalized = scenario.normalize(cfg)
    need(normalized["scenario"]["runtime"]["scout_iterations"] == 35 and
         normalized["scenario"]["runtime"]["confirm_iterations"] == 320 and
         normalized["scenario"]["runtime"]["max_native_calls"] == 2,
         "HIGH_ITERATION_POLICY_NOT_EXPLICIT")
    same = json.loads(json.dumps(normalized["scenario"]))
    same["runtime"] = old["runtime"]
    need(same == old, "USER_GEAR_TALENTS_COMBAT_OR_CONSUMABLE_DRIFT")
    entries = official.parse_exact_input(prepared["reference"])
    fixed = set(official.TIER) | set(official.SPECIAL) | set(official.CRAFTED) | set(official.TRINKETS)
    filler = [row for slot, row in entries.items() if slot not in fixed]
    static = budgets.compile_static_budget(normalized, filler,
                                           prepared["native_static_cache"])
    original = prepared["budget"]
    need(static["G_if_complete"] == original["G_if_complete"] == 2847 and
         static["budget"]["J"] == 138 and static["budget"]["F"] == 165 and
         static["budget"]["T_official"] == original["budget"]["T_official"] == 3150
         and static["locked_L_when_all_specials_observed"] ==
         original["locked_L_when_all_specials_observed"] ==
         {"crit_rating": 100, "haste_rating": 201,
          "mastery_rating": 0, "versatility_rating": 0} and
         not static["missing_nontrinket_static"] and
         static["budget"]["oil_stays_OUTSIDE_T"] is True,
         "OFFICIAL_GJF_OR_SPECIAL_L_CHANGED")
    return normalized, static

def choose_requests(prepared, prior_official, prior_scout, out):
    anchor, scout = earlier_pair(prepared, prior_official, prior_scout)
    old_state = scheduler.initial_state(prepared["normalized"], prepared["budget"],
                                        [anchor, scout], step=100,
                                        scout_max=0, confirmation_runs=2)
    total, lower, upper = scheduler.bounds(prepared["normalized"], prepared["budget"])
    rows = scheduler.observations_by_vector(old_state["observations"], total, lower, upper)
    vectors = scheduler.confirmation_pair(rows, total, lower, upper)
    need(set(vectors) == {scheduler.key(anchor["target"]), scheduler.key(scout["target"])},
         "V015_CONFIRMATION_PAIR_DIFFERENT")
    normalized, static = high_iteration_context(prepared)
    requests = [port.make_request(normalized, static, prepared["calibration"],
                prepared["reference"], probe.BIN_SHA,
                scheduler.to_target(vector), ITERATIONS,
                pathlib.Path(out) / ("confirm_%02d" % i) / "result.json")
                for i, vector in enumerate(vectors)]
    need(len(requests) == CAP and requests[0]["case_key"] != requests[1]["case_key"],
         "HIGH_CONFIRM_DUPLICATE_OR_UNBOUNDED")
    return anchor, scout, vectors, normalized, static, requests

def comparison(first, second):
    """Descriptive independent-normal comparison; not a global optimum test."""
    delta = first["dps_mean"] - second["dps_mean"]
    half = 1.9599639854 * math.hypot(first["dps_sem"], second["dps_sem"])
    seeds = (first.get("simc_seed"), second.get("simc_seed"))
    independent = all(s is not None for s in seeds) and seeds[0] != seeds[1]
    separated = abs(delta) > half
    return {
        "first_minus_second_dps": delta,
        "approx_independent_95pct_ci": [delta - half, delta + half],
        "approx_independent_95pct_halfwidth": half,
        "distinct_native_seeds_observed": independent,
        "approx_95pct_statistically_separated": separated,
        "pairwise_winner_supported": independent and separated,
        "winner_if_supported": ("first" if delta > 0 else "second")
                               if independent and separated else None,
        "global_optimum_proven": False,
        "near_best_materially_different_alternative_proven": False,
        "observed_rating_transfer": sum(abs(first["target"][k] -
                        second["target"][k]) for k in scenario.STATS) // 2,
    }

def run(witness_root, prior_official, prior_scout, out, binary=None,
        cache_only=False, cancel_file=None):
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    summary = {"schema": SCHEMA, "status": "BLOCKED", "native_cap": CAP,
               "confirm_iterations": ITERATIONS,
               "new_native_calls_this_invocation": 0,
               "new_native_attempts_started_this_invocation": 0,
               "historical_native_results_reused": 0,
               "official_formula": "T=G+J+F", "global_optimum_proven": False,
               "original_v015_v016_sources_modified": False}
    report = out / "V072_RECEIPT.json"
    try:
        prepared = official.prepare(witness_root, probe.BIN_SHA)
        a, b, vectors, normalized, static, requests = choose_requests(
            prepared, prior_official, prior_scout, out)
        summary.update({"status": "PASS_HIGH_ITERATION_PAIR_PLAN_ZERO_NATIVE",
                        "historical_native_results_reused": 4,
                        "historical_breakdown": {"v069_numeric_witnesses": 2,
                         "v070_official_seed": 1, "v071_adaptive_scout": 1},
                        "old_scout_results": [{"target": x["target"],
                         "dps_mean": x["dps_mean"], "dps_sem": x["dps_sem"],
                         "dps_samples": x["dps_samples"],
                         "native_json_sha256": x["native_json_sha256"]}
                         for x in (a, b)],
                        "T": static["budget"]["T_official"], "G": 2847,
                        "J": 138, "F": 165,
                        "special_L": static["locked_L_when_all_specials_observed"],
                        "offset": prepared["calibration"]["net_input_to_json2_rating_offset"],
                        "scoped_scenario_digest": normalized["scenario_digest"],
                        "stable_profile_sha256": prepared["calibration"]["stable_profile_sha256"],
                        "confirmed_pair_targets": [x["target"] for x in requests],
                        "exact_selected_items_unchanged": True})
        if binary is not None:
            binary = pathlib.Path(binary).resolve()
            need(binary.is_file() and sha(binary.read_bytes()) == probe.BIN_SHA,
                 "PINNED_SIMC_BINARY_CHANGED")
            identity = {"schema": SCHEMA,
              "scenario_digest": normalized["scenario_digest"],
              "profile_sha256": prepared["calibration"]["stable_profile_sha256"],
              "revision": prepared["calibration"]["native_revision"],
              "binary_sha256": probe.BIN_SHA,
              "case_keys": [r["case_key"] for r in requests],
              "prior_native_sha256s": [a["native_json_sha256"], b["native_json_sha256"]],
              "iterations": ITERATIONS, "native_cap": CAP}
            seal = out / "V072_IDENTITY.json"
            if seal.exists():
                need(read_json(seal) == identity, "RESUME_IDENTITY_CONFLICT")
            else:
                engine.write_atomic(seal, identity)
            progress_file = out / "V065_PROGRESS.json"
            progress = {"schema": SCHEMA, "scenario_digest": normalized["scenario_digest"],
                        "case_keys": identity["case_keys"],
                        "profile_sha256": identity["profile_sha256"],
                        "native_cap": CAP, "native_attempts": 0, "status": "READY"}
            if progress_file.exists():
                saved = read_json(progress_file)
                need(all(saved.get(k) == progress[k] for k in
                         ("schema", "scenario_digest", "case_keys",
                          "profile_sha256", "native_cap")) and
                     type(saved.get("native_attempts")) is int and
                     0 <= saved["native_attempts"] <= CAP,
                     "RESUME_PROGRESS_IDENTITY_OR_CAP_CONFLICT")
                progress["native_attempts"] = saved["native_attempts"]
            else:
                need(not any((out / ("confirm_%02d" % i) / "result.json").exists()
                             for i in range(CAP)), "RESULT_WITHOUT_DURABLE_PROGRESS")
                engine.write_atomic(progress_file, progress)
            findings = []
            for i, request in enumerate(requests):
                folder = out / ("confirm_%02d" % i)
                if cancel_file is not None:
                    need(not pathlib.Path(cancel_file).exists(), "USER_CANCELLED")
                existing = (folder / "result.json").exists() or (folder / "native_receipt.json").exists()
                if not existing:
                    need(not cache_only, "CACHE_ONLY_WITHOUT_HIGH_NATIVE")
                    need(progress["native_attempts"] < CAP,
                         "TWO_NATIVE_ATTEMPTS_ALREADY_EXHAUSTED")
                    summary["new_native_attempts_started_this_invocation"] += 1
                obs = engine.execute_one(request, prepared["calibration"], binary,
                      folder, progress, cancel_file=cancel_file,
                      cache_only=cache_only)
                summary["new_native_calls_this_invocation"] += int(
                    obs.get("source") == "NEW_NATIVE")
                need(obs["iterations"] == ITERATIONS and obs["dps_samples"] >= 300 and
                     obs["rating_actual"] == request["target"],
                     "FRESH_320_SAMPLES_OR_FINAL_RATING_INVALID")
                findings.append(obs)
                summary["completed_confirmations"] = len(findings)
                summary["status"] = "PARTIAL_HIGH_NATIVE_CONFIRMED"
                engine.write_atomic(report, summary)
            result = scheduler.fresh_confirmation_judgment(vectors, {
                        scheduler.key(obs["target"]): obs for obs in findings})
            stats = comparison(findings[0], findings[1])
            need(result["pairwise_direction_supported"] ==
                 stats["pairwise_winner_supported"], "EXISTING_SCHEDULER_DISAGREEMENT")
            summary.update({"status": "PASS_TWO_ROGUE_FRESH_320_NATIVE_CONFIRMATIONS",
              "fresh": [{"source": r["source"], "target": r["target"],
                 "rating_actual": r["rating_actual"],
                 "dps_mean": r["dps_mean"], "dps_sem": r["dps_sem"],
                 "dps_samples": r["dps_samples"], "seed": r.get("simc_seed"),
                 "input_sha256": r["input_sha256"],
                 "native_json_sha256": r["native_json_sha256"],
                 "native_receipt_sha256": sha((out / ("confirm_%02d" % i) /
                     "native_receipt.json").read_bytes())}
                     for i, r in enumerate(findings)],
              "v015_fresh_judgment": result, "comparison": stats,
              "native_attempts_total_durable": progress["native_attempts"],
              "cache_replay_all_verified": all(
                   r["source"] == "CACHED_VERIFIED_NATIVE" for r in findings)})
    except Exception as exc:
        summary["status"] = "BLOCKED_OR_PARTIAL"
        summary["error"] = type(exc).__name__ + ":" + str(exc)
        progress_file = out / "V065_PROGRESS.json"
        if progress_file.exists():
            try:
                summary["native_attempts_total_durable"] = read_json(
                    progress_file).get("native_attempts")
            except (ValueError, OSError):
                summary["durable_progress_unreadable"] = True
    engine.write_atomic(report, summary)
    print("V072", summary["status"], "new_native",
          summary["new_native_calls_this_invocation"], flush=True)
    return 0 if summary["status"].startswith("PASS") else 3

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--witness-root", required=True, type=pathlib.Path)
    ap.add_argument("--prior-official", required=True, type=pathlib.Path)
    ap.add_argument("--prior-scout", required=True, type=pathlib.Path)
    ap.add_argument("--out", required=True, type=pathlib.Path)
    ap.add_argument("--binary", type=pathlib.Path)
    ap.add_argument("--cache-only", action="store_true")
    ap.add_argument("--cancel-file", type=pathlib.Path)
    args = ap.parse_args(argv)
    return run(args.witness_root, args.prior_official, args.prior_scout,
               args.out, args.binary, args.cache_only, args.cancel_file)

if __name__ == "__main__":
    sys.exit(main())
