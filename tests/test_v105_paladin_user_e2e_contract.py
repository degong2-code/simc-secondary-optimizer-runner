"""v105 user-facing Paladin P1-1 plan and acceptance contract; no SimC."""
import pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"integration_probes"))
import v105_paladin_user_e2e as p1

class UserJourneyAcceptance(unittest.TestCase):
    def test_paladin_simple_controls_no_full_gear_or_developer_fields(self):
        u=p1.sample_user()
        self.assertEqual(u["character"]["class"],"paladin")
        self.assertEqual(u["character"]["spec"],"retribution")
        self.assertEqual(u["target"],{"ilevel":334,"final_T":None})
        self.assertEqual({x["slot"] for x in u["trinkets"]},
                         {"trinket1","trinket2"})
        self.assertNotIn("profile_simc",u)
        self.assertNotIn("seed_targets_B",u)
        self.assertNotIn("fillers_json",u)

    def test_prepare_full_user_flow_planned_six_native_without_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            fake=root/"not_native";fake.write_bytes(b"NO_NATIVE")
            receipt=p1.run(root/"output",fake,execute=False)
            p1.check_plan(receipt["plan"])
            self.assertEqual(receipt["native_calls_completed_here"],0)
            self.assertEqual(receipt["plan"]["fixed_O"]["crit_rating"],16)
            self.assertEqual(receipt["plan"]["fixed_O"]["haste_rating"],16)
            self.assertEqual(receipt["plan"]["final_T"],3182)
            self.assertEqual(receipt["stage"],"PLAN_ONLY")
            self.assertFalse((root/"output"/"generated"/"simc_results").exists())
            self.assertFalse((root/"output"/"V105_REAL_E2E_RECEIPT.json").exists())

    def test_real_native_mode_rejects_unpinned_binary_before_any_dps(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            fake=root/"not_native";fake.write_bytes(b"NO_NATIVE")
            with self.assertRaisesRegex(ValueError,"PINNED_SIMC_ELF_SHA_MISMATCH"):
                p1.run(root/"output",fake,execute=True)
            self.assertFalse((root/"output"/"generated").exists())

    def test_existing_result_requires_actual_95_percent_observations(self):
        with self.assertRaises((KeyError,ValueError,TypeError)):
            p1.check_user_result({"status":"PASS_FAKE",
                   "base_B":3150,"final_T":3182,"user_result":{}})

if __name__=="__main__":unittest.main()
