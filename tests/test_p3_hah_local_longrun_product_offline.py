"""P3-HAH local product route/worker integration, no real Native."""
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

from fastapi.testclient import TestClient

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v113_local_web_api as web
import v293_local_longrun_session as service


class FakeChild:
    def __init__(self):
        self.exit_code=None
    def poll(self):
        return self.exit_code


class LocalLongRunHTTP(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root=pathlib.Path(self.tmp.name)
        self.app=web.create_app(root=root/"runs",token="local-token")
        self.client=TestClient(self.app,base_url="http://127.0.0.1:8765")
        self.auth={"x-simc-local-token":"local-token",
                   "origin":"http://127.0.0.1:8765"}
        self.folder=root/"runs"/("a"*20)
        (self.folder/"generated").mkdir(parents=True)
        (self.folder/"generated"/"manifest.json").write_text("{}")
        (self.folder/"V106_SESSION_IDENTITY.json").write_text("{}")
        self.stage=service.stage_path(self.folder,12)
        self.stage.mkdir(parents=True)
        jobs=self.app.state.jobs
        self.plan=mock.patch.object(jobs,"plan",return_value={
            "session_id":self.folder.name})
        self.args=mock.patch.object(jobs,"args_for_existing",
                                    return_value=(root/"simc","abcd123",None))
        self.deps=mock.patch.object(jobs,"_verify_environment_dependencies",
                                    return_value=None)
        self.prepare=mock.patch.object(web.longrun_sessions,"prepare",
                                      return_value={"paths":{}})
        self.child=FakeChild()
        self.popen=mock.patch.object(web.subprocess,"Popen",
                                    return_value=self.child)
        for patcher in (self.plan,self.args,self.deps,self.prepare,self.popen):
            patcher.start(); self.addCleanup(patcher.stop)

    def post(self,path,data):
        return self.client.post(path,json=data,
                                headers=self.auth|{"content-type":"application/json"})

    def test_http_start_status_cancel_restart_resume_and_import_only(self):
        endpoint="/api/v1/longrun/start"
        data={"controls":{},"binary":"c:/simc.exe",
              "revision":"abc1234","current_season_product":True,
              "max_native_calls":12,"max_new_native_this_invocation":4}
        self.assertEqual(self.client.post(endpoint,json=data).status_code,403)
        self.assertFalse(self.client.get(
            "/api/v1/sessions/"+self.folder.name+"/longrun/status",
            headers=self.auth).json()["enabled"])
        first=self.post(endpoint,data)
        self.assertEqual(first.status_code,200,first.text)
        self.assertEqual(first.json()["max_new_native_this_invocation"],4)
        self.assertEqual(service.config(self.folder)["native_budget"],12)
        self.assertTrue(self.client.get(
            "/api/v1/sessions/"+self.folder.name+"/longrun/status",
            headers=self.auth).json()["active"])
        self.assertEqual(self.post(endpoint,data).status_code,409)
        cancel=self.post("/api/v1/sessions/"+self.folder.name+
                         "/longrun/cancel",{})
        self.assertEqual(cancel.status_code,200,cancel.text)
        self.assertTrue((self.stage/"CANCEL").is_file())
        self.child.exit_code=0
        self.assertFalse(self.client.get(
            "/api/v1/sessions/"+self.folder.name+"/longrun/status",
            headers=self.auth).json()["active"])
        resumed=self.post("/api/v1/sessions/"+self.folder.name+
                          "/longrun/resume",
                          {"max_new_native_this_invocation":2})
        self.assertEqual(resumed.status_code,200,resumed.text)
        self.assertFalse((self.stage/"CANCEL").exists())
        self.assertEqual(resumed.json()["max_new_native_this_invocation"],2)
        self.child.exit_code=0
        imp=self.post("/api/v1/sessions/"+self.folder.name+
                      "/longrun/import",
                      {"archive_path":"/tmp/fixture.zip",
                       "archive_sha256":"f"*64})
        self.assertEqual(imp.status_code,200,imp.text)
        args=self.app.state.jobs.children[self.folder.name]
        self.assertIs(args,self.child)
        call=web.subprocess.Popen.call_args
        self.assertIn("--portable-archive",call.args[0])
        self.assertIn("--portable-sha256",call.args[0])
        self.assertIn("--cache-only",call.args[0])
        self.assertEqual(self.post("/api/v1/sessions/"+self.folder.name+
                         "/longrun/import",
                         {"archive_path":"/tmp/fixture.zip",
                          "archive_sha256":"wrong"}).status_code,422)

    def test_sealed_manifest_tamper_blocks_status_and_resume(self):
        data={"controls":{},"binary":"/simc",
              "revision":"abcd123","current_season_product":True}
        self.assertEqual(self.post("/api/v1/longrun/start",data).status_code,200)
        (self.folder/"generated"/"manifest.json").write_text('{"tampered":true}')
        self.assertEqual(self.client.get(
            "/api/v1/sessions/"+self.folder.name+"/longrun/status",
            headers=self.auth).status_code,422)
        self.child.exit_code=0
        self.assertEqual(self.post("/api/v1/sessions/"+self.folder.name+
                         "/longrun/resume",{}).status_code,422)

    def test_insecure_host_is_denied(self):
        response=self.client.get(
            "/api/v1/sessions/"+self.folder.name+"/longrun/status",
            headers={"host":"evil.com","x-simc-local-token":"local-token"})
        self.assertEqual(response.status_code,403)


class LocalLongRunWorkerOffline(unittest.TestCase):
    def test_worker_uses_original_lock_and_bounded_v291_without_native(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=pathlib.Path(tmp)/("a"*20)
            folder.mkdir()
            budget=12
            manifest=folder/"generated"/"manifest.json"
            manifest.parent.mkdir()
            manifest.write_text("{}")
            doc={"schema":service.SCHEMA,"native_budget":budget,
                 "manifest_sha256":hashlib.sha256(
                     manifest.read_bytes()).hexdigest()}
            service.durable.atomic(service.config_path(folder),doc)
            binary=folder/"dummy"
            binary.write_bytes(b"test")
            output=service.stage_path(folder,budget)/"simc_results"
            cancel=service.stage_path(folder,budget)/"CANCEL"
            prepared={"context":{},"flask":{},"paths":{
                "output_dir":output,"cancel_file":cancel,
                "native_binary":binary}}
            fake_result={"status":"PAUSED_INVOCATION_NATIVE_BUDGET",
                         "new_native_this_invocation":2}
            with mock.patch.object(service,"prepare",return_value=prepared), \
                 mock.patch.object(service.durable,"run",
                                   return_value=fake_result) as executor:
                ok=service.run_worker(folder,12,2)
                self.assertEqual(ok,0)
                self.assertEqual(executor.call_args.kwargs[
                    "max_new_native_this_invocation"],2)
                self.assertFalse(executor.call_args.kwargs["cache_only"])
                state=service.durable.read_json(
                    service.worker_state_path(folder))
                self.assertEqual(state["status"],"PAUSED_INVOCATION_NATIVE_BUDGET")
                self.assertEqual(state["new_native_this_invocation"],2)
                with service.sessions.worker_lock(folder):
                    denied=service.run_worker(folder,12,2)
                self.assertEqual(denied,3)
                self.assertEqual(service.durable.read_json(
                    service.worker_state_path(folder)),state)

    def test_result_adapter_never_claims_global_optimum(self):
        base={"crit_rating":1,"haste_rating":1552,
              "mastery_rating":1553,"versatility_rating":1}
        report={"status":"PAUSED_INVOCATION_NATIVE_BUDGET",
            "confidence_for_display":0.95,
            "no_global_optimum_proof":True,
            "summary":{
                "final_T":3107,"underlying_B":3107,
                "fixed_O":{k:0 for k in base},
                "observed_best_T":base,
                "observed_best_dps":185438.66,
                "observed_best_sem":280.53,
                "observed_unique_targets":8,
                "material_alternatives":[]},
            "confirmed_selected_pair_95":{
                "pairwise_direction_supported":True},
            "native_attempts_cumulative":10,
            "verified_cache_cases_this_invocation":10}
        result=service.user_result(report)
        self.assertEqual(result["confidence_level"],0.95)
        self.assertFalse(result["global_optimum_proven"])
        self.assertFalse(result["selection_multiplicity_corrected"])
        self.assertTrue(result["confirmation_pair_direction_supported_at_95"])
        self.assertEqual(sum(result["observed_first_choice"][
            "percent_of_final_T"].values()),100.0)
        report["no_global_optimum_proof"]=False
        with self.assertRaises(service.LocalLongRunBlocked):
            service.user_result(report)


if __name__=="__main__":
    unittest.main()
