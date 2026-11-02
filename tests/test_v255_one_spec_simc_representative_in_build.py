"""P3-AV: normal Build -> existing v251/v232 one-spec representative stage.

All inputs are synthetic pinned-source fixtures. The v251 bridge is stubbed in
the focused stage test; real tier/SimC bridge coverage remains in v251 tests.
No real Wago, new Native, historical season input, or G promotion.
"""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v216_environment_build_coordinator as build
import v229_simc_only_source_seed as seed
import v231_simc_tier_item_join as tier_source
import v167_product_season_gear_adapter as gear
from tests.test_v229_simc_only_source_seed import BUILD,OLD,REVISION
from tests.test_v232_simc_only_ordinary_representative import make_fixture


class OneSpecInBuild(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.stage=self.root/"stage"
        self.stage.mkdir()
        self.seed=self.root/"seed"
        self.seed.mkdir()
        files=make_fixture()
        for name,raw in files.items():
            (self.seed/name).write_bytes(raw)
        receipt=seed.inventory(
            files,simc_revision=REVISION,expected_build=BUILD,
            previous_game_build=OLD,
            expected_git_blob={k:seed.git_blob(v) for k,v in files.items()})
        (self.seed/seed.RECEIPT).write_text(
            json.dumps(receipt),encoding="utf8")
        self.simc_tier=tier_source.select(
            seed_directory=self.seed,cls="paladin",
            spec="retribution",set_option="season_token_test")
        allowed={
            9020:(5,4,4),9028:(9,4,4),9021:(6,4,4),
            9022:(8,4,4),9023:(2,4,0),9024:(16,4,0),
            9012:(11,4,0),9025:(11,4,0),9010:(17,2,8)}
        rows=[{
            "item_id":iid,"name":f"wago_{iid}",
            "category":"plain_representative_candidate",
            "inventory_type":inv,"class_id":kind,"subclass_id":sub,
            "allowed_class_mask":2,"item_set_id":0,
            "source_kinds":["raid_journal"]
        } for iid,(inv,kind,sub) in sorted(allowed.items())]
        source={
            "schema":gear.SCHEMA,
            "status":"CURRENT_SEASON_CANDIDATE_SELECTION_ONLY",
            "no_old_catalog_seed":True,
            "season_build":BUILD,
            "item_count":len(rows),
            "role_counts":{"plain_representative_candidate":len(rows)},
            "items":rows,
            "not_certified":{"tier_four_set":True,"simc_item_effects":True},
            "new_native_calls":0,"new_api_calls":0}
        self.gear_path=self.root/"v167.json"
        self.gear_path.write_text(json.dumps(source),encoding="utf8")
        self.tier_path=self.root/"v251.json"
        self.tier_path.write_text(json.dumps({
            "schema":build.tier_simc_bridge.SCHEMA,
            "status":"OBSERVED_CURRENT_RAID_CORRELATED_65_PIECE_TIER_CANDIDATE",
            "game_build":BUILD,
            "season_membership_verified":False,
            "environment_ready":False}),encoding="utf8")
        self.fresh_gear={"candidate_path":str(self.gear_path)}
        self.tier_bridge={"candidate_path":str(self.tier_path)}
        self.request={"class":"paladin","spec":"retribution",
                      "target_ilevel":335}

    def invoke(self,seed_directory=None):
        return build._one_spec_ordinary_simc_stage(
            stage_root=self.stage,build=BUILD,
            fresh_gear=self.fresh_gear,
            tier_bridge=self.tier_bridge,
            seed_directory=seed_directory,request=self.request)

    def test_one_spec_existing_simc_representative_and_stage_reuse(self):
        with mock.patch.object(build.tier_simc_bridge,"select_for_simc",
                               return_value={"v231_candidate":self.simc_tier}) as select:
            first=self.invoke(self.seed)
            second=self.invoke(self.seed)
        self.assertEqual(first["status"],
                         "FRESH_ONE_SPEC_SIMC_G_SOURCE_CANDIDATE_PENDING_NATIVE")
        self.assertEqual(second["status"],first["status"])
        self.assertEqual(first["source_stage"]["status"],"EXECUTED_AND_SEALED")
        self.assertEqual(second["source_stage"]["status"],"REUSED_VERIFIED")
        self.assertEqual(select.call_count,1)
        self.assertEqual(first["network_calls_by_stage"],0)
        self.assertEqual(first["native_calls"],0)
        result=json.loads(Path(first["candidate_path"]).read_text())
        self.assertEqual(len(result["selected_G_slot_ids"]),13)
        self.assertEqual(result["selected_G_slot_ids"]["wrists"],9028)
        self.assertEqual(result["selected_G_slot_ids"]["main_hand"],9010)
        self.assertIsNone(result["G"])
        self.assertIsNone(result["B"])
        self.assertIsNone(result["T"])
        self.assertFalse(result["environment_ready"])
        self.assertTrue(result["same_season_membership_not_proven"])

    def test_full_simc_item_source_absence_is_zero_network_pending(self):
        status=self.invoke()
        self.assertEqual(status["status"],
                         "FRESH_ONE_SPEC_FULL_PINNED_SIMC_ITEM_DATA_PENDING")
        self.assertEqual(status["network_calls_by_stage"],0)
        self.assertFalse(status["environment_ready"])
        (self.seed/"item_data.inc").unlink()
        status=self.invoke(self.seed)
        self.assertEqual(status["status"],
                         "FRESH_ONE_SPEC_FULL_PINNED_SIMC_ITEM_DATA_PENDING")
        self.assertEqual(status["network_calls_by_stage"],0)

    def test_wrong_build_and_unsupported_spec_rejected(self):
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "ONE_SPEC_SOURCE_BUILD_OR_PROVENANCE_MISMATCH"):
            build._one_spec_ordinary_simc_stage(
                stage_root=self.stage,build="12.9.9.99999",
                fresh_gear=self.fresh_gear,tier_bridge=self.tier_bridge,
                seed_directory=self.seed,request=self.request)
        self.request={"class":"evoker","spec":"augmentation",
                      "target_ilevel":335}
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "ONE_SPEC_26_DPS_REQUEST_REQUIRED"):
            self.invoke(self.seed)

    def test_only_one_missing_ordinary_slot_yields_pending_not_fake_g(self):
        data=json.loads(self.gear_path.read_text())
        data["items"]=[x for x in data["items"] if x["item_id"]!=9021]
        data["item_count"]=len(data["items"])
        data["role_counts"]["plain_representative_candidate"]=len(data["items"])
        self.gear_path.write_text(json.dumps(data),encoding="utf8")
        with mock.patch.object(build.tier_simc_bridge,"select_for_simc",
                               return_value={"v231_candidate":self.simc_tier}):
            output=self.invoke(self.seed)
        self.assertEqual(output["status"],
                         "FRESH_ONE_SPEC_PHYSICAL_SOURCE_OR_COVERAGE_PENDING")
        self.assertIn("V232_ORDINARY_SLOT_WITHOUT_SIMC_CANDIDATE",
                      output["reason"])
        self.assertFalse(output["environment_ready"])
        self.assertEqual(output["native_calls"],0)


if __name__=="__main__":
    unittest.main()
