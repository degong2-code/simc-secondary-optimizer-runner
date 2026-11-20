"""v647 UI editorial balance: retain section separators, reduce row-rule clutter.

Test actual HTML/CSS/JS feature names without browser screenshots or Native.
All existing DOM ids and programmatic accessibility/status behavior remain.
"""
from html.parser import HTMLParser
import pathlib
import shutil
import subprocess
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]


class HTMLIds(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids={}
    def handle_starttag(self,tag,attrs):
        values=dict(attrs)
        if "id" in values:
            self.ids.setdefault(values["id"],[]).append((tag,values))


class ThreeViewEditorial(unittest.TestCase):
    def test_visual_contract_and_computation_targets_preserved(self):
        css=(ROOT/"runner/webui/styles.css").read_text("utf8")
        html=(ROOT/"runner/webui/index.html").read_text("utf8")
        js=(ROOT/"runner/webui/app.js").read_text("utf8")
        parser=HTMLIds()
        parser.feed(html)
        self.assertTrue(all(len(rows)==1 for rows in parser.ids.values()),
                        "Duplicate ID causes lost button/status bindings")
        required=["notice","view-settings","view-results","view-optimizer",
                  "season-build-summary","season-build-remedy",
                  "season-build-remedy-title","season-build-remedy-detail",
                  "season-build-remedy-action","source-credentials-save-btn",
                  "simc-check-btn","simc-connection-confirm-btn",
                  "optimizer-environment-state","manual-t-mode",
                  "budget-preview-total","season-build-pending",
                  "start-btn","dps","sem","conf95","budget","stat-bars",
                  "alt-count","alt-list","resume-btn","cancel-btn","run-label"]
        for elem in required:
            with self.subTest(id=elem):
                self.assertIn(elem,parser.ids)
        self.assertEqual(parser.ids["notice"][0][1].get("role"),"status")
        self.assertEqual(parser.ids["notice"][0][1].get("aria-live"),"polite")
        self.assertEqual(parser.ids["season-build-remedy"][0][1].get("role"),"status")
        self.assertIn('function setNotice(message, error=false)',js)
        self.assertIn('node.classList.toggle("error",Boolean(error))',js)
        self.assertIn('function seasonBuildRecoveryPlan(data,errorCode=null)',js)
        self.assertIn('function showSeasonEnvironmentBuild(data,forUserVariant=false)',js)
        self.assertIn('95% 비교 결과',html)
        self.assertIn('표준오차 (SEM)',html)
        self.assertIn('관측 1순위 · 전역 최적해 입증 아님',html)
        for text in (
            '.notice{\n padding:7px 11px;border:0;border-left:3px solid',
            '.notice.error{\n border-left-color:',
            '#view-optimizer .optimizer-environment-strip{\n border:0;border-left:2px solid',
            '#view-settings .panel+.panel{\n margin-top:25px;border-top:1px solid',
            '#view-settings .simc-update-panel{\n margin-top:20px;border-top:1px solid',
            '#view-settings #season-setup-details{\n border-top:1px solid',
            '#view-results .panel+.panel{\n  border-top:1px solid',
            '#view-results .metrics>div:first-child{\n  border-left:2px solid',
            '#view-results .alt-row+.alt-row{border-top:1px solid',
            '#view-results .alt-metric{\n  border:0!important',
            '#view-results .result-footer>div{\n  border:0!important',
            '#optimizer-form .gear-section .inline-item{\n min-height:',
            '#optimizer-form .fold,#optimizer-form .restore,\n#optimizer-form .condition-group,#optimizer-form .gear-row{\n border:0!important',
            '#optimizer-form input:not([type=checkbox]),\n#optimizer-form select,#optimizer-form textarea,\n#optimizer-form .choice-picker input[type=search]{\n border:1px solid transparent!important',
        ):
            with self.subTest(selector=text[:68]):
                self.assertIn(text,css)
        self.assertIn('SimC 세트 효과 원본의 빌드 정보를 확인하지 못했습니다.',js)
        self.assertIn('게임 빌드 불일치가 확정된 것은 아닙니다.',js)
        self.assertIn('기술 진단:',js)
        self.assertIn('V229_SET_BONUS_BUILD_OR_HEADER_MISMATCH',js)

    def test_notice_is_live_and_error_toggle_works_on_actual_js(self):
        node=shutil.which("node")
        if node is None:
            self.skipTest("node not installed")
        script=r"""
const assert=require('assert'),fs=require('fs');
const raw=fs.readFileSync(process.argv[1],'utf8');
const start=raw.indexOf('function setNotice(message, error=false) {');
const end=raw.indexOf('\nfunction option(value,label) {',start);
assert(start>=0&&end>start);
const classes=new Set();
const element={textContent:'',classList:{toggle(name,enabled){
  if(enabled) classes.add(name); else classes.delete(name);
}}};
const f=Function('$',raw.slice(start,end)+'\nreturn setNotice;')(
  id=>{assert.equal(id,'notice');return element});
f('구축 단계 조회 완료 · READY 여부는 별도 검증');
assert(element.textContent.includes('READY 여부'));
assert.equal(classes.has('error'),false);
f('실제 원본 검증 차단',true);
assert.equal(classes.has('error'),true);
f('조회 정상',false);
assert.equal(classes.has('error'),false);
assert.equal(element.textContent,'조회 정상');
"""
        result=subprocess.run([node,"-e",script,str(ROOT/"runner/webui/app.js")],
                 capture_output=True,text=True,encoding="utf8",errors="replace",
                 timeout=20,cwd=ROOT)
        self.assertEqual(result.returncode,0,result.stderr)


    def test_v649_passive_polling_cadence_keeps_native_and_restore_live(self):
        """Execute actual JS: idle GETs are throttled, active work is not."""
        node=shutil.which("node")
        if node is None:
            self.skipTest("node not installed")
        script=r"""
const assert=require('node:assert/strict'),fs=require('node:fs');
const source=fs.readFileSync(process.argv[1],'utf8');
function cut(a,b){
  const i=source.indexOf(a),j=source.indexOf(b,i);
  assert(i>=0&&j>i,'source function missing '+a);
  return source.slice(i,j);
}
const functions=
  cut('function renderProgress(data) {','\nfunction renderResult(payload) {')+
  '\n'+cut('function beginPolling() {','\nasync function loadRecentSessions() {')+
  '\n'+cut('function markSession(id) {','\nfunction buttonState(');
const nodes=new Map();
function $(id){
  if(!nodes.has(id))nodes.set(id,{
    value:'',hidden:false,textContent:'',style:{},options:[{value:''}]
  });
  return nodes.get(id);
}
const state={
  session:'a'.repeat(20),running:false,busy:false,pollBusy:false,
  pollTimer:null,pollFailures:0,nextPollAt:0,nextPassivePollAt:0,
  longrunCompleted:false,budgetPreviewDirty:false,longrunResultReady:false
};
let now=500000,tick=null,calls=0;
const f=Function('state',','number','showEnvironmentBuild',
  'longrunSavedResultDisplayable','buttonState','setInterval','clearInterval',
  'pollOnce','handlePollFailure','Date','refreshResultNavigation',
  'switchView','localStorage',functions+
  '\nreturn {renderProgress,beginPolling,markSession};');
const x=f(state,$,v=>String(v),()=>{},()=>false,
  active=>{state.running=active},
  callback=>{tick=callback;return 1},()=>{},
  ()=>{calls++;return Promise.resolve()},()=>{},
  {now:()=>now},()=>{},()=>{},{setItem(){}});
const report=(active,status)=>({
  enabled:true,active,result_ready:false,
  progress:{completed_jobs:3,planned_jobs:64,
            progress_percent:4.6875,worker:{status}}
});
const flush=()=>new Promise(done=>setImmediate(done));
(async()=>{
  x.renderProgress(report(false,'PAUSED_USER_CANCEL'));
  assert.equal(state.nextPassivePollAt,now+15000);
  x.beginPolling();
  tick();assert.equal(calls,0);
  now+=14999;tick();assert.equal(calls,0);
  now++;tick();assert.equal(calls,1);
  await flush();
  x.renderProgress(report(true,'RUNNING'));
  assert.equal(state.nextPassivePollAt,0);
  now+=1400;tick();assert.equal(calls,2);
  await flush();
  x.renderProgress(report(false,'QUEUED'));
  assert.equal(state.nextPassivePollAt,now+5000);
  now+=4999;tick();assert.equal(calls,2);
  now++;tick();assert.equal(calls,3);
  await flush();
  x.renderProgress(report(false,'PAUSED_ELAPSED_BUDGET'));
  assert(state.nextPassivePollAt>now);
  x.markSession('b'.repeat(20));
  assert.equal(state.nextPassivePollAt,0);
  now+=1400;tick();assert.equal(calls,4);
  await flush();
  state.nextPollAt=now+30000;
  x.renderProgress(report(true,'RUNNING'));
  now+=1400;tick();assert.equal(calls,4);
  now+=30000;tick();assert.equal(calls,5);
  await flush();
  console.log('V649_PASSIVE_POLL_ACTIVE_IDLE_RESTORE_AND_BACKOFF_PASS');
})().catch(err=>{console.error(err);process.exitCode=1});
"""
        result=subprocess.run(
            [node,"-e",script,str(ROOT/"runner/webui/app.js")],
            capture_output=True,text=True,encoding="utf8",errors="replace",
            timeout=20,cwd=ROOT)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn(
            "V649_PASSIVE_POLL_ACTIVE_IDLE_RESTORE_AND_BACKOFF_PASS",
            result.stdout)


if __name__=="__main__":
    unittest.main()
