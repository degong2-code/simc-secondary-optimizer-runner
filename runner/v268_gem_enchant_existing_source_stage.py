#!/usr/bin/env python3
"""One optional Wago enchant source table inside the ORIGINAL v216 Build.

The v161 ten-table Wago receipt remains immutable. The v217 source stage
caches one separately fetched SpellItemEnchantment CSV; v266 subsequently
joins only gem enchant IDs already present in v221. Nothing admits J/UI.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

try:
    from . import v217_stage_execution_engine as stage
    from . import v266_gem_enchant_raw_stat_source as join
    from . import v267_gem_enchant_one_csv_fetch as source
except ImportError:
    import v217_stage_execution_engine as stage
    import v266_gem_enchant_raw_stat_source as join
    import v267_gem_enchant_one_csv_fetch as source

STAGE="fresh-gem-enchantment-source-csv"
VERSION="v267-one-build-one-table-v1"
OUTPUTS={"csv":"wago/SpellItemEnchantment.csv"}


def collect(*,stage_root,build,transport=None):
    """One extra HTTP only on a new source identity; no existing Wago retry."""
    root=Path(stage_root)
    path=root/OUTPUTS["csv"]
    fingerprint=stage.module_dependency_fingerprint([
        Path(source.__file__),Path(stage.__file__)])
    inputs={"game_build":build,"table":source.TABLE,"locale":"enUS",
            "fetch_code_sha256":fingerprint["sha256"]}
    def execute():
        raw,_=source.fetch(
            build=build,
            transport=source.urlopen if transport is None else transport)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(raw)
    def validate(files):
        file=files["csv"]
        if not file.is_file() or not 0<file.stat().st_size<=source.MAX_BYTES:
            return False
        with file.open("rb") as stream:
            raw_header=stream.readline(16384)
        try:
            fields=next(csv.reader([raw_header.decode("utf-8-sig")]))
        except (UnicodeError,csv.Error,ValueError,StopIteration):
            return False
        return set(join.COLUMNS)<=set(fields)
    try:
        receipt=stage.execute_stage(
            root=root,stage_id=STAGE,stage_version=VERSION,inputs=inputs,
            outputs=OUTPUTS,execute=execute,validate=validate)
    except (stage.StageExecutionBlocked,source.GemEnchantFetchBlocked,
            ValueError,OSError,KeyError) as exc:
        return {"status":"GEM_ENCHANT_SINGLE_CSV_SOURCE_PENDING",
                "reason":str(exc).split(":",1)[0],
                "candidate_path":None,"network_calls_by_stage":0,
                "J":None,"native_calls":0,"environment_ready":False}
    return {
        "status":"GEM_ENCHANT_CSV_SOURCE_SEALED",
        "candidate_path":str(path.resolve()),
        "source_stage":{k:v for k,v in receipt.items() if k!="result"},
        "network_calls_by_stage":int(receipt["executed"]),
        "J":None,"native_calls":0,"environment_ready":False,
    }


def view(*,stage_root,v221_candidate_path,build,selected_gem_item_ids=None,
         selected_source_gem_item_ids=None):
    """Reuse a sealed v266 source view and only project selected raw gem IDs.

    Raw EffectPointsMin values are NOT proven effective rating, best quality,
    legal sockets or Native accepted gems. No new CSV read or SimC run.
    """
    if selected_gem_item_ids is not None:
        if (type(selected_gem_item_ids) is not list or
                len(selected_gem_item_ids)>64 or
                any(type(item) is not int or item<=0
                    for item in selected_gem_item_ids)):
            raise ValueError("V268_SELECTED_GEM_ITEM_IDS_INVALID")
    if selected_source_gem_item_ids is not None:
        if (type(selected_source_gem_item_ids) is not list or
                not 1<=len(selected_source_gem_item_ids)<=64 or
                any(type(item) is not int or item<=0
                    for item in selected_source_gem_item_ids) or
                len(set(selected_source_gem_item_ids))!=len(
                    selected_source_gem_item_ids)):
            raise ValueError("V268_SOURCE_GEM_ITEM_IDS_INVALID")
    root=Path(stage_root)
    csv_path=root/OUTPUTS["csv"]
    receipt_path=root/".stage_receipts"/(STAGE+".json")
    if not csv_path.is_file() or not receipt_path.is_file():
        return {"status":"GEM_ENCHANT_SINGLE_CSV_SOURCE_NOT_COLLECTED",
                "raw_static_candidate_count":0,
                "J":None,"native_calls":0,"network_calls":0}
    try:
        sealed=stage._read_receipt(receipt_path)
        fingerprint=stage.module_dependency_fingerprint([
            Path(source.__file__),Path(stage.__file__)])
        expected=stage._input_sha(
            STAGE,VERSION,{
                "game_build":build,"table":source.TABLE,"locale":"enUS",
                "fetch_code_sha256":fingerprint["sha256"]})
        if (sealed.get("status")!="COMPLETE" or
            sealed.get("stage_id")!=STAGE or
            sealed.get("stage_version")!=VERSION or
            sealed.get("input_fingerprint")!=expected or
            sealed.get("output_paths")!=OUTPUTS):
            raise ValueError("V268_GEM_CSV_RECEIPT_IDENTITY_DRIFT")
        path=Path(v221_candidate_path)
        if not path.is_file() or path.is_symlink():
            raise ValueError("V268_V221_EXACT_JOIN_MISSING")
        records=json.loads(path.read_text("utf8"))
        raw=csv_path.read_bytes()
        if not 0<len(raw)<=source.MAX_BYTES:
            raise ValueError("V268_CSV_SIZE_INVALID")
        result=join.preview(gem_join=records,raw_enchant_csv=raw,
                            expected_game_build=build)
        recorded=sealed["outputs"]["csv"]
        if (result["enchant_source_sha256"]!=recorded["sha256"] or
                len(raw)!=recorded["size"]):
            raise ValueError("V268_SEALED_CSV_BYTES_CHANGED")
    except (ValueError,TypeError,KeyError,OSError,
            stage.StageExecutionBlocked,join.EnchantSourceBlocked) as exc:
        return {"status":"GEM_ENCHANT_LOCAL_JOIN_PENDING",
                "reason":str(exc).split(":",1)[0],
                "J":None,"native_calls":0,"network_calls":0}
    # v266 already traversed and verified the exact v221/CSV join. Limit the
    # downstream projection to actually placed gems, not the whole item DB.
    selected={}
    unresolved=[]
    if selected_gem_item_ids is not None:
        by_id={row["item_id"]:row for row in result["records"]}
        for item_id in sorted(set(selected_gem_item_ids)):
            row=by_id.get(item_id)
            if (row is None or row["effect_classification"]!=
                    "RAW_STATIC_CHMV_POINTS_CANDIDATE_ONLY"):
                unresolved.append(item_id)
                continue
            vector=row["raw_static_points_candidate"]
            if (type(vector) is not dict or
                    set(vector)!={"crit_rating","haste_rating",
                                  "mastery_rating","versatility_rating"} or
                    any(type(amount) is not int or amount<0
                        for amount in vector.values()) or
                    sum(vector.values())<=0):
                unresolved.append(item_id)
            else:
                selected[str(item_id)]=sum(vector.values())
    source_membership={}
    if selected_source_gem_item_ids is not None:
        # The v221 candidate and same-build source relation were already
        # parsed and validated by v266.preview in THIS call.
        exact={row["item_id"]:row for row in records["joins"]}
        requested=sorted(set(selected_source_gem_item_ids))
        missing=sorted(set(requested)-set(exact))
        # v221 already supplied the physical ItemSparse->GemProperty join.
        # Project those SAME rows into the normal Build input contract.
        # Color/minimum-level are source facts, not game-socket legality.
        properties=[]
        unresolved_properties=[]
        for item_id in requested:
            row=exact.get(item_id)
            if row is None:
                continue
            keys=("gem_property_id","enchant_id","color_mask",
                  "minimum_ilevel","expansion_id")
            if (any(type(row.get(k)) is not int or
                    row[k] < (1 if k=="gem_property_id" else 0)
                    for k in keys) or
                row.get("socket_eligibility")!="NOT_YET_VERIFIED" or
                row.get("ui_selectable") is not False):
                unresolved_properties.append(item_id)
                continue
            properties.append({"item_id":item_id,
                               **{k:row[k] for k in keys}})
        source_membership={
            "selected_gem_v221_item_ids_unadmitted":sorted(
                set(requested)&set(exact)),
            "selected_gem_v221_missing_item_ids":missing,
            "selected_gem_v221_same_build_items_all_present":not missing,
            "selected_gem_v221_source_properties_unadmitted":properties,
            "selected_gem_v221_source_properties_unresolved_item_ids":
                unresolved_properties,
            "selected_gem_v221_source_properties_complete":(
                not missing and not unresolved_properties and
                len(properties)==len(requested)),
            "selected_gem_v221_source_only":True}
    return {
        "status":result["status"],
        **source_membership,
        "selected_gem_raw_points_by_id_unadmitted":selected,
        "selected_gem_unresolved_item_ids":unresolved,
        "selected_gem_all_raw_points_known":(
            selected_gem_item_ids is not None and not unresolved and
            bool(selected_gem_item_ids)),
        "selected_gem_raw_points_not_native_verified":True,
        "selected_gem_raw_points_not_quality_or_socket_verified":True,
        "raw_static_candidate_count":result["raw_static_candidate_count"],
        "unresolved_enchant_count":result["unresolved_count"],
        "linked_gem_items":result["gem_item_link_count"],
        "enchant_source_sha256":result["enchant_source_sha256"],
        "highest_quality_J_verified":False,
        "J":None,"environment_ready":False,
        "native_calls":0,"network_calls":0,
    }
