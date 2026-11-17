#!/usr/bin/env python3
"""v572: original extracted Windows ZIP + official pinned SimC + actual
source-owned first-user Build, default primary 64 session, Chrome cancel,
Windows BAT/OS-server restart, new Chrome saved-session restore, resume and
cancel again. Only a few real DPS Native: NOT full 64 search repeat.

Uses the unmodified product localhost HTTP API for every action. No mocked
Build, gear, worker, resume or result. Bounded stop at first native progress.
Source secrets are written only to actual Windows Credential Manager through
the original local API; the child process never inherits CI secret env vars.
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
from selenium.webdriver.support.ui import Select,WebDriverWait
from selenium.webdriver.common.keys import Keys

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner"),str(ROOT/"integration_probes")]
import v289_retail_live_build_source as retail
import v348_windows_user_source_credentials as credential_owner
from p1_v345_windows_extracted_zip_cmd_browser_restore import (
    PREFIX, REV, BUILD, SIMC_SHA, URL, wait_for_http,
    stop_cmd, actual_chrome, http_json, digest)
from p1_v570_real_windows_cold_browser_to_simc_once import (
    navigate,clickable,input_text,wait_idle,
    browser_snapshot,select_trinket,TRINKETS,REQUIRED_SECRETS)
from p1_v344_windows_real_browser_native64_once import choose_visible_search

SCHEMA="p1_v572_windows_zip_real_adaptive_cancel_bat_restart_resume_v1"
NAME="V572_WINDOWS_ZIP_REAL_CANCEL_RESTART_RESUME_COMPACT.json"
MAX_BEFORE_CANCEL=9
MAX_AFTER_RESUME_NEW=9
LONGRUN_BUDGET=64

def need(ok,reason):
    if not ok: raise RuntimeError("V572_"+reason)

def code_only(exc):
    s=str(exc).split("\n",1)[0].split(":",1)[0]
    return s if re.fullmatch(r"V572_[A-Z_0-9]{3,110}",s) else type(exc).__name__

def safe_easy_start(root,home,appdata,log):
    # Do not pass actual API secrets to a server subprocess. Read them
    # exclusively at the test client boundary for the original localhost
    # Windows Credential Manager save endpoint.
    env={k:v for k,v in os.environ.items() if k not in REQUIRED_SECRETS}
    env.update({"HOME":str(home),"USERPROFILE":str(home),
        "LOCALAPPDATA":str(appdata),"PYTHONIOENCODING":"utf-8",
        "PYTHONDONTWRITEBYTECODE":"1"})
    proc=subprocess.Popen(["cmd","/d","/c",
        str(root/"START_HERE_AUTO_SETUP_AND_RUN.bat")],cwd=root,
        env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
    wait_for_http(proc)
    return proc

def build_snapshot(browser):
    return browser.execute_script("""
      const e=window.__v572_environment;
      if(!e)return null;
      return {
        environment_ready:e.environment_ready,
        environment_installed:e.environment_installed,
        normal_build_entry:e.normal_build_entry,
        source_compilation_status:e.source_compilation?.status,
        first_requires:e.zero_history_build?.requires?.[0]||null,
        game_build:e.web_environment_scope?.game_build,
        target_ilevel:e.web_environment_scope?.target_ilevel,
        native_calls:e.native_calls,
        G:e.G,J:e.J,F:e.F,O:e.O,B:e.B,T:e.T,
        installed_sha:
          e.source_compilation?.verified_environment_install?.manifest_sha256||
          e.installed_manifest_sha256||null
      };
    """)

def status(session,token):
    code,document=http_json("/api/v1/sessions/"+session+"/longrun/status",token=token)
    need(code==200 and document.get("enabled") is True,
         "REAL_LOCAL_HTTP_LONGRUN_STATUS_UNAVAILABLE")
    return document

def poll_after_state(sid,token,accept,seconds=80):
    deadline=time.monotonic()+seconds
    last=None
    while time.monotonic()<deadline:
        last=status(sid,token)
        if accept(last):return last
        time.sleep(.17)
    raise RuntimeError("V572_LONGRUN_STATE_WAIT_TIMEOUT")

def native_sha_summary(stage):
    files={}
    for field,basename in [
        ("inputs","input.simc"),("json2","result.json"),
        ("native_receipts","native_receipt.json")]:
        files[field]=sorted(stage.glob("cases/case_*/native/"+basename))
    count=len(files["inputs"])
    need(count==len(files["json2"])==len(files["native_receipts"]),
         "REAL_NATIVE_TRIPLET_COUNT_DRIFT")
    return {
        "count":count,
        "input_sha":[digest(f) for f in files["inputs"]],
        "json2_sha":[digest(f) for f in files["json2"]],
        "receipt_sha":[digest(f) for f in files["native_receipts"]]
    }

def run(source_zip,simc,out):
    need(sys.platform=="win32","WINDOWS_ONLY")
    out=pathlib.Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    archive=pathlib.Path(source_zip).resolve(strict=True)
    binary=pathlib.Path(simc).resolve(strict=True)
    receipt=out/NAME
    report={"schema":SCHEMA,"status":"STARTED","platform":"windows-2022",
      "verified_product_zip":False,"real_extracted_bat":False,
      "real_chrome":False,"mocked_api_or_native":False,
      "user_pc_installed":False,"new_source_build":False,
      "actual_v212_installed":False,"real_primary_64_started":False,
      "browser_user_cancelled":False,"restarted_real_bat":False,
      "browser_restored_saved_real_longrun":False,
      "browser_resumed_real_longrun":False,
      "new_environment_native":0,"new_dps_native":0,
      "official_budget":{"G":None,"J":None,"F":None,"O":None,"B":None,"T":None},
      "confirmed_result_95":False,"global_optimum_proven":False,
      "official_completion_contract_changed":False,
      "source_credentials_clear_status":"NOT_SAVED",
      "test_trinkets":list(TRINKETS)}
    def save():
        receipt.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,
            allow_nan=False,indent=2,default=str)+"\n",encoding="utf8")
    save()
    browser=proc=log=None
    creds_saved=False
    token=None
    sid=None
    root=None
    try:
        need(binary.name.lower()=="simc.exe" and
             digest(binary)==SIMC_SHA,"SAME_BUILD_OFFICIAL_SIMC_SHA_REQUIRED")
        need(os.environ.get("SIMC_PINNED_SOURCE_COMMIT")==REV and
             os.environ.get("SIMC_PINNED_GAME_BUILD")==BUILD,
             "PINNED_GAME_BUILD_REVISION_REQUIRED")
        need(all(os.environ.get(k) for k in REQUIRED_SECRETS),
             "SOURCE_CREDENTIALS_REQUIRED")
        discovered=retail.discover(region="KR")
        report["live_game_build"]=discovered.get("game_build")
        report["live_source_sha256"]=discovered.get("source_sha256")
        if discovered.get("game_build")!=BUILD:
            report["status"]="PENDING_EXACT_LIVE_BUILD_SIMC_REPLACEMENT"
            report["first_blocker"]="LIVE_GAME_BUILD_NOT_PINNED_SIMC"
            save()
            return 2
        observed_banner=subprocess.run([str(binary)],input="",
            capture_output=True,text=True,errors="replace",
            cwd=binary.parent,timeout=25)
        need(observed_banner.returncode==0 and BUILD in observed_banner.stdout,
             "ACTUAL_SIMC_BANNER_BUILD_MISMATCH")
        with tempfile.TemporaryDirectory(prefix="v572-win-zip-",dir=out) as work:
            work=pathlib.Path(work)
            home=work/"user-home";home.mkdir()
            appdata=work/"localappdata";appdata.mkdir()
            with zipfile.ZipFile(archive) as z:
                paths=z.namelist()
                need(paths and len(paths)==len(set(paths)) and all(
                    n.startswith(PREFIX+"/") and
                    ".." not in pathlib.PurePosixPath(n).parts
                    for n in paths),"SOURCE_ZIP_PATH_INVALID")
                manifest=json.loads(z.read(PREFIX+"/V181_PACKAGE_MANIFEST.json"))
                members=manifest["files"]
                need(manifest["archive_root"]==PREFIX and
                     len(members)==manifest["file_count"] and
                     len(members)>=75 and
                     not manifest["native_executable_bundled"] and
                     not manifest["sessions_bundled"] and
                     not manifest["historical_native_json2_bundled"],
                     "SOURCE_ZIP_CONTRACT_DRIFT")
                for item in members:
                    raw=z.read(PREFIX+"/"+item["path"])
                    need(len(raw)==item["size"] and
                         hashlib.sha256(raw).hexdigest()==item["sha256"],
                         "EXACT_PACKAGE_MEMBER_SHA_DRIFT")
                exact=("runner/webui/app.js",
                     "runner/v113_local_web_api.py",
                     "runner/v216_environment_build_coordinator.py",
                     "runner/v212_environment_manifest.py",
                     "runner/v293_local_longrun_session.py",
                     "START_HERE_AUTO_SETUP_AND_RUN.bat")
                for path in exact:
                    need(hashlib.sha256(z.read(PREFIX+"/"+path)).hexdigest()==
                         digest(ROOT/path),"PACKAGE_NOT_EXACT_CURRENT_SOURCE")
                need(not any(x.lower().endswith((".exe",".dll",".pfx",".pem",
                    ".key")) for x in paths),"BINARY_OR_SECRET_BUNDLED")
                z.extractall(work)
            root=work/PREFIX
            report["verified_product_zip"]=True
            report["source_zip_sha256"]=digest(archive)
            report["package_file_count"]=len(members)
            # Prepared user-local Python matches v571: not a first install of
            # Python/requirements. Do not silently invoke pip or winget.
            venv_dir=appdata/"SIMC_Secondary_Optimizer"/"web-python"
            venv.create(str(venv_dir),system_site_packages=True,with_pip=False)
            venv_python=venv_dir/"Scripts"/"python.exe"
            check=subprocess.run([str(venv_python),"-c",
                "import fastapi,uvicorn; print('READY')"],capture_output=True,
                text=True,timeout=25)
            need(check.returncode==0 and "READY" in check.stdout,
                 "USER_VENV_REUSE_UNAVAILABLE")
            log=(out/"V572_WINDOWS_EXTRACTED_APP_LOG.txt").open(
                "w",encoding="utf8")
            proc=safe_easy_start(root,home,appdata,log)
            report["real_extracted_bat"]=True
            browser=actual_chrome()
            report["real_chrome"]=True
            token=browser.execute_script("return state.token")
            st,auth_status=http_json("/api/v1/source-credentials/status",
                token=token)
            need(st==200 and auth_status.get("supported") is True and
                 auth_status.get("storage")=="WINDOWS_CREDENTIAL_MANAGER" and
                 auth_status.get("configured") is False,
                 "ISOLATED_WINDOWS_CREDENTIAL_STORE_NOT_EMPTY")
            # Explicit local consent. No secret material into receipts.
            key_map={
               "blizzard_client_id":os.environ["BLIZZARD_CLIENT_ID"],
               "blizzard_client_secret":os.environ["BLIZZARD_CLIENT_SECRET"],
               "wcl_client_id":os.environ["WCL_CLIENT_ID"],
               "wcl_client_secret":os.environ["WCL_CLIENT_SECRET"]}
            st,confirmation=http_json("/api/v1/source-credentials/save",
                token=token,body=key_map)
            need(st==200 and confirmation.get("configured") is True,
                 "REAL_WINDOWS_SOURCE_CREDENTIAL_SAVE_FAILED")
            creds_saved=True
            report["source_credentials_clear_status"]="PENDING_CLEANUP"
            save()
            browser.execute_script("""
               window.confirm=()=>true;window.__v572_environment=null;
               const old=showSeasonEnvironmentBuild;
               showSeasonEnvironmentBuild=function(data,variant){
                 window.__v572_environment=data;
                 return old(data,variant);
               };
            """)
            choose_visible_search(browser,"class-choice","사냥꾼","사냥꾼")
            choose_visible_search(browser,"spec","생존","생존")
            oil=browser.find_element(By.ID,"optimizer-oil-enabled")
            if oil.is_selected():clickable(browser,oil)
            navigate(browser,"settings")
            technical=browser.find_element(By.ID,"simc-technical-panel")
            if not technical.get_attribute("open"):
                clickable(browser,technical.find_element(By.TAG_NAME,"summary"))
            input_text(browser,"binary",str(binary))
            input_text(browser,"revision",REV)
            browser.find_element(By.ID,"revision").send_keys(Keys.TAB)
            wait_idle(browser,50)
            navigate(browser,"optimizer")
            initial=browser_snapshot(browser)
            need(not initial["start_disabled"] and
                 initial["start_label"]=="시즌 환경 준비 · 장신구 목록 불러오기" and
                 not initial["sid"],"EXTRACTED_FIRST_USER_BUTTON_NOT_READY")
            clickable(browser,browser.find_element(By.ID,"start-btn"))
            wait_idle(browser,1650)
            environment=build_snapshot(browser)
            need(type(environment) is dict,
                 "ORIGINAL_PACKAGE_ENVIRONMENT_RESPONSE_MISSING")
            report["new_environment_native"]=environment.get("native_calls")
            if not (environment["environment_ready"] is True and
                    environment["environment_installed"] is True):
                report["status"]="PENDING_REAL_PACKAGE_SEASON_BUILD"
                report["first_blocker"]=environment["first_requires"] or (
                    environment["source_compilation_status"] or "UNKNOWN")
                save()
                return 2
            now=browser_snapshot(browser)
            install=environment["installed_sha"]
            need(re.fullmatch(r"[a-f0-9]{64}",install or "") is not None and
                 now["gear_sha"]==install and
                 now["build"]==environment["game_build"]==BUILD and
                 now["ilvl"]==now["gear_level"]==
                        environment["target_ilevel"]==334 and
                 environment["G"]==2850 and environment["J"]==92 and
                 environment["F"]==165 and
                 environment["B"]==environment["T"]==3107 and
                 sum(environment["O"].values())==0 and
                 type(environment["native_calls"]) is int and
                 0<=environment["native_calls"]<=6,
                 "EXTRACTED_REAL_V212_BUDGET_OR_SHA_DRIFT")
            report["new_source_build"]=True
            report["actual_v212_installed"]=True
            report["installed_manifest_sha256"]=install
            report["official_budget"]={k:environment[k]
                for k in ("G","J","F","O","B","T")}
            save()
            # Same actual installed source-bound card chooser as v570.
            for value in dict.fromkeys(filter(None,now["trinkets"])):
                select_trinket(browser,int(value))
            need(browser_snapshot(browser)["trinkets"]==["",""],
                 "HISTORICAL_TRINKETS_REMAIN_SELECTED")
            for item in TRINKETS:
                select_trinket(browser,item)
            chosen=browser_snapshot(browser)
            need(chosen["trinkets"]==list(map(str,TRINKETS)) and
                 not chosen["start_disabled"] and
                 chosen["start_label"]=="최적 스탯 찾기",
                 "TWO_SOURCE_BOUND_TRINKETS_NOT_SELECTED")
            # Original primary button. Native bounded via real Chrome cancel
            # as soon as the first complete actual candidate is observed.
            clicked=browser.execute_script("""
                const v=buildRequest();
                return {sha:v.installed_manifest_sha256,
                  build:v.installed_season_game_build,
                  trinkets:v.controls.trinket_ids,
                  user_product:v.current_season_product};
            """)
            need(clicked["sha"]==install and clicked["build"]==BUILD and
                 clicked["trinkets"]==list(TRINKETS) and
                 clicked["user_product"] is True,
                 "EXACT_PRIMARY_BROWSER_REQUEST_SHA_MISMATCH")
            clickable(browser,browser.find_element(By.ID,"start-btn"))
            sid=WebDriverWait(browser,90).until(lambda d:d.execute_script(
                "return /^[a-f0-9]{20}$/.test(state.session||'') ? state.session : null"))
            folder=home/"SIMC_Secondary_Optimizer"/"runs"/sid
            need(folder.is_dir(),"NATIVE_SESSION_NOT_IN_ISOLATED_USER_HOME")
            config=json.loads((folder/"V293_LONGRUN_CONFIG.json").read_text("utf8"))
            need(config["native_budget"]==LONGRUN_BUDGET and
                 config["scout_iterations"]==56,
                 "PRIMARY_64_N56_NOT_PRODUCT_DEFAULT")
            report["real_primary_64_started"]=True
            report["session_id_hash"]=hashlib.sha256(sid.encode()).hexdigest()
            save()
            before=None
            deadline=time.monotonic()+130
            while time.monotonic()<deadline:
                before=status(sid,token)
                attempts=before["progress"]["native_attempts"]
                if attempts>=1:break
                time.sleep(.12)
            need(before and before["progress"]["native_attempts"]>=1 and
                 before["active"] is True and
                 before["progress"]["native_attempts"]<=MAX_BEFORE_CANCEL,
                 "PRIMARY_DID_NOT_REACH_BOUNDED_NATIVE_CANCEL_WINDOW")
            WebDriverWait(browser,20).until(lambda d:
                d.find_element(By.ID,"cancel-btn").is_enabled())
            clickable(browser,browser.find_element(By.ID,"cancel-btn"))
            stopped=poll_after_state(sid,token,
                lambda d: not d["active"] and
                    d["progress"]["worker"].get("status")==
                       "PAUSED_USER_CANCEL",seconds=180)
            n0=stopped["progress"]["native_attempts"]
            need(1<=n0<=MAX_BEFORE_CANCEL and
                 not stopped["result_ready"] and
                 stopped["cancel_requested"] is True,
                 "PAUSED_SESSION_NOT_BOUNDED_OR_UNCONFIRMED")
            stage=folder/"generated"/"v291_longrun_64"/"simc_results"
            first_triplets=native_sha_summary(stage)
            need(first_triplets["count"]==n0,
                 "FIRST_PAUSED_NATIVE_COUNT_VS_TRIPLETS")
            report["first_pause_native_attempts"]=n0
            report["first_pause_worker"]=stopped["progress"]["worker"]["status"]
            report["browser_user_cancelled"]=True
            report["new_dps_native"]=n0
            save()
            browser.quit();browser=None
            stop_cmd(proc);proc=None
            proc=safe_easy_start(root,home,appdata,log)
            browser=actual_chrome()
            token=browser.execute_script("return state.token")
            initial_restarted=browser_snapshot(browser)
            need(not initial_restarted["sid"] and
                 browser.find_element(By.ID,"results-nav-btn").is_displayed(),
                 "SAVED_SESSION_RESULT_TAB_HIDDEN_AFTER_BAT_RESTART")
            clickable(browser,browser.find_element(By.ID,"results-nav-btn"))
            WebDriverWait(browser,20).until(
                lambda d:d.find_element(By.ID,"view-results").is_displayed())
            WebDriverWait(browser,35).until(lambda d:any(
               x.get_attribute("value")==sid for x in
               d.find_element(By.ID,"recent-session-id").find_elements(
                  By.TAG_NAME,"option")))
            summary=browser.find_element(By.CSS_SELECTOR,
                  "details.restore > summary")
            clickable(browser,summary)
            Select(browser.find_element(By.ID,
                  "recent-session-id")).select_by_value(sid)
            clickable(browser,browser.find_element(By.ID,"recent-open-btn"))
            WebDriverWait(browser,60).until(lambda d:d.execute_script("""
              return state.session===arguments[0] && !state.busy &&
                state.longrunEnabled && !state.running &&
                document.getElementById("run-label").textContent.includes(
                    "취소");
            """,sid))
            resumed_pre=status(sid,token)
            need(resumed_pre["progress"]["native_attempts"]==n0 and
                 resumed_pre["progress"]["worker"]["status"]=="PAUSED_USER_CANCEL"
                 and not resumed_pre["active"] and
                 native_sha_summary(stage)==first_triplets,
                 "RESTART_ALREADY_RECOMPUTED_OR_CHANGED_PAUSED_NATIVE")
            report["restarted_real_bat"]=True
            report["browser_restored_saved_real_longrun"]=True
            save()
            # User-visible main Resume (continuous); stop immediately after
            # one additional real candidate to avoid repeating all 64. This
            # intentionally does not pretend a full 64-case result exists.
            browser.execute_script("window.confirm=()=>true")
            need(browser.find_element(By.ID,"resume-btn").is_enabled(),
                 "RESTORED_LONGRUN_RESUME_BUTTON_DISABLED")
            clickable(browser,browser.find_element(By.ID,"resume-btn"))
            begun=poll_after_state(sid,token,lambda d:d["active"],seconds=35)
            need(begun["native_budget"]==LONGRUN_BUDGET,
                 "RESUME_BUDGET_CHANGED")
            after=None
            deadline=time.monotonic()+140
            while time.monotonic()<deadline:
                after=status(sid,token)
                if after["progress"]["native_attempts"]>n0:break
                time.sleep(.12)
            need(after and after["progress"]["native_attempts"]>n0 and
                 after["active"] and
                 after["progress"]["native_attempts"]<=n0+MAX_AFTER_RESUME_NEW,
                 "RESUMED_NATIVE_NOT_BOUNDED_BEFORE_SECOND_CANCEL")
            WebDriverWait(browser,20).until(
                lambda d:d.find_element(By.ID,"cancel-btn").is_enabled())
            clickable(browser,browser.find_element(By.ID,"cancel-btn"))
            again=poll_after_state(sid,token,lambda d:not d["active"] and
                d["progress"]["worker"].get("status")=="PAUSED_USER_CANCEL",seconds=160)
            n1=again["progress"]["native_attempts"]
            need(n0<n1<=n0+MAX_AFTER_RESUME_NEW and
                 n1<LONGRUN_BUDGET and not again["result_ready"],
                 "RESUMED_CANDIDATES_NOT_BOUNDED")
            second_triplets=native_sha_summary(stage)
            need(second_triplets["count"]==n1 and
                 all(second_triplets[key][:n0]==first_triplets[key]
                     for key in ("input_sha","json2_sha","receipt_sha")),
                 "RESTORED_PRIOR_SHA_CHANGED_OR_DUPLICATE_NATIVE")
            report["browser_resumed_real_longrun"]=True
            report["resume_new_native"]=n1-n0
            report["new_dps_native"]=n1
            report["session_native_cumulative"]=n1
            report["resume_kept_existing_native_triplet_sha"]=True
            report["final_worker_status"]=again["progress"]["worker"]["status"]
            report["status"]="PASS_EXTRACTED_WINDOWS_ZIP_REAL_NATIVE_CANCEL_RESTART_RESUME_PARTIAL"
            save()
            print("V572_WINDOWS_ZIP_REAL_RESUME "+
                 json.dumps({k:report[k] for k in (
                    "status","new_environment_native","new_dps_native",
                    "first_pause_native_attempts","resume_new_native",
                    "resume_kept_existing_native_triplet_sha",
                    "real_extracted_bat","actual_v212_installed")},
                    sort_keys=True,ensure_ascii=True),flush=True)
            return 0
    except Exception as exc:
        report["status"]="BLOCKED_OR_PARTIAL_REAL_PACKAGE_PATH"
        report["first_blocker"]=code_only(exc)
        report["error_type"]=type(exc).__name__
        save()
        return 2
    finally:
        if creds_saved:
            # Use the same original Windows Cred Manager owner directly,
            # including if the packaged server already exited unexpectedly.
            # This target was verified empty before the test wrote to it.
            try:
                store=credential_owner.WindowsSourceCredentialStore()
                cleared=store.clear()
                report["source_credentials_clear_status"]=(
                    "CLEARED" if cleared.get("deleted") is True and
                    store.status().get("configured") is False
                    else "CLEANUP_FAILED")
            except Exception:
                report["source_credentials_clear_status"]="CLEANUP_FAILED"
            save()
        if browser:
            try:browser.quit()
            except Exception:pass
        if proc:
            try:stop_cmd(proc)
            except Exception:pass
        if log:log.close()
        print("V572_WINDOWS_ZIP_VERDICT "+
            json.dumps({k:report.get(k) for k in (
                "status","first_blocker","live_game_build",
                "new_environment_native","new_dps_native",
                "first_pause_native_attempts","resume_new_native",
                "source_credentials_clear_status")},
                sort_keys=True,ensure_ascii=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--zip",type=pathlib.Path,required=True)
    p.add_argument("--simc",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    a=p.parse_args()
    raise SystemExit(run(a.zip,a.simc,a.out))
