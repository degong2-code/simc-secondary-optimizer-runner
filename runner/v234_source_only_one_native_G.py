#!/usr/bin/env python3
"""v234: one optional real SimC subprocess for v233's exact source G probe.

Actual subprocess calls require explicit max_new=1, exact expected binary
SHA256, and one immutable run directory. Reuse v046's Native JSON2 parser
and stat sum; do NOT implement a second stat calculator. Failures keep the
verbatim SimC log and cannot be silently overwritten. Profile and binary
identity are recorded from bytes used in the same invocation, but the binary
game DB build and true current-season membership remain unproved, so G is
OBSERVED, never approved as a user budget.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import subprocess

try:
    from . import v046_static_item_cache as static
    from . import v229_simc_only_source_seed as seed
    from . import v233_source_only_G_probe_profile as compiler
    from . import v222_season_budget_contract as budget
except ImportError:
    import v046_static_item_cache as static
    import v229_simc_only_source_seed as seed
    import v233_source_only_G_probe_profile as compiler
    import v222_season_budget_contract as budget

SCHEMA="v234_one_source_only_physical_native_G_observation_v1"
HEX64=re.compile(r"[a-f0-9]{64}\Z")
SLOT_REMAP={"shoulder":"shoulders","wrist":"wrists","hand":"hands",
            "ring1":"finger1","ring2":"finger2"}


class PhysicalNativeBlocked(ValueError):
    pass


def need(ok,code):
    if not ok:
        raise PhysicalNativeBlocked(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def observe(*, native_raw, profile_receipt, native_binary_sha256,
            executed_profile_sha256):
    """Reconcile one exact v233 profile with v046 JSON2, without old cache."""
    need(type(profile_receipt) is dict and
         profile_receipt.get("schema")==compiler.SCHEMA and
         profile_receipt.get("receipt_sha256")==seed.digest(
            seed.canonical({k:v for k,v in profile_receipt.items()
                            if k!="receipt_sha256"}).encode("utf8")) and
         profile_receipt.get("environment_ready") is False and
         profile_receipt.get("G") is None and
         profile_receipt.get("native_calls")==0,
         "V234_V233_PROFILE_RECEIPT_INVALID")
    need(type(native_binary_sha256) is str and
         HEX64.fullmatch(native_binary_sha256) and
         type(executed_profile_sha256) is str and
         HEX64.fullmatch(executed_profile_sha256),
         "V234_EXECUTION_HASH_REQUIRED")
    need(type(native_raw) is bytes and
         0<len(native_raw)<=static.MAX_NATIVE_BYTES,
         "V234_NATIVE_JSON2_BYTES_INVALID")
    try:
        doc=json.loads(native_raw)
    except (UnicodeError,ValueError) as exc:
        raise PhysicalNativeBlocked("V234_NATIVE_JSON2_DECODE_FAILED") from exc
    revision=doc.get("git_revision") if type(doc) is dict else None
    need(type(revision) is str and
         re.fullmatch(r"[a-f0-9]{7,40}",revision) is not None and
         profile_receipt["simc_revision"].startswith(revision),
         "V234_NATIVE_REVISION_NOT_SOURCE_PINNED")
    game_build=profile_receipt["game_build_declared_by_simc_source"]
    season="simc_"+game_build.replace(".","_")
    try:
        records=static.native_records(native_raw,season=season,
                                      artifact_id="V234_SOURCE_EXECUTION")
    except (static.CacheBlocked,TypeError,KeyError,ValueError) as exc:
        raise PhysicalNativeBlocked("V234_NATIVE_V046_STATIC_PARSER_REJECTED:"+str(exc)) from exc
    selected=profile_receipt["selected_G_slot_ids"]
    observed={}
    identities=[]
    for rec in records:
        slot=SLOT_REMAP.get(rec["observed_slot"],rec["observed_slot"])
        need(slot in selected and slot not in observed,
             "V234_NATIVE_UNEXPECTED_OR_DUPLICATE_EQUIPMENT_SLOT")
        ident=rec["identity"]
        need(ident["item_id"]==selected[slot] and
             ident["ilevel"]==profile_receipt["target_ilevel"] and
             ident["options"]=={} and
             rec["modifiers_present"] is False and
             rec["metadata"]["item_db_source"]=="local",
             "V234_NATIVE_G_ITEM_ID_ILEVEL_OR_MODIFIERS_CHANGED")
        observed[slot]=rec
        identities.append(ident)
    need(set(observed)==set(selected) and len(observed) in (13,14),
         "V234_NATIVE_EQUIPMENT_SLOT_COVERAGE_INCOMPLETE")
    temporary=static.empty_cache(season)
    try:
        static.merge_native(temporary,records)
        total=static.selected_gear_sum(temporary,identities)
    except (static.CacheBlocked,KeyError,TypeError) as exc:
        raise PhysicalNativeBlocked("V234_V046_STATIC_G_SUM_REJECTED") from exc
    vector=total["G_vector"]
    value=total["G_native_static_including_selected_modifiers"]
    need(type(value) is int and value>0 and
         sum(vector.values())==value and
         all(type(vector[k]) is int and vector[k]>=0 for k in static.STATS),
         "V234_NATIVE_STATIC_G_NUMERIC_INVALID")
    # v046 already computed the only physical G. Standardize its TOTAL
    # exactly once, without inventing a second stat extraction or a season
    # approval. v222 will reconcile J/F/O only when those sources are proven.
    native_sha=sha(native_raw)
    g_standard_preview=budget.standardize_representative_G(
        observed_G_total=value,
        target_ilevel=profile_receipt["target_ilevel"],
        source_observation_sha256=native_sha)
    data={
        "schema":SCHEMA,
        "status":"REAL_NATIVE_G_OBSERVED_SEASON_MEMBERSHIP_AND_COMPILED_BUILD_PENDING",
        "source_profile_receipt_sha256":profile_receipt["receipt_sha256"],
        "source_candidate_receipt_sha256":
            profile_receipt["source_candidate_receipt_sha256"],
        "binary_sha256":native_binary_sha256,
        "physical_input_sha256":executed_profile_sha256,
        "native_json2_sha256":native_sha,
        "source_simc_revision":profile_receipt["simc_revision"],
        "native_observed_revision":revision,
        "game_build_from_source_not_independently_binary_attested":game_build,
        "class":profile_receipt["class"],"spec":profile_receipt["spec"],
        "target_ilevel":profile_receipt["target_ilevel"],
        "matching_nontrinket_G_slots":len(observed),
        "observed_G_vector":vector,
        "observed_G_total":value,
        "standardized_G_preview_unapproved":g_standard_preview,
        "generic_G_numeric_reference_usable":(
            profile_receipt.get("generic_G_physical_conditions_verified")
                is True and
            profile_receipt.get(
                "generic_G_current_season_membership_required") is False),
        # Source season is not a precondition for a generic static budget.
        "generic_G_current_season_membership_required":False,
        "source_current_season_membership_verified":False,
        "native_compiled_game_build_independently_verified":False,
        "full_G_approved":False,
        "G":None,"J":None,"F":None,"O":None,"B":None,"T":None,
        "environment_ready":False,
        "new_native_calls_by_observer":0,
        "existing_static_cache_modified":False,
    }
    return {**data,"receipt_sha256":seed.digest(seed.canonical(data).encode())}


def execute(*, source_directory, tier_candidate, representative_candidate,
            race, binary, expected_binary_sha256,
            output_dir, level=None, talents=None,
            iterations=1, timeout_seconds=180, max_new=0,
            season_gear_db=None):
    """Explicit max_new=1 for a single Native call. Other mode is plan only."""
    need(max_new in (0,1) and type(max_new) is int and
         type(iterations) is int and 1<=iterations<=35 and
         type(timeout_seconds) is int and 1<=timeout_seconds<=900,
         "V234_ONE_NATIVE_RUN_LIMIT_INVALID")
    need(type(expected_binary_sha256) is str and
         HEX64.fullmatch(expected_binary_sha256),
         "V234_EXACT_BINARY_SHA_REQUIRED")
    profile,prepared=compiler.build(
        source_directory=source_directory,
        tier_candidate=tier_candidate,
        representative_candidate=representative_candidate,
        race=race,level=level,talents=talents,
        season_gear_db=season_gear_db)
    binary=pathlib.Path(binary).resolve(strict=True)
    need(binary.is_file() and sha(binary.read_bytes())==expected_binary_sha256,
         "V234_BINARY_BYTES_NOT_PINNED_SHA256")
    root=pathlib.Path(output_dir).resolve()
    need(not root.exists(),"V234_ONE_RUN_OUTPUT_MUST_BE_NEW_NO_OVERWRITE")
    root.mkdir(parents=True)
    jsonfile=root/"native.json"
    # Record the actual input bytes passed to the real subprocess, not merely
    # the upstream physical template. The explicit JSON2 path is output only.
    run_input=(profile+f"iterations={iterations}\n"+
               "threads=1\n"+
               f"json2={jsonfile}\n").encode("utf8")
    input_sha=sha(run_input)
    (root/"native.simc").write_bytes(run_input)
    (root/"v233_receipt.json").write_text(
        json.dumps(prepared,indent=2,sort_keys=True)+"\n",encoding="utf8")
    identity={
        "profile_receipt_sha256":prepared["receipt_sha256"],
        "binary_sha256":expected_binary_sha256,
        "native_input_sha256":input_sha,
        "iterations":iterations,
        "timeout_seconds":timeout_seconds,
        "source_game_build":prepared["game_build_declared_by_simc_source"],
        "binary_path_used":str(binary),
    }
    if max_new==0:
        result={"schema":SCHEMA,"status":"PREPARED_NATIVE_NOT_EXECUTED",
                "identity":identity,"new_native_calls":0,
                "native_returncode":None,"observed_G":None,
                "G":None,"B":None,"T":None,"environment_ready":False}
        (root/"receipt.json").write_text(json.dumps(
            result,indent=2,sort_keys=True)+"\n",encoding="utf8")
        return result
    status="FAIL_NATIVE_NOT_RETURNED"
    error=None
    returncode=None
    observed=None
    try:
        with (root/"simc.log").open("wb") as log:
            finished=subprocess.run(
                [str(binary),str(root/"native.simc")],
                cwd=str(root),stdout=log,stderr=subprocess.STDOUT,
                timeout=timeout_seconds,check=False)
        returncode=finished.returncode
        if returncode!=0:
            status="FAIL_NATIVE_EXIT"
            error="returncode="+str(returncode)
        elif not jsonfile.is_file():
            status="FAIL_NATIVE_JSON2_MISSING"
            error="SIMC_DID_NOT_CREATE_JSON2"
        else:
            observed=observe(
                native_raw=jsonfile.read_bytes(),profile_receipt=prepared,
                native_binary_sha256=expected_binary_sha256,
                executed_profile_sha256=input_sha)
            status="PASS_NATIVE_PHYSICAL_G_OBSERVED_NOT_SEASON_APPROVED"
    except (OSError,ValueError,TypeError,KeyError,subprocess.TimeoutExpired,
            PhysicalNativeBlocked) as exc:
        status="FAIL_NATIVE_EXECUTION_OR_JSON2"
        error=type(exc).__name__+":"+str(exc)
    result={"schema":SCHEMA,"status":status,
            "identity":identity,"new_native_calls":1,
            "native_returncode":returncode,
            "error":error,"native_json2_sha256":
                sha(jsonfile.read_bytes()) if jsonfile.is_file() else None,
            "simc_log_sha256":sha((root/"simc.log").read_bytes())
                if (root/"simc.log").is_file() else None,
            "observed_G":observed,"G":None,"B":None,"T":None,
            "environment_ready":False}
    (root/"receipt.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8")
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed-dir",type=pathlib.Path,required=True)
    p.add_argument("--tier-candidate",type=pathlib.Path,required=True)
    p.add_argument("--representative-candidate",type=pathlib.Path,required=True)
    p.add_argument("--season-gear-db",type=pathlib.Path,
                   help="Same-build v167 catalog for exact v232 replay")
    p.add_argument("--race",required=True)
    p.add_argument("--level",type=int,default=None,
                   help="Optional internal override; defaults to compiled SimC MAX_LEVEL")
    p.add_argument("--talents")
    p.add_argument("--simc-binary",type=pathlib.Path,required=True)
    p.add_argument("--simc-sha256",required=True)
    p.add_argument("--output-dir",type=pathlib.Path,required=True)
    p.add_argument("--iterations",type=int,default=1)
    p.add_argument("--max-new",type=int,choices=(0,1),default=0)
    args=p.parse_args(argv)
    tier=json.loads(args.tier_candidate.read_text("utf8"))
    rep=json.loads(args.representative_candidate.read_text("utf8"))
    season_db=(json.loads(args.season_gear_db.read_text("utf8"))
               if args.season_gear_db else None)
    receipt=execute(source_directory=args.seed_dir,tier_candidate=tier,
        representative_candidate=rep,race=args.race,level=args.level,
        talents=args.talents,binary=args.simc_binary,
        expected_binary_sha256=args.simc_sha256,
        output_dir=args.output_dir,iterations=args.iterations,
        max_new=args.max_new,season_gear_db=season_db)
    print("V234_SIMC_NATIVE_ONE_REQUEST",receipt["status"],
          "new_native",receipt["new_native_calls"],flush=True)
    return 0 if receipt["status"].startswith(
        ("PASS_NATIVE","PREPARED_NATIVE")) else 3


if __name__=="__main__":
    raise SystemExit(main())
