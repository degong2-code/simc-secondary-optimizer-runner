"""v180 P1-C: 26 DPS x five ilvls, real source-first season DB, no Native.

Keep existing 334 key, historical non334 independent sessions and physical-stage
witnesses unchanged. 130 newly supported current-season product plans.
"""
from __future__ import annotations
import json,pathlib,sys,tempfile,unittest
from unittest import mock
from fastapi.testclient import TestClient
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v098_target_user_scenario_bootstrap as bootstrap
import v106_user_session_controller as sessions
import v113_local_web_api as api
import v089_ilvl_chmv_budget_selector as budget

LEVELS=(266,300,321,340,344)

class CurrentSeasonMultiLevelProductOffline(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=pathlib.Path(self.temp.name)
        self.binary=self.root/"no_real_native"
        self.binary.write_bytes(b"V180_NATIVE_ZERO")
        self.rev="7bc10711b5"

    def test_all_26_five_ilvls_true_source_first_budget_and_unique_identity(self):
        registry,_=budget.load_registry()
        observed=set()
        count=0
        with mock.patch.object(bootstrap.entry.durable,"run") as native:
            for level in LEVELS:
                reference=registry["values"][level-266]
                for cls,spec in sessions.SUPPORTED:
                    with self.subTest(ilevel=level,spec=cls+"/"+spec):
                        controls=sessions.standard_controls((cls,spec))
                        controls["ilevel"]=level
                        user=sessions.user_scenario(controls)
                        sid,ident=sessions.session_key(user,self.binary,self.rev,
                            current_season_product=True)
                        self.assertNotIn(sid,observed)
                        observed.add(sid)
                        self.assertEqual(ident["current_season_product"],
                                         "v177_source_first_26_dps_v1")
                        folder=self.root/(cls+"_"+spec+"_"+str(level))
                        planned=bootstrap.build(user,folder,self.binary,self.rev,
                                          current_season_product=True)
                        plan=planned["plan"]
                        self.assertEqual(plan["base_B"],
                            reference["fury_dual_2h" if (cls,spec)==("warrior","fury")
                                      else "general"])
                        self.assertEqual(plan["final_T"],
                            plan["base_B"]+sum(plan["fixed_O"].values()))
                        self.assertEqual(plan["native_limit"],6)
                        self.assertEqual(len(planned["effective_four_tier_slots"]),4)
                        self.assertTrue(planned["current_season_product"])
                        self.assertTrue(planned["non334_physical_simc_not_yet_observed"])
                        self.assertFalse(planned["v176_base_physical_26_of_26_verified"])
                        manifest=json.loads((folder/"manifest.json").read_text("utf8"))
                        self.assertNotIn(bootstrap.entry.STAGE_FIELD,manifest)
                        profile=(folder/"profile.simc").read_text("utf8")
                        allgear=[x for x in profile.splitlines() if ",ilevel=" in x]
                        self.assertGreaterEqual(len(allgear),15)
                        self.assertTrue(all(",ilevel="+str(level) in x
                                            for x in allgear),("unexpected level",cls,spec,level))
                        self.assertFalse((folder/"simc_results").exists())
                        count+=1
            native.assert_not_called()
        self.assertEqual(count,26*len(LEVELS))
        self.assertEqual(len(observed),count)

    def test_same_user_new_level_vs_old_non334_and_334_preserves_seals(self):
        user=sessions.user_scenario(sessions.standard_controls())
        original_key=sessions.session_key(user,self.binary,self.rev,
                                         current_season_product=True)[0]
        first=sessions.store_session(user,self.root/"sessions",self.binary,
                    self.rev,current_season_product=True)
        original=first.joinpath("V106_SESSION_IDENTITY.json").read_bytes()
        user["target"]["ilevel"]=321
        new_key,ident=sessions.session_key(user,self.binary,self.rev,
                                         current_season_product=True)
        old_non334=sessions.session_key(user,self.binary,self.rev,
                                       independent_target_level=True)[0]
        self.assertNotEqual(new_key,original_key)
        self.assertNotEqual(new_key,old_non334)
        self.assertFalse(ident.get("independent_target_level",False))
        self.assertEqual(first.joinpath("V106_SESSION_IDENTITY.json").read_bytes(),
                         original)
        user["target"]["ilevel"]=345
        with self.assertRaisesRegex(sessions.SessionBlocked,
                                    "CURRENT_SEASON_PRODUCT_SCOPE_TARGET_RANGE"):
            sessions.session_key(user,self.binary,self.rev,
                                 current_season_product=True)
        user["target"]["ilevel"]=265
        with self.assertRaisesRegex(sessions.SessionBlocked,
                                    "CURRENT_SEASON_PRODUCT_SCOPE_TARGET_RANGE"):
            sessions.session_key(user,self.binary,self.rev,
                                 current_season_product=True)

    def test_web_non334_plan_two_distinct_levels_and_old_api_mode(self):
        app=api.create_app(root=self.root/"runs",token="v180-test")
        client=TestClient(app,base_url="http://127.0.0.1:8765")
        headers={"x-simc-local-token":"v180-test",
                 "origin":"http://127.0.0.1:8765",
                 "content-type":"application/json"}
        controls=sessions.standard_controls(("warrior","fury"))
        requests=[]
        for level in (321,344):
            controls["ilevel"]=level
            payload={"controls":dict(controls),"binary":str(self.binary),
                     "revision":self.rev,"current_season_product":True}
            with mock.patch.object(api.subprocess,"Popen") as spawn:
                response=client.post("/api/v1/sessions/plan",
                             headers=headers,json=payload)
                spawn.assert_not_called()
            self.assertEqual(response.status_code,200,response.text)
            self.assertTrue(response.json()["plan"]["current_season_product"])
            self.assertTrue(response.json()["plan"]["non334_physical_native_not_yet_observed"])
            self.assertFalse(response.json()["plan"]["v176_26_of_26_base_physical_native"])
            sid=response.json()["session_id"]
            requests.append(sid)
            restored=client.get("/api/v1/sessions/"+sid+"/inputs",headers=headers)
            self.assertEqual(restored.status_code,200,restored.text)
            self.assertTrue(restored.json()["current_season_product"])
            self.assertEqual(restored.json()["user"]["target"]["ilevel"],level)
        self.assertEqual(len(set(requests)),2)
        # Old API clients remain on their original independent non334 path.
        controls["ilevel"]=321
        original=client.post("/api/v1/sessions/plan",headers=headers,json={
            "controls":controls,"binary":str(self.binary),"revision":self.rev})
        self.assertEqual(original.status_code,200,original.text)
        self.assertTrue(original.json()["plan"]["independent_non334_profile"])
        self.assertFalse(original.json()["plan"]["current_season_product"])
        self.assertNotEqual(original.json()["session_id"],requests[0])

if __name__=="__main__":unittest.main()
