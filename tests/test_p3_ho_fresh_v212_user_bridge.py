"""P3-HO: original v212 installed -> v096 source adapter (offline).

Synthetic installed documents and a mocked v217 lookup exercise only this
adapter's accounting; they are NOT real provenance, SimC or a product READY.
The original full v217/v212 verifier is unchanged and required in production.
"""
import copy
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v061_scenario_contract as contract
import v096_unified_product_entry as entry
import v212_environment_manifest as installed
import v216_environment_build_coordinator as coordinator
from test_v091_weapon_oil_external_adapter import frost


class FreshInstalledV096Bridge(unittest.TestCase):
    def make_case(self,root):
        profile,cfg,_=frost(root)
        cfg["target"]={"mode":"manual_total","ilevel":334,
                       "manual_total":3150,
                       "manual_total_scope":contract.MANUAL_TOTAL_SCOPE}
        normalized=contract.normalize(cfg)
        J=normalized["budget"]["J"]
        F=normalized["budget"]["F"]
        zeros={stat:0 for stat in contract.STATS}
        flask=dict(zeros)
        flask["haste_rating"]=F
        token="flask_of_audited_haste_3"
        profile+="\nflask="+token+"\n"
        meta={"physical_item_id":241324,"simc_input_token":token,
              "crafting_quality":3,"static_CHMV_vector":flask,
              "F_rating":F,"original_F_source_sha256":"a"*64,
              "v278_native_pair_receipt_sha256":["b"*64,"c"*64],
              "source_verification":"EXACT_NATIVE",
              "other_flask_effects_unverified_here":True,
              "source_authentication_created_here":False}
        payload={"schema":installed.FRESH_SEASON_INSTALLED_SCHEMA,
              "status":"FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY",
              "game_build":"12.1.5.70783","simc_revision":"7bc10711b5",
              "target_ilevel":334,
              "source_catalog_manifest_sha256":"a"*64,
              "source_catalog_artifact_sha256":"b"*64,
              "staged_source_environment_sha256":"c"*64,
              "original_v216_preflight_sha256":"d"*64,
              "original_v217_stage_receipts":{},
              "trusted_budget_evidence_sha256":"e"*64,
              "trusted_budget_component_source_identities":{
                  k:{"source_sha256":str(i)*64,
                     "source_verification":"VALID_SAME_SEASON_SOURCE"}
                  for i,k in enumerate(("G","J","F","O"),1)},
              "official_G":3150-J-F,"official_effective_G":3150-J-F,
              "official_J":J,"official_F":F,
              "official_F_physical_source":meta,
              "official_O":zeros,"official_B":3150,"official_T":3150,
              "manual_final_T_authoritative":False,
              "v222_reconciled_budget":{},
              "original_v196_prepared_options_sha256":"f"*64,
              "published_verified_options":[],
              "published_verified_option_count":0,
              "optional_quality_pending_item_ids":[],
              "optional_other_proof_pending_by_id":{},
              "optional_items_do_not_block_base":True,
              "environment_ready":True,"environment_installed":True,
              "options_published":True,
              "dps_optimization_required":False,
              "user_profile_or_trinkets_required":False,
              "source_authentication_created_here":False,
              "native_calls":0,"network_calls":0}
        doc={**payload,"manifest_sha256":installed.sha(
            installed.canonical(payload).encode("utf8"))}
        self.assertTrue(installed.verify_fresh_installed_environment(doc))
        folder=root/"_fresh_season_sources"/"wago_12.1.5.70783"/"fresh_source"
        folder.mkdir(parents=True)
        path=folder/("v212_installed_"+doc["manifest_sha256"][:20]+".json")
        path.write_text(installed.canonical(doc)+"\n",encoding="utf8")
        selection={"schema":entry.FRESH_SEASON_SCHEMA,
                   "installed_environment_path":str(path),
                   "installed_manifest_sha256":doc["manifest_sha256"],
                   "oil_by_hand":{}}
        attested={"environment_ready":True,"environment_installed":True,
                  "installed_manifest_sha256":doc["manifest_sha256"],
                  "stage_receipt_sha256":"a"*64}
        return path,doc,cfg,flask,profile,selection,attested

    def test_real_verifier_hook_and_original_B_F_O_identity(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            path,doc,cfg,flask,profile,selection,attested=self.make_case(root)
            with mock.patch.object(coordinator,
                    "find_verified_installed_season_environment",
                    return_value=attested) as verify:
                result=entry._admitted_fresh_season_source(
                    manifest_path=root/"manifest.json",season=selection,
                    revision="different-runtime-revision",
                    user_scenario=cfg,flask_F=flask,oil_hands=[],
                    profile=profile)
            # Windows TemporaryDirectory may expose 8.3 alias spelling;
            # v096 resolves the real installed parent before its finder call.
            verify.assert_called_once_with(
                root.resolve(),334,expected_game_build="12.1.5.70783",
                expected_installed_manifest_sha256=doc["manifest_sha256"])
            self.assertTrue(result["fresh_v212_installed"])
            self.assertEqual(result["season_budget"]["base_B"],3150)
            self.assertEqual(result["season_source_identity"][
                "environment_build_receipt_sha256"],doc["manifest_sha256"])
            self.assertEqual(result["oil_by_hand"],{})

    def test_no_v217_proof_or_changed_manifest_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            path,doc,cfg,flask,profile,selection,attested=self.make_case(root)
            with mock.patch.object(coordinator,
                    "find_verified_installed_season_environment",
                    return_value=None):
                with self.assertRaisesRegex(entry.EntryBlocked,
                       "FRESH_SEASON_V217_INSTALLED_PROOF_NOT_FOUND"):
                    entry._admitted_fresh_season_source(
                        manifest_path=root/"manifest.json",season=selection,
                        revision="runtime",user_scenario=cfg,flask_F=flask,
                        oil_hands=[],profile=profile)
            wrong=copy.deepcopy(selection)
            wrong["installed_manifest_sha256"]="0"*64
            with self.assertRaisesRegex(entry.EntryBlocked,
                       "FRESH_SEASON_INSTALLED_MANIFEST_IDENTITY_DRIFT"):
                entry._admitted_fresh_season_source(
                    manifest_path=root/"manifest.json",season=wrong,
                    revision="runtime",user_scenario=cfg,flask_F=flask,
                    oil_hands=[],profile=profile)

    def test_physical_F_or_oil_or_manual_B_drift_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            path,doc,cfg,flask,profile,selection,attested=self.make_case(root)
            with mock.patch.object(coordinator,
                    "find_verified_installed_season_environment",
                    return_value=attested):
                with self.assertRaisesRegex(entry.EntryBlocked,
                      "FRESH_SEASON_SELECTED_PHYSICAL_F_PROFILE_DRIFT"):
                    entry._admitted_fresh_season_source(
                        manifest_path=root/"manifest.json",season=selection,
                        revision="runtime",user_scenario=cfg,
                        flask_F=flask,oil_hands=[],
                        profile=profile.replace("flask=flask_of_audited_haste_3",
                                                "flask=disabled"))
                with self.assertRaisesRegex(entry.EntryBlocked,
                      "FRESH_SEASON_TYPED_GJFO_B_T_O_DRIFT"):
                    entry._admitted_fresh_season_source(
                        manifest_path=root/"manifest.json",season=selection,
                        revision="runtime",user_scenario=cfg,
                        flask_F=flask,oil_hands=["main_hand"],
                        profile=profile)
                changed=copy.deepcopy(cfg)
                changed["target"]["manual_total"]=3151
                with self.assertRaisesRegex(entry.EntryBlocked,
                      "FRESH_SEASON_TYPED_GJFO_B_T_O_DRIFT"):
                    entry._admitted_fresh_season_source(
                        manifest_path=root/"manifest.json",season=selection,
                        revision="runtime",user_scenario=changed,
                        flask_F=flask,oil_hands=[],profile=profile)


    def signed_budget_case(self,root):
        """Build one synthetic v212 document with its actual v222 budget row."""
        path,doc,cfg,flask,profile,selection,attested=self.make_case(root)
        old_path=path
        zeros={stat:0 for stat in contract.STATS}
        budget={
            "reference_G":doc["official_G"],
            "effective_G":doc["official_effective_G"],
            "J":doc["official_J"],"F":doc["official_F"],
            "fixed_O":dict(zeros),"fixed_L":dict(zeros),
            "fixed_E":dict(zeros),
            "reference_B":doc["official_B"],
            "base_B":doc["official_B"],"final_T":doc["official_T"],
            "game_build":doc["game_build"],
            "target_ilevel":doc["target_ilevel"],
            "source_catalog_manifest_sha256":
                doc["source_catalog_manifest_sha256"],
            "source_catalog_artifact_sha256":
                doc["source_catalog_artifact_sha256"],
            "manual_final_T_authoritative":False
        }
        payload={k:v for k,v in doc.items() if k!="manifest_sha256"}
        payload["v222_reconciled_budget"]=budget
        doc={**payload,"manifest_sha256":installed.sha(
            installed.canonical(payload).encode("utf8"))}
        self.assertTrue(installed.verify_fresh_installed_environment(doc))
        path=old_path.with_name(
            "v212_installed_"+doc["manifest_sha256"][:20]+".json")
        old_path.unlink()
        path.write_text(installed.canonical(doc)+"\n",encoding="utf8")
        selection["installed_environment_path"]=str(path)
        selection["installed_manifest_sha256"]=doc["manifest_sha256"]
        attested["installed_manifest_sha256"]=doc["manifest_sha256"]
        return path,doc,cfg,flask,profile,selection,attested

    def test_user_final_T_retargets_only_session_and_separates_cache_source(self):
        import v222_season_budget_contract as budget
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            path,doc,cfg,flask,profile,selection,proof=(
                self.signed_budget_case(root))
            original_bytes=path.read_bytes()
            numeric=budget.retarget_verified_install(
                document=doc,manual_final_T=3500)
            self.assertEqual(numeric["base_B"],3500)
            self.assertEqual(numeric["final_T"],3500)
            self.assertTrue(numeric["manual_final_T_authoritative"])
            self.assertEqual(numeric["installed_reference_T"],3150)
            selected=copy.deepcopy(selection)
            selected["user_final_T"]=3500
            requested=copy.deepcopy(cfg)
            requested["target"]["manual_total"]=3500
            with mock.patch.object(coordinator,
                 "find_verified_installed_season_environment",
                 return_value=proof):
                baseline=entry._admitted_fresh_season_source(
                    manifest_path=root/"manifest.json",season=selection,
                    revision="runtime-updated",user_scenario=cfg,
                    flask_F=flask,oil_hands=[],profile=profile)
                manual=entry._admitted_fresh_season_source(
                    manifest_path=root/"manifest.json",season=selected,
                    revision="runtime-updated",user_scenario=requested,
                    flask_F=flask,oil_hands=[],profile=profile)
                self.assertEqual(manual["season_budget"]["base_B"],3500)
                self.assertEqual(manual["season_budget"]["final_T"],3500)
                self.assertEqual(manual["user_manual_final_T"],3500)
                self.assertNotEqual(
                    manual["season_source_identity"]["source_input_sha256"],
                    baseline["season_source_identity"]["source_input_sha256"])
                with self.assertRaisesRegex(
                     entry.EntryBlocked,"FRESH_SEASON_TYPED_GJFO_B_T_O_DRIFT"):
                    entry._admitted_fresh_season_source(
                        manifest_path=root/"manifest.json",season=selected,
                        revision="runtime-updated",user_scenario=cfg,
                        flask_F=flask,oil_hands=[],profile=profile)
            self.assertEqual(path.read_bytes(),original_bytes)
            self.assertEqual(doc["official_B"],3150)

    def test_manual_T_too_low_and_fixed_L_E_are_not_silently_dropped(self):
        import v222_season_budget_contract as budget
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            path,doc,cfg,flask,profile,selection,proof=(
                self.signed_budget_case(root))
            floor=doc["official_J"]+doc["official_F"]
            with self.assertRaisesRegex(
                 budget.SeasonBudgetBlocked,"GJFO_FIXED_MINIMA_EXCEED_TOTAL"):
                budget.retarget_verified_install(
                    document=doc,manual_final_T=floor-1)
            constrained=copy.deepcopy(doc)
            constrained["v222_reconciled_budget"]["fixed_L"][
                "crit_rating"]=250
            constrained["v222_reconciled_budget"]["fixed_E"][
                "haste_rating"]=50
            with self.assertRaisesRegex(
                 budget.SeasonBudgetBlocked,"GJFO_FIXED_MINIMA_EXCEED_TOTAL"):
                budget.retarget_verified_install(
                    document=constrained,manual_final_T=floor+299)
            mismatch=copy.deepcopy(doc)
            mismatch["v222_reconciled_budget"]["J"]+=1
            with self.assertRaisesRegex(
                 budget.SeasonBudgetBlocked,
                 "GJFO_MANUAL_INSTALLED_ORIGINAL_BUDGET_DRIFT"):
                budget.retarget_verified_install(
                    document=mismatch,manual_final_T=3500)

    def test_v098_manual_preview_uses_signed_budget_not_unadmitted_guess(self):
        import v098_target_user_scenario_bootstrap as bootstrap
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            path,doc,cfg,flask,profile,selection,proof=(
                self.signed_budget_case(root))
            stage_root=path.parent.parent
            candidate=stage_root/"case_G.json"
            candidate.write_text("{}")
            gear=root/"gear.json"
            tier=root/"tier.json"
            gear.write_text(json.dumps({"season_build":doc["game_build"]}))
            tier.write_text(json.dumps({"retail_build":doc["game_build"]}))
            catalog=root/"catalog.json"
            catalog.write_text("{}")
            original_calc={
                "game_build":doc["game_build"],
                "simc_revision":doc["simc_revision"],
                "target_ilevel":334,"numeric_preview_only":True,
                "J":doc["official_J"],"F":doc["official_F"],
                "base_B":doc["official_B"],"final_T":doc["official_T"],
                "fixed_O":doc["official_O"],
                "source_catalog_manifest_sha256":
                    doc["source_catalog_manifest_sha256"],
                "source_catalog_artifact_sha256":
                    doc["source_catalog_artifact_sha256"]}
            compilation={
                "status":"FRESH_V191_V211_V213_COMPILED_UNADMITTED",
                "source_catalog_path":str(catalog),
                "stage_root":str(stage_root),
                "simc_revision":doc["simc_revision"],
                "v191_original_gear_tier_source_paths":{
                    "catalog":str(catalog),"gear":str(gear),"tier":str(tier)},
                "v098_source_only_profile_inputs_unadmitted":{
                    "schema":"v098_internal_season_profile_inputs_v1",
                    "v216_numeric_preview":{
                        "schema":"v216_zero_history_selected_v222_numeric_preview_v1",
                        "status":"SELECTED_GJFO_V222_ARITHMETIC_PREVIEW_UNADMITTED",
                        "numeric_preview_only":True,"environment_ready":False,
                        "calculation":original_calc}},
                "verified_environment_install":{
                    "status":"FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY",
                    "environment_ready":True,"environment_installed":True,
                    "stage_output_path":str(path),
                    "manifest_sha256":doc["manifest_sha256"]},
                "preflight_sha256":"3"*64}
            env={"normal_build_entry":True,
                 "zero_history_build":{"environment_ready":True},
                 "source_compilation":compilation,
                 "fresh_one_spec_simc_representative":{
                     "candidate_path":str(candidate)}}
            captured={}
            def build(*args,**kwargs):
                captured.update(kwargs)
                return {
                    "original_v191_gear_tier_source_unadmitted":{
                        "source_catalog_artifact_sha256":
                            doc["source_catalog_artifact_sha256"],
                        "source_catalog_manifest_sha256":
                            doc["source_catalog_manifest_sha256"]}}
            user={"target":{"ilevel":334,"final_T":3500}}
            settings={"default_consumables":{
                "gem_budget_J":doc["official_J"],
                "flask_budget_F":doc["official_F"],
                "omnium_talents":None}}
            # This older test validates ONLY signed manual-T arithmetic.
            # Its synthetic "{}" one-spec G fixture is not a real source
            # receipt; bypass THAT unrelated source helper in this isolated
            # unit test, never weaken the production SHA fail-closed policy.
            with (mock.patch.object(bootstrap,"build",side_effect=build),
                  mock.patch.object(
                      bootstrap,"_choose_user_specific_fresh_G_source",
                      return_value=(None,True)),
                  mock.patch.object(
                      bootstrap,"_select_v216_source_only_user_spec",
                      return_value={"selected_G_slot_ids":{}})):
                result=bootstrap.preview_from_environment_build(
                    user,root/"session",root/"fake_simc","runtime",
                    environment_result=env,season_settings=settings)
            adjusted=captured["season_profile_inputs"][
                "v216_numeric_preview"]["calculation"]
            self.assertEqual(adjusted["base_B"],3500)
            self.assertEqual(adjusted["final_T"],3500)
            self.assertTrue(adjusted["manual_final_T_authoritative"])
            self.assertEqual(original_calc["final_T"],3150)
            self.assertEqual(doc["official_T"],3150)
            self.assertTrue(result["fresh_installed_v212_source_reused"])


class OneSpecNativeRepresentativeBridge(unittest.TestCase):
    def test_original_v232_selected_G_replaces_missing_common_neck(self):
        import v098_target_user_scenario_bootstrap as boot
        import v169_source_first_representative_stage as source_first
        import v232_simc_only_ordinary_representative as physical
        from tests.test_v287_zero_history_v222_user_budget_bridge import (
            ZeroHistoryPreprofileUserBudget)
        bundle=ZeroHistoryPreprofileUserBudget().synthetic_future_season_source_bundle()
        cls,spec="paladin","retribution"
        old=source_first.select_class_spec(
            bundle["gear"],bundle["tier"],cls,spec)
        # The physical G candidate is sufficient for the selected-spec
        # serializer, regardless of a global 26-spec plain-neck selector.
        # Do not alter v167's sealed item-count contract in this fixture.
        neck_id=old["common_gear"]["neck"]
        tier_ids=bundle["tier"]["classes"][cls]["pieces"]
        selected={**{slot:tier_ids[slot] for slot in source_first.FOUR},
                  **old["ordinary"],**old["common_gear"],**old["weapons"]}
        candidate={"schema":physical.SCHEMA,
                   "status":"SIMC_SOURCE_PHYSICAL_CANDIDATE_NOT_ACTUAL_SEASON_PROOF",
                   "game_build":bundle["gear"]["season_build"],
                   "simc_revision":"c"*40,
                   "target_ilevel":334,
                   "character":{"class":cls,"spec":spec},
                   "selected_ordinary":old["ordinary"],
                   "selected_common":old["common_gear"],
                   "selected_weapons":old["weapons"],
                   "selected_G_slot_ids":selected}
        candidate["receipt_sha256"]=physical.seed.digest(
            physical.seed.canonical(candidate).encode("utf8"))
        scope=boot._verified_one_spec_G_profile_scope(
            source_bundle=bundle,candidate=candidate,
            selected_key=(cls,spec),target_ilevel=334,source_revision="c"*40)
        self.assertEqual(scope["common_gear"]["neck"],neck_id)
        with self.assertRaisesRegex(
                boot.UserScenarioBlocked,
                "FRESH_V232_SELECTED_G_BUILD_SPEC_OR_ILEVEL_DRIFT"):
            boot._verified_one_spec_G_profile_scope(
                source_bundle=bundle,candidate=candidate,
                selected_key=(cls,spec),target_ilevel=334,
                source_revision="d"*40)

        self.assertEqual(list(scope["specializations"]),["paladin/retribution"])
        coverage=boot._current_season_profile_supplier_coverage(
            scope,"paladin/retribution",one_spec_only=True)
        self.assertEqual(coverage["current_season_profile_supplier_count"],1)
        wrong=copy.deepcopy(candidate)
        wrong["selected_common"]={"neck":999999,
             **{k:v for k,v in wrong["selected_common"].items()
                if k!="neck"}}
        wrong["receipt_sha256"]=physical.seed.digest(
            physical.seed.canonical({
                k:v for k,v in wrong.items() if k!="receipt_sha256"
            }).encode("utf8"))
        with self.assertRaisesRegex(
                boot.UserScenarioBlocked,"FRESH_V232_USER_PHYSICAL_G_SLOT_DRIFT"):
            boot._verified_one_spec_G_profile_scope(
                source_bundle=bundle,candidate=wrong,
                selected_key=(cls,spec),target_ilevel=334,source_revision="c"*40)
        changed=copy.deepcopy(candidate)
        changed["game_build"]="12.2.1.99999"
        changed["receipt_sha256"]=physical.seed.digest(
            physical.seed.canonical({
                k:v for k,v in changed.items() if k!="receipt_sha256"
            }).encode("utf8"))
        with self.assertRaisesRegex(
                boot.UserScenarioBlocked,
                "FRESH_V232_SELECTED_G_BUILD_SPEC_OR_ILEVEL_DRIFT"):
            boot._verified_one_spec_G_profile_scope(
                source_bundle=bundle,candidate=changed,
                selected_key=(cls,spec),target_ilevel=334,source_revision="c"*40)


if __name__=="__main__":
    unittest.main()
