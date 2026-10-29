"""P1 non-334 season representative user plans; NO SimC Native calls.

The existing 334 native evidence is never promoted to a different itemlevel.
"""
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
import v106_user_session_controller as sessions
import v113_local_web_api as web

class Non334SourceIndependentProductOffline(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root=pathlib.Path(temp.name)
        self.binary=self.root/"not_actual_simc.exe"
        self.binary.write_bytes(b"V153_NO_NATIVE_REFERENCE_333")
        self.revision="7bc1071"
        self.client=TestClient(web.create_app(root=self.root/"runs",
            token="v153-only"),base_url="http://127.0.0.1:8765")
        self.headers={"x-simc-local-token":"v153-only",
                      "origin":"http://127.0.0.1:8765",
                      "content-type":"application/json"}

    def post(self,key,ilevel=333,final_T=None):
        controls=sessions.standard_controls(key)
        controls["ilevel"]=ilevel
        controls["final_T"]=final_T
        return self.client.post("/api/v1/sessions/plan",
            json={"controls":controls,"binary":str(self.binary),
                  "revision":self.revision},headers=self.headers)

    def test_all_supported_26_dps_plan_non334_without_source_or_native(self):
        self.assertEqual(len(sessions.SUPPORTED),26)
        self.assertNotIn(("evoker","augmentation"),sessions.SUPPORTED)
        with mock.patch.object(web.subprocess,"Popen") as spawn:
            for key in sessions.SUPPORTED:
                with self.subTest(key=key):
                    response=self.post(key)
                    self.assertEqual(response.status_code,200,response.text)
                    obj=response.json()
                    self.assertEqual(obj["native_calls"],0)
                    self.assertTrue(obj["plan"]["independent_non334_profile"])
                    self.assertTrue(obj["plan"]["non334_physical_native_not_yet_observed"])
                    self.assertFalse(obj["plan"]["independent_target334_profile"])
                    folder=self.root/"runs"/obj["session_id"]
                    seal=json.loads((folder/"V106_SESSION_IDENTITY.json").read_text("utf8"))
                    self.assertTrue(seal["independent_target_level"])
                    self.assertNotIn("independent_334",seal)
                    manifest=json.loads((folder/"generated"/"manifest.json").read_text("utf8"))
                    self.assertEqual(manifest["native_limit"],6)
                    profile=(folder/"generated"/"profile.simc").read_text("utf8")
                    self.assertIn("default_actions=1",profile)
                    self.assertIn(",ilevel=333",profile)
                    self.assertNotIn(",ilevel=334",profile)
                    self.assertIn("gear_crit_rating=",profile)
            spawn.assert_not_called()
        self.assertEqual(len(list((self.root/"runs").iterdir())),26)

    def test_four_more_levels_all_26_share_one_profile_pipeline_no_native(self):
        # One bounded matrix catches per-level profile, budget and identity
        # regressions in every supported DPS spec. No 26x Native campaign.
        import v089_ilvl_chmv_budget_selector as budget
        registry,_=budget.load_registry()
        levels=(266,310,331,344)
        seen=set()
        with mock.patch.object(web.subprocess,"Popen") as spawn:
            for level in levels:
                row=registry["values"][level-266]
                for key in sessions.SUPPORTED:
                    with self.subTest(level=level,spec=key):
                        response=self.post(key,level)
                        self.assertEqual(response.status_code,200,response.text)
                        obj=response.json()
                        self.assertEqual(obj["native_calls"],0)
                        plan=obj["plan"]
                        self.assertTrue(plan["independent_non334_profile"])
                        self.assertTrue(plan["non334_physical_native_not_yet_observed"])
                        self.assertEqual(plan["native_limit"],6)
                        expected_B=row["fury_dual_2h"
                                       if key==("warrior","fury") else "general"]
                        self.assertEqual(plan["base_B"],expected_B)
                        self.assertEqual(plan["final_T"],
                                         expected_B+sum(plan["fixed_O"].values()))
                        sid=obj["session_id"]
                        self.assertNotIn(sid,seen)
                        seen.add(sid)
                        folder=self.root/"runs"/sid
                        seal=json.loads((folder/"V106_SESSION_IDENTITY.json")
                                        .read_text("utf8"))
                        self.assertTrue(seal["independent_target_level"])
                        self.assertNotIn("independent_334",seal)
                        manifest=json.loads((folder/"generated"/"manifest.json")
                                            .read_text("utf8"))
                        self.assertEqual(manifest["native_limit"],6)
                        profile=(folder/"generated"/"profile.simc").read_text("utf8")
                        lines=[line for line in profile.splitlines()
                               if ",ilevel=" in line]
                        self.assertGreaterEqual(len(lines),15)
                        self.assertTrue(all(",ilevel="+str(level) in line
                                            for line in lines))
                        self.assertIn("default_actions=1",profile)
            spawn.assert_not_called()
        self.assertEqual(len(seen),26*len(levels))
        self.assertEqual(len(list((self.root/"runs").iterdir())),len(seen))

    def test_non334_manual_T_consumables_and_exact_special_L_reuse_one_path(self):
        # Two different levels, exact slot/ilevel/options and a primary-only
        # diamond switch: synthetic Native-static cache for OFFLINE testing.
        # Never claim these synthetic records prove real SimC item support.
        from tests.test_v062_static_budget_bridge import record
        import v061_scenario_contract as contract
        import v062_static_budget_bridge as static_budget
        import v089_ilvl_chmv_budget_selector as budget
        reference,_=budget.load_registry()
        fixed={"crit_rating":0,"haste_rating":175,
               "mastery_rating":0,"versatility_rating":0}
        item={"slot":"head","item_id":271483,
              "options":{"bonus_id":"13848",
                         "redirected_base_stats":"268231"}}
        cache_paths={}
        seen=set()
        with mock.patch.object(web.subprocess,"Popen") as spawn:
            for level in (331,344):
                with self.subTest(level=level):
                    cache=boot.cache_mod.empty_cache()
                    record(cache,{**item,"ilevel":level},fixed)
                    cache_path=self.root/("synthetic_L_"+str(level)+".json")
                    boot.cache_mod.write_atomic(cache_path,cache)
                    cache_paths[level]=cache_path
                    controls=sessions.standard_controls(("shaman","elemental"))
                    controls["ilevel"]=level
                    controls["final_T"]=reference["values"][level-266]["general"]+100
                    controls["special_items"]=[item]
                    choices=controls["consumable_choices"].copy()
                    choices.update({"food":"royal_roast",
                                    "potion":"lights_potential_2",
                                    "augmentation":"disabled","diamond_id":240967})
                    controls["consumable_choices"]=choices
                    response=self.client.post("/api/v1/sessions/plan",json={
                        "controls":controls,"binary":str(self.binary),
                        "revision":self.revision,
                        "static_cache":str(cache_path)},headers=self.headers)
                    self.assertEqual(response.status_code,200,response.text)
                    output=response.json()
                    self.assertEqual(output["native_calls"],0)
                    self.assertEqual(output["plan"]["final_T"],controls["final_T"])
                    self.assertEqual(output["plan"]["base_B"]+
                                     sum(output["plan"]["fixed_O"].values()),
                                     controls["final_T"])
                    sid=output["session_id"]
                    self.assertNotIn(sid,seen)
                    seen.add(sid)
                    folder=self.root/"runs"/sid
                    cfg=json.loads((folder/"generated"/"scenario.json")
                                   .read_text("utf8"))
                    fillers=json.loads((folder/"generated"/"fillers.json")
                                       .read_text("utf8"))
                    measured=static_budget.compile_static_budget(
                        contract.normalize(cfg),fillers,cache)
                    self.assertEqual(measured["locked_L_when_all_specials_observed"],
                                     fixed)
                    self.assertFalse(measured["missing_special_fixed_static"])
                    profile=(folder/"generated"/"profile.simc").read_text("utf8")
                    self.assertIn("head=",profile)
                    self.assertIn("gem_id=240967",profile)
                    self.assertIn(",ilevel="+str(level),profile)
                    for line in ("food=royal_roast","potion=lights_potential_2",
                                 "augmentation=disabled"):
                        self.assertEqual(profile.splitlines().count(line),1)
                    self.assertTrue(json.loads(
                        (folder/"V106_SESSION_IDENTITY.json").read_text("utf8"))
                        ["independent_target_level"])
            # A valid but WRONG-LEVEL exact cache cannot supply this item L.
            wrong=sessions.standard_controls(("shaman","elemental"))
            wrong["ilevel"]=344
            wrong["special_items"]=[item]
            response=self.client.post("/api/v1/sessions/plan",json={
                "controls":wrong,"binary":str(self.binary),
                "revision":self.revision,
                "static_cache":str(cache_paths[331])},headers=self.headers)
            self.assertEqual(response.status_code,422,response.text)
            self.assertEqual(response.json()["detail"]["code"],
                             "SPECIAL_L_REQUIRES_EXACT_NATIVE_STATIC_VARIANT")
            spawn.assert_not_called()
        self.assertEqual(len(seen),2)

    def test_same_user_333_and_334_have_distinct_seals_and_old_334_unchanged(self):
        key=("mage","fire")
        ordinary=sessions.user_scenario(sessions.standard_controls(key))
        old_key,old_seal=sessions.session_key(ordinary,self.binary,self.revision,
                                             independent_334=True)
        also=sessions.user_scenario(sessions.standard_controls(key))
        also["target"]["ilevel"]=333
        new_key,new_seal=sessions.session_key(also,self.binary,self.revision,
                                             independent_target_level=True)
        self.assertNotEqual(new_key,old_key)
        self.assertTrue(old_seal["independent_334"])
        self.assertNotIn("independent_target_level",old_seal)
        self.assertTrue(new_seal["independent_target_level"])
        self.assertNotIn("independent_334",new_seal)
        self.assertEqual(sessions.session_key(ordinary,self.binary,self.revision,
                          independent_334=True),(old_key,old_seal))
        with self.assertRaisesRegex(sessions.SessionBlocked,
                                    "INDEPENDENT_NON334_USER_SCOPE"):
            sessions.session_key(ordinary,self.binary,self.revision,
                                 independent_target_level=True)
        with self.assertRaisesRegex(sessions.SessionBlocked,
                                    "ONLY_ONE_INDEPENDENT_PROFILE_MODE"):
            sessions.session_key(ordinary,self.binary,self.revision,
                 independent_334=True,independent_target_level=True)

    def test_revised_user_manual_final_T_changes_B_and_remains_separate(self):
        standard=self.post(("shaman","enhancement"),333)
        manual=self.post(("shaman","enhancement"),333,3100)
        self.assertEqual(standard.status_code,200,standard.text)
        self.assertEqual(manual.status_code,200,manual.text)
        a=standard.json()
        z=manual.json()
        self.assertNotEqual(a["session_id"],z["session_id"])
        self.assertEqual(z["plan"]["final_T"],3100)
        self.assertEqual(z["plan"]["base_B"]+sum(z["plan"]["fixed_O"].values()),3100)

    def test_non334_resume_worker_passes_sealed_mode_not_334(self):
        key=("rogue","subtlety")
        controls=sessions.standard_controls(key)
        controls["ilevel"]=333
        user=sessions.user_scenario(controls)
        folder=sessions.store_session(user,self.root/"isolated",self.binary,
                         self.revision,independent_target_level=True)
        recorded=[]
        def mocked_run(*args,**kwargs):
            recorded.append(kwargs)
            return {"native_result":{"status":"BLOCKED_NO_NATIVE_TEST"}}
        with mock.patch.object(sessions.bootstrap,"run",side_effect=mocked_run):
            code=sessions.worker(folder,self.binary,self.revision)
        self.assertEqual(code,3)
        self.assertEqual(len(recorded),1)
        self.assertTrue(recorded[0]["independent_target_level"])
        self.assertNotIn("independent_334",recorded[0])
        self.assertEqual(json.loads((folder/"V106_WORKER_STATE.json").read_text("utf8"))
                         ["status"],"BLOCKED_OR_PARTIAL")

    def test_out_of_range_and_aug_never_promote_or_invoke_native(self):
        for level in (265,345):
            self.assertEqual(self.post(("mage","frost"),level).status_code,422)
        controls=sessions.standard_controls(("evoker","devastation"))
        controls["spec"]="augmentation"
        response=self.client.post("/api/v1/sessions/plan",
            json={"controls":controls,"binary":str(self.binary),
                  "revision":self.revision},headers=self.headers)
        self.assertEqual(response.status_code,422)

if __name__=="__main__":unittest.main()
