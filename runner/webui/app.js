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
  "rogue/outlaw":"도적 · 무법",
  "deathknight/frost":"죽음의 기사 · 냉기",
  "deathknight/unholy":"죽음의 기사 · 부정",
  "druid/feral":"드루이드 · 야성",
  "demonhunter/devourer":"악마사냥꾼 · 포식",
  "demonhunter/havoc":"악마사냥꾼 · 파멸",
  "hunter/marksmanship":"사냥꾼 · 사격",
  "hunter/survival":"사냥꾼 · 생존",
  "mage/arcane":"마법사 · 비전",
  "mage/fire":"마법사 · 화염",
  "monk/windwalker":"수도사 · 풍운",
  "priest/shadow":"사제 · 암흑",
  "rogue/assassination":"도적 · 암살",
  "shaman/enhancement":"주술사 · 고양",
  "warlock/affliction":"흑마법사 · 고통",
  "warlock/demonology":"흑마법사 · 악마",
  "warlock/destruction":"흑마법사 · 파괴",
  "warrior/arms":"전사 · 무기",
  "shaman/elemental":"주술사 · 정기",
  "druid/balance":"드루이드 · 조화",
  "evoker/devastation":"기원사 · 황폐"
};
// Verified Korean display strings: Blizzard Korea's playable-races page.
// A race name is display only; its exact SimC token goes into user controls.
const classNames={
  deathknight:"죽음의 기사",demonhunter:"악마사냥꾼",druid:"드루이드",
  evoker:"기원사",hunter:"사냥꾼",mage:"마법사",monk:"수도사",
  paladin:"성기사",priest:"사제",rogue:"도적",shaman:"주술사",
  warlock:"흑마법사",warrior:"전사"
};
const raceNames={
  human:"인간", dwarf:"드워프", night_elf:"나이트 엘프", gnome:"노움",
  draenei:"드레나이", worgen:"늑대인간", pandaren:"판다렌",
  orc:"오크", undead:"언데드", tauren:"타우렌", troll:"트롤",
  blood_elf:"블러드 엘프", goblin:"고블린", dracthyr:"드랙티르",
  void_elf:"공허 엘프", lightforged_draenei:"빛벼림 드레나이",
  dark_iron_dwarf:"검은무쇠 드워프", kul_tiran:"쿨 티란",
  mechagnome:"기계노움", earthen:"토석인", nightborne:"나이트본",
  highmountain_tauren:"높은산 타우렌", maghar_orc:"마그하르 오크",
  zandalari_troll:"잔달라 트롤", vulpera:"불페라"
};
const raceTokens=new Map(Object.entries(raceNames).map(([token,label])=>[label,token]));
const verifiedTerms={class:{},spec:{},race:{}};
function simcRace(value){return raceTokens.get(value.trim())||value.trim();}
function displayRace(token){return verifiedTerms.race[token]||raceNames[token]||token;}
function classLabel(token){return verifiedTerms.class[token]||classNames[token]||token;}
function specLabel(token) {
  return verifiedTerms.spec[token]||
    (specLabels[token]||token).split(" · ").slice(-1)[0];
}
function applyOfficialGameTerms(doc) {
  const legalKeys={
    class:new Set(state.defaults.map(x=>x.class)),
    spec:new Set(state.defaults.map(x=>x.class+"/"+x.spec)),
    race:new Set(Object.keys(raceNames))
  };
  if(doc?.schema!=="v336_verified_official_playable_terms_ko_KR_v1"||
    !["COMPLETE","PARTIAL_VERIFIED_NAMES"].includes(doc.status)||
    !doc.names||typeof doc.names!=="object")return false;
  const before=simcRace(field("race"));
  const selectedClass=field("class-choice");
  const selectedSpec=field("spec");
  for(const kind of ["class","spec","race"]) {
    const rows=doc.names[kind];
    if(!rows||typeof rows!=="object")continue;
    const safe={};
    for(const [key,label] of Object.entries(rows)) {
      if(!legalKeys[kind].has(key)||typeof label!=="string"||
         label.length>120||!/[가-힣]/.test(label))continue;
      safe[key]=label;
    }
    verifiedTerms[kind]=safe;
  }
  // Preserve old official/manual labels in reverse lookup for older sessions.
  raceTokens.clear();
  for(const [token,label] of Object.entries(raceNames))
    raceTokens.set(label,token);
  for(const [token,label] of Object.entries(verifiedTerms.race))
    if(!raceTokens.has(label)||raceTokens.get(label)===token)
      raceTokens.set(label,token);
  const classes=[...new Set(state.defaults.map(x=>x.class))]
    .sort((a,b)=>classLabel(a).localeCompare(classLabel(b),"ko-KR"));
  populateSelect("class-choice",classes,classLabel);
  $("class-choice").value=classes.includes(selectedClass)?selectedClass:classes[0];
  populateSpecializationsForClass(field("class-choice"),selectedSpec);
  drawClassSpecTiles();
  const item=state.defaults.find(x=>x.class+"/"+x.spec===field("spec"));
  if(item) {
    setRaceSuggestions(item);
    $("race").value=before?displayRace(before):displayRace(item.race);
    showCharacterDefaultHint();
  }
  return true;
}
async function refreshOfficialGameTerms(build) {
  if(!/^\d+(?:\.\d+){3}$/.test(build||""))return;
  const catalog=await api("/api/v1/environment/official-game-terms?game_build="+
    encodeURIComponent(build));
  const installed=applyOfficialGameTerms(catalog);
  $("season-terms-status").textContent=installed?
    "공식 한국어 게임 용어 확인 "+Object.values(catalog.names)
      .reduce((n,group)=>n+Object.keys(group).length,0)+
    "종 · 미확인 항목은 기존 표기 유지":
    "공식 한국어 게임 용어 원본 확인 보류 · 기존 표기 유지";
}
const statOptions = ["head","neck","shoulders","back","chest","wrists","hands",
                     "waist","legs","feet","finger1","finger2","main_hand","off_hand"];
const slotNames={head:"머리",neck:"목",shoulders:"어깨",back:"등",chest:"가슴",
  wrists:"손목",hands:"손",waist:"허리",legs:"다리",feet:"발",
  finger1:"반지 1",finger2:"반지 2",main_hand:"주무기",off_hand:"보조무기"};
const craftStats={crit:"32",haste:"36",mastery:"49",vers:"40"};
const statNames={crit:"치명",haste:"가속",mastery:"특화",vers:"유연"};
const classArmor={mage:1,warlock:1,priest:1,
  rogue:2,druid:2,monk:2,demonhunter:2,
  hunter:3,shaman:3,evoker:3,
  warrior:4,paladin:4,deathknight:4};
// Embellishment compatibility comes from the same server metadata used
// by Python validation. No client-side assumptions about jewelry/weapons.
const armorCraftSlots = new Set(["head","shoulders","back","chest",
 "wrists","hands","waist","legs","feet"]);
const gearGroups = {
  "special-rows":{title:"특수효과 장비",fields:["slot","item_id","bonus_id","redirected_base_stats"]},
  "crafted-rows":{title:"장식 제작장비",fields:["slot","embellishment","stat_a","stat_b","item_id","bonus_id"]}
};
const names = {
  slot:"부위",item_id:"아이템 ID",bonus_id:"bonus_id",
  redirected_base_stats:"촉매 원본 ID",crafted_stats:"제작 스탯",
  embellishment:"장식 토큰"
};
const state = { token:"", defaults:[], allowedRacesBySpec:{}, seasonGear:null, dkRuneIds:new Set(), oilLoadouts:[], oilCatalog:null, eagleApproved:false, session:"", running:false,
                longrunEnabled:false, longrunResultReady:false,
                longrunCompleted:false,
                busy:false, options:null, pollTimer:null, pollBusy:false,
                pollFailures:0, nextPollAt:0 };
const number = (value,decimals=0) =>
  typeof value==="number" && Number.isFinite(value) ?
    value.toLocaleString("ko-KR",{minimumFractionDigits:decimals,
      maximumFractionDigits:decimals}) : "–";


/* v353: task-first views. A tab switch never changes a SimC session. */
let currentView="optimizer";
function switchView(view) {
  if(!["optimizer","settings","results"].includes(view))return;
  if(view==="results"&&!state.session)return;
  currentView=view;
  for(const panel of document.querySelectorAll("[data-view-panel]"))
    panel.hidden=panel.dataset.viewPanel!==view;
  for(const button of document.querySelectorAll("[data-view]")) {
    const active=button.dataset.view===view;
    button.classList.toggle("is-active",active);
    if(active)button.setAttribute("aria-current","page");
    else button.removeAttribute("aria-current");
  }
  if(view==="results")$("results-nav-btn").hidden=false;
  window.scrollTo({top:0,behavior:"auto"});
}
function refreshResultNavigation() {
  $("results-nav-btn").hidden=!state.session;
}
function updateManualTMode() {
  const manual=$("manual-t-mode").checked;
  $("manual-t-field").hidden=!manual;
  $("final_T").disabled=!manual;
  if(!manual)$("final_T").value="";
  updateBudgetPreview();
}
function updateBudgetPreview() {
  const manual=$("manual-t-mode").checked;
  const t=Number(field("final_T"));
  $("budget-preview-total").textContent=manual?
    (Number.isSafeInteger(t)&&t>0?number(t)+" rating (수동 T)":"수동 T 입력 대기"):
    "시즌 구성 검증 후 표시";
  $("budget-preview-note").textContent=manual?
    "수동 입력 T가 자동 예산보다 우선합니다. 기름 O 포함, 고정치·분배 가능성은 실행 전 검증합니다.":
    "시즌 G/J/F/O와 선택 장비의 근거가 검증되면 T를 확정합니다. 미검증 값은 추정하지 않습니다.";
}



/* v359: image slots and names in always-visible source-bound item lists.
   Preserve the original selects as the only session/SimC ID owners. */
let activeTrinketSlot="trinket1";
function inlineEquipmentCard(item,{type,selected,disabled,reason="",onSelect}){
  const b=document.createElement("button");
  b.type="button";b.className="inline-item";
  b.dataset.itemId=String(item.item_id);
  b.disabled=disabled;
  b.setAttribute("aria-pressed",String(selected));
  const icon=document.createElement("span");
  icon.className="inline-item-icon";icon.setAttribute("aria-hidden","true");
  // No fetched icon can be inferred from a numeric ItemID.
  icon.textContent="◆";
  const text=document.createElement("span");text.className="inline-item-label";
  text.textContent=item.name_ko||item.name||"아이템 #"+item.item_id;
  const mark=document.createElement("span");mark.className="inline-item-mark";
  mark.textContent=selected?"✓":"";
  b.append(icon,text,mark);
  b.title=text.textContent+(reason?" · "+reason:"");
  b.addEventListener("click",onSelect);
  return b;
}
function drawInlineEquipment(){
  const trinketGrid=$("equipment-trinket-grid");
  const specialGrid=$("equipment-special-grid");
  if(!trinketGrid||!specialGrid)return;
  const blank=(parent,message)=>{
    parent.replaceChildren();
    const p=document.createElement("p");p.className="equipment-inline-empty";
    p.textContent=message;parent.appendChild(p);
  };
  const trinkets=eligibleEquipment("trinket");
  const tQuery=equipNorm($("equipment-trinket-search").value);
  const tFiltered=trinkets.filter(x=>!tQuery||
    equipNorm(x.name_ko||x.name).includes(tQuery)||String(x.item_id).includes(tQuery));
  trinketGrid.replaceChildren();
  if(!tFiltered.length)blank(trinketGrid,state.seasonGear?
    "검색 결과가 없습니다.":"시즌 장신구 목록을 불러오지 못했습니다.");
  for(const item of tFiltered.slice(0,80)){
    const id=String(item.item_id);
    const used1=field("trinket1")===id,used2=field("trinket2")===id;
    const selected=used1||used2;
    const b=inlineEquipmentCard(item,{type:"trinket",selected,
      disabled:false,
      reason:used1?"장신구 1 선택 · 다시 클릭하여 해제":
        used2?"장신구 2 선택 · 다시 클릭하여 해제":"",
      onSelect:()=>{
        // A second click on an already-selected item must clear the slot
        // that actually owns that item, regardless of the current focus.
        const owned=used1?"trinket1":used2?"trinket2":null;
        const target=owned||(!field("trinket1")?"trinket1":
          !field("trinket2")?"trinket2":activeTrinketSlot);
        const node=$(target);
        node.value=owned?"":id;
        activeTrinketSlot=owned||(!field("trinket1")?"trinket1":
          !field("trinket2")?"trinket2":target);
        node.dispatchEvent(new Event("change",{bubbles:true}));
      }});
    if(used1)b.dataset.slot="1";
    if(used2)b.dataset.slot="2";
    trinketGrid.appendChild(b);
  }
  $("equipment-trinket-status").textContent=state.seasonGear?
    "장신구 "+(field("trinket1")?1:0)+(field("trinket2")?1:0)+"/2 선택"+
    (tFiltered.length>80?" · 검색하여 나머지 확인":""):
    "시즌 선택지 미확인";

  const rows=[...$("special-rows").querySelectorAll(".gear-row")];
  const selectedRows=rows.map(row=>({
    row,select:row.querySelector('select[data-field="item_id"]'),
    slot:row.querySelector('select[data-field="slot"]')
  }));
  const selectedIds=new Set(selectedRows.filter(x=>x.select?.value).map(x=>x.select.value));
  const occupiedSlots=new Set(selectedRows.filter(x=>x.select?.value&&x.slot?.value).map(x=>x.slot.value));
  const specials=eligibleEquipment("special_effect_gear_candidate");
  const sQuery=equipNorm($("equipment-special-search").value);
  const sFiltered=specials.filter(x=>!sQuery||
    equipNorm(x.name_ko||x.name).includes(sQuery)||String(x.item_id).includes(sQuery));
  specialGrid.replaceChildren();
  if(!sFiltered.length)blank(specialGrid,state.seasonGear?
    "검색 결과가 없습니다.":"시즌 특수효과 장비 목록이 없습니다.");
  for(const item of sFiltered.slice(0,80)){
    const id=String(item.item_id),selected=selectedIds.has(id);
    const valid=specialAllowedSlots(item);
    const slotFree=valid.some(v=>!occupiedSlots.has(v));
    const noRoom=selectedIds.size>=rows.length;
    const disabled=!selected&&(!slotFree||noRoom);
    const b=inlineEquipmentCard(item,{type:"special",selected,disabled,
      reason:!selected&&(!slotFree?"장착할 수 있는 부위 없음":noRoom?"최대 8개 선택":"")||"",
      onSelect:()=>{
        if(selected){
          const entry=selectedRows.find(x=>x.select?.value===id);
          if(entry){
            entry.select.value="";
            entry.select.dispatchEvent(new Event("change",{bubbles:true}));
          }
        }else{
          const entry=selectedRows.find(x=>!x.select?.value);
          if(!entry)return;
          entry.row.hidden=false;
          entry.select.value=id;
          entry.select.dispatchEvent(new Event("change",{bubbles:true}));
        }
        refreshSpecialSlots();refreshEquipmentSelectionUI();
        buttonState(state.running,state.longrunResultReady);
      }});
    specialGrid.appendChild(b);
  }
  $("equipment-special-status").textContent=state.seasonGear?
    "특수효과 장비 "+selectedIds.size+"개 선택"+(sFiltered.length>80?
    " · 나머지는 검색":""):"선택 사항";
  // Native slot controls are maintained only for the original API,
  // not used as an extra, redundant user-facing selection bar.

}

/* v354 — image-free card chooser. Every actual selected ID stays in the
   original native SELECT; the browser only displays eligible source candidates. */
let equipmentDialogTarget=null;
let equipmentDialogOpener=null;
const equipNorm=x=>String(x??"").normalize("NFKC").toLocaleLowerCase("ko-KR").trim();
function eligibleEquipment(group){
  return [...(state.seasonGear?.choices?.[group]||[])]
    .filter(x=>Number.isSafeInteger(Number(x.item_id))&&Number(x.item_id)>0)
    .sort((a,b)=>String(a.name_ko||a.name||"").localeCompare(
      String(b.name_ko||b.name||""),"ko-KR")||a.item_id-b.item_id);
}
function refreshEquipmentSelectionUI(){
  for(const id of ["trinket1","trinket2"]){
    const select=$(id),btn=document.querySelector('[data-equip-select="'+id+'"]');
    const label=document.querySelector('[data-equip-label="'+id+'"]');
    if(!btn)continue;
    const chosen=select?.selectedOptions?.[0];
    btn.textContent=chosen?.value?chosen.textContent:"장신구 목록 열기 · 카드로 선택";
    if(label)label.textContent=chosen?.value?
      "ItemID "+select.value:"아직 선택한 장신구가 없습니다.";
    btn.disabled=!state.seasonGear;
  }
  for(const row of $("special-rows").querySelectorAll(".gear-row")){
    const select=row.querySelector('select[data-field="item_id"]');
    const btn=row.querySelector(".special-equipment-open");
    if(!btn)continue;
    const opt=select?.selectedOptions?.[0];
    btn.textContent=opt?.value?opt.textContent+" · 변경":"특수효과 장비 선택 (선택 사항)";
    btn.disabled=!state.seasonGear;
  }
  drawInlineEquipment();
}
function equipmentKind(select){
  return ["trinket1","trinket2"].includes(select?.id)?
    "trinket":"special_effect_gear_candidate";
}
function closeEquipmentDialog(){
  const dlg=$("equipment-dialog"),opener=equipmentDialogOpener;
  if(dlg.open&&typeof dlg.close==="function")dlg.close();
  else dlg.removeAttribute("open");
  equipmentDialogTarget=null;equipmentDialogOpener=null;
  if(opener?.isConnected)opener.focus();
}
function openEquipmentPicker(select,opener=null){
  if(!select)return;
  const type=equipmentKind(select);
  if(type==="trinket"){
    activeTrinketSlot=select.id;
    drawInlineEquipment();
    $("equipment-trinket-search").focus();
  }else{
    drawInlineEquipment();
    $("equipment-special-search").focus();
  }
}

function renderEquipmentGallery(query){
  const select=equipmentDialogTarget,grid=$("equipment-gallery");
  grid.replaceChildren();
  if(!select)return;
  const group=equipmentKind(select);
  const all=eligibleEquipment(group);
  const q=equipNorm(query);
  const items=all.filter(item=>!q||equipNorm(item.name_ko||item.name).includes(q)||
    String(item.item_id).includes(q));
  const visible=items.slice(0,48);
  $("equipment-dialog-status").textContent=!state.seasonGear?
    "현재 시즌 후보 목록이 없습니다. 환경 설정의 시즌 설치 상태를 확인하세요.":
    "시즌 후보 "+all.length+"종 · 검색 일치 "+items.length+"종"+
    (items.length>visible.length?" · 처음 48종만 표시, 검색어를 좁혀 주세요":"")+
    " · 아이템 실장착과 예산은 서버 검증";
  if(!visible.length){
    const empty=document.createElement("p");empty.className="equipment-gallery-empty";
    empty.textContent="선택 가능한 후보가 없습니다. 검색어 또는 시즌 환경을 확인하세요.";
    grid.appendChild(empty);return;
  }
  const other=group==="trinket"?
    field(select.id==="trinket1"?"trinket2":"trinket1"):"";
  const specialOther=new Set();
  if(group!=="trinket")
    for(const row of $("special-rows").querySelectorAll(".gear-row")){
      const item=row.querySelector('select[data-field="item_id"]');
      if(item&&item!==select&&item.value)specialOther.add(item.value);
    }
  for(const item of visible){
    const id=String(item.item_id);
    const dup=group==="trinket"?id===other:specialOther.has(id);
    const compatible=group==="trinket"||specialAllowedSlots(item).length>0;
    const card=document.createElement("button");
    card.type="button";card.className="equipment-card";
    card.disabled=dup||!compatible;
    card.setAttribute("aria-pressed",String(id===select.value));
    const placeholder=document.createElement("span");
    placeholder.className="equipment-placeholder";
    placeholder.textContent="◆";placeholder.setAttribute("aria-hidden","true");
    const label=document.createElement("span");label.className="equipment-card-name";
    label.textContent=item.name_ko||item.name||"아이템 #"+id;
    const meta=document.createElement("span");meta.className="equipment-card-meta";
    meta.textContent="ItemID "+id+(dup?" · 다른 칸에 선택됨":
      !compatible?" · 무기/부위 비호환":"");
    card.title=label.textContent+" · "+meta.textContent;
    card.append(placeholder,label,meta);
    card.addEventListener("click",()=>{
      select.value=id;
      select.dispatchEvent(new Event("change",{bubbles:true}));
      refreshEquipmentSelectionUI();
      updateBudgetPreview();
      closeEquipmentDialog();
    });
    grid.appendChild(card);
  }
}
function drawClassSpecTiles(){
  // A compact native-select presentation is active. Avoid rebuilding 13+
  // decorative tile buttons on every class/spec update when hidden.
  if($("class-choice-tiles")?.hidden && $("spec-choice-tiles")?.hidden)return;
  if(!state.defaults.length)return;
  const cls=$("class-choice"),spec=$("spec");
  const classes=$("class-choice-tiles");classes.replaceChildren();
  for(const opt of Array.from(cls.options).filter(x=>x.value)){
    const btn=document.createElement("button");btn.type="button";
    btn.className="class-choice-tile";btn.textContent=opt.textContent;
    btn.setAttribute("aria-pressed",String(opt.value===cls.value));
    btn.addEventListener("click",()=>{
      if(cls.value!==opt.value){
        cls.value=opt.value;
        cls.dispatchEvent(new Event("change",{bubbles:true}));
      }
      drawClassSpecTiles();
    });
    classes.appendChild(btn);
  }
  const specs=$("spec-choice-tiles");specs.replaceChildren();
  for(const opt of Array.from(spec.options).filter(x=>x.value)){
    const btn=document.createElement("button");btn.type="button";
    btn.className="spec-choice-tile";btn.textContent=opt.textContent;
    btn.setAttribute("aria-pressed",String(opt.value===spec.value));
    btn.addEventListener("click",()=>{
      if(spec.value!==opt.value){
        spec.value=opt.value;
        spec.dispatchEvent(new Event("change",{bubbles:true}));
      }
      drawClassSpecTiles();
    });
    specs.appendChild(btn);
  }
}
function hasRequiredSelections(){
  return Boolean(state.token&&field("spec")&&field("race")&&
    field("trinket1")&&field("trinket2")&&
    field("trinket1")!==field("trinket2")&&
    Number.isInteger(Number(field("ilevel")))&&Number(field("ilevel"))>0);
}

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
// Exact original SELECT remains the only SimC/season ID owner.
// An accessible searchable listbox is presentation-only.
const searchChoices=new Map();
function syncSearchChoices(){for(const x of searchChoices.values())x.sync();}
function enhanceSelect(select){
  if(!select||searchChoices.has(select))return;
  const box=document.createElement("div");box.className="choice-picker";
  const input=document.createElement("input");input.type="search";
  input.id="choice-"+(select.id||"row-"+searchChoices.size);
  input.autocomplete="off";input.placeholder="이름으로 검색";
  const label=select.getAttribute("aria-label")||
    select.labels?.[0]?.textContent?.trim()||"항목";
  input.setAttribute("aria-label",label+" 검색");
  input.setAttribute("role","combobox");
  input.setAttribute("aria-autocomplete","list");
  input.setAttribute("aria-expanded","false");
  const menu=document.createElement("div");menu.id=input.id+"-results";
  menu.className="choice-results";menu.setAttribute("role","listbox");
  menu.hidden=true;input.setAttribute("aria-controls",menu.id);
  box.append(input,menu);
  const gearLabel=select.closest(".gear-row")?select.closest("label"):null;
  if(gearLabel){
    // A gear control must occupy ONE grid cell with its own label.
    // Moving the label retains the native SELECT, data-field and listeners.
    const fieldWrap=document.createElement("div");
    fieldWrap.className="gear-choice-field";
    gearLabel.before(fieldWrap);fieldWrap.append(gearLabel,box);
  }else select.after(box);
  select.classList.add("choice-native-select");
  select.setAttribute("aria-hidden","true");select.tabIndex=-1;
  let shown=false,index=0;
  const norm=s=>String(s).normalize("NFKC").toLocaleLowerCase("ko-KR").trim();
  const sync=()=>{
    if(!shown){const selected=select.selectedOptions?.[0];
      input.value=selected?.value?selected.textContent:"";}
    input.disabled=select.disabled;
    if(!select.validity||select.validity.valid)input.removeAttribute("aria-invalid");
  };
  function close(){
    shown=false;menu.hidden=true;
    input.setAttribute("aria-expanded","false");sync();
  }
  function choose(opt){
    select.value=opt.value;select.dispatchEvent(new Event("change",{bubbles:true}));
    close();input.focus();
  }
  function draw(query){
    menu.replaceChildren();
    const q=norm(query);
    const matches=Array.from(select.options).filter(opt=>
      !opt.disabled&&(!q||norm(opt.textContent).includes(q)||norm(opt.value).includes(q)));
    const visible=matches.slice(0,50);
    index=Math.min(index,Math.max(0,visible.length-1));
    for(const [i,opt] of visible.entries()){
      const b=document.createElement("button");b.type="button";
      b.className="choice-result";b.textContent=opt.textContent;
      b.setAttribute("role","option");
      b.setAttribute("aria-selected",String(opt.value===select.value));
      if(i===index)b.classList.add("choice-active");
      b.addEventListener("mousedown",e=>e.preventDefault());
      b.addEventListener("click",()=>choose(opt));menu.appendChild(b);
    }
    if(!matches.length||matches.length>visible.length){
      const p=document.createElement("p");p.className="choice-empty";
      p.textContent=!matches.length?"검색 결과가 없습니다.":
        matches.length+"개 중 50개 표시 · 더 구체적으로 검색해 주세요.";
      menu.appendChild(p);
    }
  }
  const open=(query="")=>{
    if(select.disabled)return;
    shown=true;menu.hidden=false;index=0;
    input.setAttribute("aria-expanded","true");draw(query);
  };
  input.addEventListener("focus",()=>{input.select();open();});
  input.addEventListener("input",()=>open(input.value));
  input.addEventListener("keydown",e=>{
    if(e.key==="Escape"){e.preventDefault();close();input.blur();}
    if(e.key==="ArrowDown"||e.key==="ArrowUp"){
      e.preventDefault();if(!shown)open();
      const rows=Array.from(menu.querySelectorAll(".choice-result"));
      if(rows.length){
        index=(index+(e.key==="ArrowDown"?1:-1)+rows.length)%rows.length;
        rows.forEach((r,i)=>r.classList.toggle("choice-active",i===index));
        rows[index].scrollIntoView({block:"nearest"});
      }
    }
    if(e.key==="Enter"&&shown){
      const rows=menu.querySelectorAll(".choice-result");
      if(rows.length){e.preventDefault();rows[index].click();}
    }
  });
  input.addEventListener("blur",()=>setTimeout(()=>{
    if(!box.contains(document.activeElement))close();
  },0));
  document.addEventListener("click",e=>{if(shown&&!box.contains(e.target))close();});
  select.addEventListener("change",close);
  select.addEventListener("invalid",()=>{
    input.setAttribute("aria-invalid","true");input.focus();
  });
  new MutationObserver(()=>{if(shown)draw(input.value);else sync();}).observe(
    select,{subtree:true,childList:true,attributes:true,attributeFilter:["disabled"]});
  searchChoices.set(select,{sync});sync();
}
function initializeSearchChoices(){
  for(const id of ["class-choice","spec","trinket1","trinket2","food","potion",
    "augmentation","diamond","omnium","optimizer-oil-loadout",
    "dk_rune_main","dk_rune_off","season_enchant_finger1"])
    enhanceSelect($(id));
  for(const row of document.querySelectorAll(".gear-row")){
    const fields=row.dataset.group==="special-rows"?["item_id"]:["embellishment","slot"];
    for(const key of fields)enhanceSelect(
      row.querySelector('select[data-field="'+key+'"]'));
  }
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
// Import ONLY a single character's identity/talents. Never read worn gear,
// gear_* totals, socket/rating values, APL, trinkets or consumable settings.
// Parsing happens entirely in this browser; no upload, persistence or Native.
function parseSimcCharacter(source) {
  if(typeof source!=="string"||!source.trim()||source.length>250000)
    throw Error("SimC 프로필 텍스트는 1~250,000자여야 합니다.");
  const classes=new Set(state.defaults.map(x=>x.class));
  const actors=[];
  const info={};
  for(const raw of source.split(/\r?\n/)) {
    const line=raw.trim();
    if(!line||line.startsWith("#"))continue;
    const matched=/^([a-z_]+)\s*=\s*(.*)$/i.exec(line);
    if(!matched)continue;
    const name=matched[1].toLowerCase(),value=matched[2].trim();
    if(classes.has(name))actors.push(name);
    if(["spec","race","talents"].includes(name)) {
      if(Object.hasOwn(info,name))throw Error("SimC 프로필에 중복된 "+name+" 항목이 있습니다.");
      info[name]=value;
    }
    if(name==="copy")throw Error("여러 캐릭터/복제 프로필은 가져올 수 없습니다.");
  }
  if(actors.length!==1||!info.spec)
    throw Error("한 캐릭터의 직업·전문화가 필요합니다.");
  const race=(info.race||"").toLowerCase(),spec=info.spec.toLowerCase();
  if((race&&!/^[a-z_]{2,40}$/.test(race))||
     !/^[a-z_]{2,60}$/.test(spec)||
     (info.talents&&!/^[A-Za-z0-9+/_=-]{10,2048}$/.test(info.talents)))
    throw Error("SimC 종족·전문화·특성 코드 형식이 올바르지 않습니다.");
  const key=actors[0]+"/"+spec;
  const matched=state.defaults.find(x=>x.class+"/"+x.spec===key);
  if(!matched)throw Error("아직 지원하지 않는 전문화: "+key);
  return {key,race,talents:info.talents||"",defaults:matched};
}
async function importSimcCharacter() {
  const file=$("simc-import-file").files?.[0];
  if(file&&file.size>250000)throw Error("SimC 프로필 파일은 250KB 이하여야 합니다.");
  const source=file?await file.text():$("simc-import-text").value;
  const parsed=parseSimcCharacter(source);
  if(field("spec")!==parsed.key) {
    $("class-choice").value=parsed.defaults.class;
    populateSpecializationsForClass(parsed.defaults.class,parsed.key);
    // Same reset behavior as a manual specialization change.
    fillDefault(parsed.defaults);
  }
  if(parsed.race)$("race").value=displayRace(parsed.race);
  $("talents").value=parsed.talents;
  drawClassSpecTiles();
  showCharacterDefaultHint();
  setNotice("SimC 캐릭터 정보만 적용됨 · 미입력 종족/특성은 기본값 사용 · 장비/스탯은 가져오지 않음 · Native 0회");
}
// The only user-selectable non-crafted equipment is seasonal trinkets and
// optional special-effect gear. General plain equipment stays internal.
function seasonChoice(group,id) {
  return !!state.seasonGear?.choices?.[group]?.some(x=>x.item_id===Number(id));
}
function setTrinketSelection(fieldId,itemId,restored=false) {
  const node=$(fieldId),value=String(itemId??"");
  // Remove historical-only choices when switching specializations.
  for(const opt of Array.from(node.options))
    if(opt.dataset.historic==="true")opt.remove();
  if(seasonChoice("trinket",value)) {
    node.value=value;
    refreshEquipmentSelectionUI();
    return;
  }
  // Show an earlier session's exact identity without silently substituting
  // another trinket. A NEW plan will require an eligible current-season pair.
  if(restored&&/^[0-9]+$/.test(value)) {
    const old=option(value,"이전 세션 장신구 #"+value+" · 새 계획은 재선택");
    old.dataset.historic="true";
    node.appendChild(old);
    node.value=value;
    refreshEquipmentSelectionUI();
    return;
  }
  node.value="";
  refreshEquipmentSelectionUI();
}
function installSeasonGearHints(catalog) {
  state.seasonGear=catalog?.status==="CURRENT_SEASON_CANDIDATE_SELECTION_ONLY"
    ? catalog : null;
  const node=$("season-gear-note");
  const current=state.seasonGear?.choices||{};
  const sortedKorean=items=>[...(items||[])].sort((a,b)=>
    (a.name_ko||a.name).localeCompare(b.name_ko||b.name,"ko-KR")||
    a.item_id-b.item_id);
  for(const fieldId of ["trinket1","trinket2"]) {
    const node=$(fieldId);
    node.replaceChildren(option("","이번 시즌 장신구 선택"));
    for(const item of sortedKorean(current.trinket))
      node.appendChild(option(item.item_id,(item.name_ko||item.name)));
  }
  for(const row of $("special-rows").querySelectorAll(".gear-row")) {
    const element=row.querySelector('[data-field="item_id"]');
    element.replaceChildren(option("","이번 시즌 특수효과 장비 선택"));
    for(const item of sortedKorean(current.special_effect_gear_candidate))
      element.appendChild(option(item.item_id,(item.name_ko||item.name)));
  }
  refreshSpecialSlots();
  refreshEquipmentSelectionUI();
  if(!state.seasonGear) {
    node.textContent="시즌 선택 목록이 없습니다. 새 장신구·특수효과 선택은 보류됩니다. 기존 세션 조회는 가능합니다.";
    return;
  }
  node.textContent="시즌 장신구와 특수효과 장비를 아래에서 선택하세요.";
}
// Item.InventoryType determines special equipment slot. Ring and dual
// weapons have equivalent hands, so select the next free valid slot.
function specialAllowedSlots(item) {
  if(!item)return [];
  const form=state.seasonGear?.weapon_forms?.[field("spec")];
  const fixed={1:"head",2:"neck",3:"shoulders",5:"chest",20:"chest",
    6:"waist",7:"legs",8:"feet",9:"wrists",10:"hands",16:"back"};
  if(Object.hasOwn(fixed,item.inventory_type))return [fixed[item.inventory_type]];
  if(item.inventory_type===11)return ["finger1","finger2"];
  if(item.inventory_type===13) {
    if(["dual_one_hand"].includes(form))return ["main_hand","off_hand"];
    if(["one_hand_frill","one_hand_shield","single_one_hand"].includes(form))
      return ["main_hand"];
    return [];
  }
  if(item.inventory_type===17)return form==="dual_two_hand"?
    ["main_hand","off_hand"]:form==="single_two_hand"?["main_hand"]:[];
  if([15,26].includes(item.inventory_type))return form==="ranged"?["main_hand"]:[];
  if(item.inventory_type===14)return form==="one_hand_shield"?["off_hand"]:[];
  if(item.inventory_type===23)return form==="one_hand_frill"?["off_hand"]:[];
  return [];
}
function refreshSpecialSlots() {
  const used=new Set(),ids=new Set();
  for(const row of $("special-rows").querySelectorAll(".gear-row")) {
    const id=row.querySelector('[data-field="item_id"]');
    const slot=row.querySelector('[data-field="slot"]');
    const note=row.querySelector(".auto-slot-note");
    slot.value="";
    if(!id?.value){note.textContent="장비를 선택하면 부위가 자동 지정됩니다.";continue;}
    const item=state.seasonGear?.choices?.special_effect_gear_candidate
      ?.find(x=>x.item_id===Number(id.value));
    if(!item) {note.textContent="이전 세션 장비 또는 시즌 목록에 없는 ID · 재선택 필요";continue;}
    const valid=specialAllowedSlots(item);
    const chosen=valid.find(x=>!used.has(x));
    if(!chosen||ids.has(item.item_id)) {
      note.textContent="이 전문화에서 장착할 수 없거나 중복된 장비입니다.";
      continue;
    }
    slot.value=chosen;used.add(chosen);ids.add(item.item_id);
    note.textContent="자동 부위: "+slotNames[chosen]+
      (valid.length>1?" (동일 유형의 다른 장비는 남는 칸으로 배정)":"");
  }
}
function syncCraftRow(row,restored=false) {
  const kind=row.querySelector('[data-field="embellishment"]');
  const slot=row.querySelector('[data-field="slot"]');
  const previous=slot.value;
  const meta=state.options?.embellishments?.[kind.value];
  const slots=(meta?.slots||[]).filter(x=>armorCraftSlots.has(x)&&!!chosenCraft(x));
  slot.replaceChildren(option("","적용 부위 선택"));
  for(const x of statOptions)if(slots.includes(x))
    slot.appendChild(option(x,slotNames[x]));
  if(previous&&slots.includes(previous))slot.value=previous;
  else if(restored&&previous) {
    const optionOld=option(previous,slotNames[previous]||previous);
    optionOld.dataset.historic="true";slot.appendChild(optionOld);slot.value=previous;
  }
  const note=row.querySelector(".craft-slot-note");
  note.textContent=!kind.value?"장식 종류를 먼저 선택하면 호환 부위가 표시됩니다.":
    !meta?"검증되지 않은 이전 장식 · 새 계획은 재선택 필요":
    slots.length?"지원 유형: 방어구 전용 · 목걸이/반지/무기에는 적용 불가":
    "이 직업에서 선택 가능한 제작 방어구가 없습니다.";
}

function showRepresentativeScope() {
  const item=state.defaults.find(d=>d.class+"/"+d.spec===field("spec"));
  const note=$("gear-scope-note");
  note.hidden=!item;
  if(!item)return;
  note.textContent=Number(field("ilevel"))===334?
    "일반 장비·무기·티어 4세트는 자동 구성합니다.":
    "선택한 목표 레벨의 대표 장비를 자동 구성합니다. 실제 결과는 SimC에서 확인합니다.";
}

function showCharacterDefaultHint() {
  const item=state.defaults.find(d=>d.class+"/"+d.spec===field("spec"));
  const allowed=Array.isArray(state.allowedRacesBySpec[item?.class+"/"+item?.spec]);
  $("race-default-note").textContent=!item?"전문화 선택 후 종족을 지정할 수 있습니다.":
    "대표 종족 "+displayRace(item.race)+" 선택됨 · "+
    (allowed?"해당 전문화의 확인된 종족만 목록에 표시합니다.":
     "다른 종족은 실행 시 실제 SimC 적용 여부를 확인합니다.");
  $("talents-default-note").textContent=
    "특성 미입력 시 선택한 전문화의 검증된 기본 대표 특성을 사용합니다.";
}
function setRaceSuggestions(item) {
  const roster=$("race-list");
  const approved=state.allowedRacesBySpec[item?.class+"/"+item?.spec];
  const allowed=Array.isArray(approved)?new Set(approved):null;
  const entries=Object.keys(raceNames).filter(token=>!allowed||allowed.has(token))
    .map(token=>[token,displayRace(token)])
    .sort((a,b)=>a[1].localeCompare(b[1],"ko-KR"));
  roster.replaceChildren(...entries.map(([token,name])=>{
    const opt=document.createElement("option");
    opt.value=name;opt.label=token;return opt;
  }));
}
function populateSpecializationsForClass(cls,selectedKey=""){
  const available=state.defaults.filter(x=>x.class===cls);
  const selected=available.some(x=>x.class+"/"+x.spec===selectedKey)
    ?selectedKey:(available[0]?cls+"/"+available[0].spec:"");
  $("spec").replaceChildren(...available.map(item=>{
    const key=item.class+"/"+item.spec;
    return option(key,specLabel(key));
  }));
  $("spec").value=selected;
  $("spec").disabled=!available.length;
  syncSearchChoices();
  drawClassSpecTiles();
}
function installClassSpecChoices() {
  const classes=[...new Set(state.defaults.map(x=>x.class))]
    .sort((a,b)=>classLabel(a).localeCompare(classLabel(b),"ko-KR"));
  populateSelect("class-choice",classes,classLabel);
  $("class-choice").disabled=false;
  const first=classes.includes("paladin")?"paladin":classes[0];
  $("class-choice").value=first;
  populateSpecializationsForClass(first);
}
function fillDefault(item) {
  // Explicitly display the SOURCE-approved race instead of letting the
  // server silently choose dwarf (invalid for druid/DH/evoker).
  setRaceSuggestions(item);
  $("race").value=displayRace(item.race);
  $("talents").value="";
  showCharacterDefaultHint();
  setTrinketSelection("trinket1",item.trinket_ids[0]);
  setTrinketSelection("trinket2",item.trinket_ids[1]);
  $("ilevel").value=item.ilevel;
  $("final_T").value=item.final_T??"";
  $("manual-t-mode").checked=Boolean($("final_T").value);
  updateManualTMode();
  $("max-single-stat-percent").value=item.max_single_stat_percent??60;
  $("targets").value=item.targets;
  $("duration").value=item.duration_seconds;
  $("raid_buffs").checked=item.raid_buffs;
  // Fresh user intent defaults to oil ON. Never assume or invent O:
  // an installed, exact full-hand manifest must satisfy this preference.
  oilUseIntent=true;
  $("oil_main").checked=false;
  $("oil_off").checked=false;
  $("optimizer-oil-main-id").value="";
  $("optimizer-oil-off-id").value="";
  $("optimizer-oil-loadout").value="";
  oilCompatibility();
  renderInstalledOilLoadouts(state.oilCatalog);
  $("dk_rune_main").value="";
  $("dk_rune_off").value="";
  runeCompatibility();
  for (const id of ["food","potion","augmentation","diamond","omnium"]) $(id).selectedIndex=0;
  refreshDefaultConsumableSummaries();
  $("season_enchant_finger1").value="";
  // Reset optional slots on specialization changes, including hidden extra rows.
  fillGearRows("special-rows",[]);
  fillGearRows("crafted-rows",[]);
  for(const row of $("crafted-rows").querySelectorAll(".gear-row"))syncCraftRow(row);
  showRepresentativeScope();
  syncSearchChoices();
  drawClassSpecTiles();
  refreshEquipmentSelectionUI();
}

/* v363: default-on is USER INTENT, not an assertion of validated O.
   Only source-verified, full-hand physical IDs can fulfill that intent. */
let oilUseIntent=true;
function oilNeedsOffhand() {
  const form=state.seasonGear?.weapon_forms?.[field("spec")];
  return form==="dual_one_hand"||form==="dual_two_hand";
}
function fullVerifiedOilMatch(item) {
  const form=state.seasonGear?.weapon_forms?.[field("spec")];
  if(!form)return false;
  const needOff=oilNeedsOffhand();
  const ids=item?.selected_oil_item_ids_by_hand||{};
  return Number.isSafeInteger(ids.main_hand)&&ids.main_hand>0&&
    Boolean(ids.off_hand)===needOff&&
    Object.keys(ids).length===(needOff?2:1);
}
function selectedFullVerifiedOil() {
  if(!$("oil_main").checked ||
      $("oil_off").checked!==oilNeedsOffhand())return null;
  const main=Number(field("optimizer-oil-main-id"));
  const off=Number(field("optimizer-oil-off-id"));
  if(!Number.isSafeInteger(main)||main<=0 ||
     (oilNeedsOffhand()&&(!Number.isSafeInteger(off)||off<=0)))return null;
  return state.oilLoadouts.find(item=>
    fullVerifiedOilMatch(item)&&
    item.selected_oil_item_ids_by_hand.main_hand===main &&
    (!oilNeedsOffhand()||
      item.selected_oil_item_ids_by_hand.off_hand===off))||null;
}
function syncOilUseToggle(){
  const box=$("optimizer-oil-enabled");
  if(!box)return;
  box.checked=oilUseIntent;
  const verified=oilUseIntent?selectedFullVerifiedOil():null;
  $("optimizer-oil-toggle-status").textContent=!oilUseIntent?"미사용":
    verified?(oilNeedsOffhand()?"양쪽 무기 적용":"주무기 적용"):
      "기름 검증·선택 필요";
}
function tryApplyDefaultOil(){
  if(!oilUseIntent){syncOilUseToggle();return;}
  // A restored or deliberately configured selection must not be overwritten
  // by another season installation, even if the latest catalog differs.
  if($("oil_main").checked||$("oil_off").checked){
    syncOilUseToggle();return;
  }
  const matches=state.oilLoadouts.filter(fullVerifiedOilMatch);
  if(matches.length!==1){syncOilUseToggle();return;}
  $("optimizer-oil-loadout").value=matches[0].installed_manifest_sha256;
  chooseInstalledOilLoadout();
  updateBudgetPreview();
}
function applyOilUseToggle(){
  oilUseIntent=$("optimizer-oil-enabled").checked;
  if(!oilUseIntent){
    $("optimizer-oil-loadout").value="";
    $("oil_main").checked=false;$("oil_off").checked=false;
    $("optimizer-oil-main-id").value="";
    $("optimizer-oil-off-id").value="";
    oilCompatibility();syncOilUseToggle();updateBudgetPreview();return;
  }
  tryApplyDefaultOil();
  const matches=state.oilLoadouts.filter(fullVerifiedOilMatch);
  if(matches.length!==1&&!selectedFullVerifiedOil()){
    if(matches.length>1){
      const advanced=document.querySelector("#optimizer-form .env-advanced-controls");
      if(advanced)advanced.open=true;
      $("env-oil-options").open=true;
    }
    setNotice(matches.length?
      "기름 사용 기본값은 켜져 있습니다. 검증된 조합이 여러 개라 직접 고르세요.":
      "기름 사용 기본값은 켜져 있지만 검증된 조합이 없습니다. 시즌 환경 검증 또는 기름 미사용을 선택하세요.");
  }
  syncOilUseToggle();updateBudgetPreview();
}

function oilCompatibility() {
  const key=field("spec");
  const form=state.seasonGear?.weapon_forms?.[key];
  const supportsOff=form==="dual_one_hand"||form==="dual_two_hand";
  $("oil_off").disabled=!supportsOff;
  if(!supportsOff)$("oil_off").checked=false;
  $("oil_off").title=supportsOff?"두 무기에 기름 적용 가능":"이 전문화의 보조무기에는 기름을 사용할 수 없습니다.";
  syncOilUseToggle();
}


function refreshDefaultConsumableSummaries(){
  const fid=field("season-selected-flask-id");
  const fOption=[...$("season-verified-flask").options].find(o=>o.value===fid);
  $("env-flask-summary").textContent=fid?
    (fOption?.textContent||"영약 #"+fid+" · 검증 필요"):"시즌 기본값";
  const potion=$("potion"),chosen=field("potion");
  $("env-potion-summary").textContent=!chosen||chosen==="source_default"?
    "미사용 (이번 시즌 기본)":potion.selectedOptions?.[0]?.textContent||chosen;
}

function renderInstalledFlaskChoices(data) {
  const selector=$("season-verified-flask");
  const prior=field("season-selected-flask-id");
  selector.replaceChildren(option("","검증 설치 영약 선택 (선택 · 없으면 고급 ItemID 유지)"));
  if(data?.schema==="v113_verified_installed_oil_loadouts_v1" &&
     Number(data.target_ilevel)===Number(field("ilevel"))) {
    for(const item of data.verified_flasks||[]) {
      if(!Number.isSafeInteger(item.physical_item_id)||
         item.physical_item_id<=0 ||
         !Number.isInteger(item.crafting_quality)||
         item.crafting_quality<0 ||
         !Number.isInteger(item.F_rating)||item.F_rating<0 ||
         !/^[a-z0-9_]{1,90}$/.test(item.simc_input_token||""))continue;
      const official=(typeof item.official_name_ko==="string" &&
        item.official_name_ko.trim())?item.official_name_ko:null;
      selector.appendChild(option(item.physical_item_id,
        (official||item.simc_input_token.replace(/_/g," "))+
        " · 검증 품질 "+item.crafting_quality+" · F "+item.F_rating));
    }
  }
  selector.value=Array.from(selector.options).some(x=>x.value===prior)?prior:"";
  const count=selector.options.length-1;
  refreshDefaultConsumableSummaries();
  $("season-verified-flask-status").textContent=count?
    "이 PC에 검증 설치된 영약 "+count+"종 · 같은 빌드/ilvl에서만 표시 · "+
    "새 환경 요청 시 기존 원본 엔진이 다시 확인":
    "이 빌드/ilvl에서 검증 설치 영약이 없습니다. 원본 수집·검증 후 표시되며 "+
    "미검증 아이템은 자동 등록하지 않습니다.";
}
function chooseInstalledFlask() {
  $("season-selected-flask-id").value=field("season-verified-flask");
  refreshDefaultConsumableSummaries();
}
function renderInstalledOilLoadouts(data) {
  state.oilCatalog=data;
  const selector=$("optimizer-oil-loadout");
  selector.replaceChildren(option("","기름 사용 안 함 (O=0)"));
  const form=state.seasonGear?.weapon_forms?.[field("spec")];
  const offAllowed=form==="dual_one_hand"||form==="dual_two_hand";
  state.oilLoadouts=[];
  if(data?.schema==="v113_verified_installed_oil_loadouts_v1" &&
     data.status==="VERIFIED_INSTALLED_OIL_LOADOUTS" &&
     Number(data.target_ilevel)===Number(field("ilevel"))) {
    for(const item of data.items||[]) {
      const ids=item.selected_oil_item_ids_by_hand||{};
      if(!/^[a-f0-9]{64}$/.test(item.installed_manifest_sha256||"") ||
         !Object.keys(ids).length||Object.keys(ids).length>2||
         (ids.off_hand&&!offAllowed)||
         Object.values(ids).some(v=>!Number.isSafeInteger(v)||v<=0))continue;
      state.oilLoadouts.push(item);
      selector.appendChild(option(item.installed_manifest_sha256,
        item.display_name+" · 설치 확인"));
    }
  }
  const current={};
  for(const [hand,id] of [["main_hand","optimizer-oil-main-id"],
                          ["off_hand","optimizer-oil-off-id"]]) {
    if(field(id))current[hand]=Number(field(id));
  }
  const exact=state.oilLoadouts.find(item=>{
    const ids=item.selected_oil_item_ids_by_hand;
    return Object.keys(ids).length===Object.keys(current).length&&
      Object.entries(ids).every(([hand,id])=>current[hand]===id);
  });
  selector.value=exact?.installed_manifest_sha256||"";
  const count=state.oilLoadouts.length;
  tryApplyDefaultOil();
  $("optimizer-oil-loadout-status").textContent=count?
    "이 PC에 봉인된 "+count+"개 기름 조합 · 저장된 게임 빌드 "+
    data.game_build+" / ilvl "+data.target_ilevel+
    " · 실제 시즌·무기 적용은 실행 때 재검증":
    "현재 조건에 검증된 기름 조합이 없습니다. 기름 사용이 선택된 동안은 실행 전에 검증이 필요합니다. "+
    "기름을 사용하지 않으려면 체크를 해제하세요.";
}
async function refreshInstalledOilLoadouts() {
  const ilevel=valueInt("ilevel");
  const build=field("season-game-build");
  const extra=build?"&game_build="+encodeURIComponent(build):"";
  const data=await api("/api/v1/verified-oil-loadouts?ilevel="+ilevel+extra);
  renderInstalledOilLoadouts(data);
  // Flask and oil choices use the optimization target ilvl.
  // A single local verified-install scan is sufficient.
  renderInstalledFlaskChoices(data);
}
function chooseInstalledOilLoadout() {
  const chosen=state.oilLoadouts.find(item=>
    item.installed_manifest_sha256===field("optimizer-oil-loadout"));
  const ids=chosen?.selected_oil_item_ids_by_hand||{};
  oilUseIntent=Boolean(chosen);
  $("oil_main").checked=Boolean(ids.main_hand);
  $("oil_off").checked=Boolean(ids.off_hand);
  $("optimizer-oil-main-id").value=ids.main_hand??"";
  $("optimizer-oil-off-id").value=ids.off_hand??"";
  oilCompatibility();
  syncOilUseToggle();
}
function runeCompatibility() {
  const key=field("spec");
  const isDK=key.startsWith("deathknight/");
  $("dk-runeforge-panel").hidden=!isDK;
  const dual=state.seasonGear?.weapon_forms?.[key]==="dual_one_hand";
  const sourceReady=state.dkRuneIds.size>0;
  $("dk_rune_main").disabled=!isDK||!sourceReady;
  $("dk_rune_off").disabled=!isDK||!dual||!sourceReady;
  if(!isDK)$("dk_rune_main").value="";
  if(!dual)$("dk_rune_off").value="";
}
function craftSlot(item) {
  if(item.slot_hint)return item.slot_hint;
  if(item.inventory_type===11)return "finger1";
  if(item.inventory_type===20)return "chest";
  return null;
}
function chosenCraft(slot,exactItemId=null) {
  const family=classArmor[field("spec").split("/")[0]];
  const rows=state.seasonGear?.choices?.selectable_stat_craft||[];
  const valid=rows.filter(item=>{
    if(item.class_id!==4)return false;
    const actual=craftSlot(item);
    if(slot==="finger2") {
      if(actual!=="finger1")return false;
    } else if(actual!==slot)return false;
    return item.subclass_id===family ||
      (["back","finger1","finger2","neck"].includes(slot) &&
       (item.subclass_id===0||slot==="back"&&item.subclass_id===1));
  }).sort((a,b)=>a.item_id-b.item_id);
  return exactItemId===null?(valid[0]||null):
    (valid.find(item=>item.item_id===exactItemId)||null);
}
function gearInputs(nodeId, config) {
  const parent=$(nodeId),isSpecial=nodeId==="special-rows";
  const limit=isSpecial?8:2;
  const title=document.createElement("h3");
  title.textContent=config.title+" · 최대 "+limit+"개";
  const group=document.createElement("div");
  group.className="gear-group";group.appendChild(title);
  for (let i=0;i<limit;i++) {
    const row=document.createElement("div");row.className="gear-row";
    if(isSpecial&&i>=2)row.hidden=true;
    row.dataset.group=nodeId;row.dataset.index=String(i);
    const heading=document.createElement("p");heading.className="gear-row-title";
    heading.textContent=config.title+" "+(i+1);row.appendChild(heading);
    const grid=document.createElement("div");grid.className="gear-fields";
    for(const name of config.fields) {
      const label=document.createElement("label");
      const isPrivate=["bonus_id","redirected_base_stats"].includes(name)||
                  (isSpecial&&name==="slot");
      label.hidden=isPrivate;
      label.textContent=name==="item_id"?(isSpecial?"이번 시즌 장비":
        "정확한 제작장비 ItemID (선택 · 비우면 자동)"):
        name==="stat_a"?"제작 스탯 1":
        name==="stat_b"?"제작 스탯 2":
        name==="embellishment"?"장식 종류":(names[name]||name);
      const input=(name==="slot"||name==="embellishment"||
                   ["stat_a","stat_b"].includes(name)||
                   isSpecial&&name==="item_id") ?
        document.createElement("select"):document.createElement("input");
      input.dataset.field=name;
      if(name==="item_id"&&isSpecial) {
        input.appendChild(option("","이번 시즌 특수효과 장비 선택"));
        input.addEventListener("change",()=>{refreshSpecialSlots();refreshEquipmentSelectionUI();});
      }else if(name==="slot") {
        input.appendChild(option("","미선택"));
        for(const slot of statOptions)input.appendChild(option(slot,slotNames[slot]));
      }else if(name==="embellishment") {
        input.appendChild(option("","장식 종류 선택"));
        input.addEventListener("change",()=>syncCraftRow(row));
      }else if(name==="stat_a"||name==="stat_b") {
        input.appendChild(option("","스탯 선택"));
        for(const [value,labelName] of Object.entries(statNames))
          input.appendChild(option(value,labelName));
      }else if(name==="item_id"&&!isSpecial) {
        input.type="number";input.min="1";input.max="999999999";
        input.step="1";input.placeholder="미입력 시 시즌 목록에서 자동 선택";
      }else input.type="hidden";
      input.setAttribute("aria-label",config.title+" "+(i+1)+" "+label.textContent);
      input.autocomplete="off";label.appendChild(input);grid.appendChild(label);
    }
    row.appendChild(grid);
    const note=document.createElement("p");
    note.className="hint "+(isSpecial?"auto-slot-note":"craft-slot-note");
    note.textContent=isSpecial?"장비를 선택하면 부위가 자동 지정됩니다.":
      "장식 종류를 먼저 선택하면 호환 부위가 표시됩니다.";
    row.appendChild(note);group.appendChild(row);
  }
  if(isSpecial) {
    for(const row of group.querySelectorAll(".gear-row")){
      const launch=document.createElement("button");
      launch.type="button";launch.className="btn equipment-open special-equipment-open";
      launch.textContent="특수효과 장비 선택 (선택 사항)";
      launch.addEventListener("click",()=>openEquipmentPicker(
        row.querySelector('select[data-field="item_id"]'),launch));
      row.querySelector(".gear-fields").before(launch);
    }
    const add=document.createElement("button");add.type="button";
    add.className="btn secondary";add.textContent="+ 특수효과 장비 추가";
    add.addEventListener("click",()=>{
      const next=Array.from(group.querySelectorAll(".gear-row")).find(r=>r.hidden);
      if(next)next.hidden=false;
      add.disabled=!Array.from(group.querySelectorAll(".gear-row")).some(r=>r.hidden);
    });
    group.appendChild(add);
  }
  parent.appendChild(group);
}
function fillGearRows(nodeId, entries) {
  const group=$(nodeId),rows=Array.from(group.querySelectorAll(".gear-row"));
  if(entries.length>rows.length)throw Error("SESSION_GEAR_ROWS_OUT_OF_RANGE");
  const byCode={32:"crit",36:"haste",49:"mastery",40:"vers"};
  for(const [index,row] of rows.entries()) {
    const entry=entries[index]||null;
    row.hidden=nodeId==="special-rows"&&index>=Math.max(2,entries.length);
    const stats=(entry?.options?.crafted_stats||"").split("/");
    for(const input of row.querySelectorAll("[data-field]")) {
      const name=input.dataset.field;
      const value=!entry?"":name==="slot"?entry.slot:
        name==="item_id"?String(entry.item_id):
        name==="stat_a"?byCode[stats[0]]||"":
        name==="stat_b"?byCode[stats[1]]||"":
        String(entry.options?.[name]??"");
      if(nodeId==="special-rows"&&name==="item_id") {
        for(const opt of Array.from(input.options))
          if(opt.dataset.historic==="true")opt.remove();
        if(value&&!seasonChoice("special_effect_gear_candidate",value)) {
          const old=option(value,"이전 세션 특수장비 #"+value+" · 새 계획은 재선택");
          old.dataset.historic="true";input.appendChild(old);
        }
      }
      input.value=value;
    }
  }
  const add=group.querySelector(".gear-group > button");
  if(add)add.disabled=!rows.some(row=>row.hidden);
  if(nodeId==="special-rows")refreshSpecialSlots();
  else for(const row of rows)syncCraftRow(row,!!entries.length);
  refreshEquipmentSelectionUI();
}
function fillSessionInputs(payload) {
  const u=payload.user,c=u.character,t=u.target,b=u.combat;
  const spec=c.class+"/"+c.spec;
  if(!state.defaults.some(item=>item.class+"/"+item.spec===spec))
    throw Error("SESSION_SPEC_NOT_SUPPORTED");
  $("class-choice").value=c.class;
  populateSpecializationsForClass(c.class,spec);
  $("spec").value=spec;
  drawClassSpecTiles();
  setRaceSuggestions(state.defaults.find(x=>x.class+"/"+x.spec===spec));
  $("race").value=displayRace(c.race);
  $("talents").value=c.talents;
  showCharacterDefaultHint();
  $("ilevel").value=t.ilevel;
  // Exact v212 installation is recovered from the sealed session, never
  // from whichever build happens to be selected on the current page.
  $("season-game-build").value=payload.installed_season_game_build??"";
  const userVariant=payload.verified_user_variant;
  $("season-target-socket-count").value=userVariant?.socket_total??4;
  $("season-existing-special-gem-id").value=userVariant?.special_gem_id??"";
  $("season-selected-flask-id").value=userVariant?.flask_item_id??"";
  updateSeasonSocketBreakdown();
  $("final_T").value=t.final_T??"";
  $("manual-t-mode").checked=Boolean($("final_T").value);
  updateManualTMode();
  // A sealed pre-policy session has an implicit strict <50% rule.
  // Its restoration must display 50, never silently claim the new 60.
  $("max-single-stat-percent").value=u.max_single_stat_percent??50;
  setTrinketSelection("trinket1",u.trinkets[0].item_id,true);
  setTrinketSelection("trinket2",u.trinkets[1].item_id,true);
  $("targets").value=b.targets;
  $("duration").value=b.duration_seconds;
  $("raid_buffs").checked=b.raid_buffs;
  oilUseIntent=u.oil_hands.length>0;
  $("oil_main").checked=u.oil_hands.includes("main_hand");
  $("oil_off").checked=u.oil_hands.includes("off_hand");
  // The server derives these exact IDs from this session's sealed v212
  // install, never from untrusted browser memory or a latest-oil guess.
  const restoredOils=payload.verified_oil_item_ids_by_hand||{};
  $("optimizer-oil-main-id").value=restoredOils.main_hand??"";
  $("optimizer-oil-off-id").value=restoredOils.off_hand??"";
  oilCompatibility();
  renderInstalledOilLoadouts(state.oilCatalog);
  runeCompatibility();
  // Saved historical choices remain legible but are not auto-promoted to
  // the newest installed season's selectable list.
  for(const [id,hand] of [["dk_rune_main","main_hand"],
                          ["dk_rune_off","off_hand"]]) {
    const value=String(u.runeforge_by_hand?.[hand]??"");
    const node=$(id);
    for(const prior of Array.from(node.options))
      if(prior.dataset.historic==="true")prior.remove();
    if(value&&!Array.from(node.options).some(x=>x.value===value)) {
      const old=option(value,"이전 세션 룬 #"+value+" · 새 선택은 시즌 검증 필요");
      old.dataset.historic="true";node.appendChild(old);
    }
    node.value=value;
  }
  const choices=u.consumable_choices||{};
  for(const key of ["food","potion","augmentation"]) {
    const node=$(key),value=choices[key]??"source_default";
    // Preserve old sealed-session choices for inspection. A historical
    // SimC token alone does not grant a fresh-season user option.
    for(const previous of Array.from(node.options))
      if(previous.dataset?.historic==="true")previous.remove();
    if(!Array.from(node.options).some(o=>o.value===value)) {
      const names={food:"음식",potion:"물약",augmentation:"증강 룬"};
      const old=option(value,"이전 세션 "+names[key]+" · "+value+" (새 시즌 미승인)");
      old.dataset.historic="true";node.appendChild(old);
    }
    node.value=value;
  }
  const oldOmnium=choices.omnium_talents??"source_default";
  const omni=$("omnium");
  for(const x of Array.from(omni.options))
    if(x.dataset.historic==="true")x.remove();
  if(!Array.from(omni.options).some(x=>x.value===oldOmnium)){
    const historical=option(oldOmnium,"기존 세션 4열 선택 유지");
    historical.dataset.historic="true";omni.appendChild(historical);
  }
  omni.value=oldOmnium;
  const diamondValue=String(choices.diamond_id??0);
  const diamond=$("diamond");
  for(const x of Array.from(diamond.options))
    if(x.dataset.historic==="true")x.remove();
  if(!Array.from(diamond.options).some(x=>x.value===diamondValue)) {
    const historical=option(diamondValue,"이전 세션 다이아몬드 #"+diamondValue+" · 새 시즌 미승인");
    historical.dataset.historic="true";diamond.appendChild(historical);
  }
  diamond.value=diamondValue;
  fillGearRows("special-rows",u.special_items||[]);
  fillGearRows("crafted-rows",u.embellishments||[]);
  const restoredEagle=u.selected_season_enchants?.finger1===7967;
  if(restoredEagle&&!state.eagleApproved)
    throw Error("SAVED_EAGLE_SEASON_EVIDENCE_UNAVAILABLE");
  $("season_enchant_finger1").value=restoredEagle?"7967":"";
  // Recover the exact local inputs from this machine's saved session only.
  // No talent strings or OS file paths are stored in browser localStorage.
  $("binary").value=payload.binary;
  $("revision").value=payload.revision;
  $("static_cache").value=payload.static_cache??"";
  showRepresentativeScope();
  syncSearchChoices();
}
function selectedGear(nodeId, group) {
  const result=[],isCraft=group==="embellishments";
  if(!isCraft)refreshSpecialSlots();
  for(const row of $(nodeId).querySelectorAll(".gear-row")) {
    const fields={};
    for(const input of row.querySelectorAll("[data-field]"))
      fields[input.dataset.field]=input.value.trim();
    if(!Object.values(fields).some(Boolean))continue;
    if(isCraft) {
      if(!fields.slot||!fields.embellishment||!fields.stat_a||!fields.stat_b)
        throw Error("장식 종류·호환 부위·제작 스탯 2개를 선택해 주세요.");
      if(!state.options?.embellishments?.[fields.embellishment]?.slots?.includes(fields.slot))
        throw Error("이 장식은 선택 부위에 사용할 수 없습니다.");
      if(fields.stat_a===fields.stat_b)
        throw Error("제작 스탯은 서로 다른 두 가지를 선택해야 합니다.");
      // Never replace an explicit/restored ID with a different first match.
      // Source candidate membership is a preflight; the server still owns
      // final item, build, budget, and profile admission.
      if(fields.item_id&&!/^[1-9][0-9]{0,8}$/.test(fields.item_id))
        throw Error("제작장비 ItemID는 1~999999999의 정확한 양의 정수여야 합니다.");
      const resolved=chosenCraft(fields.slot,
        fields.item_id?Number(fields.item_id):null);
      if(!resolved)throw Error(fields.item_id?
        "지정한 제작장비 ItemID가 이번 시즌의 해당 직업·부위 후보 목록에 없습니다. 다른 장비로 대체하지 않습니다.":
        "이 직업·부위에 사용할 시즌 제작장비가 없습니다.");
      const raw={"crafted_stats":craftStats[fields.stat_a]+"/"+
                  craftStats[fields.stat_b],"embellishment":fields.embellishment};
      // Existing restored bonus IDs are kept only for the EXACT same item.
      if(fields.bonus_id&&Number(fields.item_id)===resolved.item_id)
        raw.bonus_id=fields.bonus_id;
      result.push({slot:fields.slot,item_id:resolved.item_id,options:raw});
    }else {
      if(!fields.slot||!/^[0-9]+$/.test(fields.item_id))
        throw Error("시즌 특수장비를 선택해 주세요. 부위가 불가능하거나 중복됐을 수 있습니다.");
      if(!seasonChoice("special_effect_gear_candidate",fields.item_id))
        throw Error("이번 시즌 특수효과 장비 목록에서 선택해야 합니다.");
      const options={};
      for(const k of ["bonus_id","redirected_base_stats"])
        if(fields[k])options[k]=fields[k];
      result.push({slot:fields.slot,item_id:Number(fields.item_id),options});
    }
  }
  if(result.length>(isCraft?2:8))throw Error("선택한 장비 수가 제한을 초과했습니다.");
  return result;
}
function buildRequest() {
  // v356: binary/revision moved into settings and are no longer form descendants.
  // Keep their same required/pattern validation before any session request.
  if(!$("binary").checkValidity()||!$("revision").checkValidity()){
    switchView("settings");
    $("simc-technical-panel").open=true;
    const invalid=!$("binary").checkValidity()?$("binary"):$("revision");
    invalid.reportValidity();invalid.focus();
    throw Error("SimulationCraft 실행 파일 경로와 Git revision을 확인해 주세요.");
  }
  if(!field("trinket1")||!field("trinket2")){
    switchView("optimizer");
    openEquipmentPicker($(!field("trinket1")?"trinket1":"trinket2"));
    throw Error("장신구 두 개를 이번 시즌 목록에서 선택해 주세요.");
  }
  if(!$("optimizer-form").reportValidity()) throw Error("필수 입력과 수치 범위를 확인해 주세요.");
  const spec=field("spec");
  const source=state.defaults.find(d=>d.class+"/"+d.spec===spec);
  if(!source) throw Error("지원되는 전문화를 선택해 주세요.");
  const resolvedRace=simcRace(field("race"));
  const provenRaces=state.allowedRacesBySpec[spec];
  if(Array.isArray(provenRaces)&&
     !provenRaces.includes(resolvedRace))
    throw Error("이 전문화에서 확인된 종족을 선택해 주세요.");
  if(["druid","demonhunter","evoker"].includes(source.class)&&
     (!resolvedRace||resolvedRace==="dwarf"))
    throw Error("이 전문화에서 사용할 수 있는 종족을 선택해 주세요.");
  if(!seasonChoice("trinket",valueInt("trinket1"))||
     !seasonChoice("trinket",valueInt("trinket2")))
    throw Error("장신구 2개를 이번 시즌 목록에서 선택해 주세요.");
  const approvedOptional=state.options?.current_season_product_choices;
  for(const name of ["food","potion","augmentation"]) {
    const allowed=approvedOptional?.[name];
    if(!Array.isArray(allowed)||!allowed.includes(field(name)))
      throw Error("이전 세션 또는 미검증 "+name+" 선택은 이번 시즌 새 최적화에 사용할 수 없습니다.");
  }
  if(!Array.isArray(approvedOptional?.diamond_id) ||
     !approvedOptional.diamond_id.includes(Number(field("diamond"))) ||
     !Array.isArray(approvedOptional?.omnium_talents) ||
     !approvedOptional.omnium_talents.includes(field("omnium")))
    throw Error("이번 시즌 미검증 다이아몬드·Omnium 선택은 새 최적화에 사용할 수 없습니다.");
  const controls={
    class:source.class,spec:source.spec,
    race:resolvedRace,talents:field("talents"),
    ilevel:valueInt("ilevel"),final_T:field("final_T") ? valueInt("final_T"):null,
    max_single_stat_percent:valueInt("max-single-stat-percent"),
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
  if(source.class==="deathknight") {
    const runeByHand={};
    if(field("dk_rune_main"))runeByHand.main_hand=Number(field("dk_rune_main"));
    if(field("dk_rune_off"))runeByHand.off_hand=Number(field("dk_rune_off"));
    if(Object.keys(runeByHand).length) {
      if(!Object.values(runeByHand).every(id=>state.dkRuneIds.has(id)))
        throw Error("이번 시즌 검증된 죽음의 기사 룬만 새 세션에 적용할 수 있습니다.");
      controls.runeforge_by_hand=runeByHand;
    }
  }
  if(field("season_enchant_finger1")) {
    if(!state.eagleApproved||field("season_enchant_finger1")!=="7967")
      throw Error("UNVERIFIED_ENCHANT_SELECTION_BLOCKED");
    controls.enchant_choices={finger1:7967};
  }
  if(!Number.isInteger(controls.ilevel)||controls.ilevel<266||controls.ilevel>344)
    throw Error("최신 시즌 대표장비의 목표 ilvl은 266~344입니다.");
  // A checked, default-on oil switch cannot silently turn into O=0.
  // Only a fully source-bound manifest for this class, hand count and
  // current ilvl is eligible for a NEW optimizer session.
  if(oilUseIntent&&!selectedFullVerifiedOil())
    throw Error("무기 기름 사용이 선택되어 있지만 이 시즌·전문화의 검증된 전체 무기 조합이 없습니다. 환경 구축 또는 미사용을 선택하세요.");
  const exactOils={};
  for(const [hand,node] of [["main_hand","optimizer-oil-main-id"],
                            ["off_hand","optimizer-oil-off-id"]]) {
    const input=field(node);
    if(!input)continue;
    if(!/^[1-9][0-9]*$/.test(input))
      throw Error("기름 ItemID는 양의 정수여야 합니다.");
    const id=Number(input);
    if(!Number.isSafeInteger(id)||id>999999999)
      throw Error("기름 ItemID 범위가 올바르지 않습니다.");
    if(!controls.oil_hands.includes(hand))
      throw Error("기름 ItemID를 지정한 무기 손도 체크해 주세요.");
    exactOils[hand]=id;
  }
  if(Object.keys(exactOils).length&&
     Object.keys(exactOils).length!==controls.oil_hands.length)
    throw Error("기름 ItemID를 지정하려면 선택한 모든 손의 ID가 필요합니다.");
  const gemSocketTotal=valueInt("season-target-socket-count");
  const specialText=field("season-existing-special-gem-id");
  if(specialText&&!/^[1-9][0-9]*$/.test(specialText))
    throw Error("특수보석 ItemID는 양의 정수여야 합니다.");
  const userSpecialGem=specialText?Number(specialText):null;
  if(!Number.isSafeInteger(gemSocketTotal)||gemSocketTotal<4||
     gemSocketTotal>64||
     (userSpecialGem!==null&&(!Number.isSafeInteger(userSpecialGem)||
      userSpecialGem>999999999||gemSocketTotal<5)))
    throw Error("전체 소켓은 4~64개이며 특수보석 사용 시 최소 5개입니다.");
  const flaskText=field("season-selected-flask-id");
  if(flaskText&&!/^[1-9][0-9]*$/.test(flaskText))
    throw Error("영약 ID는 검증된 양의 정수여야 합니다.");
  const flaskId=flaskText?Number(flaskText):null;
  if(flaskId!==null&&(!Number.isSafeInteger(flaskId)||flaskId>999999999))
    throw Error("영약 ID 범위가 잘못됐습니다.");
  const request={controls,binary:field("binary"),revision:field("revision"),
                 user_socket_total:gemSocketTotal,
                 user_special_gem_id:userSpecialGem,
                 selected_flask_item_id:flaskId,
                 static_cache:field("static_cache")||null,
                 current_season_product:true};
  // Explicit Build UI selection binds the following session to that exact
  // ALREADY INSTALLED season. This never asks v216 to collect fresh sources.
  const installedBuild=field("season-game-build");
  if(installedBuild) {
    if(!/^\d+(?:\.\d+){3}$/.test(installedBuild))
      throw Error("설치 시즌 게임 빌드 형식이 올바르지 않습니다.");
    request.installed_season_game_build=installedBuild;
  }
  if(Object.keys(exactOils).length)
    request.selected_oil_item_ids_by_hand=exactOils;
  return request;
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
  const changed=id!==state.session;
  state.session=id;
  if(changed) {
    // A new plan is not the result of the previously selected session.
    $("filled-result").hidden=true;
    $("empty-result").hidden=false;
    $("run-label").textContent="대기";
    $("progress-label").textContent="평가 0회";
    $("progress-pct").textContent="0%";
    $("progress-bar").style.width="0%";
    $("stage-text").textContent="이 세션의 상태를 조회 중입니다.";
    state.longrunEnabled=false;state.longrunResultReady=false;
    state.longrunCompleted=false;
  }
  $("session-id").textContent=id;
  refreshResultNavigation();
  switchView("results");
  $("restore-id").value=id;
  // Only the opaque ID (not talents, paths or other personal details) persists.
  try{localStorage.setItem("simc_secondary_session_id",id);}catch{}
}
function buttonState(active=false,ready=false) {
  state.running=active;
  const busy=state.busy;
  $("plan-btn").disabled=busy||active||!state.token;
  $("season-build-btn").disabled=busy||active||!state.token;
  $("user-variant-prepare-btn").disabled=busy||active||!state.token;
  if(busy){
    $("source-credentials-save-btn").disabled=true;
    $("source-credentials-clear-btn").disabled=true;
  }
  $("start-btn").disabled=busy||active||!hasRequiredSelections();
  $("resume-btn").disabled=busy||active||!state.session||state.longrunCompleted;
  $("cache-btn").disabled=busy||active||!state.session||!ready;
  $("cancel-btn").disabled=busy||!active;
  $("longrun-prepare-btn").disabled=busy||active||!state.token;
  $("longrun-start-btn").disabled=busy||active||!state.token;
  $("longrun-resume-btn").disabled=busy||active||!state.session||
                                   !state.longrunEnabled||state.longrunCompleted;
  $("longrun-cache-btn").disabled=busy||active||!state.longrunEnabled||
                                  !state.longrunResultReady;
  $("longrun-cancel-btn").disabled=busy||!active||!state.longrunEnabled;
  $("longrun-import-btn").disabled=busy||active||!state.longrunEnabled;
  $("resume-btn").disabled=busy||active||!state.session||state.longrunCompleted;
  $("cache-btn").disabled=busy||active||!state.session||!ready||state.longrunEnabled;
  $("restore-btn").disabled=busy;
}
async function withBusy(fn) {
  if(state.busy) return;
  state.busy=true;buttonState(state.running,false);
  try{await fn();}catch(err){
    if(err.message==="SESSION_NOT_FOUND")
      setNotice("현재 PC에는 해당 세션이 없습니다. 다른 컴퓨터에서 실행했다면 그 PC에서 조회해야 합니다.",true);
    else {
      // Never treat missing exact L as zero or run Native to guess it.
      const guidance={
        "V106_SPECIAL_EQUIPMENT_REQUIRES_EXACT_STATIC_CACHE":
          "선택 특수장비의 정적 캐시가 없습니다. 최신 시즌 경로에서 ‘SimC 최적화 실행’을 누르면 내부에서 정확한 L을 먼저 조회합니다.",
        "V106_STATIC_CACHE_NOT_FOUND":
          "지정한 정적 캐시 JSON 파일을 찾을 수 없습니다. 경로를 확인하세요.",
        "SPECIAL_L_REQUIRES_EXACT_NATIVE_STATIC_VARIANT":
          "정확한 L이 없어 예산 미리 확인은 차단됐습니다. 직접 캐시를 준비할 필요는 없습니다. ‘SimC 최적화 실행’을 누르면 로컬 SimC가 누락된 선택 특수장비의 정적 L을 최대 1회 조회한 뒤 DPS 계산을 진행합니다. 다른 레벨의 레코드를 대신 적용하지 않습니다.",
        "REFERENCE_FIXED_L_CONSTRAINT_UNRESOLVED":
          "선택 장비의 정확한 고정 스탯 L 하한을 확인할 수 없습니다.",
        "SPECIAL_L_DECORATED_NUMERIC_VARIANT_NOT_YET_ATTRIBUTABLE":
          "선택 특수장비의 보석·마부 옵션이 정적 스탯 L과 섞여 있어 안전하게 분리할 수 없습니다. 임의로 합산하지 않으며, 현재 이 조합은 차단합니다.",
        "SELECTED_SPECIAL_FLOOR_UNFEASIBLE":
          "선택 장비의 고정 스탯 하한 L과 입력 총량 T가 충돌합니다.",
        "SEASON_PROFILE_OIL_PHYSICAL_ITEMS_OR_HANDS_DRIFT":
          "선택한 무기 기름의 정확한 시즌 아이템·무기 적용 조건·고정 O가 현재 설치 환경과 일치하지 않습니다. 새 세션에서 기름을 해제하거나 정확한 기름이 등록된 환경을 사용하세요. 검증되지 않은 O를 0으로 처리하지 않습니다.",
        "WEB_FRESH_SELECTED_OIL_ITEM_IDS_NOT_INSTALLED":
          "선택한 물리 기름 ItemID·무기 손과 정확히 일치하는 검증된 시즌 환경이 설치되어 있지 않습니다. ‘변경한 소켓·영약·기름 구성 검증·준비’에서 해당 조합을 검증한 뒤 선택하세요.",
        "WEB_USER_VARIANT_REQUIRES_VERIFIED_SEASON_INSTALL":
          "선택한 소켓·특수보석·영약·기름 구성과 정확히 일치하는 검증 설치본이 없습니다. ‘변경한 소켓·영약·기름 구성 검증·준비’를 먼저 실행하세요. 기존 4소켓 구성의 J/F/O를 대신 적용하지 않습니다.",
        "WEB_USER_TOTAL_SOCKETS_INCLUDE_SPECIAL_INVALID":
          "전체 소켓 수는 일반보석 4개에 특수보석을 더한 수입니다. 특수보석을 넣으면 총 5개 이상이어야 합니다.",
        "WEB_USER_VARIANT_NOT_INSTALLED_OR_AMBIGUOUS":
          "현재 최적화 조건에 맞는 검증 설치본이 없거나 둘 이상입니다. 선택한 품목과 시즌·ilvl을 확인하고 해당 구성만 검증·준비하세요.",
        "WEB_PRIMARY_VERIFIED_SEASON_INSTALL_REQUIRED":
          "기본 최적화(64회)를 시작하려면 현재 게임 빌드의 G/J/F/O 검증 시즌 환경이 먼저 설치돼 있어야 합니다. ‘시즌 환경 확인·설치’를 완료한 뒤 시작하세요. ZIP에 들어 있는 과거 카탈로그는 현재 시즌 READY를 증명하지 않습니다.",
        "WEB_FRESH_EXACT_OIL_HAND_ID_SELECTION_INVALID":
          "기름 ItemID와 체크한 무기 손이 서로 다릅니다. 선택한 모든 손에 정확한 ItemID를 지정하세요.",
        "V216_REUSE_OIL_HANDS_MULTIPLE_VERIFIED_ITEMS_SELECT_ID":
          "같은 손에 서로 다른 검증 기름이 있습니다. 고급 기름 ItemID 항목에 정확한 물리 ID를 지정하세요.",
        "FIVE_TIER_LAYOUT_OUTSIDE_FOUR_ROW_CONTRACT":
          "기본 티어 4세트에 다섯 번째 티어 아이템이 추가되었습니다. 이미 포함된 티어 부위로 선택하거나 다른 특수장비 슬롯을 사용하세요."
      };
      setNotice("요청 차단 또는 오류: "+(guidance[err.message]||err.message),true);
    }
  }
  finally{state.busy=false;buttonState(state.running,$("filled-result").hidden===false);}
}

 // An explicitly copied diagnosis only; never persist raw source, private paths or API credentials.
let lastSeasonDiagnosticReceipt=null;
function compactSeasonBuildReceipt(data,forUserVariant=false) {
  // Read-only, allowlisted evidence projection; not an approval or READY Gate.
  const scope=data?.web_environment_scope||{};
  const source=data?.source_compilation||{};
  const progress=data?.zero_history_build||{};
  const owner=progress.required_core_source_owner_report||
    source.required_core_source_owner_report||null;
  const cleanCode=x=>typeof x==="string"&&/^[A-Z][A-Z0-9_]{0,119}$/.test(x)?
    x:null;
  const codes=x=>Array.isArray(x)?x.slice(0,100).map(cleanCode)
    .filter(Boolean):null;
  const build=x=>typeof x==="string"&&/^\d+(?:\.\d+){3}$/.test(x)?x:null;
  const sha=x=>typeof x==="string"&&/^[a-f0-9]{64}$/.test(x)?x:null;
  const integer=x=>Number.isSafeInteger(x)&&x>=0?x:null;
  const seenBoolean=x=>typeof x==="boolean"?x:null;
  const ready=scope.environment_ready===true&&
    scope.environment_installed===true;
  const installed=source.verified_environment_install||
    progress.versioned_environment_installed||{};
  const observed=owner?.original_source_owner_numeric_present;
  const gJFO=observed&&["G","J","F","O"].every(k=>
    typeof observed[k]==="boolean")?
    Object.fromEntries(["G","J","F","O"].map(k=>[k,observed[k]])):null;
  // A missing source_compilation in a verified-install cache hit is NOT
  // evidence of missing compiler inputs. Null means unobserved, not [].
  const stats={};
  if(ready)for(const key of ["G","J","F","B","T"]){
    stats[key]=integer(data?.[key]);
  }
  if(ready){
    stats.O=["crit_rating","haste_rating","mastery_rating",
      "versatility_rating"].every(k=>integer(data?.O?.[k])!==null)?
      Object.fromEntries(["crit_rating","haste_rating","mastery_rating",
        "versatility_rating"].map(k=>[k,data.O[k]])):null;
  }
  return JSON.stringify({
    schema:"v384_user_copied_season_build_diagnostic_v1",
    evidence_only_no_ready_authority:true,
    for_user_variant:forUserVariant===true,
    outcome:cleanCode(data?.status),
    game_build:build(scope.game_build||data?.installed_source_game_build),
    target_ilevel:integer(scope.target_ilevel),
    source_mode:{
      auto_initial_core:seenBoolean(scope.auto_initial_core_build_requested),
      native_G:seenBoolean(scope.local_native_G_requested),
      native_F:seenBoolean(scope.auto_native_F_requested),
      native_O:seenBoolean(scope.auto_native_O_requested),
      reused_verified_install:seenBoolean(scope.reused_verified_installed_season)
    },
    season_discovery_status:cleanCode(data?.season_discovery?.status),
    season_join_status:cleanCode(data?.season_join?.status),
    source_stage_status:cleanCode(progress.source_stage_status||
      data?.source_stage?.status),
    compiler_status:cleanCode(source.status||progress.source_compilation_status),
    compiler_missing:codes(source.missing??progress.source_compilation_missing),
    core_numeric_owner_present:gJFO,
    core_numeric_owner_missing:codes(
      owner?.original_source_owner_missing_for_selected_request),
    oil_selection_status:cleanCode(owner?.oil_selection_status),
    explicit_no_oil_awaits_v222:
      typeof owner?.explicit_no_oil_awaits_v222==="boolean"?
      owner.explicit_no_oil_awaits_v222:null,
    installed_by_v212:seenBoolean(owner?.full_environment_installed_verified_by_v212),
    requires:codes(progress.requires),
    native_G_status:cleanCode(progress.native_G_status),
    installed_manifest_sha256:sha(installed.manifest_sha256||
      data?.installed_manifest_sha256),
    verified_budget:ready?stats:null,
    environment_ready:ready,
    new_native_calls:integer(data?.native_calls),
    note:"Null means not observed in this response; not zero, false, or failure."
  },null,2);
}
async function copySeasonBuildDiagnostic() {
  if(lastSeasonDiagnosticReceipt===null)return;
  try {
    if(!navigator.clipboard?.writeText)throw Error("CLIPBOARD_UNAVAILABLE");
    await navigator.clipboard.writeText(lastSeasonDiagnosticReceipt);
    setNotice("시즌 진단 요약 복사 완료 · 비밀키·원본 파일 경로는 제외");
  }catch{
    setNotice("진단 복사를 지원하지 않는 브라우저입니다. localhost에서 다시 시도하세요.",true);
  }
}

function diagnoseSeasonBuildEvidence(data) {
  // UI-only, read-only classification. v212/v216 own ALL real admission.
  // A sealed DB2/WCL content-candidate join is NOT evidence that every loot
  // item belongs to this season; neither is an unknown optional WSE a global
  // blocker for an otherwise fully proven G/J/F/O installation.
  const scope=data?.web_environment_scope||{};
  const compiled=data?.source_compilation||{};
  const step=data?.zero_history_build||{};
  const join=data?.season_join?.status||"";
  const contentCandidatesJoined=
    join==="DB2_WCL_CANDIDATES_JOINED_SEASON_CONDITIONS_PENDING";
  const sourceSealed=step.season_content_candidate_join_sealed===true;
  const mode=(scope.auto_initial_core_build_requested===true?
    "기본 자동 G/F 구축 요청":
    scope.local_native_G_requested===true||
    scope.auto_native_F_requested===true||
    scope.auto_native_O_requested===true?
    "고급 선택 Native 요청":
    "원본 확인·수집 요청");
  const missing=Array.isArray(compiled.missing)?compiled.missing:[];
  const requires=Array.isArray(step.requires)?
    step.requires.filter(v=>!(sourceSealed&&v==="SOURCE_SEASON_JOIN_PENDING")):[];
  const firstMissing=(missing.length?
    "소스 컴파일 입력: "+String(missing[0]):
    requires.length?"후속 검증: "+String(requires[0]):
    "필수 원본의 상세 미완료 항목 미보고");
  const owners=step.required_core_source_owner_report;
  const observedOwners=owners?.original_source_owner_numeric_present;
  const coreOwnerSummary=observedOwners&&
      ["G","J","F","O"].every(key=>typeof observedOwners[key]==="boolean")?
    ["G","J","F","O"].map(key=>
      key+"="+(observedOwners[key]?"원본 확인":
        key==="O"&&owners.explicit_no_oil_awaits_v222?
          "기름 미사용·v222 확정 전":"증거 대기")).join(" / "):null;
  return {mode,contentCandidatesJoined,sourceSealed,
          firstMissing,coreOwnerSummary,
          compilerMissingCount:missing.length,
          requiredMissingCount:requires.length,
          isEnvironmentReady:scope.environment_ready===true&&
                             scope.environment_installed===true};
}
function showSeasonEnvironmentBuild(data,forUserVariant=false) {
  const scope=data?.web_environment_scope||{};
  const step=data?.zero_history_build||{};
  const source=data?.source_compilation||{};
  const diagnosed=diagnoseSeasonBuildEvidence(data);
  const needs=[...(Array.isArray(step.requires)?
    step.requires.filter(v=>!(diagnosed.sourceSealed&&
                            v==="SOURCE_SEASON_JOIN_PENDING")):[]),
    ...(Array.isArray(source.missing)?source.missing.map(x=>"SOURCE_COMPILER:"+x):[]),
    ...(Array.isArray(source.selected_J_F_source_owner_numeric_unadmitted?.missing)?
      source.selected_J_F_source_owner_numeric_unadmitted.missing.map(x=>"J/F 원본: "+x):[]),
    ...(Array.isArray(source.selected_J_F_source_owner_quality_unadmitted?.missing)?
      source.selected_J_F_source_owner_quality_unadmitted.missing.map(x=>"J/F 품질: "+x):[])];
  const ready=scope.environment_ready===true&&scope.environment_installed===true;
  $("optimizer-environment-state").textContent=ready?
    "시즌 G/J/F/O 검증 설치 확인 · 선택한 개인 조건은 별도 검증":
    "시즌 환경 설치·검증 미완료 · 환경 설정에서 원인을 확인하세요";
  // Only a user-specific installed v212 READY report can show this T.
  // Source-only numeric previews or unadmitted candidate joins are not budgets.
  if(ready&&forUserVariant&&!$("manual-t-mode").checked&&
     Number.isSafeInteger(Number(data?.T))&&Number(data.T)>0){
    $("budget-preview-total").textContent=number(Number(data.T))+" rating · 개인 구성 검증";
    $("budget-preview-note").textContent=
      "같은 시즌 원본에서 검증한 G/J/F/O · B/T입니다. 구성 변경 후에는 다시 확인해야 합니다.";
  }
  // v347: public Wago DB2 + pinned SimC source may be sealed, but without
  // independently verified season/raid membership cannot approve G/J/F/O.
  // Explain a real PENDING result without asking users for developer keys.
  const missingSeasonScope=!ready&&
    data?.season_discovery?.status==="AUTHENTICATED_SEASON_CREDENTIALS_MISSING"&&
    data?.season_join?.status==="AUTHENTICATED_SEASON_JOIN_NOT_READY";
  const unique=[...new Set([...needs,...(missingSeasonScope?[
    "현재 시즌·레이드 범위를 검증할 공인 원본이 부족합니다. 개발자용 비밀키를 입력하는 대신 검증된 시즌 자료 업데이트가 필요합니다. 환경 READY 전에는 기본 계산을 시작할 수 없습니다."
  ]:[])])];
  const node=$("season-build-stage");
  const headline=$("season-build-summary");
  const technicalPanel=$("season-build-technical-panel");
  const technical=$("season-build-technical");
  technical.textContent="";technicalPanel.hidden=true;
  const discovery=data?.season_discovery?.status||"원본 단계 미보고";
  const joined=data?.season_join?.status||"원본 단계 미보고";
  const wago=step.source_stage_status||data?.source_stage?.status||"원본 단계 미보고";
  if(ready) {
    headline.textContent="시즌 G/J/F/O 검증 환경 설치 완료 · 새 최적화 실행 프로필은 해당 소켓 구성과 일치해야 합니다.";
  } else if(joined==="AUTHENTICATED_SEASON_JOIN_NOT_READY"){
    headline.textContent="설치 보류 · 활성 시즌·레이드 연결이 아직 확인되지 않았습니다. 인증정보가 저장됐는지만으로는 확인 완료가 아닙니다. "+
      "원본 수집 상태: "+wago+" · Blizzard/WCL 단계: "+discovery+". "+
      "아래 1차 미완료 원인 때문에 후속 티어·장비·G/J/F/O 조건이 함께 보류될 수 있습니다.";
  } else if(joined==="DB2_WCL_CANDIDATES_JOINED_SEASON_CONDITIONS_PENDING"){
    headline.textContent="시즌 콘텐츠 후보 결합 완료 · 일부 개별 아이템 조건은 미해석 상태입니다. "+
      "미선택 후보의 미해석은 그 자체로 환경 전체의 설치 차단 근거가 아닙니다. "+
      diagnosed.mode+" · "+diagnosed.firstMissing+
      " · 실제 설치는 선택된 필수 G/J/F/O·티어 증거로 판정합니다.";
  } else if(joined==="LIVE_SEASON_SCOPE_AMBIGUOUS_PENDING"){
    headline.textContent="설치 보류 · 원본은 조회했지만 활성 시즌 범위를 하나로 확정할 수 없습니다. "+
      "Blizzard/WCL 단계: "+discovery+" · Wago DB2 단계: "+wago+".";
  } else {
    headline.textContent="설치 보류 · 시즌 원본과 예산의 필수 검증이 남았습니다. "+
      "Blizzard/WCL 단계: "+discovery+" · 시즌 연결: "+joined+
      " · Wago DB2 단계: "+wago+".";
  }
  if(data?.status==="VERIFIED_INSTALLED_SAME_SEASON_SOURCE_REUSED"&&ready){
    node.textContent="기존 검증 시즌 환경 재사용 완료 · 저장된 원본 빌드 "+
      data.installed_source_game_build+
      (data.official_F_physical_source?.physical_item_id?
        " · F 영약 ItemID "+data.official_F_physical_source.physical_item_id+
        " (원본 SimC Native 확인)":"")+
      " · G="+data.G+" J="+data.J+" F="+data.F+
      (data.selected_oil_item_ids_by_hand&&
        Object.keys(data.selected_oil_item_ids_by_hand).length?
        " · 확인된 기름 "+Object.entries(data.selected_oil_item_ids_by_hand)
          .map(([hand,id])=>hand+" #"+id).join(", "):"")+
      " / B="+data.B+" T="+data.T+
      " · 신규 수집/Native 0회 · 최신 서버 시즌 재인증 없음"+
      " · SimC DPS 캐시는 사용한 실행 바이너리별 분리";
    const details=$("season-build-pending");
    $("season-build-missing").replaceChildren();
    details.hidden=true;
    return;
  }
  const numeric=step.selected_auto_v222_numeric_preview_unadmitted?.calculation;
  const autoFO=source.automatic_F_O_measurement_candidates_unadmitted;
  const measuredF=source.automatic_F_native_measurements_unadmitted;
  const measuredO=source.automatic_O_native_measurements_unadmitted;
  const autoFlask=source.auto_observed_flask_budget_preview_unadmitted;
  const sourceDefaultF=source.automatic_default_F_source_selection_unadmitted;
  const originalVerifiedF=source.original_J_F_verified_components_not_full_environment?.F;
  node.textContent=(ready?"시즌 환경 설치 완료":"원본 수집·검증 진행 결과 (설치 미완료)")+
    " · 요청 빌드 "+(scope.game_build||"–")+
    (scope.selected_flask_item_id?" · 지정 F ItemID "+scope.selected_flask_item_id:"")+
    (scope.selected_oil_item_ids_by_hand&&
      Object.keys(scope.selected_oil_item_ids_by_hand).length?
      " · 선택 기름 "+Object.entries(scope.selected_oil_item_ids_by_hand)
        .map(([hand,id])=>hand+" #"+id).join(", "):"")+
    (scope.source_target_socket_count?" · "+(forUserVariant?"개별 선택":"시즌 내부 대표")+" 소켓 "+scope.source_target_socket_count+"개 (SimC 적용 미검증)":"")+
    (scope.game_build_source==="BLIZZARD_PUBLIC_RETAIL_KR"?" (Retail 자동)":"")+
    " · 원본 "+(step.source_stage_status||data?.source_stage?.status||"미확정")+
    " · 컴파일 "+(source.status||step.source_compilation_status||"대기")+
    " · G 관측 "+(step.native_G_status||"대기")+
    (autoFO?.source_only===true&&autoFO.candidate_count>0?
      " · F/O 자동 발견 "+autoFO.candidate_count+"건(측정 후보·미승인)":"")+
    (measuredF?.status==="AUTO_F_NATIVE_MEASURED_SOURCE_ONLY"?
      " · F Native "+measuredF.attempted+"/"+measuredF.total_source_candidates+
      "건(미승인)":"")+
    (measuredO?.status==="AUTO_O_NATIVE_MEASURED_SOURCE_ONLY"?
      " · O Native "+measuredO.attempted+"/"+measuredO.total_source_candidates+
      "건(손별 측정 후보·미승인)":"")+
    (sourceDefaultF?.status==="AUTO_DEFAULT_F_SOURCE_ITEM_SELECTED_UNADMITTED"?
        " · 대표 F ItemID "+sourceDefaultF.selected_physical_items_unadmitted.flask_item_id+
        " (시즌 원본 최고품질 후보·최적 영약 추천 아님)":"")+
    (originalVerifiedF?.source_verification==="EXACT_NATIVE"?
        " · F 원본 실측 "+originalVerifiedF.rating+" (환경 정식 등록 전)":"")+
    (scope.four_stat_ordinary_default_requested===true?
        " · 일반보석 4종 기본 배치 요청(특수효과 SimC 담당)":
      scope.four_stat_ordinary_source_requested===true?
        " · 일반보석 4종 시즌 원본 수집 요청(J 승인·배치 별도)":"")+
    (diagnosed.coreOwnerSummary?
      " · 필수 G/J/F/O 원본 "+diagnosed.coreOwnerSummary:"")+
    " · 실행 경로 "+diagnosed.mode+
    " · 신규 Native "+(Number(data?.native_calls)||0)+"회"+
    (autoFlask?.status==="ONE_OBSERVED_FLASK_NO_OIL_NUMERIC_PREVIEW_UNADMITTED"?
      (scope.auto_select_observed_F_no_oil===true?
        " · F 관측 1가족 선택 요청·기름 미사용(실제 원본 인증 대기)":
        " · F 관측 1가족 · 기름 미적용 가정(공식 선택 아님)"):"")+
    (numeric?.numeric_preview_only===true&&numeric.environment_ready===false?
       " · 관측 수치(미승인) G="+numeric.reference_G+
       " J="+numeric.J+" F="+numeric.F+
       " O="+Object.values(numeric.fixed_O||{}).reduce((a,b)=>a+Number(b||0),0)+
       " / B="+numeric.base_B+" T="+numeric.final_T:"")+
    " · 환경 매니페스트 "+(step.versioned_environment_source_stage?.stage_status||"입력 대기")+
    " · 진단 항목 "+unique.length+"개(연쇄 포함) · DPS 최적화 0회"+
    (scope.user_character_or_trinkets_required===false?" · 사용자 장비 입력 없음":"")+
    (missingSeasonScope?" · 현재 시즌·레이드 범위 미검증(환경 설치 보류)":"");
  // Preserve full source/Native diagnostics for troubleshooting, without
  // treating dependent PENDING rows as separate user-facing failures.
  technical.textContent=node.textContent;
  technicalPanel.hidden=false;
  node.textContent=ready?
    "시즌 G/J/F/O 검증 환경 설치 완료 · 새 세션의 소켓·영약·기름 구성은 별도로 확인합니다.":
    joined==="DB2_WCL_CANDIDATES_JOINED_SEASON_CONDITIONS_PENDING"?
    "시즌 콘텐츠 후보 결합 완료 · "+diagnosed.mode+
    " · "+diagnosed.firstMissing:
    "시즌 환경 설치 보류 · "+diagnosed.mode+
    " · "+diagnosed.firstMissing;
  const details=$("season-build-pending"),list=$("season-build-missing");
  list.replaceChildren();
  for(const missing of unique){
    const item=document.createElement("li");
    item.textContent=String(missing);
    list.appendChild(item);
  }
  details.hidden=unique.length===0;
}
const sourceCredentialFields=[
  ["source-blizzard-id","blizzard_client_id"],
  ["source-blizzard-secret","blizzard_client_secret"],
  ["source-wcl-id","wcl_client_id"],
  ["source-wcl-secret","wcl_client_secret"]
];
async function refreshSourceCredentialStatus() {
  const status=await api("/api/v1/source-credentials/status");
  $("source-credentials-status").textContent=(
    !status.supported?"Windows 자격 증명 관리자 전용 기능입니다.":
    status.configured?"Blizzard·WCL API 인증정보가 이 Windows 계정에 저장되어 있습니다.":
    "저장된 API 인증정보가 없습니다. 새 시즌 갱신에 인증이 필요할 경우 등록하세요.");
  $("source-credentials-save-btn").disabled=!status.supported||!state.token;
  $("source-credentials-clear-btn").disabled=!status.supported||!status.configured||!state.token;
}
async function saveSourceCredentials() {
  const payload={};
  for(const [id,key] of sourceCredentialFields){
    payload[key]=$(id).value;
    if(!payload[key]||payload[key].trim()!==payload[key])
      throw Error("네 개의 API 인증정보를 모두 정확히 입력해야 합니다.");
  }
  if(!window.confirm("이 Windows 계정의 자격 증명 관리자에 API 인증정보를 저장할까요? 외부 서버로 키를 전송하지 않습니다."))return;
  try {
    await api("/api/v1/source-credentials/save",{method:"POST",payload});
    setNotice("내 API 인증정보 저장 완료 · 실제 시즌 조회는 ‘시즌 환경 확인·설치’에서만 수행됩니다.");
    await refreshSourceCredentialStatus();
  } finally {
    for(const [id] of sourceCredentialFields)$(id).value="";
    for(const key of Object.keys(payload))payload[key]="";
  }
}
async function clearSourceCredentials() {
  if(!window.confirm("이 Windows 계정에 저장된 두 API 인증정보를 삭제할까요? 기존 시즌 데이터·세션은 보존됩니다."))return;
  await api("/api/v1/source-credentials/clear",{method:"POST",payload:{}});
  for(const [id] of sourceCredentialFields)$(id).value="";
  setNotice("API 인증정보 삭제 완료 · 저장된 시즌 결과는 변경하지 않았습니다.");
  await refreshSourceCredentialStatus();
}
function updateSeasonSocketBreakdown() {
  const total=Number(field("season-target-socket-count"));
  const special=field("season-existing-special-gem-id")!==""?1:0;
  const ordinary=total-special;
  $("season-socket-breakdown").textContent=(
    !Number.isSafeInteger(total)||total<4||total>64?
      "전체 소켓 수는 4~64개여야 합니다.":
    ordinary<4?
      "일반보석 4종을 유지하려면 특수보석 포함 총 5개 이상을 선택해야 합니다.":
      "일반보석 "+ordinary+"개 + 특수보석 "+special+
      "개 = 전체 소켓 "+total+"개 · 변경 시 새 구성 재검증 필요");
}
function beginSeasonBuildActivity() {
  const section=$("season-build-running");
  const elapsed=$("season-build-elapsed");
  const started=Date.now();
  section.hidden=false;
  const redraw=()=>{elapsed.textContent=Math.floor((Date.now()-started)/1000)+
    "초 경과 · 단계별 실제 진행률은 서버 결과에서 확인";};
  redraw();
  const clock=window.setInterval(redraw,1000);
  return ()=>{window.clearInterval(clock);section.hidden=true;};
}
async function buildSeasonEnvironment(forUserVariant=false) {
  const supplied_build=field("season-game-build");
  if(supplied_build&&!/^\d+(?:\.\d+){3}$/.test(supplied_build))
    throw Error("게임 빌드는 네 개의 숫자 그룹 형식이어야 합니다.");
  const game_build=supplied_build||null;
  const refresh_reason=forUserVariant?null:
    (field("season-refresh-reason")||null);
  if(refresh_reason!==null&&!["season_change","expansion_change",
      "item_content_change"].includes(refresh_reason))
    throw Error("지원하지 않는 시즌 갱신 조건입니다.");
  const target_ilevel=forUserVariant?valueInt("ilevel"):
    valueInt("season-target-ilevel");
  if(target_ilevel<1||target_ilevel>1000)
    throw Error("목표 ilvl은 1~1000 범위여야 합니다.");
  // This is a separate explicit per-user numeric/source preparation.
  // A new selectable budget cannot silently borrow G/J/F/O from the
  // canonical four-gem season environment.
  const nativeRequested=$("season-native-g").checked||forUserVariant;
  const auto_native_F_requested=$("season-native-f").checked||forUserVariant;
  const auto_native_O_requested=$("season-native-o").checked||
    (forUserVariant&&(Boolean(field("season-oil-main-id"))||
                      Boolean(field("season-oil-off-id"))||
                      Boolean(field("optimizer-oil-main-id"))||
                      Boolean(field("optimizer-oil-off-id"))));
  const auto_select_observed_F_no_oil=$("season-auto-f-no-oil").checked||
    (forUserVariant&&!field("season-selected-flask-id")&&
     !auto_native_O_requested);
  const selectedFlask=forUserVariant?field("season-selected-flask-id"):"";
  if(selectedFlask&&!/^[1-9][0-9]*$/.test(selectedFlask))
    throw Error("영약 ItemID는 양의 정수여야 합니다.");
  const selected_flask_item_id=selectedFlask?Number(selectedFlask):null;
  if(selected_flask_item_id!==null&&
      (!Number.isSafeInteger(selected_flask_item_id)||
       selected_flask_item_id>999999999))
    throw Error("영약 ItemID 범위가 올바르지 않습니다.");
  if(selected_flask_item_id!==null&&auto_select_observed_F_no_oil)
    throw Error("정확한 영약 ItemID 선택과 영약 자동 선택은 함께 사용할 수 없습니다.");
  // The advanced oil controls select physical item identities only. Their
  // static CHMV values, spell syntax, quality and eligibility are *never*
  // supplied by the browser; existing season source owners determine them.
  const selected_oil_item_ids_by_hand={};
  for(const [hand,node] of [["main_hand","season-oil-main-id"],
                           ["off_hand","season-oil-off-id"]]) {
    const runtimeId=hand==="main_hand"?"optimizer-oil-main-id":
      "optimizer-oil-off-id";
    const advanced=field(node),userSelected=field(runtimeId);
    if(forUserVariant&&advanced&&userSelected&&advanced!==userSelected)
      throw Error("사용자 기름 ItemID와 고급 검증 ID가 서로 다릅니다.");
    const value=forUserVariant?(advanced||userSelected):"";
    if(value&&!/^[1-9][0-9]*$/.test(value))
      throw Error("선택한 기름 ItemID는 양의 정수여야 합니다.");
    if(value){
      const physical=Number(value);
      if(!Number.isSafeInteger(physical)||physical>999999999)
        throw Error("선택한 기름 ItemID 범위가 올바르지 않습니다.");
      selected_oil_item_ids_by_hand[hand]=physical;
    }
  }
  const oilHands=Object.keys(selected_oil_item_ids_by_hand);
  if(oilHands.length&&selected_flask_item_id===null)
    throw Error("기름을 선택한 시즌 환경은 정확한 영약 ItemID도 지정해야 합니다.");
  if(oilHands.length&&auto_select_observed_F_no_oil)
    throw Error("기름 선택과 기름 미사용 영약 자동 선택은 함께 실행할 수 없습니다.");
  const existingSpecial=forUserVariant?field("season-existing-special-gem-id"):"";
  if(existingSpecial&&!/^[1-9][0-9]*$/.test(existingSpecial))
    throw Error("기존 특수보석 ItemID는 양의 정수여야 합니다.");
  const existing_special_gem_id=existingSpecial?Number(existingSpecial):null;
  if(existing_special_gem_id!==null&&
      (!Number.isSafeInteger(existing_special_gem_id)||
       existing_special_gem_id>999999999))
    throw Error("특수보석 ItemID 범위가 올바르지 않습니다.");
  const requested_sockets=forUserVariant?valueInt("season-target-socket-count"):4;
  if(!Number.isSafeInteger(requested_sockets)||
     requested_sockets<(existing_special_gem_id===null?4:5)||
     requested_sockets>64)
    throw Error("일반보석은 4개 이상, 선택 특수보석까지 넣는 경우 5개 이상이 필요합니다.");
  const source_target_socket_count=requested_sockets;
  if(auto_select_observed_F_no_oil&&(!auto_native_F_requested||auto_native_O_requested))
    throw Error("영약 자동 선택은 F Native 측정을 켜고 기름 O 측정을 끈 상태에서만 사용할 수 있습니다.");
  // A selected, scaled oil uses only the existing SimC precombat gear
  // runner/cache. Unselected oil candidates remain pinned-source-only.
  const selectedOilNative=oilHands.length>0&&auto_native_O_requested;
  const native_F_O_requested=auto_native_F_requested||selectedOilNative;
  const executable=(nativeRequested||native_F_O_requested)?field("binary"):null;
  if((nativeRequested||native_F_O_requested)&&!executable)
    throw Error("G/F 또는 선택된 기름의 정적 SimC 측정에는 실행 파일 경로가 필요합니다.");
  // G is truly optional even if F/O uses the same executable.
  const native_G_binary=nativeRequested?executable:null;
  const consumable_native_binary=native_F_O_requested?executable:null;
  // Existing v216 source-owned G/F measurements, never a new effect engine.
  // Advanced item/native selection takes precedence over this default.
  const explicitAdvanced=Boolean(nativeRequested||auto_native_F_requested||
      auto_native_O_requested||auto_select_observed_F_no_oil||
      selected_flask_item_id!==null||oilHands.length);
  const auto_initial_core_build=$("season-auto-core").checked&&!explicitAdvanced;
  const auto_initial_core_simc_binary=
      auto_initial_core_build?(field("binary")||null):null;
  if(auto_initial_core_build&&!auto_initial_core_simc_binary)
    throw Error("최초 G/F 자동 구축에는 SimC 실행파일 경로가 필요합니다. 경로를 지정하거나 자동 구축 선택을 해제하면 원본만 수집할 수 있습니다.");
  const revision=field("revision");
  if(revision&&!/^(?:[a-f0-9]{7,12}|[a-f0-9]{40})$/.test(revision))
    throw Error("SimC revision은 7~12자리 또는 40자리 소문자 16진수여야 합니다.");
  if(!window.confirm((refresh_reason?
      "선택한 시즌/콘텐츠 갱신 요청을 시작할까요? 기존 봉인 자료는 보존됩니다. ":
      "기존 검증 시즌 환경을 우선 재사용하고, 없으면 원본 구축을 시작할까요? ")+
      "필요 시 외부 네트워크를 사용할 수 있습니다."+
      (auto_initial_core_build?
       " 검증 설치 재사용 시 Native 0회; 신규 시즌에는 기존 G 최대 1회와 대표 영약 F 최대 2회만 측정할 수 있습니다. 원본 검증이 부족하면 설치하지 않습니다.":
       (nativeRequested?" 기존 G Native 최대 1회 실행될 수 있습니다.":" Native는 기본적으로 실행하지 않습니다."))+
      (auto_native_F_requested?
       (auto_select_observed_F_no_oil?
         " 기본 영약 F 후보 1종만 신규 SimC Native 최대 2회 측정합니다. 기존 캐시를 재사용하며 공식 F 등록은 별도입니다.":
         " 영약 F 후보만 최대 8회 신규 Native로 관측할 수 있습니다. 기름은 Native를 실행하지 않습니다."):"")+
      (auto_native_O_requested?
       (selectedOilNative?
        " 선택한 기름의 스케일링 값은 기존 실행 캐시를 먼저 재사용하고, 필요한 손에만 SimC 측정을 수행합니다.":
        " 선택한 기름이 없으므로 SimC 원본 확인만 수행하며 O Native는 실행하지 않습니다."):"")))
    return;
  $("season-build-stage").textContent="시즌 환경 요청 처리 중 · 응답을 받으면 원본 단계 결과를 구분해서 표시합니다…";
  if(forUserVariant) $("user-variant-status").textContent=
    "선택한 개별 구성의 시즌 원본·J/F/O 예산 재검증 요청 중…";
  lastSeasonDiagnosticReceipt=null;
  $("season-diagnostic-copy-btn").disabled=true;
  $("season-build-pending").hidden=true;
  $("season-build-summary").textContent="검증 진행 중 · 결과 미확정 (READY 아님)";
  const stopSeasonActivity=beginSeasonBuildActivity();
  try {
    const report=await api("/api/v1/environment/season-build",
      {method:"POST",payload:{game_build,target_ilevel,native_G_binary,
                              consumable_native_binary,
                              auto_initial_core_build,auto_initial_core_simc_binary,
                              auto_native_F_requested,auto_native_O_requested,
                              auto_select_observed_F_no_oil,
                              selected_flask_item_id,
                              selected_oil_item_ids_by_hand,
                              existing_special_gem_id,source_target_socket_count,
                              refresh_reason,
                              simc_revision_hint:revision||null}});
    stopSeasonActivity();
    lastSeasonDiagnosticReceipt=compactSeasonBuildReceipt(report,forUserVariant);
    $("season-diagnostic-copy-btn").disabled=false;
    showSeasonEnvironmentBuild(report,forUserVariant);
    if(forUserVariant) $("user-variant-status").textContent=(
      report.web_environment_scope?.environment_ready===true?
        "선택 구성의 J/F/O와 G/B/T 검증 설치 완료 · 최적화 단계에서도 같은 구성·SHA를 재확인합니다.":
        "선택 구성 검증 보류 · 시즌 원본 또는 품목·보석의 근거가 부족합니다. 이전 예산을 대신 사용하지 않습니다.");
    const localization=report.official_ko_localization;
    const localized=$("season-locale-status");
    if(localization?.status==="VERIFIED_OFFICIAL_NAMES_COMPLETE") {
      localized.textContent="현재 검증된 선택 목록의 한국어 명칭 "+
        localization.verified_names+"종 확인 완료 · 기존 이름 재사용 "+
        localization.existing_same_build_name_records_reused+"종";
    }else if(localization) {
      localized.textContent="한국어 이름 구축: "+
        (localization.verified_names||0)+"종 확인 · "+
        (localization.pending_names||0)+"종 확인 보류 · "+
        "미확정 명칭은 원본 이름을 표시합니다.";
    }
    if(report.web_environment_scope?.game_build) {
      try {await refreshOfficialGameTerms(report.web_environment_scope.game_build);}
      catch(error){$("season-terms-status").textContent=
        "공식 한국어 게임 용어 조회 오류 · 기존 표기 유지";}
    }
    // A verified new installation may supply a different season rune roster.
    // Refresh read-only options only, never launch optimization on Build.
    try{renderSeasonOptionCatalog(await api("/api/v1/season-option-catalog"));}
    catch(error){$("dk-runeforge-status").textContent=
      "시즌 룬 원본 조회 실패 · 선택 잠금";}
    try{await refreshInstalledOilLoadouts();}
    catch(error){$("optimizer-oil-loadout-status").textContent=
      "검증 설치 기름 목록 조회 실패 · 고급 입력 유지";}
    setNotice("시즌 환경 구축 단계 조회 완료 · READY 여부는 별도 검증 · 개별 DPS 최적화는 시작되지 않았습니다.");
  }catch(err){
    // A failed HTTP response supplies no trusted source/owner report.
    const safeError=/^[A-Z][A-Z0-9_]{0,119}$/.test(err.message)?
      err.message:"REQUEST_ERROR_NOT_EXPORTED";
    lastSeasonDiagnosticReceipt=JSON.stringify({
      schema:"v384_user_copied_season_build_diagnostic_v1",
      evidence_only_no_ready_authority:true,
      for_user_variant:forUserVariant,
      outcome:"REQUEST_FAILED_NO_SOURCE_REPORT",
      game_build,target_ilevel,error_code:safeError,
      compiler_missing:null,core_numeric_owner_present:null,
      environment_ready:false,
      note:"Request failed before usable source evidence; missing is not zero."
    },null,2);
    $("season-diagnostic-copy-btn").disabled=false;
    $("season-build-summary").textContent="요청 차단 또는 오류 · 실행 완료가 아닙니다. 오류 코드를 확인하세요.";
    $("season-build-stage").textContent="시즌 환경 구축 단계 차단/오류 · "+err.message+
      " · 기존 영수증은 보존됩니다.";
    throw err;
  } finally {
    stopSeasonActivity();
  }
}
function showEnvironmentBuild(build) {
  const node=$("environment-build-status");
  if(!node)return;
  if(!build) {
    node.textContent="환경 구축 전 · 설치된 시즌 데이터는 예산 확인을 누르면 검사합니다.";
    return;
  }
  const labels={
    "READY":"준비 완료",
    "READY_WITH_LIMITATIONS":"제한 사항 포함 준비 완료",
    "BLOCKED":"차단"
  };
  const change=build.dependency_change||{};
  const reused=Array.isArray(change.reused_components)?change.reused_components.length:0;
  const rebuilt=Array.isArray(change.rebuilt_components)?change.rebuilt_components.length:0;
  const changed=Array.isArray(change.changed_inputs)?change.changed_inputs.length:0;
  const hits=Number(build.cache_reuse?.installed_v213_artifact_hits)||0;
  const audit=build.readiness?.source_join_audit;
  const joinLabels={
    "gear_inventory_slot":"일반 장비 부위",
    "permanent_enchant_slot":"무기 마부 손·부위",
    "embellishment_effect_item_slot":"장식 아이템·부위",
    "temporary_enchant_weapon_hand":"임시 마부 무기 손",
    "gem_property_item":"보석 아이템 ID"
  };
  const pendingSource=(
    audit?.schema==="v213_source_join_audit_v1" && audit.families
  )?Object.entries(audit.families)
    .filter(([,entry])=>Number(entry.pending_rows)>0)
    .map(([key,entry])=>(joinLabels[key]||key)+" "+entry.pending_rows)
    .join(" · "):null;
  const joinText=pendingSource===null?
    " · DB Join Audit 없음(구형 카탈로그)":
    pendingSource?" · DB 연결 근거 보류(소스 행) "+pendingSource:
    " · DB 연결 근거 미해결 없음(조사 범위 한정)";
  const coverage=build.readiness?.profile_plan_suppliers;
  const coverageText=coverage?
    " · 계획 공급원 "+coverage.count+"/"+coverage.total+
    (coverage.adaptive_native_evidence_complete?"":" (adaptive Native 미완료)"):"";
  node.textContent="환경 구축 "+(labels[build.status]||build.status)+
    " · 재사용 "+reused+" · 재구축 "+rebuilt+
    " · 변경 입력 "+changed+" · v213 artifact 재사용 "+hits+
    coverageText+joinText+" · Native 0 · Network 0";
}
function showPlan(plan) {
  if(!plan?.plan) return;
  const o=Object.values(plan.plan.fixed_O).reduce((a,n)=>a+n,0);
  const environment=plan.environment_manifest;
  showEnvironmentBuild(plan.environment_build);
  const coverage=environment?.profile_supplier_coverage;
  const supplierText=coverage?
    " · 프로필 공급원 "+coverage.current_season_profile_supplier_count+
    "/"+coverage.contract_count+" (계획 경로; 전체 적응형 Native 미검증)":
    "";
  const environmentText=environment?
    " · 환경 "+environment.status+
    " · 미해결 "+(environment.unresolved_dependencies||[]).length+
    supplierText:
    "";
  if(!$("manual-t-mode").checked) {
    $("budget-preview-total").textContent=number(plan.plan.final_T)+" rating · 검증된 계획";
    $("budget-preview-note").textContent="선택한 조건의 서버 계획 결과입니다. 입력 변경 시 다시 확인해야 합니다.";
  }
  setNotice("계산 준비 확인 · B "+number(plan.plan.base_B)+
    " + 고정 기름 O "+number(o)+" = 최종 T "+number(plan.plan.final_T)+
    " · 계획 Native 최대 "+plan.plan.native_limit+"회 (지금 실행 0회)"+
    (plan.plan.current_season_product?" · 새 시즌 대표장비 별도 세션":"")+
    (plan.static_cache_auto_used?" · 저장된 정적 캐시 자동 적용":"")+
    environmentText);
}
function renderProgress(data) {
  state.longrunEnabled=Boolean(data?.enabled);
  state.longrunResultReady=Boolean(data?.enabled && data?.result_ready);
  const p=data?.progress||{};
  // A resumed v291 run may leave its previous V291_RESULT.json in place.
  // Do not present that older observation as the active run's final result.
  if(data?.active || !data?.result_ready) {
    $("filled-result").hidden=true;
    $("empty-result").hidden=false;
  }
  const n=Number(p.completed_jobs)||0,limit=Number(p.planned_jobs)||6;
  const pct=Number(p.progress_percent)||0;
  $("progress-label").textContent="평가 "+n+"회 · 최대 "+limit+"회";
  $("progress-pct").textContent=number(pct,0)+"%";
  $("progress-bar").style.width=Math.max(0,Math.min(100,pct))+"%";
  const worker=p.worker?.status||p.status||"NOT_STARTED";
  // A failed resumed worker may stop before v094 overwrites old progress.
  // Show its NEW reason, rather than repeating an older Native error forever.
  const cancelled=!data.active && (worker==="CANCELLED_PARTIAL"||
                                      worker==="PAUSED_USER_CANCEL");
  // A sealed budget that reached the user-selected ceiling cannot advance.
  const finished=!data.active && state.longrunEnabled &&
    worker==="BUDGET_EXHAUSTED" && data.result_ready===true;
  const paused=!data.active && state.longrunEnabled &&
    (worker==="PAUSED_ELAPSED_BUDGET"||
     worker==="PAUSED_INVOCATION_NATIVE_BUDGET");
  state.longrunCompleted=Boolean(finished);
  // After an interrupted Windows server/worker lifetime, the sealed worker
  // file can still say RUNNING or QUEUED while no OS worker is active.
  // Its stored N56 session remains resumable; never label it as idle.
  const interrupted=!data.active && state.longrunEnabled &&
    (worker==="RUNNING"||worker==="QUEUED");
  const status=data.active?worker:
    cancelled?"사용자 요청으로 중단 · 완료한 후보 보존 · 같은 세션 재개 가능":
    worker==="BLOCKED_OR_PARTIAL"?
      (p.worker?.reason||p.error||worker):
      (p.error||p.worker?.reason||worker);
  const environment=data?.environment_manifest;
  const environmentText=environment?" · 환경 "+environment.status:"";
  showEnvironmentBuild(data?.environment_build);
  $("stage-text").textContent=data.active?"SimC에서 후보를 평가 중입니다. 현재 "+n+"회 완료 / 세션 상한 "+limit+"회 · 확정된 관측만 결과에 표시합니다.":
    interrupted?"작업자가 실행 중이지 않습니다 · 저장된 세션을 재개할 수 있습니다":
    ({BUDGET_EXHAUSTED:"탐색 완료",PAUSED_USER_CANCEL:"중단됨 · 재개 가능",PAUSED_ELAPSED_BUDGET:"시간 제한 도달 · 재개 가능",PAUSED_INVOCATION_NATIVE_BUDGET:"중단된 계산 · 재개 가능",NOT_STARTED:"계산 대기"})[worker]||status;
  $("run-label").textContent=data.active?"진행 중":
    finished?"탐색 상한 완료 · 결과 저장":
    cancelled?"취소됨 · 재개 가능":
    paused?"회차 중단 · 재개 가능":
    interrupted?"실행 중단 · 재개 가능":
    worker==="BLOCKED_OR_PARTIAL"?"실행 차단":
    state.longrunEnabled&&data.result_ready?"관측 결과 저장 · 재개 가능":
    data.result_ready&&worker.startsWith("PASS")?"완료":
    data.cancel_requested?"취소 요청":"대기";
  buttonState(Boolean(data.active),Boolean(data.result_ready));
}
function renderResult(payload) {
  const r=payload.user_result;
  const warning=$("result-panel").querySelector(".result-warning");
  if(warning) warning.textContent=r.selected_pair_95_only
    ?"관측 1순위 · 선택된 확인 쌍만 95% 근사 비교 (다중선택 보정 없음)"
    :"관측 1순위 · 전역 최적해 입증 아님";
  if(r.confidence_level!==0.95||r.global_optimum_proven!==false)
    throw Error("ONLY_95_RESULT_ALLOWED");
  const best=r.observed_first_choice;
  const total=r.final_T;
  $("dps").textContent=number(best.observed_dps_mean,1);
  $("sem").textContent=number(best.simc_sem,2);
  const oil=Object.values(r.fixed_O).reduce((a,x)=>a+x,0);
  if(!$("manual-t-mode").checked) {
    $("budget-preview-total").textContent=number(total)+" rating · 검증된 세션";
    $("budget-preview-note").textContent="현재 표시된 값은 이 세션의 확정된 T입니다. 입력을 변경하면 재검증해야 합니다.";
  }
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
  // Reuse the result adapter's existing observations; never infer new
  // candidates, confidence decisions, or approximate DPS in the browser.
  const alts=r.material_near_alternatives||[];
  $("alt-count").textContent=alts.length+"개 / 관측 "+number(r.observed_unique_candidates)+"분배";
  const list=$("alt-list");list.replaceChildren();
  if(!alts.length) {
    const row=document.createElement("div");row.className="alt-row";
    row.textContent="관측된 분배 중 조건에 맞는 근접 대안이 없습니다. 미탐색 분배의 성능은 알 수 없습니다.";
    list.appendChild(row);
  }
  for(const [index,alt] of alts.entries()) {
    const row=document.createElement("article");row.className="alt-row";
    const pairLabel=alt.pairwise_95_label==="OBSERVED_NEAR_BUT_LOWER_AT_95"
      ?"95% 기준 낮음":alt.pairwise_95_label==="OBSERVED_NEAR_UNRESOLVED_AT_95"
      ?"95% 우열 미확정":"95% 비교 미확인";
    const head=document.createElement("div");head.className="alt-row-head";
    const title=document.createElement("strong");
    title.textContent="관측 근접 대안 "+(index+1);
    const verdict=document.createElement("span");verdict.textContent=pairLabel;
    verdict.className="alt-verdict";head.append(title,verdict);
    const metrics=document.createElement("div");metrics.className="alt-row-metrics";
    for(const [label,value] of [
      ["DPS",number(alt.observed_dps_mean,1)],
      ["SEM","±"+number(alt.simc_sem,2)],
      ["관측 DPS 차이",number(alt.observed_dps_loss_pct,3)+"%"],
      ["분배 이동",number(100*alt.rating_moved_fraction_B,1)+"%"]]){
      const kv=document.createElement("div");kv.className="alt-metric";
      const k=document.createElement("span");k.textContent=label;
      const v=document.createElement("strong");v.textContent=value;
      kv.append(k,v);metrics.appendChild(kv);
    }
    const stats=document.createElement("p");stats.className="alt-stat-summary";
    stats.textContent=statOrder.map(([key,label])=>label+" "+
      number(alt.absolute_rating_T[key])+" ("+
      number(alt.percent_of_final_T[key],2)+"%)").join(" · ");
    row.append(head,metrics,stats);
    list.appendChild(row);
  }
  $("empty-result").hidden=true;$("filled-result").hidden=false;
}
async function readSession(id) {
  // GET only: no SimC Native, no session file writes.
  const longrun=await api("/api/v1/sessions/"+id+"/longrun/status");
  if(longrun.enabled===true){
    const result=longrun.result_ready&&!longrun.active
      ? await api("/api/v1/sessions/"+id+"/longrun/result") : null;
    return {progress:longrun,result,longrun:true};
  }
  const progress=await api("/api/v1/sessions/"+id+"/status");
  const worker=progress.progress?.worker?.status||progress.progress?.status||"";
  const result=progress.result_ready && !progress.active && worker.startsWith("PASS")
    ? await api("/api/v1/sessions/"+id+"/result") : null;
  return {progress,result};
}
async function pollOnce() {
  if(!state.session)return;
  const id=state.session;
  const snapshot=await readSession(id);
  if(id!==state.session)return;
  renderProgress(snapshot.progress);
  if(snapshot.result)renderResult(snapshot.result);
}
function handlePollFailure(err,id) {
  if(id!==state.session)return;
  if(err.message==="SESSION_NOT_FOUND") {
    // A remembered ID from another PC is not evidence of a local session.
    state.session="";
    $("session-id").textContent="없음";
    $("run-label").textContent="기록 없음";
    $("progress-label").textContent="평가 기록 없음";
    $("progress-pct").textContent="–";
    $("progress-bar").style.width="0%";
    $("stage-text").textContent="현재 PC에 세션 파일이 없습니다.";
    $("filled-result").hidden=true;$("empty-result").hidden=false;
    refreshResultNavigation();
    try{localStorage.removeItem("simc_secondary_session_id");}catch{}
    buttonState(false,false);
    setNotice("현재 PC에 해당 세션이 없습니다. 다른 컴퓨터에서 만든 세션일 수 있습니다.",true);
    return; // Stop polling this missing ID.
  }
  state.pollFailures=Math.min(state.pollFailures+1,5);
  state.nextPollAt=Date.now()+Math.min(30000,1400*Math.pow(2,state.pollFailures));
  setNotice("로컬 서버 상태 조회 오류 · 연결을 확인하는 동안 재시도 간격을 늘립니다.",true);
}
function beginPolling() {
  if(state.pollTimer!==null)clearInterval(state.pollTimer);
  state.pollTimer=setInterval(()=>{
    if(state.busy||state.pollBusy||!state.session||Date.now()<state.nextPollAt)return;
    state.pollBusy=true;
    const id=state.session;
    pollOnce().then(()=>{
      if(id===state.session){state.pollFailures=0;state.nextPollAt=0;}
    }).catch(err=>handlePollFailure(err,id)).finally(()=>{state.pollBusy=false;});
  },1400);
}
async function loadRecentSessions() {
  // Existing local v106 sessions only, never a remote or GitHub search.
  // GET is read-only: no Native, user input contents or executable hashing.
  const selected=$("recent-session-id").value;
  const data=await api("/api/v1/sessions");
  if(data.read_only!==true||data.native_calls_now!==0||
     !Array.isArray(data.sessions))throw Error("SESSION_LIST_READ_ONLY_CONTRACT");
  const list=$("recent-session-id");
  list.replaceChildren(option("","이 PC의 저장된 세션 선택"));
  for(const item of data.sessions) {
    if(typeof item.session_id!=="string"||
       !/^[a-f0-9]{20}$/.test(item.session_id))continue;
    const label=(specLabels[item.class+"/"+item.spec]||
      item.class+" · "+item.spec).split(" (")[0];
    const status=item.result_saved?"결과 저장":item.recorded_status;
    const stamp=Number.isFinite(item.updated_unix)?
      new Date(item.updated_unix*1000).toLocaleString("ko-KR"):"";
    list.appendChild(option(item.session_id,
      label+" · 목표 "+item.target_ilevel+" · "+status+" · "+stamp));
  }
  if(Array.from(list.options).some(x=>x.value===selected))list.value=selected;
  $("recent-open-btn").disabled=!list.value;
  $("recent-session-note").textContent=
    "현재 PC의 기록 "+(list.options.length-1)+"개 · Native 0회 · "+
    "특성·장비·로컬 경로는 목록에 포함되지 않음";
}
async function restore(id) {
  if(!/^[a-f0-9]{20}$/.test(id))
    throw Error("세션 ID는 20자리 해시여야 합니다.");
  // Check existence, result and stored inputs BEFORE marking success.
  const [snapshot,inputs]=await Promise.all([
    readSession(id),api("/api/v1/sessions/"+id+"/inputs")
  ]);
  fillSessionInputs(inputs);
  markSession(id);
  // The local dropdown scope follows the restored sealed build; avoid
  // showing loadouts from a previous page selection.
  try{await refreshInstalledOilLoadouts();}
  catch(error){$("optimizer-oil-loadout-status").textContent=
    "검증 설치 기름 목록 조회 실패 · 복원한 세션은 그대로 유지";}
  state.pollFailures=0;state.nextPollAt=0;
  $("filled-result").hidden=true;$("empty-result").hidden=false;
  renderProgress(snapshot.progress);
  if(snapshot.result)renderResult(snapshot.result);
  setNotice("기존 세션·입력 복원 성공 · "+id+" · 새 Native 계산 0회");
}
function renderSeasonOptionCatalog(catalog) {
  const runeSource=catalog?.verified_weapon_enhancements?.dk_runeforges;
  const runes=(runeSource?.status==="PINNED_DK_RUNES_INSTALLED" &&
       Array.isArray(runeSource.items))?runeSource.items:[];
  state.dkRuneIds=new Set();
  for(const name of ["dk_rune_main","dk_rune_off"]) {
    const node=$(name);
    node.replaceChildren(option("","사용자 선택 없음 (기존 SimC 입력)"));
    for(const row of runes) {
      if(!Number.isSafeInteger(row.enchant_id)||row.enchant_id<=0||
         row.class!=="deathknight"||
         !Array.isArray(row.weapon_hands)||
         !row.weapon_hands.includes(name==="dk_rune_main"?"main_hand":"off_hand"))
        continue;
      state.dkRuneIds.add(row.enchant_id);
      node.appendChild(option(row.enchant_id,
        row.display_name+" · #"+row.enchant_id));
    }
  }
  $("dk-runeforge-status").textContent=state.dkRuneIds.size?
    "현재 시즌 SimC 원본 검증 룬 "+state.dkRuneIds.size+"종 선택 가능":
    "이번 시즌 검증된 룬 원본이 설치되지 않아 신규 선택 잠금";
  runeCompatibility();
  const status=$("season-option-catalog-status");
  const host=$("season-enchant-groups");
  const selector=$("season_enchant_finger1");
  state.eagleApproved=false;
  selector.replaceChildren(option("","마법부여 없음 (기존 설정)"));
  selector.disabled=true;
  host.replaceChildren();
  if(catalog?.schema!=="v196_current_season_ui_catalog_v1" ||
     catalog?.status!=="SOURCE_COMBINED_WITH_CLEAR_APPROVAL_BOUNDARY") {
    status.textContent="이번 시즌 마법부여 출처 자료가 준비되지 않았습니다. 기존 승인 선택은 그대로 유지됩니다.";
    return;
  }
  const enchants=catalog.enchant_candidates||{};
  const selectable=(enchants.items||[]).filter(x=>x.ui_selectable===true);
  if(enchants.total!==(enchants.items||[]).length ||
     selectable.length!==enchants.selectable_count ||
     selectable.length>1 ||
     selectable.some(x=>x.enchant_id!==7967 ||
       x.effect_family!=="crit_effectiveness" ||
       x.static_CHMV_budget_impact!=="NO_INCREMENT_FROM_NONCHMV_EFFECT")) {
    status.textContent="마법부여 선택 승인 상태가 일치하지 않아 목록을 차단했습니다.";
    return;
  }
  state.eagleApproved=selectable.length===1;
  if(state.eagleApproved) {
    selector.appendChild(option("7967","독수리의 눈 · 치명타 효과 증가 (CHMV 변동 없음)"));
    selector.disabled=false;
  }
  const raw=catalog.related_source_counts||{};
  status.textContent="게임 빌드 "+catalog.season_build+
    " · SimC "+catalog.simc_revision.slice(0,10)+
    " · 일반장비 후보 "+(raw.gear_item_candidates??"?")+
    " · 티어 ID "+(raw.tier_piece_ids??"?")+
    " · 음식 원시 후보 "+(raw.food_raw_item_candidates??"?")+
    " · 물약 원시 후보 "+(raw.potion_raw_item_candidates??"?")+
    " · SimC 장식/다크문 효과 등록 "+(raw.embellishment_darkmoon_registrations??"?")+
    " · 보석 속성 기록 "+(raw.gem_property_records??"?")+
    " · 최고 품질 마부 후보 "+enchants.total+
    "개 (독수리의 눈 "+(state.eagleApproved?"1종 선택 가능":"미검증 잠금")+
    " · 나머지 마부는 잠금)"+
    (catalog.one_enchant_native_evidence_status==="EXACT_SCOPE_OBSERVED_READ_ONLY"?
      " · 조건부 마부 Native 증거 1건 관측":
      " · 조건부 마부 Native 증거 확인 불가, 수치 표시 생략");
  const names={boots:"장화",chest:"가슴",helm:"머리",ring:"반지",
               shoulders:"어깨",weapon:"무기"};
  for(const kind of ["helm","shoulders","chest","boots","ring","weapon"]) {
    const rows=enchants.items.filter(x=>x.kind===kind);
    if(!rows.length)continue;
    const detail=document.createElement("details");
    detail.className="catalog-source-group";
    const head=document.createElement("summary");
    head.textContent=(names[kind]||kind)+" · "+rows.length+
      "종 · 가장 높은 등록 품질 · 선택 기능 준비 중";
    detail.appendChild(head);
    const list=document.createElement("ul");
    for(const entry of rows) {
      const li=document.createElement("li");
      const kind=entry.preferred_if_same_effect_source;
      const qualifier=kind==="STRONGER_VARIANT_REPORTED"?
        " · 동일 효과 상위형 후보":
        kind==="WEAKER_VARIANT_REPORTED"?
        " · 같은 효과의 더 강한 후보 존재":
        kind==="DISTINCT_EFFECT_NO_DOMINANCE"?
        " · 별개의 효과이므로 유지":"";
      const proof=entry.measured_E_in_one_simc_native_scope;
      const observed=proof?
        " · Native 관측: 가속 +"+proof.haste_rating+
        " (냉법 334·Linux SimC 한정, gear_* 중복 가산 없음)":"";
      li.textContent=(entry.display_name||entry.token)+
        " · "+(entry.effect_description||"효과 원본 연결 필요")+
        qualifier+" · enchant ID "+entry.enchant_id+
        " · 최고 관측 등급 "+entry.highest_source_quality_rank+
        observed+(entry.ui_selectable?" · 사용자 선택 가능 (고정 CHMV B/T 불변)":
                  " · 사용자 선택은 아직 비활성");
      list.appendChild(li);
    }
    detail.appendChild(list);
    host.appendChild(detail);
  }
}
function installOptions(options) {
  state.options=options;
  const label=(key,value)=>options.display_labels?.[key]?.[String(value)]??
    String(value);
  // /options also contains source-known historical v108 tokens for saved
  // sessions; the actual product always uses current_season_product=true.
  // Render ONLY its explicit approved subset. A missing/malformed subset
  // fails closed to a no-optional-effect source_default (SimC disabled).
  const approved=options.current_season_product_choices;
  for(const name of ["food","potion","augmentation"]) {
    const offered=options[name]||[];
    const permitted=approved?.schema==="v113_current_season_optional_consumables_v1" &&
      approved?.source_default_simc_token==="disabled" &&
      Array.isArray(approved[name])&&approved[name].includes("source_default") &&
      approved[name].every(token=>offered.includes(token)) ?
      approved[name]:["source_default"];
    populateSelect(name,permitted,v=>v==="source_default"?
      "미사용 (이번 시즌 기본)":label(name,v));
  }
  // Preserve historical catalogues in /options, but never advertise a
  // diamond or season module selection that v218 cannot admit at runtime.
  const seasonScope=approved?.schema==="v113_current_season_optional_consumables_v1";
  const diamonds=seasonScope && Array.isArray(approved.diamond_id) &&
    approved.diamond_id.includes(0) &&
    approved.diamond_id.every(id=>(options.diamond_id||[]).includes(id)) ?
    approved.diamond_id:[0];
  populateSelect("diamond",diamonds,v=>v===0?
    "선택 없음 (이번 시즌 기본)":label("diamond_id",v));
  const omnium=seasonScope && Array.isArray(approved.omnium_talents) &&
    approved.omnium_talents.includes("source_default") &&
    approved.omnium_talents.every(token=>(options.omnium_talents||[]).includes(token)) ?
    approved.omnium_talents:["source_default"];
  populateSelect("omnium",omnium,v=>({
     source_default:"전문화 기본값 유지 (추가 선택 미검증)",
     row4_crit:"치명",row4_haste:"가속",
     row4_mastery:"특화",row4_vers:"유연"
  })[v]||label("omnium_talents",v));
  refreshDefaultConsumableSummaries();
  for(const row of $("crafted-rows").querySelectorAll(".gear-row")){
    const selector=row.querySelector('[data-field="embellishment"]');
    selector.replaceChildren(option("","장식 종류 선택"));
    for(const [token,details] of Object.entries(options.embellishments||{}))
      selector.appendChild(option(token,details.name+" · "+details.effect));
    syncCraftRow(row);
  }
}

// Settings: user-triggered official SimC download, separate from season DB.
// The existing manually supplied binary remains usable and is never overwritten.
let simcOffer=null;
let manualSimcBeforeUpdate=null;
function rememberPreManagedBinary() {
  if(manualSimcBeforeUpdate||!field("binary"))return;
  manualSimcBeforeUpdate={binary:field("binary"),revision:field("revision")};
  try{localStorage.setItem("simc_secondary_manual_simc_before_update",
                           JSON.stringify(manualSimcBeforeUpdate));}catch{}
}
function savedPreManagedBinary() {
  if(manualSimcBeforeUpdate)return manualSimcBeforeUpdate;
  try{
    const parsed=JSON.parse(localStorage.getItem("simc_secondary_manual_simc_before_update"));
    if(parsed&&typeof parsed.binary==="string"&&typeof parsed.revision==="string"
       &&parsed.binary.length<=4096&&/^[a-f0-9]{7,40}$/i.test(parsed.revision))
      return parsed;
  }catch{}
  return null;
}
function applyManagedSimc(data) {
  if(!data?.active_binary||!data?.installed)return false;
  $("binary").value=data.active_binary;
  $("revision").value=data.installed.revision_short;
  return true;
}
function displaySimcUpdater(data) {
  const supported=Boolean(data.windows_supported);
  $("simc-check-btn").disabled=!supported;
  $("simc-rollback-btn").disabled=!supported||!data.installed;
  const current=data.installed;
  $("simc-update-status").textContent=!supported?
    "SimC 업데이트 관리는 Windows x64에서 지원합니다. 직접 지정한 경로는 유지됩니다.":
    current?"관리 중: "+current.filename+" · "+current.revision_short+
      " · SHA256 "+current.sha256.slice(0,16)+"…":
    "앱 관리 SimC 없음 · 직접 지정한 실행 파일은 변경하지 않습니다.";
  if(supported&&!data.archive_extractor_available)
    $("simc-update-status").textContent+=" · 설치하려면 7-Zip이 필요합니다.";
}
async function refreshSimcUpdater(preferManaged=false) {
  const status=await api("/api/v1/simc-updates/status");
  displaySimcUpdater(status);
  if(status.active_binary&&(preferManaged||!field("binary")))applyManagedSimc(status);
  return status;
}
async function checkSimcUpdater() {
  simcOffer=null;
  $("simc-install-btn").disabled=true;
  const result=await api("/api/v1/simc-updates/check",
     {method:"POST",payload:{}});
  simcOffer=result.candidate?.filename||null;
  const line=$("simc-update-candidate");
  if(simcOffer) {
    line.textContent="공식 Windows x64 후보: "+simcOffer+
      " · revision "+result.candidate.revision_short+
      (result.archive_extractor_available?"":" · 설치에는 7-Zip 필요");
  }else{
    const reasons={
      OFFICIAL_NIGHTLY_TLS_CERTIFICATE_INVALID:"공식 nightly 다운로드 서버의 HTTPS 인증서를 검증할 수 없습니다.",
      OFFICIAL_NIGHTLY_CONNECTION_TIMEOUT:"공식 nightly 다운로드 서버 연결 시간이 초과됐습니다.",
      OFFICIAL_NIGHTLY_CONNECTION_UNAVAILABLE:"공식 nightly 다운로드 서버에 연결할 수 없습니다.",
      NO_OFFICIAL_WIN64_NIGHTLY_FOUND:"공식 nightly 목록에서 Windows x64 패키지를 찾지 못했습니다."
    };
    line.replaceChildren(document.createTextNode(
      (reasons[result.official_index_problem]||
        "공식 nightly 직접 조회에 실패했습니다 ("+
        (result.official_index_problem||"원인 미상")+").")+
      " 인증서 검증을 우회하지 않습니다. "));
    const alt=result.github_alternative;
    if(alt?.source==="OFFICIAL_SIMC_GITHUB_ACTIONS"&&
       /^https:\/\/github\.com\/simulationcraft\/simc-publish\/actions\/runs\/\d+\/artifacts\/\d+$/.test(alt.artifact_zip_url)){
      const link=document.createElement("a");
      link.href=alt.artifact_zip_url;
      link.target="_blank";link.rel="noopener noreferrer";
      link.textContent="SimC 공식 GitHub Windows nightly 받기";
      line.appendChild(link);
      line.appendChild(document.createTextNode(
        " · GitHub 로그인이 필요할 수 있습니다. 받은 artifact ZIP에서 .7z를 꺼낸 뒤 아래 '내 PC의 .7z 파일 설치'를 사용하세요."));
    }else{
      const link=document.createElement("a");
      link.href="https://github.com/simulationcraft/simc-publish/actions";
      link.target="_blank";link.rel="noopener noreferrer";
      link.textContent="공식 GitHub nightly 기록 열기";
      line.appendChild(link);
      line.appendChild(document.createTextNode(
        " · Windows x64 artifact에서 .7z를 찾아 아래에서 설치하세요."));
    }
  }
  $("simc-install-btn").disabled=!simcOffer||!result.archive_extractor_available;
}
async function installSimcUpdater() {
  if(!simcOffer)throw Error("먼저 공식 업데이트를 확인해 주세요.");
  if(!window.confirm("공식 SimulationCraft Windows x64 패키지를 다운로드하고 앱 전용 폴더에 설치할까요? 기존 실행 파일과 세션은 변경하지 않습니다."))return;
  rememberPreManagedBinary();
  const candidate=simcOffer;
  $("simc-install-btn").disabled=true;
  try{
    const result=await api("/api/v1/simc-updates/install",
       {method:"POST",payload:{filename:candidate}});
    simcOffer=null;
    displaySimcUpdater(result);
    applyManagedSimc(result);
    $("simc-update-candidate").textContent="설치 완료 · 신규 최적화에만 새 SimC가 적용됩니다. 시즌 DB와 과거 캐시는 그대로입니다.";
    setNotice("SimC 설치 완료 · 바이너리 SHA에 따라 새 최적화 세션이 분리됩니다.");
  }catch(err){
    $("simc-install-btn").disabled=false;
    throw err;
  }
}
async function installLocalSimcUpdater() {
  const path=field("simc-local-archive");
  if(!path.toLowerCase().endsWith(".7z"))
    throw Error("공식 Windows x64 SimC .7z 파일의 로컬 경로를 입력해 주세요.");
  if(!window.confirm("이 PC의 파일을 SimC 관리 폴더에 설치할까요? 사용자가 직접 내려받은 파일은 공식 서명을 독립 확인할 수 없습니다."))return;
  rememberPreManagedBinary();
  const result=await api("/api/v1/simc-updates/install-local",
    {method:"POST",payload:{archive_path:path}});
  displaySimcUpdater(result);
  applyManagedSimc(result);
  simcOffer=null;$("simc-install-btn").disabled=true;
  $("simc-update-candidate").textContent="로컬 파일 설치 완료. 출처는 독립 인증되지 않았으며 기존 사용자 실행 파일과 세션은 유지됩니다.";
  setNotice("로컬 SimC 설치 완료 · 신규 계산은 다른 바이너리 SHA의 세션으로 분리됩니다.");
}
async function rollbackSimcUpdater() {
  if(!window.confirm("관리 중인 SimC를 이전 버전으로 되돌릴까요? 기존 사용자 파일은 변경하지 않습니다."))return;
  const result=await api("/api/v1/simc-updates/rollback",
       {method:"POST",payload:{}});
  displaySimcUpdater(result);
  if(result.active_binary)applyManagedSimc(result);
  else if(savedPreManagedBinary()) {
    const previous=savedPreManagedBinary();
    $("binary").value=previous.binary;
    $("revision").value=previous.revision;
  }else {
    $("binary").value="";$("revision").value="";
  }
  $("simc-update-candidate").textContent="복원 완료. 기존 세션과 계산 결과는 그대로 보존됩니다.";
  setNotice("SimC 관리 버전 복원 완료 · 사용자 원본 설치는 유지됩니다.");
}
function registerHandlers() {
  $("optimizer-oil-enabled").addEventListener("change",()=>withBusy(applyOilUseToggle));
  $("equipment-trinket-search").addEventListener("input",drawInlineEquipment);
  $("equipment-special-search").addEventListener("input",drawInlineEquipment);
  for(const launch of document.querySelectorAll("[data-equip-select]"))
    launch.addEventListener("click",()=>openEquipmentPicker(
      $(launch.dataset.equipSelect),launch));
  $("equipment-dialog-close").addEventListener("click",closeEquipmentDialog);
  $("equipment-dialog-clear").addEventListener("click",()=>{
    if(!equipmentDialogTarget)return;
    equipmentDialogTarget.value="";
    equipmentDialogTarget.dispatchEvent(new Event("change",{bubbles:true}));
    refreshEquipmentSelectionUI();updateBudgetPreview();
    closeEquipmentDialog();
  });
  $("equipment-search").addEventListener("input",()=>renderEquipmentGallery(field("equipment-search")));
  $("equipment-dialog").addEventListener("close",()=>{
    equipmentDialogTarget=null;equipmentDialogOpener=null;
  });
  for(const id of ["trinket1","trinket2"])
    $(id).addEventListener("change",()=>{
      refreshEquipmentSelectionUI();
      buttonState(state.running,state.longrunResultReady);
    });
  for(const button of document.querySelectorAll("[data-view]"))
    button.addEventListener("click",()=>switchView(button.dataset.view));
  $("manual-t-mode").addEventListener("change",updateManualTMode);
  $("final_T").addEventListener("input",updateBudgetPreview);
  // A verified T is scoped to the exact user choices. Any CHMV ownership
  // change invalidates its visual preview, never just the backend cache key.
  for(const id of ["ilevel","season-target-socket-count","season-existing-special-gem-id",
    "season-selected-flask-id","season-verified-flask","optimizer-oil-loadout",
    "optimizer-oil-main-id","optimizer-oil-off-id","oil_main","oil_off",
    "spec","trinket1","trinket2","season_enchant_finger1",
    "diamond","omnium"])
    $(id).addEventListener("change",updateBudgetPreview);
  for(const group of ["special-rows","crafted-rows"])
    $(group).addEventListener("change",updateBudgetPreview);

  $("simc-check-btn").addEventListener("click",()=>withBusy(checkSimcUpdater));
  $("simc-install-btn").addEventListener("click",()=>withBusy(installSimcUpdater));
  $("simc-install-local-btn").addEventListener("click",()=>withBusy(installLocalSimcUpdater));
  $("simc-rollback-btn").addEventListener("click",()=>withBusy(rollbackSimcUpdater));
  $("simc-import-btn").addEventListener("click",()=>withBusy(importSimcCharacter));
  $("season-build-btn").addEventListener("click",()=>withBusy(()=>buildSeasonEnvironment(false)));
  $("season-diagnostic-copy-btn").addEventListener("click",copySeasonBuildDiagnostic);
  $("user-variant-prepare-btn").addEventListener("click",()=>withBusy(()=>buildSeasonEnvironment(true)));
  $("season-target-socket-count").addEventListener("input",updateSeasonSocketBreakdown);
  $("season-existing-special-gem-id").addEventListener("input",updateSeasonSocketBreakdown);
  updateSeasonSocketBreakdown();
  $("source-credentials-save-btn").addEventListener("click",()=>withBusy(saveSourceCredentials));
  $("source-credentials-clear-btn").addEventListener("click",()=>withBusy(clearSourceCredentials));
  $("season-verified-flask").addEventListener("change",chooseInstalledFlask);
  $("potion").addEventListener("change",refreshDefaultConsumableSummaries);
  $("season-selected-flask-id").addEventListener("input",()=>{
    $("season-verified-flask").value="";
    refreshDefaultConsumableSummaries();
  });
  $("optimizer-oil-loadout").addEventListener("change",chooseInstalledOilLoadout);
  for(const [check,id] of [["oil_main","optimizer-oil-main-id"],
                           ["oil_off","optimizer-oil-off-id"]]) {
    $(check).addEventListener("change",()=>{
      oilUseIntent=$("oil_main").checked||$("oil_off").checked;
      syncOilUseToggle();
      $("optimizer-oil-loadout").value="";
      if(!$(check).checked)$(id).value="";
    });
    $(id).addEventListener("input",()=>{
      $("optimizer-oil-loadout").value="";
    });
  }
  $("class-choice").addEventListener("change",()=>{
    populateSpecializationsForClass(field("class-choice"));
    const selected=state.defaults.find(d=>d.class+"/"+d.spec===field("spec"));
    if(selected)fillDefault(selected);
    drawClassSpecTiles();
    buttonState(state.running,state.longrunResultReady);
  });
  $("spec").addEventListener("change",()=>{
    const selected=state.defaults.find(d=>d.class+"/"+d.spec===field("spec"));
    if(selected)fillDefault(selected);
    drawClassSpecTiles();
    buttonState(state.running,state.longrunResultReady);
  });
  $("race").addEventListener("change",()=>buttonState(state.running,state.longrunResultReady));
  $("ilevel").addEventListener("input",()=>buttonState(state.running,state.longrunResultReady));
  $("ilevel").addEventListener("change",showRepresentativeScope);
  $("ilevel").addEventListener("change",()=>withBusy(refreshInstalledOilLoadouts));
  $("season-target-ilevel").addEventListener("change",()=>
    withBusy(refreshInstalledOilLoadouts));
  $("season-game-build").addEventListener("change",()=>
    withBusy(refreshInstalledOilLoadouts));
  $("plan-btn").addEventListener("click",()=>withBusy(async()=>{
    const p=await api("/api/v1/sessions/plan",{method:"POST",payload:buildRequest()});
    markSession(p.session_id);showPlan(p);await pollOnce();
  }));
  $("longrun-prepare-btn").addEventListener("click",()=>withBusy(async()=>{
    const budget=valueInt("longrun-budget");
    if(budget<12||budget>2000)throw Error("Native 예산은 12~2,000회여야 합니다.");
    if(!window.confirm("장기 세션만 준비할까요? DPS Native 0회이며, 미확정 특수장비 L은 기존 정적 Native로 확인할 수 있습니다."))return;
    const response=await api("/api/v1/longrun/prepare",{
      method:"POST",payload:{...buildRequest(),max_native_calls:budget}});
    markSession(response.session_id);
    setNotice("장기 세션 프로필·예산 봉인 완료 · 새 DPS Native 0회 · "+
      (response.static_L_native_calls_this_start||0)+"회 정적 L Native");
    await pollOnce();
  }));
  $("longrun-start-btn").addEventListener("click",()=>withBusy(async()=>{
    const budget=valueInt("longrun-budget");
    const batch=valueInt("longrun-batch");
    if(budget<12||budget>2000||batch<1||batch>32)
      throw Error("장기 탐색 Native 예산은 12~2000, 회차 상한은 1~32여야 합니다.");
    if(!window.confirm("현재 PC에서 적응형 장기 탐색을 시작할까요? 총 Native 상한 "+budget+"회, 이번 회차 최대 "+batch+"회입니다."))return;
    const payload={...buildRequest(),max_native_calls:budget,
                   max_new_native_this_invocation:batch};
    const response=await api("/api/v1/longrun/start",
                             {method:"POST",payload});
    markSession(response.session_id);
    setNotice("장기 적응형 탐색 시작 · 이번 회차 Native 최대 "+batch+"회");
    await pollOnce();
  }));
  $("longrun-resume-btn").addEventListener("click",()=>withBusy(async()=>{
    const batch=valueInt("longrun-batch");
    if(batch<1||batch>32)throw Error("회차 Native 상한은 1~32회여야 합니다.");
    if(!window.confirm("동일한 장기 세션을 최대 "+batch+"회 신규 SimC로 재개할까요?"))return;
    await api("/api/v1/sessions/"+state.session+"/longrun/resume",{
      method:"POST",payload:{max_new_native_this_invocation:batch}});
    setNotice("장기 세션 재개 · 동일 후보 캐시는 중복 실행하지 않습니다.");
    await pollOnce();
  }));
  $("longrun-cache-btn").addEventListener("click",()=>withBusy(async()=>{
    await api("/api/v1/sessions/"+state.session+"/longrun/cache-only",{
      method:"POST",payload:{}});
    setNotice("기존 장기 Native 결과 SHA 재검증 · 신규 실행 0회");
    await pollOnce();
  }));
  $("longrun-cancel-btn").addEventListener("click",()=>withBusy(async()=>{
    await api("/api/v1/sessions/"+state.session+"/longrun/cancel",{
      method:"POST",payload:{}});
    setNotice("장기 세션 취소 요청 · 현재 Native 1건의 완료 후 중단");
    await pollOnce();
  }));
  $("longrun-import-btn").addEventListener("click",()=>withBusy(async()=>{
    const archive=field("longrun-archive-path");
    const sha=field("longrun-archive-sha");
    if(!archive||!/^[0-9a-f]{64}$/.test(sha))
      throw Error("정확한 로컬 ZIP 경로와 원본 SHA256을 입력해 주세요.");
    if(!window.confirm("기존 Native ZIP을 원본·현재 조건으로 검증한 뒤, 신규 Native 0회로 가져올까요?"))return;
    await api("/api/v1/sessions/"+state.session+"/longrun/import",{
      method:"POST",payload:{archive_path:archive,archive_sha256:sha}});
    setNotice("원본 ZIP 및 현재 프로필 검증을 시작했습니다. 신규 DPS Native 0회");
    await pollOnce();
  }));
  $("start-btn").addEventListener("click",()=>withBusy(async()=>{
    // This is the only new-job action. Never start SimC on page load or refresh.
    if(!field("binary")||!field("revision")) {
      switchView("settings");
      $("simc-technical-panel").open=true;
      const missing=!field("binary")?"binary":"revision";
      $(missing).focus();
      throw Error("SimulationCraft 연결 설정을 먼저 완료해 주세요.");
    }
    if(!window.confirm("이 PC에서 최적화를 시작할까요? 계산 중에도 중단할 수 있습니다."))return;
    const p=await api("/api/v1/longrun/start",{method:"POST",payload:{...buildRequest(),max_native_calls:64,continuous:true}});
    markSession(p.session_id);$("filled-result").hidden=true;
    $("empty-result").hidden=false;
    setNotice("로컬 SimC 작업 시작. 계산은 이 PC에서 수행됩니다.");
    await pollOnce();
  }));
  $("resume-btn").addEventListener("click",()=>withBusy(async()=>{
    if(!window.confirm("동일 세션을 재개할까요? 캐시가 없으면 남은 Native 계산이 실행될 수 있습니다."))return;
    await api("/api/v1/sessions/"+state.session+(state.longrunEnabled?"/longrun/resume":"/resume"),
              {method:"POST",payload:state.longrunEnabled?{continuous:true}:{}});
    setNotice("동일 세션 재개 요청됨.");await pollOnce();
  }));
  $("cache-btn").addEventListener("click",()=>withBusy(async()=>{
    await api("/api/v1/sessions/"+state.session+"/cache-only",
              {method:"POST",payload:{}});
    setNotice("기존 Native 6/6 캐시 검증 시작 · 추가 Native 호출 0회");
    await pollOnce();
  }));
  $("cancel-btn").addEventListener("click",()=>withBusy(async()=>{
    await api("/api/v1/sessions/"+state.session+(state.longrunEnabled?"/longrun/cancel":"/cancel"),
              {method:"POST",payload:{}});
    setNotice("취소 요청됨 · 현재 SimC 한 건의 완료 후 다음 후보부터 중단.");
    await pollOnce();
  }));
  $("recent-session-id").addEventListener("change",()=>{
    $("recent-open-btn").disabled=!field("recent-session-id");
  });
  $("recent-open-btn").addEventListener("click",()=>withBusy(
    ()=>restore(field("recent-session-id"))));
  $("recent-refresh-btn").addEventListener("click",()=>withBusy(loadRecentSessions));
  $("restore-btn").addEventListener("click",()=>withBusy(
    ()=>restore(field("restore-id"))));
}
async function initialize() {
  for(const [id,config] of Object.entries(gearGroups))gearInputs(id,config);
  registerHandlers();
  initializeSearchChoices();
  try {
    const boot=await api("/api/v1/bootstrap",{publicRoute:true});
    state.token=boot.session_token;
    const [d,opt,gear]=await Promise.all([api("/api/v1/defaults"),api("/api/v1/options"),
      api("/api/v1/season-gear").catch(()=>null)]);
    state.defaults=d.archetypes;
    state.allowedRacesBySpec=d.allowed_races_by_spec||{};
    installClassSpecChoices();
    installOptions(opt);
    installSeasonGearHints(gear);
    try{await refreshSourceCredentialStatus();}catch(err){
      $("source-credentials-status").textContent="로컬 인증정보 상태 조회 오류: "+err.message;}
    try{renderSeasonOptionCatalog(await api("/api/v1/season-option-catalog"));}
    catch(err){
      $("season-option-catalog-status").textContent=
        "시즌 마법부여 데이터 조회 실패 · 기존 승인 선택을 유지합니다: "+err.message;
    }
    // Read-only local choices. No SimC, new approval or source downloads.
    try{await refreshInstalledOilLoadouts();}
    catch(err){$("optimizer-oil-loadout-status").textContent=
      "검증 설치 기름 목록 조회 실패: "+err.message;}
    // Local verified season only: zero external API calls on web startup.
    if(state.oilCatalog?.game_build) {
      try{await refreshOfficialGameTerms(state.oilCatalog.game_build);}
      catch(err){$("season-terms-status").textContent=
        "공식 한국어 용어 조회 오류 · 기존 표기 유지";}
    }
    // Read-only local status. No remote release lookup on page load.
    try{await refreshSimcUpdater(false);}catch(err){
      $("simc-update-status").textContent="SimC 관리 상태 조회 오류: "+err.message;
    }
    $("simc-technical-panel").open=!field("binary")||!field("revision");
    try{await loadRecentSessions();}
    catch(err){$("recent-session-note").textContent="세션 목록 조회 오류: "+err.message;}
    const paladin=state.defaults.find(v=>v.class==="paladin"&&v.spec==="retribution");
    if(paladin) {
      $("class-choice").value=paladin.class;
      populateSpecializationsForClass(paladin.class,paladin.class+"/"+paladin.spec);
      fillDefault(paladin);
    }else if(state.defaults.length) {
      const first=state.defaults[0];
      $("class-choice").value=first.class;
      populateSpecializationsForClass(first.class,first.class+"/"+first.spec);
      fillDefault(first);
    }
    buttonState();
    beginPolling();
    let previous=null;
    try{previous=localStorage.getItem("simc_secondary_session_id");}catch{}
    if(previous&&/^[a-f0-9]{20}$/.test(previous)){
      try{await restore(previous);}catch(err){
        if(err.message==="SESSION_NOT_FOUND") {
          try{localStorage.removeItem("simc_secondary_session_id");}catch{}
          setNotice("현재 PC에 이전 세션이 없습니다. 다른 컴퓨터에 저장된 기록일 수 있습니다.",true);
        } else {
          setNotice("이전 세션 조회 오류: "+err.message,true);
        }
      }
    }else setNotice("로컬 서버 연결됨 · 새 최적화는 실행 버튼을 눌러야만 시작됩니다.");
  }catch(e){
    setNotice("로컬 서버/사용자 입력 정보 연결 실패: "+e.message,true);
    buttonState();
  }
}
document.addEventListener("DOMContentLoaded",initialize);
