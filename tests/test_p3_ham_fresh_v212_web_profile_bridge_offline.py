"""P3-HAM: fresh v212-installed source reaches web user planning without Native."""
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]/"runner"))
import v113_local_web_api as web


class VerifiedFreshWebProfileBridge(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)/"runs"
        self.root.mkdir()
        self.jobs=web.LocalJobs(self.root)
        self.build="12.1.5.70783"
        self.digest="a"*64
        self.catalog_digest="b"*64
        fresh=self.root/"_fresh_season_sources"/("wago_"+self.build)/"fresh_source"
        fresh.mkdir(parents=True)
        self.catalog=fresh/"v213_candidate_catalog.json"
        self.catalog.write_text(json.dumps(
            {"game_build":self.build,"manifest_sha256":self.catalog_digest}))
        raw_digest=hashlib.sha256(self.catalog.read_bytes()).hexdigest()
        self.installed=fresh/("v212_installed_"+self.digest[:20]+".json")
        self.installed_doc={
            "manifest_sha256":self.digest,"game_build":self.build,
            "target_ilevel":334,
            "source_catalog_artifact_sha256":raw_digest,
            "source_catalog_manifest_sha256":self.catalog_digest}
        self.installed.write_text(json.dumps(self.installed_doc))
        self.original={
            "normal_build_entry":True,
            "zero_history_build":{"environment_ready":True},
            "source_compilation":{
                "status":"FRESH_V191_V211_V213_COMPILED_UNADMITTED",
                "source_catalog_path":str(self.catalog),
                "stage_root":str(fresh.parent),
                "simc_revision":"abcdef0",
                "v191_original_gear_tier_source_paths":{},
                "v098_source_only_profile_inputs_unadmitted":{},
                "physical_gem_layout_unadmitted":{},
                "physical_gem_J_arithmetic_unadmitted":{},
                "selected_v221_gem_item_relation_unadmitted":{},
                "preflight_sha256":self.catalog_digest,
                "verified_environment_install":{
                    "stage_output_path":str(self.installed),
                    "manifest_sha256":self.digest,
                    "official_T":3107,"environment_ready":True}},
            "fresh_one_spec_simc_representative":{"candidate_path":"probe"}}

    def remember(self):
        with (
            mock.patch.object(web.environment_manifest,
                              "verify_fresh_installed_environment"),
            mock.patch.object(
                web.environment_build,
                "find_verified_installed_season_environment",
                return_value={"installed_manifest_sha256":self.digest})
        ):
            return self.jobs.remember_verified_fresh_environment(self.original)

    def test_only_original_verified_v212_receipt_is_accepted(self):
        self.assertEqual(self.remember(),self.digest)
        result=self.jobs._verified_fresh_profile_result
        self.assertEqual(result["source_compilation"][
            "verified_environment_install"]["manifest_sha256"],self.digest)
        self.assertTrue(result["normal_build_entry"])
        self.assertEqual(result["verified_target_ilevel"],334)
        with (
            mock.patch.object(web.environment_manifest,
                              "verify_fresh_installed_environment"),
            mock.patch.object(
                web.environment_build,
                "find_verified_installed_season_environment",
                return_value={"installed_manifest_sha256":"e"*64})
        ):
            with self.assertRaises(web.environment_manifest.EnvironmentBlocked):
                self.jobs.remember_verified_fresh_environment(self.original)

    def test_fresh_plan_uses_verified_profile_owner_not_legacy_v216(self):
        self.remember()
        source=self.jobs._verified_fresh_profile_result
        binfile=self.root/"simc.exe"
        binfile.write_bytes(b"fake executable never executed")
        controls=web.sessions.standard_controls()
        params=web.UserRequest(controls=controls,binary=str(binfile),
                               revision="abcdef0",current_season_product=True)
        folder=self.root/("a"*20)
        folder.mkdir()
        user_result={"plan":{"class":"paladin","spec":"retribution",
                             "base_B":3107,"fixed_O":{},
                             "final_T":3107,"native_limit":6}}
        with (
            mock.patch.object(web.sessions,"store_session",return_value=folder)
                as store,
            mock.patch.object(web.profile_stage,"build_or_reuse",
                              return_value=(user_result,{})) as stage,
            mock.patch.object(self.jobs,"_fresh_environment_summary",
                              return_value={"status":"READY"}) as summary
        ):
            response=self.jobs.plan(params)
        self.assertEqual(response["status"],"READY_ZERO_NATIVE")
        self.assertEqual(response["native_calls"],0)
        self.assertEqual(store.call_args.kwargs[
            "fresh_installed_manifest_sha256"],self.digest)
        self.assertEqual(store.call_args.kwargs[
            "source_catalog_path"],self.catalog)
        self.assertIs(stage.call_args.kwargs[
            "verified_fresh_environment_result"],source)
        summary.assert_called_once()
        self.assertEqual(response["environment_manifest"]["status"],"READY")

    def test_start_resume_uses_original_v217_installed_manifest_sha(self):
        folder=self.root/("f"*20)
        folder.mkdir()
        (folder/"V106_SESSION_IDENTITY.json").write_text(json.dumps(
            {"fresh_v212_installed_manifest_sha256":self.digest}))
        summary={"fresh_v212_installed_manifest_sha256":self.digest,
                 "target_ilevel":334,"game_build":self.build}
        with mock.patch.object(web.environment_build,
            "find_verified_installed_season_environment",
            return_value={"installed_manifest_sha256":self.digest}):
            self.jobs._verify_environment_dependencies(summary,folder)
        (folder/"V106_SESSION_IDENTITY.json").write_text(json.dumps(
            {"fresh_v212_installed_manifest_sha256":"f"*64}))
        with mock.patch.object(web.environment_build,
            "find_verified_installed_season_environment",
            return_value={"installed_manifest_sha256":self.digest}):
            with self.assertRaises(web.environment_manifest.EnvironmentBlocked):
                self.jobs._verify_environment_dependencies(summary,folder)


    def test_v217_source_snapshot_recovers_fresh_new_session_after_restart(self):
        with (
            mock.patch.object(web.environment_manifest,
                              "verify_fresh_installed_environment"),
            mock.patch.object(web.environment_build,
                "find_verified_installed_season_environment",
                return_value={"installed_manifest_sha256":self.digest})
        ):
            self.jobs.remember_verified_fresh_environment(self.original)
            receipt=self.jobs.persist_verified_fresh_profile()
            self.assertEqual(receipt["status"],"EXECUTED_AND_SEALED")
            self.assertEqual(receipt["new_native_calls"],0)
            again=self.jobs.persist_verified_fresh_profile()
            self.assertEqual(again["status"],"REUSED_VERIFIED")
            restarted=web.LocalJobs(self.root)
            self.assertIsNone(restarted._verified_fresh_profile_result)
            recovered=restarted.restore_verified_fresh_profile(
                target_ilevel=334,game_build=self.build)
            self.assertEqual(recovered["verified_target_ilevel"],334)
            self.assertEqual(recovered["source_compilation"][
                "verified_environment_install"]["manifest_sha256"],self.digest)
            self.assertEqual(restarted._current_fresh_game_build,self.build)
            # A second application process needs neither source collection
            # nor fresh G/F Native to serve new user planning.
            user_result={"plan":{"class":"paladin","spec":"retribution",
                                 "base_B":3107,"fixed_O":{},
                                 "final_T":3107,"native_limit":6}}
            fake=self.root/"simc.bin"
            fake.write_bytes(b"offline fixture never executed")
            folder=self.root/("c"*20)
            folder.mkdir()
            form=web.UserRequest(controls=web.sessions.standard_controls(),
                binary=str(fake),revision="abcdef0",
                current_season_product=True,fresh_season_build=self.build)
            with (
                mock.patch.object(web.sessions,"store_session",
                                  return_value=folder) as store,
                mock.patch.object(web.profile_stage,"build_or_reuse",
                    return_value=(user_result,{})) as stage,
                mock.patch.object(restarted,"_fresh_environment_summary",
                                  return_value={"status":"READY"})
            ):
                response=restarted.plan(form)
            self.assertEqual(response["status"],"READY_ZERO_NATIVE")
            self.assertEqual(response["native_calls"],0)
            self.assertEqual(store.call_args.kwargs[
                "fresh_installed_manifest_sha256"],self.digest)
            self.assertEqual(stage.call_args.kwargs[
                "verified_fresh_environment_result"][
                    "verified_target_ilevel"],334)

    def test_restarted_snapshot_tampering_blocks_and_does_not_rebuild(self):
        with (
            mock.patch.object(web.environment_manifest,
                              "verify_fresh_installed_environment"),
            mock.patch.object(web.environment_build,
                "find_verified_installed_season_environment",
                return_value={"installed_manifest_sha256":self.digest})
        ):
            self.jobs.remember_verified_fresh_environment(self.original)
            self.jobs.persist_verified_fresh_profile()
            root,_,relative=self.jobs._verified_profile_stage(
                self.installed_doc)
            target=root/relative
            raw=json.loads(target.read_text(encoding="utf8"))
            raw["environment_result"]["verified_target_ilevel"]=335
            target.write_bytes((web.stage_engine.canonical(raw)+"\n").encode("utf8"))
            restarted=web.LocalJobs(self.root)
            with self.assertRaises(web.stage_engine.StageExecutionBlocked):
                restarted.restore_verified_fresh_profile(
                    target_ilevel=334,game_build=self.build)

    def test_verified_prior_environment_without_snapshot_stays_no_native(self):
        with (
            mock.patch.object(web.environment_build,
                "find_verified_installed_season_environment",
                return_value={"installed_manifest_sha256":self.digest,
                              "target_ilevel":334,"environment_ready":True,
                              "environment_installed":True,
                              "G":2850,"J":92,"F":165,"B":3107,"T":3107}),
            mock.patch.object(web.environment_build,"build_environment") as build,
            mock.patch.object(web.environment_manifest,
                              "verify_fresh_installed_environment")
        ):
            result=self.jobs.build_season_environment(
                game_build=self.build,target_ilevel=334)
            self.assertTrue(result["environment_ready"])
            self.assertFalse(result["verified_v113_profile_source_restored"])
            self.assertIsNone(self.jobs._verified_fresh_profile_result)
            build.assert_not_called()
            self.assertIsNone(self.jobs.load_fresh_profile_for_user(
                334,explicit_build=self.build))
            # An older environment without a v113 profile snapshot retains
            # its previous source-backed browser path (no new Native).


    def test_existing_fresh_snapshot_cannot_fall_back_to_wrong_target(self):
        with (
            mock.patch.object(web.environment_manifest,
                              "verify_fresh_installed_environment"),
            mock.patch.object(web.environment_build,
                "find_verified_installed_season_environment",
                return_value={"installed_manifest_sha256":self.digest})
        ):
            self.jobs.remember_verified_fresh_environment(self.original)
            self.jobs.persist_verified_fresh_profile()
        restarted=web.LocalJobs(self.root)
        with mock.patch.object(web.environment_build,
            "find_verified_installed_season_environment",return_value=None):
            with self.assertRaisesRegex(
                    web.environment_manifest.EnvironmentBlocked,
                    "WEB_FRESH_TARGET_BUILD_NOT_INSTALLED_RUN_SEASON_BUILD"):
                restarted.load_fresh_profile_for_user(
                    335,explicit_build=self.build)


class SeasonNoOilBrowserDefaults(unittest.TestCase):
    def test_zero_o_baseline_does_not_auto_select_legacy_main_hand(self):
        from fastapi.testclient import TestClient
        with tempfile.TemporaryDirectory() as scratch:
            app=web.create_app(root=pathlib.Path(scratch),
                               token="web-default-oil-test-token")
            with TestClient(app,base_url="http://127.0.0.1:8765") as client:
                response=client.get("/api/v1/defaults",headers={
                    "x-simc-local-token":"web-default-oil-test-token",
                    "origin":"http://127.0.0.1:8765"})
                self.assertEqual(response.status_code,200)
                archetypes=response.json()["archetypes"]
                self.assertEqual(len(archetypes),26)
                self.assertTrue(all(row["oil_hands"]==[] for row in archetypes))


class NativeCaseArchiveLayout(unittest.TestCase):
    def test_original_v291_nested_case_directory_is_preserved_in_zip(self):
        from integration_probes import p3_haj_real_local_web_native_e2e as real_web
        import v293_local_longrun_session as longrun
        import zipfile

        with tempfile.TemporaryDirectory() as scratch:
            root=pathlib.Path(scratch)/"sessions"
            root.mkdir()
            session="a"*20
            (root/session).mkdir()
            stage=root/session/"longrun_12"
            output=stage/"simc_results"
            output.mkdir(parents=True)
            for name in ("V291_SESSION.json","V291_JOURNAL.jsonl",
                         "V291_RESULT.json","V291_PROGRESS.json"):
                (output/name).write_text("{}")
            for index in (1,2):
                directory=output/"cases"/("case_%05d"%index)/"native"
                directory.mkdir(parents=True)
                for name in ("input.simc","result.json","native_receipt.json"):
                    (directory/name).write_text("witness")
            destination=pathlib.Path(scratch)/"archive.zip"
            with (
                mock.patch.object(longrun,"config",
                                  return_value={"native_budget":12}),
                mock.patch.object(longrun,"stage_path",return_value=stage)
            ):
                receipt=real_web.save_cases(root,session,destination)
            self.assertEqual(receipt["native_case_files"],6)
            with zipfile.ZipFile(destination) as z:
                names=set(z.namelist())
                self.assertIn("cases/case_00001/native/result.json",names)
                self.assertIn("cases/case_00002/native/native_receipt.json",names)
                self.assertEqual(len(names),10)


if __name__=="__main__":
    unittest.main()
