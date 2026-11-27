#!/usr/bin/env python3
"""One new real browser oil preparation + crafted-only auto-T boundary.

Reuse existing actual CLI, one same-build workspace and original v216/v113
owners. Base O=0 Build then selected named oil Build via ordinary browser
controls; reuse the BASE install for the previously untested automatic
crafted G delta + bounded DPS. Do not repeat the v806 mixed-weapon proof.
Only compact, allowlisted evidence leaves this isolated run.
"""
import argparse,hashlib,json,re,tempfile
from urllib.parse import quote
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select,WebDriverWait
from p1_v769_incremental_environment_once import (
    BUILD,REV,EphemeralActionsCredentials,digest,summary,need)
from p1_v580_windows_real_oil_chrome_manual_t_once import (
    start_http,browser_open,navigate,clickable,input_text,wait_idle)
from p1_v581_real_positive_oil_two_dps_native_cache_once import wait_quiet
from p1_v802_selected_mixed_oil_once import _safe_failure,observe_real_boundary
import v113_local_web_api as web
import v289_retail_live_build_source as retail
import v293_local_longrun_session as longrun

TARGET=334
FLASK=241324
OIL=243734
CRAFT=244579
MAX_BASE_NATIVE=24
MAX_VARIANT_NATIVE=24

# Exact app.js buildSeasonEnvironment(true) consent for the tested F+O
# selection, not a general acceptance rule for other dialogs or future UI.
SELECTED_ENVIRONMENT_CONFIRM = (
    "기존 검증 시즌 환경을 우선 재사용하고, 없으면 원본 구축을 시작할까요? "
    "필요 시 외부 네트워크를 사용할 수 있습니다."
    " 기존 G Native 최대 1회 실행될 수 있습니다."
    " 영약 F 후보만 최대 8회 신규 Native로 관측할 수 있습니다. 기름은 Native를 실행하지 않습니다."
    " 선택한 기름의 스케일링 값은 기존 실행 캐시를 먼저 재사용하고, 필요한 손에만 SimC 측정을 수행합니다."
)

def accept_selected_environment_confirm(browser, evidence, timeout=15):
    """Read the actual modal before any execute_script polling; accept once
    only for this exact stage. Unknown text is not logged or approved."""
    evidence.update(expected_code="SELECTED_F_O_BUILD_CONFIRM",
                    expected_text=SELECTED_ENVIRONMENT_CONFIRM,
                    status="WAITING")
    try:
        dialog=WebDriverWait(browser,timeout).until(EC.alert_is_present())
    except TimeoutException:
        evidence["status"]="MISSING"
        raise RuntimeError("V814_EXPECTED_SELECTED_ENVIRONMENT_CONFIRM_MISSING")
    actual=dialog.text
    evidence["observed_text_sha256"]=hashlib.sha256(actual.encode("utf8")).hexdigest()
    evidence["observed_text_length"]=len(actual)
    if actual!=SELECTED_ENVIRONMENT_CONFIRM:
        evidence["status"]="UNEXPECTED_NOT_ACCEPTED"
        raise RuntimeError("V814_UNEXPECTED_SELECTED_ENVIRONMENT_CONFIRM")
    evidence["observed_text"]=actual
    evidence["status"]="MATCHED"
    dialog.accept()
    evidence["status"]="ACCEPTED"

def preflight_selected_environment_confirm(evidence):
    """Real Chrome fixture, no season app/API/source/SimC calls. Exercise
    the same click, alert wait and exact comparison used by the real probe."""
    options=Options()
    for flag in ("--headless=new","--no-sandbox","--disable-dev-shm-usage",
                 "--window-size=1440,950"):
        options.add_argument(flag)
    browser=webdriver.Chrome(options=options)
    try:
        browser.get("data:text/html;charset=utf-8,"+quote(
            '<button id="prepare">Prepare</button>'))
        def click_confirm(message):
            browser.execute_script("""
                window.confirmResult=null;
                document.getElementById("prepare").onclick=()=>{
                    window.confirmResult=window.confirm(arguments[0]);
                };
            """,message)
            clickable(browser,browser.find_element(By.ID,"prepare"))
        click_confirm(SELECTED_ENVIRONMENT_CONFIRM)
        evidence["expected"]={}
        accept_selected_environment_confirm(browser,evidence["expected"])
        WebDriverWait(browser,10).until(lambda d:d.execute_script(
            "return window.confirmResult===true"))
        click_confirm("V814 unrelated confirmation fixture")
        evidence["unexpected"]={}
        try:
            accept_selected_environment_confirm(browser,evidence["unexpected"])
        except RuntimeError as exc:
            if str(exc)!="V814_UNEXPECTED_SELECTED_ENVIRONMENT_CONFIRM":
                raise
            # Fixture only: verify refusal left the unexpected alert open,
            # then dismiss it to clean up the test browser.
            dialog=browser.switch_to.alert
            need(dialog.text=="V814 unrelated confirmation fixture",
                 "V814_UNEXPECTED_FIXTURE_NOT_PRESERVED")
            dialog.dismiss()
            WebDriverWait(browser,10).until(lambda d:d.execute_script(
                "return window.confirmResult===false"))
        else:
            raise RuntimeError("V814_UNEXPECTED_FIXTURE_WAS_ACCEPTED")
        evidence["status"]="PASS_REAL_CHROME_EXPECTED_AND_UNEXPECTED_CONFIRM"
    finally:
        browser.quit()

class Credentials(EphemeralActionsCredentials):
    def status(self):
        return {"supported":True,"configured":self.load() is not None}

def safe_code(value):
    code=str(value).split(":",1)[0].split("\n",1)[0]
    return code if re.fullmatch(r"[A-Z][A-Z0-9_]{3,140}",code) else None

def run(args):
    out=Path(args.out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    report={"status":"STARTED","build":BUILD,"revision":REV,
            "target_ilevel":TARGET,"full_product_e2e":"PENDING",
            "quality_equivalence_verified":False,"global_optimum_proven":False,
            "dps_native":0,"browser_actual":False,"builds":[]}
    browser=server=thread=None
    def save(stage=None):
        if stage:report["stage"]=stage
        # Lossless JSON escapes keep the receipt safe on Windows CP1252 stdout.
        # Use the same bytes for file and console; readers recover the exact text.
        raw=json.dumps(report,sort_keys=True,ensure_ascii=True,allow_nan=False)
        (out/"V813_OIL_NAME_CRAFTED_AUTO_T.json").write_text(raw+"\n",encoding="utf8")
        print("V813_RECEIPT "+raw,flush=True)
    def check(code,actual,expected):
        if actual!=expected:
            report["failed_comparison"]={"code":code,"observed":actual,"expected":expected}
            save()
            raise RuntimeError(code)
    def api(method,path,payload=None):
        browser.set_script_timeout(180)
        result=browser.execute_async_script("""
          const [method,path,payload]=arguments,done=arguments[arguments.length-1];
          api(path,{method,payload}).then(value=>done({ok:true,value}))
            .catch(e=>done({ok:false,error:String(e?.message||e),
                           kind:e?.safeKind||null,status:e?.httpStatus||null}));
        """,method,path,payload)
        if not result.get("ok"):
            report["http_blocker"]={"code":safe_code(result.get("error")),
                "kind":result.get("kind"),"status":result.get("status")}
            save()
            raise RuntimeError("V813_ORIGINAL_HTTP_BLOCKED")
        return result["value"]
    def select(id,value):
        node=browser.find_element(By.ID,id)
        check("V813_CONTROL_VISIBLE_"+id.upper().replace("-","_"),node.is_displayed(),True)
        check("V813_CONTROL_ENABLED_"+id.upper().replace("-","_"),node.is_enabled(),True)
        Select(node).select_by_value(str(value))
    def open_fold(id):
        node=browser.find_element(By.ID,id)
        if not node.get_attribute("open"):
            clickable(browser,node.find_element(By.TAG_NAME,"summary"))
    def evidence(env):
        # Read existing source projections only; do not calculate effects.
        comp=env.get("source_compilation") or {}
        plan=comp.get("automatic_F_O_measurement_candidates_unadmitted") or {}
        raw=comp.get("unbuffed_oil_original_simc_source_unadmitted") or {}
        by_id={row["enchant_id"]:row for row in raw.get("items",[])}
        return [{"item_id":r["physical_item_id"],"quality":r["crafting_quality"],
                 "token":r["simc_input_token"],"enchant_id":r["simc_enchant_id"],
                 "raw_numeric_status":by_id.get(r["simc_enchant_id"],{}).get("status"),
                 "raw_numeric_reasons":by_id.get(r["simc_enchant_id"],{}).get("source_reason_codes"),
                 "min_ilevel":by_id.get(r["simc_enchant_id"],{}).get("source_min_ilevel"),
                 "max_ilevel":by_id.get(r["simc_enchant_id"],{}).get("source_max_ilevel")}
                for r in plan.get("oil",[]) if r.get("selected_hand")=="main_hand"][:32]
    try:
        report["confirmation_preflight"]={}
        save("CONFIRMATION_PREFLIGHT_NO_SOURCE_OR_NATIVE")
        preflight_selected_environment_confirm(report["confirmation_preflight"])
        save("PINNED_BINARY_AND_LIVE_BUILD")
        binary=Path(args.simc).resolve(strict=True)
        identity=json.loads(Path(args.identity).read_text("utf-8-sig"))
        check("V813_BINARY_BUILD",identity["game_build"],BUILD)
        check("V813_BINARY_REV",identity["source_commit"],REV)
        check("V813_BINARY_SHA",digest(binary),identity["binary_sha256"])
        report["binary_sha256"]=identity["binary_sha256"]
        check("V813_LIVE_BUILD",retail.discover(region="KR")["game_build"],BUILD)
        credentials=Credentials()
        need(credentials.load() is not None,"V813_SOURCE_CREDENTIALS_MISSING")
        with tempfile.TemporaryDirectory(prefix="v813-") as tmp:
            root=Path(tmp)/"runs";root.mkdir()
            app=web.create_app(root=root,token="v813-local-only",
                               source_credential_store=credentials)
            jobs=app.state.jobs
            original=jobs.build_season_environment
            # Observer only: original method executes and returns unchanged.
            def observed_build(*a,**kw):
                try:env=original(*a,**kw)
                except Exception as exc:
                    report.setdefault("original_build_failure",_safe_failure(exc))
                    save()
                    raise
                report["builds"].append(summary(env))
                if len(report["builds"])==1:
                    report["oil_quality_source_observations"]=evidence(env)
                save()
                return env
            jobs.build_season_environment=observed_build
            save("BASE_O_ZERO_BUILD")
            base=jobs.build_season_environment(game_build=BUILD,target_ilevel=TARGET,
                native_G_binary=str(binary),consumable_native_binary=str(binary),
                auto_native_F_requested=True,selected_flask_item_id=FLASK,
                selected_oil_item_ids_by_hand={},source_target_socket_count=4,
                simc_revision_hint=REV)
            check("V813_BASE_READY",base.get("environment_ready"),True)
            check("V813_BASE_INSTALLED",base.get("environment_installed"),True)
            check("V813_BASE_O",sum(base["O"].values()),0)
            need(0<=base["native_calls"]<=MAX_BASE_NATIVE,"V813_BASE_NATIVE_BOUND")
            base_install=base["source_compilation"]["verified_environment_install"]
            base_sha=base_install["manifest_sha256"]
            base_path=Path(base_install["stage_output_path"])
            base_bytes=digest(base_path)
            report["base_sha"]=base_sha
            with observe_real_boundary(report,root):
                save("SOURCE_NAME_CHOICES_BEFORE_INSTALL")
                data=jobs.installed_oil_loadouts(TARGET,BUILD)
                prep=data.get("oil_preparation_source") or {}
                check("V813_PREPARATION_SOURCE_STATUS",prep.get("status"),
                      "OIL_PREPARATION_SOURCE_IDENTIFIED")
                check("V813_PREPARATION_NATIVE",prep.get("native_calls"),0)
                check("V813_PREPARATION_NETWORK",prep.get("network_calls"),0)
                row=[r for r in prep["items"] if r["physical_item_id"]==OIL]
                check("V813_EXACT_PHYSICAL_SOURCE_COUNT",len(row),1)
                check("V813_UNVERIFIED_SOURCE_NOT_REGISTERED",row[0]["user_selectable"],False)
                check("V813_NO_POSITIVE_INSTALL_BEFORE_SELECTION",len(data["items"]),0)
                report["preparation_candidate_count"]=len(prep["items"])
                report["preparation_source_sha"]=prep["source_candidate_sha256"]
                save("REAL_CHROME_INPUT")
                server,thread=start_http(app)
                browser=browser_open()
                report["browser_actual"]=True
                browser.execute_script("""
                  const n=$("season-game-build");
                  n.value=arguments[0];
                  n.dispatchEvent(new Event("input",{bubbles:true}));
                  n.dispatchEvent(new Event("change",{bubbles:true}));
                """,BUILD)
                WebDriverWait(browser,120).until(lambda b:b.execute_script("""
                   return !state.busy && installedConsumableScopeMatches(state.oilCatalog)
                     && Array.from($("oil-preparation-main").options).some(
                       x=>x.value===String(arguments[0]));
                """,OIL))
                select("optimizer-oil-use-mode","off")
                wait_idle(browser,60)
                select("season-verified-flask",FLASK)
                wait_idle(browser,60)
                # Re-dispatch real DOM change if a unique F was already chosen.
                if browser.execute_script("return state.seasonGear?.installed_manifest_sha256")!=base_sha:
                    browser.execute_script('$("season-verified-flask").dispatchEvent(new Event("change",{bubbles:true}))')
                    wait_idle(browser,60)
                check("V813_BROWSER_BASE_BIND",browser.execute_script(
                    "return state.seasonGear?.installed_manifest_sha256||null"),base_sha)
                navigate(browser,"settings")
                open_fold("simc-technical-panel")
                input_text(browser,"binary",str(binary))
                input_text(browser,"revision",REV)
                wait_idle(browser,60)
                navigate(browser,"optimizer")
                open_fold("env-oil-options")
                open_fold("oil-preparation-panel")
                check("V813_NAME_CONTROL_OUTSIDE_EXPERT",browser.execute_script("""
                    return !$("optimizer-season-itemid-expert").contains($("oil-preparation-main"));
                """),True)
                select("oil-preparation-main",OIL)
                selected=browser.execute_script("""return {
                    id:field("optimizer-oil-main-id"),flask:field("season-selected-flask-id"),
                    intent:oilUseIntent,ready:state.seasonGearTargetIlevel,
                    old_budget:field("season-verified-budget")
                }""")
                report["browser_selected_intent"]=selected
                check("V813_BROWSER_PHYSICAL_OIL",selected["id"],str(OIL))
                check("V813_BROWSER_F_PRESERVED",selected["flask"],str(FLASK))
                check("V813_BROWSER_OIL_INTENT",selected["intent"],True)
                check("V813_BROWSER_OLD_READY_REVOKED",selected["ready"],None)
                check("V813_BROWSER_OLD_BUDGET_REVOKED",selected["old_budget"],"")
                check("V813_NAME_SELECTION_NO_BUILD",len(report["builds"]),1)
                save("BROWSER_SELECTED_ENVIRONMENT_PREPARE")
                report["selected_environment_confirmation"]={}
                clickable(browser,browser.find_element(By.ID,"user-variant-prepare-btn"))
                accept_selected_environment_confirm(
                    browser,report["selected_environment_confirmation"])
                save("BROWSER_SELECTED_ENVIRONMENT_CONFIRM_ACCEPTED")
                wait_idle(browser,720)
                report["browser_preparation_technical_code"]=safe_code(
                    browser.execute_script("return state.lastUserBlocker?.technical||null"))
                check("V813_ONE_SELECTED_BUILD",len(report["builds"]),2)
                variant=report["builds"][1]
                check("V813_VARIANT_READY",variant["environment_ready"],True)
                check("V813_VARIANT_INSTALLED",variant["environment_installed"],True)
                need(type(variant["native_calls"]) is int and
                     0<=variant["native_calls"]<=MAX_VARIANT_NATIVE,
                     "V813_VARIANT_NATIVE_BOUND")
                oil_sha=variant["installed_manifest_sha256"]
                need(type(oil_sha) is str and oil_sha!=base_sha,"V813_POSITIVE_INSTALL_SHA_REQUIRED")
                check("V813_POSITIVE_O",sum(variant["budget"]["O"].values())>0,True)
                check("V813_REGISTERED_BROWSER_OIL",browser.execute_script(
                    "return !!selectedFullVerifiedOil()"),True)
                check("V813_BROWSER_BOUND_POSITIVE_SHA",browser.execute_script(
                    "return state.seasonGear?.installed_manifest_sha256||null"),oil_sha)
                check("V813_BASE_INSTALL_BYTES_UNCHANGED",digest(base_path),base_bytes)
                report["oil_registration_pass"]=True
                save("CRAFTED_ONLY_AUTO_T_PREPARE")
                # Same exact BASE install, no new environment Build; this
                # is a real HTTP/Native test, not a claim of browser crafting.
                controls=web.sessions.standard_controls(("hunter","survival"))
                controls.update(race="human",oil_hands=[],final_T=None,
                    embellishments=[{"slot":"head","item_id":CRAFT,
                         "options":{"crafted_stats":"32/36","embellishment":"arcanoweave_lining"}}])
                request={"controls":controls,"binary":str(binary),"revision":REV,
                    "current_season_product":True,"installed_season_game_build":BUILD,
                    "installed_manifest_sha256":base_sha,"selected_flask_item_id":FLASK,
                    "selected_oil_item_ids_by_hand":{},"user_socket_total":4}
                longreq={**request,"max_native_calls":12,
                          "max_new_native_this_invocation":1,"max_elapsed_seconds":360}
                p=api("POST","/api/v1/longrun/prepare",longreq)
                report["crafted_prepare"]={k:p.get(k) for k in (
                    "status","new_dps_native_calls","static_L_native_calls_this_start",
                    "selected_G_delta_native_calls_this_start",
                    "selected_static_native_calls_this_start","selected_oil_native_calls_this_start")}
                receipt=p.get("static_L_start_receipt") or {}
                report["crafted_prepare"]["selected_special_count"]=receipt.get("selected_special_count")
                report["crafted_prepare"]["selected_G_delta"]=receipt.get("selected_G_delta")
                save()
                check("V813_CRAFTED_PREPARE_STATUS",p.get("status"),
                      "LONGRUN_SOURCE_PREPARED_NO_DPS_NATIVE")
                check("V813_CRAFTED_PREPARE_DPS",p.get("new_dps_native_calls"),0)
                check("V813_CRAFTED_NO_LOCKED_L",p.get("static_L_native_calls_this_start"),0)
                check("V813_CRAFTED_NO_SELECTED_SPECIAL",receipt.get("selected_special_count"),0)
                delta=p.get("selected_G_delta_native_calls_this_start")
                need(type(delta) is int and 0<=delta<=2,"V813_CRAFTED_G_DELTA_NATIVE_BOUND")
                sid=p["session_id"]
                profile=root/sid/"generated"/"profile.simc"
                line=next((x for x in profile.read_text("utf8").splitlines()
                           if x.startswith("head=")),"")
                check("V813_CRAFTED_HEAD_PRESENT",bool(re.search(r"(?:^|,)id="+str(CRAFT)+r"(?:,|$)",line)),True)
                check("V813_CRAFTED_STATS_PRESENT","crafted_stats=32/36" in line,True)
                check("V813_CRAFTED_EMBELLISHMENT_PRESENT","embellishment=arcanoweave_lining" in line,True)
                save("CRAFTED_READ_ONLY_AUTO_T_PLAN")
                plan=api("POST","/api/v1/sessions/plan",request)
                check("V813_CRAFTED_PLAN_STATUS",plan.get("status"),"READY_ZERO_NATIVE")
                check("V813_CRAFTED_PLAN_NATIVE",plan.get("native_calls"),0)
                check("V813_CRAFTED_PLAN_SESSION",plan.get("session_id")==sid,True)
                budget=plan["plan"]
                check("V813_CRAFTED_AUTO_BUDGET_SOURCE",budget.get("budget_source"),
                      "ADMITTED_SELECTED_FRESH_SEASON_B8_V436")
                check("V813_CRAFTED_NO_MANUAL_T",budget.get("user_manual_final_T"),None)
                check("V813_CRAFTED_AUTO_T_ACCOUNTING",budget["final_T"],budget["base_B"]+sum(budget["fixed_O"].values()))
                report["crafted_B"]=budget["base_B"];report["crafted_T"]=budget["final_T"]
                save("CRAFTED_REPREPARE_CACHE")
                replay=api("POST","/api/v1/longrun/prepare",longreq)
                check("V813_CRAFTED_REPREPARE_SAME_SESSION",replay.get("session_id")==sid,True)
                check("V813_CRAFTED_REPREPARE_STATIC_NATIVE",replay.get("selected_static_native_calls_this_start"),0)
                url="/api/v1/sessions/"+sid
                def cases():
                    cfg=longrun.config(root/sid)
                    folder=longrun.stage_path(root/sid,cfg["native_budget"])/"simc_results"/"cases"
                    return [{name:digest(p/name) for name in ("input.simc","result.json","native_receipt.json")}
                            for p in sorted(folder.glob("case_*/native"))
                            if all((p/name).is_file() for name in
                                   ("input.simc","result.json","native_receipt.json"))]
                seen=[]
                for count in (1,2):
                    save("CRAFTED_DPS_NATIVE_"+str(count))
                    api("POST",url+"/longrun/resume",{"max_new_native_this_invocation":1,
                                                     "max_elapsed_seconds":360})
                    status=wait_quiet(browser,sid)
                    progress=status["progress"]
                    report["dps_native"]=progress["native_attempts"]
                    check("V813_CRAFTED_DPS_ATTEMPTS",progress["native_attempts"],count)
                    check("V813_CRAFTED_DPS_COMPLETED",progress["completed_jobs"],count)
                    current=cases()
                    check("V813_CRAFTED_DPS_CASE_COUNT",len(current),count)
                    check("V813_CRAFTED_DPS_OLD_BYTES",current[:len(seen)]==seen,True)
                    seen=current
                save("CRAFTED_CACHE_ONLY")
                api("POST",url+"/longrun/cache-only",{})
                status=wait_quiet(browser,sid)
                check("V813_CRAFTED_CACHE_ATTEMPTS",status["progress"]["native_attempts"],2)
                check("V813_CRAFTED_CACHE_BYTES",cases()==seen,True)
                result=api("GET",url+"/longrun/result")
                user=result["user_result"];best=user["observed_first_choice"]
                check("V813_CRAFTED_RESULT_T",sum(best["absolute_rating_T"].values()),budget["final_T"])
                check("V813_CRAFTED_RESULT_95",user["confidence_level"],.95)
                check("V813_CRAFTED_RESULT_NOT_GLOBAL_PROOF",user["global_optimum_proven"],False)
                need(best["observed_dps_mean"]>0 and best["simc_sem"]>=0,"V813_CRAFTED_DPS_OR_SEM_INVALID")
                check("V813_NO_ADDITIONAL_BUILDS",len(report["builds"]),2)
                report.update(status="PASS_REAL_OIL_NAME_REGISTRATION_CRAFTED_AUTO_T_TWO_DPS_CACHE",
                    cases=seen,dps=best["observed_dps_mean"],sem=best["simc_sem"],
                    rating=best["absolute_rating_T"])
                return 0
    except Exception as exc:
        report["status"]="BLOCKED"
        report["first_blocker"]=safe_code(exc) or type(exc).__name__
        report.setdefault("probe_failure",_safe_failure(exc))
        return 2
    finally:
        if browser:
            try:browser.quit()
            except Exception:pass
        if server:
            server.should_exit=True
            if thread:thread.join(timeout=30)
        save()

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for name in ("simc","identity","out"):p.add_argument("--"+name,required=True)
    raise SystemExit(run(p.parse_args()))
