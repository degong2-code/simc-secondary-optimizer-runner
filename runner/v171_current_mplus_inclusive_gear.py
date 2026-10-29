#!/usr/bin/env python3
"""v171: include ALL 223 season-mapped M+ Journal equipment candidates.

The v163 source joined 8/8 live WCL season dungeons to same-build DB2.
v165/v166 quarantined all 223 because Journal DisplaySeason=0 / opaque
WorldStateExpression, and because some returning dungeons use older
ExpansionID. These are not negative eligibility evidence. Include as
SEASON_MPLUS_DUNGEON_CANDIDATE (not item-drop/SimC-effect certification).
Two unrelated raid set items remain excluded. No network/Native/gear seed.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import Counter
from pathlib import Path
import v167_product_season_gear_adapter as adapter

SCHEMA="v171_current_mplus_inclusive_gear_update_v1"
PINNED_BUILD="12.1.5.70575"
MPLUS_BASIS="SEASON_MPLUS_JOURNAL_CANDIDATE_WORLDSTATE_UNRESOLVED"
MAX_CSV=210_000_000
MAX_ROWS=1_000_000
class InclusionBlocked(ValueError):pass
def need(condition,why):
    if not condition:raise InclusionBlocked(why)
def as_int(value):
    try:return int(value)
    except(ValueError,TypeError):raise InclusionBlocked("INVALID_DB2_INTEGER")
def table(path,ids,fields):
    p=Path(path)
    need(p.is_file() and 0<p.stat().st_size<=MAX_CSV,"DB2_MISSING_OR_TOO_BIG")
    out={}
    with p.open(encoding="utf-8-sig",newline="") as f:
        r=csv.DictReader(f)
        need(set(fields)<=set(r.fieldnames or ()),"DB2_COLUMNS_MISSING")
        for i,row in enumerate(r):
            need(i<MAX_ROWS,"DB2_ROW_LIMIT")
            try:id=as_int(row["ID"])
            except InclusionBlocked:continue
            if id not in ids:continue
            need(id not in out,"DUPLICATE_DB2_ITEM")
            out[id]=row
    need(set(out)==ids,"MPLUS_ITEM_DB2_NOT_FOUND")
    return out
def digest(path):
    value=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            value.update(chunk)
    return value.hexdigest()
def build(source,item_file,sparse_file,*,receipt=None):
    need(type(source) is dict and source.get("schema")==adapter.SOURCE_SCHEMA
         and source.get("status")=="COMPACT_CANDIDATE_DB_WITH_PENDING_GAPS"
         and source.get("season_build")==PINNED_BUILD
         and source.get("no_old_catalog_seed") is True
         and source.get("native_calls")==0,
         "CURRENT_SEASON_V166_PINNED_SOURCE_REQUIRED")
    if receipt is not None:
        need(receipt.get("build")==PINNED_BUILD and receipt.get("locale")=="enUS",
             "DB2_RECEIPT_BUILD_OR_LOCALE_MISMATCH")
        for name,path in (("Item",item_file),("ItemSparse",sparse_file)):
            meta=receipt.get("tables",{}).get(name,{})
            need(meta.get("bytes")==Path(path).stat().st_size and
                 meta.get("sha256")==digest(path),"DB2_PINNED_SHA_MISMATCH_"+name)
    conditional=source.get("conditional_unverified")
    need(type(conditional) is list and
         len(conditional)==source.get("conditional_count"),
         "CONDITIONAL_COUNT_MISMATCH")
    # ALL candidate rows belong to the already live-WCL-mapped eight M+ dungeons.
    # Never reinterpret unresolved WorldStateExpression as false or "not current".
    mplus=[x for x in conditional if
           x.get("reason")=="CONDITIONAL_SEASON_NOT_ESTABLISHED"
           and x.get("source_kinds")==["mplus_journal"]
           and x.get("category") in (
               "trinket","special_effect_gear_candidate",
               "plain_representative_candidate")]
    other=[x for x in conditional if x not in mplus]
    need(len(mplus)==223 and len(other)==2 and
         all(x.get("category")=="set_piece_unclassified" for x in other)
         and len({x["item_id"] for x in mplus})==223,
         "SEASON_MPLUS_SOURCE_SET_UNEXPECTED")
    ids={x["item_id"] for x in mplus}
    items=table(item_file,ids,("ID","ClassID","SubclassID","InventoryType"))
    sparse=table(sparse_file,ids,("ID","Display_lang","InventoryType",
        "ExpansionID","AllowableClass","ItemSet","StatModifier_bonusStat_0"))
    # A previous-expansion ItemSparse.ExpansionID is normal for returning
    # M+ dungeons; it must not disqualify a live-season journal candidate.
    added=[]
    expansion_counts=Counter()
    for old in mplus:
        id=old["item_id"];raw=items[id];s=sparse[id]
        inventory=as_int(raw["InventoryType"])
        cls=as_int(raw["ClassID"]);sub=as_int(raw["SubclassID"])
        expansion=as_int(s["ExpansionID"])
        need(inventory==as_int(s["InventoryType"])==old["slot"]
             and cls in (2,4) and sub>=0 and
             as_int(s["ItemSet"])==0 and
             type(s["Display_lang"]) is str and s["Display_lang"],
             "MPLUS_ITEM_METADATA_OR_SLOT_MISMATCH")
        need((old["category"]=="trinket")==(
            inventory==adapter.TRINKET_INVENTORY_TYPE),
            "MPLUS_TRINKET_ROLE_MISMATCH")
        row={"item_id":id,"name":s["Display_lang"],"slot":inventory,
            "class_id":cls,"subclass_id":sub,
            "allowed_class_mask":as_int(s["AllowableClass"]),
            "stat_modifier_codes":[as_int(s.get(
                "StatModifier_bonusStat_"+str(i),"0") or "0")
                for i in range(10)],
            "item_set_id":0,"category":old["category"],
            "source_kinds":["mplus_journal"],
            "selection_evidence":"CURRENT_CANDIDATE"}
        row["stat_modifier_codes"]=[x for x in row["stat_modifier_codes"]
                                    if x!=0]
        added.append(row)
        expansion_counts[expansion]+=1
    upgraded=dict(source)
    upgraded["current_candidates"]=source["current_candidates"]+added
    upgraded["current_candidate_count"]=len(upgraded["current_candidates"])
    upgraded["current_role_counts"]=dict(sorted(
        Counter(x["category"] for x in upgraded["current_candidates"]).items()))
    upgraded["conditional_unverified"]=other
    upgraded["conditional_count"]=len(other)
    # v167 enforces exact category/slot/name and status; preserve code path.
    product=adapter.from_v166(upgraded)
    for item in product["items"]:
        if item["item_id"] in ids:
            item["season_list_basis"]=MPLUS_BASIS
    product["mplus_season_candidate_inclusion"]={
        "schema":SCHEMA,"matched_current_season_dungeons":8,
        "added_item_count":len(added),
        "added_roles":dict(sorted(Counter(x["category"] for x in added).items())),
        "older_expansion_ids_permitted":dict(sorted(expansion_counts.items())),
        "world_state_effectively_resolved":False,
        "actual_drop_or_simc_effect_certified":False,
        "provider_api_calls":0,"native_calls":0}
    need(product["item_count"]==511 and
         product["role_counts"]=={
           "trinket":63,"special_effect_gear_candidate":14,
           "selectable_stat_craft":106,"plain_representative_candidate":328}
         and product["conditional_ids_excluded"]==2,
         "INCLUSIVE_ROLE_COUNTS_UNEXPECTED")
    return adapter.validate(product)

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--source-v166",type=Path,required=True)
    p.add_argument("--csv-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args(argv)
    try:
        folder=a.csv_dir
        receipt=json.loads((folder/"receipt.json").read_text(encoding="utf8"))
        output=build(json.loads(a.source_v166.read_text(encoding="utf8")),
            folder/"Item.csv",folder/"ItemSparse.csv",receipt=receipt)
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(output,ensure_ascii=False,sort_keys=True,
                  separators=(",",":"))+"\n",encoding="utf8")
        print(json.dumps({"status":"MPLUS_SEASON_LINKED_CANDIDATES_INCLUDED",
             "items":output["item_count"],"roles":output["role_counts"],
             "added_mplus":output["mplus_season_candidate_inclusion"]["added_item_count"],
             "unresolved_raid_set":output["conditional_ids_excluded"],
             "native":0,"provider":0},sort_keys=True))
        return 0
    except (InclusionBlocked,adapter.GearBlocked,ValueError,
            TypeError,KeyError,OSError) as exc:
        code=(str(exc) if isinstance(exc,(InclusionBlocked,adapter.GearBlocked))
              else type(exc).__name__)
        print(json.dumps({"status":"BLOCKED","code":code}))
        return 3
if __name__=="__main__":raise SystemExit(main())
