"""P3-CR: real Wago header-shaped masks joined to original v281 source.

Synthetic fixtures only. No actual Wago calls, Native, budget or UI READY.
"""
import io
import json
import pathlib
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v285_consumable_weapon_source as v285
import v281_consumable_simc_relation as v281
import v286_representative_oil_source_binding as v286
from tests.test_v281_consumable_simc_relation import (
    SOURCE,TMP,FLASK,CSV,BUILD)

WEAPON=b"""ID,SpellID,EquippedItemClass,EquippedItemInvTypes,EquippedItemSubclass
254979,211,2,73572352,983039
254980,212,2,73572352,983039
"""
class Fake(io.BytesIO):
    status=200
    def __enter__(self):return self
    def __exit__(self,*args):self.close()

class WeaponMaskSourceTests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root=pathlib.Path(t.name)
        effects=self.root/"effects.csv";effects.write_bytes(CSV)
        self.original=v281.correlate(
             SOURCE,v281.scan_spell_effects(effects,{111,211,212}),
             TMP,build=BUILD,flask_dbc_rows=FLASK)
        self.candidate=self.root/"source"/"v284_simc_consumable_relations.json"
        self.candidate.parent.mkdir()
        self.candidate.write_text(json.dumps(self.original),encoding="utf8")
        self.source={"candidate_path":str(self.candidate),
                     "source_stage":{"status":"EXECUTED_AND_SEALED",
                                     "receipt_sha256":"b"*64}}
        self.mock_hit=[]
    def transport(self,req,timeout):
        self.mock_hit.append(req.full_url)
        return Fake(WEAPON)
    def test_real_wago_columns_source_masks_no_false_approval(self):
        p=self.root/"weapon.csv";p.write_bytes(WEAPON)
        rows=v285.scan(p,{211,212})
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[0]["equipped_item_class"],2)
        self.assertEqual(rows[0]["inventory_type_mask"],73572352)
        self.assertEqual(rows[0]["weapon_subclass_mask"],983039)
        o=v285.attach(self.original,rows,BUILD)
        oil=o["items"][1]["weapon_spell_equipped_source"]
        self.assertEqual(oil["status"],"EXACT_SAME_BUILD_WEAPON_MASK_SOURCE_ONLY")
        self.assertEqual(oil["source_rows"][0]["spell_id"],211)
        self.assertFalse(oil["weapon_and_hand_applicability_verified"])
        self.assertFalse(oil["same_effect_quality_group_verified"])
        self.assertEqual(o["weapon_equipped_source"]["exact_mask_join_candidates"],1)
        self.assertFalse(o["automatic_ui_promotion"])
        self.assertIsNone(o["weapon_equipped_source"]["O"])
        self.assertIsNone(o["weapon_equipped_source"]["F"])
    def test_one_real_source_fetch_then_zero_reuse_and_tamper_block(self):
        kw=dict(stage_root=self.root,build=BUILD,
                consumables=self.source,transport=self.transport)
        first=v285.collect(**kw)
        self.assertEqual(first["status"],"EXACT_SAME_BUILD_WEAPON_MASK_SOURCE_ONLY",first)
        self.assertEqual(first["network_calls_by_stage"],1)
        self.assertEqual(first["counts"]["exact_mask_join_candidates"],1)
        second=v285.collect(**kw)
        self.assertEqual(second["network_calls_by_stage"],0)
        self.assertEqual(second["source_stage"]["status"],"REUSED_VERIFIED")
        self.assertEqual(len(self.mock_hit),1)
        pathlib.Path(first["candidate_path"]).write_bytes(b"MODIFIED")
        third=v285.collect(**kw)
        self.assertEqual(third["status"],"WEAPON_MASK_SOURCE_PENDING")
        self.assertEqual(third["network_calls_by_stage"],0)
        self.assertEqual(len(self.mock_hit),1)
    def test_preparation_reads_only_original_candidate_and_never_admits(self):
        first=v285.collect(stage_root=self.root,build=BUILD,
                           consumables=self.source,transport=self.transport)
        self.assertEqual(first["status"],"EXACT_SAME_BUILD_WEAPON_MASK_SOURCE_ONLY")
        projection=v286.preparation_options_from_sealed_stage(
            stage_root=self.root,game_build=BUILD)
        self.assertEqual(projection["status"],"OIL_PREPARATION_SOURCE_IDENTIFIED",projection)
        self.assertEqual([x["physical_item_id"] for x in projection["items"]],[601])
        self.assertEqual(projection["items"][0]["source_quality_rank"],2)
        self.assertFalse(projection["items"][0]["user_selectable"])
        self.assertFalse(projection["quality_equivalence_verified"])
        self.assertEqual(projection["native_calls"],0)
        self.assertEqual(projection["network_calls"],0)
        self.assertEqual(len(self.mock_hit),1)
        wrong=v286.preparation_options_from_sealed_stage(
            stage_root=self.root,game_build="12.2.0.99998")
        self.assertEqual(wrong["items"],[])
        self.assertEqual(wrong["reason"],"V286_OIL_PREPARATION_BUILD_OR_SOURCE_DRIFT")
        pathlib.Path(first["candidate_path"]).write_bytes(b"MODIFIED")
        tampered=v286.preparation_options_from_sealed_stage(
            stage_root=self.root,game_build=BUILD)
        self.assertEqual(tampered["items"],[])
        self.assertEqual(tampered["reason"],"V286_OIL_CANDIDATE_SIZE_DRIFT")
        self.assertEqual(len(self.mock_hit),1)

    def test_missing_preparation_stage_does_not_block_base(self):
        result=v286.preparation_options_from_sealed_stage(
            stage_root=self.root,game_build=BUILD)
        self.assertEqual(result["status"],"OIL_PREPARATION_SOURCE_PENDING")
        self.assertEqual(result["items"],[])
        self.assertEqual(result["reason"],"V286_OIL_PREPARATION_STAGE_MISSING")

    def test_missing_exact_simc_source_causes_no_http(self):
        p=v285.collect(stage_root=self.root,build=BUILD,consumables={},
                      transport=lambda *_:self.fail("UNEXPECTED_NETWORK"))
        self.assertEqual(p["network_calls_by_stage"],0)
        self.assertEqual(p["status"],"WEAPON_MASK_SOURCE_PENDING")
        self.assertIsNone(p["F"]);self.assertIsNone(p["O"])
    def test_missing_source_or_conflicting_weapon_masks_is_pending(self):
        rows=[{"row_id":1,"spell_id":211,
               "equipped_item_class":2,"inventory_type_mask":73572352,
               "weapon_subclass_mask":983039},
              {"row_id":2,"spell_id":211,
               "equipped_item_class":2,"inventory_type_mask":8,
               "weapon_subclass_mask":983039}]
        doc=v285.attach(self.original,rows,BUILD)
        p=doc["items"][1]["weapon_spell_equipped_source"]
        self.assertEqual(p["status"],"WEAPON_MASK_OR_SIMC_EFFECT_SOURCE_PENDING")
        self.assertIsNone(p["inventory_type_mask"])
    def test_nonweapon_gear_class_is_not_oil_eligible(self):
        doc=v285.attach(self.original,[{"row_id":1,"spell_id":211,
               "equipped_item_class":4,"inventory_type_mask":73572352,
               "weapon_subclass_mask":983039}],BUILD)
        self.assertEqual(doc["weapon_equipped_source"][
                         "exact_mask_join_candidates"],0)
if __name__=="__main__":unittest.main()
