"""v456: product UI cannot offer historic v108 tokens as season approvals.

Test the actual /options FastAPI route and actual app.js installOptions,
plus read-only historical session display. No Native, network, source scans,
session creation or special gem/oil changes.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import unittest

from fastapi.testclient import TestClient

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v113_local_web_api as api
import v218_v098_profile_stage_adapter as stage
import v106_user_session_controller as sessions


class CurrentSeasonOptionalConsumables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=api.create_app(token="v456-ui-scope")
        cls.client=TestClient(cls.app,base_url="http://127.0.0.1:8765")
        cls.headers={"x-simc-local-token":"v456-ui-scope"}

    def get_options(self):
        res=self.client.get("/api/v1/options",headers=self.headers)
        self.assertEqual(res.status_code,200,res.text)
        return res.json()

    def test_actual_api_separates_legacy_source_tokens_from_new_user_choices(self):
        self.assertEqual(self.client.get("/api/v1/options").status_code,403)
        data=self.get_options()
        approved=data["current_season_product_choices"]
        self.assertEqual(approved["schema"],
                         "v113_current_season_optional_consumables_v1")
        self.assertEqual(approved["status"],
                         "NONDEFAULT_UNADMITTED_UNTIL_VERIFIED_SEASON_BINDING")
        self.assertEqual(approved["source_default_simc_token"],"disabled")
        self.assertIs(approved["nondefault_user_selectable"],False)
        for kind in ("food","potion","augmentation"):
            self.assertEqual(approved[kind],["source_default"])
            self.assertIn("disabled",data[kind])
            self.assertGreater(len(data[kind]),1)
        self.assertEqual(approved["diamond_id"],[0])
        self.assertEqual(approved["omnium_talents"],["source_default"])
        self.assertGreater(len(data["diamond_id"]),1)
        self.assertGreater(len(data["omnium_talents"]),1)

    def test_existing_user_defaults_resolve_only_to_disabled_simc_effects(self):
        user=sessions.user_scenario(
            sessions.standard_controls(("mage","frost")))
        result=stage._verified_fresh_season_consumables(user)
        self.assertEqual(result,{
            "food":"disabled","potion":"disabled","augmentation":"disabled"})

    def test_nondefault_diamond_and_folio_still_fail_actual_server_admission(self):
        user=sessions.user_scenario(sessions.standard_controls(("mage","frost")))
        for key,value in (("diamond_id",240967),("omnium_talents","row4_crit")):
            other={**user,"consumable_choices":{
                **user["consumable_choices"],key:value}}
            with self.subTest(key=key),self.assertRaisesRegex(
                    Exception,"FRESH_SEASON_FLASK_DIAMOND_OR_MODULE_NOT_ADMITTED"):
                stage._verified_fresh_season_consumables(other)

    def test_actual_javascript_renders_only_current_season_subset(self):
        node=shutil.which("node")
        if node is None:
            self.skipTest("node is not available on this runner")
        source=ROOT/"runner"/"webui"/"app.js"
        payload=json.dumps(self.get_options(),ensure_ascii=False)
        js=r"""
const fs=require("fs"),assert=require("assert");
const raw=fs.readFileSync(process.argv[1],"utf8");
const a=raw.indexOf("function installOptions(options) {");
const b=raw.indexOf("// Settings: user-triggered official SimC download",a);
assert(a>=0&&b>a,"installOptions original source required");
const rs=raw.indexOf("  const choices=u.consumable_choices||{};");
const re=raw.indexOf('  fillGearRows("special-rows"',rs);
assert(rs>=0&&re>rs,"saved-session original source required");
const options=JSON.parse(process.argv[2]);
const harness=String.raw`
const assert=require("assert");
const state={options:null};
const nodes={};
function $(id) {
  if(!nodes[id])nodes[id]={
    value:"",options:[],
    querySelectorAll(){return []},
    replaceChildren(...arr){this.options=[...arr];this.value=arr[0]?.value||""},
    appendChild(row){this.options.push(row)}
  };
  return nodes[id];
}
function option(value,label){
  const row={value:String(value),textContent:String(label),dataset:{}};
  row.remove=()=>{for(const n of Object.values(nodes)){
    const i=n.options.indexOf(row);if(i>=0)n.options.splice(i,1);
  }};
  return row;
}
function populateSelect(id,values,labeler){
  const el=$(id);el.replaceChildren();
  for(const value of values)el.appendChild(option(value,labeler(value)));
}
function refreshDefaultConsumableSummaries(){}
function syncCraftRow(){}
`;
const inner=raw.slice(a,b);
const saved=raw.slice(rs,re);
const fn=Function("options",harness+inner+String.raw`
installOptions(options);
for(const name of ["food","potion","augmentation"]){
  assert.deepStrictEqual($(name).options.map(v=>v.value),["source_default"]);
  assert.strictEqual($(name).options[0].textContent,
    "미사용 (이번 시즌 기본)");
}
assert.deepStrictEqual($("diamond").options.map(v=>v.value),["0"]);
assert.deepStrictEqual($("omnium").options.map(v=>v.value),["source_default"]);
assert(options.potion.some(v=>v!=="source_default"),"historical options retained server-side");
const u={consumable_choices:{food:"royal_roast",
  potion:"potion_of_recklessness_2",augmentation:"void_touched",
  diamond_id:240967,omnium_talents:"row4_crit"}};
{
`+saved+String.raw`
}
for(const name of ["food","potion","augmentation"]){
  assert.strictEqual($(name).value,u.consumable_choices[name]);
  assert.strictEqual($(name).options.at(-1).dataset.historic,"true");
}
for(const [name,value] of [["diamond","240967"],["omnium","row4_crit"]]){
  assert.strictEqual($(name).value,value);
  assert.strictEqual($(name).options.at(-1).dataset.historic,"true");
}
const u2={consumable_choices:{food:"source_default",
  potion:"source_default",augmentation:"source_default",
  diamond_id:0,omnium_talents:"source_default"}};
{
`+saved.replaceAll("u.consumable_choices","u2.consumable_choices")+
String.raw`
}
for(const name of ["food","potion","augmentation"]){
  assert.strictEqual($(name).value,"source_default");
  assert.strictEqual($(name).options.length,1);
}
assert.deepStrictEqual($("diamond").options.map(v=>v.value),["0"]);
assert.deepStrictEqual($("omnium").options.map(v=>v.value),["source_default"]);
return true;
`);
assert.strictEqual(fn(options),true);
const lost={...options};delete lost.current_season_product_choices;
const render=Function("options",harness+inner+String.raw`
installOptions(options);
for(const name of ["food","potion","augmentation"])
  assert.deepStrictEqual($(name).options.map(v=>v.value),["source_default"]);
assert.deepStrictEqual($("diamond").options.map(v=>v.value),["0"]);
assert.deepStrictEqual($("omnium").options.map(v=>v.value),["source_default"]);
return true;`);
assert.strictEqual(render(lost),true);
console.log("V456_SEASON_OPTION_UI_READONLY_RESTORE_PASS");
"""
        completed=subprocess.run(
            [node,"-e",js,str(source),payload],
            capture_output=True,text=True,timeout=20)
        self.assertEqual(completed.returncode,0,completed.stderr)
        self.assertIn("V456_SEASON_OPTION_UI_READONLY_RESTORE_PASS",
                      completed.stdout)

    def test_current_season_form_refuses_nonapproved_legacy_values(self):
        js=(ROOT/"runner"/"webui"/"app.js").read_text("utf8")
        self.assertIn("const approvedOptional=state.options?.current_season_product_choices;",js)
        self.assertIn("!allowed.includes(field(name))",js)
        self.assertIn("!approvedOptional.diamond_id.includes(Number(field(\"diamond\")))",js)
        self.assertIn("!approvedOptional.omnium_talents.includes(field(\"omnium\"))",js)
        self.assertIn("이전 세션 또는 미검증 ",js)
        self.assertIn("current_season_product:true",js)
        self.assertIn('old.dataset.historic="true";node.appendChild(old);',js)

    def test_source_validations_and_legacy_catalogue_remain_unchanged(self):
        code=(ROOT/"runner"/"v098_target_user_scenario_bootstrap.py").read_text("utf8")
        self.assertIn("bound[k]==default_choice[k]",code)
        data=self.get_options()
        self.assertIn("royal_roast",data["food"])
        self.assertIn("potion_of_recklessness_2",data["potion"])
        self.assertIn("void_touched",data["augmentation"])


if __name__=="__main__":
    unittest.main()
