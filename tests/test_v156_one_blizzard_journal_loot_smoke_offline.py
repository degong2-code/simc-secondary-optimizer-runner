"""Offline validation for one real Blizzard journal raid-boss smoke."""
import json
import pathlib,sys,unittest
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v156_one_blizzard_journal_loot_smoke as smoke

class JournalLootSmokeOffline(unittest.TestCase):
    def test_unique_named_does_not_guess_an_ambiguous_id(self):
        self.assertEqual(smoke.unique_named([{"id":23,"name":"Example"}],
                                           "example","INSTANCE"),23)
        for rows in ([],[{"id":2,"name":"X"},{"id":3,"name":"X"}]):
            with self.assertRaises(smoke.api.ProbeBlocked):
                smoke.unique_named(rows,"X","INSTANCE")

    def test_mock_journal_one_boss_and_metadata_reconciliation(self):
        class Resp:
            status=200
            def __init__(self,obj):self.payload=json.dumps(obj).encode()
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):return self.payload
        requests=[]
        def transport(req,timeout):
            requests.append(req.full_url)
            if req.full_url.endswith("/token"):
                return Resp({"access_token":"DUMMY_SECRET_NOT_OUTPUT"})
            if "journal-instance/index" in req.full_url:
                return Resp({"instances":[{"id":1234,
                         "name":"The Venomous Abyss"}]})
            if "journal-instance/1234" in req.full_url:
                return Resp({"id":1234,"encounters":[{"id":999,"name":"Kith'ix"}]})
            if "journal-encounter/999" in req.full_url:
                return Resp({"id":999,"items":[
                    {"item":{"id":281235}},
                    {"item":{"id":271874}},
                    {"item":{"id":987654}}]})
            raise AssertionError("UNEXPECTED_TEST_ENDPOINT")
        data=smoke.run_probe("client","secret",transport=transport)
        self.assertEqual(data["blizzard_game_data_requests"],3)
        self.assertEqual(data["loot"]["observed_unique_ids"],3)
        self.assertEqual(data["loot"]["existing_reference_matches"],
                         [271874,281235])
        self.assertEqual(data["loot"]["existing_effect_hint_matches"],
                         [271874])
        self.assertEqual(data["loot"]["existing_delta_special_armor_matches"],
                         [281235])
        self.assertFalse(data["season_complete"])
        self.assertNotIn("DUMMY_SECRET_NOT_OUTPUT",json.dumps(data))
        self.assertEqual(len(requests),4)

    def test_no_loot_field_is_unknown_not_zero(self):
        ref=smoke.existing.existing_reference(
             smoke.existing.read_json(smoke.existing.MASTER),
             smoke.existing.read_json(smoke.existing.DELTA))
        data=smoke.summarize_loot({"id":777,"spells":[{"id":123}]},777,ref)
        self.assertEqual(data["status"],"LOOT_FIELD_MISSING_UNKNOWN")
        self.assertIsNone(data["observed_item_ids"])
        self.assertIsNone(data["existing_reference_matches"])

if __name__=="__main__":
    unittest.main()
