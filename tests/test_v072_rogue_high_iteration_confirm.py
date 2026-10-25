"""v072 bounded confirmation tests; synthetic fixtures are NOT Native proof."""
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))
import v072_rogue_high_iteration_confirm as v072
import v061_scenario_contract as scenario
from test_v064_adaptive_evaluator_port import make_fixture


def observation(mean, sem, seed):
    return {"target": {"crit_rating": 813, "haste_rating": 913,
                       "mastery_rating": 712, "versatility_rating": 712},
            "dps_mean": mean, "dps_sem": sem, "simc_seed": seed}


class V072Bounded(unittest.TestCase):
    def test_exact_two_native_cap_and_requested_precision(self):
        self.assertEqual(v072.CAP, 2)
        self.assertEqual(v072.ITERATIONS, 320)
        self.assertEqual(v072.probe.BIN_SHA,
                         "64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e")
        self.assertEqual(v072.V071_NEW_JSON_SHA,
                         "6db7cad804a2c01bb855d3063b9c3e6f71653d4484d853c380c4a541649b95b4")

    def test_overlapping_ci_refuses_winner(self):
        a = observation(224892, 1006, 12)
        b = observation(223167, 1186, 13)
        x = v072.comparison(a, b)
        self.assertIsNone(x["winner_if_supported"])
        self.assertFalse(x["pairwise_winner_supported"])
        self.assertFalse(x["global_optimum_proven"])

    def test_separated_comparison_still_requires_distinct_seeds(self):
        a = observation(225000, 100, 77)
        b = observation(221000, 100, 77)
        x = v072.comparison(a, b)
        self.assertTrue(x["approx_95pct_statistically_separated"])
        self.assertFalse(x["pairwise_winner_supported"])
        self.assertIsNone(x["winner_if_supported"])
        b["simc_seed"] = 78
        y = v072.comparison(a, b)
        self.assertTrue(y["pairwise_winner_supported"])
        self.assertEqual(y["winner_if_supported"], "first")
        self.assertFalse(y["global_optimum_proven"])

    def test_scenario_runtime_change_requires_distinct_identity(self):
        normalized, _, _, _ = make_fixture()
        original = normalized["scenario"]
        altered = json.loads(json.dumps(original))
        altered["runtime"]["confirm_iterations"] = 320
        altered["runtime"]["max_native_calls"] = 2
        high = scenario.normalize(altered)
        self.assertNotEqual(high["scenario_digest"], normalized["scenario_digest"])
        self.assertEqual(high["scenario"]["combat"], original["combat"])
        self.assertEqual(high["scenario"]["equipment"], original["equipment"])

    def test_missing_actual_artifacts_blocks_without_simc(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            code = v072.run(root / "missing_witness",
                            root / "missing_official",
                            root / "missing_scout",
                            root / "out", binary=None)
            self.assertEqual(code, 3)
            report = json.loads((root / "out" / "V072_RECEIPT.json").read_text())
            self.assertEqual(report["new_native_calls_this_invocation"], 0)
            self.assertEqual(report["historical_native_results_reused"], 0)
            self.assertEqual(report["status"], "BLOCKED_OR_PARTIAL")
            self.assertFalse(report["global_optimum_proven"])

    def test_prior_source_sha_violation_is_not_repaired(self):
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td)
            (p / "input.simc").write_bytes(b"tampered")
            self.assertNotEqual(v072.sha(b"tampered"), v072.V071_NEW_JSON_SHA)


if __name__ == "__main__":
    unittest.main()
