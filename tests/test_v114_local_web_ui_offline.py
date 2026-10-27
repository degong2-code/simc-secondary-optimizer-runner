"""P1-WEB-2 static HTML/UI/HTTP regression. Strictly no SimC Native calls."""
from html.parser import HTMLParser
import pathlib,sys,unittest
from fastapi.testclient import TestClient
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v113_local_web_api as api

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=set();self.scripts=[];self.links=[]
        self.forms=0
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if "id" in d:
            if d["id"] in self.ids:raise AssertionError("DUPLICATE_ID "+d["id"])
            self.ids.add(d["id"])
        if tag=="script":self.scripts.append(d)
        if tag=="link":self.links.append(d)
        if tag=="form":self.forms+=1

class RealHTTPPageOffline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client=TestClient(api.create_app(token="ui-offline-token"),
              base_url="http://127.0.0.1:8765")
        cls.head={"x-simc-local-token":"ui-offline-token",
                  "origin":"http://127.0.0.1:8765"}

    def test_browser_root_local_static_no_auth_but_guarded_by_host_and_origin(self):
        result=self.client.get("/")
        self.assertEqual(result.status_code,200)
        self.assertIn("text/html",result.headers["content-type"])
        self.assertIn("no-store",result.headers["cache-control"])
        self.assertIn("script-src 'self'",result.headers["content-security-policy"])
        self.assertEqual(result.headers["x-frame-options"],"DENY")
        self.assertEqual(result.headers["x-content-type-options"],"nosniff")
        page=PageParser();page.feed(result.text)
        self.assertEqual(page.forms,1)
        self.assertIn("특수장비 최대 8개 · 장식 최대 2개",result.text)
        self.assertEqual(page.scripts,[{"src":"/assets/app.js","defer":None}])
        self.assertEqual(page.links,[{"rel":"stylesheet","href":"/assets/styles.css"}])
        required=("optimizer-form","spec","race","talents","trinket1",
          "trinket2","ilevel","final_T","targets","duration",
          "raid_buffs","oil_main","oil_off","binary","revision","static_cache",
          "special-rows","crafted-rows","food","potion","augmentation",
          "diamond","omnium","plan-btn","start-btn","resume-btn","cache-btn",
          "cancel-btn","restore-btn","restore-id","notice","session-id",
          "stage-text","progress-label","progress-pct","progress-bar",
          "filled-result","empty-result","dps","sem","budget","stat-bars",
          "conf95","alt-count","alt-list")
        self.assertTrue(set(required)<=page.ids,set(required)-page.ids)
        for path in ("/","/assets/app.js","/assets/styles.css"):
            self.assertEqual(self.client.get(path,headers={"host":"evil.test:8765"}).status_code,403)
            self.assertEqual(self.client.get(path,headers={"origin":"https://evil.test"}).status_code,403)

    def test_css_and_javascript_are_exact_local_assets_no_external_framework(self):
        css=self.client.get("/assets/styles.css")
        js=self.client.get("/assets/app.js")
        self.assertEqual(css.status_code,200)
        self.assertEqual(js.status_code,200)
        self.assertIn("text/css",css.headers["content-type"])
        self.assertTrue(js.headers["content-type"].startswith(("text/javascript","application/javascript")))
        self.assertIn("P1-WEB-2",js.text)
        self.assertNotIn("innerHTML",js.text)
        self.assertNotIn("eval(",js.text)
        self.assertNotIn("window.open(",js.text)
        self.assertNotIn("@import",css.text)
        self.assertNotIn("https://",css.text)
        self.assertIn('"/api/v1/bootstrap"',js.text)
        self.assertIn('"/api/v1/options"',js.text)
        self.assertIn('localStorage.setItem("simc_secondary_session_id"',js.text)
        self.assertIn("cache-only",js.text)
        self.assertIn("result",js.text)
        self.assertIn('"/api/v1/sessions/start"',js.text)
        self.assertIn('window.confirm("이 PC에서 실제 SimC',js.text)
        self.assertEqual(self.client.get("/assets/missing.js").status_code,403)

    def test_special_effect_gear_has_eight_dynamic_rows_not_two(self):
        js=self.client.get("/assets/app.js").text
        self.assertIn('const limit=isSpecial?8:2;',js)
        self.assertIn('add.textContent="+ 특수효과 장비 추가"',js)
        self.assertIn('if(isSpecial&&i>=2)row.hidden=true',js)
        self.assertIn('group==="special_items"?8:2',js)
        self.assertIn('for (let i=0;i<limit;i++)',js)

    def test_missing_session_returns_read_only_404_with_precise_code(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)/"runs"
            client=TestClient(api.create_app(root=root,token="offline"),
                base_url="http://127.0.0.1:8765")
            r=client.get("/api/v1/sessions/abca493c00d6ee2599f1/status",
                headers={"x-simc-local-token":"offline"})
            self.assertEqual(r.status_code,404)
            self.assertEqual(r.json()["detail"]["code"],"SESSION_NOT_FOUND")
            self.assertFalse(root.exists())

    def test_missing_session_is_not_saved_as_verified_and_polling_backs_off(self):
        js=self.client.get("/assets/app.js").text
        self.assertIn('fillSessionInputs(inputs);\n  markSession(id);',js)
        self.assertIn('api("/api/v1/sessions/"+id+"/inputs")',js)
        self.assertIn('function fillGearRows(nodeId, entries)',js)
        self.assertIn('fillGearRows("special-rows",u.special_items||[])',js)
        self.assertIn('fillGearRows("crafted-rows",u.embellishments||[])',js)
        self.assertIn('$("binary").value=payload.binary;',js)
        self.assertIn('$("revision").value=payload.revision;',js)
        self.assertIn('$("static_cache").value=payload.static_cache??"";',js)
        self.assertNotIn('localStorage.setItem("simc_binary',js)
        self.assertIn('if(err.message==="SESSION_NOT_FOUND")',js)
        self.assertIn('localStorage.removeItem("simc_secondary_session_id")',js)
        self.assertIn('return; // Stop polling this missing ID.',js)
        self.assertIn('state.nextPollAt=Date.now()+Math.min(30000',js)
        self.assertIn('state.pollBusy=true;',js)
        self.assertIn('setNotice("기존 세션·입력 복원 성공',js)

    def test_session_inputs_restore_requires_token_and_is_read_only(self):
        import json,tempfile
        with tempfile.TemporaryDirectory() as td:
            home=pathlib.Path(td)
            root=home/"runs"
            binary=home/"simc.exe"
            binary.write_bytes(b"fake native, never executed")
            controls=api.sessions.standard_controls(("paladin","retribution"))
            user=api.sessions.user_scenario(controls)
            folder=api.sessions.store_session(user,root,binary,"7bc1071")
            generated=folder/"generated"
            generated.mkdir()
            manifest={"native_binary":str(binary),"native_revision":"7bc1071",
                      "static_cache_json":None}
            (generated/"manifest.json").write_text(json.dumps(manifest),
                                                   encoding="utf8")
            client=TestClient(api.create_app(root=root,token="local-form"),
                base_url="http://127.0.0.1:8765")
            url="/api/v1/sessions/"+folder.name+"/inputs"
            self.assertEqual(client.get(url).status_code,403)
            resp=client.get(url,headers={"x-simc-local-token":"local-form"})
            self.assertEqual(resp.status_code,200)
            payload=resp.json()
            self.assertEqual(payload["user"],user)
            self.assertEqual(payload["binary"],str(binary))
            self.assertEqual(payload["revision"],"7bc1071")
            self.assertIsNone(payload["static_cache"])
            self.assertIs(payload["native_called"],False)
            self.assertFalse((folder/"V106_WORKER_STATE.json").exists())
            self.assertFalse((folder/"generated"/"simc_results").exists())
            self.assertFalse((folder/"V106_WORKER.log").exists())

    def test_session_input_manifest_drift_fails_closed(self):
        import json,tempfile
        with tempfile.TemporaryDirectory() as td:
            home=pathlib.Path(td)
            binary=home/"simc.exe"
            binary.write_bytes(b"fake")
            user=api.sessions.user_scenario(
                api.sessions.standard_controls(("paladin","retribution")))
            folder=api.sessions.store_session(user,home/"runs",binary,"7bc1071")
            generated=folder/"generated"
            generated.mkdir()
            (generated/"manifest.json").write_text(json.dumps({
                "native_binary":str(binary),"native_revision":"wrong",
                "static_cache_json":None}),encoding="utf8")
            client=TestClient(api.create_app(root=home/"runs",token="drift"),
                base_url="http://127.0.0.1:8765")
            resp=client.get("/api/v1/sessions/"+folder.name+"/inputs",
                            headers={"x-simc-local-token":"drift"})
            self.assertEqual(resp.status_code,422)
            self.assertEqual(resp.json()["detail"]["code"],
                             "SESSION_INPUTS_OR_MANIFEST_DRIFT")

    def test_source_observed_options_are_official_contract_not_user_invented(self):
        self.assertEqual(self.client.get("/api/v1/options").status_code,403)
        r=self.client.get("/api/v1/options",headers=self.head)
        self.assertEqual(r.status_code,200)
        options=r.json()
        self.assertEqual(set(options),{"food","potion","augmentation","diamond_id","omnium_talents"})
        self.assertEqual(options["diamond_id"],[0,240967,240983])
        self.assertEqual(len(options["omnium_talents"]),7)
        self.assertEqual(options["food"][0],"source_default")
        self.assertEqual(options["augmentation"][0],"source_default")
        self.assertNotIn("flask",options)
        self.assertNotIn("bis",str(options).lower())

    def test_ui_static_get_and_options_do_not_touch_user_sessions(self):
        # API test uses a different root and no configured SimC binary.
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)/"runs"
            client=TestClient(api.create_app(root=root,token="private"),
                base_url="http://127.0.0.1:8765")
            for path in ("/","/assets/app.js","/assets/styles.css",
                         "/api/v1/bootstrap"):
                self.assertEqual(client.get(path).status_code,200)
            self.assertEqual(client.get("/api/v1/options",
                headers={"x-simc-local-token":"private"}).status_code,200)
            self.assertFalse(root.exists())

if __name__=="__main__":
    unittest.main()
