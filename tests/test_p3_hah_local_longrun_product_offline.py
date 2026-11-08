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




if __name__=="__main__":
    unittest.main()
