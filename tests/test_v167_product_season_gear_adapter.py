"""v167 read-only catalog into UI and ordinary armor-compatible previews."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest

from runner import v167_product_season_gear_adapter as adapter


def source():
    def row(i, name, category, slot, cl, sub):
        return {"item_id":i,"name":name,"category":category,"slot":slot,
                "class_id":cl,"subclass_id":sub,"allowed_class_mask":-1,
                "stat_modifier_codes":[5,24],"item_set_id":0,
                "source_kinds":["raid_journal"],
                "selection_evidence":"CURRENT_CANDIDATE"}
    return {
        "schema":"v166_current_season_product_gear_db_v1",
        "status":"COMPACT_CANDIDATE_DB_WITH_PENDING_GAPS",
        "season_build":"12.1.5.70575","expansion_id":11,"display_season_id":37,
        "current_candidate_count":5,"conditional_count":2,
        "no_old_catalog_seed":True,"native_calls":0,
        "current_candidates":[
            row(101,"Plate Wrist","plain_representative_candidate",9,4,4),
            row(102,"Cloth Wrist","plain_representative_candidate",9,4,1),
            row(103,"Everyone Cloak","plain_representative_candidate",16,4,1),
            row(104,"Delve Trinket","trinket",12,4,0),
            row(105,"Craftable Boots","selectable_stat_craft",8,4,4)]}


class ProductAdapterTests(unittest.TestCase):
    def test_only_user_effect_choices_and_craft_id_exception(self):
        c=adapter.from_v166(source())
        options=adapter.public_options(c)
        self.assertEqual(c["item_count"],5)
        self.assertFalse(options["manual_exact_id_allowed"])
        self.assertEqual(options["manual_exact_id_exception"],"CRAFTED_EQUIPMENT_VARIANTS_ONLY")
        self.assertEqual(len(options["choices"]["trinket"]),1)
        self.assertEqual(options["choices"]["trinket"][0]["name"],"Delve Trinket")
        self.assertNotIn("plain_representative_candidate",options["choices"])
        self.assertFalse(options["ordinary_equipment_user_selectable"])
        self.assertEqual(c["conditional_ids_excluded"],2)
        self.assertEqual(c["new_native_calls"],0)

    def test_plain_representative_is_nonmutating_and_class_family_filtered(self):
        c=adapter.from_v166(source())
        plate=adapter.ordinary_candidates(c,"plate")
        cloth=adapter.ordinary_candidates(c,"cloth")
        self.assertEqual([x["item_id"] for x in plate["candidate_slots"]["wrists"]],[101])
        self.assertEqual([x["item_id"] for x in cloth["candidate_slots"]["wrists"]],[102])
        self.assertEqual([x["item_id"] for x in plate["candidate_slots"]["back"]],[103])
        self.assertFalse(plate["tier_four_piece_id_confirmed"])
        self.assertFalse(plate["weapon_profile_confirmed"])
        self.assertEqual(plate["status"],"PREVIEW_ONLY_NOT_A_PROFILE")

    def test_reject_conditional_or_uncertified_as_current(self):
        a=source();a["current_candidates"][0]["selection_evidence"]="CONDITIONAL_SEASON_NOT_ESTABLISHED"
        with self.assertRaises(adapter.GearBlocked):
            adapter.from_v166(a)
        b=source();b["current_candidates"][3]["slot"]=5
        with self.assertRaises(adapter.GearBlocked):
            adapter.from_v166(b)

    def test_unknown_roles_counts_and_tier_fail_closed(self):
        doc=adapter.from_v166(source())
        doc["role_counts"]["trinket"]=20
        with self.assertRaises(adapter.GearBlocked):
            adapter.public_options(doc)
        doc=adapter.from_v166(source())
        doc["not_certified"]["tier_four_set"]=False
        with self.assertRaises(adapter.GearBlocked):
            adapter.validate(doc)
        with self.assertRaises(adapter.GearBlocked):
            adapter.ordinary_candidates(adapter.from_v166(source()),"mail",
                                        slots=("main_hand",))

    def test_determinism_and_round_trip(self):
        d=adapter.from_v166(source())
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"season.json"
            p.write_text(json.dumps(d))
            self.assertEqual(adapter.read(p),d)
        self.assertEqual(adapter.from_v166(source()),d)

    def test_real_saved_v166_when_provided(self):
        p=os.environ.get("SIMC_V166_PRODUCT_GEAR_DB")
        if not p:
            self.skipTest("real v166 artifact not supplied to offline test")
        doc=adapter.from_v166(json.loads(Path(p).read_text()))
        self.assertEqual(doc["item_count"],288)
        self.assertEqual(doc["role_counts"],{
            "plain_representative_candidate":136,
            "selectable_stat_craft":106,
            "special_effect_gear_candidate":10,
            "trinket":36})
        self.assertEqual(doc["conditional_ids_excluded"],225)
        self.assertEqual(doc["new_native_calls"],0)


if __name__=="__main__":
    unittest.main()
