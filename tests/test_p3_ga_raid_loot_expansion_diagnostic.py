"""P3-GA: mixed raid non-equipment must not guess expansion ownership."""
import unittest
from integration_probes.p3_ga_raid_loot_expansion_diagnostic import summarize_raid_loot

class LootExpansionObservation(unittest.TestCase):
    def setUp(self):
        self.e=[{"ID":"10","JournalInstanceID":"1317"},
                {"ID":"11","JournalInstanceID":"1320"},
                {"ID":"12","JournalInstanceID":"1324"}]
        self.loot=[{"JournalEncounterID":"10","ItemID":"101"},
                   {"JournalEncounterID":"10","ItemID":"102"},
                   {"JournalEncounterID":"11","ItemID":"103"},
                   {"JournalEncounterID":"12","ItemID":"104"}]
        self.item=[{"ID":"101","ClassID":"4"},
                   {"ID":"102","ClassID":"0"},
                   {"ID":"103","ClassID":"2"},
                   {"ID":"104","ClassID":"7"}]
        self.sparse=[{"ID":"101","ExpansionID":"12"},
                     {"ID":"102","ExpansionID":"11"},
                     {"ID":"103","ExpansionID":"12"},
                     {"ID":"104","ExpansionID":"0"}]

    def test_non_equipment_legacy_expansion_does_not_infer_season_but_classifies(self):
        x=summarize_raid_loot(self.e,self.loot,self.item,self.sparse)
        self.assertEqual(x["expansion_by_item_class_counts"]["equipment"],{"12":2})
        self.assertEqual(x["expansion_by_item_class_counts"]["non_equipment"],
                         {"11":1,"0":1})
        self.assertTrue(x["unique_equipment_expansion_observed_source_only"])
        self.assertFalse(x["environment_ready"])
        self.assertEqual(x["native_calls"],0)

    def test_multiple_equipment_expansions_not_selected(self):
        self.sparse[-2]["ExpansionID"]="11"
        x=summarize_raid_loot(self.e,self.loot,self.item,self.sparse)
        self.assertEqual(x["equipment_expansion_candidate_count"],2)
        self.assertFalse(x["unique_equipment_expansion_observed_source_only"])

    def test_missing_sparse_row_blocks_unique_source_claim(self):
        x=summarize_raid_loot(self.e,self.loot,self.item,self.sparse[:2])
        self.assertEqual(x["missing_count"]["ItemSparse"],2)
        self.assertFalse(x["unique_equipment_expansion_observed_source_only"])

    def test_not_part_of_proven_raid_instances_excluded(self):
        x=summarize_raid_loot(
            self.e+[{"ID":"100","JournalInstanceID":"2222"}],
            self.loot+[{"JournalEncounterID":"100","ItemID":"999"}],
            self.item+[{"ID":"999","ClassID":"4"}],
            self.sparse+[{"ID":"999","ExpansionID":"13"}])
        self.assertEqual(x["raid_loot_item_count"],4)
        self.assertNotIn(13,x["candidate_equipment_expansion_ids_source_only"])

if __name__=="__main__":
    unittest.main()
