#!/usr/bin/env python3
"""Reuse the original v236/v234 Native G observation in the one v216 Build.

No new SimC runner, rating parser, source collector, rounding algorithm or
historical gear references. A content-addressed v236 output folder is the
idempotency boundary: an incomplete/failed prior run NEVER silently reruns.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import v222_season_budget_contract as budget
import v229_simc_only_source_seed as seed
import v233_source_only_G_probe_profile as profile_source
import v236_sealed_one_native_G as native

SCHEMA = "v277_zero_history_single_native_G_reuse_v1"
OUTPUT_PREFIX = "source/v277_native_G_"
MAX_LOG_SNIPPET = 12_000
MAX_RECEIPT = 200_000


class GNativeStageBlocked(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise GNativeStageBlocked(code)


def sha_file(file):
    hasher = hashlib.sha256()
    with file.open("rb") as stream:
        for part in iter(lambda: stream.read(1024*1024), b""):
            hasher.update(part)
    return hasher.hexdigest()


def _source_pin(collected):
    source=collected.get("fresh_pinned_first_party_simc_source")
    need(type(source) is dict and type(source.get("source_stage")) is dict
         and source["source_stage"].get("status") in (
              "EXECUTED_AND_SEALED","REUSED_VERIFIED","RECOVERED_VERIFIED")
         and type(source.get("source_dir")) is str,
         "V277_PINNED_SIMC_SOURCE_REQUIRED")
    p=Path(source["source_dir"])
    f=p/seed.RECEIPT
    need(not p.is_symlink() and not f.is_symlink() and f.is_file()
         and 0<f.stat().st_size<MAX_RECEIPT,
         "V277_PINNED_SIMC_SOURCE_RECEIPT_MISSING")
    receipt=json.loads(f.read_text("utf8"))
    need(receipt.get("schema")==seed.SCHEMA and
         receipt.get("provenance_tree_blob_authenticated") is True and
         receipt.get("simc_generated_build")==collected["expected_game_build"]
         and receipt.get("receipt_sha256")==source.get("simc_receipt_sha256"),
         "V277_PINNED_SOURCE_BUILD_OR_RECEIPT_DRIFT")
    revision=receipt.get("simc_revision")
    need(type(revision) is str and seed.REV.fullmatch(revision),
         "V277_EXACT_SOURCE_REVISION_REQUIRED")
    return revision


def _read_log(folder):
    path=folder/"simc.log"
    if not path.is_file() or path.is_symlink():
        return None
    with path.open("rb") as stream:
        sample=stream.read(MAX_LOG_SNIPPET+1)
    return sample[:MAX_LOG_SNIPPET].decode("utf8","replace")


def _verified_cached(receipt, *, output, profile_receipt, binary_sha,
                     source_revision, game_build, iterations):
    need(type(receipt) is dict and receipt.get("schema")==native.SCHEMA
         and type(receipt.get("identity")) is dict,
         "V277_EXISTING_NATIVE_RECEIPT_INVALID")
    identity=receipt["identity"]
    need(identity.get("source_receipt_sha256")==
            profile_receipt["receipt_sha256"]
         and identity.get("source_profile_sha256")==
            profile_receipt["physical_profile_sha256"]
         and identity.get("executable_sha256")==binary_sha
         and identity.get("simc_source_revision")==source_revision
         and identity.get("source_game_build")==game_build
         and identity.get("target_ilevel")==profile_receipt["target_ilevel"]
         and identity.get("iterations")==iterations
         and identity.get("compiled_game_build_not_proven") is True,
         "V277_EXISTING_NATIVE_IDENTITY_CHANGED")
    for name,key in (("input.simc","executed_input_sha256"),
                     ("native.json","native_json2_sha256"),
                     ("simc.log","native_log_sha256")):
        path=output/name
        expected=(identity.get(key) if name=="input.simc"
                  else receipt.get(key))
        if expected is None:
            need(not path.exists(),"V277_UNRECEIPTED_NATIVE_OUTPUT_EXISTS")
        else:
            need(path.is_file() and not path.is_symlink()
                 and sha_file(path)==expected,
                 "V277_NATIVE_OUTPUT_SHA_DRIFT:"+name)
    status=receipt.get("status")
    if status=="PASS_NATIVE_OBSERVED_G_UNPROMOTED":
        need(receipt.get("returncode")==0
             and receipt.get("new_native_calls")==1
             and type(receipt.get("observed_G")) is dict,
             "V277_SUCCESSFUL_NATIVE_RECEIPT_FIELDS_INVALID")
        observed=receipt["observed_G"]
        original={k:v for k,v in observed.items() if k!="receipt_sha256"}
        need(observed.get("receipt_sha256")==seed.digest(
             seed.canonical(original).encode("utf8"))
             and observed.get("native_json2_sha256")==
                 receipt["native_json2_sha256"]
             and observed.get("source_simc_revision")==source_revision
             and observed.get("source_profile_receipt_sha256")==
                 profile_receipt["receipt_sha256"]
             and observed.get("target_ilevel")==profile_receipt["target_ilevel"]
             and observed.get("generic_G_numeric_reference_usable") is True
             and observed.get("generic_G_current_season_membership_required")
                 is False
             and observed.get("full_G_approved") is False
             and observed.get("environment_ready") is False,
             "V277_NATIVE_STATIC_G_OR_SOURCE_RECEIPT_DRIFT")
        rounded=budget.standardize_representative_G(
            observed_G_total=observed["observed_G_total"],
            target_ilevel=observed["target_ilevel"],
            source_observation_sha256=observed["native_json2_sha256"])
        need(observed.get("standardized_G_preview_unapproved")==rounded,
             "V277_EXISTING_G_ROUNDING_DRIFT")
        return {"status":"G_NATIVE_NUMERIC_REFERENCE_OBSERVED_JFO_PENDING",
                "observed_G_total":observed["observed_G_total"],
                "observed_G_vector":observed["observed_G_vector"],
                "standardized_G":rounded["standardized_G"],
                "standardization":rounded,
                "native_json2_sha256":observed["native_json2_sha256"],
                "native_receipt_sha256":sha_file(output/"receipt.json"),
                "source_profile_receipt_sha256":
                    profile_receipt["receipt_sha256"],
                "native_binary_sha256":binary_sha,
                "new_native_calls":0,
                "full_G_approved":False,
                "environment_ready":False}
    need(status in ("FAIL_NATIVE_EXIT","FAIL_NATIVE_JSON2_MISSING",
                    "FAIL_NATIVE_ERROR_OR_STATIC_MISMATCH") and
         receipt.get("new_native_calls")==1,
         "V277_EXISTING_NATIVE_STATUS_UNSAFE")
    return {"status":"G_NATIVE_ATTEMPT_FAILED_NO_AUTOMATIC_RETRY",
            "native_status":status,
            "native_returncode":receipt.get("returncode"),
            "native_error":receipt.get("error"),
            "native_log_excerpt":_read_log(output),
            "native_receipt_sha256":sha_file(output/"receipt.json"),
            "new_native_calls":0,"full_G_approved":False,
            "environment_ready":False}


def collect(*, sessions_root, collected, binary, iterations=1,
            timeout_seconds=180):
    """If installed binary exists, execute at most one original v236 probe.

    No extra user seed/hash field. Same bytes+source+profile reuse the cached
    result; any partial or corrupt prior output blocks instead of repeating
    potentially expensive Native work.
    """
    pending={"schema":SCHEMA,
             "status":"G_NATIVE_SOURCE_PROFILE_OR_BINARY_PENDING",
             "observed_G_total":None,"standardized_G":None,
             "new_native_calls":0,"environment_ready":False}
    probe=collected.get("fresh_one_spec_physical_G_probe")
    if (type(probe) is not dict or not probe.get("profile_path") or
        not probe.get("profile_receipt_path")):
        return {**pending,"reason":"V277_V233_G_PROBE_PROFILE_PENDING"}
    if binary is None:
        return {**pending,"reason":"V277_LOCAL_SIMC_BINARY_NOT_CONFIGURED"}
    root=Path(sessions_root).resolve()
    need(root.is_dir() and not root.is_symlink(),
         "V277_ZERO_HISTORY_WORKSPACE_MISSING")
    stage_root=Path(collected["snapshot_receipt_path"]).resolve().parent.parent
    need(stage_root.is_dir() and stage_root.is_relative_to(root),
         "V277_SOURCE_STAGE_OUTSIDE_WORKSPACE")
    profile=Path(probe["profile_path"])
    receipt_file=Path(probe["profile_receipt_path"])
    need(profile.is_file() and receipt_file.is_file()
         and not profile.is_symlink() and not receipt_file.is_symlink()
         and profile.resolve().is_relative_to(stage_root)
         and receipt_file.resolve().is_relative_to(stage_root)
         and 0<receipt_file.stat().st_size<MAX_RECEIPT,
         "V277_G_PROFILE_NOT_SEALED_SOURCE_PATH")
    prepared=json.loads(receipt_file.read_text("utf8"))
    source_rev=_source_pin(collected)
    need(prepared.get("schema")==profile_source.SCHEMA
         and prepared.get("simc_revision")==source_rev
         and prepared.get("game_build_declared_by_simc_source")==
             collected["expected_game_build"]
         and prepared.get("generic_G_physical_conditions_verified") is True
         and prepared.get("generic_G_current_season_membership_required")
             is False,
         "V277_G_GENERIC_PHYSICAL_SOURCE_NOT_READY")
    native.check(profile.read_bytes(),prepared,
                 expected_source_revision=source_rev,
                 expected_game_build=collected["expected_game_build"])
    # Check the supplied path before resolve() hides a symlink alias.
    supplied_binary=Path(binary).expanduser()
    need(not supplied_binary.is_symlink() and supplied_binary.is_file(),
         "V277_NATIVE_BINARY_FILE_REQUIRED")
    binfile=supplied_binary.resolve(strict=True)
    need(binfile.is_file() and not binfile.is_symlink(),
         "V277_NATIVE_BINARY_FILE_REQUIRED")
    bin_sha=sha_file(binfile)
    need(type(iterations) is int and iterations==1
         and type(timeout_seconds) is int and 1<=timeout_seconds<=900,
         "V277_ONE_NATIVE_REFERENCE_POLICY")
    identity={
        "profile_sha256":prepared["physical_profile_sha256"],
        "profile_receipt_sha256":prepared["receipt_sha256"],
        "source_revision":source_rev,
        "game_build":collected["expected_game_build"],
        "target_ilevel":prepared["target_ilevel"],
        "binary_sha256":bin_sha,
        "iterations":iterations,
    }
    key=seed.digest(seed.canonical(identity).encode("utf8"))[:24]
    output=stage_root/(OUTPUT_PREFIX+key)
    if output.exists():
        need(output.is_dir() and not output.is_symlink(),
             "V277_EXISTING_NATIVE_OUTPUT_UNSAFE")
        report=output/"receipt.json"
        need(report.is_file() and not report.is_symlink()
             and 0<report.stat().st_size<MAX_RECEIPT,
             "V277_INCOMPLETE_NATIVE_OUTPUT_NO_AUTOMATIC_RETRY")
        raw=report.read_bytes()
        try:
            doc=json.loads(raw)
        except (ValueError,UnicodeError) as exc:
            raise GNativeStageBlocked(
                "V277_INVALID_SAVED_NATIVE_RECEIPT_NO_RETRY") from exc
        outcome=_verified_cached(doc,output=output,
            profile_receipt=prepared,binary_sha=bin_sha,
            source_revision=source_rev,
            game_build=collected["expected_game_build"],
            iterations=iterations)
        return {**pending,**outcome,
                "native_run_folder":str(output),
                "cache_reused":True,"new_native_calls":0}
    run=native.run(
        profile_path=profile,receipt_path=receipt_file,
        binary=binfile,binary_sha256=bin_sha,
        expected_source_revision=source_rev,
        expected_game_build=collected["expected_game_build"],
        output_dir=output,max_new=1,iterations=iterations,
        timeout_seconds=timeout_seconds)
    outcome=_verified_cached(run,output=output,
        profile_receipt=prepared,binary_sha=bin_sha,
        source_revision=source_rev,
        game_build=collected["expected_game_build"],
        iterations=iterations)
    return {**pending,**outcome,
            "native_run_folder":str(output),
            "cache_reused":False,
            "new_native_calls":run["new_native_calls"]}
