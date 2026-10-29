"""v170: season physical composer is internal, never a user-facing API."""
import pathlib,sys,unittest
from fastapi.testclient import TestClient
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v113_local_web_api as api
import v169_source_first_representative_stage as stage
import v167_product_season_gear_adapter as gear

class InternalPhysicalPreview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client=TestClient(api.create_app(token="local-only"),
                              base_url="http://127.0.0.1:8765")
        cls.header={"x-simc-local-token":"local-only"}

    def test_all_26_internal_staged_tier_and_weapon_ids_only(self):
        source=gear.read();tier=stage.load_tier()
        self.assertEqual(len(api.sessions.SUPPORTED),26)
        for cls,spec in api.sessions.SUPPORTED:
            with self.subTest(spec=cls+"/"+spec):
                doc=stage.select_class_spec(source,tier,cls,spec)
                self.assertEqual(doc["tier_ids"],tier["classes"][cls]["pieces"])
                self.assertEqual(len(doc["four_tier_slots"]),4)
                self.assertEqual(set(doc["ordinary"]),
                                 {"chest","wrists","waist","feet"})
                self.assertEqual(set(doc["weapons"]),
                    set(stage.contracts.WEAPON_FORMS[
                        stage.contracts.lookup(cls,spec)["weapon_form"]]))
                self.assertTrue(doc["weapon_subclass_proficiency_native_unverified"])
                self.assertEqual(doc["native_calls"],0)

    def test_no_user_facing_ordinary_or_physical_gear_routes(self):
        for uri in (
            "/api/v1/season-gear/representative/paladin/retribution",
            "/api/v1/season-gear/physical-preview/druid/balance"):
            with self.subTest(uri=uri):
                self.assertEqual(self.client.get(uri,headers=self.header).status_code,404)

    def test_default_user_scenario_never_exposes_ordinary_choice(self):
        ctrl=api.sessions.standard_controls(("paladin","retribution"))
        self.assertNotIn("tier_ids",ctrl)
        self.assertNotIn("current_season_gear",ctrl)
        self.assertNotIn("ordinary",ctrl)
        self.assertEqual(len(ctrl["trinket_ids"]),2)

if __name__=="__main__":
    unittest.main()
