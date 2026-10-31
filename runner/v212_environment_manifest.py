#!/usr/bin/env python3
"""v212: deterministic, Native0 Environment Manifest from the real v213 catalog.

Consumes the exact source-to-catalog artifact, the existing v196 approval
projection, and a v098 current-season target profile. It does not collect,
generate profiles, run SimC, or execute the optimizer.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import v143_specialization_contracts as specs
import v046_static_item_cache as item_cache
import v062_static_budget_bridge as budget
import v196_current_season_user_catalog as ui_catalog
import v206_nonchmv_eagle_selection as eagle
import v213_source_to_catalog as source_bridge

SCHEMA = "v212_simc_environment_manifest_v2"
V098 = "v098_target_ilevel_user_scenario_v1"
EXPECTED_APPROVED_ENCHANT_IDS = [7967]
EXPECTED_ENCHANT_COUNT = 38

WINDOWS_PACKAGE_SCHEMA = "v181_windows_local_web_beta_source_package_v1"
EXPECTED_SIMC_REVISION_LENGTH = 40


class EnvironmentBlocked(ValueError):
    pass


def need(condition, code):
    if not condition:
        raise EnvironmentBlocked(code)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def valid_sha(value):
    return (type(value) is str and len(value) == 64 and
            all(ch in "0123456789abcdef" for ch in value))


def read_json(path, max_bytes=25_000_000):
    path = Path(path).resolve()
    need(path.is_file() and 0 < path.stat().st_size <= max_bytes,
         "INPUT_FILE_MISSING_OR_SIZE_INVALID:" + path.name)
    raw = path.read_bytes()
    try:
        return json.loads(raw.decode("utf8")), sha(raw)
    except (UnicodeError, ValueError) as exc:
        raise EnvironmentBlocked("INPUT_JSON_INVALID:" + path.name) from exc


def verify_windows_package_manifest(package_manifest_path, source_catalog_path,
                                      source_catalog, source_catalog_sha):
    if package_manifest_path is None:
        return {"status": "NOT_PROVIDED"}
    raw_path = Path(package_manifest_path)
    need(raw_path.is_file() and not raw_path.is_symlink(),
         "WINDOWS_PACKAGE_MANIFEST_MISSING_OR_INVALID")
    package_path = raw_path.resolve()
    package, package_sha = read_json(package_path, max_bytes=5_000_000)
    package_root = package_path.parent
    source_path = Path(source_catalog_path).resolve()
    need(source_path.is_file() and
         sha_file(source_path)["sha256"] == source_catalog_sha,
         "WINDOWS_PACKAGE_SOURCE_CATALOG_BYTES_CHANGED")
    try:
        relative = source_path.relative_to(package_root).as_posix()
    except ValueError as exc:
        raise EnvironmentBlocked(
            "WINDOWS_PACKAGE_SOURCE_CATALOG_ESCAPES_PACKAGE_ROOT") from exc
    need(package.get("schema") == WINDOWS_PACKAGE_SCHEMA and
         package.get("archive_root") == package_root.name,
         "WINDOWS_PACKAGE_MANIFEST_IDENTITY_INVALID")
    source = package.get("source_catalog")
    need(type(source) is dict and
         relative == "data/current_season_source_to_catalog.json" and
         source.get("path") == relative and
         source.get("schema") == source_catalog.get("schema") and
         source.get("artifact_sha256") == source_catalog_sha and
         source.get("manifest_sha256") == source_catalog.get("manifest_sha256") and
         source.get("game_build") == source_catalog.get("game_build") and
         source.get("simc_revision") == source_catalog.get("simc_revision") and
         source.get("native_calls") == 0 and
         source.get("network_calls") == 0 and
         source.get("automatic_ui_promotion") is False,
         "WINDOWS_PACKAGE_SOURCE_CATALOG_IDENTITY_MISMATCH")
    files = package.get("files")
    need(type(files) is list and
         type(package.get("file_count")) is int and
         package["file_count"] == len(files) and
         all(type(row) is dict and type(row.get("path")) is str
             for row in files) and
         len({row["path"] for row in files}) == len(files),
         "WINDOWS_PACKAGE_FILE_MANIFEST_INVALID")
    matches = [row for row in files if row["path"] == relative]
    need(len(matches) == 1 and
         matches[0].get("sha256") == source_catalog_sha and
         matches[0].get("size") == source_path.stat().st_size,
         "WINDOWS_PACKAGE_SOURCE_CATALOG_FILE_SHA_MISMATCH")
    return {
        "status": "VERIFIED",
        "schema": package["schema"],
        "manifest_sha256": package_sha,
        "archive_root": package["archive_root"],
        "file_count": package["file_count"],
        "source_catalog_path": relative,
        "source_catalog_sha256": source_catalog_sha,
    }


def sha_file(path):
    path = Path(path).resolve()
    need(path.is_file(), "RUNTIME_BINARY_OR_CACHE_MISSING:" + path.name)
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            size += len(chunk)
            digest.update(chunk)
    return {"basename": path.name, "size_bytes": size,
            "sha256": digest.hexdigest()}


def file_identity(path, root):
    path = Path(path).resolve()
    root = Path(root).resolve()
    need(path.is_file(), "TARGET_PROFILE_FILE_MISSING:" + path.name)
    try:
        relative = path.relative_to(root).as_posix()
    except ValueError as exc:
        raise EnvironmentBlocked("TARGET_PROFILE_FILE_ESCAPES_ROOT") from exc
    raw = path.read_bytes()
    return {"path": relative, "size_bytes": len(raw), "sha256": sha(raw)}


def _source_identity(source_catalog, source_catalog_sha):
    source_bridge.verify_catalog(source_catalog)
    need(valid_sha(source_catalog_sha), "V213_ARTIFACT_FILE_SHA256_INVALID")
    need(source_catalog.get("schema") == source_bridge.SCHEMA
         and source_catalog.get("native_calls") == 0
         and source_catalog.get("network_calls") == 0
         and source_catalog.get("automatic_ui_promotion") is False
         and source_catalog.get("selection_state_mutated") is False
         and source_catalog.get("simc_effect_reimplemented") is False,
         "V213_SOURCE_CATALOG_CONTRACT_INVALID")
    provenance = source_catalog.get("source_provenance")
    need(type(provenance) is dict and
         type(provenance.get("v191")) is dict and
         type(provenance.get("v211")) is dict,
         "V213_SOURCE_PROVENANCE_MISSING")
    v191 = provenance["v191"]
    v211 = provenance["v211"]
    need(v191.get("schema") == "v191_unified_patch_season_expansion_data_candidates_v1"
         and valid_sha(v191.get("sha256"))
         and v211.get("schema") ==
             "v211_current_season_enchant_effect_classification_v1"
         and valid_sha(v211.get("sha256")),
         "V213_COMPONENT_SOURCE_IDENTITY_INVALID")
    build = source_catalog.get("game_build")
    revision = source_catalog.get("simc_revision")
    need(type(build) is str and bool(build) and
         type(revision) is str and
         len(revision) == EXPECTED_SIMC_REVISION_LENGTH and
         all(ch in "0123456789abcdef" for ch in revision),
         "V213_GAME_BUILD_OR_SIMC_REVISION_INVALID")
    need(type(v191.get("sha256_by_input")) is dict and
         set(v191["sha256_by_input"]) ==
             {"gear", "tier", "budget", "v189", "v190"} and
         all(valid_sha(x) for x in v191["sha256_by_input"].values()),
         "V213_V191_INPUT_SOURCE_SHA256_INVALID")
    generated = v191.get("simc_generated_sources")
    need(type(generated) is dict and set(generated) ==
         {"permanent_enchant", "temporary_enchant", "gem_property"} and
         all(type(row) is dict and row.get("source_build") == build and
             type(row.get("declared_rows")) is int and
             row["declared_rows"] > 0 and valid_sha(row.get("sha256"))
             for row in generated.values()),
         "V213_SIMC_GENERATED_SOURCE_SHA256_INVALID")
    need(v211.get("candidate_source_schema") == v191["schema"] and
         v211.get("candidate_source_artifact_id") is None,
         "V213_V211_CANDIDATE_SOURCE_IDENTITY_INVALID")
    return build, revision, v191, v211


def _approved_enchants(source_catalog, ui):
    items = ui.get("enchant_candidates", {}).get("items")
    need(type(items) is list and len(items) == EXPECTED_ENCHANT_COUNT
         and ui.get("enchant_candidates", {}).get("total") ==
             EXPECTED_ENCHANT_COUNT,
         "V196_ENCHANT_CATALOG_COVERAGE_MISMATCH")
    selectable = [row for row in items if row.get("ui_selectable") is True]
    approved_ids = sorted(row.get("enchant_id") for row in selectable)
    need(approved_ids == EXPECTED_APPROVED_ENCHANT_IDS,
         "V196_EXACT_APPROVED_ENCHANT_ID_MISMATCH")
    approved = selectable[0]
    need(approved.get("token") == "enchant_ring__eyes_of_the_eagle"
         and approved.get("effect_family") == "crit_effectiveness",
         "V196_APPROVED_ENCHANT_IDENTITY_MISMATCH")
    joined = source_catalog["catalog"]["enchants"]["items"]
    by_id = {row["enchant_id"]: row for row in joined}
    need(len(by_id) == EXPECTED_ENCHANT_COUNT and 7967 in by_id
         and 8025 in by_id,
         "V213_ENCHANT_SOURCE_ID_SET_INVALID")
    need(by_id[7967].get("selection_status") ==
             "EXISTING_EAGLE_ONE_SCOPE_USER_CHOICE"
         and by_id[8025].get("selection_status") ==
             "DEVELOPER_ONLY_EXACT_SCOPE"
         and by_id[7967].get("ui_selectable") is False
         and by_id[8025].get("ui_selectable") is False,
         "V213_EXISTING_APPROVAL_SOURCE_BOUNDARY_INVALID")
    need(all(row.get("ui_selectable") is False for row in joined),
         "V213_CLASSIFIER_GRANTED_USER_SELECTION")
    need(source_catalog["catalog"]["enchants"]["selection_policy"].get(
             "only_existing_native_scoped_choice") == 7967
         and source_catalog["catalog"]["enchants"]["selection_policy"].get(
             "developer_only") == [8025]
         and source_catalog["catalog"]["enchants"]["selection_policy"].get(
             "all_other_candidates_remain_locked") is True,
         "V213_ENCHANT_SELECTION_POLICY_DRIFT")
    return approved_ids, by_id


def _selected_enchant(bootstrap, profile_text, approved_ids):
    selected = bootstrap.get("selected_nonchmv_enchant")
    profile_ring = [line for line in profile_text.splitlines()
                    if line.startswith("finger1=")]
    need(len(profile_ring) == 1, "V098_PROFILE_FINGER1_ASSIGNMENT_INVALID")
    if selected is None:
        need("enchant_id=7967" not in profile_ring[0],
             "V098_UNDECLARED_EAGLE_ENCHANT_IN_PROFILE")
        return {"selected_id": None, "slot": None,
                "static_CHMV_E": None,
                "budget_increment": 0,
                "status": "NO_OPTIONAL_ENCHANT_SELECTED"}
    need(approved_ids == EXPECTED_APPROVED_ENCHANT_IDS
         and type(selected) is dict
         and selected.get("schema") == eagle.SCHEMA
         and selected.get("choice") == eagle.CHOICE
         and selected.get("effect_family") == "crit_effectiveness"
         and selected.get("static_CHMV_E") == eagle.E_ZERO
         and selected.get("budget_policy") ==
             "NON_CHMV_NO_CHANGE_TO_REFERENCE_B_OR_FINAL_T",
         "V098_SELECTED_ENCHANT_NOT_EXACT_EXISTING_APPROVAL")
    need(profile_ring[0].count("enchant_id=7967") == 1,
         "V098_APPROVED_ENCHANT_NOT_PRESENT_EXACTLY_ONCE")
    return {"selected_id": 7967, "slot": "finger1",
            "static_CHMV_E": dict(eagle.E_ZERO),
            "budget_increment": 0,
            "evidence_scope": "ONE_WINDOWS_PALADIN334_STATIC_E_ZERO_NOT_ALL_DPS",
            "status": "EXISTING_7967_APPROVAL_PRESERVED"}


def _selected_special_L(scenario, static_cache_identity):
    equipment = scenario.get("equipment")
    need(type(equipment) is dict and
         type(equipment.get("special")) is list,
         "V098_SCENARIO_SPECIAL_EQUIPMENT_INVALID")
    rows = equipment["special"]
    normalized = []
    for row in rows:
        need(type(row) is dict and type(row.get("slot")) is str and
             type(row.get("item_id")) is int and
             type(row.get("ilevel")) is int and
             type(row.get("options")) is dict,
             "V098_SELECTED_SPECIAL_IDENTITY_INVALID")
        normalized.append({
            "slot": row["slot"], "item_id": row["item_id"],
            "ilevel": row["ilevel"], "options": row["options"],
        })
    normalized.sort(key=lambda x: (x["slot"], x["item_id"], x["ilevel"]))
    need(not normalized or static_cache_identity is not None,
         "SELECTED_SPECIAL_STATIC_L_CACHE_SNAPSHOT_MISSING")
    return {
        "selected_count": len(normalized),
        "selected_identity_sha256": sha(
            canonical(normalized).encode("utf8")),
        "static_cache": static_cache_identity,
        "verification": (
            "V098_PLAN_ACCEPTED_WITH_STATIC_CACHE_SNAPSHOT"
            if normalized else "NO_SELECTED_SPECIAL_L"),
        "native_calls_in_manifest_build": 0,
        "v208_policy": "EXISTING_SELECTED_ONLY_ONE_NATIVE_ON_MISS_CACHE_REUSED",
    }


def _verify_v208_start_receipt(receipt, scenario, source_catalog,
                                source_catalog_sha, revision, binary,
                                static_cache_identity, special_L):
    if special_L["selected_count"] == 0:
        need(receipt is None, "V208_RECEIPT_WITHOUT_SELECTED_SPECIAL")
        return {"status":"NOT_REQUIRED_NO_SELECTED_SPECIAL"}
    if receipt is None:
        return {"status":"NOT_PROVIDED"}
    need(type(receipt) is dict and
         receipt.get("schema")=="v208_selected_special_start_receipt_v1" and
         receipt.get("status")=="VERIFIED",
         "V208_START_RECEIPT_SCHEMA_OR_STATUS_INVALID")
    receipt_payload={k:v for k,v in receipt.items() if k!="receipt_sha256"}
    need(valid_sha(receipt.get("receipt_sha256")) and
         receipt["receipt_sha256"]==
         sha(canonical(receipt_payload).encode("utf8")),
         "V208_START_RECEIPT_DIGEST_MISMATCH")
    selected=scenario["equipment"]["special"]
    expected=[budget.exact_identity(row) for row in selected]
    actual=[row.get("selected_identity")
            for row in receipt.get("selected_specials",[])
            if type(row) is dict]
    expected.sort(key=lambda x:(x["slot"],x["item_id"],x["ilevel"]))
    actual.sort(key=lambda x:(x.get("slot",""),x.get("item_id",0),
                              x.get("ilevel",0)) if type(x) is dict else ("",0,0))
    need(len(actual)==special_L["selected_count"] and actual==expected,
         "V208_RECEIPT_SELECTED_SPECIAL_IDENTITY_MISMATCH")
    rows=receipt["selected_specials"]
    need(receipt.get("selected_special_count")==len(rows),
         "V208_RECEIPT_SELECTED_SPECIAL_COUNT_MISMATCH")
    hits=0
    misses=0
    new_misses=0
    native_hashes=set()
    for row in rows:
        selected_identity=row["selected_identity"]
        bare_raw={"slot":selected_identity["slot"],
                  "item_id":selected_identity["item_id"],
                  "ilevel":selected_identity["ilevel"],
                  "options":selected_identity["options"]}
        expected_bare=budget.exact_identity(budget.undecorated_special(bare_raw))
        need(row.get("selected_identity_sha256")==
             sha(canonical(selected_identity).encode("utf8")) and
             row.get("bare_identity")==expected_bare and
             row.get("bare_identity_sha256")==
             sha(canonical(expected_bare).encode("utf8")),
             "V208_RECEIPT_BARE_SPECIAL_IDENTITY_MISMATCH")
        need(row.get("cache_status") in
             ("HIT","MISS_NEW_NATIVE_JSON2","MISS_REUSED_NATIVE_JSON2"),
             "V208_RECEIPT_CACHE_STATUS_INVALID")
        if row["cache_status"]=="HIT":
            hits+=1
        else:
            misses+=1
            if row["cache_status"]=="MISS_NEW_NATIVE_JSON2":
                new_misses+=1
        need(valid_sha(row.get("static_digest")),
             "V208_RECEIPT_STATIC_DIGEST_INVALID")
        measured=row.get("measured_L")
        need(type(measured) is dict and set(measured)==set(item_cache.STATS)
             and all(type(value) is int and 0<=value<=100000
                     for value in measured.values()),
             "V208_RECEIPT_MEASURED_L_INVALID")
        source_kind=row.get("source_kind")
        native=row.get("native_json2")
        need(type(native) is dict,
             "V208_RECEIPT_NATIVE_JSON2_RECORD_MISSING")
        if source_kind=="NATIVE_JSON2_RESOLVED_VARIANT":
            need(valid_sha(native.get("sha256")) and
                 type(native.get("revision")) is str and
                 native["revision"].startswith(revision[:7]) and
                 type(native.get("source")) is str and bool(native["source"]),
                 "V208_RECEIPT_NATIVE_JSON2_PROVENANCE_INVALID")
            native_hashes.add(native["sha256"])
        else:
            need(source_kind=="USER_REQUESTED_MANUAL_CORRECTION" and
                 native.get("sha256") is None and
                 native.get("revision") is None,
                 "V208_RECEIPT_STATIC_SOURCE_UNSUPPORTED")
        if row["cache_status"] in (
                "MISS_NEW_NATIVE_JSON2","MISS_REUSED_NATIVE_JSON2"):
            need(source_kind=="NATIVE_JSON2_RESOLVED_VARIANT",
                 "V208_RECEIPT_NEW_MISS_NOT_NATIVE_RESOLVED")
    summary=receipt.get("cache_summary")
    need(type(summary) is dict and
         summary.get("hits")==hits and summary.get("misses")==misses and
         type(receipt.get("native_calls_this_start")) is int and
         summary.get("native_calls_this_start")==
             receipt.get("native_calls_this_start") and
         receipt.get("native_calls_this_start")== (1 if new_misses else 0),
         "V208_RECEIPT_CACHE_OR_NATIVE_COUNT_MISMATCH")
    need(receipt.get("native_json2_sha256s")==sorted(native_hashes),
         "V208_RECEIPT_NATIVE_JSON2_SHA_LIST_MISMATCH")
    simc=receipt.get("simc")
    need(type(simc) is dict and simc.get("revision")==revision and
         simc.get("binary_sha256")==binary.get("sha256"),
         "V208_RECEIPT_SIMC_BINARY_IDENTITY_MISMATCH")
    cache=receipt.get("static_cache")
    need(type(cache) is dict and static_cache_identity is not None and
         cache.get("sha256")==static_cache_identity.get("sha256") and
         cache.get("size_bytes")==static_cache_identity.get("size_bytes") and
         cache.get("basename")==static_cache_identity.get("basename"),
         "V208_RECEIPT_STATIC_CACHE_IDENTITY_MISMATCH")
    source=receipt.get("source_catalog")
    need(type(source) is dict and
         source.get("schema")==source_catalog["schema"] and
         source.get("artifact_sha256")==source_catalog_sha and
         source.get("manifest_sha256")==source_catalog["manifest_sha256"] and
         source.get("game_build")==source_catalog["game_build"] and
         source.get("simc_revision")==revision,
         "V208_RECEIPT_SOURCE_CATALOG_IDENTITY_MISMATCH")
    return {
        "status":"VERIFIED",
        "schema":receipt["schema"],
        "receipt_sha256":receipt["receipt_sha256"],
        "selected_special_count":len(rows),
        "selected_identity_sha256":special_L["selected_identity_sha256"],
        "static_cache_sha256":static_cache_identity["sha256"],
        "cache_hits":hits,"cache_misses":misses,
        "native_calls_this_start":receipt["native_calls_this_start"],
        "native_json2_sha256s":sorted(native_hashes),
    }


def _verify_profile_supplier_coverage(bootstrap, v191, build, archetype):
    coverage=bootstrap.get("profile_supplier_coverage")
    expected=sorted(specs.CONTRACTS)
    need(type(coverage) is dict and
         coverage.get("schema")=="v215_profile_supplier_coverage_v1" and
         coverage.get("status")=="CURRENT_SEASON_PLAN_SUPPLIERS_26_OF_26",
         "V098_PROFILE_SUPPLIER_COVERAGE_MISSING")
    need(coverage.get("supported_specializations")==expected and
         coverage.get("contract_count")==26 and
         coverage.get("legacy_source_backed_count")==24 and
         coverage.get("source_independent_count")==2 and
         coverage.get("user_input_default_count")==26 and
         coverage.get("starter_default_count")==26 and
         coverage.get("season_catalog_count")==26 and
         coverage.get("current_season_profile_supplier_count")==26 and
         coverage.get("selected_specialization")==archetype and
         coverage.get("selected_specialization_plan_supplier") is True and
         coverage.get("season_build")==build and
         coverage.get("all_specs_ready") is False and
         coverage.get("adaptive_native_evidence_complete") is False and
         coverage.get("native_calls")==0 and
         coverage.get("network_calls")==0,
         "V098_PROFILE_SUPPLIER_COVERAGE_CONTRACT_INVALID")
    source_hashes=coverage.get("source_input_sha256")
    expected_hashes=v191["sha256_by_input"]
    need(type(source_hashes) is dict and
         set(source_hashes)=={"gear","tier","budget"} and
         all(valid_sha(value) for value in source_hashes.values()) and
         all(source_hashes[key]==expected_hashes[key]
             for key in ("gear","tier","budget")),
         "V098_PROFILE_SUPPLIER_SOURCE_INPUT_SHA_MISMATCH")
    code_hashes=coverage.get("supplier_code_sha256")
    need(type(code_hashes) is dict and
         set(code_hashes)=={"contracts","profile_composer",
                            "user_session","season_stage"} and
         all(valid_sha(value) for value in code_hashes.values()),
         "V098_PROFILE_SUPPLIER_CODE_IDENTITY_INVALID")
    return coverage


# Declarative dependency edges are consumed by the generic DAG evaluator
# below. Each edge is upstream -> directly affected downstream component.
# Transitive invalidation and execution ordering are derived by the engine,
# not duplicated as hand-maintained per-input impact lists.
DEPENDENCY_INVALIDATION_RULES={
    "v213_source_catalog":(
        "v196_ui_projection","v098_profile","v208_receipt_validation",
        "session_identity"),
    "v191_gear_input":(
        "v213_source_catalog","v098_profile","session_identity"),
    "v191_tier_input":(
        "v213_source_catalog","v098_profile","session_identity"),
    "v191_budget_input":(
        "v213_source_catalog","v098_budget_plan","session_identity"),
    "v196_ui_projection":("v098_selected_choice","session_identity"),
    "v098_selected_choice":("v098_profile",),
    "v098_budget_plan":("v098_profile",),
    "v098_profile":("environment_manifest","optimizer_session"),
    "selected_special_identity":(
        "v208_receipt_validation","optimizer_session"),
    "static_item_cache":(
        "v208_receipt_validation","optimizer_session"),
    "v208_start_receipt":("environment_manifest",),
    "v208_receipt_validation":(
        "environment_manifest","optimizer_session"),
    "windows_package_manifest":(
        "environment_manifest","start_runtime_verification"),
    "simc_binary":(
        "environment_manifest","optimizer_session","adaptive_dps_cache"),
    "simc_revision":(
        "environment_manifest","optimizer_session","adaptive_dps_cache"),
    "session_identity":("optimizer_session",),
    "optimizer_session":("adaptive_dps_cache",),
}
DEPENDENCY_GRAPH_SCHEMA="v212_environment_dependency_graph_v2"


def _validated_dependency_edges(edges):
    need(type(edges) is dict, "DEPENDENCY_GRAPH_EDGES_OBJECT_REQUIRED")
    normalized={}
    for upstream,downstream in edges.items():
        need(type(upstream) is str and bool(upstream.strip()) and
             type(downstream) in (list,tuple) and
             all(type(node) is str and bool(node.strip()) for node in downstream) and
             len(set(downstream))==len(downstream),
             "DEPENDENCY_GRAPH_EDGE_INVALID")
        normalized[upstream]=tuple(sorted(downstream))
    nodes=set(normalized)
    for downstream in normalized.values():
        nodes.update(downstream)
    indegree={node:0 for node in nodes}
    adjacency={node:[] for node in nodes}
    for upstream,downstream in normalized.items():
        for node in downstream:
            adjacency[upstream].append(node)
            indegree[node]+=1
    ready=sorted(node for node,count in indegree.items() if count==0)
    order=[]
    while ready:
        node=ready.pop(0)
        order.append(node)
        for child in sorted(adjacency[node]):
            indegree[child]-=1
            if indegree[child]==0:
                ready.append(child)
                ready.sort()
    need(len(order)==len(nodes), "DEPENDENCY_GRAPH_CYCLE")
    return normalized,tuple(order),nodes


def _dependency_closure(changed_inputs, edges):
    invalidated=set()
    pending=list(sorted(changed_inputs))
    while pending:
        upstream=pending.pop(0)
        for downstream in edges.get(upstream,()):
            if downstream not in invalidated:
                invalidated.add(downstream)
                pending.append(downstream)
    return invalidated


def compare_dependency_graphs(previous_manifest, current_graph):
    """Evaluate a declarative DAG without mutating sessions, caches or inputs.

    The result is an execution plan, not proof that a component was reused.
    Runtime adapters must separately report whether work was actually skipped,
    recomputed identically, or rebuilt.
    """
    need(type(current_graph) is dict and
         current_graph.get("schema")==DEPENDENCY_GRAPH_SCHEMA,
         "DEPENDENCY_GRAPH_SCHEMA_INVALID")
    current=current_graph.get("fingerprints")
    need(type(current) is dict and
         all(type(key) is str and bool(key.strip()) for key in current),
         "DEPENDENCY_GRAPH_FINGERPRINTS_INVALID")
    edges,topological_order,nodes=_validated_dependency_edges(
        current_graph.get("invalidation_rules"))
    need(set(current)<=nodes, "DEPENDENCY_GRAPH_FINGERPRINT_NODE_MISSING")
    component_nodes=set(node for values in edges.values() for node in values)

    if previous_manifest is None:
        changed=sorted(current)
        invalidated=_dependency_closure(changed,edges)
        same_static=True
        rules_changed=False
        previous_sha=None
        reusable=[]
    else:
        need(type(previous_manifest) is dict,
             "PREVIOUS_ENVIRONMENT_MANIFEST_OBJECT_REQUIRED")
        previous_payload={k:v for k,v in previous_manifest.items()
                          if k!="manifest_sha256"}
        need(valid_sha(previous_manifest.get("manifest_sha256")) and
             sha(canonical(previous_payload).encode("utf8"))==
                 previous_manifest["manifest_sha256"],
             "PREVIOUS_ENVIRONMENT_MANIFEST_DIGEST_INVALID")
        old_graph=previous_manifest.get("dependency_graph")
        need(type(old_graph) is dict and
             type(old_graph.get("fingerprints")) is dict,
             "PREVIOUS_DEPENDENCY_GRAPH_INVALID")
        old=old_graph["fingerprints"]
        changed=sorted(key for key in set(old)|set(current)
                       if old.get(key)!=current.get(key))
        rules_changed=(
            old_graph.get("schema")!=DEPENDENCY_GRAPH_SCHEMA or
            old_graph.get("invalidation_rules")!=
                current_graph.get("invalidation_rules"))
        if rules_changed:
            changed.append("$dependency_graph")
            changed.sort()
            invalidated=set(component_nodes)
        else:
            invalidated=_dependency_closure(changed,edges)
        same_static=(old.get("static_item_cache")==
                     current.get("static_item_cache"))
        previous_sha=previous_manifest.get("manifest_sha256")
        reusable=sorted(
            node for node in topological_order
            if node in component_nodes and node not in invalidated
            and node not in changed)

    execution_order=[node for node in topological_order
                     if node in invalidated and node in component_nodes]
    return {
        "status":"INITIAL_ENVIRONMENT" if previous_manifest is None else
                 ("DEPENDENCIES_CHANGED" if changed else "UNCHANGED"),
        "previous_manifest_sha256":previous_sha,
        "changed_inputs":changed,
        "invalidated_components":sorted(invalidated),
        "planned_execution_order":execution_order,
        "reusable_candidates":reusable,
        "dependency_rules_changed":rules_changed,
        "static_item_cache_preserved":same_static,
        "historical_sessions_preserved":True,
        "cache_mutations":0,"native_calls":0,
    }


def _dependency_graph(source_catalog_sha, v191, ui_sha,
                      bootstrap_identity_sha, profile_files, special_L,
                      static_cache_identity, v208_receipt_identity,
                      windows_package, binary, revision):
    fingerprints={
        "v213_source_catalog":source_catalog_sha,
        "v191_gear_input":v191["sha256_by_input"]["gear"],
        "v191_tier_input":v191["sha256_by_input"]["tier"],
        "v191_budget_input":v191["sha256_by_input"]["budget"],
        "v196_ui_projection":ui_sha,
        "v098_profile":bootstrap_identity_sha,
        "selected_special_identity":special_L["selected_identity_sha256"],
        "static_item_cache":(static_cache_identity["sha256"]
                             if static_cache_identity else None),
        "v208_start_receipt":v208_receipt_identity.get("receipt_sha256"),
        "windows_package_manifest":windows_package.get("manifest_sha256"),
        "simc_binary":binary["sha256"],
        "simc_revision":revision,
    }
    return {
        "schema":DEPENDENCY_GRAPH_SCHEMA,
        "fingerprints":fingerprints,
        "invalidation_rules":{
            key:list(value) for key,value in DEPENDENCY_INVALIDATION_RULES.items()},
        "cache_policy":{
            "static_item_cache":
                "PRESERVE_UNLESS_EXACT_VARIANT_IDENTITY_CHANGED; REVISION_ONLY_DOES_NOT_PURGE",
            "dps_cache":
                "BINARY_REVISION_PROFILE_CANDIDATE_COMBAT_AND_ITERATION_IDENTITY",
            "historical_sessions":
                "IMMUTABLE; DEPENDENCY_CHANGES_CREATE_OR_REQUIRE_A_NEW_SESSION",
        },
    }


def compile_manifest(source_catalog, source_catalog_sha, ui, ui_sha,
                     bootstrap, target_root, v208_start_receipt=None,
                     windows_package=None, previous_environment_manifest=None):
    build, revision, v191, v211 = _source_identity(
        source_catalog, source_catalog_sha)
    need(ui.get("schema") == ui_catalog.SCHEMA
         and ui.get("season_build") == build
         and ui.get("simc_revision") == revision,
         "V196_APPROVED_CATALOG_BUILD_OR_REVISION_MISMATCH")
    need(valid_sha(ui_sha), "V196_NORMALIZED_UI_CATALOG_SHA256_INVALID")
    source_ui = ui.get("source_catalog")
    need(type(source_ui) is dict and
         source_ui.get("schema") == source_catalog["schema"] and
         source_ui.get("manifest_sha256") ==
             source_catalog.get("manifest_sha256"),
         "V196_UI_NOT_DERIVED_FROM_EXACT_V213_ARTIFACT")
    approved_ids, source_enchants = _approved_enchants(source_catalog, ui)
    windows_package = ({"status":"NOT_PROVIDED"}
                       if windows_package is None else windows_package)
    need(type(windows_package) is dict and
         windows_package.get("status") in ("VERIFIED", "NOT_PROVIDED"),
         "WINDOWS_PACKAGE_IDENTITY_INVALID")

    need(bootstrap.get("schema") == V098
         and bootstrap.get("native_calls") == 0
         and bootstrap.get("status") == "READY_INTERNAL_MANIFEST_ZERO_NATIVE"
         and bootstrap.get("current_season_product") is True,
         "V098_CURRENT_SEASON_TARGET_PROFILE_NOT_PLAN_READY")
    need(bootstrap.get("all_specs_ready") is False or
         bootstrap.get("all_specs_ready") is True,
         "V098_ARCHETYPE_SCOPE_FLAG_MISSING")
    archetype = bootstrap.get("template_archetype")
    target_ilevel = bootstrap.get("target_ilevel")
    need(type(archetype) is str and archetype in specs.CONTRACTS
         and len(specs.CONTRACTS) == 26
         and "evoker/augmentation" not in specs.CONTRACTS
         and all(row.get("role") in ("attack", "spell")
                 for row in specs.CONTRACTS.values()),
         "PRODUCT_DPS_26_SPECIALIZATION_CONTRACT_DRIFT")
    need(type(target_ilevel) is int,
         "V098_TARGET_IDENTITY_MISSING")
    profile_supplier_coverage=_verify_profile_supplier_coverage(
        bootstrap,v191,build,archetype)
    plan = bootstrap.get("plan")
    need(type(plan) is dict and type(plan.get("base_B")) is int
         and type(plan.get("final_T")) is int,
         "V098_TARGET_BUDGET_PLAN_MISSING")

    target_root = Path(target_root).resolve()
    generated = Path(bootstrap.get("generated_manifest", "")).resolve()
    need(generated.parent == target_root and generated.name == "manifest.json",
         "V098_GENERATED_MANIFEST_OUTSIDE_TARGET_ROOT")
    profile_files = {}
    for name in ("manifest.json", "profile.simc", "scenario.json", "fillers.json"):
        profile_files[name] = file_identity(target_root / name, target_root)
    target_manifest, _ = read_json(generated)
    need(target_manifest.get("profile_simc") == "profile.simc"
         and target_manifest.get("scenario_json") == "scenario.json"
         and target_manifest.get("fillers_json") == "fillers.json",
         "V098_PROFILE_MANIFEST_FILE_BINDING_INVALID")
    need(target_manifest.get("native_limit") == 6
         and target_manifest.get("native_revision") == revision,
         "V098_ADAPTIVE_LIMIT_OR_SIMC_REVISION_CHANGED")
    binary = sha_file(target_manifest.get("native_binary", ""))
    static_cache = target_manifest.get("static_cache_json")
    static_cache_identity = sha_file(static_cache) if static_cache else None
    profile_text = (target_root / "profile.simc").read_text(encoding="utf8")
    selected_enchant = _selected_enchant(bootstrap, profile_text, approved_ids)
    scenario, scenario_sha = read_json(target_root / "scenario.json")
    special_L = _selected_special_L(scenario, static_cache_identity)
    v208_receipt_identity = _verify_v208_start_receipt(
        v208_start_receipt, scenario, source_catalog, source_catalog_sha,
        revision, binary, static_cache_identity, special_L)

    # Hash a machine-independent projection; do not leak local absolute paths.
    target_manifest_identity = {
        "profile_simc": target_manifest["profile_simc"],
        "scenario_json": target_manifest["scenario_json"],
        "fillers_json": target_manifest["fillers_json"],
        "native_revision": target_manifest["native_revision"],
        "native_limit": target_manifest["native_limit"],
        "weapon_layout": target_manifest.get("weapon_layout"),
        "oil_hands": target_manifest.get("oil_hands"),
        "flask_F": target_manifest.get("flask_F"),
        "seed_targets_B": target_manifest.get("seed_targets_B"),
        "static_cache_sha256": (
            static_cache_identity["sha256"] if static_cache_identity else None),
    }
    target_manifest_identity_sha = sha(
        canonical(target_manifest_identity).encode("utf8"))
    bootstrap_identity = {
        "schema": bootstrap["schema"],
        "status": bootstrap["status"],
        "template_archetype": archetype,
        "target_ilevel": target_ilevel,
        "base_B": plan["base_B"],
        "final_T": plan["final_T"],
        "native_calls": bootstrap["native_calls"],
        "current_season_product": bootstrap["current_season_product"],
        "all_specs_ready": bootstrap["all_specs_ready"],
        "profile_supplier_coverage":profile_supplier_coverage,
        "source_independent_334_user_session":
            bootstrap.get("source_independent_334_user_session"),
        "source_independent_non334_user_session":
            bootstrap.get("source_independent_non334_user_session"),
        "selected_nonchmv_enchant": selected_enchant,
        "selected_special_identity_sha256":
            special_L["selected_identity_sha256"],
        "plan_identity": {
            key: plan[key] for key in (
                "class", "spec", "item_slots", "fixed_O", "budget_source",
                "scenario_digest", "source_profile_sha256")
            if key in plan
        },
    }
    bootstrap_identity_sha = sha(canonical(bootstrap_identity).encode("utf8"))
    limitations = list(source_catalog.get("readiness_limitations", []))
    if not profile_supplier_coverage["all_specs_ready"]:
        limitations.append(
            "ALL_26_ADAPTIVE_PROFILE_NATIVE_ACCEPTANCE_NOT_COMPLETE")
    if ui.get("enchant_candidates", {}).get("source_classification_counts", {}).get(
            "native_E_measured", 0) < EXPECTED_ENCHANT_COUNT:
        limitations.append("ENCHANT_SOURCE_CLASSIFICATION_IS_NOT_GENERAL_NATIVE_E")
    if (special_L["selected_count"] and
            v208_receipt_identity["status"]!="VERIFIED"):
        limitations.append(
            "V208_SELECTED_SPECIAL_L_START_RECEIPT_NOT_YET_SERIALIZED_IN_ENVIRONMENT_MANIFEST")
    if windows_package["status"] != "VERIFIED":
        limitations.append("V213_WINDOWS_PACKAGE_MANIFEST_NOT_VERIFIED")
    limitations.append("WINDOWS_ONE_CLICK_BUILD_START_PROGRESS_CANCEL_RESUME_NOT_FULLY_ACCEPTED")
    limitations = list(dict.fromkeys(limitations))
    unresolved = []
    if not profile_supplier_coverage["all_specs_ready"]:
        unresolved.append("ALL_26_ADAPTIVE_PROFILE_NATIVE_ACCEPTANCE")
    if (special_L["selected_count"] and
            v208_receipt_identity["status"]!="VERIFIED"):
        unresolved.append(
            "V208_SELECTED_SPECIAL_L_START_RECEIPT_NOT_YET_SERIALIZED_IN_ENVIRONMENT_MANIFEST")
    if windows_package["status"] != "VERIFIED":
        unresolved.append("V213_WINDOWS_PACKAGE_MANIFEST_NOT_VERIFIED")
    unresolved.append("WINDOWS_ONE_CLICK_BUILD_START_PROGRESS_CANCEL_RESUME_NOT_FULLY_ACCEPTED")
    payload = {
        "schema": SCHEMA,
        "status": "READY_WITH_LIMITATIONS" if limitations or unresolved else "READY",
        "native_calls": 0,
        "network_calls": 0,
        "automatic_ui_promotion": False,
        "product_scope": {
            "supported_specializations": 26,
            "excluded": ["evoker/augmentation", "all_tanks", "all_healers"],
            "current_profile_archetype": archetype,
            "all_specs_ready": bootstrap.get("all_specs_ready"),
            "profile_supplier_coverage":profile_supplier_coverage,
        },
        "source_catalog": {
            "schema": source_catalog["schema"],
            "artifact_sha256": source_catalog_sha,
            "manifest_sha256": source_catalog["manifest_sha256"],
            "game_build": build,
            "simc_revision": revision,
            "v191": {
                "sha256": v191["sha256"],
                "sha256_by_input": v191["sha256_by_input"],
                "simc_generated_sources": v191["simc_generated_sources"],
            },
            "v211": {
                "sha256": v211["sha256"],
                "source_files": v211.get("source_files"),
                "candidate_source_schema": v211["candidate_source_schema"],
            },
            "catalog_summary": source_catalog.get("catalog_summary"),
            "related_source_counts": source_catalog.get("related_source_counts"),
        },
        "approved_ui_catalog": {
            "schema": ui["schema"],
            "normalized_sha256": ui_sha,
            "source_catalog_manifest_sha256": source_ui["manifest_sha256"],
            "season_build": build,
            "simc_revision": revision,
            "enchant_count": ui["enchant_candidates"]["total"],
            "selectable_enchant_ids": approved_ids,
            "developer_only_enchant_ids": [8025],
            "all_other_enchants_locked": True,
        },
        "selected_nonchmv_enchant": selected_enchant,
        "v208_start_receipt": v208_receipt_identity,
        "windows_package": windows_package,
        "target_profile": {
            "schema": bootstrap["schema"],
            "normalized_result_sha256": bootstrap_identity_sha,
            "template_archetype": archetype,
            "target_ilevel": target_ilevel,
            "base_B": plan["base_B"],
            "final_T": plan["final_T"],
            "generated_manifest_sha256": target_manifest_identity_sha,
            "runtime_binary": binary,
            "static_cache": static_cache_identity,
            "selected_special_L": special_L,
            "profile_files": profile_files,
            "scenario_sha256": scenario_sha,
            "profile_supplier_coverage_sha256":sha(
                canonical(profile_supplier_coverage).encode("utf8")),
            "native_calls": bootstrap["native_calls"],
        },
        "dependency_graph":None,
        "dependency_change":None,
        "readiness_limitations": limitations,
        "unresolved_dependencies": unresolved,
    }
    graph=_dependency_graph(
        source_catalog_sha,v191,ui_sha,bootstrap_identity_sha,profile_files,
        special_L,static_cache_identity,v208_receipt_identity,
        windows_package,binary,revision)
    payload["dependency_graph"]=graph
    payload["dependency_change"]=compare_dependency_graphs(
        previous_environment_manifest,graph)
    digest = sha(canonical(payload).encode("utf8"))
    return {**payload, "manifest_sha256": digest}


def compile_from_paths(source_catalog_path, bootstrap_path, target_root,
                      v208_start_receipt_path=None,
                      package_manifest_path=None,
                      previous_manifest_path=None):
    source_catalog_path = Path(source_catalog_path).resolve()
    source_catalog, source_catalog_sha = read_json(source_catalog_path)
    bootstrap, _ = read_json(bootstrap_path)
    receipt=None
    if v208_start_receipt_path is not None:
        receipt,_=read_json(v208_start_receipt_path)
    ui = ui_catalog.public_options(source_catalog_path)
    ui_sha = sha(canonical(ui).encode("utf8"))
    package_identity = verify_windows_package_manifest(
        package_manifest_path, source_catalog_path,
        source_catalog, source_catalog_sha)
    previous=None
    if previous_manifest_path is not None:
        previous,_=read_json(previous_manifest_path)
        need(type(previous) is dict and
             valid_sha(previous.get("manifest_sha256")) and
             sha(canonical({k:v for k,v in previous.items()
                            if k!="manifest_sha256"}).encode("utf8"))==
                 previous["manifest_sha256"],
             "PREVIOUS_ENVIRONMENT_MANIFEST_DIGEST_INVALID")
    return compile_manifest(source_catalog, source_catalog_sha, ui, ui_sha,
                             bootstrap, target_root, receipt, package_identity,
                             previous)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-to-catalog", required=True, type=Path)
    parser.add_argument("--bootstrap-result", required=True, type=Path)
    parser.add_argument("--target-root", required=True, type=Path)
    parser.add_argument("--v208-start-receipt", type=Path)
    parser.add_argument("--package-manifest", type=Path)
    parser.add_argument("--previous-manifest", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = compile_from_paths(args.source_to_catalog,
                                    args.bootstrap_result, args.target_root,
                                    args.v208_start_receipt,
                                    args.package_manifest,
                                    args.previous_manifest)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("V212_ENVIRONMENT_BUILD_BLOCKED", type(exc).__name__, str(exc))
        return 3
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(result, sort_keys=True, ensure_ascii=False,
                         indent=2, allow_nan=False) + "\n"
    if out.exists():
        need(out.read_text("utf8") == encoded,
             "EXISTING_ENVIRONMENT_MANIFEST_CHANGED")
    else:
        out.write_text(encoded, encoding="utf8")
    print("V212_ENVIRONMENT_MANIFEST_PASS", result["status"],
          result["manifest_sha256"], "NATIVE_0", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
