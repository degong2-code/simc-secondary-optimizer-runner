#!/usr/bin/env python3
"""One-off pinned Retail Wago CSV snapshot, zero existing gear catalog.

Only fixed wago.tools tables and build, bounded disk/HTTP; saves exact CSV
snapshot as ephemeral GitHub artifact, not to repository or product runtime.
"""
from __future__ import annotations
import argparse,hashlib,json,os,re,zipfile
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

BUILD="12.1.5.70575"
TABLES=("JournalTierXInstance","JournalInstance","JournalEncounter",
        "JournalEncounterItem","MythicPlusSeasonTrackedMap",
        "MapChallengeMode","Map","CraftingData","ItemSparse","Item")
MAX_TOTAL=320_000_000
MAX_PER=210_000_000
def snapshot(folder,build=BUILD,fetch=urlopen):
    if not re.fullmatch(r"\d+\.\d+\.\d+\.\d+",build):
        raise ValueError("INVALID_BUILD")
    folder.mkdir(parents=True,exist_ok=True)
    receipt={"schema":"v161_wago_zero_seed_csv_snapshot_v1",
             "build":build,"locale":"enUS","source":"wago.tools/db2",
             "legacy_item_ids_imported":False,"simc_native_calls":0,
             "tables":{}}
    budget=0
    for table in TABLES:
        url="https://wago.tools/db2/"+table+"/csv?"+urlencode({
             "build":build,"locale":"enUS"})
        req=Request(url,headers={"User-Agent":"SIMC-Secondary-DB2-Research/1.0",
                                 "Accept":"text/csv"})
        sha=hashlib.sha256()
        received=0
        with fetch(req,timeout=90) as resp:
            if resp.status!=200:raise ValueError(table+"_HTTP_"+str(resp.status))
            with (folder/(table+".csv")).open("wb") as out:
                while True:
                    chunk=resp.read(262144)
                    if not chunk:break
                    received+=len(chunk)
                    if received>MAX_PER or budget+received>MAX_TOTAL:
                        raise ValueError("CSV_DOWNLOAD_LIMIT_EXCEEDED")
                    sha.update(chunk)
                    out.write(chunk)
        budget+=received
        receipt["tables"][table]={"bytes":received,"sha256":sha.hexdigest()}
    receipt["total_csv_bytes"]=budget
    receipt["status"]="ALL_CSV_DOWNLOADED_NOT_YET_INTERPRETED"
    (folder/"receipt.json").write_text(json.dumps(
        receipt,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf8")
    # Separate archive inside output directory, only CSV and receipt
    with zipfile.ZipFile(folder/"db2-snapshot.zip","w",zipfile.ZIP_DEFLATED,
                         compresslevel=5) as archive:
        for table in TABLES:
            archive.write(folder/(table+".csv"),arcname=table+".csv")
        archive.write(folder/"receipt.json",arcname="receipt.json")
    return receipt
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--build",default=BUILD)
    args=p.parse_args()
    try:
        data=snapshot(args.out,build=args.build)
        print(json.dumps({"status":data["status"],"tables":len(data["tables"]),
                 "csv_bytes":data["total_csv_bytes"],"native":0}))
    except Exception as e:
        print(json.dumps({"status":"BLOCKED","code":type(e).__name__,
            "message":str(e) if isinstance(e,ValueError) else "REQUEST_FAILED"}))
        raise SystemExit(3)
if __name__=="__main__":main()
