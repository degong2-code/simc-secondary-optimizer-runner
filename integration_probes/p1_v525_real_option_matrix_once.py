#!/usr/bin/env python3
"""Deterministic bounded real Windows option-matrix; zero AI runtime.

Existing v113/v216/v222/v212, v098/v096 and SimC own all mechanics.
No model endpoint, generated selection, item-effect emulation or synthetic
approval. Unknown 5+ sockets/enchants must be reported as blocked, not passed.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import zipfile

from fastapi.testclient import TestClient

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "runner"), str(ROOT / "integration_probes")]
import v046_static_item_cache as static
import v098_target_user_scenario_bootstrap as bootstrap
import v113_local_web_api as web
import v218_v098_profile_stage_adapter as stage
import p1_v524_m1_m2_source_owner_once as v524
import p1_v439_one_selected_70783_native as v439
from integration_probes import p3_haj_real_local_web_native_e2e as web_native

SCHEMA = "p1_v525_deterministic_real_70783_selected_option_matrix_v1"
BUILD = v524.BUILD
REV = v524.REV
EXE_SHA = v524.EXE_SHA
CACHE_SHA = "517cd212fe3d3011593a3fae0b2a2c06ff5865a40145e2279f04eb8820e132e8"
SPECIAL_NECK = 268250                  # DB2 70783 special_effect_gear_candidate
CRAFT_HEAD = 244579                     # v439 real Native observed
CRAFT_WRISTS = 244584                   # v057 mail crafted recipe ID, no inferred rating
CRAFT_OPTS = {"crafted_stats": "32/36", "embellishment": "arcanoweave_lining"}
TRINKETS = (
    (270175, 270173),                  # v146 hunter/survival source starters
    (270169, 270174),                  # v213-era 70783 source item candidates
    (270166, 270170),                  # v213-era 70783 source item candidates
)
MAX_ENV_NATIVE = 3
MAX_STATIC_NATIVE = 8
MAX_DPS_NATIVE = 30
MAX_NATIVE_TOTAL = MAX_ENV_NATIVE + MAX_STATIC_NATIVE + MAX_DPS_NATIVE


def need(ok, code):
    if not ok:
        raise RuntimeError("V525_" + code)


def raw_sha(path):
    h = hashlib.sha256()
    with pathlib.Path(path).open("rb") as handle:
        for b in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2,
                               sort_keys=True, allow_nan=False) + "\n", encoding="utf8")


def controls(trinkets=TRINKETS[0], *, special=False, crafted=0, enchant=None):
    c = web.sessions.standard_controls(("hunter", "survival"))
    c["race"] = "human"
    c["oil_hands"] = []
    c["trinket_ids"] = list(trinkets)
    c["special_items"] = ([{"slot": "neck", "item_id": SPECIAL_NECK,
                            "options": {}}] if special else [])
    c["embellishments"] = [
        {"slot": "head", "item_id": CRAFT_HEAD, "options": dict(CRAFT_OPTS)},
        {"slot": "wrists", "item_id": CRAFT_WRISTS,
         "options": dict(CRAFT_OPTS)}][:crafted]
    if enchant is not None:
        c["enchant_choices"] = {"finger1": enchant}
    return c


def response(client, method, uri, body=None):
    h = {"x-simc-local-token": "v525-matrix-test-token",
         "origin": "http://127.0.0.1:8765"}
    r = client.get(uri, headers=h) if method == "GET" else client.post(
        uri, headers=h, json=body if body is not None else {})
    if r.status_code == 200:
        return r.json()
    doc = r.json()
    detail = doc.get("detail", {}) if isinstance(doc, dict) else {}
    code = detail.get("code") if isinstance(detail, dict) else None
    return {"http_status": r.status_code,
            "blocked_code": code if isinstance(code, str) else "UNKNOWN"}


def digest_source_profiles(folder):
    result = []
    for path in sorted((folder / "generated" / "simc_results").rglob("input.simc")):
        text = path.read_text(encoding="utf8")
        def one(slot):
            rows = [x for x in text.splitlines() if x.startswith(slot + "=")]
            return rows[0] if len(rows) == 1 else None
        trinkets = [one("trinket1"), one("trinket2")]
        result.append({
            "input_sha256": raw_sha(path),
            "trinket_ids_present": all(isinstance(trinkets[i], str)
                       and ("id=" + str(json.loads(
                           (folder / "user.json").read_text(encoding="utf8")
                       )["trinkets"][i]["item_id"])) in trinkets[i]
                       for i in range(2)),
            "tier_chest_id_present": "id=271495" in (one("chest") or ""),
            "crafted_head_id_present": "id=244579" in (one("head") or ""),
            "crafted_wrists_id_present": "id=244584" in (one("wrists") or ""),
            "special_neck_id_present": "id=268250" in (one("neck") or ""),
        })
    return result


def run(binary, out, archived_cache):
    out = pathlib.Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    receipt_file = out / "V525_REAL_OPTION_MATRIX.json"
    report = {
        "schema": SCHEMA, "status": "STARTED", "game_build": BUILD,
        "revision": REV, "binary_sha256": EXE_SHA,
        "deterministic_input_only": True, "AI_calls": 0,
        "AI_decisions_in_runtime": 0, "effect_and_dps_owner": "EXISTING_SIMC",
        "max_new_native_total": MAX_NATIVE_TOTAL,
        "environment_native_attempts": 0,
        "static_native_attempts": 0,
        "dps_native_attempts": 0,
        "static_proofs": [], "cases": {},
        "full_product_e2e": "PENDING", "global_optimum_proven": False,
    }
    def checkpoint():
        report["new_native_attempts_total"] = (
            report["environment_native_attempts"] +
            report["static_native_attempts"] + report["dps_native_attempts"])
        need(report["new_native_attempts_total"] <= MAX_NATIVE_TOTAL,
             "NATIVE_BUDGET_EXCEEDED")
        save(receipt_file, report)
    checkpoint()
    try:
        binary = pathlib.Path(binary).resolve(strict=True)
        need(sys.platform == "win32" and binary.name.lower() == "simc.exe",
             "REAL_WINDOWS_PINNED_SIMC_REQUIRED")
        need(raw_sha(binary) == EXE_SHA and
             os.environ.get("SIMC_PINNED_SOURCE_COMMIT") == REV and
             os.environ.get("SIMC_PINNED_GAME_BUILD") == BUILD,
             "PINNED_SIMC_SOURCE_DRIFT")
        archived_cache = pathlib.Path(archived_cache).resolve(strict=True)
        need(raw_sha(archived_cache) == CACHE_SHA,
             "HISTORICAL_V439_STATIC_CACHE_SHA_DRIFT")
        need(static.load(archived_cache)["season"] == "midnight_s2",
             "HISTORICAL_STATIC_SEASON_CHANGED")
        need(v524.EphemeralActionsCredentials().load() is not None,
             "REQUIRED_AUTHENTICATED_SOURCE_CREDENTIALS_MISSING")
        live = v439.v343.retail.discover(region="KR")
        need(live.get("game_build") == BUILD, "ACTIVE_RETAIL_BUILD_CHANGED")
        with tempfile.TemporaryDirectory(prefix="v525-matrix-", dir=out) as temp:
            root = pathlib.Path(temp) / "runs"
            root.mkdir()
            owner = web.LocalJobs(
                root, source_credential_store=v524.EphemeralActionsCredentials())
            target = owner.discover_season_myth_target(BUILD)
            need(target.get("status") ==
                 "MYTH_TARGET_CANDIDATE_FROM_MATCHED_WAGO_V163_SOURCE"
                 and target.get("target_ilevel") == 334,
                 "M1_MYTH_ACTUAL_SOURCE_NOT_VERIFIED")
            report["m1_currency_sha256"] = target["currency_csv_sha256"]
            report["m1_target_ilevel"] = target["target_ilevel"]
            checkpoint()
            env = owner.build_season_environment(
                game_build=BUILD, target_ilevel=target["target_ilevel"],
                auto_initial_core_build=True,
                auto_initial_core_simc_binary=str(binary),
                simc_revision_hint=REV,
                existing_special_gem_id=None,
                source_target_socket_count=4,
                auto_myth_target_source_build=BUILD,
                auto_myth_target_source_sha256=target["currency_csv_sha256"])
            report["environment_native_attempts"] = env.get(
                "native_calls", MAX_ENV_NATIVE + 1)
            need(0 <= report["environment_native_attempts"] <= MAX_ENV_NATIVE
                 and env.get("environment_ready") is True
                 and env.get("environment_installed") is True
                 and env.get("G") == 2850 and env.get("J") == 92
                 and env.get("F") == 165 and env.get("B") == 3107
                 and env.get("T") == 3107 and sum(env["O"].values()) == 0,
                 "REAL_M2_INSTALLED_BASE_BUDGET_INVALID")
            compiled = env["source_compilation"]
            need(compiled.get("missing") == [] and
                 compiled["required_core_source_owner_report"][
                    "original_source_owner_missing_for_selected_request"] == [],
                 "REAL_SOURCE_OWNERS_NOT_COMPLETE")
            report["installed_manifest_sha256"] = compiled[
                "verified_environment_install"]["manifest_sha256"]
            checkpoint()
            native_cache = static.load(archived_cache)
            cache_file = out / "selected_v046_snapshot.json"
            static.write_atomic(cache_file, native_cache)
            source = compiled["source_catalog_path"]
            with web_native.verified_current_catalog(source, BUILD):
                app = web.create_app(root=root, token="v525-matrix-test-token")
                app.state.jobs.remember_verified_fresh_environment(env)
                with TestClient(app, base_url="http://127.0.0.1:8765") as client:
                    def payload(c, cache=None, sockets=None):
                        args = {"controls": c, "binary": str(binary),
                                "revision": REV, "current_season_product": True,
                                "installed_season_game_build": BUILD,
                                "installed_manifest_sha256":
                                    report["installed_manifest_sha256"]}
                        if cache is not None:
                            args["static_cache"] = str(cache)
                        if sockets is not None:
                            args["user_socket_total"] = sockets
                        return args

                    def block(label, c, *, sockets=None):
                        r = response(client, "POST", "/api/v1/sessions/plan",
                                     payload(c, sockets=sockets))
                        report["cases"][label] = {
                            "status": ("BLOCKED" if "http_status" in r else
                                       "UNEXPECTEDLY_ADMITTED"),
                            "http_status": r.get("http_status"),
                            "code": r.get("blocked_code"),
                            "new_native_calls": 0}
                        checkpoint()
                        return r

                    # Exercise user 4 -> 5 -> 6 socket totals against a
                    # *real installed J=92/4-socket source*. No bonus proof
                    # is injected; 5+/uninstalled must fail closed.
                    for n in (5, 6):
                        block("socket_" + str(n) + "_without_verified_J",
                              controls(), sockets=n)
                    # Other ring enchants are NOT approved for this install.
                    # 7967 has historical single-profile E0 evidence only:
                    # observe whether current v212 admits it; no forced pass.
                    for enchant_id in (7967, 8025, 7965):
                        block("ring_enchant_" + str(enchant_id),
                              controls(enchant=enchant_id))
                    # Three embellishments/gear-slot overlap: reject before
                    # Native and never treat as a supported loadout.
                    triple = controls(crafted=2)
                    triple["embellishments"].append({
                        "slot": "waist", "item_id": 244581,
                        "options": dict(CRAFT_OPTS)})
                    block("three_embellishments_rejected", triple)
                    clash = controls(special=True)
                    clash["embellishments"] = [{
                        "slot": "neck", "item_id": 244584,
                        "options": dict(CRAFT_OPTS)}]
                    block("special_crafted_same_slot_rejected", clash)

                    def prepare_selected(label, c):
                        user = web.sessions.user_scenario(c)
                        season = stage._verified_fresh_season_consumables(user)
                        def preview():
                            return bootstrap.preview_from_environment_build(
                                user, root / "selected_preview_only", binary, REV,
                                environment_result=env,
                                season_controls=season,
                                selected_static_cache_path=cache_file)
                        first = preview()
                        p = first.get("budget_preflight") or {}
                        missing = p.get("missing_exact_native_variants", [])
                        need(isinstance(missing, list) and
                             len(missing) <= MAX_STATIC_NATIVE and all(
                             x["identity"]["ilevel"] == 334 and
                             x["identity"]["season"] == "midnight_s2"
                             for x in missing), "SELECTED_STATIC_SCOPE_INVALID")
                        if missing:
                            # v439 collector uses static_01 etc. per work root;
                            # isolate each selected change set. The canonical
                            # append-only cache remains shared across all cases.
                            work = out / ("static_" + label)
                            work.mkdir(exist_ok=False)
                            v439.collect_missing(binary=binary, work=work,
                                cache=native_cache, missing=missing,
                                report=report, checkpoint=checkpoint)
                            static.write_atomic(cache_file, native_cache)
                        final = preview()
                        details = final.get("budget_preflight") or {}
                        report["cases"][label + "_preflight"] = {
                            "status": final.get("status"),
                            "static_native_new": len(missing),
                            "changed_slots": [x["slot"] for x in
                              details.get("changed_physical_slots", [])],
                            "four_tier_slots": details.get("four_tier_slots"),
                            "B": details.get("base_B"),
                            "T": details.get("final_T"),
                            "fixed_L": details.get("fixed_L_in_G_once"),
                            "J": details.get("J"), "F": details.get("F"),
                            "missing_variants_after": details.get(
                                "missing_exact_native_variants")}
                        checkpoint()
                        return final

                    special = controls(special=True)
                    combo = controls(TRINKETS[1], special=True, crafted=2)
                    special_pre = prepare_selected("special_neck", special)
                    combined_pre = prepare_selected(
                        "special_plus_two_crafted_and_four_tier", combo)

                    def native_case(label, c, *, selected=False,
                                    expect_four_tier=False, replay=False):
                        opts = payload(c, cache=cache_file if selected else None,
                                       sockets=4)
                        planned = response(
                            client, "POST", "/api/v1/sessions/plan", opts)
                        row = {"plan_status": planned.get("status"),
                               "plan_http": planned.get("http_status"),
                               "plan_blocked": planned.get("blocked_code")}
                        report["cases"][label] = row
                        checkpoint()
                        if planned.get("status") != "READY_ZERO_NATIVE":
                            row["status"] = "BLOCKED_PLAN"
                            checkpoint()
                            return False
                        sid = planned["session_id"]
                        row["session_id"] = sid
                        row["base_B"] = planned["plan"]["base_B"]
                        row["final_T"] = planned["plan"]["final_T"]
                        if expect_four_tier:
                            need(combined_pre["budget_preflight"][
                                    "four_tier_slots"] ==
                                 ["chest", "hands", "legs", "shoulders"],
                                 "COMBINED_FOUR_TIER_NOT_PRESENT")
                        started = response(
                            client, "POST", "/api/v1/sessions/start", opts)
                        row["start_status"] = started.get("status")
                        row["start_blocked"] = started.get("blocked_code")
                        if started.get("status") != "WORKER_STARTED":
                            row["status"] = "BLOCKED_START"
                            checkpoint()
                            return False
                        need(started.get("session_id") == sid and
                             started.get("static_L_native_calls_this_start", 0) == 0,
                             "DUPLICATE_STATIC_NATIVE_AT_START")
                        report["dps_native_attempts"] += 6
                        checkpoint()
                        worker = app.state.jobs.children[sid]
                        exit_code = worker.wait(timeout=660)
                        row["worker_exit"] = exit_code
                        if exit_code != 0:
                            row["status"] = "SIMC_WORKER_NONZERO"
                            checkpoint()
                            return False
                        finished = response(
                            client, "GET",
                            "/api/v1/sessions/" + sid + "/result")
                        row["result_blocked"] = finished.get("blocked_code")
                        if finished.get("native_calls_cumulative") != 6:
                            row["status"] = "DPS_SIX_CASE_COUNT_INVALID"
                            checkpoint()
                            return False
                        user_result = finished["user_result"]
                        observed = user_result["observed_first_choice"]
                        need(user_result["confidence_level"] == 0.95 and
                             user_result["global_optimum_proven"] is False and
                             sum(observed["absolute_rating_T"].values()) ==
                                 planned["plan"]["final_T"] and
                             observed["observed_dps_mean"] > 0 and
                             observed["simc_sem"] >= 0,
                             "REAL_DPS_CHMV_SEM_95_INVALID")
                        row["status"] = "PASS_REAL_SIX_SIMC_DPS"
                        row["DPS"] = observed["observed_dps_mean"]
                        row["SEM"] = observed["simc_sem"]
                        row["confidence"] = user_result["confidence_level"]
                        row["profile_inputs"] = digest_source_profiles(root / sid)
                        need(len(row["profile_inputs"]) == 6 and
                             all(x["trinket_ids_present"] for x in
                                 row["profile_inputs"]),
                             "TRINKET_SOURCE_ID_NOT_IN_ACTUAL_SIMC_INPUT")
                        if expect_four_tier:
                            need(all(x["tier_chest_id_present"] and
                                     x["crafted_head_id_present"] and
                                     x["crafted_wrists_id_present"] and
                                     x["special_neck_id_present"]
                                     for x in row["profile_inputs"]),
                                 "COMBINED_GEAR_TIER_SOURCE_NOT_IN_SIMC")
                        if replay:
                            replayed = response(client, "POST",
                                "/api/v1/sessions/" + sid + "/cache-only", {})
                            need(replayed.get("new_native_execution_permitted") is False,
                                 "CACHE_REPLAY_NOT_NATIVE_FREE")
                            need(app.state.jobs.children[sid].wait(timeout=180) == 0,
                                 "CACHE_REPLAY_WORKER_FAILED")
                            restored = response(client, "GET",
                                "/api/v1/sessions/" + sid + "/result")
                            need(restored["cache_hits_this_run"] == 6 and
                                 restored["user_result"] == finished["user_result"],
                                 "CACHE_REPLAY_SEMANTIC_OR_HITS_DRIFT")
                            row["cache_only_hits"] = 6
                            row["cache_only_new_native"] = 0
                        checkpoint()
                        return True

                    successes = {}
                    # Each run is an actual six-case adaptive SimC worker.
                    for label, c, sel, tier, cache in (
                            ("trinkets_starter", controls(TRINKETS[0]), False, False, True),
                            ("trinkets_swap_A", controls(TRINKETS[1]), False, False, False),
                            ("trinkets_swap_B", controls(TRINKETS[2]), False, False, False),
                            ("special_neck_only", special, True, False, False),
                            ("two_embellishments_special_neck_four_tier", combo, True, True, True)):
                        try:
                            successes[label] = native_case(
                                label, c, selected=sel,
                                expect_four_tier=tier, replay=cache)
                        except Exception as exc:
                            report["cases"][label]["status"] = "FAILED_REAL_CASE"
                            report["cases"][label]["error_code"] = (
                                str(exc)[:260] if re.fullmatch(
                                    r"[A-Z][A-Z0-9_]{3,200}", str(exc))
                                else type(exc).__name__)
                            successes[label] = False
                            checkpoint()
                    report["actual_positive_cases"] = sum(successes.values())
                    report["actual_positive_target_cases"] = len(successes)
                    report["source_only_or_blocked_case_count"] = 8
                    report["status"] = (
                        "PASS_DETERMINISTIC_OPTION_MATRIX_REAL_5X6_DPS"
                        if all(successes.values())
                        else "PARTIAL_OPTION_MATRIX_SEE_INDIVIDUAL_CASES")
                    checkpoint()
                    return 0 if all(successes.values()) else 2
    except Exception as exc:
        report["status"] = "BLOCKED_BEFORE_MATRIX_COMPLETE"
        report["failure_kind"] = type(exc).__name__
        report["failure_code"] = (
            str(exc)[:200] if re.fullmatch(r"[A-Z][A-Z0-9_]{3,200}", str(exc))
            else type(exc).__name__)
        checkpoint()
        return 3
    finally:
        print("V525_MATRIX_RESULT " + json.dumps({
            "status": report["status"],
            "actual_positive_cases": report.get("actual_positive_cases", 0),
            "total_native_attempts": report.get("new_native_attempts_total", 0),
            "case_statuses": {k: v.get("status") for k, v in
                             report["cases"].items()},
        }, ensure_ascii=False, sort_keys=True), flush=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--simc", type=pathlib.Path, required=True)
    p.add_argument("--out", type=pathlib.Path, required=True)
    p.add_argument("--v439-cache", type=pathlib.Path, required=True)
    a = p.parse_args()
    raise SystemExit(run(a.simc, a.out, a.v439_cache))


if __name__ == "__main__":
    main()
