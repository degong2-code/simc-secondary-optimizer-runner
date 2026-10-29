"""P1 existing local sessions list; strictly read-only, no Native or secrets."""
from __future__ import annotations
import copy
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

from fastapi.testclient import TestClient

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v106_user_session_controller as sessions
import v113_local_web_api as web

class LocalSavedSessionIndexOffline(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        self.runs=self.root/"runs"
        self.binary=self.root/"fake_simc.exe"
        self.binary.write_bytes(b"V150_OFFLINE_BINARY_NOT_EXECUTABLE")
        self.app=web.create_app(root=self.runs,token="v150-offline")
        self.client=TestClient(self.app,base_url="http://127.0.0.1:8765")
        self.headers={"x-simc-local-token":"v150-offline",
                      "origin":"http://127.0.0.1:8765"}

    def add_session(self,key,*,independent=False,status="PASS"):
        user=sessions.user_scenario(sessions.standard_controls(key))
        folder=sessions.store_session(user,self.runs,self.binary,"7bc1071",
                                     independent_334=independent)
        if status:
            p=sessions.paths(folder)["state"]
            p.write_text(json.dumps({"schema":sessions.SCHEMA,
                                      "status":status}),encoding="utf8")
        return folder

    def index(self):
        return self.client.get("/api/v1/sessions",headers=self.headers)

    def test_empty_index_does_not_create_runs_folder(self):
        with mock.patch.object(web.subprocess,"Popen") as spawn:
            response=self.index()
            spawn.assert_not_called()
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json(),
                         {"sessions":[],"read_only":True,"native_calls_now":0})
        self.assertFalse(self.runs.exists())

    def test_multiple_sealed_session_list_never_exposes_private_data(self):
        first=self.add_session(("demonhunter","havoc"),independent=True,
                               status="PASS_CACHE_ONLY")
        second=self.add_session(("shaman","enhancement"),independent=True,
                                status="BLOCKED_OR_PARTIAL")
        # An unrelated legacy sealed session remains visible and unchanged.
        third=self.add_session(("mage","frost"),independent=False)
        before={str(p.relative_to(self.root)):p.read_bytes()
                for p in self.runs.rglob("*") if p.is_file()}
        original=pathlib.Path.read_bytes
        def fail_if_binary_read(path,*args,**kwargs):
            if path==self.binary:
                raise AssertionError("BIN_SHA_READ_ON_GET")
            return original(path,*args,**kwargs)
        with mock.patch.object(pathlib.Path,"read_bytes",fail_if_binary_read), \
             mock.patch.object(web.subprocess,"Popen") as spawn:
            result=self.index()
            spawn.assert_not_called()
        self.assertEqual(result.status_code,200,result.text)
        data=result.json()
        self.assertEqual(len(data["sessions"]),3)
        byid={x["session_id"]:x for x in data["sessions"]}
        self.assertEqual(byid[first.name]["recorded_status"],"PASS_CACHE_ONLY")
        self.assertTrue(byid[first.name]["independent_target334_profile"])
        self.assertFalse(byid[third.name]["independent_target334_profile"])
        self.assertEqual(byid[second.name]["recorded_status"],"BLOCKED_OR_PARTIAL")
        self.assertEqual(data["native_calls_now"],0)
        self.assertTrue(data["read_only"])
        self.assertNotIn("talents",result.text)
        self.assertNotIn("trinkets",result.text)
        self.assertNotIn(str(self.root),result.text)
        self.assertNotIn("simc_binary_sha256",result.text)
        after={str(p.relative_to(self.root)):p.read_bytes()
               for p in self.runs.rglob("*") if p.is_file()}
        self.assertEqual(before,after)

    def test_tampered_user_and_identity_excluded_without_affecting_others(self):
        good=self.add_session(("druid","feral"),independent=True)
        drift=self.add_session(("shaman","enhancement"),independent=True)
        raw=json.loads((drift/"user.json").read_text(encoding="utf8"))
        raw["target"]["ilevel"]=333
        (drift/"user.json").write_text(json.dumps(raw),encoding="utf8")
        missing=self.add_session(("mage","arcane"),independent=True)
        (missing/"V106_SESSION_IDENTITY.json").unlink()
        huge=self.add_session(("priest","shadow"),independent=True)
        (huge/"V106_WORKER_STATE.json").write_bytes(b"x"*20000)
        result=self.index()
        self.assertEqual(result.status_code,200,result.text)
        self.assertEqual([x["session_id"] for x in result.json()["sessions"]],
                         [good.name])

    def test_local_token_and_restore_endpoint_still_required(self):
        self.assertEqual(self.client.get("/api/v1/sessions").status_code,403)
        self.assertEqual(self.client.get("/api/v1/sessions",
            headers={**self.headers,"origin":"https://evil.example"}).status_code,403)
        controls=sessions.standard_controls(("demonhunter","havoc"))
        payload={"controls":controls,"binary":str(self.binary),"revision":"7bc1071"}
        postheaders={**self.headers,"content-type":"application/json"}
        with mock.patch.object(web.subprocess,"Popen") as spawn:
            planned=self.client.post("/api/v1/sessions/plan",
                                     json=payload,headers=postheaders)
            self.assertEqual(planned.status_code,200,planned.text)
            record=self.index()
            self.assertEqual(record.status_code,200)
            sid=planned.json()["session_id"]
            self.assertEqual(record.json()["sessions"][0]["session_id"],sid)
            restore=self.client.get("/api/v1/sessions/"+sid+"/inputs",
                                    headers=self.headers)
            self.assertEqual(restore.status_code,200,restore.text)
            self.assertEqual(restore.json()["user"]["character"]["spec"],"havoc")
            spawn.assert_not_called()

if __name__=="__main__":unittest.main()
