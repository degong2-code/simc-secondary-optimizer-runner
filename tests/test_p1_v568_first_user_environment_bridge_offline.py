"""v568: first-user browser season bridge, offline only, no actual Native/HTTP."""
import pathlib,shutil,subprocess,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class FirstUserBridge(unittest.TestCase):
    def test_static_start_source_and_user_consent_boundary(self):
        js=(ROOT/"runner/webui/app.js").read_text("utf8")
        html=(ROOT/"runner/webui/index.html").read_text("utf8")
        self.assertIn('id="season-auto-core" type="checkbox" checked',html)
        self.assertIn("async function prepareSeasonBeforeOptimizerStart()",js)
        event=js.index('$("start-btn").addEventListener("click",')
        self.assertLess(js.index("if(await prepareSeasonBeforeOptimizerStart())return;",event),
                        js.index('api("/api/v1/longrun/start"',event))
        self.assertIn('if(report===null)return true;',js)
        self.assertIn('return report;',js)
        self.assertIn('(!needsEnvironment&&!hasRequiredSelections())',js)
        self.assertNotIn("prepareSeasonBeforeOptimizerStart()",js[
            js.index("async function initialize()"):])
    def test_actual_js_helper_ready_reuse_pending_cancel_no_dps(self):
        node=shutil.which("node")
        if node is None:self.skipTest("node unavailable")
        harness=r"""
const fs=require("fs"), assert=require("assert");
const raw=fs.readFileSync(process.argv[1],"utf8");
const a=raw.indexOf("function optimizerNeedsSeasonPreparation()");
const b=raw.indexOf("\nfunction buildRequest()",a);
assert(a>=0 && b>a);
// The real UI now shares nonthrowing ilvl validation between button state
// and first-click preparation; load that actual helper into this isolated test.
const helperA=raw.indexOf("function validTargetIlevel()");
const helperB=raw.indexOf("\nfunction hasRequiredSelections()",helperA);
assert(helperA>=0 && helperB>helperA);
const src=raw.slice(helperA,helperB)+"\n"+raw.slice(a,b);
assert(!src.includes("/api/v1/longrun/start"));
const factory=Function("field","valueInt","state",
  "verifiedInstalledGearScopeMatchesRun","buildSeasonEnvironment",
  "switchView","setNotice",src+
  "\nreturn {optimizerNeedsSeasonPreparation,prepareSeasonBeforeOptimizerStart};");
const good={web_environment_scope:{environment_ready:true,environment_installed:true}};
const pending={web_environment_scope:{environment_ready:false,environment_installed:false}};
(async()=>{
  let calls=0,views=[],notices=[],response=good,linkReady=true;
  const state={verifiedInstalledBuildFromThisPage:null,ready:false};
  const f=factory(id=>id==="season-game-build"?"":"334",
    ()=>334,state,
    (build,ilvl)=>state.ready && build==="12.1.5.70783" && ilvl===334,
    async()=>{calls++;if(linkReady&&response===good){
      state.ready=true;state.verifiedInstalledBuildFromThisPage="12.1.5.70783";
    }return response;},
    v=>views.push(v),v=>notices.push(v));
  assert.strictEqual(f.optimizerNeedsSeasonPreparation(),true);
  assert.strictEqual(await f.prepareSeasonBeforeOptimizerStart(),true);
  assert.strictEqual(calls,1);assert.strictEqual(views.at(-1),"optimizer");
  assert.strictEqual(await f.prepareSeasonBeforeOptimizerStart(),false);
  assert.strictEqual(calls,1,"same installed build must not rebuild");
  state.ready=false;state.verifiedInstalledBuildFromThisPage=null;
  response=pending;linkReady=false;
  await assert.rejects(f.prepareSeasonBeforeOptimizerStart(),
    /SEASON_INITIAL_USER_BUILD_READY_REQUIRED/);
  assert.strictEqual(views.at(-1),"settings");
  response=good;
  await assert.rejects(f.prepareSeasonBeforeOptimizerStart(),
    /SEASON_INITIAL_USER_BUILD_READY_REQUIRED/);
  response=null;
  assert.strictEqual(await f.prepareSeasonBeforeOptimizerStart(),true);
  assert.strictEqual(calls,4);
  assert.strictEqual(notices.length,1);
})().catch(e=>{console.error(e);process.exitCode=1;});
"""
        p=subprocess.run([node,"-e",harness,str(ROOT/"runner/webui/app.js")],
                         cwd=ROOT,capture_output=True,text=True,timeout=15)
        self.assertEqual(p.returncode,0,p.stderr)
    def test_real_start_handler_checks_simc_before_any_season_or_dps_work(self):
        """Execute production click handler: invalid SimC cannot spend API/Native."""
        node=shutil.which("node")
        if node is None:self.skipTest("node unavailable")
        harness=r"""
const fs=require("fs"),assert=require("assert");
const raw=fs.readFileSync(process.argv[1],"utf8");
const a=raw.indexOf('$("start-btn").addEventListener("click",');
const b=raw.indexOf('\n  $("resume-btn").addEventListener("click",',a);
assert(a>=0&&b>a);
const source=raw.slice(a,b);
assert(source.indexOf("checkValidity()")<
       source.indexOf("if(await prepareSeasonBeforeOptimizerStart())return;"));
function run(binaryOK,revisionOK,needsSeason) {
  let handler=null;
  const calls={season:0,dps:0,focus:null,view:null,reported:0};
  const fields={
    binary:{checkValidity:()=>binaryOK,
      reportValidity:()=>{calls.reported++;return binaryOK;},
      focus:()=>{calls.focus="binary";}},
    revision:{checkValidity:()=>revisionOK,
      reportValidity:()=>{calls.reported++;return revisionOK;},
      focus:()=>{calls.focus="revision";}},
    "simc-technical-panel":{open:false},
    "filled-result":{hidden:false},"empty-result":{hidden:true},
    "start-btn":{addEventListener:(event,fn)=>{handler=fn;}}
  };
  const $=id=>fields[id];
  const params={
    $,withBusy:cb=>cb(),manualFinalTOrNull:()=>null,
    prepareSeasonBeforeOptimizerStart:async()=>{calls.season++;return needsSeason;},
    switchView:name=>{calls.view=name;},window:{confirm:()=>true},
    api:async()=>{calls.dps++;return {session_id:"mock-only"};},
    buildRequest:()=>({}),markSession:()=>{},setNotice:()=>{},pollOnce:async()=>{}
  };
  new Function(...Object.keys(params),source)(...Object.values(params));
  return {calls,invoke:()=>handler()};
}
(async()=>{
  let t=run(false,true,false);
  await assert.rejects(t.invoke(),/SimulationCraft/);
  assert.deepStrictEqual([t.calls.season,t.calls.dps,t.calls.view,t.calls.focus],
                         [0,0,"settings","binary"]);
  t=run(true,false,false);
  await assert.rejects(t.invoke(),/SimulationCraft/);
  assert.deepStrictEqual([t.calls.season,t.calls.dps,t.calls.focus],
                         [0,0,"revision"]);
  t=run(true,true,true);
  await t.invoke();assert.equal(t.calls.season,1);assert.equal(t.calls.dps,0);
  t=run(true,true,false);
  await t.invoke();assert.equal(t.calls.season,1);assert.equal(t.calls.dps,1);
})().catch(err=>{console.error(err);process.exitCode=1;});
"""
        p=subprocess.run([node,"-e",harness,str(ROOT/"runner/webui/app.js")],
                         cwd=ROOT,capture_output=True,text=True,timeout=15)
        self.assertEqual(p.returncode,0,p.stderr)

if __name__=="__main__":unittest.main()
