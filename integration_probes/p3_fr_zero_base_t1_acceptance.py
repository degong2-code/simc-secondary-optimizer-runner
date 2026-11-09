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

from runner import v143_specialization_contracts as spec_contracts
from runner import v216_environment_build_coordinator as engine
from runner import v271_user_socket_gem_layout as physical_gems
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



@contextmanager
def atomic_native_audit_zip(destination):
    """Failed verification never leaves an uploadable partial ZIP."""
    pending=destination.with_name(destination.name+".pending")
    if pending.exists() or pending.is_symlink():
        raise ValueError("P3_GJ_NATIVE_ARCHIVE_PENDING_EXISTS")
    try:
        with zipfile.ZipFile(pending,"w",compression=zipfile.ZIP_DEFLATED,
                             compresslevel=6) as output:
            yield output
        pending.replace(destination)
    finally:
        if pending.exists() or pending.is_symlink():
            pending.unlink()


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
    with atomic_native_audit_zip(destination) as archive:
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



def summarize_existing_f_and_j(progress, compiled, *, special_gem_id):
    """Diagnose existing v216 source rows, no item discovery or Native."""
    progress=progress if type(progress) is dict else {}
    compiled=compiled if type(compiled) is dict else {}
    row=compiled.get("automatic_F_native_measurements_unadmitted")
    if type(row) is not dict:
        row=progress.get("automatic_F_native_measurements_unadmitted")
    if type(row) is not dict:
        row={}
    per_item=row.get("per_item")
    if type(per_item) is not list:
        per_item=[]
    if len(per_item)>8:
        raise ValueError("P3_GK_F_MEASUREMENT_RECEIPT_COUNT")
    summary=[]
    for item in per_item:
        if type(item) is not dict:
            raise ValueError("P3_GK_F_MEASUREMENT_ROW")
        summary.append({
            k:item.get(k) for k in ("physical_item_id","status",
                                    "new_native_calls","cache_hit")})
    source=compiled.get("automatic_F_O_measurement_candidates_unadmitted")
    work=source.get("flask") if type(source) is dict else None
    return {
        "F":{
            "status":row.get("status"),
            "attempted":row.get("attempted"),
            "remaining":row.get("remaining"),
            "new_native_calls":row.get("new_native_calls"),
            "source_candidate_count":len(work) if type(work) is list else None,
            "items":summary,
            "next_batch_pending":"AUTO_F_NEXT_MEASUREMENT_BATCH_PENDING"
                in progress.get("requires",[]),
            "source_only_not_official_F":True,
        },
        "J":{
            "existing_special_gem_id_supplied":(
                type(special_gem_id) is int and special_gem_id>0),
            "physical_layout_observed":bool(
                progress.get("default_intrinsic_gem_layout_unadmitted")),
            "missing_required_existing_special_gem_id":(
                special_gem_id is None),
            "missing_special_id_is_test_input_not_season_absence":True,
        },
        "native_calls":0,
        "source_http_calls":0,
    }



def optional_exact_item_id(environment, name):
    """Internal T1 diagnostic selection only; numeric rating is NEVER input."""
    raw=environment.get(name,"")
    if raw is None or raw=="":
        return None
    if type(raw) is not str or re.fullmatch(r"[1-9][0-9]{0,8}",raw) is None:
        raise ValueError("P3_GM_EXACT_PHYSICAL_ITEM_ID_INVALID")
    return int(raw)



def t1_native_source_controls(*, selected_F, f_only, binary_available):
    """F-only requests exactly one selected v278 pair; no G Native."""
    if f_only and selected_F is None:
        raise ValueError("P3_GP_F_ONLY_EXACT_ITEM_ID_REQUIRED")
    return {
        "auto_four_stat_source_requested":not f_only,
        "auto_native_G_requested":binary_available and not f_only,
        "auto_native_F_requested":binary_available,
        "auto_native_O_requested":False,
        "auto_select_observed_F_no_oil":(
            binary_available and selected_F is None),
    }


def source_only_J_socket_controls():
    """Run the original source and J role stages without G/F/O Native."""
    return {"auto_four_stat_source_requested":True,
            "auto_native_G_requested":False,"auto_native_F_requested":False,
            "auto_native_O_requested":False,
            "auto_select_observed_F_no_oil":False}


def selected_t1_source_inputs(*, exact_flask_item_id, existing_special_gem_id,
                              game_build=None, target_socket_count=5):
    """Pass the exact-build nominal J source just like the normal v113 Build.

    This source only supplies season-scoped nominal inputs; the original
    v216 owners remain responsible for J/quality/socket admission and READY.
    Missing exact-build package data must remain PENDING, never fallback.
    """
    result={}
    if exact_flask_item_id is not None:
        result["selected_budget_items"]={
            "flask_item_id":exact_flask_item_id,
            "oil_item_ids_by_hand":{}}
    if existing_special_gem_id is not None:
        result["source_selected_gem_roles"]={
            "special_gem_id":existing_special_gem_id,
            "ordinary_gem_ids":None}
        if game_build is not None:
            nominal=physical_gems.load_packaged_season_nominal_source(
                game_build=game_build,need=engine.need)
            if nominal is not None:
                result["source_target_socket_count"]=target_socket_count
                result["source_ordinary_nominal_by_stat"]=nominal
    return result


def original_verified_F_only_uninstalled(compilation, selected_item_id):
    """Expose a source-verified F number, never product READY or full GJFO."""
    if selected_item_id is None or type(compilation) is not dict:
        return None
    owners=compilation.get(
        "original_J_F_verified_components_not_full_environment") or {}
    item=owners.get("F") if type(owners) is dict else None
    if type(item) is not dict:
        return None
    if (item.get("selected_flask_item_id")!=selected_item_id
            or item.get("source_verification")!="EXACT_NATIVE"
            or type(item.get("rating")) is not int
            or item["rating"]<=0
            or type(item.get("native_pair_receipt_sha256")) is not list
            or len(item["native_pair_receipt_sha256"])!=2):
        raise ValueError("P3_GM_ORIGINAL_F_SOURCE_OWNER_IDENTITY_DRIFT")
    return {"status":"ORIGINAL_SOURCE_VERIFIED_F_NOT_INSTALLED",
            "selected_physical_item_id":selected_item_id,
            "F_rating":item["rating"],
            "source_sha256":item.get("source_sha256"),
            "native_pair_receipt_sha256":
                list(item["native_pair_receipt_sha256"]),
            "official_environment_F":None,
            "environment_ready":False,"new_native_calls":0}


def summarized_existing_GJF_owner_components(compilation):
    """Original verified components only, no installed READY inference."""
    c=compilation if type(compilation) is dict else {}
    partial=c.get("original_J_F_verified_components_not_full_environment") or {}
    if type(partial) is not dict:
        partial={}
    output={}
    for key,item in (("G",c.get("native_G_source_owner_component_not_full_environment")),
                     ("J",partial.get("J")),("F",partial.get("F"))):
        if type(item) is dict:
            output[key]={k:item.get(k) for k in
                         ("rating","source_verification","source_sha256")}
            if key=="F":
                output[key]["physical_item_id"]=item.get("selected_flask_item_id")
                output[key]["native_pair_receipt_sha256"]=item.get(
                    "native_pair_receipt_sha256")
    j=c.get("selected_J_F_source_owner_numeric_unadmitted") or {}
    sockets=c.get("selected_J_intrinsic_socket_origin_unadmitted") or {}
    return {"schema":"p3_gq_original_GJF_owner_summary_v1",
            "verified_components_not_full_environment":output,
            "selected_J_F_numeric_status":j.get("status"),
            "selected_J_F_missing":list(j.get("missing",[])),
            "intrinsic_socket_status":sockets.get("status"),
            "official_GJFO_B_T_ready_inferred":False,
            "native_calls":0,"network_calls":0}


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



def requested_t1_character(environment, *, dps_once):
    """Exact bounded one-spec test input; the real v216 engine stays generic."""
    names=("P3_T1_SPEC_CLASS","P3_T1_SPEC_NAME","P3_T1_SPEC_RACE")
    default=("paladin","retribution","dwarf")
    chosen=tuple(environment.get(name,value)
                 for name,value in zip(names,default))
    if any(type(value) is not str or
           not re.fullmatch(r"[a-z_]+",value) for value in chosen):
        raise ValueError("P3_HS_REQUESTED_CHARACTER_INVALID")
    if not dps_once and chosen!=default:
        raise ValueError("P3_HS_DIFFERENT_SPEC_REQUIRES_DPS_ONE_SHOT")
    contract=spec_contracts.lookup(chosen[0],chosen[1])
    if contract is None or (contract["allowed_races"] is not None
                           and chosen[2] not in contract["allowed_races"]):
        raise ValueError("P3_HS_REQUESTED_DPS_SPEC_OR_RACE_UNSUPPORTED")
    return {"class":chosen[0],"spec":chosen[1],"race":chosen[2]}



def optional_full_consumables(environment, *, dps_once, character):
    """One selected user loadout, without permanent enchant or special gear.

    SimC/v108 owns effects and existing source-pinned token spelling.
    Enhancement's weapon imbues remain equipped; no oil is selected.
    """
    toggle=environment.get("P3_T1_FULL_CONSUMABLES_ONCE","0")
    if toggle not in ("0","1"):
        raise ValueError("P3_HU_FULL_CONSUMABLES_OPT_IN_INVALID")
    if toggle=="0":
        return None
    if not dps_once or (character["class"],character["spec"])!=(
            "shaman","enhancement"):
        raise ValueError("P3_HU_ONE_SHAMAN_DPS_SCOPE_REQUIRED")
    from runner import v108_native_consumable_inputs as existing
    mapping={
        "food":environment.get("P3_T1_FULL_FOOD"),
        "potion":environment.get("P3_T1_FULL_POTION"),
        "augmentation":environment.get("P3_T1_FULL_AUGMENTATION"),
        "omnium_talents":environment.get("P3_T1_FULL_OMNIUM"),
    }
    if any(mapping[k] not in existing.SUPPORTED[k] or
           mapping[k]=="disabled"
           for k in ("food","potion","augmentation")):
        raise ValueError("P3_HU_SOURCE_PINNED_CONSUMABLE_TOKEN_REQUIRED")
    if mapping["omnium_talents"] not in existing.OMNIUM_PRESETS:
        raise ValueError("P3_HU_SOURCE_PINNED_OPTIONAL_MODULE_REQUIRED")
    return mapping


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
        exact_f=optional_exact_item_id(os.environ,"P3_T1_EXACT_FLASK_ITEM_ID")
        special=optional_exact_item_id(os.environ,"P3_T1_EXISTING_SPECIAL_GEM_ID")
        rec["user_selected_flask_id"]=exact_f
        rec["user_selected_gem_ids"]=1 if special is not None else 0
        mode=os.environ.get("P3_T1_F_ONLY","0")
        if mode not in ("0","1"):
            raise ValueError("P3_GP_F_ONLY_OPT_IN_INVALID")
        f_only=(mode=="1")
        source_value=os.environ.get("P3_T1_J_SOCKET_SOURCE_ONLY","0")
        if source_value not in ("0","1"):
            raise ValueError("P3_GU_SOURCE_MODE_INVALID")
        source_only=source_value=="1"
        if source_only and (f_only or exact_f is None or special is None):
            raise ValueError("P3_GU_SOURCE_MODE_SELECTED_IDS_REQUIRED")
        if f_only and exact_f is None:
            raise ValueError("P3_GP_F_ONLY_EXACT_ITEM_ID_REQUIRED")
        rec["selected_f_only_native_mode"]=f_only
        rec["selected_J_socket_source_only_mode"]=source_only
        hy_longrun=os.environ.get("P3_T1_V291_LONGRUN_NATIVE_ONCE","0")
        if hy_longrun not in ("0","1"):
            raise ValueError("P3_HY_EXACT_LONGRUN_MODE_REQUIRED")
        hy_longrun=hy_longrun=="1"
        had_eight=os.environ.get("P3_T1_V291_EIGHT_NATIVE_ONCE","0")
        if had_eight not in ("0","1"):
            raise ValueError("P3_HAD_EXACT_EIGHT_NATIVE_OPT_IN_REQUIRED")
        had_eight=had_eight=="1"
        if had_eight and not hy_longrun:
            raise ValueError("P3_HAD_REQUIRES_V291_LONGRUN")
        hae_ten=os.environ.get("P3_T1_V291_TEN_NATIVE_ONCE","0")
        if hae_ten not in ("0","1"):
            raise ValueError("P3_HAE_EXACT_TEN_NATIVE_OPT_IN_REQUIRED")
        hae_ten=hae_ten=="1"
        if hae_ten and (not hy_longrun or had_eight):
            raise ValueError("P3_HAE_MUST_USE_EXCLUSIVE_V291_LONGRUN")
        hag_portable=os.environ.get("P3_T1_V292_PORTABLE_ONCE","0")
        if hag_portable not in ("0","1"):
            raise ValueError("P3_HAG_EXACT_PORTABLE_OPT_IN_REQUIRED")
        hag_portable=hag_portable=="1"
        if hag_portable and (not hy_longrun or hae_ten or had_eight):
            raise ValueError("P3_HAG_MUST_USE_EXCLUSIVE_V291_LONGRUN")
        dps_once=os.environ.get("P3_T1_DPS_E2E_ONCE","0")
        if dps_once not in ("0","1"):
            raise ValueError("P3_HO_USER_DPS_OPT_IN_INVALID")
        dps_once=dps_once=="1"
        if dps_once and (source_only or f_only or special is None or exact_f is None):
            raise ValueError("P3_HO_REAL_USER_DPS_GJFO_INPUTS_REQUIRED")
        if hy_longrun and not dps_once:
            raise ValueError("P3_HY_MUST_REQUEST_DPS_WITH_VERIFIED_ENVIRONMENT")
        web_longrun=os.environ.get("P3_T1_WEB_LONGRUN_ONCE","0")
        if web_longrun not in ("0","1"):
            raise ValueError("P3_HAJ_EXPLICIT_WEB_OPT_IN_REQUIRED")
        web_longrun=web_longrun=="1"
        if web_longrun and (hy_longrun or hag_portable or not dps_once):
            raise ValueError("P3_HAJ_EXCLUSIVE_REAL_WEB_DPS_REQUIRED")
        rec["web_longrun_e2e_requested"]=web_longrun
        rec["longrun_v291_native_requested"]=hy_longrun
        rec["user_dps_e2e_requested"]=dps_once
        character=requested_t1_character(os.environ,dps_once=dps_once)
        rec["requested_character"]=character
        full_consumables=optional_full_consumables(
            os.environ,dps_once=dps_once,character=character)
        rec["optional_consumables_requested"]=full_consumables
        coverage_on=os.environ.get("P3_T1_AXIS_COVERAGE_ONCE","0")
        if coverage_on not in ("0","1") or (coverage_on=="1" and
                (not dps_once or character["class"]!="shaman" or
                 character["spec"]!="enhancement" or full_consumables is None)):
            raise ValueError("P3_HV_COVERAGE_REQUIRES_FULL_SHAMAN_DPS")
        exploration_policy=(
            "axis_coverage_v1" if coverage_on=="1" else None)
        rec["exploration_policy_requested"]=exploration_policy
        rec["permanent_enchants_requested"]=False
        rec["special_equipment_requested"]=False
        rec["requested_max_F_native_calls"]=(
            0 if source_only else 2 if f_only else 8)
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
                    "class":character["class"],"spec":character["spec"],
                    "target_ilevel":334},
                "g_probe_character":{"race":character["race"]},
                "simc_revision_hint":pin["revision_hint"],
                **(source_only_J_socket_controls() if source_only else
                   t1_native_source_controls(
                       selected_F=exact_f,f_only=f_only,
                       binary_available=candidate is not None)),
                **selected_t1_source_inputs(
                    exact_flask_item_id=exact_f,
                    existing_special_gem_id=special,
                    game_build=live["game_build"]),
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
                "F_J_existing_source_diagnostics":summarize_existing_f_and_j(
                    progress,compiled,special_gem_id=special),
                "GJF_original_source_owner_summary":
                    summarized_existing_GJF_owner_components(compiled),
                "future_five_socket_plan_unadmitted":(
                    compiled.get("future_five_socket_plan_unadmitted")
                    or progress.get("future_five_socket_plan_unadmitted")),
                "J_four_ordinary_two_stat_sources_unadmitted":(
                    compiled.get(
                        "four_stat_ordinary_source_selection_unadmitted")
                    or progress.get(
                        "four_stat_ordinary_source_selection_unadmitted")),
                "J_v268_existing_owner_conditions_unadmitted":(
                    compiled.get(
                        "four_stat_source_owner_diagnostic_unadmitted")
                    or progress.get(
                        "four_stat_source_owner_diagnostic_unadmitted")),
                "J_original_nominal_source_unadmitted":(
                    (compiled.get(
                        "selected_J_F_source_owner_numeric_unadmitted") or {}
                    ).get("J")),
                "existing_season_socket_item_source_unadmitted":(
                    compiled.get(
                        "existing_season_socket_item_source_unadmitted")
                    or progress.get(
                        "existing_season_socket_item_source_unadmitted")),
                "original_source_verified_F_uninstalled":
                    original_verified_F_only_uninstalled(compiled,exact_f),
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
            if dps_once:
                if not ready:
                    raise ValueError("P3_HO_INSTALLED_READY_REQUIRED_BEFORE_DPS")
                # Execute exactly one approved user target through the ORIGINAL
                # v098/v096/v094 adaptive route. SimC owns effects and DPS.
                # No extra J/G/F Native probe or per-spec sweep.
                import v098_target_user_scenario_bootstrap as user_boot
                import v106_user_session_controller as user_sessions
                user_controls=user_sessions.standard_controls(
                    (character["class"],character["spec"]))
                user_controls["race"]=character["race"]
                user=user_sessions.user_scenario(user_controls)
                user["oil_hands"]=[]
                if full_consumables is not None and (
                    user["special_items"] or user["embellishments"] or
                    "enchant_choices" in user):
                    raise ValueError("P3_HU_EXCLUDED_EQUIPMENT_OR_ENCHANT_SELECTED")
                if web_longrun:
                    from integration_probes import p3_haj_real_local_web_native_e2e as web_e2e
                    manual_target=os.environ.get("P3_HAR_USER_MANUAL_FINAL_T")
                    user_manual_T=(int(manual_target) if manual_target
                                   else None)
                    web_result=web_e2e.execute(
                        root,candidate,pin["revision_hint"],live["game_build"],
                        result,receipt_file="p3_haj_web_e2e_receipt.json",
                        manual_final_T=user_manual_T)
                    rec["web_local_e2e"]=web_result
                    if web_result.get("status")!=(
                            "PASS_REAL_FASTAPI_LONGRUN_PREPARE_RUN_RESUME_CACHE"):
                        raise ValueError("P3_HAJ_REAL_HTTP_NATIVE_NOT_COMPLETE")
                    rec["user_dps_e2e"]={
                        "status":web_result["status"],
                        "native_calls_cumulative":
                            web_result["reported"]["native_calls_cumulative"],
                        "budget_source":"ADMITTED_FRESH_SEASON_GJFO_V212_V217",
                        "base_B":(web_result["reported"]["final_T"]-
                                  (result["T"]-result["B"])),
                        "final_T":web_result["reported"]["final_T"],
                        "installed_reference_B":result["B"],
                        "installed_reference_T":result["T"],
                        "user_manual_final_T":user_manual_T,
                        "observed_first_choice":{
                            "absolute_rating_T":
                                web_result["reported"]["observed_chmv"],
                            "observed_dps_mean":
                                web_result["reported"]["dps_mean"],
                            "simc_sem":web_result["reported"]["sem"]},
                        "global_optimum_proven":False}
                elif hy_longrun:
                    # Existing zero-history v212 READY and v098 selected items
                    # supply the unmodified source context. v291 owns Native
                    # checkpoints; v094's six-case test is NOT called.
                    from runner import v096_unified_product_entry as entry
                    from runner import v291_durable_multiscale_native_runner as longrun
                    prepared=user_boot.run_from_verified_environment_build(
                        user,root/"one_user_dps",candidate,
                        pin["revision_hint"],environment_result=result,
                        season_controls=full_consumables,
                        execute=False,open_folder=False)
                    if (prepared.get("status") !=
                        "READY_SOURCE_BOUND_SEASON_MANIFEST_ZERO_NATIVE" or
                        prepared.get("fresh_v212_installed_proof_reused") is not True):
                        raise ValueError("P3_HY_VERIFIED_V098_MANIFEST_REQUIRED")
                    ready_input=entry.source(prepared["generated_manifest"])
                    if had_eight or hae_ten or hag_portable:
                        # v096 reauthenticates a separate higher-budget session.
                        ready_input,_=longrun.stage_extended_manifest(
                            ready_input,prepared["generated_manifest"],12,
                            source_loader=entry.source)
                    total_cap=12 if (had_eight or hae_ten or hag_portable) else 6
                    batches=((4,6) if hae_ten else
                             (4,4) if had_eight else (2,1))
                    required_cases=sum(batches)
                    stage=root/"one_user_dps"/"v291_native"
                    if hag_portable:
                        from runner import v292_portable_native_case_cache as portable
                        origin_archive=pathlib.Path(
                            ".p3-hag-origin/p3_hae_v291_native_evidence.zip"
                        ).resolve(strict=True)
                        origin_sha=(
                            "c53dc09015377ccaf3d53f24bb85950e3999efacecc629be756b9f8856ef5fa9")
                        reused=portable.import_verified_archive(
                            ready_input["context"],ready_input["flask"],
                            candidate,stage,origin_archive,origin_sha,
                            max_native_calls=12)
                        imported=longrun.read_json(stage/"V292_IMPORT.json")
                        pair=reused.get("confirmed_selected_pair_95")
                        native_rows=longrun._load_journal(stage/"V291_JOURNAL.jsonl")
                        if (reused["completed_cases"]!=10
                            or reused["new_native_this_invocation"]!=0
                            or reused["native_attempts_cumulative"]!=10
                            or len(native_rows)!=10
                            or [row["phase"] for row in native_rows[:8]]!=["scout"]*8
                            or [row["phase"] for row in native_rows[8:]]!=["precision"]*2
                            or any(row["iterations"]!=320 for row in native_rows[8:])
                            or not isinstance(pair,dict)
                            or pair["distinct_simc_seeds_observed"] is not True
                            or pair["pairwise_direction_supported"] is not True
                            or pair["global_optimum_proven"] is not False
                            or imported["new_native_executions"]!=0):
                            raise ValueError("P3_HAG_PORTABLE_REAL_NATIVE_REPLAY_DRIFT")
                        rec["v292_portable_replay_e2e"]={
                            "status":"PASS_EXACT_CROSS_JOB_NATIVE_REPLAY_ZERO_NEW_DPS",
                            "source_artifact_run_id":42501052586,
                            "source_archive_sha256":origin_sha,
                            "imported_historical_dps_native":10,
                            "new_dps_native_calls":0,
                            "new_environment_native_calls":rec["simc_native_calls_reported"],
                            "selected_pair_95":pair,
                            "source_catalog_and_full_simc_profile_verified":True}
                        rec["user_dps_e2e"]={
                            "status":"PASS_V292_TEN_PORTABLE_NATIVE_ZERO_NEW_DPS",
                            "native_calls_cumulative":10,
                            "new_dps_native_calls":0,
                            "budget_source":"ADMITTED_FRESH_SEASON_GJFO_V212_V217",
                            "base_B":result["B"],"final_T":result["T"],
                            "observed_first_choice":{
                                "absolute_rating_T":reused["summary"]["observed_best_T"],
                                "observed_dps_mean":reused["summary"]["observed_best_dps"],
                                "simc_sem":reused["summary"]["observed_best_sem"]},
                            "global_optimum_proven":False}
                        pathlib.Path("p3_hag_v292_portable_receipt.json").write_text(
                            json.dumps(rec["v292_portable_replay_e2e"],
                                       sort_keys=True,indent=2)+"\n",encoding="utf8")
                    else:
                        try:
                            first=longrun.run(
                                ready_input["context"],ready_input["flask"],
                                candidate,stage,max_native_calls=total_cap,
                                max_new_native_this_invocation=batches[0])
                            second=longrun.run(
                                ready_input["context"],ready_input["flask"],
                                candidate,stage,max_native_calls=total_cap,
                                max_new_native_this_invocation=batches[1])
                            replay=longrun.run(
                                ready_input["context"],ready_input["flask"],
                                candidate,stage,max_native_calls=total_cap,
                                max_new_native_this_invocation=0,cache_only=True)
                        except Exception:
                            # Capture only exact SimC case files while the
                            # temporary zero-history workspace still exists.
                            audit_zip=pathlib.Path(
                                "p3_hae_v291_failure_evidence.zip" if hae_ten else
                                "p3_hy_v291_failure_evidence.zip")
                            names={"V291_SESSION.json","V291_PENDING.json",
                                   "V291_JOURNAL.jsonl","V291_PROGRESS.json",
                                   "V291_RESULT.json","V065_PROGRESS.json",
                                   "input.simc","result.json","native_receipt.json",
                                   "stderr.txt"}
                            budget_bytes=0
                            with zipfile.ZipFile(audit_zip,"x",
                                                 compression=zipfile.ZIP_DEFLATED,
                                                 compresslevel=6) as audit:
                                for src in sorted(stage.rglob("*")):
                                    if not src.is_file() or src.is_symlink() or src.name not in names:
                                        continue
                                    length=src.stat().st_size
                                    if length>20_000_000 or budget_bytes+length>50_000_000:
                                        raise ValueError("P3_HY_FAILURE_EVIDENCE_BOUNDS_EXCEEDED")
                                    budget_bytes+=length
                                    audit.write(src,src.relative_to(stage).as_posix())
                            rec["v291_failure_evidence"]={
                                "name":audit_zip.name,
                                "sha256":hashlib.sha256(audit_zip.read_bytes()).hexdigest(),
                                "bytes_uncompressed":budget_bytes}
                            raise
                        if (first["status"]!="PAUSED_INVOCATION_NATIVE_BUDGET"
                            or first["completed_cases"]!=batches[0]
                            or first["new_native_this_invocation"]!=batches[0]
                            or second["status"]!="PAUSED_INVOCATION_NATIVE_BUDGET"
                            or second["completed_cases"]!=required_cases
                            or second["new_native_this_invocation"]!=batches[1]
                            or replay["completed_cases"]!=required_cases
                            or replay["new_native_this_invocation"]!=0
                            or replay["native_attempts_cumulative"]!=required_cases
                            or replay["summary"]!=second["summary"]
                            or replay["summary"]["underlying_B"]!=result["B"]):
                            raise ValueError("P3_HAD_OR_HY_V291_NATIVE_RESUME_REPLAY_DRIFT")
                        if hae_ten:
                            native_rows=longrun._load_journal(
                                stage/"V291_JOURNAL.jsonl")
                            pair=replay.get("confirmed_selected_pair_95")
                            if (len(native_rows)!=10 or
                                [row["phase"] for row in native_rows[:8]]!=["scout"]*8 or
                                [row["phase"] for row in native_rows[8:]]!=["precision"]*2 or
                                any(row["iterations"]!=320 for row in native_rows[8:]) or
                                not isinstance(pair,dict) or
                                pair["comparison_scope"]!="SELECTED_CONFIRMED_PAIR_ONLY"):
                                raise ValueError("P3_HAE_NATIVE_SELECTED_PRECISION_NOT_CONFIRMED")
                        archive_path=pathlib.Path(
                            "p3_hae_v291_native_evidence.zip" if hae_ten else
                            "p3_had_v291_native_evidence.zip" if had_eight else
                            "p3_hy_v291_native_evidence.zip")
                        case_files=("input.simc","result.json","native_receipt.json")
                        with zipfile.ZipFile(archive_path,"x",
                                             compression=zipfile.ZIP_DEFLATED,
                                             compresslevel=6) as archive:
                            for i in range(required_cases):
                                folder=longrun.case_folder(stage,i)
                                for filename in case_files:
                                    src=folder/filename
                                    if not src.is_file() or src.stat().st_size>20_000_000:
                                        raise ValueError("P3_HY_NATIVE_CASE_BYTES_MISSING")
                                    archive.write(src,"cases/case_%05d/"%i+filename)
                            for filename in ("V291_SESSION.json","V291_RESULT.json",
                                             "V291_PROGRESS.json","V291_JOURNAL.jsonl"):
                                archive.write(stage/filename,filename)
                        rec["v291_ten_native_e2e" if hae_ten else
                            "v291_eight_native_e2e" if had_eight else "v291_three_native_e2e"]={
                            "status":"PASS_REAL_V291_NATIVE_AND_DURABLE_RESUME_REPLAY",
                            "first_calls":batches[0],"second_calls":batches[1],
                            "replay_new_calls":0,
                            "native_attempts_cumulative":required_cases,
                            "observed":replay["summary"],
                            "confirmed_selected_pair_95":replay.get("confirmed_selected_pair_95"),
                            "archive_sha256":hashlib.sha256(
                                archive_path.read_bytes()).hexdigest(),
                            "archive_name":archive_path.name,
                            "global_optimum_proven":False}
                        rec["user_dps_e2e"]={
                            "status":("PASS_V291_TEN_REAL_NATIVE_PRECISION" if hae_ten
                                      else "PASS_V291_EIGHT_REAL_NATIVE" if had_eight
                                      else "PASS_V291_THREE_REAL_NATIVE"),
                            "native_calls_cumulative":required_cases,
                            "budget_source":"ADMITTED_FRESH_SEASON_GJFO_V212_V217",
                            "base_B":result["B"],"final_T":result["T"],
                            "observed_first_choice":{
                                "absolute_rating_T":
                                    replay["summary"]["observed_best_T"],
                                "observed_dps_mean":
                                    replay["summary"]["observed_best_dps"],
                                "simc_sem":replay["summary"]["observed_best_sem"]},
                            "global_optimum_proven":False}
                else:
                    end_to_end=user_boot.run_from_verified_environment_build(
                        user,root/"one_user_dps",candidate,
                        pin["revision_hint"],environment_result=result,
                        season_controls=full_consumables,
                        exploration_policy=exploration_policy,
                        execute=True,open_folder=False)
                    applied=end_to_end["input_preparation"]
                    native=end_to_end["native_result"]
                    observed=native["user_result"]
                    if (not native["status"].startswith("PASS") or
                        applied["plan"]["budget_source"]!=
                            "ADMITTED_FRESH_SEASON_GJFO_V212_V217" or
                        observed["base_B"]!=result["B"] or
                        observed["final_T"]!=result["T"] or
                        observed["confidence_level"]!=0.95):
                        raise ValueError("P3_HO_USER_DPS_SOURCE_OR_RESULT_DRIFT")
                    rec["user_dps_e2e"]={
                        "status":native["status"],
                        "native_calls_cumulative":
                            native["native_calls_cumulative"],
                        "budget_source":native["budget_source"],
                        "base_B":observed["base_B"],
                        "final_T":observed["final_T"],
                        "observed_first_choice":
                            observed["observed_first_choice"],
                        "confirmation_pair_direction_supported_at_95":
                            observed["confirmation_pair_direction_supported_at_95"],
                        "global_optimum_proven":
                            observed["global_optimum_proven"],
                        "simc_native_gear_consumables_reused":True}
                    if os.environ.get("P3_T1_DPS_NATIVE_AUDIT_ONCE","0")=="1":
                        from integration_probes import p3_ht_observe_existing_dps_native as observer
                        rec["dps_native_audit"]=observer.record(
                            applied,native,root,
                            output_path=pathlib.Path("p3_ht_dps_native_audit.zip"))
            if source_only:
                rec["status"]=(
                    "J_SOCKET_SOURCE_ONLY_SEALED_NOT_READY"
                    if rec["source_compilation_status"]==
                        "FRESH_V191_V211_V213_COMPILED_UNADMITTED"
                        and not rec["source_compilation_missing"]
                        and rec["simc_native_calls_reported"]==0
                    else "J_SOCKET_SOURCE_ONLY_INCOMPLETE_NOT_READY")
            elif f_only:
                # F may be original-v278-proven while G/J/B/T stay absent.
                # A full environment READY claim is strictly prohibited.
                f_receipt=rec["original_source_verified_F_uninstalled"]
                rec["status"]=(
                    "F_ONLY_ORIGINAL_SIMC_SOURCE_VERIFIED_NOT_ENVIRONMENT_READY"
                    if f_receipt is not None and not ready
                    else "F_ONLY_NATIVE_SOURCE_OR_QUALITY_PENDING")
            else:
                rec["status"]=(
                    "ZERO_BASE_USER_DPS_E2E_PASS" if dps_once and ready else
                    "ZERO_BASE_T1_PASS" if ready else "ZERO_BASE_T1_NOT_READY")
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
                "current_build_source_identity","requested_character",
                "optional_consumables_requested",
                "exploration_policy_requested",
                "budget_evidence","installed_status",
                "live_retail_version","source_stage_status",
                "source_compilation_missing","zero_history_requires",
                "simc_native_calls_reported","native_evidence_archive",
                "selected_f_only_native_mode",
                "selected_J_socket_source_only_mode",
                "original_source_verified_F_uninstalled",
                "GJF_original_source_owner_summary","diagnostics",
                "environment_ready","environment_installed",
                "user_dps_e2e_requested","user_dps_e2e",
                "longrun_v291_native_requested","v291_three_native_e2e",
                "v291_eight_native_e2e","v291_ten_native_e2e",
                "v292_portable_replay_e2e")},ensure_ascii=False,default=str),
            flush=True)
    return 0 if rec["status"] in (
        "ZERO_BASE_T1_PASS",
        "ZERO_BASE_USER_DPS_E2E_PASS",
        "F_ONLY_ORIGINAL_SIMC_SOURCE_VERIFIED_NOT_ENVIRONMENT_READY",
        "J_SOCKET_SOURCE_ONLY_SEALED_NOT_READY") else 2

if __name__=="__main__":
    raise SystemExit(main())
