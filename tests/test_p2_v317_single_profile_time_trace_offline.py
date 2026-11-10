"""v317 minimal ONE-SCENARIO Native trigger preflight, offline no Native."""
import inspect
import os
import unittest
from unittest import mock

from integration_probes import p2_v317_single_profile_time_trace_real_once as pilot
from integration_probes import p2_new_profile_product_e2e_once as source
from runner import v291_durable_multiscale_native_runner as durable


class V317Offline(unittest.TestCase):
    def test_optin_required_before_any_external_action(self):
        with mock.patch.dict(os.environ,{"P2_V317_SINGLE_TRACE_ONCE":""}):
            with self.assertRaisesRegex(
                    pilot.V317Blocked,"EXPLICIT_ONE_SHOT_REAL_NATIVE_REQUIRED"):
                pilot.main()

    def test_one_real_fresh_user_profile_no_historical_import(self):
        case, controls = source.selected_case(pilot.CASE)
        self.assertEqual((case["character_class"],case["character_spec"]),
                         ("warrior","arms"))
        self.assertEqual(case["final_T"],3250)
        self.assertIsNone(case["special_gem"])
        self.assertFalse(controls.get("import_simc_profile"))
        self.assertEqual(controls["consumable_choices"]["diamond_id"],0)

    def test_existing_v291_two_exact_iterations_and_optin(self):
        self.assertEqual((pilot.ITER_SCOUT,pilot.ITER_CONFIRM),(35,320))
        self.assertEqual(pilot.NATIVE_CAP,12)
        self.assertIn("case_timing_trace",
                      inspect.signature(durable.run).parameters)


if __name__ == "__main__":
    unittest.main()
