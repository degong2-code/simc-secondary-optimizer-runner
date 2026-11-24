#!/usr/bin/env python3
"""One contiguous *real packaged Windows* cold first-user acceptance.

No historical season cache, user session or SimC managed install is injected.
The ONLY input from runner is real user-like Blizzard/WCL credentials via
secrets. SimC is requested with the real public one-click UI, and no exact
70961 CLI is passed in. A new unsupported live build is a PENDING blocker,
never a pass or a fallback to old season measurements.

The native engine is unchanged: on full readiness the normal user primary
button launches its original bounded 64 candidate adaptive long-run.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import pathlib
import re
import sys
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"integration_probes"),str(ROOT/"runner")]
import p1_v573_windows_zip_cold_web_setup_consent_once as startup
from p1_v345_windows_extracted_zip_cmd_browser_restore import actual_chrome
from p1_v570_real_windows_cold_browser_to_simc_once import (
    choose_visible_search,clickable,navigate,select_trinket,wait_idle,
    browser_snapshot)

RECEIPT="V690_FIRST_USER_ONE_ZIP_CONTIGUOUS.json"
SCHEMA="p1_v690_real_extracted_zip_first_user_current_season_v1"
SECRETS=("BLIZZARD_CLIENT_ID","BLIZZARD_CLIENT_SECRET",
         "WCL_CLIENT_ID","WCL_CLIENT_SECRET")
FIELDS=("source-blizzard-id","source-blizzard-secret",
        "source-wcl-id","source-wcl-secret")


def require(ok,code):
    if not ok:
        raise RuntimeError("V690_"+code)


def safe(exc):
    value=str(exc).split(":",1)[0].split("\n",1)[0]
    return value if re.fullmatch(
        r"(?:V690|V344|V570)_[A-Z0-9_]{4,110}",value
    ) else type(exc).__name__


def eliminate_historical_sources(root,env,work):
    need=[
      root/"runner/v113_local_web_api.py",
      root/"runner/v216_environment_build_coordinator.py",
      root/"runner/v660_simc_one_click_provision.py",
    ]
    require(all(x.is_file() for x in need),"CURRENT_ZIP_RUNTIME_MISSING")
    folders=[(root/"data","current_season_*.json"),
             (root/"data","v202_*.json"),
             (root/"data","v206_*.json"),
             (root/"data/season_ordinary_gem_nominal","*.json")]
    dest=work/"prior-season-quarantine";dest.mkdir()
    removed=0
    for folder,pattern in folders:
        for source in folder.glob(pattern):
            (dest/(str(removed)+"-"+source.name)).write_bytes(
                source.read_bytes())
            source.unlink()
            removed+=1
    require(removed>0,"NO_HISTORICAL_BUNDLED_SEASON_TO_QUARANTINE")
    home=pathlib.Path(env["HOME"])
    local=pathlib.Path(env["LOCALAPPDATA"])
    require(not (home/"SIMC_Secondary_Optimizer"/"runs").exists() and
            not (local/"SIMC_Secondary_Optimizer"/"managed").exists(),
            "USER_SESSIONS_OR_SIMC_ALREADY_PRESENT")
    return removed


def stage(args):
    out=pathlib.Path(args.out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    destination=out/RECEIPT
    record={"schema":SCHEMA,"status":"STARTED",
            "real_windows_zip":True,"new_user_appdata":True,
            "historical_source_reused":False,
            "same_window_first_setup":True,
            "simc_managed_installed_before_first_click":False,
            "prebundled_simc_exe":False,
            "external_prebuilt_simc_injected":False,
            "real_browser_not_synthetic_http":True,
            "new_dps_native_calls":0,"full_product_e2e":"PENDING",
            "other_seasons_or_26_specs_proven":False,
            "personal_pc_tested":False}
    def save():
        destination.write_text(json.dumps(
            record,ensure_ascii=False,sort_keys=True,indent=2,
            allow_nan=False)+"\n",encoding="utf8")
    def before(root,env,work):
        record["quarantined_historical_source_files"]=(
            eliminate_historical_sources(root,env,work))
        save()
    def continued(root,env,work):
        driver=None
        local_token=[None]
        try:
            driver=actual_chrome()
            require(driver.execute_script(
                "return state.defaults.length===26&&!state.session"
                "&&state.seasonGear===null;"),
                "FIRST_BROWSER_ALREADY_SEEDED")
            driver.execute_script("window.confirm=()=>true")
            navigate(driver,"settings")
            record["last_completed_stage"]="COLD_CHROME_AND_SETTINGS"
            # In the real product the secret fields are intentionally hidden
            # inside <details>. Click its human-visible summary first.
            credentials_panel=driver.find_element(
                By.ID,"season-credentials-panel")
            if not credentials_panel.get_attribute("open"):
                clickable(driver,credentials_panel.find_element(
                    By.TAG_NAME,"summary"))
            # Act like a new owner in the real UI; never record secret values.
            for key,field in zip(SECRETS,FIELDS):
                value=env.get(key,"")
                if not value:
                    record["status"]="PENDING_NO_SOURCE_API_CREDENTIALS"
                    record["first_blocker"]="CI_OWNER_API_CREDENTIALS_NOT_PROVIDED"
                    save()
                    return record
                box=driver.find_element(By.ID,field)
                box.send_keys(value)
            clickable(driver,driver.find_element(
                By.ID,"source-credentials-save-btn"))
            WebDriverWait(driver,30).until(lambda d:d.execute_script(
                "return document.getElementById('source-credentials-status')"
                ".textContent.includes('저장됨')&&!state.busy"))
            record["source_credentials_saved_via_real_browser"]=True
            local_token[0]=driver.execute_script(
                "return state.token")
            record["last_completed_stage"]="SOURCE_CREDENTIALS_SAVED"
            for field in FIELDS:
                require(driver.find_element(By.ID,field).get_attribute(
                    "value")=="","SECRET_REMAINED_IN_BROWSER_FIELD")
            details=driver.find_element(By.ID,"simc-technical-panel")
            if not details.get_attribute("open"):
                clickable(driver,details.find_element(By.TAG_NAME,"summary"))
            manager=driver.find_element(By.ID,"simc-update-panel")
            if not manager.get_attribute("open"):
                clickable(driver,manager.find_element(By.TAG_NAME,"summary"))
            # No provided simc.exe: the user explicitly asks for current
            # public official/self-built SimC through the ORIGINAL button.
            require(not driver.find_element(By.ID,"binary").get_attribute(
                "value"),"PREINSTALLED_USER_SIMC_PATH")
            clickable(driver,driver.find_element(
                By.ID,"simc-auto-prepare-btn"))
            WebDriverWait(driver,460,poll_frequency=1).until(
                lambda d:d.execute_script(
                    "return !state.busy && !document.getElementById("
                    "'simc-auto-prepare-btn').disabled"))
            provision=driver.execute_script("""return {
              status:document.getElementById('simc-auto-prepare-status')
                .textContent.slice(0,280),
              binary:document.getElementById('binary').value,
              revision:document.getElementById('revision').value,
              build:document.getElementById('season-game-build').value
            }""")
            record["one_click_simc_status_summary"]=provision["status"]
            record["last_completed_stage"]="SIMC_ONE_CLICK_RETURNED"
            record["one_click_simc_binary_configured"]=bool(
                provision["binary"])
            if not provision["binary"] or not provision["revision"]:
                record["status"]="PENDING_PUBLIC_SIMC_NOT_INSTALLABLE"
                record["first_blocker"]="CURRENT_LIVE_PUBLIC_SIMC_MISSING"
                save()
                return record
            exe=pathlib.Path(provision["binary"])
            require(exe.is_file() and exe.name.lower()=="simc.exe",
                    "SIMC_ONE_CLICK_PATH_NOT_INSTALLED")
            record["one_click_simc_binary_sha256"]=hashlib.sha256(
                exe.read_bytes()).hexdigest()
            # Verify the user's saved source and SimC connection. The
            # one-click UI may apply without a separate connection save.
            record["auto_simc_revision"]=provision["revision"]
            # Class/spec controls belong to the optimizer tab. The product
            # does not expose the search listboxes while Settings is active.
            # Navigate like a real user BEFORE attempting keyboard selection.
            navigate(driver,"optimizer")
            record["last_completed_stage"]="VISIBLE_OPTIMIZER_TAB"
            # User-facing diagnostics only: exact accessible option labels
            # and widget state. No user secrets, raw HTML, or screenshots.
            record["actual_choice_widgets"]=driver.execute_script("""return {
              tab:document.querySelector('.top-nav button.is-active')?.
                    dataset.view,
              busy:state.busy,
              class_input:!!document.getElementById('choice-class-choice'),
              class_input_disabled:document.getElementById(
                    'choice-class-choice')?.disabled,
              class_options:[...document.getElementById('class-choice').
                    options].map(x=>x.textContent).slice(0,20),
              spec_input:!!document.getElementById('choice-spec'),
              spec_input_disabled:document.getElementById(
                    'choice-spec')?.disabled
            }""")
            record["last_completed_stage"]="CLASS_SEARCH"
            save()
            choose_visible_search(driver,"class-choice",
                                  "흑마법사","흑마법사")
            record["last_completed_stage"]="CLASS_SELECTED"
            save()
            choose_visible_search(driver,"spec","파괴","파괴")
            record["last_completed_stage"]="SPEC_SELECTED"
            save()
            require(driver.execute_script(
                "return field('spec')==='warlock/destruction'"),
                "GENERIC_NON_PRIOR_SPEC_SELECTION_INVALID")
            record["selected_user_spec"]="warlock/destruction"
            # Each following real UI action gets a named step. Avoid
            # inventing success from Selenium's generic TimeoutException.
            record["last_completed_stage"]="SPEC_EXACT_VALUE_VERIFIED"
            save()
            # Let the original asynchronous class/spec oil catalog update
            # settle before changing the user's visible oil-use selector.
            # Otherwise a concurrent refresh may restore the prior default.
            wait_idle(driver,60)
            oil_mode=driver.find_element(By.ID,"optimizer-oil-use-mode")
            WebDriverWait(driver,30,poll_frequency=.25).until(
                lambda d:oil_mode.is_displayed() and oil_mode.is_enabled()
                and not d.execute_script("return state.busy"))
            record["oil_visible_mode_before"]=oil_mode.get_attribute("value")
            record["last_completed_stage"]="VISIBLE_OIL_MODE_BEFORE_SELECT"
            save()
            if oil_mode.get_attribute("value")!="off":
                Select(oil_mode).select_by_value("off")
            # The genuine UI handler applies through withBusy and mirrors
            # the selector to the hidden O-use checkbox. Do not use only
            # wait_idle(): a transient !busy can precede change dispatch.
            try:
                WebDriverWait(driver,40,poll_frequency=.25).until(
                    lambda d:d.execute_script("""return (
                      document.getElementById('optimizer-oil-use-mode')
                        .value==='off' &&
                      !document.getElementById('optimizer-oil-enabled')
                        .checked &&
                      !state.busy);"""))
            except TimeoutException:
                record["visible_oil_after_attempt"]=driver.execute_script(
                    """return {mode:document.getElementById(
                      'optimizer-oil-use-mode').value,
                      mirror_checked:document.getElementById(
                      'optimizer-oil-enabled').checked,
                      busy:state.busy, running:state.running,
                      status:document.getElementById(
                      'optimizer-oil-toggle-status').textContent.slice(0,90)
                    };""")
                save()
                require(False,"VISIBLE_OIL_OFF_NOT_APPLIED")
            record["oil_visible_mode_after"]="off"
            record["last_completed_stage"]="VISIBLE_OIL_OFF_APPLIED"
            save()
            navigate(driver,"optimizer")
            record["last_completed_stage"]="OPTIMIZER_TAB_AFTER_OIL"
            save()
            start=browser_snapshot(driver)
            require(start["gear_sha"] is None and
                    "시즌 환경 준비" in start["start_label"] and
                    not start["start_disabled"],
                    "COLD_SOURCE_BUTTON_NOT_AVAILABLE")
            record["first_user_visible_initial_environment"]=True
            record["last_completed_stage"]="COLD_SEASON_BUTTON_READY"
            save()
            driver.execute_script("""window.__v690_season=null;
              const original=showSeasonEnvironmentBuild;
              showSeasonEnvironmentBuild=function(...args) {
                window.__v690_season=args[0]; return original(...args);
              };""")
            record["last_completed_stage"]="SEASON_START_CLICKING"
            save()
            clickable(driver,driver.find_element(By.ID,"start-btn"))
            record["last_completed_stage"]="SEASON_START_CLICK_ACCEPTED"
            save()
            wait_idle(driver,1650)
            environment=driver.execute_script("""const e=window.__v690_season;
              if(!e)return null;
              function boundedJF(e) {
                const p=e.zero_history_build||{}, c=e.source_compilation||{};
                const get=k=>p[k]??c[k]??null;
                const code=v=>typeof v==="string"&&/^[A-Z][A-Z0-9_]{1,119}$/.test(v.split(":")[0])?v.split(":")[0]:null;
                const codes=v=>Array.isArray(v)?v.slice(0,32).map(code).filter(Boolean):[];
                const num=v=>Number.isSafeInteger(v)&&v>=0?v:null;
                const sha=v=>typeof v==="string"&&/^[a-f0-9]{64}$/.test(v)?v:null;
                const stage=r=>r&&typeof r==="object"?{
                  status:code(r.status),reason:code(r.reason),requires:codes(r.requires),
                  missing:codes(r.missing),quality_source_status:code(r.quality_source_status),
                  tier_source_status:code(r.tier_source_status),candidate_count:num(r.candidate_count),
                  sample_count:num(r.sample_count),new_native_calls:num(r.new_native_calls),
                  source_sha256:sha(r.source_sha256),v221_sha256:sha(r.v221_stage_receipt_sha256),
                  v230_sha256:sha(r.v230_stage_receipt_sha256)
                }:null;
                const nativeRows=v=>Array.isArray(v)?v.slice(0,24).map(r=>({
                  status:code(r.status),reason:code(r.reason),native_error_code:code(r.native_error),
                  native_error_present:!!r.native_error,new_native_calls:num(r.new_native_calls),
                  failed_variant:["baseline","active"].includes(r.failed_variant)?r.failed_variant:null,
                  native_status:code(r.native_status),
                  native_returncode:Number.isSafeInteger(r.native_returncode)?r.native_returncode:null,
                  simc_error_lines:typeof r.native_log_excerpt==="string"?
                    r.native_log_excerpt.split(String.fromCharCode(10))
                      .map(s=>s.trim()).filter(s=>s.startsWith("Error:"))
                      .slice(0,2).map(s=>s.slice(0,500)):[],
                  physical_item_id:num(r.physical_item_id??r.ordinary_gem_id??r.physical_item_native_source_unadmitted?.physical_item_id),
                  J_candidate:num(r.simc_effective_two_stat_rating_unadmitted),
                  F_candidate:num(r.F_candidate_unadmitted)
                })):[];
                const jNative=get("four_stat_simc_native_j_source_unadmitted");
                const fNative=get("automatic_F_native_measurements_unadmitted");
                const fSelected=get("automatic_default_F_source_selection_unadmitted");
                const owners=get("selected_J_F_source_owner_numeric_unadmitted");
                const core=get("required_core_source_owner_report");
                return {
                  J:{metadata:stage(get("ordinary_gem_v221_v230_source_candidates_unadmitted")),
                     pinned_dbc:stage(get("four_stat_pinned_dbc_j_source_unadmitted")),
                     native:stage(jNative),native_rows:nativeRows(jNative?.native_observations_unadmitted)},
                  F:{selection:stage(fSelected),
                     physical_item_id:num(fSelected?.selected_physical_items_unadmitted?.flask_item_id),
                     native:stage(fNative),native_rows:nativeRows(fNative?.per_item),
                     observations:nativeRows(e.native_effect_numeric_sources_unadmitted?.filter(r=>r.kind==="flask"))},
                  numeric_owner:stage(owners),J_rating:num(owners?.J?.rating),F_rating:num(owners?.F?.rating),
                  quality_owner:stage(get("selected_J_F_source_owner_quality_unadmitted")),
                  selected_budget:stage(get("selected_auto_v222_numeric_preview_unadmitted")),
                  verified_components:codes(get("original_J_F_verified_component_names")),
                  missing_core_owners:codes(core?.original_source_owner_missing_for_selected_request)
                };
              }
              return {
                ready:e.web_environment_scope?.environment_ready===true,
                installed:e.web_environment_scope?.environment_installed===true,
                build:e.web_environment_scope?.game_build,
                ilvl:e.web_environment_scope?.target_ilevel,
                B:e.B,T:e.T,native_calls:e.native_calls,
                sha:e.installed_manifest_sha256||
                    e.source_compilation?.verified_environment_install?.
                      manifest_sha256,
                requires:e.zero_history_build?.requires||[],
                status:e.source_compilation?.status,
                jf_source_diagnostic:boundedJF(e)};""")
            # These are bounded SimC error lines from the internal public
            # representative source profiles, not a full user profile/log.
            # Remove local roots and credentials before storing any receipt.
            if isinstance(environment,dict):
                diag=environment.get("jf_source_diagnostic") or {}
                sensitive=[env.get(key,"") for key in SECRETS]
                sensitive.extend((str(work),str(root),env.get("HOME",""),
                                  env.get("LOCALAPPDATA",""),str(exe)))
                sensitive=sorted({v for v in sensitive if v},key=len,reverse=True)
                for rows in ((diag.get("J") or {}).get("native_rows",[]),
                             (diag.get("F") or {}).get("native_rows",[]),
                             (diag.get("F") or {}).get("observations",[])):
                    for row in rows:
                        lines=row.get("simc_error_lines",[])
                        for i,line in enumerate(lines):
                            for value in sensitive:
                                line=line.replace(value,"<redacted>")
                            lines[i]=line
            record["last_completed_stage"]="REAL_ENVIRONMENT_RETURNED"
            record["first_real_environment_summary"]=environment
            if not isinstance(environment,dict) or not (
                environment.get("ready") is True and
                environment.get("installed") is True):
                record["status"]="PENDING_REAL_FIRST_SEASON_INSTALL"
                record["first_blocker"]=(
                    "ORIGINAL_ENVIRONMENT_NOT_READY" if
                    not isinstance(environment,dict) else
                    str((environment.get("requires") or [
                        environment.get("status") or
                        "ORIGINAL_ENVIRONMENT_UNRESOLVED"])[0])[:100])
                save()
                return record
            require(environment["sha"] and
                    re.fullmatch("[a-f0-9]{64}",environment["sha"]) and
                    environment["build"] and
                    browser_snapshot(driver)["gear_sha"]==environment["sha"] and
                    type(environment["B"]) is int and
                    type(environment["T"]) is int and
                    environment["T"]>=environment["B"],
                    "REAL_FIRST_INSTALL_SHA_B_T_DRIFT")
            record["actual_real_installed_v212_sha256"]=environment["sha"]
            record["user_target_ilevel"]=environment["ilvl"]
            record["real_game_build"]=environment["build"]
            record["observed_B"]=environment["B"]
            record["observed_T"]=environment["T"]
            record["new_environment_native_calls"]=environment["native_calls"]
            # Choose only a validated option visible in this real browser.
            before=browser_snapshot(driver)["trinkets"]
            for trinket in dict.fromkeys(filter(None,before)):
                select_trinket(driver,int(trinket))
            require(browser_snapshot(driver)["trinkets"]==["",""],
                    "TRINKET_DEFAULTS_COULD_NOT_BE_CLEARED")
            cards=driver.find_elements(By.CSS_SELECTOR,
                        "#equipment-trinket-grid button[data-item-id]")
            choices=[]
            for card in cards:
                if card.is_enabled() and card.is_displayed():
                    physical=card.get_attribute("data-item-id")
                    if physical and physical.isdigit() and physical not in choices:
                        choices.append(physical)
                    if len(choices)==2:break
            if len(choices)<2:
                record["status"]="PENDING_REAL_FIRST_TRINKET_CHOICES"
                record["first_blocker"]="LESS_THAN_TWO_UI_TRINKETS"
                save()
                return record
            for physical in choices:select_trinket(driver,int(physical))
            record["actually_visible_trinkets"]=list(map(int,choices))
            # Use the product's ORIGINAL long-run start and actual worker.
            selected=browser_snapshot(driver)
            require(selected["gear_sha"]==environment["sha"] and
                    selected["start_label"]=="최적 스탯 찾기" and
                    not selected["start_disabled"],
                    "REAL_COLD_SECOND_USER_BUTTON_NOT_READY")
            request=driver.execute_script(
                "const r=buildRequest();return {sha:r.installed_manifest_sha256,"
                "build:r.installed_season_game_build,spec:r.controls.spec,"
                "trinkets:r.controls.trinket_ids};")
            require(request["sha"]==environment["sha"] and
                    request["build"]==environment["build"] and
                    request["spec"]=="destruction" and
                    request["trinkets"]==list(map(int,choices)),
                    "EXACT_USER_SELECTED_REQUEST_DRIFT")
            # Actual worker Native count is not captured by this browser receipt.
            record["new_dps_native_calls"]=None
            clickable(driver,driver.find_element(By.ID,"start-btn"))
            sid=WebDriverWait(driver,120).until(lambda d:d.execute_script(
                "return /^[a-f0-9]{20}$/.test(state.session||'')?"
                "state.session:null"))
            record["real_dps_session_id_sha256"]=hashlib.sha256(
                sid.encode()).hexdigest()
            # UI is a normal 64 native primary adaptive long-run. No
            # per-candidate custom executor, cache injection, fake API.
            WebDriverWait(driver,1750,poll_frequency=1).until(
                lambda d:d.execute_script(
                    "return state.longrunResultReady && !state.busy"))
            screen=browser_snapshot(driver)
            require(screen["result_visible"] and
                    screen["dps"] not in ("","–") and
                    screen["sem"] not in ("","–") and
                    screen["conf95"] not in ("","–"),
                    "ACTUAL_COLD_CHROME_RESULT_NOT_SHOWN")
            record["actual_browser_dps"]=screen["dps"]
            record["actual_browser_sem"]=screen["sem"]
            record["actual_browser_conf95"]=screen["conf95"]
            record["actual_first_user_result_screen"]=True
            record["last_completed_stage"]="REAL_USER_DPS_RESULT_VISIBLE"
            record["status"]="PASS_REAL_FIRST_USER_SOURCE_AND_DPS"
            save()
            return record
        except Exception as exc:
            record["status"]="BLOCKED_REAL_FIRST_USER"
            record["first_blocker"]=safe(exc)
            record["failure_after_stage"]=record.get("last_completed_stage")
            record["error_type"]=type(exc).__name__
            save()
            return record
        finally:
            if driver:
                try:driver.quit()
                except Exception:pass
            # Windows CI is ephemeral; explicit remove of source secrets
            # is still required. Never write plaintext secrets to artifact.
            try:
                if driver is not None and record.get(
                        "source_credentials_saved_via_real_browser"):
                    from p1_v345_windows_extracted_zip_cmd_browser_restore import (
                        http_json)
                    # Obtain only the local ephemeral CSRF token from the
                    # same UI; never capture, display or serialize secrets.
                    # http_json uses the original loopback POST endpoint.
                    # Some driver versions refuse execute_script after quit,
                    # so capture token earlier if needed.
                    token=local_token[0]
                    if token:
                        status,_=http_json(
                            "/api/v1/source-credentials/clear",
                            token=token,body={})
                        record["test_source_credentials_cleared"]=(
                            status==200)
                        save()
            except Exception:
                pass

    save()
    code=startup.run(
        args.zip,out,
        before_first_server=before,
        continue_after_cold_browser=continued)
    record["packaged_setup_exit_code"]=code
    save()
    print("V690_FIRST_USER_VERDICT "+json.dumps({
        k:record.get(k) for k in (
            "status","first_blocker","one_click_simc_binary_configured",
            "real_game_build","observed_T","real_dps_session_id_sha256",
            "actual_browser_dps","actual_browser_sem",
            "actual_browser_conf95")},sort_keys=True,ensure_ascii=True),
          flush=True)
    return 0 if record["status"]=="PASS_REAL_FIRST_USER_SOURCE_AND_DPS" else 2


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--zip",required=True,type=pathlib.Path)
    parser.add_argument("--out",required=True,type=pathlib.Path)
    args=parser.parse_args()
    sys.exit(stage(args))
