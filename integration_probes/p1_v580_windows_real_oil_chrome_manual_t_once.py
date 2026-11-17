#!/usr/bin/env python3
"""v580: exact actual 70783 selected physical-O v212 install -> ORIGINAL
Chrome UI default oil binding -> original browser generated manual T3500
request -> original localhost sessions/plan. User DPS Native 0.

Fresh isolated source-owned v216 environment may run its bounded G/F/O
SimC probes once; it never starts the 64-case search. No mocks for sources,
installed SHA, season gear, original web API or SimC inputs. Browser only
performs input and reads original UI state; no synthetic cache/approval.
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
import v212_environment_manifest as installed
import v216_environment_build_coordinator as coordinator
import v289_retail_live_build_source as retail
from p1_v578_real_positive_oil_manual_t_plan_once import (
    BUILD,REV,EXE_SHA,FLASK_ITEM,OIL_ITEM,MANUAL_T,
    Credentials,digest,code)
from p1_v570_real_windows_cold_browser_to_simc_once import (
    navigate,clickable,input_text,wait_idle,browser_snapshot,select_trinket)

PORT=8798
URL=f"http://127.0.0.1:{PORT}/"
SCHEMA="p1_v580_actual_windows_chrome_positive_oil_exact_v212_manual_t_plan_v1"
NAME="V580_REAL_CHROME_POSITIVE_OIL_MANUAL_T_COMPACT.json"
TRINKETS=(270175,270173)
ENV_NATIVE_LIMIT=12

class BrowserSourceCredentials(Credentials):
    """CI-only status view for the original web UI, no secret exposure.

    The real positive-O source Build reads ephemeral Actions credentials.
    A live browser's read-only status route additionally requires status().
    """
    def status(self):
        return {"supported":True,"configured":self.load() is not None}

def need(ok,reason):
    if not ok:raise RuntimeError("V580_"+reason)

def start_http(app):
    config=uvicorn.Config(app,host="127.0.0.1",port=PORT,
                          access_log=False,proxy_headers=False,log_level="error")
    server=uvicorn.Server(config)
    thread=threading.Thread(target=server.run,daemon=True)
    thread.start()
    for _ in range(200):
        need(thread.is_alive(),"ACTUAL_LOCALHOST_SERVER_EXITED")
        if server.started:
            try:
                with urlopen(URL+"api/v1/health",timeout=2) as resp:
                    if resp.status==200:return server,thread
            except OSError:pass
        time.sleep(.1)
    raise RuntimeError("V580_ACTUAL_LOCALHOST_SERVER_TIMEOUT")

def browser_open():
    options=Options()
    for flag in ("--headless=new","--no-sandbox",
                 "--disable-dev-shm-usage","--window-size=1440,950"):
        options.add_argument(flag)
    browser=webdriver.Chrome(options=options)
    browser.get(URL)
    WebDriverWait(browser,60).until(lambda d:d.execute_script("""
      return !!state.token && state.defaults.length===26 &&
         !state.busy && field("spec")==="paladin/retribution";
    """))
    return browser

def visible(browser):
    return browser.execute_script("""
      const row=selectedFullVerifiedOil();
      return {
         spec:field("spec"),
         build:field("season-game-build")||
               state.verifiedInstalledBuildFromThisPage,
         ilevel:Number(field("ilevel")),
         manual_mode:$("manual-t-mode").checked,
         final_T:field("final_T"),
         oil_use_intent:oilUseIntent,
         oil_main:$("oil_main").checked,
         oil_off:$("oil_off").checked,
         oil_id:field("optimizer-oil-main-id"),
         loadout_sha:field("optimizer-oil-loadout"),
         installed_sha:state.seasonGear?.installed_manifest_sha256||null,
         installed_level:state.seasonGearTargetIlevel,
         source_scope:state.seasonGear?.source_scope,
         found_verified_oil:!!row,
         verified_oil_sha:row?.installed_manifest_sha256||null,
         flask_id:field("season-selected-flask-id"),
         trinkets:[field("trinket1"),field("trinket2")],
         busy:state.busy,
         notice:$("notice").textContent
      };
    """)

def run(binary,out):
    binary=pathlib.Path(binary).resolve(strict=True)
    out=pathlib.Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    receipt=out/NAME
    data={
      "schema":SCHEMA,"status":"STARTED","game_build":BUILD,
      "target_ilevel":334,"simc_revision":REV,
      "simc_executable_sha256":EXE_SHA,
      "actual_source_environment_native":None,
      "actual_user_dps_native":0,
      "actual_chrome":False,
      "actual_http_original_app":False,
      "actual_verified_oil_item_id":OIL_ITEM,
      "actual_flask_item_id":FLASK_ITEM,
      "user_manual_final_T":MANUAL_T,
      "original_v212_manifest_sha256":None,
      "real_browser_auto_bound_exact_positive_O_sha":False,
      "real_browser_generated_exact_request":False,
      "real_http_user_plan_ready":False,
      "source_approval_synthetic":False,
      "personal_pc_tested":False,
      "global_optimum_proven":False,
      "full_product_e2e":"PENDING"}
    def save():
        receipt.write_text(json.dumps(data,sort_keys=True,indent=2,
            allow_nan=False,ensure_ascii=False)+"\n",encoding="utf8")
    save()
    browser=server=thread=None
    try:
        need(sys.platform=="win32" and binary.name.lower()=="simc.exe" and
             digest(binary)==EXE_SHA,"ORIGINAL_OFFICIAL_WINDOWS_SIMC_REQUIRED")
        need(os.environ.get("SIMC_PINNED_SOURCE_COMMIT")==REV and
             os.environ.get("SIMC_PINNED_GAME_BUILD")==BUILD,
             "SAME_BUILD_REVISION_REQUIRED")
        need(Credentials().load() is not None,
             "AUTHENTIC_SOURCE_CREDENTIALS_REQUIRED")
        banner=subprocess.run([str(binary)],input="",capture_output=True,
             text=True,errors="replace",cwd=binary.parent,timeout=25)
        need(banner.returncode==0 and BUILD in
             (banner.stdout+"\n"+banner.stderr),
             "SAME_BUILD_SIMC_BANNER_REQUIRED")
        live=retail.discover(region="KR")
        data["live_retail_build"]=live.get("game_build")
        if live.get("game_build")!=BUILD:
            data["status"]="PENDING_PINNED_SIMC_NOT_ACTIVE_RETAIL"
            data["first_blocker"]="ACTIVE_BUILD_CHANGED"
            save();return 2
        with tempfile.TemporaryDirectory(prefix="v580-real-browser-oil-",dir=out) as d:
            root=pathlib.Path(d)/"runs";root.mkdir()
            original_jobs=web.LocalJobs(root,
                source_credential_store=Credentials())
            env=original_jobs.build_season_environment(
                 game_build=BUILD,target_ilevel=334,
                 native_G_binary=str(binary),consumable_native_binary=str(binary),
                 auto_native_F_requested=True,auto_native_O_requested=True,
                 selected_flask_item_id=FLASK_ITEM,
                 selected_oil_item_ids_by_hand={"main_hand":OIL_ITEM},
                 source_target_socket_count=4,
                 existing_special_gem_id=None,simc_revision_hint=REV)
            data["actual_source_environment_native"]=env.get("native_calls")
            data["environment_ready"]=env.get("environment_ready")
            data["environment_installed"]=env.get("environment_installed")
            data["observed_GJFO_B_T"]={
                x:env.get(x) for x in ("G","J","F","O","B","T")}
            save()
            need(type(data["actual_source_environment_native"]) is int and
                 0<=data["actual_source_environment_native"]<=ENV_NATIVE_LIMIT,
                 "ACTUAL_SOURCE_NATIVE_BOUND_EXCEEDED")
            if not (data["environment_ready"] and data["environment_installed"]):
                data["status"]="PENDING_ORIGINAL_POSITIVE_O_ENVIRONMENT"
                data["first_blocker"]=str(
                    (env.get("zero_history_build") or {}).get(
                        "requires",["ACTUAL_SOURCE_NOT_READY"])[0])[:120]
                save();return 2
            entry=(env.get("source_compilation") or {}).get(
                "verified_environment_install") or {}
            sha=entry.get("manifest_sha256")
            need(isinstance(sha,str) and re.fullmatch("[a-f0-9]{64}",sha),
                 "EXACT_REAL_POSITIVE_O_MANIFEST_SHA_REQUIRED")
            doc,_=installed.read_json(pathlib.Path(entry["stage_output_path"]))
            installed.verify_fresh_installed_environment(doc)
            need(doc["manifest_sha256"]==sha and
                 doc.get("official_O_physical_source",{}).get(
                    "selected_oil_item_ids_by_hand")=={"main_hand":OIL_ITEM} and
                 sum(doc["official_O"].values())>0,
                 "REAL_POSITIVE_O_PHYSICAL_SOURCE_DRIFT")
            authenticated=coordinator.find_verified_installed_season_environment(
                root,334,expected_game_build=BUILD,
                selected_oil_item_ids_by_hand={"main_hand":OIL_ITEM},
                expected_installed_manifest_sha256=sha)
            need(authenticated is not None and
                 authenticated["installed_manifest_sha256"]==sha,
                 "REAL_V217_EXACT_POSITIVE_O_RECEIPT_UNAVAILABLE")
            data["original_v212_manifest_sha256"]=sha
            app=web.create_app(root=root,
                source_credential_store=BrowserSourceCredentials())
            app.state.jobs.remember_verified_fresh_environment(env)
            # Exact restored v113 profile and installed O loadout must exist
            # before a real browser can offer any selection.
            choices=app.state.jobs.installed_oil_loadouts(334,BUILD)
            rows=[x for x in choices.get("items",[])
                  if x.get("installed_manifest_sha256")==sha and
                     x.get("selected_oil_item_ids_by_hand")=={
                         "main_hand":OIL_ITEM}]
            need(choices.get("status")=="VERIFIED_INSTALLED_OIL_LOADOUTS" and
                 len(rows)==1 and rows[0]["verified_variant_count"]==1 and
                 rows[0]["ordinary_four_gem_profile"] is True,
                 "EXACT_USER_SELECTABLE_V113_OIL_VARIANT_NOT_INSTALLED")
            data["actual_read_only_verified_oil_choices"]=len(rows)
            server,thread=start_http(app)
            data["actual_http_original_app"]=True
            browser=browser_open()
            data["actual_chrome"]=True
            data["initial_browser"]=visible(browser)
            save()
            # Explicit same-build selection via actual DOM input/change.
            # This triggers original browser event and original local HTTP.
            browser.execute_script("""
              const n=$("season-game-build");
              n.value=arguments[0];
              n.dispatchEvent(new Event("input",{bubbles:true}));
              n.dispatchEvent(new Event("change",{bubbles:true}));
            """,BUILD)
            WebDriverWait(browser,100,poll_frequency=.5).until(
                lambda d:(lambda x:
                    x["installed_sha"]==sha and
                    x["loadout_sha"]==sha and
                    x["verified_oil_sha"]==sha and
                    x["found_verified_oil"] and
                    x["oil_main"] and not x["oil_off"] and
                    x["oil_id"]==str(OIL_ITEM) and
                    x["installed_level"]==334 and not x["busy"]
                )(visible(d)))
            snapshot=visible(browser)
            data["browser_auto_bound"]={
                k:snapshot[k] for k in (
                    "spec","build","ilevel","oil_use_intent",
                    "oil_main","oil_off","oil_id","loadout_sha",
                    "installed_sha","installed_level",
                    "found_verified_oil","verified_oil_sha")}
            data["real_browser_auto_bound_exact_positive_O_sha"]=True
            save()
            # Real user-level SimC/target/trinket DOM controls, not injected
            # internal oil state or a fabricated request object.
            navigate(browser,"settings")
            tech=browser.find_element(By.ID,"simc-technical-panel")
            if not tech.get_attribute("open"):
                clickable(browser,tech.find_element(By.TAG_NAME,"summary"))
            input_text(browser,"binary",str(binary))
            input_text(browser,"revision",REV)
            browser.find_element(By.ID,"revision").send_keys(Keys.TAB)
            wait_idle(browser,40)
            navigate(browser,"optimizer")
            current=browser_snapshot(browser)["trinkets"]
            for item_id in dict.fromkeys(filter(None,current)):
                select_trinket(browser,int(item_id))
            for item_id in TRINKETS:
                select_trinket(browser,item_id)
            checkbox=browser.find_element(By.ID,"manual-t-mode")
            if not checkbox.is_selected():clickable(browser,checkbox)
            input_text(browser,"final_T",str(MANUAL_T))
            exact=browser.execute_script("""
               const p=buildRequest();
               return {
                 final_T:p.controls.final_T,
                 ilevel:p.controls.ilevel,
                 oil_hands:p.controls.oil_hands,
                 selected_oil_item_ids_by_hand:
                   p.selected_oil_item_ids_by_hand||{},
                 installed_manifest_sha256:p.installed_manifest_sha256,
                 installed_season_game_build:p.installed_season_game_build,
                 trinket_ids:p.controls.trinket_ids,
                 current_season_product:p.current_season_product,
                 selected_flask_item_id:p.selected_flask_item_id
               };
            """)
            data["browser_actual_request"]=exact
            need(exact["final_T"]==MANUAL_T and
                 exact["installed_manifest_sha256"]==sha and
                 exact["installed_season_game_build"]==BUILD and
                 exact["oil_hands"]==["main_hand"] and
                 exact["selected_oil_item_ids_by_hand"]=={
                    "main_hand":OIL_ITEM} and
                 exact["trinket_ids"]==list(TRINKETS) and
                 exact["current_season_product"] is True,
                 "ORIGINAL_CHROME_UI_MANUAL_T_OIL_REQUEST_INVALID")
            data["real_browser_generated_exact_request"]=True
            save()
            # Original localhost API called FROM Chrome via original api().
            # No hidden UI plan button is pretended to be a visible click.
            response=browser.execute_async_script("""
              const callback=arguments[arguments.length-1];
              api("/api/v1/sessions/plan",{
                  method:"POST",payload:buildRequest()})
                .then(x=>callback({ok:true,value:x}))
                .catch(e=>callback({ok:false,error:String(e?.message||e)}));
            """)
            data["browser_plan_http_ok"]=response.get("ok")
            if not response.get("ok"):
                data["first_blocker"]=response.get("error","UNKNOWN")[:150]
                data["status"]="PENDING_CHROME_USER_PLAN_ORIGINAL_API"
                save();return 2
            plan=response["value"].get("plan") or {}
            sid=response["value"].get("session_id")
            need(type(sid) is str and re.fullmatch(r"[a-f0-9]{20}",sid),
                 "ORIGINAL_PLAN_SESSION_ID_MISSING")
            profile=root/sid/"generated"/"profile.simc"
            need(profile.is_file(),"ORIGINAL_CHROME_PLAN_PROFILE_MISSING")
            oil_line=sum(x.startswith("temporary_enchant=") and
                "thalassian_phoenix_oil" in x
                for x in profile.read_text(encoding="utf8").splitlines())
            data["plan"]={k:plan.get(k) for k in (
                "base_B","final_T","fixed_O")}
            data["user_plan_native_calls"]=response["value"].get("native_calls")
            data["profile_oil_token_once"]=oil_line==1
            data["original_browser_plan_session_sha256"]=[
                hashlib.sha256(sid.encode()).hexdigest()]
            need(response["value"].get("status")=="READY_ZERO_NATIVE" and
                 data["plan"]["base_B"]==MANUAL_T-
                    sum(doc["official_O"].values()) and
                 data["plan"]["final_T"]==MANUAL_T and
                 data["plan"]["fixed_O"]==doc["official_O"] and
                 data["user_plan_native_calls"]==0 and
                 oil_line==1,
                 "CHROME_ACTUAL_POSITIVE_O_PLAN_BUDGET_DRIFT")
            data["real_http_user_plan_ready"]=True
            data["status"]="PASS_ACTUAL_CHROME_POSITIVE_O_V212_SHA_MANUAL_T_HTTP_PLAN_NO_DPS"
            save()
            print("V580_REAL_CHROME_OIL "+json.dumps({
              k:data.get(k) for k in(
                "status","actual_source_environment_native",
                "actual_user_dps_native","real_browser_auto_bound_exact_positive_O_sha",
                "real_browser_generated_exact_request","plan",
                "user_plan_native_calls")},sort_keys=True),flush=True)
            return 0
    except Exception as exc:
        data["status"]="BLOCKED_ACTUAL_CHROME_"+type(exc).__name__
        data["first_blocker"]=code(exc)
        if browser is not None:
            try:
                state=visible(browser)
                data["last_browser_observed"]={
                  k:state.get(k) for k in (
                    "spec","build","ilevel","oil_id","loadout_sha",
                    "installed_sha","source_scope","busy","notice")}
            except Exception:pass
        save()
        print("V580_REAL_CHROME_BLOCKER "+json.dumps({
            k:data.get(k) for k in(
                "status","first_blocker","actual_source_environment_native",
                "real_browser_auto_bound_exact_positive_O_sha")},
                sort_keys=True),flush=True)
        return 2
    finally:
        if browser is not None:
            try:browser.quit()
            except Exception:pass
        if server is not None:
            server.should_exit=True
            if thread is not None:
                thread.join(timeout=30)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--simc",required=True)
    p.add_argument("--out",required=True)
    q=p.parse_args()
    raise SystemExit(run(q.simc,q.out))
