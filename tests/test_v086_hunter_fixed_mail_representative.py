"""v086: one bounded corrected Hunter mail fixture and all-slot input integrity."""
import pathlib,sys,tempfile,unittest,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v086_hunter_fixed_mail_representative as fixed
import v079_hunter_ranged_generic_native as prior
import v061_scenario_contract as scenario
SOURCE=(ROOT/"integration_probes/fixtures/v079_upstream_mid2_hunter_beast_mastery_reference.simc")

class V086TwoFixedSecondaryMailSlots(unittest.TestCase):
    def make(self,root):
        return fixed.source_profile(SOURCE.read_text("utf8"),root)

    def test_two_new_ids_no_random_options_and_rest_gear_identical(self):
        with tempfile.TemporaryDirectory() as d:
            original,old_cfg,old_filler,_=prior.source_profile(SOURCE.read_text("utf8"),d)
            result,cfg,fill,meta=self.make(d)
        before={z.partition("=")[0]:z for z in original.splitlines()
                if z.startswith(tuple(slot+"=" for slot in prior.ALL_SLOTS))}
        after={z.partition("=")[0]:z for z in result.splitlines()
                if z.startswith(tuple(slot+"=" for slot in prior.ALL_SLOTS))}
        self.assertEqual(set(before),set(after))
        self.assertEqual(len(after),15)
        for slot in after:
            if slot not in ("head","feet"):
                self.assertEqual(before[slot],after[slot])
        self.assertEqual(after["head"],
            "head=selected_249317,id=249317,ilevel=334,source=local,gem_id=240983")
        self.assertEqual(after["feet"],
            "feet=selected_249320,id=249320,ilevel=334,source=local")
        self.assertEqual(meta["nontrinket_unclassified_unknown_items"],0)
        self.assertEqual({f["item_id"] for f in fill if f["slot"] in ("head","feet")},
                         {249317,249320})

    def test_exact_original_hunter_apl_talents_and_tier_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            before,old_cfg,_,_=prior.source_profile(SOURCE.read_text("utf8"),d)
            after,cfg,fill,_=self.make(d)
        actions=lambda s:[v for v in s.splitlines() if v.startswith("actions")]
        talents=lambda s:[v for v in s.splitlines() if v.startswith("talents=")]
        self.assertEqual(actions(before),actions(after))
        self.assertEqual(talents(before),talents(after))
        self.assertEqual(cfg["equipment"]["tier"],old_cfg["equipment"]["tier"])
        self.assertEqual(cfg["equipment"]["trinkets"],old_cfg["equipment"]["trinkets"])
        self.assertEqual(scenario.normalize(cfg)["scenario"]["target"]["ilevel"],334)

    def test_verified_real_native_budget_is_3148_not_old_2797(self):
        self.assertEqual(fixed.MEASURED_NONTRINKET_G,2845)
        self.assertEqual(fixed.MEASURED_OFFICIAL_T,2845+138+165)
        self.assertEqual(sum(fixed.KNOWN_NATIVE_HEAD_SECONDARY.values()),201)
        self.assertEqual(sum(fixed.KNOWN_NATIVE_FEET_SECONDARY.values()),150)
        self.assertEqual(fixed.MEASURED_OFFICIAL_T-(2494+138+165),351)
        self.assertEqual(len(fixed.NATIVE_EVIDENCE_JSON_SHA256),64)

    def test_tampered_upstream_source_fails_closed(self):
        raw=SOURCE.read_text("utf8").replace("spec=beast_mastery","spec=marksmanship",1)
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"HUNTER_UPSTREAM_APL_IDENTITY_DRIFT"):
                fixed.source_profile(raw,d)

    def test_cli_offline_writes_correct_profile_no_new_native_claim(self):
        with tempfile.TemporaryDirectory() as d:
            out=pathlib.Path(d)
            ret=fixed.main(["--upstream",str(SOURCE),"--out",str(out)])
            self.assertEqual(ret,0)
            m=json.loads((out/"V086_PROFILE_META.json").read_text())
            text=(out/"V086_REFERENCE.simc").read_text()
            self.assertIn("head=selected_249317,id=249317",text)
            self.assertIn("feet=selected_249320,id=249320",text)
            self.assertEqual(m["verified_T_with_declared_J138_F165"],3148)

if __name__=="__main__":unittest.main()
