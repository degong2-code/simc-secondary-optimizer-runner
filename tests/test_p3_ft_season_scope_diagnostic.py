"""Offline-only diagnostic projection. No public HTTP, credentials or Native."""
import unittest
from integration_probes import p3_ft_season_scope_diagnostic as scope


class CurrentSeasonRaidCandidateDiagnostic(unittest.TestCase):
    def test_multiple_complete_same_tier_zones_are_reported_not_chosen(self):
        report={"wcl":{"midnight_zones":[
            {"zone_id":11,"zone_name":"Raid Alpha","wcl_frozen":False,
             "encounters":[{"name":"Alpha Boss"}]},
            {"zone_id":12,"zone_name":"Raid Beta","wcl_frozen":False,
             "encounters":[{"name":"Beta Boss"}]},
            {"zone_id":30,"zone_name":"Dungeon Rotation","wcl_frozen":False,
             "encounters":[{"name":"Dungeon Boss"}]}]}}
        journal=[
            {"Name_lang":"Alpha Boss","JournalInstanceID":"111"},
            {"Name_lang":"Beta Boss","JournalInstanceID":"112"},
            {"Name_lang":"Dungeon Boss","JournalInstanceID":"113"}]
        tiers=[
            {"JournalTierID":"5","JournalInstanceID":"111"},
            {"JournalTierID":"5","JournalInstanceID":"112"},
            {"JournalTierID":"5","JournalInstanceID":"113"}]
        rows=scope.raid_candidates(
            report,journal,tiers,mplus_zone_id=30)
        eligible=[r for r in rows
                  if r["qualified_by_original_raid_rule"]]
        self.assertEqual(len(eligible),2)
        self.assertEqual({r["zone_name"] for r in eligible},
                         {"Raid Alpha","Raid Beta"})
        self.assertEqual([r["matching_raid_tier_ids"] for r in eligible],
                         [[5],[5]])
        self.assertFalse(rows[2]["qualified_by_original_raid_rule"])
        self.assertTrue(all(r["fully_matched_to_journal"] for r in rows))

    def test_current_and_catalog_tiers_are_reported_not_guessed(self):
        raids=[{
            "zone_id":53,"fully_matched_to_journal":True,
            "matching_raid_tier_ids":[505,516],
            "journal_instance_ids":[1317,1320,1324]}]
        tiers=[
            {"ID":"505","Name_lang":"Current Season","Flags":"1"},
            {"ID":"516","Name_lang":"Midnight","Flags":"0"},
            {"ID":"999","Name_lang":"Unrelated","Flags":"0"}]
        links=[
            {"JournalTierID":str(t),"JournalInstanceID":str(i),
             "AvailabilityCondition":("149388" if t==505 else "0")}
            for t in (505,516,999) for i in (1317,1320,1324)]
        out=scope.related_journal_tier_sources(
            raids,mplus_zone_id=55,tier_rows=tiers,links=links)
        self.assertEqual([int(r["ID"])
                          for r in out["journal_tier_candidate_rows"]],
                         [505,516])
        self.assertEqual(len(out["matching_raid_tier_link_rows"]),6)
        self.assertEqual({
            (int(row["JournalTierID"]),row["AvailabilityCondition"])
            for row in out["matching_raid_tier_link_rows"]},
            {(505,"149388"),(516,"0")})
        self.assertNotIn("selected_tier",out)
        self.assertNotIn("season_verified",out)

    def test_missing_or_ambiguous_journal_match_never_becomes_candidate(self):
        report={"wcl":{"midnight_zones":[
            {"zone_id":11,"zone_name":"Unmapped","wcl_frozen":False,
             "encounters":[{"name":"Unknown Boss"}]},
            {"zone_id":12,"zone_name":"Duplicate","wcl_frozen":False,
             "encounters":[{"name":"Twin Boss"}]},
            {"zone_id":13,"zone_name":"Frozen","wcl_frozen":True,
             "encounters":[{"name":"Twin Boss"}]}]}}
        journal=[
            {"Name_lang":"Twin Boss","JournalInstanceID":"111"},
            {"Name_lang":"Twin Boss","JournalInstanceID":"112"}]
        tiers=[
            {"JournalTierID":"5","JournalInstanceID":"111"},
            {"JournalTierID":"5","JournalInstanceID":"112"}]
        rows=scope.raid_candidates(report,journal,tiers)
        self.assertEqual(len(rows),2)
        self.assertTrue(all(
            not r["qualified_by_original_raid_rule"] for r in rows))
        self.assertTrue(all(
            not r["fully_matched_to_journal"] for r in rows))


if __name__=="__main__":
    unittest.main()
