#!/usr/bin/env python3
"""v571: actual extracted Windows source ZIP, user easy-start BAT, Chrome,
read-only historical plan persistence and restart/restore. Zero Native.

This does NOT run v216, seal a new v212 current-season installation, or
exercise actual adaptive cancellation; those have distinct prior evidence.
Existing 6-case source-backed plan is deliberately read-only historical
session and may NOT authorize the primary 64-case optimizer.
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
import time
import venv
import zipfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait,Select

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"integration_probes"))
from p1_v345_windows_extracted_zip_cmd_browser_restore import (
    PREFIX, REV, URL, wait_for_http, stop_cmd, actual_chrome, http_json, digest)

SCHEMA="p1_v571_extracted_windows_easy_start_real_chrome_restore_zero_native_v1"
NAME="V571_WINDOWS_ZIP_EASY_START_CHROME_RESTART_RECEIPT.json"

def need(ok,code):
    if not ok:raise RuntimeError("V571_"+code)

def safe(code):
    v=str(code).split("\n",1)[0]
    return v if re.fullmatch(r"V571_[A-Z_]{3,120}",v) else type(code).__name__

def browser_state(driver):
    return driver.execute_script("""
        return {
           supported:state.defaults.length,
           token:!!state.token,
           session:state.session,
           spec:field("spec"),race:field("race"),
           start_label:document.getElementById("start-btn").textContent,
           start_disabled:document.getElementById("start-btn").disabled,
           verified_build:state.verifiedInstalledBuildFromThisPage,
           gear_sha:state.seasonGear?.installed_manifest_sha256||null,
           gear_target:state.seasonGearTargetIlevel,
           level:Number(field("ilevel")),
           running:state.running,
           notice:document.getElementById("notice").textContent
        };
    """)

def launch_easy(root,home,localdata,log):
    env={**os.environ,"HOME":str(home),"USERPROFILE":str(home),
         "LOCALAPPDATA":str(localdata),"PYTHONIOENCODING":"utf-8",
         "PYTHONDONTWRITEBYTECODE":"1"}
    proc=subprocess.Popen(["cmd","/d","/c",
         str(root/"START_HERE_AUTO_SETUP_AND_RUN.bat")],
         cwd=root,env=env,stdin=subprocess.DEVNULL,
         stdout=log,stderr=subprocess.STDOUT)
    wait_for_http(proc)
    return proc

def run(zip_file,out):
    need(os.name=="nt","WINDOWS_RUNNER_ONLY")
    out=pathlib.Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    zip_file=pathlib.Path(zip_file).resolve(strict=True)
    report={"schema":SCHEMA,"status":"NOT_STARTED",
        "package_zip_sha256":digest(zip_file),"real_windows_runner":True,
        "real_extracted_easy_start":False,"real_chrome":False,
        "historical_plan_only":True,"primary_longrun_started":False,
        "real_adaptive_cancel_resume_exercised":False,
        "native_environment_calls":0,"native_dps_calls":0,
        "new_source_collection_calls":0,
        "synthetic_http":False,
        "personal_pc_setup_verified":False,
        "new_python_dependencies_installed_inside_test":False}
    def save():
        (out/NAME).write_text(json.dumps(report,ensure_ascii=False,
           sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf8")
    save()
    browser=proc=log=None
    with tempfile.TemporaryDirectory(prefix="v571-extracted-win-",dir=out) as temp:
        work=pathlib.Path(temp)
        home=work/"user-profile";home.mkdir()
        localdata=work/"local-appdata";localdata.mkdir()
        root=work/PREFIX
        try:
            with zipfile.ZipFile(zip_file) as archive:
                names=archive.namelist()
                need(len(names)==len(set(names)) and all(
                    x.startswith(PREFIX+"/") and
                    ".." not in pathlib.PurePosixPath(x).parts
                    for x in names),"ZIP_PATH_POLICY")
                manifest=json.loads(archive.read(
                    PREFIX+"/V181_PACKAGE_MANIFEST.json"))
                entries=manifest["files"]
                need(manifest["archive_root"]==PREFIX and
                     manifest["file_count"]==len(entries) and
                     len(entries)>=75 and
                     not manifest["native_executable_bundled"] and
                     not manifest["sessions_bundled"] and
                     not manifest["historical_native_json2_bundled"],
                     "ZIP_PAYLOAD_POLICY")
                for file in entries:
                    member=archive.read(PREFIX+"/"+file["path"])
                    need(len(member)==file["size"] and
                         hashlib.sha256(member).hexdigest()==file["sha256"],
                         "ZIP_MEMBER_SHA")
                required=("runner/webui/app.js",
                   "runner/v113_local_web_api.py",
                   "runner/v216_environment_build_coordinator.py",
                   "runner/v212_environment_manifest.py",
                   "runner/v293_local_longrun_session.py",
                   "START_HERE_AUTO_SETUP_AND_RUN.bat",
                   "START_SIMC_OPTIMIZER_WEB_WINDOWS.cmd")
                need(all(PREFIX+"/"+p in names for p in required),
                     "ZIP_RUNTIME_PATHS_MISSING")
                for file in required:
                    need(hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==
                         hashlib.sha256(archive.read(PREFIX+"/"+file)).hexdigest(),
                         "ZIP_CURRENT_HEAD_SOURCE_BYTES_MISMATCH")
                need(not any(n.lower().endswith((".exe",".dll",".pem",".key",
                      ".pfx")) for n in names),"BINARY_OR_SECRET_IN_PACKAGE")
                archive.extractall(work)
            report["archive_file_count"]=len(entries)
            report["verified_latest_runtime_sha"]=True
            need(root.is_dir() and
                (root/"START_HERE_AUTO_SETUP_AND_RUN.bat").is_file(),
                "EXTRACTED_ROOT_MISSING")
            # Reuse the Windows runner's already installed Python test stack.
            # Precreate a user-local venv, so the easy-start BAT's consent and
            # pip installers are NOT invoked and no network/native is needed.
            envpath=localdata/"SIMC_Secondary_Optimizer"/"web-python"
            venv.create(str(envpath),system_site_packages=True,with_pip=False)
            python=envpath/"Scripts"/"python.exe"
            need(python.is_file(),"USER_LOCAL_PYTHON_MISSING")
            check=subprocess.run([str(python),"-c",
                 "import fastapi,uvicorn; print('v571-python-ready')"],
                 capture_output=True,text=True,timeout=22)
            need(check.returncode==0 and
                 "v571-python-ready" in check.stdout,
                 "USER_LOCAL_VENV_DEPENDENCIES_UNAVAILABLE")
            env={**os.environ,"HOME":str(home),"USERPROFILE":str(home),
                 "LOCALAPPDATA":str(localdata),"PYTHONIOENCODING":"utf-8"}
            checked=subprocess.run(["cmd","/d","/c",
                str(root/"START_HERE_AUTO_SETUP_AND_RUN.bat"),"--check"],
                cwd=root,env=env,stdin=subprocess.DEVNULL,
                capture_output=True,text=True,encoding="utf8",
                errors="replace",timeout=35)
            need(checked.returncode==0 and
                 "[READY]" in checked.stdout and
                 "[SETUP]" not in checked.stdout,
                 "EASY_START_CHECK_REUSED_VENV_INCORRECTLY")
            report["easy_start_check_no_install"]=True
            state_home=home/"SIMC_Secondary_Optimizer"/"runs"
            need(not state_home.exists(),"SESSION_CREATED_DURING_CHECK")
            log=(out/"V571_WINDOWS_EASY_START_LAUNCHER.log").open(
                "w",encoding="utf8")
            proc=launch_easy(root,home,localdata,log)
            report["real_extracted_easy_start"]=True
            browser=actual_chrome()
            report["real_chrome"]=True
            first=browser_state(browser)
            need(first["supported"]==26 and first["token"] and
                 not first["session"] and first["verified_build"] is None and
                 first["gear_target"] is None and
                 first["start_label"]==
                   "시즌 환경 준비 · 장신구 목록 불러오기" and
                 not first["start_disabled"],"COLD_PRODUCT_START_UI_NOT_READY")
            initial=browser.execute_script("""
                return performance.getEntriesByType("resource").map(e=>e.name)
                  .filter(u=>u.includes("/environment/season-build") ||
                      u.includes("/environment/myth-target") ||
                      u.includes("/longrun/start"));
            """)
            need(not initial,"COLD_START_TRIGGERED_BUILD_OR_DPS")
            report["cold_visible_first_button"]=True
            # The first explicit click can be cancelled without any season
            # download, SimC launch, installation or orphan session.
            browser.execute_script("window.confirm=()=>false")
            btn=browser.find_element(By.ID,"start-btn")
            browser.execute_script(
                "arguments[0].scrollIntoView({block:'center'})",btn)
            btn.click()
            WebDriverWait(browser,15).until(
               lambda d:d.execute_script("return !state.busy"))
            snapshot=browser_state(browser)
            report["cancel_snapshot_flags"]={
                "session_type":type(snapshot["session"]).__name__,
                "session_present":bool(snapshot["session"]),
                "verified_build_present":bool(snapshot["verified_build"]),
                "gear_target":snapshot["gear_target"],
                "start_label":snapshot["start_label"],
                "notice":snapshot["notice"][:180]}
            print("V571_CANCEL_SNAPSHOT "+
                json.dumps(report["cancel_snapshot_flags"],
                           ensure_ascii=True,sort_keys=True),flush=True)
            need(not snapshot["session"] and
                 snapshot["verified_build"] is None and
                 snapshot["gear_target"] is None,
                 "CANCELLED_BUILD_MUTATED_STATE")
            no_network=browser.execute_script("""
                return performance.getEntriesByType("resource").map(e=>e.name)
                  .filter(u=>u.includes("/environment/season-build") ||
                      u.includes("/environment/myth-target") ||
                      u.includes("/longrun/start"));
            """)
            need(not no_network,"CANCELLED_BUTTON_SENT_SOURCE_OR_DPS")
            report["explicit_cancel_fails_closed"]=True
            # Seed a *historical read-only plan*, by the original product
            # HTTP /sessions/plan route (like v181), NOT current verified
            # longrun and NOT a made-up installed manifest or worker.
            token=browser.execute_script("return state.token")
            st,defaults=http_json("/api/v1/defaults",token=token)
            need(st==200 and len(defaults["archetypes"])==26,
                 "DEFAULTS_NOT_26")
            chosen=next(row for row in defaults["archetypes"] if
                        row["class"]=="paladin" and row["spec"]=="retribution")
            controls={k:v for k,v in chosen.items()
                      if k!="representative_scope"}
            controls["oil_hands"]=[]
            fake=work/"NO_NATIVE_PASSTHROUGH_SOURCE_ONLY.exe"
            fake.write_bytes(b"V571_TEST_HISTORICAL_PLAN_ONLY_DO_NOT_EXECUTE")
            payload={"controls":controls,"binary":str(fake),
                 "revision":manifest["source_catalog"]["simc_revision"],
                 "user_socket_total":4,"current_season_product":True}
            st,plan=http_json("/api/v1/sessions/plan",token=token,body=payload)
            need(st==200 and plan.get("native_calls")==0 and
                 re.fullmatch(r"[0-9a-f]{20}",plan.get("session_id","")),
                 "HISTORICAL_ZERO_NATIVE_PLAN_BLOCKED")
            sid=plan["session_id"]
            report["historical_plan_session_hash"]=hashlib.sha256(
                sid.encode()).hexdigest()
            report["plan_native_calls"]=0
            need(state_home.is_dir() and
                 (state_home/sid).is_dir(),
                 "HISTORICAL_PLAN_NOT_DURABLE_OUTSIDE_PACKAGE")
            st,inp=http_json("/api/v1/sessions/"+sid+"/inputs",token=token)
            need(st==200 and
                 inp["user"]["target"]["ilevel"]==334 and
                 inp["user"]["character"]["spec"]=="retribution",
                 "SAVED_HISTORICAL_PLAN_INPUTS_INVALID")
            report["session_stored_outside_extracted_zip"]=True
            save()
            browser.quit();browser=None
            stop_cmd(proc);proc=None
            # New process, new browser profile. Same isolated Windows user
            # home outside ZIP. This exercises the normal visible session
            # picker; it must not upgrade a legacy plan to v212 READY.
            proc=launch_easy(root,home,localdata,log)
            browser=actual_chrome()
            WebDriverWait(browser,35).until(lambda d:any(
                x.get_attribute("value")==sid for x in
                d.find_element(By.ID,"recent-session-id").find_elements(
                    By.TAG_NAME,"option")))
            picker=browser.find_element(By.CSS_SELECTOR,
                "details.restore > summary")
            browser.execute_script("arguments[0].scrollIntoView({block:'center'})",
                                   picker)
            picker.click()
            Select(browser.find_element(By.ID,
                "recent-session-id")).select_by_value(sid)
            button=browser.find_element(By.ID,"recent-open-btn")
            browser.execute_script(
                "arguments[0].scrollIntoView({block:'center'})",button)
            button.click()
            WebDriverWait(browser,45).until(lambda d:d.execute_script("""
               return state.session===arguments[0] && !state.busy &&
                 document.getElementById("notice").textContent.includes(
                      "기존 세션·입력 복원 성공");
            """,sid))
            restored=browser_state(browser)
            need(restored["session"]==sid and
                 restored["spec"]=="paladin/retribution" and
                 restored["level"]==334 and not restored["running"],
                 "VISIBLE_HISTORICAL_RESTORE_MISMATCH")
            st,progress=http_json("/api/v1/sessions/"+sid+"/status",
                                  token=browser.execute_script("return state.token"))
            need(st==200 and not progress["active"] and
                 progress["progress"]["native_attempts"]==0,
                 "RESTART_ACCIDENTALLY_STARTED_NATIVE")
            need(restored["verified_build"] is None and
                 restored["gear_target"] is None,
                 "HISTORICAL_PLAN_WRONGLY_PROMOTED_TO_NEW_SEASON")
            report["restart_new_bat_process"]=True
            report["visible_saved_session_restore"]=True
            report["historical_plan_not_promoted_to_verified_season"]=True
            report["status"]="PASS_EXTRACTED_WINDOWS_EASY_START_CHROME_COLD_RESTORE_NATIVE_ZERO"
            save()
            print("V571_WINDOWS_PACKAGE "+json.dumps({
              k:report[k] for k in ("status","archive_file_count",
                "easy_start_check_no_install","cold_visible_first_button",
                "explicit_cancel_fails_closed","visible_saved_session_restore",
                "native_environment_calls","native_dps_calls")},
                ensure_ascii=True,sort_keys=True),flush=True)
            return 0
        except BaseException as exc:
            report["status"]="BLOCKED_OR_PARTIAL_"+type(exc).__name__
            report["error_code"]=safe(exc)
            save()
            raise
        finally:
            if browser:
                try:browser.quit()
                except Exception:pass
            if proc:stop_cmd(proc)
            if log:log.close()

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--zip",required=True,type=pathlib.Path)
    parser.add_argument("--out",required=True,type=pathlib.Path)
    args=parser.parse_args()
    raise SystemExit(run(args.zip,args.out))
