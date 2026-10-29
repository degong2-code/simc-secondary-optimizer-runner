#!/usr/bin/env python3
"""v166 product-ready shape for a small season roster, without effect simulation.

Current candidates and conditional Journal loot are separated. Adds exact
same-build Item.class/subclass and un-interpreted stat modifier IDs so the
existing representative composer can select class-compatible base items later.
Never certifies an entire DPS spec, a four-piece tier, or an item effect.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import Counter
from pathlib import Path

SCHEMA="v166_current_season_product_gear_db_v1"
MAX_BYTES=3_000_000
MAX_CSV=210_000_000
MAX_ROWS=1_000_000

class GearDbBlocked(ValueError):pass
def need(value,code):
    if not value:raise GearDbBlocked(code)
def load(path):
    p=Path(path)
    need(p.is_file() and 0<p.stat().st_size<=MAX_BYTES,"SOURCE_POOL_INVALID")
    return json.loads(p.read_text(encoding="utf8"))
def extract(path,columns,ids):
    p=Path(path)
    need(p.is_file() and 0<p.stat().st_size<=MAX_CSV,"ITEM_TABLE_MISSING")
    matched={}
    with p.open(encoding="utf-8-sig",newline="") as f:
        rd=csv.DictReader(f)
        need(set(columns)<=set(rd.fieldnames or []),"ITEM_COLUMNS_MISSING")
        for i,row in enumerate(rd):
            need(i<MAX_ROWS,"ITEM_ROW_LIMIT")
            try:iid=int(row["ID"])
            except (ValueError,TypeError):continue
            if iid in ids:
                need(iid not in matched,"DUPLICATE_DB2_ITEM_ID")
                matched[iid]=row
    need(set(matched)==ids,"CATALOG_ITEM_NOT_IN_DB2")
    return matched
def integer(x):
    try:return int(x)
    except (ValueError,TypeError):raise GearDbBlocked("ITEM_FIELD_NOT_INTEGER")
def build(pool,item_file,sparse_file):
    need(pool.get("schema")=="v165_current_season_gear_pool_v1"
         and pool.get("status")=="EFFECT_TABLE_OBSERVED_CANDIDATES"
         and pool.get("no_legacy_catalog_seed") is True
         and isinstance(pool.get("item_x_item_effect_csv_sha256"),str),
         "SOURCE_POOL_NOT_CLASSIFIED")
    values=pool.get("items")
    need(type(values) is list and 1<=len(values)<=30000,"SOURCE_ITEM_ROWS_INVALID")
    ids={x["item_id"] for x in values}
    need(len(ids)==len(values),"DUPLICATE_POOL_ITEM_ID")
    items=extract(item_file,("ID","ClassID","SubclassID","InventoryType"),ids)
    sparse=extract(sparse_file,("ID","InventoryType","ExpansionID","AllowableClass",
        "StatModifier_bonusStat_0","ItemSet"),ids)
    selectable=[]; conditional=[]
    for v in values:
        iid=v["item_id"];raw=items[iid];extra=sparse[iid]
        slot=integer(raw["InventoryType"])
        need(slot==integer(extra["InventoryType"])==v["inventory_type"],
             "ITEM_SLOT_MISMATCH")
        cl=integer(raw["ClassID"]);subcl=integer(raw["SubclassID"])
        need(cl in (2,4),"NON_EQUIPMENT_ITEM_IN_GEAR_POOL")
        raw_stats=[integer(extra.get(f"StatModifier_bonusStat_{i}","0"))
                   for i in range(10)]
        data={"item_id":iid,"name":v["name"],"slot":slot,"class_id":cl,
            "subclass_id":subcl,"allowed_class_mask":integer(extra["AllowableClass"]),
            "stat_modifier_codes":[x for x in raw_stats if x != 0],
            "item_set_id":v["item_set_id"],"quality":v["quality"],
            "category":v["category"],"direct_item_effect_record":v["direct_item_effect_record"],
            "source_kinds":sorted(set(x["source"] for x in v["acquisition_sources"])),
            "selection_evidence":v["season_selection"]}
        if v["user_selectable_candidate"]:
            selectable.append(data)
        else:
            # Keep only the minimal conditional identification for follow-up
            # season evidence; not a second permanent legacy gear catalog.
            conditional.append({"item_id":iid,"slot":slot,
                "category":v["category"],"source_kinds":data["source_kinds"],
                "reason":v["season_selection"]})
    role_counts=Counter(v["category"] for v in selectable)
    return {"schema":SCHEMA,"status":"COMPACT_CANDIDATE_DB_WITH_PENDING_GAPS",
      "season_build":pool["build"],"expansion_id":pool["expansion_id"],
      "display_season_id":pool["db2_display_season_id"],
      "source_item_count":len(values),
      "current_candidates":selectable,
      "current_candidate_count":len(selectable),
      "conditional_unverified":conditional,
      "conditional_count":len(conditional),
      "current_role_counts":dict(sorted(role_counts.items())),
      "consumable_budget_reference":pool["consumable_budget_reference"],
      "representative_selection_needs_primary_and_four_tier_resolution":True,
      "current_mplus_world_state_confirmed":False,
      "data_is_role_candidates_not_simc_special_effect_certification":True,
      "no_old_catalog_seed":True,
      "native_calls":0}
def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("--pool",type=Path,required=True)
    ap.add_argument("--item",type=Path,required=True)
    ap.add_argument("--item-sparse",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args(argv)
    try:
        result=build(load(args.pool),args.item,args.item_sparse)
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,
                                    separators=(",",":"))+"\n",encoding="utf8")
        print(json.dumps({"status":result["status"],"current":result["current_candidate_count"],
             "conditional":result["conditional_count"],"roles":result["current_role_counts"],
             "native":0},sort_keys=True))
        return 0
    except (GearDbBlocked,KeyError,TypeError,ValueError,OSError) as exc:
        print(json.dumps({"status":"BLOCKED","code":str(exc) if isinstance(exc,GearDbBlocked)
                           else type(exc).__name__}))
        return 3
if __name__=="__main__":raise SystemExit(main())
