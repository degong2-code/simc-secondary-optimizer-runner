#!/usr/bin/env python3
"""ONE bounded real-SimC benchmark: same initial global sample & iteration cost.

Opt-in by P2_REAL_EQUAL_BUDGET_ONCE=1, exact previous binary/profile artifacts
and SHA; no item/source refresh. v290 arm is a *normalized-scout proposal
variant*, NOT the untouched v290 schedule. Do not claim optimizer dominance.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import pathlib
import statistics
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "runner"), str(ROOT / "integration_probes")]
import p2_nested_real_simc_timing_once as prior
import v290_multiscale_adaptive_policy as v290
import v302_weak_multiregion_zoom as v302
import v303_adaptive_region_resource_policy as v303
import v304_v303_durable_adapter as v304

SCHEMA = "p2_real_equal_native_budget_v304_pilot_v1"
GLOBAL = 32
POST = 32
CONFIRM = 4
SCOUT_ITERS = 35
CONFIRM_ITERS = 320
RECHECK_ITERS = 1000
MAX_NEW_NATIVE = 150
MAX_WORK_SECONDS = 240.0
B, LOWER, UPPER = prior.B, prior.LOW, prior.UP
ARMS = ("fixed_local6", "adaptive_v304", "v290_proposal_normalized")
ROOT_OUT = pathlib.Path("out/p2_real_equal_v304_once").resolve()
BINARY = pathlib.Path("out/binary/simc").resolve()
HISTORY = pathlib.Path("out/previous_100/receipt.json").resolve()
KNOWN_SOURCE_COMMIT = "c20e2ad52e4c33711f74272309a5748125175fe8"


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def equal_resource_contract():
    return {
        "global_scouts": GLOBAL, "post_scouts_per_arm": POST,
        "confirmations_per_arm": CONFIRM, "rechecks_per_arm": 1,
        "scout_iterations": SCOUT_ITERS,
        "confirmation_iterations": CONFIRM_ITERS,
        "independent_recheck_iterations": RECHECK_ITERS,
        "requested_iterations_per_arm":
            (GLOBAL + POST) * SCOUT_ITERS + CONFIRM * CONFIRM_ITERS
            + RECHECK_ITERS,
        "logical_requests_per_arm": GLOBAL + POST + CONFIRM + 1,
        "shared_global_observations": True,
        "all_arms_identical_benchmark_binary_profile_combat": True,
        "candidate_policy_v290_caveat":
            "v290 proposal selector with forced 35-iteration scouts; "
            "NOT unmodified default v290 precision cadence",
        "global_optimum_proven": False,
        "familywise_95_confirmed": False,
    }


def row_to_native(row):
    target = tuple(row["vector"])
    iterations = row["iterations"]
    mean, sem = row["dps_mean"], row["dps_sem"]
    need(type(iterations) is int and iterations in
         (SCOUT_ITERS, CONFIRM_ITERS, RECHECK_ITERS)
         and v290.legacy.eligible(target, B, LOWER, UPPER)
         and type(mean) in (int, float) and math.isfinite(mean) and mean > 0
         and type(sem) in (int, float) and math.isfinite(sem) and sem > 0,
         "BENCHMARK_NATIVE_OBSERVATION_INVALID")
    return {
        "vector": list(target), "iterations": iterations,
        "dps_mean": float(mean), "dps_sem": float(sem),
        "samples": int(row.get("samples", iterations)),
        "simc_seed": row.get("simc_seed"),
        "json2_sha256": row.get("json2_sha256"),
    }


def historical_cache(path, stable_profile_sha):
    """Reuse exact SHA/scenario-matched older *compact* real observations.

    Not a v291 authenticated Native JSON2 cache: raw JSON2 is unavailable.
    """
    doc = json.loads(path.read_text(encoding="utf8"))
    need(doc.get("schema") == "p2_nested_real_simc_11_21_comparison_v1"
         and doc.get("status") == "PASS_REAL_NATIVE_EXPLORATORY_NO_GLOBAL_PROOF"
         and doc.get("binary_sha256") == prior.BINARY_SHA
         and doc.get("source_archive_sha256") == prior.INNER_SHA
         and doc.get("source_commit") == KNOWN_SOURCE_COMMIT
         and doc.get("stable_input_profile_sha256") == stable_profile_sha,
         "HISTORICAL_REAL_COMPACT_SOURCE_IDENTITY_MISMATCH")
    cache = {}
    for rows in doc["observations"].values():
        for row in rows:
            if row.get("iterations") not in (SCOUT_ITERS, CONFIRM_ITERS):
                continue
            parsed = row_to_native(row)
            key = (tuple(parsed["vector"]), parsed["iterations"])
            if key in cache:
                old = cache[key]
                need(old["dps_mean"] == parsed["dps_mean"] and
                     old["dps_sem"] == parsed["dps_sem"] and
                     old["json2_sha256"] == parsed["json2_sha256"],
                     "HISTORICAL_DUPLICATE_NATIVE_OBSERVATION_DRIFT")
            cache[key] = parsed
    need(cache and len(cache) <= 156, "HISTORICAL_COMPACT_MISSING")
    return cache


def fixed_local_candidates(global_rows, *, count):
    initial = v303.initialize_regions(global_rows, total=B)
    centers = initial["regions"]
    need(len(centers) > 0, "FIXED_NO_GLOBAL_SHORTLIST")
    excluded = {tuple(row["vector"]) for row in global_rows}
    output = []
    center_count = len(centers)
    # A stable region6 scout ranking: space-filling within every shortlisted
    # mode. Constant radius (6.5% of B), not adaptive, to isolate effect.
    plans = v302.region_candidates(
        B, LOWER, UPPER, [tuple(c["center"]) for c in centers],
        per_region=max(1, math.ceil(count / center_count)),
        radius_fraction=.065, exclude=excluded)
    for item in plans:
        vec = tuple(item["target"])
        if vec not in excluded:
            output.append(vec)
            excluded.add(vec)
        if len(output) == count:
            break
    # If fewer than 8 modes passed 3%+SEM, fill remaining requests by the
    # v302 global farthest policy, do not silently shorten the iteration budget.
    while len(output) < count:
        vec = v290._unobserved_global_maximin(B, LOWER, UPPER, 64, excluded)
        need(vec is not None and vec not in excluded,
             "FIXED_LOCAL6_NO_UNIQUE_FALLBACK")
        output.append(vec)
        excluded.add(vec)
    return tuple(output)


def normalized_v290_candidate(rows):
    """Reuse the genuine v290 planning function, normalize evaluation cost."""
    state = [
        {"target": v290.legacy.to_target(tuple(r["vector"])),
         "iterations": r["iterations"], "dps_mean": r["dps_mean"],
         "dps_sem": r["dps_sem"]}
        for r in rows
    ]
    proposal = v290.next_plan(
        state, total=B, lower=LOWER, upper=UPPER,
        native_calls_used=len(rows), max_native_calls=GLOBAL + POST + CONFIRM,
        scout_iterations=SCOUT_ITERS,
        confirmation_iterations=CONFIRM_ITERS,
        max_iterations=CONFIRM_ITERS)
    seen = {tuple(r["vector"]) for r in rows}
    nxt = proposal.get("next_request")
    if nxt:
        vec = tuple(v290.legacy.key(nxt["target"]))
        if vec not in seen:
            return vec, proposal["decision"], nxt["phase"] != "scout"
    # v290 may propose a 320-iteration recheck: this fixed-scout cohort
    # instead uses v290's own global maximin as the next 35-iteration vector.
    fallback = v290._unobserved_global_maximin(
        B, LOWER, UPPER, 64, seen)
    need(fallback is not None and fallback not in seen,
         "V290_NORMALIZED_NO_NEW_SCOUT_VECTOR")
    return fallback, "V290_GLOBAL_FALLBACK_FROM_PRECISION", True


def to_v304_row(row, plan):
    return {
        "target": v290.legacy.to_target(tuple(row["vector"])),
        "iterations": row["iterations"], "dps_mean": row["dps_mean"],
        "dps_sem": row["dps_sem"], "phase": plan["phase"],
        "adaptive_stage": plan["adaptive_stage"],
        "region_id": plan["region_id"],
        "region_center": plan["region_center"],
        "region_radius_fraction": plan["region_radius_fraction"],
    }


def material_top(rows, count):
    by_vec = {tuple(row["vector"]): row for row in rows
              if row["iterations"] == SCOUT_ITERS}
    return sorted(by_vec, key=lambda v: (
        -v303.score(by_vec[v]), v))[:count]


def mean_sem_pair(a, b):
    difference = a["dps_mean"] - b["dps_mean"]
    half = v290.Z95 * math.hypot(a["dps_sem"], b["dps_sem"])
    return {"mean_difference": difference, "nominal_95_halfwidth": half,
            "nominal_pair_direction": abs(difference) > half,
            "familywise_95_proven": False,
            "global_optimum_proven": False,
            "post_selection_bias_not_corrected": True}


def main():
    need(os.getenv("P2_REAL_EQUAL_BUDGET_ONCE") == "1",
         "REQUIRES_EXPLICIT_ONE_SHOT_REAL_NATIVE_OPT_IN")
    need(BINARY.is_file() and sha(BINARY.read_bytes()) == prior.BINARY_SHA,
         "EXACT_HISTORICAL_BINARY_SHA_MISSING")
    need(HISTORY.is_file(), "HISTORICAL_100_NATIVE_RECEIPT_MISSING")
    template, stable = prior.read_archived_profile()
    cached = historical_cache(HISTORY, stable)
    ROOT_OUT.mkdir(parents=True, exist_ok=True)
    receipt_path = ROOT_OUT / "receipt.json"
    receipt = {
        "schema": SCHEMA, "status": "STARTED",
        "binary_sha256": prior.BINARY_SHA,
        "source_archive_sha256": prior.INNER_SHA,
        "source_commit": KNOWN_SOURCE_COMMIT,
        "stable_profile_sha256": stable,
        "historical_compact_sha256": sha(HISTORY.read_bytes()),
        "historical_100_unique_existing": len(cached),
        "history_498_full_raw_available": False,
        "historical_100_compact_not_v291_verified_cache": True,
        "budget": equal_resource_contract(),
        "source_special_gem_historical_not_current_default": True,
        "arms": {a: [] for a in ARMS},
        "initial_global": [],
        "new_native": 0, "historical_exact_observation_reuses": 0,
        "same_run_cache_reuses": 0,
        "global_optimum_proven": False,
    }
    def write():
        tmp = receipt_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(receipt, sort_keys=True,
                                  indent=2, ensure_ascii=False) + "\n")
        tmp.replace(receipt_path)

    write()
    cache = dict(cached)
    used_in_this_run = set()
    started = time.perf_counter()
    def evaluate(vec, iterations):
        vec = tuple(vec)
        need(v290.legacy.eligible(vec, B, LOWER, UPPER),
             "BENCHMARK_VECTORS_OUT_OF_BOUNDS")
        need(time.perf_counter() - started < MAX_WORK_SECONDS,
             "BENCHMARK_REAL_WALL_TIME_CAP")
        key = vec, iterations
        if key in cache:
            row = dict(cache[key])
            if key in used_in_this_run:
                receipt["same_run_cache_reuses"] += 1
                row["source"] = "SAME_RUN_OBSERVATION_REUSE"
            else:
                receipt["historical_exact_observation_reuses"] += 1
                row["source"] = "VERIFIED_HISTORICAL_COMPACT_OBSERVATION"
            used_in_this_run.add(key)
            return row
        need(receipt["new_native"] < MAX_NEW_NATIVE,
             "EXPLICIT_REAL_NATIVE_CAP_EXCEEDED")
        index = receipt["new_native"]
        folder = ROOT_OUT / "cases" / ("case_%03d" % index)
        folder.mkdir(parents=True, exist_ok=False)
        output = folder / "native.json"
        text = prior.encode_candidate(template, stable, vec,
                                      iterations, output)
        inputfile = folder / "input.simc"
        inputfile.write_text(text, encoding="utf8")
        begin = time.perf_counter()
        try:
            result = subprocess.run(
                [str(BINARY), str(inputfile)], cwd=BINARY.parent,
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, timeout=60)
        finally:
            # Even a failed or timed-out process consumes the Native cap.
            receipt["new_native"] += 1
            write()
        wall = time.perf_counter() - begin
        if result.returncode != 0:
            receipt["status"] = "BLOCKED_SIMC_EXIT_" + str(result.returncode)
            receipt["simc_error_tail"] = result.stderr.decode(
                "utf8", errors="replace")[-2400:]
            write()
            raise RuntimeError(receipt["status"])
        need(output.is_file(), "SIMC_NO_NATIVE_JSON2")
        parsed = prior.extract_simc(output, vec, iterations)
        row = row_to_native({
            **parsed, "vector": list(vec), "iterations": iterations,
        })
        row.update(
            source="NEW_NATIVE", wall_seconds=round(wall, 6),
            input_sha256=sha(inputfile.read_bytes()),
        )
        cache[key] = dict(row)
        used_in_this_run.add(key)
        # Each run is SHA-proven by its input and full native JSON2; only the
        # compact measured facts are retained as a 7-day Actions artifact.
        output.unlink()
        inputfile.unlink()
        write()
        return row

    global_order = v304._global_order(
        B, tuple(LOWER), tuple(UPPER), GLOBAL)
    try:
        for index, vec in enumerate(global_order):
            need(index == len(receipt["initial_global"]),
                 "GLOBAL_SAMPLE_INDEX_DRIFT")
            row = evaluate(vec, SCOUT_ITERS)
            receipt["initial_global"].append(row)
            write()
        common = receipt["initial_global"]
        fixed_pool = fixed_local_candidates(common, count=POST)
        v304_history = []
        for i, row in enumerate(common):
            proposal = v304.next_plan(
                v304_history, total=B, lower=LOWER, upper=UPPER,
                max_native_calls=GLOBAL + POST + CONFIRM,
                scout_iterations=SCOUT_ITERS,
                confirmation_iterations=CONFIRM_ITERS,
                initial_global_calls=GLOBAL,
                confirmation_calls=CONFIRM)
            req = proposal["next_request"]
            need(req["adaptive_stage"] == "global_initial"
                 and tuple(v290.legacy.key(req["target"])) ==
                 tuple(row["vector"]), "V304_COMMON_GLOBAL_SEED_ORDER_DRIFT")
            v304_history.append(to_v304_row(row, req))
        for round_id in range(POST):
            for arm in ARMS:
                if arm == "fixed_local6":
                    vector = fixed_pool[round_id]
                    decision = "FIXED_V302_LOCAL6_SPATIAL_POOL"
                    meta = None
                elif arm == "adaptive_v304":
                    proposal = v304.next_plan(
                        v304_history, total=B, lower=LOWER, upper=UPPER,
                        max_native_calls=GLOBAL + POST + CONFIRM,
                        scout_iterations=SCOUT_ITERS,
                        confirmation_iterations=CONFIRM_ITERS,
                        initial_global_calls=GLOBAL,
                        confirmation_calls=CONFIRM)
                    req = proposal["next_request"]
                    need(req is not None and req["phase"] == "scout",
                         "V304_POST_SCOUT_PLAN_MISSING")
                    vector = tuple(v290.legacy.key(req["target"]))
                    decision, meta = proposal["decision"], req
                else:
                    vector, decision, forced = normalized_v290_candidate(
                        common + receipt["arms"][arm])
                    meta = {"forced_scout_from_precision": forced}
                seen_this_arm = {tuple(r["vector"]) for r in
                                 common + receipt["arms"][arm]}
                need(vector not in seen_this_arm, "DUPLICATE_ARM_SCOUT_TARGET")
                row = dict(evaluate(vector, SCOUT_ITERS),
                           policy_decision=decision,
                           policy_round=round_id + 1)
                if arm == "adaptive_v304":
                    v304_history.append(to_v304_row(row, meta))
                    row["adaptive_stage"] = meta["adaptive_stage"]
                    row["region_id"] = meta["region_id"]
                    row["region_center"] = meta["region_center"]
                    row["region_radius_fraction"] = meta[
                        "region_radius_fraction"]
                elif arm == "v290_proposal_normalized":
                    row.update(meta)
                receipt["arms"][arm].append(row)
                write()
            if (round_id + 1) % 8 == 0:
                print("P2_EQUAL_REAL_PROGRESS", json.dumps({
                    "post_scout_round": round_id + 1,
                    "new_native": receipt["new_native"],
                    "historical_reuses": receipt[
                        "historical_exact_observation_reuses"],
                    "elapsed_seconds": round(
                        time.perf_counter() - started, 2),
                }), flush=True)

        # Fixed 4 candidate confirmations are interleaved to limit drift.
        top = {arm: material_top(
            common + receipt["arms"][arm], CONFIRM)
            for arm in ARMS}
        for j in range(CONFIRM):
            for arm in ARMS:
                vec = top[arm][j]
                row = dict(evaluate(vec, CONFIRM_ITERS),
                           confirmation_rank_at_scout=j+1)
                receipt["arms"][arm].append(row)
                if arm == "adaptive_v304":
                    proposal = v304.next_plan(
                        v304_history, total=B, lower=LOWER, upper=UPPER,
                        max_native_calls=GLOBAL + POST + CONFIRM,
                        scout_iterations=SCOUT_ITERS,
                        confirmation_iterations=CONFIRM_ITERS,
                        initial_global_calls=GLOBAL,
                        confirmation_calls=CONFIRM)
                    req = proposal["next_request"]
                    need(req is not None and
                         req["adaptive_stage"] == "confirmation",
                         "V304_CONFIRMATION_PHASE_DRIFT")
                    need(tuple(v290.legacy.key(req["target"])) ==
                         vec, "V304_CONFIRMATION_ORDER_NOT_SAME_TOP4")
                    v304_history.append(to_v304_row(row, req))
                write()

        winners = {}
        for arm in ARMS:
            confirms = [r for r in receipt["arms"][arm]
                        if r["iterations"] == CONFIRM_ITERS]
            need(len(confirms) == CONFIRM, "FIXED_CONFIRM_COUNT_DRIFT")
            winner = max(confirms, key=lambda r: (
                r["dps_mean"], -r["dps_sem"]))
            winners[arm] = tuple(winner["vector"])
        for arm in ARMS:
            receipt["arms"][arm].append(dict(
                evaluate(winners[arm], RECHECK_ITERS),
                selected_recheck=True))
            write()

        summaries = {}
        for arm in ARMS:
            rows = common + receipt["arms"][arm]
            iterations = sum(r["iterations"] for r in rows)
            need(iterations == equal_resource_contract()[
                "requested_iterations_per_arm"], "EQUAL_ITERATIONS_DRIFT")
            recheck = [r for r in rows if r["iterations"] == RECHECK_ITERS]
            need(len(recheck) == 1, "INDEPENDENT_RECHECK_COUNT_DRIFT")
            summaries[arm] = {
                "logical_requests": len(rows),
                "requested_iterations": iterations,
                "observed_best_1000": recheck[0],
                "best_320": max((r for r in rows
                                 if r["iterations"] == CONFIRM_ITERS),
                                key=lambda r: r["dps_mean"]),
                "full_method_includes_reused_global_start": True,
                "arm_new_native_count": sum(
                    r["source"] == "NEW_NATIVE"
                    for r in receipt["arms"][arm]),
                "method_wall_time_not_directly_isolated":
                    "Interleaved arms and cached initial global",
            }
        comparisons = {}
        for i, arm in enumerate(ARMS):
            for other in ARMS[i+1:]:
                comparisons[arm + "__vs__" + other] = mean_sem_pair(
                    summaries[arm]["observed_best_1000"],
                    summaries[other]["observed_best_1000"])
        receipt["summaries"] = summaries
        receipt["nominal_pairwise_1000"] = comparisons
        receipt["elapsed_seconds_total"] = round(
            time.perf_counter() - started, 3)
        receipt["status"] = "PASS_REAL_SIMC_EXPLORATORY_NO_GLOBAL_PROOF"
        write()
        print("P2_EQUAL_REAL_FINAL", json.dumps({
            "status": receipt["status"],
            "new_native": receipt["new_native"],
            "historical_reuses": receipt[
                "historical_exact_observation_reuses"],
            "same_run_reuses": receipt["same_run_cache_reuses"],
            "elapsed_seconds": receipt["elapsed_seconds_total"],
            "summaries": {
                arm: {
                    "vector": r["observed_best_1000"]["vector"],
                    "dps": r["observed_best_1000"]["dps_mean"],
                    "sem": r["observed_best_1000"]["dps_sem"],
                    "requested_iterations": r["requested_iterations"],
                }
                for arm, r in summaries.items()},
            "comparisons": comparisons,
        }, sort_keys=True), flush=True)
    except BaseException as exc:
        receipt["status"] = "BLOCKED_OR_PARTIAL_" + type(exc).__name__
        receipt["first_error"] = str(exc)[:350]
        receipt["elapsed_seconds_total"] = round(
            time.perf_counter() - started, 3)
        write()
        print("P2_EQUAL_REAL_BLOCKED", receipt["first_error"], flush=True)
        raise


if __name__ == "__main__":
    main()
