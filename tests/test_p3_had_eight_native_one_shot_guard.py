"""P3-HAD eight real-Native one-shot safety guard (offline)."""
import json
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
REQ=ROOT/"integration_probes/requests/p3_had_eight_native_20261109.json"

class HadOptInGuard(unittest.TestCase):
    def test_opt_in_and_archive_only(self):
        w=(ROOT/".github/workflows/p3_fz_reuse_exact_simc_live_t1.yml").read_text()
        p=(ROOT/"integration_probes/p3_fr_zero_base_t1_acceptance.py").read_text()
        for token in ("[p3-had-eight-native-once]",REQ.name,
                      "P3_T1_V291_EIGHT_NATIVE_ONCE",
                      '"native_batches":[4,4]',
                      '"longrun_total_native_budget":12',
                      "p3_had_v291_native_evidence.zip"):
            self.assertIn(token,w)
        for token in ("longrun.stage_extended_manifest(",
                      "source_loader=entry.source",
                      "batches=(4,4) if had_eight else (2,1)",
                      "max_new_native_this_invocation=0,cache_only=True",
                      "p3_had_v291_native_evidence.zip"):
            self.assertIn(token,p)
        compile(p,str(ROOT/"integration_probes/p3_fr_zero_base_t1_acceptance.py"),"exec")
        if REQ.exists():
            data=json.loads(REQ.read_text())
            self.assertEqual(data["native_batches"],[4,4])
            self.assertEqual(data["longrun_total_native_budget"],12)
            self.assertTrue(data["strict_final_half_cap"])

if __name__=="__main__":
    unittest.main()
