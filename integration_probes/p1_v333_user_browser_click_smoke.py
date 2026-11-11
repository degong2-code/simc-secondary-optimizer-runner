#!/usr/bin/env python3
"""P1: real Chrome click smoke, localhost-only, no SimC binary or Native."""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

ROOT=pathlib.Path(__file__).resolve().parents[1]
URL="http://127.0.0.1:8765/"

def need(ok,code):
    if not ok: raise RuntimeError("V333_"+code)

def select_label(driver,field,query,expected):
    wait=WebDriverWait(driver,12)
    search=wait.until(lambda d:d.find_element(By.ID,"choice-"+field))
    need(search.is_displayed(),"SEARCH_NOT_VISIBLE")
    search.click()
    search.send_keys(Keys.CONTROL,"a")
    search.send_keys(query)
    options=wait.until(lambda d:d.find_elements(By.CSS_SELECTOR,
        "#choice-"+field+"-results button.choice-result"))
    matching=[x for x in options if expected in x.text]
    need(matching,"MISSING_SEARCH_RESULT_"+field)
    matching[0].click()

def main():
    report={"schema":"v333_user_browser_smoke_v1","status":"NOT_STARTED",
            "new_native_calls":0,"new_session_calls":0}
    out=ROOT/"out";out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="v333-web-") as home:
        env=dict(os.environ,HOME=home,USERPROFILE=home)
        server=subprocess.Popen([sys.executable,"-u",
            str(ROOT/"runner/v113_local_web_api.py"),"--port","8765"],
            cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        driver=None
        try:
            for _ in range(100):
                need(server.poll() is None,"SERVER_EXITED")
                try:
                    with urlopen(URL+"api/v1/health",timeout=1) as r:
                        if r.status==200:break
                except OSError:time.sleep(.1)
            else:need(False,"SERVER_NOT_READY")
            options=Options()
            for arg in ("--headless=new","--no-sandbox","--disable-dev-shm-usage",
                        "--window-size=1440,950"):
                options.add_argument(arg)
            driver=webdriver.Chrome(options=options)
            driver.get(URL)
            wait=WebDriverWait(driver,25)
            wait.until(lambda d:d.find_element(By.ID,"class-choice").is_enabled())
            need(len(driver.find_elements(By.CSS_SELECTOR,
                "#class-choice option"))==13,"CLASS_COUNT")
            select_label(driver,"class-choice","드루이드","드루이드")
            select_label(driver,"spec","조화","조화")
            need(driver.find_element(By.ID,"spec").get_attribute("value")==
                 "druid/balance","SPEC_VALUE")
            need(driver.find_element(By.ID,"race").get_attribute("value")==
                 "나이트 엘프","DRUID_RACE")
            select_label(driver,"class-choice","기원사","기원사")
            need(driver.find_element(By.ID,"spec").get_attribute("value")==
                 "evoker/devastation","EVOKER_SPEC")
            need(driver.find_element(By.ID,"race").get_attribute("value")==
                 "드랙티르","EVOKER_RACE")
            roster=[o.get_attribute("value") for o in
                driver.find_elements(By.CSS_SELECTOR,"#race-list option")]
            need(roster==["드랙티르"],"EVOKER_ROSTER")
            # v336: actual browser fetches the immutable 64/64 official
            # Blizzard source by exact installed game build, with no Native.
            verified=driver.execute_async_script("""
                const done=arguments[0];
                refreshOfficialGameTerms('12.1.5.70783').then(()=>
                    done({status:document.getElementById('season-terms-status').textContent,
                          spec:document.getElementById('spec').value,
                          race:document.getElementById('race').value}))
                .catch(e=>done({error:String(e)}));
            """)
            need(not verified.get("error") and
                 "공식 한국어 게임 용어 확인 64종" in verified["status"],
                 "V336_VERIFIED_KO_TERMS_NOT_APPLIED")
            need(verified["spec"]=="evoker/devastation" and
                 verified["race"]=="드랙티르",
                 "V336_SOURCE_CHANGED_SIMC_CHARACTER_SELECTION")
            select_label(driver,"class-choice","악마사냥꾼","악마사냥꾼")
            select_label(driver,"spec","포식","포식")
            need(driver.find_element(By.ID,"spec").get_attribute("value")==
                 "demonhunter/devourer","V336_DEVOURER_OFFICIAL_NAME_ID_DRIFT")
            select_label(driver,"class-choice","기원사","기원사")
            need(len(driver.find_elements(By.CSS_SELECTOR,
                 "#trinket1 option"))==64,"TRINKETS_63")
            select_label(driver,"trinket1","메레크타","메레크타의 송곳니")
            need(driver.find_element(By.ID,"trinket1").get_attribute("value")==
                 "158367","OFFICIAL_ID")
            need(not driver.find_element(By.ID,"binary").get_attribute("value"),
                 "UNEXPECTED_SIMC_CONFIG")
            driver.find_element(By.ID,"start-btn").click()
            wait.until(lambda d:"연결 설정을 먼저 완료" in
                       d.find_element(By.ID,"notice").text)
            need(driver.find_element(By.ID,"simc-technical-panel").
                 get_attribute("open") is not None,"SIMC_SETUP_NOT_SHOWN")
            # The ID is inside a deliberately hidden developer-only node;
            # Selenium .text omits hidden text even when no job was started.
            need(driver.find_element(By.ID,"session-id").
                 get_property("textContent").strip()=="없음",
                 "UNEXPECTED_JOB")
            api_traffic=driver.execute_script(
                "return performance.getEntriesByType('resource').filter("+
                "e=>e.name.includes('/longrun/start')).length")
            need(api_traffic==0,"UNEXPECTED_NATIVE_START_REQUEST")
            # Browser runtime regression: a previous V291_RESULT.json remains
            # ready while the same sealed session is being resumed. Do not
            # show the old "final" DPS as the active worker's new result.
            # Synthetic display state only: no API start, session or Native.
            active_view=driver.execute_script("""
                const filled=document.getElementById('filled-result');
                filled.hidden=false;
                renderProgress({enabled:true,active:true,result_ready:true,
                  progress:{status:'RUNNING',planned_jobs:64,
                    completed_jobs:16,progress_percent:25,
                    worker:{status:'RUNNING'}}});
                return {filled_hidden:filled.hidden,
                  empty_visible:!document.getElementById('empty-result').hidden,
                  running:document.getElementById('run-label').textContent,
                  progress:document.getElementById('progress-label').textContent};
            """)
            need(active_view["filled_hidden"] and active_view["empty_visible"]
                 and active_view["running"]=="진행 중"
                 and "평가 16회" in active_view["progress"],
                 "ACTIVE_RESUME_STALE_RESULT_VISIBLE")
            report.update(status="PASS",classes=13,supported_dps=26,
                          active_resume_stale_result_hidden=True,
                          verified_official_game_terms=64,
                          verified_source_build="12.1.5.70783",
                          displayed_official_trinkets=63,selected_item_id=158367,
                          known_evoker_races=roster)
        finally:
            if driver is not None:
                try:driver.save_screenshot(str(out/"v333_user_browser.png"))
                except Exception:pass
                driver.quit()
            server.terminate()
            try:server.wait(timeout=5)
            except subprocess.TimeoutExpired:server.kill()
            (out/"v333_user_browser_receipt.json").write_text(
                json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                encoding="utf8")
            print("V333_BROWSER "+json.dumps(report,ensure_ascii=False),flush=True)

if __name__=="__main__":main()
