#!/usr/bin/env python3
"""v569 actual Chrome first-user clicks; local v113 server, synthetic Build,
synthetic gear and DPS route. Zero Native and external season data calls."""
import json,os,pathlib,subprocess,sys,tempfile,time
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

ROOT=pathlib.Path(__file__).resolve().parents[1]
URL="http://127.0.0.1:8795/"
INSTALL=r"""
const originalFetch=window.fetch.bind(window);
const SHA="a".repeat(64), BUILD="12.1.5.70783";
window.__v569={mode:"cancel",calls:[],builds:0,gears:0,dps:0};
window.confirm=()=>window.__v569.mode!=="cancel";
window.fetch=async (resource,config={})=>{
 const u=new URL(typeof resource==="string"?resource:resource.url,location.origin);
 const p=u.pathname,m=(config.method||"GET").toUpperCase(),s=window.__v569;
 const reply=x=>new Response(JSON.stringify(x),{status:200,
    headers:{"Content-Type":"application/json"}});
 if(p==="/api/v1/environment/myth-target"&&m==="POST"){
   s.calls.push("myth");return reply({
    status:"MYTH_TARGET_CANDIDATE_FROM_MATCHED_WAGO_V163_SOURCE",
    target_ilevel:334,game_build:BUILD,currency_csv_sha256:"b".repeat(64)});
 }
 if(p==="/api/v1/environment/season-build"&&m==="POST"){
   s.builds++;s.calls.push("build");
   const body=JSON.parse(config.body);
   if(body.auto_initial_core_build!==true||
      body.auto_myth_target_source_build!==BUILD||
      body.auto_myth_target_source_sha256!=="b".repeat(64))
     throw Error("V569_WRONG_BUILD_REQUEST");
   if(s.mode==="pending")return reply({
     web_environment_scope:{game_build:BUILD,target_ilevel:334,
       environment_ready:false,environment_installed:false},
     zero_history_build:{requires:["GEM_J_PENDING"]},
     source_compilation:{missing:[]}});
   return reply({status:"VERIFIED_INSTALLED_SAME_SEASON_SOURCE_REUSED",
     installed_manifest_sha256:SHA,installed_source_game_build:BUILD,
     verified_v113_profile_source_restored:true,
     G:2850,J:92,F:165,O:0,B:3107,T:3107,
     web_environment_scope:{game_build:BUILD,target_ilevel:334,
       active_season_reverified_in_this_lookup:true,
       environment_ready:true,environment_installed:true}});
 }
 if(p==="/api/v1/season-gear"&&m==="GET"&&u.searchParams.has("installed_manifest_sha256")){
   s.gears++;s.calls.push("gear");
   if(u.searchParams.get("installed_manifest_sha256")!==SHA)
     throw Error("V569_WRONG_GEAR_QUERY_SHA");
   return reply({status:"CURRENT_SEASON_CANDIDATE_SELECTION_ONLY",
     source_scope:"VERIFIED_INSTALLED_V212_SOURCE_V213_CANDIDATES",
     installed_manifest_sha256:s.mode==="wrong-sha"?"c".repeat(64):SHA,
     season_build:BUILD,weapon_forms:{"paladin/retribution":"two_hand"},
     choices:{trinket:[{item_id:910001,name:"Synthetic Alpha"},
                         {item_id:910002,name:"Synthetic Beta"}],
       special_effect_gear_candidate:[],selectable_stat_craft:[]}});
 }
 if(p==="/api/v1/longrun/start"&&m==="POST"){
   s.calls.push("dps");s.dps++;
   const body=JSON.parse(config.body);s.last=body;
   if(body.installed_manifest_sha256!==SHA||
      body.installed_season_game_build!==BUILD||
      body.controls.trinket_ids.join(",")!=="910001,910002")
     throw Error("V569_WRONG_DPS_SHA_OR_IDS");
   return reply({session_id:"0123456789abcdef0123",status:"QUEUED"});
 }
 if(p.endsWith("/longrun/status"))return reply({enabled:true,active:false,
   result_ready:false,progress:{status:"QUEUED",completed_jobs:0,planned_jobs:64,
   progress_percent:0,worker:{status:"QUEUED"}}});
 if(p.endsWith("/longrun/result"))return reply({status:"PENDING",result_ready:false});
 return originalFetch(resource,config);
};
"""
def need(condition,code):
    if not condition:raise RuntimeError("V569_"+code)
def snap(d):
    return d.execute_script("""
      const s=window.__v569;
      return {builds:s.builds,gears:s.gears,dps:s.dps,
       label:document.getElementById("start-btn").textContent,
       disabled:document.getElementById("start-btn").disabled,
       notice:document.getElementById("notice").textContent,
       sha:state.seasonGear?.installed_manifest_sha256||null,
       level:state.seasonGearTargetIlevel,
       build:state.verifiedInstalledBuildFromThisPage,
       trinkets:[field("trinket1"),field("trinket2")]};
    """)
def idle(d):
    WebDriverWait(d,30).until(lambda x:x.execute_script("return !!state.token&&!state.busy"))
def click(d):
    button=d.find_element(By.ID,"start-btn")
    d.execute_script("arguments[0].scrollIntoView({block:'center',behavior:'instant'})",button)
    WebDriverWait(d,12).until(lambda x:x.execute_script("""
        const b=document.getElementById('start-btn');
        const r=b.getBoundingClientRect();
        const top=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);
        return !b.disabled && r.top>=0 && r.bottom<=innerHeight &&
          (top===b || b.contains(top));
    """))
    button.click()
    idle(d)
def main():
    out=ROOT/"out"/"v569";out.mkdir(parents=True,exist_ok=True)
    receipt={"schema":"v569_chrome_first_user_synthetic_http_v1","status":"NOT_RUN",
      "browser_real":False,"build_mocked":True,"dps_mocked":True,
      "native_calls":0,"external_source_calls":0}
    with tempfile.TemporaryDirectory(prefix="v569-") as root:
        env={**os.environ,"HOME":root,"USERPROFILE":root}
        p=subprocess.Popen([sys.executable,"-u",
          str(ROOT/"runner/v113_local_web_api.py"),"--port","8795"],
          cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        d=None
        try:
            for _ in range(160):
                need(p.poll() is None,"SERVER_EXIT")
                try:
                    with urlopen(URL+"api/v1/health",timeout=1) as rsp:
                        if rsp.status==200:break
                except OSError:time.sleep(.1)
            else:need(False,"SERVER_HEALTH_TIMEOUT")
            opts=Options()
            for a in ("--headless=new","--no-sandbox","--disable-dev-shm-usage",
                      "--window-size=1440,950"):opts.add_argument(a)
            d=webdriver.Chrome(options=opts)
            receipt["browser_real"]=True
            d.get(URL)
            WebDriverWait(d,35).until(lambda x:x.execute_script(
                "return !!state.token && state.defaults.length===26 && "+
                "document.getElementById('start-btn').textContent.includes('시즌 환경 준비') && "+
                "!state.busy"))
            d.execute_script(INSTALL)
            cold=snap(d)
            print("V569_COLD_SCREEN "+json.dumps(cold,ensure_ascii=False),flush=True)
            need(cold["label"]=="시즌 환경 준비 · 장신구 목록 불러오기"
              and not cold["disabled"],"COLD_BUTTON_NOT_CLICKABLE")
            click(d)
            need(snap(d)["builds"]==0 and snap(d)["dps"]==0,"CANCEL_NOT_SAFE")
            d.execute_script("window.__v569.mode='pending'")
            click(d)
            need(snap(d)["builds"]==1 and snap(d)["gears"]==0 and
                 snap(d)["dps"]==0 and "SEASON_INITIAL_USER_BUILD_READY_REQUIRED"
                 in snap(d)["notice"],"PENDING_NOT_BLOCKED")
            d.execute_script("window.__v569.mode='wrong-sha'")
            click(d)
            need(snap(d)["builds"]==2 and snap(d)["gears"]==1 and
                 snap(d)["sha"] is None and snap(d)["dps"]==0,
                 "MISSMATCHED_SHA_ADMITTED")
            d.execute_script("window.__v569.mode='ready'")
            click(d)
            s=snap(d)
            need(s["builds"]==3 and s["gears"]==2 and s["dps"]==0
                 and s["sha"]=="a"*64 and s["level"]==334
                 and s["build"]=="12.1.5.70783" and s["disabled"],
                 "READY_GEAR_STAGE_WRONG")
            for item in ("910001","910002"):
                el=d.find_element(By.CSS_SELECTOR,
                  "#equipment-trinket-grid button[data-item-id='"+item+"']")
                d.execute_script("arguments[0].scrollIntoView()",el)
                el.click()
            oil=d.find_element(By.ID,"optimizer-oil-enabled")
            if oil.is_selected():oil.click()
            d.execute_script("""
              document.getElementById("binary").value="C:\\\\simc\\\\simc.exe";
              document.getElementById("revision").value="710c2408bf";
              buttonState(state.running,state.longrunResultReady);
            """)
            s=snap(d)
            need(s["trinkets"]==["910001","910002"] and not s["disabled"]
                 and s["dps"]==0,"SECOND_CLICK_NOT_AVAILABLE")
            click(d);s=snap(d)
            need(s["dps"]==1 and s["builds"]==3 and s["gears"]==2,
                 "SAME_SHA_SECOND_CLICK_NOT_USED")
            receipt.update(status="PASS_REAL_CHROME_FIRST_CLICK_SYNTHETIC_HTTP",
              build_requests=3,gear_requests=2,dps_requests_synthetic=1,
              first_click_native_zero=True,wrong_sha_rejected=True,
              user_selected_two_trinkets=True)
        finally:
            if d:d.quit()
            p.terminate()
            try:p.wait(timeout=5)
            except subprocess.TimeoutExpired:p.kill()
            (out/"V569_BROWSER_BRIDGE_RECEIPT.json").write_text(
              json.dumps(receipt,ensure_ascii=False,sort_keys=True,
                         indent=2)+"\n",encoding="utf8")
            print("V569_BROWSER "+json.dumps(receipt,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
