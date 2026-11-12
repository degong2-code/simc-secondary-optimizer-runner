"""P3-CD: normal zero-history v216 -> ORIGINAL v241 automatic handoff.

Synthetic staged files mimic the existing producers. This tests only the
automatic wiring; v241's full original compiler/receipts have their own
test_v240 suite. No real network, SimC Native, old season, user paths.
"""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v216_environment_build_coordinator as build
import v274_zero_history_source_compiler_wiring as wiring


class ZeroHistorySourceCompilerWiring(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=pathlib.Path(tmp.name)
        self.stage=self.root/"build"/"_fresh_season_sources"/"wago_12.2.0.99999"
        (self.stage/"wago").mkdir(parents=True)
        (self.stage/"wago"/"receipt.json").write_text("{}",encoding="utf8")
        self.original_revision="c"*40
        self.build="12.2.0.99999"
        self.source={
            "schema":"v216_fresh_source_stage_v1",
            "expected_game_build":self.build,
            "snapshot_receipt_path":str(self.stage/"wago"/"receipt.json"),
            "source_stage":{"status":"EXECUTED_AND_SEALED","reused":False},
            "environment_installed":False,"environment_ready":False,
            "native_calls":0,
            "G":None,"J":None,"F":None,"O":None,"B":None,"T":None,
            "simc_source_collection_context":{
                "requested_game_event":"season_change"},
        }
        self.stage_record={"status":"EXECUTED_AND_SEALED"}

    def emit(self, relative, data):
        file=self.stage/relative
        file.parent.mkdir(parents=True,exist_ok=True)
        file.write_text(json.dumps(data),encoding="utf8")
        return file

    def complete_producer_outputs(self):
        gear=self.emit("source/v167.json",
                       {"schema":"v167_product_season_gear_db_v1"})
        tier=self.emit("source/v168.json",
                       {"schema":"v168_source_first_class_tier_5pc_v1"})
        effects=self.emit("source/v189.json",
                          {"schema":"v189_pinned_simc_effect_registration_candidates_v1"})
        cons=self.emit("source/v190.json",
                        {"schema":"v190_same_build_consumable_item_candidates_v1"})
        generated=self.stage/"source"/"v229_pinned_generated"
        generated.mkdir()
        for filename in ("permanent_enchant.inc","temporary_enchant.inc",
                         "gem_data.inc"):
            (generated/filename).write_text("test",encoding="utf8")
        self.emit("source/v229_pinned_generated/simc_seed_receipt.json",{
            "schema":"v229_simc_only_first_party_source_seed_v1",
            "simc_generated_build":self.build,
            "simc_revision":self.original_revision,
            "receipt_sha256":"a"*64})
        v211=self.stage/"source"/"v211_classification"
        v211.mkdir()
        for name in build.source_wiring.enchant_classifier.FRESH_REQUIRED:
            (v211/name).write_text("test",encoding="utf8")
        manifest=self.emit("source/v211_manifest.json",{"schema":"test"})
        self.source.update({
            "fresh_ordinary_gear":{"candidate_path":str(gear),
                                    "source_stage":dict(self.stage_record)},
            "fresh_tier":{"candidate_path":str(tier),
                          "source_stage":dict(self.stage_record)},
            "fresh_food_potion_item_sources":{
                "candidate_path":str(cons),
                "source_stage":{
                    **self.stage_record,
                    "output_paths":{"v189":"source/v189.json"}}},
            "fresh_pinned_first_party_simc_source":{
                "source_dir":str(generated),
                "simc_receipt_sha256":"a"*64,
                "source_stage":dict(self.stage_record)},
            "fresh_pinned_v211_source":{
                "source_dir":str(v211),
                "manifest_path":str(manifest),
                "source_stage":dict(self.stage_record)},
        })
        return effects

    def test_missing_producers_are_reported_without_compiling_or_guessing(self):
        with mock.patch.object(build.fresh_stage,
                               "compile_fresh_candidate",
                               side_effect=AssertionError("NO_COMPILER_INPUTS")):
            result=wiring.compile_collected(
                self.source,compiler=build.fresh_stage.compile_fresh_candidate)
        self.assertEqual(result["status"],"COLLECTED_COMPILER_INPUTS_PENDING")
        self.assertIn("TIER_V168",result["missing"])
        self.assertIn("SIMC_V211_SIX_SOURCE_FILES_AND_MANIFEST",
                      result["missing"])
        self.assertIn("GENERATED_PERMANENT",result["missing"])
        self.assertEqual(result["network_calls"],0)
        self.assertFalse(result["environment_ready"])

    def test_compiler_missing_source_reports_existing_owner_not_fake_budget_gate(self):
        """An optional catalog file can be missing without inventing G/J/F/O proof."""
        self.assertEqual(set(wiring.COMPILER_INPUT_OWNER),set(wiring.NEEDED))
        absent=wiring.discover(self.source)
        impact=absent["compiler_input_impact"]
        self.assertTrue(impact["full_catalog_compilation_pending"])
        self.assertFalse(impact["base_GJFO_numeric_evidence_verified_here"])
        self.assertFalse(impact["individual_optional_item_quality_approval_verified_here"])
        self.assertTrue(impact["unused_season_item_membership_not_required"])
        self.assertEqual(len(impact["catalog_input_missing"]),len(wiring.NEEDED))
        self.complete_producer_outputs()
        complete=wiring.discover(self.source)
        self.assertEqual(complete["status"],"COLLECTED_COMPILER_INPUTS_COMPLETE")
        self.assertEqual(complete["compiler_input_impact"][
            "catalog_input_missing"],[])
        self.assertFalse(complete["compiler_input_impact"][
            "base_GJFO_numeric_evidence_verified_here"])
        source=(self.stage/"source"/"v229_pinned_generated"/
                "permanent_enchant.inc")
        source.unlink()
        pending=wiring.discover(self.source)
        self.assertEqual(pending["missing"],["GENERATED_PERMANENT"])
        self.assertEqual(pending["compiler_input_impact"][
            "catalog_input_missing"],[{
                "input":"GENERATED_PERMANENT",
                "existing_producer":"v275",
                "catalog_role":"OPTIONAL_PERMANENT_ENCHANT_CATALOG"}])
        self.assertTrue(pending["compiler_input_impact"][
            "full_catalog_compilation_pending"])
        self.assertFalse(pending["environment_ready"])
        self.assertIsNone(pending["inputs"])

    def test_same_build_auto_assembly_calls_original_v241_not_new_compiler(self):
        self.complete_producer_outputs()
        path=self.emit("fresh_source/v213_candidate_catalog.json",{})
        fake={"source_catalog_path":str(path),
              "v191_stage":{"status":"EXECUTED_AND_SEALED"},
              "v211_stage":{"status":"EXECUTED_AND_SEALED"},
              "v213_stage":{"status":"EXECUTED_AND_SEALED"}}
        kwargs={"sessions_root":self.root/"sessions","session_folder":None,
                "user":None,"binary":None,"revision":None,
                "static_cache":None,"source_catalog_path":None,
                "bootstrap_result":None,"fresh_collection_inputs":{
                    "expected_game_build":self.build,
                    "representative_request":None,
                    "g_probe_character":None,"simc_revision_hint":None}}
        with mock.patch.object(build,"collect_wago_new_season_source",
                               return_value=self.source) as collect, \
             mock.patch.object(build.fresh_stage,
                               "compile_fresh_candidate",
                               return_value=fake) as compiled, \
             mock.patch.object(build,"preflight_new_season_source",
                               return_value={
                                   "preflight_sha256":"f"*64,
                                   "status":"FRESH_SOURCE_CANDIDATES_VALID_GJFO_PENDING_NOT_INSTALLED"
                               }) as preview:
            result=build.build_environment(**kwargs)
        self.assertEqual(collect.call_count,1)
        self.assertEqual(compiled.call_count,1)
        self.assertEqual(preview.call_count,1)
        params=compiled.call_args.kwargs
        self.assertEqual(params["expected_game_build"],self.build)
        self.assertEqual(params["expected_simc_revision"],
                         self.original_revision)
        self.assertEqual(params["stage_root"],self.stage)
        original=params["fresh_v191_inputs"]
        self.assertEqual(original["event"],"season_change")
        self.assertEqual(original["gear"].name,"v167.json")
        self.assertEqual(original["tier"].name,"v168.json")
        self.assertEqual(original["v189"].name,"v189.json")
        self.assertEqual(original["v190"].name,"v190.json")
        self.assertEqual(original["simc_generated_folder"].name,
                         "v229_pinned_generated")
        self.assertEqual(result["source_compilation"]["status"],
                         "FRESH_V191_V211_V213_COMPILED_UNADMITTED")
        original_links=result["source_compilation"][
            "v191_original_gear_tier_source_paths"]
        self.assertEqual(original_links["catalog"],str(path))
        self.assertEqual(original_links["gear"],str(original["gear"]))
        self.assertEqual(original_links["tier"],str(original["tier"]))
        self.assertEqual(result["source_compilation"]["preflight_sha256"],
                         "f"*64)
        self.assertFalse(result["zero_history_build"]["environment_ready"])
        self.assertFalse(result["zero_history_build"]["user_session_created"])
        self.assertFalse((self.root/"sessions").exists())

    def test_weapon_mask_successor_is_passed_to_original_v191(self):
        self.complete_producer_outputs()
        derived=self.emit("source/v285_weapon_masks.json",{
            "schema":"v190_same_build_consumable_item_candidates_v1",
            "weapon_equipped_source":{
                "schema":"v285_same_build_consumable_spell_weapon_source_v1",
                "game_build":self.build,"source_only":True}})
        self.source["fresh_consumable_weapon_source"]={
            "candidate_path":str(derived),
            "source_stage":{"status":"EXECUTED_AND_SEALED"}}
        discovered=wiring.discover(self.source)
        self.assertEqual(discovered["status"],"COLLECTED_COMPILER_INPUTS_COMPLETE")
        self.assertEqual(discovered["inputs"]["fresh_v191_inputs"]["v190"],
                         derived)
        self.assertFalse(discovered["environment_ready"])

    def test_wrong_tier_schema_or_foreign_sources_do_not_enter_v191(self):
        self.complete_producer_outputs()
        (self.stage/"source"/"v168.json").write_text(
            json.dumps({"schema":"v260_structural_tier_candidate"}))
        result=wiring.discover(self.source)
        self.assertIn("TIER_V168",result["missing"])
        self.assertIsNone(result["inputs"])
        outside=self.emit("source/v168.json",{
            "schema":"v168_source_first_class_tier_5pc_v1"})
        self.source["fresh_tier"]["candidate_path"]=str(self.root/"foreign.json")
        (self.root/"foreign.json").write_text(outside.read_text())
        result=wiring.discover(self.source)
        self.assertIn("TIER_V168",result["missing"])

    def test_untrusted_compiler_failure_blocks_without_installing(self):
        self.complete_producer_outputs()
        kwargs={"sessions_root":self.root/"sessions","session_folder":None,
                "user":None,"binary":None,"revision":None,
                "static_cache":None,"source_catalog_path":None,
                "bootstrap_result":None,"fresh_collection_inputs":{
                    "expected_game_build":self.build,
                    "representative_request":None,
                    "g_probe_character":None,"simc_revision_hint":None}}
        with mock.patch.object(build,"collect_wago_new_season_source",
                               return_value=self.source), \
             mock.patch.object(build.fresh_stage,"compile_fresh_candidate",
                               side_effect=ValueError("INVALID_SOURCE_BYTES")):
            with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                        "V216_ZERO_HISTORY_SOURCE_COMPILER_INVALID"):
                build.build_environment(**kwargs)
        self.assertFalse((self.root/"sessions").exists())


if __name__=="__main__":
    unittest.main()
