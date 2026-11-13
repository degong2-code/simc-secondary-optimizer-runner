"""v167 read-only catalog into UI and ordinary armor-compatible previews."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

# Standalone unittest discovery does not add runner/ to sys.path;
# v167's display-only v332 dependency is intentionally runner-local.
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runner"))
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

    def test_fresh_j_f_unknown_is_preserved_without_making_it_ready(self):
        inp=source()
        inp["consumable_budget_source_mode"]="NEW_SEASON_J_F_BUDGET_EVIDENCE_PENDING"
        inp["consumable_budget_reference"]=None
        result=adapter.from_v166(inp)
        self.assertEqual(result["consumable_budget_source_mode"],
                         "NEW_SEASON_J_F_BUDGET_EVIDENCE_PENDING")
        self.assertTrue(result["J_F_NUMERIC_AUTHENTICATION_NOT_IN_GEAR_COLLECTOR"])
        self.assertEqual(result["item_count"],5)
        self.assertTrue(result["not_certified"]["tier_four_set"])

    def test_reject_conditional_or_uncertified_as_current(self):
        a=source();a["current_candidates"][0]["selection_evidence"]="CONDITIONAL_SEASON_NOT_ESTABLISHED"
        with self.assertRaises(adapter.GearBlocked):
            adapter.from_v166(a)
        b=source();b["current_candidates"][3]["slot"]=5
        with self.assertRaises(adapter.GearBlocked):
            adapter.from_v166(b)

    def test_conditional_worldstate_plain_is_internal_only(self):
        source_doc=source()
        source_doc["internal_conditional_mplus_plain_candidates"]=[{
            "item_id":200,"name":"Conditional M+ Wrist","slot":9,
            "class_id":4,"subclass_id":4,
            "allowed_class_mask":2,"stat_modifier_codes":[4],
            "item_set_id":0,"direct_item_effect_record":False,
            "category":"plain_representative_candidate",
            "selection_evidence":"CONDITIONAL_SEASON_NOT_ESTABLISHED",
            "source_kinds":["mplus_journal"],
            "source_evidence":[{
                "source":"mplus_journal",
                "season_evidence":"UNKNOWN_WORLD_STATE_EXPRESSION",
                "display_season_id":37,"world_state_expression_id":441,
                "journal_encounter_id":10,"journal_instance_id":20}]}]
        source_doc["internal_conditional_mplus_plain_count"]=1
        c=adapter.from_v166(source_doc)
        self.assertEqual(c["internal_conditional_mplus_plain_count"],1)
        self.assertNotIn(200,{x["item_id"] for x in c["items"]})
        self.assertFalse(c["internal_conditional_mplus_plain_candidates"][0][
            "ui_selectable"])
        self.assertNotIn("plain_representative_candidate",
                         adapter.public_options(c)["choices"])
        # A new season may expose no approved current choices yet while
        # the sole WSE-pending same-display-season plain item is available
        # for INTERNAL physical source discovery.
        source_doc["current_candidates"]=[]
        source_doc["current_candidate_count"]=0
        only_pending=adapter.from_v166(source_doc)
        self.assertEqual(only_pending["item_count"],0)
        self.assertEqual(only_pending[
            "internal_conditional_mplus_plain_count"],1)
        self.assertEqual(adapter.public_options(only_pending)["choices"][
            "trinket"],[])
        c["internal_conditional_mplus_plain_candidates"][0]["ui_selectable"]=True
        with self.assertRaisesRegex(adapter.GearBlocked,
                                    "INTERNAL_MPLUS_SOURCE_NOT_PENDING"):
            adapter.validate(c)

    def test_internal_plain_neck_is_not_user_selectable(self):
        src=source()
        src["internal_source_only_plain_neck_candidates"]=[{
            "item_id":200,"name":"Generic neck","slot":2,
            "class_id":4,"subclass_id":0,"allowed_class_mask":-1,
            "stat_modifier_codes":[5],"item_set_id":0,
            "direct_item_effect_record":False,
            "category":"plain_representative_candidate",
            "selection_evidence":"CONDITIONAL_SEASON_NOT_ESTABLISHED",
            "source_expansion_id":11,"internal_generic_G_only":True,
            "user_selectable_candidate":False,
            "source_kinds":["raid_journal"],
            "source_evidence":[{"source":"raid_journal"}]}]
        src["internal_source_only_plain_neck_count"]=1
        row=adapter.from_v166(src)
        self.assertEqual(row["internal_source_only_plain_neck_count"],1)
        self.assertNotIn(200,{x["item_id"] for x in row["items"]})
        visible=adapter.public_options(row)["choices"]
        self.assertNotIn(200,{x["item_id"] for v in visible.values() for x in v})
        tampered=copy.deepcopy(row)
        tampered["internal_source_only_plain_neck_candidates"][0][
            "ui_selectable"]=True
        with self.assertRaisesRegex(adapter.GearBlocked,
                                     "PRODUCT_INTERNAL_SOURCE_NECK_NOT_JUSTIFIED"):
            adapter.validate(tampered)

    def test_internal_plain_ring_not_ui_and_tampering_blocked(self):
        src=source()
        src["internal_source_only_plain_ring_candidates"]=[{
            "item_id":201,"name":"Generic ring","slot":11,
            "class_id":4,"subclass_id":0,"allowed_class_mask":-1,
            "stat_modifier_codes":[5],"item_set_id":0,
            "direct_item_effect_record":False,
            "category":"plain_representative_candidate",
            "selection_evidence":"CONDITIONAL_SEASON_NOT_ESTABLISHED",
            "source_expansion_id":11,"internal_generic_G_only":True,
            "user_selectable_candidate":False,
            "source_kinds":["raid_journal"],
            "source_evidence":[{"source":"raid_journal"}]}]
        src["internal_source_only_plain_ring_count"]=1
        row=adapter.from_v166(src)
        self.assertEqual(row["internal_source_only_plain_ring_count"],1)
        self.assertNotIn(201,{x["item_id"] for x in row["items"]})
        visible=adapter.public_options(row)["choices"]
        self.assertNotIn(201,{x["item_id"] for v in visible.values() for x in v})
        tampered=copy.deepcopy(row)
        tampered["internal_source_only_plain_ring_candidates"][0][
            "ui_selectable"]=True
        with self.assertRaisesRegex(adapter.GearBlocked,
                                     "PRODUCT_INTERNAL_SOURCE_RING_NOT_JUSTIFIED"):
            adapter.validate(tampered)

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
