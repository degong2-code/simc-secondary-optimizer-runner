#!/usr/bin/env python3
"""One existing SimC v269 precombat effect delta, at most two Native executions.

The original v269.prepare/compare own option isolation and all CHMV rating
parsing. This thin source-identity runner uses immutable baseline/active
receipts, shared baseline across options, and preserves original SimC errors.
It NEVER proves a flask/oil item's quality, actual weapon compatibility,
game eligibility or v222 budget ownership. No guessed season stat values.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import v269_simc_chmv_effect_snapshot as effect

SCHEMA="v278_original_simc_precombat_native_pair_v1"
MAX_PROFILE=4_000_000
MAX_RECEIPT=20_000
MAX_LOG=12_000
MAX_CASES=2
ITERATIONS=1


class NativePairBlocked(ValueError):
    pass


def need(ok,why):
    if not ok:
        raise NativePairBlocked(why)


def canonical(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,
                      separators=(",",":"),allow_nan=False).encode("utf8")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def file_sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for piece in iter(lambda:f.read(1024*1024),b""):
            h.update(piece)
    return h.hexdigest()


def log_excerpt(folder):
    p=folder/"simc.log"
    if not p.is_file() or p.is_symlink():
        return None
    with p.open("rb") as f:
        return f.read(MAX_LOG).decode("utf8","replace")


def run_case(*,stage_root,profile,source_identity,binary,binary_sha256,
             revision,variant,timeout_seconds):
    """Content key owns immutable attempted run; cache hits never reexecute."""
    need(variant in ("baseline","active"),"V278_CASE_KIND_REQUIRED")
    need(type(timeout_seconds) is int and 1<=timeout_seconds<=900,
         "V278_TIMEOUT_INVALID")
    profile_sha=sha(profile.encode("utf8"))
    identity={
        "profile_sha256":profile_sha,
        "source_profile_sha256":source_identity,
        "binary_sha256":binary_sha256,
        "simc_revision":revision,"iterations":ITERATIONS,
        "variant":variant,
    }
    key=sha(canonical(identity))[:32]
    folder=stage_root/"source"/("v278_"+variant+"_"+key)
    expected_input=(profile+"iterations=1\nthreads=1\n"+
                    "json2="+str((folder/"native.json").resolve())+"\n")
    inp=expected_input.encode("utf8")
    input_sha=sha(inp)
    manifest=folder/"receipt.json"
    if folder.exists():
        need(folder.is_dir() and not folder.is_symlink() and
             manifest.is_file() and not manifest.is_symlink() and
             0<manifest.stat().st_size<=MAX_RECEIPT,
             "V278_INCOMPLETE_NATIVE_ATTEMPT_NO_AUTO_RETRY")
        try:
            prior=json.loads(manifest.read_text("utf8"))
        except (UnicodeError,ValueError) as exc:
            raise NativePairBlocked("V278_INVALID_IMMUTABLE_RECEIPT") from exc
        need(type(prior) is dict and prior.get("schema")==SCHEMA
             and prior.get("identity")==identity
             and prior.get("input_sha256")==input_sha,
             "V278_CACHED_NATIVE_IDENTITY_DRIFT")
        for file,hashfield in (("input.simc","input_sha256"),
                               ("native.json","native_json2_sha256"),
                               ("simc.log","log_sha256")):
            target=folder/file
            expected=prior.get(hashfield)
            if expected is None:
                need(not target.exists(),
                     "V278_UNRECEIPTED_OUTPUT_EXISTS:"+file)
            else:
                need(target.is_file() and not target.is_symlink() and
                     file_sha(target)==expected,
                     "V278_CACHED_NATIVE_OUTPUT_TAMPERED:"+file)
        need(prior.get("status") in (
               "NATIVE_JSON2_CAPTURED","NATIVE_FAILED",
               "NATIVE_JSON2_MISSING","NATIVE_TIMEOUT") and
             prior.get("new_native_calls")==1,
             "V278_CACHED_NATIVE_COMPLETION_NOT_TRUSTED")
        return {"receipt":prior,"folder":folder,
                "new_native_calls":0,"cache_reused":True}
    # mkdir(exist_ok=False) is an attempt-lock: if a process crashes before
    # receipt publication, future calls fail closed rather than rerun.
    folder.mkdir(parents=True,exist_ok=False)
    (folder/"input.simc").write_bytes(inp)
    status="NATIVE_FAILED"
    code=None
    error=None
    try:
        with (folder/"simc.log").open("wb") as log:
            try:
                completed=subprocess.run([str(binary),str(folder/"input.simc")],
                    cwd=folder,stdout=log,stderr=subprocess.STDOUT,
                    check=False,timeout=timeout_seconds)
                code=completed.returncode
                status=("NATIVE_JSON2_CAPTURED" if code==0 and
                        (folder/"native.json").is_file()
                        else "NATIVE_JSON2_MISSING" if code==0
                        else "NATIVE_FAILED")
            except subprocess.TimeoutExpired:
                status="NATIVE_TIMEOUT"
                error="SimC timed out"
            except OSError as exc:
                status="NATIVE_FAILED"
                error=type(exc).__name__+":"+str(exc)
    finally:
        data={
            "schema":SCHEMA,"identity":identity,"input_sha256":input_sha,
            "native_json2_sha256":(
                file_sha(folder/"native.json")
                if (folder/"native.json").is_file() else None),
            "log_sha256":(
                file_sha(folder/"simc.log")
                if (folder/"simc.log").is_file() else None),
            "status":status,"native_returncode":code,
            "error":error,"new_native_calls":1,
        }
        manifest.write_bytes(canonical(data)+b"\n")
    return {"receipt":data,"folder":folder,
            "new_native_calls":1,"cache_reused":False}


def measure(*,stage_root,source_profile_path,binary,simc_revision,
            kind,token,timeout_seconds=180):
    """Run exact shared-baseline/active profile using original v269 schema.

    Caller owns source-quality/selection policy. This method does not
    automatically register any option or count oil O in gear_ overrides.
    """
    pending={"schema":SCHEMA,"status":"SIMC_CONSUMABLE_SOURCE_OR_BINARY_PENDING",
             "kind":kind,"token":token,"new_native_calls":0,
             "static_CHMV_candidate":None,"environment_ready":False,
             "quality_or_slot_verified":False,
             "budget_owner_verified":False}
    if binary is None or source_profile_path is None:
        return {**pending,"reason":"V278_PROFILE_OR_BINARY_NOT_CONFIGURED"}
    root=Path(stage_root).resolve(strict=True)
    source=Path(source_profile_path)
    need(root.is_dir() and not root.is_symlink()
         and source.is_file() and not source.is_symlink()
         and source.resolve().is_relative_to(root)
         and 0<source.stat().st_size<=MAX_PROFILE,
         "V278_SOURCE_PROFILE_NOT_FROM_THIS_STAGE")
    binfile=Path(binary).expanduser().resolve(strict=True)
    need(binfile.is_file() and not binfile.is_symlink(),
         "V278_NATIVE_BINARY_NOT_A_FILE")
    need(type(simc_revision) is str and effect.REV.fullmatch(simc_revision),
         "V278_PINNED_SIMC_REVISION_REQUIRED")
    source_raw=source.read_bytes()
    try:
        profile=source_raw.decode("utf8")
        prepared=effect.prepare(profile=profile,kind=kind,token=token)
    except (UnicodeError,effect.SnapshotBlocked) as exc:
        raise NativePairBlocked(str(exc).split(":",1)[0]) from exc
    binary_sha=file_sha(binfile)
    calls=0
    cases=[]
    for variant in ("baseline","active"):
        case=run_case(
            stage_root=root,
            profile=prepared[variant+"_profile"],
            source_identity=prepared["source_profile_sha256"],
            binary=binfile,binary_sha256=binary_sha,
            revision=simc_revision,variant=variant,
            timeout_seconds=timeout_seconds)
        calls+=case["new_native_calls"]
        cases.append(case)
        if case["receipt"]["status"]!="NATIVE_JSON2_CAPTURED":
            return {**pending,
                "status":"SIMC_CONSUMABLE_NATIVE_FAILED_NO_AUTO_RETRY",
                "failed_variant":variant,
                "native_status":case["receipt"]["status"],
                "native_returncode":case["receipt"]["native_returncode"],
                "native_error":case["receipt"]["error"],
                "native_log_excerpt":log_excerpt(case["folder"]),
                "new_native_calls":calls}
    try:
        observed=effect.compare(
            baseline_json2=(cases[0]["folder"]/"native.json").read_bytes(),
            active_json2=(cases[1]["folder"]/"native.json").read_bytes(),
            prepared=prepared,binary_sha256=binary_sha,
            simc_revision=simc_revision)
    except (effect.SnapshotBlocked,ValueError) as exc:
        raise NativePairBlocked(
            "V278_ORIGINAL_V269_NATIVE_COMPARISON_FAILED:"
            +str(exc).split(":",1)[0]) from exc
    need(observed["baseline_profile_sha256"]==
             prepared["baseline_profile_sha256"]
         and observed["active_profile_sha256"]==
             prepared["active_profile_sha256"],
         "V278_V269_PROFILE_IDENTITY_DRIFT")
    return {**pending,
        "status":("SIMC_STATIC_CHMV_EFFECT_OBSERVED_NOT_ADMITTED"
                  if observed["static_CHMV_candidate"] is not None else
                  "SIMC_CONDITIONAL_OR_NONSTATIC_EFFECT_PENDING"),
        "observed":observed,
        "static_CHMV_candidate":observed["static_CHMV_candidate"],
        "simc_revision":simc_revision,"binary_sha256":binary_sha,
        "source_profile_sha256":prepared["source_profile_sha256"],
        "native_case_receipts":[
            {"variant":variant,
             "receipt_path":str(case["folder"]/"receipt.json"),
             "receipt_sha256":file_sha(case["folder"]/"receipt.json"),
             "cache_reused":case["cache_reused"]}
            for variant,case in zip(("baseline","active"),cases)],
        "new_native_calls":calls,
        "F_candidate_unadmitted":(
            sum(observed["static_CHMV_candidate"].values())
            if kind=="flask" and observed["static_CHMV_candidate"] is not None
            else None),
        "O_candidate_unadmitted":(
            observed["static_CHMV_candidate"]
            if kind=="temporary_enchant" else None),
        "source_only_numeric_observation":True}
