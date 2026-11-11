#!/usr/bin/env python3
"""v344: real Windows Chrome click -> real local v113 -> exact 70783 SimC.

One fresh Retail environment (at most G1+F2 Native), one actual default
64-case N56 exploration. Click start/cancel, restart HTTP app after pause,
click resume/restore. Never synthetic fetch, fake SimC or old 12->64 import.
"""
from __future__ import annotations
import argparse,hashlib,json,os,pathlib,re,sys,tempfile,threading,time,zipfile
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select,WebDriverWait
import uvicorn

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner"),str(ROOT/"integration_probes")]
import v113_local_web_api as web
import v293_local_longrun_session as longrun
import v289_retail_live_build_source as retail
from integration_probes.p3_haj_real_local_web_native_e2e import save_cases

BUILD="12.1.5.70783"
EXE_SHA="1fc927d2be7f1b6064c75f004b5b22245b064a6b3e56e572af4048ba822a986d"
REV="de11f57df75dda668bae6ac7043a43b98831fa96"
PORT=8797
URL=f"http://127.0.0.1:{PORT}/"
SCHEMA="p1_v344_win_chrome_real_http_native64_start_cancel_resume_v1"

def need(condition,label):
    if not condition:raise RuntimeError("V344_"+label)

def sha(p):
    h=hashlib.sha256()
    with pathlib.Path(p).open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def start_server(root):
    app=web.create_app(root=root)
    server=uvicorn.Server(uvicorn.Config(app,host="127.0.0.1",port=PORT,
        access_log=False,proxy_headers=False,log_level="error"))
    thread=threading.Thread(target=server.run,daemon=True)
    thread.start()
    for _ in range(150):
        need(thread.is_alive(),"HTTP_SERVER_THREAD_EXITED")
        if server.started:
            try:
                with urlopen(URL+"api/v1/health",timeout=2) as reply:
                    if reply.status==200:return app,server,thread
            except OSError:pass
        time.sleep(.1)
    raise RuntimeError("V344_HTTP_SERVER_START_TIMEOUT")

def stop_server(server,thread):
    if server:
        server.should_exit=True
        thread.join(timeout=20)
        need(not thread.is_alive(),"HTTP_SERVER_NOT_STOPPED")

def driver_open():
    options=Options()
    for flag in ("--headless=new","--no-sandbox","--disable-dev-shm-usage",
                 "--window-size=1440,950"):
        options.add_argument(flag)
    browser=webdriver.Chrome(options=options)
    browser.get(URL)
    WebDriverWait(browser,35).until(
        lambda d:d.find_element(By.ID,"start-btn").is_enabled())
    return browser

def field(browser,name,value):
    node=browser.find_element(By.ID,name)
    if not node.is_displayed():
        if name in ("binary","revision"):
            browser.find_element(By.CSS_SELECTOR,
                "#simc-technical-panel > summary").click()
        elif name=="season-game-build":
            browser.find_element(By.CSS_SELECTOR,
                "#season-setup-details > summary").click()
        else:raise RuntimeError("V344_INPUT_NOT_VISIBLE_"+name)
    node.clear()
    node.send_keys(str(value))
    need(node.get_attribute("value")==str(value),"FORM_FIELD_NOT_SET_"+name)

def elapsed_wait(browser,expression,timeout=180):
    return WebDriverWait(browser,timeout,poll_frequency=.25).until(
        lambda d:d.execute_script("return ("+expression+")"))

def read_ui(browser):
    return browser.execute_script("""
      return {
        session:state.session,
        running:state.running,
        longrun:state.longrunEnabled,
        label:document.getElementById("run-label").textContent,
        progress:document.getElementById("progress-label").textContent,
        dps:document.getElementById("dps").textContent,
        sem:document.getElementById("sem").textContent,
        conf:document.getElementById("conf95").textContent,
        result_visible:!document.getElementById("filled-result").hidden,
        resume_disabled:document.getElementById("resume-btn").disabled,
        cancel_disabled:document.getElementById("cancel-btn").disabled,
        notice:document.getElementById("notice").textContent
      };
    """)

def run(binary,out):
    need(sys.platform=="win32","REAL_WINDOWS_ONLY")
    binary=pathlib.Path(binary).resolve(strict=True)
    need(binary.name.lower()=="simc.exe" and sha(binary)==EXE_SHA,
         "EXACT_CURRENT_WINDOWS_EXECUTABLE_CHANGED")
    need(os.environ.get("SIMC_PINNED_SOURCE_COMMIT")==REV and
         os.environ.get("SIMC_PINNED_GAME_BUILD")==BUILD,
         "PINNED_SOURCE_IDENTITY_CHANGED")
    need(all(os.environ.get(k) for k in (
        "BLIZZARD_CLIENT_ID","BLIZZARD_CLIENT_SECRET",
        "WCL_CLIENT_ID","WCL_CLIENT_SECRET")),"ENVIRONMENT_SOURCE_AUTH_MISSING")
    live=retail.discover(region="KR")
    need(live.get("game_build")==BUILD,"LIVE_KR_BUILD_NOT_70783")
    out=pathlib.Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    report={
        "schema":SCHEMA,"status":"NOT_STARTED","platform":"windows-2022",
        "game_build":BUILD,"binary_sha256":EXE_SHA,"revision":REV,
        "character":"hunter/survival","target_ilevel":334,
        "source":"ACTUAL_CHROME_CLICKS_AND_ORIGINAL_LOCAL_HTTP",
        "synthetic_worker":False,"actual_simc_native":False,
        "new_environment_native":0,"new_dps_native":0,
        "max_dps_native":64,"global_optimum_proven":False,
        "old_v343_12_case_imported":False,
        "real_user_personal_pc_proven":False,
        "same_build_proven_only":True}
    def save():
        (out/"V344_WINDOWS_REAL_BROWSER64_COMPACT.json").write_text(
            json.dumps(report,sort_keys=True,ensure_ascii=False,
                       allow_nan=False,indent=2)+"\n",encoding="utf8")
    save()
    app=server=thread=browser=None
    sid=None
    with tempfile.TemporaryDirectory(prefix="v344-windows-e2e-",dir=out) as tmp:
        root=pathlib.Path(tmp)/"sessions"
        root.mkdir()
        try:
            app,server,thread=start_server(root)
            browser=driver_open()
            browser.execute_script("window.confirm=()=>true;")
            field(browser,"binary",binary)
            field(browser,"revision",REV)
            field(browser,"season-game-build",BUILD)
            # A real <input> 'change' event fires on blur and starts an
            # asynchronous read-only installed-oil refresh. Allow it to
            # settle BEFORE the main Build click: the v113 UI intentionally
            # rejects a second withBusy action while one is active.
            browser.find_element(By.ID,"season-game-build").send_keys(Keys.TAB)
            elapsed_wait(browser,'!state.busy',timeout=35)
            # Observe the *actual* returned environment report at its
            # existing presentation boundary; pass it unchanged to the
            # product UI. No synthetic fetch, modified HTTP or Native mocks.
            browser.execute_script("""
              window.__v344_displayed_environment=null;
              const originalShow=showSeasonEnvironmentBuild;
              showSeasonEnvironmentBuild=function(data){
                window.__v344_displayed_environment=data;
                return originalShow(data);
              };
            """)
            # Real user-facing Environment Build click: all HTTP/data/native
            # work remains owned by v113/v216, with no internal call shortcut.
            browser.find_element(By.ID,"season-build-btn").click()
            elapsed_wait(browser,'!state.busy',timeout=480)
            report["season_build_ui_notice"]=read_ui(browser)["notice"][:260]
            report["season_build_ui_stage"]=browser.find_element(
                By.ID,"season-build-stage").text[:260]
            need("시즌 환경 구축 단계 조회 완료" in
                 report["season_build_ui_notice"],
                 "BROWSER_ENVIRONMENT_BUILD_NOT_COMPLETE")
            # v113's in-memory verified *profile* is intentionally a
            # compact subset: it does not contain numeric G/J/F/O.
            # Use only the original v216 HTTP Build report captured above.
            observed=browser.execute_script("""
              const data=window.__v344_displayed_environment;
              if(!data)return null;
              const c=data.source_compilation||{};
              const installed=c.verified_environment_install||{};
              return {
                status:data.status,environment_ready:data.environment_ready,
                environment_installed:data.environment_installed,
                native_calls:data.native_calls,
                G:data.G,J:data.J,F:data.F,O:data.O,B:data.B,T:data.T,
                manifest_sha256:installed.manifest_sha256
              };
            """)
            report["original_environment_report"]=observed
            installed=app.state.jobs._verified_fresh_profile_result
            need(type(installed) is dict and
                 type(observed) is dict,
                 "BROWSER_BUILD_DID_NOT_INSTALL_SOURCE")
            source=installed.get("source_compilation") or {}
            env_install=source.get("verified_environment_install") or {}
            report["installed_manifest_sha256"]=env_install.get("manifest_sha256")
            report["environment_budget"]={
                k:observed.get(k) for k in ("G","J","F","O","B","T")}
            report["new_environment_native"]=observed.get("native_calls")
            need(observed.get("environment_ready") is True and
                 observed.get("environment_installed") is True and
                 observed.get("manifest_sha256")==
                   report["installed_manifest_sha256"] and
                 type(report["new_environment_native"]) is int and
                 0<=report["new_environment_native"]<=3,
                 "UI_FRESH_SEASON_NOT_READY_OR_NATIVE_LIMIT")
            need(all(observed[k]==v for k,v in
                     (("G",2850),("J",92),("F",165),("B",3107),("T",3107))) and
                 sum(observed["O"].values())==0,
                 "EXACT_SEASON_BUDGET_DRIFT")
            report["browser_environment_build_clicked"]=True
            save()
            # Actual native <select> events: not a synthetic JS input stub.
            Select(browser.find_element(By.ID,"class-choice")).select_by_value("hunter")
            Select(browser.find_element(By.ID,"spec")).select_by_value("hunter/survival")
            chosen=browser.execute_script("""
              const r=buildRequest();
              return {controls:r.controls,product:r.current_season_product,
                      pinned:r.installed_season_game_build};
            """)
            controls=chosen["controls"]
            need(chosen["product"] and chosen["pinned"]==BUILD and
                 controls["class"]=="hunter" and
                 controls["spec"]=="survival" and
                 controls["ilevel"]==334 and
                 controls["final_T"] is None and
                 controls["oil_hands"]==[] and
                 len(controls["trinket_ids"])==2,
                 "ACTUAL_BROWSER_DEFAULT_USER_SCENARIO_DRIFT")
            report["browser_actual_user_controls_verified"]=True
            # PRIMARY button, never the opt-in 12-Native panel or an API fake.
            browser.find_element(By.ID,"start-btn").click()
            sid=elapsed_wait(browser,
                  'state.session && /^[a-f0-9]{20}$/.test(state.session) ? state.session : null',50)
            report["session_id"]=sid
            folder=root/sid
            need(longrun.config(folder)["native_budget"]==64 and
                 longrun.config(folder)["scout_iterations"]==56,
                 "ACTUAL_PRIMARY_64_N56_SESSION_NOT_SEALED")
            elapsed_wait(browser,'!document.getElementById("cancel-btn").disabled',30)
            # Allow the real worker to record at least one candidate when
            # possible; never let a cancelled partial become a fake result.
            progress=app.state.jobs.longrun_status(folder)
            for _ in range(30):
                if progress["progress"]["native_attempts"]>=1 or not progress["active"]:
                    break
                time.sleep(.08)
                progress=app.state.jobs.longrun_status(folder)
            need(progress["active"],"FULL64_FINISHED_BEFORE_CANCEL_TEST")
            browser.find_element(By.ID,"cancel-btn").click()
            child=app.state.jobs.children[sid]
            need(child.wait(timeout=160)==0,"CANCELLED_OS_WORKER_FAILED")
            paused=app.state.jobs.longrun_status(folder)
            need(paused["progress"]["worker"]["status"]=="PAUSED_USER_CANCEL"
                 and not paused["active"] and
                 paused["progress"]["native_attempts"]<64,
                 "CANCELLED_PARTIAL_AND_OS_STATE_NOT_VERIFIED")
            before=paused["progress"]["native_attempts"]
            report["native_attempts_at_cancel"]=before
            report["cancel_actual_browser"]=True
            # A real HTTP process restart, not a second in-memory app only.
            stop_server(server,thread)
            server=thread=None
            app,server,thread=start_server(root)
            browser.refresh()
            browser.execute_script("window.confirm=()=>true;")
            elapsed_wait(browser,
                  'state.session === "'+sid+'" && !state.busy && !state.running',40)
            status=read_ui(browser)
            need(status["longrun"] and
                 "취소" in status["label"] and not status["resume_disabled"],
                 "REAL_RESTART_NOT_RESUMABLE_IN_BROWSER")
            report["real_local_http_restart_and_ui_restore"]=True
            browser.find_element(By.ID,"resume-btn").click()
            elapsed_wait(browser,'state.running === true',30)
            report["actual_browser_resume_continuous"]=True
            # Worker is true SimC, HTTP status is read-only.
            live_worker=app.state.jobs.children[sid]
            need(live_worker.wait(timeout=600)==0,"FULL64_OS_WORKER_EXIT_FAILURE")
            done=app.state.jobs.longrun_status(folder)
            need(done["progress"]["worker"]["status"]=="BUDGET_EXHAUSTED"
                 and not done["active"] and done["result_ready"] and
                 done["progress"]["native_attempts"]==64 and
                 done["progress"]["completed_jobs"]==64 and
                 done["scout_iterations_per_CHMV"]==56,
                 "ORIGINAL_FULL64_N56_NOT_COMPLETE")
            elapsed_wait(browser,
                '!document.getElementById("filled-result").hidden && '+
                'document.getElementById("run-label").textContent.includes("탐색 상한 완료")',
                timeout=60)
            ui=read_ui(browser)
            need(ui["resume_disabled"] and ui["result_visible"] and
                 ui["dps"]!="–" and ui["sem"]!="–",
                 "BROWSER_FINAL_RESULT_OR_DUPLICATE_RESUME_NOT_BLOCKED")
            result=longrun.read_result(folder)
            user=result["user_result"]
            top=user["observed_first_choice"]
            need(result["native_calls_cumulative"]==64 and
                 user["confidence_level"]==0.95 and
                 user["global_optimum_proven"] is False and
                 sum(top["absolute_rating_T"].values())==user["final_T"]==3107 and
                 top["observed_dps_mean"]>0 and top["simc_sem"]>=0,
                 "TRUE64_DPS_SEM_95_CHMV_INVALID")
            report["new_dps_native"]=64
            report["actual_simc_native"]=True
            report["observed"]={
                "chmv":top["absolute_rating_T"],"dps":top["observed_dps_mean"],
                "sem":top["simc_sem"],"confidence":user["confidence_level"],
                "selected_pair_direction_supported_95":
                     user["confirmation_pair_direction_supported_at_95"],
                "global_optimum_proven":False}
            report["browser_final"]=ui
            # Real visible restore panel, not a synthetic JS click or mock.
            browser.find_element(By.CSS_SELECTOR,"details.restore > summary").click()
            browser.find_element(By.ID,"restore-btn").click()
            elapsed_wait(browser,
                '!document.getElementById("filled-result").hidden',30)
            reopened=read_ui(browser)
            need(reopened["dps"]==ui["dps"] and
                 reopened["sem"]==ui["sem"] and
                 reopened["resume_disabled"],
                 "BROWSER_REOPENED_64_RESULT_CHANGED")
            report["browser_result_reopened_exactly"]=True
            # Read-only Native SHA conservation; no additional SimC.
            stage=longrun.stage_path(folder,64)/"simc_results"
            native_json=sorted(stage.glob("cases/case_*/native/result.json"))
            native_input=sorted(stage.glob("cases/case_*/native/input.simc"))
            native_receipts=sorted(stage.glob("cases/case_*/native/native_receipt.json"))
            need(len(native_json)==len(native_input)==len(native_receipts)==64,
                 "NATIVE_64_ORIGINAL_TRIPLETS_MISSING")
            report["json2_sha256"]=[sha(p) for p in native_json]
            report["first_input_sha256"]=sha(native_input[0])
            bundle=out/"V344_NATIVE64_INPUT_JSON2_RECEIPTS.zip"
            detail=save_cases(root,sid,bundle)
            report["native_original_zip_sha256"]=detail["sha256"]
            report["native_original_case_files"]=detail["native_case_files"]
            report["status"]="PASS_REAL_WIN_BROWSER_LOCAL_SERVER_70783_NATIVE64"
            save()
            print("V344_REAL_WIN_BROWSER_NATIVE64 "+json.dumps({
                k:report[k] for k in ("status","new_environment_native",
                    "new_dps_native","native_attempts_at_cancel","observed",
                    "browser_result_reopened_exactly")},
                ensure_ascii=False,sort_keys=True),flush=True)
        except BaseException as exc:
            report["status"]="BLOCKED_OR_PARTIAL_"+type(exc).__name__
            msg=str(exc)
            report["first_stable_error_code"]=(msg if re.fullmatch(
                r"V344_[A-Z0-9_]{3,100}",msg) else type(exc).__name__)
            if sid and folder.is_dir():
                try:
                    p=longrun.read_status(folder,active=False)
                    report["native_attempts_on_failure"]=p["progress"].get(
                        "native_attempts",0)
                except Exception:pass
            save()
            raise
        finally:
            if browser:
                try:browser.quit()
                except Exception:pass
            if server:stop_server(server,thread)

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--simc",type=pathlib.Path,required=True)
    a.add_argument("--out",type=pathlib.Path,required=True)
    opts=a.parse_args()
    run(opts.simc,opts.out)
