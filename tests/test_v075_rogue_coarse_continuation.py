"""v075: synthetic unit cases only; not substituted for actual Native proof."""
import json
import pathlib
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v075_rogue_coarse_continuation as v075
import v074_rogue_selected_D_high_confirmation as v074
import v065_v015_scheduler_adapter as scheduler

class V075CoarseContinuation(unittest.TestCase):
    def test_coarse_fine_policy_is_only_proposal(self):
        self.assertEqual(v075.COARSE_STEP,350)
        self.assertEqual(v075.FINE_STEP_PLANNED_ONLY,100)
        self.assertEqual(v075.NATIVE_CAP,2)
        self.assertEqual(v075.ITERATIONS,60)

    def test_confirmed_high_d_overrides_identical_old_scout_target(self):
        high=[
         {"target":dict(v074.EXPECTED_A),"dps_mean":223489,"dps_sem":367,
          "dps_samples":319,"status":"PASS_NATIVE_DPS_AND_RATING"},
         {"target":dict(v074.EXPECTED_D),"dps_mean":224438,"dps_sem":365,
          "dps_samples":319,"status":"PASS_NATIVE_DPS_AND_RATING"}]
        self.assertEqual(v075.preferred_high(high)["target"],v074.EXPECTED_D)
        self.assertEqual(v075.preferred_high(high)["dps_samples"],319)

    def test_high_is_selected_without_low_scout_leader(self):
        high=[{"target":dict(v074.EXPECTED_A),"dps_mean":223489,
               "dps_sem":367,"dps_samples":319},
              {"target":dict(v074.EXPECTED_D),"dps_mean":224438,
               "dps_sem":365,"dps_samples":319}]
        low={"target":dict(v074.EXPECTED_D),"dps_mean":230000,
             "dps_sem":800,"dps_samples":59}
        self.assertEqual(v075.preferred_high(high)["dps_mean"],224438)
        self.assertNotEqual(v075.preferred_high(high)["dps_mean"],low["dps_mean"])

    def test_missing_previous_native_blocks_without_new_calls(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            result=v075.run(root/"069",root/"070",root/"071",root/"072",
                       root/"073",root/"074",root/"out")
            self.assertEqual(result,3)
            receipt=json.loads((root/"out"/"V075_RECEIPT.json").read_text())
            self.assertEqual(receipt["status"],"BLOCKED_OR_PARTIAL")
            self.assertEqual(receipt["new_native_calls_this_invocation"],0)

    def test_stats_distance(self):
        from v073_rogue_material_adaptive_scout import moved
        self.assertEqual(moved(v074.EXPECTED_A,v074.EXPECTED_D),350)
        self.assertEqual(sum(v074.EXPECTED_D.values()),3150)

if __name__=="__main__":
    unittest.main()
