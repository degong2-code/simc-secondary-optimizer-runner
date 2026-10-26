"""v110 regression: written Native SimC UTF-8 input is byte-identical on Windows.

No SimC calls. Exercises the REAL v065 execute_one code path, intercepts
subprocess.run before any executable can be started. Pre-Native stale CRLF
input from the user's Windows v109 failed run is safe to overwrite; a
completed Native JSON2 + receipt remains separately protected by v064.
"""
import hashlib,pathlib,sys,tempfile,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
sys.path.insert(0,str(ROOT/"tests"))
import v065_original_scheduler_native_bridge as bridge
import v064_adaptive_evaluator_port as adaptive
from test_v064_adaptive_evaluator_port import make_fixture,SIMC_SHA,CHMV1

class WrittenNativeExactBytes(unittest.TestCase):
    def setUp(self):
        self.c,self.b,self.k,self.reference=make_fixture()
    def make_request(self,case):
        return adaptive.make_request(self.c,self.b,self.k,self.reference,
            SIMC_SHA,CHMV1,60,case/"result.json")

    def test_real_native_entry_writes_lf_utf8_even_on_windows_and_accepts_retry(self):
        with tempfile.TemporaryDirectory() as td:
            case=pathlib.Path(td)/"seed_00"
            case.mkdir()
            request=self.make_request(case)
            exact=request["input"].encode("utf8")
            self.assertIn(b"\n",exact)
            self.assertNotIn(b"\r\n",exact)
            self.assertEqual(hashlib.sha256(exact).hexdigest(),
                             request["input_sha256"])
            # The failed Windows attempt wrote a CRLF-translated input
            # before any result.json or native_receipt.json was created.
            previous=exact.replace(b"\n",b"\r\n")
            self.assertNotEqual(hashlib.sha256(previous).hexdigest(),
                                request["input_sha256"])
            (case/"input.simc").write_bytes(previous)
            self.assertFalse((case/"result.json").exists())
            self.assertFalse((case/"native_receipt.json").exists())

            def intercept(args,**kwargs):
                # This is before any real process invocation. A byte hash
                # mismatch would have blocked the code before this callback.
                actual=(case/"input.simc").read_bytes()
                self.assertEqual(actual,exact)
                self.assertEqual(hashlib.sha256(actual).hexdigest(),
                                 request["input_sha256"])
                self.assertEqual(kwargs["stdin"],bridge.subprocess.DEVNULL)
                raise RuntimeError("V110_INTERCEPTED_BEFORE_NATIVE_NO_EXECUTION")

            progress={"native_attempts":0,"status":"PLAN"}
            with patch.object(bridge.subprocess,"run",side_effect=intercept) as run:
                with self.assertRaisesRegex(RuntimeError,
                         "V110_INTERCEPTED_BEFORE_NATIVE_NO_EXECUTION"):
                    bridge.execute_one(request,self.k,ROOT/"runner"/"pilot.py",
                                       case,progress)
            self.assertEqual(run.call_count,1)
            self.assertEqual((case/"input.simc").read_bytes(),exact)
            self.assertEqual(progress["native_attempts"],1)
            # The test intercepts the call before starting any Native SimC.
            self.assertFalse((case/"result.json").exists())
            self.assertFalse((case/"native_receipt.json").exists())

    def test_cancel_before_rewriting_input_preserves_original_failed_artifact(self):
        with tempfile.TemporaryDirectory() as td:
            case=pathlib.Path(td)/"seed_00";case.mkdir()
            request=self.make_request(case)
            old=request["input"].replace("\n","\r\n").encode("utf8")
            (case/"input.simc").write_bytes(old)
            cancel=case.parent/"CANCEL";cancel.touch()
            with patch.object(bridge.subprocess,"run") as run:
                with self.assertRaisesRegex(bridge.PipelineBlocked,
                                            "USER_CANCEL_FILE_PRESENT"):
                    bridge.execute_one(request,self.k,ROOT/"runner"/"pilot.py",
                                       case,{"native_attempts":0},cancel_file=cancel)
            run.assert_not_called()
            self.assertEqual((case/"input.simc").read_bytes(),old)

if __name__=="__main__":
    unittest.main()
