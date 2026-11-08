"""P3-GQ existing one-shot G/J/F source path; no Native in these tests."""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from integration_probes import p3_fr_zero_base_t1_acceptance as p

class CombinedOriginalSources(unittest.TestCase):
    def test_existing_T1_GJF_mode_uses_one_G_one_F_pair_without_oil(self):
        setup=p.t1_native_source_controls(
            selected_F=241324,f_only=False,binary_available=True)
        self.assertEqual(setup,{
            "auto_four_stat_source_requested":True,
            "auto_native_G_requested":True,
            "auto_native_F_requested":True,
            "auto_native_O_requested":False,
            "auto_select_observed_F_no_oil":False})
        selection=p.selected_t1_source_inputs(
            exact_flask_item_id=241324,existing_special_gem_id=240967)
        self.assertEqual(selection["selected_budget_items"],
                         {"flask_item_id":241324,"oil_item_ids_by_hand":{}})
        self.assertEqual(selection["source_selected_gem_roles"],
                         {"special_gem_id":240967,"ordinary_gem_ids":None})
        self.assertNotIn("F_rating",selection)
    def test_real_t1_uses_exact_build_nominal_J_like_normal_web(self):
        selection=p.selected_t1_source_inputs(
            exact_flask_item_id=241324,existing_special_gem_id=240967,
            game_build="12.1.5.70783")
        self.assertEqual(selection["source_target_socket_count"],5)
        source=selection["source_ordinary_nominal_by_stat"]
        self.assertEqual(source["game_build"],"12.1.5.70783")
        self.assertEqual({row["item_id"] for row in source["by_stat"].values()},
                         {240908,240892,240900,240918})
        self.assertEqual({row["rating"] for row in source["by_stat"].values()},
                         {23})
        self.assertNotIn("J",selection)
        self.assertNotIn("environment_ready",selection)

    def test_real_t1_does_not_relabel_nominal_J_across_builds(self):
        selection=p.selected_t1_source_inputs(
            exact_flask_item_id=241324,existing_special_gem_id=240967,
            game_build="12.2.0.99999")
        self.assertNotIn("source_ordinary_nominal_by_stat",selection)
        self.assertNotIn("source_target_socket_count",selection)
        self.assertEqual(selection["source_selected_gem_roles"],
                         {"special_gem_id":240967,"ordinary_gem_ids":None})
        self.assertEqual(p.selected_t1_source_inputs(
            exact_flask_item_id=241324,existing_special_gem_id=None,
            game_build="12.1.5.70783"),{"selected_budget_items":{
                "flask_item_id":241324,"oil_item_ids_by_hand":{}}})

    def test_verified_summary_is_not_a_new_readiness_gate(self):
        original={
            "G":{"rating":4040,"source_verification":"EXACT_NATIVE",
                 "source_sha256":"a"*64},
            "J":{"rating":230,"source_verification":"VALID_SAME_SEASON_SOURCE",
                 "source_sha256":"b"*64},
            "F":{"rating":165,"selected_flask_item_id":241324,
                 "source_verification":"EXACT_NATIVE","source_sha256":"c"*64,
                 "native_pair_receipt_sha256":["d"*64,"e"*64]}}
        source={
            "native_G_source_owner_component_not_full_environment":
                original["G"],
            "original_J_F_verified_components_not_full_environment":{
                "J":original["J"],"F":original["F"]},
            "selected_J_intrinsic_socket_origin_unadmitted":{
                "status":"J_INTRINSIC_COUNTS_BOUND_SOURCE_ONLY"}}
        out=p.summarized_existing_GJF_owner_components(source)
        self.assertEqual(set(out["verified_components_not_full_environment"]),
                         {"G","J","F"})
        self.assertEqual(out["verified_components_not_full_environment"]["F"][
            "rating"],165)
        self.assertFalse(out["official_GJFO_B_T_ready_inferred"])
        self.assertEqual(out["native_calls"],0)
        self.assertEqual(p.summarized_existing_GJF_owner_components({})[
            "verified_components_not_full_environment"],{})
    def test_one_spec_zero_history_shaman_enhancement_uses_same_engine(self):
        default=p.requested_t1_character({},dps_once=False)
        self.assertEqual(default,{"class":"paladin","spec":"retribution",
                                  "race":"dwarf"})
        other={"P3_T1_SPEC_CLASS":"shaman",
               "P3_T1_SPEC_NAME":"enhancement",
               "P3_T1_SPEC_RACE":"dwarf"}
        self.assertEqual(p.requested_t1_character(other,dps_once=True),
                         {"class":"shaman","spec":"enhancement","race":"dwarf"})
        with self.assertRaisesRegex(ValueError,"REQUIRES_DPS_ONE_SHOT"):
            p.requested_t1_character(other,dps_once=False)
        with self.assertRaisesRegex(ValueError,"UNSUPPORTED"):
            p.requested_t1_character({**other,"P3_T1_SPEC_NAME":"restoration"},
                                     dps_once=True)

    def test_guard_separates_prior_GP_and_new_GQ(self):
        root=pathlib.Path(__file__).resolve().parents[1]
        s=(root/".github/workflows/p3_fz_reuse_exact_simc_live_t1.yml"
           ).read_text("utf8")
        self.assertIn("p3_gp_f_only_once_20261106.json",s)
        self.assertIn("p3_gq_gjf_one_shot_20261107.json",s)
        self.assertIn("[p3-gq-gjf-once]",s)
        self.assertIn("[p3-hs-other-spec-dps-once]",s)
        self.assertIn("p3_hs_other_spec_user_dps_20261108.json",s)
        self.assertIn("G_native_max",s)
        self.assertIn("special_gem_effect_independently_checked",s)
        self.assertIn("fetch-depth: 2",s)
        self.assertNotIn("F_rating: 165",s)
if __name__=="__main__":
    unittest.main()
