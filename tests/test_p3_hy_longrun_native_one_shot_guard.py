"""P3-HY offline exact bounded real-v291 acceptance workflow/guard."""
import pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class LiveOneShotGuard(unittest.TestCase):
    def test_guarded_one_shot_and_archive_are_opt_in(self):
        w=(ROOT/".github/workflows/p3_fz_reuse_exact_simc_live_t1.yml").read_text()
        p=(ROOT/"integration_probes/p3_fr_zero_base_t1_acceptance.py").read_text()
        self.assertIn("[p3-hy-longrun-three-native-once]",w)
        self.assertIn("p3_hy_longrun_three_native_20261108.json",w)
        self.assertIn("P3_T1_V291_LONGRUN_NATIVE_ONCE",w)
        self.assertIn("p3_hy_v291_native_evidence.zip",w)
        self.assertIn("p3_hy_v291_failure_evidence.zip",w)
        self.assertIn("v291_failure_evidence",p)
        self.assertIn("v291_three_native_e2e",p)
        self.assertIn("resume_and_cache_replay_required",w)
        self.assertIn("batches=((4,6) if hae_ten else",p)
        self.assertIn("(4,4) if had_eight else (2,1))",p)
        self.assertIn("max_new_native_this_invocation=batches[0]",p)
        self.assertIn("max_new_native_this_invocation=batches[1]",p)
        self.assertIn("max_new_native_this_invocation=0,cache_only=True",p)
        self.assertIn("PASS_REAL_V291_NATIVE_AND_DURABLE_RESUME_REPLAY",p)
        # Offline syntax compile before any live workflow is triggered.
        compile(p,str(ROOT/"integration_probes/p3_fr_zero_base_t1_acceptance.py"),"exec")
if __name__=="__main__":
    unittest.main()
