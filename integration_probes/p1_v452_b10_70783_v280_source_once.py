#!/usr/bin/env python3
"""One bounded real 70783 source observation for B10 via ORIGINAL v161/v189/v190/v280.

This is NOT a new product collector or entitlement/effect oracle. On success
retain only item/use-spell IDs, source byte SHA and honest pending qualifiers.
No Native, DPS, v212 install, UI option promotion, or season-wide game DB.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from runner import v161_wago_db2_snapshot as wago
from runner import v189_simc_consumable_embellishment_discovery as simc
from runner import v190_consumable_item_snapshot_join as physical
from runner import v280_consumable_item_use_spell_source as joined

BUILD="12.1.5.70783"
PINNED_REVISION="c20e2ad52e4c33711f74272309a5748125175fe8"
EXPANSION_ID=11
OUTPUT=pathlib.Path("p1_v452_b10_70783_socket_source_receipt.json")
MAX_ITEM_RELATION=32_000_000
SCHEMA="p1_v452_b10_real_70783_original_v280_item_use_source_v1"
SOCKET_NAME_TOKENS=("jewelbinder","jeweler's setting","jewelers setting")

def fetch_existing_relation(name):
    """Bounded missing-table Wago fetch, identical URL and hash rules to v280."""
    url="https://wago.tools/db2/"+name+"/csv?"+urlencode(
        {"build":BUILD,"locale":"enUS"})
    req=Request(url,headers={"User-Agent":"SIMC-Secondary-B10-OriginalSource/1.0",
                             "Accept":"text/csv"})
    with urlopen(req,timeout=75) as response:
        if response.status!=200:
            raise ValueError("B10_"+name+"_HTTP_NON200")
        raw=response.read(MAX_ITEM_RELATION+1)
    if not 0<len(raw)<=MAX_ITEM_RELATION:
        raise ValueError("B10_"+name+"_BOUNDED_TABLE_REQUIRED")
    return raw

def run():
    receipt={
        "schema":SCHEMA,"game_build":BUILD,
        "pinned_simc_revision":PINNED_REVISION,
        "status":"SOURCE_PENDING",
        "physical_item_use_candidates_unadmitted":[],
        "source_table_sha256":{},
        "source_only":True,
        "user_item_applicability_verified":False,
        "pvp_exclusion_verified":False,
        "added_socket_spell_effect_verified":False,
        "actual_bonus_socket_count_verified":False,
        "J_approved":False,
        "ui_selectable":False,"environment_ready":False,
        "native_calls":0,"dps_calls":0,"installed_environment":False}
    raw=simc.read_source(commit=PINNED_REVISION)
    discovered=simc.discover(raw,PINNED_REVISION)
    receipt["source_table_sha256"]["simc_pinned_unique_gear"]=simc.sha(raw)
    with tempfile.TemporaryDirectory(prefix="p1-v452-b10-") as temp:
        # Reuse v161 with only the original v190 required two tables.
        folder=pathlib.Path(temp)/"wago"
        old=wago.TABLES
        try:
            wago.TABLES=("Item","ItemSparse")
            snapshot=wago.snapshot(folder,build=BUILD,make_archive=False)
        finally:
            wago.TABLES=old
        receipt["source_table_sha256"].update({
            name:row["sha256"] for name,row in snapshot["tables"].items()})
        candidate=physical.build(discovered,folder,expected_build=BUILD,
                                  expansion_id=EXPANSION_ID)
        relation=fetch_existing_relation("ItemXItemEffect")
        effect=fetch_existing_relation("ItemEffect")
        hashes={
            "ItemXItemEffect":hashlib.sha256(relation).hexdigest(),
            "ItemEffect":hashlib.sha256(effect).hexdigest()}
        receipt["source_table_sha256"].update(hashes)
        # v280 original exact FK join only. Never infer usable socket from
        # name, item-to-spell identity, a PTR tooltip or parser acceptance.
        result=joined.join(candidate,relation,effect,build=BUILD,
                           relation_sha256=hashes["ItemXItemEffect"],
                           effect_sha256=hashes["ItemEffect"])
        receipt["original_v280_join_sha256"]=hashlib.sha256(
            json.dumps(result,ensure_ascii=False,sort_keys=True,
                       separators=(",",":")).encode("utf8")).hexdigest()
        receipt["v280_total_considered"]=result[
            "item_use_spell_join"]["candidate_count"]
        hints=[]
        for row in result["items"]:
            if row.get("kind")!="item_enhancement":
                continue
            label=row.get("name_enUS")
            if not isinstance(label,str) or not any(
                    token in label.casefold().replace("’","'")
                    for token in SOCKET_NAME_TOKENS):
                continue
            use=row.get("item_effect_source") or {}
            if (use.get("status")!=
                    "EXACT_DB2_ITEM_TO_ON_USE_SPELL_SOURCE_ONLY" or
                    not use.get("on_use_spell_ids")):
                continue
            hints.append({
                "item_id":row["item_id"],"name_enUS":label,
                "expansion_id":row["expansion_id"],
                "on_use_spell_ids":use["on_use_spell_ids"],
                "item_class":row["item_class"],
                "item_subclass":row["item_subclass"],
                "ui_selectable":False,
                "same_season_use_applicability_verified":False})
        receipt["physical_item_use_candidates_unadmitted"]=sorted(
            hints,key=lambda v:v["item_id"])
        receipt["status"]=(
            "REAL_SAME_BUILD_V280_SOURCE_HINTS_UNADMITTED"
            if hints else
            "REAL_SAME_BUILD_V280_NO_MATCH_IN_SOURCE_SCOPE")
    return receipt

def main():
    result={
        "schema":SCHEMA,"game_build":BUILD,
        "status":"NOT_EXECUTED","source_only":True,
        "physical_item_use_candidates_unadmitted":[],
        "J_approved":False,"environment_ready":False,
        "native_calls":0}
    try:
        result=run()
    except (ValueError,TypeError,KeyError,RuntimeError,OSError,
            HTTPError,URLError,
            simc.DiscoveryBlocked,physical.ConsumableJoinBlocked,
            joined.ItemSpellBlocked) as exc:
        result["status"]="SOURCE_PENDING"
        result["first_missing_source"]=(
            str(exc).split(":",1)[0] if isinstance(exc,ValueError)
            else type(exc).__name__)
    OUTPUT.write_text(json.dumps(result,ensure_ascii=False,
        sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf8")
    print("P1_V452_B10_REAL_SOURCE",json.dumps({
        "status":result["status"],"build":BUILD,
        "candidate_count":len(result[
            "physical_item_use_candidates_unadmitted"]),
        "source_hash_count":len(result.get("source_table_sha256",{})),
        "native_calls":0,"J_approved":False},sort_keys=True),flush=True)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
