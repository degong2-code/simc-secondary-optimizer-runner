"""IDEA-002 v328 conditional radius invariants, synthetic Native0."""
import unittest
from unittest import mock
from runner import v328_idea002_evidence_gated_radius as policy

class Tests(unittest.TestCase):
    def state(self,n=3):
        center=(800,800,800,700)
        row={"target":policy.base.legacy.to_target(center),
             "dps_mean":100000.,"dps_sem":300.}
        local=[dict(row,sequence=i) for i in range(n)]
        return {"seed":row,"best":row,"center":center,
                "radius":.065,"local":local}
    def test_ambiguous_native_expands(self):
        radius,why=policy.radius_decision(self.state(),total=3100)
        self.assertAlmostEqual(radius,.104)
        self.assertEqual(why,"EXPAND_UNCERTAIN")
    def test_no_local_evidence_preserves_previous(self):
        self.assertEqual(policy.radius_decision(self.state(1),total=3100)[1],
                         "BASELINE_NO_LOCAL_EVIDENCE")
    def test_regional_proposal_changes_only_candidate_and_radius(self):
        center=(800,800,800,700);candidate=(850,750,800,700)
        req={"adaptive_stage":"regional","region_id":"r0",
             "target":policy.base.legacy.to_target(center),
             "region_center":list(center),"region_radius_fraction":.065,
             "hybrid_method":policy.previous.GRID,"phase":"scout",
             "iterations":35}
        observations=[{"phase":"scout","target":req["target"]}]
        with mock.patch.object(policy.previous,"next_plan",
                   return_value={"next_request":req,"decision":"BASELINE"}), \
             mock.patch.object(policy.previous,"_measured_region_state",
                   return_value={"r0":self.state()}), \
             mock.patch.object(policy.resources,"_candidate",
                   return_value=(candidate,322)):
            result=policy.next_plan(observations,total=3100,
                lower=(0,0,0,0),upper=(2000,2000,2000,2000),
                max_native_calls=64,scout_iterations=35,
                confirmation_iterations=320,initial_global_calls=16,
                confirmation_calls=8)
        self.assertEqual(result["schema"],policy.SCHEMA)
        self.assertEqual(result["decision"],"V328_IDEA002_EXPAND_UNCERTAIN")
        self.assertEqual(tuple(result["next_request"]["target"].values()),candidate)
    def test_source_pairwise_method_is_preserved_exactly(self):
        center=(800,800,800,700)
        req={"adaptive_stage":"regional","region_id":"r0",
             "target":policy.base.legacy.to_target(center),
             "region_center":list(center),"region_radius_fraction":.065,
             "hybrid_method":policy.previous.PAIRFINE,
             "phase":"scout","iterations":35}
        original={"next_request":req,"decision":"V306_ORIGINAL_PAIR"}
        with mock.patch.object(policy.previous,"next_plan",
             return_value=original), \
             mock.patch.object(policy.previous,"_measured_region_state",
             side_effect=AssertionError("Should not mutate or even inspect pair")):
            out=policy.next_plan([],total=3100,lower=(0,0,0,0),
                upper=(2000,2000,2000,2000),max_native_calls=64,
                scout_iterations=35,confirmation_iterations=320,
                initial_global_calls=16,confirmation_calls=8)
        self.assertEqual(out["next_request"],req)
        self.assertEqual(out["decision"],original["decision"])
        self.assertEqual(out["schema"],policy.SCHEMA)
    def test_invalid_original_budget_fails_closed(self):
        with self.assertRaises(policy.PolicyBlocked):
            policy.radius_decision(self.state(),total=3101)
    def test_baseline_policy_remains_distinct(self):
        self.assertNotEqual(policy.SCHEMA,policy.previous.SCHEMA)
if __name__=="__main__":unittest.main()
