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
                     "credentials":{},
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
