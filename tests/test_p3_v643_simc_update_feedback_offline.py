"""v643: real browser update-check function always exposes local progress/error.
No real network, simulation, or season source. Node evaluates production JS.
"""
import pathlib
import shutil
import subprocess
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]


class SimCUpdaterFeedback(unittest.TestCase):
    def test_real_check_function_pending_success_error_and_busy_click(self):
        node=shutil.which("node")
        if not node:
            self.skipTest("Node unavailable")
        harness=r"""
const assert=require('assert'),fs=require('fs');
const raw=fs.readFileSync(process.argv[1],'utf8');
const a=raw.indexOf('async function checkSimcUpdater() {');
const b=raw.indexOf('\nasync function installSimcUpdater()',a);
assert(a>=0&&b>a);
const source=raw.slice(a,b);
function fixture(){
  const nodes={
    'simc-check-btn':{textContent:'공식 업데이트 확인',disabled:false},
    'simc-install-btn':{disabled:false},
    'simc-update-candidate':{textContent:'준비'}
  };
  let resolve,reject;
  const request=new Promise((yes,no)=>{resolve=yes;reject=no});
  const mockApi=(path,opts)=>{
    assert.equal(path,'/api/v1/simc-updates/check');
    assert.equal(opts.method,'POST');
    return request;
  };
  const make=Function('$','api','document',
    'let simcOffer=null;'+source+
    '\nreturn {checkSimcUpdater,getOffer:()=>simcOffer};');
  const impl=make(id=>nodes[id],mockApi,{
    createTextNode:text=>({textContent:text}),
    createElement:()=>({appendChild(){}})
  });
  return {nodes,resolve,reject,...impl};
}
(async()=>{
  let f=fixture();
  let task=f.checkSimcUpdater();
  assert.equal(f.nodes['simc-check-btn'].disabled,true);
  assert(f.nodes['simc-check-btn'].textContent.includes('조회 중'));
  assert(f.nodes['simc-update-candidate'].textContent.includes('확인 중'));
  assert.equal(f.nodes['simc-install-btn'].disabled,true);
  f.resolve({candidate:{filename:'simc-1215-01-win64-710c240.7z',
     revision_short:'710c240'},archive_extractor_available:true});
  await task;
  assert.equal(f.getOffer(),'simc-1215-01-win64-710c240.7z');
  assert.equal(f.nodes['simc-check-btn'].disabled,false);
  assert.equal(f.nodes['simc-check-btn'].textContent,'공식 업데이트 확인');
  assert.equal(f.nodes['simc-install-btn'].disabled,false);
  assert(f.nodes['simc-update-candidate'].textContent.includes('공식 Windows x64 후보'));

  f=fixture();task=f.checkSimcUpdater();
  f.reject(Error('HTTP_409'));
  await assert.rejects(task,/HTTP_409/);
  assert(f.nodes['simc-update-candidate'].textContent.includes('조회 실패'));
  assert(f.nodes['simc-update-candidate'].textContent.includes('HTTP_409'));
  assert.equal(f.nodes['simc-check-btn'].disabled,false);
  assert.equal(f.nodes['simc-install-btn'].disabled,true);
  assert.equal(f.getOffer(),null);

  const event=raw.indexOf('$("simc-check-btn").addEventListener("click",');
  const following=raw.slice(event,event+450);
  assert(event>=0&&following.includes('if(state.busy)'));
  assert(following.includes('다른 요청을 처리 중'));
})().catch(e=>{console.error(e);process.exitCode=1});
"""
        p=subprocess.run([node,"-e",harness,
            str(ROOT/"runner/webui/app.js")],cwd=ROOT,
            capture_output=True,text=True,timeout=20)
        self.assertEqual(p.returncode,0,p.stderr)


if __name__=="__main__":
    unittest.main()
