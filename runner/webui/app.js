"use strict";
/* P1-WEB-2: browser presentation only. Python owns SimC, CHMV, budgets,
   cache safety and 95% statistical decisions. No external JS libraries. */
const $ = (id) => document.getElementById(id);
const statOrder = [
  ["crit_rating","치명","#be8b87"],
  ["haste_rating","가속","#74a4ad"],
  ["mastery_rating","특화","#a394bd"],
  ["versatility_rating","유연","#87a58c"]
];
const specLabels = {
  "paladin/retribution":"성기사 · 징벌",
  "warrior/fury":"전사 · 분노",
  "mage/frost":"마법사 · 냉기",
  "hunter/beast_mastery":"사냥꾼 · 야수",
  "rogue/subtlety":"도적 · 잠행",
  "shaman/elemental":"주술사 · 정기"
};
const statOptions = ["head","neck","shoulders","back","chest","wrists","hands",
                     "waist","legs","feet","finger1","finger2","main_hand","off_hand"];
const gearGroups = {
  "special-rows":{title:"특수효과 장비",fields:["slot","item_id","bonus_id","redirected_base_stats"]},
  "crafted-rows":{title:"장식 제작장비",fields:["slot","item_id","crafted_stats","embellishment","bonus_id"]}
};
const names = {
  slot:"부위",item_id:"아이템 ID",bonus_id:"bonus_id",
  redirected_base_stats:"촉매 원본 ID",crafted_stats:"제작 스탯",
  embellishment:"장식 토큰"
};
const state = { token:"", defaults:[], session:"", running:false,
                busy:false, options:null, pollTimer:null };
const number = (value,decimals=0) =>
  typeof value==="number" && Number.isFinite(value) ?
    value.toLocaleString("ko-KR",{minimumFractionDigits:decimals,
      maximumFractionDigits:decimals}) : "–";

function setNotice(message, error=false) {
  const node=$("notice");
  node.textContent=message;
  node.classList.toggle("error",Boolean(error));
}
function option(value,label) {
  const el=document.createElement("option");
  el.value=String(value); el.textContent=label ?? String(value);
  return el;
}
function populateSelect(id, values, labeler) {
  const el=$(id); el.replaceChildren();
  for (const value of values) el.appendChild(option(value,labeler(value)));
}
function field(id) {return $(id).value.trim();}
function valueInt(id) {
  const text=field(id);
  if (!/^[0-9]+$/.test(text)) throw Error(id.toUpperCase()+"_POSITIVE_INTEGER_REQUIRED");
  return Number(text);
}
function fillDefault(item) {
  $("race").value=item.race;
  $("talents").value=item.talents;
  $("trinket1").value=item.trinket_ids[0];
  $("trinket2").value=item.trinket_ids[1];
  $("ilevel").value=item.ilevel;
  $("final_T").value=item.final_T??"";
  $("targets").value=item.targets;
  $("duration").value=item.duration_seconds;
  $("raid_buffs").checked=item.raid_buffs;
  $("oil_main").checked=item.oil_hands.includes("main_hand");
  $("oil_off").checked=item.oil_hands.includes("off_hand");
  for (const id of ["food","potion","augmentation","diamond","omnium"]) $(id).selectedIndex=0;
  // Never carry other specialization's optional equipment into a new plan.
  for (const row of document.querySelectorAll(".gear-row")) {
    for (const input of row.querySelectorAll("input,select")) input.value="";
  }
}
function gearInputs(nodeId, config) {
  const parent=$(nodeId);
  const title=document.createElement("h3");title.textContent=config.title+" · 최대 2개";
  const group=document.createElement("div");group.className="gear-group";group.appendChild(title);
  for (let i=0;i<2;i++) {
    const row=document.createElement("div");row.className="gear-row";
    row.dataset.group=nodeId; row.dataset.index=String(i);
    const heading=document.createElement("p");heading.className="gear-row-title";
    heading.textContent=config.title+" "+(i+1);
    row.appendChild(heading);
    const grid=document.createElement("div");grid.className="gear-fields";
    for (const name of config.fields) {
      const label=document.createElement("label");
      label.textContent=names[name]||name;
      const input=name==="slot" ? document.createElement("select") :
                                   document.createElement("input");
      input.dataset.field=name;
      input.setAttribute("aria-label",config.title+" "+(i+1)+" "+names[name]);
      if (name==="slot") {
        input.appendChild(option("","미선택"));
        for(const slot of statOptions) input.appendChild(option(slot,slot));
      } else input.type="text";
      input.autocomplete="off";
      label.appendChild(input);
      grid.appendChild(label);
    }
    row.appendChild(grid);group.appendChild(row);
  }
  parent.appendChild(group);
}
function selectedGear(nodeId, group) {
  const result=[];
  for (const row of $(nodeId).querySelectorAll(".gear-row")) {
    const fields={};
    for (const input of row.querySelectorAll("[data-field]"))
      fields[input.dataset.field]=input.value.trim();
    if (!Object.values(fields).some(Boolean)) continue;
    if (!fields.slot|| !/^[0-9]+$/.test(fields.item_id))
      throw Error("특수장비/장식은 부위와 양의 정수 아이템 ID가 모두 필요합니다.");
    const options={};
    for(const [key,value] of Object.entries(fields)) {
      if(key!=="slot" && key!=="item_id" && value) options[key]=value;
    }
    result.push({slot:fields.slot,item_id:Number(fields.item_id),options});
  }
  if(result.length>2) throw Error(group+" 최대 2개");
  return result;
}
function buildRequest() {
  if(!$("optimizer-form").reportValidity()) throw Error("필수 입력과 수치 범위를 확인해 주세요.");
  const spec=field("spec");
  const source=state.defaults.find(d=>d.class+"/"+d.spec===spec);
  if(!source) throw Error("지원되는 6개 전문화에서 선택해 주세요.");
  const controls={
    class:source.class,spec:source.spec,
    race:field("race"),talents:field("talents"),
    ilevel:valueInt("ilevel"),final_T:field("final_T") ? valueInt("final_T"):null,
    trinket_ids:[valueInt("trinket1"),valueInt("trinket2")],
    oil_hands:["main_hand","off_hand"].filter(
      hand=>$(hand==="main_hand"?"oil_main":"oil_off").checked),
    targets:valueInt("targets"),duration_seconds:valueInt("duration"),
    raid_buffs:$("raid_buffs").checked,
    special_items:selectedGear("special-rows","special_items"),
    embellishments:selectedGear("crafted-rows","embellishments"),
    consumable_choices:{
      flask:"source_default", food:field("food"),potion:field("potion"),
      augmentation:field("augmentation"),
      diamond_id:Number(field("diamond")),omnium_talents:field("omnium")
    }
  };
  return {controls,binary:field("binary"),revision:field("revision"),
          static_cache:field("static_cache")||null};
}
async function api(path,{method="GET",payload=null,publicRoute=false}={}) {
  const headers={"Accept":"application/json"};
  if(!publicRoute) headers["x-simc-local-token"]=state.token;
  if(payload!==null) headers["Content-Type"]="application/json";
  const response=await fetch(path,{method,headers,cache:"no-store",
       credentials:"same-origin",body:payload===null?undefined:JSON.stringify(payload)});
  let data=null;
  try{data=await response.json();}catch{ /* Stable fail-closed network/UI error */ }
  if(!response.ok){
    // Never echo arbitrary user-controlled request body or raw backend traceback.
    const code=typeof data?.detail?.code==="string" ?
      data.detail.code : "HTTP_"+response.status;
    throw Error(code);
  }
  return data;
}
function markSession(id) {
  if (!/^[a-f0-9]{20}$/.test(id)) throw Error("세션 ID는 20자리 해시여야 합니다.");
  state.session=id;
  $("session-id").textContent=id;
  $("restore-id").value=id;
  // Only the opaque ID (not talents, paths or other personal details) persists.
  try{localStorage.setItem("simc_secondary_session_id",id);}catch{}
}
function buttonState(active=false,ready=false) {
  state.running=active;
  const busy=state.busy;
  $("plan-btn").disabled=busy||active||!state.token;
  $("start-btn").disabled=busy||active||!state.token;
  $("resume-btn").disabled=busy||active||!state.session;
  $("cache-btn").disabled=busy||active||!state.session||!ready;
  $("cancel-btn").disabled=busy||!active;
  $("restore-btn").disabled=busy;
}
async function withBusy(fn) {
  if(state.busy) return;
  state.busy=true;buttonState(state.running,false);
  try{await fn();}catch(err){setNotice("요청 차단 또는 오류: "+err.message,true);}
  finally{state.busy=false;buttonState(state.running,$("filled-result").hidden===false);}
}
function showPlan(plan) {
  if(!plan?.plan) return;
  const o=Object.values(plan.plan.fixed_O).reduce((a,n)=>a+n,0);
  setNotice("계산 준비 확인 · B "+number(plan.plan.base_B)+
    " + 고정 기름 O "+number(o)+" = 최종 T "+number(plan.plan.final_T)+
    " · 계획 Native 최대 "+plan.plan.native_limit+"회 (지금 실행 0회)");
}
function renderProgress(data) {
  const p=data?.progress||{};
  const n=Number(p.completed_jobs)||0,limit=Number(p.planned_jobs)||6;
  const pct=Number(p.progress_percent)||0;
  $("progress-label").textContent=n+" / "+limit+" 후보";
  $("progress-pct").textContent=number(pct,0)+"%";
  $("progress-bar").style.width=Math.max(0,Math.min(100,pct))+"%";
  const worker=p.worker?.status||p.status||"NOT_STARTED";
  const status=p.error||p.worker?.reason||worker;
  $("stage-text").textContent=status+" · Native 누적 "+(p.native_attempts||0)+
                       " · 캐시 "+(p.cache_hits||0);
  $("run-label").textContent=data.active?"진행 중":
    data.result_ready&&worker.startsWith("PASS")?"완료":
    data.cancel_requested?"취소 요청":"대기";
  buttonState(Boolean(data.active),Boolean(data.result_ready));
}
function renderResult(payload) {
  const r=payload.user_result;
  if(r.confidence_level!==0.95||r.global_optimum_proven!==false)
    throw Error("ONLY_95_RESULT_ALLOWED");
  const best=r.observed_first_choice;
  const total=r.final_T;
  $("dps").textContent=number(best.observed_dps_mean,1);
  $("sem").textContent=number(best.simc_sem,2);
  const oil=Object.values(r.fixed_O).reduce((a,x)=>a+x,0);
  $("budget").textContent="최종 CHMV T "+number(total)+
      "  ·  B="+number(r.base_B)+" + 고정 기름 O="+number(oil);
  const bars=$("stat-bars");bars.replaceChildren();
  for(const [key,label,color] of statOrder){
    const value=best.absolute_rating_T[key],pct=best.percent_of_final_T[key];
    const container=document.createElement("div");
    const head=document.createElement("div");head.className="stat-heading";
    const name=document.createElement("span");name.className="stat-label";
    const dot=document.createElement("span");dot.className="stat-dot";dot.style.backgroundColor=color;
    name.append(dot,document.createTextNode(label));
    const val=document.createElement("span");
    val.textContent=number(value)+" · "+number(pct,2)+"%";
    head.append(name,val);
    const line=document.createElement("div");line.className="stat-line";
    const fill=document.createElement("div");fill.className="stat-fill";
    fill.style.backgroundColor=color;fill.style.width=Math.max(0,Math.min(100,Number(pct)))+"%";
    line.appendChild(fill);container.append(head,line);bars.appendChild(container);
  }
  $("conf95").textContent=r.confirmation_pair_direction_supported_at_95?"방향 지지":"미확정";
  const alts=r.material_near_alternatives||[];
  $("alt-count").textContent=alts.length+"개 관측";
  const list=$("alt-list");list.replaceChildren();
  for(const [index,alt] of alts.entries()) {
    const row=document.createElement("div");row.className="alt-row";
    row.textContent="대안 "+(index+1)+" · DPS "+number(alt.observed_dps_mean,1)+" · "+
       statOrder.map(([key,label])=>label+" "+number(alt.absolute_rating_T[key])).join(" / ")+
       " · "+(alt.pairwise_95_label||"95% 비교 미확정");
    list.appendChild(row);
  }
  $("empty-result").hidden=true;$("filled-result").hidden=false;
}
async function pollOnce() {
  if(!state.session)return;
  const id=state.session;
  const p=await api("/api/v1/sessions/"+id+"/status");
  if(id!==state.session)return;
  renderProgress(p);
  if(p.result_ready && !p.active &&
     (p.progress?.worker?.status||p.progress?.status||"").startsWith("PASS")){
    const result=await api("/api/v1/sessions/"+id+"/result");
    if(id===state.session) renderResult(result);
  }
}
function beginPolling() {
  if(state.pollTimer!==null)clearInterval(state.pollTimer);
  state.pollTimer=setInterval(()=>{
    if(!state.busy&&state.session)pollOnce().catch(
      ()=>setNotice("상태 조회가 실패했습니다. 로컬 서버 연결을 확인해 주세요.",true));
  },1400);
}
async function restore(id) {
  markSession(id);
  $("filled-result").hidden=true;$("empty-result").hidden=false;
  await pollOnce();
  setNotice("기존 세션 연결 · "+id+" · 상태/결과 조회에는 새 Native 계산이 없습니다.");
}
function installOptions(options) {
  for(const name of ["food","potion","augmentation"]){
    populateSelect(name,options[name],v=>v==="source_default"?"원본 기본값":v);
  }
  populateSelect("diamond",options.diamond_id,
    v=>Number(v)===0?"원본 기본값":String(v));
  populateSelect("omnium",options.omnium_talents,(v,i)=>
    v==="source_default"?"원본 5룬 조합":v);
}
function registerHandlers() {
  $("spec").addEventListener("change",()=>{
    const selected=state.defaults.find(d=>d.class+"/"+d.spec===field("spec"));
    if(selected)fillDefault(selected);
  });
  $("plan-btn").addEventListener("click",()=>withBusy(async()=>{
    const p=await api("/api/v1/sessions/plan",{method:"POST",payload:buildRequest()});
    markSession(p.session_id);showPlan(p);await pollOnce();
  }));
  $("start-btn").addEventListener("click",()=>withBusy(async()=>{
    // This is the only new-job action. Never start SimC on page load or refresh.
    if(!window.confirm("이 PC에서 실제 SimC 최적화를 시작할까요? (세션 누적 Native 최대 6회)"))return;
    const p=await api("/api/v1/sessions/start",{method:"POST",payload:buildRequest()});
    markSession(p.session_id);$("filled-result").hidden=true;
    $("empty-result").hidden=false;
    setNotice("로컬 SimC 작업 시작. 계산은 이 PC에서 수행됩니다.");
    await pollOnce();
  }));
  $("resume-btn").addEventListener("click",()=>withBusy(async()=>{
    if(!window.confirm("동일 세션을 재개할까요? 캐시가 없으면 남은 Native 계산이 실행될 수 있습니다."))return;
    await api("/api/v1/sessions/"+state.session+"/resume",
              {method:"POST",payload:{}});
    setNotice("동일 세션 재개 요청됨.");await pollOnce();
  }));
  $("cache-btn").addEventListener("click",()=>withBusy(async()=>{
    await api("/api/v1/sessions/"+state.session+"/cache-only",
              {method:"POST",payload:{}});
    setNotice("기존 Native 6/6 캐시 검증 시작 · 추가 Native 호출 0회");
    await pollOnce();
  }));
  $("cancel-btn").addEventListener("click",()=>withBusy(async()=>{
    await api("/api/v1/sessions/"+state.session+"/cancel",
              {method:"POST",payload:{}});
    setNotice("취소 요청됨 · 현재 SimC 한 건의 완료 후 다음 후보부터 중단.");
    await pollOnce();
  }));
  $("restore-btn").addEventListener("click",()=>withBusy(
    ()=>restore(field("restore-id"))));
}
async function initialize() {
  for(const [id,config] of Object.entries(gearGroups))gearInputs(id,config);
  registerHandlers();
  try {
    const boot=await api("/api/v1/bootstrap",{publicRoute:true});
    state.token=boot.session_token;
    const [d,opt]=await Promise.all([api("/api/v1/defaults"),api("/api/v1/options")]);
    state.defaults=d.archetypes;
    $("spec").replaceChildren(...state.defaults.map(item=>
      option(item.class+"/"+item.spec,
             specLabels[item.class+"/"+item.spec]||item.class+" · "+item.spec)));
    $("spec").disabled=false;
    installOptions(opt);
    const paladin=state.defaults.find(v=>v.class==="paladin"&&v.spec==="retribution");
    if(paladin) {
      $("spec").value=paladin.class+"/"+paladin.spec;
      fillDefault(paladin);
    }else if(state.defaults.length)fillDefault(state.defaults[0]);
    buttonState();
    beginPolling();
    let previous=null;
    try{previous=localStorage.getItem("simc_secondary_session_id");}catch{}
    if(previous&&/^[a-f0-9]{20}$/.test(previous)){
      try{await restore(previous);}catch{
        // Do not erase user's old session: stale localStorage is nonauthoritative.
        setNotice("로컬 UI 연결됨. 이전 세션은 조회되지 않아 새 조건을 입력할 수 있습니다.");
      }
    }else setNotice("로컬 서버 연결됨 · 새 최적화는 실행 버튼을 눌러야만 시작됩니다.");
  }catch(e){
    setNotice("로컬 서버/사용자 입력 정보 연결 실패: "+e.message,true);
    buttonState();
  }
}
document.addEventListener("DOMContentLoaded",initialize);
