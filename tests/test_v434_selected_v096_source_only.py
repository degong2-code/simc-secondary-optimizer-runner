"""v434: v096 reuses v091/v090/v065 selected-budget path, Native zero.

These source-bound receipts are synthetic/mocked, not actual 70783 Native
or source-admission evidence. No manifest or optimizer should be created.
"""
from __future__ import annotations

import copy
import hashlib
import pathlib
import sys
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v096_unified_product_entry as entry
import v098_target_user_scenario_bootstrap as bootstrap
import v212_environment_manifest as installed
from tests.test_v433_selected_profile_budget_integration import SelectedSourceProfileBridge
from tests.test_v432_selected_4pc_budget_bridge import STATS

def vec(**kwargs):
    return {k:kwargs.get(k,0) for k in STATS}

class V096SelectedNonadmittedPreflight(unittest.TestCase):
    def setUp(self):
        self.fx=SelectedSourceProfileBridge()
        self.fx.setUp()
        self.addCleanup(self.fx.dir.cleanup)
        self.selected=self.fx.preflight()
        self.profile='flask=verified_flask_token\ntemporary_enchant=disabled\n'
        self.sha=hashlib.sha256(self.profile.encode("utf8")).hexdigest()
        self.F=vec(haste_rating=165)
        self.doc=self.fx.doc
        self.doc["official_F_physical_source"]={
            "physical_item_id":987654,
            "simc_input_token":"verified_flask_token",
            "static_CHMV_vector":self.F,"F_rating":165}
        self.raw={
            "source":{"profile_sha256":self.sha},
            "target":{"mode":"manual_total","ilevel":334,
                      "manual_total":3162},
            "equipment":self.selected["selected_equipment"]}
        self.normalized={
            "scenario":self.raw,
            "scenario_digest":"e"*64,
            "budget":{"T":3162,"J":92,"F":165,
                      "external_temporary_rating":vec()}}
        self.typed={
            "scenario":self.raw,
            "scenario_digest":self.normalized["scenario_digest"],
            "base_B":3162,"final_T":3162,"fixed_O":vec(),
            "flask_F":self.F,
            "source_profile_sha256":self.sha}
        self.composed={
            "schema":"v098_source_only_season_profile_plan_v1",
            "status":"SEASON_PROFILE_COMPOSED_NOT_ADMITTED_NO_NATIVE",
            "v096_typed_input_unadmitted":self.typed,
            "profile_simc":self.profile,
            "scenario":self.raw,
            "source_profile_sha256":self.sha}
        self.season={
            "flask":{"physical_item_id":987654,
                     "simc_input_token":"verified_flask_token",
                     "static_CHMV_vector":self.F},
            "oil_by_hand":{}}
        self.native={
            "oil":{"profile_sha256":self.sha,"declared_O":vec()},
            "prepared":{"T":3162,"scenario":self.normalized,
                        "static_budget":{
                            "locked_L_when_all_specials_observed":vec()}},
            "approved_total":{"base_B":3162,"final_T":3162}}

    def verify(self):
        with (
            mock.patch.object(installed,
                              "verify_fresh_installed_environment",
                              return_value=True),
            mock.patch.object(entry.contract,"normalize",
                              return_value=self.normalized),
            mock.patch.object(entry.oil_adapter,"prepare",
                              return_value=self.native) as prep,
            mock.patch.object(entry.scheduler,
                              "budget_with_fixed_components",
                              return_value={"bounded":True}) as bound,
            mock.patch.object(entry.scheduler,"bounds",
                              return_value=(3162,(0,0,0,0),
                                            (3162,3162,3162,3162)))
        ):
            out=entry.preflight_selected_fresh_source_only(
                selected=self.selected,composed=self.composed,
                fillers=[],native_cache=self.fx.cache,
                installed_document=self.doc,
                season_profile_inputs=self.season,
                weapon_layout="single_two_hand",oil_hands=[])
        return out,prep,bound

    def test_source_profile_v212_F_O_G_L_B_T_and_bounds_no_native(self):
        out,prep,bound=self.verify()
        self.assertEqual(out["status"],
          "B8_V096_SOURCE_ONLY_PROFILE_AND_STATIC_BOUNDS_VALIDATED")
        self.assertEqual((out["base_B"],out["final_T"]),(3162,3162))
        self.assertEqual(out["fixed_L_once"],vec())
        self.assertEqual(out["flask_F"],self.F)
        self.assertFalse(out["native_execution_authorized"])
        self.assertFalse(out["runtime_manifest_created"])
        self.assertEqual(out["native_calls"],0)
        self.assertEqual(prep.call_count,1)
        self.assertEqual(prep.call_args.kwargs["season_base_B"],3162)
        self.assertEqual(bound.call_count,1)

    def test_changed_final_profile_sha_is_blocked(self):
        self.composed["profile_simc"]+="gear_crit_rating=99999\n"
        with self.assertRaisesRegex(entry.EntryBlocked,"PROFILE_J_F_O_B_T_OR_SHA"):
            self.verify()

    def test_manual_T_inconsistent_with_selected_B_is_blocked(self):
        self.typed["base_B"]=4000
        with self.assertRaisesRegex(entry.EntryBlocked,"PROFILE_J_F_O_B_T"):
            self.verify()

    def test_wrong_physical_flask_id_does_not_pass_same_F(self):
        self.season["flask"]["physical_item_id"]=111111
        with self.assertRaisesRegex(entry.EntryBlocked,"F_ITEM_OR_TOKEN"):
            self.verify()

    def test_installed_oil_diff_blocks_even_when_zero_reported(self):
        self.season["oil_by_hand"]={"main_hand":{
            "physical_item_id":1,"simc_input_token":"main_hand:fake",
            "static_CHMV_vector":vec(haste_rating=16)}}
        with self.assertRaisesRegex(entry.EntryBlocked,"PHYSICAL_HAND_DRIFT"):
            self.verify()

    def test_v433_sha_tampering_and_missing_variant_fail_closed(self):
        self.selected["bound_source_identity"]["selected_budget_identity_sha256"]="0"*64
        with self.assertRaisesRegex(entry.EntryBlocked,"PROOF_INSTALLED_OR_SHA"):
            self.verify()
        self.selected=self.fx.preflight()
        self.selected["budget_preflight"]["missing_exact_native_variants"]=[
            {"slot":"head","item_id":239652}]
        with self.assertRaisesRegex(entry.EntryBlocked,"PROOF_INSTALLED_OR_SHA"):
            self.verify()

    def test_native_static_L_or_B_mismatch_blocks(self):
        self.native["prepared"]["static_budget"][
            "locked_L_when_all_specials_observed"]=vec(crit_rating=15)
        with self.assertRaisesRegex(entry.EntryBlocked,"EXACT_L_OR_PREPARED"):
            self.verify()
        self.native["prepared"]["static_budget"][
            "locked_L_when_all_specials_observed"]=vec()
        self.native["approved_total"]["final_T"]=3200
        with self.assertRaisesRegex(entry.EntryBlocked,"EXACT_L_OR_PREPARED"):
            self.verify()

    def test_unadmitted_v433_cannot_become_runtime_input(self):
        self.selected["native_execution_authorized"]=True
        with self.assertRaisesRegex(entry.EntryBlocked,"NONADMITTED_V433"):
            self.verify()


class V098SelectedCompositionWiring(unittest.TestCase):
    def setUp(self):
        self.fx=SelectedSourceProfileBridge()
        self.fx.setUp()
        self.addCleanup(self.fx.dir.cleanup)
        self.user=self.fx.fx.user

    def test_rebased_v222_budget_reaches_existing_season_serializer(self):
        # The same user that swaps crafted head restores fifth chest tier.
        proof=self.fx.preflight()
        original={
            "v216_numeric_preview":{"calculation":{
                "game_build":"12.1.5.70783","target_ilevel":334,
                "source_catalog_manifest_sha256":"b"*64,
                "source_catalog_artifact_sha256":"c"*64,
                "base_B":3107,"final_T":3107,
                "J":92,"F":165,"fixed_O":vec()}}}
        final_profile=self.fx.profile+"flask=verified\ntemporary_enchant=disabled\n"
        final_sha=hashlib.sha256(final_profile.encode("utf8")).hexdigest()
        composed={
            "profile_simc":final_profile,"source_profile_sha256":final_sha,
            "scenario":self.fx.cfg,
            "v096_typed_input_unadmitted":{"scenario_digest":"d"*64}}
        preflight={
            "base_B":3162,
            "lower_B":vec(),"upper_B":{k:3162 for k in STATS}}
        # Limit mocks to original v212 read and existing serializer/v096
        # owner; v432 delta, real physical-row and profile binding remain.
        with (
            mock.patch.object(installed,"read_json",
                              return_value=(self.fx.doc,None)),
            mock.patch.object(installed,
                "verify_fresh_installed_environment",return_value=True),
            mock.patch.object(bootstrap,"season_profile_source_only",
                              return_value=composed) as serializer,
            mock.patch.object(bootstrap.entry,
                "preflight_selected_fresh_source_only",
                return_value=preflight) as owner
        ):
            out=bootstrap._selected_season_profile_budget_preflight(
                user=self.user,profile=self.fx.profile,
                cfg=self.fx.cfg,rows=self.fx.fx.after,
                groups=self.fx.fx.groups,catalyst=[],
                baseline_rows=self.fx.fx.base,candidate=self.fx.candidate,
                class_tier_five=self.fx.fx.tier,
                original_v191_link=self.fx.fx.link,
                installed_path=self.fx.install_file,
                cache_path=self.fx.cache_file,
                season_profile_inputs=original,
                weapon_layout="single_two_hand",fillers=[])
        args=serializer.call_args.kwargs
        self.assertEqual(args["season_profile_inputs"][
            "v216_numeric_preview"]["calculation"]["base_B"],3162)
        self.assertEqual(args["season_profile_inputs"][
            "v216_numeric_preview"]["calculation"]["final_T"],3162)
        self.assertEqual(original["v216_numeric_preview"][
            "calculation"]["base_B"],3107)
        self.assertEqual(owner.call_count,1)
        self.assertEqual(out["status"],
            "B8_SELECTED_V096_COMPLETE_PROFILE_BUDGET_NOT_ADMITTED")
        self.assertEqual(out["source_profile_sha256"],final_sha)
        self.assertEqual(len(out["seed_targets_B_unadmitted"]),2)
        self.assertFalse(out["native_execution_authorized"])
        self.assertFalse(out["runtime_manifest_created"])


if __name__=="__main__":
    unittest.main()
