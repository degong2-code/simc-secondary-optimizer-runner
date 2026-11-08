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
            verify.assert_called_once_with(root,334,
                expected_game_build="12.1.5.70783")
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
