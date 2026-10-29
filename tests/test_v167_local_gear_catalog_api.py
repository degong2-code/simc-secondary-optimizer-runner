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

if __name__=="__main__":
    unittest.main()
