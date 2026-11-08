"""P3-HAG exact source-locked cross-job Native0 workflow guard."""
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]


class HagSourceOnly(unittest.TestCase):
    def test_only_separate_opt_in_can_download_source_native_archive(self):
        workflow=(ROOT/".github/workflows/p3_fz_reuse_exact_simc_live_t1.yml").read_text()
        probe=(ROOT/"integration_probes/p3_fr_zero_base_t1_acceptance.py").read_text()
        for value in (
            "[p3-hag-portable-cache-once]",
            "p3_hag_portable_cache_once_20261109.json",
            "P3_T1_V292_PORTABLE_ONCE",
            "run-id: 42501052586",
            "p3_hag_v292_portable_receipt.json",
            '"new_dps_native_calls":0',
            '"imported_native_cases":10'):
            self.assertIn(value,workflow)
        for value in ("v292_portable_native_case_cache",
                      "portable.import_verified_archive(",
                      "PASS_EXACT_CROSS_JOB_NATIVE_REPLAY_ZERO_NEW_DPS",
                      "new_dps_native_calls",
                      "P3_HAG_PORTABLE_REAL_NATIVE_REPLAY_DRIFT"):
            self.assertIn(value,probe)
        compile(probe,str(ROOT/"integration_probes/p3_fr_zero_base_t1_acceptance.py"),"exec")


if __name__=="__main__":
    unittest.main()
