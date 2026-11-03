#!/usr/bin/env python3
"""Source-only consumable item -> ItemEffect -> on-use SpellID bridge.

This is a small source stage of the ORIGINAL v216 Environment Build. Reuse
the already sealed ItemXItemEffect from the ordinary-gear stage, fetch only
the missing same-build ItemEffect DB2, and retain all uncertainty about
SimC tokens, oil eligibility, quality and stat magnitude. No new effect
engine, Native call, user publication, or old-season fallback.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import v190_consumable_item_snapshot_join as physical
import v217_stage_execution_engine as stages

SCHEMA = "v280_consumable_item_use_spell_source_join_v1"
STAGED = ("EXECUTED_AND_SEALED", "REUSED_VERIFIED", "RECOVERED_VERIFIED")
OUT = {
    "item_effect": "source/v280_ItemEffect.csv",
    "candidate": "source/v280_consumable_use_spell_candidates.json",
}
MAX_EFFECT_BYTES = 32_000_000
ON_USE_TRIGGER = 0  # item spell trigger ON_USE; other trigger types stay pending

class ItemSpellBlocked(ValueError):
    pass

def need(ok, reason):
    if not ok:
        raise ItemSpellBlocked(reason)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def _rows(raw, required, label):
    need(isinstance(raw, bytes) and 0 < len(raw) <= MAX_EFFECT_BYTES,
         "V280_"+label+"_BYTES_MISSING_OR_TOO_LARGE")
    try:
        stream=io.StringIO(raw.decode("utf-8-sig"))
        reader=csv.DictReader(stream)
        need(set(required) <= set(reader.fieldnames or ()),
             "V280_"+label+"_COLUMNS_MISSING")
        for count, row in enumerate(reader):
            need(count < 1_000_000, "V280_"+label+"_ROW_LIMIT")
            yield row
    except UnicodeError as exc:
        raise ItemSpellBlocked("V280_"+label+"_INVALID_UTF8") from exc

def _id(value, label, *, zero=False):
    need(isinstance(value,str) and value.isdecimal() and
         (int(value)>=0 if zero else int(value)>0),
         "V280_"+label+"_INVALID")
    return int(value)

def join(physical_source, relation_bytes, effect_bytes, *,
         build, relation_sha256, effect_sha256):
    """Exact DB2 foreign-key join; only TriggerType=0 is recorded as on-use.

    No relation SpellID is itself a SimC token, applied weapon enchant,
    highest-quality claim or authorized user choice.
    """
    need(isinstance(physical_source,dict) and
         physical_source.get("schema")==physical.SCHEMA and
         physical_source.get("automatic_ui_promotion") is False and
         physical_source.get("source",{}).get("wago_snapshot_build")==build and
         isinstance(physical_source.get("items"),list),
         "V280_PHYSICAL_SAME_BUILD_SOURCE_REQUIRED")
    need(sha(relation_bytes)==relation_sha256 and
         sha(effect_bytes)==effect_sha256,
         "V280_DB2_SHA_MISMATCH")
    watched={}
    for row in physical_source["items"]:
        need(type(row) is dict and type(row.get("item_id")) is int and
             row.get("kind") in ("food","potion","flask","item_enhancement") and
             row.get("ui_selectable") is False,
             "V280_PHYSICAL_ROW_INVALID")
        if row["kind"] in ("flask","item_enhancement"):
            need(row["item_id"] not in watched,"V280_DUPLICATE_PHYSICAL_ID")
            watched[row["item_id"]]=row
    links={item_id:set() for item_id in watched}
    for row in _rows(relation_bytes,("ItemID","ItemEffectID"),"RELATION"):
        item_id=_id(row["ItemID"],"RELATION_ITEM_ID")
        if item_id in links:
            links[item_id].add(_id(row["ItemEffectID"],"RELATION_EFFECT_ID"))
    effect_ids={value for bucket in links.values() for value in bucket}
    effects={}
    for row in _rows(effect_bytes,("ID","SpellID","TriggerType"),"EFFECT"):
        effect_id=_id(row["ID"],"EFFECT_ID")
        if effect_id not in effect_ids:
            continue
        need(effect_id not in effects,"V280_DUPLICATE_EFFECT_ID")
        effects[effect_id]={
            "item_effect_id":effect_id,
            "spell_id":_id(row["SpellID"],"SPELL_ID",zero=True),
            "trigger_type":_id(row["TriggerType"],"TRIGGER_TYPE",zero=True)}
    enriched=[]
    matches=0
    unresolved=0
    for row in physical_source["items"]:
        copy=dict(row)
        if row["item_id"] in watched:
            ids=sorted(links[row["item_id"]])
            details=[effects[x] for x in ids if x in effects]
            on_use=sorted({e["spell_id"] for e in details
                           if e["trigger_type"]==ON_USE_TRIGGER and
                           e["spell_id"]>0})
            missing=sorted(set(ids)-set(effects))
            copy["item_effect_source"]={
                "item_effect_ids":ids,
                "observed_effects":details,
                "missing_item_effect_ids":missing,
                "on_use_spell_ids":on_use,
                "status":("EXACT_DB2_ITEM_TO_ON_USE_SPELL_SOURCE_ONLY"
                          if on_use and not missing else
                          "ITEM_USE_SPELL_RELATION_PENDING")}
            matches+=bool(on_use and not missing)
            unresolved+=not bool(on_use and not missing)
            # SimC input is NOT guessed from an ItemEffect SpellID.
            need(copy["simc_token"]=="UNRESOLVED" and
                 copy["ui_selectable"] is False,
                 "V280_PREMATURE_ITEM_SELECTION")
        enriched.append(copy)
    result=dict(physical_source)
    result["items"]=enriched
    result["item_use_spell_join"]={
        "schema":SCHEMA,"game_build":build,
        "relation_sha256":relation_sha256,
        "item_effect_sha256":effect_sha256,
        "candidate_count":len(watched),
        "exact_on_use_source_count":matches,
        "pending_count":unresolved,
        "source_only":True,"simc_effect_token_join_verified":False,
        "highest_quality_verified":False,
        "weapon_and_hand_applicability_verified":False,
        "F":None,"O":None,"environment_ready":False,
        "native_calls":0}
    result["automatic_ui_promotion"]=False
    return result

def pending(reason):
    return {"schema":SCHEMA,"status":"ITEM_USE_SPELL_SOURCE_PENDING",
            "reason":reason,"candidate_path":None,
            "network_calls_by_stage":0,"native_calls":0,
            "F":None,"O":None,"environment_ready":False}

def collect(*, stage_root, build, fresh_gear, consumables, transport=None):
    """Seal the ONE additional DB2 table and joined source in v217.

    Existing v254 ItemXItemEffect receipt is reused, not downloaded again.
    Existing v279/v190 immutable source is never overwritten.
    """
    root=Path(stage_root).resolve()
    gear_stage=(fresh_gear or {}).get("source_stage") or {}
    consumable_stage=(consumables or {}).get("source_stage") or {}
    if (gear_stage.get("status") not in STAGED or
            consumable_stage.get("status") not in STAGED or
            not (consumables or {}).get("candidate_path")):
        return pending("V280_V254_OR_V279_SEALED_INPUT_PENDING")
    relation_relative=gear_stage.get("output_paths",{}).get("effect")
    need(type(relation_relative) is str and
         not Path(relation_relative).is_absolute() and
         ".." not in Path(relation_relative).parts,
         "V280_V254_RELATION_PATH_INVALID")
    relation=root/relation_relative
    candidate=Path(consumables["candidate_path"]).resolve()
    need(relation.is_file() and not relation.is_symlink() and
         relation.is_relative_to(root) and
         candidate.is_file() and not candidate.is_symlink() and
         candidate.is_relative_to(root),
         "V280_V254_V279_SOURCE_NOT_IN_STAGE")
    raw_source=candidate.read_bytes()
    need(0<len(raw_source)<=5_000_000,"V280_V190_SOURCE_TOO_LARGE")
    physical_source=json.loads(raw_source)
    need(physical_source.get("schema")==physical.SCHEMA and
         physical_source.get("source",{}).get("wago_snapshot_build")==build,
         "V280_V190_BUILD_DRIFT")
    # The original v217 stage already verified its outputs. Read this small
    # relation once on a fresh join to validate FK values; no network replay.
    relation_sha=sha(relation.read_bytes())
    calls=[0]
    def execute():
        url="https://wago.tools/db2/ItemEffect/csv?"+urlencode(
            {"build":build,"locale":"enUS"})
        req=Request(url,headers={
            "User-Agent":"SIMC-Secondary-Environment-ItemEffect/1.0",
            "Accept":"text/csv"})
        calls[0]+=1
        with (urlopen if transport is None else transport)(req,timeout=75) as resp:
            need(resp.status==200,"V280_ITEM_EFFECT_HTTP_NON_200")
            raw=resp.read(MAX_EFFECT_BYTES+1)
        need(0<len(raw)<=MAX_EFFECT_BYTES,"V280_ITEM_EFFECT_HTTP_SIZE_LIMIT")
        output=root/OUT["item_effect"]
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_bytes(raw)
        joined=join(physical_source,relation.read_bytes(),raw,build=build,
                    relation_sha256=relation_sha,effect_sha256=sha(raw))
        (root/OUT["candidate"]).write_text(
            json.dumps(joined,sort_keys=True,ensure_ascii=False,
                       indent=2,allow_nan=False)+"\n",encoding="utf8")
    def validate(paths):
        doc=json.loads(paths["candidate"].read_text("utf8"))
        info=doc.get("item_use_spell_join",{})
        return (doc.get("schema")==physical.SCHEMA and
                info.get("schema")==SCHEMA and
                info.get("game_build")==build and
                info.get("relation_sha256")==relation_sha and
                info.get("item_effect_sha256")==
                    sha(paths["item_effect"].read_bytes()) and
                info.get("source_only") is True and
                info.get("F") is None and info.get("O") is None and
                doc.get("automatic_ui_promotion") is False and
                all(x.get("ui_selectable") is False
                    for x in doc.get("items",[])))
    code=stages.module_dependency_fingerprint(
        [Path(__file__),Path(physical.__file__),Path(stages.__file__)])
    try:
        stage=stages.execute_stage(
            root=root,stage_id="fresh-consumable-item-use-spell-source",
            stage_version="v280-first-party-itemeffect-db2-v1",
            inputs={"game_build":build,
                    "v254_stage_sha256":gear_stage.get("receipt_sha256"),
                    "v279_stage_sha256":consumable_stage.get("receipt_sha256"),
                    "v190_candidate_sha256":sha(raw_source),
                    "item_x_item_effect_sha256":relation_sha,
                    "code_sha256":code["sha256"]},
            outputs=OUT,execute=execute,validate=validate)
    except (stages.StageExecutionBlocked,ItemSpellBlocked,
            OSError,ValueError,KeyError,TypeError) as exc:
        return {**pending(str(exc).split(":",1)[0]),
                "network_calls_by_stage":calls[0]}
    doc=json.loads((root/OUT["candidate"]).read_text("utf8"))
    return {"schema":SCHEMA,
            "status":"ITEM_USE_SPELL_SOURCE_JOINED_UNADMITTED",
            "candidate_path":str((root/OUT["candidate"]).resolve()),
            "counts":doc["item_use_spell_join"],
            "source_stage":{k:v for k,v in stage.items() if k!="result"},
            "network_calls_by_stage":calls[0],"native_calls":0,
            "F":None,"O":None,"environment_ready":False}
