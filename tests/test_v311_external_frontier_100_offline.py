"""v311 last 50% dense 21-level frontier: geometry and v291 sealed replay.

All DPS synthetic, fake Native uses existing v065 fixture. No actual SimC.
"""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v290_multiscale_adaptive_policy as v290
import v291_durable_multiscale_native_runner as native
import v311_external_frontier_100_only as v311
import test_p3_hx_durable_longrun_offline as fixture

B,LOWER,UPPER=3400,(0,0,0,165),(2040,2040,2040,2040)


class V311External100Only(unittest.TestCase):
    def test_9906_new_targets_final_level21_completion(self):
        geo=v311.geometry(B,LOWER,UPPER)
        self.assertEqual(geo["source11"],2784)
        self.assertEqual(geo["source25"],2169)
        self.assertEqual(geo["source50"],4953)
        self.assertEqual(geo["source_unique"],9906)
        self.assertEqual(geo["new_100_count"],9906)
        self.assertEqual(geo["new_total"],19812)
        self.assertEqual(geo["from_cursor"],7122)
        self.assertEqual(geo["to_cursor"],17028)
        self.assertEqual(geo["calls"],9922)
        previous=v311.geometric.geometry(B,LOWER,UPPER)
        self.assertEqual(geo["targets"],previous["new"][7122:17028])
        old=set(previous["old"])|set(previous["new"][:7122])
        self.assertTrue(old.isdisjoint(set(geo["targets"])))
        rows=[]
        for idx in range(geo["calls"]):
            plan=v311.next_plan(rows,total=B,lower=LOWER,upper=UPPER,
                    max_native_calls=geo["calls"],scout_iterations=35,
                    confirmation_iterations=320)
            req=plan["next_request"]
            self.assertIsNotNone(req)
            v=tuple(v290.legacy.key(req["target"]))
            self.assertTrue(v290.legacy.eligible(v,B,LOWER,UPPER))
            if idx<geo["new_100_count"]:
                self.assertEqual(v,geo["targets"][idx])
                self.assertEqual(req["level21_new_cursor"],7122+idx)
                self.assertNotIn(v,old)
            rows.append(dict(req,index=idx,
                     dps_mean=180000.+idx%233*4.,
                     dps_sem=600.))
        completed=v311.coverage(rows,total=B,lower=LOWER,upper=UPPER,
                    prior={"source_total_unique":9906})
        self.assertTrue(completed["complete_at_level21"])
        self.assertEqual(completed["combined_observed"],19812)
        self.assertEqual(completed["remaining_unobserved"],0)
        self.assertEqual(completed["new_precision_confirmations"],16)
        audit=v311.audit_recorded_history(rows,total=B,lower=LOWER,
                    upper=UPPER,max_native_calls=geo["calls"],
                    scout_iterations=35,confirmation_iterations=320)
        self.assertEqual(audit["newly_observed_unique"],9906)
        self.assertEqual(audit["newly_confirmed_unique"],16)
        self.assertFalse(audit["historical_native_imported_into_active_cache"])
        self.assertIsNone(v311.next_plan(
                    rows,total=B,lower=LOWER,upper=UPPER,
                    max_native_calls=geo["calls"],scout_iterations=35,
                    confirmation_iterations=320)["next_request"])

    def test_true_journal_cursor_and_sealed_pending_with_fake_native(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx,binary,out=fixture.V291LongRun().fixture(tmp,cap=100000)
            ident=ctx["identity"]
            scenario=ctx["bundle"]["prepared"]["scenario"]
            B,lo,hi=native.constraints.bounds(
                scenario,native.adaptive.feasible_budget(ctx,fixture.F))
            geo=v311.geometry(B,tuple(lo),tuple(hi))
            prior={
                "schema":"v311_external_verified_three_source_frontier_v1",
                "first11_raw_sha256":"a"*64,
                "first25_raw_sha256":"b"*64,
                "third50_raw_sha256":"c"*64,
                "first11_compact_sha256":"d"*64,
                "first25_compact_sha256":"e"*64,
                "third50_compact_sha256":"f"*64,
                "source_profile_sha256":ident["source_profile_sha256"],
                "binary_sha256":ident["binary_sha256"],
                "revision":ident["revision"],"season_build":"TEST_ONLY",
                "B":B,"lower":tuple(lo),"upper":tuple(hi),
                "scout_iterations":ident["scout_iterations"],
                "confirm_iterations":ident["confirm_iterations"],
                "source_total_unique":geo["source_unique"],
                "expected_new_100_calls":geo["calls"],
                "highest_historical_confirmed":{
                    "target":{"crit_rating":500,"haste_rating":500,
                              "mastery_rating":500,"versatility_rating":500},
                    "dps_mean":180000.,"dps_sem":250.,
                    "iterations":80},
                "previous_original_native_in_each_run_reauthenticated":True,
                "cross_run_import_as_exact_active_native_cache":False}
            def run(**kw):
                return native.run(ctx,fixture.F,binary,out,
                     max_native_calls=geo["calls"],
                     v311_three_source_manifest_path="synthetic-proof.json",
                     **kw)
            with mock.patch.object(v311,"load_three_original_sources",
                                   return_value=prior), \
                 mock.patch.object(native.engine,"execute_one",
                                   side_effect=fixture.fake_native), \
                 mock.patch.object(native.oil,"ingest_native",
                                   side_effect=fixture.fake_ingest):
                partial=run(max_new_native_this_invocation=8)
                self.assertEqual(partial["completed_cases"],8)
                self.assertEqual(partial["policy"],v311.SCHEMA)
                self.assertEqual(partial["frontier100_coverage"][
                    "combined_observed"],geo["source_unique"]+8)
                self.assertEqual(run(cache_only=True)["new_native_this_invocation"],0)
                pending=native.read_json(out/"V291_PENDING.json")
                native.atomic(out/"V291_PENDING.json",dict(
                    pending,level21_new_cursor=99999))
                with self.assertRaisesRegex(native.LongRunBlocked,
                                             "V304_PENDING_PLAN_DRIFT"):
                    run(cache_only=True)
                native.atomic(out/"V291_PENDING.json",pending)
                journal=out/"V291_JOURNAL.jsonl"
                original=journal.read_bytes()
                rows=[json.loads(l) for l in original.splitlines()]
                rows[0]["level21_new_cursor"]+=1
                journal.write_text("".join(json.dumps(
                    r,sort_keys=True,separators=(",",":"))+"\n"
                    for r in rows))
                with self.assertRaisesRegex(v311.FrontierBlocked,
                                             "V311_SCOUT_CURSOR_OR_TARGET_DRIFT"):
                    run(cache_only=True)
                journal.write_bytes(original)
                resumed=run(max_new_native_this_invocation=7)
                self.assertEqual(resumed["completed_cases"],15)
                with self.assertRaisesRegex(
                    native.LongRunBlocked,"V311_EXCLUSIVE_THREE_SOURCE_FRONTIER_REQUIRED"):
                    native.run(ctx,fixture.F,binary,out,
                        max_native_calls=geo["calls"],cache_only=True,
                        v311_three_source_manifest_path="synthetic-proof.json",
                        dense_nested_grid_max_level=21)


if __name__=="__main__":
    unittest.main()
