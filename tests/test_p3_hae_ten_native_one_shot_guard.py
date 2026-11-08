"""P3-HAE real 8 scout + 2 selected confirmations opt-in guard; offline."""
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]

class HaeExactGuard(unittest.TestCase):
    def test_exact_one_shot_guard_remains_separate_from_had_and_hy(self):
        w=(ROOT/".github/workflows/p3_fz_reuse_exact_simc_live_t1.yml").read_text()
        p=(ROOT/"integration_probes/p3_fr_zero_base_t1_acceptance.py").read_text()
        for token in ("[p3-hae-ten-native-once]",
                      "p3_hae_ten_native_20261109.json",
                      "P3_T1_V291_TEN_NATIVE_ONCE",
                      '"native_batches":[4,6]',
                      '"confirmation_iterations":320',
                      "p3_hae_v291_native_evidence.zip"):
            self.assertIn(token,w)
        for token in ("batches=((4,6) if hae_ten else",
                      "longrun.stage_extended_manifest(",
                      "P3_HAE_NATIVE_SELECTED_PRECISION_NOT_CONFIRMED",
                      '"confirmed_selected_pair_95"',
                      "p3_hae_v291_failure_evidence.zip"):
            self.assertIn(token,p)
        compile(p,str(ROOT/"integration_probes/p3_fr_zero_base_t1_acceptance.py"),"exec")

if __name__=="__main__":
    unittest.main()
