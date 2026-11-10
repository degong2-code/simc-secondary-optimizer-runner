"""Offline contract tests for adaptive region resources; no SimC Native."""
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))

import v290_multiscale_adaptive_policy as base
import v302_weak_multiregion_zoom as geometry
import v303_adaptive_region_resource_policy as adaptive


class AdaptiveRegionResources(unittest.TestCase):
    B = 3107
    LO = (0, 165, 0, 0)
    HI = (1864, 1864, 1864, 1864)
    SCOUT = 35
    CONFIRM = 320

    def regions(self):
        centers = (
            (800, 800, 800, 707),
            (900, 700, 800, 707),
            (700, 900, 800, 707),
            (800, 700, 900, 707),
        )
        return [
            {"region_id": "r%d" % i, "center": center,
             "radius_fraction": .065}
            for i, center in enumerate(centers)
        ]

    def row(self, region, vector, mean, sem, seq, iterations=35):
        return {
            "region_id": region, "vector": vector,
            "dps_mean": float(mean), "dps_sem": float(sem),
            "sequence": seq, "iterations": iterations,
            "phase": "scout" if iterations == self.SCOUT else "precision",
        }

    def plan(self, observations=None, regions=None, **kwargs):
        return adaptive.next_plan(
            observations or [], total=self.B, lower=self.LO, upper=self.HI,
            regions=self.regions() if regions is None else regions,
            total_scout_calls=160, scout_iterations=self.SCOUT,
            confirmation_iterations=self.CONFIRM, **kwargs
        )

    def test_initialize_regions_reuses_v302_spatial_shortlist(self):
        vectors = (
            (736, 900, 736, 735),
            (1090, 1250, 400, 367),
            (50, 1864, 1192, 1),
            (1500, 600, 500, 507),
        )
        rows = [
            {"vector": vector, "iterations": self.SCOUT,
             "dps_mean": 190000 - i * 100, "dps_sem": 200}
            for i, vector in enumerate(vectors)
        ]
        result = adaptive.initialize_regions(rows, total=self.B)
        self.assertEqual(result["global_seed_count"], 4)
        self.assertFalse(result["global_optimum_proven"])
        self.assertGreaterEqual(len(result["regions"]), 3)
        self.assertEqual(
            {tuple(row["center"]) for row in result["regions"]},
            set(vectors),
        )

    def test_initial_allocation_is_exact_capped_and_reserves_global_budget(self):
        result = self.plan()
        self.assertEqual(result["status"], "NEXT_LOCAL_NATIVE_PROPOSED")
        self.assertEqual(result["global_reserve_calls"], 24)
        self.assertEqual(result["post_global_scout_calls"], 160)
        self.assertEqual(result["regional_budget_calls"], 136)
        self.assertEqual(result["regional_budget_calls"]
                         + result["global_reserve_calls"], 160)
        self.assertEqual(sum(x["target_scout_calls"]
                             for x in result["allocations"]), 136)
        self.assertLessEqual(max(x["target_scout_calls"]
                                 for x in result["allocations"]), 55)
        self.assertEqual(result["global_reserve_remaining"], 24)
        self.assertEqual(result["next_request"]["iterations"], self.SCOUT)
        self.assertFalse(result["global_optimum_proven"])
        self.assertEqual(result["statistical_claim"],
                         "ALLOCATION_HEURISTICS_ONLY_NOT_95_PERCENT")

    def test_edge_improvement_expands_and_recenters_region(self):
        center = (800, 800, 800, 707)
        regions = [{"region_id": "r0", "center": center,
                    "radius_fraction": .05}]
        observations = [
            self.row("r0", center, 190000, 500, 0),
            self.row("r0", (850, 750, 800, 707), 190100, 500, 1),
            self.row("r0", (940, 760, 800, 607), 191000, 400, 2),
            self.row("r0", (950, 750, 800, 607), 191500, 350, 3),
        ]
        result = self.plan(observations, regions)
        region = result["allocations"][0]
        self.assertGreater(region["radius_fraction"], .05)
        self.assertEqual(region["center"], [950, 750, 800, 607])
        self.assertGreater(region["edge_ratio"], .8)

    def test_improving_edge_region_receives_more_native_budget(self):
        centers = (
            (800, 800, 800, 707),
            (900, 700, 800, 707),
            (700, 900, 800, 707),
            (800, 700, 900, 707),
        )
        regions = [
            {"region_id": "r%d" % i, "center": center,
             "radius_fraction": .05}
            for i, center in enumerate(centers)
        ]
        observations = [
            self.row("r0", centers[0], 190000, 500, 0),
            self.row("r0", (850, 750, 800, 707), 190100, 500, 1),
            self.row("r0", (940, 760, 800, 607), 191000, 400, 2),
            self.row("r0", (950, 750, 800, 607), 191500, 350, 3),
        ]
        seq = 4
        for index in range(1, 4):
            center = centers[index]
            for step in range(6):
                vector = (center[0] + step * 2, center[1] - step * 2,
                          center[2], center[3])
                observations.append(self.row(
                    "r%d" % index, vector, 180000 - step * 10, 100, seq
                ))
                seq += 1
        result = self.plan(observations, regions)
        allocations = {row["region_id"]: row["target_scout_calls"]
                       for row in result["allocations"]}
        self.assertGreater(allocations["r0"], allocations["r1"])
        self.assertGreater(allocations["r0"], allocations["r2"])
        self.assertGreater(allocations["r0"], allocations["r3"])

    def test_stable_confirmed_interior_leader_shrinks_radius(self):
        center = (800, 800, 800, 707)
        regions = [{"region_id": "r0", "center": center,
                    "radius_fraction": .08}]
        observations = [
            self.row("r0", center, 190000, 400, 0),
            self.row("r0", (810, 790, 800, 707), 189500, 400, 1),
            self.row("r0", center, 190500, 200, 2, self.CONFIRM),
            self.row("r0", (820, 780, 800, 707), 190100, 200, 3,
                     self.CONFIRM),
        ]
        result = self.plan(observations, regions)
        region = result["allocations"][0]
        self.assertTrue(region["rank_stable_heuristic"])
        self.assertLess(region["radius_fraction"], .08)

    def test_low_noise_stagnation_shrinks_radius(self):
        center = (800, 800, 800, 707)
        regions = [{"region_id": "r0", "center": center,
                    "radius_fraction": .08}]
        observations = [
            self.row("r0", center, 190000, 100, 0),
            self.row("r0", (810, 790, 800, 707), 189900, 100, 1),
            self.row("r0", (820, 780, 800, 707), 189800, 100, 2),
            self.row("r0", (830, 770, 800, 707), 189700, 100, 3),
            self.row("r0", (840, 760, 800, 707), 189600, 100, 4),
            self.row("r0", (850, 750, 800, 707), 189500, 100, 5),
        ]
        result = self.plan(observations, regions)
        self.assertLess(result["allocations"][0]["radius_fraction"], .08)
        self.assertGreater(result["allocations"][0]["stagnation"], 2)

    def test_exhausted_local_pool_yields_global_reserve_not_false_completion(self):
        center = (800, 800, 800, 707)
        regions = [{"region_id": "r0", "center": center,
                    "radius_fraction": .25, "remaining_candidates": 0}]
        result = self.plan(regions=regions)
        self.assertEqual(result["status"], "GLOBAL_RESERVE_ONLY")
        self.assertIsNone(result["next_request"])
        self.assertGreater(result["global_reserve_remaining"], 0)
        self.assertFalse(result["global_optimum_proven"])

    def test_duplicate_native_identity_and_unknown_region_block(self):
        center = (800, 800, 800, 707)
        regions = [{"region_id": "r0", "center": center}]
        row = self.row("r0", center, 190000, 200, 0)
        with self.assertRaisesRegex(adaptive.PolicyBlocked,
                                    "DUPLICATE_NATIVE_VECTOR_ITERATION_IDENTITY"):
            self.plan([row, dict(row, sequence=1)], regions)
        with self.assertRaisesRegex(adaptive.PolicyBlocked,
                                    "OBSERVATION_UNKNOWN_REGION"):
            self.plan([dict(row, region_id="unknown")], regions)

    def test_spent_region_calls_cannot_be_reallocated(self):
        active = [{"region_id": name} for name in ("r0", "r1", "r2")]
        weights = {"r0": 0.05, "r1": 0.9, "r2": 0.05}
        spent = {"r0": 8, "r1": 0, "r2": 0}
        allocation = adaptive._allocate(
            active, weights, 20, 0.40, already=spent)
        self.assertEqual(sum(allocation.values()), 20)
        self.assertGreaterEqual(allocation["r0"], 8)
        self.assertLessEqual(max(allocation.values()), 8)

    def test_weaker_recent_region_does_not_discard_prior_leader(self):
        center = (800, 800, 800, 707)
        region = {"region_id": "r0", "center": center,
                  "radius_fraction": .08}
        rows = [
            self.row("r0", center, 191000, 100, 0),
            self.row("r0", (810, 790, 800, 707), 190500, 100, 1),
            self.row("r0", (820, 780, 800, 707), 189000, 100, 2),
            self.row("r0", (830, 770, 800, 707), 189100, 100, 3),
        ]
        metric = adaptive._metrics(region, rows, self.B, 100.0)
        self.assertEqual(metric["center"], center)

    def test_equal_iteration_comparison_contract_and_receipts(self):
        contract = adaptive.comparison_budget_contract(
            initial_global_calls=160, scout_iterations=35,
            post_global_scout_calls=160, confirmation_iterations=320,
            confirmation_calls=8, wall_clock_budget_seconds=180,
        )
        self.assertEqual(contract["adaptive_regional_scout_calls"], 136)
        self.assertEqual(contract["adaptive_global_reserve_calls"], 24)
        self.assertEqual(
            contract["requested_iterations_per_method"],
            (160 + 160) * 35 + 8 * 320,
        )
        receipts = {}
        for method in contract["methods"]:
            receipts[method] = {
                "binary_sha256": "a" * 64,
                "profile_sha256": "b" * 64,
                "combat_sha256": "c" * 64,
                "initial_global_sample_sha256": "d" * 64,
                "bounds_sha256": "e" * 64,
                "requested_iterations": contract["requested_iterations_per_method"],
                "wall_clock_seconds": 90.0,
                "native_requests": contract["native_requests_per_method"],
                "new_native_calls": 164,
                "cache_reuses": 164,
                "global_optimum_proven": False,
            }
        valid = adaptive.validate_comparison_receipts(contract, receipts)
        self.assertEqual(valid["status"], "COMPARISON_RESOURCE_RECEIPTS_VALID")
        self.assertFalse(valid["dps_quality_assessed"])
        receipts["sobol"]["requested_iterations"] -= 1
        with self.assertRaisesRegex(adaptive.PolicyBlocked,
                                    "COMPARISON_ITERATIONS_NOT_EQUAL"):
            adaptive.validate_comparison_receipts(contract, receipts)

        receipts["sobol"]["requested_iterations"] = contract["requested_iterations_per_method"]
        receipts["sobol"]["native_requests"] -= 1
        with self.assertRaisesRegex(adaptive.PolicyBlocked,
                                    "COMPARISON_NATIVE_REQUESTS_NOT_EQUAL"):
            adaptive.validate_comparison_receipts(contract, receipts)

    def test_comparison_rejects_binary_or_profile_drift_and_wall_cap(self):
        contract = adaptive.comparison_budget_contract(
            initial_global_calls=4, scout_iterations=35,
            post_global_scout_calls=8, confirmation_iterations=320,
            confirmation_calls=2, wall_clock_budget_seconds=30,
        )
        receipts = {}
        for method in contract["methods"]:
            receipts[method] = {
                "binary_sha256": "a" * 64,
                "profile_sha256": "b" * 64,
                "combat_sha256": "c" * 64,
                "initial_global_sample_sha256": "d" * 64,
                "bounds_sha256": "e" * 64,
                "requested_iterations": contract["requested_iterations_per_method"],
                "wall_clock_seconds": 20.0,
                "native_requests": contract["native_requests_per_method"],
                "new_native_calls": 10,
                "cache_reuses": 4,
                "global_optimum_proven": False,
            }
        receipts["mads_like"]["binary_sha256"] = "f" * 64
        with self.assertRaisesRegex(adaptive.PolicyBlocked,
                                    "COMPARISON_SHARED_IDENTITY_DRIFT"):
            adaptive.validate_comparison_receipts(contract, receipts)
        receipts["mads_like"]["binary_sha256"] = "a" * 64
        receipts["mads_like"]["wall_clock_seconds"] = 31.0
        with self.assertRaisesRegex(adaptive.PolicyBlocked,
                                    "COMPARISON_WALL_CLOCK_CAP"):
            adaptive.validate_comparison_receipts(contract, receipts)


if __name__ == "__main__":
    unittest.main()
