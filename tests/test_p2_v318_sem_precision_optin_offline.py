"""v318 opt-in precision: synthetic observations and exact v291 replay, Native0."""
from __future__ import annotations
import json
import pathlib
import tempfile
import unittest
from unittest import mock

from runner import v290_multiscale_adaptive_policy as old
from runner import v318_sem_distance_precision_priority as policy
from runner import v291_durable_multiscale_native_runner as durable
from tests import test_p3_hx_durable_longrun_offline as fake

KEYS = ("crit_rating", "haste_rating", "mastery_rating", "versatility_rating")

def row(v, mean, sem, iters=35):
    return {"target":dict(zip(KEYS, v)), "dps_mean":float(mean),
            "dps_sem":float(sem), "iterations":iters}

class V318Precision(unittest.TestCase):
    def sample(self):
        a=(300,300,300,100)
        b=(310,290,300,100)
        c=(100,400,300,200)
        rows=[row(a,1000,10,320), row(b,999,30), row(c,994,5)]
        for i in range(11):
            v=(10+i*15,90,500,400-i*15)
            rows.append(row(v,850-i,5))
        return rows,a,b,c

    def call(self,planner,observations,used=14):
        return planner(
            observations, total=1000, lower=(0,0,0,0),
            upper=(1000,1000,1000,1000),
            native_calls_used=used, max_native_calls=100,
            scout_iterations=35, confirmation_iterations=320,
            max_iterations=320)

    def test_credible_distant_alternative_over_noisy_nearby_challenger(self):
        rows,a,b,c=self.sample()
        self.assertEqual(len({tuple(r["target"][k] for k in KEYS)
                             for r in rows}),14)
        baseline=self.call(old.next_plan,rows)
        selected=self.call(policy.next_plan,rows)
        self.assertEqual(baseline["next_request"]["phase"],"precision")
        self.assertEqual(baseline["next_request"]["target"],dict(zip(KEYS,b)))
        self.assertEqual(selected["next_request"]["target"],dict(zip(KEYS,c)))
        self.assertEqual(selected["next_request"]["iterations"],320)
        self.assertEqual(selected["decision"],"V318_SEM_AND_REGION_PRIORITY")

    def test_reference_absent_uses_highest_measured_mean(self):
        rows,a,b,c=self.sample()
        rows[0]["iterations"]=35
        got=self.call(policy.next_plan,rows)
        self.assertEqual(got["next_request"]["target"],dict(zip(KEYS,a)))
        self.assertEqual(got["decision"],"V318_FIRST_320_ANCHOR")

    def test_no_changes_when_scout_due_or_budget_exhausted(self):
        rows,a,b,c=self.sample()
        for used,observed in ((11,rows[:11]), (100,rows)):
            expected=self.call(old.next_plan,observed,used)
            actual=self.call(policy.next_plan,observed,used)
            self.assertEqual(actual,expected)

    def test_all_original_320_confirmed_or_ineligible_fallback(self):
        rows,a,b,c=self.sample()
        rows[1]["iterations"]=320
        rows[2]["dps_mean"]=500.
        output=self.call(policy.next_plan,rows)
        baseline=self.call(old.next_plan,rows)
        self.assertEqual(output,baseline)

    def test_duplicate_target_320_identity_fails_closed(self):
        rows,_,_,_=self.sample()
        rows.append(dict(rows[0]))
        with self.assertRaisesRegex(old.PolicyBlocked,
                                    "DUPLICATE_TARGET_ITERATION_IDENTITY"):
            self.call(old.next_plan,rows,15)
        # v318 uses the unqualified v290 import; exception class identity
        # may differ from the package-qualified import above.
        with self.assertRaisesRegex(policy.baseline.PolicyBlocked,
                                    "DUPLICATE_TARGET_ITERATION_IDENTITY"):
            self.call(policy.next_plan,rows,15)

    def test_v291_optin_seal_prevents_cross_policy_replay_and_native_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx,binary,out=fake.V291LongRun().fixture(tmp,cap=12)
            with mock.patch.object(durable.engine,"execute_one",
                                   side_effect=fake.fake_native), \
                 mock.patch.object(durable.oil,"ingest_native",
                                   side_effect=fake.fake_ingest):
                first=durable.run(
                    ctx,fake.F,binary,out,max_native_calls=12,
                    max_new_native_this_invocation=2,
                    sem_precision_priority_optin=True)
                self.assertEqual(first["new_native_this_invocation"],2)
                self.assertEqual(first["policy"], policy.SCHEMA)
                seal=json.loads((out/"V291_SESSION.json").read_text())
                self.assertIn("experimental_v318_sem_precision_priority",seal)
                with self.assertRaisesRegex(durable.LongRunBlocked,
                                            "SEALED_SESSION_IDENTITY_DRIFT"):
                    durable.run(ctx,fake.F,binary,out,
                                max_native_calls=12,
                                max_new_native_this_invocation=0,
                                cache_only=True)
                second=durable.run(
                    ctx,fake.F,binary,out,max_native_calls=12,
                    max_new_native_this_invocation=0,
                    cache_only=True,
                    sem_precision_priority_optin=True)
                self.assertEqual(second["new_native_this_invocation"],0)
                continued=durable.run(
                    ctx,fake.F,binary,out,max_native_calls=12,
                    max_new_native_this_invocation=2,
                    sem_precision_priority_optin=True)
                self.assertEqual(continued["new_native_this_invocation"],2)
                self.assertEqual(len(durable._load_journal(
                    out/"V291_JOURNAL.jsonl")),4)

    def test_other_optimizers_do_not_mix_with_v318(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx,binary,out=fake.V291LongRun().fixture(tmp,cap=12)
            with self.assertRaisesRegex(durable.LongRunBlocked,
                                        "V318_ONLY_PLAIN_V290_POLICY"):
                durable.run(ctx,fake.F,binary,out,max_native_calls=12,
                            sem_precision_priority_optin=True,
                            model_guided_multiregion=True)

if __name__=="__main__":
    unittest.main()
