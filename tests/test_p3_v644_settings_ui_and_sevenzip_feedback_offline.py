"""P3 v644: settings style and live JS 7-Zip/season diagnostic UI contract.

CSS/HTML-only changes must not disrupt IDs or results/optimizer semantics.
No external HTTPS, Native or real archive unpacking.
"""
import pathlib
import re
import shutil
import subprocess
import unittest
from html.parser import HTMLParser

ROOT=pathlib.Path(__file__).resolve().parents[1]

class IDs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]
    def handle_starttag(self,tag,attrs):
        values=dict(attrs)
        if values.get("id"):self.ids.append(values["id"])

class SettingsUI(unittest.TestCase):
    def test_existing_dom_bindings_and_settings_editorial_layout(self):
        html=(ROOT/"runner/webui/index.html").read_text("utf8")
        css=(ROOT/"runner/webui/styles.css").read_text("utf8")
        js=(ROOT/"runner/webui/app.js").read_text("utf8")
        parser=IDs();parser.feed(html)
        self.assertEqual(len(parser.ids),len(set(parser.ids)),
                         "Duplicate element IDs can break existing JS handlers")
        for id in ("view-settings","view-results","season-build-btn",
                   "season-build-running","season-build-summary",
                   "season-build-pending","simc-technical-panel",
                   "simc-update-panel","binary","revision",
                   "simc-check-btn","simc-install-btn","simc-rollback-btn",
                   "simc-local-archive","simc-install-local-btn",
                   "simc-update-candidate","simc-local-install-status",
                   "source-credentials-status","results-nav-btn",
                   "resume-btn","cancel-btn","recent-refresh-btn","dps",
                   "sem","conf95","budget","stat-bars","alt-list"):
            with self.subTest(id=id):self.assertIn(id,parser.ids)
        self.assertIn('id="simc-local-install-status" class="hint settings-live-status" role="status" aria-live="polite"',html)
        self.assertIn('href="https://www.7-zip.org/download.html"',html)
        self.assertLess(html.index('id="simc-check-btn"'),
                        html.index('id="simc-update-candidate"'))
        self.assertLess(html.index('id="simc-install-local-btn"'),
                        html.index('id="simc-local-install-status"'))
        for token in (
             '#view-settings .panel{\n  border:0!important',
             '#view-settings .section-head{\n  margin:0 0 15px;border:0',
             '#view-settings .fold{\n  border:0!important',
             '#view-settings .fold[open]>summary{\n  border:0!important',
             '.simc-update-actions .btn{flex:0 1 auto',
             '#view-settings .btn{\n  border:1px solid',
             '#view-settings .field input',
             '#view-settings :is(.two,.season-build-fields){grid-template-columns:minmax(0,1fr)}',
             '#view-results .panel{',
             '#optimizer-form>.profile-panel'):
            self.assertIn(token,css)
        for handler in ('$("simc-install-local-btn").addEventListener("click",',
                        '$("simc-check-btn").addEventListener("click",',
                        '$("season-build-btn").addEventListener("click",'):
            self.assertIn(handler,js)

    def test_actual_local_install_js_reports_missing_7zip_next_to_action(self):
        node=shutil.which("node")
        if not node:self.skipTest("node unavailable")
        harness=r"""
const assert=require('assert'),fs=require('fs');
const raw=fs.readFileSync(process.argv[1],'utf8');
const a=raw.indexOf('async function installLocalSimcUpdater() {');
const b=raw.indexOf('\nasync function rollbackSimcUpdater()',a);
assert(a>=0&&b>a);
const source=raw.slice(a,b);
function fixture(apiResult,path='C:\\\\Downloads\\\\simc-1210.01.0d19401-win64.7z'){
 const nodes={
  'simc-local-install-status':{textContent:'초기'},
  'simc-install-btn':{disabled:true},
  'simc-update-candidate':{textContent:''}
 };
 const calls=[];
 const api=(route,args)=>{
  calls.push({route,args});
  return typeof apiResult==='function'?apiResult():apiResult;
 };
 const maker=Function('$','field','api','window',
    'rememberPreManagedBinary','displaySimcUpdater','applyManagedSimc',
    'setNotice',
    'let simcOffer=null;'+source+'\nreturn installLocalSimcUpdater;');
 const fn=maker(id=>(nodes[id]??={textContent:''}),()=>path,api,
   {confirm:()=>true},()=>{},()=>{},()=>{},()=>{});
 return {fn,nodes,calls};
}
(async()=>{
 let f=fixture(Promise.reject(Error('SEVEN_ZIP_REQUIRED')));
 await assert.rejects(f.fn(),/SEVEN_ZIP_REQUIRED/);
 assert.equal(f.calls.length,1);
 assert.equal(f.calls[0].route,'/api/v1/simc-updates/install-local');
 assert.equal(f.calls[0].args.payload.archive_path,'C:\\\\Downloads\\\\simc-1210.01.0d19401-win64.7z');
 assert(f.nodes['simc-local-install-status'].textContent.includes('7z.exe'));
 assert(f.nodes['simc-local-install-status'].textContent.includes('PATH에 7z.exe'));
 f=fixture(Promise.resolve({active_binary:'C:/managed/simc.exe',installed:{revision_short:'abc1234'}}));
 await f.fn();
 assert(f.nodes['simc-local-install-status'].textContent.includes('설치 및 기동 검증 완료'));
 f=fixture(Promise.resolve({}),'/tmp/unrelated.zip');
 await assert.rejects(f.fn(),/\.7z/);
 assert.equal(f.calls.length,0);
})().catch(e=>{console.error(e);process.exitCode=1});
"""
        p=subprocess.run([node,"-e",harness,str(ROOT/"runner/webui/app.js")],
                         cwd=ROOT,text=True,capture_output=True,timeout=20)
        self.assertEqual(p.returncode,0,p.stderr)

    def test_managed_source_revision_uses_full_40_sha_when_available(self):
        """No short-GitHub-commit lookup for receipt-backed managed SimC."""
        js=(ROOT/"runner/webui/app.js").read_text("utf8")
        self.assertIn("function managedFullSimcSourceRevision(data) {",js)
        self.assertIn("installed.source_revision_full,short=installed.revision_short",js)
        self.assertIn("/^[a-f0-9]{40}$/.test(full)",js)
        self.assertIn("full.startsWith(short)?full:null;",js)
        self.assertIn("managedFullSimcSourceRevision(data)||",js)
        self.assertIn("data.installed.revision_short;",js)
        self.assertIn("field(\"binary\")===status.active_binary",js)
        self.assertIn("field(\"revision\")===status.installed.revision_short",js)
        self.assertIn("관리 자체 빌드의 전체 소스 Git SHA",js)
        self.assertIn("저장하려면 ‘SimC 연결 확인·저장’",js)
        self.assertLess(js.index("function managedFullSimcSourceRevision(data) {"),
                        js.index("function applyManagedSimc(data) {"))
    def test_real_compiler_missing_diagnostic_is_collapsed_and_explained(self):
        js=(ROOT/"runner/webui/app.js").read_text("utf8")
        html=(ROOT/"runner/webui/index.html").read_text("utf8")
        self.assertIn('const sourceNames={',js)
        self.assertIn('원본 컴파일에 필요한 파일 "+missing.length+"종 미확정',js)
        self.assertIn('미완료 코드는 연쇄 진단이며',js)
        self.assertIn('원본 단계 진단 보기 · 연쇄 미완료 항목',html)
        self.assertIn('class="fold" hidden><summary>원본 단계 진단 보기',html)
        self.assertIn('technicalPanel.hidden=false;',js)
        self.assertIn('list.appendChild(item);',js)

if __name__=="__main__":unittest.main()
