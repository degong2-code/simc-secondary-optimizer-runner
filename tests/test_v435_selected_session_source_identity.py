"""v435 selected full-profile session/cache identity; no Native or folder.

Synthetic v212/v432 data and a mocked normalization boundary: this tests
SHA/cache/user identity behavior, not real current-season SimC admission.
"""
from __future__ import annotations

import copy
import hashlib
import pathlib
import sys
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v106_user_session_controller as sessions
from tests.test_v434_selected_v096_source_only import V096SelectedNonadmittedPreflight

def digest(value):
    return sessions.sha(sessions.canonical(value).encode("utf8"))

class SelectedFutureSessionKey(unittest.TestCase):
    def setUp(self):
        self.fixture=V096SelectedNonadmittedPreflight()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        verified,_,_=self.fixture.verify()
        self.user={
            **copy.deepcopy(self.fixture.fx.fx.user),
            "character":{"class":"mage","spec":"frost",
                         "race":"human","talents":"BEkACnH8fIxO0gcJ4/DQz3AAAAA"}}
        self.selected=copy.deepcopy(self.fixture.selected)
        self.verified=verified
        self.runtime={
            "scout_iterations":35,
            "confirm_iterations":320,
            "threads":1}
        self.typed_scenario={
            "runtime":copy.deepcopy(self.runtime),
            "target":{"mode":"manual_total","ilevel":334,"manual_total":3162},
            "equipment":copy.deepcopy(self.selected["selected_equipment"])}
        self.normalized={
            "scenario":self.typed_scenario,
            "scenario_digest":verified["scenario_digest"],
            "budget":{"external_temporary_rating":
                       copy.deepcopy(self.selected[
                           "budget_preflight"]["fixed_O"])}}
        self.selected["status"]=(
            "B8_SELECTED_V096_COMPLETE_PROFILE_BUDGET_NOT_ADMITTED")
        self.selected["profile_simc"]=self.fixture.profile
        self.selected["source_profile_sha256"]=self.fixture.sha
        self.selected["scenario_source_only"]={
            "runtime":copy.deepcopy(self.runtime)}
        self.selected["v096_typed_input_unadmitted"]={
            "scenario":self.typed_scenario,
            "scenario_digest":verified["scenario_digest"]}
        self.selected["v096_selected_source_only_preflight"]=verified
        self.final={
            "schema":"v434_b8_selected_full_native_profile_source_binding_v1",
            "v433_preconsumable_source_sha256":
                self.selected["bound_source_identity_sha256"],
            "verified_v096_preflight_sha256":digest(verified),
            "final_profile_sha256":self.fixture.sha,
            "final_scenario_digest":verified["scenario_digest"],
            "installed_v212_manifest_sha256":
                self.fixture.doc["manifest_sha256"],
            "selected_budget_identity_sha256":
                self.selected["budget_preflight"][
                    "selected_budget_identity_sha256"],
            "seed_targets_B":[{"crit_rating":700,
                "haste_rating":900,"mastery_rating":900,
                "versatility_rating":662},
                {"crit_rating":750,"haste_rating":850,
                "mastery_rating":900,"versatility_rating":662}]}
        self.selected["final_source_identity"]=self.final
        self.selected["final_source_identity_sha256"]=digest(self.final)
        self.binary=pathlib.Path(self.fixture.fx.dir.name)/"fake-binary.exe"
        self.binary.write_bytes(b"NOT_SIMC_NO_NATIVE_B8_TEST")
        self.static=self.fixture.fx.cache_file
        self.source=pathlib.Path(self.fixture.fx.dir.name)/"source.json"
        self.install=self.fixture.doc["manifest_sha256"]

    def preview(self,*,binary=None,revision="c"*40):
        # Real v106 key construction/user+binary+cache hashing runs; only
        # the local source-catalog and profile-stage fingerprint suppliers
        # (unrelated to B8 identity) are mocked.
        with (
            mock.patch.object(sessions,"source_catalog_identity",
                              return_value={"game_build":"12.1.5.70783"}),
            mock.patch.object(sessions.profile_stage,"session_identity",
                              return_value={"identity_sha256":"f"*64}),
            mock.patch.object(sessions.bootstrap.scenario,"normalize",
                              return_value=self.normalized)
        ):
            return sessions.preview_selected_fresh_session_identity(
                user=self.user,binary=(binary or self.binary),
                revision=revision,static_cache=self.static,
                selected_source=self.selected,
                source_catalog_path=self.source,
                installed_manifest_sha256=self.install)

    def test_future_v106_key_binds_exact_v434_without_creating_folder(self):
        out=self.preview()
        self.assertEqual(out["status"],
            "B8_SELECTED_SESSION_KEY_SOURCE_ONLY_NOT_ADMITTED")
        self.assertEqual(len(out["session_key_preview"]),20)
        self.assertTrue(out["old_v106_session_key_not_reused"])
        self.assertFalse(out["session_folder_created"])
        self.assertFalse(out["native_execution_authorized"])
        self.assertFalse(out["runtime_manifest_created"])
        self.assertEqual(out["new_native_calls"],0)
        self.assertFalse(any(path.is_dir() for path in
            pathlib.Path(self.fixture.fx.dir.name).glob("[a-f0-9]"*20)))

    def test_same_source_binary_and_cache_reuses_stable_future_key(self):
        a=self.preview()
        b=self.preview()
        self.assertEqual(a["identity_sha256"],b["identity_sha256"])
        self.assertEqual(a["session_key_preview"],b["session_key_preview"])

    def test_binary_and_revision_are_isolated_for_dps_cache(self):
        first=self.preview()
        self.binary.write_bytes(b"DIFFERENT_LOCAL_SIMC_BINARY")
        binary_changed=self.preview()
        revision_changed=self.preview(revision="d"*40)
        self.assertEqual(len({
            first["identity_sha256"],binary_changed["identity_sha256"],
            revision_changed["identity_sha256"]}),3)

    def test_static_cache_byte_edit_fails_closed_even_if_json_equal(self):
        self.static.write_bytes(self.static.read_bytes()+b"\n")
        with self.assertRaisesRegex(sessions.SessionBlocked,
                                    "STATIC_CACHE_FILE_OR_INSTALLED"):
            self.preview()

    def test_selected_gear_id_tampering_does_not_resign_existing_source(self):
        self.user["embellishments"][0]["item_id"]+=1
        with self.assertRaisesRegex(sessions.SessionBlocked,
                                    "USER_ITEM_ID_NOT_PHYSICALLY"):
            self.preview()

    def test_manual_final_t_must_match_reconciled_selected_T(self):
        self.user["target"]["final_T"]=3162
        with self.assertRaisesRegex(sessions.SessionBlocked,
                                    "USER_TARGET_NOT_BOUND"):
            self.preview()

    def test_final_profile_bytes_cannot_reuse_previous_selected_session(self):
        self.selected["profile_simc"]+="gear_haste_rating=42\n"
        with self.assertRaisesRegex(sessions.SessionBlocked,
                                    "FINAL_PROFILE_OR_SOURCE_SHA"):
            self.preview()

    def test_stale_v434_stat_bounds_or_source_identity_are_rejected(self):
        self.selected["v096_selected_source_only_preflight"]["base_B"]+=1
        with self.assertRaisesRegex(sessions.SessionBlocked,
                                    "FINAL_PROFILE_OR_SOURCE_SHA"):
            self.preview()

    def test_iterations_mutated_after_final_typed_digest_are_rejected(self):
        self.selected["scenario_source_only"]["runtime"][
            "scout_iterations"]+=1
        with self.assertRaisesRegex(sessions.SessionBlocked,
                                    "TYPED_SCENARIO_OR_PREVIEW_CACHE"):
            self.preview()

    def test_not_usable_with_unadmitted_partial_v433_preview(self):
        self.selected["status"]=(
            "B8_SELECTED_PROFILE_BUDGET_RECONCILED_NOT_ADMITTED")
        with self.assertRaisesRegex(sessions.SessionBlocked,
                                    "V434_SOURCE_ONLY_IDENTITY"):
            self.preview()


    def test_v098_top_level_selected_preview_forwards_exact_v106_key(self):
        import v098_target_user_scenario_bootstrap as bootstrap
        expected={
            "schema":"v435_selected_fresh_session_key_preview_v1",
            "status":"B8_SELECTED_SESSION_KEY_SOURCE_ONLY_NOT_ADMITTED",
            "native_execution_authorized":False,
            "runtime_manifest_created":False,
            "session_folder_created":False,
            "session_key_preview":"c"*20}
        compilation={
            "source_catalog_path":str(self.source),
            "verified_environment_install":{"manifest_sha256":self.install}}
        with mock.patch.object(
                sessions,"preview_selected_fresh_session_identity",
                return_value=expected) as inner:
            out=bootstrap._attach_selected_future_session_identity_unadmitted(
                user=self.user,binary=self.binary,revision="c"*40,
                cache_path=self.static,compilation=compilation,
                result=self.selected)
        self.assertEqual(out["v435_future_v106_session_key_unadmitted"],
                         expected)
        self.assertTrue(out[
            "v435_isolated_selected_dps_cache_identity_preview_only"])
        self.assertFalse(out["native_execution_authorized"])
        self.assertFalse(out["runtime_manifest_created"])
        self.assertIs(inner.call_args.kwargs["selected_source"],
                      self.selected)
        self.assertEqual(inner.call_args.kwargs[
            "installed_manifest_sha256"],self.install)
        self.assertEqual(inner.call_args.kwargs[
            "static_cache"],self.static)

    def test_v098_pending_selected_variant_never_derives_future_session(self):
        import v098_target_user_scenario_bootstrap as bootstrap
        self.selected["status"]=(
            "B8_SELECTED_PROFILE_STATIC_VARIANTS_PENDING_NO_NATIVE")
        with mock.patch.object(
                sessions,"preview_selected_fresh_session_identity",
                side_effect=AssertionError("NO_KEY_FOR_PENDING")):
            out=bootstrap._attach_selected_future_session_identity_unadmitted(
                user=self.user,binary=self.binary,revision="c"*40,
                cache_path=None,compilation={},result=self.selected)
        self.assertEqual(out["status"],self.selected["status"])
        self.assertNotIn("v435_future_v106_session_key_unadmitted",out)

    def test_v098_cannot_promote_future_key_to_runtime_ready(self):
        import v098_target_user_scenario_bootstrap as bootstrap
        forbidden={
            "schema":"v435_selected_fresh_session_key_preview_v1",
            "status":"B8_SELECTED_SESSION_KEY_SOURCE_ONLY_NOT_ADMITTED",
            "native_execution_authorized":True,
            "runtime_manifest_created":False,
            "session_folder_created":False}
        with mock.patch.object(
                sessions,"preview_selected_fresh_session_identity",
                return_value=forbidden):
            with self.assertRaisesRegex(
                    bootstrap.UserScenarioBlocked,
                    "FUTURE_SESSION_MUST_STAY_SOURCE_ONLY"):
                bootstrap._attach_selected_future_session_identity_unadmitted(
                    user=self.user,binary=self.binary,revision="c"*40,
                    cache_path=self.static,
                    compilation={
                        "source_catalog_path":str(self.source),
                        "verified_environment_install":{
                            "manifest_sha256":self.install}},
                    result=self.selected)


    def _stored(self):
        with (
            mock.patch.object(sessions,"source_catalog_identity",
                              return_value={"game_build":"12.1.5.70783"}),
            mock.patch.object(sessions.profile_stage,"session_identity",
                              return_value={"identity_sha256":"f"*64}),
            mock.patch.object(sessions.bootstrap.scenario,"normalize",
                              return_value=self.normalized)
        ):
            return sessions.store_selected_fresh_session(
                self.user,pathlib.Path(self.fixture.fx.dir.name)/"separate",
                self.binary,"c"*40,self.static,
                selected_source=self.selected,
                source_catalog_path=self.source,
                installed_manifest_sha256=self.install)

    def test_selected_session_store_persists_only_new_full_identity(self):
        folder=self._stored()
        seal=__import__("json").loads(
            (folder/"V106_SESSION_IDENTITY.json").read_text("utf8"))
        self.assertEqual(seal["schema"],sessions.SCHEMA)
        self.assertEqual(seal["user"],self.user)
        self.assertIn("v435_selected_source_identity",seal)
        self.assertEqual(digest(seal)[:20],folder.name)
        self.assertTrue((folder/"user.json").is_file())
        self.assertFalse((folder/"generated"/"manifest.json").exists())

    def test_selected_session_store_is_idempotent_and_rejects_user_drift(self):
        folder=self._stored()
        self.assertEqual(self._stored(),folder)
        (folder/"user.json").write_text("{}\n",encoding="utf8")
        with self.assertRaisesRegex(sessions.SessionBlocked,
                                    "EXISTING_SEALED_SESSION_CHANGED"):
            self._stored()

    def test_selected_worker_missing_native_manifest_fails_without_dps(self):
        folder=self._stored()
        with mock.patch.object(sessions.bootstrap.entry,"run_manifest",
                               side_effect=AssertionError("NO_NATIVE")):
            self.assertEqual(sessions.worker(
                folder,self.binary,"c"*40,self.static),3)
        self.assertFalse((folder/"generated"/"manifest.json").exists())

    def test_selected_worker_changed_static_cache_bytes_rejected_pre_native(self):
        folder=self._stored()
        self.static.write_bytes(self.static.read_bytes()+b"\n")
        with mock.patch.object(sessions.bootstrap.entry,"run_manifest",
                               side_effect=AssertionError("NO_NATIVE")):
            self.assertEqual(sessions.worker(
                folder,self.binary,"c"*40,self.static),3)

if __name__=="__main__":
    unittest.main()
