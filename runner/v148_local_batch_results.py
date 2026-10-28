#!/usr/bin/env python3
"""P1 read-only 24-spec real Native batch results; portable for VIEWING only.

Use the copied folder's local structure, NEVER the old machine's absolute
paths embedded in SUMMARY.json. Verify original v145 physical JSON2 hashes,
user/profile identities and exact stored v094 report -> v096 display values.
This is NOT a relocated Native cache or a product-wide specialization unlock.
No subprocess, writes, or separate optimizer/statistics engine.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re

import v096_unified_product_entry as entry
import v098_target_user_scenario_bootstrap as bootstrap

SCHEMA="v148_read_only_native_batch_results_v1"
BATCH=re.compile(r"simc_([0-9a-f]{16})_([0-9a-f]{7,40})\Z")
FULL_SHA=re.compile(r"[0-9a-f]{64}\Z")
SPECS=frozenset("/".join(k) for k in bootstrap.ARCHETYPES)
MAX_BATCHES=16
MAX_SUMMARY_BYTES=1024*1024
MAX_JSON_BYTES=8*1024*1024

class BatchViewBlocked(ValueError): pass

def need(ok,reason):
    if not ok:raise BatchViewBlocked("V148_"+reason)

def sha(raw):return hashlib.sha256(raw).hexdigest()

def _source_path(base,*parts):
    """Avoid symlink escapes and do not resolve paths embedded in user JSON."""
    base=pathlib.Path(base).resolve()
    target=base.joinpath(*parts)
    need(target.resolve().is_relative_to(base),
         "PATH_OUTSIDE_SELECTED_LOCAL_BATCH")
    return target

def _json(path,limit=MAX_JSON_BYTES):
    path=pathlib.Path(path)
    need(path.is_file() and path.stat().st_size<=limit,"FILE_MISSING_OR_TOO_LARGE")
    return json.loads(path.read_bytes())

def _local_batch(folder):
    folder=pathlib.Path(folder).expanduser().resolve()
    name=folder.name
    match=BATCH.fullmatch(name)
    need(match is not None,"BATCH_FOLDER_ID_INVALID")
    summary=_json(_source_path(folder,"SUMMARY.json"),MAX_SUMMARY_BYTES)
    need(type(summary) is dict and
         summary.get("schema")=="v147_24_dps_source_free_batch_v1"
         and type(summary.get("results")) is list
         and type(summary.get("revision")) is str
         and summary["revision"].lower()==match[2]
         and type(summary.get("binary_sha256")) is str
         and bool(FULL_SHA.fullmatch(summary["binary_sha256"]))
         and summary["binary_sha256"].startswith(match[1]),
         "V147_SUMMARY_IDENTITY_DRIFT")
    return folder,summary

def find_batches(root):
    """Discover only local named batch folders, no read of actual Native files."""
    root=pathlib.Path(root).expanduser().resolve()
    if not root.is_dir():return []
    candidates=[x for x in root.iterdir() if x.is_dir()
                and not x.is_symlink() and BATCH.fullmatch(x.name)]
    # Do not accept arbitrary user-supplied sibling paths or follow links.
    need(len(candidates)<=MAX_BATCHES,"TOO_MANY_BATCH_FOLDERS_SELECT_ONE")
    found=[]
    for folder in sorted(candidates,key=lambda p:p.name):
        try:
            _,doc=_local_batch(folder)
            rows=doc["results"]
            valid_specs=(len(rows)<=24 and
                len({x.get("spec") for x in rows if type(x) is dict})==len(rows) and
                all(type(x) is dict and x.get("spec") in SPECS for x in rows))
            if not valid_specs:continue
            found.append({"batch_id":folder.name,
                          "revision":doc["revision"],
                          "selected_specs":len(rows),
                          "reported_adaptive_pass":sum(
                            x.get("status")=="ADAPTIVE_PASS" for x in rows),
                          "scope":"LOCAL_COPY_READ_ONLY_NOT_NATIVE_CACHE_REPLAY"})
        except (OSError,ValueError,TypeError,KeyError,OverflowError):
            # A corrupted copied folder must not make the whole UI unusable.
            continue
    return found

def _read_pass(folder,summary,row):
    """Fail closed for a reported PASS whose original local files disagree.

    Compare the original Native JSON2 physical data and exact re-derived
    v096 95% display from the stored v094 report. Do not trust copied paths.
    """
    spec=row["spec"]
    need(type(spec) is str and spec in SPECS,
         "NOT_AN_UNPROMOTED_PREVIEW_SPEC")
    need(row.get("status")=="ADAPTIVE_PASS" and
         row.get("physical_status")=="PASS_PHYSICAL_SIMC" and
         row.get("adaptive_status")=="PASS_BOUNDED_GENERIC_NATIVE_SEARCH_AND_CACHE",
         "ADAPTIVE_PASS_STATUS_REQUIRED")
    original=row.get("physical_output")
    # SUMMARY may come from Windows and be opened on Linux; treat it ONLY
    # as an expected basename, NEVER a path to read.
    need(type(original) is str and
         original.replace("\\","/").split("/")[-1].startswith(
             spec.replace("/","__")+"__"),
         "ORIGINAL_PHYSICAL_CASE_NAME_INVALID")
    basename=original.replace("\\","/").split("/")[-1]
    need(bool(re.fullmatch(re.escape(spec.replace("/","__"))+r"__[0-9a-f]{16}",basename)),
         "PHYSICAL_CASE_NAME_INVALID")
    physical=_source_path(folder,"physical",basename)
    adaptive=_source_path(folder,"adaptive",basename)
    user_path=_source_path(physical,"user.json")
    need(user_path.is_file(),"PHYSICAL_USER_MISSING")
    user_raw=user_path.read_bytes()
    user_sha=sha(user_raw)
    need(basename==spec.replace("/","__")+"__"+user_sha[:16],
         "PHYSICAL_USER_SHA_FOLDER_DRIFT")
    user=json.loads(user_raw)
    ch=user.get("character") if type(user) is dict else None
    need(type(ch) is dict and
         ch.get("class")+"/"+ch.get("spec")==spec and
         user.get("target")=={"ilevel":334,"final_T":None} and
         user.get("oil_hands")==[] and
         "import_simc_profile" not in user,
         "PHYSICAL_USER_SCENARIO_DRIFT")
    receipt=_json(_source_path(physical,"receipt.json"))
    ident=receipt.get("identity") if type(receipt) is dict else None
    need(type(ident) is dict and
         receipt.get("schema")==
            "v145_one_spec_source_free_physical_diagnostic_v1" and
         receipt.get("status")=="PASS_PHYSICAL_SIMC" and
         receipt.get("native_calls")==1 and
         ident.get("user_sha256")==user_sha and
         ident.get("spec")==spec and
         ident.get("simc_binary_sha256")==summary["binary_sha256"] and
         ident.get("simc_revision")==summary["revision"] and
         ident.get("CHMV_numeric_overrides_removed") is True and
         receipt.get("physical_sample_only") is True,
         "PHYSICAL_RECEIPT_IDENTITY_DRIFT")
    profile=_source_path(physical,"stage","profile.simc")
    need(profile.is_file() and sha(profile.read_bytes())==
         ident.get("profile_sha256"),
         "PHYSICAL_STAGE_PROFILE_DRIFT")
    native_raw=_source_path(physical,"physical.json").read_bytes()
    need(sha(native_raw)==receipt.get("json2_sha256"),
         "PHYSICAL_JSON2_SHA_DRIFT")
    native=json.loads(native_raw)
    need(native.get("report_version")=="2.0.0" and
         type(native.get("git_revision")) is str and
         native["git_revision"].lower().startswith(summary["revision"].lower()) or
         (type(native.get("git_revision")) is str and
          summary["revision"].lower().startswith(native["git_revision"].lower())),
         "PHYSICAL_NATIVE_GIT_REVISION_MISMATCH")
    players=(native.get("sim") or {}).get("players") or []
    need(len(players)==1 and type(players[0]) is dict,
         "PHYSICAL_JSON2_SINGLE_PLAYER_REQUIRED")
    report=_json(_source_path(adaptive,"simc_results","V094_RESULT.json"))
    need(type(report) is dict and
         report.get("schema")=="v094_generic_durable_inclusive_adaptive_v1" and
         report.get("status")==row["adaptive_status"] and
         report.get("global_optimum_proven") is False and
         type(report.get("observations")) is list and
         len(report["observations"])==6 and
         report.get("new_native_attempts_cumulative")==6,
         "EXISTING_V094_REPORT_NOT_SIX_PASS")
    actual=entry.user_facing_result(report)
    need(actual==row.get("user_result") and
         actual.get("confidence_level")==0.95 and
         actual.get("global_optimum_proven") is False and
         actual.get("final_T")==report.get("official_final_T"),
         "SUMMARY_V094_DPS_SEM_OR_95_DRIFT")
    return {"spec":spec,"status":"LOCAL_NATIVE_REPORT_HASHES_AND_95_RESULT_MATCH",
            "user_result":actual,
            "physical_original_sha256":sha(native_raw),
            "native_candidates_recorded":6,
            "native_calls_now":0,
            "cache_portable_for_execution":False}

def view_batch(root,batch_id):
    need(type(batch_id) is str and BATCH.fullmatch(batch_id),
         "BATCH_ID_INVALID")
    root=pathlib.Path(root).expanduser().resolve()
    folder=_source_path(root,batch_id)
    need(not folder.is_symlink(),"BATCH_SYMLINK_REFUSED")
    folder,summary=_local_batch(folder)
    rows=summary["results"]
    need(len(rows)<=24 and
         all(type(x) is dict and x.get("spec") in SPECS for x in rows) and
         len({x["spec"] for x in rows})==len(rows),
         "V147_DUPLICATE_OR_UNKNOWN_SPECS")
    results=[]
    for row in rows:
        if row.get("status")!="ADAPTIVE_PASS":
            results.append({"spec":row["spec"],"status":"NOT_COMPLETED_IN_SOURCE_BATCH",
                            "native_calls_now":0})
        else:
            try:
                results.append(_read_pass(folder,summary,row))
            except (OSError,ValueError,TypeError,KeyError,OverflowError) as exc:
                results.append({"spec":row["spec"],
                                "status":"LOCAL_EVIDENCE_NOT_MATCHED",
                                "reason":type(exc).__name__+
                                         ":"+str(exc).split(":",1)[0],
                                "native_calls_now":0})
    passed=sum(x["status"]=="LOCAL_NATIVE_REPORT_HASHES_AND_95_RESULT_MATCH"
               for x in results)
    return {"schema":SCHEMA,"batch_id":batch_id,
            "revision":summary["revision"],
            "total_specs":len(rows),"matched_read_only_results":passed,
            "scope":"ORIGINAL_BATCH_COPY_REPORT_VIEW_NOT_NATIVE_CACHE_REPLAY",
            "execution_ready_from_relocated_cache":False,
            "native_calls_now":0,"results":results}
