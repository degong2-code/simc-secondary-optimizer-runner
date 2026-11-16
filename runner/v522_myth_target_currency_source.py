#!/usr/bin/env python3
"""Optional same-build Myth target-ilvl source via the EXISTING v161 Wago DB2.

Not a second gear/season engine. Preserve the ten v161/v217 required CSV
identities and immutable receipts: CurrencyTypes has its OWN capped source
file and receipt, and never modifies the original snapshot/stage/caches.

A matched Myth currency description is a source-only default candidate.
The selected active RAID must come from the original authenticated v163 join;
a highest item drop, generic ItemSparse.ItemLevel or stale currency is unsafe.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import pathlib
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:
    from . import v161_wago_db2_snapshot as wago
    from . import v163_zero_seed_db2_join as season_join
except ImportError:
    import v161_wago_db2_snapshot as wago
    import v163_zero_seed_db2_join as season_join

SCHEMA="v522_optional_myth_target_currency_source_v1"
TABLE="CurrencyTypes"
FILE="CurrencyTypes.csv"
RECEIPT="CurrencyTypes.target_source_receipt.json"
MAX_BYTES=16_000_000
MAX_ROWS=100_000
# Exact upgrade sentence only: do NOT take the crafting range or Mythic
# special raid-reward equivalents as the normal Myth-track maximum.
UPGRADE=re.compile(
    r"\bUsed to upgrade (?:Myth(?: track)? (?:equipment|gear)|"
    r"(?:equipment|gear) on the Myth track) in "
    r"(?P<season>[A-Za-z][A-Za-z0-9 '\\-]{3,90}?) "
    r"up to item levels? (?P<low>\d{2,4})\s*[-–]\s*"
    r"(?P<high>\d{2,4})\b",re.IGNORECASE)

class TargetSourceBlocked(ValueError):
    pass

def need(ok,code):
    if not ok:
        raise TargetSourceBlocked(code)

def url(build):
    return ("https://wago.tools/db2/"+TABLE+"/csv?"+
            urlencode({"build":build,"locale":"enUS"}))

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda:fh.read(262144),b""):
            h.update(chunk)
    return h.hexdigest()

def base_receipt(folder,build):
    need(type(build) is str and
         re.fullmatch(r"\d+(?:\.\d+){3}",build) is not None,
         "TARGET_BUILD_FORMAT_INVALID")
    need(not folder.is_symlink() and folder.is_dir(),
         "TARGET_WAGO_FOLDER_INVALID")
    base=folder/"receipt.json"
    need(base.is_file() and not base.is_symlink() and
         base.stat().st_size<=65536,"TARGET_ORIGINAL_V161_RECEIPT_REQUIRED")
    raw=base.read_bytes()
    try:
        doc=json.loads(raw)
    except (ValueError,UnicodeError) as exc:
        raise TargetSourceBlocked("TARGET_V161_RECEIPT_INVALID") from exc
    need(doc.get("schema")=="v161_wago_zero_seed_csv_snapshot_v1"
         and doc.get("build")==build and doc.get("locale")=="enUS"
         and set(doc.get("tables",{}))==set(wago.TABLES),
         "TARGET_ORIGINAL_V161_BUILD_OR_TABLES_MISMATCH")
    return hashlib.sha256(raw).hexdigest()

def verify(folder,build):
    folder=pathlib.Path(folder)
    base_sha=base_receipt(folder,build)
    csv_path=folder/FILE
    receipt=folder/RECEIPT
    need(csv_path.is_file() and not csv_path.is_symlink() and
         receipt.is_file() and not receipt.is_symlink() and
         receipt.stat().st_size<=4096,
         "TARGET_CURRENCY_RECEIPT_OR_CSV_MISSING")
    doc=json.loads(receipt.read_text(encoding="utf8"))
    need(doc.get("schema")==SCHEMA and
         doc.get("build")==build and doc.get("locale")=="enUS" and
         doc.get("source_url")==url(build) and
         doc.get("original_v161_receipt_sha256")==base_sha and
         type(doc.get("bytes")) is int and
         0<doc["bytes"]<=MAX_BYTES and
         csv_path.stat().st_size==doc["bytes"] and
         type(doc.get("sha256")) is str and
         re.fullmatch(r"[0-9a-f]{64}",doc["sha256"]) is not None and
         sha(csv_path)==doc["sha256"],
         "TARGET_CURRENCY_SOURCE_SHA_OR_BUILD_MISMATCH")
    return doc

def collect(folder,build,*,fetch=urlopen):
    """Optional ONE same-build HTTP CSV on a verified v161 Wago folder.

    Never added to v161.TABLES, old stage dependency hashes, or mandatory
    source receipt. An already sealed identical copy costs 0 network calls.
    """
    folder=pathlib.Path(folder)
    original_sha=base_receipt(folder,build)
    path=folder/FILE
    receipt=folder/RECEIPT
    if path.exists() or receipt.exists() or path.is_symlink() or receipt.is_symlink():
        doc=verify(folder,build)
        return {**doc,"reused_same_build":True,"network_calls_now":0,
                "native_calls":0}
    endpoint=url(build)
    req=Request(endpoint,headers={"User-Agent":"SIMC-Secondary-DB2-Research/1.0",
                                  "Accept":"text/csv"})
    temp=folder/(FILE+".partial")
    need(not temp.exists() and not temp.is_symlink(),
         "TARGET_CURRENCY_PARTIAL_FILE_EXISTS")
    h=hashlib.sha256()
    length=0
    try:
        with fetch(req,timeout=90) as response:
            need(getattr(response,"status",200)==200,
                 "TARGET_CURRENCY_HTTP_STATUS_INVALID")
            with temp.open("xb") as out:
                while True:
                    chunk=response.read(262144)
                    if not chunk:break
                    length+=len(chunk)
                    need(length<=MAX_BYTES,"TARGET_CURRENCY_CSV_SIZE_LIMIT")
                    h.update(chunk)
                    out.write(chunk)
        need(length>0,"TARGET_CURRENCY_CSV_EMPTY")
        # A 200 response can be an HTML error page. Reject its CSV schema
        # BEFORE sealing the content-addressed optional source; otherwise
        # a bad one-time response would poison the same-season cache.
        try:
            with temp.open(encoding="utf-8-sig",newline="") as csv_file:
                header=csv.DictReader(csv_file).fieldnames
        except (UnicodeError,csv.Error) as exc:
            raise TargetSourceBlocked(
                "TARGET_CURRENCY_DOWNLOAD_NOT_UTF8_CSV") from exc
        need(header is not None and
             {"ID","Name_lang","Description_lang"}<=set(header),
             "TARGET_CURRENCY_DOWNLOAD_COLUMNS_INVALID")
        doc={"schema":SCHEMA,"build":build,"locale":"enUS",
             "source_url":endpoint,"original_v161_receipt_sha256":original_sha,
             "bytes":length,"sha256":h.hexdigest(),
             "interpretation":"SOURCE_ONLY_NOT_ENVIRONMENT_READY"}
        temp.replace(path)
        try:
            receipt.write_text(json.dumps(doc,sort_keys=True)+"\n",encoding="utf8")
        except Exception:
            path.unlink(missing_ok=True)
            raise
        return {**doc,"reused_same_build":False,"network_calls_now":1,
                "native_calls":0}
    finally:
        temp.unlink(missing_ok=True)

def myth_target_candidate(folder,build,*,active_season_scope):
    """Read only exact Wago CSV + verified v163 current RAID association.

    No numeric ID assumptions, no max(ItemLevel) guess. Return PENDING for
    missing/ambiguous currency so the caller can request manual target ilvl.
    """
    doc=verify(folder,build)
    scope=active_season_scope
    need(type(scope) is dict and
         scope.get("source_basis")=="LIVE_WCL_ACTIVE_ZONES_AND_SAME_BUILD_DB2"
         and type(scope.get("db2_display_season_id")) is int
         and scope["db2_display_season_id"]>0 and
         type(scope.get("raid_zone")) is str
         and len(scope["raid_zone"])>=5,
         "TARGET_ACTIVE_SEASON_RAID_JOIN_REQUIRED")
    raid=season_join.norm(scope["raid_zone"])
    matches=[]
    with (pathlib.Path(folder)/FILE).open(
            encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        need(reader.fieldnames is not None and
             {"ID","Name_lang","Description_lang"}<=set(reader.fieldnames),
             "TARGET_CURRENCY_REQUIRED_COLUMNS_MISSING")
        for i,row in enumerate(reader):
            need(i<MAX_ROWS,"TARGET_CURRENCY_ROW_LIMIT")
            description=row.get("Description_lang")
            if type(description) is not str:continue
            # Currency descriptions may contain escaped line breaks.
            normalized=description.replace("\\n"," ").replace("\n"," ")
            parsed=UPGRADE.search(normalized)
            if parsed is None or raid not in season_join.norm(normalized):
                continue
            item_id=row.get("ID")
            low,high=int(parsed["low"]),int(parsed["high"])
            need(type(item_id) is str and item_id.isdecimal() and
                 int(item_id)>0 and 1<=low<=high<=1000,
                 "TARGET_CURRENCY_MATCH_NUMERIC_INVALID")
            matches.append({
                "currency_id":int(item_id),"currency_name":row["Name_lang"],
                "season_label":parsed["season"].strip(),
                "myth_range_low":low,"target_ilevel":high})
    # Actual 12.1.5.70783 Wago CurrencyTypes returns BOTH 3441 and 3446
    # for Myth Mistcrest. Their normal Myth range is identical (321..334);
    # one variant additionally names a separate crafting range (318..331).
    # Duplicate IDs are not conflicting *target levels*. Group only by
    # independently parsed season label AND normal Myth track bounds.
    # Different caps/season labels remain ambiguous; never take max(...).
    groups={}
    for candidate in matches:
        key=(season_join.norm(candidate["season_label"]),
             candidate["myth_range_low"],candidate["target_ilevel"])
        groups.setdefault(key,[]).append(candidate)
    result={
        "schema":"v522_myth_target_from_active_raid_currency_v1",
        "status":"SOURCE_CANDIDATE_ONLY_NOT_INSTALLED",
        "game_build":build,
        "selected_db2_display_season_id":scope["db2_display_season_id"],
        "selected_active_raid":scope["raid_zone"],
        "currency_csv_sha256":doc["sha256"],
        "original_v161_receipt_sha256":doc["original_v161_receipt_sha256"],
        "candidate_count":len(matches),
        "distinct_season_myth_range_count":len(groups),
        "target_ilevel":None,"native_calls":0,"network_calls":0,
        "environment_ready":False,
        "needs_user_target_ilevel":len(groups)!=1}
    if len(groups)==1:
        unique=sorted(next(iter(groups.values())),
                      key=lambda row:row["currency_id"])
        canonical=unique[0]
        ids=sorted({row["currency_id"] for row in unique})
        result.update({
            "season_label":canonical["season_label"],
            "myth_range_low":canonical["myth_range_low"],
            "target_ilevel":canonical["target_ilevel"],
            "currency_ids":ids,
            "currency_id":ids[0] if len(ids)==1 else None,
            "currency_name":(
                canonical["currency_name"]
                if len({row["currency_name"] for row in unique})==1
                else None),
            "equivalent_id_count":len(ids),
            "duplicate_myth_ranges_deduplicated":len(unique)>1})
        result["status"]="MYTH_TRACK_TARGET_SOURCE_MATCH_UNADMITTED"
    else:
        result["reason"]=(
            "TARGET_MYTH_CURRENCY_NOT_LINKED_TO_ACTIVE_RAID"
            if not matches else "TARGET_MYTH_CURRENCY_AMBIGUOUS")
    return result
