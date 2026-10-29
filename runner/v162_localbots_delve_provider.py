#!/usr/bin/env python3
"""v162: Localbots upstream Delve gear pool + exact-build Wago ItemSparse identity.

Current season source is a continuously maintained *independent publisher*,
not a preloaded WEQUIP/legacy gear DB. Wowhead Zah'ran name comparison was
done ONCE in 2026-10-29, not repeated at new seasons. Unknown != absent.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from urllib.parse import urlencode

SCHEMA="v162_localbots_delve_source_v1"
SOURCE_URL="https://raw.githubusercontent.com/balovich-matje/localbots/main/data/delve-loot.json"
WAGO_URL="https://wago.tools/db2/ItemSparse/csv"
MAX_SOURCE_BYTES=250_000
MAX_CSV_BYTES=150_000_000
TIMEOUT=45

class SourceBlocked(ValueError):
    pass

def need(ok,code):
    if not ok: raise SourceBlocked(code)

def canonical(name):
    need(type(name) is str and bool(name.strip()) and len(name)<=200,
         "ITEM_NAME_INVALID")
    return " ".join(name.strip().casefold().replace("\u2019","'").split())

def download(url,limit,*,transport=urlopen):
    need(url==SOURCE_URL or url.startswith(WAGO_URL+"?"),
         "REMOTE_SOURCE_NOT_ALLOWED")
    request=Request(url,headers={
        "User-Agent":"SIMCSecondaryOptimizer-Source-Research/1.0",
        "Accept":"application/json,text/csv"})
    try:
        with transport(request,timeout=TIMEOUT) as response:
            need(response.status==200,"SOURCE_HTTP_NOT_200")
            chunks=[]
            size=0
            while True:
                chunk=response.read(262144)
                if not chunk:break
                size+=len(chunk)
                need(size<=limit,"SOURCE_BYTES_LIMIT")
                chunks.append(chunk)
            return b"".join(chunks)
    except (HTTPError,URLError,TimeoutError,OSError) as err:
        raise SourceBlocked("SOURCE_TRANSPORT_OR_HTTP_ERROR") from err

def source_rows(source_bytes):
    need(type(source_bytes) is bytes and len(source_bytes)<=MAX_SOURCE_BYTES,
         "LOCALBOTS_JSON_TOO_BIG")
    doc=json.loads(source_bytes.decode("utf-8-sig"))
    need(type(doc) is dict and type(doc.get("items")) is list,
         "LOCALBOTS_ITEMS_SHAPE")
    entries=doc["items"]
    need(0<len(entries)<=1000,"LOCALBOTS_ITEMS_LIMIT")
    normalized=set()
    for row in entries:
        need(type(row) is dict and type(row.get("name")) is str,
             "LOCALBOTS_ROW_SHAPE")
        name=canonical(row["name"])
        need(name not in normalized,"LOCALBOTS_DUPLICATE_NAME")
        normalized.add(name)
        if "id" in row:
            need(type(row["id"]) is int and row["id"]>0,
                 "LOCALBOTS_ITEM_ID_INVALID")
    return entries

def sparse_rows(csv_bytes,requested_names,requested_ids):
    need(type(csv_bytes) is bytes and 0<len(csv_bytes)<=MAX_CSV_BYTES,
         "ITEMSPARSE_SIZE")
    try:
        reader=csv.DictReader(io.StringIO(csv_bytes.decode("utf-8-sig")))
        must={"ID","Display_lang","OverallQualityID","InventoryType","ExpansionID"}
        need(must.issubset(reader.fieldnames or []),
             "ITEMSPARSE_FIELDS_MISSING")
        found=[]
        for row in reader:
            item_id=row["ID"].strip()
            if not item_id.isdecimal():continue
            iid=int(item_id)
            name=row["Display_lang"]
            if not name:continue
            cn=canonical(name)
            if iid not in requested_ids and cn not in requested_names:
                continue
            try:
                quality=int(row["OverallQualityID"])
                inventory=int(row["InventoryType"])
                expansion=int(row["ExpansionID"])
            except (ValueError,TypeError):
                continue
            found.append({"item_id":iid,"name":name,
                          "quality":quality,"inventory_type":inventory,
                          "expansion_id":expansion})
        return found
    except (UnicodeError,csv.Error) as e:
        raise SourceBlocked("ITEMSPARSE_CSV_UNREADABLE") from e

def assemble(source_bytes,db2_bytes,*,build,expansion_id=None):
    entries=source_rows(source_bytes)
    need(type(build) is str and bool(build),"DB2_BUILD_REQUIRED")
    need(expansion_id is None or
         (type(expansion_id) is int and expansion_id>0),
         "EXPANSION_ID_INVALID")
    by_name={canonical(x["name"]):x for x in entries}
    by_id={x["id"]:x for x in entries if "id" in x}
    observed=sparse_rows(db2_bytes,set(by_name),set(by_id))
    indexes={}
    direct={}
    for row in observed:
        if row["inventory_type"]<=0:continue
        if expansion_id is not None and row["expansion_id"]!=expansion_id:
            continue
        indexes.setdefault(canonical(row["name"]),[]).append(row)
        direct[row["item_id"]]=row
    resolved=[]
    unresolved=[]
    for entry in entries:
        name=entry["name"]
        if "id" in entry:
            row=direct.get(entry["id"])
            if row is None or canonical(row["name"])!=canonical(name):
                unresolved.append({"name":name,"input_item_id":entry["id"],
                                   "reason":"DB2_ID_NAME_OR_EXPANSION_MISMATCH"})
                continue
            origin="LOCALBOTS_EXPLICIT_ID_DB2_VERIFIED"
        else:
            options=indexes.get(canonical(name),[])
            if not options:
                unresolved.append({"name":name,
                                   "reason":"DB2_EXACT_NAME_NOT_FOUND"})
                continue
            # Same policy as Localbots: higher item quality, then higher ID.
            row=max(options,key=lambda x:(x["quality"],x["item_id"]))
            origin="LOCALBOTS_NAME_DB2_RESOLVED"
        resolved.append({
            "item_id":row["item_id"],"name":name,
            "inventory_type":row["inventory_type"],
            "expansion_id":row["expansion_id"],
            "resolution":origin})
    resolved.sort(key=lambda row:(row["item_id"],canonical(row["name"])))
    seen=set()
    for row in resolved:
        need(row["item_id"] not in seen,"RESOLVED_DUPLICATE_ITEM_ID")
        seen.add(row["item_id"])
    return {
        "schema":SCHEMA,"status":(
            "LOCALBOTS_POOL_FULLY_RESOLVED" if not unresolved else
            "LOCALBOTS_POOL_HAS_UNRESOLVED_NAMES"),
        "source_provider":"Localbots / balovich-matje/localbots",
        "source_url":SOURCE_URL,
        "source_content_sha256":hashlib.sha256(source_bytes).hexdigest(),
        "db2_provider":"wago.tools/DB2/ItemSparse",
        "db2_build":build,
        "db2_content_sha256":hashlib.sha256(db2_bytes).hexdigest(),
        "db2_expansion_id":expansion_id,
        "names_in_source":len(entries),
        "source_explicit_ids":len(by_id),
        "source_name_only":len(entries)-len(by_id),
        "resolved_count":len(resolved),
        "unresolved_count":len(unresolved),
        "items":resolved,
        "unresolved":unresolved,
        "acquisition_kind":"delve",
        "vendor":"Zah'ran",
        "validated_vendor_names_on":"2026-10-29",
        "validated_vendor_names_count":79 if len(entries)==79 and
            set(canonical(e["name"]) for e in entries)==ONE_TIME_20261029 else None,
        "vendor_validation_not_repeated":True,
        "current_season_pool_from_provider_not_proven_server_complete":True,
        "prior_wequip_or_past_item_db_used":False,
        "simc_native_calls":0}

# One-time comparison is historical evidence, not an engine membership gate:
# Source count/hash should NEVER be restricted to the 2026-10-29 79.
ONE_TIME_20261029=set()  # Set is intentionally EMPTY; see docs for 79/79 audit.

def main(argv=None):
    p=argparse.ArgumentParser(description="Localbots → Wago DB2 Delve Item IDs")
    p.add_argument("--source-file",type=Path,
                   help="Pre-fetched GitHub JSON (avoid network)")
    p.add_argument("--item-sparse-csv",type=Path,
                   help="Pre-fetched exact-build ItemSparse.csv (avoid network)")
    p.add_argument("--build",required=True)
    p.add_argument("--expansion-id",type=int)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args(argv)
    try:
        need(bool(args.source_file)==bool(args.item_sparse_csv),
             "LOCAL_FILES_MUST_BE_PAIRED")
        if args.source_file:
            src=args.source_file.read_bytes()
            db2=args.item_sparse_csv.read_bytes()
        else:
            src=download(SOURCE_URL,MAX_SOURCE_BYTES)
            db2=download(WAGO_URL+"?"+urlencode(
                {"build":args.build,"locale":"enUS"}),MAX_CSV_BYTES)
        result=assemble(src,db2,build=args.build,
                        expansion_id=args.expansion_id)
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,indent=2,sort_keys=True,
                             ensure_ascii=False)+"\n",encoding="utf8")
        print(json.dumps({"status":result["status"],
              "source_names":result["names_in_source"],
              "resolved_ids":result["resolved_count"],
              "unresolved":result["unresolved_count"],
              "native":0},sort_keys=True))
        return 0
    except Exception as exc:
        code=str(exc) if isinstance(exc,SourceBlocked) else type(exc).__name__
        print(json.dumps({"status":"BLOCKED","code":code}))
        return 3

if __name__=="__main__":raise SystemExit(main())
