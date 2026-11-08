"""P3-HAB: mandatory <50% per stat of FINAL oil-inclusive T.

Old max_fraction=0.5 was inclusive on base B. New user rule is a separate,
non-overridable global hard cap with one stat's FINAL share strictly < 0.5.
Synthetic tests only. No real SimC measurement or effect gate.
"""
import copy
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v061_scenario_contract as sc
import v063_numeric_injection as num
import v065_v015_scheduler_adapter as search
from test_v061_scenario_contract import manual
from test_v064_adaptive_evaluator_port import make_fixture


class FinalStrictHalf(unittest.TestCase):
    def test_integer_boundary_even_odd_and_oil(self):
        z={s:0 for s in sc.STATS}
        even=sc.strict_final_half_base_caps(3000,z)
        odd=sc.strict_final_half_base_caps(3107,z)
        self.assertEqual(set(even.values()),{1499})
        self.assertEqual(set(odd.values()),{1553})
        o=dict(z,crit_rating=16,haste_rating=16)
        x=sc.strict_final_half_base_caps(3000,o)
        self.assertEqual(x["crit_rating"],1499)
        self.assertEqual(x["haste_rating"],1499)
        self.assertEqual(x["mastery_rating"],1515)
        for s in sc.STATS:
            self.assertLess(2*(x[s]+o[s]),3032)
            self.assertGreaterEqual(2*(x[s]+o[s]+1),3032)

    def test_manual_final_oil_boundary_is_strict_and_unoverrideable(self):
        doc=manual()
        doc["constraints"]["max_fraction"]={s:1.0 for s in sc.STATS}
        # Existing source says manual_total is B=3000, selected oil is O=32.
        self.assertEqual(sc.normalize(doc)["budget"]["T"],3000)
        doc["constraints"]["minimum_rating"]["crit_rating"]=1499
        self.assertEqual(sc.normalize(doc)["budget"]["T"],3000)
        doc["constraints"]["minimum_rating"]["crit_rating"]=1500
        with self.assertRaisesRegex(sc.ScenarioInvalid,
                                    "UNFEASIBLE_MANUAL_TOTAL_BOUNDS"):
            sc.normalize(doc)
        doc["constraints"]["minimum_rating"]["crit_rating"]=0
        doc["constraints"]["min_fraction"]["haste_rating"]=.51
        with self.assertRaisesRegex(sc.ScenarioInvalid,
                                    "UNFEASIBLE_MANUAL_TOTAL_BOUNDS"):
            sc.normalize(doc)

    def test_scheduler_floor_and_exact_native_injection_use_same_caps(self):
        c,b,_,_=make_fixture()
        base=b["budget"]["T_official"]
        strict=sc.strict_final_half_base_caps(
            base,c["budget"]["external_temporary_rating"])
        B,lo,hi=search.bounds(c,b)
        self.assertEqual(B,base)
        for i,s in enumerate(sc.STATS):
            self.assertLessEqual(hi[i],strict[s])
            self.assertLess(2*(hi[i]+c["budget"][
                "external_temporary_rating"][s]),
                B+sum(c["budget"]["external_temporary_rating"].values()))
        c2=copy.deepcopy(c)
        b2=copy.deepcopy(b)
        # The v063 static injection must independently reject a one-point
        # over-cap candidate, even if the scheduler is bypassed.
        cap=hi[0]
        over={s:0 for s in sc.STATS}
        over["crit_rating"]=cap+1
        over["haste_rating"]=B-cap-1
        with self.assertRaisesRegex(num.InjectionError,
                                    "TARGET_OUTSIDE_SPECIAL_FLOOR_OR_CAP"):
            num.check_target(c2,b2,over)
        # Fixed special L/E impossible to satisfy -> pre-Native failure.
        b2["effective_floor_if_possible"]["crit_rating"]=strict[
            "crit_rating"]+1
        with self.assertRaisesRegex(search.SchedulerBlocked,
                                    "BOUNDS_NOT_FEASIBLE"):
            search.bounds(c2,b2)

    def test_generated_neighbors_cannot_reach_exact_half_even(self):
        B=3000
        O={s:0 for s in sc.STATS}
        hi=tuple(sc.strict_final_half_base_caps(B,O)[s] for s in sc.STATS)
        lo=(0,0,0,0)
        center=(750,750,750,750)
        result=search.neighbors(center,749,B,lo,hi,{center})
        self.assertTrue(result)
        self.assertTrue(all(max(v)<1500 and sum(v)==B for v in result))
        self.assertNotIn((1500,0,750,750),result)


if __name__=="__main__":
    unittest.main()
