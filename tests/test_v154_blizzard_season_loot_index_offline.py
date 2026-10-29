"""Bounded Blizzard encounter lookup: existing ID reconciliation only, NO network/Native."""
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))
import v154_blizzard_season_loot_index as discovery

class BlizzardSeasonEvidenceOffline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = discovery.existing_reference(
            discovery.read_json(discovery.MASTER),
            discovery.read_json(discovery.DELTA))

    def test_real_existing_master_and_partial_patch_are_used_not_generated(self):
        r = self.ref
        self.assertEqual(r["source_rows"], 395)
        self.assertEqual(r["master_distinct_ids"], 394)
        self.assertEqual(r["delta_rows"], 10)
        self.assertEqual(sum(x["known_effect_candidate"]
                             for x in r["known"].values()), 80)
        self.assertTrue(r["known"][271874]["known_effect_candidate"])
        self.assertTrue(r["known"][281235]["delta_special_armor"])
        self.assertEqual(r["known"][251139]["source_classes"], ["mplus"])
        report = discovery.reference_only(r)
        self.assertEqual(report["blizzard_requests"], 0)
        self.assertEqual(report["status"],
                         "EXISTING_REFERENCE_ONLY_BLIZZARD_UNQUERIED")
        self.assertEqual(report["loot_coverage"],
                         "NOT_EVALUATED_NO_BLIZZARD_RESPONSE")

    def test_mock_journal_response_matches_existing_ids_and_unknowns(self):
        # Fabricated provider JSON strictly verifies parser wiring, never
        # claims real Blizzard loot acceptance or 2026 current drop lists.
        query = discovery.selected_encounters({"encounters": [
            {"encounter_id": 101, "instance_id": 10, "kind": "raid"},
            {"encounter_id": 102, "instance_id": 20, "kind": "mplus"},
            {"encounter_id": 103, "instance_id": 30, "kind": "delve"}]})
        docs = {
            101: {"id": 101, "items": [
                {"item": {"id": 271874}}, {"item": {"id": 281235}},
                {"item": {"id": 271874}}, {"item": {"id": 999999}}]},
            102: {"id": 102, "loot": [{"id": 251139}]},
            103: {"id": 103, "name": "Field without loot, UNKNOWN"}}
        outcome = discovery.reconcile(self.ref, query, docs)
        self.assertEqual(outcome["provider"]["observed_unique_item_ids"], 4)
        self.assertEqual(outcome["provider"]["matched_existing_ids"], 3)
        self.assertEqual(outcome["provider"]["not_in_existing_ids"], 1)
        self.assertEqual(outcome["provider"]["prior_effect_candidates_found"], 1)
        self.assertEqual(outcome["provider"]["prior_delta_special_armor_found"], 1)
        self.assertEqual(outcome["provider"]["loot_field_unavailable_encounters"],
                         [103])
        self.assertFalse(outcome["season_loot_complete"])
        self.assertFalse(outcome["static_L_populated"])
        self.assertEqual(outcome["simc_native_calls"], 0)

    def test_unknown_loot_is_not_empty_and_not_any_nested_spell_id(self):
        self.assertIsNone(discovery.encounter_loot({"id": 7,
            "abilities": [{"id": 999999}]}, 7))
        self.assertEqual(discovery.encounter_loot({"id": 7, "items": []}, 7), [])
        for bad in (
            {"id": 7, "items": [{"spell": {"id": 268250}}]},
            {"id": 7, "items": [{"id": "268250"}]},
            {"id": 7, "items": [{"item": {"id": 0}}]},
            {"id": 7, "items": [], "loot": []},
            {"id": 8, "items": [{"id": 268250}]}):
            with self.subTest(document=bad), self.assertRaises(discovery.LootBlocked):
                discovery.encounter_loot(bad, 7)

    def test_bounded_scope_and_token_not_embedded_or_logged(self):
        with self.assertRaises(discovery.LootBlocked):
            discovery.selected_encounters({"encounters": []})
        with self.assertRaises(discovery.LootBlocked):
            discovery.selected_encounters({"encounters": [{
                "encounter_id": i + 1, "instance_id": 1, "kind": "raid"}
                for i in range(49)]})
        with self.assertRaises(discovery.LootBlocked):
            discovery.selected_encounters({"encounters": [
                {"encounter_id": 1, "instance_id": 1, "kind": "raid"},
                {"encounter_id": 1, "instance_id": 2, "kind": "mplus"}]})
        with self.assertRaises(discovery.LootBlocked):
            discovery.fetch_encounter(1234, "secret", "invalid")
        with mock.patch.object(discovery.urllib.request, "urlopen") as fetch:
            result = discovery.main(["--master", str(discovery.MASTER),
                "--delta", str(discovery.DELTA), "--live"])
            fetch.assert_not_called()
            self.assertEqual(result, 3)

    def test_cli_saved_journal_does_not_use_network_and_persists_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            (root / "journal").mkdir()
            (root / "selected.json").write_text(json.dumps({"encounters": [
                {"encounter_id": 15, "instance_id": 20, "kind": "raid"}]}))
            (root / "journal" / "encounter_15.json").write_text(
                json.dumps({"id": 15, "items": [{"item": {"id": 271874}}]}))
            out = root / "report.json"
            with mock.patch.object(discovery.urllib.request, "urlopen") as fetch:
                code = discovery.main(["--encounters", str(root / "selected.json"),
                      "--journal-dir", str(root / "journal"), "--out", str(out)])
                fetch.assert_not_called()
            self.assertEqual(code, 0)
            report = json.loads(out.read_text())
            self.assertEqual(report["provider"]["matched_existing_ids"], 1)
            self.assertEqual(report["source_mode"],
                             "saved_blizzard_json_unverified_provenance")
            self.assertEqual(report["blizzard_requests"], 0)

if __name__ == "__main__":
    unittest.main()
