"""Offline tests for read-only selected-item v163/v274/v216 audit."""
import json
import os
import tempfile
import unittest
from pathlib import Path

from integration_probes.p1_v366_existing_source_gap_report import (
    DiagnosticInputError, read_existing_json, summarize_gap)


class SelectedSourceGapTest(unittest.TestCase):
    def setUp(self):
        self.v163 = {
            "schema": "v163_zero_seed_db2_join_v1",
            "build": "12.1.5.70783", "db2_display_season_id": 37,
            "wcl_zone_ids": {"raid": 53, "mplus": 46},
            "unverified_world_state_expressions": True,
            "items": [
                {"item_id": 1001, "acquisition_sources": [
                    {"source": "raid_journal", "world_state_expression_id": 52104,
                     "display_season_id": 37,
                     "season_evidence": "UNKNOWN_WORLD_STATE_EXPRESSION",
                     "credential_token": "SECRET_SHOULD_NEVER_APPEAR"}]},
                {"item_id": 1002, "acquisition_sources": [
                    {"source": "mplus_journal", "world_state_expression_id": 0,
                     "display_season_id": 37,
                     "season_evidence": "DB2_DISPLAY_SEASON_MATCH"}]},
                {"item_id": 1003, "acquisition_sources": [
                    {"source": "selectable_stat_craft", "expansion_id": 11,
                     "classification": "PROVISIONAL_SIMC_BATCH_REVIEW"}]},
            ]}

    def test_distinguishes_positive_wse_zero_candidate_absence(self):
        result = summarize_gap(self.v163, [1001, 1002, 1003, 9999])
        rows = result["selected_equipment"]
        self.assertEqual(rows[0]["uninterpreted_positive_world_state_ids"], [52104])
        self.assertEqual(rows[1]["uninterpreted_positive_world_state_ids"], [])
        self.assertTrue(rows[2]["v163_candidate_present"])
        self.assertFalse(rows[3]["v163_candidate_present"])
        self.assertTrue(all(row["season_membership_verified"] is False for row in rows))
        self.assertFalse(result["environment_ready"])
        self.assertNotIn("SECRET_SHOULD_NEVER_APPEAR", json.dumps(result))

    def test_compiler_missing_is_not_season_join_proof(self):
        compilation = {"schema":
            "v274_v216_collected_to_v241_fresh_compile_inputs_v1",
            "status": "COLLECTED_COMPILER_INPUTS_PENDING",
            "missing": ["TIER_V168", "PINNED_SIMC_REVISION"]}
        progress = {"schema": "v216_zero_history_normal_build_progress_v1",
                    "requires": ["SOURCE_SEASON_JOIN_PENDING",
                                 "HIGHEST_QUALITY_FLASK_F_SOURCE_PENDING"]}
        result = summarize_gap(self.v163, [1002],
                               compilation=compilation, progress=progress)
        self.assertEqual(result["v274_compiler_input_files_missing"],
                         ["TIER_V168", "PINNED_SIMC_REVISION"])
        self.assertIn("SOURCE_SEASON_JOIN_PENDING", result["v216_stage_requirements"])
        self.assertFalse(result["season_membership_verified"])
        self.assertTrue(result["compiler_missing_is_not_season_membership_evidence"])
        self.assertEqual(result["new_native_calls"], 0)
        self.assertEqual(result["new_network_calls"], 0)

    def test_invalid_inputs_block_without_reclassification(self):
        for ids in ([], [0], [-1], [1, 1], list(range(1, 66))):
            with self.assertRaises(DiagnosticInputError):
                summarize_gap(self.v163, ids)
        with self.assertRaises(DiagnosticInputError):
            summarize_gap({"schema": "incorrect", "items": []}, [1])

    def test_unexpected_source_text_is_not_redisclosed(self):
        row = self.v163["items"][0]["acquisition_sources"][0]
        row["season_evidence"] = "Bearer SECRET_WSE"
        row["classification"] = {"Bearer": "SECRET_CLASS"}
        self.v163["build"] = "Bearer SECRET_BUILD"
        self.v163["db2_display_season_id"] = {"password": "SECRET_DB2"}
        self.v163["unverified_world_state_expressions"] = "SECRET_WSE_FLAG"
        result = summarize_gap(
            self.v163, [1001],
            compilation={"schema":
                "v274_v216_collected_to_v241_fresh_compile_inputs_v1",
                "missing": ["SECRET_COMPILER_INPUT"]},
            progress={"schema": "v216_zero_history_normal_build_progress_v1",
                      "requires": ["Authorization: SECRET_TOKEN"]})
        self.assertNotIn("SECRET", json.dumps(result))
        self.assertEqual(result["v274_unrecognized_missing_count"], 1)
        self.assertEqual(result["v216_other_requirement_count"], 1)
        self.assertFalse(result["environment_ready"])

    def test_read_existing_json_sha_no_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/"source.json"
            p.write_text(json.dumps(self.v163), encoding="utf8")
            before = p.read_bytes()
            doc, sha = read_existing_json(str(p))
            self.assertEqual(doc, self.v163)
            self.assertEqual(len(sha), 64)
            self.assertEqual(p.read_bytes(), before)
            if hasattr(os, "symlink"):
                q = Path(temp)/"link.json"
                try:
                    os.symlink(p, q)
                except (OSError, NotImplementedError):
                    return
                with self.assertRaises(DiagnosticInputError):
                    read_existing_json(str(q))


if __name__ == "__main__":
    unittest.main()
