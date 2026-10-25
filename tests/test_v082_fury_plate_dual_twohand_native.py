"""v082 Fury Dwarf plate dual-twohand source and static-c contract tests.

Offline/synthetic-only; Native authenticity is established only by the
isolated GitHub Action with genuine SimC input+JSON2 receipt.
"""
import pathlib,sys,tempfile,unittest,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v082_fury_plate_dual_twohand_native as fury
import v061_scenario_contract as scenario
import v077_generic_profile_bootstrap_readiness as readiness
import v046_static_item_cache as static

UPSTREAM=ROOT/"integration_probes/fixtures/v082_upstream_mid2_warrior_fury_reference.simc"

class FuryNativeArchetype(unittest.TestCase):
    def setUp(self):
        self.source=UPSTREAM.read_text(encoding="utf8")

    def test_origin_has_two_distinct_source_backed_weapons_and_plate_tier(self):
        with tempfile.TemporaryDirectory() as d:
            text,cfg,fill,meta=fury.source_profile(self.source,d)
        self.assertEqual(meta["armor"],"plate")
        self.assertEqual(meta["weapon_form"],"dual_two_handed")
        self.assertEqual((meta["main_hand_source_id"],meta["off_hand_source_id"]),
                         (268213,237847))
        self.assertEqual(cfg["character"]["race"],"dwarf")
        self.assertEqual(cfg["character"]["spec"],"fury")
        self.assertEqual({row["slot"] for row in cfg["equipment"]["tier"]},
                         {"head","shoulders","chest","hands"})
        self.assertEqual({row["slot"] for row in cfg["equipment"]["crafted"]},
                         {"wrists","off_hand"})
        self.assertIn("main_hand=selected_268213,id=268213,ilevel=334",text)
        self.assertIn("off_hand=selected_237847,id=237847,ilevel=334",text)
        self.assertEqual(len(cfg["equipment"]["trinkets"]),2)
        self.assertEqual(len(fill),8)
        self.assertFalse(meta["F_attribution_confirmed_independently"])

    def test_exact_original_simc_apl_unchanged_and_oil_not_added_to_T(self):
        with tempfile.TemporaryDirectory() as d:
            text,cfg,fill,meta=fury.source_profile(self.source,d)
        original=[x for x in self.source.splitlines() if x.startswith("actions")]
        later=[x for x in text.splitlines() if x.startswith("actions")]
        self.assertEqual(original,later)
        self.assertTrue(len(original)>35)
        self.assertNotIn("temporary_enchant=",text)
        self.assertIsNone(cfg["consumables"]["weapon_temporary"])
        self.assertEqual(sum(fury.DECLARED_F.values()),165)
        self.assertEqual(cfg["consumables"]["flask_budget_F"],165)

    def test_generic_first_use_blocks_missing_nontrinket_static(self):
        with tempfile.TemporaryDirectory() as d:
            text,cfg,fill,_=fury.source_profile(self.source,d)
            normalized=scenario.normalize(cfg)
            planned=readiness.prepare(cfg,fill,static.empty_cache(),
                                      text,pathlib.Path(d)/"witnesses")
        self.assertEqual(normalized["scenario"]["target"]["ilevel"],334)
        self.assertEqual(planned["status"],
                         "BLOCKED_EXACT_NATIVE_STATIC_VARIANTS_MISSING")
        self.assertGreater(planned["missing_exact_native_variant_count"],0)
        self.assertFalse(planned["native_success_claimed"])
        self.assertEqual(planned["new_native_calls"],0)

    def test_profile_source_git_blob_changed_fails_closed(self):
        altered=self.source.replace("race=dwarf","race=orc",1)
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(fury.Blocked,
                                        "UPSTREAM_FURY_SOURCE_BLOB_DRIFT"):
                fury.source_profile(altered,d)

    def test_no_binary_does_not_claim_native(self):
        with tempfile.TemporaryDirectory() as d:
            out=pathlib.Path(d)/"output"
            rc=fury.run(UPSTREAM,out)
            self.assertEqual(rc,0)
            receipt=json.loads((out/"V082_RECEIPT.json").read_text("utf8"))
        self.assertEqual(receipt["status"],
                         "PASS_UPSTREAM_TWO_WEAPON_STATIC_PLAN_ZERO_NATIVE")
        self.assertEqual(receipt["new_native_this_invocation"],0)
        self.assertEqual(receipt["maximum_new_native"],4)
        self.assertFalse(receipt["global_optimum_proven"])

    def test_legacy_only_exposes_one_scenario_and_no_fabricated_g(self):
        with tempfile.TemporaryDirectory() as d:
            _,cfg,fill,_=fury.source_profile(self.source,d)
        self.assertEqual(cfg["runtime"]["max_native_calls"],4)
        self.assertEqual(cfg["target"]["mode"],"derived_ilevel")
        self.assertEqual(cfg["equipment"]["special"],[])
        self.assertEqual(len(fury.ALL_SLOTS),16)

if __name__=="__main__":
    unittest.main()
