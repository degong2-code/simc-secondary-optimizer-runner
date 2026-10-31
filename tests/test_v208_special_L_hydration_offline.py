"""v208: source-accurate selected special L static hydration, offline fake Native only.

No actual SimC calls: the subprocess is replaced with a JSON2 fixture whose
gear identity MUST agree with the v098 fully generated selected item.
"""
import copy,json,pathlib,sys,tempfile,unittest
from unittest import mock
from fastapi.testclient import TestClient
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v106_user_session_controller as sessions
import v208_internal_exact_special_L_hydrator as hydrate
import v046_static_item_cache as cache
import v113_local_web_api as web

def user_controls():
    c=sessions.standard_controls(("shaman","elemental"))
    c["ilevel"]=331
    c["special_items"]=[{"slot":"chest","item_id":271486,
        "options":{"bonus_id":"13848","redirected_base_stats":"268231"}}]
    return c

class FakeNativeCompleted:
    returncode=0

class OneExactSpecialHydration(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        self.root.joinpath("runs").mkdir()
        self.binary=self.root/"simc.exe"
        self.binary.write_bytes(b"TEST_FAKE_SIMC_NOT_EXECUTABLE")
        self.controls=user_controls()
        self.user=sessions.user_scenario(self.controls)
        self.calls=0

    def fake_native(self,cmd,**kwargs):
        self.calls+=1
        profile=pathlib.Path(cmd[1]).read_text("utf8")
        self.assertIn("iterations=1",profile)
        self.assertNotIn("gear_crit_rating=",profile)
        self.assertEqual(profile.count("json2="),1)
        line=next(x for x in profile.splitlines() if x.startswith("chest="))
        self.assertIn("id=271486",line)
        self.assertIn("ilevel=331",line)
        self.assertIn("bonus_id=13848",line)
        self.assertIn("redirected_base_stats=268231",line)
        result=pathlib.Path(next(x.split("=",1)[1] for x in profile.splitlines()
                                 if x.startswith("json2=")))
        response={"report_version":"2.0.0","git_revision":"710c2408bf",
                  "sim":{"players":[{"gear":{"chest":{
                   "ilevel":331,
                   "encoded_item":line.split("=",1)[1],
                   "crit_rating":0,"haste_rating":175,
                   "mastery_rating":0,"versatility_rating":0}}}]}}
        result.write_text(json.dumps(response),encoding="utf8")
        return FakeNativeCompleted()

    def test_no_cached_exact_L_one_native_snapshot_then_cache_only(self):
        with mock.patch.object(hydrate.subprocess,"run",side_effect=self.fake_native):
            first=hydrate.hydrate(self.user,self.root/"runs",self.binary,"710c2408bf")
            self.assertEqual(first["native_new_calls"],1)
            self.assertEqual(first["observed_selected_variants"],1)
            self.assertEqual(self.calls,1)
            path=pathlib.Path(first["static_cache_path"])
            saved=cache.load(path)
            self.assertEqual(len(saved["variants"]),1)
            self.assertEqual(next(iter(saved["variants"].values()))
                             ["static"]["secondary"]["haste_rating"],175)
            self.assertEqual(hydrate.source_cache(self.root/"runs",None),path)
            oldbytes=path.read_bytes()
            again=hydrate.hydrate(self.user,self.root/"runs",self.binary,
                                   "710c2408bf",existing=path)
            self.assertEqual(again["native_new_calls"],0)
            self.assertEqual(self.calls,1)
            self.assertEqual(oldbytes,path.read_bytes())
            self.assertEqual(again["static_cache_path"],str(path))

    def test_explicit_old_cache_unmodified_one_native_then_new_snapshot(self):
        before=cache.empty_cache()
        legacy=self.root/"static-item-cache.json"
        cache.write_atomic(legacy,before)
        original=legacy.read_bytes()
        with mock.patch.object(hydrate.subprocess,"run",side_effect=self.fake_native):
            result=hydrate.hydrate(self.user,self.root/"runs",
                          self.binary,"710c2408bf",existing=legacy)
        self.assertEqual(result["native_new_calls"],1)
        self.assertEqual(legacy.read_bytes(),original)
        self.assertNotEqual(pathlib.Path(result["static_cache_path"]),legacy)
        self.assertEqual(cache.load(legacy)["variants"],{})

    def test_plain_plan_zero_native_start_hydrates_once_and_replays_same_identity(self):
        app=web.create_app(root=self.root/"runs",token="static-L-token")
        client=TestClient(app,base_url="http://127.0.0.1:8765")
        headers={"x-simc-local-token":"static-L-token",
                 "origin":"http://127.0.0.1:8765"}
        payload={"controls":self.controls,"binary":str(self.binary),
                 "revision":"710c2408bf","current_season_product":True}
        plan=client.post("/api/v1/sessions/plan",headers=headers,json=payload)
        self.assertEqual(plan.status_code,422,plan.text)
        self.assertEqual(self.calls,0)
        self.assertEqual(plan.json()["detail"]["code"],
                         "V106_SPECIAL_EQUIPMENT_REQUIRES_EXACT_STATIC_CACHE")
        with (mock.patch.object(hydrate.subprocess,"run",side_effect=self.fake_native),
              mock.patch.object(web.subprocess,"Popen") as spawned):
            spawned.return_value.poll.return_value=None
            started=client.post("/api/v1/sessions/start",headers=headers,json=payload)
            self.assertEqual(started.status_code,200,started.text)
            self.assertEqual(started.json()["static_L_native_calls_this_start"],1)
            self.assertEqual(started.json()["native_attempt_ceiling_cumulative"],6)
            self.assertEqual(self.calls,1)
            sid=started.json()["session_id"]
            manifest=json.loads((self.root/"runs"/sid/"generated"/"manifest.json")
                               .read_text("utf8"))
            self.assertTrue(manifest["static_cache_json"])
            self.assertTrue(pathlib.Path(manifest["static_cache_json"]).is_file())
            self.assertEqual(started.json()["status"],"WORKER_STARTED")
            # Stop mocked pseudo worker, then the same start is cache-only
            # for static L; DPS subprocess still belongs to original worker.
            spawned.return_value.poll.return_value=0
            second=client.post("/api/v1/sessions/start",headers=headers,json=payload)
            self.assertEqual(second.status_code,200,second.text)
            self.assertEqual(second.json()["static_L_native_calls_this_start"],0)
            self.assertEqual(second.json()["session_id"],sid)
            self.assertEqual(self.calls,1)

    def test_source_listed_cloak_is_unmodified_special_L_variant(self):
        # Fail here (Native zero) if the source composer auto-decorates
        # this special with gem/enchant; exact fixed L cannot be derived
        # from decorated CHMV options without separate evidence.
        controls=copy.deepcopy(self.controls)
        controls["special_items"]=[{"slot":"back","item_id":159288,"options":{}}]
        user=sessions.user_scenario(controls)
        stage=hydrate.bootstrap.build(
            user,self.root/"scope-only",self.binary,"710c2408bf",
            current_season_product=True,static_special_probe_only=True)
        self.assertEqual(stage["native_calls"],0)
        self.assertEqual(len(stage["special_rows"]),1)
        item=stage["special_rows"][0]
        self.assertEqual((item["slot"],item["item_id"],item["ilevel"]),
                         ("back",159288,331))
        self.assertFalse(set(item["options"]) & {"gem_id","enchant",
                          "enchant_id"})

    def test_decorated_special_neck_runs_only_bare_L_and_preserves_full_profile(self):
        import v062_static_budget_bridge as budget
        controls=copy.deepcopy(self.controls)
        controls["special_items"]=[{"slot":"neck","item_id":268250,
                                     "options":{}}]
        user=sessions.user_scenario(controls)
        stage=hydrate.bootstrap.build(
            user,self.root/"neck-source",self.binary,"710c2408bf",
            current_season_product=True,static_special_probe_only=True)
        row=stage["special_rows"][0]
        self.assertIn("gem_id",row["options"])
        original_profile=stage["profile"]
        self.assertIn("gem_id=",next(x for x in original_profile.splitlines()
                                     if x.startswith("neck=")))
        base=budget.undecorated_special(row)
        self.assertNotIn("gem_id",base["options"])
        def simulate_native(cmd,**kwargs):
            self.calls+=1
            physical=pathlib.Path(cmd[1]).read_text("utf8")
            bare_neck=next(x for x in physical.splitlines() if x.startswith("neck="))
            self.assertNotIn("gem_id=",bare_neck)
            self.assertIn("id=268250",bare_neck)
            self.assertIn("ilevel=331",bare_neck)
            self.assertNotIn("gear_crit_rating=",physical)
            path=pathlib.Path(next(x.split("=",1)[1] for x in physical.splitlines()
                                   if x.startswith("json2=")))
            response={"report_version":"2.0.0","git_revision":"710c2408bf",
                     "sim":{"players":[{"gear":{"neck":{
                      "ilevel":331,"encoded_item":bare_neck.split("=",1)[1],
                      "crit_rating":0,"haste_rating":0,
                      "mastery_rating":110,"versatility_rating":20}}}]}}
            path.write_text(json.dumps(response),encoding="utf8")
            return FakeNativeCompleted()
        with mock.patch.object(hydrate.subprocess,"run",side_effect=simulate_native):
            first=hydrate.hydrate(user,self.root/"runs",self.binary,"710c2408bf")
            self.assertEqual(first["native_new_calls"],1)
            self.assertEqual(self.calls,1)
            path=pathlib.Path(first["static_cache_path"])
            snapshot=cache.load(path)
            self.assertIn(cache.digest(budget.exact_identity(base)),snapshot["variants"])
            self.assertNotIn(cache.digest(budget.exact_identity(row)),snapshot["variants"])
            plan=hydrate.bootstrap.build(user,self.root/"neck-plan",self.binary,
                                         "710c2408bf",path,current_season_product=True)
            self.assertEqual(plan["plan"]["base_B"],3110)
            self.assertEqual(plan["plan"]["final_T"],3142)
            self.assertIn("gem_id=", (self.root/"neck-plan"/"profile.simc").read_text())
            self.assertEqual(plan["plan"]["selected_fixed_enchant_E"] if
                             "selected_fixed_enchant_E" in plan["plan"] else None,None)
            self.assertEqual(hydrate.hydrate(
                user,self.root/"runs",self.binary,"710c2408bf",
                existing=path)["native_new_calls"],0)
            self.assertEqual(self.calls,1)

    def test_mismatch_in_temporary_physical_special_source_blocked(self):
        import v062_static_budget_bridge as budget
        controls=copy.deepcopy(self.controls)
        controls["special_items"]=[{"slot":"neck","item_id":268250,"options":{}}]
        user=sessions.user_scenario(controls)
        stage=hydrate.bootstrap.build(
            user,self.root/"neck-source-2",self.binary,"710c2408bf",
            current_season_product=True,static_special_probe_only=True)
        original=stage["special_rows"][0]
        bare=budget.undecorated_special(original)
        with self.assertRaisesRegex(hydrate.StaticLBlocked,
                                    "SOURCE_NOT_EXACT_USER_VARIANT"):
            wrong=stage["profile"].replace("id=268250","id=268251")
            hydrate.physical_input(wrong,self.root/"x.json",[original],[bare])

    def test_forged_native_item_id_or_missing_profile_stats_fail_closed(self):
        fake=hydrate.selected_records
        row={"slot":"chest","item_id":271486,"ilevel":331,
             "options":{"bonus_id":"13848","redirected_base_stats":"268231"}}
        raw={"report_version":"2.0.0","git_revision":"710c2408bf",
             "sim":{"players":[{"gear":{"chest":{
               "ilevel":331,
               "encoded_item":"chest_bad,id=111111,ilevel=331,source=local,"
                              "bonus_id=13848,redirected_base_stats=268231"
              }}}]}}
        with self.assertRaisesRegex(hydrate.StaticLBlocked,"IDENTITY|MISMATCH"):
            fake(json.dumps(raw).encode(),[row],"710c2408bf")

if __name__=="__main__":unittest.main()
