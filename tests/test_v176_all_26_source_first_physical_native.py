"""v176 coverage, exact spec set, no Native in preflight, no optimizer calls."""
import pathlib,sys,tempfile,unittest
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"integration_probes"),str(ROOT/"runner")]
import v176_all_26_source_first_physical_native as batch

class FullDpsSeasonPhysicalOffline(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root=pathlib.Path(temp.name)
        self.binary=self.root/"dummy_simc"
        self.binary.write_bytes(b"NOT_AN_EXECUTABLE")
        self.out=self.root/"out"

    def test_all_26_real_season_source_first_preflight_zero_simc(self):
        with mock.patch.object(batch.physical.subprocess,"run") as proc:
            result=batch.run(self.binary,self.out,iterations=35)
            proc.assert_not_called()
        self.assertEqual(result["status"],"PREFLIGHT_26_READY",result["counts"])
        self.assertEqual(len(result["results"]),26)
        self.assertEqual(result["counts"],{"PLAN_READY_ZERO_NATIVE":26})
        self.assertEqual(result["new_native_calls_confirmed"],0)
        self.assertEqual(result["new_native_permits_reserved"],0)
        self.assertEqual(result["adaptive_optimizer_native_calls"],0)
        self.assertEqual(len(list(self.out.glob(
            "*__source_first_v172__*/stage/profile.simc"))),26)
        self.assertEqual(len(list(self.out.glob(
            "*__source_first_v172__*/receipt.json"))),0)
        self.assertEqual(len(list(self.out.glob(
            "*__source_first_v172__*/physical.simc"))),0)

    def test_native_cap_requires_explicit_execute_and_original_25_only(self):
        with self.assertRaisesRegex(batch.BatchBlocked,
                                    "PHYSICAL_ONLY_NATIVE_BOUNDS"):
            batch.run(self.binary,self.out,max_new=25)
        with mock.patch.object(batch,"BINARY_SHA",
                batch.physical.sha(self.binary.read_bytes())):
            with self.assertRaisesRegex(batch.BatchBlocked,
                       "EXACT_25_NEW_WITH_V174_PALADIN_REPLAY_REQUIRED"):
                batch.run(self.binary,self.out,execute=True,max_new=26)
        with self.assertRaisesRegex(batch.BatchBlocked,
                                    "PINNED_SIMC_BINARY_SHA_CHANGED"):
            batch.run(self.binary,self.out,execute=True,max_new=25)
        self.assertFalse(self.out.exists())

    def test_unknown_default_trinket_or_spec_is_not_silently_promoted(self):
        allowed={250215,281215}
        u=batch.user_for("druid/balance",allowed)
        self.assertEqual(u["oil_hands"],[])
        self.assertEqual(u["target"],{"ilevel":334,"final_T":None})
        with self.assertRaisesRegex(batch.BatchBlocked,"NON_SEASON_TRINKET"):
            batch.user_for("druid/balance",{281215})
        self.assertNotIn("evoker/augmentation",batch.ALL)

if __name__=="__main__":unittest.main()
