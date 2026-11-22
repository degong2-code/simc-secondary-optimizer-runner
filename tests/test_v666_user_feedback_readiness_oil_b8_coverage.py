"""P3 v666: user screenshot follow-up (no Native or season-source collection)."""
from __future__ import annotations
import pathlib, shutil, subprocess, unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]


class UserFeedbackV666(unittest.TestCase):
    def test_optimizer_readiness_real_js_no_speculative_oil_and_button_reasons(self):
        node=shutil.which("node")
        if node is None:self.skipTest("node not available")
        harness=r"""
const fs=require('fs'),assert=require('assert');
const raw=fs.readFileSync(process.argv[1],'utf8');
function cut(a,b){
 const i=raw.indexOf(a),j=raw.indexOf(b,i);
 assert(i>=0&&j>i,'real source missing: '+a);
 return raw.slice(i,j)+'\n';
}
const code=cut('function validTargetIlevel() {','function setNotice(')+
 cut('function optimizerNeedsSeasonPreparation() {','// v568:')+
 cut('function buttonState(active=false,ready=false) {','async function withBusy(');
const nodes={};
const $=id=>nodes[id]??={value:'',textContent:'',disabled:false,title:'',
  setAttribute(){}};
const field=id=>String($(id).value).trim();
let oilUseIntent=true,oilOk=false;
const state={token:'local',verifiedInstalledBuildFromThisPage:'12.1.5.70961',
 busy:false,session:'',longrunEnabled:false,longrunResultReady:false,
 longrunCompleted:false};
for(const [k,v] of Object.entries({
 'season-game-build':'12.1.5.70961','spec':'mage/fire','race':'dwarf',
 'ilevel':'334','trinket1':'270175','trinket2':'270173'
}))$(k).value=v;
const api=Function('state','$','field','verifiedInstalledGearScopeMatchesRun',
 'valueInt','oilUseIntent','selectedFullVerifiedOil',code+
 '\nreturn {buttonState};');
function refresh(){
 api(state,$,field,(build,l)=>build==='12.1.5.70961'&&l===334,
 ()=>{throw Error('STATUS_NOT_ALLOWED_TO_START_NATIVE')},
 oilUseIntent,()=>oilOk).buttonState();
}
refresh();
assert.strictEqual($('start-btn').disabled,true);
assert($('optimizer-submit-note').textContent.includes('무기 기름'));
oilUseIntent=false;refresh();
assert.strictEqual($('start-btn').disabled,false);
assert($('optimizer-submit-note').textContent.includes('실행 조건이 준비'));
$('trinket2').value='';refresh();
assert.strictEqual($('start-btn').disabled,true);
assert($('optimizer-submit-note').textContent.includes('장신구 2개'));
$('trinket2').value='270173';oilUseIntent=true;oilOk=true;refresh();
assert.strictEqual($('start-btn').disabled,false);
$('ilevel').value='335';refresh();
assert.strictEqual($('start-btn').disabled,false,
 'season preparation must remain an actionable button before gear selection');
assert($('optimizer-submit-note').textContent.includes('시즌 환경'));
state.busy=true;refresh();
assert.strictEqual($('start-btn').disabled,true,
 'busy must disable even in season-preparation mode');
state.busy=false;$('ilevel').value='';refresh();
assert.strictEqual($('start-btn').disabled,true);
assert($('optimizer-submit-note').textContent.includes('아이템레벨'));
console.log('V666_READINESS_OIL_DISABLED_REASONS_PASS');
"""
        result=subprocess.run([node,"-e",harness,
            str(ROOT/"runner/webui/app.js")],capture_output=True,text=True,
            timeout=25)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn("V666_READINESS_OIL_DISABLED_REASONS_PASS",result.stdout)

    def test_b8_specific_missing_evidence_error_and_no_oil_conflation(self):
        api=(ROOT/"runner/v113_local_web_api.py").read_text("utf8")
        ui=(ROOT/"runner/webui/app.js").read_text("utf8")
        for code in ("WEB_SELECTED_B8_EXACT_STATIC_VARIANTS_PENDING",
                     "WEB_SELECTED_B8_PROFILE_SOURCE_PENDING"):
            self.assertIn(code,api)
            self.assertIn(code,ui)
        self.assertIn('observed=="B8_SELECTED_PROFILE_STATIC_VARIANTS_PENDING_NO_NATIVE"',api)
        self.assertIn('observed=="V216_TO_V098_SOURCE_PROFILE_PENDING"',api)
        self.assertIn("if(!oilUseIntent){",ui)
        self.assertIn('$("oil_main").checked=false;$("oil_off").checked=false;',ui)
        self.assertIn('state.seasonGearTargetIlevel=null;',ui)

    def test_partial_special_gear_list_not_a_full_season_or_a_display_limit(self):
        ui=(ROOT/"runner/webui/app.js").read_text("utf8")
        html=(ROOT/"runner/webui/index.html").read_text("utf8")
        gear=(ROOT/"runner/v167_product_season_gear_adapter.py").read_text("utf8")
        self.assertIn("specials.length",ui)
        self.assertIn("시즌 전체 목록 완성 확인 전",ui)
        self.assertIn("시즌 전체 목록의 완전성은 아직 확인되지 않았습니다",ui)
        self.assertIn('"full_season_completeness_confirmed":False',gear)
        self.assertIn('id="equipment-special-status"',html)
        self.assertIn('id="optimizer-submit-note" role="status" aria-live="polite"',html)


if __name__=="__main__":unittest.main()
