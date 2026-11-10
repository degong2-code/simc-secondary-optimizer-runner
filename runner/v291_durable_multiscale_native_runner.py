#!/usr/bin/env python3
"""v291: durable multi-case runner of the opt-in v290 search policy.

Reuse v093 request generation, v065 exact-case SimC execution/cache and v091
oil-inclusive Native JSON2 acceptance. This module neither implements SimC
effects nor changes the established v094 six-case execution mode.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import pathlib
import sys
import time

import v046_static_item_cache as cache
import v061_scenario_contract as scenario
import v065_original_scheduler_native_bridge as engine
import v065_v015_scheduler_adapter as constraints
import v091_weapon_oil_external_adapter as oil
import v093_inclusive_adaptive_scheduler_bridge as adaptive
import v094_durable_inclusive_adaptive_runner as bounded
import v290_multiscale_adaptive_policy as search
import v298_adaptive_percent_grid as percent_grid
import v299_multiregion_percent_policy as multiregion_grid
import v300_multiregion_throughput_resolution as measured_resolution
import v301_nested_multiregion_policy as nested_regions
import v302_weak_multiregion_zoom as region_geometry
import v303_adaptive_region_resource_policy as region_resources
import v304_v303_durable_adapter as durable_regions
import v305_grid_pairwise_adaptive_hybrid as hybrid_regions
import v306_seed_retained_coarse_escape_regions as seed_escape_regions
import v307_dense_nested_coverage_grid as dense_grid

SCHEMA = "v291_durable_multiscale_native_runner_v1"


class LongRunBlocked(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise LongRunBlocked(reason)


def digest(obj):
    return cache.digest(obj)


def read_json(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf8"))


def atomic(path, data):
    engine.write_atomic(path, data)


def case_folder(output, number):
    need(type(number) is int and 0 <= number < 100000,
         "CASE_INDEX_BOUND")
    return output / "cases" / ("case_%05d" % number) / "native"


def _mode(phase, iterations, identity):
    need(phase in ("scout", "precision"), "UNKNOWN_PLANNED_PHASE")
    selected = (identity["scout_iterations"] if phase == "scout"
                else identity["confirm_iterations"])
    need(iterations == selected, "UNTYPED_SIMC_ITERATION_IDENTITY")
    return "scout" if phase == "scout" else "confirm"


def _request(context, flask, output, plan):
    need(type(plan) is dict and set(plan) >=
         {"phase", "target", "iterations", "index"},
         "PENDING_PLAN_FIELDS")
    folder = case_folder(output, plan["index"])
    phase = _mode(plan["phase"], plan["iterations"], context["identity"])
    request = adaptive.request(
        context, plan["target"], flask, folder / "result.json", phase=phase)
    need(request["iterations"] == plan["iterations"] and
         request["v092_base_target"] == plan["target"] and
         request["v092_fixed_O"] == context["identity"]["oil_vector"],
         "SOURCE_LOCKED_REQUEST_DRIFT")
    return request, folder


def _verified_row(req, binary, folder, calibration, *, allow_cache):
    # No second Native. Original v065 checks input bytes, JSON2 and receipt
    # against exact v064 case-key and real SimC revision/stat validation.
    receipt = engine.execute_one(
        req, calibration, binary, folder, {"native_attempts": 0},
        cache_only=allow_cache)
    native_bytes = (folder / "result.json").read_bytes()
    native_doc = json.loads(native_bytes)
    actual = oil.ingest_native(req, native_doc, native_bytes)
    actual["simc_seed"] = _source_seed(native_doc, receipt)
    need(actual["native_json_sha256"] == receipt["native_json_sha256"]
         and actual["case_key"] == receipt["case_key"],
         "EXISTING_NATIVE_AND_OIL_VALIDATOR_DISAGREE")
    return actual, receipt["source"]


def _source_seed(native_json, accepted_receipt):
    """Read actual SimC JSON2 seed, never manufacture a seed from the target."""
    options = (native_json.get("sim") or {}).get("options") or {}
    observed = options.get("seed")
    recorded = accepted_receipt.get("simc_seed")
    if recorded is not None:
        need(type(observed) is int and recorded == observed,
             "SIMC_SEED_NATIVE_JSON_RECEIPT_DRIFT")
    return observed if type(observed) is int else None


V304_METADATA = ("adaptive_stage", "region_id",
                 "region_center", "region_radius_fraction")


def _compact(req, native, source, plan):
    row = {
        "index": plan["index"], "phase": plan["phase"],
        "target": dict(plan["target"]), "iterations": plan["iterations"],
        "v092_base_target": dict(req["v092_base_target"]),
        "final_T": dict(req["target"]), "case_key": req["case_key"],
        "input_sha256": req["input_sha256"],
        "native_sha256": native["native_json_sha256"],
        "dps_mean": native["dps_mean"], "dps_sem": native["dps_sem"],
        "samples": native["dps_samples"], "source": source,
        "simc_seed": native.get("simc_seed"),
    }
    if "adaptive_stage" in plan:
        need(all(key in plan for key in V304_METADATA),
             "V304_PENDING_REGION_METADATA_MISSING")
        row.update({key: plan[key] for key in V304_METADATA})
        if "hybrid_method" in plan:
            row["hybrid_method"] = plan["hybrid_method"]
    if "grid_stage" in plan:
        need(all(k in plan for k in dense_grid.METADATA),
             "V307_PENDING_GRID_METADATA_MISSING")
        row.update({k: plan[k] for k in dense_grid.METADATA})
    return row


def _load_journal(path):
    if not path.exists():
        return []
    need(path.stat().st_size <= 20_000_000,
         "JOURNAL_SIZE_LIMIT")
    result = []
    with path.open("rb") as reader:
        for line in reader:
            need(line.endswith(b"\n") and len(line) < 12_000,
                 "TORN_OR_OVERSIZED_JOURNAL_LINE")
            doc = json.loads(line)
            need(type(doc) is dict and doc.get("index") == len(result),
                 "JOURNAL_INDEX_CONTIGUITY_DRIFT")
            result.append(doc)
    return result


def _append_journal(path, row):
    with path.open("ab") as writer:
        writer.write((json.dumps(row, sort_keys=True, separators=(",", ":"),
                                 allow_nan=False) + "\n").encode("utf8"))
        writer.flush()
        os.fsync(writer.fileno())


def _count_attempts(output):
    parent = output / "cases"
    attempts = 0
    if not parent.exists():
        return attempts
    for folder in parent.iterdir():
        need(folder.is_dir() and not folder.is_symlink() and
             folder.name.startswith("case_") and
             len(folder.name) == 10 and folder.name[5:].isdigit(),
             "FOREIGN_CASE_FOLDER")
        marker = folder / "V065_PROGRESS.json"
        if marker.exists():
            rec = read_json(marker)
            need(type(rec.get("native_attempts")) is int and
                 0 <= rec["native_attempts"] <= 1,
                 "ONE_NATIVE_ATTEMPT_PER_CASE_REQUIRED")
            attempts += rec["native_attempts"]
    return attempts


def _summary(observations, context):
    B = context["identity"]["base_B"]
    O = context["identity"]["oil_vector"]
    if not observations:
        return None
    # Reuse v094 real-DPS near-alternative reporting, never predicted DPS.
    records = [
        {"v092_base_target": row["v092_base_target"],
         "target": row["final_T"], "iterations": row["iterations"],
         "case_key": row["case_key"], "dps_mean": row["dps_mean"],
         "dps_sem": row["dps_sem"]}
        for row in observations
    ]
    return bounded._candidate_summary(records, B, O)


def confirmed_selected_pair_95(observations, confirm_iterations):
    """Normal-approx 95% for two SELECTED confirmed Native candidates only."""
    by_vector = {}
    for row in observations:
        if row["phase"] == "precision" and row["iterations"] == confirm_iterations:
            vector = constraints.key(row["target"])
            need(vector not in by_vector, "DUPLICATE_CONFIRMED_VECTOR_IDENTITY")
            by_vector[vector] = row
    if len(by_vector) < 2:
        return None
    ranked = sorted(by_vector.values(),
                    key=lambda row: (-row["dps_mean"], row["case_key"]))
    best, runner_up = ranked[:2]
    half = search.Z95 * math.hypot(best["dps_sem"], runner_up["dps_sem"])
    gap = best["dps_mean"] - runner_up["dps_mean"]
    seeds = (best.get("simc_seed"), runner_up.get("simc_seed"))
    distinct = all(seed is not None for seed in seeds) and seeds[0] != seeds[1]
    return {
        "schema": "v291_selected_confirmed_pair_approx95_v1",
        "comparison_scope": "SELECTED_CONFIRMED_PAIR_ONLY",
        "selected_from_multiple_candidates": True,
        "multiplicity_and_winner_bias_not_corrected": True,
        "first_target": dict(best["target"]),
        "second_target": dict(runner_up["target"]),
        "first_dps": best["dps_mean"], "second_dps": runner_up["dps_mean"],
        "first_sem": best["dps_sem"], "second_sem": runner_up["dps_sem"],
        "first_minus_second_dps": gap, "approx_ci95_halfwidth": half,
        "distinct_simc_seeds_observed": distinct,
        "pairwise_direction_supported": gap > half and distinct,
        "global_optimum_proven": False,
    }


def run(context, flask_vector, binary, output, *,
        max_native_calls, max_new_native_this_invocation=None,
        cache_only=False, cancel_file=None, max_elapsed_seconds=None,
        recover_verified_partial=False, open_folder=False,
        percentage_grid_points=None, multiregion_percent_grid=False,
        nested_percent_grid=False, adaptive_region_resources=False,
        hybrid_region_grid_neighbors=False,
        seed_retained_coarse_escape_regions=False,
        dense_nested_grid_max_level=None,
        adaptive_initial_global_calls=160, adaptive_confirmation_calls=8):
    """Resume an exact source-bound session, or execute one Native per plan.

    A previously committed journal is always re-validated against ORIGINAL
    exact-case Native bytes. A pending case has been sealed on disk before
    Native begins; a partial outcome cannot be silently retried.
    """
    binary = pathlib.Path(binary).resolve(strict=True)
    output = pathlib.Path(output).resolve()
    need(type(max_native_calls) is int and
         1 <= max_native_calls <= 100000,
         "EXPLICIT_TOTAL_NATIVE_BUDGET_REQUIRED")
    need(max_new_native_this_invocation is None or
         (type(max_new_native_this_invocation) is int and
          0 <= max_new_native_this_invocation <= max_native_calls),
         "PER_INVOCATION_NATIVE_CAP")
    need(max_elapsed_seconds is None or
         (type(max_elapsed_seconds) in (int, float) and
          0 < max_elapsed_seconds <= 86400),
         "ELAPSED_SECONDS_CAP")
    # New, explicitly opt-in experimental candidate strategy. Default None
    # means the original v290 session seal and journal remain byte-compatible.
    percent_enabled = percentage_grid_points is not None
    need(type(hybrid_region_grid_neighbors) is bool and
         type(adaptive_region_resources) is bool and
         not (adaptive_region_resources and hybrid_region_grid_neighbors),
         "V305_SEPARATE_EXPERIMENTAL_POLICY_OPT_INS")
    need(type(seed_retained_coarse_escape_regions) is bool and
         not (seed_retained_coarse_escape_regions and
              (adaptive_region_resources or hybrid_region_grid_neighbors)),
         "V306_EXCLUSIVE_EXPERIMENTAL_POLICY_OPT_INS")
    region_enabled = (adaptive_region_resources or hybrid_region_grid_neighbors
                      or seed_retained_coarse_escape_regions)
    grid_enabled = dense_nested_grid_max_level is not None
    need(not grid_enabled or (
         type(dense_nested_grid_max_level) is int and
         dense_nested_grid_max_level in dense_grid.LEVELS and
         not (region_enabled or percent_enabled or multiregion_percent_grid or
              nested_percent_grid) and
         adaptive_initial_global_calls == 160 and
         adaptive_confirmation_calls == 8),
         "V307_EXCLUSIVE_DENSE_GRID_OPT_IN")
    special_enabled = region_enabled or grid_enabled
    need(not (region_enabled and
              (percent_enabled or multiregion_percent_grid or nested_percent_grid)),
         "V304_EXCLUSIVE_ADAPTIVE_REGION_OPT_IN")
    need(region_enabled or
         (adaptive_initial_global_calls == 160 and
          adaptive_confirmation_calls == 8),
         "V304_OPTIONS_REQUIRE_EXPLICIT_OPT_IN")
    region_planner = (seed_escape_regions if seed_retained_coarse_escape_regions
                      else hybrid_regions if hybrid_region_grid_neighbors
                      else durable_regions)
    metadata_keys = (dense_grid.METADATA if grid_enabled else
                     V304_METADATA + (("hybrid_method",)
                                      if (hybrid_region_grid_neighbors or
                                          seed_retained_coarse_escape_regions)
                                      else ()))
    if region_enabled:
        region_opts = durable_regions.options(
            max_native_calls, adaptive_initial_global_calls,
            adaptive_confirmation_calls)
    need(type(multiregion_percent_grid) is bool and
         (not multiregion_percent_grid or percent_enabled),
         "MULTIREGION_REQUIRES_PERCENT_GRID_OPT_IN")
    need(type(nested_percent_grid) is bool and
         (not nested_percent_grid or multiregion_percent_grid),
         "NESTED_GRID_REQUIRES_MULTIREGION_OPT_IN")
    need(not nested_percent_grid or percentage_grid_points == "auto" or
         (type(percentage_grid_points) is int and
          percentage_grid_points in nested_regions.LEVELS),
         "NESTED_GRID_LEVEL_6_11_21_41_ONLY")
    need(percentage_grid_points is None or
         percentage_grid_points == "auto" or
         (type(percentage_grid_points) is int and
          3 <= percentage_grid_points <= 41),
         "PERCENT_GRID_OPT_IN_POINTS_3_TO_41_OR_AUTO")
    need(context.get("schema") == adaptive.SCHEMA and
         context.get("status") == "READY_TO_SELECT_B_SCOUT_WITH_FINAL_T_NATIVE",
         "ADMITTED_ADAPTIVE_CONTEXT_REQUIRED")
    identity = context["identity"]
    normalized = context["bundle"]["prepared"]["scenario"]
    runtime = normalized["scenario"]["runtime"]
    need(max_native_calls <= runtime["max_native_calls"],
         "TOTAL_NATIVE_BUDGET_EXCEEDS_TYPED_SCENARIO")
    need(hashlib.sha256(binary.read_bytes()).hexdigest() ==
         identity["binary_sha256"], "SIMC_BINARY_SHA_CHANGED")
    need(adaptive.identity(context["bundle"], identity["binary_sha256"],
         identity["revision"], identity["scout_iterations"],
         identity["confirm_iterations"]) == identity,
         "EXACT_ADAPTIVE_CONTEXT_IDENTITY_DRIFT")
    scenario.vector(flask_vector, "V291_FLASK_F")
    need(sum(flask_vector.values()) == normalized["budget"]["F"],
         "FLASK_F_NOT_SCENARIO")
    B, lower, upper = constraints.bounds(
        normalized, adaptive.feasible_budget(context, flask_vector))
    need(B == identity["base_B"], "APPROVED_B_CHANGED")
    # Existing runtime provides only two exact iteration identities for now.
    scout_iters = identity["scout_iterations"]
    confirm_iters = identity["confirm_iterations"]
    need(scout_iters < confirm_iters, "LONG_RUN_REQUIRES_TWO_ITERATION_LEVELS")
    policy_sha = hashlib.sha256(pathlib.Path(search.__file__).read_bytes()).hexdigest()
    seal = {
        "schema": SCHEMA, "policy_sha256": policy_sha,
        "context": identity, "flask_F": flask_vector,
        "max_native_calls": max_native_calls,
        "scout_iterations": scout_iters,
        "confirm_iterations": confirm_iters,
        "B": B, "lower": constraints.to_target(lower),
        "upper": constraints.to_target(upper),
        "statistical_confidence": 0.95,
    }
    if region_enabled:
        seal["experimental_adaptive_regions"] = {
            "schema": durable_regions.SCHEMA,
            "v302_sha256": hashlib.sha256(
                pathlib.Path(region_geometry.__file__).read_bytes()).hexdigest(),
            "v303_sha256": hashlib.sha256(
                pathlib.Path(region_resources.__file__).read_bytes()).hexdigest(),
            "v304_sha256": hashlib.sha256(
                pathlib.Path(durable_regions.__file__).read_bytes()).hexdigest(),
            **region_opts,
        }
        if hybrid_region_grid_neighbors:
            seal["experimental_adaptive_regions"]["hybrid_v305"] = {
                "schema": hybrid_regions.SCHEMA,
                "source_sha256": hashlib.sha256(
                    pathlib.Path(hybrid_regions.__file__).read_bytes()).hexdigest(),
            }
        if seed_retained_coarse_escape_regions:
            seal["experimental_adaptive_regions"]["seed_retained_v306"] = {
                "schema": seed_escape_regions.SCHEMA,
                "source_sha256": hashlib.sha256(
                    pathlib.Path(seed_escape_regions.__file__).read_bytes()).hexdigest(),
                "v305_dependency_sha256": hashlib.sha256(
                    pathlib.Path(hybrid_regions.__file__).read_bytes()).hexdigest(),
            }
    if grid_enabled:
        dense_grid.budget(max_native_calls)
        seal["experimental_dense_nested_grid"] = {
            "schema": dense_grid.SCHEMA,
            "source_sha256": hashlib.sha256(
                pathlib.Path(dense_grid.__file__).read_bytes()).hexdigest(),
            "v302_geometry_sha256": hashlib.sha256(
                pathlib.Path(region_geometry.__file__).read_bytes()).hexdigest(),
            "max_level": dense_nested_grid_max_level,
            "levels": [level for level in dense_grid.LEVELS
                       if level <= dense_nested_grid_max_level],
            "budget": dense_grid.budget(max_native_calls),
        }
    if percent_enabled:
        seal["experimental_percent_grid"] = {
            "schema": percent_grid.SCHEMA,
            "source_sha256": hashlib.sha256(
                pathlib.Path(percent_grid.__file__).read_bytes()).hexdigest(),
            "resolution": percentage_grid_points,
        }
        if multiregion_percent_grid:
            seal["experimental_multiregion"] = {
                "schema": multiregion_grid.SCHEMA,
                "source_sha256": hashlib.sha256(
                    pathlib.Path(multiregion_grid.__file__).read_bytes()).hexdigest(),
                "throughput_sha256": hashlib.sha256(
                    pathlib.Path(measured_resolution.__file__).read_bytes()
                ).hexdigest(),
            }
            if nested_percent_grid:
                seal["experimental_multiregion"]["nested_grid"] = {
                    "schema": nested_regions.SCHEMA,
                    "source_sha256": hashlib.sha256(
                        pathlib.Path(nested_regions.__file__).read_bytes()
                    ).hexdigest(),
                }
    if output.exists():
        need(not output.is_symlink(), "OUTPUT_SYMLINK_NOT_ALLOWED")
    output.mkdir(parents=True, exist_ok=True)
    seal_path = output / "V291_SESSION.json"
    if seal_path.exists():
        need(read_json(seal_path) == seal, "SEALED_SESSION_IDENTITY_DRIFT")
    else:
        need(not any(output.iterdir()), "NONEMPTY_UNSEALED_SESSION_REJECTED")
        atomic(seal_path, seal)
    (output / "cases").mkdir(exist_ok=True)
    journal_path = output / "V291_JOURNAL.jsonl"
    pending_path = output / "V291_PENDING.json"
    progress_path = output / "V291_PROGRESS.json"
    report_path = output / "V291_RESULT.json"
    calibration = {"native_revision": identity["revision"]}
    stored = _load_journal(journal_path)
    need(len(stored) <= max_native_calls, "JOURNAL_EXCEEDS_SESSION_BUDGET")
    # Validation on resume is linear in existing case count, not a repeated
    # O(N^2) scan during each newly appended case.
    observations = []
    for row in stored:
        plan = {k: row[k] for k in ("index", "phase",
                                    "target", "iterations")}
        if region_enabled:
            need(all(k in row for k in metadata_keys) and
                 (hybrid_region_grid_neighbors or
                  seed_retained_coarse_escape_regions or
                  "hybrid_method" not in row) and
                 not any(k in row for k in dense_grid.METADATA),
                 "V305_JOURNAL_REGION_METADATA_MISSING")
            plan.update({k: row[k] for k in metadata_keys})
        elif grid_enabled:
            need(all(k in row for k in metadata_keys) and
                 not any(k in row for k in (*V304_METADATA,"hybrid_method")),
                 "V307_JOURNAL_GRID_METADATA_MISSING")
            plan.update({k: row[k] for k in metadata_keys})
        else:
            need(not any(k in row for k in
                         (*V304_METADATA, "hybrid_method",
                          *dense_grid.METADATA)),
                 "V307_UNSEALED_METADATA_IN_LEGACY_JOURNAL")
        req, folder = _request(context, flask_vector, output, plan)
        actual, _ = _verified_row(req, binary, folder, calibration, allow_cache=True)
        expected = _compact(req, actual, row["source"], plan)
        # Old v291 journals omitted a real seed. When every original
        # input/JSON2/receipt SHA has been revalidated above, permit only
        # that single missing metadata field and keep the old journal bytes.
        if row.get("simc_seed") is None and expected["simc_seed"] is not None:
            former = dict(expected)
            former["simc_seed"] = None
            need(former == row, "RECORDED_NATIVE_CASE_BYTES_OR_SUMMARY_DRIFT")
            observations.append(expected)
        else:
            need(expected == row, "RECORDED_NATIVE_CASE_BYTES_OR_SUMMARY_DRIFT")
            observations.append(row)
    pending = read_json(pending_path) if pending_path.exists() else None
    if pending is not None and pending["index"] < len(stored):
        row = stored[pending["index"]]
        need(all(row[k] == pending[k] for k in
                 ("index", "target", "iterations", "phase",
                  *(metadata_keys if special_enabled else ()))),
             "ALREADY_COMMITTED_PENDING_DISAGREES")
        pending_path.unlink()
        pending = None
    need(pending is None or
         (pending["index"] == len(stored) and
          set(pending) == ({"index", "target", "iterations", "phase",
                            "decision"} |
                           (set(metadata_keys) if region_enabled else set()))),
         "PENDING_CASE_NOT_CONTIGUOUS")
    if special_enabled and pending is not None:
        # A persisted pending request is a source of truth ONLY after its
        # exact deterministic plan is reconstructed from verified journal.
        if grid_enabled:
            proposed_pending = dense_grid.next_plan(
                observations, total=B, lower=lower, upper=upper,
                max_native_calls=max_native_calls, scout_iterations=scout_iters,
                confirmation_iterations=confirm_iters,
                max_level=dense_nested_grid_max_level)
        else:
            proposed_pending = region_planner.next_plan(
                observations, total=B, lower=lower, upper=upper,
                max_native_calls=max_native_calls, scout_iterations=scout_iters,
                confirmation_iterations=confirm_iters,
                initial_global_calls=adaptive_initial_global_calls,
                confirmation_calls=adaptive_confirmation_calls)
        need(proposed_pending["next_request"] is not None,
             "V304_PENDING_PLAN_DRIFT")
        action = proposed_pending["next_request"]
        expected_pending = {
            "index": len(observations), "phase": action["phase"],
            "target": action["target"], "iterations": action["iterations"],
            "decision": proposed_pending["decision"],
            **{key: action[key] for key in metadata_keys},
        }
        need(pending == expected_pending, "V304_PENDING_PLAN_DRIFT")
    attempts = _count_attempts(output)
    need(attempts <= max_native_calls, "PREVIOUS_NATIVE_ATTEMPTS_EXCEED_BUDGET")
    need(attempts >= len(stored), "JOURNAL_WITHOUT_NATIVE_ATTEMPT")
    new_this_invocation = 0
    cached_this_invocation = len(stored)
    started = time.monotonic()
    status = "STARTED"
    # Optional throughput telemetry, not part of a native-DPS receipt or
    # the exact-cache identity. A lost/malformed hint must never block resume.
    timing_path = output / "V298_NATIVE_TIMINGS.json"
    timings = []
    if percent_enabled and timing_path.is_file():
        try:
            hints = read_json(timing_path)
            if type(hints) is list:
                for hint in hints[-11:]:
                    if (type(hint) is dict and
                            type(hint.get("index")) is int and
                            type(hint.get("seconds")) in (float, int) and
                            0 <= hint["index"] < len(observations) and
                            observations[hint["index"]]["phase"] == "scout" and
                            observations[hint["index"]]["source"] == "NEW_NATIVE" and
                            math.isfinite(hint["seconds"]) and
                            0 < hint["seconds"] <= 240):
                        timings.append(hint)
        except (OSError, ValueError, TypeError):
            pass
    try:
        while True:
            if cancel_file and pathlib.Path(cancel_file).exists():
                status = "PAUSED_USER_CANCEL"
                break
            if max_elapsed_seconds is not None and (
                    time.monotonic() - started >= max_elapsed_seconds):
                status = "PAUSED_ELAPSED_BUDGET"
                break
            if pending is None and attempts >= max_native_calls:
                status = "BUDGET_EXHAUSTED"
                break
            if pending is None:
                if grid_enabled:
                    proposed = dense_grid.next_plan(
                        observations, total=B, lower=lower, upper=upper,
                        max_native_calls=max_native_calls,
                        scout_iterations=scout_iters,
                        confirmation_iterations=confirm_iters,
                        max_level=dense_nested_grid_max_level)
                elif region_enabled:
                    proposed = region_planner.next_plan(
                        observations, total=B, lower=lower, upper=upper,
                        max_native_calls=max_native_calls,
                        scout_iterations=scout_iters,
                        confirmation_iterations=confirm_iters,
                        initial_global_calls=adaptive_initial_global_calls,
                        confirmation_calls=adaptive_confirmation_calls)
                else:
                    planner = (nested_regions.next_plan if nested_percent_grid
                               else multiregion_grid.next_plan if multiregion_percent_grid
                               else percent_grid.next_plan if percent_enabled
                               else search.next_plan)
                    point_count = percentage_grid_points
                    if percentage_grid_points == "auto":
                        remaining_seconds = (
                            max_elapsed_seconds - (time.monotonic() - started)
                            if max_elapsed_seconds is not None else None)
                        estimate_kwargs = {
                            "remaining_calls": max(0, max_native_calls-attempts),
                            "seconds_available": (max(0.001, remaining_seconds)
                                if remaining_seconds is not None else None),
                        }
                        if multiregion_percent_grid:
                            estimator = (nested_regions.choose_points_from_throughput
                                         if nested_percent_grid else
                                         measured_resolution.choose_points_from_throughput)
                            point_count = estimator(
                                [hint["seconds"] for hint in timings],
                                confirmation_to_scout_iterations=(
                                    confirm_iters/scout_iters),
                                **estimate_kwargs)
                        else:
                            # Existing v298 auto sessions retain source SHA/algorithm.
                            point_count = percent_grid.choose_points_from_throughput(
                                [hint["seconds"] for hint in timings],
                                **estimate_kwargs)
                    proposed = planner(
                        [{"target": row["target"], "iterations": row["iterations"],
                          "dps_mean": row["dps_mean"], "dps_sem": row["dps_sem"]}
                         for row in observations],
                        total=B, lower=lower, upper=upper,
                        native_calls_used=attempts,
                        max_native_calls=max_native_calls,
                        scout_iterations=scout_iters,
                        confirmation_iterations=confirm_iters,
                        max_iterations=confirm_iters,
                        **({"reference_points": point_count}
                           if percent_enabled else {}))
                if proposed["next_request"] is None:
                    status = proposed["status"]
                    break
                action = proposed["next_request"]
                pending = {"index": len(observations),
                           "target": action["target"],
                           "iterations": action["iterations"],
                           "phase": action["phase"],
                           "decision": proposed["decision"]}
                if special_enabled:
                    pending.update({key: action[key] for key in metadata_keys})
                atomic(pending_path, pending)
            req, folder = _request(context, flask_vector, output, pending)
            previous_marker = folder.parent / "V065_PROGRESS.json"
            prior_attempt = (read_json(previous_marker).get("native_attempts")
                             if previous_marker.exists() else 0)
            need(prior_attempt in (0, 1), "CASE_ATTEMPT_MARKER_INVALID")
            cached_case = (folder / "result.json").is_file() and (
                folder / "native_receipt.json").is_file()
            # Crash after starting Native with neither complete receipt nor
            # authenticated recoverable result must never consume another
            # Native automatically.
            if prior_attempt and not cached_case and not (
                    recover_verified_partial and
                    (folder / "result.json").is_file()):
                raise LongRunBlocked("PARTIAL_NATIVE_NEEDS_EXPLICIT_RECOVERY")
            if not cached_case and not prior_attempt:
                if cache_only:
                    status = "PAUSED_CACHE_ONLY"
                    break
                if (max_new_native_this_invocation is not None and
                        new_this_invocation >= max_new_native_this_invocation):
                    status = "PAUSED_INVOCATION_NATIVE_BUDGET"
                    break
                need(attempts < max_native_calls, "TOTAL_NATIVE_BUDGET_EXHAUSTED")
                if cancel_file and pathlib.Path(cancel_file).exists():
                    status = "PAUSED_USER_CANCEL"
                    break
            # v065 is a scoped per-case executor; per-case marker resides in a
            # unique parent, and v291 owns the global multi-case limit.
            progress = {"native_attempts": prior_attempt}
            native_started = time.monotonic()
            result = engine.execute_one(
                req, calibration, binary, folder, progress,
                cancel_file=cancel_file, cache_only=cache_only,
                recover_verified_partial=recover_verified_partial)
            native_elapsed = time.monotonic() - native_started
            native_bytes = (folder / "result.json").read_bytes()
            native_doc = json.loads(native_bytes)
            native = oil.ingest_native(req, native_doc, native_bytes)
            native["simc_seed"] = _source_seed(native_doc, result)
            need(result["native_json_sha256"] == native["native_json_sha256"]
                 and result["case_key"] == native["case_key"],
                 "NATIVE_DOUBLE_ACCEPTANCE_DRIFT")
            source = result["source"]
            if source == "NEW_NATIVE":
                attempts += 1
                new_this_invocation += 1
            else:
                cached_this_invocation += 1
            row = _compact(req, native, source, pending)
            _append_journal(journal_path, row)
            observations.append(row)
            pending_path.unlink()
            if (percent_enabled and source == "NEW_NATIVE" and
                    row["phase"] == "scout" and
                    math.isfinite(native_elapsed) and native_elapsed > 0):
                timings.append({"index": row["index"],
                                "seconds": round(native_elapsed, 6)})
                timings = timings[-11:]
                try:
                    atomic(timing_path, timings)
                except OSError:
                    # Optional pacing telemetry never invalidates real Native.
                    pass
            pending = None
            atomic(progress_path, {
                "schema": SCHEMA, "status": "CHECKPOINTED",
                "completed_cases": len(observations),
                "native_attempts_cumulative": attempts,
                "new_native_this_invocation": new_this_invocation,
                "verified_cached_this_invocation": cached_this_invocation,
                "last_case_key": req["case_key"],
                "global_optimum_proven": False})
    except Exception as exc:
        status = "PARTIAL_OR_BLOCKED"
        atomic(progress_path, {
            "schema": SCHEMA, "status": status,
            "error": type(exc).__name__ + ":" + str(exc),
            "completed_cases": len(observations),
            "native_attempts_cumulative": _count_attempts(output),
            "global_optimum_proven": False})
        raise
    summary = _summary(observations, context)
    report = {"schema": SCHEMA, "status": status,
              "policy": (dense_grid.SCHEMA if grid_enabled
                         else seed_escape_regions.SCHEMA if seed_retained_coarse_escape_regions
                         else hybrid_regions.SCHEMA if hybrid_region_grid_neighbors
                         else durable_regions.SCHEMA if adaptive_region_resources
                         else nested_regions.SCHEMA if nested_percent_grid
                         else multiregion_grid.SCHEMA if multiregion_percent_grid
                         else percent_grid.SCHEMA if percent_enabled
                         else "v290_multiscale_noisy_simplex_policy_v1"),
              "official_formula": "T=G+J+F+O",
              "base_B": B, "fixed_O": identity["oil_vector"],
              "final_T": identity["approved_final_T"],
              "native_attempts_cumulative": attempts,
              "new_native_this_invocation": new_this_invocation,
              "verified_cache_cases_this_invocation": cached_this_invocation,
              "completed_cases": len(observations),
              "summary": summary,
              "confirmed_selected_pair_95": confirmed_selected_pair_95(
                  observations, confirm_iters),
              "confidence_for_display": 0.95,
              "no_global_optimum_proof": True,
              "native_cases_not_to_be_confused_with_iterations": True}
    if grid_enabled:
        report["dense_grid_coverage"] = dense_grid.coverage(
            observations, total=B, lower=lower, upper=upper,
            max_level=dense_nested_grid_max_level)
    atomic(report_path, report)
    atomic(progress_path, {
        "schema": SCHEMA, "status": status,
        "completed_cases": len(observations),
        "native_attempts_cumulative": attempts,
        "new_native_this_invocation": new_this_invocation,
        "verified_cached_this_invocation": cached_this_invocation,
        "global_optimum_proven": False})
    if open_folder and os.name == "nt":
        try:
            os.startfile(str(output))
        except Exception:
            pass
    return report



def stage_extended_manifest(ready, manifest_path, max_native_calls, *,
                            source_loader=None):
    """Fork a verified *input only*, not the old v094/v291 result/cache.

    This is the product user's explicit long-run budget opt-in. Keep exact
    profile, F/O/J/gear and source evidence byte-identical. The newly typed
    runtime changes the scenario digest; v096 must reauthenticate it BEFORE
    accepting any Native candidate. No historical sessions are overwritten.
    """
    manifest_path=pathlib.Path(manifest_path).resolve(strict=True)
    need(type(max_native_calls) is int and
         6 <= max_native_calls <= 100000,
         "EXTENDED_NATIVE_BUDGET_RANGE")
    need(type(ready) is dict and "manifest" in ready and
         "paths" in ready and "plan" in ready,
         "VERIFIED_V096_ENTRY_REQUIRED")
    paths=ready["paths"]
    cfg=read_json(paths["scenario_json"])
    existing=cfg["runtime"]["max_native_calls"]
    need(type(existing) is int and 1<=existing<max_native_calls,
         "ONLY_INCREASE_VERIFIED_RUNTIME_BUDGET")
    cfg["runtime"]["max_native_calls"]=max_native_calls
    original=ready["manifest"]
    need(type(original) is dict and original["native_limit"]>=6 and
         original["native_limit"]<=max_native_calls,
         "EXISTING_TYPED_NATIVE_LIMIT_NOT_COMPATIBLE")
    copied=dict(original)
    copied.update({
        "profile_simc":"profile.simc",
        "scenario_json":"scenario.json",
        "fillers_json":"fillers.json",
        "static_cache_json":(
            str(paths["static_cache_json"])
            if paths["static_cache_json"] is not None else None),
        "native_binary":str(paths["native_binary"]),
        "output_dir":"simc_results",
        "cancel_file":"CANCEL",
    })
    directory=manifest_path.parent/("v291_longrun_%d"%max_native_calls)
    need(not directory.is_symlink(),"LONGRUN_STAGE_SYMLINK")
    directory.mkdir(parents=True,exist_ok=True)
    def write_identical(path,data):
        need(not path.is_symlink() and
             (not path.exists() or path.is_file() and
              path.read_bytes()==data),
             "LONGRUN_STAGED_SESSION_SOURCE_DRIFT")
        if not path.exists():
            path.write_bytes(data)
    inputs={
        "profile.simc":pathlib.Path(paths["profile_simc"]).read_bytes(),
        "scenario.json":(json.dumps(cfg,sort_keys=True,
                                     separators=(",",":"),ensure_ascii=False)
                         +"\n").encode("utf8"),
        "fillers.json":pathlib.Path(paths["fillers_json"]).read_bytes(),
        "manifest.json":(json.dumps(copied,sort_keys=True,
                                    separators=(",",":"),ensure_ascii=False)
                         +"\n").encode("utf8"),
    }
    for file,content in inputs.items():
        write_identical(directory/file,content)
    if source_loader is None:
        import v096_unified_product_entry as entry
        source_loader=entry.source
    upgraded=source_loader(directory/"manifest.json")
    old_plan=ready["plan"]
    new_plan=upgraded["plan"]
    need(all(new_plan.get(k)==old_plan.get(k) for k in
             ("base_B","fixed_O","final_T","source_profile_sha256",
              "budget_source","binary_sha256"))
         and new_plan["scenario_digest"]!=old_plan["scenario_digest"],
         "EXTENDED_RUNTIME_MUST_REAUTHENTICATE_SOURCE_NEW_SESSION")
    new_runtime=upgraded["context"]["bundle"]["prepared"]["scenario"][
        "scenario"]["runtime"]
    need(new_runtime["max_native_calls"]==max_native_calls,
         "EXTENDED_RUNTIME_NOT_EFFECTIVE")
    return upgraded, directory/"manifest.json"


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Long-run v290 Native execution through exact v093/v065")
    p.add_argument("--manifest", required=True)
    p.add_argument("--max-native-calls", type=int, required=True)
    p.add_argument("--max-new-native-this-invocation", type=int, default=None)
    p.add_argument("--max-elapsed-seconds", type=float, default=None)
    p.add_argument("--cache-only", action="store_true")
    p.add_argument("--recover-verified-partial", action="store_true")
    p.add_argument("--adaptive-region-resources", action="store_true",
                   help="EXPERIMENTAL, opt-in v303 region resource policy")
    p.add_argument("--hybrid-region-grid-neighbors", action="store_true",
                   help="EXPERIMENTAL, opt-in v305 grid + v290 regional moves")
    p.add_argument("--seed-retained-coarse-escape-regions", action="store_true",
                   help="EXPERIMENTAL, opt-in v306 seed retention and 12/24 pct B escapes")
    p.add_argument("--dense-nested-grid-max-level", type=int,
                   choices=dense_grid.LEVELS, default=None,
                   help="EXPERIMENTAL v307 nested coverage grid, 6/11/21/41/81")
    p.add_argument("--adaptive-global-calls", type=int, default=160)
    p.add_argument("--adaptive-confirm-calls", type=int, default=8)
    p.add_argument("--portable-archive",
                   help="Explicit original v291 Native case ZIP (import only)")
    p.add_argument("--portable-archive-sha256",
                   help="Approved SHA256 of exact original ZIP")
    args = p.parse_args(argv)
    import v096_unified_product_entry as product
    ready = product.source(args.manifest)
    original_runtime=ready["context"]["bundle"]["prepared"]["scenario"]["scenario"]["runtime"]
    if args.max_native_calls>original_runtime["max_native_calls"]:
        ready,_=stage_extended_manifest(ready,args.manifest,args.max_native_calls,
                                        source_loader=product.source)
    paths = ready["paths"]
    try:
        need(bool(args.portable_archive) ==
             bool(args.portable_archive_sha256),
             "PORTABLE_ARCHIVE_AND_SHA_MUST_BE_PAIRED")
        if args.portable_archive:
            # Import only: any new Native after rekeyed SHA validation requires
            # a separate explicit invocation on the sealed resumed session.
            need(args.max_new_native_this_invocation in (None, 0) and
                 args.recover_verified_partial is False,
                 "PORTABLE_IMPORT_SEPARATE_FROM_NEW_NATIVE_OR_PARTIAL_RECOVERY")
            import v292_portable_native_case_cache as portable
            result = portable.import_verified_archive(
                ready["context"], ready["flask"], paths["native_binary"],
                paths["output_dir"], args.portable_archive,
                args.portable_archive_sha256,
                max_native_calls=args.max_native_calls)
        else:
            result = run(
                ready["context"], ready["flask"], paths["native_binary"],
                paths["output_dir"], max_native_calls=args.max_native_calls,
                max_new_native_this_invocation=args.max_new_native_this_invocation,
                max_elapsed_seconds=args.max_elapsed_seconds,
                cancel_file=paths["cancel_file"], cache_only=args.cache_only,
                recover_verified_partial=args.recover_verified_partial,
                adaptive_region_resources=args.adaptive_region_resources,
                hybrid_region_grid_neighbors=args.hybrid_region_grid_neighbors,
                seed_retained_coarse_escape_regions=args.seed_retained_coarse_escape_regions,
                dense_nested_grid_max_level=args.dense_nested_grid_max_level,
                adaptive_initial_global_calls=args.adaptive_global_calls,
                adaptive_confirmation_calls=args.adaptive_confirm_calls,
                open_folder=True)
        print(json.dumps({"status": result["status"],
                          "completed_cases": result["completed_cases"],
                          "native_attempts_cumulative":
                          result["native_attempts_cumulative"],
                          "report": str(paths["output_dir"] / "V291_RESULT.json")},
                         ensure_ascii=False))
        return 0
    except Exception as exc:
        print("V291_BLOCKED_OR_PARTIAL:", type(exc).__name__, str(exc),
              file=sys.stderr)
        print("Result folder:", paths["output_dir"], file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
