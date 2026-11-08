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

    def test_p3_fm_four_stat_default_uses_each_nominal_type_once(self):
        source={
            stat:{"item_id":311100+i,"raw_nominal_points":40+i}
            for i,stat in enumerate(sockets.ORDINARY_FOUR_STATS)}
        before=copy.deepcopy(source)
        ids=sockets.ordinary_four_stat_default(
            observed_by_stat=source,socket_total=7,special_gem_id=311200,
            need=self.need)
        self.assertEqual(ids,[311100,311101,311102,311103,311100,311101])
        self.assertEqual(source,before)
        self.assertEqual(len(set(ids[:4])),4)
        self.assertNotIn(311200,ids)
        for wrong in (
            {"socket_total":4},
            {"observed_by_stat":{k:v for k,v in source.items()
                                 if k!="crit_rating"}},
            {"observed_by_stat":{**source,
                "mastery_rating":source["crit_rating"]}},
            {"observed_by_stat":{**source,
                "crit_rating":{"item_id":311200,"raw_nominal_points":40}}},
            {"observed_by_stat":{**source,
                "crit_rating":{"item_id":240967,"raw_nominal_points":40}}},
        ):
            args={"observed_by_stat":source,"socket_total":7,
                  "special_gem_id":311200,"need":self.need}
            with self.subTest(wrong=wrong),self.assertRaises(ValueError):
                sockets.ordinary_four_stat_default(**{**args,**wrong})

    def test_engine_uses_nominal_totals_without_v266_or_native(self):
        # Season-build identity is an input contract, not proof of quality.
        source={"game_build":"12.1.5.70783","source_sha256":"a"*64,
                "by_stat":{
                    stat:{"item_id":311100+i,"rating":23}
                    for i,stat in enumerate(sockets.ORDINARY_FOUR_STATS)}}
        before=copy.deepcopy(source)
        for sockets_n,total in ((5,92),(7,138)):
            selection=sockets.nominal_four_stat_from_season_source(
                source=source,game_build="12.1.5.70783",
                socket_total=sockets_n,special_gem_id=311200,
                need=self.need)
            self.assertEqual(selection["J_candidate_unadmitted"],total)
            self.assertEqual(selection["ordinary_gem_ids"],
                             [311100+i%4 for i in range(sockets_n-1)])
            self.assertEqual(selection["rating_by_id"],
                             {str(311100+i):23 for i in range(4)})
            self.assertFalse(selection["environment_ready"])
            self.assertEqual(selection["native_calls"],0)
        self.assertEqual(source,before)
        invalid=[
            {**source,"game_build":"12.1.5.70575"},
            {**source,"by_stat":{**source["by_stat"],
                "crit_rating":{"item_id":311100,"rating":0}}},
            {**source,"by_stat":{**source["by_stat"],
                "crit_rating":{"item_id":311101,"rating":23}}},
            {**source,"by_stat":{k:v for k,v in
                source["by_stat"].items() if k!="crit_rating"}},
        ]
        for candidate in invalid:
            with self.subTest(candidate=candidate),self.assertRaises(ValueError):
                sockets.nominal_four_stat_from_season_source(
                    source=candidate,game_build="12.1.5.70783",
                    socket_total=5,special_gem_id=311200,need=self.need)

    def test_packaged_current_build_nominal_item_totals_and_missing_next_season(self):
        # Current fixture records 4 top-rank physical item tooltips,
        # not a new Native measurement or product admission.
        source=sockets.load_packaged_season_nominal_source(
            game_build="12.1.5.70783",need=self.need)
        self.assertEqual(list(source["by_stat"]),list(sockets.ORDINARY_FOUR_STATS))
        self.assertEqual({x["rating"] for x in source["by_stat"].values()},{23})
        self.assertEqual({x["item_id"] for x in source["by_stat"].values()},
                         {240908,240892,240900,240918})
        self.assertRegex(source["source_sha256"],r"^[0-9a-f]{64}$")
        self.assertIsNone(sockets.load_packaged_season_nominal_source(
            game_build="12.2.0.99999",need=self.need))
        selection=sockets.nominal_four_stat_from_season_source(
            source=source,game_build="12.1.5.70783",socket_total=7,
            special_gem_id=240967,need=self.need)
        self.assertEqual(selection["J_candidate_unadmitted"],138)
        self.assertFalse(selection["environment_ready"])
        self.assertFalse(selection["simc_gem_delta_required"])

    def test_nominal_catalog_bad_build_and_bad_components_block_without_native(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            src=(ROOT/"data"/"season_ordinary_gem_nominal"/
                 "12.1.5.70783.json")
            good=json.loads(src.read_text(encoding="utf8"))
            for patch in (
                    {"game_build":"12.1.5.70575"},
                    {"by_stat":{**good["by_stat"],
                         "crit_rating":{**good["by_stat"]["crit_rating"],
                           "secondary_components":{"crit_rating":23}}}},
                    {"by_stat":{**good["by_stat"],
                         "crit_rating":{**good["by_stat"]["crit_rating"],
                           "secondary_components":{"crit_rating":0,
                                                   "haste_rating":23}}}},
                    {"by_stat":{**good["by_stat"],
                         "crit_rating":{**good["by_stat"]["crit_rating"],
                                      "item_id":240892}}}):
                payload={**good,**patch}
                (root/"12.1.5.70783.json").write_text(
                    json.dumps(payload),encoding="utf8")
                with self.assertRaises(ValueError):
                    sockets.load_packaged_season_nominal_source(
                        game_build="12.1.5.70783",
                        need=self.need,source_folder=root)
    def test_p3_hk_nominal_J_owner_reuses_package_v221_without_raw_effect_gate(self):
        """v216 must bind real packaged J to its ORIGINAL numeric owner."""
        from runner import v216_environment_build_coordinator as engine
        source=sockets.load_packaged_season_nominal_source(
            game_build="12.1.5.70783",need=self.need)
        picked=sockets.nominal_four_stat_from_season_source(
            source=source,game_build="12.1.5.70783",
            socket_total=5,special_gem_id=240967,need=self.need)
        rows=self.rows()
        plan={"socket_counts":{"head":1,"wrists":2,"waist":1,"feet":1},
              "special_gem_id":240967,"special_slot":"head",
              "ordinary_gem_ids":picked["ordinary_gem_ids"],
              sockets.SOURCE_IDS_FIELD:sorted(
                  {240967,*picked["ordinary_gem_ids"]})}
        _,layout=sockets.arrange(rows,plan,self.need)
        link={"same_build_gem_item_join_only":True,
              "special_gem_item_id":240967,
              "selected_item_ids":sorted({240967,*picked["ordinary_gem_ids"]}),
              "v221_stage_receipt_sha256":"b"*64}
        pre={"game_build":"12.1.5.70783",
             "source_catalog_manifest_sha256":"a"*64}
        j={"rating_origin":"SEASON_NOMINAL_PER_ITEM_TOTAL_SOURCE",
           "nominal_source_sha256":source["source_sha256"],
           "nominal_source_game_build":"12.1.5.70783",
           "source_v221_stage_receipt_sha256":"b"*64,
           "J_candidate_unadmitted":92,
           "physical_gem_item_ids":layout["ordinary_gem_ids"],
           "status":"PHYSICAL_GEM_J_ARITHMETIC_UNADMITTED",
           "J_accounting_policy":"SUM_SELECTED_ORDINARY_GEM_RATINGS",
           "special_gem_count_in_J":0}
        verified=engine._fresh_source_owner_packaged_nominal_J(
            preflight=pre,layout=layout,link=link,j=j)
        self.assertEqual(verified["rating"],92)
        self.assertEqual(verified["per_item_nominal_rating"],
                         picked["rating_by_id"])
        self.assertEqual(set(verified["observed_quality_rank_by_id"].values()),
                         {2})
        self.assertFalse(verified["highest_available_quality_verified"])
        self.assertFalse(verified["real_socket_source_verified"])
        self.assertTrue(verified["nominal_J_not_simc_effective_delta"])
        for tamper in ({"nominal_source_sha256":"f"*64},
                       {"J_candidate_unadmitted":91},
                       {"source_v221_stage_receipt_sha256":"f"*64}):
            with self.subTest(tamper=tamper),self.assertRaises(
                    engine.EnvironmentBuildBlocked):
                engine._fresh_source_owner_packaged_nominal_J(
                    preflight=pre,layout=layout,link=link,j={**j,**tamper})
        self.assertIsNone(engine._fresh_source_owner_packaged_nominal_J(
            preflight={**pre,"game_build":"12.2.0.99999"},
            layout=layout,link=link,j=j))
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

    def test_special_gem_exactly_one_required_even_in_future_source_preview(self):
        # Policy correction P3-EC: ordinary gems do not replace the one
        # required special gem. The future-season item ID is established
        # separately; it must not be silently omitted at profile staging.
        plan = {"socket_counts": {"head": 1, "wrists": 1},
                "special_gem_id": None, "special_slot": None,
                "ordinary_gem_ids": [240908, 240908]}
        before = self.rows()
        with self.assertRaisesRegex(
                ValueError, "SOCKET_SINGLE_SPECIAL_GEM_POSITION_REQUIRED"):
            sockets.arrange(before, plan, self.need)
        self.assertEqual(before, self.rows())

        character = {"class": "druid", "spec": "balance",
                     "race": "night_elf", "talents": "CAAAABBB11122"}
        trinkets = [
            {"slot": "trinket1", "item_id": 270175, "options": {}},
            {"slot": "trinket2", "item_id": 270173, "options": {}}]
        with self.assertRaisesRegex(
                ValueError, "SOCKET_SINGLE_SPECIAL_GEM_POSITION_REQUIRED"):
            pure.v098_inputs(character, trinkets,
                             socket_plan=plan,
                             source_only_season_consumables=True)

        # A second special gem cannot be hidden among ordinary gems.
        plan["special_gem_id"] = 240983
        plan["special_slot"] = "head"
        plan["ordinary_gem_ids"] = [240967]
        with self.assertRaisesRegex(
                ValueError, "SOCKET_ORDINARY_GEMS_SOURCE_OBSERVED_AND_COUNTED"):
            sockets.arrange(before, plan, self.need)

    def test_same_build_source_gem_ids_support_one_new_special_only(self):
        """Source-only v221 ID allowance, not proof of special effect or socket."""
        plan={"socket_counts":{"head":1,"wrists":2,"waist":1},
              "special_gem_id":311003,"special_slot":"wrists",
              "ordinary_gem_ids":[311001,311001,311002],
              "source_observed_gem_item_ids":[311001,311002,311003]}
        old=self.rows()
        staged,receipt=sockets.arrange(old,plan,self.need)
        self.assertEqual(old,self.rows())
        self.assertEqual(staged["wrists"]["options"]["gem_id"],
                         "311003/311002")
        # A source-observed special may occupy an ordinary open wrist
        # socket. No source color/type comparison with the slot is needed.
        self.assertEqual(receipt["special_slot"],"wrists")
        self.assertEqual(receipt["socket_total"],4)
        self.assertEqual(staged["head"]["options"]["gem_id"],"311001")
        self.assertEqual(receipt["ordinary_gem_ids"],
                         [311001,311001,311002])
        self.assertEqual(receipt["special_gem_id"],311003)
        self.assertEqual(receipt["ordinary_count"],3)
        self.assertFalse(receipt["highest_quality_gem_ids_verified_for_new_season"])
        self.assertFalse(receipt["game_socket_applicability_verified"])
        j=sockets.reconcile_observed_J(
            receipt,{"311001":20,"311002":30},self.need)
        self.assertEqual(j["J_candidate_unadmitted"],70)
        self.assertFalse(j["environment_ready"])
        character={"class":"druid","spec":"balance",
                   "race":"night_elf","talents":"CAAAABBB11122"}
        trinkets=[{"slot":"trinket1","item_id":270175,"options":{}},
                  {"slot":"trinket2","item_id":270173,"options":{}}]
        profile,cfg,rows,_,_,_,_,_=pure.v098_inputs(
            character,trinkets,socket_plan=plan,
            source_only_season_consumables=True)
        self.assertEqual(cfg["consumables"]["special_gem_id"],311003)
        self.assertIn("gem_id=311003/311002",profile)
        self.assertNotIn("gem_id=240983",profile)
        self.assertEqual(rows["wrists"]["options"]["gem_id"],
                         "311003/311002")
        for patch in (
            {"source_observed_gem_item_ids":[311001,311002]},
            {"source_observed_gem_item_ids":[311001,311002,311003,311004]},
            {"ordinary_gem_ids":[311003,311002,311001]},
            {"special_gem_id":None},
            {"special_gem_id":999999},
            {"source_observed_gem_item_ids":[311001,311001,311003]},
        ):
            with self.subTest(patch=patch),self.assertRaises(ValueError):
                sockets.arrange(old,{**plan,**patch},self.need)


    def test_p3_fj_intrinsic_source_plan_stages_one_special_and_n_ordinary(self):
        counts={"head":1,"waist":0,"wrists":2,"feet":1}
        original=copy.deepcopy(counts)
        plan=sockets.intrinsic_source_plan(
            intrinsic_socket_counts=counts,special_gem_id=311003,
            ordinary_gem_ids=[311001,311001,311002],
            source_observed_gem_item_ids=[311001,311002,311003],
            need=self.need)
        self.assertEqual(counts,original)
        self.assertEqual(plan["socket_counts"],
                         {"feet":1,"head":1,"wrists":2})
        self.assertEqual(plan["special_slot"],"head")
        rows,receipt=sockets.arrange(self.rows(),plan,self.need)
        self.assertEqual(rows["head"]["options"]["gem_id"],"311003")
        self.assertEqual(rows["wrists"]["options"]["gem_id"],"311001/311002")
        self.assertEqual(receipt["ordinary_count"],3)
        self.assertEqual(receipt["special_gem_id"],311003)
        self.assertFalse(receipt["environment_ready"])
        self.assertFalse(receipt["CHMV_J_source_authenticated"])
        self.assertFalse(receipt["game_socket_applicability_verified"])

        wrist=sockets.intrinsic_source_plan(
            intrinsic_socket_counts={"wrists":2,"feet":1},
            special_gem_id=311003,
            ordinary_gem_ids=[311001,311002],
            source_observed_gem_item_ids=[311001,311002,311003],
            need=self.need)
        self.assertEqual(wrist["special_slot"],"feet")
        for changed in (
            {"intrinsic_socket_counts":{"head":1}},
            {"ordinary_gem_ids":[311001,311001]},
            {"special_gem_id":None},
            {"ordinary_gem_ids":[311003,311001,311002]},
            {"source_observed_gem_item_ids":[311001,311003]},
            {"intrinsic_socket_counts":{"head":1,"wrists":-1}},
        ):
            args={"intrinsic_socket_counts":counts,
                  "special_gem_id":311003,
                  "ordinary_gem_ids":[311001,311001,311002],
                  "source_observed_gem_item_ids":[311001,311002,311003],
                  "need":self.need}
            with self.subTest(changed=changed),self.assertRaises(ValueError):
                sockets.intrinsic_source_plan(**{**args,**changed})

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
