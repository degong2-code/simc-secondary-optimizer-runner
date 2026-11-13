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

if __name__=="__main__":
    unittest.main()
