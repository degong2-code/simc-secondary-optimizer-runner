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
        self.assertIsNone(c["final_T"])
        self.assertIsNone(controls["final_T"])
        self.assertEqual(c["sockets"],4)
        self.assertIsNone(c["special_gem"])
        self.assertEqual(controls["max_single_stat_percent"],45)
        self.assertEqual(controls["oil_hands"],[])
        self.assertEqual(controls["consumable_choices"]["diamond_id"],0)
        self.assertEqual(controls["special_items"],[])
        self.assertEqual(controls["embellishments"],[])

    def test_season_engine_auto_budget_overrides_nothing(self):
        from runner import v106_user_session_controller as users
        controls=users.standard_controls(("monk","windwalker"))
        self.assertIsNone(controls["final_T"])
        source={"G":2850,"J":92,"F":165,"O":{
            "crit_rating":0,"haste_rating":0,
            "mastery_rating":0,"versatility_rating":0},
            "B":3107,"T":3107}
        self.assertEqual(pilot.verified_automatic_T(source,controls),3107)
        source2={**source,"G":3182,"B":3439,"T":3439}
        self.assertEqual(pilot.verified_automatic_T(source2,controls),3439)
        controls["final_T"]=3450
        with self.assertRaisesRegex(pilot.V319Blocked,
                                    "MANUAL_FINAL_T_NOT_ALLOWED"):
            pilot.verified_automatic_T(source,controls)
        controls["final_T"]=None
        source2["T"]=3450
        with self.assertRaisesRegex(pilot.V319Blocked,
                                    "GJFO_FORMULA_DRIFT"):
            pilot.verified_automatic_T(source2,controls)

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
