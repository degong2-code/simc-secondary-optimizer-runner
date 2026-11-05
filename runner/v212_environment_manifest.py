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
import re
from pathlib import Path

import v143_specialization_contracts as specs
import v046_static_item_cache as item_cache
import v062_static_budget_bridge as budget
import v196_current_season_user_catalog as ui_catalog
import v206_nonchmv_eagle_selection as eagle
import v213_source_to_catalog as source_bridge
import v222_season_budget_contract as season_budget

SCHEMA = "v212_simc_environment_manifest_v2"
V098 = "v098_target_ilevel_user_scenario_v1"
EXPECTED_APPROVED_ENCHANT_IDS = [7967]
EXPECTED_ENCHANT_COUNT = 38

FRESH_SEASON_STAGE_SCHEMA = "v212_fresh_source_environment_stage_v1"
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



def _validate_fresh_prepared_option_sources(prepared, catalog):
    """Source identity check before an eventually authorized v212 install.

    v220/v196 already decide exact proofs; never certify effects or READY here.
    An updated JSON digest alone must not authorize a wrong item/slot/quality.
    """
    rows=catalog["catalog"]["enchants"]["items"]
    by_id={r["enchant_id"]:r for r in rows}
    selected=prepared["verified_option_inputs_unpublished"]
    eligible=prepared.get("v220_exact_proof_eligible_count")
    pending=prepared.get("quality_use_scope_pending_item_ids")
    other=prepared.get("other_proofs_pending_by_item_id")
    need(len(by_id)==len(rows) and type(eligible) is int and
         len(selected)<=eligible<=len(rows) and
         type(pending) is list and
         all(type(i) is int and i in by_id for i in pending) and
         len(set(pending))==len(pending) and
         type(other) is dict and
         all(type(i) is str and i.isdecimal() and int(i) in by_id and
             type(v) is list and all(type(reason) is str for reason in v)
             for i,v in other.items()) and
         eligible==len(selected)+len(pending),
         "FRESH_ENVIRONMENT_PREPARED_POLICY_A_COUNTS_DRIFT")
    need(prepared.get("status")==(
         "EXACT_OPTIONS_PREPARED_FOR_VERSIONED_INSTALL" if selected else
         "EXACT_OPTIONS_NOT_YET_PREPARED") and
         prepared.get("native_calls")==0 and
         prepared.get("network_calls")==0,
         "FRESH_ENVIRONMENT_PREPARED_STATUS_OR_SIDE_EFFECT_DRIFT")
    expected_fields={"enchant_id","simc_token","slot",
                     "highest_verified_quality_rank",
                     "policy_A_source_relation_sha256",
                     "quality_source_sha256","exact_v220_identity"}
    ids=[]
    for row in selected:
        need(type(row) is dict and set(row)==expected_fields and
             type(row.get("enchant_id")) is int and
             row["enchant_id"] in by_id,
             "FRESH_ENVIRONMENT_PREPARED_ITEM_ID_OR_FIELDS_INVALID")
        source=by_id[row["enchant_id"]]
        need(source["slot_resolution_status"]=="SOURCE_MASK_RESOLVED" and
             type(source["slot_group"]) is str and
             "/" not in source["slot_group"],
             "FRESH_ENVIRONMENT_PREPARED_SOURCE_SLOT_UNRESOLVED")
        identity={"kind":"permanent_enchant","exact_id":source["enchant_id"],
                  "simc_token":source["token"],"slot":source["slot_group"],
                  "game_build":catalog["game_build"],
                  "simc_revision":catalog["simc_revision"],
                  "catalog_sha256":catalog["manifest_sha256"]}
        need(row["exact_v220_identity"]==identity and
             row["simc_token"]==source["token"] and
             row["slot"]==source["slot_group"] and
             type(row["highest_verified_quality_rank"]) is int and
             row["highest_verified_quality_rank"]==source["quality_rank"] and
             valid_sha(row["policy_A_source_relation_sha256"]) and
             valid_sha(row["quality_source_sha256"]),
             "FRESH_ENVIRONMENT_PREPARED_SOURCE_IDENTITY_DRIFT")
        ids.append(row["enchant_id"])
    need(ids==sorted(set(ids)) and
         not (set(ids)&set(pending)) and
         not (set(map(str,ids))&set(other)),
         "FRESH_ENVIRONMENT_PREPARED_DUPLICATE_OR_PENDING_CONFLICT")
    return len(ids)


def compile_fresh_source_environment(*, source_catalog, source_artifact_sha256,
                                     preflight, compilation, target_ilevel,
                                     selected_numeric=None):
    """Versioned ENVIRONMENT-only source stage, reusable by original v216.

    Not the legacy per-user v098/DPS manifest. Original v213/v216/v217
    authentication and v222 arithmetic remain upstream; no caller-provided
    status can turn these unaudited ratings or policy options into READY.
    """
    source_bridge.verify_catalog(source_catalog)
    need(valid_sha(source_artifact_sha256) and
         type(target_ilevel) is int and 1<=target_ilevel<=1000,
         "FRESH_ENVIRONMENT_SOURCE_IDENTITY_REQUIRED")
    need(type(preflight) is dict and
         preflight.get("schema")=="v216_new_season_source_preflight_v1" and
         preflight.get("status")==
             "FRESH_SOURCE_CANDIDATES_VALID_GJFO_PENDING_NOT_INSTALLED" and
         preflight.get("source_artifact_sha256")==source_artifact_sha256 and
         preflight.get("source_catalog_manifest_sha256")==
             source_catalog.get("manifest_sha256") and
         preflight.get("game_build")==source_catalog.get("game_build") and
         preflight.get("simc_revision")==source_catalog.get("simc_revision") and
         preflight.get("environment_ready") is False and
         preflight.get("approved_new_choices")==0 and
         all(preflight.get(x) is None for x in ("G","J","F","O","B","T")),
         "FRESH_ENVIRONMENT_ORIGINAL_PREFLIGHT_REQUIRED")
    expected_preflight_sha=sha(canonical({
        k:v for k,v in preflight.items() if k!="preflight_sha256"
    }).encode("utf8"))
    need(preflight.get("preflight_sha256")==expected_preflight_sha,
         "FRESH_ENVIRONMENT_PREFLIGHT_DIGEST_DRIFT")
    need(type(compilation) is dict and
         compilation.get("status")==
             "FRESH_V191_V211_V213_COMPILED_UNADMITTED" and
         compilation.get("preflight_sha256")==expected_preflight_sha and
         compilation.get("simc_revision")==source_catalog["simc_revision"] and
         compilation.get("environment_ready") is False,
         "FRESH_ENVIRONMENT_COMPILER_LINK_REQUIRED")
    seals={}
    for key in ("v191_stage","v211_stage","v213_stage"):
        receipt=compilation.get(key)
        need(type(receipt) is dict and
             receipt.get("status") in ("EXECUTED_AND_SEALED",
                                      "REUSED_VERIFIED","RECOVERED_VERIFIED")
             and valid_sha(receipt.get("receipt_sha256")),
             "FRESH_ENVIRONMENT_ORIGINAL_STAGE_RECEIPT_REQUIRED:"+key)
        seals[key]=receipt["receipt_sha256"]
    preview=None
    if selected_numeric is not None:
        need(type(selected_numeric) is dict and
             selected_numeric.get("schema")==
                "v216_zero_history_selected_v222_numeric_preview_v1" and
             selected_numeric.get("status")==
                "SELECTED_GJFO_V222_ARITHMETIC_PREVIEW_UNADMITTED" and
             selected_numeric.get("numeric_preview_only") is True and
             selected_numeric.get("environment_ready") is False and
             type(selected_numeric.get("calculation")) is dict,
             "FRESH_ENVIRONMENT_V222_NUMERIC_PREVIEW_UNADMITTED_REQUIRED")
        calc=selected_numeric["calculation"]
        need(calc.get("game_build")==source_catalog["game_build"] and
             calc.get("simc_revision")==source_catalog["simc_revision"] and
             calc.get("target_ilevel")==target_ilevel and
             calc.get("source_catalog_manifest_sha256")==
                source_catalog["manifest_sha256"] and
             calc.get("source_catalog_artifact_sha256")==
                source_artifact_sha256 and
             calc.get("numeric_preview_only") is True and
             calc.get("environment_ready") is False,
             "FRESH_ENVIRONMENT_V222_PREVIEW_IDENTITY_DRIFT")
        # Reuse the ORIGINAL v222 accounting outcome. A self-described
        # numeric receipt is not game/source authentication. Store only
        # its bounded identities and values: no new Native, re-calculation,
        # or user/session inputs are introduced by this manifest.
        need(calc.get("schema")=="v222_season_gjfo_budget_contract_v1" and
             calc.get("status")==
                 "NUMERIC_PREVIEW_UNADMITTED_NO_SOURCE_AUTHENTICATION" and
             calc.get("source_authentication_performed_here") is False and
             type(calc.get("reference_G")) is int and calc["reference_G"]>0 and
             type(calc.get("J")) is int and calc["J"]>=0 and
             type(calc.get("F")) is int and calc["F"]>=0 and
             type(calc.get("base_B")) is int and calc["base_B"]>0 and
             type(calc.get("final_T")) is int and calc["final_T"]>0 and
             type(calc.get("fixed_O")) is dict and
             set(calc["fixed_O"]) == {
                 "crit_rating","haste_rating","mastery_rating",
                 "versatility_rating"} and
             all(type(v) is int and v>=0
                 for v in calc["fixed_O"].values()) and
             calc["base_B"]+sum(calc["fixed_O"].values())==
                 calc["final_T"],
             "FRESH_ENVIRONMENT_ORIGINAL_V222_ARITHMETIC_REQUIRED")
        identities=selected_numeric.get("numeric_receipt_identities")
        # Native G and an already-scoped v222 G reference are alternative
        # evidence routes, not interchangeable measurements. Exactly one.
        g_sources={"G_native_json2_sha256",
                   "G_same_season_reference_source_sha256"}
        common={"J_physical_layout_rating_sha256",
                "F_selected_item_native_sha256",
                "O_selected_hands_native_mask_sha256"}
        present=(set(identities) if type(identities) is dict else set())
        need(len(present & g_sources)==1 and
             present==common | (present & g_sources) and
             all(valid_sha(value) for value in identities.values()),
             "FRESH_ENVIRONMENT_GJFO_ORIGINAL_RECEIPT_IDENTITIES_REQUIRED")
        selection=selected_numeric.get("selected_physical_items")
        need(type(selection) is dict and
             set(selection)=={"flask_item_id","oil_item_ids_by_hand"} and
             type(selection["flask_item_id"]) is int and
             selection["flask_item_id"]>0 and
             type(selection["oil_item_ids_by_hand"]) is dict and
             set(selection["oil_item_ids_by_hand"])<={
                 "main_hand","off_hand"} and
             all(type(v) is int and v>0 for v in
                 selection["oil_item_ids_by_hand"].values()) and
             (bool(selection["oil_item_ids_by_hand"]) or
              sum(calc["fixed_O"].values())==0),
             "FRESH_ENVIRONMENT_PHYSICAL_F_O_SELECTION_REQUIRED")
        preview={"status":"NUMERIC_OBSERVED_NOT_ADMITTED",
                 "reference_G_unadmitted":calc["reference_G"],
                 "J_unadmitted":calc["J"],
                 "F_unadmitted":calc["F"],
                 "fixed_O_unadmitted":dict(calc["fixed_O"]),
                 "base_B_unadmitted":calc["base_B"],
                 "final_T_unadmitted":calc["final_T"],
                 "manual_final_T_authoritative":
                     calc.get("manual_final_T_authoritative") is True,
                 "physical_item_selection_unadmitted":{
                     "flask_item_id":selection["flask_item_id"],
                     "oil_item_ids_by_hand":
                         dict(selection["oil_item_ids_by_hand"])},
                 "exact_source_receipt_identities_unadmitted":
                     dict(identities),
                 "original_v222_calculation_sha256":sha(
                     canonical(calc).encode("utf8")),
                 "source_authentication_performed_here":False}
    # Existing v196/v220 exact item proofs are retained across the original
    # v216 -> v212 versioned boundary, independently of the core GJFO gate.
    # Even fully prepared optional rows do not authorize user publication
    # while this fresh-season environment remains NOT INSTALLED.
    optional=preflight.get("optional_policy_A_evidence_unadmitted")
    prepared=(optional.get("prepared_verified_options_unpublished")
              if type(optional) is dict else None)
    if prepared is not None:
        need(type(prepared) is dict and
             prepared.get("schema")==
                 "v196_fresh_verified_option_install_inputs_v1" and
             prepared.get("game_build")==source_catalog["game_build"] and
             prepared.get("simc_revision")==source_catalog["simc_revision"] and
             prepared.get("source_catalog_manifest_sha256")==
                 source_catalog["manifest_sha256"] and
             prepared.get("selection_mutated") is False and
             prepared.get("ui_selectable") is False and
             prepared.get("environment_ready") is False and
             prepared.get("environment_installed") is False and
             prepared.get("options_published") is False and
             type(prepared.get("verified_option_inputs_unpublished")) is list,
             "FRESH_ENVIRONMENT_POLICY_A_PREPARED_SCOPE_DRIFT")
        body={k:v for k,v in prepared.items()
              if k!="prepared_options_sha256"}
        need(prepared.get("prepared_options_sha256")==sha(
             canonical(body).encode("utf8")),
             "FRESH_ENVIRONMENT_POLICY_A_PREPARED_DIGEST_INVALID")
        _validate_fresh_prepared_option_sources(prepared, source_catalog)
    payload={
        "schema":FRESH_SEASON_STAGE_SCHEMA,
        "status":"FRESH_SEASON_ENVIRONMENT_STAGED_NOT_INSTALLED",
        "game_build":source_catalog["game_build"],
        "simc_revision":source_catalog["simc_revision"],
        "target_ilevel":target_ilevel,
        "source_catalog_manifest_sha256":source_catalog["manifest_sha256"],
        "source_catalog_artifact_sha256":source_artifact_sha256,
        "original_v217_stage_receipts":seals,
        "original_v216_preflight_sha256":expected_preflight_sha,
        "pending_core_requirements":list(preflight["requires"]),
        "optional_policy_A_pending_separate":True,
        "versioned_policy_A_prepared_options_unpublished":prepared,
        "optional_item_missing":preflight.get(
            "optional_policy_A_evidence_unadmitted",{}).get("per_item_missing_reasons",{}),
        "numeric_budget_preview_unadmitted":preview,
        "official_G":None,"official_J":None,"official_F":None,
        "official_O":None,"official_B":None,"official_T":None,
        "environment_ready":False,"environment_installed":False,
        "options_published":False,"dps_optimization_required":False,
        "user_profile_or_trinkets_required":False,
        "source_authorization_created_here":False,
        "native_calls":0,"network_calls":0,
    }
    return {**payload,"manifest_sha256":sha(canonical(payload).encode("utf8"))}


def verify_fresh_source_environment(document):
    """Read-only integrity check for a source-only ENVIRONMENT stage."""
    need(type(document) is dict and
         document.get("schema")==FRESH_SEASON_STAGE_SCHEMA and
         document.get("status")==
             "FRESH_SEASON_ENVIRONMENT_STAGED_NOT_INSTALLED" and
         all(document.get(x) is None for x in
             ("official_G","official_J","official_F","official_O",
              "official_B","official_T")) and
         document.get("environment_ready") is False and
         document.get("environment_installed") is False and
         document.get("options_published") is False and
         document.get("dps_optimization_required") is False,
         "FRESH_ENVIRONMENT_STAGE_CANNOT_PROMOTE_TO_READY")
    payload={k:v for k,v in document.items() if k!="manifest_sha256"}
    need(document.get("manifest_sha256")==sha(
        canonical(payload).encode("utf8")),
        "FRESH_ENVIRONMENT_STAGE_MANIFEST_DIGEST_INVALID")
    return True



FRESH_SEASON_INSTALLED_SCHEMA = "v212_fresh_verified_environment_installed_v1"


def compile_fresh_installed_environment(*, source_catalog, source_artifact_sha256,
                                        staged_source_environment,
                                        trusted_budget_evidence, source_ui,
                                        trusted_policy_A_receipts_by_id,
                                        target_ilevel, manual_final_T=None):
    """Assemble the actual fresh-season install from existing verified owners.

    INTERNAL ONLY: trusted_budget_evidence must originate from verified
    G/J/F/O source owners, and Policy A receipts from the existing v220
    internal source/SimC/product/CHMV verification pipeline. Neither a user
    request, source-only v222 preview nor a self-rehashed stage is authority.
    This function does no additional source authentication/Native/network.
    The caller MUST install through v217.execute_stage before exposing READY.
    """
    source_bridge.verify_catalog(source_catalog)
    verify_fresh_source_environment(staged_source_environment)
    need(valid_sha(source_artifact_sha256) and
         staged_source_environment["source_catalog_manifest_sha256"]==
             source_catalog["manifest_sha256"] and
         staged_source_environment["source_catalog_artifact_sha256"]==
             source_artifact_sha256 and
         staged_source_environment["game_build"]==source_catalog["game_build"] and
         staged_source_environment["simc_revision"]==
             source_catalog["simc_revision"] and
         staged_source_environment["target_ilevel"]==target_ilevel,
         "FRESH_INSTALL_SEALED_STAGE_OR_SEASON_IDENTITY_MISMATCH")
    need(type(trusted_budget_evidence) is dict and
         type(trusted_policy_A_receipts_by_id) is dict and
         type(source_ui) is dict,
         "FRESH_INSTALL_TRUSTED_INTERNAL_INPUTS_REQUIRED")
    try:
        budget=season_budget.preprofile_budget(
            source_catalog=source_catalog,
            source_artifact_sha256=source_artifact_sha256,
            evidence=trusted_budget_evidence,target_ilevel=target_ilevel,
            manual_final_T=manual_final_T)
    except season_budget.SeasonBudgetBlocked as exc:
        raise EnvironmentBlocked(
            "FRESH_INSTALL_OFFICIAL_GJFO_RECONCILIATION_BLOCKED:"+str(exc)
        ) from exc
    need(budget["status"]==
             "ARITHMETIC_RECONCILED_SOURCE_AUTHENTICATION_EXTERNAL" and
         budget["source_authentication_performed_here"] is False and
         not budget.get("numeric_preview_only",False),
         "FRESH_INSTALL_UNADMITTED_V222_PREVIEW_CANNOT_PROMOTE")
    # v196 is the original admission/quality projection. Each optional item
    # lacking proof remains pending; it cannot block an otherwise proven base.
    try:
        prepared=ui_catalog.prepare_verified_fresh_choices(
            source_catalog,source_ui,trusted_policy_A_receipts_by_id)
    except ui_catalog.CatalogBlocked as exc:
        raise EnvironmentBlocked(
            "FRESH_INSTALL_POLICY_A_ORIGIN_BLOCKED:"+str(exc)) from exc
    _validate_fresh_prepared_option_sources(prepared,source_catalog)
    published=[{**row,"ui_selectable":True}
               for row in prepared["verified_option_inputs_unpublished"]]
    oil=budget["fixed_O"]
    components=trusted_budget_evidence["components"]
    payload={
        "schema":FRESH_SEASON_INSTALLED_SCHEMA,
        "status":"FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY",
        "game_build":source_catalog["game_build"],
        "simc_revision":source_catalog["simc_revision"],
        "target_ilevel":target_ilevel,
        "source_catalog_manifest_sha256":source_catalog["manifest_sha256"],
        "source_catalog_artifact_sha256":source_artifact_sha256,
        "staged_source_environment_sha256":
            staged_source_environment["manifest_sha256"],
        "original_v216_preflight_sha256":
            staged_source_environment["original_v216_preflight_sha256"],
        "original_v217_stage_receipts":
            dict(staged_source_environment["original_v217_stage_receipts"]),
        "trusted_budget_evidence_sha256":
            sha(canonical(trusted_budget_evidence).encode("utf8")),
        "trusted_budget_component_source_identities":{
            k:{"source_sha256":components[k]["source_sha256"],
               "source_verification":components[k]["source_verification"]}
            for k in ("G","J","F","O")},
        "official_G":budget["reference_G"],
        "official_effective_G":budget["effective_G"],
        "official_J":budget["J"],
        "official_F":budget["F"],
        "official_O":dict(oil),
        "official_B":budget["base_B"],
        "official_T":budget["final_T"],
        "manual_final_T_authoritative":
            budget["manual_final_T_authoritative"],
        "v222_reconciled_budget":budget,
        "original_v196_prepared_options_sha256":
            prepared["prepared_options_sha256"],
        "published_verified_options":published,
        "published_verified_option_count":len(published),
        "optional_quality_pending_item_ids":
            list(prepared["quality_use_scope_pending_item_ids"]),
        "optional_other_proof_pending_by_id":
            dict(prepared["other_proofs_pending_by_item_id"]),
        "optional_items_do_not_block_base":True,
        "environment_ready":True,"environment_installed":True,
        "options_published":True,
        "dps_optimization_required":False,
        "user_profile_or_trinkets_required":False,
        "source_authentication_created_here":False,
        "native_calls":0,"network_calls":0,
    }
    return {**payload,
            "manifest_sha256":sha(canonical(payload).encode("utf8"))}


def verify_fresh_installed_environment(document):
    """Integrity and official accounting of a versioned installed output.

    This does not replace existing source owner verification, which must
    occur before compile_fresh_installed_environment is called.
    """
    need(type(document) is dict and
         document.get("schema")==FRESH_SEASON_INSTALLED_SCHEMA and
         document.get("status")==
             "FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY" and
         document.get("environment_ready") is True and
         document.get("environment_installed") is True and
         document.get("options_published") is True and
         document.get("source_authentication_created_here") is False and
         document.get("optional_items_do_not_block_base") is True and
         valid_sha(document.get("staged_source_environment_sha256")) and
         valid_sha(document.get("trusted_budget_evidence_sha256")) and
         valid_sha(document.get("original_v196_prepared_options_sha256")) and
         type(document.get("official_G")) is int and
         document["official_G"]>0 and
         type(document.get("official_J")) is int and
         document["official_J"]>=0 and
         type(document.get("official_F")) is int and
         document["official_F"]>=0 and
         type(document.get("official_O")) is dict and
         set(document["official_O"])==set(season_budget.STATS) and
         all(type(i) is int and i>=0
             for i in document["official_O"].values()) and
         type(document.get("official_B")) is int and
         type(document.get("official_T")) is int and
         document["official_B"]+sum(document["official_O"].values())==
             document["official_T"] and
         type(document.get("published_verified_options")) is list and
         document.get("published_verified_option_count")==
             len(document["published_verified_options"]) and
         all(type(row) is dict and row.get("ui_selectable") is True
             for row in document["published_verified_options"]) and
         document.get("dps_optimization_required") is False and
         document.get("native_calls")==0 and document.get("network_calls")==0,
         "FRESH_INSTALL_READY_OR_BUDGET_CONTRACT_DRIFT")
    payload={k:v for k,v in document.items() if k!="manifest_sha256"}
    need(document.get("manifest_sha256")==sha(canonical(payload).encode("utf8")),
         "FRESH_INSTALL_MANIFEST_DIGEST_INVALID")
    return True


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
                 re.fullmatch(r"[a-f0-9]{7,40}",
                              native["revision"]) is not None and
                 # A sealed HIT can be static data from an older SimC.
                 # Native misses must match the executing SimC revision.
                 (row["cache_status"]=="HIT" or
                  native["revision"].startswith(revision[:7])) and
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
         source.get("simc_revision")==source_catalog["simc_revision"],
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
    # Static catalog source and current SimC executable revisions are
    # separate: ordinary balance/APL updates must not rebuild unchanged GJFO.
    runtime_revision=target_manifest.get("native_revision")
    need(target_manifest.get("native_limit") == 6
         and type(runtime_revision) is str and
         re.fullmatch(r"[a-f0-9]{7,40}",runtime_revision) is not None,
         "V098_ADAPTIVE_LIMIT_OR_SIMC_REVISION_INVALID")
    binary = sha_file(target_manifest.get("native_binary", ""))
    static_cache = target_manifest.get("static_cache_json")
    static_cache_identity = sha_file(static_cache) if static_cache else None
    profile_text = (target_root / "profile.simc").read_text(encoding="utf8")
    selected_enchant = _selected_enchant(bootstrap, profile_text, approved_ids)
    scenario, scenario_sha = read_json(target_root / "scenario.json")
    special_L = _selected_special_L(scenario, static_cache_identity)
    v208_receipt_identity = _verify_v208_start_receipt(
        v208_start_receipt, scenario, source_catalog, source_catalog_sha,
        runtime_revision, binary, static_cache_identity, special_L)

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
    source_join_audit = source_catalog.get("source_join_audit")
    if source_join_audit is None:
        # Historical packaged source did not carry row-based join evidence.
        join_unresolved = ["SOURCE_JOIN_AUDIT_NOT_AVAILABLE"]
    else:
        need(type(source_join_audit) is dict and
             source_join_audit.get("schema") == "v213_source_join_audit_v1" and
             source_join_audit.get("user_selection_granted") is False and
             type(source_join_audit.get("unresolved_dependencies")) is list,
             "V213_SOURCE_JOIN_AUDIT_INVALID")
        join_unresolved = list(source_join_audit["unresolved_dependencies"])
    if join_unresolved:
        limitations.append("SOURCE_JOIN_AUDIT_HAS_UNRESOLVED_EVIDENCE")
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
    unresolved = list(join_unresolved)
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
            "source_join_audit": source_join_audit,
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
        windows_package,binary,runtime_revision)
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
