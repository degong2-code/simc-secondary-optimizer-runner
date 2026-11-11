"""v319 strict contract: freshly generate Monk/Windwalker user input per campaign; Native0."""
import inspect
import os
import unittest
from unittest import mock

from integration_probes import p2_v319_new_windwalker_v290_v318_real_once as pilot
from integration_probes import p2_new_profile_product_e2e_once as fresh
from runner import v291_durable_multiscale_native_runner as durable

class V319NewSpecializationOffline(unittest.TestCase):
    def test_fresh_new_monks_not_previous_v313_v314_matrix(self):
        c, controls=pilot.new_user_case()
        self.assertEqual((c["character_class"],c["character_spec"]),
                         ("monk","windwalker"))
        self.assertEqual(c["final_T"],3450)
        self.assertEqual(c["sockets"],4)
        self.assertIsNone(c["special_gem"])
        self.assertEqual(controls["max_single_stat_percent"],45)
        self.assertEqual(controls["oil_hands"],[])
        self.assertEqual(controls["consumable_choices"]["diamond_id"],0)
        self.assertEqual(controls["special_items"],[])
        self.assertEqual(controls["embellishments"],[])

    def test_new_profile_optin_fails_before_binary_native_or_web(self):
        with mock.patch.dict(os.environ,
                             {"P2_V319_ONE_FRESH_SPEC_AB_ONCE":"0"}):
            with self.assertRaisesRegex(
                    pilot.V319Blocked,"EXPLICIT_ONE_SHOT_NATIVE_OPT_IN"):
                pilot.main()

    def test_two_algorithms_share_source_and_exact_iteration_ids(self):
        self.assertEqual(set(pilot.EXPECTED_POLICIES),
                         {"v290_original","v318_idea001"})
        self.assertEqual((pilot.ITER_SCOUT,pilot.ITER_CONFIRM),(35,320))
        self.assertGreaterEqual(pilot.MAX_NATIVE_PER_ARM,16)
        self.assertIn("sem_precision_priority_optin",
                      inspect.signature(durable.run).parameters)
        self.assertEqual(fresh.BUILD,"12.1.5.70783")

if __name__=="__main__":
    unittest.main()
