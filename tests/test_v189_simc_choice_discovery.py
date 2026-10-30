"""v189 on-demand pinned SimC registry, pure offline no API or Native."""
import hashlib,json,pathlib,sys,tempfile,unittest
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v189_simc_consumable_embellishment_discovery as catalog
import v108_native_consumable_inputs as before

PIN="7bc10711b5a4514066fa402ca0a71c9ba4b7c9dd"
SOURCE="""// Complete minimal test fixture; no real DBC or Native.
void register_special_effects()
{
  // Food
  unique_gear::register_special_effect( 1259656, consumables::selector_food( 1232091, true ) ); // blooming feast
  unique_gear::register_special_effect( 1232909, consumables::secondary_food( 1232491, STAT_MASTERY_RATING ) ); // glitter skewers
  // Flasks
  // Potions
  register_special_effect( 1236994, consumables::potion_of_recklessness );
  set_min_version( wowv_t( 12, 1, 0 ) );
  register_special_effect( 1295132, consumables::liquid_luster, true );
  reset_version_check();
  // Oils
  // Embellishments & Tinkers
  register_special_effect( 1283697, embellishments::arcanoweave_lining );
  register_special_effect( 1251905, DISABLED_EFFECT ); // unsupported gemstone bandolier
  set_min_version( wowv_t( 12, 1, 0 ) );
  register_special_effect( 1296550, embellishments::snakeskin_lining );
  reset_version_check();
  // Darkmoon Trinkets & Embellishments
  register_special_effect( { 1245001, 1245053 }, darkmoon::blood );
  // Trinkets
}
"""
class SimCEffectCandidateDiscovery(unittest.TestCase):
    def test_registry_categories_versions_origin_and_no_approval(self):
        receipt=catalog.discover(SOURCE.encode("utf8"),PIN)
        self.assertEqual(receipt["counts"],{
           "food_handler_registrations":2,"potion_handler_registrations":2,
           "embellishment_and_darkmoon_registrations":4,
           "disabled_embellishment_registrations":1})
        self.assertEqual(receipt["source"]["sha256"],
             hashlib.sha256(SOURCE.encode()).hexdigest())
        self.assertEqual(receipt["source"]["commit"],PIN)
        self.assertTrue(receipt["source_only_not_native"])
        self.assertFalse(receipt["auto_promote_to_user_ui"])
        self.assertEqual(receipt["new_native_calls"],0)
        self.assertEqual(receipt["candidates"]["potion"][1]["minimum_game_version"],
                         [12,1,0])
        self.assertEqual(receipt["candidates"]["embellishment_or_darkmoon"][3]["spell_ids"],
                         [1245001,1245053])
        self.assertFalse(receipt["candidates"]["embellishment_or_darkmoon"][1]["implemented"])
        self.assertTrue(all(x["ui_selectable"] is False
             for v in receipt["candidates"].values() for x in v))
        self.assertIn("FOOD_AND_POTION_ITEM_LIST_FROM_SAME_BUILD_SIMC_DBC",
                      receipt["unresolved_requirements"])
    def test_fail_closed_on_schema_or_unparsed_registration(self):
        cases=[
          SOURCE.replace("  // Flasks","  // Flasks MISSING"),
          SOURCE.replace("1236994","1234 + 2"),
          SOURCE.replace("1296550","1251905"),
          SOURCE.replace("  // Food","  // Drinks"),
          SOURCE.replace("set_min_version( wowv_t( 12, 1, 0 ) );",
                         "set_min_version( unknown_build );",1),
          SOURCE+SOURCE,
        ]
        for raw in cases:
            with self.subTest(raw=raw[-35:]):
                with self.assertRaises((catalog.DiscoveryBlocked,ValueError)):
                    catalog.discover(raw.encode("utf8"),PIN)
    def test_source_path_must_be_pinned_and_will_not_call_network(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            source=root/"native.cpp";source.write_text(SOURCE)
            report=root/"receipt.json"
            with mock.patch.object(catalog,"urlopen",
                                   side_effect=AssertionError("NO_HTTP_ALLOWED")):
                self.assertEqual(catalog.main([
                    "--simc-commit",PIN,"--source",str(source),
                    "--source-sha256",hashlib.sha256(SOURCE.encode()).hexdigest(),
                    "--out",str(report)]),0)
            receipt=json.loads(report.read_text())
            self.assertEqual(receipt["status"],
                             "DISCOVERED_EFFECT_HANDLERS_NOT_PUBLISHED")
            with self.assertRaises(catalog.DiscoveryBlocked):
                catalog.main(["--simc-commit",PIN,
                     "--source",str(source),"--out",str(root/"bad.json")])
    def test_no_change_to_previous_user_consumable_contract(self):
        self.assertEqual(before.SUPPORTED["food"],
                         frozenset({"harandar_celebration","silvermoon_parade",
                           "royal_roast","blooming_feast","disabled"}))
        self.assertEqual(before.SUPPORTED["potion"],
                         frozenset({"potion_of_recklessness_2",
                           "lights_potential_2","liquid_luster_2","disabled"}))
if __name__=="__main__":unittest.main()
