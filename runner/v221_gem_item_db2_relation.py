#!/usr/bin/env python3
"""v221: verified same-build gem-property -> physical item ID DB2 join.

Reuses ONLY the existing v161 Item/ItemSparse CSV snapshot and the v213
catalog's source-preserved gem_property_id rows. No collection, Native, HTTP,
effect simulation, or user-option publication. ItemSparse.Gem_properties is
the DB2 foreign key to GemProperties::ID, not a gem item ID itself.

A SIMC-generated DBC build differing from the Wago DB2 build is PENDING,
not an exact cross-build match. This stage proves item/property identity,
NOT socket eligibility, SimC runtime acceptance or CHMV budget handling.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

import v213_source_to_catalog as v213

SCHEMA="v221_verified_gem_property_item_source_join_v1"
MAX_TABLE=210_000_000
MAX_ROWS=1_000_000
GEM_CLASS=3


class GemJoinBlocked(ValueError):
    pass


def require(ok,code):
    if not ok:
        raise GemJoinBlocked(code)


def _sha_file(path):
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def _verify_db2(root,expected_build,*,verified_tables=None):
    receipt_path=root/"receipt.json"
    require(receipt_path.is_file() and not receipt_path.is_symlink() and
            0<receipt_path.stat().st_size<=100_000,
            "DB2_RECEIPT_MISSING_OR_INVALID")
    receipt=json.loads(receipt_path.read_text(encoding="utf8"))
    require(type(receipt) is dict and
            receipt.get("schema")=="v161_wago_zero_seed_csv_snapshot_v1" and
            receipt.get("status")=="ALL_CSV_DOWNLOADED_NOT_YET_INTERPRETED" and
            receipt.get("build")==expected_build and
            receipt.get("locale")=="enUS" and
            receipt.get("source")=="wago.tools/db2",
            "DB2_SNAPSHOT_BUILD_OR_SOURCE_MISMATCH")
    files={}
    if verified_tables is not None:
        require(type(verified_tables) is dict and
                set(verified_tables)=={"Item","ItemSparse"},
                "V217_VERIFIED_TABLE_SET_MISMATCH")
    for name in ("Item","ItemSparse"):
        p=root/(name+".csv")
        meta=receipt.get("tables",{}).get(name,{})
        require(p.is_file() and not p.is_symlink() and
                0<p.stat().st_size<=MAX_TABLE and
                type(meta) is dict and meta.get("bytes")==p.stat().st_size and
                type(meta.get("sha256")) is str,
                "DB2_TABLE_SHA_OR_SIZE_MISMATCH:"+name)
        if verified_tables is None:
            require(_sha_file(p)==meta["sha256"],
                    "DB2_TABLE_SHA_OR_SIZE_MISMATCH:"+name)
        else:
            require(verified_tables[name]=={
                "sha256":meta["sha256"],"bytes":meta["bytes"]},
                "V217_VERIFIED_TABLE_PROVENANCE_MISMATCH:"+name)
        files[name]={"bytes":meta["bytes"],"sha256":meta["sha256"]}
    return files


def _rows(path,columns):
    with path.open("r",encoding="utf-8-sig",newline="") as stream:
        reader=csv.DictReader(stream)
        require(type(reader.fieldnames) is list and
                len(reader.fieldnames)==len(set(reader.fieldnames)) and
                set(columns)<=set(reader.fieldnames),
                "DB2_REQUIRED_COLUMNS_NOT_PRESENT:"+path.name)
        for index,row in enumerate(reader):
            require(index<MAX_ROWS,"DB2_ROW_LIMIT:"+path.name)
            require(None not in row and
                    all(row.get(key) is not None for key in columns),
                    "DB2_CSV_ROW_INVALID:"+path.name)
            yield row


def _integer(value,code,positive=False):
    try:
        number=int(value)
    except (TypeError,ValueError) as exc:
        raise GemJoinBlocked(code) from exc
    require(number>0 if positive else number>=0,code)
    return number


def _source_properties(source):
    try:
        v213.verify_catalog(source)
    except (ValueError,TypeError,KeyError) as exc:
        raise GemJoinBlocked("V213_SOURCE_CATALOG_INVALID") from exc
    raw=source["catalog"]["gem_properties"].get("source_records")
    expected=source["catalog"]["gem_properties"]["source_count"]
    require(type(raw) is list and len(raw)==expected,
            "V213_GEM_SOURCE_KEYS_NOT_RETAINED")
    mapping={}
    duplicate=0
    for row in raw:
        require(type(row) is dict and
                set(row)=={"gem_property_id","enchant_id","color_mask",
                           "minimum_ilevel"} and
                all(type(value) is int and value>=0 for value in row.values()) and
                row["gem_property_id"]>0,
                "V213_GEM_PROPERTY_RECORD_INVALID")
        key=row["gem_property_id"]
        if key in mapping:
            duplicate+=1
            require(mapping[key]==row,"V213_GEM_PROPERTY_KEY_CONFLICT")
        else:
            mapping[key]=row
    return mapping,duplicate


def join(source_catalog,snapshot_folder,*,verified_tables=None):
    """Return ONLY exact same-build physical item/property links.

    Empty matches are not proof that no gems exist. All unresolved data is
    retained separately, with no user admission or DPS cache mutation.
    """
    properties,source_duplicates=_source_properties(source_catalog)
    build=source_catalog["game_build"]
    generated=source_catalog["source_provenance"]["v191"][
        "simc_generated_sources"]["gem_property"]["source_build"]
    root=Path(snapshot_folder)
    tables=_verify_db2(root,build,verified_tables=verified_tables)
    base={
        "schema":SCHEMA,
        "game_build":build,
        "simc_generated_gem_source_build":generated,
        "simc_revision":source_catalog["simc_revision"],
        "v213_manifest_sha256":source_catalog["manifest_sha256"],
        "db2_tables":tables,
        "gem_property_source_rows":
            source_catalog["catalog"]["gem_properties"]["source_count"],
        "gem_property_distinct_keys":len(properties),
        "gem_property_duplicate_rows":source_duplicates,
        "joins":[],
        "exact_link_count":0,
        "automatic_ui_promotion":False,
        "simc_native_calls":0,
        "network_calls":0,
        "historical_cache_modified":False,
        "effect_proc_dps_owner":"SimC",
    }
    if generated!=build:
        return {**base,
                "status":"PENDING_GENERATED_SIMC_DBC_AND_DB2_BUILD_MISMATCH",
                "unresolved":["SAME_BUILD_GEM_PROPERTY_IDENTITY_REQUIRED"]}
    item_ids=set()
    for row in _rows(root/"Item.csv",("ID","ClassID")):
        item_id=_integer(row["ID"],"DB2_ITEM_ID_INVALID",positive=True)
        # We need to detect duplicates for candidate gem class items only.
        if _integer(row["ClassID"],"DB2_ITEM_CLASS_INVALID")==GEM_CLASS:
            require(item_id not in item_ids,"DB2_DUPLICATE_GEM_ITEM_ID")
            item_ids.add(item_id)
    matched={}
    for row in _rows(root/"ItemSparse.csv",
                     ("ID","Gem_properties","ExpansionID")):
        item_id=_integer(row["ID"],"DB2_SPARSE_ITEM_ID_INVALID",positive=True)
        if item_id not in item_ids:
            continue
        require(item_id not in matched,"DB2_DUPLICATE_GEM_ITEMSPARSE_ID")
        # Count each candidate at most once, including unresolved property.
        property_id=_integer(row["Gem_properties"],
                             "DB2_GEM_PROPERTY_ID_INVALID")
        expansion=_integer(row["ExpansionID"],"DB2_EXPANSION_INVALID")
        matched[item_id]=True
        if property_id not in properties or expansion!=source_catalog["expansion_id"]:
            continue
        property_row=properties[property_id]
        base["joins"].append({
            "item_id":item_id,
            "gem_property_id":property_id,
            "enchant_id":property_row["enchant_id"],
            "color_mask":property_row["color_mask"],
            "minimum_ilevel":property_row["minimum_ilevel"],
            "expansion_id":expansion,
            "status":"EXACT_DB2_ITEMSPARSE_GEM_PROPERTY_RELATION",
            "socket_eligibility":"NOT_YET_VERIFIED",
            "simc_input_acceptance":"NOT_YET_VERIFIED",
            "chmv_accounting":"NOT_YET_VERIFIED",
            "ui_selectable":False,
        })
    base["joins"].sort(key=lambda x:x["item_id"])
    base["exact_link_count"]=len(base["joins"])
    return {**base,
            "status":"SOURCE_ITEM_PROPERTY_LINKS_ONLY_NOT_USER_ADMITTED",
            "unresolved":[
                "EXACT_SOCKET_APPLICABILITY_AND_SIMC_INPUT_NOT_YET_VERIFIED",
                "CHMV_BUDGET_OWNERSHIP_NOT_YET_VERIFIED",
            ]}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v213-source",type=Path,required=True)
    parser.add_argument("--db2-folder",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        source=json.loads(args.v213_source.read_text(encoding="utf8"))
        result=join(source,args.db2_folder)
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print("V221_GEM_RELATION_BLOCKED",type(exc).__name__,str(exc))
        return 3
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,
                                   indent=2)+"\n",encoding="utf8")
    print("V221_GEM_RELATION",result["status"],
          "EXACT_LINKS",result["exact_link_count"],"NATIVE0_NO_ADMISSION")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
