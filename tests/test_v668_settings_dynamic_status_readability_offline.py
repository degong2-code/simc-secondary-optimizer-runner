"""v668: environment/settings dynamic values need visibly truthful labels.

Presentation-only. No new SimC, source lookup, cache eviction or Native DPS.
"""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]


class SettingsStatusReadability(unittest.TestCase):
    def test_settings_status_markup_and_typographic_hierarchy(self):
        html=(ROOT/"runner/webui/index.html").read_text("utf8")
        css=(ROOT/"runner/webui/styles.css").read_text("utf8")
        self.assertEqual(html.count('id="simc-connection-status-facts"'),1)
        self.assertEqual(html.count('id="season-environment-status-facts"'),1)
        self.assertIn('role="group" aria-label="SimC 연결 검증 결과"',html)
        self.assertIn('role="group" aria-label="시즌 환경 확인 결과"',html)
        self.assertLess(html.index('id="season-environment-status-facts"'),
                        html.index('id="season-build-stage"'))
        self.assertLess(html.index('id="simc-connection-status-facts"'),
                        html.index('id="simc-connection-status"'))
        for token in (
           ".settings-status-head",".settings-status-label",
           ".settings-status-value",".settings-status-rows",
           '.settings-status-facts[data-state="ok"]',
           '.settings-status-facts[data-state="error"]',
           '.settings-status-facts[data-state="pending"]',
           ".settings-status-facts[hidden]",
           ".settings-live-status",
           "@media(max-width:580px)"
        ):
            self.assertIn(token,css)

    def test_dynamic_result_states_are_grounded_and_no_html_injection(self):
        node=shutil.which("node")
        if not node:self.skipTest("Node unavailable")
        harness=r"""
const fs=require('fs'),assert=require('assert');
const raw=fs.readFileSync(process.argv[1],'utf8');
const from=(a,b)=>{
  const i=raw.indexOf(a),j=raw.indexOf(b,i);
  assert(i>=0&&j>i,"Source fragment missing: "+a);
  return raw.slice(i,j);
};
const code=
 from('function renderSettingsStatusFacts(', 'function showSeasonEnvironmentBuild(')+
 from('function displaySimcConnectionFacts(', '// Confirm a manual SimC link explicitly;');
class Elem {
  constructor(tag){this.tag=tag;this.children=[];this.dataset={};this.hidden=true;
    this.className='';this._text='';}
  append(...children){this.children.push(...children);}
  replaceChildren(...children){this.children=children;this._text='';}
  set textContent(value){this._text=String(value);this.children=[];}
  get textContent(){return this._text+this.children.map(x=>x.textContent).join(' ');}
}
const roots={
 'simc-connection-status-facts':new Elem('div'),
 'season-environment-status-facts':new Elem('div')
};
const document={
 createElement: tag=>new Elem(tag),
 getElementById: id=>roots[id]||null
};
const funcs=Function('document',code+
 '\nreturn {displaySeasonEnvironmentFacts,displaySeasonEnvironmentAttempt,displaySimcConnectionFacts,renderSettingsStatusFacts};')(document);
const simc=roots['simc-connection-status-facts'];
const season=roots['season-environment-status-facts'];
const saved={
 revision:'710c240',observed_game_build:'12.1.5.70575',
 revision_identity:'USER_ENTERED_REVISION_NOT_ATTESTED'
};
funcs.displaySimcConnectionFacts({saved,verified_now:false},true);
assert.strictEqual(simc.dataset.state,'pending');
assert(simc.textContent.includes('현재 실행 검증 전'));
assert(simc.textContent.includes('저장 당시 게임 빌드'));
assert(simc.textContent.includes('12.1.5.70575'));
assert(!simc.textContent.includes('CLI 실행 확인 · 설정 저장 완료'));
funcs.displaySimcConnectionFacts({saved,verified_now:true},false);
assert.strictEqual(simc.dataset.state,'ok');
assert(simc.textContent.includes('SimC CLI 실행 확인'));
assert(simc.textContent.includes('입력값·파일명 확인 수준'));
assert(simc.textContent.includes('현재 게임·시즌 일치'));
assert(simc.textContent.includes('별도 원본 검증 필요'));
assert(!simc.textContent.includes('CLI 출력과 일치'));
funcs.displaySimcConnectionFacts({saved:{...saved,
 revision_identity:'SIMC_CLI_PRINTED_REVISION_VERIFIED'},verified_now:true},false);
assert(simc.textContent.includes('당시 CLI 출력과 일치'));
funcs.displaySimcConnectionFacts({saved:null},true);
assert.strictEqual(simc.dataset.state,'pending');
assert(simc.textContent.includes('연결 정보 없음'));

const full={status:'VERIFIED_INSTALLED_SAME_SEASON_SOURCE_REUSED',
 G:2850,J:92,F:165,O:0,T:3107,
 web_environment_scope:{
  environment_ready:true,environment_installed:true,
  game_build:'12.1.5.70961',target_ilevel:334
 }};
funcs.displaySeasonEnvironmentFacts(full,false);
assert.strictEqual(season.dataset.state,'ok');
assert(season.textContent.includes('기존 검증 시즌 환경 재사용'));
assert(season.textContent.includes('3,107 rating'));
assert(season.textContent.includes('G 2850 · J 92 · F 165 · O 0'));
const pending={...full,web_environment_scope:{...full.web_environment_scope,
 environment_ready:false}};
funcs.displaySeasonEnvironmentFacts(pending);
assert.strictEqual(season.dataset.state,'pending');
assert(season.textContent.includes('정식 확인 대기'));
assert(!season.textContent.includes('3,107 rating'));
funcs.displaySeasonEnvironmentAttempt('error','시즌 환경 요청 실패',
 '12.1.5.70961',334,'LOCAL_SESSION_PRECHECK_BLOCKED');
assert.strictEqual(season.dataset.state,'error');
assert(season.textContent.includes('READY 아님'));
assert(season.textContent.includes('LOCAL_SESSION_PRECHECK_BLOCKED'));
funcs.displaySeasonEnvironmentAttempt('pending','시즌 환경 확인 중',
 '12.1.5.70961',334);
assert.strictEqual(season.dataset.state,'pending');
assert(season.textContent.includes('서버 응답 확인 중'));
funcs.renderSettingsStatusFacts('season-environment-status-facts','ok',
 '<b>fake</b>',[{label:'이름',value:'<img onerror=x>'}]);
assert(season.textContent.includes('<b>fake</b>'));
assert(season.textContent.includes('<img onerror=x>'));
assert(season.children.every(x=>x.tag==='p'||x.tag==='div'));
console.log('V668_TRUTHFUL_STATUS_VALUES_PASS');
"""
        result=subprocess.run([node,"-e",harness,
                    str(ROOT/"runner/webui/app.js")],
                    cwd=ROOT,text=True,capture_output=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('V668_TRUTHFUL_STATUS_VALUES_PASS',result.stdout)

    def test_state_change_hooks_distinguish_verified_from_loading_and_failure(self):
        js=(ROOT/"runner/webui/app.js").read_text("utf8")
        self.assertIn('displaySeasonEnvironmentFacts(data,forUserVariant)',js)
        self.assertIn('displaySeasonEnvironmentAttempt("pending","시즌 환경 확인 중"',js)
        self.assertIn('displaySeasonEnvironmentAttempt("error","시즌 환경 요청 실패"',js)
        self.assertIn('displaySimcConnectionFacts(result,restored)',js)
        self.assertIn('renderSettingsStatusFacts("simc-connection-status-facts","pending"',js)
        self.assertIn('renderSettingsStatusFacts("simc-connection-status-facts","error"',js)
        self.assertIn('const justVerified=result.verified_now===true&&!restored;',js)


if __name__=="__main__":unittest.main()
