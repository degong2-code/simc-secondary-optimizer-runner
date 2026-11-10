"""v306 P2 deterministic 12/24%B escape and v291 durable opt-in. Fake Native only."""
from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest
from collections import Counter
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"runner"),str(ROOT/"tests")]

import v290_multiscale_adaptive_policy as v290
import v304_v303_durable_adapter as v304
import v306_seed_retained_coarse_escape_regions as v306
import v291_durable_multiscale_native_runner as runner
import test_p3_hx_durable_longrun_offline as fixture_module

F=fixture_module.F
B=3107
LOWER=(0,165,0,0)
UPPER=(1864,)*4


def offline_plan(history, cap=68, global_calls=32, confirmations=4):
    return v306.next_plan(
        history, total=B, lower=LOWER, upper=UPPER,
        max_native_calls=cap, scout_iterations=35,
        confirmation_iterations=320,
        initial_global_calls=global_calls,
        confirmation_calls=confirmations)


class V306SeedRetained(unittest.TestCase):
    def test_complete_offline_budget_4520_seed_retained_and_12_pct_escape(self):
        history=[]
        global_order=v304._global_order(B,LOWER,UPPER,32)
        for i in range(68):
            plan=offline_plan(history)
            req=plan["next_request"]
            self.assertIsNotNone(req)
            vec=tuple(v290.legacy.key(req["target"]))
            self.assertTrue(v290.legacy.eligible(vec,B,LOWER,UPPER))
            if i<32:
                self.assertEqual(req["hybrid_method"],v306.GLOBAL)
                self.assertEqual(vec,global_order[i])
            elif i<64:
                self.assertEqual(req["phase"],"scout")
                self.assertIn(req["hybrid_method"],
                    (v306.GRID,v306.PAIR12,v306.PAIR24,
                     v306.PAIRFINE,v306.FALLBACK,v306.RESERVE))
            else:
                self.assertEqual(req["hybrid_method"],v306.CONFIRM)
            if req["phase"]=="scout":
                self.assertNotIn(vec,
                    {tuple(v290.legacy.key(r["target"])) for r in history
                     if r["phase"]=="scout"})
            mean=(199000.0 if i==31 else
                  183000.0+(i%11)*12 if i<32 else
                  175000.0+(i%7)*10)
            history.append(dict(
                target=req["target"],phase=req["phase"],
                iterations=req["iterations"],
                dps_mean=mean,dps_sem=850.0,
                region_id=req["region_id"],
                region_center=req["region_center"],
                region_radius_fraction=req["region_radius_fraction"],
                adaptive_stage=req["adaptive_stage"],
                hybrid_method=req["hybrid_method"]))
        self.assertIsNone(offline_plan(history)["next_request"])
        modes=Counter(r["hybrid_method"] for r in history)
        self.assertEqual(modes[v306.GLOBAL],32)
        self.assertEqual(modes[v306.RESERVE],5)
        self.assertEqual(modes[v306.CONFIRM],4)
        self.assertGreaterEqual(modes[v306.PAIR12],1)
        self.assertGreaterEqual(modes[v306.PAIR24],1)
        self.assertEqual(sum(r["iterations"] for r in history),
                         64*35+4*320)
        local=[r for r in history if r["adaptive_stage"]=="regional"]
        self.assertEqual(len(local),27)
        rid=local[0]["region_id"]
        seed=global_order[31]
        # Seed index31 is the highest synthetic actual measurement.
        first=next(r for r in local if r["region_id"]==rid)
        second=[r for r in local if r["region_id"]==rid][1]
        self.assertEqual(tuple(first["region_center"]),seed)
        self.assertEqual(tuple(second["region_center"]),seed)
        self.assertEqual(second["hybrid_method"],v306.PAIR12)
        self.assertLessEqual(v290._distance(
            tuple(v290.legacy.key(second["target"])),seed),round(B*.24))
        self.assertGreaterEqual(v290._distance(
            tuple(v290.legacy.key(second["target"])),seed),round(B*.10))
        counts=Counter(r["region_id"] for r in local)
        self.assertEqual(len(counts),8)
        self.assertTrue(all(n>=1 for n in counts.values()))
        self.assertLessEqual(max(counts.values()),11)

    def test_forged_hybrid_method_or_stage_refused(self):
        hist=[]
        req=offline_plan(hist)["next_request"]
        hist.append(dict(target=req["target"],phase=req["phase"],
                         iterations=req["iterations"],
                         dps_mean=185000.,dps_sem=250.,
                         region_id=req["region_id"],
                         region_center=req["region_center"],
                         region_radius_fraction=req["region_radius_fraction"],
                         adaptive_stage=req["adaptive_stage"],
                         hybrid_method=v306.PAIR12))
        with self.assertRaisesRegex(v306.PolicyBlocked,
                                    "V306_HISTORY_STAGE_METHOD_DRIFT"):
            offline_plan(hist)

    def test_v291_new_session_optin_exact_cache_pause_resume_and_seal(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx,binary,out=fixture_module.V291LongRun().fixture(folder,cap=24)
            def call(**kw):
                return runner.run(ctx,F,binary,out,max_native_calls=24,
                    seed_retained_coarse_escape_regions=True,
                    adaptive_initial_global_calls=8,
                    adaptive_confirmation_calls=3,**kw)
            with mock.patch.object(runner.engine,"execute_one",
                                   side_effect=fixture_module.fake_native),\
                 mock.patch.object(runner.oil,"ingest_native",
                                   side_effect=fixture_module.fake_ingest):
                first=call(max_new_native_this_invocation=12)
                self.assertEqual(first["completed_cases"],12)
                self.assertEqual(first["policy"],v306.SCHEMA)
                seal=runner.read_json(out/"V291_SESSION.json")
                self.assertEqual(seal["experimental_adaptive_regions"][
                    "seed_retained_v306"]["schema"],v306.SCHEMA)
                replay=call(cache_only=True)
                self.assertEqual(replay["status"],"PAUSED_CACHE_ONLY")
                self.assertEqual(replay["new_native_this_invocation"],0)
                pending=runner.read_json(out/"V291_PENDING.json")
                replay_again=call(cache_only=True)
                self.assertEqual(runner.read_json(out/"V291_PENDING.json"),pending)
                self.assertEqual(replay_again["new_native_this_invocation"],0)
                journal=runner._load_journal(out/"V291_JOURNAL.jsonl")
                self.assertTrue(all("hybrid_method" in r for r in journal))
                with self.assertRaisesRegex(
                        runner.LongRunBlocked,"SEALED_SESSION_IDENTITY_DRIFT"):
                    runner.run(ctx,F,binary,out,max_native_calls=24,
                               hybrid_region_grid_neighbors=True,
                               adaptive_initial_global_calls=8,
                               adaptive_confirmation_calls=3,
                               cache_only=True)
                with self.assertRaisesRegex(
                        runner.LongRunBlocked,
                        "V306_EXCLUSIVE_EXPERIMENTAL_POLICY_OPT_INS"):
                    runner.run(ctx,F,binary,out,max_native_calls=24,
                               hybrid_region_grid_neighbors=True,
                               seed_retained_coarse_escape_regions=True,
                               adaptive_initial_global_calls=8,
                               adaptive_confirmation_calls=3,
                               cache_only=True)
                done=call()
                self.assertEqual(done["status"],"BUDGET_EXHAUSTED")
                self.assertEqual(done["completed_cases"],24)
                self.assertEqual(call()["new_native_this_invocation"],0)


if __name__=="__main__":
    unittest.main()
