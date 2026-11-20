"""v646: execute production season recovery mapping; no network or Native.

Only a source-backed first blocker may drive a specific user action.
Dependent compiler PENDING must never trigger a false READY or fake version.
"""
from html.parser import HTMLParser
import pathlib
import shutil
import subprocess
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.attrs={}
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get("id"):
            self.attrs[a["id"]]=(tag,a)


class SeasonRecovery(unittest.TestCase):
    def test_same_panel_recovery_is_wired_and_no_new_source_gate(self):
        html=(ROOT/"runner/webui/index.html").read_text("utf8")
        js=(ROOT/"runner/webui/app.js").read_text("utf8")
        css=(ROOT/"runner/webui/styles.css").read_text("utf8")
        tags=Tags()
        tags.feed(html)
        for element in ("season-build-remedy","season-build-remedy-title",
                        "season-build-remedy-detail","season-build-remedy-action",
                        "season-build-summary","season-build-pending",
                        "season-diagnostic-copy-btn","simc-technical-panel",
                        "season-credentials-panel"):
            self.assertIn(element,tags.attrs)
        self.assertEqual(tags.attrs["season-build-remedy"][1].get("role"),"status")
        self.assertEqual(tags.attrs["season-build-remedy"][1].get("aria-live"),"polite")
        self.assertIn("hidden",tags.attrs["season-build-remedy"][1])
        self.assertIn('$("season-build-remedy-action").addEventListener("click",performSeasonBuildRecovery)',js)
        self.assertIn('displaySeasonBuildRecovery(ready?null:seasonBuildRecoveryPlan(data))',js)
        self.assertIn('displaySeasonBuildRecovery(seasonBuildRecoveryPlan(null,safeError))',js)
        self.assertIn("simc_source_reason:cleanCode",js)
        self.assertIn("simc_revision_resolution_reason:cleanCode",js)
        self.assertIn('#view-settings .season-remedy[hidden]{display:none!important}',css)
        self.assertIn('GitHub Windows nightly 기록(최신/빌드 일치 미검증)',js)
        self.assertNotIn('link.textContent="SimC 공식 GitHub Windows nightly 받기";',js)

    def test_actual_production_js_first_cause_priority_and_buttons(self):
        node=shutil.which("node")
        if not node:
            self.skipTest("Node unavailable")
        harness=r"""
const assert=require('assert');
const fs=require('fs');
const raw=fs.readFileSync(process.argv[1],'utf8');
const a=raw.indexOf('function seasonBuildRecoveryPlan(data,errorCode=null) {');
const b=raw.indexOf('\nfunction diagnoseSeasonBuildEvidence(data) {',a);
assert(a>=0&&b>a);
const source=raw.slice(a,b);
const nodes={};
for(const id of ['season-build-remedy','season-build-remedy-title',
                 'season-build-remedy-detail','season-build-remedy-action',
                 'simc-technical-panel','simc-update-panel','revision',
                 'season-credentials-panel','source-credentials-status',
                 'source-blizzard-id','season-build-btn',
                 'season-verified-flask'])
  nodes[id]={hidden:true,textContent:'',open:false,focused:false,
    focus(){this.focused=true},scrollIntoView(){this.scrolled=true}};
const changed=[];
let copied=0;
const make=Function('$','switchView','copySeasonBuildDiagnostic',source+
  '\nreturn {seasonBuildRecoveryPlan,displaySeasonBuildRecovery,performSeasonBuildRecovery};');
const {seasonBuildRecoveryPlan:plan,displaySeasonBuildRecovery:render,
       performSeasonBuildRecovery:action}=make(
  id=>nodes[id],x=>changed.push(x),()=>copied++);
const mismatch={
  web_environment_scope:{game_build:'12.1.5.70961'},
  fresh_pinned_first_party_simc_source:{
    status:'SIMC_FIRST_PARTY_SOURCE_COLLECTION_PENDING',
    reason:'V229_GENERATED_SIMC_COMPILED_BUILD_MISMATCH'},
  source_compilation:{status:'COLLECTED_COMPILER_INPUTS_PENDING',
    missing:['TIER_V168','GENERATED_GEM','PINNED_SIMC_REVISION']},
  zero_history_build:{requires:['G_NATIVE_RATING_OBSERVATION_PENDING']}};
let got=plan(mismatch);
assert.equal(got.kind,'simc');
assert(got.title.includes('불일치'));
assert(got.detail.includes('12.1.5.70961'));
assert(!got.detail.includes('70448')); // never invent an observed source build
render(got);assert.equal(nodes['season-build-remedy'].hidden,false);
assert(nodes['season-build-remedy-detail'].textContent.includes('GitHub 대체 Nightly'));
action();
assert.equal(changed.at(-1),'settings');
assert.equal(nodes['simc-technical-panel'].open,true);
assert.equal(nodes['simc-update-panel'].open,true);
assert.equal(nodes.revision.focused,true);

got=plan({
  web_environment_scope:{game_build:'12.1.5.70961'},
  season_discovery:{status:'AUTHENTICATED_SEASON_CREDENTIALS_MISSING'},
  season_join:{status:'AUTHENTICATED_SEASON_JOIN_NOT_READY'},
  source_compilation:{missing:['TIER_V168']}});
assert.equal(got.kind,'credentials');render(got);action();
assert.equal(nodes['season-credentials-panel'].open,true);
assert.equal(nodes['source-blizzard-id'].focused,true);

got=plan({fresh_pinned_first_party_simc_source:{
  status:'SIMC_FIRST_PARTY_SOURCE_COLLECTION_PENDING',
  reason:'V229_GITHUB_TREE_FETCH_FAILED'},
 source_compilation:{missing:['TIER_V168']}});
assert.equal(got.kind,'simc-source');
assert(!got.title.includes('빌드가 요청 빌드와'));
got=plan({source_compilation:{missing:['TIER_V168','V189']}});
assert.equal(got.kind,'source');render(got);action();
assert.equal(copied,1);
got=plan({fresh_pinned_first_party_simc_source:{
 status:'SIMC_FIRST_PARTY_SOURCE_COLLECTION_PENDING',
 reason:'V229_SET_BONUS_BUILD_OR_HEADER_MISMATCH'},
 source_compilation:{missing:['TIER_V168']}});
assert.equal(got.kind,'simc-source'); // ambiguous header is not proven mismatch
got=plan(null,'RETAIL_VERSION_LIVE_SOURCE_UNAVAILABLE');
assert.equal(got.kind,'network');render(got);action();
assert.equal(nodes['season-build-btn'].focused,true);
got=plan(null,'V216_UNQUALIFIED_MULTIPLE_INSTALLED_FJ_VARIANTS_SELECT_EXACT_SHA');
assert.equal(got.kind,'selection');
got=plan({source_compilation:{missing:[]}});
assert.equal(got.kind,'unknown');
assert.equal(plan(null),null);
render(null);
assert.equal(nodes['season-build-remedy'].hidden,true);
assert.equal(copied,1);
"""
        completed=subprocess.run([node,"-e",harness,
                      str(ROOT/"runner/webui/app.js")],
                 cwd=ROOT,timeout=20,text=True,capture_output=True)
        self.assertEqual(completed.returncode,0,completed.stderr)


if __name__=="__main__":
    unittest.main()
