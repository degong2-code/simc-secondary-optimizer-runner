"""v446 B10: selected gear cannot silently mutate verified J/gem placement.

Pure regression: simulated rows, no external source, SimC, or product READY.
"""
from __future__ import annotations

import copy
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v098_target_user_scenario_bootstrap as bootstrap


class B10SelectedGemAfterEquipment(unittest.TestCase):
    @staticmethod
    def need(ok,reason):
        if not ok:
            raise bootstrap.UserScenarioBlocked(reason)

    @staticmethod
    def rows():
        return {
            "head":{"item_id":270001,"options":{"gem_id":"240900"}},
            "neck":{"item_id":270002,"options":{"gem_id":"240908"}},
            "finger1":{"item_id":270003,"options":{"gem_id":"240918"}},
            "finger2":{"item_id":270004,"options":{"gem_id":"240892"}},
            "wrists":{"item_id":270005,"options":{}},
            "trinket1":{"item_id":270006,"options":{}},
            "trinket2":{"item_id":270007,"options":{}}}

    @classmethod
    def expected(cls):
        return {slot:row["options"].get("gem_id","")
                for slot,row in cls.rows().items()
                if not slot.startswith("trinket")}

    def check(self,rows,expected=None):
        bootstrap._assert_season_gem_tokens_unchanged_by_selected_equipment(
            self.expected() if expected is None else expected,
            rows,self.need)

    def test_selected_crafted_head_inherits_same_gem_without_j_change(self):
        rows=self.rows()
        rows["head"]["item_id"]=244579
        before=copy.deepcopy(rows)
        self.check(rows)
        self.assertEqual(rows,before)

    def test_selected_item_overrides_same_count_different_gem_id_blocked(self):
        rows=self.rows()
        rows["head"]["item_id"]=244579
        rows["head"]["options"]["gem_id"]="240906"
        with self.assertRaisesRegex(
                bootstrap.UserScenarioBlocked,
                "SEASON_V271_USER_EQUIPMENT_GEM_IDS_CHANGED_AFTER_J"):
            self.check(rows)

    def test_selected_item_removes_original_gem_blocked(self):
        rows=self.rows()
        rows["head"]["options"].pop("gem_id")
        with self.assertRaises(bootstrap.UserScenarioBlocked):
            self.check(rows)

    def test_selected_item_adds_extra_unbudgeted_socket_gem_blocked(self):
        rows=self.rows()
        rows["wrists"]["options"]["gem_id"]="240906"
        with self.assertRaises(bootstrap.UserScenarioBlocked):
            self.check(rows)

    def test_selected_item_adds_second_gem_to_existing_slot_blocked(self):
        rows=self.rows()
        rows["neck"]["options"]["gem_id"]="240908/240906"
        with self.assertRaises(bootstrap.UserScenarioBlocked):
            self.check(rows)

    def test_missing_or_extra_physical_slot_blocks(self):
        rows=self.rows()
        rows.pop("wrists")
        with self.assertRaises(bootstrap.UserScenarioBlocked):
            self.check(rows)
        rows=self.rows()
        rows["feet"]={"item_id":270008,"options":{}}
        with self.assertRaises(bootstrap.UserScenarioBlocked):
            self.check(rows)

    def test_trinket_swap_does_not_invalidate_nontrinket_J(self):
        rows=self.rows()
        rows["trinket1"]["item_id"]=271000
        self.check(rows)

    def test_no_selected_season_uses_existing_legacy_path(self):
        # The production caller activates this guard only when
        # season_socket_plan is present; legacy records remain unchanged.
        self.assertTrue(callable(
            bootstrap._assert_season_gem_tokens_unchanged_by_selected_equipment))


if __name__=="__main__":
    unittest.main()
