import json
import shutil
import tempfile
import unittest
from pathlib import Path

from runner import v143_specialization_contracts as specs
from runner import v196_current_season_user_catalog as ui_catalog
from runner import v206_nonchmv_eagle_selection as eagle
from runner import v212_environment_manifest as p
from runner import v213_source_to_catalog as source_bridge
from tests.test_v213_source_to_catalog import SourceToCatalogTests


class EnvironmentManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_builder = SourceToCatalogTests()
        cls.source_builder.setUpClass()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        season, classification = self.source_builder.build_inputs()
        self.source_catalog = source_bridge.compile_catalog(
            season, "a" * 64, classification, "b" * 64)
        self.source_path = self.root / "v213_source_to_catalog.json"
        self.source_path.write_text(
            json.dumps(self.source_catalog, ensure_ascii=False,
                       sort_keys=True, indent=2) + "\n", encoding="utf8")
        self.source_catalog_sha = p.sha(self.source_path.read_bytes())
        self.ui = ui_catalog.public_options(self.source_path)
        self.ui_sha = p.sha(p.canonical(self.ui).encode("utf8"))
        self.binary = self.root / "simc_not_executed.bin"
        self.binary.write_bytes(b"SIMC_TEST_BINARY_NEVER_EXECUTED")
        self.target = self.root / "target"
        self.target.mkdir()
        self.selected = {
            "schema": eagle.SCHEMA,
            "choice": dict(eagle.CHOICE),
            "effect_family": "crit_effectiveness",
            "static_CHMV_E": dict(eagle.E_ZERO),
            "budget_policy":
                "NON_CHMV_NO_CHANGE_TO_REFERENCE_B_OR_FINAL_T",
            "native_static_scope":
                "ONE_WINDOWS_PALADIN334_STATIC_E_ZERO_NOT_ALL_DPS",
            "mechanics_owner": "SimC",
        }
        target_manifest = {
            "profile_simc": "profile.simc",
            "scenario_json": "scenario.json",
            "fillers_json": "fillers.json",
            "native_binary": str(self.binary),
            "native_revision": self.source_catalog["simc_revision"],
            "native_limit": 6,
            "weapon_layout": "one_hand_frill",
            "oil_hands": ["main_hand"],
            "flask_F": 165,
            "seed_targets_B": [
                {"crit_rating": 700, "haste_rating": 800,
                 "mastery_rating": 900, "versatility_rating": 750},
                {"crit_rating": 900, "haste_rating": 700,
                 "mastery_rating": 800, "versatility_rating": 750},
            ],
            "static_cache_json": None,
        }
        (self.target / "manifest.json").write_text(
            json.dumps(target_manifest), encoding="utf8")
        (self.target / "profile.simc").write_text(
            "spec=retribution\n"
            "finger1=selected_ring,id=240111,ilevel=334,enchant_id=7967\n",
            encoding="utf8")
        (self.target / "scenario.json").write_text(
            json.dumps({"equipment": {"special": []},
                        "character": {"class": "paladin",
                                      "spec": "retribution"},
                        "target": {"ilevel": 334}}),
            encoding="utf8")
        (self.target / "fillers.json").write_text("[]\n", encoding="utf8")
        self.bootstrap = {
            "schema": p.V098,
            "native_calls": 0,
            "status": "READY_INTERNAL_MANIFEST_ZERO_NATIVE",
            "current_season_product": True,
            "all_specs_ready": False,
            "supported_archetypes_now": 24,
            "template_archetype": "paladin/retribution",
            "target_ilevel": 334,
            "generated_manifest": str(self.target / "manifest.json"),
            "plan": {
                "class": "paladin", "spec": "retribution",
                "base_B": 3150, "final_T": 3182, "item_slots": 15,
                "fixed_O": {"crit_rating": 16, "haste_rating": 16,
                            "mastery_rating": 0, "versatility_rating": 0},
                "budget_source": "REFERENCE_B_PLUS_FIXED_O",
                "scenario_digest": "c" * 64,
                "source_profile_sha256": "d" * 64,
            },
            "selected_nonchmv_enchant": self.selected,
        }

    def compile(self):
        return p.compile_manifest(
            self.source_catalog, self.source_catalog_sha,
            self.ui, self.ui_sha, self.bootstrap, self.target)

    def test_v213_real_source_contract_and_exact_7967_approval(self):
        result = self.compile()
        self.assertTrue(source_bridge.verify_catalog(self.source_catalog))
        self.assertEqual(result["schema"], p.SCHEMA)
        self.assertEqual(result["status"], "READY_WITH_LIMITATIONS")
        self.assertEqual(result["native_calls"], 0)
        self.assertEqual(result["network_calls"], 0)
        self.assertEqual(result["source_catalog"]["artifact_sha256"],
                         self.source_catalog_sha)
        self.assertEqual(result["source_catalog"]["manifest_sha256"],
                         self.source_catalog["manifest_sha256"])
        self.assertEqual(result["approved_ui_catalog"]["selectable_enchant_ids"],
                         [7967])
        self.assertEqual(result["approved_ui_catalog"]["developer_only_enchant_ids"],
                         [8025])
        self.assertEqual(result["selected_nonchmv_enchant"]["selected_id"], 7967)
        self.assertEqual(result["selected_nonchmv_enchant"]["budget_increment"], 0)
        self.assertEqual(result["target_profile"]["base_B"], 3150)
        self.assertEqual(result["target_profile"]["final_T"], 3182)
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
        shutil.copytree(self.target, other)
        moved_bootstrap = dict(self.bootstrap)
        moved_bootstrap["generated_manifest"] = str(other / "manifest.json")
        moved = p.compile_manifest(
            self.source_catalog, self.source_catalog_sha,
            self.ui, self.ui_sha, moved_bootstrap, other)
        self.assertEqual(first["manifest_sha256"], moved["manifest_sha256"])

    def test_build_or_revision_mismatch_fails_closed(self):
        self.ui["season_build"] = "12.1.5.70576"
        with self.assertRaisesRegex(p.EnvironmentBlocked,
                                    "BUILD_OR_REVISION_MISMATCH"):
            self.compile()
        self.ui["season_build"] = self.source_catalog["game_build"]
        self.ui["simc_revision"] = "c" * 40
        with self.assertRaisesRegex(p.EnvironmentBlocked,
                                    "BUILD_OR_REVISION_MISMATCH"):
            self.compile()

    def test_wrong_or_expanded_approved_id_fails_closed(self):
        items = self.ui["enchant_candidates"]["items"]
        next(x for x in items if x["enchant_id"] == 7967)["ui_selectable"] = False
        next(x for x in items if x["enchant_id"] == 8025)["ui_selectable"] = True
        self.ui["enchant_candidates"]["selectable_count"] = 1
        with self.assertRaisesRegex(p.EnvironmentBlocked,
                                    "EXACT_APPROVED_ENCHANT_ID_MISMATCH"):
            self.compile()

    def test_bootstrap_cannot_select_developer_only_or_other_enchant(self):
        self.bootstrap["selected_nonchmv_enchant"] = {
            **self.selected, "choice": {"finger1": 8025}}
        with self.assertRaisesRegex(p.EnvironmentBlocked,
                                    "SELECTED_ENCHANT_NOT_EXACT_EXISTING_APPROVAL"):
            self.compile()

    def test_v213_digest_or_artifact_sha_mismatch_fails_closed(self):
        self.source_catalog["manifest_sha256"] = "0" * 64
        with self.assertRaisesRegex(p.CatalogBlocked,
                                    "V213_CATALOG_DIGEST_MISMATCH"):
            self.compile()
        self.source_catalog["manifest_sha256"] = p.sha(
            p.canonical({k: v for k, v in self.source_catalog.items()
                         if k != "manifest_sha256"}).encode("utf8"))
        with self.assertRaisesRegex(p.EnvironmentBlocked,
                                    "ARTIFACT_FILE_SHA256_INVALID"):
            p.compile_manifest(self.source_catalog, "not-a-sha",
                               self.ui, self.ui_sha,
                               self.bootstrap, self.target)

    def test_profile_change_changes_environment_identity(self):
        first = self.compile()
        with (self.target / "profile.simc").open("a", encoding="utf8") as stream:
            stream.write("desired_targets=2\n")
        second = self.compile()
        self.assertNotEqual(first["manifest_sha256"], second["manifest_sha256"])

    def test_selected_special_requires_bound_static_cache_snapshot(self):
        scenario = {
            "equipment": {"special": [{
                "slot": "back", "item_id": 159288, "ilevel": 331,
                "options": {},
            }]},
            "character": {"class": "shaman", "spec": "elemental"},
            "target": {"ilevel": 331},
        }
        (self.target / "scenario.json").write_text(
            json.dumps(scenario), encoding="utf8")
        with self.assertRaisesRegex(p.EnvironmentBlocked,
                                    "SELECTED_SPECIAL_STATIC_L_CACHE_SNAPSHOT_MISSING"):
            self.compile()

    def test_augmentation_and_non_dps_contracts_are_not_accepted(self):
        self.bootstrap["template_archetype"] = "evoker/augmentation"
        with self.assertRaisesRegex(p.EnvironmentBlocked,
                                    "PRODUCT_DPS_26_SPECIALIZATION_CONTRACT_DRIFT"):
            self.compile()
        self.assertEqual(len(specs.CONTRACTS), 26)
        self.assertNotIn("evoker/augmentation", specs.CONTRACTS)

    def test_native_or_ui_promotion_in_source_artifact_fails_closed(self):
        self.source_catalog["native_calls"] = 1
        self.source_catalog["manifest_sha256"] = p.sha(
            p.canonical({k: v for k, v in self.source_catalog.items()
                         if k != "manifest_sha256"}).encode("utf8"))
        with self.assertRaisesRegex(p.CatalogBlocked,
                                    "V213_CATALOG_CONTRACT_INVALID"):
            self.compile()


if __name__ == "__main__":
    unittest.main()
