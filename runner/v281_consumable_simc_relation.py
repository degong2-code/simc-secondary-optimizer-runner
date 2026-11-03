#!/usr/bin/env python3
"""P3-CL: exact ID-based consumable → SimC source relation in normal v216.

Reuse v280's actual ItemID→on-use SpellID, sealed v275 temporary enchant
entries, and optional v256/v230 exact compiled item DBC. Fetch only the
missing same-build SpellEffect table, once, as a v217 source stage. A spell
effect 54 with misc enchant ID can be matched to the exact SimC generated
enchant ID, not to an oil by item name. Flask SimC input remains a candidate
until real SimC acceptance and quality/effect proof. Never publish F/O/UI.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import v190_consumable_item_snapshot_join as physical
import v191_unified_season_data_update as season
import v217_stage_execution_engine as stages
import v229_simc_only_source_seed as seed
import v230_simc_item_metadata as metadata
import v280_consumable_item_use_spell_source as use_spells

SCHEMA="v281_consumable_simc_relation_source_only_v1"
STAGED=frozenset(("EXECUTED_AND_SEALED","REUSED_VERIFIED","RECOVERED_VERIFIED"))
SPELL_EFFECT_SIZE_LIMIT=150_000_000
OUT={"spell_effect":"source/v281_SpellEffect.csv",
     "candidate":"source/v281_simc_consumable_relations.json"}
# SpellEffect effect 54 = ENCHANT_ITEM_TEMPORARY. This is a DB2 identity
# relation only; neither a game weapon-eligibility nor a stat measurement.
TEMPORARY_ENCHANT_EFFECT=54
TOKEN_CHARS=re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")

class SimCRelationBlocked(ValueError):
    pass

def need(ok, reason):
    if not ok:
        raise SimCRelationBlocked(reason)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def pending(reason):
    return {"schema":SCHEMA,"status":"CONSUMABLE_SIMC_RELATION_SOURCE_PENDING",
            "reason":reason,"candidate_path":None,
            "network_calls_by_stage":0,"native_calls":0,
            "F":None,"O":None,"environment_ready":False}

def _safe_path(root, path):
    need(type(path) is str,"V281_SOURCE_FILE_PATH_REQUIRED")
    p=Path(path)
    need(not p.is_symlink() and p.is_file() and
         p.resolve().is_relative_to(root),
         "V281_SOURCE_FILE_OUTSIDE_SEALED_STAGE")
    return p

def _int(value,name,allow_negative=False):
    need(type(value) is str and
         re.fullmatch(r"-?\d+" if allow_negative else r"\d+",value) is not None,
         "V281_"+name+"_INVALID")
    out=int(value)
    need(allow_negative or out>=0,"V281_"+name+"_NEGATIVE")
    return out

def _normalize_simc_item_name(value):
    """Conservative candidate spelling, never verified input acceptance."""
    if type(value) is not str or not value.isascii():
        return None
    text=re.sub(r"[^a-z0-9]+","_",value.lower()).strip("_")
    return text if TOKEN_CHARS.fullmatch(text) is not None else None

def correlate(source, spell_rows, temporary_rows, *, build, flask_dbc_rows=()):
    """Attach only exact SpellEffect enchant ID / exact SimC item ID facts.

    Missing source rows, multi-effect use spells, generic item enhancements
    and ambiguous temporary enchant IDs remain explicitly unadmitted.
    """
    need(type(source) is dict and source.get("schema")==physical.SCHEMA
         and source.get("automatic_ui_promotion") is False
         and source.get("source",{}).get("wago_snapshot_build")==build
         and source.get("item_use_spell_join",{}).get("schema")==use_spells.SCHEMA
         and type(source.get("items")) is list,
         "V281_EXACT_V280_SOURCE_REQUIRED")
    need(type(temporary_rows) is list and all(type(x) is dict and
         type(x.get("enchant_id")) is int and x["enchant_id"]>0
         and type(x.get("quality_rank")) is int
         and type(x.get("effect_spell_id")) is int
         and type(x.get("simc_token")) is str for x in temporary_rows),
         "V281_PINNED_TEMPORARY_ROWS_REQUIRED")
    by_enchant={}
    for row in temporary_rows:
        by_enchant.setdefault(row["enchant_id"],[]).append(row)
    by_flask={}
    for row in flask_dbc_rows:
        need(type(row) is dict and type(row.get("item_id")) is int
             and row["item_id"]>0 and row.get("class_id")==0
             and row.get("subclass_id")==3
             and type(row.get("crafting_quality")) is int,
             "V281_SIMC_FLASK_ITEM_DBC_INVALID")
        need(row["item_id"] not in by_flask,
             "V281_DUPLICATE_SIMC_FLASK_ID")
        by_flask[row["item_id"]]=row
    wanted={}
    for row in source["items"]:
        need(type(row) is dict and type(row.get("item_id")) is int
             and row["item_id"]>0 and row.get("ui_selectable") is False,
             "V281_SOURCE_ITEM_INVALID")
        if row.get("kind") not in ("flask","item_enhancement"):
            continue
        spell=row.get("item_effect_source",{})
        need(type(spell) is dict and
             type(spell.get("on_use_spell_ids")) is list
             and all(type(s) is int and s>0 for s in spell["on_use_spell_ids"]),
             "V281_ITEM_USE_SPELL_ROWS_REQUIRED")
        for sid in spell["on_use_spell_ids"]:
            wanted[sid]=[]
    need(type(spell_rows) is list,"V281_SPELL_EFFECT_ROWS_REQUIRED")
    for record in spell_rows:
        need(type(record) is dict and
             type(record.get("spell_id")) is int and
             type(record.get("effect")) is int and
             type(record.get("enchant_id")) is int,
             "V281_SPELL_EFFECT_ROW_INVALID")
        if record["spell_id"] in wanted:
            wanted[record["spell_id"]].append(record)
    enriched=[];oil_linked=flask_exact=0
    for item in source["items"]:
        row=dict(item)
        if item.get("kind") not in ("flask","item_enhancement"):
            enriched.append(row);continue
        origin=item["item_effect_source"]
        spell_ids=origin["on_use_spell_ids"]
        effects=sorted([e for sid in spell_ids for e in wanted.get(sid,[])],
                       key=lambda x:(x["spell_id"],x["effect"],x["enchant_id"]))
        row["spell_effect_source"]={
            "on_use_spell_ids":list(spell_ids),
            "observed_spell_effects":effects,
            "status":"SAME_BUILD_SPELL_EFFECT_SOURCE_ONLY" if effects
                     else "SPELL_EFFECT_SOURCE_PENDING"}
        if item["kind"]=="flask":
            dbc=by_flask.get(item["item_id"])
            if dbc is None:
                row["simc_flask_item_source"]={
                    "status":"SIMC_FLASK_EXACT_ITEM_DBC_PENDING",
                    "simc_flask_option_candidate":None}
            else:
                token=_normalize_simc_item_name(dbc.get("name"))
                rank=dbc["crafting_quality"]
                option=(token+("_"+str(rank) if rank else "")
                        if token is not None and rank>=0 else None)
                row["simc_flask_item_source"]={
                    "status":("SIMC_ITEM_ID_CLASS_SUBCLASS_CANDIDATE"
                              if option is not None else
                              "SIMC_ITEM_ID_FOUND_TOKEN_UNRESOLVED"),
                    "simc_item_id":dbc["item_id"],
                    "simc_name_enUS":dbc.get("name"),
                    "crafting_quality":rank,
                    "simc_flask_option_candidate":option,
                    "simc_option_native_verified":False,
                    "same_effect_quality_group_verified":False}
                flask_exact+=option is not None
        else:
            # Wago spell effect MUST explicitly carry the exact temporary
            # enchant ID. Same-looking spell name and token alone are invalid.
            links=[];not_simc=[];conflicted=[]
            for effect in effects:
                if (effect["effect"]!=TEMPORARY_ENCHANT_EFFECT or
                        effect["enchant_id"]<=0 or
                        effect.get("difficulty_id",0)!=0):
                    continue
                source_rows=by_enchant.get(effect["enchant_id"],[])
                if len(source_rows)==1:
                    match=source_rows[0]
                    links.append({
                        "on_use_spell_id":effect["spell_id"],
                        "enchant_id":match["enchant_id"],
                        "quality_rank":match["quality_rank"],
                        "simc_effect_spell_id":match["effect_spell_id"],
                        "simc_token":match["simc_token"],
                        "exact_join":"SPELL_EFFECT_54_MISC_TO_SIMC_TEMP_ENCHANT_ID"})
                elif not source_rows:
                    not_simc.append(effect["enchant_id"])
                else:
                    conflicted.append(effect["enchant_id"])
            links=sorted(links,key=lambda x:(x["on_use_spell_id"],x["enchant_id"]))
            # A matched ID is a candidate only when unambiguous. Multiple
            # different valid enchant IDs are not safely interchangeable.
            one_enchant=len({x["enchant_id"] for x in links})==1
            row["simc_temporary_enchant_source"]={
                "status":("EXACT_SIMC_TEMP_ENCHANT_ID_CANDIDATE"
                          if links and one_enchant and not conflicted and not not_simc
                          and origin.get("status")==
                              "EXACT_DB2_ITEM_TO_ON_USE_SPELL_SOURCE_ONLY"
                          else "TEMP_ENCHANT_SIMC_RELATION_PENDING"),
                "exact_source_matches":links,
                "enchant_ids_without_simc_row":sorted(set(not_simc)),
                "ambiguous_simc_enchant_ids":sorted(set(conflicted)),
                "weapon_oil_identity_verified":False,
                "weapon_and_hand_applicability_verified":False,
                "same_effect_quality_group_verified":False,
                "simc_option_native_verified":False}
            oil_linked+=row["simc_temporary_enchant_source"]["status"]==(
                "EXACT_SIMC_TEMP_ENCHANT_ID_CANDIDATE")
            need(row.get("weapon_oil_identity")=="NOT_ESTABLISHED",
                 "V281_GENERIC_ENHANCEMENT_PREMATURE_OIL_CLASSIFICATION")
        need(row.get("ui_selectable") is False and
             row.get("simc_token")=="UNRESOLVED",
             "V281_PREMATURE_SIMC_SELECTION")
        enriched.append(row)
    result=dict(source)
    result["items"]=enriched
    result["simc_relation_source"]={
        "schema":SCHEMA,"game_build":build,
        "matched_temporary_enchant_source_items":oil_linked,
        "matched_simc_flask_id_candidates":flask_exact,
        "registered_temporary_enchant_rows":len(temporary_rows),
        "source_only":True,"highest_quality_verified":False,
        "weapon_oil_identity_verified":False,
        "weapon_and_hand_applicability_verified":False,
        "simc_token_native_verified":False,
        "F":None,"O":None,"environment_ready":False,"native_calls":0}
    result["automatic_ui_promotion"]=False
    return result

def scan_spell_effects(csv_path, wanted):
    """Stream same-build SpellEffect once, keep only watched SpellIDs."""
    need(type(wanted) is set and all(type(s) is int and s>0 for s in wanted),
         "V281_WATCHED_USE_SPELL_SET_INVALID")
    out=[];seen=set()
    with Path(csv_path).open("r",encoding="utf-8-sig",newline="") as stream:
        reader=csv.DictReader(stream)
        need({"SpellID","Effect","EffectIndex","EffectMiscValue_0",
              "DifficultyID"}<=set(reader.fieldnames or ()),
             "V281_SPELL_EFFECT_DB2_COLUMNS_DRIFT")
        for n,row in enumerate(reader):
            need(n<2_500_000,"V281_SPELL_EFFECT_ROW_LIMIT")
            sid=_int(row["SpellID"],"SPELL_ID")
            if sid not in wanted:continue
            effect=_int(row["Effect"],"EFFECT_CODE")
            misc=_int(row["EffectMiscValue_0"],"MISC_VALUE_0",allow_negative=True)
            difficulty=_int(row["DifficultyID"],"DIFFICULTY_ID")
            idx=(_int(row["EffectIndex"],"EFFECT_INDEX")
                 if "EffectIndex" in row else n)
            key=(sid,difficulty,idx)
            need(key not in seen,"V281_DUPLICATE_SPELL_EFFECT_INDEX")
            seen.add(key)
            out.append({"spell_id":sid,"effect":effect,
                        "enchant_id":misc,"effect_index":idx,
                        "difficulty_id":difficulty})
    return out

def _flask_from_sealed_item_data(full_seed, build):
    """Existing v256 + v229 SHA identity, original v230 item parser only."""
    if type(full_seed) is not dict or not full_seed.get("source_dir"):
        return [],"SIMC_FULL_ITEM_DATA_SOURCE_PENDING",None
    root=Path(full_seed["source_dir"])
    need(not root.is_symlink() and root.is_dir(),
         "V281_SIMC_ITEM_DATA_FOLDER_INVALID")
    receipt=seed.bounded_read(root/seed.RECEIPT,2_000_000)
    doc=json.loads(receipt)
    need(doc.get("schema")==seed.SCHEMA
         and doc.get("simc_generated_build")==build
         and doc.get("item_data_present") is True
         and doc.get("provenance_tree_blob_authenticated") is True
         and doc.get("receipt_sha256")==seed.digest(
             seed.canonical({k:v for k,v in doc.items()
                             if k!="receipt_sha256"}).encode("utf8")),
         "V281_SIMC_ITEM_DBC_RECEIPT_INVALID")
    raw=seed.bounded_read(root/"item_data.inc",seed.MAX_ITEM_FILE)
    meta=doc.get("source_files",{}).get("item_data.inc",{})
    need(meta.get("sha256")==seed.digest(raw) and
         meta.get("git_blob_sha1")==seed.git_blob(raw),
         "V281_SIMC_ITEM_DBC_SOURCE_DRIFT")
    parsed=metadata.parse_exact(
        raw,build=build,candidate_filter=lambda fields:
            fields[11]=="0" and fields[12]=="3",candidate_limit=5000)
    return parsed["items"],"SIMC_EXACT_FLASK_ITEM_ID_ROWS",meta["sha256"]

def _full_seed_identity(full_seed,build):
    """Verify small v229 receipt on cache hits, no 26MB reparse."""
    if type(full_seed) is not dict or not full_seed.get("source_dir"):
        return None
    root=Path(full_seed["source_dir"])
    need(root.is_dir() and not root.is_symlink() and
         full_seed.get("source_stage",{}).get("status") in STAGED,
         "V281_FULL_SIMC_ITEM_SEAL_MISSING")
    raw=seed.bounded_read(root/seed.RECEIPT,2_000_000)
    doc=json.loads(raw)
    expected=seed.digest(seed.canonical({
        k:v for k,v in doc.items() if k!="receipt_sha256"}).encode("utf8"))
    need(doc.get("schema")==seed.SCHEMA
         and doc.get("receipt_sha256")==expected
         and doc.get("simc_generated_build")==build
         and doc.get("item_data_present") is True,
         "V281_FULL_SIMC_ITEM_IDENTITY_DRIFT")
    item=doc.get("source_files",{}).get("item_data.inc",{})
    need(type(item.get("sha256")) is str and len(item["sha256"])==64
         and (root/"item_data.inc").is_file()
         and not (root/"item_data.inc").is_symlink(),
         "V281_FULL_SIMC_ITEM_SOURCE_MISSING")
    return item["sha256"]


def collect(*,stage_root,build,consumables,compiler_source,
            full_simc_item_source=None,transport=None):
    """One missing Wago SpellEffect only; v280/v275/v256 are reused."""
    root=Path(stage_root).resolve()
    src=consumables or {}
    compiler=compiler_source or {}
    if (src.get("source_stage",{}).get("status") not in STAGED
        or compiler.get("source_stage",{}).get("status") not in STAGED
        or not src.get("candidate_path") or not compiler.get("source_dir")):
        return pending("V281_V280_OR_V275_SOURCE_PENDING")
    if not (type(full_simc_item_source) is dict and
            full_simc_item_source.get("source_dir")):
        return pending("V281_V256_FULL_SIMC_ITEM_DATA_PENDING")
    item_sha=_full_seed_identity(full_simc_item_source,build)
    candidate=_safe_path(root,src["candidate_path"])
    temp_path=_safe_path(root,str(Path(compiler["source_dir"])/"temporary_enchant.inc"))
    raw=candidate.read_bytes()
    need(0<len(raw)<=5_000_000,"V281_V280_CANDIDATE_FILE_TOO_LARGE")
    source=json.loads(raw)
    need(source.get("item_use_spell_join",{}).get("schema")==use_spells.SCHEMA
         and source.get("source",{}).get("wago_snapshot_build")==build,
         "V281_ITEM_USE_SPELL_SOURCE_BUILD_DRIFT")
    all_use={sid for row in source["items"]
             if row.get("kind") in ("flask","item_enhancement")
             for sid in row.get("item_effect_source",{}).get("on_use_spell_ids",[])}
    if not all_use:
        return pending("V281_NO_ON_USE_SPELL_IDS_TO_JOIN")
    temp_raw=temp_path.read_bytes()
    generated=season.parse_generated("temporary_enchant",temp_raw)
    need(generated["source_build"]==build,
         "V281_SIMC_TEMP_ENCHANT_SOURCE_BUILD_DRIFT")
    calls=[0]
    def execute():
        url="https://wago.tools/db2/SpellEffect/csv?"+urlencode(
            {"build":build,"locale":"enUS"})
        request=Request(url,headers={
            "User-Agent":"SIMC-Secondary-v281-ConsumableJoin/1.0",
            "Accept":"text/csv"})
        calls[0]+=1
        target=root/OUT["spell_effect"]
        target.parent.mkdir(parents=True,exist_ok=True)
        total=0
        with (urlopen if transport is None else transport)(request,timeout=75) as resp:
            need(resp.status==200,"V281_WAGO_SPELL_EFFECT_HTTP_NOT_200")
            with target.open("wb") as f:
                while True:
                    part=resp.read(262144)
                    if not part:break
                    total+=len(part)
                    need(total<=SPELL_EFFECT_SIZE_LIMIT,
                         "V281_SPELL_EFFECT_SIZE_LIMIT")
                    f.write(part)
        need(total>0,"V281_SPELL_EFFECT_EMPTY")
        simc_rows,status,validated_item_sha=_flask_from_sealed_item_data(
            full_simc_item_source,build)
        need(validated_item_sha==item_sha,"V281_ITEM_IDENTITY_CHANGED")
        result=correlate(source,scan_spell_effects(target,all_use),
                         generated["rows"],build=build,
                         flask_dbc_rows=simc_rows)
        result["simc_relation_source"]["flask_dbc_status"]=status
        result["simc_relation_source"]["item_data_sha256"]=item_sha
        (root/OUT["candidate"]).write_text(
            json.dumps(result,sort_keys=True,ensure_ascii=False,
                       indent=2,allow_nan=False)+"\n",encoding="utf8")
    def validate(paths):
        result=json.loads(paths["candidate"].read_text("utf8"))
        row=result.get("simc_relation_source",{})
        return (result.get("schema")==physical.SCHEMA
                and row.get("schema")==SCHEMA
                and row.get("game_build")==build
                and row.get("F") is None and row.get("O") is None
                and row.get("environment_ready") is False
                and row.get("simc_token_native_verified") is False
                and result.get("automatic_ui_promotion") is False
                and all(item.get("ui_selectable") is False for item in result["items"]))
    fingerprint=stages.module_dependency_fingerprint([
        Path(__file__),Path(metadata.__file__),Path(season.__file__),
        Path(stages.__file__)])
    # Read verified small input bytes once, no old-season/static/DPS cache.
    try:
        stage=stages.execute_stage(
            root=root,stage_id="fresh-consumable-simc-spell-effect-source",
            stage_version="v281-same-build-db2-simc-source-join-v1",
            inputs={
                "game_build":build,
                "v280_receipt":src["source_stage"]["receipt_sha256"],
                "v275_receipt":compiler["source_stage"]["receipt_sha256"],
                "v280_candidate_sha256":digest(raw),
                "temporary_enchant_sha256":digest(temp_raw),
                "item_data_sha256":item_sha,
                "code_sha256":fingerprint["sha256"]},
            outputs=OUT,execute=execute,validate=validate)
    except (stages.StageExecutionBlocked,SimCRelationBlocked,
            metadata.ItemMetadataBlocked,season.CatalogBlocked,
            OSError,ValueError,KeyError,TypeError) as exc:
        return {**pending(str(exc).split(":",1)[0]),
                "network_calls_by_stage":calls[0]}
    result=json.loads((root/OUT["candidate"]).read_text("utf8"))
    return {"schema":SCHEMA,"status":"SIMC_CONSUMABLE_RELATIONS_SOURCE_ONLY",
            "candidate_path":str((root/OUT["candidate"]).resolve()),
            "source_stage":{k:v for k,v in stage.items() if k!="result"},
            "counts":result["simc_relation_source"],
            "network_calls_by_stage":calls[0],"native_calls":0,
            "F":None,"O":None,"environment_ready":False}
