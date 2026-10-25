"""v077 synthetic-only generic readiness checks. No Native success assertions."""
import copy
import json
import pathlib
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v046_static_item_cache as cache
import v077_generic_profile_bootstrap_readiness as v077
from test_v066_profile_neutral_preflight import fixture

class GenericFirstUseReadiness(unittest.TestCase):
    def test_complete_synthetic_cache_generates_two_distinct_unchanged_total(self):
        cfg,fill,existing,profile,_=fixture()
        with tempfile.TemporaryDirectory() as d:
            plan=v077.prepare(cfg,fill,existing,profile,pathlib.Path(d))
        self.assertEqual(plan["status"],"READY_FOR_TWO_NATIVE_CALIBRATION_WITNESSES")
        self.assertEqual(plan["new_native_calls"],0)
        self.assertFalse(plan["native_success_claimed"])
        self.assertEqual(plan["missing_exact_native_variant_count"],0)
        w=plan["two_native_witness_inputs"]
        self.assertEqual(len(w),2)
        self.assertNotEqual(w[0]["input_sha256"],w[1]["input_sha256"])
        self.assertEqual(w[0]["stable_profile_sha256"],w[1]["stable_profile_sha256"])
        self.assertEqual(sum(w[0]["raw_rating"].values()),
                         sum(w[1]["raw_rating"].values()))
        self.assertTrue(plan["full_native_static_binding"]["two_trinkets_bound"])

    def test_another_synthetic_class_is_not_native_acceptance(self):
        cfg,fill,existing,profile,_=fixture("warrior","arms","attack")
        with tempfile.TemporaryDirectory() as d:
            plan=v077.prepare(cfg,fill,existing,profile,pathlib.Path(d))
        self.assertEqual(plan["class"],"warrior")
        self.assertEqual(plan["status"],"READY_FOR_TWO_NATIVE_CALIBRATION_WITNESSES")
        self.assertFalse(plan["native_success_claimed"])
        self.assertFalse(plan["numeric_offset_known"])

    def test_missing_exact_nontrinket_is_explicit_and_never_guessed(self):
        cfg,fill,existing,profile,_=fixture()
        empty=cache.empty_cache()
        with tempfile.TemporaryDirectory() as d:
            plan=v077.prepare(cfg,fill,empty,profile,pathlib.Path(d))
        self.assertEqual(plan["status"],"BLOCKED_EXACT_NATIVE_STATIC_VARIANTS_MISSING")
        self.assertGreater(plan["missing_exact_native_variant_count"],0)
        self.assertIsNone(plan["G_native_if_complete"])
        self.assertEqual(plan["new_native_calls"],0)

    def test_wrong_exact_item_id_rejected_before_native(self):
        cfg,fill,existing,profile,_=fixture()
        changed=profile.replace("id=250224","id=250244",1)
        self.assertNotEqual(changed,profile)
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(v077.ReadinessBlocked,
                                        "EXACT_ITEM_VARIANT_MISMATCH"):
                v077.prepare(cfg,fill,existing,changed,pathlib.Path(d))

    def test_bad_character_variant_refused(self):
        cfg,fill,existing,profile,_=fixture()
        bad=copy.deepcopy(cfg)
        bad["character"]["race"]="troll"
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(v077.ReadinessBlocked,
                                        "PROFILE_CHARACTER_DRIFT:race"):
                v077.prepare(bad,fill,existing,profile,pathlib.Path(d))

    def test_two_sources_keep_ratings_in_budget_sum_even_before_offset(self):
        cfg,fill,existing,profile,_=fixture()
        with tempfile.TemporaryDirectory() as d:
            cases=v077.paired_input(profile,pathlib.Path(d))
        self.assertEqual(len(cases),2)
        self.assertEqual(sum(cases[0]["raw_rating"].values()),
                         sum(cases[1]["raw_rating"].values()))
        self.assertEqual(cases[0]["iterations"],35)
        self.assertEqual(cases[1]["iterations"],35)

    def test_insufficient_raw_donor_fails_closed(self):
        cfg,fill,existing,profile,_=fixture()
        import re
        bad=re.sub(r"(?m)^gear_(crit|haste|mastery|versatility)_rating=\d+$",
                   lambda m: m.group(0).split("=")[0]+"=0", profile)
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(v077.ReadinessBlocked,
                                        "NO_GEARRATING_DONOR"):
                v077.paired_input(bad,pathlib.Path(d))

if __name__=="__main__":
    unittest.main()
