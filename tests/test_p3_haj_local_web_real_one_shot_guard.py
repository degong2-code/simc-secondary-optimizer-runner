"""P3-HAJ: source-locked 70783 local web real Native single-shot guard."""
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]

class WebRealOnceGuard(unittest.TestCase):
    def test_opt_in_scope_and_real_web_bridge(self):
        w=(ROOT/".github/workflows/p3_fz_reuse_exact_simc_live_t1.yml").read_text()
        p=(ROOT/"integration_probes/p3_fr_zero_base_t1_acceptance.py").read_text()
        q=(ROOT/"integration_probes/p3_haj_real_local_web_native_e2e.py").read_text()
        for k in ("[p3-haj-web-native-once]",
                  "p3_haj_real_web_native_once_20261109.json",
                  "P3_T1_WEB_LONGRUN_ONCE",
                  '"adaptive_dps_native_max":4',
                  '"cache_only_new_native_calls":0',
                  "requirements-web-test.txt"):
            self.assertIn(k,w)
        for k in ("if web_longrun:","web_e2e.execute(",
                  "P3_HAJ_EXCLUSIVE_REAL_WEB_DPS_REQUIRED"):
            self.assertIn(k,p)
        for k in ("v213_source_to_catalog","/api/v1/longrun/prepare",
                  "/longrun/resume","/longrun/cancel",
                  "/longrun/cache-only","/longrun/result",
                  "all(v*2<total for v in vector.values())",
                  "real_browser_click_tested"):
            self.assertIn(k,q)
        # Ret web once must not inherit Enh specialization or v291 probe mode.
        for key in ("P3_T1_SPEC_CLASS:", "P3_T1_SPEC_NAME:",
                    "P3_T1_FULL_CONSUMABLES_ONCE:",
                    "P3_T1_V291_LONGRUN_NATIVE_ONCE:"):
            line=next(x for x in w.splitlines() if x.strip().startswith(key))
            self.assertNotIn("p3-haj-web-native-once",line)
        for key in ("P3_T1_EXISTING_SPECIAL_GEM_ID:",
                    "P3_T1_DPS_E2E_ONCE:",
                    "P3_T1_WEB_LONGRUN_ONCE:"):
            line=next(x for x in w.splitlines() if x.strip().startswith(key))
            self.assertIn("p3-haj-web-native-once",line)
        compile(p,"p3_fr_zero_base_t1_acceptance.py","exec")
        compile(q,"p3_haj_real_local_web_native_e2e.py","exec")

if __name__=="__main__":
    unittest.main()
