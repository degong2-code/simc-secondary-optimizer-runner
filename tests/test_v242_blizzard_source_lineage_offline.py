"""A4: authenticated Blizzard index source owners, not item-stat ownership.

Only synthetic v155 reports and the real v217 stage engine. No network, DB2,
Native, past season ID, special item or equipment catalog is injected.
"""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v242_authenticated_season_source_stage as stage

def raw_report():
    index={}
    for i,key in enumerate(stage.BLIZZARD_INDEX_OWNERS):
        index[key]={
            "status":"HTTP_200",
            "data":{"current_season_id":None},
            "original_http_body":{
                "raw_response_sha256":("%064x" % (i+1)),
                "raw_response_bytes":100+i}}
    index["keystone_season_index"]["data"]["current_season_id"]=18
    return {
        "schema":stage.probe.SCHEMA,
        "mode":"LIVE_AUTHENTICATED_BOUNDED",
        "native_simc_calls":0,
        "item_catalog_generated":False,
        "season_loot_complete":False,
        "blizzard":{"requests":4,"endpoints":index},
        "wcl":{"requests":2,"status":"ZONES_WITH_JOURNAL_IDS_RETURNED"}}

class BlizzardSourceOwners(unittest.TestCase):
    def test_all_four_original_source_bodies_record_without_item_claim(self):
        lineage=stage.blizzard_source_lineage(raw_report())
        self.assertEqual(lineage["schema"],stage.SOURCE_LINEAGE_SCHEMA)
        self.assertTrue(lineage["blizzard_index_originals_verified"])
        self.assertEqual(set(lineage["indices"]),
                         set(stage.BLIZZARD_INDEX_OWNERS))
        self.assertEqual(lineage["indices"]["keystone_season_index"]
                         ["response_bytes"],100)
        self.assertTrue(all(row["status"]=="ORIGINAL_HTTP_BODY_SHA_OBSERVED"
                            for row in lineage["indices"].values()))
        self.assertEqual(lineage["selected_item_data_owner"],
                         "SAME_BUILD_WAGO_DB2_AND_PINNED_SIMC_DOWNSTREAM")
        self.assertFalse(lineage[
            "selected_item_id_and_stats_blizzard_proof_claimed"])
        self.assertFalse(lineage[
            "blizzard_item_detail_runtime_required_for_base"])
        self.assertFalse(lineage["optional_ko_name_missing_blocks_base"])
        self.assertFalse(lineage["current_season_membership_certified_here"])
        self.assertEqual(lineage["additional_blizzard_requests"],0)
        self.assertEqual(lineage["native_calls"],0)

    def test_partial_old_receipt_cannot_claim_four_original_hashes(self):
        report=raw_report()
        del report["blizzard"]["endpoints"]["keystone_period_index"][
            "original_http_body"]
        report["blizzard"]["endpoints"]["journal_instance_index"][
            "original_http_body"]["raw_response_sha256"]="not-a-digest"
        info=stage.blizzard_source_lineage(report)
        self.assertFalse(info["blizzard_index_originals_verified"])
        self.assertIsNone(info["indices"]["keystone_period_index"][
            "response_sha256"])
        self.assertIsNone(info["indices"]["journal_instance_index"][
            "response_sha256"])
        self.assertFalse(info["selected_item_id_and_stats_blizzard_proof_claimed"])
        self.assertFalse(stage.blizzard_source_lineage({})[
            "blizzard_index_originals_verified"])

    def test_v242_original_sealed_stage_reuses_without_recollecting(self):
        credentials={
            "BLIZZARD_CLIENT_ID":"blid",
            "BLIZZARD_CLIENT_SECRET":"private-bl-secret",
            "WCL_CLIENT_ID":"wclid",
            "WCL_CLIENT_SECRET":"private-wcl-secret"}
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(stage.probe,"run_probe",
                                   return_value=raw_report()) as fetch:
                first=stage.collect(stage_root=tmp,
                                    expected_game_build="13.0.0.88888",
                                    credentials=credentials)
            fetch.assert_called_once()
            self.assertTrue(first["blizzard_source_lineage"][
                "blizzard_index_originals_verified"])
            self.assertTrue(first["season_join_ready"])
            self.assertEqual(first["network_calls_by_stage"],8)
            self.assertEqual(first["native_calls"],0)
            with mock.patch.object(stage.probe,"run_probe",
                     side_effect=AssertionError("REUSED_SOURCE_NO_NETWORK")):
                second=stage.collect(stage_root=tmp,
                                     expected_game_build="13.0.0.88888",
                                     credentials=credentials)
            self.assertEqual(second["network_calls_by_stage"],0)
            self.assertTrue(second["blizzard_source_lineage"][
                "blizzard_index_originals_verified"])
            self.assertEqual(first["stage"]["receipt_sha256"],
                             second["stage"]["receipt_sha256"])
            receipt=pathlib.Path(first["source_report_path"]).read_text(
                encoding="utf8")
            self.assertNotIn(credentials["BLIZZARD_CLIENT_SECRET"],receipt)
            self.assertNotIn(credentials["WCL_CLIENT_SECRET"],receipt)
            self.assertNotIn("access_token",receipt)

    def test_missing_credentials_uses_existing_pending_contract(self):
        empty={key:"" for key in stage.FIELDS}
        result=stage.collect(stage_root="/nonexistent",
                             expected_game_build="13.0.0.88888",
                             credentials=empty)
        self.assertEqual(result["status"],
                         "AUTHENTICATED_SEASON_CREDENTIALS_MISSING")
        self.assertFalse(result["authenticated_provider_response"])
        self.assertFalse(result["current_season_membership_verified"])

if __name__=="__main__":
    unittest.main()
