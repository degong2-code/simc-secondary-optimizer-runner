"""v206 one source-classified nonCHMV permanent enchant, zero Native tests."""
from __future__ import annotations
import copy,json,pathlib,sys,tempfile,unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v206_nonchmv_eagle_selection as eagle
import v106_user_session_controller as sessions
import v098_target_user_scenario_bootstrap as bootstrap
import v196_current_season_user_catalog as catalog
import v113_local_web_api as web

class EagleFixedBudgetBoundary(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        self.binary=self.root/"fake_simc.exe"
        self.binary.write_bytes(b"FAKE_SIMC_BINARY_DO_NOT_EXECUTE")
        self.controls=sessions.standard_controls(("paladin","retribution"))

    def scenario(self,*,eagle_choice=False,manual=None):
        controls=copy.deepcopy(self.controls)
        controls["final_T"]=manual
        if eagle_choice:controls["enchant_choices"]={"finger1":7967}
        return sessions.user_scenario(controls)

    def build(self,user,name):
        folder=self.root/name
        staged=bootstrap.build(user,folder,self.binary,"710c2408bf",
                                current_season_product=True)
        return staged,folder

    def test_proven_source_and_two_native_window_scope(self):
        p=eagle.evidence()
        self.assertEqual(p["static_CHMV_E"],eagle.E_ZERO)
        self.assertEqual(p["native_new_calls"],2)
        source=eagle.source()
        self.assertEqual(source["enchant_id"],7967)
        self.assertEqual(source["token"],"enchant_ring__eyes_of_the_eagle")
        choice=eagle.check_choice({"finger1":7967})
        self.assertEqual(choice["effect_family"],"crit_effectiveness")
        self.assertEqual(choice["static_CHMV_E"],eagle.E_ZERO)

    def test_selected_profile_changes_but_B_T_dont_and_session_rekeys(self):
        base=self.scenario()
        changed=self.scenario(eagle_choice=True)
        self.assertNotIn(eagle.FIELD,base)
        a,old=self.build(base,"baseline")
        b,new=self.build(changed,"enchanted")
        self.assertEqual((a["plan"]["base_B"],a["plan"]["final_T"]),(3150,3182))
        self.assertEqual((b["plan"]["base_B"],b["plan"]["final_T"]),(3150,3182))
        self.assertEqual(a["plan"]["budget_source"],"OPT_IN_ILVL_REFERENCE_BASE_B")
        self.assertEqual(b["plan"]["budget_source"],"OPT_IN_ILVL_REFERENCE_BASE_B")
        self.assertEqual(b["plan"]["selected_nonchmv_enchant"]["static_CHMV_E"],eagle.E_ZERO)
        profile0=(old/"profile.simc").read_text("utf8")
        profile1=(new/"profile.simc").read_text("utf8")
        self.assertNotIn("enchant_id=7967",profile0)
        self.assertIn("enchant_id=7967",profile1)
        self.assertNotEqual(a["plan"]["source_profile_sha256"],
                            b["plan"]["source_profile_sha256"])
        self.assertNotEqual(a["plan"]["scenario_digest"],
                            b["plan"]["scenario_digest"])
        k0,_=sessions.session_key(base,self.binary,"710c2408bf",current_season_product=True)
        k1,_=sessions.session_key(changed,self.binary,"710c2408bf",current_season_product=True)
        self.assertNotEqual(k0,k1)
        self.assertEqual(b["native_calls"],0)

    def test_manual_inclusive_T_remains_authoritative(self):
        user=self.scenario(eagle_choice=True,manual=4000)
        staged,_=self.build(user,"manual4000")
        self.assertEqual(staged["plan"]["final_T"],4000)
        self.assertEqual(staged["plan"]["base_B"],3968)
        self.assertEqual(staged["plan"]["budget_source"],
                         "USER_MANUAL_FINAL_INCLUDING_OIL")

    def test_other_or_malformed_enchant_never_admitted(self):
        for bad in ({"finger1":8025},{"finger2":7967},{},
                    {"finger1":7967,"finger2":7967},{"finger1":"7967"}):
            with self.subTest(bad=bad),self.assertRaises(eagle.EnchantChoiceBlocked):
                eagle.check_choice(bad)
        invalid=copy.deepcopy(self.controls)
        invalid["verified_enchant"]={"finger1":8025}
        with self.assertRaisesRegex(sessions.SessionBlocked,"USER_INPUT_FIELDS"):
            sessions.user_scenario(invalid)

    def test_native_evidence_absent_fails_closed_and_38_catalog_remains(self):
        with patch.object(eagle,"PROOF",self.root/"missing.json"):
            with self.assertRaises(OSError):
                eagle.check_choice({"finger1":7967})
            rows=catalog.public_options()["enchant_candidates"]
            self.assertEqual(rows["total"],38)
            self.assertEqual(rows["selectable_count"],0)
            self.assertTrue(all(not x["ui_selectable"] for x in rows["items"]))

    def test_conflicting_special_finger1_rejected_before_enchant_mutation(self):
        rows={"finger1":{"item_id":158366,"ilevel":334,"options":{}}}
        user={"special_items":[{"slot":"finger1","item_id":158366,"options":{}}],
              "embellishments":[]}
        def need(ok,reason):
            if not ok:raise ValueError(reason)
        with self.assertRaisesRegex(ValueError,"OVERLAPS_SELECTED_SPECIAL"):
            eagle.apply(rows,{"finger1":7967},user,
                        current_season_product=True,need_user=need)
        self.assertEqual(rows["finger1"]["options"],{})
        with self.assertRaisesRegex(ValueError,"ONLY_CURRENT_SEASON"):
            eagle.apply(rows,{"finger1":7967},
                        {"special_items":[],"embellishments":[]},
                        current_season_product=False,need_user=need)

    def test_real_local_http_plan_rejects_bad_and_no_native(self):
        api=web.create_app(root=self.root/"runs",token="v206-test-token")
        client=TestClient(api,base_url="http://127.0.0.1:8765")
        headers={"x-simc-local-token":"v206-test-token",
                 "origin":"http://127.0.0.1:8765"}
        controls=copy.deepcopy(self.controls)
        controls["enchant_choices"]={"finger1":7967}
        payload={"controls":controls,"binary":str(self.binary),
                 "revision":"710c2408bf","static_cache":None,
                 "current_season_product":True}
        r=client.post("/api/v1/sessions/plan",headers=headers,json=payload)
        self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(r.json()["plan"]["base_B"],3150)
        self.assertEqual(r.json()["plan"]["final_T"],3182)
        self.assertEqual(r.json()["native_calls"],0)
        sid=r.json()["session_id"]
        restored=client.get("/api/v1/sessions/"+sid+"/inputs",headers=headers)
        self.assertEqual(restored.json()["user"][eagle.FIELD],eagle.CHOICE)
        wrong=copy.deepcopy(payload)
        wrong["controls"]["enchant_choices"]={"finger1":8025}
        bad=client.post("/api/v1/sessions/plan",headers=headers,json=wrong)
        self.assertEqual(bad.status_code,422)
        self.assertEqual(bad.json()["detail"]["code"],
                         "ONLY_VERIFIED_EAGLE_FINGER1_NONCHMV_SELECTION")
        legacy=copy.deepcopy(payload);legacy["current_season_product"]=False
        blocked=client.post("/api/v1/sessions/plan",headers=headers,json=legacy)
        self.assertEqual(blocked.status_code,422)

    def test_ui_catalog_only_one_and_rest_locked(self):
        c=catalog.public_options()
        e=c["enchant_candidates"]
        self.assertEqual(e["total"],38)
        self.assertEqual(e["selectable_count"],1)
        self.assertEqual([x["enchant_id"] for x in e["items"]
                           if x["ui_selectable"]],[7967])
        self.assertTrue(c["new_approval_granted"])

if __name__=="__main__":unittest.main()
