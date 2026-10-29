#!/usr/bin/env python3
"""v168: discover current season 13 class x 5 tier pieces from pinned DB2.

No historical/v144 tier-ID seeding, no SimC Native, no new external queries.
Current independent publisher names select item-set *identity* only; every
physical item ID comes from ItemSparse.ItemSet, Item.InventoryType and class
mask in a pinned same-build DB2 snapshot. Inherited catalyst stats/cantrips
are NOT represented by the fixed tier-token item IDs.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import defaultdict
from pathlib import Path

SCHEMA="v168_source_first_class_tier_5pc_v1"
SOURCE_SCHEMA="v168_season_tier_source_anchors_v1"
CORE={1:"head",3:"shoulders",5:"chest",20:"chest",10:"hands",7:"legs"}
SLOTS=("head","shoulders","chest","hands","legs")
FAMILY={"deathknight":4,"demonhunter":2,"druid":2,"evoker":3,
        "hunter":3,"mage":1,"monk":2,"paladin":4,"priest":1,
        "rogue":2,"shaman":3,"warlock":1,"warrior":4}
MAX_TABLE_BYTES=180_000_000
MAX_ROWS=1_000_000
class TierBlocked(ValueError):pass
def need(ok,code):
    if not ok:raise TierBlocked(code)
def as_int(value,default=None):
    try:return int(value)
    except(ValueError,TypeError):return default
def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf8"))
def rows(path,columns):
    p=Path(path)
    need(p.is_file() and 0<p.stat().st_size<=MAX_TABLE_BYTES,
         "TIER_DB2_FILE_MISSING_OR_TOO_LARGE")
    with p.open(encoding="utf-8-sig",newline="") as f:
        r=csv.DictReader(f)
        need(set(columns)<=set(r.fieldnames or []),"TIER_DB2_SCHEMA_MISSING")
        for n,x in enumerate(r):
            need(n<MAX_ROWS,"TIER_DB2_ROWS_LIMIT")
            yield x
def hash_file(path):
    d=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            d.update(b)
    return d.hexdigest()

def discover(anchors,sparse_csv,item_csv,*,receipt=None):
    need(type(anchors) is dict and anchors.get("schema")==SOURCE_SCHEMA
         and anchors.get("policy")=="SOURCE_FIRST_SAME_BUILD_MATCH_CLASS_NAME_AND_ITEMSET_NOT_OLD_PROFILE_IDS"
         and type(anchors.get("classes")) is dict
         and set(anchors["classes"])==set(FAMILY)
         and type(anchors.get("retail_build")) is str
         and type(anchors.get("expansion_id")) is int
         and anchors.get("native_item_set_effect_certified") is False,
         "TIER_SOURCE_ANCHORS_INVALID")
    if receipt is not None:
        need(receipt.get("build")==anchors["retail_build"] and
             receipt.get("locale")=="enUS", "TIER_SNAPSHOT_BUILD_MISMATCH")
        for name,path in (("Item",item_csv),("ItemSparse",sparse_csv)):
            row=receipt.get("tables",{}).get(name,{})
            need(row.get("bytes")==Path(path).stat().st_size
                 and row.get("sha256")==hash_file(path),
                 "TIER_DB2_SNAPSHOT_SHA_MISMATCH_"+name)
    # One scan: find nonzero set groups with current expansion, including
    # names not containing the marketing name (notably Evoker's chest/legs).
    sets=defaultdict(list)
    matches=defaultdict(set)
    for r in rows(sparse_csv,("ID","Display_lang","InventoryType","ExpansionID",
                              "ItemSet","AllowableClass")):
        if as_int(r["ExpansionID"])!=anchors["expansion_id"]:continue
        itemset=as_int(r["ItemSet"],0)
        slot=CORE.get(as_int(r["InventoryType"],0))
        if itemset<=0 or slot is None:continue
        rec={"item_id":as_int(r["ID"]),"name":r["Display_lang"],
             "slot":slot,"inventory_type":as_int(r["InventoryType"]),
             "item_set_id":itemset,"allowable_class":as_int(r["AllowableClass"])}
        need(type(rec["item_id"]) is int and rec["item_id"]>0,
             "TIER_ITEM_ID_INVALID")
        sets[itemset].append(rec)
        for cl,needle in anchors["classes"].items():
            need(type(needle) is str and len(needle)>=7 and len(needle)<=80,
                 "TIER_ANCHOR_NAME_INVALID")
            if needle.casefold() in rec["name"].casefold():
                matches[cl].add(itemset)
    assigned={}
    for cl in sorted(FAMILY):
        observed=matches[cl]
        need(len(observed)==1,"TIER_NAME_SET_NOT_UNIQUE:"+cl)
        itemset=next(iter(observed))
        pieces=sets[itemset]
        need(len(pieces)==5 and {x["slot"] for x in pieces}==set(SLOTS),
             "TIER_ITEMSET_NOT_EXACT_FIVE:"+cl)
        restrictions={x["allowable_class"] for x in pieces}
        need(len(restrictions)==1 and next(iter(restrictions))>0
             and (next(iter(restrictions)) & (next(iter(restrictions))-1))==0,
             "TIER_CLASS_MASK_NOT_SINGLE_CLASS:"+cl)
        assigned[cl]={"item_set_id":itemset,"allowed_class_mask":
                      next(iter(restrictions)),
                      "pieces":{x["slot"]:x["item_id"] for x in pieces},
                      "names":{x["slot"]:x["name"] for x in pieces}}
    need(len({r["item_set_id"] for r in assigned.values()})==len(FAMILY),
         "TIER_ITEMSET_SHARED_ACROSS_CLASSES")
    needed={item_id for info in assigned.values() for item_id in info["pieces"].values()}
    need(len(needed)==len(FAMILY)*5,"TIER_ID_DUPLICATE")
    item_meta={}
    for r in rows(item_csv,("ID","ClassID","SubclassID","InventoryType")):
        iid=as_int(r["ID"])
        if iid not in needed:continue
        need(iid not in item_meta,"TIER_ITEM_DUPLICATE_DB2")
        item_meta[iid]=(as_int(r["ClassID"]),as_int(r["SubclassID"]),
                        as_int(r["InventoryType"]))
    need(set(item_meta)==needed,"TIER_ITEMS_NOT_IN_ITEM_DB2")
    for cl,info in assigned.items():
        for slot,iid in info["pieces"].items():
            cls,sub,inv=item_meta[iid]
            need(cls==4 and sub==FAMILY[cl] and CORE.get(inv)==slot,
                 "TIER_PHYSICAL_CLASS_OR_SLOT_MISMATCH:"+cl)
    return {"schema":SCHEMA,"status":"SOURCE_VERIFIED_13_CLASS_FIVE_PIECE_IDS",
      "season":anchors["season"],"retail_build":anchors["retail_build"],
      "expansion_id":anchors["expansion_id"],"class_count":len(assigned),
      "item_count":len(needed),"classes":assigned,
      "evidence":{"publisher_url":anchors["source_url"],
        "db2_item_sparse_sha256":hash_file(sparse_csv),
        "db2_item_sha256":hash_file(item_csv),
        "name_anchor_is_not_item_id_seed":True},
      "native_calls":0,"api_calls":0,
      "simc_tier_bonus_mechanics_verified":False,
      "catalyst_retains_original_stats_and_cantrips":True,
      "catalyst_variant_emulation_implemented":False,
      "production_profile_promoted":False}
def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--anchors",type=Path,required=True)
    p.add_argument("--csv-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args(argv)
    try:
        receipt=read_json(a.csv_dir/"receipt.json")
        result=discover(read_json(a.anchors),a.csv_dir/"ItemSparse.csv",
                        a.csv_dir/"Item.csv",receipt=receipt)
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(result,ensure_ascii=False,
                         sort_keys=True,indent=2)+"\n",encoding="utf8")
        print(json.dumps({"status":result["status"],"classes":result["class_count"],
             "pieces":result["item_count"],"native":0},sort_keys=True))
        return 0
    except (TierBlocked,ValueError,TypeError,KeyError,OSError) as e:
        print(json.dumps({"status":"BLOCKED","code":str(e) if isinstance(e,TierBlocked) else type(e).__name__}))
        return 3
if __name__=="__main__":
    raise SystemExit(main())
