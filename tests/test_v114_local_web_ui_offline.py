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

    def test_v353_task_first_view_and_dark_tactical_accessibility(self):
        page=self.client.get("/").text
        css=self.client.get("/assets/styles.css").text
        js=self.client.get("/assets/app.js").text
        self.assertIn('<meta name="color-scheme" content="dark">',page)
        self.assertIn('aria-label="화면 구획 이동"',page)
        for dest in ("optimizer","settings","results"):
            self.assertIn('data-view-panel="'+dest+'"',page)
            self.assertIn('data-view="'+dest+'"',page)
        for ident in ("manual-t-mode","budget-preview-total","equipment-dialog",
                      "equipment-gallery","optimizer-form","season-build-btn",
                      "simc-technical-panel","start-btn","resume-btn","result-panel"):
            self.assertIn('id="'+ident+'"',page)
        self.assertEqual(page.count('id="optimizer-form"'),1)
        self.assertIn('function switchView(view)',js)
        self.assertIn('function openEquipmentPicker(select,opener=null)',js)
        self.assertIn('function renderEquipmentGallery(query)',js)
        self.assertIn('function drawClassSpecTiles()',js)
        self.assertIn('function hasRequiredSelections()',js)
        self.assertIn('function refreshEquipmentSelectionUI()',js)
        self.assertIn('class-choice-tile',css)
        self.assertIn('equipment-card',css)
        self.assertIn('alt-row-metrics',css)
        for ident in ("class-choice-tiles","spec-choice-tiles","equipment-dialog-clear"):
            self.assertIn('id="'+ident+'"',page)
        self.assertIn('function updateManualTMode()',js)
        self.assertIn('switchView("settings");',js)
        self.assertIn('switchView("results");',js)
        self.assertIn('$("binary").checkValidity()',js)
        self.assertIn('$("optimizer-environment-state").textContent=ready?',js)
        self.assertIn('Number.isSafeInteger(Number(data?.T))',js)
        self.assertIn('selected_pair_95_only',js)
        for color in ("#1D1F24","#09090B","#24262B","#E8B34B"):
            self.assertIn(color,css)
        self.assertIn(':focus-visible',css)
        self.assertIn('@media(max-width:680px)',css)
        self.assertIn('@media(prefers-reduced-motion:reduce)',css)
        self.assertNotIn('--bg:#f5f6f4',css)
        self.assertNotIn('https://fonts.googleapis.com',css)

    def test_v357_client_javascript_syntax_and_contract_when_node_available(self):
        import shutil,subprocess
        binary=shutil.which("node")
        if binary is None:
            self.skipTest("node is not installed on this runner")
        result=subprocess.run([binary,"--check",
              str(ROOT/"runner/webui/app.js")],
              capture_output=True,text=True,timeout=15,check=False)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_v359_inline_equipment_and_stat_cap_location(self):
        page=self.client.get("/").text
        js=self.client.get("/assets/app.js").text
        css=self.client.get("/assets/styles.css").text
        self.assertEqual(page.count('id="max-single-stat-percent"'),1)
        self.assertLess(page.index('id="budget-preview-total"'),
                        page.index('id="max-single-stat-percent"'))
        self.assertLess(page.index('id="max-single-stat-percent"'),
                        page.index('id="conditions-title"'))
        for ident in ("equipment-trinket-grid","equipment-special-grid",
                      "equipment-trinket-search","equipment-special-search",
                      "equipment-trinket-status","equipment-special-status"):
            self.assertIn('id="'+ident+'"',page)
        self.assertIn('function drawInlineEquipment()',js)
        self.assertIn('function inlineEquipmentCard(item,',js)
        self.assertIn('inline-equipment-grid',css)
        self.assertIn('activeTrinketSlot',js)
        self.assertIn('data-equip-select="trinket1"',page)
        self.assertIn('data-equip-select="trinket2"',page)
        self.assertIn('function openEquipmentPicker(select,opener=null)',js)
        self.assertIn('#optimizer-form .conditions-panel .hint:not([role="status"])',css)
        self.assertIn('role="status"',page)
        self.assertIn('document.createElement("button")',js)
        self.assertIn('item.name_ko||item.name',js)
        self.assertNotIn('https://wow.zamimg.com/images/wow/icons',js)

    def test_v358_compact_form_is_two_up_then_full_width_equipment(self):
        page=self.client.get("/").text
        css=self.client.get("/assets/styles.css").text
        js=self.client.get("/assets/app.js").text
        self.assertIn('#optimizer-form{\n  display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr)',css)
        self.assertIn('#optimizer-form>.profile-panel{grid-column:1;grid-row:1}',css)
        self.assertIn('#optimizer-form>.conditions-panel{grid-column:2;grid-row:1}',css)
        self.assertIn('#optimizer-form>.fixed-gear-panel{grid-column:1/-1;grid-row:2}',css)
        self.assertIn('@media(max-width:970px)',css)
        self.assertIn('<details class="fold profile-import">',page)
        self.assertIn('id="class-choice-tiles" hidden',page)
        self.assertIn('id="spec-choice-tiles" hidden',page)
        self.assertIn('function drawClassSpecTiles()',js)
        self.assertIn('if($("class-choice-tiles")?.hidden && $("spec-choice-tiles")?.hidden)return;',js)
        self.assertIn('id="season-gem-layout" open',page)
        self.assertIn('id="trinket1"',page)
        self.assertIn('id="trinket2"',page)
        self.assertIn('id="simc-import-btn"',page)
        self.assertIn('id="start-btn"',page)

    def test_v357_single_form_and_exact_controls_preserved_across_views(self):
        page=self.client.get("/").text
        p=PageParser();p.feed(page)
        self.assertEqual(p.forms,1)
        self.assertEqual(len(p.ids),171)
        for ident in ("class-choice","spec","race","ilevel","talents","final_T",
                      "trinket1","trinket2","special-rows","crafted-rows",
                      "season-target-socket-count","season-verified-flask",
                      "optimizer-oil-loadout","binary","revision","start-btn",
                      "run-label","progress-label","dps","sem","conf95",
                      "result-panel","results-nav-btn","equipment-dialog"):
            self.assertIn(ident,p.ids)
        self.assertIn('data-view-panel="optimizer"',page)
        self.assertIn('data-view-panel="settings" hidden',page)
        self.assertIn('data-view-panel="results" hidden',page)

    def test_configurable_stat_cap_is_visible_and_restores_old_sessions(self):
        html=(ROOT/"runner/webui/index.html").read_text(encoding="utf8")
        js=(ROOT/"runner/webui/app.js").read_text(encoding="utf8")
        self.assertIn('id="max-single-stat-percent"',html)
        self.assertIn('value="60" required',html)
        self.assertIn('max_single_stat_percent:valueInt("max-single-stat-percent")',js)
        self.assertIn('u.max_single_stat_percent??50',js)
        self.assertIn('item.max_single_stat_percent??60',js)

    def test_p3_hah_longrun_controls_and_http_routes_are_explicit_only(self):
        html=(ROOT/"runner/webui/index.html").read_text(encoding="utf8")
        js=(ROOT/"runner/webui/app.js").read_text(encoding="utf8")
        for token in ("longrun-panel","longrun-budget","longrun-batch",
                      "longrun-start-btn","longrun-resume-btn",
                      "longrun-cache-btn","longrun-cancel-btn",
                      "longrun-import-btn","longrun-archive-sha"):
            self.assertIn('id="'+token+'"',html)
        for token in ("/api/v1/longrun/start","/longrun/resume",
                      "/longrun/cancel","/longrun/cache-only",
                      "/longrun/import","/longrun/status",
                      "/longrun/result",
                      "selected_pair_95_only"):
            self.assertIn(token,js)
        self.assertIn("const longrun=await api(",js)
        self.assertIn("if(longrun.enabled===true)",js)
        self.assertIn("max_native_calls:64,continuous:true",js)
        self.assertIn('state.longrunEnabled?"/longrun/resume":"/resume"',js)
        self.assertIn('state.longrunEnabled?"/longrun/cancel":"/cancel"',js)
        self.assertIn('''$("start-btn").addEventListener''',js)

    def test_new_current_season_oil_defaults_never_override_verified_zero_o(self):
        html=self.client.get("/").text
        js=self.client.get("/assets/app.js").text
        self.assertIn('id="oil_main" type="checkbox"',html)
        self.assertNotIn('id="oil_main" type="checkbox" checked',html)
        self.assertIn("새 최적화 세션은 기본적으로 기름을 사용하지 않습니다(O=0)",html)
        self.assertIn("SEASON_PROFILE_OIL_PHYSICAL_ITEMS_OR_HANDS_DRIFT",js)
        self.assertIn("검증되지 않은 O를 0으로 처리하지 않습니다.",js)
        new_default=js.split("function fillDefault(item) {",1)[1].split(
            "function oilCompatibility()",1)[0]
        self.assertIn('$("oil_main").checked=false;',new_default)
        self.assertIn('$("oil_off").checked=false;',new_default)
        self.assertNotIn('item.oil_hands.includes(',new_default)
        restore=js.split("function fillSessionInputs(payload) {",1)[1].split(
            "function ",1)[0]
        self.assertIn('u.oil_hands.includes("main_hand")',restore)
        self.assertIn('u.oil_hands.includes("off_hand")',restore)
        self.assertIn('oil_hands:["main_hand","off_hand"].filter(',js)


    def test_verified_installed_flask_selects_existing_F_id_without_new_proof(self):
        html=self.client.get("/").text
        js=self.client.get("/assets/app.js").text
        for token in ("season-verified-flask","season-verified-flask-status",
                      "season-selected-flask-id"):
            self.assertIn('id="'+token+'"',html)
        for token in ("function renderInstalledFlaskChoices(data)",
                      "function chooseInstalledFlask()",
                      'data.verified_flasks||[]',
                      '$("season-selected-flask-id").value=field("season-verified-flask")',
                      'Number(data.target_ilevel)===Number(field("ilevel"))',
                      '"season-target-ilevel").addEventListener("change"',
                      "renderInstalledFlaskChoices(data)"):
            self.assertIn(token,js)
        self.assertIn('id="season-verified-flask"',html)
        self.assertNotIn("request.F_rating=",js)
        self.assertNotIn("request.verified_flasks=",js)
        # Same v216 takes the physical ID through existing Build input.
        self.assertIn("selected_flask_item_id,",js)
        self.assertIn('const target_ilevel=forUserVariant?valueInt("ilevel"):',js)
        self.assertIn('valueInt("season-target-ilevel");',js)
        self.assertNotIn("const flaskData=seasonLevel===ilevel?data:",js)
        self.assertIn('id="season-gem-layout" open',html)
        self.assertNotIn("영약은 검증된 원본 고정치 F=165",html)
        self.assertNotIn("기존 6회 실행과 별개",html)

    def test_verified_oil_dropdown_reuses_exact_id_web_request(self):
        html=self.client.get("/").text
        js=self.client.get("/assets/app.js").text
        for ident in ("optimizer-oil-loadout","optimizer-oil-loadout-status"):
            self.assertIn('id="'+ident+'"',html)
        for token in ("/api/v1/verified-oil-loadouts?ilevel=",
                      "VERIFIED_INSTALLED_OIL_LOADOUTS",
                      "chooseInstalledOilLoadout",
                      "state.oilLoadouts.find(",
                      '$( "optimizer-oil-main-id")'):
            self.assertIn(token.replace('$( "','$("'),js)
        self.assertIn("ids.main_hand??",js)
        self.assertIn("ids.off_hand??",js)
        self.assertIn("renderInstalledOilLoadouts(state.oilCatalog)",js)
        self.assertIn("request.selected_oil_item_ids_by_hand=exactOils",js)
        self.assertNotIn("request.fixed_O=",js)
        self.assertIn("품질 우위를 추정하지 않습니다",html)

    def test_installed_build_is_a_bound_session_choice_not_collection(self):
        js=self.client.get("/assets/app.js").text
        self.assertIn('request.installed_season_game_build=installedBuild;',js)
        self.assertIn('const installedBuild=field("season-game-build");',js)
        self.assertIn('payload.installed_season_game_build??""',js)
        self.assertIn('try{await refreshInstalledOilLoadouts();}',js)
        self.assertNotIn('request.fresh_season_build=',js)
        self.assertIn('...buildRequest(),max_native_calls:budget',js)
        self.assertIn('const payload={...buildRequest(),max_native_calls:budget,',js)

    def test_exact_verified_oil_ids_reach_both_web_optimizer_routes(self):
        """Only physical IDs are carried; browser supplies no numeric O."""
        html=self.client.get("/").text
        js=self.client.get("/assets/app.js").text
        for ident in ("optimizer-oil-exact-panel",
                      "optimizer-oil-main-id","optimizer-oil-off-id"):
            self.assertIn('id="'+ident+'"',html)
        self.assertIn("const exactOils={};",js)
        self.assertIn("if(!controls.oil_hands.includes(hand))",js)
        self.assertIn("Object.keys(exactOils).length!==controls.oil_hands.length",js)
        self.assertIn("request.selected_oil_item_ids_by_hand=exactOils",js)
        self.assertIn("...buildRequest(),max_native_calls:budget",js)
        self.assertIn("const payload={...buildRequest(),max_native_calls:budget,",js)
        self.assertIn("payload.verified_oil_item_ids_by_hand||{}",js)
        self.assertIn('$("optimizer-oil-main-id").value="";',js)
        self.assertIn('$("optimizer-oil-off-id").value="";',js)
        self.assertIn("WEB_FRESH_SELECTED_OIL_ITEM_IDS_NOT_INSTALLED",js)
        # Neither free-form oil ratings nor arbitrary SimC effects are accepted.
        self.assertNotIn('controls.fixed_O=',js)
        self.assertNotIn('request.static_CHMV_vector=',js)

    def test_dk_runeforge_ui_selection_restore_and_distinct_oil(self):
        page=self.client.get("/").text
        js=self.client.get("/assets/app.js").text
        for name in ("dk-runeforge-panel","dk_rune_main","dk_rune_off"):
            self.assertIn('id="'+name+'"',page)
        self.assertIn("function runeCompatibility()",js)
        self.assertIn("controls.runeforge_by_hand=runeByHand",js)
        self.assertIn("u.runeforge_by_hand?.[hand]",js)
        self.assertIn("기름 O와 별개인 영구 강화",page)
        self.assertNotIn('value="3368"',page)
        self.assertIn('state.dkRuneIds=new Set()',js)
        self.assertIn('PINNED_DK_RUNES_INSTALLED',js)
        self.assertIn('이번 시즌 검증된 죽음의 기사 룬만 새 세션',js)
        catalog=self.client.get("/api/v1/season-option-catalog",
                                headers=self.head)
        self.assertEqual(catalog.status_code,200,catalog.text)
        self.assertIn("verified_weapon_enhancements",catalog.json())

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
        self.assertIn("특수효과 장비 · 장식",result.text)
        self.assertEqual(page.scripts,[{"src":"/assets/app.js","defer":None}])
        self.assertEqual(page.links,[{"rel":"stylesheet","href":"/assets/styles.css"}])
        required=("optimizer-form","spec","simc-import-text","simc-import-file",
          "simc-import-btn","class-choice","race","talents","trinket1",
          "trinket2","ilevel","final_T","targets","duration",
          "raid_buffs","oil_main","oil_off","binary","revision","static_cache",
          "special-rows","crafted-rows","food","potion","augmentation",
          "diamond","omnium","plan-btn","start-btn","resume-btn","cache-btn",
          "cancel-btn","restore-btn","restore-id","notice","session-id",
          "stage-text","progress-label","progress-pct","progress-bar",
          "filled-result","empty-result","dps","sem","budget","stat-bars",
          "conf95","alt-count","alt-list","recent-session-id","recent-open-btn",
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
        self.assertNotIn('"/api/v1/native-batches"',js.text)
        self.assertIn('"/api/v1/sessions"',js.text)
        self.assertIn("async function loadRecentSessions()",js.text)
        self.assertIn('withBusy(loadRecentSessions)',js.text)
        self.assertNotIn('async function showNativeBatch()',js.text)
        self.assertNotIn("fetch(\"file://",js.text)
        self.assertIn('localStorage.setItem("simc_secondary_session_id"',js.text)
        self.assertIn("cache-only",js.text)
        self.assertIn("result",js.text)
        self.assertIn('"/api/v1/longrun/start"',js.text)
        self.assertIn('window.confirm("이 PC에서 최적화를 시작할까요?',js.text)
        self.assertEqual(self.client.get("/assets/missing.js").status_code,403)

    def test_simple_korean_product_surface_and_race_value_seal(self):
        page=self.client.get("/").text
        js=self.client.get("/assets/app.js").text
        self.assertIn('id="race-list"',page)
        self.assertIn('id="class-choice"',page)
        self.assertIn('value="드랙티르"',page)
        self.assertIn('id="simc-technical-panel"',page)
        self.assertIn('id="season-setup-details"',page)
        self.assertIn("최적 스탯 찾기",page)
        self.assertIn("function simcRace(value)",js)
        self.assertIn("function installClassSpecChoices()",js)
        self.assertIn("function populateSpecializationsForClass(cls,selectedKey",js)
        self.assertIn("function setRaceSuggestions(item)",js)
        self.assertIn('$("race").value=displayRace(item.race)',js)
        self.assertIn('$("simc-technical-panel").open=true',js)
        self.assertIn("race:resolvedRace",js)
        self.assertIn("이번 시즌 장신구 선택",js)
        self.assertIn('"/api/v1/longrun/start"',js)

    def test_searchable_choices_preserve_exact_ids_and_keyboard(self):
        js=self.client.get("/assets/app.js").text
        css=self.client.get("/assets/styles.css").text
        self.assertIn("function enhanceSelect(select)",js)
        self.assertIn("function initializeSearchChoices()",js)
        self.assertIn('select.dispatchEvent(new Event("change",{bubbles:true}))',js)
        self.assertIn('input.setAttribute("role","combobox")',js)
        self.assertIn('menu.className="choice-results"',js)
        self.assertIn('e.key==="ArrowDown"',js)
        self.assertIn(".choice-native-select",css)
        self.assertIn("fieldWrap.className=\"gear-choice-field\"",js)
        self.assertIn("gearLabel.before(fieldWrap);fieldWrap.append(gearLabel,box)",js)
        self.assertIn('textContent="평가 "+n+"회 · 최대 "+limit+"회"',js)

    def test_official_item_names_bound_to_current_ids(self):
        response=self.client.get("/api/v1/season-gear",headers=self.head)
        self.assertEqual(response.status_code,200)
        data=response.json()
        self.assertEqual(data["verified_ko_item_names"],77)
        visible=data["choices"]["trinket"]+data["choices"]["special_effect_gear_candidate"]
        self.assertEqual(len(visible),77)
        self.assertTrue(all("name_ko" in item for item in visible))
        self.assertEqual(next(x["name_ko"] for x in visible if x["item_id"]==158367),
                         "메레크타의 송곳니")

    def test_v336_official_source_terms_are_not_simc_control_tokens(self):
        page=self.client.get("/").text
        js=self.client.get("/assets/app.js").text
        self.assertIn('id="season-terms-status"',page)
        self.assertIn("function applyOfficialGameTerms(doc)",js)
        self.assertIn("function refreshOfficialGameTerms(build)",js)
        self.assertIn('verifiedTerms.spec[token]',js)
        self.assertIn('verifiedTerms.race[token]',js)
        self.assertIn("refreshOfficialGameTerms(state.oilCatalog.game_build)",js)
        self.assertIn("refreshOfficialGameTerms(report.web_environment_scope.game_build)",js)
        self.assertIn("function simcRace(value)",js)
        self.assertNotIn("verifiedTerms.spec[field",js)

    def test_official_korean_names_are_environment_build_stage(self):
        page=self.client.get("/").text
        js=self.client.get("/assets/app.js").text
        self.assertIn('id="season-locale-status"',page)
        self.assertIn("report.official_ko_localization",js)
        self.assertIn("현재 검증된 선택 목록의 한국어 명칭",js)
        self.assertIn("미확정 명칭은 원본 이름을 표시합니다.",js)
        self.assertIn('item.official_name_ko',js)

    def test_v349_season_build_activity_socket_total_and_advanced_ids(self):
        """Activity is indeterminate; user scope is separate from source IDs."""
        html=self.client.get("/").text
        js=self.client.get("/assets/app.js").text
        css=(ROOT/"runner/webui/styles.css").read_text(encoding="utf8")
        for ident in ("season-build-running","season-build-elapsed",
                      "season-build-summary","season-socket-breakdown",
                      "season-gem-layout","optimizer-season-itemid-expert"):
            self.assertIn('id="'+ident+'"',html)
        self.assertIn("특수보석을 포함한 전체 소켓 수",html)
        self.assertIn("새 J 예산·보석 배치가 검증",html)
        self.assertIn("일반 사용자가 시즌 구축을 위해 조사하는 항목이 아닙니다",html)
        self.assertIn("일반보석 "+'"+ordinary+"'+"개 + 특수보석",js)
        self.assertIn('stopSeasonActivity=beginSeasonBuildActivity()',js)
        self.assertIn('stopSeasonActivity();',js)
        self.assertIn("실제 진행률은 서버 결과에서 확인",js)
        self.assertIn("시즌 원본과 예산의 필수 검증이 남았습니다",js)
        self.assertIn("아래 1차 미완료 원인",js)
        self.assertIn("season-activity-track",css)
        self.assertNotIn('id="season-build-percent"',html)
        self.assertNotIn("환경 구축 100%",js)

    def test_v350_approved_common_season_vs_individual_inputs_separation(self):
        page=self.client.get("/").text
        js=self.client.get("/assets/app.js").text
        common=page.split('<section class="panel environment-setup"',1)[1].split(
            '</section>',1)[0]
        optimization=page.split('<form id="optimizer-form"',1)[1].split(
            '</form>',1)[0]
        for ident in ("season-target-socket-count","season-existing-special-gem-id",
                      "season-verified-flask","season-selected-flask-id",
                      "optimizer-season-itemid-expert","user-variant-prepare-btn"):
            self.assertNotIn('id="'+ident+'"',common)
            self.assertIn('id="'+ident+'"',optimization)
        self.assertIn("시즌 환경 자동 확인·구축",common)
        self.assertIn("보석 소켓 수",optimization)
        self.assertIn("시즌 공통 원본·아이템·품질·적용 조건",common)
        self.assertIn('async function buildSeasonEnvironment(forUserVariant=false)',js)
        self.assertIn('const requested_sockets=forUserVariant?valueInt("season-target-socket-count"):4',js)
        self.assertIn('const selectedFlask=forUserVariant?field("season-selected-flask-id"):""',js)
        self.assertIn('user_socket_total:gemSocketTotal',js)
        self.assertIn('user_special_gem_id:userSpecialGem',js)
        self.assertIn('selected_flask_item_id:flaskId',js)
        self.assertIn('buildSeasonEnvironment(true)',js)
        self.assertIn('payload.verified_user_variant',js)
        self.assertNotIn("data.environment_ready=true",js)

    def test_v347_unscoped_credentialless_season_is_pending_not_ready(self):
        """Real v347 negative evidence gets an actionable user-facing reason."""
        js=(ROOT/"runner/webui/app.js").read_text(encoding="utf8")
        self.assertIn("AUTHENTICATED_SEASON_CREDENTIALS_MISSING",js)
        self.assertIn("AUTHENTICATED_SEASON_JOIN_NOT_READY",js)
        self.assertIn("missingSeasonScope",js)
        self.assertIn("현재 시즌·레이드 범위 미검증(환경 설치 보류)",js)
        self.assertIn("환경 READY 전에는 기본 계산을 시작할 수 없습니다.",js)
        self.assertIn("WEB_PRIMARY_VERIFIED_SEASON_INSTALL_REQUIRED",js)
        self.assertNotIn("data.environment_ready=true",js)

    def test_environment_build_surface_is_not_optimizer_plan(self):
        page=self.client.get("/").text
        js=self.client.get("/assets/app.js").text
        for ident in ("season-game-build","season-target-ilevel",
                      "season-native-g","season-native-f","season-native-o",
                      "season-auto-core","season-build-btn",
                      "season-build-stage","season-build-missing",
                      "season-refresh-reason",
                      "season-existing-special-gem-id",
                      "season-target-socket-count",
                      "season-selected-flask-id"):
            self.assertIn('id="'+ident+'"',page)
        self.assertIn('"/api/v1/environment/season-build"',js)
        self.assertIn("const refresh_reason=forUserVariant?null:",js)
        self.assertIn('(field("season-refresh-reason")||null);',js)
        self.assertIn("VERIFIED_INSTALLED_SAME_SEASON_SOURCE_REUSED",js)
        self.assertIn('id="season-build-technical-panel"',page)
        self.assertIn('id="season-build-technical"',page)
        self.assertIn("technical.textContent=node.textContent;",js)
        self.assertIn("후속 장비·G/J/F/O 미완료는 이 원인에서 연쇄 발생",js)
        self.assertIn("시즌 환경 자동 확인·구축 (검증된 동일 시즌 원본 재사용)",page)
        self.assertIn("BLIZZARD_PUBLIC_RETAIL_KR",js)
        self.assertIn("현재 Retail(KR) 자동 조회",page)
        self.assertIn("const game_build=supplied_build||null",js)
        self.assertIn("existing_special_gem_id",js)
        self.assertIn("source_target_socket_count",js)
        self.assertIn('id="season-target-socket-count" type="number" min="4" max="64" step="1" value="4"',page)
        self.assertIn("보석 소켓 수",page)
        self.assertIn("selected_flask_item_id",js)
        self.assertIn("J/F 원본: ",js)
        self.assertIn("J/F 품질: ",js)
        self.assertIn("정확한 영약 ItemID 선택",js)
        self.assertIn("기존 같은 시즌 v281 원본",page)

        self.assertIn("일반보석 4종 기본 배치 요청",js)
        self.assertIn("모든 효과 계산은 SimC",page)
        self.assertIn("이미 선택된 특수보석",page)

        self.assertIn('"/api/v1/sessions/plan"',js)
        self.assertIn("user_character_or_trinkets_required",js)
        self.assertIn("DPS 최적화 0회",js)
        self.assertIn("관측 수치(미승인)",js)
        self.assertIn("F/O 자동 발견",js)
        self.assertIn("F Native",js)
        self.assertIn("auto_native_F_requested",js)
        self.assertIn('id="season-auto-core" type="checkbox" checked',page)
        self.assertIn("auto_initial_core_build",js)
        self.assertIn("auto_initial_core_simc_binary",js)
        self.assertIn("auto_native_O_requested",js)
        self.assertIn("consumable_native_binary",js)
        self.assertIn("G 실측 불필요",page)
        self.assertIn("native_G_binary=nativeRequested?executable:null",js)
        self.assertIn("consumable_native_binary=native_F_O_requested?executable:null",js)
        self.assertNotIn("F/O 측정을 위해 위 G Native 선택도 필요합니다.",js)
        self.assertIn("O Native",js)
        self.assertIn("기름 미적용 가정(공식 선택 아님)",js)
        self.assertIn("automatic_F_O_measurement_candidates_unadmitted",js)
        self.assertIn("numeric_preview_only",js)
        self.assertIn("신규 Native",js)
        self.assertNotIn('id="season-optimizer-submit"',page)

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

    def test_environment_source_join_audit_is_visible_without_new_approvals(self):
        js=self.client.get("/assets/app.js").text
        self.assertIn("build.readiness?.source_join_audit",js)
        self.assertIn("DB 연결 근거 보류(소스 행)",js)
        self.assertIn("DB Join Audit 없음(구형 카탈로그)",js)
        self.assertIn("gem_property_item",js)
        self.assertIn("entry.pending_rows",js)
        self.assertNotIn("innerHTML",js)

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
        self.assertIn('if(actors.length!==1||!info.spec)',js)
        self.assertIn('const race=(info.race||"").toLowerCase()',js)
        self.assertIn('talents:info.talents||""',js)
        self.assertIn("미입력 종족/특성은 기본값 사용",js)
        self.assertIn('if(name==="copy")',js)
        self.assertIn('if(field("spec")!==parsed.key)',js)
        self.assertIn('fillDefault(parsed.defaults);',js)
        self.assertIn('  if(parsed.race)$("race").value=displayRace(parsed.race);',js)
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
        self.assertIn("일반 장비·무기·티어 4세트는 자동 구성합니다.",js)
        self.assertIn("선택한 목표 레벨의 대표 장비를 자동 구성합니다.",js)
        self.assertNotIn('id="current_season_product"',page)
        self.assertIn('  showRepresentativeScope();\n  syncSearchChoices();\n}',js)
        self.assertIn('function fillSessionInputs(payload)',js)
        self.assertNotIn("innerHTML",js)

    def test_special_effect_gear_has_eight_dynamic_rows_not_two(self):
        js=self.client.get("/assets/app.js").text
        self.assertIn('const limit=isSpecial?8:2;',js)
        self.assertIn('add.textContent="+ 특수효과 장비 추가"',js)
        self.assertIn('if(isSpecial&&i>=2)row.hidden=true',js)
        self.assertIn('if(result.length>(isCraft?2:8))',js)
        self.assertIn('for (let i=0;i<limit;i++)',js)

    def test_new_plan_does_not_display_previous_specialization_dps(self):
        js=self.client.get("/assets/app.js").text
        self.assertIn("const changed=id!==state.session;",js)
        self.assertIn('if(changed) {\n    // A new plan is not the result',js)
        self.assertIn('if(data?.active || !data?.result_ready) {\n    $("filled-result").hidden=true;',js)
        self.assertIn('markSession(p.session_id);showPlan(p);await pollOnce();',js)
        self.assertIn('if(snapshot.result)renderResult(snapshot.result);',js)

    def test_running_resume_never_shows_saved_partial_result_as_current(self):
        # The v293 status endpoint can report result_ready from a prior batch
        # while a newly resumed worker is active. Browser presentation must
        # hide that older result without deleting or changing the real data.
        js=self.client.get("/assets/app.js").text
        self.assertIn("data?.active || !data?.result_ready",js)
        self.assertIn("const result=longrun.result_ready&&!longrun.active",js)
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

    def test_inactive_stale_running_longrun_is_resumable_not_idle(self):
        # Worker state survives an HTTP server restart; OS activity is the
        # authority, not the prior V293_WORKER_STATE.json word RUNNING.
        js=self.client.get("/assets/app.js").text
        self.assertIn("const interrupted=!data.active && state.longrunEnabled",js)
        self.assertIn('worker==="RUNNING"||worker==="QUEUED"',js)
        self.assertIn('interrupted?"실행 중단 · 재개 가능"',js)
        self.assertIn("저장된 세션을 재개할 수 있습니다",js)

    def test_v342_cancelled_and_full_budget_are_distinct_from_idle(self):
        js=self.client.get("/assets/app.js").text
        self.assertIn('worker==="PAUSED_USER_CANCEL"',js)
        self.assertIn('worker==="BUDGET_EXHAUSTED" && data.result_ready===true',js)
        self.assertIn('finished?"탐색 상한 완료 · 결과 저장"',js)
        self.assertIn('paused?"회차 중단 · 재개 가능"',js)
        self.assertIn('state.longrunCompleted=Boolean(finished);',js)
        self.assertIn('!state.session||state.longrunCompleted',js)
        self.assertIn('!state.longrunEnabled||state.longrunCompleted',js)
        self.assertIn('state.longrunCompleted=false;',js)

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
        self.assertEqual(set(options),{"food","potion","augmentation","diamond_id","omnium_talents","display_labels","embellishments"})
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
