"""Focused normal v216 Environment Build integration of existing v262/v222."""
import copy
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))
import v216_environment_build_coordinator as build
import v222_season_budget_contract as budget
from tests.test_v222_season_budget_contract import fixture


def prepared():
    catalog, first, _ = fixture()
    catalog.update({
        "schema": "fresh-v213-test",
        "source_provenance": {"v191": {
            "sha256_by_input": {"budget": None}}},
        "enchant_classification": {"source_manifest_sha256": "d"*64},
        "catalog": {
            "consumables": {
                "flask": {"reference": None},
                "general_gems": {"reference": None}},
            "gear": {"count": 13},
            "tier": {"piece_count": 5}},
    })
    second = copy.deepcopy(first)
    second["target_ilevel"] = 335
    second["components"]["G"]["source_sha256"] = "e"*64
    for level, observed, proof in (
            (334,2847,first),(335,2853,second)):
        g = proof["components"]["G"]
        g["reference_track"] = "ordinary_two_hand"
        g["standardization"] = budget.standardize_representative_G(
            observed_G_total=observed,target_ilevel=level,
            source_observation_sha256=g["source_sha256"])
        g["rating"] = g["standardization"]["standardized_G"]
    ui = {
        "season_build": catalog["game_build"],
        "simc_revision":catalog["simc_revision"],
        "status":"FRESH_SEASON_CANDIDATES_UNAPPROVED_NOT_ENVIRONMENT_READY",
        "enchant_candidates":{"selectable_count":0,"total":0},
        "existing_allowed_input_choices":{},
        "environment_ready":False,
        "G":None,"J":None,"F":None,"O":None,"B":None,"T":None,
        "native_calls_now":0,"game_db_recollection_now":0,
        "optimizer_or_cache_mutated":False,
    }
    return catalog, {334:first,335:second}, ui


class StandardBudgetNormalBuildTests(unittest.TestCase):
    def preflight(self, table, *, level=334, manual=None,
                  track="ordinary_two_hand", exact=None):
        catalog, _, ui = prepared()
        with tempfile.TemporaryDirectory() as d:
            path = pathlib.Path(d)/"v213.json"
            path.write_text("{}",encoding="utf8")
            with mock.patch.object(build.environment_manifest,"read_json",
                                   return_value=(catalog,"a"*64)), \
                 mock.patch.object(build.source_to_catalog,"verify_catalog"), \
                 mock.patch.object(build.user_catalog,"public_options",
                                   return_value=ui):
                return build.preflight_new_season_source(
                    source_catalog_path=path,
                    expected_game_build=catalog["game_build"],
                    expected_simc_revision=catalog["simc_revision"],
                    standard_budget_evidence_by_ilevel=table,
                    standard_budget_reference_track=track,
                    target_ilevel=level,manual_final_T=manual,
                    budget_evidence=exact)

    def test_preflight_reuses_all_measured_rows_and_manual_final_T(self):
        _, table, _ = prepared()
        result = self.preflight(table,manual=3300)
        rows = result["standardized_ilevel_budget_rows_unadmitted"]
        self.assertEqual([x["ilevel"] for x in rows["rows"]],[334,335])
        self.assertEqual([x["G_standard"] for x in rows["rows"]],[2850,2850])
        self.assertEqual([x["B"] for x in rows["rows"]],[3153,3153])
        self.assertEqual(rows["rows"][0]["T"],3185)
        proposed=result["proposed_budget_arithmetic_unadmitted"]
        self.assertEqual((proposed["reference_G"],proposed["reference_B"],
                          proposed["base_B"],proposed["final_T"]),
                         (2850,3153,3268,3300))
        self.assertTrue(proposed["manual_final_T_authoritative"])
        self.assertIsNone(result["G"])
        self.assertFalse(result["environment_ready"])
        self.assertEqual((result["native_calls"],result["network_calls"]),(0,0))
        self.assertIn("G/J/F/O_VERIFIED_SOURCE_RECEIPTS",result["requires"])

    def test_missing_level_conflicting_proof_or_different_track_rejected(self):
        _, table, _ = prepared()
        with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                    "TARGET_ILEVEL_G_OBSERVATION_NOT_PROVIDED"):
            self.preflight(table,level=336)
        wrong=copy.deepcopy(table)
        wrong[335]["components"]["G"]["reference_track"]="titan_grip"
        with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                    "STANDARD_BUDGET_ROWS_INVALID"):
            self.preflight(wrong)
        different=copy.deepcopy(table[334])
        different["components"]["G"]["rating"]=2840
        with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                    "STANDARD_BUDGET_TARGET_EVIDENCE_CONFLICT"):
            self.preflight(table,exact=different)
        with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                    "LEVELS_AND_TRACK_MUST_BE_PAIRED"):
            self.preflight(None)

    def test_existing_normal_build_entry_passes_rows_and_user_manual_T(self):
        catalog, table, _ = prepared()
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            source=root/"v213.json"
            source.write_text("{}",encoding="utf8")
            user={"target":{"ilevel":334,"final_T":3300}}
            with mock.patch.object(build.environment_manifest,"read_json",
                                   return_value=(catalog,"a"*64)), \
                 mock.patch.object(build,"preflight_new_season_source",
                                   return_value={"preflight_sha256":"9"*64}) as pf:
                with self.assertRaisesRegex(
                        build.EnvironmentBuildBlocked,
                        "FRESH_SOURCE_PROVENANCE_PASS_GJFO_NOT_READY"):
                    build.build_environment(
                        sessions_root=root/"sessions",
                        session_folder=root/"sessions"/("0"*20),
                        user=user,binary=root/"simc",
                        revision=catalog["simc_revision"],
                        static_cache=root/"cache",
                        source_catalog_path=source,bootstrap_result={},
                        expected_new_season_build=catalog["game_build"],
                        fresh_standard_budget_evidence_by_ilevel=table,
                        fresh_standard_budget_reference_track="ordinary_two_hand")
            self.assertEqual(pf.call_count,1)
            kwargs=pf.call_args.kwargs
            self.assertIs(kwargs["standard_budget_evidence_by_ilevel"],table)
            self.assertEqual(kwargs["standard_budget_reference_track"],
                             "ordinary_two_hand")
            self.assertEqual(kwargs["target_ilevel"],334)
            self.assertEqual(kwargs["manual_final_T"],3300)
            self.assertFalse((root/"sessions").exists())


if __name__=="__main__":
    unittest.main()
