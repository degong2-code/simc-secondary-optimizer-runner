"""v170: user gets only seasonal effect choices; ordinary gear remains internal."""
import pathlib,sys,unittest
from unittest import mock
from fastapi.testclient import TestClient
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v113_local_web_api as api
import v167_product_season_gear_adapter as gear
from tests.test_v167_product_season_gear_adapter import source

class SeasonGearUserScope(unittest.TestCase):
    def setUp(self):
        self.client=TestClient(api.create_app(token="season-gear-offline"),
                 base_url="http://127.0.0.1:8765")
        self.headers={"x-simc-local-token":"season-gear-offline"}

    def test_session_input_keys_remain_identical(self):
        self.assertNotIn("season_gear",api.sessions.standard_controls())
        self.assertEqual(api.sessions.user_scenario(api.sessions.standard_controls())
                        ["schema"],api.bootstrap.SCHEMA)

    def test_catalog_options_need_local_token_and_no_ordinary_choices(self):
        self.assertEqual(self.client.get("/api/v1/season-gear").status_code,403)
        with mock.patch.object(api.season_gear,"read",
                               return_value=gear.from_v166(source())):
            r=self.client.get("/api/v1/season-gear",headers=self.headers)
            self.assertEqual(r.status_code,200)
            d=r.json()
            self.assertEqual(d["count"],5)
            self.assertFalse(d["manual_exact_id_allowed"])
            self.assertEqual(d["manual_exact_id_exception"],
                             "CRAFTED_EQUIPMENT_VARIANTS_ONLY")
            self.assertFalse(d["ordinary_equipment_user_selectable"])
            self.assertEqual(set(d["choices"]),{
                "trinket","special_effect_gear_candidate","selectable_stat_craft"})
            self.assertEqual(d["native_calls_now"],0)

    def test_ordinary_candidate_and_physical_routes_are_private_internal_only(self):
        for suffix in ("representative/paladin/retribution",
                       "physical-preview/paladin/retribution"):
            with self.subTest(route=suffix):
                r=self.client.get("/api/v1/season-gear/"+suffix,
                                  headers=self.headers)
                self.assertEqual(r.status_code,404)

    def test_missing_catalog_blocks_new_ui_selection_not_legacy_replay(self):
        with mock.patch.object(api.season_gear,"read",
                               side_effect=gear.GearBlocked("MISSING")):
            r=self.client.get("/api/v1/season-gear",headers=self.headers)
            self.assertEqual(r.status_code,200)
            d=r.json()
            self.assertEqual(d["status"],"SEASON_GEAR_CATALOG_UNAVAILABLE")
            self.assertFalse(d["manual_exact_id_allowed"])
            self.assertEqual(d["manual_exact_id_exception"],
                             "CRAFTED_EQUIPMENT_VARIANTS_ONLY")

    def test_actual_288_catalog_only_156_user_selectable_effect_options(self):
        r=self.client.get("/api/v1/season-gear",headers=self.headers)
        self.assertEqual(r.status_code,200,r.text)
        d=r.json()
        self.assertEqual(d["count"],288)
        self.assertEqual(len(d["choices"]["trinket"]),36)
        self.assertEqual(len(d["choices"]["special_effect_gear_candidate"]),10)
        self.assertEqual(len(d["choices"]["selectable_stat_craft"]),106)
        self.assertEqual(sum(map(len,d["choices"].values())),152)
        self.assertFalse(d["manual_exact_id_allowed"])
        self.assertEqual(d["native_calls_now"],0)

    def test_browser_selects_only_season_effects_and_crafted_manual_exception(self):
        html=self.client.get("/").text
        js=self.client.get("/assets/app.js").text
        self.assertIn('id="season-gear-note"',html)
        self.assertIn('<select id="trinket1" required>',html)
        self.assertIn('<select id="trinket2" required>',html)
        self.assertNotIn('<input id="trinket1"',html)
        self.assertIn('function installSeasonGearHints(catalog)',js)
        self.assertIn('function setTrinketSelection(fieldId,itemId,restored=false)',js)
        self.assertIn('const input=(name==="slot"||(isSpecial&&name==="item_id"))',js)
        self.assertIn('seasonChoice("special_effect_gear_candidate",fields.item_id)',js)
        self.assertIn('seasonChoice("trinket",valueInt("trinket1"))',js)
        self.assertNotIn('addList("season-trinket-ids"',js)
        self.assertIn('name!=="item_id"||!isSpecial',js)
        self.assertIn('embellishments:selectedGear("crafted-rows","embellishments")',js)
        self.assertIn('setTrinketSelection("trinket1",u.trinkets[0].item_id,true)',js)
        self.assertNotIn("innerHTML",js)

if __name__=="__main__":
    unittest.main()
