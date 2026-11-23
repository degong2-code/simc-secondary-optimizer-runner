"""v684 actual-source diagnostic receipt contracts, purely synthetic/offline.

The production v216 is patched at the single call boundary. These tests
do NOT fetch Wago/SimC, install a season, or run any Native/DPS work.
"""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"runner"),str(ROOT/"integration_probes")]

import p1_v684_real_optional_source_onebuild_once as diagnostic


def row(item_id, *, kind="food", token=None, effect=None, quality=3):
    return {"kind":kind,"physical_item_id":item_id,
            "simc_input_token":token or "food_"+str(item_id)+"_3",
            "crafting_quality":quality,
            "effect_identity":effect or "simc:handler:spell:"+str(item_id),
            "use_condition_identity":"wago_on_use_0",
            "name_enUS":"Synthetic Item "+str(item_id)}


def original_result(rows=None, *, native_calls=0, include_bridge=True):
    if rows is None:
        rows=[row(101),row(102,kind="potion",token="potion_102_3")]
    source={"game_build":diagnostic.BUILD,
            "simc_revision":diagnostic.REV,
            "source_receipt_sha256":"b"*64,
            "rows":rows}
    compilation={"status":"FRESH_V191_V211_V213_COMPILED_UNADMITTED",
                 "missing":["J_GEM_SOURCE_PENDING"]}
    if include_bridge:
        compilation["source_owned_optional_consumables"]=source
    return {
        "source_compilation":compilation,
        "fresh_food_potion_item_sources":{
            "status":"FRESH_FOOD_POTION_FLASK_ENHANCEMENT_DB2_CANDIDATES_NOT_USER_ADMITTED",
            "food_item_count":2,"potion_item_count":1},
        "fresh_optional_food_potion_wago_effects":{
            "status":"FOOD_POTION_WAGO_USE_SPELLS_SOURCE_READY",
            "food_item_count":2,"potion_item_count":1,
            "source_stage":{"receipt_sha256":"a"*64}},
        "fresh_lazy_full_pinned_simc_item_source":{
            "status":"PINNED_SOURCE_SEALED",
            "source_dir":"fixture-only-never-read",
            "receipt_sha256":"c"*64},
        "native_calls":native_calls}


class V684OneBuildReceiptTests(unittest.TestCase):
    def invoke(self,result,*,has_credentials=True):
        with tempfile.TemporaryDirectory(prefix="v684-receipt-test-") as td:
            with mock.patch.object(
                    diagnostic.EphemeralActionsCredentials,"load",
                    return_value=({"test":"present"} if has_credentials
                                  else None)),mock.patch.object(
                    diagnostic.original,"build_environment",
                    return_value=result) as builder:
                status=diagnostic.observe(td)
            doc=json.loads((pathlib.Path(td)/
                "V684_ONE_BUILD_OPTIONAL_SOURCE_ONLY.json").read_text("utf8"))
            return status,doc,builder

    def test_real_owner_contract_is_called_once_with_no_native(self):
        status,doc,builder=self.invoke(original_result())
        self.assertEqual(status,0)
        self.assertEqual(doc["status"],
                         "PASS_REAL_V216_SOURCE_TO_V212_OPTION_PROJECTION")
        self.assertEqual(doc["simc_wago_joined_rows"],2)
        self.assertEqual(doc["v212_selectable_option_count"],2)
        self.assertEqual(doc["v212_source_only_projection"]["food"][
                             "option_count"],1)
        self.assertEqual(doc["v212_source_only_projection"]["potion"][
                             "option_count"],1)
        self.assertTrue(doc["source_only_not_installed"])
        self.assertFalse(doc["actual_parser_native_accepted"])
        self.assertEqual(doc["native_calls_reported"],0)
        builder.assert_called_once()
        call=builder.call_args.kwargs
        self.assertIsNone(call["binary"])
        self.assertIsNone(call["revision"])
        self.assertIsNone(call["session_folder"])
        options=call["fresh_collection_inputs"]
        self.assertEqual(options["expected_game_build"],diagnostic.BUILD)
        self.assertEqual(options["simc_revision_hint"],diagnostic.REV)
        for flag in ("auto_native_G_requested","auto_native_F_requested",
                     "auto_native_O_requested"):
            self.assertIs(options[flag],False)
        self.assertNotIn("fetch",options)
        self.assertNotIn("same_build_budget_evidence",options)

    def test_multiple_joined_rows_but_zero_user_choices_are_pending(self):
        # v212 correctly rejects an equal-quality same-effect tie. A nonzero
        # Wago/SimC join is NOT proof that the menu has options.
        two=[row(111,token="food_equal_a_3",effect="simc:same"),
             row(112,token="food_equal_b_3",effect="simc:same")]
        status,doc,_=self.invoke(original_result(two))
        self.assertEqual(status,2)
        self.assertEqual(doc["simc_wago_joined_rows"],2)
        self.assertEqual(doc["v212_selectable_option_count"],0)
        self.assertEqual(doc["status"],
                         "PENDING_ALL_WAGO_SIMC_OPTIONS_WITHHELD_BY_V212")
        self.assertEqual(doc["v212_source_only_projection"]["food"][
                             "status"],"SOURCE_OPTIONS_UNAVAILABLE")
        self.assertTrue(doc["source_only_not_installed"])

    def test_no_joined_rows_and_missing_bridge_are_not_success(self):
        status,doc,_=self.invoke(original_result([]))
        self.assertEqual(status,2)
        self.assertEqual(doc["status"],"PENDING_NO_WAGO_SIMC_JOINED_ROWS")
        status,doc,_=self.invoke(
            original_result([],include_bridge=False))
        self.assertEqual(status,2)
        self.assertEqual(doc["status"],"PENDING_ORIGINAL_V680_SOURCE_JOIN")
        self.assertIsNotNone(doc["first_blocker"])

    def test_native_violation_and_absent_credentials_fail_closed(self):
        status,doc,_=self.invoke(original_result(native_calls=1))
        self.assertEqual(status,2)
        self.assertEqual(doc["status"],"BLOCKED_REAL_V216_OPTIONAL_SOURCE")
        self.assertEqual(doc["first_blocker"],
                         "V684_SOURCE_ONLY_UNEXPECTED_NATIVE")
        status,doc,builder=self.invoke(original_result(),
                                        has_credentials=False)
        self.assertEqual(status,2)
        self.assertEqual(doc["status"],
                         "PENDING_EXISTING_ACTIONS_SOURCE_CREDENTIALS")
        builder.assert_not_called()


if __name__=="__main__":
    unittest.main()
