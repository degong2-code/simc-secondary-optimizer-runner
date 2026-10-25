"""v084 Human Frost source-backed 1H + nonweapon offhand regression tests.

These are synthetic/offline source contract tests. Actual Native acceptance is
a separate GitHub Action with pinned binary and SHA-verified JSON2 receipts.
"""
import json,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v084_frost_cloth_1h_frill_native as frost
import v082_fury_plate_dual_twohand_native as runner
import v077_generic_profile_bootstrap_readiness as readiness
import v046_static_item_cache as cache
import v061_scenario_contract as scenario

SOURCE=ROOT/"integration_probes/fixtures/v084_upstream_mid2_mage_frost_reference.simc"

class V084FrostClothOneHandFrill(unittest.TestCase):
    def setUp(self):
        self.original=SOURCE.read_text("utf8")

    def test_human_frost_cloth_with_exact_onehand_frill_and_sixteen_slots(self):
        with tempfile.TemporaryDirectory() as d:
            ref,cfg,fill,m=frost.source_profile(self.original,d)
        self.assertEqual((cfg["character"]["class"],cfg["character"]["spec"],
                          cfg["character"]["race"]),("mage","frost","human"))
        self.assertEqual((m["armor"],m["weapon_form"]),
                    ("cloth","onehand_plus_nonweapon_offhand"))
        self.assertEqual(len(frost.ALL_SLOTS),16)
        self.assertEqual(len(fill),8)
        self.assertEqual(m["main_hand_source_id"],271092)
        self.assertEqual(m["off_hand_source_id"],245769)
        self.assertIn("main_hand=selected_271092,id=271092,ilevel=334",ref)
        self.assertIn("off_hand=selected_245769,id=245769,ilevel=334",ref)
        self.assertEqual({x["slot"] for x in cfg["equipment"]["tier"]},
                {"shoulders","chest","hands","legs"})
        self.assertEqual({x["slot"] for x in cfg["equipment"]["crafted"]},
                {"waist","off_hand"})
        self.assertEqual(len(cfg["equipment"]["trinkets"]),2)

    def test_original_frost_APL_preserved_and_only_four_tier(self):
        with tempfile.TemporaryDirectory() as d:
            ref,cfg,_,m=frost.source_profile(self.original,d)
        actions=lambda s:[x for x in s.splitlines() if x.startswith("actions")]
        self.assertEqual(actions(ref),actions(self.original))
        self.assertEqual(m["source_APL_lines_preserved"],71)
        self.assertEqual(m["fifth_tier_head_replaced"],271564)
        self.assertEqual(m["non_tier_source_backed_head"],271874)
        self.assertIn("head=selected_271874,id=271874,ilevel=334",ref)
        self.assertFalse(m["F_attribution_independently_verified"])
        self.assertNotIn("temporary_enchant=",ref)

    def test_flask_f_crit_not_haste_and_oil_still_outside_T(self):
        with tempfile.TemporaryDirectory() as d:
            ref,cfg,_,meta=frost.source_profile(self.original,d)
        self.assertIn("flask=flask_of_the_shattered_sun_2",ref)
        self.assertEqual(meta["declared_F_vector"],{
            "crit_rating":165,"haste_rating":0,
            "mastery_rating":0,"versatility_rating":0})
        self.assertEqual(cfg["consumables"]["flask_budget_F"],165)
        self.assertIsNone(cfg["consumables"]["weapon_temporary"])
        self.assertEqual(runner.DECLARED_F["haste_rating"],165,
                         "Old Fury/Paladin F default must remain unchanged")

    def test_first_use_exact_static_missing_is_blocked_not_assumed_zero(self):
        with tempfile.TemporaryDirectory() as d:
            ref,cfg,fill,_=frost.source_profile(self.original,d)
            prepared=readiness.prepare(cfg,fill,cache.empty_cache(),ref,
                             pathlib.Path(d)/"raw")
        self.assertEqual(prepared["status"],
                    "BLOCKED_EXACT_NATIVE_STATIC_VARIANTS_MISSING")
        self.assertGreater(prepared["missing_exact_native_variant_count"],0)
        self.assertIsNone(prepared["G_native_if_complete"])
        self.assertEqual(prepared["new_native_calls"],0)

    def test_source_byte_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            bad=self.original.replace("race=tauren","race=human",1)
            with self.assertRaisesRegex(frost.Blocked,"FROST_UPSTREAM_GIT_BLOB_CHANGED"):
                frost.source_profile(bad,d)

    def test_offline_plan_is_not_real_native_acceptance(self):
        with tempfile.TemporaryDirectory() as d:
            out=pathlib.Path(d)/"result"
            code=frost.run(SOURCE,out)
            self.assertEqual(code,0)
            receipt=json.loads((out/"V084_RECEIPT.json").read_text())
        self.assertEqual(receipt["status"],
                    "PASS_FROST_CLOTH_1H_FRILL_INPUT_ONLY_ZERO_NATIVE")
        self.assertEqual(receipt["new_native_this_invocation"],0)
        self.assertEqual(receipt["declared_F_vector"],frost.F_DECLARED)
        self.assertFalse(receipt["global_optimum_proven"])

if __name__=="__main__":
    unittest.main()
