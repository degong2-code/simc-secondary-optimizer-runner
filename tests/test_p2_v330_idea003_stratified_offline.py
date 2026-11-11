"""IDEA-003 pure planner tests: no SimC."""
import unittest
from unittest import mock
from runner import v330_idea003_stratified_reserve as p
from runner import v306_seed_retained_coarse_escape_regions as old
from runner import v291_durable_multiscale_native_runner as durable

T=3107
LO=(0,0,0,0)
HI=(1398,1398,1398,1398)
KW=dict(total=T,lower=LO,upper=HI,max_native_calls=64,scout_iterations=35,
        confirmation_iterations=320,initial_global_calls=16,confirmation_calls=8)

class Tests(unittest.TestCase):
    def test_pool_exact_and_disjoint(self):
        pool,centers,cells=p.partition(T,LO,HI)
        self.assertEqual(len(centers),12)
        self.assertEqual(set(pool),set(v for c in cells for v in c))
        self.assertEqual(sum(map(len,cells)),len(pool))
        self.assertTrue(all(cells))
        self.assertTrue(all(old.base.legacy.eligible(v,T,LO,HI) for v in pool))
    def test_only_reserve_changes(self):
        pool,_,_=p.partition(T,LO,HI)
        rows=[{"target":old.base.legacy.to_target(v),"phase":"scout"}
              for v in pool[:16]]
        for stage in ("global_initial","regional","confirmation","global_reserve"):
            action={"adaptive_stage":stage,"target":rows[0]["target"],
                    "phase":"precision" if stage=="confirmation" else "scout",
                    "iterations":320 if stage=="confirmation" else 35,
                    "hybrid_method":"preserved"}
            proposal={"schema":old.SCHEMA,"decision":"old","next_request":action}
            with mock.patch.object(p.prior,"next_plan",return_value=proposal):
                answer=p.next_plan(rows,**KW)
                self.assertEqual(answer["schema"],p.SCHEMA)
                if stage=="global_reserve":
                    self.assertNotIn(answer["next_request"]["target"],[r["target"] for r in rows])
                    self.assertEqual({k:v for k,v in action.items() if k!="target"},
                         {k:v for k,v in answer["next_request"].items() if k!="target"})
                else:self.assertEqual(answer["next_request"],action)
    def test_zero_budget_no_candidate_and_degenerate(self):
        self.assertIsNone(p.choose([],total=T,lower=LO,upper=HI))
        pool,centers,cells=p.partition(4,(1,1,1,1),(1,1,1,1))
        self.assertEqual(pool,((1,1,1,1),))
        self.assertEqual(len(cells),1)
    def test_deterministic_sparse_cell_coverage(self):
        _,centers,cells=p.partition(T,LO,HI)
        rows=[{"target":old.base.legacy.to_target(v),"phase":"scout"} for v in cells[0][:5]]
        before=p.coverage(rows,total=T,lower=LO,upper=HI)
        v=p.choose(rows,total=T,lower=LO,upper=HI)
        self.assertEqual(v,p.choose(rows,total=T,lower=LO,upper=HI))
        self.assertNotEqual(p.cell_for(v,centers),0)
        after=p.coverage(rows+[{"target":old.base.legacy.to_target(v),"phase":"scout"}],total=T,lower=LO,upper=HI)
        self.assertEqual(after["occupied_cells"],before["occupied_cells"]+1)
if __name__=="__main__":unittest.main()
