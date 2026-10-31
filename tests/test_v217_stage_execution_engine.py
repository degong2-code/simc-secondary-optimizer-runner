"""v217 generic Stage Execution Engine tests; offline and no SimC."""
import pathlib
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v217_stage_execution_engine as stage


class StageExecutionEngineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        self.outputs={"profile":"profile.simc","manifest":"manifest.json"}
        self.inputs={"user_sha256":"a"*64,"code_sha256":"b"*64}
        self.calls=[]

    def execute(self):
        self.calls.append("execute")
        (self.root/"profile.simc").write_text("profile-v1",encoding="utf8")
        (self.root/"manifest.json").write_text('{"ready":true}',encoding="utf8")
        return {"built":True}

    def validate(self,paths):
        return (paths["profile"].read_text(encoding="utf8")=="profile-v1" and
                paths["manifest"].read_text(encoding="utf8")=='{"ready":true}')

    def test_first_execution_is_sealed_and_second_request_skips_executor(self):
        first=stage.execute_stage(root=self.root,stage_id="profile",
            stage_version="v1",inputs=self.inputs,outputs=self.outputs,
            execute=self.execute,validate=self.validate)
        second=stage.execute_stage(root=self.root,stage_id="profile",
            stage_version="v1",inputs=self.inputs,outputs=self.outputs,
            execute=self.execute,validate=self.validate)
        self.assertEqual(first["status"],"EXECUTED_AND_SEALED")
        self.assertTrue(first["executed"])
        self.assertEqual(first["receipt_writes"],2)
        self.assertEqual(second["status"],"REUSED_VERIFIED")
        self.assertTrue(second["reused"])
        self.assertFalse(second["executed"])
        self.assertEqual(second["receipt_writes"],0)
        self.assertEqual(self.calls,["execute"])
        self.assertEqual(first["output_count"],2)
        self.assertGreater(first["output_bytes"],0)

    def test_completed_output_corruption_blocks_without_overwrite(self):
        stage.execute_stage(root=self.root,stage_id="profile",
            stage_version="v1",inputs=self.inputs,outputs=self.outputs,
            execute=self.execute,validate=self.validate)
        (self.root/"profile.simc").write_text("tampered",encoding="utf8")
        with self.assertRaisesRegex(stage.StageExecutionBlocked,
                                    "STAGE_OUTPUT_HASH_MISMATCH"):
            stage.execute_stage(root=self.root,stage_id="profile",
                stage_version="v1",inputs=self.inputs,outputs=self.outputs,
                execute=self.execute,validate=self.validate)
        self.assertEqual(self.calls,["execute"])
        self.assertEqual((self.root/"profile.simc").read_text(),"tampered")

    def test_completed_stage_rejects_changed_input_fingerprint(self):
        stage.execute_stage(root=self.root,stage_id="profile",
            stage_version="v1",inputs=self.inputs,outputs=self.outputs,
            execute=self.execute,validate=self.validate)
        with self.assertRaisesRegex(stage.StageExecutionBlocked,
                                    "STAGE_INPUT_FINGERPRINT_MISMATCH"):
            stage.execute_stage(root=self.root,stage_id="profile",
                stage_version="v1",inputs=self.inputs|{"code_sha256":"c"*64},
                outputs=self.outputs,execute=self.execute,validate=self.validate)
        self.assertEqual(self.calls,["execute"])

    def test_interrupted_complete_outputs_are_recovered_without_reexecution(self):
        def interrupted():
            self.calls.append("execute")
            (self.root/"profile.simc").write_text("profile-v1",encoding="utf8")
            (self.root/"manifest.json").write_text(
                '{"ready":true}',encoding="utf8")
            raise RuntimeError("simulated process interruption")
        with self.assertRaisesRegex(RuntimeError,"interruption"):
            stage.execute_stage(root=self.root,stage_id="profile",
                stage_version="v1",inputs=self.inputs,outputs=self.outputs,
                execute=interrupted,validate=self.validate)
        recovered=stage.execute_stage(root=self.root,stage_id="profile",
            stage_version="v1",inputs=self.inputs,outputs=self.outputs,
            execute=self.execute,validate=self.validate)
        self.assertEqual(recovered["status"],"RECOVERED_VERIFIED")
        self.assertTrue(recovered["recovered"])
        self.assertFalse(recovered["executed"])
        self.assertEqual(self.calls,["execute"])
        self.assertEqual(stage.verify_stage(root=self.root,stage_id="profile",
            stage_version="v1",inputs=self.inputs,outputs=self.outputs)["status"],
            "REUSED_VERIFIED")

    def test_interrupted_partial_outputs_retry_only_declared_stage_files(self):
        def interrupted():
            self.calls.append("execute")
            (self.root/"profile.simc").write_text("partial",encoding="utf8")
            raise RuntimeError("simulated partial write")
        with self.assertRaisesRegex(RuntimeError,"partial write"):
            stage.execute_stage(root=self.root,stage_id="profile",
                stage_version="v1",inputs=self.inputs,outputs=self.outputs,
                execute=interrupted,validate=self.validate)
        second=stage.execute_stage(root=self.root,stage_id="profile",
            stage_version="v1",inputs=self.inputs,outputs=self.outputs,
            execute=self.execute,validate=self.validate)
        self.assertEqual(second["status"],"EXECUTED_AND_SEALED")
        self.assertEqual(self.calls,["execute","execute"])
        self.assertEqual((self.root/"profile.simc").read_text(),"profile-v1")

    def test_module_fingerprint_tracks_transitive_local_imports(self):
        runner=self.root/"runner"
        runner.mkdir()
        (runner/"entry.py").write_text("import helper\nVALUE=helper.VALUE\n",
                                       encoding="utf8")
        (runner/"helper.py").write_text("VALUE=1\n",encoding="utf8")
        first=stage.module_dependency_fingerprint([runner/"entry.py"])
        self.assertEqual(first["module_count"],2)
        (runner/"helper.py").write_text("VALUE=2\n",encoding="utf8")
        second=stage.module_dependency_fingerprint([runner/"entry.py"])
        self.assertNotEqual(first["sha256"],second["sha256"])
        self.assertNotEqual(first["files"]["helper.py"],
                            second["files"]["helper.py"])


if __name__=="__main__":
    unittest.main()
