#!/usr/bin/env python3
"""DB2-first class tier CANDIDATES: zero publisher names or season ID seeds.

Three small same-build Wago relations: ItemSet, ItemSetSpell and
ChrSpecialization. Physical candidates are checked against the existing
v161 ItemSparse/Item snapshot using original v168 slot/armor contracts.
Candidates NEVER certify current season: multiple same-expansion tier
rosters can each have 13 classes, 5 pieces and 2/4 spell thresholds.
"""
from __future__ import annotations

import csv
from collections import defaultdict
import hashlib
import io
import json
from pathlib import Path
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

import v168_current_season_tier_discovery as physical
import v217_stage_execution_engine as stages
import v231_simc_tier_item_join as simc_tier

SCHEMA="v245_db2_first_class_tier_candidates_v1"
TABLES=("ItemSet","ItemSetSpell","ChrSpecialization")
MAX_SOURCE_BYTES={"ItemSet":5_000_000,"ItemSetSpell":20_000_000,
                  "ChrSpecialization":5_000_000}
CLASS_IDS=simc_tier.CLASS_ID
BY_ID={v:k for k,v in CLASS_IDS.items()}
MAX_RELATION_ROWS=30000

class TierDBBlocked(ValueError): pass

def need(ok,code):
    if not ok:raise TierDBBlocked(code)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def number(x):
    try:return int(x)
    except (ValueError,TypeError):return 0

def rows(raw,columns,table):
    need(type(raw) is bytes and 0<len(raw)<=MAX_SOURCE_BYTES[table],
         "TIER_DB2_SOURCE_BYTES_INVALID:"+table)
    try:
        reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
        need(reader.fieldnames and set(columns)<=set(reader.fieldnames),
             "TIER_DB2_SOURCE_COLUMNS_MISSING:"+table)
        result=[]
        for n,r in enumerate(reader):
            need(n<MAX_RELATION_ROWS,"TIER_DB2_SOURCE_ROWS_LIMIT:"+table)
            result.append(r)
        return result
    except (csv.Error,UnicodeError) as exc:
        raise TierDBBlocked("TIER_DB2_SOURCE_CSV_INVALID:"+table) from exc

def discover(*,wago_folder,build,expansion_id,source_bytes):
    """No prior season ID, set name, raid loot token, historical profile."""
    need(type(source_bytes) is dict and set(source_bytes)==set(TABLES)
         and type(build) is str and re.fullmatch(
             r"\d+(?:\.\d+){3}",build) is not None
         and type(expansion_id) is int and expansion_id>0,
         "TIER_DB2_SCOPE_OR_SOURCE_INVALID")
    folder=Path(wago_folder)
    receipt=json.loads((folder/"receipt.json").read_text("utf8"))
    need(receipt.get("build")==build and receipt.get("locale")=="enUS"
         and set(("ItemSparse","Item"))<=set(receipt.get("tables",{})),
         "TIER_DB2_PINNED_V161_RECEIPT_REQUIRED")
    for name in ("ItemSparse","Item"):
        p=folder/(name+".csv")
        need(p.is_file() and not p.is_symlink()
             and p.stat().st_size==receipt["tables"][name]["bytes"],
             "TIER_DB2_PINNED_PHYSICAL_FILE_INVALID:"+name)
        # The original v216 stage already sealed every original v161 output
        # and checks its SHA; no additional full-file digest pass here.
    sets=rows(source_bytes["ItemSet"],("ID","Name_lang",*[f"ItemID_{i}"
                    for i in range(17)]),"ItemSet")
    spells=rows(source_bytes["ItemSetSpell"],
                ("ItemSetID","ChrSpecID","SpellID","Threshold"),
                "ItemSetSpell")
    specs=rows(source_bytes["ChrSpecialization"],("ID","ClassID"),
               "ChrSpecialization")
    spec_class={}
    for r in specs:
        sid,cid=number(r["ID"]),number(r["ClassID"])
        if sid>0:
            need(sid not in spec_class,"TIER_CHRSPEC_DUPLICATE_ID")
            spec_class[sid]=cid
    need(bool(spec_class),"TIER_CHRSPEC_EMPTY")
    bonuses=defaultdict(lambda:defaultdict(dict))
    for r in spells:
        setid,spec,threshold,spell=map(number,(r["ItemSetID"],
                                        r["ChrSpecID"],r["Threshold"],
                                        r["SpellID"]))
        if setid<=0 or spec_class.get(spec) not in BY_ID or threshold not in (2,4):
            continue
        need(spell>0,"TIER_BONUS_SPELL_ID_INVALID")
        subset=bonuses[setid][spec]
        need(threshold not in subset or subset[threshold]==spell,
             "TIER_BONUS_DUPLICATE_SPEC_THRESHOLD")
        subset[threshold]=spell
    known=set()
    provisional={}
    wanted=set()
    for r in sets:
        sid=number(r["ID"])
        need(sid>0 and sid not in known,"TIER_ITEMSET_ID_MISSING_OR_DUPLICATE")
        known.add(sid)
        group=bonuses.get(sid,{})
        qualified={spec:pair for spec,pair in group.items()
                   if set(pair)=={2,4}}
        if len(qualified)<2 or len(qualified)!=len(group):
            continue
        classes={spec_class[s] for s in qualified}
        if len(classes)!=1:continue
        cid=next(iter(classes))
        physical_ids=[number(r[f"ItemID_{i}"]) for i in range(17)]
        physical_ids=[iid for iid in physical_ids if iid>0]
        if len(physical_ids)!=5 or len(set(physical_ids))!=5:
            continue
        provisional[sid]={"item_set_id":sid,
            "name":r["Name_lang"],"class":BY_ID[cid],"class_id":cid,
            "item_ids":sorted(physical_ids),
            "spec_bonus_spells":{str(spec):{"2":sp[2],"4":sp[4]}
                                 for spec,sp in sorted(qualified.items())}}
        wanted.update(physical_ids)
    sparse={}
    for r in physical.rows(folder/"ItemSparse.csv",
                           ("ID","ItemSet","ExpansionID","AllowableClass",
                            "InventoryType")):
        iid=number(r["ID"])
        if iid in wanted:
            need(iid not in sparse,"TIER_PHYSICAL_DUPLICATE_ITEMSPARSE")
            sparse[iid]=(number(r["ItemSet"]),number(r["ExpansionID"]),
                         number(r["AllowableClass"]),number(r["InventoryType"]))
    items={}
    for r in physical.rows(folder/"Item.csv",
                           ("ID","ClassID","SubclassID","InventoryType")):
        iid=number(r["ID"])
        if iid in wanted:
            need(iid not in items,"TIER_PHYSICAL_DUPLICATE_ITEM")
            items[iid]=(number(r["ClassID"]),number(r["SubclassID"]),
                        number(r["InventoryType"]))
    found=[]
    for sid,data in sorted(provisional.items()):
        cl,cid=data["class"],data["class_id"]
        mask=1<<(cid-1)
        pieces={}
        for iid in data["item_ids"]:
            sp=sparse.get(iid)
            it=items.get(iid)
            if (not sp or not it or sp[0]!=sid or sp[1]!=expansion_id
                or sp[2]!=mask or it[:2]!=(4,physical.FAMILY[cl])
                or it[2]!=sp[3]):
                break
            slot=physical.CORE.get(sp[3])
            if slot is None or slot in pieces:break
            pieces[slot]=iid
        else:
            if set(pieces)==set(physical.SLOTS):
                found.append({"item_set_id":sid,
                    "name_observed_not_used_for_selection":data["name"],
                    "class":cl,"class_id":cid,
                    "tier_piece_ids":{k:pieces[k] for k in physical.SLOTS},
                    "spec_bonus_spells":data["spec_bonus_spells"],
                    "season_membership_verified":False})
    byclass={cl:[r["item_set_id"] for r in found if r["class"]==cl]
             for cl in sorted(physical.FAMILY)}
    payload={"schema":SCHEMA,
        "status":"DB2_CLASS_TIER_CANDIDATES_SEASON_PENDING",
        "game_build":build,"expansion_id":expansion_id,
        "candidate_set_count":len(found),"candidate_counts_by_class":
            {cl:len(ids) for cl,ids in byclass.items()},
        "candidate_set_ids_by_class":byclass,
        "candidates":found,
        "evidence":{"source":"WAGO_SAME_BUILD_DB2",
             "item_set_sha256":sha(source_bytes["ItemSet"]),
             "item_set_spell_sha256":sha(source_bytes["ItemSetSpell"]),
             "chr_specialization_sha256":sha(source_bytes["ChrSpecialization"]),
             "v161_item_sparse_sha256":receipt["tables"]["ItemSparse"]["sha256"],
             "v161_item_sha256":receipt["tables"]["Item"]["sha256"],
             "class_armor_slots_from_existing_v168":True},
        "used_prior_tier_names":False,"used_prior_tier_ids":False,
        "current_season_selection":None,
        "source_season_verified":False,"environment_ready":False,
        "native_calls":0}
    return payload

def fetch_table(table,build,*,transport=urlopen):
    need(table in TABLES,"TIER_DB2_TABLE_UNSUPPORTED")
    url="https://wago.tools/db2/"+table+"/csv?"+urlencode({
        "build":build,"locale":"enUS"})
    req=Request(url,headers={"User-Agent":"SIMC-Secondary-DB2-Tier/1.0",
                              "Accept":"text/csv"})
    try:
        with transport(req,timeout=60) as response:
            need(response.status==200,"TIER_DB2_HTTP_NON_200:"+table)
            output=io.BytesIO()
            while True:
                chunk=response.read(262144)
                if not chunk:break
                need(output.tell()+len(chunk)<=MAX_SOURCE_BYTES[table],
                     "TIER_DB2_DOWNLOAD_LIMIT:"+table)
                output.write(chunk)
            need(output.tell()>0,"TIER_DB2_SOURCE_EMPTY:"+table)
            return output.getvalue()
    except (HTTPError,URLError,TimeoutError,OSError) as exc:
        raise TierDBBlocked("TIER_DB2_DOWNLOAD_FAILED:"+table) from exc

def build_stage(*,stage_root,wago_folder,build,expansion_id,
                wago_receipt_sha256,transport=None):
    root=Path(stage_root)
    need(root.is_dir() and not root.is_symlink(),
         "TIER_DB2_STAGE_ROOT_INVALID")
    need(type(wago_receipt_sha256) is str and
         re.fullmatch(r"[0-9a-f]{64}",wago_receipt_sha256) is not None,
         "TIER_DB2_V161_RECEIPT_IDENTITY_REQUIRED")
    outputs={t:"source/db2_tier_"+t+".csv" for t in TABLES}
    outputs["candidates"]="source/v245_db2_tier_candidates.json"
    code=stages.module_dependency_fingerprint(
        [Path(__file__),Path(stages.__file__)])
    def execute():
        opts={} if transport is None else {"transport":transport}
        sources={t:fetch_table(t,build,**opts) for t in TABLES}
        result=discover(wago_folder=wago_folder,build=build,
                         expansion_id=expansion_id,source_bytes=sources)
        for t in TABLES:
            p=root/outputs[t];p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(sources[t])
        p=root/outputs["candidates"]
        p.write_text(json.dumps(result,sort_keys=True,
            ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    def validate(paths):
        doc=json.loads(paths["candidates"].read_text("utf8"))
        return (doc.get("schema")==SCHEMA
                and doc.get("game_build")==build
                and doc.get("expansion_id")==expansion_id
                and doc.get("status")==
                    "DB2_CLASS_TIER_CANDIDATES_SEASON_PENDING"
                and doc.get("used_prior_tier_names") is False
                and doc.get("used_prior_tier_ids") is False
                and doc.get("current_season_selection") is None
                and doc.get("source_season_verified") is False
                and doc.get("environment_ready") is False
                and doc.get("native_calls")==0
                and all(doc.get("evidence",{}).get(
                    {"ItemSet":"item_set_sha256",
                     "ItemSetSpell":"item_set_spell_sha256",
                     "ChrSpecialization":"chr_specialization_sha256"}[t])
                    ==sha(paths[t].read_bytes()) for t in TABLES))
    try:
        stage=stages.execute_stage(root=root,
            stage_id="fresh-db2-class-tier-candidates",
            stage_version="v245-no-name-no-season-seed-1",
            inputs={"game_build":build,"expansion_id":expansion_id,
                    "v161_receipt_sha256":wago_receipt_sha256,
                    "wago_extra_tables":list(TABLES),
                    "code_sha256":code["sha256"]},
            outputs=outputs,execute=execute,validate=validate)
    except stages.StageExecutionBlocked as exc:
        raise TierDBBlocked("TIER_DB2_CANDIDATE_STAGE_BLOCKED:"+str(exc)) from exc
    target=root/outputs["candidates"]
    doc=json.loads(target.read_text("utf8"))
    return {"schema":SCHEMA,"status":doc["status"],
            "candidate_path":str(target.resolve()),
            "candidate_set_count":doc["candidate_set_count"],
            "candidate_counts_by_class":doc["candidate_counts_by_class"],
            "source_stage":{k:v for k,v in stage.items() if k!="result"},
            "network_calls_by_stage":len(TABLES) if stage["executed"] else 0,
            "used_publisher_names":False,
            "source_season_verified":False,"environment_installed":False,
            "environment_ready":False,"native_calls":0}
