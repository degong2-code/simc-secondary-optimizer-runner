"""v570: execute the real CI-only credential adapter without Selenium or Native.

The Windows production credential store is unchanged.  This focused test
ensures that the real browser's initial read-only credential-status route
never throws because the v570 environment-only adapter omitted an API method.
"""
from __future__ import annotations

import ast
import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

from fastapi.testclient import TestClient

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v113_local_web_api as web

SOURCE=ROOT/"integration_probes/p1_v570_real_windows_cold_browser_to_simc_once.py"
KEYS=("BLIZZARD_CLIENT_ID","BLIZZARD_CLIENT_SECRET",
      "WCL_CLIENT_ID","WCL_CLIENT_SECRET")


def actual_adapter():
    # Parse only the exact class from the original experiment to avoid
    # importing Selenium and any real source probe side effects.
    tree=ast.parse(SOURCE.read_text(encoding="utf8"))
    cls=next(node for node in tree.body if
             isinstance(node,ast.ClassDef) and node.name=="SourceCredentials")
    isolated=ast.fix_missing_locations(ast.Module(body=[cls],type_ignores=[]))
    scope={"os":os,"REQUIRED_SECRETS":KEYS}
    exec(compile(isolated,str(SOURCE),"exec"),scope)
    return scope["SourceCredentials"]


class ActualV570CredentialAdapter(unittest.TestCase):
    def test_read_only_status_does_not_export_values(self):
        adapter=actual_adapter()
        dummy={key:"SYNTHETIC_VALUE_NOT_A_REAL_SECRET" for key in KEYS}
        with mock.patch.dict(os.environ,dummy):
            auth=adapter()
            self.assertEqual(auth.status(),{"supported":True,"configured":True})
            self.assertEqual(auth.load(),dummy)
            self.assertNotIn(dummy[KEYS[0]],str(auth.status()))
        with mock.patch.dict(os.environ,{key:"" for key in KEYS}):
            self.assertEqual(adapter().status(),
                             {"supported":True,"configured":False})
            self.assertIsNone(adapter().load())

    def test_original_local_api_bootstrap_status_offline(self):
        adapter=actual_adapter()
        dummy={key:"SYNTHETIC_VALUE_NOT_A_REAL_SECRET" for key in KEYS}
        with tempfile.TemporaryDirectory(prefix="v570-status-offline-") as tmp:
            app=web.create_app(root=tmp,token="v570-offline-token",
                               source_credential_store=adapter())
            with mock.patch.dict(os.environ,dummy):
                with TestClient(app,base_url="http://127.0.0.1:8765") as client:
                    result=client.get("/api/v1/source-credentials/status",
                        headers={"x-simc-local-token":"v570-offline-token",
                                 "origin":"http://127.0.0.1:8765"})
                self.assertEqual(result.status_code,200,result.text)
                self.assertEqual(result.json(),
                    {"supported":True,"configured":True})
                self.assertNotIn(dummy[KEYS[0]],result.text)


if __name__=="__main__":
    unittest.main()
