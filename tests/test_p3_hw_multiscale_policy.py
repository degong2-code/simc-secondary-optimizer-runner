"""Scalable policy offline regression: no SimC calls or DPS fabrication."""
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v290_multiscale_adaptive_policy as p

class Multiscale(unittest.TestCase):
    B=3107
    lo=(50,0,0,0)
    hi=(1553,1553,1553,1553)

    def _call(self, rows, used, cap=2000):
        return p.next_plan(rows,total=self.B,lower=self.lo,upper=self.hi,
                           native_calls_used=used,max_native_calls=cap,
                           scout_iterations=64,confirmation_iterations=320,
                           max_iterations=2560)

    def test_projection_boundary_and_cap_preserve_full_budget(self):
        for n in range(1,400):
            w=tuple(-__import__("math").log(max(1e-12,p._halton(n,base)))
                    for base in (2,3,5,7))
            vec=p._apportion(self.B,self.lo,self.hi,w)
            self.assertEqual(sum(vec),self.B)
            self.assertTrue(all(l<=v<=h for v,l,h in zip(vec,self.lo,self.hi)))
        pool=list(p._global_pool(self.B,self.lo,self.hi,100))
        self.assertEqual(len(pool),len(set(pool)))
        self.assertGreaterEqual(len(pool),50)

    def test_budget_2000_does_not_mean_six_and_candidates_vary(self):
        rows=[]; seen=set(); phases=set()
        for k in range(128):
            result=self._call(rows,k)
            self.assertEqual(result["status"],"NEXT_NATIVE_PROPOSED")
            q=result["next_request"];v=tuple(q["target"][s] for s in p.STATS)
            self.assertEqual(sum(v),self.B)
            self.assertTrue(all(lo<=v[i]<=hi for i,(lo,hi) in enumerate(
                zip(self.lo,self.hi))))
            self.assertNotIn((v,q["iterations"]),seen)
            seen.add((v,q["iterations"]))
            phases.add(q["phase"])
            # Deterministic synthetic oracle tests scheduler ONLY, never DPS.
            mean=185000 - .004*sum((x-y)**2 for x,y in zip(
                v,(750,900,730,727)))
            rows.append({"target":q["target"],"iterations":q["iterations"],
                         "dps_mean":mean,"dps_sem":
                         650. if q["phase"]=="scout" else 150.})
        self.assertGreater(len({tuple(r["target"][s] for s in p.STATS)
                                for r in rows}),70)
        self.assertIn("scout",phases)
        self.assertIn("precision",phases)
        self.assertEqual(self._call(rows,2000)["status"],"BUDGET_EXHAUSTED")

    def test_zero_allowed_bounds_choose_positive_real_json2_ratings(self):
        # The existing v063 native accepter requires four observed stats.
        # Positive proxies do not assert exact 0-rating optimality.
        lower=(0,0,0,0)
        upper=(1553,1553,1553,1553)
        rows=[]
        for call in range(42):
            proposal=p.next_plan(rows,total=3107,lower=lower,upper=upper,
                                 native_calls_used=call,max_native_calls=2000,
                                 scout_iterations=35,confirmation_iterations=320,
                                 max_iterations=320)
            self.assertEqual(proposal["status"],"NEXT_NATIVE_PROPOSED")
            q=proposal["next_request"]
            v=tuple(q["target"][s] for s in p.STATS)
            self.assertEqual(sum(v),3107)
            self.assertTrue(all(x>=1 for x in v),q)
            rows.append({"target":q["target"],"iterations":q["iterations"],
                         "dps_mean":180000.-float(call*9),
                         "dps_sem":650. if q["phase"]=="scout" else 250.})
        self.assertEqual(rows[0]["target"],p.legacy.to_target(
            p._apportion(3107,(1,1,1,1),upper,(1,1,1,1))))

    def test_stats_not_claimed_global_optimum_and_strict_input(self):
        planned=self._call([],0)
        self.assertFalse(planned["global_optimum_proven"])
        row={"target":planned["next_request"]["target"],"iterations":64,
             "dps_mean":200000.,"dps_sem":650.}
        with self.assertRaisesRegex(p.PolicyBlocked,"DUPLICATE"):
            self._call([row,row],2)
        with self.assertRaisesRegex(p.PolicyBlocked,"OUTSIDE_BOUNDS"):
            self._call([{"target":p.legacy.to_target((1,1,1,1)),
                         "iterations":64,"dps_mean":100000.,"dps_sem":600.}],1)

if __name__=="__main__":unittest.main()
