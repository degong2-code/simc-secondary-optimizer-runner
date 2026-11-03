#!/usr/bin/env python3
"""P3-CT: reuse sealed representative gear + oil masks in the normal Build.

A source-only option-to-selected-weapon join, NOT a second environment
builder, gameplay effect calculator, quality policy or user UI approval.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import v217_stage_execution_engine as stages
import v167_product_season_gear_adapter as gear_db
import v232_simc_only_ordinary_representative as representative_db
import v285_consumable_weapon_source as oil_db

SCHEMA="v286_representative_oil_source_compatibility_v1"
STAGED=frozenset(("EXECUTED_AND_SEALED","REUSED_VERIFIED","RECOVERED_VERIFIED"))
MAX_CANDIDATE=24_000_000

class OilRepresentativeSourceBlocked(ValueError):
    pass

def need(ok,why):
    if not ok:raise OilRepresentativeSourceBlocked(why)

def pending(reason):
    return {"schema":SCHEMA,"status":"REPRESENTATIVE_OIL_SOURCE_PENDING",
            "reason":reason,"candidate_options":[],
            "source_mask_matches":0,"new_native_calls":0,
            "network_calls":0,"quality_groups_verified":False,
            "F":None,"O":None,"B":None,"T":None,
            "environment_ready":False,"user_selectable":False}

def _verified_candidate(root,row,label):
    """Read only a small v217 candidate that its original stage already sealed."""
    stage=row.get("source_stage",{}) if type(row) is dict else {}
    if (type(stage) is not dict or stage.get("status") not in STAGED
            or not row.get("candidate_path")):
        return None
    stage_id=stage.get("stage_id")
    relative=(stage.get("output_paths") or {}).get("candidate")
    need(type(stage_id) is str and bool(stage_id) and
         type(relative) is str and relative.startswith("source/")
         and ".." not in Path(relative).parts,
         "V286_"+label+"_SEALED_CANDIDATE_PATH_REQUIRED")
    path=Path(row["candidate_path"])
    need(not path.is_symlink() and path.is_file()
         and path.resolve().is_relative_to(root)
         and path.resolve()==(root/relative).resolve(),
         "V286_"+label+"_CANDIDATE_PATH_DRIFT")
    receipt_path=root/".stage_receipts"/(stage_id+".json")
    try:
        receipt=stages._read_receipt(receipt_path)
    except (stages.StageExecutionBlocked,OSError) as exc:
        raise OilRepresentativeSourceBlocked(
            "V286_"+label+"_SOURCE_RECEIPT_MISSING_OR_INVALID") from exc
    need(receipt.get("status")=="COMPLETE"
         and receipt.get("stage_id")==stage_id
         and receipt.get("receipt_sha256")==stage.get("receipt_sha256")
         and receipt.get("input_fingerprint")==stage.get("input_fingerprint")
         and receipt.get("stage_version")==stage.get("stage_version")
         and receipt.get("output_paths")==stage.get("output_paths"),
         "V286_"+label+"_SOURCE_RECEIPT_DRIFT")
    registered=(receipt.get("outputs") or {}).get("candidate") or {}
    need(registered.get("path")==relative
         and type(registered.get("size")) is int
         and 0<registered["size"]<=MAX_CANDIDATE
         and path.stat().st_size==registered["size"],
         "V286_"+label+"_CANDIDATE_SIZE_DRIFT")
    raw=path.read_bytes()
    need(hashlib.sha256(raw).hexdigest()==registered.get("sha256"),
         "V286_"+label+"_CANDIDATE_SHA_DRIFT")
    try:
        data=json.loads(raw)
    except (UnicodeError,ValueError) as exc:
        raise OilRepresentativeSourceBlocked(
            "V286_"+label+"_SOURCE_JSON_INVALID") from exc
    need(type(data) is dict,"V286_"+label+"_CANDIDATE_OBJECT_REQUIRED")
    return data,stage["receipt_sha256"],registered["sha256"]

def match_collected(collected):
    """Report usable physical oil masks for the auto-selected representative.

    This checks masks against the selected SAME-BUILD gear and slot, not an
    uploaded current outfit. Unobserved metadata stays pending (never 0/false
    for an actual item), and all variants remain internal diagnostics.
    """
    if type(collected) is not dict or collected.get("schema")!=(
         "v216_fresh_source_stage_v1"):
        return pending("V286_NORMAL_BUILD_SOURCE_REQUIRED")
    snapshot=collected.get("snapshot_receipt_path")
    if type(snapshot) is not str:
        return pending("V286_STAGE_ROOT_PENDING")
    source_root=Path(snapshot)
    if (source_root.name!="receipt.json"
         or source_root.parent.name!="wago"
         or not source_root.parent.is_dir()
         or source_root.is_symlink()
         or source_root.parent.is_symlink()):
        return pending("V286_STAGE_ROOT_PENDING")
    root=source_root.parent.parent.resolve()
    if not root.is_dir() or root.is_symlink():
        return pending("V286_STAGE_ROOT_PENDING")
    source_data={}
    source_identity={}
    for name,key in (("OIL","fresh_consumable_weapon_source"),
                     ("GEAR","fresh_ordinary_gear"),
                     ("REPRESENTATIVE","fresh_one_spec_simc_representative")):
        ready=_verified_candidate(root,collected.get(key),name)
        if ready is None:
            return pending("V286_"+name+"_SOURCE_PENDING")
        source_data[name],receipt,sha=ready
        source_identity[name]={"stage_receipt_sha256":receipt,
                               "candidate_sha256":sha}
    build=collected.get("expected_game_build")
    oil=source_data["OIL"]
    gear=source_data["GEAR"]
    rep=source_data["REPRESENTATIVE"]
    need(type(build) is str and build
         and oil.get("weapon_equipped_source",{}).get("schema")==oil_db.SCHEMA
         and oil["weapon_equipped_source"].get("game_build")==build
         and oil["weapon_equipped_source"].get("source_only") is True
         and oil.get("automatic_ui_promotion") is False
         and gear.get("schema")==gear_db.SCHEMA
         and gear.get("season_build")==build
         and rep.get("schema")==representative_db.SCHEMA
         and rep.get("game_build")==build
         and rep.get("selected_G_source_candidate_not_approved") is True,
         "V286_SAME_BUILD_REPRESENTATIVE_SOURCE_DRIFT")
    selected=rep.get("selected_weapons")
    need(type(selected) is dict and all(
         hand in ("main_hand","off_hand") and type(iid) is int and iid>0
         for hand,iid in selected.items()),
         "V286_SELECTED_REPRESENTATIVE_WEAPONS_INVALID")
    # Keep actual Wago inventory/subclass codes; avoid invented conversion
    # tables or item DB rereads. Use already selected source records only.
    provider={}
    for row in (gear.get("items") or []) + (
        gear.get("internal_conditional_mplus_plain_candidates") or []):
        if type(row) is dict and type(row.get("item_id")) is int:
            provider.setdefault(row["item_id"],[]).append(row)
    weapon_info={}
    unresolved=[]
    for hand,iid in sorted(selected.items()):
        meta=provider.get(iid,[])
        keys={(r.get("class_id"),r.get("subclass_id"),
               r.get("inventory_type")) for r in meta}
        if len(keys)!=1:
            unresolved.append({"hand":hand,"item_id":iid,
                               "reason":"SOURCE_WEAPON_METADATA_UNAVAILABLE_OR_CONFLICT"})
            continue
        cls,sub,inv=next(iter(keys))
        if not (type(cls) is int and type(sub) is int and
                type(inv) is int and 0<=sub<32 and 0<=inv<32):
            unresolved.append({"hand":hand,"item_id":iid,
                               "reason":"SOURCE_WEAPON_FIELDS_INVALID"})
            continue
        weapon_info[hand]={"item_id":iid,"class_id":cls,
                           "subclass_id":sub,"inventory_type":inv}
    options=[]
    for item in oil.get("items",[]):
        if type(item) is not dict or item.get("kind")!="item_enhancement":
            continue
        simc=item.get("simc_temporary_enchant_source") or {}
        links=simc.get("exact_source_matches") or []
        identity={(link.get("enchant_id"),link.get("quality_rank"),
                   link.get("simc_token")) for link in links
                   if type(link) is dict}
        if (simc.get("status")!="EXACT_SIMC_TEMP_ENCHANT_ID_CANDIDATE"
             or len(identity)!=1):
            continue
        enchant,quality,token=next(iter(identity))
        if (type(enchant) is not int or enchant<=0
            or type(quality) is not int or quality<0
            or type(token) is not str or "oil" not in token.split("_")):
            continue  # Exclude stones and general temporary enchants.
        source=item.get("weapon_spell_equipped_source") or {}
        if source.get("status")!="EXACT_SAME_BUILD_WEAPON_MASK_SOURCE_ONLY":
            continue
        cls=source.get("equipped_item_class")
        inv_mask=source.get("inventory_type_mask")
        sub_mask=source.get("weapon_subclass_mask")
        if not (cls==2 and type(inv_mask) is int and
                type(sub_mask) is int and inv_mask>0 and sub_mask>0):
            continue
        for hand,actual in sorted(weapon_info.items()):
            matching=(actual["class_id"]==cls
                and bool(inv_mask&(1<<actual["inventory_type"]))
                and bool(sub_mask&(1<<actual["subclass_id"])))
            if matching:
                options.append({
                    "oil_item_id":item["item_id"],
                    "quality_rank":quality,"simc_token":token,
                    "simc_enchant_id":enchant,
                    "hand":hand,
                    "representative_weapon_id":actual["item_id"],
                    "weapon_source_class":actual["class_id"],
                    "weapon_source_subclass":actual["subclass_id"],
                    "weapon_source_inventory_type":actual["inventory_type"],
                    "matched_same_build_spell_equipped_masks":True,
                    "game_weapon_ilevel_and_use_requirements_verified":False,
                    "quality_effect_equivalence_verified":False,
                    "user_selectable":False})
    return {
        "schema":SCHEMA,
        "status":("REPRESENTATIVE_OIL_MASK_MATCH_SOURCE_ONLY"
                  if options else "REPRESENTATIVE_OIL_MASK_MATCH_PENDING"),
        "game_build":build,"simc_revision":rep.get("simc_revision"),
        "selected_representative_weapon_ids":dict(sorted(selected.items())),
        "candidate_options":sorted(options,key=lambda x:(
           x["oil_item_id"],x["hand"])),
        "source_mask_matches":len(options),
        "unresolved_representative_weapons":unresolved,
        "source_stage_identities":source_identity,
        "same_build_source_only":True,
        "not_an_item_recommendation":True,
        "same_effect_quality_group_verified":False,
        "weapon_use_ilevel_requirement_verified":False,
        "new_native_calls":0,"network_calls":0,
        "F":None,"O":None,"B":None,"T":None,
        "environment_ready":False,"user_selectable":False}
