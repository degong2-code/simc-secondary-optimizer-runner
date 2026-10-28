"""Existing v140 physical receipts unlock ONLY exact source-free pilot profiles.

Every SimC call in this test is mocked. No new Native execution or readiness
claim; the real user Windows v140 2/2 receipt is historical context.
"""
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
sys.path.insert(0,str(ROOT/"runner"))
sys.path.insert(0,str(ROOT/"integration_probes"))
import v098_target_user_scenario_bootstrap as bootstrap
import v140_pure_profile_physical_native_smoke as physical
import v141_verified_pure_native_pilot as pilot

class ExactReceiptReuseTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=pathlib.Path(tmp.name)
        self.binary=self.root/"simc.exe"
        self.binary.write_bytes(b"OFFLINE_FAKE_SIMC_NOT_NATIVE")
        self.revision="7bc10711b5"
        self.witness=self.root/"v140_output"

    def fake_native(self,cmd,*,cwd,stdout,stderr,timeout,check):
        path=pathlib.Path(cwd)
        (path/"physical.json").write_text(
            json.dumps({"report_version":"2.0.0",
                        "sim":{"players":[{
                             "name":"fake_only",
                             "collected_data":{"dps":{"mean":1.0}}}]} }),
            encoding="utf8")
        return subprocess.CompletedProcess(cmd,0,b"MOCK ONLY")

    def accepted(self):
        with mock.patch.object(physical.subprocess,"run",
                               side_effect=self.fake_native) as native:
            report=physical.run(self.binary,self.witness,revision=self.revision,
                                iterations=1,max_new=2)
        self.assertEqual(native.call_count,2)
        self.assertTrue(report["all_pass"])
        self.assertEqual(report["new_native_calls"],2)

    def userfile(self,key,change=None):
        user=physical.user_for(key)
        if change:change(user)
        path=self.root/("user_"+key.replace("/","_")+
                        ("_changed" if change else "")+".json")
        path.write_text(bootstrap.canonical(user)+"\n",encoding="utf8")
        return path

    def test_prior_receipt_reused_for_exact_two_specs_with_no_new_physical_native(self):
        self.accepted()
        for key in physical.ACTORS:
            with self.subTest(key=key):
                source=self.userfile(key)
                output=self.root/("run_"+key.replace("/","_"))
                fake={"status":"PASS_MOCK_ONLY",
                      "new_native_attempts_cumulative":0,
                      "verified_cache_hits_this_run":0,
                      "B":3000,"official_final_T":3000}
                with mock.patch.object(bootstrap.entry.durable,"run",
                                       return_value=fake) as existing,\
                     mock.patch.object(bootstrap.entry,"user_facing_result",
                                       return_value={"mock":True}):
                    result=bootstrap.run(
                        source,output,self.binary,self.revision,
                        execute=True,pure_stage=True,
                        physical_acceptance_root=self.witness)
                self.assertEqual(existing.call_count,1)
                self.assertEqual(result["native_result"]["status"],
                                 "PASS_MOCK_ONLY")
                provenance=result["native_result"]["internal_pure_physical_acceptance"]
                self.assertEqual(provenance["spec"],key)
                self.assertTrue(provenance["physical_native_already_executed"])
                self.assertFalse(provenance["full_chmv_optimization_completed"])
                self.assertEqual(provenance["new_native_calls"],0)
                manifest=json.loads((output/"manifest.json").read_text())
                self.assertTrue(manifest[bootstrap.entry.STAGE_FIELD])

    def test_direct_v096_and_v098_execution_without_witness_remain_blocked(self):
        self.accepted()
        source=self.userfile("druid/balance")
        folder=self.root/"unverified"
        stage=bootstrap.build(json.loads(source.read_text()),folder,
                              self.binary,self.revision,pure_stage=True)
        with mock.patch.object(bootstrap.entry.durable,"run") as native:
            with self.assertRaisesRegex(bootstrap.entry.EntryBlocked,
                                       "UNVERIFIED_PURE_PROFILE_NATIVE_EXECUTION_BLOCKED"):
                bootstrap.entry.run_manifest(stage["generated_manifest"])
            with self.assertRaisesRegex(bootstrap.UserScenarioBlocked,
                                       "PURE_STAGE_NATIVE_NOT_AUTHORIZED"):
                bootstrap.run(source,self.root/"refused",self.binary,self.revision,
                              execute=True,pure_stage=True)
            native.assert_not_called()

    def test_changed_trinket_or_talent_cannot_borrow_prior_physical_receipt(self):
        self.accepted()
        for key,change in (
            ("druid/balance",lambda u:u["trinkets"][0].update(item_id=250224)),
            ("evoker/devastation",lambda u:u["character"].update(talents="CAAAABBB11122"))):
            with self.subTest(key=key):
                source=self.userfile(key,change)
                with mock.patch.object(bootstrap.entry.durable,"run") as native:
                    with self.assertRaisesRegex(pilot.AcceptanceBlocked,
                                               "STAGED_PROFILE_BYTES_CHANGED"):
                        bootstrap.run(source,self.root/("changed_"+key.split("/")[0]),
                            self.binary,self.revision,execute=True,pure_stage=True,
                            physical_acceptance_root=self.witness)
                    native.assert_not_called()

    def test_changed_binary_revision_or_json2_fails_before_existing_native(self):
        self.accepted()
        key="druid/balance"
        source=self.userfile(key)
        path=self.witness/"druid__balance"/"physical.json"
        path.write_text('{"sim":{"players":[]}}',encoding="utf8")
        with mock.patch.object(bootstrap.entry.durable,"run") as native:
            with self.assertRaisesRegex(pilot.AcceptanceBlocked,
                                       "PHYSICAL_NATIVE_JSON2_SHA256_DRIFT"):
                bootstrap.run(source,self.root/"json_changed",self.binary,
                    self.revision,execute=True,pure_stage=True,
                    physical_acceptance_root=self.witness)
            native.assert_not_called()
        self.assertEqual(self.binary.read_bytes(),b"OFFLINE_FAKE_SIMC_NOT_NATIVE")
        self.binary.write_bytes(b"CHANGED_FAKE_SIMC")
        with mock.patch.object(bootstrap.entry.durable,"run") as native:
            with self.assertRaisesRegex(pilot.AcceptanceBlocked,
                                       "PHYSICAL_BINARY_SHA256_CHANGED"):
                bootstrap.run(source,self.root/"binary_changed",self.binary,
                    self.revision,execute=True,pure_stage=True,
                    physical_acceptance_root=self.witness)
            native.assert_not_called()

    def test_different_revision_is_not_authorized_by_same_physical_receipt(self):
        self.accepted()
        source=self.userfile("druid/balance")
        with mock.patch.object(bootstrap.entry.durable,"run") as native:
            with self.assertRaisesRegex(pilot.AcceptanceBlocked,
                                        "RECEIPT_IDENTITY_OR_REVISION_DRIFT"):
                bootstrap.run(source,self.root/"revision_changed",self.binary,
                    "another_revision123",execute=True,pure_stage=True,
                    physical_acceptance_root=self.witness)
            native.assert_not_called()

    def test_unrelated_default_profile_rejects_physical_root(self):
        source=self.userfile("druid/balance")
        with self.assertRaisesRegex(bootstrap.UserScenarioBlocked,
                                    "PURE_PHYSICAL_ACCEPTANCE_NOT_FOR_SOURCE_PROFILES"):
            bootstrap.run(source,self.root/"normal",self.binary,self.revision,
                pure_stage=False,physical_acceptance_root=self.witness)

if __name__=="__main__":
    unittest.main()
