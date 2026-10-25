"""v079 BM Hunter source-backed ranged/no-offhand cross-class smoke tests.

These are OFFLINE source/input tests; only GitHub real SimC Native can prove
DPS/json2 success.
"""
import json
import pathlib
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v079_hunter_ranged_generic_native as v079
import v061_scenario_contract as scenario
import v063_numeric_injection as numeric
import v077_generic_profile_bootstrap_readiness as readiness
import v046_static_item_cache as cache

UPSTREAM=ROOT/"integration_probes/fixtures/v079_upstream_mid2_hunter_beast_mastery_reference.simc"

class HunterRangedCrossClass(unittest.TestCase):
    def setUp(self):
        self.source=UPSTREAM.read_text("utf8")

    def test_actual_source_has_fifteen_gear_slots_no_offhand(self):
        with tempfile.TemporaryDirectory() as d:
            ref,cfg,fill,meta=v079.source_profile(self.source,d)
        self.assertEqual(len(v079.ALL_SLOTS),15)
        self.assertNotIn("off_hand=",ref)
        self.assertIn("main_hand=selected_268207,id=268207,ilevel=334",ref)
        self.assertEqual(cfg["character"]["class"],"hunter")
        self.assertEqual(cfg["character"]["spec"],"beast_mastery")
        self.assertEqual(cfg["character"]["race"],"troll")
        self.assertEqual(len(cfg["equipment"]["tier"]),4)
        self.assertEqual(len(cfg["equipment"]["crafted"]),2)
        self.assertEqual(len(cfg["equipment"]["trinkets"]),2)
        self.assertEqual(meta["weapon_type"],"ranged_no_offhand")

    def test_upstream_pet_and_apl_remain_exact(self):
        with tempfile.TemporaryDirectory() as d:
            ref,_,_,_=v079.source_profile(self.source,d)
        actions=lambda s:[x for x in s.splitlines() if x.startswith("actions")]
        self.assertEqual(actions(self.source),actions(ref))
        self.assertIn("actions.precombat=summon_pet",ref)

    def test_generic_v077_ready_gate_on_native_static_miss(self):
        with tempfile.TemporaryDirectory() as d:
            ref,cfg,fill,_=v079.source_profile(self.source,d)
            got=readiness.prepare(cfg,fill,cache.empty_cache(),ref,
                pathlib.Path(d)/"witnesses")
        self.assertEqual(got["status"],
                "BLOCKED_EXACT_NATIVE_STATIC_VARIANTS_MISSING")
        self.assertGreater(got["missing_exact_native_variant_count"],0)
        self.assertEqual(got["new_native_calls"],0)
        self.assertFalse(got["native_success_claimed"])

    def test_raw_witnesses_share_same_stable_gear_and_profile(self):
        with tempfile.TemporaryDirectory() as d:
            ref,cfg,fill,_=v079.source_profile(self.source,d)
            normalized=scenario.normalize(cfg)
            x=readiness.paired_input(ref,pathlib.Path(d)/"witnesses")
        self.assertEqual(normalized["scenario"]["target"]["ilevel"],334)
        self.assertEqual(len(x),2)
        self.assertNotEqual(x[0]["input_sha256"],x[1]["input_sha256"])
        self.assertEqual(x[0]["stable_profile_sha256"],
                         x[1]["stable_profile_sha256"])
        self.assertEqual(sum(x[0]["raw_rating"].values()),2800)
        self.assertEqual(sum(x[1]["raw_rating"].values()),2800)
        self.assertEqual(len(fill),7)

    def test_unexpected_offhand_and_gear_id_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            bad=self.source+"\noff_hand=unexpected,id=999999\n"
            with self.assertRaisesRegex(v079.Blocked,
                    "EXPECTED_UPSTREAM_RANGED_MAINHAND_CHANGED"):
                v079.source_profile(bad,d)
            bad2=self.source.replace(",id=268207",",id=999999",1)
            with self.assertRaisesRegex(v079.Blocked,
                    "EXPECTED_UPSTREAM_RANGED_MAINHAND_CHANGED"):
                v079.source_profile(bad2,d)

    def test_without_native_only_proposes_input_plan(self):
        with tempfile.TemporaryDirectory() as d:
            out=pathlib.Path(d)/"out"
            rc=v079.execute(UPSTREAM,out)
            self.assertEqual(rc,0)
            r=json.loads((out/"V079_RECEIPT.json").read_text())
        self.assertEqual(r["status"],"PASS_SOURCE_BACKED_RANGED_RAW_INPUT_PLAN_ZERO_NATIVE")
        self.assertEqual(r["new_native_this_invocation"],0)
        self.assertFalse(r["native_success_claimed_in_plan"])
        self.assertEqual(r["maximum_new_native_total"],5)

if __name__=="__main__":
    unittest.main()
