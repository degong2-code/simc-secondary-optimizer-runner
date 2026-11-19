#!/usr/bin/env python3
"""v621 real Chrome 70961: signed chest E0 click -> start -> cancel -> resume.

An actual v113 server, exact same-build source Build (v216/v217/v212),
and original 64-budget adaptive runner. STOP after demonstrating a new
Native evaluation on resume rather than unnecessarily repeating all 64.
The earlier v619 six-JSON2 full DPS/SEM/95% evidence is reused as history,
never claimed as this partial run's result.

Never forge v212 or inject source/catalog, JS state, native data or receipts.
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

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner"),str(ROOT/"integration_probes")]
import v289_retail_live_build_source as retail
import v293_local_longrun_session as longrun
import p1_v570_real_windows_cold_browser_to_simc_once as browser_base
from p1_v570_real_windows_cold_browser_to_simc_once import (
    start_server,stop_server,chrome,navigate,clickable,input_text,
    wait_idle,browser_snapshot,select_trinket)
from p1_v344_windows_real_browser_native64_once import (
    choose_visible_search,elapsed_wait,read_ui)
from p1_v610_real_installed_enchant_one_build import bounded_code

SCHEMA="p1_v621_real_70961_browser_signed_e0_one_session_cancel_resume_v1"
BUILD="12.1.5.70961"
REV="9933ffb946fb55b1fa66657b848f519ac19006e1"
ENCHANT_ID=7957
SLOT="chest"
TRINKETS=(270175,270173)


def sha(path):
    h=hashlib.sha256()
    with pathlib.Path(path).open("rb") as f:
        for data in iter(lambda:f.read(1048576),b""):
            h.update(data)
    return h.hexdigest()


def require(ok,code):
    if not ok:raise RuntimeError("V621_"+code)


def browser_enchant_snapshot(driver):
    return driver.execute_script("""return {
      installed_sha:state.seasonGear?.installed_manifest_sha256||null,
      active_build:state.verifiedInstalledBuildFromThisPage,
      status:document.getElementById("season-option-catalog-status").textContent,
      approved:state.installedOtherE0Choices?.has("chest:7957")===true,
      chest_enabled:!document.getElementById("env-enchant-chest").disabled,
      chest_options:[...document.getElementById("env-enchant-chest").options]
         .filter(x=>x.value).map(x=>({value:x.value,disabled:x.disabled})),
      chest_selected:document.getElementById("env-enchant-chest").value,
      underlying:document.getElementById("season_enchant_other").value,
      ring1:document.getElementById("season_enchant_finger1").value,
      ring2:document.getElementById("season_enchant_finger2").value
    };""")


def run(binary,out,*,complete_after_resume=False):
    import platform
    out=pathlib.Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    report={"schema":("p1_v624_real_70961_signed_e0_browser_full_result_restore_v1"
                      if complete_after_resume else SCHEMA),"status":"STARTED",
        "game_build":BUILD,"simc_revision":REV,
        "actual_chrome":False,"signed_registered_option_not_fabricated":True,
        "new_approval_granted":False,
        "user_profile_gear_selected_directly":False,
        "new_simc_compilation":False,
        "reused_prior_v619_user_DPS_for_current_result":False,
        "original_adaptive_engine_unchanged":True,
        "partial_cancel_resume_not_full_64_or_global_optimum":not complete_after_resume,
        "new_native_calls":None,
        "official_78_complete_not_modified":True,
        "full_product_e2e":"PENDING"}
    receipt=out/("V624_REAL_CHROME_ENCHANT_FULL_RESULT_RESTORE.json"
                 if complete_after_resume else "V621_REAL_CHROME_ENCHANT_CANCEL_RESUME.json")
    def save():
        receipt.write_text(json.dumps(report,ensure_ascii=False,indent=2,
            sort_keys=True,allow_nan=False,default=str)+"\n",encoding="utf8")
    save()
    app=server=thread=driver=None
    sid=None
    try:
        require(platform.system()=="Windows","WINDOWS_ONLY")
        binary=pathlib.Path(binary).resolve(strict=True)
        require(binary.name.lower()=="simc.exe","ORIGINAL_WINDOWS_SIMC_ONLY")
        require(os.getenv("SIMC_PINNED_GAME_BUILD")==BUILD and
                os.getenv("SIMC_PINNED_SOURCE_COMMIT")==REV,
                "SOURCE_REVISION_BUILD_IDENTITY_MISMATCH")
        observed_sha=sha(binary)
        report["exact_source_bound_simc_binary_sha256"]=observed_sha
        report["simc_binary_reused"]=True
        cli=subprocess.run([str(binary)],input="",capture_output=True,
            text=True,errors="replace",cwd=binary.parent,timeout=25)
        require(cli.returncode==0 and BUILD in (cli.stdout+"\n"+cli.stderr),
                "SIMC_CLI_70961_BANNER_MISMATCH")
        live=retail.discover(region="KR")
        report["live_game_build"]=live.get("game_build")
        if live.get("game_build")!=BUILD:
            report["status"]="PENDING_NEW_LIVE_GAME_BUILD_SOURCE"
            report["first_blocker"]="CURRENT_RETAIL_BUILD_DIFFERS_FROM_PINNED_70961"
            save()
            return 2
        source=ROOT/"data"
        old=list(source.glob("current_season_*.json"))
        old+=list((source/"season_ordinary_gem_nominal").glob("*.json"))
        old+=list(source.glob("v202_*.json"))
        old+=list(source.glob("v206_*.json"))
        require(not old,"HISTORICAL_OTHER_BUILD_SOURCES_NOT_QUARANTINED")
        with tempfile.TemporaryDirectory(prefix="v621-real-chrome-",dir=out) as temp:
            root=pathlib.Path(temp)/"runs"
            root.mkdir()
            app,server,thread=start_server(root)
            driver=chrome()
            report["actual_chrome"]=True
            driver.execute_script("""window.confirm=()=>true;
              window.__v621_season=null;
              const original=showSeasonEnvironmentBuild;
              showSeasonEnvironmentBuild=function(doc,variant) {
                 window.__v621_season=doc;return original(doc,variant);
              };""")
            choose_visible_search(driver,"class-choice","성기사","성기사")
            choose_visible_search(driver,"spec","징벌","징벌")
            require(driver.execute_script("return field('spec')")==
                    "paladin/retribution","USER_VISIBLE_RETRIBUTION_INPUT")
            oil=driver.find_element(By.ID,"optimizer-oil-enabled")
            if oil.is_selected():clickable(driver,oil)
            navigate(driver,"settings")
            technical=driver.find_element(By.ID,"simc-technical-panel")
            if not technical.get_attribute("open"):
                clickable(driver,technical.find_element(By.TAG_NAME,"summary"))
            input_text(driver,"binary",str(binary))
            input_text(driver,"revision",REV)
            driver.find_element(By.ID,"revision").send_keys(Keys.TAB)
            wait_idle(driver,55)
            navigate(driver,"optimizer")
            initial=browser_snapshot(driver)
            require(initial["gear_sha"] is None and
                    not initial["start_disabled"] and
                    "시즌 환경 준비" in initial["start_label"],
                    "ORIGINAL_COLD_USER_ENVIRONMENT_START_NOT_READY")
            clickable(driver,driver.find_element(By.ID,"start-btn"))
            wait_idle(driver,1700)
            environment=driver.execute_script("""const e=window.__v621_season;
              if(!e)return null;
              return {ready:e.environment_ready,installed:e.environment_installed,
                G:e.G,J:e.J,F:e.F,O:e.O,B:e.B,T:e.T,
                status:e.source_compilation?.status,
                native_calls:e.native_calls,
                game_build:e.web_environment_scope?.game_build,
                manifest_sha:e.installed_manifest_sha256||
                  e.source_compilation?.verified_environment_install?.manifest_sha256,
                requires:e.zero_history_build?.requires||[]};""")
            report["real_environment_summary"]=environment
            if not isinstance(environment,dict) or not(
                    environment.get("ready") is True and
                    environment.get("installed") is True):
                report["status"]="PENDING_REAL_UI_ENVIRONMENT_BUILD"
                report["first_blocker"]=str(
                  (environment or {}).get("requires") or
                  (environment or {}).get("status"))[:140]
                save();return 2
            require(environment["game_build"]==BUILD and
                    environment["G"]==2850 and environment["J"]==92
                    and environment["F"]==165 and environment["B"]==3107
                    and environment["T"]==3107,"SOURCE_GJFO_B_T_70961_DRIFT")
            gear=browser_snapshot(driver)
            source_sha=environment["manifest_sha"]
            require(gear["gear_sha"]==source_sha and
                    re.fullmatch("[0-9a-f]{64}",source_sha) is not None,
                    "REAL_UI_V212_AND_GEAR_SHA_NOT_BOUND")
            installed_path=(root/"_fresh_season_sources"/
                            ("wago_"+BUILD)/"fresh_source"/
                            ("v212_installed_"+source_sha[:20]+".json"))
            require(installed_path.is_file(),"V212_ACTUAL_INSTALLED_FILE_MISSING")
            # Both web and native products must consume THIS installed v212.
            import v212_environment_manifest as v212
            installed,_=v212.read_json(installed_path)
            v212.verify_fresh_installed_environment(installed)
            matching=[x for x in installed["published_verified_options"]
                      if x.get("enchant_id")==ENCHANT_ID and
                         x.get("slot")==SLOT]
            require(len(matching)==1 and
                    matching[0].get("verified_fixed_E")=={
                     "crit_rating":0,"haste_rating":0,
                     "mastery_rating":0,"versatility_rating":0},
                    "SIGNED_7957_E0_NOT_IN_REAL_V212")
            report["actual_v212_registered_count"]=len(
                installed["published_verified_options"])
            report["actual_v212_manifest_sha256"]=source_sha
            selection=browser_enchant_snapshot(driver)
            report["visible_signed_enchant_before_click"]=selection
            require(selection["approved"] and selection["chest_enabled"] and
                    any(x["value"]=="chest:7957" and not x["disabled"]
                        for x in selection["chest_options"]),
                    "V620_VISIBLE_SIGNED_CHEST_OPTION_NOT_SELECTABLE")
            # REAL Selenium native select action, no JS state mutation.
            widget=driver.find_element(By.ID,"env-enchant-chest")
            Select(widget).select_by_value("chest:7957")
            chosen=browser_enchant_snapshot(driver)
            require(chosen["chest_selected"]=="chest:7957" and
                    chosen["underlying"]=="chest:7957" and
                    not chosen["ring1"] and not chosen["ring2"],
                    "VISIBLE_CHEST_CLICK_NOT_MIRRORED_EXACT_ONE")
            report["actual_visible_slot_selected"]=True
            report["visible_selected_chest_option"]="chest:7957"
            report["actual_chest_selection_summary"]=chosen
            # The default trinket cards may already be selected. Use the
            # existing real human-visible picker for the other two, never
            # inject missing trinket_ids into the request.
            initial_trinkets=browser_snapshot(driver)["trinkets"]
            for t in dict.fromkeys(filter(None,initial_trinkets)):
                select_trinket(driver,int(t))
            require(browser_snapshot(driver)["trinkets"]==["",""],
                    "OLDER_DEFAULT_TRINKETS_NOT_UNSELECTED")
            for tid in TRINKETS:select_trinket(driver,tid)
            req=driver.execute_script("""const r=buildRequest();return {
                sha:r.installed_manifest_sha256,
                season:r.installed_season_game_build,
                spec:r.controls.spec,
                enchant:r.controls.enchant_choices,
                trinkets:r.controls.trinket_ids,
                final_T:r.controls.final_T,
                ilvl:r.controls.ilevel,
                current:r.current_season_product,
                oil_hands:r.controls.oil_hands,
                binary:r.binary};""")
            # Optional manual final_T may be absent in auto-ilvl mode.
            # Preserve exact explicit build, signed enchant and one item.
            report["actual_browser_request_scoped"]={
                "sha":req.get("sha"),"build":req.get("season"),
                "enchant":req.get("enchant"),"trinkets":req.get("trinkets"),
                "ilevel":req.get("ilvl"),"oil_hands":req.get("oil_hands"),
                "request_keys":sorted(req),"manual_final_T":req.get("final_T")}
            require(req.get("sha")==source_sha and req.get("season")==BUILD and
                    req.get("enchant")=={"chest":7957} and
                    req.get("trinkets")==list(TRINKETS) and
                    req.get("final_T") is None and req.get("ilvl")==334 and
                    req.get("oil_hands")==[] and req.get("current") is True and
                    req.get("binary")==str(binary),
                    "EXACT_NEW_BROWSER_SELECTED_ENCHANT_REQUEST_INVALID")
            require(browser_snapshot(driver)["start_label"]=="최적 스탯 찾기",
                    "NATIVE_BROWSER_START_NOT_READY")
            report["same_signed_manifest_user_start"]=True
            save()
            clickable(driver,driver.find_element(By.ID,"start-btn"))
            sid=elapsed_wait(driver,
                    "state.session && /^[a-f0-9]{20}$/.test(state.session) ? state.session : null",75)
            report["session_id_sha256"]=hashlib.sha256(sid.encode()).hexdigest()
            folder=root/sid
            require(longrun.config(folder)["native_budget"]==64,
                    "ORIGINAL_LONGRUN_BUDGET_NOT_SEALED")
            inputs=json.loads((folder/"V106_SESSION_USER.json").read_text("utf8")) \
                if (folder/"V106_SESSION_USER.json").is_file() else None
            # Do not presume private file layout: the existing session
            # controller's signed inputs are checked by API at restore.
            WebDriverWait(driver,40).until(lambda d:d.execute_script(
                "return !document.getElementById('cancel-btn').disabled"))
            progress=app.state.jobs.longrun_status(folder)
            for _ in range(125):
                if progress["progress"]["native_attempts"]>=1 or not progress["active"]:break
                time.sleep(.12)
                progress=app.state.jobs.longrun_status(folder)
            require(progress["active"],"FINISHED_BEFORE_CANCEL_CANNOT_PROVE_RESUME")
            clickable(driver,driver.find_element(By.ID,"cancel-btn"))
            child=app.state.jobs.children[sid]
            require(child.wait(timeout=190)==0,"ORIGINAL_CANCEL_WORKER_FAILED")
            paused=app.state.jobs.longrun_status(folder)
            prior=paused["progress"]["native_attempts"]
            report["actual_native_attempts_before_resume"]=prior
            require(paused["progress"]["worker"]["status"]=="PAUSED_USER_CANCEL"
                    and not paused["active"] and prior<64,
                    "REAL_CANCEL_DID_NOT_PRESERVE_PARTIAL_CASES")
            report["actual_browser_cancelled"]=True
            save()
            # New HTTP application instance verifies disk session identity
            # and v212 stage receipts rather than trusting JS's stale state.
            stop_server(server,thread);server=thread=None
            app,server,thread=start_server(root)
            driver.refresh()
            driver.execute_script("window.confirm=()=>true")
            elapsed_wait(driver,
                'state.session === "'+sid+'" && state.longrunEnabled && '+
                '!state.busy && !state.running && '+
                '!document.getElementById("resume-btn").disabled',90)
            status=read_ui(driver)
            require("취소" in status["label"] and not status["resume_disabled"],
                    "REAL_RESTART_CANCELLED_SESSION_NOT_RESUMABLE")
            report["real_http_restart_and_saved_session"]=True
            # Saved v212 E0 must re-authorize the formerly chosen UI slot
            # without turning an old unsigned option into a new approval.
            restored=browser_enchant_snapshot(driver)
            report["reopened_signed_enchant_summary"]=restored
            require(restored["chest_selected"]=="chest:7957" and
                    restored["underlying"]=="chest:7957" and
                    restored["approved"],
                    "EXACT_SIGNED_ENCHANT_NOT_RESTORED_AFTER_RESTART")
            clickable(driver,driver.find_element(By.ID,"resume-btn"))
            elapsed_wait(driver,"state.session === '"+sid+"' && state.running === true",35)
            report["actual_browser_same_session_resumed"]=True
            post=app.state.jobs.longrun_status(folder)
            for _ in range(140):
                if (post["progress"]["native_attempts"]>prior
                    or not post["active"]):break
                time.sleep(.12)
                post=app.state.jobs.longrun_status(folder)
            new_count=post["progress"]["native_attempts"]
            report["actual_native_attempts_after_resume_start"]=new_count
            require(new_count>prior,
                    "RESUME_HAS_NOT_EVALUATED_ADDITIONAL_NATIVE_CASE")
            if complete_after_resume:
                # Existing 64-budget v291 worker, not a new search engine.
                # This is a separate v624 one-scenario acceptance probe.
                require(app.state.jobs.children[sid].wait(timeout=1100)==0,
                        "ORIGINAL_64_WORKER_FAILED")
                done=app.state.jobs.longrun_status(folder)
                p=done["progress"]
                require(not done["active"] and done["result_ready"] and
                        p["worker"]["status"]=="BUDGET_EXHAUSTED" and
                        p["completed_jobs"]==p["planned_jobs"]==64 and
                        p["native_attempts"]==64 and
                        done["scout_iterations_per_CHMV"]==56,
                        "EXACT_64_NATIVE_BUDGET_NOT_EXHAUSTED")
                actual=longrun.read_result(folder)
                user=actual["user_result"]
                best=user["observed_first_choice"]
                ratings=best["absolute_rating_T"]
                percentages=best["percent_of_final_T"]
                stat_names=("crit_rating","haste_rating","mastery_rating",
                            "versatility_rating")
                alts=user["material_near_alternatives"]
                require(actual["status"]=="BUDGET_EXHAUSTED" and
                        actual["native_calls_cumulative"]==64 and
                        user["confidence_level"]==0.95 and
                        user["global_optimum_proven"] is False and
                        user["selected_pair_95_only"] is True and
                        user["final_T"]==user["base_B"]==3107 and
                        sum(user["fixed_O"].values())==0 and
                        set(ratings)==set(percentages)==set(stat_names) and
                        sum(ratings.values())==3107 and
                        abs(sum(percentages.values())-100)<0.01 and
                        best["observed_dps_mean"]>0 and
                        best["simc_sem"]>=0 and
                        all(set(a["absolute_rating_T"])==set(stat_names)
                            for a in alts),
                        "REAL_64_ABSOLUTE_DPS_SEM_95_OR_O_ACCOUNTING_INVALID")
                result_file=longrun.stage_path(folder,64)/"simc_results"/"V291_RESULT.json"
                report["saved_final_v291_sha256"]=sha(result_file)
                report["saved_user_result"]={
                    "absolute_rating_T":ratings,
                    "ratio_percent":percentages,
                    "dps_mean":best["observed_dps_mean"],
                    "sem":best["simc_sem"],
                    "confidence_level":user["confidence_level"],
                    "pairwise_direction_supported_at_95":
                        user["confirmation_pair_direction_supported_at_95"],
                    "selected_pair_95_only":True,
                    "material_near_alternatives":len(alts),
                    "final_T":user["final_T"],"base_B":user["base_B"],
                    "global_optimum_proven":False}
                # Reuse the real browser polling/rendering (v570/v344), not
                # synthetic result injection or hand-crafted DOM.
                elapsed_wait(driver,
                    'state.session === "'+sid+'" && state.longrunCompleted && '+
                    '!document.getElementById("filled-result").hidden && '+
                    'document.getElementById("run-label").textContent.includes("탐색 상한 완료")',
                    100)
                def final_ui():
                    return driver.execute_script("""const e=id=>document.getElementById(id);
                        return {
                          dps:e("dps").textContent,
                          sem:e("sem").textContent,
                          conf95:e("conf95").textContent,
                          budget:e("budget").textContent,
                          alt_count:e("alt-count").textContent,
                          alt_rows:e("alt-list").querySelectorAll("article.alt-row").length,
                          stat_lines:[...e("stat-bars").querySelectorAll(".stat-heading")]
                            .map(n=>n.textContent),
                          result_visible:!e("filled-result").hidden,
                          run_label:e("run-label").textContent,
                          resume_disabled:e("resume-btn").disabled,
                          completed:state.longrunCompleted,
                          selected_session:state.session
                        };""")
                visible=final_ui()
                def good_ui(observed):
                    require(observed["selected_session"]==sid and
                            observed["completed"] and observed["result_visible"] and
                            observed["resume_disabled"] and
                            "탐색 상한 완료" in observed["run_label"] and
                            observed["dps"]==format(best["observed_dps_mean"],",.1f") and
                            observed["sem"]==format(best["simc_sem"],",.2f") and
                            observed["conf95"]==("방향 지지" if
                                user["confirmation_pair_direction_supported_at_95"]
                                else "미확정") and
                            "3,107" in observed["budget"] and
                            len(observed["stat_lines"])==4 and
                            observed["alt_rows"]==len(alts) and
                            observed["alt_count"].startswith(str(len(alts))+"개"),
                            "REAL_BROWSER_64_DPS_SEM_95_OR_ALTERNATIVES_DRIFT")
                    for k, label in zip(stat_names,("치명","가속","특화","유연")):
                        need_line=next((line for line in observed["stat_lines"]
                                        if label in line),None)
                        require(need_line is not None and
                                format(ratings[k],",d") in need_line,
                                "REAL_BROWSER_FOUR_ABSOLUTE_STATS_DRIFT")
                good_ui(visible)
                report["browser_final_verified"]=True
                report["browser_final_scope"]={
                    "result_visible":True,"dps":visible["dps"],
                    "sem":visible["sem"],"conf95":visible["conf95"],
                    "four_rating_lines":len(visible["stat_lines"]),
                    "material_alternative_rows":visible["alt_rows"]}
                # v622 saved-session dropdown, real read-only HTTP GET.
                # A user must be able to find this v293 completion, not
                # merely reopen it by knowing the opaque session key.
                driver.find_element(By.CSS_SELECTOR,"details.restore > summary").click()
                clickable(driver,driver.find_element(By.ID,"recent-refresh-btn"))
                elapsed_wait(driver,
                    'Array.from(document.getElementById("recent-session-id").options)'+
                    '.some(x=>x.value==="'+sid+'" && x.textContent.includes("결과 저장"))',
                    35)
                report["v622_saved_result_index_visible"]=True
                # Existing v570 browser restore, now after an HTTP restart.
                stop_server(server,thread)
                server=thread=None
                app,server,thread=start_server(root)
                driver.refresh()
                driver.execute_script("window.confirm=()=>true")
                elapsed_wait(driver,
                    'state.session==="'+sid+'" && state.longrunCompleted && '+
                    '!document.getElementById("filled-result").hidden',120)
                reopened=final_ui()
                good_ui(reopened)
                require(reopened==visible and
                        sha(result_file)==report["saved_final_v291_sha256"] and
                        app.state.jobs.longrun_status(folder)["progress"]["native_attempts"]==64,
                        "RESTART_REOPEN_CHANGED_RESULT_OR_NATIVE_COUNT")
                report["http_restart_final_result_reopened"]=True
                report["native_attempts_after_readonly_reopen"]=64
                report["new_native_calls"]=64
                report["case_count_after_resume"]=64
                report["second_cancel_or_completed_worker_status"]="BUDGET_EXHAUSTED"
                report["native_attempts_were_reused_without_reset"]=True
                report["status"]="PASS_REAL_CHROME_SIGNED_E0_64_FINAL_RESULT_REOPEN"
                save()
                return 0
            if post["active"]:
                clickable(driver,driver.find_element(By.ID,"cancel-btn"))
                require(app.state.jobs.children[sid].wait(timeout=190)==0,
                        "SECOND_SAFE_CANCEL_OS_WORKER_FAILED")
                post=app.state.jobs.longrun_status(folder)
            report["new_native_calls"]=post["progress"]["native_attempts"]
            report["case_count_after_resume"]=post["progress"]["completed_jobs"]
            report["second_cancel_or_completed_worker_status"]=post["progress"]["worker"]["status"]
            report["native_attempts_were_reused_without_reset"]=(
                post["progress"]["native_attempts"]>=prior)
            require(post["progress"]["native_attempts"]>=new_count and
                    post["progress"]["completed_jobs"]>=prior,
                    "PARTIAL_CACHE_CHECKPOINT_REGRESSION")
            report["status"]="PASS_REAL_CHROME_SIGNED_E0_START_CANCEL_RESTART_RESUME"
            save()
            return 0
    except Exception as exc:
        report["status"]="BLOCKED_"+type(exc).__name__
        report["first_blocker"]=bounded_code(exc)
        save()
        return 2
    finally:
        if driver:
            try:driver.quit()
            except Exception:pass
        if server:
            try:stop_server(server,thread)
            except Exception:pass


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--simc",required=True)
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    sys.exit(run(args.simc,args.out))


if __name__=="__main__":
    main()
