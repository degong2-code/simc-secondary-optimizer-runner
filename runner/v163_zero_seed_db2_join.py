#!/usr/bin/env python3
"""Offline, zero-seed DB2 CSV join. No API calls, Native SimC or legacy catalog.

Consumes a pinned v161 folder and an actual v155-style Blizzard/WCL discovery
receipt. DisplaySeasonID and Blizzard keystone season ID are distinct namespaces.
Opaque WorldStateExpressionID is NEVER interpreted as a boolean or freshness.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re

SCHEMA = 'v163_zero_seed_db2_join_v1'
TABLES = ('JournalTierXInstance','JournalInstance','JournalEncounter',
          'JournalEncounterItem','MythicPlusSeasonTrackedMap','MapChallengeMode',
          'Map','CraftingData','ItemSparse','Item')
MAX_CSV_BYTES = 210_000_000
MAX_ROWS = 1_000_000

class JoinBlocked(ValueError):
    pass

def fail_if(condition, code):
    if condition:
        raise JoinBlocked(code)

def number(value, default=0):
    try: return int(value)
    except (ValueError, TypeError): return default

def norm(name):
    return re.sub(r'[^a-z0-9]+', '', name.casefold())

def read_rows(folder, table):
    path = folder / (table + '.csv')
    fail_if(not path.is_file() or path.stat().st_size > MAX_CSV_BYTES,
            'CSV_MISSING_OR_TOO_LARGE_' + table)
    with path.open(encoding='utf-8-sig', newline='') as source:
        reader = csv.DictReader(source)
        fail_if(not reader.fieldnames or 'ID' not in reader.fieldnames,
                'CSV_HEADER_INVALID_' + table)
        for i, row in enumerate(reader):
            fail_if(i >= MAX_ROWS, 'CSV_ROW_LIMIT_' + table)
            yield row

def verify_snapshot(folder, build, *, verified_tables=None):
    receipt = json.loads((folder / 'receipt.json').read_text(encoding='utf-8'))
    fail_if(receipt.get('build') != build or receipt.get('locale') != 'enUS'
            or set(receipt.get('tables', {})) != set(TABLES),
            'PINNED_RECEIPT_MISMATCH')
    # Only the normal collector supplies the already SHA-checked v217 table
    # identities. A standalone caller retains the original full-file scan.
    if verified_tables is not None:
        fail_if(type(verified_tables) is not dict or
                set(verified_tables) != set(TABLES),
                'V217_VERIFIED_TABLE_SET_MISMATCH')
    for table in TABLES:
        path = folder / (table+'.csv')
        fail_if(not path.is_file(), 'CSV_MISSING_'+table)
        meta = receipt['tables'][table]
        fail_if(path.stat().st_size != meta.get('bytes'), 'CSV_SIZE_MISMATCH_'+table)
        if verified_tables is None:
            digest = hashlib.sha256()
            with path.open('rb') as f:
                for chunk in iter(lambda: f.read(1024*1024), b''):
                    digest.update(chunk)
            fail_if(digest.hexdigest() != meta.get('sha256'),
                    'CSV_SHA_MISMATCH_'+table)
        else:
            fail_if(verified_tables[table] != {
                'sha256': meta.get('sha256'), 'bytes': meta.get('bytes')},
                'V217_VERIFIED_TABLE_PROVENANCE_MISMATCH_'+table)
    return receipt

def named_zone(report, name):
    zones = (report.get('wcl') or {}).get('midnight_zones') or []
    found = [z for z in zones if norm(z.get('zone_name','')) == norm(name)
             and z.get('wcl_frozen') is False]
    fail_if(len(found) != 1, 'ACTIVE_WCL_ZONE_NOT_UNIQUE_'+name)
    return found[0]

def uniquely_match(name, candidates, key):
    exact = [x for x in candidates if norm(x[key]) == norm(name)]
    if len(exact) == 1: return exact[0]
    if exact: return None
    # WCL can use a longer boss epithet than the client Journal name.
    prefix = [x for x in candidates if len(norm(x[key])) >= 5
              and norm(name).startswith(norm(x[key]))]
    return prefix[0] if len(prefix) == 1 else None

def classify_era(display_season, wse, selected):
    if wse: return 'UNKNOWN_WORLD_STATE_EXPRESSION'
    if display_season == selected: return 'DB2_DISPLAY_SEASON_MATCH'
    if display_season == 0: return 'UNKNOWN_UNSCOPED_JOURNAL'
    return 'UNKNOWN_OTHER_DISPLAY_SEASON'

def resolve_raid_journal_tier(tier_links, required_instances):
    """Resolve overlapping raid tiers by their source conditions.

    For a single authenticated WCL raid, a uniform positive seasonal
    AvailabilityCondition may coexist with unconditional expansion-tier
    entries. Do not infer by tier ID, or treat this as effect or complete
    season attestation. Any other ambiguity remains PENDING.
    """
    needed=set(required_instances)
    if not needed or any(type(i) is not int or i<=0 for i in needed):
        return None
    links=defaultdict(lambda:defaultdict(set))
    for row in tier_links:
        tid=number(row.get("JournalTierID"))
        iid=number(row.get("JournalInstanceID"))
        raw=row.get("AvailabilityCondition")
        # Reject invalid populated condition IDs rather than turning
        # malformed source data into an unconditional catalog.
        if raw not in (None,"") and (
                type(raw) is not str or not raw.isdigit()):
            return None
        if tid>0 and iid>0:
            links[tid][iid].add(number(raw))
    matches=sorted(t for t,rows in links.items() if needed<=set(rows))
    if len(matches)==1:
        return matches[0]
    if not matches:
        return None
    scoped=[]
    for tid in matches:
        all_conditions=[links[tid][iid] for iid in needed]
        if (all(len(c)==1 for c in all_conditions) and
            len(set().union(*all_conditions))==1 and
            next(iter(all_conditions[0]))>0):
            scoped.append(tid)
    if len(scoped)!=1:
        return None
    candidate=scoped[0]
    if any(any(links[t][iid]!={0} for iid in needed)
           for t in matches if t!=candidate):
        return None
    return candidate


def discover_unique_live_scope(folder, report):
    """Derive exact zone, season and expansion IDs from live WCL + DB2.

    Fail closed on ambiguous maps/raid tiers/loot expansions; not a proof
    of global season membership or WorldStateExpression semantics.
    """
    fail_if(report.get("schema") != "v155_season_discovery_provider_probe_v1"
            or report.get("mode") != "LIVE_AUTHENTICATED_BOUNDED",
            "LIVE_SEASON_REPORT_REQUIRED")
    zones=[z for z in (report.get("wcl",{}).get("midnight_zones") or [])
           if z.get("wcl_frozen") is False and z.get("encounters")]
    fail_if(not zones,"LIVE_ACTIVE_WCL_ZONES_NOT_PROVEN")
    challenge={number(x["ID"]):x for x in read_rows(folder,"MapChallengeMode")}
    groups=defaultdict(set)
    for row in read_rows(folder,"MythicPlusSeasonTrackedMap"):
        fail_if(not {"DisplaySeasonID","MapChallengeModeID"}<=set(row),
                "LIVE_MPLUS_DB2_SOURCE_SCHEMA_PENDING")
        sid=number(row["DisplaySeasonID"])
        mode=challenge.get(number(row["MapChallengeModeID"]))
        if sid>0 and mode and mode.get("Name_lang"):
            groups[sid].add(norm(mode["Name_lang"]))
    choices=[(z,sid) for z in zones for sid,names in groups.items()
             if names and {norm(x["name"]) for x in z["encounters"]}==names]
    fail_if(len(choices)!=1,"LIVE_MPLUS_ZONE_OR_DISPLAY_SEASON_AMBIGUOUS")
    mplus,sid=choices[0]
    encounters=list(read_rows(folder,"JournalEncounter"))
    tier_links=list(read_rows(folder,"JournalTierXInstance"))
    raidzones=[]
    for zone in zones:
        if zone["zone_id"]==mplus["zone_id"]:continue
        found=[uniquely_match(e["name"],encounters,"Name_lang")
               for e in zone["encounters"]]
        if not found or any(x is None for x in found):continue
        instances={number(x["JournalInstanceID"]) for x in found}
        tid=resolve_raid_journal_tier(tier_links,instances)
        if tid is not None:
            raidzones.append((zone,found,tid))
    fail_if(len(raidzones)!=1,"LIVE_RAID_ZONE_OR_TIER_AMBIGUOUS")
    raid,found,tid=raidzones[0]
    eids={number(x["ID"]) for x in found}
    loot={number(x["ItemID"]) for x in read_rows(folder,"JournalEncounterItem")
          if number(x["JournalEncounterID"]) in eids
          and number(x["ItemID"])>0}
    fail_if(not loot,"LIVE_RAID_LOOT_IDS_NOT_FOUND")
    seen={number(x["ID"]):number(x["ExpansionID"])
          for x in read_rows(folder,"ItemSparse")
          if number(x["ID"]) in loot}
    exps=set(seen.values())
    fail_if(set(seen)!=loot or len(exps)!=1 or next(iter(exps))<=0,
            "LIVE_RAID_LOOT_EXPANSION_ID_NOT_UNIQUE")
    return {"raid_zone":raid["zone_name"],
            "mplus_zone":mplus["zone_name"],
            "expansion_id":next(iter(exps)),
            "db2_display_season_id":sid,
            "raid_journal_tier_id":tid,
            "source_basis":"LIVE_WCL_ACTIVE_ZONES_AND_SAME_BUILD_DB2",
            "season_membership_completely_verified":False,
            "unknown_world_state_not_promoted":True}


def build_index(folder, report, *, raid_zone, mplus_zone, build,
                expansion_id, verified_tables=None):
    fail_if(report.get('schema') != 'v155_season_discovery_provider_probe_v1'
            or report.get('mode') != 'LIVE_AUTHENTICATED_BOUNDED',
            'LIVE_SEASON_REPORT_REQUIRED')
    receipt = verify_snapshot(folder, build,
                              verified_tables=verified_tables)
    raid = named_zone(report, raid_zone)
    mplus = named_zone(report, mplus_zone)
    fail_if(not raid.get('encounters') or not mplus.get('encounters'),
            'WCL_ENCOUNTERS_EMPTY')
    journal_instances = {number(r['ID']):r for r in read_rows(folder,'JournalInstance')}
    encounters = list(read_rows(folder,'JournalEncounter'))
    mapped_raid, problems = [], []
    for wcl in raid['encounters']:
        match = uniquely_match(wcl['name'], encounters, 'Name_lang')
        if match is None:
            problems.append({'kind':'raid_boss_unmapped','name':wcl['name']})
            continue
        mapped_raid.append((wcl,number(match['ID']), number(match['JournalInstanceID'])))
    tier_links=list(read_rows(folder,'JournalTierXInstance'))
    required_instances={x[2] for x in mapped_raid}
    matching_tiers=sorted({number(x['JournalTierID'])
         for x in tier_links if number(x['JournalTierID'])>0
         and number(x['JournalInstanceID']) in required_instances})
    selected_tier=resolve_raid_journal_tier(
        tier_links,required_instances)
    if selected_tier is None:
        problems.append({'kind':'raid_tier_not_unique',
                         'candidates':matching_tiers})
    challenges = {number(r['ID']):r for r in read_rows(folder,'MapChallengeMode')}
    season_groups = defaultdict(list)
    for r in read_rows(folder,'MythicPlusSeasonTrackedMap'):
        c = challenges.get(number(r['MapChallengeModeID']))
        if c: season_groups[number(r['DisplaySeasonID'])].append(c)
    wcl_mplus_names = {norm(x['name']) for x in mplus['encounters']}
    matching_seasons = [sid for sid,cs in season_groups.items() if
        {norm(x['Name_lang']) for x in cs} == wcl_mplus_names]
    fail_if(len(matching_seasons)!=1, 'DB2_DISPLAY_SEASON_NOT_UNIQUE')
    season_id = matching_seasons[0]
    map_to_instances = defaultdict(list)
    for iid,r in journal_instances.items():map_to_instances[number(r['MapID'])].append(iid)
    mapped_mplus = []
    for wcl in mplus['encounters']:
        challenges_found = [c for c in season_groups[season_id]
                            if norm(c['Name_lang']) == norm(wcl['name'])]
        options = [(c, iid) for c in challenges_found
                   for iid in map_to_instances[number(c['MapID'])]
                   if norm(journal_instances[iid]['Name_lang'])==norm(wcl['name'])]
        if len(options)!=1:
            problems.append({'kind':'mplus_dungeon_unmapped','name':wcl['name']})
            continue
        mapped_mplus.append((wcl, options[0][1], number(options[0][0]['ID'])))
    by_instance = defaultdict(list)
    for r in encounters:by_instance[number(r['JournalInstanceID'])].append(number(r['ID']))
    sources = defaultdict(list)
    raid_by_enc = defaultdict(list)
    for wcl,eid,iid in mapped_raid:
        raid_by_enc[eid].append((wcl,iid))
    mplus_by_enc = defaultdict(list)
    for wcl,iid,cid in mapped_mplus:
        for eid in by_instance[iid]:mplus_by_enc[eid].append((wcl,iid,cid))
    for r in read_rows(folder,'JournalEncounterItem'):
        eid = number(r['JournalEncounterID']); item_id=number(r['ItemID'])
        if item_id<=0 or (eid not in raid_by_enc and eid not in mplus_by_enc):continue
        season = number(r['DisplaySeasonID']); wse=number(r['WorldStateExpressionID'])
        era = classify_era(season,wse,season_id)
        for wcl,iid in raid_by_enc[eid]:
            sources[item_id].append({'source':'raid_journal','name':wcl['name'],
                'journal_encounter_id':eid,'journal_instance_id':iid,
                'display_season_id':season,'world_state_expression_id':wse,
                'season_evidence':era})
        for wcl,iid,cid in mplus_by_enc[eid]:
            sources[item_id].append({'source':'mplus_journal','name':wcl['name'],
                'journal_encounter_id':eid,'journal_instance_id':iid,
                'challenge_mode_id':cid,'display_season_id':season,
                'world_state_expression_id':wse,'season_evidence':era})
    crafted_ids={number(r['CraftedItemID']) for r in read_rows(folder,'CraftingData')
                 if number(r['CraftedItemID'])>0}
    needed=set(sources)|crafted_ids
    items={number(r['ID']):r for r in read_rows(folder,'Item') if number(r['ID']) in needed}
    sparse={number(r['ID']):r for r in read_rows(folder,'ItemSparse') if number(r['ID']) in needed}
    results={}
    raid_non_equipment=[]
    for iid,provenances in sources.items():
        it=items.get(iid);sp=sparse.get(iid)
        if not it or not sp:continue
        item_class=number(it['ClassID'])
        if item_class not in (2,4):
            # The old equipment-only pool filtered raid tokens out. Retain
            # source-backed NON-EQUIPMENT loot only as internal evidence; no
            # claim that every such item is a tier token or current-season gear.
            raid_sources=[p for p in provenances if p['source']=='raid_journal']
            if raid_sources and number(sp.get('ExpansionID'))==expansion_id:
                base_level=number(sp.get('ItemLevel'))
                raid_non_equipment.append({
                    'item_id':iid,'item_class_id':item_class,
                    'observed_base_item_level':base_level if base_level>0 else None,
                    'observed_expansion_id':number(sp['ExpansionID']),
                    'acquisition_sources':sorted(
                        raid_sources,key=lambda p:(p['journal_encounter_id'],
                                                 p['journal_instance_id'])),
                    'classification':'RAID_NON_EQUIPMENT_LOOT_TOKEN_UNVERIFIED'})
            continue
        results[iid]={'item_id':iid,'name':sp['Display_lang'],
            'slot':number(it['InventoryType']),
            'acquisition_sources':sorted({json.dumps(s,sort_keys=True) for s in provenances})}
    for iid in crafted_ids:
        it=items.get(iid);sp=sparse.get(iid)
        if not it or not sp:continue
        stats={number(sp.get(f'StatModifier_bonusStat_{i}')) for i in range(10)}
        if (number(sp['ExpansionID'])!=expansion_id or number(it['ClassID']) not in (2,4)
            or number(sp['OverallQualityID'])<3 or not {24,25}<=stats):continue
        result=results.setdefault(iid,{'item_id':iid,'name':sp['Display_lang'],
            'slot':number(it['InventoryType']),'acquisition_sources':[]})
        result['acquisition_sources'].append(json.dumps({'source':'selectable_stat_craft',
            'expansion_id':expansion_id,'stat_placeholders':[24,25],
            'known_inherent_limit_category':number(sp['LimitCategory']) in (512,697),
            'classification':'PROVISIONAL_SIMC_BATCH_REVIEW'},sort_keys=True))
    for row in results.values():
        row['acquisition_sources']=[json.loads(x) for x in sorted(set(row['acquisition_sources']))]
    counts={t:len({i for i,r in results.items() if any(x['source']==t
            for x in r['acquisition_sources'])})
            for t in ('raid_journal','mplus_journal','selectable_stat_craft')}
    return {'schema':SCHEMA,'source_provider':'WAGO_TOOLS_PINNED_DB2_WCL_LIVE',
        'status':'SOURCE_CANDIDATES_WITH_UNRESOLVED_SEASON_CONDITIONS',
        'build':build,'db2_expansion_id':expansion_id,'locale':'enUS','snapshot_receipt_sha256':hashlib.sha256(
           (folder/'receipt.json').read_bytes()).hexdigest(),
        'blizzard_keystone_season_id':((report.get('blizzard') or {}).get('endpoints') or {}).get('keystone_season_index',{}).get('data',{}).get('current_season_id'),
        'db2_display_season_id':season_id,'raid_journal_tier_id':selected_tier,
        'wcl_zone_ids':{'raid':raid.get('zone_id'),'mplus':mplus.get('zone_id')},
        'mapped_raid_bosses':len(mapped_raid),'wcl_raid_bosses':len(raid['encounters']),
        'mapped_mplus_dungeons':len(mapped_mplus),'wcl_mplus_dungeons':len(mplus['encounters']),
        'collection_counts':counts,'items':[results[i] for i in sorted(results)],
        'raid_non_equipment_loot_candidates':sorted(
            raid_non_equipment,key=lambda r:r['item_id']),
        'raid_non_equipment_tier_tokens_verified':False,
        'raid_non_equipment_in_user_gear_catalog':False,
        'unknown':problems,'unverified_world_state_expressions':True,
        'full_season_completeness_confirmed':False,
        'old_item_catalog_imported':False,'simc_native_calls':0}

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--csv-dir',type=Path,required=True)
    p.add_argument('--season-report',type=Path,required=True)
    p.add_argument('--expansion-id',type=int,required=True)
    p.add_argument('--raid-zone',required=True)
    p.add_argument('--mplus-zone',required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args(argv)
    try:
        receipt=json.loads((a.csv_dir/'receipt.json').read_text(encoding='utf8'))
        report=json.loads(a.season_report.read_text(encoding='utf8'))
        result=build_index(a.csv_dir,report,raid_zone=a.raid_zone,
                           mplus_zone=a.mplus_zone,build=receipt['build'],
                           expansion_id=a.expansion_id)
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(json.dumps({'status':result['status'],**result['collection_counts'],
              'mapped_raid':result['mapped_raid_bosses'],
              'mapped_mplus':result['mapped_mplus_dungeons'],'native':0}))
        return 0
    except (JoinBlocked,KeyError,ValueError,OSError) as e:
        print(json.dumps({'status':'BLOCKED','code':str(e) if isinstance(e,JoinBlocked) else type(e).__name__}))
        return 3

if __name__=='__main__':raise SystemExit(main())
