"""v169 P1 real season tier 4pc and weapon form API -- NO SimC calls."""
import pathlib,sys,unittest
from unittest import mock
from fastapi.testclient import TestClient

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v113_local_web_api as api
import v169_source_first_representative_stage as stage

class CurrentPhysicalEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client=TestClient(api.create_app(token="physical-preview-local"),
                              base_url="http://127.0.0.1:8765")
        cls.header={"x-simc-local-token":"physical-preview-local"}

    def test_all_26_native_zero_current_tier_four_and_weapon_shapes(self):
        self.assertEqual(self.client.get(
             "/api/v1/season-gear/physical-preview/warrior/fury").status_code,403)
        active=stage.load_tier()
        for cls,spec in api.sessions.SUPPORTED:
            with self.subTest(spec=cls+"/"+spec):
                res=self.client.get(
                   "/api/v1/season-gear/physical-preview/"+cls+"/"+spec,
                   headers=self.header)
                self.assertEqual(res.status_code,200,res.text)
                doc=res.json()
                self.assertEqual(doc["status"],
                    "P1_SOURCE_FIRST_PHYSICAL_PREVIEW_NOT_NATIVE_ACCEPTED")
                self.assertEqual(doc["tier_ids"],active["classes"][cls]["pieces"])
                self.assertEqual(len(doc["four_tier_slots"]),4)
                self.assertEqual(set(doc["ordinary"]),
                                 {"chest","wrists","waist","feet"})
                self.assertEqual(len(doc["common_gear"]),4)
                self.assertEqual(set(doc["weapons"]),
                    set(stage.contracts.WEAPON_FORMS[
                        stage.contracts.lookup(cls,spec)["weapon_form"]]))
                self.assertTrue(doc["original_profile_unchanged"])
                self.assertTrue(doc["weapon_subclass_proficiency_native_unverified"])
                self.assertEqual(doc["native_calls_now"],0)

    def test_unsupported_spec_and_missing_snapshot_fail_closed(self):
        self.assertEqual(self.client.get(
            "/api/v1/season-gear/physical-preview/evoker/augmentation",
            headers=self.header).status_code,404)
        with mock.patch.object(api.season_physical,"load_tier",
                               side_effect=stage.RepresentativeBlocked("TIER_MISSING")):
            res=self.client.get(
                "/api/v1/season-gear/physical-preview/druid/balance",
                headers=self.header)
            self.assertEqual(res.status_code,409)
            self.assertEqual(res.json()["detail"]["code"],
                             "SEASON_PHYSICAL_PREVIEW_UNAVAILABLE")

    def test_unverified_profile_is_not_running_as_product_default(self):
        ctrl=api.sessions.standard_controls(("paladin","retribution"))
        self.assertNotIn("tier_ids",ctrl)
        self.assertNotIn("current_season_gear",ctrl)
        self.assertEqual(len(ctrl["trinket_ids"]),2)

if __name__=="__main__":unittest.main()
