#!/usr/bin/env python3
"""v190: same-build DB2 consumable candidates joined to v189 pinned SimC.

Offline and request-triggered; reuses an EXISTING v161 Item+ItemSparse
snapshot. No HTTP, Native, stat/effect simulation, UI publication or recipe
eligibility guesses. SimC DBC and DB2 must not be silently conflated.
"""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path

SCHEMA="v190_same_build_consumable_item_candidates_v1"
MAX_TABLE=210_000_000
MAX_ROWS=1_000_000
FOOD_CLASS_SUBCLASS=(0,5)
POTION_CLASS_SUBCLASS=(0,1)
class ConsumableJoinBlocked(ValueError):pass
def need(ok,why):
    if not ok:raise ConsumableJoinBlocked(why)
def sha_file(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()
def csvrows(path,required):
    p=Path(path)
    need(p.is_file() and 0<p.stat().st_size<=MAX_TABLE,
         "DB2_TABLE_ABSENT_OR_TOO_LARGE:"+p.name)
    with p.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        need(set(required)<=set(reader.fieldnames or []),
             "DB2_COLUMNS_MISSING:"+p.name)
        for n,row in enumerate(reader):
            need(n<MAX_ROWS,"DB2_TABLE_ROW_LIMIT:"+p.name)
            yield row
def integer(value,code):
    try:return int(value)
    except (ValueError,TypeError):raise ConsumableJoinBlocked(code)
def build(discovered,snapshot_folder,*,expected_build,expansion_id):
    need(type(discovered) is dict and discovered.get("schema")==
         "v189_pinned_simc_effect_registration_candidates_v1" and
         discovered.get("auto_promote_to_user_ui") is False,
         "V189_SOURCE_CANDIDATE_RECEIPT_REQUIRED")
    need(type(expected_build) is str and expected_build.count(".")==3,
         "EXPLICIT_GAME_BUILD_REQUIRED")
    need(type(expansion_id) is int and expansion_id>0,
         "EXPLICIT_EXPANSION_ID_REQUIRED")
    root=Path(snapshot_folder)
    receipt=json.loads((root/"receipt.json").read_text(encoding="utf8"))
    need(receipt.get("schema")=="v161_wago_zero_seed_csv_snapshot_v1" and
         receipt.get("status")=="ALL_CSV_DOWNLOADED_NOT_YET_INTERPRETED" and
         receipt.get("build")==expected_build and receipt.get("locale")=="enUS",
         "V161_SNAPSHOT_BUILD_OR_LOCALE_MISMATCH")
    actual={}
    for table in ("Item","ItemSparse"):
        path=root/(table+".csv")
        recorded=receipt.get("tables",{}).get(table,{})
        need(type(recorded.get("sha256")) is str and
             path.is_file() and
             recorded.get("bytes")==path.stat().st_size and
             sha_file(path)==recorded["sha256"],
             "V161_TABLE_SHA_MISMATCH:"+table)
        actual[table]={"sha256":recorded["sha256"],
                       "bytes":recorded["bytes"]}
    # Keep only consumables of the two legal subclasses, not all items:
    # this avoids duplicating the season equipment DB in memory or artifacts.
    base={}
    for row in csvrows(root/"Item.csv",
                       ("ID","ClassID","SubclassID","InventoryType")):
        iid=integer(row["ID"],"BAD_ITEM_ID")
        family=(integer(row["ClassID"],"BAD_ITEM_CLASS"),
                integer(row["SubclassID"],"BAD_ITEM_SUBCLASS"))
        if family not in (FOOD_CLASS_SUBCLASS,POTION_CLASS_SUBCLASS):continue
        need(iid not in base,"DUPLICATE_ITEM_ID")
        base[iid]={"item_id":iid,"kind":"food" if family==FOOD_CLASS_SUBCLASS
                   else "potion","item_class":family[0],
                   "item_subclass":family[1],
                   "inventory_type":integer(row["InventoryType"],"BAD_INVENTORY_TYPE")}
    found={};selected=[]
    for row in csvrows(root/"ItemSparse.csv",("ID","ExpansionID","Display_lang")):
        iid=integer(row["ID"],"BAD_SPARSE_ID")
        if iid not in base:continue
        need(iid not in found,"DUPLICATE_SPARSE_ID")
        found[iid]=True
        expansion=integer(row["ExpansionID"],"BAD_EXPANSION_ID")
        if expansion!=expansion_id:continue
        name=row["Display_lang"].strip()
        need(name and len(name)<=250,"DB2_CONSUMABLE_NAME_INVALID")
        item=base[iid]
        item.update({"name_enUS":name,"expansion_id":expansion,
            "source":"SAME_BUILD_DB2_ITEM_AND_ITEMSPARSE",
            "simc_dbc_presence":"NOT_CHECKED",
            "simc_token":"UNRESOLVED",
            "effect_handler_spell_join":"NOT_CHECKED",
            "crafting_quality":"UNRESOLVED",
            "real_in_game_obtainability":"NOT_CHECKED",
            "native_acceptance":"NOT_CHECKED",
            "ui_selectable":False})
        selected.append(item)
    selected.sort(key=lambda x:(x["kind"],x["name_enUS"].casefold(),x["item_id"]))
    return {
      "schema":SCHEMA,"status":"DB2_CONSUMABLE_CANDIDATES_PENDING_SIMC_DBC_JOIN",
      "source":{"simc_revision":discovered["source"]["commit"],
        "simc_registration_sha256":discovered["source"]["sha256"],
        "wago_snapshot_build":expected_build,
        "wago_locale":"enUS","expansion_id":expansion_id,
        "tables":actual},
      "counts":{"food_items":sum(x["kind"]=="food" for x in selected),
                "potion_items":sum(x["kind"]=="potion" for x in selected),
                "simc_effect_food_registrations":discovered["counts"]["food_handler_registrations"],
                "simc_effect_potion_registrations":discovered["counts"]["potion_handler_registrations"]},
      "items":selected,
      "unresolved_requirements":[
          "SIMC_COMPILED_DBC_ITEM_PRESENCE_AND_TOKEN_QUALITY",
          "SAME_BUILD_ITEM_EFFECT_SPELL_LINK_FOR_CLASSIFICATION",
          "GAME_RECIPE_ELIGIBILITY_FOR_EMBELLISHMENT_SLOTS",
          "EXACT_PINNED_SIMC_NATIVE_NEW_OPTION_ACCEPTANCE",
          "REAL_KOREAN_LOCALIZED_NAME_TOOLTIP_SOURCE"],
      "automatic_ui_promotion":False,"simc_native_calls":0,
      "preserve_old_runtime_whitelist":True,
      "historical_sessions_modified":False}
def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--v189",type=Path,required=True)
    p.add_argument("--db2-folder",type=Path,required=True)
    p.add_argument("--expected-build",required=True)
    p.add_argument("--expansion-id",type=int,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args(argv)
    source=json.loads(a.v189.read_text("utf8"))
    out=build(source,a.db2_folder,expected_build=a.expected_build,
              expansion_id=a.expansion_id)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,
                                indent=2)+"\n",encoding="utf8")
    print("V190_DB2_CONSUMABLE_CANDIDATES",json.dumps(out["counts"]),
          "NATIVE_0_NOT_UI_PUBLISHED")
    return 0
if __name__=="__main__":raise SystemExit(main())
