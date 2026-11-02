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
import v229_simc_only_source_seed as simc_source
import v232_simc_only_ordinary_representative as simc_representative
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
    # A source containing only trinkets/special-effect items is not a usable
    # ordinary gear/weapon pool. Preserve its sealed evidence as PENDING.
    return {"status":("FRESH_GEAR_PLAIN_CANDIDATES_SOURCE_ONLY" if plain
                      else "FRESH_GEAR_PLAIN_CANDIDATES_NOT_FOUND_PENDING"),
            "candidate_path":str((root/paths["candidate"]).resolve()),
            "item_count":result["item_count"],
            "plain_candidate_count":len(plain),
            "plain_armor_candidate_count":sum(x["class_id"]==4 for x in plain),
            "plain_weapon_candidate_count":sum(x["class_id"]==2 for x in plain),
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
         season_event in ("season_change","expansion_change","mid_patch"),
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





def _resolve_one_spec_simc_commit_stage(*, stage_root, build, gear, tier,
                                       revision_hint=None, transport=None):
    """One pinned SimC source commit, cached; not a binary or season proof."""
    waiting={"status":"SIMC_SOURCE_COMMIT_NOT_YET_RESOLVABLE_PENDING",
             "simc_revision":None,"network_calls_by_stage":0,
             "environment_ready":False,"binary_attested":False}
    if (revision_hint is None or not gear.get("candidate_path")
            or not tier.get("candidate_path")):
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
        req=Request(simc_source.RAW_BASE+revision+
                    "/engine/dbc/generated/"+item,
                    headers={"User-Agent":"SIMC-Secondary-source-cold-start/1.0"})
        with fetch(req,timeout=90) as response:
            need(response.status==200,
                 "V216_FULL_SIMC_ITEM_DATA_HTTP_NON_200")
            data=response.read(limit+1)
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
    Real Native/G and independently authenticated season membership remain
    prerequisites for any production profile or budget promotion.
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
    output="source/v255_one_spec_source_representative.json"
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
                and row.get("same_season_membership_not_proven") is True and
                row.get("native_physical_and_static_G_still_required") is True and
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
            root=root,stage_id="fresh-one-spec-source-representative",
            stage_version="v251-v232-exact-sources-one-spec-v1",
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
        return {"status":"FRESH_ONE_SPEC_PHYSICAL_SOURCE_OR_COVERAGE_PENDING",
                "reason":str(exc).split(":",1)[0],
                "network_calls_by_stage":0,"native_calls":0,
                "environment_ready":False}
    return {"status":"FRESH_ONE_SPEC_SIMC_G_SOURCE_CANDIDATE_PENDING_NATIVE",
            "candidate_path":str(path.resolve()),
            "source_stage":{k:v for k,v in staged.items() if k!="result"},
            "network_calls_by_stage":0,"native_calls":0,
            "season_membership_verified":False,"G":None,
            "environment_ready":False}


def collect_wago_new_season_source(*, sessions_root, expected_game_build,
                                   fetch=None, credentials=None,
                                   discovery_transport=None,
                                   tier_transport=None,
                                   bonus_transport=None,
                                   gear_transport=None,
                                   simc_seed_directory=None,
                                   simc_revision=None,
                                   previous_game_build=None,
                                   simc_season_event="season_change",
                                   simc_transport=None,
                                   representative_request=None,
                                   simc_revision_hint=None):
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
    pinned_simc=_collect_first_party_simc_seed_stage(
        stage_root=stage_root,build=expected_game_build,
        revision=(pinned_revision if previous_game_build is not None or
                  simc_season_event=="mid_patch" else None),
        previous_game_build=previous_game_build,
        season_event=simc_season_event,transport=simc_transport)
    effective_seed=simc_seed_directory or pinned_simc.get("source_dir")
    first_party=_verified_first_party_tier_options_stage(
        stage_root=stage_root,tier_bridge=tier_bridge,
        simc_seed_directory=effective_seed)
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
    one_spec=_one_spec_ordinary_simc_stage(
        stage_root=stage_root,build=expected_game_build,
        fresh_gear=fresh_gear,tier_bridge=tier_bridge,
        seed_directory=full_seed.get("source_dir") or effective_seed,
        request=representative_request)
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
        "fresh_tier":fresh_tier,
        "fresh_tier_raid_bonus_corroboration":tier_bonus,
        "fresh_tier_simc_candidate_bridge":tier_bridge,
        "fresh_tier_first_party_simc_options":first_party,
        "fresh_pinned_first_party_simc_source":pinned_simc,
        "fresh_pinned_simc_commit_resolution":resolved_simc,
        "fresh_lazy_full_pinned_simc_item_source":full_seed,
        "tier_discovery_mode":"DB2_FIRST_NO_PUBLISHER_NAME_LOOKUP",
        "network_calls_by_stage":(len(wago_snapshot.TABLES)
            if stage["executed"] else 0)+discovered["network_calls_by_stage"]+
            fresh_gear["network_calls_by_stage"]+
            fresh_tier["network_calls_by_stage"]+
            tier_bonus["network_calls_by_stage"]+
            pinned_simc["network_calls_by_stage"]+
            resolved_simc["network_calls_by_stage"]+
            full_seed["network_calls_by_stage"],
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
