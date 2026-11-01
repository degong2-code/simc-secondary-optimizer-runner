#!/usr/bin/env python3
"""v219 non-persistent local Stage reuse cost probe. OFFLINE, never runs SimC.

Uses the real v113 /sessions/plan -> v217/v218 profile stage path with a
synthetic binary. Reports observed timing and Path.read_bytes I/O only; these
measurements never enter session identity, stage receipts, or DPS caches.
This is NOT a user-PC SimC acceptance or a universal speed benchmark.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import tempfile
import time
from unittest import mock

from fastapi.testclient import TestClient

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))
import v106_user_session_controller as sessions
import v113_local_web_api as web

SCHEMA = "v219_offline_profile_stage_efficiency_observation_v1"
REPETITIONS = 3


def immutable_snapshot(folder):
    """Read outside the timed section; inspect bytes AND file mtimes."""
    files = {}
    for path in sorted(folder.rglob("*")):
        if path.is_file():
            raw = path.read_bytes()
            files[path.relative_to(folder).as_posix()] = {
                "size": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "mtime_ns": path.stat().st_mtime_ns,
            }
    return files


def run_probe():
    with tempfile.TemporaryDirectory(prefix="simc-v219-offline-") as tmp:
        root = pathlib.Path(tmp)
        fake_binary = root / "simc.fake"
        fake_binary.write_bytes(b"V219_FAKE_BINARY_NOT_SIMC_NATIVE")
        sessions_root = root / "sessions"
        app = web.create_app(root=sessions_root, token="v219-offline-only")
        client = TestClient(app, base_url="http://127.0.0.1:8765")
        payload = {
            "controls": sessions.standard_controls(("evoker", "devastation")),
            "binary": str(fake_binary),
            "revision": "7bc1071",
            "static_cache": None,
            "current_season_product": False,
        }
        headers = {
            "x-simc-local-token": "v219-offline-only",
            "origin": "http://127.0.0.1:8765",
            "content-type": "application/json",
        }
        original_read_bytes = pathlib.Path.read_bytes
        samples = []
        session_id = None
        baseline_files = None
        with mock.patch.object(web.bootstrap, "build",
                               wraps=web.bootstrap.build) as generator, \
             mock.patch.object(web.subprocess, "Popen",
                               side_effect=AssertionError("NO_NATIVE_PERMITTED")) as spawn:
            for index in range(REPETITIONS + 1):
                reads = {"path_read_bytes_calls": 0,
                         "path_read_bytes_total_bytes": 0}

                def observed_read_bytes(path):
                    raw = original_read_bytes(path)
                    reads["path_read_bytes_calls"] += 1
                    reads["path_read_bytes_total_bytes"] += len(raw)
                    return raw

                with mock.patch.object(pathlib.Path, "read_bytes",
                                       observed_read_bytes):
                    before_ns = time.perf_counter_ns()
                    response = client.post("/api/v1/sessions/plan",
                                           json=payload, headers=headers)
                    elapsed_ns = time.perf_counter_ns() - before_ns
                if response.status_code != 200:
                    raise AssertionError(
                        f"OFFLINE_PLAN_FAILED:{response.status_code}:{response.text}")
                data = response.json()
                stage = data["profile_stage"]
                if session_id is None:
                    session_id = data["session_id"]
                assert data["session_id"] == session_id, "SESSION_ID_DRIFT"
                assert data["native_calls"] == 0, "UNEXPECTED_NATIVE"
                expected_status = ("EXECUTED_AND_SEALED" if index == 0
                                   else "REUSED_VERIFIED")
                assert stage["status"] == expected_status, "STAGE_EXECUTION_DRIFT"
                assert stage["executed"] == (index == 0), "EXECUTOR_CALLED_ON_REUSE"
                assert stage["receipt_writes"] == (2 if index == 0 else 0), \
                    "STAGE_RECEIPT_REWRITTEN"
                folder = sessions_root / session_id
                current = immutable_snapshot(folder)
                if baseline_files is None:
                    baseline_files = current
                    assert len(current) >= 7, "SEALED_STAGE_FILES_MISSING"
                else:
                    assert current == baseline_files, "SESSION_FILES_CHANGED_ON_REUSE"
                samples.append({
                    "request": "initial_build" if index == 0 else "verified_reuse",
                    "elapsed_ms": round(elapsed_ns / 1_000_000, 3),
                    **reads,
                    "stage_output_hash_bytes": stage["output_bytes"],
                    "stage_receipt_writes": stage["receipt_writes"],
                })
            assert generator.call_count == 1, "GENERATOR_WAS_REPEATED"
            spawn.assert_not_called()
        client.close()
        return {
            "schema": SCHEMA,
            "status": "PASS_REAL_PLAN_STAGE_REUSE_NO_NATIVE",
            "platform": sys.platform,
            "profile_supplier": "evoker/devastation",
            "samples": samples,
            "generator_calls": 1,
            "native_calls": 0,
            "network_calls": 0,
            "session_file_mutations_on_reuse": 0,
            "session_file_count": len(baseline_files),
            "timing_persisted_to_session": False,
            "io_scope": "Path.read_bytes only; excludes Path.read_text/open and OS cache",
            "notes": "Timing is observed, not a contractual speed-up threshold.",
        }


if __name__ == "__main__":
    try:
        print(json.dumps(run_probe(), ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")), flush=True)
    except Exception as exc:
        print("V219_OFFLINE_PROFILE_STAGE_EFFICIENCY_FAIL:",
              type(exc).__name__, str(exc), file=sys.stderr, flush=True)
        raise
