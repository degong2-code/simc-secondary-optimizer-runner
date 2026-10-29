"""Focused v163 tests. Fully offline; real v161 snapshot optional for acceptance."""
import importlib.util
import csv
import hashlib
import tempfile
import json
import os
from pathlib import Path
import unittest

MOD = Path(__file__).resolve().parents[1]/'runner'/'v163_zero_seed_db2_join.py'
spec = importlib.util.spec_from_file_location('v163', MOD)
v163 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v163)

class JoinTests(unittest.TestCase):
    def test_opaque_world_state_always_unknown(self):
        self.assertEqual(v163.classify_era(37,52104,37),'UNKNOWN_WORLD_STATE_EXPRESSION')
        self.assertEqual(v163.classify_era(0,0,37),'UNKNOWN_UNSCOPED_JOURNAL')
        self.assertEqual(v163.classify_era(37,0,37),'DB2_DISPLAY_SEASON_MATCH')
        self.assertEqual(v163.classify_era(34,0,37),'UNKNOWN_OTHER_DISPLAY_SEASON')

    def test_no_ambiguous_prefix_match(self):
        rows=[{'Name_lang':"Nek'zali"},{'Name_lang':'Nek'}]
        self.assertEqual(v163.uniquely_match("Nek'zali the Soulcoiler",rows,'Name_lang'),rows[0])
        self.assertIsNone(v163.uniquely_match('same',[{'Name_lang':'same'}, {'Name_lang':'same'}],'Name_lang'))

    def test_tiny_end_to_end_snapshot_and_season_join(self):
        rows = {
            'JournalTierXInstance':[{'ID':'1','JournalTierID':'505','JournalInstanceID':'1','AvailabilityCondition':'0'}],
            'JournalInstance':[{'ID':'1','Name_lang':'Test Raid','MapID':'100'}, {'ID':'2','Name_lang':'Test Dungeon','MapID':'200'}],
            'JournalEncounter':[{'ID':'11','JournalInstanceID':'1','Name_lang':'Hydra'}, {'ID':'22','JournalInstanceID':'2','Name_lang':'Dungeon Boss'}],
            'JournalEncounterItem':[{'ID':'1','JournalEncounterID':'11','ItemID':'1001','DisplaySeasonID':'0','WorldStateExpressionID':'0'}, {'ID':'2','JournalEncounterID':'22','ItemID':'2001','DisplaySeasonID':'37','WorldStateExpressionID':'52104'}, {'ID':'3','JournalEncounterID':'22','ItemID':'2002','DisplaySeasonID':'37','WorldStateExpressionID':'0'}],
            'MythicPlusSeasonTrackedMap':[{'ID':'1','MapChallengeModeID':'9','DisplaySeasonID':'37'}],
            'MapChallengeMode':[{'ID':'9','Name_lang':'Test Dungeon','MapID':'200'}],
            'Map':[{'ID':'100','MapName_lang':'Test Raid'}, {'ID':'200','MapName_lang':'Test Dungeon'}],
            'CraftingData':[{'ID':'1','CraftedItemID':'3001'}],
            'ItemSparse':[{'ID':str(i),'Display_lang':str(i),'ExpansionID':'11','OverallQualityID':'4','LimitCategory':'0', 'StatModifier_bonusStat_0':'24' if i==3001 else '0', 'StatModifier_bonusStat_1':'25' if i==3001 else '0'} for i in [1001,2001,2002,3001]],
            'Item':[{'ID':str(i),'ClassID':'4','InventoryType':'5'} for i in [1001,2001,2002,3001]],
        }
        season_report={'schema':'v155_season_discovery_provider_probe_v1','mode':'LIVE_AUTHENTICATED_BOUNDED','blizzard':{'endpoints':{'keystone_season_index':{'data':{'current_season_id':18}}}},'wcl':{'midnight_zones':[{'zone_name':'Test Raid', 'zone_id':10,'wcl_frozen':False,'encounters':[{'name':'Hydra'}]},{'zone_name':'Mythic+ S2','zone_id':11,'wcl_frozen':False,'encounters':[{'name':'Test Dungeon'}]}]}}
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            receipt={'build':'12.1.5.70575','locale':'enUS','tables':{}}
            for table in v163.TABLES:
                with (folder/(table+'.csv')).open('w',encoding='utf8',newline='') as fp:
                    writer=csv.DictWriter(fp,fieldnames=rows[table][0].keys())
                    writer.writeheader();writer.writerows(rows[table])
                data=(folder/(table+'.csv')).read_bytes()
                receipt['tables'][table]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
            (folder/'receipt.json').write_text(json.dumps(receipt))
            result=v163.build_index(folder, season_report,raid_zone='Test Raid',
                mplus_zone='Mythic+ S2',build='12.1.5.70575',expansion_id=11)
            self.assertEqual(result['collection_counts'],{'raid_journal':1,'mplus_journal':2,'selectable_stat_craft':1})
            self.assertEqual(result['raid_journal_tier_id'],505)
            self.assertEqual(result['db2_display_season_id'],37)
            self.assertEqual(result['blizzard_keystone_season_id'],18)
            self.assertIn('UNKNOWN_WORLD_STATE_EXPRESSION',[x['season_evidence'] for i in result['items'] for x in i['acquisition_sources'] if x['source']=='mplus_journal'])
            self.assertEqual(result['simc_native_calls'],0)

    def test_real_snapshot_when_supplied(self):
        folder=os.environ.get('SIMC_V161_SNAPSHOT_DIR')
        report_path=os.environ.get('SIMC_V155_SEASON_REPORT')
        if not (folder and report_path):self.skipTest('real CSV evidence not mounted in CI')
        result=v163.build_index(Path(folder),json.loads(Path(report_path).read_text()),
            raid_zone='The Venomous Abyss',mplus_zone='Mythic+ Season 2',
            build='12.1.5.70575',expansion_id=11)
        self.assertEqual((result['mapped_raid_bosses'],result['mapped_mplus_dungeons']), (10,8))
        self.assertEqual(result['collection_counts'],{'raid_journal':105,'mplus_journal':223,
            'selectable_stat_craft':106})
        self.assertEqual(result['db2_display_season_id'],37)
        self.assertEqual(result['blizzard_keystone_season_id'],18)
        self.assertTrue(any(s['season_evidence']=='UNKNOWN_WORLD_STATE_EXPRESSION'
             for row in result['items'] for s in row['acquisition_sources']))
        self.assertEqual(result['simc_native_calls'],0)
        self.assertFalse(result['old_item_catalog_imported'])

if __name__=='__main__':unittest.main()
