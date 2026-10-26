"""v095 material-distance scout and SEM-guided precision; strictly 95%.

Synthetic observations below are OFFLINE fixtures, never claimed real Native.
"""
from __future__ import annotations
import copy,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v046_static_item_cache as cache
import v091_weapon_oil_external_adapter as oil
import v095_material_precision_policy as choose
import v094_durable_inclusive_adaptive_runner as runtime
from test_v091_weapon_oil_external_adapter import fury,FURY_TARGET,BIN,REV
from test_v093_inclusive_adaptive_scheduler_bridge import simulated_result
import v093_inclusive_adaptive_scheduler_bridge as adapter
import v082_fury_plate_dual_twohand_native as warrior

class V095MaterialAndPrecision(unittest.TestCase):
    def make(self,path):
        profile,doc,filler=fury(path)
        prepared=oil.prepare(profile,doc,filler,cache.empty_cache(),
                            "dual_two_hand",["main_hand","off_hand"])
        session=adapter.prepare(prepared,BIN,REV,35,80)
        a=adapter.request(session,FURY_TARGET,warrior.DECLARED_F,
                          pathlib.Path(path)/"a.json","seed")
        b=adapter.request(session,
                   {"crit_rating":938,"haste_rating":738,
                    "mastery_rating":837,"versatility_rating":837},
                    warrior.DECLARED_F,pathlib.Path(path)/"b.json","seed")
        rows=[adapter.project_native_for_v065(req,
                    simulated_result(req,200000+i*100,650,seed=i+1))
             for i,req in enumerate((a,b))]
        return prepared,rows,a,b

    def test_material_neighbor_reuses_v065_and_real_B_geometry(self):
        with tempfile.TemporaryDirectory() as td:
            p,rows,a,b=self.make(td)
            q=choose.material_neighbor(p["prepared"]["scenario"],
                       p["prepared"]["static_budget"],rows,0.10)
            self.assertEqual(q["base_B"],3350)
            self.assertGreaterEqual(q["rating_transferred"],335)
            self.assertEqual(sum(q["candidate_B"].values()),3350)
            self.assertNotEqual(q["candidate_B"],rows[0]["target"])
            self.assertNotEqual(q["candidate_B"],rows[1]["target"])
            self.assertEqual(q["source"],"v065.neighbors_and_score_direction")
            self.assertTrue(q["near_DPS_not_proven"])

    def test_material_planner_never_marks_unmeasured_as_near(self):
        with tempfile.TemporaryDirectory() as td:
            p,rows,a,b=self.make(td)
            candidate=choose.material_neighbor(p["prepared"]["scenario"],
                    p["prepared"]["static_budget"],rows)
            self.assertFalse(candidate["native_observed"])
            self.assertNotIn("dps_mean",candidate)
            with self.assertRaisesRegex(choose.PlanBlocked,"MATERIAL_FRACTION_RANGE"):
                choose.material_neighbor(p["prepared"]["scenario"],
                    p["prepared"]["static_budget"],rows,0)

    def test_precision_95_unresolved_suggests_bounded_repeat(self):
        with tempfile.TemporaryDirectory() as td:
            _,_,a,b=self.make(td)
            x=simulated_result(a,204530,522,seed=1)
            y=simulated_result(b,203843,487,seed=2)
            x["iterations"]=80;y["iterations"]=80
            p=choose.precision_plan(x,y,400)
            self.assertEqual(p["confidence"],0.95)
            self.assertTrue(p["requires_two_fresh_simc_runs"])
            self.assertGreater(p["suggested_new_iterations_each"],80)
            self.assertLessEqual(p["suggested_new_iterations_each"],400)
            self.assertGreater(p["current_95_halfwidth"],p["current_difference"])
            self.assertNotIn("97",str(p))
            with self.assertRaisesRegex(choose.PlanBlocked,"ONLY_USER_APPROVED_CONFIDENCE_95"):
                choose.precision_plan(x,y,400,confidence=0.97)

    def test_precision_no_repeat_if_already_separated_or_maxed(self):
        with tempfile.TemporaryDirectory() as td:
            _,_,a,b=self.make(td)
            x=simulated_result(a,205000,200)
            y=simulated_result(b,203000,200)
            x["iterations"]=80;y["iterations"]=80
            decision=choose.precision_plan(x,y,400)
            self.assertEqual(decision["reason"],"95_PERCENT_ALREADY_SEPARATED")
            self.assertFalse(decision["requires_two_fresh_simc_runs"])
            x["dps_sem"]=522;y["dps_sem"]=487
            x["dps_mean"]=204530;y["dps_mean"]=203843
            bounded=choose.precision_plan(x,y,80)
            self.assertEqual(bounded["reason"],"TYPED_ITERATION_LIMIT_REACHED")
            self.assertFalse(bounded["requires_two_fresh_simc_runs"])

    def test_observed_close_alternative_can_be_statistically_lower(self):
        base={"crit_rating":838,"haste_rating":838,
              "mastery_rating":837,"versatility_rating":837}
        far={"crit_rating":503,"haste_rating":838,
             "mastery_rating":837,"versatility_rating":1172}
        from test_v094_durable_inclusive_adaptive_runner import ob
        rows=runtime._candidate_summary(
            [ob(base,203286.6376,534.898),
             ob(far,201534.1539,530.085)],3350,
            {"crit_rating":32,"haste_rating":32,
             "mastery_rating":0,"versatility_rating":0})
        self.assertEqual(len(rows["material_alternatives"]),1)
        alt=rows["material_alternatives"][0]
        self.assertTrue(alt["difference_95_separated"])
        self.assertEqual(alt["label"],"OBSERVED_NEAR_BUT_LOWER_AT_95")
        self.assertLess(alt["observed_relative_dps_loss"],0.01)

    def test_new_material_scout_must_be_authorized_by_native_limit(self):
        with tempfile.TemporaryDirectory() as td:
            p,rows,a,b=self.make(td)
            binary=pathlib.Path(td)/"fake-simc"
            binary.write_bytes(b"offline test binary")
            # Wrong SHA of course blocked by the existing identity before
            # any executable/native call can possibly occur.
            ctx=adapter.prepare(p,"a"*64,REV,35,80)
            with self.assertRaisesRegex(runtime.DurableBlocked,"SIMC_BINARY_SHA_CHANGED"):
                runtime.run(ctx,[FURY_TARGET,
                      {"crit_rating":938,"haste_rating":738,
                       "mastery_rating":837,"versatility_rating":837}],
                      warrior.DECLARED_F,binary,pathlib.Path(td)/"fail",
                      scouts=0,material_scouts=1,native_limit=4,cache_only=True)

if __name__=="__main__":unittest.main()
