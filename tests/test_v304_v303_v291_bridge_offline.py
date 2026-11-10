"""v304→v291 opt-in durable replay; synthetic Native only, never real SimC."""
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "runner"), str(ROOT / "tests")]
import v291_durable_multiscale_native_runner as runner
# Access fixture through its module to avoid unittest discovering the
# imported legacy TestCase again in this test module (duplicate CI work).
import test_p3_hx_durable_longrun_offline as fixture_module
F, fake_native, fake_ingest = (fixture_module.F,
                               fixture_module.fake_native,
                               fixture_module.fake_ingest)


class V304DurableRegionalBridge(unittest.TestCase):
    TOTAL = 24
    GLOBAL = 8
    CONFIRM = 3

    def fixture(self, folder):
        return fixture_module.V291LongRun().fixture(folder, cap=self.TOTAL)

    def call(self, context, binary, folder, **options):
        return runner.run(
            context, F, binary, folder,
            max_native_calls=self.TOTAL, adaptive_region_resources=True,
            adaptive_initial_global_calls=self.GLOBAL,
            adaptive_confirmation_calls=self.CONFIRM, **options)

    def patcher(self):
        return (
            mock.patch.object(runner.engine, "execute_one",
                              side_effect=fake_native),
            mock.patch.object(runner.oil, "ingest_native",
                              side_effect=fake_ingest)
        )

    def test_full_24_case_cohort_exact_phase_and_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx, binary, out = self.fixture(tmp)
            with self.patcher()[0], self.patcher()[1]:
                first = self.call(ctx, binary, out,
                                  max_new_native_this_invocation=10)
                self.assertEqual(first["completed_cases"], 10)
                self.assertEqual(first["policy"], runner.durable_regions.SCHEMA)
                seal = runner.read_json(out / "V291_SESSION.json")
                self.assertEqual(
                    seal["experimental_adaptive_regions"]["global_reserve_calls"],
                    2)
                stages = [r["adaptive_stage"] for r in runner._load_journal(
                    out / "V291_JOURNAL.jsonl")]
                self.assertEqual(stages[:8], ["global_initial"] * 8)

                replay = self.call(ctx, binary, out,
                                   max_new_native_this_invocation=0,
                                   cache_only=True)
                self.assertEqual(replay["completed_cases"], 10)
                self.assertEqual(replay["new_native_this_invocation"], 0)

                done = self.call(ctx, binary, out)
                self.assertEqual(done["status"], "BUDGET_EXHAUSTED")
                self.assertEqual(done["completed_cases"], self.TOTAL)
                self.assertEqual(done["native_attempts_cumulative"], self.TOTAL)
                journal = runner._load_journal(out / "V291_JOURNAL.jsonl")
                stages = [r["adaptive_stage"] for r in journal]
                self.assertEqual(stages.count("global_initial"), 8)
                self.assertEqual(stages.count("regional"), 11)
                self.assertEqual(stages.count("global_reserve"), 2)
                self.assertEqual(stages.count("confirmation"), 3)
                self.assertTrue(all(r["region_id"] is not None
                                    for r in journal if
                                    r["adaptive_stage"] == "regional"))
                self.assertEqual(len({
                    tuple(sorted(r["target"].items()))
                    for r in journal if r["phase"] == "scout"
                }), 21)
                self.assertEqual(len({
                    tuple(sorted(r["target"].items()))
                    for r in journal if r["phase"] == "precision"
                }), 3)
                self.assertFalse(done["no_global_optimum_proof"] is False)
                self.assertEqual(self.call(ctx, binary, out)["new_native_this_invocation"], 0)

    def test_seal_exclusive_and_options_immutable(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx, binary, out = self.fixture(tmp)
            with self.patcher()[0], self.patcher()[1]:
                self.call(ctx, binary, out, max_new_native_this_invocation=2)
                with self.assertRaisesRegex(runner.LongRunBlocked,
                                            "SEALED_SESSION_IDENTITY_DRIFT"):
                    runner.run(ctx, F, binary, out, max_native_calls=self.TOTAL,
                               max_new_native_this_invocation=0)
                with self.assertRaisesRegex(runner.LongRunBlocked,
                                            "SEALED_SESSION_IDENTITY_DRIFT"):
                    runner.run(ctx, F, binary, out, max_native_calls=self.TOTAL,
                               adaptive_region_resources=True,
                               adaptive_initial_global_calls=9,
                               adaptive_confirmation_calls=3,
                               max_new_native_this_invocation=0)
                with self.assertRaisesRegex(runner.LongRunBlocked,
                                            "V304_EXCLUSIVE_ADAPTIVE_REGION_OPT_IN"):
                    runner.run(ctx, F, binary, out, max_native_calls=self.TOTAL,
                               adaptive_region_resources=True,
                               percentage_grid_points=11, cache_only=True)

    def test_cancel_and_resume_exact_without_new_native(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx, binary, out = self.fixture(tmp)
            cancel = pathlib.Path(tmp) / "CANCEL"
            with self.patcher()[0], self.patcher()[1]:
                self.call(ctx, binary, out, max_new_native_this_invocation=6)
                cancel.write_text("x")
                canceled = self.call(ctx, binary, out, cancel_file=cancel)
                self.assertEqual(canceled["status"], "PAUSED_USER_CANCEL")
                cancel.unlink()
                resumed = self.call(ctx, binary, out,
                                    max_new_native_this_invocation=4)
                self.assertEqual(resumed["completed_cases"], 10)
                check = self.call(ctx, binary, out,
                                  max_new_native_this_invocation=0,
                                  cache_only=True)
                self.assertEqual(check["completed_cases"], 10)
                self.assertEqual(check["new_native_this_invocation"], 0)

    def test_cold_resume_reconstructs_region_radius_and_same_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx, binary, out = self.fixture(tmp)
            with self.patcher()[0], self.patcher()[1]:
                first = self.call(ctx, binary, out,
                                  max_new_native_this_invocation=14)
                self.assertEqual(first["completed_cases"], 14)
                journal = runner._load_journal(out / "V291_JOURNAL.jsonl")
                self.assertTrue(any(r["adaptive_stage"] == "regional"
                                    for r in journal))
                paused = self.call(ctx, binary, out, cache_only=True)
                self.assertEqual(paused["status"], "PAUSED_CACHE_ONLY")
                pending = runner.read_json(out / "V291_PENDING.json")
                # Simulate process restart: discard the only in-memory global
                # lattice cache; state comes from source SHA + accepted journal.
                runner.durable_regions._global_order.cache_clear()
                replay = self.call(ctx, binary, out, cache_only=True)
                self.assertEqual(replay["status"], "PAUSED_CACHE_ONLY")
                self.assertEqual(
                    runner.read_json(out / "V291_PENDING.json"), pending)
                self.assertEqual(replay["new_native_this_invocation"], 0)

    def test_adaptive_pending_replay_guards_metadata_and_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx, binary, out = self.fixture(tmp)
            with self.patcher()[0], self.patcher()[1]:
                paused = self.call(ctx, binary, out, cache_only=True)
                self.assertEqual(paused["status"], "PAUSED_CACHE_ONLY")
                pending_path = out / "V291_PENDING.json"
                expected = runner.read_json(pending_path)
                tampered = dict(expected, adaptive_stage="regional", region_id="r0")
                runner.atomic(pending_path, tampered)
                with self.assertRaisesRegex(runner.LongRunBlocked,
                                            "V304_PENDING_PLAN_DRIFT"):
                    self.call(ctx, binary, out, cache_only=True)
                runner.atomic(pending_path, expected)
                accepted = self.call(ctx, binary, out,
                                     max_new_native_this_invocation=1)
                self.assertEqual(accepted["completed_cases"], 1)


if __name__ == "__main__":
    unittest.main()
