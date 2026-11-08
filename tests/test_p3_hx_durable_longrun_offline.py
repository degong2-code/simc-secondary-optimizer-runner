"""v291 long-run control and source binding, offline only.

Native and oil acceptance are synthetic fakes; they are not SimC evidence.
"""
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v291_durable_multiscale_native_runner as runner
from test_v094_durable_inclusive_adaptive_runner import V094Durable

F={"crit_rating":0,"haste_rating":165,"mastery_rating":0,"versatility_rating":0}


def fake_native(req,calibration,binary,folder,progress,*,
                cache_only=False,cancel_file=None,
                recover_verified_partial=False):
    folder=pathlib.Path(folder)
    source=folder/"input.simc"
    native=folder/"result.json"
    receipt=folder/"native_receipt.json"
    if receipt.exists():
        assert source.read_bytes()==req["input"].encode()
        doc=json.loads(native.read_bytes())
        assert doc["case_key"]==req["case_key"]
        return {"case_key":req["case_key"],
                "native_json_sha256":hashlib.sha256(native.read_bytes()).hexdigest(),
                "source":"CACHED_VERIFIED_NATIVE"}
    if cache_only:
        raise ValueError("CACHE_ONLY_REFUSES_NEW_NATIVE")
    if progress["native_attempts"]:
        raise ValueError("PARTIAL_NATIVE_MUST_NOT_RETRY")
    folder.mkdir(parents=True,exist_ok=True)
    source.write_bytes(req["input"].encode())
    target=req["v092_base_target"]
    dps=185000.0-0.0009*sum((v-800)**2 for v in target.values())
    raw=json.dumps({"case_key":req["case_key"],"dps":dps},sort_keys=True).encode()
    native.write_bytes(raw)
    receipt.write_text(json.dumps({"case_key":req["case_key"]}))
    runner.atomic(folder.parent/"V065_PROGRESS.json",
                  {"native_attempts":1,"status":"RUNNING_NATIVE"})
    return {"case_key":req["case_key"],
            "native_json_sha256":hashlib.sha256(raw).hexdigest(),
            "source":"NEW_NATIVE"}


def fake_ingest(req,doc,raw):
    assert doc["case_key"]==req["case_key"]
    return {"case_key":req["case_key"],"native_json_sha256":hashlib.sha256(raw).hexdigest(),
            "dps_mean":doc["dps"],"dps_sem":300.0,
            "dps_samples":req["iterations"],
            "simc_seed":12345,"status":"PASS_NATIVE_DPS_AND_STATIC_CHMV_INPUT"}


class V291LongRun(unittest.TestCase):
    def fixture(self,folder):
        from test_v091_weapon_oil_external_adapter import fury, REV
        import v091_weapon_oil_external_adapter as adapter
        import v093_inclusive_adaptive_scheduler_bridge as adaptive
        import v046_static_item_cache as static_cache
        p,c,f=fury(folder)
        c["runtime"]["max_native_calls"]=6
        prepared=adapter.prepare(
            p,c,f,static_cache.empty_cache(),
            "dual_two_hand",["main_hand","off_hand"])
        binary=pathlib.Path(folder)/"dummy-simc"
        binary.write_bytes(b"synthetic test-only executable SHA")
        ctx=adaptive.prepare(
            prepared,hashlib.sha256(binary.read_bytes()).hexdigest(),REV,35,80)
        return ctx,binary,pathlib.Path(folder)/"longrun"

    def test_three_native_resume_exact_replay_zero_new_and_cancel(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx,binary,out=self.fixture(folder)
            with mock.patch.object(runner.engine,"execute_one",side_effect=fake_native), \
                 mock.patch.object(runner.oil,"ingest_native",side_effect=fake_ingest):
                first=runner.run(ctx,F,binary,out,max_native_calls=6,
                    max_new_native_this_invocation=3)
                self.assertEqual(first["completed_cases"],3)
                self.assertEqual(first["native_attempts_cumulative"],3)
                self.assertEqual(first["status"],"PAUSED_INVOCATION_NATIVE_BUDGET")
                self.assertEqual(first["new_native_this_invocation"],3)
                replay=runner.run(ctx,F,binary,out,max_native_calls=6,
                    max_new_native_this_invocation=0)
                self.assertEqual(replay["new_native_this_invocation"],0)
                self.assertEqual(replay["completed_cases"],3)
                stop=pathlib.Path(folder)/"CANCEL"
                stop.write_text("x")
                canceled=runner.run(ctx,F,binary,out,max_native_calls=6,cancel_file=stop)
                self.assertEqual(canceled["status"],"PAUSED_USER_CANCEL")
                stop.unlink()
                done=runner.run(ctx,F,binary,out,max_native_calls=6)
                self.assertEqual(done["status"],"BUDGET_EXHAUSTED")
                self.assertEqual(done["completed_cases"],6)
                self.assertEqual(done["native_attempts_cumulative"],6)
                again=runner.run(ctx,F,binary,out,max_native_calls=6)
                self.assertEqual(again["new_native_this_invocation"],0)
                self.assertEqual(again["completed_cases"],6)

    def test_fail_closed_on_tampered_real_case_and_session(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx,binary,out=self.fixture(folder)
            with mock.patch.object(runner.engine,"execute_one",side_effect=fake_native), \
                 mock.patch.object(runner.oil,"ingest_native",side_effect=fake_ingest):
                runner.run(ctx,F,binary,out,max_native_calls=6,
                           max_new_native_this_invocation=2)
                with self.assertRaisesRegex(runner.LongRunBlocked,
                                             "SEALED_SESSION_IDENTITY_DRIFT"):
                    runner.run(ctx,F,binary,out,max_native_calls=5)
                path=runner.case_folder(out,0)/"result.json"
                doc=json.loads(path.read_text())
                doc["dps"]=1.0
                path.write_text(json.dumps(doc))
                with self.assertRaisesRegex(runner.LongRunBlocked,
                                             "RECORDED_NATIVE_CASE_BYTES_OR_SUMMARY_DRIFT"):
                    runner.run(ctx,F,binary,out,max_native_calls=6)

    def test_cache_only_no_native_and_partial_attempt_refuses_repeat(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx,binary,out=self.fixture(folder)
            with mock.patch.object(runner.engine,"execute_one",side_effect=fake_native), \
                 mock.patch.object(runner.oil,"ingest_native",side_effect=fake_ingest):
                first=runner.run(ctx,F,binary,out,max_native_calls=6,
                                 cache_only=True)
                self.assertEqual(first["status"],"PAUSED_CACHE_ONLY")
                self.assertEqual(first["native_attempts_cumulative"],0)
                parent=runner.case_folder(out,0).parent
                runner.atomic(parent/"V065_PROGRESS.json",
                              {"native_attempts":1,"status":"RUNNING_NATIVE"})
                with self.assertRaisesRegex(runner.LongRunBlocked,
                                            "PARTIAL_NATIVE_NEEDS_EXPLICIT_RECOVERY"):
                    runner.run(ctx,F,binary,out,max_native_calls=6)
if __name__=="__main__":
    unittest.main()
