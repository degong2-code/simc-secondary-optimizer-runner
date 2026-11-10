"""Versioned speed-aware 22-point policy only; no SimC execution."""
import pathlib
import sys
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v290_multiscale_adaptive_policy as old
import v300_multiregion_throughput_resolution as res

class MeasuredGridResolution(unittest.TestCase):
    def test_auto_22_at_200_calls_when_simc_scout_fast(self):
        f=res.choose_points_from_throughput
        self.assertEqual(f([],remaining_calls=200,seconds_available=600),11)
        self.assertEqual(f([0.5,0.5],remaining_calls=200,
                           seconds_available=600),11)
        self.assertEqual(f([0.5]*3,remaining_calls=200,
                           seconds_available=None),11)
        self.assertEqual(f([0.5]*3,remaining_calls=200,
                           seconds_available=600,
                           confirmation_to_scout_iterations=320/35),22)
        self.assertEqual(f([0.5]*3,remaining_calls=200,
                           seconds_available=300,
                           confirmation_to_scout_iterations=320/35),11)
        self.assertEqual(f([0.5]*3,remaining_calls=200,
                           seconds_available=1600,
                           confirmation_to_scout_iterations=320/35),31)
        self.assertEqual(f([0.5]*3,remaining_calls=200,
                           seconds_available=2500,
                           confirmation_to_scout_iterations=320/35),41)
        self.assertEqual(f([20.]*3,remaining_calls=200,
                           seconds_available=500),5)
        self.assertEqual(f([1.]*3,remaining_calls=10,
                           seconds_available=1000),7)
        with self.assertRaisesRegex(old.PolicyBlocked,
                                    "PERCENT_GRID_ITERATION_RATIO"):
            f([1.]*3,remaining_calls=200,seconds_available=1000,
              confirmation_to_scout_iterations=0.5)

if __name__=="__main__":
    unittest.main()
