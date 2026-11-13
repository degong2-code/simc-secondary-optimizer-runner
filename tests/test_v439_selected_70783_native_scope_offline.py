"""v439 one 70783 selected crafted MAIL head/4pc Native scope, offline.

Pure request+scope checks: they do not call SimC, season APIs, or mark B8
complete. The Windows one-shot workflow owns any actual product evidence.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"runner"))
from integration_probes import p1_v439_one_selected_70783_native as p

class SelectedNativeBoundedScope(unittest.TestCase):
    def setUp(self):
        self.missing=[
            {"slot":"head","item_id":271440,
             "identity":{"season":"midnight_s2","slot":"head",
                         "item_id":271440,"ilevel":334,"options":{}}},
            {"slot":"head","item_id":p.CRAFTED_MAIL_HEAD_ID,
             "identity":{"season":"midnight_s2","slot":"head",
                         "item_id":p.CRAFTED_MAIL_HEAD_ID,"ilevel":334,
                         "options":dict(p.CRAFTED_OPTIONS)}},
            {"slot":"chest","item_id":268222,
             "identity":{"season":"midnight_s2","slot":"chest",
                         "item_id":268222,"ilevel":334,"options":{}}},
            {"slot":"chest","item_id":271495,
             "identity":{"season":"midnight_s2","slot":"chest",
                         "item_id":271495,"ilevel":334,"options":{}}},
        ]
        self.pre={"status":
            "B8_SELECTED_PROFILE_STATIC_VARIANTS_PENDING_NO_NATIVE",
            "budget_preflight":{
                "changed_physical_slots":[
                    {"slot":"head","previous_id":271440,
                     "selected_id":p.CRAFTED_MAIL_HEAD_ID},
                    {"slot":"chest","previous_id":268222,
                     "selected_id":271495}],
                "four_tier_slots":["chest","hands","legs","shoulders"],
                "crafted_first_split_is_not_L":True,
                "missing_exact_native_variants":self.missing}}

    def test_only_four_missing_exact_two_changed_slots(self):
        self.assertEqual(p.checked_change_scope(self.pre),self.missing)
        self.assertEqual(p.MAX_MISSING_STATIC_NATIVE,4)
        self.assertEqual(p.MAX_DPS_NATIVE,6)
        self.assertEqual(p.MAX_TOTAL_NATIVE,13)

    def test_real_simc_crafted_token_from_upstream_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=p.stats_source(self.missing[1]["identity"],
                               pathlib.Path(tmp)/"result.json")
        self.assertIn("head=selected_244579,id=244579,ilevel=334",src)
        self.assertIn("crafted_stats=32/36",src)
        self.assertIn("embellishment=arcanoweave_lining",src)
        self.assertIn("spec=marksmanship",src)
        self.assertIn("iterations=1",src)
        self.assertIn("actions=wait,sec=1",src)
        self.assertNotIn("gear_crit_rating=",src)

    def test_any_nonchanged_slot_in_static_query_is_blocked(self):
        self.pre["budget_preflight"]["missing_exact_native_variants"][0][
            "slot"]="waist"
        with self.assertRaisesRegex(RuntimeError,
                                    "EXACT_STATIC_MISSING_OUTSIDE"):
            p.checked_change_scope(self.pre)

    def test_more_than_four_native_static_variants_not_allowed(self):
        self.pre["budget_preflight"]["missing_exact_native_variants"]+= [
            {"slot":"head","item_id":999999,"identity":{
                "season":"midnight_s2","slot":"head",
                "item_id":999999,"ilevel":334,"options":{}}}]
        with self.assertRaisesRegex(RuntimeError,
                                    "EXACT_STATIC_MISSING_OUTSIDE"):
            p.checked_change_scope(self.pre)

    def test_missing_selected_four_tier_or_class_head_blocks(self):
        self.pre["budget_preflight"]["four_tier_slots"]=[
            "head","hands","legs","shoulders"]
        with self.assertRaisesRegex(RuntimeError,
                                    "SOURCE_SELECTED_HEAD_CHEST"):
            p.checked_change_scope(self.pre)
        self.pre["budget_preflight"]["four_tier_slots"]=[
            "chest","hands","legs","shoulders"]
        self.pre["budget_preflight"]["changed_physical_slots"][0][
            "selected_id"]=1
        with self.assertRaisesRegex(RuntimeError,
                                    "SOURCE_CRAFTED_HEAD_ID"):
            p.checked_change_scope(self.pre)

    def test_no_dps_or_native_exec_from_scope_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            p.stats_source(self.missing[1]["identity"],
                           pathlib.Path(tmp)/"json2.json")
            self.assertEqual(list(pathlib.Path(tmp).iterdir()),[])
        self.assertTrue(p.SCHEMA.endswith("_v1"))

if __name__=="__main__":
    unittest.main()
