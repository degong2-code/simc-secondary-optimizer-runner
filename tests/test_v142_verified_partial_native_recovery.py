"""Recover exactly one previously written Native result without a second SimC.

Offline test. The returned data in success cases is mocked; this does NOT
establish actual rating/DPS, which is verified by v064 in the live pipeline.
"""
from __future__ import annotations
import hashlib,json,pathlib,sys,tempfile,unittest
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v065_original_scheduler_native_bridge as bridge

class PhysicalNativePartialRecovery(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root=pathlib.Path(temp.name)/"seed_00"
        self.root.mkdir(parents=True)
        self.source="druid=trial\\niterations=35\\n"
        self.input=self.root/"input.simc"
        self.input.write_bytes(self.source.encode("utf8"))
        self.native=self.root/"result.json"
        self.document={"report_version":"2.0.0","git_revision":"7bc1071",
                       "sim":{"options":{"seed":42},"players":[{}]}}
        self.native.write_bytes(json.dumps(self.document).encode("utf8"))
        self.req={"input":self.source,
                  "input_sha256":hashlib.sha256(self.source.encode()).hexdigest(),
                  "json2_location":str(self.native)}
        self.calib={"native_revision":"7bc10711b5"}
        self.verified={"status":"PASS_NATIVE_DPS_AND_STATIC_CHMV_INPUT",
                       "case_key":"offline_case","native_revision":"7bc10711b5"}

    def call(self,enabled):
        return bridge.execute_one(
            self.req,self.calib,self.root/"fake_simc.exe",self.root,
            {"native_attempts":1},recover_verified_partial=enabled)

    def test_default_partial_still_blocks_unchanged(self):
        with mock.patch.object(bridge.evaluator,"ingest_native") as evaluate,\
             mock.patch.object(bridge.subprocess,"run") as exe:
            with self.assertRaisesRegex(bridge.PipelineBlocked,
                  "PARTIAL_NATIVE_OUTPUT_REQUIRES_EXPLICIT_RECOVERY"):
                self.call(False)
            evaluate.assert_not_called()
            exe.assert_not_called()
        self.assertFalse((self.root/"native_receipt.json").exists())

    def test_receipt_authorized_recovery_validates_original_json_and_no_native(self):
        with mock.patch.object(bridge.evaluator,"ingest_native",
                               return_value=self.verified) as evaluate,\
             mock.patch.object(bridge.subprocess,"run") as exe:
            result=self.call(True)
            evaluate.assert_called_once()
            exe.assert_not_called()
        self.assertEqual(result["source"],"CACHED_VERIFIED_NATIVE")
        self.assertTrue(result["recovered_partial_validated_without_native"])
        receipt=json.loads((self.root/"native_receipt.json").read_text())
        self.assertEqual(receipt["simc_seed"],42)
        self.assertEqual(receipt["native_revision"],"7bc10711b5")
        self.assertEqual(json.loads(self.native.read_text()),self.document)
        # Next pass is the unchanged ordinary cache validator, not recovery.
        with mock.patch.object(bridge.evaluator,"verify_disk_cache",
                               return_value=self.verified) as valid,\
             mock.patch.object(bridge.subprocess,"run") as exe:
            again=self.call(False)
            valid.assert_called_once()
            exe.assert_not_called()
        self.assertEqual(again["source"],"CACHED_VERIFIED_NATIVE")

    def test_modified_existing_input_refused_even_when_opted_in(self):
        self.input.write_bytes(b"CHANGED!")
        with mock.patch.object(bridge.evaluator,"ingest_native") as evaluate,\
             mock.patch.object(bridge.subprocess,"run") as exe:
            with self.assertRaisesRegex(bridge.PipelineBlocked,
                                        "PARTIAL_NATIVE_INPUT_IDENTITY_MISMATCH"):
                self.call(True)
            evaluate.assert_not_called()
            exe.assert_not_called()
        self.assertFalse((self.root/"native_receipt.json").exists())

    def test_invalid_partial_json_remains_unreceipted(self):
        self.native.write_bytes(b"{bad json")
        with mock.patch.object(bridge.evaluator,"ingest_native") as evaluate,\
             mock.patch.object(bridge.subprocess,"run") as exe:
            with self.assertRaises(json.JSONDecodeError):
                self.call(True)
            evaluate.assert_not_called()
            exe.assert_not_called()
        self.assertFalse((self.root/"native_receipt.json").exists())

    def test_existing_validator_rejection_cannot_be_recategorized_as_cache(self):
        with mock.patch.object(bridge.evaluator,"ingest_native",
                      side_effect=ValueError("NATIVE_RATING_OR_REVISION_DRIFT")) as evaluate,\
             mock.patch.object(bridge.subprocess,"run") as exe:
            with self.assertRaisesRegex(ValueError,
                                        "NATIVE_RATING_OR_REVISION_DRIFT"):
                self.call(True)
            evaluate.assert_called_once()
            exe.assert_not_called()
        self.assertFalse((self.root/"native_receipt.json").exists())

if __name__=="__main__":
    unittest.main()
