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

import v212_environment_manifest as environment_manifest

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


def build_environment(*, sessions_root, session_folder, user, binary, revision,
                      static_cache, source_catalog_path, bootstrap_result,
                      v208_start_receipt_path=None, package_manifest_path=None):
    """Reconcile existing inputs and seal one incremental, auditable build.

    Source acquisition is intentionally outside this local coordinator:
    v191/v211/v213 are consumed from the exact installed package artifact.
    A new season/source refresh must first install a separately verified
    versioned source package. The coordinator never silently relabels stale
    source bytes as current.
    """
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
              "COMPUTED_IDENTICAL" if same_profile else "COMPUTED_CHANGED",
              normalized_result_sha256=profile.get("normalized_result_sha256"),
              profile_files=profile.get("profile_files")),
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
                          ("COMPUTED_CHANGED","COMPILED_CHANGED_WRITTEN")]
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
        },
        "cache_reuse": cache_reuse,
        "readiness": {
            "status": result["status"],
            "limitations": list(result.get("readiness_limitations", [])),
            "unresolved_dependencies": list(
                result.get("unresolved_dependencies", [])),
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
        "dependency_change": receipt["dependency_change"],
        "cache_reuse": receipt["cache_reuse"],
        "readiness": receipt["readiness"],
        "native_calls": receipt["native_calls"],
        "network_calls": receipt["network_calls"],
        "cache_mutations": receipt["cache_mutations"],
        "historical_sessions_preserved":
            receipt["historical_sessions_preserved"],
    }
