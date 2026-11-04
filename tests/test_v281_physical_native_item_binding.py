"""P3-CQ: physical ItemID→sealed SimC option→original v216/v278 seam.

All sources and Native results are synthetic offline fixtures. No gear
recommendations, item approval, budget mutation, HTTP or actual SimC Native.
"""
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"runner"))
import v217_stage_execution_engine as stages
import v281_consumable_simc_relation as relation
import v216_environment_build_coordinator as build
from tests.test_v281_consumable_simc_relation import (
    SOURCE, TMP, FLASK, CSV, BUILD)

REV="a"*40

class ExactPhysicalNativeInput(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=pathlib.Path(tmp.name)
        spell=self.root/"effects.csv"
        spell.write_bytes(CSV)
        raw=dict(SOURCE)
        raw["source"]={**SOURCE["source"],"simc_revision":REV}
        derived=relation.correlate(
            raw,relation.scan_spell_effects(spell,{111,211,212}),
            TMP,build=BUILD,flask_dbc_rows=FLASK)
        self.output=self.root/"source"/"v284_simc_consumable_relations.json"
        self.output.parent.mkdir(parents=True)
        def execute():
            self.output.write_text(json.dumps(derived),encoding="utf8")
            (self.root/"source"/"v284_SpellEffect.csv").write_bytes(CSV)
        stage=stages.execute_stage(
            root=self.root,
            stage_id="fresh-consumable-simc-spell-effect-source-other",
            stage_version="v281-real-other-consumables-v2",
            inputs={"build":BUILD},
            outputs={"candidate":"source/v284_simc_consumable_relations.json",
                     "spell_effect":"source/v284_SpellEffect.csv"},
            execute=execute)
        self.source={"candidate_path":str(self.output),
                     "source_stage":{k:v for k,v in stage.items()
                                     if k!="result"}}
    def choose(self,kind,item_id,hand=None,source=None,build_arg=BUILD):
        return relation.resolve_native_input(
            stage_root=self.root,
            relation=self.source if source is None else source,
            build=build_arg,simc_revision=REV,
            kind=kind,item_id=item_id,hand=hand)
    def test_auto_measurement_plan_uses_original_exact_source_without_manual_ids(self):
        planned=relation.plan_physical_native_measurements(
            stage_root=self.root,relation=self.source,
            build=BUILD,simc_revision=REV)
        self.assertEqual(
            planned["status"],"MEASURABLE_PHYSICAL_F_O_CANDIDATES_UNADMITTED")
        self.assertEqual(planned["candidate_count"],3)
        self.assertEqual([x["physical_item_id"] for x in planned["flask"]],
                         [501])
        self.assertEqual({x["selected_hand"] for x in planned["oil"]},
                         {"main_hand","off_hand"})
        self.assertTrue(all(not x["user_selectable"] for x in
                            planned["flask"]+planned["oil"]))
        self.assertFalse(planned["quality_coverage_verified"])
        self.assertFalse(planned["weapon_applicability_verified"])
        self.assertFalse(planned["environment_ready"])
        self.assertEqual(planned["native_calls"],0)
        self.assertEqual(planned["network_calls"],0)
        again=relation.plan_physical_native_measurements(
            stage_root=self.root,relation=self.source,
            build=BUILD,simc_revision=REV)
        self.assertEqual(again,planned)
        self.assertEqual(
            relation.plan_physical_native_measurements(
                stage_root=self.root,relation={},
                build=BUILD,simc_revision=REV)["candidate_count"],0)
        self.output.write_text("{}",encoding="utf8")
        with self.assertRaisesRegex(
                relation.SimCRelationBlocked,
                "AUTO_MEASUREMENT_CANDIDATE_SCHEMA_INVALID"):
            relation.plan_physical_native_measurements(
                stage_root=self.root,relation=self.source,
                build=BUILD,simc_revision=REV)

    def test_flask_and_main_offhand_use_exact_physical_id(self):
        f=self.choose("flask",501)
        self.assertEqual(f["physical_item_id"],501)
        self.assertEqual(f["simc_input_token"],"test_flask_3")
        self.assertEqual(f["crafting_quality"],3)
        self.assertEqual(f["source_stage_receipt_sha256"],
                         self.source["source_stage"]["receipt_sha256"])
        o=self.choose("temporary_enchant",601,"main_hand")
        self.assertEqual(o["simc_input_token"],"main_hand:thalassian_phoenix_oil")
        self.assertEqual(o["simc_enchant_id"],8052)
        self.assertEqual(o["crafting_quality"],2)
        off=self.choose("temporary_enchant",601,"off_hand")
        self.assertEqual(off["simc_input_token"],
                         "main_hand:disabled/off_hand:thalassian_phoenix_oil")
        for item in (f,o,off):
            self.assertTrue(item["source_only"])
            self.assertFalse(item["same_effect_quality_group_verified"])
            self.assertFalse(item["weapon_and_hand_applicability_verified"])
            self.assertIsNone(item["F"])
            self.assertIsNone(item["O"])
            self.assertFalse(item["environment_ready"])
    def test_wrong_item_or_unlinked_temp_cannot_trigger_native(self):
        with self.assertRaisesRegex(relation.SimCRelationBlocked,
                                    "NOT_EXACTLY_ONE"):
            self.choose("flask",9999)
        with self.assertRaisesRegex(relation.SimCRelationBlocked,
                                    "RELATION_PENDING"):
            self.choose("temporary_enchant",602,"main_hand")
        with self.assertRaisesRegex(relation.SimCRelationBlocked,
                                    "HAND_SELECTION_INVALID"):
            self.choose("temporary_enchant",601)
        with self.assertRaisesRegex(relation.SimCRelationBlocked,
                                    "BUILD_OR_PROMOTION_DRIFT"):
            self.choose("flask",501,build_arg="12.2.0.99998")
    def test_tamper_receipt_or_candidate_blocks_not_rerun(self):
        self.output.write_text("modified",encoding="utf8")
        with self.assertRaisesRegex(relation.SimCRelationBlocked,
                                    "CANDIDATE_SIZE_DRIFT|CANDIDATE_SHA_DRIFT"):
            self.choose("flask",501)
    def test_real_missing_relation_is_pending(self):
        result=self.choose("flask",501,source={})
        self.assertIsNone(result)
    def test_normal_v216_build_uses_id_bound_tokens_not_user_text(self):
        source={"schema":"v216_fresh_source_stage_v1",
            "source_stage":{"status":"EXECUTED_AND_SEALED","reused":False},
            "environment_installed":False,"environment_ready":False,
            "native_calls":0,"G":None,"J":None,"F":None,"O":None,
            "B":None,"T":None,
            "expected_game_build":BUILD,
            "snapshot_receipt_path":str(self.root/"wago"/"receipt.json"),
            "fresh_consumable_simc_effect_relation":self.source}
        compiled={"status":"FRESH_V191_V211_V213_COMPILED_UNADMITTED",
                  "stage_root":str(self.root),"simc_revision":REV,
                  "source_catalog_path":str(self.root/"catalog.json"),
                  "missing":[]}
        requests=[
            {"source_profile_path":str(self.root/"profile.simc"),
             "kind":"flask","item_id":501},
            {"source_profile_path":str(self.root/"profile.simc"),
             "kind":"temporary_enchant","item_id":601,"hand":"main_hand"},
        ]
        parameters={
            "expected_game_build":BUILD,"representative_request":None,
            "g_probe_character":None,"simc_revision_hint":None,
            "effect_probe_requests":requests}
        called=[]
        def observed(**kwargs):
            called.append(kwargs)
            return {"kind":kwargs["kind"],"status":"SOURCE_ONLY",
                    "new_native_calls":0,
                    "F_candidate_unadmitted":11 if kwargs["kind"]=="flask" else None,
                    "O_candidate_unadmitted":{"crit_rating":5}
                      if kwargs["kind"]=="temporary_enchant" else None}
        with mock.patch.object(build,"collect_wago_new_season_source",
                               return_value=source),\
             mock.patch.object(build.source_wiring,"compile_collected",
                               return_value=compiled),\
             mock.patch.object(build,"preflight_new_season_source",
                               return_value={"preflight_sha256":"b"*64,
                                             "status":"FRESH_SOURCE_UNADMITTED"}),\
             mock.patch.object(build.zero_history_G_native,"collect",
                               return_value={"status":"PENDING",
                                             "new_native_calls":0}),\
             mock.patch.object(build.native_effect_pair,"measure",
                               side_effect=observed):
            result=build.build_environment(sessions_root=self.root,
                session_folder=None,user=None,binary=None,revision=None,
                static_cache=None,source_catalog_path=None,
                bootstrap_result=None,fresh_collection_inputs=parameters)
        self.assertEqual([x["token"] for x in called],
                         ["test_flask_3","main_hand:thalassian_phoenix_oil"])
        actual=result["native_effect_numeric_sources_unadmitted"]
        self.assertEqual(len(actual),2)
        self.assertEqual(actual[0]["physical_item_native_source_unadmitted"][
                         "physical_item_id"],501)
        self.assertFalse(actual[1]["physical_item_native_source_unadmitted"][
                         "weapon_and_hand_applicability_verified"])
        self.assertIsNone(result["F"])
        self.assertIsNone(result["O"])
        self.assertFalse(result["zero_history_build"]["environment_ready"])
    def test_missing_relation_in_normal_build_never_calls_native(self):
        source={"schema":"v216_fresh_source_stage_v1",
            "source_stage":{"status":"EXECUTED_AND_SEALED","reused":False},
            "environment_installed":False,"environment_ready":False,
            "native_calls":0,"G":None,"J":None,"F":None,"O":None,
            "B":None,"T":None,
            "expected_game_build":BUILD,
            "snapshot_receipt_path":str(self.root/"wago"/"receipt.json")}
        compiled={"status":"FRESH_V191_V211_V213_COMPILED_UNADMITTED",
                  "stage_root":str(self.root),"simc_revision":REV,
                  "source_catalog_path":str(self.root/"catalog.json"),
                  "missing":[]}
        params={
            "expected_game_build":BUILD,"representative_request":None,
            "g_probe_character":None,"simc_revision_hint":None,
            "effect_probe_requests":[{
               "source_profile_path":str(self.root/"profile.simc"),
               "kind":"flask","item_id":501}]}
        with mock.patch.object(build,"collect_wago_new_season_source",
                               return_value=source),\
             mock.patch.object(build.source_wiring,"compile_collected",
                               return_value=compiled),\
             mock.patch.object(build,"preflight_new_season_source",
                               return_value={"preflight_sha256":"b"*64,
                                             "status":"FRESH_SOURCE_UNADMITTED"}),\
             mock.patch.object(build.zero_history_G_native,"collect",
                               return_value={"status":"PENDING",
                                             "new_native_calls":0}),\
             mock.patch.object(build.native_effect_pair,"measure",
                               side_effect=AssertionError("NEW_NATIVE_FORBIDDEN")):
            result=build.build_environment(sessions_root=self.root,
                session_folder=None,user=None,binary=None,revision=None,
                static_cache=None,source_catalog_path=None,
                bootstrap_result=None,fresh_collection_inputs=params)
        self.assertEqual(result["native_calls"],0)
        self.assertIn("F_O_EXACT_ITEM_SIMC_SOURCE_PENDING",
                      result["zero_history_build"]["requires"])
        self.assertIsNone(result["F"])
        self.assertFalse(result["zero_history_build"]["environment_ready"])

if __name__=="__main__":
    unittest.main()
