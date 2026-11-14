"""v451 B10: representative intrinsic vs declared vs final USER physical item.

The per-slot v098 source inspection is observational, never physical socket
permission, J installation, an extra Native call or a new item database.
"""
from __future__ import annotations
import copy,pathlib,sys,unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v098_target_user_scenario_bootstrap as bootstrap


class V451FinalSocketSource(unittest.TestCase):
    BUILD="12.1.5.70783"

    @staticmethod
    def candidate():
        slots={"head":271492,"neck":251142,"finger1":268266,
               "finger2":251136,"wrists":251500,"waist":271510}
        return {"schema":
            "v232_simc_only_one_dps_representative_source_candidate_v1",
            "game_build":V451FinalSocketSource.BUILD,
            "target_ilevel":334,"selected_G_slot_ids":slots,
            "selected_intrinsic_socket_count_by_slot_source_only":{
                "head":0,"neck":1,"finger1":1,"finger2":1,
                "wrists":0,"waist":0}}

    @classmethod
    def rows(cls):
        return {slot:{"item_id":iid,"options":{}}
                for slot,iid in cls.candidate()["selected_G_slot_ids"].items()}

    @staticmethod
    def plan(counts=None):
        return {"socket_counts":counts if counts is not None else {
            "head":1,"neck":1,"finger1":1,"finger2":1,"wrists":1},
            "special_gem_id":None,"special_slot":None,
            "ordinary_gem_ids":[240900,240908,240918,240892,240906]}

    def inspect(self,*,source=None,plan=None,rows=None,build=None):
        return bootstrap._v232_final_socket_item_source_comparison(
            candidate=self.candidate() if source is None else source,
            plan=self.plan() if plan is None else plan,
            rows=self.rows() if rows is None else rows,
            game_build=self.BUILD if build is None else build,
            ilevel=334)

    def test_inherited_v232_intrinsic_is_distinct_from_declared_extra(self):
        result=self.inspect()
        self.assertEqual(result["status"],
            "ORIGINAL_V232_V271_FINAL_USER_ITEMS_COMPARED_SOURCE_ONLY")
        self.assertEqual(result["unverified_extra_by_slot"],
                         {"head":1,"wrists":1})
        self.assertEqual(result["user_changed_item_by_slot"],{})
        self.assertEqual(result["by_slot"]["neck"]["status"],
                         "V232_INTRINSIC_COUNTS_ONLY")
        self.assertEqual(result["by_slot"]["head"]["status"],
                         "DECLARED_ADDITIONAL_SOCKET_UNVERIFIED")
        self.assertFalse(result["game_socket_legality_verified"])
        self.assertFalse(result["J_approved_here"])

    def test_user_replaced_head_retains_declared_gem_but_not_original_source(self):
        rows=self.rows()
        rows["head"]["item_id"]=244579
        out=self.inspect(rows=rows)
        self.assertEqual(out["user_changed_item_by_slot"],{
            "head":{"v232_item_id":271492,"final_user_item_id":244579}})
        self.assertEqual(out["by_slot"]["head"]["status"],
                         "FINAL_USER_ITEM_SOCKET_SOURCE_UNVERIFIED")
        self.assertIsNone(out["by_slot"]["head"][
            "additional_socket_count_without_game_proof"])
        self.assertNotIn("head",out["unverified_extra_by_slot"])
        self.assertFalse(out["bonus_socket_application_verified"])

    def test_user_replaced_intrinsic_neck_is_not_assumed_socketed(self):
        rows=self.rows()
        rows["neck"]["item_id"]=244111
        out=self.inspect(rows=rows)
        self.assertEqual(out["by_slot"]["neck"]["status"],
                         "FINAL_USER_ITEM_SOCKET_SOURCE_UNVERIFIED")
        self.assertIsNone(out["by_slot"]["neck"][
            "additional_socket_count_without_game_proof"])

    def test_four_ordinary_declared_not_a_global_socket_certificate(self):
        plan=self.plan({"head":1,"neck":1,"finger1":1,"finger2":1})
        out=self.inspect(plan=plan)
        self.assertEqual(out["unverified_extra_by_slot"],{"head":1})
        self.assertFalse(out["game_socket_legality_verified"])
        self.assertFalse(out["J_approved_here"])

    def test_five_real_intrinsic_source_has_no_requested_extra(self):
        source=self.candidate()
        source["selected_intrinsic_socket_count_by_slot_source_only"].update({
            "head":1,"wrists":1})
        out=self.inspect(source=source)
        self.assertEqual(out["unverified_extra_by_slot"],{})
        self.assertEqual(out["by_slot"]["wrists"]["status"],
                         "V232_INTRINSIC_COUNTS_ONLY")
        self.assertFalse(out["J_approved_here"])

    def test_missing_exact_v232_candidate_never_infers_counts(self):
        out=self.inspect(source={})
        self.assertEqual(out["status"],
                         "ORIGINAL_V232_SOCKET_ITEM_SOURCE_PENDING")
        self.assertFalse(out["original_same_build_source"])
        self.assertEqual(out["by_slot"],{})

    def test_wrong_game_build_or_ilevel_stays_unadmitted(self):
        source=self.candidate()
        source["game_build"]="12.2.0.99999"
        self.assertFalse(self.inspect(source=source)[
            "original_same_build_source"])
        source=self.candidate()
        source["target_ilevel"]=335
        self.assertFalse(self.inspect(source=source)[
            "original_same_build_source"])
        self.assertFalse(self.inspect(build="12.2.0.99999")[
            "original_same_build_source"])

    def test_declared_phantom_slot_has_no_matching_original_source(self):
        out=self.inspect(plan=self.plan({"neck":1,"finger1":1,
                                          "finger2":1,"phantom":2}))
        self.assertEqual(out["status"],
                         "ORIGINAL_V232_SOCKET_ITEM_SOURCE_PENDING")

    def test_source_item_ids_and_counts_must_be_exact_coverage(self):
        source=self.candidate()
        del source["selected_G_slot_ids"]["waist"]
        self.assertFalse(self.inspect(source=source)[
            "original_same_build_source"])
        source=self.candidate()
        source["selected_intrinsic_socket_count_by_slot_source_only"][
            "head"]=True
        self.assertFalse(self.inspect(source=source)[
            "original_same_build_source"])

    def test_final_item_missing_retains_explicit_unverified_state(self):
        rows=self.rows()
        del rows["wrists"]
        out=self.inspect(rows=rows)
        self.assertIn("wrists",out["user_changed_item_by_slot"])
        self.assertEqual(out["by_slot"]["wrists"]["status"],
                         "FINAL_USER_ITEM_SOCKET_SOURCE_UNVERIFIED")

    def test_comparison_does_not_mutate_received_sources(self):
        source=self.candidate()
        plan=self.plan()
        rows=self.rows()
        before=copy.deepcopy((source,plan,rows))
        self.inspect(source=source,plan=plan,rows=rows)
        self.assertEqual((source,plan,rows),before)

    def test_source_only_none_plan_skips_new_diagnostic(self):
        self.assertIsNone(
            bootstrap._v232_final_socket_item_source_comparison(
                candidate=self.candidate(),plan=None,rows=self.rows(),
                game_build=self.BUILD,ilevel=334))


if __name__=="__main__":
    unittest.main()
