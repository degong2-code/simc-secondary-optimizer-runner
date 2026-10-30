"""v177 product opt-in, current-season snapshot identity, web and v094 route.

Only offline plans/mocked worker. No Native SimC in this test.
"""
from __future__ import annotations
import copy,json,pathlib,sys,tempfile,unittest
from unittest import mock
from fastapi.testclient import TestClient

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v098_target_user_scenario_bootstrap as bootstrap
import v106_user_session_controller as sessions
import v113_local_web_api as web
import v096_unified_product_entry as entry
import v169_source_first_representative_stage as first
from tests.test_v106_user_session_controller import fake_native

class CurrentSeasonProductIntegration(unittest.TestCase):
    def setUp(self):
        temporary=tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root=pathlib.Path(temporary.name)
        self.binary=self.root/"simc-not-real"
        self.binary.write_bytes(b"DO_NOT_RUN_SIMC")
        self.rev="7bc10711b5"

    def user(self,spec=("paladin","retribution")):
        controls=sessions.standard_controls(spec)
        return sessions.user_scenario(controls)

    def test_new_26_product_plans_no_native_and_original_v094_manifest(self):
        for key in sessions.SUPPORTED:
            with self.subTest(spec=key):
                u=self.user(key)
                with mock.patch.object(bootstrap.entry.durable,"run") as native:
                    result=bootstrap.build(u,self.root/("p_"+"/".join(key).replace("/","_")),
                              self.binary,self.rev,current_season_product=True)
                    native.assert_not_called()
                self.assertEqual(result["status"],"READY_INTERNAL_MANIFEST_ZERO_NATIVE")
                self.assertEqual(result["plan"]["class"],key[0])
                self.assertEqual(result["plan"]["spec"],key[1])
                self.assertEqual(result["plan"]["native_limit"],6)
                self.assertEqual(len(result["effective_four_tier_slots"]),4)
                self.assertTrue(result["current_season_product"])
                manifest=json.loads(pathlib.Path(result["generated_manifest"]).read_text())
                self.assertNotIn(entry.STAGE_FIELD,manifest)
                self.assertEqual(manifest["native_limit"],6)
                self.assertEqual(manifest["scouts"],1)
                self.assertEqual(manifest["material_scouts"],1)
        self.assertEqual(len(sessions.SUPPORTED),26)

    def test_separate_snapshot_bound_session_and_immutable_default(self):
        u=self.user()
        default=sessions.store_session(u,self.root/"runs",self.binary,self.rev)
        first_folder=sessions.store_session(u,self.root/"runs",self.binary,
                  self.rev,current_season_product=True)
        self.assertNotEqual(default,first_folder)
        self.assertEqual(first_folder,
           sessions.store_session(u,self.root/"runs",self.binary,self.rev,
                         current_season_product=True))
        original=json.loads((default/"V106_SESSION_IDENTITY.json").read_text())
        changed=json.loads((first_folder/"V106_SESSION_IDENTITY.json").read_text())
        self.assertNotIn("current_season_product",original)
        self.assertEqual(changed["current_season_product"],
                         "v177_source_first_26_dps_v1")
        for k in ("current_season_gear_sha256","current_season_tier_sha256",
                  "current_season_budget_sha256","source_first_base_catalog_sha256"):
            self.assertEqual(len(changed[k]),64)
        # A different season DB identity must produce a new session, no cache alias.
        changed_db=self.root/"changed_season_db.json"
        changed_db.write_bytes(b"NEW_SEASON_BYTES")
        with mock.patch.object(sessions.bootstrap.source_first.gear,
                               "DEFAULT",changed_db):
            other,_=sessions.session_path(u,self.root/"runs",
                        self.binary,self.rev,current_season_product=True)
        self.assertNotEqual(other,first_folder)
        self.assertEqual(json.loads((default/"V106_SESSION_IDENTITY.json").read_text()),
                         original)

    def test_non334_season_is_separate_and_never_unseals_old_pure_stage(self):
        u=self.user()
        default,_=sessions.session_path(u,self.root,self.binary,self.rev,
                                        current_season_product=True)
        u["target"]["ilevel"]=333
        new=sessions.store_session(u,self.root,self.binary,self.rev,
                                   current_season_product=True)
        self.assertNotEqual(new,default)
        result=bootstrap.build(u,self.root/"new333",self.binary,self.rev,
                               current_season_product=True)
        self.assertEqual(result["plan"]["native_limit"],6)
        self.assertTrue(result["non334_physical_simc_not_yet_observed"])
        self.assertNotIn(entry.STAGE_FIELD,
                         json.loads((self.root/"new333"/"manifest.json").read_text()))
        u["target"]["ilevel"]=334
        with self.assertRaisesRegex(bootstrap.UserScenarioBlocked,
                                    "SOURCE_FIRST_STAGE_AND_PRODUCT_ARE_EXCLUSIVE"):
            bootstrap.build(u,self.root/"bad",self.binary,self.rev,
                            current_season_product=True,source_first_stage=True,
                            pure_stage=True)

    def test_existing_worker_routes_prod_optin_through_bootstrap_without_new_engine(self):
        u=self.user()
        folder=sessions.store_session(u,self.root/"runs",self.binary,self.rev,
                                     current_season_product=True)
        simulated={"native_result":fake_native()}
        with mock.patch.object(sessions.bootstrap,"run",return_value=simulated) as executor:
            self.assertEqual(sessions.worker(folder,self.binary,self.rev),0)
            self.assertEqual(executor.call_count,1)
            self.assertIs(executor.call_args.kwargs["current_season_product"],True)
            self.assertIs(executor.call_args.kwargs["execute"],True)
            self.assertNotIn("pure_stage",executor.call_args.kwargs)
        self.assertEqual(json.loads(sessions.paths(folder)["final"].read_text())["base_B"],3150)
        sessions.request_cancel(folder)
        self.assertTrue(sessions.paths(folder)["cancel"].is_file())
        sessions.clear_cancel(folder)
        self.assertFalse(sessions.paths(folder)["cancel"].exists())

    def test_local_http_user_choice_and_restore_existing_session_mode(self):
        app=web.create_app(root=self.root/"web",token="v177-offline-token")
        client=TestClient(app,base_url="http://127.0.0.1:8765")
        headers={"x-simc-local-token":"v177-offline-token",
                 "origin":"http://127.0.0.1:8765",
                 "content-type":"application/json"}
        user=sessions.standard_controls()
        payload={"controls":user,"binary":str(self.binary),
                 "revision":self.rev,"static_cache":None}
        p=client.post("/api/v1/sessions/plan",headers=headers,json=payload)
        self.assertEqual(p.status_code,200,p.text)
        original_id=p.json()["session_id"]
        enabled=dict(payload,current_season_product=True)
        with mock.patch.object(web.subprocess,"Popen") as proc:
            r=client.post("/api/v1/sessions/plan",headers=headers,json=enabled)
            proc.assert_not_called()
        self.assertEqual(r.status_code,200,r.text)
        new_id=r.json()["session_id"]
        self.assertNotEqual(original_id,new_id)
        self.assertTrue(r.json()["plan"]["current_season_product"])
        self.assertEqual(r.json()["native_calls"],0)
        assert r.json()["plan"]["native_limit"]==6
        restored=client.get("/api/v1/sessions/"+new_id+"/inputs",headers=headers)
        self.assertEqual(restored.status_code,200,restored.text)
        self.assertIs(restored.json()["current_season_product"],True)
        restored_default=client.get("/api/v1/sessions/"+original_id+"/inputs",headers=headers)
        self.assertIs(restored_default.json()["current_season_product"],False)
        non334=dict(enabled,controls={**user,"ilevel":333})
        valid=client.post("/api/v1/sessions/plan",headers=headers,json=non334)
        self.assertEqual(valid.status_code,200,valid.text)
        self.assertNotEqual(valid.json()["session_id"],new_id)
        self.assertTrue(valid.json()["plan"]["non334_physical_native_not_yet_observed"])
        self.assertFalse(valid.json()["plan"]["v176_26_of_26_base_physical_native"])
        html=client.get("/",headers=headers).text
        self.assertIn('id="current_season_product" type="checkbox" checked',html)
        script=client.get("/assets/app.js",headers=headers).text
        self.assertIn("current_season_product:currentSeason",script)
        self.assertIn('$("current_season_product").checked=true',script)
        self.assertIn('$("current_season_product").checked=payload.current_season_product===true',script)
        self.assertIn('$("ilevel").addEventListener("change",showRepresentativeScope)',script)

if __name__=="__main__":unittest.main()
