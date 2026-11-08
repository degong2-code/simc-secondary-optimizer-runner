#!/usr/bin/env python3
"""v292: verified portability of source-bound SimC cases across output paths.

The old Native input, JSON2 and v065 receipt MUST validate under the exact
original request. The unmodified JSON2 is separately validated against the
new request. No SimC execution or change to existing v064/v065 validators.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import pathlib
import re
import shutil
import tempfile
import zipfile

import v063_numeric_injection as numeric
import v291_durable_multiscale_native_runner as runner

SHA = re.compile(r"[0-9a-f]{64}\Z")
MAX_ARCHIVE_BYTES = 64_000_000
MAX_EXPANDED_BYTES = 160_000_000
MAX_FILE_BYTES = 50_000_000
MAX_CASES = 32


def need(ok, reason):
    runner.need(ok, "PORTABLE_" + reason)


def _load_zip(path, expected_sha):
    need(type(expected_sha) is str and SHA.fullmatch(expected_sha),
         "EXACT_ORIGINAL_ARCHIVE_SHA_REQUIRED")
    path = pathlib.Path(path).resolve(strict=True)
    need(path.is_file() and 0 < path.stat().st_size <= MAX_ARCHIVE_BYTES,
         "BOUNDED_ARCHIVE_FILE_REQUIRED")
    raw = path.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == expected_sha,
         "ORIGINAL_ARCHIVE_SHA_MISMATCH")
    archive = zipfile.ZipFile(io.BytesIO(raw))
    seen, expanded = set(), 0
    for item in archive.infolist():
        need(item.filename not in seen and not item.is_dir(),
             "DUPLICATE_OR_DIRECTORY_MEMBER")
        seen.add(item.filename)
        mode = item.external_attr >> 16 & 0o170000
        need(mode in (0, 0o100000), "NONREGULAR_ARCHIVE_MEMBER")
        need(0 <= item.file_size <= MAX_FILE_BYTES,
             "OVERSIZED_ARCHIVE_MEMBER")
        expanded += item.file_size
        need(expanded <= MAX_EXPANDED_BYTES, "ARCHIVE_EXPANSION_LIMIT")
    return archive, seen


def _current_seal(context, flask, binary, limit):
    binary = pathlib.Path(binary).resolve(strict=True)
    identity = context["identity"]
    need(hashlib.sha256(binary.read_bytes()).hexdigest() ==
         identity["binary_sha256"], "BINARY_BYTES_CHANGED")
    need(runner.adaptive.identity(context["bundle"],
         identity["binary_sha256"], identity["revision"],
         identity["scout_iterations"],
         identity["confirm_iterations"]) == identity,
         "UNVERIFIED_CURRENT_CONTEXT")
    scenario = context["bundle"]["prepared"]["scenario"]
    need(type(limit) is int and 1 <= limit <=
         scenario["scenario"]["runtime"]["max_native_calls"],
         "CURRENT_NATIVE_BUDGET_EXCEEDED")
    runner.scenario.vector(flask, "V292_FLASK_F")
    need(sum(flask.values()) == scenario["budget"]["F"],
         "CURRENT_FLASK_BUDGET_CHANGED")
    B, lower, upper = runner.constraints.bounds(
        scenario, runner.adaptive.feasible_budget(context, flask))
    need(B == identity["base_B"] and
         identity["scout_iterations"] < identity["confirm_iterations"],
         "CURRENT_BASE_OR_ITERATIONS_CHANGED")
    seal = {
        "schema": runner.SCHEMA,
        "policy_sha256": hashlib.sha256(
            pathlib.Path(runner.search.__file__).read_bytes()).hexdigest(),
        "context": identity,
        "flask_F": flask,
        "max_native_calls": limit,
        "scout_iterations": identity["scout_iterations"],
        "confirm_iterations": identity["confirm_iterations"],
        "B": B,
        "lower": runner.constraints.to_target(lower),
        "upper": runner.constraints.to_target(upper),
        "statistical_confidence": 0.95,
    }
    return seal, (B, lower, upper)


def _same_context(origin, active):
    need(type(origin) is dict and type(active) is dict,
         "SOURCE_CONTEXT_REQUIRED")
    a, b = dict(origin), dict(active)
    old_env = a.pop("admitted_season_environment_identity", None)
    new_env = b.pop("admitted_season_environment_identity", None)
    need(a == b, "SIMC_PROFILE_SCENARIO_BINARY_OR_OPTIONS_CHANGED")
    need((old_env is None) == (new_env is None),
         "ENVIRONMENT_ATTESTATION_PRESENCE_DRIFT")
    if old_env is not None:
        keys = {"environment_build_receipt_sha256",
                "environment_manifest_sha256",
                "source_catalog_artifact_sha256", "source_input_sha256"}
        need(type(old_env) is dict and type(new_env) is dict and
             set(old_env) == keys and set(new_env) == keys and
             all(type(x) is str and SHA.fullmatch(x) for x in
                 (*old_env.values(), *new_env.values())),
             "ENVIRONMENT_ATTESTATION_STRUCTURE_DRIFT")
        # Only source wrapper receipt/input hashes may vary across runs.
        # Actual catalog, scenario, exact slots and whole profile must match.
        need(old_env["source_catalog_artifact_sha256"] ==
             new_env["source_catalog_artifact_sha256"],
             "SEASON_SOURCE_CATALOG_CHANGED")


def _original_json2(source, index):
    paths = [s.partition("=")[2] for s in source.splitlines()
             if s.startswith("json2=")]
    need(len(paths) == 1 and paths[0] and
         pathlib.Path(paths[0]).is_absolute(),
         "ORIGINAL_ABSOLUTE_JSON2_DESTINATION_REQUIRED")
    p = pathlib.Path(paths[0])
    need(p.name == "result.json" and p.parent.name == "native" and
         p.parent.parent.name == "case_%05d" % index,
         "ORIGINAL_CASE_DESTINATION_DRIFT")
    return p


def _verify_case(archive, old, context, flask, destination, index, bounds, history, limit):
    plan = {k: old[k] for k in ("index", "phase", "target", "iterations")}
    need(plan["index"] == index, "ORIGIN_JOURNAL_OUT_OF_ORDER")
    B, lower, upper = bounds
    proposed = runner.search.next_plan(
        history, total=B, lower=lower, upper=upper,
        native_calls_used=index, max_native_calls=limit,
        scout_iterations=context["identity"]["scout_iterations"],
        confirmation_iterations=context["identity"]["confirm_iterations"],
        max_iterations=context["identity"]["confirm_iterations"])
    next_req = proposed["next_request"]
    need(next_req is not None and
         all(next_req[k] == plan[k] for k in ("target", "phase", "iterations")),
         "POLICY_SEQUENCE_CHANGED")
    root = "cases/case_%05d/" % index
    old_bytes = archive.read(root + "input.simc")
    native_bytes = archive.read(root + "result.json")
    original_receipt_raw = archive.read(root + "native_receipt.json")
    original_receipt = json.loads(original_receipt_raw)
    original_source = old_bytes.decode("utf8")
    old_path = _original_json2(original_source, index)
    mode = runner._mode(plan["phase"], plan["iterations"],
                        context["identity"])
    old_request = runner.adaptive.request(
        context, plan["target"], flask, old_path, phase=mode)
    need(old_request["input"].encode("utf8") == old_bytes and
         old_request["input_sha256"] ==
         hashlib.sha256(old_bytes).hexdigest(),
         "ORIGINAL_EXACT_SIMC_SOURCE_NOT_REPRODUCIBLE")
    new_request, _ = runner._request(
        context, flask, destination, plan)
    need(old_request["case_key"] == new_request["case_key"] ==
         old["case_key"], "PATH_INVARIANT_CASE_KEY_DRIFT")
    need(numeric.input_parts(original_source) ==
         numeric.input_parts(new_request["input"]) and
         old_request["target"] == new_request["target"] and
         old_request["iterations"] == new_request["iterations"],
         "NON_JSON2_SIMC_INPUT_DRIFT")
    calibration = {"native_revision": context["identity"]["revision"]}
    # Reuse original v064 complete byte/source/static-CHMV/DPS acceptance.
    runner.engine.evaluator.verify_disk_cache(
        old_request, calibration, original_receipt, native_bytes)
    doc = json.loads(native_bytes)
    old_actual = runner.oil.ingest_native(old_request, doc, native_bytes)
    old_actual["simc_seed"] = runner._source_seed(doc, original_receipt)
    expected = runner._compact(old_request, old_actual, old["source"], plan)
    if old.get("simc_seed") is None and expected["simc_seed"] is not None:
        expected["simc_seed"] = None
    need(expected == old, "ORIGINAL_JOURNAL_NATIVE_SHA_DRIFT")
    # Revalidate the UNMODIFIED JSON2 under the new exact destination.
    new_actual = runner.oil.ingest_native(new_request, doc, native_bytes)
    new_actual["simc_seed"] = runner._source_seed(doc, original_receipt)
    new_receipt = runner.engine.evaluator.ingest_native(
        new_request, doc, calibration, native_bytes)
    new_receipt["simc_seed"] = new_actual["simc_seed"]
    digest = hashlib.sha256(native_bytes).hexdigest()
    need(digest == new_actual["native_json_sha256"] ==
         new_receipt["native_json_sha256"],
         "CURRENT_NATIVE_JSON2_REVALIDATION_DRIFT")
    row = runner._compact(new_request, new_actual,
                          "PORTABLE_REVALIDATED_NATIVE", plan)
    provenance = {
        "schema": "v292_portable_case_provenance_v1",
        "original_case_key": old["case_key"],
        "original_input_sha256": old["input_sha256"],
        "original_native_sha256": old["native_sha256"],
        "original_receipt_sha256":
            hashlib.sha256(original_receipt_raw).hexdigest(),
        "current_input_sha256": new_request["input_sha256"],
        "native_reexecuted": False,
    }
    return (plan, new_request, new_receipt, native_bytes, row, provenance)


def import_verified_archive(context, flask, binary, destination, archive_path,
                            expected_sha256, *, max_native_calls):
    """Import a bounded, exact-SHA ZIP into a brand-new sealed v291 session."""
    destination = pathlib.Path(destination).resolve()
    need(not destination.exists(), "IMPORT_DESTINATION_MUST_BE_NEW")
    seal, bounds = _current_seal(context, flask, binary, max_native_calls)
    archive, members = _load_zip(archive_path, expected_sha256)
    try:
        need({"V291_SESSION.json", "V291_JOURNAL.jsonl"} <= members,
             "ORIGINAL_SESSION_AND_JOURNAL_REQUIRED")
        original = json.loads(archive.read("V291_SESSION.json"))
        former, current = dict(original), dict(seal)
        _same_context(former.pop("context", None),
                      current.pop("context", None))
        need(former == current, "SOURCE_SESSION_POLICY_OR_BUDGET_CHANGED")
        lines = archive.read("V291_JOURNAL.jsonl").splitlines()
        need(1 <= len(lines) <= min(max_native_calls, MAX_CASES),
             "ORIGINAL_CASE_COUNT_BOUND")
        expected = {"V291_SESSION.json", "V291_JOURNAL.jsonl"}
        for i in range(len(lines)):
            expected.update({
                "cases/case_%05d/%s" % (i, name)
                for name in ("input.simc", "result.json",
                             "native_receipt.json")})
        need(expected <= members and members - expected <=
             {"V291_RESULT.json", "V291_PROGRESS.json"},
             "FOREIGN_OR_MISSING_ARCHIVE_MEMBERS")
        cases, history = [], []
        for i, raw_line in enumerate(lines):
            old = json.loads(raw_line)
            need(type(old) is dict and old.get("source") in
                 ("NEW_NATIVE", "CACHED_VERIFIED_NATIVE",
                  "PORTABLE_REVALIDATED_NATIVE"),
                 "ORIGIN_MUST_BE_VERIFIED_NATIVE")
            case = _verify_case(archive, old, context, flask, destination,
                                i, bounds, history, max_native_calls)
            cases.append(case)
            history.append(case[4])
    finally:
        archive.close()
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = pathlib.Path(tempfile.mkdtemp(
        prefix=".v292-stage-", dir=destination.parent))
    try:
        runner.atomic(stage / "V291_SESSION.json", seal)
        for plan, req, receipt, native, row, provenance in cases:
            folder = runner.case_folder(stage, plan["index"])
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "input.simc").write_bytes(req["input"].encode("utf8"))
            (folder / "result.json").write_bytes(native)
            runner.atomic(folder / "native_receipt.json", receipt)
            runner.atomic(folder.parent / "V065_PROGRESS.json", {
                "native_attempts": 1,
                "status": "PORTABLE_VERIFIED_NATIVE_NO_NEW_SIMC"})
            runner.atomic(folder.parent / "V292_ORIGIN.json", provenance)
            runner._append_journal(stage / "V291_JOURNAL.jsonl", row)
        runner.atomic(stage / "V292_IMPORT.json", {
            "schema": "v292_portable_native_case_import_v1",
            "original_archive_sha256": expected_sha256,
            "imported_native_cases": len(cases),
            "new_native_executions": 0,
            "validated_case_keys": [case[4]["case_key"]
                                    for case in cases],
            "source_catalog_and_full_simc_profile_verified": True,
        })
        need(not destination.exists(), "IMPORT_DESTINATION_RACE")
        os.replace(stage, destination)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    # v291 itself verifies EVERY imported row and the new exact input SHA.
    replay = runner.run(context, flask, binary, destination,
                        max_native_calls=max_native_calls,
                        max_new_native_this_invocation=0, cache_only=True)
    need(replay["completed_cases"] == len(cases) and
         replay["new_native_this_invocation"] == 0,
         "POST_IMPORT_REPLAY_MUST_USE_ZERO_NATIVE")
    return replay
