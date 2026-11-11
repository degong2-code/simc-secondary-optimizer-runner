#!/usr/bin/env python3
"""P1 v342: real Chrome UI clicks, synthetic 64-case worker; zero SimC Native.

All normal page assets/bootstrap/defaults are served by actual v113 localhost.
Only the explicit longrun session endpoints are intercepted by browser fetch.
This is UI contract evidence, NOT a 64-Native performance test.
"""
from __future__ import annotations
import json,os,pathlib,subprocess,sys,tempfile,time
from urllib.request import Request,urlopen
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

ROOT=pathlib.Path(__file__).resolve().parents[1]
PORT=8797
URL=f"http://127.0.0.1:{PORT}/"
SID="0123456789abcdef0123"
INSTALL=r"""
window.confirm=()=>true;
const original=window.fetch.bind(window);
const sid="0123456789abcdef0123";
window.__v342={phase:"IDLE",calls:[],payload:null};
const s=window.__v342;
const stat={crit_rating:1072,haste_rating:38,mastery_rating:1577,
            versatility_rating:420};
const alternative={crit_rating:1000,haste_rating:100,mastery_rating:1500,
                   versatility_rating:507};
const pct=v=>Object.fromEntries(Object.entries(v).map(([k,n])=>[k,100*n/3107]));
const userResult={
  confidence_level:0.95,global_optimum_proven:false,
  selected_pair_95_only:true,selection_multiplicity_corrected:false,
  base_B:3107,final_T:3107,
  fixed_O:{crit_rating:0,haste_rating:0,mastery_rating:0,versatility_rating:0},
  observed_first_choice:{absolute_rating_T:stat,percent_of_final_T:pct(stat),
    observed_dps_mean:123456.78,simc_sem:321.09},
  observed_unique_candidates:64,
  confirmation_pair_direction_supported_at_95:false,
  material_near_alternatives:[{
    absolute_rating_T:alternative,percent_of_final_T:pct(alternative),
    observed_dps_mean:122900,simc_sem:350,observed_dps_loss_pct:0.45,
    rating_moved_fraction_B:0.11,
    pairwise_95_label:"OBSERVED_NEAR_UNRESOLVED_AT_95"
  }]
};
window.fetch=async (resource,opts={})=>{
  const u=new URL(typeof resource==="string"?resource:resource.url,location.origin);
  const method=(opts.method||"GET").toUpperCase();
  const send=value=>new Response(JSON.stringify(value),{
    status:200,headers:{"Content-Type":"application/json"}});
  const pre="/api/v1/sessions/"+sid;
  if(u.pathname==="/api/v1/longrun/start"&&method==="POST"){
    s.calls.push("start");
    const p=JSON.parse(opts.body);
    if(p.max_native_calls!==64||p.continuous!==true||
       p.current_season_product!==true||p.controls.ilevel!==334||
       p.controls.oil_hands.length!==0||
       p.controls.trinket_ids.length!==2)
      throw Error("WRONG_PRIMARY_64_PAYLOAD");
    s.payload=p;s.phase="RUNNING";
    return send({session_id:sid,status:"LONGRUN_WORKER_STARTED",
                 native_attempt_ceiling_cumulative:64});
  }
  if(u.pathname===pre+"/longrun/status"&&method==="GET"){
    s.calls.push("status");
    const done=s.phase==="DONE",paused=s.phase==="PAUSED";
    const active=s.phase==="RUNNING"||s.phase==="RESUMED";
    const n=done?64:paused||s.phase==="RESUMED"?2:0;
    const st=done?"BUDGET_EXHAUSTED":paused?"PAUSED_USER_CANCEL":"RUNNING";
    return send({enabled:true,session_id:sid,active,
      native_budget:64,scout_iterations_per_CHMV:56,cancel_requested:paused,
      result_ready:done,native_calls_now:0,
      progress:{status:st,completed_jobs:n,planned_jobs:64,
                progress_percent:100*n/64,native_attempts:n,cache_hits:0,
                worker:{status:st}}});
  }
  if(u.pathname===pre+"/longrun/cancel"&&method==="POST"){
    s.calls.push("cancel");
    if(s.phase!=="RUNNING")throw Error("INVALID_CANCEL_PHASE");
    s.phase="PAUSED";
    return send({session_id:sid,status:"LONGRUN_CANCEL_REQUESTED_AFTER_CURRENT_NATIVE"});
  }
  if(u.pathname===pre+"/longrun/resume"&&method==="POST"){
    s.calls.push("resume");
    if(s.phase!=="PAUSED"||JSON.parse(opts.body).continuous!==true)
      throw Error("INVALID_CONTINUOUS_RESUME");
    s.phase="RESUMED";
    return send({session_id:sid,status:"LONGRUN_WORKER_STARTED",
                 native_attempt_ceiling_cumulative:64});
  }
  if(u.pathname===pre+"/longrun/result"&&method==="GET"){
    s.calls.push("result");
    if(s.phase!=="DONE")throw Error("PREMATURE_RESULT");
    return send({session_id:sid,status:"BUDGET_EXHAUSTED",
                 native_calls_cumulative:64,cache_hits_this_run:0,
                 scout_iterations_per_CHMV:56,user_result:userResult});
  }
  if(u.pathname===pre+"/inputs"&&method==="GET"){
    s.calls.push("inputs");
    const p=s.payload;
    if(!p)throw Error("MISSING_INPUTS");
    const c=p.controls;
    return send({session_id:sid,binary:p.binary,revision:p.revision,
      static_cache:p.static_cache,current_season_product:true,
      verified_oil_item_ids_by_hand:{},
      user:{
        character:{class:c.class,spec:c.spec,race:c.race,talents:c.talents},
        target:{ilevel:c.ilevel,final_T:c.final_T},
        combat:{targets:c.targets,duration_seconds:c.duration_seconds,
                raid_buffs:c.raid_buffs},
        trinkets:c.trinket_ids.map(item_id=>({item_id})),
        oil_hands:c.oil_hands,runeforge_by_hand:c.runeforge_by_hand||{},
        max_single_stat_percent:c.max_single_stat_percent,
        special_items:c.special_items,embellishments:c.embellishments,
        consumable_choices:c.consumable_choices,
        selected_season_enchants:c.enchant_choices||{}
      }
    });
  }
  return original(resource,opts);
};
if(state.pollTimer!==null){clearInterval(state.pollTimer);state.pollTimer=null;}
document.getElementById("binary").value="C:\\simc\\simc.exe";
document.getElementById("revision").value="710c2408bf";
if(buildRequest().controls.spec!=="retribution")
  throw Error("DEFAULT_SPEC_DRIFT");
"""

def need(ok,reason):
    if not ok: raise RuntimeError("V342_"+reason)

def wait_phase(driver,phase):
    WebDriverWait(driver,12).until(
        lambda d:d.execute_script("return window.__v342?.phase")==phase)

def run():
    out=ROOT/"out"/"v342";out.mkdir(parents=True,exist_ok=True)
    receipt={"schema":"v342_browser64_real_click_synthetic_http_v1",
             "status":"NOT_RUN","browser_actual":True,"synthetic_worker":True,
             "new_native_calls":0}
    with tempfile.TemporaryDirectory(prefix="v342-web-") as home:
        env=dict(os.environ,HOME=home,USERPROFILE=home)
        proc=subprocess.Popen([sys.executable,"-u",
           str(ROOT/"runner/v113_local_web_api.py"),"--port",str(PORT)],
           cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        driver=None
        try:
            for _ in range(100):
                need(proc.poll() is None,"LOCAL_SERVER_EXITED")
                try:
                    with urlopen(URL+"api/v1/health",timeout=1) as r:
                        if r.status==200:break
                except OSError:time.sleep(.1)
            else:need(False,"HEALTH_TIMEOUT")
            opts=Options()
            for flag in ("--headless=new","--no-sandbox","--disable-dev-shm-usage",
                         "--window-size=1440,950"):opts.add_argument(flag)
            driver=webdriver.Chrome(options=opts)
            driver.get(URL)
            wait=WebDriverWait(driver,25)
            wait.until(lambda d:d.find_element(By.ID,"start-btn").is_enabled())
            driver.execute_script(INSTALL)
            driver.find_element(By.ID,"start-btn").click()
            wait_phase(driver,"RUNNING")
            wait.until(lambda d:d.find_element(By.ID,"run-label").text=="진행 중")
            need(not driver.find_element(By.ID,"cancel-btn").get_property("disabled"),
                 "CANCEL_BUTTON_DISABLED")
            driver.find_element(By.ID,"cancel-btn").click()
            wait_phase(driver,"PAUSED")
            wait.until(lambda d:"취소됨" in d.find_element(By.ID,"run-label").text)
            need(not driver.find_element(By.ID,"resume-btn").get_property("disabled"),
                 "RESUME_BUTTON_DISABLED")
            driver.find_element(By.ID,"resume-btn").click()
            wait_phase(driver,"RESUMED")
            wait.until(lambda d:d.find_element(By.ID,"run-label").text=="진행 중")
            rendered=driver.execute_async_script("""
              const done=arguments[0];window.__v342.phase="DONE";
              pollOnce().then(()=>done({
                label:document.getElementById("run-label").textContent,
                progress:document.getElementById("progress-label").textContent,
                visible:!document.getElementById("filled-result").hidden,
                dps:document.getElementById("dps").textContent,
                sem:document.getElementById("sem").textContent,
                conf:document.getElementById("conf95").textContent,
                alternatives:document.getElementById("alt-count").textContent,
                resume_disabled:document.getElementById("resume-btn").disabled
              })).catch(e=>done({error:String(e)}));
            """)
            need(not rendered.get("error") and
                 "탐색 상한 완료" in rendered["label"] and
                 "64회" in rendered["progress"] and rendered["visible"] and
                 "123,456.8" in rendered["dps"] and
                 rendered["sem"]=="321.09" and rendered["conf"]=="미확정" and
                 "1개" in rendered["alternatives"] and
                 rendered["resume_disabled"],"FINAL64_UI_CONTRACT")
            driver.execute_script("""
              document.getElementById("filled-result").hidden=true;
              document.getElementById("empty-result").hidden=false;
            """)
            # The ID restore control sits inside a collapsed <details>.
            # Use the actual user action rather than a forced hidden click.
            driver.find_element(By.CSS_SELECTOR,"details.restore > summary").click()
            wait.until(lambda d:d.find_element(By.ID,"restore-btn").is_displayed())
            driver.find_element(By.ID,"restore-btn").click()
            wait.until(lambda d: not d.find_element(By.ID,"filled-result").
                       get_property("hidden"))
            need(driver.find_element(By.ID,"dps").text==rendered["dps"],
                 "RESTORE_RESULT_CHANGED")
            calls=driver.execute_script("return window.__v342.calls")
            need(all(calls.count(x)==1 for x in
                     ("start","cancel","resume","inputs")) and
                 calls.count("result")>=2,"CLICK_SEQUENCE_DRIFT")
            token=driver.execute_script("return state.token")
            request=Request(URL+"api/v1/sessions",headers={
                "x-simc-local-token":token,"Origin":URL.rstrip("/")})
            with urlopen(request,timeout=5) as res:
                listed=json.load(res)
            need(listed.get("read_only") is True and
                 listed.get("native_calls_now")==0 and
                 len(listed.get("sessions",[]))==0,
                 "FAKE_TEST_CREATED_REAL_JOB")
            receipt.update(status="PASS_REAL_BROWSER_SYNTHETIC_64_WORKFLOW",
                submitted_native_ceiling=64,
                click_sequence=["start","cancel","resume","result","restore"],
                verified_original_http_session_count=0,
                actual_simc_executed=False)
        finally:
            if driver:
                try:driver.quit()
                except Exception:pass
            proc.terminate()
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:proc.kill()
            (out/"V342_BROWSER64_RECEIPT.json").write_text(
                json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",
                encoding="utf8")
            print("V342_BROWSER64 "+json.dumps(receipt,ensure_ascii=False),flush=True)
    need(receipt["status"]=="PASS_REAL_BROWSER_SYNTHETIC_64_WORKFLOW",
         "DID_NOT_COMPLETE")

if __name__=="__main__":run()
