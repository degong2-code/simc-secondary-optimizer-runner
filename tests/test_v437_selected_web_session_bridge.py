"""v437: fresh selected web plan routes through isolated v435/v436 session.

Only internal web orchestration is mocked, no SimC/Native or actual-season
selected item is admitted by these synthetic fixtures.
"""
from __future__ import annotations

import pathlib
import sys
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v113_local_web_api as web
from tests.test_p3_ham_fresh_v212_web_profile_bridge_offline import (
    VerifiedFreshWebProfileBridge)

class SelectedWebSession(unittest.TestCase):
    def setUp(self):
        self.base=VerifiedFreshWebProfileBridge()
        self.base.setUp()
        self.addCleanup(self.base.doCleanups)
        self.base.remember()
        self.jobs=self.base.jobs
        self.folder=self.base.root/("b"*20)
        self.folder.mkdir()
        self.binary=self.base.root/"selected-simc.exe"
        self.binary.write_bytes(b"SIMC_STUB_DO_NOT_RUN")
        self.cache=self.base.root/"selected-static-cache.json"
        self.cache.write_text("{}\n")
        self.controls=web.sessions.standard_controls()
        self.controls["oil_hands"]=[]
        self.controls["special_items"]=[{
            "slot":"head","item_id":290111,"options":{}}]
        self.params=web.UserRequest(
            controls=self.controls,binary=str(self.binary),
            revision="abcdef0",current_season_product=True,
            static_cache=str(self.cache))
        self.preview={
            "status":"B8_SELECTED_V096_COMPLETE_PROFILE_BUDGET_NOT_ADMITTED",
            "v435_future_v106_session_key_unadmitted":{
                "identity_sha256":"a"*64,
                "session_key_preview":self.folder.name},
            "native_execution_authorized":False}
        self.materialized={
            "schema":web.bootstrap.SCHEMA,
            "status":"READY_SELECTED_SOURCE_LOCKED_V096_MANIFEST_ZERO_NATIVE",
            "plan":{
                "class":"paladin","spec":"retribution",
                "base_B":3100,"fixed_O":{
                    "crit_rating":0,"haste_rating":0,
                    "mastery_rating":0,"versatility_rating":0},
                "final_T":3100,"native_limit":6}}

    def test_selected_web_uses_separate_v106_store_and_native0_writer(self):
        fresh=self.jobs._verified_fresh_profile_result
        with (
            mock.patch.object(self.jobs,"load_fresh_profile_for_user",
                              return_value=fresh),
            mock.patch.object(web.bootstrap,
                "preview_from_environment_build",
                return_value=self.preview) as preview,
            mock.patch.object(web.sessions,"store_selected_fresh_session",
                return_value=self.folder) as store,
            mock.patch.object(web.sessions,"store_session",
                side_effect=AssertionError("NO_OLD_SESSION")) as old,
            mock.patch.object(web.profile_stage,"build_or_reuse",
                side_effect=AssertionError("NO_OLD_STAGE")),
            mock.patch.object(web.bootstrap,
                "materialize_selected_verified_environment",
                return_value=self.materialized) as writer,
            mock.patch.object(self.jobs,"_fresh_environment_summary",
                return_value={"status":"READY"}) as env
        ):
            response=self.jobs.plan(self.params)
        self.assertEqual(response["status"],"READY_ZERO_NATIVE")
        self.assertEqual(response["native_calls"],0)
        self.assertEqual(response["session_id"],self.folder.name)
        self.assertEqual(response["plan"]["base_B"],3100)
        preview.assert_called_once()
        store.assert_called_once()
        self.assertEqual(store.call_args.kwargs["selected_source"],self.preview)
        writer.assert_called_once()
        self.assertIs(writer.call_args.kwargs["preview_result"],self.preview)
        self.assertEqual(writer.call_args.kwargs["folder"],
                         self.folder/"generated")
        self.assertFalse(old.called)
        env.assert_called_once()

    def test_selected_web_without_exact_cache_blocks_before_session(self):
        self.params=self.params.model_copy(update={"static_cache":None})
        with (
            mock.patch.object(web.exact_L,"source_cache",return_value=None),
            mock.patch.object(web.bootstrap,
                "preview_from_environment_build",
                side_effect=AssertionError("NO_UNVERIFIED_PREVIEW")),
            mock.patch.object(web.sessions,"store_selected_fresh_session",
                side_effect=AssertionError("NO_SESSION_CREATE")),
            mock.patch.object(self.jobs,"load_fresh_profile_for_user",
                return_value=self.jobs._verified_fresh_profile_result)
        ):
            with self.assertRaises(web.HTTPException) as caught:
                self.jobs.plan(self.params)
        self.assertIn("WEB_SELECTED_B8_EXACT_STATIC_CACHE_REQUIRED",
                      str(caught.exception.detail))


    def _selected_saved_session(self):
        import json
        self.base.installed_doc["status"]=(
            "FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY")
        self.base.installed.write_text(json.dumps(
            self.base.installed_doc),encoding="utf8")
        identity={"schema":web.sessions.SCHEMA,
                  "fresh_v212_installed_manifest_sha256":self.base.digest,
                  "v435_selected_source_identity":{"schema":"v435_test_source"}}
        digest=web.sessions.sha(web.sessions.canonical(
            identity).encode("utf8"))
        folder=self.base.root/digest[:20]
        generated=folder/"generated"
        generated.mkdir(parents=True)
        (folder/"V106_SESSION_IDENTITY.json").write_text(
            web.sessions.canonical(identity)+"\n",encoding="utf8")
        manifest={"schema":web.bootstrap.entry.SCHEMA,
                  web.bootstrap.entry.SELECTED_FRESH_SEASON_FIELD:{
                    "schema":web.bootstrap.entry.SELECTED_FRESH_SEASON_SCHEMA,
                    "installed_environment_path":str(self.base.installed),
                    "installed_manifest_sha256":self.base.digest,
                    "selected_v435_identity_sha256":digest}}
        (generated/"manifest.json").write_text(
            web.sessions.canonical(manifest)+"\n",encoding="utf8")
        return folder,manifest,identity

    def test_v438_selected_source_returns_installed_environment_summary(self):
        folder,manifest,identity=self._selected_saved_session()
        with mock.patch.object(
                web.environment_manifest,
                "verify_fresh_installed_environment") as installed:
            summary=self.jobs._read_environment_summary(folder)
        self.assertEqual(summary[
            "fresh_v212_installed_manifest_sha256"],self.base.digest)
        self.assertEqual(summary["game_build"],self.base.build)
        self.assertEqual(summary["target_ilevel"],334)
        installed.assert_called_once()

    def test_v438_selected_start_rechecks_real_v217_install_not_none(self):
        folder,manifest,identity=self._selected_saved_session()
        with (
            mock.patch.object(web.environment_manifest,
                              "verify_fresh_installed_environment"),
            mock.patch.object(web.environment_build,
               "find_verified_installed_season_environment",
               return_value={"installed_manifest_sha256":
                             self.base.digest}) as v217
        ):
            summary=self.jobs._read_environment_summary(folder)
            self.jobs._verify_environment_dependencies(summary,folder)
        v217.assert_called_once()
        self.assertEqual(v217.call_args.kwargs[
            "expected_installed_manifest_sha256"],self.base.digest)

    def test_v438_selected_manifest_without_v435_seal_fails_closed(self):
        folder,manifest,identity=self._selected_saved_session()
        identity.pop("v435_selected_source_identity")
        (folder/"V106_SESSION_IDENTITY.json").write_text(
            web.sessions.canonical(identity)+"\n",encoding="utf8")
        with self.assertRaisesRegex(
                web.environment_manifest.EnvironmentBlocked,
                "WEB_B8_SELECTED_SOURCE_OR_SESSION_SHA_DRIFT"):
            self.jobs._read_environment_summary(folder)

    def test_v438_selected_manifest_changed_v435_sha_fails_closed(self):
        folder,manifest,identity=self._selected_saved_session()
        manifest[web.bootstrap.entry.SELECTED_FRESH_SEASON_FIELD][
            "selected_v435_identity_sha256"]="0"*64
        (folder/"generated"/"manifest.json").write_text(
            web.sessions.canonical(manifest)+"\n",encoding="utf8")
        with self.assertRaisesRegex(
                web.environment_manifest.EnvironmentBlocked,
                "WEB_B8_SELECTED_SOURCE_OR_SESSION_SHA_DRIFT"):
            self.jobs._read_environment_summary(folder)

    def test_v438_two_installed_fields_do_not_suppress_verifier(self):
        folder,manifest,identity=self._selected_saved_session()
        manifest[web.bootstrap.entry.FRESH_SEASON_FIELD]={
            "installed_environment_path":str(self.base.installed)}
        (folder/"generated"/"manifest.json").write_text(
            web.sessions.canonical(manifest)+"\n",encoding="utf8")
        with self.assertRaisesRegex(
                web.environment_manifest.EnvironmentBlocked,
                "WEB_FRESH_MULTIPLE_INSTALLED_SOURCE_FIELDS"):
            self.jobs._read_environment_summary(folder)

if __name__=="__main__":
    unittest.main()
