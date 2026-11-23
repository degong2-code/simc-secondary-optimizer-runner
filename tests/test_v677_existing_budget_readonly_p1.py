"""v677: exact existing v212/v113 G/J/F/O reuse; no new SimC/Native/DB2.

The user chooses ONE independently verified original SHA. This test checks
read-only numeric budget authority and actual JS button wiring, not DPS.
"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from fastapi.testclient import TestClient

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v113_local_web_api as web


class ExistingBudgetReadOnlyHTTP(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        self.app=web.create_app(root=self.root/"runs",token="fixture-local-only")
        self.client=TestClient(self.app,base_url="http://127.0.0.1:8765")
        self.headers={"x-simc-local-token":"fixture-local-only",
                      "origin":"http://127.0.0.1:8765"}
        self.build="12.1.5.70961"
        self.ilevel=334
        self.sha="a"*64
        self.flask=241320
        self.oil={stat:0 for stat in web.environment_manifest.season_budget.STATS}
        docs=self.app.state.jobs.root/"_fresh_season_sources"/(
            "wago_"+self.build)/"fresh_source"
        docs.mkdir(parents=True)
        self.docs=docs
        self.installed={
            "manifest_sha256":self.sha,"game_build":self.build,
            "target_ilevel":self.ilevel,
            "official_G_reference_track":"general",
            "official_G":2850,"official_J":92,"official_F":165,
            "official_B":3107,"official_T":3107,
            "official_O":dict(self.oil),
            "official_O_physical_source":None,
            "official_F_physical_source":{
                "physical_item_id":self.flask,
                "crafting_quality":2,"F_rating":165,
                "simc_input_token":"flask_of_thalassian_resistance_2"
            }
        }
        self.receipt=docs/("v212_installed_"+self.sha[:20]+".json")
        self.receipt.write_text(json.dumps(self.installed),encoding="utf8")
        self.snapshot=docs/("v113_profile_"+self.sha[:20]+".json")
        self.snapshot.write_text(json.dumps({
            "environment_result":{"source_compilation":{
                "physical_gem_layout_unadmitted":{
                    "schema":"v271_user_socket_gem_layout_stage_v1",
                    "status":"PHYSICAL_GEMS_STAGED_SOURCE_AND_SOCKET_PROOFS_PENDING",
                    "ordinary_gem_ids":[240890,240898,240906,240914],
                    "special_gem_id":None,"socket_total":4
                }
            }}
        }),encoding="utf8")
        self.matched={
            "environment_ready":True,"environment_installed":True,
            "installed_manifest_sha256":self.sha,
            "selected_oil_item_ids_by_hand":{},
            "G":2850,"J":92,"F":165,"O":dict(self.oil),
            "B":3107,"T":3107
        }
        self.url="/api/v1/environment/installed-budget"

    def get(self,**kwargs):
        data={"game_build":self.build,"target_ilevel":self.ilevel,
              "installed_manifest_sha256":self.sha,
              "selected_flask_item_id":self.flask,
              "reference_G_track":"general"}
        data.update(kwargs)
        return self.client.get(self.url,params=data,headers=self.headers)

    def test_original_install_read_only_GJFO_T_no_native(self):
        before={p.name:p.read_bytes() for p in self.docs.iterdir()}
        def find(*args,**kwargs):
            self.assertEqual(kwargs["expected_game_build"],self.build)
            self.assertEqual(kwargs["expected_installed_manifest_sha256"],self.sha)
            self.assertEqual(kwargs["selected_oil_item_ids_by_hand"],{})
            self.assertEqual(kwargs["required_reference_G_track"],"general")
            return dict(self.matched)
        with mock.patch.object(web.environment_build,
                               "find_verified_installed_season_environment",
                               side_effect=find), \
             mock.patch.object(web.environment_manifest,
                               "verify_fresh_installed_environment"), \
             mock.patch.object(web,
                               "_v672_verified_runtime_inputs_digest",
                               return_value="verified-original-stage"), \
             mock.patch.object(web.subprocess,"Popen",
                               side_effect=AssertionError("NO_NATIVE")), \
             mock.patch.object(web.retail_build_source,"discover",
                               side_effect=AssertionError("NO_NETWORK")):
            response=self.get()
        self.assertEqual(response.status_code,200,response.text)
        data=response.json()
        self.assertEqual(data["status"],"VERIFIED_EXISTING_INSTALLED_BUDGET")
        self.assertEqual((data["G"],data["J"],data["F"],data["B"],data["T"]),
                         (2850,92,165,3107,3107))
        self.assertEqual(data["O"],self.oil)
        self.assertEqual(data["installed_manifest_sha256"],self.sha)
        self.assertTrue(data["verified_saved_v113_profile"])
        self.assertFalse(data["current_retail_build_verified"])
        self.assertFalse(data["dps_optimization_started"])
        self.assertEqual(data["native_calls_now"],0)
        self.assertEqual(data["network_calls_now"],0)
        self.assertEqual(before,
                         {p.name:p.read_bytes() for p in self.docs.iterdir()},
                         "existing budget lookup cannot write to the receipt cache")

    def test_scope_stale_original_and_inconsistent_budget_all_rejected(self):
        def find(*args,**kwargs):
            return dict(self.matched)
        with mock.patch.object(web.environment_build,
                               "find_verified_installed_season_environment",
                               side_effect=find), \
             mock.patch.object(web.environment_manifest,
                               "verify_fresh_installed_environment"), \
             mock.patch.object(web,
                               "_v672_verified_runtime_inputs_digest",
                               return_value="valid-stage"):
            for kwargs in ({"selected_flask_item_id":241321},
                           {"reference_G_track":"fury_dual_2h"},
                           {"game_build":"12.1.5.70575"},
                           {"target_ilevel":335},
                           {"installed_manifest_sha256":"b"*64}):
                with self.subTest(kwargs=kwargs):
                    self.assertEqual(self.get(**kwargs).status_code,409)
            self.assertEqual(self.get(game_build="bad").status_code,422)
            self.assertEqual(self.get(installed_manifest_sha256="abc").status_code,422)
            for key,value in (("official_T",3108),("official_B",3108),
                              ("official_J",93),
                              ("official_O",{**self.oil,"crit_rating":10})):
                prior=self.installed[key]
                self.installed[key]=value
                self.receipt.write_text(json.dumps(self.installed),
                                        encoding="utf8")
                with self.subTest(field=key):
                    self.assertEqual(self.get().status_code,409)
                self.installed[key]=prior
                self.receipt.write_text(json.dumps(self.installed),
                                        encoding="utf8")
        self.assertNotEqual(self.get().status_code,200,
                            "unmocked incomplete source cannot be admitted")
        self.assertNotEqual(
            self.client.get(self.url,params={"game_build":self.build},
                            headers={}).status_code,200)

    def test_missing_gem_proof_and_snapshot_stage_do_not_authorize_T(self):
        with mock.patch.object(web.environment_build,
                               "find_verified_installed_season_environment",
                               return_value=dict(self.matched)), \
             mock.patch.object(web.environment_manifest,
                               "verify_fresh_installed_environment"), \
             mock.patch.object(web,
                               "_v672_verified_runtime_inputs_digest",
                               return_value="original-stage"):
            self.assertEqual(self.get().status_code,200)
            self.snapshot.write_text(json.dumps({"environment_result":{}}),
                                     encoding="utf8")
            self.assertEqual(self.get().status_code,409)
            self.snapshot.unlink()
            self.assertEqual(self.get().status_code,409)


    def test_first_failed_original_check_code_without_native_or_paths(self):
        """One original verifier stage, not nine guessed root causes."""
        with mock.patch.object(web.subprocess,"Popen",
                               side_effect=AssertionError("NO_NATIVE")), \
             mock.patch.object(web.retail_build_source,"discover",
                               side_effect=AssertionError("NO_NETWORK")):
            invalid=self.get(game_build="not-a-build")
            self.assertEqual(invalid.status_code,422)
            self.assertEqual(invalid.json()["detail"]["check"],"SCOPE_INPUT")
            with mock.patch.object(web.environment_build,
                                   "find_verified_installed_season_environment",
                                   return_value=None):
                missing=self.get()
            self.assertEqual(missing.status_code,409)
            self.assertEqual(missing.json()["detail"]["check"],
                             "INSTALLED_ENVIRONMENT")
            with mock.patch.object(web.environment_build,
                                   "find_verified_installed_season_environment",
                                   return_value=dict(self.matched)), \
                 mock.patch.object(web.environment_manifest,
                                   "verify_fresh_installed_environment"):
                original_snapshot=self.snapshot.read_text(encoding="utf8")
                self.snapshot.unlink()
                missing_profile=self.get()
                self.assertEqual(missing_profile.json()["detail"]["check"],
                                 "INSTALL_OR_PROFILE_RECEIPT")
                self.snapshot.write_text(original_snapshot,encoding="utf8")
                wrong_flask=self.get(selected_flask_item_id=241321)
                self.assertEqual(wrong_flask.json()["detail"]["check"],
                                 "FLASK_OR_OIL_PHYSICAL_IDENTITY")
                with mock.patch.object(web,
                                       "_v672_verified_runtime_inputs_digest",
                                       return_value=None):
                    mismatch=self.get()
                self.assertEqual(mismatch.json()["detail"]["check"],
                                 "SAVED_PROFILE_INPUTS")
                with mock.patch.object(web,
                                       "_v672_verified_runtime_inputs_digest",
                                       return_value="original-stage"):
                    self.installed["official_T"]=3108
                    self.receipt.write_text(json.dumps(self.installed),encoding="utf8")
                    total=self.get()
                self.assertEqual(total.json()["detail"]["check"],
                                 "GJFO_TOTAL_CONSISTENCY")
                self.assertNotIn(str(self.root),total.text)
                self.assertNotIn("simc.exe",total.text)



class ExistingBudgetReadOnlyBrowser(unittest.TestCase):
    def test_actual_js_button_uses_only_exact_get_not_season_build(self):
        node=shutil.which("node")
        if node is None:
            self.skipTest("Node needed for browser JS execution")
        harness=r"""
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync(process.argv[1],'utf8');
const a=src.indexOf('async function prepareSelectedExistingEnvironment() {');
const b=src.indexOf('function optimizerNeedsSeasonPreparation() {',a);
assert(a>=0&&b>a);
const nodes=Object.create(null),calls=[],notices=[];
const $=id=>(nodes[id]??={value:'',textContent:'',checked:false});
const field=id=>String($(id).value||'');
const A='a'.repeat(64);
$('season-verified-budget').value=A;
$('season-game-build').value='12.1.5.70961';
$('ilevel').value='334';$('season-target-socket-count').value='4';
$('season-verified-flask').value='241320';
$('season-selected-flask-id').value='241320';
$('spec').value='mage/fire';
const O={crit_rating:0,haste_rating:0,mastery_rating:0,versatility_rating:0};
const report={
  schema:'v677_verified_existing_installed_budget_v1',
  status:'VERIFIED_EXISTING_INSTALLED_BUDGET',
  game_build:'12.1.5.70961',target_ilevel:334,
  installed_manifest_sha256:A,selected_flask_item_id:241320,
  reference_G_track:'general',verified_saved_v113_profile:true,
  current_retail_build_verified:false,native_calls_now:0,
  G:2850,J:92,F:165,O,B:3107,T:3107
};
const state={
 verifiedBaseFlaskInstalls:[{installed_manifest_sha256:A,
   flask_item_id:241320,individually_verified:true}],
 seasonGear:{installed_manifest_sha256:A},
 seasonGearTargetIlevel:334,verifiedInstalledBuildFromThisPage:null,
 verifiedExistingBudget:null
};
let oilUseIntent=false, native=0, previews=0;
const api=async url=>{
  calls.push(url);
  assert(url.startsWith('/api/v1/environment/installed-budget?'));
  assert(url.includes('installed_manifest_sha256='+A));
  assert(url.includes('selected_flask_item_id=241320'));
  return report;
};
const seasonBuildInputScope=()=>JSON.stringify(
 ['season-game-build','ilevel','season-target-socket-count',
  'season-verified-budget','season-verified-flask','season-selected-flask-id']
 .map(id=>field(id)));
const verifiedInstalledGearScopeMatchesRun=(build,ilevel)=>
  build==='12.1.5.70961'&&ilevel===334&&
  state.seasonGear.installed_manifest_sha256===A;
const verifiedExistingBudgetScopeMatchesRun=()=>true;
const funcs=Function('state','field','$','oilUseIntent',
 'seasonBuildInputScope','api','verifiedInstalledGearScopeMatchesRun',
 'chooseInstalledFlask','verifiedExistingBudgetScopeMatchesRun',
 'updateBudgetPreview','number','setNotice','buildSeasonEnvironment',
 src.slice(a,b)+'\nreturn {prepareUserSelectedEnvironment};')(
 state,field,$,oilUseIntent,seasonBuildInputScope,api,
 verifiedInstalledGearScopeMatchesRun,async()=>{throw Error('NO_GEAR_REPEAT')},
 verifiedExistingBudgetScopeMatchesRun,()=>previews++,n=>String(n),
 msg=>notices.push(msg),async()=>{native++;throw Error('NO_NATIVE_BUILD');});
(async()=>{
 await funcs.prepareUserSelectedEnvironment();
 assert.equal(calls.length,1);
 assert.equal(native,0);
 assert.equal(previews,2);
 assert.equal(state.verifiedExistingBudget.T,3107);
 assert($('user-variant-status').textContent.includes('신규 Native 0회'));
 assert(!calls[0].includes('season-build'));
 // Missing exact choice: never trigger Native by default.
 $('season-verified-budget').value='';
 await funcs.prepareUserSelectedEnvironment().then(
  ()=>{throw Error('SHOULD_FAIL')},
  err=>assert(err.message.includes('먼저 선택')));
 assert.equal(native,0);
 assert.equal(calls.length,1);
 console.log('V677_EXISTING_INSTALL_BUTTON_NATIVE0_PASS');
})().catch(e=>{console.error(e.stack||e);process.exitCode=1});
"""
        r=subprocess.run([node,"-e",harness,
                          str(ROOT/"runner/webui/app.js")],
                         cwd=ROOT,text=True,capture_output=True,timeout=20)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn("V677_EXISTING_INSTALL_BUTTON_NATIVE0_PASS",r.stdout)

    def test_optimizer_and_UI_hooks_use_read_only_selected_source(self):
        s=(ROOT/"runner/webui/app.js").read_text(encoding="utf8")
        self.assertIn('"user-variant-prepare-btn").addEventListener("click",()=>withBusy(prepareUserSelectedEnvironment)',s)
        self.assertIn("await prepareSelectedExistingEnvironment();",s)
        self.assertIn("/api/v1/environment/installed-budget?",s)
        self.assertIn("verifiedExistingBudgetScopeMatchesRun()",s)
        self.assertIn("state.verifiedExistingBudget=null;",s)
        self.assertIn('rating (검증된 설치본)',s)
        self.assertIn('return buildSeasonEnvironment(true)',s)
        self.assertNotIn(
            '"user-variant-prepare-btn").addEventListener("click",()=>withBusy(()=>buildSeasonEnvironment(true))',s)


    def test_first_blocker_user_text_and_safe_codes_real_js(self):
        node=shutil.which("node")
        if node is None:
            self.skipTest("Node needed for actual browser helper")
        harness=r"""
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync(process.argv[1],'utf8');
const a=src.indexOf('function describeUserBlocker(err,context) {');
const b=src.indexOf('function clearUserBlocker()',a);
assert(a>=0&&b>a);
const describe=Function(src.slice(a,b)+'return describeUserBlocker;')();
const missing=describe({message:'EXISTING_INSTALLED_BUDGET_SOURCE_NOT_VERIFIED',
 safeCheck:'FOUR_GEM_LAYOUT',preparationStep:'BUDGET_READ',
 httpStatus:409},'environment');
assert(missing.message.includes('보석'));
assert(missing.message.includes('기존 예산 조회'));
assert(missing.message.includes('다음 조치'));
assert(missing.technical.includes('FOUR_GEM_LAYOUT'));
const unknown=describe({message:'LOCAL_SESSION_PRECHECK_BLOCKED',
 safeKind:'ValueError'},'optimizer');
assert(unknown.message.includes('내부 원인'));
assert(unknown.technical.includes('ValueError'));
const oil=describe({message:'WEB_FRESH_SELECTED_OIL_ITEM_IDS_NOT_INSTALLED'},
 'optimizer');
assert(oil.message.includes('무기 기름'));
const b8=describe({message:'WEB_SELECTED_B8_EXACT_STATIC_VARIANTS_PENDING'},
 'optimizer');
assert(b8.message.includes('정적 rating'));
const leaked=describe({message:'C:\\Users\\private\\secret-key'},
 'environment');
assert(!leaked.message.includes('private'));
assert(!leaked.technical.includes('private'));
console.log('V678_FIRST_BLOCKER_SAFE_STAGE_UI_PASS');
"""
        p=subprocess.run([node,"-e",harness,
                          str(ROOT/"runner/webui/app.js")],
                         cwd=ROOT,text=True,capture_output=True,timeout=20)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn("V678_FIRST_BLOCKER_SAFE_STAGE_UI_PASS",p.stdout)
        html=(ROOT/"runner/webui/index.html").read_text(encoding="utf8")
        self.assertIn('id="user-variant-diagnostic"',html)
        self.assertIn('id="user-variant-diagnostic-text"',html)
        js=(ROOT/"runner/webui/app.js").read_text(encoding="utf8")
        self.assertIn("error.safeCheck=check",js)
        self.assertIn('err.preparationStep="BUDGET_READ"',js)
        self.assertIn('err.preparationStep="GEAR_BIND"',js)
        self.assertIn("state.lastUserBlocker.message",js)



if __name__=="__main__":
    unittest.main()
