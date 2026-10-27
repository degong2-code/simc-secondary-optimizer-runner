"""v136 acceptance runner: real v098 plan, bounded synthetic Native, Native0 in CI."""
from __future__ import annotations
import json,pathlib,sys,tempfile,unittest
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v136_target334_single_smoke as runner

class TargetSmoke(unittest.TestCase):
    def test_sixteen_plans_are_existing_v098_and_native_zero(self):
        with tempfile.TemporaryDirectory() as td:
            home=pathlib.Path(td)
            binary=home/"fake.exe";binary.write_bytes(b"synthetic no real Native")
            self.assertEqual(len(runner.keys()),16)
            with mock.patch.object(runner.subprocess,"run",
                                   side_effect=AssertionError("NATIVE_FORBIDDEN")):
                result=runner.run(binary,home/"output",max_new=0)
            self.assertEqual(result["new_native_calls"],0)
            self.assertEqual(len(result["cases"]),16)
            self.assertTrue(all(x["status"]=="NOT_RUN_LIMIT"
                                for x in result["cases"]))
            self.assertFalse(list((home/"output").rglob("native_input.simc")))
            self.assertFalse(list((home/"output").rglob("result.json")))

    def test_one_fake_native_and_receipt_sha_cache_without_repeat(self):
        with tempfile.TemporaryDirectory() as td:
            home=pathlib.Path(td); binary=home/"fake.exe"
            binary.write_bytes(b"NO ACTUAL SIMC")
            invoked=[]
            def fake_subprocess(argv,**kwargs):
                p=pathlib.Path(argv[1]); text=p.read_text("utf8")
                json2=next(x.split("=",1)[1] for x in text.splitlines()
                           if x.startswith("json2="))
                pathlib.Path(json2).write_text(json.dumps(
                    {"sim":{"players":[{"name":"synthetic"}]}}),encoding="utf8")
                invoked.append(p)
                class R: returncode=0; stdout=b"fake"
                return R()
            with mock.patch.object(runner.subprocess,"run",side_effect=fake_subprocess):
                first=runner.run(binary,home/"out",max_new=1)
                self.assertEqual(first["new_native_calls"],1)
                self.assertEqual(first["cases"][0]["status"],"PASS_NATIVE_SMOKE")
                second=runner.run(binary,home/"out",max_new=0)
                self.assertEqual(second["new_native_calls"],0)
                self.assertEqual(second["cases"][0]["status"],"CACHED_VERIFIED_NATIVE")
            self.assertEqual(len(invoked),1)
            with self.assertRaisesRegex(runner.SmokeBlocked,"SMOKE_OUTPUT_DRIFT"):
                jsonpath=home/"out"/("__".join(runner.keys()[0]))/"result.json"
                jsonpath.write_text("{}",encoding="utf8")
                runner.run(binary,home/"out",max_new=0)
    def test_errors_and_scope(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            with self.assertRaisesRegex(runner.SmokeBlocked,"SIMC_BINARY_REQUIRED"):
                runner.run(root/"missing",root/"out")
            b=root/"fake.exe";b.write_bytes(b"fake")
            with self.assertRaisesRegex(runner.SmokeBlocked,"INVALID_MAX_NEW"):
                runner.run(b,root/"out",max_new=17)
            with self.assertRaisesRegex(runner.SmokeBlocked,"INVALID_ITERATIONS"):
                runner.run(b,root/"out",iterations=0)
if __name__=="__main__":unittest.main()
