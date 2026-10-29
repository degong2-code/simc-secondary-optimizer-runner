"""v145 P1 one-spec physical SimC diagnostic. Mocked subprocess ONLY; Native 0."""
from __future__ import annotations
import copy
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"integration_probes"))
sys.path.insert(0,str(ROOT/"runner"))
import v145_targeted_pure_physical_native as target
import v098_target_user_scenario_bootstrap as bootstrap

REVISION="7bc10711b5"

def user_for(key):
    cl,sp=key.split("/")
    return {"schema":bootstrap.SCHEMA,
            "character":{"class":cl,"spec":sp,"race":"dwarf",
                         "talents":"CAAAABBB11122"},
            "target":{"ilevel":334,"final_T":None},
            "trinkets":[{"slot":"trinket1","item_id":270175,"options":{}},
                        {"slot":"trinket2","item_id":270173,"options":{}}],
            "special_items":[],"embellishments":[],"oil_hands":[],
            "combat":{"targets":1,"duration_seconds":300,"raid_buffs":True}}

class OneSpecDiagnosticOffline(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root=pathlib.Path(temp.name)
        self.binary=self.root/"fake_simc"
        self.binary.write_bytes(b"FAKE_NO_NATIVE")
        self.out=self.root/"runs"

    def test_starter_spec_command_reads_no_complete_simc_and_defaults_to_zero_calls(self):
        original_text=pathlib.Path.read_text
        original_bytes=pathlib.Path.read_bytes
        attempts=[]
        def deny_fixture(path,*args,**kw):
            if ("/integration_probes/fixtures/" in
                str(path).replace(chr(92),"/") and str(path).endswith(".simc")):
                attempts.append(str(path))
                raise AssertionError("LEGACY_COMPLETE_PROFILE_WAS_READ")
        def text_read(path,*args,**kw):
            deny_fixture(path)
            return original_text(path,*args,**kw)
        def bytes_read(path,*args,**kw):
            deny_fixture(path)
            return original_bytes(path,*args,**kw)
        with mock.patch.object(pathlib.Path,"read_text",text_read), \
             mock.patch.object(pathlib.Path,"read_bytes",bytes_read), \
             mock.patch.object(target.subprocess,"run") as proc, \
             mock.patch.object(target.os,"startfile",create=True):
            result=target.main([
                "--starter-spec","mage/frost",
                "--simc",str(self.binary),
                "--revision",REVISION,
                "--out",str(self.out)])
            proc.assert_not_called()
        self.assertEqual(result,0)
        self.assertEqual(attempts,[])
        cases=list(self.out.glob("mage__frost__*"))
        self.assertEqual(len(cases),1)
        generated=json.loads((cases[0]/"user.json").read_text())
        self.assertEqual(generated["character"]["spec"],"frost")
        self.assertEqual(generated["oil_hands"],[])
        self.assertEqual(len(generated["trinkets"]),2)
        self.assertFalse((cases[0]/"physical.simc").exists())

    def test_default_zero_calls_and_no_unreceipted_profile_files(self):
        u=user_for("mage/frost")
        with mock.patch.object(target.subprocess,"run") as proc:
            result=target.run(u,self.binary,self.out,REVISION,max_new=0)
            proc.assert_not_called()
        self.assertEqual(result["status"],"PREPARED_NO_NATIVE")
        self.assertEqual(result["new_native_calls"],0)
        folder=pathlib.Path(result["output_dir"])
        self.assertTrue((folder/"stage"/"manifest.json").exists())
        self.assertTrue((folder/"stage"/"profile.simc").exists())
        self.assertFalse((folder/"physical.simc").exists())
        self.assertFalse((folder/"receipt.json").exists())
        self.assertFalse((folder/"physical.json").exists())
        summary=json.loads((folder/"SUMMARY.json").read_text())
        self.assertFalse(summary["user_optimizer_ready"])
        self.assertEqual(summary["spec"],"mage/frost")

    def test_one_mocked_native_acceptance_then_exact_cache_hit(self):
        count=[]
        def fake_simc(cmd,*,cwd,stdout,stderr,timeout,check):
            count.append(cmd)
            self.assertEqual(cmd[0],str(self.binary.resolve()))
            source=pathlib.Path(cmd[1]).read_text()
            self.assertEqual(len(cmd),2)
            self.assertNotIn("gear_crit_rating=",source)
            self.assertNotIn("gear_haste_rating=",source)
            self.assertIn("default_actions=1",source)
            self.assertIn("off_hand=",source)
            self.assertIn("json2=",source)
            stdout.write(b"original SimulationCraft stdout\n")
            raw={"report_version":"2.0.0","git_revision":REVISION,
                 "sim":{"players":[{"name":"target","specialization":"frost",
                   "collected_data":{"dps":{"mean":12345.0}}}]}}
            (pathlib.Path(cwd)/"physical.json").write_text(json.dumps(raw))
            return subprocess.CompletedProcess(cmd,0)
        u=user_for("mage/frost")
        with mock.patch.object(target.subprocess,"run",side_effect=fake_simc):
            first=target.run(u,self.binary,self.out,REVISION,max_new=1)
            cached=target.run(u,self.binary,self.out,REVISION,max_new=1)
        self.assertEqual(len(count),1)
        self.assertEqual(first["status"],"PASS_PHYSICAL_SIMC")
        self.assertEqual(first["new_native_calls"],1)
        self.assertEqual(cached["status"],"CACHED_VERIFIED_PHYSICAL_SIMC")
        self.assertEqual(cached["new_native_calls"],0)
        self.assertEqual(cached["native_json2"]["json2"]["dps_mean"],12345.0)
        folder=pathlib.Path(cached["output_dir"])
        self.assertIn("original SimulationCraft stdout",
                      (folder/"simc.log").read_text())
        receipt=json.loads((folder/"receipt.json").read_text())
        self.assertFalse(receipt["CHMV_optimization_completed"])
        self.assertFalse(receipt["APL_proc_4pc_effect_certified"])
        self.assertEqual(receipt["identity"]["simc_binary_sha256"],
                         target.sha(self.binary.read_bytes()))

    def test_real_simc_failure_is_preserved_without_retry_or_success_claim(self):
        def failed(cmd,*,cwd,stdout,stderr,timeout,check):
            stdout.write(b"SimulationCraft Error: unknown option test\n")
            return subprocess.CompletedProcess(cmd,2)
        u=user_for("warrior/fury")
        with mock.patch.object(target.subprocess,"run",side_effect=failed) as proc:
            first=target.run(u,self.binary,self.out,REVISION,max_new=1)
            again=target.run(u,self.binary,self.out,REVISION,max_new=1)
            self.assertEqual(proc.call_count,1)
        self.assertEqual(first["status"],"FAIL_NATIVE_EXIT")
        self.assertEqual(again["status"],"PRIOR_FAILURE_RETAINED")
        self.assertEqual(again["new_native_calls"],0)
        folder=pathlib.Path(first["output_dir"])
        self.assertEqual((folder/"simc.log").read_bytes(),
                         b"SimulationCraft Error: unknown option test\n")
        self.assertEqual(json.loads((folder/"receipt.json").read_text())
                         ["native_returncode"],2)

    def test_json2_wrong_simc_revision_cannot_certify_profile(self):
        def wrong_revision(cmd,*,cwd,stdout,stderr,timeout,check):
            (pathlib.Path(cwd)/"physical.json").write_text(json.dumps({
                "report_version":"2.0.0","git_revision":"0000000000",
                "sim":{"players":[{"collected_data":{
                    "dps":{"mean":25000.0}}}]}}))
            return subprocess.CompletedProcess(cmd,0)
        with mock.patch.object(target.subprocess,"run",side_effect=wrong_revision):
            result=target.run(user_for("mage/frost"),self.binary,
                              self.out,REVISION,max_new=1)
        self.assertEqual(result["status"],"FAIL_NATIVE_JSON2_OR_EXEC")
        record=json.loads((pathlib.Path(result["output_dir"])/"receipt.json").read_text())
        self.assertIn("REVISION_MISMATCH",record["error"])
        self.assertFalse(record["user_optimizer_ready"])

    def test_tampered_json2_and_altered_binary_rejected_no_simc(self):
        def okay(cmd,*,cwd,stdout,stderr,timeout,check):
            (pathlib.Path(cwd)/"physical.json").write_text(json.dumps({
                "report_version":"2.0.0","git_revision":REVISION,
                "sim":{"players":[{"collected_data":{
                    "dps":{"mean":1000.0}}}]}}))
            return subprocess.CompletedProcess(cmd,0)
        u=user_for("mage/frost")
        with mock.patch.object(target.subprocess,"run",side_effect=okay):
            report=target.run(u,self.binary,self.out,REVISION,max_new=1)
        folder=pathlib.Path(report["output_dir"])
        (folder/"physical.json").write_text('{"tampered":true}')
        with mock.patch.object(target.subprocess,"run") as no_simc:
            with self.assertRaisesRegex(target.TargetedSmokeBlocked,
                                        "CACHED_JSON2_DRIFT"):
                target.run(u,self.binary,self.out,REVISION,max_new=1)
            no_simc.assert_not_called()
        (folder/"physical.json").write_text(json.dumps({
            "report_version":"2.0.0","git_revision":REVISION,
            "sim":{"players":[{"collected_data":{"dps":{"mean":1000.0}}}]}}))
        self.binary.write_bytes(b"CHANGED_BINARY_IDENTITY")
        with mock.patch.object(target.subprocess,"run") as no_simc:
            with self.assertRaisesRegex(Exception,"DRIFT|CHANGED"):
                target.run(u,self.binary,self.out,REVISION,max_new=1)
            no_simc.assert_not_called()

    def test_existing_os_lock_prevents_concurrent_identical_native_attempt(self):
        u=user_for("mage/frost")
        key=target.user_key(u)
        folder=self.out/(key.replace("/","__")+"__"+
                         target.sha(target.canonical(u).encode("utf8"))[:16])
        with target.session_controls.worker_lock(folder):
            with mock.patch.object(target.subprocess,"run") as native:
                with self.assertRaisesRegex(
                    target.session_controls.SessionBlocked,
                    "V106_SAME_SESSION_ALREADY_RUNNING"):
                    target.run(u,self.binary,self.out,REVISION,max_new=1)
                native.assert_not_called()
        # Lock file remains as audit marker but is no longer locked.
        with mock.patch.object(target.subprocess,"run") as native:
            prepared=target.run(u,self.binary,self.out,REVISION,max_new=0)
            native.assert_not_called()
        self.assertEqual(prepared["status"],"PREPARED_NO_NATIVE")
        self.assertTrue((folder/"V106_WORKER.lock").exists())

    def test_unverified_spec_can_not_be_silently_promoted_or_oiled(self):
        u=user_for("druid/balance")
        with self.assertRaisesRegex(target.TargetedSmokeBlocked,
                                    "ALREADY_NATIVE_WITNESSED"):
            target.run(u,self.binary,self.out,REVISION,max_new=0)
        u=user_for("rogue/subtlety")
        u["oil_hands"]=["main_hand"]
        with self.assertRaisesRegex(target.TargetedSmokeBlocked,
                                    "PHYSICAL_ONLY_NEEDS"):
            target.run(u,self.binary,self.out,REVISION,max_new=0)
        u=user_for("rogue/subtlety")
        u["target"]["final_T"]=4000
        with self.assertRaisesRegex(target.TargetedSmokeBlocked,
                                    "PHYSICAL_ONLY_NEEDS"):
            target.run(u,self.binary,self.out,REVISION,max_new=0)
        self.assertFalse(self.out.exists())

class SourceFirstCurrentSeasonPhysicalOptIn(unittest.TestCase):
    """One real current gear stage in its own receipt namespace; zero Native."""

    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=pathlib.Path(tmp.name)
        self.binary=self.root/"fake_simc"
        self.binary.write_bytes(b"NO_REAL_SIMC")
        self.out=self.root/"runs"

    def test_current_season_plan_and_old_v145_receipt_namespace_are_disjoint(self):
        u=user_for("mage/frost")
        with mock.patch.object(target.subprocess,"run") as native:
            old=target.run(u,self.binary,self.out,REVISION,max_new=0)
            new=target.run(u,self.binary,self.out,REVISION,max_new=0,
                           source_first_stage=True)
            native.assert_not_called()
        self.assertEqual(old["status"],"PREPARED_NO_NATIVE")
        self.assertEqual(new["status"],"PREPARED_NO_NATIVE")
        self.assertEqual(old["new_native_calls"],0)
        self.assertEqual(new["new_native_calls"],0)
        self.assertNotEqual(old["output_dir"],new["output_dir"])
        self.assertIn("__source_first_v172__",new["output_dir"])
        first=pathlib.Path(old["output_dir"])
        second=pathlib.Path(new["output_dir"])
        a=(first/"stage"/"profile.simc").read_bytes()
        b=(second/"stage"/"profile.simc").read_bytes()
        self.assertNotEqual(a,b)
        self.assertEqual((first/"stage"/"profile.simc").read_bytes(),a)
        self.assertIs(json.loads((second/"stage"/"manifest.json").read_text())
                      [bootstrap.entry.STAGE_FIELD],True)
        self.assertFalse((second/"receipt.json").exists())
        self.assertFalse((second/"physical.simc").exists())
        self.assertFalse((second/"physical.json").exists())

    def test_current_source_first_case_can_differ_from_old_two_verified_specs(self):
        u=user_for("druid/balance")
        u["character"]["race"]="night_elf"
        with mock.patch.object(target.subprocess,"run") as native:
            with self.assertRaisesRegex(target.TargetedSmokeBlocked,
                                        "ALREADY_NATIVE_WITNESSED"):
                target.run(u,self.binary,self.out,REVISION,max_new=0)
            new=target.run(u,self.binary,self.out,REVISION,max_new=0,
                           source_first_stage=True)
            native.assert_not_called()
        self.assertEqual(new["status"],"PREPARED_NO_NATIVE")
        self.assertIn("__source_first_v172__",new["output_dir"])

    def test_current_season_one_mocked_native_and_hash_checked_reuse(self):
        called=[]
        def fake(cmd,*,cwd,stdout,stderr,timeout,check):
            called.append(cmd)
            raw=pathlib.Path(cmd[1]).read_text()
            self.assertNotIn("gear_crit_rating=",raw)
            self.assertIn("default_actions=1",raw)
            self.assertIn("json2=",raw)
            stdout.write(b"SimC synthetic one-shot stdout\n")
            (pathlib.Path(cwd)/"physical.json").write_text(json.dumps({
              "report_version":"2.0.0","git_revision":REVISION,
              "sim":{"players":[{"name":"target",
                     "collected_data":{"dps":{"mean":10123.0}}}]}}))
            return subprocess.CompletedProcess(cmd,0)
        u=user_for("mage/frost")
        with mock.patch.object(target.subprocess,"run",side_effect=fake):
            first=target.run(u,self.binary,self.out,REVISION,max_new=1,
                             source_first_stage=True)
            again=target.run(u,self.binary,self.out,REVISION,max_new=1,
                             source_first_stage=True)
        self.assertEqual(len(called),1)
        self.assertEqual(first["status"],"PASS_PHYSICAL_SIMC")
        self.assertEqual(again["status"],"CACHED_VERIFIED_PHYSICAL_SIMC")
        self.assertEqual(again["new_native_calls"],0)
        receipt=json.loads((pathlib.Path(first["output_dir"])/"receipt.json").read_text())
        self.assertIs(receipt["identity"]["source_first_current_season_stage"],True)
        self.assertEqual(len(receipt["identity"]["current_season_gear_snapshot_sha256"]),64)
        self.assertEqual(len(receipt["identity"]["current_season_tier_snapshot_sha256"]),64)
        self.assertIs(receipt["CHMV_optimization_completed"],False)
        self.assertIs(receipt["APL_proc_4pc_effect_certified"],False)


if __name__=="__main__":
    unittest.main()
