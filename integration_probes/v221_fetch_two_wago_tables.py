#!/usr/bin/env python3
"""One request: re-use v161's Wago download protocol for two DB2 tables only.

Historical ten-CSV artifact is expired. New raw CSVs remain in the Actions
temporary working directory, not bundled in the runtime or uploaded as output.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen

TABLES=("Item","ItemSparse")
BUILD="12.1.5.70575"
MAX_FILE=210_000_000
MAX_TOTAL=260_000_000

def fetch_two(folder,build=BUILD,transport=urlopen):
    if build!=BUILD:
        raise ValueError("PINNED_BUILD_REQUIRED")
    folder=Path(folder)
    if folder.exists():
        raise ValueError("OUTPUT_FOLDER_ALREADY_EXISTS")
    folder.mkdir(parents=True)
    receipt={"schema":"v161_wago_zero_seed_csv_snapshot_v1",
             "status":"ALL_CSV_DOWNLOADED_NOT_YET_INTERPRETED",
             "build":build,"locale":"enUS","source":"wago.tools/db2",
             "tables":{},"scope":"EPHEMERAL_ITEM_ITEMSPARSE_ONLY",
             "simc_native_calls":0}
    total=0
    for name in TABLES:
        url="https://wago.tools/db2/"+name+"/csv?"+urlencode({
            "build":build,"locale":"enUS"})
        req=Request(url,headers={"User-Agent":"SIMC-Secondary-v221/1.0",
                                 "Accept":"text/csv"})
        length=0
        digest=hashlib.sha256()
        with transport(req,timeout=90) as response:
            if response.status!=200:
                raise ValueError("DB2_HTTP_STATUS:"+name+":"+str(response.status))
            with (folder/(name+".csv")).open("wb") as f:
                while True:
                    chunk=response.read(262144)
                    if not chunk: break
                    length+=len(chunk)
                    if length>MAX_FILE or total+length>MAX_TOTAL:
                        raise ValueError("DB2_TWO_TABLE_BYTE_LIMIT:"+name)
                    f.write(chunk)
                    digest.update(chunk)
        if length==0:
            raise ValueError("DB2_EMPTY_TABLE:"+name)
        total+=length
        receipt["tables"][name]={"bytes":length,"sha256":digest.hexdigest()}
    (folder/"receipt.json").write_text(json.dumps(
        receipt,sort_keys=True,indent=2)+"\n",encoding="utf8")
    return receipt

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--folder",required=True,type=Path)
    args=parser.parse_args()
    r=fetch_two(args.folder)
    print("V221_TWO_TABLE_PINNED_SOURCE_PASS",r["build"],
          list(r["tables"].items()),"NATIVE_0")
