"""New v065 pipeline controls. No original tests or SimC are invoked here."""
import copy,hashlib,json,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v065_original_scheduler_native_bridge as runner
import v065_v015_scheduler_adapter as policy
import v064_adaptive_evaluator_port as evaluation
from test_v064_adaptive_evaluator_port import make_fixture,SIMC_SHA,CHMV1
from test_v063_numeric_injection import fake_doc

class BoundedPipeline(unittest.TestCase):
    def setUp(self):
        self.c,self.b,self.k,self.reference=make_fixture()
    def request(self,d):
        return evaluation.make_request(self.c,self.b,self.k,self.reference,
                                       SIMC_SHA,CHMV1,60,
                                       pathlib.Path(d)/"result.json")
    def test_writer_atomic_json_receipt_and_no_nonjson(self):
        with tempfile.TemporaryDirectory() as d:
            path=pathlib.Path(d)/"p"/"receipt.json"
            runner.write_atomic(path,{"a":1,"b":"가속"})
            self.assertEqual(json.loads(path.read_text()),{"a":1,"b":"가속"})
            self.assertTrue(path.is_file())
    def test_stop_file_prevents_new_native_case_before_simc(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            request=self.request(root)
            cancel=root/"stop"
            cancel.write_text("stop")
            progress={"native_attempts":0,"status":"PLAN"}
            with self.assertRaisesRegex(runner.PipelineBlocked,
                                       "USER_CANCEL_FILE_PRESENT"):
                runner.execute_one(request,self.k,root,ROOT/"runner"/"pilot.py",
                      progress,cancel)
            self.assertEqual(progress["native_attempts"],0)
            self.assertFalse((root/"input.simc").exists())
    def test_partial_native_unverified_output_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            request=self.request(root)
            (root/"result.json").write_text("{}")
            with self.assertRaisesRegex(runner.PipelineBlocked,
                                       "PARTIAL_NATIVE_OUTPUT_REQUIRES_EXPLICIT_RECOVERY"):
                runner.execute_one(request,self.k,root,ROOT/"runner"/"pilot.py",
                    {"native_attempts":0})
    def test_native_bounded_count_refuses_before_invocation(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            request=self.request(root)
            with self.assertRaisesRegex(runner.PipelineBlocked,
                                       "NATIVE_CALL_BUDGET_EXCEEDED"):
                runner.execute_one(request,self.k,root,ROOT/"runner"/"pilot.py",
                    {"native_attempts":4})
    def test_actual_result_verified_cache_can_be_reused_without_binary_run(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            request=self.request(root)
            (root/"input.simc").write_text(request["input"])
            doc=fake_doc(request["input"])
            raw=json.dumps(doc,sort_keys=True).encode()
            (root/"result.json").write_bytes(raw)
            receipt=evaluation.ingest_native(request,doc,self.k,raw)
            receipt["simc_seed"]=None
            runner.write_atomic(root/"native_receipt.json",receipt)
            progress={"native_attempts":4}
            observed=runner.execute_one(request,self.k,root,ROOT/"runner"/"pilot.py",
                               progress)
            self.assertEqual(observed["source"],"CACHED_VERIFIED_NATIVE")
            self.assertEqual(progress["native_attempts"],4)
    def test_tampered_native_receipt_not_reused(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            request=self.request(root)
            (root/"input.simc").write_text(request["input"])
            doc=fake_doc(request["input"])
            raw=json.dumps(doc,sort_keys=True).encode()
            (root/"result.json").write_bytes(raw)
            receipt=evaluation.ingest_native(request,doc,self.k,raw)
            receipt["dps_mean"]+=1
            runner.write_atomic(root/"native_receipt.json",receipt)
            with self.assertRaisesRegex(evaluation.PortBlocked,"CACHE_RESULT_CHANGED"):
                runner.execute_one(request,self.k,root,ROOT/"runner"/"pilot.py",
                                   {"native_attempts":0})
    def test_result_parser_does_not_import_original_executables(self):
        self.assertEqual(policy.SOURCE_V015_SHA256,
          "a44f73cf232c8204dbe958e79fe50f111e68654ac583a1170a283f16035c0ec3")
        self.assertFalse(hasattr(runner,"legacy"))
        self.assertEqual(runner.SCOUT_MAX,2)
        self.assertEqual(runner.CONFIRM_ITERATIONS,320)
        self.assertEqual(runner.NEW_NATIVE_MAX,4)

if __name__=="__main__":unittest.main()
