"""P3-CB zero-history acceptance through the ONE v216 Build entry.

The Wago fetch is a deterministic fake transport; no real HTTP, SimC, cache
or preexisting season file is used. Real collection uses the same v161/v217.
"""
from __future__ import annotations

import io
import pathlib
import sys
import tempfile
import unittest
from unittest import mock
from urllib.parse import parse_qs, urlsplit

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v216_environment_build_coordinator as engine


class ZeroHistoryNormalBuild(unittest.TestCase):
    def test_empty_workspace_build_collects_once_then_reuses_same_source(self):
        class Response(io.BytesIO):
            status=200
            def __enter__(self):return self
            def __exit__(self,*exc):self.close()
        calls=[]
        build="12.2.0.99999"
        def fake_fetch(req,timeout):
            url=urlsplit(req.full_url)
            assert url.hostname=="wago.tools"
            assert parse_qs(url.query)["build"]==[build]
            table=url.path.split("/")[-2]
            assert table in engine.wago_snapshot.TABLES
            calls.append(table)
            return Response(("ID,Name\n1,"+table+"\n").encode("utf8"))
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)/"totally-new-install"
            self.assertFalse(root.exists())
            options={"expected_game_build":build,
                     "representative_request":None,
                     "g_probe_character":None,
                     "simc_revision_hint":None,
                     "credentials":{name:"" for name in
                                    engine.discovery_stage.FIELDS},
                     "fetch":fake_fetch}
            kwargs={"sessions_root":root,"session_folder":None,
                    "user":None,"binary":None,"revision":None,
                    "static_cache":None,"source_catalog_path":None,
                    "bootstrap_result":None,
                    "fresh_collection_inputs":options}
            one=engine.build_environment(**kwargs)
            two=engine.build_environment(**kwargs)
            self.assertEqual(len(calls),len(engine.wago_snapshot.TABLES))
            self.assertEqual(len(set(calls)),len(calls))
            self.assertEqual(one["source_stage"]["status"],"EXECUTED_AND_SEALED")
            self.assertEqual(two["source_stage"]["status"],"REUSED_VERIFIED")
            self.assertEqual(one["network_calls_by_stage"],
                             len(engine.wago_snapshot.TABLES))
            self.assertEqual(two["network_calls_by_stage"],0)
            for result in (one,two):
                self.assertTrue(result["normal_build_entry"])
                report=result["zero_history_build"]
                self.assertEqual(report["entrypoint"],"v216.build_environment")
                self.assertEqual(report["stage_engine"],"v217.execute_stage")
                self.assertFalse(report["history_dependency_required"])
                self.assertTrue(report["resume_from_sealed_source_stage"])
                self.assertFalse(report["environment_ready"])
                self.assertFalse(report["environment_installed"])
                self.assertFalse(report["user_session_created"])
                self.assertTrue(report["no_historical_budget_defaults"])
                self.assertIn("G_NATIVE_RATING_OBSERVATION_PENDING",
                              report["requires"])
                self.assertIn("HIGHEST_QUALITY_GEM_J_SOURCE_PENDING",
                              report["requires"])
                self.assertIn("HIGHEST_QUALITY_FLASK_F_SOURCE_PENDING",
                              report["requires"])
                self.assertTrue(all(report[k] is None for k in
                                    ("G","J","F","O","B","T")))
                self.assertEqual(result["native_calls"],0)
            self.assertFalse(one["zero_history_build"]["same_build_cache_reuse"])
            self.assertTrue(two["zero_history_build"]["same_build_cache_reuse"])
            self.assertEqual([x.name for x in root.iterdir()],
                             ["_fresh_season_sources"])
            self.assertFalse((root/"data").exists())
            self.assertFalse((root/"manifest.json").exists())
            self.assertEqual(one["snapshot_receipt_path"],
                             two["snapshot_receipt_path"])

    def test_zero_history_refuses_prior_scenario_artifact_and_budget_shortcuts(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)/"unused-root"
            base={"sessions_root":root,"session_folder":None,
                  "user":None,"binary":None,"revision":None,
                  "static_cache":None,"source_catalog_path":None,
                  "bootstrap_result":None,
                  "fresh_collection_inputs":{
                    "expected_game_build":"12.2.0.99999",
                    "representative_request":None,
                    "g_probe_character":None,"simc_revision_hint":None}}
            with mock.patch.object(engine,"collect_wago_new_season_source",
                                   side_effect=AssertionError("FETCH_FORBIDDEN")):
                for override in (
                    {"source_catalog_path":root/"prior.json"},
                    {"fresh_gjfo_evidence":{"components":{}}},
                    {"bootstrap_result":{"schema":"historical"}},
                    {"session_folder":root/"abcd"},
                    {"fresh_source_stage_inputs":{"legacy":"source"}},
                ):
                    with self.subTest(override=override):
                        with self.assertRaisesRegex(
                                engine.EnvironmentBuildBlocked,
                                "ZERO_HISTORY_MUST_NOT_USE_INSTALLED_SESSION_OR_BUDGET"):
                            engine.build_environment(**{**base,**override})
            self.assertFalse(root.exists())

    def test_sealed_content_join_is_not_whole_season_item_gate(self):
        source={"schema":"v216_fresh_source_stage_v1",
                "source_stage":{"status":"REUSED_VERIFIED","reused":True},
                "environment_installed":False,"environment_ready":False,
                "native_calls":0,"G":None,"J":None,"F":None,"O":None,
                "B":None,"T":None,
                "season_join":{
                    "status":"DB2_WCL_CANDIDATES_JOINED_SEASON_CONDITIONS_PENDING",
                    "candidate_path":"source/v163_unapproved_candidates.json",
                    "season_membership_verified":False,
                    "stage":{"status":"REUSED_VERIFIED"}}}
        report=engine._zero_history_source_progress(source)
        self.assertTrue(report["season_content_candidate_join_sealed"])
        self.assertFalse(report["season_item_membership_completely_verified"])
        self.assertTrue(report[
            "unresolved_unselected_item_conditions_not_base_gate"])
        self.assertNotIn("SOURCE_SEASON_JOIN_PENDING",report["requires"])
        self.assertIn("REPRESENTATIVE_TIER_SOURCE_PENDING",report["requires"])
        self.assertIn("G_NATIVE_RATING_OBSERVATION_PENDING",report["requires"])
        self.assertIn("HIGHEST_QUALITY_GEM_J_SOURCE_PENDING",report["requires"])
        self.assertIn("HIGHEST_QUALITY_FLASK_F_SOURCE_PENDING",report["requires"])
        self.assertFalse(report["environment_ready"])
        self.assertTrue(all(report[k] is None for k in
                            ("G","J","F","O","B","T")))
        for altered in (
            {"stage":{"status":"RUNNING"}},
            {"candidate_path":None},
            {"status":"LIVE_SEASON_SCOPE_AMBIGUOUS_PENDING"},
            {"season_membership_verified":True},
        ):
            with self.subTest(altered=altered):
                wrong={**source,"season_join":{
                    **source["season_join"],**altered}}
                result=engine._zero_history_source_progress(wrong)
                self.assertFalse(result[
                    "season_content_candidate_join_sealed"])
                self.assertIn("SOURCE_SEASON_JOIN_PENDING",
                              result["requires"])
                self.assertFalse(result["environment_ready"])

    def test_required_information_scope_tracks_actual_selected_items(self):
        scope=engine._fresh_required_information_scope
        base={"representative_request":{"target_ilevel":334}}
        unselected=scope(**base)
        self.assertEqual(unselected["oil_source_mode"],
                         "UNSELECTED_PENDING_CHOICE")
        self.assertIsNone(unselected["selected_physical_sources"]["flask_item_id"])
        self.assertFalse(unselected["environment_ready"])
        self.assertTrue(unselected["season_wide_item_membership_not_required"])
        self.assertTrue(unselected[
            "nonselected_WSE_and_unrelated_loot_may_remain_unknown"])
        no_oil=scope(**base,selected_budget_items={
            "flask_item_id":500,"oil_item_ids_by_hand":{}})
        self.assertEqual(no_oil["oil_source_mode"],"EXPLICIT_NO_OIL_PROOF")
        self.assertTrue(no_oil["unselected_oil_item_proofs_not_needed"])
        self.assertFalse(no_oil["selected_oil_item_and_hand_proof_needed"])
        for hands in ({"main_hand":901},
                      {"main_hand":901,"off_hand":902}):
            with self.subTest(hands=hands):
                selected=scope(**base,selected_budget_items={
                    "flask_item_id":500,"oil_item_ids_by_hand":hands},
                    selected_gem_roles={"ordinary_gem_ids":[701,702],
                                        "special_gem_id":703})
                self.assertEqual(selected["selected_physical_sources"][
                    "oil_item_ids_by_hand"],hands)
                self.assertTrue(selected[
                    "selected_oil_item_and_hand_proof_needed"])
                self.assertEqual(selected["selected_physical_sources"][
                    "ordinary_gem_ids"],[701,702])
                self.assertEqual(selected["selected_physical_sources"][
                    "special_gem_id"],703)
                self.assertFalse(selected["environment_ready"])

    def test_selected_physical_data_needs_real_target_before_collect(self):
        with tempfile.TemporaryDirectory() as td:
            kwargs={"sessions_root":pathlib.Path(td)/"new",
                    "session_folder":None,"user":None,"binary":None,
                    "revision":None,"static_cache":None,
                    "source_catalog_path":None,"bootstrap_result":None}
            req={"expected_game_build":"12.2.0.99999",
                 "representative_request":None,
                 "g_probe_character":None,"simc_revision_hint":None}
            for selected in (
                {"selected_budget_items":{
                    "flask_item_id":501,"oil_item_ids_by_hand":{}}},
                {"source_selected_gem_roles":{
                    "ordinary_gem_ids":[501],"special_gem_id":None}}):
                with self.subTest(selected=selected),mock.patch.object(
                        engine,"collect_wago_new_season_source",
                        side_effect=AssertionError("UNWANTED_SOURCE_FETCH")):
                    with self.assertRaisesRegex(
                            engine.EnvironmentBuildBlocked,
                            "V216_REQUIRED_SELECTION_TARGET_REPRESENTATIVE_REQUIRED"):
                        engine.build_environment(**kwargs,
                            fresh_collection_inputs={**req,**selected})

    def test_scope_changes_do_not_refetch_one_same_build_source(self):
        class Response(io.BytesIO):
            status=200
            def __enter__(self): return self
            def __exit__(self,*exc): self.close()
        builds=[];build="12.2.0.99999"
        def fake_fetch(req,timeout):
            url=urlsplit(req.full_url)
            self.assertEqual(url.hostname,"wago.tools")
            self.assertEqual(parse_qs(url.query)["build"],[build])
            table=url.path.split("/")[-2]
            self.assertIn(table,engine.wago_snapshot.TABLES)
            builds.append(table)
            return Response(("ID,Name\\n1,"+table+"\\n").encode("utf8"))
        with tempfile.TemporaryDirectory() as td:
            kwargs={"sessions_root":pathlib.Path(td)/"new",
                    "session_folder":None,"user":None,"binary":None,
                    "revision":None,"static_cache":None,
                    "source_catalog_path":None,"bootstrap_result":None}
            inputs={"expected_game_build":build,
                    "representative_request":{
                        "class":"paladin","spec":"retribution",
                        "target_ilevel":334},
                    "g_probe_character":None,"simc_revision_hint":None,
                    "credentials":{name:"" for name in
                                   engine.discovery_stage.FIELDS},
                    "fetch":fake_fetch}
            for mode,selection in (
                    ("UNSELECTED_PENDING_CHOICE",None),
                    ("EXPLICIT_NO_OIL_PROOF",{
                        "flask_item_id":501,"oil_item_ids_by_hand":{}}),
                    ("SELECTED_OIL_ITEM_AND_HAND_EVIDENCE",{
                        "flask_item_id":501,"oil_item_ids_by_hand":{
                            "main_hand":900}})):
                with self.subTest(mode=mode):
                    params=dict(inputs)
                    if selection is not None:
                        params["selected_budget_items"]=selection
                    out=engine.build_environment(
                        **kwargs,fresh_collection_inputs=params)
                    report=out["zero_history_build"]
                    self.assertEqual(report["required_information_scope"][
                        "oil_source_mode"],mode)
                    self.assertFalse(report["environment_ready"])
                    self.assertEqual(
                        "WEAPON_OIL_O_EXACT_APPLICATION_AND_RATING_PENDING"
                        in report["requires"],
                        mode!="EXPLICIT_NO_OIL_PROOF")
            self.assertEqual(len(builds),len(engine.wago_snapshot.TABLES))
            self.assertEqual(len(set(builds)),len(builds))

    def test_premature_ready_or_unsealed_stage_never_advances(self):
        source={"schema":"v216_fresh_source_stage_v1",
                "source_stage":{"status":"EXECUTED_AND_SEALED","reused":False},
                "environment_installed":False,"environment_ready":False,
                "native_calls":0,"G":None,"J":None,"F":None,"O":None,
                "B":None,"T":None}
        good=engine._zero_history_source_progress(source)
        self.assertFalse(good["environment_ready"])
        for change,marker in (
            ({"J":138},"PREMATURE_BUDGET_OR_READY"),
            ({"environment_ready":True},"PREMATURE_BUDGET_OR_READY"),
            ({"native_calls":1},"PREMATURE_BUDGET_OR_READY"),
            ({"source_stage":{"status":"RUNNING"}},"SOURCE_STAGE_NOT_SEALED"),
        ):
            with self.subTest(change=change):
                with self.assertRaisesRegex(engine.EnvironmentBuildBlocked,
                                            marker):
                    engine._zero_history_source_progress({**source,**change})


if __name__=="__main__":
    unittest.main()
