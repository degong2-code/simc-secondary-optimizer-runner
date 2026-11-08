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
    actual = oil.ingest_native(req, json.loads(native_bytes), native_bytes)
    need(actual["native_json_sha256"] == receipt["native_json_sha256"]
         and actual["case_key"] == receipt["case_key"],
         "EXISTING_NATIVE_AND_OIL_VALIDATOR_DISAGREE")
    return actual, receipt["source"]


def _compact(req, native, source, plan):
    return {
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


def run(context, flask_vector, binary, output, *,
        max_native_calls, max_new_native_this_invocation=None,
        cache_only=False, cancel_file=None, max_elapsed_seconds=None,
        recover_verified_partial=False, open_folder=False):
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
        req, folder = _request(context, flask_vector, output, plan)
        actual, _ = _verified_row(req, binary, folder, calibration, allow_cache=True)
        expected = _compact(req, actual, row["source"], plan)
        need(expected == row, "RECORDED_NATIVE_CASE_BYTES_OR_SUMMARY_DRIFT")
        observations.append(row)
    pending = read_json(pending_path) if pending_path.exists() else None
    if pending is not None and pending["index"] < len(stored):
        row = stored[pending["index"]]
        need(all(row[k] == pending[k] for k in
                 ("index", "target", "iterations", "phase")),
             "ALREADY_COMMITTED_PENDING_DISAGREES")
        pending_path.unlink()
        pending = None
    need(pending is None or
         (pending["index"] == len(stored) and
          set(pending) == {"index", "target", "iterations", "phase",
                           "decision"}),
         "PENDING_CASE_NOT_CONTIGUOUS")
    attempts = _count_attempts(output)
    need(attempts <= max_native_calls, "PREVIOUS_NATIVE_ATTEMPTS_EXCEED_BUDGET")
    need(attempts >= len(stored), "JOURNAL_WITHOUT_NATIVE_ATTEMPT")
    new_this_invocation = 0
    cached_this_invocation = len(stored)
    started = time.monotonic()
    status = "STARTED"
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
                proposed = search.next_plan(
                    [{"target": row["target"], "iterations": row["iterations"],
                      "dps_mean": row["dps_mean"], "dps_sem": row["dps_sem"]}
                     for row in observations],
                    total=B, lower=lower, upper=upper,
                    native_calls_used=attempts,
                    max_native_calls=max_native_calls,
                    scout_iterations=scout_iters,
                    confirmation_iterations=confirm_iters,
                    max_iterations=confirm_iters)
                if proposed["next_request"] is None:
                    status = proposed["status"]
                    break
                action = proposed["next_request"]
                pending = {"index": len(observations),
                           "target": action["target"],
                           "iterations": action["iterations"],
                           "phase": action["phase"],
                           "decision": proposed["decision"]}
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
            result = engine.execute_one(
                req, calibration, binary, folder, progress,
                cancel_file=cancel_file, cache_only=cache_only,
                recover_verified_partial=recover_verified_partial)
            native_bytes = (folder / "result.json").read_bytes()
            native = oil.ingest_native(req, json.loads(native_bytes),
                                       native_bytes)
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
              "policy": "v290_multiscale_noisy_simplex_policy_v1",
              "official_formula": "T=G+J+F+O",
              "base_B": B, "fixed_O": identity["oil_vector"],
              "final_T": identity["approved_final_T"],
              "native_attempts_cumulative": attempts,
              "new_native_this_invocation": new_this_invocation,
              "verified_cache_cases_this_invocation": cached_this_invocation,
              "completed_cases": len(observations),
              "summary": summary,
              "confidence_for_display": 0.95,
              "no_global_optimum_proof": True,
              "native_cases_not_to_be_confused_with_iterations": True}
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


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Long-run v290 Native execution through exact v093/v065")
    p.add_argument("--manifest", required=True)
    p.add_argument("--max-native-calls", type=int, required=True)
    p.add_argument("--max-new-native-this-invocation", type=int, default=None)
    p.add_argument("--max-elapsed-seconds", type=float, default=None)
    p.add_argument("--cache-only", action="store_true")
    p.add_argument("--recover-verified-partial", action="store_true")
    args = p.parse_args(argv)
    import v096_unified_product_entry as product
    ready = product.source(args.manifest)
    paths = ready["paths"]
    try:
        result = run(
            ready["context"], ready["flask"], paths["native_binary"],
            paths["output_dir"], max_native_calls=args.max_native_calls,
            max_new_native_this_invocation=args.max_new_native_this_invocation,
            max_elapsed_seconds=args.max_elapsed_seconds,
            cancel_file=paths["cancel_file"], cache_only=args.cache_only,
            recover_verified_partial=args.recover_verified_partial,
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
