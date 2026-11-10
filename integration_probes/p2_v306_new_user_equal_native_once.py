#!/usr/bin/env python3
"""One NEW product user source -> exact SimC, equal-cost v290/v306 pilot.

New *destruction warlock* through v113 zero-history season environment,
v216/v212 approved G/J/F/O, v106 controls, v113 FastAPI /longrun/prepare,
v098 generated source, original v291 request + v065 actual SimC acceptance.

This compares the v290 candidate proposal under fixed-scout resource
normalization, NOT the unchanged v290 default precision cadence. Two arms
share precisely one profile, source, binary, combat, initial global sample,
scout/confirm iteration identities, and requested iterations. No historical
HAE/Ret/Frost profile or DPS is imported; no Native result is interpolated.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import pathlib
import re
import tempfile
import time
from collections import Counter

from fastapi.testclient import TestClient

from runner import v106_user_session_controller as users
from runner import v113_local_web_api as web
from runner import v289_retail_live_build_source as retail
from runner import v291_durable_multiscale_native_runner as durable
from runner import v293_local_longrun_session as longrun
from runner import v290_multiscale_adaptive_policy as v290
from runner import v303_adaptive_region_resource_policy as regional
from runner import v304_v303_durable_adapter as v304
from runner import v306_seed_retained_coarse_escape_regions as v306
from integration_probes import p2_new_profile_product_e2e_once as fresh
from integration_probes import p3_haj_real_local_web_native_e2e as web_probe

SCHEMA="p2_v306_new_destruction_product_equal_simc_v1"
CASE_ID="destruction_warlock_4ordinary_T3400"
GLOBAL, POST, CONFIRM = 20, 20, 4
PLAN_CAP = GLOBAL + POST + CONFIRM
MAX_TOTAL_NEW_DPS_NATIVE = GLOBAL + 2 * (POST + CONFIRM)
MAX_WALL_SECONDS = 300
OUT=pathlib.Path("out/p2_v306_new_product_equal_once").resolve()
RECEIPT=OUT/"receipt.json"
ARMS=("v290_normalized_scout","v306_seed_retained")
SOURCE_BUILD=fresh.BUILD
SOURCE_REVISION=fresh.REVISION
EXPECTED_BINARY_SHA=fresh.BINARY_SHA


class PilotBlocked(RuntimeError):
    pass


def need(ok,code):
    if not ok:
        raise PilotBlocked(code)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def equal_budget(scout,confirm):
    need(type(scout) is int and type(confirm) is int
         and 0 < scout < confirm, "P2_EXACT_NATIVE_ITERATION_IDENTITIES")
    return {
        "global_scouts": GLOBAL,
        "post_scouts_per_arm": POST,
        "confirmations_per_arm": CONFIRM,
        "logical_requests_per_arm": PLAN_CAP,
        "logical_initial_global_shared": True,
        "requested_iterations_per_arm": (GLOBAL + POST)*scout + CONFIRM*confirm,
        "scout_iterations":scout,"confirmation_iterations":confirm,
        "maximum_fresh_dps_native":MAX_TOTAL_NEW_DPS_NATIVE,
        "same_binary_profile_combat_target_initial_candidates":True,
        "v290_comparator":"V290_PROPOSAL_ONLY_NORMALIZED_SCOUT_SCHEDULE_NOT_PRODUCT_DEFAULT",
        "one_profile_not_26_spec_generalization":True,
    }


def normalized_v290_candidate(rows, *, B, lower, upper, scout,confirm):
    """Genuine v290 proposals, scout-only cost; never claim original cadence."""
    observations = [{
        "target":v290.legacy.to_target(tuple(r["vector"])),
        "iterations":r["iterations"],"dps_mean":r["dps_mean"],
        "dps_sem":r["dps_sem"]} for r in rows]
    p = v290.next_plan(
        observations, total=B,lower=lower,upper=upper,
        native_calls_used=len(rows),max_native_calls=PLAN_CAP,
        scout_iterations=scout,confirmation_iterations=confirm,
        max_iterations=confirm)
    seen={tuple(r["vector"]) for r in rows}
    req=p.get("next_request")
    if req:
        vector=tuple(v290.legacy.key(req["target"]))
        if vector not in seen and v290.legacy.eligible(vector,B,lower,upper):
            return vector,p["decision"],req["phase"]!="scout"
    # Unlike the default precision path, this fixed-scout cohort must spend
    # its next equal-cost 35/64-iteration resource on a new vector.
    vector=v290._unobserved_global_maximin(B,lower,upper,64,seen)
    need(vector is not None and vector not in seen,
         "P2_V290_NORMALIZED_SCOUT_POOL_EXHAUSTED")
    return vector,"V290_PRECISION_TO_GLOBAL_SCOUT_FALLBACK",True


def plan_v306(history, *, B, lower, upper,scout,confirm):
    return v306.next_plan(
        history,total=B,lower=lower,upper=upper,
        max_native_calls=PLAN_CAP,scout_iterations=scout,
        confirmation_iterations=confirm,
        initial_global_calls=GLOBAL,confirmation_calls=CONFIRM)


def history_row(row, req):
    return {
        "target":v290.legacy.to_target(tuple(row["vector"])),
        "iterations":row["iterations"],"dps_mean":row["dps_mean"],
        "dps_sem":row["dps_sem"],"phase":req["phase"],
        "adaptive_stage":req["adaptive_stage"],
        "region_id":req["region_id"],
        "region_center":req["region_center"],
        "region_radius_fraction":req["region_radius_fraction"],
        "hybrid_method":req["hybrid_method"]}


def compare_selected(a,b):
    delta=a["dps_mean"]-b["dps_mean"]
    width=v290.Z95*math.hypot(a["dps_sem"],b["dps_sem"])
    # The two top candidates were selected adaptively and the SimC seeds may
    # differ. Do NOT turn a nominal 95% pairwise z into familywise superiority.
    return {
        "v306_minus_v290_normalized_dps":delta,
        "nominal_two_selected_95_halfwidth":width,
        "observed_gap_exceeds_nominal_halfwidth":abs(delta)>width,
        "multiple_selection_familywise_95_proven":False,
        "global_optimum_proven":False,
        "best_selected_pair_only":True}


def main():
    need(os.getenv("P2_V306_NEW_USER_EQUAL_NATIVE_ONCE")=="1",
         "EXPLICIT_P2_NEW_USER_REAL_NATIVE_OPT_IN_REQUIRED")
    case,controls=fresh.selected_case(CASE_ID)
    need((case["character_class"],case["character_spec"],case["final_T"],
          case["sockets"],case["special_gem"])==
         ("warlock","destruction",3400,4,None),
         "P2_NEW_DIFFERENT_SPEC_INPUT_DRIFT")
    binary=pathlib.Path("out/binary/simc").resolve(strict=True)
    binary_sha=digest(binary.read_bytes())
    need(binary_sha==EXPECTED_BINARY_SHA,"P2_PINNED_SIMC_BINARY_SHA_DRIFT")
    OUT.mkdir(parents=True,exist_ok=True)
    need(not RECEIPT.exists(),"P2_REUSED_ONE_SHOT_RECEIPT_FORBIDDEN")
    report={
        "schema":SCHEMA,"status":"STARTED","case_id":CASE_ID,
        "new_profile":case,"binary_sha256":binary_sha,
        "game_build":SOURCE_BUILD,"simc_revision":SOURCE_REVISION,
        "source_built_from_fresh_workspace":False,
        "historical_profile_or_dps_reused":False,
        "initial_global":[],"arms":{arm:[] for arm in ARMS},
        "new_environment_native":0,"new_product_dps_native":0,
        "same_run_exact_observation_reuses":0,
        "global_optimum_proven":False,
        "familywise_95_proven":False,
        "default_v290_replaced":False,
        "real_windows_browser_clicked":False}
    def save():
        temporary=RECEIPT.with_suffix(".tmp")
        temporary.write_text(json.dumps(report,sort_keys=True,indent=2,
                         allow_nan=False,ensure_ascii=False)+"\n",encoding="utf8")
        temporary.replace(RECEIPT)
    save()
    try:
        live=retail.discover(region="KR")
        report["observed_live_build"]=live["game_build"]
        need(live["game_build"]==SOURCE_BUILD,
             "CURRENT_RETAIL_BUILD_DIFFERS_FROM_PINNED_SOURCE")
        need(all(os.getenv(x) for x in (
             "BLIZZARD_CLIENT_ID","BLIZZARD_CLIENT_SECRET",
             "WCL_CLIENT_ID","WCL_CLIENT_SECRET")),
             "FRESH_SEASON_SOURCE_CREDENTIALS_REQUIRED")
        with tempfile.TemporaryDirectory(prefix="p2-new-warlock-v306-") as work:
            root=pathlib.Path(work)
            need(not list(root.iterdir()),"FRESH_BUILD_WORKSPACE_NOT_EMPTY")
            environment=web.LocalJobs(root).build_season_environment(
                game_build=SOURCE_BUILD,target_ilevel=case["target_ilevel"],
                auto_initial_core_build=True,
                auto_initial_core_simc_binary=str(binary),
                simc_revision_hint=SOURCE_REVISION,
                existing_special_gem_id=None,
                source_target_socket_count=case["sockets"])
            compilation=environment.get("source_compilation") or {}
            layout=compilation.get("physical_gem_layout_unadmitted") or {}
            installed=compilation.get("verified_environment_install") or {}
            report["environment_budget"]={k:environment.get(k)
                for k in ("G","J","F","O","B","T")}
            report["new_environment_native"]=environment.get("native_calls",0)
            need(environment.get("environment_ready") is True and
                 environment.get("environment_installed") is True and
                 installed.get("status")==
                 "FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY" and
                 type(report["new_environment_native"]) is int and
                 0<=report["new_environment_native"]<=3,
                 "FRESH_ENV_NATIVE_READY_OR_THREE_CALL_CAP")
            need(layout.get("socket_total")==4 and
                 layout.get("special_gem_id") is None and
                 len(layout.get("ordinary_gem_ids") or [])==4 and
                 len(set(layout["ordinary_gem_ids"]))==4,
                 "FOUR_DISTINCT_ORDINARY_GEMS_NO_SPECIAL_REQUIRED")
            need(environment["B"]==environment["G"]+
                 environment["J"]+environment["F"] and
                 environment["T"]==environment["B"] and
                 sum(environment["O"].values())==0,
                 "FRESH_G_J_F_O_ACCOUNTING_DRIFT")
            report["installed_manifest_sha256"]=installed["manifest_sha256"]
            report["source_built_from_fresh_workspace"]=True
            save()

            source_catalog=compilation["source_catalog_path"]
            with web_probe.verified_current_catalog(source_catalog,SOURCE_BUILD):
                app=web.create_app(root=root,token="p2-v306-one-shot-token")
                app.state.jobs.remember_verified_fresh_environment(environment)
                controls["oil_hands"]=[]
                payload={
                    "controls":controls,"binary":str(binary),
                    "revision":SOURCE_REVISION,"current_season_product":True,
                    "max_native_calls":80,
                    "max_new_native_this_invocation":1,
                    "max_elapsed_seconds":360}
                with TestClient(app,base_url="http://127.0.0.1:8765") as client:
                    headers={"x-simc-local-token":"p2-v306-one-shot-token",
                             "origin":"http://127.0.0.1:8765"}
                    p=client.post("/api/v1/longrun/prepare",
                                  headers=headers,json=payload)
                    if p.status_code!=200:
                        try:
                            detail=p.json().get("detail",{})
                            err=detail.get("code") if type(detail) is dict else detail
                        except (ValueError,TypeError):
                            err="UNREADABLE_HTTP_DETAIL"
                        raise PilotBlocked("USER_PRODUCT_PREPARE_HTTP_%d_%s"%(
                            p.status_code,err))
                    prepared=p.json()
                    need(prepared.get("status")==
                         "LONGRUN_SOURCE_PREPARED_NO_DPS_NATIVE",
                         "PRODUCT_WEB_PREPARE_NOT_SOURCE_ONLY")
                    session=prepared["session_id"]
                    inputs=client.get("/api/v1/sessions/%s/inputs"%session,
                                      headers=headers)
                    need(inputs.status_code==200,"USER_INPUT_SEAL_HTTP_FAILED")
                    effective=inputs.json()["user"]
                    char=effective["character"]
                    need((char["class"],char["spec"],char["race"])==
                         ("warlock","destruction","human") and
                         effective["target"]["final_T"]==3400,
                         "FRESH_PRODUCT_USER_INPUT_MUTATED")
                    need(prepared["environment_manifest"][
                         "fresh_v212_installed_manifest_sha256"]==
                         report["installed_manifest_sha256"],
                         "PRODUCT_SOURCE_BUILD_MANIFEST_SHA_DRIFT")
                    staged=longrun.prepare(root/session,80)
                    context=staged["context"]
                    flask=staged["flask"]
                    identity=context["identity"]
                    need(identity["binary_sha256"]==binary_sha and
                         identity["revision"]==SOURCE_REVISION and
                         identity["approved_final_T"]==case["final_T"] and
                         sum(identity["oil_vector"].values())==0,
                         "PRODUCT_CONTEXT_SOURCE_BINARY_FINAL_T_DRIFT")
                    normalized=context["bundle"]["prepared"]["scenario"]
                    B,lo,hi=durable.constraints.bounds(
                        normalized,durable.adaptive.feasible_budget(context,flask))
                    lower,upper=tuple(lo),tuple(hi)
                    scout=identity["scout_iterations"]
                    confirm=identity["confirm_iterations"]
                    need(B==case["final_T"] and
                         v290.legacy.eligible(
                            v290._apportion(B,lower,upper,(1,1,1,1)),
                            B,lower,upper),
                         "FRESH_MANUAL_T_BOUNDS_NOT_FEASIBLE")
                    report.update(
                        product_profile_sha256=identity["source_profile_sha256"],
                        product_scenario_digest=identity["scenario_digest"],
                        approved_final_T=identity["approved_final_T"],
                        free_budget_B=B,
                        fixed_O=identity["oil_vector"],
                        lower=lower,upper=upper,
                        budget=equal_budget(scout,confirm),
                        product_v113_v216_v212_v098_FastAPI=True)
                    save()

                    cache={}
                    elapsed_begin=time.perf_counter()
                    def evaluate(vector,iters):
                        vector=tuple(vector)
                        need(iters in (scout,confirm) and
                             v290.legacy.eligible(vector,B,lower,upper),
                             "P2_EXACT_RATING_OR_ITERATION_DRIFT")
                        key=(vector,iters)
                        if key in cache:
                            report["same_run_exact_observation_reuses"]+=1
                            return dict(cache[key],source="SAME_RUN_EXACT_OBSERVATION_REUSE")
                        need(report["new_product_dps_native"] <
                             MAX_TOTAL_NEW_DPS_NATIVE,
                             "P2_REAL_NATIVE_CALL_LIMIT_EXCEEDED")
                        need(time.perf_counter()-elapsed_begin<MAX_WALL_SECONDS,
                             "P2_BOUNDED_NATIVE_WALL_SECONDS_EXCEEDED")
                        index=report["new_product_dps_native"]
                        plan={"index":index,"phase":("scout" if iters==scout else "precision"),
                              "target":v290.legacy.to_target(vector),"iterations":iters}
                        req,folder=durable._request(
                            context,flask,OUT,plan)
                        start=time.perf_counter()
                        # Exact v065 executor, not a reimplementation of DPS,
                        # proc, effect or validation. Fail closed on partial.
                        accepted=durable.engine.execute_one(
                            req,{"native_revision":SOURCE_REVISION},
                            binary,folder,{"native_attempts":0},
                            cache_only=False,recover_verified_partial=False)
                        raw=(folder/"result.json").read_bytes()
                        native=durable.oil.ingest_native(req,json.loads(raw),raw)
                        need(accepted["native_json_sha256"]==
                             native["native_json_sha256"] and
                             accepted["case_key"]==native["case_key"] and
                             req["v092_final_T"]==case["final_T"] and
                             req["v092_base_B"]==B,
                             "P2_JSON2_AND_FINAL_CHMV_NOT_ACCEPTED")
                        row={"vector":list(vector),"iterations":iters,
                             "dps_mean":native["dps_mean"],
                             "dps_sem":native["dps_sem"],
                             "json2_sha256":native["native_json_sha256"],
                             "input_sha256":req["input_sha256"],
                             "case_key":req["case_key"],
                             "simc_seed":durable._source_seed(
                                 json.loads(raw),accepted),
                             "wall_seconds":round(time.perf_counter()-start,5),
                             "source":"NEW_NATIVE"}
                        cache[key]=dict(row)
                        report["new_product_dps_native"]+=1
                        save()
                        return dict(row)

                    global_order=v304._global_order(B,lower,upper,GLOBAL)
                    v306_history=[]
                    for idx,vector in enumerate(global_order):
                        proposed=plan_v306(v306_history,B=B,lower=lower,
                                           upper=upper,scout=scout,confirm=confirm)
                        req=proposed["next_request"]
                        need(req is not None and
                             req["adaptive_stage"]=="global_initial" and
                             tuple(v290.legacy.key(req["target"]))==vector,
                             "V306_COMMON_INITIAL_20_GLOBAL_ORDER_DRIFT")
                        measured=evaluate(vector,scout)
                        report["initial_global"].append(measured)
                        v306_history.append(history_row(measured,req))
                        save()

                    for round_id in range(POST):
                        for arm in ARMS:
                            if arm=="v306_seed_retained":
                                proposed=plan_v306(
                                    v306_history,B=B,lower=lower,
                                    upper=upper,scout=scout,confirm=confirm)
                                req=proposed["next_request"]
                                need(req is not None and req["phase"]=="scout"
                                     and req["adaptive_stage"] in
                                     ("regional","global_reserve"),
                                     "V306_POST_GLOBAL_SCOUT_PHASE_DRIFT")
                                vector=tuple(v290.legacy.key(req["target"]))
                                decision=proposed["decision"]
                            else:
                                req=None
                                vector,decision,forced=normalized_v290_candidate(
                                    report["initial_global"]+report["arms"][arm],
                                    B=B,lower=lower,upper=upper,
                                    scout=scout,confirm=confirm)
                            seen={tuple(r["vector"]) for r in
                                  report["initial_global"]+report["arms"][arm]}
                            need(vector not in seen,"P2_SAME_ARM_DUPLICATE_SCOUT")
                            row=dict(evaluate(vector,scout),
                                     policy_decision=decision,
                                     policy_round=round_id+1)
                            if arm=="v306_seed_retained":
                                v306_history.append(history_row(row,req))
                                row.update(
                                  adaptive_stage=req["adaptive_stage"],
                                  region_id=req["region_id"],
                                  region_center=req["region_center"],
                                  region_radius_fraction=req["region_radius_fraction"],
                                  hybrid_method=req["hybrid_method"])
                            else:
                                row["forced_scout_from_precision"]=forced
                            report["arms"][arm].append(row)
                            save()
                        if (round_id+1)%5==0:
                            print("P2_V306_EQUAL_PROGRESS",
                                  json.dumps({
                                      "post_scout_round":round_id+1,
                                      "new_dps_native":report["new_product_dps_native"],
                                      "same_run_reuses":report[
                                         "same_run_exact_observation_reuses"],
                                      "elapsed_seconds":round(
                                        time.perf_counter()-elapsed_begin,2)},
                                      sort_keys=True),flush=True)

                    for rank in range(CONFIRM):
                        for arm in ARMS:
                            if arm=="v306_seed_retained":
                                proposed=plan_v306(
                                    v306_history,B=B,lower=lower,upper=upper,
                                    scout=scout,confirm=confirm)
                                req=proposed["next_request"]
                                need(req is not None and
                                     req["adaptive_stage"]=="confirmation" and
                                     req["iterations"]==confirm,
                                     "V306_EXACT_CONFIRM_PHASE_MISSING")
                                vec=tuple(v290.legacy.key(req["target"]))
                            else:
                                req=None
                                scouts=report["initial_global"]+[
                                    r for r in report["arms"][arm]
                                    if r["iterations"]==scout]
                                by_vec={tuple(r["vector"]):r for r in scouts}
                                ranked=sorted(by_vec,key=lambda v:
                                    (-regional.score(by_vec[v]),v))
                                oldconf={tuple(r["vector"]) for r in
                                         report["arms"][arm] if
                                         r["iterations"]==confirm}
                                vec=next(v for v in ranked if v not in oldconf)
                            measured=evaluate(vec,confirm)
                            row=dict(measured,confirmation_rank=rank+1)
                            report["arms"][arm].append(row)
                            if req is not None:
                                v306_history.append(history_row(row,req))
                                row["hybrid_method"]=req["hybrid_method"]
                            save()

                    need(plan_v306(v306_history,B=B,lower=lower,upper=upper,
                                   scout=scout,confirm=confirm)[
                                   "next_request"] is None,
                         "V306_SESSION_NOT_BUDGET_EXHAUSTED")
                    for arm in ARMS:
                        rows=report["initial_global"]+report["arms"][arm]
                        need(len(rows)==PLAN_CAP and
                             len({(tuple(r["vector"]),r["iterations"])
                                  for r in rows})==PLAN_CAP and
                             sum(r["iterations"] for r in rows)==
                             report["budget"]["requested_iterations_per_arm"],
                             "P2_ARM_EXACT_REQUEST_ITERATION_MISMATCH")
                    confirms={
                        arm:[r for r in report["arms"][arm]
                             if r["iterations"]==confirm] for arm in ARMS}
                    need(all(len(r)==CONFIRM for r in confirms.values()),
                         "P2_CONFIRMED_COHORT_MISSING")
                    winners={arm:max(rows,key=lambda r:(
                        r["dps_mean"],-r["dps_sem"])) for arm,rows in confirms.items()}
                    report["selected_320_or_typed_confirm"]=winners
                    report["selected_pair_comparison"]=compare_selected(
                        winners["v306_seed_retained"],
                        winners["v290_normalized_scout"])
                    report["methods_by_region"]=dict(Counter(
                        r.get("hybrid_method") for r in
                        report["arms"]["v306_seed_retained"]
                        if r["iterations"]==scout))
                    report["actual_benchmark_elapsed_seconds"]=round(
                        time.perf_counter()-elapsed_begin,3)
                    report["status"]="PASS_REAL_NEW_PROFILE_EQUAL_ITERATIONS_EXPLORATORY"
                    save()
                    print("P2_V306_NEW_PRODUCT_REAL_FINAL",json.dumps({
                        "status":report["status"],
                        "case":CASE_ID,
                        "new_environment_native":report["new_environment_native"],
                        "new_product_dps_native":report["new_product_dps_native"],
                        "same_run_reuses":report["same_run_exact_observation_reuses"],
                        "budget":report["budget"],
                        "profile_sha":report["product_profile_sha256"],
                        "winner_v290_normalized":winners["v290_normalized_scout"],
                        "winner_v306":winners["v306_seed_retained"],
                        "selected_comparison":report["selected_pair_comparison"],
                    },sort_keys=True),flush=True)
        return report
    except BaseException as exc:
        report["status"]="BLOCKED_OR_PARTIAL_"+type(exc).__name__
        value=str(exc)
        report["first_error_code"]=(value if
            re.fullmatch(r"[A-Z][A-Z0-9_]{3,100}",value)
            else type(exc).__name__)
        save()
        raise


if __name__=="__main__":
    main()
