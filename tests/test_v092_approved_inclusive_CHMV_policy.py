"""v092 approved oil-inclusive total T=B+O; fixed o only, no double-add."""
import copy,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v046_static_item_cache as cache
import v061_scenario_contract as scenario
import v092_approved_inclusive_CHMV_policy as policy
import v091_weapon_oil_external_adapter as oil
import v082_fury_plate_dual_twohand_native as fury_runner
import v084_frost_cloth_1h_frill_native as frost_runner
from test_v091_weapon_oil_external_adapter import frost,fury,BIN,REV,FROST_TARGET,FURY_TARGET

class V092Inclusive(unittest.TestCase):
    def test_reference_334_general_baseline_and_one_oil(self):
        b=policy.calculate(3150,oil.PER_WEAPON)
        self.assertEqual(b["base_B"],3150)
        self.assertEqual(b["final_T"],3182)
        self.assertEqual(policy.effective_candidate(
            FROST_TARGET,b),{"crit_rating":916,"haste_rating":816,
                 "mastery_rating":800,"versatility_rating":650})
        self.assertEqual(b["total_formula"],"T=G+J+F+O")

    def test_dual_common_and_fury_both_oils(self):
        both={s:oil.PER_WEAPON[s]*2 for s in scenario.STATS}
        self.assertEqual(policy.calculate(3150,both)["final_T"],3214)
        self.assertEqual(policy.calculate(3350,both)["final_T"],3414)
        self.assertEqual(policy.calculate(3350,dict.fromkeys(both,0))
                         ["final_T"],3350)

    def test_optimal_base_total_excludes_oil_for_scheduler(self):
        with tempfile.TemporaryDirectory() as td:
            p,c,f=fury(td)
            runs=[]
            for hands in ([],["main_hand"],["off_hand"],
                          ["main_hand","off_hand"]):
                z=oil.prepare(p,c,f,cache.empty_cache(),
                              "dual_two_hand",hands)
                req=oil.propose(z,FURY_TARGET,fury_runner.DECLARED_F,
                      BIN,REV,35,pathlib.Path(td)/(str(len(hands))+str(hands))/
                      "result.json")
                n=len(hands)
                self.assertEqual(z["prepared"]["T"],3350)
                self.assertEqual(z["approved_total"]["final_T"],3350+32*n)
                self.assertEqual(req["target"]["crit_rating"],838+16*n)
                self.assertEqual(req["target"]["haste_rating"],838+16*n)
                self.assertEqual(req["raw_gear_override"]["crit_rating"],838+16*n)
                self.assertEqual(req["raw_gear_override"]["haste_rating"],673+16*n)
                self.assertEqual(req["raw_gear_override"]["mastery_rating"],837)
                self.assertEqual(req["raw_gear_override"]["versatility_rating"],837)
                self.assertEqual(sum(req["target"].values()),3350+32*n)
                self.assertEqual(req["official_total"],3350+32*n)
                self.assertEqual(req["v092_base_target"],FURY_TARGET)
                self.assertEqual(req["v092_base_B"],3350)
                self.assertFalse(req["oil_fungible"])
                runs.append(req)
            self.assertEqual(len({q["case_key"] for q in runs}),4)
            self.assertNotEqual(runs[1]["case_key"],runs[2]["case_key"])

    def test_explicit_final_manual_user_entry_converts_to_base(self):
        with tempfile.TemporaryDirectory() as td:
            _,doc,_=frost(td)
            requested=3182
            x=policy.approved_manual_total_to_legacy_B(
                 doc,requested,oil.PER_WEAPON)
            self.assertEqual(x["manual_total_scope"],
                             "INCLUDES_G_J_F_O")
            self.assertEqual(x["user_entered_total_T"],requested)
            self.assertEqual(x["legacy_v061_base_B"],3150)
            self.assertEqual(x["approved_accounting"]["final_T"],requested)
            self.assertEqual(x["normalized_legacy_B"]["budget"]["T"],3150)

    def test_manual_less_than_O_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            _,doc,_=frost(td)
            with self.assertRaisesRegex(policy.TotalPolicyBlocked,
                                         "USER_TOTAL_LESS_THAN_FIXED_O"):
                policy.approved_manual_total_to_legacy_B(doc,31,oil.PER_WEAPON)
            with self.assertRaisesRegex(policy.TotalPolicyBlocked,
                                         "USER_INCLUSIVE_TOTAL_REQUIRED"):
                policy.approved_manual_total_to_legacy_B(doc,3182.0,oil.PER_WEAPON)

    def test_fixed_O_is_not_fungible_or_spent_twice(self):
        p=policy.calculate(3150,oil.PER_WEAPON)
        with self.assertRaisesRegex(policy.TotalPolicyBlocked,
                                    "BASE_CHMV_SUM_MISMATCH"):
            policy.effective_candidate(dict(FROST_TARGET,crit_rating=916),p)
        with self.assertRaisesRegex(policy.TotalPolicyBlocked,
                                    "BASE_CHMV_SUM_MISMATCH"):
            policy.effective_candidate(
                {"crit_rating":916,"haste_rating":816,"mastery_rating":800,
                 "versatility_rating":650},p)

    def test_F_is_not_double_subtracted_when_oil_added(self):
        with tempfile.TemporaryDirectory() as td:
            prof,doc,fill=frost(td)
            p=oil.prepare(prof,doc,fill,cache.empty_cache(),
                          "one_hand_frill",["main_hand"])
            q=oil.propose(p,FROST_TARGET,frost_runner.F_DECLARED,
                          BIN,REV,35,pathlib.Path(td)/"native.json")
            self.assertEqual(q["raw_gear_override"]["crit_rating"],751)
            self.assertEqual(q["raw_gear_override"]["haste_rating"],816)
            self.assertEqual(q["target"]["crit_rating"],916)
            self.assertEqual(q["target"]["haste_rating"],816)
            self.assertEqual(q["v092_base_target"]["crit_rating"],900)
            self.assertEqual(q["official_total"],3182)
            self.assertEqual(sum(q["raw_gear_override"].values()),3017)
            self.assertEqual(sum(q["static_flask_F_vector"].values()),165)
            self.assertEqual(sum(q["target"].values()),3182)

if __name__=="__main__":unittest.main()
