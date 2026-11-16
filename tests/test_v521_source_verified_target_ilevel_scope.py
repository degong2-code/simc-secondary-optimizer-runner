"""M1/M2 new-season target level scope, offline only, Native/network 0.

This regression tests contracts, NOT proof of new-season item IDs, rating G,
source admission, physical Native acceptance or end-to-end product READY.
"""
from __future__ import annotations

import copy
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))
import v106_user_session_controller as sessions
import v098_target_user_scenario_bootstrap as bootstrap
import v139_pure_target_profile_composer as pure


class FreshTargetLevelScope(unittest.TestCase):
    def user(self, level=350):
        controls = sessions.standard_controls(("paladin", "retribution"))
        controls["ilevel"] = level
        return sessions.user_scenario(controls)

    def test_new_target_input_is_not_stuck_at_old_344_ceiling(self):
        self.assertEqual(self.user()["target"]["ilevel"], 350)
        with self.assertRaisesRegex(sessions.SessionBlocked, "ILVL_OUT_OF_REFERENCE"):
            self.user(1001)

    def test_fresh_sha_required_for_source_level_beyond_old_reference(self):
        with tempfile.TemporaryDirectory() as folder:
            binary = pathlib.Path(folder) / "fake-simc"
            binary.write_bytes(b"NO_SIMC_NATIVE")
            user = self.user()
            with mock.patch.object(sessions, "source_catalog_identity",
                                   return_value={"test_only": True}), \
                 mock.patch.object(sessions.profile_stage, "session_identity",
                                   return_value={"test_only": True}):
                with self.assertRaisesRegex(
                        sessions.SessionBlocked,
                        "CURRENT_SEASON_PRODUCT_SCOPE_TARGET_RANGE"):
                    sessions.session_key(
                        user, binary, "a" * 12,
                        current_season_product=True,
                        source_catalog_path=str(pathlib.Path(folder) / "source.json"))
                key, identity = sessions.session_key(
                    user, binary, "a" * 12,
                    current_season_product=True,
                    source_catalog_path=str(pathlib.Path(folder) / "source.json"),
                    fresh_installed_manifest_sha256="b" * 64)
            self.assertEqual(len(key), 20)
            self.assertEqual(identity["fresh_v212_installed_manifest_sha256"],
                             "b" * 64)

    def test_historical_product_bootstrap_still_blocks_unverified_350(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            binary = root / "fake-simc"
            binary.write_bytes(b"NO_SIMC_NATIVE")
            with self.assertRaisesRegex(
                    bootstrap.UserScenarioBlocked,
                    "CURRENT_SEASON_PRODUCT_SCOPE_TARGET_RANGE"):
                bootstrap.build(
                    self.user(), root / "generated", binary, "a" * 12,
                    current_season_product=True)

    def test_matching_season_catalog_350_composes_without_old_level_preview(self):
        # The synthetic level change is only a composer contract fixture.
        # It does not certify actual item ilvl scaling or source readiness.
        season = copy.deepcopy(pure.catalog())
        season["target_ilevel"] = 350
        character = {
            "class": "druid", "spec": "balance",
            "race": "night_elf", "talents": "CAAAABBB11122"}
        trinkets = [
            {"slot": "trinket1", "item_id": 270175, "options": {}},
            {"slot": "trinket2", "item_id": 270173, "options": {}}]
        profile, cfg, rows, *_ = pure.v098_inputs(
            character, trinkets, target_ilevel=350,
            season_override=season, level_preview=False,
            source_only_season_consumables=True)
        self.assertEqual(cfg["target"]["ilevel"], 350)
        self.assertTrue(all(row["ilevel"] == 350 for row in rows.values()))
        self.assertIn("ilevel=350", profile)
        # A 350 preview against the old 334 catalog remains forbidden.
        with self.assertRaisesRegex(
                pure.ProfileStageBlocked,
                "NONDEFAULT_LEVEL_PREVIEW_OUTSIDE_REFERENCE"):
            pure.v098_inputs(
                character, trinkets, target_ilevel=350,
                level_preview=True, source_only_season_consumables=True)

    def test_web_controls_accept_350_but_not_unverified_install(self):
        html = (ROOT / "runner/webui/index.html").read_text(encoding="utf8")
        js = (ROOT / "runner/webui/app.js").read_text(encoding="utf8")
        self.assertIn(
            'id="ilevel" type="number" min="1" max="1000"', html)
        self.assertIn("level>=1&&level<=1000", js)
        self.assertIn("controls.ilevel<1||controls.ilevel>1000", js)
        self.assertIn("ilvl!=season_override[\"target_ilevel\"]",
                      (ROOT / "runner/v098_target_user_scenario_bootstrap.py")
                      .read_text(encoding="utf8"))


if __name__ == "__main__":
    unittest.main()
