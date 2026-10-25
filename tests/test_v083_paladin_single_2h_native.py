"""v083 Blood Elf Retribution plate single 2H source and bounded engine reuse."""
import json,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v083_paladin_single_2h_native as paladin
import v082_fury_plate_dual_twohand_native as fury
import v061_scenario_contract as scenario
import v077_generic_profile_bootstrap_readiness as readiness
import v046_static_item_cache as static

SOURCE=ROOT/"integration_probes/fixtures/v083_upstream_mid2_paladin_retribution_reference.simc"

class V083SourceBackedSingle2H(unittest.TestCase):
    def setUp(self):self.source=SOURCE.read_text("utf8")
    def test_single_twohand_blood_elf_and_fifteen_slots(self):
        with tempfile.TemporaryDirectory() as d:
            reference,cfg,filler,meta=paladin.source_profile(self.source,d)
        self.assertEqual(cfg["character"]["class"],"paladin")
        self.assertEqual(cfg["character"]["spec"],"retribution")
        self.assertEqual(cfg["character"]["race"],"blood_elf")
        self.assertEqual(meta["armor"],"plate")
        self.assertEqual(meta["weapon_form"],"single_two_handed_no_offhand")
        self.assertEqual(meta["main_hand_source_id"],268213)
        self.assertNotIn("off_hand=",reference)
        self.assertIn("main_hand=selected_268213,id=268213,ilevel=334",reference)
        self.assertEqual(len(filler),8)
        self.assertEqual(len(paladin.ALL_SLOTS),15)
        self.assertEqual(len(cfg["equipment"]["crafted"]),1)
        self.assertEqual(len(cfg["equipment"]["trinkets"]),2)
        self.assertEqual({e["slot"] for e in cfg["equipment"]["tier"]},
                         {"head","shoulders","chest","hands"})
        self.assertEqual(meta["replacement_non_tier_plate_legs_id"],271878)
        self.assertIn("legs=selected_271878,id=271878,ilevel=334",reference)

    def test_original_retribution_apl_is_exact_and_no_oil(self):
        with tempfile.TemporaryDirectory() as d:
            ref,cfg,_,meta=paladin.source_profile(self.source,d)
        original=[s for s in self.source.splitlines() if s.startswith("actions")]
        actual=[s for s in ref.splitlines() if s.startswith("actions")]
        self.assertEqual(original,actual)
        self.assertEqual(len(original),meta["source_paladin_APL_lines_preserved"])
        self.assertIsNone(cfg["consumables"]["weapon_temporary"])
        self.assertNotIn("temporary_enchant=",ref)
        self.assertFalse(meta["F_attribution_confirmed_independently"])

    def test_exact_nontrinket_native_G_missing_blocks_before_claim(self):
        with tempfile.TemporaryDirectory() as d:
            ref,cfg,fill,_=paladin.source_profile(self.source,d)
            result=readiness.prepare(cfg,fill,static.empty_cache(),ref,
                                     pathlib.Path(d)/"witnesses")
        self.assertEqual(result["status"],
                         "BLOCKED_EXACT_NATIVE_STATIC_VARIANTS_MISSING")
        self.assertGreater(result["missing_exact_native_variant_count"],0)
        self.assertFalse(result["native_success_claimed"])

    def test_source_and_replacement_provenance_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(paladin.Blocked,
                                      "PALADIN_UPSTREAM_SOURCE_BLOB_CHANGED"):
                paladin.source_profile(self.source.replace("race=dwarf","race=orc",1),d)

    def test_bounded_original_fury_default_remains_unchanged(self):
        self.assertEqual(fury.NATIVE_MAX,4)
        self.assertEqual(paladin.shared.run.__defaults__,(None,False))
        self.assertEqual(paladin.DECLARED_F,
            {"crit_rating":0,"haste_rating":165,"mastery_rating":0,"versatility_rating":0})

    def test_offline_no_real_native_claim(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            rc=paladin.run(SOURCE,root/"out")
            self.assertEqual(rc,0)
            receipt=json.loads((root/"out"/"V083_RECEIPT.json").read_text("utf8"))
        self.assertEqual(receipt["status"],
                         "PASS_PALADIN_SINGLE_2H_EXACT_INPUT_PLAN_ZERO_NATIVE")
        self.assertEqual(receipt["new_native_this_invocation"],0)
        self.assertEqual(receipt["maximum_new_native"],4)
        self.assertEqual(receipt["origin"]["weapon_form"],"single_two_handed_no_offhand")
        self.assertFalse(receipt["global_optimum_proven"])

if __name__=="__main__":unittest.main()
