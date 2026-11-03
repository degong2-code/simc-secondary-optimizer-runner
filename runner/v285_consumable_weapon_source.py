#!/usr/bin/env python3
"""P3-CR: one SAME-BUILD SpellEquippedItems join to existing v281 source.

No weapon effects are reimplemented, no Native or quality certification.
Only original DB2 SpellID → equipped-item masks is attached, preserving the
entire v281 source candidate and its immutable v284 receipt unchanged.
"""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import v217_stage_execution_engine as stages
import v190_consumable_item_snapshot_join as physical
import v281_consumable_simc_relation as relation

SCHEMA="v285_same_build_consumable_spell_weapon_source_v1"
STAGE="fresh-consumable-weapon-inventory-source"
VERSION="v285-spell-equipped-items-source-v1"
OUTPUTS={"equipped":"source/v285_SpellEquippedItems.csv",
         "candidate":"source/v285_consumable_weapon_masks.json"}
HEADERS={"ID","SpellID","EquippedItemClass",
         "EquippedItemInvTypes","EquippedItemSubclass"}
MAX_FILE=8_000_000
STAGED=frozenset(("EXECUTED_AND_SEALED","REUSED_VERIFIED",
                  "RECOVERED_VERIFIED"))

class WeaponSourceBlocked(ValueError):pass
def need(ok,reason):
    if not ok:raise WeaponSourceBlocked(reason)
def sha(data):
    return hashlib.sha256(data).hexdigest()
def pending(reason):
    return {"schema":SCHEMA,"status":"WEAPON_MASK_SOURCE_PENDING",
            "reason":reason,"candidate_path":None,
            "network_calls_by_stage":0,"native_calls":0,
            "F":None,"O":None,"environment_ready":False}

def scan(path,wanted):
    need(type(wanted) is set and all(type(x) is int and x>0
                                    for x in wanted),
         "V285_WANTED_SPELL_IDS_INVALID")
    found=[];seen=set()
    with Path(path).open(encoding="utf-8-sig",newline="") as stream:
        reader=csv.DictReader(stream)
        need(HEADERS.issubset(set(reader.fieldnames or ())),
             "V285_REAL_SPELL_EQUIPPED_COLUMNS_DRIFT")
        for row in reader:
            sid=row["SpellID"]
            if sid not in {str(x) for x in wanted}:
                continue
            need(all(row[k].lstrip("-").isdigit() for k in HEADERS),
                 "V285_REAL_SPELL_EQUIPPED_NUMERIC_FIELDS_INVALID")
            ident=int(row["ID"])
            need(ident not in seen,"V285_REAL_SPELL_EQUIPPED_DUPLICATE_ID")
            seen.add(ident)
            found.append({
                "row_id":ident,"spell_id":int(sid),
                "equipped_item_class":int(row["EquippedItemClass"]),
                "inventory_type_mask":int(row["EquippedItemInvTypes"]),
                "weapon_subclass_mask":int(row["EquippedItemSubclass"])})
    return sorted(found,key=lambda x:(x["spell_id"],x["row_id"]))

def attach(source,rows,build):
    need(type(source) is dict and source.get("schema")==physical.SCHEMA
         and source.get("automatic_ui_promotion") is False
         and source.get("source",{}).get("wago_snapshot_build")==build
         and source.get("simc_relation_source",{}).get("schema")==relation.SCHEMA
         and type(source.get("items")) is list and type(rows) is list,
         "V285_EXACT_V281_SAME_BUILD_SOURCE_REQUIRED")
    by_spell={}
    for row in rows:
        need(type(row) is dict and
             all(type(row.get(k)) is int for k in (
                "row_id","spell_id","equipped_item_class",
                "inventory_type_mask","weapon_subclass_mask")),
             "V285_SPELL_EQUIPPED_ROW_INVALID")
        by_spell.setdefault(row["spell_id"],[]).append(row)
    items=[];exact=0
    for raw in source["items"]:
        item=dict(raw)
        if item.get("kind")=="item_enhancement":
            simc=item.get("simc_temporary_enchant_source") or {}
            links=simc.get("exact_source_matches") or []
            spells={x.get("on_use_spell_id") for x in links
                    if type(x) is dict}
            matches=[r for spell in spells for r in by_spell.get(spell,[])]
            unique={(r["equipped_item_class"],
                     r["inventory_type_mask"],
                     r["weapon_subclass_mask"]) for r in matches}
            if (simc.get("status")==
                  "EXACT_SIMC_TEMP_ENCHANT_ID_CANDIDATE"
                and bool(matches) and len(unique)==1
                and all(r["equipped_item_class"]==2
                        and r["inventory_type_mask"]>0
                        and r["weapon_subclass_mask"]>0
                        for r in matches)):
                cls,inventory,subclass=next(iter(unique))
                status="EXACT_SAME_BUILD_WEAPON_MASK_SOURCE_ONLY"
                exact+=1
            else:
                cls=inventory=subclass=None
                status="WEAPON_MASK_OR_SIMC_EFFECT_SOURCE_PENDING"
            item["weapon_spell_equipped_source"]={
                "status":status,
                "matched_spell_ids":sorted(int(s) for s in spells
                                           if type(s) is int),
                "source_rows":matches,
                "equipped_item_class":cls,
                "inventory_type_mask":inventory,
                "weapon_subclass_mask":subclass,
                "source_only":True,
                "selected_actual_weapon_verified":False,
                "weapon_and_hand_applicability_verified":False,
                "same_effect_quality_group_verified":False,
            }
        need(item.get("ui_selectable") is False,
             "V285_PREMATURE_ITEM_REGISTRATION")
        items.append(item)
    output={**source,"items":items,
            "weapon_equipped_source":{
                "schema":SCHEMA,"game_build":build,
                "exact_mask_join_candidates":exact,
                "source_only":True,"native_calls":0,
                "O":None,"F":None,"environment_ready":False}}
    output["automatic_ui_promotion"]=False
    return output

def collect(*,stage_root,build,consumables,transport=None):
    root=Path(stage_root).resolve()
    source=consumables or {}
    stage=source.get("source_stage",{}) if type(source) is dict else {}
    if (stage.get("status") not in STAGED
         or not source.get("candidate_path")):
        return pending("V285_SEALED_V281_SOURCE_PENDING")
    input_path=Path(source["candidate_path"])
    need(input_path.is_file() and not input_path.is_symlink()
         and input_path.resolve().is_relative_to(root)
         and 0<input_path.stat().st_size<=5_000_000,
         "V285_V281_SOURCE_CANDIDATE_UNSAFE")
    raw=input_path.read_bytes()
    original=json.loads(raw)
    need(original.get("simc_relation_source",{}).get("schema")==relation.SCHEMA
         and original.get("source",{}).get("wago_snapshot_build")==build,
         "V285_V281_SAME_BUILD_PROOF_MISSING")
    wanted={r["on_use_spell_id"] for item in original["items"]
            if item.get("kind")=="item_enhancement"
            for r in item.get("simc_temporary_enchant_source",{}).get(
                "exact_source_matches",[]) if type(r) is dict
            and type(r.get("on_use_spell_id")) is int}
    if not wanted:
        return pending("V285_NO_EXACT_TEMPORARY_ENCHANT_USE_SPELLS")
    calls=[0]
    def execute():
        uri="https://wago.tools/db2/SpellEquippedItems/csv?"+urlencode(
             {"build":build,"locale":"enUS"})
        req=Request(uri,headers={"Accept":"text/csv",
                    "User-Agent":"SIMC-Secondary-v285-WeaponMasks/1.0"})
        calls[0]+=1
        target=root/OUTPUTS["equipped"]
        target.parent.mkdir(parents=True,exist_ok=True)
        total=0
        with (urlopen if transport is None else transport)(req,timeout=75) as resp:
            need(resp.status==200,"V285_WAGO_SOURCE_HTTP_NON200")
            with target.open("wb") as stream:
                while True:
                    part=resp.read(262144)
                    if not part:break
                    total+=len(part)
                    need(total<=MAX_FILE,"V285_WAGO_SOURCE_SIZE_CAP")
                    stream.write(part)
        need(total>0,"V285_WAGO_SOURCE_EMPTY")
        result=attach(original,scan(target,wanted),build)
        (root/OUTPUTS["candidate"]).write_text(
            json.dumps(result,ensure_ascii=False,sort_keys=True,
                       indent=2,allow_nan=False)+"\n",encoding="utf8")
    def validate(outputs):
        candidate=json.loads(outputs["candidate"].read_text("utf8"))
        return (candidate.get("schema")==physical.SCHEMA
                and candidate.get("weapon_equipped_source",{}).get(
                    "schema")==SCHEMA
                and candidate.get("weapon_equipped_source",{}).get(
                    "game_build")==build
                and candidate.get("automatic_ui_promotion") is False
                and all(x.get("ui_selectable") is False
                        for x in candidate.get("items",[])))
    try:
        fingerprint=stages.module_dependency_fingerprint([
            Path(__file__),Path(stages.__file__)])
        receipt=stages.execute_stage(
            root=root,stage_id=STAGE,stage_version=VERSION,
            inputs={"game_build":build,
                    "v281_stage_sha256":stage["receipt_sha256"],
                    "v281_candidate_sha256":sha(raw),
                    "source_code_sha256":fingerprint["sha256"]},
            outputs=OUTPUTS,execute=execute,validate=validate)
    except (stages.StageExecutionBlocked,WeaponSourceBlocked,
            OSError,ValueError,TypeError,KeyError) as exc:
        return {**pending(str(exc).split(":",1)[0]),
                "network_calls_by_stage":calls[0]}
    result=json.loads((root/OUTPUTS["candidate"]).read_text("utf8"))
    return {"schema":SCHEMA,
            "status":"EXACT_SAME_BUILD_WEAPON_MASK_SOURCE_ONLY",
            "candidate_path":str((root/OUTPUTS["candidate"]).resolve()),
            "source_stage":{k:v for k,v in receipt.items() if k!="result"},
            "counts":result["weapon_equipped_source"],
            "network_calls_by_stage":calls[0],"native_calls":0,
            "F":None,"O":None,"environment_ready":False}
