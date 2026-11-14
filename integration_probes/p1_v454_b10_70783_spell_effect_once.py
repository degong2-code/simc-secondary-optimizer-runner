#!/usr/bin/env python3
"""B10 one-shot 70783 SpellEffect raw evidence using ORIGINAL v281 scanner.

Input: already observed v452 source receipt, three real item-on-use SpellIDs,
plus the public separate 1297709 effect-spell research candidate. No game
entitlement, J approval, effect interpreter, Native, reinstall or profile.
"""
from __future__ import annotations
import hashlib
import http.client
import json
import pathlib
import tempfile
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

from runner import v281_consumable_simc_relation as existing

BUILD="12.1.5.70783"
V452_SOURCE=(pathlib.Path(__file__).resolve().parents[1]/
    "docs/development/research_receipts"/
    "p1_v452_b10_real_70783_v280_socket_item_use_source.json")
OUT=pathlib.Path("p1_v454_b10_70783_spell_effect_receipt.json")
SCHEMA="p1_v454_b10_70783_spell_effect_source_only_v1"
# This ID is an external tooltip research candidate, NOT a v280-use ID.
PUBLIC_EFFECT_CANDIDATE=1297709


def inspect():
    source=json.loads(V452_SOURCE.read_text(encoding="utf8"))
    if (source.get("schema")!=
            "p1_v452_b10_real_70783_original_v280_item_use_source_v1"
            or source.get("game_build")!=BUILD
            or source.get("original_workflow_run_id")!=43566234553
            or source.get("J_approved") is not False
            or source.get("source_only") is not True):
        raise ValueError("V454_V452_ORIGINAL_70783_SOURCE_REQUIRED")
    physical=source["physical_item_use_candidates_unadmitted"]
    by_item={v["item_id"]:v["on_use_spell_ids"] for v in physical}
    if by_item!={263897:[1270804],275707:[1309820],
                 276187:[1309139]}:
        raise ValueError("V454_V452_OBSERVED_ITEM_USE_DRIFT")
    watch={s for ids in by_item.values() for s in ids}
    watch.add(PUBLIC_EFFECT_CANDIDATE)
    uri="https://wago.tools/db2/SpellEffect/csv?"+urlencode(
        {"build":BUILD,"locale":"enUS"})
    request=Request(uri,headers={
        "User-Agent":"SIMC-Secondary-v281-B10-SourceResearch/1.0",
        "Accept":"text/csv"})
    with tempfile.TemporaryDirectory(prefix="b10-v454-") as td:
        target=pathlib.Path(td)/"SpellEffect.csv"
        total=0
        sha=hashlib.sha256()
        for attempt in range(2):
            total=0
            sha=hashlib.sha256()
            try:
                with urlopen(request,timeout=90) as response:
                    if response.status!=200:
                        raise ValueError("V454_SPELL_EFFECT_HTTP_NON200")
                    with target.open("wb") as output:
                        while True:
                            chunk=response.read(262144)
                            if not chunk:break
                            total+=len(chunk)
                            if total>existing.SPELL_EFFECT_SIZE_LIMIT:
                                raise ValueError("V454_SPELL_EFFECT_BOUNDED_FILE_REQUIRED")
                            sha.update(chunk)
                            output.write(chunk)
                if not total:
                    raise ValueError("V454_SPELL_EFFECT_SOURCE_EMPTY")
                break
            except http.client.IncompleteRead:
                target.unlink(missing_ok=True)
                if attempt:
                    raise ValueError("V454_SPELL_EFFECT_INCOMPLETE_TWICE") from None
        # v281's ORIGINAL conservative DB2 column and value validation.
        effects=existing.scan_spell_effects(target,watch)
    by_spell={str(s):sorted(
        ({"effect":r["effect"],"effect_index":r["effect_index"],
          "effect_misc_value_0":r["enchant_id"],
          "difficulty_id":r["difficulty_id"]}
         for r in effects if r["spell_id"]==s),
        key=lambda x:(x["difficulty_id"],x["effect_index"]))
        for s in sorted(watch)}
    return {
        "schema":SCHEMA,"status":"REAL_70783_SPELL_EFFECT_ROWS_SOURCE_ONLY",
        "game_build":BUILD,
        "v452_original_run_id":source["original_workflow_run_id"],
        "v452_original_join_sha256":source["original_v280_join_sha256"],
        "v452_item_use_pairs":{str(k):v for k,v in sorted(by_item.items())},
        "spell_effect_raw_sha256":sha.hexdigest(),
        "spell_effect_raw_bytes":total,
        "v281_observed_effects_by_spell_id":by_spell,
        "public_effect_spell_candidate_separate_from_item_use":{
            "spell_id":PUBLIC_EFFECT_CANDIDATE,
            "origin":"PUBLIC_TOOLTIP_REFERENCE_NOT_SOURCE_JOIN",
            "physical_item_link_proved":False},
        "no_effect_mechanism_reimplemented":True,
        "on_use_to_effect_spell_chain_proved":False,
        "target_item_season_eligibility_verified":False,
        "target_item_pvp_eligibility_verified":False,
        "target_item_zero_socket_verified":False,
        "added_socket_count_verified":False,
        "J_approved":False,"environment_ready":False,"ui_selectable":False,
        "source_only":True,"native_calls":0,"dps_calls":0,
        "new_db2_tables":1,"source_download_count":1}

def main():
    payload={"schema":SCHEMA,"status":"SOURCE_PENDING",
             "game_build":BUILD,"J_approved":False,
             "environment_ready":False,"source_only":True,
             "native_calls":0}
    try:
        payload=inspect()
    except (existing.SimCRelationBlocked,HTTPError,URLError,ValueError,
            TypeError,KeyError,OSError) as exc:
        payload["first_missing_source"]=(
            str(exc).split(":",1)[0] if isinstance(exc,ValueError)
            else type(exc).__name__)
    OUT.write_text(json.dumps(payload,ensure_ascii=False,sort_keys=True,
        indent=2,allow_nan=False)+"\n",encoding="utf8")
    print("P1_V454_SPELL_EFFECT",json.dumps({
        "status":payload["status"],"game_build":BUILD,
        "effects":{k:len(v) for k,v in payload.get(
            "v281_observed_effects_by_spell_id",{}).items()},
        "J_approved":False,"native_calls":0},sort_keys=True),flush=True)

if __name__=="__main__":
    main()
