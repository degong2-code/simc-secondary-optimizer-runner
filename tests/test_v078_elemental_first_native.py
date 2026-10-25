"""v078 new Shaman smoke input tests; no claim of actual Native proof here."""
import pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v078_elemental_first_native as pilot
import v077_generic_profile_bootstrap_readiness as generic
import v061_scenario_contract as scenario
import v062_static_budget_bridge as budget
import v046_static_item_cache as cache
import v063_numeric_injection as numeric

UPSTREAM=ROOT/"integration_probes/fixtures/v078_upstream_mid2_shaman_elemental_reference.simc"

class V078FirstNewClass(unittest.TestCase):
    def setUp(self):
        self.src=UPSTREAM.read_text("utf8")
    def test_pinned_apl_action_bytes_and_four_tier_mail_shield(self):
        with tempfile.TemporaryDirectory() as p:
            ref,cfg,filler,metadata=pilot.spec_profile(self.src,p)
        before=[x for x in self.src.splitlines() if x.startswith("actions")]
        after=[x for x in ref.splitlines() if x.startswith("actions")]
        self.assertEqual(before,after)
        self.assertEqual(cfg["character"]["class"],"shaman")
        self.assertEqual(cfg["character"]["race"],"orc")
        self.assertEqual(cfg["character"]["spec"],"elemental")
        self.assertEqual({x["slot"] for x in cfg["equipment"]["tier"]},
             {"shoulders","chest","hands","legs"})
        self.assertEqual(metadata["selected_representative_gear"]["off_hand"],268262)
        self.assertIn("off_hand=selected_268262",ref)
        self.assertEqual(len(cfg["equipment"]["trinkets"]),2)
        self.assertEqual(len(cfg["equipment"]["crafted"]),2)
    def test_scenario_and_two_distinct_raw_injection_inputs(self):
        with tempfile.TemporaryDirectory() as p:
            ref,cfg,fill,metadata=pilot.spec_profile(self.src,p)
            normalized=scenario.normalize(cfg)
            vectors=generic.paired_input(ref,pathlib.Path(p)/"native")
        self.assertEqual(normalized["scenario"]["target"]["ilevel"],334)
        self.assertEqual(normalized["budget"]["T_status"],"WAIT_NATIVE_G")
        self.assertEqual(len(vectors),2)
        self.assertEqual(vectors[0]["stable_profile_sha256"],vectors[1]["stable_profile_sha256"])
        self.assertNotEqual(vectors[0]["input_sha256"],vectors[1]["input_sha256"])
        self.assertEqual(sum(vectors[0]["raw_rating"].values()),2800)
        self.assertEqual(sum(vectors[1]["raw_rating"].values()),2800)
    def test_missing_cache_blocks_official_native_budget_not_input(self):
        with tempfile.TemporaryDirectory() as p:
            ref,cfg,filler,_=pilot.spec_profile(self.src,p)
            planned=generic.prepare(cfg,filler,cache.empty_cache(),ref,pathlib.Path(p))
        self.assertEqual(planned["status"],"BLOCKED_EXACT_NATIVE_STATIC_VARIANTS_MISSING")
        self.assertGreater(planned["missing_exact_native_variant_count"],0)
        self.assertFalse(planned["native_success_claimed"])
        self.assertIsNone(planned["G_native_if_complete"])
    def test_missing_original_gear_id_blocks_before_native(self):
        bad=self.src.replace("off_hand=bubblefin_splash_guard,id=268262",
                             "off_hand=bubblefin_splash_guard",1)
        self.assertNotEqual(bad,self.src)
        with tempfile.TemporaryDirectory() as p:
            with self.assertRaisesRegex(pilot.Blocked,"UPSTREAM_ID_MISSING:off_hand"):
                pilot.spec_profile(bad,p)
    def test_no_binary_generates_only_plan(self):
        with tempfile.TemporaryDirectory() as p:
            root=pathlib.Path(p)
            rc=pilot.run(UPSTREAM,root/"native")
            self.assertEqual(rc,0)
            import json
            s=json.loads((root/"native"/"V078_RECEIPT.json").read_text())
        self.assertEqual(s["status"],"PASS_NEW_CLASS_TWO_WITNESS_INPUT_PLAN_ONLY")
        self.assertEqual(s["new_native_this_invocation"],0)
        self.assertEqual(len(s["witness_input_sha256"]),2)
        self.assertEqual(s["official_budget_formula"],"T=G+J+F")

if __name__=="__main__":
    unittest.main()
