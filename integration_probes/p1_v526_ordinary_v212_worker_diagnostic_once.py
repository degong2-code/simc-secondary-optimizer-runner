#!/usr/bin/env python3
"""v526 one actual ordinary v212-installed worker error diagnostic, no AI.
Physical 70783 source → existing v113/v212 → one ordinary session.
Read only bounded code from original v106 worker log/status, never fake PASS.
"""
from __future__ import annotations
import argparse, json, os, pathlib, re, sys, tempfile, hashlib
from fastapi.testclient import TestClient
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner"),str(ROOT/"integration_probes")]
import v113_local_web_api as web
import p1_v524_m1_m2_source_owner_once as v524
from integration_probes import p3_haj_real_local_web_native_e2e as native_web

def check(v, code):
    if not v: raise RuntimeError("V526_"+code)

def sha(path):
    with pathlib.Path(path).open("rb") as f: return hashlib.file_digest(f,"sha256").hexdigest()

def submit(client, path, payload):
    h={"x-simc-local-token":"v526-proof-token",
       "origin":"http://127.0.0.1:8765"}
    r=client.post(path,headers=h,json=payload)
    return r.json() if r.status_code==200 else {
        "http_status":r.status_code,"detail":r.json().get("detail")}

def run(binary,out):
    out=pathlib.Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    receipt=out/"V526_REAL_BASE_WORKER_REASON.json"
    report={"schema":"v526_real_v212_ordinary_worker_blocker_v1",
            "status":"NOT_STARTED","build":v524.BUILD,"target_ilevel":334,
            "AI_runtime_calls":0,"new_dps_native_confirmed":0,
            "environment_native":None,"worker_exit":None,"full_product_e2e":"PENDING"}
    def save():receipt.write_text(json.dumps(report,sort_keys=True,ensure_ascii=False,
        indent=2)+"\n",encoding="utf8")
    save()
    try:
        check(sys.platform=="win32","WINDOWS_REQUIRED")
        binary=pathlib.Path(binary).resolve(strict=True)
        check(binary.name.lower()=="simc.exe" and sha(binary)==v524.EXE_SHA,
              "PINNED_SIMC_BINARY_REQUIRED")
        check(v524.EphemeralActionsCredentials().load() is not None,
              "SOURCE_CREDS_MISSING")
        with tempfile.TemporaryDirectory(prefix="v526-ordinary-",dir=out) as t:
            root=pathlib.Path(t)/"runs";root.mkdir()
            jobs=web.LocalJobs(root,source_credential_store=
                v524.EphemeralActionsCredentials())
            myth=jobs.discover_season_myth_target(v524.BUILD)
            check(myth.get("target_ilevel")==334 and myth.get("status")==
                  "MYTH_TARGET_CANDIDATE_FROM_MATCHED_WAGO_V163_SOURCE",
                  "M1_NOT_VERIFIED")
            env=jobs.build_season_environment(game_build=v524.BUILD,
                  target_ilevel=334,auto_initial_core_build=True,
                  auto_initial_core_simc_binary=str(binary),
                  simc_revision_hint=v524.REV,existing_special_gem_id=None,
                  source_target_socket_count=4,
                  auto_myth_target_source_build=v524.BUILD,
                  auto_myth_target_source_sha256=myth["currency_csv_sha256"])
            report["environment_native"]=env.get("native_calls")
            check(env.get("environment_installed") is True and
                  env.get("environment_ready") is True and
                  env.get("G")==2850 and env.get("J")==92 and env.get("F")==165,
                  "M2_BASE_NOT_INSTALLED")
            report["manifest_sha256"]=env["source_compilation"][
                "verified_environment_install"]["manifest_sha256"]
            save()
            with native_web.verified_current_catalog(
                env["source_compilation"]["source_catalog_path"],v524.BUILD):
                app=web.create_app(root=root,token="v526-proof-token")
                app.state.jobs.remember_verified_fresh_environment(env)
                with TestClient(app,base_url="http://127.0.0.1:8765") as c:
                    controls=web.sessions.standard_controls(("hunter","survival"))
                    controls["race"]="human";controls["oil_hands"]=[]
                    request={"controls":controls,"binary":str(binary),
                       "revision":v524.REV,"current_season_product":True,
                       "installed_season_game_build":v524.BUILD,
                       "installed_manifest_sha256":report["manifest_sha256"]}
                    plan=submit(c,"/api/v1/sessions/plan",request)
                    report["plan_status"]=plan.get("status")
                    check(plan.get("status")=="READY_ZERO_NATIVE",
                          "REAL_ORDINARY_PLAN_NOT_READY")
                    sid=plan["session_id"]
                    report["session_id"]=sid
                    parent=root/sid
                    identity=json.loads((parent/"V106_SESSION_IDENTITY.json").read_text("utf8"))
                    report["original_worker_identity"]={
                      "fresh_manifest_present":
                       "fresh_v212_installed_manifest_sha256" in identity,
                      "original_catalog_game_build":(
                       identity.get("current_season_source_catalog") or {}).get("game_build")}
                    start=submit(c,"/api/v1/sessions/start",request)
                    report["start_status"]=start.get("status")
                    check(start.get("status")=="WORKER_STARTED",
                          "REAL_ORDINARY_START_FAILED")
                    report["worker_exit"]=app.state.jobs.children[sid].wait(timeout=660)
                    state=web.sessions.paths(parent)
                    if state["state"].is_file():
                        worker=json.loads(state["state"].read_text("utf8"))
                        report["worker_state"]=worker.get("status")
                        reason=worker.get("reason","")
                        tokens=re.findall(r"[A-Z][A-Z0-9_]{4,120}",reason)
                        report["worker_error_code_tokens"]=tokens[:8]
                        report["worker_error_kind"]=reason.split(":",1)[0][:64]
                    if state["progress"].is_file():
                        progress=json.loads(state["progress"].read_text("utf8"))
                        report["native_attempts_progress"]=progress.get("new_native_attempts")
                        report["completed_cases"]=progress.get("completed_jobs")
                    if state["log"].is_file():
                        text=state["log"].read_text("utf8",errors="replace")
                        for line in reversed(text.splitlines()):
                            if line.startswith(("V106_BLOCKED:","V096_BLOCKED:")):
                                report["original_worker_log_kind"]=line.split(":",1)[0]
                                report["worker_log_error_tokens"]=re.findall(
                                    r"[A-Z][A-Z0-9_]{4,120}",line)[:8]
                                break
                    report["status"]=("PASS_ORDINARY_NATIVE_SIX" if report[
                        "worker_exit"]==0 else
                        "CONFIRMED_ORDINARY_V212_WORKER_BLOCKED")
                    save()
                    return 0
    except Exception as exc:
        report["status"]="DIAGNOSTIC_RUN_ABORTED"
        report["error_type"]=type(exc).__name__
        report["error_tokens"]=re.findall(r"[A-Z][A-Z0-9_]{4,120}",str(exc))[:8]
        save();return 3
    finally:
        print("V526_BASELINE_DIAGNOSTIC "+json.dumps(report,
           sort_keys=True,ensure_ascii=False),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--binary",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    a=p.parse_args();sys.exit(run(a.binary,a.out))
