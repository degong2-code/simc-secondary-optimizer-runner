"""v348: Windows user's own API credentials; offline/no SimC or remote API."""
from __future__ import annotations

import json
import os
import pathlib
import secrets
import sys
import tempfile
import unittest
from unittest import mock

from fastapi.testclient import TestClient

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v113_local_web_api as web
import v348_windows_user_source_credentials as vault

PAYLOAD={
    "blizzard_client_id":"local-test-blizzard-client-id",
    "blizzard_client_secret":"local-test-blizzard-client-secret",
    "wcl_client_id":"local-test-wcl-client-id",
    "wcl_client_secret":"local-test-wcl-client-secret"}
INTERNAL={x.upper():y for x,y in PAYLOAD.items()}

class FakeWindowsVault:
    def __init__(self):
        self.record=None
        self.reads=0
    def save(self,data):
        vault._validate(data)
        self.record=dict(data)
        return {"schema":vault.SCHEMA,"storage":"WINDOWS_CREDENTIAL_MANAGER",
                "saved":True,"configured":True,"native_calls":0,"network_calls":0}
    def load(self):
        self.reads+=1
        return dict(self.record) if self.record is not None else None
    def status(self):
        return {"schema":vault.SCHEMA,"storage":"WINDOWS_CREDENTIAL_MANAGER",
                "configured":self.record is not None,"supported":True,
                "native_calls":0,"network_calls":0}
    def clear(self):
        self.record=None
        return {"schema":vault.SCHEMA,"storage":"WINDOWS_CREDENTIAL_MANAGER",
                "deleted":True,"configured":False,"native_calls":0,
                "network_calls":0}

class LocalSourceCredentialHTTP(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=pathlib.Path(tmp.name)/"runs"
        self.vault=FakeWindowsVault()
        self.app=web.create_app(root=self.root,token="test-v348-opaque-token",
                                source_credential_store=self.vault)
        self.client=TestClient(self.app,base_url="http://127.0.0.1:8765")
        self.headers={"x-simc-local-token":"test-v348-opaque-token",
                      "origin":"http://127.0.0.1:8765",
                      "content-type":"application/json"}
    def post(self,path,data):
        return self.client.post(path,json=data,headers=self.headers)
    def get(self,path):
        return self.client.get(path,headers=self.headers)

    def test_save_status_clear_are_local_explicit_and_secret_free(self):
        path="/api/v1/source-credentials"
        self.assertEqual(self.get(path+"/status").json()["configured"],False)
        bad=self.client.post(path+"/save",json=PAYLOAD,
                             headers={"content-type":"application/json"})
        self.assertEqual(bad.status_code,403)
        foreign=self.client.post(path+"/save",json=PAYLOAD,headers={
            **self.headers,"origin":"http://evil.com"})
        self.assertEqual(foreign.status_code,403)
        self.assertIsNone(self.vault.record)
        response=self.post(path+"/save",PAYLOAD)
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(self.vault.record,INTERNAL)
        self.assertEqual(self.get(path+"/status").json()["configured"],True)
        for response in (response,self.get(path+"/status")):
            self.assertNotIn("local-test-",response.text)
            self.assertNotIn("BLIZZARD_CLIENT_SECRET",response.text)
        # No source/credential bytes are ever stored in the session root.
        self.assertFalse(self.root.exists())
        invalid=self.post(path+"/save",{**PAYLOAD,"wcl_client_secret":"\nBAD"})
        self.assertEqual(invalid.status_code,422)
        self.assertEqual(self.vault.record,INTERNAL)
        missing=self.post(path+"/save",{k:v for k,v in PAYLOAD.items()
                                        if k!="wcl_client_secret"})
        self.assertEqual(missing.status_code,422)
        self.assertNotIn("local-test-",missing.text)
        deleted=self.post(path+"/clear",{})
        self.assertEqual(deleted.status_code,200,deleted.text)
        self.assertFalse(self.get(path+"/status").json()["configured"])
        self.assertIsNone(self.vault.load())
        self.assertFalse(self.root.exists())

    def test_operator_credentials_reach_original_v216_only_on_cache_miss(self):
        self.post("/api/v1/source-credentials/save",PAYLOAD)
        pending={"status":"SOURCE_STAGE_PENDING","environment_ready":False,
                 "environment_installed":False,"native_calls":0,
                 "zero_history_build":{"requires":["SEASON_MEMBERSHIP_PENDING"],
                                       "environment_ready":False}}
        jobs=self.app.state.jobs
        with mock.patch.object(web.environment_build,"build_environment",
                               return_value=pending) as owner, \
             mock.patch.object(web.physical_gems,
                               "load_packaged_season_nominal_source",
                               return_value=None), \
             mock.patch.object(jobs,"_with_verified_ko_localization",
                               side_effect=lambda b,t,r,**kw:r), \
             mock.patch.object(jobs,"plan",
                               side_effect=AssertionError("DPS_FORBIDDEN")):
            result=self.post("/api/v1/environment/season-build",{
                "game_build":"12.1.5.70783","target_ilevel":334})
        self.assertEqual(result.status_code,200,result.text)
        self.assertEqual(result.json()["status"],"SOURCE_STAGE_PENDING")
        self.assertFalse(result.json()["web_environment_scope"]["environment_ready"])
        self.assertEqual(owner.call_count,1)
        passed=owner.call_args.kwargs["fresh_collection_inputs"]
        self.assertEqual(passed["credentials"],INTERNAL)
        self.assertEqual(passed["expected_game_build"],"12.1.5.70783")
        self.assertEqual(passed["representative_request"],
                         {"class":"paladin","spec":"retribution",
                          "target_ilevel":334})
        self.assertEqual(self.vault.reads,1)
        for val in PAYLOAD.values():
            self.assertNotIn(val,result.text)
        self.assertFalse(self.root.exists())

    def test_missing_keys_keep_v216_original_optional_no_key_route(self):
        pending={"status":"SOURCE_STAGE_PENDING","environment_ready":False,
                 "environment_installed":False}
        jobs=self.app.state.jobs
        with mock.patch.object(web.environment_build,"build_environment",
                               return_value=pending) as owner, \
             mock.patch.object(web.physical_gems,
                               "load_packaged_season_nominal_source",
                               return_value=None), \
             mock.patch.object(jobs,"_with_verified_ko_localization",
                               side_effect=lambda b,t,r,**kw:r):
            result=self.post("/api/v1/environment/season-build",{
                "game_build":"12.1.5.70783"})
        self.assertEqual(result.status_code,200,result.text)
        self.assertNotIn("credentials",
                         owner.call_args.kwargs["fresh_collection_inputs"])
        self.assertEqual(self.vault.reads,1)

    def test_malformed_secret_never_enters_native_or_workflow(self):
        path="/api/v1/source-credentials/save"
        for val in ("\x00sentinel","\n","  spaced  "):
            obj={**PAYLOAD,"blizzard_client_secret":val}
            self.assertEqual(self.post(path,obj).status_code,422)
        self.assertIsNone(self.vault.record)
        with self.assertRaisesRegex(vault.CredentialBlocked,
                                     "SOURCE_API_CREDENTIAL_TARGET_INVALID"):
            vault.WindowsSourceCredentialStore("unsafe-target")

class PlatformCredentialBackend(unittest.TestCase):
    @unittest.skipUnless(os.name=="nt","Windows Credential Manager required")
    def test_actual_windows_credential_manager_roundtrip_and_delete(self):
        # Independent GUID-like test target, never the user's production key.
        target=vault.TARGET+"."+secrets.token_hex(10)
        store=vault.WindowsSourceCredentialStore(target)
        try:
            store.clear()
            self.assertIsNone(store.load())
            self.assertFalse(store.status()["configured"])
            self.assertTrue(store.save(INTERNAL)["saved"])
            self.assertTrue(store.status()["configured"])
            self.assertEqual(store.load(),INTERNAL)
            self.assertTrue(store.clear()["deleted"])
            self.assertIsNone(store.load())
        finally:
            store.clear()

    @unittest.skipIf(os.name=="nt","Non-Windows fallback only")
    def test_non_windows_no_plaintext_fallback(self):
        store=vault.WindowsSourceCredentialStore()
        self.assertFalse(store.status()["configured"])
        self.assertIsNone(store.load())
        with self.assertRaisesRegex(vault.CredentialBlocked,
                                     "SOURCE_API_WINDOWS_CREDENTIAL_MANAGER_ONLY"):
            store.save(INTERNAL)
        with self.assertRaises(vault.CredentialBlocked):
            store.clear()

if __name__=="__main__":
    unittest.main()
