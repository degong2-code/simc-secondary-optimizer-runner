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
    def run_build(self,manual=None,proof=True,level=334,user_level=None):
        inputs={
            "expected_game_build":self.catalog["game_build"],
            "representative_request":{
                "class":"mage","spec":"frost","target_ilevel":level},
            "g_probe_character":None,
            "simc_revision_hint":None}
        if proof:
            inputs["same_build_budget_evidence"]=self.table[334]
        user={"target":{"ilevel":user_level if user_level is not None else level,
                        "final_T":manual}}
        with mock.patch.object(build,"collect_wago_new_season_source",
                               return_value=self.collected) as collect,\
             mock.patch.object(build.zero_history_G_native,"collect",
                               return_value={"status":"PENDING",
                                             "new_native_calls":0}) as native,\
             mock.patch.object(build.source_wiring,"compile_collected",
                               return_value=dict(self.compiled)) as compiler,\
             mock.patch.object(build.environment_manifest,"read_json",
                               return_value=(self.catalog,"a"*64)),\
             mock.patch.object(build.source_to_catalog,"verify_catalog"),\
             mock.patch.object(build.user_catalog,"public_options",
                               return_value=self.ui),\
             mock.patch.object(build,"_fresh_gem_item_source_stage",
                               return_value={"candidate_path":None}):
            result=build.build_environment(
                sessions_root=self.root/"sessions",session_folder=None,
                user=user,binary=None,revision=None,static_cache=None,
                source_catalog_path=None,bootstrap_result=None,
                fresh_collection_inputs=inputs)
        self.assertEqual(collect.call_count,1)
        self.assertEqual(native.call_count,1)
        self.assertEqual(compiler.call_count,1)
        self.assertNotIn("same_build_budget_evidence",
                         collect.call_args.kwargs)
        self.assertFalse((self.root/"sessions").exists())
        return result
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
