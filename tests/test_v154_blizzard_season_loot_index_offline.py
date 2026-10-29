"""Provider-only encounter collection from an empty starting state (no Native)."""
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))
import v154_blizzard_season_loot_index as discovery

class BlizzardSourceFirstOffline(unittest.TestCase):
    def test_api_only_item_discovery_dedup_and_unknown(self):
        rows=discovery.selected_encounters({"encounters": [
            {"encounter_id":101,"instance_id":10,"kind":"raid"},
            {"encounter_id":102,"instance_id":20,"kind":"mplus"},
            {"encounter_id":103,"instance_id":30,"kind":"delve"}]})
        docs={
            101:{"id":101,"items":[{"item":{"id":777777}},
                                    {"item":{"id":888888}},
                                    {"item":{"id":777777}}]},
            102:{"id":102,"items":[{"item":{"id":888888}},
                                    {"item":{"id":999999}}]},
            103:{"id":103,"name":"Encounter with no exposed loot"}}
        data=discovery.collect(rows,docs)
        self.assertEqual(data["unique_item_ids"],[777777,888888,999999])
        self.assertEqual(data["encounters_missing_loot_field"],[103])
        self.assertEqual(data["items"][1]["source_encounter_ids"],[101,102])
        self.assertFalse(data["legacy_item_data_used"])
        self.assertFalse(data["season_complete"])
        self.assertEqual(data["simc_native_calls"],0)
        self.assertNotIn("reference",json.dumps(data))

    def test_empty_explicit_loot_is_not_missing_field(self):
        rows=discovery.selected_encounters({"encounters":[
            {"encounter_id":7,"instance_id":8,"kind":"raid"}]})
        d=discovery.collect(rows,{7:{"id":7,"items":[]}})
        self.assertEqual(d["unique_item_ids"],[])
        self.assertEqual(d["encounters_missing_loot_field"],[])
        self.assertEqual(d["encounter_sources"][0]["loot_state"],"EXPLICIT_API_LIST")
        self.assertIsNone(discovery.encounter_loot({"id":7,"spells":[]},7))

    def test_items_are_not_spell_or_boss_ids(self):
        for bad in ({"id":7,"items":[{"spell":{"id":888888}}]},
                    {"id":7,"items":[{"id":"888888"}]},
                    {"id":7,"loot":[{"item":{"id":0}}]},
                    {"id":7,"items":[],"loot":[]},
                    {"id":8,"items":[{"id":777777}]}):
            with self.subTest(doc=bad),self.assertRaises(discovery.LootBlocked):
                discovery.encounter_loot(bad,7)

    def test_source_scope_rejects_oversized_and_duplicated_enounters(self):
        with self.assertRaises(discovery.LootBlocked):
            discovery.selected_encounters({"encounters":[]})
        with self.assertRaises(discovery.LootBlocked):
            discovery.selected_encounters({"encounters":[
                {"encounter_id":i+1,"instance_id":9,"kind":"raid"}
                for i in range(49)]})
        with self.assertRaises(discovery.LootBlocked):
            discovery.selected_encounters({"encounters":[
                {"encounter_id":1,"instance_id":5,"kind":"raid"},
                {"encounter_id":1,"instance_id":6,"kind":"mplus"}]})
        with self.assertRaises(discovery.LootBlocked):
            discovery.fetch_encounter(1234,"token","invalid")

    def test_saved_provider_json_without_any_prior_db(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            (root/"responses").mkdir()
            (root/"encounters.json").write_text(json.dumps({"encounters":[
                {"encounter_id":11,"instance_id":10,"kind":"raid"}]}))
            (root/"responses"/"encounter_11.json").write_text(
                json.dumps({"id":11,"items":[{"item":{"id":123456}}]}))
            out=root/"fresh.json"
            with mock.patch.object(discovery.api,"request_json") as remote:
                exitcode=discovery.main(["--encounters",str(root/"encounters.json"),
                    "--journal-dir",str(root/"responses"),"--out",str(out)])
                remote.assert_not_called()
            self.assertEqual(exitcode,0)
            self.assertEqual(json.loads(out.read_text())["unique_item_ids"],
                             [123456])
            self.assertEqual(json.loads(out.read_text())["source_authority"],
                             "UNVERIFIED_SAVED_INPUT")

    def test_no_legacy_reference_cli_parameters(self):
        with self.assertRaises(SystemExit):
            discovery.main(["--master","obsolete.json"])

if __name__=="__main__":
    unittest.main()
