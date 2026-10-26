"""Offline user-facing result adapter from the already validated v094 output shape."""
import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v096_unified_product_entry as entry

O={"crit_rating":32,"haste_rating":32,"mastery_rating":0,"versatility_rating":0}
B={"crit_rating":838,"haste_rating":838,"mastery_rating":837,"versatility_rating":837}
T={"crit_rating":870,"haste_rating":870,"mastery_rating":837,"versatility_rating":837}
ALT_B={"crit_rating":503,"haste_rating":838,"mastery_rating":837,"versatility_rating":1172}
ALT_T={"crit_rating":535,"haste_rating":870,"mastery_rating":837,"versatility_rating":1172}

def report():
    return {"schema":"v094_generic_durable_inclusive_adaptive_v1",
        "status":"PASS_MATERIAL_SCOUT_AND_FRESH_CONFIRM",
        "official_formula":"T=G+J+F+O","B":3350,"fixed_O":dict(O),
        "official_final_T":3414,"alternatives":{
            "confidence_for_decision_and_display":0.95,
            "underlying_B":3350,"final_T":3414,"fixed_O":dict(O),
            "observed_unique_targets":3,"observed_best_B":dict(B),
            "observed_best_T":dict(T),"observed_best_dps":203286.6376,
            "observed_best_sem":534.8979,
            "material_alternatives":[{
                "B":dict(ALT_B),"T":dict(ALT_T),
                "dps_mean":201534.1539,"dps_sem":530.0852,
                "observed_relative_dps_loss":0.00862075,
                "fraction_B_moved":0.1,
                "label":"OBSERVED_NEAR_BUT_LOWER_AT_95"}]},
        "confirmation":{"pairwise_direction_supported":True}}

class V097UserResult(unittest.TestCase):
    def test_native_summary_is_absolute_final_rating_not_readding_oil(self):
        z=entry.user_facing_result(report())
        first=z["observed_first_choice"]
        self.assertEqual(z["final_T"],3414)
        self.assertEqual(first["absolute_rating_T"],T)
        self.assertEqual(sum(first["absolute_rating_T"].values()),3414)
        self.assertEqual(first["base_rating_B"],B)
        self.assertEqual(z["confidence_level"],0.95)
        self.assertFalse(z["global_optimum_proven"])
        self.assertEqual(first["simc_sem"],534.8979)
        self.assertEqual(z["material_near_alternatives"][0]["absolute_rating_T"],ALT_T)
        self.assertEqual(z["material_near_alternatives"][0]["observed_dps_loss_pct"],0.862)
        self.assertEqual(z["confirmation_scope"],
                         "TWO_FRESH_SELECTED_CANDIDATES_ONLY_NOT_GLOBAL")
    def test_statistically_unresolved_can_still_have_observed_first(self):
        r=report()
        r["confirmation"]["pairwise_direction_supported"]=False
        z=entry.user_facing_result(r)
        self.assertEqual(z["observed_first_choice"]["absolute_rating_T"],T)
        self.assertFalse(z["confirmation_pair_direction_supported_at_95"])
    def test_no_near_alternative_is_empty_not_invented(self):
        r=report()
        r["alternatives"]["material_alternatives"]=[]
        self.assertEqual(entry.user_facing_result(r)["material_near_alternatives"],[])
    def test_prevent_double_inclusion_or_inconsistent_native_result(self):
        r=report();r["alternatives"]["observed_best_T"]["crit_rating"]+=32
        with self.assertRaisesRegex(entry.EntryBlocked,"RESULT_BASE_O_FINAL_RATING_DRIFT"):
            entry.user_facing_result(r)
    def test_reject_97_percent_or_unaccepted_output(self):
        r=report();r["alternatives"]["confidence_for_decision_and_display"]=0.97
        with self.assertRaisesRegex(entry.EntryBlocked,"RESULT_B_T_OR_CONFIDENCE_DRIFT"):
            entry.user_facing_result(r)
        r=report();r["status"]="PARTIAL_OR_BLOCKED"
        with self.assertRaisesRegex(entry.EntryBlocked,"NATIVE_RESULT_NOT_ACCEPTED"):
            entry.user_facing_result(r)
    def test_drifted_alternatives_summary_does_not_render(self):
        r=report();r["alternatives"]["final_T"]=3478
        with self.assertRaisesRegex(entry.EntryBlocked,"RESULT_B_T_OR_CONFIDENCE_DRIFT"):
            entry.user_facing_result(r)
if __name__=="__main__":unittest.main()
