"""P3-CU: existing v216 zero-history Build -> ORIGINAL v222 user B/T.

Source-only synthetic proof in tests. It never authorizes a real season,
publishes a v098 user profile, runs Native or recollects Wago.
"""
from __future__ import annotations
import copy
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner")]
import v216_environment_build_coordinator as build
from tests.test_v264_environment_standard_budget_integration import prepared

class ZeroHistoryPreprofileUserBudget(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root=pathlib.Path(t.name)
        self.catalog,self.table,self.ui=prepared()
        self.path=self.root/"source_catalog.json"
        self.path.write_text("{}",encoding="utf8")
        self.wago=self.root/"wago"
        self.wago.mkdir()
        (self.wago/"receipt.json").write_text("{}",encoding="utf8")
        self.collected={
            "schema":"v216_fresh_source_stage_v1",
            "source_stage":{"status":"EXECUTED_AND_SEALED","reused":False},
            "environment_installed":False,"environment_ready":False,
            "native_calls":0,"G":None,"J":None,"F":None,"O":None,"B":None,"T":None,
            "expected_game_build":self.catalog["game_build"],
            "snapshot_receipt_path":str(self.wago/"receipt.json")}
        self.compiled={
            "status":"FRESH_V191_V211_V213_COMPILED_UNADMITTED",
            "stage_root":str(self.root),
            "simc_revision":self.catalog["simc_revision"],
            "source_catalog_path":str(self.path),"missing":[]}
    def run_build(self,manual=None,proof=True,level=334,user_level=None,
                  native_result=None,gem_layout=None,gem_ratings=None,
                  effect_requests=None,effect_resolver=None,
                  effect_observation=None,selected_budget_items=None,
                  raw_gem_source=None,trusted_provider=None,
                  auto_four_stat_source=False):
        inputs={
            "expected_game_build":self.catalog["game_build"],
            "representative_request":{
                "class":"mage","spec":"frost","target_ilevel":level},
            "g_probe_character":None,
            "simc_revision_hint":None}
        if proof:
            inputs["same_build_budget_evidence"]=self.table[334]
        if auto_four_stat_source:
            inputs["auto_four_stat_source_requested"]=True
        if gem_layout is not None:
            inputs["gem_layout_receipt"]=gem_layout
        if gem_ratings is not None:
            inputs["gem_rating_by_id"]=gem_ratings
        if effect_requests is not None:
            inputs["effect_probe_requests"]=effect_requests
        if selected_budget_items is not None:
            inputs["selected_budget_items"]=selected_budget_items
        if trusted_provider is not None:
            inputs["verified_install_input_provider"]=trusted_provider
        user={"target":{"ilevel":user_level if user_level is not None else level,
                        "final_T":manual}}
        with mock.patch.object(build,"collect_wago_new_season_source",
                               return_value=self.collected) as collect,\
             mock.patch.object(build.zero_history_G_native,"collect",
                               return_value=(native_result if native_result is not None
                                             else {"status":"PENDING",
                                                   "new_native_calls":0})) as native,\
             mock.patch.object(build.source_wiring,"compile_collected",
                               return_value=dict(self.compiled)) as compiler,\
             mock.patch.object(build.environment_manifest,"read_json",
                               return_value=(self.catalog,"a"*64)),\
             mock.patch.object(build.source_to_catalog,"verify_catalog"),\
             mock.patch.object(build.user_catalog,"public_options",
                               return_value=self.ui),\
             mock.patch.object(build,"_fresh_gem_item_source_stage",
                               return_value={
                                   "candidate_path":(
                                       "sealed_v221.json"
                                       if raw_gem_source is not None else None),
                                   "source_stage":{"receipt_sha256":"5"*64}}),\
             mock.patch.object(build.gem_enchant_stage,"view",
                               return_value=raw_gem_source),\
             mock.patch.object(build.consumable_simc_relation,
                               "resolve_native_input",
                               return_value=effect_resolver),\
             mock.patch.object(build.native_effect_pair,"measure",
                               return_value=effect_observation):
            result=build.build_environment(
                sessions_root=self.root/"sessions",session_folder=None,
                user=user,binary=None,revision=None,static_cache=None,
                source_catalog_path=None,bootstrap_result=None,
                fresh_collection_inputs=inputs)
        self.assertEqual(collect.call_count,1)
        if auto_four_stat_source:
            self.assertIs(collect.call_args.kwargs.get("auto_four_stat_gems"),
                          True)
            self.assertNotIn("auto_four_stat_source_requested",
                             collect.call_args.kwargs)
        self.assertEqual(native.call_count,1)
        self.assertEqual(compiler.call_count,1)
        for name in ("same_build_budget_evidence","gem_layout_receipt",
                     "gem_rating_by_id","effect_probe_requests",
                     "selected_budget_items","verified_install_input_provider"):
            self.assertNotIn(name,collect.call_args.kwargs)
        self.assertFalse((self.root/"sessions").exists())
        return result
    def v277_native_G(self, *, level=334, source_sha=None):
        # Synthetic source-only Native return: v277 itself is mocked here.
        # Existing P3-CO/CP/BX real evidence is NOT re-executed.
        g=self.table[334]["components"]["G"]
        sha=source_sha or g["source_sha256"]
        import v222_season_budget_contract as budget
        rounded=budget.standardize_representative_G(
            observed_G_total=2847,target_ilevel=level,
            source_observation_sha256=sha)
        return {
            "status":"G_NATIVE_NUMERIC_REFERENCE_OBSERVED_JFO_PENDING",
            "observed_G_total":2847,
            "standardized_G":rounded["standardized_G"],
            "standardization":rounded,
            "native_json2_sha256":sha,
            "native_receipt_sha256":"1"*64,
            "source_profile_receipt_sha256":"2"*64,
            "native_binary_sha256":"3"*64,
            "new_native_calls":0,"full_G_approved":False,
            "environment_ready":False,
        }

    def test_p3_fs_independent_simc_source_commit_reuses_immutable_stage(self):
        # One known source-prefix is eligible for the existing v229 pin
        # before any authenticated raid/gear/tier selection has succeeded.
        # This is not binary or current-season attestation.
        expected="a"*40
        with mock.patch.object(
                build.simc_source,"resolve_exact_commit",
                return_value=expected) as resolver:
            first=build._resolve_one_spec_simc_commit_stage(
                stage_root=self.root,build=self.catalog["game_build"],
                gear={},tier={},revision_hint="a"*8)
            second=build._resolve_one_spec_simc_commit_stage(
                stage_root=self.root,build=self.catalog["game_build"],
                gear={},tier={},revision_hint="a"*8)
            self.assertEqual(resolver.call_count,1)
        self.assertEqual(first["status"],
            "SIMC_SOURCE_COMMIT_EXACT_PIN_CANDIDATE")
        self.assertEqual(second["simc_revision"],expected)
        self.assertFalse(first["binary_attested"])
        self.assertFalse(first["season_verified"])
        self.assertFalse(first["environment_ready"])
        # The mocked resolver performs zero HTTP; actual v257 records each
        # resolution request via its existing transport when not mocked.
        self.assertEqual(first["network_calls_by_stage"],0)
        missing=build._resolve_one_spec_simc_commit_stage(
            stage_root=self.root,build=self.catalog["game_build"],
            gear={},tier={},revision_hint=None)
        self.assertIsNone(missing["simc_revision"])
        self.assertFalse(missing["environment_ready"])

    def test_p3_fs_zero_base_requests_same_build_gem_DBC_without_role_ID(self):
        # Source collection is distinct from four-stat ItemID selection and
        # does not assert J or install a representative SimC profile.
        result=self.run_build(proof=False,auto_four_stat_source=True)
        self.assertFalse(result["zero_history_build"]["environment_ready"])
        self.assertFalse(result["environment_installed"])
        self.assertIsNone(result["J"])

    def test_native_G_without_JFO_proof_is_visible_but_never_ready(self):
        result=self.run_build(proof=False,native_result=self.v277_native_G())
        source=result["source_compilation"]
        numeric=source["v277_native_G_preprofile_unadmitted"]
        self.assertEqual(numeric["standardized_G"],2850)
        self.assertEqual(numeric["target_ilevel"],334)
        self.assertFalse(numeric["source_admission_performed_here"])
        self.assertNotIn("preprofile_budget_arithmetic_unadmitted",source)
        self.assertFalse(result["zero_history_build"]["environment_ready"])
        self.assertFalse(result["zero_history_build"]["user_session_created"])
        self.assertEqual(result["native_calls"],0)

    def test_existing_v277_G_fills_only_missing_component_for_v222(self):
        native_result=self.v277_native_G()
        component=self.table[334]["components"].pop("G")
        try:
            result=self.run_build(
                manual=3300,native_result=native_result)
        finally:
            self.table[334]["components"]["G"]=component
        calc=result["source_compilation"][
            "preprofile_budget_arithmetic_unadmitted"]
        self.assertEqual((calc["reference_G"],calc["base_B"],calc["final_T"]),
                         (2850,3268,3300))
        self.assertTrue(calc["manual_final_T_authoritative"])
        self.assertFalse(calc["source_authentication_performed_here"])
        self.assertFalse(result["zero_history_build"]["environment_ready"])
        self.assertEqual(result["native_calls"],0)

    def test_v277_native_and_supplied_G_conflict_fails_closed(self):
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_ZERO_HISTORY_SOURCE_COMPILER_INVALID:"
                "V216_ZERO_HISTORY_V277_G_V222_CONFLICT"):
            self.run_build(native_result=self.v277_native_G(
                source_sha="7"*64))
        self.assertFalse((self.root/"sessions").exists())

    def test_v277_native_target_drift_fails_before_budget(self):
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_ZERO_HISTORY_SOURCE_COMPILER_INVALID:"
                "V216_ZERO_HISTORY_V277_G_ROUNDING_OR_TARGET_DRIFT"):
            self.run_build(native_result=self.v277_native_G(level=335))
        self.assertFalse((self.root/"sessions").exists())

    def physical_layout(self, rating=23):
        ordinary = [240908] * 6
        return ({
            "schema": build.physical_gems.SCHEMA,
            "status":"PHYSICAL_GEMS_STAGED_SOURCE_AND_SOCKET_PROOFS_PENDING",
            "ordinary_gem_ids":ordinary,
            "ordinary_count":len(ordinary),"socket_total":7,
            "socket_counts":{"head":1,"wrists":2,"waist":2,"feet":2},
            "special_gem_id":240967,"special_slot":"head",
        }, {"240908":rating})

    def physical_effect(self, *, kind="flask", hand=None, static=True):
        import v222_season_budget_contract as budget
        stats=budget.STATS
        vec={k:0 for k in stats}
        vec["crit_rating"]=165 if kind=="flask" else 16
        if kind=="temporary_enchant":
            vec["haste_rating"]=17
        token=("test_flask_2" if kind=="flask" else
               "main_hand:thalassian_phoenix_oil")
        item_id=241326 if kind=="flask" else 243734
        bound={
            "schema":build.consumable_simc_relation.MEASUREMENT_BINDING_SCHEMA,
            "game_build":self.catalog["game_build"],
            "simc_revision":self.catalog["simc_revision"],
            "physical_item_id":item_id,"kind":kind,
            "simc_input_token":token,"crafting_quality":2,
            "simc_enchant_id":None if kind=="flask" else 8052,
            "selected_hand":hand,
            "source_stage_receipt_sha256":"c"*64,
            "source_candidate_sha256":"d"*64,
            "source_only":True,"environment_ready":False}
        observation={
            "kind":kind,"token":token,
            "status":("SIMC_STATIC_CHMV_EFFECT_OBSERVED_NOT_ADMITTED"
                      if static else
                      "SIMC_CONDITIONAL_OR_NONSTATIC_EFFECT_PENDING"),
            "simc_revision":self.catalog["simc_revision"],
            "binary_sha256":"e"*64,
            "source_profile_sha256":"f"*64,
            "static_CHMV_candidate":vec if static else None,
            "F_candidate_unadmitted":(
                sum(vec.values()) if kind=="flask" and static else None),
            "O_candidate_unadmitted":(
                vec if kind=="temporary_enchant" and static else None),
            "native_case_receipts":[
                {"variant":k,"receipt_sha256":h*64}
                for k,h in (("baseline","a"),("active","b"))],
            "new_native_calls":0}
        if static:
            observation["observed"]={
                "schema":build.simc_snapshot_delta.SCHEMA,
                "kind":kind,"token":token,
                "simc_revision":self.catalog["simc_revision"],
                "binary_sha256":observation["binary_sha256"],
                "source_profile_sha256":observation["source_profile_sha256"],
                "static_CHMV_candidate":vec}
        request={
            "source_profile_path":"source.simc","kind":kind,
            "item_id":item_id}
        if kind=="temporary_enchant":
            request["hand"]=hand
        return request,bound,observation

    def test_p3_ey_v232_intrinsic_j_source_reuses_original_build(self):
        layout,ratings=self.physical_layout()
        previous=self.collected.get("fresh_one_spec_simc_representative")
        counts={"head":1,"wrists":2,"waist":2,"feet":2}
        original={"status":
                      "FRESH_ONE_SPEC_SIMC_G_SOURCE_CANDIDATE_PENDING_NATIVE",
                  "source_stage":{"status":"REUSED_VERIFIED",
                                  "receipt_sha256":"a"*64},
                  "intrinsic_socket_counts_by_selected_slot_source_only":counts,
                  "selected_slot_count":4,"intrinsic_socket_total_source_only":7,
                  "added_socket_bonus_and_game_permission_not_proven":True}
        try:
            self.collected["fresh_one_spec_simc_representative"]=original
            result=self.run_build(proof=False,gem_layout=layout,gem_ratings=ratings)
            join=result["source_compilation"][
                "selected_J_intrinsic_socket_origin_unadmitted"]
            self.assertEqual(join["status"],"J_INTRINSIC_COUNTS_BOUND_SOURCE_ONLY")
            self.assertEqual(join["observed_J_unadmitted"],138)
            self.assertEqual(join["additional_socket_proof_required_by_slot"],{})
            self.assertFalse(join["J_approved"])
            self.assertIsNone(result["J"])
            self.assertEqual(result["native_calls"],0)
            self.collected["fresh_one_spec_simc_representative"]={
                **original,"intrinsic_socket_counts_by_selected_slot_source_only":{
                    **counts,"wrists":1},
                "intrinsic_socket_total_source_only":6}
            more=self.run_build(proof=False,gem_layout=layout,gem_ratings=ratings)
            extra=more["source_compilation"][
                "selected_J_intrinsic_socket_origin_unadmitted"]
            self.assertEqual(extra["status"],
                             "J_ADDITIONAL_SOCKET_SOURCE_PROOF_PENDING")
            self.assertEqual(extra["additional_socket_proof_required_by_slot"],
                             {"wrists":1})
            self.assertFalse(extra["J_approved"])
            self.collected["fresh_one_spec_simc_representative"]={
                **original,"intrinsic_socket_total_source_only":8}
            with self.assertRaisesRegex(
                    build.EnvironmentBuildBlocked,
                    "V216_J_V232_ORIGINAL_SEALED_SOURCE_DRIFT"):
                self.run_build(proof=False,gem_layout=layout,gem_ratings=ratings)
            self.collected.pop("fresh_one_spec_simc_representative")
            missing=self.run_build(
                proof=False,gem_layout=layout,gem_ratings=ratings)[
                    "source_compilation"][
                    "selected_J_intrinsic_socket_origin_unadmitted"]
            self.assertEqual(missing["status"],"J_V232_INTRINSIC_SOURCE_PENDING")
            self.assertIsNone(missing["intrinsic_socket_counts_by_slot"])
        finally:
            if previous is None:
                self.collected.pop("fresh_one_spec_simc_representative",None)
            else:
                self.collected["fresh_one_spec_simc_representative"]=previous

    def test_real_id_gem_layout_J_reused_in_zero_history_without_promotion(self):
        layout, ratings=self.physical_layout()
        result=self.run_build(proof=False,gem_layout=layout,
                              gem_ratings=ratings)
        j=result["source_compilation"]["physical_gem_J_arithmetic_unadmitted"]
        self.assertEqual(j["J_candidate_unadmitted"],138)
        self.assertEqual(result["source_compilation"][
            "physical_gem_layout_unadmitted"],layout)
        self.assertEqual(j["physical_gem_item_ids"],[240908]*6)
        self.assertFalse(j["game_socket_legality_verified_here"])
        self.assertNotIn("preprofile_budget_arithmetic_unadmitted",
                         result["source_compilation"])
        self.assertIsNone(result["J"])
        self.assertFalse(result["zero_history_build"]["environment_ready"])

    def preflight_with_sealed_gem_raw(self, layout, raw, manual_ratings=None,
                                      pinned_seed=None):
        gem_source={"candidate_path":str(self.root/"gem_candidate.json"),
                    "source_stage":{"receipt_sha256":"5"*64}}
        with (mock.patch.object(build.environment_manifest,"read_json",
                                return_value=(self.catalog,"a"*64)),
              mock.patch.object(build.source_to_catalog,"verify_catalog"),
              mock.patch.object(build.user_catalog,"public_options",
                                return_value=self.ui),
              mock.patch.object(build,"_fresh_gem_item_source_stage",
                                return_value=gem_source),
              mock.patch.object(build.gem_enchant_stage,"view",
                                return_value=raw) as view):
            result=build.preflight_new_season_source(
                source_catalog_path=self.path,
                expected_game_build=self.catalog["game_build"],
                expected_simc_revision=self.catalog["simc_revision"],
                source_snapshot_folder=self.wago,
                source_stage_root=self.root,
                gem_layout_receipt=layout,gem_rating_by_id=manual_ratings,
                pinned_gem_simc_source_folder=pinned_seed)
            self.assertEqual(view.call_args.kwargs["selected_gem_item_ids"],
                             layout["ordinary_gem_ids"])
            self.assertEqual(view.call_args.kwargs["selected_source_gem_item_ids"],
                             layout.get("source_observed_gem_item_ids"))
            self.assertEqual(view.call_args.kwargs[
                "selected_special_gem_item_id"],(
                    layout["special_gem_id"]
                    if "source_observed_gem_item_ids" in layout else None))
            return result

    def source_selected_future_gems(self):
        rows={slot:{"slot":slot,"item_id":100001,
                    "ilevel":334,"options":{}}
              for slot in ("head","waist","wrists")}
        plan={"socket_counts":{"head":1,"waist":1,"wrists":2},
              "special_gem_id":311003,"special_slot":"wrists",
              "ordinary_gem_ids":[311001,311001,311002],
              "source_observed_gem_item_ids":[311001,311002,311003]}
        _,layout=build.physical_gems.arrange(rows,plan,build.need)
        return layout

    def test_v221_one_new_special_and_ordinary_exact_source_link_no_admission(self):
        layout=self.source_selected_future_gems()
        raw={"status":"ENCHANT_RAW_POINTS_SOURCE_ONLY_J_NOT_APPROVED",
             "enchant_source_sha256":"4"*64,
             "selected_gem_raw_points_by_id_unadmitted":{
                 "311001":20,"311002":30},
             "selected_gem_all_raw_points_known":True,
             "selected_gem_v221_item_ids_unadmitted":[311001,311002,311003],
             "selected_gem_v221_same_build_items_all_present":True,
             "J":None,"environment_ready":False}
        pre=self.preflight_with_sealed_gem_raw(layout,raw)
        source=pre["selected_v221_gem_item_relation_unadmitted"]
        self.assertEqual(source["selected_item_ids"],
                         [311001,311002,311003])
        self.assertEqual(source["special_gem_item_id"],311003)
        self.assertEqual(source["v221_stage_receipt_sha256"],"5"*64)
        self.assertFalse(source["special_class_and_quality_verified"])
        self.assertFalse(source["game_socket_applicability_verified"])
        self.assertIsNone(
            source["selected_special_gem_raw_effect_unadmitted"])
        self.assertEqual(pre["physical_gem_J_arithmetic_unadmitted"][
            "J_candidate_unadmitted"],70)
        self.assertIsNone(pre["J"])
        self.assertFalse(pre["environment_ready"])
        bad={**raw,"selected_gem_v221_same_build_items_all_present":False,
             "selected_gem_v221_item_ids_unadmitted":[311001,311002],
             "selected_gem_v221_missing_item_ids":[311003]}
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_V221_SELECTED_SAME_BUILD_GEM_ITEM_SOURCE_REQUIRED"):
            self.preflight_with_sealed_gem_raw(layout,bad)

    def test_p3_fq_selected_F_measures_only_exact_source_and_reuses_v278(self):
        (self.root/"v233.profile").write_text(
            "paladin=simc_source_g_probe\nrace=dwarf\nspec=retribution\n"
            "main_hand=simc_source_weapon,id=9010,ilevel=334,source=local\n",
            encoding="utf8")
        # The v281 source list already exists. Neither a new fetch nor
        # a competing flask Native measurement is needed for an exact ID.
        candidates=[
            {"physical_item_id":8111,"simc_input_token":"flask_bloom_1",
             "crafting_quality":1},
            {"physical_item_id":8112,"simc_input_token":"flask_bloom_2",
             "crafting_quality":2},
            {"physical_item_id":8223,"simc_input_token":"flask_storm_3",
             "crafting_quality":3}]
        collected={
            "expected_game_build":self.catalog["game_build"],
            "fresh_one_spec_physical_G_probe":{
                "profile_path":str(self.root/"v233.profile"),
                "source_stage":{"status":"REUSED_VERIFIED"}},
            "fresh_consumable_simc_effect_relation":{}}
        compiled={
            "status":"FRESH_V191_V211_V213_COMPILED_UNADMITTED",
            "stage_root":str(self.root),
            "simc_revision":self.catalog["simc_revision"],
            "automatic_F_O_measurement_candidates_unadmitted":{
                "flask":candidates,"oil":[]}}
        def resolve(**kwargs):
            self.assertEqual(kwargs["kind"],"flask")
            item=next(x for x in candidates
                      if x["physical_item_id"]==kwargs["item_id"])
            return {**item,"selected_hand":None}
        native={"status":"NATIVE_JSON2_CAPTURED",
                "new_native_calls":2,"kind":"flask"}
        with mock.patch.object(
                build.consumable_simc_relation,"resolve_native_input",
                side_effect=resolve) as exact, mock.patch.object(
                build.native_effect_pair,"measure",
                return_value=native) as measure:
            rows,selected=build._auto_F_native_from_sealed_v281(
                collected=collected,compilation=compiled,
                binary=self.root/"fake_simc",selected_item_id=8112)
            self.assertEqual([x["physical_item_native_source_unadmitted"][
                "physical_item_id"] for x in rows],[8112])
            self.assertEqual(selected["attempted"],1)
            self.assertEqual(selected["remaining"],0)
            self.assertEqual(selected["total_source_candidates"],1)
            self.assertEqual(selected["all_source_candidate_count"],3)
            self.assertEqual(selected["selected_exact_item_id"],8112)
            self.assertEqual(selected["new_native_calls"],2)
            self.assertFalse(selected["environment_ready"])
            self.assertFalse(selected["F_approved"])
            exact.assert_called_once()
            measure.assert_called_once()
            exact.reset_mock()
            measure.reset_mock()
            rows,low=build._auto_F_native_from_sealed_v281(
                collected=collected,compilation=compiled,
                binary=self.root/"fake_simc",selected_item_id=8111)
            self.assertEqual(rows,[])
            self.assertIn("AUTO_F_SELECTED_ITEM_BELOW_OBSERVED_QUALITY",
                          low["requires"])
            rows,missing=build._auto_F_native_from_sealed_v281(
                collected=collected,compilation=compiled,
                binary=self.root/"fake_simc",selected_item_id=9999)
            self.assertEqual(rows,[])
            self.assertIn("AUTO_F_SELECTED_EXACT_ITEM_NOT_IN_V281_SOURCE",
                          missing["requires"])
            exact.assert_not_called()
            measure.assert_not_called()
            with self.assertRaisesRegex(
                    build.EnvironmentBuildBlocked,
                    "V216_AUTO_F_O_NATIVE_BUDGET_OR_KIND_INVALID"):
                build._auto_F_native_from_sealed_v281(
                    collected=collected,compilation=compiled,
                    binary=self.root/"fake_simc",
                    kind="temporary_enchant",selected_item_id=8112)
            # No explicit selection now measures only the top available
            # source quality per distinct SimC token family. The lower bloom
            # rank remains in the original v281 source; no effect admission.
            rows,all_candidates=build._auto_F_native_from_sealed_v281(
                collected=collected,compilation=compiled,
                binary=self.root/"fake_simc")
            self.assertEqual([x["physical_item_native_source_unadmitted"][
                "physical_item_id"] for x in rows],[8112,8223])
            self.assertEqual(len(rows),2)
            self.assertEqual(all_candidates["new_native_calls"],4)
            self.assertEqual(all_candidates["all_source_candidate_count"],3)
            self.assertEqual(all_candidates["deferred_lower_quality_measurements"],1)
            self.assertTrue(all_candidates["source_quality_priority_only_not_policy_A"])
            self.assertNotIn("selected_exact_item_id",all_candidates)

    def test_p3_fp_single_stat_cannot_enter_J_even_with_manual_number(self):
        # A physically selected one-stat ordinary gem may remain on the
        # SimC socket layout for special-effect activation, but never in J.
        layout=self.source_selected_future_gems()
        raw={"status":"ENCHANT_RAW_POINTS_SOURCE_ONLY_J_NOT_APPROVED",
             "enchant_source_sha256":"4"*64,
             "selected_gem_raw_points_by_id_unadmitted":{
                 "311001":20,"311002":30},
             "selected_gem_all_raw_points_known":True,
             "selected_ordinary_gem_two_stat_budget_eligible_unadmitted":False,
             "selected_ordinary_gem_two_stat_by_id_unadmitted":{
                 "311001":False,"311002":True},
             "selected_one_stat_gem_activation_only_item_ids":[311001],
             "selected_gem_v221_item_ids_unadmitted":[311001,311002,311003],
             "selected_gem_v221_same_build_items_all_present":True,
             "J":None,"environment_ready":False}
        # Neither raw (20+20+30) nor a manually provided numeric override
        # may convert a one-stat activation gem into J budget evidence.
        for manual in (None,{"311001":20,"311002":30}):
            with self.subTest(manual=manual):
                pre=self.preflight_with_sealed_gem_raw(
                    layout,raw,manual_ratings=manual)
                self.assertIn("physical_gem_layout_unadmitted",pre)
                self.assertNotIn("physical_gem_J_arithmetic_unadmitted",pre)
                self.assertTrue(pre[
                    "ordinary_gem_J_two_stat_requirement_pending"])
                self.assertIn(
                    "ORDINARY_GEM_J_REQUIRES_EXACTLY_TWO_SECONDARY_STATS",
                    pre["requires"])
                self.assertIsNone(pre["J"])
                self.assertFalse(pre["environment_ready"])
        # Proven two-stat ordinary sources retain the normal numeric
        # projection, including repeated physical gems in multiple sockets.
        approved_shape={**raw,
            "selected_ordinary_gem_two_stat_budget_eligible_unadmitted":True,
            "selected_ordinary_gem_two_stat_by_id_unadmitted":{
                "311001":True,"311002":True},
            "selected_one_stat_gem_activation_only_item_ids":[]}
        pre=self.preflight_with_sealed_gem_raw(
            layout,approved_shape)
        self.assertEqual(pre[
            "physical_gem_J_arithmetic_unadmitted"][
                "J_candidate_unadmitted"],70)
        self.assertNotIn(
            "ordinary_gem_J_two_stat_requirement_pending",pre)
        self.assertIsNone(pre["J"])

    def test_special_raw_chmv_source_reaches_preflight_without_fake_j(self):
        layout=self.source_selected_future_gems()
        vec={stat:0 for stat in build.season_budget_contract.STATS}
        vec["mastery_rating"]=35
        raw={
            "status":"ENCHANT_RAW_POINTS_SOURCE_ONLY_J_NOT_APPROVED",
            "enchant_source_sha256":"4"*64,
            "selected_gem_raw_points_by_id_unadmitted":{
                "311001":20,"311002":30},
            "selected_gem_all_raw_points_known":True,
            "selected_gem_v221_item_ids_unadmitted":[311001,311002,311003],
            "selected_gem_v221_same_build_items_all_present":True,
            "selected_special_gem_raw_effect_unadmitted":{
                "item_id":311003,
                "effect_classification":
                    "RAW_STATIC_CHMV_POINTS_CANDIDATE_ONLY",
                "raw_static_CHMV_vector_candidate_unadmitted":vec,
                "raw_static_CHMV_total_candidate_unadmitted":35,
                "missing_or_nonstatic_never_assumed_zero":True,
                "simc_effective_rating_verified":False,
                "J_budget_attribution_verified":False},
            "J":None,"environment_ready":False}
        pre=self.preflight_with_sealed_gem_raw(layout,raw)
        link=pre["selected_v221_gem_item_relation_unadmitted"]
        self.assertEqual(link[
            "selected_special_gem_raw_effect_unadmitted"][
            "raw_static_CHMV_total_candidate_unadmitted"],35)
        self.assertEqual(pre["physical_gem_J_arithmetic_unadmitted"][
            "J_candidate_unadmitted"],70)
        self.assertIsNone(pre["J"])
        numeric=build._zero_history_auto_v222_numeric_preview(
            preflight={**pre,
                "v222_G_component_reference_unadmitted":
                    self.table[334]["components"]["G"],
                "proposed_budget_arithmetic_unadmitted":pre.get(
                    "proposed_budget_arithmetic_unadmitted")},
            native_numeric={"flask":[],"oil":[]},
            source_choices={"oil_representative_weapon_matches_unadmitted":[]},
            selected={"flask_item_id":241326,
                      "oil_item_ids_by_hand":{}},
            gem_ratings={"311001":20,"311002":30},
            target_ilevel=334,manual_final_T=None)
        self.assertIsNone(numeric["calculation"])
        self.assertNotIn(
            "SPECIAL_GEM_STATIC_CHMV_J_BUDGET_ATTRIBUTION_PENDING",
            numeric["requires"])
        self.assertEqual(numeric["J_accounting_policy"],
                         "ORDINARY_GEM_NOMINAL_SECONDARY_SUM_ONLY")
        bad={**raw,"selected_special_gem_raw_effect_unadmitted":{
            **raw["selected_special_gem_raw_effect_unadmitted"],
            "item_id":999999}}
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_SPECIAL_GEM_RAW_EFFECT_SOURCE_SCOPE_DRIFT"):
            self.preflight_with_sealed_gem_raw(layout,bad)

    def test_p3_ez_special_static_raw_does_not_expand_nominal_j(self):
        layout=self.source_selected_future_gems()
        vec={key:0 for key in build.season_budget_contract.STATS}
        vec["mastery_rating"]=80
        raw={
            "status":"ENCHANT_RAW_POINTS_SOURCE_ONLY_J_NOT_APPROVED",
            "enchant_source_sha256":"4"*64,
            "selected_gem_raw_points_by_id_unadmitted":{
                "311001":20,"311002":30},
            "selected_gem_all_raw_points_known":True,
            "selected_gem_v221_item_ids_unadmitted":[311001,311002,311003],
            "selected_gem_v221_same_build_items_all_present":True,
            "selected_special_gem_raw_effect_unadmitted":{
                "item_id":311003,
                "effect_classification":"RAW_STATIC_CHMV_POINTS_CANDIDATE_ONLY",
                "raw_static_CHMV_vector_candidate_unadmitted":vec,
                "raw_static_CHMV_total_candidate_unadmitted":80,
                "missing_or_nonstatic_never_assumed_zero":True,
                "simc_effective_rating_verified":False,
                "J_budget_attribution_verified":False},
            "J":None,"environment_ready":False}
        pre=self.preflight_with_sealed_gem_raw(layout,raw)
        j=pre["physical_gem_J_arithmetic_unadmitted"]
        self.assertEqual(j["J_candidate_unadmitted"],70)
        self.assertEqual(j["special_gem_count_in_J"],0)
        self.assertFalse(j["simc_effective_rating_is_budget_gate"])
        numeric,_=self.selected_physical_pair()
        pre={**pre,"v277_native_G_preprofile_unadmitted":{
            "status":"NATIVE_G_NUMERIC_SOURCE_ONLY_JFO_AND_ADMISSION_PENDING",
            "standardized_G":2850,"native_json2_sha256":"a"*64,
            "target_ilevel":334}}
        candidate=build._zero_history_auto_v222_numeric_preview(
            preflight=pre,native_numeric=numeric,
            source_choices={"oil_representative_weapon_matches_unadmitted":[]},
            selected={"flask_item_id":241326,"oil_item_ids_by_hand":{}},
            gem_ratings={"311001":20,"311002":30},
            target_ilevel=334,manual_final_T=None)
        self.assertEqual(candidate["calculation"]["J"],70)
        self.assertEqual(candidate["calculation"]["base_B"],3085)
        self.assertEqual(candidate["J_accounting_policy"],
                         "ORDINARY_GEM_NOMINAL_SECONDARY_SUM_ONLY")
        self.assertFalse(candidate["environment_ready"])

    def test_p3_ei_source_property_rows_reach_v216_and_v098_unadmitted(self):
        import v098_target_user_scenario_bootstrap as boot
        layout=self.source_selected_future_gems()
        rows=[
            {"item_id":i,"gem_property_id":i-300000,
             "enchant_id":100+i,"color_mask":(1 if i==311003 else 2),
             "minimum_ilevel":(345 if i==311003 else 300),
             "expansion_id":12}
            for i in (311001,311002,311003)]
        raw={"status":"ENCHANT_RAW_POINTS_SOURCE_ONLY_J_NOT_APPROVED",
             "enchant_source_sha256":"4"*64,
             "selected_gem_raw_points_by_id_unadmitted":{
                 "311001":20,"311002":30},
             "selected_gem_all_raw_points_known":True,
             "selected_gem_v221_item_ids_unadmitted":[311001,311002,311003],
             "selected_gem_v221_same_build_items_all_present":True,
             "selected_gem_v221_source_properties_complete":True,
             "selected_gem_v221_source_properties_unadmitted":rows,
             "J":None,"environment_ready":False}
        pre=self.preflight_with_sealed_gem_raw(layout,raw)
        linked=pre["selected_v221_gem_item_relation_unadmitted"]
        self.assertTrue(linked["gem_property_source_fields_complete"])
        self.assertEqual(linked["selected_gem_property_records_unadmitted"],rows)
        self.assertEqual(linked["special_gem_source_property_unadmitted"],
                         rows[2])
        self.assertFalse(linked["special_class_and_quality_verified"])
        self.assertFalse(linked["game_socket_applicability_verified"])
        joined={"physical_gem_layout_unadmitted":layout,
                "physical_gem_J_arithmetic_unadmitted":
                    pre["physical_gem_J_arithmetic_unadmitted"],
                "selected_v221_gem_item_relation_unadmitted":linked}
        inputs={"v216_numeric_preview":{"calculation":{
                    "J":70,"F":165,"game_build":self.catalog["game_build"],
                    "target_ilevel":334}},
                "flask":{"simc_input_token":"flask_of_the_shattered_sun_2",
                    "static_CHMV_vector":{
                        "crit_rating":165,"haste_rating":0,
                        "mastery_rating":0,"versatility_rating":0}}}
        derived=boot._season_settings_from_v216(
            compilation=joined,numeric_inputs=inputs,need=boot.need)
        self.assertEqual(derived["status"],
                         "SEASON_SETTINGS_PHYSICAL_GEMS_FLASK_COMPOSED_UNADMITTED")
        self.assertEqual(derived[
            "selected_v221_gem_property_inputs_unadmitted"],rows)
        self.assertFalse(derived[
            "source_minimum_ilevel_for_selected_gems_observed_only"])
        self.assertFalse(derived["game_socket_legality_authenticated_here"])
        bad={**raw,"selected_gem_v221_source_properties_unadmitted":
             [rows[0],rows[1],{**rows[2],"item_id":999999}]}
        with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                    "SOURCE_PROPERTY_RECORDS_DRIFT"):
            self.preflight_with_sealed_gem_raw(layout,bad)

    def test_p3_ej_reuses_pinned_simc_selected_gem_quality_with_stage_cache(self):
        from runner import v229_simc_only_source_seed as source_seed
        import v098_target_user_scenario_bootstrap as boot
        selected=[311001,311002,311003]
        simc_dir=self.root/"source"/"v256_full_pinned_simc"
        simc_dir.mkdir(parents=True,exist_ok=True)
        receipt={"schema":source_seed.SCHEMA,
                 "provenance_tree_blob_authenticated":True,
                 "item_data_present":True,
                 "simc_generated_build":self.catalog["game_build"],
                 "simc_revision":self.catalog["simc_revision"],
                 "receipt_sha256":"8"*64,
                 "source_files":{"item_data.inc":{"sha256":"7"*64}}}
        (simc_dir/source_seed.RECEIPT).write_text(
            json.dumps(receipt),encoding="utf8")
        items=[{"item_id":item_id,"quality":3,"crafting_quality":rank,
                "class_id":3,"subclass_id":0}
               for item_id,rank in zip(selected,(1,3,2))]
        parsed={"schema":build.simc_item_metadata.SCHEMA,
                "game_build":self.catalog["game_build"],
                "simc_revision":self.catalog["simc_revision"],
                "requested_item_count":3,
                "source_receipt_sha256":"8"*64,
                "source_sha256":"7"*64,
                "items":items}
        with mock.patch.object(
                build.simc_item_metadata,"from_seed",return_value=parsed) as parser:
            first=build._fresh_selected_gem_simc_quality_stage(
                stage_root=self.root,seed_directory=simc_dir,
                game_build=self.catalog["game_build"],
                simc_revision=self.catalog["simc_revision"],
                selected_item_ids=selected)
            again=build._fresh_selected_gem_simc_quality_stage(
                stage_root=self.root,seed_directory=simc_dir,
                game_build=self.catalog["game_build"],
                simc_revision=self.catalog["simc_revision"],
                selected_item_ids=selected)
            parser.assert_called_once()
        self.assertEqual(first["status"],
                         "PINNED_SIMC_GEM_QUALITY_SOURCE_ONLY_UNADMITTED")
        self.assertEqual(first["selected_item_quality_unadmitted"],items)
        self.assertTrue(first["quality_source_authenticated"])
        self.assertEqual(again["v230_stage_cache_status"],"REUSED_VERIFIED")
        self.assertFalse(first["highest_quality_selection_verified"])
        self.assertFalse(first["special_gem_role_verified"])
        self.assertEqual(first["native_calls"],0)
        layout=self.source_selected_future_gems()
        raw={"status":"ENCHANT_RAW_POINTS_SOURCE_ONLY_J_NOT_APPROVED",
             "enchant_source_sha256":"4"*64,
             "selected_gem_raw_points_by_id_unadmitted":{
                 "311001":20,"311002":30},
             "selected_gem_all_raw_points_known":True,
             "selected_gem_v221_item_ids_unadmitted":selected,
             "selected_gem_v221_same_build_items_all_present":True,
             "J":None,"environment_ready":False}
        # The existing sealed stage is hit without another v230 parse.
        pre=self.preflight_with_sealed_gem_raw(
            layout,raw,pinned_seed=simc_dir)
        bound=pre["selected_v221_gem_item_relation_unadmitted"]
        self.assertEqual(
            bound["selected_simc_gem_quality_source_unadmitted"][
                "selected_item_quality_unadmitted"],items)
        self.assertFalse(bound["special_class_and_quality_verified"])
        self.assertIsNone(pre["J"])
        joined={"physical_gem_layout_unadmitted":layout,
                "physical_gem_J_arithmetic_unadmitted":
                    pre["physical_gem_J_arithmetic_unadmitted"],
                "selected_v221_gem_item_relation_unadmitted":bound}
        inputs={"v216_numeric_preview":{"calculation":{
                    "J":70,"F":165,"game_build":self.catalog["game_build"],
                    "target_ilevel":334}},
                "flask":{"simc_input_token":"flask_of_the_shattered_sun_2",
                    "static_CHMV_vector":{
                        "crit_rating":165,"haste_rating":0,
                        "mastery_rating":0,"versatility_rating":0}}}
        derived=boot._season_settings_from_v216(
            compilation=joined,numeric_inputs=inputs,need=boot.need)
        self.assertEqual(derived["selected_v230_gem_item_quality_unadmitted"],
                         items)
        self.assertFalse(derived["gem_highest_quality_verified_here"])
        bad={**first,"selected_item_ids":[311001,311003]}
        with mock.patch.object(
                build,"_fresh_selected_gem_simc_quality_stage",
                return_value=bad):
            with self.assertRaisesRegex(
                    build.EnvironmentBuildBlocked,"QUALITY_SOURCE_SCOPE_DRIFT"):
                self.preflight_with_sealed_gem_raw(
                    layout,raw,pinned_seed=simc_dir)
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_SELECTED_GEM_PINNED_V230_SCOPE_INVALID"):
            build._fresh_selected_gem_simc_quality_stage(
                stage_root=self.root,seed_directory=self.root,
                game_build=self.catalog["game_build"],
                simc_revision=self.catalog["simc_revision"],
                selected_item_ids=selected)

    def test_p3_ek_gem_effect_quality_reuses_original_v220_without_ui(self):
        import v098_target_user_scenario_bootstrap as boot
        layout=self.source_selected_future_gems()
        selected=[311001,311002,311003]
        properties=[
            {"item_id":item_id,
             "gem_property_id":item_id-300000,
             "enchant_id":991 if item_id!=311003 else 992,
             "color_mask":2 if item_id!=311003 else 1,
             "minimum_ilevel":300 if item_id!=311003 else 345,
             "expansion_id":12}
            for item_id in selected]
        vec={"crit_rating":20,"haste_rating":0,
             "mastery_rating":0,"versatility_rating":0}
        raw={"status":"ENCHANT_RAW_POINTS_SOURCE_ONLY_J_NOT_APPROVED",
             "enchant_source_sha256":"4"*64,
             "selected_gem_raw_points_by_id_unadmitted":{
                 "311001":20,"311002":20},
             "selected_gem_raw_CHMV_vectors_by_id_unadmitted":{
                 "311001":dict(vec),"311002":dict(vec)},
             "selected_gem_all_raw_points_known":True,
             "selected_gem_v221_item_ids_unadmitted":selected,
             "selected_gem_v221_same_build_items_all_present":True,
             "selected_gem_v221_source_properties_complete":True,
             "selected_gem_v221_source_properties_unadmitted":properties,
             "J":None,"environment_ready":False}
        quality_rows=[
            {"item_id":item_id,"quality":3,"crafting_quality":rank,
             "class_id":3,"subclass_id":0}
            for item_id,rank in zip(selected,(1,3,2))]
        quality={"status":"PINNED_SIMC_GEM_QUALITY_SOURCE_ONLY_UNADMITTED",
                 "game_build":self.catalog["game_build"],
                 "simc_revision":self.catalog["simc_revision"],
                 "selected_item_ids":selected,
                 "selected_item_quality_unadmitted":quality_rows,
                 "quality_source_authenticated":True,
                 "highest_quality_selection_verified":False}
        with mock.patch.object(
                build,"_fresh_selected_gem_simc_quality_stage",
                return_value=quality):
            pre=self.preflight_with_sealed_gem_raw(
                layout,raw,pinned_seed=self.root)
        source=pre["selected_v221_gem_item_relation_unadmitted"]
        verdict=source["gem_policy_A_source_and_quality_unadmitted"]
        self.assertEqual(verdict["status"],
                         "SELECTED_GEM_SOURCE_RELATION_AND_QUALITY_UNADMITTED")
        self.assertEqual(len(verdict["per_item_policy_A_source_only"]),3)
        self.assertEqual(verdict["automatically_eligible"],0)
        self.assertIsNone(pre["J"])
        for option in verdict["per_item_policy_A_source_only"]:
            self.assertEqual(option["decision"]["status"],
                             "PENDING_EXACT_EVIDENCE")
            self.assertNotIn(
                "EVIDENCE_MISSING:source_relation",
                option["decision"]["missing"])
            self.assertFalse(option["user_selectable"])
        groups=verdict["quality_source_groups_unadmitted"]
        self.assertEqual(len(groups),1)
        self.assertEqual(groups[0]["observed_item_ids"],
                         [311002,311001])
        self.assertEqual(groups[0][
            "highest_observed_quality_item_id_unadmitted"],311002)
        self.assertTrue(groups[0][
            "same_raw_four_stat_vector_source_only"])
        self.assertFalse(groups[0][
            "actual_same_effect_and_use_conditions_verified"])
        self.assertFalse(groups[0]["all_available_quality_ranks_verified"])
        self.assertFalse(groups[0]["quality_filtered_user_options"])
        self.assertFalse(verdict["environment_ready"])
        self.assertEqual(pre["physical_gem_J_arithmetic_unadmitted"][
            "J_candidate_unadmitted"],60)
        joined={"physical_gem_layout_unadmitted":layout,
                "physical_gem_J_arithmetic_unadmitted":
                    pre["physical_gem_J_arithmetic_unadmitted"],
                "selected_v221_gem_item_relation_unadmitted":source}
        numeric={"v216_numeric_preview":{"calculation":{
                     "J":60,"F":165,"game_build":self.catalog["game_build"],
                     "target_ilevel":334}},
                 "flask":{"simc_input_token":"flask_of_the_shattered_sun_2",
                     "static_CHMV_vector":{
                         "crit_rating":165,"haste_rating":0,
                         "mastery_rating":0,"versatility_rating":0}}}
        derived=boot._season_settings_from_v216(
            compilation=joined,numeric_inputs=numeric,need=boot.need)
        self.assertEqual(
            derived["gem_policy_A_source_and_quality_unadmitted"],verdict)
        self.assertFalse(derived["gem_highest_quality_verified_here"])
        self.assertFalse(derived["game_socket_legality_authenticated_here"])
        # A different stat vector or enchant ID must never be merged even
        # when quality ranks are ordered. No quality-based UI publication.
        mismatched={**raw,"selected_gem_raw_CHMV_vectors_by_id_unadmitted":{
            "311001":dict(vec),
            "311002":{**vec,"crit_rating":0,"haste_rating":20}}}
        with mock.patch.object(
                build,"_fresh_selected_gem_simc_quality_stage",
                return_value=quality):
            changed=self.preflight_with_sealed_gem_raw(
                layout,mismatched,pinned_seed=self.root)
        no_merge=changed["selected_v221_gem_item_relation_unadmitted"][
            "gem_policy_A_source_and_quality_unadmitted"][
                "quality_source_groups_unadmitted"][0]
        self.assertFalse(no_merge["same_raw_four_stat_vector_source_only"])
        self.assertIsNone(no_merge[
            "highest_observed_quality_item_id_unadmitted"])
        # The strongest observed comparable rating wins even when the
        # weaker candidate has a higher craft rank and a different minimum
        # item level. No exhaustive quality/use-condition certification.
        dominant={**raw,
          "selected_gem_raw_points_by_id_unadmitted":{
              "311001":26,"311002":20},
          "selected_gem_raw_CHMV_vectors_by_id_unadmitted":{
              "311001":{**vec,"crit_rating":26},
              "311002":dict(vec)},
          "selected_gem_v221_source_properties_unadmitted":[
              {**properties[0],"minimum_ilevel":315},
              properties[1],properties[2]]}
        with mock.patch.object(
                build,"_fresh_selected_gem_simc_quality_stage",
                return_value=quality):
            stronger=self.preflight_with_sealed_gem_raw(
                layout,dominant,pinned_seed=self.root)
        preferred=stronger["selected_v221_gem_item_relation_unadmitted"][
            "gem_policy_A_source_and_quality_unadmitted"][
                "quality_source_groups_unadmitted"][0]
        self.assertEqual(preferred["highest_observed_effect_item_id_source_only"],
                         311001)
        self.assertTrue(preferred[
            "observed_strongest_effect_sufficient_quality_policy"])
        self.assertFalse(preferred["same_raw_four_stat_vector_source_only"])
        different={**raw,"selected_gem_v221_source_properties_unadmitted":
            [properties[0],{**properties[1],"enchant_id":993},
             properties[2]]}
        with mock.patch.object(
                build,"_fresh_selected_gem_simc_quality_stage",
                return_value=quality):
            independent=self.preflight_with_sealed_gem_raw(
                layout,different,pinned_seed=self.root)
        separated=independent["selected_v221_gem_item_relation_unadmitted"][
            "gem_policy_A_source_and_quality_unadmitted"]
        self.assertEqual(separated["quality_source_groups_unadmitted"],[])

    def test_new_season_special_v098_source_settings_require_bound_v221_ids(self):
        import v098_target_user_scenario_bootstrap as boot
        layout=self.source_selected_future_gems()
        compilation={
            "physical_gem_layout_unadmitted":layout,
            "physical_gem_J_arithmetic_unadmitted":{
                "status":"PHYSICAL_GEM_J_ARITHMETIC_UNADMITTED",
                "physical_gem_item_ids":list(layout["ordinary_gem_ids"]),
                "J_candidate_unadmitted":70},
            "selected_v221_gem_item_relation_unadmitted":{
                "selected_item_ids":[311001,311002,311003],
                "special_gem_item_id":311003,
                "v221_stage_receipt_sha256":"5"*64,
                "same_build_gem_item_join_only":True}}
        inputs={
            "v216_numeric_preview":{"calculation":{
                "J":70,"F":165,
                "game_build":self.catalog["game_build"],
                "target_ilevel":334}},
            "flask":{
                "simc_input_token":"flask_of_the_shattered_sun_2",
                "static_CHMV_vector":{
                    "crit_rating":165,"haste_rating":0,
                    "mastery_rating":0,"versatility_rating":0}}}
        derived=boot._season_settings_from_v216(
            compilation=compilation,numeric_inputs=inputs,need=boot.need)
        self.assertEqual(derived["status"],
                         "SEASON_SETTINGS_PHYSICAL_GEMS_FLASK_COMPOSED_UNADMITTED")
        self.assertEqual(derived["v271_socket_plan_unadmitted"][
            "special_gem_id"],311003)
        self.assertEqual(derived["v271_socket_plan_unadmitted"][
            "source_observed_gem_item_ids"],[311001,311002,311003])
        self.assertEqual(derived["settings"]["default_consumables"][
            "gem_budget_J"],70)
        self.assertFalse(derived["game_socket_legality_authenticated_here"])
        unbound=dict(compilation)
        unbound.pop("selected_v221_gem_item_relation_unadmitted")
        missing=boot._season_settings_from_v216(
            compilation=unbound,numeric_inputs=inputs,need=boot.need)
        self.assertEqual(missing["status"],"SEASON_SETTINGS_SOURCE_PENDING")
        self.assertIn("V221_SELECTED_SPECIAL_GEM_SOURCE_LINK_PENDING",
                      missing["missing"])

    def test_sealed_v266_raw_gem_ID_reuses_v271_not_manual_J(self):
        layout,_=self.physical_layout()
        raw={"status":"ENCHANT_RAW_POINTS_SOURCE_ONLY_J_NOT_APPROVED",
             "enchant_source_sha256":"4"*64,
             "selected_gem_raw_points_by_id_unadmitted":{"240908":24},
             "selected_gem_unresolved_item_ids":[],
             "selected_gem_all_raw_points_known":True,
             "highest_quality_J_verified":False,"J":None,
             "environment_ready":False}
        auto=self.preflight_with_sealed_gem_raw(layout,raw)
        j=auto["physical_gem_J_arithmetic_unadmitted"]
        self.assertEqual(j["J_candidate_unadmitted"],144)
        self.assertEqual(j["rating_origin"],
                         "V266_RAW_SAME_BUILD_EFFECT_POINTS_ONLY")
        self.assertFalse(j["simc_effective_rating_verified"])
        self.assertFalse(j["highest_quality_verified"])
        self.assertEqual(j["source_enchant_sha256"],"4"*64)
        self.assertEqual(auto["physical_gem_raw_rating_by_id_unadmitted"],
                         {"240908":24})
        self.assertTrue(auto["physical_gem_raw_rating_source_only"])
        self.assertIsNone(auto["J"])
        self.assertFalse(auto["environment_ready"])
        manual=self.preflight_with_sealed_gem_raw(layout,raw,
                                                 {"240908":23})
        self.assertEqual(manual["physical_gem_J_arithmetic_unadmitted"][
            "J_candidate_unadmitted"],138)
        self.assertNotIn("rating_origin",manual[
            "physical_gem_J_arithmetic_unadmitted"])

    def test_sealed_v266_unresolved_raw_J_does_not_invent_zero(self):
        layout,_=self.physical_layout()
        raw={"status":"ENCHANT_RAW_POINTS_SOURCE_ONLY_J_NOT_APPROVED",
             "selected_gem_all_raw_points_known":False,
             "selected_gem_raw_points_by_id_unadmitted":{},
             "selected_gem_unresolved_item_ids":[240908],
             "J":None}
        pending=self.preflight_with_sealed_gem_raw(layout,raw)
        self.assertNotIn("physical_gem_J_arithmetic_unadmitted",pending)
        self.assertIsNone(pending["J"])
        self.assertFalse(pending["environment_ready"])

    def test_gem_j_conflicting_existing_budget_blocks_without_native(self):
        layout, ratings=self.physical_layout(rating=24)
        with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                    "V216_ZERO_HISTORY_SOURCE_COMPILER_INVALID:"
                                    "V216_J_RATING_DISAGREES"):
            self.run_build(gem_layout=layout,gem_ratings=ratings)
        self.assertFalse((self.root/"sessions").exists())

    def test_bound_exact_flask_native_is_source_only_F_candidate(self):
        request,bound,observed=self.physical_effect()
        result=self.run_build(proof=False,effect_requests=[request],
                              effect_resolver=bound,effect_observation=observed)
        native=result["source_compilation"][
            "physical_F_O_native_source_candidates_unadmitted"]
        self.assertEqual(len(native["flask"]),1)
        self.assertEqual(native["flask"][0]["physical_item_id"],241326)
        self.assertEqual(native["flask"][0]["rating_candidate_unadmitted"],165)
        self.assertIsNone(native["F"])
        self.assertIsNone(result["F"])
        self.assertFalse(result["zero_history_build"]["environment_ready"])

    def test_bound_oil_static_vector_does_not_certify_weapon_hand(self):
        request,bound,observed=self.physical_effect(
            kind="temporary_enchant",hand="main_hand")
        result=self.run_build(proof=False,effect_requests=[request],
                              effect_resolver=bound,effect_observation=observed)
        native=result["zero_history_build"][
            "physical_F_O_native_source_candidates_unadmitted"]
        self.assertIsNone(native["oil"][0]["rating_candidate_unadmitted"])
        self.assertEqual(native["oil"][0][
            "buffed_CHMV_observation_unadmitted"]["haste_rating"],17)
        self.assertEqual(native["oil"][0]["status"],
                         "SIMC_BUFFED_O_OBSERVED_NOT_STATIC_SOURCE")
        self.assertFalse(native["oil"][0][
            "weapon_and_hand_applicability_verified"])
        self.assertIsNone(native["O"])
        self.assertIsNone(result["O"])

    def test_no_static_delta_is_pending_not_zero_o(self):
        request,bound,observed=self.physical_effect(
            kind="temporary_enchant",hand="main_hand",static=False)
        result=self.run_build(proof=False,effect_requests=[request],
                              effect_resolver=bound,effect_observation=observed)
        native=result["source_compilation"][
            "physical_F_O_native_source_candidates_unadmitted"]
        self.assertIsNone(native["oil"][0]["rating_candidate_unadmitted"])
        self.assertEqual(native["oil"][0]["status"],
                         "SOURCE_ONLY_NATIVE_STATIC_RATING_PENDING")
        self.assertIsNone(native["O"])

    def test_tampered_native_item_token_fails_without_new_probe(self):
        request,bound,observed=self.physical_effect()
        bound["simc_input_token"]="wrong_flask"
        with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                    "V216_ZERO_HISTORY_FO_PHYSICAL_NATIVE_IDENTITY_DRIFT"):
            self.run_build(proof=False,effect_requests=[request],
                           effect_resolver=bound,effect_observation=observed)
        self.assertFalse((self.root/"sessions").exists())

    def test_token_only_legacy_probe_is_not_auto_promoted(self):
        _,_,observed=self.physical_effect()
        result=self.run_build(
            proof=False,effect_requests=[{
                "source_profile_path":"source.simc","kind":"flask",
                "token":"test_flask_2"}],
            effect_observation=observed)
        candidates=result["source_compilation"][
            "physical_F_O_native_source_candidates_unadmitted"]
        self.assertEqual(candidates["flask"],[])
        self.assertIsNone(candidates["F"])


    def test_flask_observed_quality_ranks_same_simc_family_only(self):
        first,_,_=self.physical_effect()
        def flask(iid,quality,crit,token):
            vector={k:0 for k in build.season_budget_contract.STATS}
            vector["crit_rating"]=crit
            return {
                "physical_item_id":iid,"crafting_quality":quality,
                "simc_input_token":token,
                "status":"SIMC_NATIVE_STATIC_NUMBER_SOURCE_ONLY",
                "rating_candidate_unadmitted":crit,
                "static_CHMV_vector_unadmitted":vector,
            }
        numeric={
            "status":"PHYSICAL_ITEM_SIMC_F_O_CANDIDATES_UNADMITTED",
            "flask":[
                flask(241327,1,151,"flask_of_the_shattered_sun_1"),
                flask(241326,2,165,"flask_of_the_shattered_sun_2")],
            "oil":[]}
        out=build._zero_history_quality_weapon_candidate_join(
            numeric=numeric,weapon_source={},
            game_build=self.catalog["game_build"],
            simc_revision=self.catalog["simc_revision"])
        family=out["flask_quality_groups_observed_unadmitted"][0]
        self.assertEqual(family["status"],
                         "TOP_QUALITY_AMONG_OBSERVED_ONLY")
        self.assertEqual(family[
            "highest_observed_quality_item_id_unadmitted"],241326)
        self.assertEqual(family["highest_observed_rating_unadmitted"],165)
        self.assertFalse(family["all_market_qualities_verified"])
        self.assertTrue(family[
            "observed_strongest_effect_sufficient_quality_policy"])
        # The effect magnitude, not the printed crafting-quality rank, wins.
        stronger={"status":"PHYSICAL_ITEM_SIMC_F_O_CANDIDATES_UNADMITTED",
                  "flask":[
                    flask(241327,1,180,"flask_of_the_shattered_sun_1"),
                    flask(241326,2,165,"flask_of_the_shattered_sun_2")],
                  "oil":[]}
        preferred=build._zero_history_quality_weapon_candidate_join(
            numeric=stronger,weapon_source={},
            game_build=self.catalog["game_build"],
            simc_revision=self.catalog["simc_revision"])[
                "flask_quality_groups_observed_unadmitted"][0]
        self.assertEqual(preferred[
            "highest_observed_quality_item_id_unadmitted"],241327)
        self.assertEqual(preferred["highest_observed_rating_unadmitted"],180)
        self.assertTrue(preferred[
            "observed_strongest_effect_sufficient_quality_policy"])
        self.assertIsNone(out["F"])
        self.assertFalse(out["user_selectable"])

    def test_flask_different_stats_or_nonmonotone_not_merged_or_promoted(self):
        z={k:0 for k in build.season_budget_contract.STATS}
        a=dict(z,crit_rating=151)
        b=dict(z,haste_rating=165)
        def option(iid,rank,vector):
            return {"physical_item_id":iid,"crafting_quality":rank,
                    "simc_input_token":"flask_of_same_stem_"+str(rank),
                    "status":"SIMC_NATIVE_STATIC_NUMBER_SOURCE_ONLY",
                    "rating_candidate_unadmitted":sum(vector.values()),
                    "static_CHMV_vector_unadmitted":vector}
        native={"status":"PHYSICAL_ITEM_SIMC_F_O_CANDIDATES_UNADMITTED",
                "flask":[option(1,1,a),option(2,2,b)],"oil":[]}
        out=build._zero_history_quality_weapon_candidate_join(
            numeric=native,weapon_source=None,
            game_build=self.catalog["game_build"],
            simc_revision=self.catalog["simc_revision"])
        group=out["flask_quality_groups_observed_unadmitted"][0]
        self.assertEqual(group["status"],"QUALITY_STATIC_STATS_NOT_COMPARABLE")
        self.assertIsNone(group[
            "highest_observed_quality_item_id_unadmitted"])
        self.assertIsNone(out["F"])

    def existing_oil_mask_fixture(self,matched=True):
        return {
            "schema":"v286_representative_oil_source_compatibility_v1",
            "status":("REPRESENTATIVE_OIL_MASK_MATCH_SOURCE_ONLY"
                      if matched else "REPRESENTATIVE_OIL_MASK_MATCH_PENDING"),
            "same_build_source_only":True,
            "game_build":self.catalog["game_build"],
            "simc_revision":self.catalog["simc_revision"],
            "environment_ready":False,
            "source_stage_identities":{
                "OIL":{"candidate_sha256":"a"*64}},
            "candidate_options":([{
                "oil_item_id":243734,
                "quality_rank":2,"simc_token":"thalassian_phoenix_oil",
                "simc_enchant_id":8052,"hand":"main_hand",
                "representative_weapon_id":9101,
                "matched_same_build_spell_equipped_masks":True,
                "user_selectable":False}]
                if matched else []),
        }

    def test_oil_native_rating_attaches_only_to_existing_representative_weapon(self):
        request,bound,observed=self.physical_effect(
            kind="temporary_enchant",hand="main_hand")
        self.compiled["representative_oil_source_options_unadmitted"]=(
            self.existing_oil_mask_fixture())
        out=self.run_build(proof=False,effect_requests=[request],
                           effect_resolver=bound,effect_observation=observed)
        quality=out["source_compilation"][
            "observed_quality_weapon_choices_unadmitted"]
        record=quality["oil_representative_weapon_matches_unadmitted"][0]
        self.assertEqual(record["status"],
            "SAME_BUILD_REPRESENTATIVE_WEAPON_MASK_MATCH_SOURCE_ONLY")
        self.assertEqual(record[
            "selected_representative_weapon_id_unadmitted"],9101)
        self.assertIsNone(record["static_O_for_hand_unadmitted"])
        self.assertEqual(record["status"],
                         "SAME_BUILD_REPRESENTATIVE_WEAPON_MASK_MATCH_SOURCE_ONLY")
        self.assertFalse(record["user_selectable"])
        self.assertIsNone(quality["O"])
        self.assertFalse(out["zero_history_build"]["environment_ready"])

    def test_oil_offhand_shield_or_unresolved_mask_not_assumed_eligible(self):
        request,bound,observed=self.physical_effect(
            kind="temporary_enchant",hand="main_hand")
        src=self.existing_oil_mask_fixture(matched=False)
        native=build._zero_history_F_O_native_component_candidates(
            observations=[{**observed,
                "physical_item_native_source_unadmitted":bound}],
            game_build=self.catalog["game_build"],
            simc_revision=self.catalog["simc_revision"])
        q=build._zero_history_quality_weapon_candidate_join(
            numeric=native,weapon_source=src,
            game_build=self.catalog["game_build"],
            simc_revision=self.catalog["simc_revision"])
        entry=q["oil_representative_weapon_matches_unadmitted"][0]
        self.assertEqual(entry["status"],
                         "REPRESENTATIVE_WEAPON_MASK_NOT_MATCHED_OR_PENDING")
        self.assertIsNone(entry["static_O_for_hand_unadmitted"])
        self.assertIsNone(q["O"])

    def test_oil_foreign_weapon_source_build_or_revision_blocks(self):
        req,bound,obs=self.physical_effect(
            kind="temporary_enchant",hand="main_hand")
        native=build._zero_history_F_O_native_component_candidates(
            observations=[{**obs,
                "physical_item_native_source_unadmitted":bound}],
            game_build=self.catalog["game_build"],
            simc_revision=self.catalog["simc_revision"])
        src=self.existing_oil_mask_fixture()
        src["game_build"]="12.2.0.99999"
        with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                    "V216_FO_V286_WEAPON_SOURCE_IDENTITY_DRIFT"):
            build._zero_history_quality_weapon_candidate_join(
                numeric=native,weapon_source=src,
                game_build=self.catalog["game_build"],
                simc_revision=self.catalog["simc_revision"])


    def test_selected_items_without_native_observations_remain_visible_pending(self):
        selected={"flask_item_id":241326,
                  "oil_item_ids_by_hand":{"main_hand":243734}}
        out=self.run_build(selected_budget_items=selected)
        linked=out["source_compilation"][
            "selected_physical_F_O_budget_link_unadmitted"]
        self.assertEqual(linked["status"],"SELECTED_PHYSICAL_F_O_SOURCE_PENDING")
        self.assertEqual(linked["selected_physical_items"],selected)
        self.assertFalse(linked["v222_numbers_reconciled"])
        self.assertFalse(out["zero_history_build"]["user_session_created"])
        self.assertEqual(out["native_calls"],0)

    def test_t1_incomplete_selected_budget_preserves_original_source_stage(self):
        """The real v216 coordinator must stage v212 even with pending F/O.

        Only the last v212 stage writer is observed here; the full external
        cold start remains the separate T1 acceptance objective.
        """
        previous=self.compiled
        self.compiled={
            **previous,
            **{name:{"status":"REUSED_VERIFIED",
                     "receipt_sha256":str(i)*64}
               for i,name in enumerate(
                   ("v191_stage","v211_stage","v213_stage"),1)},
        }
        selected={"flask_item_id":241326,
                  "oil_item_ids_by_hand":{"main_hand":243734}}
        try:
            # This focused fake compiler has NO actual v217 source bytes:
            # never treat its fabricated receipt IDs as Policy A proof.
            # Real v241/v217 source-relation path is tested separately in
            # test_v240 (no internal source-stage mocks).
            with mock.patch.object(
                    build,"_v217_policy_A_source_relation_receipts",
                    return_value={}) as no_fake_policy, mock.patch.object(
                    build,"_stage_source_environment_only",
                    return_value={"status":"FRESH_SEASON_ENVIRONMENT_STAGED_NOT_INSTALLED",
                                  "environment_ready":False,
                                  "environment_installed":False}) as staged:
                result=self.run_build(
                    proof=False,selected_budget_items=selected)
                self.assertTrue(no_fake_policy.called)
        finally:
            self.compiled=previous
        staged.assert_called_once()
        self.assertIsNone(staged.call_args.kwargs["selected_numeric"])
        self.assertEqual(
            result["source_compilation"]["versioned_environment_source_stage"]
                  ["status"],
            "FRESH_SEASON_ENVIRONMENT_STAGED_NOT_INSTALLED")
        numeric=result["source_compilation"][
            "selected_auto_v222_numeric_preview_unadmitted"]
        self.assertIsNone(numeric["calculation"])
        self.assertIn("SELECTED_AUTO_GJFO_SAME_SEASON_G_BUDGET_SOURCE_PENDING",
                      result["zero_history_build"]["requires"])
        self.assertFalse(result["zero_history_build"]["environment_ready"])
        self.assertEqual(result["native_calls"],0)

    def test_original_v277_native_G_owner_reuses_receipt_and_merges(self):
        # P3-EX exercises the source-owner boundary with synthetic receipt
        # bytes. This is not a real Native measurement nor season READY.
        import hashlib
        import v222_season_budget_contract as budget
        native=self.v277_native_G()
        stage=self.root/"source"
        stage.mkdir(exist_ok=True)
        folder=stage/("v277_native_G_"+"a"*24)
        folder.mkdir()
        level=334
        identity={
            "source_game_build":self.catalog["game_build"],
            "simc_source_revision":self.catalog["simc_revision"],
            "target_ilevel":level,
            "source_receipt_sha256":native["source_profile_receipt_sha256"],
            "executable_sha256":native["native_binary_sha256"],
            "compiled_game_build_not_proven":True}
        observed={
            "observed_G_total":native["observed_G_total"],
            "native_json2_sha256":native["native_json2_sha256"],
            "generic_G_numeric_reference_usable":True,
            "generic_G_current_season_membership_required":False,
            "full_G_approved":False,
            "source_profile_receipt_sha256":
                native["source_profile_receipt_sha256"],
            "target_ilevel":level,
            "standardized_G_preview_unapproved":native["standardization"]}
        receipt={"identity":identity,"observed_G":observed,
                 "status":"PASS_NATIVE_OBSERVED_G_UNPROMOTED",
                 "returncode":0,"new_native_calls":1,
                 "native_json2_sha256":native["native_json2_sha256"]}
        raw=json.dumps(receipt).encode("utf8")
        (folder/"receipt.json").write_bytes(raw)
        native["native_run_folder"]=str(folder)
        native["native_receipt_sha256"]=hashlib.sha256(raw).hexdigest()
        preflight={
            "schema":build.FRESH_SOURCE_PREFLIGHT_SCHEMA,
            "game_build":self.catalog["game_build"],
            "simc_revision":self.catalog["simc_revision"],
            "source_catalog_manifest_sha256":self.catalog["manifest_sha256"],
            "environment_ready":False,"preflight_sha256":"f"*64}
        candidate,_=build._reuse_v277_G_in_preprofile(
            catalog=self.catalog,target_ilevel=level,
            native_G=native,budget_evidence=None)
        preflight["v277_native_G_preprofile_unadmitted"]=candidate
        compilation={"stage_root":str(self.root),
                     "simc_revision":self.catalog["simc_revision"]}
        staged={"status":"FRESH_SEASON_ENVIRONMENT_STAGED_NOT_INSTALLED",
                "original_v216_preflight_sha256":"f"*64}
        def owner(native_row=native,flight=preflight,stage_row=staged):
            return build._fresh_source_owner_native_G_component(
                native_G=native_row,preflight=flight,
                compilation=compilation,staged=stage_row,
                target_ilevel=level)
        g=owner()
        self.assertEqual(g["rating"],2850)
        self.assertEqual(g["source_verification"],"EXACT_NATIVE")
        self.assertEqual(g["source_sha256"],native["native_json2_sha256"])
        evidence={"components":{"J":{"rating":140},"F":{"rating":170}}}
        merged=build._fresh_source_owner_merge_native_G(
            trusted_budget_evidence=evidence,owner_G=g)
        self.assertEqual(merged["components"]["G"],g)
        self.assertNotIn("G",evidence["components"])
        self.assertEqual(build._fresh_source_owner_merge_native_G(
            trusted_budget_evidence=evidence,owner_G=None),evidence)
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,"PROVIDER_COMPONENT_CONFLICT"):
            build._fresh_source_owner_merge_native_G(
                trusted_budget_evidence={"components":{
                    "G":{**g,"rating":2840}}},
                owner_G=g)
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_NATIVE_G_OWNER_ORIGINAL_SOURCE_SCOPE_REQUIRED"):
            owner(flight={**preflight,"simc_revision":"b"*40})
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_NATIVE_G_OWNER_ORIGINAL_SOURCE_SCOPE_REQUIRED"):
            owner(stage_row={**staged,
                            "original_v216_preflight_sha256":"e"*64})
        (folder/"receipt.json").write_bytes(raw+b" ")
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_NATIVE_G_OWNER_RECEIPT_SHA_DRIFT"):
            owner()
        # An unsealed synthetic preview is never automatically certified.
        self.assertIsNone(owner(native_row={
            **native,"native_run_folder":None}))

    def test_source_owner_no_oil_uses_exact_selection_not_preview(self):
        # P3-EW: original v222 O=0 is valid only for explicit no oil.
        import v222_season_budget_contract as budget
        preflight={
            "schema":build.FRESH_SOURCE_PREFLIGHT_SCHEMA,
            "game_build":self.catalog["game_build"],
            "source_catalog_manifest_sha256":self.catalog["manifest_sha256"],
            "environment_ready":False}
        raw={"components":{"G":{"rating":2800},"J":{"rating":140},
                            "F":{"rating":170}}}
        selected={"flask_item_id":241326,"oil_item_ids_by_hand":{}}
        merged=build._fresh_source_owner_exact_no_oil(
            preflight=preflight,selected_budget_items=selected,
            trusted_budget_evidence=raw)
        exact=budget.explicit_no_oil_component(
            game_build=self.catalog["game_build"],
            source_catalog_manifest_sha256=self.catalog["manifest_sha256"],
            selected_oil_item_ids_by_hand={})
        self.assertEqual(merged["components"]["O"],exact)
        self.assertNotIn("O",raw["components"])
        for choice in (None,{"flask_item_id":241326,
                             "oil_item_ids_by_hand":{"main_hand":243734}}):
            self.assertEqual(
                build._fresh_source_owner_exact_no_oil(
                    preflight=preflight,selected_budget_items=choice,
                    trusted_budget_evidence=raw),raw)
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_SOURCE_OWNER_NO_OIL_PROOF_CONFLICT"):
            build._fresh_source_owner_exact_no_oil(
                preflight=preflight,selected_budget_items=selected,
                trusted_budget_evidence={
                    "components":{**raw["components"],"O":{
                        **exact,"rating":{**exact["rating"],
                                          "crit_rating":1}}}})
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_SOURCE_OWNER_NO_OIL_ORIGINAL_PREFLIGHT_REQUIRED"):
            build._fresh_source_owner_exact_no_oil(
                preflight={**preflight,
                           "source_catalog_manifest_sha256":"wrong"},
                selected_budget_items=selected,
                trusted_budget_evidence=raw)


    def test_p3_fe_original_v217_source_relation_only_merge(self):
        from runner import v220_catalog_auto_admission as policy
        identity={"kind":"permanent_enchant","exact_id":91001,
                  "simc_token":"enchant_boots__source",
                  "slot":"feet","game_build":self.catalog["game_build"],
                  "simc_revision":self.catalog["simc_revision"],
                  "catalog_sha256":self.catalog["manifest_sha256"]}
        proof={"identity":identity,
               "status":"EXACT_SOURCE_RELATION_VERIFIED",
               "evidence_sha256":"1"*64}
        pre={"schema":build.FRESH_SOURCE_PREFLIGHT_SCHEMA,
             "game_build":self.catalog["game_build"],
             "simc_revision":self.catalog["simc_revision"],
             "source_catalog_manifest_sha256":self.catalog["manifest_sha256"],
             "source_artifact_sha256":"a"*64,
             "preflight_sha256":"e"*64,"environment_ready":False,
             "optional_policy_A_evidence_unadmitted":{
                 "v217_source_relation_receipt_count":1,
                 "v217_source_relation_scoped_only":True,
                 "source_catalog_manifest_sha256":
                     self.catalog["manifest_sha256"],
                 "source_catalog_artifact_sha256":"a"*64,
                 "original_v217_source_relation_receipts_internal":{
                     91001:{"source_relation":proof}}}}
        staged={"status":"FRESH_SEASON_ENVIRONMENT_STAGED_NOT_INSTALLED",
                "stage_status":"REUSED_VERIFIED",
                "original_v216_preflight_sha256":"e"*64}
        provider={91001:{"simc_input":{
            "identity":dict(identity),"status":"SIMC_INPUT_ACCEPTED",
            "evidence_sha256":"2"*64}}}
        merge=build._fresh_source_owner_merge_policy_A_original_source_relation
        result=merge(preflight=pre,staged=staged,
                     trusted_policy_A_receipts_by_id=provider)
        self.assertEqual(result[91001]["source_relation"],proof)
        self.assertEqual(set(provider[91001]),{"simc_input"})
        choice={**identity,"slot_status":"SOURCE_MASK_RESOLVED"}
        decision=policy.decide(choice,result[91001])
        self.assertFalse(decision["eligible"])
        self.assertIn("EVIDENCE_MISSING:product_input",decision["missing"])
        self.assertIn("EVIDENCE_MISSING:chmv_budget",decision["missing"])
        self.assertEqual(result,merge(preflight=pre,staged=staged,
                                      trusted_policy_A_receipts_by_id=result))
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_POLICY_A_PROVIDER_SOURCE_RELATION_CONFLICT"):
            merge(preflight=pre,staged=staged,
                  trusted_policy_A_receipts_by_id={
                    91001:{"source_relation":{**proof,
                         "evidence_sha256":"3"*64}}})
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_POLICY_A_ORIGINAL_V217_SEALED_SCOPE_REQUIRED"):
            merge(preflight=pre,staged={**staged,
                    "original_v216_preflight_sha256":"b"*64},
                  trusted_policy_A_receipts_by_id=provider)
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_POLICY_A_V217_ORIGINAL_SOURCE_PROOF_DRIFT"):
            forged=copy.deepcopy(pre)
            forged["optional_policy_A_evidence_unadmitted"][
                "original_v217_source_relation_receipts_internal"][91001][
                    "source_relation"]["identity"]["exact_id"]=99999
            merge(preflight=forged,staged=staged,
                  trusted_policy_A_receipts_by_id=provider)
        empty=copy.deepcopy(pre)
        empty["optional_policy_A_evidence_unadmitted"][
            "original_v217_source_relation_receipts_internal"]={}
        empty["optional_policy_A_evidence_unadmitted"][
            "v217_source_relation_receipt_count"]=0
        self.assertIs(merge(preflight=empty,staged=staged,
                            trusted_policy_A_receipts_by_id=provider),provider)



    def test_p3_fj_intrinsic_v232_roles_stage_exactly_one_special_for_preflight(self):
        # The pure adapter uses only previously sealed source observations.
        # Input gem ROLE IDs are provisional until the original v221 join,
        # so this test does NOT claim the selected item is a real special.
        original={
            "schema":build.simc_representative.SCHEMA,
            "game_build":self.catalog["game_build"],
            "target_ilevel":334,
            "selected_G_slot_ids":{"head":1001,"waist":1002,"wrists":1003},
            "selected_intrinsic_socket_count_by_slot_source_only":{
                "head":1,"waist":0,"wrists":2},
            "environment_ready":False}
        original["receipt_sha256"]=build.simc_source.digest(
            build.simc_source.canonical(original).encode("utf8"))
        path=self.root/"source"/"v232_original.json"
        path.parent.mkdir()
        path.write_text(json.dumps(original),encoding="utf8")
        collected={"expected_game_build":self.catalog["game_build"],
                   "fresh_one_spec_simc_representative":{
                       "status":"FRESH_ONE_SPEC_SIMC_G_SOURCE_CANDIDATE_PENDING_NATIVE",
                       "candidate_path":str(path),
                       "source_stage":{"status":"REUSED_VERIFIED",
                                       "receipt_sha256":"f"*64,
                                       "output_paths":{
                                           "candidate":"source/v232_original.json"}},
                       "selected_slot_count":3,
                       "intrinsic_socket_total_source_only":3,
                       "intrinsic_socket_counts_by_selected_slot_source_only":{
                           "head":1,"waist":0,"wrists":2}}}
        roles={"special_gem_id":311003,
               "ordinary_gem_ids":[311001,311002]}
        fn=build._fresh_default_intrinsic_gem_layout_from_source
        result=fn(collected=collected,selected_roles=roles,target_ilevel=334)
        self.assertEqual(result["socket_counts"],{"head":1,"wrists":2})
        self.assertEqual(result["special_slot"],"head")
        self.assertEqual(result["special_gem_id"],311003)
        self.assertEqual(result["ordinary_gem_ids"],[311001,311002])
        self.assertFalse(result["environment_ready"])
        self.assertFalse(result["CHMV_J_source_authenticated"])
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_DEFAULT_GEM_ORIGINAL_V232_CANDIDATE_IDENTITY_DRIFT"):
            fn(collected=collected,selected_roles=roles,target_ilevel=335)
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "SOCKET_INTRINSIC_SPECIAL_AND_ORDINARY_IDS_REQUIRED"):
            fn(collected=collected,selected_roles={
                "special_gem_id":311003,"ordinary_gem_ids":[311001]},
                target_ilevel=334)
        path.write_text(json.dumps({
            **original,"selected_G_slot_ids":{
                "head":9999,"waist":1002,"wrists":1003}}),encoding="utf8")
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_DEFAULT_GEM_ORIGINAL_V232_CANDIDATE_IDENTITY_DRIFT"):
            fn(collected=collected,selected_roles=roles,target_ilevel=334)

    def test_p3_fm_auto_four_stat_requires_existing_special_and_real_sockets(self):
        # The source-only adapter will refuse any invented 5th socket.
        selected={
            stat:{"item_id":311100+i,"raw_nominal_points":35+i}
            for i,stat in enumerate(build.physical_gems.ORDINARY_FOUR_STATS)}
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "SOCKET_FOUR_ORDINARY_TYPES_NEED_FIVE_PHYSICAL_SOCKETS"):
            build.physical_gems.ordinary_four_stat_default(
                observed_by_stat=selected,socket_total=3,
                special_gem_id=311200,need=build.need)
        self.assertEqual(len(build.physical_gems.ordinary_four_stat_default(
            observed_by_stat=selected,socket_total=5,
            special_gem_id=311200,need=build.need)),4)

    def test_p3_fg_default_web_original_four_budget_without_provider(self):
        # Complete exact sources can form G/J/F/O, but only in the
        # season-wide no OPTIONAL special equipment/enchant or oil.
        # Exactly one special GEM is still mandatory under v271.
        from runner import v222_season_budget_contract as season
        data=self.table[334]
        meta={"schema":build.FRESH_SOURCE_PREFLIGHT_SCHEMA,
              "game_build":self.catalog["game_build"],
              "simc_revision":self.catalog["simc_revision"],
              "source_catalog_manifest_sha256":
                  self.catalog["manifest_sha256"],
              "source_artifact_sha256":
                  data["source_catalog_artifact_sha256"],
              "preflight_sha256":"a"*64,"environment_ready":False}
        staged={"status":"FRESH_SEASON_ENVIRONMENT_STAGED_NOT_INSTALLED",
                "stage_status":"REUSED_VERIFIED",
                "original_v216_preflight_sha256":"a"*64}
        original_G={**data["components"]["G"],
            "rating":2850,"source_verification":"EXACT_NATIVE",
            "standardization":season.standardize_representative_G(
                observed_G_total=2847,target_ilevel=334,
                source_observation_sha256=
                    data["components"]["G"]["source_sha256"])}
        original_J={**data["components"]["J"],
                    "source_verification":"VALID_SAME_SEASON_SOURCE"}
        original_F={**data["components"]["F"],
                    "source_verification":"EXACT_NATIVE",
                    "selected_flask_item_id":241326}
        owners={"J":original_J,"F":original_F}
        selected={"flask_item_id":241326,"oil_item_ids_by_hand":{}}
        make=build._fresh_original_default_base_install_inputs
        out=make(preflight=meta,staged=staged,original_G=original_G,
                 original_J_F=owners,selected_budget_items=selected,
                 target_ilevel=334,user=None)
        self.assertEqual(set(out),{
            "trusted_budget_evidence","trusted_policy_A_receipts_by_id"})
        self.assertEqual(out["trusted_policy_A_receipts_by_id"],{})
        proof=out["trusted_budget_evidence"]
        self.assertEqual(set(proof["components"]),{"G","J","F","O"})
        self.assertEqual(proof["fixed_L"],
                         {k:0 for k in season.STATS})
        self.assertEqual(proof["fixed_E"],
                         {k:0 for k in season.STATS})
        self.assertEqual(proof["components"]["O"]["source_verification"],
                         season.NO_OIL_SOURCE)
        self.assertIsNone(make(
            preflight=meta,staged=staged,original_G=original_G,
            original_J_F=owners,selected_budget_items=selected,
            target_ilevel=334,user={"target":{
                "ilevel":334,"final_T":None}}))
        self.assertIsNone(make(
            preflight=meta,staged=staged,original_G=original_G,
            original_J_F=owners,selected_budget_items={
                "flask_item_id":241326,
                "oil_item_ids_by_hand":{"main_hand":243734}},
            target_ilevel=334,user=None))
        self.assertIsNone(make(
            preflight=meta,staged=staged,original_G=original_G,
            original_J_F={"J":original_J},selected_budget_items=selected,
            target_ilevel=334,user=None))
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_DEFAULT_BASE_SELECTED_FLASK_OR_SOURCE_DRIFT"):
            make(preflight=meta,staged=staged,original_G=original_G,
                 original_J_F=owners,selected_budget_items={
                     "flask_item_id":241327,"oil_item_ids_by_hand":{}},
                 target_ilevel=334,user=None)
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_DEFAULT_BASE_ORIGINAL_STAGE_REQUIRED"):
            make(preflight=meta,staged={**staged,
                  "original_v216_preflight_sha256":"b"*64},
                 original_G=original_G,original_J_F=owners,
                 selected_budget_items=selected,target_ilevel=334,user=None)

    def test_verified_install_provider_connects_same_normal_build(self):
        # Existing v217/v216 source stage is a prerequisite. The internal
        # provider returns None until it has actually verified GJFO.
        old=self.compiled
        self.compiled={**old,
            **{key:{"status":"REUSED_VERIFIED",
                    "receipt_sha256":str(i)*64}
               for i,key in enumerate(
                   ("v191_stage","v211_stage","v213_stage"),1)}}
        staged={"schema":"v212_fresh_source_environment_stage_v1",
                "status":"FRESH_SEASON_ENVIRONMENT_STAGED_NOT_INSTALLED",
                "manifest_sha256":"b"*64,
                "stage_status":"REUSED_VERIFIED",
                "environment_ready":False,
                "environment_installed":False}
        installed={
            "status":"FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY",
            "official_G":2800,"official_J":140,"official_F":170,
            "official_O":{"crit_rating":0,"haste_rating":0,
                          "mastery_rating":0,"versatility_rating":0},
            "official_B":3110,"official_T":3110,
            "environment_ready":True,"environment_installed":True,
            "options_published":True,"published_verified_option_count":0,
            "stage_status":"EXECUTED_AND_SEALED"}
        try:
            with mock.patch.object(build,
                    "_v217_policy_A_source_relation_receipts",
                    return_value={}),mock.patch.object(build,
                    "_stage_source_environment_only",
                    return_value=staged),mock.patch.object(build,
                    "_install_verified_fresh_environment_only",
                    return_value=installed) as installer:
                missing=mock.Mock(return_value=None)
                previous=self.run_build(proof=False,trusted_provider=missing)
                self.assertFalse(previous["zero_history_build"][
                    "environment_ready"])
                installer.assert_not_called()
                supplied={"trusted_budget_evidence":{"components":{}},
                          "trusted_policy_A_receipts_by_id":{}}
                provider=mock.Mock(return_value=supplied)
                # Prove original Build passes a separately verified native-G
                # source-owner result to the existing installer. The owner
                # itself is mocked here; its sealed-proof contract has its
                # own focused regression above, not a synthetic season pass.
                original_G=self.table[334]["components"]["G"]
                with mock.patch.object(
                        build,"_fresh_source_owner_native_G_component",
                        return_value=original_G) as g_owner:
                    result=self.run_build(
                        proof=False,trusted_provider=provider)
                    g_owner.assert_called_once()
                provider.assert_called_once()
                installer.assert_called_once()
                self.assertEqual(installer.call_args.kwargs[
                    "trusted_budget_evidence"],
                    {"components":{"G":original_G}})
                self.assertEqual(result["zero_history_build"]["status"],
                                 installed["status"])
                self.assertTrue(result["environment_ready"])
                self.assertTrue(result["environment_installed"])
                self.assertEqual(result["G"],2800)
                self.assertEqual(result["T"],3110)
                self.assertEqual(result["zero_history_build"]["requires"],[])
                self.assertTrue(result["zero_history_build"][
                    "source_only_pending_before_install"])
        finally:
            self.compiled=old

    def test_verified_install_provider_must_be_internal_callable(self):
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_VERIFIED_INSTALL_PROVIDER_INTERNAL_CALLABLE_REQUIRED"):
            build.build_environment(
                sessions_root=self.root/"sessions",session_folder=None,
                user={"target":{"ilevel":334,"final_T":None}},binary=None,
                revision=None,static_cache=None,source_catalog_path=None,
                bootstrap_result=None,
                fresh_collection_inputs={
                    "expected_game_build":self.catalog["game_build"],
                    "representative_request":{
                        "class":"mage","spec":"frost","target_ilevel":334},
                    "g_probe_character":None,"simc_revision_hint":None,
                    "verified_install_input_provider":{"verified":True}})
        self.assertFalse((self.root/"sessions").exists())

    def test_p3_fb_selected_jf_observed_quality_scope_is_not_admission(self):
        # All quality comparisons are original selected-source projections,
        # not a proof that every season quality or use condition is known.
        layout=self.source_selected_future_gems()
        raw={"status":"ENCHANT_RAW_POINTS_SOURCE_ONLY_J_NOT_APPROVED",
             "enchant_source_sha256":"4"*64,
             "selected_gem_raw_points_by_id_unadmitted":{
                 "311001":20,"311002":30},
             "selected_gem_all_raw_points_known":True,
             "selected_gem_v221_item_ids_unadmitted":[311001,311002,311003],
             "selected_gem_v221_same_build_items_all_present":True,
             "J":None,"environment_ready":False}
        pre=self.preflight_with_sealed_gem_raw(layout,raw)
        link=pre["selected_v221_gem_item_relation_unadmitted"]
        selected=[311001,311002,311003]
        quality_rows=[
            {"item_id":i,"crafting_quality":rank}
            for i,rank in zip(selected,(1,3,2))]
        pre["selected_v221_gem_item_relation_unadmitted"]={
            **link,
            "selected_simc_gem_quality_source_unadmitted":{
                "quality_source_authenticated":True,
                "v230_stage_receipt_sha256":"c"*64,
                "game_build":self.catalog["game_build"],
                "simc_revision":self.catalog["simc_revision"],
                "selected_item_ids":selected,
                "selected_item_quality_unadmitted":quality_rows},
            "gem_policy_A_source_and_quality_unadmitted":{
                "schema":"v216_selected_gem_quality_policy_A_preview_v1",
                "game_build":self.catalog["game_build"],
                "simc_revision":self.catalog["simc_revision"],
                "quality_source_groups_unadmitted":[{
                    "observed_item_ids":[311002,311001],
                    "observed_crafting_quality_ranks":[3,1],
                    "highest_observed_quality_item_id_unadmitted":311002,
                    "same_raw_four_stat_vector_source_only":True,
                    "actual_same_effect_and_use_conditions_verified":False,
                    "all_available_quality_ranks_verified":False}]}}
        numeric,quality=self.selected_physical_pair()
        chosen={"flask_item_id":241326,"oil_item_ids_by_hand":{}}
        linked=build._zero_history_selected_F_O_v222_reconcile(
            selected=chosen,numeric=numeric,choices=quality,
            existing_budget=None,budget_evidence=None)
        compiled={"status":"FRESH_V191_V211_V213_COMPILED_UNADMITTED",
                  "simc_revision":self.catalog["simc_revision"],
                  "selected_physical_F_O_budget_link_unadmitted":linked,
                  "observed_quality_weapon_choices_unadmitted":quality}
        owner=build._fresh_source_owner_selected_J_F_numeric(
            preflight=pre,compilation=compiled,
            selected_physical_items=chosen)
        result=build._fresh_source_owner_observed_J_F_quality(
            preflight=pre,compilation=compiled,owner_numeric=owner)
        self.assertEqual(result["status"],
            "SELECTED_J_F_OBSERVED_QUALITY_BOUND_UNADMITTED")
        self.assertEqual(result["J"][
            "observed_crafting_quality_by_item_id"],{
                "311001":1,"311002":3})
        self.assertEqual(result["J"][
            "same_enchant_quality_groups_source_only"][0][
            "highest_observed_item_id_source_only"],311002)
        self.assertEqual(result["J"]["v230_stage_receipt_sha256"],"c"*64)
        self.assertEqual(result["F"]["selected_item_id"],241326)
        self.assertTrue(result["F"][
            "selected_is_highest_observed_source_only"])
        self.assertTrue(result["F"][
            "discovered_best_effect_accepted_as_quality_policy"])
        self.assertEqual(result["F"][
            "highest_observed_quality_item_id_unadmitted"],241326)
        self.assertFalse(result["highest_available_quality_verified"])
        self.assertFalse(result["same_effect_and_use_conditions_verified"])
        self.assertFalse(result["environment_ready"])
        self.assertEqual(result["new_native_calls"],0)
        broken=copy.deepcopy(pre)
        broken["selected_v221_gem_item_relation_unadmitted"][
            "selected_simc_gem_quality_source_unadmitted"][
                "selected_item_quality_unadmitted"][1]["crafting_quality"]=1
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_JF_QUALITY_ORIGINAL_V220_OBSERVED_RANK_DRIFT"):
            build._fresh_source_owner_observed_J_F_quality(
                preflight=broken,compilation=compiled,owner_numeric=owner)
        damaged=copy.deepcopy(quality)
        damaged["flask_quality_groups_observed_unadmitted"][0][
            "observed_qualities"]=[1]
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_JF_QUALITY_SELECTED_F_ITEM_RANK_DRIFT"):
            build._fresh_source_owner_observed_J_F_quality(
                preflight=pre,
                compilation={**compiled,
                             "observed_quality_weapon_choices_unadmitted":
                                 damaged},
                owner_numeric=owner)
        missing=build._fresh_source_owner_observed_J_F_quality(
            preflight=pre,
            compilation={**compiled,
                         "observed_quality_weapon_choices_unadmitted":None},
            owner_numeric=owner)
        self.assertIsNone(missing["F"])
        self.assertFalse(missing["environment_ready"])
        self.assertIn("F_SELECTED_SIMC_NUMERIC_OR_QUALITY_SOURCE_PENDING",
                      missing["missing"])


    def test_p3_fd_original_J_verified_from_selected_nominal_and_sockets(self):
        # An original same-build v221/v266 J, v230 observed-best quality
        # and original v232 intrinsic counts suffice without Native J.
        layout=self.source_selected_future_gems()
        raw={"status":"ENCHANT_RAW_POINTS_SOURCE_ONLY_J_NOT_APPROVED",
             "enchant_source_sha256":"4"*64,
             "selected_gem_raw_points_by_id_unadmitted":{
                 "311001":20,"311002":30},
             "selected_gem_all_raw_points_known":True,
             "selected_gem_v221_item_ids_unadmitted":[311001,311002,311003],
             "selected_gem_v221_same_build_items_all_present":True,
             "J":None,"environment_ready":False}
        pre=self.preflight_with_sealed_gem_raw(layout,raw)
        compiled={"status":"FRESH_V191_V211_V213_COMPILED_UNADMITTED",
                  "simc_revision":self.catalog["simc_revision"]}
        owner=build._fresh_source_owner_selected_J_F_numeric(
            preflight=pre,compilation=compiled,
            selected_physical_items=None)
        socket={"status":"J_INTRINSIC_COUNTS_BOUND_SOURCE_ONLY",
                "selected_socket_counts":layout["socket_counts"],
                "additional_socket_proof_required_by_slot":{},
                "observed_J_unadmitted":70,
                "v232_stage_receipt_sha256":"9"*64}
        compiled["selected_J_intrinsic_socket_origin_unadmitted"]=socket
        jq={"ordinary_gem_item_ids":list(layout["ordinary_gem_ids"]),
            "v230_stage_receipt_sha256":"c"*64,
            "v221_stage_receipt_sha256":
                owner["J"]["v221_stage_receipt_sha256"],
            "same_enchant_quality_groups_source_only":[{
                "observed_item_ids":[311001,311002],
                "best_discovered_effect_item_id_source_only":311002,
                "comparable_effect_source_only":True}],
            "real_socket_proof_required":True}
        staged={"status":"FRESH_SEASON_ENVIRONMENT_STAGED_NOT_INSTALLED",
                "stage_status":"REUSED_VERIFIED",
                "stage_receipt_sha256":"8"*64}
        # A lower-quality same-family gem may not silently become the
        # official maximum. It remains a user source-only candidate.
        partial=build._fresh_source_owner_original_J_F_components(
            preflight=pre,compilation=compiled,staged=staged,
            owner_numeric=owner,quality_scope={"J":jq},
            effect_observations=[])
        self.assertNotIn("J",partial)
        # A best-discovered comparable family with no lower-ranked
        # selected gem can be used directly as nominal J.
        jq["same_enchant_quality_groups_source_only"]=[]
        result=build._fresh_source_owner_original_J_F_components(
            preflight=pre,compilation=compiled,staged=staged,
            owner_numeric=owner,quality_scope={"J":jq},
            effect_observations=[])
        self.assertEqual(result["J"]["rating"],70)
        self.assertEqual(result["J"]["source_verification"],
                         "VALID_SAME_SEASON_SOURCE")
        self.assertEqual(result["J"]["budget_policy"],
                         "NOMINAL_ORDINARY_GEMS_ONLY")
        merged=build._fresh_source_owner_merge_original_J_F(
            trusted_budget_evidence={"components":{"G":{"rating":2000}}},
            owner_components=result)
        self.assertEqual(merged["components"]["J"],result["J"])
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_JF_OWNER_PROVIDER_J_CONFLICT"):
            build._fresh_source_owner_merge_original_J_F(
                trusted_budget_evidence={"components":{
                    "J":{"rating":71}}},owner_components=result)
        compiled["selected_J_intrinsic_socket_origin_unadmitted"]={
            **socket,"additional_socket_proof_required_by_slot":{"head":1}}
        self.assertEqual(build._fresh_source_owner_original_J_F_components(
            preflight=pre,compilation=compiled,staged=staged,
            owner_numeric=owner,quality_scope={"J":jq},
            effect_observations=[]),{})

    def test_p3_fd_selected_F_requires_original_sealed_native_pair(self):
        # Synthetic receipt bytes emulate the exact v278 pair solely for
        # offline validation. No subprocess or same-season approval claim.
        request,bound,observed=self.physical_effect()
        native=build._zero_history_F_O_native_component_candidates(
            observations=[{**observed,
                "physical_item_native_source_unadmitted":bound}],
            game_build=self.catalog["game_build"],
            simc_revision=self.catalog["simc_revision"])
        selected={"flask_item_id":bound["physical_item_id"],
                  "oil_item_ids_by_hand":{}}
        link=build._zero_history_selected_F_O_v222_reconcile(
            selected=selected,numeric=native,choices={},
            existing_budget=None,budget_evidence=None)
        pre={"schema":build.FRESH_SOURCE_PREFLIGHT_SCHEMA,
             "game_build":self.catalog["game_build"],
             "simc_revision":self.catalog["simc_revision"],
             "source_catalog_manifest_sha256":self.catalog["manifest_sha256"],
             "environment_ready":False}
        compiled={"simc_revision":self.catalog["simc_revision"],
                  "stage_root":str(self.root)}
        staged={"status":"FRESH_SEASON_ENVIRONMENT_STAGED_NOT_INSTALLED",
                "stage_status":"REUSED_VERIFIED",
                "stage_receipt_sha256":"8"*64}
        quality={"F":{"selected_item_id":bound["physical_item_id"],
                      "discovered_best_effect_accepted_as_quality_policy":True}}
        f=link["matched_f"]
        owner={"F":{"rating":f["rating"],
                    "physical_item_id":f["physical_item_id"],
                    "crafting_quality":f["crafting_quality"],
                    "simc_input_token":f["simc_input_token"],
                    "source_candidate_sha256":f["source_candidate_sha256"],
                    "source_identity_sha256":"7"*64,
                    "static_CHMV_vector":f["static_CHMV_vector"],
                    "native_pair_receipt_sha256":f[
                        "simc_native_receipt_sha256"]}}
        # Without real original case paths, even a plausible digest is
        # still NOT a certified F budget.
        self.assertEqual(build._fresh_source_owner_original_J_F_components(
            preflight=pre,compilation=compiled,staged=staged,
            owner_numeric=owner,quality_scope=quality,
            effect_observations=[]),{})
        cases=[]
        for variant,idx in (("baseline",0),("active",1)):
            profile="1"*64 if idx==0 else "2"*64
            folder=self.root/"source"/("v278_"+variant+"_"+"a"*32)
            folder.mkdir(parents=True)
            (folder/"native.json").write_text("{}",encoding="utf8")
            json_sha=build.native_effect_pair.file_sha(folder/"native.json")
            receipt={"schema":build.native_effect_pair.SCHEMA,
                     "status":"NATIVE_JSON2_CAPTURED",
                     "identity":{"variant":variant,
                         "simc_revision":self.catalog["simc_revision"],
                         "binary_sha256":observed["binary_sha256"],
                         "source_profile_sha256":
                             observed["source_profile_sha256"],
                         "profile_sha256":profile,"iterations":1},
                     "native_json2_sha256":json_sha}
            contents=build.canonical(receipt).encode("utf8")+b"\n"
            (folder/"receipt.json").write_bytes(contents)
            cases.append({"variant":variant,
                          "receipt_path":str(folder/"receipt.json"),
                          "receipt_sha256":build.digest(contents)})
        observed["observed"]["baseline_profile_sha256"]="1"*64
        observed["observed"]["active_profile_sha256"]="2"*64
        observed["native_case_receipts"]=cases
        owner["F"]["native_pair_receipt_sha256"]=[
            r["receipt_sha256"] for r in cases]
        fixed=build._fresh_source_owner_original_J_F_components(
            preflight=pre,compilation=compiled,staged=staged,
            owner_numeric=owner,quality_scope=quality,
            effect_observations=[{**observed,
                "physical_item_native_source_unadmitted":bound}])
        self.assertEqual(fixed["F"]["rating"],165)
        self.assertEqual(fixed["F"]["source_verification"],"EXACT_NATIVE")
        self.assertEqual(fixed["F"]["selected_flask_item_id"],241326)
        self.assertEqual(fixed["F"]["simc_input_token"],f["simc_input_token"])
        self.assertEqual(fixed["F"]["crafting_quality"],f["crafting_quality"])
        self.assertEqual(fixed["F"]["static_CHMV_vector"],
                         f["static_CHMV_vector"])
        (self.root/"source"/("v278_active_"+"a"*32)/
            "native.json").write_text("{ }",encoding="utf8")
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "ORIGINAL_NATIVE_JSON2_SHA_DRIFT"):
            build._fresh_source_owner_original_J_F_components(
                preflight=pre,compilation=compiled,staged=staged,
                owner_numeric=owner,quality_scope=quality,
                effect_observations=[{**observed,
                    "physical_item_native_source_unadmitted":bound}])

    def test_p3_fa_original_J_F_source_owner_numeric_and_provider_conflict(self):
        # Reuse v266 sealed ordinary-item points and v281/v278 same-item F.
        # No real Native, implicit admission, or new effect engine.
        layout=self.source_selected_future_gems()
        raw={"status":"ENCHANT_RAW_POINTS_SOURCE_ONLY_J_NOT_APPROVED",
             "enchant_source_sha256":"4"*64,
             "selected_gem_raw_points_by_id_unadmitted":{
                "311001":20,"311002":30},
             "selected_gem_all_raw_points_known":True,
             "selected_gem_v221_item_ids_unadmitted":[311001,311002,311003],
             "selected_gem_v221_same_build_items_all_present":True,
             "J":None,"environment_ready":False}
        pre=self.preflight_with_sealed_gem_raw(layout,raw)
        numeric,_=self.selected_physical_pair()
        chosen={"flask_item_id":241326,"oil_item_ids_by_hand":{}}
        source_link=build._zero_history_selected_F_O_v222_reconcile(
            selected=chosen,numeric=numeric,choices={},
            existing_budget=None,budget_evidence=None)
        compiled={"status":"FRESH_V191_V211_V213_COMPILED_UNADMITTED",
                  "simc_revision":self.catalog["simc_revision"],
                  "selected_physical_F_O_budget_link_unadmitted":source_link}
        owner=build._fresh_source_owner_selected_J_F_numeric(
            preflight=pre,compilation=compiled,
            selected_physical_items=chosen)
        self.assertEqual(owner["status"],
            "SELECTED_J_F_NUMERIC_SOURCES_BOUND_UNADMITTED")
        self.assertEqual(owner["J"]["rating"],70)
        self.assertEqual(owner["J"]["ordinary_gem_item_ids"],
                         [311001,311001,311002])
        self.assertFalse(owner["J"]["special_gem_contributes_to_J"])
        self.assertFalse(owner["J"]["highest_available_quality_verified"])
        self.assertEqual(owner["F"]["rating"],165)
        self.assertEqual(owner["F"]["physical_item_id"],241326)
        self.assertEqual(owner["F"]["crafting_quality"],2)
        self.assertEqual(owner["F"]["native_pair_receipt_sha256"],
                         ["a"*64,"b"*64])
        self.assertFalse(owner["F"]["highest_available_quality_verified"])
        self.assertFalse(owner["environment_ready"])
        self.assertEqual(owner["new_native_calls"],0)
        evidence={"components":{
            "J":{"source_sha256":owner["J"]["source_identity_sha256"],
                 "rating":70},
            "F":{"source_sha256":"f"*64,"rating":165}}}
        self.assertIs(
            build._fresh_source_owner_crosscheck_selected_J_F(
                owner_numeric=owner,trusted_budget_evidence=evidence),
            evidence)
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_JF_OWNER_SAME_SOURCE_NOMINAL_J_CONFLICT"):
            build._fresh_source_owner_crosscheck_selected_J_F(
                owner_numeric=owner,trusted_budget_evidence={
                    "components":{**evidence["components"],"J":{
                        **evidence["components"]["J"],"rating":71}}})
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_JF_OWNER_SELECTED_SIMC_F_NUMBER_CONFLICT"):
            build._fresh_source_owner_crosscheck_selected_J_F(
                owner_numeric=owner,trusted_budget_evidence={
                    "components":{**evidence["components"],"F":{
                        **evidence["components"]["F"],"rating":151}}})
        # An independently authenticated J could legitimately use a
        # different numeric source. Raw v266 is only a candidate.
        other={"components":{"J":{"rating":71,"source_sha256":"e"*64},
                              "F":{"rating":165}}}
        self.assertIs(
            build._fresh_source_owner_crosscheck_selected_J_F(
                owner_numeric=owner,trusted_budget_evidence=other),other)
        pre["physical_gem_raw_rating_by_id_unadmitted"]["311001"]=19
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_JF_OWNER_ORIGINAL_V266_ORDINARY_NUMERIC_DRIFT"):
            build._fresh_source_owner_selected_J_F_numeric(
                preflight=pre,compilation=compiled,
                selected_physical_items=chosen)
        # If selected flask Native was not collected, it stays PENDING.
        pending=build._fresh_source_owner_selected_J_F_numeric(
            preflight={**pre,
              "physical_gem_raw_rating_by_id_unadmitted":{
                  "311001":20,"311002":30}},
            compilation={**compiled,
                "selected_physical_F_O_budget_link_unadmitted":{}},
            selected_physical_items=chosen)
        self.assertIsNone(pending["F"])
        self.assertFalse(pending["environment_ready"])

    def test_p3_ez_F_uses_same_simc_numeric_and_item_origin(self):
        request,bound,observation=self.physical_effect()
        vec={key:0 for key in build.season_budget_contract.STATS}
        vec["haste_rating"]=177
        observation["static_CHMV_candidate"]=dict(vec)
        observation["observed"]["static_CHMV_candidate"]=dict(vec)
        observation["F_candidate_unadmitted"]=177
        native=build._zero_history_F_O_native_component_candidates(
            observations=[{**observation,
                           "physical_item_native_source_unadmitted":bound}],
            game_build=self.catalog["game_build"],
            simc_revision=self.catalog["simc_revision"])
        selected={"flask_item_id":bound["physical_item_id"],
                  "oil_item_ids_by_hand":{}}
        matched=build._zero_history_selected_F_O_v222_reconcile(
            selected=selected,numeric=native,choices={},
            existing_budget=None,budget_evidence=None)
        row=matched["matched_f"]
        self.assertEqual(row["rating"],177)
        self.assertEqual(row["static_CHMV_vector"],vec)
        self.assertEqual(row["crafting_quality"],bound["crafting_quality"])
        self.assertEqual(row["simc_input_token"],bound["simc_input_token"])
        self.assertEqual(row["source_candidate_sha256"],
                         bound["source_candidate_sha256"])
        self.assertEqual(row["F_numeric_source_owner"],
                         "EXISTING_V281_V278_SIMC_DELTA_ONLY")
        self.assertFalse(matched["environment_ready"])
        drift=copy.deepcopy(native)
        drift["flask"][0]["rating_candidate_unadmitted"]=178
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_SELECTED_F_SIMC_NUMBER_OR_EXACT_SOURCE_DRIFT"):
            build._zero_history_selected_F_O_v222_reconcile(
                selected=selected,numeric=drift,choices={},
                existing_budget=None,budget_evidence=None)
        _,_,conditional=self.physical_effect(static=False)
        pending=build._zero_history_F_O_native_component_candidates(
            observations=[{**conditional,
                           "physical_item_native_source_unadmitted":bound}],
            game_build=self.catalog["game_build"],
            simc_revision=self.catalog["simc_revision"])
        unresolved=build._zero_history_selected_F_O_v222_reconcile(
            selected=selected,numeric=pending,choices={},
            existing_budget=None,budget_evidence=None)
        self.assertIsNone(unresolved["matched_f"])
        self.assertIn("SELECTED_FLASK_STATIC_NATIVE_PENDING",
                      unresolved["missing"])

    def test_selected_flask_explicit_no_oil_reconciles_original_manual_T(self):
        request,bound,observed=self.physical_effect()
        original=copy.deepcopy(self.table[334]["components"]["O"])
        try:
            self.table[334]["components"]["O"]["rating"]={
                k:0 for k in build.season_budget_contract.STATS}
            self.table[334]["components"]["O"]["applied_hands"]=[]
            result=self.run_build(
                manual=3300,effect_requests=[request],
                effect_resolver=bound,effect_observation=observed,
                selected_budget_items={
                    "flask_item_id":241326,"oil_item_ids_by_hand":{}})
        finally:
            self.table[334]["components"]["O"]=original
        linked=result["source_compilation"][
            "selected_physical_F_O_budget_link_unadmitted"]
        self.assertTrue(linked["v222_numbers_reconciled"])
        self.assertEqual(linked["matched_f"]["rating"],165)
        self.assertEqual(linked["matched_o_by_hand"],{})
        self.assertEqual(linked["v222_arithmetic_unadmitted"]["final_T"],3300)
        self.assertEqual(linked["v222_arithmetic_unadmitted"]["base_B"],3300)
        self.assertTrue(linked["v222_arithmetic_unadmitted"][
            "manual_final_T_authoritative"])
        self.assertFalse(linked["source_admission_performed_here"])
        self.assertFalse(result["zero_history_build"]["environment_ready"])
        self.assertNotIn("WEAPON_OIL_O_EXACT_APPLICATION_AND_RATING_PENDING",
                         result["zero_history_build"]["requires"])
        self.assertEqual(result["native_calls"],0)

    def selected_physical_pair(self):
        f_request,f_bound,f_obs=self.physical_effect()
        o_request,o_bound,o_obs=self.physical_effect(
            kind="temporary_enchant",hand="main_hand")
        numeric=build._zero_history_F_O_native_component_candidates(
            observations=[
                {**f_obs,"physical_item_native_source_unadmitted":f_bound},
                {**o_obs,"physical_item_native_source_unadmitted":o_bound}],
            game_build=self.catalog["game_build"],
            simc_revision=self.catalog["simc_revision"])
        # The historical v269 snapshot in o_obs was buffed +16/+17.
        # Source-only budget tests must now attach an INDEPENDENT generated
        # stat enchant record (+16/+16) before any O accounting.
        import v296_pinned_oil_static_rating_source as raw_oil
        simc_row=('// spell item enchantments, wow build '+
                  self.catalog["game_build"]+'\n'+
                  '{ 8052, 0, 0, 0, 0, 0, 0, 0, 0, '+
                  '{ 5, 5, 0 }, { 16, 16, 0 }, { 32, 36, 0 }, '+
                  '{ 0, 0, 0 }, 1237006, "Thalassian Phoenix Oil" },\n')
        source=raw_oil.extract(
            generated_text=simc_row,
            game_build=self.catalog["game_build"],
            simc_revision=self.catalog["simc_revision"],
            enchant_ids={8052})
        numeric=raw_oil.project_source_oils(
            source=source,
            worklist={"oil":[{
                "kind":"temporary_enchant",
                "physical_item_id":o_bound["physical_item_id"],
                "selected_hand":o_bound["selected_hand"],
                "simc_input_token":o_bound["simc_input_token"],
                "simc_enchant_id":o_bound["simc_enchant_id"],
                "crafting_quality":o_bound["crafting_quality"],
                "source_candidate_sha256":
                    o_bound["source_candidate_sha256"],
                "source_stage_receipt_sha256":
                    o_bound["source_stage_receipt_sha256"]}]},
            native_numeric=numeric)
        masks=self.existing_oil_mask_fixture()
        choices=build._zero_history_quality_weapon_candidate_join(
            numeric=numeric,weapon_source=masks,
            game_build=self.catalog["game_build"],
            simc_revision=self.catalog["simc_revision"])
        return numeric,choices

    def test_selected_physical_oil_matches_existing_v222_only_once(self):
        numeric,choices=self.selected_physical_pair()
        source=copy.deepcopy(self.table[334])
        source["components"]["O"]["rating"]={
            "crit_rating":16,"haste_rating":16,
            "mastery_rating":0,"versatility_rating":0}
        source["components"]["O"]["applied_hands"]=["main_hand"]
        original=build.season_budget_contract.preprofile_budget(
            source_catalog=self.catalog,source_artifact_sha256="a"*64,
            evidence=source,target_ilevel=334,manual_final_T=3333)
        selected={"flask_item_id":241326,
                  "oil_item_ids_by_hand":{"main_hand":243734}}
        linked=build._zero_history_selected_F_O_v222_reconcile(
            selected=selected,numeric=numeric,choices=choices,
            existing_budget=original,budget_evidence=source)
        self.assertTrue(linked["v222_numbers_reconciled"])
        self.assertEqual(linked["v222_arithmetic_unadmitted"]["fixed_O"][
            "haste_rating"],16)
        self.assertEqual(linked["v222_arithmetic_unadmitted"]["base_B"],3301)
        self.assertEqual(linked["v222_arithmetic_unadmitted"]["final_T"],3333)
        self.assertEqual(linked["matched_o_by_hand"]["main_hand"][
            "representative_weapon_id"],9101)
        self.assertFalse(linked["user_selectable"])

    def test_selected_flask_or_oil_rating_conflict_blocks(self):
        numeric,choices=self.selected_physical_pair()
        source=copy.deepcopy(self.table[334])
        source["components"]["O"]["applied_hands"]=["main_hand"]
        # Only a genuinely DIFFERENT static source is now a conflict.
        # The synthetic standard v222 fixture itself already says 16/16.
        source["components"]["O"]["rating"]["haste_rating"]=15
        original=build.season_budget_contract.preprofile_budget(
            source_catalog=self.catalog,source_artifact_sha256="a"*64,
            evidence=source,target_ilevel=334,manual_final_T=3300)
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "SELECTED_F_O_V222_PHYSICAL_RATING_OR_HANDS_CONFLICT"):
            build._zero_history_selected_F_O_v222_reconcile(
                selected={"flask_item_id":241326,
                          "oil_item_ids_by_hand":{"main_hand":243734}},
                numeric=numeric,choices=choices,
                existing_budget=original,budget_evidence=source)
        changed=dict(original,F=166)
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "SELECTED_F_O_V222_PHYSICAL_RATING_OR_HANDS_CONFLICT"):
            build._zero_history_selected_F_O_v222_reconcile(
                selected={"flask_item_id":241326,
                          "oil_item_ids_by_hand":{}},
                numeric=numeric,choices=choices,
                existing_budget=changed,budget_evidence=source)

    def test_selected_unknown_oil_or_unmatched_shield_remains_pending(self):
        numeric,choices=self.selected_physical_pair()
        selected={"flask_item_id":241326,
                  "oil_item_ids_by_hand":{"off_hand":243734}}
        out=build._zero_history_selected_F_O_v222_reconcile(
            selected=selected,numeric=numeric,choices=choices,
            existing_budget=None,budget_evidence=None)
        self.assertFalse(out["v222_numbers_reconciled"])
        self.assertIn("SELECTED_OIL_OFF_HAND_STATIC_OR_WEAPON_MASK_PENDING",
                      out["missing"])
        self.assertNotIn("off_hand",out["matched_o_by_hand"])
        self.assertFalse(out["environment_ready"])

    def test_selected_physical_budget_bad_input_blocks_before_collector(self):
        with mock.patch.object(build,"collect_wago_new_season_source",
                side_effect=AssertionError("WAGO_MUST_NOT_RUN")):
            with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                         "SELECTED_PHYSICAL_BUDGET_ITEM_FIELDS_INVALID"):
                build.build_environment(
                    sessions_root=self.root/"sessions",session_folder=None,
                    user={"target":{"ilevel":334,"final_T":None}},
                    binary=None,revision=None,static_cache=None,
                    source_catalog_path=None,bootstrap_result=None,
                    fresh_collection_inputs={
                        "expected_game_build":self.catalog["game_build"],
                        "representative_request":{
                            "class":"mage","spec":"frost","target_ilevel":334},
                        "g_probe_character":None,"simc_revision_hint":None,
                        "selected_budget_items":{
                            "flask_item_id":241326,
                            "oil_item_ids_by_hand":{"offhand":243734}}})



    def test_p3_fh_best_observed_same_family_without_full_worklist(self):
        def row(item_id,quality,rating,measured=True):
            vector={k:0 for k in build.season_budget_contract.STATS}
            vector["crit_rating"]=rating
            return {"physical_item_id":item_id,"crafting_quality":quality,
                    "simc_input_token":"test_flask_"+str(quality),
                    "status":("SIMC_NATIVE_STATIC_NUMBER_SOURCE_ONLY"
                              if measured else "SIMC_NATIVE_SOURCE_PENDING"),
                    "rating_candidate_unadmitted":rating if measured else None,
                    "static_CHMV_vector_unadmitted":
                        vector if measured else None}
        numeric={"status":"PHYSICAL_ITEM_SIMC_F_O_CANDIDATES_UNADMITTED",
                 "flask":[row(501,1,180),row(502,2,0,False)],"oil":[]}
        observed=build._zero_history_quality_weapon_candidate_join(
            numeric=numeric,weapon_source={},
            game_build=self.catalog["game_build"],
            simc_revision=self.catalog["simc_revision"])
        group=observed["flask_quality_groups_observed_unadmitted"][0]
        self.assertEqual(group["observed_item_ids"],[501])
        self.assertEqual(group["source_unmeasured_item_ids_unadmitted"],[502])
        self.assertEqual(group["highest_observed_quality_item_id_unadmitted"],501)
        self.assertTrue(group["observed_strongest_effect_sufficient_quality_policy"])
        preflight={"v277_native_G_preprofile_unadmitted":{"status":"source"},
                   "physical_gem_J_arithmetic_unadmitted":{"status":"source"}}
        planned={"status":"MEASURABLE_PHYSICAL_F_O_CANDIDATES_UNADMITTED",
                 "flask":[{"physical_item_id":x["physical_item_id"],
                           "simc_input_token":x["simc_input_token"],
                           "crafting_quality":x["crafting_quality"]}
                          for x in numeric["flask"]]}
        selected=build._source_only_one_flask_budget_preview(
            preflight=preflight,worklist=planned,
            native_numeric={"flask":[numeric["flask"][0]]},
            source_choices=observed)
        self.assertEqual(selected["selected_physical_items_unadmitted"],{
            "flask_item_id":501,"oil_item_ids_by_hand":{}})
        self.assertFalse(selected["environment_ready"])
        waiting=build._source_only_one_flask_budget_preview(
            preflight=preflight,worklist=planned,
            native_numeric={"flask":[]},source_choices=observed)
        self.assertIn("ORIGINAL_OBSERVED_FLASK_SOURCE_PENDING",
                      waiting["requires"])


    def test_p3_fh_auto_flask_only_scope_requires_explicit_none_oil(self):
        # Check rejection happens BEFORE any source/network and does not
        # treat web input as proof. The real selection requires paired F
        # Native evidence after original v281 discovery.
        with mock.patch.object(build,"collect_wago_new_season_source",
                               side_effect=AssertionError("NO_NETWORK")):
            for kwargs in (
                {"auto_select_observed_F_no_oil":True},
                {"auto_select_observed_F_no_oil":True,
                 "auto_native_F_requested":True,
                 "selected_budget_items":{
                     "flask_item_id":241326,"oil_item_ids_by_hand":{}}},
                {"auto_select_observed_F_no_oil":True,
                 "auto_native_F_requested":True,
                 "auto_native_O_requested":True}):
                with self.assertRaisesRegex(
                    build.EnvironmentBuildBlocked,
                    "V216_AUTO_F_NO_OIL_EXPLICIT_SCOPE_REQUIRED"):
                    build.build_environment(
                        sessions_root=self.root/"sessions",
                        session_folder=None,user=None,binary="TEST_NOT_EXECUTED",
                        revision=None,static_cache=None,
                        source_catalog_path=None,bootstrap_result=None,
                        fresh_collection_inputs={
                            "expected_game_build":self.catalog["game_build"],
                            "representative_request":{
                                "class":"mage","spec":"frost",
                                "target_ilevel":334},
                            "g_probe_character":None,
                            "simc_revision_hint":None,
                            **kwargs})

    def test_auto_one_observed_flask_source_only_v222_preview_no_manual_id(self):
        """Full same-build v281 worklist + G/J permits a preview, not READY."""
        layout,ratings=self.physical_layout()
        request,bound,observation=self.physical_effect()
        plan={"status":"MEASURABLE_PHYSICAL_F_O_CANDIDATES_UNADMITTED",
              "flask":[{"physical_item_id":bound["physical_item_id"],
                        "simc_input_token":bound["simc_input_token"],
                        "crafting_quality":bound["crafting_quality"]}],
              "oil":[]}
        with mock.patch.object(build.consumable_simc_relation,
                               "plan_physical_native_measurements",
                               return_value=plan):
            result=self.run_build(
                proof=False,native_result=self.v277_native_G(),
                gem_layout=layout,gem_ratings=ratings,
                effect_requests=[request],effect_resolver=bound,
                effect_observation=observation)
        source=result["source_compilation"]
        chosen=source["auto_observed_flask_budget_preview_unadmitted"]
        self.assertEqual(chosen["status"],
                         "ONE_OBSERVED_FLASK_NO_OIL_NUMERIC_PREVIEW_UNADMITTED")
        self.assertEqual(chosen["selected_physical_items_unadmitted"],
                         {"flask_item_id":241326,"oil_item_ids_by_hand":{}})
        self.assertFalse(chosen["highest_available_quality_verified"])
        self.assertTrue(chosen["oil_zero_is_preview_assumption_only"])
        numeric=source["selected_auto_v222_numeric_preview_unadmitted"]
        self.assertTrue(numeric["oil_zero_is_preview_assumption_only"])
        self.assertNotIn("O_weapon_proof_not_required_reason",
                         numeric["calculation"])
        calc=numeric["calculation"]
        self.assertEqual((calc["reference_G"],calc["J"],calc["F"]),
                         (2850,138,165))
        self.assertEqual((calc["base_B"],calc["final_T"]),(3153,3153))
        self.assertTrue(calc["numeric_preview_only"])
        self.assertFalse(calc["environment_ready"])
        self.assertIsNone(result["F"])
        self.assertIsNone(result["T"])
        self.assertFalse(result["zero_history_build"]["environment_ready"])

    def test_auto_flask_preview_never_guesses_multiple_families_or_missing(self):
        preflight={"v277_native_G_preprofile_unadmitted":{"status":"source"},
                   "physical_gem_J_arithmetic_unadmitted":{"status":"source"}}
        first={"physical_item_id":501,"crafting_quality":2,
               "simc_input_token":"first_flask_2"}
        second={"physical_item_id":502,"crafting_quality":2,
                "simc_input_token":"second_flask_2"}
        plan={"status":"MEASURABLE_PHYSICAL_F_O_CANDIDATES_UNADMITTED",
              "flask":[first,second]}
        observed={"flask":[{**first,
             "status":"SIMC_NATIVE_STATIC_NUMBER_SOURCE_ONLY"}]}
        many=build._source_only_one_flask_budget_preview(
            preflight=preflight,worklist=plan,native_numeric=observed,
            source_choices={"flask_quality_groups_observed_unadmitted":[{
                "status":"ONLY_ONE_QUALITY_OBSERVED",
                "highest_observed_quality_item_id_unadmitted":501,
                "observed_item_ids":[501]}]})
        self.assertIsNone(many["selected_physical_items_unadmitted"])
        self.assertIn("FLASK_EFFECT_FAMILY_NOT_UNAMBIGUOUS",
                      many["requires"])
        observed["flask"].append({**second,
            "status":"SIMC_NATIVE_STATIC_NUMBER_SOURCE_ONLY"})
        ambiguous=build._source_only_one_flask_budget_preview(
            preflight=preflight,worklist=plan,native_numeric=observed,
            source_choices={"flask_quality_groups_observed_unadmitted":[
                {"status":"ONLY_ONE_QUALITY_OBSERVED",
                 "highest_observed_quality_item_id_unadmitted":501,
                 "observed_item_ids":[501]},
                {"status":"ONLY_ONE_QUALITY_OBSERVED",
                 "highest_observed_quality_item_id_unadmitted":502,
                 "observed_item_ids":[502]}]})
        self.assertIsNone(ambiguous["selected_physical_items_unadmitted"])
        self.assertIn("FLASK_EFFECT_FAMILY_NOT_UNAMBIGUOUS",
                      ambiguous["requires"])

    def test_more_than_four_cached_exact_F_rows_do_not_block_v222_source(self):
        _,bound,observation=self.physical_effect()
        items=[]
        for i in range(5):
            this={**observation,
                  "physical_item_native_source_unadmitted":{
                      **bound,"physical_item_id":bound["physical_item_id"]+i}}
            items.append(this)
        out=build._zero_history_F_O_native_component_candidates(
            observations=items,game_build=self.catalog["game_build"],
            simc_revision=self.catalog["simc_revision"])
        self.assertEqual(len(out["flask"]),5)
        self.assertTrue(out["source_only"])
        self.assertIsNone(out["F"])
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_ZERO_HISTORY_FO_OBSERVATION_COUNT_INVALID"):
            build._zero_history_F_O_native_component_candidates(
                observations=items*26,
                game_build=self.catalog["game_build"],
                simc_revision=self.catalog["simc_revision"])

    def test_sealed_v266_v271_GJFO_to_original_v222_without_manual_J(self):
        layout,_=self.physical_layout()
        req,bound,obs=self.physical_effect()
        source_view={
            "status":"ENCHANT_RAW_POINTS_SOURCE_ONLY_J_NOT_APPROVED",
            "enchant_source_sha256":"4"*64,
            "selected_gem_raw_points_by_id_unadmitted":{"240908":24},
            "selected_gem_unresolved_item_ids":[],
            "selected_gem_all_raw_points_known":True,
            "highest_quality_J_verified":False,"J":None,
            "environment_ready":False}
        result=self.run_build(
            proof=False,native_result=self.v277_native_G(),
            gem_layout=layout,gem_ratings=None,
            effect_requests=[req],effect_resolver=bound,
            effect_observation=obs,
            selected_budget_items={"flask_item_id":241326,
                                   "oil_item_ids_by_hand":{}},
            raw_gem_source=source_view)
        stage=result["source_compilation"]
        j=stage["physical_gem_J_arithmetic_unadmitted"]
        self.assertEqual(j["J_candidate_unadmitted"],144)
        self.assertEqual(j["rating_origin"],
                         "V266_RAW_SAME_BUILD_EFFECT_POINTS_ONLY")
        calc=stage["selected_auto_v222_numeric_preview_unadmitted"][
            "calculation"]
        self.assertEqual((calc["reference_G"],calc["J"],calc["F"]),
                         (2850,144,165))
        self.assertEqual((calc["reference_B"],calc["final_T"]),
                         (3159,3159))
        old_identity=build.digest(build.canonical({
            "kind":"physical_gem_layout_and_ratings",
            "items":{"layout":layout,"rating_by_id":{"240908":24}}
        }).encode("utf8"))
        self.assertNotEqual(stage["selected_auto_v222_numeric_preview_unadmitted"][
            "numeric_receipt_identities"]["J_physical_layout_rating_sha256"],
            old_identity)
        self.assertTrue(calc["numeric_preview_only"])
        self.assertFalse(calc["environment_ready"])
        self.assertIsNone(result["J"])
        self.assertIsNone(result["T"])
        self.assertFalse(result["zero_history_build"]["environment_ready"])

    def test_p3_eg_same_season_G_reference_reuses_v222_without_native(self):
        # Simulate no v277 observation: an existing scoped G receipt already
        # reconciled by v222 can drive the SAME source-only numeric preview.
        layout,ratings=self.physical_layout()
        req,bound,observed=self.physical_effect()
        plan={"status":"MEASURABLE_PHYSICAL_F_O_CANDIDATES_UNADMITTED",
              "flask":[{"physical_item_id":bound["physical_item_id"],
                        "simc_input_token":bound["simc_input_token"],
                        "crafting_quality":bound["crafting_quality"]}],
              "oil":[]}
        with mock.patch.object(
                build.consumable_simc_relation,
                "plan_physical_native_measurements",return_value=plan):
            result=self.run_build(
                proof=True,gem_layout=layout,gem_ratings=ratings,
                effect_requests=[req],effect_resolver=bound,
                effect_observation=observed)
        stage=result["source_compilation"]
        self.assertNotIn("v277_native_G_preprofile_unadmitted",stage)
        ref=stage["v222_G_component_reference_unadmitted"]
        self.assertEqual(ref["rating"],2850)
        preview=stage["selected_auto_v222_numeric_preview_unadmitted"]
        self.assertEqual(preview["status"],
                         "SELECTED_GJFO_V222_ARITHMETIC_PREVIEW_UNADMITTED")
        self.assertEqual(preview["calculation"]["reference_G"],2850)
        self.assertEqual(preview["calculation"]["final_T"],3153)
        self.assertEqual(
            preview["numeric_receipt_identities"][
                "G_same_season_reference_source_sha256"],
            ref["source_sha256"])
        self.assertNotIn("G_native_json2_sha256",
                         preview["numeric_receipt_identities"])
        self.assertFalse(preview["source_authenticated"])
        self.assertTrue(preview["oil_zero_is_preview_assumption_only"])
        self.assertNotIn("O_weapon_proof_not_required_reason",
                         preview["calculation"])
        self.assertFalse(preview["environment_ready"])
        self.assertFalse(result["zero_history_build"]["environment_ready"])
        self.assertNotIn("G_NATIVE_RATING_OBSERVATION_PENDING",
                         result["zero_history_build"]["requires"])
        self.assertIn("G_SAME_SEASON_REFERENCE_SOURCE_AUTHENTICATION_PENDING",
                      result["zero_history_build"]["requires"])
        self.assertEqual(result["native_calls"],0)

    def test_p3_eg_unbound_or_drifted_G_source_stays_pending(self):
        known=self.table[334]["components"]["G"]
        calc={"game_build":self.catalog["game_build"],
              "simc_revision":self.catalog["simc_revision"],
              "source_catalog_manifest_sha256":self.catalog["manifest_sha256"],
              "source_catalog_artifact_sha256":"a"*64,
              "target_ilevel":334,"reference_G":known["rating"],
              "source_authentication_performed_here":False}
        basis={"game_build":self.catalog["game_build"],
               "simc_revision":self.catalog["simc_revision"],
               "source_catalog_manifest_sha256":self.catalog["manifest_sha256"],
               "source_artifact_sha256":"a"*64,
               "v222_G_component_reference_unadmitted":known,
               "proposed_budget_arithmetic_unadmitted":calc}
        resolved=build._zero_history_G_numeric_input_from_preflight(
            preflight=basis,target_ilevel=334)
        self.assertEqual(resolved["status"],
                         "V222_SAME_SEASON_REFERENCE_G_NUMERIC_UNADMITTED")
        for edit in (
                {"target_ilevel":335},
                {"reference_G":known["rating"]+10},
                {"source_catalog_artifact_sha256":"f"*64},
                {"source_authentication_performed_here":True},
        ):
            with self.subTest(edit=edit):
                bad={**basis,"proposed_budget_arithmetic_unadmitted":
                    {**calc,**edit}}
                self.assertIsNone(
                    build._zero_history_G_numeric_input_from_preflight(
                        preflight=bad,target_ilevel=334))
        for bad_g in (
                {**known,"game_build":"12.2.0.99999"},
                {**known,"source_verification":"UNADMITTED_NUMERIC_OBSERVATION"},
                {**known,"rating":known["rating"]+10},
                {**known,"source_sha256":"not_sha"},
        ):
            with self.subTest(g=bad_g):
                self.assertIsNone(
                    build._zero_history_G_numeric_input_from_preflight(
                        preflight={**basis,
                            "v222_G_component_reference_unadmitted":bad_g},
                        target_ilevel=334))
        self.assertIsNone(build._zero_history_G_numeric_input_from_preflight(
            preflight={**basis,"v222_G_component_reference_unadmitted":None},
            target_ilevel=334))

    def test_auto_v222_new_season_GJFO_without_manual_budget_evidence(self):
        layout,ratings=self.physical_layout()
        req,bound,obs=self.physical_effect()
        selected={"flask_item_id":241326,"oil_item_ids_by_hand":{}}
        result=self.run_build(
            proof=False,manual=3333,
            native_result=self.v277_native_G(),
            gem_layout=layout,gem_ratings=ratings,
            effect_requests=[req],effect_resolver=bound,
            effect_observation=obs,selected_budget_items=selected)
        auto=result["source_compilation"][
            "selected_auto_v222_numeric_preview_unadmitted"]
        self.assertEqual(auto["status"],
                         "SELECTED_GJFO_V222_ARITHMETIC_PREVIEW_UNADMITTED")
        calc=auto["calculation"]
        self.assertEqual((calc["reference_G"],calc["J"],calc["F"]),
                         (2850,138,165))
        old_j_sha=build.digest(build.canonical({
            "kind":"physical_gem_layout_and_ratings",
            "items":{"layout":layout,"rating_by_id":ratings}
        }).encode("utf8"))
        self.assertEqual(auto["numeric_receipt_identities"][
            "J_physical_layout_rating_sha256"],old_j_sha)
        self.assertEqual((calc["reference_B"],calc["base_B"],calc["final_T"]),
                         (3153,3333,3333))
        self.assertEqual(sum(calc["fixed_O"].values()),0)
        self.assertEqual(calc["O_weapon_proof_not_required_reason"],
                         "NO_APPLIED_OIL_ITEM_OR_WEAPON_HAND")
        self.assertTrue(calc["numeric_preview_only"])
        self.assertTrue(calc["manual_final_T_authoritative"])
        self.assertFalse(auto["environment_ready"])
        self.assertFalse(auto["user_session_created"])
        self.assertIsNone(result["B"])
        self.assertIsNone(result["T"])
        self.assertEqual(result["native_calls"],0)

    def test_auto_v222_selected_phoenix_oil_uses_existing_v286_mask_once(self):
        layout,ratings=self.physical_layout()
        numeric,choices=self.selected_physical_pair()
        g=self.v277_native_G()
        preview_g,_=build._reuse_v277_G_in_preprofile(
            catalog=self.catalog,target_ilevel=334,native_G=g,
            budget_evidence=None)
        gem=build.physical_gems.reconcile_observed_J(
            layout,ratings,build.need)
        preflight={
            "v277_native_G_preprofile_unadmitted":preview_g,
            "physical_gem_J_arithmetic_unadmitted":gem,
            "physical_gem_layout_unadmitted":layout,
            "game_build":self.catalog["game_build"],
            "simc_revision":self.catalog["simc_revision"],
            "source_catalog_manifest_sha256":self.catalog["manifest_sha256"],
            "source_artifact_sha256":"a"*64}
        selected={"flask_item_id":241326,
                  "oil_item_ids_by_hand":{"main_hand":243734}}
        auto=build._zero_history_auto_v222_numeric_preview(
            preflight=preflight,native_numeric=numeric,
            source_choices=choices,selected=selected,
            gem_ratings=ratings,target_ilevel=334,manual_final_T=3333)
        calc=auto["calculation"]
        self.assertEqual((calc["reference_B"],calc["base_B"],calc["final_T"]),
                         (3153,3301,3333))
        self.assertEqual(calc["fixed_O"]["crit_rating"],16)
        self.assertEqual(calc["fixed_O"]["haste_rating"],16)
        self.assertEqual(calc["fixed_O"]["mastery_rating"],0)
        self.assertFalse(calc["environment_ready"])
        self.assertFalse(auto["policy_A_registered"])
        no_oil=build._zero_history_auto_v222_numeric_preview(
            preflight=preflight,native_numeric=numeric,
            source_choices=choices,selected={"flask_item_id":241326,
                                              "oil_item_ids_by_hand":{}},
            gem_ratings=ratings,target_ilevel=334,manual_final_T=None)
        self.assertEqual(no_oil["calculation"]["final_T"],3153)
        self.assertEqual(sum(no_oil["calculation"]["fixed_O"].values()),0)

    def test_auto_v222_incomplete_G_J_or_oil_never_uses_old_defaults(self):
        numeric,choices=self.selected_physical_pair()
        no_source=build._zero_history_auto_v222_numeric_preview(
            preflight=None,native_numeric=numeric,source_choices=choices,
            selected={"flask_item_id":241326,
                      "oil_item_ids_by_hand":{}},
            gem_ratings=None,target_ilevel=334,manual_final_T=None)
        self.assertIsNone(no_source["calculation"])
        self.assertIn("CURRENT_V213_PREFLIGHT_PENDING",
                      no_source["requires"])
        no_gj=build._zero_history_auto_v222_numeric_preview(
            preflight={"game_build":self.catalog["game_build"]},
            native_numeric=numeric,source_choices=choices,
            selected={"flask_item_id":241326,
                      "oil_item_ids_by_hand":{"off_hand":243734}},
            gem_ratings=None,target_ilevel=334,manual_final_T=3300)
        self.assertIsNone(no_gj["calculation"])
        self.assertIn("SAME_SEASON_G_BUDGET_SOURCE_PENDING",no_gj["requires"])
        self.assertIn("V271_PHYSICAL_GEM_J_NUMERIC_PENDING",no_gj["requires"])
        self.assertIn("SELECTED_OIL_OFF_HAND_NATIVE_OR_WEAPON_MASK_PENDING",
                      no_gj["requires"])


    def dynamic_season_profile_inputs(self, *, oil=True, manually=True):
        import v098_target_user_scenario_bootstrap as boot
        fixed={"crit_rating":16,"haste_rating":17,
               "mastery_rating":0,"versatility_rating":0}
        if not oil:
            fixed={k:0 for k in fixed}
        preview={"schema":"v216_zero_history_selected_v222_numeric_preview_v1",
            "status":"SELECTED_GJFO_V222_ARITHMETIC_PREVIEW_UNADMITTED",
            "numeric_preview_only":True,"source_authenticated":False,
            "environment_ready":False,
            "selected_physical_items":{
                "flask_item_id":241326,
                "oil_item_ids_by_hand":{"main_hand":243734} if oil else {}},
            "calculation":{
                "game_build":boot._profile_supplier_registry()["season_build"],
                "simc_revision":"c"*40,"target_ilevel":334,
                "numeric_preview_only":True,
                "source_authentication_performed_here":False,
                "J":143,"F":176,"fixed_O":fixed,
                "base_B":3367 if oil else 3400,
                "final_T":3400,
                "manual_final_T_authoritative":manually}}
        return {"schema":"v098_internal_season_profile_inputs_v1",
                "v216_numeric_preview":preview,
                "flask":{"physical_item_id":241326,
                         "simc_input_token":"flask_of_the_shattered_sun_2",
                         "static_CHMV_vector":{
                             "crit_rating":176,"haste_rating":0,
                             "mastery_rating":0,"versatility_rating":0}},
                "oil_by_hand":{"main_hand":{
                    "physical_item_id":243734,
                    "simc_input_token":"main_hand:thalassian_phoenix_oil",
                    "static_CHMV_vector":{"crit_rating":16,"haste_rating":17,
                         "mastery_rating":0,"versatility_rating":0}}}
                    if oil else {}}

    def test_v098_profile_engine_serializes_variable_j_f_and_o_without_native(self):
        import v098_target_user_scenario_bootstrap as boot
        import v106_user_session_controller as sessions
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            binary=root/"fake_simc"
            binary.write_bytes(b"TEST_OFFLINE_NO_NATIVE")
            folder=root/"unadmitted_preview"
            user=sessions.user_scenario(
                sessions.standard_controls(("mage","frost")))
            user["target"]["final_T"]=3400
            user["oil_hands"]=["main_hand"]
            payload=self.dynamic_season_profile_inputs()
            result=boot.build(user,folder,binary,"c"*40,
                current_season_product=True,
                season_profile_inputs=payload)
            self.assertEqual(result["status"],
                "SEASON_PROFILE_COMPOSED_NOT_ADMITTED_NO_NATIVE")
            self.assertIn("flask=flask_of_the_shattered_sun_2",
                          result["profile_simc"])
            self.assertIn("temporary_enchant=main_hand:thalassian_phoenix_oil",
                          result["profile_simc"])
            self.assertEqual(result["scenario"]["consumables"][
                "gem_budget_J"],143)
            self.assertEqual(result["scenario"]["consumables"][
                "flask_budget_F"],176)
            self.assertEqual(result["scenario"]["consumables"][
                "weapon_temporary_fixed_rating"]["haste_rating"],17)
            self.assertEqual(result["budget_preview_unadmitted"]["final_T"],3400)
            typed=result["v096_typed_input_unadmitted"]
            self.assertEqual(typed["scenario"]["target"]["manual_total"],3367)
            self.assertEqual(typed["scenario"]["target"]["mode"],"manual_total")
            self.assertEqual(typed["flask_F"]["crit_rating"],176)
            self.assertEqual(typed["fixed_O"]["haste_rating"],17)
            self.assertEqual(typed["final_T"],3400)
            self.assertFalse(typed["native_execution_authorized"])
            self.assertFalse(typed["runtime_manifest_created"])
            seeds=typed["adaptive_seed_plan_unadmitted"]
            self.assertEqual(len(seeds["seed_targets_B"]),2)
            self.assertEqual(seeds["base_B"],3367)
            self.assertFalse(seeds["runtime_native_authorized"])
            self.assertTrue(all(sum(x.values())==3367
                                for x in seeds["seed_targets_B"]))
            self.assertNotEqual(seeds["seed_targets_B"][0],
                                seeds["seed_targets_B"][1])
            self.assertFalse(result["environment_ready"])
            self.assertFalse(result["adaptive_v094_started"])
            self.assertEqual(result["new_native_calls"],0)
            self.assertFalse(folder.exists())


    def test_v098_season_preview_never_calls_historical_jf_or_gem_gate(self):
        import v098_target_user_scenario_bootstrap as boot
        import v106_user_session_controller as sessions
        from unittest import mock
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            binary=root/"fake"
            binary.write_bytes(b"OFFLINE")
            user=sessions.user_scenario(
                sessions.standard_controls(("mage","frost")))
            user["target"]["final_T"]=3400
            user["oil_hands"]=["main_hand"]
            with (mock.patch.object(boot.consumer,"apply",
                                   side_effect=AssertionError(
                                       "LEGACY_J_F_MUST_NOT_RUN")),
                 mock.patch.object(boot.common,
                                   "ensure_representative_gem_colors",
                                   side_effect=AssertionError(
                                       "OLD_SEASON_GEM_GATE_MUST_NOT_RUN"))):
                result=boot.build(
                    user,root/"preview",binary,"c"*40,
                    current_season_product=True,
                    season_profile_inputs=self.dynamic_season_profile_inputs())
            self.assertEqual(result["scenario"]["consumables"][
                "gem_budget_J"],143)
            self.assertEqual(result["scenario"]["consumables"][
                "flask_budget_F"],176)
            self.assertFalse((root/"preview").exists())

    def test_v098_source_only_disallows_ignored_user_consumable_overrides(self):
        import v098_target_user_scenario_bootstrap as boot
        import v106_user_session_controller as sessions
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            binary=root/"fake"
            binary.write_bytes(b"OFFLINE")
            user=sessions.user_scenario(
                sessions.standard_controls(("mage","frost")))
            user["consumable_choices"]["food"]="harandar_celebration"
            user["target"]["final_T"]=3400
            with self.assertRaisesRegex(
                boot.UserScenarioBlocked,
                "SEASON_PROFILE_NONDEFAULT_CONSUMABLES_NOT_SOURCE_BOUND"):
                boot.build(user,root/"preview",binary,"c"*40,
                    current_season_product=True,
                    season_profile_inputs=self.dynamic_season_profile_inputs())
            self.assertFalse((root/"preview").exists())

    def test_v098_season_serializer_rejects_mismatched_build_or_oil(self):
        import v098_target_user_scenario_bootstrap as boot
        from tests.test_v091_weapon_oil_external_adapter import frost
        with tempfile.TemporaryDirectory() as td:
            profile,cfg,_=frost(td)
            user={"target":{"ilevel":334,"final_T":3400},
                  "oil_hands":["main_hand"]}
            inp=self.dynamic_season_profile_inputs()
            kwargs={"profile":profile,"cfg":cfg,
                    "weapon_layout":"one_hand_frill","user":user,
                    "season_build":inp["v216_numeric_preview"][
                         "calculation"]["game_build"],
                    "simc_revision":"c"*40}
            good=boot.season_profile_source_only(
                season_profile_inputs=inp,**kwargs)
            self.assertEqual(good["status"],
                "SEASON_PROFILE_COMPOSED_NOT_ADMITTED_NO_NATIVE")
            import copy
            changed=copy.deepcopy(inp)
            changed["oil_by_hand"]["main_hand"][
                "static_CHMV_vector"]["haste_rating"]=16
            with self.assertRaisesRegex(
                (boot.UserScenarioBlocked),"SEASON_PROFILE_FIXED_J_F_O"):
                boot.season_profile_source_only(
                    season_profile_inputs=changed,**kwargs)
            with self.assertRaisesRegex(
                (boot.UserScenarioBlocked),"SEASON_PROFILE_GEAR_BUILD"):
                boot.season_profile_source_only(
                    season_profile_inputs=inp,
                    **{**kwargs,"season_build":"12.2.0.99999"})

    def test_v091_new_oil_by_hand_never_reuses_old_16_16(self):
        from tests.test_v091_weapon_oil_external_adapter import frost
        import v091_weapon_oil_external_adapter as oil_adapter
        with tempfile.TemporaryDirectory() as td:
            p,c,_=frost(td)
            sample=self.dynamic_season_profile_inputs()["oil_by_hand"]
            configured=oil_adapter.configure(
                p,c,"one_hand_frill",["main_hand"],
                season_oil_by_hand=sample)
            self.assertEqual(configured["declared_O"]["crit_rating"],16)
            self.assertEqual(configured["declared_O"]["haste_rating"],17)
            self.assertTrue(configured["internal_season_oil_source_only"])
            self.assertFalse(configured["season_oil_budget_admitted_here"])
            with self.assertRaisesRegex(
                oil_adapter.OilInputBlocked,"SEASON_OIL_PHYSICAL_HAND_SET"):
                oil_adapter.configure(
                    p,c,"one_hand_frill",[],
                    season_oil_by_hand=sample)
            with self.assertRaisesRegex(
                oil_adapter.OilInputBlocked,"NONWEAPON_OFFHAND"):
                oil_adapter.configure(
                    p,c,"one_hand_frill",["off_hand"],
                    season_oil_by_hand={"off_hand":{
                        "physical_item_id":243734,
                        "simc_input_token":
                            "main_hand:disabled/off_hand:thalassian_phoenix_oil",
                        "static_CHMV_vector":
                            sample["main_hand"]["static_CHMV_vector"]}})

    def test_v108_source_only_accepts_new_season_rating_without_legacy_default(self):
        from tests.test_v091_weapon_oil_external_adapter import frost
        import v108_native_consumable_inputs as serializer
        with tempfile.TemporaryDirectory() as td:
            p,c,_=frost(td)
            result=serializer.season_static_consumables_source_only(
                p,c,gem_budget_J=143,flask_budget_F=176,
                flask_item_id=241326,
                flask_simc_token="flask_of_the_shattered_sun_2")
            self.assertEqual(result["scenario"]["consumables"][
                "gem_budget_J"],143)
            self.assertEqual(result["scenario"]["consumables"][
                "flask_budget_F"],176)
            self.assertIn("flask=flask_of_the_shattered_sun_2",
                          result["profile"])
            self.assertFalse(result["environment_ready"])
            with self.assertRaisesRegex(
                serializer.ConsumableBlocked,
                "SEASON_FLASK_SOURCE_PROFILE_SHA_MISMATCH"):
                serializer.season_static_consumables_source_only(
                    p.replace("race=human","race=orc"),c,
                    gem_budget_J=143,flask_budget_F=176,
                    flask_item_id=241326,
                    flask_simc_token="flask_of_the_shattered_sun_2")


    def test_v216_selected_source_flows_into_v098_profile_without_manual_payload(self):
        import v098_target_user_scenario_bootstrap as boot
        from tests.test_v091_weapon_oil_external_adapter import frost
        layout,ratings=self.physical_layout()
        req,bound,obs=self.physical_effect()
        result=self.run_build(
            proof=False,manual=3333,
            native_result=self.v277_native_G(),
            gem_layout=layout,gem_ratings=ratings,
            effect_requests=[req],effect_resolver=bound,
            effect_observation=obs,
            selected_budget_items={
                "flask_item_id":241326,"oil_item_ids_by_hand":{}})
        payload=result["source_compilation"][
            "v098_source_only_profile_inputs_unadmitted"]
        self.assertEqual(payload["flask"]["physical_item_id"],241326)
        self.assertEqual(payload["flask"]["simc_input_token"],"test_flask_2")
        self.assertEqual(payload["flask"]["static_CHMV_vector"]["crit_rating"],165)
        self.assertEqual(payload["oil_by_hand"],{})
        with tempfile.TemporaryDirectory() as td:
            p,c,_=frost(td)
            profile=boot.season_profile_source_only(
                profile=p,cfg=c,weapon_layout="one_hand_frill",
                user={"target":{"ilevel":334,"final_T":3333},
                      "oil_hands":[]},
                season_profile_inputs=payload,
                season_build=self.catalog["game_build"],
                simc_revision=self.catalog["simc_revision"])
            self.assertEqual(profile["status"],
                "SEASON_PROFILE_COMPOSED_NOT_ADMITTED_NO_NATIVE")
            self.assertEqual(profile["scenario"]["consumables"][
                "flask_budget_F"],165)
            self.assertEqual(profile["v096_typed_input_unadmitted"][
                "flask_F"]["crit_rating"],165)
            self.assertIn("flask=test_flask_2",profile["profile_simc"])
            self.assertIn("temporary_enchant=disabled",
                          profile["profile_simc"])
            self.assertFalse(profile["user_session_created"])
            self.assertFalse(profile["environment_ready"])
            self.assertEqual(profile["new_native_calls"],0)

    def test_v216_v098_exact_physical_oil_payload_and_pending_rejected(self):
        numeric,choices=self.selected_physical_pair()
        g=self.v277_native_G()
        preview_g,_=build._reuse_v277_G_in_preprofile(
            catalog=self.catalog,target_ilevel=334,native_G=g,
            budget_evidence=None)
        layout,ratings=self.physical_layout()
        gem=build.physical_gems.reconcile_observed_J(
            layout,ratings,build.need)
        preflight={
            "v277_native_G_preprofile_unadmitted":preview_g,
            "physical_gem_J_arithmetic_unadmitted":gem,
            "physical_gem_layout_unadmitted":layout,
            "game_build":self.catalog["game_build"],
            "simc_revision":self.catalog["simc_revision"],
            "source_catalog_manifest_sha256":self.catalog["manifest_sha256"],
            "source_artifact_sha256":"a"*64}
        selection={"flask_item_id":241326,
                   "oil_item_ids_by_hand":{"main_hand":243734}}
        auto=build._zero_history_auto_v222_numeric_preview(
            preflight=preflight,native_numeric=numeric,
            source_choices=choices,selected=selection,
            gem_ratings=ratings,target_ilevel=334,manual_final_T=3333)
        payload=build._zero_history_v098_profile_source_inputs(
            numeric_preview=auto,physical_sources=numeric)
        self.assertEqual(payload["oil_by_hand"]["main_hand"][
            "static_CHMV_vector"]["haste_rating"],16)
        self.assertEqual(payload["oil_by_hand"]["main_hand"][
            "simc_input_token"],"main_hand:thalassian_phoenix_oil")
        pending={**auto,
            "status":"GJFO_SELECTED_NUMERIC_OBSERVATIONS_PENDING",
            "calculation":None}
        self.assertIsNone(build._zero_history_v098_profile_source_inputs(
            numeric_preview=pending,physical_sources=numeric))


    def test_v098_typed_v096_source_only_input_manual_and_automatic_total(self):
        import v098_target_user_scenario_bootstrap as boot
        from tests.test_v091_weapon_oil_external_adapter import frost
        from copy import deepcopy
        with tempfile.TemporaryDirectory() as td:
            p,c,_=frost(td)
            budget=self.dynamic_season_profile_inputs(oil=False)
            budget["v216_numeric_preview"]["calculation"].update({
                "base_B":3400,"final_T":3400,
                "fixed_O":{k:0 for k in (
                    "crit_rating","haste_rating","mastery_rating",
                    "versatility_rating")},
                "manual_final_T_authoritative":False})
            user={"target":{"ilevel":334,"final_T":None},"oil_hands":[]}
            auto=boot.season_profile_source_only(
                profile=p,cfg=c,user=user,
                weapon_layout="one_hand_frill",
                season_profile_inputs=budget,
                season_build=budget["v216_numeric_preview"][
                    "calculation"]["game_build"],simc_revision="c"*40)
            from runner import v061_scenario_contract as typed_contract
            plan=typed_contract.normalize(
                auto["v096_typed_input_unadmitted"]["scenario"])
            self.assertEqual(plan["budget"]["T"],3400)
            self.assertEqual(sum(plan["budget"][
                "external_temporary_rating"].values()),0)
            self.assertEqual(auto["v096_typed_input_unadmitted"][
                "base_B"],3400)
            self.assertFalse(auto["v096_typed_input_unadmitted"][
                "native_execution_authorized"])
            bad=deepcopy(budget)
            bad["flask"]["static_CHMV_vector"]["crit_rating"]=175
            with self.assertRaisesRegex(
                boot.UserScenarioBlocked,"SEASON_PROFILE_FLASK_NATIVE_VECTOR_SUM_DRIFT"):
                boot.season_profile_source_only(
                    profile=p,cfg=c,user=user,
                    weapon_layout="one_hand_frill",
                    season_profile_inputs=bad,
                    season_build=budget["v216_numeric_preview"][
                        "calculation"]["game_build"],simc_revision="c"*40)

    def test_sealed_v216_to_v096_to_v094_offline_delegation(self):
        import v096_unified_product_entry as entry
        from tests.test_v096_unified_product_entry import V096Unified
        with tempfile.TemporaryDirectory() as td:
            path,raw,receipt=V096Unified().seasonal_fixture(td)
            ready=entry.source(path)
            self.assertEqual(ready["plan"]["budget_source"],
                             "ADMITTED_SEASON_GJFO_V216_V223")
            self.assertEqual(ready["plan"]["final_T"],3183)
            self.assertEqual(ready["context"]["identity"][
                "admitted_season_environment_identity"][
                "environment_build_receipt_sha256"],
                receipt["receipt_sha256"])
            with mock.patch.object(entry.durable,"run",
                    side_effect=RuntimeError("EXISTING_V094_DELEGATED")) as actual:
                with self.assertRaisesRegex(
                        RuntimeError,"EXISTING_V094_DELEGATED"):
                    entry.run_manifest(path,plan_only=False)
            self.assertEqual(actual.call_count,1)
            _,options=actual.call_args
            self.assertEqual(options["native_limit"],4)
            self.assertFalse((path.parent/"output").exists())


    def test_previous_v096_reference_path_still_works_after_seasonal_failure(self):
        from tests.test_v096_unified_product_entry import V096Unified
        # Exercise the existing legacy restore regression in the focused
        # workflow too; v097 covered it at the preceding failing SHA.
        V096Unified().test_seasonal_source_receipt_sha_drift_blocks_and_legacy_unchanged()

    def test_season_execution_is_not_authorized_by_numeric_or_fake_v223_flag(self):
        import v096_unified_product_entry as entry
        import v216_environment_build_coordinator as original
        from tests.test_v096_unified_product_entry import V096Unified
        with tempfile.TemporaryDirectory() as td:
            path,user,receipt=V096Unified().seasonal_fixture(td)
            receipt["season_budget"]["source_links_verified_by_v223"]=False
            receipt["receipt_sha256"]=original.digest(original.canonical(
                {k:v for k,v in receipt.items()
                 if k!="receipt_sha256"}).encode("utf8"))
            (path.parent/"environment_build_receipt.json").write_text(
                json.dumps(receipt),encoding="utf8")
            user[entry.SEASON_FIELD]["environment_receipt_sha256"]=(
                receipt["receipt_sha256"])
            path.write_text(json.dumps(user),encoding="utf8")
            with mock.patch.object(entry.durable,"run",
                side_effect=AssertionError("V094_MUST_NOT_RUN")) as actual:
                with self.assertRaisesRegex(
                        entry.EntryBlocked,
                        "SEASON_V223_ACTUAL_SOURCE_LINKS_NOT_VERIFIED"):
                    entry.run_manifest(path,plan_only=False)
                self.assertEqual(actual.call_count,0)
            self.assertFalse((path.parent/"output").exists())


    def admitted_v216_receipt_for_source_only_v098(self, td, season_payload):
        import v216_environment_build_coordinator as env
        from tests.test_v096_unified_product_entry import V096Unified
        path,_,receipt=V096Unified().seasonal_fixture(td)
        budget=season_payload["v216_numeric_preview"]["calculation"]
        target=path.parent/"environment_build_receipt.json"
        b=receipt["season_budget"]
        for key in ("game_build","simc_revision","target_ilevel",
                    "base_B","final_T","J","F","fixed_O"):
            b[key]=copy.deepcopy(budget[key])
        receipt["source"]["game_build"]=budget["game_build"]
        receipt["source"]["simc_revision"]=budget["simc_revision"]
        season_payload["v216_numeric_preview"]["calculation"].update({
            "source_catalog_manifest_sha256":
                receipt["source"]["manifest_sha256"],
            "source_catalog_artifact_sha256":
                receipt["source"]["artifact_sha256"]})
        receipt["receipt_sha256"]=env.digest(env.canonical({
            k:v for k,v in receipt.items() if k!="receipt_sha256"
        }).encode("utf8"))
        target.write_text(json.dumps(receipt),encoding="utf8")
        return target

    def test_v098_automatically_writes_admitted_v096_manifest_and_reuses_v094(self):
        import v098_target_user_scenario_bootstrap as boot
        import v096_unified_product_entry as entry
        import v106_user_session_controller as sessions
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            user=sessions.user_scenario(
                sessions.standard_controls(("mage","frost")))
            user["target"]["final_T"]=3400
            user["oil_hands"]=["main_hand"]
            payload=self.dynamic_season_profile_inputs()
            proof=self.admitted_v216_receipt_for_source_only_v098(td,payload)
            binary=root/"fake_simc"
            binary.write_bytes(b"OFFLINE_NO_NATIVE")
            folder=root/"auto_session"
            result=boot.build(
                user,folder,binary,"c"*40,current_season_product=True,
                season_profile_inputs=payload,
                season_environment_receipt_path=proof)
            self.assertEqual(result["status"],
                "READY_SOURCE_BOUND_SEASON_MANIFEST_ZERO_NATIVE")
            self.assertEqual(result["plan"]["budget_source"],
                             "ADMITTED_SEASON_GJFO_V216_V223")
            self.assertEqual(result["plan"]["base_B"],3367)
            self.assertEqual(result["plan"]["final_T"],3400)
            self.assertEqual(result["plan"]["fixed_O"]["haste_rating"],17)
            self.assertTrue((folder/"manifest.json").is_file())
            self.assertFalse((folder/"simc_results").exists())
            self.assertEqual(entry.run_manifest(
                result["generated_manifest"],plan_only=True),result["plan"])
            with mock.patch.object(entry.durable,"run",
                      side_effect=RuntimeError("EXISTING_V094_REUSED")) as actual:
                with self.assertRaisesRegex(
                        RuntimeError,"EXISTING_V094_REUSED"):
                    entry.run_manifest(result["generated_manifest"])
                self.assertEqual(actual.call_count,1)
            self.assertFalse((folder/"simc_results").exists())
            replay=boot.build(
                user,folder,binary,"c"*40,current_season_product=True,
                season_profile_inputs=payload,
                season_environment_receipt_path=proof)
            self.assertEqual(replay["generated_manifest"],
                             result["generated_manifest"])
            self.assertEqual(replay["plan"],result["plan"])

    def test_v098_unadmitted_source_never_writes_any_session(self):
        import v098_target_user_scenario_bootstrap as boot
        import v106_user_session_controller as sessions
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            user=sessions.user_scenario(
                sessions.standard_controls(("mage","frost")))
            user["target"]["final_T"]=3400
            user["oil_hands"]=["main_hand"]
            payload=self.dynamic_season_profile_inputs()
            proof=self.admitted_v216_receipt_for_source_only_v098(td,payload)
            payload["v216_numeric_preview"]["calculation"][
                "source_catalog_manifest_sha256"]="f"*64
            binary=root/"fake_simc"
            binary.write_bytes(b"OFFLINE")
            dest=root/"must_not_create"
            with self.assertRaisesRegex(
                    boot.UserScenarioBlocked,
                    "SEASON_WRITER_V216_V098_SOURCE_ACCOUNTING_DRIFT"):
                boot.build(user,dest,binary,"c"*40,
                    current_season_product=True,
                    season_profile_inputs=payload,
                    season_environment_receipt_path=proof)
            self.assertFalse(dest.exists())


    def test_v098_season_receipt_change_cannot_overwrite_sealed_session(self):
        import v098_target_user_scenario_bootstrap as boot
        import v106_user_session_controller as sessions
        import v216_environment_build_coordinator as env
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            user=sessions.user_scenario(
                sessions.standard_controls(("mage","frost")))
            user["target"]["final_T"]=3400
            user["oil_hands"]=["main_hand"]
            payload=self.dynamic_season_profile_inputs()
            receipt_path=self.admitted_v216_receipt_for_source_only_v098(
                td,payload)
            binary=root/"fake_simc"
            binary.write_bytes(b"OFFLINE")
            folder=root/"session"
            first=boot.build(
                user,folder,binary,"c"*40,current_season_product=True,
                season_profile_inputs=payload,
                season_environment_receipt_path=receipt_path)
            original={
                x.name:x.read_bytes() for x in
                (folder/"profile.simc",folder/"scenario.json",
                 folder/"fillers.json",folder/"manifest.json")}
            altered=json.loads(receipt_path.read_text("utf8"))
            altered["season_budget"]["source_input_sha256"]["gear"]="9"*64
            altered["receipt_sha256"]=env.digest(env.canonical({
                k:v for k,v in altered.items()
                if k!="receipt_sha256"}).encode("utf8"))
            replacement=root/"different_source_receipt.json"
            replacement.write_text(json.dumps(altered),encoding="utf8")
            with self.assertRaisesRegex(
                    boot.UserScenarioBlocked,
                    "SEASON_WRITER_EXISTING_SESSION_SOURCE_CHANGED:manifest.json"):
                boot.build(user,folder,binary,"c"*40,
                    current_season_product=True,
                    season_profile_inputs=payload,
                    season_environment_receipt_path=replacement)
            self.assertEqual(original,{
                x.name:x.read_bytes() for x in
                (folder/"profile.simc",folder/"scenario.json",
                 folder/"fillers.json",folder/"manifest.json")})
            self.assertFalse((folder/"simc_results").exists())


    def synthetic_future_season_source_bundle(self):
        import v169_source_first_representative_stage as source_first
        import v139_pure_target_profile_composer as pure
        db=copy.deepcopy(source_first.gear.read())
        tier=copy.deepcopy(source_first.load_tier())
        settings=copy.deepcopy(pure.catalog())
        budget=json.loads(
            source_first.BUDGET_PATH.read_text(encoding="utf8"))
        # Synthetic fixture only. Never cite these changed build/item IDs
        # as facts about an actual World of Warcraft future season.
        build="12.2.0.99999"
        db["season_build"]=build
        tier["retail_build"]=build
        budget["retail_build"]=build
        settings["season"]="synthetic_future_only_not_game_data"
        settings["gems"]["head"]="250999"
        settings["default_consumables"]["gem_budget_J"]=143
        settings["default_consumables"]["flask_budget_F"]=176
        budget["ordinary_gem"]["total_J"]=143
        budget["flasks"]["total_F"]=176
        return {"schema":"v098_internal_season_source_bundle_v1",
                "gear":db,"tier":tier,
                "budget":budget,"settings":settings}

    def test_future_season_document_swap_composes_source_only_without_old_diamond(self):
        import v169_source_first_representative_stage as source_first
        import v139_pure_target_profile_composer as pure
        import v098_target_user_scenario_bootstrap as boot
        import v106_user_session_controller as sessions
        doc=self.synthetic_future_season_source_bundle()
        args={k:doc[k] for k in ("gear","tier","settings")}
        args["db"]=args.pop("gear")
        with self.assertRaisesRegex(source_first.RepresentativeBlocked,
                                     "P1_J_F_BUDGET_NOT_ALIGNED"):
            source_first.season_scope(**args)
        scope=source_first.season_scope(
            **args,budget=doc["budget"])
        self.assertEqual(len(scope["specializations"]),26)
        user=sessions.user_scenario(
            sessions.standard_controls(("mage","frost")))
        payload=self.dynamic_season_profile_inputs()
        payload["v216_numeric_preview"]["calculation"][
            "game_build"]=doc["gear"]["season_build"]
        user["target"]["final_T"]=3400
        user["oil_hands"]=["main_hand"]
        with tempfile.TemporaryDirectory() as td:
            from pathlib import Path
            root=Path(td)
            binary=root/"fake_simc"
            binary.write_bytes(b"NO_NATIVE_SYNTHETIC_FUTURE")
            # With ordinary default mode, even a valid synthetic season
            # scope cannot bypass the original legacy diamond semantics.
            with self.assertRaisesRegex(pure.ProfileStageBlocked,
                                        "STAGED_PRIMARY_DIAMOND_REQUIRED"):
                pure.v098_inputs(
                    user["character"],user["trinkets"],
                    season_override=scope)
            result=boot.build(
                user,root/"preview",binary,"c"*40,
                current_season_product=True,
                season_source_bundle=doc,
                season_profile_inputs=payload)
            self.assertEqual(result["status"],
                             "SEASON_PROFILE_COMPOSED_NOT_ADMITTED_NO_NATIVE")
            self.assertIn("gem_id=250999",result["profile_simc"])
            self.assertEqual(result["same_season_build"],
                             "12.2.0.99999")
            self.assertEqual(result["v096_typed_input_unadmitted"][
                             "base_B"],3367)
            self.assertFalse(result["environment_ready"])
            self.assertFalse((root/"preview").exists())

    def test_future_season_document_swap_rejects_cross_build_or_budget(self):
        import v098_target_user_scenario_bootstrap as boot
        import v106_user_session_controller as sessions
        import v169_source_first_representative_stage as source_first
        doc=self.synthetic_future_season_source_bundle()
        mismatched=copy.deepcopy(doc)
        mismatched["tier"]["retail_build"]="12.3.0.99999"
        with self.assertRaisesRegex(source_first.RepresentativeBlocked,
                                     "GEAR_TIER_BUILD_MISMATCH"):
            source_first.season_scope(
                db=mismatched["gear"],tier=mismatched["tier"],
                settings=mismatched["settings"],
                budget=mismatched["budget"])
        bad_budget=copy.deepcopy(doc)
        bad_budget["budget"]["flasks"]["total_F"]=165
        with self.assertRaisesRegex(source_first.RepresentativeBlocked,
                                     "P1_J_F_BUDGET_NOT_ALIGNED"):
            source_first.season_scope(
                db=bad_budget["gear"],tier=bad_budget["tier"],
                settings=bad_budget["settings"],
                budget=bad_budget["budget"])
        user=sessions.user_scenario(
            sessions.standard_controls(("mage","frost")))
        user["target"]["final_T"]=3400
        user["oil_hands"]=["main_hand"]
        payload=self.dynamic_season_profile_inputs()
        with tempfile.TemporaryDirectory() as td:
            from pathlib import Path
            root=Path(td);binary=root/"fake"
            binary.write_bytes(b"OFFLINE")
            with self.assertRaisesRegex(
                     boot.UserScenarioBlocked,
                     "SEASON_SOURCE_BUNDLE_V216_BUILD_OR_TARGET_DRIFT"):
                boot.build(user,root/"no_write",binary,"c"*40,
                    current_season_product=True,
                    season_source_bundle=doc,
                    season_profile_inputs=payload)
            self.assertFalse((root/"no_write").exists())


    def test_future_season_bundle_is_preview_only_even_with_old_receipt(self):
        import v098_target_user_scenario_bootstrap as boot
        import v106_user_session_controller as sessions
        user=sessions.user_scenario(
            sessions.standard_controls(("mage","frost")))
        user["target"]["final_T"]=3400
        user["oil_hands"]=["main_hand"]
        source=self.synthetic_future_season_source_bundle()
        payload=self.dynamic_season_profile_inputs()
        payload["v216_numeric_preview"]["calculation"][
            "game_build"]=source["gear"]["season_build"]
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            binary=root/"fake"
            binary.write_bytes(b"NO_NATIVE")
            with self.assertRaisesRegex(
                    boot.UserScenarioBlocked,
                    "SEASON_SOURCE_BUNDLE_ORIGINAL_GEAR_TIER_SHA_ADMISSION_PENDING"):
                boot.build(
                    user,root/"blocked",binary,"c"*40,
                    current_season_product=True,
                    season_profile_inputs=payload,
                    season_source_bundle=source,
                    season_environment_receipt_path=root/"synthetic_receipt.json")
            self.assertFalse((root/"blocked").exists())
    def test_p3_dg_original_raw_sha_links_only_to_preview(self):
        import hashlib
        from unittest import mock
        import v098_target_user_scenario_bootstrap as boot
        import v106_user_session_controller as sessions
        doc=self.synthetic_future_season_source_bundle()
        user=sessions.user_scenario(sessions.standard_controls(("mage","frost")))
        user["target"]["final_T"]=3400
        user["oil_hands"]=["main_hand"]
        numeric=self.dynamic_season_profile_inputs()
        numeric["v216_numeric_preview"]["calculation"]["game_build"]=(
            doc["gear"]["season_build"])
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            (root/"fresh_source").mkdir()
            (root/"sources").mkdir()
            paths={"catalog":root/"fresh_source"/"v213_candidate_catalog.json",
                   "gear":root/"sources"/"gear.json",
                   "tier":root/"sources"/"tier.json"}
            for k in ("gear","tier"):
                paths[k].write_text(json.dumps(doc[k],sort_keys=True),
                                    encoding="utf8")
            sha={k:hashlib.sha256(paths[k].read_bytes()).hexdigest()
                 for k in ("gear","tier")}
            catalog={"game_build":doc["gear"]["season_build"],
                     "simc_revision":"c"*40,"manifest_sha256":"a"*64,
                     "source_provenance":{"v191":{"sha256_by_input":
                         {**sha,"budget":None}}}}
            paths["catalog"].write_text(json.dumps(catalog),encoding="utf8")
            originals={k:str(v) for k,v in paths.items()}
            binary=root/"fake";binary.write_bytes(b"OFFLINE_NO_NATIVE")
            # v213's original source validator is tested separately;
            # here test exact raw-byte binding against its verified identity.
            with mock.patch.object(boot.original_catalog,"verify_catalog",
                                   return_value=True):
                preview=boot.build(user,root/"preview",binary,"c"*40,
                    current_season_product=True,season_source_bundle=doc,
                    season_profile_inputs=numeric,
                    season_original_source_paths=originals)
                self.assertEqual(preview["status"],
                    "SEASON_PROFILE_COMPOSED_NOT_ADMITTED_NO_NATIVE")
                link=preview["original_v191_gear_tier_source_unadmitted"]
                self.assertEqual(link["raw_source_sha256"],sha)
                self.assertFalse(link["native_authorized"])
                self.assertFalse((root/"preview").exists())
                changed=copy.deepcopy(doc)
                changed["tier"]["classes"]={}
                with self.assertRaisesRegex(boot.UserScenarioBlocked,
                    "SEASON_V191_TIER_RAW_SHA_OR_BYTES_DRIFT"):
                    boot._v191_raw_gear_tier_link(changed,originals,"c"*40)
                paths["gear"].write_text(paths["gear"].read_text("utf8")+" ",
                                         encoding="utf8")
                with self.assertRaisesRegex(boot.UserScenarioBlocked,
                    "SEASON_V191_GEAR_RAW_SHA_OR_BYTES_DRIFT"):
                    boot._v191_raw_gear_tier_link(doc,originals,"c"*40)
                # Even a fully matched raw source cannot authorize v096
                # when v216/v223 actual NEW-season GJFO is not admitted.
                paths["gear"].write_text(json.dumps(doc["gear"],sort_keys=True),
                                         encoding="utf8")
                with self.assertRaisesRegex(boot.UserScenarioBlocked,
                    "SEASON_SOURCE_BUNDLE_ORIGINAL_GEAR_TIER_SHA_ADMISSION_PENDING"):
                    boot.build(user,root/"blocked",binary,"c"*40,
                        current_season_product=True,season_source_bundle=doc,
                        season_profile_inputs=numeric,
                        season_original_source_paths=originals,
                        season_environment_receipt_path=root/"old.json")
                self.assertFalse((root/"blocked").exists())

    def test_p3_dh_one_call_v216_to_v098_uses_original_gear_and_v222_j_f(self):
        import hashlib
        import v098_target_user_scenario_bootstrap as boot
        import v106_user_session_controller as sessions
        doc=self.synthetic_future_season_source_bundle()
        user=sessions.user_scenario(
            sessions.standard_controls(("mage","frost")))
        user["target"]["final_T"]=3400
        user["oil_hands"]=["main_hand"]
        payload=self.dynamic_season_profile_inputs()
        payload["v216_numeric_preview"]["calculation"]["game_build"]=(
            doc["gear"]["season_build"])
        with tempfile.TemporaryDirectory() as temp:
            root=pathlib.Path(temp)
            (root/"fresh_source").mkdir()
            (root/"inputs").mkdir()
            paths={"catalog":root/"fresh_source"/"v213_candidate_catalog.json",
                   "gear":root/"inputs"/"gear.json",
                   "tier":root/"inputs"/"tier.json"}
            for name in ("gear","tier"):
                paths[name].write_text(json.dumps(doc[name],sort_keys=True),
                                       encoding="utf8")
            source_sha={name:hashlib.sha256(
                paths[name].read_bytes()).hexdigest()
                for name in ("gear","tier")}
            catalog={"game_build":doc["gear"]["season_build"],
                     "simc_revision":"c"*40,"manifest_sha256":"d"*64,
                     "source_provenance":{"v191":{
                         "sha256_by_input":{**source_sha,"budget":None}}}}
            paths["catalog"].write_text(json.dumps(catalog),encoding="utf8")
            calc=payload["v216_numeric_preview"]["calculation"]
            calc["source_catalog_manifest_sha256"]=catalog["manifest_sha256"]
            calc["source_catalog_artifact_sha256"]=hashlib.sha256(
                paths["catalog"].read_bytes()).hexdigest()
            originals={name:str(path) for name,path in paths.items()}
            env={"normal_build_entry":True,
                 "zero_history_build":{"environment_ready":False},
                 "source_compilation":{
                    "status":"FRESH_V191_V211_V213_COMPILED_UNADMITTED",
                    "source_catalog_path":str(paths["catalog"]),
                    "v191_original_gear_tier_source_paths":originals,
                    "v098_source_only_profile_inputs_unadmitted":payload,
                    "simc_revision":"c"*40,
                    "preflight_sha256":"e"*64}}
            binary=root/"fake";binary.write_bytes(b"NO_NATIVE_NO_NETWORK")
            with mock.patch.object(boot.original_catalog,"verify_catalog",
                                   return_value=True):
                result=boot.preview_from_environment_build(
                    user,root/"preview",binary,"c"*40,
                    environment_result=env,season_settings=doc["settings"])
                self.assertEqual(result["status"],
                    "SEASON_PROFILE_COMPOSED_NOT_ADMITTED_NO_NATIVE")
                self.assertTrue(result[
                    "v216_to_v098_auto_source_linked_preview"])
                self.assertEqual(result["budget_preview_unadmitted"]["J"],143)
                self.assertEqual(result["budget_preview_unadmitted"]["F"],176)
                self.assertEqual(result["v096_typed_input_unadmitted"][
                    "base_B"],3367)
                self.assertEqual(result["original_v191_gear_tier_source_unadmitted"][
                    "raw_source_sha256"],source_sha)
                self.assertEqual(result["v216_preflight_sha256"],"e"*64)
                self.assertFalse(result["season_settings_source_admitted_here"])
                # Reconstruct the v139 season gems from ORIGINAL v271
                # physical slots, and the flask stat from original v278.
                # No legacy v144 numeric/default choices are copied.
                defaults=doc["settings"]["default_consumables"]
                controls={
                    "food":defaults["food"],"potion":defaults["potion"],
                    "augmentation":defaults["augmentation"],
                    "omnium_talents":None}
                waiting=boot.preview_from_environment_build(
                    user,root/"gem_pending",binary,"c"*40,
                    environment_result=env,season_controls=controls)
                self.assertEqual(waiting["status"],
                    "V216_TO_V098_SOURCE_PROFILE_PENDING")
                self.assertIn("V271_SELECTED_PHYSICAL_GEM_LAYOUT_AND_J_PENDING",
                              waiting["missing"])
                self.assertFalse((root/"gem_pending").exists())
                layout,_=self.physical_layout()
                env["source_compilation"]["physical_gem_layout_unadmitted"]=layout
                env["source_compilation"][
                    "physical_gem_J_arithmetic_unadmitted"]={
                    "status":"PHYSICAL_GEM_J_ARITHMETIC_UNADMITTED",
                    "physical_gem_item_ids":list(layout["ordinary_gem_ids"]),
                    "J_candidate_unadmitted":143}
                derived=boot.preview_from_environment_build(
                    user,root/"derived",binary,"c"*40,
                    environment_result=env,season_controls=controls)
                self.assertEqual(derived["status"],
                    "SEASON_PROFILE_COMPOSED_NOT_ADMITTED_NO_NATIVE")
                self.assertTrue(derived[
                    "season_settings_physical_gem_flask_assembled_unadmitted"])
                self.assertIn("gem_id=240967",
                              derived["profile_simc"])
                self.assertIn("gem_id=240908/240908",
                              derived["profile_simc"])
                self.assertNotIn("omnium_talents=",
                                 derived["profile_simc"])
                self.assertNotIn("\nlevel=", "\n"+derived["profile_simc"])
                self.assertEqual(derived["scenario"]["consumables"]["food"],
                                 defaults["food"])
                # Without a season-specific optional choice, the real
                # source-only Build is still allowed to compose GJFO.
                automatic=boot.preview_from_environment_build(
                    user,root/"optional_off",binary,"c"*40,
                    environment_result=env)
                self.assertEqual(automatic["status"],
                    "SEASON_PROFILE_COMPOSED_NOT_ADMITTED_NO_NATIVE")
                self.assertIn("\nfood=disabled\n", "\n"+automatic["profile_simc"])
                self.assertIn("\npotion=disabled\n", "\n"+automatic["profile_simc"])
                self.assertIn("\naugmentation=disabled\n",
                              "\n"+automatic["profile_simc"])
                self.assertNotIn("omnium_talents=",automatic["profile_simc"])
                self.assertNotIn("\nlevel=", "\n"+automatic["profile_simc"])
                self.assertEqual(automatic["new_native_calls"],0)
                self.assertFalse((root/"optional_off").exists())
                self.assertFalse(derived[
                    "optional_omnium_module_active_in_profile"])
                self.assertEqual(derived["scenario"]["consumables"][
                    "gem_budget_J"],143)
                self.assertEqual(derived["scenario"]["consumables"][
                    "flask_budget_F"],176)
                self.assertEqual(derived["new_native_calls"],0)
                self.assertFalse((root/"derived").exists())
                # P3-DK: use the EXISTING v271/v139 variable socket
                # compositor end-to-end, including special gem on wrist,
                # not the original 6+head season template.
                variable=copy.deepcopy(layout)
                variable["socket_counts"]={"wrists":1,"waist":2,"feet":2}
                variable["socket_total"]=5
                variable["ordinary_count"]=4
                variable["ordinary_gem_ids"]=[240908]*4
                variable["special_gem_id"]=240983
                variable["special_slot"]="wrists"
                calc["J"]=92
                env["source_compilation"][
                    "physical_gem_layout_unadmitted"]=variable
                env["source_compilation"][
                    "physical_gem_J_arithmetic_unadmitted"]={
                        "status":"PHYSICAL_GEM_J_ARITHMETIC_UNADMITTED",
                        "physical_gem_item_ids":[240908]*4,
                        "J_candidate_unadmitted":92}
                variable_result=boot.preview_from_environment_build(
                    user,root/"variable_socket",binary,"c"*40,
                    environment_result=env)
                self.assertEqual(variable_result["status"],
                    "SEASON_PROFILE_COMPOSED_NOT_ADMITTED_NO_NATIVE")
                self.assertTrue(variable_result[
                    "existing_v271_variable_socket_connected_unadmitted"])
                self.assertIn("gem_id=240983",
                    next(row for row in variable_result["profile_simc"].splitlines()
                         if row.startswith("wrists=")))
                self.assertNotIn("gem_id=",
                    next(row for row in variable_result["profile_simc"].splitlines()
                         if row.startswith("head=")))
                self.assertEqual(variable_result["scenario"]["consumables"][
                    "special_gem_id"],240983)
                self.assertEqual(variable_result["scenario"]["consumables"][
                    "gem_budget_J"],92)
                self.assertEqual(variable_result[
                    "v271_variable_socket_layout_unadmitted"][
                    "ordinary_gem_ids"],[240908]*4)
                self.assertEqual(variable_result["new_native_calls"],0)
                self.assertFalse((root/"variable_socket").exists())
                # A v271 four-color reshuffle may change physical IDs.
                # v222's original per-ID J cannot be silently reused.
                variable["special_gem_id"]=240967
                with self.assertRaisesRegex(boot.UserScenarioBlocked,
                        "SEASON_V271_PHYSICAL_GEM_IDS_CHANGED_AFTER_J"):
                    boot.preview_from_environment_build(
                        user,root/"changed_physical_gem_id",binary,"c"*40,
                        environment_result=env)
                self.assertFalse((root/"changed_physical_gem_id").exists())
                calc["J"]=143
                env["source_compilation"][
                    "physical_gem_layout_unadmitted"]=layout
                env["source_compilation"][
                    "physical_gem_J_arithmetic_unadmitted"]={
                        "status":"PHYSICAL_GEM_J_ARITHMETIC_UNADMITTED",
                        "physical_gem_item_ids":list(layout["ordinary_gem_ids"]),
                        "J_candidate_unadmitted":143}
                env["source_compilation"][
                    "physical_gem_J_arithmetic_unadmitted"][
                        "J_candidate_unadmitted"]=142
                with self.assertRaisesRegex(
                        boot.UserScenarioBlocked,
                        "SEASON_SETTINGS_V271_V222_PHYSICAL_J_DRIFT"):
                    boot.preview_from_environment_build(
                        user,root/"bad_J",binary,"c"*40,
                        environment_result=env,season_controls=controls)
                self.assertFalse((root/"bad_J").exists())
                self.assertFalse(result[
                    "verified_user_default_options_registered"])
                self.assertEqual(result["new_native_calls"],0)
                self.assertFalse((root/"preview").exists())
                wrong_settings=copy.deepcopy(doc["settings"])
                wrong_settings["default_consumables"]["gem_budget_J"]=138
                with self.assertRaisesRegex(boot.UserScenarioBlocked,
                        "SEASON_V216_SETTINGS_J_F_DRIFT"):
                    boot.preview_from_environment_build(
                        user,root/"wrong_settings",binary,"c"*40,
                        environment_result=env,
                        season_settings=wrong_settings)
                old_sha=calc["source_catalog_artifact_sha256"]
                calc["source_catalog_artifact_sha256"]="0"*64
                try:
                    with self.assertRaisesRegex(boot.UserScenarioBlocked,
                            "SEASON_V216_GJFO_SOURCE_CATALOG_SHA_DRIFT"):
                        boot.preview_from_environment_build(
                            user,root/"wrong_catalog",binary,"c"*40,
                            environment_result=env,
                            season_settings=doc["settings"])
                finally:
                    calc["source_catalog_artifact_sha256"]=old_sha
                # Both the settings and replacement budget may agree with
                # each other yet disagree with the ORIGINAL v222 GJFO.
                bad_bundle=copy.deepcopy(doc)
                bad_bundle["settings"]["default_consumables"]["flask_budget_F"]=177
                bad_bundle["budget"]["flasks"]["total_F"]=177
                with self.assertRaisesRegex(boot.UserScenarioBlocked,
                        "SEASON_SOURCE_BUNDLE_V222_J_F_RATING_DRIFT"):
                    boot.build(user,root/"wrong_jf",binary,"c"*40,
                        current_season_product=True,
                        season_source_bundle=bad_bundle,
                        season_profile_inputs=payload)
                self.assertFalse((root/"wrong_settings").exists())
                self.assertFalse((root/"wrong_catalog").exists())
                self.assertFalse((root/"wrong_jf").exists())

    def test_p3_dh_incomplete_source_or_settings_remains_pending(self):
        import v098_target_user_scenario_bootstrap as boot
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            incomplete={"normal_build_entry":True,
                        "zero_history_build":{"environment_ready":False},
                        "source_compilation":{
                            "status":"COLLECTED_COMPILER_INPUTS_PENDING",
                            "missing":["TIER_V168"]}}
            result=boot.preview_from_environment_build(
                {},root/"never_writes",root/"no_binary","c"*40,
                environment_result=incomplete)
            self.assertEqual(result["status"],
                "V216_TO_V098_SOURCE_PROFILE_PENDING")
            self.assertIn("ORIGINAL_V191_V213_COMPILATION_PENDING",
                          result["missing"])
            self.assertIn("ORIGINAL_V191_GEAR_TIER_PATHS_PENDING",
                          result["missing"])
            self.assertIn("SELECTED_V222_GJFO_PROFILE_INPUTS_PENDING",
                          result["missing"])
            self.assertIn("SEASON_SPECIFIC_GEM_AND_CONSUMABLE_SETTINGS_PENDING",
                          result["missing"])
            self.assertFalse(result["environment_ready"])
            self.assertFalse(result["user_session_created"])
            self.assertFalse((root/"never_writes").exists())
            with self.assertRaisesRegex(boot.UserScenarioBlocked,
                    "SEASON_V216_NORMAL_BUILD_UNADMITTED_RESULT_REQUIRED"):
                boot.preview_from_environment_build(
                    {},root/"invalid",root/"no_binary","c"*40,
                    environment_result={"normal_build_entry":False})

    def test_p3_di_unsupported_layout_and_multi_stat_flask_stay_pending(self):
        import v098_target_user_scenario_bootstrap as boot
        layout,_=self.physical_layout()
        numeric=self.dynamic_season_profile_inputs()
        controls={"food":"food_token",
                  "potion":"potion_token","augmentation":"aug_token",
                  "omnium_talents":None}
        joined={"physical_gem_layout_unadmitted":layout,
                "physical_gem_J_arithmetic_unadmitted":{
                    "status":"PHYSICAL_GEM_J_ARITHMETIC_UNADMITTED",
                    "physical_gem_item_ids":[240908]*6,
                    "J_candidate_unadmitted":143}}
        direct=boot._season_settings_from_v216(
            compilation=joined,numeric_inputs=numeric,
            controls=controls,need=boot.need)
        self.assertEqual(direct["settings"]["gems"]["head"],"240967")
        self.assertEqual(direct["settings"]["gems"]["feet"],"240908/240908")
        self.assertFalse(direct["game_socket_legality_authenticated_here"])
        self.assertIsNone(direct["settings"]["character_level"])
        with self.assertRaisesRegex(
                boot.UserScenarioBlocked,
                "SEASON_SETTINGS_ONLY_OPTIONAL_CONSUMABLE_AND_MODULE_FIELDS"):
            boot._season_settings_from_v216(
                compilation=joined,numeric_inputs=numeric,
                controls={**controls,"character_level":90},need=boot.need)
        with self.assertRaisesRegex(
                boot.UserScenarioBlocked,
                "SEASON_SETTINGS_EXACT_OPTIONAL_SIMC_TOKEN_REQUIRED"):
            boot._season_settings_from_v216(
                compilation=joined,numeric_inputs=numeric,
                controls={**controls,"food":"source_default"},need=boot.need)
        changed=copy.deepcopy(layout)
        changed["ordinary_gem_ids"]=[240908]*5
        changed["socket_counts"]["feet"]=1
        changed["socket_total"]=6
        joined["physical_gem_layout_unadmitted"]=changed
        joined["physical_gem_J_arithmetic_unadmitted"]={
            **joined["physical_gem_J_arithmetic_unadmitted"],
            "physical_gem_item_ids":[240908]*5}
        result=boot._season_settings_from_v216(
            compilation=joined,numeric_inputs=numeric,
            controls=controls,need=boot.need)
        self.assertEqual(result["status"],
            "SEASON_SETTINGS_PHYSICAL_GEMS_FLASK_COMPOSED_UNADMITTED")
        self.assertEqual(result["v271_socket_plan_unadmitted"][
            "ordinary_gem_ids"],[240908]*5)
        self.assertEqual(result["v271_socket_plan_unadmitted"][
            "socket_counts"]["feet"],1)
        joined["physical_gem_layout_unadmitted"]=layout
        joined["physical_gem_J_arithmetic_unadmitted"]={
            **joined["physical_gem_J_arithmetic_unadmitted"],
            "physical_gem_item_ids":[240908]*6}
        different=copy.deepcopy(numeric)
        different["flask"]["static_CHMV_vector"]["crit_rating"]=80
        different["flask"]["static_CHMV_vector"]["haste_rating"]=96
        result=boot._season_settings_from_v216(
            compilation=joined,numeric_inputs=different,
            controls=controls,need=boot.need)
        self.assertIn("V139_MULTI_STAT_FLASK_SOURCE_COMPOSER_PENDING",
                      result["missing"])

    def test_automatic_target_goes_through_existing_v222_once(self):
        result=self.run_build()
        source=result["source_compilation"]
        calc=source["preprofile_budget_arithmetic_unadmitted"]
        self.assertEqual((calc["reference_G"],calc["J"],calc["F"]),
                         (2850,138,165))
        self.assertEqual((calc["reference_B"],calc["base_B"],calc["final_T"]),
                         (3153,3153,3185))
        self.assertEqual(sum(calc["fixed_O"].values()),32)
        self.assertFalse(calc["manual_final_T_authoritative"])
        self.assertEqual(result["zero_history_build"][
            "preprofile_budget_arithmetic_unadmitted"],calc)
        self.assertEqual(calc["native_calls"],0)
        self.assertTrue(result["normal_build_entry"])
        self.assertEqual(result["native_calls"],0)
        for name in ("G","J","F","O","B","T"):
            self.assertIsNone(result[name])
        self.assertFalse(result["zero_history_build"]["environment_ready"])
    def test_manual_user_final_T_is_not_overwritten_by_auto_reference(self):
        result=self.run_build(manual=3300)
        calc=result["source_compilation"][
            "preprofile_budget_arithmetic_unadmitted"]
        self.assertEqual((calc["reference_B"],calc["base_B"],calc["final_T"]),
                         (3153,3268,3300))
        self.assertTrue(calc["manual_final_T_authoritative"])
        self.assertEqual(calc["base_B"]+sum(calc["fixed_O"].values()),
                         calc["final_T"])
        self.assertFalse(result["zero_history_build"]["user_session_created"])
    def test_same_build_proof_absent_preserves_prior_source_pending(self):
        result=self.run_build(proof=False)
        self.assertNotIn("preprofile_budget_arithmetic_unadmitted",
                         result["source_compilation"])
        self.assertNotIn("preprofile_budget_arithmetic_unadmitted",
                         result["zero_history_build"])
        self.assertFalse(result["zero_history_build"]["environment_ready"])
    def test_user_target_mismatch_blocks_before_collector(self):
        with mock.patch.object(build,"collect_wago_new_season_source",
                               side_effect=AssertionError("WAGO_MUST_NOT_RUN")):
            with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                        "USER_REPRESENTATIVE_ILEVEL_MISMATCH"):
                build.build_environment(
                    sessions_root=self.root/"sessions",session_folder=None,
                    user={"target":{"ilevel":335,"final_T":3300}},
                    binary=None,revision=None,static_cache=None,
                    source_catalog_path=None,bootstrap_result=None,
                    fresh_collection_inputs={
                        "expected_game_build":self.catalog["game_build"],
                        "representative_request":{"class":"mage","spec":"frost",
                                                  "target_ilevel":334},
                        "g_probe_character":None,
                        "simc_revision_hint":None,
                        "same_build_budget_evidence":self.table[334]})
    def test_unrelated_build_proof_blocks_no_fake_budget(self):
        foreign=copy.deepcopy(self.table[334])
        foreign["components"]["F"]["game_build"]="12.2.0.99999"
        orig=self.table[334]
        self.table[334]=foreign
        try:
            with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                        "V216_ZERO_HISTORY_SOURCE_COMPILER_INVALID"):
                self.run_build()
        finally:
            self.table[334]=orig
        self.assertFalse((self.root/"sessions").exists())
    def test_infeasible_manual_T_does_not_install_session(self):
        with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                    "V216_ZERO_HISTORY_SOURCE_COMPILER_INVALID"):
            self.run_build(manual=100)
        self.assertFalse((self.root/"sessions").exists())

if __name__=="__main__":
    unittest.main()
