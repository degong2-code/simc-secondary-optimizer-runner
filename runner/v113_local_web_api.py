#!/usr/bin/env python3
"""v113 P1-WEB-1: loopback-only HTTP adapter to EXISTING user/SimC worker.

Thin adapter; no optimizer, SimC mechanics, HTML app, or cloud execution.
The browser loads its per-process token from same-origin /api/v1/bootstrap.
Server listens on 127.0.0.1 only. File paths are never accepted as session IDs.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import secrets
import subprocess
import sys
import threading
import tempfile
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field

import v106_user_session_controller as sessions
import v098_target_user_scenario_bootstrap as bootstrap
import v108_native_consumable_inputs as consumables
import v188_user_choice_metadata as choice_labels
import v196_current_season_user_catalog as ui_catalog
import v529_current_season_eagle_E0_bridge as exact_e0_enchant
import v531_current_season_positive_E_bridge as exact_positive_enchant
import v193_simc_local_updater as simc_updates
import v660_simc_one_click_provision as simc_one_click
import v645_simc_connection_prefs as simc_connection
import v148_local_batch_results as batch_view
import v167_product_season_gear_adapter as season_gear
import v208_internal_exact_special_L_hydrator as exact_L
import v212_environment_manifest as environment_manifest
import v213_source_to_catalog as source_to_catalog
import v216_environment_build_coordinator as environment_build
import v286_representative_oil_source_binding as oil_preparation
import v289_retail_live_build_source as retail_build_source
import v522_myth_target_currency_source as myth_target_source
import v348_windows_user_source_credentials as local_source_keys
import v271_user_socket_gem_layout as physical_gems
import v218_v098_profile_stage_adapter as profile_stage
import v217_stage_execution_engine as stage_engine
import v293_local_longrun_session as longrun_sessions
import v335_environment_official_ko_localization as official_ko_env
import v336_environment_ko_playable_terms as official_playable_terms
import v665_official_item_icons as official_item_icons

SCHEMA = "v113_local_web_api_p1_v1"
KEY = re.compile(r"[a-f0-9]{20}\Z")
LOCAL_HOST = "127.0.0.1"
WEB_ASSETS = pathlib.Path(__file__).resolve().parent / "webui"
PUBLIC_STATIC = frozenset(("/", "/assets/app.js", "/assets/styles.css"))


def _static_cache_bytes_equal(stored, requested):
    """Preserve exact cache-alias identity with bounded read memory.

    v106 already hashes the selected cache in chunks for its session key;
    the existing sealed manifest path needs an independent byte comparison
    before it can be reused instead of rewriting an immutable session.
    """
    with pathlib.Path(stored).open("rb") as source, \
         pathlib.Path(requested).open("rb") as candidate:
        return (hashlib.file_digest(source,"sha256").digest()==
                hashlib.file_digest(candidate,"sha256").digest())

def _verified_snapshot_gem_layout_matches(result, *, special_gem_id,
                                          socket_total):
    """Reject a verified-budget cache hit for a different SimC gem profile."""
    compilation=(result.get("source_compilation")
                 if type(result) is dict else None)
    layout=(compilation.get("physical_gem_layout_unadmitted")
            if type(compilation) is dict else None)
    if (type(layout) is not dict or
            layout.get("schema")!="v271_user_socket_gem_layout_stage_v1"):
        return False
    ordinary=layout.get("ordinary_gem_ids")
    return (
        layout.get("status")==
            "PHYSICAL_GEMS_STAGED_SOURCE_AND_SOCKET_PROOFS_PENDING"
        and layout.get("special_gem_id")==special_gem_id
        and layout.get("socket_total")==socket_total
        and type(ordinary) is list and len(ordinary)>=4
        and len(set(ordinary[:4]))==4
        and len(ordinary)+int(special_gem_id is not None)==socket_total)



def _v670_sealed_fj_difference_proofs(doc, gem_layout):
    """Fingerprint allowlisted existing source evidence; no hashes leave this process.

    The caller separately verifies original v212/v113 and exact installed SHA.
    These comparisons confer no READY or session admission authority.
    """
    owners=doc.get("trusted_budget_component_source_identities")
    owners=owners if type(owners) is dict else {}
    stage_receipts=doc.get("original_v217_stage_receipts")
    stage_receipts=stage_receipts if type(stage_receipts) is dict else {}
    groups={
        "SIMC_REVISION":doc.get("simc_revision"),
        "G_REFERENCE":(
            doc.get("official_G_reference_track","general"),
            doc.get("official_G"),doc.get("official_effective_G"),
            doc.get("official_G_profile_receipt_sha256")),
        "B_T_ACCOUNTING":(
            doc.get("official_B"),doc.get("official_T"),
            doc.get("manual_final_T_authoritative")),
        "G_SOURCE":owners.get("G"),
        "J_SOURCE":owners.get("J"),
        "F_SOURCE":owners.get("F"),
        "O_SOURCE":owners.get("O"),
        "F_NATIVE_PROOF":doc.get("official_F_physical_source"),
        "O_FIXED_VECTOR":doc.get("official_O"),
        "SOURCE_CATALOG":(
            doc.get("source_catalog_manifest_sha256"),
            doc.get("source_catalog_artifact_sha256")),
        "SOURCE_STAGES":(
            doc.get("staged_source_environment_sha256"),
            doc.get("original_v216_preflight_sha256"),
            doc.get("original_v217_stage_receipts")),
        # v671: decompose the sole observed collision class without
        # comparing source values by eye or choosing a manifest by order.
        "STAGED_SOURCE_MANIFEST":doc.get("staged_source_environment_sha256"),
        "V216_PREFLIGHT_SEAL":doc.get("original_v216_preflight_sha256"),
        "V217_V191_RECEIPT":stage_receipts.get("v191_stage"),
        "V217_V211_RECEIPT":stage_receipts.get("v211_stage"),
        "V217_V213_RECEIPT":stage_receipts.get("v213_stage"),
        "V217_OTHER_RECEIPTS":{
            key:value for key,value in stage_receipts.items()
            if key not in ("v191_stage","v211_stage","v213_stage")},
        "TRUSTED_BUDGET_EVIDENCE":doc.get("trusted_budget_evidence_sha256"),
        "V222_BUDGET_OWNER":doc.get("v222_reconciled_budget"),
        "POLICY_A_OPTIONS":(
            doc.get("original_v196_prepared_options_sha256"),
            doc.get("published_verified_options"),
            doc.get("optional_quality_pending_item_ids"),
            doc.get("optional_other_proof_pending_by_id")),
        "DK_OPTIONAL_MODULE":doc.get("verified_DK_runeforges"),
        "GEM_LAYOUT_PROOF":gem_layout}
    return {name:hashlib.sha256(json.dumps(value,sort_keys=True,
        ensure_ascii=True,separators=(",",":")).encode("utf8")).hexdigest()
        for name,value in groups.items()}


def _v670_colliding_fj_diagnostics(proofs):
    """Describe differences without exposing installed SHA, paths or source data."""
    buckets={}
    for physical,proof in proofs:
        buckets.setdefault(physical,[]).append(proof)
    reports=[]
    for physical,entries in sorted(buckets.items()):
        if len(entries)<2:
            continue
        differences=sorted(name for name in entries[0]
                           if len({entry[name] for entry in entries})>1)
        if not differences:
            differences=["OTHER_SEALED_IDENTITY"]
        flask_id,quality,F,J,sockets,gem_ids=physical
        reports.append({
            "flask_item_id":flask_id,"flask_quality":quality,
            "F":F,"J":J,"socket_total":sockets,
            "ordinary_gem_item_ids":list(gem_ids),
            "installed_count":len(entries),
            "difference_codes":differences})
    return reports


def _v675_runtime_input_field_digests(snapshot_clean):
    """Hash *every* sealed runtime field under fixed, non-secret UI codes.

    The original v212/v113 stages have already been independently checked by
    the caller. No raw fields, paths or hash values are returned to the UI.
    An unknown/new field is included in OTHER_* so it remains fail-closed.
    """
    if type(snapshot_clean) is not dict:
        return None
    runtime=snapshot_clean.get("environment_result")
    if type(runtime) is not dict:
        return None
    compilation=runtime.get("source_compilation")
    if type(compilation) is not dict:
        return None
    keys={
        "snapshot":(
            ("SNAPSHOT_SCHEMA","schema"),
            ("SNAPSHOT_CATALOG","source_catalog_artifact_sha256")),
        "runtime":(
            ("RUNTIME_ENTRY","normal_build_entry"),
            ("RUNTIME_READY","zero_history_build"),
            ("RUNTIME_REPRESENTATIVE","fresh_one_spec_simc_representative"),
            ("RUNTIME_ORDINARY_GEAR","fresh_ordinary_gear"),
            ("RUNTIME_TIER_BRIDGE","fresh_tier_simc_candidate_bridge"),
            ("RUNTIME_PINNED_ITEM_SOURCE","fresh_lazy_full_pinned_simc_item_source"),
            ("RUNTIME_GAME_BUILD","expected_game_build"),
            ("RUNTIME_PERMANENT_ENCHANT","fresh_permanent_enchant_item_source"),
            ("RUNTIME_TARGET_ILEVEL","verified_target_ilevel"),
            ("RUNTIME_OIL_IDS","verified_oil_item_ids_by_hand")),
        "compilation":(
            ("COMPILATION_STATUS","status"),
            ("COMPILATION_SOURCE_CATALOG_PATH","source_catalog_path"),
            ("COMPILATION_STAGE_ROOT","stage_root"),
            ("COMPILATION_SIMC_REVISION","simc_revision"),
            ("COMPILATION_TIER_SOURCE_PATHS","v191_original_gear_tier_source_paths"),
            ("COMPILATION_V098_PROFILE","v098_source_only_profile_inputs_unadmitted"),
            ("COMPILATION_GEM_LAYOUT","physical_gem_layout_unadmitted"),
            ("COMPILATION_GEM_BUDGET","physical_gem_J_arithmetic_unadmitted"),
            ("COMPILATION_GEM_ITEM_RELATION","selected_v221_gem_item_relation_unadmitted"))
    }
    holders={"snapshot":snapshot_clean,"runtime":runtime,
             "compilation":compilation}
    result={}
    for group,owner in holders.items():
        fields=keys[group]
        for code,name in fields:
            # Missing differs from a present explicit null; missing is
            # never silently treated as zero or an approved default.
            present=name in owner
            comparison={"present":present,
                        "value":owner[name] if present else None}
            result[code]=stage_engine.digest(
                stage_engine.canonical(comparison).encode("utf8"))
        known={field for _,field in fields}
        if group=="snapshot":
            known.add("environment_result")
        elif group=="runtime":
            known.add("source_compilation")
        other={k:v for k,v in owner.items() if k not in known}
        result["OTHER_"+group.upper()+"_FIELDS"]=stage_engine.digest(
            stage_engine.canonical(other).encode("utf8"))
    return result


def _verified_saved_profile_snapshot(docs, installed, snapshot):
    """Read the exact v113 profile after original v212 install verification.

    Return the already authenticated bytes' decoded payload, not an
    equivalence digest. No new stage, cache, or live-season assertion.
    """
    try:
        digest=installed["manifest_sha256"]
        if (docs.is_symlink() or docs.parent.is_symlink() or
                not re.fullmatch(r"[a-f0-9]{64}",digest)):
            return None
        if (snapshot.is_symlink() or not snapshot.is_file() or
                snapshot.stat().st_size>8_000_000 or
                snapshot!=docs/("v113_profile_"+digest[:20]+".json")):
            return None
        raw=snapshot.read_bytes()
        snap=json.loads(raw.decode("utf8"))
        if (type(snap) is not dict or
                snap.get("schema")!=
                    "v113_verified_v212_profile_source_snapshot_v1" or
                snap.get("installed_manifest_sha256")!=digest or
                snap.get("source_catalog_artifact_sha256")!=
                    installed.get("source_catalog_artifact_sha256") or
                raw!=(stage_engine.canonical(snap)+"\n").encode("utf8")):
            return None
        stage_engine.verify_stage(
            root=docs.parent,
            stage_id="fresh-v113-profile-"+digest[:20],
            stage_version="v113-fresh-v212-profile-snapshot-1",
            inputs={"installed_manifest_sha256":digest,
                    "source_catalog_artifact_sha256":
                        installed["source_catalog_artifact_sha256"],
                    "snapshot_sha256":stage_engine.digest(raw)},
            outputs={"snapshot":"fresh_source/"+snapshot.name})
        runtime=snap.get("environment_result")
        compilation=runtime.get("source_compilation") if type(runtime) is dict else None
        linked=(compilation.get("verified_environment_install")
                if type(compilation) is dict else None)
        if (type(compilation) is not dict or type(linked) is not dict or
                compilation.get("preflight_sha256")!=
                    installed.get("original_v216_preflight_sha256") or
                linked.get("manifest_sha256")!=digest):
            return None
        return snap
    except (ValueError,TypeError,KeyError,UnicodeError,OSError,
            stage_engine.StageExecutionBlocked,
            environment_manifest.EnvironmentBlocked):
        return None


def _v672_verified_runtime_inputs_digest(docs, installed, snapshot, *,
                                        return_component_digests=False):
    """Prove saved runtime-input equivalence, NOT preflight or current Live.

    Called only after exact original v216/v212 installed receipt verification.
    Independently verify v212 staged and v113 profile stage receipts too.
    Removing only content-address linking fields cannot grant source approval.
    """
    try:
        if (type(installed) is not dict or
                docs.is_symlink() or not docs.is_dir() or
                docs.parent.is_symlink() or not docs.parent.is_dir()):
            return None
        digest=installed["manifest_sha256"]
        staged_sha=installed["staged_source_environment_sha256"]
        if not (re.fullmatch(r"[a-f0-9]{64}",digest) and
                re.fullmatch(r"[a-f0-9]{64}",staged_sha)):
            return None
        stage_path=docs/("v212_environment_"+staged_sha[:20]+".json")
        if (stage_path.is_symlink() or not stage_path.is_file() or
                stage_path.stat().st_size>environment_build.MAX_RECEIPT_BYTES):
            return None
        stage_doc,_=environment_manifest.read_json(
            stage_path,environment_build.MAX_RECEIPT_BYTES)
        environment_manifest.verify_fresh_source_environment(stage_doc)
        if (stage_doc.get("manifest_sha256")!=staged_sha or
                stage_doc.get("original_v216_preflight_sha256")!=
                    installed.get("original_v216_preflight_sha256") or
                stage_doc.get("original_v217_stage_receipts")!=
                    installed.get("original_v217_stage_receipts") or
                stage_doc.get("game_build")!=installed.get("game_build") or
                stage_doc.get("target_ilevel")!=installed.get("target_ilevel") or
                stage_doc.get("source_catalog_artifact_sha256")!=
                    installed.get("source_catalog_artifact_sha256")):
            return None
        stage_engine.verify_stage(
            root=docs.parent,
            stage_id="fresh-v212-environment-"+staged_sha[:20],
            stage_version="v212-fresh-source-environment-1",
            inputs={"manifest_sha256":staged_sha,
                    "v216_preflight_sha256":
                        stage_doc["original_v216_preflight_sha256"]},
            outputs={"environment":"fresh_source/"+stage_path.name})
        snap=_verified_saved_profile_snapshot(docs,installed,snapshot)
        if snap is None:
            return None
        runtime=snap["environment_result"]
        compilation=runtime["source_compilation"]
        # Compare all other sealed fields without reinterpreting values.
        # Only two preflight-derived *non-executable* status lists may
        # differ after two independent READY installations have each passed
        # original stage+profile verification. Keep all numeric, Policy A,
        # source owner, code and profile inputs in the comparison.
        # Unqualified v216 source stages remain NOT INSTALLED and cannot
        # authorize a selection on their own.
        stage_clean={k:v for k,v in stage_doc.items()
                     if k not in ("manifest_sha256",
                                  "original_v216_preflight_sha256",
                                  "pending_core_requirements",
                                  "optional_item_missing")}
        installed_clean={k:v for k,v in installed.items()
                         if k not in ("manifest_sha256",
                                      "staged_source_environment_sha256",
                                      "original_v216_preflight_sha256")}
        runtime_clean={k:v for k,v in runtime.items()
                       if k!="source_compilation"}
        runtime_clean["source_compilation"]={
            k:v for k,v in compilation.items()
            if k not in ("preflight_sha256","verified_environment_install")}
        snapshot_clean={k:v for k,v in snap.items()
                        if k not in ("installed_manifest_sha256",
                                     "environment_result")}
        snapshot_clean["environment_result"]=runtime_clean
        compared={"installed":installed_clean,"source_stage":stage_clean,
                  "runtime_snapshot":snapshot_clean}
        # Separate hashes remain internal; only fixed reason codes may be
        # exposed to the browser. Never leak receipt hashes/source values.
        if return_component_digests:
            hashes={key:stage_engine.digest(
                stage_engine.canonical(value).encode("utf8"))
                for key,value in compared.items()}
            hashes["runtime_fields"]=_v675_runtime_input_field_digests(
                snapshot_clean)
            if hashes["runtime_fields"] is None:
                return None
            return hashes
        return stage_engine.digest(stage_engine.canonical(compared).encode("utf8"))
    except (ValueError,TypeError,KeyError,UnicodeError,OSError,
            stage_engine.StageExecutionBlocked,
            environment_manifest.EnvironmentBlocked):
        return None



def _v677_verified_existing_budget(jobs, *, game_build, target_ilevel,
                                  installed_manifest_sha256,
                                  selected_flask_item_id,
                                  required_reference_G_track,
                                  failure_stage=None):
    """Read-only budget from ONE independently admitted v212/v113 install.

    No new season build, Wago fetch, SimC/native process, cache write,
    user-profile mutation, or cross-installation equality requirement.
    Return values are evidence for this exact *historical build*, never a
    claim of current KR Retail compatibility or DPS optimization success.
    """
    # Stages name the first failing existing check without disclosing source
    # paths or creating any new certification requirement.
    def check(name):
        if failure_stage is not None:
            failure_stage[:] = [name]

    check("SCOPE_INPUT")
    if (type(game_build) is not str or
            re.fullmatch(r"\d+(?:\.\d+){3}",game_build) is None or
            type(target_ilevel) is not int or not 1<=target_ilevel<=1000 or
            type(installed_manifest_sha256) is not str or
            re.fullmatch(r"[a-f0-9]{64}",installed_manifest_sha256) is None or
            type(selected_flask_item_id) is not int or
            not 1<=selected_flask_item_id<=999999999 or
            required_reference_G_track not in ("general","fury_dual_2h")):
        return None
    check("INSTALLED_SOURCE_DIRECTORY")
    docs=(jobs.root/"_fresh_season_sources"/
          ("wago_"+game_build)/"fresh_source")
    if (docs.is_symlink() or not docs.is_dir() or
            docs.parent.is_symlink()):
        return None
    with jobs.season_source_lock:
        check("INSTALLED_ENVIRONMENT")
        found=environment_build.find_verified_installed_season_environment(
            jobs.root,target_ilevel,expected_game_build=game_build,
            selected_oil_item_ids_by_hand={},
            expected_installed_manifest_sha256=installed_manifest_sha256,
            required_reference_G_track=required_reference_G_track)
        if (type(found) is not dict or
                found.get("installed_manifest_sha256")!=
                    installed_manifest_sha256 or
                found.get("environment_ready") is not True or
                found.get("environment_installed") is not True):
            return None
        check("INSTALL_OR_PROFILE_RECEIPT")
        path=docs/("v212_installed_"+
                   installed_manifest_sha256[:20]+".json")
        snapshot=docs/("v113_profile_"+
                       installed_manifest_sha256[:20]+".json")
        if (path.is_symlink() or not path.is_file() or
                path.stat().st_size>environment_build.MAX_RECEIPT_BYTES or
                snapshot.is_symlink() or not snapshot.is_file() or
                not 0<snapshot.stat().st_size<=8_000_000):
            return None
        check("INSTALL_MANIFEST_IDENTITY")
        doc,_=environment_manifest.read_json(
            path,environment_build.MAX_RECEIPT_BYTES)
        environment_manifest.verify_fresh_installed_environment(doc)
        if (doc.get("manifest_sha256")!=installed_manifest_sha256 or
                doc.get("game_build")!=game_build or
                doc.get("target_ilevel")!=target_ilevel or
                doc.get("official_G_reference_track","general")!=
                    required_reference_G_track):
            return None
        check("FLASK_OR_OIL_PHYSICAL_IDENTITY")
        physical=doc.get("official_F_physical_source")
        if (type(physical) is not dict or
                physical.get("physical_item_id")!=selected_flask_item_id or
                physical.get("F_rating")!=doc.get("official_F") or
                doc.get("official_O_physical_source") is not None or
                found.get("selected_oil_item_ids_by_hand")!={}):
            return None
        check("SAVED_PROFILE_INPUTS")
        if _v672_verified_runtime_inputs_digest(
                docs,doc,snapshot) is None:
            return None
        payload=json.loads(snapshot.read_bytes())
        original=payload.get("environment_result")
        check("FOUR_GEM_LAYOUT")
        if not _verified_snapshot_gem_layout_matches(
                original,special_gem_id=None,socket_total=4):
            return None
        # The original installed manifest verifies owner identities and
        # B/T; the matched v216 receipt is a separate original attestation.
        stats=environment_manifest.season_budget.STATS
        check("OIL_FIXED_BUDGET")
        oil=doc.get("official_O")
        if (type(oil) is not dict or set(oil)!=set(stats) or
                any(type(oil[x]) is not int or oil[x]!=0 for x in stats)):
            return None
        check("GJFO_TOTAL_CONSISTENCY")
        g,j,f,b,t=(doc.get("official_"+name)
                   for name in ("G","J","F","B","T"))
        if (any(type(x) is not int or x<0 for x in (g,j,f,b,t)) or
                b!=g+j+f or t!=b+sum(oil.values()) or
                any(found.get(name)!=value for name,value in
                    (("G",g),("J",j),("F",f),("B",b),("T",t))) or
                found.get("O")!=oil):
            return None
        if failure_stage is not None:
            failure_stage.clear()
        return {
            "schema":"v677_verified_existing_installed_budget_v1",
            "status":"VERIFIED_EXISTING_INSTALLED_BUDGET",
            "game_build":game_build,
            "target_ilevel":target_ilevel,
            "installed_manifest_sha256":installed_manifest_sha256,
            "selected_flask_item_id":selected_flask_item_id,
            "reference_G_track":required_reference_G_track,
            "G":g,"J":j,"F":f,"O":dict(oil),"B":b,"T":t,
            "verified_saved_v113_profile":True,
            "source_scope":"EXACT_V212_V113_INSTALLED_REUSE",
            "installed_optional_consumable_choices":
                _v680_public_installed_optional_choices(doc),
            "current_retail_build_verified":False,
            "native_calls_now":0,"network_calls_now":0,
            "dps_optimization_started":False
        }


class UpdateInstallRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    filename: str = Field(min_length=12,max_length=140)

class UpdateLocalArchiveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    archive_path: str = Field(min_length=8,max_length=4096)

class UpdateSelfBuiltZipRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    artifact_path: str = Field(min_length=8,max_length=4096)

class SimCConnectionConfirmRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    binary: str = Field(min_length=1,max_length=4096)
    revision: str = Field(pattern=r"^(?:[a-f0-9]{7,12}|[a-f0-9]{40})$")
    static_cache: str = Field(default="",max_length=4096)


class LocalSourceCredentialsRequest(BaseModel):
    """Never echoed, written into a session, or accepted as season evidence."""
    model_config = ConfigDict(extra="forbid")
    blizzard_client_id: str = Field(min_length=1,max_length=500)
    blizzard_client_secret: str = Field(min_length=1,max_length=500)
    wcl_client_id: str = Field(min_length=1,max_length=500)
    wcl_client_secret: str = Field(min_length=1,max_length=500)

class SeasonMythTargetRequest(BaseModel):
    """A source-only request, never a new DPS/gear optimizer."""
    model_config = ConfigDict(extra="forbid")
    game_build: str | None = Field(
        default=None,pattern=r"^\d+(?:\.\d+){3}$",
        min_length=7,max_length=32)


class SeasonEnvironmentBuildRequest(BaseModel):
    """Season-wide Build, independent of DPS scenario/trinket/target optimization."""
    model_config = ConfigDict(extra="forbid")
    # Blank/omitted means live Retail KR build discovery, not legacy defaults.
    game_build: str | None = Field(
        default=None,pattern=r"^\d+(?:\.\d+){3}$",
        min_length=7,max_length=32)
    target_ilevel: int = Field(default=334,ge=1,le=1000)
    reference_G_track: str = Field(
        default="general",pattern=r"^(?:general|fury_dual_2h)$")
    # Guard the live Retail build after the separate Myth source preflight:
    # a patch between two requests must never carry the old target forward.
    auto_myth_target_source_build: str | None = Field(
        default=None,pattern=r"^\d+(?:\.\d+){3}$",
        min_length=7,max_length=32)
    # Optional exact source pin ONLY for auto-selected Myth default ilvl.
    # Does not change the independent G/J/F/O or v212 approval contract.
    auto_myth_target_source_sha256: str | None = Field(
        default=None,pattern=r"^[a-f0-9]{64}$")
    # Explicit opt-in to the EXISTING single v277/v236 Native G probe.
    native_G_binary: str | None = Field(default=None,min_length=1,max_length=4096)
    # Same optional SimC executable may measure F/O with no G subprocess.
    consumable_native_binary: str | None = Field(default=None,min_length=1,max_length=4096)
    auto_native_F_requested: bool = False
    auto_native_O_requested: bool = False
    # The user's selected flask is an exact physical ID, NOT trusted F
    # evidence. A missing selection leaves the normal Build pending.
    selected_flask_item_id: int | None = Field(default=None,ge=1,le=999999999)
    # Exact physical item IDs by selected weapon hand, NEVER user O ratings.
    # Absent/empty retains the existing explicit no-oil behavior.
    selected_oil_item_ids_by_hand: dict[str,int] = Field(default_factory=dict)
    auto_select_observed_F_no_oil: bool = False
    # Existing v216 G/F measurement sources on first Build; off for legacy clients.
    auto_initial_core_build: bool = False
    auto_initial_core_simc_binary: str | None = Field(
        default=None,min_length=1,max_length=4096)
    # Optional existing selection; never identify or measure the special effect.
    existing_special_gem_id: int | None = Field(default=None,ge=1,le=999999999)
    # Declared final gem sockets; the v216 source must still validate gem IDs.
    source_target_socket_count: int | None = Field(default=None,ge=4,le=64)
    simc_revision_hint: str | None = Field(
        default=None,pattern=r"^(?:[a-f0-9]{7,12}|[a-f0-9]{40})$")
    refresh_reason: str | None = Field(
        default=None,pattern=r"^(?:season_change|expansion_change|item_content_change)$")


class LongRunBatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    continuous: bool = False
    max_new_native_this_invocation: int = Field(default=4,ge=0,le=32)
    max_elapsed_seconds: int = Field(default=900,ge=60,le=3600)


class LongRunStartRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    continuous: bool = False
    controls: dict
    binary: str = Field(min_length=1,max_length=4096)
    revision: str = Field(min_length=7,max_length=40)
    static_cache: str | None = Field(default=None,max_length=4096)
    current_season_product: bool = True
    # Exact IDs are optional; legacy hand-only sessions remain supported.
    selected_oil_item_ids_by_hand: dict[str,int] = Field(default_factory=dict)
    # Per-user final socket/consumable selections; never season DB identities.
    user_socket_total: int | None = Field(default=None,ge=4,le=64)
    user_special_gem_id: int | None = Field(default=None,ge=1,le=999999999)
    selected_flask_item_id: int | None = Field(default=None,ge=1,le=999999999)
    # Select an ALREADY INSTALLED/VERIFIED environment, not fresh collection.
    installed_season_game_build: str | None = Field(
        default=None,max_length=32,pattern=r"^\d+(?:\.\d+){3}$")
    # Exact v212 installation selected by the same UI gear/F/J/O source.
    installed_manifest_sha256: str | None = Field(
        default=None,pattern=r"^[a-f0-9]{64}$")
    max_native_calls: int = Field(default=12,ge=12,le=2000)
    max_new_native_this_invocation: int = Field(default=4,ge=1,le=32)
    max_elapsed_seconds: int = Field(default=900,ge=60,le=3600)


class LongRunImportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    archive_path: str = Field(min_length=1,max_length=4096)
    archive_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    max_elapsed_seconds: int = Field(default=900,ge=60,le=3600)


class UserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    controls: dict
    binary: str = Field(min_length=1, max_length=4096)
    revision: str = Field(min_length=7, max_length=40)
    static_cache: str | None = Field(default=None, max_length=4096)
    current_season_product: bool = False
    # Optional exact physical IDs, matched only against sealed v212 installs.
    selected_oil_item_ids_by_hand: dict[str,int] = Field(default_factory=dict)
    user_socket_total: int | None = Field(default=None,ge=4,le=64)
    user_special_gem_id: int | None = Field(default=None,ge=1,le=999999999)
    selected_flask_item_id: int | None = Field(default=None,ge=1,le=999999999)
    installed_season_game_build: str | None = Field(
        default=None,max_length=32,pattern=r"^\d+(?:\.\d+){3}$")
    # Exact v212 installation selected by the same UI gear/F/J/O source.
    installed_manifest_sha256: str | None = Field(
        default=None,pattern=r"^[a-f0-9]{64}$")
    # Opt-in normal-source collection only; never grants new environment READY.
    fresh_season_build: str | None = Field(
        default=None,max_length=32,pattern=r"^\d+(?:\.\d+){3}$")
    # Explicit user-scoped source-only Fury G observation. Never a GJFO
    # install, DPS admission or ordinary season Build default.
    measure_fury_G_source_only: bool = False

def _v680_exact_installed_optional_document(root,params,user):
    """One original installed v212, not a browser-supplied token list.

    This is a cheap lookup and same-scope read before possible Native work.
    v113 plan still resolves/validates the exact original v217 install later.
    Absent exact selection retains historical source_default-only behavior.
    """
    sha=params.installed_manifest_sha256
    build=params.installed_season_game_build
    if sha is None or build is None:
        return None
    level=user["target"]["ilevel"]
    path=(pathlib.Path(root)/"_fresh_season_sources"/("wago_"+build)/
          "fresh_source"/("v212_installed_"+sha[:20]+".json"))
    if path.is_symlink() or not path.is_file():
        raise environment_manifest.EnvironmentBlocked(
            "WEB_SELECTED_SEASON_OPTION_INSTALL_MISSING")
    doc,_=environment_manifest.read_json(path)
    environment_manifest.verify_fresh_installed_environment(doc)
    if (doc["manifest_sha256"]!=sha or doc["game_build"]!=build or
            doc["target_ilevel"]!=level):
        raise environment_manifest.EnvironmentBlocked(
            "WEB_SELECTED_SEASON_OPTION_INSTALL_CHANGED")
    return doc


def _v775_source_optional_defaults(doc,approved):
    """Preference over the verified installed menu, never new admission."""
    source=doc.get("installed_optional_consumables") or {}
    observation=source.get("native_default_observation")
    groups=(environment_build.optional_source_join.observed_default_groups(observation)
            if observation is not None else
            environment_build.optional_source_join.reviewed_apl_default_groups(
                doc.get("game_build"),doc.get("simc_revision")))
    defaults={}
    for kind,tokens in groups.items():
        for token,specs in tokens.items():
            if token not in approved[kind]:
                continue
            for spec in specs.split():
                defaults.setdefault(spec,{})[kind]=token
    return defaults


def _v680_public_installed_optional_choices(doc):
    """One verified v212 source projection used by UI and profile selection."""
    approved=profile_stage.current_season_approved_optional_choices(doc)
    source=doc.get("installed_optional_consumables")
    return {"schema":"v113_current_season_optional_consumables_v1",
            **approved,"source_default_simc_token":"disabled",
            "recommended_tokens_by_spec":_v775_source_optional_defaults(doc,approved),
            "diamond_id":[0],"omnium_talents":["source_default"],
            "installed_manifest_sha256":doc["manifest_sha256"],
            "items":([{"kind":name,**row}
                for name in ("food","potion","augmentation")
                for row in source["categories"][name]["options"]]
                if type(source) is dict else [])}


def _v680_preflight_optional_consumables(root,params,user):
    """Only an ACTUAL selected optional item needs the installed registry.

    Disabled/source_default is the old BASE path: no extra manifest read,
    no new validation and no extra I/O in a normal product session.
    """
    selected=user.get(bootstrap.CONSUME_FIELD) or {}
    needs_installed=any(selected.get(name) not in
                        (None,"source_default","disabled")
                        for name in ("food","potion","augmentation"))
    doc=(_v680_exact_installed_optional_document(root,params,user)
         if needs_installed else None)
    return profile_stage._verified_fresh_season_consumables(
        user,installed_environment=doc)


class InstalledFjSelectionRequired(environment_manifest.EnvironmentBlocked):
    """A verified live build may be known before a budget is selected."""
    def __init__(self, game_build, source_sha256, target_ilevel):
        super().__init__("V216_UNQUALIFIED_MULTIPLE_INSTALLED_FJ_VARIANTS_SELECT_EXACT_SHA")
        self.game_build=game_build
        self.source_sha256=source_sha256
        self.target_ilevel=target_ilevel


def blocked(exc, *, stage=None):
    """Return stable codes, not private absolute paths, talent strings, or tracebacks.

    A fixed stage is diagnostic only. It does not change admission, receipts,
    or reveal the actual exception message on a generic HTTP 409.
    """
    if isinstance(exc, InstalledFjSelectionRequired):
        # Only the already-discovered public build, never a source path,
        # session identity or permission to use an unselected environment.
        return HTTPException(422,detail={
            "code":str(exc),"stage":"SEASON_ENVIRONMENT_BUILD",
            "verified_retail_game_build":exc.game_build,
            "retail_build_source_sha256":exc.source_sha256,
            "target_ilevel":exc.target_ilevel,
            "environment_ready":False})
    if isinstance(exc, (longrun_sessions.LocalLongRunBlocked,
                         sessions.SessionBlocked, bootstrap.UserScenarioBlocked,
                        sessions.nonchmv_enchant.EnchantChoiceBlocked,
                        bootstrap.fresh_eagle.SourceBlocked,
                        bootstrap.positive_enchant.PositiveEnchantBlocked,
                        exact_L.StaticLBlocked,
                        environment_manifest.EnvironmentBlocked,
                        local_source_keys.CredentialBlocked)):
        code = str(exc).split(":", 1)[0].split("\n", 1)[0]
        return HTTPException(422, detail={"code": code})
    # Exact special L is a user-actionable, pre-Native input mismatch.
    # Only these fixed codes escape; arbitrary exception text can expose
    # private paths, options or SimC content and must remain generic.
    reference = bootstrap.oil_mod.reference_path
    if isinstance(exc, reference.ReferenceNativeBlocked):
        if str(exc) in ("SPECIAL_L_REQUIRES_EXACT_NATIVE_STATIC_VARIANT",
                        "REFERENCE_FIXED_L_CONSTRAINT_UNRESOLVED"):
            return HTTPException(422, detail={"code": str(exc)})
    if isinstance(exc, reference.statics.BudgetBlocked):
        if str(exc) == "SELECTED_SPECIAL_FLOOR_UNFEASIBLE":
            return HTTPException(422, detail={"code": str(exc)})
    detail={"code":"LOCAL_SESSION_PRECHECK_BLOCKED",
            "kind":type(exc).__name__}
    if stage in ("SEASON_ENVIRONMENT_BUILD",):
        detail["stage"]=stage
    return HTTPException(409, detail=detail)

class LocalJobs:
    def __init__(self, root, source_credential_store=None):
        self.root = pathlib.Path(root).expanduser().resolve()
        self.source_credential_store=(
            source_credential_store if source_credential_store is not None
            else local_source_keys.WindowsSourceCredentialStore())
        self.lock = threading.Lock()
        self.children = {}
        self.static_lock = threading.Lock()
        self.profile_stage_lock = threading.Lock()
        self.season_source_lock = threading.Lock()
        self.locale_cache_lock = threading.Lock()
        self.equipment_icon_lock = threading.Lock()
        self.equipment_icon_cache = {}
        self.season_gear_refresh_cache = {}
        self._verified_fresh_profile_result = None
        self._current_fresh_game_build = None

    def remember_verified_fresh_environment(self, result, *,
                                           required_reference_G_track=None):
        """Reuse only original v216/v212 installed READY, never user-supplied JSON."""
        compilation=(result.get("source_compilation")
                     if type(result) is dict else None)
        progress=(result.get("zero_history_build")
                  if type(result) is dict else None)
        installed=(compilation.get("verified_environment_install")
                   if type(compilation) is dict else None)
        if (result.get("normal_build_entry") is not True
            or type(progress) is not dict
            or progress.get("environment_ready") is not True
            or type(installed) is not dict
            or installed.get("environment_ready") is not True
            or type(installed.get("stage_output_path")) is not str):
            raise environment_manifest.EnvironmentBlocked(
                "WEB_FRESH_ORIGINAL_V216_INSTALLED_RESULT_REQUIRED")
        path=pathlib.Path(installed["stage_output_path"])
        if path.is_symlink() or not path.is_file():
            raise environment_manifest.EnvironmentBlocked(
                "WEB_FRESH_V212_INSTALLED_FILE_MISSING")
        doc,_=environment_manifest.read_json(path)
        environment_manifest.verify_fresh_installed_environment(doc)
        if (required_reference_G_track is not None and
                doc.get("official_G_reference_track","general")!=
                    required_reference_G_track):
            raise environment_manifest.EnvironmentBlocked(
                "WEB_FRESH_INSTALLED_G_REFERENCE_TRACK_CHANGED")
        physical_O=doc.get("official_O_physical_source")
        installed_oils=(physical_O.get("selected_oil_item_ids_by_hand")
                        if type(physical_O) is dict else {})
        verified=environment_build.find_verified_installed_season_environment(
            self.root,doc["target_ilevel"],
            expected_game_build=doc["game_build"],
            selected_oil_item_ids_by_hand=installed_oils,
            expected_installed_manifest_sha256=doc["manifest_sha256"])
        if (verified is None or
            verified["installed_manifest_sha256"]!=doc["manifest_sha256"] or
            installed.get("manifest_sha256")!=doc["manifest_sha256"]):
            raise environment_manifest.EnvironmentBlocked(
                "WEB_FRESH_V217_ORIGINAL_RECEIPT_MISMATCH")
        source=pathlib.Path(compilation["source_catalog_path"])
        if source.is_symlink() or not source.is_file():
            raise environment_manifest.EnvironmentBlocked(
                "WEB_FRESH_V213_CATALOG_MISSING")
        catalog,actual_sha=environment_manifest.read_json(source)
        if (actual_sha!=doc["source_catalog_artifact_sha256"] or
            catalog.get("manifest_sha256")!=
                doc["source_catalog_manifest_sha256"] or
            catalog.get("game_build")!=doc["game_build"]):
            raise environment_manifest.EnvironmentBlocked(
                "WEB_FRESH_V213_INSTALLED_CATALOG_DRIFT")
        names=("status","source_catalog_path","stage_root","simc_revision",
               "v191_original_gear_tier_source_paths",
               "v098_source_only_profile_inputs_unadmitted",
               "physical_gem_layout_unadmitted",
               "physical_gem_J_arithmetic_unadmitted",
               "selected_v221_gem_item_relation_unadmitted",
               "preflight_sha256","verified_environment_install")
        if any(k not in compilation for k in names):
            raise environment_manifest.EnvironmentBlocked(
                "WEB_FRESH_V098_ORIGINAL_PROFILE_INPUT_MISSING")
        self._verified_fresh_profile_result={
            "normal_build_entry":True,
            "zero_history_build":{"environment_ready":True},
            "source_compilation":{k:compilation[k] for k in names},
            "fresh_one_spec_simc_representative":
                result.get("fresh_one_spec_simc_representative"),
            # Reuse the ORIGINAL v216 pinned same-build source for
            # a different user's physical representative, never the old
            # measured representative's gear. Source-only v251/v232 can
            # generate a second spec in the same stage at ZERO new Native.
            "fresh_ordinary_gear":result.get("fresh_ordinary_gear"),
            "fresh_tier_simc_candidate_bridge":
                result.get("fresh_tier_simc_candidate_bridge"),
            "fresh_lazy_full_pinned_simc_item_source":
                result.get("fresh_lazy_full_pinned_simc_item_source"),
            # v589/v590 user-selected source checks require the exact
            # v217-sealed Wago stage locator plus SAME installed build.
            # The old v113 compact snapshot discarded both. Reuse only
            # the original tiny stage reference; do not copy optional DB
            # payload, fetch Wago, run Native, or change base G/J/F/O.
            "expected_game_build":doc["game_build"],
            "fresh_permanent_enchant_item_source":
                environment_build.original_optional_enchant_source_reference(
                    result),
            "verified_target_ilevel":doc["target_ilevel"],
            "verified_oil_item_ids_by_hand":dict(installed_oils)}
        return doc["manifest_sha256"]


    def _verified_profile_stage(self, document):
        """Fixed local v217 stage location, derived from v212 only, never HTTP."""
        build=document["game_build"]
        digest=document["manifest_sha256"]
        if (type(build) is not str or
            re.fullmatch(r"\d+(?:\.\d+){3}",build) is None or
            type(digest) is not str or
            re.fullmatch(r"[a-f0-9]{64}",digest) is None):
            raise environment_manifest.EnvironmentBlocked(
                "WEB_FRESH_V212_STAGE_IDENTITY_INVALID")
        root=self.root/"_fresh_season_sources"/("wago_"+build)
        key=digest[:20]
        return (root,"fresh-v113-profile-"+key,
                "fresh_source/v113_profile_"+key+".json")

    def persist_verified_fresh_profile(self):
        """One compact v217-sealed source-owner snapshot; NO Native/network."""
        result=self._verified_fresh_profile_result
        if type(result) is not dict:
            raise environment_manifest.EnvironmentBlocked(
                "WEB_FRESH_PROFILE_RESULT_NOT_VERIFIED")
        installed=result["source_compilation"]["verified_environment_install"]
        doc,_=environment_manifest.read_json(installed["stage_output_path"])
        environment_manifest.verify_fresh_installed_environment(doc)
        root,stage_id,out=self._verified_profile_stage(doc)
        expected=root/"fresh_source"/("v212_installed_"+
                                     doc["manifest_sha256"][:20]+".json")
        if (expected.resolve()!=pathlib.Path(
            installed["stage_output_path"]).resolve() or
            not root.is_dir() or root.is_symlink()):
            raise environment_manifest.EnvironmentBlocked(
                "WEB_FRESH_PROFILE_INSTALLED_LOCATION_CHANGED")
        payload={"schema":"v113_verified_v212_profile_source_snapshot_v1",
                 "installed_manifest_sha256":doc["manifest_sha256"],
                 "source_catalog_artifact_sha256":
                     doc["source_catalog_artifact_sha256"],
                 "environment_result":result}
        raw=(stage_engine.canonical(payload)+"\n").encode("utf8")
        if not 0<len(raw)<=8_000_000:
            raise environment_manifest.EnvironmentBlocked(
                "WEB_FRESH_PROFILE_SNAPSHOT_SIZE_INVALID")
        inputs={"installed_manifest_sha256":doc["manifest_sha256"],
                "source_catalog_artifact_sha256":
                    doc["source_catalog_artifact_sha256"],
                "snapshot_sha256":stage_engine.digest(raw)}
        def write():
            dest=root/out
            dest.parent.mkdir(parents=True,exist_ok=True)
            if dest.exists() or dest.is_symlink():
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_FRESH_PROFILE_SNAPSHOT_EXISTS_UNRECEIPTED")
            dest.write_bytes(raw)
        def validate(files):
            return files["snapshot"].read_bytes()==raw
        receipt=stage_engine.execute_stage(
            root=root,stage_id=stage_id,
            stage_version="v113-fresh-v212-profile-snapshot-1",
            inputs=inputs,outputs={"snapshot":out},
            execute=write,validate=validate)
        self._current_fresh_game_build=doc["game_build"]
        return {"status":receipt["status"],
                "installed_manifest_sha256":doc["manifest_sha256"],
                "new_native_calls":0}

    def restore_verified_fresh_profile(
            self, *, target_ilevel, game_build,
            selected_oil_item_ids_by_hand=None, required_gem_layout=None,
            expected_installed_manifest_sha256=None,
            required_reference_G_track="general"):
        """Recover only the exact selected installed environment, no Native."""
        found=environment_build.find_verified_installed_season_environment(
            self.root,target_ilevel,expected_game_build=game_build,
            selected_oil_item_ids_by_hand=selected_oil_item_ids_by_hand,
            expected_installed_manifest_sha256=expected_installed_manifest_sha256,
            **({"required_reference_G_track":required_reference_G_track}
               if required_reference_G_track is not None else {}))
        if found is None:
            return None
        digest=found["installed_manifest_sha256"]
        root=self.root/"_fresh_season_sources"/("wago_"+game_build)
        installed_path=(root/"fresh_source"/
                        ("v212_installed_"+digest[:20]+".json"))
        if installed_path.is_symlink() or not installed_path.is_file():
            raise environment_manifest.EnvironmentBlocked(
                "WEB_FRESH_PROFILE_INSTALLED_FILE_MISSING")
        doc,_=environment_manifest.read_json(installed_path)
        environment_manifest.verify_fresh_installed_environment(doc)
        if (doc["manifest_sha256"]!=digest or
            doc["target_ilevel"]!=target_ilevel or
            doc["game_build"]!=game_build):
            raise environment_manifest.EnvironmentBlocked(
                "WEB_FRESH_PROFILE_INSTALLED_DOCUMENT_DRIFT")
        root,stage_id,out=self._verified_profile_stage(doc)
        file=root/out
        if not file.exists():
            return None
        if (file.is_symlink() or not file.is_file() or
            file.stat().st_size>8_000_000):
            raise environment_manifest.EnvironmentBlocked(
                "WEB_FRESH_PROFILE_SNAPSHOT_FILE_INVALID")
        raw=file.read_bytes()
        try:
            payload=json.loads(raw)
        except (ValueError,UnicodeError) as exc:
            raise environment_manifest.EnvironmentBlocked(
                "WEB_FRESH_PROFILE_SNAPSHOT_JSON_INVALID") from exc
        if (type(payload) is not dict or
            payload.get("schema")!=
                "v113_verified_v212_profile_source_snapshot_v1" or
            payload.get("installed_manifest_sha256")!=digest or
            payload.get("source_catalog_artifact_sha256")!=
                doc["source_catalog_artifact_sha256"] or
            not raw.endswith(b"\n") or
            raw!=(stage_engine.canonical(payload)+"\n").encode("utf8")):
            raise environment_manifest.EnvironmentBlocked(
                "WEB_FRESH_PROFILE_SNAPSHOT_CONTENT_INVALID")
        stage_engine.verify_stage(
            root=root,stage_id=stage_id,
            stage_version="v113-fresh-v212-profile-snapshot-1",
            inputs={"installed_manifest_sha256":digest,
                    "source_catalog_artifact_sha256":
                        doc["source_catalog_artifact_sha256"],
                    "snapshot_sha256":stage_engine.digest(raw)},
            outputs={"snapshot":out})
        original=payload.get("environment_result")
        if type(original) is not dict:
            raise environment_manifest.EnvironmentBlocked(
                "WEB_FRESH_PROFILE_SNAPSHOT_RESULT_INVALID")
        if required_gem_layout is not None:
            if (type(required_gem_layout) is not dict or
                    set(required_gem_layout)!={"special_gem_id","socket_total"}):
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_FRESH_REQUIRED_GEM_LAYOUT_INVALID")
            if not _verified_snapshot_gem_layout_matches(
                    original,**required_gem_layout):
                # Reject mismatched legacy/special sockets without mutating
                # this process's verified user profile.
                return None
        self.remember_verified_fresh_environment(original)
        if self._verified_fresh_profile_result["verified_target_ilevel"]!=target_ilevel:
            raise environment_manifest.EnvironmentBlocked(
                "WEB_FRESH_PROFILE_TARGET_CHANGED")
        self._current_fresh_game_build=game_build
        return self._verified_fresh_profile_result

    def load_fresh_profile_for_user(
            self, target_ilevel, explicit_build=None,
            selected_oil_hands=None, selected_oil_item_ids_by_hand=None,
            required_gem_layout=None, selected_flask_item_id=None,
            expected_installed_manifest_sha256=None,
            required_reference_G_track="general"):
        """Find the exact verified oil variant, never a newest-file guess."""
        # No installed v113 snapshot means the original packaged/legacy
        # current-season route must remain unchanged. Do not fetch a retail
        # build or automatically collect/Native for each ordinary web plan.
        workspace=self.root/"_fresh_season_sources"
        if not workspace.is_dir() or workspace.is_symlink():
            return None
        if not any(p.is_file() and not p.is_symlink() for p in
                   workspace.glob("wago_*/fresh_source/v113_profile_*.json")):
            return None
        if (expected_installed_manifest_sha256 is not None and
                explicit_build is None):
            raise environment_manifest.EnvironmentBlocked(
                "WEB_INSTALLED_SHA_REQUIRES_EXACT_SEASON_BUILD")
        game_build=explicit_build or self._current_fresh_game_build
        if game_build is None:
            # One cheap current-build discovery per first restarted user plan.
            try:
                observed=retail_build_source.discover(region="KR")
            except retail_build_source.RetailVersionBlocked as exc:
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_FRESH_CURRENT_GAME_BUILD_UNAVAILABLE") from exc
            game_build=observed["game_build"]
            self._current_fresh_game_build=game_build
        selected_ids=None
        if selected_oil_item_ids_by_hand:
            # Prefer a user's exact physical item/hand identity. v216
            # authenticates the matching installed v212 source and SHA.
            if (selected_oil_hands is not None and
                    set(selected_oil_hands)!=set(selected_oil_item_ids_by_hand)):
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_FRESH_EXACT_OIL_HAND_ID_SELECTION_INVALID")
            # A physical hand-ID map does not identify a unique F/gem
            # installation. Defer the v216 verification to the per-receipt
            # SHA selection below; checking the first same-oil receipt here
            # caused redundant I/O and could choose the wrong F/J variant.
            selected_ids=dict(selected_oil_item_ids_by_hand)
        elif selected_oil_hands is not None:
            # Explicit no-oil does not need a prior hand-only search. That
            # search could pick a newer F/J installation before the exact
            # per-receipt variant check, doubling local SHA verification.
            if not selected_oil_hands:
                selected_ids={}
            else:
                # Without physical item IDs, identify only a unique hand map.
                selected=environment_build.find_verified_installed_season_environment(
                    self.root,target_ilevel,expected_game_build=game_build,
                    selected_oil_hands=selected_oil_hands,
                    **({"expected_installed_manifest_sha256":
                         expected_installed_manifest_sha256}
                       if expected_installed_manifest_sha256 is not None else {}))
                if selected is None:
                    raise environment_manifest.EnvironmentBlocked(
                        "WEB_FRESH_SELECTED_OIL_HANDS_NOT_INSTALLED")
                selected_ids=selected["selected_oil_item_ids_by_hand"]
        if (required_gem_layout is not None or
                selected_flask_item_id is not None or
                selected_oil_item_ids_by_hand is not None or
                selected_oil_hands is not None or
                expected_installed_manifest_sha256 is not None):
            # A hand-only (including O=0) API request cannot guess the
            # newest F/J receipt when multiple v212 variants are installed.
            # Require one authentic manifest SHA, just like explicit F/J/O.
            # A selected O hand-ID map still permits multiple verified
            # F/gem installations. Use the exact same one-receipt selection
            # as user F/socket variants; never choose the newest F/J budget.
            # Per-receipt v216 SHA verification is the existing admission.
            candidates=[]
            directory=workspace/("wago_"+game_build)/"fresh_source"
            if directory.is_dir() and not directory.is_symlink():
                # User-selected flask/gem variants are not limited to
                # the first 64 installation filenames.
                paths=((directory/("v212_installed_"+
                           expected_installed_manifest_sha256[:20]+".json"),)
                       if expected_installed_manifest_sha256 is not None
                       else directory.glob("v212_installed_*.json"))
                for path in paths:
                    if (path.is_symlink() or not path.is_file() or
                            path.stat().st_size>environment_build.MAX_RECEIPT_BYTES):
                        continue
                    try:
                        installed,_=environment_manifest.read_json(
                            path,environment_build.MAX_RECEIPT_BYTES)
                        environment_manifest.verify_fresh_installed_environment(
                            installed)
                        digest=installed["manifest_sha256"]
                        if (path.name!="v212_installed_"+digest[:20]+".json"
                                or (expected_installed_manifest_sha256 is not None
                                    and digest!=expected_installed_manifest_sha256)
                                or installed["game_build"]!=game_build or
                                installed["target_ilevel"]!=target_ilevel
                                or (required_reference_G_track is not None
                                    and installed.get(
                                        "official_G_reference_track","general")
                                        !=required_reference_G_track)):
                            continue
                        oils=installed.get("official_O_physical_source")
                        actual_oils=(oils.get("selected_oil_item_ids_by_hand")
                                     if type(oils) is dict else {})
                        if actual_oils!=(selected_ids or {}):
                            continue
                        if selected_flask_item_id is not None:
                            flask=installed.get("official_F_physical_source")
                            if (type(flask) is not dict or
                                    flask.get("physical_item_id")!=
                                        selected_flask_item_id):
                                continue
                        source=directory/("v113_profile_"+digest[:20]+".json")
                        if (source.is_symlink() or not source.is_file() or
                                not 0<source.stat().st_size<=8_000_000):
                            continue
                        snapshot=json.loads(source.read_text("utf8"))
                        original=snapshot.get("environment_result")
                        if (required_gem_layout is not None and
                                not _verified_snapshot_gem_layout_matches(
                                    original,**required_gem_layout)):
                            continue
                        verified=environment_build.find_verified_installed_season_environment(
                            self.root,target_ilevel,expected_game_build=game_build,
                            selected_oil_item_ids_by_hand=(selected_ids or {}),
                            expected_installed_manifest_sha256=digest)
                        if verified is not None:
                            candidates.append(digest)
                    except (OSError,ValueError,TypeError,KeyError,
                            environment_manifest.EnvironmentBlocked):
                        continue
            if not candidates and selected_oil_item_ids_by_hand and (
                    selected_flask_item_id is None and
                    required_gem_layout is None):
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_FRESH_SELECTED_OIL_ITEM_IDS_NOT_INSTALLED")
            if len(candidates)!=1:
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_USER_VARIANT_NOT_INSTALLED_OR_AMBIGUOUS")
            restored=self.restore_verified_fresh_profile(
                target_ilevel=target_ilevel,game_build=game_build,
                selected_oil_item_ids_by_hand=selected_ids,
                expected_installed_manifest_sha256=candidates[0],
                required_gem_layout=required_gem_layout,
                **({"required_reference_G_track":required_reference_G_track}
                   if required_reference_G_track!="general" else {}))
        else:
            restored=self.restore_verified_fresh_profile(
                target_ilevel=target_ilevel,game_build=game_build,
                selected_oil_item_ids_by_hand=selected_ids,
                **({"required_reference_G_track":required_reference_G_track}
                   if required_reference_G_track!="general" else {}))
        # When a fresh v113 snapshot exists, do not silently fall back to
        # an old packaged profile for a different current build or target.
        # The no-snapshot legacy path returned early above without network.
        if restored is None:
            raise environment_manifest.EnvironmentBlocked(
                "WEB_FRESH_TARGET_BUILD_NOT_INSTALLED_RUN_SEASON_BUILD")
        return restored

    def _fresh_environment_summary(self, folder, result):
        installed=result["source_compilation"]["verified_environment_install"]
        doc,_=environment_manifest.read_json(
            pathlib.Path(installed["stage_output_path"]))
        environment_manifest.verify_fresh_installed_environment(doc)
        manifest=json.loads((pathlib.Path(folder)/"generated"/"manifest.json")
                            .read_text(encoding="utf8"))
        seal=(manifest.get(bootstrap.entry.FRESH_SEASON_FIELD) or
              manifest.get(bootstrap.entry.SELECTED_FRESH_SEASON_FIELD))
        if (type(seal) is not dict or
            seal.get("installed_manifest_sha256")!=doc["manifest_sha256"] or
            seal.get("installed_environment_path")!=installed["stage_output_path"]):
            raise environment_manifest.EnvironmentBlocked(
                "WEB_FRESH_V096_INSTALLED_MANIFEST_MISMATCH")
        return {"schema":"v113_web_fresh_v212_installed_session_v1",
                "status":"FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY",
                "fresh_v212_installed_manifest_sha256":doc["manifest_sha256"],
                "game_build":doc["game_build"],
                "target_ilevel":doc["target_ilevel"],
                "native_calls":0,"network_calls":0}

    def default_static_cache(self, user, requested):
        """Reuse an existing same-PC static cache; never create L or call SimC.

        Optional user-specified paths retain prior behavior and identity.
        The stable app-local file is used only for selected specials; normal
        sessions and old sealed caches are unchanged.
        """
        if requested is not None or not user.get("special_items"):
            return requested
        candidate=exact_L.source_cache(self.root,None)
        return str(candidate) if candidate is not None else None

    def _with_verified_ko_localization(self, game_build, target_ilevel, outcome,
                                       *, verified_profile_compilation=None):
        # Distinct source families: exact physical item names (v335) and
        # English/Korean Blizzard playable terminology (v336). Both are
        # dependent read-only display metadata; neither changes item admission.
        terms=outcome.get("official_ko_terms")
        if type(terms) is not dict or terms.get("schema")!=official_playable_terms.SCHEMA:
            try:
                with self.locale_cache_lock:
                    terms=official_playable_terms.build_for_environment(
                        self.root,game_build)
            except Exception:
                terms={"schema":official_playable_terms.SCHEMA,
                       "status":"OFFICIAL_TERMS_SOURCE_REQUIRES_REVIEW",
                       "network_calls_now":0,"native_calls_now":0}
            outcome={**outcome,"official_ko_terms":terms}
        # Reuse v216's exact Environment Build result. The web adapter must
        # never re-fetch these names or create a parallel source of truth.
        already=outcome.get("official_ko_localization")
        if type(already) is dict and already.get("schema")==official_ko_env.SCHEMA:
            return outcome
        # Verified v212 installed-season reuse has no fresh v216 invocation.
        try:
            # Serializes same-process incremental label cache updates and
            # avoids duplicate official requests for concurrent Build calls.
            with self.locale_cache_lock:
                # Reused v212 numeric receipts omit physical gem layout.
                # Supply it only from the already restored, sealed v113
                # source-owner profile snapshot; never guess IDs from the
                # existing name cache or silently narrow the worklist.
                localization_source=outcome
                if verified_profile_compilation is not None:
                    localization_source={**outcome,
                        "source_compilation":verified_profile_compilation}
                localization=official_ko_env.build_for_environment(
                    self.root,game_build,localization_source,
                    target_ilevel=target_ilevel)
        except (official_ko_env.LocalizationBlocked,
                environment_manifest.EnvironmentBlocked,
                OSError,ValueError,TypeError,KeyError):
            localization={
                "schema":official_ko_env.SCHEMA,
                "game_build":game_build,
                "status":"OFFICIAL_KO_SOURCE_OR_CACHE_REQUIRES_REVIEW",
                "native_calls_now":0,"network_calls_now":0}
        return {**outcome,"official_ko_localization":localization}

    def discover_season_myth_target(self, game_build=None):
        """Source-only: existing v216/v163 active raid + ONE optional Wago CSV.

        The returned level is a candidate for the user's *default*, not an
        installed G/J/F/O/B/T environment. The normal Build must still verify.
        A missing source requires user ilvl input instead of an old 334 guess.
        """
        requested_build=game_build
        discovered=None
        if game_build is None:
            try:
                discovered=retail_build_source.discover(region="KR")
                game_build=discovered["game_build"]
            except retail_build_source.RetailVersionBlocked:
                return {
                    "schema":"v113_myth_default_source_discovery_v1",
                    "status":"MYTH_TARGET_SOURCE_PENDING",
                    "reason_code":"RETAIL_LIVE_GAME_BUILD_UNAVAILABLE",
                    "game_build":None,"target_ilevel":None,
                    "manual_target_ilevel_allowed":True,
                    "environment_ready":False,"native_calls":0}
        def pending(reason):
            return {
                "schema":"v113_myth_default_source_discovery_v1",
                "status":"MYTH_TARGET_SOURCE_PENDING",
                "reason_code":reason,"game_build":game_build,
                "retail_build_reverified":discovered is not None,
                "target_ilevel":None,"manual_target_ilevel_allowed":True,
                "environment_ready":False,"native_calls":0}
        try:
            credentials=self.source_credential_store.load()
        except (local_source_keys.CredentialBlocked,OSError):
            return pending("MYTH_TARGET_AUTHENTICATED_SOURCE_CREDENTIALS_UNAVAILABLE")
        # The v163 active raid comes from authenticated source discovery.
        # Do not collect ten large CSV files when that join cannot be run.
        if not credentials:
            return pending("MYTH_TARGET_ACTIVE_RAID_SOURCE_CREDENTIALS_MISSING")
        try:
            with self.season_source_lock:
                collected=environment_build.collect_wago_new_season_source(
                    sessions_root=self.root,expected_game_build=game_build,
                    credentials=credentials,representative_request=None,
                    g_probe_character=None,myth_target_source_only=True)
                joined=collected.get("season_join") or {}
                if (joined.get("status")!=
                    "DB2_WCL_CANDIDATES_JOINED_SEASON_CONDITIONS_PENDING"
                    or type(joined.get("source_scope")) is not dict
                    or not joined.get("candidate_path")):
                    return pending("MYTH_TARGET_V163_ACTIVE_RAID_JOIN_PENDING")
                # Original v217 Wago receipt/stage is reused. Do not append
                # CurrencyTypes to the ten immutable v161 mandatory tables.
                folder=pathlib.Path(collected["snapshot_receipt_path"]).parent
                expected=(self.root/"_fresh_season_sources"/
                          ("wago_"+game_build)/"wago").resolve()
                if folder.resolve()!=expected or folder.is_symlink():
                    return pending("MYTH_TARGET_ORIGINAL_WAGO_SCOPE_MISMATCH")
                source=myth_target_source.collect(folder,game_build)
                target=myth_target_source.myth_target_candidate(
                    folder,game_build,
                    active_season_scope=joined["source_scope"])
        except (environment_build.EnvironmentBuildBlocked,
                myth_target_source.TargetSourceBlocked,
                OSError,ValueError,KeyError,TypeError) as exc:
            code=str(exc).split(":",1)[0]
            return pending(code if re.fullmatch(r"[A-Z][A-Z0-9_]{0,100}",code)
                           else "MYTH_TARGET_SOURCE_COLLECTION_PENDING")
        return {
            **target,
            "schema":"v113_myth_default_source_discovery_v1",
            "status":(
                "MYTH_TARGET_CANDIDATE_FROM_MATCHED_WAGO_V163_SOURCE"
                if target.get("status")==
                    "MYTH_TRACK_TARGET_SOURCE_MATCH_UNADMITTED"
                else "MYTH_TARGET_SOURCE_PENDING"),
            "game_build":game_build,
            "retail_build_reverified":discovered is not None,
            "retail_build_source_sha256":(
                discovered["source_sha256"] if discovered else None),
            "optional_currency_network_calls_now":source["network_calls_now"],
            "manual_target_ilevel_allowed":True,
            "environment_ready":False,"native_calls":0}

    def build_season_environment(self, game_build=None, target_ilevel=334,
                                 native_G_binary=None, simc_revision_hint=None,
                                 auto_native_F_requested=False,
                                 auto_native_O_requested=False,
                                 consumable_native_binary=None,
                                 selected_flask_item_id=None,
                                 selected_oil_item_ids_by_hand=None,
                                 auto_select_observed_F_no_oil=False,
                                 auto_initial_core_build=False,
                                 auto_initial_core_simc_binary=None,
                                 existing_special_gem_id=None,
                                 source_target_socket_count=None,
                                 refresh_reason=None,
                                 auto_myth_target_source_build=None,
                                 auto_myth_target_source_sha256=None,
                                 reference_G_track="general"):
        """Run original v216 with season inputs, never a user DPS scenario.

        One deterministic one-spec reference G probe is NOT season-level
        validation, Fury-TG proof or a user character/profile input.
        """
        if reference_G_track not in ("general","fury_dual_2h"):
            raise environment_manifest.EnvironmentBlocked(
                "SEASON_G_REFERENCE_TRACK_INVALID")
        # One normal user Build: first try verified v212 reuse; only on a
        # cache miss invoke existing receipt-backed G/F stages. Explicit
        # advanced selections remain separate and require their own proof.
        if (type(auto_initial_core_build) is not bool or
                (not auto_initial_core_build and
                 auto_initial_core_simc_binary is not None) or
                (auto_initial_core_build and (
                    native_G_binary is not None or
                    consumable_native_binary is not None or
                    auto_native_F_requested or auto_native_O_requested or
                    auto_select_observed_F_no_oil or
                    selected_flask_item_id is not None or
                    bool(selected_oil_item_ids_by_hand)))):
            raise environment_manifest.EnvironmentBlocked(
                "SEASON_INITIAL_CORE_ADVANCED_SELECTION_CONFLICT")
        binary=None
        for label,requested in (
                ("SEASON_NATIVE_G_BINARY_INVALID",native_G_binary),
                ("SEASON_NATIVE_F_O_BINARY_INVALID",consumable_native_binary)):
            if requested is None:
                continue
            supplied=pathlib.Path(requested).expanduser()
            if supplied.is_symlink() or not supplied.is_file():
                raise environment_manifest.EnvironmentBlocked(label)
            resolved=supplied.resolve()
            if binary is not None and resolved!=binary:
                raise environment_manifest.EnvironmentBlocked(
                    "SEASON_NATIVE_G_F_O_BINARY_MISMATCH")
            binary=resolved
        # Source-bound oil selection, not a backdoor for CHMV numbers.
        # An absent oil map is an explicit NONE for a selected F, while a
        # positive map must be reconciled to physical v281/v286 originals.
        selected_oils=(
            {} if selected_oil_item_ids_by_hand is None
            else selected_oil_item_ids_by_hand)
        if (type(selected_oils) is not dict or len(selected_oils)>2
                or not set(selected_oils)<={"main_hand","off_hand"}
                or any(type(v) is not int or v<=0 or v>999999999
                       for v in selected_oils.values())
                or (selected_oils and selected_flask_item_id is None)):
            raise environment_manifest.EnvironmentBlocked(
                "SEASON_SELECTED_OIL_PHYSICAL_IDS_AND_FLASK_REQUIRED")
        if auto_select_observed_F_no_oil and (
                selected_flask_item_id is not None or selected_oils
                or not auto_native_F_requested or auto_native_O_requested):
            raise environment_manifest.EnvironmentBlocked(
                "SEASON_AUTO_F_REQUIRES_EXPLICIT_F_NATIVE_AND_NO_OIL")
        if consumable_native_binary is not None and not (
                auto_native_F_requested or auto_native_O_requested):
            raise environment_manifest.EnvironmentBlocked(
                "SEASON_F_O_BINARY_WITHOUT_MEASUREMENT_SELECTION")
        # Prefer verified original installation on an unchanged season.
        # Explicit selected items, Native requests and season/content changes
        # still use original fresh v216 validation; no automatic reapproval.
        if refresh_reason not in (None,"season_change","expansion_change",
                                  "item_content_change"):
            raise environment_manifest.EnvironmentBlocked(
                "SEASON_REFRESH_REASON_INVALID")
        if (source_target_socket_count is not None and
                (type(source_target_socket_count) is not int or
                 not (5 if existing_special_gem_id is not None else 4)
                     <=source_target_socket_count<=64)):
            raise environment_manifest.EnvironmentBlocked(
                "SEASON_DECLARED_SOCKET_COUNT_INVALID")
        # Resolve the requested build BEFORE any installed source reuse.
        # Without an explicit build, recheck Blizzard's inexpensive version
        # endpoint once. Never silently treat the newest installed *past*
        # build as the currently active Retail season after a patch.
        requested_game_build=game_build
        discovered_build=None
        if game_build is None:
            try:
                discovered_build=retail_build_source.discover(region="KR")
            except retail_build_source.RetailVersionBlocked as exc:
                raise environment_manifest.EnvironmentBlocked(str(exc)) from exc
            game_build=discovered_build["game_build"]
        version_network_calls=1 if discovered_build is not None else 0
        # Validation-only provenance guard; does not authorize G/J/F/O,
        # install a source or create a new cache key.
        if (auto_myth_target_source_build is not None and
                auto_myth_target_source_build!=game_build):
            raise environment_manifest.EnvironmentBlocked(
                "MYTH_TARGET_LIVE_GAME_BUILD_CHANGED_REDISCOVER")
        # The preflight's observed CSV SHA previously stopped at the browser.
        # Pin it to the unchanged same-build original BEFORE an installed
        # v212 cache hit or a new G/J/F/O source collection is considered.
        # A manual ilvl has no such source pin or new dependency.
        if auto_myth_target_source_sha256 is not None:
            if auto_myth_target_source_build is None:
                raise environment_manifest.EnvironmentBlocked(
                    "MYTH_TARGET_SOURCE_SHA_REQUIRES_VERIFIED_BUILD")
            candidate_folder=(self.root/"_fresh_season_sources"/
                              ("wago_"+game_build)/"wago")
            try:
                with self.season_source_lock:
                    source_doc=myth_target_source.verify(
                        candidate_folder,game_build)
            except (myth_target_source.TargetSourceBlocked,
                    OSError,ValueError,KeyError,TypeError) as exc:
                raise environment_manifest.EnvironmentBlocked(
                    "MYTH_TARGET_SOURCE_IDENTITY_CHANGED_REDISCOVER") from exc
            if source_doc["sha256"]!=auto_myth_target_source_sha256:
                raise environment_manifest.EnvironmentBlocked(
                    "MYTH_TARGET_SOURCE_IDENTITY_CHANGED_REDISCOVER")
        if (refresh_reason is None and native_G_binary is None and
            consumable_native_binary is None and
            not auto_native_F_requested and not auto_native_O_requested and
            selected_flask_item_id is None and not selected_oils and
            not auto_select_observed_F_no_oil and
            existing_special_gem_id is None):
            try:
                with self.season_source_lock:
                    prior=environment_build.find_verified_installed_season_environment(
                        self.root,target_ilevel,expected_game_build=game_build,
                        require_unique_unqualified=True,
                        required_reference_G_track=reference_G_track)
            except environment_build.EnvironmentBuildBlocked as exc:
                if (str(exc)=="V216_UNQUALIFIED_MULTIPLE_INSTALLED_FJ_VARIANTS_SELECT_EXACT_SHA"
                    and discovered_build is not None
                    and re.fullmatch(r"[a-f0-9]{64}",
                        discovered_build.get("source_sha256","")) is not None):
                    # The selection failure does not invalidate the
                    # independently authenticated live Retail build.
                    raise InstalledFjSelectionRequired(
                        game_build,discovered_build["source_sha256"],
                        target_ilevel) from exc
                raise
            if prior is not None:
                # A true original v212 receipt carries its installed SHA.
                # Previous API mocks/legacy reuse results retain old behavior.
                snapshot=(self.restore_verified_fresh_profile(
                    target_ilevel=target_ilevel,game_build=game_build,
                    **({"required_reference_G_track":reference_G_track}
                       if reference_G_track=="fury_dual_2h" else {}),
                    required_gem_layout={
                        "special_gem_id":None,
                        "socket_total":(
                            source_target_socket_count
                            if source_target_socket_count is not None else 4)})
                    if type(prior.get("installed_manifest_sha256")) is str
                    else None)
                # A sealed profile must match its gems. A verified v212
                # budget without a saved v113 profile is budget-READY only.
                # A user-requested automatic core Build must not get stuck
                # returning budget-only READY forever: continue into the
                # ORIGINAL v216 Build to recover the missing profile using
                # existing sealed sources/cache where possible.
                digest=prior.get("installed_manifest_sha256")
                has_profile=(type(digest) is str and
                    (self.root/"_fresh_season_sources"/("wago_"+game_build)/
                     "fresh_source"/("v113_profile_"+digest[:20]+".json")).exists())
                if snapshot is not None or (
                        not has_profile and not auto_initial_core_build):
                    return self._with_verified_ko_localization(
                        game_build,target_ilevel,{**prior,
                    "verified_v113_profile_source_restored":snapshot is not None,
                    "network_calls":version_network_calls,
                    "web_environment_scope":{
                    "schema":"v113_web_season_environment_build_scope_v1",
                    "game_build":game_build,
                    "game_build_source":"PREVIOUS_V217_VERIFIED_INSTALL",
                    "game_build_resolution":(
                        "BLIZZARD_PUBLIC_RETAIL_KR"
                        if discovered_build is not None
                        else "EXPLICIT_GAME_BUILD"),
                    "requested_game_build":requested_game_build,
                    "active_season_reverified_in_this_lookup":
                        discovered_build is not None,
                    "retail_build_source_sha256":(
                        discovered_build["source_sha256"]
                        if discovered_build is not None else None),
                    "retail_version_network_calls":version_network_calls,
                    "target_ilevel":target_ilevel,
                    "reference_G_track":reference_G_track,
                    "environment_ready":True,"environment_installed":True,
                    "native_calls":0,"network_calls":version_network_calls,
                    "dps_optimization_started":False,
                    "reused_verified_installed_season":True,
                    "auto_initial_core_build_requested":
                        auto_initial_core_build,
                    "auto_initial_core_native_skipped_existing_ready":
                        auto_initial_core_build,
                    "refresh_reason":None}},
                        verified_profile_compilation=(
                            snapshot.get("source_compilation")
                            if snapshot is not None else None))
        # Immutable by-build Wago stage cannot be silently replayed to
        # claim new item content at the exact same game build. The existing
        # targeted static correction path must handle a confirmed hotfix.
        # An explicit season/expansion event must never read a pre-event
        # same-build v217 Wago source receipt as though freshly observed.
        # The original stage identity is build-scoped, not season-event-
        # scoped. Preserve the immutable source/cache and fail closed until
        # an exact source correction/refresh identity is supplied.
        if refresh_reason is not None:
            prior=(self.root/"_fresh_season_sources"/("wago_"+game_build)/
                   ".stage_receipts"/"fresh-wago-db2.json")
            if prior.exists() or prior.is_symlink():
                if refresh_reason=="item_content_change":
                    raise environment_manifest.EnvironmentBlocked(
                        "SAME_BUILD_CONTENT_CHANGE_EXACT_SOURCE_CORRECTION_REQUIRED")
                raise environment_manifest.EnvironmentBlocked(
                    "SAME_BUILD_SEASON_EVENT_EXACT_SOURCE_REFRESH_REQUIRED")
        if auto_initial_core_build:
            # Resolve an executable only on a cache miss. A verified READY
            # install does not need its original SimC binary to be present.
            if auto_initial_core_simc_binary is None:
                raise environment_manifest.EnvironmentBlocked(
                    "SEASON_INITIAL_CORE_SIMC_BINARY_REQUIRED")
            supplied=pathlib.Path(auto_initial_core_simc_binary).expanduser()
            if supplied.is_symlink() or not supplied.is_file():
                raise environment_manifest.EnvironmentBlocked(
                    "SEASON_INITIAL_CORE_SIMC_BINARY_INVALID")
            binary=supplied.resolve()
            native_G_binary=binary
            consumable_native_binary=binary
            auto_native_F_requested=True
            auto_select_observed_F_no_oil=True
        with self.season_source_lock:
            # Only on a season cache miss, read the Windows user's
            # Credential Manager. No environment-variable mutation, process
            # spawning, receipt writing or API response contains these keys.
            # A missing local entry preserves the original optional v216
            # environment-variable path for developer CI and legacy uses.
            source_credentials=self.source_credential_store.load()
            # Internal packaged season source: no user numbers or new Native
            # probes. Missing exact-build data stays PENDING in original v216.
            nominal_source=(
                physical_gems.load_packaged_season_nominal_source(
                    game_build=game_build,need=environment_build.need))
            observed=environment_build.build_environment(
                sessions_root=self.root,session_folder=None,user=None,
                binary=binary,revision=None,static_cache=None,
                source_catalog_path=None,bootstrap_result=None,
                fresh_collection_inputs={
                    "expected_game_build":game_build,
                    "representative_request":{
                        "class":("warrior" if reference_G_track=="fury_dual_2h"
                                 else "paladin"),
                        "spec":("fury" if reference_G_track=="fury_dual_2h"
                                else "retribution"),
                        "target_ilevel":target_ilevel},
                    "g_probe_character":{"race":"dwarf"},
                    "simc_revision_hint":simc_revision_hint,
                    **({"credentials":source_credentials}
                       if source_credentials is not None else {}),
                    "auto_native_F_requested":auto_native_F_requested,
                    "auto_native_O_requested":auto_native_O_requested,
                    "auto_native_G_requested":native_G_binary is not None,
                    # Only this ordinary USER default mode may defer G
                    # Native if the original source compiler is incomplete.
                    # Advanced explicit G+F probes retain their authority.
                    **({"default_auto_core_build_requested":True}
                       if auto_initial_core_build else {}),
                    # Cold-start always collects the same-build ordinary
                    # four-stat source, even without an optional special
                    # gem ID. This does not place gems or approve J; the
                    # original v221/v266/v230/v232 owner retains that gate.
                    "auto_four_stat_source_requested":True,
                    # Explicit flask choice + no selected oil. Normal v216
                    # checks the same-build physical F and original Native
                    # receipts BEFORE any official v222 install. Do not
                    # pass an unverified F amount or a receipt from HTTP.
                    **({"selected_budget_items":{
                        "flask_item_id":selected_flask_item_id,
                        "oil_item_ids_by_hand":dict(selected_oils)}}
                       if selected_flask_item_id is not None else {}),
                    **({"auto_select_observed_F_no_oil":True}
                       if auto_select_observed_F_no_oil else {}),
                    # Default: four source-observed ordinary gems and no
                    # required special. A chosen existing special remains
                    # optional; all effects are delegated to SimC.
                    "source_selected_gem_roles":{
                        "special_gem_id":existing_special_gem_id,
                        "ordinary_gem_ids":None},
                    "source_target_socket_count":(
                        (5 if existing_special_gem_id is not None else 4)
                        if source_target_socket_count is None
                        else source_target_socket_count),
                    **({"source_ordinary_nominal_by_stat":nominal_source}
                       if nominal_source is not None else {})})
        if observed.get("environment_ready") is True:
            self.remember_verified_fresh_environment(
                observed,required_reference_G_track=reference_G_track)
            self.persist_verified_fresh_profile()
        return self._with_verified_ko_localization(
            game_build,target_ilevel,{**observed,"web_environment_scope":{
            "schema":"v113_web_season_environment_build_scope_v1",
            "game_build":game_build,"target_ilevel":target_ilevel,
            "game_build_source":(
                "BLIZZARD_PUBLIC_RETAIL_KR" if discovered_build is not None
                else "EXPLICIT_GAME_BUILD"),
            "retail_build_source_sha256":(
                discovered_build["source_sha256"]
                if discovered_build is not None else None),
            "retail_version_network_calls":version_network_calls,
            "active_season_reverified_in_this_lookup":
                discovered_build is not None,
            "internal_numeric_probe":(
                "warrior/fury" if reference_G_track=="fury_dual_2h"
                else "paladin/retribution"),
            "reference_G_track_requested":reference_G_track,
            "numeric_probe_not_whole_season_G_certification":True,
            "local_native_G_requested":native_G_binary is not None,
            "F_O_native_binary_configured":consumable_native_binary is not None,
            "auto_native_F_requested":auto_native_F_requested,
            "auto_native_O_requested":auto_native_O_requested,
            "selected_flask_item_id":selected_flask_item_id,
            "selected_oil_item_ids_by_hand":dict(selected_oils),
            "explicit_no_oil_with_selected_flask":
                selected_flask_item_id is not None and not selected_oils,
            "auto_select_observed_F_no_oil":
                auto_select_observed_F_no_oil,
            "auto_initial_core_build_requested":auto_initial_core_build,
            "auto_initial_core_native_requested_on_cache_miss":
                auto_initial_core_build,
            "four_stat_ordinary_default_requested":True,
            "four_stat_ordinary_source_requested":True,
            "ordinary_nominal_source_sha256":(
                nominal_source["source_sha256"]
                if nominal_source is not None else None),
            "ordinary_nominal_source_only_not_approved":
                nominal_source is not None,
            "source_target_socket_count":(
                (5 if existing_special_gem_id is not None else 4)
                if source_target_socket_count is None else
                source_target_socket_count),
            "declared_gem_profile_native_verified_here":False,
            "special_gem_effect_verified_here":False,
            "dps_optimization_started":False,
            "user_character_or_trinkets_required":False,
            "environment_installed":observed.get("environment_installed") is True,
            "environment_ready":observed.get("environment_ready") is True}})

    def collect_fresh_source(self, build, controls, revision_hint=None, *,
                             measure_fury_G_source_only=False, binary=None):
        # Reuse the product's existing user validator; never ask users for
        # internal source filenames, SHA, tier IDs or G seed vectors.
        # Prevalidate the requested DPS/ilvl BEFORE expensive HTTP.
        user=sessions.user_scenario(controls)
        character=user["character"]
        requested={"class":character["class"],"spec":character["spec"],
                   "target_ilevel":user["target"]["ilevel"]}
        if measure_fury_G_source_only:
            # One *explicit* existing v277/v236 measurement for the
            # different dual-twohand G track, never F/O or user DPS.
            # Its numerical receipt is not a v212 user budget/install.
            if ((character["class"],character["spec"])!=("warrior","fury")
                    or user["target"]["final_T"] is not None or
                    type(binary) is not str or not binary):
                raise environment_manifest.EnvironmentBlocked(
                    "FRESH_FURY_G_SOURCE_ONLY_EXACT_USER_BINARY_REQUIRED")
            source_binary=pathlib.Path(binary).expanduser()
            if source_binary.is_symlink() or not source_binary.is_file():
                raise environment_manifest.EnvironmentBlocked(
                    "FRESH_FURY_G_SOURCE_ONLY_SIMC_BINARY_INVALID")
            source_binary=source_binary.resolve()
            with self.season_source_lock:
                result=environment_build.build_environment(
                    sessions_root=self.root,session_folder=None,user=None,
                    binary=source_binary,revision=None,static_cache=None,
                    source_catalog_path=None,bootstrap_result=None,
                    fresh_collection_inputs={
                        "expected_game_build":build,
                        "representative_request":requested,
                        "g_probe_character":{"race":character["race"]},
                        "simc_revision_hint":revision_hint,
                        "auto_native_G_requested":True,
                        "auto_native_F_requested":False,
                        "auto_native_O_requested":False})
            if (result.get("environment_ready") is True or
                    result.get("environment_installed") is True):
                raise environment_manifest.EnvironmentBlocked(
                    "FRESH_FURY_G_PROBE_MUST_NOT_INSTALL_ENVIRONMENT")
            observed_G=result.get("native_G_numeric_source")
            return {**result,
                    "fury_G_source_only_requested":True,
                    "fury_G_numeric_observed_source_only":(
                        type(observed_G) is dict and
                        observed_G.get("status")==
                            "G_NATIVE_NUMERIC_REFERENCE_OBSERVED_JFO_PENDING"),
                    "fury_G_budget_admitted":False,
                    "fury_G_native_new_calls":result.get("native_calls",0),
                    "fury_G_user_dps_started":False}
        if binary is not None:
            raise environment_manifest.EnvironmentBlocked(
                "FRESH_SOURCE_NATIVE_NOT_EXPLICITLY_REQUESTED")
        # One request per exact build at a time. v217 reuses source bytes.
        # With no full pinned SimC item_data, one-spec stays PENDING/Native0.
        with self.season_source_lock:
            return environment_build.build_environment(
                sessions_root=self.root,session_folder=None,user=user,
                binary=None,revision=None,static_cache=None,
                source_catalog_path=None,bootstrap_result=None,
                fresh_collection_inputs={
                    "expected_game_build":build,
                    "representative_request":requested,
                    "g_probe_character":{
                        "race":character["race"],
                        "talents":character["talents"]},
                    "simc_revision_hint":revision_hint})

    def source_catalog_path(self):
        """Use the packaged v213 artifact when present; legacy source remains fallback."""
        candidate=pathlib.Path(__file__).resolve().parents[1]/"data"/"current_season_source_to_catalog.json"
        return candidate if candidate.is_file() else None


    def installed_oil_loadouts(self, ilevel, game_build=None):
        """List complete, sealed local oil combinations; no new approval/Native."""
        if type(ilevel) is not int or not 1<=ilevel<=1000 or (
            game_build is not None and
            re.fullmatch(r"\d+(?:\.\d+){3}",game_build) is None):
            raise environment_manifest.EnvironmentBlocked(
                "WEB_OIL_CHOICES_SCOPE_INVALID")
        base=self.root/"_fresh_season_sources"
        build=game_build or self._current_fresh_game_build
        if build is None and base.is_dir() and not base.is_symlink():
            # One stored build is NOT evidence that Retail is still on it.
            folders=[p.name[5:] for p in base.iterdir()
                     if p.is_dir() and not p.is_symlink() and
                     re.fullmatch(r"wago_\d+(?:\.\d+){3}",p.name)]
            if len(folders)==1:
                build=folders[0]
        result={"schema":"v113_verified_installed_oil_loadouts_v1",
                "status":"NO_VERIFIED_OIL_LOADOUTS",
                "game_build":build,"target_ilevel":ilevel,
                "items":[],"verified_flasks":[],
                "verified_base_flask_installs":[],
                "verified_gem_installs":[],
                "verified_base_fj_collision_diagnostics":[],
                "native_calls":0,"network_calls":0}
        if build is None:
            result["status"]="SELECT_LOCAL_INSTALLED_BUILD"
            return result
        stage_root=base/("wago_"+build)
        # Source preparation choices are NOT installed/runtime oil options.
        # Reuse the original candidate receipt once, independently of F/J/O.
        preparation=oil_preparation.preparation_options_from_sealed_stage(
            stage_root=stage_root,game_build=build)
        result["oil_preparation_source"]=preparation
        docs=stage_root/"fresh_source"
        if not docs.is_dir() or docs.is_symlink():
            return result
        candidates=[]
        # Browse every local install receipt: arbitrary first-64 truncation
        # hid valid F/O variants. Exact per-receipt SHA and v113 profile
        # verification below keep this read-only, without fresh Native/HTTP.
        for path in docs.glob("v212_installed_*.json"):
            if (path.is_symlink() or not path.is_file() or
                re.fullmatch(r"v212_installed_[a-f0-9]{20}\.json",path.name)
                    is None):continue
            try:candidates.append((path.stat().st_mtime,path))
            except OSError:continue
        seen=set()
        flasks_by_id={}
        conflicting_flasks=set()
        # Each receipt is admitted independently, never by comparison
        # against another installation with the same F/J.
        for _,path in sorted(candidates,key=lambda p:(-p[0],str(p[1]))):
            try:
                if path.stat().st_size>environment_build.MAX_RECEIPT_BYTES:
                    continue
                doc,_=environment_manifest.read_json(
                    path,environment_build.MAX_RECEIPT_BYTES)
                environment_manifest.verify_fresh_installed_environment(doc)
                positive=doc.get("official_O_physical_source")
                if (doc["game_build"]!=build or doc["target_ilevel"]!=ilevel
                    or path.name!="v212_installed_"+
                       doc["manifest_sha256"][:20]+".json"):
                    continue
                # O=0 installs are valid owners of a verified physical F.
                # Keep the same v212+v113 saved-profile admission as oils.
                ids=(positive["selected_oil_item_ids_by_hand"]
                     if type(positive) is dict else {})
                # Without a saved v113 profile the user's plan cannot resume.
                snapshot=docs/("v113_profile_"+
                               doc["manifest_sha256"][:20]+".json")
                if (snapshot.is_symlink() or not snapshot.is_file() or
                    not 0<snapshot.stat().st_size<=8_000_000):continue
                # Every v212 receipt may own a different F/gem/selected-O
                # variant even when hand IDs match. Verify THIS receipt's SHA,
                # not an arbitrary first same-oil installation.
                match=environment_build.find_verified_installed_season_environment(
                    self.root,ilevel,expected_game_build=build,
                    selected_oil_item_ids_by_hand=ids,
                    expected_installed_manifest_sha256=doc["manifest_sha256"])
                if (match is None or match["installed_manifest_sha256"]
                    !=doc["manifest_sha256"]):continue
                # v216 above already verifies the staged v212 source.
                # Authenticate this exact saved runtime profile once and
                # reuse it for ALL flask/oil/gem-layout projections.
                profile_doc=_verified_saved_profile_snapshot(docs,doc,snapshot)
                if profile_doc is None:
                    continue
                ordinary_4_gems=_verified_snapshot_gem_layout_matches(
                    profile_doc.get("environment_result"),
                    special_gem_id=None,socket_total=4)
                flask=doc.get("official_F_physical_source")
                # Project exact installed gem layouts from the SAME verified
                # snapshot. No raw source candidate becomes selectable here.
                runtime=profile_doc.get("environment_result")
                compilation=(runtime.get("source_compilation")
                             if type(runtime) is dict else None)
                layout=(compilation.get("physical_gem_layout_unadmitted")
                        if type(compilation) is dict else None)
                if type(layout) is dict and type(flask) is dict:
                    special=layout.get("special_gem_id")
                    sockets=layout.get("socket_total")
                    ordinary=layout.get("ordinary_gem_ids")
                    if ((special is None or
                         type(special) is int and special>0) and
                        type(sockets) is int and 4<=sockets<=64 and
                        type(ordinary) is list and
                        all(type(g) is int and g>0 and g!=special
                            for g in ordinary) and
                        _verified_snapshot_gem_layout_matches(
                            runtime,special_gem_id=special,
                            socket_total=sockets)):
                        result["verified_gem_installs"].append({
                            "installed_manifest_sha256":doc["manifest_sha256"],
                            "special_gem_id":special,
                            "socket_total":sockets,
                            "flask_item_id":flask["physical_item_id"],
                            "selected_oil_item_ids_by_hand":dict(ids),
                            "reference_G_track":doc.get(
                                "official_G_reference_track","general")})
                if type(flask) is dict and not ids and ordinary_4_gems:
                    layout=profile_doc["environment_result"][
                        "source_compilation"]["physical_gem_layout_unadmitted"]
                    gem_ids=layout["ordinary_gem_ids"][:4]
                    quality=flask.get("crafting_quality")
                    if (all(type(item_id) is int and item_id>0
                            for item_id in gem_ids) and
                            type(quality) is int and quality>=0):
                        result["verified_base_flask_installs"].append({
                            "installed_manifest_sha256":doc["manifest_sha256"],
                            "flask_item_id":flask["physical_item_id"],
                            "flask_quality":quality,
                            "ordinary_gem_item_ids":list(gem_ids),
                            "J":doc["official_J"],
                            "F":doc["official_F"],
                            "socket_total":4,
                            "reference_G_track":doc.get(
                                "official_G_reference_track","general"),
                            "simc_revision":doc["simc_revision"],
                            "individually_verified":True})
                if type(flask) is dict:
                    physical=flask["physical_item_id"]
                    if physical not in conflicting_flasks:
                        row={"physical_item_id":physical,
                             "simc_input_token":flask["simc_input_token"],
                             "crafting_quality":flask["crafting_quality"],
                             "F_rating":flask["F_rating"]}
                        prior=flasks_by_id.get(physical)
                        if prior is not None and prior!=row:
                            # One physical ID with inconsistent authenticated
                            # projections is not a user-selectable option.
                            flasks_by_id.pop(physical,None)
                            conflicting_flasks.add(physical)
                        else:
                            flasks_by_id[physical]=row
                if not ids:continue
                # Keep exact independently authenticated installations inside
                # one physical oil menu entry. A user-selected F/G scope can
                # resolve a unique variant without a fresh environment Build.
                variant={
                    "installed_manifest_sha256":doc["manifest_sha256"],
                    "ordinary_four_gem_profile":ordinary_4_gems,
                    "verified_flask_item_id":(
                        flask.get("physical_item_id")
                        if type(flask) is dict else None),
                    "reference_G_track":doc.get("official_G_reference_track",
                                                "general")}
                key=tuple(sorted(ids.items()))
                if key in seen:
                    # Same physical oil hands may have different sealed F/J
                    # budgets. Preserve the legacy one-row oil choice, but
                    # forbid an auto-bind to whichever receipt was newest.
                    for existing in result["items"]:
                        if tuple(sorted(existing[
                                "selected_oil_item_ids_by_hand"].items()))==key:
                            existing["verified_variant_count"]+=1
                            existing["verified_variants"].append(variant)
                            break
                    continue
                seen.add(key)
                description=[]
                for hand,row in sorted(positive["oil_by_hand"].items()):
                    token=row["simc_input_token"].rsplit(":",1)[-1]
                    description.append(
                        ("주무기" if hand=="main_hand" else "보조무기")+
                        " · "+token.replace("_"," ")+
                        " (#"+str(row["physical_item_id"])+")")
                result["items"].append({
                    "installed_manifest_sha256":doc["manifest_sha256"],
                    "selected_oil_item_ids_by_hand":dict(ids),
                    "display_name":" / ".join(description),
                    "verified_variant_count":1,
                    "verified_variants":[variant],
                    "ordinary_four_gem_profile":ordinary_4_gems,
                    "verified_flask_item_id":(
                        flask.get("physical_item_id")
                        if type(flask) is dict else None),
                    "game_build":build,"target_ilevel":ilevel})
            except (OSError,ValueError,TypeError,KeyError,
                    environment_manifest.EnvironmentBlocked):
                continue
        # One source-sealed cache read for all visible flask/oil IDs.
        # Missing official names retain the historical SimC-token labels.
        oil_ids={item_id for entry in result["items"]
                 for item_id in
                 entry["selected_oil_item_ids_by_hand"].values()}
        special_ids={entry["special_gem_id"]
                     for entry in result["verified_gem_installs"]
                     if entry["special_gem_id"] is not None}
        preparation_ids={row["physical_item_id"] for row in preparation["items"]}
        official_names=official_ko_env.read_names(
            self.root,build,set(flasks_by_id)|oil_ids|special_ids|preparation_ids)
        for row in preparation["items"]:
            if row["physical_item_id"] in official_names:
                row["official_name_ko"]=official_names[row["physical_item_id"]]
        for entry in result["verified_gem_installs"]:
            item_id=entry["special_gem_id"]
            if item_id in official_names:
                entry["official_name_ko"]=official_names[item_id]
        result["verified_gem_installs"].sort(
            key=lambda x:(x["special_gem_id"] or 0,x["socket_total"],
                          x["installed_manifest_sha256"]))
        # v676: multiple independently admitted installations are separate
        # exact-SHA choices, without cross-SHA equality requirements.
        # Session creation and cache/resume must reverify the selected SHA.
        result["verified_base_flask_installs"].sort(
            key=lambda x:(x["flask_item_id"],x["J"],
                          x["installed_manifest_sha256"]))
        result["verified_flasks"]=[
            {**flasks_by_id[k],
             **({"official_name_ko":official_names[k]}
                if k in official_names else {})}
            for k in sorted(flasks_by_id)]
        for entry in result["items"]:
            items=entry["selected_oil_item_ids_by_hand"]
            if items and all(item_id in official_names
                             for item_id in items.values()):
                entry["display_name"]=" / ".join(
                    ("주무기" if hand=="main_hand" else "보조무기")+
                    " · "+official_names[item_id]
                    for hand,item_id in sorted(items.items()))
        if result["items"]:
            result["status"]="VERIFIED_INSTALLED_OIL_LOADOUTS"
        return result

    def package_manifest_path(self):
        """Return the exact package-root manifest, never infer from a ZIP filename."""
        candidate=pathlib.Path(__file__).resolve().parents[1]/"V181_PACKAGE_MANIFEST.json"
        return candidate if candidate.is_file() and not candidate.is_symlink() else None

    @staticmethod
    def _write_atomic(path, encoded):
        path=pathlib.Path(path)
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.is_file() and path.read_text(encoding="utf8")==encoded:
            return path
        fd,temp=tempfile.mkstemp(prefix=".environment-manifest-",dir=path.parent)
        try:
            with os.fdopen(fd,"w",encoding="utf8") as stream:
                stream.write(encoded);stream.flush();os.fsync(stream.fileno())
            os.replace(temp,path)
        finally:
            if os.path.exists(temp):os.unlink(temp)
        return path

    @staticmethod
    def _environment_summary(document):
        payload={k:v for k,v in document.items() if k!="manifest_sha256"}
        digest=environment_manifest.sha(
            environment_manifest.canonical(payload).encode("utf8"))
        if digest!=document.get("manifest_sha256"):
            raise environment_manifest.EnvironmentBlocked(
                "ENVIRONMENT_MANIFEST_DIGEST_MISMATCH")
        source=document.get("source_catalog") or {}
        package=document.get("windows_package") or {}
        scope=document.get("product_scope") or {}
        receipt=document.get("v208_start_receipt") or {}
        return {
            "schema":document.get("schema"),
            "status":document.get("status"),
            "manifest_sha256":digest,
            "source_catalog_sha256":source.get("artifact_sha256"),
            "source_catalog_manifest_sha256":source.get("manifest_sha256"),
            "windows_package_status":package.get("status","NOT_PROVIDED"),
            "windows_package_manifest_sha256":package.get("manifest_sha256"),
            "all_specs_ready":scope.get("all_specs_ready"),
            "profile_supplier_coverage":scope.get("profile_supplier_coverage"),
            "dependency_change":document.get("dependency_change"),
            "v208_start_receipt_status":receipt.get("status"),
            "unresolved_dependencies":list(document.get(
                "unresolved_dependencies",[])),
            "native_calls":document.get("native_calls"),
            "network_calls":document.get("network_calls"),
        }

    def _read_environment_summary(self, folder):
        path=pathlib.Path(folder)/"generated"/"environment_manifest.json"
        if not path.is_file():
            # Fresh v212 admission lives in the original v096 manifest,
            # not in the legacy v216 environment_manifest.json.
            manifest=pathlib.Path(folder)/"generated"/"manifest.json"
            if not manifest.is_file():
                return None
            try:
                data=json.loads(manifest.read_text(encoding="utf8"))
                # v438: selected v436 manifests use the separate installed
                # field but MUST receive the same v212/v217 pre-start
                # verification as baseline fresh sessions. A missing summary
                # used to silently skip _verify_environment_dependencies.
                selected=data.get(
                    bootstrap.entry.SELECTED_FRESH_SEASON_FIELD)
                normal=data.get(bootstrap.entry.FRESH_SEASON_FIELD)
                if selected is not None and normal is not None:
                    raise environment_manifest.EnvironmentBlocked(
                        "WEB_FRESH_MULTIPLE_INSTALLED_SOURCE_FIELDS")
                fresh=selected if selected is not None else normal
                if fresh is None:
                    return None
                if type(fresh) is not dict:
                    raise environment_manifest.EnvironmentBlocked(
                        "WEB_FRESH_INSTALLED_SOURCE_MUST_BE_OBJECT")
                if selected is not None:
                    identity_path=pathlib.Path(folder)/"V106_SESSION_IDENTITY.json"
                    if identity_path.is_symlink() or not identity_path.is_file():
                        raise environment_manifest.EnvironmentBlocked(
                            "WEB_B8_SELECTED_V435_SESSION_IDENTITY_MISSING")
                    identity=json.loads(identity_path.read_text(encoding="utf8"))
                    selected_bound=identity.get("v435_selected_source_identity")
                    if (type(selected_bound) is not dict
                        or fresh.get("schema")!=
                           bootstrap.entry.SELECTED_FRESH_SEASON_SCHEMA
                        or fresh.get("selected_v435_identity_sha256")!=
                           sessions.sha(sessions.canonical(identity).encode(
                               "utf8"))
                        or sessions.sha(sessions.canonical(identity).encode(
                               "utf8"))[:20]!=pathlib.Path(folder).name):
                        raise environment_manifest.EnvironmentBlocked(
                            "WEB_B8_SELECTED_SOURCE_OR_SESSION_SHA_DRIFT")
                installed=pathlib.Path(fresh["installed_environment_path"])
                if installed.is_symlink() or not installed.is_file():
                    raise environment_manifest.EnvironmentBlocked(
                        "WEB_FRESH_V212_INSTALLED_FILE_MISSING")
                doc,_=environment_manifest.read_json(installed)
                environment_manifest.verify_fresh_installed_environment(doc)
                if doc["manifest_sha256"]!=fresh.get("installed_manifest_sha256"):
                    raise environment_manifest.EnvironmentBlocked(
                        "WEB_FRESH_V212_SEALED_MANIFEST_CHANGED")
                return {"schema":"v113_web_fresh_v212_installed_session_v1",
                        "status":doc["status"],"game_build":doc["game_build"],
                        "target_ilevel":doc["target_ilevel"],
                        "fresh_v212_installed_manifest_sha256":
                            doc["manifest_sha256"],
                        "native_calls":0,"network_calls":0}
            except (OSError,ValueError,TypeError,KeyError) as exc:
                # Do not erase selected B8 source/identity fail-closed
                # reasons while preserving old baseline error semantics.
                if (isinstance(exc,environment_manifest.EnvironmentBlocked)
                    and str(exc).startswith((
                        "WEB_B8_SELECTED_",
                        "WEB_FRESH_MULTIPLE_INSTALLED_SOURCE_FIELDS"))):
                    raise
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_FRESH_ENVIRONMENT_MANIFEST_INVALID") from exc
        try:
            document=json.loads(path.read_text(encoding="utf8"))
            if type(document) is not dict:
                raise ValueError("ENVIRONMENT_MANIFEST_OBJECT_REQUIRED")
            return self._environment_summary(document)
        except (OSError,ValueError,TypeError,KeyError) as exc:
            raise environment_manifest.EnvironmentBlocked(
                "ENVIRONMENT_MANIFEST_INVALID:"+type(exc).__name__) from exc

    def _verify_environment_dependencies(self, summary, folder=None):
        if not summary:
            return
        if summary.get("fresh_v212_installed_manifest_sha256") is not None:
            if folder is None:
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_FRESH_V212_SESSION_FOLDER_REQUIRED")
            # A session is bound to a specific v212 manifest, not merely
            # season+ilevel. Derive the oil selection from that sealed
            # manifest before looking up the corresponding cached variant.
            digest=summary["fresh_v212_installed_manifest_sha256"]
            if (type(digest) is not str or
                    re.fullmatch(r"[a-f0-9]{64}",digest) is None):
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_FRESH_SESSION_INSTALL_SHA_INVALID")
            root=self.root/"_fresh_season_sources"/(
                "wago_"+summary["game_build"])/"fresh_source"
            selected_file=root/("v212_installed_"+digest[:20]+".json")
            if selected_file.is_symlink() or not selected_file.is_file():
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_FRESH_SESSION_INSTALL_MISSING")
            selected_doc,_=environment_manifest.read_json(selected_file)
            environment_manifest.verify_fresh_installed_environment(
                selected_doc)
            if (selected_doc["manifest_sha256"]!=digest or
                selected_doc["game_build"]!=summary["game_build"] or
                selected_doc["target_ilevel"]!=summary["target_ilevel"]):
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_FRESH_SESSION_INSTALL_DOCUMENT_DRIFT")
            physical_O=selected_doc.get("official_O_physical_source")
            selected_oils=(physical_O.get("selected_oil_item_ids_by_hand")
                           if type(physical_O) is dict else {})
            # Session already carries its exact v212 installation SHA.
            # Selecting by oil alone can pick another valid F/gem variant,
            # blocking resume or reusing unrelated product conditions.
            verified=environment_build.find_verified_installed_season_environment(
                self.root,summary["target_ilevel"],
                expected_game_build=summary["game_build"],
                selected_oil_item_ids_by_hand=selected_oils,
                expected_installed_manifest_sha256=digest)
            if (verified is None or
                verified["installed_manifest_sha256"]!=
                    summary["fresh_v212_installed_manifest_sha256"]):
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_FRESH_V217_INSTALLED_RECEIPT_CHANGED")
            identity=json.loads((pathlib.Path(folder)/
                "V106_SESSION_IDENTITY.json").read_text(encoding="utf8"))
            if (identity.get("fresh_v212_installed_manifest_sha256")!=
                summary["fresh_v212_installed_manifest_sha256"]):
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_FRESH_SESSION_INSTALL_SHA_DRIFT")
            # Pre-spawn/resume: the exact installed v212 may be authentic
            # yet belong to a DIFFERENT representative G track. Reuse
            # existing sealed session user/manifest; no second source read,
            # Native, profile recomposition or new runtime approval gate.
            bound_user=identity.get("user")
            if type(bound_user) is dict:
                character=bound_user.get("character")
                target=bound_user.get("target")
                if type(character) is dict and type(target) is dict:
                    fury=(character.get("class"),character.get("spec"))==(
                        "warrior","fury")
                    track=selected_doc.get(
                        "official_G_reference_track","general")
                    if ((track=="fury_dual_2h" and not fury) or
                            (fury and target.get("final_T") is None
                             and track!="fury_dual_2h")):
                        raise environment_manifest.EnvironmentBlocked(
                            "WEB_FRESH_SESSION_G_REFERENCE_TRACK_MISMATCH")
            # Reuse the already authenticated source identity when a
            # saved user form is restored. No additional SimC or collection.
            return dict(selected_oils)
        source_path=self.source_catalog_path()
        if summary.get("source_catalog_sha256"):
            if source_path is None or folder is None:
                raise environment_manifest.EnvironmentBlocked(
                    "V213_PACKAGED_SOURCE_REMOVED_AFTER_PLAN")
            source_doc,source_sha=environment_manifest.read_json(source_path)
            if source_sha!=summary.get("source_catalog_sha256"):
                raise environment_manifest.EnvironmentBlocked(
                    "V213_SOURCE_CATALOG_CHANGED_AFTER_PLAN")
            try:
                session_identity=json.loads(
                    (pathlib.Path(folder)/"V106_SESSION_IDENTITY.json")
                    .read_text(encoding="utf8"))
            except (OSError,ValueError,TypeError) as exc:
                raise environment_manifest.EnvironmentBlocked(
                    "V213_SESSION_SOURCE_IDENTITY_MISSING") from exc
            bound=session_identity.get("current_season_source_catalog")
            if (type(bound) is not dict or
                bound.get("artifact_sha256")!=source_sha or
                bound.get("manifest_sha256")!=summary.get(
                    "source_catalog_manifest_sha256") or
                bound.get("game_build")!=source_doc.get("game_build") or
                bound.get("simc_revision")!=source_doc.get("simc_revision")):
                raise environment_manifest.EnvironmentBlocked(
                    "V213_SESSION_SOURCE_IDENTITY_MISMATCH")
            package_path=self.package_manifest_path()
            if summary.get("windows_package_status")=="VERIFIED":
                if package_path is None:
                    raise environment_manifest.EnvironmentBlocked(
                        "V213_PACKAGED_SOURCE_REMOVED_AFTER_PLAN")
                package_raw=package_path.read_bytes()
                if bound.get("package_manifest_sha256")!=sessions.sha(package_raw):
                    raise environment_manifest.EnvironmentBlocked(
                        "V181_SESSION_PACKAGE_IDENTITY_MISMATCH")
                package=environment_manifest.verify_windows_package_manifest(
                    package_path,source_path,source_doc,source_sha)
                if package.get("manifest_sha256")!=summary.get(
                        "windows_package_manifest_sha256"):
                    raise environment_manifest.EnvironmentBlocked(
                        "V181_PACKAGE_MANIFEST_CHANGED_AFTER_PLAN")

    def _latest_v208_receipt_path(self, folder):
        pointer=pathlib.Path(folder)/"V208_START_RECEIPT_REF.json"
        if not pointer.is_file():
            return None
        try:
            record=json.loads(pointer.read_text(encoding="utf8"))
            relative=record.get("path")
            if (record.get("schema")!="v113_v208_start_receipt_pointer_v1" or
                type(relative) is not str or not relative or
                pathlib.Path(relative).is_absolute() or
                ".." in pathlib.PurePosixPath(relative.replace("\\","/")).parts):
                raise ValueError("V208_RECEIPT_POINTER_INVALID")
            root=pathlib.Path(folder).resolve()
            target=(root/relative).resolve()
            if not target.is_relative_to(root) or not target.is_file():
                raise ValueError("V208_RECEIPT_POINTER_TARGET_INVALID")
            receipt=json.loads(target.read_text(encoding="utf8"))
            if receipt.get("receipt_sha256")!=record.get("receipt_sha256"):
                raise ValueError("V208_RECEIPT_POINTER_DIGEST_MISMATCH")
            return target
        except (OSError,ValueError,TypeError,KeyError) as exc:
            raise environment_manifest.EnvironmentBlocked(
                "V208_RECEIPT_POINTER_INVALID:"+type(exc).__name__) from exc

    def _record_v208_receipt(self, folder, receipt_info):
        relative=receipt_info.get("path")
        if type(relative) is not str or not relative:
            raise environment_manifest.EnvironmentBlocked(
                "V208_RECEIPT_RELATIVE_PATH_REQUIRED")
        pointer={
            "schema":"v113_v208_start_receipt_pointer_v1",
            "path":relative,
            "receipt_sha256":receipt_info.get("receipt_sha256"),
        }
        encoded=json.dumps(pointer,sort_keys=True,ensure_ascii=False,
                           indent=2,allow_nan=False)+"\n"
        self._write_atomic(pathlib.Path(folder)/"V208_START_RECEIPT_REF.json",encoded)

    def _seal_environment_manifest(self, folder, bootstrap_result,
                                   receipt_path=None, profile_stage_receipt=None):
        generated=pathlib.Path(folder)/"generated"
        bootstrap_path=generated/"v098_bootstrap_result.json"
        encoded_bootstrap=json.dumps(bootstrap_result,sort_keys=True,
            ensure_ascii=False,indent=2,allow_nan=False)+"\n"
        bootstrap.put_once(bootstrap_path,encoded_bootstrap)
        source_path=self.source_catalog_path()
        if source_path is None:
            return {"status":"SOURCE_CATALOG_NOT_PACKAGED",
                    "windows_package_status":"NOT_VERIFIED",
                    "all_specs_ready":bootstrap_result.get("all_specs_ready"),
                    "profile_supplier_coverage":bootstrap_result.get(
                        "profile_supplier_coverage"),
                    "v208_start_receipt_status":"NOT_VERIFIED",
                    "unresolved_dependencies":[
                        "V213_SOURCE_CATALOG_NOT_PACKAGED"],
                    "native_calls":0,"network_calls":0}
        if receipt_path is None:
            receipt_path=self._latest_v208_receipt_path(folder)
        try:
            user=json.loads((pathlib.Path(folder)/"user.json").read_text("utf8"))
            target_manifest=json.loads(
                (generated/"manifest.json").read_text("utf8"))
        except (OSError,ValueError,TypeError) as exc:
            raise environment_manifest.EnvironmentBlocked(
                "V216_BUILD_INPUT_IDENTITY_INVALID:"+type(exc).__name__) from exc
        built=environment_build.build_environment(
            sessions_root=self.root,session_folder=folder,user=user,
            binary=target_manifest.get("native_binary"),
            revision=target_manifest.get("native_revision"),
            static_cache=target_manifest.get("static_cache_json"),
            source_catalog_path=source_path,bootstrap_result=bootstrap_result,
            v208_start_receipt_path=receipt_path,
            package_manifest_path=self.package_manifest_path(),
            profile_stage_receipt=profile_stage_receipt)
        return self._environment_summary(built["manifest"])

    def _read_environment_build_summary(self, folder):
        path=pathlib.Path(folder)/"generated"/"environment_build_receipt.json"
        if not path.is_file():
            return None
        receipt=environment_build.read_receipt(path,folder.name)
        return environment_build.public_summary(receipt)

    def recent_sessions(self, limit=48):
        """Read-only local session index; no binary hashing, Native or writes.

        A session is listed only when its copied user bytes and sealed v106
        identity agree with its directory hash. No talents, paths, options
        or trinket IDs leave this endpoint; list is advisory, not authorization.
        Start/resume still performs complete current-binary/cache verification.
        """
        if not self.root.is_dir():
            return {"sessions":[],"read_only":True,"native_calls_now":0}
        candidates=[]
        for folder in self.root.iterdir():
            if (not KEY.fullmatch(folder.name) or folder.is_symlink()
                    or not folder.is_dir()):
                continue
            try:
                seal=folder/"V106_SESSION_IDENTITY.json"
                user_file=folder/"user.json"
                if not seal.is_file() or not user_file.is_file():
                    continue
                # An adversarial or corrupted local file must not force
                # unbounded parsing on a frequently visited UI screen.
                if seal.stat().st_size>524288 or user_file.stat().st_size>524288:
                    continue
                identity=json.loads(seal.read_text(encoding="utf8"))
                user=json.loads(user_file.read_text(encoding="utf8"))
                if (type(identity) is not dict or type(user) is not dict
                        or identity.get("schema")!=sessions.SCHEMA
                        or identity.get("user")!=user
                        or sessions.sha(sessions.canonical(identity).encode("utf8"))[:20]
                           !=folder.name):
                    continue
                character=user.get("character")
                target=user.get("target")
                if (type(character) is not dict or type(target) is not dict
                        or type(character.get("class")) is not str
                        or type(character.get("spec")) is not str
                        or (character["class"],character["spec"]) not in
                           sessions.SUPPORTED
                        or type(target.get("ilevel")) is not int
                        or type(identity.get("simc_revision")) is not str
                        or re.fullmatch(r"[0-9a-fA-F]{7,40}",
                                        identity["simc_revision"]) is None
                        or type(identity.get("independent_334",False)) is not bool):
                    continue
                state_file=folder/"V106_WORKER_STATE.json"
                result_file=folder/"V106_USER_RESULT.json"
                status="NOT_STARTED"
                if state_file.is_file():
                    if state_file.stat().st_size>16384:
                        continue
                    recorded=json.loads(state_file.read_text(encoding="utf8"))
                    if (type(recorded) is not dict or
                            recorded.get("schema")!=sessions.SCHEMA or
                            type(recorded.get("status")) is not str):
                        continue
                    status=recorded["status"]
                source=(state_file if state_file.is_file() else seal)
                result_saved=result_file.is_file()
                # Normal web Start uses v293/v291, not V106_USER_RESULT.
                # Use the existing sealed, zero-Native status reader; only a
                # fully exhausted run is a completed saved result. A paused
                # run may keep V291_RESULT.json observations for resume.
                if longrun_sessions.config_path(folder).is_file():
                    latest=longrun_sessions.read_status(folder,active=False)
                    worker=latest["progress"].get("worker",{})
                    if type(worker) is not dict:
                        continue
                    status=worker.get("status") or latest["progress"]["status"]
                    result_saved=(status=="BUDGET_EXHAUSTED" and
                                  latest["result_ready"] and
                                  latest["progress"]["completed_jobs"]==
                                  latest["progress"]["planned_jobs"])
                    longrun_state=longrun_sessions.worker_state_path(folder)
                    if (longrun_state.is_file() and
                            not longrun_state.is_symlink()):
                        source=longrun_state
                candidates.append((source.stat().st_mtime,{
                    "session_id":folder.name,
                    "class":character["class"],"spec":character["spec"],
                    "target_ilevel":target["ilevel"],
                    "recorded_status":status,
                    "result_saved":result_saved,
                    "independent_target334_profile":
                        identity.get("independent_334",False),
                    "updated_unix":int(source.stat().st_mtime)}))
            except (OSError,ValueError,TypeError,KeyError,OverflowError):
                # Corrupt single session is ignored; other sessions survive.
                continue
        candidates.sort(key=lambda item:(-item[0],item[1]["session_id"]))
        return {"sessions":[item for _,item in candidates[:limit]],
                "read_only":True,"native_calls_now":0}

    def folder(self, key):
        if not KEY.fullmatch(key):
            raise HTTPException(404, detail={"code":"SESSION_ID_INVALID"})
        # A key alone is not a user-supplied filesystem path.
        folder = (self.root / key).resolve()
        if not folder.is_relative_to(self.root) or not folder.is_dir():
            raise HTTPException(404, detail={"code":"SESSION_NOT_FOUND"})
        if not (folder / "V106_SESSION_IDENTITY.json").is_file():
            raise HTTPException(404, detail={"code":"SESSION_NOT_FOUND"})
        return folder

    def plan(self, params):
        try:
            user = sessions.user_scenario(params.controls)
            # Reuse the same current-season approval as /options BEFORE
            # creating sessions or resolving any exact-static-L Native.
            # A historical v108 SimC token is not a registered item.
            # Carry the ONE verified v212 optional-choice result into the
            # selected special/embellishment preview. Previously this result
            # was discarded and the preview revalidated without its registry,
            # rejecting an option already approved for this same installation.
            season_optional_controls=(
                _v680_preflight_optional_consumables(self.root,params,user)
                if params.current_season_product else None)
            exact_oils=params.selected_oil_item_ids_by_hand
            sockets=params.user_socket_total
            special=params.user_special_gem_id
            flask_id=params.selected_flask_item_id
            if ((special is not None and
                    (sockets is None or sockets<5)) or
                    (sockets is not None and not 4<=sockets<=64)):
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_USER_TOTAL_SOCKETS_INCLUDE_SPECIAL_INVALID")
            if (not params.current_season_product and
                    (sockets not in (None,4) or special is not None or
                     flask_id is not None)):
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_USER_VARIANT_VERIFIED_SEASON_ONLY")
            gem_choice=(None if sockets is None else
                        {"socket_total":sockets,"special_gem_id":special})
            if exact_oils and (
                not params.current_season_product or
                set(exact_oils)!=set(user["oil_hands"]) or
                len(exact_oils)>2 or
                any(type(value) is not int or value<=0
                    for value in exact_oils.values())):
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_FRESH_EXACT_OIL_HAND_ID_SELECTION_INVALID")
            # The executable SHA, not the path spelling, identifies a SimC run.
            binary=pathlib.Path(params.binary).expanduser().resolve()
            resolved_static=self.default_static_cache(user,params.static_cache)
            # 24 source-independent v147-proven representative archetypes:
            # user-selected target334 gets its own sealed product identity.
            # Legacy sessions and non-334 plans keep the original route.
            ch=user["character"]
            key=(ch["class"],ch["spec"])
            current_season=params.current_season_product
            pinned_build=params.installed_season_game_build
            if pinned_build is not None and not current_season:
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_INSTALLED_SEASON_SELECTION_REQUIRES_CURRENT_PRODUCT")
            if (params.installed_manifest_sha256 is not None and
                    (not current_season or pinned_build is None)):
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_INSTALLED_SHA_REQUIRES_EXACT_SEASON_BUILD")
            # A successful previous Build pins a v212 profile in process
            # memory, but does NOT reverify the active Retail version for a
            # later, unpinned plan. The modern UI always sends the exact
            # installed build after a successful verified Build. Do not run
            # an older in-memory G/J/F/O just because its ilvl, F, gems and
            # O happen to match. Existing source-free legacy plans remain.
            if (current_season and pinned_build is None and
                    (self._verified_fresh_profile_result is not None or
                     self._current_fresh_game_build is not None)):
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_FRESH_INSTALLED_GAME_BUILD_PIN_REQUIRED")
            independent=(not current_season and user["target"]["ilevel"]==334 and
                         key in bootstrap.ARCHETYPES)
            independent_level=(not current_season and user["target"]["ilevel"]!=334 and
                               key in sessions.SUPPORTED)
            fresh=self._verified_fresh_profile_result if current_season else None
            # The user-facing controls currently select O by hand, not by
            # arbitrary rating. Resolve that selection against exactly one
            # verified physical oil map before binding a v212 manifest.
            # On O=0, keep the prior in-memory fast path when it matches.
            # The in-memory source identity was verified and retained at
            # environment installation/restore; avoid per-plan disk reads.
            remembered_hands=(
                sorted(fresh.get("verified_oil_item_ids_by_hand",{}))
                if type(fresh) is dict else [])
            requested_G_track=(
                "fury_dual_2h" if key==("warrior","fury") and
                user["target"]["final_T"] is None else
                None if key==("warrior","fury") else "general")
            gem_matches=(gem_choice is None or
                         _verified_snapshot_gem_layout_matches(
                             fresh,**gem_choice))
            flask_matches=True
            # An explicitly pinned season always resolves its own exact
            # v212 SHA/F/J/O via load_fresh_profile_for_user below. Do not
            # first read an unrelated in-memory *previous* season's flask
            # receipt: that older file can be absent after a refresh and
            # must not block a valid new-season selection.
            if (fresh is not None and flask_id is not None and
                    pinned_build is None):
                # An unpinned legacy in-memory selection still checks F
                # before reusing that installed profile.
                original=fresh["source_compilation"][
                    "verified_environment_install"]["stage_output_path"]
                doc,_=environment_manifest.read_json(pathlib.Path(original))
                environment_manifest.verify_fresh_installed_environment(doc)
                selected_F=doc.get("official_F_physical_source")
                flask_matches=(type(selected_F) is dict and
                               selected_F.get("physical_item_id")==flask_id)
            variant_args={}
            if gem_choice is not None:
                variant_args["required_gem_layout"]=gem_choice
            if flask_id is not None:
                variant_args["selected_flask_item_id"]=flask_id
            if params.installed_manifest_sha256 is not None:
                variant_args["expected_installed_manifest_sha256"]=(
                    params.installed_manifest_sha256)
            if requested_G_track!="general":
                variant_args["required_reference_G_track"]=requested_G_track
            if current_season and (
                pinned_build is not None or
                fresh is None or
                user["target"]["ilevel"]!=fresh["verified_target_ilevel"] or
                sorted(user["oil_hands"])!=remembered_hands or
                bool(user["oil_hands"]) or
                not gem_matches or not flask_matches or
                (params.fresh_season_build is not None and
                 params.fresh_season_build!=
                     fresh["source_compilation"]["verified_environment_install"]
                         .get("installed_source_game_build",
                              self._current_fresh_game_build))):
                fresh=self.load_fresh_profile_for_user(
                    user["target"]["ilevel"],
                    pinned_build or params.fresh_season_build,
                    selected_oil_hands=user["oil_hands"],
                    selected_oil_item_ids_by_hand=exact_oils or None,
                    **variant_args)
            if current_season and fresh is None and (
                    special is not None or sockets not in (None,4) or
                    flask_id is not None):
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_USER_VARIANT_REQUIRES_VERIFIED_SEASON_INSTALL")
            if pinned_build is not None and fresh is None:
                # An explicit installed build never falls back to another
                # season or G track. Tell an automatic Fury user which
                # missing representative budget actually prevents planning.
                if requested_G_track=="fury_dual_2h":
                    raise environment_manifest.EnvironmentBlocked(
                        "WEB_FRESH_FURY_DISTINCT_G_AUTO_BUDGET_SOURCE_REQUIRED")
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_SELECTED_INSTALLED_SEASON_BUILD_NOT_FOUND")
            if exact_oils and fresh is None:
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_FRESH_SELECTED_OIL_ITEM_IDS_NOT_INSTALLED")
            if params.installed_manifest_sha256 is not None and (
                    fresh is None or fresh["source_compilation"][
                        "verified_environment_install"]["manifest_sha256"]!=
                        params.installed_manifest_sha256):
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_SELECTED_INSTALLED_SEASON_SHA_MISMATCH")
            if fresh is not None and (
                    (gem_choice is not None and
                     not _verified_snapshot_gem_layout_matches(
                         fresh,**gem_choice))):
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_USER_GEM_LAYOUT_NOT_VERIFIED")
            # A generic v212 G reference cannot be silently reused as
            # Fury Titan's Grip dual-2H automatic B/T. User manual final T
            # remains authoritative; avoid creating a wrong DPS session.
            if (fresh is not None and key==("warrior","fury") and
                    user["target"]["final_T"] is None):
                installed_path=pathlib.Path(
                    fresh["source_compilation"][
                        "verified_environment_install"]["stage_output_path"])
                installed_doc,_=environment_manifest.read_json(installed_path)
                if installed_doc.get("official_G_reference_track")!=(
                        "fury_dual_2h"):
                    raise environment_manifest.EnvironmentBlocked(
                        "WEB_FRESH_FURY_DISTINCT_G_AUTO_BUDGET_SOURCE_REQUIRED")
                environment_manifest.verify_fresh_installed_environment(
                    installed_doc)
            # A legacy/packaged product with no installed v113 snapshot
            # retains its historical v098 oil path. A *verified fresh*
            # snapshot already rejects missing or ambiguous physical O
            # above, so do not block unrelated legacy sessions here.
            source_catalog_path=(pathlib.Path(
                fresh["source_compilation"]["source_catalog_path"])
                if fresh is not None else self.source_catalog_path())
            package_manifest_path=(None if fresh is not None
                                   else self.package_manifest_path())
            selected_fresh=bool(fresh is not None and (
                user["special_items"] or user["embellishments"]))
            if selected_fresh:
                # A crafted-only user may reuse the existing same-season
                # v046 cache without invoking the special-only v208 probe.
                if resolved_static is None:
                    candidate=exact_L.source_cache(self.root,None)
                    resolved_static=(str(candidate) if candidate is not None
                                     else None)
                # Selected replacement of G/L must be calculated and
                # source-bound BEFORE any persistent folder is created.
                # No old unselected v106 key may hold a selected profile.
                if resolved_static is None:
                    raise environment_manifest.EnvironmentBlocked(
                        "WEB_SELECTED_B8_EXACT_STATIC_CACHE_REQUIRED")
                controls=season_optional_controls
                preview=bootstrap.preview_from_environment_build(
                    user,self.root/"_b8_unwritten_preview",
                    binary,params.revision,environment_result=fresh,
                    season_controls=controls,
                    selected_static_cache_path=resolved_static)
                if preview.get("status")!=(
                        "B8_SELECTED_V096_COMPLETE_PROFILE_BUDGET_NOT_ADMITTED"):
                    # Oil-off and selected physical variants are independent.
                    # Expose only source-approved bounded reason codes; never
                    # echo original profile, cache paths or exact user inputs.
                    observed=preview.get("status")
                    reason=(
                        "WEB_SELECTED_B8_EXACT_STATIC_VARIANTS_PENDING"
                        if observed=="B8_SELECTED_PROFILE_STATIC_VARIANTS_PENDING_NO_NATIVE"
                        else "WEB_SELECTED_B8_PROFILE_SOURCE_PENDING"
                        if observed=="V216_TO_V098_SOURCE_PROFILE_PENDING"
                        else "WEB_SELECTED_B8_PROFILE_OR_STATIC_VARIANTS_PENDING")
                    raise environment_manifest.EnvironmentBlocked(reason)
                selected_v435=preview.get(
                    "v435_future_v106_session_key_unadmitted")
                if type(selected_v435) is not dict:
                    raise environment_manifest.EnvironmentBlocked(
                        "WEB_SELECTED_B8_SEPARATE_SESSION_KEY_REQUIRED")
                folder=sessions.store_selected_fresh_session(
                    user,self.root,binary,params.revision,resolved_static,
                    selected_source=preview,
                    source_catalog_path=source_catalog_path,
                    installed_manifest_sha256=fresh[
                        "source_compilation"]["verified_environment_install"][
                            "manifest_sha256"])
                with self.profile_stage_lock:
                    bootstrap_result=(
                        bootstrap.materialize_selected_verified_environment(
                            user=user,folder=folder/"generated",
                            binary=binary,revision=params.revision,
                            environment_result=fresh,
                            selected_static_cache_path=resolved_static,
                            season_controls=controls,
                            preview_result=preview))
                profile_stage_receipt={
                    "schema":"v436_selected_v096_replay_stage_v1",
                    "status":"SELECTED_FRESH_SOURCE_REPLAY_VERIFIED_NO_NATIVE",
                    "stage_id":"v436_selected_fresh_v096",
                    "native_calls":0,"network_calls":0,
                    "session_key":folder.name}
            else:
                folder = sessions.store_session(user,self.root,binary,params.revision,
                                                resolved_static,
                                                independent_334=independent,
                                                independent_target_level=independent_level,
                                                current_season_product=current_season,
                                                source_catalog_path=(source_catalog_path
                                                    if current_season else None),
                                                package_manifest_path=(package_manifest_path
                                                    if current_season and source_catalog_path
                                                    else None),
                                                fresh_installed_manifest_sha256=(
                                                    fresh["source_compilation"][
                                                        "verified_environment_install"][
                                                            "manifest_sha256"]
                                                    if fresh is not None else None))
                # Session identity binds CACHE CONTENT, not its user-visible
                # path. If the same bytes are passed via a different path later,
                # honor the already-sealed manifest path rather than rewriting
                # immutable generated files or causing a needless new session.
                prior=folder/"generated"/"manifest.json"
                if resolved_static and prior.is_file():
                    previous=json.loads(prior.read_text(encoding="utf8"))
                    saved=previous.get("static_cache_json")
                    if (type(saved) is str and saved!=str(
                            pathlib.Path(resolved_static).resolve())):
                        old=pathlib.Path(saved)
                        if (old.is_file() and _static_cache_bytes_equal(
                                old, pathlib.Path(resolved_static))):
                            resolved_static=saved
                with self.profile_stage_lock:
                    bootstrap_result, profile_stage_receipt = profile_stage.build_or_reuse(
                        user=user,session_folder=folder,binary=binary,
                        revision=params.revision,static_cache=resolved_static,
                        independent_334=independent,
                        independent_target_level=independent_level,
                        current_season_product=current_season,
                        source_catalog_path=source_catalog_path,
                        verified_fresh_environment_result=fresh)
            plan=bootstrap_result["plan"]
            environment=(self._fresh_environment_summary(folder,fresh)
                         if fresh is not None else
                         self._seal_environment_manifest(
                             folder,bootstrap_result,
                             profile_stage_receipt=profile_stage_receipt)
                         if current_season else None)
            environment_build_receipt=(
                self._read_environment_build_summary(folder)
                if current_season else None)
            return {"session_id":folder.name,"status":"READY_ZERO_NATIVE",
                    "environment_manifest":environment,
                    "environment_build":environment_build_receipt,
                    "profile_stage":profile_stage_receipt,
                    "native_calls":0,
                    "static_cache_auto_used":bool(
                        resolved_static and params.static_cache is None),
                    "plan":{
                      "class":plan["class"],"spec":plan["spec"],
                      "base_B":plan["base_B"],
                      "fixed_O":plan["fixed_O"],"final_T":plan["final_T"],
                      "native_limit":plan["native_limit"],
                      "native_called":False,
                      "independent_target334_profile":independent,
                      "independent_non334_profile":independent_level,
                      "non334_physical_native_not_yet_observed":(
                          independent_level or
                          (current_season and user["target"]["ilevel"]!=334)),
                      "current_season_product":current_season,
                      # v176 is a historical BASE physical-acceptance
                      # receipt, not a certification of every DPS profile
                      # in a newly installed v212 season at the same ilvl.
                      "v176_26_of_26_base_physical_native":(
                          current_season and fresh is None and
                          user["target"]["ilevel"]==334)}}
        except Exception as exc:
            raise blocked(exc) from None

    def _catalog_for_selected_special_L(self, user, params, *, with_environment=False):
        """Reuse the same installed v212 catalog as normal user planning.

        This executes only for an explicitly selected special item. An
        uninstalled/legacy session retains its packaged catalog path; an
        explicitly pinned installed build never falls back to that package.
        No SimC/Native or independent authentication is added here.
        """
        gems=(None if params.user_socket_total is None else {
            "socket_total":params.user_socket_total,
            "special_gem_id":params.user_special_gem_id})
        if (params.user_special_gem_id is not None and
                (params.user_socket_total is None or
                 params.user_socket_total<5)):
            raise environment_manifest.EnvironmentBlocked(
                "WEB_USER_TOTAL_SOCKETS_INCLUDE_SPECIAL_INVALID")
        verified=self.load_fresh_profile_for_user(
            user["target"]["ilevel"],
            params.installed_season_game_build or params.fresh_season_build,
            selected_oil_hands=user["oil_hands"],
            selected_oil_item_ids_by_hand=(
                params.selected_oil_item_ids_by_hand or None),
            required_gem_layout=gems,
            selected_flask_item_id=params.selected_flask_item_id,
            **({"required_reference_G_track":
                 ("fury_dual_2h" if user["target"]["final_T"] is None else None)}
               if (user["character"]["class"],user["character"]["spec"])==
                  ("warrior","fury") else {}),
            **({"expected_installed_manifest_sha256":
                 params.installed_manifest_sha256}
               if params.installed_manifest_sha256 is not None else {}))
        if verified is not None and params.installed_manifest_sha256 is not None:
            if verified["source_compilation"][
                    "verified_environment_install"]["manifest_sha256"]!=(
                    params.installed_manifest_sha256):
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_SELECTED_INSTALLED_SEASON_SHA_MISMATCH")
        if verified is None:
            if params.installed_season_game_build is not None:
                raise environment_manifest.EnvironmentBlocked(
                    "WEB_SELECTED_INSTALLED_SEASON_BUILD_NOT_FOUND")
            path=self.source_catalog_path()
        else:
            path=pathlib.Path(verified["source_compilation"]["source_catalog_path"])
        return (path,verified) if with_environment else path

    def prepare_with_internal_special_L(self, params):
        """Share the existing exact static-L hydration for both explicit starts.

        Never measure special item effects; SimC owns those. Only static L is
        recorded by the pre-existing exact Native cache/receipt path.
        """
        season_controls=None
        try:
            user=sessions.user_scenario(params.controls)
            if params.current_season_product:
                # Same exact v212 optional choices as the later profile,
                # before possible special-L Native work, not an old v108 list.
                season_controls=_v680_preflight_optional_consumables(
                    self.root,params,user)
        except Exception as exc:
            raise blocked(exc) from None
        hydrated=None
        prepared_params=params
        if params.current_season_product and (
                user["special_items"] or
                (user["embellishments"] and
                 params.installed_season_game_build is not None)):
            # v475 must apply BEFORE optional exact-L Native/cache hydration,
            # not only in the later plan() call. On a restarted server the
            # saved v113 snapshot is also evidence that a stale installed
            # season could be selected by an unpinned special-gear request.
            # Legacy packaged special-L starts without a saved fresh v113
            # snapshot retain their original path.
            if params.installed_season_game_build is None:
                workspace=self.root/"_fresh_season_sources"
                saved_fresh=(workspace.is_dir() and not workspace.is_symlink()
                    and any(p.is_file() and not p.is_symlink() for p in
                            workspace.glob(
                                "wago_*/fresh_source/v113_profile_*.json")))
                if (self._verified_fresh_profile_result is not None or
                        self._current_fresh_game_build is not None or
                        saved_fresh):
                    raise blocked(environment_manifest.EnvironmentBlocked(
                        "WEB_FRESH_INSTALLED_GAME_BUILD_PIN_REQUIRED"))
            binary=pathlib.Path(params.binary).expanduser().resolve()
            with self.static_lock:
                source=self.default_static_cache(user,params.static_cache)
                if source is None and not user["special_items"]:
                    candidate=exact_L.source_cache(self.root,None)
                    source=str(candidate) if candidate is not None else None
                try:
                    selected_catalog,verified=self._catalog_for_selected_special_L(
                        user,params,with_environment=True)
                    hydrated=exact_L.hydrate(
                        user,self.root,binary,params.revision,
                        existing=source,
                        source_catalog_path=selected_catalog,
                        **({"environment_result":verified,
                            "season_controls":season_controls}
                           if verified is not None else {}))
                except Exception as exc:
                    raise blocked(exc) from None
                prepared_params=params.model_copy(update={
                    "static_cache":hydrated["static_cache_path"]})
        prepared=self.plan(prepared_params)
        folder=self.folder(prepared["session_id"])
        if hydrated:
            receipt_info=exact_L.write_start_receipt(
                folder,hydrated["start_receipt"])
            self._record_v208_receipt(folder,receipt_info)
            # Fresh v212 session is already source-bound by v098/v096.
            # Re-running the legacy packaged v216 manifest here can reject
            # a correct new-season L variant and mix previous-season sources.
            environment=prepared.get("environment_manifest")
            if (type(environment) is not dict or
                    environment.get(
                        "fresh_v212_installed_manifest_sha256") is None):
                bootstrap_path=folder/"generated"/"v098_bootstrap_result.json"
                bootstrap_result=json.loads(
                    bootstrap_path.read_text(encoding="utf8"))
                environment=self._seal_environment_manifest(
                    folder,bootstrap_result,folder/receipt_info["path"],
                    prepared.get("profile_stage"))
        else:
            environment=prepared.get("environment_manifest")
        # The environment manifest is sealed before the optimizer worker is
        # launched, so Start never outruns its exact v213/v208 provenance.
        return folder,hydrated,environment,(
            receipt_info if hydrated else None)

    def start_with_internal_special_L(self, params):
        """Existing six-case start, unchanged execution and L contract."""
        folder,hydrated,environment,receipt_info=(
            self.prepare_with_internal_special_L(params))
        response=self.launch(folder)
        if hydrated:
            response["static_L_start_receipt"]=receipt_info
            if "selected_static_native_calls" in hydrated:
                response["selected_static_native_calls_this_start"]=(
                    hydrated["selected_static_native_calls"])
                response["selected_G_delta_native_calls_this_start"]=(
                    hydrated["selected_G_delta_native_calls"])
            if "selected_oil_native_calls" in hydrated:
                response["selected_oil_native_calls_this_start"]=hydrated["selected_oil_native_calls"]
        response["environment_manifest"]=environment
        response["static_L_native_calls_this_start"]=(
            hydrated["native_new_calls"] if hydrated else 0)
        response["static_L_reused_exact_variants"]=(
            hydrated["cache_reused"] if hydrated else 0)
        return response

    def args_for_existing(self, folder):
        """Recover binary/options from self-generated manifest, verify v106 identity."""
        m = folder / "generated" / "manifest.json"
        if not m.is_file():
            raise HTTPException(409,detail={"code":"SESSION_MANIFEST_MISSING"})
        try:
            manifest = json.loads(m.read_text(encoding="utf8"))
            user = json.loads((folder / "user.json").read_text(encoding="utf8"))
            recorded = json.loads((folder / "V106_SESSION_IDENTITY.json").read_text(
                encoding="utf8"))
            # Use original v106 SHA identity; an alias to identical bytes
            # does not invalidate an existing saved result/session.
            binary=pathlib.Path(manifest["native_binary"]).expanduser().resolve()
            rev = manifest["native_revision"]
            static = manifest["static_cache_json"]
            # A manually staged, internal ordinary-gear variant may be
            # resumed under its own sealed identity. Browser planning still
            # creates DEFAULT variants only; never infer one from user gear.
            variant = recorded.get("ordinary_variant")
            current_season=bool(recorded.get("current_season_product",False))
            has_source=("current_season_source_catalog" in recorded)
            source_record=recorded.get("current_season_source_catalog") or {}
            fresh_sha=recorded.get("fresh_v212_installed_manifest_sha256")
            if fresh_sha is not None:
                # Original exact build path, never a path supplied by the UI
                # or an unchecked filename from an old session.
                build=source_record.get("game_build")
                if (type(build) is not str or
                    re.fullmatch(r"\d+(?:\.\d+){3}",build) is None):
                    raise sessions.SessionBlocked(
                        "FRESH_V212_SESSION_BUILD_INVALID")
                source_path=(self.root/"_fresh_season_sources"/
                    ("wago_"+build)/"fresh_source"/"v213_candidate_catalog.json")
                package_path=None
                self._verify_environment_dependencies(
                    self._read_environment_summary(folder),folder)
            else:
                source_path=(self.source_catalog_path()
                             if current_season and has_source else None)
                package_path=(self.package_manifest_path()
                              if type(source_record) is dict and
                                 source_record.get("package_manifest_sha256")
                              else None)
            key, check = sessions.session_key(
                user,binary,rev,static,ordinary_variant=variant,
                independent_334=recorded.get("independent_334",False),
                independent_target_level=recorded.get("independent_target_level",False),
                current_season_product=current_season,
                source_catalog_path=source_path,
                package_manifest_path=package_path,
                fresh_installed_manifest_sha256=fresh_sha)
            selected_seal=("v435_selected_source_identity" in recorded)
            recorded_base={k:v for k,v in recorded.items()
                           if k not in ("profile_stage",
                                        "v435_selected_source_identity")}
            current_base={k:v for k,v in check.items() if k!="profile_stage"}
            recorded_key=sessions.sha(
                sessions.canonical(recorded).encode("utf8"))[:20]
            if recorded_key != folder.name or current_base != recorded_base:
                raise sessions.SessionBlocked("SESSION_BINARY_REVISION_OR_CACHE_DRIFT")
            if "profile_stage" in recorded and not selected_seal:
                profile_stage.verify_existing(folder,recorded)
            if selected_seal:
                # Parent checks binary/cache and complete sealed user key.
                # The child v096 validates v217 and recomputes v098 before
                # any Native; this is not an early source authorization.
                if manifest.get(
                      bootstrap.entry.SELECTED_FRESH_SEASON_FIELD) is None:
                    raise sessions.SessionBlocked(
                        "B8_SELECTED_REPLAY_MANIFEST_REQUIRED")
            return binary,rev,static
        except HTTPException:
            raise
        except Exception as exc:
            raise blocked(exc) from None

    def is_active(self, folder):
        key = folder.name
        child = self.children.get(key)
        if child is not None and child.poll() is None:
            return True
        # Never CREATE lock files during GET/status; status is read-only.
        # A worker can survive an HTTP server restart: check an existing
        # OS lock rather than trusting the persisted RUNNING status.
        if not (folder / "V106_WORKER.lock").is_file():
            return False
        try:
            with sessions.worker_lock(folder):
                return False
        except sessions.SessionBlocked:
            return True

    def status(self, folder):
        item = sessions.progress(folder)
        p = sessions.paths(folder)
        return {"session_id":folder.name,"active":self.is_active(folder),
                "cancel_requested":p["cancel"].exists(),
                "progress":item,
                "result_ready":p["final"].is_file(),
                "environment_manifest":self._read_environment_summary(folder),
                "environment_build":self._read_environment_build_summary(folder)}

    def inputs(self, folder):
        """Restore locally sealed user form/SimC paths, read-only and without Native.

        No binary hashing on every page refresh: actual identity and executable
        checks still belong to start/resume and the v106 session controller.
        """
        try:
            recorded = json.loads((folder / "V106_SESSION_IDENTITY.json").read_text(
                encoding="utf8"))
            user = json.loads((folder / "user.json").read_text(encoding="utf8"))
            manifest = json.loads((folder / "generated" / "manifest.json").read_text(
                encoding="utf8"))
            if (recorded.get("schema") != sessions.SCHEMA or
                user != recorded.get("user") or
                manifest.get("native_revision") != recorded.get("simc_revision") or
                not isinstance(manifest.get("native_binary"), str) or
                not manifest["native_binary"] or
                not isinstance(manifest.get("static_cache_json"), (str, type(None)))):
                raise sessions.SessionBlocked("SESSION_INPUTS_OR_MANIFEST_DRIFT")
            restored_oils={}
            verified_build=None
            restored_manifest_sha=None
            verified_user_variant=None
            if recorded.get("fresh_v212_installed_manifest_sha256") is not None:
                # The existing start/resume proof validates the original
                # v212 SHA, source, chosen hand+physical IDs and session.
                # Reusing it on a read-only restore avoids a second selector.
                summary=self._read_environment_summary(folder)
                restored_oils=self._verify_environment_dependencies(
                    summary,folder)
                if type(restored_oils) is not dict:
                    raise environment_manifest.EnvironmentBlocked(
                        "WEB_FRESH_SESSION_INSTALL_SHA_DRIFT")
                # Historic sealed/mocked session summaries may omit the
                # display build; existing exact v212 validation still owns
                # authority. Do not fail read-only restore on optional UI data.
                verified_build=summary.get("game_build")
                # Restore only already-sealed v113/v212 source identity. No
                # new source acquisition, budget recalculation or Native.
                digest=recorded["fresh_v212_installed_manifest_sha256"]
                # The original session/install identity was already checked
                # against its immutable v212 source; expose only its digest.
                # No source discovery or new approval on a read-only GET.
                if type(verified_build) is str and type(digest) is str:
                    restored_manifest_sha=digest
                if verified_build and type(digest) is str:
                    directory=(self.root/"_fresh_season_sources"/
                               ("wago_"+verified_build)/"fresh_source")
                    snapshot_file=directory/("v113_profile_"+digest[:20]+".json")
                    installed_file=directory/("v212_installed_"+digest[:20]+".json")
                    if (snapshot_file.is_file() and
                            not snapshot_file.is_symlink() and
                            installed_file.is_file() and
                            not installed_file.is_symlink()):
                        try:
                            raw=snapshot_file.read_bytes()
                            snapshot=json.loads(raw.decode("utf8"))
                            installed,_=environment_manifest.read_json(installed_file)
                            environment_manifest.verify_fresh_installed_environment(
                                installed)
                            stage_root,stage_id,out=self._verified_profile_stage(
                                installed)
                            if (snapshot_file!=stage_root/out or
                                snapshot.get("installed_manifest_sha256")!=digest or
                                raw!=(stage_engine.canonical(snapshot)+"\n").encode("utf8")):
                                raise environment_manifest.EnvironmentBlocked(
                                    "WEB_USER_VARIANT_SAVED_SNAPSHOT_INVALID")
                            stage_engine.verify_stage(
                                root=stage_root,stage_id=stage_id,
                                stage_version="v113-fresh-v212-profile-snapshot-1",
                                inputs={"installed_manifest_sha256":digest,
                                        "source_catalog_artifact_sha256":
                                            installed["source_catalog_artifact_sha256"],
                                        "snapshot_sha256":stage_engine.digest(raw)},
                                outputs={"snapshot":out})
                            if installed["manifest_sha256"]==digest:
                                original=snapshot.get("environment_result") or {}
                                compilation=original.get("source_compilation") or {}
                                gem=compilation.get(
                                    "physical_gem_layout_unadmitted") or {}
                                sockets=gem.get("socket_total")
                                special=gem.get("special_gem_id")
                                flask=installed.get("official_F_physical_source")
                                if (type(sockets) is int and
                                        4<=sockets<=64 and
                                        type(flask) is dict):
                                    verified_user_variant={
                                        "socket_total":sockets,
                                        "special_gem_id":special,
                                        "flask_item_id":flask.get(
                                            "physical_item_id")}
                        except (OSError,ValueError,TypeError,KeyError,
                                stage_engine.StageExecutionBlocked,
                                environment_manifest.EnvironmentBlocked):
                            pass
            return {"schema": "v116_local_session_inputs_read_only_v1",
                    "session_id": folder.name, "user": user,
                    "binary": manifest["native_binary"],
                    "revision": recorded["simc_revision"],
                    "static_cache": manifest["static_cache_json"],
                    "current_season_product":bool(
                        recorded.get("current_season_product",False)),
                    "verified_oil_item_ids_by_hand":restored_oils,
                    "installed_season_game_build":verified_build,
                    "installed_manifest_sha256":restored_manifest_sha,
                    "verified_user_variant":verified_user_variant,
                    "native_called": False}
        except Exception as exc:
            raise blocked(exc) from None

    def launch(self, folder, *, cache_only=False):
        with self.lock:
            if self.is_active(folder):
                raise HTTPException(409,detail={"code":"SESSION_ALREADY_RUNNING"})
            try:
                # Verify the sealed package/source identity before spawning a worker.
                environment=self._read_environment_summary(folder)
                self._verify_environment_dependencies(environment,folder)
                binary, rev, static = self.args_for_existing(folder)
                if cache_only:
                    sessions.cache_only_preflight(folder)
                else:
                    # Already-resolved identical manifest/user: real worker
                    # owns preparing/running without creating a new identity.
                    sessions.clear_cancel(folder)
                cmd = [sys.executable,
                       str(pathlib.Path(sessions.__file__).resolve()),
                       "--session",str(folder),"--binary",str(binary),
                       "--revision",rev]
                if static: cmd.extend(["--static-cache",str(static)])
                if cache_only: cmd.append("--cache-only")
                log = sessions.paths(folder)["log"]
                with log.open("a",encoding="utf8",buffering=1) as stream:
                    stream.write("\n=== V113 LOCAL API CACHE_ONLY ===\n"
                                 if cache_only else
                                 "\n=== V113 LOCAL API START / RESUME ===\n")
                    stream.flush()
                    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name=="nt" else 0
                    process = subprocess.Popen(cmd, stdin=subprocess.DEVNULL,
                             stdout=stream, stderr=subprocess.STDOUT,
                             creationflags=flags,
                             env={**os.environ,"PYTHONIOENCODING":"utf-8"})
                self.children[folder.name] = process
            except HTTPException:
                raise
            except Exception as exc:
                raise blocked(exc) from None
        return {"session_id":folder.name,
                "status":"CACHE_ONLY_WORKER_STARTED" if cache_only else "WORKER_STARTED",
                "native_attempt_ceiling_cumulative":6,
                "new_native_execution_permitted":not cache_only,
                "environment_manifest":environment,
                "environment_build":self._read_environment_build_summary(folder)}

    def longrun_launch(self, folder, *, budget=None, batch=4, elapsed=900,
                       cache_only=False, archive=None, sha=None, continuous=False):
        with self.lock:
            if self.is_active(folder):
                raise HTTPException(409,detail={"code":"SESSION_ALREADY_RUNNING"})
            queued_for_spawn=False
            try:
                environment=self._read_environment_summary(folder)
                self._verify_environment_dependencies(environment,folder)
                previous=longrun_sessions.config(folder)
                requested_budget=(previous["native_budget"]
                                  if previous is not None else budget)
                # The default user 64-case run must never be launched or
                # resumed from the packaged, historically pinned v213
                # source-only catalog.  Existing 12-case legacy sessions and
                # read-only cache/report access remain unchanged.
                if (not cache_only and
                    (continuous or (type(requested_budget) is int and
                                   requested_budget>=64)) and
                    (type(environment) is not dict or
                     not environment.get(
                         "fresh_v212_installed_manifest_sha256"))):
                    raise HTTPException(422,detail={"code":
                        "WEB_PRIMARY_VERIFIED_SEASON_INSTALL_REQUIRED"})
                self.args_for_existing(folder)
                if previous is None:
                    if budget is None:
                        raise longrun_sessions.LocalLongRunBlocked(
                            "V293_LONGRUN_START_REQUIRED")
                    longrun_sessions.establish(folder,budget)
                else:
                    if budget is not None and budget!=previous["native_budget"]:
                        raise longrun_sessions.LocalLongRunBlocked(
                            "V293_EXISTING_SESSION_BUDGET_CANNOT_CHANGE")
                    budget=previous["native_budget"]
                    longrun_sessions.prepare(folder,budget)
                if archive is not None and (
                     not sha or batch!=0 or not cache_only):
                    raise longrun_sessions.LocalLongRunBlocked(
                        "V293_IMPORT_MUST_BE_CACHE_ONLY")
                if cache_only and archive is None:
                    staged=longrun_sessions.stage_path(folder,budget)
                    if not (staged/"simc_results"/"V291_JOURNAL.jsonl").is_file():
                        raise longrun_sessions.LocalLongRunBlocked(
                            "V293_CACHE_ONLY_REQUIRES_EXISTING_CASES")
                cancel=longrun_sessions.stage_path(folder,budget)/"CANCEL"
                if cancel.exists():cancel.unlink()
                longrun_sessions.state(folder,"QUEUED")
                queued_for_spawn=True
                cmd=[sys.executable,
                     str(pathlib.Path(longrun_sessions.__file__).resolve()),
                     "--session",str(folder),
                     "--max-native-calls",str(budget),
                     "--batch",str(batch),
                     "--max-elapsed-seconds",str(elapsed)]
                if continuous:cmd.append("--continuous")
                if cache_only:cmd.append("--cache-only")
                if archive is not None:
                    cmd.extend(["--portable-archive",archive,
                                "--portable-sha256",sha])
                log=folder/"V293_WORKER.log"
                with log.open("a",encoding="utf8",buffering=1) as stream:
                    stream.write("\n=== V293 LONGRUN OPT-IN ===\n")
                    stream.flush()
                    flags=getattr(subprocess,"CREATE_NO_WINDOW",0) if os.name=="nt" else 0
                    child=subprocess.Popen(
                        cmd,stdin=subprocess.DEVNULL,
                        stdout=stream,stderr=subprocess.STDOUT,
                        creationflags=flags,
                        env={**os.environ,"PYTHONIOENCODING":"utf-8"})
                self.children[folder.name]=child
                queued_for_spawn=False
            except HTTPException:
                raise
            except Exception as exc:
                # The queued state was written, but no OS worker was
                # successfully launched. The prior V291_RESULT/journal
                # remains durable; never leave a phantom QUEUED worker.
                # Do not expose the local executable/log path in status.
                if queued_for_spawn:
                    try:
                        longrun_sessions.state(
                            folder,"BLOCKED_OR_PARTIAL",
                            reason="V293_WORKER_LAUNCH_FAILED_BEFORE_NATIVE")
                    except (OSError,ValueError):
                        pass  # Keep the original launch exception.
                raise blocked(exc) from None
        return {"session_id":folder.name,
                "status":"LONGRUN_IMPORT_STARTED" if archive is not None
                    else "LONGRUN_CACHE_ONLY_STARTED" if cache_only
                    else "LONGRUN_WORKER_STARTED",
                "native_attempt_ceiling_cumulative":budget,
                "max_new_native_this_invocation":(0 if cache_only else batch),
                "new_native_execution_permitted":not cache_only}

    def longrun_prepare(self, request):
        """Explicit source-bound session setup; no optimization DPS Native."""
        if request.current_season_product is not True:
            raise HTTPException(422,detail={"code":"V293_VERIFIED_SEASON_REQUIRED"})
        # Older Windows source ZIPs can still create historical v213 plans.
        # The default 64/continuous product run is different: require an
        # explicitly selected same-build v212 installed READY environment.
        # Refuse before profile staging, L Native, or any DPS subprocess.
        if ((request.continuous or request.max_native_calls>=64) and
                request.installed_season_game_build is None):
            raise HTTPException(422,detail={"code":
                "WEB_PRIMARY_VERIFIED_SEASON_INSTALL_REQUIRED"})
        params=UserRequest(
            controls=request.controls,binary=request.binary,
            revision=request.revision,static_cache=request.static_cache,
            current_season_product=True,
            selected_oil_item_ids_by_hand=request.selected_oil_item_ids_by_hand,
            user_socket_total=request.user_socket_total,
            user_special_gem_id=request.user_special_gem_id,
            selected_flask_item_id=request.selected_flask_item_id,
            installed_season_game_build=request.installed_season_game_build,
            installed_manifest_sha256=request.installed_manifest_sha256)
        folder,hydrated,environment,receipt_info=(
            self.prepare_with_internal_special_L(params))
        with self.lock:
            if self.is_active(folder):
                raise HTTPException(409,detail={"code":"SESSION_ALREADY_RUNNING"})
            try:
                self._verify_environment_dependencies(environment,folder)
                self.args_for_existing(folder)
                longrun_sessions.establish(folder,request.max_native_calls)
            except HTTPException:
                raise
            except Exception as exc:
                raise blocked(exc) from None
        response={"session_id":folder.name,
                  "status":"LONGRUN_SOURCE_PREPARED_NO_DPS_NATIVE",
                  "native_attempt_ceiling_cumulative":request.max_native_calls,
                  "new_dps_native_calls":0,
                  "environment_manifest":environment,
                  "static_L_native_calls_this_start":(
                      hydrated["native_new_calls"] if hydrated else 0),
                  "static_L_reused_exact_variants":(
                      hydrated["cache_reused"] if hydrated else 0)}
        if hydrated:
            response["static_L_start_receipt"]=receipt_info
            if "selected_static_native_calls" in hydrated:
                response["selected_static_native_calls_this_start"]=(
                    hydrated["selected_static_native_calls"])
                response["selected_G_delta_native_calls_this_start"]=(
                    hydrated["selected_G_delta_native_calls"])
            if "selected_oil_native_calls" in hydrated:
                response["selected_oil_native_calls_this_start"]=hydrated["selected_oil_native_calls"]
        return response

    def longrun_start(self, request):
        prepared=self.longrun_prepare(request)
        launched=self.longrun_launch(
            self.folder(prepared["session_id"]),
            budget=request.max_native_calls,
            batch=request.max_new_native_this_invocation,
            elapsed=request.max_elapsed_seconds,continuous=request.continuous)
        launched.update({k:v for k,v in prepared.items()
                         if k not in ("status","new_dps_native_calls")})
        return launched

    def longrun_status(self, folder):
        try:
            return longrun_sessions.read_status(
                folder,active=self.is_active(folder))
        except Exception as exc:
            raise blocked(exc) from None

    def longrun_cancel(self, folder):
        with self.lock:
            try:
                saved=longrun_sessions.config(folder)
            except Exception as exc:
                raise blocked(exc) from None
            if saved is None or not self.is_active(folder):
                raise HTTPException(409,detail={"code":"LONGRUN_NOT_RUNNING"})
            worker=longrun_sessions.worker_state_path(folder)
            doc=(json.loads(worker.read_text(encoding="utf8"))
                 if worker.is_file() else {})
            if doc.get("status") not in ("QUEUED","RUNNING"):
                raise HTTPException(409,detail={"code":"LONGRUN_NOT_RUNNING"})
            flag=longrun_sessions.stage_path(
                folder,saved["native_budget"])/"CANCEL"
            flag.touch(exist_ok=True)
            return {"session_id":folder.name,
                    "status":"LONGRUN_CANCEL_REQUESTED_AFTER_CURRENT_NATIVE"}

    def longrun_result(self, folder):
        try:
            return longrun_sessions.read_result(folder)
        except Exception as exc:
            raise blocked(exc) from None

    def cancel(self, folder):
        with self.lock:
            if not self.is_active(folder):
                raise HTTPException(409,detail={"code":"SESSION_NOT_RUNNING"})
            sessions.request_cancel(folder)
            return {"session_id":folder.name,
                    "status":"CANCEL_REQUESTED_AFTER_CURRENT_NATIVE"}

    def result(self, folder):
        path = sessions.paths(folder)["final"]
        if not path.is_file():
            raise HTTPException(404,detail={"code":"RESULT_NOT_READY"})
        try:
            data=json.loads(path.read_text(encoding="utf8"))
            text=sessions.format_result(data)
            return {"session_id":folder.name,
                    "status":data["status"],
                    "native_calls_cumulative":data["native_calls_cumulative"],
                    "cache_hits_this_run":data["cache_hits_this_run"],
                    "base_B":data["base_B"],"final_T":data["final_T"],
                    "user_result":data["user_result"],
                    "display_text":text}
        except Exception as exc:
            raise blocked(exc) from None

def create_app(*,root=None, token=None, batch_root=None, update_root=None,
               update_platform=None, source_credential_store=None):
    jobs=LocalJobs(root or sessions.DEFAULT_ROOT,
                   source_credential_store=source_credential_store)
    updater=simc_updates.SimCManager(
        update_root or (jobs.root.parent/"simc-managed"),platform=update_platform)
    snapshots=(pathlib.Path(batch_root).expanduser().resolve() if batch_root
               else pathlib.Path.home()/"SIMC_Secondary_Optimizer"/"v147_batch")
    key=token or secrets.token_urlsafe(32)
    app=FastAPI(title="SIMC Secondary Optimizer LOCAL API",
                version="113.0",openapi_url=None,docs_url=None,redoc_url=None)
    app.state.jobs=jobs
    app.state.simc_updates=updater
    simc_prefs=simc_connection.LocalSimCConnectionPrefs(jobs.root.parent)

    @app.exception_handler(RequestValidationError)
    async def redact_source_credential_validation(request: Request, exc):
        # FastAPI's normal validation body includes a copy of the submitted
        # input. Never echo any part of Client ID/Secret on this one route.
        if request.url.path in ("/api/v1/source-credentials/save",
                                "/api/v1/simc-connection/confirm"):
            code=("SOURCE_API_CREDENTIAL_FIELDS_INVALID"
                  if request.url.path.endswith("source-credentials/save")
                  else "SIMC_CONNECTION_INPUTS_INVALID")
            return JSONResponse(
                {"detail":{"code":code}},
                status_code=422)
        return await request_validation_exception_handler(request,exc)

    @app.middleware("http")
    async def localhost_firewall(request: Request, call_next):
        raw_host=request.headers.get("host","")
        try:
            parsed=urlsplit("http://" + raw_host)
            valid_host=(parsed.hostname==LOCAL_HOST and
                        parsed.username is None and parsed.password is None and
                        parsed.path=="" and parsed.query=="" and parsed.fragment=="")
            port=parsed.port
        except ValueError:
            valid_host=False;port=None
        peer=request.client.host if request.client else None
        # 127.0.0.1 binding is enforced again in main(); this is a separate
        # DNS rebinding / non-loopback client defense.
        if not valid_host or peer not in ("127.0.0.1","::1","testclient"):
            return JSONResponse({"detail":{"code":"LOOPBACK_ONLY"}},403)
        expected_origin="http://" + raw_host
        origin=request.headers.get("origin")
        if origin is not None and origin != expected_origin:
            return JSONResponse({"detail":{"code":"FOREIGN_ORIGIN_BLOCKED"}},403)
        if request.headers.get("sec-fetch-site")=="cross-site":
            return JSONResponse({"detail":{"code":"CROSS_SITE_BLOCKED"}},403)
        if request.url.path not in ("/api/v1/health","/api/v1/bootstrap") and request.url.path not in PUBLIC_STATIC:
            if not secrets.compare_digest(
                request.headers.get("x-simc-local-token",""), key):
                return JSONResponse({"detail":{"code":"LOCAL_TOKEN_REQUIRED"}},403)
        if request.method in ("POST","PUT","PATCH","DELETE"):
            ct=request.headers.get("content-type","").split(";",1)[0].strip().lower()
            if ct!="application/json":
                return JSONResponse({"detail":{"code":"JSON_CONTENT_TYPE_REQUIRED"}},415)
            length=request.headers.get("content-length")
            if length:
                try:
                    large=int(length)>131072
                except ValueError:
                    return JSONResponse({"detail":{"code":"CONTENT_LENGTH_INVALID"}},400)
                if large:
                    return JSONResponse({"detail":{"code":"PAYLOAD_TOO_LARGE"}},413)
        response = await call_next(request)
        # No inline scripts, remote resources, or browser-side file/network APIs.
        # Token and local user output should not be cached by browser/proxy.
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; img-src 'self' data: https://render.worldofwarcraft.com; "
            "base-uri 'none'; form-action 'self'; frame-ancestors 'none'")
        return response

    @app.get("/")
    def index():
        return FileResponse(WEB_ASSETS / "index.html",media_type="text/html")

    @app.get("/assets/app.js")
    def browser_js():
        return FileResponse(WEB_ASSETS / "app.js",media_type="text/javascript")

    @app.get("/assets/styles.css")
    def browser_styles():
        return FileResponse(WEB_ASSETS / "styles.css",media_type="text/css")

    def updates_action(operation,*,read_only=False):
        # Never switch managed binaries during a running SimC worker.
        # Authenticated read-only status is safe and must remain available.
        if not read_only and any(jobs.is_active(jobs.root/sid) for sid in tuple(jobs.children)):
            raise HTTPException(409,detail={"code":"ACTIVE_SIMC_JOB_UPDATE_BLOCKED"})
        try:
            return operation()
        except (simc_updates.UpdateBlocked,
                simc_one_click.ProvisionBlocked) as exc:
            raise HTTPException(422,detail={"code":str(exc)}) from None
        except (OSError,TimeoutError,ValueError,subprocess.SubprocessError) as exc:
            raise HTTPException(409,detail={"code":"OFFICIAL_SIMC_UPDATE_UNAVAILABLE",
                                           "kind":type(exc).__name__}) from None

    @app.get("/api/v1/simc-updates/status")
    def simc_update_status():
        return updates_action(updater.status,read_only=True)

    @app.post("/api/v1/simc-updates/check")
    def simc_update_check():
        # Preserve the historical raw offer contract for existing callers.
        return updates_action(updater.check)

    @app.post("/api/v1/simc-updates/prepare-auto")
    def simc_update_prepare_auto():
        # One explicit user action, zero personal GitHub credentials. Only
        # authenticated local requests can change the managed binary pointer.
        # No automatic CI dispatch, no season changes, no DPS Native.
        return updates_action(
            lambda:simc_one_click.prepare_one_click(updater))

    @app.post("/api/v1/simc-updates/check-compatible")
    def simc_update_check_compatible():
        # Explicit user-click only; no Native DPS or season build. Do not
        # conflate a saved SimC header observation with a fresh CLI check.
        def run():
            result=updater.check_for_retail_compatibility()
            try:
                saved=(simc_prefs.status().get("saved") or {})
                observed=saved.get("observed_game_build")
                if observed and re.fullmatch(r"\d+(?:\.\d+){3}",observed):
                    comp=result["retail_compatibility"]
                    comp["saved_simc_observed_build"]=observed
                    comp["saved_simc_observation_fresh"]=False
                    comp["saved_simc_matches_kr_build"]=(
                        observed==comp.get("kr_game_build")
                        if comp.get("kr_game_build") else None)
            except (ValueError,OSError,TypeError,KeyError):
                pass
            return result
        return updates_action(run)

    @app.post("/api/v1/simc-updates/install")
    def simc_update_install(request:UpdateInstallRequest):
        return updates_action(lambda:updater.install(request.filename))

    @app.post("/api/v1/simc-updates/install-local")
    def simc_update_install_local(request:UpdateLocalArchiveRequest):
        return updates_action(lambda:updater.install_local(request.archive_path))

    @app.post("/api/v1/simc-updates/install-self-built")
    def simc_update_install_self_built(request:UpdateSelfBuiltZipRequest):
        # User-picked local artifact only. No GitHub token, remote URL,
        # automatic compilation, official-distribution claim or DPS Native.
        return updates_action(
            lambda:updater.install_self_built(request.artifact_path))

    @app.post("/api/v1/simc-updates/rollback")
    def simc_update_rollback():
        return updates_action(updater.rollback)


    @app.get("/api/v1/verified-oil-loadouts")
    def verified_oil_loadouts(ilevel: int = 334, game_build: str | None = None):
        try:
            return jobs.installed_oil_loadouts(ilevel,game_build)
        except environment_manifest.EnvironmentBlocked as exc:
            raise blocked(exc) from None

    @app.get("/api/v1/season-option-catalog")
    def season_option_catalog(game_build: str | None = None,
                              target_ilevel: int = 334,
                              installed_manifest_sha256: str | None = None):
        """Read-only option scope; an explicit v212 SHA cannot use old sources."""
        exact=(game_build is not None or
               installed_manifest_sha256 is not None)
        if exact and (
                type(game_build) is not str or
                re.fullmatch(r"\d+(?:\.\d+){3}",game_build) is None or
                type(installed_manifest_sha256) is not str or
                re.fullmatch(r"[a-f0-9]{64}",
                             installed_manifest_sha256) is None or
                not 1<=target_ilevel<=1000):
            raise HTTPException(422,detail={
                "code":"SEASON_OPTIONS_EXACT_INSTALLED_SCOPE_REQUIRED"})
        try:
            fresh=jobs._verified_fresh_profile_result
            compilation=(fresh.get("source_compilation")
                         if type(fresh) is dict else None)
            sealed=None
            if exact:
                docs=(jobs.root/"_fresh_season_sources"/
                      ("wago_"+game_build)/"fresh_source")
                installed_path=docs/("v212_installed_"+
                                     installed_manifest_sha256[:20]+".json")
                source_path=docs/"v213_candidate_catalog.json"
                if (docs.is_symlink() or
                    installed_path.is_symlink() or
                    source_path.is_symlink() or
                    not installed_path.is_file() or
                    not source_path.is_file()):
                    raise environment_manifest.EnvironmentBlocked(
                        "INSTALLED_SEASON_OPTION_SOURCE_MISSING")
                sealed,_=environment_manifest.read_json(
                    installed_path,environment_build.MAX_RECEIPT_BYTES)
                environment_manifest.verify_fresh_installed_environment(sealed)
                if (sealed["manifest_sha256"]!=installed_manifest_sha256 or
                    sealed["game_build"]!=game_build or
                    sealed["target_ilevel"]!=target_ilevel):
                    raise environment_manifest.EnvironmentBlocked(
                        "INSTALLED_SEASON_OPTION_IDENTITY_MISMATCH")
                physical=sealed.get("official_O_physical_source")
                oils=(physical.get("selected_oil_item_ids_by_hand")
                      if type(physical) is dict else {})
                receipt=environment_build.find_verified_installed_season_environment(
                    jobs.root,target_ilevel,expected_game_build=game_build,
                    selected_oil_item_ids_by_hand=oils,
                    expected_installed_manifest_sha256=installed_manifest_sha256)
                if (receipt is None or
                    receipt["installed_manifest_sha256"]!=installed_manifest_sha256):
                    raise environment_manifest.EnvironmentBlocked(
                        "INSTALLED_SEASON_OPTION_STAGE_RECEIPT_CHANGED")
                source,raw_sha=environment_manifest.read_json(source_path)
                source_to_catalog.verify_catalog(source)
                if (raw_sha!=sealed["source_catalog_artifact_sha256"] or
                    source["manifest_sha256"]!=
                        sealed["source_catalog_manifest_sha256"] or
                    source["game_build"]!=game_build):
                    raise environment_manifest.EnvironmentBlocked(
                        "INSTALLED_SEASON_OPTION_SOURCE_SHA_CHANGED")
            else:
                source_path=(pathlib.Path(compilation["source_catalog_path"])
                             if type(compilation) is dict and
                             type(compilation.get("source_catalog_path")) is str
                             else jobs.source_catalog_path())
            published=(ui_catalog.public_options(source_path)
                       if source_path else ui_catalog.public_options())
            if exact and (
                published.get("source_catalog",{}).get("manifest_sha256")!=
                    sealed["source_catalog_manifest_sha256"] or
                published.get("season_build")!=game_build):
                raise environment_manifest.EnvironmentBlocked(
                    "INSTALLED_SEASON_OPTION_PROJECTION_SOURCE_CHANGED")
            # Only the actual verified installed v212 environment can expose
            # new-season runeforges. A v213 source-only candidate is not a
            # selectable item. Never fall back to hardcoded web IDs.
            choices={"status":"DK_RUNEFORGE_NOT_INSTALLED","items":[]}
            oil={"status":"NO_POSITIVE_O_INSTALLED","items":[]}
            # v212 may have completed policy-A registration while v196/v098
            # still lack a general user-selected static E vector and final
            # SimC profile binding. Publish its EXACT installed identity as
            # read-only registration, not an executable enchant choice.
            registered={"status":"NO_VERIFIED_INSTALLED_ENCHANTS",
                        "items":[],"runtime_selectable":False,
                        "new_approval_granted":False}
            if exact:
                doc=sealed
                installation={"manifest_sha256":installed_manifest_sha256}
                option_source_verified=True
            else:
                installation=(compilation.get("verified_environment_install")
                              if type(compilation) is dict else None)
                option_source_verified=False
                if type(installation) is dict:
                    path=pathlib.Path(installation["stage_output_path"])
                    if path.is_file() and not path.is_symlink():
                        doc,_=environment_manifest.read_json(path)
                        environment_manifest.verify_fresh_installed_environment(doc)
                        option_source_verified=(
                            doc["manifest_sha256"]==installation["manifest_sha256"]
                            and doc["source_catalog_manifest_sha256"]==
                            published.get("source_catalog",{}).get(
                                "manifest_sha256"))
            if option_source_verified:
                if exact:
                    confirmed=doc["published_verified_options"]
                    registered={"status":(
                        "INSTALLED_POLICY_A_REGISTRATIONS_RUNTIME_BINDING_PENDING"
                        if confirmed else "NO_VERIFIED_INSTALLED_ENCHANTS"),
                        "items":[{
                            "enchant_id":entry["enchant_id"],
                            "slot":entry["slot"],
                            "simc_token":entry["simc_token"],
                            "highest_verified_quality_rank":
                                entry["highest_verified_quality_rank"],
                            **({"verified_fixed_E":
                                    dict(entry["verified_fixed_E"]),
                                "chmv_budget_receipt_sha256":
                                    entry["chmv_budget_receipt_sha256"]}
                               if "verified_fixed_E" in entry else {})}
                            for entry in confirmed],
                        "installed_manifest_sha256":doc["manifest_sha256"],
                        # A signed Policy A item with a verified E0 vector
                        # may use the exact-user v098/v096 profile route.
                        # This is not an effect/proc proof and does not
                        # make unrelated E+/unknown options selectable.
                        "installed_E0_final_finger_candidates":[{
                            "enchant_id":entry["enchant_id"],
                            "simc_token":entry["simc_token"],
                            "slot":entry["slot"],
                            "highest_verified_quality_rank":
                                entry["highest_verified_quality_rank"],
                            "chmv_budget_receipt_sha256":
                                entry["chmv_budget_receipt_sha256"]}
                            for entry in confirmed
                            if entry.get("slot")=="finger1/finger2"
                            and type(entry.get("verified_fixed_E")) is dict
                            and set(entry["verified_fixed_E"])==
                                set(environment_manifest.season_budget.STATS)
                            and all(type(entry["verified_fixed_E"][stat])
                                    is int and
                                    0<=entry["verified_fixed_E"][stat]<=100000
                                    for stat in environment_manifest.
                                        season_budget.STATS)
                            and environment_manifest.valid_sha(
                                entry.get("chmv_budget_receipt_sha256"))],
                        "runtime_selectable":False,
                        "unresolved":"FINAL_USER_ITEM_AND_SIMC_MASK_STILL_VERIFIED_AT_START",
                        "new_approval_granted":False}
                source=doc.get("verified_DK_runeforges")
                if type(source) is dict:
                    choices={"status":"PINNED_DK_RUNES_INSTALLED",
                             "items":source["items"],
                             "source_sha256":source["source_sha256"],
                             "source_manifest_sha256":
                                 source["manifest_sha256"],
                             "game_build":source["game_build"]}
                positive=doc.get("official_O_physical_source")
                if type(positive) is dict:
                    oil={"status":"VERIFIED_INSTALLED_O_HAND_SET_ONLY",
                         "items":[{"hand":hand,**row}
                             for hand,row in sorted(
                                 positive["oil_by_hand"].items())],
                         "source_sha256":
                             positive["original_O_source_sha256"],
                         "user_selectable_individually":False}
            # v535: source-bound per-user runtime *candidates*, separate
            # from the general unapproved season catalogue. Do not mark
            # unverified source rows or other character/loadouts selectable.
            exact_runtime={"status":"EXACT_USER_RUNTIME_SCOPE_UNAVAILABLE",
                           "items":[],"general_selectable":False}
            if exact and doc.get("game_build")==exact_e0_enchant.BUILD:
                try:
                    projected=exact_positive_enchant.project(
                        doc,{"finger1":8025},manual_final_T=None)
                    if (projected["base_B"]==3137 and
                        doc["target_ilevel"]==334):
                        exact_e0_enchant.source(
                            exact_e0_enchant.CHOICE,source_path)
                        items=[{"enchant_id":7967,
                                "name":"독수리의 눈",
                                "fixed_E":dict(exact_e0_enchant.ZERO),
                                "status":"EXACT_RUNTIME_NATIVE_WITNESSED"}]
                        for eid,name in ((8025,"실버문의 기민함"),
                                         (7965,"아마니의 특화")):
                            _,E=exact_positive_enchant.source(
                                {"finger1":eid},source_path)
                            items.append({
                                "enchant_id":eid,"name":name,
                                "fixed_E":E,
                                "status":"EXACT_RUNTIME_NATIVE_WITNESSED"})
                        exact_runtime={
                            "status":"EXACT_V528_V530_V532_V533_USER_ONLY",
                            "items":items,"general_selectable":False,
                            "game_build":doc["game_build"],
                            "target_ilevel":334,
                            "installed_manifest_sha256":
                                doc["manifest_sha256"],
                            "scope":{"class":"hunter","spec":"survival",
                                     "race":"human",
                                     "finger1_item_id":268266,
                                     "trinket_ids":[270175,270173],
                                     "oil_hands":[],"special_items":[],
                                     "embellishments":[]}}
                except (exact_e0_enchant.SourceBlocked,
                        exact_positive_enchant.PositiveEnchantBlocked,
                        ui_catalog.CatalogBlocked,
                        environment_manifest.EnvironmentBlocked,
                        KeyError,ValueError,TypeError):
                    pass
            # v665: display-only same-effect family for an EXACT signed
            # installed 70961 ring E pair. No effect or budget approval.
            if exact and game_build=="12.1.5.70961":
                import v197_enchant_effect_families as ring_families
                signed={row["enchant_id"]:row for row in
                        registered.get("items",[])
                        if row.get("slot")=="finger1/finger2" and
                        type(row.get("verified_fixed_E")) is dict}
                for entry in published.get("enchant_candidates",{}).get("items",[]):
                    row=signed.get(entry.get("enchant_id"))
                    if (not row or row.get("simc_token")!=entry.get("token")
                        or not entry["token"].startswith("enchant_ring__")):
                        continue
                    family=ring_families.RING_EFFECTS.get(
                        entry["token"].split("__",1)[1])
                    if family is None or family[1] not in ("regular","stronger"):
                        continue
                    stat,rank=family
                    E=row["verified_fixed_E"]
                    if (type(E.get(stat)) is not int or E[stat]<=0 or
                        any(type(value) is not int or value!=0
                            for key,value in E.items() if key!=stat)):
                        continue
                    entry["effect_family"]=stat
                    entry["preferred_if_same_effect_source"]=(
                        "STRONGER_VARIANT_REPORTED" if rank=="stronger"
                        else "WEAKER_VARIANT_REPORTED")
            # Exact installed v212 choices are one owner for web and
            # profile. The old uninstalled route remains source_default-only.
            optional=(_v680_public_installed_optional_choices(doc)
                      if option_source_verified else
                      {"schema":"v113_current_season_optional_consumables_v1",
                       **profile_stage.current_season_approved_optional_choices(),
                       "source_default_simc_token":"disabled",
                       "diamond_id":[0],"omnium_talents":["source_default"],
                       "installed_manifest_sha256":None,"items":[]})
            return {**published,
                    "installed_optional_consumable_choices":optional,
                    "verified_exact_user_enchant_runtime":exact_runtime,
                    **({"source_scope":"VERIFIED_INSTALLED_V212_OPTION_CATALOG",
                        "installed_manifest_sha256":installed_manifest_sha256}
                       if exact else {}),
                    "verified_installed_enchant_registrations":registered,
                    "verified_weapon_enhancements":{
                "dk_runeforges":choices,"weapon_oils":oil}}
        except (ui_catalog.CatalogBlocked, OSError, ValueError, KeyError,
                TypeError, AssertionError,
                environment_manifest.EnvironmentBlocked) as exc:
            return {"schema":ui_catalog.SCHEMA,
                    "status":"SOURCE_OPTION_CATALOG_UNAVAILABLE",
                    "detail_code":type(exc).__name__,
                    "proven_native_input_choices":{},
                    "enchant_candidates":{"total":0,"groups":{},
                                          "items":[],"selectable_count":0},
                    "native_calls_now":0,"new_approval_granted":False}

    @app.get("/api/v1/options")
    def options():
        # v108 SUPPORTED contains historical SimC-recognized tokens. These
        # are NOT current-season item/quality/selection approvals. The web
        # product always requests current_season_product=True. Its normal
        # v216/v113 Build binds no optional food/potion/augmentation, so only
        # source_default (resolved to disabled by v218) is newly selectable.
        # Keep the legacy token catalogue for existing saved-session display,
        # without silently converting it into a new season registration.
        approved_optional=profile_stage.current_season_approved_optional_choices()
        return {
            "current_season_product_choices":{
                "schema":"v113_current_season_optional_consumables_v1",
                "status":"NONDEFAULT_UNADMITTED_UNTIL_VERIFIED_SEASON_BINDING",
                **approved_optional,
                # Current v218 admits no new historical diamond or Folio rows.
                "diamond_id":[0],"omnium_talents":["source_default"],
                "source_default_simc_token":"disabled",
                "nondefault_user_selectable":False},
            "food":["source_default",*sorted(consumables.SUPPORTED["food"])],
            "potion":["source_default",*sorted(consumables.SUPPORTED["potion"])],
            "augmentation":["source_default",*sorted(consumables.SUPPORTED["augmentation"])],
            "diamond_id":[0,*sorted(consumables.DIAMONDS)],
            "omnium_talents":["source_default",*sorted(consumables.OMNIUM_PRESETS)],
            "display_labels":choice_labels.labels(),
            "embellishments":choice_labels.public_embellishments()
        }



    @app.get("/api/v1/environment/official-game-terms")
    def official_game_terms(game_build: str | None = None):
        """Read-only validated Blizzard ko_KR playable labels, no network."""
        if game_build is not None and (
            re.fullmatch(r"\d+(?:\.\d+){3}",game_build) is None):
            raise HTTPException(422,detail={"code":"GAME_BUILD_FORMAT_INVALID"})
        build=game_build or jobs._current_fresh_game_build
        if build is None:
            return {"schema":official_playable_terms.SCHEMA,
                    "status":"SEASON_BUILD_NOT_SELECTED",
                    "names":{"class":{},"spec":{},"race":{}},
                    "native_calls_now":0,"network_calls_now":0}
        return official_playable_terms.public(jobs.root,build)

    @app.get("/api/v1/environment/official-ko-localization")
    def official_ko_localization_status(game_build: str | None = None):
        """Read-only verified Korean label cache; no network or new Native."""
        import re as _re
        if game_build is not None and (
            _re.fullmatch(r"\d+(?:\.\d+){3}",game_build) is None):
            raise HTTPException(422,detail={"code":"GAME_BUILD_FORMAT_INVALID"})
        build=game_build or jobs._current_fresh_game_build
        if not build:
            return {"schema":official_ko_env.SCHEMA,
                    "status":"SEASON_BUILD_NOT_SELECTED",
                    "native_calls_now":0,"network_calls_now":0}
        return official_ko_env.cache_status(jobs.root,build)

    @app.get("/api/v1/environment/installed-budget")
    def exact_installed_budget(game_build: str,
                               target_ilevel: int,
                               installed_manifest_sha256: str,
                               selected_flask_item_id: int,
                               reference_G_track: str = "general"):
        """User-selected exact installed source only. No Native or rebuild."""
        if (re.fullmatch(r"\d+(?:\.\d+){3}",game_build) is None or
                not 1<=target_ilevel<=1000 or
                re.fullmatch(r"[a-f0-9]{64}",
                             installed_manifest_sha256) is None or
                not 1<=selected_flask_item_id<=999999999 or
                reference_G_track not in ("general","fury_dual_2h")):
            raise HTTPException(422,detail={
                "code":"EXISTING_INSTALLED_BUDGET_SCOPE_INVALID",
                "check":"SCOPE_INPUT"})
        failure_stage=[]
        try:
            report=_v677_verified_existing_budget(
                jobs,game_build=game_build,target_ilevel=target_ilevel,
                installed_manifest_sha256=installed_manifest_sha256,
                selected_flask_item_id=selected_flask_item_id,
                required_reference_G_track=reference_G_track,
                failure_stage=failure_stage)
        except (OSError,ValueError,TypeError,KeyError,
                stage_engine.StageExecutionBlocked,
                environment_manifest.EnvironmentBlocked):
            report=None
        if report is None:
            raise HTTPException(409,detail={
                "code":"EXISTING_INSTALLED_BUDGET_SOURCE_NOT_VERIFIED",
                "check":failure_stage[0] if failure_stage else "UNCLASSIFIED_ORIGINAL"})
        return report

    @app.get("/api/v1/season-gear")
    def current_season_gear(game_build: str | None = None,
                            target_ilevel: int = 334,
                            installed_manifest_sha256: str | None = None):
        """Read-only source-bound candidate choices, never item approval."""
        return _current_season_gear(game_build,target_ilevel,installed_manifest_sha256,
                                    include_refresh=True)

    def _annotate_current_trinket_roles(base,root,build):
        # Read-only optional metadata; failure must not hide any choices.
        try:
            import v737_trinket_loot_spec_source as roles
            role_sources=roles.read_sources(root,build)
            if role_sources is not None:
                roles.annotate_trinkets(base["choices"]["trinket"],build,role_sources)
        except (OSError,ValueError,TypeError,KeyError):
            pass
        return base

    def _current_season_gear(game_build,target_ilevel,installed_manifest_sha256,
                             *,include_refresh):
        if game_build is not None or installed_manifest_sha256 is not None:
            if (type(game_build) is not str or
                    re.fullmatch(r"\d+(?:\.\d+){3}",game_build) is None or
                    type(installed_manifest_sha256) is not str or
                    re.fullmatch(r"[a-f0-9]{64}",
                                 installed_manifest_sha256) is None or
                    not 1<=target_ilevel<=1000):
                raise HTTPException(422,detail={
                    "code":"SEASON_GEAR_EXACT_INSTALLED_SCOPE_REQUIRED"})
            empty={"schema":season_gear.SCHEMA,
                   "status":"SEASON_GEAR_INSTALLED_SOURCE_UNAVAILABLE",
                   "season_build":game_build,
                   "source_scope":"EXACT_INSTALLED_V212_REQUIRED",
                   "choices":{k:[] for k in ("trinket",
                     "special_effect_gear_candidate","selectable_stat_craft")},
                   "count":0,"native_calls_now":0,
                   "ordinary_equipment_user_selectable":False,
                   "full_season_completeness_confirmed":False}
            try:
                docs=(jobs.root/"_fresh_season_sources"/
                      ("wago_"+game_build)/"fresh_source")
                receipt=docs/("v212_installed_"+
                              installed_manifest_sha256[:20]+".json")
                if (docs.is_symlink() or receipt.is_symlink() or
                        not receipt.is_file()):
                    return empty
                installed,_=environment_manifest.read_json(
                    receipt,environment_build.MAX_RECEIPT_BYTES)
                environment_manifest.verify_fresh_installed_environment(
                    installed)
                if (installed["manifest_sha256"]!=installed_manifest_sha256 or
                    installed["game_build"]!=game_build or
                    installed["target_ilevel"]!=target_ilevel):
                    return empty
                physical=installed.get("official_O_physical_source")
                oils=(physical.get("selected_oil_item_ids_by_hand")
                      if type(physical) is dict else {})
                matched=environment_build.find_verified_installed_season_environment(
                    jobs.root,target_ilevel,expected_game_build=game_build,
                    selected_oil_item_ids_by_hand=oils,
                    expected_installed_manifest_sha256=installed_manifest_sha256)
                if (matched is None or
                    matched["installed_manifest_sha256"]!=installed_manifest_sha256):
                    return empty
                source_path=docs/"v213_candidate_catalog.json"
                if source_path.is_symlink() or not source_path.is_file():
                    return empty
                source,raw_sha=environment_manifest.read_json(source_path)
                source_to_catalog.verify_catalog(source)
                if (raw_sha!=installed["source_catalog_artifact_sha256"] or
                    source["manifest_sha256"]!=
                        installed["source_catalog_manifest_sha256"] or
                    source["game_build"]!=game_build):
                    return empty
                groups=source["catalog"]["gear"]["slot_groups"]
                ids={item["item_id"] for rows in groups.values()
                     for item in rows if item.get("category") in (
                         "trinket","special_effect_gear_candidate",
                         "selectable_stat_craft")}
                names=official_ko_env.read_names(jobs.root,game_build,ids)
                base=season_gear.public_installed_v213_candidates(
                    source,installed_manifest_sha256=installed_manifest_sha256,
                    official_names=names)
                # Gear source selection is also a specific G budget track.
                # This is the already verified v212 receipt, not a new read.
                base["reference_G_track"]=installed.get(
                    "official_G_reference_track","general")
                if not include_refresh:return base
                # Restore verified source-only selectable additions on GET,
                # including after server restart. Never mutate v213/v212.
                # A missing or ambiguous derived source leaves base intact.
                try:
                    with jobs.season_source_lock:
                        refreshed=jobs.season_gear_refresh_cache.get(game_build)
                        if refreshed is None:
                            refreshed=environment_build.read_sealed_selectable_gear_generation(
                                stage_root=docs.parent,build=game_build)
                            if refreshed is not None:
                                refreshed={**refreshed,"special_generation_verified":True,
                                           "explicit_refresh_complete":False}
                                jobs.season_gear_refresh_cache[game_build]=refreshed
                    if refreshed is None:return _annotate_current_trinket_roles(base,docs.parent,game_build)
                    candidate=refreshed["candidate"]
                    if candidate.get("season_build")!=game_build:return _annotate_current_trinket_roles(base,docs.parent,game_build)
                    old_ids={r["item_id"] for rows in groups.values() for r in rows}
                    additions={r["item_id"] for r in candidate["items"]
                        if r["category"]=="trinket" and r["item_id"] not in old_ids}
                    old_special_ids={r["item_id"] for r in base["choices"]["special_effect_gear_candidate"]}
                    special_ids=_refreshed_special_ids(refreshed,old_ids,
                        existing_special_ids=old_special_ids)
                    new_names=official_ko_env.read_names(jobs.root,game_build,
                                                         additions|special_ids)
                    rows=season_gear.public_options(candidate,official_names=new_names)["choices"]
                    for role,ids,count_key in (
                        ("trinket",additions,"refreshed_trinket_count"),
                        ("special_effect_gear_candidate",special_ids,"refreshed_special_count")):
                        new=[r for r in rows[role] if r["item_id"] in ids]
                        base["choices"][role]=sorted(
                            base["choices"][role]+new,
                            key=lambda r:(r["name"].casefold(),r["item_id"]))
                        base["count"]+=len(new)
                        base[count_key]=len(new)
                        base["verified_ko_item_names"]+=sum("name_ko" in r for r in new)
                    base["source_generation_sha256"]=refreshed["source_generation_sha256"]
                except (OSError,ValueError,TypeError,KeyError):
                    pass
                return _annotate_current_trinket_roles(base,docs.parent,game_build)
            except (OSError,ValueError,KeyError,TypeError):
                return empty
        # Historical browsing fallback only. It is NOT an installed v212
        # environment and is never used when an installed SHA was supplied.
        try:
            catalog=season_gear.read()
            ids={row["item_id"] for row in catalog["items"]
                 if row["category"] in ("trinket",
                      "special_effect_gear_candidate","selectable_stat_craft")}
            names=official_ko_env.read_names(
                jobs.root,catalog["season_build"],ids)
            return season_gear.public_options(catalog,
                                              official_names=names)
        except (season_gear.GearBlocked, ValueError, OSError, KeyError):
            return {"schema":season_gear.SCHEMA,
                    "status":"SEASON_GEAR_CATALOG_UNAVAILABLE",
                    "choices":{k:[] for k in ("trinket","special_effect_gear_candidate","selectable_stat_craft")},
                    "count":0,"manual_exact_id_allowed":False,
                    "manual_exact_id_exception":"CRAFTED_EQUIPMENT_VARIANTS_ONLY",
                    "ordinary_equipment_user_selectable":False,
                    "full_season_completeness_confirmed":False,
                    "native_calls_now":0}

    def _refreshed_special_ids(refreshed,old_ids,*,existing_special_ids=None):
        if not refreshed.get("special_generation_verified"):return set()
        candidate=refreshed["candidate"]
        return {r["item_id"] for r in candidate["items"]
                if (r["item_id"] not in old_ids or
                    (existing_special_ids is not None and r["item_id"] not in existing_special_ids and
                     r.get("season_list_basis")=="SEALED_CONTEXT_FREE_EFFECT_OPTION")) and
                bootstrap.refreshed_special_source_eligible(
                    r,candidate.get("db2_display_season_id"))}

    @app.post("/api/v1/season-gear/refresh")
    def refresh_installed_season_gear(game_build: str,target_ilevel: int,
                                      installed_manifest_sha256: str):
        """Refresh choices without re-installing the verified numeric scope.

        Trinkets use the existing exact-ID profile path. Special choices
        require the same unique sealed generation used by v098's selected
        source connection; no provisional crafted/bonus-only promotion.
        """
        base=_current_season_gear(game_build,target_ilevel,installed_manifest_sha256,
                                  include_refresh=False)
        result={"schema":"season_selectable_gear_refresh_v1",
                "status":"SEASON_SELECTABLE_GEAR_REFRESH_PENDING",
                "season_build":game_build,"target_ilevel":target_ilevel,
                "installed_manifest_sha256":installed_manifest_sha256,
                "source_catalog_manifest_sha256":base.get("source_catalog_manifest_sha256"),
                "new_trinkets":[],"new_special_items":[],"new_special_pending_count":None,
                "native_calls_now":0,"network_calls_now":0,
                "budget_rebuilt":False,"full_season_completeness_confirmed":False}
        if (base.get("source_scope")!="VERIFIED_INSTALLED_V212_SOURCE_V213_CANDIDATES"
            or base.get("installed_manifest_sha256")!=installed_manifest_sha256):
            return result
        try:
            with jobs.season_source_lock:
                refreshed=jobs.season_gear_refresh_cache.get(game_build)
                # GET restoration and a completed explicit refresh are
                # different: the former need not have attempted bonus raw,
                # and an optional source failure must be retryable.
                if (refreshed is None or not refreshed.get("explicit_refresh_complete") or
                        refreshed.get("bonus_effect_review",{}).get("status")!=
                            "POTENTIAL_BONUS_EFFECT_LINKS_OBSERVED"):
                    root=jobs.root/"_fresh_season_sources"/("wago_"+game_build)
                    refreshed=environment_build.refresh_existing_season_gear_source(
                        stage_root=root,build=game_build)
                    # Confirm the same unambiguous generation v098 will
                    # resolve on selection. Only small sealed files, not
                    # another raw acquisition or numeric environment Build.
                    sealed=None
                    if any(bootstrap.refreshed_special_source_eligible(
                            r,refreshed["candidate"].get("db2_display_season_id"))
                           for r in refreshed["candidate"]["items"]):
                        sealed=environment_build.read_sealed_selectable_gear_generation(
                            stage_root=root,build=game_build)
                    refreshed={**refreshed,"special_generation_verified":(
                        sealed is not None and
                        sealed["source_generation_sha256"]==refreshed["source_generation_sha256"])}
                    # Display can reuse a partial result, but an explicit
                    # refresh must retry failed optional acquisition. The
                    # raw owner already reuses successful same-build bytes.
                    jobs.season_gear_refresh_cache.pop(game_build,None)
                    if (refreshed.get("supplementary_delve_status") in (
                            "SUPPLEMENTARY_SOURCE_OBSERVED",
                            "SUPPLEMENTARY_SOURCE_PARTIAL") and
                            refreshed.get("bonus_effect_review",{}).get("status")==
                                "POTENTIAL_BONUS_EFFECT_LINKS_OBSERVED"):
                        jobs.season_gear_refresh_cache[game_build]={
                            **refreshed,"network_calls":0,"explicit_refresh_complete":True}
                # Independent optional retry: do not repeat gear refresh
                # merely because loot-spec metadata is missing.
                role_review=environment_build.refresh_trinket_loot_spec_sources(
                    stage_root=jobs.root/"_fresh_season_sources"/("wago_"+game_build),
                    build=game_build)
            result["network_calls_now"]=refreshed["network_calls"]+role_review["network_calls_by_stage"]
            result["loot_spec_source_status"]=role_review["status"]
            source=refreshed["candidate"]
            prior_ids={r["item_id"] for rows in base["choices"].values() for r in rows}
            new_ids={r["item_id"] for r in source["items"]
                     if r["category"]=="trinket" and r["item_id"] not in prior_ids}
            special_ids=_refreshed_special_ids(refreshed,prior_ids,
                existing_special_ids={r["item_id"] for r in base["choices"]["special_effect_gear_candidate"]})
            names=official_ko_env.read_names(jobs.root,game_build,new_ids|special_ids)
            rows=season_gear.public_options(source,official_names=names)["choices"]
            # Metadata may change even when no new equipment is admitted.
            # Project once over the union of the installed and new IDs.
            if role_review["status"]=="TRINKET_LOOT_SPEC_SOURCE_OBSERVED":
                union=base["choices"]["trinket"]+[
                    r for r in rows["trinket"] if r["item_id"] in new_ids]
                enriched=_annotate_current_trinket_roles(
                    {"choices":{"trinket":union}},
                    jobs.root/"_fresh_season_sources"/("wago_"+game_build),game_build)
                metadata={str(r["item_id"]):r["loot_spec_metadata"]
                    for r in enriched["choices"]["trinket"] if "loot_spec_metadata" in r}
                if metadata:result["trinket_loot_spec_metadata"]=metadata
                else:result["loot_spec_source_status"]="TRINKET_LOOT_SPEC_SOURCE_PENDING"
            result.update(status="SEASON_TRINKET_SOURCE_REFRESHED",
                source_generation_sha256=refreshed["source_generation_sha256"],
                supplementary_delve_status=refreshed["supplementary_delve_status"],
                supplementary_delve_unresolved_count=refreshed.get(
                    "supplementary_delve_unresolved_count"),
                new_trinkets=[r for r in rows["trinket"] if r["item_id"] in new_ids],
                mplus_trinket_coverage=refreshed.get("mplus_trinket_coverage"),
                new_special_items=[r for r in rows["special_effect_gear_candidate"]
                                   if r["item_id"] in special_ids],
                new_special_pending_count=sum(r["item_id"] not in prior_ids|special_ids
                    for r in rows["special_effect_gear_candidate"]))
        except (stage_engine.StageExecutionBlocked,environment_build.EnvironmentBuildBlocked,
                OSError,ValueError,TypeError,KeyError) as exc:
            # Optional choices are not a numeric environment requirement.
            # Export only stable internal codes, never local paths or data.
            code=str(exc)
            if isinstance(exc,(stage_engine.StageExecutionBlocked,
                               environment_build.EnvironmentBuildBlocked)) and re.fullmatch(
                    r"[A-Z][A-Z0-9_]{0,119}(?::[A-Z][A-Z0-9_]{0,119})?",code):
                result["reason"]=code
            else:
                result["reason"]="SEASON_GEAR_REFRESH_SOURCE_UNAVAILABLE"
        return result

    @app.get("/api/v1/season-item-icons")
    def installed_season_item_icons(game_build: str,
                                    target_ilevel: int,
                                    installed_manifest_sha256: str):
        """Display-only official media for exact installed candidate IDs.

        This endpoint uses an already verified season/gear scope and local
        Windows credentials. No newly submitted arbitrary item IDs, no Native,
        no DB mutation, no season admission or source cache invalidation.
        """
        if (re.fullmatch(r"\d+(?:\.\d+){3}",game_build) is None or
                not 1<=target_ilevel<=1000 or
                re.fullmatch(r"[a-f0-9]{64}",
                             installed_manifest_sha256) is None):
            raise HTTPException(422,detail={
                "code":"ITEM_ICONS_VERIFIED_SEASON_SCOPE_REQUIRED"})
        gear=current_season_gear(game_build,target_ilevel,
                                 installed_manifest_sha256)
        if (gear.get("status")!="CURRENT_SEASON_CANDIDATE_SELECTION_ONLY" or
            gear.get("source_scope")!=
                "VERIFIED_INSTALLED_V212_SOURCE_V213_CANDIDATES" or
            gear.get("installed_manifest_sha256")!=installed_manifest_sha256):
            return {"schema":official_item_icons.SCHEMA,
                    "status":"VERIFIED_SEASON_GEAR_UNAVAILABLE",
                    "icons":{},"requested":0,"network_calls_now":0,
                    "native_calls":0,"display_only":True}
        visible=gear.get("choices") or {}
        ids=sorted({x["item_id"] for kind in
                    ("trinket","special_effect_gear_candidate")
                    for x in visible.get(kind,[])
                    if type(x) is dict and type(x.get("item_id")) is int})
        if not ids or len(ids)>official_item_icons.MAX_ITEMS:
            return {"schema":official_item_icons.SCHEMA,
                    "status":"MEDIA_SOURCE_SIZE_OUT_OF_SCOPE",
                    "icons":{},"requested":len(ids),"network_calls_now":0,
                    "native_calls":0,"display_only":True}
        scope=(game_build,target_ilevel,installed_manifest_sha256)
        with jobs.equipment_icon_lock:
            if scope in jobs.equipment_icon_cache:
                doc=jobs.equipment_icon_cache[scope]
                return {**doc,"network_calls_now":0,
                        "localization_network_calls_now":0,"cached":True}
            try:
                credentials=jobs.source_credential_store.load()
            except (local_source_keys.CredentialBlocked,OSError):
                credentials=None
            doc=official_item_icons.collect(ids,credentials)
            # This existing optional presentation request is already scoped
            # to the verified installed gear list. Complete missing Korean
            # labels here using v335's same-build cache, not a new Build.
            # The exact /season-gear and /installed-budget GETs remain
            # strictly local, and name failures never block gear/SimC.
            names=official_ko_env.read_names(jobs.root,game_build,ids)
            if len(names)<len(ids) and credentials:
                try:
                    with jobs.locale_cache_lock:
                        localization=official_ko_env.build_for_environment(
                            jobs.root,game_build,{
                                "environment_ready":True,
                                "environment_installed":True,
                                "installed_manifest_sha256":installed_manifest_sha256},
                            target_ilevel=target_ilevel,credentials=credentials)
                        names=official_ko_env.read_names(jobs.root,game_build,ids)
                    doc={**doc,"localization_network_calls_now":
                         localization.get("network_calls_now",0)}
                except (official_ko_env.LocalizationBlocked,OSError,ValueError,
                        TypeError,KeyError):
                    pass
            doc={**doc,"names_ko":{str(i):name for i,name in names.items()},
                 "localization_network_calls_now":
                     doc.get("localization_network_calls_now",0)}
            if doc["status"] in ("COMPLETE","PARTIAL"):
                jobs.equipment_icon_cache[scope]=doc
            return {**doc,"cached":False}

    @app.get("/api/v1/native-batches")
    def native_batches():
        return {"schema":batch_view.SCHEMA,
                "batches":batch_view.find_batches(snapshots),
                "native_calls_now":0,
                "mode":"LOCAL_COPIED_REPORT_READ_ONLY"}

    @app.get("/api/v1/native-batches/{batch_id}/results")
    def native_batch_results(batch_id: str):
        try:
            return batch_view.view_batch(snapshots,batch_id)
        except batch_view.BatchViewBlocked as exc:
            # Do not return original path, source profile or raw SimC JSON.
            raise HTTPException(422,detail={"code":str(exc).split(":",1)[0]}) from None

    @app.get("/api/v1/sessions")
    def recent_sessions():
        return jobs.recent_sessions()

    @app.get("/api/v1/health")
    def health():
        return {"schema":SCHEMA,"mode":"LOCAL_ONLY",
                "native_called_by_health":False,"supported_dps":len(sessions.SUPPORTED)}

    @app.get("/api/v1/bootstrap")
    def browser_bootstrap():
        return {"schema":SCHEMA,"session_token":key,
                "supported":[{"class":cl,"spec":spec}
                             for cl,spec in sessions.SUPPORTED],
                "local_only":True}

    @app.get("/api/v1/defaults")
    def defaults():
        # Compact v146 starters and season representative catalog now serve
        # all 26 DPS without legacy complete source .simc fixtures.
        # A plan for the 24 new cases selects the independent path only at
        # target334; non-334 retains a separate historical source-backed route.
        archetypes=[]
        for pair in sessions.SUPPORTED:
            controls=sessions.standard_controls(pair)
            # The default season environment installs no weapon oil (O=0).
            # The browser must not silently request the legacy main-hand oil.
            # User-selected oil remains explicit and source-bound at prepare.
            controls["oil_hands"]=[]
            scope=("SOURCE_INDEPENDENT_SEASON_CATALOG"
                   if pair in bootstrap.PURE_PRODUCT_SPECS else
                   "SOURCE_INDEPENDENT_TARGET334_VALIDATED_BATCH")
            archetypes.append({"class":pair[0],"spec":pair[1],**controls,
                               "representative_scope":scope})
        # Metadata is not part of reusable /plan user controls.
        known_races={"/".join(pair):list(info["allowed_races"])
                     for pair in sessions.SUPPORTED
                     if (info:=bootstrap.pure.contracts.lookup(*pair)) is not None
                     and info["allowed_races"] is not None}
        return {"archetypes":archetypes,
                "allowed_races_by_spec":known_races,
                "unavailable_missing_legacy_fixtures":[]}

    @app.get("/api/v1/simc-connection/status")
    def simc_connection_status():
        try:
            return simc_prefs.status()
        except simc_connection.SimCConnectionBlocked as exc:
            raise HTTPException(422,detail={"code":str(exc)}) from None

    @app.post("/api/v1/simc-connection/confirm")
    def simc_connection_confirm(request: SimCConnectionConfirmRequest):
        # Explicit user click only. A tiny display_build=2 CLI call is not DPS.
        if any(jobs.is_active(jobs.root/sid) for sid in tuple(jobs.children)):
            raise HTTPException(409,detail={
                "code":"ACTIVE_SIMC_JOB_CONNECTION_CHECK_BLOCKED"})
        try:
            return simc_prefs.confirm(
                binary=request.binary,revision=request.revision,
                static_cache=request.static_cache,managed=updater.status())
        except simc_connection.SimCConnectionBlocked as exc:
            raise HTTPException(422,detail={"code":str(exc)}) from None

    @app.get("/api/v1/source-credentials/status")
    def source_credentials_status():
        """No identifiers, secret values, credential path, or external IO."""
        try:
            return jobs.source_credential_store.status()
        except local_source_keys.CredentialBlocked as exc:
            raise blocked(exc) from None

    @app.post("/api/v1/source-credentials/save")
    def source_credentials_save(request: LocalSourceCredentialsRequest):
        """User opt-in. Windows Credential Manager only; no secret echo."""
        try:
            values={
                "BLIZZARD_CLIENT_ID":request.blizzard_client_id,
                "BLIZZARD_CLIENT_SECRET":request.blizzard_client_secret,
                "WCL_CLIENT_ID":request.wcl_client_id,
                "WCL_CLIENT_SECRET":request.wcl_client_secret}
            return jobs.source_credential_store.save(values)
        except local_source_keys.CredentialBlocked as exc:
            raise blocked(exc) from None

    @app.post("/api/v1/source-credentials/clear")
    def source_credentials_clear():
        """User-requested clear; no season/candidate/session cache deletion."""
        try:
            return jobs.source_credential_store.clear()
        except local_source_keys.CredentialBlocked as exc:
            raise blocked(exc) from None

    @app.post("/api/v1/environment/myth-target")
    def season_myth_target(request: SeasonMythTargetRequest):
        # This never invokes the adaptive optimizer or a SimC binary.
        return jobs.discover_season_myth_target(request.game_build)

    @app.post("/api/v1/environment/season-build")
    def season_environment_build(request: SeasonEnvironmentBuildRequest):
        """Web-app Environment Build only: no DPS inputs or optimizer."""
        try:
            result=jobs.build_season_environment(
                request.game_build,request.target_ilevel,
                native_G_binary=request.native_G_binary,
                consumable_native_binary=request.consumable_native_binary,
                simc_revision_hint=request.simc_revision_hint,
                auto_native_F_requested=request.auto_native_F_requested,
                auto_native_O_requested=request.auto_native_O_requested,
                selected_flask_item_id=request.selected_flask_item_id,
                selected_oil_item_ids_by_hand=
                    request.selected_oil_item_ids_by_hand,
                auto_select_observed_F_no_oil=
                    request.auto_select_observed_F_no_oil,
                auto_initial_core_build=request.auto_initial_core_build,
                auto_initial_core_simc_binary=
                    request.auto_initial_core_simc_binary,
                reference_G_track=request.reference_G_track,
                existing_special_gem_id=request.existing_special_gem_id,
                source_target_socket_count=request.source_target_socket_count,
                refresh_reason=request.refresh_reason,
                **({"auto_myth_target_source_build":
                        request.auto_myth_target_source_build}
                   if request.auto_myth_target_source_build is not None else {}),
                **({"auto_myth_target_source_sha256":
                        request.auto_myth_target_source_sha256}
                   if request.auto_myth_target_source_sha256 is not None else {}))
            # An audit field only: the M1 currency cap is NOT evidence for
            # G/J/F/O, B/T or v212. Leave source owner admission unchanged.
            if request.auto_myth_target_source_sha256 is not None:
                scope=result.get("web_environment_scope")
                if type(scope) is dict:
                    result={**result,"web_environment_scope":{
                        **scope,"auto_myth_target_source_csv_sha256":
                        request.auto_myth_target_source_sha256,
                        "auto_myth_target_source_sha_verified":True}}
            return result
        except Exception as exc:
            raise blocked(exc,stage="SEASON_ENVIRONMENT_BUILD") from None

    @app.post("/api/v1/environment/build")
    def build_environment(request: UserRequest):
        # Backward compatible installed-season plan. The separate seasonal
        # Environment Build UI uses /environment/season-build.
        # New season source collection is not an installed current-season plan.
        if request.fresh_season_build is not None:
            try:
                return jobs.collect_fresh_source(
                    request.fresh_season_build,request.controls,
                    request.revision,
                    **({"measure_fury_G_source_only":True,
                        "binary":request.binary}
                       if request.measure_fury_G_source_only else {}))
            except Exception as exc:
                raise blocked(exc) from None
        if request.measure_fury_G_source_only:
            raise HTTPException(422,detail={
                "code":"FURY_G_SOURCE_PROBE_REQUIRES_FRESH_SEASON_BUILD"})
        if not request.current_season_product:
            raise HTTPException(422,detail={"code":"ENVIRONMENT_BUILD_CURRENT_SEASON_ONLY"})
        return jobs.plan(request)

    @app.get("/api/v1/environment/{session_id}")
    def environment_status(session_id: str):
        folder=jobs.folder(session_id)
        return {"session_id":session_id,
                "environment_manifest":jobs._read_environment_summary(folder),
                "environment_build":jobs._read_environment_build_summary(folder),
                "native_calls":0,"network_calls":0}

    @app.post("/api/v1/longrun/prepare")
    def longrun_prepare(request: LongRunStartRequest):
        return jobs.longrun_prepare(request)

    @app.post("/api/v1/longrun/start")
    def longrun_start(request: LongRunStartRequest):
        return jobs.longrun_start(request)

    @app.post("/api/v1/sessions/{session_id}/longrun/resume")
    def longrun_resume(session_id: str, request: LongRunBatchRequest):
        return jobs.longrun_launch(
            jobs.folder(session_id),
            batch=request.max_new_native_this_invocation,
            elapsed=request.max_elapsed_seconds,continuous=request.continuous)

    @app.post("/api/v1/sessions/{session_id}/longrun/cache-only")
    def longrun_cache_only(session_id: str):
        return jobs.longrun_launch(jobs.folder(session_id),
                                   batch=0,cache_only=True)

    @app.post("/api/v1/sessions/{session_id}/longrun/import")
    def longrun_import(session_id: str, request: LongRunImportRequest):
        return jobs.longrun_launch(
            jobs.folder(session_id),batch=0,cache_only=True,
            archive=request.archive_path,sha=request.archive_sha256,
            elapsed=request.max_elapsed_seconds)

    @app.post("/api/v1/sessions/{session_id}/longrun/cancel")
    def longrun_cancel(session_id: str):
        return jobs.longrun_cancel(jobs.folder(session_id))

    @app.get("/api/v1/sessions/{session_id}/longrun/status")
    def longrun_status(session_id: str):
        return jobs.longrun_status(jobs.folder(session_id))

    @app.get("/api/v1/sessions/{session_id}/longrun/result")
    def longrun_result(session_id: str):
        return jobs.longrun_result(jobs.folder(session_id))

    @app.post("/api/v1/sessions/plan")
    def plan(request: UserRequest):
        if request.fresh_season_build is not None:
            raise HTTPException(422,detail={"code":"FRESH_SOURCE_NOT_INSTALLED"})
        return jobs.plan(request)

    @app.post("/api/v1/sessions/start")
    def start(request: UserRequest):
        if request.fresh_season_build is not None:
            raise HTTPException(422,detail={"code":"FRESH_SOURCE_NOT_INSTALLED"})
        return jobs.start_with_internal_special_L(request)

    @app.post("/api/v1/sessions/{session_id}/resume")
    def resume(session_id: str):
        return jobs.launch(jobs.folder(session_id))

    @app.post("/api/v1/sessions/{session_id}/cache-only")
    def cache_only(session_id: str):
        return jobs.launch(jobs.folder(session_id),cache_only=True)

    @app.post("/api/v1/sessions/{session_id}/cancel")
    def cancel(session_id: str):
        return jobs.cancel(jobs.folder(session_id))

    @app.get("/api/v1/sessions/{session_id}/status")
    def status(session_id: str):
        return jobs.status(jobs.folder(session_id))

    @app.get("/api/v1/sessions/{session_id}/inputs")
    def inputs(session_id: str):
        return jobs.inputs(jobs.folder(session_id))

    @app.get("/api/v1/sessions/{session_id}/result")
    def result(session_id: str):
        return jobs.result(jobs.folder(session_id))
    return app

def main(argv=None):
    import argparse
    p=argparse.ArgumentParser(description="P1-WEB-2 local HTML webapp with existing SimC engine")
    p.add_argument("--host",default=LOCAL_HOST,choices=[LOCAL_HOST])
    p.add_argument("--port",type=int,default=8765)
    p.add_argument("--batch-root",type=pathlib.Path,
                   help="Optional relocated v147_batch directory; read-only Native results, never cache relocation")
    p.add_argument("--open-browser",action="store_true",
                   help="Open local browser only after this own Uvicorn server starts")
    args=p.parse_args(argv)
    if not 1024<=args.port<=65535:
        p.error("PORT_MUST_BE_1024_TO_65535")
    import uvicorn
    url=f"http://{LOCAL_HOST}:{args.port}/"
    print("SIMC_LOCAL_WEB "+url,flush=True)
    app=create_app(batch_root=args.batch_root)
    if not args.open_browser:
        # Preserve original CLI behavior, sockets and Native/session inputs.
        uvicorn.run(app,host=LOCAL_HOST,port=args.port,
                    proxy_headers=False,access_log=False)
        return
    # Check THIS server's started flag; never open a different process's
    # occupant of port 8765 if our bind fails. No network or Native checks.
    import time
    import webbrowser
    server=uvicorn.Server(uvicorn.Config(
        app,host=LOCAL_HOST,port=args.port,
        proxy_headers=False,access_log=False))
    def open_when_started():
        for _ in range(150):
            if server.started:
                webbrowser.open(url,new=2)
                return
            if server.should_exit:
                return
            time.sleep(0.1)
    threading.Thread(target=open_when_started,daemon=True).start()
    server.run()

if __name__=="__main__":
    main()
