"""IDEA-006 local geometry screening unit contracts: SYNTHETIC ONLY.

Zero Native; not a measure of real SimC accuracy or algorithm superiority.
"""
from __future__ import annotations

import math
import unittest
import numpy as np
from integration_probes import p2_idea006_historical_local_geometry_screen_offline as screen

K=("crit_rating","haste_rating","mastery_rating","versatility_rating")


def make_row(crit,haste,mastery,total=3400):
    vers=total-crit-haste-mastery
    coords=(crit,haste,mastery,vers)
    if min(coords)<0:
        raise ValueError("NOT_A_FEASIBLE_SYNTHETIC_VECTOR")
    # Exactly a quadratic in local independent CHMV coordinates,
    # deliberately not a claim that true SimC DPS is quadratic.
    y=170000+.2*crit+.4*haste-.5*mastery-(
        (crit-850)**2/2200+
        (haste-700)**2/3000+(mastery-1100)**2/1700)
    return {
        "target":dict(zip(K,coords)),
        "phase":"scout","iterations":35,
        "dps_mean":float(y),"dps_sem":500.0}


class Idea006LocalQuadraticSynthetic(unittest.TestCase):
    def test_local_fit_uses_exact_simplex_coordinates(self):
        rows=[make_row(400+80*i,500+80*j,600+80*k)
              for i in range(8) for j in range(6) for k in range(4)]
        center=np.array((960,700,1000,740),dtype=float)/3400
        pred,count,orientation=screen._fit_at(
            rows,center,.32,return_flat=True)
        self.assertGreaterEqual(count,screen.LOCAL_MIN)
        self.assertTrue(math.isfinite(pred))
        self.assertIsNotNone(orientation)
        self.assertAlmostEqual(float(np.linalg.norm(orientation)),1,places=6)
        self.assertEqual(screen.B,3400)

    def test_sparse_region_returns_no_direction_not_fabricated_dps(self):
        rows=[make_row(600+i*6,700,900) for i in range(8)]
        center=np.array((600,700,900,1200),dtype=float)/3400
        pred,n,axis=screen._fit_at(rows,center,.20,return_flat=True)
        self.assertLess(n,screen.LOCAL_MIN)
        self.assertIsNone(pred)
        self.assertIsNone(axis)

    def test_no_95_or_optimizer_claim_in_screen_contract(self):
        self.assertEqual(screen.SIZES,(128,400,1200))
        self.assertTrue(all(0<r<1 for r in screen.RADII))
        self.assertEqual(screen.SCHEMA,
            "p2_idea006_original9906_local_geometry_48precision_screen_v1")


if __name__=="__main__":
    unittest.main()
