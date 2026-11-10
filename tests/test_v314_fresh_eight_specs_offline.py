"""v314 fresh user-built DPS 8x2 matrix and statistical reporting, OFFLINE ONLY.

No synthetic value in this file is passed off as a real SimC observation.
"""
from __future__ import annotations
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))

import v314_fresh_eight_spec_matrix_contract as matrix


def fake_trial(policy,dps,sem,seed):
    rows=[
        {"phase":"scout","target":{k:(200 if i else 2400)
               for i,k in enumerate(matrix.KEYS)},
         "iterations":35,"case_key":policy+"scout",
         "dps_mean":dps-1000,"dps_sem":700,
         "native_sha256":"a"*64},
        {"phase":"precision","target":{k:(300 if i else 2100)
               for i,k in enumerate(matrix.KEYS)},
         "iterations":320,"case_key":policy+"precision",
         "dps_mean":dps,"dps_sem":sem,
         "simc_seed":seed,"native_sha256":"b"*64}]
    report={"completed_cases":2,"native_attempts_cumulative":2,
            "new_native_this_invocation":2,"status":"BUDGET_EXHAUSTED",
            "policy":("v290_multiscale_noisy_simplex_policy_v1" if
                      policy=="v290_original" else
                      "v312_model_guided_multiregion_native_proposal_v1")}
    return matrix.trial_summary(report,rows,9.5,policy_name=policy,
                               original_profile_sha256="c"*64)


class V314CrossSpecMatrixOffline(unittest.TestCase):
    def test_all_sixteen_independent_source_first_dps_profiles(self):
        check=matrix.validate_matrix()
        self.assertEqual((check["specializations"],check["cases"]),(8,16))
        specs={ (v["class"],v["spec"]) for v in matrix.CASES.values()}
        self.assertEqual(specs,{
            ("hunter","marksmanship"),("hunter","beast_mastery"),
            ("mage","arcane"),("mage","frost"),("mage","fire"),
            ("death_knight","frost"),("rogue","subtlety"),
            ("rogue","assassination")})
        self.assertEqual(matrix.CASES[
            "frost_death_knight__wide"]["race"],"human")
        self.assertEqual(len(set(matrix.CASES)),16)
        for case in matrix.CASES:
            obj,ctrl=matrix.select(case)
            self.assertEqual(ctrl["final_T"],obj["final_T"])
            self.assertEqual(ctrl["max_single_stat_percent"],
                             obj["max_single_stat_percent"])
            self.assertEqual(ctrl["consumable_choices"]["diamond_id"],0)
            self.assertEqual(ctrl["oil_hands"],[])
            self.assertEqual(ctrl["targets"],1)
        with self.assertRaisesRegex(ValueError,"EXACT_APPROVED"):
            matrix.select("destruction_warlock__wide")

    def test_same_real_source_required_different_seed_95_separation_not_global(self):
        old=fake_trial("v290_original",185000,210,991)
        new=fake_trial("v312_model_guided",186500,220,992)
        case=matrix.CASES["arcane_mage__narrow"]
        pair=matrix.paired_result(case,old,new)
        self.assertEqual(pair["status"],"PARTIAL_OR_TIME_CAPPED")
        self.assertTrue(pair["95_pairwise_separated"])
        self.assertFalse(pair["winner_selection_bias_corrected"])
        self.assertFalse(pair["global_optimum_proven"])
        self.assertEqual(pair["v290_total_iterations"],355)
        self.assertEqual(pair["v312_total_iterations"],355)
        new["input_profile_sha256"]="d"*64
        with self.assertRaisesRegex(ValueError,
                                    "SAME_PROFILE_AND_TWO_EXPECTED"):
            matrix.paired_result(case,old,new)

    def test_iteration_inequity_is_exposed_and_sixteen_case_aggregate(self):
        cases=[]
        for i,(key,case) in enumerate(matrix.CASES.items()):
            old=fake_trial("v290_original",180000+i*1000,230,i*2+1)
            new=fake_trial("v312_model_guided",180300+i*1000,235,i*2+2)
            old["native_calls"]=new["native_calls"]=matrix.NATIVE_CAP
            old["actual_simc_iterations"]=69765
            new["actual_simc_iterations"]=39840
            p=matrix.paired_result(case,old,new)
            self.assertEqual(p["status"],"COMPLETE_EQUAL_NATIVE_CALLS")
            self.assertTrue(p["different_simc_iteration_budgets"])
            cases.append(p)
        agg=matrix.aggregate(cases)
        self.assertEqual((agg["completed"],agg["coverage_specializations"]),
                         (16,8))
        self.assertTrue(agg["all_sixteen_complete"])
        self.assertEqual(agg["v312_observed_win_count"],16)
        self.assertFalse(agg["familywise_95_proven"])
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            matrix.aggregate([cases[0],cases[0]])


if __name__=="__main__":
    unittest.main()
