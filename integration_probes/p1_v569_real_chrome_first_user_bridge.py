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
const SHA="a".repeat(64), NEW_SHA="d".repeat(64), BUILD="12.1.5.70783";
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
      (s.builds<=3&&(body.auto_myth_target_source_build!==BUILD||
       body.auto_myth_target_source_sha256!=="b".repeat(64))))
     throw Error("V569_WRONG_BUILD_REQUEST");
   const level=body.target_ilevel;
   if(level!==(s.builds<=3?334:330))throw Error("V840_WRONG_TARGET_LEVEL");
   if(s.mode==="pending")return reply({
     web_environment_scope:{game_build:BUILD,target_ilevel:level,
       environment_ready:false,environment_installed:false},
     zero_history_build:{requires:["GEM_J_PENDING"]},
     source_compilation:{missing:[]}});
   return reply({status:"VERIFIED_INSTALLED_SAME_SEASON_SOURCE_REUSED",
     installed_manifest_sha256:level===330?NEW_SHA:SHA,installed_source_game_build:BUILD,
     verified_v113_profile_source_restored:true,
     G:2850,J:92,F:165,O:0,B:3107,T:3107,
     web_environment_scope:{game_build:BUILD,target_ilevel:level,
       active_season_reverified_in_this_lookup:true,
       environment_ready:true,environment_installed:true}});
 }
 if(p==="/api/v1/season-gear"&&m==="GET"&&u.searchParams.has("installed_manifest_sha256")){
   s.gears++;s.calls.push("gear");
   const expected=Number(u.searchParams.get("target_ilevel"))===330?NEW_SHA:SHA;
   if(u.searchParams.get("installed_manifest_sha256")!==expected)
     throw Error("V569_WRONG_GEAR_QUERY_SHA");
   return reply({status:"CURRENT_SEASON_CANDIDATE_SELECTION_ONLY",
     source_scope:"VERIFIED_INSTALLED_V212_SOURCE_V213_CANDIDATES",
     installed_manifest_sha256:s.mode==="wrong-sha"?"c".repeat(64):expected,
     season_build:BUILD,weapon_forms:{"paladin/retribution":"two_hand"},
     selected_slot_inventory:{two_hand:{head:[1]}},
     choices:{trinket:[{item_id:910001,name:"Synthetic Alpha"},
                         {item_id:910002,name:"Synthetic Beta"}],
       special_effect_gear_candidate:[{item_id:910003,name:"Synthetic Special",
        inventory_type:1,class_id:4,subclass_id:4}],selectable_stat_craft:[]}});
 }
 if(p==="/api/v1/season-gear/refresh"||p==="/api/v1/season-item-icons"||
    p==="/api/v1/environment/official-game-terms")
   return reply({});
 if(p==="/api/v1/verified-oil-loadouts")
   return reply({schema:"v113_verified_installed_oil_loadouts_v1",game_build:BUILD,
     target_ilevel:Number(u.searchParams.get("ilevel")),items:[]});
 if(p==="/api/v1/longrun/start"&&m==="POST"){
   s.calls.push("dps");s.dps++;
   const body=JSON.parse(config.body);s.last=body;
   if(body.installed_manifest_sha256!==NEW_SHA||
      body.installed_season_game_build!==BUILD||
      body.controls.trinket_ids.join(",")!=="910001,910002"||
      body.controls.ilevel!==330)
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
       trinkets:[field("trinket1"),field("trinket2")],
       special:[...document.querySelectorAll('#special-rows select[data-field="item_id"]')]
          .map(x=>x.value).filter(Boolean),
       specialLevel:document.querySelector('#special-rows [data-field="ilevel"]').value,
       specialHistoric:document.querySelector('#special-rows select[data-field="item_id"]')
          .selectedOptions[0]?.dataset.historic||null};
    """)
def idle(d):
    WebDriverWait(d,30).until(lambda x:x.execute_script("return !!state.token&&!state.busy"))
def click(d):
    if d.execute_script("return currentView")!="optimizer":
        d.find_element(By.CSS_SELECTOR,
          'header.topbar button[data-view="optimizer"]').click()
        WebDriverWait(d,12).until(lambda x:x.execute_script(
            "return currentView==='optimizer'"))
    button=d.find_element(By.ID,"start-btn")
    d.execute_script("arguments[0].scrollIntoView({block:'center',behavior:'instant'})",button)
    geometry=d.execute_script("""
        const b=document.getElementById('start-btn');
        const r=b.getBoundingClientRect();
        const x=r.left+r.width/2,y=r.top+r.height/2;
        const hit=document.elementFromPoint(x,y);
        return {top:r.top,bottom:r.bottom,left:r.left,right:r.right,
          viewport_height:innerHeight,viewport_width:innerWidth,
          hit_id:hit?.id||null,hit_class:hit?.className||null,
          hit_tag:hit?.tagName||null,scroll_y:scrollY,
          disabled:b.disabled};
    """)
    print("V569_CLICK_GEOMETRY "+json.dumps(geometry,ensure_ascii=True),flush=True)
    WebDriverWait(d,12).until(lambda x:x.execute_script("""
        const b=document.getElementById('start-btn');
        const r=b.getBoundingClientRect();
        const top=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);
        return !b.disabled && r.top>=0 && r.bottom<=innerHeight &&
          (top===b || b.contains(top));
    """))
    button.click()
    idle(d)
def visible_click(d,element):
    d.execute_script(
      "arguments[0].scrollIntoView({block:'center',behavior:'instant'})",element)
    WebDriverWait(d,12).until(lambda x:x.execute_script("""
       const e=arguments[0],r=e.getBoundingClientRect();
       const hit=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);
       return !e.disabled&&r.top>=0&&r.bottom<=innerHeight&&
         (hit===e||e.contains(hit));
    """,element))
    element.click()
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
            # The current product validates path/revision before any Build.
            # These synthetic values never reach a real Native endpoint.
            d.execute_script("""
              document.getElementById("binary").value=arguments[0];
              document.getElementById("revision").value="710c2408bf";
              buttonState(state.running,state.longrunResultReady);
            ""","C:/simc/simc.exe")
            cold=snap(d)
            print("V569_COLD_SCREEN "+json.dumps(cold,ensure_ascii=True),flush=True)
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
                visible_click(d,el)
            s=snap(d)
            print("V841_SELECTED_TRINKETS "+json.dumps(s,ensure_ascii=True),flush=True)
            need(s["trinkets"]==["910001","910002"],"V841_TWO_DISTINCT_CURRENT_TRINKETS")
            # Card interaction uses the actual product DOM and event handlers.
            special=d.find_element(By.CSS_SELECTOR,
                "#equipment-special-grid button[data-item-id='910003']")
            visible_click(d,special)
            # Only the selected-only visible control is a real user input.
            level=d.find_element(By.CSS_SELECTOR,
                "#equipment-selected-specials [data-item-id='910003'] input")
            level.send_keys("330")
            need(snap(d)["specialLevel"]=="330","V842_VISIBLE_LEVEL_MIRRORS_OWNER")
            d.execute_script("""
              const target=document.getElementById("ilevel");
              target.value="330";target.dispatchEvent(new Event("input",{bubbles:true}));
              const oil=document.getElementById("optimizer-oil-use-mode");
              oil.value="off";oil.dispatchEvent(new Event("change",{bubbles:true}));
            """)
            idle(d)
            print("V841_BEFORE_PENDING "+json.dumps(snap(d),ensure_ascii=True),flush=True)
            d.execute_script("window.__v569.mode='pending'")
            click(d);s=snap(d)
            print("V841_AFTER_PENDING "+json.dumps(s,ensure_ascii=True),flush=True)
            need(s["builds"]==4 and s["dps"]==0 and s["sha"] is None
                 and s["trinkets"]==["910001","910002"] and s["special"]==["910003"]
                 and s["specialLevel"]=="330" and s["specialHistoric"]=="true",
                 "V840_PENDING_PRESERVES_GEAR")
            d.execute_script("window.__v569.mode='ready'")
            click(d);s=snap(d)
            print("V841_AFTER_RETRY "+json.dumps(s,ensure_ascii=True),flush=True)
            need(s["builds"]==5 and s["dps"]==0 and s["level"]==330 and s["sha"]=="d"*64
                 and s["trinkets"]==["910001","910002"] and s["special"]==["910003"]
                 and s["specialLevel"]=="330" and not s["specialHistoric"],
                 "V840_RETRY_REBINDS_EXACT_GEAR")
            # Explicit clear is the user's decision, not a hidden rebind effect.
            clear=d.find_element(By.CSS_SELECTOR,
                "#equipment-selected-specials [data-item-id='910003'] button")
            visible_click(d,clear)
            need(snap(d)["special"]==[] and snap(d)["specialLevel"]=="" and
                 not d.find_element(By.ID,"equipment-selected-specials").is_displayed(),
                 "V840_EXPLICIT_CLEAR_REMOVES_ALL_FIELDS")
            s=snap(d)
            need(s["trinkets"]==["910001","910002"] and not s["disabled"]
                 and s["dps"]==0,"SECOND_CLICK_NOT_AVAILABLE")
            click(d);s=snap(d)
            print("V841_AFTER_DPS_REQUEST "+json.dumps(s,ensure_ascii=True),flush=True)
            need(s["dps"]==1 and s["builds"]==5 and s["gears"]==3,
                 "SAME_SHA_SECOND_CLICK_NOT_USED")
            receipt.update(status="PASS_REAL_CHROME_FIRST_CLICK_SYNTHETIC_HTTP",
              build_requests=5,gear_requests=3,dps_requests_synthetic=1,
              first_click_native_zero=True,wrong_sha_rejected=True,
              user_selected_two_trinkets=True,failed_build_retains_gear=True,
              retry_restores_gear=True,explicit_clear_removes_fields=True,
              visible_special_level_owner=True)
        except Exception as exc:
            receipt["status"]="FAIL"
            receipt["failure_type"]=type(exc).__name__
            if isinstance(exc,RuntimeError):
                receipt["failure_code"]=str(exc)
            if d:
                try:receipt["last_snapshot"]=snap(d)
                except Exception:pass
            raise
        finally:
            if d:d.quit()
            p.terminate()
            try:p.wait(timeout=5)
            except subprocess.TimeoutExpired:p.kill()
            (out/"V569_BROWSER_BRIDGE_RECEIPT.json").write_text(
              json.dumps(receipt,ensure_ascii=False,sort_keys=True,
                         indent=2)+"\n",encoding="utf8")
            print("V569_BROWSER "+json.dumps(receipt,ensure_ascii=True),flush=True)
if __name__=="__main__":main()
