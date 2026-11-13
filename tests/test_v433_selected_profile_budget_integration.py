"""v433 B8 source-only v098/v432 physical selected profile integration.

All receipts and stat cache are fabricated in-memory; these tests prove
fail-closed wiring, not current-season Native acceptance or product E2E.
"""
from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v046_static_item_cache as cache_mod
import v098_target_user_scenario_bootstrap as bootstrap
import v101_common_representative_equipment as common
import v212_environment_manifest as installed
import v218_v098_profile_stage_adapter as stage
from tests.test_v432_selected_4pc_budget_bridge import B8BudgetPreflight, STATS


class SelectedSourceProfileBridge(unittest.TestCase):
    def setUp(self):
        self.fx=B8BudgetPreflight()
        self.fx.setUp()
        self.dir=tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.cache_file=pathlib.Path(self.dir.name)/"exact-v046.json"
        self.install_file=pathlib.Path(self.dir.name)/"v212.json"
        self.profile='mage="Selected_B8"\nspec=frost\n'
        self.cfg={
            "source":{"kind":"user_supplied","profile_sha256":
                      hashlib.sha256(self.profile.encode("utf8")).hexdigest()},
            "equipment":common.physical_gear_groups(
                self.fx.after,self.fx.groups,[])[0]}
        self.candidate={
            "receipt_sha256":"a"*64,
            "selected_G_slot_ids":{
                k:v["item_id"] for k,v in self.fx.base.items()},
            "game_build":"12.1.5.70783",
            "simc_revision":"c"*40}
        self.fx.doc["simc_revision"]="c"*40
        self.refresh_cache()

    def refresh_cache(self):
        self.cache_file.write_text(json.dumps(
            self.fx.cache,sort_keys=True),encoding="utf8")
        self.install_file.write_text("{}\n",encoding="utf8")

    def preflight(self):
        with mock.patch.object(installed,"read_json",return_value=(
                self.fx.doc,None)) as read, \
             mock.patch.object(installed,
                "verify_fresh_installed_environment",
                return_value=True) as validated:
            result=bootstrap._selected_season_profile_budget_preflight(
                user=self.fx.user,profile=self.profile,cfg=self.cfg,
                rows=self.fx.after,groups=self.fx.groups,catalyst=[],
                baseline_rows=self.fx.base,candidate=self.candidate,
                class_tier_five=self.fx.tier,
                original_v191_link=self.fx.link,
                installed_path=self.install_file,
                cache_path=self.cache_file)
        read.assert_called_once()
        validated.assert_called_once()
        return result

    def test_exact_selected_physical_profile_and_budget_are_bound_not_admitted(self):
        result=self.preflight()
        self.assertEqual(result["status"],
                         "B8_SELECTED_PROFILE_BUDGET_RECONCILED_NOT_ADMITTED")
        self.assertEqual(result["budget_preflight"]["base_B"],3162)
        self.assertEqual(result["budget_preflight"]["fixed_L_in_G_once"],
                         {k:0 for k in STATS})
        self.assertEqual(result["selected_equipment"],self.cfg["equipment"])
        self.assertEqual(result["bound_source_identity"][
            "selected_profile_sha256"],self.cfg["source"]["profile_sha256"])
        self.assertTrue(result["bound_source_identity_sha256"])
        self.assertFalse(result["runtime_manifest_created"])
        self.assertFalse(result["native_execution_authorized"])
        self.assertEqual(result["native_calls"],0)

    def test_missing_exact_variant_keeps_selected_profile_pending(self):
        head=self.fx.after["head"]
        import v432_selected_4pc_budget_bridge as budget
        ident=budget._bare(head,self.fx.cache["season"])
        self.fx.cache["variants"].pop(cache_mod.digest(ident))
        self.refresh_cache()
        result=self.preflight()
        self.assertEqual(result["status"],
                         "B8_SELECTED_PROFILE_STATIC_VARIANTS_PENDING_NO_NATIVE")
        self.assertEqual([r["item_id"] for r in result[
            "budget_preflight"]["missing_exact_native_variants"]],[239652])
        self.assertNotIn("base_B",result["budget_preflight"])
        self.assertFalse(result["native_execution_authorized"])

    def test_wrong_original_tier_map_fails_closed(self):
        self.fx.tier["chest"]=999999
        with self.assertRaisesRegex(bootstrap.UserScenarioBlocked,
                                    "FOUR_TIER_DRIFT"):
            self.preflight()

    def test_changed_real_profile_without_rebinding_sha_is_blocked(self):
        self.profile+="gear_crit_rating=999999\n"
        with self.assertRaisesRegex(bootstrap.UserScenarioBlocked,
                                    "EQUIPMENT_OR_SHA_DRIFT"):
            self.preflight()

    def test_changed_cache_season_without_new_source_owner_is_blocked(self):
        self.fx.cache["season"]="midnight_s3"
        self.refresh_cache()
        with self.assertRaisesRegex(bootstrap.UserScenarioBlocked,
                                    "CACHE_SEASON_NOT_VERIFIED"):
            self.preflight()

    def test_static_digest_or_install_source_drift_is_blocked(self):
        first=next(iter(self.fx.cache["variants"].values()))
        first["static_digest"]="0"*64
        self.refresh_cache()
        with self.assertRaisesRegex(bootstrap.UserScenarioBlocked,
                                    "B8_SELECTED_EXACT_STATIC_CACHE_INVALID"):
            self.preflight()
        self.fx=B8BudgetPreflight()
        self.fx.setUp()
        self.refresh_cache()
        self.fx.link["source_catalog_artifact_sha256"]="e"*64
        with self.assertRaisesRegex(bootstrap.UserScenarioBlocked,
                                    "SOURCE_IDENTITY_DRIFT"):
            self.preflight()

    def test_missing_verified_install_or_cache_never_creates_manifest(self):
        env={
            "normal_build_entry":True,
            "zero_history_build":{"environment_ready":True},
            "source_compilation":{
                "verified_environment_install":{
                    "environment_ready":True,
                    "environment_installed":True,
                    "status":"FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY",
                    "stage_output_path":str(self.install_file)}}}
        user=self.fx.user
        result=bootstrap.preview_from_environment_build(
            user,pathlib.Path(self.dir.name)/"generated",
            pathlib.Path("/not-an-executable"),"c"*40,
            environment_result=env)
        self.assertEqual(result["status"],
                         "B8_SELECTED_VERIFIED_INSTALL_OR_EXACT_CACHE_PENDING")
        self.assertIn("B8_SELECTED_EXACT_V046_CACHE_REQUIRED",result["missing"])
        self.assertFalse(result["native_execution_authorized"])
        self.assertFalse((pathlib.Path(self.dir.name)/"generated").exists())

    def test_v218_web_fresh_selected_start_blocks_before_files_or_native(self):
        folder=pathlib.Path(self.dir.name)/"web-session"
        with self.assertRaisesRegex(stage.engine.StageExecutionBlocked,
                                    "B8_SELECTED_PROFILE_BUDGET_NOT_RUNTIME"):
            stage.build_or_reuse(
                user=self.fx.user,session_folder=folder,
                binary=pathlib.Path("/not-an-executable"),
                revision="c"*40,static_cache=None,
                current_season_product=True,
                verified_fresh_environment_result={})
        self.assertFalse(folder.exists())


if __name__=="__main__":
    unittest.main()
