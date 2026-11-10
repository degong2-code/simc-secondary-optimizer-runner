"""Opt-in percentage-grid geometry tests; no SimC or inferred DPS."""
import pathlib
import sys
import time
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v290_multiscale_adaptive_policy as old
import v298_adaptive_percent_grid as grid


class PercentageGrid(unittest.TestCase):
    def test_60_percent_11_levels_exact_1920_shell_and_clamped_ratio(self):
        result=grid.reference_pool(
            2000,(0,0,0,0),(1200,1200,1200,1200),11)
        coords={row[0]: row for row in result}
        self.assertIn((1200,400,400,0),coords)
        self.assertEqual(coords[(1200,400,400,0)][1],(10,3,3,0))
        self.assertEqual(grid.bounded_proportional(
            2000,(0,0,0,0),(1200,1200,1200,1200),
            (1200,360,360,0)),(1200,400,400,0))
        self.assertTrue(all(sum(v)==2000 and max(v)<=1200
                            and min(v)>=0 for v,_,_ in result))
        self.assertEqual(len(result),len(coords))
        self.assertGreater(len(result),50)
        self.assertLessEqual(len(result),745)

    def test_o_and_locked_floors_and_inclusive_cap(self):
        # final T=2032, O=(16,16,0,0), inclusive 60% final cap 1219.
        base=2000
        low=(100,165,0,0)
        high=(1203,1203,1219,1219)
        result=grid.reference_pool(base,low,high,11)
        self.assertGreater(len(result),5)
        for v,_,_ in result:
            self.assertTrue(old.legacy.eligible(v,base,low,high))
            self.assertLessEqual(v[0]+16,1219)
            self.assertLessEqual(v[1]+16,1219)
            self.assertGreaterEqual(v[1],165)

    def test_zero_shell_and_fixed_axes_not_error(self):
        self.assertEqual(grid.bounded_proportional(
            500,(0,0,0,0),(500,0,0,0),(0,0,0,0)),(500,0,0,0))
        rows=grid.reference_pool(500,(0,0,0,0),(500,0,0,0),3)
        self.assertEqual({v for v,_,_ in rows},{(500,0,0,0)})
        exact=grid.reference_pool(500,(120,80,300,0),
                                  (120,80,300,0),11)
        self.assertEqual(len(exact),1)
        self.assertEqual(exact[0][0],(120,80,300,0))

    def test_decimal_boundary_integer_reconcile_and_provenance(self):
        for B in (128,3107,6214,9999):
            lo=(3,7,0,0)
            cap=(B*60)//100
            hi=(cap,cap,cap,cap)
            for m in (7,11,17):
                pool=grid.reference_pool(B,lo,hi,m,512)
                self.assertGreater(len(pool),5)
                self.assertEqual(len(pool),len({v for v,_,_ in pool}))
                self.assertTrue(all(old.legacy.eligible(
                    v,B,lo,hi) for v,_,_ in pool))
                self.assertTrue(all(n>=1 for _,_,n in pool))

    def test_points_from_measured_throughput_not_guess(self):
        self.assertEqual(grid.choose_points_from_throughput(
            [],remaining_calls=200,seconds_available=500),11)
        self.assertEqual(grid.choose_points_from_throughput(
            [0.5,0.6],remaining_calls=200,seconds_available=500),11)
        self.assertEqual(grid.choose_points_from_throughput(
            [0.5,0.5,0.5],remaining_calls=200,seconds_available=None),11)
        # 200-call example: measured fast scout and reserved 20% higher
        # iterations can raise the lattice resolution to EXACTLY 22 points.
        self.assertEqual(grid.choose_points_from_throughput(
            [.5,.5,.5],remaining_calls=200,seconds_available=600,
            confirmation_to_scout_iterations=320/35),22)
        self.assertEqual(grid.choose_points_from_throughput(
            [.5,.5,.5],remaining_calls=200,seconds_available=300,
            confirmation_to_scout_iterations=320/35),11)
        self.assertEqual(grid.choose_points_from_throughput(
            [.5,.5,.5],remaining_calls=200,seconds_available=1600,
            confirmation_to_scout_iterations=320/35),31)
        self.assertEqual(grid.choose_points_from_throughput(
            [.5,.5,.5],remaining_calls=200,seconds_available=2500,
            confirmation_to_scout_iterations=320/35),41)
        self.assertEqual(grid.choose_points_from_throughput(
            [20.,20.,20.],remaining_calls=200,seconds_available=500),5)
        self.assertEqual(grid.choose_points_from_throughput(
            [1.,1.,1.],remaining_calls=10,seconds_available=1000),7)
        with self.assertRaisesRegex(old.PolicyBlocked,
                                    "PERCENT_GRID_ITERATION_RATIO"):
            grid.choose_points_from_throughput(
                [1.,1.,1.],remaining_calls=200,seconds_available=1000,
                confirmation_to_scout_iterations=0.5)

    def test_opt_in_no_change_to_default_first_or_precision(self):
        params=dict(total=3107,lower=(0,0,0,0),
                    upper=(1864,1864,1864,1864),native_calls_used=0,
                    max_native_calls=200,
                    scout_iterations=35,confirmation_iterations=320,
                    max_iterations=320)
        base=old.next_plan([],**params)
        opt=grid.next_plan([],**params)
        self.assertEqual(base,opt)
        rows=[dict(target=base["next_request"]["target"],iterations=35,
                   dps_mean=185000.,dps_sem=500.)]
        params["native_calls_used"]=1
        old_next=old.next_plan(rows,**params)
        opt_next=grid.next_plan(rows,**params)
        self.assertEqual(old_next["next_request"]["phase"],"scout")
        self.assertEqual(opt_next["next_request"]["phase"],"scout")
        self.assertIn(opt_next["decision"],
                      ("GLOBAL_PERCENT_GRID_MAXIMIN",
                       "GLOBAL_MAXIMIN_SIMPLEX_COVERAGE"))
        a=tuple(old_next["next_request"]["target"][s] for s in old.STATS)
        b=tuple(opt_next["next_request"]["target"][s] for s in old.STATS)
        observed=tuple(base["next_request"]["target"][s] for s in old.STATS)
        self.assertGreaterEqual(old._distance(b,observed),
                                old._distance(a,observed))
        self.assertTrue(old.legacy.eligible(
            b,3107,params["lower"],params["upper"]))

    def test_reject_genuinely_infeasible_not_rounding(self):
        with self.assertRaisesRegex(old.PolicyBlocked,"PERCENT_GRID_BOUNDS"):
            grid.reference_pool(2000,(0,0,0,0),(300,300,300,300),11)
        with self.assertRaisesRegex(old.PolicyBlocked,
                                    "PERCENT_GRID_RESOLUTION"):
            grid.reference_pool(2000,(0,0,0,0),(1200,)*4,2)
        self.assertEqual(sum(grid.bounded_proportional(
            1000,(0,0,0,0),(600,600,600,600),
            (100,10,1,0))),1000)


if __name__=="__main__":
    unittest.main()
