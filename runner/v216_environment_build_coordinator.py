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
import v222_season_budget_contract as season_budget_contract
import v223_installed_season_budget_source as season_source_proof
import v213_source_to_catalog as source_to_catalog
import v161_wago_db2_snapshot as wago_snapshot
import v242_authenticated_season_source_stage as discovery_stage
import v163_zero_seed_db2_join as season_join
import v245_db2_first_tier_discovery as tier_db
import v250_raid_tier_bonus_corroboration as raid_bonus
import v251_db2_raid_tier_simc_bridge as tier_simc_bridge
import v217_stage_execution_engine as stage_engine
import v196_current_season_user_catalog as user_catalog
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


FRESH_SOURCE_PREFLIGHT_SCHEMA="v216_new_season_source_preflight_v1"


def preflight_new_season_source(*, source_catalog_path, expected_game_build,
                                expected_simc_revision):
    """Inspect a freshly assembled v213 artifact in the NORMAL Build path.

    This does not install an environment or require previously held source
    values. Source acquisition and item-level G/J/F/O authentication are
    still prerequisites of final admission; checking local hashes does not
    constitute upstream retrieval authentication.
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
        "requires":["G/J/F/O_VERIFIED_SOURCE_RECEIPTS",
                    "POLICY_A_OPTION_ADMISSION",
                    "NEW_SEASON_TARGET_PROFILE_AND_V212_MANIFEST"],
        "source_retrieval_authenticated_by_this_stage":False,
        "native_calls":0,"network_calls":0,"cache_mutations":0,
    }
    return {**payload,"preflight_sha256":
        digest(canonical(payload).encode("utf8"))}



def _join_authenticated_season_source(*,stage_root,output_dir,
                                      expected_game_build,discovered,
                                      wago_stage_receipt):
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
            build=expected_game_build,expansion_id=scope["expansion_id"])
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


def collect_wago_new_season_source(*, sessions_root, expected_game_build,
                                   fetch=None, credentials=None,
                                   discovery_transport=None,
                                   tier_transport=None,
                                   bonus_transport=None):
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
    linked=_join_authenticated_season_source(
        stage_root=stage_root,output_dir=output_dir,
        expected_game_build=expected_game_build,
        discovered=discovered,
        wago_stage_receipt=stage["receipt_sha256"])
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
        "fresh_tier":fresh_tier,
        "fresh_tier_raid_bonus_corroboration":tier_bonus,
        "fresh_tier_simc_candidate_bridge":tier_bridge,
        "tier_discovery_mode":"DB2_FIRST_NO_PUBLISHER_NAME_LOOKUP",
        "network_calls_by_stage":(len(wago_snapshot.TABLES)
            if stage["executed"] else 0)+discovered["network_calls_by_stage"]+
            fresh_tier["network_calls_by_stage"]+
            tier_bonus["network_calls_by_stage"],
        "native_calls":0,
        "environment_installed":False,
        "environment_ready":False,
        "source_season_verified":False,
        "simc_source_verified":False,
        "G":None,"J":None,"F":None,"O":None,"B":None,"T":None,
        "requires":["CURRENT_EXPANSION_AND_SEASON_WCL_BLIZZARD_JOIN",
                    "DB2_CLASS_TIER_SEASON_MEMBERSHIP_PROOF",
                    "SOURCE_FIRST_GEAR_AND_CONSUMABLE_JOINS",
                    "SIMC_EXACT_SOURCE_MANIFEST",
                    "G_J_F_O_B_T_AND_POLICY_A",
                    "NEW_SEASON_V212_PROFILE_INSTALL"],
        "existing_session_or_cache_mutated":False,
    }


def build_environment(*, sessions_root, session_folder, user, binary, revision,
                      static_cache, source_catalog_path, bootstrap_result,
                      v208_start_receipt_path=None, package_manifest_path=None,
                      profile_stage_receipt=None, season_budget_evidence=None,
                      season_budget_source_paths=None,
                      expected_new_season_build=None,
                      fresh_source_stage_inputs=None):
    """Reconcile existing inputs and seal one incremental, auditable build.

    Source acquisition is intentionally outside this local coordinator:
    v191/v211/v213 are consumed from the exact installed package artifact.
    A new season/source refresh must first install a separately verified
    versioned source package. The coordinator never silently relabels stale
    source bytes as current.
    """
    # Existing v217 stages assemble the same v211/v213 source candidate
    # inside this original Build request. No session is created before the
    # ensuing preflight/required-budget barrier; never imply installation.
    if fresh_source_stage_inputs is not None:
        need(source_catalog_path is None and
             type(fresh_source_stage_inputs) is dict and
             set(fresh_source_stage_inputs) in (
                 frozenset(("stage_root", "v191_path",
                            "simc_source_dir", "simc_manifest_path")),
                 frozenset(("stage_root", "fresh_v191_inputs",
                            "simc_source_dir", "simc_manifest_path"))),
             "V216_FRESH_STAGE_INPUT_CONTRACT_INVALID")
        need(type(expected_new_season_build) is str,
             "V216_EXPLICIT_NEW_SEASON_BUILD_REQUIRED")
        prepared = fresh_stage.compile_fresh_candidate(
            **fresh_source_stage_inputs,
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
                preflight=preflight_new_season_source(
                    source_catalog_path=candidate_path,
                    expected_game_build=expected_new_season_build,
                    expected_simc_revision=revision)
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
