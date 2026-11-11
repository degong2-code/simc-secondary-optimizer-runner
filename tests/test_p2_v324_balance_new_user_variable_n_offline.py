"""v324 new Balance Druid and arbitrary experimental N source, Native0."""
from __future__ import annotations
import os
import pathlib
import unittest
from unittest import mock
from integration_probes import p2_v319_new_windwalker_v290_v318_real_once as harness
from integration_probes import p2_v324_balance_new_user_variable_n_real_once as study
class V324NewBalanceOffline(unittest.TestCase):
    def test_different_new_dps_specialization_auto_T(self):
        case,controls=harness.new_user_case(
            study.CASE_ID,study.EXPECTED_SPEC)
        self.assertEqual((case["character_class"],case["character_spec"]),
                         ("druid","balance"))
        self.assertEqual(controls["race"],"night_elf")
        self.assertIsNone(controls["final_T"])
        self.assertIsNone(case["final_T"])
        self.assertEqual(case["target_ilevel"],334)
    def test_original_profile_only_iteration_and_json2_changed(self):
        original=("druid=trial\nspec=balance\niterations=320\n"
                  "gear_crit_rating=123\ngear_haste_rating=456\n"
                  "json2=/previous/result.json\n")
        with __import__("tempfile").TemporaryDirectory() as t:
            path=pathlib.Path(t)/"result.json"
            x=study.update_input(original,48,path)
            self.assertEqual(x,original.replace(
                "iterations=320","iterations=48").replace(
                "/previous/result.json",str(path.resolve())))
            with self.assertRaises(study.VariableNBlocked):
                study.update_input(original,35,path)
    def test_N_grid_is_calibration_not_default_tier(self):
        self.assertEqual(len(study.N_GRID),8)
        self.assertNotIn(35,study.N_GRID)
        self.assertEqual(study.EXPECTED_RESEARCH_NATIVE,32)
    def test_explicit_guard_denies_unauthorized_native(self):
        with mock.patch.dict(os.environ,
                             {"P2_V324_NEW_BALANCE_N_SWEEP_ONCE":"0"}):
            with self.assertRaises(study.VariableNBlocked):
                study.main()
    def test_windwalker_old_default_source_stays_compatible(self):
        case,controls=harness.new_user_case()
        self.assertEqual((case["character_class"],case["character_spec"]),
                         ("monk","windwalker"))
        self.assertIsNone(controls["final_T"])
if __name__=="__main__": unittest.main()
