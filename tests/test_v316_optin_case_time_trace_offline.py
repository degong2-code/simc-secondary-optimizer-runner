"""v316 optional per-case clock sidecar: SYNTHETIC executor, ZERO SimC Native.

Never use these fake Native results to claim DPS performance or timings.
Default v291 journal/session seal/case identity remain byte-compatible.
"""
from __future__ import annotations

import json
import pathlib
import tempfile
import unittest
from unittest import mock

from tests import test_p3_hx_durable_longrun_offline as fake
from runner import v291_durable_multiscale_native_runner as durable
trace = durable.time_trace  # exact module instance used by the runner


class V316IndependentNativeCaseTrace(unittest.TestCase):
    def test_optin_only_cache_resume_cancel_no_retimed_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx,binary,out=fake.V291LongRun().fixture(tmp,cap=12)
            with mock.patch.object(durable.engine,"execute_one",
                                   side_effect=fake.fake_native), \
                 mock.patch.object(durable.oil,"ingest_native",
                                   side_effect=fake.fake_ingest):
                first=durable.run(ctx,fake.F,binary,out,max_native_calls=12,
                    max_new_native_this_invocation=2)
                seal_bytes=(out/"V291_SESSION.json").read_bytes()
                self.assertNotIn("experimental_case_timing_trace",first)
                self.assertFalse((out/trace.NAME).exists())
                second=durable.run(ctx,fake.F,binary,out,max_native_calls=12,
                    max_new_native_this_invocation=2,case_timing_trace=True)
                report=second["experimental_case_timing_trace"]
                self.assertEqual(report["case_time_trace_rows"],2)
                self.assertEqual(report["untraced_journal_indices"],[0,1])
                self.assertFalse(report["complete_original_journal_trace"])
                self.assertEqual([x["index"] for x in trace.load(
                    out/trace.NAME,durable._load_journal(
                        out/"V291_JOURNAL.jsonl"),
                    trace.identity_hash(out/"V291_SESSION.json"))],[2,3])
                before=(out/trace.NAME).read_bytes()
                replay=durable.run(ctx,fake.F,binary,out,max_native_calls=12,
                    max_new_native_this_invocation=0,cache_only=True,
                    case_timing_trace=True)
                self.assertEqual(replay["new_native_this_invocation"],0)
                self.assertEqual((out/trace.NAME).read_bytes(),before)
                stop=pathlib.Path(tmp)/"cancel"
                stop.write_text("stop")
                paused=durable.run(ctx,fake.F,binary,out,max_native_calls=12,
                    cancel_file=stop,case_timing_trace=True)
                self.assertEqual(paused["status"],"PAUSED_USER_CANCEL")
                self.assertEqual((out/trace.NAME).read_bytes(),before)
                stop.unlink()
                next_=durable.run(ctx,fake.F,binary,out,max_native_calls=12,
                    max_new_native_this_invocation=1,case_timing_trace=False)
                self.assertEqual(next_["new_native_this_invocation"],1)
                final=durable.run(ctx,fake.F,binary,out,max_native_calls=12,
                    max_new_native_this_invocation=2,case_timing_trace=True)
                summary=final["experimental_case_timing_trace"]
                self.assertEqual(summary["untraced_journal_indices"],[0,1,4])
                self.assertEqual(summary["new_native_traced"],4)
                self.assertEqual((out/"V291_SESSION.json").read_bytes(),seal_bytes)
                self.assertTrue(all(x["source"]=="NEW_NATIVE" for x in
                                    trace.load(out/trace.NAME,
                                        durable._load_journal(
                                            out/"V291_JOURNAL.jsonl"),
                                        trace.identity_hash(
                                            out/"V291_SESSION.json"))))

    def test_trace_tampering_blocks_optin_before_any_second_native(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx,binary,out=fake.V291LongRun().fixture(tmp,cap=6)
            with mock.patch.object(durable.engine,"execute_one",
                                   side_effect=fake.fake_native), \
                 mock.patch.object(durable.oil,"ingest_native",
                                   side_effect=fake.fake_ingest):
                durable.run(ctx,fake.F,binary,out,max_native_calls=6,
                    max_new_native_this_invocation=2,case_timing_trace=True)
                path=out/trace.NAME
                lines=path.read_text().splitlines()
                first=json.loads(lines[0])
                first["engine_execute_seconds"]=-1
                lines[0]=json.dumps(first,sort_keys=True)
                path.write_text("\n".join(lines)+"\n")
                with self.assertRaisesRegex(trace.TraceBlocked,
                                             "ORIGINAL_NATIVE_TRACE_INTEGRITY"):
                    durable.run(ctx,fake.F,binary,out,max_native_calls=6,
                        max_new_native_this_invocation=0,
                        cache_only=True,case_timing_trace=True)
                # Default remains source-compatible and does not consume the
                # auxiliary trace, even if a supplemental metric was tampered.
                replay=durable.run(ctx,fake.F,binary,out,max_native_calls=6,
                    max_new_native_this_invocation=0,cache_only=True)
                self.assertEqual(replay["new_native_this_invocation"],0)

    def test_trace_append_crash_never_duplicates_original_native(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx,binary,out=fake.V291LongRun().fixture(tmp,cap=6)
            count=[0]
            def count_native(*args,**kwargs):
                if not (pathlib.Path(args[3])/"native_receipt.json").exists():
                    count[0]+=1
                return fake.fake_native(*args,**kwargs)
            with mock.patch.object(durable.engine,"execute_one",
                                   side_effect=count_native), \
                 mock.patch.object(durable.oil,"ingest_native",
                                   side_effect=fake.fake_ingest):
                with mock.patch.object(trace,"append",
                        side_effect=OSError("SYNTHETIC_TRACE_DISK_FULL")):
                    with self.assertRaisesRegex(OSError,"TRACE_DISK_FULL"):
                        durable.run(ctx,fake.F,binary,out,max_native_calls=6,
                            max_new_native_this_invocation=1,
                            case_timing_trace=True)
                self.assertEqual(count[0],1)
                self.assertEqual(len(durable._load_journal(
                    out/"V291_JOURNAL.jsonl")),1)
                resumed=durable.run(ctx,fake.F,binary,out,max_native_calls=6,
                    max_new_native_this_invocation=1,
                    case_timing_trace=True)
                self.assertEqual(count[0],2)
                self.assertEqual(resumed["completed_cases"],2)
                self.assertEqual(resumed["experimental_case_timing_trace"][
                    "untraced_journal_indices"],[0])


    def test_single_process_wall_checkpoint_is_confirmed_only(self):
        import copy
        invocation="b"*32
        journal=[]
        timing=[]
        for i,(phase,elapsed,dps,sem,seed) in enumerate((
                ("scout",100.,182000.,650.,1),
                ("precision",210.,185000.,100.,3),
                ("precision",480.,186000.,100.,4))):
            row={
                "index":i,"phase":phase,
                "iterations":35 if phase=="scout" else 320,
                "case_key":f"fake-{i}","input_sha256":"a"*64,
                "native_sha256":"c"*64,"source":"NEW_NATIVE",
                "simc_seed":seed,"dps_mean":dps,"dps_sem":sem,
            }
            journal.append(row)
            timing.append(trace.record(
                row,session_sha256="d"*64,plan_pending_seconds=.01,
                engine_execute_seconds=elapsed/10,
                native_json_ingest_seconds=.002,
                journal_checkpoint_seconds=.003,
                invocation_elapsed_seconds=elapsed,
                resumed_pending=False,invocation_id=invocation))
        ck=trace.checkpoints(timing,journal,320)
        self.assertTrue(ck["exact_5_10_minute_result_available"])
        at300=ck["checkpoints"]["300"]
        at600=ck["checkpoints"]["600"]
        self.assertEqual(at300["highest_observed_confirmed_dps"],185000.)
        self.assertEqual(at300["confirmed_320_or_configured_iteration_candidates"],1)
        self.assertEqual(at600["highest_observed_confirmed_dps"],186000.)
        self.assertEqual(at600["confirmed_320_or_configured_iteration_candidates"],2)
        self.assertTrue(at600["selected_pair_95"][
            "selected_pair_nominal_95_separated"])
        self.assertTrue(at600["selected_pair_95"][
            "multiplicity_and_selection_bias_not_corrected"])
        changed=copy.deepcopy(timing)
        changed[2]["invocation_id"]="e"*32
        other=trace.checkpoints(changed,journal,320)
        self.assertFalse(other["exact_5_10_minute_result_available"])
        changed=copy.deepcopy(timing)
        changed[2]["invocation_elapsed_seconds"]=150.
        other=trace.checkpoints(changed,journal,320)
        self.assertFalse(other["exact_5_10_minute_result_available"])
        self.assertFalse(trace.checkpoints(timing[1:],journal,320)[
            "exact_5_10_minute_result_available"])

    def test_whole_uninterrupted_fake_run_reports_real_clock_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx,binary,out=fake.V291LongRun().fixture(tmp,cap=12)
            with mock.patch.object(durable.engine,"execute_one",
                                   side_effect=fake.fake_native), \
                 mock.patch.object(durable.oil,"ingest_native",
                                   side_effect=fake.fake_ingest):
                result=durable.run(ctx,fake.F,binary,out,max_native_calls=12,
                                   case_timing_trace=True)
                self.assertEqual(result["completed_cases"],12)
                self.assertTrue(result["experimental_case_timing_trace"][
                    "complete_original_journal_trace"])
                checkpoints=result["experimental_wall_confirmed_checkpoints"]
                self.assertTrue(checkpoints[
                    "exact_5_10_minute_result_available"])
                self.assertGreater(checkpoints["checkpoints"]["300"][
                    "confirmed_320_or_configured_iteration_candidates"],0)
                self.assertFalse(checkpoints["global_optimum_proven"])
                journal=durable._load_journal(out/"V291_JOURNAL.jsonl")
                self.assertTrue(all("engine_execute_seconds" not in row
                                    for row in journal))
                self.assertNotIn("v316",str((out/"V291_SESSION.json").read_text()).lower())

if __name__=="__main__":
    unittest.main()
