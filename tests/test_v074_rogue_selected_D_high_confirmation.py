"""v074 offline controls; synthetic fixtures are never labeled real Native."""
import json
import pathlib
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v074_rogue_selected_D_high_confirmation as v074

class SelectedDContract(unittest.TestCase):
    def test_one_selected_high_precision_native_only(self):
        self.assertEqual(v074.CAP,1)
        self.assertEqual(v074.ITERATIONS,320)
        self.assertEqual(sum(v074.EXPECTED_D.values()),3150)
        self.assertEqual(v074.EXPECTED_D["crit_rating"],1163)

    def test_actual_material_transfer(self):
        import v073_rogue_material_adaptive_scout as v073
        self.assertEqual(v073.moved(v074.EXPECTED_A,v074.EXPECTED_D),350)

    def test_held_out_confirmation_can_be_unresolved(self):
        a={"target":dict(v074.EXPECTED_A),"dps_mean":223489.67,
           "dps_sem":367.88,"dps_samples":319,"simc_seed":1,
           "status":"PASS_NATIVE_DPS_AND_RATING"}
        d={"target":dict(v074.EXPECTED_D),"dps_mean":223600.0,
           "dps_sem":360.0,"dps_samples":319,"simc_seed":2,
           "status":"PASS_NATIVE_DPS_AND_RATING"}
        r=v074.comparison(a,d,3150)
        self.assertFalse(r["pairwise_direction_supported_by_fresh_approx95"])
        self.assertFalse(r["D_superior_pairwise_unadjusted_approx95"])
        self.assertFalse(r["global_optimum_proven"])
        self.assertFalse(r["v073_scout_data_pooled_with_confirmed_D"])

    def test_held_out_direction_requires_independent_seed(self):
        a={"target":dict(v074.EXPECTED_A),"dps_mean":220000.0,
           "dps_sem":300.0,"dps_samples":319,"simc_seed":42,
           "status":"PASS_NATIVE_DPS_AND_RATING"}
        d={"target":dict(v074.EXPECTED_D),"dps_mean":224000.0,
           "dps_sem":300.0,"dps_samples":319,"simc_seed":42,
           "status":"PASS_NATIVE_DPS_AND_RATING"}
        r=v074.comparison(a,d,3150)
        self.assertFalse(r["D_superior_pairwise_unadjusted_approx95"])
        self.assertFalse(r["distinct_native_seeds"])

    def test_missing_actual_evidence_blocks_zero_native(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            rc=v074.run(root/"069",root/"070",root/"071",root/"072",
                       root/"073",root/"out")
            self.assertEqual(rc,3)
            receipt=json.loads((root/"out"/"V074_RECEIPT.json").read_text())
            self.assertEqual(receipt["status"],"BLOCKED_OR_PARTIAL")
            self.assertEqual(receipt["new_native_calls_this_invocation"],0)

if __name__=="__main__":
    unittest.main()
