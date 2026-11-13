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
        # A missing/zero selected season must never certify an unscoped row.
        with self.assertRaisesRegex(
                v163.JoinBlocked,'DB2_DISPLAY_SEASON_NOT_POSITIVE'):
            v163.classify_era(0,0,0)

    def test_display_season_source_must_be_explicit_and_nonnegative(self):
        self.assertEqual(v163.exact_display_season_id('0'),0)
        self.assertEqual(v163.exact_display_season_id('37'),37)
        for invalid in ('', ' ', 'garbage', '-1', '0.0',
                        '0x0', None, 0, '1'*13):
            with self.subTest(value=invalid):
                with self.assertRaisesRegex(
                        v163.JoinBlocked,'DB2_DISPLAY_SEASON_SOURCE_INVALID'):
                    v163.exact_display_season_id(invalid)

    def test_world_state_expression_source_must_not_fallback_to_zero(self):
        self.assertEqual(v163.exact_world_state_expression_id('0'),0)
        self.assertEqual(v163.exact_world_state_expression_id('52104'),52104)
        for invalid in ('', ' ', 'not-a-number', '-1', '0.0',
                        '0x0', None, 0, '1'*13):
            with self.subTest(value=invalid):
                with self.assertRaisesRegex(v163.JoinBlocked,
                        'JOURNAL_WORLD_STATE_EXPRESSION_SOURCE_INVALID'):
                    v163.exact_world_state_expression_id(invalid)
        self.assertEqual(v163.classify_era(37,52104,37),
                         'UNKNOWN_WORLD_STATE_EXPRESSION')

    def test_no_ambiguous_prefix_match(self):
        rows=[{'Name_lang':"Nek'zali"},{'Name_lang':'Nek'}]
        self.assertEqual(v163.uniquely_match("Nek'zali the Soulcoiler",rows,'Name_lang'),rows[0])
        self.assertIsNone(v163.uniquely_match('same',[{'Name_lang':'same'}, {'Name_lang':'same'}],'Name_lang'))

    def test_condition_scoped_raid_tier_selected_without_numeric_id_guess(self):
        def pair(scoped,archive):
            return [
                {'JournalTierID':str(scoped),'JournalInstanceID':str(i),
                 'AvailabilityCondition':'123456'}
                for i in (110,120,130)]+[
                {'JournalTierID':str(archive),'JournalInstanceID':str(i),
                 'AvailabilityCondition':'0'}
                for i in (110,120,130)]
        ids={110,120,130}
        self.assertEqual(
            v163.resolve_raid_journal_tier(pair(52,8),ids),52)
        # Deliberately reverse numeric ordering; this is source semantics,
        # NOT min/max tier or a fixed 505/516 special case.
        self.assertEqual(
            v163.resolve_raid_journal_tier(pair(3,888),ids),3)
        self.assertEqual(
            v163.resolve_raid_journal_tier(pair(888,3),ids),888)
        self.assertEqual(v163.resolve_raid_journal_tier(
            [{'JournalTierID':'123','JournalInstanceID':'110',
              'AvailabilityCondition':'0'}],{110}),123)
        second=pair(9,10)
        second.extend(pair(11,12)[:3])
        self.assertIsNone(
            v163.resolve_raid_journal_tier(second,ids))
        with_unknown=pair(8,9)
        with_unknown[1]['AvailabilityCondition']='0'
        self.assertIsNone(
            v163.resolve_raid_journal_tier(with_unknown,ids))
        invalid=pair(9,10)
        invalid[0]['AvailabilityCondition']='not-a-number'
        self.assertIsNone(
            v163.resolve_raid_journal_tier(invalid,ids))
        self.assertIsNone(v163.resolve_raid_journal_tier(pair(9,10),set()))

    def test_equipment_expansion_excludes_non_equipment_tokens(self):
        loot={1001,1002,1003}
        items=[{"ID":"1001","ClassID":"4"},
               {"ID":"1002","ClassID":"2"},
               {"ID":"1003","ClassID":"15"}]
        sparse=[{"ID":"1001","ExpansionID":"11"},
                {"ID":"1002","ExpansionID":"11"},
                {"ID":"1003","ExpansionID":"-3"}]
        self.assertEqual(v163.raid_equipment_expansion_id(
            loot,items,sparse),11)
        # If a second *weapon* is from another expansion, no guessing.
        with self.assertRaisesRegex(
            v163.JoinBlocked,"LIVE_RAID_EQUIPMENT_EXPANSION_ID_NOT_UNIQUE"):
            v163.raid_equipment_expansion_id(
                loot,items,[sparse[0],{**sparse[1],"ExpansionID":"12"},
                            sparse[2]])
        for broken in (items[:2],items[1:]):
            with self.assertRaisesRegex(
                v163.JoinBlocked,"LIVE_RAID_LOOT_ITEM_CLASSES_INCOMPLETE"):
                v163.raid_equipment_expansion_id(loot,broken,sparse)
        with self.assertRaisesRegex(
            v163.JoinBlocked,"LIVE_RAID_EQUIPMENT_EXPANSION_ID_NOT_UNIQUE"):
            v163.raid_equipment_expansion_id(loot,items,sparse[:1])
        with self.assertRaisesRegex(
            v163.JoinBlocked,"LIVE_RAID_EQUIPMENT_LOOT_NOT_FOUND"):
            v163.raid_equipment_expansion_id(
                {1003},[items[2]],[sparse[2]])

    def test_tiny_end_to_end_snapshot_and_season_join(self):
        rows = {
            'JournalTierXInstance':[
                {'ID':'1','JournalTierID':'505','JournalInstanceID':'1','AvailabilityCondition':'123456'},
                {'ID':'2','JournalTierID':'516','JournalInstanceID':'1','AvailabilityCondition':'0'}],
            'JournalInstance':[{'ID':'1','Name_lang':'Test Raid','MapID':'100'}, {'ID':'2','Name_lang':'Test Dungeon','MapID':'200'}],
            'JournalEncounter':[{'ID':'11','JournalInstanceID':'1','Name_lang':'Hydra'}, {'ID':'22','JournalInstanceID':'2','Name_lang':'Dungeon Boss'}],
            'JournalEncounterItem':[{'ID':'1','JournalEncounterID':'11','ItemID':'1001','DisplaySeasonID':'0','WorldStateExpressionID':'0'}, {'ID':'2','JournalEncounterID':'22','ItemID':'2001','DisplaySeasonID':'37','WorldStateExpressionID':'52104'}, {'ID':'3','JournalEncounterID':'22','ItemID':'2002','DisplaySeasonID':'37','WorldStateExpressionID':'0'},
                                    {'ID':'4','JournalEncounterID':'11','ItemID':'4001','DisplaySeasonID':'0','WorldStateExpressionID':'0'}],
            'MythicPlusSeasonTrackedMap':[{'ID':'1','MapChallengeModeID':'9','DisplaySeasonID':'37'}],
            'MapChallengeMode':[{'ID':'9','Name_lang':'Test Dungeon','MapID':'200'}],
            'Map':[{'ID':'100','MapName_lang':'Test Raid'}, {'ID':'200','MapName_lang':'Test Dungeon'}],
            'CraftingData':[{'ID':'1','CraftedItemID':'3001'}],
            'ItemSparse':[{'ID':str(i),'Display_lang':str(i),'ExpansionID':'11','OverallQualityID':'4','LimitCategory':'0', 'StatModifier_bonusStat_0':'24' if i==3001 else '0', 'StatModifier_bonusStat_1':'25' if i==3001 else '0',
                           'ItemLevel':'219' if i==4001 else '197'} for i in [1001,2001,2002,3001,4001]],
            'Item':[{'ID':str(i),'ClassID':'15' if i==4001 else '4',
                     'InventoryType':'0' if i==4001 else '5'}
                    for i in [1001,2001,2002,3001,4001]],
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
            self.assertEqual(len(result['raid_non_equipment_loot_candidates']),1)
            token=result['raid_non_equipment_loot_candidates'][0]
            self.assertEqual(token['item_id'],4001)
            self.assertEqual(token['item_class_id'],15)
            self.assertEqual(token['observed_base_item_level'],219)
            self.assertEqual(token['acquisition_sources'][0]['source'],'raid_journal')
            self.assertFalse(result['raid_non_equipment_tier_tokens_verified'])
            self.assertFalse(result['raid_non_equipment_in_user_gear_catalog'])
            self.assertTrue(all(item['item_id']!=4001 for item in result['items']))
            self.assertEqual(result['db2_display_season_id'],37)
            self.assertEqual(result['blizzard_keystone_season_id'],18)
            self.assertTrue(result['unverified_world_state_expressions'])
            self.assertIn('UNKNOWN_WORLD_STATE_EXPRESSION',[x['season_evidence'] for i in result['items'] for x in i['acquisition_sources'] if x['source']=='mplus_journal'])
            self.assertEqual(result['simc_native_calls'],0)
            scope=v163.discover_unique_live_scope(folder,season_report)
            self.assertEqual(scope["raid_zone"],"Test Raid")
            self.assertEqual(scope["mplus_zone"],"Mythic+ S2")
            self.assertEqual(scope["expansion_id"],11)
            self.assertEqual(scope["db2_display_season_id"],37)
            self.assertFalse(scope["season_membership_completely_verified"])
            # A1: source-driven expansion IDs, not a named Midnight pick.
            # Current and legacy zones may be simultaneously non-frozen.
            # The raid must belong to the same *WCL* expansion as the
            # DB2-matched Mythic+ source; that WCL ID is not ItemSparse ID.
            dynamic=json.loads(json.dumps(season_report))
            old=dynamic["wcl"].pop("midnight_zones")
            dynamic["wcl"]["zones"]=[
                {**row,"expansion_id":807} for row in old]+[
                {"zone_name":"Test Raid","zone_id":1900,
                 "wcl_frozen":False,"expansion_id":99,
                 "encounters":[{"name":"Hydra"}]}]
            dynamic_scope=v163.discover_unique_live_scope(folder,dynamic)
            self.assertEqual(dynamic_scope["wcl_expansion_id"],807)
            self.assertEqual(dynamic_scope["expansion_id"],11)
            self.assertEqual(dynamic_scope["db2_display_season_id"],37)
            self.assertFalse(
                dynamic_scope["season_membership_completely_verified"])
            current=v163.build_index(folder,dynamic,raid_zone="Test Raid",
                mplus_zone="Mythic+ S2",build="12.1.5.70575",
                expansion_id=11,wcl_expansion_id=807)
            self.assertEqual(current["db2_display_season_id"],37)
            # Cross-expansion raid cannot complete a current-season pair.
            cross=json.loads(json.dumps(dynamic))
            cross["wcl"]["zones"]=[
                row for row in cross["wcl"]["zones"]
                if not (row["expansion_id"]==807 and
                        row["zone_name"]=="Test Raid")]
            with self.assertRaisesRegex(
                    v163.JoinBlocked,"LIVE_RAID_ZONE_OR_TIER_AMBIGUOUS"):
                v163.discover_unique_live_scope(folder,cross)
            # New all-expansion source MUST preserve expansion IDs; a
            # malformed provider response cannot be relabelled as legacy.
            invalid=json.loads(json.dumps(dynamic))
            del invalid["wcl"]["zones"][0]["expansion_id"]
            with self.assertRaisesRegex(
                    v163.JoinBlocked,"WCL_ALL_EXPANSION_SOURCE_INVALID"):
                v163.discover_unique_live_scope(folder,invalid)
            duplicated=json.loads(json.dumps(season_report))
            duplicated["wcl"]["midnight_zones"].append(
                dict(duplicated["wcl"]["midnight_zones"][0],zone_id=12))
            with self.assertRaisesRegex(
                    v163.JoinBlocked,"LIVE_RAID_ZONE_OR_TIER_AMBIGUOUS"):
                v163.discover_unique_live_scope(folder,duplicated)

            # Real same-build CSV join, including receipt hash updates:
            # no opaque condition -> diagnostic False, not season approval.
            journal=folder/'JournalEncounterItem.csv'
            original=journal.read_text(encoding='utf8')
            self.assertIn('2001,37,52104',original)
            no_conditional=original.replace('2001,37,52104','2001,37,0')
            journal.write_text(no_conditional,encoding='utf8')
            raw=journal.read_bytes()
            receipt['tables']['JournalEncounterItem']={
                'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
            (folder/'receipt.json').write_text(json.dumps(receipt))
            clean=v163.build_index(folder,season_report,
                raid_zone='Test Raid',mplus_zone='Mythic+ S2',
                build='12.1.5.70575',expansion_id=11)
            self.assertFalse(clean['unverified_world_state_expressions'])
            self.assertFalse(clean['full_season_completeness_confirmed'])

            # An otherwise perfectly name-matched DB2 season 0 was
            # previously accepted as the unique season, which could label
            # unscoped journal loot DB2_DISPLAY_SEASON_MATCH.
            tracked=folder/'MythicPlusSeasonTrackedMap.csv'
            tracked_text=tracked.read_text(encoding='utf8')
            self.assertIn('1,9,37',tracked_text)
            for bogus, code in (('0','DB2_DISPLAY_SEASON_NOT_UNIQUE'),
                                ('bogus','DB2_DISPLAY_SEASON_SOURCE_INVALID')):
                tracked.write_text(
                    tracked_text.replace('1,9,37','1,9,'+bogus),encoding='utf8')
                raw=tracked.read_bytes()
                receipt['tables']['MythicPlusSeasonTrackedMap']={
                    'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
                (folder/'receipt.json').write_text(json.dumps(receipt))
                with self.subTest(season=bogus):
                    with self.assertRaisesRegex(v163.JoinBlocked,code):
                        v163.build_index(folder,season_report,
                            raid_zone='Test Raid',mplus_zone='Mythic+ S2',
                            build='12.1.5.70575',expansion_id=11)
            tracked.write_text(tracked_text,encoding='utf8')
            raw=tracked.read_bytes()
            receipt['tables']['MythicPlusSeasonTrackedMap']={
                'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
            (folder/'receipt.json').write_text(json.dumps(receipt))

            # Malformed journal DisplaySeasonID must never fall back to 0.
            journal.write_text(no_conditional.replace('2002,37,0',
                              '2002,invalid,0'),encoding='utf8')
            raw=journal.read_bytes()
            receipt['tables']['JournalEncounterItem']={
                'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
            (folder/'receipt.json').write_text(json.dumps(receipt))
            with self.assertRaisesRegex(
                    v163.JoinBlocked,'DB2_DISPLAY_SEASON_SOURCE_INVALID'):
                v163.build_index(folder,season_report,
                    raid_zone='Test Raid',mplus_zone='Mythic+ S2',
                    build='12.1.5.70575',expansion_id=11)

            journal.write_text(no_conditional,encoding='utf8')
            raw=journal.read_bytes()
            receipt['tables']['JournalEncounterItem']={
                'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
            (folder/'receipt.json').write_text(json.dumps(receipt))

            broken=no_conditional.replace('2002,37,0',
                                          '2002,37,not-a-number')
            self.assertNotEqual(broken,no_conditional)
            journal.write_text(broken,encoding='utf8')
            raw=journal.read_bytes()
            receipt['tables']['JournalEncounterItem']={
                'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
            (folder/'receipt.json').write_text(json.dumps(receipt))
            with self.assertRaisesRegex(v163.JoinBlocked,
                    'JOURNAL_WORLD_STATE_EXPRESSION_SOURCE_INVALID'):
                v163.build_index(folder,season_report,
                    raid_zone='Test Raid',mplus_zone='Mythic+ S2',
                    build='12.1.5.70575',expansion_id=11)

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
