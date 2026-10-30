"""v188 user-readable labels and physical category safety; zero SimC Native."""
from __future__ import annotations
import json,pathlib,sys,unittest
from fastapi.testclient import TestClient

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v108_native_consumable_inputs as simc
import v188_user_choice_metadata as descriptions
import v113_local_web_api as app

class ChoiceLabelsAndSlots(unittest.TestCase):
    def setUp(self):
        self.client=TestClient(app.create_app(root=ROOT/"unused-test-runs",
                                              token="metadata-offline"),
                               base_url="http://127.0.0.1:8765")
        self.auth={"x-simc-local-token":"metadata-offline"}
    def test_choice_labels_cover_exact_approved_simc_tokens_and_diamonds(self):
        data=descriptions.labels()
        for kind in ("food","potion","augmentation"):
            self.assertEqual(set(data[kind]),{"source_default",*simc.SUPPORTED[kind]})
            for token,label in data[kind].items():
                self.assertTrue(label and len(label)>=5)
                self.assertNotEqual(token,label)
        self.assertEqual(set(data["diamond_id"]),{"0","240967","240983"})
        self.assertIn("치명타",data["diamond_id"]["240967"])
        self.assertIn("주능력치 +32",data["diamond_id"]["240983"])
        self.assertIn("효과 상세 미확인",data["potion"]["liquid_luster_2"])
    def test_runtime_unchanged_public_options_add_metadata_only(self):
        resp=self.client.get("/api/v1/options",headers=self.auth)
        self.assertEqual(resp.status_code,200)
        doc=resp.json()
        self.assertEqual(doc["diamond_id"],[0,240967,240983])
        for kind in ("food","potion","augmentation"):
            self.assertEqual(doc[kind][0],"source_default")
            self.assertEqual(set(doc[kind])-{"source_default"},simc.SUPPORTED[kind])
        self.assertEqual(doc["display_labels"],descriptions.labels())
        self.assertEqual(doc["embellishments"],json.loads(json.dumps(descriptions.public_embellishments())))
        self.assertEqual(len(doc["embellishments"]),2)
        self.assertNotIn("flask",doc)
    def test_lining_only_armor_and_no_unverified_jewelry_weapon_token(self):
        for token,data in descriptions.public_embellishments().items():
            with self.subTest(token=token):
                self.assertEqual(data["category"],"armor")
                self.assertEqual(set(data["slots"]),descriptions.ARMOR_SLOTS)
                for disallowed in ("neck","finger1","finger2","main_hand","off_hand"):
                    with self.assertRaisesRegex(ValueError,"WRONG_EQUIPMENT_CATEGORY"):
                        descriptions.check_embellishment(token,disallowed,
                          lambda ok,msg:None if ok else (_ for _ in ()).throw(ValueError(msg)))
        self.assertNotIn("darkmoon_sigil_void",descriptions.public_embellishments())
    def test_html_hides_legacy_batch_and_default_toggle_js_forces_season(self):
        html=self.client.get("/").text
        js=self.client.get("/assets/app.js").text
        self.assertNotIn('id="current_season_product"',html)
        self.assertNotIn('id="batch-table"',html)
        self.assertNotIn("24개 전문화 실측 결과",html)
        self.assertIn("current_season_product:true",js)
        self.assertIn("function specialAllowedSlots(item)",js)
        self.assertIn("function refreshSpecialSlots()",js)
        self.assertIn("function syncCraftRow(row,restored=false)",js)
        self.assertIn("options.display_labels",js)
        self.assertIn('const isPrivate=',js)
        self.assertNotIn("showNativeBatch",js)
    def test_default_source_tokens_preserve_exact_existing_simc_entry(self):
        import v106_user_session_controller as user
        original=user.standard_controls(("mage","frost"))
        c=user.user_scenario(original)
        self.assertEqual(c["consumable_choices"],{
            "flask":"source_default","food":"source_default",
            "potion":"source_default","augmentation":"source_default",
            "diamond_id":0,"omnium_talents":"source_default"})

if __name__=="__main__":unittest.main()
