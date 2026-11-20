"""v645 explicit SimC path/revision confirm + durable user-local preference.

No real SimC process, internet access, game build downloads or DPS.
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from fastapi.testclient import TestClient

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v645_simc_connection_prefs as prefs
import v113_local_web_api as web


class SimCConnectionPrefs(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        self.exe=self.root/"simc.exe"
        self.exe.write_bytes(b"MZ"+b"mock-cli-file"*900)
        self.store=prefs.LocalSimCConnectionPrefs(self.root/"user-settings")

    def _run(self,output=b"SimulationCraft 12.1.5.70961\n"):
        return mock.Mock(returncode=0,stdout=output,stderr=b"")

    def test_confirm_is_one_nondps_cli_then_saved_and_restored_without_cli(self):
        calls=[]
        def cli(*args,**kw):
            calls.append((args,kw));return self._run()
        result=self.store.confirm(binary=str(self.exe),revision="9933ffb",
                                  run=cli)
        self.assertTrue(result["verified_now"])
        self.assertEqual(result["native_calls_now"],1)
        self.assertEqual(result["dps_native_calls_now"],0)
        self.assertEqual(result["saved"]["observed_game_build"],"12.1.5.70961")
        self.assertEqual(result["saved"]["revision_identity"],
                         "USER_ENTERED_REVISION_NOT_ATTESTED")
        self.assertEqual(len(calls),1)
        self.assertEqual(calls[0][0][0],[str(self.exe),"display_build=2"])
        self.assertEqual(calls[0][1]["timeout"],20)
        restored=self.store.status()
        self.assertFalse(restored["verified_now"])
        self.assertEqual(restored["native_calls_now"],0)
        self.assertEqual(restored["saved"]["binary"],str(self.exe))
        self.assertFalse((self.root/"runs").exists())
        self.assertFalse((self.root/"user-settings"/"runs").exists())

    def test_failure_never_replaces_saved_connection_and_never_reports_unsafe_path(self):
        previous=self.store.confirm(binary=str(self.exe),revision="9933ffb",
                                    run=lambda *a,**kw:self._run())
        saved=(self.root/"user-settings"/prefs.FILE).read_bytes()
        with self.assertRaisesRegex(prefs.SimCConnectionBlocked,
                                    "SIMC_CONNECTION_CLI_SMOKE_FAILED"):
            self.store.confirm(binary=str(self.exe),revision="7bc1071",
                run=lambda *a,**kw:self._run(b"not a simc cli"))
        self.assertEqual((self.root/"user-settings"/prefs.FILE).read_bytes(),saved)
        self.assertEqual(self.store.status()["saved"],previous["saved"])
        with self.assertRaisesRegex(prefs.SimCConnectionBlocked,
                                    "SIMC_CONNECTION_BINARY_NOT_FOUND"):
            self.store.confirm(binary=str(self.root/"not-found.exe"),
                revision="9933ffb",run=lambda *a,**kw:self._run())
        with self.assertRaisesRegex(prefs.SimCConnectionBlocked,
                                    "SIMC_CONNECTION_REVISION_INVALID"):
            self.store.confirm(binary=str(self.exe),revision="not-hex",
                               run=lambda *a,**kw:self._run())
        with self.assertRaisesRegex(prefs.SimCConnectionBlocked,
                                    "SIMC_CONNECTION_REVISION_MISMATCH"):
            self.store.confirm(binary=str(self.exe),revision="9933ffb",
               run=lambda *a,**kw:self._run(
                   b"SimulationCraft build 12.1.5.70961 git revision 7bc1071\n"))

    def test_managed_source_sha_revision_must_match_and_optional_cache_exists(self):
        import hashlib
        digest=hashlib.sha256(self.exe.read_bytes()).hexdigest()
        managed={"active_binary":str(self.exe),
                 "installed":{"sha256":digest,"revision_short":"9933ffb"}}
        okay=self.store.confirm(binary=str(self.exe),revision="9933ffb",
                                managed=managed,run=lambda *a,**kw:self._run())
        self.assertEqual(okay["saved"]["revision_identity"],
                         "MANAGED_LOCAL_ARCHIVE_REVISION_NOT_ATTESTED")
        with self.assertRaisesRegex(prefs.SimCConnectionBlocked,
                                    "SIMC_CONNECTION_MANAGED_REVISION_MISMATCH"):
            self.store.confirm(binary=str(self.exe),revision="7bc1071",
                               managed=managed,run=lambda *a,**kw:self._run())
        with self.assertRaisesRegex(prefs.SimCConnectionBlocked,
                                    "SIMC_CONNECTION_STATIC_CACHE_NOT_FOUND"):
            self.store.confirm(binary=str(self.exe),revision="9933ffb",
                        static_cache=str(self.root/"missing.json"),
                        run=lambda *a,**kw:self._run())

    def test_api_token_origin_and_in_use_lock_and_non_dps_consent(self):
        app=web.create_app(root=self.root/"runs",token="v645-token",
                           update_root=self.root/"managed",update_platform="win32")
        client=TestClient(app,base_url="http://127.0.0.1:8765")
        h={"x-simc-local-token":"v645-token","origin":"http://127.0.0.1:8765"}
        route="/api/v1/simc-connection/confirm"
        payload={"binary":str(self.exe),"revision":"9933ffb","static_cache":""}
        self.assertEqual(client.get("/api/v1/simc-connection/status").status_code,403)
        self.assertEqual(client.post(route,json=payload,
                        headers=h|{"origin":"http://evil.local"}).status_code,403)
        self.assertFalse((self.root/"simc-user-connection.json").exists())
        malformed=client.post(route,json={"binary":str(self.exe),
                    "revision":"secret-value-should-not-echo",
                    "static_cache":""},headers=h)
        self.assertEqual(malformed.status_code,422)
        self.assertNotIn("secret-value-should-not-echo",malformed.text)
        self.assertIsNone(client.get("/api/v1/simc-connection/status",
                                    headers=h).json()["saved"])
        job=mock.Mock();job.poll.return_value=None
        app.state.jobs.children["a"*20]=job
        response=client.post(route,json=payload,headers=h)
        self.assertEqual(response.status_code,409,response.text)
        self.assertEqual(response.json()["detail"]["code"],
                         "ACTIVE_SIMC_JOB_CONNECTION_CHECK_BLOCKED")
        app.state.jobs.children.clear()
        with mock.patch.object(prefs.subprocess,"run",return_value=self._run()):
            response=client.post(route,json=payload,headers=h)
        self.assertEqual(response.status_code,200,response.text)
        self.assertTrue(response.json()["verified_now"])
        self.assertEqual(response.json()["dps_native_calls_now"],0)
        saved=client.get("/api/v1/simc-connection/status",headers=h)
        self.assertEqual(saved.status_code,200)
        self.assertEqual(saved.json()["saved"]["revision"],"9933ffb")
        self.assertFalse(saved.json()["verified_now"])


if __name__=="__main__":
    unittest.main()
