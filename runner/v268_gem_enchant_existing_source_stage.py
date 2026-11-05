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
         selected_source_gem_item_ids=None,selected_special_gem_item_id=None,
         excluded_ordinary_item_id=None):
    """Reuse a sealed v266 source view and only project selected raw gem IDs.

    Raw EffectPointsMin values are NOT proven effective rating, best quality,
    legal sockets or Native accepted gems. No network or SimC run. The CSV
    bytes are still hashed each time, but the full parse is cached by v217.
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
    if selected_special_gem_item_id is not None:
        if (type(selected_special_gem_item_id) is not int or
                selected_special_gem_item_id<=0 or
                selected_source_gem_item_ids is None or
                selected_special_gem_item_id not in
                    selected_source_gem_item_ids or
                (selected_gem_item_ids is not None and
                 selected_special_gem_item_id in selected_gem_item_ids)):
            raise ValueError("V268_SPECIAL_GEM_MUST_BE_SOURCE_BOUND_AND_DISTINCT")
    # Existing selected special is excluded from the ordinary four-type
    # candidates; its effect remains wholly SimC-owned and unmeasured here.
    if excluded_ordinary_item_id is not None:
        if (type(excluded_ordinary_item_id) is not int or
            excluded_ordinary_item_id<=0 or
            selected_source_gem_item_ids is None or
            excluded_ordinary_item_id not in selected_source_gem_item_ids):
            raise ValueError("V268_ORDINARY_EXCLUSION_SOURCE_BOUND_ID_REQUIRED")
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
        # Check original source bytes on EVERY view, including cache hits.
        # A cached join must never hide changed or corrupted CSV/DB2 inputs.
        v221_raw=path.read_bytes()
        records=json.loads(v221_raw.decode("utf8"))
        raw=csv_path.read_bytes()
        if not 0<len(raw)<=source.MAX_BYTES:
            raise ValueError("V268_CSV_SIZE_INVALID")
        raw_sha=hashlib.sha256(raw).hexdigest()
        recorded=sealed["outputs"]["csv"]
        if raw_sha!=recorded["sha256"] or len(raw)!=recorded["size"]:
            raise ValueError("V268_SEALED_CSV_BYTES_CHANGED")
        # The v266 source join is independent of which gems a user selects.
        # Seal it ONCE per exact CSV, v221 artifact, code and game build.
        # Subsequent selections read a small authenticated projection rather
        # than decoding and scanning the full CSV on every preflight.
        join_stage_id="fresh-v266-gem-enchant-join"
        join_version="v266-exact-same-build-source-only-join-v1"
        parser_sha=stage.module_dependency_fingerprint([
            Path(join.__file__),Path(__file__),Path(stage.__file__)
        ])["sha256"]
        join_inputs={
            "game_build":build,
            "source_enchant_sha256":raw_sha,
            "v221_candidate_sha256":hashlib.sha256(v221_raw).hexdigest(),
            "join_code_sha256":parser_sha}
        join_key=stage._input_sha(join_stage_id,join_version,join_inputs)[:20]
        output="fresh_source/v266_exact_gem_enchant_join_"+join_key+".json"
        output_path=root/output
        def execute_join():
            result=join.preview(gem_join=records,raw_enchant_csv=raw,
                                expected_game_build=build)
            output_path.parent.mkdir(parents=True,exist_ok=True)
            output_path.write_text(json.dumps(result,sort_keys=True,
                ensure_ascii=False,separators=(",",":"),allow_nan=False)+"\n",
                encoding="utf8")
        def validate_join(files):
            doc=json.loads(files["joined"].read_text("utf8"))
            return (doc.get("schema")==join.SCHEMA and
                    doc.get("status")==
                        "ENCHANT_RAW_POINTS_SOURCE_ONLY_J_NOT_APPROVED" and
                    doc.get("game_build")==build and
                    doc.get("simc_revision")==records.get("simc_revision") and
                    doc.get("v221_manifest_sha256")==
                        records.get("v213_manifest_sha256") and
                    doc.get("gem_item_link_count")==records.get("exact_link_count") and
                    doc.get("enchant_source_sha256")==raw_sha and
                    type(doc.get("records")) is list and
                    len(doc["records"])==records.get("exact_link_count") and
                    doc.get("highest_quality_selection_verified") is False and
                    doc.get("environment_ready") is False and
                    doc.get("network_calls")==0 and
                    doc.get("native_calls")==0 and
                    doc.get("cache_mutations")==0)
        join_stage=stage.execute_stage(
            root=root,stage_id=join_stage_id+"-"+join_key,
            stage_version=join_version,inputs=join_inputs,
            outputs={"joined":output},execute=execute_join,
            validate=validate_join)
        result=json.loads(output_path.read_text("utf8"))
    except (ValueError,TypeError,KeyError,OSError,
            stage.StageExecutionBlocked,join.EnchantSourceBlocked) as exc:
        return {"status":"GEM_ENCHANT_LOCAL_JOIN_PENDING",
                "reason":str(exc).split(":",1)[0],
                "J":None,"native_calls":0,"network_calls":0}
    # Four nominal CHMV types from the existing same-build v221/v266 join.
    # No SimC effect check, special-gem search, or option admission.
    stat_types=("crit_rating","haste_rating",
                "mastery_rating","versatility_rating")
    four_stat_best={}
    for record in result["records"]:
        item_id=record["item_id"]
        if (item_id in (selected_special_gem_item_id,
                        excluded_ordinary_item_id) or
            item_id in (240967,240983) or
            record["effect_classification"]!=
                "RAW_STATIC_CHMV_POINTS_CANDIDATE_ONLY"):
            continue
        vector=record["raw_static_points_candidate"]
        if (type(vector) is not dict or set(vector)!=set(stat_types) or
            any(type(v) is not int or v<0 for v in vector.values())):
            continue
        nonzero=[stat for stat in stat_types if vector[stat]>0]
        if len(nonzero)!=1:
            continue
        stat=nonzero[0]
        current=four_stat_best.get(stat)
        if (current is None or
            (-vector[stat],item_id)<
            (-current["raw_nominal_points"],current["item_id"])):
            four_stat_best[stat]={
                "item_id":item_id,"raw_nominal_points":vector[stat]}
    # Only the best observed *nominal* point amount is compared.
    # v266 already traversed and verified the exact v221/CSV join. Limit the
    # downstream projection to actually placed gems, not the whole item DB.
    selected={}
    selected_vectors={}
    unresolved=[]
    by_id={row["item_id"]:row for row in result["records"]}
    if selected_gem_item_ids is not None:
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
                selected_vectors[str(item_id)]=dict(vector)
    # The same sealed v266 record also describes the mandatory special gem.
    # It may contribute fixed CHMV, or it may have an unresolved/nonstatic
    # effect. Neither case may be silently interpreted as zero for final J.
    special_effect=None
    if selected_special_gem_item_id is not None:
        row=by_id.get(selected_special_gem_item_id)
        if row is None:
            raise ValueError("V268_SPECIAL_GEM_NOT_IN_SEALED_ENCHANT_JOIN")
        vector=row["raw_static_points_candidate"]
        if row["effect_classification"]=="RAW_STATIC_CHMV_POINTS_CANDIDATE_ONLY":
            if (type(vector) is not dict or
                    set(vector)!={"crit_rating","haste_rating",
                                  "mastery_rating","versatility_rating"} or
                    any(type(amount) is not int or amount<0
                        for amount in vector.values()) or
                    sum(vector.values())<=0):
                raise ValueError("V268_SPECIAL_GEM_RAW_VECTOR_INVALID")
            vector=dict(vector)
        else:
            vector=None
        special_effect={
            "item_id":selected_special_gem_item_id,
            "effect_classification":row["effect_classification"],
            "raw_static_CHMV_vector_candidate_unadmitted":vector,
            "raw_static_CHMV_total_candidate_unadmitted":(
                sum(vector.values()) if vector is not None else None),
            "missing_or_nonstatic_never_assumed_zero":True,
            "simc_effective_rating_verified":False,
            "J_budget_attribution_verified":False}
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
        "four_stat_ordinary_best_observed_unadmitted":four_stat_best,
        "four_stat_ordinary_source_complete_unadmitted":(
            set(four_stat_best)==set(stat_types)),
        "four_stat_effect_or_special_role_reverified":False,
        **source_membership,
        "selected_gem_raw_points_by_id_unadmitted":selected,
        "selected_gem_raw_CHMV_vectors_by_id_unadmitted":selected_vectors,
        "selected_special_gem_raw_effect_unadmitted":special_effect,
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
