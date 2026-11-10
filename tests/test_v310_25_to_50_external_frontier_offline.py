"""v310 external 11+25 source-attested FRONTIER -> NEW-only 50 schedule.

Zero real SimC. Fake v065 Native is for checkpoint/seal plumbing only.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v290_multiscale_adaptive_policy as v290
import v291_durable_multiscale_native_runner as runner
import v310_external_frontier_50_only as v310
import test_p3_hx_durable_longrun_offline as fixture

B,LOWER,UPPER=3400,(0,0,0,165),(2040,2040,2040,2040)


class V310FrontierOffline(unittest.TestCase):
    def test_full_new_only_50_vector_contract_and_95_nonclaim(self):
        geo=v310.geometry(B,LOWER,UPPER)
        self.assertEqual(geo["old_11"],2784)
        self.assertEqual(geo["original25_new"],2169)
        self.assertEqual(geo["new_50_count"],4953)
        self.assertEqual(geo["existing_combined"],4953)
        self.assertEqual(geo["combined_50"],9906)
        self.assertEqual(geo["level21_total"],19812)
        self.assertEqual(geo["native_cap"],4969)
        old=v310.previous.geometry(B,LOWER,UPPER)
        self.assertEqual(geo["new_targets"],old["new"][2169:7122])
        self.assertTrue(set(geo["new_targets"]).isdisjoint(
            set(old["old"])|set(old["new"][:2169])))
        rows=[]
        for idx in range(geo["native_cap"]):
            req=v310.next_plan(
                rows,total=B,lower=LOWER,upper=UPPER,
                max_native_calls=geo["native_cap"],
                scout_iterations=35,confirmation_iterations=320)[
                    "next_request"]
            self.assertIsNotNone(req)
            target=v290.legacy.key(req["target"])
            self.assertTrue(v290.legacy.eligible(target,B,LOWER,UPPER))
            if idx<geo["new_50_count"]:
                self.assertEqual(target,geo["new_targets"][idx])
                self.assertEqual(req["new21_cursor"],2169+idx)
            rows.append(dict(req,index=idx,
                             dps_mean=175000+(idx%123)*18.,
                             dps_sem=700.))
        self.assertIsNone(v310.next_plan(
            rows,total=B,lower=LOWER,upper=UPPER,
            max_native_calls=geo["native_cap"],
            scout_iterations=35,confirmation_iterations=320)[
                "next_request"])
        audit=v310.audit_recorded_history(
            rows,total=B,lower=LOWER,upper=UPPER,
            max_native_calls=geo["native_cap"],
            scout_iterations=35,confirmation_iterations=320)
        self.assertEqual(audit["new_scouts_authenticated_in_current_session"],
                         4953)
        self.assertEqual(audit["new_confirms_authenticated_in_current_session"],16)
        cover=v310.coverage(rows,total=B,lower=LOWER,upper=UPPER,
                            frontier={"prior_total_scouts":4953})
        self.assertEqual(cover["combined_observed"],9906)
        self.assertEqual(cover["remaining_unmeasured"],9906)
        self.assertFalse(cover["global_optimum_proven"])
        with self.assertRaisesRegex(v310.FrontierBlocked,
                                    "V310_RECORDED_NEW21_CURSOR"):
            broken=dict(rows[15],new21_cursor=0)
            v310.audit_recorded_history(
                rows[:15]+[broken],total=B,lower=LOWER,upper=UPPER,
                max_native_calls=geo["native_cap"],
                scout_iterations=35,confirmation_iterations=320)

    def test_v291_isolated_frontier_50_fake_native_resume_and_seal(self):
        with tempfile.TemporaryDirectory() as temp:
            ctx,binary,out=fixture.V291LongRun().fixture(temp,cap=100000)
            ident=ctx["identity"]
            normalized=ctx["bundle"]["prepared"]["scenario"]
            B,lo,hi=runner.constraints.bounds(
                normalized,runner.adaptive.feasible_budget(ctx,fixture.F))
            geo=v310.geometry(B,tuple(lo),tuple(hi))
            prior={
                "schema":"v310_external_sha_attested_first50_frontier_v1",
                "old11_raw_archive_sha256":"a"*64,
                "old11_compact_sha256":"b"*64,
                "old25_raw_archive_sha256":"c"*64,
                "old25_compact_sha256":"d"*64,
                "source_profile_sha256":ident["source_profile_sha256"],
                "binary_sha256":ident["binary_sha256"],
                "revision":ident["revision"],"season_build":"TEST_ONLY",
                "B":B,"lower":tuple(lo),"upper":tuple(hi),
                "scout_iterations":ident["scout_iterations"],
                "confirm_iterations":ident["confirm_iterations"],
                "prior_total_scouts":geo["existing_combined"],
                "expected_new50_scouts":geo["new_50_count"],
                "expected_new50_native_calls":geo["native_cap"],
                "old_best_confirmed":{
                    "target":{"crit_rating":400,"haste_rating":400,
                              "mastery_rating":400,"versatility_rating":400},
                    "dps_mean":180000.,"dps_sem":200.,
                    "iterations":80},
                "previously_proven_raw_native_in_origin_sessions":True,
                "cross_session_exact_native_case_imported":False}
            def run(**opts):
                return runner.run(
                    ctx,fixture.F,binary,out,
                    max_native_calls=geo["native_cap"],
                    v310_frontier_manifest_path="test_fake_frontier.json",
                    **opts)
            with mock.patch.object(v310,"load_frontier",return_value=prior),\
                 mock.patch.object(runner.engine,"execute_one",
                                   side_effect=fixture.fake_native),\
                 mock.patch.object(runner.oil,"ingest_native",
                                   side_effect=fixture.fake_ingest):
                first=run(max_new_native_this_invocation=7)
                self.assertEqual(first["policy"],v310.SCHEMA)
                self.assertEqual(first["completed_cases"],7)
                self.assertEqual(first["frontier50_coverage"][
                    "combined_observed"],geo["existing_combined"]+7)
                self.assertEqual(run(cache_only=True)[
                    "new_native_this_invocation"],0)
                pending=runner.read_json(out/"V291_PENDING.json")
                runner.atomic(out/"V291_PENDING.json",
                              dict(pending,new21_cursor=99999))
                with self.assertRaisesRegex(runner.LongRunBlocked,
                                           "V304_PENDING_PLAN_DRIFT"):
                    run(cache_only=True)
                runner.atomic(out/"V291_PENDING.json",pending)
                second=run(max_new_native_this_invocation=4)
                self.assertEqual(second["completed_cases"],11)
                with self.assertRaisesRegex(
                        runner.LongRunBlocked,
                        "V310_EXCLUSIVE_SHA_FRONTIER_PROOF_REQUIRED"):
                    runner.run(ctx,fixture.F,binary,out,
                               max_native_calls=geo["native_cap"],
                               v310_frontier_manifest_path="fake",
                               dense_nested_grid_max_level=21,
                               cache_only=True)


if __name__=="__main__":
    unittest.main()
