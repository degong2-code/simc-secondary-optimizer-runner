"""v163->v158 bridge: synthetic offline regression, optionally actual saved reports."""
import json
import os
from pathlib import Path
import unittest
from runner import v158_source_first_season_catalog as catalog


def wago_report():
    return {
        'schema':'v163_zero_seed_db2_join_v1',
        'source_provider':'WAGO_TOOLS_PINNED_DB2_WCL_LIVE',
        'status':'SOURCE_CANDIDATES_WITH_UNRESOLVED_SEASON_CONDITIONS',
        'old_item_catalog_imported':False,
        'full_season_completeness_confirmed':False,
        'simc_native_calls':0,
        'build':'12.1.5.70575',
        'db2_expansion_id':11,
        'db2_display_season_id':37,
        'mapped_raid_bosses':1,
        'mapped_mplus_dungeons':1,
        'collection_counts':{'raid_journal':1,'mplus_journal':1,'selectable_stat_craft':0},
        'items':[{
            'item_id':12345,'name':'A','slot':5,
            'acquisition_sources':[{'source':'raid_journal',
                                    'season_evidence':'UNKNOWN_UNSCOPED_JOURNAL',
                                    'journal_encounter_id':77,'journal_instance_id':88,
                                    'world_state_expression_id':0}]
        },{
            'item_id':12346,'name':'B','slot':12,
            'acquisition_sources':[{'source':'mplus_journal',
                                    'season_evidence':'UNKNOWN_WORLD_STATE_EXPRESSION',
                                    'journal_encounter_id':79,'journal_instance_id':90,
                                    'world_state_expression_id':52104}]
        }],
        'unknown':[{'kind':'raid_tier_not_unique','candidates':[505,516]}]
    }


def localbots_report():
    return {
        'schema':'v162_localbots_delve_source_v1',
        'source_provider':'Localbots / balovich-matje/localbots',
        'source_url':'https://raw.githubusercontent.com/balovich-matje/localbots/main/data/delve-loot.json',
        'prior_wequip_or_past_item_db_used':False,
        'source_content_sha256':'synthetic',
        'db2_build':'12.1.5.70575',
        'names_in_source':1,
        'items':[{'item_id':12347,'name':'C','resolution':'LOCALBOTS_NAME_DB2_RESOLVED'}],
        'unresolved':[],'resolved_count':1,'unresolved_count':0
    }


class BridgeTests(unittest.TestCase):
    def test_shared_index_keeps_unknown_season_provenance(self):
        index=catalog.ingest([wago_report(),localbots_report()])
        self.assertEqual(index['observed_unique_item_ids'],3)
        self.assertFalse(index['full_season_completeness_confirmed'])
        self.assertFalse(index['old_item_catalog_imported'])
        self.assertEqual(index['simc_native_calls'],0)
        self.assertEqual(index['season_data']['wago_db2_display_season_id'],37)
        rows={row['item_id']:row for row in index['items']}
        self.assertEqual(rows[12346]['acquisition_sources'][0]['season_evidence'],
                         'UNKNOWN_WORLD_STATE_EXPRESSION')
        self.assertEqual(rows[12347]['acquisition_sources'][0]['kind'],'delve')
        self.assertEqual(len(index['unresolved_provider_fields']),1)

    def test_cross_source_build_mismatch_blocks(self):
        lb=localbots_report()
        lb['db2_build']='12.1.5.70576'
        with self.assertRaises(catalog.CatalogBlocked):
            catalog.ingest([wago_report(),lb])

    def test_real_reports_when_supplied(self):
        p=os.getenv('SIMC_V163_JOIN_REPORT')
        q=os.getenv('SIMC_V162_REPORT')
        if not (p and q):self.skipTest('real prior reports not mounted in CI')
        index=catalog.ingest([json.loads(Path(p).read_text()),
                              json.loads(Path(q).read_text())])
        self.assertTrue(index['observed_unique_item_ids']>=79)
        self.assertTrue(any(x['type']=='localbots_delve_pool' for x in index['collection_receipts']))
        self.assertTrue(any(x['type']=='wago_db2_source_first_candidates' for x in index['collection_receipts']))
        self.assertEqual(index['simc_native_calls'],0)


if __name__=='__main__': unittest.main()
