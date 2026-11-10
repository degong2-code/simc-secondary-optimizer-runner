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
import v299_multiregion_percent_policy as multiregion


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
        first_hit_by_peak=[None]*len(peaks)
        best_at_5000=None
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
            if requested_iterations<=5000:
                best_at_5000=max(best if best_at_5000 is None else
                                 best_at_5000,observed)
            for pi,(peak,_,_) in enumerate(peaks):
                if (first_hit_by_peak[pi] is None and
                        baseline._distance(vec,peak)<=self.B*.05):
                    first_hit_by_peak[pi]={
                        "call":used+1,
                        "cumulative_iterations":requested_iterations}
            rows.append({"target":q["target"],"iterations":q["iterations"],
                         "dps_mean":observed,
                         "dps_sem":500. if q["phase"]=="scout" else 150.})
        return {"native_requests":len(rows),
                "requested_iterations":requested_iterations,
                "unique_vectors":len({baseline.legacy.key(x["target"])
                                       for x in rows}),
                "global_proposals":global_calls,
                "best_synthetic_score":round(best,3),
                "first_hit_per_peak_5pct_B":first_hit_by_peak,
                "best_at_5000_iterations":(
                    round(best_at_5000,3)
                    if best_at_5000 is not None else None),
                "distance_from_nearest_peak":min(
                    baseline._distance(best_vec,peak)
                    for peak,_,_ in peaks),
                "planning_elapsed_seconds":round(time.monotonic()-start,3),
                "best":best_vec}

    def blended(self, every_nth_global):
        """Keep most original global targets; selectively inject grid targets."""
        count=[0]
        def plan(rows, **kwargs):
            regular=baseline.next_plan(rows,**kwargs)
            if (regular["status"] == "NEXT_NATIVE_PROPOSED" and
                    regular["next_request"]["phase"] == "scout" and
                    "GLOBAL" in regular["decision"]):
                count[0]+=1
                if count[0] % every_nth_global == 0:
                    return grid.next_plan(rows,**kwargs)
            return regular
        return plan

    def test_reference_pool_generation_cost_and_bounds(self):
        # CPU-only microbenchmark: these are NOT SimC runtime seconds.
        for lo,hi,label in (
                ((0,165,0,0),(1864,1864,1864,1864),"flask_floor"),
                ((1200,1500,0,0),(1864,1864,500,500),
                 "asymmetric_locked")):
            for points in (7,11,21,41):
                started=time.monotonic()
                candidates=grid.reference_pool(
                    self.B,lo,hi,points,max_pool=2048)
                elapsed=time.monotonic()-started
                self.assertTrue(candidates)
                self.assertLessEqual(len(candidates),2048)
                self.assertTrue(all(baseline.legacy.eligible(
                    vec,self.B,lo,hi) for vec,_,_ in candidates))
                print("P2_GRID_POOL_CPU_ONLY "+
                      json.dumps({"bounds":label,"points":points,
                                  "candidate_count":len(candidates),
                                  "elapsed_seconds":round(elapsed,4)},
                                 sort_keys=True),flush=True)

    def test_equal_case_budget_synthetic_multimodal_comparison(self):
        records={}
        for name,peaks in self.PEAKS.items():
            for p,_,_ in peaks:
                self.assertEqual(sum(p),self.B)
                self.assertTrue(baseline.legacy.eligible(
                    p,self.B,self.LOWER,self.UPPER))
            modes={"v290":baseline.next_plan,
                   "v298_opt_in":grid.next_plan,
                   "grid_every_2_global":self.blended(2),
                   "grid_every_3_global":self.blended(3),
                   "grid_every_4_global":self.blended(4),
                   "regional_grid_11":multiregion.next_plan,
                   "regional_grid_22":lambda rows,**kw:
                       multiregion.next_plan(
                           rows,reference_points=22,**kw)}
            results={name:self.compare(peaks,strategy)
                     for name,strategy in modes.items()}
            self.assertTrue(all(v["native_requests"] == 112
                                for v in results.values()))
            # A difference in total requested iterations is reported,
            # never relabeled as an equal-CPU/equal-iteration victory.
            records[name]=results
            print("P2_PERCENT_GRID_SYNTHETIC "+
                  json.dumps({"shape":name,**results},sort_keys=True),
                  flush=True)
        self.assertEqual(set(records),set(self.PEAKS))


if __name__=="__main__":
    unittest.main()
