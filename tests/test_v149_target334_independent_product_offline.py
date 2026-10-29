"""P1: 24 real-Native-proven archetypes -> ordinary local user flow.

OFFLINE ONLY. Does not simulate actual SimC DPS evidence or promote old v145
physical receipts. Existing source-backed and v147 immutable modes preserved.
"""
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
import v098_target_user_scenario_bootstrap as boot
import v106_user_session_controller as session
import v113_local_web_api as web

class AllTarget334ProductOffline(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root=pathlib.Path(temp.name)
        self.binary=self.root/"simc_fake_not_executable.exe"
        self.binary.write_bytes(b"ZERO_NATIVE_24_SPEC_PRODUCT_PLANS")
        self.revision="7bc1071"
        self.app=web.create_app(root=self.root/"runs",token="v149-offline")
        self.client=TestClient(self.app,base_url="http://127.0.0.1:8765")
        self.headers={"x-simc-local-token":"v149-offline",
                      "origin":"http://127.0.0.1:8765",
                      "content-type":"application/json"}

    def test_each_of_24_without_source_fixtures_plans_independent_profile(self):
        with mock.patch.object(web.subprocess,"Popen") as spawn:
            for key in sorted(boot.ARCHETYPES):
                with self.subTest(key=key):
                    controls=session.standard_controls(key)
                    data={"controls":controls,"binary":str(self.binary),
                          "revision":self.revision}
                    response=self.client.post("/api/v1/sessions/plan",json=data,
                                              headers=self.headers)
                    self.assertEqual(response.status_code,200,response.text)
                    item=response.json()
                    self.assertTrue(item["plan"]["independent_target334_profile"])
                    folder=self.root/"runs"/item["session_id"]
                    identity=json.loads(
                        (folder/"V106_SESSION_IDENTITY.json").read_text("utf8"))
                    self.assertIs(identity["independent_334"],True)
                    manifest=json.loads(
                        (folder/"generated"/"manifest.json").read_text("utf8"))
                    self.assertNotIn(boot.entry.STAGE_FIELD,manifest)
                    profile=(folder/"generated"/"profile.simc").read_text("utf8")
                    self.assertIn("default_actions=1",profile)
                    self.assertIn("gear_crit_rating=",profile)
                    self.assertTrue(item["plan"]["base_B"]>0)
                    self.assertEqual(item["native_calls"],0)
            spawn.assert_not_called()
        self.assertEqual(len(list((self.root/"runs").iterdir())),24)

    def test_legacy_same_input_identity_is_not_reused(self):
        key=("mage","frost")
        u=session.user_scenario(session.standard_controls(key))
        old_key,old_identity=session.session_key(
            u,self.binary,self.revision)
        new_key,new_identity=session.session_key(
            u,self.binary,self.revision,independent_334=True)
        self.assertNotEqual(old_key,new_key)
        self.assertNotIn("independent_334",old_identity)
        self.assertTrue(new_identity["independent_334"])
        self.assertEqual(session.session_key(u,self.binary,self.revision),
                         (old_key,old_identity))
        with mock.patch.object(web.subprocess,"Popen") as spawn:
            response=self.client.post("/api/v1/sessions/plan",
                json={"controls":session.standard_controls(key),
                      "binary":str(self.binary),"revision":self.revision},
                headers=self.headers)
            spawn.assert_not_called()
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()["session_id"],new_key)

    def test_change_ilevel_or_gear_mode_does_not_repoint_native_receipt(self):
        u=session.user_scenario(session.standard_controls(("mage","frost")))
        u["target"]["ilevel"]=333
        with self.assertRaisesRegex(session.SessionBlocked,
                                    "INDEPENDENT_334_USER_SCOPE"):
            session.session_key(u,self.binary,self.revision,independent_334=True)
        with self.assertRaisesRegex(boot.UserScenarioBlocked,
                                    "INDEPENDENT_334_USER_SCOPE"):
            boot.build(u,self.root/"bad",self.binary,self.revision,
                       independent_334=True)
        old=session.session_key(u,self.binary,self.revision)[0]
        self.assertNotIn("independent_334",session.session_key(
            u,self.binary,self.revision)[1])
        self.assertEqual(len(old),20)

    def test_no_new_optimizer_engine_and_no_physical_witness_needed_for_user_job(self):
        user=session.user_scenario(
            session.standard_controls(("shaman","enhancement")))
        path=self.root/"user.json"
        path.write_text(session.canonical(user))
        stage=self.root/"stage"
        original=boot.entry.run_manifest
        calls=[]
        def skip_native(manifest,**kwargs):
            if kwargs.get("plan_only"):
                return original(manifest,**kwargs)
            calls.append((manifest,kwargs))
            return {"status":"PASS_BOUNDED_GENERIC_NATIVE_SEARCH_AND_CACHE",
                    "new_native_attempts_cumulative":0}
        with mock.patch.object(boot.entry,"run_manifest",
                               side_effect=skip_native):
            result=boot.run(path,stage,self.binary,self.revision,execute=True,
                            independent_334=True,open_folder=False)
        self.assertEqual(len(calls),1)
        self.assertFalse(calls[0][1].get("physical_acceptance_root"))
        self.assertFalse(calls[0][1].get("plan_only",False))
        self.assertEqual(result["native_result"]["status"],
                         "PASS_BOUNDED_GENERIC_NATIVE_SEARCH_AND_CACHE")
        self.assertFalse(json.loads((stage/"manifest.json").read_text())
                         .get(boot.entry.STAGE_FIELD,False))

if __name__=="__main__":
    unittest.main()
