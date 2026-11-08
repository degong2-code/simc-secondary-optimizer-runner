"""P3-HV exact observed CHMV direction coverage, no new SimC required."""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"runner"))
import v065_v015_scheduler_adapter as p

# Literal candidate *targets* from P3-HT and P3-HU SHA-verified Native
# receipts; DPS figures are never imputed or used as simulated predictions.
S0=(736,901,735,735)
S1=(425,1212,735,735)
BOUNDS=(0,0,0,0),(3107,3107,3107,3107)
def rows():
    return {S0:[{"dps_mean":182928.28}],
            S1:[{"dps_mean":181777.11}]}
class NativeBudgetDirectionCoverage(unittest.TestCase):
    def test_historical_legacy_chooses_lex_and_ignores_mastery(self):
        original=p.choose_next(rows(),100,3107,*BOUNDS)
        self.assertEqual(original[2]["method"],
                         "V015_LOCAL_MIRROR_FOR_SCOUT_ORDER_ONLY")
        self.assertEqual(original[1][2],735)
    def test_new_coverage_uses_unmeasured_mastery_and_versatility(self):
        anchor,one,proof=p.axis_coverage_choice(rows(),100,3107,*BOUNDS)
        self.assertEqual(sum(one),3107)
        self.assertEqual(proof["new_axes_explored"],2)
        self.assertNotEqual(one[2],735)
        self.assertNotEqual(one[3],735)
        self.assertEqual(proof["coverage_before"]["mastery_rating"],0)
        self.assertGreater(proof["coverage_after"]["mastery_rating"],0)
        self.assertFalse(proof["DPS_predictions_or_effect_simulations_created"])
        self.assertFalse(proof["global_optimum_proven"])
    def test_feasible_L_floor_and_repeated_targets_not_bypassed(self):
        lo=(100,200,700,700);hi=(1200,1200,1200,1200)
        prev={(736,901,735,735):[{"dps_mean":200000.}],
              (636,1001,735,735):[{"dps_mean":199000.}]}
        anchor,candidate,_=p.axis_coverage_choice(prev,20,3107,lo,hi)
        self.assertTrue(p.eligible(candidate,3107,lo,hi))
        self.assertNotIn(candidate,prev)
        self.assertTrue(anchor in prev)
    def test_invalid_or_exhausted_feasible_space_fails_closed(self):
        with self.assertRaisesRegex(p.SchedulerBlocked,"COVERAGE_NO_FEASIBLE"):
            p.axis_coverage_choice({(1,1,1,1):[{"dps_mean":1.}]},
                                   1,4,(1,1,1,1),(1,1,1,1))
if __name__=="__main__": unittest.main()
