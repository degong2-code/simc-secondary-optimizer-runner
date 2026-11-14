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
        # This sealed v212 fixture has explicit O=0; a hand-only positive
        # request must not be silently assigned this no-oil environment.
        controls["oil_hands"]=[]
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

    def test_user_pinned_installed_build_reaches_sealed_v212_profile(self):
        """Positive selection: same exact build to short/long-run core.

        The original v212 owner and session SHA are reused; no SimC starts.
        """
        self.remember()
        source=self.jobs._verified_fresh_profile_result
        binary=self.root/"pinned-simc.exe"
        binary.write_bytes(b"no-native")
        controls=web.sessions.standard_controls()
        controls["oil_hands"]=[]
        params=web.UserRequest(
            controls=controls,binary=str(binary),revision="abcdef0",
            current_season_product=True,
            installed_season_game_build=self.build)
        folder=self.root/("a"*20)
        folder.mkdir()
        plan={"plan":{"class":"paladin","spec":"retribution",
                      "base_B":3107,"fixed_O":{},"final_T":3107,
                      "native_limit":6}}
        with (mock.patch.object(self.jobs,"load_fresh_profile_for_user",
                                return_value=source) as restore,
              mock.patch.object(web.retail_build_source,"discover",
                                side_effect=AssertionError("NO_LIVE_BUILD_GUESS")),
              mock.patch.object(web.sessions,"store_session",
                                return_value=folder) as seal,
              mock.patch.object(web.profile_stage,"build_or_reuse",
                                return_value=(plan,{})),
              mock.patch.object(self.jobs,"_fresh_environment_summary",
                                return_value={"status":"READY"})):
            response=self.jobs.plan(params)
        self.assertEqual(response["status"],"READY_ZERO_NATIVE")
        self.assertEqual(response["native_calls"],0)
        restore.assert_called_once_with(
            334,self.build,selected_oil_hands=[],
            selected_oil_item_ids_by_hand=None)
        self.assertEqual(seal.call_args.kwargs[
            "fresh_installed_manifest_sha256"],self.digest)

    def test_manual_final_t_changes_real_v106_session_cache_identity(self):
        """User-facing target must never reuse a different-T DPS session."""
        fake=self.root/"simc.bin"
        fake.write_bytes(b"native-not-executed")
        variants=[]
        for chosen in (None,3107,3500,3501):
            controls=web.sessions.standard_controls()
            controls["final_T"]=chosen
            user=web.sessions.user_scenario(controls)
            self.assertEqual(user["target"]["final_T"],chosen)
            with (
                mock.patch.object(web.sessions,"source_catalog_identity",
                    return_value={"source_catalog_sha256":"c"*64}),
                mock.patch.object(web.sessions.profile_stage,
                    "session_identity",
                    return_value={"identity_sha256":"e"*64})
            ):
                key,identity=web.sessions.session_key(
                    user,fake,"abcdef0",current_season_product=True,
                    source_catalog_path=self.catalog,
                    fresh_installed_manifest_sha256=self.digest)
            self.assertEqual(identity[
                "fresh_v212_installed_manifest_sha256"],self.digest)
            self.assertEqual(identity["user"]["target"]["final_T"],chosen)
            variants.append(key)
        self.assertEqual(len(set(variants)),len(variants))

    def test_exact_oil_id_uses_verified_installed_variant_not_hand_guess(self):
        """Exact oil IDs require the matching signed v212 variant, not O=0."""
        self.remember()
        with mock.patch.object(
            web.environment_manifest,"verify_fresh_installed_environment"
        ):
            self.jobs.persist_verified_fresh_profile()
        selected={"main_hand":245678}
        # An old O=0 install and one selected-O install coexist. The direct
        # per-receipt path must never take a first-match shortcut.
        digest="c"*64
        docs=self.installed.parent
        chosen=docs/("v212_installed_"+digest[:20]+".json")
        chosen.write_text(json.dumps({
            "manifest_sha256":digest,"game_build":self.build,
            "target_ilevel":334,
            "official_O_physical_source":{
                "selected_oil_item_ids_by_hand":selected}}))
        (docs/("v113_profile_"+digest[:20]+".json")).write_text(
            json.dumps({"environment_result":{}}))
        with (
            mock.patch.object(
                web.environment_manifest,"verify_fresh_installed_environment"),
            mock.patch.object(
                web.environment_build,
                "find_verified_installed_season_environment",
                return_value={"installed_manifest_sha256":digest}) as lookup,
            mock.patch.object(
                self.jobs,"restore_verified_fresh_profile",
                return_value={"verified_target_ilevel":334}) as restore
        ):
            result=self.jobs.load_fresh_profile_for_user(
                334,self.build,selected_oil_hands=["main_hand"],
                selected_oil_item_ids_by_hand=selected)
        self.assertEqual(result["verified_target_ilevel"],334)
        lookup.assert_called_once_with(
            self.jobs.root,334,expected_game_build=self.build,
            selected_oil_item_ids_by_hand=selected,
            expected_installed_manifest_sha256=digest)
        restore.assert_called_once_with(
            target_ilevel=334,game_build=self.build,
            selected_oil_item_ids_by_hand=selected,
            expected_installed_manifest_sha256=digest,
            required_gem_layout=None)

    def test_exact_oil_selection_requires_same_hands_and_real_install(self):
        """No O=0 substitution or legacy fallback for a named positive oil."""
        fake=self.root/"simc.exe"
        fake.write_bytes(b"never executed")
        controls=web.sessions.standard_controls()
        controls["oil_hands"]=["main_hand"]
        form=web.UserRequest(
            controls=controls,binary=str(fake),revision="abcdef0",
            current_season_product=True,
            selected_oil_item_ids_by_hand={"off_hand":245678})
        with self.assertRaises(web.HTTPException) as error:
            self.jobs.plan(form)
        self.assertEqual(error.exception.status_code,422)
        self.assertEqual(error.exception.detail["code"],
                         "WEB_FRESH_EXACT_OIL_HAND_ID_SELECTION_INVALID")
        form=form.model_copy(update={
            "selected_oil_item_ids_by_hand":{"main_hand":245678}})
        with self.assertRaises(web.HTTPException) as error:
            self.jobs.plan(form)
        self.assertEqual(error.exception.detail["code"],
                         "WEB_FRESH_SELECTED_OIL_ITEM_IDS_NOT_INSTALLED")
        longrun=web.LongRunStartRequest(
            controls=controls,binary=str(fake),revision="abcdef0",
            selected_oil_item_ids_by_hand={"main_hand":245678})
        self.assertEqual(longrun.selected_oil_item_ids_by_hand,
                         {"main_hand":245678})

    def test_saved_session_restores_exact_oil_ids_using_existing_sealed_proof(self):
        """Read-only form restore cannot invent a different physical oil."""
        folder=self.root/("e"*20)
        generated=folder/"generated"
        generated.mkdir(parents=True)
        controls=web.sessions.standard_controls()
        controls["oil_hands"]=["main_hand"]
        user=web.sessions.user_scenario(controls)
        (folder/"user.json").write_text(json.dumps(user))
        identity={"schema":web.sessions.SCHEMA,"user":user,
                  "simc_revision":"abcdef0",
                  "fresh_v212_installed_manifest_sha256":self.digest}
        (folder/"V106_SESSION_IDENTITY.json").write_text(json.dumps(identity))
        manifest={"native_revision":"abcdef0",
                  "native_binary":"fake-simc-not-executed",
                  "static_cache_json":None}
        (generated/"manifest.json").write_text(json.dumps(manifest))
        selected={"main_hand":245678}
        summary={"fresh_v212_installed_manifest_sha256":self.digest,
                 "game_build":self.build}
        with (
            mock.patch.object(self.jobs,"_read_environment_summary",
                              return_value=summary) as read,
            mock.patch.object(self.jobs,"_verify_environment_dependencies",
                              return_value=selected) as checked
        ):
            result=self.jobs.inputs(folder)
        self.assertEqual(result["verified_oil_item_ids_by_hand"],selected)
        self.assertEqual(result["installed_season_game_build"],self.build)
        self.assertFalse(result["native_called"])
        read.assert_called_once_with(folder)
        checked.assert_called_once_with(summary,folder)
        identity.pop("fresh_v212_installed_manifest_sha256")
        (folder/"V106_SESSION_IDENTITY.json").write_text(json.dumps(identity))
        with mock.patch.object(
            self.jobs,"_verify_environment_dependencies",
            side_effect=AssertionError("OLD_SESSION_SHOULD_NOT_VERIFY_FRESH")
        ):
            old=self.jobs.inputs(folder)
        self.assertEqual(old["verified_oil_item_ids_by_hand"],{})
        self.assertIsNone(old["installed_season_game_build"])
        self.assertFalse(old["native_called"])

    def test_start_resume_uses_original_v217_installed_manifest_sha(self):
        folder=self.root/("f"*20)
        folder.mkdir()
        (folder/"V106_SESSION_IDENTITY.json").write_text(json.dumps(
            {"fresh_v212_installed_manifest_sha256":self.digest}))
        summary={"fresh_v212_installed_manifest_sha256":self.digest,
                 "target_ilevel":334,"game_build":self.build}
        with mock.patch.object(web.environment_manifest,
                               "verify_fresh_installed_environment"), \
             mock.patch.object(web.environment_build,
                "find_verified_installed_season_environment",
                return_value={"installed_manifest_sha256":self.digest}):
            self.jobs._verify_environment_dependencies(summary,folder)
        (folder/"V106_SESSION_IDENTITY.json").write_text(json.dumps(
            {"fresh_v212_installed_manifest_sha256":"f"*64}))
        with mock.patch.object(web.environment_manifest,
                               "verify_fresh_installed_environment"), \
             mock.patch.object(web.environment_build,
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
            controls=web.sessions.standard_controls()
            controls["oil_hands"]=[]
            form=web.UserRequest(controls=controls,
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


    def test_v413_fresh_flask_variant_beyond_64_reuses_saved_profile(self):
        root=self.installed.parent
        self.installed_doc["official_F_physical_source"]={
            "physical_item_id":9001}
        self.installed.write_text(json.dumps(self.installed_doc),encoding="utf8")
        (root/("v113_profile_"+self.digest[:20]+".json")).write_text(
            json.dumps({"environment_result":self.original}),encoding="utf8")
        for i in range(65):
            digest=f"{i+1:020x}"+"b"*44
            old={**self.installed_doc,"manifest_sha256":digest,
                 "official_F_physical_source":{"physical_item_id":1}}
            (root/("v212_installed_"+digest[:20]+".json")).write_text(
                json.dumps(old),encoding="utf8")
        with mock.patch.object(web.environment_manifest,
                 "verify_fresh_installed_environment"), \
             mock.patch.object(web.environment_build,
                 "find_verified_installed_season_environment",
                 return_value={"installed_manifest_sha256":self.digest}), \
             mock.patch.object(self.jobs,"restore_verified_fresh_profile",
                 return_value={"verified_target_ilevel":334}) as restored:
            value=self.jobs.load_fresh_profile_for_user(
                334,explicit_build=self.build,selected_flask_item_id=9001)
        self.assertEqual(value["verified_target_ilevel"],334)
        self.assertEqual(restored.call_count,1)
        self.assertEqual(restored.call_args.kwargs[
            "expected_installed_manifest_sha256"],self.digest)

    def test_fresh_resume_uses_exact_install_sha_even_with_other_same_oil(self):
        session=self.root/("d"*20)
        session.mkdir()
        (session/"V106_SESSION_IDENTITY.json").write_text(json.dumps({
            "fresh_v212_installed_manifest_sha256":self.digest}),encoding="utf8")
        summary={"game_build":self.build,"target_ilevel":334,
                 "fresh_v212_installed_manifest_sha256":self.digest}
        with mock.patch.object(web.environment_manifest,
                "verify_fresh_installed_environment"), \
             mock.patch.object(web.environment_build,
                "find_verified_installed_season_environment",
                return_value={"installed_manifest_sha256":self.digest}) as find:
            selected=self.jobs._verify_environment_dependencies(summary,session)
        self.assertEqual(selected,{})
        self.assertEqual(find.call_args.kwargs[
            "expected_installed_manifest_sha256"],self.digest)
        self.assertEqual(find.call_args.kwargs[
            "selected_oil_item_ids_by_hand"],{})

    def test_fresh_special_L_uses_selected_catalog_and_keeps_v212_environment(self):
        self.remember()
        verified=self.jobs._verified_fresh_profile_result
        controls=web.sessions.standard_controls()
        controls["special_items"]=[{
            "slot":"back","item_id":159288,"options":{}}]
        params=web.UserRequest(
            controls=controls,binary=str(self.root/"unused-simc"),
            revision="abcdef0",current_season_product=True,
            installed_season_game_build=self.build)
        folder=self.root/("d"*20)
        folder.mkdir()
        ready={"schema":"v113_web_fresh_v212_installed_session_v1",
               "fresh_v212_installed_manifest_sha256":self.digest}
        receipt={"path":"start-receipts/v208-selected.json",
                 "receipt_sha256":"c"*64}
        with mock.patch.object(self.jobs,"load_fresh_profile_for_user",
                return_value=verified) as select, \
             mock.patch.object(self.jobs,"default_static_cache",
                return_value=None), \
             mock.patch.object(web.exact_L,"hydrate",return_value={
                "static_cache_path":str(self.root/"static-L.json"),
                "start_receipt":{},"native_new_calls":0,
                "cache_reused":1}) as hydrate, \
             mock.patch.object(self.jobs,"plan",return_value={
                "session_id":folder.name,
                "environment_manifest":ready}) as plan, \
             mock.patch.object(self.jobs,"folder",return_value=folder), \
             mock.patch.object(web.exact_L,"write_start_receipt",
                return_value=receipt), \
             mock.patch.object(self.jobs,"_record_v208_receipt"), \
             mock.patch.object(self.jobs,"_seal_environment_manifest",
                side_effect=AssertionError("PACKAGED_SEASON_MUST_NOT_RUN")):
            prepared=self.jobs.prepare_with_internal_special_L(params)
        self.assertEqual(prepared[2],ready)
        self.assertEqual(prepared[3],receipt)
        self.assertEqual(hydrate.call_args.kwargs[
            "source_catalog_path"],self.catalog)
        self.assertEqual(hydrate.call_args.kwargs["existing"],None)
        self.assertEqual(plan.call_count,1)
        self.assertEqual(select.call_args.args[:2],(334,self.build))

    def test_missing_pinned_v212_installed_source_blocks_before_special_L_native(self):
        controls=web.sessions.standard_controls()
        controls["special_items"]=[{
            "slot":"back","item_id":159288,"options":{}}]
        params=web.UserRequest(
            controls=controls,binary=str(self.root/"unused-simc"),
            revision="abcdef0",current_season_product=True,
            installed_season_game_build=self.build)
        with mock.patch.object(self.jobs,"load_fresh_profile_for_user",
                return_value=None), \
             mock.patch.object(self.jobs,"default_static_cache",
                return_value=None), \
             mock.patch.object(web.exact_L,"hydrate",
                side_effect=AssertionError("NO_UNVERIFIED_SPECIAL_L_NATIVE")) as native:
            with self.assertRaises(web.HTTPException) as raised:
                self.jobs.prepare_with_internal_special_L(params)
        self.assertEqual(raised.exception.status_code,422)
        self.assertEqual(raised.exception.detail["code"],
                         "WEB_SELECTED_INSTALLED_SEASON_BUILD_NOT_FOUND")
        native.assert_not_called()

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



class FreshOptionalConsumableForwarding(unittest.TestCase):
    def _user(self, **chosen):
        controls=web.sessions.standard_controls()
        controls["consumable_choices"].update(chosen)
        return web.sessions.user_scenario(controls)

    def test_default_uses_disabled_and_selected_simc_tokens_survive(self):
        serialize=web.profile_stage._verified_fresh_season_consumables
        self.assertEqual(serialize(self._user()),{
            "food":"disabled","potion":"disabled","augmentation":"disabled"})
        chosen=self._user(food="royal_roast",
                          potion="potion_of_recklessness_2",
                          augmentation="void_touched")
        self.assertEqual(serialize(chosen),{
            "food":"royal_roast",
            "potion":"potion_of_recklessness_2",
            "augmentation":"void_touched"})

    def test_unadmitted_option_never_silently_changes_profile(self):
        serialize=web.profile_stage._verified_fresh_season_consumables
        with self.assertRaisesRegex(web.bootstrap.UserScenarioBlocked,
                                    "FRESH_SEASON_FLASK_DIAMOND_OR_MODULE_NOT_ADMITTED"):
            serialize(self._user(omnium_talents="row4_crit"))
        with self.assertRaisesRegex(web.bootstrap.UserScenarioBlocked,
                                    "FRESH_SEASON_SIMC_OPTION_UNSUPPORTED"):
            serialize(self._user(food="unverified_food_item"))

    def test_stage_passes_exact_user_choices_to_existing_v098_builder(self):
        user=self._user(food="royal_roast",augmentation="void_touched")
        with tempfile.TemporaryDirectory() as scratch:
            folder=pathlib.Path(scratch)/("e"*20)
            folder.mkdir()
            (folder/"V106_SESSION_IDENTITY.json").write_text(json.dumps(
                {"profile_stage":{"identity_sha256":"c"*64}}))
            recorded={}
            def source_plan(*args,**kwargs):
                recorded.update(kwargs)
                generated=pathlib.Path(args[1])
                return {"schema":web.bootstrap.SCHEMA,
                        "generated_manifest":str(generated/"manifest.json"),
                        "plan":{"class":"paladin","spec":"retribution"}}
            def stage(*,execute,**kwargs):
                result=execute()
                return {"result":result,"status":"EXECUTED_AND_SEALED",
                        "executed":True,"reused":False,"recovered":False,
                        "input_fingerprint":"a"*64,"receipt_sha256":"b"*64,
                        "output_count":5,"output_bytes":0,"receipt_writes":2}
            with (
                mock.patch.object(web.profile_stage.bootstrap,
                                  "run_from_verified_environment_build",
                                  side_effect=source_plan) as builder,
                mock.patch.object(web.profile_stage.engine,
                                  "execute_stage",side_effect=stage)
            ):
                data,receipt=web.profile_stage.build_or_reuse(
                    user=user,session_folder=folder,binary=folder/"simc",
                    revision="abcdeff",static_cache=None,
                    current_season_product=True,
                    verified_fresh_environment_result={
                        "normal_build_entry":True})
            self.assertEqual(builder.call_count,1)
            self.assertEqual(recorded["season_controls"],{
                "food":"royal_roast","potion":"disabled",
                "augmentation":"void_touched"})
            self.assertFalse(recorded["execute"])
            self.assertEqual(receipt["native_calls"],0)




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
