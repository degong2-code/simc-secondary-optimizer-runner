"""Optional offline P2 optimizer-policy comparison; no actual SimC DPS.

Runs only from an explicitly triggered one-shot workflow. Synthetic surfaces
do NOT model WoW mechanics. Compare unique proposals, best synthetic observed
height, exact requested iterations, candidate coverage and planning seconds.
"""
import json
import pathlib
import sys
import time
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v290_multiscale_adaptive_policy as baseline
import v298_adaptive_percent_grid as grid


class GridPolicyAudit(unittest.TestCase):
    B=3107
    LOWER=(50,0,0,0)
    UPPER=(1864,1864,1864,1864)
    PEAKS={
      "single_smooth":(((736,900,736,735),190000.,.007),),
      "separated_interior":(((736,900,736,735),188000.,.009),
                            ((245,1450,795,617),192000.,.032)),
      "separated_boundary":(((736,900,736,735),188000.,.009),
                            ((50,1864,1192,1),193000.,.028)),
      "three_disjoint":(((736,900,736,735),188000.,.009),
                        ((245,1450,795,617),192000.,.032),
                        ((1430,305,700,672),191500.,.030)),
      "off_axis_narrow":(((736,900,736,735),188000.,.008),
                         ((1090,1250,400,367),194000.,.055)),
      "off_axis_broad":(((736,900,736,735),189000.,.008),
                        ((350,650,1200,907),192000.,.015)),
    }

    def compare(self, peaks, candidate_policy, budget=112):
        rows=[]
        seen=set()
        best=float("-inf")
        best_vec=None
        requested_iterations=0
        global_calls=0
        start=time.monotonic()
        for used in range(budget):
            plan=candidate_policy(
                rows,total=self.B,lower=self.LOWER,upper=self.UPPER,
                native_calls_used=used,max_native_calls=budget,
                scout_iterations=35,confirmation_iterations=320,
                max_iterations=320)
            self.assertEqual(plan["status"],"NEXT_NATIVE_PROPOSED")
            q=plan["next_request"]
            vec=tuple(q["target"][s] for s in baseline.STATS)
            self.assertTrue(baseline.legacy.eligible(
                vec,self.B,self.LOWER,self.UPPER))
            self.assertNotIn((vec,q["iterations"]),seen)
            seen.add((vec,q["iterations"]))
            if "GLOBAL" in plan["decision"]:
                global_calls+=1
            observed=max(height-weight*baseline._distance(vec,peak)**2
                         for peak,height,weight in peaks)
            if observed>best:
                best,best_vec=observed,vec
            requested_iterations+=q["iterations"]
            rows.append({"target":q["target"],"iterations":q["iterations"],
                         "dps_mean":observed,
                         "dps_sem":500. if q["phase"]=="scout" else 150.})
        return {"native_requests":len(rows),
                "requested_iterations":requested_iterations,
                "unique_vectors":len({baseline.legacy.key(x["target"])
                                       for x in rows}),
                "global_proposals":global_calls,
                "best_synthetic_score":round(best,3),
                "distance_from_nearest_peak":min(
                    baseline._distance(best_vec,peak)
                    for peak,_,_ in peaks),
                "planning_elapsed_seconds":round(time.monotonic()-start,3),
                "best":best_vec}

    def test_equal_case_budget_synthetic_multimodal_comparison(self):
        records={}
        for name,peaks in self.PEAKS.items():
            for p,_,_ in peaks:
                self.assertEqual(sum(p),self.B)
                self.assertTrue(baseline.legacy.eligible(
                    p,self.B,self.LOWER,self.UPPER))
            old=self.compare(peaks,baseline.next_plan)
            new=self.compare(peaks,grid.next_plan)
            self.assertEqual(old["native_requests"],new["native_requests"])
            self.assertEqual(old["native_requests"],112)
            # A difference in total requested iterations is reported,
            # never relabeled as an equal-CPU/equal-iteration victory.
            records[name]={"v290":old,"v298_opt_in":new}
            print("P2_PERCENT_GRID_SYNTHETIC "+
                  json.dumps({"shape":name,"v290":old,"v298_opt_in":new},
                             sort_keys=True),flush=True)
        self.assertEqual(set(records),set(self.PEAKS))


if __name__=="__main__":
    unittest.main()
