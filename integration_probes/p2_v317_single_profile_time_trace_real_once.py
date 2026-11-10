#!/usr/bin/env python3
"""One fresh Arms Warrior product scenario for REAL v316 per-case Native trace.

Only measures existing v290/v291. No algorithm promotion, no historical DPS
profile import, no fixed 10-minute runtime requirement. Fails closed on source
and binary drift. Real user Windows clicking is NOT tested.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import time
import zipfile

from fastapi.testclient import TestClient

from runner import v113_local_web_api as web
from runner import v289_retail_live_build_source as retail
from runner import v291_durable_multiscale_native_runner as durable
from runner import v293_local_longrun_session as longrun
from runner import v316_optin_case_time_trace as trace
from integration_probes import p2_new_profile_product_e2e_once as fresh
from integration_probes import p3_haj_real_local_web_native_e2e as web_probe

ROOT = pathlib.Path("out/p2_v317_single_real_trace").resolve()
RECEIPT = ROOT / "receipt.json"
RAW = ROOT / "original_native_and_timing.zip"
CASE = "arms_warrior_4ordinary_T3250"
NATIVE_CAP = 12
ITER_SCOUT = 35
ITER_CONFIRM = 320


class V317Blocked(RuntimeError):
    pass


def need(ok, code):
    if not ok:
        raise V317Blocked(code)


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def save(doc):
    ROOT.mkdir(parents=True, exist_ok=True)
    temp = RECEIPT.with_suffix(".tmp")
    temp.write_text(json.dumps(
        doc, sort_keys=True, ensure_ascii=False, indent=2,
        allow_nan=False) + "\n", encoding="utf8")
    temp.replace(RECEIPT)


def main():
    need(os.getenv("P2_V317_SINGLE_TRACE_ONCE") == "1",
         "V317_EXPLICIT_ONE_SHOT_REAL_NATIVE_REQUIRED")
    case, controls = fresh.selected_case(CASE)
    controls["max_single_stat_percent"] = 60
    controls["oil_hands"] = []
    need((case["character_class"],case["character_spec"]) ==
         ("warrior","arms") and case["final_T"] == 3250 and
         case["special_gem"] is None and case["sockets"] == 4,
         "V317_FRESH_SCENARIO_CONTRACT_DRIFT")
    need(not ROOT.exists(), "V317_ONE_SHOT_OUTPUT_ALREADY_PRESENT")
    doc = {
        "schema":"p2_v317_fresh_one_case_real_v316_timing_v1",
        "status":"STARTED", "case":CASE,
        "source_build":fresh.BUILD, "simc_revision":fresh.REVISION,
        "binary_sha256":fresh.BINARY_SHA,
        "target_final_T":case["final_T"],
        "native_cap":NATIVE_CAP, "scout_iterations":ITER_SCOUT,
        "confirm_iterations":ITER_CONFIRM,
        "case_timing_trace":True, "product_default_v290_changed":False,
        "no_prior_profile_or_dps_cache_import":True,
        "time_600_seconds_not_hard_rejection":True,
        "windows_user_click_tested":False, "global_optimum_proven":False,
    }
    save(doc)
    try:
        binary = pathlib.Path("out/binary/simc").resolve(strict=True)
        need(sha(binary) == fresh.BINARY_SHA,
             "V317_PINNED_SIMC_BINARY_DRIFT")
        live = retail.discover(region="KR")
        need(live["game_build"] == fresh.BUILD,
             "V317_LIVE_GAME_BUILD_MISMATCH")
        need(all(os.getenv(k) for k in (
             "BLIZZARD_CLIENT_ID","BLIZZARD_CLIENT_SECRET",
             "WCL_CLIENT_ID","WCL_CLIENT_SECRET")),
             "V317_VERIFIED_SEASON_SOURCE_CREDENTIALS_REQUIRED")
        workspace = ROOT / "new_user_workspace"
        workspace.mkdir()
        env = web.LocalJobs(workspace).build_season_environment(
            game_build=fresh.BUILD,
            target_ilevel=case["target_ilevel"],
            auto_initial_core_build=True,
            auto_initial_core_simc_binary=str(binary),
            simc_revision_hint=fresh.REVISION,
            existing_special_gem_id=None,
            source_target_socket_count=case["sockets"])
        source = env.get("source_compilation") or {}
        installed = source.get("verified_environment_install") or {}
        layout = source.get("physical_gem_layout_unadmitted") or {}
        doc["environment_native_calls"] = env.get("native_calls")
        doc["environment_budget"] = {k:env.get(k)
                                     for k in ("G","J","F","O","B","T")}
        doc["installed_manifest_sha256"] = installed.get("manifest_sha256")
        save(doc)
        need(env.get("environment_ready") is True and
             env.get("environment_installed") is True and
             installed.get("status") ==
                 "FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY" and
             type(doc["environment_native_calls"]) is int and
             0 <= doc["environment_native_calls"] <= 3 and
             layout.get("special_gem_id") is None and
             layout.get("socket_total") == 4 and
             len(set(layout.get("ordinary_gem_ids") or [])) == 4 and
             env["B"] == env["G"] + env["J"] + env["F"] and
             env["T"] == env["B"] and sum(env["O"].values()) == 0,
             "V317_FRESH_GJFO_OR_GEM_SOURCE_NOT_VERIFIED")
        with web_probe.verified_current_catalog(
                source["source_catalog_path"],fresh.BUILD):
            app = web.create_app(root=workspace,token="v317-case-only")
            app.state.jobs.remember_verified_fresh_environment(env)
            payload = {
                "controls":controls, "binary":str(binary),
                "revision":fresh.REVISION,"current_season_product":True,
                "max_native_calls":NATIVE_CAP,
                "max_new_native_this_invocation":NATIVE_CAP,
                "max_elapsed_seconds":1800}
            with TestClient(app,base_url="http://127.0.0.1:8765") as client:
                headers={"x-simc-local-token":"v317-case-only",
                         "origin":"http://127.0.0.1:8765"}
                response = client.post("/api/v1/longrun/prepare",
                                       headers=headers,json=payload)
                if response.status_code != 200:
                    raise V317Blocked("V317_USER_PREPARE_HTTP_"+str(
                        response.status_code)+"_"+str(response.json().get(
                        "detail", "NO_DETAIL"))[:140])
                prepared = response.json()
                need(prepared.get("status") ==
                     "LONGRUN_SOURCE_PREPARED_NO_DPS_NATIVE",
                     "V317_NO_DPS_NATIVE_BEFORE_PREPARE")
                session = workspace / prepared["session_id"]
                result = client.get(
                    f"/api/v1/sessions/{prepared['session_id']}/inputs",
                    headers=headers)
                need(result.status_code == 200 and
                     result.json()["user"]["target"]["final_T"] ==
                     case["final_T"], "V317_MANUAL_T_NOT_PRESERVED")
                manifest = longrun.source_manifest(session)
                base = longrun.entry.source(manifest)
                staged,_ = durable.stage_extended_manifest(
                    base, manifest, NATIVE_CAP,
                    source_loader=longrun.entry.source)
                context,flask = staged["context"],staged["flask"]
                ident = context["identity"]
                need(ident["approved_final_T"] == case["final_T"] and
                     ident["scout_iterations"] == ITER_SCOUT and
                     ident["confirm_iterations"] == ITER_CONFIRM and
                     ident["binary_sha256"] == fresh.BINARY_SHA and
                     ident["revision"] == fresh.REVISION and
                     sum(ident["oil_vector"].values()) == 0 and
                     len(ident["source_profile_sha256"]) == 64,
                     "V317_EXACT_NATIVE_SCENARIO_IDENTITY_DRIFT")
                doc["source_profile_sha256"] = ident["source_profile_sha256"]
                doc["scenario_digest"] = ident["scenario_digest"]
                doc["prepared_user_profile_newly_generated"] = True
                save(doc)
                output = ROOT / "v291_real_source_cases"
                started = time.monotonic()
                measured = durable.run(
                    context,flask,binary,output,
                    max_native_calls=NATIVE_CAP,
                    max_new_native_this_invocation=NATIVE_CAP,
                    max_elapsed_seconds=1800,
                    case_timing_trace=True,
                    model_guided_multiregion=False,
                    open_folder=False)
                doc["optimizer_invocation_seconds"] = round(
                    time.monotonic()-started,6)
                journal = durable._load_journal(
                    output / "V291_JOURNAL.jsonl")
                timing = trace.load(
                    output / trace.NAME, journal,
                    trace.identity_hash(output/"V291_SESSION.json"))
                summ = trace.summary(timing,journal)
                cks = trace.checkpoints(timing,journal,ITER_CONFIRM)
                doc["optimizer_status"] = measured["status"]
                doc["original_native_case_count"] = len(journal)
                doc["actual_iterations"] = sum(
                    r["iterations"] for r in journal if r["source"] ==
                    "NEW_NATIVE")
                doc["precision_case_count"] = sum(
                    r["phase"] == "precision" and
                    r["iterations"] == ITER_CONFIRM for r in journal)
                doc["v316_timing_summary"] = summ
                doc["v316_confirmed_checkpoints"] = cks
                doc["v291_journal_sha256"] = sha(
                    output/"V291_JOURNAL.jsonl")
                doc["v316_trace_sha256"] = sha(output/trace.NAME)
                need(summ["new_native_traced"] == len(journal) ==
                     measured["new_native_this_invocation"] and
                     len(timing) == len(journal) and
                     summ["complete_original_journal_trace"] and
                     cks["exact_5_10_minute_result_available"],
                     "V317_REAL_CASE_TRACE_INTEGRITY_OR_CHECKPOINT_GAP")
                original_trace = (output/trace.NAME).read_bytes()
                cached = durable.run(
                    context,flask,binary,output,
                    max_native_calls=NATIVE_CAP,
                    max_new_native_this_invocation=0,
                    cache_only=True, case_timing_trace=True,
                    model_guided_multiregion=False, open_folder=False)
                need(cached["new_native_this_invocation"] == 0 and
                     (output/trace.NAME).read_bytes() == original_trace,
                     "V317_ZERO_NEW_NATIVE_CACHE_ONLY_TRACE_REPLAY")
                doc["cache_only_zero_new_native"] = True
                doc["status"] = ("PASS_REAL_NATIVE_TIMING_AND_CONFIRMED"
                    if doc["precision_case_count"] >= 1
                    else "PARTIAL_NATIVE_TIMING_NO_CONFIRMED_CANDIDATE")
                save(doc)
                with zipfile.ZipFile(RAW,"w",
                                     compression=zipfile.ZIP_DEFLATED,
                                     compresslevel=5) as archive:
                    for path in sorted(output.rglob("*")):
                        if path.is_file() and not path.is_symlink():
                            archive.write(
                                path,arcname=path.relative_to(output))
                doc["raw_native_zip_sha256"] = sha(RAW)
                save(doc)
                print("P2_V317_SINGLE_REAL_V316_TRACE",json.dumps({
                    "status":doc["status"],
                    "source_profile_sha256":doc["source_profile_sha256"],
                    "new_native":len(journal),
                    "iterations":doc["actual_iterations"],
                    "precision":doc["precision_case_count"],
                    "wall_seconds":doc["optimizer_invocation_seconds"],
                    "checkpoint_status":cks["status"],
                    "cache_replay_new_native":cached["new_native_this_invocation"],
                    "raw_zip_sha256":doc["raw_native_zip_sha256"]},
                    sort_keys=True),flush=True)
                return doc
    except BaseException as exc:
        doc["status"] = "BLOCKED_OR_PARTIAL_" + type(exc).__name__
        value = str(exc)
        doc["first_error_code"] = (value if re.fullmatch(
            r"[A-Z][A-Z0-9_]{3,160}",value) else type(exc).__name__)
        save(doc)
        raise


if __name__ == "__main__":
    main()
