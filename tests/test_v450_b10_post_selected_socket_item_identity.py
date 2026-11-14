"""v450 B10: 5+ selected sockets cannot move J to a different gear item.

Pure source-owner regressions; no actual season item permission is invented.
"""
from __future__ import annotations

import copy
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v098_target_user_scenario_bootstrap as boot
from tests.test_v446_b10_selected_gem_after_equipment import (
    B10SelectedGemAfterEquipment as OriginalGems)


class FivePlusSocketItemIdentity(unittest.TestCase):
    @staticmethod
    def need(ok,reason):
        if not ok:
            raise boot.UserScenarioBlocked(reason)

    @staticmethod
    def rows():
        r=OriginalGems.rows()
        r["wrists"]["options"]["gem_id"]="240906"
        return r

    @classmethod
    def original(cls):
        return {slot:row["item_id"] for slot,row in cls.rows().items()
                if row["options"].get("gem_id")}

    def check(self,rows,original=None):
        boot._assert_season_extra_socket_items_unchanged_by_selected_equipment(
            self.original() if original is None else original,
            rows,self.need)

    def test_unmodified_five_socket_owner_is_valid(self):
        rows=self.rows()
        self.check(rows)

    def test_selected_crafted_wrist_with_identical_gems_cannot_reuse_old_j(self):
        rows=self.rows()
        before=OriginalGems.expected()
        before["wrists"]="240906"
        rows["wrists"]["item_id"]=244579
        boot._assert_season_gem_tokens_unchanged_by_selected_equipment(
            before,rows,self.need)
        with self.assertRaisesRegex(
                boot.UserScenarioBlocked,
                "SEASON_V271_USER_EQUIPMENT_SOCKET_ITEM_CHANGED_AFTER_J"):
            self.check(rows)

    def test_selected_special_head_same_gem_but_new_physical_id_blocked(self):
        rows=self.rows()
        rows["head"]["item_id"]=271492
        with self.assertRaises(boot.UserScenarioBlocked):
            self.check(rows)

    def test_reallocated_tier_item_id_in_socketed_slot_blocked(self):
        rows=self.rows()
        rows["finger1"]["item_id"]=268266
        with self.assertRaises(boot.UserScenarioBlocked):
            self.check(rows)

    def test_item_change_in_unsocketed_slot_does_not_affect_existing_j(self):
        rows=self.rows()
        rows["feet"]={"item_id":271800,"options":{}}
        before=copy.deepcopy(rows)
        self.check(rows)
        self.assertEqual(rows,before)

    def test_trinket_swap_not_j_owner(self):
        rows=self.rows()
        rows["trinket1"]["item_id"]=271000
        self.check(rows)

    def test_same_physical_item_id_with_other_provenance_does_not_change_id(self):
        rows=self.rows()
        rows["head"]["item_id"]=self.original()["head"]
        self.check(rows)

    def test_owner_snapshot_corrupt_item_id_or_missing_slot_fails_closed(self):
        for patch in ({"head":"270001"},{"head":0},{"phantom":270001}):
            with self.subTest(patch=patch):
                with self.assertRaises(boot.UserScenarioBlocked):
                    self.check(self.rows(),{**self.original(),**patch})
        r=self.rows()
        del r["head"]
        with self.assertRaises(boot.UserScenarioBlocked):
            self.check(r)

    def test_empty_owner_snapshot_not_verifiable(self):
        with self.assertRaises(boot.UserScenarioBlocked):
            self.check(self.rows(),{})

    def test_source_only_four_ordinary_existing_override_not_changed(self):
        rows=OriginalGems.rows()
        rows["head"]["item_id"]=244579
        boot._assert_season_gem_tokens_unchanged_by_selected_equipment(
            OriginalGems.expected(),rows,self.need)
        # In the runtime the physical-ID owner is intentionally checked only
        # when sum(season_socket_plan.socket_counts)>4.
        # Four-ordinary J is the previously accepted compatibility case.
        self.assertEqual(rows["head"]["item_id"],244579)


if __name__=="__main__":
    unittest.main()
