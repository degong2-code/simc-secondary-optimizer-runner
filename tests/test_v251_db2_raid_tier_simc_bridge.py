"""No-name DB2/raid tier identity bridge into exact SimC v231 candidates."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from runner import v250_raid_tier_bonus_corroboration as v250
from runner import v251_db2_raid_tier_simc_bridge as bridge
from tests.test_v250_raid_tier_bonus_corroboration import (
    inputs,raid_scope,source_rows,BUILD)

def fixture(root):
    tier,raid=inputs(root)
    corroboration=v250.correlate(tier=tier,raid=raid,
                                  source_bytes=source_rows())
    return tier,corroboration

class DB2SimCBridgeTests(unittest.TestCase):
    def test_13_classes_65_pieces_precise_candidate_without_season_promotion(self):
        with tempfile.TemporaryDirectory() as d:
            tier,bonus=fixture(d)
            result=bridge.preview(db2=tier,corroboration=bonus)
            self.assertEqual(result["class_count"],13)
            self.assertEqual(result["piece_count"],65)
            self.assertEqual(result["observed_base_item_level"],219)
            self.assertEqual(result["game_build"],BUILD)
            self.assertEqual(result["raid_bonus_overlap_count"],2)
            self.assertEqual(result["status"],
                "OBSERVED_CURRENT_RAID_CORRELATED_65_PIECE_TIER_CANDIDATE")
            self.assertFalse(result["season_membership_verified"])
            self.assertFalse(result["simc_source_verified"])
            self.assertFalse(result["production_profile_promoted"])
            self.assertIsNone(result["G"])
            self.assertIsNone(result["B"])
            self.assertIsNone(result["T"])
            self.assertEqual(result["native_calls"],0)
            self.assertEqual(result["network_calls"],0)
            ids={iid for x in result["classes"].values()
                    for iid in x["tier_piece_ids"].values()}
            self.assertEqual(len(ids),65)
            self.assertTrue(all(x["four_piece_slots"]==
                ["head","shoulders","hands","legs"]
                and x["simc_set_option"] is None for x in result["classes"].values()))

    def test_ambiguous_or_modified_observed_cohort_cannot_emit_65_items(self):
        with tempfile.TemporaryDirectory() as d:
            tier,bonus=fixture(d)
            bonus["status"]="RAID_BONUS_TIER_COHORT_AMBIGUOUS_PENDING"
            with self.assertRaisesRegex(bridge.BridgeBlocked,
                                        "UNPROMOTED_SAME_BUILD"):
                bridge.preview(db2=tier,corroboration=bonus)
            (Path(d)/"second_fixture").mkdir()
            tier,bonus=inputs(Path(d)/"second_fixture")
            bonus=v250.correlate(tier=tier,raid=bonus,source_bytes=source_rows())
            tier["candidates"]=[x for x in tier["candidates"]
                                if x["class"]!="paladin"]
            with self.assertRaisesRegex(bridge.BridgeBlocked,
                                        "DB2_SOURCE_SET_CLASS_SLOT"):
                bridge.preview(db2=tier,corroboration=bonus)
            (Path(d)/"third_fixture").mkdir()
            tier,raid=inputs(Path(d)/"third_fixture")
            bonus=v250.correlate(tier=tier,raid=raid,source_bytes=source_rows())
            bonus["observed_leading_cohort"]["source_season_verified"]=True
            with self.assertRaisesRegex(bridge.BridgeBlocked,
                                        "UNIQUE_OBSERVED_RAID_COHORT"):
                bridge.preview(db2=tier,corroboration=bonus)

    def test_first_party_simc_exact_item_ids_discover_option_not_text(self):
        with tempfile.TemporaryDirectory() as d:
            tier,bonus=fixture(d)
            candidate=bridge.preview(db2=tier,corroboration=bonus)
            cls="paladin";spec="retribution";entry=candidate["classes"][cls]
            group={"class_id":2,"set_id":entry["item_set_id"],
                   "item_ids":list(entry["tier_piece_ids"].values()),
                   "observed_bonus_sizes":[2,4],
                   "set_opt":"opaque_token_without_name_match"}
            selected={"set_id":entry["item_set_id"],
                      "tier_piece_ids":entry["tier_piece_ids"],
                      "game_build":BUILD,"environment_ready":False,
                      "native_calls":0}
            with mock.patch.object(bridge.simc_tier,"read_receipt",
                        return_value=({"simc_generated_build":BUILD},
                                      {"candidate_groups":[group]})),\
                 mock.patch.object(bridge.simc_tier,"select",
                        return_value=selected) as selector:
                result=bridge.select_for_simc(
                    candidate=candidate,seed_directory=d,cls=cls,spec=spec)
            self.assertEqual(result["simc_set_option_discovered"],
                             "opaque_token_without_name_match")
            selector.assert_called_once_with(
                seed_directory=d,cls=cls,spec=spec,
                set_option="opaque_token_without_name_match")
            self.assertFalse(result["season_membership_verified"])
            self.assertFalse(result["production_profile_promoted"])
            self.assertFalse(result["environment_ready"])
            self.assertEqual(result["native_calls"],0)

    def test_simc_item_difference_or_wrong_build_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            tier,bonus=fixture(d)
            candidate=bridge.preview(db2=tier,corroboration=bonus)
            cls="paladin";spec="retribution";entry=candidate["classes"][cls]
            g={"class_id":2,"set_id":entry["item_set_id"],
               "item_ids":list(entry["tier_piece_ids"].values())[:-1]+[9999],
               "observed_bonus_sizes":[2,4],"set_opt":"untrusted"}
            with mock.patch.object(bridge.simc_tier,"read_receipt",
                return_value=({"simc_generated_build":BUILD},
                              {"candidate_groups":[g]})):
                with self.assertRaisesRegex(bridge.BridgeBlocked,
                                            "EXACT_ID_OPTION_NOT_UNIQUE"):
                    bridge.select_for_simc(
                        candidate=candidate,seed_directory=d,cls=cls,spec=spec)
            with mock.patch.object(bridge.simc_tier,"read_receipt",
                return_value=({"simc_generated_build":"12.3.0.99999"},
                              {"candidate_groups":[g]})):
                with self.assertRaisesRegex(bridge.BridgeBlocked,
                                            "SAME_BUILD_SIMC"):
                    bridge.select_for_simc(
                        candidate=candidate,seed_directory=d,cls=cls,spec=spec)
            with self.assertRaisesRegex(bridge.BridgeBlocked,
                                        "SUPPORTED_26_DPS"):
                bridge.select_for_simc(
                    candidate=candidate,seed_directory=d,cls=cls,spec="holy")

    def test_stage_cached_and_sealed(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d)
            tier,bonus=fixture(base)
            t=base/"tier.json";b=base/"bonus.json"
            t.write_text(json.dumps(tier),encoding="utf8")
            b.write_text(json.dumps(bonus),encoding="utf8")
            stage=base/"stage";stage.mkdir()
            opts=dict(stage_root=stage,db2_candidate_path=t,
                      bonus_candidate_path=b,
                      db2_receipt="a"*64,bonus_receipt="b"*64)
            first=bridge.build_stage(**opts)
            second=bridge.build_stage(**opts)
            self.assertEqual(first["source_stage"]["status"],
                             "EXECUTED_AND_SEALED")
            self.assertEqual(second["source_stage"]["status"],
                             "REUSED_VERIFIED")
            self.assertEqual(first["network_calls_by_stage"],0)
            self.assertEqual(second["network_calls_by_stage"],0)
            self.assertEqual(first["piece_count"],65)
            self.assertFalse(second["simc_source_verified"])
            self.assertFalse(first["environment_ready"])

if __name__=="__main__":
    unittest.main()
