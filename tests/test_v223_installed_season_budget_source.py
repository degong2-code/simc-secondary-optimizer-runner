import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from runner import v213_source_to_catalog as v213
from runner import v216_environment_build_coordinator as v216
from runner import v222_season_budget_contract as v222
from runner import v223_installed_season_budget_source as p
from tests.test_v213_source_to_catalog import SourceToCatalogTests
from tests.test_v216_environment_build_coordinator import sealed_manifest

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "gear": ROOT / "data/current_season_product_gear_db.json",
    "tier": ROOT / "data/current_season_tier_itemsets.json",
    "budget": ROOT / "data/current_season_chmv_consumables.json",
    "reference": ROOT / "integration_probes/data/midnight_s2_ilvl_chmv_reference_v1.json",
}


class InstalledSeasonSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = SourceToCatalogTests()
        cls.builder.setUpClass()
        season, classification = cls.builder.build_inputs()
        for key in ("gear", "tier", "budget"):
            season["sha256_by_input"][key] = hashlib.sha256(
                FILES[key].read_bytes()).hexdigest()
        cls.catalog = v213.compile_catalog(
            season, "a" * 64, classification, "b" * 64)
        v213.verify_catalog(cls.catalog)

    def setUp(self):
        self.user = {
            "character": {"class": "paladin", "spec": "retribution"},
            "target": {"ilevel": 334, "final_T": None},
            "oil_hands": ["main_hand"],
            "special_items": [], "embellishments": [],
        }
        self.bootstrap = {
            "target_ilevel": 334, "weapon_form": "single_two_hand",
            "plan": {
                "base_B": 3150, "final_T": 3182,
                "fixed_O": {"crit_rating": 16, "haste_rating": 16,
                            "mastery_rating": 0, "versatility_rating": 0},
            },
        }
        self.profile = (
            "main_hand=representative,id=158373,ilevel=334\n"
            "temporary_enchant=main_hand:thalassian_phoenix_oil_2\n")

    def produce(self, paths=None, catalog=None):
        cat = catalog if catalog is not None else self.catalog
        return p.produce(
            catalog=cat,
            catalog_sha="f" * 64,
            source_paths=paths if paths is not None else FILES,
            user=self.user, bootstrap=self.bootstrap,
            physical_profile=self.profile)

    def test_installed_exact_sources_gjfo_reconcile_without_native(self):
        receipt = self.produce()
        out = v222.reconcile(
            source_catalog=self.catalog,
            source_artifact_sha256="f" * 64,
            evidence=receipt["evidence"],
            plan=self.bootstrap["plan"], target_ilevel=334)
        self.assertEqual((out["reference_G"], out["J"], out["F"],
                          out["base_B"], out["final_T"]),
                         (2847, 138, 165, 3150, 3182))
        self.assertTrue(receipt["reference_rounded"])
        self.assertEqual(receipt["native_calls"], 0)
        self.assertIn("NOT_REFRESHED", receipt["status"])

    def test_other_level_uses_same_79_row_not_334_hardcode(self):
        self.user["target"]["ilevel"] = 344
        self.bootstrap["target_ilevel"] = 344
        self.bootstrap["plan"]["base_B"] = 0
        self.bootstrap["plan"]["final_T"] = 0
        receipt = self.produce()
        from runner import v089_ilvl_chmv_budget_selector as ref
        registry, _ = ref.load_registry(FILES["reference"])
        expected = registry["values"][344 - 266]["general"]
        self.bootstrap["plan"]["base_B"] = expected
        self.bootstrap["plan"]["final_T"] = expected + 32
        out = v222.reconcile(
            source_catalog=self.catalog,
            source_artifact_sha256="f" * 64,
            evidence=receipt["evidence"],
            plan=self.bootstrap["plan"], target_ilevel=344)
        self.assertEqual(out["base_B"], expected)

    def test_fury_uses_own_two_hand_reference_track(self):
        self.user["character"] = {"class": "warrior", "spec": "fury"}
        self.user["oil_hands"] = ["main_hand", "off_hand"]
        self.bootstrap["weapon_form"] = "dual_two_hand"
        self.profile = (
            "main_hand=representative,id=158373\n"
            "off_hand=representative,id=158374\n"
            "temporary_enchant=main_hand:thalassian_phoenix_oil_2/"
            "off_hand:thalassian_phoenix_oil_2\n")
        self.bootstrap["plan"]["base_B"] = 3350
        self.bootstrap["plan"]["final_T"] = 3414
        self.bootstrap["plan"]["fixed_O"] = {
            "crit_rating": 32, "haste_rating": 32,
            "mastery_rating": 0, "versatility_rating": 0}
        receipt = self.produce()
        self.assertEqual(receipt["reference_track"], "fury_dual_2h")
        self.assertEqual(receipt["evidence"]["components"]["G"]["rating"],
                         3350 - 138 - 165)
        self.assertEqual(v222.reconcile(
            source_catalog=self.catalog,
            source_artifact_sha256="f" * 64,
            evidence=receipt["evidence"], plan=self.bootstrap["plan"],
            target_ilevel=334)["final_T"], 3414)

    def test_modified_budget_bytes_block_even_if_same_numbers(self):
        with tempfile.TemporaryDirectory() as td:
            altered = Path(td) / "budget.json"
            altered.write_bytes(FILES["budget"].read_bytes() + b" ")
            paths = dict(FILES, budget=altered)
            with self.assertRaisesRegex(p.SourceBudgetBlocked,
                                        "SOURCE_BYTES"):
                self.produce(paths=paths)

    def test_tier_season_drift_and_new_build_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            tier = json.loads(FILES["tier"].read_text("utf8"))
            tier["season"] = "next_unverified_season"
            path = Path(td) / "tier.json"
            path.write_text(json.dumps(tier), encoding="utf8")
            cat = copy.deepcopy(self.catalog)
            payload = {k:v for k,v in cat.items() if k != "manifest_sha256"}
            cat["manifest_sha256"] = v213.sha(v213.canonical(payload).encode())
            with self.assertRaisesRegex(p.SourceBudgetBlocked, "SOURCE_BYTES"):
                self.produce(paths=dict(FILES, tier=path), catalog=cat)
        cat = copy.deepcopy(self.catalog)
        cat["game_build"] = "12.2.0.99999"
        with self.assertRaisesRegex(p.SourceBudgetBlocked,
                                    "V213_CATALOG_NOT_SEALED"):
            self.produce(catalog=cat)

    def test_unproved_selected_items_or_oil_hand_not_published(self):
        self.user["special_items"] = [{"slot": "neck"}]
        with self.assertRaisesRegex(p.SourceBudgetBlocked, "FIXED_L_E"):
            self.produce()
        self.user["special_items"] = []
        self.profile = self.profile.replace(
            "main_hand:thalassian_phoenix_oil_2", "disabled")
        with self.assertRaisesRegex(p.SourceBudgetBlocked, "SERIALIZATION"):
            self.produce()

    def test_v216_uses_source_producer_and_does_not_claim_refresh(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            sid = root / ("a" * 20)
            sid.mkdir()
            (sid / "profile.simc").write_text(self.profile, encoding="utf8")
            source = root / "catalog.json"
            source.write_text(json.dumps(self.catalog), encoding="utf8")
            # Internal file hash is the source artifact identity for v222.
            with mock.patch.object(v216.environment_manifest,
                                   "compile_from_paths",
                                   return_value=sealed_manifest()):
                result = v216.build_environment(
                    sessions_root=root, session_folder=sid,
                    user=self.user, binary=root / "unused",
                    revision=self.catalog["simc_revision"],
                    static_cache=None, source_catalog_path=source,
                    bootstrap_result=self.bootstrap,
                    season_budget_source_paths=FILES)
            self.assertTrue(result["receipt"]["season_budget"][
                "source_links_verified_by_v223"])
            self.assertEqual(result["receipt"]["season_budget"]["base_B"], 3150)
            self.assertFalse(result["receipt"]["source"]["refresh_performed"])
            self.assertIn(
                "SEASON_GJFO_AUTO_REFRESH_NOT_VERIFIED",
                result["receipt"]["readiness"]["limitations"])


if __name__ == "__main__":
    unittest.main()
