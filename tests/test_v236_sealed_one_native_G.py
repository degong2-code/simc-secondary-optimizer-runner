"""v236 sealed source actual profile runner: synthetic Native only in tests."""
from __future__ import annotations
import hashlib
import json
import pathlib
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from runner import v236_sealed_one_native_G as engine
from tests.test_v233_v234_source_native_G import SinglePhysicalNativeTests


class SealedNativeSourceTests(unittest.TestCase):
    def setUp(self):
        self.fixture=SinglePhysicalNativeTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.fixture.temp.cleanup)
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        self.pin_fixture_for_pinned_binary()
        self.profile=self.root/"sealed.simc"
        self.profile.write_bytes(self.fixture.text.encode("utf8"))
        self.receipt=self.root/"sealed.json"
        self.receipt.write_text(json.dumps(self.fixture.prepared),encoding="utf8")
        self.exe=self.root/"simc_fake"
        self.exe.write_bytes(b"fake simc binary must not be launched unmocked")
        self.binarysha=hashlib.sha256(self.exe.read_bytes()).hexdigest()

    def pin_fixture_for_pinned_binary(self):
        from runner import v229_simc_only_source_seed as source
        r=self.fixture.prepared
        r["simc_revision"]="710c2408bfd3ae4df71b8cd55cdf01f63fd6c926"
        r["game_build_declared_by_simc_source"]="12.1.5.70575"
        r["receipt_sha256"]=source.digest(source.canonical(
            {k:v for k,v in r.items() if k!="receipt_sha256"}).encode("utf8"))

    def run_one(self, *, max_new=0,output="out"):
        return engine.run(profile_path=self.profile,receipt_path=self.receipt,
                          binary=self.exe,binary_sha256=self.binarysha,
                          expected_source_revision="710c2408bfd3ae4df71b8cd55cdf01f63fd6c926",
                          expected_game_build="12.1.5.70575",
                          output_dir=self.root/output,max_new=max_new)

    def test_omitted_level_is_byte_sealed_and_not_a_native_gate(self):
        # The chosen compiled SimC MAX_LEVEL owns the level; the sealed
        # profile has no explicit level assignment and cannot drift.
        self.fixture.text,self.fixture.prepared=engine.compiler.build(
            source_directory=self.fixture.folder,
            tier_candidate=self.fixture.tier,
            representative_candidate=self.fixture.representative,
            race=self.fixture.race,level=None,talents=None)
        self.pin_fixture_for_pinned_binary()
        self.profile.write_bytes(self.fixture.text.encode("utf8"))
        self.receipt.write_text(json.dumps(self.fixture.prepared),
                                encoding="utf8")
        self.assertFalse(any(x.startswith("level=")
                             for x in self.fixture.text.splitlines()))
        self.assertEqual(self.fixture.prepared["level_mode"],
                         "SIMC_COMPILED_MAX_LEVEL")
        with patch.object(engine.subprocess,"run") as native_call:
            result=self.run_one(max_new=0)
        native_call.assert_not_called()
        self.assertEqual(result["status"],"PREPARED_NOT_EXECUTED")
        self.assertEqual(result["new_native_calls"],0)
        self.assertFalse(result["environment_ready"])
        self.assertIsNone(result["G"])

    def test_preflight_zero_native_and_no_repeated_output(self):
        with patch.object(engine.subprocess,"run") as runner:
            result=self.run_one()
            runner.assert_not_called()
        self.assertEqual(result["new_native_calls"],0)
        self.assertEqual(result["status"],"PREPARED_NOT_EXECUTED")
        self.assertIsNone(result["G"])
        self.assertFalse(result["environment_ready"])
        with self.assertRaisesRegex(engine.SealedNativeBlocked,
                                    "NEW_OUTPUT_REQUIRED"):
            self.run_one()

    def test_one_real_subprocess_call_is_mocked_and_source_hash_bound(self):
        events=[]
        def callback(cmd,*,cwd,stdout,stderr,check,timeout):
            events.append(cmd)
            contents=pathlib.Path(cmd[1]).read_text(encoding="utf8")
            self.assertIn("json2=",contents)
            self.assertEqual(contents.count("source=local"),13)
            (pathlib.Path(cwd)/"native.json").write_text(
                json.dumps(self.fixture._fake_json2()),encoding="utf8")
            stdout.write(b"one mocked simc run")
            return SimpleNamespace(returncode=0)
        with patch.object(engine.subprocess,"run",side_effect=callback):
            result=self.run_one(max_new=1)
        self.assertEqual(len(events),1)
        self.assertEqual(result["status"],"PASS_NATIVE_OBSERVED_G_UNPROMOTED")
        self.assertEqual(result["new_native_calls"],1)
        self.assertEqual(result["observed_G"]["matching_nontrinket_G_slots"],13)
        self.assertIsNone(result["G"])
        self.assertIsNone(result["B"])
        self.assertIsNone(result["T"])
        self.assertEqual(result["native_log_sha256"],hashlib.sha256(
            b"one mocked simc run").hexdigest())

    def test_nonzero_native_failure_preserves_log_and_cannot_relaunch(self):
        def callback(cmd,*,cwd,stdout,stderr,check,timeout):
            stdout.write(b"SIMC ERROR original text: no APL\n")
            return SimpleNamespace(returncode=9)
        with patch.object(engine.subprocess,"run",side_effect=callback):
            result=self.run_one(max_new=1)
        self.assertEqual(result["status"],"FAIL_NATIVE_EXIT")
        self.assertEqual(result["returncode"],9)
        self.assertEqual(result["new_native_calls"],1)
        self.assertEqual((self.root/"out/simc.log").read_bytes(),
                         b"SIMC ERROR original text: no APL\n")
        with self.assertRaisesRegex(engine.SealedNativeBlocked,
                                    "NEW_OUTPUT_REQUIRED"):
            self.run_one(max_new=1)

    def test_profile_tamper_and_binary_tamper_are_blocked_before_process(self):
        self.profile.write_bytes(self.profile.read_bytes()+b"flask=oops\n")
        with patch.object(engine.subprocess,"run") as runner:
            with self.assertRaisesRegex(engine.SealedNativeBlocked,
                                        "PROFILE_BYTES_NOT_SEALED"):
                self.run_one(max_new=1)
            runner.assert_not_called()
        self.profile.write_bytes(self.fixture.text.encode("utf8"))
        self.exe.write_bytes(b"new executable bytes")
        with self.assertRaisesRegex(engine.SealedNativeBlocked,
                                    "EXECUTABLE_SHA256_MISMATCH"):
            self.run_one(max_new=1)

    def test_receipt_can_not_forge_revision_or_equipment_even_with_rehashed_receipt(self):
        r=json.loads(self.receipt.read_text())
        r["selected_G_slot_ids"]["head"]=99999
        from runner import v229_simc_only_source_seed as source
        r["receipt_sha256"]=source.digest(source.canonical(
            {k:v for k,v in r.items() if k!="receipt_sha256"}).encode("utf8"))
        self.receipt.write_text(json.dumps(r))
        with self.assertRaisesRegex(engine.SealedNativeBlocked,
                                    "SOURCE_EQUIPMENT_OR_OVERRIDES_CHANGED"):
            self.run_one()
        r["simc_revision"]="b"*40
        r["receipt_sha256"]=source.digest(source.canonical(
            {k:v for k,v in r.items() if k!="receipt_sha256"}).encode("utf8"))
        self.receipt.write_text(json.dumps(r))
        with self.assertRaises(engine.SealedNativeBlocked):
            self.run_one()

    def test_explicit_revision_and_build_pin_mismatch_blocks_before_native(self):
        packed=json.loads(self.receipt.read_text())
        with self.assertRaisesRegex(engine.SealedNativeBlocked,
                                    "SOURCE_REVISION_OR_GAME_BUILD_NOT_PINNED"):
            engine.check(self.profile.read_bytes(),packed,
                expected_source_revision="b"*40,
                expected_game_build="12.1.5.70575")
        with self.assertRaisesRegex(engine.SealedNativeBlocked,
                                    "SOURCE_REVISION_OR_GAME_BUILD_NOT_PINNED"):
            engine.check(self.profile.read_bytes(),packed,
                expected_source_revision="710c2408bfd3ae4df71b8cd55cdf01f63fd6c926",
                expected_game_build="12.2.0.99999")
        with self.assertRaisesRegex(engine.SealedNativeBlocked,
                                    "EXPLICIT_IMMUTABLE_SOURCE_PIN_REQUIRED"):
            engine.check(self.profile.read_bytes(),packed,
                expected_source_revision="latest",
                expected_game_build="12.1.5.70575")

    def test_fourteen_source_slots_fury(self):
        from tests.test_v232_simc_only_ordinary_representative import make_fixture
        self.fixture.fixture.seed_files(make_fixture(warrior=True),
                                        cls="warrior",spec="fury")
        self.fixture.tier=self.fixture.fixture.tier
        self.fixture.representative=self.fixture.fixture.plan()
        self.fixture._profile()
        self.pin_fixture_for_pinned_binary()
        self.profile.write_bytes(self.fixture.text.encode("utf8"))
        self.receipt.write_text(json.dumps(self.fixture.prepared))
        doc=json.loads(self.receipt.read_text())
        self.assertEqual(len(doc["selected_G_slot_ids"]),14)
        engine.check(self.profile.read_bytes(),doc,
                     expected_source_revision="710c2408bfd3ae4df71b8cd55cdf01f63fd6c926",
                     expected_game_build="12.1.5.70575")
        self.assertIn("off_hand=",self.profile.read_text())


if __name__=="__main__":
    unittest.main()
