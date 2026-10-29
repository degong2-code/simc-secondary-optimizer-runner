"""P1-WEB-1 FastAPI HTTP boundary; all tests OFFLINE, never execute SimC."""
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
import v113_local_web_api as web
import v106_user_session_controller as sessions
from tests.test_v106_user_session_controller import fake_native

class LocalWebAPIOffline(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        self.binary=self.root/"fake_simc.exe"
        self.binary.write_bytes(b"FAKE_SIMC_BINARY_ZERO_NATIVE")
        self.controls=sessions.standard_controls()
        self.payload={"controls":self.controls,"binary":str(self.binary),
                      "revision":"7bc1071","static_cache":None}
        self.app=web.create_app(root=self.root/"runs",token="offline-only-token")
        self.client=TestClient(self.app,base_url="http://127.0.0.1:8765")
        self.headers={"x-simc-local-token":"offline-only-token",
                      "origin":"http://127.0.0.1:8765"}
        self.postheaders=self.headers|{"content-type":"application/json"}

    def post(self,path,data=None):
        return self.client.post(path,json=data if data is not None else {},
                                headers=self.postheaders)

    def plan(self):
        r=self.post("/api/v1/sessions/plan",self.payload)
        self.assertEqual(r.status_code,200,r.text)
        return r.json()

    def test_bootstrap_health_and_all_26_dps_defaults_no_simc(self):
        health=self.client.get("/api/v1/health")
        self.assertEqual(health.status_code,200)
        self.assertEqual(health.json()["supported_dps"],26)
        boot=self.client.get("/api/v1/bootstrap").json()
        self.assertEqual(boot["session_token"],"offline-only-token")
        self.assertEqual(len(boot["supported"]),26)
        defaults=self.client.get("/api/v1/defaults",headers=self.headers)
        self.assertEqual(defaults.status_code,200)
        status_counts={}
        for row in defaults.json()["archetypes"]:
            self.assertEqual(len(row["trinket_ids"]),2)
            self.assertEqual(row["ilevel"],334)
            self.assertEqual(len(row["consumable_choices"]),6)
            scope=row["representative_scope"]
            status_counts[scope]=status_counts.get(scope,0)+1
            expected=("SOURCE_INDEPENDENT_SEASON_CATALOG"
                      if (row["class"],row["spec"]) in
                          web.bootstrap.PURE_PRODUCT_SPECS
                      else "SOURCE_INDEPENDENT_TARGET334_VALIDATED_BATCH")
            self.assertEqual(scope,expected)
        self.assertEqual(status_counts,{
            "SOURCE_INDEPENDENT_TARGET334_VALIDATED_BATCH":24,
            "SOURCE_INDEPENDENT_SEASON_CATALOG":2})
        self.assertFalse((self.root/"runs").exists())

    def test_web_remains_usable_with_no_legacy_complete_simc_fixtures(self):
        # In a package without the old 24 full SimC source fixtures, the
        # ready/default UI list must still expose both Native-proven pure
        # paths, but may not claim the unavailable legacy paths work.
        original_text=pathlib.Path.read_text
        original_bytes=pathlib.Path.read_bytes
        original_is_file=pathlib.Path.is_file
        seen=[]
        checked=[]
        def is_legacy(path):
            return ("/integration_probes/fixtures/" in
                    str(path).replace(chr(92),"/") and
                    str(path).endswith(".simc"))
        def absent_text(path,*args,**kwargs):
            if is_legacy(path):
                seen.append(str(path))
                raise FileNotFoundError("LEGACY_SOURCE_PROFILE_NOT_INSTALLED")
            return original_text(path,*args,**kwargs)
        def absent_bytes(path,*args,**kwargs):
            if is_legacy(path):
                seen.append(str(path))
                raise FileNotFoundError("LEGACY_SOURCE_PROFILE_NOT_INSTALLED")
            return original_bytes(path,*args,**kwargs)
        def absent_is_file(path,*args,**kwargs):
            if is_legacy(path):
                checked.append(str(path))
                return False
            return original_is_file(path,*args,**kwargs)
        with mock.patch.object(pathlib.Path,"read_text",absent_text), \
             mock.patch.object(pathlib.Path,"read_bytes",absent_bytes), \
             mock.patch.object(pathlib.Path,"is_file",absent_is_file):
            response=self.client.get("/api/v1/defaults",headers=self.headers)
            self.assertEqual(response.status_code,200,response.text)
            data=response.json()
            visible={(r["class"],r["spec"]) for r in data["archetypes"]}
            self.assertEqual(visible,set(sessions.SUPPORTED))
            missing={(r["class"],r["spec"]) for r in
                     data["unavailable_missing_legacy_fixtures"]}
            self.assertEqual(missing,set())
            self.assertEqual(len(checked),0)
            self.assertEqual(seen,[])
            # Character/talent/trinket defaults for all 26 are now
            # available independently; only actual legacy EXECUTION is
            # unavailable when those complete historical files are absent.
            for key in sessions.SUPPORTED:
                source=sessions.standard_controls(key)
                self.assertEqual((source["class"],source["spec"]),key)
            self.assertEqual(seen,[])
            for spec in sorted(visible):
                with self.subTest(spec=spec):
                    payload={**self.payload,
                             "controls":sessions.standard_controls(spec)}
                    with mock.patch.object(web.subprocess,"Popen") as spawn:
                        plan=self.post("/api/v1/sessions/plan",payload)
                        self.assertEqual(plan.status_code,200,plan.text)
                        self.assertEqual(plan.json()["native_calls"],0)
                        spawn.assert_not_called()

    def test_two_pure_local_web_plans_reuse_normal_session_without_native(self):
        for key in sorted(web.bootstrap.PURE_PRODUCT_SPECS):
            with self.subTest(spec=key):
                params={**self.payload,"controls":sessions.standard_controls(key)}
                with mock.patch.object(web.subprocess,"Popen") as spawn:
                    response=self.post("/api/v1/sessions/plan",params)
                    spawn.assert_not_called()
                self.assertEqual(response.status_code,200,response.text)
                body=response.json()
                self.assertEqual(body["plan"]["final_T"],3150)
                folder=self.root/"runs"/body["session_id"]/"generated"
                self.assertIn("default_actions=1",
                              (folder/"profile.simc").read_text())
                self.assertNotIn(web.bootstrap.entry.STAGE_FIELD,
                         json.loads((folder/"manifest.json").read_text()))
                again=self.post("/api/v1/sessions/plan",params)
                self.assertEqual(again.json()["session_id"],body["session_id"])

    def test_host_rebinding_foreign_origin_token_and_cross_site_all_denied(self):
        for host in ("attacker.example:8765","localhost:8765",
                     "127.0.0.1.evil.example:8765"):
            r=self.client.get("/api/v1/bootstrap",headers={"host":host})
            self.assertEqual(r.status_code,403,host)
        self.assertEqual(self.client.get("/api/v1/defaults").status_code,403)
        r=self.client.get("/api/v1/defaults",headers={
            **self.headers,"x-simc-local-token":"incorrect"})
        self.assertEqual(r.status_code,403)
        r=self.client.get("/api/v1/defaults",headers={
            **self.headers,"origin":"http://evil.example"})
        self.assertEqual(r.status_code,403)
        r=self.client.get("/api/v1/defaults",headers={
            **self.headers,"sec-fetch-site":"cross-site"})
        self.assertEqual(r.status_code,403)
        r=self.client.post("/api/v1/sessions/plan",data="hello",
            headers=self.headers|{"content-type":"text/plain"})
        self.assertEqual(r.status_code,415)
        self.assertFalse((self.root/"runs").exists())

    def test_plan_builds_real_pinned_paladin_manifest_without_native(self):
        with mock.patch.object(web.subprocess,"Popen") as spawn:
            planned=self.plan()
            spawn.assert_not_called()
        self.assertEqual(planned["status"],"READY_ZERO_NATIVE")
        self.assertEqual(planned["native_calls"],0)
        self.assertEqual(planned["plan"]["base_B"],3150)
        self.assertEqual(sum(planned["plan"]["fixed_O"].values()),32)
        self.assertEqual(planned["plan"]["final_T"],3182)
        self.assertFalse(planned["plan"]["native_called"])
        path=(self.root/"runs"/planned["session_id"])
        self.assertTrue((path/"generated"/"manifest.json").is_file())
        self.assertFalse((path/"generated"/"simc_results").exists())
        self.assertFalse((path/"V106_WORKER_STATE.json").exists())
        status=self.client.get(
            "/api/v1/sessions/"+planned["session_id"]+"/status",
            headers=self.headers)
        self.assertEqual(status.status_code,200)
        self.assertEqual(status.json()["progress"]["completed_jobs"],0)
        self.assertFalse(status.json()["active"])

    def test_internal_variant_resume_uses_sealed_identity_not_browser_defaults(self):
        # Developer stage only: browser plan/defaults still expose no variant.
        user=sessions.user_scenario(sessions.standard_controls(
             ("demonhunter","havoc")))
        folder=sessions.store_session(user,self.root/"runs",self.binary,
            "7bc1071",ordinary_variant="mid2_havoc_leather_feet_v1")
        web.bootstrap.build(user,folder/"generated",self.binary,"7bc1071",
            ordinary_variant="mid2_havoc_leather_feet_v1")
        jobs=web.LocalJobs(self.root/"runs")
        binary,rev,static=jobs.args_for_existing(folder)
        self.assertEqual(binary,self.binary.resolve())
        self.assertEqual(rev,"7bc1071")
        self.assertIsNone(static)
        self.assertFalse((folder/"generated"/"simc_results").exists())
        browser=self.client.get("/api/v1/defaults",headers=self.headers).json()
        self.assertTrue(all("ordinary_variant" not in r
                            for r in browser["archetypes"]))
        self.assertNotIn("ordinary_variant",self.controls)

    def test_existing_app_local_exact_static_cache_auto_used_only_for_specials(self):
        # Synthetic exact record tests local cache discovery only. This is
        # NOT SimC-validated stat authority or item-effect certification.
        from tests.test_v062_static_budget_bridge import record
        cache=web.bootstrap.cache_mod.empty_cache()
        item={"slot":"chest","item_id":271486,"ilevel":331,
              "options":{"bonus_id":"13848",
                         "redirected_base_stats":"268231"}}
        record(cache,item,{"crit_rating":0,"haste_rating":175,
                           "mastery_rating":0,"versatility_rating":0})
        default=self.root/"static-item-cache.json"
        web.bootstrap.cache_mod.write_atomic(default,cache)
        controls=sessions.standard_controls(("shaman","elemental"))
        controls["ilevel"]=331
        controls["special_items"]=[{k:v for k,v in item.items()
                                   if k!="ilevel"}]
        payload={**self.payload,"controls":controls}
        with mock.patch.object(web.subprocess,"Popen") as launch:
            result=self.post("/api/v1/sessions/plan",payload)
            launch.assert_not_called()
        self.assertEqual(result.status_code,200,result.text)
        data=result.json()
        self.assertTrue(data["static_cache_auto_used"])
        self.assertEqual(data["native_calls"],0)
        folder=self.root/"runs"/data["session_id"]
        manifest=json.loads((folder/"generated"/"manifest.json").read_text())
        self.assertTrue(pathlib.Path(manifest["static_cache_json"])
                        .samefile(default))
        seal=json.loads((folder/"V106_SESSION_IDENTITY.json").read_text())
        self.assertEqual(seal["static_cache_sha256"],
                         sessions.sha(default.read_bytes()))
        self.assertEqual(self.post("/api/v1/sessions/plan",payload)
                         .json()["session_id"],data["session_id"])
        restored=self.client.get("/api/v1/sessions/"+
            data["session_id"]+"/inputs",headers=self.headers)
        self.assertEqual(restored.status_code,200,restored.text)
        self.assertTrue(pathlib.Path(restored.json()["static_cache"])
                        .samefile(default))
        # Manual override remains the exact prior contract.
        explicit=self.root/"explicit-cache.json"
        web.bootstrap.cache_mod.write_atomic(explicit,cache)
        override=self.post("/api/v1/sessions/plan",
                    {**payload,"static_cache":str(explicit)})
        self.assertEqual(override.status_code,200,override.text)
        self.assertFalse(override.json()["static_cache_auto_used"])
        # Same bytes use the exact same sealed identity; a changed PATH
        # must not silently create a new run or rewrite its manifest.
        self.assertEqual(data["session_id"],
                         override.json()["session_id"])
        self.assertEqual(json.loads((folder/"generated"/"manifest.json")
                         .read_text())["static_cache_json"],
                         manifest["static_cache_json"])
        # If no special was selected, NEVER inject any cache / alter the
        # ordinary user's historical sealed session identity.
        ordinary=self.post("/api/v1/sessions/plan",
                    {**payload,"controls":{**controls,"special_items":[]}})
        self.assertEqual(ordinary.status_code,200,ordinary.text)
        self.assertFalse(ordinary.json()["static_cache_auto_used"])
        self.assertIsNone(json.loads((self.root/"runs"/
            ordinary.json()["session_id"]/"generated"/"manifest.json")
            .read_text())["static_cache_json"])

    def test_default_static_cache_missing_exact_L_fails_closed_without_native(self):
        from tests.test_v062_static_budget_bridge import record
        cache=web.bootstrap.cache_mod.empty_cache()
        record(cache,{"slot":"chest","item_id":271486,"ilevel":331,
            "options":{"bonus_id":"13848","redirected_base_stats":"268231"}},
            {"crit_rating":0,"haste_rating":175,
             "mastery_rating":0,"versatility_rating":0})
        web.bootstrap.cache_mod.write_atomic(
            self.root/"static-item-cache.json",cache)
        controls=sessions.standard_controls(("shaman","elemental"))
        controls["ilevel"]=344
        controls["special_items"]=[{"slot":"chest","item_id":271486,
            "options":{"bonus_id":"13848","redirected_base_stats":"268231"}}]
        with mock.patch.object(web.subprocess,"Popen") as launch:
            response=self.post("/api/v1/sessions/plan",
                {**self.payload,"controls":controls})
            launch.assert_not_called()
        self.assertEqual(response.status_code,422,response.text)
        self.assertEqual(response.json()["detail"]["code"],
                         "SPECIAL_L_REQUIRES_EXACT_NATIVE_STATIC_VARIANT")

    def test_exact_special_L_precheck_returns_only_known_safe_codes(self):
        reference=web.bootstrap.oil_mod.reference_path
        expected=(
            reference.ReferenceNativeBlocked(
                "SPECIAL_L_REQUIRES_EXACT_NATIVE_STATIC_VARIANT"),
            reference.ReferenceNativeBlocked(
                "REFERENCE_FIXED_L_CONSTRAINT_UNRESOLVED"),
            reference.statics.BudgetBlocked(
                "SELECTED_SPECIAL_FLOOR_UNFEASIBLE"),
        )
        for exc in expected:
            with self.subTest(code=str(exc)):
                response=web.blocked(exc)
                self.assertEqual(response.status_code,422)
                self.assertEqual(response.detail,{"code":str(exc)})
        secret=reference.ReferenceNativeBlocked(
            "UNEXPECTED_PATH_C:/private/profile.simc")
        safe=web.blocked(secret)
        self.assertEqual(safe.status_code,409)
        self.assertEqual(safe.detail["code"],"LOCAL_SESSION_PRECHECK_BLOCKED")
        self.assertNotIn("private",str(safe.detail))

    def test_invalid_user_rejected_without_new_native_or_extra_session(self):
        data=copy.deepcopy(self.payload)
        data["controls"]["spec"]="protection"
        response=self.post("/api/v1/sessions/plan",data)
        self.assertEqual(response.status_code,422)
        self.assertEqual(response.json()["detail"]["code"],
                         "V106_DPS_ARCHETYPE_NOT_READY")
        self.assertFalse((self.root/"runs").exists())
        data=self.payload|{"unexpected":"not_allowed"}
        self.assertEqual(self.post("/api/v1/sessions/plan",data).status_code,422)

    def test_start_resume_duplicate_guard_and_deferred_cancel_no_real_simc(self):
        planned=self.plan()
        sid=planned["session_id"]
        child=mock.Mock()
        child.poll.return_value=None
        with mock.patch.object(web.subprocess,"Popen",return_value=child) as spawn:
            r=self.post("/api/v1/sessions/"+sid+"/resume")
            self.assertEqual(r.status_code,200,r.text)
            self.assertEqual(r.json()["status"],"WORKER_STARTED")
            self.assertEqual(r.json()["native_attempt_ceiling_cumulative"],6)
            self.assertTrue(r.json()["new_native_execution_permitted"])
            argv=spawn.call_args.args[0]
            self.assertEqual(argv[0],sys.executable)
            self.assertIn("v106_user_session_controller.py",argv[1])
            self.assertIn("--session",argv)
            self.assertNotIn("--cache-only",argv)
            self.assertEqual(self.post("/api/v1/sessions/"+sid+"/resume").status_code,
                             409)
            state=self.client.get("/api/v1/sessions/"+sid+"/status",
                                  headers=self.headers).json()
            self.assertTrue(state["active"])
            cancel=self.post("/api/v1/sessions/"+sid+"/cancel")
            self.assertEqual(cancel.status_code,200)
            self.assertIn("AFTER_CURRENT_NATIVE",cancel.json()["status"])
            self.assertTrue((self.root/"runs"/sid/"generated"/"CANCEL").is_file())
            spawn.assert_called_once()
        child.poll.return_value=0
        self.assertEqual(self.post("/api/v1/sessions/"+sid+"/cancel").status_code,409)

    def test_result_reads_previous_six_case_user_result_without_native(self):
        sid=self.plan()["session_id"]
        folder=self.root/"runs"/sid
        example=fake_native(hits=6)
        sessions.paths(folder)["final"].write_text(
            json.dumps(example),encoding="utf8")
        with mock.patch.object(web.subprocess,"Popen") as spawn:
            r=self.client.get("/api/v1/sessions/"+sid+"/result",
                              headers=self.headers)
            spawn.assert_not_called()
        self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(r.json()["final_T"],3182)
        self.assertEqual(r.json()["cache_hits_this_run"],6)
        self.assertFalse(r.json()["user_result"]["global_optimum_proven"])
        self.assertIn("95%",r.json()["display_text"])
        example["user_result"]["confidence_level"]=0.99
        sessions.paths(folder)["final"].write_text(json.dumps(example))
        self.assertEqual(self.client.get(
            "/api/v1/sessions/"+sid+"/result",headers=self.headers).status_code,422)

    def test_cache_only_never_launches_with_missing_real_json2_and_receipts(self):
        sid=self.plan()["session_id"]
        with mock.patch.object(web.subprocess,"Popen") as spawn:
            r=self.post("/api/v1/sessions/"+sid+"/cache-only")
            self.assertEqual(r.status_code,422,r.text)
            spawn.assert_not_called()
        self.assertIn("CACHE_ONLY_REQUIRES_COMPLETED_REAL_SESSION",
                      r.text)
        self.assertEqual(self.client.get("/api/v1/sessions/../../etc/status",
                          headers=self.headers).status_code,404)
        self.assertEqual(self.client.get(
            "/api/v1/sessions/1234/status",headers=self.headers).status_code,404)

    def test_legacy_windows_case_not_modified_by_health_or_results(self):
        self.plan()
        before={str(p.relative_to(self.root)):p.read_bytes()
                for p in (self.root/"runs").rglob("*") if p.is_file()}
        self.client.get("/api/v1/health")
        for p in self.root.joinpath("runs").iterdir():
            self.client.get("/api/v1/sessions/"+p.name+"/status",
                            headers=self.headers)
        after={str(p.relative_to(self.root)):p.read_bytes()
               for p in (self.root/"runs").rglob("*") if p.is_file()}
        self.assertEqual(before,after)

if __name__=="__main__":
    unittest.main()
