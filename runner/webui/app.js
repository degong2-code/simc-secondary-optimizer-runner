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
const state = { token:"", defaults:[], seasonGear:null, session:"", running:false,
                busy:false, options:null, pollTimer:null, pollBusy:false,
                pollFailures:0, nextPollAt:0 };
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
  if(actors.length!==1||!info.spec||!info.race||!info.talents)
    throw Error("한 캐릭터의 직업·전문화·종족·talents가 모두 필요합니다.");
  const race=info.race.toLowerCase(),spec=info.spec.toLowerCase();
  if(!/^[a-z_]{2,40}$/.test(race)||
     !/^[a-z_]{2,60}$/.test(spec)||
     !/^[A-Za-z0-9+/_=-]{10,2048}$/.test(info.talents))
    throw Error("SimC 종족·전문화·특성 코드 형식이 올바르지 않습니다.");
  const key=actors[0]+"/"+spec;
  const matched=state.defaults.find(x=>x.class+"/"+x.spec===key);
  if(!matched)throw Error("아직 지원하지 않는 전문화: "+key);
  return {key,race,talents:info.talents,defaults:matched};
}
async function importSimcCharacter() {
  const file=$("simc-import-file").files?.[0];
  if(file&&file.size>250000)throw Error("SimC 프로필 파일은 250KB 이하여야 합니다.");
  const source=file?await file.text():$("simc-import-text").value;
  const parsed=parseSimcCharacter(source);
  if(field("spec")!==parsed.key) {
    $("spec").value=parsed.key;
    // Same reset behavior as a manual specialization change.
    fillDefault(parsed.defaults);
  }
  $("race").value=parsed.race;
  $("talents").value=parsed.talents;
  setNotice("SimC 캐릭터 정보만 적용됨 · 현재 장비·스탯은 가져오지 않았고 Native 0회");
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
    return;
  }
  // Show an earlier session's exact identity without silently substituting
  // another trinket. A NEW plan will require an eligible current-season pair.
  if(restored&&/^[0-9]+$/.test(value)) {
    const old=option(value,"이전 세션 장신구 #"+value+" · 새 계획은 재선택");
    old.dataset.historic="true";
    node.appendChild(old);
    node.value=value;
    return;
  }
  node.value="";
}
function installSeasonGearHints(catalog) {
  state.seasonGear=catalog?.status==="CURRENT_SEASON_CANDIDATE_SELECTION_ONLY"
    ? catalog : null;
  const node=$("season-gear-note");
  const current=state.seasonGear?.choices||{};
  for(const fieldId of ["trinket1","trinket2"]) {
    const node=$(fieldId);
    node.replaceChildren(option("","이번 시즌 장신구 선택"));
    for(const item of current.trinket||[])
      node.appendChild(option(item.item_id,item.name+" · #"+item.item_id+
        (item.season_list_basis?" · 시즌 신화+ 후보":"")));
  }
  for(const row of $("special-rows").querySelectorAll(".gear-row")) {
    const element=row.querySelector('[data-field="item_id"]');
    element.replaceChildren(option("","이번 시즌 특수효과 장비 선택"));
    for(const item of current.special_effect_gear_candidate||[])
      element.appendChild(option(item.item_id,item.name+" · #"+item.item_id+
        (item.season_list_basis?" · 시즌 신화+ 후보":"")));
  }
  refreshSpecialSlots();
  if(!state.seasonGear) {
    node.textContent="시즌 선택 목록이 없습니다. 새 장신구·특수효과 선택은 보류됩니다. 기존 세션 조회는 가능합니다.";
    return;
  }
  node.textContent="장신구 "+(current.trinket?.length||0)+"개 · 특수효과 "+
    (current.special_effect_gear_candidate?.length||0)+
    "개를 시즌 목록에서 선택 · 신화+ 후보 포함(드롭 조건 미확정) · 일반장비 자동 구성 · 정확 ID 직접 입력은 제작장비만 예외";
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
    "최신 시즌 대표 장비·직업별 티어 4세트를 내부 생성합니다. 26개 전문화 기본 프로필은 실제 SimC 수용 확인. 사용자 선택 옵션은 실제 SimC 입력으로 평가하며 결과는 세션마다 다릅니다.":
    "334 이외 목표 ilvl: 최신 시즌 대표 장비·티어·무기를 선택 레벨로 구성합니다. 기존 334 Native 결과를 다른 레벨로 확대하지 않으며, 해당 조건의 수용 여부는 실제 SimC 실행으로 판정합니다.";
}

function fillDefault(item) {
  $("race").value=item.race;
  $("talents").value=item.talents;
  setTrinketSelection("trinket1",item.trinket_ids[0]);
  setTrinketSelection("trinket2",item.trinket_ids[1]);
  $("ilevel").value=item.ilevel;
  $("final_T").value=item.final_T??"";
  $("targets").value=item.targets;
  $("duration").value=item.duration_seconds;
  $("raid_buffs").checked=item.raid_buffs;
  $("oil_main").checked=item.oil_hands.includes("main_hand");
  $("oil_off").checked=item.oil_hands.includes("off_hand");
  oilCompatibility();
  for (const id of ["food","potion","augmentation","diamond","omnium"]) $(id).selectedIndex=0;
  // Reset optional slots on specialization changes, including hidden extra rows.
  fillGearRows("special-rows",[]);
  fillGearRows("crafted-rows",[]);
  for(const row of $("crafted-rows").querySelectorAll(".gear-row"))syncCraftRow(row);
  showRepresentativeScope();
}
function oilCompatibility() {
  const key=field("spec");
  const form=state.seasonGear?.weapon_forms?.[key];
  const supportsOff=form==="dual_one_hand"||form==="dual_two_hand";
  $("oil_off").disabled=!supportsOff;
  if(!supportsOff)$("oil_off").checked=false;
  $("oil_off").title=supportsOff?"두 무기에 기름 적용 가능":"이 전문화의 보조무기에는 기름을 사용할 수 없습니다.";
}
function craftSlot(item) {
  if(item.slot_hint)return item.slot_hint;
  if(item.inventory_type===11)return "finger1";
  if(item.inventory_type===20)return "chest";
  return null;
}
function chosenCraft(slot) {
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
  return valid[0]||null;
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
                      (!isSpecial&&name==="item_id")||(isSpecial&&name==="slot");
      label.hidden=isPrivate;
      label.textContent=name==="item_id"?"이번 시즌 장비":
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
        input.addEventListener("change",refreshSpecialSlots);
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
}
function fillSessionInputs(payload) {
  const u=payload.user,c=u.character,t=u.target,b=u.combat;
  const spec=c.class+"/"+c.spec;
  if(!state.defaults.some(item=>item.class+"/"+item.spec===spec))
    throw Error("SESSION_SPEC_NOT_SUPPORTED");
  $("spec").value=spec;
  $("race").value=c.race;
  $("talents").value=c.talents;
  $("ilevel").value=t.ilevel;
  $("final_T").value=t.final_T??"";
  setTrinketSelection("trinket1",u.trinkets[0].item_id,true);
  setTrinketSelection("trinket2",u.trinkets[1].item_id,true);
  $("targets").value=b.targets;
  $("duration").value=b.duration_seconds;
  $("raid_buffs").checked=b.raid_buffs;
  $("oil_main").checked=u.oil_hands.includes("main_hand");
  $("oil_off").checked=u.oil_hands.includes("off_hand");
  oilCompatibility();
  const choices=u.consumable_choices||{};
  for(const key of ["food","potion","augmentation"])
    $(key).value=choices[key]??"source_default";
  const oldOmnium=choices.omnium_talents??"source_default";
  const omni=$("omnium");
  for(const x of Array.from(omni.options))
    if(x.dataset.historic==="true")x.remove();
  if(!Array.from(omni.options).some(x=>x.value===oldOmnium)){
    const historical=option(oldOmnium,"기존 세션 4열 선택 유지");
    historical.dataset.historic="true";omni.appendChild(historical);
  }
  omni.value=oldOmnium;
  $("diamond").value=String(choices.diamond_id??0);
  fillGearRows("special-rows",u.special_items||[]);
  fillGearRows("crafted-rows",u.embellishments||[]);
  // Recover the exact local inputs from this machine's saved session only.
  // No talent strings or OS file paths are stored in browser localStorage.
  $("binary").value=payload.binary;
  $("revision").value=payload.revision;
  $("static_cache").value=payload.static_cache??"";
  showRepresentativeScope();
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
      const resolved=chosenCraft(fields.slot);
      if(!resolved)throw Error("이 직업·부위에 사용할 시즌 제작장비가 없습니다.");
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
  if(!$("optimizer-form").reportValidity()) throw Error("필수 입력과 수치 범위를 확인해 주세요.");
  const spec=field("spec");
  const source=state.defaults.find(d=>d.class+"/"+d.spec===spec);
  if(!source) throw Error("지원되는 전문화를 선택해 주세요.");
  if(!seasonChoice("trinket",valueInt("trinket1"))||
     !seasonChoice("trinket",valueInt("trinket2")))
    throw Error("장신구 2개를 이번 시즌 목록에서 선택해 주세요.");
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
  if(!Number.isInteger(controls.ilevel)||controls.ilevel<266||controls.ilevel>344)
    throw Error("최신 시즌 대표장비의 목표 ilvl은 266~344입니다.");
  return {controls,binary:field("binary"),revision:field("revision"),
          static_cache:field("static_cache")||null,
          current_season_product:true};
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
    $("progress-label").textContent="0 / 6 후보";
    $("progress-pct").textContent="0%";
    $("progress-bar").style.width="0%";
    $("stage-text").textContent="이 세션의 상태를 조회 중입니다.";
  }
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
  try{await fn();}catch(err){
    if(err.message==="SESSION_NOT_FOUND")
      setNotice("현재 PC에는 해당 세션이 없습니다. 다른 컴퓨터에서 실행했다면 그 PC에서 조회해야 합니다.",true);
    else {
      // Never treat missing exact L as zero or run Native to guess it.
      const guidance={
        "V106_SPECIAL_EQUIPMENT_REQUIRES_EXACT_STATIC_CACHE":
          "특수효과 장비에 필요한 정확한 Native 정적 캐시 JSON 경로를 입력하세요.",
        "V106_STATIC_CACHE_NOT_FOUND":
          "지정한 정적 캐시 JSON 파일을 찾을 수 없습니다. 경로를 확인하세요.",
        "SPECIAL_L_REQUIRES_EXACT_NATIVE_STATIC_VARIANT":
          "선택 장비의 아이템 ID·목표 ilvl·옵션과 일치하는 Native 정적 스탯 L이 캐시에 없습니다. 다른 레벨의 레코드를 대신 적용하지 않습니다.",
        "REFERENCE_FIXED_L_CONSTRAINT_UNRESOLVED":
          "선택 장비의 정확한 고정 스탯 L 하한을 확인할 수 없습니다.",
        "SELECTED_SPECIAL_FLOOR_UNFEASIBLE":
          "선택 장비의 고정 스탯 하한 L과 입력 총량 T가 충돌합니다.",
        "FIVE_TIER_LAYOUT_OUTSIDE_FOUR_ROW_CONTRACT":
          "기본 티어 4세트에 다섯 번째 티어 아이템이 추가되었습니다. 이미 포함된 티어 부위로 선택하거나 다른 특수장비 슬롯을 사용하세요."
      };
      setNotice("요청 차단 또는 오류: "+(guidance[err.message]||err.message),true);
    }
  }
  finally{state.busy=false;buttonState(state.running,$("filled-result").hidden===false);}
}
function showPlan(plan) {
  if(!plan?.plan) return;
  const o=Object.values(plan.plan.fixed_O).reduce((a,n)=>a+n,0);
  setNotice("계산 준비 확인 · B "+number(plan.plan.base_B)+
    " + 고정 기름 O "+number(o)+" = 최종 T "+number(plan.plan.final_T)+
    " · 계획 Native 최대 "+plan.plan.native_limit+"회 (지금 실행 0회)"+
    (plan.plan.current_season_product?" · 새 시즌 대표장비 별도 세션":"")+
    (plan.static_cache_auto_used?" · 저장된 정적 캐시 자동 적용":""));
}
function renderProgress(data) {
  const p=data?.progress||{};
  if(!data?.result_ready) {
    $("filled-result").hidden=true;
    $("empty-result").hidden=false;
  }
  const n=Number(p.completed_jobs)||0,limit=Number(p.planned_jobs)||6;
  const pct=Number(p.progress_percent)||0;
  $("progress-label").textContent=n+" / "+limit+" 후보";
  $("progress-pct").textContent=number(pct,0)+"%";
  $("progress-bar").style.width=Math.max(0,Math.min(100,pct))+"%";
  const worker=p.worker?.status||p.status||"NOT_STARTED";
  // A failed resumed worker may stop before v094 overwrites old progress.
  // Show its NEW reason, rather than repeating an older Native error forever.
  const cancelled=!data.active && worker==="CANCELLED_PARTIAL";
  const status=data.active?worker:
    cancelled?"사용자 요청으로 중단 · 완료한 후보 보존 · 같은 세션 재개 가능":
    worker==="BLOCKED_OR_PARTIAL"?
      (p.worker?.reason||p.error||worker):
      (p.error||p.worker?.reason||worker);
  $("stage-text").textContent=status+" · Native 누적 "+(p.native_attempts||0)+
                       " · 캐시 "+(p.cache_hits||0);
  $("run-label").textContent=data.active?"진행 중":
    cancelled?"취소됨 · 재개 가능":
    worker==="BLOCKED_OR_PARTIAL"?"실행 차단":
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
    const row=document.createElement("div");row.className="alt-row";
    const pairLabel=alt.pairwise_95_label==="OBSERVED_NEAR_BUT_LOWER_AT_95"
      ?"95% 기준 낮음":alt.pairwise_95_label==="OBSERVED_NEAR_UNRESOLVED_AT_95"
      ?"95% 우열 미확정":"95% 비교 미확인";
    row.textContent="대안 "+(index+1)+" · DPS "+number(alt.observed_dps_mean,1)+
       " · SEM ±"+number(alt.simc_sem,2)+
       " · 관측 DPS 손실 "+number(alt.observed_dps_loss_pct,3)+"%"+
       " · 분배 이동 "+number(100*alt.rating_moved_fraction_B,1)+"%"+
       " · "+statOrder.map(([key,label])=>label+" "+number(alt.absolute_rating_T[key])+
       " ("+number(alt.percent_of_final_T[key],2)+"%)").join(" / ")+
       " · "+pairLabel;
    list.appendChild(row);
  }
  $("empty-result").hidden=true;$("filled-result").hidden=false;
}
async function readSession(id) {
  // GET only: no SimC Native or session file writes.
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
    $("progress-label").textContent="– / – 후보";
    $("progress-pct").textContent="–";
    $("progress-bar").style.width="0%";
    $("stage-text").textContent="현재 PC에 세션 파일이 없습니다.";
    $("filled-result").hidden=true;$("empty-result").hidden=false;
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
  state.pollFailures=0;state.nextPollAt=0;
  $("filled-result").hidden=true;$("empty-result").hidden=false;
  renderProgress(snapshot.progress);
  if(snapshot.result)renderResult(snapshot.result);
  setNotice("기존 세션·입력 복원 성공 · "+id+" · 새 Native 계산 0회");
}
function installOptions(options) {
  state.options=options;
  const label=(key,value)=>options.display_labels?.[key]?.[String(value)]??
    String(value);
  for(const name of ["food","potion","augmentation"])
    populateSelect(name,options[name],v=>label(name,v));
  populateSelect("diamond",options.diamond_id,v=>label("diamond_id",v));
  populateSelect("omnium",["source_default","row4_crit","row4_haste",
                            "row4_mastery","row4_vers"],v=>({
     source_default:"전문화 기본 Omnium 4열 유지",row4_crit:"치명",
     row4_haste:"가속",row4_mastery:"특화",row4_vers:"유연"
  })[v]);
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
  $("simc-update-candidate").textContent=simcOffer?
    "공식 Windows x64 후보: "+simcOffer+
    " · revision "+result.candidate.revision_short+
    (result.archive_extractor_available?"":" · 7-Zip 필요"):
    "공식 배포 후보를 찾지 못했습니다.";
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
  $("simc-check-btn").addEventListener("click",()=>withBusy(checkSimcUpdater));
  $("simc-install-btn").addEventListener("click",()=>withBusy(installSimcUpdater));
  $("simc-install-local-btn").addEventListener("click",()=>withBusy(installLocalSimcUpdater));
  $("simc-rollback-btn").addEventListener("click",()=>withBusy(rollbackSimcUpdater));
  $("simc-import-btn").addEventListener("click",()=>withBusy(importSimcCharacter));
  $("spec").addEventListener("change",()=>{
    const selected=state.defaults.find(d=>d.class+"/"+d.spec===field("spec"));
    if(selected)fillDefault(selected);
  });
  $("ilevel").addEventListener("change",showRepresentativeScope);
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
  try {
    const boot=await api("/api/v1/bootstrap",{publicRoute:true});
    state.token=boot.session_token;
    const [d,opt,gear]=await Promise.all([api("/api/v1/defaults"),api("/api/v1/options"),
      api("/api/v1/season-gear").catch(()=>null)]);
    state.defaults=d.archetypes;
    $("spec").replaceChildren(...state.defaults.map(item=>
      option(item.class+"/"+item.spec,
             (specLabels[item.class+"/"+item.spec]||
               item.class+" · "+item.spec).split(" (")[0])));
    $("spec").disabled=false;
    installOptions(opt);
    installSeasonGearHints(gear);
    // Read-only local status. No remote release lookup on page load.
    try{await refreshSimcUpdater(false);}catch(err){
      $("simc-update-status").textContent="SimC 관리 상태 조회 오류: "+err.message;
    }
    try{await loadRecentSessions();}
    catch(err){$("recent-session-note").textContent="세션 목록 조회 오류: "+err.message;}
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
