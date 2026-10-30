"""v196: source-driven UI entry preserves native choices and budget gate."""
from __future__ import annotations
import copy, json, pathlib, sys, unittest
from fastapi.testclient import TestClient

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v196_current_season_user_catalog as catalog
import v108_native_consumable_inputs as native
import v113_local_web_api as api

class SourceSeasonUiCatalog(unittest.TestCase):
    def test_real_saved_pinned_v191_enchants_are_grouped_but_not_approved(self):
        c=catalog.public_options()
        self.assertEqual(c["season_build"],"12.1.5.70575")
        self.assertEqual(c["simc_revision"],
                         "710c2408bfd3ae4df71b8cd55cdf01f63fd6c926")
        self.assertEqual(c["source_artifact_id"],12961140046)
        enc=c["enchant_candidates"]
        self.assertEqual(enc["total"],38)
        self.assertEqual(enc["selectable_count"],0)
        self.assertEqual(enc["groups"],{
            "boots":3,"chest":4,"helm":6,"ring":9,"shoulders":6,"weapon":10})
        self.assertTrue(all(not x["ui_selectable"] for x in enc["items"]))
        self.assertEqual({tuple(x["source_slots"]) for x in enc["items"]
            if x["kind"]=="ring"},{("finger1/finger2",)})
        self.assertEqual({tuple(x["source_slots"]) for x in enc["items"]
            if x["kind"]=="weapon"},
            {("WEAPON_SUBCLASS_NOT_YET_USER_SLOT_CERTIFIED",)})
        self.assertEqual(c["native_calls_now"],0)
        self.assertFalse(c["new_approval_granted"])
        self.assertFalse(c["optimizer_or_cache_mutated"])
    def test_existing_real_user_options_unchanged(self):
        c=catalog.public_options()
        for kind in ("food","potion","augmentation"):
            tokens={x["value"] for x in c["proven_native_input_choices"][kind]}
            self.assertEqual(tokens,native.SUPPORTED[kind]|{"source_default"})
        diamond={x["value"] for x in
                 c["proven_native_input_choices"]["diamond_id"]}
        self.assertEqual(diamond,{"0","240967","240983"})
        self.assertEqual(set(c["proven_armor_embellishments"]),{
                         "arcanoweave_lining","sunfire_silk_lining"})
        self.assertIn("FIXED",c["future_categories"]["flask"])
    def test_source_attempted_promotion_fails_closed(self):
        source,_rows,_groups=catalog.read()
        bad=copy.deepcopy(source)
        bad["rows"][0]["approved"]=True
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as td:
            p=pathlib.Path(td)/"tampered.json"
            p.write_text(json.dumps(bad))
            with self.assertRaisesRegex(catalog.CatalogBlocked,
                                        "SOURCE_FIRST_ENCHANT_ROW_INVALID"):
                catalog.public_options(p)
            bad["rows"][0]["approved"]=False
            bad["rows"][0]["inventory_type_mask"]=1<<29
            p.write_text(json.dumps(bad))
            with self.assertRaisesRegex(catalog.CatalogBlocked,
                                        "CURRENT_SEASON_ENCHANT_CATEGORY_COUNTS_INVALID|UNRECOGNIZED"):
                catalog.public_options(p)
    def test_local_http_and_web_view_do_not_offer_unverified_enchant(self):
        client=TestClient(api.create_app(root=ROOT/"__no_runtime_write_v196",
                            token="v196-catalog-test"),
                          base_url="http://127.0.0.1:8765")
        h={"x-simc-local-token":"v196-catalog-test"}
        self.assertEqual(client.get("/api/v1/season-option-catalog").status_code,403)
        resp=client.get("/api/v1/season-option-catalog",headers=h)
        self.assertEqual(resp.status_code,200,resp.text)
        self.assertEqual(resp.json()["enchant_candidates"]["total"],38)
        self.assertEqual(resp.json()["enchant_candidates"]["selectable_count"],0)
        opts=client.get("/api/v1/options",headers=h).json()
        self.assertNotIn("enchant",opts)
        html=client.get("/").text
        js=client.get("/assets/app.js").text
        self.assertIn('id="season-option-catalog-panel"',html)
        self.assertIn("renderSeasonOptionCatalog",js)
        self.assertIn('"/api/v1/season-option-catalog"',js)
        self.assertIn("current_season_product:true",js)
        self.assertNotIn("enchant_choices:selectedGear",js)

if __name__=="__main__":unittest.main()
