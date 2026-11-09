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
        (self.root/"source"/"probe.simc").write_text(
            "paladin=simc_source_g_probe\nrace=dwarf\nspec=retribution\n"
            "main_hand=simc_source_weapon,id=9010,ilevel=334,source=local\n",
            encoding="utf8")
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
        self.assertEqual(o["simc_input_token"],"main_hand:thalassian_phoenix_oil_2")
        self.assertEqual(o["simc_enchant_id"],8052)
        self.assertEqual(o["crafting_quality"],2)
        off=self.choose("temporary_enchant",601,"off_hand")
        self.assertEqual(off["simc_input_token"],
                         "main_hand:disabled/off_hand:thalassian_phoenix_oil_2")
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
                         ["test_flask_3","main_hand:thalassian_phoenix_oil_2"])
        actual=result["native_effect_numeric_sources_unadmitted"]
        self.assertEqual(len(actual),2)
        self.assertEqual(actual[0]["physical_item_native_source_unadmitted"][
                         "physical_item_id"],501)
        self.assertFalse(actual[1]["physical_item_native_source_unadmitted"][
                         "weapon_and_hand_applicability_verified"])
        auto=result["source_compilation"][
            "automatic_F_O_measurement_candidates_unadmitted"]
        self.assertEqual(auto["candidate_count"],3)
        self.assertEqual([x["physical_item_id"] for x in auto["flask"]],[501])
        self.assertFalse(auto["environment_ready"])
        self.assertFalse(auto["user_selectable"])
        self.assertIsNone(result["F"])
        self.assertIsNone(result["O"])
        self.assertFalse(result["zero_history_build"]["environment_ready"])
    def test_normal_v216_auto_F_native_opt_in_uses_exact_v281_id_only(self):
        """No user-supplied F ID; same v281 source + original v278 worker."""
        src={"schema":"v216_fresh_source_stage_v1",
            "source_stage":{"status":"EXECUTED_AND_SEALED","reused":False},
            "environment_installed":False,"environment_ready":False,
            "native_calls":0,"G":None,"J":None,"F":None,"O":None,
            "B":None,"T":None,
            "expected_game_build":BUILD,
            "snapshot_receipt_path":str(self.root/"wago"/"receipt.json"),
            "fresh_consumable_simc_effect_relation":self.source,
            "fresh_one_spec_physical_G_probe":{
                "profile_path":str(self.root/"source"/"probe.simc"),
                "source_stage":{"status":"EXECUTED_AND_SEALED"}}}
        compiled={"status":"FRESH_V191_V211_V213_COMPILED_UNADMITTED",
                  "stage_root":str(self.root),"simc_revision":REV,
                  "source_catalog_path":str(self.root/"catalog.json"),
                  "missing":[]}
        p={"expected_game_build":BUILD,
           "representative_request":{"class":"paladin","spec":"retribution",
                                     "target_ilevel":334},
           "g_probe_character":{"race":"dwarf"},
           "simc_revision_hint":None,"auto_native_F_requested":True}
        measured=[]
        def controlled_measure(**kwargs):
            measured.append(kwargs)
            return {"kind":"flask",
                    "status":"SIMC_CONSUMABLE_SOURCE_OR_BINARY_PENDING",
                    "token":kwargs["token"],"new_native_calls":0,
                    "F_candidate_unadmitted":None}
        with mock.patch.object(build,"collect_wago_new_season_source",
                               return_value=src) as collect,\
             mock.patch.object(build.source_wiring,"compile_collected",
                               return_value=compiled),\
             mock.patch.object(build,"preflight_new_season_source",
                               return_value={"preflight_sha256":"b"*64,
                                             "status":"FRESH_SOURCE_UNADMITTED"}),\
             mock.patch.object(build.zero_history_G_native,"collect",
                               return_value={"status":"PENDING",
                                             "new_native_calls":0}),\
             mock.patch.object(build.native_effect_pair,"measure",
                               side_effect=controlled_measure):
            result=build.build_environment(
                sessions_root=self.root,session_folder=None,user=None,
                binary=self.root/"simc_mock",revision=None,
                static_cache=None,source_catalog_path=None,
                bootstrap_result=None,fresh_collection_inputs=p)
        self.assertEqual(len(measured),1)
        self.assertEqual(measured[0]["token"],"test_flask_3")
        self.assertEqual(measured[0]["kind"],"flask")
        self.assertNotIn("auto_native_F_requested",collect.call_args.kwargs)
        report=result["source_compilation"][
            "automatic_F_native_measurements_unadmitted"]
        self.assertEqual(report["total_source_candidates"],1)
        self.assertEqual(report["attempted"],1)
        self.assertEqual(report["new_native_calls"],0)
        self.assertFalse(report["F_approved"])
        self.assertFalse(report["environment_ready"])
        self.assertIsNone(result["F"])
        self.assertFalse(result["zero_history_build"]["environment_ready"])


    def test_p3_gn_multi_flask_auto_default_measures_one_exact_item(self):
        # Normal zero-history engine, not a standalone item scorer:
        # two distinct high-quality types are present in v281, but the
        # automatic default measures only the deterministic first family.
        src={"schema":"v216_fresh_source_stage_v1",
             "source_stage":{"status":"EXECUTED_AND_SEALED","reused":False},
             "environment_installed":False,"environment_ready":False,
             "native_calls":0,"G":None,"J":None,"F":None,"O":None,
             "B":None,"T":None,"expected_game_build":BUILD,
             "snapshot_receipt_path":str(self.root/"wago"/"receipt.json"),
             "fresh_consumable_simc_effect_relation":self.source,
             "fresh_one_spec_physical_G_probe":{
                 "profile_path":str(self.root/"source"/"probe.simc"),
                 "source_stage":{"status":"EXECUTED_AND_SEALED"}}}
        compiled={"status":"FRESH_V191_V211_V213_COMPILED_UNADMITTED",
                  "stage_root":str(self.root),"simc_revision":REV,
                  "source_catalog_path":str(self.root/"catalog.json"),
                  "missing":[]}
        base=relation.plan_physical_native_measurements(
            stage_root=self.root,relation=self.source,
            build=BUILD,simc_revision=REV)
        rows=base["flask"]+[
            {"physical_item_id":502,"simc_input_token":"unrelated_flask_3",
             "crafting_quality":3}]
        plan={**base,"flask":rows,"candidate_count":len(rows)}
        requested={"expected_game_build":BUILD,
                   "representative_request":{"class":"paladin",
                       "spec":"retribution","target_ilevel":334},
                   "g_probe_character":{"race":"dwarf"},
                   "simc_revision_hint":None,
                   "auto_native_F_requested":True,
                   "auto_native_G_requested":False,
                   "auto_select_observed_F_no_oil":True}
        called=[]
        def pair(**kwargs):
            called.append(kwargs["token"])
            return {"kind":"flask","token":kwargs["token"],
                    "status":"SIMC_CONSUMABLE_SOURCE_OR_BINARY_PENDING",
                    "new_native_calls":0,"F_candidate_unadmitted":None}
        with mock.patch.object(build,"collect_wago_new_season_source",
                               return_value=src), \
             mock.patch.object(build.source_wiring,"compile_collected",
                               return_value=compiled), \
             mock.patch.object(build,"preflight_new_season_source",
                               return_value={"preflight_sha256":"b"*64,
                                             "status":"FRESH_SOURCE_UNADMITTED"}), \
             mock.patch.object(build.zero_history_G_native,"collect",
                               return_value={"status":"PENDING",
                                             "new_native_calls":0}), \
             mock.patch.object(relation,"plan_physical_native_measurements",
                               return_value=plan), \
             mock.patch.object(build.native_effect_pair,"measure",
                               side_effect=pair):
            result=build.build_environment(
                sessions_root=self.root,session_folder=None,user=None,
                binary=self.root/"fake_simc",revision=None,static_cache=None,
                source_catalog_path=None,bootstrap_result=None,
                fresh_collection_inputs=requested)
        self.assertEqual(called,["test_flask_3"])
        comp=result["source_compilation"]
        default=comp["automatic_default_F_source_selection_unadmitted"]
        self.assertEqual(default["status"],
                         "AUTO_DEFAULT_F_SOURCE_ITEM_SELECTED_UNADMITTED")
        self.assertEqual(default["selected_physical_items_unadmitted"],
                         {"flask_item_id":501,"oil_item_ids_by_hand":{}})
        self.assertEqual(comp["automatic_F_native_measurements_unadmitted"]
                         ["attempted"],1)
        self.assertIsNone(result["F"])
        self.assertFalse(result["environment_ready"])
        self.assertFalse(default["environment_ready"])

    def test_auto_F_measurement_uses_sealed_precombat_without_editing_v233(self):
        original=self.root/"source"/"probe.simc"
        raw=original.read_bytes()
        first=build._sealed_v233_precombat_F_O_profile(
            stage_root=self.root,source_profile_path=original)
        second=build._sealed_v233_precombat_F_O_profile(
            stage_root=self.root,source_profile_path=original)
        self.assertEqual(first,second)
        self.assertEqual(raw,original.read_bytes())
        derived=pathlib.Path(first).read_text("utf8")
        self.assertEqual(derived.count("actions.precombat=flask"),1)
        self.assertEqual(derived.count("actions.precombat+=/snapshot_stats"),1)
        from runner import v269_simc_chmv_effect_snapshot as snapshot
        f=snapshot.prepare(profile=derived,kind="flask",token="test_flask_3")
        self.assertTrue(f["other_consumables_explicitly_disabled"])
        # v217 detects source alteration on the same content-addressed path.
        pathlib.Path(first).write_text(derived+"actions=wait\n",encoding="utf8")
        with self.assertRaises(build.stage_engine.StageExecutionBlocked):
            build._sealed_v233_precombat_F_O_profile(
                stage_root=self.root,source_profile_path=original)
        self.assertEqual(raw,original.read_bytes())

    def test_auto_F_O_bounded_native_calls_are_counted_once(self):
        """Existing exact v281 F/O worklist binds both hands, 8-run shared cap."""
        src={"schema":"v216_fresh_source_stage_v1",
             "source_stage":{"status":"EXECUTED_AND_SEALED","reused":False},
             "environment_installed":False,"environment_ready":False,
             "native_calls":0,"G":None,"J":None,"F":None,"O":None,
             "B":None,"T":None,"expected_game_build":BUILD,
             "snapshot_receipt_path":str(self.root/"wago"/"receipt.json"),
             "fresh_consumable_simc_effect_relation":self.source,
             "fresh_one_spec_physical_G_probe":{
                 "profile_path":str(self.root/"source"/"probe.simc"),
                 "source_stage":{"status":"EXECUTED_AND_SEALED"}}}
        compiled={"status":"FRESH_V191_V211_V213_COMPILED_UNADMITTED",
                  "stage_root":str(self.root),"simc_revision":REV,
                  "source_catalog_path":str(self.root/"catalog.json"),
                  "missing":[]}
        params={"expected_game_build":BUILD,
                "representative_request":{"class":"paladin","spec":"retribution",
                                          "target_ilevel":334},
                "g_probe_character":{"race":"dwarf"},"simc_revision_hint":None,
                "auto_native_F_requested":True,"auto_native_O_requested":True,
                "auto_native_G_requested":False}
        called=[]
        def measure(**kwargs):
            called.append((kwargs["kind"],kwargs["token"]))
            return {"kind":kwargs["kind"],"token":kwargs["token"],
                    "status":"SIMC_CONSUMABLE_SOURCE_OR_BINARY_PENDING",
                    "new_native_calls":2,"F_candidate_unadmitted":None,
                    "O_candidate_unadmitted":None}
        with mock.patch.object(build,"collect_wago_new_season_source",
                               return_value=src) as collector,\
             mock.patch.object(build.source_wiring,"compile_collected",
                               return_value=compiled),\
             mock.patch.object(build,"preflight_new_season_source",
                               return_value={"preflight_sha256":"b"*64,
                                             "status":"FRESH_SOURCE_UNADMITTED"}),\
             mock.patch.object(build.zero_history_G_native,"collect",
                               return_value={"status":"PENDING",
                                             "new_native_calls":0}) as g_native,\
             mock.patch.object(build.native_effect_pair,"measure",
                               side_effect=measure):
            result=build.build_environment(
                sessions_root=self.root,session_folder=None,user=None,
                binary=self.root/"simc_mock",revision=None,
                static_cache=None,source_catalog_path=None,
                bootstrap_result=None,fresh_collection_inputs=params)
        self.assertEqual(len(called),3)
        # F/O use the same executable while G Native is truly disabled.
        self.assertIsNone(g_native.call_args.kwargs["binary"])
        self.assertEqual(called[0],("flask","test_flask_3"))
        self.assertEqual({token for kind,token in called
                          if kind=="temporary_enchant"},
                         {"main_hand:thalassian_phoenix_oil_2",
                          "main_hand:disabled/off_hand:thalassian_phoenix_oil_2"})
        self.assertNotIn("auto_native_O_requested",collector.call_args.kwargs)
        self.assertEqual(result["native_calls"],6)
        self.assertEqual(result["zero_history_build"]["new_native_calls"],6)
        reports=result["source_compilation"]
        self.assertEqual(reports["automatic_F_native_measurements_unadmitted"]
                         ["new_native_calls"],2)
        self.assertEqual(reports["automatic_O_native_measurements_unadmitted"]
                         ["new_native_calls"],4)
        self.assertFalse(reports["automatic_O_native_measurements_unadmitted"]
                         ["O_approved"])
        self.assertFalse(result["zero_history_build"]["environment_ready"])
        self.assertIsNone(result["O"])

    def test_G_native_explicit_without_binary_blocks_before_source(self):
        inputs={"expected_game_build":BUILD,"representative_request":None,
                "g_probe_character":None,"simc_revision_hint":None,
                "auto_native_G_requested":True}
        with mock.patch.object(build,"collect_wago_new_season_source",
                               side_effect=AssertionError("NO_SOURCE_COLLECTION")):
            with self.assertRaisesRegex(
                    build.EnvironmentBuildBlocked,
                    "AUTO_G_NATIVE_EXPLICIT_BINARY_REQUIRED"):
                build.build_environment(
                    sessions_root=self.root,session_folder=None,user=None,
                    binary=None,revision=None,static_cache=None,
                    source_catalog_path=None,bootstrap_result=None,
                    fresh_collection_inputs=inputs)

    def test_auto_O_native_without_binary_blocks_before_collection(self):
        params={"expected_game_build":BUILD,"representative_request":None,
                "g_probe_character":None,"simc_revision_hint":None,
                "auto_native_O_requested":True}
        with mock.patch.object(build,"collect_wago_new_season_source",
                               side_effect=AssertionError("NO_SOURCE_FETCH")):
            with self.assertRaisesRegex(
                    build.EnvironmentBuildBlocked,
                    "AUTO_O_NATIVE_EXPLICIT_BINARY_REQUIRED"):
                build.build_environment(
                    sessions_root=self.root,session_folder=None,user=None,
                    binary=None,revision=None,static_cache=None,
                    source_catalog_path=None,bootstrap_result=None,
                    fresh_collection_inputs=params)

    def test_auto_F_native_without_binary_blocks_before_source_collection(self):
        p={"expected_game_build":BUILD,"representative_request":None,
           "g_probe_character":None,"simc_revision_hint":None,
           "auto_native_F_requested":True}
        with mock.patch.object(build,"collect_wago_new_season_source",
                               side_effect=AssertionError("NO_SOURCE_FETCH")):
            with self.assertRaisesRegex(
                    build.EnvironmentBuildBlocked,
                    "AUTO_F_NATIVE_EXPLICIT_BINARY_REQUIRED"):
                build.build_environment(
                    sessions_root=self.root,session_folder=None,user=None,
                    binary=None,revision=None,static_cache=None,
                    source_catalog_path=None,bootstrap_result=None,
                    fresh_collection_inputs=p)

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
