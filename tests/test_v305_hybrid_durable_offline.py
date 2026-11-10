"""v305 hybrid planning / v291 durable connection. Fake Native only."""
from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"runner"),str(ROOT/"tests")]

import v290_multiscale_adaptive_policy as v290
import v304_v303_durable_adapter as v304
import v305_grid_pairwise_adaptive_hybrid as v305
import v291_durable_multiscale_native_runner as runner
import test_p3_hx_durable_longrun_offline as fixture_module
F=fixture_module.F


class V305Hybrid(unittest.TestCase):
    def fixture(self, folder, cap=24):
        return fixture_module.V291LongRun().fixture(folder,cap=cap)

    def exec_one(self, ctx, binary, out, **kw):
        return runner.run(ctx,F,binary,out,max_native_calls=24,
                          hybrid_region_grid_neighbors=True,
                          adaptive_initial_global_calls=8,
                          adaptive_confirmation_calls=3,**kw)

    def patches(self):
        return (
            mock.patch.object(runner.engine,"execute_one",
                              side_effect=fixture_module.fake_native),
            mock.patch.object(runner.oil,"ingest_native",
                              side_effect=fixture_module.fake_ingest),
        )

    def test_hybrid_real_v291_interface_complete_and_distinct(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx,binary,out=self.fixture(folder)
            with self.patches()[0],self.patches()[1]:
                first=self.exec_one(ctx,binary,out,
                                    max_new_native_this_invocation=13)
                self.assertEqual(first["completed_cases"],13)
                self.assertEqual(first["policy"],v305.SCHEMA)
                replay=self.exec_one(ctx,binary,out,
                                     max_new_native_this_invocation=0,
                                     cache_only=True)
                self.assertEqual(replay["completed_cases"],13)
                self.assertEqual(replay["new_native_this_invocation"],0)
                done=self.exec_one(ctx,binary,out)
                self.assertEqual(done["status"],"BUDGET_EXHAUSTED")
                self.assertEqual(done["completed_cases"],24)
                self.assertEqual(done["native_attempts_cumulative"],24)
                journal=runner._load_journal(out/"V291_JOURNAL.jsonl")
                modes=[r["hybrid_method"] for r in journal]
                self.assertEqual(modes.count(v305.GLOBAL),8)
                self.assertEqual(modes.count(v305.RESERVE),2)
                self.assertEqual(modes.count(v305.CONFIRM),3)
                self.assertGreaterEqual(modes.count(v305.GRID),1)
                self.assertGreaterEqual(modes.count(v305.PAIR),1)
                self.assertEqual(len({tuple(sorted(r["target"].items()))
                                      for r in journal if r["phase"]=="scout"}),21)
                self.assertEqual(self.exec_one(ctx,binary,out)[
                                 "new_native_this_invocation"],0)

    def test_hybrid_session_seal_opt_in_only(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx,binary,out=self.fixture(folder)
            with self.patches()[0],self.patches()[1]:
                self.exec_one(ctx,binary,out,max_new_native_this_invocation=2)
                seal=runner.read_json(out/"V291_SESSION.json")
                self.assertEqual(seal["experimental_adaptive_regions"][
                    "hybrid_v305"]["schema"],v305.SCHEMA)
                with self.assertRaisesRegex(
                        runner.LongRunBlocked,"SEALED_SESSION_IDENTITY_DRIFT"):
                    runner.run(ctx,F,binary,out,max_native_calls=24,
                               adaptive_region_resources=True,
                               adaptive_initial_global_calls=8,
                               adaptive_confirmation_calls=3,cache_only=True)
                with self.assertRaisesRegex(
                        runner.LongRunBlocked,"V305_SEPARATE_EXPERIMENTAL_POLICY_OPT_INS"):
                    runner.run(ctx,F,binary,out,max_native_calls=24,
                               hybrid_region_grid_neighbors=True,
                               adaptive_region_resources=True,cache_only=True)

    def test_cold_resume_pending_tamper_fails_without_new_native(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx,binary,out=self.fixture(folder)
            with self.patches()[0],self.patches()[1]:
                self.exec_one(ctx,binary,out,max_new_native_this_invocation=12)
                paused=self.exec_one(ctx,binary,out,cache_only=True)
                self.assertEqual(paused["status"],"PAUSED_CACHE_ONLY")
                pending_path=out/"V291_PENDING.json"
                expected=runner.read_json(pending_path)
                v304._global_order.cache_clear()
                self.assertEqual(self.exec_one(ctx,binary,out,cache_only=True)[
                                 "new_native_this_invocation"],0)
                self.assertEqual(runner.read_json(pending_path),expected)
                runner.atomic(pending_path,
                              dict(expected,hybrid_method="forged_plan"))
                with self.assertRaisesRegex(runner.LongRunBlocked,
                                            "V304_PENDING_PLAN_DRIFT"):
                    self.exec_one(ctx,binary,out,cache_only=True)
                runner.atomic(pending_path,expected)
                self.assertEqual(self.exec_one(
                    ctx,binary,out,max_new_native_this_invocation=1)[
                    "completed_cases"],13)

    def test_cancel_resume_exact(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx,binary,out=self.fixture(folder)
            cancel=pathlib.Path(folder)/"CANCEL"
            with self.patches()[0],self.patches()[1]:
                self.exec_one(ctx,binary,out,max_new_native_this_invocation=9)
                cancel.write_text("1")
                self.assertEqual(self.exec_one(ctx,binary,out,cancel_file=cancel)[
                                 "status"],"PAUSED_USER_CANCEL")
                cancel.unlink()
                self.assertEqual(self.exec_one(
                    ctx,binary,out,max_new_native_this_invocation=1)[
                    "completed_cases"],10)

    def test_pairwise_respects_chmv_bounds_and_unique(self):
        B=3107
        lo=(0,165,0,0)
        hi=(1864,)*4
        center=(800,800,800,707)
        row={"target":v290.legacy.to_target(center),
             "region_id":"r0","phase":"scout","dps_mean":189000.0,
             "dps_sem":300.0,"iterations":35}
        candidate=v305.pairwise_local_candidate(
            [row],"r0",center,.065,total=B,lower=lo,upper=hi)
        self.assertIsNotNone(candidate)
        self.assertNotEqual(tuple(candidate),center)
        self.assertTrue(v290.legacy.eligible(candidate,B,lo,hi))
        self.assertLessEqual(v290._distance(candidate,center),
                             round(B*.065*1.5))


if __name__=="__main__":
    unittest.main()
