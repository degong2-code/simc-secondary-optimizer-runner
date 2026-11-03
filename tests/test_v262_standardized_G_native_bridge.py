"""Synthetic v234 static G observation -> v222 aggregate rounding, no Native."""
import json
import unittest
from unittest import mock

from runner import v234_source_only_one_native_G as native
from runner import v222_season_budget_contract as budget


class StandardizedGNativeBridgeTests(unittest.TestCase):
    def test_existing_native_parser_total_produces_one_rounded_reference(self):
        slots={
            "head":101,"neck":102,"shoulders":103,"back":104,
            "chest":105,"wrists":106,"hands":107,"waist":108,
            "legs":109,"feet":110,"finger1":111,"finger2":112,
            "main_hand":113,
        }
        receipt={
            "schema":native.compiler.SCHEMA,
            "environment_ready":False,"G":None,"native_calls":0,
            "simc_revision":"a"*40,
            "game_build_declared_by_simc_source":"12.1.5.70575",
            "selected_G_slot_ids":slots,
            "target_ilevel":334,
            "source_candidate_receipt_sha256":"b"*64,
            "class":"paladin","spec":"retribution",
            "generic_G_physical_conditions_verified":True,
            "generic_G_current_season_membership_required":False,
        }
        receipt["receipt_sha256"]=native.seed.digest(native.seed.canonical(
            receipt).encode("utf8"))
        records=[]
        for slot,itemid in slots.items():
            records.append({
                "observed_slot":slot,
                "identity":{"item_id":itemid,"ilevel":334,"options":{}},
                "modifiers_present":False,
                "metadata":{"item_db_source":"local"},
            })
        vector={name:0 for name in native.static.STATS}
        vector[native.static.STATS[0]]=2847
        raw=json.dumps({"git_revision":"a"*12}).encode("utf8")
        with mock.patch.object(native.static,"native_records",
                               return_value=records) as parser, \
             mock.patch.object(native.static,"empty_cache",
                               return_value={}), \
             mock.patch.object(native.static,"merge_native"), \
             mock.patch.object(native.static,"selected_gear_sum",
                               return_value={
                                    "G_vector":vector,
                                    "G_native_static_including_selected_modifiers":
                                        2847}):
            result=native.observe(
                native_raw=raw,profile_receipt=receipt,
                native_binary_sha256="c"*64,
                executed_profile_sha256="d"*64)
        parser.assert_called_once()
        meta=result["standardized_G_preview_unapproved"]
        self.assertEqual(meta["standardized_G"],2850)
        self.assertEqual(meta["observed_G_total"],2847)
        self.assertEqual(meta["rounding_delta"],3)
        self.assertEqual(meta["source_observation_sha256"],
                         result["native_json2_sha256"])
        self.assertEqual(meta["schema"],budget.G_ROUNDING_SCHEMA)
        self.assertEqual(result["observed_G_total"],2847)
        self.assertIsNone(result["G"])
        self.assertFalse(result["full_G_approved"])
        self.assertFalse(result["source_current_season_membership_verified"])
        self.assertTrue(result["generic_G_numeric_reference_usable"])
        self.assertFalse(result["generic_G_current_season_membership_required"])
        self.assertFalse(result["environment_ready"])
        self.assertEqual(result["new_native_calls_by_observer"],0)

    def test_unapproved_native_preview_is_not_budget_source_verification(self):
        with self.assertRaisesRegex(budget.SeasonBudgetBlocked,
                                    "SOURCE_VERIFICATION_MISSING"):
            catalog={"game_build":"12.1.5.70575",
                     "simc_revision":"a"*40,
                     "manifest_sha256":"b"*64}
            from tests.test_v222_season_budget_contract import fixture
            _, proof, _ = fixture()
            proof["simc_revision"]="a"*40
            proof["components"]["G"]["source_verification"]="OBSERVED_ONLY"
            meta=budget.standardize_representative_G(
                observed_G_total=2847,target_ilevel=334,
                source_observation_sha256=proof["components"]["G"]["source_sha256"])
            proof["components"]["G"].update(
                rating=meta["standardized_G"],standardization=meta)
            budget.preprofile_budget(
                source_catalog=catalog,source_artifact_sha256="a"*64,
                evidence=proof,target_ilevel=334)


if __name__=="__main__":
    unittest.main()
