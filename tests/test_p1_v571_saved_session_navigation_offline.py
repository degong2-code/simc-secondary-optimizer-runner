"""v571: previously saved local sessions unlock their own restore tab.
Offline real JS helper extraction, zero HTTP, zero SimC and zero Native.
"""
from __future__ import annotations
import pathlib
import shutil
import subprocess
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]

class RestoreNavigation(unittest.TestCase):
    def test_real_js_saved_session_navigation(self):
        node=shutil.which("node")
        if node is None:self.skipTest("node is not installed")
        source=r"""
const fs=require("fs"),assert=require("assert");
const raw=fs.readFileSync(process.argv[1],"utf8");
const first=raw.indexOf("let currentView=\"optimizer\";");
const end=raw.indexOf("\nfunction updateManualTMode()",first);
assert(first>=0&&end>first);
const nav=raw.slice(first,end);
assert(nav.includes("function resultsAvailable()"));
const items={"results-nav-btn":{hidden:true},
             "recent-session-id":{options:[{value:""}]}};
const fakePanel={dataset:{viewPanel:"results"},hidden:true};
const fakeButton={
  dataset:{view:"results"},classList:{toggle(){}},
  setAttribute(){},removeAttribute(){}
};
const document={querySelectorAll(x){
  if(x==="[data-view-panel]")return [fakePanel];
  if(x==="[data-view]")return [fakeButton];
  throw Error("UNEXPECTED_DOCUMENT_QUERY");
}};
let scrolls=0;
const window={scrollTo(){scrolls++;}};
const state={session:null};
const api=Function("state","$","document","window",nav+
  "\nreturn {resultsAvailable,switchView,refreshResultNavigation,getView:()=>currentView};")(
  state,id=>items[id],document,window);
assert.strictEqual(api.resultsAvailable(),false);
api.refreshResultNavigation();
assert.strictEqual(items["results-nav-btn"].hidden,true);
api.switchView("results");
assert.strictEqual(api.getView(),"optimizer");
assert.strictEqual(scrolls,0);
items["recent-session-id"].options.push({value:"0123456789abcdef0123"});
assert.strictEqual(api.resultsAvailable(),true);
api.refreshResultNavigation();
assert.strictEqual(items["results-nav-btn"].hidden,false);
api.switchView("results");
assert.strictEqual(api.getView(),"results");
assert.strictEqual(fakePanel.hidden,false);
assert.strictEqual(state.session,null,"navigation must not promote saved ID");
assert.strictEqual(scrolls,1);
items["recent-session-id"].options=[{value:""}];
api.refreshResultNavigation();
assert.strictEqual(items["results-nav-btn"].hidden,true);
state.session="0123456789abcdef0123";
api.refreshResultNavigation();
assert.strictEqual(items["results-nav-btn"].hidden,false);
assert.strictEqual(api.resultsAvailable(),true);
"""
        result=subprocess.run([node,"-e",source,str(ROOT/"runner/webui/app.js")],
            cwd=ROOT,capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr)

if __name__=="__main__":
    unittest.main()
