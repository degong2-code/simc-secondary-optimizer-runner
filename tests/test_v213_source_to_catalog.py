from __future__ import annotations

import copy
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))

import v196_current_season_user_catalog as v196
import v213_source_to_catalog as v213


class SourceToCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gear_source = json.loads(
            (ROOT / "data/current_season_product_gear_db.json").read_text("utf8"))
        cls.tier_source = json.loads(
            (ROOT / "data/current_season_tier_itemsets.json").read_text("utf8"))
        cls.enchant_source = json.loads(
            (ROOT / "data/current_season_simc_enchant_candidates.json").read_text("utf8"))
        cls.runtime_classification = json.loads(
            (ROOT / "data/current_season_enchant_effect_classification.json").read_text("utf8"))

    def build_inputs(self):
        candidates = []
        for row in self.enchant_source["rows"]:
            item = dict(row)
            item["simc_token"] = item.pop("token")
            item["inventory_type_options"] = [
                i for i in range(1, 31)
                if item["inventory_type_mask"] & (1 << i)]
            item["user_selectable"] = False
            candidates.append(item)

        tier_classes = {}
        for class_name, row in self.tier_source["classes"].items():
            tier_classes[class_name] = {
                "allowed_class_mask": row["allowed_class_mask"],
                "item_set_id": row["item_set_id"],
                "names": dict(row["names"]),
                "pieces": dict(row["pieces"]),
            }

        food = [{"item_id": 700000 + i, "kind": "food"} for i in range(192)]
        potion = [{"item_id": 710000 + i, "kind": "potion"} for i in range(61)]
        embellishments = [{
            "kind": "embellishment_or_darkmoon",
            "actual_item_id": "UNRESOLVED",
            "ui_selectable": False,
        } for _ in range(20)]
        temporary = [{
            "enchant_id": 720000 + i,
            "simc_token": "temporary_test_" + str(i),
            "user_selectable": False,
        } for i in range(117)]

        season = {
            "schema": "v191_unified_patch_season_expansion_data_candidates_v1",
            "status": "SOURCE_COMBINED_NOT_YET_USER_SELECTABLE",
            "source_first": True,
            "automatic_ui_promotion": False,
            "native_calls": 0,
            "network_calls_by_compiler": 0,
            "game_build": "12.1.5.70575",
            "expansion_id": 11,
            "simc_revision": "710c2408bfd3ae4df71b8cd55cdf01f63fd6c926",
            "simc_generated_sources": {
                name: {
                    "source_build": "12.1.5.70575",
                    "declared_rows": 100 if name == "permanent_enchant" else 50,
                    "sha256": "6" * 64,
                }
                for name in ("permanent_enchant", "temporary_enchant", "gem_property")
            },
            "source_artifacts": {
                "v189": {
                    "schema": "v189_pinned_simc_effect_registration_candidates_v1",
                    "simc_commit": "710c2408bfd3ae4df71b8cd55cdf01f63fd6c926",
                    "source_sha256": "a" * 64,
                },
                "v190": {
                    "schema": "v190_same_build_consumable_item_candidates_v1",
                    "game_build": "12.1.5.70575",
                    "simc_revision": "710c2408bfd3ae4df71b8cd55cdf01f63fd6c926",
                    "simc_registration_sha256": "a" * 64,
                },
            },
            "sha256_by_input": {
                "gear": "1" * 64, "tier": "2" * 64, "budget": "3" * 64,
                "v189": "4" * 64, "v190": "5" * 64,
            },
            "related_source_counts": {
                "gear_item_candidates": len(self.gear_source["items"]),
                "tier_piece_ids": 65,
                "food_raw_item_candidates": len(food),
                "potion_raw_item_candidates": len(potion),
                "food_handler_registrations": 37,
                "potion_handler_registrations": 5,
                "embellishment_darkmoon_registrations": len(embellishments),
                "temporary_enchant_entries": 117,
                "gem_property_records": 2409,
            },
            "gear": {
                "count": len(self.gear_source["items"]),
                "candidates": copy.deepcopy(self.gear_source["items"]),
            },
            "tier": {
                "class_count": 13,
                "piece_count": 65,
                "classes": tier_classes,
            },
            "consumables": {
                "food": {"candidates": food, "stage": "DB2_ID_ONLY"},
                "potion": {"candidates": potion, "stage": "DB2_ID_ONLY"},
                "flask": {"stage": "FIXED_REFERENCE"},
                "augmentation_rune": {"stage": "PENDING"},
                "weapon_oils": {"stage": "PENDING"},
                "general_gems": {"stage": "PENDING"},
                "special_diamonds": {"stage": "PENDING"},
            },
            "embellishments": {"registered_effects": embellishments},
            "enchants": {
                "current_season_midnight": {
                    "count": 38, "highest_rank_candidates": candidates,
                },
                "temporary": {
                    "source_rows": 117, "highest_rank_candidates": temporary,
                },
            },
            "gem_properties": {"source_count": 2409, "stage": "PENDING"},
        }

        by_id = {x["enchant_id"]: x for x in candidates}
        classification_rows = []
        for compact in self.runtime_classification["rows"]:
            candidate = by_id[compact["enchant_id"]]
            static_components = [
                {"item_mod": name, "category": "CHMV_SECONDARY_RATING"}
                for name in compact["static_components"]
            ]
            spells = [
                {"driver_spell_id": spell_id, "effect_role": role}
                for spell_id, role in zip(
                    compact["driver_spell_ids"], compact["spell_effect_roles"])
            ]
            classification_rows.append({
                "token": compact["token"],
                "enchant_id": compact["enchant_id"],
                "quality_rank": candidate["quality_rank"],
                "item_class": candidate["item_class"],
                "inventory_type_mask": candidate["inventory_type_mask"],
                "item_subclass_mask": candidate["item_subclass_mask"],
                "static_components": static_components,
                "spell_effects": spells,
                "unknown_components": [],
                "effect_family": compact["effect_family"],
                "effect_summary": compact["effect_summary"],
                "static_chmv_rating_present_in_dbc":
                    compact["static_chmv_rating_present"],
                "static_chmv_stats": compact["static_chmv_stats"],
                "dynamic_chmv_proc_present_in_spell_text":
                    compact["dynamic_chmv_proc_present"],
                "dynamic_chmv_proc_roles": compact["dynamic_chmv_proc_roles"],
                "simc_effect_owner": compact["simc_effect_owner"],
                "simc_effect_reimplemented": compact["simc_effect_reimplemented"],
                "simc_custom_handlers": compact["simc_custom_handlers"],
                "simc_generic_or_unregistered_spell_count":
                    compact["simc_generic_or_unregistered_spell_count"],
                "native_E_evidence": {
                    "status": compact["native_E_status"],
                    "static_E": compact["native_E"],
                },
                "selection_status": compact["selection_status"],
            })

        classification = {
            "schema": "v211_current_season_enchant_effect_classification_v1",
            "status":
                "SOURCE_CLASSIFIED_NOT_GENERAL_NATIVE_ACCEPTANCE_OR_UI_PROMOTION",
            "season_game_build": "12.1.5.70575",
            "simc_commit": "710c2408bfd3ae4df71b8cd55cdf01f63fd6c926",
            "candidate_source_schema":
                "v191_unified_patch_season_expansion_data_candidates_v1",
            "candidate_source_artifact_id": None,
            "source_files": self.runtime_classification["source_files"],
            "simc_item_enchant_pipeline":
                self.runtime_classification["simc_item_enchant_pipeline"],
            "counts": self.runtime_classification["counts"],
            "native_calls": 0,
            "network_calls_by_classifier": 0,
            "automatic_ui_promotion": False,
            "simc_effect_reimplemented": False,
            "rows": classification_rows,
        }
        return season, classification

    def compile(self, season=None, classification=None):
        if season is None or classification is None:
            season, classification = self.build_inputs()
        return v213.compile_catalog(
            season, "a" * 64, classification, "b" * 64)

    def test_actual_source_rows_join_and_v196_preserves_approval_boundary(self):
        result = self.compile()
        self.assertTrue(v213.verify_catalog(result))
        self.assertEqual(result["status"],
                         "SOURCE_TO_CATALOG_JOINED_NOT_USER_PUBLISHED")
        self.assertEqual(result["native_calls"], 0)
        self.assertEqual(result["network_calls"], 0)
        self.assertEqual(result["catalog"]["gear"]["count"], 511)
        self.assertEqual(result["catalog"]["tier"]["class_count"], 13)
        self.assertEqual(result["catalog"]["tier"]["piece_count"], 65)
        self.assertEqual(result["catalog"]["enchants"]["count"], 38)
        self.assertEqual(result["catalog"]["enchants"]["group_counts"], {
            "boots": 3, "chest": 4, "helm": 6, "ring": 9,
            "shoulders": 6, "weapon": 10,
        })
        self.assertEqual(result["v196_enchant_source"]["source_artifact_id"], None)
        self.assertTrue(all(not x["approved"]
                            for x in result["v196_enchant_source"]["rows"]))
        self.assertTrue(all(not x["ui_selectable"]
                            for x in result["catalog"]["enchants"]["items"]))

        with tempfile.TemporaryDirectory() as td:
            path = pathlib.Path(td) / "v213_source_to_catalog.json"
            path.write_text(json.dumps(result, ensure_ascii=False), encoding="utf8")
            ui = v196.public_options(path)
        self.assertEqual(ui["enchant_candidates"]["total"], 38)
        self.assertEqual(ui["enchant_candidates"]["source_classified_count"], 38)
        self.assertEqual(
            [x["enchant_id"] for x in ui["enchant_candidates"]["items"]
             if x["ui_selectable"]], [7967])
        self.assertEqual(ui["source_catalog"]["manifest_sha256"],
                         result["manifest_sha256"])
        self.assertEqual(ui["source_catalog"]["summary"]["gear"]["count"], 511)
        self.assertEqual(ui["native_calls_now"], 0)
        self.assertFalse(ui["optimizer_or_cache_mutated"])

    def test_unknown_gear_inventory_type_is_retained_as_pending(self):
        season, classification = self.build_inputs()
        season["gear"]["candidates"][0]["inventory_type"] = 999
        result = self.compile(season, classification)
        self.assertEqual(result["catalog"]["gear"]["unresolved_count"], 1)
        self.assertIn("UNKNOWN_INVENTORY_TYPE_999",
                      result["catalog"]["gear"]["slot_group_counts"])
        self.assertIn("GEAR_SLOT_UNKNOWN:158344",
                      result["catalog"]["gear"]["unresolved"])

    def test_enchant_mask_drift_blocks_exact_join(self):
        season, classification = self.build_inputs()
        season["enchants"]["current_season_midnight"]["highest_rank_candidates"][0][
            "inventory_type_options"] = []
        with self.assertRaisesRegex(v213.CatalogBlocked,
                                    "V191_ENCHANT_MASK_OPTIONS_DRIFT"):
            self.compile(season, classification)

    def test_missing_or_mismatched_classification_blocks(self):
        season, classification = self.build_inputs()
        classification["rows"][0]["token"] = "enchant_boots__wrong_source"
        with self.assertRaisesRegex(v213.CatalogBlocked,
                                    "EXACT_ENCHANT_IDENTITY_JOIN_MISSING"):
            self.compile(season, classification)

    def test_build_or_revision_mismatch_blocks(self):
        season, classification = self.build_inputs()
        classification["season_game_build"] = "12.1.5.70576"
        with self.assertRaisesRegex(v213.CatalogBlocked, "GAME_BUILD_MISMATCH"):
            self.compile(season, classification)

    def test_manifest_digest_detects_catalog_mutation(self):
        result = self.compile()
        result["catalog_summary"]["gear"]["count"] = 0
        with self.assertRaisesRegex(v213.CatalogBlocked, "DIGEST_MISMATCH"):
            v213.verify_catalog(result)


if __name__ == "__main__":
    unittest.main()
