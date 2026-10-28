"""No SimC executed here. Verify bounded Native pilot inputs/caching with mocks."""
from __future__ import annotations
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"integration_probes"))
import v140_pure_profile_physical_native_smoke as v140

class PurePhysicalPilotOffline(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=pathlib.Path(self.temp.name)
        self.binary=self.root/"fake_simc.exe"
        self.binary.write_bytes(b"NOT_AN_ACTUAL_SIMC_BINARY")
        self.out=self.root/"results"

    def test_source_free_pilot_uses_real_talent_example_input_not_fake_unit_test_code(self):
        self.assertEqual(set(v140.ACTORS),
                         {"druid/balance","evoker/devastation"})
        for key in v140.ACTORS:
            actor=v140.user_for(key)
            self.assertGreater(len(actor["character"]["talents"]),60)
            self.assertEqual(actor["target"]["ilevel"],334)
            self.assertEqual(len(actor["trinkets"]),2)
            self.assertEqual(actor["oil_hands"],[])
            self.assertFalse(actor["special_items"])

    def test_bounded_plan_and_physical_input_keep_items_but_remove_gear_override(self):
        with mock.patch.object(v140.subprocess,"run") as runner:
            out=v140.run(self.binary,self.out,revision="7bc10711b5",
                         max_new=0,iterations=1)
            runner.assert_not_called()
        self.assertEqual(out["new_native_calls"],0)
        self.assertFalse(out["all_pass"])
        self.assertEqual(len(out["cases"]),2)
        self.assertTrue(all(x["status"]=="NOT_RUN_NEW_CALL_LIMIT"
                            for x in out["cases"]))
        for key in v140.ACTORS:
            root=self.out/key.replace("/","__")
            stage=(root/"stage"/"profile.simc").read_text(encoding="utf8")
            physical=(root/"physical.simc").read_text(encoding="utf8")
            self.assertIn("gear_crit_rating=",stage)
            self.assertNotIn("gear_crit_rating=",physical)
            self.assertNotIn("gear_haste_rating=",physical)
            self.assertNotIn("gear_mastery_rating=",physical)
            self.assertNotIn("gear_versatility_rating=",physical)
            self.assertIn("json2="+str((root/"physical.json").resolve()),physical)
            self.assertIn("iterations=1",physical)
            self.assertEqual(
                [s for s in stage.splitlines() if s.startswith("head=")],
                [s for s in physical.splitlines() if s.startswith("head=")])
            self.assertEqual(
                [s for s in stage.splitlines() if s.startswith("main_hand=")],
                [s for s in physical.splitlines() if s.startswith("main_hand=")])
            self.assertIn("default_actions=1",physical)
            self.assertNotIn("load_default_gear=1",physical)

    def test_only_two_new_mocked_native_calls_then_identity_verified_cache(self):
        calls=[]
        def fake_process(cmd,*,cwd,stdout,stderr,timeout,check):
            self.assertEqual(cmd[0],str(self.binary.resolve()))
            self.assertEqual(len(cmd),2)
            self.assertTrue(pathlib.Path(cmd[1]).exists())
            self.assertTrue(pathlib.Path(cwd).is_dir())
            calls.append(cmd)
            result={"report_version":"2.0.0",
                    "sim":{"players":[{"name":"target", "specialization":"pilot",
                        "collected_data":{"dps":{"mean":1.0}}}]}}
            (pathlib.Path(cwd)/"physical.json").write_text(
                json.dumps(result),encoding="utf8")
            return subprocess.CompletedProcess(cmd,0,b"FAKE SUCCESS ONLY")
        with mock.patch.object(v140.subprocess,"run",side_effect=fake_process):
            outcome=v140.run(self.binary,self.out,revision="7bc10711b5",
                             max_new=2,iterations=1)
            self.assertEqual(len(calls),2)
            self.assertEqual(outcome["new_native_calls"],2)
            self.assertTrue(outcome["all_pass"])
            again=v140.run(self.binary,self.out,revision="7bc10711b5",
                            max_new=2,iterations=1)
            self.assertEqual(len(calls),2)
            self.assertEqual(again["new_native_calls"],0)
            self.assertTrue(again["all_pass"])
            self.assertTrue(all(x["status"]=="CACHED_VERIFIED_PHYSICAL_SIMC"
                                for x in again["cases"]))
        for key in v140.ACTORS:
            folder=self.out/key.replace("/","__")
            receipt=json.loads((folder/"receipt.json").read_text())
            self.assertEqual(receipt["status"],"PASS_PHYSICAL_SIMC")
            self.assertFalse(receipt["chmv_optimization_completed"])
            self.assertTrue(receipt["identity"]["gear_rating_override_removed"])

    def test_bad_cached_input_is_rejected_before_new_native(self):
        with mock.patch.object(v140.subprocess,"run"):
            v140.run(self.binary,self.out,revision="7bc10711b5",max_new=0)
            file=self.out/"druid__balance"/"physical.simc"
            file.write_text("TAMPER\n",encoding="utf8")
            # The fixture with max_new=0 has no receipt, so the input is
            # classified as unreceipted, not silently overwritten.
            with self.assertRaisesRegex(v140.PhysicalSmokeBlocked,
                                        "PREEXISTING_UNRECEIPTED_NATIVE_FILES"):
                v140.run(self.binary,self.out,revision="7bc10711b5",max_new=2)

if __name__=="__main__":
    unittest.main()
