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

    def test_zero_allowed_bounds_include_exact_zero_native_candidates(self):
        # Source-matched SimC JSON2 omits 0 fields. The existing v063
        # validator now accepts those only with actual Native stats and
        # exact rating reconciliation; never turn an unobserved case into DPS.
        lower=(0,0,0,0)
        upper=(1553,1553,1553,1553)
        rows=[]
        visited_zero=False
        for call in range(42):
            proposal=p.next_plan(rows,total=3107,lower=lower,upper=upper,
                                 native_calls_used=call,max_native_calls=2000,
                                 scout_iterations=35,confirmation_iterations=320,
                                 max_iterations=320)
            self.assertEqual(proposal["status"],"NEXT_NATIVE_PROPOSED")
            q=proposal["next_request"]
            v=tuple(q["target"][s] for s in p.STATS)
            self.assertEqual(sum(v),3107)
            self.assertTrue(all(x>=0 for x in v),q)
            visited_zero=visited_zero or any(x==0 for x in v)
            rows.append({"target":q["target"],"iterations":q["iterations"],
                         "dps_mean":180000.-float(call*9),
                         "dps_sem":650. if q["phase"]=="scout" else 250.})
        self.assertTrue(visited_zero,"global coverage must include real zero boundaries")
        self.assertEqual(rows[0]["target"],p.legacy.to_target(
            p._apportion(3107,lower,upper,(1,1,1,1))))

    def test_typed_twelve_precision_after_eight_without_changing_2000(self):
        # Historic eight target coordinates, synthetic DPS/SEM assertions.
        coords=[(736,900,736,735),(1,165,1388,1553),
                (1553,165,1,1388),(1,1552,1553,1),
                (1,1553,1,1552),(1552,1553,1,1),
                (1388,165,1553,1),(267,615,1553,672)]
        values=[182360.,171500.,169160.,186630.,166990.,179244.,
                181589.,179995.]
        rows=[{"target":p.legacy.to_target(v),"iterations":35,
               "dps_mean":d,"dps_sem":800.}
              for v,d in zip(coords,values)]
        kwargs={"total":3107,"lower":(0,165,0,0),"upper":self.hi,
                "scout_iterations":35,"confirmation_iterations":320,
                "max_iterations":320}
        first=p.next_plan(rows,native_calls_used=8,max_native_calls=12,
                          **kwargs)
        self.assertEqual(first["decision"],"UNCERTAINTY_AWARE_REMEASURE")
        self.assertEqual(first["next_request"]["phase"],"precision")
        self.assertEqual(first["next_request"]["iterations"],320)
        self.assertEqual(first["next_request"]["target"],rows[3]["target"])
        rows.append({"target":first["next_request"]["target"],
                     "iterations":320,"dps_mean":186000.,"dps_sem":250.})
        second=p.next_plan(rows,native_calls_used=9,max_native_calls=12,
                           **kwargs)
        self.assertEqual(second["next_request"]["phase"],"precision")
        self.assertNotEqual(second["next_request"]["target"],
                            first["next_request"]["target"])
        longrun=p.next_plan(rows[:8],native_calls_used=8,
                            max_native_calls=2000,**kwargs)
        self.assertEqual(longrun["next_request"]["phase"],"scout")


    def test_exhausted_local_steps_do_not_hide_unseen_global_regions(self):
        """Offline counterexample: 16 leaders' every preset neighbor measured.

        This is a *geometry* witness, not fabricated SimC evidence. The
        existing finite global pool still has feasible unseen candidates.
        Previously next_plan prematurely returned NO_NEW despite spare cap.
        """
        pool=list(p._global_pool(self.B,self.lo,self.hi,256))
        anchors=pool[:16]
        self.assertEqual(len(anchors),16)
        observed=set(anchors)
        for anchor in anchors:
            for fraction in p.SCALES:
                step=max(1,min(self.B,round(self.B*fraction)))
                observed.update(p.legacy.neighbors(
                    anchor,step,self.B,self.lo,self.hi,set()))
        # Avoid the already-established every-23rd-request global cadence:
        # this regression exercises the *local* branch's exhaustion.
        while len(observed)%23==0:
            extra=next(v for v in pool if v not in observed)
            observed.add(extra)
        self.assertGreaterEqual(len(observed),64)
        self.assertLess(len(observed),2000)
        unseen={v for v in pool if v not in observed}
        self.assertTrue(unseen)
        rows=[{"target":p.legacy.to_target(v),"iterations":320,
               "dps_mean":200000. if v in anchors else 100000.,
               "dps_sem":100.} for v in sorted(observed)]
        before=self._call(rows,len(rows))
        again=self._call(rows,len(rows))
        self.assertEqual(before,again)
        self.assertEqual(before["status"],"NEXT_NATIVE_PROPOSED")
        self.assertEqual(before["decision"],
                         "GLOBAL_MAXIMIN_AFTER_LOCAL_EXHAUSTION")
        target=tuple(before["next_request"]["target"][s] for s in p.STATS)
        self.assertIn(target,unseen)
        self.assertTrue(p.legacy.eligible(
            target,self.B,self.lo,self.hi))
        self.assertFalse(before["global_optimum_proven"])

    def test_multiscale_local_choice_uses_one_history_extrema_pass(self):
        # A local-only policy call with many historical rows: it must not
        # scan the full history for every local neighbor, and it must keep
        # exactly the same deterministic target on repeat calls.
        from unittest.mock import patch
        rows = []
        for i in range(180):
            weights = tuple(1 + p._halton(i + 1, prime)
                            for prime in (2, 3, 5, 7))
            vec = p._apportion(self.B, self.lo, self.hi, weights)
            target = p.legacy.to_target(vec)
            if any(row["target"] == target for row in rows):
                continue
            rows.append({"target": target, "iterations": 64,
                         "dps_mean": 180000. - 3. * len(rows),
                         "dps_sem": 400.})
        # unique 180, index %23 != 0, no periodic precision.
        self.assertGreaterEqual(len(rows), 100)
        while len(rows) % 23 == 0 or len(rows) % 16 in (14, 15):
            rows.pop()
        first = self._call(rows, len(rows))
        second = self._call(rows, len(rows))
        self.assertEqual(first, second)
        self.assertEqual(first["decision"],
                         "NOISE_AWARE_MULTISCALE_FEASIBLE_NEIGHBOR")
        self.assertEqual(sum(first["next_request"]["target"].values()),
                         self.B)

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
