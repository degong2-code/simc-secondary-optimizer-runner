#!/usr/bin/env python3
"""v160: small, zero-seed, pinned-build wago.tools DB2 CSV availability probe.

No old item database, WoW/SimC binaries, credentials, legacy sources, or
full-table downloads. HTTP 200 is not sufficient: verify CSV header + rows.
Do not label a CSV as current-season loot solely because it exists.
"""
from __future__ import annotations
import argparse
import csv
import io
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

SCHEMA="v160_zero_seed_wago_db2_csv_probe_v1"
HOST="https://wago.tools/db2/"
BUILD="12.1.5.70575"  # public Retail build tracker, 2026-10-24
LOCALE="enUS"
MAX_READ=32768
TIMEOUT=9
TABLES={
    "JournalTierXInstance":("JournalTierID","JournalInstanceID"),
    "JournalInstance":("ID","Name_lang"),
    "JournalEncounter":("ID","JournalInstanceID"),
    "JournalEncounterItem":("JournalEncounterID","ItemID"),
    "MythicPlusSeasonTrackedMap":("MapChallengeModeID","DisplaySeasonID"),
    "MapChallengeMode":("ID","Name_lang"),
    "Map":("ID","InstanceType","ExpansionID"),
    "CraftingData":("CraftedItemID",),
    "ItemSparse":("ID","Display_lang","ExpansionID",
                  "StatModifier_bonusStat_0"),
}
def csv_preview(payload,required):
    if payload.startswith(b"\\x1f\\x8b"):
        return {"status":"ENCODING_GZIP_NOT_SUPPORTED"}
    try:
        reader=csv.reader(io.StringIO(payload.decode("utf-8-sig",errors="strict")))
        header=next(reader)
        header=[x.strip() for x in header]
        if not header or any(not name for name in header):
            return {"status":"INVALID_CSV_HEADER"}
        missing=[n for n in required if n not in header]
        if missing:
            return {"status":"REQUIRED_COLUMNS_MISSING",
                    "missing_columns":missing,
                    "header_sample":header[:35]}
        return {"status":"CSV_COLUMNS_CONFIRMED",
                "header_sample":header[:35],"header_field_count":len(header),
                "preview_rows":min(2,sum(1 for _ in (next(reader,None),next(reader,None))
                                          if _ is not None))}
    except (ValueError,UnicodeDecodeError,StopIteration,csv.Error):
        return {"status":"NON_CSV_OR_INVALID_UTF8"}
def fetch_header(table,required,*,transport=urlopen,build=BUILD):
    if table not in TABLES or not build or len(build)>40 or any(
       c not in "0123456789." for c in build):
        raise ValueError("INVALID_TABLE_OR_BUILD")
    url=HOST+table+"/csv?"+urlencode({"build":build,"locale":LOCALE})
    request=Request(url,headers={"User-Agent":"SIMCSecondaryOptimizer-DB2-Probe/1.0",
                                 "Accept":"text/csv"})
    try:
        with transport(request,timeout=TIMEOUT) as response:
            status=response.status
            content_type=response.headers.get("Content-Type","")
            data=response.read(MAX_READ)
    except HTTPError as e:
        return {"status":"HTTP_ERROR","http_status":e.code}
    except (URLError,TimeoutError,OSError):
        return {"status":"TRANSPORT_FAILED"}
    if status!=200:
        return {"status":"UNEXPECTED_HTTP_STATUS","http_status":status}
    result=csv_preview(data,required)
    result["http_status"]=status
    result["content_type"]=content_type[:90]
    return result
def run(build=BUILD,*,transport=urlopen):
    outcomes={}
    for table,required in TABLES.items():
        outcomes[table]=fetch_header(table,required,build=build,transport=transport)
    return {
        "schema":SCHEMA,"build":build,"product":"Retail / Midnight",
        "source":"WAGO_TOOLS_DB2_PER_BUILD_CSV",
        "tables":outcomes,"requested_csv_tables":len(outcomes),
        "confirmed_csv_tables":sum(r["status"]=="CSV_COLUMNS_CONFIRMED"
                                   for r in outcomes.values()),
        "no_legacy_item_db_used":True,
        "full_tables_downloaded":False,
        "raid_mplus_crafting_item_ids_extracted":False,
        "delve_loot_pool_extracted":False,
        "vendor_Zahran_inventory_in_DB2_verified":False,
        "simc_native_calls":0}
def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--build",default=BUILD)
    args=p.parse_args(argv)
    if len(args.build)>40 or any(c not in "0123456789." for c in args.build):
        raise SystemExit("INVALID_BUILD")
    result=run(build=args.build)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False,
                                   sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({"status":"PROBE_REPORTED",
                      "csv_columns_confirmed":result["confirmed_csv_tables"],
                      "requested_tables":result["requested_csv_tables"],
                      "native":0},sort_keys=True))
if __name__=="__main__":
    main()
