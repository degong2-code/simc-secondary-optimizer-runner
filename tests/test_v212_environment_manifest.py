import json
import tempfile
import unittest
from pathlib import Path

from runner import v212_environment_manifest as p


class EnvironmentManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.binary = self.root / "simc"
        self.binary.write_bytes(b"SIMC-TEST-BINARY")
        self.target = self.root / "target"
        self.target.mkdir()
        target_manifest = {
            "profile_simc": "profile.simc",
            "scenario_json": "scenario.json",
            "fillers_json": "fillers.json",
            "native_binary": str(self.binary),
            "native_revision": "a" * 40,
            "native_limit": 6,
            "weapon_layout": "onehand",
            "oil_hands": ["main_hand"],
            "flask_F": 165,
            "seed_targets_B": [[10, 20, 30, 40], [40, 30, 20, 10]],
            "static_cache_json": None,
        }
        (self.target / "manifest.json").write_text(
            json.dumps(target_manifest), encoding="utf8")
        (self.target / "profile.simc").write_text("spec=frost\n", encoding="utf8")
        (self.target / "scenario.json").write_text('{"spec":"frost"}\n', encoding="utf8")
        (self.target / "fillers.json").write_text("[]\n", encoding="utf8")
        self.season = {
            "schema": p.V191, "source_first": True,
            "automatic_ui_promotion": False, "native_calls": 0,
            "game_build": "12.1.5.70575", "simc_revision": "a" * 40,
        }
        self.enchants = {
            "schema": p.V211, "automatic_ui_promotion": False,
            "native_calls": 0, "simc_effect_reimplemented": False,
            "season_game_build": "12.1.5.70575", "simc_commit": "a" * 40,
            "counts": {"total": 38}, "rows": [{"enchant_id": i} for i in range(38)],
            "source_files": {"permanent_enchant.inc": {"sha256": "b" * 64}},
        }
        self.ui = {
            "schema": p.V196, "season_build": "12.1.5.70575",
            "simc_revision": "a" * 40,
            "enchant_candidates": {"total": 38, "selectable_count": 1,
                                   "source_classification_counts": {
                                       "native_E_measured": 2}},
        }
        self.bootstrap = {
            "schema": p.V098, "native_calls": 0,
            "status": "READY_INTERNAL_MANIFEST_ZERO_NATIVE",
            "all_specs_ready": False, "template_archetype": "mage/frost",
            "target_ilevel": 334, "generated_manifest": str(self.target / "manifest.json"),
            "plan": {"base_B": 3150, "final_T": 3182},
        }

    def compile(self):
        return p.compile_manifest(
            self.season, "1" * 64, self.enchants, "2" * 64,
            self.ui, "3" * 64, self.bootstrap, "4" * 64, self.target)

    def test_builds_ready_with_limitations_and_native_zero(self):
        result = self.compile()
        self.assertEqual(result["schema"], p.SCHEMA)
        self.assertEqual(result["status"], "READY_WITH_LIMITATIONS")
        self.assertEqual(result["native_calls"], 0)
        self.assertEqual(result["network_calls"], 0)
        self.assertEqual(result["target_profile"]["base_B"], 3150)
        self.assertEqual(result["target_profile"]["final_T"], 3182)
        self.assertEqual(result["approved_ui_catalog"]["selectable_enchant_count"], 1)
        self.assertEqual(result["target_profile"]["runtime_binary"]["sha256"],
                         p.sha_file(self.binary)["sha256"])
        self.assertIn("ALL_26_DPS_REPRESENTATIVE_PROFILE_SUPPLIERS",
                      result["unresolved_dependencies"])

    def test_same_inputs_produce_byte_stable_manifest(self):
        first = self.compile()
        second = self.compile()
        self.assertEqual(p.canonical(first), p.canonical(second))
        self.assertEqual(first["manifest_sha256"], second["manifest_sha256"])

    def test_same_profile_at_different_local_root_has_same_environment_digest(self):
        first = self.compile()
        other = self.root / "relocated-target"
        other.mkdir()
        for name in ("manifest.json", "profile.simc", "scenario.json", "fillers.json"):
            (other / name).write_bytes((self.target / name).read_bytes())
        moved_bootstrap = dict(self.bootstrap)
        moved_bootstrap["generated_manifest"] = str(other / "manifest.json")
        moved = p.compile_manifest(
            self.season, "1" * 64, self.enchants, "2" * 64,
            self.ui, "3" * 64, moved_bootstrap, "9" * 64, other)
        self.assertEqual(first["manifest_sha256"], moved["manifest_sha256"])

    def test_build_mismatch_fails_closed(self):
        self.enchants["season_game_build"] = "12.1.5.70576"
        with self.assertRaisesRegex(p.EnvironmentBlocked, "GAME_BUILD_MISMATCH"):
            self.compile()

    def test_simc_revision_mismatch_fails_closed(self):
        self.ui["simc_revision"] = "c" * 40
        with self.assertRaisesRegex(p.EnvironmentBlocked, "SIMC_REVISION_MISMATCH"):
            self.compile()

    def test_unapproved_ui_expansion_fails_closed(self):
        self.ui["enchant_candidates"]["selectable_count"] = 2
        with self.assertRaisesRegex(p.EnvironmentBlocked, "APPROVAL_BOUNDARY_CHANGED"):
            self.compile()

    def test_profile_file_change_changes_environment_identity(self):
        first = self.compile()
        (self.target / "profile.simc").write_text("spec=fire\n", encoding="utf8")
        second = self.compile()
        self.assertNotEqual(first["manifest_sha256"], second["manifest_sha256"])

    def test_profile_path_escape_fails_closed(self):
        outside = self.root / "outside.simc"
        outside.write_text("spec=frost\n", encoding="utf8")
        (self.target / "profile.simc").unlink()
        (self.target / "profile.simc").symlink_to(outside)
        with self.assertRaisesRegex(p.EnvironmentBlocked, "ESCAPES_ROOT"):
            self.compile()

    def test_native_or_ui_promotion_in_source_artifact_fails_closed(self):
        self.season["native_calls"] = 1
        with self.assertRaisesRegex(p.EnvironmentBlocked, "V191_SOURCE_CANDIDATE"):
            self.compile()


if __name__ == "__main__":
    unittest.main()
