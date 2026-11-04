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
                  effect_observation=None,selected_budget_items=None):
        inputs={
            "expected_game_build":self.catalog["game_build"],
            "representative_request":{
                "class":"mage","spec":"frost","target_ilevel":level},
            "g_probe_character":None,
            "simc_revision_hint":None}
        if proof:
            inputs["same_build_budget_evidence"]=self.table[334]
        if gem_layout is not None:
            inputs["gem_layout_receipt"]=gem_layout
        if gem_ratings is not None:
            inputs["gem_rating_by_id"]=gem_ratings
        if effect_requests is not None:
            inputs["effect_probe_requests"]=effect_requests
        if selected_budget_items is not None:
            inputs["selected_budget_items"]=selected_budget_items
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
                               return_value={"candidate_path":None}),\
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
        self.assertEqual(native.call_count,1)
        self.assertEqual(compiler.call_count,1)
        for name in ("same_build_budget_evidence","gem_layout_receipt",
                     "gem_rating_by_id","effect_probe_requests",
                     "selected_budget_items"):
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

    def test_real_id_gem_layout_J_reused_in_zero_history_without_promotion(self):
        layout, ratings=self.physical_layout()
        result=self.run_build(proof=False,gem_layout=layout,
                              gem_ratings=ratings)
        j=result["source_compilation"]["physical_gem_J_arithmetic_unadmitted"]
        self.assertEqual(j["J_candidate_unadmitted"],138)
        self.assertEqual(j["physical_gem_item_ids"],[240908]*6)
        self.assertFalse(j["game_socket_legality_verified_here"])
        self.assertNotIn("preprofile_budget_arithmetic_unadmitted",
                         result["source_compilation"])
        self.assertIsNone(result["J"])
        self.assertFalse(result["zero_history_build"]["environment_ready"])

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
        self.assertEqual(native["oil"][0]["rating_candidate_unadmitted"]
                         ["haste_rating"],17)
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
        self.assertEqual(record[
            "static_O_for_hand_unadmitted"]["haste_rating"],17)
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
            "crit_rating":16,"haste_rating":17,
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
            "haste_rating"],17)
        self.assertEqual(linked["v222_arithmetic_unadmitted"]["base_B"],3300)
        self.assertEqual(linked["v222_arithmetic_unadmitted"]["final_T"],3333)
        self.assertEqual(linked["matched_o_by_hand"]["main_hand"][
            "representative_weapon_id"],9101)
        self.assertFalse(linked["user_selectable"])

    def test_selected_flask_or_oil_rating_conflict_blocks(self):
        numeric,choices=self.selected_physical_pair()
        source=copy.deepcopy(self.table[334])
        source["components"]["O"]["applied_hands"]=["main_hand"]
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
