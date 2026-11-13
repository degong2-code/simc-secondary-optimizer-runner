#!/usr/bin/env python3
"""v439 bounded real 70783 selected 4pc E2E, Windows-only, exact 1 actor.

One hunter/survival ilvl334 crafted MAIL head replaces the head tier, chest
restores 4pc. Reuse v343's verified original v212 install and v058/v046
static JSON2; no 26-spec rerun, no generic static refresh, no new solver.
Never claim selected equipment correctness unless real source + six DPS
JSON2 and exact cache-only replay are observed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import zipfile

from fastapi.testclient import TestClient

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner"),str(ROOT/"integration_probes")]
import v046_static_item_cache as static
import v058_lazy_crafted_native as native_item
import v098_target_user_scenario_bootstrap as bootstrap
import v113_local_web_api as web
import v218_v098_profile_stage_adapter as profile_stage
from integration_probes import p1_v343_windows_70783_real_native_once as v343
from integration_probes import p3_haj_real_local_web_native_e2e as web_native

SCHEMA="p1_v439_b8_one_70783_selected_4pc_e2e_v1"
# Source: v057 crafted mail head catalogue; SimC de11f57 MID2
# Devourer sample uses embellishment=arcanoweave_lining, crafted_stats=32/36.
CRAFTED_MAIL_HEAD_ID=244579
CRAFTED_OPTIONS={"crafted_stats":"32/36",
                 "embellishment":"arcanoweave_lining"}
MAX_ENVIRONMENT_NATIVE=3
MAX_MISSING_STATIC_NATIVE=4
MAX_DPS_NATIVE=6
MAX_TOTAL_NATIVE=MAX_ENVIRONMENT_NATIVE+MAX_MISSING_STATIC_NATIVE+MAX_DPS_NATIVE
STATS=("crit_rating","haste_rating","mastery_rating","versatility_rating")

def need(ok,why):
    if not ok:
        raise RuntimeError("V439_"+why)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def sha(path):
    return digest(pathlib.Path(path).read_bytes())

def save(path,payload):
    path.write_text(json.dumps(payload,sort_keys=True,indent=2,
                               ensure_ascii=False,allow_nan=False)+"\n",
                    encoding="utf8")

def stats_source(ident,output):
    # Existing v058 source-only Native serializer; no fresh mechanism.
    request={"item_id":ident["item_id"],"slot":ident["slot"],
             "ilevel":ident["ilevel"],"options":ident["options"],
             "compatible_profile":{"class":"hunter","spec":"marksmanship",
                                   "role":"attack"}}
    native_item.validate_request(request)
    text=native_item.native_source(request,output)
    need("iterations=1" in text and "actions=wait,sec=1" in text,
         "STATIC_QUERY_NOT_SINGLE_ITERATION")
    need("json2="+str(output.resolve()) in text,"STATIC_JSON2_PATH_DRIFT")
    return text

def checked_change_scope(pre):
    need(pre.get("status")==
         "B8_SELECTED_PROFILE_STATIC_VARIANTS_PENDING_NO_NATIVE",
         "PRE_STATIC_SOURCE_NOT_PENDING_EXACT_VARIANTS")
    budget=pre["budget_preflight"]
    changed=budget["changed_physical_slots"]
    need(set(x["slot"] for x in changed)=={"head","chest"} and
         len(changed)==2 and
         budget["four_tier_slots"]==
              ["chest","hands","legs","shoulders"] and
         budget["crafted_first_split_is_not_L"] is True,
         "SOURCE_SELECTED_HEAD_CHEST_FOUR_TIER_NOT_RESTORED")
    selected=next(x for x in changed if x["slot"]=="head")
    need(selected["selected_id"]==CRAFTED_MAIL_HEAD_ID,
         "SOURCE_CRAFTED_HEAD_ID_CHANGED")
    missing=budget["missing_exact_native_variants"]
    need(type(missing) is list and 1<=len(missing)<=MAX_MISSING_STATIC_NATIVE
         and all(row["slot"] in ("head","chest") and
                 row["identity"]["season"]==static.SEASON and
                 row["identity"]["ilevel"]==334 and
                 type(row["identity"]["options"]) is dict
                 for row in missing),
         "EXACT_STATIC_MISSING_OUTSIDE_CHANGED_TWO_SLOTS")
    ids=[static.digest(row["identity"]) for row in missing]
    need(len(ids)==len(set(ids)),"DUPLICATE_MISSING_STATIC_IDENTITIES")
    return missing

def collect_missing(*,binary,work,cache,missing,report,checkpoint):
    variants=[]
    for index,row in enumerate(missing):
        ident=row["identity"]
        folder=work/("static_%02d"%(index+1))
        folder.mkdir(exist_ok=False)
        result=folder/"result.json"
        source=folder/"query.simc"
        source.write_text(stats_source(ident,result),encoding="utf8")
        # One call per truly missing physical variant. No whole-gear rescans.
        report["static_native_attempts"]+=1
        checkpoint()
        try:
            done=subprocess.run([str(binary),str(source)],
                cwd=binary.parent,stdin=subprocess.DEVNULL,
                capture_output=True,timeout=60)
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("V439_STATIC_NATIVE_TIMEOUT") from exc
        (folder/"stdout.txt").write_bytes(done.stdout)
        (folder/"stderr.txt").write_bytes(done.stderr)
        need(done.returncode==0 and result.is_file(),
             "STATIC_NATIVE_NONZERO_EXIT_OR_JSON2_MISSING_%02d"%(index+1))
        raw=result.read_bytes()
        rows=static.native_records(raw,artifact_id=
                                   "V439_70783_B8_EXACT_TWO_CHANGED_SLOTS")
        exact=[v for v in rows if v["identity"]==ident]
        need(len(exact)==1 and exact[0]["metadata"]["native_revision"].startswith(
                v343.REVISION[:7]),
             "STATIC_NATIVE_JSON2_REVISION_OR_VARIANT_NOT_EXACT_%02d"%(index+1))
        variants.append(exact[0])
        report["static_proofs"].append({
            "slot":row["slot"],"item_id":ident["item_id"],
            "ilevel":ident["ilevel"],"options":ident["options"],
            "json2_sha256":digest(raw),
            "static_secondary":exact[0]["static"]["secondary"],
            "source_input_sha256":sha(source)})
        checkpoint()
    merged=static.merge_native(cache,variants)
    need(merged["added_variants"]==len(variants),
         "STATIC_CACHE_NOT_EXACT_APPEND_ONLY")
    dest=work/"selected_v046_snapshot.json"
    static.write_atomic(dest,cache)
    need(static.load(dest)==cache,"STATIC_SNAPSHOT_AFTER_MERGE_DRIFT")
    report["selected_static_cache_sha256"]=sha(dest)
    return dest

def response(client,kind,url,body=None):
    headers={"x-simc-local-token":"v439-one-test-token",
             "origin":"http://127.0.0.1:8765"}
    res=(client.get(url,headers=headers) if kind=="GET"
         else client.post(url,headers=headers,json=body or {}))
    if res.status_code!=200:
        body=res.json()
        detail=body.get("detail",{})
        code=detail.get("code","UNKNOWN") if type(detail) is dict else "UNKNOWN"
        raise RuntimeError("V439_HTTP_"+kind+"_"+url.replace("/","_")+
                           "_"+str(res.status_code)+"_"+str(code))
    return res.json()

def run(binary,out):
    need(sys.platform=="win32","ACTUAL_WINDOWS_PLATFORM_REQUIRED")
    binary=pathlib.Path(binary).resolve(strict=True)
    out=pathlib.Path(out).resolve()
    need(binary.name.lower()=="simc.exe" and
         sha(binary)==v343.EXE_SHA,
         "PINNED_70783_WINDOWS_BINARY_SHA_REQUIRED")
    need(os.environ.get("SIMC_PINNED_SOURCE_COMMIT")==v343.REVISION and
         os.environ.get("SIMC_PINNED_GAME_BUILD")==v343.BUILD,
         "EXACT_PINNED_70783_SOURCE_REQUIRED")
    for secret in ("BLIZZARD_CLIENT_ID","BLIZZARD_CLIENT_SECRET",
                   "WCL_CLIENT_ID","WCL_CLIENT_SECRET"):
        need(bool(os.environ.get(secret)),"SEASON_SOURCE_CREDS_MISSING")
    out.mkdir(parents=True,exist_ok=True)
    receipt_file=out/"V439_ONE_SELECTED_70783_B8_RECEIPT.json"
    receipt={
        "schema":SCHEMA,"status":"STARTED_SOURCE_B8_NOT_NATIVE_PROVEN",
        "game_build":v343.BUILD,"simc_revision":v343.REVISION,
        "binary_sha256":v343.EXE_SHA,
        "spec":"hunter/survival","ilevel":334,
        "selected_crafted_head_id":CRAFTED_MAIL_HEAD_ID,
        "selected_crafted_options":CRAFTED_OPTIONS,
        "environment_native_attempts":0,
        "static_native_attempts":0,"dps_native_attempts":0,
        "max_native_attempts_total":MAX_TOTAL_NATIVE,
        "static_proofs":[],"global_optimum_proven":False,
        "confidence_level_for_display":0.95,
        "source_only_until_native_json2":True}
    def checkpoint():
        receipt["total_attempts_recorded"]=(
            receipt["environment_native_attempts"]+
            receipt["static_native_attempts"]+
            receipt["dps_native_attempts"])
        save(receipt_file,receipt)
    checkpoint()
    try:
        live=v343.retail.discover(region="KR")
        receipt["live_observed_build"]=live["game_build"]
        need(live["game_build"]==v343.BUILD,
             "LIVE_KR_BUILD_NOT_70783_STOP_BEFORE_NATIVE")
        with tempfile.TemporaryDirectory(prefix="v439-one-selected-",
                                         dir=out) as tmp:
            root=pathlib.Path(tmp)/"runs"
            root.mkdir()
            owner=web.LocalJobs(root)
            # Reuse the original v343 exact one-spec G/J/F/O environment
            # build, never run an all-26 Native or hidden full item sweep.
            environment=owner.build_season_environment(
                game_build=v343.BUILD,target_ilevel=334,
                auto_initial_core_build=True,
                auto_initial_core_simc_binary=str(binary),
                simc_revision_hint=v343.REVISION,
                existing_special_gem_id=None,
                source_target_socket_count=4)
            receipt["environment_native_attempts"]=environment.get(
                "native_calls",MAX_ENVIRONMENT_NATIVE)
            need(type(receipt["environment_native_attempts"]) is int and
                 0<=receipt["environment_native_attempts"]<=
                     MAX_ENVIRONMENT_NATIVE and
                 environment.get("environment_installed") is True and
                 environment["B"]==3107 and environment["J"]==92 and
                 environment["F"]==165 and
                 sum(environment["O"].values())==0,
                 "SAME_SEASON_V343_334_GJFO_OR_NATIVE_LIMIT_DRIFT")
            receipt["original_installed_manifest_sha256"]=environment[
                "source_compilation"]["verified_environment_install"][
                    "manifest_sha256"]
            checkpoint()
            user_controls=web.sessions.standard_controls(
                ("hunter","survival"))
            user_controls["race"]="human"
            user_controls["oil_hands"]=[]
            user_controls["embellishments"]=[{
                "slot":"head","item_id":CRAFTED_MAIL_HEAD_ID,
                "options":dict(CRAFTED_OPTIONS)}]
            user=web.sessions.user_scenario(user_controls)
            raw_source=environment["source_compilation"]["source_catalog_path"]
            with web_native.verified_current_catalog(
                    raw_source,v343.BUILD):
                app=web.create_app(root=root,token="v439-one-test-token")
                app.state.jobs.remember_verified_fresh_environment(environment)
                stage_controls=profile_stage._verified_fresh_season_consumables(
                    user)
                native_cache=static.empty_cache()
                seed=root/"v439_start_empty_static_cache.json"
                static.write_atomic(seed,native_cache)
                first=bootstrap.preview_from_environment_build(
                    user,root/"no_session_written",binary,v343.REVISION,
                    environment_result=environment,
                    season_controls=stage_controls,
                    selected_static_cache_path=seed)
                missing=checked_change_scope(first)
                receipt["missing_changed_slots_only"]=[
                    {"slot":r["slot"],"item_id":r["item_id"],
                     "identity_sha256":static.digest(r["identity"])}
                    for r in missing]
                checkpoint()
                selected_cache=collect_missing(
                    binary=binary,work=out,cache=native_cache,
                    missing=missing,report=receipt,
                    checkpoint=checkpoint)
                # Require the source-owned v432 G rebase and complete v434
                # profile again, with the exact v046 snapshot.
                validated=bootstrap.preview_from_environment_build(
                    user,root/"no_session_written",binary,v343.REVISION,
                    environment_result=environment,
                    season_controls=stage_controls,
                    selected_static_cache_path=selected_cache)
                need(validated["status"]==
                     "B8_SELECTED_V096_COMPLETE_PROFILE_BUDGET_NOT_ADMITTED"
                     and validated["budget_preflight"][
                         "missing_exact_native_variants"]==[]
                     and validated["budget_preflight"]["four_tier_slots"]==
                         ["chest","hands","legs","shoulders"]
                     and all(v==0 for v in
                           validated["budget_preflight"][
                               "fixed_L_in_G_once"].values()),
                     "POST_STATIC_B8_4PC_AND_NO_CRAFT_SPLIT_LOCK_INVALID")
                B=validated["budget_preflight"]["base_B"]
                T=validated["budget_preflight"]["final_T"]
                receipt["selected_budget"]={
                    "reference_G_not_all_slots_native_exact":
                        validated["budget_preflight"][
                          "G_projected_reference_not_native_exact"],
                    "delta_changed_exact_native":
                        validated["budget_preflight"][
                          "changed_slots_exact_static_delta"],
                    "J":validated["budget_preflight"]["J"],
                    "F":validated["budget_preflight"]["F"],"B":B,"T":T,
                    "fixed_L":validated["budget_preflight"][
                        "fixed_L_in_G_once"],
                    "four_tier_slots":validated["budget_preflight"][
                        "four_tier_slots"]}
                receipt["selected_final_profile_sha256"]=validated[
                    "source_profile_sha256"]
                checkpoint()
                with TestClient(app,base_url="http://127.0.0.1:8765") as c:
                    params={"controls":user_controls,"binary":str(binary),
                        "revision":v343.REVISION,
                        "current_season_product":True,
                        "installed_season_game_build":v343.BUILD,
                        "static_cache":str(selected_cache)}
                    planned=response(c,"POST","/api/v1/sessions/plan",params)
                    need(planned["status"]=="READY_ZERO_NATIVE"
                         and planned["native_calls"]==0
                         and planned["plan"]["base_B"]==B
                         and planned["plan"]["final_T"]==T,
                         "REAL_WEB_SELECTED_PLAN_B_T_OR_ZERO_NATIVE_DRIFT")
                    sid=planned["session_id"]
                    folder=root/sid
                    manifest=json.loads((folder/"generated"/"manifest.json")
                                        .read_text("utf8"))
                    need(web.bootstrap.entry.SELECTED_FRESH_SEASON_FIELD in
                         manifest and
                         manifest["static_cache_json"]==str(selected_cache),
                         "WEB_B8_SOURCE_REPLAY_MANIFEST_NOT_PRESENT")
                    receipt["session_id"]=sid
                    checkpoint()
                    started=response(c,"POST","/api/v1/sessions/start",params)
                    need(started["status"]=="WORKER_STARTED" and
                         started["session_id"]==sid and
                         started.get("static_L_native_calls_this_start",0)==0,
                         "REAL_START_MUST_USE_IDENTICAL_SOURCE_SEALED_SESSION")
                    proc=app.state.jobs.children[sid]
                    receipt["dps_native_attempts_reserved"]=MAX_DPS_NATIVE
                    checkpoint()
                    need(proc.wait(timeout=660)==0,
                         "SELECTED_SIX_DPS_NATIVE_CHILD_EXIT_NONZERO")
                    finished=response(c,"GET",
                             "/api/v1/sessions/"+sid+"/result")
                    best=finished["user_result"]["observed_first_choice"]
                    need(finished["native_calls_cumulative"]==MAX_DPS_NATIVE
                         and finished["base_B"]==B and
                         finished["final_T"]==T and
                         finished["user_result"]["confidence_level"]==0.95
                         and finished["user_result"][
                             "global_optimum_proven"] is False
                         and sum(best["absolute_rating_T"].values())==T
                         and best["observed_dps_mean"]>0 and
                         best["simc_sem"]>=0,
                         "SELECTED_REAL_DPS_SEM_95_OR_TOTAL_INVALID")
                    receipt["dps_native_attempts"]=finished[
                        "native_calls_cumulative"]
                    receipt["dps_observed"]=best["observed_dps_mean"]
                    receipt["dps_sem"]=best["simc_sem"]
                    receipt["observed_absolute_T"]=best["absolute_rating_T"]
                    receipt["status"]="NATIVE_SIX_DPS_PASS_CACHE_REPLAY_PENDING"
                    checkpoint()
                    replay=response(c,"POST",
                             "/api/v1/sessions/"+sid+"/cache-only",{})
                    need(replay["new_native_execution_permitted"] is False,
                         "CACHE_REPLAY_NEW_NATIVE_NOT_FORBIDDEN")
                    need(app.state.jobs.children[sid].wait(timeout=180)==0,
                         "SELECTED_CACHE_ONLY_REPLAY_EXIT_NONZERO")
                    repeated=response(c,"GET",
                             "/api/v1/sessions/"+sid+"/result")
                    need(repeated["cache_hits_this_run"]==MAX_DPS_NATIVE
                         and repeated["native_calls_cumulative"]==
                             MAX_DPS_NATIVE
                         and repeated["user_result"]==
                             finished["user_result"]
                         and sha(selected_cache)==receipt[
                             "selected_static_cache_sha256"],
                         "SELECTED_NATIVE_CACHE_OR_USER_RESULT_DRIFT")
                    proof=json.loads((folder/"V112_CACHE_REPLAY_RECEIPT.json")
                                     .read_text("utf8"))
                    need(proof["additional_native_calls"]==0 and
                         proof["cache_hits_this_run"]==MAX_DPS_NATIVE and
                         len(proof["native_json2_sha256"])==MAX_DPS_NATIVE,
                         "SELECTED_NATIVE_SIX_JSON2_CACHE_SHA_MISSING")
                    receipt["six_dps_json2_sha256"]=proof[
                        "native_json2_sha256"]
                    # Preserve the actual six input/JSON2/native receipts
                    # rather than just a success flag or claimed hash list.
                    case_root=folder/"generated"/"simc_results"
                    saved={}
                    for name in ("input.simc","result.json",
                                 "native_receipt.json"):
                        files=sorted(case_root.rglob(name))
                        need(len(files)==MAX_DPS_NATIVE,
                             "B8_SIX_ACTUAL_NATIVE_CASE_"+name+"_MISSING")
                        saved[name]=files
                    real_hashes=sorted(sha(p) for p in saved["result.json"])
                    need(real_hashes==sorted(proof[
                            "native_json2_sha256"].values()),
                         "B8_ACTUAL_JSON2_HASHES_DIFFER_FROM_CACHE_RECEIPT")
                    zip_path=out/"V439_B8_SIX_NATIVE_JSON2_EVIDENCE.zip"
                    byte_total=0
                    with zipfile.ZipFile(zip_path,"x",
                                         zipfile.ZIP_DEFLATED,
                                         compresslevel=6) as evidence:
                        for name in sorted(saved):
                            for path in saved[name]:
                                size=path.stat().st_size
                                byte_total+=size
                                need(size<=15_000_000 and
                                     byte_total<=55_000_000,
                                     "B8_EVIDENCE_SIZE_CAP")
                                evidence.write(path,arcname=
                                    path.relative_to(case_root).as_posix())
                    receipt["native_evidence_zip_sha256"]=sha(zip_path)
                    receipt["six_original_case_count"]=MAX_DPS_NATIVE
                    receipt["cache_only_hits"]=MAX_DPS_NATIVE
                    receipt["cache_only_new_native"]=0
                    receipt["status"]=(
                      "PASS_REAL_70783_SELECTED_FOUR_TIER_DPS6_CACHE6")
                    receipt["source_only_until_native_json2"]=False
                    checkpoint()
        return 0
    except Exception as exc:
        receipt["status"]="BLOCKED_OR_FAILED_NOT_PRODUCT_COMPLETE"
        receipt["failure_type"]=type(exc).__name__
        receipt["failure_reason"]=str(exc)[:500]
        checkpoint()
        print("V439_BLOCKED",receipt["failure_type"],
              receipt["failure_reason"],flush=True)
        return 3

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--binary",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    a=p.parse_args()
    raise SystemExit(run(a.binary,a.out))

if __name__=="__main__":
    main()
