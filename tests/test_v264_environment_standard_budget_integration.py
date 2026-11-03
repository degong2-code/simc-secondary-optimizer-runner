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
                  track="ordinary_two_hand", exact=None,
                  native_paths=None):
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
                    budget_evidence=exact,
                    g_native_receipt_paths_by_ilevel=native_paths)

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

    def test_reuses_real_v234_receipt_schema_once_without_native_or_JFO_guess(self):
        catalog, table, _ = prepared()
        def receipt_for(level):
            component=table[level]["components"]["G"]
            observed={
                "schema":"v234_one_source_only_physical_native_G_observation_v1",
                "source_simc_revision":catalog["simc_revision"],
                "game_build_from_source_not_independently_binary_attested":
                    catalog["game_build"],
                "target_ilevel":level,
                "observed_G_total":
                    component["standardization"]["observed_G_total"],
                "native_json2_sha256":component["source_sha256"],
                "standardized_G_preview_unapproved":
                    component["standardization"],
                "source_profile_receipt_sha256":"f"*64,
                "full_G_approved":False,
                "environment_ready":False,
            }
            observed["receipt_sha256"]=build.digest(
                build.canonical(observed).encode("utf8"))
            return {
                "status":"PASS_NATIVE_PHYSICAL_G_OBSERVED_NOT_SEASON_APPROVED",
                "native_returncode":0,"new_native_calls":1,
                "environment_ready":False,
                "identity":{"source_game_build":catalog["game_build"]},
                "native_json2_sha256":observed["native_json2_sha256"],
                "observed_G":observed,
            }
        with tempfile.TemporaryDirectory() as temp:
            base=pathlib.Path(temp)
            paths={}
            for level in table:
                path=base/f"native_{level}.json"
                path.write_text(__import__("json").dumps(receipt_for(level)),
                                encoding="utf8")
                paths[level]=path
            result=self.preflight(table,native_paths=paths)
            rows=result["measured_ilevel_G_from_existing_native_unadmitted"]
            self.assertEqual([x["target_ilevel"] for x in rows],[334,335])
            self.assertEqual([x["standardization"]["standardized_G"]
                              for x in rows],[2850,2850])
            self.assertEqual([x["native_json2_sha256"] for x in rows],
                             [table[k]["components"]["G"]["source_sha256"]
                              for k in sorted(table)])
            self.assertFalse(result["environment_ready"])
            self.assertIsNone(result["G"])
            self.assertEqual(result["native_calls"],0)
            # If highest-quality J/F/O is not established, only G is shown.
            just_g=self.preflight(None,level=None,track=None,
                                  native_paths=paths)
            self.assertNotIn("standardized_ilevel_budget_rows_unadmitted",
                             just_g)
            self.assertEqual(len(just_g[
                "measured_ilevel_G_from_existing_native_unadmitted"]),2)
            self.assertIsNone(just_g["B"])
            broken=receipt_for(334)
            broken["observed_G"]["observed_G_total"]=1
            paths[334].write_text(__import__("json").dumps(broken),
                                  encoding="utf8")
            with self.assertRaisesRegex(
                    build.EnvironmentBuildBlocked,
                    "EXISTING_G_NATIVE_RECEIPT_INVALID"):
                self.preflight(table,native_paths=paths)

    def test_v234_receipt_and_budget_G_disagreement_is_not_silently_accepted(self):
        catalog, table, _ = prepared()
        proof=table[334]["components"]["G"]
        native={
            "schema":"v234_one_source_only_physical_native_G_observation_v1",
            "source_simc_revision":catalog["simc_revision"],
            "game_build_from_source_not_independently_binary_attested":
                catalog["game_build"],
            "target_ilevel":334,
            "observed_G_total":2847,
            "native_json2_sha256":"4"*64,
            "standardized_G_preview_unapproved":
                budget.standardize_representative_G(
                    observed_G_total=2847,target_ilevel=334,
                    source_observation_sha256="4"*64),
            "source_profile_receipt_sha256":"f"*64,
            "full_G_approved":False,"environment_ready":False,
        }
        native["receipt_sha256"]=build.digest(
            build.canonical(native).encode("utf8"))
        outer={
            "status":"PASS_NATIVE_PHYSICAL_G_OBSERVED_NOT_SEASON_APPROVED",
            "native_returncode":0,"new_native_calls":1,
            "environment_ready":False,
            "identity":{"source_game_build":catalog["game_build"]},
            "native_json2_sha256":"4"*64,
            "observed_G":native,
        }
        with tempfile.TemporaryDirectory() as temp:
            path=pathlib.Path(temp)/"native.json"
            path.write_text(__import__("json").dumps(outer),encoding="utf8")
            with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                        "G_NATIVE_V222_OBSERVATION_DRIFT"):
                self.preflight({334:table[334]},native_paths={334:path})
            self.assertNotEqual(proof["source_sha256"],
                                native["native_json2_sha256"])

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
                        fresh_standard_budget_reference_track="ordinary_two_hand",
                        fresh_g_native_receipt_paths_by_ilevel={334:source})
            self.assertEqual(pf.call_count,1)
            kwargs=pf.call_args.kwargs
            self.assertIs(kwargs["standard_budget_evidence_by_ilevel"],table)
            self.assertEqual(kwargs["standard_budget_reference_track"],
                             "ordinary_two_hand")
            self.assertEqual(kwargs["target_ilevel"],334)
            self.assertEqual(kwargs["manual_final_T"],3300)
            self.assertEqual(kwargs["g_native_receipt_paths_by_ilevel"],
                             {334:source})
            self.assertFalse((root/"sessions").exists())


if __name__=="__main__":
    unittest.main()
