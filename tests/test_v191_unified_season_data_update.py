"""v191 unified, explicitly patch-triggered catalog with source quality dedup."""
from __future__ import annotations
import copy, pathlib, sys, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v191_unified_season_data_update as u

PERM=b"""// Permanent item enchants, wow build 12.1.5.70448
static constexpr std::array<permanent_enchant_entry_t, 5> __permanent_enchant_data { {
  { 6614,  1,  4, 0x00100020, 0x0000001f, "accelerated_agility" },
  { 6615,  2,  4, 0x00100020, 0x0000001f, "accelerated_agility" },
  { 6616,  3,  4, 0x00100020, 0x0000001f, "accelerated_agility" },
  { 7777,  3,  4, 0x00000800, 0x0000001f, "accelerated_agility" },
  { 8765,  2,  4, 0x00100020, 0x0000001f, "different_effect" },
} };
"""
TEMP=b"""// Temporary item enchants, wow build 12.1.5.70448
static constexpr std::array<temporary_enchant_entry_t, 3> __temporary_enchant_data { {
  {  7523,  1,  1212345, "somestrength_oil" },
  {  7524,  2,  1212346, "somestrength_oil" },
  {  7525,  3,  1212347, "somestrength_oil" },
} };
"""
GEMS=b"""// Gem properties, wow build 12.1.5.70448
static constexpr std::array<gem_property_data_t, 2> __gem_property_data { {
  { 12345, 3456, 0x00000002, 0 }, // primary
  { 12346, 3457, 0x00000008, 0 }, // secondary
} };
"""
class UnifiedCatalogTest(unittest.TestCase):
    def test_permanent_enchant_slot_masks_and_highest_quality(self):
        src=u.parse_generated("permanent_enchant",PERM)
        rows=u.highest_known_quality(src["rows"],"permanent_enchant")
        self.assertEqual(src["source_build"],"12.1.5.70448")
        self.assertEqual(len(rows),3)
        self.assertEqual([x["enchant_id"] for x in rows],[6616,7777,8765])
        cloth_chest=next(x for x in rows if x["enchant_id"]==6616)
        self.assertEqual(u.inventory_options(cloth_chest),[5,20])
        self.assertNotIn(11,u.inventory_options(cloth_chest))
        self.assertEqual(u.inventory_options({"inventory_type_mask":0}),[])
    def test_midnight_named_enchants_keep_only_best_quality_and_skip_tools(self):
        src=u.parse_generated("permanent_enchant",PERM)
        rows=[dict(x) for x in src["rows"]]
        rows.extend([
          {"enchant_id":8018,"quality_rank":1,"item_class":4,
           "inventory_type_mask":1<<8,"item_subclass_mask":31,
           "simc_token":"enchant_boots__farstriders_hunt"},
          {"enchant_id":8019,"quality_rank":2,"item_class":4,
           "inventory_type_mask":1<<8,"item_subclass_mask":31,
           "simc_token":"enchant_boots__farstriders_hunt"},
          {"enchant_id":7975,"quality_rank":2,"item_class":19,
           "inventory_type_mask":1<<29,"item_subclass_mask":0,
           "simc_token":"enchant_tool__amani_perception"}
        ])
        src["rows"]=rows
        selected=u.current_season_enchant_candidates(src)
        self.assertEqual(len(selected),1)
        self.assertEqual(selected[0]["enchant_id"],8019)
        self.assertEqual(selected[0]["inventory_type_options"],[8])
        self.assertFalse(selected[0]["user_selectable"])

    def test_temporary_and_gem_data_not_confused_with_item_ids(self):
        tmp=u.parse_generated("temporary_enchant",TEMP)
        rows=u.highest_known_quality(tmp["rows"],"temporary_enchant")
        self.assertEqual([x["enchant_id"] for x in rows],[7525])
        gems=u.parse_generated("gem_property",GEMS)
        self.assertEqual(gems["declared_rows"],2)
        self.assertEqual(gems["rows"][0]["gem_item_id"],"UNRESOLVED")
    def test_strongest_effect_only_when_scalar_proven_and_same_slot(self):
        x={"kind":"food","effect_fingerprint":"haste_buff","allowed_slots":[],
           "quality_rank":2,"effect_strength":45,"id":1}
        y=dict(x,id=2,quality_rank=3,effect_strength=60)
        z=dict(x,id=3,quality_rank=3,effect_strength=80)
        other=dict(x,id=4,effect_fingerprint="crit_buff")
        ring=dict(x,id=5,kind="enchant",allowed_slots=["finger1"])
        best=u.highest_effect_variants([x,y,z,other,ring])
        self.assertEqual({r["id"] for r in best},{3,4,5})
        ukn=dict(x,id=6,effect_strength="UNKNOWN")
        keep=u.highest_effect_variants([x,ukn])
        self.assertEqual(len(keep),2)
    def test_bad_incomplete_enchant_source_fails_not_silent(self):
        with self.assertRaisesRegex(u.CatalogBlocked,"ROW_COUNT_MISMATCH"):
            u.parse_generated("permanent_enchant",
                PERM.replace(b"array<permanent_enchant_entry_t, 5>",
                             b"array<permanent_enchant_entry_t, 6>"))
        with self.assertRaisesRegex(u.CatalogBlocked,"UNPARSED"):
            u.parse_generated("temporary_enchant",
                              TEMP.replace(b"1212345",b"NOTNUMERIC"))
    def test_actual_source_catalog_assemble_readonly_unpublished(self):
        import json
        gear=json.loads((ROOT/"data/current_season_product_gear_db.json").read_text())
        tier=json.loads((ROOT/"data/current_season_tier_itemsets.json").read_text())
        budget=json.loads((ROOT/"data/current_season_chmv_consumables.json").read_text())
        pinned="7bc10711b5a4514066fa402ca0a71c9ba4b7c9dd"
        effects={"schema":"v189_pinned_simc_effect_registration_candidates_v1",
           "auto_promote_to_user_ui":False,
           "source":{"commit":pinned,"sha256":"a"*64},
           "candidates":{"embellishment_or_darkmoon":[{
             "kind":"embellishment_or_darkmoon",
             "spell_ids":[1283697],"handler":"embellishments::arcanoweave_lining",
             "implemented":True,"ui_selectable":False}]}}
        consumables={"schema":"v190_same_build_consumable_item_candidates_v1",
           "automatic_ui_promotion":False,
           "source":{"wago_snapshot_build":"12.1.5.70575",
                     "simc_revision":pinned,
                     "simc_registration_sha256":"a"*64},
           "items":[{"item_id":500001,"kind":"food"},
                    {"item_id":500002,"kind":"potion"}]}
        generated={"permanent_enchant":u.parse_generated("permanent_enchant",PERM),
                   "temporary_enchant":u.parse_generated("temporary_enchant",TEMP),
                   "gem_property":u.parse_generated("gem_property",GEMS)}
        result=u.compile_catalog(gear,tier,budget,effects,consumables,
                                 generated,event="mid_patch")
        self.assertEqual(result["gear"]["count"],511)
        self.assertEqual(len(result["gear"]["candidates"]),511)
        self.assertEqual(result["gear"]["candidates"][0]["inventory_type"],3)
        self.assertEqual(result["tier"]["piece_count"],65)
        self.assertEqual(len(result["tier"]["classes"]),13)
        self.assertEqual(result["tier"]["classes"]["deathknight"]["pieces"]["head"],271474)
        self.assertEqual(result["related_source_counts"],{
            "gear_item_candidates":511,"tier_piece_ids":65,
            "food_raw_item_candidates":1,"potion_raw_item_candidates":1,
            "food_handler_registrations":0,"potion_handler_registrations":0,
            "embellishment_darkmoon_registrations":1,
            "temporary_enchant_entries":3,"gem_property_records":2})
        self.assertEqual(result["consumables"]["food"]["candidates"][0]["item_id"],500001)
        self.assertFalse(result["automatic_ui_promotion"])
        self.assertTrue(result["historical_cache_modified"] is False)
        self.assertEqual(result["native_calls"],0)
        self.assertIn("SIMC_COMPILED_DBC_AND_GAME_DB2_BUILDS_DIFFER_REVIEW",
                      result["warnings"])
        bad=copy.deepcopy(tier);bad["retail_build"]="0.0.0.0"
        with self.assertRaisesRegex(u.CatalogBlocked,"CORE_BUILD"):
            u.compile_catalog(gear,bad,budget,effects,consumables,
                              generated,event="mid_patch")
        with self.assertRaisesRegex(u.CatalogBlocked,"UPDATE_EVENT_NOT_EXPLICIT"):
            u.compile_catalog(gear,tier,budget,effects,consumables,
                              generated,event="daily_auto_poll")
if __name__=="__main__":unittest.main()
