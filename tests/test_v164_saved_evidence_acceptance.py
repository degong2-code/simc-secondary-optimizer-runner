"""No-network v164 composition and failure boundaries."""
import copy
import unittest
from runner import v164_saved_evidence_season_acceptance as v164


def example():
    season = {"schema":"v155_season_discovery_provider_probe_v1",
        "mode":"LIVE_AUTHENTICATED_BOUNDED",
        "blizzard":{"endpoints":{"keystone_season_index":{"data":{"current_season_id":18}}}}}
    db2 = {"schema":"v163_zero_seed_db2_join_v1",
        "source_provider":"WAGO_TOOLS_PINNED_DB2_WCL_LIVE",
        "build":"12.1.5.70575","db2_expansion_id":11,
        "db2_display_season_id":37,
        "mapped_raid_bosses":1,"wcl_raid_bosses":1,
        "mapped_mplus_dungeons":1,"wcl_mplus_dungeons":1,
        "old_item_catalog_imported":False,
        "full_season_completeness_confirmed":False,
        "simc_native_calls":0,
        "collection_counts":{"raid_journal":1,"mplus_journal":1,"selectable_stat_craft":0},
        "items":[{"item_id":1001,"name":"Sample 1","slot":5,
                  "acquisition_sources":[{"source":"raid_journal",
                  "journal_encounter_id":77,"journal_instance_id":88,
                  "season_evidence":"UNKNOWN_UNSCOPED_JOURNAL",
                  "world_state_expression_id":0}]},
                 {"item_id":1002,"name":"Sample 2","slot":12,
                  "acquisition_sources":[{"source":"mplus_journal",
                  "journal_encounter_id":79,"journal_instance_id":90,
                  "season_evidence":"UNKNOWN_WORLD_STATE_EXPRESSION",
                  "world_state_expression_id":52104}]}],
        "unknown":[{"kind":"raid_tier_not_unique","candidates":[505,516]}]}
    delve = {"schema":"v162_localbots_delve_source_v1",
        "source_provider":"Localbots / balovich-matje/localbots",
        "source_url":"https://raw.githubusercontent.com/balovich-matje/localbots/main/data/delve-loot.json",
        "db2_build":"12.1.5.70575","db2_expansion_id":11,
        "prior_wequip_or_past_item_db_used":False,
        "items":[{"item_id":1002,"name":"Delve Duplicate",
                 "resolution":"LOCALBOTS_EXPLICIT_ID_DB2_VERIFIED"},
                 {"item_id":1003,"name":"Delve New",
                 "resolution":"LOCALBOTS_NAME_DB2_RESOLVED"}],
        "resolved_count":2,"unresolved_count":0,
        "unresolved":[],"names_in_source":2}
    return season,db2,delve


class AcceptanceTests(unittest.TestCase):
    def test_composition_dedup_and_unknown_preserved(self):
        index, receipt=v164.compose(*example())
        self.assertEqual(index["item_ids"],[1001,1002,1003])
        self.assertEqual(receipt["cross_source_overlap_ids"],1)
        self.assertEqual(receipt["source_unique_item_ids"],
                         {"wago_db2":2,"localbots_delve":2})
        self.assertEqual(index["simc_native_calls"],0)
        self.assertFalse(index["full_season_completeness_confirmed"])
        self.assertEqual(len(index["items"][1]["acquisition_sources"]),2)
        self.assertEqual(receipt["db2_season_evidence_records"]["UNKNOWN_WORLD_STATE_EXPRESSION"],1)
        self.assertEqual(receipt["new_api_calls"],0)
        self.assertEqual(receipt["blizzard_keystone_season_id"],18)
        self.assertEqual(receipt["db2_display_season_id"],37)

    def test_not_fixed_to_historical_79(self):
        a,b,c=example()
        c["items"]=c["items"][:1]
        c["resolved_count"]=1
        c["names_in_source"]=1
        index,receipt=v164.compose(a,b,c)
        self.assertEqual(receipt["integrated_unique_item_ids"],2)
        self.assertEqual(index["item_ids"],[1001,1002])

    def test_build_expansion_and_mapping_blocks(self):
        for key,value in (("db2_build","12.1.5.70576"),("db2_expansion_id",12)):
            a,b,c=example();c[key]=value
            with self.assertRaises(v164.AcceptanceBlocked):
                v164.compose(a,b,c)
        a,b,c=example();b["mapped_raid_bosses"]=0
        with self.assertRaises(v164.AcceptanceBlocked):
            v164.compose(a,b,c)

    def test_duplicate_db2_id_row_blocks(self):
        a,b,c=example()
        b["items"].append(copy.deepcopy(b["items"][0]))
        with self.assertRaises(v164.AcceptanceBlocked):
            v164.compose(a,b,c)

    def test_untrusted_or_partial_season_receipt_blocks(self):
        a,b,c=example();a["mode"]="OFFLINE_FIXTURE"
        with self.assertRaises(v164.AcceptanceBlocked):
            v164.compose(a,b,c)


if __name__ == "__main__":unittest.main()
