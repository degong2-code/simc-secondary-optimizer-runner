"""v307 dense nested survey: exact lattice, honest coverage and v291 seal.

No actual Native and no season source requests. v291 tests use original
mocked v065 one-case acceptance fixture and exact SHA-style session journaling.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest
from collections import Counter
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]

import v290_multiscale_adaptive_policy as v290
import v302_weak_multiregion_zoom as v302
import v307_dense_nested_coverage_grid as grid
import v291_durable_multiscale_native_runner as runner
import test_p3_hx_durable_longrun_offline as fixture_module

F=fixture_module.F
B=3107
LOWER=(0,165,0,0)
UPPER=(1864,)*4


def plan(rows,cap=520,level=21):
    return grid.next_plan(
        rows,total=B,lower=LOWER,upper=UPPER,
        max_native_calls=cap,scout_iterations=35,
        confirmation_iterations=320,max_level=level)


class V307DenseGrid(unittest.TestCase):
    def test_exact_nested_residual_6_11_21_41_with_original_source(self):
        collections={}
        expected={6:433,11:2778,21:19380,41:146221}
        for level in (6,11,21,41):
            group=set(grid.lattice(B,LOWER,UPPER,level))
            self.assertEqual(len(group),expected[level])
            self.assertEqual(len(group),len(grid.lattice(
                B,LOWER,UPPER,level)))
            self.assertTrue(all(v290.legacy.eligible(
                v,B,LOWER,UPPER) for v in group))
            self.assertEqual(len(grid.ordered_new_level(
                B,LOWER,UPPER,level)),len(group) -
                    (len(collections[max(collections)]) if collections else 0))
            collections[level]=group
        for a,b in ((6,11),(11,21),(21,41)):
            self.assertTrue(collections[a].issubset(collections[b]))
        self.assertEqual(grid.ordered_new_level(
            B,LOWER,UPPER,11)[0] in collections[6],False)
        self.assertGreater(len({
            grid._cell(v,LOWER,UPPER) for v in
            grid.ordered_new_level(B,LOWER,UPPER,6)[:100]}),20)

    def test_81_is_optional_lazily_exact_and_not_a_fabricated_coverage(self):
        # Tiny total protects focused CI from a million-vector 81 probe.
        b,low,high=50,(0,0,0,0),(40,40,40,40)
        small={level:set(grid.lattice(b,low,high,level))
               for level in (41,81)}
        self.assertTrue(small[41].issubset(small[81]))
        self.assertGreater(len(small[81]),len(small[41]))
        self.assertTrue(all(sum(v)==b and max(v)<=40 for v in small[81]))
        report=grid.coverage([],total=b,lower=low,upper=high,max_level=81)
        self.assertFalse(report["levels"]["81"]["complete_at_this_resolution"])
        self.assertEqual(report["levels"]["81"]["observed_targets"],0)

    def test_coverage_first_520_budget_realistic_partial_11_and_region_zoom(self):
        history=[]
        for i in range(520):
            proposed=plan(history)
            req=proposed["next_request"]
            self.assertIsNotNone(req)
            v=v290.legacy.key(req["target"])
            self.assertTrue(v290.legacy.eligible(v,B,LOWER,UPPER))
            self.assertEqual(sum(v),B)
            if i<433:
                self.assertEqual(req["grid_stage"],grid.SURVEY)
                self.assertEqual(req["grid_level"],6)
                self.assertIsNone(req["grid_origin"])
            if req["phase"]=="scout":
                self.assertNotIn(v,{
                    v290.legacy.key(row["target"]) for row in history
                    if row["phase"]=="scout"})
            row=dict(req,dps_mean=180000.+(i%17)*30.,
                     dps_sem=700.,case_key=str(i))
            history.append(row)
        self.assertIsNone(plan(history)["next_request"])
        budget=grid.budget(520)
        self.assertEqual(sum(row["phase"]=="precision" for row in history),
                         budget["confirmation_calls"])
        stages=Counter(r["grid_stage"] for r in history)
        self.assertGreater(stages[grid.LOCAL],0)
        self.assertGreater(stages[grid.SURVEY],433)
        coverage=grid.coverage(history,total=B,lower=LOWER,
                               upper=UPPER,max_level=21)
        self.assertTrue(coverage["levels"]["6"][
            "complete_at_this_resolution"])
        self.assertFalse(coverage["levels"]["11"][
            "complete_at_this_resolution"])
        self.assertEqual(coverage["levels"]["6"]["unobserved_targets"],0)
        self.assertIsNone(coverage["highest_complete_level"] if
            coverage["highest_complete_level"] is None else None)

    def test_reject_unsealed_or_forged_observation(self):
        rows=[]
        req=plan(rows,cap=24)["next_request"]
        rows.append(dict(req,dps_mean=185000.,dps_sem=400.))
        self.assertIsNotNone(plan(rows,cap=24)["next_request"])
        forged=dict(rows[0],grid_level=81)
        with self.assertRaisesRegex(grid.GridBlocked,
                                    "V307_SURVEY_METADATA_DRIFT"):
            plan([forged],cap=24)
        with self.assertRaisesRegex(grid.GridBlocked,
                                    "V307_HISTORY_GRID_METADATA_OR_PHASE_DRIFT"):
            plan([dict(rows[0],phase="precision")],cap=24)
        with self.assertRaisesRegex(grid.GridBlocked,
                                    "V307_GRID_LEVEL_6_11_21_41_81"):
            plan([],cap=24,level=22)

    def test_v291_exact_cache_only_pending_cancel_resume_and_seal_isolation(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx,binary,out=fixture_module.V291LongRun().fixture(folder,cap=24)
            def run(**kw):
                return runner.run(
                    ctx,F,binary,out,max_native_calls=24,
                    dense_nested_grid_max_level=11,**kw)
            with mock.patch.object(runner.engine,"execute_one",
                                   side_effect=fixture_module.fake_native), \
                 mock.patch.object(runner.oil,"ingest_native",
                                   side_effect=fixture_module.fake_ingest):
                partial=run(max_new_native_this_invocation=12)
                self.assertEqual(partial["completed_cases"],12)
                self.assertEqual(partial["policy"],grid.SCHEMA)
                seal=runner.read_json(out/"V291_SESSION.json")
                self.assertEqual(seal["experimental_dense_nested_grid"][
                    "max_level"],11)
                pause=run(cache_only=True)
                self.assertEqual(pause["status"],"PAUSED_CACHE_ONLY")
                self.assertEqual(pause["new_native_this_invocation"],0)
                pending=runner.read_json(out/"V291_PENDING.json")
                self.assertEqual(pending["grid_stage"],grid.SURVEY)
                self.assertEqual(run(cache_only=True)[
                    "new_native_this_invocation"],0)
                self.assertEqual(runner.read_json(out/"V291_PENDING.json"),
                                 pending)
                with self.assertRaisesRegex(
                        runner.LongRunBlocked,"SEALED_SESSION_IDENTITY_DRIFT"):
                    runner.run(ctx,F,binary,out,max_native_calls=24,
                               dense_nested_grid_max_level=21,
                               cache_only=True)
                with self.assertRaisesRegex(
                        runner.LongRunBlocked,"V307_EXCLUSIVE_DENSE_GRID_OPT_IN"):
                    runner.run(ctx,F,binary,out,max_native_calls=24,
                               dense_nested_grid_max_level=11,
                               seed_retained_coarse_escape_regions=True,
                               cache_only=True)
                forged=dict(pending,grid_cursor=pending["grid_cursor"]+2)
                runner.atomic(out/"V291_PENDING.json",forged)
                with self.assertRaisesRegex(runner.LongRunBlocked,
                                           "V304_PENDING_PLAN_DRIFT"):
                    run(cache_only=True)
                runner.atomic(out/"V291_PENDING.json",pending)
                finish=run()
                self.assertEqual(finish["status"],"BUDGET_EXHAUSTED")
                self.assertEqual(finish["completed_cases"],24)
                self.assertEqual(finish["native_attempts_cumulative"],24)
                self.assertEqual(run()["new_native_this_invocation"],0)
                result=runner.read_json(out/"V291_RESULT.json")
                self.assertEqual(result["dense_grid_coverage"]["levels"]["6"][
                    "observed_targets"],22)
                self.assertFalse(result["dense_grid_coverage"]["levels"]["6"][
                    "complete_at_this_resolution"])


if __name__=="__main__":
    unittest.main()
