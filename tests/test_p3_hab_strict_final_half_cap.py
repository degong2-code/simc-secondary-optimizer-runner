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
    def test_new_configurable_inclusive_caps_and_legacy_preservation(self):
        z={s:0 for s in sc.STATS}
        self.assertEqual(set(sc.configurable_final_stat_caps(
            2000,z,50).values()),{1000})
        self.assertEqual(set(sc.configurable_final_stat_caps(
            2000,z,60).values()),{1200})
        self.assertEqual(set(sc.strict_final_half_base_caps(
            2000,z).values()),{999})
        oil=dict(z,crit_rating=16,haste_rating=16)
        # T=2032, 60% inclusive => max final 1219 and oil already reserved.
        caps=sc.configurable_final_stat_caps(2000,oil,60)
        self.assertEqual(caps["crit_rating"],1203)
        self.assertEqual(caps["mastery_rating"],1219)
        self.assertTrue(all(caps[s]+oil[s]<=1219 for s in sc.STATS))
        for bad in (24,101,60.0,True):
            with self.assertRaisesRegex(sc.ScenarioInvalid,
                                        "STAT_CAP_PERCENT_25_TO_100"):
                sc.configurable_final_stat_caps(2000,z,bad)

    def test_normalized_manual_cap_and_scheduler_bound_share_one_policy(self):
        doc=manual()
        doc["constraints"]["max_fraction"]={s:1.0 for s in sc.STATS}
        doc["constraints"]["max_single_stat_percent"]=60
        doc["constraints"]["minimum_rating"]["crit_rating"]=1700
        normalized=sc.normalize(doc)
        self.assertEqual(normalized["scenario"]["constraints"][
            "max_single_stat_percent"],60)
        doc["constraints"]["max_single_stat_percent"]=50
        with self.assertRaisesRegex(sc.ScenarioInvalid,
                                    "UNFEASIBLE_MANUAL_TOTAL_BOUNDS"):
            sc.normalize(doc)
        doc["constraints"]["max_single_stat_percent"]=60
        doc["constraints"]["minimum_rating"]["crit_rating"]=0
        normalized=sc.normalize(doc)
        c,b,_,_=make_fixture()
        b=copy.deepcopy(b)
        b["scenario_digest"]=normalized["scenario_digest"]
        b["effective_floor_if_possible"]={s:0 for s in sc.STATS}
        b["budget"]["T_official"]=3000
        B,lo,hi=search.bounds(normalized,b)
        self.assertEqual(B,3000)
        self.assertEqual(hi[0],1803)
        self.assertEqual(hi[2],1819)
        self.assertTrue(search.eligible((1700,500,400,400),B,lo,hi))
        # Same current scenario with 50% inclusive cannot admit 1700 crit.
        doc["constraints"]["max_single_stat_percent"]=50
        lower=sc.normalize(doc)
        b["scenario_digest"]=lower["scenario_digest"]
        _,_,tight=search.bounds(lower,b)
        self.assertLess(tight[0],1700)

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
