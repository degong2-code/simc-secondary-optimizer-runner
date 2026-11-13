"""v432 pure B8 selected physical G/L delta, no Native or product admission."""
from __future__ import annotations

import copy
import pathlib
import sys
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))
import v046_static_item_cache as cache_mod
import v212_environment_manifest as installed
import v432_selected_4pc_budget_bridge as bridge

STATS = ("crit_rating", "haste_rating", "mastery_rating",
         "versatility_rating")
SLOTS = ("head", "neck", "shoulders", "back", "chest", "wrists",
         "hands", "waist", "legs", "feet", "finger1", "finger2",
         "main_hand")


def vec(**kwargs):
    return {k: kwargs.get(k, 0) for k in STATS}


class B8BudgetPreflight(unittest.TestCase):
    def setUp(self):
        self.base = {slot: {
            "slot": slot, "item_id": 260000 + i,
            "ilevel": 334, "options": {}}
            for i, slot in enumerate(SLOTS)}
        self.groups = {slot: "tier" for slot in
                       ("head", "shoulders", "hands", "legs")}
        self.tier = {slot: (self.base[slot]["item_id"] if
                           slot != "chest" else 271495)
                     for slot in
                     ("head", "shoulders", "chest", "hands", "legs")}
        self.after = copy.deepcopy(self.base)
        self.after["head"] = {
            "slot": "head", "item_id": 239652, "ilevel": 334,
            "options": {"crafted_stats": "32/36",
                        "embellishment": "arcanoweave_lining"}}
        self.after["chest"] = {
            "slot": "chest", "item_id": self.tier["chest"],
            "ilevel": 334, "options": {}}
        self.groups["head"] = "crafted"
        self.groups["chest"] = "tier"
        self.user = {
            "target": {"ilevel": 334, "final_T": None},
            "special_items": [],
            "embellishments": [{
                "slot": "head", "item_id": 239652,
                "options": {"crafted_stats": "32/36",
                            "embellishment": "arcanoweave_lining"}}],
            "oil_hands": []}
        self.cache = cache_mod.empty_cache()
        self.link = {
            "schema": "v098_v191_original_gear_tier_link_v1",
            "status": "ORIGINAL_GEAR_TIER_RAW_SHA_LINKED_PREVIEW_ONLY",
            "source_catalog_manifest_sha256": "b" * 64,
            "source_catalog_artifact_sha256": "c" * 64,
            "raw_source_sha256": {"gear": "d" * 64, "tier": "e" * 64}}
        o = vec()
        self.doc = {
            "status": "FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY",
            "environment_ready": True, "environment_installed": True,
            "game_build": "12.1.5.70783",
            "target_ilevel": 334, "manifest_sha256": "a" * 64,
            "source_catalog_manifest_sha256": "b" * 64,
            "source_catalog_artifact_sha256": "c" * 64,
            "official_G": 2850, "official_effective_G": 2850,
            "official_J": 92, "official_F": 165,
            "official_O": o, "official_B": 3107, "official_T": 3107,
            "v222_reconciled_budget": {
                "reference_G": 2850, "effective_G": 2850,
                "J": 92, "F": 165, "fixed_O": o,
                "fixed_E": vec(), "fixed_L": vec(),
                "base_B": 3107, "final_T": 3107}}
        self.add(self.base["head"], vec(crit_rating=120))
        self.add(self.base["chest"], vec(crit_rating=130))
        self.add(self.after["head"], vec(haste_rating=145))
        self.add(self.after["chest"], vec(mastery_rating=160))

    def add(self, row, rating):
        identity = bridge._bare(row, self.cache["season"])
        stat = {"secondary": rating, "primary_other": {},
                "weapon_if_native": {}}
        record = {
            "identity": identity, "static": stat,
            "static_digest": cache_mod.digest(stat),
            "source_kind": "NATIVE_JSON2_RESOLVED_VARIANT",
            "metadata": {"native_json_sha256": "f" * 64}}
        cache_mod.merge_native(self.cache, [record])

    def run_bridge(self):
        with mock.patch.object(installed,
                               "verify_fresh_installed_environment",
                               return_value=True) as verified:
            result = bridge.reconcile(
                baseline_rows=self.base, final_rows=self.after,
                final_groups=self.groups, user=self.user,
                class_tier_five=self.tier,
                baseline_slot_ids={k: v["item_id"]
                                   for k, v in self.base.items()},
                installed_document=self.doc,
                original_v191_link=self.link,
                native_cache=self.cache,
                expected_cache_season="midnight_s2")
        verified.assert_called_once_with(self.doc)
        return result

    def test_crafted_head_chest_restore_rebases_G_without_L(self):
        out = self.run_bridge()
        self.assertEqual(out["status"],
                         "B8_SELECTED_PHYSICAL_G_L_RECONCILED_NOT_ADMITTED")
        self.assertEqual(out["four_tier_slots"],
                         ["chest", "hands", "legs", "shoulders"])
        self.assertEqual(out["changed_slots_exact_static_delta"], 55)
        self.assertEqual(out["G_projected_reference_not_native_exact"], 2905)
        self.assertEqual(out["base_B"], 3162)
        self.assertEqual(out["final_T"], 3162)
        self.assertEqual(out["fixed_L_in_G_once"], vec())
        self.assertFalse(out["runtime_native_authorized"])

    def test_special_L_is_fixed_inside_G_not_added_twice(self):
        self.groups["head"] = "special"
        self.after["head"] = {
            "slot": "head", "item_id": 290111, "ilevel": 334,
            "options": {"gem_id": "240983"}}
        self.user["embellishments"] = []
        self.user["special_items"] = [{
            "slot": "head", "item_id": 290111, "options": {}}]
        self.add(self.after["head"],
                 vec(crit_rating=50, mastery_rating=75))
        out = self.run_bridge()
        self.assertEqual(out["fixed_L_in_G_once"],
                         vec(crit_rating=50, mastery_rating=75))
        self.assertEqual(out["G_projected_reference_not_native_exact"],
                         2885)
        self.assertEqual(out["final_T"], 3142)

    def test_manual_T_wins_and_fixed_oil_is_not_reallocated(self):
        self.doc["official_O"] = vec(crit_rating=16, haste_rating=16)
        self.doc["official_T"] = 3139
        self.doc["v222_reconciled_budget"]["fixed_O"] = (
            self.doc["official_O"])
        self.doc["v222_reconciled_budget"]["final_T"] = 3139
        self.user["target"]["final_T"] = 3500
        out = self.run_bridge()
        self.assertEqual(out["base_B"], 3468)
        self.assertEqual(out["final_T"], 3500)
        self.assertEqual(sum(out["fixed_O"].values()), 32)

    def test_missing_selected_native_only_reports_exact_variant(self):
        identity = bridge._bare(self.after["head"], self.cache["season"])
        del self.cache["variants"][cache_mod.digest(identity)]
        out = self.run_bridge()
        self.assertEqual(out["status"],
                         "B8_EXACT_CHANGED_STATIC_VARIANTS_PENDING")
        self.assertEqual([x["item_id"] for x in
                          out["missing_exact_native_variants"]], [239652])
        self.assertNotIn("base_B", out)
        self.assertFalse(out["runtime_native_authorized"])

    def test_wrong_base_slot_identity_is_blocked(self):
        self.base["head"]["item_id"] = 111111
        with self.assertRaisesRegex(bridge.SelectedBudgetBlocked,
                                    "B8_V232_INSTALLED_G_BASELINE"):
            # Explicit source-owned baseline must not be inferred from
            # replaced mutable rows.
            with mock.patch.object(
                    installed, "verify_fresh_installed_environment",
                    return_value=True):
                bridge.reconcile(
                    baseline_rows=self.base, final_rows=self.after,
                    final_groups=self.groups, user=self.user,
                    class_tier_five=self.tier,
                    baseline_slot_ids={k: 260000 + i
                                       for i, k in enumerate(SLOTS)},
                    installed_document=self.doc,
                    original_v191_link=self.link,
                    native_cache=self.cache,
                    expected_cache_season="midnight_s2")

    def test_tier_or_source_drift_blocks(self):
        self.groups.pop("chest")
        with self.assertRaisesRegex(bridge.SelectedBudgetBlocked,
                                    "FOUR_TIER_DRIFT"):
            self.run_bridge()
        self.groups["chest"] = "tier"
        self.link["source_catalog_artifact_sha256"] = "0" * 64
        with self.assertRaisesRegex(bridge.SelectedBudgetBlocked,
                                    "ORIGINAL_SOURCE_IDENTITY_DRIFT"):
            self.run_bridge()

    def test_cache_identity_changes_when_selected_variant_changes(self):
        one = self.run_bridge()
        self.after["head"]["item_id"] = 239653
        self.user["embellishments"][0]["item_id"] = 239653
        self.add(self.after["head"], vec(haste_rating=146))
        two = self.run_bridge()
        self.assertNotEqual(one["selected_budget_identity_sha256"],
                            two["selected_budget_identity_sha256"])

    def test_unverified_cache_season_and_infeasible_manual_T_block(self):
        with self.assertRaisesRegex(bridge.SelectedBudgetBlocked,
                                    "CACHE_SEASON_NOT_SOURCE_BOUND"):
            with mock.patch.object(installed,
                                   "verify_fresh_installed_environment",
                                   return_value=True):
                bridge.reconcile(
                    baseline_rows=self.base, final_rows=self.after,
                    final_groups=self.groups, user=self.user,
                    class_tier_five=self.tier,
                    baseline_slot_ids={k: v["item_id"]
                                       for k, v in self.base.items()},
                    installed_document=self.doc,
                    original_v191_link=self.link,
                    native_cache=self.cache,
                    expected_cache_season="other_season")
        self.user["target"]["final_T"] = 50
        with self.assertRaisesRegex(bridge.SelectedBudgetBlocked,
                                    "FIXED_MINIMA_INFEASIBLE"):
            self.run_bridge()


if __name__ == "__main__":
    unittest.main()
