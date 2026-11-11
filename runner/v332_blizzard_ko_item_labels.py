#!/usr/bin/env python3
"""Item-ID-verified, official ko_KR DISPLAY names only. No budget or gear DB writes."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import pathlib
import re
from concurrent.futures import ThreadPoolExecutor

import v155_season_api_probe as blizzard

SCHEMA="v332_official_ko_KR_item_names_v1"
ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=ROOT/"data"/"current_season_product_gear_db.json"
DEST=ROOT/"data"/"current_season_gear_ko_KR_verified.json"
URL_ROOT="https://kr.api.blizzard.com/data/wow/item/"
URL_SUFFIX="?namespace=static-kr&locale=ko_KR"

class LocaleBlocked(ValueError):
    pass

def need(ok,code):
    if not ok:raise LocaleBlocked(code)

def source_sha(path=SOURCE):
    path=pathlib.Path(path)
    need(path.is_file() and path.stat().st_size<=2_000_000,"ITEM_SOURCE_MISSING")
    return hashlib.sha256(path.read_bytes()).hexdigest()

def selected_ids(source=SOURCE):
    import v167_product_season_gear_adapter as catalog
    public=catalog.public_options(catalog.read(source))
    rows=public["choices"]["trinket"]+public["choices"]["special_effect_gear_candidate"]
    ids=sorted({r["item_id"] for r in rows})
    need(1<=len(ids)<=128,"VISIBLE_ITEM_COUNT_OUT_OF_BOUNDS")
    return public["season_build"],ids

def url_for(i):
    need(type(i) is int and 1<=i<=999999999,"INVALID_ITEM_ID")
    return URL_ROOT+str(i)+URL_SUFFIX

def row_from_api(item_id,document):
    need(type(document) is dict and type(document.get("id")) is int and
         document["id"]==item_id,"BLIZZARD_ITEM_ID_MISMATCH")
    name=document.get("name")
    if type(name) is dict:name=name.get("ko_KR")
    need(type(name) is str and 1<=len(name.strip())<=200,
         "BLIZZARD_KO_NAME_UNAVAILABLE")
    canonical=json.dumps(document,ensure_ascii=False,sort_keys=True,
                         separators=(",",":")).encode("utf8")
    return {"item_id":item_id,"name_ko":name.strip(),
            "api_url":url_for(item_id),
            "response_canonical_sha256":hashlib.sha256(canonical).hexdigest()}

def build_document(build,ids,entries,*,catalog_sha):
    ids=sorted(set(ids))
    rows=sorted(entries,key=lambda r:r["item_id"])
    selected={r["item_id"] for r in rows}
    need(selected<=set(ids),"UNREQUESTED_ITEM")
    return {"schema":SCHEMA,"locale":"ko_KR",
            "provider":"BLIZZARD_OFFICIAL_GAME_DATA_API",
            "api_namespace":"static-kr",
            "catalog_build":build,"catalog_sha256":catalog_sha,
            "status":"COMPLETE" if len(selected)==len(ids) else "PARTIAL",
            "requested_item_ids":ids,"items":rows}

def verified_names(document,expected_build,allowed_ids,expected_sha):
    need(type(document) is dict and document.get("schema")==SCHEMA and
         document.get("locale")=="ko_KR" and
         document.get("provider")=="BLIZZARD_OFFICIAL_GAME_DATA_API" and
         document.get("api_namespace")=="static-kr" and
         document.get("catalog_build")==expected_build and
         document.get("catalog_sha256")==expected_sha and
         document.get("status") in ("COMPLETE","PARTIAL"),
         "KO_ITEM_PROVENANCE_MISMATCH")
    need(type(document.get("requested_item_ids")) is list and
         document["requested_item_ids"]==sorted(set(document["requested_item_ids"])) and
         set(document["requested_item_ids"])==set(allowed_ids),
         "KO_ITEM_REQUESTED_SET_DRIFT")
    rows=document.get("items")
    need(type(rows) is list and len(rows)<=128,"KO_ITEM_ROWS_INVALID")
    names={}
    for row in rows:
        need(type(row) is dict and set(row)=={
            "item_id","name_ko","api_url","response_canonical_sha256"},
            "KO_ITEM_ROW_FIELDS")
        i=row["item_id"];name=row["name_ko"];digest=row["response_canonical_sha256"]
        need(type(i) is int and i in allowed_ids and i not in names and
             type(name) is str and 1<=len(name.strip())<=200 and
             name==name.strip() and type(digest) is str and
             re.fullmatch("[a-f0-9]{64}",digest) and
             row["api_url"]==url_for(i),"KO_ITEM_ROW_NOT_VERIFIED")
        names[i]=name
    need(document["status"]==("COMPLETE" if len(names)==len(allowed_ids)
                              else "PARTIAL"),"KO_ITEM_COMPLETENESS_FALSE")
    return names

def installed_names(build,allowed_ids,path=DEST,source=SOURCE):
    path=pathlib.Path(path)
    if not path.is_file():return {}
    try:
        need(not path.is_symlink() and path.stat().st_size<=100_000,
             "KO_ITEM_FILE_UNSAFE")
        document=json.loads(path.read_text(encoding="utf8"))
        return verified_names(document,build,set(allowed_ids),source_sha(source))
    except (OSError,ValueError,TypeError,KeyError,LocaleBlocked):
        # Fail closed for localization; never block already-verified gear choices.
        return {}

def collect(*,destination,source=SOURCE):
    need(os.getenv("P1_KO_ITEM_SOURCE_ONCE")=="1","EXPLICIT_LOCALIZATION_OPT_IN_REQUIRED")
    build,ids=selected_ids(source)
    token=os.getenv("BLIZZARD_ACCESS_TOKEN")
    if not token:
        cid=os.getenv("BLIZZARD_CLIENT_ID","")
        secret=os.getenv("BLIZZARD_CLIENT_SECRET","")
        need(bool(cid and secret),"BLIZZARD_LOCALE_CREDENTIALS_REQUIRED")
        token=blizzard.oauth_token(blizzard.BLIZZARD_TOKEN_URL,cid,secret)
    def get(i):
        try:
            doc=blizzard.request_json(url_for(i),headers={
                "Authorization":"Bearer "+token})
            return row_from_api(i,doc),None
        except Exception as exc:
            return None,{"item_id":i,"error":type(exc).__name__}
    with ThreadPoolExecutor(max_workers=4) as pool:
        observations=list(pool.map(get,ids))
    names=[row for row,error in observations if row is not None]
    errors=[error for row,error in observations if error is not None]
    doc=build_document(build,ids,names,catalog_sha=source_sha(source))
    verified_names(doc,build,set(ids),source_sha(source))
    destination=pathlib.Path(destination)
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(doc,ensure_ascii=False,sort_keys=True,
                       indent=2)+"\n",encoding="utf8")
    for row in names:
        print("V332_KO_ITEM",json.dumps(row,ensure_ascii=False,sort_keys=True),flush=True)
    print("V332_SUMMARY",json.dumps({"status":doc["status"],
        "catalog_build":build,"count":len(names),"expected":len(ids),
        "errors":errors},sort_keys=True),flush=True)
    return doc

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=pathlib.Path)
    x=p.parse_args()
    doc=collect(destination=x.out)
    return 0 if doc["status"]=="COMPLETE" else 3

if __name__=="__main__":raise SystemExit(main())
