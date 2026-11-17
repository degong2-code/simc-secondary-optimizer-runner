"""v579: execute real UI oil-default-to-exact-v212 binder on one verified
physical O>0 installed receipt. Offline, no Native, no network, synthetic
browser DOM/calls; original UI code rather than a rewritten algorithm.
v578 retains separate real same-build SimC positive-O evidence.
"""
from __future__ import annotations
import pathlib
import shutil
import subprocess
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]

class DefaultOilInstalledShaUI(unittest.TestCase):
    def test_one_user_default_on_binds_verified_positive_oil_fj_sha_once(self):
        node=shutil.which("node")
        if node is None:self.skipTest("Node required to run actual UI JS")
        script=r"""
const fs=require("fs"),assert=require("assert");
const raw=fs.readFileSync(process.argv[1],"utf8");
function block(start,end){
  const a=raw.indexOf(start),b=raw.indexOf(end,a+start.length);
  assert(a>=0&&b>a,"missing source block "+start);
  return raw.slice(a,b);
}
const sections=[
 block("let oilUseIntent=true;","\nfunction applyOilUseToggle()"),
 block("function installedConsumableScopeMatches(data) {",
       "function renderInstalledFlaskChoices(data) {"),
 block("function renderInstalledOilLoadouts(data) {",
       "// A selected verified oil is an O intent"),
 block("async function bindUniqueInstalledOilVariant() {",
       "function runeCompatibility() {"),
 block("function seasonBuildInputScope(forUserVariant=false) {",
       "async function buildSeasonEnvironment(")
].join("\n");
const BUILD="12.1.5.70783", OLD="a".repeat(64),OIL="b".repeat(64);
const event=[],urls=[],notices=[],selected=[];
const nodes=Object.create(null);
const $=id=>(nodes[id]??={
  type:"text",value:"",checked:false,disabled:false,open:false,
  textContent:"",options:[],querySelectorAll:()=>[],
  replaceChildren(...xs){this.options=[...xs];this.value=xs[0]?.value||""},
  appendChild(v){this.options.push(v)}
});
for(const name of ["oil_main","oil_off","optimizer-oil-enabled",
  "manual-t-mode","season-auto-core"])$(name).type="checkbox";
const field=id=>String($(id).value).trim();
const valueInt=id=>Number(field(id));
const option=(id,label)=>({value:String(id),textContent:String(label)});
const state={
  seasonGearTargetIlevel:334,seasonOptionRequestEpoch:0,
  verifiedInstalledBuildFromThisPage:null,
  oilLoadouts:[],oilCatalog:null,
  seasonGear:{
    status:"CURRENT_SEASON_CANDIDATE_SELECTION_ONLY",
    source_scope:"VERIFIED_INSTALLED_V212_SOURCE_V213_CANDIDATES",
    season_build:BUILD,installed_manifest_sha256:OLD,
    weapon_forms:{"paladin/retribution":"two_hand"},
    choices:{special_effect_gear_candidate:[]}
  }
};
const row={
  installed_manifest_sha256:OIL,selected_oil_item_ids_by_hand:{main_hand:243734},
  verified_flask_item_id:241324,verified_variant_count:1,
  ordinary_four_gem_profile:true,display_name:"주무기 기름 #243734"
};
const catalog={
  schema:"v113_verified_installed_oil_loadouts_v1",
  status:"VERIFIED_INSTALLED_OIL_LOADOUTS",
  game_build:BUILD,target_ilevel:334,items:[row]
};
$("spec").value="paladin/retribution";
$("season-game-build").value=BUILD;
$("ilevel").value="334";
$("season-target-socket-count").value="4";
$("season-selected-flask-id").value="241324";
$("final_T").value="3500";$("manual-t-mode").checked=true;
$("trinket1").value="270175";$("trinket2").value="270173";
const funcs=Function(
 "state","$","field","valueInt","option","renderInstalledFlaskChoices",
 "api","installSeasonGearHints","setTrinketSelection","fillGearRows",
 "specialAllowedSlots","renderSeasonOptionCatalog",
 "restoreInstalledSeasonOptionCatalog","updateBudgetPreview",
 "setNotice","verifiedInstalledGearScopeMatchesRun","oilCompatibility",
 "document",sections+"\nreturn {refreshInstalledOilLoadouts,"+
 "selectedFullVerifiedOil,tryApplyDefaultOil};"
)(state,$,field,valueInt,option,
 data=>{event.push("flasks");assert.strictEqual(data,catalog)},
 async url=>{
   urls.push(url);
   if(url.startsWith("/api/v1/verified-oil-loadouts?")){
     event.push("catalog-get");return catalog;
   }
   if(url.startsWith("/api/v1/season-gear?")){
     event.push("exact-v212-gear-get");
     assert(url.endsWith("&installed_manifest_sha256="+OIL));
     assert(event.includes("flasks"),"Flask catalog must be rendered first");
     return {
       status:"CURRENT_SEASON_CANDIDATE_SELECTION_ONLY",
       source_scope:"VERIFIED_INSTALLED_V212_SOURCE_V213_CANDIDATES",
       season_build:BUILD,installed_manifest_sha256:OIL,
       weapon_forms:{"paladin/retribution":"two_hand"},
       choices:{special_effect_gear_candidate:[]}
     };
   }
   throw Error("UNEXPECTED_HTTP_OR_NATIVE:"+url);
 },
 gear=>{selected.push(gear.installed_manifest_sha256);
   state.seasonGear=gear;state.seasonGearTargetIlevel=null;},
 (id,v)=>$(id).value=v,
 ()=>{},()=>[],()=>{},
 async obj=>{event.push("options-read");assert.equal(obj.installed_manifest_sha256,OIL);},
 ()=>{},s=>notices.push(s),
 ()=>false,
 ()=>{ /* source oilCompatibility calls syncOilUseToggle in product */ },
 {querySelector:()=>({open:false})});
(async()=>{
  await funcs.refreshInstalledOilLoadouts();
  assert.deepStrictEqual(selected,[OIL]);
  assert.strictEqual(state.seasonGear.installed_manifest_sha256,OIL);
  assert.strictEqual(state.seasonGearTargetIlevel,334);
  assert.strictEqual($("optimizer-oil-loadout").value,OIL);
  assert.strictEqual($("optimizer-oil-main-id").value,243734);
  assert.strictEqual($("oil_main").checked,true);
  assert.strictEqual($("oil_off").checked,false);
  assert.strictEqual($("final_T").value,"3500");
  assert.strictEqual($("manual-t-mode").checked,true);
  assert.deepStrictEqual([$("trinket1").value,$("trinket2").value],
     ["270175","270173"]);
  assert(funcs.selectedFullVerifiedOil());
  assert.equal(urls.filter(x=>x.startsWith("/api/v1/season-gear?")).length,1,
    "Default one verified O must resolve exact gear SHA once");
  await funcs.refreshInstalledOilLoadouts();
  assert.equal(urls.filter(x=>x.startsWith("/api/v1/season-gear?")).length,1,
    "Refreshed already-bound verified O cannot repeat gear GET");

  // A unique physical oil mapping with two installed F/J variants must
  // not guess a manifest from a single item/hand label.
  state.seasonGear.installed_manifest_sha256=OLD;
  state.seasonGearTargetIlevel=334;
  $("oil_main").checked=false;$("oil_off").checked=false;
  $("optimizer-oil-main-id").value="";
  $("optimizer-oil-off-id").value="";
  const originalVariantCount=row.verified_variant_count;
  row.verified_variant_count=2;
  await funcs.refreshInstalledOilLoadouts();
  assert.equal(urls.filter(x=>x.startsWith("/api/v1/season-gear?")).length,1);
  assert.strictEqual(state.seasonGearTargetIlevel,null,
    "Ambiguous F/J must invalidate old O=0 installed readiness");
  assert(notices.at(-1).includes("둘 이상"));
  row.verified_variant_count=originalVariantCount;
  console.log("V579_UI_VERIFIED_POSITIVE_O_DEFAULT_EXACT_SHA_BIND_ONCE_PASS");
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});
"""
        result=subprocess.run([node,"-e",script,str(ROOT/"runner/webui/app.js")],
                              cwd=ROOT,capture_output=True,text=True,timeout=18)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn("V579_UI_VERIFIED_POSITIVE_O_DEFAULT_EXACT_SHA_BIND_ONCE_PASS",
                      result.stdout)

    def test_no_new_collection_or_unverified_default_approval(self):
        text=(ROOT/"runner/webui/app.js").read_text(encoding="utf8")
        self.assertIn("    const defaultOilChosen=renderInstalledOilLoadouts(data);",text)
        self.assertIn("    renderInstalledFlaskChoices(data);\n"+
                      "    if(defaultOilChosen)await bindUniqueInstalledOilVariant();",text)
        self.assertIn("  return true;\n}\nfunction applyOilUseToggle()",text)
        self.assertIn("if(matches.length!==1){syncOilUseToggle();return false;}",text)
        self.assertIn("candidate.verified_variant_count===1",text)
        self.assertIn("candidate.ordinary_four_gem_profile===true",text)
        self.assertIn("if(seasonBuildInputScope(true)!==scope ||",text)
        self.assertIn("if(gear.status!==\"CURRENT_SEASON_CANDIDATE_SELECTION_ONLY\"",text)
        self.assertNotIn("automatic_O_approved_by_ui",text)

if __name__=="__main__":
    unittest.main()
