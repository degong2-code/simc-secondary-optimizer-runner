"""v227 existing v046 Native item cache reuse, without J/F carryover or trust inflation."""
from __future__ import annotations
import copy
import json
import pathlib
import tempfile
import unittest

from runner import v046_static_item_cache as native_cache
from runner import v226_representative_native_g_work_order as planner
from runner import v227_cached_native_g_observation as observe
from tests.test_v226_representative_native_g_work_order import (
    RepresentativeGWorkOrderTests)


class CachedGObservationTests(unittest.TestCase):
    def setUp(self):
        self.provider=RepresentativeGWorkOrderTests()
        self.provider.setUp()
        self.addCleanup(self.provider.provider.tmp.cleanup)
        self.work=self.provider.plan()
        self.cache=native_cache.empty_cache(self.work["season"])

    def fill(self):
        for i,(slot,item_id) in enumerate(sorted(
                self.work["selected_source_slots"].items())):
            identity={
                "season": self.work["season"],
                "slot": native_cache.normalize_slot(slot),
                "item_id": item_id,
                "ilevel": self.work["target_ilevel"],
                "options": {},
            }
            vector=dict.fromkeys(native_cache.STATS,0)
            vector["crit_rating"]=i+1
            vector["haste_rating"]=2*(i+1)
            static={"secondary":vector,"primary_other":{},
                    "weapon_if_native":{}}
            record={
                "identity":identity,
                "static":static,
                "static_digest":native_cache.digest(static),
                "source_kind":"NATIVE_JSON2_RESOLVED_VARIANT",
                "modifiers_present":False,
                "eligible_for_gear_sum_only_in_exact_same_variant":True,
                "metadata":{
                    "native_json_sha256":"f"*64,
                    "native_revision":"a"*40,
                },
            }
            self.cache["variants"][native_cache.digest(identity)]=record

    def test_empty_cache_never_makes_missing_G_zero(self):
        result=observe.observe(work_order=self.work,cache=self.cache)
        self.assertEqual(result["status"],"WAIT_EXACT_NATIVE_STATIC_VARIANTS")
        self.assertEqual(len(result["missing_variant_requests"]),13)
        self.assertIsNone(result["observed_G_total_if_complete"])
        self.assertIsNone(result["G"])
        self.assertEqual(result["native_calls"],0)

    def test_exact_records_sum_four_stat_G_and_ignore_historical_JF(self):
        self.fill()
        result=observe.observe(work_order=self.work,cache=self.cache)
        n=len(self.work["selected_source_slots"])
        total=3*n*(n+1)//2
        self.assertEqual(result["observed_G_total_if_complete"],total)
        self.assertEqual(result["observed_G_vector_if_complete"][
            "crit_rating"],n*(n+1)//2)
        self.assertEqual(result["observed_G_vector_if_complete"][
            "haste_rating"],n*(n+1))
        self.assertIsNone(result["G"])
        self.assertIsNone(result["J"])
        self.assertIsNone(result["F"])
        self.assertIsNone(result["B"])
        self.assertIsNone(result["T"])
        self.assertFalse(result["environment_ready"])
        self.assertIn("V046_ITEM_CACHE_DOES_NOT_ATTEST_GAME_BUILD_BY_VARIANT",
                      result["why_G_not_approved"])

    def test_missing_exact_variant_is_request_not_implicit_zero(self):
        self.fill()
        key=next(iter(self.cache["variants"]))
        record=self.cache["variants"].pop(key)
        result=observe.observe(work_order=self.work,cache=self.cache)
        self.assertEqual(result["exact_native_cache_variants_found"],12)
        self.assertEqual(len(result["missing_variant_requests"]),1)
        self.assertEqual(result["missing_variant_requests"][0]["item_id"],
                         record["identity"]["item_id"])
        self.assertIsNone(result["observed_G_total_if_complete"])

    def test_different_ilvl_never_reuses_old_static_variants(self):
        self.fill()
        different=self.provider.plan(ilevel=336)
        result=observe.observe(work_order=different,cache=self.cache)
        self.assertEqual(len(result["missing_variant_requests"]),13)

    def test_wrong_season_and_native_metadata_are_blocked(self):
        self.fill()
        wrong=native_cache.empty_cache("different_season")
        with self.assertRaisesRegex(observe.GObservationBlocked,
                                    "STATIC_CACHE_SEASON_DRIFT"):
            observe.observe(work_order=self.work,cache=wrong)
        record=next(iter(self.cache["variants"].values()))
        record["metadata"].pop("native_json_sha256")
        with self.assertRaisesRegex(observe.GObservationBlocked,
                                    "NATIVE_ORIGIN_RECORD_INCOMPLETE"):
            observe.observe(work_order=self.work,cache=self.cache)

    def test_mutated_static_value_cache_fails_provenance(self):
        self.fill()
        record=next(iter(self.cache["variants"].values()))
        record["static"]["secondary"]["crit_rating"]+=1
        with self.assertRaisesRegex(observe.GObservationBlocked,
                                    "EXISTING_V046_CACHE_INVALID"):
            observe.observe(work_order=self.work,cache=self.cache)

    def test_revision_independence_and_work_id(self):
        self.fill()
        first=observe.observe(work_order=self.work,cache=self.cache)
        for record in self.cache["variants"].values():
            record["metadata"]["native_revision"]="b"*40
        second=observe.observe(work_order=self.work,cache=self.cache)
        self.assertEqual(first["work_identity_sha256"],
                         second["work_identity_sha256"])
        self.assertEqual(first["observed_G_total_if_complete"],
                         second["observed_G_total_if_complete"])

    def test_tampered_work_order_cannot_use_exact_cache(self):
        self.fill()
        changed=copy.deepcopy(self.work)
        changed["selected_source_slots"]["main_hand"]=99999999
        with self.assertRaisesRegex(observe.GObservationBlocked,
                                    "WORK_ORDER_SHA_DRIFT"):
            observe.observe(work_order=changed,cache=self.cache)

    def test_json_receipt_is_deterministic_without_native(self):
        self.fill()
        first=observe.observe(work_order=self.work,cache=self.cache)
        second=observe.observe(work_order=self.work,cache=self.cache)
        self.assertEqual(first,second)
        self.assertEqual(first["receipt_sha256"],
                         planner.digest({k:v for k,v in first.items()
                                        if k!="receipt_sha256"}))
        self.assertEqual(first["cache_mutations"],0)


if __name__=="__main__":
    unittest.main()
