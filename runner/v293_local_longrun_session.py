#!/usr/bin/env python3
"""P1-3: opt-in local long-run session adapter to existing v096/v291/v292.

No new optimization/effect engine. The parent v106 session identity and its
OS worker lock are shared by legacy and long-run executions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

import v096_unified_product_entry as entry
import v106_user_session_controller as sessions
import v291_durable_multiscale_native_runner as durable

SCHEMA = "v293_local_longrun_session_v1"


class LocalLongRunBlocked(ValueError):
    pass


def need(condition, code):
    if not condition:
        raise LocalLongRunBlocked(code)


def config_path(folder):
    return pathlib.Path(folder) / "V293_LONGRUN_CONFIG.json"


def worker_state_path(folder):
    return pathlib.Path(folder) / "V293_WORKER_STATE.json"


def source_manifest(folder):
    path = pathlib.Path(folder).resolve() / "generated" / "manifest.json"
    need(path.is_file() and not path.is_symlink(),
         "V293_EXISTING_V106_MANIFEST_REQUIRED")
    return path


def source_identity(folder):
    path = source_manifest(folder)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def config(folder):
    path = config_path(folder)
    if not path.is_file():
        return None
    need(not path.is_symlink() and path.stat().st_size <= 16384,
         "V293_CONFIG_INVALID_FILE")
    doc = json.loads(path.read_text(encoding="utf8"))
    need(type(doc) is dict and set(doc) == {
         "schema","native_budget","manifest_sha256"} and
         doc["schema"] == SCHEMA and
         type(doc["native_budget"]) is int and
         12 <= doc["native_budget"] <= 2000 and
         doc["manifest_sha256"] == source_identity(folder),
         "V293_SEALED_CONFIG_OR_MANIFEST_DRIFT")
    return doc


def stage_path(folder, budget):
    need(type(budget) is int and 12 <= budget <= 2000,
         "V293_BOUNDED_NATIVE_BUDGET_REQUIRED")
    return pathlib.Path(folder).resolve() / "generated" / (
        "v291_longrun_%d" % budget)


def prepare(folder, budget):
    """Re-authenticate the product source and typed budget; zero Native."""
    manifest = source_manifest(folder)
    ready = entry.source(manifest)
    original_cap = ready["context"]["bundle"]["prepared"]["scenario"][
        "scenario"]["runtime"]["max_native_calls"]
    need(type(original_cap) is int and original_cap < budget,
         "V293_LONGRUN_NEEDS_DISTINCT_TYPED_BUDGET")
    staged, new_manifest = durable.stage_extended_manifest(
        ready, manifest, budget, source_loader=entry.source)
    stage = stage_path(folder, budget)
    need(new_manifest == (stage / "manifest.json") and
         staged["paths"]["output_dir"] == stage / "simc_results" and
         staged["paths"]["cancel_file"] == stage / "CANCEL" and
         staged["context"]["identity"]["approved_final_T"] ==
            ready["context"]["identity"]["approved_final_T"],
         "V293_STAGE_OR_APPROVED_BUDGET_DRIFT")
    return staged


def establish(folder, budget):
    """Seal one opt-in long-run budget per existing v106 session."""
    existing = config(folder)
    if existing is not None:
        need(existing["native_budget"] == budget,
             "V293_EXISTING_SESSION_BUDGET_CANNOT_CHANGE")
    prepared = prepare(folder, budget)
    document = {"schema": SCHEMA, "native_budget": budget,
                "manifest_sha256": source_identity(folder)}
    if existing is None:
        durable.atomic(config_path(folder), document)
    return prepared


def state(folder, status, *, reason=None, native_calls=None):
    item = {"schema": SCHEMA, "status": status}
    if reason is not None:
        item["reason"] = str(reason)[:500]
    if native_calls is not None:
        item["new_native_this_invocation"] = native_calls
    durable.atomic(worker_state_path(folder), item)


def run_worker(folder, budget, batch, *, cache_only=False,
               portable_archive=None, portable_sha256=None,
               max_elapsed_seconds=900):
    folder = pathlib.Path(folder).resolve(strict=True)
    need(type(batch) is int and 0 <= batch <= 32,
         "V293_NATIVE_BATCH_LIMIT")
    need(type(max_elapsed_seconds) is int and
         60 <= max_elapsed_seconds <= 3600,
         "V293_ELAPSED_BOUND")
    need(bool(portable_archive) == bool(portable_sha256),
         "V293_ARCHIVE_REQUIRES_APPROVED_SHA")
    need(not portable_archive or (cache_only and batch == 0),
         "V293_IMPORT_MUST_BE_ZERO_NATIVE")
    acquired = False
    try:
        with sessions.worker_lock(folder):
            acquired = True
            saved = config(folder)
            need(saved is not None and saved["native_budget"] == budget,
                 "V293_SESSION_CONFIG_NOT_SEALED")
            prepared = prepare(folder, budget)
            state(folder, "RUNNING")
            path = prepared["paths"]
            output = path["output_dir"]
            if portable_archive:
                import v292_portable_native_case_cache as portable
                result = portable.import_verified_archive(
                    prepared["context"], prepared["flask"],
                    path["native_binary"], output,
                    portable_archive, portable_sha256,
                    max_native_calls=budget)
            else:
                result = durable.run(
                    prepared["context"], prepared["flask"],
                    path["native_binary"], output,
                    max_native_calls=budget,
                    max_new_native_this_invocation=(0 if cache_only else batch),
                    cache_only=cache_only,
                    cancel_file=path["cancel_file"],
                    max_elapsed_seconds=max_elapsed_seconds,
                    recover_verified_partial=False,
                    open_folder=False)
            state(folder, result["status"],
                  native_calls=result["new_native_this_invocation"])
            return 0
    except Exception as exc:
        # A competing worker owns the shared v106 lock. Never overwrite its
        # running status or cancel marker when this invocation is rejected.
        if acquired:
            state(folder, "BLOCKED_OR_PARTIAL",
                  reason=type(exc).__name__+":"+str(exc))
        print("V293_LONGRUN_BLOCKED:",type(exc).__name__,str(exc),
              file=sys.stderr,flush=True)
        return 3


def read_status(folder, active=False):
    saved = config(folder)
    if saved is None:
        return {"enabled": False, "native_calls_now": 0}
    budget = saved["native_budget"]
    stage = stage_path(folder,budget)
    output = stage/"simc_results"
    progress_file = output/"V291_PROGRESS.json"
    result_file = output/"V291_RESULT.json"
    worker_file = worker_state_path(folder)
    progress = (durable.read_json(progress_file)
                if progress_file.is_file() else {})
    worker = (durable.read_json(worker_file)
              if worker_file.is_file() else {})
    completed = progress.get("completed_cases",0)
    attempts = progress.get("native_attempts_cumulative",0)
    need(type(completed) is int and 0 <= completed <= budget and
         type(attempts) is int and 0 <= attempts <= budget,
         "V293_PROGRESS_BUDGET_DRIFT")
    return {
        "enabled": True, "session_id": pathlib.Path(folder).name,
        "active": bool(active), "cancel_requested": (stage/"CANCEL").exists(),
        "result_ready": result_file.is_file(),
        "native_calls_now": 0,
        "native_budget": budget,
        "progress": {
            "status": progress.get("status","NOT_STARTED"),
            "completed_jobs": completed, "planned_jobs": budget,
            "progress_percent": (100.0 * completed / budget),
            "native_attempts": attempts,
            "cache_hits":progress.get("verified_cached_this_invocation",0),
            "worker":worker,
            "error":progress.get("error")
        }
    }


def user_result(report):
    """Only map v291 actual measurements to the existing v113 display."""
    summary = report["summary"]
    need(report["confidence_for_display"] == 0.95 and
         report["no_global_optimum_proof"] is True,
         "V293_ONLY_REAL_95_NONOPTIMAL_RESULT")
    T = summary["final_T"]
    best = summary["observed_best_T"]
    need(T > 0 and sum(best.values()) == T,
         "V293_OBSERVED_T_MISMATCH")
    pair = report.get("confirmed_selected_pair_95")
    alternatives = []
    for alt in summary["material_alternatives"]:
        alternatives.append({
            "absolute_rating_T": alt["T"],
            "percent_of_final_T":{k:100.0*v/T for k,v in alt["T"].items()},
            "observed_dps_mean":alt["dps_mean"],
            "simc_sem":alt["dps_sem"],
            "observed_dps_loss_pct":100.0*alt["observed_relative_dps_loss"],
            "rating_moved_fraction_B":alt["fraction_B_moved"],
            "pairwise_95_label": alt["label"]
        })
    return {
        "confidence_level":0.95, "global_optimum_proven":False,
        "base_B":summary["underlying_B"],
        "final_T":T, "fixed_O":summary["fixed_O"],
        "observed_first_choice":{
            "absolute_rating_T":best,
            "percent_of_final_T":{k:100.0*v/T for k,v in best.items()},
            "observed_dps_mean":summary["observed_best_dps"],
            "simc_sem":summary["observed_best_sem"]},
        "observed_unique_candidates":summary["observed_unique_targets"],
        "material_near_alternatives":alternatives,
        "confirmation_pair_direction_supported_at_95": bool(
            pair and pair["pairwise_direction_supported"]),
        "selected_pair_95_only":True,
        "selection_multiplicity_corrected":False
    }


def read_result(folder):
    saved = config(folder)
    need(saved is not None, "V293_NOT_CONFIGURED")
    path = stage_path(folder,saved["native_budget"])/"simc_results"/"V291_RESULT.json"
    need(path.is_file(), "V293_RESULT_NOT_READY")
    report = durable.read_json(path)
    return {"session_id":pathlib.Path(folder).name,
            "status":report["status"],
            "native_calls_cumulative":report["native_attempts_cumulative"],
            "cache_hits_this_run":report["verified_cache_cases_this_invocation"],
            "user_result":user_result(report),
            "confirmed_selected_pair_95":report.get("confirmed_selected_pair_95"),
            "selected_from_multiple_candidates":True,
            "global_optimum_proven":False}


def main(argv=None):
    p = argparse.ArgumentParser(description="P1-3 existing v291 long-run local worker")
    p.add_argument("--session",required=True)
    p.add_argument("--max-native-calls",type=int,required=True)
    p.add_argument("--batch",type=int,default=4)
    p.add_argument("--max-elapsed-seconds",type=int,default=900)
    p.add_argument("--cache-only",action="store_true")
    p.add_argument("--portable-archive")
    p.add_argument("--portable-sha256")
    x=p.parse_args(argv)
    return run_worker(x.session,x.max_native_calls,x.batch,
                      cache_only=x.cache_only,
                      portable_archive=x.portable_archive,
                      portable_sha256=x.portable_sha256,
                      max_elapsed_seconds=x.max_elapsed_seconds)


if __name__=="__main__":
    raise SystemExit(main())
