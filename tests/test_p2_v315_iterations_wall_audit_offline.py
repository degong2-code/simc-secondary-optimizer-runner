"""P2 v315 iteration/wall audit: synthetic contracts, ZERO SimC."""
from __future__ import annotations

import copy
import unittest

from integration_probes import p2_v315_iteration_wall_real_receipt_analysis_offline as a
from runner import v313_multispec_matrix_contract as m313
from runner import v314_fresh_eight_spec_matrix_contract as m314

POLICIES=a.POLICIES


def receipt(cohort="v313", caseid="frost_mage__wide", wall=(490.,420.),
            iters=(70050,39840), differences=(-.1)):
    case=dict((m313 if cohort=="v313" else m314).CASES[caseid])
    profile="c"*64
    arms={}
    for j,(label,policy) in enumerate(POLICIES.items()):
        arms[label]={
            "policy":policy,"native_calls":1008,
            "actual_simc_iterations":iters[j],
            "measured_seconds":wall[j],
            "confirmed_candidates":24 if j==0 else 16,
            "no_historical_native_results_imported":True,
            "native_file_bytes_rechecked_cache_only":True,
            "input_profile_sha256":profile,
            "best_confirmed_320":{
                "dps":float(190000+j*100),
                "sem":250.,"native_json_sha256":("a" if j==0 else "b")*64,
            }
        }
    return {
        "schema":next(k for k,(label,_) in a.SCHEMAS.items()
                      if label==cohort),
        "case":case,
        "status":"PASS_REAL_TWO_ALGORITHMS_FULL_CAP",
        "source_profile_sha256":profile,
        "trials":arms,
        "scenario_from_existing_native_winner":False,
        "prior_dps_cache_reused":False,
        "default_v290_changed":False,
        "new_profile_generated_in_this_case_workspace":cohort=="v314",
        "historical_completed_profile_imported":False,
        "pairwise_result":{
            "case_id":caseid,
            "status":"COMPLETE_EQUAL_NATIVE_CALLS",
            "different_simc_iteration_budgets":iters[0]!=iters[1],
            "relative_dps_difference_pct":differences,
            "95_pairwise_separated":False,
        }
    }


class P2V315MeasuredResourceAccounting(unittest.TestCase):
    def test_equal_calls_different_iterations_not_same_cost(self):
        row=a.evaluate_receipt(receipt())
        self.assertTrue(row["native_calls_equal"])
        self.assertFalse(row["simc_iterations_equal"])
        self.assertTrue(row["v312_lower_iterations"])
        self.assertTrue(row["v312_faster_wall"])
        self.assertFalse(row["can_fit_simc_seconds_per_iteration_from_these_two_arms"])
        self.assertAlmostEqual(row["v312_wall_ratio_to_v290"],420/490,places=5)
        self.assertAlmostEqual(row["v312_iteration_ratio_to_v290"],39840/70050,places=5)

    def test_more_efficient_iteration_count_does_not_prove_wall_speed(self):
        row=a.evaluate_receipt(receipt(wall=(400,420)))
        self.assertTrue(row["v312_lower_iterations"])
        self.assertFalse(row["v312_faster_wall"])
        self.assertFalse(row["actual_time_to_best_320_by_checkpoint_available"])
        self.assertTrue(row["selected_pair_unadjusted_95_only"])

    def test_strict_identity_duplicate_and_new_profile_requirements(self):
        doc=receipt(cohort="v314",caseid="marksmanship_hunter__wide")
        self.assertEqual(a.evaluate_receipt(doc)["cohort"],"v314")
        bad=copy.deepcopy(doc)
        bad["historical_completed_profile_imported"]=True
        with self.assertRaisesRegex(ValueError,"NEW_PROFILE"):
            a.evaluate_receipt(bad)
        bad=copy.deepcopy(doc)
        bad["trials"]["v290_original"]["actual_simc_iterations"]=-1
        with self.assertRaisesRegex(ValueError,"ITERATIONS_WALL"):
            a.evaluate_receipt(bad)
        with self.assertRaisesRegex(ValueError,"DUPLICATED"):
            a.aggregate([doc,doc])

    def test_aggregate_does_not_claim_decomposed_overhead_or_statistical_win(self):
        rows=[receipt(),receipt("v314","marksmanship_hunter__wide")]
        result=a.aggregate(rows)
        self.assertEqual((result["v313_cases"],result["v314_cases"]),(1,1))
        self.assertEqual(result["v312_iteration_lower_cases"],2)
        self.assertTrue(result["fixed_cost_and_iteration_slope_not_identifiable"])
        self.assertTrue(result["no_equal_iteration_comparison_performed"])
        self.assertFalse(result["familywise_95_proven"])
        self.assertFalse(result["algorithms_changed"])
        self.assertEqual(result["new_real_native_calls"],0)


if __name__=="__main__":
    unittest.main()
