"""v584: supplemental Wago-verified DPS enchant candidate → EXISTING SimC classifiers.

This is a thin SOURCE-ONLY adapter inside the ORIGINAL v583/v216 source
collection. It reuses v191's exact SimC quality-family parser, v211's DBC /
spelltext effect + same-family static noninferiority classifier and v213's
existing slot enum mapping. It neither invents effect mechanics nor creates
an independent catalog/optimizer or a new user admission gate.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import v191_unified_season_data_update as simc_season
import v211_enchant_source_effect_classification as effect
import v213_source_to_catalog as slots

SCHEMA="v584_supplemental_permanent_enchant_effects_source_only_v1"
COMPLETE="SUPPLEMENTAL_DPS_ENCHANT_EFFECTS_CLASSIFIED_UNADMITTED"
PENDING="SUPPLEMENTAL_DPS_ENCHANT_EFFECTS_PENDING"


def pending(reason):
    return {"schema":SCHEMA,"status":PENDING,"reason":reason,
            "rows":[],"source_only":True,
            "ui_selectable":False,"native_calls":0,
            "mechanics_owner":"SimC"}



def weapon_subclasses_from_pinned_source(item_subclass_mask, source):
    """Original SimC enum is the sole name authority; preserve unknown IDs."""
    resolved={}
    for line in source.splitlines():
        m=re.match(r"^\s*ITEM_SUBCLASS_WEAPON_([A-Z0-9_]+)\s*=\s*(\d+)\s*,?",line)
        if m:
            key,val=m.group(1),int(m.group(2))
            if key!="INVALID" and val not in resolved:
                resolved[val]=key
    ids=[i for i in range(32) if item_subclass_mask & (1<<i)]
    return {"source_item_subclass_ids":ids,
            "source_enum_names":[resolved.get(i) for i in ids],
            "source_enum_all_ids_resolved":bool(ids) and all(i in resolved for i in ids),
            "source_ranged_weapon_types_only":bool(ids) and all(
                resolved.get(i) in ("BOW","GUN","CROSSBOW") for i in ids),
            "hand_applicability_verified":False}



def _slot(row):
    """Use physical SimC masks, never a string token or an item name."""
    cls,mask,sub=row["item_class"],row["inventory_type_mask"],row["item_subclass_mask"]
    if cls==4 and mask>0:
        enum=simc_season.inventory_options(row)
        if enum and all(x in slots.ARMOR_ENCHANT_SLOTS for x in enum):
            allowed=sorted({slots.ARMOR_ENCHANT_SLOTS[x] for x in enum})
            if len(allowed)==1:
                return {"slot_group":allowed[0],
                        "status":"SOURCE_MASK_RESOLVED",
                        "inventory_type_options":enum}
        return {"slot_group":None,
                "status":"ARMOR_MASK_EXACT_SLOT_UNRESOLVED",
                "inventory_type_options":enum}
    if cls==2 and sub>0:
        return {"slot_group":"WEAPON_SUBCLASS_NOT_YET_USER_SLOT_CERTIFIED",
                "status":"WEAPON_SUBCLASS_PENDING_EXACT_HAND_APPLICABILITY",
                "inventory_type_options":simc_season.inventory_options(row),
                "weapon_subclass_ids_from_source_mask":
                    [i for i in range(32) if sub & (1<<i)]}
    return {"slot_group":None,"status":"SIMC_GEAR_MASK_INVALID",
            "inventory_type_options":[]}


def classify(*, relation, source_dir, manifest_path, game_build, simc_revision):
    """Classify verified additional source families without modifying v191-v213.

    Only IDs already joined by original v583 Wago+SimC are eligible to be
    considered, and only source-only. Missing/changed optional source blocks
    this supplement, not G/J/F/O nor existing fresh v191-v213 compile.
    """
    if (type(relation) is not dict or relation.get("status")!=
            "PERMANENT_ENCHANT_EXACT_WAGO_SIMC_SOURCE_ONLY"
            or relation.get("game_build")!=game_build
            or relation.get("source_only") is not True):
        return pending("V584_VERIFIED_V583_RELATION_REQUIRED")
    observed=relation.get("additional_enchants_unadmitted")
    if not isinstance(observed,list):
        return pending("V584_V583_SUPPLEMENTAL_ITEMS_REQUIRED")
    high_ids=relation.get("additional_dps_gear_highest_source_rank_candidate_ids")
    if not isinstance(high_ids,list) or any(type(x) is not int or x<=0 for x in high_ids):
        return pending("V584_SELECTED_SOURCE_RANK_IDS_MISSING")
    if not high_ids:
        return {"schema":SCHEMA,"status":COMPLETE,"reason":"NO_NEW_GEAR_CANDIDATES",
                "rows":[],"source_only":True,"ui_selectable":False,
                "native_calls":0,"mechanics_owner":"SimC",
                "source_quality_observations":[]}
    if (not isinstance(source_dir,(str,Path))
            or not isinstance(manifest_path,(str,Path))
            or not isinstance(simc_revision,str) or len(simc_revision)!=40):
        return pending("V584_EXISTING_PINNED_SIMC_V211_SOURCES_PENDING")
    folder=Path(source_dir)
    manifest_file=Path(manifest_path)
    if (not folder.is_dir() or folder.is_symlink()
            or not manifest_file.is_file() or manifest_file.is_symlink()):
        return pending("V584_PINNED_SOURCE_FILES_NOT_SEALED")
    try:
        manifest=json.loads(manifest_file.read_text(encoding="utf8"))
        sources,original_receipts=effect.load_fresh_sources(
            folder,manifest,game_build=game_build,simc_revision=simc_revision)
        generated=simc_season.parse_generated(
            "permanent_enchant",sources["permanent_enchant.inc"].encode("utf8"))
        if generated["source_build"]!=game_build or generated["sha256"]!=relation["simc_generated_sha256"]:
            return pending("V584_PINNED_GENERATED_PERMANENT_SHA_MISMATCH")
        original=effect.parse_permanent(sources["permanent_enchant.inc"])
        enums=effect.parse_enums(sources["data_enums.hh"])
        texts=effect.parse_spelltexts(sources["spelltext_data.inc"])
        handlers=effect.parse_custom_handlers(sources["unique_gear.cpp"])
        by_id={}
        for row in observed:
            if (not isinstance(row,dict)
                    or type(row.get("enchant_id")) is not int
                    or row.get("scope") not in (
                        "DPS_EQUIPMENT_PERMANENT_CANDIDATE_UNADMITTED",
                        "PROFESSION_TOOL_OUTSIDE_DPS_EQUIPMENT",
                        "SIMC_PERMANENT_EQUIPMENT_SCOPE_UNRESOLVED",
                        "SIMC_EQUIPMENT_APPLICABILITY_AMBIGUOUS")):
                return pending("V584_V583_SOURCE_SCOPE_ROWS_INVALID")
            if row["scope"]=="DPS_EQUIPMENT_PERMANENT_CANDIDATE_UNADMITTED":
                by_id[row["enchant_id"]]=row
        if set(high_ids)-set(by_id):
            return pending("V584_SELECTED_SOURCE_ID_NOT_PHYSICALLY_MATCHED")
        selected=[]
        for iid in high_ids:
            item=by_id[iid]
            original_rows=item.get("simc_source_rows")
            if not isinstance(original_rows,list) or len(original_rows)!=1:
                return pending("V584_SIMC_SOURCE_ID_AMBIGUOUS:"+str(iid))
            r=original_rows[0]
            matched=[x for x in original.get(iid,[])
                     if (x["token"],x["quality_rank"],x["item_class"],
                         x["inventory_type_mask"],x["item_subclass_mask"])==
                        (r["simc_token"],r["quality_rank"],r["item_class"],
                         r["inventory_type_mask"],r["item_subclass_mask"])]
            if len(matched)!=1:
                return pending("V584_SIMC_SOURCE_RANK_MASK_CHANGED:"+str(iid))
            selected.append(matched[0])
        # Only classify selected ID rows. The original quality comparator below
        # loads the COMPLETE same-family ranks from independent SimC DBC.
        dbc=effect.parse_dbc_rows(sources["spell_item_enchantment.inc"],
                                  set(high_ids))
        rows=[]
        for r in selected:
            classified=effect.classify_row(
                r,dbc[r["enchant_id"]],enums,texts,handlers,{},
                unknown_item_mods_pending=True)
            allowed=_slot(r)
            if r["item_class"]==2 and r["item_subclass_mask"]>0:
                allowed["pinned_weapon_subclasses"]=weapon_subclasses_from_pinned_source(
                    r["item_subclass_mask"],sources["data_enums.hh"])
            physical=by_id[r["enchant_id"]]["physical_items"]
            if not isinstance(physical,list) or not physical:
                return pending("V584_PHYSICAL_ITEM_ID_REQUIRED")
            rows.append({
                "enchant_id":r["enchant_id"],
                "simc_token":r["token"],
                "quality_rank_simc":r["quality_rank"],
                "source_class_and_masks":{
                    "item_class":r["item_class"],
                    "inventory_type_mask":r["inventory_type_mask"],
                    "item_subclass_mask":r["item_subclass_mask"]},
                "physical_item_ids":sorted({p["item_id"] for p in physical}),
                "source_slot":allowed,
                "effect_family":classified["effect_family"],
                "effect_summary":classified["effect_summary"],
                "static_components":classified["static_components"],
                "spell_effects":classified["spell_effects"],
                "unknown_components":classified["unknown_components"],
                "static_chmv_present":classified[
                    "static_chmv_rating_present_in_dbc"],
                "static_E":"NOT_MEASURED_IF_CHMV",
                "static_E_source_status":(
                    "STATIC_CHMV_NUMERIC_MEASUREMENT_PENDING"
                    if classified["static_chmv_rating_present_in_dbc"] else
                    "UNKNOWN_STATIC_COMPONENT_REVIEW_PENDING"
                    if classified["unknown_components"] else
                    "NO_STATIC_CHMV_COMPONENT_IN_SIMC_DBC"),
                "selection_status":"SUPPLEMENTAL_SOURCE_ONLY_NOT_USER_PUBLISHED",
                "ui_selectable":False,
                "simc_effect_owner":"SimC"})
        sample={"game_build":game_build,"simc_revision":simc_revision,
                "enchants":{"permanent":{
                    "source_rows":generated["declared_rows"],
                    "source_records":generated["rows"]}}}
        quality=effect._fresh_static_quality_source_only(
            sample,selected,original,sources["spell_item_enchantment.inc"],enums)
        observations=quality.get("observations",[])
        by_observation={o["selected_enchant_id"]:o for o in observations}
        for row in rows:
            src_quality=by_observation.get(row["enchant_id"],{})
            # Entire family comes from the same independent pinned SimC
            # source; this source-only comparison never approves its rank.
            row["raw_rank_component_evidence"]=src_quality.get(
                "source_rank_component_comparison")
        unknown_ids={r["enchant_id"] for r in rows
                     if r["unknown_components"]}
        # v211's raw numeric comparator may compare the same unknown stat
        # ID; source-only numerical ordering must NOT certify an unknown
        # effect. Keep the candidate and report the withheld conclusion.
        for row in observations:
            if row.get("selected_enchant_id") in unknown_ids:
                row["status"]="UNKNOWN_STAT_COMPONENT_QUALITY_EFFECT_PENDING"
                row["source_only_noninferior"]=False
                row["policy_A_product_input_verified"]=False
        return {"schema":SCHEMA,"status":COMPLETE,
                "game_build":game_build,"simc_revision":simc_revision,
                "v211_source_sha256_by_file":{
                    k:v["sha256"] for k,v in sorted(original_receipts.items())},
                "candidate_count":len(rows),
                "slot_resolved_count":sum(x["source_slot"]["status"]==
                                          "SOURCE_MASK_RESOLVED" for x in rows),
                "weapon_hand_pending_count":sum(x["source_slot"]["status"]==
                    "WEAPON_SUBCLASS_PENDING_EXACT_HAND_APPLICABILITY"
                    for x in rows),
                "unknown_component_candidate_count":len(unknown_ids),
                "static_chmv_candidate_count":sum(x["static_chmv_present"] for x in rows),
                "quality_noninferior_source_count":sum(
                    x.get("source_only_noninferior") is True for x in observations),
                "raw_static_component_nondecreasing_candidate_count":sum(
                    x.get("source_rank_component_comparison",{}).get(
                        "source_raw_amount_and_coefficient_nondecreasing") is True
                    for x in observations),
                "raw_static_component_rank_evidence_only":True,
                "source_quality_observations":observations,
                "rows":rows,"source_only":True,
                "ui_selectable":False,"native_calls":0,
                "mechanics_owner":"SimC"}
    except (OSError,ValueError,TypeError,KeyError,UnicodeError,
            effect.SourceBlocked,simc_season.CatalogBlocked) as exc:
        # Optional does not interfere with the previously verified BASE.
        return pending(str(exc).split(":",1)[0])
