#!/usr/bin/env python3
"""P1 bounded, resumable 24-DPS physical -> existing adaptive SimC BATCH.

Only 24 unpromoted source-free preview profiles. Reuses v145 physical input
and SHA receipt, v141 exact acceptance, v098/v096/v094 DPS/SEM/95% results.
NO Native SimC in import/plan-only; no custom solver, effects engine, or
global spec promotion. Every failed specialization is isolated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
sys.path.insert(0,str(ROOT/"integration_probes"))
import v098_target_user_scenario_bootstrap as bootstrap
import v106_user_session_controller as sessions
import v145_targeted_pure_physical_native as physical

SCHEMA="v147_24_dps_source_free_batch_v1"
DEFAULT_OUT=pathlib.Path.home()/"SIMC_Secondary_Optimizer"/"v147_batch"
ALL_SPECS=tuple(sorted("/".join(key) for key in bootstrap.ARCHETYPES))
EXPECTED_SPECS=24
MAX_NATIVE_PER_ADAPTIVE=6

class BatchBlocked(ValueError):
    pass

def need(condition,reason):
    if not condition:
        raise BatchBlocked(reason)

def canonical(obj):
    return json.dumps(obj,sort_keys=True,ensure_ascii=False,
                      separators=(",",":"),allow_nan=False)+"\n"

def atomic_json(path,doc):
    """One latest view only; proof authority remains per-spec Native receipts."""
    path=pathlib.Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+".tmp")
    tmp.write_text(canonical(doc),encoding="utf8")
    os.replace(tmp,path)

def starter_user(key):
    """Real class starter talents/trinkets from compact v146, not source files."""
    need(key in ALL_SPECS,"NOT_ONE_OF_24_DPS_PREVIEWS:"+str(key))
    cl,sp=key.split("/")
    controls=sessions.standard_controls((cl,sp))
    controls["oil_hands"]=[]
    return sessions.user_scenario(controls)

def planned_specs(requested=None):
    need(len(ALL_SPECS)==EXPECTED_SPECS and
         not any(k in bootstrap.PURE_PRODUCT_SPECS
                 for k in bootstrap.ARCHETYPES),
         "BATCH_24_PREVIEW_SET_CHANGED")
    if requested is None:
        return ALL_SPECS
    need(type(requested) in (list,tuple) and bool(requested)
         and all(type(k) is str for k in requested),
         "SPEC_SELECTION_INVALID")
    need(len(requested)==len(set(requested)) and
         all(k in ALL_SPECS for k in requested),
         "SPEC_SELECTION_UNKNOWN_OR_DUPLICATED")
    return tuple(sorted(requested))

def run(binary,out,revision,*,specs=None,execute=False,
        max_new_physical=0,optimize_accepted=False,
        max_adaptive_specs=24,timeout_seconds=180):
    """Continue all selected specs. Failure receipts are never silently retried.

    User intent is explicit: execute=False NEVER calls SimC; execute=True
    permits at most max_new_physical one-iteration physical Native calls.
    optimize_accepted=True may launch original v094 (<=6 candidates/spec);
    it is allowed only when execute=True and the one-spec physical receipt
    passes full original v141 identity verification.
    """
    selected=planned_specs(specs)
    need(type(execute) is bool and type(optimize_accepted) is bool and
         type(max_new_physical) is int and
         0<=max_new_physical<=len(selected) and
         type(max_adaptive_specs) is int and
         0<=max_adaptive_specs<=EXPECTED_SPECS and
         type(timeout_seconds) is int and 1<=timeout_seconds<=900,
         "BATCH_EXECUTION_LIMITS_INVALID")
    need(execute or (max_new_physical==0 and not optimize_accepted),
         "BATCH_NATIVE_REQUIRES_EXPLICIT_EXECUTE")
    need(type(revision) is str and
         7<=len(revision)<=40 and
         all(c in "0123456789abcdef" for c in revision.lower()),
         "BATCH_SIMC_REVISION_MUST_BE_VERIFIED_GIT_HEX")
    binary=pathlib.Path(binary).expanduser().resolve()
    need(binary.is_file(),"BATCH_SIMC_BINARY_REQUIRED")
    # The selected real binary (and revision) provides a stable output
    # namespace, so old exact successes are reused but another revision
    # does not try to overwrite an immutable v145/v098 manifest.
    binary_sha=hashlib.sha256(binary.read_bytes()).hexdigest()
    out=pathlib.Path(out).expanduser().resolve()
    root=out/("simc_"+binary_sha[:16]+"_"+revision.lower())
    physical_root=root/"physical"
    adaptive_root=root/"adaptive"
    summary_path=root/"SUMMARY.json"
    stop_file=root/"CANCEL"
    current={"schema":SCHEMA,"status":"RUNNING",
             "selected_specs":list(selected),
             "binary_sha256":binary_sha,"revision":revision,
             "physical_new_native_calls":0,
             "physical_native_permits_reserved":0,
             "adaptive_specs_attempted_this_run":0,
             "adaptive_calls_existing_runner_limit_per_spec":
                 MAX_NATIVE_PER_ADAPTIVE,
             "new_native_calls_exact_total":None,
             "results":[],
             "user_optimizer_ready_for_all":False,
             "actual_native_trials_are_not_simulated":True}
    def save():
        stats={}
        for row in current["results"]:
            status=row["status"]
            stats[status]=stats.get(status,0)+1
        current["counts"]=stats
        atomic_json(summary_path,current)

    with sessions.worker_lock(root):
        save()
        physical_used=0
        adaptive_used=0
        try:
            for key in selected:
                if stop_file.is_file():
                    current["status"]="CANCELLED_BETWEEN_SPECIALIZATIONS"
                    break
                row={"spec":key,"status":"PENDING",
                     "physical_native_calls_this_run":0,
                     "adaptive_started_this_run":False}
                current["results"].append(row)
                save()
                physical_outcome_uncertain=False
                try:
                    user=starter_user(key)
                    token=physical.sha(physical.canonical(user).encode("utf8"))[:16]
                    physical_case=physical_root/(key.replace("/","__")+"__"+token)
                    row["physical_output"]=str(physical_case)
                    may_run=bool(execute and physical_used<max_new_physical)
                    if may_run:
                        # Reserve capacity BEFORE entering the Native call.
                        # Even an interrupted/unknown outcome cannot cause
                        # the batch to overshoot the user's explicit cap.
                        physical_used+=1
                        current["physical_native_permits_reserved"]=physical_used
                        physical_outcome_uncertain=True
                        save()
                    probe=physical.run(user,binary,physical_root,revision,
                                       iterations=1,timeout_seconds=timeout_seconds,
                                       max_new=int(may_run))
                    physical_outcome_uncertain=False
                    n=probe["new_native_calls"]
                    need(type(n) is int and n in (0,1),
                         "PHYSICAL_CALL_COUNT_INVALID")
                    if may_run and n==0:
                        physical_used-=1
                    row["physical_native_calls_this_run"]=n
                    current["physical_new_native_calls"]+=n
                    current["physical_native_permits_reserved"]=physical_used
                    row["physical_status"]=probe["status"]
                    if probe["status"]=="PREPARED_NO_NATIVE":
                        row["status"]="PENDING_PHYSICAL_NATIVE"
                    elif probe["status"] in ("PRIOR_FAILURE_RETAINED",) or (
                        probe["status"].startswith("FAIL_")):
                        row["status"]="PHYSICAL_FAILED_RETAINED"
                        log=probe.get("raw_log")
                        row["simc_raw_log"]=log
                    elif probe["status"] in ("PASS_PHYSICAL_SIMC",
                                              "CACHED_VERIFIED_PHYSICAL_SIMC"):
                        if not optimize_accepted or adaptive_used>=max_adaptive_specs:
                            row["status"]="PHYSICAL_PASS_ADAPTIVE_PENDING"
                        else:
                            if stop_file.is_file():
                                row["status"]="PHYSICAL_PASS_ADAPTIVE_PENDING"
                                current["status"]="CANCELLED_BETWEEN_SPECIALIZATIONS"
                                save()
                                break
                            adaptive_used+=1
                            current["adaptive_specs_attempted_this_run"]=adaptive_used
                            row["adaptive_started_this_run"]=True
                            stage=adaptive_root/(key.replace("/","__")+"__"+token)
                            row["adaptive_output"]=str(stage)
                            # Keep exact v145 user.json bytes and explicit
                            # per-user physical witness, never another spec.
                            answer=bootstrap.run(
                                physical_case/"user.json",stage,binary,revision,
                                execute=True,pure_stage=True,
                                physical_acceptance_root=physical_case,
                                open_folder=False)
                            result=answer["native_result"]
                            row["adaptive_status"]=result["status"]
                            row["adaptive_result_path"]=result.get("result_path")
                            row["cache_hits_this_run"]=result.get("cache_hits_this_run")
                            row["native_calls_cumulative"]=result.get("native_calls_cumulative")
                            # Output existing selected 95% data without
                            # duplicating v094 detailed Native histories.
                            row["user_result"]=result.get("user_result")
                            row["status"]=("ADAPTIVE_PASS"
                                if result["status"]==
                                "PASS_BOUNDED_GENERIC_NATIVE_SEARCH_AND_CACHE"
                                else "ADAPTIVE_COMPLETED_OTHER_STATUS")
                    else:
                        raise BatchBlocked("UNEXPECTED_PHYSICAL_STATUS:"+
                                           str(probe["status"]))
                except KeyboardInterrupt:
                    # Native may have returned before its receipt was sealed.
                    # Never label the attempt as a confirmed zero call.
                    row["status"]="INTERRUPTED_NATIVE_OUTCOME_UNVERIFIED"
                    row["physical_outcome_uncertain"]=physical_outcome_uncertain
                    raise
                except Exception as exc:
                    # One bad specialization must not stop the other 23.
                    # Original SimC logs remain at per-spec v145/v094 paths.
                    row["status"]="SPEC_FAILED"
                    row["error"]=type(exc).__name__+":"+str(exc)
                    if physical_outcome_uncertain:
                        row["physical_outcome_uncertain"]=True
                finally:
                    save()
            else:
                current["status"]="FINISHED_WITH_PER_SPEC_RESULTS"
        except KeyboardInterrupt:
            current["status"]="INTERRUPTED_RESUMABLE"
        finally:
            save()
    return current

def main(argv=None):
    p=argparse.ArgumentParser(
        description="24 DPS representative SimC batch; plan-only by default, isolated and resumable")
    p.add_argument("--simc",type=pathlib.Path,required=True)
    p.add_argument("--revision",required=True)
    p.add_argument("--out",type=pathlib.Path,default=DEFAULT_OUT)
    p.add_argument("--spec",action="append",help="Optional repeated subset, default ALL 24")
    p.add_argument("--execute",action="store_true",
                   help="Explicitly authorize Native, still bounded by call caps")
    p.add_argument("--max-new-physical",type=int,default=0,
                   help="New physical SimC calls 0..24 (default 0)")
    p.add_argument("--optimize-accepted",action="store_true",
                   help="Execute existing <=6 Native DPS calls for each accepted spec")
    p.add_argument("--max-adaptive-specs",type=int,default=24,
                   help="Maximum adaptive specs this launch, default 24")
    p.add_argument("--timeout-seconds",type=int,default=180)
    args=p.parse_args(argv)
    try:
        report=run(args.simc,args.out,args.revision,
                   specs=args.spec,execute=args.execute,
                   max_new_physical=args.max_new_physical,
                   optimize_accepted=args.optimize_accepted,
                   max_adaptive_specs=args.max_adaptive_specs,
                   timeout_seconds=args.timeout_seconds)
        print("BATCH_STATUS:",report["status"])
        print("SPEC_STATUS_COUNTS:",json.dumps(
            report["counts"],ensure_ascii=False,sort_keys=True))
        print("PHYSICAL_NATIVE_NEW:",report["physical_new_native_calls"])
        print("ADAPTIVE_SPECS_ATTEMPTED:",
              report["adaptive_specs_attempted_this_run"])
        for row in report["results"]:
            print(row["spec"],row["status"],
                  row.get("error") or row.get("simc_raw_log") or "")
        result_folder=pathlib.Path(args.out).expanduser().resolve()/(
            "simc_"+report["binary_sha256"][:16]+"_"+report["revision"].lower())
        print("OUTPUT_DIR:",result_folder)
        if os.name=="nt":
            try:
                os.startfile(str(result_folder))
            except OSError:
                pass
        return 0 if all(r["status"] in (
            "PENDING_PHYSICAL_NATIVE","PHYSICAL_PASS_ADAPTIVE_PENDING",
            "ADAPTIVE_PASS") for r in report["results"]) and report["status"]==(
                "FINISHED_WITH_PER_SPEC_RESULTS") else 3
    except Exception as exc:
        print("V147_BLOCKED:",type(exc).__name__,str(exc),file=sys.stderr)
        return 3

if __name__=="__main__":
    raise SystemExit(main())
