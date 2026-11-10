"""v305 32+32+4 equal-cost pilot deterministic offline proof (no Native)."""
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"integration_probes")]

import v290_multiscale_adaptive_policy as base
import v304_v303_durable_adapter as v304
import v305_grid_pairwise_adaptive_hybrid as v305
import p2_real_hybrid_v305_once as benchmark
import p2_real_equal_v304_once as previous


class V305BenchOffline(unittest.TestCase):
    def test_contract_4520_and_history_steps(self):
        history=[]
        order=v304._global_order(
            previous.B,tuple(previous.LOWER),
            tuple(previous.UPPER),previous.GLOBAL)
        for i in range(previous.GLOBAL+previous.POST+previous.CONFIRM):
            result=benchmark.plan(history)
            req=result["next_request"]
            self.assertIsNotNone(req)
            if i<previous.GLOBAL:
                self.assertEqual(req["hybrid_method"],v305.GLOBAL)
                self.assertEqual(tuple(base.legacy.key(req["target"])),order[i])
            elif i<previous.GLOBAL+previous.POST:
                self.assertEqual(req["phase"],"scout")
                self.assertIn(req["hybrid_method"],
                              (v305.GRID,v305.PAIR,v305.FALLBACK,v305.RESERVE))
            else:
                self.assertEqual(req["hybrid_method"],v305.CONFIRM)
                self.assertEqual(req["iterations"],previous.CONFIRM_ITERS)
            vec=tuple(base.legacy.key(req["target"]))
            fake={
                "target":req["target"],"phase":req["phase"],
                "iterations":req["iterations"],
                "dps_mean":191000.0+(i%11)*13.0,
                "dps_sem":250.0,
                "adaptive_stage":req["adaptive_stage"],
                "region_id":req["region_id"],
                "region_center":req["region_center"],
                "region_radius_fraction":req["region_radius_fraction"],
                "hybrid_method":req["hybrid_method"],
            }
            history.append(fake)
        methods=[r["hybrid_method"] for r in history]
        self.assertEqual(methods.count(v305.GLOBAL),32)
        self.assertEqual(methods.count(v305.RESERVE),5)
        self.assertEqual(methods.count(v305.CONFIRM),4)
        self.assertEqual(sum(methods.count(k)
                       for k in (v305.GRID,v305.PAIR,v305.FALLBACK)),27)
        self.assertGreaterEqual(methods.count(v305.GRID),1)
        self.assertGreaterEqual(methods.count(v305.PAIR),1)
        self.assertIsNone(benchmark.plan(history)["next_request"])
        self.assertEqual(previous.equal_resource_contract()[
                         "requested_iterations_per_arm"],4520)

    def test_negative_profile_identity_rejected_before_native(self):
        # The actual source requires the exact previous receipt. This test
        # confirms that an empty/untrusted document cannot pass as evidence.
        with self.assertRaisesRegex(RuntimeError,
                                    "HISTORICAL_127_EXACT_PROFILE_BUDGET_PROOF_DRIFT"):
            benchmark.validate_old({},benchmark.PROFILE_SHA)

    def test_pairwise_mode_requires_valid_stage_and_region_metadata(self):
        history=[]
        for i in range(4):
            p=benchmark.plan(history)
            req=p["next_request"]
            fake=dict(target=req["target"],phase=req["phase"],
                      iterations=req["iterations"],
                      dps_mean=185000.0,dps_sem=350.0,
                      adaptive_stage=req["adaptive_stage"],
                      region_id=req["region_id"],
                      region_center=req["region_center"],
                      region_radius_fraction=req["region_radius_fraction"],
                      hybrid_method=req["hybrid_method"])
            history.append(fake)
        history[0]["hybrid_method"]=v305.PAIR
        with self.assertRaisesRegex(
                v305.HybridBlocked,"V305_NONREGION_METHOD_STAGE_DRIFT"):
            benchmark.plan(history)


if __name__=="__main__":
    unittest.main()
