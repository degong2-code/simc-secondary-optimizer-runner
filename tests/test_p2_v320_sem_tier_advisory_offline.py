"""v320 SEM iteration-budget advisory focused tests; Native 0."""
from __future__ import annotations
import math
import unittest
from runner import v320_idea001_sem_tier_advisory as a

S=a.STATS

def row(v,mean,sem,n,samples):
    return {"target":dict(zip(S,v)),"dps_mean":float(mean),
            "dps_sem":float(sem),"iterations":n,"samples":samples}

class V320Advisory(unittest.TestCase):
    def setUp(self):
        self.anchor=row((710,1088,1033,276),183000,270,320,319)

    def test_screen_obviously_lower_candidate_not_a_95_global_claim(self):
        o=a.recommend(row((0,1398,1398,311),181000,800,35,34),self.anchor)
        self.assertEqual(o["suggested_iterations"],35)
        self.assertEqual(o["decision"],"SCREEN_LOWER_PRIORITY_NOT_95_EXCLUSION")
        self.assertFalse(o["selection_multiplicity_95_proven"])

    def test_mid120_only_when_reference_error_and_gap_allow(self):
        o=a.recommend(row((345,1088,1398,276),184200,800,35,34),self.anchor)
        self.assertEqual(o["suggested_iterations"],120)
        self.assertTrue(35<o["estimated_required_candidate_iterations"]<=120)
        self.assertFalse(o["requested_tier_is_executable_in_v291"])
        self.assertAlmostEqual(o["projected_sem_120_not_native"],
                               800*math.sqrt(34/119))

    def test_direct320_when_mid_cannot_resolve_observed_gap(self):
        o=a.recommend(row((345,1088,1398,276),183800,800,35,34),self.anchor)
        self.assertEqual(o["suggested_iterations"],320)
        self.assertTrue(120<o["estimated_required_candidate_iterations"]<=320)

    def test_reference_SEM_floor_and_selected_tie_no_fabricated_95(self):
        o=a.recommend(row((345,1088,1398,276),183400,800,35,34),self.anchor)
        self.assertIsNone(o["estimated_required_candidate_iterations"])
        self.assertEqual(o["decision"],"CLOSE_PAIR_320_MAY_NOT_RESOLVE_RANKING")
        self.assertFalse(o["global_optimum_proven"])

    def test_promising_new_leader_must_confirm_at_320(self):
        o=a.recommend(row((345,1088,1398,276),186000,800,35,34),self.anchor)
        self.assertEqual(o["decision"],"CONFIRM_APPARENT_NEW_LEADER_320")
        self.assertEqual(o["suggested_iterations"],320)

    def test_same_target_is_calibration_not_challenger(self):
        v=(710,1088,1033,276)
        o=a.recommend(row(v,183500,800,35,34),self.anchor)
        self.assertIsNone(o["suggested_iterations"])

    def test_rejects_fake_nan_mismatched_samples_and_bad_targets(self):
        for changed in (
            {"dps_sem":float("nan")},
            {"samples":35,"iterations":34},
            {"iterations":120},
            {"target":{"crit_rating":100}},
        ):
            candidate=row((345,1088,1398,276),184200,800,35,34)
            candidate.update(changed)
            with self.assertRaises(a.TierAdvisoryBlocked):
                a.recommend(candidate,self.anchor)

    def test_existing_v291_has_only_35_320_typed_modes_not_120(self):
        from runner import v291_durable_multiscale_native_runner as v291
        identity={"scout_iterations":35,"confirm_iterations":320}
        self.assertEqual(v291._mode("scout",35,identity),"scout")
        self.assertEqual(v291._mode("precision",320,identity),"confirm")
        with self.assertRaisesRegex(v291.LongRunBlocked,
                                    "UNTYPED_SIMC_ITERATION_IDENTITY"):
            v291._mode("precision",120,identity)

if __name__=="__main__":
    unittest.main()
