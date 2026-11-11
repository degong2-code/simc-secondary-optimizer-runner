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
        self.valid_controls=web.sessions.standard_controls()
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

    def test_primary64_cannot_use_packaged_source_without_fresh_v212(self):
        """No old v213 source-only plan may launch the default product worker."""
        data={"controls":self.valid_controls,"binary":"c:/simc.exe",
              "revision":"abc1234","current_season_product":True,
              "max_native_calls":64,"continuous":True}
        with mock.patch.object(
                self.app.state.jobs,"prepare_with_internal_special_L"
                ) as stage:
            response=self.post("/api/v1/longrun/start",data)
        self.assertEqual(response.status_code,422,response.text)
        self.assertEqual(response.json()["detail"]["code"],
                         "WEB_PRIMARY_VERIFIED_SEASON_INSTALL_REQUIRED")
        stage.assert_not_called()
        web.subprocess.Popen.assert_not_called()
        self.assertIsNone(service.config(self.folder))
        # Explicitly spelling an old build never creates an installed
        # profile; the existing source owner must validate it.
        data["installed_season_game_build"]="12.1.5.70575"
        with mock.patch.object(
                self.app.state.jobs,"prepare_with_internal_special_L"
                ) as original:
            original.side_effect=web.environment_manifest.EnvironmentBlocked(
                "WEB_SELECTED_INSTALLED_SEASON_BUILD_NOT_FOUND")
            missing=self.post("/api/v1/longrun/start",data)
        self.assertEqual(missing.status_code,422,missing.text)
        web.subprocess.Popen.assert_not_called()

    def test_existing_64_source_only_resume_fails_before_native(self):
        """Preexisting historical long-run artifacts remain readable only."""
        service.establish(self.folder,64)
        jobs=self.app.state.jobs
        with mock.patch.object(jobs,"_read_environment_summary",
                               return_value={"status":"READY_WITH_LIMITATIONS"}):
            result=self.post(
                "/api/v1/sessions/"+self.folder.name+"/longrun/resume",
                {"continuous":True})
        self.assertEqual(result.status_code,422,result.text)
        self.assertEqual(result.json()["detail"]["code"],
                         "WEB_PRIMARY_VERIFIED_SEASON_INSTALL_REQUIRED")
        web.subprocess.Popen.assert_not_called()
        self.assertEqual(service.config(self.folder)["native_budget"],64)

    def test_http_start_status_cancel_restart_resume_and_import_only(self):
        endpoint="/api/v1/longrun/start"
        data={"controls":self.valid_controls,"binary":"c:/simc.exe",
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
        self.assertEqual(service.config(self.folder)["scout_iterations"],56)
        self.assertEqual(self.client.get(
            "/api/v1/sessions/"+self.folder.name+"/longrun/status",
            headers=self.auth).json()["scout_iterations_per_CHMV"],56)
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
        self.assertEqual(service.config(self.folder)["scout_iterations"],56)
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

    def test_restart_with_stale_running_status_preserves_result_and_resume(self):
        # Windows process restart boundary. Fake worker & synthetic V291
        # report ONLY; never execute SimC or modify a verified Native cache.
        req={"controls":self.valid_controls,"binary":"c:/simc.exe",
             "revision":"abc1234","current_season_product":True,
             "max_native_calls":12,"max_new_native_this_invocation":4}
        started=self.post("/api/v1/longrun/start",req)
        self.assertEqual(started.status_code,200,started.text)
        self.child.exit_code=1  # worker no longer owns a live OS process
        service.state(self.folder,"RUNNING")
        result_dir=self.stage/"simc_results"
        result_dir.mkdir(parents=True,exist_ok=True)
        base={"crit_rating":1,"haste_rating":1552,
              "mastery_rating":1553,"versatility_rating":1}
        report={"status":"PAUSED_INVOCATION_NATIVE_BUDGET",
                "confidence_for_display":0.95,
                "no_global_optimum_proof":True,
                "summary":{"final_T":3107,"underlying_B":3107,
                           "fixed_O":{k:0 for k in base},
                           "observed_best_T":base,
                           "observed_best_dps":185438.66,
                           "observed_best_sem":280.53,
                           "observed_unique_targets":8,
                           "material_alternatives":[]},
                "native_attempts_cumulative":10,
                "verified_cache_cases_this_invocation":0}
        (result_dir/"V291_RESULT.json").write_text(
            json.dumps(report),encoding="utf8")
        (result_dir/"V291_PROGRESS.json").write_text(
            json.dumps({"completed_cases":10,"native_attempts_cumulative":10,
                        "status":"RUNNING"}),encoding="utf8")
        watched=[service.config_path(self.folder),service.worker_state_path(self.folder),
                 result_dir/"V291_RESULT.json",result_dir/"V291_PROGRESS.json"]
        before={str(p):p.read_bytes() for p in watched}
        # New in-memory FastAPI instance using the exact same local sessions.
        # No hidden import, session re-key, or new profile constructor.
        second=web.create_app(root=self.folder.parent,token="local-token")
        client=TestClient(second,base_url="http://127.0.0.1:8765")
        uri="/api/v1/sessions/"+self.folder.name+"/longrun"
        status=client.get(uri+"/status",headers=self.auth)
        self.assertEqual(status.status_code,200,status.text)
        self.assertTrue(status.json()["enabled"])
        self.assertFalse(status.json()["active"])
        self.assertTrue(status.json()["result_ready"])
        self.assertEqual(status.json()["progress"]["worker"]["status"],"RUNNING")
        self.assertEqual(status.json()["scout_iterations_per_CHMV"],56)
        self.assertEqual(status.json()["progress"]["completed_jobs"],10)
        prior=client.get(uri+"/result",headers=self.auth)
        self.assertEqual(prior.status_code,200,prior.text)
        self.assertEqual(prior.json()["native_calls_cumulative"],10)
        self.assertEqual(prior.json()["user_result"]["confidence_level"],0.95)
        self.assertFalse(prior.json()["user_result"]["global_optimum_proven"])
        self.assertEqual(before,{str(p):p.read_bytes() for p in watched})
        self.assertEqual(web.subprocess.Popen.call_count,1)
        with mock.patch.object(second.state.jobs,
                               "_verify_environment_dependencies",return_value=None), \
             mock.patch.object(second.state.jobs,"args_for_existing",
                               return_value=(self.folder/"simc.exe","abc1234",None)):
            resumed=client.post(uri+"/resume",
                headers=self.auth|{"content-type":"application/json"},
                json={"max_new_native_this_invocation":2})
        self.assertEqual(resumed.status_code,200,resumed.text)
        self.assertEqual(resumed.json()["max_new_native_this_invocation"],2)
        self.assertEqual(service.config(self.folder)["scout_iterations"],56)
        self.assertEqual(web.subprocess.Popen.call_count,2)
        self.assertIn("--max-native-calls",
                      web.subprocess.Popen.call_args.args[0])
        self.assertEqual((result_dir/"V291_RESULT.json").read_bytes(),
                         before[str(result_dir/"V291_RESULT.json")])

    def test_prepare_before_cache_import_does_not_start_native_worker(self):
        data={"controls":self.valid_controls,"binary":"c:/simc.exe",
              "revision":"abc1234","current_season_product":True,
              "max_native_calls":12}
        response=self.post("/api/v1/longrun/prepare",data)
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()["new_dps_native_calls"],0)
        self.assertEqual(response.json()["status"],
                         "LONGRUN_SOURCE_PREPARED_NO_DPS_NATIVE")
        self.assertIsNotNone(service.config(self.folder))
        web.subprocess.Popen.assert_not_called()
        new=self.post("/api/v1/sessions/"+self.folder.name+
                      "/longrun/import",
                      {"archive_path":"/tmp/exact.zip",
                       "archive_sha256":"f"*64})
        self.assertEqual(new.status_code,200,new.text)
        self.assertEqual(new.json()["max_new_native_this_invocation"],0)
        self.assertIn("--portable-archive",web.subprocess.Popen.call_args.args[0])
        self.assertIn("--cache-only",web.subprocess.Popen.call_args.args[0])

    def test_sealed_manifest_tamper_blocks_status_and_resume(self):
        data={"controls":self.valid_controls,"binary":"/simc",
              "revision":"abcd123","current_season_product":True}
        self.assertEqual(self.post("/api/v1/longrun/start",data).status_code,200)
        (self.folder/"generated"/"manifest.json").write_text('{"tampered":true}')
        self.assertEqual(self.client.get(
            "/api/v1/sessions/"+self.folder.name+"/longrun/status",
            headers=self.auth).status_code,422)
        self.child.exit_code=0
        self.assertEqual(self.post("/api/v1/sessions/"+self.folder.name+
                         "/longrun/resume",{}).status_code,422)

    def test_longrun_start_shares_exact_static_L_preparation(self):
        jobs=self.app.state.jobs
        fake_hydrated={"native_new_calls":1,"cache_reused":0}
        receipt={"path":"V208_STATIC_L.json"}
        with mock.patch.object(jobs,"prepare_with_internal_special_L",
                               return_value=(self.folder,fake_hydrated,
                                             {"status":"READY"},receipt)) as prepare, \
             mock.patch.object(jobs,"longrun_launch",
                               return_value={"session_id":self.folder.name,
                                             "status":"LONGRUN_WORKER_STARTED"}) as launch:
            start=self.post("/api/v1/longrun/start",{
                "controls":{},"binary":"c:/simc.exe",
                "revision":"abc1234","current_season_product":True,
                "max_native_calls":12,"max_new_native_this_invocation":4})
            self.assertEqual(start.status_code,200,start.text)
            self.assertEqual(start.json()["static_L_native_calls_this_start"],1)
            self.assertEqual(start.json()["static_L_start_receipt"],receipt)
            self.assertEqual(start.json()["environment_manifest"],{"status":"READY"})
            self.assertEqual(prepare.call_count,1)
            launch.assert_called_once()

    def test_insecure_host_is_denied(self):
        response=self.client.get(
            "/api/v1/sessions/"+self.folder.name+"/longrun/status",
            headers={"host":"evil.com","x-simc-local-token":"local-token"})
        self.assertEqual(response.status_code,403)




if __name__=="__main__":
    unittest.main()
