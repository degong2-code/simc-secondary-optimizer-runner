"""Regression of percent-based 21-global / weak shortlist / six-local policy.

No SimC Native is executed. Synthetic DPS rows test only selector geometry.
"""
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v290_multiscale_adaptive_policy as base
import v302_weak_multiregion_zoom as zoom


class WeakZoomPolicy(unittest.TestCase):
    B=3107
    LO=(0,165,0,0)
    HI=(1864,1864,1864,1864)

    def test_nested_exact_residual_global_and_rotated_unbiased(self):
        # The actual integer candidate sets, not just nominal percentages,
        # nest from 11 to 21 to 41. Global upper bounds remain enforced.
        lo,hi=(0,0,0,0),(1200,1200,1200,1200)
        sets={}
        for m in (11,21,41):
            pool=zoom.residual_lattice(2000,lo,hi,m)
            self.assertEqual(len(pool),len(set(pool)))
            self.assertTrue(all(sum(v)==2000 and
                                max(v)<=1200 and min(v)>=0 for v in pool))
            sets[m]=set(pool)
        self.assertTrue(sets[11]<sets[21])
        self.assertTrue(sets[21]<sets[41])

    def test_actual_historical_constraints_and_local_boundaries(self):
        pool=zoom.residual_lattice(self.B,self.LO,self.HI,21)
        self.assertEqual(len(pool),19380)
        self.assertIn((0,1243,1864,0),pool)
        self.assertTrue(all(base.legacy.eligible(
            v,self.B,self.LO,self.HI) for v in pool))
        center=(1152,930,1025,0)
        local=zoom.residual_lattice(self.B,self.LO,self.HI,6,
                                    center=center,radius=202)
        self.assertIn(center,local)
        self.assertGreater(len(local),20)
        self.assertTrue(all(
            sum(v)==self.B and
            all(abs(v[i]-center[i])<=202 for i in range(4))
            and base.legacy.eligible(v,self.B,self.LO,self.HI)
            for v in local))

    def test_loose_uncertainty_preserves_distinct_regions(self):
        rows=[
            {"vector":(932,870,1305,0),"dps_mean":190000.,
             "dps_sem":800.,"iterations":35},
            {"vector":(387,1207,1513,0),"dps_mean":188000.,
             "dps_sem":950.,"iterations":35},
            {"vector":(559,1243,1305,0),"dps_mean":189000.,
             "dps_sem":800.,"iterations":35},
            {"vector":(1360,542,1097,108),"dps_mean":185500.,
             "dps_sem":1000.,"iterations":35},
            {"vector":(0,165,1864,1078),"dps_mean":176000.,
             "dps_sem":500.,"iterations":35},
        ]
        found=zoom.loose_regions(rows,total=self.B,
                                  max_regions=4,relative_loss=.03)
        self.assertGreaterEqual(found["eligible_count"],3)
        self.assertEqual(found["centers"][0],(932,870,1305,0))
        self.assertNotIn((0,165,1864,1078),found["centers"])
        self.assertFalse(found["95_percent_claim"])
        regions=zoom.region_candidates(
            self.B,self.LO,self.HI,found["centers"],
            local_points=6,radius_fraction=.065,
            exclude={tuple(r["vector"]) for r in rows},per_region=6)
        self.assertEqual(len(regions),len({r["target"] for r in regions}))
        self.assertTrue(all(base.legacy.eligible(
            p["target"],self.B,self.LO,self.HI) for p in regions))

    def test_farthest_deterministic_respects_budget(self):
        pool=zoom.residual_lattice(self.B,self.LO,self.HI,11)
        seed=(736,901,735,735)
        a=zoom.bounded_farthest(pool,20,seed=seed,
                                exclude={seed})
        b=zoom.bounded_farthest(pool,20,seed=seed,
                                exclude={seed})
        self.assertEqual(a,b)
        self.assertEqual(len(a),20)
        self.assertEqual(len(a),len(set(a)))
        self.assertNotIn(seed,a)

    def test_no_hard_95_gate_and_invalid_geometry_rejected(self):
        with self.assertRaisesRegex(base.PolicyBlocked,
                                    "P2_ZOOM_LOCAL_PARAMETERS"):
            zoom.residual_lattice(self.B,self.LO,self.HI,6,
                                  center=(3000,0,0,107),radius=100)
        with self.assertRaisesRegex(base.PolicyBlocked,
                                    "P2_ZOOM_LOCAL_GRID_PARAMETERS"):
            zoom.region_candidates(self.B,self.LO,self.HI,
                                   [(1152,930,1025,0)],
                                   local_points=21)


if __name__=="__main__":
    unittest.main()
