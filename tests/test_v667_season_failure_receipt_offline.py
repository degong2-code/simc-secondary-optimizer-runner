"""v667: exact first failed season stage, safe public error type; no Native."""
import pathlib
import subprocess
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v113_local_web_api as web


class SeasonFailureReceipt(unittest.TestCase):
    def test_backend_generic_409_reports_type_and_fixed_stage_only(self):
        from fastapi.testclient import TestClient
        with tempfile.TemporaryDirectory() as folder:
            app=web.create_app(root=pathlib.Path(folder)/"runs",
                               token="local-only-testing")
            headers={"x-simc-local-token":"local-only-testing",
                     "origin":"http://127.0.0.1:8765"}
            with mock.patch.object(app.state.jobs,
                    "build_season_environment",
                    side_effect=RuntimeError("C:/Private/Secret/OAuth?value=42")) as runner:
                with TestClient(app,base_url="http://127.0.0.1:8765") as client:
                    resp=client.post("/api/v1/environment/season-build",
                        json={"game_build":"12.1.5.70961","target_ilevel":334},
                        headers=headers)
            self.assertEqual(resp.status_code,409,resp.text)
            detail=resp.json()["detail"]
            self.assertEqual(detail,{
                "code":"LOCAL_SESSION_PRECHECK_BLOCKED",
                "kind":"RuntimeError",
                "stage":"SEASON_ENVIRONMENT_BUILD"})
            self.assertNotIn("Secret",resp.text)
            self.assertNotIn("Private",resp.text)
            runner.assert_called_once()

    def test_known_block_code_stays_exact_and_no_new_authority(self):
        from fastapi.testclient import TestClient
        with tempfile.TemporaryDirectory() as folder:
            app=web.create_app(root=pathlib.Path(folder)/"runs",
                               token="local-only-testing")
            headers={"x-simc-local-token":"local-only-testing",
                     "origin":"http://127.0.0.1:8765"}
            with mock.patch.object(app.state.jobs,
                    "build_season_environment",
                    side_effect=web.environment_manifest.EnvironmentBlocked(
                        "V216_UNQUALIFIED_MULTIPLE_INSTALLED_FJ_VARIANTS_SELECT_EXACT_SHA")):
                with TestClient(app,base_url="http://127.0.0.1:8765") as client:
                    response=client.post("/api/v1/environment/season-build",
                        json={"game_build":"12.1.5.70961","target_ilevel":334},
                        headers=headers)
            self.assertEqual(response.status_code,422)
            self.assertEqual(response.json()["detail"],{
                "code":"V216_UNQUALIFIED_MULTIPLE_INSTALLED_FJ_VARIANTS_SELECT_EXACT_SHA"})

    def test_js_safe_error_kind_stale_pending_cleared_and_copy_enabled(self):
        js=(ROOT/"runner/webui/app.js").read_text("utf8")
        self.assertIn("error.safeKind=kind",js)
        self.assertIn("error.safeStage=stage",js)
        self.assertIn('error_kind:typeof err.safeKind',js)
        self.assertIn('failure_stage:err.safeStage',js)
        self.assertIn('http_status:Number.isInteger(err.httpStatus)',js)
        self.assertIn('$("season-build-pending").hidden=true;',js)
        self.assertIn('if(forUserVariant)$("user-variant-status").textContent=',js)
        self.assertIn('$("season-diagnostic-copy-btn").disabled=false;',js)
        self.assertIn('action:"diagnostic",button:"진단 영수증 복사"',js)
        self.assertIn('const multipleInstalledBudgets=',js)
        self.assertIn('kind:"selection",',js)
        self.assertIn("기존 자료를 보존",js)
        self.assertNotIn('console.log(error)',js)

    def test_exact_verified_fj_dropdown_is_read_only_and_never_guesses(self):
        ui=(ROOT/"runner/webui/app.js").read_text("utf8")
        html=(ROOT/"runner/webui/index.html").read_text("utf8")
        self.assertEqual(html.count('id="season-verified-budget"'),1)
        self.assertIn('id="season-verified-budget-group"',html)
        self.assertIn('const budgetSelector=typeof document',ui)
        # v676: multiple individually verified installed environments
        # remain separate exact-SHA choices; no cross-source equality Gate.
        self.assertIn('item.individually_verified===true',ui)
        self.assertIn('const candidate=option(item.installed_manifest_sha256,label)',ui)
        self.assertNotIn('candidate.disabled=duplicate',ui)
        self.assertIn('state.verifiedBaseFlaskInstalls.filter(x=>',ui)
        self.assertIn('x.installed_manifest_sha256===selectedBudget',ui)
        self.assertIn('field("season-verified-budget")!==selectedBudget',ui)
        self.assertIn('const exact=state.verifiedBaseFlaskInstalls.find(item=>',ui)
        self.assertIn('await chooseInstalledFlask();',ui)
        self.assertIn('if(exact.length!==1) {',ui)
        # The browser receives only read-only v212 receipts, not a fabricated
        # budget and never calls season-build on choosing one.
        self.assertNotIn('sessionStorage.setItem("v212_',ui)

    def test_actual_browser_api_rejects_no_raw_exception_body(self):
        node=shutil.which("node")
        if node is None:self.skipTest("Node not installed")
        js=r"""
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync(process.argv[1],'utf8');
const start=src.indexOf('async function api(path,');
const end=src.indexOf('function markSession',start);
assert(start>=0&&end>start);
const state={token:'local-only'};
const fetch=async()=>({ok:false,status:409,json:async()=>({
  detail:{code:'LOCAL_SESSION_PRECHECK_BLOCKED',
    kind:'RuntimeError',stage:'SEASON_ENVIRONMENT_BUILD',
    private_path:'C:/Secret'}})});
const api=Function('state','fetch',src.slice(start,end)+'\nreturn api;')(
  state,fetch);
(async()=>{
 try{
  await api('/api/v1/environment/season-build',{method:'POST',payload:{}});
  assert.fail('must reject');
 }catch(e){
  assert.strictEqual(e.message,'LOCAL_SESSION_PRECHECK_BLOCKED');
  assert.strictEqual(e.safeKind,'RuntimeError');
  assert.strictEqual(e.safeStage,'SEASON_ENVIRONMENT_BUILD');
  assert.strictEqual(e.httpStatus,409);
  assert(!JSON.stringify(e).includes('Secret'));
 }
 console.log('V667_SAFE_SEASON_HTTP_ERROR_PASS');
})().catch(e=>{console.error(e);process.exitCode=1});
"""
        result=subprocess.run([node,"-e",js,
                str(ROOT/"runner/webui/app.js")],
                cwd=ROOT,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn("V667_SAFE_SEASON_HTTP_ERROR_PASS",result.stdout)


if __name__=="__main__":unittest.main()
