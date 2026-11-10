"""Pure 21-level 25/50/100 schedule and v291 original-raw prior seam.

Synthetic DPS and fake Native are strictly not SimC evidence. Real origin
2800 ZIP is checked by gated Actions before any NEW SimC starts.
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
import v291_durable_multiscale_native_runner as durable
import v309_prior_anchored_level21_progressive as progressive
import test_p3_hx_durable_longrun_offline as base_test

B=3400
LOWER=(0,0,0,165)
UPPER=(2040,)*4
F=base_test.F


class V309Milestones(unittest.TestCase):
    def test_new_only_21_25_50_100_exact_counts(self):
        geo=progressive.geometry(B,LOWER,UPPER)
        self.assertEqual(geo["size_old"],2784)
        self.assertEqual(geo["size_fine"],19812)
        self.assertEqual(geo["new_only_count"],17028)
        self.assertEqual(geo["new_counts"],(2169,7122,17028))
        self.assertEqual(geo["milestone_calls"],(2185,7154,17076))
        self.assertTrue(set(geo["old"]).isdisjoint(set(geo["new"])))
        checked=[]
        # Full pure schedule: explicit 25/50/100 points, no random DPS.
        for index in range(geo["total_calls"]):
            plan=progressive.next_plan(
                checked,total=B,lower=LOWER,upper=UPPER,
                max_native_calls=geo["total_calls"],
                scout_iterations=35,confirmation_iterations=320)
            req=plan["next_request"]
            self.assertIsNotNone(req)
            vector=v290.legacy.key(req["target"])
            self.assertTrue(v290.legacy.eligible(vector,B,LOWER,UPPER))
            if req["new_level_stage"]==progressive.SURVEY:
                self.assertEqual(vector,geo["new"][req["new_level_cursor"]])
            fake=dict(req,index=index,
                      dps_mean=180000.-(index%17)*20,
                      dps_sem=630.)
            checked.append(fake)
            if index+1 in geo["milestone_calls"]:
                milestone=[25,50,100][geo["milestone_calls"].index(index+1)]
                cov=progressive.coverage(
                    checked,total=B,lower=LOWER,upper=UPPER,
                    prior_count=geo["size_old"])
                self.assertEqual(cov["combined_observed_geometric_coverage"],
                                 geo["milestone_targets"][[25,50,100].index(
                                     milestone)])
                self.assertEqual(cov["new_confirmation_vectors"],
                                 [25,50,100].index(milestone)*16+16)
        self.assertIsNone(progressive.next_plan(
            checked,total=B,lower=LOWER,upper=UPPER,
            max_native_calls=geo["total_calls"],
            scout_iterations=35,confirmation_iterations=320)["next_request"])
        audit=progressive.audit_committed_history(
            checked,total=B,lower=LOWER,upper=UPPER,
            max_native_calls=geo["total_calls"],
            scout_iterations=35,confirmation_iterations=320)
        self.assertEqual(audit["observed_new_unique"],17028)
        self.assertEqual(audit["confirmed_new_unique"],48)

    def test_journal_cursor_forgery_fails_before_new_native(self):
        with tempfile.TemporaryDirectory() as temp:
            # v291 uses a Fury fake to verify plumbing only.
            context,binary,out=base_test.V291LongRun().fixture(temp,cap=100000)
            ident=context["identity"]
            normal=context["bundle"]["prepared"]["scenario"]
            budget,lo,hi=durable.constraints.bounds(
                normal,durable.adaptive.feasible_budget(context,F))
            geo=progressive.geometry(budget,tuple(lo),tuple(hi))
            prior={
                "schema":"v309_external_original11_historical_anchor_v1",
                "raw_archive_sha256":"a"*64,
                "original_compact_journal_sha256":"b"*64,
                "source_profile_sha256":ident["source_profile_sha256"],
                "original_scenario_digest":"c"*64,
                "binary_sha256":ident["binary_sha256"],
                "revision":ident["revision"],"season_build":"TEST_ONLY",
                "B":budget,"lower":tuple(lo),"upper":tuple(hi),
                "scout_iterations":ident["scout_iterations"],
                "confirm_iterations":ident["confirm_iterations"],
                "confirmed_baseline":(),
                "prior_level11_count":geo["size_old"],
                "verified_origin_zip_member_shas":True,
                "old_original_v291_cache_only_authenticated_in_origin_run":True,
                "cross_runtime_cache_import_authenticated":False,
            }
            files=("fake_compact.zip","fake_raw.zip","a"*64)
            def run(**opts):
                return durable.run(context,F,binary,out,
                    max_native_calls=geo["total_calls"],
                    v309_prior_compact_artifact_zip=files[0],
                    v309_prior_raw_checkpoint_zip=files[1],
                    v309_prior_raw_checkpoint_sha256=files[2],**opts)
            with mock.patch.object(progressive,"load_original_prior",
                                   return_value=prior),\
                 mock.patch.object(durable.engine,"execute_one",
                                   side_effect=base_test.fake_native),\
                 mock.patch.object(durable.oil,"ingest_native",
                                   side_effect=base_test.fake_ingest):
                first=run(max_new_native_this_invocation=8)
                self.assertEqual(first["completed_cases"],8)
                self.assertEqual(first["policy"],progressive.SCHEMA)
                self.assertEqual(first["new_native_this_invocation"],8)
                self.assertEqual(first["progressive_level21_coverage"][
                    "combined_observed_geometric_coverage"],
                    geo["size_old"]+8)
                seal=durable.read_json(out/"V291_SESSION.json")
                self.assertEqual(seal["experimental_prior_anchored_21"][
                    "origin"]["raw_archive_sha256"],"a"*64)
                resume=run(cache_only=True)
                self.assertEqual(resume["new_native_this_invocation"],0)
                pending=durable.read_json(out/"V291_PENDING.json")
                distorted=dict(pending,
                               new_level_cursor=pending["new_level_cursor"]+5)
                durable.atomic(out/"V291_PENDING.json",distorted)
                with self.assertRaisesRegex(
                        durable.LongRunBlocked,"V304_PENDING_PLAN_DRIFT"):
                    run(cache_only=True)
                durable.atomic(out/"V291_PENDING.json",pending)
                journal=out/"V291_JOURNAL.jsonl"
                original=journal.read_bytes()
                import json
                rows=[json.loads(l) for l in original.splitlines()]
                rows[0]["new_level_cursor"]+=2
                journal.write_text("".join(json.dumps(
                    row,sort_keys=True,separators=(",",":"))+"\n"
                    for row in rows))
                with self.assertRaisesRegex(progressive.PilotBlocked,
                                            "V309_RECORDED_SCHEDULE_METADATA_DRIFT"):
                    run(cache_only=True)
                journal.write_bytes(original)
                again=run(max_new_native_this_invocation=4)
                self.assertEqual(again["completed_cases"],12)
                with self.assertRaisesRegex(
                        durable.LongRunBlocked,"V309_EXCLUSIVE_VERIFIED_PRIOR_PROOF_REQUIRED"):
                    durable.run(context,F,binary,out,
                        max_native_calls=geo["total_calls"],
                        v309_prior_compact_artifact_zip="fake",
                        v309_prior_raw_checkpoint_zip="fake",
                        v309_prior_raw_checkpoint_sha256="a"*64,
                        dense_nested_grid_max_level=21,
                        cache_only=True)


if __name__=="__main__":
    unittest.main()
