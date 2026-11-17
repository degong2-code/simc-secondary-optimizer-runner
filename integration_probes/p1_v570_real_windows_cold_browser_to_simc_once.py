#!/usr/bin/env python3
"""v570: one real Windows cold UI -> real v113/v216/v212 Build -> installed
trinket cards -> original 64-case adaptive SimC -> visible DPS/SEM/95%.

No synthetic/fake fetch, no seeded catalogue, no preinstalled v212 manifest,
no prior DPS cache, no manually registered environment. Only test-user input
and real official same-build SimC binary are supplied. This is one bounded
Native product-integration test, not 26-specialization coverage.
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
import threading
import time
from urllib.request import urlopen

import uvicorn
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner"),str(ROOT/"integration_probes")]
import v113_local_web_api as web
import v293_local_longrun_session as longrun
import v289_retail_live_build_source as retail
from integration_probes.p1_v344_windows_real_browser_native64_once import (
    choose_visible_search,sha)

PORT=8794
URL=f"http://127.0.0.1:{PORT}/"
REV="de11f57df75dda668bae6ac7043a43b98831fa96"
BUILD="12.1.5.70783"
SIMC_SHA="1fc927d2be7f1b6064c75f004b5b22245b064a6b3e56e572af4048ba822a986d"
SCHEMA="p1_v570_windows_actual_cold_browser_build_installed_dps64_v1"
TRINKETS=(270175,270173)
REQUIRED_SECRETS=("BLIZZARD_CLIENT_ID","BLIZZARD_CLIENT_SECRET",
    "WCL_CLIENT_ID","WCL_CLIENT_SECRET")

class SourceCredentials:
    def load(self):
        values={key:os.environ.get(key,"") for key in REQUIRED_SECRETS}
        return values if all(values.values()) else None

    def status(self):
        # v570 CI-only environment adapter, not the user's Windows key store.
        # Product bootstrap queries this read-only route before the Build;
        # never surface secret values or invoke a network/source operation.
        return {"supported":True,"configured":self.load() is not None}

def need(ok,code):
    if not ok:raise RuntimeError("V570_"+code)

def code_only(exc):
    code=str(exc).split("\n",1)[0].split(":",1)[0]
    return code if re.fullmatch(r"[A-Z][A-Z0-9_]{3,120}",code) else type(exc).__name__

def start_server(root):
    app=web.create_app(root=root,source_credential_store=SourceCredentials())
    config=uvicorn.Config(app,host="127.0.0.1",port=PORT,
        access_log=False,proxy_headers=False,log_level="error")
    server=uvicorn.Server(config)
    thread=threading.Thread(target=server.run,daemon=True)
    thread.start()
    for _ in range(220):
        need(thread.is_alive(),"HTTP_SERVER_EXITED")
        if server.started:
            try:
                with urlopen(URL+"api/v1/health",timeout=2) as response:
                    if response.status==200:return app,server,thread
            except OSError:pass
        time.sleep(.1)
    raise RuntimeError("V570_HTTP_SERVER_TIMEOUT")

def stop_server(server,thread):
    if server:
        server.should_exit=True
        thread.join(timeout=25)
        need(not thread.is_alive(),"HTTP_SERVER_NOT_STOPPED")

def chrome():
    options=Options()
    for flag in ("--headless=new","--no-sandbox",
                 "--disable-dev-shm-usage","--window-size=1440,950"):
        options.add_argument(flag)
    browser=webdriver.Chrome(options=options)
    browser.get(URL)
    WebDriverWait(browser,60).until(lambda d:d.execute_script(
      "return !!state.token && state.defaults.length===26 && "+
      "!state.busy && document.getElementById('start-btn').textContent.includes('시즌 환경 준비')"))
    return browser

def navigate(browser,view):
    if browser.execute_script("return document.querySelector('.top-nav button.is-active')?.dataset.view")==view:
        return
    browser.find_element(By.CSS_SELECTOR,
        'header.topbar button[data-view="'+view+'"]').click()
    WebDriverWait(browser,20).until(lambda d:d.execute_script(
        "return document.querySelector('.top-nav button.is-active')?.dataset.view===arguments[0]",
        view))

def clickable(browser,element):
    browser.execute_script(
        "arguments[0].scrollIntoView({block:'center',behavior:'instant'})",element)
    WebDriverWait(browser,20).until(lambda d:d.execute_script("""
        const n=arguments[0],r=n.getBoundingClientRect();
        const top=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);
        return !n.disabled&&r.top>=0&&r.bottom<=innerHeight &&
            (top===n||n.contains(top));
    """,element))
    element.click()

def input_text(browser,ident,value):
    node=browser.find_element(By.ID,ident)
    need(node.is_displayed(),"INPUT_NOT_VISIBLE_"+ident.replace("-","_").upper())
    node.clear()
    node.send_keys(str(value))
    need(node.get_attribute("value")==str(value),"FORM_INPUT_NOT_SET_"+ident.upper())

def wait_idle(browser,timeout=650):
    WebDriverWait(browser,timeout,poll_frequency=.5).until(
        lambda d:d.execute_script("return !state.busy"))

def browser_snapshot(browser):
    return browser.execute_script("""
      return {
        token_present:!!state.token,spec:field("spec"),race:field("race"),
        build:state.verifiedInstalledBuildFromThisPage,
        ilvl:Number(field("ilevel")),
        gear_sha:state.seasonGear?.installed_manifest_sha256||null,
        gear_level:state.seasonGearTargetIlevel,
        trinkets:[field("trinket1"),field("trinket2")],
        start_disabled:document.getElementById("start-btn").disabled,
        start_label:document.getElementById("start-btn").textContent,
        environment_state:document.getElementById("optimizer-environment-state").textContent,
        notice:document.getElementById("notice").textContent,
        sid:state.session,result_visible:!document.getElementById("filled-result").hidden,
        dps:document.getElementById("dps").textContent,
        sem:document.getElementById("sem").textContent,
        conf95:document.getElementById("conf95").textContent
      };
    """)

def select_trinket(browser,physical_id):
    ident=str(physical_id)
    search=browser.find_element(By.ID,"equipment-trinket-search")
    search.clear();search.send_keys(ident)
    element=WebDriverWait(browser,15).until(
        lambda d:d.find_element(By.CSS_SELECTOR,
          '#equipment-trinket-grid button[data-item-id="'+ident+'"]'))
    clickable(browser,element)
    search.clear()

def run(binary,output):
    need(sys.platform=="win32","WINDOWS_ONLY")
    output=pathlib.Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    binary=pathlib.Path(binary).resolve(strict=True)
    report={"schema":SCHEMA,"status":"STARTED","platform":"windows-2022",
        "actual_chrome":False,"http_synthetic":False,
        "actual_original_v216_build":False,"actual_v212_install":False,
        "actual_simc_native":False,"test_user_trinket_ids":list(TRINKETS),
        "expected_revision":REV,"expected_game_build":BUILD,
        "fresh_root_before_build":False,"new_environment_native":None,
        "new_dps_native":None,"global_optimum_proven":False,
        "official_78_complete_not_modified":True,
        "real_personal_pc_installation_proven":False}
    receipt=output/"V570_REAL_WINDOWS_FIRST_USER_PRODUCT.json"
    def save():
        receipt.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,
          allow_nan=False,indent=2,default=str)+"\n",encoding="utf8")
    save()
    app=server=thread=browser=None
    sid=None
    root=None
    try:
        need(binary.name.lower()=="simc.exe" and sha(binary)==SIMC_SHA,
             "PINNED_WINDOWS_SIMC_IDENTITY_INVALID")
        need(os.environ.get("SIMC_PINNED_SOURCE_COMMIT")==REV and
             os.environ.get("SIMC_PINNED_GAME_BUILD")==BUILD,
             "PINNED_SOURCE_IDENTITY_INVALID")
        need(SourceCredentials().load() is not None,
             "REQUIRED_SEASON_CREDENTIALS_MISSING")
        actual=retail.discover(region="KR")
        report["actual_live_build"]=actual.get("game_build")
        report["actual_live_source_sha256"]=actual.get("source_sha256")
        if actual.get("game_build")!=BUILD:
            report["status"]="PENDING_SAME_BUILD_SIMC_FOR_NEW_LIVE_RETAIL"
            report["first_blocker"]="LIVE_BUILD_NOT_CURRENT_PINNED_SIMC_BUILD"
            save()
            return 2
        actual_cli=subprocess.run([str(binary)],input="",capture_output=True,
            text=True,errors="replace",timeout=25,cwd=binary.parent)
        need(actual_cli.returncode==0 and BUILD in actual_cli.stdout,
             "SIMC_EXE_GAME_BUILD_BANNER_MISMATCH")
        # Same v552 genuinely cold season proof; NO historical fallback data.
        old=ROOT/"data"
        prohibited=list(old.glob("current_season_*.json"))
        prohibited+=list((old/"season_ordinary_gem_nominal").glob("*.json"))
        prohibited+=list(old.glob("v202_*.json"))
        prohibited+=list(old.glob("v206_*.json"))
        need(not prohibited,"HISTORICAL_SEASON_INPUTS_NOT_QUARANTINED")
        with tempfile.TemporaryDirectory(prefix="v570-cold-",dir=output) as temp:
            root=pathlib.Path(temp)/"runs";root.mkdir()
            need(not list(root.iterdir()),"FIRST_USER_ROOT_NOT_EMPTY")
            report["fresh_root_before_build"]=True
            app,server,thread=start_server(root)
            browser=chrome()
            report["actual_chrome"]=True
            browser.execute_script("""
              window.confirm=()=>true;window.__v570_environment=null;
              const original=showSeasonEnvironmentBuild;
              showSeasonEnvironmentBuild=function(data,variant){
                window.__v570_environment=data;
                return original(data,variant);
              };
            """)
            # The user fills the visible specialization/SimC controls; the
            # season build, exact gear and DPS routes remain unmodified HTTP.
            choose_visible_search(browser,"class-choice","사냥꾼","사냥꾼")
            choose_visible_search(browser,"spec","생존","생존")
            need(browser.execute_script("return field('spec')")==
                 "hunter/survival","VISIBLE_USER_SPEC_SELECTION_FAILED")
            oil=browser.find_element(By.ID,"optimizer-oil-enabled")
            if oil.is_selected():clickable(browser,oil)
            navigate(browser,"settings")
            tech=browser.find_element(By.ID,"simc-technical-panel")
            if not tech.get_attribute("open"):
                clickable(browser,tech.find_element(By.TAG_NAME,"summary"))
            input_text(browser,"binary",str(binary))
            input_text(browser,"revision",REV)
            browser.find_element(By.ID,"revision").send_keys(Keys.TAB)
            wait_idle(browser,50)
            navigate(browser,"optimizer")
            first=browser_snapshot(browser)
            need(first["start_label"]=="시즌 환경 준비 · 장신구 목록 불러오기"
                 and not first["start_disabled"] and first["gear_sha"] is None,
                 "COLD_BUTTON_SOURCE_BEFORE_FIRST_USER_CLICK")
            report["first_user_start_button_ready"]=True
            save()
            # This is the unmodified v568 product button handler. It requests
            # current Myth ilvl, then POST /environment/season-build and GET
            # exact installed SHA /season-gear. No app.state short circuit.
            clickable(browser,browser.find_element(By.ID,"start-btn"))
            wait_idle(browser,1600)
            data=browser.execute_script("""
              const e=window.__v570_environment;
              if(!e)return null;
              return {normal_build_entry:e.normal_build_entry,
                environment_ready:e.environment_ready,
                environment_installed:e.environment_installed,
                source_compilation_status:e.source_compilation?.status,
                stage_requires:e.zero_history_build?.requires||[],
                G:e.G,J:e.J,F:e.F,O:e.O,B:e.B,T:e.T,
                native_calls:e.native_calls,
                installed_manifest_sha256:
                  e.source_compilation?.verified_environment_install?.manifest_sha256 ||
                  e.installed_manifest_sha256 || null,
                source_catalog_path_present:
                  !!e.source_compilation?.source_catalog_path,
                game_build:e.web_environment_scope?.game_build,
                target_ilevel:e.web_environment_scope?.target_ilevel};
            """)
            report["browser_original_build"] = data
            profile=app.state.jobs._verified_fresh_profile_result
            visible=browser_snapshot(browser)
            report["after_build_browser"]={k:visible[k] for k in (
                "build","ilvl","gear_sha","gear_level","start_label",
                "environment_state","spec","trinkets","start_disabled")}
            need(type(data) is dict,"PRODUCT_UI_ORIGINAL_BUILD_REPORT_MISSING")
            report["new_environment_native"]=data.get("native_calls")
            if not(data.get("environment_ready") is True and
                   data.get("environment_installed") is True):
                report["status"]="PENDING_ORIGINAL_SOURCE_ENVIRONMENT"
                report["first_blocker"]=str((data.get("stage_requires") or
                    [data.get("source_compilation_status") or "UNKNOWN"])[0])[:120]
                save()
                return 2
            manifest=data["installed_manifest_sha256"]
            need(re.fullmatch(r"[a-f0-9]{64}",manifest or "") is not None and
                 type(profile) is dict and
                 visible["gear_sha"]==manifest and
                 visible["gear_level"]==data["target_ilevel"] and
                 visible["build"]==data["game_build"] and
                 visible["ilvl"]==data["target_ilevel"],
                 "REAL_BUILD_INSTALLED_GEAR_SAME_SHA_BRIDGE_REQUIRED")
            need(data["G"]==2850 and data["J"]==92 and data["F"]==165 and
                 data["B"]==3107 and data["T"]==3107 and
                 isinstance(data["O"],dict) and
                 sum(data["O"].values())==0,
                 "REAL_70783_GJFO_B_T_IDENTITY_DRIFT")
            need(type(data.get("native_calls")) is int and
                 0<=data["native_calls"]<=6,
                 "UNEXPECTED_ENVIRONMENT_NATIVE_COST")
            report["actual_original_v216_build"]=True
            report["actual_v212_install"]=True
            report["manifest_sha256"]=manifest
            report["verified_GJFO_B_T"]={k:data[k]
                for k in ("G","J","F","O","B","T")}
            save()
            # Reset selections by real clicks if defaults were retained.
            navigate(browser,"optimizer")
            current=browser_snapshot(browser)["trinkets"]
            for ident in dict.fromkeys(filter(None,current)):
                select_trinket(browser,int(ident))
            need(browser_snapshot(browser)["trinkets"]==["",""],
                 "OLD_DEFAULT_TRINKETS_NOT_CLEARED")
            for physical in TRINKETS:
                select_trinket(browser,physical)
            chosen=browser_snapshot(browser)
            need(chosen["trinkets"]==list(map(str,TRINKETS)) and
                 chosen["gear_sha"]==manifest and
                 chosen["start_label"]=="최적 스탯 찾기" and
                 not chosen["start_disabled"],
                 "TWO_REAL_TRINKET_CLICKS_NOT_READY")
            exact=browser.execute_script("""
              const request=buildRequest();
              return {installed_sha:request.installed_manifest_sha256,
                game_build:request.installed_season_game_build,
                trinkets:request.controls.trinket_ids,
                oil_hands:request.controls.oil_hands,
                target_ilevel:request.controls.ilevel,
                final_T:request.controls.final_T,
                binary:request.binary,
                current_season_product:request.current_season_product};
            """)
            need(exact["installed_sha"]==manifest and
                 exact["trinkets"]==list(TRINKETS) and
                 exact["oil_hands"]==[] and
                 exact["target_ilevel"]==data["target_ilevel"] and
                 exact["final_T"] is None and
                 exact["binary"]==str(binary) and
                 exact["current_season_product"] is True,
                 "PRODUCT_UI_EXACT_SELECTED_DPS_REQUEST_INVALID")
            report["user_controls_source_sha_bound"]=True
            save()
            # Second separate real click launches ORIGINAL 64-case adaptive
            # longrun, not injected six-case plan, custom worker or JS mock.
            clickable(browser,browser.find_element(By.ID,"start-btn"))
            sid=WebDriverWait(browser,90).until(lambda d:d.execute_script(
              "return /^[a-f0-9]{20}$/.test(state.session||'') ? state.session : null"))
            report["session_id_hash"]=hashlib.sha256(sid.encode()).hexdigest()
            folder=root/sid
            need(longrun.config(folder)["native_budget"]==64,
                 "ORIGINAL_UI_ADAPTIVE_64_SEALED_SESSION_NOT_CREATED")
            report["actual_simc_native"]=True
            save()
            child=app.state.jobs.children[sid]
            exitcode=child.wait(timeout=1250)
            report["DPS_worker_exit"]=exitcode
            need(exitcode==0,"ACTUAL_LONGRUN_WORKER_NONZERO_EXIT")
            outcome=app.state.jobs.longrun_status(folder)
            result=longrun.read_result(folder)
            user=result["user_result"]
            first=user["observed_first_choice"]
            n=result["native_calls_cumulative"]
            need(outcome["result_ready"] and
                 user["confidence_level"]==0.95 and
                 user["global_optimum_proven"] is False and
                 user["final_T"]==data["T"] and
                 sum(first["absolute_rating_T"].values())==data["T"] and
                 first["observed_dps_mean"]>0 and
                 first["simc_sem"]>=0 and
                 0<n<=64,
                 "ACTUAL_DPS_SEM_95_OR_BUDGET_INVALID")
            report["new_dps_native"]=n
            report["result_summary"]={
                "observed_first_absolute_rating_T":first["absolute_rating_T"],
                "observed_dps":first["observed_dps_mean"],
                "simc_sem":first["simc_sem"],
                "confidence_level":user["confidence_level"],
                "global_optimum_proven":user["global_optimum_proven"],
                "material_near_alternatives_count":
                    len(user.get("material_near_alternatives") or [])}
            # Observe browser's unmodified polling/rendering of actual
            # HTTP result: do not synthesize or manually render any DPS.
            WebDriverWait(browser,100).until(lambda d:d.execute_script("""
              return state.session===arguments[0] &&
                !document.getElementById("filled-result").hidden &&
                document.getElementById("dps").textContent!=="–" &&
                document.getElementById("sem").textContent!=="–";
            """,sid))
            displayed=browser_snapshot(browser)
            need(displayed["result_visible"] and
                 displayed["dps"] not in ("","–") and
                 displayed["sem"] not in ("","–") and
                 displayed["conf95"] not in ("","–"),
                 "REAL_SIMC_RESULT_NOT_DISPLAYED_IN_BROWSER")
            report["browser_display"]={
                k:displayed[k] for k in ("dps","sem","conf95","result_visible")}
            report["status"]="PASS_REAL_WINDOWS_COLD_UI_BUILD_TO_SIMC_DPS_SEM_95"
            save()
            print("V570_REAL_WINDOWS_USER "+json.dumps({
                k:report[k] for k in ("status","new_environment_native",
                "new_dps_native","verified_GJFO_B_T","result_summary",
                "browser_display")},ensure_ascii=True,sort_keys=True),flush=True)
            return 0
    except Exception as exc:
        report["status"]="BLOCKED_REAL_FIRST_USER_UI_PATH"
        report["error_type"]=type(exc).__name__
        report["first_blocker"]=code_only(exc)
        if sid and root and (root/sid).is_dir():
            try:
                state=longrun.read_status(root/sid,active=False)
                report["dps_native_attempts_on_failure"]=state.get(
                    "progress",{}).get("native_attempts")
            except Exception:pass
        save()
        return 2
    finally:
        if browser:
            try:browser.quit()
            except Exception:pass
        if server:
            stop_server(server,thread)
        print("V570_REAL_WINDOWS_VERDICT "+json.dumps({
            k:report.get(k) for k in ("status","first_blocker",
            "actual_live_build","new_environment_native",
            "actual_v212_install","new_dps_native",
            "dps_native_attempts_on_failure","DPS_worker_exit")
        },ensure_ascii=True,sort_keys=True),flush=True)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--simc",type=pathlib.Path,required=True)
    parser.add_argument("--out",type=pathlib.Path,required=True)
    opts=parser.parse_args()
    raise SystemExit(run(opts.simc,opts.out))
