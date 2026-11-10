"""Multi-region normalized-grid proposal tests; fake DPS/no Native only."""
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v290_multiscale_adaptive_policy as base
import v298_adaptive_percent_grid as grid
import v299_multiregion_percent_policy as regions


class RegionPolicy(unittest.TestCase):
    B=3107
    LO=(50,0,0,0)
    HI=(1864,1864,1864,1864)
    def observations(self):
        vecs=[
            ((736,900,736,735),188000),
            ((1090,1250,400,367),194000),
            ((50,1864,1192,1),192000),
            ((1500,600,500,507),185000),
        ]
        return [dict(target=base.legacy.to_target(v),
                     iterations=35,dps_mean=dps,dps_sem=200)
                for v,dps in vecs]

    def test_diagonal_moves_preserve_exact_B_and_bounds(self):
        observed={base.legacy.key(self.observations()[0]["target"])}
        anchor=next(iter(observed))
        moves=list(regions._diagonal_neighbors(
            anchor,round(self.B*.03),self.B,self.LO,self.HI,observed))
        self.assertGreaterEqual(len(moves),6)
        for vec,moved in moves:
            self.assertTrue(base.legacy.eligible(
                vec,self.B,self.LO,self.HI))
            self.assertEqual(moved,base._distance(vec,anchor))
            self.assertEqual(sum(x>y for x,y in zip(vec,anchor)),2)
            self.assertEqual(sum(x<y for x,y in zip(vec,anchor)),2)

    def test_ranked_regions_do_not_collapse_to_one_incumbent(self):
        rows=self.observations()
        by,ident=base._best_by_vector(rows,self.B,self.LO,self.HI)
        centers=regions._regions(by,total=self.B)
        self.assertGreaterEqual(len(centers),3)
        self.assertEqual(centers[0],(1090,1250,400,367))
        self.assertTrue(all(base._distance(a,b)>=self.B*.10-1
                            for i,a in enumerate(centers)
                            for b in centers[i+1:]))

    def test_global_then_regional_refinement_feasible_and_unique(self):
        params=dict(total=self.B,lower=self.LO,upper=self.HI,
                    max_native_calls=112,scout_iterations=35,
                    confirmation_iterations=320,max_iterations=320,
                    reference_points=22,initial_global_calls=2)
        row=self.observations()
        first=regions.next_plan(row,native_calls_used=4,**params)
        self.assertEqual(first["status"],"NEXT_NATIVE_PROPOSED")
        self.assertEqual(first["decision"],
                         "MULTIREGION_LOCAL_PERCENT_DIAGONAL")
        self.assertGreaterEqual(first["regional_center_count"],3)
        vec=base.legacy.key(first["next_request"]["target"])
        self.assertTrue(base.legacy.eligible(
            vec,self.B,self.LO,self.HI))
        self.assertNotIn(vec,{base.legacy.key(r["target"]) for r in row})
        early=regions.next_plan(row[:1],native_calls_used=1,**params)
        self.assertEqual(early["decision"],"MULTIREGION_GLOBAL_COVERAGE")
        self.assertTrue(base.legacy.eligible(
            base.legacy.key(early["next_request"]["target"]),
            self.B,self.LO,self.HI))

    def test_no_observations_and_precision_still_use_v290(self):
        params=dict(total=self.B,lower=self.LO,upper=self.HI,
                    max_native_calls=112,scout_iterations=35,
                    confirmation_iterations=320,max_iterations=320)
        base_first=base.next_plan([],native_calls_used=0,**params)
        region_first=regions.next_plan(
            [],native_calls_used=0,reference_points=22,**params)
        self.assertEqual(region_first,base_first)
        with self.assertRaisesRegex(base.PolicyBlocked,
                                    "MULTIREGION_INITIAL_GLOBAL_CALLS"):
            regions.next_plan([],native_calls_used=0,
                              reference_points=22,
                              initial_global_calls=112,**params)
        with self.assertRaisesRegex(base.PolicyBlocked,
                                    "PERCENT_GRID_RESOLUTION"):
            regions.next_plan([],native_calls_used=0,
                              reference_points=42,**params)


if __name__=="__main__":
    unittest.main()
