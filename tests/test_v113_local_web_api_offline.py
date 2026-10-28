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
                      else "SOURCE_NON_TIER_NOT_ALL_STANDARDIZED"
                      if (row["class"],row["spec"]) in
                          web.bootstrap.common.GENERIC_PENDING
                      else "SOURCE_BACKED_PARTIAL_ORDINARY_POOL")
            self.assertEqual(scope,expected)
        self.assertEqual(status_counts,{
            "SOURCE_NON_TIER_NOT_ALL_STANDARDIZED":17,
            "SOURCE_BACKED_PARTIAL_ORDINARY_POOL":7,
            "SOURCE_INDEPENDENT_SEASON_CATALOG":2})
        self.assertFalse((self.root/"runs").exists())

    def test_web_remains_usable_with_no_legacy_complete_simc_fixtures(self):
        # In a package without the old 24 full SimC source fixtures, the
        # ready/default UI list must still expose both Native-proven pure
        # paths, but may not claim the unavailable legacy paths work.
        original_text=pathlib.Path.read_text
        original_bytes=pathlib.Path.read_bytes
        seen=[]
        def forbid_source(path):
            loc=str(path).replace(chr(92),"/")
            if "/integration_probes/fixtures/" in loc and loc.endswith(".simc"):
                seen.append(loc)
                raise FileNotFoundError("LEGACY_SOURCE_PROFILE_NOT_INSTALLED")
        def absent_text(path,*args,**kwargs):
            forbid_source(path)
            return original_text(path,*args,**kwargs)
        def absent_bytes(path,*args,**kwargs):
            forbid_source(path)
            return original_bytes(path,*args,**kwargs)
        with mock.patch.object(pathlib.Path,"read_text",absent_text), \
             mock.patch.object(pathlib.Path,"read_bytes",absent_bytes):
            response=self.client.get("/api/v1/defaults",headers=self.headers)
            self.assertEqual(response.status_code,200,response.text)
            data=response.json()
            visible={(r["class"],r["spec"]) for r in data["archetypes"]}
            self.assertEqual(visible,web.bootstrap.PURE_PRODUCT_SPECS)
            missing={(r["class"],r["spec"]) for r in
                     data["unavailable_missing_legacy_fixtures"]}
            self.assertEqual(missing,set(sessions.SUPPORTED)-visible)
            self.assertEqual(len(seen),24)
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
