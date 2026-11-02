#!/usr/bin/env python3
"""Same-build DB2 tier/active-raid bonus-group corroboration; never auto-admit.

Uses independently authenticated current-raid loot already discovered by v163,
structural 13x5 candidate rosters from v245, and only two small Wago DB2
relations. No set names, hardcoded item/season IDs, Native, or effect reimplementation.
A unique observed bonus-group match is EVIDENCE, not guaranteed season membership.
"""
from __future__ import annotations

from collections import defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError,URLError

import v217_stage_execution_engine as stages

SCHEMA="v250_active_raid_bonus_tier_corroboration_v1"
TABLES=("ItemXBonusTree","ItemBonusTreeNode")
MAX_BYTES={"ItemXBonusTree":12_000_000,"ItemBonusTreeNode":5_000_000}
MAX_CANDIDATES=1000

class BonusSourceBlocked(ValueError):pass

def need(ok,code):
    if not ok:raise BonusSourceBlocked(code)

def num(x):
    try:return int(x)
    except (ValueError,TypeError):return 0

def sha(raw):return hashlib.sha256(raw).hexdigest()

def rows(raw,table,columns):
    need(isinstance(raw,bytes) and 0<len(raw)<=MAX_BYTES[table],
         "V250_SOURCE_BYTES_INVALID_"+table)
    try:
        r=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
        need(set(columns)<=set(r.fieldnames or ()),
             "V250_SOURCE_COLUMNS_MISSING_"+table)
        yield from r
    except (UnicodeError,csv.Error) as e:
        raise BonusSourceBlocked("V250_CSV_INVALID_"+table) from e

def correlate(*,tier,raid,source_bytes):
    need(tier.get("schema")=="v245_db2_first_class_tier_candidates_v1"
         and tier.get("current_season_selection") is None
         and tier.get("source_season_verified") is False
         and tier.get("environment_ready") is False
         and type(tier.get("candidates")) is list
         and len(tier["candidates"])<=MAX_CANDIDATES,
         "V250_DB2_TIER_CANDIDATES_REQUIRED")
    need(raid.get("schema")=="v163_zero_seed_db2_join_v1"
         and raid.get("source_provider")=="WAGO_TOOLS_PINNED_DB2_WCL_LIVE"
         and raid.get("auto_source_scope",{}).get("source_basis")==
             "LIVE_WCL_ACTIVE_ZONES_AND_SAME_BUILD_DB2"
         and raid.get("full_season_completeness_confirmed") is False
         and raid.get("build")==tier.get("game_build")
         and (tier.get("expansion_id") is None or
              raid.get("db2_expansion_id")==tier["expansion_id"]),
         "V250_AUTHENTICATED_SAME_BUILD_RAID_REQUIRED")
    need(type(source_bytes) is dict and set(source_bytes)==set(TABLES),
         "V250_SAME_BUILD_BONUS_RELATIONS_REQUIRED")
    original=defaultdict(set)
    raid_ilvl={}
    for x in raid.get("items",[]):
        if any(s.get("source")=="raid_journal"
               for s in x.get("acquisition_sources",[])):
            need(type(x.get("item_id")) is int and x["item_id"]>0,
                 "V250_RAID_ITEM_ID_INVALID")
            original[x["item_id"]].add("raid_journal")
    for x in raid.get("raid_non_equipment_loot_candidates",[]):
        need(type(x.get("item_id")) is int and x["item_id"]>0,
             "V250_NON_EQUIPMENT_ITEM_ID_INVALID")
        if any(s.get("source")=="raid_journal"
               for s in x.get("acquisition_sources",[])):
            original[x["item_id"]].add("raid_non_equipment_loot")
            lvl=x.get("observed_base_item_level")
            if type(lvl) is int and lvl>0:raid_ilvl[x["item_id"]]=lvl
    need(original,"V250_ACTIVE_RAID_SOURCE_LOOT_EMPTY")
    roster_groups=[r for r in tier.get("observed_base_ilvl_roster_groups",[])
                   if r.get("exact_13_class_5piece_structural_roster") is True]
    if not roster_groups:
        raise BonusSourceBlocked("V250_NO_COMPLETE_13_CLASS_COHORT")
    byset={x["item_set_id"]:x for x in tier["candidates"]}
    cohorts=[]
    all_tier_ids=set()
    for g in roster_groups:
        sets=g["item_set_ids_by_class"]
        need(len(sets)==13 and all(len(a)==1 for a in sets.values()),
             "V250_COHORT_CLASS_SET_INVALID")
        entries=[byset[ids[0]] for ids in sets.values()]
        need(all(x["observed_expansion_id"]==g["observed_expansion_id"]
                 and x.get("observed_base_item_level_min")==
                     g["observed_base_item_level"]
                 and x.get("observed_base_item_level_max")==
                     g["observed_base_item_level"]
                 for x in entries),"V250_COHORT_ILVL_CONFLICT")
        ids={x for e in entries for x in e["tier_piece_ids"].values()}
        need(len(ids)==65,"V250_PHYSICAL_ROSTER_NOT_65")
        cohorts.append((g,entries,ids))
        all_tier_ids.update(ids)
    wanted=set(original)|all_tier_ids
    byitem=defaultdict(set)
    for r in rows(source_bytes["ItemXBonusTree"],"ItemXBonusTree",
                  ("ItemID","ItemBonusTreeID")):
        item=num(r["ItemID"])
        if item in wanted:
            tree=num(r["ItemBonusTreeID"])
            if tree>0:byitem[item].add(tree)
    groups=defaultdict(set);children=defaultdict(set)
    for r in rows(source_bytes["ItemBonusTreeNode"],"ItemBonusTreeNode",
                  ("ParentItemBonusTreeID","ChildItemBonusTreeID",
                   "ChildItemBonusListGroupID")):
        parent=num(r["ParentItemBonusTreeID"])
        if parent<=0:continue
        group=num(r["ChildItemBonusListGroupID"])
        child=num(r["ChildItemBonusTreeID"])
        if group>0:groups[parent].add(group)
        if child>0:children[parent].add(child)
    cache={}
    def fingerprint(item):
        if item in cache:return cache[item]
        pending=list(byitem[item]);visited=set();result=set()
        while pending:
            t=pending.pop()
            if t in visited:continue
            visited.add(t)
            need(len(visited)<=50000,"V250_BONUS_TREE_TOO_DEEP")
            result.update(groups[t])
            pending.extend(children[t]-visited)
        cache[item]=frozenset(result)
        return cache[item]
    raid_groups={i:fingerprint(i) for i in original}
    rows_out=[]
    for cohort,entries,ids in cohorts:
        fingerprints={fingerprint(i) for i in ids}
        valid=(len(fingerprints)==1 and bool(next(iter(fingerprints))))
        common=next(iter(fingerprints)) if valid else frozenset()
        matches={i for i,f in raid_groups.items() if common & f}
        tokenmatches={i for i in matches
                      if "raid_non_equipment_loot" in original[i]}
        lvlmatches={i for i in tokenmatches
                    if raid_ilvl.get(i)==cohort["observed_base_item_level"]}
        rows_out.append({
            "observed_expansion_id":cohort["observed_expansion_id"],
            "observed_base_item_level":cohort["observed_base_item_level"],
            "item_set_ids_by_class":cohort["item_set_ids_by_class"],
            "physical_items":len(ids),
            "uniform_65_item_bonus_fingerprint":valid,
            "bonus_list_group_ids":sorted(common),
            "raid_loot_overlap_item_count":len(matches),
            "raid_non_equipment_overlap_item_count":len(tokenmatches),
            "raid_non_equipment_same_base_ilvl_count":len(lvlmatches),
            "raid_loot_items_with_bonus_groups":
                sum(bool(x) for x in raid_groups.values()),
            "source_season_verified":False,
        })
    rows_out.sort(key=lambda r:(-r["raid_loot_overlap_item_count"],
                                -r["raid_non_equipment_same_base_ilvl_count"],
                                r["observed_base_item_level"],
                                r["observed_expansion_id"]))
    best=rows_out[0]
    unique=(best["uniform_65_item_bonus_fingerprint"]
            and best["raid_loot_overlap_item_count"]>0
            and (len(rows_out)==1 or best["raid_loot_overlap_item_count"]>
                  rows_out[1]["raid_loot_overlap_item_count"]))
    return {
        "schema":SCHEMA,
        "status":("UNIQUE_RAID_BONUS_CORRELATED_TIER_COHORT_SEASON_PENDING"
                  if unique else "RAID_BONUS_TIER_COHORT_AMBIGUOUS_PENDING"),
        "game_build":tier["game_build"],
        "active_raid_scope":raid["auto_source_scope"]["raid_zone"],
        "raid_journal_item_count":len(original),
        "active_raid_bonus_group_evidence_count":
            sum(bool(x) for x in raid_groups.values()),
        "candidate_cohort_count":len(rows_out),
        "cohort_comparisons":rows_out,
        "observed_leading_cohort":best if unique else None,
        "observed_leading_cohort_is_certified_current_season":False,
        "source_season_verified":False,
        "environment_ready":False,
        "native_calls":0,
        "source_evidence":{
            "ItemXBonusTree_sha256":sha(source_bytes["ItemXBonusTree"]),
            "ItemBonusTreeNode_sha256":sha(source_bytes["ItemBonusTreeNode"]),
            "v163_raid_scope_source":
                raid["auto_source_scope"]["source_basis"],
            "v245_five_piece_metadata_verified":True,
            "previous_itemset_id_seed_used":False,
            "publisher_tier_name_used":False,
            "observed_bonus_groups_not_a_season_flag":True}}

def fetch_table(name,build,*,transport=urlopen):
    need(name in TABLES,"V250_TABLE_INVALID")
    url="https://wago.tools/db2/"+name+"/csv?"+urlencode(
        {"build":build,"locale":"enUS"})
    req=Request(url,headers={"User-Agent":"SIMC-Secondary-Tier-Bonus/1.0"})
    try:
        with transport(req,timeout=70) as r:
            need(r.status==200,"V250_HTTP_NON_200_"+name)
            out=io.BytesIO()
            while True:
                buf=r.read(262144)
                if not buf:break
                need(out.tell()+len(buf)<=MAX_BYTES[name],
                     "V250_CSV_TOO_LARGE_"+name)
                out.write(buf)
        need(out.tell()>0,"V250_CSV_EMPTY_"+name)
        return out.getvalue()
    except (URLError,HTTPError,OSError,TimeoutError) as e:
        raise BonusSourceBlocked("V250_DOWNLOAD_FAILED_"+name) from e

def build_stage(*,stage_root,build,tier_candidate_path,raid_candidate_path,
                tier_stage_receipt,raid_stage_receipt,transport=None):
    root=Path(stage_root)
    need(root.is_dir() and not root.is_symlink(),"V250_STAGE_ROOT_INVALID")
    tier_path=Path(tier_candidate_path)
    raid_path=Path(raid_candidate_path)
    need(tier_path.is_file() and raid_path.is_file() and
         not tier_path.is_symlink() and not raid_path.is_symlink(),
         "V250_SOURCE_REPORTS_REQUIRED")
    tier_raw=tier_path.read_bytes();raid_raw=raid_path.read_bytes()
    tier=json.loads(tier_raw);raid=json.loads(raid_raw)
    need(tier.get("game_build")==build and raid.get("build")==build,
         "V250_SOURCE_BUILD_MISMATCH")
    output={name:"source/v250_bonus_"+name+".csv" for name in TABLES}
    output["result"]="source/v250_raid_bonus_corroboration.json"
    code=stages.module_dependency_fingerprint(
        [Path(__file__),Path(stages.__file__)])
    attempted=[0]
    def tracked(req,timeout):
        attempted[0]+=1
        return (urlopen if transport is None else transport)(req,timeout=timeout)
    def execute():
        data={name:fetch_table(name,build,transport=tracked)
              for name in TABLES}
        result=correlate(tier=tier,raid=raid,source_bytes=data)
        for name in TABLES:
            dest=root/output[name]
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(data[name])
        (root/output["result"]).write_text(
            json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
            encoding="utf8")
    def validate(paths):
        result=json.loads(paths["result"].read_text("utf8"))
        return (result.get("schema")==SCHEMA
                and result.get("game_build")==build
                and result.get("source_season_verified") is False
                and result.get("observed_leading_cohort_is_certified_current_season")
                    is False
                and result.get("environment_ready") is False
                and result.get("native_calls")==0
                and all(result.get("source_evidence",{}).get(name+"_sha256")
                        ==sha(paths[name].read_bytes()) for name in TABLES))
    try:
        stage=stages.execute_stage(
            root=root,stage_id="fresh-v250-raid-bonus-corroboration",
            stage_version="source-only-unique-observed-no-promotion-v1",
            inputs={"build":build,
                    "tier_candidate_sha256":sha(tier_raw),
                    "raid_candidate_sha256":sha(raid_raw),
                    "tier_stage_receipt":tier_stage_receipt,
                    "raid_stage_receipt":raid_stage_receipt,
                    "code_sha256":code["sha256"]},
            outputs=output,execute=execute,validate=validate)
    except (stages.StageExecutionBlocked,BonusSourceBlocked) as e:
        error=BonusSourceBlocked("V250_STAGE_PENDING:"+str(e).split(":",1)[0])
        error.network_calls_attempted=attempted[0]
        raise error from e
    dest=root/output["result"]
    result=json.loads(dest.read_text("utf8"))
    return {
        "schema":SCHEMA,
        "status":result["status"],
        "candidate_path":str(dest.resolve()),
        "observed_leading_cohort":result["observed_leading_cohort"],
        "raid_journal_item_count":result["raid_journal_item_count"],
        "source_season_verified":False,
        "environment_ready":False,
        "network_calls_by_stage":attempted[0],
        "source_stage":{k:v for k,v in stage.items() if k!="result"},
        "native_calls":0}
