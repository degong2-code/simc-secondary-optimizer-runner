#!/usr/bin/env python3
"""Bounded real SimC v307 finite-grid coverage, NEW product Web user source.

ONE fresh 70783 user environment, same historical approved binary, 4 ordinary
gems, manual final T3400, Destruction Warlock. Uses v113/v216/v212/v098 and
the exact v291/v065 Native JSON2 verifier; never rewrites a SimC effect.
It is a *high-density coverage* experiment, NOT a same-cost winner test.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import tempfile
import time
import zipfile

from fastapi.testclient import TestClient

from runner import v113_local_web_api as web
from runner import v289_retail_live_build_source as retail
from runner import v291_durable_multiscale_native_runner as durable
from runner import v293_local_longrun_session as longrun
from runner import v307_dense_nested_coverage_grid as dense
from integration_probes import p2_new_profile_product_e2e_once as fresh
from integration_probes import p3_haj_real_local_web_native_e2e as web_probe

SCHEMA = "p2_v307_one_actual_dense_coarse_coverage_v1"
CASE = "destruction_warlock_4ordinary_T3400"
OUTPUT = pathlib.Path("out/p2_v307_dense_real_once").resolve()
RECEIPT = OUTPUT / "receipt.json"
PROOF_ZIP = OUTPUT / "top_confirm_native_bytes.zip"
MAX_DPS_NATIVE = 520
MAX_SECS = 720


class NativeStudyBlocked(RuntimeError):
    pass


def need(ok, code):
    if not ok:
        raise NativeStudyBlocked(code)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def save(doc):
    path = RECEIPT.with_suffix(".tmp")
    path.write_text(json.dumps(doc,sort_keys=True,ensure_ascii=False,
                         indent=2,allow_nan=False)+"\n",encoding="utf8")
    path.replace(RECEIPT)


def main():
    need(os.getenv("P2_V307_DENSE_REAL_ONCE")=="1",
         "P2_V307_EXPLICIT_REAL_SIMC_OPT_IN_REQUIRED")
    case,controls=fresh.selected_case(CASE)
    need((case["character_class"],case["character_spec"],
          case["character_race"],case["target_ilevel"],
          case["final_T"],case["sockets"],case["special_gem"])==
         ("warlock","destruction","human",334,3400,4,None),
         "P2_V307_USER_CASE_DRIFT")
    binary=pathlib.Path("out/binary/simc").resolve(strict=True)
    need(digest(binary.read_bytes())==fresh.BINARY_SHA,
         "P2_V307_APPROVED_BINARY_SHA_MISMATCH")
    OUTPUT.mkdir(parents=True,exist_ok=True)
    need(not RECEIPT.exists(),"P2_V307_ONE_SHOT_RECEIPT_REUSE_FORBIDDEN")
    result={
        "schema":SCHEMA,"status":"STARTED",
        "case_id":CASE,"user_choices":case,
        "binary_sha256":fresh.BINARY_SHA,
        "season_build":fresh.BUILD,
        "revision":fresh.REVISION,
        "new_environment_native":0,
        "new_dps_native":0,
        "raw_native_all_520_uploaded":False,
        "previous_dps_imported":False,
        "historical_equipment_copied":False,
        "user_windows_browser_clicked":False,
        "global_optimum_proven":False,
        "familywise_95_proven":False,
        "legacy_v290_default_unchanged":True}
    save(result)
    try:
        live=retail.discover(region="KR")
        result["live_build"]=live["game_build"]
        need(live["game_build"]==fresh.BUILD,
             "CURRENT_BUILD_DIFFERS_FROM_PINNED_SAME_SEASON")
        need(all(os.environ.get(k) for k in (
              "BLIZZARD_CLIENT_ID","BLIZZARD_CLIENT_SECRET",
              "WCL_CLIENT_ID","WCL_CLIENT_SECRET")),
             "P2_V307_SOURCE_CREDENTIALS_MISSING")
        with tempfile.TemporaryDirectory(prefix="p2-v307-real-") as tmp:
            root=pathlib.Path(tmp)
            need(not list(root.iterdir()),"P2_V307_BUILD_WORKSPACE_NOT_EMPTY")
            env=web.LocalJobs(root).build_season_environment(
                game_build=fresh.BUILD,
                target_ilevel=case["target_ilevel"],
                auto_initial_core_build=True,
                auto_initial_core_simc_binary=str(binary),
                simc_revision_hint=fresh.REVISION,
                existing_special_gem_id=None,
                source_target_socket_count=case["sockets"])
            compiled=env.get("source_compilation") or {}
            physical=compiled.get("physical_gem_layout_unadmitted") or {}
            installed=compiled.get("verified_environment_install") or {}
            result["new_environment_native"]=env.get("native_calls",0)
            result["season_budget"]={k:env.get(k)
                                      for k in ("G","J","F","O","B","T")}
            result["installed_manifest_sha256"]=installed.get(
                "manifest_sha256")
            need(env.get("environment_ready") is True and
                 env.get("environment_installed") is True and
                 0<=result["new_environment_native"]<=3 and
                 installed.get("status")==
                    "FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY",
                 "P2_V307_FRESH_GJFO_INSTALL_FAILED")
            need(physical.get("socket_total")==4 and
                 physical.get("special_gem_id") is None and
                 len(physical.get("ordinary_gem_ids") or [])==4 and
                 len(set(physical["ordinary_gem_ids"]))==4,
                 "P2_V307_PHYSICAL_ORDINARY_FOUR_GEM_DRIFT")
            need(env["B"]==env["G"]+env["J"]+env["F"] and
                 env["T"]==env["B"] and
                 sum(env["O"].values())==0,
                 "P2_V307_G_J_F_O_B_T_DRIFT")
            save(result)
            with web_probe.verified_current_catalog(
                    compiled["source_catalog_path"],fresh.BUILD):
                app=web.create_app(root=root,token="v307-private-local-token")
                app.state.jobs.remember_verified_fresh_environment(env)
                controls["oil_hands"]=[]
                payload={
                    "controls":controls,"binary":str(binary),
                    "revision":fresh.REVISION,
                    "current_season_product":True,
                    "max_native_calls":12,
                    "max_new_native_this_invocation":1,
                    "max_elapsed_seconds":360}
                with TestClient(app,base_url="http://127.0.0.1:8765") as client:
                    headers={"x-simc-local-token":"v307-private-local-token",
                             "origin":"http://127.0.0.1:8765"}
                    response=client.post("/api/v1/longrun/prepare",
                                         headers=headers,json=payload)
                    if response.status_code!=200:
                        try:
                            detail=response.json().get("detail",{})
                            reason=detail.get("code") if isinstance(
                                detail,dict) else detail
                        except (TypeError,ValueError):
                            reason="UNKNOWN_HTTP_DETAIL"
                        raise NativeStudyBlocked(
                            "P2_V307_WEB_PREPARE_HTTP_%d_%s"%
                            (response.status_code,str(reason)[:100]))
                    prepared=response.json()
                    need(prepared["status"]==
                         "LONGRUN_SOURCE_PREPARED_NO_DPS_NATIVE",
                         "P2_V307_WEB_PREPARE_NOT_ZERO_DPS_NATIVE")
                    session=prepared["session_id"]
                    check=client.get("/api/v1/sessions/%s/inputs"%session,
                                     headers=headers)
                    need(check.status_code==200,
                         "P2_V307_SOURCE_INPUTS_NOT_RETRIEVABLE")
                    choices=check.json()["user"]
                    character=choices["character"]
                    need((character["class"],character["spec"],
                          character["race"])==("warlock","destruction","human")
                         and choices["target"]["final_T"]==3400,
                         "P2_V307_ACTUAL_USER_CHOICE_DRIFT")
                    need(prepared["environment_manifest"][
                         "fresh_v212_installed_manifest_sha256"]==
                         result["installed_manifest_sha256"],
                         "P2_V307_INSTALLED_MANIFEST_SHA_DRIFT")
                    staged=longrun.prepare(root/session,MAX_DPS_NATIVE)
                    context,flask=staged["context"],staged["flask"]
                    ident=context["identity"]
                    normalized=context["bundle"]["prepared"]["scenario"]
                    B,lower,upper=durable.constraints.bounds(
                        normalized,durable.adaptive.feasible_budget(
                            context,flask))
                    need(B==case["final_T"] and
                         ident["approved_final_T"]==B and
                         sum(ident["oil_vector"].values())==0 and
                         ident["revision"]==fresh.REVISION and
                         ident["binary_sha256"]==fresh.BINARY_SHA,
                         "P2_V307_MANUAL_T_EXACT_PROFILE_DRIFT")
                    expected_coarse=len(dense.lattice(
                        B,tuple(lower),tuple(upper),6))
                    need(0<expected_coarse<
                         MAX_DPS_NATIVE-dense.budget(
                             MAX_DPS_NATIVE)["confirmation_calls"],
                         "P2_V307_COARSE_SCAN_NOT_BUDGET_FEASIBLE")
                    result.update(
                        source_profile_sha256=ident["source_profile_sha256"],
                        source_scenario_sha256=ident["scenario_digest"],
                        product_v113_v216_v212_v098_TestClient=True,
                        base_B=B,final_T=ident["approved_final_T"],
                        fixed_O=ident["oil_vector"],
                        stat_lower=list(lower),stat_upper=list(upper),
                        scout_iterations=ident["scout_iterations"],
                        confirmation_iterations=ident["confirm_iterations"],
                        full_coarse_feasible_targets=expected_coarse,
                        total_native_budget=MAX_DPS_NATIVE,
                        dense_max_level=11)
                    save(result)
                    start=time.perf_counter()
                    output=staged["paths"]["output_dir"]
                    native=durable.run(
                        context,flask,binary,output,
                        max_native_calls=MAX_DPS_NATIVE,
                        max_new_native_this_invocation=MAX_DPS_NATIVE,
                        max_elapsed_seconds=MAX_SECS,
                        dense_nested_grid_max_level=11,
                        open_folder=False)
                    elapsed=time.perf_counter()-start
                    result["native_runner_status"]=native["status"]
                    result["new_dps_native"]=native["new_native_this_invocation"]
                    result["native_elapsed_seconds"]=round(elapsed,3)
                    result["coverage"]=native["dense_grid_coverage"]
                    result["selected_pair_95"]=native[
                        "confirmed_selected_pair_95"]
                    need(native["status"]=="BUDGET_EXHAUSTED"
                         and native["completed_cases"]==MAX_DPS_NATIVE
                         and result["new_dps_native"]==MAX_DPS_NATIVE
                         and result["coverage"]["levels"]["6"][
                             "complete_at_this_resolution"] is True
                         and result["coverage"]["levels"]["6"][
                             "observed_targets"]==expected_coarse,
                         "P2_V307_NATIVE_FULL_COARSE_GRID_NOT_COMPLETE")
                    rows=durable._load_journal(output/"V291_JOURNAL.jsonl")
                    need(len(rows)==MAX_DPS_NATIVE,
                         "P2_V307_NATIVE_JOURNAL_COUNT_DRIFT")
                    require={
                        "scout":ident["scout_iterations"],
                        "precision":ident["confirm_iterations"]}
                    need(all(row["iterations"]==require[row["phase"]]
                             and sum(row["final_T"].values())==B and
                             sum(row["target"].values())==B and
                             row["source"]=="NEW_NATIVE"
                             for row in rows),
                         "P2_V307_ACCEPTED_NATIVE_TOTAL_OR_ITERS_DRIFT")
                    summary={
                        "global_grid_6_native":sum(
                            row["grid_stage"]=="global_grid" and
                            row["grid_level"]==6 for row in rows),
                        "global_grid_11_native":sum(
                            row["grid_stage"]=="global_grid" and
                            row["grid_level"]==11 for row in rows),
                        "regional_dense_native":sum(
                            row["grid_stage"]=="regional_dense" for row in rows),
                        "confirmed_native":sum(
                            row["grid_stage"]=="measured_confirm" for row in rows)}
                    result["stage_counts"]=summary
                    confirmed=sorted(
                        [row for row in rows if row["phase"]=="precision"],
                        key=lambda row:(-row["dps_mean"],row["case_key"]))
                    need(len(confirmed)>=2,
                         "P2_V307_NO_TWO_ACTUAL_CONFIRMED_CHOICES")
                    result["top_three_confirmed"]=[{
                        "index":row["index"],"target":row["target"],
                        "dps_mean":row["dps_mean"],"dps_sem":row["dps_sem"],
                        "iterations":row["iterations"],
                        "case_key":row["case_key"],
                        "native_json_sha256":row["native_sha256"],
                        "input_sha256":row["input_sha256"],
                        "simc_seed":row["simc_seed"]}
                        for row in confirmed[:3]]
                    # Preserve the ACTUAL first and second selected SimC
                    # original bytes, not merely synthetic compact records.
                    with zipfile.ZipFile(
                            PROOF_ZIP,"x",zipfile.ZIP_DEFLATED,
                            compresslevel=6) as archive:
                        total_size=0
                        for r in confirmed[:2]:
                            casefolder=durable.case_folder(
                                output,r["index"])
                            for name in ("input.simc","result.json",
                                         "native_receipt.json"):
                                item=casefolder/name
                                need(item.is_file() and item.stat().st_size
                                     <12_000_000,
                                     "P2_V307_NATIVE_PROOF_CASE_MISSING")
                                total_size+=item.stat().st_size
                                need(total_size<=25_000_000,
                                     "P2_V307_PROOF_ARCHIVE_TOO_LARGE")
                                archive.write(item,
                                    "case_%05d/%s"%(r["index"],name))
                    result["two_selected_raw_json2_proof_zip_sha256"] = digest(
                        PROOF_ZIP.read_bytes())
                    # Cache-only replay re-authenticates every ORIGINAL native
                    # case and must not execute a single new SimC process.
                    replay=durable.run(
                        context,flask,binary,output,
                        max_native_calls=MAX_DPS_NATIVE,
                        max_new_native_this_invocation=0,
                        cache_only=True,
                        dense_nested_grid_max_level=11,
                        open_folder=False)
                    need(replay["new_native_this_invocation"]==0
                         and replay["completed_cases"]==MAX_DPS_NATIVE
                         and replay["dense_grid_coverage"]==result["coverage"],
                         "P2_V307_CACHE_ONLY_REVALIDATION_NOT_EXACT")
                    result["cache_only_replay_new_native"]=0
                    result["status"]="PASS_REAL_PRODUCT_FULL_LEVEL6_GRID"
                    save(result)
                    print("P2_V307_REAL_DENSE_GRID_PASS",
                          json.dumps({k:result[k] for k in (
                              "status","case_id","new_environment_native",
                              "new_dps_native","native_elapsed_seconds",
                              "source_profile_sha256","stage_counts",
                              "top_three_confirmed","coverage")},
                                     sort_keys=True,ensure_ascii=False),
                          flush=True)
        return result
    except BaseException as exc:
        result["status"]="BLOCKED_OR_PARTIAL_"+type(exc).__name__
        message=str(exc)
        result["first_stable_error_code"]=(
            message if re.fullmatch(r"[A-Z][A-Z0-9_]{3,100}",message)
            else type(exc).__name__)
        save(result)
        raise


if __name__=="__main__":
    main()
