"""Nested 11/21/41 final-B candidate sets and sealed opt-in guard."""
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))

import v290_multiscale_adaptive_policy as base
import v301_nested_multiregion_policy as nested


class NestedGridRegression(unittest.TestCase):
    def test_11_final_rating_set_strict_subset_of_21_and_41(self):
        cases=[
            (2000,(0,0,0,0),(1200,1200,1200,1200)),
            (3107,(50,165,0,0),(1864,1864,1864,1864)),
            (3107,(1200,1500,0,0),(1864,1864,500,500)),
            (6214,(1,0,0,0),(3728,3728,3728,3728)),
        ]
        for B,lo,hi in cases:
            sets={}
            for resolution in (6,11,21,41):
                pool=nested.nested_reference_pool(B,lo,hi,resolution)
                points={vec for vec,_ in pool}
                self.assertEqual(len(points),len(pool))
                self.assertTrue(all(
                    base.legacy.eligible(v,B,lo,hi) for v in points))
                sets[resolution]=points
            self.assertTrue(sets[6].issubset(sets[11]))
            self.assertTrue(sets[11].issubset(sets[21]))
            self.assertTrue(sets[21].issubset(sets[41]))
            # This checks actual normalized integer vectors, not just
            # unprojected 0/5/10% reference coordinates.
            if lo==(0,0,0,0):
                self.assertGreater(len(sets[21]),len(sets[11]))
                self.assertGreater(len(sets[41]),len(sets[21]))

    def test_speed_200_calls_selects_21_not_22(self):
        f=nested.choose_points_from_throughput
        self.assertEqual(f([],remaining_calls=200,
                           seconds_available=600),11)
        self.assertEqual(f([0.5]*3,remaining_calls=200,
                           seconds_available=600,
                           confirmation_to_scout_iterations=320/35),21)
        self.assertEqual(f([0.5]*3,remaining_calls=200,
                           seconds_available=300,
                           confirmation_to_scout_iterations=320/35),11)
        self.assertEqual(f([0.5]*3,remaining_calls=200,
                           seconds_available=2500,
                           confirmation_to_scout_iterations=320/35),41)
        self.assertEqual(f([30.]*3,remaining_calls=200,
                           seconds_available=500),6)
        self.assertTrue(all(f([0.5]*3,remaining_calls=200,
                            seconds_available=t,
                            confirmation_to_scout_iterations=320/35)
                            in nested.LEVELS for t in (60,100,300,600,1000,3000)))

    def test_planner_maintains_budget_static_constraints(self):
        kwargs=dict(total=3107,lower=(50,165,0,0),
                    upper=(1864,1864,1864,1864),
                    native_calls_used=1,max_native_calls=100,
                    scout_iterations=35,confirmation_iterations=320,
                    max_iterations=320)
        first=base.next_plan([],**dict(kwargs,native_calls_used=0))
        rows=[dict(target=first["next_request"]["target"],iterations=35,
                   dps_mean=188000.0,dps_sem=450.0)]
        p=nested.next_plan(rows,reference_points=21,**kwargs)
        self.assertEqual(p["status"],"NEXT_NATIVE_PROPOSED")
        v=base.legacy.key(p["next_request"]["target"])
        self.assertTrue(base.legacy.eligible(
            v,3107,kwargs["lower"],kwargs["upper"]))
        self.assertNotEqual(v,base.legacy.key(rows[0]["target"]))
        self.assertIn(p["decision"],(
            "NESTED_MULTIREGION_GLOBAL_COVERAGE",
            "MULTIREGION_LOCAL_PERCENT_DIAGONAL"))
        with self.assertRaisesRegex(base.PolicyBlocked,
                                    "NESTED_PERCENT_GRID_LEVEL"):
            nested.next_plan(rows,reference_points=22,**kwargs)


if __name__=="__main__":
    unittest.main()
