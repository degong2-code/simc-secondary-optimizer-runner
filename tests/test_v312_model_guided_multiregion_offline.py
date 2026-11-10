"""v312 cubic surrogate + diversified SimC proposals; pure offline only.

Synthetic Native values below are NOT DPS evidence. Existing v291 byte-bound
runner is faked only to prove sealed opt-in identity, cancellation and resume.
"""
from __future__ import annotations

import math
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v290_multiscale_adaptive_policy as base
import v291_durable_multiscale_native_runner as durable
import v312_model_guided_multiregion_policy as policy
import test_p3_hx_durable_longrun_offline as fixture


STATS=("crit_rating","haste_rating","mastery_rating","versatility_rating")
B=3400
LOWER=(0,0,0,165)
UPPER=(2040,2040,2040,2040)


def synthetic(target):
    v=tuple(target[x] for x in STATS)
    # Two separated broad optima + a small deterministic pseudo-noise term.
    x,y,z,w=v
    modes=(math.exp(-sum((a-b)**2 for a,b in zip(v,
             (1020,816,1399,165)))/1_200_000),
           math.exp(-sum((a-b)**2 for a,b in zip(v,
             (700,1400,800,500)))/2_000_000))
    noisy=(sum(i*val for i,val in enumerate(v,1))%31-15)*22.
    return 163000+18000*modes[0]+14000*modes[1]+noisy


class V312ModelOptIn(unittest.TestCase):
    def test_cubic_model_is_only_prediction_not_dps_receipt(self):
        records=[]
        for point in policy._global_order(B,LOWER,UPPER,128):
            rows=base.legacy.to_target(point)
            records.append((point,float(synthetic(rows)),650.))
        model=policy._fit(tuple(records),B)
        predictions=[policy._predict(model,v,B) for v,_,_ in records]
        self.assertTrue(all(math.isfinite(v) for v in predictions))
        self.assertEqual(len(policy.EXPONENTS),20)
        self.assertLess(sum(abs(x-r[1]) for x,r in
                            zip(predictions,records))/len(records),3500)

    def test_128_global_then_16_diverse_with_exact_B_bounds_and_memoized_batch(self):
        rows=[]
        for idx in range(144):
            proposal=policy.next_plan(
                rows,total=B,lower=LOWER,upper=UPPER,
                max_native_calls=400,scout_iterations=35,
                confirmation_iterations=320)
            req=proposal["next_request"]
            self.assertEqual(req["phase"],"scout")
            self.assertEqual(req["iterations"],35)
            vector=tuple(req["target"][x] for x in STATS)
            self.assertEqual(sum(vector),B)
            self.assertTrue(base.legacy.eligible(vector,B,LOWER,UPPER))
            self.assertNotIn(vector,{tuple(r["target"][x] for x in STATS)
                                     for r in rows})
            self.assertEqual(req["surrogate_stage"],
                             "global" if idx<128 else "adaptive")
            rows.append(dict(req,index=idx,
                             dps_mean=float(synthetic(req["target"])),
                             dps_sem=650.,source="SYNTHETIC_NOT_NATIVE"))
        self.assertEqual(len(set(tuple(r["target"].values())
                                 for r in rows)),144)
        self.assertEqual(set(r["surrogate_method"] for r in rows[128:]),
                         {"model_ucb","measured_region","global_uncertainty"})
        policy.audit_recorded_history(
            rows,total=B,lower=LOWER,upper=UPPER,
            max_native_calls=400,scout_iterations=35,
            confirmation_iterations=320)
        copied=[dict(row) for row in rows]
        copied[130]["surrogate_rank"]+=1
        with self.assertRaisesRegex(policy.ProposalBlocked,
                                    "V312_RECORDED_SURROGATE_PLAN_OR_STAGE_DRIFT"):
            policy.audit_recorded_history(
                copied,total=B,lower=LOWER,upper=UPPER,
                max_native_calls=400,scout_iterations=35,
                confirmation_iterations=320)

    def test_optin_v291_native_fake_pending_cache_cancel_and_exclusive(self):
        with tempfile.TemporaryDirectory() as temp:
            ctx,binary,out=fixture.V291LongRun().fixture(temp,cap=400)
            with mock.patch.object(durable.engine,"execute_one",
                                   side_effect=fixture.fake_native), \
                 mock.patch.object(durable.oil,"ingest_native",
                                   side_effect=fixture.fake_ingest):
                first=durable.run(ctx,fixture.F,binary,out,
                    max_native_calls=400,model_guided_multiregion=True,
                    max_new_native_this_invocation=5)
                self.assertEqual(first["policy"],policy.SCHEMA)
                self.assertEqual(first["completed_cases"],5)
                self.assertEqual(first["new_native_this_invocation"],5)
                self.assertEqual(first["model_guided_progress"][
                                 "stage_counts"]["global"],5)
                second=durable.run(ctx,fixture.F,binary,out,
                    max_native_calls=400,model_guided_multiregion=True,
                    max_new_native_this_invocation=0,cache_only=True)
                self.assertEqual(second["new_native_this_invocation"],0)
                seal=durable.read_json(out/"V291_SESSION.json")
                self.assertIn("experimental_model_guided_regions",seal)
                with self.assertRaisesRegex(
                        durable.LongRunBlocked,
                        "SEALED_SESSION_IDENTITY_DRIFT"):
                    durable.run(ctx,fixture.F,binary,out,
                        max_native_calls=400,model_guided_multiregion=False,
                        max_new_native_this_invocation=0,cache_only=True)
                with self.assertRaisesRegex(
                        durable.LongRunBlocked,
                        "V312_EXCLUSIVE_EXPLICIT_MODEL_GUIDED_OPT_IN"):
                    durable.run(ctx,fixture.F,binary,out,
                        max_native_calls=400,model_guided_multiregion=True,
                        dense_nested_grid_max_level=21,
                        max_new_native_this_invocation=0,cache_only=True)
                cancel=pathlib.Path(temp)/"cancel"
                cancel.write_text("cancel")
                paused=durable.run(ctx,fixture.F,binary,out,
                    max_native_calls=400,model_guided_multiregion=True,
                    cancel_file=cancel)
                self.assertEqual(paused["status"],"PAUSED_USER_CANCEL")
                cancel.unlink()
                follow=durable.run(ctx,fixture.F,binary,out,
                    max_native_calls=400,model_guided_multiregion=True,
                    max_new_native_this_invocation=2)
                self.assertEqual(follow["completed_cases"],7)


if __name__=="__main__":
    unittest.main()
