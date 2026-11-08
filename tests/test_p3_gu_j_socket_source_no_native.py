"""P3-GU: native-free current-season J/socket source capture mode."""
import pathlib
import sys
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from integration_probes import p3_fr_zero_base_t1_acceptance as p
from runner import v216_environment_build_coordinator as engine

class SourceOnlyJSession(unittest.TestCase):
    def test_source_mode_keeps_native_off_and_selected_ids_source_only(self):
        self.assertEqual(p.source_only_J_socket_controls(),{
            "auto_four_stat_source_requested":True,
            "auto_native_G_requested":False,
            "auto_native_F_requested":False,
            "auto_native_O_requested":False,
            "auto_select_observed_F_no_oil":False})
        ids=p.selected_t1_source_inputs(
            exact_flask_item_id=241324,existing_special_gem_id=240967)
        self.assertEqual(ids["selected_budget_items"],
                         {"flask_item_id":241324,"oil_item_ids_by_hand":{}})
        self.assertEqual(ids["source_selected_gem_roles"],
                         {"special_gem_id":240967,"ordinary_gem_ids":None})
        self.assertNotIn("F_rating",ids)

    def test_p3_hb_existing_v268_source_diagnostic_is_factual_and_native_free(self):
        projected=engine._existing_v268_four_stat_source_diagnostic(
            observed={
                "status":"ENCHANT_RAW_POINTS_SOURCE_ONLY_J_NOT_APPROVED",
                "selected_gem_v221_same_build_items_all_present":True,
                "selected_gem_v221_missing_item_ids":[],
                "four_stat_ordinary_source_complete_unadmitted":False,
                "four_stat_ordinary_best_observed_unadmitted":{
                    "crit_rating":{"item_id":101,"raw_nominal_points":30},
                    "haste_rating":{"item_id":102,"raw_nominal_points":28}},
                "linked_gem_items":11,
                "raw_static_candidate_count":4,
                "unresolved_enchant_count":7},
            csv_source={"status":"GEM_ENCHANT_CSV_SOURCE_SEALED"})
        self.assertEqual(projected["selected_special_in_same_build_v221"],True)
        self.assertFalse(projected["four_ordinary_two_stat_types_complete"])
        self.assertEqual(projected["observed_leading_types"],
                         ["crit_rating","haste_rating"])
        self.assertEqual(projected["missing_leading_types"],
                         ["mastery_rating","versatility_rating"])
        self.assertEqual(projected["v266_unresolved_enchant_count"],7)
        self.assertEqual(projected["official_J"],None)
        self.assertFalse(projected["environment_ready"])
        self.assertEqual(projected["native_calls"],0)
        pending=engine._existing_v268_four_stat_source_diagnostic(
            observed={"status":"GEM_ENCHANT_LOCAL_JOIN_PENDING",
                      "reason":"V268_V221_EXACT_JOIN_MISSING"},
            csv_source={"status":"GEM_ENCHANT_CSV_SOURCE_SEALED"})
        self.assertIsNone(pending["selected_special_in_same_build_v221"])
        self.assertIsNone(pending["four_ordinary_two_stat_types_complete"])
        self.assertEqual(pending["v268_reason"],
                         "V268_V221_EXACT_JOIN_MISSING")
        self.assertIsNone(pending["v221_linked_gem_item_count"])

    def test_workflow_new_source_guard_preserves_prior_gp_and_gq(self):
        src=(pathlib.Path(__file__).resolve().parents[1]/
            ".github/workflows/p3_fz_reuse_exact_simc_live_t1.yml"
            ).read_text(encoding="utf8")
        for t in ("[p3-gp-f-only-once]","[p3-gq-gjf-once]",
                  "[p3-gu-j-socket-source-once]",
                  "p3_gu_j_socket_source_once_20261107.json",
                  "P3_T1_J_SOCKET_SOURCE_ONLY",
                  "G_native_max","F_native_max","O_native_max"):
            self.assertIn(t,src)
        self.assertIn("fetch-depth: 2",src)

    def test_no_original_proof_cannot_be_claimed_installed(self):
        d=p.summarized_existing_GJF_owner_components({})
        self.assertEqual(d["verified_components_not_full_environment"],{})
        self.assertFalse(d["official_GJFO_B_T_ready_inferred"])
if __name__=="__main__":
    unittest.main()
