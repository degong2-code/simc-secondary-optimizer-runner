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
        "options":{"bonus_id":"13848","redirected_base_stats":"271876"}}]
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
        self.assertIn("redirected_base_stats=271876",line)
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
            receipt=first["start_receipt"]
            self.assertEqual(receipt["schema"],
                             "v208_selected_special_start_receipt_v1")
            self.assertEqual(receipt["native_calls_this_start"],1)
            self.assertEqual(receipt["cache_summary"],
                             {"hits":0,"misses":1,"native_calls_this_start":1})
            self.assertEqual(receipt["selected_specials"][0]["cache_status"],
                             "MISS_NEW_NATIVE_JSON2")
            self.assertEqual(receipt["selected_specials"][0]["measured_L"],
                             {"crit_rating":0,"haste_rating":175,
                              "mastery_rating":0,"versatility_rating":0})
            self.assertEqual(receipt["selected_specials"][0]["native_json2"]["sha256"],
                             first["native_json2_sha256"])
            self.assertEqual(receipt["receipt_sha256"],
                hydrate.sha(hydrate.canonical({k:v for k,v in receipt.items()
                                               if k!="receipt_sha256"})))
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
            self.assertEqual(again["start_receipt"]["cache_summary"],
                             {"hits":1,"misses":0,"native_calls_this_start":0})
            self.assertEqual(again["start_receipt"]["selected_specials"][0]
                             ["cache_status"],"HIT")
            self.assertEqual(again["start_receipt"]["selected_specials"][0]
                             ["native_json2"]["sha256"],
                             receipt["selected_specials"][0]["native_json2"]["sha256"])

    def test_verified_environment_probe_uses_same_source_preview_and_cache(self):
        staged=hydrate.bootstrap.build(
            self.user,self.root/"unwritten",self.binary,"710c2408bf",
            static_special_probe_only=True,current_season_product=True)
        env={"normal_build_entry":True,"zero_history_build":{"environment_ready":True}}
        controls={"test":"same installed controls"}
        with (mock.patch.object(hydrate.bootstrap,"preview_from_environment_build",
                                return_value=staged) as preview,
              mock.patch.object(hydrate.bootstrap,"build",
                                side_effect=AssertionError("legacy probe used")),
              mock.patch.object(hydrate.subprocess,"run",side_effect=self.fake_native)):
            first=hydrate.hydrate(self.user,self.root/"runs",self.binary,
                "710c2408bf",environment_result=env,season_controls=controls)
            again=hydrate.hydrate(self.user,self.root/"runs",self.binary,
                "710c2408bf",existing=first["static_cache_path"],
                environment_result=env,season_controls=controls)
        self.assertEqual(self.calls,1)
        self.assertEqual(again["native_new_calls"],0)
        self.assertEqual(preview.call_count,2)
        self.assertIs(preview.call_args.kwargs["environment_result"],env)
        self.assertIs(preview.call_args.kwargs["season_controls"],controls)
        self.assertTrue(preview.call_args.kwargs["static_special_probe_only"])

    def test_verified_changed_G_variants_share_two_batches_then_zero(self):
        staged=hydrate.bootstrap.build(
            self.user,self.root/"unwritten",self.binary,"710c2408bf",
            static_special_probe_only=True,current_season_product=True)
        final=staged["special_rows"][0]
        before={**final,"item_id":271876,"options":{}}
        staged["changed_G_rows"]={"before":[before],"after":[final]}
        observed=[]
        def native(cmd,**kwargs):
            physical=pathlib.Path(cmd[1]).read_text("utf8")
            line=next(x for x in physical.splitlines() if x.startswith("chest="))
            encoded=line.split("=",1)[1]
            _,opts=cache.parse_encoded(encoded)
            iid=int(opts["id"]);observed.append(iid)
            self.assertIn(iid,(271486,271876))
            self.assertNotIn("gear_crit_rating=",physical)
            target=pathlib.Path(next(x.split("=",1)[1] for x in
                physical.splitlines() if x.startswith("json2=")))
            target.write_text(json.dumps({"report_version":"2.0.0",
                "git_revision":"710c2408bf","sim":{"players":[{"gear":{
                    "chest":{"ilevel":331,"encoded_item":encoded,
                    "haste_rating":175 if iid==271486 else 130}}}]}}),encoding="utf8")
            return FakeNativeCompleted()
        env={"normal_build_entry":True,"zero_history_build":{"environment_ready":True}}
        with (mock.patch.object(hydrate.bootstrap,"preview_from_environment_build",
                                return_value=staged),
              mock.patch.object(hydrate.subprocess,"run",side_effect=native)):
            first=hydrate.hydrate(self.user,self.root/"runs",self.binary,
                "710c2408bf",environment_result=env)
            path=pathlib.Path(first["static_cache_path"]);oldbytes=path.read_bytes()
            again=hydrate.hydrate(self.user,self.root/"runs",self.binary,
                "710c2408bf",existing=path,environment_result=env)
        self.assertEqual(observed,[271486,271876])
        self.assertEqual(first["native_new_calls"],1)
        self.assertEqual(first["selected_G_delta_native_calls"],1)
        self.assertEqual(first["selected_static_native_calls"],2)
        self.assertEqual(again["selected_static_native_calls"],0)
        self.assertEqual(again["cache_reused"],1)
        self.assertEqual(again["static_cache_path"],str(path))
        self.assertEqual(path.read_bytes(),oldbytes)
        self.assertEqual(len(cache.load(path)["variants"]),2)

    def test_crafted_only_fresh_delta_two_batches_then_cache_zero_L(self):
        # Exercise existing batch/receipt owner using exact physical
        # source fixture, with no special slots. Native remains mocked.
        staged=hydrate.bootstrap.build(
            self.user,self.root/"unwritten",self.binary,"710c2408bf",
            static_special_probe_only=True,current_season_product=True)
        final=staged["special_rows"][0]
        before={**final,"item_id":271876,"options":{}}
        staged["special_rows"]=[]
        staged["changed_G_rows"]={"before":[before],"after":[final]}
        crafted={**self.user,"special_items":[],
                 "embellishments":[{"slot":"chest","item_id":271486}]}
        observed=[]
        def native(cmd,**kwargs):
            physical=pathlib.Path(cmd[1]).read_text("utf8")
            line=next(x for x in physical.splitlines() if x.startswith("chest="))
            encoded=line.split("=",1)[1]
            _,opts=cache.parse_encoded(encoded)
            iid=int(opts["id"]);observed.append(iid)
            target=pathlib.Path(next(x.split("=",1)[1] for x in
                physical.splitlines() if x.startswith("json2=")))
            target.write_text(json.dumps({"report_version":"2.0.0",
                "git_revision":"710c2408bf","sim":{"players":[{"gear":{
                    "chest":{"ilevel":331,"encoded_item":encoded,
                    "haste_rating":175 if iid==271486 else 130}}}]}}),encoding="utf8")
            return FakeNativeCompleted()
        env={"normal_build_entry":True,"zero_history_build":{"environment_ready":True}}
        with (mock.patch.object(hydrate.bootstrap,"preview_from_environment_build",
                                return_value=staged),
              mock.patch.object(hydrate.subprocess,"run",side_effect=native)):
            first=hydrate.hydrate(crafted,self.root/"runs",self.binary,
                "710c2408bf",environment_result=env)
            again=hydrate.hydrate(crafted,self.root/"runs",self.binary,
                "710c2408bf",existing=first["static_cache_path"],
                environment_result=env)
        self.assertEqual(observed,[271486,271876])
        self.assertEqual(first["native_new_calls"],0)
        self.assertEqual(first["selected_G_delta_native_calls"],2)
        self.assertEqual(first["selected_static_native_calls"],2)
        self.assertEqual(first["start_receipt"]["selected_specials"],[])
        self.assertEqual(first["start_receipt"]["selected_special_count"],0)
        self.assertEqual(again["selected_static_native_calls"],0)
        self.assertEqual(first["static_cache_path"],again["static_cache_path"])
        self.assertEqual(len(cache.load(pathlib.Path(first["static_cache_path"]))["variants"]),2)
        with self.assertRaisesRegex(hydrate.StaticLBlocked,
                                    "EXPLICIT_SELECTED_SPECIAL_REQUIRED"):
            hydrate.hydrate(crafted,self.root/"runs",self.binary,"710c2408bf")

    def test_crafted_only_unchanged_delta_empty_cache_zero_native(self):
        crafted={**self.user,"special_items":[],
                 "embellishments":[{"slot":"chest","item_id":271486}]}
        staged={"schema":"v208_exact_current_special_static_source_v1",
                "native_calls":0,"special_rows":[],"profile":"unused",
                "changed_G_rows":{"before":[],"after":[]}}
        with (mock.patch.object(hydrate.bootstrap,"preview_from_environment_build",
                                return_value=staged),
              mock.patch.object(hydrate.subprocess,"run") as native):
            result=hydrate.hydrate(crafted,self.root/"runs",self.binary,
                "710c2408bf",environment_result={})
        native.assert_not_called()
        self.assertEqual(result["selected_static_native_calls"],0)
        self.assertEqual(result["start_receipt"]["selected_special_count"],0)
        self.assertEqual(cache.load(pathlib.Path(result["static_cache_path"]))["variants"],{})

    def test_verified_probe_without_install_never_falls_back(self):
        env={"normal_build_entry":True,
             "zero_history_build":{"environment_ready":False},
             "source_compilation":{}}
        with mock.patch.object(hydrate.subprocess,"run") as native:
            with self.assertRaisesRegex(hydrate.bootstrap.UserScenarioBlocked,
                                       "STATIC_SPECIAL_PROBE_REQUIRES_VERIFIED_INSTALL"):
                hydrate.hydrate(self.user,self.root/"runs",self.binary,
                    "710c2408bf",environment_result=env)
        native.assert_not_called()

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
        # This test preserves the historical v208 receipt contract with a
        # revision-prefix fixture. v213 package binding is exercised separately
        # with the exact 40-character pinned revision in v181/v113 integration.
        with mock.patch.object(app.state.jobs,"source_catalog_path",
                               return_value=None):
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
                receipt_ref=started.json()["static_L_start_receipt"]
                self.assertEqual(receipt_ref["schema"],
                                 "v208_selected_special_start_receipt_v1")
                receipt_path=self.root/"runs"/sid/receipt_ref["path"]
                receipt=json.loads(receipt_path.read_text("utf8"))
                self.assertEqual(receipt["receipt_sha256"],
                                 receipt_ref["receipt_sha256"])
                self.assertEqual(receipt["native_calls_this_start"],1)
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
                second_receipt=second.json()["static_L_start_receipt"]
                self.assertEqual(second_receipt["native_calls_this_start"],0)
                self.assertNotEqual(second_receipt["receipt_sha256"],
                                    receipt_ref["receipt_sha256"])
                self.assertTrue((self.root/"runs"/sid/second_receipt["path"]).is_file())
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
             "options":{"bonus_id":"13848","redirected_base_stats":"271876"}}
        raw={"report_version":"2.0.0","git_revision":"710c2408bf",
             "sim":{"players":[{"gear":{"chest":{
               "ilevel":331,
               "encoded_item":"chest_bad,id=111111,ilevel=331,source=local,"
                              "bonus_id=13848,redirected_base_stats=271876"
              }}}]}}
        with self.assertRaisesRegex(hydrate.StaticLBlocked,"IDENTITY|MISMATCH"):
            fake(json.dumps(raw).encode(),[row],"710c2408bf")

class MixedSelectedLevelContract(unittest.TestCase):
    def test_optional_selected_level_preserved_and_legacy_shape_unchanged(self):
        controls=user_controls()
        legacy=sessions.user_scenario(controls)
        self.assertNotIn("ilevel",legacy["special_items"][0])
        controls["special_items"][0]["ilevel"]=327
        user=sessions.user_scenario(controls)
        self.assertEqual(user["target"]["ilevel"],331)
        self.assertEqual(user["special_items"][0]["ilevel"],327)
        for invalid in (0,1001,True,"327"):
            controls["special_items"][0]["ilevel"]=invalid
            with self.assertRaises(ValueError):
                sessions.user_scenario(controls)

    def test_mixed_levels_require_exact_explicit_selected_slots(self):
        from v432_selected_4pc_budget_bridge import _final_levels_match_user
        controls=user_controls()
        controls["special_items"][0]["ilevel"]=327
        user=sessions.user_scenario(controls)
        rows={"chest":{"slot":"chest","ilevel":327},
              "head":{"slot":"head","ilevel":331}}
        self.assertTrue(_final_levels_match_user(rows,user,331))
        rows["chest"]["ilevel"]=331
        self.assertFalse(_final_levels_match_user(rows,user,331))
        rows["chest"]["ilevel"]=327
        rows["head"]["ilevel"]=330
        self.assertFalse(_final_levels_match_user(rows,user,331))

class FinalWeaponDirectOilContract(unittest.TestCase):
    def test_direct_oil_scope_final_weapon_only_and_installed_vector(self):
        from v432_selected_4pc_budget_bridge import (
            _verified_direct_oil_for_changed_weapon,SelectedBudgetBlocked)
        oil={"physical_item_id":123,"simc_input_token":"main_hand:test",
             "static_CHMV_vector":{"crit_rating":16,"haste_rating":16,
                                   "mastery_rating":0,"versatility_rating":0}}
        row={"slot":"main_hand","item_id":456,"ilevel":330,"options":{}}
        masks={"equipped_item_class":2,"inventory_type_mask":1<<13,
               "weapon_subclass_mask":1<<7}
        gear={"items":[{"item_id":456,"class_id":2,"subclass_id":7,
                         "inventory_type":13}]}
        inputs={"oil_by_hand":{"main_hand":oil},
                "oil_weapon_scope_source_only":{"main_hand":{
                    "physical_item_id":123,"simc_input_token":"main_hand:test",
                    "masks":masks,"source_min_ilevel":300,
                    "source_max_ilevel":350,"scaled_rating_ilevel":None}}}
        doc={"official_O_physical_source":{"oil_by_hand":{"main_hand":oil}}}
        binding=hydrate.bootstrap._assert_final_season_oil_weapon_scope(
            inputs=inputs,rows={"main_hand":row},gear=gear)
        self.assertEqual(_verified_direct_oil_for_changed_weapon(
            binding,"main_hand",row,doc)["oil"],oil)
        for changed in ({**row,"ilevel":331},{**row,"item_id":457}):
            with self.assertRaises(SelectedBudgetBlocked):
                _verified_direct_oil_for_changed_weapon(binding,"main_hand",changed,doc)
        bad=copy.deepcopy(doc)
        bad["official_O_physical_source"]["oil_by_hand"]["main_hand"]["static_CHMV_vector"]["crit_rating"]=17
        with self.assertRaises(SelectedBudgetBlocked):
            _verified_direct_oil_for_changed_weapon(binding,"main_hand",row,bad)
        inputs["oil_weapon_scope_source_only"]["main_hand"]["scaled_rating_ilevel"]=330
        self.assertEqual(hydrate.bootstrap._assert_final_season_oil_weapon_scope(
            inputs=inputs,rows={"main_hand":row},gear=gear),{})
        with self.assertRaisesRegex(ValueError,"REMEASUREMENT_REQUIRED"):
            hydrate.bootstrap._assert_final_season_oil_weapon_scope(
                inputs=inputs,rows={"main_hand":{**row,"ilevel":331}},gear=gear)

class SelectedMeasuredOilContract(unittest.TestCase):
    def test_final_weapon_measurement_cache_only_and_exact_variant(self):
        import v297_sealed_simc_oil_gear_delta as owner
        weapon={"slot":"main_hand","item_id":456,"ilevel":330,"options":{}}
        oil={"physical_item_id":123,"simc_input_token":"main_hand:test"}
        profile=("warrior=actor\nmain_hand=selected_456,id=456,ilevel=330,source=local\n"
                 "iterations=1000\ngear_crit_rating=400\ntemporary_enchant=main_hand:test\n")
        with mock.patch.object(owner,"measure",return_value={"new_native_calls":0}) as measured:
            owner.measure_final_weapon(stage_root=".",profile=profile,weapon=weapon,
                oil=oil,binary="unused",simc_revision="a"*40,game_build="12.1.5.70961")
            args=measured.call_args.kwargs
            self.assertTrue(args["cache_only"])
            self.assertEqual(args["physical_oil_item_id"],123)
            self.assertEqual(args["target_ilevel"],330)
            self.assertEqual(args["expected_weapon_id"],456)
            self.assertNotIn("gear_crit_rating=",args["source_profile_text"])
            self.assertNotIn("temporary_enchant=",args["source_profile_text"])
            with self.assertRaisesRegex(ValueError,"VARIANT_DRIFT"):
                owner.measure_final_weapon(stage_root=".",profile=profile,
                    weapon={**weapon,"ilevel":331},oil=oil,binary="unused",
                    simc_revision="a"*40,game_build="12.1.5.70961")
            self.assertEqual(measured.call_count,1)

    def test_cache_only_native_miss_has_no_write_or_process(self):
        import v278_sealed_simc_consumable_native_pair as pair
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            with mock.patch.object(pair.subprocess,"run") as native:
                with self.assertRaisesRegex(ValueError,"CACHED_NATIVE_REQUIRED_NO_EXECUTION"):
                    pair.run_case(stage_root=root,profile="warrior=actor\n",
                        source_identity="a"*64,binary=root/"unused",binary_sha256="b"*64,
                        revision="a"*40,variant="baseline",timeout_seconds=1,cache_only=True)
                native.assert_not_called()
            self.assertEqual(list(root.iterdir()),[])

    def test_measured_selected_oil_retargets_only_user_budget(self):
        import v432_selected_4pc_budget_bridge as bridge
        zero={k:0 for k in bridge.STATS}
        old_o={**zero,"crit_rating":16,"haste_rating":16}
        new_o={**zero,"crit_rating":18,"haste_rating":17}
        oil={"physical_item_id":123,"simc_input_token":"main_hand:test",
             "static_CHMV_vector":old_o}
        slots={"head":101,"shoulders":102,"chest":103,"hands":104,"legs":105,
               "main_hand":456}
        base={slot:{"slot":slot,"item_id":iid,"ilevel":334,"options":{}}
              for slot,iid in slots.items()}
        final=copy.deepcopy(base)
        final["main_hand"].update(item_id=457,ilevel=330)
        groups={slot:"tier" for slot in ("head","shoulders","chest","hands")}
        groups["main_hand"]="special"
        user={"target":{"ilevel":334,"final_T":None},"oil_hands":["main_hand"],
              "special_items":[{"slot":"main_hand","item_id":457,
                                "ilevel":330,"options":{}}],"embellishments":[]}
        doc={"game_build":"12.1.5.70961","simc_revision":"a"*40,"target_ilevel":334,
             "manifest_sha256":"b"*64,"source_catalog_manifest_sha256":"c"*64,
             "source_catalog_artifact_sha256":"d"*64,"official_G":1000,
             "official_effective_G":1000,"official_J":92,"official_F":165,
             "official_B":1257,"official_O":old_o,
             "official_O_physical_source":{"oil_by_hand":{"main_hand":oil}},
             "v222_reconciled_budget":{"reference_G":1000,"effective_G":1000,
                "J":92,"F":165,"fixed_O":old_o,"base_B":1257,
                "fixed_L":zero,"fixed_E":zero}}
        original=copy.deepcopy(doc)
        link={"schema":"v098_v191_original_gear_tier_link_v1",
              "status":"ORIGINAL_GEAR_TIER_RAW_SHA_LINKED_PREVIEW_ONLY",
              "raw_source_sha256":{"gear":"e"*64,"tier":"f"*64},
              "source_catalog_manifest_sha256":"c"*64,
              "source_catalog_artifact_sha256":"d"*64}
        scope={"main_hand":{"weapon_id":457,"ilevel":330,"oil":oil,
                            "requires_measurement":True}}
        witness={"main_hand":{"physical_oil_item_id":123,
            "simc_input_token":"main_hand:test","selected_hand":"main_hand",
            "representative_weapon_id":457,"target_ilevel":330,
            "game_build":doc["game_build"],"simc_revision":doc["simc_revision"],
            "binary_sha256":"a"*64,"source_profile_sha256":"b"*64,
            "native_case_receipt_sha256":["c"*64,"d"*64],
            "static_CHMV_vector_unadmitted":new_o}}
        def read_variant(_cache,identity):
            return {"rating":{**zero,"crit_rating":
                    100 if identity["item_id"]==456 else 80},
                    "static_digest":"a"*64}
        with mock.patch.object(bridge.installed_manifest,"verify_fresh_installed_environment"), \
             mock.patch.object(bridge,"_native",side_effect=read_variant):
            kw=dict(baseline_rows=base,final_rows=final,final_groups=groups,
                user=user,class_tier_five={k:v for k,v in slots.items() if k!="main_hand"},
                baseline_slot_ids=slots,installed_document=doc,original_v191_link=link,
                native_cache=cache.empty_cache(),expected_cache_season=cache.SEASON,
                final_direct_oil_binding=scope,final_measured_oil_binding=witness)
            auto=bridge.reconcile(**kw)
            self.assertEqual((auto["base_B"],auto["final_T"]),(1237,1272))
            self.assertEqual(auto["fixed_O"],new_o)
            self.assertEqual(auto["fixed_L_in_G_once"]["crit_rating"],80)
            user["target"]["final_T"]=1300
            manual=bridge.reconcile(**kw)
            self.assertEqual((manual["base_B"],manual["final_T"]),(1265,1300))
            self.assertEqual(doc,original)
            self.assertNotEqual(auto["selected_budget_identity_sha256"],
                                manual["selected_budget_identity_sha256"])
            kw["final_measured_oil_binding"]=None
            with self.assertRaisesRegex(ValueError,"APPLICABILITY_RECHECK_REQUIRED"):
                bridge.reconcile(**kw)

if __name__=="__main__":unittest.main()
