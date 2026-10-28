"""v147 24-spec batch: pure stage, bounded mocked Native, resume, isolation.

NEVER invokes real SimulationCraft. Offline counterexamples are not receipts.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
sys.path.insert(0,str(ROOT/"integration_probes"))
import v147_all_dps_targeted_native_batch as batch

REV="7bc10711b5"

class BatchOffline(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root=pathlib.Path(temp.name)
        self.binary=self.root/"fake_simc.exe"
        self.binary.write_bytes(b"NO_ACTUAL_SIMC")
        self.out=self.root/"batch"

    def scoped(self):
        h=hashlib.sha256(self.binary.read_bytes()).hexdigest()
        return self.out/("simc_"+h[:16]+"_"+REV)

    def test_default_all_24_full_source_free_plan_without_native_or_fixtures(self):
        self.assertEqual(len(batch.ALL_SPECS),24)
        self.assertEqual(
            set(batch.ALL_SPECS),
            {"/".join(k) for k in batch.bootstrap.ARCHETYPES})
        self.assertFalse(set(batch.ALL_SPECS) & {
            "/".join(k) for k in batch.bootstrap.PURE_PRODUCT_SPECS})
        original_text=pathlib.Path.read_text
        original_bytes=pathlib.Path.read_bytes
        reads=[]
        def block(path):
            loc=str(path).replace(chr(92),"/")
            if "/integration_probes/fixtures/" in loc and loc.endswith(".simc"):
                reads.append(loc)
                raise AssertionError("FULL_SIMC_FIXTURE_READ_BY_BATCH")
        def read_text(path,*args,**kwargs):
            block(path)
            return original_text(path,*args,**kwargs)
        def read_bytes(path,*args,**kwargs):
            block(path)
            return original_bytes(path,*args,**kwargs)
        with mock.patch.object(pathlib.Path,"read_text",read_text), \
             mock.patch.object(pathlib.Path,"read_bytes",read_bytes), \
             mock.patch.object(batch.physical.subprocess,"run") as native:
            report=batch.run(self.binary,self.out,REV)
            native.assert_not_called()
        self.assertEqual(reads,[])
        self.assertEqual(report["status"],"FINISHED_WITH_PER_SPEC_RESULTS")
        self.assertEqual(len(report["results"]),24)
        self.assertEqual(report["counts"],{"PENDING_PHYSICAL_NATIVE":24})
        self.assertEqual(report["physical_new_native_calls"],0)
        self.assertEqual(report["adaptive_specs_attempted_this_run"],0)
        self.assertTrue((self.scoped()/"SUMMARY.json").is_file())
        self.assertEqual(len(list((self.scoped()/"physical").glob(
            "*/stage/profile.simc"))),24)

    def test_execute_requires_explicit_two_switches_and_selection_contract(self):
        with self.assertRaisesRegex(batch.BatchBlocked,
                                    "BATCH_NATIVE_REQUIRES_EXPLICIT_EXECUTE"):
            batch.run(self.binary,self.out,REV,max_new_physical=1)
        with self.assertRaisesRegex(batch.BatchBlocked,
                                    "BATCH_NATIVE_REQUIRES_EXPLICIT_EXECUTE"):
            batch.run(self.binary,self.out,REV,optimize_accepted=True)
        with self.assertRaisesRegex(batch.BatchBlocked,
                                    "SPEC_SELECTION_UNKNOWN_OR_DUPLICATED"):
            batch.run(self.binary,self.out,REV,specs=["mage/frost","mage/frost"])
        with self.assertRaisesRegex(batch.BatchBlocked,
                                    "SPEC_SELECTION_UNKNOWN_OR_DUPLICATED"):
            batch.run(self.binary,self.out,REV,specs=["evoker/devastation"])
        with self.assertRaisesRegex(batch.BatchBlocked,
                                    "BATCH_SIMC_REVISION_MUST_BE_VERIFIED_GIT_HEX"):
            batch.run(self.binary,self.out,"fake-version",specs=["mage/frost"])
        self.assertFalse(self.out.exists())

    def test_three_specs_native_one_failure_isolated_other_two_adaptive(self):
        specs=["mage/frost","rogue/outlaw","warrior/fury"]
        calls=[]
        def simc(cmd,*,cwd,stdout,stderr,timeout,check):
            calls.append(str(cwd))
            key=pathlib.Path(cwd).name.split("__")[0]
            if key=="rogue":
                stdout.write(b"SimC real error text preserved in per-spec log\n")
                return subprocess.CompletedProcess(cmd,2)
            native={"report_version":"2.0.0","git_revision":REV,
                    "sim":{"players":[{"name":"mock",
                    "specialization":"frost",
                    "collected_data":{"dps":{"mean":19521.0}}}]}}
            (pathlib.Path(cwd)/"physical.json").write_text(json.dumps(native))
            stdout.write(b"NO REAL SIMC used by offline test\n")
            return subprocess.CompletedProcess(cmd,0)
        durable_return={
            "status":"PASS_BOUNDED_GENERIC_NATIVE_SEARCH_AND_CACHE",
            "new_native_attempts_cumulative":6,
            "verified_cache_hits_this_run":0,
            "B":3150,"official_final_T":3150}
        with mock.patch.object(batch.physical.subprocess,"run",
                               side_effect=simc) as physical_native, \
             mock.patch.object(batch.bootstrap.entry.durable,"run",
                               return_value=durable_return) as adaptive, \
             mock.patch.object(batch.bootstrap.entry,"user_facing_result",
                               return_value={"confidence_level":0.95,
                                            "observed_first_choice":
                                                {"observed_dps_mean":21000}}):
            report=batch.run(self.binary,self.out,REV,specs=specs,
                             execute=True,max_new_physical=3,
                             optimize_accepted=True,max_adaptive_specs=3)
            self.assertEqual(physical_native.call_count,3)
            self.assertEqual(adaptive.call_count,2)
            self.assertTrue(all(call.kwargs["open_folder"] is False
                                for call in adaptive.call_args_list))
            # Re-run: one failure retained, two successes cache-reused; the
            # existing adaptive runner is still responsible for its own
            # durable resume/cache verification.
            resumed=batch.run(self.binary,self.out,REV,specs=specs,
                              execute=True,max_new_physical=0,
                              optimize_accepted=True,max_adaptive_specs=3)
            self.assertEqual(physical_native.call_count,3)
            self.assertEqual(adaptive.call_count,4)
        self.assertEqual(report["physical_new_native_calls"],3)
        self.assertEqual(report["counts"],{"ADAPTIVE_PASS":2,
                                            "PHYSICAL_FAILED_RETAINED":1})
        self.assertEqual(report["adaptive_specs_attempted_this_run"],2)
        self.assertEqual(resumed["physical_new_native_calls"],0)
        self.assertEqual(resumed["counts"],{"ADAPTIVE_PASS":2,
                                             "PHYSICAL_FAILED_RETAINED":1})
        failures=[r for r in report["results"] if r["status"]==
                  "PHYSICAL_FAILED_RETAINED"]
        self.assertEqual(len(failures),1)
        self.assertIn("SimC real error text",
                      pathlib.Path(failures[0]["simc_raw_log"]).read_text())

    def test_global_cancel_then_resume_uses_identical_starter_identities(self):
        root=self.scoped()
        root.mkdir(parents=True)
        (root/"CANCEL").touch()
        with mock.patch.object(batch.physical.subprocess,"run") as native:
            paused=batch.run(self.binary,self.out,REV,
                             specs=["mage/frost","warrior/fury"])
            native.assert_not_called()
        self.assertEqual(paused["status"],"CANCELLED_BETWEEN_SPECIALIZATIONS")
        self.assertEqual(paused["results"],[])
        (root/"CANCEL").unlink()
        with mock.patch.object(batch.physical.subprocess,"run") as native:
            continued=batch.run(self.binary,self.out,REV,
                                specs=["mage/frost","warrior/fury"])
            native.assert_not_called()
        self.assertEqual(continued["counts"],{"PENDING_PHYSICAL_NATIVE":2})

    def test_bounded_one_call_per_launch_auto_resumes_next_spec(self):
        selected=["mage/frost","rogue/outlaw","warrior/fury"]
        calls=[]
        def simc(cmd,*,cwd,stdout,stderr,timeout,check):
            calls.append(str(cwd))
            native={"report_version":"2.0.0","git_revision":REV,
                    "sim":{"players":[{"collected_data":{
                        "dps":{"mean":5500.0}}}]}}
            (pathlib.Path(cwd)/"physical.json").write_text(json.dumps(native))
            return subprocess.CompletedProcess(cmd,0)
        with mock.patch.object(batch.physical.subprocess,"run",
                               side_effect=simc):
            for expected in (1,2,3):
                report=batch.run(self.binary,self.out,REV,specs=selected,
                                 execute=True,max_new_physical=1)
                self.assertEqual(len(calls),expected)
                self.assertEqual(report["physical_new_native_calls"],1)
                self.assertEqual(report["counts"].get(
                    "PHYSICAL_PASS_ADAPTIVE_PENDING"),expected)
                self.assertEqual(report["counts"].get(
                    "PENDING_PHYSICAL_NATIVE",0),3-expected)
            cached=batch.run(self.binary,self.out,REV,specs=selected,
                             execute=True,max_new_physical=1)
        self.assertEqual(len(calls),3)
        self.assertEqual(cached["physical_new_native_calls"],0)
        self.assertEqual(cached["counts"],{
            "PHYSICAL_PASS_ADAPTIVE_PENDING":3})

    def test_batch_root_os_lock_blocks_second_concurrent_worker(self):
        with batch.sessions.worker_lock(self.scoped()):
            with mock.patch.object(batch.physical.subprocess,"run") as native:
                with self.assertRaisesRegex(batch.sessions.SessionBlocked,
                                           "V106_SAME_SESSION_ALREADY_RUNNING"):
                    batch.run(self.binary,self.out,REV,specs=["mage/frost"])
                native.assert_not_called()

    def test_no_adaptive_when_only_prepared_and_adaptive_subset_cap(self):
        with mock.patch.object(batch.physical.subprocess,"run") as simc, \
             mock.patch.object(batch.bootstrap.entry.durable,"run") as adaptive:
            report=batch.run(self.binary,self.out,REV,
                 specs=["mage/frost","warrior/fury"],execute=True,
                 max_new_physical=0,optimize_accepted=True,
                 max_adaptive_specs=24)
            simc.assert_not_called()
            adaptive.assert_not_called()
        self.assertEqual(report["counts"],{"PENDING_PHYSICAL_NATIVE":2})

if __name__=="__main__":
    unittest.main()
