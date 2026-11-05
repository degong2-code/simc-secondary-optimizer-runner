"""P3-BZ opt-in socket placement, source ID reuse and legacy isolation.

Pure Python only: no HTTP, SimC Native, source certification or DPS claims.
"""
from __future__ import annotations

import copy
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))

import v139_pure_target_profile_composer as pure
import v271_user_socket_gem_layout as sockets


class SocketLayoutTests(unittest.TestCase):
    @staticmethod
    def need(ok, why):
        if not ok:
            raise ValueError(why)

    @staticmethod
    def rows():
        return {slot: {"slot": slot, "item_id": 12345,
                       "ilevel": 334, "options": {"gem_id": "240908"}}
                for slot in ("head", "wrists", "waist", "feet", "shoulders")}

    def test_five_sockets_one_wrist_diamond_four_actual_colors(self):
        before = self.rows()
        plan = {"socket_counts": {"head": 1, "wrists": 2,
                                   "waist": 1, "feet": 1},
                "special_gem_id": 240967, "special_slot": "wrists",
                "ordinary_gem_ids": [240908] * 4}
        after, meta = sockets.arrange(before, plan, self.need)
        self.assertEqual(before, self.rows())  # no in-place mutation
        self.assertEqual(after["wrists"]["options"]["gem_id"].split("/")[0],
                         "240967")
        self.assertEqual(meta["ordinary_count"], 4)
        self.assertEqual(meta["socket_total"], 5)
        self.assertTrue(meta["four_colors_physically_present"])
        self.assertEqual(set(meta["ordinary_colors_observed"]),
                         {"garnet", "amethyst", "lapis", "peridot"})
        self.assertIsNone(meta["candidate_J_unadmitted"])
        self.assertFalse(meta["environment_ready"])
        self.assertFalse(meta["game_socket_applicability_verified"])
        self.assertNotIn("gem_id", after["shoulders"]["options"])

    def test_small_socket_count_never_claims_four_color_max(self):
        plan = {"socket_counts": {"waist": 1, "wrists": 1},
                "special_gem_id": 240967, "special_slot": "waist",
                "ordinary_gem_ids": [240908]}
        after, meta = sockets.arrange(self.rows(), plan, self.need)
        self.assertEqual(after["waist"]["options"]["gem_id"], "240967")
        self.assertEqual(meta["ordinary_count"], 1)
        self.assertFalse(meta["four_colors_physically_present"])
        self.assertFalse(meta["max_four_color_effect_claimed"])

    def test_seven_sockets_J_is_only_an_unadmitted_arithmetic_preview(self):
        plan = {"socket_counts": {"head": 1, "wrists": 2,
                                   "waist": 2, "feet": 2},
                "special_gem_id": 240983, "special_slot": "head",
                "ordinary_gem_ids": [240908] * 6}
        _, meta = sockets.arrange(
            self.rows(), plan, self.need, observed_rating_per_ordinary=23)
        self.assertEqual(meta["ordinary_count"], 6)
        self.assertEqual(meta["candidate_J_unadmitted"], 138)
        self.assertFalse(meta["CHMV_J_source_authenticated"])
        self.assertFalse(meta["highest_quality_gem_ids_verified_for_new_season"])

    def test_ordinary_only_future_gems_no_historical_diamond_or_color_gate(self):
        before=self.rows()
        plan={"socket_counts":{"head":2,"wrists":1,"waist":1},
              "special_gem_id":None,"special_slot":None,
              "ordinary_gem_ids":[310001,310002,310001,310002]}
        staged,meta=sockets.arrange(before,plan,self.need,
                                     observed_rating_per_ordinary=27)
        self.assertEqual(before,self.rows())
        self.assertEqual(staged["head"]["options"]["gem_id"],
                         "310001/310002")
        self.assertNotIn("gem_id",staged["feet"]["options"])
        self.assertEqual(meta["socket_total"],4)
        self.assertEqual(meta["ordinary_count"],4)
        self.assertIsNone(meta["special_gem_id"])
        self.assertIsNone(meta["special_slot"])
        self.assertFalse(meta["four_colors_physically_present"])
        self.assertEqual(meta["candidate_J_unadmitted"],108)
        self.assertFalse(meta["environment_ready"])
        reconciled=sockets.reconcile_observed_J(
            meta,{"310001":33,"310002":24},self.need)
        self.assertEqual(reconciled["J_candidate_unadmitted"],114)
        self.assertEqual(reconciled["physical_gem_item_ids"],
                         [310001,310002,310001,310002])
        self.assertFalse(reconciled["game_socket_legality_verified_here"])
        for invalid in (
            {**plan,"special_slot":"head"},
            {**plan,"special_gem_id":240983},
            {**plan,"ordinary_gem_ids":[240967,310002,310001,310002]},
            {**plan,"ordinary_gem_ids":[310001,310002]},
        ):
            with self.subTest(invalid=invalid),self.assertRaises(ValueError):
                sockets.arrange(before,invalid,self.need)

    def test_existing_one_special_only_zero_ordinary_J_remains_supported(self):
        plan={"socket_counts":{"head":1},
              "special_gem_id":240983,"special_slot":"head",
              "ordinary_gem_ids":[]}
        staged,meta=sockets.arrange(self.rows(),plan,self.need)
        self.assertEqual(staged["head"]["options"]["gem_id"],"240983")
        self.assertEqual(meta["ordinary_count"],0)
        candidate=sockets.reconcile_observed_J(meta,{},self.need)
        self.assertEqual(candidate["J_candidate_unadmitted"],0)
        self.assertFalse(candidate["environment_ready"])

    def test_v139_source_only_ordinary_only_profile_and_old_defaults(self):
        character={"class":"druid","spec":"balance",
                   "race":"night_elf","talents":"CAAAABBB11122"}
        trinkets=[{"slot":"trinket1","item_id":270175,"options":{}},
                  {"slot":"trinket2","item_id":270173,"options":{}}]
        plan={"socket_counts":{"head":2,"wrists":1,"waist":1},
              "special_gem_id":None,"special_slot":None,
              "ordinary_gem_ids":[310001,310002,310001,310002]}
        historical,receipt,_,_=pure.compose(character,trinkets)
        preview,cfg,rows,_,_,_,_,_=pure.v098_inputs(
            character,trinkets,socket_plan=plan,
            source_only_season_consumables=True)
        self.assertNotEqual(preview,historical)
        self.assertEqual(receipt["ordinary_gems"],6)
        self.assertIsNone(cfg["consumables"]["special_gem_id"])
        self.assertEqual(rows["head"]["options"]["gem_id"],
                         "310001/310002")
        self.assertIn("head=",preview)
        self.assertIn("gem_id=310001/310002",preview)
        self.assertNotIn("gem_id=240983",preview)
        self.assertNotIn("gem_id=240967",preview)

    def test_invalid_slots_unknown_gem_or_extra_diamond_fail_closed(self):
        base = {"socket_counts": {"head": 1, "wrists": 1},
                "special_gem_id": 240983, "special_slot": "head",
                "ordinary_gem_ids": [240908]}
        for patch in (
            {"socket_counts": {"trinket1": 1, "head": 1}},
            {"socket_counts": {"head": 1, "wrists": -1}},
            {"ordinary_gem_ids": [240983]},
            {"ordinary_gem_ids": [999999]},
            {"ordinary_gem_ids": []},
            {"special_slot": "feet"},
            {"special_gem_id": 0},
        ):
            with self.subTest(patch=patch):
                plan = {**base, **patch}
                before = self.rows()
                with self.assertRaises(ValueError):
                    sockets.arrange(before, plan, self.need)
                self.assertEqual(before, self.rows())

    def test_opt_in_pure_profile_serializes_actual_diamond_and_colors(self):
        character = {"class": "druid", "spec": "balance",
                     "race": "night_elf", "talents": "CAAAABBB11122"}
        trinkets = [{"slot": "trinket1", "item_id": 270175, "options": {}},
                    {"slot": "trinket2", "item_id": 270173, "options": {}}]
        plan = {"socket_counts": {"head": 1, "wrists": 2,
                                   "waist": 1, "feet": 1},
                "special_gem_id": 240967, "special_slot": "wrists",
                "ordinary_gem_ids": [240908] * 4}
        old_profile, old_meta, _, _ = pure.compose(character, trinkets)
        profile, receipt, rows, _ = pure.compose(
            character, trinkets, socket_plan=plan)
        self.assertNotEqual(profile, old_profile)
        self.assertEqual(old_meta["ordinary_gems"], 6)
        self.assertEqual(receipt["ordinary_gems"], 4)
        self.assertTrue(receipt["socket_layout"]["four_colors_physically_present"])
        self.assertFalse(receipt["chmv_budget_ready"])
        self.assertFalse(receipt["user_optimizer_ready"])
        self.assertEqual(receipt["native_calls"], 0)
        self.assertIn("gem_id=240967/", next(
            line for line in profile.splitlines() if line.startswith("wrists=")))
        self.assertEqual(sum("gem_id=240967" in line
                             for line in profile.splitlines()), 1)
        self.assertEqual(rows["wrists"]["options"]["gem_id"].split("/")[0],
                         "240967")


if __name__ == "__main__":
    unittest.main()
