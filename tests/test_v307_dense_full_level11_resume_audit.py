"""v307 correctness gates discovered during full level-11 audit.

No SimC Native: exact fake-v065 receipts are used only to exercise session
seals, journal audit and cache-only restart behavior.
"""
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]

import v307_dense_nested_coverage_grid as grid
import v291_durable_multiscale_native_runner as runner
import test_p3_hx_durable_longrun_offline as fixtures

F=fixtures.F


class DenseNoSkipRegression(unittest.TestCase):
    def test_full_level_11_if_exactly_enough_budget_to_measure_all(self):
        B,lo,hi=60,(0,0,0,0),(50,50,50,50)
        size=len(grid.lattice(B,lo,hi,11))
        self.assertEqual(size,439)
        calls=453
        self.assertEqual(grid.budget(calls)["scout"],size)
        observations=[]
        for i in range(calls):
            req=grid.next_plan(
                observations,total=B,lower=lo,upper=hi,
                max_native_calls=calls,scout_iterations=35,
                confirmation_iterations=320,max_level=11,
                complete_grid_first=True)["next_request"]
            self.assertIsNotNone(req)
            self.assertNotEqual(req["grid_stage"],grid.LOCAL)
            row=dict(req,dps_mean=180000.+(i%9)*40,
                     dps_sem=600.,case_key=str(i))
            observations.append(row)
        c=grid.coverage(observations,total=B,lower=lo,
                        upper=hi,max_level=11)
        self.assertTrue(c["levels"]["6"]["complete_at_this_resolution"])
        self.assertTrue(c["levels"]["11"]["complete_at_this_resolution"])
        self.assertEqual(c["levels"]["11"]["unobserved_targets"],0)
        self.assertEqual(sum(x["phase"]=="precision" for x in observations),
                         calls-size)
        self.assertEqual(grid.audit_recorded_history(
            observations,total=B,lower=lo,upper=hi,
            max_level=11)["unique_scouts"],size)
        self.assertIsNone(grid.next_plan(
            observations,total=B,lower=lo,upper=hi,
            max_native_calls=calls,scout_iterations=35,
            confirmation_iterations=320,max_level=11,
            complete_grid_first=True)["next_request"])

    def test_survey_cursor_jump_is_detected_on_authenticated_journal(self):
        with tempfile.TemporaryDirectory() as folder:
            context,binary,out=fixtures.V291LongRun().fixture(folder,cap=24)
            def run(**kw):
                return runner.run(context,F,binary,out,
                    max_native_calls=24,
                    dense_nested_grid_max_level=11,
                    dense_nested_grid_full_scan=True,**kw)
            with mock.patch.object(runner.engine,"execute_one",
                                   side_effect=fixtures.fake_native), \
                 mock.patch.object(runner.oil,"ingest_native",
                                   side_effect=fixtures.fake_ingest):
                first=run(max_new_native_this_invocation=12)
                self.assertEqual(first["completed_cases"],12)
                seal=runner.read_json(out/"V291_SESSION.json")
                self.assertTrue(seal["experimental_dense_nested_grid"][
                    "complete_grid_first"])
                journal=out/"V291_JOURNAL.jsonl"
                original=journal.read_bytes()
                lines=[json.loads(z) for z in original.splitlines()]
                lines[0]["grid_cursor"]+=2
                journal.write_text("".join(json.dumps(
                    r,sort_keys=True,separators=(",",":"))+"\n"
                    for r in lines))
                with self.assertRaisesRegex(grid.GridBlocked,
                                           "V307_RECORDED_SURVEY_SEQUENCE_DRIFT"):
                    run(cache_only=True)
                journal.write_bytes(original)
                replay=run(cache_only=True)
                self.assertEqual(replay["new_native_this_invocation"],0)
                done=run()
                self.assertEqual(done["completed_cases"],24)
                self.assertEqual(done["status"],"BUDGET_EXHAUSTED")
                self.assertEqual(run()["new_native_this_invocation"],0)

    def test_forged_early_level_and_wrong_local_anchor_refused(self):
        B,lo,hi=60,(0,0,0,0),(50,50,50,50)
        req=grid.next_plan([],total=B,lower=lo,upper=hi,
                           max_native_calls=24,scout_iterations=35,
                           confirmation_iterations=320,max_level=11)[
                           "next_request"]
        row=dict(req,dps_mean=180000.,dps_sem=500.)
        with self.assertRaisesRegex(grid.GridBlocked,
                                    "V307_RECORDED_SURVEY_SEQUENCE_DRIFT"):
            grid.audit_recorded_history(
                [dict(row,grid_level=11)],
                total=B,lower=lo,upper=hi,max_level=11)
        local=dict(row,grid_stage=grid.LOCAL,grid_level=6,
                   grid_cursor=None,grid_origin=list(
                       (20,20,20,0)))
        with self.assertRaisesRegex(grid.GridBlocked,
                                    "V307_RECORDED_LOCAL_GEOMETRY_OR_PROOF_DRIFT"):
            grid.audit_recorded_history(
                [local],total=B,lower=lo,upper=hi,max_level=11)


if __name__=="__main__":
    unittest.main()
