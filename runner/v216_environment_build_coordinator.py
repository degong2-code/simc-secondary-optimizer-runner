#!/usr/bin/env python3
"""v216 request-driven incremental Environment Build coordinator.

Consumes the installed, immutable v213 source-to-catalog artifact and reuses
v191/v211 provenance embedded in it. It does not recollect season data, fetch
network resources, call SimC Native, mutate optimizer/DPS caches, or replace
historical sessions. Existing v098 and v212 components remain authoritative.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import tempfile
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import v212_environment_manifest as environment_manifest
import v222_season_budget_contract as season_budget_contract
import v262_standardized_ilevel_budget_rows as standardized_budget_rows
import v269_simc_chmv_effect_snapshot as simc_snapshot_delta
import v221_gem_item_db2_relation as gem_item_join
import v268_gem_enchant_existing_source_stage as gem_enchant_stage
import v271_user_socket_gem_layout as physical_gems
import v274_zero_history_source_compiler_wiring as source_wiring
import v275_pinned_simc_compiler_inputs as pinned_compiler_source
import v295_season_runeforge_source as dk_rune_source
import v296_pinned_oil_static_rating_source as oil_raw_source
import v276_sealed_tier_compiler_source as compiler_tier_source
import v277_zero_history_native_G_stage as zero_history_G_native
import v278_sealed_simc_consumable_native_pair as native_effect_pair
import v280_consumable_item_use_spell_source as item_spell_bridge
import v281_consumable_simc_relation as consumable_simc_relation
import v285_consumable_weapon_source as consumable_weapon_source
import v223_installed_season_budget_source as season_source_proof
import v213_source_to_catalog as source_to_catalog
import v161_wago_db2_snapshot as wago_snapshot
import v242_authenticated_season_source_stage as discovery_stage
import v163_zero_seed_db2_join as season_join
import v165_current_season_gear_pool as source_gear_pool
import v166_compact_product_gear_db as compact_gear_db
import v167_product_season_gear_adapter as product_gear_db
import v245_db2_first_tier_discovery as tier_db
import v250_raid_tier_bonus_corroboration as raid_bonus
import v251_db2_raid_tier_simc_bridge as tier_simc_bridge
import v261_tier_source_evidence_reuse as tier_evidence_reuse
import v229_simc_only_source_seed as simc_source
import v230_simc_item_metadata as simc_item_metadata
import v189_simc_consumable_embellishment_discovery as simc_effect_candidates
import v190_consumable_item_snapshot_join as consumable_item_candidates
import v232_simc_only_ordinary_representative as simc_representative
import v233_source_only_G_probe_profile as g_probe_profile
import v217_stage_execution_engine as stage_engine
import v196_current_season_user_catalog as user_catalog
import v220_catalog_auto_admission as auto_admission
import v241_fresh_source_stage_adapter as fresh_stage

SCHEMA = "v216_incremental_environment_build_receipt_v1"
SESSION_KEY = re.compile(r"[a-f0-9]{20}\Z")
MAX_RECEIPT_BYTES = 1_000_000
MAX_PRIOR_SESSIONS = 128

class EnvironmentBuildBlocked(environment_manifest.EnvironmentBlocked):
    pass


def need(condition, code):
    if not condition:
        raise EnvironmentBuildBlocked(code)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _existing_v268_four_stat_source_diagnostic(*, observed, csv_source):
    """Compact, read-only projection of already-computed v268 J candidates.

    Missing data is tri-state: None is unobserved, False is observed absent.
    Never turns raw EffectPointsMin into verified J or admits a UI choice.
    """
    candidate=observed if type(observed) is dict else {}
    sealed=csv_source if type(csv_source) is dict else {}
    expected=set(physical_gems.ORDINARY_FOUR_STATS)
    best=candidate.get("four_stat_ordinary_best_observed_unadmitted")
    best=best if type(best) is dict else {}
    known={key:{"item_id":row.get("item_id"),
                "raw_nominal_points":row.get("raw_nominal_points")}
           for key,row in best.items()
           if key in expected and type(row) is dict}
    missing_source_ids=candidate.get("selected_gem_v221_missing_item_ids")
    # A full same-build link with zero RAW_STATIC classifications is NOT
    # evidence that those gems have no effective rating. P3-GZ's real SimC
    # JSON2 buffed_stats already demonstrates an independent physical value.
    link_count=candidate.get("linked_gem_items")
    raw_count=candidate.get("raw_static_candidate_count")
    unresolved_count=candidate.get("unresolved_enchant_count")
    raw_zero_full_source=(
        type(link_count) is int and link_count>0 and
        type(raw_count) is int and raw_count==0 and
        type(unresolved_count) is int and
        unresolved_count==link_count)
    return {
        "schema":"p3_hb_existing_v268_j_source_diagnostic_v1",
        "v221_gem_relation_source_status":sealed.get("status"),
        "v268_status":candidate.get("status"),
        "v268_reason":candidate.get("reason"),
        "selected_special_in_same_build_v221":candidate.get(
            "selected_gem_v221_same_build_items_all_present"),
        "selected_source_missing_item_ids":(
            list(missing_source_ids)
            if type(missing_source_ids) is list else None),
        "four_ordinary_two_stat_types_complete":candidate.get(
            "four_stat_ordinary_source_complete_unadmitted"),
        "observed_leading_types":sorted(known),
        "missing_leading_types":sorted(expected-set(known)),
        "observed_nominal_candidates_by_type_unadmitted":known,
        "v221_linked_gem_item_count":candidate.get("linked_gem_items"),
        "v266_raw_static_candidate_count":candidate.get(
            "raw_static_candidate_count"),
        "v266_unresolved_enchant_count":candidate.get(
            "unresolved_enchant_count"),
        "raw_static_zero_across_linked_source":raw_zero_full_source,
        "J_numeric_next_owner":(
            "SEASON_NOMINAL_ITEM_TOTAL_SOURCE_OR_VERIFIED_REFERENCE_REQUIRED"
            if raw_zero_full_source else None),
        "original_v266_raw_gate_bypassed":False,
        "official_J":None,"environment_ready":False,
        "native_calls":0,"network_calls":0,
    }


def _atomic_write(path, encoded):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = encoded.encode("utf8")
    if path.is_file() and not path.is_symlink() and path.read_bytes() == raw:
        return False
    fd, temporary = tempfile.mkstemp(
        prefix=".v216-environment-build-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return True


def environment_scope_identity(user):
    """Group comparable builds by exact user choices, across dependency changes.

    SimC binary/revision, installed source artifact and static-cache bytes are
    intentionally excluded: v212's dependency graph must compare those
    versions and report their downstream invalidations rather than hiding the
    previous environment behind a different lookup key.
    """
    need(type(user) is dict, "V216_USER_SCENARIO_OBJECT_REQUIRED")
    payload = {
        "schema": "v216_environment_scope_identity_v1",
        "user_scenario_sha256": digest(canonical(user).encode("utf8")),
    }
    return {**payload, "scope_sha256": digest(canonical(payload).encode("utf8"))}


def verify_receipt(document):
    need(type(document) is dict and document.get("schema") == SCHEMA,
         "V216_BUILD_RECEIPT_SCHEMA_INVALID")
    supplied = document.get("receipt_sha256")
    payload = {key: value for key, value in document.items()
               if key != "receipt_sha256"}
    need(type(supplied) is str and
         supplied == digest(canonical(payload).encode("utf8")),
         "V216_BUILD_RECEIPT_DIGEST_INVALID")
    session_id = document.get("session_id")
    need(type(session_id) is str and SESSION_KEY.fullmatch(session_id) is not None,
         "V216_BUILD_RECEIPT_SESSION_ID_INVALID")
    need(document.get("native_calls") == 0 and
         document.get("network_calls") == 0 and
         document.get("cache_mutations") == 0 and
         document.get("historical_sessions_preserved") is True,
         "V216_BUILD_RECEIPT_SIDE_EFFECT_CONTRACT_INVALID")
    return True


def _verified_manifest(path):
    path = pathlib.Path(path)
    if not path.is_file() or path.is_symlink():
        return None
    try:
        document, _ = environment_manifest.read_json(path)
        payload = {key: value for key, value in document.items()
                   if key != "manifest_sha256"}
        if (type(document) is not dict or
                document.get("schema") != environment_manifest.SCHEMA or
                document.get("manifest_sha256") !=
                digest(canonical(payload).encode("utf8"))):
            return None
        return document
    except (OSError, ValueError, TypeError, KeyError):
        return None


def find_verified_installed_season_environment(
        sessions_root, target_ilevel, *, expected_game_build):
    """Read-only, exact-build v217/v212 reuse across all 26 DPS profiles.

    A matching itemlevel alone is NEVER sufficient; even a fully sealed
    prior installed environment is stale for a different live game build.
    SimC binary revision changes do not by themselves invalidate static
    item-source evidence for the same authenticated build. Use the exact
    season folder to avoid scanning every historical patch and its files.
    """
    need(type(target_ilevel) is int and 1<=target_ilevel<=1000,
         "V216_REUSE_TARGET_ILEVEL_INVALID")
    need(type(expected_game_build) is str and
         re.fullmatch(r"\d+(?:\.\d+){3}",expected_game_build) is not None,
         "V216_REUSE_EXACT_GAME_BUILD_REQUIRED")
    supplied=pathlib.Path(sessions_root).expanduser()
    need(not supplied.is_symlink(),"V216_REUSE_SESSION_ROOT_SYMLINK")
    workspace=supplied.resolve()/"_fresh_season_sources"
    if not workspace.is_dir() or workspace.is_symlink():
        return None
    folder=workspace/("wago_"+expected_game_build)
    if folder.is_symlink() or not folder.is_dir():
        return None
    docs=folder/"fresh_source"
    if docs.is_symlink() or not docs.is_dir():
        return None
    candidates=[]
    for count,file in enumerate(docs.glob("v212_installed_*.json")):
        if count>=64:
            break
        if (file.is_symlink() or not file.is_file() or
            re.fullmatch(r"v212_installed_[a-f0-9]{20}\.json",file.name)
               is None):
            continue
        try:
            candidates.append((file.stat().st_mtime,folder,file))
        except OSError:
            pass
    candidates.sort(key=lambda row:(-row[0],row[2].as_posix()))
    for _,root,file in candidates[:64]:
        try:
            if file.stat().st_size>MAX_RECEIPT_BYTES:
                continue
            doc,_=environment_manifest.read_json(file,MAX_RECEIPT_BYTES)
            environment_manifest.verify_fresh_installed_environment(doc)
            key=doc["manifest_sha256"]
            if (file.name!="v212_installed_"+key[:20]+".json" or
                doc["game_build"]!=expected_game_build or
                doc["game_build"]!=root.name[5:] or
                doc["target_ilevel"]!=target_ilevel):
                continue
            catalog_path=root/"fresh_source"/"v213_candidate_catalog.json"
            if catalog_path.is_symlink() or not catalog_path.is_file():
                continue
            catalog,raw_sha=environment_manifest.read_json(catalog_path)
            source_to_catalog.verify_catalog(catalog)
            if (raw_sha!=doc["source_catalog_artifact_sha256"] or
                catalog["manifest_sha256"]!=doc["source_catalog_manifest_sha256"] or
                catalog["game_build"]!=doc["game_build"] or
                catalog["simc_revision"]!=doc["simc_revision"]):
                continue
            staged_sha=doc["staged_source_environment_sha256"]
            staged=root/"fresh_source"/(
                "v212_environment_"+staged_sha[:20]+".json")
            if staged.is_symlink() or not staged.is_file():
                continue
            stage_doc,_=environment_manifest.read_json(staged,MAX_RECEIPT_BYTES)
            environment_manifest.verify_fresh_source_environment(stage_doc)
            if (stage_doc["manifest_sha256"]!=staged_sha or
                stage_doc["source_catalog_artifact_sha256"]!=raw_sha or
                stage_doc["target_ilevel"]!=target_ilevel):
                continue
            stage_engine.verify_stage(
                root=root,stage_id="fresh-v212-environment-"+staged_sha[:20],
                stage_version="v212-fresh-source-environment-1",
                inputs={"manifest_sha256":staged_sha,
                        "v216_preflight_sha256":
                            stage_doc["original_v216_preflight_sha256"]},
                outputs={"environment":"fresh_source/"+staged.name})
            receipt=stage_engine.verify_stage(
                root=root,stage_id="fresh-v212-installed-"+key[:20],
                stage_version="v212-fresh-installed-environment-1",
                inputs={"manifest_sha256":key,
                        "source_stage_sha256":staged_sha,
                        "trusted_budget_evidence_sha256":
                            doc["trusted_budget_evidence_sha256"],
                        "policy_A_prepared_sha256":
                            doc["original_v196_prepared_options_sha256"]},
                outputs={"environment":"fresh_source/"+file.name})
        except (OSError,ValueError,TypeError,KeyError,
                stage_engine.StageExecutionBlocked,
                environment_manifest.EnvironmentBlocked):
            continue
        return {
            "schema":"v216_verified_installed_season_reuse_v1",
            "status":"VERIFIED_INSTALLED_SAME_SEASON_SOURCE_REUSED",
            "environment_ready":True,"environment_installed":True,
            "installed_source_game_build":doc["game_build"],
            "installed_source_simc_revision":doc["simc_revision"],
            "installed_manifest_sha256":key,
            "stage_receipt_sha256":receipt["receipt_sha256"],
            "target_ilevel":target_ilevel,
            "G":doc["official_G"],"J":doc["official_J"],
            "F":doc["official_F"],"O":doc["official_O"],
            "official_F_physical_source":
                doc.get("official_F_physical_source"),
            "B":doc["official_B"],"T":doc["official_T"],
            "published_verified_options":doc["published_verified_options"],
            "published_verified_option_count":
                doc["published_verified_option_count"],
            "active_season_reverified_in_this_lookup":False,
            "runtime_simc_version_does_not_invalidate_static_source":True,
            "network_calls":0,"native_calls":0,"cache_mutations":0,
            "dps_optimization_started":False,
        }
    return None


def find_previous_environment(sessions_root, current_folder, scope_sha256):
    """Find a prior same-input environment across source-versioned sessions.

    Only small, self-digested receipts and manifests are read. Paths are derived
    from validated 20-hex session IDs; symlinks and receipt-supplied paths are
    never followed. No session or cache is modified.
    """
    root = pathlib.Path(sessions_root).expanduser().resolve()
    current = pathlib.Path(current_folder).expanduser().resolve()
    if not root.is_dir():
        return None
    folders = []
    for folder in root.iterdir():
        if (folder.is_symlink() or not folder.is_dir() or
                SESSION_KEY.fullmatch(folder.name) is None):
            continue
        try:
            folders.append((folder.stat().st_mtime, folder))
        except OSError:
            continue
    folders.sort(key=lambda row: (-row[0], row[1].name))
    candidates = []
    for _, folder in folders[:MAX_PRIOR_SESSIONS]:
        if folder == current:
            continue
        generated = folder / "generated"
        if generated.is_symlink():
            continue
        receipt_path = generated / "environment_build_receipt.json"
        if not receipt_path.is_file() or receipt_path.is_symlink():
            continue
        try:
            if receipt_path.stat().st_size > MAX_RECEIPT_BYTES:
                continue
            receipt = json.loads(receipt_path.read_text(encoding="utf8"))
            verify_receipt(receipt)
            if (receipt.get("session_id") != folder.name or
                    receipt.get("environment_scope_sha256") != scope_sha256):
                continue
            manifest_path = folder / "generated" / "environment_manifest.json"
            manifest = _verified_manifest(manifest_path)
            if (manifest is None or
                    manifest.get("manifest_sha256") !=
                    receipt.get("environment_manifest_sha256")):
                continue
            candidates.append((receipt_path.stat().st_mtime,
                               folder.name, manifest_path, manifest))
        except (OSError, ValueError, TypeError, KeyError):
            continue
    candidates.sort(key=lambda row: (-row[0], row[1]))
    if not candidates:
        return None
    _, session_id, manifest_path, manifest = candidates[0]
    return {"session_id": session_id, "manifest_path": manifest_path,
            "manifest": manifest, "receipt": None,
            "legacy_same_session": False}


def _step(name, status, **details):
    return {"component": name, "status": status, **details}


FRESH_SOURCE_PREFLIGHT_SCHEMA="v216_new_season_source_preflight_v1"



def _fresh_gem_item_source_stage(*, stage_root, wago_folder,
                                 source_catalog_path, expected_game_build):
    """Join new-season gem property IDs to physical ItemSparse gem items.

    Reuse the original v221 verifier and the same v161 snapshot: no HTTP,
    Native, J rating guesses, item cache mutation, or user admission.
    v217 seals a deterministic compact candidate; replays recheck the two
    original DB2 file hashes without re-parsing their million rows.
    """
    root = pathlib.Path(stage_root).expanduser()
    snapshot = pathlib.Path(wago_folder).expanduser()
    need(root.is_dir() and not root.is_symlink() and
         snapshot.is_dir() and not snapshot.is_symlink(),
         "V216_FRESH_GEM_STAGE_OR_SNAPSHOT_ROOT_INVALID")
    source_path = pathlib.Path(source_catalog_path).expanduser()
    need(source_path.is_file() and not source_path.is_symlink(),
         "V216_FRESH_GEM_V213_SOURCE_REQUIRED")
    catalog, source_sha = environment_manifest.read_json(source_path)
    need(catalog.get("game_build") == expected_game_build,
         "V216_FRESH_GEM_V213_GAME_BUILD_MISMATCH")
    try:
        db2 = gem_item_join._verify_db2(snapshot, expected_game_build)
    except (gem_item_join.GemJoinBlocked, ValueError, OSError) as exc:
        raise EnvironmentBuildBlocked(
            "V216_FRESH_GEM_DB2_SOURCE_INVALID:" + str(exc)) from exc
    receipt = snapshot / "receipt.json"
    receipt_sha = digest(receipt.read_bytes())
    code = stage_engine.module_dependency_fingerprint([
        pathlib.Path(gem_item_join.__file__),
        pathlib.Path(stage_engine.__file__)])
    output = "fresh_source/v221_new_season_gem_item_candidates.json"
    path = root / output
    def execute():
        # The original _verify_db2 above has already checked both files.
        result = gem_item_join.join(catalog, snapshot, verified_tables=db2)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, sort_keys=True,
            ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf8")
    def validate(outputs):
        row = json.loads(outputs["candidate"].read_text(encoding="utf8"))
        return (row.get("schema") == gem_item_join.SCHEMA
                and row.get("game_build") == expected_game_build
                and row.get("v213_manifest_sha256") ==
                    catalog.get("manifest_sha256")
                and row.get("db2_tables") == db2
                and row.get("status") in (
                    "SOURCE_ITEM_PROPERTY_LINKS_ONLY_NOT_USER_ADMITTED",
                    "PENDING_GENERATED_SIMC_DBC_AND_DB2_BUILD_MISMATCH")
                and row.get("exact_link_count") ==
                    len(row.get("joins", []))
                and row.get("automatic_ui_promotion") is False
                and row.get("historical_cache_modified") is False
                and row.get("network_calls") == 0
                and row.get("simc_native_calls") == 0
                and all(x.get("ui_selectable") is False
                        for x in row.get("joins", [])))
    try:
        stage = stage_engine.execute_stage(
            root=root, stage_id="fresh-v221-gem-item-source",
            stage_version="source-only-same-build-v1",
            inputs={"source_artifact_sha256":source_sha,
                    "game_build":expected_game_build,
                    "wago_receipt_sha256":receipt_sha,
                    "wago_core_db2_sha256":db2,
                    "code_sha256":code["sha256"]},
            outputs={"candidate":output},
            execute=execute, validate=validate)
    except (gem_item_join.GemJoinBlocked,
            stage_engine.StageExecutionBlocked, ValueError, OSError) as exc:
        raise EnvironmentBuildBlocked(
            "V216_FRESH_GEM_ITEM_JOIN_BLOCKED:" + str(exc)) from exc
    result = json.loads(path.read_text(encoding="utf8"))
    return {
        "status":result["status"],
        "candidate_path":str(path.resolve()),
        "physical_gem_item_links":result["exact_link_count"],
        "source_stage":{k:v for k,v in stage.items() if k!="result"},
        "simc_dbc_build_matched":(
            result["simc_generated_gem_source_build"] ==
            expected_game_build),
        "highest_quality_J_verified":False,
        "J":None,"environment_ready":False,
        "network_calls_by_stage":0,"native_calls":0,
    }


def _fresh_selected_gem_simc_quality_stage(*, stage_root, seed_directory,
                                            game_build, simc_revision,
                                            selected_item_ids):
    """Reuse existing v230 exact selected-item fields from sealed v256 seed.

    This is a v217-cached SOURCE-ONLY projection, not quality equivalence,
    same-effect certification, special classification, socket permission
    or highest-quality option publication. No network or Native.
    """
    root=pathlib.Path(stage_root).resolve()
    seed=pathlib.Path(seed_directory).resolve()
    need(seed==root/"source"/"v256_full_pinned_simc" and
         seed.is_dir() and not seed.is_symlink() and
         type(selected_item_ids) is list and
         1<=len(selected_item_ids)<=64 and
         all(type(item) is int and item>0 for item in selected_item_ids) and
         len(set(selected_item_ids))==len(selected_item_ids) and
         type(game_build) is str and bool(game_build) and
         type(simc_revision) is str and
         re.fullmatch(r"[a-f0-9]{40}",simc_revision) is not None,
         "V216_SELECTED_GEM_PINNED_V230_SCOPE_INVALID")
    selected=sorted(selected_item_ids)
    receipt_file=seed/simc_source.RECEIPT
    need(receipt_file.is_file() and not receipt_file.is_symlink(),
         "V216_SELECTED_GEM_V230_SEED_RECEIPT_REQUIRED")
    receipt=json.loads(simc_source.bounded_read(receipt_file,2_000_000))
    need(receipt.get("schema")==simc_source.SCHEMA and
         receipt.get("provenance_tree_blob_authenticated") is True and
         receipt.get("item_data_present") is True and
         receipt.get("simc_generated_build")==game_build and
         receipt.get("simc_revision")==simc_revision and
         type(receipt.get("source_files",{}).get("item_data.inc")) is dict,
         "V216_SELECTED_GEM_V230_ORIGINAL_BUILD_REVISION_REQUIRED")
    input_seed={
        "game_build":game_build,"simc_revision":simc_revision,
        "seed_receipt_sha256":digest(receipt_file.read_bytes()),
        "selected_gem_item_ids":selected,
        "v230_parser_code_sha256":stage_engine.module_dependency_fingerprint(
            [pathlib.Path(simc_item_metadata.__file__),
             pathlib.Path(stage_engine.__file__)])["sha256"]}
    key=digest(canonical(input_seed).encode("utf8"))[:20]
    output="fresh_source/v230_selected_gem_item_source_"+key+".json"
    path=root/output
    def execute():
        original=simc_item_metadata.from_seed(
            directory=seed,item_ids=selected)
        need(original.get("schema")==simc_item_metadata.SCHEMA and
             original.get("game_build")==game_build and
             original.get("simc_revision")==simc_revision and
             original.get("requested_item_count")==len(selected) and
             [row.get("item_id") for row in original.get("items",[])]==
                selected and
             all(type(row.get("quality")) is int and
                 type(row.get("crafting_quality")) is int and
                 row["quality"]>=0 and row["crafting_quality"]>=0 and
                 row.get("class_id")==gem_item_join.GEM_CLASS
                 for row in original["items"]),
             "V216_SELECTED_GEM_V230_EXACT_GEM_METADATA_REQUIRED")
        payload={
            "schema":"v216_selected_gem_source_quality_observation_v1",
            "status":"PINNED_SIMC_GEM_QUALITY_SOURCE_ONLY_UNADMITTED",
            "game_build":game_build,"simc_revision":simc_revision,
            "seed_receipt_sha256":original["source_receipt_sha256"],
            "item_data_sha256":original["source_sha256"],
            "selected_item_ids":selected,
            "selected_item_quality_unadmitted":[{
                "item_id":row["item_id"],
                "quality":row["quality"],
                "crafting_quality":row["crafting_quality"],
                "class_id":row["class_id"],
                "subclass_id":row["subclass_id"],
            } for row in original["items"]],
            "exact_same_effect_and_conditions_verified":False,
            "highest_quality_selection_verified":False,
            "special_gem_role_verified":False,
            "game_socket_legality_verified":False,
            "environment_ready":False,
            "native_calls":0,"network_calls":0}
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(canonical(payload)+"\n",encoding="utf8")
    def validate(files):
        try:
            doc=json.loads(files["quality"].read_text("utf8"))
            qualities=doc["selected_item_quality_unadmitted"]
            return (doc.get("schema")==
                    "v216_selected_gem_source_quality_observation_v1" and
                    doc.get("status")==
                    "PINNED_SIMC_GEM_QUALITY_SOURCE_ONLY_UNADMITTED" and
                    doc.get("game_build")==game_build and
                    doc.get("simc_revision")==simc_revision and
                    doc.get("selected_item_ids")==selected and
                    doc.get("seed_receipt_sha256")==
                        receipt["receipt_sha256"] and
                    doc.get("item_data_sha256")==
                        receipt["source_files"]["item_data.inc"]["sha256"] and
                    type(qualities) is list and
                    len(qualities)==len(selected) and
                    [row.get("item_id") for row in qualities]==selected and
                    all(type(row.get(k)) is int and row[k]>=0
                        for row in qualities
                        for k in ("quality","crafting_quality",
                                  "class_id","subclass_id")) and
                    all(row["class_id"]==gem_item_join.GEM_CLASS
                        for row in qualities) and
                    doc.get("highest_quality_selection_verified") is False and
                    doc.get("special_gem_role_verified") is False and
                    doc.get("game_socket_legality_verified") is False and
                    doc.get("environment_ready") is False and
                    doc.get("native_calls")==0 and doc.get("network_calls")==0)
        except (OSError,ValueError,KeyError,TypeError):
            return False
    try:
        stage=stage_engine.execute_stage(
            root=root,stage_id="fresh-v230-selected-gem-"+key,
            stage_version="selected-gem-existing-v230-quality-source-v1",
            inputs=input_seed,outputs={"quality":output},
            execute=execute,validate=validate)
    except (simc_item_metadata.ItemMetadataBlocked,
            stage_engine.StageExecutionBlocked,
            EnvironmentBuildBlocked,ValueError,OSError,KeyError) as exc:
        return {"status":"PINNED_SIMC_SELECTED_GEM_METADATA_PENDING",
                "reason":str(exc).split(":",1)[0],
                "quality_source_authenticated":False,
                "native_calls":0,"network_calls":0}
    doc=json.loads(path.read_text("utf8"))
    return {**doc,"v230_stage_receipt_sha256":stage["receipt_sha256"],
            "v230_stage_cache_status":stage["status"],
            "quality_source_authenticated":True}


def _selected_gem_quality_policy_A_preview(*, source_catalog,
                                           source_item_link, gem_enchant,
                                           ordinary_gem_ids):
    """Reuse original v221/v266/v230 comparable-effect observations.

    The best OBSERVED comparable secondary-stat vector suffices for the
    quality preference; no exhaustive market scan or separate use-condition
    certificate is required. Exact source/slot and four v220 proof families
    still control final admission, not this source-only grouping.
    """
    properties=source_item_link.get(
        "selected_gem_property_records_unadmitted")
    if properties is None:
        return {"status":"SELECTED_GEM_PROPERTY_SOURCE_PENDING",
                "per_item_policy_A_source_only":[],
                "quality_source_groups_unadmitted":[],
                "automatically_eligible":0,
                "user_selectable":False,"environment_ready":False}
    need(type(properties) is list and
         len(properties)==len(source_item_link["selected_item_ids"]) and
         [r.get("item_id") for r in properties]==
             source_item_link["selected_item_ids"],
         "V216_GEM_POLICY_A_PROPERTIES_IDENTITY_DRIFT")
    ordinary=set(ordinary_gem_ids)
    vectors=gem_enchant.get(
        "selected_gem_raw_CHMV_vectors_by_id_unadmitted") or {}
    need(type(vectors) is dict and len(vectors)<=64 and
         set(vectors)<=set(map(str,ordinary)),
         "V216_GEM_RAW_CHMV_VECTOR_SCOPE_DRIFT")
    quality=source_item_link.get(
        "selected_simc_gem_quality_source_unadmitted")
    metadata={}
    if type(quality) is dict and quality.get(
            "quality_source_authenticated") is True:
        need(quality.get("game_build")==source_catalog["game_build"]
             and quality.get("simc_revision")==source_catalog["simc_revision"]
             and quality.get("selected_item_ids")==
                 source_item_link["selected_item_ids"],
             "V216_GEM_QUALITY_SOURCE_BUILD_DRIFT")
        metadata={r["item_id"]:r
                  for r in quality["selected_item_quality_unadmitted"]}
        need(len(metadata)==len(properties),
             "V216_GEM_QUALITY_SOURCE_ITEM_COUNT_DRIFT")
    per_item=[]
    eligible_count=0
    source_groups={}
    for prop in properties:
        item_id=prop["item_id"]
        candidate=auto_admission.candidate_from_source_gem(
            source_catalog,prop)
        identity=auto_admission._identity(candidate)
        evidence={
            "v221_stage_receipt_sha256":
                source_item_link["v221_stage_receipt_sha256"],
            "v266_enchant_source_sha256":
                source_item_link["enchant_source_sha256"],
            "v221_exact_gem_property":prop}
        proof={"source_relation":{
            "identity":identity,
            "status":"EXACT_SOURCE_RELATION_VERIFIED",
            "evidence_sha256":digest(canonical(evidence).encode("utf8"))}}
        decision=auto_admission.decide(candidate,proof)
        eligible_count+=int(decision["eligible"])
        per_item.append({
            "item_id":item_id,"candidate":candidate,
            "source_relation_evidence_sha256":
                proof["source_relation"]["evidence_sha256"],
            "decision":decision,"user_selectable":False})
        if item_id not in ordinary or item_id not in metadata:
            continue
        row=metadata[item_id]
        # Exact source enchant/color/class/expansion identify a comparable
        # effect family. Minimum item level is NOT a separate quality gate:
        # variants may have different level restrictions, and SimC owns use.
        # Do not group merely by matching a name or quality rank.
        key=(prop["enchant_id"],prop["color_mask"],
             prop["expansion_id"],row["quality"],
             row["class_id"],row["subclass_id"])
        if prop["enchant_id"]>0 and prop["color_mask"]>0:
            source_groups.setdefault(key,[]).append({
                "item_id":item_id,
                "crafting_quality":row["crafting_quality"],
                "raw_CHMV_vector_unadmitted":vectors.get(str(item_id))})
    groups=[]
    for key,items in sorted(source_groups.items()):
        if len(items)<2:
            continue
        ranked=sorted(items,key=lambda x:(
            -x["crafting_quality"],x["item_id"]))
        raw=[x["raw_CHMV_vector_unadmitted"] for x in ranked]
        numeric=(all(type(x) is dict and
                     set(x)==set(season_budget_contract.STATS) and
                     all(type(v) is int and v>=0 for v in x.values())
                     and any(x.values()) for x in raw))
        same_vector=(numeric and all(x==raw[0] for x in raw[1:]))
        # Compare EFFECT rating, not quality labels. A top candidate must
        # dominate every observed 4-stat vector of the same stat-kind set.
        # Ties use the documented craft rank, then stable physical item ID.
        strongest=(max(ranked,key=lambda x:(
            sum(x["raw_CHMV_vector_unadmitted"].values())
            if type(x["raw_CHMV_vector_unadmitted"]) is dict else -1,
            x["crafting_quality"],-x["item_id"])) if numeric else None)
        top_vector=(strongest["raw_CHMV_vector_unadmitted"]
                    if strongest is not None else None)
        comparable=(numeric and all(
            {k for k,v in vec.items() if v>0}==
            {k for k,v in raw[0].items() if v>0} for vec in raw)
            and all(all(top_vector[k]>=vec[k]
                        for k in season_budget_contract.STATS)
                    for vec in raw))
        observed_top=strongest["item_id"] if comparable else None
        groups.append({
            "enchant_id":key[0],
            "same_v221_color_expansion_and_v230_class_source":True,
            "observed_item_ids":[r["item_id"] for r in ranked],
            "observed_crafting_quality_ranks":[
                r["crafting_quality"] for r in ranked],
            "same_raw_four_stat_vector_source_only":bool(same_vector),
            "observed_effect_vectors_comparable_source_only":bool(comparable),
            "highest_observed_quality_item_id_unadmitted":observed_top,
            "highest_observed_effect_item_id_source_only":observed_top,
            "observed_strongest_effect_sufficient_quality_policy":bool(comparable),
            "actual_same_effect_and_use_conditions_verified":False,
            "all_available_quality_ranks_verified":False,
            "quality_filtered_user_options":False})
    return {
        "schema":"v216_selected_gem_quality_policy_A_preview_v1",
        "status":"SELECTED_GEM_SOURCE_RELATION_AND_QUALITY_UNADMITTED",
        "game_build":source_catalog["game_build"],
        "simc_revision":source_catalog["simc_revision"],
        "per_item_policy_A_source_only":per_item,
        "quality_source_groups_unadmitted":groups,
        "automatically_eligible":eligible_count,
        "source_relation_only":True,
        "highest_quality_verified":False,
        "actual_game_socket_verified":False,
        "user_selectable":False,"environment_ready":False,
        "native_calls":0,"network_calls":0}


def _reuse_observed_G_native_receipts(*, catalog, receipt_paths_by_ilevel):
    """Read v234's already-computed G once, no Native rerun or new verifier.

    This is a source-bound NUMERIC input, not item-eligibility certification.
    Even a well-formed observed native receipt must not imply environment READY.
    """
    need(type(receipt_paths_by_ilevel) is dict and
         1 <= len(receipt_paths_by_ilevel) <= 200 and
         all(type(k) is int and k > 0 for k in receipt_paths_by_ilevel),
         "V216_G_NATIVE_MEASURED_LEVELS_REQUIRED")
    result={}
    for level,path in sorted(receipt_paths_by_ilevel.items()):
        try:
            file=pathlib.Path(path)
            need(file.is_file() and not file.is_symlink() and
                 0 < file.stat().st_size <= MAX_RECEIPT_BYTES,
                 "V216_G_NATIVE_OBSERVATION_RECEIPT_FILE_INVALID")
            raw=file.read_bytes()
            need(0 < len(raw) <= MAX_RECEIPT_BYTES,
                 "V216_G_NATIVE_OBSERVATION_RECEIPT_TOO_LARGE")
            receipt=json.loads(raw)
            need(type(receipt) is dict and
                 type(receipt.get("observed_G")) is dict,
                 "V216_G_NATIVE_OBSERVED_OBJECT_REQUIRED")
            observed=receipt["observed_G"]
            original={k:v for k,v in observed.items() if k!="receipt_sha256"}
            expected_sha=digest(canonical(original).encode("utf8"))
            need(type(receipt.get("identity")) is dict and
                 observed.get("schema")==
                     "v234_one_source_only_physical_native_G_observation_v1"
                 and receipt.get("status")==
                     "PASS_NATIVE_PHYSICAL_G_OBSERVED_NOT_SEASON_APPROVED"
                 and receipt.get("native_returncode")==0
                 and receipt.get("new_native_calls")==1
                 and receipt.get("environment_ready") is False
                 and type(observed) is dict
                 and observed.get("receipt_sha256")==expected_sha
                 and observed.get("source_simc_revision")==
                     catalog["simc_revision"]
                 and observed.get(
                     "game_build_from_source_not_independently_binary_attested")==
                     catalog["game_build"]
                 and observed.get("target_ilevel")==level
                 and receipt.get("identity",{}).get("source_game_build")==
                     catalog["game_build"]
                 and receipt.get("native_json2_sha256")==
                     observed.get("native_json2_sha256")
                 and observed.get("full_G_approved") is False
                 and observed.get("environment_ready") is False,
                 "V216_G_NATIVE_OBSERVATION_IDENTITY_DRIFT")
            rounded=season_budget_contract.standardize_representative_G(
                observed_G_total=observed["observed_G_total"],
                target_ilevel=level,
                source_observation_sha256=observed["native_json2_sha256"])
            need(observed.get("standardized_G_preview_unapproved")==rounded,
                 "V216_G_NATIVE_ROUNDING_RECEIPT_DRIFT")
        except (OSError,TypeError,ValueError,KeyError,
                season_budget_contract.SeasonBudgetBlocked) as exc:
            raise EnvironmentBuildBlocked(
                "V216_EXISTING_G_NATIVE_RECEIPT_INVALID:" + str(exc)) from exc
        result[level]={
            "target_ilevel":level,
            "native_receipt_sha256":digest(raw),
            "native_json2_sha256":observed["native_json2_sha256"],
            "source_profile_receipt_sha256":
                observed["source_profile_receipt_sha256"],
            "source_candidate_receipt_sha256":
                observed.get("source_candidate_receipt_sha256"),
            "class":observed.get("class"),"spec":observed.get("spec"),
            "standardization":rounded,
            # The existing v232 plain/primary/weapon proof plus v234 Native
            # static observation is enough to use the numeric G reference.
            # Active-season acquisition remains a SEPARATE diagnostic.
            "generic_G_numeric_reference_usable":(
                observed.get("generic_G_numeric_reference_usable") is True
                and observed.get(
                    "generic_G_current_season_membership_required") is False),
            "generic_G_standard_rating":(
                rounded["standardized_G"]
                if observed.get("generic_G_numeric_reference_usable") is True
                and observed.get(
                    "generic_G_current_season_membership_required") is False
                else None),
            "current_season_acquisition_required_for_G":False,
            "source_selection_status":"OBSERVED_PHYSICAL_NOT_SEASON_ADMITTED",
        }
    return result


def _existing_simc_native_effect_snapshot(*, candidate, simc_revision):
    """Read two existing SimC JSON2 outputs, not a second effects engine.

    No Native execution, automatic F/O/J admission, or session mutation.
    v198 already established matched precombat rating deltas for enchants.
    """
    need(type(candidate) is dict and
         set(candidate)=={
             "source_profile_path","kind","token",
             "baseline_json2_path","active_json2_path","binary_sha256"},
         "V216_SIMC_EFFECT_PAIR_INTERNAL_INPUT_REQUIRED")
    try:
        paths={key:pathlib.Path(candidate[key]) for key in (
            "source_profile_path","baseline_json2_path",
            "active_json2_path")}
        need(all(p.is_file() and not p.is_symlink() and
                 0<p.stat().st_size<=(
                     4_000_000 if k=="source_profile_path"
                     else simc_snapshot_delta.MAX_JSON)
                 for k,p in paths.items()),
             "V216_SIMC_EFFECT_PAIR_SOURCE_FILES_INVALID")
        source=paths["source_profile_path"].read_text("utf8")
        paired=simc_snapshot_delta.prepare(
            profile=source,kind=candidate["kind"],token=candidate["token"])
        observed=simc_snapshot_delta.compare(
            baseline_json2=paths["baseline_json2_path"].read_bytes(),
            active_json2=paths["active_json2_path"].read_bytes(),
            prepared=paired,binary_sha256=candidate["binary_sha256"],
            simc_revision=simc_revision)
    except (OSError,UnicodeError,ValueError,TypeError,
            simc_snapshot_delta.SnapshotBlocked) as exc:
        raise EnvironmentBuildBlocked(
            "V216_EXISTING_SIMC_EFFECT_NATIVE_DELTA_INVALID:"+str(exc)) from exc
    return observed


def _reuse_v277_G_in_preprofile(*, catalog, target_ilevel, native_G,
                                budget_evidence):
    """Bind this Build's already-verified v277 numeric G to existing v222.

    No source collection, Native retry, new rounding rule or READY admission.
    v277 owns the original source/profile/binary/receipt verification. The
    preflight checks numeric identity and only fills a missing G in a supplied
    J/F/O arithmetic candidate; it does not authenticate those components.
    """
    need(native_G is None or type(native_G) is dict,
         "V216_ZERO_HISTORY_V277_SOURCE_OBJECT_INVALID")
    if (native_G is None or native_G.get("status") !=
            "G_NATIVE_NUMERIC_REFERENCE_OBSERVED_JFO_PENDING"):
        return None, budget_evidence
    require_sha = season_budget_contract.SHA.fullmatch
    rounded = native_G.get("standardization")
    source_sha = native_G.get("native_json2_sha256")
    need(type(target_ilevel) is int and target_ilevel > 0
         and type(source_sha) is str and require_sha(source_sha) is not None
         and type(native_G.get("observed_G_total")) is int
         and native_G["observed_G_total"] > 0
         and type(native_G.get("standardized_G")) is int
         and type(rounded) is dict
         and all(type(native_G.get(k)) is str
                 and require_sha(native_G[k]) is not None for k in (
                     "native_receipt_sha256",
                     "source_profile_receipt_sha256",
                     "native_binary_sha256"))
         and type(native_G.get("new_native_calls")) is int
         and native_G["new_native_calls"] in (0, 1)
         and native_G.get("full_G_approved") is False
         and native_G.get("environment_ready") is False,
         "V216_ZERO_HISTORY_V277_NUMERIC_SOURCE_INVALID")
    try:
        expected = season_budget_contract.standardize_representative_G(
            observed_G_total=native_G["observed_G_total"],
            target_ilevel=target_ilevel,
            source_observation_sha256=source_sha)
    except season_budget_contract.SeasonBudgetBlocked as exc:
        raise EnvironmentBuildBlocked(
            "V216_ZERO_HISTORY_V277_G_STANDARDIZATION_INVALID:" + str(exc)
        ) from exc
    need(rounded == expected
         and native_G["standardized_G"] == expected["standardized_G"],
         "V216_ZERO_HISTORY_V277_G_ROUNDING_OR_TARGET_DRIFT")
    candidate = {
        "status": "NATIVE_G_NUMERIC_SOURCE_ONLY_JFO_AND_ADMISSION_PENDING",
        "game_build": catalog["game_build"],
        "simc_revision": catalog["simc_revision"],
        "target_ilevel": target_ilevel,
        "observed_G_total": native_G["observed_G_total"],
        "standardized_G": native_G["standardized_G"],
        "standardization": expected,
        "native_json2_sha256": source_sha,
        "native_receipt_sha256": native_G["native_receipt_sha256"],
        "source_profile_receipt_sha256":
            native_G["source_profile_receipt_sha256"],
        "native_binary_sha256": native_G["native_binary_sha256"],
        "source_admission_performed_here": False,
        "environment_ready": False,
        "network_calls": 0, "native_calls": 0,
    }
    if budget_evidence is None:
        return candidate, None
    need(type(budget_evidence) is dict
         and type(budget_evidence.get("components")) is dict,
         "V216_ZERO_HISTORY_V277_BUDGET_COMPONENTS_REQUIRED")
    components = dict(budget_evidence["components"])
    if components.get("G") is None:
        components["G"] = {
            "game_build": catalog["game_build"],
            "source_catalog_manifest_sha256": catalog["manifest_sha256"],
            "source_sha256": source_sha,
            "source_verification": "EXACT_NATIVE",
            "rating": expected["standardized_G"],
            "standardization": expected,
        }
    else:
        proof = components["G"]
        need(type(proof) is dict
             and proof.get("rating") == expected["standardized_G"]
             and proof.get("source_sha256") == source_sha
             and proof.get("standardization") == expected,
             "V216_ZERO_HISTORY_V277_G_V222_CONFLICT")
    return candidate, {
        **budget_evidence, "components": components,
    }


def _v217_policy_A_source_relation_receipts(*, catalog, artifact_sha256,
                                           catalog_path, stage_attestations,
                                           public_rows):
    """Consume ORIGINAL sealed v241/v217 source joins; no new trust gate.

    This attests only exact source ItemID/token/slot-mask provenance within
    already-sealed v191→v211→v213. It does NOT authenticate game usability,
    same-effect quality, Native acceptance or CHMV fixed E. The remaining
    Policy A receipt families and unresolved physical slots stay pending.
    """
    if stage_attestations is None:
        return {}
    need(type(stage_attestations) is dict and
         set(stage_attestations)=={
             "stage_root","v191_stage","v211_stage","v213_stage"},
         "V216_POLICY_A_ORIGINAL_STAGE_ATTESTATIONS_INVALID")
    if any(stage_attestations[k] is None
           for k in ("v191_stage","v211_stage","v213_stage")):
        return {}
    stage_root=pathlib.Path(stage_attestations["stage_root"]).expanduser()
    need(stage_root.is_dir() and not stage_root.is_symlink() and
         pathlib.Path(catalog_path).resolve()==
             (stage_root.resolve()/"fresh_source"/
              "v213_candidate_catalog.json"),
         "V216_POLICY_A_V213_ORIGINAL_STAGE_PATH_DRIFT")
    source_provenance=catalog["source_provenance"]
    expected={
        "v191":("candidate","fresh_source/v191_candidate.json",
                source_provenance["v191"]["sha256"]),
        "v211":("classification","fresh_source/v211_classification.json",
                source_provenance["v211"]["sha256"]),
        "v213":("candidate","fresh_source/v213_candidate_catalog.json",
                artifact_sha256),
    }
    stamps={}
    for short,(output_name,relative,expected_sha) in expected.items():
        summary=stage_attestations["v"+short[1:]+"_stage"]
        need(type(summary) is dict and
             summary.get("status") in (
                 "EXECUTED_AND_SEALED","REUSED_VERIFIED",
                 "RECOVERED_VERIFIED") and
             summary.get("stage_id")=="fresh-"+short,
             "V216_POLICY_A_V217_STAGE_ATTESTATION_MISSING:"+short)
        receipt=stage_engine._read_receipt(
            stage_root/".stage_receipts"/("fresh-"+short+".json"))
        need(receipt.get("stage_id")=="fresh-"+short and
             receipt.get("stage_version")=="1" and
             receipt.get("status")=="COMPLETE" and
             receipt.get("receipt_sha256")==summary.get("receipt_sha256") and
             receipt.get("output_paths")=={output_name:relative} and
             type(receipt.get("outputs")) is dict and
             receipt["outputs"].get(output_name,{}).get("sha256")==
                 expected_sha and
             receipt["outputs"][output_name].get("path")==relative,
             "V216_POLICY_A_V217_SOURCE_OUTPUT_SHA_DRIFT:"+short)
        stamps[short]=receipt["receipt_sha256"]
    catalog_items={row["enchant_id"]:row
                   for row in catalog["catalog"]["enchants"]["items"]}
    v196_items={row["enchant_id"]:row
                for row in catalog["v196_enchant_source"]["rows"]}
    need(len(catalog_items)==len(v196_items)==len(public_rows),
         "V216_POLICY_A_SOURCE_RELATION_CANDIDATE_COVERAGE_DRIFT")
    source_context={"game_build":catalog["game_build"],
                    "simc_revision":catalog["simc_revision"],
                    "manifest_sha256":catalog["manifest_sha256"]}
    proofs={}
    for row in public_rows:
        item=catalog_items.get(row["enchant_id"])
        projected=v196_items.get(row["enchant_id"])
        need(item is not None and projected is not None and
             item["token"]==row["token"]==projected["token"] and
             item["inventory_type_mask"]==
                 projected["inventory_type_mask"],
             "V216_POLICY_A_SOURCE_JOIN_ID_TOKEN_MASK_DRIFT")
        candidate=auto_admission.candidate_from_source_enchant(
            source_context,row)
        identity=auto_admission._identity(candidate)
        payload={"identity":identity,"v217_source_receipts":stamps,
                 "v213_catalog_manifest_sha256":catalog["manifest_sha256"],
                 "v213_catalog_artifact_sha256":artifact_sha256,
                 "source_inventory_mask":item["inventory_type_mask"],
                 "source_item_subclass_mask":item["item_subclass_mask"],
                 "source_slot_group":item["slot_group"]}
        proofs[row["enchant_id"]]={
            "source_relation":{
                "identity":identity,
                "status":"EXACT_SOURCE_RELATION_VERIFIED",
                "evidence_sha256":digest(canonical(payload).encode("utf8"))}}
    return proofs


def preflight_new_season_source(*, source_catalog_path, expected_game_build,
                                expected_simc_revision, budget_evidence=None,
                                target_ilevel=None, manual_final_T=None,
                                source_snapshot_folder=None,
                                source_stage_root=None,
                                standard_budget_evidence_by_ilevel=None,
                                standard_budget_reference_track=None,
                                g_native_receipt_paths_by_ilevel=None,
                                simc_effect_snapshot_case=None,
                                gem_layout_receipt=None,
                                gem_rating_by_id=None,
                                nominal_gem_source=None,
                                zero_history_native_G=None,
                                policy_A_v217_stages=None,
                                pinned_gem_simc_source_folder=None):
    """Inspect a freshly assembled v213 artifact in the NORMAL Build path.

    This does not install an environment. Reuse authenticated source
    acquisition facts exactly once; identify only missing item-level G/J/F/O
    values or applicability. Reading a stored hash is not proof of game
    eligibility, and this numeric preflight is not another certification Gate.
    """
    need(type(expected_game_build) is str and bool(expected_game_build)
         and type(expected_simc_revision) is str and
         re.fullmatch(r"[a-f0-9]{40}",expected_simc_revision),
         "V216_FRESH_EXPECTED_BUILD_AND_SOURCE_COMMIT_REQUIRED")
    supplied=pathlib.Path(source_catalog_path)
    need(supplied.is_file() and not supplied.is_symlink(),
         "V216_FRESH_V213_SOURCE_FILE_REQUIRED")
    source,raw_sha=environment_manifest.read_json(supplied)
    try:
        source_to_catalog.verify_catalog(source)
        ui=user_catalog.public_options(supplied)
        # The v241 stage executor has already checked the same bytes. Reuse
        # its sealed original receipts to populate only source_relation,
        # with no fresh HTTP/Native and no standalone admission engine.
        source_relations={}
        if policy_A_v217_stages is not None:
            source_relations=_v217_policy_A_source_relation_receipts(
                catalog=source,artifact_sha256=raw_sha,catalog_path=supplied,
                stage_attestations=policy_A_v217_stages,
                public_rows=ui.get("enchant_candidates",{}).get("items",[]))
        prepared_options=None
        if source_relations:
            prepared_options,projected=(
                user_catalog.prepare_verified_fresh_choices(
                    source,ui,source_relations,
                    return_policy_A_preview=True))
            # Projection changes only diagnostics, not selectable rows.
            ui["automatic_admission"]={
                **ui["automatic_admission"],**projected,
                "status":"V217_SOURCE_RELATION_ONLY_OTHER_PROOFS_PENDING",
                "approved_count":0,"v212_install_or_user_selection_authorized":False}
    except (source_to_catalog.CatalogBlocked,
            user_catalog.CatalogBlocked) as exc:
        raise EnvironmentBuildBlocked(
            "V216_FRESH_SOURCE_OR_UI_CONTRACT_BLOCKED:"+str(exc)) from exc
    need(source.get("game_build")==expected_game_build and
         source.get("simc_revision")==expected_simc_revision and
         ui.get("season_build")==expected_game_build and
         ui.get("simc_revision")==expected_simc_revision,
         "V216_FRESH_SEASON_BUILD_OR_SIMC_REVISION_MISMATCH")
    v191=source.get("source_provenance",{}).get("v191",{})
    v211=source.get("enchant_classification",{})
    inputs=v191.get("sha256_by_input")
    need(type(inputs) is dict and
         inputs.get("budget") is None and
         v211.get("source_manifest_sha256") is not None and
         source.get("catalog",{}).get("consumables",{}).get(
             "flask",{}).get("reference","MISSING") is None and
         source.get("catalog",{}).get("consumables",{}).get(
             "general_gems",{}).get("reference","MISSING") is None,
         "V216_FRESH_NO_HISTORICAL_BUDGET_AND_SOURCE_PROOF_REQUIRED")
    need(ui.get("status")==
             "FRESH_SEASON_CANDIDATES_UNAPPROVED_NOT_ENVIRONMENT_READY" and
         ui.get("enchant_candidates",{}).get("selectable_count")==0 and
         ui.get("existing_allowed_input_choices")=={} and
         ui.get("environment_ready") is False and
         all(ui.get(x) is None for x in ("G","J","F","O","B","T")) and
         ui.get("native_calls_now")==0 and
         ui.get("game_db_recollection_now")==0 and
         ui.get("optimizer_or_cache_mutated") is False,
         "V216_FRESH_UNVERIFIED_CHOICE_OR_BUDGET_PROMOTION")
    # Reuse the already sealed v221→v266→v268 source data BEFORE checking J.
    # v268 returns selected item IDs only, not another large gem catalog.
    # Raw EffectPointsMin values are candidates, not SimC-effective ratings.
    need(source_snapshot_folder is not None or source_stage_root is None,
         "V216_FRESH_GEM_SNAPSHOT_AND_STAGE_MUST_BE_PAIRED")
    need(source_stage_root is not None or source_snapshot_folder is None,
         "V216_FRESH_GEM_SNAPSHOT_AND_STAGE_MUST_BE_PAIRED")
    gem_source = None
    gem_enchant = None
    selected_source_ids=(
        gem_layout_receipt.get(physical_gems.SOURCE_IDS_FIELD)
        if type(gem_layout_receipt) is dict else None)
    if source_snapshot_folder is not None:
        gem_source = _fresh_gem_item_source_stage(
            stage_root=source_stage_root,
            wago_folder=source_snapshot_folder,
            source_catalog_path=supplied,
            expected_game_build=expected_game_build)
        if gem_source.get("candidate_path"):
            gem_enchant=gem_enchant_stage.view(
                stage_root=source_stage_root,
                v221_candidate_path=gem_source["candidate_path"],
                build=expected_game_build,
                selected_gem_item_ids=(
                    gem_layout_receipt.get("ordinary_gem_ids")
                    if type(gem_layout_receipt) is dict else None),
                selected_source_gem_item_ids=selected_source_ids,
                selected_special_gem_item_id=(
                    gem_layout_receipt.get("special_gem_id")
                    if selected_source_ids is not None and
                       type(gem_layout_receipt) is dict else None))
    # New-season physical IDs are accepted for a SOURCE-ONLY preview only
    # when the ORIGINAL sealed v221→v266 join actually contains all IDs.
    # An input list or SHA string by itself never certifies a special gem,
    # a legal socket, effect/quality equivalence, or effective J.
    source_item_link=None
    if selected_source_ids is not None:
        need(type(selected_source_ids) is list and
             1<=len(selected_source_ids)<=64 and
             all(type(x) is int and x>0 for x in selected_source_ids) and
             len(set(selected_source_ids))==len(selected_source_ids) and
             type(gem_enchant) is dict and
             gem_enchant.get("selected_gem_v221_same_build_items_all_present") is True and
             gem_enchant.get("selected_gem_v221_item_ids_unadmitted")==
                 sorted(selected_source_ids) and
             type(gem_source) is dict and
             type(gem_source.get("source_stage")) is dict and
             type(gem_source["source_stage"].get("receipt_sha256")) is str,
             "V216_V221_SELECTED_SAME_BUILD_GEM_ITEM_SOURCE_REQUIRED")
        source_properties=None
        if gem_enchant.get("selected_gem_v221_source_properties_complete") is True:
            props=gem_enchant.get(
                "selected_gem_v221_source_properties_unadmitted")
            keys={"item_id","gem_property_id","enchant_id","color_mask",
                  "minimum_ilevel","expansion_id"}
            need(type(props) is list and len(props)==len(selected_source_ids)
                 and [row.get("item_id") for row in props
                      if type(row) is dict]==sorted(selected_source_ids)
                 and all(type(row) is dict and set(row)==keys and
                         all(type(v) is int and v>=0
                             for v in row.values()) and
                         row["gem_property_id"]>0 for row in props),
                 "V216_SELECTED_V221_SOURCE_PROPERTY_RECORDS_DRIFT")
            source_properties=[dict(row) for row in props]
        quality_source=None
        if pinned_gem_simc_source_folder is not None:
            quality_source=_fresh_selected_gem_simc_quality_stage(
                stage_root=source_stage_root,
                seed_directory=pinned_gem_simc_source_folder,
                game_build=expected_game_build,
                simc_revision=expected_simc_revision,
                selected_item_ids=sorted(selected_source_ids))
            if quality_source.get("quality_source_authenticated") is True:
                rows=quality_source.get(
                    "selected_item_quality_unadmitted")
                need(quality_source.get("game_build")==expected_game_build
                     and quality_source.get("simc_revision")==
                        expected_simc_revision
                     and quality_source.get("selected_item_ids")==
                         sorted(selected_source_ids)
                     and type(rows) is list and
                     len(rows)==len(selected_source_ids)
                     and [row.get("item_id") for row in rows
                          if type(row) is dict]==sorted(selected_source_ids)
                     and all(type(row) is dict and
                         set(row)=={"item_id","quality","crafting_quality",
                                    "class_id","subclass_id"}
                         and all(type(v) is int and v>=0
                                 for v in row.values())
                         and row["class_id"]==gem_item_join.GEM_CLASS
                         for row in rows),
                     "V216_V230_SELECTED_GEM_QUALITY_SOURCE_SCOPE_DRIFT")
        special_raw=gem_enchant.get(
            "selected_special_gem_raw_effect_unadmitted")
        if special_raw is not None:
            need(type(special_raw) is dict and
                 special_raw.get("item_id")==
                     gem_layout_receipt["special_gem_id"] and
                 special_raw.get("effect_classification") in (
                     "RAW_STATIC_CHMV_POINTS_CANDIDATE_ONLY",
                     "NONSTATIC_SCALED_OR_NON_CHMV_EFFECT_PENDING",
                     "ENCHANT_ID_MISSING_FROM_SAME_BUILD_CSV") and
                 special_raw.get("missing_or_nonstatic_never_assumed_zero")
                     is True and
                 special_raw.get("simc_effective_rating_verified") is False and
                 special_raw.get("J_budget_attribution_verified") is False,
                 "V216_SPECIAL_GEM_RAW_EFFECT_SOURCE_SCOPE_DRIFT")
            vector=special_raw.get(
                "raw_static_CHMV_vector_candidate_unadmitted")
            rating=special_raw.get(
                "raw_static_CHMV_total_candidate_unadmitted")
            if vector is None:
                need(rating is None and
                     special_raw["effect_classification"]!=
                     "RAW_STATIC_CHMV_POINTS_CANDIDATE_ONLY",
                     "V216_SPECIAL_GEM_UNKNOWN_STATIC_NOT_ZERO")
            else:
                need(type(vector) is dict and
                     set(vector)==set(season_budget_contract.STATS) and
                     all(type(n) is int and n>=0 for n in vector.values())
                     and type(rating) is int and rating>0 and
                     sum(vector.values())==rating and
                     special_raw["effect_classification"]==
                         "RAW_STATIC_CHMV_POINTS_CANDIDATE_ONLY",
                     "V216_SPECIAL_GEM_RAW_STATIC_VECTOR_DRIFT")
        source_item_link={
            "selected_special_gem_raw_effect_unadmitted":special_raw,
            "selected_simc_gem_quality_source_unadmitted":quality_source,
            "selected_item_ids":sorted(selected_source_ids),
            "selected_gem_property_records_unadmitted":source_properties,
            "gem_property_source_fields_complete":source_properties is not None,
            "special_gem_source_property_unadmitted":(
                next(row for row in source_properties
                     if row["item_id"]==gem_layout_receipt["special_gem_id"])
                if source_properties is not None else None),
            "special_gem_item_id":gem_layout_receipt["special_gem_id"],
            "v221_stage_receipt_sha256":
                gem_source["source_stage"]["receipt_sha256"],
            "enchant_source_sha256":gem_enchant["enchant_source_sha256"],
            "same_build_gem_item_join_only":True,
            "special_class_and_quality_verified":False,
            "game_socket_applicability_verified":False,
            # Compatibility diagnostic only; this is NOT a separate
            # admission gate for the nominal ordinary-gem J budget.
            "simc_effective_J_verified":False}
        source_item_link["gem_policy_A_source_and_quality_unadmitted"]=(
            _selected_gem_quality_policy_A_preview(
                source_catalog=source,source_item_link=source_item_link,
                gem_enchant=gem_enchant,
                ordinary_gem_ids=gem_layout_receipt["ordinary_gem_ids"]))
    # A staged physical gem layout is not evidence of legal game sockets.
    need(gem_layout_receipt is not None or gem_rating_by_id is None,
         "V216_GEM_LAYOUT_REQUIRED_BEFORE_RATING_MATCH")
    gem_J=None
    raw_gem_ratings=None
    # Numeric J owns exactly-two-stat ordinary gems, not single-stat
    # activation gems. This never blocks the physical SimC socket layout.
    one_stat_or_ambiguous_J=(
        type(gem_enchant) is dict and gem_enchant.get(
            "selected_ordinary_gem_two_stat_budget_eligible_unadmitted")
        is False)
    if nominal_gem_source is not None:
        # Different numeric owner than v266 raw effect points. Only a
        # matching SAME-BUILD physical v221 link may consume this preview.
        # This is still UNADMITTED until the existing source/quality and
        # v222/v212 install provider accepts it.
        need(type(gem_layout_receipt) is dict and
             type(source_item_link) is dict and
             source_item_link.get("same_build_gem_item_join_only") is True,
             "V216_NOMINAL_J_V221_PHYSICAL_SOURCE_REQUIRED")
        nominal=physical_gems.nominal_four_stat_from_season_source(
            source=nominal_gem_source,game_build=expected_game_build,
            socket_total=gem_layout_receipt["socket_total"],
            special_gem_id=gem_layout_receipt["special_gem_id"],need=need)
        need(gem_rating_by_id==nominal["rating_by_id"] and
             gem_layout_receipt["ordinary_gem_ids"]==
                nominal["ordinary_gem_ids"],
             "V216_NOMINAL_J_PHYSICAL_IDS_OR_TOTALS_DRIFT")
        one_stat_or_ambiguous_J=False
    if gem_layout_receipt is not None:
        if (not one_stat_or_ambiguous_J and gem_enchant is not None
                and gem_enchant.get(
                    "selected_gem_all_raw_points_known") is True):
            raw_gem_ratings=dict(gem_enchant[
                "selected_gem_raw_points_by_id_unadmitted"])
        if gem_rating_by_id is not None and not one_stat_or_ambiguous_J:
            gem_J=physical_gems.reconcile_observed_J(
                gem_layout_receipt,gem_rating_by_id,need)
        elif raw_gem_ratings is not None:
            gem_J=physical_gems.reconcile_observed_J(
                gem_layout_receipt,raw_gem_ratings,need)
            gem_J={**gem_J,
                   "rating_origin":"V266_RAW_SAME_BUILD_EFFECT_POINTS_ONLY",
                   "simc_effective_rating_verified":False,
                   "highest_quality_verified":False,
                   "source_enchant_sha256":
                       gem_enchant["enchant_source_sha256"],
                   "source_v221_stage_receipt_sha256":
                       (gem_source.get("source_stage") or {}).get(
                           "receipt_sha256")}
        if gem_J is not None and nominal_gem_source is not None:
            gem_J={**gem_J,
                   "rating_origin":"SEASON_NOMINAL_PER_ITEM_TOTAL_SOURCE",
                   "nominal_source_sha256":
                       nominal_gem_source["source_sha256"],
                   "nominal_source_game_build":expected_game_build,
                   "source_v221_stage_receipt_sha256":
                       gem_source["source_stage"]["receipt_sha256"],
                   "v266_effect_points_numeric_required":False,
                   "quality_and_official_admission_verified":False}
        numeric_evidence=(
            ([budget_evidence] if budget_evidence is not None else [])+
            (list(standard_budget_evidence_by_ilevel.values())
             if type(standard_budget_evidence_by_ilevel) is dict else []))
        for row in numeric_evidence:
            proof=(row.get("components",{}).get("J")
                   if type(row) is dict and
                   type(row.get("components")) is dict else None)
            if type(proof) is dict and type(proof.get("rating")) is int:
                need(gem_J is not None,
                     "V216_J_PHYSICAL_ID_RATING_LINK_MISSING")
                # v266 raw points are NOT an exact SimC-effective rating.
                # Do not reject an independently verified J based on them.
                if gem_rating_by_id is not None:
                    need(proof["rating"]==gem_J["J_candidate_unadmitted"],
                         "V216_J_RATING_DISAGREES_WITH_PHYSICAL_GEM_IDS")
    # A caller may supply source-bound numeric evidence before a v098 profile
    # exists. Only arithmetic/identity is tested here: a self-declared
    # "verified" label cannot authenticate Wago/SimC/Native provenance.
    # The top-level G/J/F/O/B/T remain null and installation remains blocked.
    existing_G_rows = None
    if g_native_receipt_paths_by_ilevel is not None:
        existing_G_rows = _reuse_observed_G_native_receipts(
            catalog=source,
            receipt_paths_by_ilevel=g_native_receipt_paths_by_ilevel)
    v277_G_preview, budget_evidence = _reuse_v277_G_in_preprofile(
        catalog=source, target_ilevel=target_ilevel,
        native_G=zero_history_native_G, budget_evidence=budget_evidence)
    # Consume already-measured ilvl rows using v262/v222, not a new engine.
    need((standard_budget_evidence_by_ilevel is None) ==
         (standard_budget_reference_track is None),
         "V216_STANDARD_BUDGET_LEVELS_AND_TRACK_MUST_BE_PAIRED")
    # A normal Environment Build already has the actual v234 observed-G
    # receipt. When J/F/O evidence is present but G was not transcribed,
    # construct that one v222 G component directly from the Native bytes.
    # It is still a candidate arithmetic input, not environment admission.
    native_G_filled_levels=[]
    if (existing_G_rows is not None
            and standard_budget_evidence_by_ilevel is not None):
        need(set(existing_G_rows)==set(standard_budget_evidence_by_ilevel),
             "V216_G_NATIVE_V262_LEVEL_SET_MISMATCH")
        populated={}
        for level,evidence in standard_budget_evidence_by_ilevel.items():
            need(type(evidence) is dict and
                 type(evidence.get("components")) is dict,
                 "V216_GJFO_EVIDENCE_COMPONENTS_OBJECT_REQUIRED")
            components=evidence["components"]
            if components.get("G") is None:
                observed=existing_G_rows[level]
                need(observed["generic_G_numeric_reference_usable"] is True,
                     "V216_G_NATIVE_GENERIC_PHYSICAL_CONDITIONS_MISSING")
                rounded=observed["standardization"]
                g_component={
                    "rating":rounded["standardized_G"],
                    "game_build":source["game_build"],
                    "source_catalog_manifest_sha256":source["manifest_sha256"],
                    "source_sha256":observed["native_json2_sha256"],
                    "source_verification":"EXACT_NATIVE",
                    "standardization":rounded,
                    "reference_track":standard_budget_reference_track,
                }
                populated[level]={
                    **evidence,
                    "components":{**components,"G":g_component}}
                native_G_filled_levels.append(level)
            else:
                populated[level]=evidence
        standard_budget_evidence_by_ilevel=populated
    standard_table = None
    if standard_budget_evidence_by_ilevel is not None:
        try:
            standard_table = standardized_budget_rows.build(
                source_catalog=source, source_artifact_sha256=raw_sha,
                evidence_by_ilevel=standard_budget_evidence_by_ilevel,
                reference_track=standard_budget_reference_track)
        except season_budget_contract.SeasonBudgetBlocked as exc:
            raise EnvironmentBuildBlocked(
                "V216_STANDARD_BUDGET_ROWS_INVALID:" + str(exc)) from exc
        if target_ilevel is not None:
            need(target_ilevel in standard_budget_evidence_by_ilevel,
                 "V216_TARGET_ILEVEL_G_OBSERVATION_NOT_PROVIDED")
            target_evidence = standard_budget_evidence_by_ilevel[target_ilevel]
            need(budget_evidence is None or budget_evidence == target_evidence,
                 "V216_STANDARD_BUDGET_TARGET_EVIDENCE_CONFLICT")
            budget_evidence = target_evidence
    if existing_G_rows is not None and standard_table is not None:
        need(set(existing_G_rows)==set(standard_budget_evidence_by_ilevel),
             "V216_G_NATIVE_V262_LEVEL_SET_MISMATCH")
        for level,native_row in existing_G_rows.items():
            component=standard_budget_evidence_by_ilevel[level]["components"]["G"]
            need(component.get("source_sha256")==
                     native_row["native_json2_sha256"] and
                 component.get("standardization")==
                     native_row["standardization"],
                 "V216_G_NATIVE_V222_OBSERVATION_DRIFT")
    need(budget_evidence is not None or manual_final_T is None,
         "V216_PREPROFILE_BUDGET_INPUT_INCOMPLETE")
    proposed_budget = None
    if budget_evidence is not None:
        try:
            proposed_budget = season_budget_contract.preprofile_budget(
                source_catalog=source, source_artifact_sha256=raw_sha,
                evidence=budget_evidence, target_ilevel=target_ilevel,
                manual_final_T=manual_final_T)
        except season_budget_contract.SeasonBudgetBlocked as exc:
            raise EnvironmentBuildBlocked(
                "V216_PREPROFILE_GJFO_ARITHMETIC_BLOCKED:" + str(exc)
            ) from exc
    # Existing focused v216 callers can supply a minimal v196 mock
    # without per-item diagnostic detail. Do not reinterpret absent proof
    # data as zero missing items or as approved product choices.
    admission=ui.get("automatic_admission") or {}
    payload={
        "schema":FRESH_SOURCE_PREFLIGHT_SCHEMA,
        "status":"FRESH_SOURCE_CANDIDATES_VALID_GJFO_PENDING_NOT_INSTALLED",
        "game_build":expected_game_build,
        "simc_revision":expected_simc_revision,
        "source_artifact_sha256":raw_sha,
        "source_catalog_manifest_sha256":source["manifest_sha256"],
        "simc_source_manifest_sha256":v211["source_manifest_sha256"],
        "gear_candidates":source["catalog"]["gear"]["count"],
        "tier_pieces":source["catalog"]["tier"]["piece_count"],
        "enchant_candidates":ui["enchant_candidates"]["total"],
        "approved_new_choices":0,
        "G":None,"J":None,"F":None,"O":None,"B":None,"T":None,
        "environment_ready":False,
        # Only the base G/J/F/O and executable profile are core Build
        # dependencies. Optional enchants/consumables lacking Policy A
        # proof must be held per item, not block an otherwise verified base.
        "requires":["G/J/F/O_VERIFIED_SOURCE_RECEIPTS",
                    "NEW_SEASON_VERSIONED_ENVIRONMENT_MANIFEST_INSTALL"],
        "optional_choice_requires":[
                    "POLICY_A_EXACT_ITEM_PROOFS_WHEN_SELECTED"],
        "optional_policy_A_evidence_unadmitted":{
            "schema":admission.get("schema"),
            "source_catalog_manifest_sha256":source["manifest_sha256"],
            "source_catalog_artifact_sha256":raw_sha,
            "candidate_count":ui["enchant_candidates"]["total"],
            "pending":admission.get("pending"),
            "per_item_missing_reasons":dict(
                admission.get("per_item_missing_reasons") or {}),
            "per_item_conflict_reasons":dict(
                admission.get("per_item_conflict_reasons") or {}),
            "source_evidence_projection_provided":bool(admission),
            "v217_source_relation_receipt_count":len(source_relations),
            "v217_source_relation_scoped_only":True,
            "original_v217_source_relation_receipts_internal":
                dict(source_relations),
            "prepared_verified_options_unpublished":prepared_options,
            "verified_options_published":False,
            "affects_verified_base_GJFO":False},
        "source_retrieval_authenticated_by_this_stage":False,
        "native_calls":0,"network_calls":0,"cache_mutations":0,
    }
    if gem_source is not None:
        payload["fresh_gem_item_source_candidates"] = gem_source
        payload["requires"].append(
            "GEM_J_HIGHEST_QUALITY_ORDINARY_RATING_AND_REAL_SOCKET_SOURCE_PENDING")
    if gem_enchant is not None:
        payload["fresh_gem_raw_enchant_points_source"] = gem_enchant
    if gem_layout_receipt is not None:
        payload["physical_gem_layout_unadmitted"] = gem_layout_receipt
        if one_stat_or_ambiguous_J:
            payload["ordinary_gem_J_two_stat_requirement_pending"]=True
            payload["requires"].append(
                "ORDINARY_GEM_J_REQUIRES_EXACTLY_TWO_SECONDARY_STATS")
        if source_item_link is not None:
            payload["selected_v221_gem_item_relation_unadmitted"]=source_item_link
            payload["requires"].append(
                "SPECIAL_GEM_EXACT_ROLE_QUALITY_AND_REAL_SOCKET_COUNTS_PENDING")
        if raw_gem_ratings is not None:
            payload["physical_gem_raw_rating_by_id_unadmitted"] = (
                dict(raw_gem_ratings))
            payload["physical_gem_raw_rating_source_only"] = True
        payload["requires"].append(
            "REAL_SOCKET_COUNTS_AND_HIGHEST_QUALITY_GEM_SOURCE_PENDING")
        if gem_J is not None:
            payload["physical_gem_J_arithmetic_unadmitted"] = {
                **gem_J,
                "J_accounting_policy":"SUM_SELECTED_ORDINARY_GEM_RATINGS",
                "special_gem_count_in_J":0,
                "simc_effective_rating_is_budget_gate":False}
        else:
            payload["requires"].append(
                "PHYSICAL_GEM_ITEM_BY_ID_CHMV_RATING_SOURCE_PENDING")
    if v277_G_preview is not None:
        payload["v277_native_G_preprofile_unadmitted"] = v277_G_preview
    if proposed_budget is not None:
        payload["proposed_budget_arithmetic_unadmitted"] = proposed_budget
        # Carry the exact already-consumed v222 G component, including its
        # original source identity. This is a numeric source-only projection:
        # preprofile_budget does not authenticate the source itself.
        payload["v222_G_component_reference_unadmitted"] = dict(
            budget_evidence["components"]["G"])
        # Follow the already-verified original source receipts. Missing
        # applicability/rating facts are resolved per item, not by a second
        # global or independent source-certification engine.
        payload["requires"].append(
            "GJFO_EXISTING_SOURCE_RECEIPT_AND_SELECTED_ITEM_LINK_PENDING")
    if standard_table is not None:
        payload["standardized_ilevel_budget_rows_unadmitted"] = standard_table
    if native_G_filled_levels:
        payload["G_levels_filled_from_existing_v234_native"] = sorted(
            native_G_filled_levels)
    if existing_G_rows is not None:
        payload["measured_ilevel_G_from_existing_native_unadmitted"] = (
            [existing_G_rows[k] for k in sorted(existing_G_rows)])
    if simc_effect_snapshot_case is not None:
        payload["simc_native_effect_rating_delta_unadmitted"] = (
            _existing_simc_native_effect_snapshot(
                candidate=simc_effect_snapshot_case,
                simc_revision=expected_simc_revision))
    return {**payload,"preflight_sha256":
        digest(canonical(payload).encode("utf8"))}



def _join_authenticated_season_source(*,stage_root,output_dir,
                                      expected_game_build,discovered,
                                      wago_stage_receipt,
                                      verified_tables=None):
    if not discovered.get("season_join_ready"):
        return {"status":"AUTHENTICATED_SEASON_JOIN_NOT_READY",
                "candidate_path":None,"stage":None,
                "season_membership_verified":False}
    report_path=pathlib.Path(discovered["source_report_path"])
    report=json.loads(report_path.read_text(encoding="utf8"))
    try:
        scope=season_join.discover_unique_live_scope(output_dir,report)
    except season_join.JoinBlocked as exc:
        return {"status":"LIVE_SEASON_SCOPE_AMBIGUOUS_PENDING",
                "reason":str(exc).split(":",1)[0],
                "candidate_path":None,"stage":None,
                "season_membership_verified":False}
    rel="source/v163_unapproved_candidates_token_provenance.json"
    path=pathlib.Path(stage_root)/rel
    code=stage_engine.module_dependency_fingerprint(
        [pathlib.Path(season_join.__file__),
         pathlib.Path(stage_engine.__file__)])
    def execute():
        result=season_join.build_index(
            output_dir,report,raid_zone=scope["raid_zone"],
            mplus_zone=scope["mplus_zone"],
            build=expected_game_build,expansion_id=scope["expansion_id"],
            verified_tables=verified_tables)
        result["auto_source_scope"]=scope
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(result,sort_keys=True,indent=2,
                        ensure_ascii=False,allow_nan=False)+"\n",encoding="utf8")
    def validate(outputs):
        doc=json.loads(outputs["candidate"].read_text("utf8"))
        return (doc.get("schema")==season_join.SCHEMA
                and doc.get("build")==expected_game_build
                and doc.get("auto_source_scope")==scope
                and doc.get("db2_display_season_id")==scope["db2_display_season_id"]
                and doc.get("full_season_completeness_confirmed") is False
                and doc.get("old_item_catalog_imported") is False
                and doc.get("simc_native_calls")==0)
    try:
        stage=stage_engine.execute_stage(
            root=stage_root,stage_id="fresh-v163-token-provenance",
            stage_version="live-unique-scope-token-provenance-1",
            inputs={"game_build":expected_game_build,
                    "wago_receipt_sha256":wago_stage_receipt,
                    "v155_sha256":digest(report_path.read_bytes()),
                    "scope":scope,"code_sha256":code["sha256"]},
            outputs={"candidate":rel},execute=execute,validate=validate)
    except stage_engine.StageExecutionBlocked as exc:
        raise EnvironmentBuildBlocked(
            "V216_FRESH_V163_STAGE_BLOCKED:"+str(exc)) from exc
    return {"status":"DB2_WCL_CANDIDATES_JOINED_SEASON_CONDITIONS_PENDING",
            "candidate_path":str(path.resolve()),
            "stage":{k:v for k,v in stage.items() if k!="result"},
            "source_scope":scope,"season_membership_verified":False,
            "G":None,"J":None,"F":None,"O":None}



def _fresh_ordinary_gear_source_stage(*, stage_root, wago_folder, build,
                                     linked, transport=None):
    """Reuse v165->v166->v167 from the authenticated v163 seasonal source.

    One additional same-build Retail ItemXItemEffect relation distinguishes
    a direct effect-record candidate from a plain-gear candidate. This is a
    source classification, not SimC effect certification, season-wide gear
    completeness, target-ilvl G, or an installed representative profile.
    No Localbots / legacy J/F / old gear input is permitted on this path.
    """
    if not linked.get("candidate_path"):
        return {"status":"FRESH_GEAR_AUTHENTICATED_RAID_SOURCE_PENDING",
                "candidate_path":None,"network_calls_by_stage":0,
                "season_representative_verified":False}
    root=pathlib.Path(stage_root)
    source_path=pathlib.Path(linked["candidate_path"])
    sparse=pathlib.Path(wago_folder)/"ItemSparse.csv"
    item=pathlib.Path(wago_folder)/"Item.csv"
    need(source_path.is_file() and not source_path.is_symlink()
         and sparse.is_file() and not sparse.is_symlink()
         and item.is_file() and not item.is_symlink(),
         "V216_FRESH_GEAR_SOURCE_FILES_MISSING")
    raw_source=source_path.read_bytes()
    try:
        source=json.loads(raw_source)
    except ValueError as exc:
        raise EnvironmentBuildBlocked("V216_FRESH_GEAR_V163_JSON_INVALID") from exc
    need(source.get("schema")==season_join.SCHEMA
         and source.get("build")==build
         and source.get("source_provider")=="WAGO_TOOLS_PINNED_DB2_WCL_LIVE"
         and source.get("old_item_catalog_imported") is False,
         "V216_FRESH_GEAR_V163_SOURCE_MISMATCH")
    rel="source/v254_fresh_ordinary_gear_"
    paths={"effect":rel+"ItemXItemEffect.csv",
           "pool":rel+"v165_pool.json",
           "compact":rel+"v166_compact.json",
           "candidate":rel+"v167_candidates.json"}
    source_identity=stage_engine.module_dependency_fingerprint([
        pathlib.Path(source_gear_pool.__file__),
        pathlib.Path(compact_gear_db.__file__),
        pathlib.Path(product_gear_db.__file__),
        pathlib.Path(stage_engine.__file__)])
    attempted=[0]
    def execute():
        url="https://wago.tools/db2/ItemXItemEffect/csv?"+urlencode(
            {"build":build,"locale":"enUS"})
        req=Request(url,headers={
            "User-Agent":"SIMC-Secondary-Environment-Gear/1.0",
            "Accept":"text/csv"})
        attempted[0]+=1
        with (urlopen if transport is None else transport)(
                req,timeout=75) as response:
            need(response.status==200,"V216_FRESH_GEAR_HTTP_NON_200")
            parts=[]
            total=0
            while True:
                chunk=response.read(262144)
                if not chunk:
                    break
                total+=len(chunk)
                need(total<=12_000_000,"V216_FRESH_GEAR_HTTP_SIZE_LIMIT")
                parts.append(chunk)
        need(total>0,"V216_FRESH_GEAR_EMPTY_EFFECT_SOURCE")
        effect=root/paths["effect"]
        effect.parent.mkdir(parents=True,exist_ok=True)
        effect.write_bytes(b"".join(parts))
        # Explicit budget_source=None prevents any installed J/F reference.
        pool=source_gear_pool.compile_pool(
            source,None,sparse,effect,budget_source=None)
        compact=compact_gear_db.build(pool,item,sparse)
        candidate=product_gear_db.from_v166(compact)
        for name,payload in (("pool",pool),("compact",compact),
                             ("candidate",candidate)):
            target=root/paths[name]
            target.write_text(json.dumps(payload,ensure_ascii=False,
                sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf8")
    def validate(outputs):
        pool=json.loads(outputs["pool"].read_text(encoding="utf8"))
        compact=json.loads(outputs["compact"].read_text(encoding="utf8"))
        candidate=json.loads(outputs["candidate"].read_text(encoding="utf8"))
        return (pool.get("build")==build
                and pool.get("item_x_item_effect_csv_sha256")==
                    digest(outputs["effect"].read_bytes())
                and pool.get("supplementary_localbots_status")==
                    "OPTIONAL_SOURCE_NOT_COLLECTED"
                and pool.get("consumable_budget_reference") is None
                and pool.get("consumable_budget_source_mode")==
                    "NEW_SEASON_J_F_BUDGET_EVIDENCE_PENDING"
                and pool.get("G") is None and pool.get("B") is None
                and pool.get("T") is None
                and compact.get("season_build")==build
                and compact.get("no_old_catalog_seed") is True
                and candidate.get("season_build")==build
                and candidate.get("item_count")==compact.get(
                    "current_candidate_count")
                and product_gear_db.validate(candidate) is candidate)
    try:
        stage=stage_engine.execute_stage(
            root=root,stage_id="fresh-ordinary-gear-source-candidates",
            stage_version="v165-v167-wago-no-legacy-budget-v1",
            inputs={"game_build":build,
                    "v163_sha256":digest(raw_source),
                    "v163_stage_receipt":(linked.get("stage") or {}).get(
                        "receipt_sha256"),
                    "code_sha256":source_identity["sha256"]},
            outputs=paths,execute=execute,validate=validate)
    except (stage_engine.StageExecutionBlocked,
            source_gear_pool.CatalogBlocked,
            compact_gear_db.GearDbBlocked,
            product_gear_db.GearBlocked,
            EnvironmentBuildBlocked,OSError,ValueError) as exc:
        return {"status":"FRESH_GEAR_SOURCE_OR_JOIN_PENDING",
                "reason":str(exc).split(":",1)[0],
                "candidate_path":None,
                "network_calls_by_stage":attempted[0],
                "season_representative_verified":False}
    result=json.loads((root/paths["candidate"]).read_text(encoding="utf8"))
    plain=[r for r in result["items"]
           if r["category"]=="plain_representative_candidate"]
    internal=result.get("internal_conditional_mplus_plain_candidates",[])
    # An internal WSE condition candidate remains useful for constructing
    # a source-only representative, but cannot be installed/published.
    # A source containing only trinkets/special-effect items is not a usable
    # ordinary gear/weapon pool. Preserve its sealed evidence as PENDING.
    return {"status":("FRESH_GEAR_PLAIN_CANDIDATES_SOURCE_ONLY"
                      if plain or internal
                      else "FRESH_GEAR_PLAIN_CANDIDATES_NOT_FOUND_PENDING"),
            "candidate_path":str((root/paths["candidate"]).resolve()),
            "item_count":result["item_count"],
            "plain_candidate_count":len(plain),
            "internal_wse_conditional_plain_count":len(internal),
            "plain_armor_candidate_count":sum(x["class_id"]==4
                for x in plain+internal),
            "plain_weapon_candidate_count":sum(x["class_id"]==2
                for x in plain+internal),
            "network_calls_by_stage":attempted[0],
            "source_stage":{k:v for k,v in stage.items() if k!="result"},
            "season_representative_verified":False,
            "seasonal_G_verified":False,"native_calls":0}


def _db2_first_tier_stage(*,stage_root,wago_folder,build,linked,
                         wago_receipt_sha256,transport=None):
    """Same Build: ItemSet + ItemSetSpell + ChrSpecialization, NO title seed.

    The exact class/2pc/4pc/5-slot structure is a CANDIDATE. Season 1 and
    2 both qualify, so this stage NEVER selects a current-season roster.
    v168 remains the original physical 13x5 verifier after season proof.
    """
    # Tier structure is discoverable directly from the pinned DB2 snapshot,
    # independent of WCL/Blizzard auth and independent of season selection.
    # Missing live scope means ALL observed expansions are candidate-only.
    scope=linked.get("source_scope") or {}
    try:
        return tier_db.build_stage(
            stage_root=stage_root,wago_folder=wago_folder,build=build,
            expansion_id=scope.get("expansion_id"),
            wago_receipt_sha256=wago_receipt_sha256,
            transport=transport)
    except (tier_db.TierDBBlocked,tier_db.physical.TierBlocked) as exc:
        return {"status":"TIER_DB2_STRUCTURAL_CANDIDATES_PENDING",
                "reason":str(exc).split(":",1)[0],
                "candidate_path":None,
                "network_calls_by_stage":getattr(
                    exc,"network_calls_attempted",0),
                "network_attempts_recorded":True,
                "source_season_verified":False,
                "environment_installed":False}


def _raid_correlated_tier_stage(*,stage_root,build,linked,fresh_tier,
                                transport=None):
    """Optional corroboration after both source stages, NEVER a new Gate.

    No live authenticated raid scope or complete 13-class/5-item cohorts:
    skip extra DB2 requests rather than blocking standalone tier discovery.
    """
    if not linked.get("candidate_path") or not fresh_tier.get("candidate_path"):
        return {"status":"RAID_BONUS_SOURCE_SCOPE_PENDING",
                "network_calls_by_stage":0,"source_season_verified":False}
    tier_path=pathlib.Path(fresh_tier["candidate_path"])
    tier_doc=json.loads(tier_path.read_text("utf8"))
    if not any(x.get("exact_13_class_5piece_structural_roster") is True
               for x in tier_doc.get("observed_base_ilvl_roster_groups",[])):
        return {"status":"RAID_BONUS_FULL_13_CLASS_BASE_ILVL_ROSTER_PENDING",
                "network_calls_by_stage":0,"source_season_verified":False}
    try:
        return raid_bonus.build_stage(
            stage_root=stage_root,build=build,
            tier_candidate_path=tier_path,
            raid_candidate_path=linked["candidate_path"],
            tier_stage_receipt=fresh_tier["source_stage"]["receipt_sha256"],
            raid_stage_receipt=linked["stage"]["receipt_sha256"],
            transport=transport)
    except raid_bonus.BonusSourceBlocked as exc:
        return {"status":"RAID_BONUS_CORROBORATION_PENDING",
                "reason":str(exc).split(":",1)[0],
                "network_calls_by_stage":getattr(
                    exc,"network_calls_attempted",0),
                "source_season_verified":False}


def _physical_tier_to_simc_candidate(*,stage_root,fresh_tier,tier_bonus):
    """Source-only 13x5 piece bridge; no Native, option inference or Gate.

    If raid correlation is not unique, the Wago candidate discovery remains
    usable and this optional stage stays pending with zero extra HTTP.
    """
    if (tier_bonus.get("status")!=
          "UNIQUE_RAID_BONUS_CORRELATED_TIER_COHORT_SEASON_PENDING"
        or not fresh_tier.get("candidate_path")
        or not tier_bonus.get("candidate_path")):
        return {"status":"TIER_SIMC_BRIDGE_RAID_CORROBORATION_PENDING",
                "source_season_verified":False,
                "simc_source_verified":False,
                "network_calls_by_stage":0}
    try:
        return tier_simc_bridge.build_stage(
            stage_root=stage_root,
            db2_candidate_path=fresh_tier["candidate_path"],
            bonus_candidate_path=tier_bonus["candidate_path"],
            db2_receipt=fresh_tier["source_stage"]["receipt_sha256"],
            bonus_receipt=tier_bonus["source_stage"]["receipt_sha256"])
    except tier_simc_bridge.BridgeBlocked as exc:
        return {"status":"TIER_SIMC_PHYSICAL_CANDIDATE_PENDING",
                "reason":str(exc).split(":",1)[0],
                "source_season_verified":False,
                "simc_source_verified":False,
                "network_calls_by_stage":0}


def _collect_first_party_simc_seed_stage(*,stage_root,build,
                                          revision=None,
                                          previous_game_build=None,
                                          season_event="season_change",
                                          transport=None):
    """Use existing verified v229 source collector, not a parallel collector.

    Exact immutable SimC revision and previous build are internal runtime
    inputs, never filled from historical season guesses. Only the three
    SMALL generated source tables; defer item_data.inc to actual G work.
    """
    if revision is None:
        return {"status":"SIMC_PINNED_REVISION_NOT_AVAILABLE_PENDING",
                "source_dir":None,"network_calls_by_stage":0}
    need(type(revision) is str and
         simc_source.REV.fullmatch(revision) is not None and
         season_event in ("season_change","expansion_change","mid_patch",
                          "cold_start"),
         "V216_SIMC_FIRST_PARTY_REVISION_OR_EVENT_INVALID")
    rel="source/v229_pinned_generated"
    outputs={name:rel+"/"+name for name in
             (*simc_source.SOURCE_FILES,simc_source.RECEIPT)}
    directory=pathlib.Path(stage_root)/rel
    code=stage_engine.module_dependency_fingerprint(
        [pathlib.Path(simc_source.__file__),
         pathlib.Path(simc_source.generated_parser.__file__),
         pathlib.Path(stage_engine.__file__)])
    calls=[0]
    def fetch(req,timeout):
        calls[0]+=1
        return (simc_source.urlopen if transport is None else transport)(
            req,timeout=timeout)
    def execute():
        need(not directory.parent.is_symlink(),
             "V216_SIMC_GENERATED_PARENT_SYMLINK_BLOCKED")
        directory.parent.mkdir(parents=True,exist_ok=True)
        simc_source.collect(
            revision=revision,expected_build=build,
            previous_game_build=previous_game_build,
            season_event=season_event,include_item_data=False,
            dest=directory,transport=fetch)
    def validate(paths):
        doc=json.loads(paths[simc_source.RECEIPT].read_text("utf8"))
        return (doc.get("schema")==simc_source.SCHEMA
                and doc.get("simc_generated_build")==build
                and doc.get("simc_revision")==revision
                and doc.get("previous_game_build")==previous_game_build
                and doc.get("provenance_tree_blob_authenticated") is True
                and doc.get("item_data_present") is False
                and doc.get("environment_ready") is False
                and doc.get("native_calls")==0
                and set(doc.get("source_files",{}))==
                    set(simc_source.SOURCE_FILES)
                and all(doc["source_files"][name].get("sha256")==
                        simc_source.digest(paths[name].read_bytes())
                        for name in simc_source.SOURCE_FILES))
    try:
        stage=stage_engine.execute_stage(
            root=stage_root,stage_id="fresh-v229-pinned-simc-generated",
            stage_version="source-three-small-files-no-native-v1",
            inputs={"game_build":build,"revision":revision,
                    "previous_game_build":previous_game_build,
                    "season_event":season_event,
                    "include_item_data":False,
                    "code_sha256":code["sha256"]},
            outputs=outputs,execute=execute,validate=validate)
    except (stage_engine.StageExecutionBlocked,
            simc_source.SimCSourceBlocked,
            ValueError,OSError) as exc:
        return {"status":"SIMC_FIRST_PARTY_SOURCE_COLLECTION_PENDING",
                "reason":str(exc).split(":",1)[0],
                "source_dir":None,
                "network_calls_by_stage":calls[0]}
    doc=json.loads((directory/simc_source.RECEIPT).read_text("utf8"))
    return {"status":"SIMC_PINNED_SET_SOURCE_RECEIPT_READY",
            "source_dir":str(directory.resolve()),
            "simc_receipt_sha256":doc["receipt_sha256"],
            "source_stage":{k:v for k,v in stage.items() if k!="result"},
            "network_calls_by_stage":calls[0],
            "native_calls":0,"source_season_verified":False}



def _fresh_consumable_item_source_stage(*, stage_root, wago_folder,
                                        build, linked, pinned_simc,
                                        transport=None, verified_tables=None):
    """Reuse original v189 and v190 to join same-season consumable IDs.

    Exactly one small pinned SimC source fetch at the already resolved
    revision; zero duplicate Wago requests, Native or UI admission.
    The source ID set includes food, potions, subclass-3 flasks and broad
    subclass-6 item enhancements. The latter are NOT necessarily weapon oils;
    no flask token, quality/effect, physical hands or F/O is approved.
    """
    pending={"status":"FRESH_CONSUMABLE_SAME_BUILD_SOURCE_PENDING",
             "candidate_path":None,"source_stage":None,
             "network_calls_by_stage":0,"native_calls":0,
             "J":None,"F":None,"O":None,
             "highest_quality_verified":False,
             "environment_ready":False}
    scope=linked.get("source_scope") or {}
    expansion=scope.get("expansion_id")
    directory=pinned_simc.get("source_dir")
    if (not linked.get("candidate_path") or
            linked.get("status")!=
                "DB2_WCL_CANDIDATES_JOINED_SEASON_CONDITIONS_PENDING" or
            type(expansion) is not int or expansion<=0 or
            not directory):
        return pending
    seed_dir=pathlib.Path(directory)
    receipt_path=seed_dir/simc_source.RECEIPT
    need(seed_dir.is_dir() and not seed_dir.is_symlink()
         and receipt_path.is_file() and not receipt_path.is_symlink(),
         "V216_CONSUMABLE_PINNED_SIMC_RECEIPT_MISSING")
    receipt_raw=receipt_path.read_bytes()
    receipt=json.loads(receipt_raw)
    revision=receipt.get("simc_revision")
    need(receipt.get("schema")==simc_source.SCHEMA
         and receipt.get("simc_generated_build")==build
         and receipt.get("provenance_tree_blob_authenticated") is True
         and type(revision) is str
         and simc_source.REV.fullmatch(revision) is not None
         and receipt.get("receipt_sha256")==simc_source.digest(
             simc_source.canonical({k:v for k,v in receipt.items()
                 if k!="receipt_sha256"}).encode("utf8"))
         and pinned_simc.get("simc_receipt_sha256")==
             receipt["receipt_sha256"],
         "V216_CONSUMABLE_PINNED_SOURCE_IDENTITY_INVALID")
    db2root=pathlib.Path(wago_folder)
    wago_doc=json.loads((db2root/"receipt.json").read_text("utf8"))
    tables=wago_doc.get("tables",{})
    need(wago_doc.get("build")==build
         and all(type(tables.get(name)) is dict and
                 type(tables[name].get("sha256")) is str
                 and len(tables[name]["sha256"])==64
                 for name in ("Item","ItemSparse")),
         "V216_CONSUMABLE_WAGO_SOURCE_IDENTITY_INVALID")
    # v217 checked these bytes at collection/reuse; compare identities only.
    # A direct standalone call without this proof retains v190 SHA scans.
    if verified_tables is not None:
        need(type(verified_tables) is dict and
             set(verified_tables)==set(wago_snapshot.TABLES) and
             all(verified_tables[t]=={"sha256":tables[t]["sha256"],
                                      "bytes":tables[t]["bytes"]}
                 for t in wago_snapshot.TABLES),
             "V216_CONSUMABLE_V217_SOURCE_SEAL_MISMATCH")
    trusted_pair=({t:verified_tables[t] for t in ("Item","ItemSparse")}
                  if verified_tables is not None else None)
    scope_file=pathlib.Path(linked["candidate_path"])
    need(scope_file.is_file() and not scope_file.is_symlink(),
         "V216_CONSUMABLE_V163_ORIGIN_FILE_REQUIRED")
    scope_raw=scope_file.read_bytes()
    need(0<len(scope_raw)<=25_000_000,
         "V216_CONSUMABLE_V163_ORIGIN_SIZE_INVALID")
    scope_doc=json.loads(scope_raw)
    need(scope_doc.get("schema")==season_join.SCHEMA
         and scope_doc.get("build")==build
         and scope_doc.get("source_provider")==
             "WAGO_TOOLS_PINNED_DB2_WCL_LIVE"
         and scope_doc.get("auto_source_scope")==scope,
         "V216_CONSUMABLE_V163_SEASON_SCOPE_DRIFT")
    root=pathlib.Path(stage_root)
    # Successor source stage: preserve historical v258 sealed bytes; the
    # A real Wago-confirmed (0,8) Other consumable contains oils. Preserve
    # earlier v258/v279 receipts; successor v282 seals the corrected scope
    # without a new Item/Sparse download or additional SimC source HTTP.
    prefix="source/v282_same_season_consumable_"
    outputs={
        "simc_source":prefix+"unique_gear_midnight.cpp",
        "v189":prefix+"v189_handlers.json",
        "candidate":prefix+"v190_items.json"}
    files={k:root/v for k,v in outputs.items()}
    code=stage_engine.module_dependency_fingerprint([
        pathlib.Path(simc_effect_candidates.__file__),
        pathlib.Path(consumable_item_candidates.__file__),
        pathlib.Path(stage_engine.__file__)])
    calls=[0]
    def execute():
        def fetch(req,timeout):
            calls[0]+=1
            return (simc_effect_candidates.urlopen
                    if transport is None else transport)(req,timeout=timeout)
        raw=simc_effect_candidates.read_source(
            commit=revision,transport=fetch)
        first=simc_effect_candidates.discover(raw,revision)
        second=consumable_item_candidates.build(
            first,db2root,expected_build=build,expansion_id=expansion,
            verified_tables=trusted_pair)
        files["simc_source"].parent.mkdir(parents=True,exist_ok=True)
        files["simc_source"].write_bytes(raw)
        for key,document in (("v189",first),("candidate",second)):
            files[key].write_text(json.dumps(document,sort_keys=True,
                ensure_ascii=False,indent=2,allow_nan=False)+"\n",
                encoding="utf8")
    def validate(checked):
        first=json.loads(checked["v189"].read_text("utf8"))
        second=json.loads(checked["candidate"].read_text("utf8"))
        return (
            first.get("schema")==simc_effect_candidates.SCHEMA
            and first.get("source",{}).get("commit")==revision
            and first["source"].get("sha256")==
                digest(checked["simc_source"].read_bytes())
            and first["source"].get("bytes")==
                checked["simc_source"].stat().st_size
            and first.get("auto_promote_to_user_ui") is False
            and first.get("new_native_calls")==0
            and second.get("schema")==consumable_item_candidates.SCHEMA
            and second.get("source",{}).get("simc_revision")==revision
            and second["source"].get("simc_registration_sha256")==
                first["source"]["sha256"]
            and second["source"].get("wago_snapshot_build")==build
            and second["source"].get("expansion_id")==expansion
            and all(second["source"].get("tables",{}).get(t,{}).get(
                "sha256")==tables[t]["sha256"]
                for t in ("Item","ItemSparse"))
            and second.get("automatic_ui_promotion") is False
            and second.get("simc_native_calls")==0
            and second.get("counts",{}).get("food_items")==
                sum(x.get("kind")=="food" for x in second.get("items",[]))
            and second.get("counts",{}).get("potion_items")==
                sum(x.get("kind")=="potion" for x in second.get("items",[]))
            and second.get("counts",{}).get("flask_items")==
                sum(x.get("kind")=="flask" for x in second.get("items",[]))
            and second.get("counts",{}).get("item_enhancement_items")==
                sum(x.get("kind")=="item_enhancement"
                    for x in second.get("items",[]))
            and all(item.get("ui_selectable") is False and
                    item.get("simc_token")=="UNRESOLVED"
                    for item in second.get("items",[])))
    try:
        stage=stage_engine.execute_stage(
            root=root,stage_id="fresh-v189-v190-consumable-physical-other",
            stage_version="same-build-real-other-consumable-v3",
            inputs={"game_build":build,"expansion_id":expansion,
                    "simc_revision":revision,
                    "simc_seed_receipt_sha256":digest(receipt_raw),
                    "v163_stage_sha256":(linked.get("stage") or {}).get(
                        "receipt_sha256"),
                    "v163_candidate_sha256":digest(scope_raw),
                    "wago_item_sha256":tables["Item"]["sha256"],
                    "wago_sparse_sha256":tables["ItemSparse"]["sha256"],
                    "code_sha256":code["sha256"]},
            outputs=outputs,execute=execute,validate=validate)
    except (stage_engine.StageExecutionBlocked,
            simc_effect_candidates.DiscoveryBlocked,
            consumable_item_candidates.ConsumableJoinBlocked,
            ValueError,KeyError,TypeError,OSError) as exc:
        return {**pending,"status":"FRESH_CONSUMABLE_HANDLER_OR_DB2_JOIN_PENDING",
                "reason":str(exc).split(":",1)[0],
                "network_calls_by_stage":calls[0]}
    observed=json.loads(files["candidate"].read_text(encoding="utf8"))
    return {**pending,
        "status":"FRESH_FOOD_POTION_FLASK_ENHANCEMENT_DB2_CANDIDATES_NOT_USER_ADMITTED",
        "candidate_path":str(files["candidate"].resolve()),
        "simc_effect_source_receipt_path":str(files["v189"].resolve()),
        "food_item_count":observed["counts"]["food_items"],
        "potion_item_count":observed["counts"]["potion_items"],
        "flask_physical_item_count":observed["counts"]["flask_items"],
        "item_enhancement_candidate_count":
            observed["counts"]["item_enhancement_items"],
        "simc_handler_registrations":
            observed["counts"]["simc_effect_food_registrations"]+
            observed["counts"]["simc_effect_potion_registrations"],
        "network_calls_by_stage":calls[0],
        "source_stage":{k:v for k,v in stage.items() if k!="result"}}


def _verified_first_party_tier_options_stage(*,stage_root,tier_bridge,
                                             simc_seed_directory=None):
    """Use existing pinned v229 SimC bytes when available, never redownload.

    The stage authenticates and exact-matches SimC set option for 13 classes,
    not the actual target season and not full item_data/Native/G.
    """
    if not tier_bridge.get("candidate_path"):
        return {"status":"FIRST_PARTY_SIMC_TIER_PHYSICAL_CANDIDATE_PENDING",
                "network_calls_by_stage":0,"source_season_verified":False}
    if simc_seed_directory is None:
        return {"status":"FIRST_PARTY_SIMC_PINNED_SOURCE_PENDING",
                "network_calls_by_stage":0,"source_season_verified":False}
    try:
        return tier_simc_bridge.build_first_party_match_stage(
            stage_root=stage_root,
            physical_candidate_path=tier_bridge["candidate_path"],
            physical_stage_receipt=tier_bridge["source_stage"]["receipt_sha256"],
            seed_directory=simc_seed_directory)
    except (tier_simc_bridge.BridgeBlocked,
            tier_simc_bridge.simc_tier.TierCandidateBlocked,
            tier_simc_bridge.simc_tier.seed.SimCSourceBlocked) as exc:
        return {"status":"FIRST_PARTY_SIMC_EXACT_OPTION_PENDING",
                "reason":str(exc).split(":",1)[0],
                "network_calls_by_stage":0,"source_season_verified":False}





def _reuse_existing_tier_source_stage(*,build,tier_bridge,first_party,
                                      request=None):
    """Consume the v217-sealed v251 raid+SimC receipts once, no new Gate.

    A selected tier source is distinct from a fully authenticated season
    environment or a measured secondary rating budget G.
    """
    pending={"status":"TIER_EXISTING_SOURCE_REUSE_PENDING",
             "source_evidence_reused":False,
             "season_membership_verified":False,
             "environment_ready":False,
             "network_calls_by_stage":0,"native_calls":0}
    if (not tier_bridge.get("candidate_path")
            or not first_party.get("candidate_path")):
        return pending
    try:
        paths=[pathlib.Path(tier_bridge["candidate_path"]),
               pathlib.Path(first_party["candidate_path"])]
        need(all(p.is_file() and not p.is_symlink() for p in paths),
             "V216_TIER_REUSE_SEALED_PATH_UNSAFE")
        # Bind only the original v251 stage outputs; refuse a caller-chosen
        # alternate JSON path without rehashing or re-certifying the sources.
        need(paths[0].parent==paths[1].parent and
             paths[0].name=="v251_raid_correlated_tier_65_piece_candidate.json" and
             paths[1].name=="v251_exact_first_party_13_class_simc_options.json",
             "V216_TIER_REUSE_SEALED_STAGE_OUTPUT_PATH_DRIFT")
        need(all(type(s.get("source_stage")) is dict and
                 s["source_stage"].get("stage_id")==name and
                 type(s["source_stage"].get("receipt_sha256")) is str and
                 len(s["source_stage"]["receipt_sha256"])==64
                 for s,name in ((tier_bridge,"fresh-v251-db2-raid-tier-candidate"),
                                (first_party,"fresh-v251-exact-first-party-simc-options"))),
             "V216_TIER_REUSE_UPSTREAM_STAGE_RECEIPTS_REQUIRED")
        physical=json.loads(paths[0].read_text("utf8"))
        matched=json.loads(paths[1].read_text("utf8"))
        chosen=tier_evidence_reuse.reuse_existing_tier_source(
            physical_candidate=physical,exact_match=matched,
            cls=request["class"] if request is not None else None,
            spec=request["spec"] if request is not None else None)
        need(chosen["game_build"]==build,
             "V216_TIER_REUSE_GAME_BUILD_DRIFT")
    except (tier_simc_bridge.BridgeBlocked,
            EnvironmentBuildBlocked,ValueError,KeyError,TypeError,OSError) as exc:
        return {**pending,"reason":str(exc).split(":",1)[0]}
    return {**chosen,
            "source_stage_receipts":{
                "raid_correlated_physical":
                    tier_bridge["source_stage"]["receipt_sha256"],
                "simc_exact_13_class":
                    first_party["source_stage"]["receipt_sha256"]},
            "network_calls_by_stage":0}


def _resolve_one_spec_simc_commit_stage(*, stage_root, build, gear, tier,
                                       revision_hint=None, transport=None):
    """Pin a supplied SimC source revision independently of gear and tier.

    The exact Git commit is an input provenance, NOT game-build, current-
    season, binary, or representative-item certification. Downstream source
    and representative stages still enforce their original prerequisites.
    """
    waiting={"status":"SIMC_SOURCE_COMMIT_NOT_YET_RESOLVABLE_PENDING",
             "simc_revision":None,"network_calls_by_stage":0,
             "environment_ready":False,"binary_attested":False}
    if revision_hint is None:
        return waiting
    need(type(revision_hint) is str and
         re.fullmatch(r"[a-f0-9]{7,12}|[a-f0-9]{40}",
                      revision_hint) is not None,
         "V216_SOURCE_REVISION_HINT_INVALID")
    root=pathlib.Path(stage_root)
    # A changed installed/source revision is a new source identity, not
    # a conflicting replacement of the earlier sealed immutable receipt.
    out="source/v257_exact_simc_commit_"+revision_hint+".json"
    code=stage_engine.module_dependency_fingerprint([
        pathlib.Path(simc_source.__file__),
        pathlib.Path(stage_engine.__file__)])
    calls=[0]
    def lookup(req,timeout):
        calls[0]+=1
        return (simc_source.urlopen if transport is None else transport)(
            req,timeout=timeout)
    def execute():
        exact=simc_source.resolve_exact_commit(revision_hint,transport=lookup)
        payload={"schema":"v257_one_spec_exact_simc_git_commit_v1",
                 "source_repo":"simulationcraft/simc",
                 "game_build_requested":build,
                 "revision_hint":revision_hint,"resolved_revision":exact,
                 "immutable_git_source_only":True,
                 "binary_attested":False,"season_verified":False,
                 "G":None,"environment_ready":False}
        dest=root/out
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(payload,sort_keys=True,ensure_ascii=False,
                          indent=2)+"\n",encoding="utf8")
    def validate(paths):
        row=json.loads(paths["resolved"].read_text("utf8"))
        return (row.get("schema")=="v257_one_spec_exact_simc_git_commit_v1"
                and row.get("source_repo")=="simulationcraft/simc"
                and row.get("game_build_requested")==build
                and row.get("revision_hint")==revision_hint
                and type(row.get("resolved_revision")) is str
                and simc_source.REV.fullmatch(row["resolved_revision"]) is not None
                and row["resolved_revision"].startswith(revision_hint)
                and row.get("immutable_git_source_only") is True
                and row.get("binary_attested") is False
                and row.get("season_verified") is False
                and row.get("G") is None
                and row.get("environment_ready") is False)
    try:
        stage=stage_engine.execute_stage(
            root=root,stage_id="fresh-v257-exact-simc-commit-"+revision_hint,
            stage_version="source-only-revision-prefix-v1",
            inputs={"requested_build":build,"revision_hint":revision_hint,
                    "code_sha256":code["sha256"]},
            outputs={"resolved":out},execute=execute,validate=validate)
    except (simc_source.SimCSourceBlocked,
            stage_engine.StageExecutionBlocked,
            OSError,ValueError) as exc:
        return {**waiting,
                "status":"SIMC_SOURCE_COMMIT_RESOLUTION_PENDING",
                "reason":str(exc).split(":",1)[0],
                "network_calls_by_stage":calls[0]}
    row=json.loads((root/out).read_text("utf8"))
    return {"status":"SIMC_SOURCE_COMMIT_EXACT_PIN_CANDIDATE",
            "simc_revision":row["resolved_revision"],
            "source_stage":{k:v for k,v in stage.items() if k!="result"},
            "network_calls_by_stage":calls[0],"environment_ready":False,
            "binary_attested":False,"season_verified":False}


def _lazy_full_pinned_simc_item_stage(*, stage_root, build, small_seed_dir,
                                      gear_candidate, tier_bridge, request,
                                      transport=None):
    """Extend existing v229 source with ONE exact item_data download.

    v229 is the only Git tree/blob authority; no duplicate small downloads,
    no season inference, no Native. v217 seals a separate complete directory
    and the original three-file receipt is never mutated.
    """
    pending={"status":"FRESH_ONE_SPEC_FULL_PINNED_SIMC_ITEM_DATA_PENDING",
             "source_dir":None,"network_calls_by_stage":0,"native_calls":0,
             "environment_ready":False}
    if (request is None or small_seed_dir is None or
            not gear_candidate.get("candidate_path") or
            not tier_bridge.get("candidate_path")):
        return pending
    root=pathlib.Path(stage_root)
    source=pathlib.Path(small_seed_dir)
    need(source.is_dir() and not source.is_symlink(),
         "V216_FULL_SIMC_SMALL_SOURCE_DIRECTORY_REQUIRED")
    receipt_file=source/simc_source.RECEIPT
    need(receipt_file.is_file() and not receipt_file.is_symlink(),
         "V216_FULL_SIMC_SMALL_SOURCE_RECEIPT_REQUIRED")
    try:
        receipt=json.loads(receipt_file.read_text("utf8"))
    except (ValueError,UnicodeError) as exc:
        raise EnvironmentBuildBlocked("V216_FULL_SIMC_SMALL_RECEIPT_INVALID") from exc
    names=tuple(simc_source.SOURCE_FILES)
    need(receipt.get("schema")==simc_source.SCHEMA
         and receipt.get("simc_generated_build")==build
         and receipt.get("item_data_present") is False
         and receipt.get("provenance_tree_blob_authenticated") is True
         and set(receipt.get("source_files",{}))==set(names)
         and type(receipt.get("simc_revision")) is str
         and simc_source.REV.fullmatch(receipt["simc_revision"]) is not None,
         "V216_FULL_SIMC_SMALL_RECEIPT_PROVENANCE_INVALID")
    raws={}
    pinned={}
    for name in names:
        data=simc_source.bounded_read(source/name,simc_source.SOURCE_FILES[name])
        row=receipt["source_files"][name]
        need(row.get("sha256")==simc_source.digest(data)
             and row.get("git_blob_sha1")==simc_source.git_blob(data),
             "V216_FULL_SIMC_SMALL_SOURCE_CHANGED:"+name)
        raws[name]=data
        pinned[name]=row["git_blob_sha1"]
    baseline=simc_source.inventory(
        raws,simc_revision=receipt["simc_revision"],
        expected_build=build,previous_game_build=receipt["previous_game_build"],
        season_event=receipt["season_event"],expected_git_blob=pinned)
    need(baseline==receipt,
         "V216_FULL_SIMC_SMALL_RECEIPT_INCONSISTENT")
    revision=receipt["simc_revision"]
    rel="source/v256_full_pinned_simc"
    output={name:rel+"/"+name for name in
            (*names,simc_source.OPTIONAL_ITEM_FILE,simc_source.RECEIPT)}
    folder=root/rel
    need(not folder.is_symlink(),"V216_FULL_SIMC_OUTPUT_SYMLINK_BLOCKED")
    calls=[0]
    def fetch(req,timeout):
        calls[0]+=1
        return (simc_source.urlopen if transport is None else transport)(
            req,timeout=timeout)
    code=stage_engine.module_dependency_fingerprint([
        pathlib.Path(__file__),
        pathlib.Path(simc_source.__file__),
        pathlib.Path(simc_source.generated_parser.__file__),
        pathlib.Path(stage_engine.__file__)])
    def execute():
        # v229 walks the immutable Git tree. The previously verified 3 blobs
        # must still match, otherwise never fetch the large fourth file.
        tree=simc_source.discover_generated_tree(revision,transport=fetch)
        need(all(tree[name]["sha"]==pinned[name] and
                 tree[name]["size"]==len(raws[name]) for name in names),
             "V216_FULL_SIMC_PINNED_SMALL_TREE_DRIFT")
        item=simc_source.OPTIONAL_ITEM_FILE
        expected=tree[item]
        limit=simc_source.MAX_ITEM_FILE
        need(type(expected["size"]) is int and
             0<expected["size"]<=limit,
             "V216_FULL_SIMC_ITEM_DATA_TREE_SIZE_INVALID")
        data=simc_source.fetch_generated_blob(
            revision=revision,name=item,expected_sha=expected["sha"],
            expected_size=expected["size"],transport=fetch,timeout=90)
        need(len(data)==expected["size"] and len(data)<=limit and
             simc_source.git_blob(data)==expected["sha"],
             "V216_FULL_SIMC_ITEM_DATA_GIT_BLOB_MISMATCH")
        merged={**raws,item:data}
        proof=simc_source.inventory(
            merged,simc_revision=revision,expected_build=build,
            previous_game_build=receipt["previous_game_build"],
            season_event=receipt["season_event"],
            expected_git_blob={**pinned,item:expected["sha"]})
        need(proof["item_data_present"] is True and
             proof["environment_ready"] is False and proof["G"] is None,
             "V216_FULL_SIMC_SOURCE_NOT_PROVISIONAL")
        folder.mkdir(parents=True,exist_ok=True)
        for name,raw in merged.items():
            (folder/name).write_bytes(raw)
        (folder/simc_source.RECEIPT).write_text(
            json.dumps(proof,sort_keys=True,ensure_ascii=False,
                       indent=2,allow_nan=False)+"\n",encoding="utf8")
    def validate(paths):
        try:
            document=json.loads(paths[simc_source.RECEIPT].read_text("utf8"))
        except (ValueError,UnicodeError):
            return False
        return (document.get("schema")==simc_source.SCHEMA and
                document.get("simc_revision")==revision and
                document.get("simc_generated_build")==build and
                document.get("item_data_present") is True and
                document.get("provenance_tree_blob_authenticated") is True and
                document.get("environment_ready") is False and
                document.get("G") is None and
                document.get("native_calls")==0 and
                set(document.get("source_files",{}))==
                     set((*names,simc_source.OPTIONAL_ITEM_FILE)) and
                all(document["source_files"][name].get("sha256")==
                    simc_source.digest(paths[name].read_bytes())
                    for name in (*names,simc_source.OPTIONAL_ITEM_FILE)))
    try:
        stage=stage_engine.execute_stage(
            root=root,stage_id="fresh-v229-full-item-data-for-one-spec",
            stage_version="v229-reuse-three-download-one-v1",
            inputs={"build":build,"revision":revision,
                    "small_seed_receipt_sha256":digest(
                        receipt_file.read_bytes()),
                    "item_data_required_for_one_spec":True,
                    "code_sha256":code["sha256"]},
            outputs=output,execute=execute,validate=validate)
    except (simc_source.SimCSourceBlocked,
            stage_engine.StageExecutionBlocked,
            EnvironmentBuildBlocked,ValueError,OSError) as exc:
        return {**pending,"status":"FRESH_FULL_PINNED_SIMC_SOURCE_PENDING",
                "reason":str(exc).split(":",1)[0],
                "network_calls_by_stage":calls[0]}
    full=json.loads((folder/simc_source.RECEIPT).read_text("utf8"))
    return {"status":"FRESH_FULL_PINNED_SIMC_ITEM_DATA_SOURCE_ONLY",
            "source_dir":str(folder.resolve()),
            "receipt_sha256":full["receipt_sha256"],
            "source_stage":{k:v for k,v in stage.items() if k!="result"},
            "network_calls_by_stage":calls[0],"native_calls":0,
            "environment_ready":False,"G":None}


def _one_spec_ordinary_simc_stage(*, stage_root, build, fresh_gear,
                                  tier_bridge, seed_directory=None,
                                  request=None):
    """Reuse v251 + v232 for ONE requested DPS; only source candidates.

    Never fetch item_data.inc implicitly or substitute the small v229 seed.
    Real Native static G remains necessary for a numeric G reference.
    Acquisition-season membership is separate from generic G eligibility;
    actual product-profile/option installation stays with the normal Build.
    """
    if request is None:
        return {"status":"FRESH_ONE_SPEC_REPRESENTATIVE_NOT_REQUESTED",
                "network_calls_by_stage":0,"native_calls":0,
                "environment_ready":False}
    need(type(request) is dict and set(request)=={
        "class","spec","target_ilevel"} and
        type(request["class"]) is str and
        type(request["spec"]) is str and
        type(request["target_ilevel"]) is int and
        1<=request["target_ilevel"]<=1000 and
        simc_representative.chooser.contracts.lookup(
            request["class"],request["spec"]) is not None,
        "V216_ONE_SPEC_26_DPS_REQUEST_REQUIRED")
    if not (fresh_gear.get("candidate_path") and
            tier_bridge.get("candidate_path")):
        return {"status":"FRESH_ONE_SPEC_GEAR_OR_TIER_SOURCE_PENDING",
                "network_calls_by_stage":0,"native_calls":0,
                "environment_ready":False}
    if seed_directory is None:
        return {"status":"FRESH_ONE_SPEC_FULL_PINNED_SIMC_ITEM_DATA_PENDING",
                "network_calls_by_stage":0,"native_calls":0,
                "environment_ready":False}
    root=pathlib.Path(stage_root)
    seed_dir=pathlib.Path(seed_directory)
    item_data=seed_dir/"item_data.inc"
    if not item_data.is_file() or item_data.is_symlink():
        return {"status":"FRESH_ONE_SPEC_FULL_PINNED_SIMC_ITEM_DATA_PENDING",
                "network_calls_by_stage":0,"native_calls":0,
                "environment_ready":False}
    gear_path=pathlib.Path(fresh_gear["candidate_path"])
    tier_path=pathlib.Path(tier_bridge["candidate_path"])
    need(gear_path.is_file() and not gear_path.is_symlink() and
         tier_path.is_file() and not tier_path.is_symlink() and
         not seed_dir.is_symlink(),
         "V216_ONE_SPEC_SOURCE_PATH_MISSING_OR_UNSAFE")
    gear_bytes=gear_path.read_bytes()
    tier_bytes=tier_path.read_bytes()
    gear=json.loads(gear_bytes)
    tier=json.loads(tier_bytes)
    need(gear.get("schema")==product_gear_db.SCHEMA and
         gear.get("season_build")==build and
         gear.get("no_old_catalog_seed") is True and
         tier.get("schema")==tier_simc_bridge.SCHEMA and
         tier.get("game_build")==build and
         tier.get("season_membership_verified") is False and
         tier.get("environment_ready") is False,
         "V216_ONE_SPEC_SOURCE_BUILD_OR_PROVENANCE_MISMATCH")
    # The SHA is a stage identity, not proof of the file's Git provenance.
    # v251/v231/v229 recheck the immutable Git tree/blob inside execute().
    receipt_path=seed_dir/simc_source.RECEIPT
    need(receipt_path.is_file() and not receipt_path.is_symlink(),
         "V216_ONE_SPEC_SIMC_RECEIPT_REQUIRED")
    source_receipt_bytes=receipt_path.read_bytes()
    item_digest=hashlib.sha256()
    with item_data.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):
            item_digest.update(chunk)
    item_sha=item_digest.hexdigest()
    # One physical gear source can serve 26 specs and many target ilvls.
    # Key only the requested physical source shape, NOT race/talents or
    # historical session identity, so the costly pinned SimC source is reused.
    one_spec_key=digest(canonical({"game_build":build,
        "request":request}).encode("utf8"))[:16]
    # New physical-budget semantics must not overwrite earlier v255 sealed
    # receipts or force re-downloading build-wide Wago/SimC source bytes.
    output="source/v265_one_spec_generic_G_representative_"+one_spec_key+".json"
    path=root/output
    # Include transitive source parser/chooser and the adapter itself.
    # An implementation change must not silently reuse an old candidate.
    code=stage_engine.module_dependency_fingerprint([
        pathlib.Path(__file__),
        pathlib.Path(tier_simc_bridge.__file__),
        pathlib.Path(tier_simc_bridge.simc_tier.__file__),
        pathlib.Path(simc_source.__file__),
        pathlib.Path(simc_representative.__file__),
        pathlib.Path(simc_representative.metadata.__file__),
        pathlib.Path(simc_representative.chooser.__file__),
        pathlib.Path(product_gear_db.__file__),
        pathlib.Path(stage_engine.__file__)])
    def execute():
        source_tier=tier_simc_bridge.select_for_simc(
            candidate=tier,seed_directory=seed_dir,
            cls=request["class"],spec=request["spec"])
        result=simc_representative.find_candidate(
            seed_directory=seed_dir,
            tier_candidate=source_tier["v231_candidate"],
            target_ilevel=request["target_ilevel"],
            season_gear_db=gear)
        need(result["game_build"]==build and
             result["G"] is None and
             result["environment_ready"] is False,
             "V216_ONE_SPEC_SOURCE_NOT_PROVISIONAL")
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(result,ensure_ascii=False,
            sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf8")
    def validate(outputs):
        row=json.loads(outputs["candidate"].read_text(encoding="utf8"))
        return (row.get("schema")==simc_representative.SCHEMA and
                row.get("status")==
                    "SIMC_SOURCE_PHYSICAL_CANDIDATE_NOT_ACTUAL_SEASON_PROOF"
                and row.get("game_build")==build and
                row.get("character",{}).get("class")==request["class"] and
                row.get("character",{}).get("spec")==request["spec"] and
                row.get("target_ilevel")==request["target_ilevel"] and
                row.get("season_candidate_provider")==
                    "EXPLICIT_SAME_BUILD_WAGO_DB2_V167_CANDIDATES" and
                row.get("season_gear_db_digest_sha256")==
                    simc_source.digest(simc_source.canonical(gear).encode("utf8"))
                and row.get("same_season_membership_not_proven") is True
                and row.get("tier_active_season_membership_not_authenticated") is True
                and row.get("selected_G_source_candidate_not_approved") is True
                and row.get("generic_G_physical_conditions_verified") is True
                and row.get("generic_G_current_season_membership_required") is False
                and type(row.get("selected_non_tier_season_condition_pending_slots"))
                    is list
                and type(row.get(
                    "selected_intrinsic_socket_count_by_slot_source_only")) is dict
                and set(row["selected_intrinsic_socket_count_by_slot_source_only"])==
                    set(row.get("selected_G_slot_ids",{}))
                and all(type(count) is int and 0<=count<=3 for count in
                    row["selected_intrinsic_socket_count_by_slot_source_only"].values())
                and row.get("selected_intrinsic_socket_total_source_only")==sum(
                    row["selected_intrinsic_socket_count_by_slot_source_only"].values())
                and row.get("added_socket_bonus_and_game_permission_not_proven") is True
                and row.get("native_physical_and_static_G_still_required") is True and
                row.get("G") is None and row.get("B") is None
                and row.get("T") is None and
                row.get("native_calls")==0 and
                row.get("environment_ready") is False and
                row.get("receipt_sha256")==simc_source.digest(
                    simc_source.canonical({
                        k:v for k,v in row.items()
                        if k!="receipt_sha256"}).encode("utf8")))
    try:
        staged=stage_engine.execute_stage(
            root=root,
            stage_id="fresh-one-spec-generic-G-representative-"+one_spec_key,
            stage_version="v251-v232-generic-G-physical-v1",
            inputs={"game_build":build,"request":request,
                    "gear_sha256":digest(gear_bytes),
                    "tier_sha256":digest(tier_bytes),
                    "seed_receipt_sha256":digest(source_receipt_bytes),
                    "simc_item_data_sha256":item_sha,
                    "code_sha256":code["sha256"]},
            outputs={"candidate":output},execute=execute,validate=validate)
    except (stage_engine.StageExecutionBlocked,
            tier_simc_bridge.BridgeBlocked,
            simc_representative.SourceRepresentativeBlocked,
            EnvironmentBuildBlocked,ValueError,KeyError,OSError) as exc:
        reason,_,detail=str(exc).partition(":")
        slot_detail, _, coverage_json = detail.partition("|")
        coverage=None
        if coverage_json and reason=="V232_COMMON_SLOT_WITHOUT_SIMC_CANDIDATE":
            try:
                observed=json.loads(coverage_json)
                fields={"db2_plain_neck_count","simc_exact_id_seen",
                    "simc_inventory_mismatch",
                    "simc_class_or_subclass_rejected",
                    "simc_class_mask_rejected","simc_item_set_rejected",
                    "simc_plain_neck_accepted","upstream_neck_total",
                    "upstream_plain_conditional"}
                ring_fields={"db2_plain_ring_count","simc_exact_id_seen",
                    "simc_class_mask_rejected","simc_item_set_rejected",
                    "simc_plain_ring_accepted","selected_ring_count",
                    "upstream_ring_total","upstream_plain_conditional"}
                if (type(observed) is dict and
                    set(observed) in (fields,ring_fields) and
                    all(type(v) is int and 0<=v<=100000 for v in observed.values())):
                    coverage=observed
            except (ValueError,TypeError):
                pass
        # Preserve actionable missing slot without exposing source paths,
        # copying gear from old seasons, or granting a G success.
        slot=(slot_detail if reason in (
            "V232_ORDINARY_SLOT_WITHOUT_SIMC_CANDIDATE",
            "V232_COMMON_SLOT_WITHOUT_SIMC_CANDIDATE")
            and slot_detail in simc_representative.chooser.contracts.SLOT_ORDER
            else None)
        return {"status":"FRESH_ONE_SPEC_PHYSICAL_SOURCE_OR_COVERAGE_PENDING",
                "reason":reason,"missing_slot":slot,
                "neck_candidate_source_coverage":(
                    coverage if slot=="neck" else None),
                "ring_candidate_source_coverage":(
                    coverage if slot in ("finger1","finger2") else None),
                "network_calls_by_stage":0,"native_calls":0,
                "environment_ready":False}
    # v217 checked this source-only file's hash even on receipt reuse.
    # Present just the selected source provenance, NOT a verified G or
    # newly authenticated season-membership verdict.
    observed=json.loads(path.read_text(encoding="utf8"))
    return {"status":"FRESH_ONE_SPEC_SIMC_G_SOURCE_CANDIDATE_PENDING_NATIVE",
            "candidate_path":str(path.resolve()),
            "source_stage":{k:v for k,v in staged.items() if k!="result"},
            "selected_slot_count":len(observed["selected_G_slot_ids"]),
            "intrinsic_socket_counts_by_selected_slot_source_only":
                dict(observed["selected_intrinsic_socket_count_by_slot_source_only"]),
            "intrinsic_socket_total_source_only":
                observed["selected_intrinsic_socket_total_source_only"],
            "added_socket_bonus_and_game_permission_not_proven":True,
            "source_kinds_by_selected_slot":
                observed["selected_gear_season_source_kinds"],
            "selected_non_tier_source_provenance":
                observed["selected_ordinary_source_provenance"],
            "pending_non_tier_season_source_slots":
                observed["selected_non_tier_season_condition_pending_slots"],
            "explicit_db2_season_matched_non_tier_count":
                observed["selected_non_tier_explicit_db2_match_count"],
            "tier_active_season_membership_not_authenticated":True,
            "G_source_approved":False,
            "generic_G_physical_conditions_verified":
                observed["generic_G_physical_conditions_verified"],
            "generic_G_current_season_membership_required":False,
            "mplus_world_state_pending":(
                observed.get("season_gear_db_mplus_worldstate_pending")
                if "mplus_season_candidate_inclusion" in gear else None),
            "network_calls_by_stage":0,"native_calls":0,
            "season_membership_verified":False,"G":None,
            "environment_ready":False}



def _one_spec_source_G_probe_stage(*, stage_root, build, one_spec,
                                   fresh_gear, tier_bridge,
                                   seed_directory=None, character=None):
    """Same original source Build -> v233 profile, only when asked.

    This is a physical G *measurement input* (not G or an approved
    production user profile). v233 itself rebuilds the v232 candidate
    from exact pinned sources. Seal the small input+receipt with v217;
    never call Native or duplicate the Wago/SimC source downloader.
    """
    if character is None:
        return {"status":"FRESH_G_PROBE_CHARACTER_NOT_REQUESTED",
                "network_calls_by_stage":0,"native_calls":0,
                "G":None,"environment_ready":False}
    if (not one_spec.get("candidate_path") or
            not fresh_gear.get("candidate_path") or
            not tier_bridge.get("candidate_path") or
            seed_directory is None):
        return {"status":"FRESH_G_PROBE_REPRESENTATIVE_SOURCE_PENDING",
                "network_calls_by_stage":0,"native_calls":0,
                "G":None,"environment_ready":False}
    root=pathlib.Path(stage_root)
    seed_dir=pathlib.Path(seed_directory)
    paths=[pathlib.Path(one_spec["candidate_path"]),
           pathlib.Path(fresh_gear["candidate_path"]),
           pathlib.Path(tier_bridge["candidate_path"]),
           seed_dir/simc_source.RECEIPT]
    need(all(p.is_file() and not p.is_symlink() for p in paths)
         and seed_dir.is_dir() and not seed_dir.is_symlink(),
         "V216_G_PROBE_SOURCE_PATH_MISSING_OR_UNSAFE")
    rep_raw,gear_raw,tier_raw,receipt_raw=[p.read_bytes() for p in paths]
    rep=json.loads(rep_raw)
    gear=json.loads(gear_raw)
    tier=json.loads(tier_raw)
    need(rep.get("schema")==simc_representative.SCHEMA
         and rep.get("game_build")==build
         and rep.get("G") is None
         and rep.get("environment_ready") is False
         and rep.get("receipt_sha256")==simc_source.digest(
             simc_source.canonical({k:v for k,v in rep.items()
                 if k!="receipt_sha256"}).encode("utf8"))
         and gear.get("schema")==product_gear_db.SCHEMA
         and gear.get("season_build")==build
         and tier.get("schema")==tier_simc_bridge.SCHEMA
         and tier.get("game_build")==build,
         "V216_G_PROBE_SOURCE_IDENTITY_INVALID")
    # A different character reuses the same v232 source IDs, while its
    # character-specific profile is independently sealed and never overwrites
    # the previous user's measurement input.
    probe_key=digest(canonical({
        "source_candidate_receipt":rep["receipt_sha256"],
        "game_build":build,"character":character}).encode("utf8"))[:16]
    outputs={"input":"source/v257_one_spec_G_probe_"+probe_key+".simc",
             "receipt":"source/v257_one_spec_G_probe_receipt_"+
                       probe_key+".json"}
    profile_path=root/outputs["input"]
    receipt_path=root/outputs["receipt"]
    code=stage_engine.module_dependency_fingerprint([
        pathlib.Path(__file__),
        pathlib.Path(g_probe_profile.__file__),
        pathlib.Path(simc_representative.__file__),
        pathlib.Path(tier_simc_bridge.__file__),
        pathlib.Path(stage_engine.__file__)])
    def execute():
        physical=tier_simc_bridge.select_for_simc(
            candidate=tier,seed_directory=seed_dir,
            cls=rep["character"]["class"],
            spec=rep["character"]["spec"])
        profile,proof=g_probe_profile.build(
            source_directory=seed_dir,
            tier_candidate=physical["v231_candidate"],
            representative_candidate=rep,
            race=character["race"],level=character.get("level"),
            talents=character.get("talents"),season_gear_db=gear)
        profile_path.parent.mkdir(parents=True,exist_ok=True)
        profile_path.write_bytes(profile.encode("utf8"))
        receipt_path.write_text(json.dumps(
            proof,sort_keys=True,ensure_ascii=False,indent=2,
            allow_nan=False)+"\n",encoding="utf8")
    def validate(out):
        observed=json.loads(out["receipt"].read_text(encoding="utf8"))
        return (
            observed.get("schema")==g_probe_profile.SCHEMA
            and observed.get("status")==
                "EXACT_SIMC_SOURCE_PROFILE_PREPARED_NOT_EXECUTED"
            and observed.get("source_candidate_receipt_sha256")==
                rep["receipt_sha256"]
            and observed.get("game_build_declared_by_simc_source")==build
            and observed.get("class")==rep["character"]["class"]
            and observed.get("spec")==rep["character"]["spec"]
            and observed.get("race")==character["race"]
            and observed.get("level")==character.get("level")
            and observed.get("level_mode")==(
                "SIMC_COMPILED_MAX_LEVEL" if character.get("level") is None
                else "EXPLICIT_INTERNAL_OVERRIDE")
            and observed.get("target_ilevel")==rep["target_ilevel"]
            and observed.get("selected_G_slot_ids")==
                rep["selected_G_slot_ids"]
            and observed.get("current_season_membership_certified") is False
            and observed.get("generic_G_physical_conditions_verified")==
                rep.get("generic_G_physical_conditions_verified",False)
            and observed.get("generic_G_current_season_membership_required")
                is False
            and observed.get("G") is None
            and observed.get("environment_ready") is False
            and observed.get("native_calls")==0
            and observed.get("physical_profile_sha256")==
                digest(out["input"].read_bytes())
            and observed.get("receipt_sha256")==simc_source.digest(
                simc_source.canonical({k:v for k,v in observed.items()
                    if k!="receipt_sha256"}).encode("utf8")))
    try:
        stage=stage_engine.execute_stage(
            root=root,stage_id="fresh-one-spec-physical-G-probe-"+probe_key,
            stage_version="v232-v233-source-profile-v3",
            inputs={"game_build":build,
                    "candidate_sha256":digest(rep_raw),
                    "gear_sha256":digest(gear_raw),
                    "tier_sha256":digest(tier_raw),
                    "simc_seed_receipt_sha256":digest(receipt_raw),
                    "source_stage_sha256":one_spec.get(
                        "source_stage",{}).get("receipt_sha256"),
                    "character":character,
                    "level_policy":"SIMC_COMPILED_DEFAULT_MAX_LEVEL",
                    "code_sha256":code["sha256"]},
            outputs=outputs,execute=execute,validate=validate)
    except (stage_engine.StageExecutionBlocked,
            tier_simc_bridge.BridgeBlocked,
            simc_representative.SourceRepresentativeBlocked,
            g_probe_profile.ProbeBlocked,ValueError,KeyError,
            TypeError,OSError) as exc:
        # A source-only proposal can fail without blocking a verified core
        # season environment or making up an exact G.
        return {"status":"FRESH_G_PROBE_SOURCE_OR_CHARACTER_PENDING",
                "reason":str(exc).split(":",1)[0],
                "network_calls_by_stage":0,"native_calls":0,
                "G":None,"environment_ready":False}
    proof=json.loads(receipt_path.read_text(encoding="utf8"))
    return {"status":"FRESH_ONE_SPEC_PHYSICAL_G_PROFILE_PREPARED_NATIVE_PENDING",
            "profile_path":str(profile_path.resolve()),
            "profile_receipt_path":str(receipt_path.resolve()),
            "physical_profile_sha256":proof["physical_profile_sha256"],
            "source_stage":{k:v for k,v in stage.items() if k!="result"},
            "level_mode":proof["level_mode"],
            "native_calls":0,"network_calls_by_stage":0,
            "generic_G_physical_conditions_verified":
                proof["generic_G_physical_conditions_verified"],
            "generic_G_current_season_membership_required":False,
            "G":None,"environment_ready":False,
            "season_membership_verified":False}


def _simc_source_collection_context(*, requested_event, previous_game_build):
    """Keep the actual game event separate from local acquisition history.

    'cold_start' is a v229 source collection compatibility mode, NOT an
    expansion or proof that the game lacks a previous build. No history
    must not force discovery of a former build or old season statistics.
    """
    need(requested_event in ("season_change","expansion_change","mid_patch"),
         "V216_GAME_EVENT_INVALID")
    need(previous_game_build is None or (
        type(previous_game_build) is str and
        simc_source.BUILD.fullmatch(previous_game_build) is not None),
        "V216_PREVIOUS_GAME_BUILD_RECORD_INVALID")
    unknown=previous_game_build is None
    source_mode=("cold_start" if unknown and requested_event in (
        "season_change","expansion_change") else requested_event)
    return {"requested_game_event":requested_event,
            "source_collection_mode":source_mode,
            "previous_build_record_status":("NOT_RECORDED" if unknown
                                            else "RECORDED"),
            "previous_game_build":previous_game_build,
            "previous_game_build_is_not_a_season_proof":True}


def collect_wago_new_season_source(*, sessions_root, expected_game_build,
                                   fetch=None, credentials=None,
                                   discovery_transport=None,
                                   tier_transport=None,
                                   bonus_transport=None,
                                   gear_transport=None,
                                   item_effect_transport=None,
                                   spell_effect_transport=None,
                                   spell_equipped_transport=None,
                                   simc_seed_directory=None,
                                   simc_revision=None,
                                   previous_game_build=None,
                                   simc_season_event="season_change",
                                   simc_transport=None,
                                   representative_request=None,
                                   simc_revision_hint=None,
                                   g_probe_character=None,
                                   gem_enchant_transport=None,
                                   simc_compiler_transport=None,
                                   auto_four_stat_gems=False):
    """First real normal-source acquisition inside the SAME Environment Build.

    Explicit build is only a request identity, not independent season or tier
    proof. Use original v161 Wago collector and v217 receipt stage. Neither
    existing season references, sessions nor optimizer caches are inputs.
    Missing other independent sources must not be marked READY or installed.
    """
    need(type(expected_game_build) is str and
         re.fullmatch(r"[0-9]+(?:\.[0-9]+){3}",
                      expected_game_build) is not None,
         "V216_EXPLICIT_NEW_SEASON_BUILD_REQUIRED")
    # Validate a requested specialization before collecting expensive DB2.
    if representative_request is not None:
        need(type(representative_request) is dict and
             set(representative_request)=={"class","spec","target_ilevel"} and
             type(representative_request["class"]) is str and
             type(representative_request["spec"]) is str and
             type(representative_request["target_ilevel"]) is int and
             1<=representative_request["target_ilevel"]<=1000 and
             simc_representative.chooser.contracts.lookup(
                representative_request["class"],
                representative_request["spec"]) is not None,
             "V216_ONE_SPEC_26_DPS_REQUEST_REQUIRED")
    if g_probe_character is not None:
        need(representative_request is not None and
             type(g_probe_character) is dict and
             set(g_probe_character) in (
                 {"race"},{"race","talents"},
                 {"race","level"},{"race","level","talents"}) and
             type(g_probe_character.get("race")) is str and
             g_probe_profile.RACE.fullmatch(g_probe_character["race"])
                 is not None and
             ("level" not in g_probe_character or
              type(g_probe_character["level"]) is int and
              1<=g_probe_character["level"]<=100) and
             (g_probe_character.get("talents") is None or
              type(g_probe_character["talents"]) is str and
              g_probe_profile.TALENTS.fullmatch(
                  g_probe_character["talents"]) is not None),
             "V216_G_PROBE_CHARACTER_CONTEXT_INVALID")
        allowed=simc_representative.chooser.contracts.lookup(
            representative_request["class"],representative_request["spec"]
        )["allowed_races"]
        need(allowed is None or g_probe_character["race"] in allowed,
             "V216_G_PROBE_RACE_NOT_ALLOWED")
    need(not (simc_revision is not None and
              simc_revision_hint is not None),
         "V216_DUPLICATE_SIMC_REVISION_SOURCES")
    if simc_revision_hint is not None:
        need(type(simc_revision_hint) is str and
             re.fullmatch(r"[a-f0-9]{7,12}|[a-f0-9]{40}",
                          simc_revision_hint) is not None,
             "V216_SOURCE_REVISION_HINT_INVALID")
    supplied=pathlib.Path(sessions_root).expanduser()
    need(not supplied.is_symlink(),
         "V216_SEASON_SOURCE_SESSION_ROOT_SYMLINK_BLOCKED")
    root=supplied.resolve()
    root.mkdir(parents=True,exist_ok=True)
    workspace=root/"_fresh_season_sources"
    need(not workspace.is_symlink(),
         "V216_FRESH_SOURCE_WORKSPACE_SYMLINK_BLOCKED")
    workspace.mkdir(exist_ok=True)
    stage_root=workspace/("wago_"+expected_game_build)
    need(not stage_root.is_symlink(),
         "V216_FRESH_SOURCE_BUILD_SYMLINK_BLOCKED")
    stage_root.mkdir(exist_ok=True)
    # Authenticated Blizzard/WCL discovery is attempted BEFORE the large
    # Wago snapshot whenever both credential pairs are configured.
    # Missing credentials do not imply an empty season or block raw Wago.
    if credentials is None:
        credentials={k:os.environ.get(k,"") for k in discovery_stage.FIELDS}
    try:
        discovered=discovery_stage.collect(
            stage_root=stage_root,expected_game_build=expected_game_build,
            credentials=credentials,transport=discovery_transport)
    except discovery_stage.DiscoveryBlocked as exc:
        raise EnvironmentBuildBlocked(str(exc).split(":",1)[0]) from exc
    except TimeoutError as exc:
        # Retain the first failed source owner without leaking credentials.
        # Existing v155/v217 receipts and data remain untouched.
        raise EnvironmentBuildBlocked(
            "V216_AUTHENTICATED_SEASON_DISCOVERY_TIMEOUT") from exc
    output_dir=stage_root/"wago"
    need(not output_dir.is_symlink(),
         "V216_FRESH_SOURCE_OUTPUT_SYMLINK_BLOCKED")
    outputs={"receipt":"wago/receipt.json"}
    outputs.update({t:"wago/"+t+".csv" for t in wago_snapshot.TABLES})
    # Fetch identity depends on collector and stage implementation only.
    # A v216 UI/profile change must not invalidate unchanged DB2 bytes.
    code=stage_engine.module_dependency_fingerprint(
        [pathlib.Path(wago_snapshot.__file__),
         pathlib.Path(stage_engine.__file__)])
    def execute():
        opts={"build":expected_game_build,"make_archive":False}
        if fetch is not None:
            opts["fetch"]=fetch
        wago_snapshot.snapshot(output_dir,**opts)
    def validate(_paths):
        # v217 streams all declared bytes and seals their SHA exactly once
        # per run; defer cross-table SHA equality to its sealed output record
        # instead of reading hundreds of MB a second time here.
        receipt=json.loads((output_dir/"receipt.json").read_text("utf8"))
        entries=receipt.get("tables",{})
        return (receipt.get("schema")==
                "v161_wago_zero_seed_csv_snapshot_v1" and
                receipt.get("status")==
                "ALL_CSV_DOWNLOADED_NOT_YET_INTERPRETED" and
                receipt.get("build")==expected_game_build and
                receipt.get("locale")=="enUS" and
                receipt.get("simc_native_calls")==0 and
                receipt.get("legacy_item_ids_imported") is False and
                isinstance(receipt.get("fetched_at_utc"),str) and
                set(entries)==set(wago_snapshot.TABLES) and
                all(isinstance(entries[t],dict) and
                    entries[t].get("source_url") ==
                        ("https://wago.tools/db2/"+t+"/csv?"+
                         wago_snapshot.urlencode({
                             "build":expected_game_build,"locale":"enUS"}))
                    and entries[t].get("bytes") ==
                        (output_dir/(t+".csv")).stat().st_size
                    for t in wago_snapshot.TABLES) and
                receipt.get("total_csv_bytes") ==
                    sum(entries[t]["bytes"] for t in wago_snapshot.TABLES))
    try:
        stage=stage_engine.execute_stage(
            root=stage_root,stage_id="fresh-wago-db2",
            stage_version="v161-normal-collector-1",
            inputs={"game_build":expected_game_build,"locale":"enUS",
                    "tables":list(wago_snapshot.TABLES),
                    "source":"https://wago.tools/db2",
                    "code_sha256":code["sha256"]},
            outputs=outputs,execute=execute,validate=validate)
    except stage_engine.StageExecutionBlocked as exc:
        raise EnvironmentBuildBlocked(
            "V216_FRESH_WAGO_STAGE_BLOCKED:"+str(exc)) from exc
    except TimeoutError as exc:
        # No second download or changed v161/v217 fingerprint: next receipt
        # can distinguish Wago source transport from authenticated discovery.
        raise EnvironmentBuildBlocked(
            "V216_FRESH_WAGO_SOURCE_TIMEOUT") from exc
    # Cross-check the original downloader's per-table SHA with the hashes
    # actually sealed by v217. No extra full CSV read.
    receipts=stage_root/".stage_receipts"/"fresh-wago-db2.json"
    stage_doc=json.loads(receipts.read_text(encoding="utf8"))
    source_doc=json.loads((output_dir/"receipt.json").read_text(encoding="utf8"))
    need(all(
        stage_doc["outputs"][table]["sha256"] ==
            source_doc["tables"][table]["sha256"] and
        stage_doc["outputs"][table]["size"] ==
            source_doc["tables"][table]["bytes"]
        for table in wago_snapshot.TABLES),
        "V216_WAGO_SOURCE_AND_STAGE_SHA_MISMATCH")
    # Reuse the source authentication already performed by v217; no second
    # whole-file SHA pass in v163 or v190. Eligibility checks remain distinct.
    verified_wago_tables={t:{"sha256":stage_doc["outputs"][t]["sha256"],
                             "bytes":stage_doc["outputs"][t]["size"]}
                          for t in wago_snapshot.TABLES}
    # Optional forensic fallback only: SimC's measured rating is the
    # preferred numerical owner. Do not download another DB2 table during
    # every ordinary season Build when the raw enchant-point rows are not
    # needed. Existing sealed CSV remains readable by the local preflight.
    # Fetch the existing one CSV only for the requested four-stat default.
    # An injected collector must never silently mix in a live Wago source.
    need(type(auto_four_stat_gems) is bool,
         "V216_FOUR_STAT_SOURCE_REQUEST_BOOL_REQUIRED")
    if gem_enchant_transport is None and (
            fetch is not None or not auto_four_stat_gems):
        gem_enchant_csv={
            "status":("GEM_ENCHANT_INJECTED_TRANSPORT_PENDING"
                      if fetch is not None else
                      "GEM_ENCHANT_OPTIONAL_DBC_SOURCE_NOT_REQUESTED"),
            "candidate_path":None,"network_calls_by_stage":0,
            "J":None,"native_calls":0,"environment_ready":False}
    else:
        gem_enchant_csv=gem_enchant_stage.collect(
            stage_root=stage_root,build=expected_game_build,
            transport=gem_enchant_transport)
    linked=_join_authenticated_season_source(
        stage_root=stage_root,output_dir=output_dir,
        expected_game_build=expected_game_build,
        discovered=discovered,
        wago_stage_receipt=stage["receipt_sha256"],
        verified_tables=verified_wago_tables)
    # A caller-injected Wago transport cannot be mixed with a LIVE effect
    # relation unless its exact same-build transport is explicitly supplied.
    # Production with the ordinary v161 collector uses the live URL.
    if fetch is not None and gear_transport is None:
        fresh_gear={"status":"FRESH_GEAR_INJECTED_SOURCE_EFFECT_TRANSPORT_PENDING",
                    "candidate_path":None,"network_calls_by_stage":0,
                    "season_representative_verified":False}
    else:
        fresh_gear=_fresh_ordinary_gear_source_stage(
            stage_root=stage_root,wago_folder=output_dir,
            build=expected_game_build,linked=linked,transport=gear_transport)
    fresh_tier=_db2_first_tier_stage(
        stage_root=stage_root,wago_folder=output_dir,
        build=expected_game_build,linked=linked,
        wago_receipt_sha256=stage["receipt_sha256"],
        transport=tier_transport)
    tier_bonus=_raid_correlated_tier_stage(
        stage_root=stage_root,build=expected_game_build,
        linked=linked,fresh_tier=fresh_tier,transport=bonus_transport)
    tier_bridge=_physical_tier_to_simc_candidate(
        stage_root=stage_root,fresh_tier=fresh_tier,tier_bonus=tier_bonus)
    resolved_simc=_resolve_one_spec_simc_commit_stage(
        stage_root=stage_root,build=expected_game_build,
        gear=fresh_gear,tier=tier_bridge,
        revision_hint=simc_revision_hint,transport=simc_transport)
    pinned_revision=simc_revision or resolved_simc.get("simc_revision")
    need(not (simc_seed_directory is not None and pinned_revision is not None),
         "V216_DUPLICATE_PINNED_SIMC_SOURCE_INPUTS")
    # Game event and local history are independent. v229's legacy
    # 'cold_start' is only a source-collection mode when no prior build is
    # *recorded*; this is equally possible on a new season/expansion.
    source_context=_simc_source_collection_context(
        requested_event=simc_season_event,
        previous_game_build=previous_game_build)
    effective_source_event=source_context["source_collection_mode"]
    pinned_simc=_collect_first_party_simc_seed_stage(
        stage_root=stage_root,build=expected_game_build,
        revision=pinned_revision,
        previous_game_build=previous_game_build,
        season_event=effective_source_event,transport=simc_transport)
    effective_seed=simc_seed_directory or pinned_simc.get("source_dir")
    first_party=_verified_first_party_tier_options_stage(
        stage_root=stage_root,tier_bridge=tier_bridge,
        simc_seed_directory=effective_seed)
    # The existing active-raid tier selection AND first-party 13x5 SimC
    # match are already sealed; reuse them as a representative source rather
    # than re-identifying/re-certifying the tier in a separate engine.
    selected_tier=_reuse_existing_tier_source_stage(
        build=expected_game_build,tier_bridge=tier_bridge,
        first_party=first_party,request=representative_request)
    # Preserve the v251 CANDIDATE status while deriving the original v191
    # physical tier input from the already sealed Wago Item/ItemSparse bytes.
    # This costs one pair of CSV scans on a new build, zero on v217 reuse.
    try:
        compiler_tier=compiler_tier_source.collect(
            stage_root=stage_root,wago_folder=output_dir,
            build=expected_game_build,tier_bridge=tier_bridge,
            first_party=first_party,selected_tier=selected_tier,
            verified_wago_tables=verified_wago_tables)
    except compiler_tier_source.TierCompilerSourceBlocked as exc:
        raise EnvironmentBuildBlocked(str(exc).split(":",1)[0]) from exc
    # Optional seasonal consumables join reuses exactly the existing Wago
    # snapshot and the pinned v229 revision; missing evidence stays PENDING.
    # Injected snapshot tests must supply an explicit SimC transport and
    # never fall through into the public network.
    if fetch is not None and simc_transport is None:
        fresh_consumables={
            "status":"FRESH_CONSUMABLE_INJECTED_TRANSPORT_PENDING",
            "candidate_path":None,"network_calls_by_stage":0,
            "native_calls":0,"J":None,"F":None,"O":None,
            "environment_ready":False}
    else:
        fresh_consumables=_fresh_consumable_item_source_stage(
            stage_root=stage_root,wago_folder=output_dir,
            build=expected_game_build,linked=linked,
            pinned_simc=pinned_simc,transport=simc_transport,
            verified_tables=verified_wago_tables)
    # Reuse the sealed v254 ItemXItemEffect: fetch only the missing DB2
    # ItemEffect source. This is still unadmitted F/O provenance, not READY.
    if fetch is not None and item_effect_transport is None:
        fresh_item_spell=item_spell_bridge.pending(
            "V280_INJECTED_ITEM_EFFECT_TRANSPORT_NOT_SUPPLIED")
    else:
        fresh_item_spell=item_spell_bridge.collect(
            stage_root=stage_root,build=expected_game_build,
            fresh_gear=fresh_gear,consumables=fresh_consumables,
            transport=item_effect_transport)
    # Reuse the v229 generated gem/temp bytes and v189 unique_gear bytes;
    # only still-missing first-party v211/permanent files are fetched.
    # When upstream v189 is pending (e.g. injected CSV without exact SimC
    # transport), avoid implicit public requests or invented source proofs.
    try:
        if simc_transport is not None and simc_compiler_transport is None:
            # A fixture transports ONLY the original v229/v189 URL set.
            # Do not silently expand its contract or fall through to LIVE
            # GitHub for v275. Production (no injection) still auto-fetches.
            pinned_classifier=pinned_compiler_source.pending(
                "V275_INJECTED_SIMC_COMPILER_TRANSPORT_NOT_SUPPLIED")
        else:
            pinned_classifier=pinned_compiler_source.collect(
                stage_root=stage_root,build=expected_game_build,
                pinned_simc=pinned_simc,consumables=fresh_consumables,
                transport=simc_compiler_transport)
    except pinned_compiler_source.SimCCompilerInputBlocked as exc:
        raise EnvironmentBuildBlocked(str(exc).split(":",1)[0]) from exc
    full_seed={"status":"FRESH_FULL_SIMC_NOT_REQUESTED",
               "source_dir":None,"network_calls_by_stage":0,"native_calls":0}
    if (representative_request is not None and
            pinned_simc.get("source_dir") and
            fresh_gear.get("candidate_path") and
            tier_bridge.get("candidate_path")):
        full_seed=_lazy_full_pinned_simc_item_stage(
            stage_root=stage_root,build=expected_game_build,
            small_seed_dir=pinned_simc["source_dir"],
            gear_candidate=fresh_gear,tier_bridge=tier_bridge,
            request=representative_request,transport=simc_transport)
    # Same normal Build: exact SpellEffect 54 -> SimC temporary enchant ID
    # and exact Flask DBC item candidate, without F/O or UI promotion.
    if fetch is not None and spell_effect_transport is None:
        simc_consumable_relation=consumable_simc_relation.pending(
            "V281_INJECTED_SPELL_EFFECT_TRANSPORT_NOT_SUPPLIED")
    else:
        simc_consumable_relation=consumable_simc_relation.collect(
            stage_root=stage_root,build=expected_game_build,
            consumables=fresh_item_spell,compiler_source=pinned_classifier,
            full_simc_item_source=full_seed,
            transport=spell_effect_transport)
    # Same-build source class/inventory masks for exact SimC-linked oils.
    # No item/weapon approval and no calls when upstream remains PENDING.
    if fetch is not None and spell_equipped_transport is None:
        weapon_source=consumable_weapon_source.pending(
            "V285_INJECTED_WEAPON_TRANSPORT_NOT_SUPPLIED")
    else:
        weapon_source=consumable_weapon_source.collect(
            stage_root=stage_root,build=expected_game_build,
            consumables=simc_consumable_relation,
            transport=spell_equipped_transport)
    one_spec=_one_spec_ordinary_simc_stage(
        stage_root=stage_root,build=expected_game_build,
        fresh_gear=fresh_gear,tier_bridge=tier_bridge,
        seed_directory=full_seed.get("source_dir") or effective_seed,
        request=representative_request)
    # Preserve the difference between a selected, provenance-backed tier and
    # still-unmeasured G. This doesn't modify the v232 source-stage artifact.
    if selected_tier.get("selected_for_request") is not None:
        one_spec["tier_selected_from_existing_source_evidence"]=(
            selected_tier["selected_for_request"])
    # SimC player_t::default_level == MAX_LEVEL for the matched binary.
    # A source-only G probe does not hardcode expansion/game cap or add
    # user-level conditions. Explicit levels remain internal test overrides.
    physical_probe=_one_spec_source_G_probe_stage(
        stage_root=stage_root,build=expected_game_build,
        one_spec=one_spec,fresh_gear=fresh_gear,tier_bridge=tier_bridge,
        seed_directory=full_seed.get("source_dir") or effective_seed,
        character=g_probe_character)
    return {
        "schema":"v216_fresh_source_stage_v1",
        "status":"FRESH_WAGO_DB2_COLLECTED_MORE_SOURCES_PENDING",
        "expected_game_build":expected_game_build,
        "source":"https://wago.tools/db2",
        "fetched_at_utc":source_doc["fetched_at_utc"],
        "snapshot_receipt_path":str((output_dir/"receipt.json").resolve()),
        "source_stage":{k:v for k,v in stage.items() if k!="result"},
        "season_discovery":discovered,
        "season_join":linked,
        "fresh_ordinary_gear":fresh_gear,
        "fresh_one_spec_simc_representative":one_spec,
        "fresh_one_spec_physical_G_probe":physical_probe,
        "fresh_food_potion_item_sources":fresh_consumables,
        "fresh_consumable_item_spell_source":fresh_item_spell,
        "fresh_consumable_simc_effect_relation":simc_consumable_relation,
        "fresh_consumable_weapon_source":weapon_source,
        "fresh_gem_enchant_raw_source":gem_enchant_csv,
        "fresh_one_spec_character_level_policy":
            "SIMC_COMPILED_DEFAULT_MAX_LEVEL",
        "fresh_tier":fresh_tier,
        "fresh_tier_raid_bonus_corroboration":tier_bonus,
        "fresh_tier_simc_candidate_bridge":tier_bridge,
        "fresh_tier_first_party_simc_options":first_party,
        "fresh_tier_selected_from_existing_evidence":selected_tier,
        "fresh_compiler_tier_source":compiler_tier,
        "fresh_pinned_first_party_simc_source":pinned_simc,
        "fresh_pinned_v211_source":pinned_classifier,
        "fresh_pinned_simc_commit_resolution":resolved_simc,
        "simc_source_event":effective_source_event,
        "simc_source_collection_context":source_context,
        "fresh_lazy_full_pinned_simc_item_source":full_seed,
        "tier_discovery_mode":"DB2_FIRST_NO_PUBLISHER_NAME_LOOKUP",
        "network_calls_by_stage":(len(wago_snapshot.TABLES)
            if stage["executed"] else 0)+discovered["network_calls_by_stage"]+
            fresh_gear["network_calls_by_stage"]+
            fresh_tier["network_calls_by_stage"]+
            tier_bonus["network_calls_by_stage"]+
            pinned_simc["network_calls_by_stage"]+
            resolved_simc["network_calls_by_stage"]+
            full_seed["network_calls_by_stage"]+
            fresh_consumables["network_calls_by_stage"]+
            fresh_item_spell["network_calls_by_stage"]+
            simc_consumable_relation["network_calls_by_stage"]+
            weapon_source["network_calls_by_stage"]+
            pinned_classifier["network_calls_by_stage"]+
            compiler_tier["network_calls_by_stage"]+
            gem_enchant_csv["network_calls_by_stage"],
        "native_calls":0,
        "environment_installed":False,
        "environment_ready":False,
        "source_season_verified":False,
        "simc_source_verified":False,
        "G":None,"J":None,"F":None,"O":None,"B":None,"T":None,
        "requires":["CURRENT_EXPANSION_AND_SEASON_WCL_BLIZZARD_JOIN"]+
            ([] if selected_tier["source_evidence_reused"] else
             ["TIER_SELECTION_FROM_EXISTING_RAID_SIMC_EVIDENCE_PENDING"])+[
                    "SOURCE_FIRST_GEAR_AND_CONSUMABLE_JOINS",
                    "SIMC_EXACT_SOURCE_MANIFEST",
                    "G_J_F_O_B_T_AND_POLICY_A",
                    "NEW_SEASON_V212_PROFILE_INSTALL"],
        "existing_session_or_cache_mutated":False,
    }


def _zero_history_source_progress(source):
    """Report the real one-engine source stage without inventing G/J/F/O.

    This has no additional fetch, old-season lookup, cache or session writes.
    The v217 receipts from the same normal collector remain the resume keys.
    """
    need(type(source) is dict and source.get("schema")==
         "v216_fresh_source_stage_v1" and
         type(source.get("source_stage")) is dict and
         source["source_stage"].get("status") in (
             "EXECUTED_AND_SEALED","REUSED_VERIFIED","RECOVERED_VERIFIED"),
         "V216_ZERO_HISTORY_SOURCE_STAGE_NOT_SEALED")
    need(source.get("environment_installed") is False and
         source.get("environment_ready") is False and
         source.get("native_calls")==0 and
         all(source.get(name) is None for name in ("G","J","F","O","B","T")),
         "V216_ZERO_HISTORY_PREMATURE_BUDGET_OR_READY")
    # Only completed source stage receipts indicate reuse. PENDING fields are
    # not proof that the season has no matching items.
    pending=[]
    components=(
        ("season_source","season_join","SOURCE_SEASON_JOIN_PENDING"),
        ("representative_tier","fresh_tier_selected_from_existing_evidence",
         "REPRESENTATIVE_TIER_SOURCE_PENDING"),
        ("representative_gear","fresh_one_spec_simc_representative",
         "REPRESENTATIVE_GEAR_SOURCE_PENDING"),
        ("G_native","fresh_one_spec_physical_G_probe",
         "G_NATIVE_RATING_OBSERVATION_PENDING"),
        ("J_gems","fresh_gem_enchant_raw_source",
         "HIGHEST_QUALITY_GEM_J_SOURCE_PENDING"),
        ("F_flask","fresh_food_potion_item_sources",
         "HIGHEST_QUALITY_FLASK_F_SOURCE_PENDING"),
    )
    for label,key,reason in components:
        row=source.get(key)
        if type(row) is not dict:
            pending.append(reason)
        elif label=="G_native" and row.get("G") is None:
            pending.append(reason)
        elif label in ("J_gems","F_flask"):
            # A source candidate or raw effect table does not certify J/F.
            pending.append(reason)
        elif label=="season_source" and row.get(
                "status","").endswith("_PENDING"):
            pending.append(reason)
        elif label=="representative_tier" and not row.get(
                "source_evidence_reused",False):
            pending.append(reason)
        elif label=="representative_gear" and not row.get(
                "candidate_path"):
            pending.append(reason)
    pending.extend((
        "WEAPON_OIL_O_EXACT_APPLICATION_AND_RATING_PENDING",
        "SAME_SEASON_GJFO_B_T_AND_VERSIONED_INSTALL_PENDING",
        "SAME_BUILD_V191_V211_V213_V212_INSTALL_PENDING",
    ))
    return {
        "schema":"v216_zero_history_normal_build_progress_v1",
        "status":"SOURCE_COLLECTED_GJFO_PENDING_NOT_INSTALLED",
        "entrypoint":"v216.build_environment",
        "source_pipeline":"v216.collect_wago_new_season_source",
        "stage_engine":"v217.execute_stage",
        "history_dependency_required":False,
        "resume_from_sealed_source_stage":True,
        "source_stage_status":source["source_stage"]["status"],
        "same_build_cache_reuse":source["source_stage"].get("reused",False),
        "no_historical_budget_defaults":True,
        "requires":pending,
        "G":None,"J":None,"F":None,"O":None,"B":None,"T":None,
        "environment_ready":False,"environment_installed":False,
        "new_native_calls":0,
        "additional_network_calls":0,
        "user_session_created":False,
    }



def _zero_history_F_O_native_component_candidates(*, observations,
                                                 game_build, simc_revision):
    """Project existing v281 exact physical ID + v278 Native observation.

    This is a READ-ONLY source-only view for the existing v222 Build, not
    selection, quality/weapon certification or an independent effect model.
    Preserve each option separately: neither multiple flask qualities nor
    two oils may be summed/selected without their own validated conditions.
    """
    # v281 already bounds the entire sealed physical F/O worklist to 128.
    # Cached v278 measurements may return >4 rows with ZERO new subprocesses.
    need(type(observations) is list and len(observations) <= 128,
         "V216_ZERO_HISTORY_FO_OBSERVATION_COUNT_INVALID")
    candidates = []
    stats = season_budget_contract.STATS
    for row in observations:
        need(type(row) is dict and row.get("kind") in (
                 "flask", "food", "temporary_enchant"),
             "V216_ZERO_HISTORY_FO_NATIVE_RECORD_INVALID")
        source = row.get("physical_item_native_source_unadmitted")
        # Legacy developer token probes and mocks without a real v278 status
        # are not physical Native rating evidence. Do not reclassify them.
        if (source is None or row.get("status") not in (
                "SIMC_STATIC_CHMV_EFFECT_OBSERVED_NOT_ADMITTED",
                "SIMC_CONDITIONAL_OR_NONSTATIC_EFFECT_PENDING",
                "SIMC_CONSUMABLE_SOURCE_OR_BINARY_PENDING",
                "SIMC_CONSUMABLE_NATIVE_FAILED_NO_AUTO_RETRY")):
            continue
        need(type(source) is dict and source.get("schema") ==
                 consumable_simc_relation.MEASUREMENT_BINDING_SCHEMA
             and source.get("source_only") is True
             and source.get("environment_ready") is False
             and source.get("game_build") == game_build
             and source.get("simc_revision") == simc_revision
             and source.get("kind") == row["kind"]
             and source.get("simc_input_token") == row.get("token")
             and type(source.get("physical_item_id")) is int
             and source["physical_item_id"] > 0
             and type(source.get("crafting_quality")) is int
             and source["crafting_quality"] >= 0
             and all(type(source.get(k)) is str
                     and season_budget_contract.SHA.fullmatch(source[k])
                     for k in ("source_stage_receipt_sha256",
                               "source_candidate_sha256")),
             "V216_ZERO_HISTORY_FO_PHYSICAL_NATIVE_IDENTITY_DRIFT")
        # This makes NO claim that an item named oil is a valid weapon oil.
        if row["kind"] == "temporary_enchant":
            need(source.get("selected_hand") in ("main_hand", "off_hand")
                 and type(source.get("simc_enchant_id")) is int
                 and source["simc_enchant_id"] > 0,
                 "V216_ZERO_HISTORY_O_PHYSICAL_HAND_OR_ENCHANT_INVALID")
        else:
            need(source.get("selected_hand") is None,
                 "V216_ZERO_HISTORY_F_PHYSICAL_HAND_INVALID")
        observed = row.get("observed")
        candidate = {
            "kind": row["kind"],
            "physical_item_id": source["physical_item_id"],
            "crafting_quality": source["crafting_quality"],
            "simc_input_token": source["simc_input_token"],
            "simc_enchant_id": source.get("simc_enchant_id"),
            "selected_hand": source.get("selected_hand"),
            "game_build": game_build, "simc_revision": simc_revision,
            "physical_item_source_stage_sha256":
                source["source_stage_receipt_sha256"],
            "physical_item_source_candidate_sha256":
                source["source_candidate_sha256"],
            "status": "SOURCE_ONLY_NATIVE_STATIC_RATING_PENDING",
            "rating_candidate_unadmitted": None,
            "static_CHMV_vector_unadmitted": None,
            "simc_native_receipt_sha256": [],
            "same_effect_quality_group_verified": False,
            "weapon_and_hand_applicability_verified": False,
            "budget_ownership_verified": False,
            "source_admitted": False,
            "environment_ready": False,
        }
        if row.get("status") == "SIMC_STATIC_CHMV_EFFECT_OBSERVED_NOT_ADMITTED":
            need(type(observed) is dict
                 and observed.get("schema") == simc_snapshot_delta.SCHEMA
                 and observed.get("kind") == row["kind"]
                 and observed.get("token") == row.get("token")
                 and observed.get("simc_revision") == simc_revision
                 and observed.get("binary_sha256") == row.get("binary_sha256")
                 and observed.get("source_profile_sha256") ==
                     row.get("source_profile_sha256")
                 and row.get("simc_revision") == simc_revision
                 and type(row.get("native_case_receipts")) is list
                 and len(row["native_case_receipts"]) == 2
                 and all(type(rec) is dict and
                         rec.get("variant") == variant and
                         type(rec.get("receipt_sha256")) is str and
                         season_budget_contract.SHA.fullmatch(
                             rec["receipt_sha256"])
                         for variant,rec in zip(
                             ("baseline","active"),
                             row["native_case_receipts"])),
                 "V216_ZERO_HISTORY_FO_SIMC_NATIVE_IDENTITY_DRIFT")
            vector = observed.get("static_CHMV_candidate")
            need(type(vector) is dict and set(vector) == set(stats)
                 and all(type(vector[k]) is int and vector[k] >= 0
                         for k in stats)
                 and sum(vector.values()) > 0
                 and vector == row.get("static_CHMV_candidate"),
                 "V216_ZERO_HISTORY_FO_STATIC_VECTOR_DRIFT")
            if row["kind"] == "flask":
                candidate["static_CHMV_vector_unadmitted"] = dict(vector)
                need(row.get("F_candidate_unadmitted") ==
                         sum(vector.values()),
                     "V216_ZERO_HISTORY_F_NATIVE_TOTAL_DRIFT")
                candidate["rating_candidate_unadmitted"] = sum(
                    vector.values())
                candidate["status"] = "SIMC_NATIVE_STATIC_NUMBER_SOURCE_ONLY"
            elif row["kind"] == "temporary_enchant":
                need(row.get("O_candidate_unadmitted") == vector,
                     "V216_ZERO_HISTORY_O_NATIVE_VECTOR_DRIFT")
                # v269's buffed rating includes talent rounding. It cannot
                # authorize a static unbuffed O value, even if it is integer.
                candidate["buffed_CHMV_observation_unadmitted"] = dict(vector)
                candidate["status"] = "SIMC_BUFFED_O_OBSERVED_NOT_STATIC_SOURCE"
            candidate["simc_native_receipt_sha256"] = [
                rec["receipt_sha256"]
                for rec in row["native_case_receipts"]]
        candidates.append(candidate)
    return {
        "status": "PHYSICAL_ITEM_SIMC_F_O_CANDIDATES_UNADMITTED",
        "flask": [x for x in candidates if x["kind"] == "flask"],
        "oil": [x for x in candidates
                if x["kind"] == "temporary_enchant"],
        "source_only": True,
        "quality_or_effect_equivalence_verified": False,
        "game_weapon_applicability_verified": False,
        "no_multi_option_summing_or_quality_promotion": True,
        "F": None, "O": None, "environment_ready": False,
        "new_native_calls": 0, "network_calls": 0,
    }



def _zero_history_quality_weapon_candidate_join(*, numeric, weapon_source,
                                                game_build, simc_revision):
    """Reuse v281/v278 physical Native rows and the original v286 mask match.

    Strongest comparable observed effect is enough for the quality POLICY,
    without an exhaustive market scan or separate item-use certification.
    Weapon eligibility uses only
    the existing same-build v286 representative join; absence is not false
    proof of ineligibility. Do not calculate F/O/B/T or publish user options.
    """
    need(type(numeric) is dict and numeric.get("status") ==
         "PHYSICAL_ITEM_SIMC_F_O_CANDIDATES_UNADMITTED"
         and type(numeric.get("flask")) is list
         and type(numeric.get("oil")) is list,
         "V216_FO_JOIN_NUMERIC_SOURCE_REQUIRED")
    groups = {}
    for option in numeric["flask"]:
        token = option["simc_input_token"]
        quality = option["crafting_quality"]
        suffix = "_" + str(quality)
        # v281 flask token comes from the exact SimC ItemID DBC relation.
        # Do not merge different stat kinds or unfamiliar naming formats.
        family = (token[:-len(suffix)]
                  if token.endswith(suffix) else
                  "item_" + str(option["physical_item_id"]))
        groups.setdefault(family, []).append(option)
    flasks = []
    for family, rows in sorted(groups.items()):
        ranked = sorted(rows, key=lambda x:(
            -x["crafting_quality"], x["physical_item_id"]))
        measured = [x for x in ranked
                    if x["status"] == "SIMC_NATIVE_STATIC_NUMBER_SOURCE_ONLY"
                    and type(x.get("static_CHMV_vector_unadmitted")) is dict]
        # The approved quality rule is strongest actually observed effect,
        # not exhaustive measurement of every catalog quality.
        best = (max(measured,key=lambda x:(
            sum(x["static_CHMV_vector_unadmitted"].values()),
            x["crafting_quality"],-x["physical_item_id"]))
            if measured else None)
        best_vector = (best["static_CHMV_vector_unadmitted"]
                       if best is not None else None)
        kinds = [frozenset(k for k,v in
                            x["static_CHMV_vector_unadmitted"].items()
                            if v > 0) for x in measured]
        comparable = (bool(measured) and bool(kinds[0])
                      and all(k == kinds[0] for k in kinds)
                      and all(all(best_vector[k]>=
                                  x["static_CHMV_vector_unadmitted"][k]
                                  for k in season_budget_contract.STATS)
                              for x in measured))
        flasks.append({
            "simc_family_stem_source_only":family,
            "observed_item_ids":[x["physical_item_id"] for x in measured],
            "observed_qualities":[x["crafting_quality"] for x in measured],
            "source_unmeasured_item_ids_unadmitted":[
                x["physical_item_id"] for x in ranked if x not in measured],
            "status":("TOP_QUALITY_AMONG_OBSERVED_ONLY"
                      if comparable and len(measured)>1 else
                      "ONLY_ONE_QUALITY_OBSERVED" if comparable else
                      "QUALITY_STATIC_STATS_NOT_COMPARABLE"),
            "highest_observed_quality_item_id_unadmitted":
                best["physical_item_id"] if comparable else None,
            "highest_observed_rating_unadmitted":
                best["rating_candidate_unadmitted"] if comparable else None,
            "observed_strongest_effect_sufficient_quality_policy":
                bool(comparable),
            # Historical diagnostic, NOT a prerequisite for selection.
            "all_market_qualities_verified":False,
            "user_selectable":False,
        })
    source = weapon_source or {}
    stage_status = source.get("status")
    if stage_status in ("REPRESENTATIVE_OIL_MASK_MATCH_SOURCE_ONLY",
                        "REPRESENTATIVE_OIL_MASK_MATCH_PENDING"):
        need(source.get("schema") ==
                 "v286_representative_oil_source_compatibility_v1"
             and source.get("same_build_source_only") is True
             and source.get("game_build") == game_build
             and source.get("simc_revision") == simc_revision
             and source.get("environment_ready") is False
             and type(source.get("candidate_options")) is list
             and len(source["candidate_options"]) <= 10000,
             "V216_FO_V286_WEAPON_SOURCE_IDENTITY_DRIFT")
        weapon_rows = source["candidate_options"]
    else:
        weapon_rows = []
    oils = []
    for option in numeric["oil"]:
        hand = option["selected_hand"]
        token = option["simc_input_token"]
        # v281 constructs precisely this hand-qualified SimC option.
        prefix = ("main_hand:" if hand == "main_hand" else
                  "main_hand:disabled/off_hand:")
        stripped = token[len(prefix):] if token.startswith(prefix) else None
        matching = [w for w in weapon_rows
                    if w.get("oil_item_id") == option["physical_item_id"]
                    and w.get("quality_rank") == option["crafting_quality"]
                    and w.get("simc_enchant_id") == option["simc_enchant_id"]
                    and stripped==(
                        w.get("simc_token")+"_"+str(option["crafting_quality"])
                        if option["crafting_quality"]>0 else
                        w.get("simc_token"))
                    and w.get("hand") == hand
                    and w.get("matched_same_build_spell_equipped_masks") is True
                    and w.get("user_selectable") is False]
        need(len(matching) <= 1, "V216_FO_V286_DUPLICATE_WEAPON_MATCH")
        selected = matching[0] if matching else None
        oils.append({
            "physical_item_id":option["physical_item_id"],
            "crafting_quality":option["crafting_quality"],
            "simc_input_token":token,
            "hand":hand,
            "status":("SAME_BUILD_REPRESENTATIVE_WEAPON_MASK_MATCH_SOURCE_ONLY"
                      if selected is not None else
                      "REPRESENTATIVE_WEAPON_MASK_NOT_MATCHED_OR_PENDING"),
            "selected_representative_weapon_id_unadmitted":
                selected["representative_weapon_id"]
                if selected is not None else None,
            "static_O_for_hand_unadmitted":(
                dict(option["rating_candidate_unadmitted"])
                if selected is not None and
                   option["status"] == "SIMC_RAW_STATIC_NUMBER_SOURCE_ONLY"
                else None),
            "weapon_min_ilevel_and_use_conditions_verified":False,
            "official_budget_ownership_verified":False,
            "user_selectable":False,
        })
    return {
        "schema":"v216_existing_flask_quality_and_weapon_mask_join_v1",
        "status":"SOURCE_ONLY_OBSERVED_CHOICES_NOT_SEASON_ADMITTED",
        "game_build":game_build,"simc_revision":simc_revision,
        "flask_quality_groups_observed_unadmitted":flasks,
        "oil_representative_weapon_matches_unadmitted":oils,
        "oil_source_status":stage_status or "REPRESENTATIVE_SOURCE_NOT_PROVIDED",
        "oil_source_stage_identities":source.get("source_stage_identities")
            if stage_status in ("REPRESENTATIVE_OIL_MASK_MATCH_SOURCE_ONLY",
                                "REPRESENTATIVE_OIL_MASK_MATCH_PENDING")
            else None,
        "highest_available_quality_verified":False,
        "quality_only_compared_when_same_simc_family_and_static_stat_kind":True,
        "weapon_min_ilevel_and_use_conditions_verified":False,
        "F":None,"O":None,"B":None,"T":None,
        "environment_ready":False,"user_selectable":False,
        "new_native_calls":0,"network_calls":0,
    }




def _zero_history_G_numeric_input_from_preflight(*, preflight,
                                                 target_ilevel=None):
    """Reuse Native G or a previously reconciled same-season v222 G source.

    The latter is NOT authenticated here; the normal Build's source-stage
    owner is responsible for validating original G provenance before READY.
    """
    if type(preflight) is not dict:
        return None
    native = preflight.get("v277_native_G_preprofile_unadmitted")
    if native is not None:
        return native
    g = preflight.get("v222_G_component_reference_unadmitted")
    calc = preflight.get("proposed_budget_arithmetic_unadmitted")
    if type(g) is not dict or type(calc) is not dict:
        return None
    if (g.get("source_verification") not in
            ("EXACT_NATIVE","VALID_SAME_SEASON_REFERENCE",
             "VALID_SAME_SEASON_SOURCE")
        or g.get("game_build") != preflight.get("game_build")
        or g.get("source_catalog_manifest_sha256") !=
            preflight.get("source_catalog_manifest_sha256")
        or calc.get("game_build") != preflight.get("game_build")
        or calc.get("simc_revision") != preflight.get("simc_revision")
        or calc.get("source_catalog_manifest_sha256") !=
            preflight.get("source_catalog_manifest_sha256")
        or calc.get("source_catalog_artifact_sha256") !=
            preflight.get("source_artifact_sha256")
        or (target_ilevel is not None and
            calc.get("target_ilevel") != target_ilevel)
        or calc.get("reference_G") != g.get("rating")
        or calc.get("source_authentication_performed_here") is not False
        or type(g.get("rating")) is not int
        or g["rating"] <= 0
        or type(g.get("source_sha256")) is not str
        or season_budget_contract.SHA.fullmatch(g["source_sha256"]) is None):
        return None
    return {
        "status":"V222_SAME_SEASON_REFERENCE_G_NUMERIC_UNADMITTED",
        "standardized_G":g["rating"],
        "native_json2_sha256":g["source_sha256"],
        "standardization":g.get("standardization"),
        "target_ilevel":calc["target_ilevel"],
        "source_origin":"V222_ALREADY_RECONCILED_G_COMPONENT",
        "source_authentication_performed_here":False,
    }


def _source_only_one_flask_budget_preview(*, preflight, worklist,
                                          native_numeric, source_choices):
    """Choose a single observed F family ONLY for an unadmitted no-oil preview.

    This reuses v281's exact measured population, v278's static deltas and
    v216's existing observed-quality comparison. It never asserts market
    coverage, gameplay effect equivalence or official oil selection.
    Multiple independent flask families are intentionally not guessed.
    """
    out={"schema":"v216_source_only_observed_flask_budget_preview_v1",
         "status":"AUTO_F_PREVIEW_PENDING",
         "requires":[],"selected_physical_items_unadmitted":None,
         "oil_zero_is_preview_assumption_only":True,
         "highest_available_quality_verified":False,
         "quality_or_effect_equivalence_verified":False,
         "user_selectable":False,"environment_ready":False,
         "native_calls":0,"network_calls":0}
    # Selecting a measured physical F item does not depend on G or J.
    # Only B/T preview computation does; keep missing core data pending.
    missing_G_J=(type(preflight) is not dict or
        _zero_history_G_numeric_input_from_preflight(
            preflight=preflight) is None or
        preflight.get("physical_gem_J_arithmetic_unadmitted") is None)
    if (type(worklist) is not dict or worklist.get("status")!=
            "MEASURABLE_PHYSICAL_F_O_CANDIDATES_UNADMITTED" or
            type(worklist.get("flask")) is not list or
            not worklist["flask"]):
        out["requires"].append("COMPLETE_SEALED_V281_FLASK_WORKLIST_REQUIRED")
        return out
    if (type(native_numeric) is not dict or
            type(native_numeric.get("flask")) is not list or
            type(source_choices) is not dict):
        out["requires"].append("EXACT_NATIVE_FLASK_OBSERVATIONS_REQUIRED")
        return out
    planned=worklist["flask"]
    measured=native_numeric["flask"]
    planned_by_id={x.get("physical_item_id"):x for x in planned}
    measured_by_id={x.get("physical_item_id"):x for x in measured}
    need(len(planned_by_id)==len(planned) and
         len(measured_by_id)==len(measured),
         "V216_F_PREVIEW_DUPLICATE_PHYSICAL_ITEMS")
    if (not measured_by_id or
            not set(measured_by_id)<=set(planned_by_id) or
            any(measured_by_id[item_id].get("status")!=
                    "SIMC_NATIVE_STATIC_NUMBER_SOURCE_ONLY" or
                measured_by_id[item_id].get("simc_input_token")!=
                    planned_by_id[item_id].get("simc_input_token") or
                measured_by_id[item_id].get("crafting_quality")!=
                    planned_by_id[item_id].get("crafting_quality")
                for item_id in measured_by_id)):
        out["requires"].append("ORIGINAL_OBSERVED_FLASK_SOURCE_PENDING")
        return out
    # Different effects are separate options, not a numerical competition:
    # never pick one family just because another is not yet measured.
    families=set()
    for row in planned:
        token=row["simc_input_token"]
        suffix="_"+str(row["crafting_quality"])
        families.add(token[:-len(suffix)] if token.endswith(suffix) else
                     "item_"+str(row["physical_item_id"]))
    if len(families)!=1:
        out["requires"].append("FLASK_EFFECT_FAMILY_NOT_UNAMBIGUOUS")
        return out
    groups=source_choices.get("flask_quality_groups_observed_unadmitted")
    if type(groups) is not list or len(groups)!=1:
        out["requires"].append("FLASK_EFFECT_FAMILY_NOT_UNAMBIGUOUS")
        return out
    group=groups[0]
    chosen=group.get("highest_observed_quality_item_id_unadmitted")
    if (group.get("status") not in (
            "TOP_QUALITY_AMONG_OBSERVED_ONLY",
            "ONLY_ONE_QUALITY_OBSERVED") or
            chosen not in measured_by_id or
            set(group.get("observed_item_ids",[]))!=set(measured_by_id)):
        out["requires"].append("FLASK_STATIC_RATING_QUALITY_COMPARISON_PENDING")
        return out
    return {**out,
            "status":"ONE_OBSERVED_FLASK_NO_OIL_NUMERIC_PREVIEW_UNADMITTED",
            "selected_physical_items_unadmitted":{
                "flask_item_id":chosen,"oil_item_ids_by_hand":{}},
            "requires":(["G_AND_PHYSICAL_J_PREVIEW_REQUIRED"]
                        if missing_G_J else [])+
                       ["F_ORIGINAL_NATIVE_RECEIPTS_REQUIRED",
                        "O_EXPLICIT_NONE_NOT_IMPLIED"]}


def _zero_history_selected_F_O_v222_reconcile(*, selected, numeric,
                                             choices, existing_budget,
                                             budget_evidence):
    """Check selected exact physical F/O against ORIGINAL v222 arithmetic.

    A successful comparison is numeric/source-only; it never authenticates
    quality coverage, socket legality, weapon minimum ilvl or product READY.
    Missing physical Native facts remain PENDING, not zero. Selected no-oil
    is an explicit empty hand mapping and legitimately has fixed O=0.
    """
    out={
        "status":"SELECTED_PHYSICAL_F_O_SOURCE_PENDING",
        "selected_physical_items":selected,
        "missing":[],"matched_f":None,"matched_o_by_hand":{},
        "v222_numbers_reconciled":False,
        "source_admission_performed_here":False,
        "environment_ready":False,"user_selectable":False,
        "new_native_calls":0,"network_calls":0}
    need(type(numeric) is dict and type(choices) is dict,
         "V216_SELECTED_PHYSICAL_NUMERIC_AND_MASK_REQUIRED")
    found=[x for x in numeric.get("flask",[])
           if x["physical_item_id"]==selected["flask_item_id"]]
    need(len(found)<=1,"V216_SELECTED_FLASK_DUPLICATE_OBSERVATION")
    flask=found[0] if found else None
    if flask is None or flask["status"]!=(
            "SIMC_NATIVE_STATIC_NUMBER_SOURCE_ONLY"):
        out["missing"].append("SELECTED_FLASK_STATIC_NATIVE_PENDING")
    else:
        # The selected F scalar is only the sum of the SAME original
        # v281 physical item and v278 SimC static CHMV vector. No effect
        # mechanism reimplementation, historical constants or extra Native.
        fvec=flask.get("static_CHMV_vector_unadmitted")
        need(type(fvec) is dict and
             set(fvec)==set(season_budget_contract.STATS) and
             all(type(fvec[s]) is int and fvec[s]>=0
                 for s in season_budget_contract.STATS) and
             sum(fvec.values())>0 and
             sum(fvec.values())==flask.get("rating_candidate_unadmitted") and
             type(flask.get("crafting_quality")) is int and
             flask["crafting_quality"]>=0 and
             type(flask.get("simc_input_token")) is str and
             type(flask.get("physical_item_source_candidate_sha256")) is str and
             season_budget_contract.SHA.fullmatch(
                 flask["physical_item_source_candidate_sha256"]) is not None,
             "V216_SELECTED_F_SIMC_NUMBER_OR_EXACT_SOURCE_DRIFT")
        out["matched_f"]={
            "physical_item_id":flask["physical_item_id"],
            "crafting_quality":flask["crafting_quality"],
            "simc_input_token":flask["simc_input_token"],
            "static_CHMV_vector":dict(fvec),
            "source_candidate_sha256":
                flask["physical_item_source_candidate_sha256"],
            "rating":flask["rating_candidate_unadmitted"],
            "simc_native_receipt_sha256":flask["simc_native_receipt_sha256"],
            "F_numeric_source_owner":"EXISTING_V281_V278_SIMC_DELTA_ONLY"}
    for hand,item_id in sorted(selected["oil_item_ids_by_hand"].items()):
        observed=[x for x in numeric.get("oil",[])
                  if x["physical_item_id"]==item_id and
                  x["selected_hand"]==hand]
        matched=[x for x in choices.get(
            "oil_representative_weapon_matches_unadmitted",[])
            if x.get("physical_item_id")==item_id and
            x.get("hand")==hand and
            x.get("status")==(
                "SAME_BUILD_REPRESENTATIVE_WEAPON_MASK_MATCH_SOURCE_ONLY")]
        need(len(observed)<=1 and len(matched)<=1,
             "V216_SELECTED_OIL_DUPLICATE_PHYSICAL_HAND_OBSERVATION")
        if (len(observed)!=1 or len(matched)!=1 or
                observed[0]["status"]!=(
                    "SIMC_RAW_STATIC_NUMBER_SOURCE_ONLY") or
                observed[0]["rating_candidate_unadmitted"]!=
                    matched[0]["static_O_for_hand_unadmitted"]):
            out["missing"].append("SELECTED_OIL_"+hand.upper()+
                                  "_STATIC_OR_WEAPON_MASK_PENDING")
        else:
            out["matched_o_by_hand"][hand]={
                "physical_item_id":item_id,
                "representative_weapon_id":
                    matched[0]["selected_representative_weapon_id_unadmitted"],
                "rating":dict(observed[0]["rating_candidate_unadmitted"]),
                "simc_native_receipt_sha256":
                    observed[0]["simc_native_receipt_sha256"]}
    if out["missing"]:
        return out
    if existing_budget is None:
        out["status"]="SELECTED_PHYSICAL_F_O_OBSERVED_V222_PROOF_PENDING"
        out["missing"].append("V222_EXISTING_BUDGET_EVIDENCE_PENDING")
        return out
    need(type(existing_budget) is dict and
         type(budget_evidence) is dict and
         type(budget_evidence.get("components")) is dict and
         type(budget_evidence["components"].get("O")) is dict,
         "V216_SELECTED_V222_EXISTING_BUDGET_CONTRACT_REQUIRED")
    summed={key:0 for key in season_budget_contract.STATS}
    for candidate in out["matched_o_by_hand"].values():
        for key in summed:
            summed[key]+=candidate["rating"][key]
    need(existing_budget["F"]==out["matched_f"]["rating"] and
         existing_budget["fixed_O"]==summed and
         sorted(budget_evidence["components"]["O"].get("applied_hands",[]))==
             sorted(selected["oil_item_ids_by_hand"]),
         "V216_SELECTED_F_O_V222_PHYSICAL_RATING_OR_HANDS_CONFLICT")
    out["status"]="SELECTED_PHYSICAL_F_O_V222_ARITHMETIC_RECONCILED_UNADMITTED"
    out["v222_numbers_reconciled"]=True
    out["v222_arithmetic_unadmitted"]={
        "F":existing_budget["F"],
        "fixed_O":existing_budget["fixed_O"],
        "base_B":existing_budget["base_B"],
        "final_T":existing_budget["final_T"],
        "manual_final_T_authoritative":
            existing_budget["manual_final_T_authoritative"]}
    return out



def _zero_history_auto_v222_numeric_preview(*, preflight, native_numeric,
                                           source_choices, selected, gem_ratings,
                                           target_ilevel, manual_final_T,
                                           no_oil_is_preview_assumption=False):
    """Original v222 B/T over already observed G/J/selected physical F/O.

    Deliberately unadmitted and not executable by v098/v094. It reuses
    original v277 G or an already reconciled same-season v222 G reference,
    plus v271, v281/v278 and v286 outputs. No old-season defaults. Only
    upstream source owners authenticate evidence; not this numeric adapter.
    """
    out = {"schema":"v216_zero_history_selected_v222_numeric_preview_v1",
           "status":"GJFO_SELECTED_NUMERIC_OBSERVATIONS_PENDING",
           "requires":[],"calculation":None,"selected_physical_items":selected,
           "numeric_preview_only":True,"source_authenticated":False,
           "policy_A_registered":False,"user_session_created":False,
           "environment_ready":False,"native_calls":0,"network_calls":0,
           "oil_zero_is_preview_assumption_only":no_oil_is_preview_assumption}
    need(type(selected) is dict and type(native_numeric) is dict
         and type(source_choices) is dict,
         "V216_AUTO_NUMERIC_SELECTED_SOURCES_INVALID")
    need(type(no_oil_is_preview_assumption) is bool
         and (not no_oil_is_preview_assumption
              or not selected.get("oil_item_ids_by_hand")),
         "V216_NO_OIL_PREVIEW_SCOPE_INVALID")
    if preflight is None:
        out["requires"].append("CURRENT_V213_PREFLIGHT_PENDING")
        return out
    g = _zero_history_G_numeric_input_from_preflight(
        preflight=preflight,target_ilevel=target_ilevel)
    j = preflight.get("physical_gem_J_arithmetic_unadmitted")
    # Policy: J is the ordinary-gem NOMINAL secondary-rating budget.
    # Exactly one special gem remains equipped for SimC effect mechanics.
    # Its optional raw-static observation is NOT an extra J component or
    # a reason to block J arithmetic. Native candidate reconciliation still
    # owns the final 4-stat vector; do not reimplement the special effect.
    out["J_accounting_policy"]="ORDINARY_GEM_NOMINAL_SECONDARY_SUM_ONLY"
    out["special_gem_effect_owner"]="SIMC_PROFILE"
    if g is None:
        # Native G is optional when a valid same-season G reference exists.
        out["requires"].append("SAME_SEASON_G_BUDGET_SOURCE_PENDING")
    if j is None:
        out["requires"].append("V271_PHYSICAL_GEM_J_NUMERIC_PENDING")
    flask_rows=[x for x in native_numeric.get("flask",[])
                if x["physical_item_id"]==selected["flask_item_id"]]
    need(len(flask_rows)<=1,"V216_AUTO_SELECTED_FLASK_DUPLICATED")
    f=flask_rows[0] if flask_rows else None
    if f is None or f["status"]!="SIMC_NATIVE_STATIC_NUMBER_SOURCE_ONLY":
        out["requires"].append("SELECTED_FLASK_NATIVE_RATING_PENDING")
    oils={}
    for hand,item_id in sorted(selected["oil_item_ids_by_hand"].items()):
        observed=[x for x in native_numeric.get("oil",[])
                  if x["physical_item_id"]==item_id and
                  x["selected_hand"]==hand]
        matched=[x for x in source_choices.get(
            "oil_representative_weapon_matches_unadmitted",[])
                 if x.get("physical_item_id")==item_id and
                 x.get("hand")==hand and x.get("status")==(
                     "SAME_BUILD_REPRESENTATIVE_WEAPON_MASK_MATCH_SOURCE_ONLY")]
        need(len(observed)<=1 and len(matched)<=1,
             "V216_AUTO_SELECTED_OIL_DUPLICATED")
        if (len(observed)!=1 or len(matched)!=1 or
            observed[0]["status"]!="SIMC_RAW_STATIC_NUMBER_SOURCE_ONLY"
            or observed[0]["rating_candidate_unadmitted"]!=
               matched[0]["static_O_for_hand_unadmitted"]):
            out["requires"].append("SELECTED_OIL_"+hand.upper()+
                                    "_NATIVE_OR_WEAPON_MASK_PENDING")
        else:
            oils[hand]={"native":observed[0],"mask":matched[0]}
    if out["requires"]:
        return out
    need(type(g) is dict and type(j) is dict
         and type(gem_ratings) is dict
         and g.get("status") in (
             "NATIVE_G_NUMERIC_SOURCE_ONLY_JFO_AND_ADMISSION_PENDING",
             "V222_SAME_SEASON_REFERENCE_G_NUMERIC_UNADMITTED")
         and j.get("status")=="PHYSICAL_GEM_J_ARITHMETIC_UNADMITTED"
         and j.get("game_socket_legality_verified_here") is False,
         "V216_AUTO_G_J_SOURCE_ONLY_IDENTITY_REQUIRED")
    stats=season_budget_contract.STATS
    oil_vector={stat:sum(row["native"]["rating_candidate_unadmitted"][stat]
                          for row in oils.values()) for stat in stats}
    catalog={"game_build":preflight["game_build"],
             "simc_revision":preflight["simc_revision"],
             "manifest_sha256":
                 preflight["source_catalog_manifest_sha256"]}
    manifest_sha=catalog["manifest_sha256"]
    def comp(rating,sha):
        return {"rating":rating,"game_build":catalog["game_build"],
                "source_catalog_manifest_sha256":manifest_sha,
                "source_sha256":sha,
                "source_verification":"UNADMITTED_NUMERIC_OBSERVATION"}
    def source_sha(*,kind,items):
        return digest(canonical({"kind":kind,"items":items}).encode("utf8"))
    j_identity={"layout":preflight["physical_gem_layout_unadmitted"],
                "rating_by_id":gem_ratings}
    # Only the NEW raw-source fallback carries v266/v221 origin. Preserve
    # the exact historical explicit-gem SHA and its existing cache identity.
    if j.get("rating_origin")== "V266_RAW_SAME_BUILD_EFFECT_POINTS_ONLY":
        j_identity["raw_points_source_sha256"]=j["source_enchant_sha256"]
        j_identity["source_v221_stage_receipt_sha256"]=j.get(
            "source_v221_stage_receipt_sha256")
    if j.get("rating_origin")=="SEASON_NOMINAL_PER_ITEM_TOTAL_SOURCE":
        j_identity["season_nominal_source_sha256"]=j[
            "nominal_source_sha256"]
        j_identity["source_v221_stage_receipt_sha256"]=j.get(
            "source_v221_stage_receipt_sha256")
    j_sha=source_sha(kind="physical_gem_layout_and_ratings",
                    items=j_identity)
    f_sha=source_sha(kind="selected_flask_original_v278_receipts",
                    items={"item_id":f["physical_item_id"],
                           "candidate_sha256":
                               f["physical_item_source_candidate_sha256"],
                           "native_receipts":
                               f["simc_native_receipt_sha256"],
                           "static_vector":
                               f["static_CHMV_vector_unadmitted"]})
    oil_receipts=[{
        "hand":hand,
        "item_id":part["native"]["physical_item_id"],
        "native_receipts":part["native"]["simc_native_receipt_sha256"],
        "candidate_sha256":
            part["native"]["physical_item_source_candidate_sha256"],
        "representative_weapon_id":
            part["mask"]["selected_representative_weapon_id_unadmitted"]}
        for hand,part in sorted(oils.items())]
    oil_sha=source_sha(kind="selected_oil_hands_and_v286_mask",
                      items=oil_receipts)
    evidence={
        "schema":season_budget_contract.SCHEMA,
        "game_build":catalog["game_build"],
        "simc_revision":catalog["simc_revision"],
        "source_catalog_manifest_sha256":manifest_sha,
        "source_catalog_artifact_sha256":
            preflight["source_artifact_sha256"],
        "target_ilevel":target_ilevel,
        "components":{
            "G":{**comp(g["standardized_G"],g["native_json2_sha256"]),
                 **({"standardization":g["standardization"]}
                    if g.get("standardization") is not None else {})},
            "J":comp(j["J_candidate_unadmitted"],j_sha),
            "F":comp(f["rating_candidate_unadmitted"],f_sha),
            "O":(season_budget_contract.explicit_no_oil_component(
                game_build=catalog["game_build"],
                source_catalog_manifest_sha256=manifest_sha,
                selected_oil_item_ids_by_hand=selected["oil_item_ids_by_hand"])
                if (not selected["oil_item_ids_by_hand"] and
                    not no_oil_is_preview_assumption) else
                {**comp(oil_vector,oil_sha),
                 "applied_hands":sorted(oils),
                 "weapon_applicability_verified":False,
                 "source_mask_matches_all_selected_only":True})},
        "fixed_L":{k:0 for k in stats},
        "fixed_E":{k:0 for k in stats},
        "G_reference_excludes_selected_E":True}
    if (not selected["oil_item_ids_by_hand"] and
            not no_oil_is_preview_assumption):
        # An actual explicit NONE is O=0. An automatic fallback is only
        # a preview assumption and must not claim the user's selection.
        oil_sha=evidence["components"]["O"]["source_sha256"]
    try:
        calculation=season_budget_contract.preprofile_budget(
            source_catalog=catalog,
            source_artifact_sha256=preflight["source_artifact_sha256"],
            evidence=evidence,target_ilevel=target_ilevel,
            manual_final_T=manual_final_T,numeric_preview_only=True)
    except season_budget_contract.SeasonBudgetBlocked as exc:
        raise EnvironmentBuildBlocked(
            "V216_AUTO_SELECTED_V222_NUMERIC_INVALID:"+str(exc)) from exc
    out.update({
        "status":"SELECTED_GJFO_V222_ARITHMETIC_PREVIEW_UNADMITTED",
        "calculation":calculation,
        "numeric_receipt_identities":{
            **({"G_native_json2_sha256":g["native_json2_sha256"]}
               if g["status"] ==
               "NATIVE_G_NUMERIC_SOURCE_ONLY_JFO_AND_ADMISSION_PENDING"
               else {"G_same_season_reference_source_sha256":
                     g["native_json2_sha256"]}),
            "J_physical_layout_rating_sha256":j_sha,
            "F_selected_item_native_sha256":f_sha,
            "O_selected_hands_native_mask_sha256":oil_sha},
        "L_E_unselected_plain_representative_only":True,
        "unknown_oil_not_treated_as_zero":True})
    return out



def _zero_history_v098_profile_source_inputs(*, numeric_preview,
                                             physical_sources):
    """Direct v216 observed ItemID/token/O -> existing v098 source-only path.

    This is JSON plumbing of the already selected v281/v278/v286 receipts,
    not independently authenticated options or a runnable product manifest.
    """
    need(type(numeric_preview) is dict and
         type(physical_sources) is dict,
         "V216_V098_SELECTED_PROFILE_INPUT_OBJECTS_REQUIRED")
    if numeric_preview.get("status")!=(
            "SELECTED_GJFO_V222_ARITHMETIC_PREVIEW_UNADMITTED"):
        return None
    selected=numeric_preview["selected_physical_items"]
    flasks=[x for x in physical_sources.get("flask",[])
            if x.get("physical_item_id")==selected["flask_item_id"]]
    need(len(flasks)==1 and flasks[0].get("status")==(
             "SIMC_NATIVE_STATIC_NUMBER_SOURCE_ONLY"),
         "V216_V098_SELECTED_FLASK_SOURCE_DRIFT")
    flask=flasks[0]
    by_hand={}
    for hand,item_id in selected["oil_item_ids_by_hand"].items():
        options=[row for row in physical_sources.get("oil",[])
                 if row.get("physical_item_id")==item_id and
                 row.get("selected_hand")==hand]
        need(len(options)==1 and options[0].get("status")==(
                 "SIMC_RAW_STATIC_NUMBER_SOURCE_ONLY"),
             "V216_V098_SELECTED_OIL_SOURCE_DRIFT")
        row=options[0]
        by_hand[hand]={
            "physical_item_id":item_id,
            "simc_input_token":row["simc_input_token"],
            "static_CHMV_vector":dict(row["static_CHMV_vector_unadmitted"])}
    return {
        "schema":"v098_internal_season_profile_inputs_v1",
        "v216_numeric_preview":numeric_preview,
        "flask":{"physical_item_id":flask["physical_item_id"],
                 "simc_input_token":flask["simc_input_token"],
                 "static_CHMV_vector":dict(
                     flask["static_CHMV_vector_unadmitted"])},
        "oil_by_hand":by_hand}



def _sealed_v233_precombat_F_O_profile(*,stage_root,source_profile_path):
    """Reuse the verified G gear but supply v269's precombat snapshot APL.

    v233's input remains pristine for static G, while v278 pairs are keyed
    by an immutable derived profile and original v217 source identity.
    This is an APL input connection, NOT a consumable effect implementation.
    """
    root=pathlib.Path(stage_root).resolve(strict=True)
    path=pathlib.Path(source_profile_path)
    need(root.is_dir() and not root.is_symlink() and
         path.is_file() and not path.is_symlink() and
         path.resolve().is_relative_to(root) and
         0<path.stat().st_size<=4_000_000,
         "V216_AUTO_F_O_V233_SOURCE_PROFILE_REQUIRED")
    original=path.read_bytes()
    try:
        raw=original.decode("utf8")
    except UnicodeError as exc:
        raise EnvironmentBuildBlocked(
            "V216_AUTO_F_O_V233_PROFILE_UTF8_INVALID") from exc
    lines=raw.splitlines()
    need(not any(line.strip().startswith("actions.precombat") for line in lines)
         and not any(line.partition("=")[0].strip() in
             ("flask","food","potion","augmentation","temporary_enchant",
              "iterations","json2","profileset.") for line in lines),
         "V216_AUTO_F_O_G_SOURCE_PROFILE_ALREADY_HAS_APL_OR_OPTIONS")
    prepared=(raw.rstrip()+"\n"+
              "actions.precombat=flask\n"+
              "actions.precombat+=/snapshot_stats\n")
    encoded=prepared.encode("utf8")
    key=simc_source.digest(original)[:24]
    output="source/v278_v233_precombat_"+key+".simc"
    saved=root/output
    receipt=stage_engine.execute_stage(
        root=root,stage_id="fresh-v278-precombat-"+key,
        stage_version="v233-v269-flask-before-snapshot-v1",
        inputs={"source_profile_sha256":simc_source.digest(original),
                "derived_profile_sha256":simc_source.digest(encoded),
                "connection":"v269-flask-snapshot-precombat"},
        outputs={"profile":output},
        execute=lambda: (saved.parent.mkdir(parents=True,exist_ok=True),
                         saved.write_bytes(encoded)),
        validate=lambda files:(
            not files["profile"].is_symlink() and
            files["profile"].read_bytes()==encoded))
    need(receipt.get("status") in
         ("EXECUTED_AND_SEALED","REUSED_VERIFIED","RECOVERED_VERIFIED"),
         "V216_AUTO_F_O_PRECOMBAT_PROFILE_SEAL_INVALID")
    return str(saved.resolve())



def _prioritize_highest_source_quality_F(worklist):
    """Top source quality per SimC token stem for measurement ONLY.

    No independent same-effect proof, quality admission, or stat mechanism.
    Ambiguous unmatched names and top-quality ties remain distinct.
    """
    need(type(worklist) is list and len(worklist)<=128,
         "V216_F_SOURCE_QUALITY_WORKLIST_INVALID")
    groups={}
    for row in worklist:
        need(type(row) is dict and type(row.get("physical_item_id")) is int
             and row["physical_item_id"]>0
             and type(row.get("simc_input_token")) is str
             and bool(row["simc_input_token"])
             and type(row.get("crafting_quality")) is int
             and row["crafting_quality"]>=0,
             "V216_F_SOURCE_QUALITY_ROW_INVALID")
        token,quality=row["simc_input_token"],row["crafting_quality"]
        suffix="_"+str(quality)
        key=(("stem",token[:-len(suffix)])
             if token.endswith(suffix) and len(token)>len(suffix)
             else ("item",row["physical_item_id"]))
        groups.setdefault(key,[]).append(row)
    top={id(row) for rows in groups.values()
         for row in rows if row["crafting_quality"]==
         max(x["crafting_quality"] for x in rows)}
    selected=[row for row in worklist if id(row) in top]
    need(len(selected)==len(top),"V216_F_QUALITY_ROW_IDENTITY_DRIFT")
    return {"selected":selected,"all_source_candidates":len(worklist),
            "deferred_lower_source_qualities":len(worklist)-len(selected),
            "distinct_source_token_families":len(groups),
            "effect_equivalence_verified":False,
            "quality_and_use_admitted":False,
            "new_native_calls":0,"network_calls":0}



def _auto_default_F_from_sealed_v281_worklist(plan):
    """Pick one representative source-quality F before any Native subprocess.

    Default for the environment B/T baseline, NOT a class preference,
    effect equivalence assertion, or registration of other F variants.
    The original v281 binding and v278 Native remain authoritative.
    """
    out={"status":"AUTO_DEFAULT_F_PHYSICAL_SOURCE_PENDING",
         "selected_physical_items_unadmitted":None,"requires":[],
         "selection_basis":"CANONICAL_HIGHEST_SOURCE_QUALITY_FLASK_FAMILY",
         "not_spec_default_or_stat_optimization":True,
         "simc_quality_effect_unverified":True,
         "environment_ready":False,"new_native_calls":0,"network_calls":0}
    if (type(plan) is not dict or plan.get("status")!=
            "MEASURABLE_PHYSICAL_F_O_CANDIDATES_UNADMITTED"
            or type(plan.get("flask")) is not list or not plan["flask"]):
        out["requires"].append("AUTO_F_SEALED_PHYSICAL_WORKLIST_PENDING")
        return out
    prioritized=_prioritize_highest_source_quality_F(plan["flask"])
    by_family={}
    for item in prioritized["selected"]:
        token,quality=item["simc_input_token"],item["crafting_quality"]
        suffix="_"+str(quality)
        # No guessed family: a token without a verified quality suffix is
        # still measurable by explicit physical ID, not auto selectable.
        if not token.endswith(suffix) or len(token)<=len(suffix):
            continue
        by_family.setdefault(token[:-len(suffix)],[]).append(item)
    # A tied physical product with the same highest-quality SimC token
    # requires an explicit selection rather than an arbitrary ItemID.
    eligible=[item for group in by_family.values() if len(group)==1
              for item in group]
    if not eligible:
        out["requires"].append("AUTO_F_HIGHEST_SOURCE_QUALITY_UNAMBIGUOUS_ITEM_PENDING")
        return out
    selected=min(eligible,key=lambda item:(
        item["simc_input_token"],item["physical_item_id"]))
    out.update({
        "status":"AUTO_DEFAULT_F_SOURCE_ITEM_SELECTED_UNADMITTED",
        "selected_physical_items_unadmitted":{
            "flask_item_id":selected["physical_item_id"],
            "oil_item_ids_by_hand":{}},
        "selected_source_quality":selected["crafting_quality"],
        "selected_source_token":selected["simc_input_token"],
        "all_source_candidates":len(plan["flask"]),
        "highest_source_quality_candidates":
            prioritized["all_source_candidates"]-
            prioritized["deferred_lower_source_qualities"],
        "distinct_flask_families":len(by_family)})
    return out


def _auto_F_native_from_sealed_v281(*,collected,compilation,binary,
                                      kind="flask",max_new_native_calls=8,
                                      selected_item_id=None):
    """Shared sealed F/O Native opt-in; original F entry point is preserved.

    v281 owns exact physical ID/hand/source evidence and v278 owns immutable
    SimC attempts and cache. Measurement is never product admission.
    """
    need(kind in ("flask","temporary_enchant") and
         type(max_new_native_calls) is int and
         0<=max_new_native_calls<=8 and
         (selected_item_id is None or
          (kind=="flask" and type(selected_item_id) is int and
           selected_item_id>0)),
         "V216_AUTO_F_O_NATIVE_BUDGET_OR_KIND_INVALID")
    oil=(kind=="temporary_enchant")
    label="O" if oil else "F"
    family="oil" if oil else "flask"
    out={"status":"AUTO_"+label+"_SOURCE_OR_PROFILE_PENDING","requires":[],
         "per_item":[],"new_native_calls":0,label+"_approved":False,
         "environment_ready":False}
    work=compilation.get("automatic_F_O_measurement_candidates_unadmitted")
    probe=collected.get("fresh_one_spec_physical_G_probe") or {}
    source_profile=(probe.get("profile_path") if type(probe) is dict and
                    type(probe.get("source_stage")) is dict and
                    probe["source_stage"].get("status") in (
                        "EXECUTED_AND_SEALED","REUSED_VERIFIED",
                        "RECOVERED_VERIFIED") else None)
    if compilation.get("status")!=(
            "FRESH_V191_V211_V213_COMPILED_UNADMITTED"):
        out["requires"].append("AUTO_"+label+"_SAME_BUILD_COMPILER_PENDING")
    elif not source_profile:
        out["requires"].append("AUTO_"+label+"_ORIGINAL_V233_PROFILE_PENDING")
    elif type(work) is not dict or not work.get(family):
        out["requires"].append("AUTO_"+label+"_EXACT_PHYSICAL_ITEM_PENDING")
    if out["requires"]:return [],out
    worklist=work[family]
    quality_priority=None
    if not oil and selected_item_id is None:
        quality_priority=_prioritize_highest_source_quality_F(worklist)
        worklist=quality_priority["selected"]
    if selected_item_id is not None:
        # The existing v281 same-build item relation owns exact ID lookup.
        # Do not spend Native calls on unrelated flask effects or quality.
        matches=[row for row in worklist
                 if row["physical_item_id"]==selected_item_id]
        need(len(matches)<=1,"V216_SELECTED_F_DUPLICATE_V281_ITEM_ID")
        if not matches:
            out["requires"].append(
                "AUTO_F_SELECTED_EXACT_ITEM_NOT_IN_V281_SOURCE")
            return [],out
        chosen=matches[0]
        token=chosen["simc_input_token"]
        rank=chosen["crafting_quality"]
        need(type(token) is str and bool(token) and
             type(rank) is int and rank>=0,
             "V216_SELECTED_F_V281_TOKEN_QUALITY_INVALID")
        suffix="_"+str(rank)
        family_key=token[:-len(suffix)] if token.endswith(suffix) else None
        # Preserve existing highest-observed-quality policy: measuring only
        # this item must not make a known lower rank look like the top rank.
        if family_key is not None:
            for other in worklist:
                q=other["crafting_quality"]
                t=other["simc_input_token"]
                need(type(q) is int and q>=0 and type(t) is str,
                     "V216_SELECTED_F_V281_QUALITY_RECORD_INVALID")
                if (t.endswith("_"+str(q)) and
                    t[:-(len(str(q))+1)]==family_key and q>rank):
                    out["requires"].append(
                        "AUTO_F_SELECTED_ITEM_BELOW_OBSERVED_QUALITY")
                    return [],out
        worklist=matches
    # Only create a derived profile when at least one physical item will be
    # measured, never for missing IDs / below-observed-quality selections.
    # The original v233 G input and Native G receipts remain unchanged.
    if worklist and max_new_native_calls>=2:
        source_profile=_sealed_v233_precombat_F_O_profile(
            stage_root=compilation["stage_root"],
            source_profile_path=source_profile)
    rows=[];receipts=[];new=0
    for item in worklist:
        # A v278 paired measurement may launch 2 new subprocesses. Reserve
        # both slots; already-sealed cache hits can be revisited next Build.
        if new+2>max_new_native_calls:break
        item_id=item["physical_item_id"]
        hand=item["selected_hand"] if oil else None
        try:
            source=consumable_simc_relation.resolve_native_input(
                stage_root=compilation["stage_root"],
                relation=collected.get(
                    "fresh_consumable_simc_effect_relation"),
                build=collected["expected_game_build"],
                simc_revision=compilation["simc_revision"],
                kind=kind,item_id=item_id,hand=hand)
            need(type(source) is dict and
                 source.get("simc_input_token")==item["simc_input_token"] and
                 source.get("selected_hand")==hand,
                 "AUTO_"+label+"_EXACT_ITEM_SOURCE_DRIFT")
            native=native_effect_pair.measure(
                stage_root=compilation["stage_root"],
                source_profile_path=source_profile,binary=binary,
                simc_revision=compilation["simc_revision"],
                kind=kind,token=source["simc_input_token"])
        except (consumable_simc_relation.SimCRelationBlocked,
                native_effect_pair.NativePairBlocked,
                OSError,KeyError,ValueError,TypeError) as exc:
            # A subprocess may already have started: never report zero calls
            # after a failure or continue launching further candidates.
            raise EnvironmentBuildBlocked(
                "V216_AUTO_"+label+"_NATIVE_OR_SOURCE_FAILED:"
                +str(exc).split(":",1)[0]) from exc
        count=native.get("new_native_calls")
        need(type(count) is int and 0<=count<=2,
             "AUTO_"+label+"_NATIVE_CALL_COUNT_INVALID")
        new+=count
        rows.append({**native,"physical_item_native_source_unadmitted":source})
        receipts.append({"physical_item_id":item_id,"selected_hand":hand,
                         "status":native["status"],"new_native_calls":count,
                         "cache_hit":count==0,
                         label+"_candidate_unadmitted":
                             native.get(label+"_candidate_unadmitted"),
                         **({"native_error":native.get("native_error"),
                             "native_log_excerpt":
                                 native.get("native_log_excerpt")}
                            if native.get("native_error") else {})})
    out.update({"status":"AUTO_"+label+"_NATIVE_MEASURED_SOURCE_ONLY",
                "total_source_candidates":len(worklist),
                 **({"all_source_candidate_count":quality_priority["all_source_candidates"],
                     "deferred_lower_quality_measurements":quality_priority["deferred_lower_source_qualities"],
                     "distinct_F_source_token_families":quality_priority["distinct_source_token_families"],
                     "source_quality_priority_only_not_policy_A":True}
                    if quality_priority is not None else {}),
                "attempted":len(receipts),
                "remaining":len(worklist)-len(receipts),
                **({"selected_exact_item_id":selected_item_id,
                    "all_source_candidate_count":len(work[family])}
                   if selected_item_id is not None else {}),
                "new_native_calls":new,"per_item":receipts,
                "requires":[("AUTO_O_QUALITY_WEAPON_HAND_AND_BUDGET_PROOF_PENDING"
                             if oil else
                             "AUTO_F_HIGHEST_QUALITY_ITEM_AND_NUMERIC_BUDGET_SOURCE_PENDING")]+
                    (["AUTO_"+label+"_NEXT_MEASUREMENT_BATCH_PENDING"]
                     if len(receipts)<len(worklist) else [])})
    return rows,out


def _stage_source_environment_only(*, compilation, preflight,
                                   target_ilevel, selected_numeric=None):
    """Seal a versioned environment UNIT with original v217; no DPS plan.

    All original same-build v191/v211/v213 and v216 preflight authentication
    already ran before this call. The artifact is always NOT INSTALLED.
    Different numeric source receipts get different content-addressed paths,
    never silently overwrite an earlier build stage or its cache.
    """
    source=pathlib.Path(compilation["source_catalog_path"]).resolve()
    stage_root=pathlib.Path(compilation["stage_root"]).resolve()
    need(source.is_file() and not source.is_symlink() and
         stage_root.is_dir() and source.is_relative_to(stage_root),
         "V216_ENVIRONMENT_STAGE_SOURCE_OUTSIDE_SEALED_WORKSPACE")
    catalog,catalog_sha=environment_manifest.read_json(source)
    document=environment_manifest.compile_fresh_source_environment(
        source_catalog=catalog,source_artifact_sha256=catalog_sha,
        preflight=preflight,compilation=compilation,
        target_ilevel=target_ilevel,selected_numeric=selected_numeric)
    key=document["manifest_sha256"][:20]
    stage_id="fresh-v212-environment-"+key
    output="fresh_source/v212_environment_"+key+".json"
    path=stage_root/output
    encoded=environment_manifest.canonical(document)+"\n"
    def execute():
        path.parent.mkdir(parents=True,exist_ok=True)
        need(not path.is_symlink(),"V216_ENVIRONMENT_STAGE_OUTPUT_SYMLINK")
        need(not path.exists(),"V216_ENVIRONMENT_STAGE_OUTPUT_UNRECEIPTED")
        path.write_text(encoded,encoding="utf8")
    def validate(files):
        saved=files["environment"]
        if saved.is_symlink() or saved.read_text(encoding="utf8")!=encoded:
            return False
        return environment_manifest.verify_fresh_source_environment(
            json.loads(saved.read_text(encoding="utf8")))
    sealed=stage_engine.execute_stage(
        root=stage_root,stage_id=stage_id,
        stage_version="v212-fresh-source-environment-1",
        inputs={"manifest_sha256":document["manifest_sha256"],
                "v216_preflight_sha256":preflight["preflight_sha256"]},
        outputs={"environment":output},execute=execute,validate=validate)
    return {"schema":environment_manifest.FRESH_SEASON_STAGE_SCHEMA,
            "status":document["status"],
            "manifest_sha256":document["manifest_sha256"],
            "original_v216_preflight_sha256":preflight["preflight_sha256"],
            "stage_status":sealed["status"],
            "stage_receipt_sha256":sealed["receipt_sha256"],
            "stage_output_path":str(path),
            "environment_ready":False,"environment_installed":False,
            "dps_optimization_required":False,
            "new_native_calls":0,"network_calls":0}



def _future_target_five_socket_plan(intrinsic_counts):
    """Propose target sockets; NEVER authenticate added sockets as intrinsic."""
    if (type(intrinsic_counts) is not dict or not intrinsic_counts or
            any(type(k) is not str or type(v) is not int or v<0 or v>3
                for k,v in intrinsic_counts.items())):
        return {"status":"J_ORIGINAL_INTRINSIC_SOCKET_SOURCE_PENDING",
                "can_place_four":False,"planned_socket_counts":None,
                "provisional_added_by_slot":{},
                "additional_source_verified":False,
                "new_native_calls":0,"network_calls":0}
    original=dict(intrinsic_counts)
    planned=dict(original)
    missing=max(0,5-sum(original.values()))
    additions={}
    # Slot feasibility is ONLY a proposal. Current-season item/use source
    # has to verify additions separately; original v232 counts remain exact.
    for slot in ("wrists","waist","head"):
        if missing<=0:break
        if slot in planned and planned[slot]==0:
            planned[slot]=1
            additions[slot]=1
            missing-=1
    can_place=missing==0
    return {
        "status":("FUTURE_FIVE_SOCKET_LAYOUT_SOURCE_ONLY"
                  if can_place else "FUTURE_FIVE_SOCKET_LAYOUT_INSUFFICIENT"),
        "can_place_four":can_place,
        "original_intrinsic_total":sum(original.values()),
        "planned_socket_total":sum(planned.values()),
        "planned_socket_counts":planned if can_place else None,
        "provisional_added_by_slot":additions,
        "additional_source_verified":not bool(additions),
        "new_native_calls":0,"network_calls":0}


def _existing_v280_season_socket_item_source(collected, compilation):
    """Read the SAME sealed item-use join for socket-item discovery hints.

    No extra CSV/HTTP, Native, separate effect interpreter, or J admission.
    Names and on-use spell links only narrow the existing source inspection;
    they cannot establish season-specific use rights or bonus-slot ownership.
    """
    out={"schema":"v216_existing_v280_socket_item_source_v1",
         "status":"SAME_BUILD_SOCKET_ITEM_SOURCE_PENDING",
         "physical_candidates_unadmitted":[],"candidate_count":0,
         "source_sha256":None,"v280_stage_receipt_sha256":None,
         "same_build_source":False,"slot_application_verified":False,
         "j_budget_admitted":False,"environment_ready":False,
         "new_native_calls":0,"network_calls":0}
    if type(collected) is not dict or type(compilation) is not dict:
        return out
    entry=collected.get("fresh_consumable_item_spell_source") or {}
    stage=entry.get("source_stage") or {}
    if (entry.get("status")!="ITEM_USE_SPELL_SOURCE_JOINED_UNADMITTED"
            or stage.get("status") not in
                ("EXECUTED_AND_SEALED","REUSED_VERIFIED","RECOVERED_VERIFIED")
            or type(stage.get("receipt_sha256")) is not str or
            season_budget_contract.SHA.fullmatch(
                stage["receipt_sha256"]) is None):
        return out
    root=pathlib.Path(compilation.get("stage_root") or "").resolve()
    filename=entry.get("candidate_path")
    need(type(filename) is str and bool(filename) and root.is_dir() and
         not root.is_symlink(),"V216_SOCKET_V280_STAGE_ROOT_REQUIRED")
    candidate=pathlib.Path(filename)
    need(candidate.is_file() and not candidate.is_symlink() and
         candidate.resolve().is_relative_to(root) and
         candidate.resolve().parent==root/"source" and
         0<candidate.stat().st_size<=10_000_000,
         "V216_SOCKET_V280_SEALED_CANDIDATE_REQUIRED")
    raw=candidate.read_bytes()
    doc=json.loads(raw)
    build=collected.get("expected_game_build")
    meta=doc.get("item_use_spell_join") or {}
    source=doc.get("source") or {}
    need(doc.get("schema")==consumable_item_candidates.SCHEMA and
         source.get("wago_snapshot_build")==build and
         meta.get("schema")==item_spell_bridge.SCHEMA and
         meta.get("game_build")==build and meta.get("source_only") is True
         and doc.get("automatic_ui_promotion") is False and
         type(doc.get("items")) is list and len(doc["items"])<=50000,
         "V216_SOCKET_V280_SAME_BUILD_ITEM_JOIN_DRIFT")
    candidates=[]
    for item in doc["items"]:
        if type(item) is not dict:
            continue
        name=item.get("name_enUS")
        effect=item.get("item_effect_source") or {}
        if (type(name) is str and name.casefold().endswith("jewelbinder")
                and type(item.get("item_id")) is int and item["item_id"]>0
                and effect.get("status")==
                    "EXACT_DB2_ITEM_TO_ON_USE_SPELL_SOURCE_ONLY"
                and type(effect.get("on_use_spell_ids")) is list
                and bool(effect["on_use_spell_ids"])
                and all(type(i) is int and i>0
                        for i in effect["on_use_spell_ids"])):
            candidates.append({
                "physical_item_id":item["item_id"],
                "name_from_same_build":name,
                "observed_on_use_spell_ids":
                    sorted(set(effect["on_use_spell_ids"])),
                "expansion_id":item.get("expansion_id"),
                "source_only":True})
    candidates.sort(key=lambda x:(x["physical_item_id"],
                                  x["name_from_same_build"]))
    return {**out,
        "status":("SAME_BUILD_SOCKET_ITEM_USE_CANDIDATES_UNADMITTED"
                  if candidates else
                  "NO_MATCH_IN_EXISTING_V280_CONSUMABLE_SCOPE"),
        "physical_candidates_unadmitted":candidates,
        "candidate_count":len(candidates),
        "source_sha256":digest(raw),
        "v280_stage_receipt_sha256":stage["receipt_sha256"],
        "same_build_source":True}


def _fresh_default_intrinsic_gem_layout_from_source(*, collected,
                                                    selected_roles,
                                                    target_ilevel,
                                                    candidate_socket_counts=None,
                                                    simc_declared_socket_counts=None):
    """Stage one existing special + ordinary gems on original v232 slots.

    A separate prospective slot plan can add *unadmitted* bonus slots.
    Original v232 intrinsic counts remain unchanged, and the existing
    downstream J socket owner detects these extra slots and keeps
    authoritative J pending until applicable same-season proof is available.
    No new Native, gem effect engine or assumed physical sockets.
    """
    source=collected.get("fresh_one_spec_simc_representative") or {}
    stage=source.get("source_stage") or {}
    need(type(selected_roles) is dict and set(selected_roles)=={
        "special_gem_id","ordinary_gem_ids"} and
         type(selected_roles["special_gem_id"]) is int and
         selected_roles["special_gem_id"]>0 and
         type(selected_roles["ordinary_gem_ids"]) is list and
         source.get("status")==
             "FRESH_ONE_SPEC_SIMC_G_SOURCE_CANDIDATE_PENDING_NATIVE"
         and stage.get("status") in (
             "EXECUTED_AND_SEALED","REUSED_VERIFIED","RECOVERED_VERIFIED")
         and type(stage.get("receipt_sha256")) is str and
         season_budget_contract.SHA.fullmatch(
             stage["receipt_sha256"]) is not None,
         "V216_DEFAULT_GEM_ORIGINAL_V232_SEALED_SOURCE_REQUIRED")
    path=pathlib.Path(source.get("candidate_path") or "")
    declared=(stage.get("output_paths") or {}).get("candidate")
    need(type(declared) is str and
         declared.startswith("source/") and
         path.is_file() and not path.is_symlink() and
         path.parent.name=="source" and
         path.resolve()==(path.parent.parent/declared).resolve() and
         0<path.stat().st_size<=10_000_000,
         "V216_DEFAULT_GEM_ORIGINAL_V232_CANDIDATE_REQUIRED")
    original=json.loads(path.read_text("utf8"))
    receipt=original.get("receipt_sha256")
    need(original.get("schema")==simc_representative.SCHEMA and
         original.get("game_build")==collected.get("expected_game_build") and
         original.get("target_ilevel")==target_ilevel and
         original.get("environment_ready") is False and
         type(receipt) is str and
         receipt==simc_source.digest(simc_source.canonical({
             k:v for k,v in original.items()
             if k!="receipt_sha256"}).encode("utf8")),
         "V216_DEFAULT_GEM_ORIGINAL_V232_CANDIDATE_IDENTITY_DRIFT")
    ids=original.get("selected_G_slot_ids")
    counts=original.get(
        "selected_intrinsic_socket_count_by_slot_source_only")
    need(type(ids) is dict and bool(ids) and
         type(counts) is dict and set(ids)==set(counts) and
         counts==source.get(
             "intrinsic_socket_counts_by_selected_slot_source_only") and
         sum(counts.values())==
             source.get("intrinsic_socket_total_source_only") and
         len(counts)==source.get("selected_slot_count") and
         all(type(i) is int and i>0 for i in ids.values()) and
         type(target_ilevel) is int and 1<=target_ilevel<=1000,
         "V216_DEFAULT_GEM_V232_PHYSICAL_SLOTS_DRIFT")
    selected=selected_roles["ordinary_gem_ids"]
    special=selected_roles["special_gem_id"]
    need(candidate_socket_counts is None or
         simc_declared_socket_counts is None,
         "V216_SOCKET_SOURCE_SIMC_INTENT_CONFLICT")
    proposed=(simc_declared_socket_counts if
              simc_declared_socket_counts is not None else
              counts if candidate_socket_counts is None else
              candidate_socket_counts)
    if simc_declared_socket_counts is not None:
        need(type(proposed) is dict and set(proposed)==set(ids) and
             all(type(n) is int and 0<=n<=3 for n in proposed.values()) and
             sum(proposed.values())>=5,
             "V216_SIMC_DECLARED_FULL_SOCKET_PLAN_INVALID")
    if candidate_socket_counts is not None:
        # Never mutate the original v232 source: these are only prospective
        # slots, and _fresh_selected_J_intrinsic_socket_source will see
        # additions and keep official J pending.
        need(type(proposed) is dict and set(proposed)==set(counts) and
             all(type(v) is int and counts[k]<=v<=3
                 for k,v in proposed.items()) and
             all(proposed[k]==counts[k] or
                 (k in ("head","waist","wrists") and
                  counts[k]==0 and proposed[k]==1)
                 for k in counts) and sum(proposed.values())>=5,
             "V216_FUTURE_SOCKET_PLAN_ORIGINAL_V232_DRIFT")
    plan=physical_gems.intrinsic_source_plan(
        intrinsic_socket_counts=proposed,
        special_gem_id=special,ordinary_gem_ids=selected,
        source_observed_gem_item_ids=sorted(set(selected)|{special}),
        need=need)
    rows={slot:{"slot":slot,"item_id":ids[slot],
                "ilevel":target_ilevel,"options":{}}
          for slot in sorted(ids)}
    _,layout=physical_gems.arrange(rows,plan,need)
    # Compare the staged physical layout against the proposed target counts,
    # NOT the smaller original intrinsic counts. The downstream source owner
    # independently compares to original v232 and flags bonus-slot proof.
    need(layout["socket_total"]==sum(proposed.values()) and
         layout["ordinary_count"]==sum(proposed.values())-1 and
         layout["special_gem_id"]==special and
         layout["environment_ready"] is False,
         "V216_DEFAULT_GEM_V271_INTRINSIC_LAYOUT_DRIFT")
    if simc_declared_socket_counts is not None:
        layout["simc_declared_full_socket_policy"]=(
            "FULL_GEM_ID_PROFILE_SIMC_OWNS")
    return layout


def _fresh_selected_J_intrinsic_socket_source(*, collected, preflight,
                                               compilation):
    """Join already sealed v232 intrinsic sockets to v271, never approve J."""
    layout=preflight.get("physical_gem_layout_unadmitted")
    if layout is None:
        return None
    need(type(layout) is dict and layout.get("schema")==physical_gems.SCHEMA
         and layout.get("status")==
             "PHYSICAL_GEMS_STAGED_SOURCE_AND_SOCKET_PROOFS_PENDING"
         and type(layout.get("ordinary_gem_ids")) is list
         and type(layout.get("socket_counts")) is dict
         and layout.get("ordinary_count")==len(layout["ordinary_gem_ids"])
         and layout.get("socket_total")==len(layout["ordinary_gem_ids"])+1
         and sum(layout["socket_counts"].values())==layout["socket_total"]
         and layout["socket_counts"].get(layout["special_slot"],0)>0,
         "V216_J_ORIGINAL_V271_LAYOUT_REQUIRED")
    out={"schema":"v216_selected_J_intrinsic_source_v1",
         "status":"J_V232_INTRINSIC_SOURCE_PENDING",
         "selected_socket_counts":dict(layout["socket_counts"]),
         "intrinsic_socket_counts_by_slot":None,
         "additional_socket_proof_required_by_slot":None,
         "v232_stage_receipt_sha256":None,"observed_J_unadmitted":None,
         "game_socket_legal_verified":False,"J_quality_and_effect_verified":False,
         "J_approved":False,"environment_ready":False,
         "new_native_calls":0,"network_calls":0}
    source=collected.get("fresh_one_spec_simc_representative") or {}
    stage=source.get("source_stage") or {}
    if (source.get("status")!=
            "FRESH_ONE_SPEC_SIMC_G_SOURCE_CANDIDATE_PENDING_NATIVE"
        or stage.get("status") not in (
            "EXECUTED_AND_SEALED","REUSED_VERIFIED","RECOVERED_VERIFIED")):
        return out
    counts=source.get("intrinsic_socket_counts_by_selected_slot_source_only")
    need(preflight.get("schema")==FRESH_SOURCE_PREFLIGHT_SCHEMA
         and preflight.get("game_build")==collected.get("expected_game_build")
         and preflight.get("simc_revision")==compilation.get("simc_revision")
         and preflight.get("environment_ready") is False
         and type(stage.get("receipt_sha256")) is str
         and season_budget_contract.SHA.fullmatch(
             stage["receipt_sha256"]) is not None
         and type(counts) is dict and bool(counts)
         and all(type(slot) is str and type(n) is int and 0<=n<=3
                 for slot,n in counts.items())
         and source.get("selected_slot_count")==len(counts)
         and source.get("intrinsic_socket_total_source_only")==sum(counts.values())
         and source.get("added_socket_bonus_and_game_permission_not_proven")
             is True,
         "V216_J_V232_ORIGINAL_SEALED_SOURCE_DRIFT")
    extra={slot:n-counts.get(slot,0)
           for slot,n in sorted(layout["socket_counts"].items())
           if n>counts.get(slot,0)}
    j=preflight.get("physical_gem_J_arithmetic_unadmitted")
    if j is not None:
        need(j.get("status")=="PHYSICAL_GEM_J_ARITHMETIC_UNADMITTED"
             and j.get("physical_gem_item_ids")==layout["ordinary_gem_ids"]
             and type(j.get("J_candidate_unadmitted")) is int
             and j.get("environment_ready") is False,
             "V216_J_V271_NUMERIC_SOURCE_DRIFT")
    declared=layout.get("simc_declared_full_socket_policy")
    need(declared in (None,"FULL_GEM_ID_PROFILE_SIMC_OWNS"),
         "V216_J_SIMC_DECLARED_SOCKET_POLICY_INVALID")
    return {**out,
            "status":("J_SIMC_DECLARED_FULL_GEM_PROFILE_SOURCE_ONLY"
                      if declared else
                      "J_INTRINSIC_COUNTS_BOUND_SOURCE_ONLY" if not extra else
                      "J_ADDITIONAL_SOCKET_SOURCE_PROOF_PENDING"),
            "intrinsic_socket_counts_by_slot":dict(counts),
            "additional_socket_proof_required_by_slot":extra,
            "v232_stage_receipt_sha256":stage["receipt_sha256"],
            "observed_J_unadmitted":(
                j["J_candidate_unadmitted"] if j is not None else None)}


def _fresh_source_owner_packaged_nominal_J(*, preflight, layout, link, j):
    """Bind the same package bytes already selected by v113 to v221/v271.

    Source-only; the original v230 quality and v232 socket owners must still
    establish admission. Do not read a historical fallback or infer zero.
    """
    if j.get("rating_origin")!="SEASON_NOMINAL_PER_ITEM_TOTAL_SOURCE":
        return None
    build=preflight["game_build"]
    stored=physical_gems.load_packaged_season_nominal_source(
        game_build=build,need=need)
    if stored is None:
        return None
    need(j.get("nominal_source_sha256")==stored["source_sha256"] and
         j.get("nominal_source_game_build")==build and
         type(layout.get("ordinary_gem_ids")) is list and
         type(layout.get("special_gem_id")) is int,
         "V216_NOMINAL_J_PACKAGED_SOURCE_SHA_OR_BUILD_DRIFT")
    matched=physical_gems.nominal_four_stat_from_season_source(
        source=stored,game_build=build,
        socket_total=layout["socket_total"],
        special_gem_id=layout["special_gem_id"],need=need)
    ids=layout["ordinary_gem_ids"]
    special=layout["special_gem_id"]
    needs=set(ids+[special])
    need(ids==matched["ordinary_gem_ids"] and
         j.get("J_candidate_unadmitted")==matched["J_candidate_unadmitted"]
         and j.get("physical_gem_item_ids")==ids and
         j.get("status")=="PHYSICAL_GEM_J_ARITHMETIC_UNADMITTED"
         and j.get("J_accounting_policy")==
             "SUM_SELECTED_ORDINARY_GEM_RATINGS"
         and j.get("special_gem_count_in_J")==0
         and j.get("source_v221_stage_receipt_sha256")==
             link.get("v221_stage_receipt_sha256")
         and link.get("same_build_gem_item_join_only") is True
         and link.get("special_gem_item_id")==special
         and link.get("selected_item_ids")==sorted(needs)
         and type(link.get("v221_stage_receipt_sha256")) is str
         and season_budget_contract.SHA.fullmatch(
             link["v221_stage_receipt_sha256"]) is not None,
         "V216_NOMINAL_J_PACKAGED_V221_LAYOUT_OR_VALUE_DRIFT")
    original={
        "kind":"nominal_ordinary_gem_J",
        "game_build":build,
        "source_catalog_manifest_sha256":
            preflight["source_catalog_manifest_sha256"],
        "v221_stage_receipt_sha256":link["v221_stage_receipt_sha256"],
        "season_nominal_source_sha256":stored["source_sha256"],
        "special_gem_item_id":special,
        "ordinary_gem_item_ids":list(ids),
        "per_item_nominal_rating":dict(matched["rating_by_id"]),
        "observed_quality_rank_by_id":dict(
            stored["observed_quality_rank_by_id"])}
    return {
        "rating":matched["J_candidate_unadmitted"],
        "source_identity_sha256":digest(canonical(original).encode("utf8")),
        **original,
        "numeric_source_owner":"PACKAGED_SEASON_NOMINAL_PER_ITEM",
        "special_gem_contributes_to_J":False,
        "highest_available_quality_verified":False,
        "real_socket_source_verified":False,
        "nominal_J_not_simc_effective_delta":True}


def _fresh_source_owner_selected_J_F_numeric(*, preflight, compilation,
                                             selected_physical_items):
    """Bind original J/F numerics for an INTERNAL quality/source owner.

    J is the nominal sum of ordinary gem ratings from the original sealed
    v266 join. F is the selected physical v281 item + v278 SimC paired
    static rating. Neither a source-only observation nor a self-computed
    digest proves highest available quality, use conditions or user READY.
    A provider must still authenticate those facts before returning v222
    trusted components. No additional Native, DB read or effect engine.
    """
    out={"schema":"v216_original_selected_J_F_numeric_owner_inputs_v1",
         "status":"SELECTED_J_F_NUMERIC_SOURCE_PENDING",
         "J":None,"F":None,"missing":[],
         "quality_and_use_scope_verified":False,
         "v222_components_admitted":False,
         "environment_ready":False,"new_native_calls":0,
         "network_calls":0}
    if (type(preflight) is not dict or
            preflight.get("schema")!=FRESH_SOURCE_PREFLIGHT_SCHEMA or
            type(compilation) is not dict or
            compilation.get("status")!=
                "FRESH_V191_V211_V213_COMPILED_UNADMITTED"):
        out["missing"].append("ORIGINAL_V216_SOURCE_COMPILATION_PENDING")
        return out
    need(preflight.get("simc_revision")==compilation.get("simc_revision") and
         preflight.get("environment_ready") is False,
         "V216_JF_OWNER_ORIGINAL_COMPILATION_IDENTITY_DRIFT")
    j=preflight.get("physical_gem_J_arithmetic_unadmitted")
    layout=preflight.get("physical_gem_layout_unadmitted")
    link=preflight.get("selected_v221_gem_item_relation_unadmitted")
    original=preflight.get("physical_gem_raw_rating_by_id_unadmitted")
    if (type(j) is dict and type(layout) is dict and
            type(link) is dict and type(original) is dict and
            j.get("rating_origin")=="V266_RAW_SAME_BUILD_EFFECT_POINTS_ONLY"):
        ids=layout.get("ordinary_gem_ids")
        special=layout.get("special_gem_id")
        need(type(ids) is list and bool(ids) and len(ids)<=64
             and all(type(x) is int and x>0 for x in ids)
             and type(special) is int and special>0 and special not in ids
             and j.get("physical_gem_item_ids")==ids
             and j.get("status")=="PHYSICAL_GEM_J_ARITHMETIC_UNADMITTED"
             and j.get("J_accounting_policy")==
                 "SUM_SELECTED_ORDINARY_GEM_RATINGS"
             and j.get("special_gem_count_in_J")==0
             and set(original)==set(str(x) for x in ids)
             and all(type(x) is int and x>0 for x in original.values())
             and sum(original[str(x)] for x in ids)==
                 j.get("J_candidate_unadmitted")
             and link.get("same_build_gem_item_join_only") is True
             and link.get("special_gem_item_id")==special
             and link.get("selected_item_ids")==sorted(set(ids+[special]))
             and type(link.get("enchant_source_sha256")) is str
             and season_budget_contract.SHA.fullmatch(
                 link["enchant_source_sha256"]) is not None
             and j.get("source_enchant_sha256")==
                 link["enchant_source_sha256"]
             and type(link.get("v221_stage_receipt_sha256")) is str
             and season_budget_contract.SHA.fullmatch(
                 link["v221_stage_receipt_sha256"]) is not None
             and j.get("source_v221_stage_receipt_sha256")==
                 link["v221_stage_receipt_sha256"],
             "V216_JF_OWNER_ORIGINAL_V266_ORDINARY_NUMERIC_DRIFT")
        src={"kind":"nominal_ordinary_gem_J",
             "game_build":preflight["game_build"],
             "source_catalog_manifest_sha256":
                 preflight["source_catalog_manifest_sha256"],
             "v221_stage_receipt_sha256":link["v221_stage_receipt_sha256"],
             "v266_enchant_source_sha256":link["enchant_source_sha256"],
             "special_gem_item_id":special,"ordinary_gem_item_ids":list(ids),
             "per_item_nominal_rating":dict(original)}
        out["J"]={"rating":j["J_candidate_unadmitted"],
                  "source_identity_sha256":
                      digest(canonical(src).encode("utf8")),
                  **src,"special_gem_contributes_to_J":False,
                  "highest_available_quality_verified":False,
                  "real_socket_source_verified":False,
                  "nominal_J_not_simc_effective_delta":True}
    elif (type(j) is dict and type(layout) is dict and
          type(link) is dict and
          j.get("rating_origin")=="SEASON_NOMINAL_PER_ITEM_TOTAL_SOURCE"):
        nominal=_fresh_source_owner_packaged_nominal_J(
            preflight=preflight,layout=layout,link=link,j=j)
        if nominal is None:
            out["missing"].append(
                "J_PACKAGED_SAME_BUILD_NOMINAL_SOURCE_PENDING")
        else:
            out["J"]=nominal
    else:
        out["missing"].append(
            "J_ORIGINAL_NOMINAL_NUMERIC_OR_HIGHEST_QUALITY_SOURCE_PENDING")
    if type(selected_physical_items) is dict:
        chosen=selected_physical_items.get("flask_item_id")
        linked=compilation.get(
            "selected_physical_F_O_budget_link_unadmitted")
        observed=(linked.get("matched_f")
                  if type(linked) is dict and
                     linked.get("selected_physical_items")==
                         selected_physical_items else None)
        if type(observed) is dict and observed.get("physical_item_id")==chosen:
            vec=observed.get("static_CHMV_vector")
            receipts=observed.get("simc_native_receipt_sha256")
            need(type(chosen) is int and chosen>0
                 and type(vec) is dict and
                 set(vec)==set(season_budget_contract.STATS)
                 and all(type(x) is int and x>=0 for x in vec.values())
                 and sum(vec.values())>0
                 and observed.get("rating")==sum(vec.values())
                 and type(observed.get("crafting_quality")) is int
                 and observed["crafting_quality"]>=0
                 and type(observed.get("simc_input_token")) is str
                 and bool(observed["simc_input_token"])
                 and type(observed.get("source_candidate_sha256")) is str
                 and season_budget_contract.SHA.fullmatch(
                     observed["source_candidate_sha256"]) is not None
                 and type(receipts) is list and len(receipts)==2
                 and all(type(x) is str and
                         season_budget_contract.SHA.fullmatch(x) is not None
                         for x in receipts),
                 "V216_JF_OWNER_SELECTED_V278_SIMC_NUMBER_OR_ID_DRIFT")
            source={"kind":"selected_flask_SimC_static_F",
                    "game_build":preflight["game_build"],
                    "simc_revision":preflight["simc_revision"],
                    "physical_item_id":chosen,
                    "crafting_quality":observed["crafting_quality"],
                    "simc_input_token":observed["simc_input_token"],
                    "source_candidate_sha256":
                        observed["source_candidate_sha256"],
                    "native_pair_receipt_sha256":list(receipts),
                    "static_CHMV_vector":dict(vec)}
            out["F"]={"rating":sum(vec.values()),
                      "source_identity_sha256":
                          digest(canonical(source).encode("utf8")),
                      **source,"highest_available_quality_verified":False,
                      "source_owner_admitted":False}
        else:
            out["missing"].append("F_SELECTED_PHYSICAL_V281_V278_NUMERIC_PENDING")
    else:
        out["missing"].append("F_EXPLICIT_SELECTED_PHYSICAL_ITEM_PENDING")
    if out["J"] is not None and out["F"] is not None:
        out["status"]="SELECTED_J_F_NUMERIC_SOURCES_BOUND_UNADMITTED"
    return out



def _fresh_source_owner_observed_J_F_quality(*, preflight, compilation,
                                             owner_numeric):
    """Expose bounded observed-effect maximum to the original source owner.

    Highest comparable effect DISCOVERED is enough as a quality preference,
    not proof of an exhaustive market or a new v220 admission receipt.
    Selected item IDs, original source receipts and exact numerical budget
    still need to match. No extra Native, DB scan or use-condition Gate.
    """
    result={
        "schema":"v216_original_selected_J_F_quality_observations_v1",
        "status":"SELECTED_J_F_QUALITY_SCOPE_PENDING",
        "J":None,"F":None,
        "missing":[],
        "highest_available_quality_verified":False,
        "same_effect_and_use_conditions_verified":False,
        "official_budget_admitted":False,
        "environment_ready":False,
        "new_native_calls":0,"network_calls":0}
    if type(owner_numeric) is not dict or (
            type(preflight) is not dict or type(compilation) is not dict):
        result["missing"].append("ORIGINAL_J_F_NUMERIC_AND_SEASON_SOURCE_PENDING")
        return result
    j=owner_numeric.get("J")
    link=preflight.get("selected_v221_gem_item_relation_unadmitted")
    if type(j) is dict and type(link) is dict:
        original=link.get("selected_simc_gem_quality_source_unadmitted")
        comparison=link.get("gem_policy_A_source_and_quality_unadmitted")
        if (type(original) is dict and
                original.get("quality_source_authenticated") is True and
                type(original.get("v230_stage_receipt_sha256")) is str and
                season_budget_contract.SHA.fullmatch(
                    original["v230_stage_receipt_sha256"]) is not None and
                type(comparison) is dict and
                comparison.get("schema")==
                    "v216_selected_gem_quality_policy_A_preview_v1"):
            all_ids=link["selected_item_ids"]
            rows=original.get("selected_item_quality_unadmitted")
            need(original.get("game_build")==preflight.get("game_build") and
                 original.get("simc_revision")==preflight.get("simc_revision") and
                 original.get("selected_item_ids")==all_ids and
                 type(rows) is list and len(rows)==len(all_ids) and
                 [r.get("item_id") for r in rows]==all_ids and
                 all(type(r.get("crafting_quality")) is int and
                     r["crafting_quality"]>=0 for r in rows) and
                 comparison.get("game_build")==preflight.get("game_build") and
                 comparison.get("simc_revision")==preflight.get("simc_revision"),
                 "V216_JF_QUALITY_ORIGINAL_V230_IDENTITY_DRIFT")
            by_id={r["item_id"]:r["crafting_quality"] for r in rows}
            ordinary=j["ordinary_gem_item_ids"]
            groups=comparison.get("quality_source_groups_unadmitted")
            need(type(groups) is list,
                 "V216_JF_QUALITY_ORIGINAL_V220_GROUPS_REQUIRED")
            bounded=[]
            for group in groups:
                ids=group.get("observed_item_ids")
                ranks=group.get("observed_crafting_quality_ranks")
                need(type(ids) is list and type(ranks) is list and
                     len(ids)==len(ranks) and len(set(ids))==len(ids) and
                     all(i in by_id and by_id[i]==q
                         for i,q in zip(ids,ranks)) and
                     (group.get("highest_observed_quality_item_id_unadmitted")
                         in ids or
                      group.get("highest_observed_quality_item_id_unadmitted")
                         is None),
                     "V216_JF_QUALITY_ORIGINAL_V220_OBSERVED_RANK_DRIFT")
                if any(i in ordinary for i in ids):
                    bounded.append({
                        "observed_item_ids":list(ids),
                        "observed_crafting_quality_ranks":list(ranks),
                        "highest_observed_item_id_source_only":
                            group.get(
                                "highest_observed_quality_item_id_unadmitted"),
                        "same_raw_four_stat_vector_source_only":
                            group.get("same_raw_four_stat_vector_source_only")
                                is True,
                        "best_discovered_effect_item_id_source_only":
                            group.get("highest_observed_effect_item_id_source_only",
                                      group.get("highest_observed_quality_item_id_unadmitted")),
                        "comparable_effect_source_only":
                            group.get("observed_effect_vectors_comparable_source_only")
                                is True})
            nominal_ranks=j.get("observed_quality_rank_by_id")
            nominal_bound=(j.get("numeric_source_owner")==
                           "PACKAGED_SEASON_NOMINAL_PER_ITEM")
            # The original v230 sealed item metadata supplies the quality
            # value. The curated same-build highest-observed reference
            # supplies the expected rank; raw v266 effect points are not used.
            quality_matched=(
                nominal_bound and
                type(nominal_ranks) is dict and
                set(nominal_ranks)==set(str(i) for i in ordinary) and
                all(by_id[i]==nominal_ranks[str(i)] for i in ordinary))
            result["J"]={
                "ordinary_gem_item_ids":list(ordinary),
                "selected_nominal_quality_matches_v230":quality_matched,
                "season_nominal_source_sha256":(
                    j.get("season_nominal_source_sha256")
                    if nominal_bound else None),
                "observed_crafting_quality_by_item_id":{
                    str(item_id):by_id[item_id] for item_id in sorted(set(ordinary))},
                "v230_stage_receipt_sha256":
                    original["v230_stage_receipt_sha256"],
                "v221_stage_receipt_sha256":link["v221_stage_receipt_sha256"],
                "same_enchant_quality_groups_source_only":bounded,
                "ranked_only_within_selected_source_items":True,
                "highest_available_quality_verified":False,
                "same_effect_and_use_conditions_verified":False,
                "real_socket_proof_required":True}
        else:
            result["missing"].append(
                "J_SELECTED_V230_SEALED_QUALITY_SOURCE_PENDING")
    else:
        result["missing"].append("J_SELECTED_NOMINAL_SOURCE_PENDING")
    f=owner_numeric.get("F")
    choices=compilation.get(
        "observed_quality_weapon_choices_unadmitted")
    if type(f) is dict and type(choices) is dict:
        if choices.get("schema")==(
                "v216_existing_flask_quality_and_weapon_mask_join_v1"):
            need(choices.get("game_build")==preflight.get("game_build") and
                 choices.get("simc_revision")==preflight.get("simc_revision") and
                 type(choices.get(
                     "flask_quality_groups_observed_unadmitted")) is list,
                 "V216_JF_QUALITY_ORIGINAL_F_SAME_BUILD_DRIFT")
            found=[]
            for group in choices["flask_quality_groups_observed_unadmitted"]:
                ids=group.get("observed_item_ids")
                ranks=group.get("observed_qualities")
                need(type(ids) is list and type(ranks) is list and
                     len(ids)==len(ranks) and len(set(ids))==len(ids) and
                     all(type(i) is int and i>0 and
                         type(q) is int and q>=0
                         for i,q in zip(ids,ranks)) and
                     (group.get("highest_observed_quality_item_id_unadmitted")
                         in ids or
                      group.get("highest_observed_quality_item_id_unadmitted")
                         is None),
                     "V216_JF_QUALITY_ORIGINAL_F_RANK_GROUP_INVALID")
                if f["physical_item_id"] in ids:
                    need(ranks[ids.index(f["physical_item_id"])]==
                             f["crafting_quality"],
                         "V216_JF_QUALITY_SELECTED_F_ITEM_RANK_DRIFT")
                    found.append(group)
            need(len(found)<=1,
                 "V216_JF_QUALITY_SELECTED_F_DUPLICATE_GROUPS")
            if found:
                g=found[0]
                result["F"]={
                    "selected_item_id":f["physical_item_id"],
                    "selected_crafting_quality":f["crafting_quality"],
                    "observed_item_ids":list(g["observed_item_ids"]),
                    "observed_qualities":list(g["observed_qualities"]),
                    "comparison_status_source_only":g["status"],
                    "highest_observed_quality_item_id_unadmitted":
                        g.get("highest_observed_quality_item_id_unadmitted"),
                    "selected_is_highest_observed_source_only":(
                        g.get("highest_observed_quality_item_id_unadmitted")==
                            f["physical_item_id"]),
                    "discovered_best_effect_accepted_as_quality_policy":(
                        g.get("highest_observed_quality_item_id_unadmitted")==
                            f["physical_item_id"] and
                        g.get("status") in (
                            "TOP_QUALITY_AMONG_OBSERVED_ONLY",
                            "ONLY_ONE_QUALITY_OBSERVED")),
                    "same_effect_and_use_conditions_verified":False,
                    "all_available_quality_ranks_verified":False,
                    "selected_simc_numeric_sha256":
                        f["source_identity_sha256"],
                    "highest_available_quality_verified":False}
            else:
                result["missing"].append(
                    "F_SELECTED_ITEM_OBSERVED_QUALITY_GROUP_PENDING")
        else:
            result["missing"].append(
                "F_ORIGINAL_QUALITY_COMPARISON_PENDING")
    else:
        result["missing"].append(
            "F_SELECTED_SIMC_NUMERIC_OR_QUALITY_SOURCE_PENDING")
    if result["J"] is not None and result["F"] is not None:
        result["status"]="SELECTED_J_F_OBSERVED_QUALITY_BOUND_UNADMITTED"
    return result


def _fresh_source_owner_crosscheck_selected_J_F(*, owner_numeric,
                                               trusted_budget_evidence):
    """Reject a claimed source match with a different J/F amount.

    A real authenticated J source may differ from raw v266 candidates;
    only a provider explicitly reusing the SAME raw-J source identity is
    compared. A selected F must match the measured SimC numeric F. Neither
    check authenticates highest-quality conditions.
    """
    if type(owner_numeric) is not dict:
        return trusted_budget_evidence
    need(type(trusted_budget_evidence) is dict and
         type(trusted_budget_evidence.get("components")) is dict,
         "V216_JF_OWNER_TRUSTED_GJFO_COMPONENTS_REQUIRED")
    proofs=trusted_budget_evidence["components"]
    source_j=owner_numeric.get("J")
    provider_j=proofs.get("J")
    if (type(source_j) is dict and type(provider_j) is dict and
            provider_j.get("source_sha256")==
                source_j["source_identity_sha256"]):
        need(provider_j.get("rating")==source_j["rating"],
             "V216_JF_OWNER_SAME_SOURCE_NOMINAL_J_CONFLICT")
    source_f=owner_numeric.get("F")
    if type(source_f) is dict:
        provider_f=proofs.get("F")
        need(type(provider_f) is dict and
             provider_f.get("rating")==source_f["rating"],
             "V216_JF_OWNER_SELECTED_SIMC_F_NUMBER_CONFLICT")
    return trusted_budget_evidence



def _fresh_source_owner_original_J_F_components(*, preflight, compilation,
                                                 staged, owner_numeric,
                                                 quality_scope,
                                                 effect_observations):
    """Promote only original already-verified J/F sources into v222 components.

    The live Build has authenticated the v221/v266/v230/v232 source stages
    and v281/v278 paired Native attempts. A J claim needs original ordinary
    gem numeric IDs, an observed-best comparable effect, and intrinsic
    sockets covering its exact selected layout. F additionally needs the
    original selected Native case files and SHA receipts rechecked in place.
    Missing evidence leaves an individual component pending; this is NOT
    a new source collector, effect validator or standalone READY decision.
    """
    out={}
    if (type(staged) is not dict or
            staged.get("status")!="FRESH_SEASON_ENVIRONMENT_STAGED_NOT_INSTALLED"
            or staged.get("stage_status") not in
                ("EXECUTED_AND_SEALED","REUSED_VERIFIED","RECOVERED_VERIFIED")
            or type(staged.get("stage_receipt_sha256")) is not str or
            season_budget_contract.SHA.fullmatch(
                staged["stage_receipt_sha256"]) is None or
            type(preflight) is not dict or type(compilation) is not dict or
            type(owner_numeric) is not dict or
            type(quality_scope) is not dict):
        return out
    build=preflight.get("game_build")
    manifest=preflight.get("source_catalog_manifest_sha256")
    need(preflight.get("schema")==FRESH_SOURCE_PREFLIGHT_SCHEMA
         and preflight.get("environment_ready") is False
         and preflight.get("simc_revision")==compilation.get("simc_revision")
         and type(build) is str and bool(build)
         and type(manifest) is str and
         season_budget_contract.SHA.fullmatch(manifest) is not None,
         "V216_JF_OWNER_VERIFIED_SAME_BUILD_STAGE_REQUIRED")
    j=owner_numeric.get("J")
    jq=quality_scope.get("J")
    socket=compilation.get("selected_J_intrinsic_socket_origin_unadmitted")
    if (type(j) is dict and type(jq) is dict and type(socket) is dict and
            socket.get("status") in (
                "J_INTRINSIC_COUNTS_BOUND_SOURCE_ONLY",
                "J_SIMC_DECLARED_FULL_GEM_PROFILE_SOURCE_ONLY")
            and (socket.get("additional_socket_proof_required_by_slot")=={}
                 or (socket.get("status")==
                     "J_SIMC_DECLARED_FULL_GEM_PROFILE_SOURCE_ONLY" and
                     (compilation.get("physical_gem_layout_unadmitted")
                      or {}).get("simc_declared_full_socket_policy")==
                         "FULL_GEM_ID_PROFILE_SIMC_OWNS"))
            and socket.get("observed_J_unadmitted")==j.get("rating")
            and type(socket.get("v232_stage_receipt_sha256")) is str and
            season_budget_contract.SHA.fullmatch(
                socket["v232_stage_receipt_sha256"]) is not None):
        ids=j.get("ordinary_gem_item_ids")
        groups=jq.get("same_enchant_quality_groups_source_only")
        need(type(ids) is list and bool(ids) and
             type(groups) is list and
             type(j.get("rating")) is int and j["rating"]>0 and
             jq.get("ordinary_gem_item_ids")==ids and
             type(jq.get("v230_stage_receipt_sha256")) is str and
             season_budget_contract.SHA.fullmatch(
                 jq["v230_stage_receipt_sha256"]) is not None and
             jq.get("v221_stage_receipt_sha256")==
                 j["v221_stage_receipt_sha256"] and
             sum(j["per_item_nominal_rating"][str(i)] for i in ids)==
                 j["rating"] and
             jq.get("real_socket_proof_required") is True,
             "V216_JF_OWNER_ORIGINAL_J_NUMERIC_QUALITY_SOCKET_DRIFT")
        valid=(
            jq.get("selected_nominal_quality_matches_v230") is True and
            jq.get("season_nominal_source_sha256")==
                j.get("season_nominal_source_sha256")
            if j.get("numeric_source_owner")==
               "PACKAGED_SEASON_NOMINAL_PER_ITEM" else True)
        for group in groups:
            seen=group.get("observed_item_ids")
            winner=group.get("best_discovered_effect_item_id_source_only")
            if not any(i in ids for i in (seen or [])):
                continue
            if (type(seen) is not list or
                    group.get("comparable_effect_source_only") is not True
                    or winner not in seen
                    or any(i!=winner for i in ids if i in seen)):
                valid=False
        if valid:
            src={"owner":j["source_identity_sha256"],
                 "v230_stage_receipt_sha256":jq["v230_stage_receipt_sha256"],
                 "v232_stage_receipt_sha256":
                     socket["v232_stage_receipt_sha256"],
                 "socket_counts":dict(socket["selected_socket_counts"])}
            out["J"]={
                "rating":j["rating"],"game_build":build,
                "source_catalog_manifest_sha256":manifest,
                "source_sha256":digest(canonical(src).encode("utf8")),
                "source_verification":"VALID_SAME_SEASON_SOURCE",
                "budget_policy":"NOMINAL_ORDINARY_GEMS_ONLY",
                "effect_quality_policy":(
                    "BEST_OBSERVED_NOMINAL_SEASON_SOURCE"
                    if j.get("numeric_source_owner")==
                        "PACKAGED_SEASON_NOMINAL_PER_ITEM"
                    else "BEST_DISCOVERED_COMPARABLE"),
                "original_J_source_sha256":j["source_identity_sha256"],
                "intrinsic_socket_receipt_sha256":
                    socket["v232_stage_receipt_sha256"]}
    f=owner_numeric.get("F")
    fq=quality_scope.get("F")
    if (type(f) is dict and type(fq) is dict and
            fq.get("selected_item_id")==f.get("physical_item_id") and
            fq.get("discovered_best_effect_accepted_as_quality_policy")
                is True and
            type(effect_observations) is list):
        physical=[row for row in effect_observations
                  if type(row) is dict and row.get("kind")=="flask"
                  and type(row.get("physical_item_native_source_unadmitted"))
                      is dict and
                  row["physical_item_native_source_unadmitted"].get(
                      "physical_item_id")==f["physical_item_id"]]
        if len(physical)==1:
            row=physical[0]
            src=row["physical_item_native_source_unadmitted"]
            recs=row.get("native_case_receipts")
            need(row.get("status")==
                 "SIMC_STATIC_CHMV_EFFECT_OBSERVED_NOT_ADMITTED"
                 and row.get("F_candidate_unadmitted")==f["rating"]
                 and row.get("static_CHMV_candidate")==
                     f["static_CHMV_vector"]
                 and src.get("schema")==
                     consumable_simc_relation.MEASUREMENT_BINDING_SCHEMA
                 and src.get("source_only") is True
                 and src.get("game_build")==build
                 and src.get("simc_revision")==compilation["simc_revision"]
                 and src.get("physical_item_id")==f["physical_item_id"]
                 and src.get("crafting_quality")==f["crafting_quality"]
                 and src.get("simc_input_token")==f["simc_input_token"]
                 and src.get("source_candidate_sha256")==
                     f["source_candidate_sha256"]
                 and type(recs) is list and len(recs)==2 and
                 [r.get("receipt_sha256") for r in recs]==
                     f["native_pair_receipt_sha256"]
                 and type(row.get("observed")) is dict,
                 "V216_JF_OWNER_SELECTED_ORIGINAL_F_SOURCE_DRIFT")
            root=pathlib.Path(compilation["stage_root"]).resolve()
            need(root.is_dir() and not root.is_symlink(),
                 "V216_JF_OWNER_NATIVE_STAGE_ROOT_REQUIRED")
            observed=row["observed"]
            for variant, rec in zip(("baseline","active"),recs):
                path=pathlib.Path(rec.get("receipt_path",""))
                folder=path.parent
                need(path.is_file() and not path.is_symlink()
                     and folder.is_dir() and not folder.is_symlink()
                     and folder.resolve().parent==root/"source"
                     and folder.name.startswith("v278_"+variant+"_")
                     and path.name=="receipt.json"
                     and 0<path.stat().st_size<=native_effect_pair.MAX_RECEIPT,
                     "V216_JF_OWNER_F_ORIGINAL_NATIVE_RECEIPT_LOCATION")
                raw=path.read_bytes()
                need(digest(raw)==rec["receipt_sha256"],
                     "V216_JF_OWNER_F_ORIGINAL_NATIVE_RECEIPT_SHA_DRIFT")
                try:
                    sealed=json.loads(raw)
                    identity=sealed["identity"]
                    profile_sha=observed[variant+"_profile_sha256"]
                except (ValueError,TypeError,KeyError) as exc:
                    raise EnvironmentBuildBlocked(
                        "V216_JF_OWNER_F_ORIGINAL_NATIVE_RECEIPT_INVALID"
                    ) from exc
                need(sealed.get("schema")==native_effect_pair.SCHEMA
                     and sealed.get("status")=="NATIVE_JSON2_CAPTURED"
                     and identity.get("variant")==variant
                     and identity.get("simc_revision")==
                         compilation["simc_revision"]
                     and identity.get("binary_sha256")==
                         row.get("binary_sha256")
                     and identity.get("source_profile_sha256")==
                         row.get("source_profile_sha256")
                     and identity.get("profile_sha256")==profile_sha
                     and identity.get("iterations")==1
                     and type(sealed.get("native_json2_sha256")) is str
                     and season_budget_contract.SHA.fullmatch(
                         sealed["native_json2_sha256"]) is not None,
                     "V216_JF_OWNER_F_ORIGINAL_NATIVE_CASE_IDENTITY_DRIFT")
                native=folder/"native.json"
                need(native.is_file() and not native.is_symlink()
                     and native_effect_pair.file_sha(native)==
                         sealed["native_json2_sha256"],
                     "V216_JF_OWNER_F_ORIGINAL_NATIVE_JSON2_SHA_DRIFT")
            out["F"]={
                "rating":f["rating"],"game_build":build,
                "source_catalog_manifest_sha256":manifest,
                "source_sha256":f["source_identity_sha256"],
                "source_verification":"EXACT_NATIVE",
                "selected_flask_item_id":f["physical_item_id"],
                "simc_input_token":f["simc_input_token"],
                "crafting_quality":f["crafting_quality"],
                "static_CHMV_vector":dict(f["static_CHMV_vector"]),
                "native_pair_receipt_sha256":
                    list(f["native_pair_receipt_sha256"]),
                "effect_quality_policy":"BEST_DISCOVERED_COMPARABLE"}
    return out


def _fresh_source_owner_merge_original_J_F(*, trusted_budget_evidence,
                                           owner_components):
    """Attach authenticated existing J/F once; never override other proofs."""
    if not owner_components:
        return trusted_budget_evidence
    need(type(trusted_budget_evidence) is dict and
         type(trusted_budget_evidence.get("components")) is dict and
         type(owner_components) is dict and
         set(owner_components)<={"J","F"},
         "V216_JF_OWNER_COMPLETE_BUDGET_EVIDENCE_REQUIRED")
    parts=trusted_budget_evidence["components"]
    for name,verified in owner_components.items():
        previous=parts.get(name)
        need(previous is None or
             (type(previous) is dict and all(
                 previous.get(k)==v for k,v in verified.items())),
             "V216_JF_OWNER_PROVIDER_"+name+"_CONFLICT")
    return {**trusted_budget_evidence,
            "components":{**parts,**{
                key:parts.get(key) or val
                for key,val in owner_components.items()}}}


def _fresh_source_owner_native_G_component(*, native_G, preflight,
                                           compilation, staged, target_ilevel):
    """Reuse the ORIGINAL v277-verified Native G as one source-owner component.

    This is called only after v277.collect and the same v216/v217 source
    compilation. Recheck its small sealed receipt and exact catalog scope,
    without another SimC subprocess, JSON2 parse, binary hash or source fetch.
    It authenticates only generic physical G, NEVER J/F/O, Policy A or READY.
    """
    if (type(native_G) is not dict or native_G.get("status")!=
            "G_NATIVE_NUMERIC_REFERENCE_OBSERVED_JFO_PENDING" or
            not native_G.get("native_run_folder")):
        # Legacy synthetic/source-only rows cannot be owner evidence.
        return None
    need(type(preflight) is dict and type(compilation) is dict and
         type(staged) is dict and
         staged.get("status")=="FRESH_SEASON_ENVIRONMENT_STAGED_NOT_INSTALLED" and
         staged.get("original_v216_preflight_sha256")==
             preflight.get("preflight_sha256") and
         preflight.get("schema")==FRESH_SOURCE_PREFLIGHT_SCHEMA and
         preflight.get("environment_ready") is False and
         preflight.get("simc_revision")==compilation.get("simc_revision") and
         type(preflight.get("game_build")) is str and
         type(preflight.get("source_catalog_manifest_sha256")) is str and
         season_budget_contract.SHA.fullmatch(
             preflight["source_catalog_manifest_sha256"]) is not None and
         type(target_ilevel) is int and target_ilevel>0,
         "V216_NATIVE_G_OWNER_ORIGINAL_SOURCE_SCOPE_REQUIRED")
    root=pathlib.Path(compilation["stage_root"]).resolve()
    folder=pathlib.Path(native_G["native_run_folder"])
    need(root.is_dir() and not root.is_symlink() and
         folder.is_dir() and not folder.is_symlink() and
         folder.resolve().parent==root/"source" and
         folder.name.startswith("v277_native_G_") and
         len(folder.name)==len("v277_native_G_")+24,
         "V216_NATIVE_G_OWNER_SEALED_STAGE_LOCATION_REQUIRED")
    receipt_file=folder/"receipt.json"
    need(receipt_file.is_file() and not receipt_file.is_symlink() and
         0<receipt_file.stat().st_size<=zero_history_G_native.MAX_RECEIPT,
         "V216_NATIVE_G_OWNER_RECEIPT_REQUIRED")
    raw=receipt_file.read_bytes()
    need(digest(raw)==native_G.get("native_receipt_sha256"),
         "V216_NATIVE_G_OWNER_RECEIPT_SHA_DRIFT")
    try:
        receipt=json.loads(raw)
        identity=receipt["identity"]
        observed=receipt["observed_G"]
        expected=season_budget_contract.standardize_representative_G(
            observed_G_total=observed["observed_G_total"],
            target_ilevel=target_ilevel,
            source_observation_sha256=observed["native_json2_sha256"])
    except (ValueError,TypeError,KeyError,
            season_budget_contract.SeasonBudgetBlocked) as exc:
        raise EnvironmentBuildBlocked(
            "V216_NATIVE_G_OWNER_ORIGINAL_NATIVE_RECORD_INVALID") from exc
    v277=preflight.get("v277_native_G_preprofile_unadmitted")
    need(type(v277) is dict and
         v277.get("status")==
             "NATIVE_G_NUMERIC_SOURCE_ONLY_JFO_AND_ADMISSION_PENDING" and
         v277.get("game_build")==preflight["game_build"] and
         v277.get("simc_revision")==preflight["simc_revision"] and
         v277.get("target_ilevel")==target_ilevel and
         v277.get("native_receipt_sha256")==digest(raw) and
         v277.get("native_json2_sha256")==observed["native_json2_sha256"] and
         v277.get("standardization")==expected and
         v277.get("standardized_G")==expected["standardized_G"] and
         v277.get("source_profile_receipt_sha256")==
             native_G.get("source_profile_receipt_sha256") and
         receipt.get("status")=="PASS_NATIVE_OBSERVED_G_UNPROMOTED" and
         receipt.get("returncode")==0 and
         receipt.get("new_native_calls")==1 and
         receipt.get("native_json2_sha256")==observed["native_json2_sha256"] and
         identity.get("source_game_build")==preflight["game_build"] and
         identity.get("simc_source_revision")==preflight["simc_revision"] and
         identity.get("target_ilevel")==target_ilevel and
         identity.get("source_receipt_sha256")==
             native_G.get("source_profile_receipt_sha256") and
         identity.get("executable_sha256")==
             native_G.get("native_binary_sha256") and
         identity.get("compiled_game_build_not_proven") is True and
         observed.get("generic_G_numeric_reference_usable") is True and
         observed.get("generic_G_current_season_membership_required") is False and
         observed.get("full_G_approved") is False and
         observed.get("source_profile_receipt_sha256")==
             native_G.get("source_profile_receipt_sha256") and
         observed.get("target_ilevel")==target_ilevel and
         observed.get("standardized_G_preview_unapproved")==expected and
         native_G.get("standardization")==expected and
         native_G.get("standardized_G")==expected["standardized_G"] and
         native_G.get("full_G_approved") is False and
         native_G.get("environment_ready") is False,
         "V216_NATIVE_G_OWNER_ORIGINAL_PROOF_OR_PROFILE_DRIFT")
    return {"rating":expected["standardized_G"],
            "game_build":preflight["game_build"],
            "source_catalog_manifest_sha256":
                preflight["source_catalog_manifest_sha256"],
            "source_sha256":observed["native_json2_sha256"],
            "source_verification":"EXACT_NATIVE",
            "standardization":expected}


def _fresh_source_owner_merge_native_G(*, trusted_budget_evidence,
                                       owner_G):
    """Attach one already verified native component, not a second G budget."""
    if owner_G is None:
        return trusted_budget_evidence
    need(type(trusted_budget_evidence) is dict and
         type(trusted_budget_evidence.get("components")) is dict and
         type(owner_G) is dict,
         "V216_NATIVE_G_OWNER_COMPLETE_EVIDENCE_REQUIRED")
    components=trusted_budget_evidence["components"]
    current=components.get("G")
    need(current is None or (type(current) is dict and
         all(current.get(k)==owner_G[k] for k in owner_G)),
         "V216_NATIVE_G_OWNER_PROVIDER_COMPONENT_CONFLICT")
    return {**trusted_budget_evidence,
            "components":{**components,"G":(current or owner_G)}}




def _fresh_original_default_base_install_inputs(*, preflight, staged,
                                                 original_G, original_J_F,
                                                 selected_budget_items,
                                                 target_ilevel, user):
    """Build the v222 input from ORIGINAL owners for an unenchanted default.

    The normal season-wide local web call cannot supply Python callbacks.
    Do not promote previews, user values, selected oils, unknown F, or any
    user-specific special/enchant scenario. The original source-owner and
    v212/v217 installation validations remain authoritative.
    """
    if (user is not None or type(selected_budget_items) is not dict
            or selected_budget_items.get("oil_item_ids_by_hand")!={}
            or type(original_G) is not dict
            or type(original_J_F) is not dict
            or set(original_J_F)!={"J","F"}):
        return None
    need(type(preflight) is dict and
         preflight.get("schema")==FRESH_SOURCE_PREFLIGHT_SCHEMA
         and preflight.get("environment_ready") is False
         and type(staged) is dict
         and staged.get("status")=="FRESH_SEASON_ENVIRONMENT_STAGED_NOT_INSTALLED"
         and staged.get("stage_status") in (
             "EXECUTED_AND_SEALED","REUSED_VERIFIED","RECOVERED_VERIFIED")
         and staged.get("original_v216_preflight_sha256")==
             preflight.get("preflight_sha256")
         and type(target_ilevel) is int and target_ilevel>0
         and type(preflight.get("source_artifact_sha256")) is str
         and season_budget_contract.SHA.fullmatch(
             preflight["source_artifact_sha256"]) is not None
         and type(preflight.get("source_catalog_manifest_sha256")) is str
         and season_budget_contract.SHA.fullmatch(
             preflight["source_catalog_manifest_sha256"]) is not None,
         "V216_DEFAULT_BASE_ORIGINAL_STAGE_REQUIRED")
    selected_flask=selected_budget_items.get("flask_item_id")
    need(type(selected_flask) is int and selected_flask>0
         and original_J_F["F"].get("selected_flask_item_id")==
             selected_flask
         and original_G.get("source_verification")=="EXACT_NATIVE"
         and original_J_F["J"].get("source_verification")==
             "VALID_SAME_SEASON_SOURCE"
         and original_J_F["F"].get("source_verification")=="EXACT_NATIVE",
         "V216_DEFAULT_BASE_SELECTED_FLASK_OR_SOURCE_DRIFT")
    game_build=preflight["game_build"]
    manifest=preflight["source_catalog_manifest_sha256"]
    for name,component in (
            ("G",original_G),("J",original_J_F["J"]),
            ("F",original_J_F["F"])):
        need(component.get("game_build")==game_build
             and component.get("source_catalog_manifest_sha256")==manifest
             and type(component.get("rating")) is int
             and component["rating"]>0
             and type(component.get("source_sha256")) is str
             and season_budget_contract.SHA.fullmatch(
                 component["source_sha256"]) is not None,
             "V216_DEFAULT_BASE_"+name+"_SAME_BUILD_PROVENANCE_DRIFT")
    standard=original_G.get("standardization")
    need(type(standard) is dict and
         standard.get("target_ilevel")==target_ilevel,
         "V216_DEFAULT_BASE_G_TARGET_ILEVEL_DRIFT")
    # v233's base has no selected enchant or optional SPECIAL EQUIPMENT.
    # Therefore fixed L/E=0 applies only to this season-wide baseline.
    # Exactly one SPECIAL GEM is still mandatory, only excluded from J.
    zero={k:0 for k in season_budget_contract.STATS}
    no_oil=season_budget_contract.explicit_no_oil_component(
        game_build=game_build,
        source_catalog_manifest_sha256=manifest,
        selected_oil_item_ids_by_hand={})
    evidence={
        "schema":season_budget_contract.SCHEMA,
        "game_build":game_build,
        "simc_revision":preflight["simc_revision"],
        "source_catalog_manifest_sha256":manifest,
        "source_catalog_artifact_sha256":
            preflight["source_artifact_sha256"],
        "target_ilevel":target_ilevel,
        "components":{"G":dict(original_G),
                      "J":dict(original_J_F["J"]),
                      "F":dict(original_J_F["F"]),"O":no_oil},
        "fixed_L":dict(zero),"fixed_E":dict(zero),
        "G_reference_excludes_selected_E":True,
        "scope":"UNENCHANTED_REPRESENTATIVE_EXPLICIT_NO_OIL"}
    # Existing v222 owns arithmetic and source identity; no new budget.
    season_budget_contract.preprofile_budget(
        source_catalog={"game_build":game_build,
            "simc_revision":preflight["simc_revision"],
            "manifest_sha256":manifest},
        source_artifact_sha256=preflight["source_artifact_sha256"],
        evidence=evidence,target_ilevel=target_ilevel)
    return {"trusted_budget_evidence":evidence,
            "trusted_policy_A_receipts_by_id":{}}


def _fresh_source_owner_merge_policy_A_original_source_relation(
        *,preflight,staged,trusted_policy_A_receipts_by_id):
    """Reuse only the original sealed v217 source family, not three others."""
    need(type(trusted_policy_A_receipts_by_id) is dict,
         "V216_POLICY_A_INTERNAL_PROVIDER_RECEIPTS_REQUIRED")
    meta=(preflight.get("optional_policy_A_evidence_unadmitted")
          if type(preflight) is dict else None)
    source=(meta.get("original_v217_source_relation_receipts_internal")
            if type(meta) is dict else None)
    if not source:
        return trusted_policy_A_receipts_by_id
    need(type(source) is dict and type(staged) is dict
         and staged.get("status")==
             "FRESH_SEASON_ENVIRONMENT_STAGED_NOT_INSTALLED"
         and staged.get("original_v216_preflight_sha256")==
             preflight.get("preflight_sha256")
         and staged.get("stage_status") in (
             "EXECUTED_AND_SEALED","REUSED_VERIFIED","RECOVERED_VERIFIED")
         and meta.get("v217_source_relation_scoped_only") is True
         and meta.get("v217_source_relation_receipt_count")==len(source)
         and meta.get("source_catalog_manifest_sha256")==
             preflight.get("source_catalog_manifest_sha256")
         and meta.get("source_catalog_artifact_sha256")==
             preflight.get("source_artifact_sha256")
         and preflight.get("schema")==FRESH_SOURCE_PREFLIGHT_SCHEMA
         and preflight.get("environment_ready") is False,
         "V216_POLICY_A_ORIGINAL_V217_SEALED_SCOPE_REQUIRED")
    need(all(type(k) is int and k>0 and type(v) is dict
             for k,v in trusted_policy_A_receipts_by_id.items()),
         "V216_POLICY_A_PROVIDER_ITEM_MAP_INVALID")
    merged={k:dict(v) for k,v in trusted_policy_A_receipts_by_id.items()}
    for item_id,parts in source.items():
        need(type(item_id) is int and item_id>0
             and type(parts) is dict
             and set(parts)=={"source_relation"}
             and type(parts["source_relation"]) is dict,
             "V216_POLICY_A_V217_SOURCE_RELATION_SHAPE_DRIFT")
        proof=parts["source_relation"]
        ident=proof.get("identity")
        need(type(ident) is dict and
             ident.get("kind")=="permanent_enchant" and
             ident.get("exact_id")==item_id and
             ident.get("game_build")==preflight.get("game_build") and
             ident.get("simc_revision")==preflight.get("simc_revision") and
             ident.get("catalog_sha256")==
                 preflight.get("source_catalog_manifest_sha256") and
             type(ident.get("slot")) is str and bool(ident["slot"]) and
             type(ident.get("simc_token")) is str
             and bool(ident["simc_token"]) and
             proof.get("status")==
                 auto_admission.PROOF_STATUSES["source_relation"] and
             type(proof.get("evidence_sha256")) is str
             and season_budget_contract.SHA.fullmatch(
                 proof["evidence_sha256"]) is not None,
             "V216_POLICY_A_V217_ORIGINAL_SOURCE_PROOF_DRIFT")
        existing=merged.get(item_id,{})
        need("source_relation" not in existing or
             existing["source_relation"]==proof,
             "V216_POLICY_A_PROVIDER_SOURCE_RELATION_CONFLICT")
        merged[item_id]={**existing,"source_relation":dict(proof)}
    return merged


def _fresh_source_owner_exact_no_oil(*, preflight, selected_budget_items,
                                     trusted_budget_evidence):
    """Reuse v222's original O=0 proof ONLY for explicitly selected no oil.

    Neither missing selections nor source-only numeric previews grant O
    ownership. G/J/F and selected actual oils still need their source owners.
    """
    if (selected_budget_items is None or
            selected_budget_items.get("oil_item_ids_by_hand") != {}):
        return trusted_budget_evidence
    need(type(preflight) is dict and
         preflight.get("schema")==FRESH_SOURCE_PREFLIGHT_SCHEMA and
         preflight.get("environment_ready") is False and
         type(preflight.get("game_build")) is str and
         type(preflight.get("source_catalog_manifest_sha256")) is str and
         season_budget_contract.SHA.fullmatch(
             preflight["source_catalog_manifest_sha256"]) is not None,
         "V216_SOURCE_OWNER_NO_OIL_ORIGINAL_PREFLIGHT_REQUIRED")
    need(type(trusted_budget_evidence) is dict and
         type(trusted_budget_evidence.get("components")) is dict,
         "V216_SOURCE_OWNER_NO_OIL_BUDGET_COMPONENTS_REQUIRED")
    exact=season_budget_contract.explicit_no_oil_component(
        game_build=preflight["game_build"],
        source_catalog_manifest_sha256=preflight[
            "source_catalog_manifest_sha256"],
        selected_oil_item_ids_by_hand={})
    components=trusted_budget_evidence["components"]
    need("O" not in components or components["O"]==exact,
         "V216_SOURCE_OWNER_NO_OIL_PROOF_CONFLICT")
    return {**trusted_budget_evidence,
            "components":{**components,"O":exact}}


def _install_verified_fresh_environment_only(*, compilation, staged,
                                             trusted_budget_evidence,
                                             target_ilevel, manual_final_T=None,
                                             trusted_policy_A_receipts_by_id=None):
    """Finish the SAME v216/v217 Environment Build after source verification.

    This INTERNAL boundary takes only source-owner-authenticated v222 GJFO
    evidence and existing v220 exact item receipts. Source-only previews,
    user-submitted JSON, or catalog stage SHA by itself MUST NOT call it.
    No new data collector, Native, cache, separate season DB or DPS run.
    """
    need(type(compilation) is dict and type(staged) is dict and
         type(trusted_budget_evidence) is dict and
         type(trusted_policy_A_receipts_by_id) is dict and
         staged.get("schema")==environment_manifest.FRESH_SEASON_STAGE_SCHEMA and
         staged.get("status")==
             "FRESH_SEASON_ENVIRONMENT_STAGED_NOT_INSTALLED" and
         staged.get("stage_status") in (
             "EXECUTED_AND_SEALED","REUSED_VERIFIED","RECOVERED_VERIFIED") and
         type(staged.get("stage_receipt_sha256")) is str,
         "V216_FRESH_INSTALL_TRUSTED_STAGE_AND_BUDGET_REQUIRED")
    source_path=pathlib.Path(compilation["source_catalog_path"])
    stage_root=pathlib.Path(compilation["stage_root"])
    staged_path=pathlib.Path(staged["stage_output_path"])
    need(source_path.is_file() and not source_path.is_symlink() and
         stage_root.is_dir() and not stage_root.is_symlink() and
         staged_path.is_file() and not staged_path.is_symlink() and
         source_path.resolve().is_relative_to(stage_root.resolve()) and
         staged_path.resolve().is_relative_to(stage_root.resolve()),
         "V216_FRESH_INSTALL_SOURCE_OR_STAGE_OUTSIDE_WORKSPACE")
    catalog,catalog_sha=environment_manifest.read_json(source_path)
    sealed, _ = environment_manifest.read_json(staged_path)
    environment_manifest.verify_fresh_source_environment(sealed)
    need(sealed["manifest_sha256"]==staged["manifest_sha256"] and
         sealed["original_v216_preflight_sha256"]==
             staged["original_v216_preflight_sha256"],
         "V216_FRESH_INSTALL_STAGED_SOURCE_RECEIPT_DRIFT")
    # Same original v196 normal product catalog and v220 Policy A pipeline.
    ui=user_catalog.public_options(source_path)
    # DK permanent runes originate ONLY from the current pinned SimC class
    # module collected within this Build. No user JSON or previous-season ID.
    dk_stage=compilation.get("dk_runeforge_source_options")
    verified_dk=None
    if (type(dk_stage) is dict and dk_stage.get("status")==
            "PINNED_SIMC_DK_RUNEFORGE_OPTIONS_SEALED"):
        dk_path=pathlib.Path(dk_stage["catalog_path"]).resolve()
        need(dk_path.is_relative_to(stage_root.resolve()) and
             dk_path.is_file() and not dk_path.is_symlink(),
             "V216_DK_PINNED_SOURCE_OUTSIDE_ORIGINAL_BUILD")
        doc=json.loads(dk_path.read_text(encoding="utf8"))
        dk_rune_source.verify(doc,game_build=catalog["game_build"],
                              simc_revision=catalog["simc_revision"])
        need(doc["manifest_sha256"]==dk_stage["manifest_sha256"] and
             type(dk_stage.get("source_stage_receipt_sha256")) is str and
             len(dk_stage["source_stage_receipt_sha256"])==64,
             "V216_DK_PINNED_SOURCE_OR_STAGE_SHA_DRIFT")
        verified_dk={**doc,"source_stage_receipt_sha256":
                    dk_stage["source_stage_receipt_sha256"]}
    installed=environment_manifest.compile_fresh_installed_environment(
        source_catalog=catalog,source_artifact_sha256=catalog_sha,
        staged_source_environment=sealed,
        trusted_budget_evidence=trusted_budget_evidence,
        source_ui=ui,
        trusted_policy_A_receipts_by_id=trusted_policy_A_receipts_by_id,
        target_ilevel=target_ilevel,manual_final_T=manual_final_T,
        verified_DK_runeforge_source=verified_dk)
    key=installed["manifest_sha256"][:20]
    stage_id="fresh-v212-installed-"+key
    output="fresh_source/v212_installed_"+key+".json"
    path=stage_root/output
    encoded=environment_manifest.canonical(installed)+"\n"
    def execute():
        path.parent.mkdir(parents=True,exist_ok=True)
        need(not path.exists() and not path.is_symlink(),
             "V216_FRESH_INSTALL_OUTPUT_ALREADY_EXISTS_UNRECEIPTED")
        path.write_text(encoded,encoding="utf8")
    def validate(files):
        saved=files["environment"]
        if saved.is_symlink() or saved.read_text(encoding="utf8")!=encoded:
            return False
        return environment_manifest.verify_fresh_installed_environment(
            json.loads(saved.read_text(encoding="utf8")))
    receipt=stage_engine.execute_stage(
        root=stage_root,stage_id=stage_id,
        stage_version="v212-fresh-installed-environment-1",
        inputs={"manifest_sha256":installed["manifest_sha256"],
                "source_stage_sha256":sealed["manifest_sha256"],
                "trusted_budget_evidence_sha256":
                    installed["trusted_budget_evidence_sha256"],
                "policy_A_prepared_sha256":
                    installed["original_v196_prepared_options_sha256"]},
        outputs={"environment":output},execute=execute,validate=validate)
    return {"schema":environment_manifest.FRESH_SEASON_INSTALLED_SCHEMA,
            "status":installed["status"],
            "manifest_sha256":installed["manifest_sha256"],
            "source_stage_sha256":sealed["manifest_sha256"],
            "stage_status":receipt["status"],
            "stage_receipt_sha256":receipt["receipt_sha256"],
            "stage_output_path":str(path),
            "environment_ready":True,"environment_installed":True,
            "options_published":True,
            "published_verified_option_count":
                installed["published_verified_option_count"],
            "official_G":installed["official_G"],
            "official_J":installed["official_J"],
            "official_F":installed["official_F"],
            "official_O":dict(installed["official_O"]),
            "official_B":installed["official_B"],
            "official_T":installed["official_T"],
            "new_native_calls":0,"network_calls":0}


def build_environment(*, sessions_root, session_folder, user, binary, revision,
                      static_cache, source_catalog_path, bootstrap_result,
                      v208_start_receipt_path=None, package_manifest_path=None,
                      profile_stage_receipt=None, season_budget_evidence=None,
                      season_budget_source_paths=None,
                      expected_new_season_build=None,
                      fresh_source_stage_inputs=None,
                      fresh_standard_budget_evidence_by_ilevel=None,
                      fresh_standard_budget_reference_track=None,
                      fresh_g_native_receipt_paths_by_ilevel=None,
                      fresh_simc_effect_snapshot_case=None,
                      fresh_gem_layout_receipt=None,
                      fresh_gem_rating_by_id=None,
                      fresh_gjfo_evidence=None,
                      fresh_collection_inputs=None):
    """Reconcile existing inputs and seal one incremental, auditable build.

    Source acquisition is intentionally outside this local coordinator:
    v191/v211/v213 are consumed from the exact installed package artifact.
    A new season/source refresh must first install a separately verified
    versioned source package. The coordinator never silently relabels stale
    source bytes as current.
    """
    # ZERO-HISTORY is an input mode of the SAME normal Build, not a parallel
    # compiler or a SimC-only fixture. The real v161/v217/v216 source chain
    # collects in its own receipt-backed workspace and returns PENDING until
    # the actual new-season G/J/F/O and source compiler can be admitted.
    if fresh_collection_inputs is not None:
        need(type(fresh_collection_inputs) is dict and
             {"expected_game_build","representative_request",
              "g_probe_character","simc_revision_hint"} <=
                 set(fresh_collection_inputs) and
             set(fresh_collection_inputs) <= {
                 "expected_game_build","representative_request",
                 "g_probe_character","simc_revision_hint",
                 "fetch","credentials","discovery_transport",
                 "tier_transport","bonus_transport","gear_transport",
                  "item_effect_transport","spell_effect_transport",
                  "spell_equipped_transport",
                 "simc_transport","simc_compiler_transport",
                 "gem_enchant_transport","effect_probe_requests",
                  "same_build_budget_evidence",
                  "gem_layout_receipt","gem_rating_by_id",
                  "selected_budget_items","auto_native_F_requested",
                  "auto_native_O_requested",
                  "auto_native_G_requested",
                   "verified_install_input_provider",
                   "auto_select_observed_F_no_oil",
                   "source_selected_gem_roles",
                   "source_target_socket_count",
                   "auto_four_stat_source_requested",
                   "source_ordinary_nominal_by_stat"},
             "V216_ZERO_HISTORY_SOURCE_INPUT_FIELDS")
        # A trusted internal source-owner adapter can provide independently
        # verified GJFO/Policy A input. JSON or HTTP cannot supply a callable.
        verified_install_provider=fresh_collection_inputs.get(
            "verified_install_input_provider")
        need(verified_install_provider is None or
             callable(verified_install_provider),
             "V216_VERIFIED_INSTALL_PROVIDER_INTERNAL_CALLABLE_REQUIRED")
        # G Native is optional when an existing same-build v222 budget
        # receipt was supplied. Do not spend a Native call merely because
        # the same SimC binary is also available for F/O. The original
        # preflight still checks the supplied G scope before any admission;
        # bad evidence fails closed instead of silently replacing the source.
        # With no supplied budget, retain the legacy binary=>G default.
        # Explicit G opt-in always overrides this efficiency default.
        auto_native_G=fresh_collection_inputs.get(
            "auto_native_G_requested",
            binary is not None and
            fresh_collection_inputs.get("same_build_budget_evidence") is None)
        need(type(auto_native_G) is bool and
             (not auto_native_G or binary is not None),
             "V216_AUTO_G_NATIVE_EXPLICIT_BINARY_REQUIRED")
        auto_native_F=fresh_collection_inputs.get("auto_native_F_requested",False)
        need(type(auto_native_F) is bool and
             (not auto_native_F or binary is not None) and
             (not auto_native_F or
              fresh_collection_inputs.get("effect_probe_requests") is None),
             "V216_AUTO_F_NATIVE_EXPLICIT_BINARY_REQUIRED")
        auto_native_O=fresh_collection_inputs.get("auto_native_O_requested",False)
        # O now uses existing pinned SimC stat source (v296), without the
        # talent-buffed v278 Native. This flag is a source-inspection opt-in
        # retained for API compatibility; no binary is required for O alone.
        need(type(auto_native_O) is bool and
             (not auto_native_O or
              fresh_collection_inputs.get("effect_probe_requests") is None),
             "V216_AUTO_O_SOURCE_ONLY_NO_EXPLICIT_PROBES")
        effect_probe_requests=fresh_collection_inputs.get("effect_probe_requests")
        # Same-build evidence is internal. The ORIGINAL catalog preflight
        # audits the source and v222 arithmetic only after v191/v211/v213.
        zero_history_budget_evidence=fresh_collection_inputs.get(
            "same_build_budget_evidence")
        zero_history_gem_layout=fresh_collection_inputs.get(
            "gem_layout_receipt")
        source_selected_gem_roles=fresh_collection_inputs.get(
            "source_selected_gem_roles")
        need(source_selected_gem_roles is None or
             (type(source_selected_gem_roles) is dict and
              set(source_selected_gem_roles)=={
                  "special_gem_id","ordinary_gem_ids"} and
              type(source_selected_gem_roles["special_gem_id"]) is int and
              source_selected_gem_roles["special_gem_id"]>0 and
              (source_selected_gem_roles["ordinary_gem_ids"] is None or
               type(source_selected_gem_roles["ordinary_gem_ids"]) is list)
              and user is None and zero_history_gem_layout is None),
             "V216_DEFAULT_GEM_INTERNAL_ROLE_SELECTION_SCOPE_REQUIRED")
        target_sockets=fresh_collection_inputs.get(
            "source_target_socket_count",5)
        need(type(target_sockets) is int and 5<=target_sockets<=64 and
             (source_selected_gem_roles is not None or
              "source_target_socket_count" not in fresh_collection_inputs),
             "V216_DECLARED_FULL_SOCKET_COUNT_REQUIRED")
        # None ordinary IDs => use four types from sealed nominal CHMV source.
        # The existing special ID is consumed, never rediscovered/probed.
        auto_four_stat_default=(
            source_selected_gem_roles is not None and
            source_selected_gem_roles["ordinary_gem_ids"] is None)
        nominal_four_stat_source=fresh_collection_inputs.get(
            "source_ordinary_nominal_by_stat")
        need(nominal_four_stat_source is None or
             (auto_four_stat_default and user is None and
              "gem_rating_by_id" not in fresh_collection_inputs),
             "V216_NOMINAL_J_ONLY_INTERNAL_FOUR_STAT_SOURCE")
        # A cold-start may collect the same-build raw DBC source without
        # inventing either special or ordinary ItemIDs. Source acquisition
        # and role selection/installation are independent contracts.
        auto_four_stat_source_requested=fresh_collection_inputs.get(
            "auto_four_stat_source_requested",False)
        need(type(auto_four_stat_source_requested) is bool,
             "V216_FOUR_STAT_SOURCE_OPT_IN_BOOL_REQUIRED")
        zero_history_gem_ratings=fresh_collection_inputs.get(
            "gem_rating_by_id")
        selected_budget_items=fresh_collection_inputs.get(
            "selected_budget_items")
        auto_select_default_F=fresh_collection_inputs.get(
            "auto_select_observed_F_no_oil",False)
        need(type(auto_select_default_F) is bool and
             (not auto_select_default_F or
              (user is None and selected_budget_items is None
               and auto_native_F and not auto_native_O)),
             "V216_AUTO_F_NO_OIL_EXPLICIT_SCOPE_REQUIRED")
        need(selected_budget_items is None or
             (type(selected_budget_items) is dict and
              set(selected_budget_items)=={
                  "flask_item_id","oil_item_ids_by_hand"} and
              type(selected_budget_items["flask_item_id"]) is int and
              selected_budget_items["flask_item_id"]>0 and
              type(selected_budget_items["oil_item_ids_by_hand"]) is dict and
              set(selected_budget_items["oil_item_ids_by_hand"]) <= {
                  "main_hand","off_hand"} and
              all(type(item_id) is int and item_id>0 for item_id in
                  selected_budget_items["oil_item_ids_by_hand"].values())),
             "V216_SELECTED_PHYSICAL_BUDGET_ITEM_FIELDS_INVALID")
        need(zero_history_budget_evidence is None or
             (type(zero_history_budget_evidence) is dict and
              type(fresh_collection_inputs["representative_request"]) is dict
              and type(fresh_collection_inputs[
                  "representative_request"].get("target_ilevel")) is int
              and 1<=fresh_collection_inputs[
                  "representative_request"]["target_ilevel"]<=1000),
             "V216_ZERO_HISTORY_BUDGET_TARGET_REPRESENTATIVE_REQUIRED")
        manual_T=None
        if user is not None:
            need(type(user) is dict and type(user.get("target")) is dict
                 and set(user["target"])=={"ilevel","final_T"}
                 and type(user["target"]["ilevel"]) is int
                 and (user["target"]["final_T"] is None or
                      type(user["target"]["final_T"]) is int
                      and 1<=user["target"]["final_T"]<=100000),
                 "V216_ZERO_HISTORY_USER_TARGET_REQUIRED")
            requested=fresh_collection_inputs["representative_request"]
            need(type(requested) is dict
                 and requested.get("target_ilevel")==user["target"]["ilevel"],
                 "V216_ZERO_HISTORY_USER_REPRESENTATIVE_ILEVEL_MISMATCH")
            manual_T=user["target"]["final_T"]
        need(effect_probe_requests is None or
             (type(effect_probe_requests) is list
              and len(effect_probe_requests)<=4
              and all(type(r) is dict and
                  type(r.get("source_profile_path")) is str and
                  ((set(r)=={"source_profile_path","kind","token"}
                    and type(r["token"]) is str
                    and r["kind"] in ("flask","food","temporary_enchant"))
                   or (set(r)=={"source_profile_path","kind","item_id"}
                       and r["kind"]=="flask"
                       and type(r["item_id"]) is int and r["item_id"]>0)
                   or (set(r)=={"source_profile_path","kind","item_id","hand"}
                       and r["kind"]=="temporary_enchant"
                       and type(r["item_id"]) is int and r["item_id"]>0
                       and r["hand"] in ("main_hand","off_hand")))
                  for r in effect_probe_requests)),
             "V216_ZERO_HISTORY_NATIVE_EFFECT_REQUEST_FIELDS")
        need(source_catalog_path is None and
             fresh_source_stage_inputs is None and
             fresh_gjfo_evidence is None and
             fresh_standard_budget_evidence_by_ilevel is None and
             session_folder is None and
             bootstrap_result is None,
             "V216_ZERO_HISTORY_MUST_NOT_USE_INSTALLED_SESSION_OR_BUDGET")
        source_inputs={
            k:v for k,v in fresh_collection_inputs.items()
            if k not in ("effect_probe_requests",
                         "same_build_budget_evidence",
                         "gem_layout_receipt","gem_rating_by_id",
                         "selected_budget_items","auto_native_F_requested",
                         "auto_native_O_requested",
                         "auto_native_G_requested",
                         "auto_select_observed_F_no_oil",
                         "source_selected_gem_roles",
                         "source_target_socket_count",
                         "auto_four_stat_source_requested",
                         "source_ordinary_nominal_by_stat",
                         "verified_install_input_provider")}
        if auto_four_stat_default or auto_four_stat_source_requested:
            source_inputs["auto_four_stat_gems"]=True
        collected=collect_wago_new_season_source(
            sessions_root=sessions_root,**source_inputs)
        progress=_zero_history_source_progress(collected)
        if source_selected_gem_roles is not None and not auto_four_stat_default:
            zero_history_gem_layout=(
                _fresh_default_intrinsic_gem_layout_from_source(
                    collected=collected,
                    selected_roles=source_selected_gem_roles,
                    target_ilevel=fresh_collection_inputs[
                        "representative_request"]["target_ilevel"]))
            progress["default_intrinsic_gem_layout_unadmitted"]=(
                zero_history_gem_layout)
        # Explicit NONE is an actual user selection, not the O=0 preview
        # assumption. The old physical-weapon applicability task is then
        # irrelevant; incomplete F/G/J evidence stays pending as before.
        if (selected_budget_items is not None and
                not selected_budget_items["oil_item_ids_by_hand"]):
            progress["requires"]=[
                requirement for requirement in progress["requires"]
                if requirement!="WEAPON_OIL_O_EXACT_APPLICATION_AND_RATING_PENDING"]
        # Reuse the original v236/v234 source-profile Native parser. Only a
        # configured local binary and existing v233 source profile may trigger
        # one real G probe. The content-addressed v236 output folder forbids
        # repeat executions on cache hits, failures and interrupted runs.
        try:
            native_G=zero_history_G_native.collect(
                sessions_root=sessions_root,collected=collected,
            binary=binary if auto_native_G else None)
        except (zero_history_G_native.GNativeStageBlocked,
                OSError,ValueError,KeyError,TypeError) as exc:
            raise EnvironmentBuildBlocked(
                "V216_ZERO_HISTORY_NATIVE_G_INVALID:"
                +str(exc).split(":",1)[0]) from exc
        progress["native_G_status"]=native_G["status"]
        progress["new_native_calls"]=native_G["new_native_calls"]
        if native_G.get("standardized_G") is not None:
            progress["G_numeric_reference_observed_unadmitted"]=(
                native_G["standardized_G"])
            progress["requires"]=[
                x for x in progress["requires"]
                if x!="G_NATIVE_RATING_OBSERVATION_PENDING"]
            progress["requires"].append(
                "G_NATIVE_NUMERIC_REFERENCE_REUSE_REQUIRES_J_F_O")
        elif native_G.get("native_log_excerpt") is not None:
            progress["requires"].append(
                "G_NATIVE_SIMC_ERROR_INSPECT_OR_CHANGE_SOURCE_BINARY")
        preflight=None
        # Reuse v241's already tested v191 -> v211 -> v213 compilers, not
        # another source builder. A missing original input is a specific
        # source-work item rather than a fake legacy file or J/F default.
        try:
            source_compilation=source_wiring.compile_collected(
                collected,compiler=fresh_stage.compile_fresh_candidate)
            if source_compilation["status"]==(
                    "FRESH_V191_V211_V213_COMPILED_UNADMITTED"):
                # Optional one-source-v217 collector. Missing DK source must
                # not invalidate a correctly verified normal G/J/F/O Build.
                # Exact byte identity is pinned to this current SimC revision.
                try:
                    rune_options=dk_rune_source.collect(
                        stage_root=source_compilation["stage_root"],
                        game_build=collected["expected_game_build"],
                        pinned_source=collected.get(
                            "fresh_pinned_v211_source"))
                except (dk_rune_source.RuneforgeSourceBlocked,
                        stage_engine.StageExecutionBlocked,
                        OSError,ValueError,KeyError,TypeError) as exc:
                    rune_options={
                        "status":"DK_RUNEFORGE_PINNED_SOURCE_PENDING",
                        "reason":type(exc).__name__+":"+str(exc).split(":",1)[0],
                        "items":[],"native_calls":0,"network_calls":0}
                source_compilation["dk_runeforge_source_options"]=rune_options
                progress["dk_runeforge_source_options"]=rune_options
            if source_compilation["status"]==(
                    "FRESH_V191_V211_V213_COMPILED_UNADMITTED"):
                if auto_four_stat_default:
                    # Reuse the original v221/v266 receipts; the normal
                    # preflight reads their same-build source again by cache.
                    src=_fresh_gem_item_source_stage(
                        stage_root=source_compilation["stage_root"],
                        wago_folder=pathlib.Path(
                            collected["snapshot_receipt_path"]).parent,
                        source_catalog_path=source_compilation[
                            "source_catalog_path"],
                        expected_game_build=collected["expected_game_build"])
                    observed=gem_enchant_stage.view(
                        stage_root=source_compilation["stage_root"],
                        v221_candidate_path=src["candidate_path"],
                        build=collected["expected_game_build"],
                        selected_source_gem_item_ids=[
                            source_selected_gem_roles["special_gem_id"]],
                        excluded_ordinary_item_id=
                            source_selected_gem_roles["special_gem_id"])
                    j_owner_diagnostic=(
                        _existing_v268_four_stat_source_diagnostic(
                            observed=observed,csv_source=src))
                    # Existing source result only: never an extra quality,
                    # effect, socket or J admission gate.
                    progress["four_stat_source_owner_diagnostic_unadmitted"]=(
                        j_owner_diagnostic)
                    source_compilation[
                        "four_stat_source_owner_diagnostic_unadmitted"]=(
                            j_owner_diagnostic)
                    # Declarative SimC gem_id layout, not game socket unlock.
                    # Uses the same v232 sealed gear IDs. No v280 item/spell
                    # lookup and no separate bonus socket eligibility Gate.
                    selected_slots=(collected.get(
                        "fresh_one_spec_simc_representative") or {}).get(
                            "intrinsic_socket_counts_by_selected_slot_source_only")
                    if type(selected_slots) is not dict or not selected_slots:
                        progress["requires"].append(
                            "SIMC_REPRESENTATIVE_GEAR_SLOT_NAMES_PENDING")
                        declared_counts=None
                    else:
                        declared_counts=physical_gems.declared_full_socket_counts(
                            available_slots=sorted(selected_slots),
                            socket_total=target_sockets,need=need)
                        progress["simc_declared_full_socket_counts_source_only"]=(
                            dict(declared_counts))
                        source_compilation[
                            "simc_declared_full_socket_counts_source_only"]=(
                                dict(declared_counts))
                    ordinary=None
                    if declared_counts is not None and (
                            observed.get(
                                "selected_gem_v221_same_build_items_all_present")
                            is True):
                        if nominal_four_stat_source is not None:
                            # Reuse independently sourced per-gem nominal
                            # totals. Raw EffectPointsMin interpretation is
                            # not the budget owner for this selected season.
                            nominal=physical_gems.nominal_four_stat_from_season_source(
                                source=nominal_four_stat_source,
                                game_build=collected["expected_game_build"],
                                socket_total=target_sockets,
                                special_gem_id=source_selected_gem_roles[
                                    "special_gem_id"],need=need)
                            ordinary=nominal["ordinary_gem_ids"]
                            zero_history_gem_ratings=nominal["rating_by_id"]
                            progress["four_stat_ordinary_nominal_source_unadmitted"]=(
                                nominal)
                            j_owner_diagnostic["original_v266_raw_gate_bypassed"]=True
                            j_owner_diagnostic["J_numeric_next_owner"]=(
                                "SEASON_NOMINAL_PER_ITEM_TOTAL_SUPPLIED_UNADMITTED")
                        elif observed.get(
                                "four_stat_ordinary_source_complete_unadmitted"
                                ) is True:
                            ordinary=physical_gems.ordinary_four_stat_default(
                                observed_by_stat=observed[
                                    "four_stat_ordinary_best_observed_unadmitted"],
                                socket_total=target_sockets,
                                special_gem_id=source_selected_gem_roles[
                                    "special_gem_id"],need=need)
                    if declared_counts is not None and ordinary is None:
                        progress["requires"].append(
                            "FOUR_ORDINARY_TYPES_SAME_BUILD_SOURCE_PENDING")
                        progress["four_stat_ordinary_source_status_unadmitted"]=(
                            observed.get("status"))
                    if ordinary is not None:
                        zero_history_gem_layout=(
                            _fresh_default_intrinsic_gem_layout_from_source(
                                collected=collected,
                                selected_roles={
                                    "special_gem_id":source_selected_gem_roles[
                                        "special_gem_id"],
                                    "ordinary_gem_ids":ordinary},
                                target_ilevel=fresh_collection_inputs[
                                    "representative_request"]["target_ilevel"],
                                simc_declared_socket_counts=declared_counts))
                        progress["default_intrinsic_gem_layout_unadmitted"]=(
                            zero_history_gem_layout)
                        progress["four_stat_ordinary_source_selection_unadmitted"]=(
                            nominal_four_stat_source["by_stat"]
                            if nominal_four_stat_source is not None else
                            observed[
                                "four_stat_ordinary_best_observed_unadmitted"])
                preflight=preflight_new_season_source(
                    source_catalog_path=source_compilation["source_catalog_path"],
                    expected_game_build=collected["expected_game_build"],
                    expected_simc_revision=source_compilation["simc_revision"],
                    source_snapshot_folder=pathlib.Path(
                        collected["snapshot_receipt_path"]).parent,
                    source_stage_root=source_compilation["stage_root"],
                    policy_A_v217_stages={
                        "stage_root":source_compilation["stage_root"],
                        "v191_stage":source_compilation.get("v191_stage"),
                        "v211_stage":source_compilation.get("v211_stage"),
                        "v213_stage":source_compilation.get("v213_stage")},
                    budget_evidence=zero_history_budget_evidence,
                    gem_layout_receipt=zero_history_gem_layout,
                    gem_rating_by_id=zero_history_gem_ratings,
                    nominal_gem_source=(
                        nominal_four_stat_source if
                        auto_four_stat_default and
                        zero_history_gem_layout is not None else None),
                    zero_history_native_G=native_G,
                    pinned_gem_simc_source_folder=collected.get(
                        "fresh_lazy_full_pinned_simc_item_source",{}).get(
                            "source_dir"),
                    target_ilevel=(
                        fresh_collection_inputs[
                            "representative_request"]["target_ilevel"]
                        if (zero_history_budget_evidence is not None or
                            native_G.get("status")==
                            "G_NATIVE_NUMERIC_REFERENCE_OBSERVED_JFO_PENDING")
                        else None),
                    manual_final_T=(
                        manual_T if zero_history_budget_evidence is not None
                        else None))
                if "physical_gem_layout_unadmitted" in preflight:
                    source_compilation["physical_gem_layout_unadmitted"]=(
                        preflight["physical_gem_layout_unadmitted"])
                    # Existing sealed v232 + original v271; no new J gate.
                    j_socket=_fresh_selected_J_intrinsic_socket_source(
                        collected=collected,preflight=preflight,
                        compilation=source_compilation)
                    source_compilation[
                        "selected_J_intrinsic_socket_origin_unadmitted"]=j_socket
                    progress[
                        "selected_J_intrinsic_socket_origin_unadmitted"]=j_socket
                if "selected_v221_gem_item_relation_unadmitted" in preflight:
                    source_compilation["selected_v221_gem_item_relation_unadmitted"]=(
                        preflight["selected_v221_gem_item_relation_unadmitted"])
                if "physical_gem_raw_rating_by_id_unadmitted" in preflight:
                    source_compilation["physical_gem_raw_rating_by_id_unadmitted"]=(
                        preflight["physical_gem_raw_rating_by_id_unadmitted"])
                if "physical_gem_J_arithmetic_unadmitted" in preflight:
                    gem_J=preflight["physical_gem_J_arithmetic_unadmitted"]
                    source_compilation["physical_gem_J_arithmetic_unadmitted"]=gem_J
                    progress["physical_gem_J_arithmetic_unadmitted"]=gem_J
                if "v277_native_G_preprofile_unadmitted" in preflight:
                    observed=preflight["v277_native_G_preprofile_unadmitted"]
                    source_compilation["v277_native_G_preprofile_unadmitted"]=observed
                    progress["v277_native_G_preprofile_unadmitted"]=observed
                if "v222_G_component_reference_unadmitted" in preflight:
                    # The same source-scoped G must reach BOTH the automatic
                    # numeric input and the Build's inspectable source summary.
                    # It remains a source-only candidate, not certified G.
                    source_compilation[
                        "v222_G_component_reference_unadmitted"]=dict(
                            preflight["v222_G_component_reference_unadmitted"])
                    # The existing v222 same-season reference is an
                    # alternative to Native G, not another required Native
                    # measurement. Report the actual remaining source
                    # authentication work without fabricating G approval.
                    referenced_G=_zero_history_G_numeric_input_from_preflight(
                        preflight=preflight,target_ilevel=fresh_collection_inputs[
                            "representative_request"]["target_ilevel"])
                    if (type(referenced_G) is dict and
                            referenced_G.get("status")==
                            "V222_SAME_SEASON_REFERENCE_G_NUMERIC_UNADMITTED"):
                        progress["requires"]=[
                            requirement for requirement in progress["requires"]
                            if requirement!="G_NATIVE_RATING_OBSERVATION_PENDING"]
                        progress["requires"].append(
                            "G_SAME_SEASON_REFERENCE_SOURCE_AUTHENTICATION_PENDING")
                if "proposed_budget_arithmetic_unadmitted" in preflight:
                    # The original v222 calculator owns B/T and manual T;
                    # source trust / user session admission remains pending.
                    arithmetic=preflight[
                        "proposed_budget_arithmetic_unadmitted"]
                    source_compilation[
                        "preprofile_budget_arithmetic_unadmitted"]=arithmetic
                    progress[
                        "preprofile_budget_arithmetic_unadmitted"]=arithmetic
                    progress["requires"].append(
                        "V222_GJFO_SOURCE_ADMISSION_AND_V098_PROFILE_PENDING")
                source_compilation["preflight_sha256"]=preflight[
                    "preflight_sha256"]
                source_compilation["preflight_status"]=preflight["status"]
        except (ValueError, OSError, KeyError, TypeError) as exc:
            raise EnvironmentBuildBlocked(
                "V216_ZERO_HISTORY_SOURCE_COMPILER_INVALID:"
                +str(exc).split(":",1)[0]) from exc
        # Build the exact original v281 measurement *worklist* from the
        # sealed same-build physical item relation. This does not select
        # F/O on the user's behalf, run Native or approve the candidate.
        if source_compilation["status"]==(
                "FRESH_V191_V211_V213_COMPILED_UNADMITTED"):
            try:
                measurement_plan=consumable_simc_relation.plan_physical_native_measurements(
                    stage_root=source_compilation["stage_root"],
                    relation=collected.get(
                        "fresh_consumable_simc_effect_relation"),
                    build=collected["expected_game_build"],
                    simc_revision=source_compilation["simc_revision"])
            except (consumable_simc_relation.SimCRelationBlocked,
                    OSError,ValueError,KeyError,TypeError) as exc:
                raise EnvironmentBuildBlocked(
                    "V216_AUTO_PHYSICAL_MEASUREMENT_SOURCE_INVALID:"
                    +str(exc).split(":",1)[0]) from exc
            progress["automatic_F_O_measurement_candidates_unadmitted"]=measurement_plan
            source_compilation["automatic_F_O_measurement_candidates_unadmitted"]=measurement_plan
            # Exact static O comes from the v275 pinned DBC, not buffed JSON2.
            oil_work=measurement_plan.get("oil",[])
            if oil_work:
                upstream=collected.get("fresh_pinned_v211_source")
                if (type(upstream) is dict and upstream.get("status")==
                        "PINNED_V211_AND_GENERATED_SOURCES_SEALED"):
                    try:
                        original_oil=oil_raw_source.from_v275(
                            pinned_source=upstream,
                            stage_root=source_compilation["stage_root"],
                            game_build=collected["expected_game_build"],
                            simc_revision=source_compilation["simc_revision"],
                            enchant_ids={r["simc_enchant_id"]
                                         for r in oil_work})
                    except (oil_raw_source.OilSourceBlocked,
                            OSError,ValueError,KeyError,TypeError) as exc:
                        raise EnvironmentBuildBlocked(
                            "V216_ORIGINAL_OIL_SOURCE_DRIFT:"
                            +str(exc).split(":",1)[0]) from exc
                    source_compilation[
                        "unbuffed_oil_original_simc_source_unadmitted"]=original_oil
                    progress[
                        "unbuffed_oil_original_simc_source_unadmitted"]=original_oil
                else:
                    progress["requires"].append(
                        "SAME_BUILD_PINNED_SIMC_OIL_STATIC_SOURCE_PENDING")
            if auto_select_default_F and selected_budget_items is None:
                # Select a deterministic top-quality physical F from the
                # COMPLETE sealed v281 source before opening any v278 case.
                # Other distinct flask effects remain independent options.
                default_F=_auto_default_F_from_sealed_v281_worklist(
                    measurement_plan)
                progress["automatic_default_F_source_selection_unadmitted"]=default_F
                source_compilation[
                    "automatic_default_F_source_selection_unadmitted"]=default_F
                selected_budget_items=default_F[
                    "selected_physical_items_unadmitted"]
                if selected_budget_items is None:
                    progress["requires"].extend(default_F["requires"])
                else:
                    # Explicit default no-oil is a real internal selection,
                    # not v222's earlier source-only O=0 preview assumption.
                    progress["requires"]=[
                        reason for reason in progress["requires"]
                        if reason!=
                        "WEAPON_OIL_O_EXACT_APPLICATION_AND_RATING_PENDING"]
        # Source-selected consumables are tested through the original
        # v269 JSON2 before/after comparer, with an immutable shared baseline.
        # No blanket item-quality or weapon-eligibility certification: the
        # product must first have a complete same-build source compilation
        # and an internal local profile with precombat snapshot_stats.
        effect_observations=[]
        auto_F_calls=0
        if auto_native_F:
            # The buffed v278 oil measurement is no longer an O budget
            # source, so no F Native calls need to be reserved for it.
            oil_reserved=0
            if (auto_select_default_F and selected_budget_items is None):
                auto_rows=[]
                auto_state={
                    "status":"AUTO_F_SOURCE_SELECTION_PENDING",
                    "requires":["AUTO_F_DEFAULT_EXACT_ITEM_SOURCE_PENDING"],
                    "per_item":[],"new_native_calls":0,
                    "F_approved":False,"environment_ready":False}
            else:
                auto_rows,auto_state=_auto_F_native_from_sealed_v281(
                    collected=collected,compilation=source_compilation,
                    binary=binary,max_new_native_calls=8-oil_reserved,
                    selected_item_id=(selected_budget_items["flask_item_id"]
                                      if selected_budget_items is not None
                                      else None))
            effect_observations.extend(auto_rows)
            auto_F_calls=auto_state["new_native_calls"]
            progress["automatic_F_native_measurements_unadmitted"]=auto_state
            source_compilation[
                "automatic_F_native_measurements_unadmitted"]=auto_state
            progress["requires"].extend(auto_state["requires"])
        if auto_native_O:
            # v269/v278 buffed-stat oil comparisons are not a static O
            # source. Preserve the user request as a source-only inspection,
            # not a hidden Native that cannot certify the desired number.
            original=source_compilation.get(
                "unbuffed_oil_original_simc_source_unadmitted")
            unresolved=(type(original) is not dict or
                any(r.get("static_CHMV_vector") is None
                    for r in original.get("items",[])))
            oil_state={
                "status":"O_BUFFED_NATIVE_SKIPPED_STATIC_SOURCE_ONLY",
                "requires":(
                    ["O_SIMC_SCALED_STATIC_RATING_PENDING"]
                    if unresolved else []),
                "per_item":[],"new_native_calls":0,
                "legacy_buffed_native_not_used_as_static_O":True,
                "O_approved":False,"environment_ready":False}
            progress["automatic_O_native_measurements_unadmitted"]=oil_state
            source_compilation[
                "automatic_O_native_measurements_unadmitted"]=oil_state
            progress["requires"].extend(oil_state["requires"])
        # Count all F/O effect observations ONCE in the shared block below.
        if effect_probe_requests:
            if source_compilation["status"]!=(
                    "FRESH_V191_V211_V213_COMPILED_UNADMITTED"):
                progress["requires"].append(
                    "F_O_SIMC_EFFECT_PROBES_WAIT_FOR_SAME_BUILD_CATALOG")
            else:
                for request in effect_probe_requests:
                    bound_item=None
                    native_token=request.get("token")
                    if "item_id" in request:
                        # An internal physical item selection must use the
                        # sealed same-build v281 item→SimC join; its source
                        # status grants measurement only, not F/O approval.
                        try:
                            bound_item=consumable_simc_relation.resolve_native_input(
                                stage_root=source_compilation["stage_root"],
                                relation=collected.get(
                                    "fresh_consumable_simc_effect_relation"),
                                build=collected["expected_game_build"],
                                simc_revision=source_compilation["simc_revision"],
                                kind=request["kind"],item_id=request["item_id"],
                                hand=request.get("hand"))
                        except (consumable_simc_relation.SimCRelationBlocked,
                                OSError,ValueError,KeyError,TypeError) as exc:
                            raise EnvironmentBuildBlocked(
                                "V216_ZERO_HISTORY_PHYSICAL_EFFECT_SOURCE_INVALID:"
                                +str(exc).split(":",1)[0]) from exc
                        if bound_item is None:
                            progress["requires"].append(
                                "F_O_EXACT_ITEM_SIMC_SOURCE_PENDING")
                            continue
                        native_token=bound_item["simc_input_token"]
                    try:
                        observation=native_effect_pair.measure(
                            stage_root=source_compilation["stage_root"],
                            source_profile_path=request["source_profile_path"],
                            binary=binary,
                            simc_revision=source_compilation["simc_revision"],
                            kind=request["kind"],token=native_token)
                    except (native_effect_pair.NativePairBlocked,
                            OSError,ValueError,KeyError,TypeError) as exc:
                        raise EnvironmentBuildBlocked(
                            "V216_ZERO_HISTORY_NATIVE_EFFECT_INVALID:"
                            +str(exc).split(":",1)[0]) from exc
                    if bound_item is not None:
                        observation={
                            **observation,
                            "physical_item_native_source_unadmitted":bound_item}
                    effect_observations.append(observation)
        if effect_observations or type(source_compilation.get(
                "unbuffed_oil_original_simc_source_unadmitted")) is dict:
            # Count automatic and explicit v278 measurements exactly once.
            # This block also runs without manual effect_probe_requests.
            progress["new_native_calls"]+=sum(
                x["new_native_calls"] for x in effect_observations)
            progress["F_O_effect_numeric_candidates_unadmitted"]={
                "F":[x.get("F_candidate_unadmitted")
                     for x in effect_observations if x["kind"]=="flask"],
                "O":[x.get("O_candidate_unadmitted")
                     for x in effect_observations
                     if x["kind"]=="temporary_enchant"]}
            progress["requires"].append(
                "F_O_HIGHEST_QUALITY_AND_WEAPON_APPLICABILITY_PENDING")
            native_F_O=_zero_history_F_O_native_component_candidates(
                observations=effect_observations,
                game_build=collected["expected_game_build"],
                simc_revision=source_compilation["simc_revision"])
            unbuffed=source_compilation.get(
                "unbuffed_oil_original_simc_source_unadmitted")
            if unbuffed is not None:
                native_F_O=oil_raw_source.project_source_oils(
                    source=unbuffed,
                    worklist=source_compilation[
                        "automatic_F_O_measurement_candidates_unadmitted"],
                    native_numeric=native_F_O)
            progress["physical_F_O_native_source_candidates_unadmitted"]=native_F_O
            source_compilation["physical_F_O_native_source_candidates_unadmitted"]=native_F_O
            quality_weapon=_zero_history_quality_weapon_candidate_join(
                numeric=native_F_O,
                weapon_source=source_compilation.get(
                    "representative_oil_source_options_unadmitted"),
                game_build=collected["expected_game_build"],
                simc_revision=source_compilation["simc_revision"])
            progress["observed_quality_weapon_choices_unadmitted"]=quality_weapon
            source_compilation["observed_quality_weapon_choices_unadmitted"]=quality_weapon
            if selected_budget_items is not None:
                selected_check=_zero_history_selected_F_O_v222_reconcile(
                    selected=selected_budget_items,numeric=native_F_O,
                    choices=quality_weapon,
                    existing_budget=source_compilation.get(
                        "preprofile_budget_arithmetic_unadmitted"),
                    budget_evidence=zero_history_budget_evidence)
                progress["selected_physical_F_O_budget_link_unadmitted"]=selected_check
                source_compilation["selected_physical_F_O_budget_link_unadmitted"]=selected_check
        # For a web Build with no internal physical selection, a uniquely
        # measured flask family may supply a *source-only* B/T preview.
        # No oil is assumed only in that preview; do not turn this into a
        # default oil choice or product admission.
        numeric_selection=selected_budget_items
        if numeric_selection is None and effect_observations:
            auto_preview=_source_only_one_flask_budget_preview(
                preflight=preflight,
                worklist=source_compilation.get(
                    "automatic_F_O_measurement_candidates_unadmitted"),
                native_numeric=native_F_O,source_choices=quality_weapon)
            progress["auto_observed_flask_budget_preview_unadmitted"]=auto_preview
            source_compilation[
                "auto_observed_flask_budget_preview_unadmitted"]=auto_preview
            numeric_selection=auto_preview["selected_physical_items_unadmitted"]
            if auto_select_default_F and numeric_selection is not None:
                # The season user explicitly chose best observed same-effect
                # flask and no oil. The preview gives an ItemID ONLY;
                # actual F requires the original v278 sealed Native cases.
                selected_budget_items=dict(numeric_selection)
                selected_check=_zero_history_selected_F_O_v222_reconcile(
                    selected=selected_budget_items,numeric=native_F_O,
                    choices=quality_weapon,
                    existing_budget=source_compilation.get(
                        "preprofile_budget_arithmetic_unadmitted"),
                    budget_evidence=zero_history_budget_evidence)
                progress["selected_physical_F_O_budget_link_unadmitted"]=selected_check
                source_compilation["selected_physical_F_O_budget_link_unadmitted"]=selected_check
                progress["automatic_observed_F_explicit_no_oil_selected_item_id"]=(
                    selected_budget_items["flask_item_id"])
        if numeric_selection is not None:
            selected_numeric=_zero_history_auto_v222_numeric_preview(
                preflight=preflight,
                native_numeric=(
                    native_F_O if effect_observations else
                    {"flask":[],"oil":[]}),
                source_choices=(
                    quality_weapon if effect_observations else
                    {"oil_representative_weapon_matches_unadmitted":[]}),
                selected=numeric_selection,
                gem_ratings=(zero_history_gem_ratings
                    if zero_history_gem_ratings is not None else
                    (preflight or {}).get(
                        "physical_gem_raw_rating_by_id_unadmitted")),
                target_ilevel=fresh_collection_inputs[
                    "representative_request"]["target_ilevel"],
                manual_final_T=manual_T,
                no_oil_is_preview_assumption=(
                    selected_budget_items is None))
            progress["selected_auto_v222_numeric_preview_unadmitted"]=selected_numeric
            source_compilation["selected_auto_v222_numeric_preview_unadmitted"]=selected_numeric
            if selected_numeric["calculation"] is None:
                # Missing physical G/J/F/O is a core *data* PENDING,
                # not a reason to discard already sealed v191/v211/v213.
                # Do not feed an incomplete preview into v212's strict
                # complete-numeric contract.
                progress["requires"].extend(
                    "SELECTED_AUTO_GJFO_"+reason
                    for reason in selected_numeric["requires"])
            else:
                profile_inputs=_zero_history_v098_profile_source_inputs(
                    numeric_preview=selected_numeric,
                    physical_sources=native_F_O)
                # A source-only v098 profile can now reuse the same exact
                # ItemID/SimC receipt without manually assembling payloads.
                # Never invoke v098 build/session from this unadmitted stage.
                source_compilation[
                    "v098_source_only_profile_inputs_unadmitted"]=profile_inputs
        if (selected_budget_items is not None and
                "selected_physical_F_O_budget_link_unadmitted" not in progress):
            waiting={
                "status":"SELECTED_PHYSICAL_F_O_SOURCE_PENDING",
                "selected_physical_items":selected_budget_items,
                "missing":["PHYSICAL_F_O_NATIVE_OBSERVATIONS_OR_CATALOG_PENDING"],
                "v222_numbers_reconciled":False,
                "source_admission_performed_here":False,
                "environment_ready":False,"user_selectable":False,
                "new_native_calls":0,"network_calls":0}
            progress["selected_physical_F_O_budget_link_unadmitted"]=waiting
            source_compilation["selected_physical_F_O_budget_link_unadmitted"]=waiting
        # Reuse original v266/v271 nominal J and v281/v278 selected SimC
        # numeric F in one compact source-owner input. Quality/use/sockets
        # still belong to the internal verifier, NOT this preview.
        jf_numeric=_fresh_source_owner_selected_J_F_numeric(
            preflight=preflight,compilation=source_compilation,
            selected_physical_items=selected_budget_items)
        source_compilation[
            "selected_J_F_source_owner_numeric_unadmitted"]=jf_numeric
        progress["selected_J_F_source_owner_numeric_unadmitted"]=jf_numeric
        # Reuse existing selected v230/v220 and v281/v278 observed quality
        # comparisons. The highest COMPARABLE OBSERVED effect now satisfies
        # quality preference; it does not replace v220's source/input/budget
        # proofs or itself install the new season.
        quality_scope=_fresh_source_owner_observed_J_F_quality(
            preflight=preflight,compilation=source_compilation,
            owner_numeric=jf_numeric)
        source_compilation[
            "selected_J_F_source_owner_quality_unadmitted"]=quality_scope
        progress["selected_J_F_source_owner_quality_unadmitted"]=quality_scope
        # The new season's exact source stage is now a versioned Environment
        # unit, independent of v098/optimizer sessions. It is not an install.
        if (preflight is not None and
                preflight.get("schema")==FRESH_SOURCE_PREFLIGHT_SCHEMA and
                source_compilation["status"]==
                    "FRESH_V191_V211_V213_COMPILED_UNADMITTED" and
                all(type(source_compilation.get(key)) is dict and
                    type(source_compilation[key].get("receipt_sha256")) is str
                    for key in ("v191_stage","v211_stage","v213_stage"))):
            # Only the original v217 COMPLETE stage receipts can authorize
            # a versioned source manifest. An old/synthetic compiler summary
            # without sealed receipts remains a source-only diagnostic.
            staged_numeric=source_compilation.get(
                "selected_auto_v222_numeric_preview_unadmitted")
            staged=_stage_source_environment_only(
                compilation=source_compilation,preflight=preflight,
                target_ilevel=fresh_collection_inputs[
                    "representative_request"]["target_ilevel"],
                selected_numeric=(
                    staged_numeric
                    if type(staged_numeric) is dict and
                    staged_numeric.get("status")==(
                        "SELECTED_GJFO_V222_ARITHMETIC_PREVIEW_UNADMITTED")
                    and type(staged_numeric.get("calculation")) is dict
                    else None))
            progress["versioned_environment_source_stage"]=staged
            source_compilation["versioned_environment_source_stage"]=staged
            # G owner reuses the SAME original v277 sealed Native result.
            # A source-only preview or mock without its original receipt
            # stays pending, and none of this implies complete G/J/F/O.
            owner_G=_fresh_source_owner_native_G_component(
                native_G=native_G,preflight=preflight,
                compilation=source_compilation,staged=staged,
                target_ilevel=fresh_collection_inputs[
                    "representative_request"]["target_ilevel"])
            if owner_G is not None:
                source_compilation[
                    "native_G_source_owner_component_not_full_environment"]=owner_G
                progress["native_G_source_owner_status"]=(
                    "EXACT_GENERIC_G_NATIVE_PROVENANCE_REUSED_J_F_O_PENDING")
            # Original source owner may now supply J from v221/v230/v232
            # nominal/socket evidence and F from exact verified v278 JSON2
            # cases. An incomplete component never blocks valid G/O reuse.
            owner_J_F=_fresh_source_owner_original_J_F_components(
                preflight=preflight,compilation=source_compilation,
                staged=staged,owner_numeric=jf_numeric,
                quality_scope=quality_scope,
                effect_observations=effect_observations)
            source_compilation[
                "original_J_F_verified_components_not_full_environment"]=owner_J_F
            progress["original_J_F_verified_component_names"]=sorted(owner_J_F)
            if not source_compilation["missing"]:
                # Default web Build can directly consume the ORIGINAL
                # four source-owned budget components without a Python
                # callback; the optional independent provider still wins.
                if verified_install_provider is None:
                    confirmed=_fresh_original_default_base_install_inputs(
                        preflight=preflight,staged=staged,
                        original_G=owner_G,original_J_F=owner_J_F,
                        selected_budget_items=selected_budget_items,
                        target_ilevel=fresh_collection_inputs[
                            "representative_request"]["target_ilevel"],
                        user=user)
                else:
                    confirmed=verified_install_provider(
                        compilation=source_compilation,preflight=preflight,
                        staged=staged,selected_numeric=staged_numeric,
                        selected_physical_items=selected_budget_items,
                        target_ilevel=fresh_collection_inputs[
                            "representative_request"]["target_ilevel"])
                if confirmed is not None:
                    need(type(confirmed) is dict and set(confirmed)=={
                        "trusted_budget_evidence",
                        "trusted_policy_A_receipts_by_id"} and
                         type(confirmed["trusted_budget_evidence"]) is dict and
                         type(confirmed["trusted_policy_A_receipts_by_id"]) is dict,
                         "V216_INSTALL_PROVIDER_VERIFIED_OUTPUT_FIELDS")
                    # Only an explicit, empty oil-hand selection owns O=0.
                    # Attach the existing v222 receipt, not a preview or an
                    # invented season constant. Conflicting provider O blocks.
                    trusted_budget=_fresh_source_owner_merge_native_G(
                        trusted_budget_evidence=confirmed["trusted_budget_evidence"],
                        owner_G=owner_G)
                    trusted_budget=_fresh_source_owner_merge_original_J_F(
                        trusted_budget_evidence=trusted_budget,
                        owner_components=owner_J_F)
                    trusted_budget=_fresh_source_owner_exact_no_oil(
                        preflight=preflight,
                        selected_budget_items=selected_budget_items,
                        trusted_budget_evidence=trusted_budget)
                    trusted_budget=_fresh_source_owner_crosscheck_selected_J_F(
                        owner_numeric=jf_numeric,
                        trusted_budget_evidence=trusted_budget)
                    policy_A_receipts=(
                        _fresh_source_owner_merge_policy_A_original_source_relation(
                            preflight=preflight,staged=staged,
                            trusted_policy_A_receipts_by_id=confirmed[
                                "trusted_policy_A_receipts_by_id"]))
                    installed=_install_verified_fresh_environment_only(
                        compilation=source_compilation,staged=staged,
                        trusted_budget_evidence=trusted_budget,
                        trusted_policy_A_receipts_by_id=policy_A_receipts,
                        target_ilevel=fresh_collection_inputs[
                            "representative_request"]["target_ilevel"],
                        manual_final_T=manual_T)
                    source_compilation["verified_environment_install"]=installed
                    progress["source_only_pending_before_install"]=list(
                        progress["requires"])
                    progress.update({
                        "status":installed["status"],"requires":[],
                        "environment_ready":True,
                        "environment_installed":True,"options_published":True,
                        "G":installed["official_G"],"J":installed["official_J"],
                        "F":installed["official_F"],
                        "O":dict(installed["official_O"]),
                        "B":installed["official_B"],"T":installed["official_T"],
                        "versioned_environment_installed":installed})
        progress["source_compilation_status"]=source_compilation["status"]
        progress["source_compilation_missing"]=source_compilation["missing"]
        if source_compilation["missing"]:
            progress["requires"].extend(
                "FRESH_COMPILER_INPUT_"+name+"_PENDING"
                for name in source_compilation["missing"])
        return {**collected,
                **({key:progress[key] for key in (
                    "G","J","F","O","B","T","environment_ready",
                    "environment_installed")} if progress["environment_ready"] else {}),
                "source_compilation":source_compilation,
                "native_G_numeric_source":native_G,
                "native_effect_numeric_sources_unadmitted":effect_observations,
                "native_calls":progress["new_native_calls"],
                "zero_history_build":progress,
                "normal_build_entry":True}
    # Existing v217 stages assemble the same v211/v213 source candidate
    # inside this original Build request. No session is created before the
    # ensuing preflight/required-budget barrier; never imply installation.
    fresh_snapshot_folder = None
    fresh_stage_root = None
    if fresh_source_stage_inputs is not None:
        valid_keys = (
            frozenset(("stage_root", "v191_path",
                        "simc_source_dir", "simc_manifest_path")),
            frozenset(("stage_root", "fresh_v191_inputs",
                        "simc_source_dir", "simc_manifest_path")))
        input_keys = set(fresh_source_stage_inputs) if type(
            fresh_source_stage_inputs) is dict else set()
        need(source_catalog_path is None and
             (frozenset(input_keys) in valid_keys or
              frozenset(input_keys - {"wago_snapshot_folder"}) in valid_keys
              and "wago_snapshot_folder" in input_keys),
             "V216_FRESH_STAGE_INPUT_CONTRACT_INVALID")
        need(type(expected_new_season_build) is str,
             "V216_EXPLICIT_NEW_SEASON_BUILD_REQUIRED")
        compile_inputs = dict(fresh_source_stage_inputs)
        fresh_snapshot_folder = compile_inputs.pop(
            "wago_snapshot_folder", None)
        fresh_stage_root = (compile_inputs["stage_root"]
                            if fresh_snapshot_folder is not None else None)
        prepared = fresh_stage.compile_fresh_candidate(
            **compile_inputs,
            expected_game_build=expected_new_season_build,
            expected_simc_revision=revision)
        source_catalog_path = prepared["source_catalog_path"]
    # A freshly collected v213 source must first pass the shared source
    # preflight. With G/J/F/O incomplete it must NOT be fed to the legacy
    # v212 manifest, which requires old exact 7967/8025 approval and v098.
    # Fail before any session file creation or historical cache access.
    if source_catalog_path is not None:
        candidate_path=pathlib.Path(source_catalog_path)
        if candidate_path.is_file() and not candidate_path.is_symlink():
            candidate,_=environment_manifest.read_json(candidate_path)
            if candidate.get("enchant_classification",{}).get(
                    "source_manifest_sha256") is not None:
                need(type(expected_new_season_build) is str and
                     re.fullmatch(r"[0-9]+(?:\.[0-9]+){3}",
                                  expected_new_season_build) is not None,
                     "V216_EXPLICIT_NEW_SEASON_BUILD_REQUIRED")
                selected_gem_layout=(
                    fresh_gem_layout_receipt if
                    fresh_gem_layout_receipt is not None else
                    (profile_stage_receipt.get("socket_layout") if
                     type(profile_stage_receipt) is dict else None))
                preflight=preflight_new_season_source(
                    source_catalog_path=candidate_path,
                    expected_game_build=expected_new_season_build,
                    expected_simc_revision=revision,
                    source_snapshot_folder=fresh_snapshot_folder,
                    source_stage_root=fresh_stage_root,
                    budget_evidence=fresh_gjfo_evidence,
                    gem_layout_receipt=selected_gem_layout,
                    gem_rating_by_id=fresh_gem_rating_by_id,
                    standard_budget_evidence_by_ilevel=(
                        fresh_standard_budget_evidence_by_ilevel),
                    standard_budget_reference_track=(
                        fresh_standard_budget_reference_track),
                    g_native_receipt_paths_by_ilevel=(
                        fresh_g_native_receipt_paths_by_ilevel),
                    simc_effect_snapshot_case=(
                        fresh_simc_effect_snapshot_case),
                    target_ilevel=(
                        user["target"]["ilevel"]
                        if (fresh_standard_budget_evidence_by_ilevel is not None
                            or fresh_gjfo_evidence is not None)
                        and type(user) is dict
                        and type(user.get("target")) is dict else None),
                    manual_final_T=(
                        user["target"].get("final_T")
                        if (fresh_standard_budget_evidence_by_ilevel is not None
                            or fresh_gjfo_evidence is not None)
                        and type(user) is dict
                        and type(user.get("target")) is dict else None))
                raise EnvironmentBuildBlocked(
                    "V216_FRESH_SOURCE_PROVENANCE_PASS_GJFO_NOT_READY:"
                    +preflight["preflight_sha256"])
    root = pathlib.Path(sessions_root).expanduser().resolve()
    folder = pathlib.Path(session_folder).expanduser().resolve()
    need(SESSION_KEY.fullmatch(folder.name) is not None and
         folder.parent == root and folder.is_dir() and
         not folder.is_symlink(),
         "V216_SESSION_FOLDER_OUTSIDE_ROOT")
    generated = folder / "generated"
    need(not generated.is_symlink(), "V216_GENERATED_DIRECTORY_SYMLINK_BLOCKED")
    generated.mkdir(parents=True, exist_ok=True)
    bootstrap_path = generated / "v098_bootstrap_result.json"
    bootstrap_encoded = json.dumps(
        bootstrap_result, sort_keys=True, ensure_ascii=False,
        indent=2, allow_nan=False) + "\n"
    if bootstrap_path.is_file():
        need(not bootstrap_path.is_symlink() and
             bootstrap_path.read_text(encoding="utf8") == bootstrap_encoded,
             "EXISTING_BOOTSTRAP_FILE_CHANGED")
    else:
        _atomic_write(bootstrap_path, bootstrap_encoded)

    source_input = (pathlib.Path(source_catalog_path).expanduser()
                    if source_catalog_path is not None else None)
    need(source_input is not None and not source_input.is_symlink(),
         "V213_SOURCE_CATALOG_SYMLINK_BLOCKED")
    source_path = source_input.resolve() if source_input is not None else None
    need(source_path is not None and source_path.is_file(),
         "V213_SOURCE_CATALOG_NOT_PACKAGED")
    source_document, source_raw_sha = environment_manifest.read_json(source_path)
    # Product's installed v213 file is a fixed app-local source, not an HTTP
    # parameter. Existing v106 already keys its sessions on v213/gear/tier/
    # consumables bytes; do not introduce a new session fingerprint and
    # invalidate historical Native caches for an accounting-only audit.
    package_root = pathlib.Path(__file__).resolve().parents[1]
    installed_catalog = (package_root / "data" /
                         "current_season_source_to_catalog.json")
    installed_source_proof = (season_budget_source_paths is None and
            season_budget_evidence is None and
            source_path == installed_catalog and
            not user.get("special_items") and
            not user.get("embellishments") and
            not user.get("verified_enchant"))
    if installed_source_proof:
        season_budget_source_paths = {
            "gear": package_root / "data" /
                    "current_season_product_gear_db.json",
            "tier": package_root / "data" /
                    "current_season_tier_itemsets.json",
            "budget": package_root / "data" /
                      "current_season_chmv_consumables.json",
            "reference": package_root / "integration_probes" / "data" /
                         "midnight_s2_ilvl_chmv_reference_v1.json",
        }
    # Optional installed same-season source proof; never a browser argument.
    # The pure arithmetic contract alone cannot validate source provenance.
    need(not (season_budget_evidence is not None and
              season_budget_source_paths is not None),
         "V216_SEASON_BUDGET_TWO_EVIDENCE_MODES")
    linked_source_proof = None
    if season_budget_source_paths is not None:
        source_scenario_path = generated / "scenario.json"
        if source_scenario_path.is_file():
            need(not source_scenario_path.is_symlink(),
                 "V216_SOURCE_SCENARIO_SYMLINK_BLOCKED")
            pre_oil_scenario, _ = environment_manifest.read_json(
                source_scenario_path)
        else:
            need(not installed_source_proof,
                 "V216_INSTALLED_SOURCE_SCENARIO_NOT_GENERATED")
            pre_oil_scenario = None
        try:
            linked_source_proof = season_source_proof.produce(
                catalog=source_document, catalog_sha=source_raw_sha,
                source_paths=season_budget_source_paths, user=user,
                bootstrap=bootstrap_result,
                physical_profile=(generated / "profile.simc").read_text(
                    encoding="utf8"),
                pre_oil_scenario=pre_oil_scenario)
            season_budget_evidence = linked_source_proof["evidence"]
        except (season_source_proof.SourceBudgetBlocked, OSError) as exc:
            raise EnvironmentBuildBlocked(
                "V216_SEASON_SOURCE_PROOF_BLOCKED:" + str(exc)) from exc
    if season_budget_evidence is None:
        season_budget = {
            "schema": season_budget_contract.SCHEMA,
            "status": "INSTALLED_REFERENCE_ONLY_GJFO_REFRESH_NOT_VERIFIED",
            "source_authentication_performed_here": False,
            "native_calls": 0, "network_calls": 0,
        }
    else:
        try:
            target = user.get("target") if type(user) is dict else None
            manual_T = target.get("final_T") if type(target) is dict else None
            season_budget = season_budget_contract.reconcile(
                source_catalog=source_document,
                source_artifact_sha256=source_raw_sha,
                evidence=season_budget_evidence,
                plan=bootstrap_result.get("plan"),
                target_ilevel=bootstrap_result.get("target_ilevel"),
                manual_final_T=manual_T)
            if linked_source_proof is not None:
                season_budget = {
                    **season_budget,
                    "status": linked_source_proof["status"],
                    "source_links_verified_by_v223": True,
                    "source_input_sha256":
                        linked_source_proof["source_input_sha256"],
                    "reference_rounded":
                        linked_source_proof["reference_rounded"],
                    "profile_oil_serialization":
                        linked_source_proof["profile_oil_serialization"],
                }
        except season_budget_contract.SeasonBudgetBlocked as exc:
            raise EnvironmentBuildBlocked(
                "V216_SEASON_BUDGET_PROOF_OR_ARITHMETIC_BLOCKED:" + str(exc)
            ) from exc
    # Verify the previous sealed source before compiling or writing ANY
    # new manifest/receipt. A source drift must not alter historical session
    # bytes, even if the numeric B/T happens to remain equal.
    prior_receipt = generated / "environment_build_receipt.json"
    if prior_receipt.is_file():
        previous_receipt = read_receipt(prior_receipt, folder.name)
        previous_budget = previous_receipt.get("season_budget") or {}
        previous_source_sha = previous_budget.get("source_input_sha256")
        current_source_sha = season_budget.get("source_input_sha256")
        # A sealed G/J/F/O source proof cannot be silently replaced inside
        # a pre-existing session, regardless of unchanged B/T arithmetic.
        if previous_source_sha is not None:
            need(previous_source_sha == current_source_sha,
                 "V216_SEALED_SESSION_GJFO_SOURCE_CHANGED")
    scope = environment_scope_identity(user)
    previous = find_previous_environment(root, folder, scope["scope_sha256"])
    previous_manifest = previous["manifest"] if previous else None
    previous_path = previous["manifest_path"] if previous else None

    manifest_path = generated / "environment_manifest.json"
    result = environment_manifest.compile_from_paths(
        source_path, bootstrap_path, generated,
        v208_start_receipt_path, package_manifest_path, previous_path)
    result_payload = {key: value for key, value in result.items()
                      if key != "manifest_sha256"}
    need(result.get("manifest_sha256") ==
         digest(canonical(result_payload).encode("utf8")),
         "V216_V212_MANIFEST_DIGEST_INVALID")
    manifest_encoded = json.dumps(
        result, sort_keys=True, ensure_ascii=False,
        indent=2, allow_nan=False) + "\n"
    manifest_reused = (manifest_path.is_file() and
                       not manifest_path.is_symlink() and
                       manifest_path.read_text(encoding="utf8") ==
                       manifest_encoded)
    if not manifest_reused:
        _atomic_write(manifest_path, manifest_encoded)

    source_provenance = result["source_catalog"]
    v191 = source_provenance["v191"]
    v211 = source_provenance["v211"]
    ui = result["approved_ui_catalog"]
    profile = result["target_profile"]
    previous_profile = (previous_manifest or {}).get("target_profile", {})
    previous_ui = (previous_manifest or {}).get("approved_ui_catalog", {})
    static_sha = ((profile.get("static_cache") or {}).get("sha256"))
    previous_static_sha = ((previous_profile.get("static_cache") or {}).get("sha256"))
    same_static_cache = static_sha is not None and static_sha == previous_static_sha
    same_profile = (
        previous_profile.get("normalized_result_sha256") ==
            profile.get("normalized_result_sha256") and
        previous_profile.get("profile_files") == profile.get("profile_files"))
    same_ui = previous_ui.get("normalized_sha256") == ui.get("normalized_sha256")
    steps = [
        _step("v191_source_collection", "REUSED_EMBEDDED",
              source_sha256=v191.get("sha256"),
              source_inputs_sha256=v191.get("sha256_by_input")),
        _step("v211_simc_effect_classification", "REUSED_EMBEDDED",
              source_sha256=v211.get("sha256")),
        _step("v213_source_to_catalog", "REUSED_PACKAGED_ARTIFACT",
              artifact_sha256=source_raw_sha,
              manifest_sha256=source_document.get("manifest_sha256")),
        _step("v196_user_catalog_projection",
              "COMPUTED_IDENTICAL" if same_ui else "COMPUTED_CHANGED",
              normalized_sha256=ui.get("normalized_sha256")),
        _step("v098_target_profile",
              ("REUSED_VERIFIED_ARTIFACTS" if (profile_stage_receipt or {}).get("reused")
               else "RECOVERED_VERIFIED_ARTIFACTS" if (profile_stage_receipt or {}).get("recovered")
               else "EXECUTED_AND_SEALED" if (profile_stage_receipt or {}).get("executed")
               else "COMPUTED_IDENTICAL" if same_profile else "COMPUTED_CHANGED"),
              normalized_result_sha256=profile.get("normalized_result_sha256"),
              profile_files=profile.get("profile_files"),
              stage_receipt_sha256=(profile_stage_receipt or {}).get("receipt_sha256")),
        _step("v212_environment_manifest",
              "COMPILED_IDENTICAL_NO_WRITE" if manifest_reused else
              "COMPILED_CHANGED_WRITTEN",
              manifest_sha256=result.get("manifest_sha256")),
    ]
    dependency_change = result.get("dependency_change") or {}
    changed_inputs = list(dependency_change.get("changed_inputs", []))
    invalidated = list(dependency_change.get("invalidated_components", []))
    reused_components = [row["component"] for row in steps
                         if row["status"].startswith("REUSED")]
    rebuilt_components = [row["component"] for row in steps
                          if row["status"] in
                          ("COMPUTED_CHANGED","COMPILED_CHANGED_WRITTEN",
                           "EXECUTED_AND_SEALED")]
    computed_components = [row["component"] for row in steps
                           if row["status"].startswith(("COMPUTED_","COMPILED_"))]
    computed_identical_components = [row["component"] for row in steps
                                     if row["status"] in
                                     ("COMPUTED_IDENTICAL",
                                      "COMPILED_IDENTICAL_NO_WRITE")]
    verified_read_only_components = [row["component"] for row in steps
                                      if row["status"] == "VERIFIED_READ_ONLY"]
    cache_reuse = {
        "installed_v213_artifact_hits": 1,
        "static_item_cache_snapshot_sha256": static_sha,
        "same_static_item_cache_as_previous_environment": same_static_cache,
        "static_item_cache_preserved": True,
        "dps_cache_touched": False,
    }
    payload = {
        "schema": SCHEMA,
        "status": result["status"],
        "session_id": folder.name,
        "environment_scope_sha256": scope["scope_sha256"],
        "environment_manifest_sha256": result["manifest_sha256"],
        "source": {
            "mode": "INSTALLED_VERSIONED_ARTIFACT_ONLY",
            "refresh_performed": False,
            "artifact_sha256": source_raw_sha,
            "manifest_sha256": source_document.get("manifest_sha256"),
            "game_build": source_document.get("game_build"),
            "simc_revision": source_document.get("simc_revision"),
            "refresh_boundary":
                "v191_v211_v213_refresh_requires_a_separately_verified_source_package",
        },
        "steps": steps,
        "season_budget": season_budget,
        "profile_stage": profile_stage_receipt,
        "dependency_change": {
            "status": dependency_change.get("status", "INITIAL_ENVIRONMENT"),
            "previous_session_id": previous.get("session_id") if previous else None,
            "changed_inputs": changed_inputs,
            "invalidated_components": invalidated,
            "reused_components": reused_components,
            "rebuilt_components": rebuilt_components,
            "verified_read_only_components": verified_read_only_components,
            "computed_components": computed_components,
            "computed_identical_components": computed_identical_components,
            "planned_execution_order": list(
                dependency_change.get("planned_execution_order", [])),
            "reusable_candidates": list(
                dependency_change.get("reusable_candidates", [])),
            "dependency_rules_changed": dependency_change.get(
                "dependency_rules_changed", False),
            "season_static_source_unchanged_candidate":
                dependency_change.get("season_static_source_unchanged_candidate",False),
            "season_static_source_identity_scope":
                dependency_change.get("season_static_source_identity_scope"),
            "simc_runtime_only_change":
                dependency_change.get("simc_runtime_only_change",False),
            "season_source_refresh_triggered_by_simc_only":False,
        },
        "cache_reuse": cache_reuse,
        "readiness": {
            "status": result["status"],
            "limitations": list(result.get("readiness_limitations", [])) +
                ["SEASON_GJFO_AUTO_REFRESH_NOT_VERIFIED"],
            "unresolved_dependencies": list(
                result.get("unresolved_dependencies", [])),
            "source_join_audit":
                result.get("source_catalog", {}).get("source_join_audit"),
            "profile_plan_suppliers": {
                "verified": profile.get("profile_supplier_coverage_sha256") is not None,
                "count": result["product_scope"]["profile_supplier_coverage"].get(
                    "current_season_profile_supplier_count"),
                "total": result["product_scope"]["profile_supplier_coverage"].get(
                    "contract_count"),
                "adaptive_native_evidence_complete":
                    result["product_scope"]["profile_supplier_coverage"].get(
                        "adaptive_native_evidence_complete"),
            },
        },
        "native_calls": 0,
        "network_calls": 0,
        "cache_mutations": 0,
        "historical_sessions_preserved": True,
    }
    receipt = {**payload, "receipt_sha256":
               digest(canonical(payload).encode("utf8"))}
    verify_receipt(receipt)
    receipt_path = generated / "environment_build_receipt.json"
    receipt_encoded = json.dumps(
        receipt, sort_keys=True, ensure_ascii=False,
        indent=2, allow_nan=False) + "\n"
    _atomic_write(receipt_path, receipt_encoded)
    return {"manifest": result, "receipt": receipt,
            "manifest_reused": manifest_reused,
            "previous_session_id": previous.get("session_id") if previous else None}


def read_receipt(path, session_id=None):
    path = pathlib.Path(path)
    need(path.is_file() and not path.is_symlink() and
         path.stat().st_size <= MAX_RECEIPT_BYTES,
         "V216_BUILD_RECEIPT_NOT_FOUND_OR_TOO_LARGE")
    try:
        document = json.loads(path.read_text(encoding="utf8"))
        verify_receipt(document)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise EnvironmentBuildBlocked(
            "V216_BUILD_RECEIPT_INVALID:" + type(exc).__name__) from exc
    if session_id is not None:
        need(document.get("session_id") == session_id,
             "V216_BUILD_RECEIPT_SESSION_MISMATCH")
    return document


def public_summary(receipt):
    verify_receipt(receipt)
    return {
        "schema": receipt["schema"],
        "status": receipt["status"],
        "receipt_sha256": receipt["receipt_sha256"],
        "environment_manifest_sha256": receipt["environment_manifest_sha256"],
        "source": {
            "mode": receipt["source"]["mode"],
            "refresh_performed": receipt["source"]["refresh_performed"],
            "artifact_sha256": receipt["source"]["artifact_sha256"],
            "game_build": receipt["source"]["game_build"],
            "simc_revision": receipt["source"]["simc_revision"],
        },
        "steps": receipt["steps"],
        "season_budget": receipt.get("season_budget"),
        "profile_stage": receipt.get("profile_stage"),
        "dependency_change": receipt["dependency_change"],
        "cache_reuse": receipt["cache_reuse"],
        "readiness": receipt["readiness"],
        "native_calls": receipt["native_calls"],
        "network_calls": receipt["network_calls"],
        "cache_mutations": receipt["cache_mutations"],
        "historical_sessions_preserved":
            receipt["historical_sessions_preserved"],
    }
