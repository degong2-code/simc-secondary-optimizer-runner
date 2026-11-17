"""v576: exact user manual-final-T intent must not silently become auto T.

Execute the production UI helpers with a bounded minimal DOM. This is
client-side request validation; verified installed season, L/E/J/F/O accounting
and user feasibility remain server-owned by v222/v098. Native/HTTP zero.
"""
from __future__ import annotations
import pathlib,shutil,subprocess,unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]

class ManualFinalTUIOffline(unittest.TestCase):
    def test_actual_manual_mode_and_request_builder(self):
        node=shutil.which("node")
        if node is None:self.skipTest("Node required for actual browser JS")
        harness=r"""
const assert=require("assert"),fs=require("fs");
const raw=fs.readFileSync(process.argv[1],"utf8");
const first=raw.indexOf("function updateManualTMode()");
const end=raw.indexOf("\nfunction syncSeasonTargetIlevel()",first);
const beginBuild=raw.indexOf("function buildRequest() {");
const endBuild=raw.indexOf("\nasync function api(",beginBuild);
assert(first>=0&&end>first&&beginBuild>first&&endBuild>beginBuild);
const source=raw.slice(first,end)+"\n"+raw.slice(beginBuild,endBuild);
const state={
  defaults:[{class:"hunter",spec:"survival"}],
  allowedRacesBySpec:{"hunter/survival":["orc"]},
  options:{current_season_product_choices:{
    food:["none"],potion:["none"],augmentation:["none"],
    diamond_id:[0],omnium_talents:[""]}},
  exactUserEnchantIds:new Set(),eagleApproved:false,
  seasonGear:{installed_manifest_sha256:"a".repeat(64)},
  verifiedInstalledBuildFromThisPage:null,
  seasonBuildTargetManualOverride:false,session:null
};
const nodes=Object.create(null);
function $(id){
  if(!nodes[id])nodes[id]={
    value:"",checked:false,disabled:false,hidden:false,required:false,
    textContent:"",open:false,
    checkValidity(){return true},
    reportValidity(){return true},focus(){}
  };
  return nodes[id];
}
function field(id){return String($(id).value).trim();}
function valueInt(id){
  const text=field(id);
  if(!/^[0-9]+$/.test(text))throw Error(id.toUpperCase()+"_POSITIVE_INTEGER_REQUIRED");
  return Number(text);
}
function updateBudgetPreview(){}
function switchView(){}
function openEquipmentPicker(){}
function simcRace(x){return x;}
function seasonChoice(type,id){
  return type==="trinket"&&[270175,270173].includes(id);
}
function selectedGear(){return [];}
function exactUserEnchantInputsMatch(){return true;}
function selectedFullVerifiedOil(){return true;}
function verifiedInstalledGearScopeMatchesRun(build,ilvl){
  return build==="12.1.5.70783"&&ilvl===334;
}
const factory=Function("state","$","field","valueInt",
  "updateBudgetPreview","switchView","openEquipmentPicker",
  "simcRace","seasonChoice","selectedGear",
  "exactUserEnchantInputsMatch","selectedFullVerifiedOil",
  "verifiedInstalledGearScopeMatchesRun","oilUseIntent",
  source+"\nreturn {updateManualTMode,manualFinalTOrNull,buildRequest};");
const {updateManualTMode,manualFinalTOrNull,buildRequest}=factory(state,$,field,valueInt,
  updateBudgetPreview,switchView,openEquipmentPicker,
  simcRace,seasonChoice,selectedGear,exactUserEnchantInputsMatch,
  selectedFullVerifiedOil,verifiedInstalledGearScopeMatchesRun,false);
$("binary").value="C:\\SimC\\simc.exe";
$("revision").value="de11f57df75dda668bae6ac7043a43b98831fa96";
$("trinket1").value="270175";$("trinket2").value="270173";
$("class-choice").value="hunter";$("spec").value="hunter/survival";
$("race").value="orc";$("ilevel").value="334";
$("talents").value="";$("max-single-stat-percent").value="60";
$("targets").value="1";$("duration").value="300";
$("raid_buffs").checked=true;
$("season-target-socket-count").value="4";
$("season-game-build").value="12.1.5.70783";
$("food").value="none";$("potion").value="none";
$("augmentation").value="none";$("diamond").value="0";
$("omnium").value="";
$("optimizer-form").reportValidity=()=>{
  const t=$("final_T");
  return t.checkValidity();
};
$("final_T").checkValidity=()=>{
  const t=$("final_T");
  return !t.required||(/^[0-9]+$/.test(t.value)&&
    Number(t.value)>=1&&Number(t.value)<=100000);
};
$("manual-t-mode").checked=true;
updateManualTMode();
assert.strictEqual($("final_T").required,true);
assert.strictEqual($("final_T").disabled,false);
assert.strictEqual($("manual-t-field").hidden,false);
assert.throws(()=>buildRequest(),/수동 최종 T를 입력해야 합니다/);
for(const bad of ["0","100001","-1","1.5","garbage"]){
  $("final_T").value=bad;
  assert.throws(()=>buildRequest(),/수동 최종 T는 1~100000/);
  assert.throws(()=>manualFinalTOrNull(),/수동 최종 T는 1~100000/);
}
// Manual final T deliberately differs from verified installed automatic 3107.
$("final_T").value="3414";
const manual=buildRequest();
assert.strictEqual(manualFinalTOrNull(),3414);
assert.strictEqual(manual.controls.final_T,3414);
assert.strictEqual(manual.controls.ilevel,334);
assert.deepStrictEqual(manual.controls.trinket_ids,[270175,270173]);
assert.strictEqual(manual.installed_season_game_build,"12.1.5.70783");
assert.strictEqual(manual.installed_manifest_sha256,"a".repeat(64));
assert.strictEqual(manual.current_season_product,true);
assert.deepStrictEqual(manual.controls.oil_hands,[]);
$("manual-t-mode").checked=false;
updateManualTMode();
assert.strictEqual($("final_T").required,false);
assert.strictEqual($("final_T").disabled,true);
assert.strictEqual($("final_T").value,"");
assert.strictEqual(manualFinalTOrNull(),null);
assert.strictEqual(buildRequest().controls.final_T,null);
// A stale disabled value must not override an explicitly selected auto mode.
$("final_T").value="3414";
assert.strictEqual(manualFinalTOrNull(),null);
assert.strictEqual(buildRequest().controls.final_T,null);
$("manual-t-mode").checked=true;updateManualTMode();
assert.strictEqual(buildRequest().controls.final_T,3414);
"""
        run=subprocess.run([node,"-e",harness,str(ROOT/"runner/webui/app.js")],
            cwd=ROOT,capture_output=True,text=True,timeout=15)
        self.assertEqual(run.returncode,0,run.stderr)

    def test_source_html_explicit_manual_validation(self):
        js=(ROOT/"runner/webui/app.js").read_text("utf8")
        html=(ROOT/"runner/webui/index.html").read_text("utf8")
        self.assertIn('id="manual-t-mode" type="checkbox"',html)
        self.assertIn('id="final_T" type="number" min="1" max="100000"',html)
        self.assertIn('$("final_T").required=manual;',js)
        self.assertIn('final_T:manualFinalT,',js)
        self.assertIn('if(!field("final_T"))',js)
        self.assertIn('const manualFinalT=manualFinalTOrNull();',js)
        first=js.index('$("start-btn").addEventListener("click",')
        self.assertLess(js.index('manualFinalTOrNull();',first),
                        js.index('if(await prepareSeasonBeforeOptimizerStart())return;',first))
        self.assertNotIn('final_T:field("final_T") ? valueInt("final_T"):null',js)

if __name__=="__main__":unittest.main()
