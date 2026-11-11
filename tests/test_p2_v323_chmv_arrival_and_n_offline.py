"""v322/v323 original CHMV arrival and variable N planner; Native 0."""
from __future__ import annotations
import unittest
from runner import v322_verified_chmv_arrival as arrival
from runner import v323_continuous_n_sem_wall_advisory as n
K=arrival.STATS
def row(i,phase,it,vector):
    return {"index":i,"phase":phase,"iterations":it,"source":"NEW_NATIVE",
            "target":dict(zip(K,vector)),"dps_mean":100., "dps_sem":2.,
            "case_key":"k%d"%i,"native_sha256":"h%d"%i}
def traced(rows):
    return [{"index":r["index"],"case_key":r["case_key"],
             "native_sha256":r["native_sha256"],"iterations":r["iterations"],
             "source":"NEW_NATIVE","invocation_id":"a"*32,
             "invocation_elapsed_seconds":r["index"]+1.}
            for r in rows]
class ArrivalN(unittest.TestCase):
    def test_exact_and_near_first_hit_and_cumulative_iterations(self):
        target=(300,300,300,100)
        rows=[row(0,"scout",35,target),
              row(1,"scout",35,(301,299,300,100)),
              row(2,"precision",320,target)]
        out=arrival.evaluate(rows,traced(rows),dict(zip(K,target)))
        self.assertEqual(out["exact"]["scout"]["iterations_through_hit"],35)
        self.assertEqual(out["exact"]["confirm"]["iterations_through_hit"],390)
        self.assertEqual(out["near"]["confirm"]["wall_seconds"],3.)
    def test_one_process_clock_required_to_claim_time(self):
        target=(300,300,300,100)
        rows=[row(0,"scout",35,target),row(1,"precision",320,target)]
        tr=traced(rows);tr[-1]["invocation_id"]="b"*32
        out=arrival.evaluate(rows,tr,dict(zip(K,target)))
        self.assertIsNone(out["exact"]["confirm"]["wall_seconds"])
    def test_near_not_exact_distinct_vector(self):
        target=(300,300,300,100)
        rows=[row(0,"scout",35,target),row(1,"precision",320,(301,299,300,100))]
        out=arrival.evaluate(rows,traced(rows),dict(zip(K,target)))
        self.assertIsNone(out["exact"]["confirm"])
        self.assertEqual(out["near"]["confirm"]["L1_rating_distance"],2)
    def test_empirical_wall_includes_noniteration_cost(self):
        model=n.fit_wall([{"iterations":it,"wall_seconds":0.12+0.003*it}
                          for it in (20,40,80,120,240,480)])
        self.assertAlmostEqual(model["slope_seconds_per_iteration"],0.003)
        self.assertAlmostEqual(model["intercept_seconds"],0.12)
    def test_n_is_not_hardcoded_to_35_120_320(self):
        c={"iterations":35,"samples":34,"dps_mean":11000.,"dps_sem":300.}
        r={"iterations":320,"samples":319,"dps_mean":10400.,"dps_sem":100.}
        out=n.recommend(c,r,min_n=16,max_n=640,step=8)
        self.assertTrue(out["next_direct_N_suggestion"] is None or
                        (out["next_direct_N_suggestion"]-16)%8==0)
        self.assertFalse(out["fixed_35_120_320_tiers_required"])
    def test_reference_noise_floor_prevents_false_precision(self):
        c={"iterations":35,"samples":34,"dps_mean":11010.,"dps_sem":300.}
        r={"iterations":320,"samples":319,"dps_mean":11000.,"dps_sem":100.}
        self.assertEqual(n.recommend(c,r)["status"],
                         "CANNOT_RESOLVE_WITH_CANDIDATE_N_ALONE")
    def test_invalid_measurements_blocked(self):
        with self.assertRaises(n.NPlanBlocked):
            n.fit_wall([{"iterations":35,"wall_seconds":.1}])
        with self.assertRaises(arrival.ArrivalBlocked):
            arrival.evaluate([],[],dict(zip(K,(1,1,1,1))))
if __name__=="__main__": unittest.main()
