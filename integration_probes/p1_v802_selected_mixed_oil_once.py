#!/usr/bin/env python3
"""One actual current-build selected weapon + measured O, no mock admission.

Reuse the v769 binary cache and original v113/v216 Build. Old v790 receipts
are compact, not a recoverable install workspace. One explicit positive-O
install only; refresh selectable gear only if the known source item is
absent. No automatic retry, no new solver, no all-spec Native fanout.
"""
import argparse
import json
from pathlib import Path
import re
import tempfile
import time
import traceback
from contextlib import contextmanager
from fastapi.testclient import TestClient
from p1_v769_incremental_environment_once import (
    BUILD, REV, EphemeralActionsCredentials, digest, summary, need)
import v113_local_web_api as web
import v289_retail_live_build_source as retail
import v293_local_longrun_session as longrun

# Same-season observed v724 source weapon (survival, polearm). Old v578
# oil/flask IDs are test selections only: current Build must prove them anew.
WEAPON=268215
OIL=243734
FLASK=241324
TARGET=334
WEAPON_LEVEL=330
T=3500
TOKEN="v802-local-only"
MAX_ENV_NATIVE=24

def _safe_failure(exc):
    """Only fixed code and repository-relative frame names; no local paths,
    profile text, credentials, raw logs or arbitrary exception message."""
    code=str(exc).split(":",1)[0].split("\n",1)[0]
    out={"kind":type(exc).__name__}
    if re.fullmatch(r"[A-Z][A-Z0-9_]{3,140}",code):
        out["code"]=code
    if isinstance(exc,KeyError) and exc.args and type(exc.args[0]) is str:
        key=exc.args[0]
        if re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]{0,80}",key):
            out["missing_field"]=key
    out["frames"]=[{"file":Path(f.filename).name,"function":f.name,
                    "line":f.lineno}
                   for f in traceback.extract_tb(exc.__traceback__)
                   if re.fullmatch(r"v[0-9]+_[a-zA-Z0-9_]+\.py",Path(f.filename).name)][-12:]
    return out

def _native_observation(root):
    """Count already recorded attempts without rerunning, exporting bytes,
    or interpreting a missing result as a successful measurement."""
    pairs={}
    for path in root.rglob("v278_*/receipt.json"):
        if not path.is_file() or path.is_symlink():continue
        try:
            row=json.loads(path.read_text("utf8"))
            if row.get("schema")=="v278_original_simc_precombat_native_pair_v1":
                pairs[path.parent.name]={"status":row.get("status"),
                    "new_native_calls":row.get("new_native_calls"),
                    "receipt_sha256":digest(path)}
        except (OSError,ValueError,TypeError):continue
    static={}
    folder=root.parent/"static-item-probes"
    if folder.is_dir():
        for path in folder.glob("*/native.log"):
            if not path.is_file() or path.is_symlink():continue
            with path.open("rb") as stream:
                count=sum(b"=== V208 ONE SELECTED USER STATIC NATIVE ===" in line
                          for line in stream)
            static[path.parent.name]={"attempts":count,
                "json2_exists":(path.parent/"native.json").is_file()}
    return pairs,static

@contextmanager
def observe_real_boundary(report,root):
    """CI-only observer: delegate the real exception mapping unchanged.
    Never bypass an admission, substitute a response or add a Native call."""
    original=web.blocked
    before_pair,before_static=_native_observation(root)
    def observe(exc,**kw):
        if "original_boundary_failure" not in report:
            report["original_boundary_failure"]=_safe_failure(exc)
        return original(exc,**kw)
    web.blocked=observe
    try:
        yield
    finally:
        web.blocked=original
        after_pair,after_static=_native_observation(root)
        new_pairs=[row for key,row in after_pair.items() if key not in before_pair]
        new_static=[{"attempts":row["attempts"]-before_static.get(key,{}).get("attempts",0),
                     "json2_exists":row["json2_exists"]}
                    for key,row in after_static.items()
                    if row["attempts"]>before_static.get(key,{}).get("attempts",0)]
        report["observed_selected_native_receipts"]={
            "oil_completed_attempt_receipts":len(new_pairs),
            "oil_cases":new_pairs,
            "static_logged_attempts":sum(row["attempts"] for row in new_static),
            "static_cases":new_static,
            "counts_are_observed_receipts_not_unrecorded_processes":True}

def run(args):
    out=Path(args.out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    receipt=out/"V802_SELECTED_MIXED_OIL.json"
    report={"status":"STARTED","build":BUILD,"revision":REV,
            "target_ilevel":TARGET,"selected_weapon_id":WEAPON,
            "selected_weapon_ilevel":WEAPON_LEVEL,"manual_final_T":T,
            "actual_environment_native":None,"selected_oil_native":None,
            "selected_static_native":None,"dps_native":0,
            "full_product_e2e":"PENDING","global_optimum_proven":False}
    def save(stage=None):
        if stage:report["stage"]=stage
        raw=json.dumps(report,sort_keys=True,ensure_ascii=False,allow_nan=False)
        receipt.write_text(raw+"\n",encoding="utf8")
        print("V802_RECEIPT "+raw,flush=True)
    def call(client,method,url,**kw):
        response=client.request(method,url,headers={
            "x-simc-local-token":TOKEN,"origin":"http://127.0.0.1:8765"},**kw)
        if response.status_code!=200:
            try:
                detail=response.json().get("detail",{})
                code=detail.get("code") if isinstance(detail,dict) else None
                kind=detail.get("kind") if isinstance(detail,dict) else None
            except ValueError:code=None;kind=None
            report["http_blocker"]={"status":response.status_code,"code":code,"kind":kind}
            save()
            raise RuntimeError("V802_ORIGINAL_HTTP_BLOCKED")
        return response.json()
    def wait(client,sid):
        limit=time.monotonic()+420
        while time.monotonic()<limit:
            status=call(client,"GET","/api/v1/sessions/"+sid+"/longrun/status")
            if not status.get("active"):
                worker=(status.get("progress") or {}).get("worker") or {}
                need(worker.get("status") not in ("BLOCKED_OR_PARTIAL","QUEUED","RUNNING"),
                     "V802_ORIGINAL_WORKER_BLOCKED")
                return status
            time.sleep(.5)
        raise RuntimeError("V802_NATIVE_TIMEOUT")
    def case_hashes(root,sid):
        folder=root/sid
        cfg=longrun.config(folder)
        cases=longrun.stage_path(folder,cfg["native_budget"])/"simc_results"/"cases"
        result=[]
        for folder in sorted(cases.glob("case_*/native")):
            inp,js,rec=(folder/name for name in ("input.simc","result.json","native_receipt.json"))
            if not all(x.is_file() for x in (inp,js,rec)):continue
            profile=inp.read_text("utf8")
            line=next((x for x in profile.splitlines() if x.startswith("main_hand=")),"")
            need(re.search(r"(?:^|,)id="+str(WEAPON)+r"(?:,|$)",line) and
                 re.search(r"(?:^|,)ilevel="+str(WEAPON_LEVEL)+r"(?:,|$)",line),
                 "V802_NATIVE_FINAL_WEAPON_DRIFT")
            need("temporary_enchant=main_hand:thalassian_phoenix_oil_2" in profile.splitlines(),
                 "V802_NATIVE_FINAL_OIL_TOKEN_DRIFT")
            result.append({"case":folder.parent.name,"input":digest(inp),
                           "json2":digest(js),"receipt":digest(rec)})
        return result
    save("BINARY")
    try:
        binary=Path(args.simc).resolve()
        meta=Path(args.identity).resolve()
        need(binary.is_file() and meta.is_file(),"V802_EXISTING_BINARY_CACHE_MISSING")
        identity=json.loads(meta.read_text("utf-8-sig"))
        need(identity["game_build"]==BUILD and identity["source_commit"]==REV and
             identity["binary_sha256"]==digest(binary),"V802_PINNED_BINARY_DRIFT")
        report["binary_sha256"]=identity["binary_sha256"]
        live=retail.discover(region="KR")
        report["observed_live_build"]=live["game_build"]
        need(live["game_build"]==BUILD,"V802_LIVE_BUILD_CHANGED")
        credentials=EphemeralActionsCredentials()
        need(credentials.load() is not None,"V802_SOURCE_CREDENTIALS_MISSING")
        with tempfile.TemporaryDirectory(prefix="v802-") as tmp:
            root=Path(tmp)/"runs";root.mkdir()
            app=web.create_app(root=root,token=TOKEN,source_credential_store=credentials)
            jobs=app.state.jobs
            save("ONE_POSITIVE_O_BUILD")
            env=jobs.build_season_environment(game_build=BUILD,target_ilevel=TARGET,
                native_G_binary=str(binary),consumable_native_binary=str(binary),
                auto_native_F_requested=True,auto_native_O_requested=True,
                selected_flask_item_id=FLASK,selected_oil_item_ids_by_hand={"main_hand":OIL},
                source_target_socket_count=4,simc_revision_hint=REV)
            report["environment"]=summary(env)
            report["actual_environment_native"]=env.get("native_calls")
            save()
            need(env.get("environment_ready") is True and env.get("environment_installed") is True,
                 "V802_ORIGINAL_POSITIVE_O_INSTALL_PENDING")
            need(type(env.get("native_calls")) is int and 0<=env["native_calls"]<=MAX_ENV_NATIVE,
                 "V802_ENV_NATIVE_BOUND")
            comp=env["source_compilation"]
            install=comp["verified_environment_install"]
            sha=install["manifest_sha256"]
            path=Path(install["stage_output_path"])
            original=digest(path)
            scope=comp["v098_source_only_profile_inputs_unadmitted"].get(
                "oil_weapon_scope_source_only",{}).get("main_hand",{})
            need(scope.get("physical_item_id")==OIL and
                 type(scope.get("scaled_rating_ilevel")) is int and
                 scope["scaled_rating_ilevel"]==TARGET and
                 sum(env["O"].values())>0,"V802_MEASURED_O_SCOPE_NOT_AVAILABLE")
            report["installed_O"]=env["O"]
            report["installed_manifest_sha256"]=sha
            query={"game_build":BUILD,"target_ilevel":TARGET,"installed_manifest_sha256":sha}
            with observe_real_boundary(report,root), TestClient(app,base_url="http://127.0.0.1:8765") as c:
                save("EXACT_SELECTED_WEAPON_SOURCE")
                gear=call(c,"GET","/api/v1/season-gear",params=query)
                def selected(g):
                    return next((r for r in g["choices"]["special_effect_gear_candidate"]
                        if r["item_id"]==WEAPON and
                           "hunter/survival" in r.get("compatible_dps_specs",[])),None)
                item=selected(gear)
                if item is None:
                    refresh=call(c,"POST","/api/v1/season-gear/refresh",params=query)
                    report["selectable_refresh"]={k:refresh.get(k) for k in
                        ("status","network_calls_now","native_calls_now","budget_rebuilt")}
                    save()
                    gear=call(c,"GET","/api/v1/season-gear",params=query)
                    item=selected(gear)
                need(item is not None,"V802_EXACT_CURRENT_SPECIAL_WEAPON_NOT_REGISTERED")
                opts=item.get("required_options") or {}
                need(type(opts) is dict and opts.get("bonus_id")=="13846",
                     "V802_EXACT_CURRENT_WEAPON_VARIANT_PENDING")
                controls=web.sessions.standard_controls(("hunter","survival"))
                controls.update(race="human",oil_hands=["main_hand"],final_T=T)
                controls["special_items"]=[{"slot":"main_hand","item_id":WEAPON,
                                            "ilevel":WEAPON_LEVEL,"options":opts}]
                request={"controls":controls,"binary":str(binary),"revision":REV,
                    "current_season_product":True,"installed_season_game_build":BUILD,
                    "installed_manifest_sha256":sha,"selected_flask_item_id":FLASK,
                    "selected_oil_item_ids_by_hand":{"main_hand":OIL},"user_socket_total":4}
                longreq={**request,"max_native_calls":12,"max_new_native_this_invocation":1,
                         "max_elapsed_seconds":360}
                save("FIRST_EXPLICIT_START_PREPARATION")
                p=call(c,"POST","/api/v1/longrun/prepare",json=longreq)
                report["selected_oil_native"]=p.get("selected_oil_native_calls_this_start")
                report["selected_static_native"]=p.get("selected_static_native_calls_this_start")
                save()
                need(p["status"]=="LONGRUN_SOURCE_PREPARED_NO_DPS_NATIVE" and
                     p["new_dps_native_calls"]==0 and
                     report["selected_oil_native"]==2 and
                     type(report["selected_static_native"]) is int and
                     0<=report["selected_static_native"]<=2,"V802_START_NATIVE_COUNTS_DRIFT")
                sid=p["session_id"];folder=root/sid
                manifest=json.loads((folder/"generated"/"manifest.json").read_text("utf8"))
                selected=manifest[web.bootstrap.entry.SELECTED_FRESH_SEASON_FIELD]
                oil=selected["oil_by_hand"]["main_hand"]["static_CHMV_vector"]
                report["selected_O"]=oil
                need(sum(oil.values())>0,"V802_SELECTED_MEASURED_O_NOT_POSITIVE")
                plan=call(c,"POST","/api/v1/sessions/plan",json=request)
                need(plan["status"]=="READY_ZERO_NATIVE" and plan["native_calls"]==0 and
                     plan["session_id"]==sid and plan["plan"]["base_B"]==T-sum(oil.values()) and
                     plan["plan"]["final_T"]==T,"V802_SELECTED_PLAN_REPLAY_OR_B_T_DRIFT")
                report["B"]=plan["plan"]["base_B"];report["T"]=T
                replay=call(c,"POST","/api/v1/longrun/prepare",json=longreq)
                need(replay["session_id"]==sid and replay.get("selected_oil_native_calls_this_start")==0
                     and replay.get("selected_static_native_calls_this_start")==0 and digest(path)==original,
                     "V802_PREPARE_CACHE_OR_INSTALLED_IMMUTABILITY_DRIFT")
                report["reprepare_native"]=0
                save("TWO_DPS_NATIVE_AND_CACHE_REPLAY")
                url="/api/v1/sessions/"+sid
                hashes=[]
                for count in (1,2):
                    call(c,"POST",url+"/longrun/resume",json={
                        "max_new_native_this_invocation":1,"max_elapsed_seconds":360})
                    status=wait(c,sid)
                    progress=status["progress"]
                    report["dps_native"]=progress["native_attempts"]
                    save()
                    need(progress["native_attempts"]==count and progress["completed_jobs"]==count,
                         "V802_DPS_NATIVE_PROGRESS_DRIFT")
                    current=case_hashes(root,sid)
                    need(len(current)==count and current[:len(hashes)]==hashes,
                         "V802_DPS_NATIVE_RECEIPT_DRIFT")
                    hashes=current
                call(c,"POST",url+"/longrun/cache-only",json={})
                status=wait(c,sid)
                need(status["progress"]["native_attempts"]==2 and
                     case_hashes(root,sid)==hashes and digest(path)==original,
                     "V802_CACHE_ONLY_NATIVE_OR_INSTALL_DRIFT")
                result=call(c,"GET",url+"/longrun/result")
                user=result["user_result"];best=user["observed_first_choice"]
                need(user["confidence_level"]==0.95 and user["global_optimum_proven"] is False and
                     sum(best["absolute_rating_T"].values())==T and
                     best["observed_dps_mean"]>0 and best["simc_sem"]>=0,
                     "V802_RESULT_DPS_SEM_T_DRIFT")
                report.update(status="PASS_REAL_SELECTED_MIXED_WEAPON_MEASURED_O_TWO_DPS_CACHE",
                    cache_only_new_native=0,cases=hashes,
                    dps=best["observed_dps_mean"],sem=best["simc_sem"],
                    rating=best["absolute_rating_T"],installed_unchanged=True)
                return 0
    except Exception as exc:
        code=str(exc).split(":",1)[0].split("\n",1)[0]
        report.update(status="BLOCKED_REAL_SELECTED_MIXED_OIL",
                      first_blocker=code if re.fullmatch(r"[A-Z][A-Z0-9_]{3,140}",code)
                                    else type(exc).__name__)
        report.setdefault("probe_failure",_safe_failure(exc))
        return 2
    finally:save()

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    for name in ("simc","identity","out"):ap.add_argument("--"+name,required=True)
    raise SystemExit(run(ap.parse_args()))
