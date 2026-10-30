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
        self.assertIn("특수효과 장비는 시즌 목록에서 선택 · 장식은 부위·종류·제작 스탯만 선택",result.text)
        self.assertEqual(page.scripts,[{"src":"/assets/app.js","defer":None}])
        self.assertEqual(page.links,[{"rel":"stylesheet","href":"/assets/styles.css"}])
        required=("optimizer-form","spec","simc-import-text","simc-import-file",
          "simc-import-btn","race","talents","trinket1",
          "trinket2","ilevel","final_T","targets","duration",
          "raid_buffs","oil_main","oil_off","binary","revision","static_cache",
          "special-rows","crafted-rows","food","potion","augmentation",
          "diamond","omnium","plan-btn","start-btn","resume-btn","cache-btn",
          "cancel-btn","restore-btn","restore-id","notice","session-id",
          "stage-text","progress-label","progress-pct","progress-bar",
          "filled-result","empty-result","dps","sem","budget","stat-bars",
          "conf95","alt-count","alt-list","batch-id","batch-open-btn",
          "batch-table","batch-status","recent-session-id","recent-open-btn",
          "recent-refresh-btn","recent-session-note")
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
        self.assertIn('"/api/v1/native-batches"',js.text)
        self.assertIn('"/api/v1/sessions"',js.text)
        self.assertIn("async function loadRecentSessions()",js.text)
        self.assertIn('withBusy(loadRecentSessions)',js.text)
        self.assertIn('async function showNativeBatch()',js.text)
        self.assertNotIn("fetch(\"file://",js.text)
        self.assertIn('localStorage.setItem("simc_secondary_session_id"',js.text)
        self.assertIn("cache-only",js.text)
        self.assertIn("result",js.text)
        self.assertIn('"/api/v1/sessions/start"',js.text)
        self.assertIn('window.confirm("이 PC에서 실제 SimC',js.text)
        self.assertEqual(self.client.get("/assets/missing.js").status_code,403)

    def test_all_26_spec_labels_are_neutral_not_historical_native_claims(self):
        js=self.client.get("/assets/app.js").text
        labels=js.split("const specLabels = {",1)[1].split("};",1)[0]
        for cl,sp in api.sessions.SUPPORTED:
            self.assertIn('"'+cl+'/'+sp+'":"',labels)
        self.assertEqual(labels.count('":"'),26)
        self.assertNotIn("최적화 미검증",labels)
        self.assertNotIn("목표 프로필 Native 시험 전",labels)
        self.assertNotIn("기본334 단발",labels)
        self.assertIn('"demonhunter/havoc":"악마사냥꾼 · 파멸"',labels)
        self.assertIn('"druid/balance":"드루이드 · 조화"',labels)
        self.assertIn('"evoker/devastation":"기원사 · 황폐"',labels)

    def test_optional_simc_import_only_extracts_identity_and_talents(self):
        page=self.client.get("/").text
        js=self.client.get("/assets/app.js").text
        self.assertIn('id="simc-import-text"',page)
        self.assertIn('id="simc-import-file"',page)
        self.assertIn('id="simc-import-btn"',page)
        self.assertIn("현재 장비·스탯은 가져오지 않음",page)
        self.assertIn("function parseSimcCharacter(source)",js)
        self.assertIn('["spec","race","talents"]',js)
        self.assertIn('const source=file?await file.text()',js)
        self.assertIn('if(actors.length!==1',js)
        self.assertIn('if(name==="copy")',js)
        self.assertIn('if(field("spec")!==parsed.key)',js)
        self.assertIn('fillDefault(parsed.defaults);',js)
        self.assertIn('  $("race").value=parsed.race;',js)
        self.assertIn('  $("talents").value=parsed.talents;',js)
        self.assertIn('withBusy(importSimcCharacter)',js)
        self.assertNotIn("FormData(",js)
        self.assertNotIn("FileReader(",js)
        self.assertNotIn("innerHTML",js)

    def test_local_cache_is_optional_and_auto_use_is_explained(self):
        html=self.client.get("/").text
        js=self.client.get("/assets/app.js").text
        self.assertIn("기본 로컬 정적 캐시가 있으면 자동 사용",html)
        self.assertIn("이미 저장된 로컬 정적 캐시는 자동으로 찾아 사용",html)
        self.assertIn("plan.static_cache_auto_used",js)
        self.assertIn("저장된 정적 캐시 자동 적용",js)
        self.assertNotIn("innerHTML",js)

    def test_special_cache_and_five_tier_errors_have_actionable_ui_guidance(self):
        js=self.client.get("/assets/app.js").text
        self.assertIn('SPECIAL_L_REQUIRES_EXACT_NATIVE_STATIC_VARIANT',js)
        self.assertIn('REFERENCE_FIXED_L_CONSTRAINT_UNRESOLVED',js)
        self.assertIn('SELECTED_SPECIAL_FLOOR_UNFEASIBLE',js)
        self.assertIn('FIVE_TIER_LAYOUT_OUTSIDE_FOUR_ROW_CONTRACT',js)
        self.assertIn('다섯 번째 티어 아이템',js)
        self.assertIn('다른 레벨의 레코드를 대신 적용하지 않습니다.',js)
        self.assertNotIn('innerHTML',js)

    def test_representative_gear_limit_is_permanent_on_form_and_restore(self):
        # Expose the source-backed scope, never claim all non-tier ordinary
        # pieces are completely standardized just because Native passes.
        page=self.client.get("/").text
        js=self.client.get("/assets/app.js").text
        self.assertIn('id="gear-scope-note"',page)
        self.assertIn("SOURCE_INDEPENDENT_TARGET334_VALIDATED_BATCH",js)
        self.assertIn("목표 334: 내부 시즌 대표 장비",js)
        self.assertIn("334 이외 목표 ilvl: 최신 시즌 대표 장비·티어·무기를 선택 레벨",js)
        self.assertIn("완전한 표준화까지 검증된 것은 아니며",js)
        self.assertIn('  showRepresentativeScope();\n}',js)
        self.assertIn('function fillSessionInputs(payload)',js)
        self.assertNotIn("innerHTML",js)

    def test_special_effect_gear_has_eight_dynamic_rows_not_two(self):
        js=self.client.get("/assets/app.js").text
        self.assertIn('const limit=isSpecial?8:2;',js)
        self.assertIn('add.textContent="+ 특수효과 장비 추가"',js)
        self.assertIn('if(isSpecial&&i>=2)row.hidden=true',js)
        self.assertIn('group==="special_items"?8:2',js)
        self.assertIn('for (let i=0;i<limit;i++)',js)

    def test_new_plan_does_not_display_previous_specialization_dps(self):
        js=self.client.get("/assets/app.js").text
        self.assertIn("const changed=id!==state.session;",js)
        self.assertIn('if(changed) {\n    // A new plan is not the result',js)
        self.assertIn('if(!data?.result_ready) {\n    $("filled-result").hidden=true;',js)
        self.assertIn('markSession(p.session_id);showPlan(p);await pollOnce();',js)
        self.assertIn('if(snapshot.result)renderResult(snapshot.result);',js)

    def test_blocked_worker_is_not_shown_as_idle_waiting(self):
        js=self.client.get("/assets/app.js").text
        self.assertIn('worker==="BLOCKED_OR_PARTIAL"?"실행 차단"',js)
        self.assertIn('p.worker?.reason||p.error||worker',js)
        self.assertIn('worker==="BLOCKED_OR_PARTIAL"?',js)
        self.assertIn('const status=data.active?worker:',js)
        self.assertIn('worker==="CANCELLED_PARTIAL"',js)
        self.assertIn('cancelled?"취소됨 · 재개 가능"',js)
        self.assertIn('완료한 후보 보존 · 같은 세션 재개 가능',js)

    def test_near_alternative_presentation_reuses_native_result_statistics(self):
        # No new SimC calculations: existing v096 user_result fields only.
        js=self.client.get("/assets/app.js").text
        self.assertIn('number(r.observed_unique_candidates)',js)
        self.assertIn('if(!alts.length)',js)
        self.assertIn('number(alt.simc_sem,2)',js)
        self.assertIn('number(alt.observed_dps_loss_pct,3)',js)
        self.assertIn('number(100*alt.rating_moved_fraction_B,1)',js)
        self.assertIn('number(alt.percent_of_final_T[key],2)',js)
        self.assertIn('OBSERVED_NEAR_BUT_LOWER_AT_95',js)
        self.assertIn('OBSERVED_NEAR_UNRESOLVED_AT_95',js)
        self.assertIn('미탐색 분배의 성능은 알 수 없습니다.',js)
        self.assertNotIn('Math.random(',js)

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
        self.assertEqual(len(options["omnium_talents"]),16)
        self.assertIn("136822:1/136823:1/136817:1/136820:1/136814:1",
                      options["omnium_talents"])
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
