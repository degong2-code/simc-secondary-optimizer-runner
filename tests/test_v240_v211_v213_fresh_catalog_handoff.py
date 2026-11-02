"""Fresh v211 → existing v213 source-to-catalog handoff: variable count.

Synthetic sources only. Same normal compiler functions, NO new parallel
Environment Builder, NO user UI admission, Native 0, network 0. This does
NOT certify current-season source retrieval, actual G/J/F/O or v196 readiness.
"""
from __future__ import annotations
import copy
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

from runner import v211_enchant_source_effect_classification as classifier
from runner import v213_source_to_catalog as join
from tests.test_v213_source_to_catalog import SourceToCatalogTests
from tests.test_v239_v211_fresh_season_dynamic_classifier import (
    BUILD,REV,fixture_source,put_sources)


class SameFreshCatalogChain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use existing fixture for all non-enchant v191 structural fields.
        # The new-season enchant identities and bytes are generated in-test.
        SourceToCatalogTests.setUpClass()

    def inputs(self,folder):
        old=SourceToCatalogTests()
        season,_old_classification=old.build_inputs()
        real_source,generated=fixture_source()
        manifest=put_sources(folder,generated)
        season["game_build"]=BUILD
        season["simc_revision"]=REV
        season["source_artifacts"]["v189"]["simc_commit"]=REV
        season["source_artifacts"]["v190"]["simc_revision"]=REV
        season["source_artifacts"]["v190"]["game_build"]=BUILD
        for record in season["simc_generated_sources"].values():
            record["source_build"]=BUILD
        season["enchants"].pop("current_season_midnight")
        season["enchants"]["current_season"]=real_source["enchants"]["current_season"]
        current=classifier.compile_fresh_season(season,folder,manifest)
        return season,current

    def test_join_variable_two_items_and_no_old_7967_8025_or_e(self):
        with tempfile.TemporaryDirectory() as d:
            season,classified=self.inputs(pathlib.Path(d))
            artifact=join.compile_catalog(
                season,"a"*64,classified,"b"*64)
            again=join.compile_catalog(
                season,"a"*64,classified,"b"*64)
        self.assertTrue(join.verify_catalog(artifact))
        self.assertEqual(artifact["manifest_sha256"],again["manifest_sha256"])
        self.assertEqual(artifact["catalog"]["enchants"]["count"],2)
        self.assertEqual(artifact["catalog_summary"]["enchants"][
                         "existing_user_approval_id"],None)
        self.assertEqual(artifact["catalog"]["enchants"]["selection_policy"][
                         "only_existing_native_scoped_choice"],None)
        self.assertEqual(artifact["catalog"]["enchants"]["selection_policy"][
                         "developer_only"],[])
        self.assertFalse(artifact["automatic_ui_promotion"])
        self.assertEqual(artifact["native_calls"],0)
        self.assertEqual(artifact["network_calls"],0)
        self.assertTrue(all(not x["ui_selectable"] for x
            in artifact["catalog"]["enchants"]["items"]))
        self.assertTrue(all(not x["approved"] for x
            in artifact["v196_enchant_source"]["rows"]))

    def test_same_v196_ui_bridge_shows_unapproved_fresh_catalog_without_old_data(self):
        import v196_current_season_user_catalog as ui
        with tempfile.TemporaryDirectory() as d:
            folder=pathlib.Path(d)
            season,classified=self.inputs(folder)
            artifact=join.compile_catalog(season,"a"*64,classified,"b"*64)
            p=folder/"fresh_v213.json"
            p.write_text(json.dumps(artifact,ensure_ascii=False),encoding="utf8")
            with patch.object(ui.v188,"labels",side_effect=AssertionError(
                    "OLD_INSTALLED_SEASON_LABELS_FORBIDDEN")), \\
                 patch.object(ui.observed_enchant,"read",side_effect=AssertionError(
                    "OLD_NATIVE_E_FORBIDDEN")):
                result=ui.public_options(p)
            self.assertEqual(result["season_build"],BUILD)
            self.assertEqual(result["simc_revision"],REV)
            self.assertEqual(result["enchant_candidates"]["total"],2)
            self.assertEqual(result["enchant_candidates"]["selectable_count"],0)
            self.assertEqual(result["existing_allowed_input_choices"],{})
            self.assertEqual(result["proven_armor_embellishments"],{})
            self.assertFalse(result["environment_ready"])
            self.assertFalse(result["new_approval_granted"])
            self.assertEqual(result["native_calls_now"],0)
            for key in ("G","J","F","O","B","T"):
                self.assertIsNone(result[key])
            self.assertTrue(all(not row["ui_selectable"] for row in
                                result["enchant_candidates"]["items"]))

    def test_reject_mismatched_source_and_false_old_enchant_approval(self):
        with tempfile.TemporaryDirectory() as d:
            season,classified=self.inputs(pathlib.Path(d))
            bad=copy.deepcopy(classified)
            bad["counts"]["locked"]=1
            with self.assertRaisesRegex(
                    join.CatalogBlocked,"CLASSIFICATION_COUNTS"):
                join.compile_catalog(season,"a"*64,bad,"b"*64)
            bad=copy.deepcopy(classified)
            bad["rows"][0]["selection_status"]="EXISTING_EAGLE_ONE_SCOPE_USER_CHOICE"
            with self.assertRaisesRegex(
                    join.CatalogBlocked,"CLASSIFICATION_COUNTS"):
                join.compile_catalog(season,"a"*64,bad,"b"*64)
            other=copy.deepcopy(season)
            other["simc_revision"]="f"*40
            with self.assertRaisesRegex(
                    join.CatalogBlocked,"SIMC_REVISION_MISMATCH"):
                join.compile_catalog(other,"a"*64,classified,"b"*64)


if __name__=="__main__":
    unittest.main()
