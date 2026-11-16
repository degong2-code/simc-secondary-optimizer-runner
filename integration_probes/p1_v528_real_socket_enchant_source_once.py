#!/usr/bin/env python3
"""v528 bounded real current build socket-owner and permanent-enchant probe.

No AI calls, no new effect/optimizer/budget implementation. Uses v113→v216
original source/J owners and v198's real physical SimC JSON2 before/after.
A declared fifth/sixth gem is never treated as a legally-added socket.
An observed enchant E is not automatically admitted to current-season UI.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
import tempfile
import zipfile

from fastapi.testclient import TestClient

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT),str(ROOT/"runner"),
                str(ROOT/"integration_probes")]
import v113_local_web_api as web
import v196_current_season_user_catalog as season_options
import v198_targeted_enchant_native_rating as enchant_probe
import p1_v524_m1_m2_source_owner_once as pinned
import p1_v525_real_option_matrix_once as matrix
from integration_probes import p3_haj_real_local_web_native_e2e as reuse_catalog

SCHEMA="p1_v528_actual_socket_5_6_source_and_three_enchant_pairs_v1"
ENCHANT_IDS=(7967,8025,7965)
SOCKET_TOTALS=(5,6)
MAX_ENCHANT_NATIVE=2*len(ENCHANT_IDS)
MAX_ENV_NATIVE=3

def need(cond,code):
    if not cond:
        raise RuntimeError("V528_"+code)

def digest(path):
    h=hashlib.sha256()
    with pathlib.Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):
            h.update(chunk)
    return h.hexdigest()

def json_write(path,doc):
    path.write_text(json.dumps(doc,ensure_ascii=False,sort_keys=True,
         indent=2,allow_nan=False)+"\n",encoding="utf8")

def stable(exc):
    codes=re.findall(r"[A-Z][A-Z0-9_]{4,120}",str(exc))
    return {"kind":type(exc).__name__,"codes":codes[:8]}

def result_subset(observed,requested):
    compilation=observed.get("source_compilation") or {}
    progress=observed.get("zero_history_build") or {}
    j=(compilation.get("selected_J_intrinsic_socket_origin_unadmitted")
       or progress.get("selected_J_intrinsic_socket_origin_unadmitted") or {})
    arithmetic=(compilation.get("physical_gem_J_arithmetic_unadmitted")
                or progress.get("physical_gem_J_arithmetic_unadmitted") or {})
    source=progress.get("required_core_source_owner_report") or {}
    return {
       "declared_total":requested,
       "environment_ready":observed.get("environment_ready") is True,
       "environment_installed":observed.get("environment_installed") is True,
       "native_calls_reported":observed.get("native_calls"),
       "compilation_status":compilation.get("status"),
       "compilation_missing":compilation.get("missing"),
       "selected_J_status":j.get("status"),
       "game_socket_legal_verified":j.get("game_socket_legal_verified"),
       "J_approved":j.get("J_approved"),
       "original_v232_intrinsic_counts":j.get("intrinsic_socket_counts_by_slot"),
       "additional_socket_proof_required_by_slot":
           j.get("additional_socket_proof_required_by_slot"),
       "v232_receipt_sha256":j.get("v232_stage_receipt_sha256"),
       "unadmitted_J_arithmetic":arithmetic.get("J_candidate_unadmitted"),
       "socket_item_source_status":(
           j.get("socket_item_source_only_for_unverified_additions") or {}).get(
               "status"),
       "socket_spell_source_status":(
           j.get("socket_spell_effect_source_only_for_unverified_additions")
               or {}).get("status"),
       "required_core_owner_missing":
           source.get("original_source_owner_missing_for_selected_request")
    }

def api(client,method,path,payload=None):
    h={"x-simc-local-token":"v528-real-option-token",
       "origin":"http://127.0.0.1:8765"}
    r=client.get(path,headers=h) if method=="GET" else client.post(
        path,headers=h,json=payload if payload is not None else {})
    need(r.status_code==200,
         "HTTP_"+str(r.status_code)+"_"+
          str((r.json().get("detail") or {}).get("code","UNKNOWN"))[:110])
    return r.json()

def run(binary,out):
    binary=pathlib.Path(binary).resolve()
    out=pathlib.Path(out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    receipt=out/"V528_SOURCE_SOCKET_ENCHANT_REAL_RESULT.json"
    data={
       "schema":SCHEMA,"status":"NOT_STARTED",
       "game_build":pinned.BUILD,"target_ilevel":334,
       "simc_revision":pinned.REV,
       "simc_binary_sha256":pinned.EXE_SHA,
       "runtime_AI_calls":0,"runtime_AI_stat_or_effect_logic":False,
       "SimC_is_only_Native_APL_effect_DPS_owner":True,
       "base_environment_native_calls":None,
       "additional_socket_environment_native_calls":0,
       "enchant_native_calls":0,
       "source_socket_cases":{},"enchant_cases":{},
       "additional_socket_game_legality_promoted":False,
       "enchant_UI_admission_promoted":False,
       "new_user_DPS_native_calls":0,
       "full_product_e2e":"PENDING"
    }
    def checkpoint():json_write(receipt,data)
    checkpoint()
    try:
        need(sys.platform=="win32","WINDOWS_ORIGINAL_NATIVE_ONLY")
        need(binary.is_file() and binary.name.lower()=="simc.exe"
             and digest(binary)==pinned.EXE_SHA,
             "OFFICIAL_SIMC_BINARY_SHA_REQUIRED")
        need(pinned.EphemeralActionsCredentials().load() is not None,
             "ORIGINAL_SOURCE_KEYS_MISSING")
        with tempfile.TemporaryDirectory(prefix="v528-real-options-",dir=out) as temp:
            root=pathlib.Path(temp)/"runs"
            root.mkdir()
            jobs=web.LocalJobs(root,source_credential_store=
                pinned.EphemeralActionsCredentials())
            myth=jobs.discover_season_myth_target(pinned.BUILD)
            need(myth.get("status")==
                   "MYTH_TARGET_CANDIDATE_FROM_MATCHED_WAGO_V163_SOURCE"
                 and myth.get("target_ilevel")==334
                 and re.fullmatch(r"[a-f0-9]{64}",
                     myth.get("currency_csv_sha256") or "") is not None,
                 "REAL_M1_SOURCE_NOT_VERIFIED")
            data["M1_currency_source_sha256"]=myth["currency_csv_sha256"]
            need(myth["currency_csv_sha256"]==pinned.V523_CURRENCY_SHA,
                 "CURRENCY_SOURCE_DRIFT_FROM_PRIOR")
            base=jobs.build_season_environment(
                game_build=pinned.BUILD,target_ilevel=334,
                auto_initial_core_build=True,
                auto_initial_core_simc_binary=str(binary),
                simc_revision_hint=pinned.REV,
                existing_special_gem_id=None,
                source_target_socket_count=4,
                auto_myth_target_source_build=pinned.BUILD,
                auto_myth_target_source_sha256=myth["currency_csv_sha256"])
            data["base_environment_native_calls"]=base.get("native_calls")
            need(base.get("environment_ready") is True and
                 base.get("environment_installed") is True and
                 base.get("G")==2850 and base.get("J")==92 and
                 base.get("F")==165 and base.get("B")==3107 and
                 base.get("T")==3107 and sum(base["O"].values())==0 and
                 isinstance(data["base_environment_native_calls"],int) and
                 0<=data["base_environment_native_calls"]<=MAX_ENV_NATIVE,
                 "ORIGINAL_70783_BASE_ENVIRONMENT_REQUIRED")
            original=base["source_compilation"]
            need(original.get("missing")==[] and
                 original["required_core_source_owner_report"][
                   "original_source_owner_missing_for_selected_request"]==[],
                 "M2_SOURCE_OWNER_MISSING")
            data["base_installed_v212_sha256"]=original[
                "verified_environment_install"]["manifest_sha256"]
            checkpoint()

            # An advanced 5/6 declaration must not reuse four-gem J or
            # create a DPS profile unless independent physical J is proved.
            # No G/F Native is requested for source-only diagnostics.
            for sockets in SOCKET_TOTALS:
                label="socket_"+str(sockets)
                entry={"requested_total":sockets,"status":"NOT_RUN",
                       "user_DPS_native_calls":0}
                data["source_socket_cases"][label]=entry;checkpoint()
                try:
                    future=jobs.build_season_environment(
                        game_build=pinned.BUILD,target_ilevel=334,
                        auto_initial_core_build=False,
                        simc_revision_hint=pinned.REV,
                        existing_special_gem_id=None,
                        source_target_socket_count=sockets,
                        auto_myth_target_source_build=pinned.BUILD,
                        auto_myth_target_source_sha256=myth["currency_csv_sha256"])
                    details=result_subset(future,sockets)
                    entry.update(details)
                    n=details["native_calls_reported"]
                    need(n is None or n==0,"SOCKET_DIAGNOSTIC_SPENT_UNREQUESTED_NATIVE")
                    entry["status"]=(
                        "SOURCE_ONLY_PROOF_PENDING"
                        if details["environment_ready"] is False and
                           details["J_approved"] is not True else
                        "UNEXPECTED_SOCKET_CLAIM_REQUIRES_MANUAL_SOURCE_AUDIT")
                except Exception as exc:
                    entry["status"]="SOURCE_STAGE_BLOCKED_NOT_ADMITTED"
                    entry["failure"]=stable(exc)
                checkpoint()

            # Confirm the same exact source catalog and one plain user
            # profile. The v198 comparison is a physical SimC before/after,
            # never auto-approved E or UI.
            source_path=original["source_catalog_path"]
            with reuse_catalog.verified_current_catalog(source_path,pinned.BUILD):
                source_doc,rows,_=season_options.read(source_path)
                app=web.create_app(root=root,token="v528-real-option-token")
                app.state.jobs.remember_verified_fresh_environment(base)
                with TestClient(app,base_url="http://127.0.0.1:8765") as client:
                    controls=matrix.controls(matrix.TRINKETS[0])
                    request={"controls":controls,"binary":str(binary),
                             "revision":pinned.REV,
                             "current_season_product":True,
                             "installed_season_game_build":pinned.BUILD,
                             "installed_manifest_sha256":
                                data["base_installed_v212_sha256"],
                             "user_socket_total":4}
                    planned=api(client,"POST","/api/v1/sessions/plan",request)
                    need(planned.get("status")=="READY_ZERO_NATIVE",
                         "BASE_USER_PROFILE_PLAN_FAILED")
                    source=root/planned["session_id"]/"generated"/"profile.simc"
                    need(source.is_file() and not source.is_symlink(),
                         "PROFILE_SOURCE_MISSING")
                    raw=source.read_text(encoding="utf8")
                    ring=[x for x in raw.splitlines() if x.startswith("finger1=")]
                    need(len(ring)==1 and
                         "source=local" in ring[0] and
                         "id=" in ring[0],
                         "SOURCE_VERIFIED_PHYSICAL_RING_REQUIRED")
                    data["actual_base_profile_sha256"]=digest(source)
                    checkpoint()
                    native_root=out/"v198_original_native_pairs"
                    native_root.mkdir(exist_ok=False)
                    archive=[]
                    for item_id in ENCHANT_IDS:
                        label="enchant_"+str(item_id)
                        row={"enchant_id":item_id,
                             "slot":"finger1",
                             "status":"NOT_RUN","UI_approved":False,
                             "DPS_native_calls":0}
                        data["enchant_cases"][label]=row;checkpoint()
                        source_rows=[r for r in rows
                             if r.get("enchant_id")==item_id]
                        row["source_row_match_count"]=len(source_rows)
                        if len(source_rows)!=1 or (
                              "finger1/finger2" not in
                              source_rows[0].get("source_slots",[])):
                            row["status"]="EXACT_70783_SOURCE_SLOT_NOT_VERIFIED"
                            checkpoint();continue
                        src=source_rows[0]
                        row["source_token"]=src.get("token")
                        row["highest_source_quality_rank"]=src.get(
                            "highest_source_quality_rank")
                        row["source_ui_selectable"]=src.get("ui_selectable")
                        need(src.get("ui_selectable") is False,
                             "SOURCE_CANDIDATE_NOT_APPROVED_BUT_SELECTED")
                        try:
                            native=enchant_probe.run(
                                source,binary,pinned.REV,"finger1",item_id,
                                native_root,iterations=35,max_new=2,timeout=240)
                            added=native["native_new_calls_this_request"]
                            data["enchant_native_calls"]+=added
                            need(added==2 and
                                 data["enchant_native_calls"]<=MAX_ENCHANT_NATIVE,
                                 "ENCHANT_NATIVE_CALLS_OUTSIDE_CAP")
                            row["status"]="PASS_ACTUAL_NATIVE_STATIC_ONLY"
                            row["static_E_observed_one_profile"]=native[
                                  "comparison"]["static_secondary"]
                            row["classification"]=native["comparison"][
                                  "classification"]
                            row["base_input_sha256"]=native[
                                  "base_input_sha256"]
                            row["enchant_input_sha256"]=native[
                                  "enchant_input_sha256"]
                            row["before_JSON2_sha256"]=native[
                                  "before_native_sha256"]
                            row["after_JSON2_sha256"]=native[
                                  "after_native_sha256"]
                            row["exact_before_after_item_identical"]=True
                            folder=native_root/enchant_probe.sha(
                                enchant_probe.canonical(native["identity"]))[:24]
                            for name in ("before.simc","after.simc",
                                         "before.json","after.json","receipt.json"):
                                p=folder/name
                                need(p.is_file(),"ENCHANT_ORIGINAL_NATIVE_EVIDENCE_MISSING")
                                archive.append((p,label+"/"+name))
                        except Exception as exc:
                            row["status"]="ACTUAL_NATIVE_COMPARISON_BLOCKED"
                            row["failure"]=stable(exc)
                        checkpoint()
                    if archive:
                        archive_file=out/"V528_ORIGINAL_V198_ENCHANT_INPUT_JSON2.zip"
                        with zipfile.ZipFile(archive_file,"w",
                            compression=zipfile.ZIP_DEFLATED,
                            compresslevel=6) as z:
                            for path,arcname in archive:
                                z.write(path,arcname)
                        data["native_originals_archive_sha256"]=digest(archive_file)
                        data["native_originals_archive_file"]=archive_file.name
                    # Do not allow a stat delta on one profile to become
                    # a general item/quality/season UI approval.
                    data["status"]=(
                        "PASS_SCOPED_ENCHANT_NATIVE_AND_SOCKET_SOURCE_DIAGNOSTICS"
                        if data["enchant_native_calls"]==MAX_ENCHANT_NATIVE
                           and all(v["status"]=="PASS_ACTUAL_NATIVE_STATIC_ONLY"
                               for v in data["enchant_cases"].values())
                           and all(v["status"]=="SOURCE_ONLY_PROOF_PENDING"
                               for v in data["source_socket_cases"].values())
                        else "PARTIAL_SOURCE_OR_NATIVE_WITH_FAIL_CLOSED")
                    checkpoint()
                    return 0 if data["status"].startswith("PASS_") else 2
    except Exception as exc:
        data["status"]="BLOCKED_BEFORE_ALL_REAL_SOURCE_CASES"
        data["failure"]=stable(exc)
        checkpoint()
        return 3
    finally:
        print("V528_REAL_OPTION_SOURCE "+json.dumps({
            "status":data["status"],
            "sockets":{k:v.get("status") for k,v in
                       data["source_socket_cases"].items()},
            "enchants":{k:v.get("status") for k,v in
                        data["enchant_cases"].items()},
            "base_environment_native":data["base_environment_native_calls"],
            "enchant_native":data["enchant_native_calls"]
        },ensure_ascii=False,sort_keys=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--simc",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    a=p.parse_args()
    sys.exit(run(a.simc,a.out))
