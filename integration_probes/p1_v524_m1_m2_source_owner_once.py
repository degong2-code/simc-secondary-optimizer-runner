#!/usr/bin/env python3
"""One bounded M1->M2 actual Environment Build, not a new budget engine.

Reuses v113/v216/v222/v212, performs no user DPS optimization and captures
only source-owner/manifest diagnostics. No historical source bytes are injected
as authorization. Exact current build, archived source SHAs and native identity
are reported separately; a same-build observation is NOT a source SHA match.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "runner")]
import v113_local_web_api as web
import v289_retail_live_build_source as retail

BUILD = "12.1.5.70783"
REV = "de11f57df75dda668bae6ac7043a43b98831fa96"
EXE_SHA = "1fc927d2be7f1b6064c75f004b5b22245b064a6b3e56e572af4048ba822a986d"
V523_V161_SHA = "f004a82fa9da52646dea49ded14ff6db756d8f903bafd29ce29449d71d9f3c6b"
V523_CURRENCY_SHA = "c1e91e4e17b622136d7c9a37c597cd0fe2409a2f5ccb494659014b154a04ef1f"
SCHEMA = "p1_v524_current_70783_m1_m2_one_actual_environment_diagnostic_v1"
KEYS = ("BLIZZARD_CLIENT_ID", "BLIZZARD_CLIENT_SECRET",
        "WCL_CLIENT_ID", "WCL_CLIENT_SECRET")


def digest(path):
    obj = hashlib.sha256()
    with pathlib.Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            obj.update(chunk)
    return obj.hexdigest()


class EphemeralActionsCredentials:
    """Use existing Actions secrets without writing a Windows credential."""
    def load(self):
        values = {key: os.environ.get(key, "") for key in KEYS}
        return values if all(values.values()) else None


def bounded_code(exc):
    code = str(exc).split(":", 1)[0].split("\n", 1)[0]
    return code if re.fullmatch(r"[A-Z][A-Z0-9_]{3,100}", code) else type(exc).__name__


def run(binary, out):
    out = pathlib.Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    output = out / "V524_M1_M2_SOURCE_OWNER_DIAGNOSTIC.json"
    state = {
        "schema": SCHEMA, "status": "NOT_RUN", "game_build": BUILD,
        "target_ilevel": None, "simc_revision": REV, "simc_binary_sha256": EXE_SHA,
        "historical_v523_v161_receipt_sha256": V523_V161_SHA,
        "historical_v523_currency_csv_sha256": V523_CURRENCY_SHA,
        "new_user_dps_native_calls": 0, "full_product_e2e": "PENDING",
        "global_optimum_proven": False, "environment_ready": False,
        "environment_installed": False, "source_compilation": None,
        "required_core_source_owner_report": None,
        "installed_manifest_sha256": None,
    }
    def save():
        output.write_text(json.dumps(state, ensure_ascii=False, sort_keys=True,
                                     indent=2, allow_nan=False) + "\n",
                          encoding="utf8")
    save()
    try:
        if sys.platform != "win32":
            raise RuntimeError("V524_WINDOWS_RUNNER_REQUIRED")
        binary = pathlib.Path(binary).resolve(strict=True)
        if binary.name.lower() != "simc.exe" or digest(binary) != EXE_SHA:
            raise RuntimeError("V524_OFFICIAL_BINARY_SHA_DRIFT")
        if (os.environ.get("SIMC_PINNED_SOURCE_COMMIT") != REV or
                os.environ.get("SIMC_PINNED_GAME_BUILD") != BUILD):
            raise RuntimeError("V524_SOURCE_PIN_DRIFT")
        if EphemeralActionsCredentials().load() is None:
            state["status"] = "PENDING_AUTHENTICATED_SOURCE_CREDENTIALS"
            save()
            return False
        banner = subprocess.run([str(binary)], input="", capture_output=True,
                                text=True, errors="replace", cwd=binary.parent,
                                timeout=25)
        if banner.returncode != 0 or BUILD not in (banner.stdout + "\n" + banner.stderr):
            raise RuntimeError("V524_SIMC_RETAIL_GAME_BUILD_DRIFT")
        live = retail.discover(region="KR")
        state["observed_live_retail_build"] = live.get("game_build")
        if live.get("game_build") != BUILD:
            state["status"] = "PENDING_RETAIL_BUILD_CHANGED"
            save()
            return False
        with tempfile.TemporaryDirectory(prefix="v524-m2-", dir=out) as temp:
            root = pathlib.Path(temp) / "runs"
            root.mkdir()
            jobs = web.LocalJobs(root, source_credential_store=EphemeralActionsCredentials())
            # The ORIGINAL M1 source-only request and the ORIGINAL M2 Build
            # use the same root, so v217 reuses the same Wago ten-table stage.
            myth = jobs.discover_season_myth_target(BUILD)
            state["m1"] = {
                key: myth.get(key) for key in (
                    "status", "reason_code", "game_build", "target_ilevel",
                    "currency_csv_sha256", "original_v161_receipt_sha256",
                    "currency_ids", "environment_ready")}
            state["target_ilevel"] = myth.get("target_ilevel")
            save()
            if (myth.get("status") !=
                    "MYTH_TARGET_CANDIDATE_FROM_MATCHED_WAGO_V163_SOURCE" or
                    myth.get("target_ilevel") != 334 or
                    not re.fullmatch(r"[a-f0-9]{64}",
                                     myth.get("currency_csv_sha256") or "")):
                state["status"] = "PENDING_M1_ACTUAL_SOURCE"
                save()
                return False
            observed = jobs.build_season_environment(
                game_build=BUILD, target_ilevel=myth["target_ilevel"],
                auto_initial_core_build=True,
                auto_initial_core_simc_binary=str(binary),
                simc_revision_hint=REV, existing_special_gem_id=None,
                source_target_socket_count=4,
                auto_myth_target_source_build=BUILD,
                auto_myth_target_source_sha256=myth["currency_csv_sha256"])
            compilation = observed.get("source_compilation") or {}
            progress = observed.get("zero_history_build") or {}
            install = compilation.get("verified_environment_install") or {}
            state["source_compilation"] = {
                "status": compilation.get("status"),
                "missing": compilation.get("missing"),
                "compiler_input_impact": compilation.get("compiler_input_impact")}
            state["required_core_source_owner_report"] = (
                progress.get("required_core_source_owner_report"))
            state["source_inventory"] = observed.get("source_inventory")
            state["zero_history_status"] = progress.get("status")
            state["required_information_scope"] = (
                progress.get("required_information_scope"))
            state["new_environment_native_calls"] = observed.get("native_calls")
            state["environment_ready"] = observed.get("environment_ready") is True
            state["environment_installed"] = observed.get("environment_installed") is True
            state["installed_manifest_sha256"] = install.get("manifest_sha256")
            if state["environment_ready"]:
                state["budget"] = {
                    key: observed.get(key) for key in ("G", "J", "F", "O", "B", "T")}
            receipt = root / "_fresh_season_sources" / ("wago_" + BUILD) / "wago" / "receipt.json"
            if receipt.is_file() and not receipt.is_symlink():
                state["actual_v161_receipt_sha256"] = digest(receipt)
                state["v161_identity_matches_v523"] = (
                    state["actual_v161_receipt_sha256"] == V523_V161_SHA)
            state["v522_identity_matches_v523"] = (
                myth["currency_csv_sha256"] == V523_CURRENCY_SHA)
            state["status"] = ("PASS_ACTUAL_M1_M2_INSTALLED"
                               if state["environment_ready"] and
                                  state["environment_installed"] and
                                  isinstance(state["installed_manifest_sha256"], str)
                               else "PENDING_ACTUAL_M2_SOURCE_OR_BUDGET")
            save()
            return state["status"] == "PASS_ACTUAL_M1_M2_INSTALLED"
    except Exception as exc:
        state["status"] = "BLOCKED_OR_PARTIAL_" + type(exc).__name__
        state["error_code"] = bounded_code(exc)
        save()
        return False
    finally:
        print("V524_M1_M2_RESULT " + json.dumps(
            {key: state.get(key) for key in (
                "status", "error_code", "target_ilevel",
                "environment_ready", "environment_installed",
                "new_environment_native_calls", "installed_manifest_sha256")},
            ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--simc", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    args = parser.parse_args()
    sys.exit(0 if run(args.simc, args.out) else 1)
