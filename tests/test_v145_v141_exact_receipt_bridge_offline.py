"""Exact one-spec v145 physical receipt -> existing v096/v094 adapter, OFFLINE.

SimC subprocess and adaptive Native runner are fully mocked. Verifies proof
identity, negative provenance cases, and unchanged legacy routing. This is
not an actual SimC physical or DPS acceptance result.
"""
from __future__ import annotations
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
import v141_verified_pure_native_pilot as verifier
import v145_targeted_pure_physical_native as diagnostic
from tests.test_v145_targeted_pure_physical_native_offline import user_for

REVISION="7bc10711b5"

class ExactV145ReceiptBridge(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=pathlib.Path(tmp.name)
        self.binary=self.root/"fake_simc.exe"
        self.binary.write_bytes(b"FAKE_OFFLINE_ONLY")
        self.user=user_for("mage/frost")
        self.physical_root=self.root/"native_physical"
        self.user_path=self.root/"user.json"
        self.user_path.write_text(bootstrap.canonical(self.user)+"\n",
                                  encoding="utf8")
        self.calls=[]
        self.blocked_serial=0

    def mocked_simc(self,cmd,*,cwd,stdout,stderr,timeout,check):
        self.calls.append(cmd)
        folder=pathlib.Path(cwd)
        (folder/"physical.json").write_text(json.dumps({
            "report_version":"2.0.0","git_revision":REVISION,
            "sim":{"players":[{"name":"frost_target",
                "specialization":"frost",
                "collected_data":{"dps":{"mean":15789.125}}}]}}),
            encoding="utf8")
        stdout.write(b"mock physical simc evidence - NOT REAL SIMC\n")
        return subprocess.CompletedProcess(cmd,0)

    def accepted_folder(self):
        with mock.patch.object(diagnostic.subprocess,"run",
                               side_effect=self.mocked_simc):
            result=diagnostic.run(self.user,self.binary,
                self.physical_root,REVISION,max_new=1)
        self.assertEqual(result["status"],"PASS_PHYSICAL_SIMC")
        self.assertEqual(len(self.calls),1)
        return pathlib.Path(result["output_dir"])

    def adaptive(self,folder,user_path=None,binary=None,revision=REVISION):
        with mock.patch.object(bootstrap.entry.durable,"run",
            return_value={"status":"MOCK_ADAPTIVE_NOT_REAL_NATIVE",
                          "new_native_attempts_cumulative":0,
                          "verified_cache_hits_this_run":0,
                          "B":3150,"official_final_T":3150}) as native, \
             mock.patch.object(bootstrap.entry,"user_facing_result",
                               return_value={"mock":True}):
            result=bootstrap.run(
                user_path or self.user_path,
                self.root/("adaptive_"+str(len(self.calls))),
                binary or self.binary,revision,execute=True,
                pure_stage=True,physical_acceptance_root=folder)
            native.assert_called_once()
        return result

    def expect_blocked(self,folder,pattern,*,user_path=None,
                       binary=None,revision=REVISION):
        self.blocked_serial+=1
        with mock.patch.object(bootstrap.entry.durable,"run") as native:
            with self.assertRaisesRegex(verifier.AcceptanceBlocked,pattern):
                bootstrap.run(
                    user_path or self.user_path,
                    self.root/("blocked_"+str(self.blocked_serial)),
                    binary or self.binary,revision,execute=True,
                    pure_stage=True,physical_acceptance_root=folder)
            native.assert_not_called()

    def test_exact_same_user_binary_profile_and_json2_reuses_one_physical(self):
        folder=self.accepted_folder()
        result=self.adaptive(folder)
        witness=result["native_result"]["internal_pure_physical_acceptance"]
        self.assertEqual(witness["spec"],"mage/frost")
        self.assertEqual(witness["new_native_calls"],0)
        self.assertEqual(witness["schema"],
              "v141_verified_reuse_of_v145_one_spec_physical_receipt_v1")
        self.assertTrue(witness["physical_native_already_executed"])
        self.assertFalse(witness["full_chmv_optimization_completed"])
        self.assertEqual(len(self.calls),1)
        self.assertEqual(result["native_result"]["status"],
                         "MOCK_ADAPTIVE_NOT_REAL_NATIVE")
        self.assertTrue(json.loads(
            (self.root/"adaptive_1"/"manifest.json").read_text())
            [bootstrap.entry.STAGE_FIELD])

    def test_no_physical_receipt_cannot_authorize_legacy_24_pure_stage(self):
        with mock.patch.object(bootstrap.entry.durable,"run") as native:
            with self.assertRaisesRegex(bootstrap.UserScenarioBlocked,
                                       "PURE_STAGE_NATIVE_NOT_AUTHORIZED"):
                bootstrap.run(self.user_path,self.root/"no_receipt",self.binary,
                              REVISION,execute=True,pure_stage=True)
            native.assert_not_called()

    def test_changed_talents_trinkets_or_combat_never_borrow_physical_receipt(self):
        folder=self.accepted_folder()
        variants=(
            ("talents",lambda u:u["character"].update(talents="CAAAABBB11123")),
            ("trinket",lambda u:u["trinkets"][0].update(item_id=250224)),
            ("combat",lambda u:u["combat"].update(targets=2)))
        for index,(label,change) in enumerate(variants):
            with self.subTest(label=label):
                u=json.loads(json.dumps(self.user))
                change(u)
                path=self.root/("changed_%02d.json"%index)
                path.write_text(bootstrap.canonical(u)+"\n")
                self.expect_blocked(folder,"V145_STAGED_PROFILE_BYTES_CHANGED",
                                    user_path=path)
        self.assertEqual(len(self.calls),1)

    def test_tampered_receipt_json2_revision_and_physical_profile_block(self):
        folder=self.accepted_folder()
        receipt_path=folder/"receipt.json"
        original=receipt_path.read_bytes()
        receipt=json.loads(original)
        receipt["status"]="FAIL_NATIVE_EXIT"
        receipt_path.write_text(json.dumps(receipt))
        self.expect_blocked(folder,"V145_NATIVE_PHYSICAL_RECEIPT_NOT_PASS")
        receipt_path.write_bytes(original)
        raw=(folder/"physical.json").read_bytes()
        (folder/"physical.json").write_text('{"tampered":true}')
        self.expect_blocked(folder,"V145_JSON2_SHA256_DRIFT")
        (folder/"physical.json").write_bytes(raw)
        physical=(folder/"physical.simc").read_bytes()
        (folder/"physical.simc").write_bytes(physical+b"# mutated\n")
        self.expect_blocked(folder,"V145_PHYSICAL_SIMC_BYTES_DRIFT")
        (folder/"physical.simc").write_bytes(physical)

    def test_changed_binary_and_revision_refused(self):
        folder=self.accepted_folder()
        other=self.root/"altered.exe"
        other.write_bytes(b"OTHER_BINARY_NOT_SIMC")
        self.expect_blocked(folder,"V145_EXACT_BINARY_REVISION_OR_OPTIONS_DRIFT",
                            binary=other)
        self.expect_blocked(folder,"V145_EXACT_BINARY_REVISION_OR_OPTIONS_DRIFT",
                            revision="deadbeef")
        self.assertEqual(len(self.calls),1)

    def test_witness_requires_exact_output_folder_not_parent_or_other_spec(self):
        folder=self.accepted_folder()
        self.expect_blocked(self.physical_root,
            "V145_EXACT_PHYSICAL_RECEIPT_FILES_REQUIRED")
        u=user_for("warrior/fury")
        path=self.root/"fury.json"
        path.write_text(bootstrap.canonical(u)+"\n")
        self.expect_blocked(folder,"V145_NATIVE_PHYSICAL_RECEIPT_NOT_PASS",
                            user_path=path)
        self.assertEqual(len(self.calls),1)

    def test_v140_historical_two_spec_contract_remains_unchanged(self):
        user={"class":"druid","spec":"balance","race":"night_elf",
              "talents":"CAAAABBB11122"}
        self.assertIn(("druid","balance"),bootstrap.PURE_PRODUCT_SPECS)
        with self.assertRaisesRegex(verifier.AcceptanceBlocked,
                                    "VERIFIED_PHYSICAL_RECEIPT_FILES_REQUIRED"):
            verifier.verify("druid=target\n",
                diagnostic.sha(self.binary.read_bytes()),REVISION,
                "druid/balance",self.root/"nonexistent")
        self.assertNotIn(("mage","frost"),bootstrap.PURE_PRODUCT_SPECS)

if __name__=="__main__":
    unittest.main()
