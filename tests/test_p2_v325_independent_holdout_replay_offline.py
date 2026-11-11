"""v325 heldout-quality arrival: 12 CHMV, 4 N x2 + holdout2, Native0."""
from __future__ import annotations
import unittest
from runner import v325_independent_holdout_quality_arrival as m

K=m.STATS
def targets():
    return [dict(zip(K,(100+i*10,1000-i*10,1000,900)))
            for i in range(12)]
def fake():
    all_targets=targets()
    rows=[]
    for i,v in enumerate(all_targets):
        for n in m.GRID+(m.HOLDOUT_N,):
            for rep in m.REPS:
                # Better quality is final vector regardless of simulated
                # short-screen seed jitter; source-generated seed distinct.
                dps=100000+i*100
                if n!=m.HOLDOUT_N:
                    dps+=(-1 if rep else 1)*(11-i)*12/n*24
                rows.append({"CHMV":v,"n":n,"rep":rep,
                             "samples":n-1,"dps":dps,"sem":100/n**.5,
                             "wall_seconds":.1+.003*n,
                             "seed":1000+i*100+n*2+rep,
                             "native_sha256":("%064x"%(1000+i*100+n*2+rep))})
    return all_targets,rows
class V325Replay(unittest.TestCase):
    def test_same_candidate_cohort_and_holdout_replay(self):
        candidates,rows=fake()
        out=m.evaluate(candidates,rows)
        self.assertEqual(out["actual_independent_Native"],120)
        self.assertEqual(out["heldout_good_candidate_count"],6)
        self.assertEqual(set(out["by_N"]),set(map(str,m.GRID)))
        self.assertTrue(out["quality_band_is_operational_not_95_equivalence"])
        self.assertIn("first_candidate_already_near_quality",out)
        for n in m.GRID:
            self.assertEqual(len(out["by_N"][str(n)]["final_holdout_regret_pct_by_rep"]),2)
        for result in out["by_N"].values():
            self.assertEqual(len(result["two_independent_screen_replicates"]),2)
            self.assertEqual(result["two_independent_screen_replicates"][0]["screen_iterations"] %
                             len(candidates),0)
    def test_new_havoc_grid_three_reps_without_changing_v326_contract(self):
        candidates,_=fake()
        rows=[]
        grid=(32,48,64,96)
        for i,target in enumerate(candidates):
            for n in grid+(640,):
                for rep in ((0,1) if n==640 else (0,1,2)):
                    rows.append({"CHMV":target,"n":n,"rep":rep,
                        "samples":n-1,"dps":100000+i*100+rep,
                        "sem":400/n**.5,"wall_seconds":0.12+.003*n,
                        "seed":i*100000+n*100+rep,
                        "native_sha256":("%064x"%(i*100000+n*100+rep))})
        result=m.evaluate(candidates,rows,grid=grid,
                          screen_reps=(0,1,2),holdout_reps=(0,1))
        self.assertEqual(result["actual_independent_Native"],168)
        self.assertEqual(result["screen_repetitions"],3)
        self.assertEqual(result["holdout_replicates"],2)
        for n in grid:
            self.assertEqual(len(result["by_N"][str(n)]["screen_runs"]),3)
            self.assertIsNone(result["by_N"][str(n)]["two_independent_screen_replicates"])
    def test_reject_missing_or_duplicate_native_without_fabrication(self):
        candidates,rows=fake()
        with self.assertRaisesRegex(m.ReplayBlocked,
                                    "COMPLETE_DISTINCT_NATIVE_SEEDS"):
            m.evaluate(candidates,rows[:-1])
        with self.assertRaisesRegex(m.ReplayBlocked,
                                    "DUPLICATE_EXACT_RESEARCH_IDENTITY"):
            m.evaluate(candidates,rows+[rows[-1]])
    def test_reject_wrong_T_or_CHMV(self):
        candidates,rows=fake()
        bad=[dict(x) for x in candidates]
        bad[-1]=dict(bad[-1]);bad[-1]["crit_rating"]+=1
        with self.assertRaisesRegex(m.ReplayBlocked,"UNIQUE_SAME_BUDGET_CHMV"):
            m.evaluate(bad,rows)
    def test_reference_seed_is_always_independent_of_screen(self):
        candidates,rows=fake()
        rows[-1]=dict(rows[-1]);rows[-1]["seed"]=rows[0]["seed"]
        with self.assertRaisesRegex(m.ReplayBlocked,
                                    "COMPLETE_DISTINCT_NATIVE_SEEDS"):
            m.evaluate(candidates,rows)
if __name__=="__main__":unittest.main()
