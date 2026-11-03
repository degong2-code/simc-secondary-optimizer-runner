"""P3-CO focused: exact pinned source, no actual Native or budget claims."""
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"runner"))
from integration_probes import p3_co_actual_flask_oil_native as probe

class P3COFocused(unittest.TestCase):
    def test_pinned_original_profile_and_consumable_action(self):
        raw=(ROOT/probe.PROFILE).read_bytes()
        profile=probe.profile_from_source(raw)
        self.assertIn("actions.precombat=flask\n",profile)
        self.assertIn("actions.precombat+=/snapshot_stats",profile)
        self.assertIn("main_hand=",profile)
        self.assertEqual(len(probe.CASES),2)
    def test_two_options_share_native_count_but_cannot_promote(self):
        invoked=[]
        def fake(**kwargs):
            invoked.append(kwargs["kind"])
            return {"status":"SIMC_STATIC_CHMV_EFFECT_OBSERVED_NOT_ADMITTED",
                    "new_native_calls":2 if len(invoked)==1 else 1,
                    "static_CHMV_candidate":{"crit_rating":21},
                    "observed":{"observed_rating_delta":{"crit_rating":21}}}
        with tempfile.TemporaryDirectory() as folder:
            result=probe.run(root=folder,source=ROOT/probe.PROFILE,
                             binary="unused",measure=fake)
        self.assertEqual(result["status"],"OBSERVATIONS_SOURCE_ONLY")
        self.assertEqual(result["new_native_calls"],3)
        self.assertEqual(invoked,["flask","temporary_enchant"])
        self.assertIsNone(result["F"])
        self.assertIsNone(result["O"])
        self.assertFalse(result["environment_ready"])
        self.assertFalse(result["ui_auto_registered"])
        self.assertFalse(result["quality_group_verified"])
    def test_invalid_sha_and_revision_fail_before_measurement(self):
        with tempfile.TemporaryDirectory() as folder:
            p=pathlib.Path(folder)/"wrong.simc";p.write_bytes(b"mage=wrong")
            with mock.patch.object(probe.pair,"measure",
                          side_effect=AssertionError("NATIVE_FORBIDDEN")):
                with self.assertRaisesRegex(ValueError,"PROFILE_SHA_DRIFT"):
                    probe.run(root=pathlib.Path(folder)/"out",
                              source=p,binary="unused")
                with self.assertRaisesRegex(ValueError,"REVISION_REQUIRED"):
                    probe.run(root=pathlib.Path(folder)/"out",
                              source=ROOT/probe.PROFILE,binary="unused",
                              simc_revision="a"*39+"b")
    def test_failure_records_native_log_without_fake_F_O(self):
        def failed(**kwargs):
            return {"status":"SIMC_CONSUMABLE_NATIVE_FAILED_NO_AUTO_RETRY",
                    "new_native_calls":1,
                    "native_log_excerpt":"SimC original ERROR"}
        with tempfile.TemporaryDirectory() as folder:
            result=probe.run(root=folder,source=ROOT/probe.PROFILE,
                             binary="unused",measure=failed)
            self.assertEqual(result["status"],"NATIVE_SOURCE_PROBE_FAILED")
            self.assertEqual(len(result["observations"]),1)
            self.assertEqual(result["new_native_calls"],1)
            self.assertIsNone(result["F"])
            self.assertIn("ERROR",(pathlib.Path(folder)/"P3_CO_RECEIPT.json").read_text())
if __name__=="__main__":
    unittest.main()
