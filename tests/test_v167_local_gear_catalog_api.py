"""P1 local gear-choice endpoint + conservative representative preview, Native 0."""
import sys
import pathlib
import unittest
from unittest import mock
from fastapi.testclient import TestClient

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v113_local_web_api as api
import v167_product_season_gear_adapter as gear
from tests.test_v167_product_season_gear_adapter import source

class ReadOnlyWebCatalog(unittest.TestCase):
    def setUp(self):
        self.app=api.create_app(token="season-gear-offline")
        self.client=TestClient(self.app,base_url="http://127.0.0.1:8765")
        self.headers={"x-simc-local-token":"season-gear-offline"}

    def test_session_input_keys_remain_identical(self):
        self.assertNotIn("season_gear",api.sessions.standard_controls())
        self.assertEqual(api.sessions.user_scenario(api.sessions.standard_controls())
                        ["schema"],api.bootstrap.SCHEMA)

    def test_read_only_options_need_local_token(self):
        self.assertEqual(self.client.get("/api/v1/season-gear").status_code,403)
        with mock.patch.object(api.season_gear,"read",return_value=gear.from_v166(source())):
            result=self.client.get("/api/v1/season-gear",headers=self.headers)
            self.assertEqual(result.status_code,200)
            d=result.json()
            self.assertEqual(d["count"],5)
            self.assertTrue(d["manual_exact_id_allowed"])
            self.assertFalse(d["full_season_completeness_confirmed"])
            self.assertEqual(d["native_calls_now"],0)

    def test_preview_uses_stable_spec_contract_and_never_runs_simc(self):
        with mock.patch.object(api.season_gear,"read",
                               return_value=gear.from_v166(source())):
            r=self.client.get("/api/v1/season-gear/representative/paladin/retribution",
                              headers=self.headers)
            self.assertEqual(r.status_code,200,r.text)
            self.assertEqual(r.json()["candidate_slots"]["wrists"][0]["item_id"],101)
            self.assertFalse(r.json()["tier_four_piece_id_confirmed"])
            bad=self.client.get("/api/v1/season-gear/representative/evoker/augmentation",
                                headers=self.headers)
            self.assertEqual(bad.status_code,404)
            self.assertEqual(bad.json()["detail"]["code"],"REPRESENTATIVE_SPEC_UNSUPPORTED")

    def test_unavailable_catalog_does_not_block_manual_inputs(self):
        with mock.patch.object(api.season_gear,"read",side_effect=gear.GearBlocked("MISSING")):
            r=self.client.get("/api/v1/season-gear",headers=self.headers)
            self.assertEqual(r.status_code,200)
            self.assertEqual(r.json()["status"],"SEASON_GEAR_CATALOG_UNAVAILABLE")
            self.assertTrue(r.json()["manual_exact_id_allowed"])
            p=self.client.get("/api/v1/season-gear/representative/paladin/retribution",
                              headers=self.headers)
            self.assertEqual(p.status_code,409)


    def test_actual_persisted_288_ids_and_all_26_family_previews(self):
        choices=self.client.get("/api/v1/season-gear",headers=self.headers)
        self.assertEqual(choices.status_code,200,choices.text)
        body=choices.json()
        self.assertEqual(body["count"],288)
        self.assertEqual(len(body["choices"]["trinket"]),36)
        self.assertEqual(len(body["choices"]["special_effect_gear_candidate"]),10)
        self.assertEqual(len(body["choices"]["selectable_stat_craft"]),106)
        self.assertTrue(body["manual_exact_id_allowed"])
        self.assertEqual(body["native_calls_now"],0)
        for cl,spec in api.sessions.SUPPORTED:
            with self.subTest(spec=cl+"/"+spec):
                r=self.client.get(
                    "/api/v1/season-gear/representative/"+cl+"/"+spec,
                    headers=self.headers)
                self.assertEqual(r.status_code,200,r.text)
                preview=r.json()
                self.assertEqual(preview["status"],"PREVIEW_ONLY_NOT_A_PROFILE")
                self.assertFalse(preview["tier_four_piece_id_confirmed"])
                self.assertFalse(preview["weapon_profile_confirmed"])
                self.assertEqual(preview["native_calls_now"],0)
                self.assertTrue(all(preview["candidate_slots"].get(slot)
                                    for slot in ("neck","back","wrists","waist","feet")))

    def test_web_hints_do_not_replace_exact_user_item_id_inputs(self):
        html=self.client.get("/").text
        js=self.client.get("/assets/app.js").text
        self.assertIn('id="season-gear-note"',html)
        self.assertIn("function installSeasonGearHints(catalog)",js)
        self.assertIn('addList("season-trinket-ids"',js)
        self.assertIn('addList("season-special-ids"',js)
        self.assertIn('addList("season-crafted-ids"',js)
        self.assertIn('selected?.slot_hint&&statOptions.includes',js)
        self.assertIn('trinket_ids:[valueInt("trinket1"),valueInt("trinket2")]',js)
        self.assertIn('special_items:selectedGear("special-rows","special_items")',js)
        self.assertIn('embellishments:selectedGear("crafted-rows","embellishments")',js)
        self.assertNotIn("innerHTML",js)

if __name__=="__main__":
    unittest.main()
