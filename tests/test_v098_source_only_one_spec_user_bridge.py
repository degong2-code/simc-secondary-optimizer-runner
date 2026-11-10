"""Offline selected-spec source-only bridge, no Native/network/file download."""
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v098_target_user_scenario_bootstrap as user_product
import v216_environment_build_coordinator as original


class SelectedOneSpecNativeZero(unittest.TestCase):
    def example(self,home):
        root=pathlib.Path(home)/"stage"
        root.mkdir()
        gear=root/"source_gear.json"
        tier=root/"source_tier.json"
        seed=root/"source_seed"
        seed.mkdir()
        (seed/"item_data.inc").write_text("pinned fake input")
        gear.write_text("{}")
        tier.write_text("{}")
        selected=root/"selected_candidate.json"
        row={"game_build":"12.1.5.70783",
             "simc_revision":"c20e2ad52e4c33711f74272309a5748125175fe8",
             "target_ilevel":334,
             "character":{"class":"mage","spec":"frost"},
             "selected_G_slot_ids":{"head":250001}}
        selected.write_text(json.dumps(row))
        source={"source_compilation":{"stage_root":str(root)},
                "fresh_ordinary_gear":{"candidate_path":str(gear)},
                "fresh_tier_simc_candidate_bridge":{
                    "candidate_path":str(tier)},
                "fresh_lazy_full_pinned_simc_item_source":{
                    "source_dir":str(seed)}}
        calc={key:row[key] for key in
              ("game_build","simc_revision","target_ilevel")}
        user={"character":{"class":"mage","spec":"frost"}}
        return source,calc,user,selected

    def test_valid_new_mage_source_is_reused_without_native(self):
        with tempfile.TemporaryDirectory() as td:
            source,calc,user,selected=self.example(td)
            with mock.patch.object(
                    original,"_one_spec_ordinary_simc_stage",
                    return_value={
                        "status":"FRESH_ONE_SPEC_SIMC_G_SOURCE_CANDIDATE_PENDING_NATIVE",
                        "candidate_path":str(selected),"native_calls":0}) as stage:
                got=user_product._select_v216_source_only_user_spec(
                    None,user=user,environment_result=source,calculation=calc)
            self.assertEqual(got["character"]["spec"],"frost")
            stage.assert_called_once()
            args=stage.call_args.kwargs
            self.assertEqual(args["request"],{
                "class":"mage","spec":"frost","target_ilevel":334})
            self.assertEqual(args["build"],"12.1.5.70783")

    def test_missing_or_offscope_pinned_source_blocks_before_native(self):
        with tempfile.TemporaryDirectory() as td:
            source,calc,user,selected=self.example(td)
            source["fresh_lazy_full_pinned_simc_item_source"]={}
            with mock.patch.object(original,
                    "_one_spec_ordinary_simc_stage") as stage:
                with self.assertRaisesRegex(user_product.UserScenarioBlocked,
                                            "PINNED_SOURCE_NOT_RETAINED"):
                    user_product._select_v216_source_only_user_spec(
                        None,user=user,environment_result=source,
                        calculation=calc)
                stage.assert_not_called()

    def test_candidate_mismatch_does_not_claim_another_spec_G(self):
        with tempfile.TemporaryDirectory() as td:
            source,calc,user,selected=self.example(td)
            doc=json.loads(selected.read_text())
            doc["character"]={"class":"paladin","spec":"retribution"}
            selected.write_text(json.dumps(doc))
            with mock.patch.object(
                    original,"_one_spec_ordinary_simc_stage",
                    return_value={
                        "status":"FRESH_ONE_SPEC_SIMC_G_SOURCE_CANDIDATE_PENDING_NATIVE",
                        "candidate_path":str(selected),"native_calls":0}):
                with self.assertRaisesRegex(user_product.UserScenarioBlocked,
                                            "NEW_SOURCE_IDENTITY_DRIFT"):
                    user_product._select_v216_source_only_user_spec(
                        None,user=user,environment_result=source,
                        calculation=calc)


if __name__=="__main__":
    unittest.main()
