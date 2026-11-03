#!/usr/bin/env python3
"""Build original v191-compatible tier input from existing v251 + same-build DB2.

This does NOT turn an observed raid tier into a certified season roster:
v251's exact physical/SimC evidence remains CANDIDATE, and this adapter
verifies only original ItemSparse/Item physical properties. No new API,
SimC Native, item DB or independently invented publisher name is introduced.
"""
from __future__ import annotations

import json
from pathlib import Path

import v168_current_season_tier_discovery as tier
import v217_stage_execution_engine as stages
import v231_simc_tier_item_join as simc_tier
import v251_db2_raid_tier_simc_bridge as bridge

SCHEMA = tier.SCHEMA
CANDIDATE_STATUS = "V251_DB2_SIMC_EXACT_13_CLASS_PHYSICAL_TIER_SEASON_PENDING"
RELATIVE_OUTPUT = "source/v276_v168_compatible_tier_from_sealed_v251.json"
EXPECTED_RECEIPTS = (
    ("physical","fresh-v251-db2-raid-tier-candidate"),
    ("exact","fresh-v251-exact-first-party-simc-options"),
)
STAGE_STATES = ("EXECUTED_AND_SEALED","REUSED_VERIFIED","RECOVERED_VERIFIED")


class TierCompilerSourceBlocked(ValueError):
    pass


def need(ok,code):
    if not ok:
        raise TierCompilerSourceBlocked(code)


def pending(reason):
    return {
        "status":"COMPILER_TIER_PHYSICAL_SOURCE_PENDING",
        "reason":reason,"candidate_path":None,
        "network_calls_by_stage":0,"native_calls":0,
        "environment_ready":False,"season_membership_verified":False,
    }


def _source_file(root,row,stage_id):
    need(type(row) is dict and type(row.get("source_stage")) is dict,
         "V276_SOURCE_STAGE_REQUIRED")
    stage=row["source_stage"]
    need(stage.get("status") in STAGE_STATES and
         stage.get("stage_id")==stage_id and
         type(stage.get("receipt_sha256")) is str and
         len(stage["receipt_sha256"])==64,
         "V276_UPSTREAM_SEALED_V251_SOURCE_REQUIRED")
    value=row.get("candidate_path")
    need(type(value) is str and bool(value),
         "V276_UPSTREAM_CANDIDATE_FILE_REQUIRED")
    path=Path(value)
    need(path.is_file() and not path.is_symlink() and
         path.resolve().is_relative_to(root),
         "V276_UPSTREAM_CANDIDATE_FILE_OUTSIDE_SOURCE_ROOT")
    return path


def _read_candidate(path):
    need(0<path.stat().st_size<=bridge.MAX_JSON,
         "V276_UPSTREAM_CANDIDATE_SIZE_INVALID")
    try:
        return json.loads(path.read_text(encoding="utf8"))
    except (ValueError,UnicodeError,OSError) as exc:
        raise TierCompilerSourceBlocked(
            "V276_UPSTREAM_CANDIDATE_JSON_INVALID") from exc


def physical_roster(*,physical,matched,selected,build,wago_folder,
                    verified_wago_tables):
    """One pass per original DB2 CSV, 65 exact IDs only; no extra SHA scans."""
    need(type(selected) is dict and selected.get("status")==
         "EXISTING_ACTIVE_RAID_SIMC_EXACT_TIER_SOURCE_REUSED" and
         selected.get("source_evidence_reused") is True and
         selected.get("season_membership_verified") is False and
         selected.get("environment_ready") is False and
         selected.get("game_build")==build and
         type(selected.get("source_stage_receipts")) is dict,
         "V276_EXISTING_TIER_SOURCE_REUSE_REQUIRED")
    need(physical.get("schema")==bridge.SCHEMA and
         physical.get("status")==
            "OBSERVED_CURRENT_RAID_CORRELATED_65_PIECE_TIER_CANDIDATE" and
         matched.get("schema")==bridge.SCHEMA and
         matched.get("status")==
            "EXACT_13_CLASS_SIMC_SET_OPTIONS_MATCHED_SEASON_PENDING" and
         physical.get("game_build")==build and matched.get("game_build")==build and
         physical.get("class_count")==matched.get("class_count")==13 and
         physical.get("piece_count")==matched.get("piece_count")==65 and
         matched.get("simc_set_option_verified_by_exact_physical_ids") is True and
         physical.get("season_membership_verified") is False and
         matched.get("season_membership_verified") is False,
         "V276_EXACT_65_SOURCE_NOT_PROVED")
    expected={}
    classes=physical["classes"]
    counterpart=matched["classes"]
    need(set(classes)==set(counterpart)==set(tier.FAMILY),
         "V276_13_CLASS_ROSTER_INCOMPLETE")
    for cls in sorted(tier.FAMILY):
        p=classes[cls];m=counterpart[cls]
        ids=p["tier_piece_ids"]
        need(set(ids)==set(tier.SLOTS) and
             len(set(ids.values()))==5 and
             all(type(i) is int and i>0 for i in ids.values()) and
             m.get("tier_piece_ids")==ids and
             m.get("item_set_id")==p["item_set_id"] and
             m.get("observed_base_item_level")==
                    p.get("observed_base_item_level") and
             m.get("source_set_bonus_sizes")==[2,4] and
             isinstance(m.get("simc_set_option"),str) and
             simc_tier.TOKEN.fullmatch(m["simc_set_option"]),
             "V276_V251_CLASS_PHYSICAL_OR_SIMC_EXACT_DRIFT")
        for slot,iid in ids.items():
            need(iid not in expected,"V276_TIER_ID_REPEATED")
            expected[iid]=(cls,slot,p["item_set_id"])
    need(len(expected)==65,"V276_TIER_ID_COUNT_NOT_65")
    root=Path(wago_folder)
    need(root.is_dir() and not root.is_symlink(),
         "V276_WAGO_SNAPSHOT_DIRECTORY_INVALID")
    receipt_path=root/"receipt.json"
    need(receipt_path.is_file() and not receipt_path.is_symlink(),
         "V276_WAGO_SNAPSHOT_RECEIPT_MISSING")
    receipt=json.loads(receipt_path.read_text("utf8"))
    need(receipt.get("build")==build and receipt.get("locale")=="enUS" and
         type(verified_wago_tables) is dict and
         all(receipt.get("tables",{}).get(t)==
             verified_wago_tables.get(t)
             for t in ("Item","ItemSparse")),
         "V276_WAGO_ALREADY_SEALED_SOURCE_IDENTITY_REQUIRED")
    sparse={}
    for row in tier.rows(root/"ItemSparse.csv",
             ("ID","Display_lang","InventoryType","ExpansionID",
              "ItemSet","AllowableClass")):
        iid=tier.as_int(row["ID"])
        if iid not in expected:continue
        need(iid not in sparse,"V276_SPARSE_DUPLICATE_ID")
        cls,slot,group=expected[iid]
        inv=tier.as_int(row["InventoryType"])
        mask=tier.as_int(row["AllowableClass"])
        expansion=tier.as_int(row["ExpansionID"])
        name=row["Display_lang"].strip()
        need(tier.CORE.get(inv)==slot and
             tier.as_int(row["ItemSet"])==group and
             expansion==physical["expansion_id"] and
             type(mask) is int and mask>0 and mask&(mask-1)==0 and
             mask==(1 << (simc_tier.CLASS_ID[cls]-1)) and
             bool(name),
             "V276_SPARSE_SLOT_SET_CLASS_OR_EXPANSION_DRIFT")
        sparse[iid]={"name":name,"mask":mask,"inv":inv}
    need(set(sparse)==set(expected),"V276_SPARSE_65_PHYSICAL_ITEMS_MISSING")
    seen=set()
    for row in tier.rows(root/"Item.csv",
             ("ID","ClassID","SubclassID","InventoryType")):
        iid=tier.as_int(row["ID"])
        if iid not in expected:continue
        need(iid not in seen,"V276_ITEM_DB2_DUPLICATE_ID")
        cls,slot,_=expected[iid]
        need(tier.as_int(row["ClassID"])==4 and
             tier.as_int(row["SubclassID"])==tier.FAMILY[cls] and
             tier.CORE.get(tier.as_int(row["InventoryType"]))==slot and
             tier.as_int(row["InventoryType"])==sparse[iid]["inv"],
             "V276_ITEM_CLASS_ARMOR_OR_SLOT_DRIFT")
        seen.add(iid)
    need(seen==set(expected),"V276_ITEM_65_PHYSICAL_ITEMS_MISSING")
    output={}
    for cls in sorted(classes):
        ids=classes[cls]["tier_piece_ids"]
        masks={sparse[i]["mask"] for i in ids.values()}
        need(len(masks)==1,"V276_TIER_CLASS_MASK_DRIFT")
        output[cls]={
            "allowed_class_mask":next(iter(masks)),
            "item_set_id":classes[cls]["item_set_id"],
            "pieces":{slot:ids[slot] for slot in tier.SLOTS},
            "names":{slot:sparse[ids[slot]]["name"] for slot in tier.SLOTS},
        }
    return {"schema":SCHEMA,"status":CANDIDATE_STATUS,
            "retail_build":build,"expansion_id":physical["expansion_id"],
            "season":None,"class_count":13,"item_count":65,"classes":output,
            "evidence":{
                "source_kind":"V251_EXISTING_RAID_AND_EXACT_SIMC_PLUS_WAGO_PHYSICAL",
                "source_scope":"OBSERVED_RAID_CANDIDATE_NOT_FULL_SEASON",
                "simc_seed_receipt_sha256":matched["simc_seed_receipt_sha256"],
                "wago_item_sha256":verified_wago_tables["Item"]["sha256"],
                "wago_item_sparse_sha256":
                    verified_wago_tables["ItemSparse"]["sha256"],
                "publisher_tier_names_verified":False,
                "all_class_65_item_simc_set_options_exact":True,
            },
            "source_season_verified":False,
            "season_membership_verified":False,
            "simc_tier_bonus_mechanics_verified":False,
            "native_calls":0,"network_calls":0,
            "environment_ready":False,"production_profile_promoted":False}


def collect(*,stage_root,wago_folder,build,tier_bridge,first_party,
            selected_tier,verified_wago_tables):
    if (type(tier_bridge) is not dict or
        not tier_bridge.get("candidate_path") or
        type(first_party) is not dict or
        not first_party.get("candidate_path") or
        type(selected_tier) is not dict or
        selected_tier.get("source_evidence_reused") is not True):
        return pending("V276_SEALED_V251_13_CLASS_EVIDENCE_PENDING")
    root=Path(stage_root).resolve()
    try:
        physical_path=_source_file(root,tier_bridge,
                   "fresh-v251-db2-raid-tier-candidate")
        exact_path=_source_file(root,first_party,
                   "fresh-v251-exact-first-party-simc-options")
        need(selected_tier.get("source_stage_receipts")=={
             "raid_correlated_physical":
                 tier_bridge["source_stage"]["receipt_sha256"],
             "simc_exact_13_class":
                 first_party["source_stage"]["receipt_sha256"]},
             "V276_V251_SELECTION_SOURCE_RECEIPT_DRIFT")
        physical=_read_candidate(physical_path)
        matched=_read_candidate(exact_path)
        document=physical_roster(
            physical=physical,matched=matched,selected=selected_tier,
            build=build,wago_folder=wago_folder,
            verified_wago_tables=verified_wago_tables)
    except (TierCompilerSourceBlocked,tier.TierBlocked,
            OSError,KeyError,TypeError,ValueError) as exc:
        return pending(str(exc).split(":",1)[0])
    fingerprint=stages.module_dependency_fingerprint([
        Path(__file__),Path(tier.__file__),Path(bridge.__file__),
        Path(stages.__file__)])
    output=root/RELATIVE_OUTPUT
    def execute():
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(document,sort_keys=True,
            indent=2,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf8")
    def validate(files):
        return (json.loads(files["candidate"].read_text("utf8"))==document
                and document["season_membership_verified"] is False
                and document["environment_ready"] is False)
    try:
        stage=stages.execute_stage(
            root=root,stage_id="fresh-v251-physical-tier-compiler-source",
            stage_version="v276-v251-plus-db2-physical-v1",
            inputs={
                "game_build":build,
                "wago_item_sha256":verified_wago_tables["Item"]["sha256"],
                "wago_sparse_sha256":
                    verified_wago_tables["ItemSparse"]["sha256"],
                "upstream_physical_stage_sha256":
                    tier_bridge["source_stage"]["receipt_sha256"],
                "upstream_exact_stage_sha256":
                    first_party["source_stage"]["receipt_sha256"],
                "simc_seed_receipt_sha256":
                    matched["simc_seed_receipt_sha256"],
                "code_sha256":fingerprint["sha256"],
            },
            outputs={"candidate":RELATIVE_OUTPUT},
            execute=execute,validate=validate)
    except stages.StageExecutionBlocked as exc:
        raise TierCompilerSourceBlocked(str(exc).split(":",1)[0]) from exc
    return {"status":CANDIDATE_STATUS,
            "candidate_path":str(output.resolve()),
            "source_stage":{k:v for k,v in stage.items() if k!="result"},
            "network_calls_by_stage":0,"native_calls":0,
            "source_season_verified":False,
            "environment_ready":False,
            "season_membership_verified":False}
