"""One real zero-history T1 attempt through the ORIGINAL v216 Build.

No fabricated items, installed season catalog, prior cache, user ItemIDs or
mocked collectors. Public Retail version is fetched at runtime; source HTTP
and the existing SimC Native path are allowed. A successful workflow means
the original v212 installed READY, not merely that a probe script ran.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import tempfile
import zipfile
from contextlib import contextmanager
from datetime import datetime,timezone

from runner import v216_environment_build_coordinator as engine
from runner import v289_retail_live_build_source as retail
from runner import v242_authenticated_season_source_stage as season_auth
from integration_probes import p3_fs_simc_image_revision as simc_image

OUT=pathlib.Path("p3_fr_zero_base_t1_receipt.json")


class ExactBinarySourcePending(ValueError):
    pass


NATIVE_EVIDENCE_ARCHIVE=pathlib.Path("p3_fr_zero_base_t1_native_evidence.zip")
MAX_NATIVE_CASES=16
MAX_NATIVE_FILE_BYTES=20_000_000
MAX_NATIVE_TOTAL_BYTES=64_000_000
NATIVE_CASE_PREFIXES=("v277_native_G_","v278_baseline_","v278_active_")
NATIVE_CASE_FILES=("receipt.json","input.simc","native.json","simc.log")


def archive_existing_native_attempts(root, destination):
    """Retain exact v277/v278 case bytes for later AUDIT, never zero-base input.

    The original v277/v278 owners still validate identity/cache reuse. In
    particular v278's input has an absolute JSON2 output path; this archive
    is not a portable cache, never an automatic source of budget approval.
    """
    root=pathlib.Path(root).resolve(strict=True)
    destination=pathlib.Path(destination)
    cases=[]
    for source in root.rglob("source"):
        if not source.is_dir() or source.is_symlink():
            continue
        for case in source.iterdir():
            if case.name.startswith(NATIVE_CASE_PREFIXES):
                if (case.is_symlink() or not case.is_dir() or
                        not case.resolve().is_relative_to(root)):
                    raise ValueError("P3_GJ_UNSAFE_NATIVE_CASE")
                cases.append(case)
    if len(cases)>MAX_NATIVE_CASES:
        raise ValueError("P3_GJ_NATIVE_CASE_LIMIT")
    if not cases:
        return {"status":"NO_NATIVE_CASES_TO_ARCHIVE","case_count":0,
                "new_native_calls":0,"portable_cache":False}
    if destination.exists() or destination.is_symlink():
        raise ValueError("P3_GJ_NATIVE_ARCHIVE_ALREADY_EXISTS")
    inventory=[]
    total=0
    count=0
    with zipfile.ZipFile(destination,"w",compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6) as archive:
        for case in sorted(cases):
            receipt_file=case/"receipt.json"
            receipt=None
            if receipt_file.exists():
                if (receipt_file.is_symlink() or not receipt_file.is_file() or
                        receipt_file.stat().st_size>200_000):
                    raise ValueError("P3_GJ_UNSAFE_NATIVE_RECEIPT")
                receipt=json.loads(receipt_file.read_text("utf8"))
                if type(receipt) is not dict:
                    raise ValueError("P3_GJ_NATIVE_RECEIPT_FORMAT")
            g_case=case.name.startswith("v277_native_G_")
            identity=receipt.get("identity",{}) if receipt else {}
            if type(identity) is not dict:
                raise ValueError("P3_GJ_NATIVE_RECEIPT_IDENTITY")
            expected={
                "input.simc":(identity.get("executed_input_sha256")
                              if g_case else receipt.get("input_sha256")
                              if receipt else None),
                "native.json":receipt.get("native_json2_sha256") if receipt else None,
                "simc.log":(receipt.get("native_log_sha256") if g_case
                            else receipt.get("log_sha256")) if receipt else None}
            copied=[]
            for filename in NATIVE_CASE_FILES:
                f=case/filename
                digest=expected.get(filename)
                if not f.exists():
                    if digest is not None:
                        raise ValueError("P3_GJ_RECEIPTED_NATIVE_FILE_MISSING")
                    continue
                if (f.is_symlink() or not f.is_file() or
                        f.stat().st_size>MAX_NATIVE_FILE_BYTES):
                    raise ValueError("P3_GJ_NATIVE_FILE_UNSAFE_OR_OVERSIZED")
                raw=f.read_bytes()
                total+=len(raw)
                if total>MAX_NATIVE_TOTAL_BYTES:
                    raise ValueError("P3_GJ_NATIVE_ARCHIVE_TOTAL_LIMIT")
                observed=hashlib.sha256(raw).hexdigest()
                if digest is not None and digest!=observed:
                    raise ValueError("P3_GJ_NATIVE_FILE_SHA_MISMATCH")
                relative=f.relative_to(root).as_posix()
                archive.writestr(relative,raw)
                copied.append({"path":relative,"sha256":observed,
                               "size_bytes":len(raw)})
                count+=1
            inventory.append({"case":case.relative_to(root).as_posix(),
                              "receipt_status":(receipt.get("status")
                                                if receipt else "INCOMPLETE"),
                              "files":copied})
        audit={"schema":"p3_gj_existing_native_case_audit_v1",
               "purpose":"read-only audit, NOT portable cache or product admission",
               "zero_history_inputs_reused":False,
               "case_count":len(cases),"file_count":count,
               "cases":inventory}
        archive.writestr("native_evidence_inventory.json",
                         json.dumps(audit,sort_keys=True,ensure_ascii=False,
                                    indent=2).encode("utf8"))
    sha=hashlib.sha256(destination.read_bytes()).hexdigest()
    return {"status":"EXISTING_NATIVE_CASE_BYTES_ARCHIVED_AUDIT_ONLY",
            "case_count":len(cases),"file_count":count,
            "archive_name":destination.name,"archive_sha256":sha,
            "portable_cache":False,"new_native_calls":0}


@contextmanager
def zero_base_workspace_with_native_audit(receipt):
    with tempfile.TemporaryDirectory(prefix="simc-zero-base-t1-") as root:
        try:
            yield root
        finally:
            try:
                receipt["native_evidence_archive"]=archive_existing_native_attempts(
                    root,NATIVE_EVIDENCE_ARCHIVE)
            except (ValueError,OSError,RuntimeError,zipfile.BadZipFile) as error:
                receipt["native_evidence_archive"]={
                    "status":"NATIVE_AUDIT_ARCHIVE_BLOCKED",
                    "error_type":type(error).__name__,
                    "error_code":str(error).split(":",1)[0][:120],
                    "portable_cache":False,"new_native_calls":0}


def verified_pinned_cli_source(*, binary_path, live_game_build, environment):
    """Check existing P3-FW executable before zero-history source/Native.

    GitHub workflow supplies P3-FW's exact upstream SHA, game build and
    binary SHA. These verify the test prerequisite only; not live season data.
    All checks are local; no Docker pull, SimC execution or network.
    """
    revision=environment.get("SIMC_PINNED_SOURCE_COMMIT") or ""
    if not revision:
        return None
    expected_build=environment.get("SIMC_PINNED_GAME_BUILD") or ""
    expected_sha=environment.get("SIMC_PINNED_BINARY_SHA256") or ""
    if re.fullmatch(r"[a-f0-9]{40}",revision) is None or (
            re.fullmatch(r"[a-f0-9]{64}",expected_sha) is None):
        raise ExactBinarySourcePending("P3_FZ_PINNED_SOURCE_IDENTITY_INVALID")
    if expected_build!=live_game_build:
        raise ExactBinarySourcePending("P3_FZ_CURRENT_RETAIL_BUILD_DIFFERS_FROM_PINNED_BINARY")
    path=pathlib.Path(binary_path)
    if path.is_symlink() or not path.is_file():
        raise ExactBinarySourcePending("P3_FZ_PINNED_BINARY_NOT_REGULAR_FILE")
    sha=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1_048_576),b""):
            sha.update(chunk)
    if sha.hexdigest()!=expected_sha:
        raise ExactBinarySourcePending("P3_FZ_PINNED_BINARY_SHA256_MISMATCH")
    return {
        "schema":"p3_fz_verified_existing_simc_binary_source_v1",
        "status":"EXISTING_P3_FW_CLI_SOURCE_AND_BYTES_ATTESTED",
        "revision_hint":revision,"source_revision":revision,
        "game_build":expected_build,
        "binary_sha256":expected_sha,
        "image_digest_checked":False,
        "environment_ready":False,
        "new_binary_compilations":0,
        "network_calls":0,"native_calls":0,
    }


def main():
    rec={
        "schema":"p3_fr_real_zero_history_t1_attempt_v1",
        "attempt_utc":datetime.now(timezone.utc).isoformat(),
        "status":"NOT_READY",
        "environment_ready":False,
        "environment_installed":False,
        "target_ilevel":334,
        "previous_item_ids":0,
        "user_selected_gem_ids":0,
        "user_selected_flask_id":None,
        "historical_source_cache_used":False,
        "previous_session_count":0,
        "simc_native_opt_in":False,
        "prerequisite_status":"NOT_CHECKED"}
    try:
        live=retail.discover(region="KR")
        rec["live_retail_version"]=live
        # These four existing v242 source credentials are required by the
        # present v163 raid/season join. Fail before a 100MB+ Wago download
        # when the runner has not received its configured secrets.
        missing=[key for key in season_auth.FIELDS
                 if not os.environ.get(key)]
        rec["missing_credential_names"]=missing  # never values
        if missing:
            rec["status"]="ZERO_BASE_T1_PREREQUISITES_MISSING"
            rec["prerequisite_status"]="AUTH_SEASON_SOURCE_INPUTS_MISSING"
            return 2
        binary=os.environ.get("SIMC_CLI_WRAPPER") or ""
        candidate=pathlib.Path(binary) if binary else None
        if candidate is not None and not candidate.is_file():
            raise RuntimeError("ZERO_BASE_SIMC_BINARY_NOT_AVAILABLE")
        rec["simc_native_opt_in"]=candidate is not None
        if candidate is None:
            rec["status"]="ZERO_BASE_T1_PREREQUISITES_MISSING"
            rec["prerequisite_status"]="SIMC_BINARY_NOT_SUPPLIED"
            return 2
        # The historical pinned SimC 70783 CLI was already built and has
        # a real binary SHA. Reuse it rather than building anew or pulling
        # an older Docker latest. This branch is diagnostic, not a bypass
        # of v229's exact newly collected generated-file source checks.
        try:
            pin=verified_pinned_cli_source(
                binary_path=candidate,live_game_build=live["game_build"],
                environment=os.environ)
        except ExactBinarySourcePending as exc:
            rec["status"]="ZERO_BASE_T1_PREREQUISITES_MISSING"
            rec["prerequisite_status"]=str(exc)
            return 2
        if pin is None:
            image_ref=os.environ.get("SIMC_IMAGE_REF") or ""
            if not image_ref:
                rec["status"]="ZERO_BASE_T1_PREREQUISITES_MISSING"
                rec["prerequisite_status"]="SIMC_BINARY_IMAGE_PIN_MISSING"
                return 2
            try:
                pin=simc_image.discover(
                    image_ref=image_ref,game_build=live["game_build"])
            except simc_image.SimCImageRevisionPending as exc:
                rec["status"]="ZERO_BASE_T1_PREREQUISITES_MISSING"
                rec["prerequisite_status"]=str(exc)
                return 2
            rec["simc_image_source_identity"]=pin
        rec["simc_source_identity"]=pin
        rec["prerequisite_status"]=(
            "EXACT_PINNED_BINARY_ATTESTED"
            if pin.get("status")=="EXISTING_P3_FW_CLI_SOURCE_AND_BYTES_ATTESTED"
            else "SOURCE_POINTERS_PRESENT_UNVERIFIED")
        # No prior files and no sealed source supplied to the program.
        with zero_base_workspace_with_native_audit(rec) as temp:
            root=pathlib.Path(temp)
            assert not list(root.iterdir())
            inputs={
                "expected_game_build":live["game_build"],
                "representative_request":{
                    "class":"paladin","spec":"retribution",
                    "target_ilevel":334},
                "g_probe_character":{"race":"dwarf"},
                "simc_revision_hint":pin["revision_hint"],
                "auto_four_stat_source_requested":True,
                "auto_native_G_requested":candidate is not None,
                "auto_native_F_requested":candidate is not None,
                "auto_native_O_requested":False,
                "auto_select_observed_F_no_oil":candidate is not None,
            }
            result=engine.build_environment(
                sessions_root=root,session_folder=None,user=None,
                binary=candidate,revision=None,static_cache=None,
                source_catalog_path=None,bootstrap_result=None,
                fresh_collection_inputs=inputs)
            # Source-owner causes, not just nine downstream compiler flags.
            # The original rows are unchanged and may be large; record only
            # compact, nonsecret status/receipt reuse information.
            owners=(
                "season_discovery","season_join","fresh_ordinary_gear",
                "fresh_tier","fresh_tier_simc_candidate_bridge",
                "fresh_tier_selected_from_existing_evidence",
                "fresh_compiler_tier_source",
                "fresh_pinned_first_party_simc_source",
                "fresh_pinned_v211_source",
                "fresh_pinned_simc_commit_resolution",
                "fresh_food_potion_item_sources",
                "fresh_consumable_item_spell_source",
                "fresh_consumable_simc_effect_relation",
                "fresh_one_spec_simc_representative",
                "fresh_one_spec_physical_G_probe",
                "fresh_gem_enchant_raw_source")
            rec["source_owner_statuses"]={
                key:{
                    "status":row.get("status"),
                    "source_stage_status":(
                        (row.get("source_stage") or {}).get("status")
                        if type(row.get("source_stage")) is dict else None),
                    "reason":row.get("reason"),
                    "missing_slot":row.get("missing_slot"),
                    "neck_candidate_source_coverage":
                        row.get("neck_candidate_source_coverage"),
                    "ring_candidate_source_coverage":
                        row.get("ring_candidate_source_coverage"),
                    "requires":row.get("requires"),
                    "missing":row.get("missing"),
                    "has_candidate":bool(row.get("candidate_path")),
                    "has_pinned_dir":bool(row.get("source_dir")),
                }
                for key in owners
                for row in [result.get(key)]
                if type(row) is dict}
            progress=result.get("zero_history_build") or {}
            compiled=result.get("source_compilation") or {}
            rec.update({
                "source_stage_status":(
                    (result.get("source_stage") or {}).get("status")),
                "source_compilation_status":compiled.get("status"),
                "source_compilation_missing":compiled.get("missing",[]),
                "zero_history_requires":progress.get("requires",[]),
                "current_build_source_identity":(
                    result.get("expected_game_build")==live["game_build"]),
                "simc_native_calls_reported":result.get("native_calls"),
                "environment_ready":result.get("environment_ready") is True,
                "environment_installed":result.get(
                    "environment_installed") is True,
                "budget_evidence":{
                    n:result.get(n) for n in ("G","J","F","O","B","T")},
                "diagnostics":{
                    "J_source":(
                        compiled.get("selected_J_F_source_owner_numeric_unadmitted") or {}
                        ).get("status"),
                    "JF_quality":(
                        compiled.get("selected_J_F_source_owner_quality_unadmitted") or {}
                        ).get("status"),
                    "G_native":(
                        result.get("native_G_numeric_source") or {}).get("status"),
                    "gem_layout":bool(
                        progress.get("default_intrinsic_gem_layout_unadmitted")),
                    "verified_installer":bool(
                        compiled.get("verified_environment_install"))},
            })
            installed=compiled.get("verified_environment_install") or {}
            rec["installed_status"]=installed.get("status")
            ready=(rec["environment_ready"] and
                   rec["environment_installed"] and
                   installed.get("status")==
                       "FRESH_SEASON_VERIFIED_ENVIRONMENT_INSTALLED_READY"
                   and installed.get("stage_output_path"))
            rec["status"]="ZERO_BASE_T1_PASS" if ready else "ZERO_BASE_T1_NOT_READY"
    except Exception as error:
        rec["status"]="ZERO_BASE_T1_BLOCKED"
        rec["exception_type"]=type(error).__name__
        rec["reason"]=str(error)[:500]
    finally:
        OUT.write_text(json.dumps(rec,ensure_ascii=False,sort_keys=True,
                                  indent=2,default=str)+"\n",encoding="utf8")
        print("P3_FR_T1_VERDICT",json.dumps({
            k:rec.get(k) for k in (
                "status","reason","prerequisite_status",
                "missing_credential_names",
                "current_build_source_identity",
                "live_retail_version","source_stage_status",
                "source_compilation_missing","zero_history_requires",
                "simc_native_calls_reported","native_evidence_archive","environment_ready",
                "environment_installed")},ensure_ascii=False,default=str),
            flush=True)
    return 0 if rec["status"]=="ZERO_BASE_T1_PASS" else 2

if __name__=="__main__":
    raise SystemExit(main())
