#!/usr/bin/env python3
"""v136: one real target-334 SimC smoke per v134-generic spec; no DPS search.

Reuse v106->v098 builder and v132 receipt/JSON2 helpers. Never rerun the
separate 17/17 original-source Native successes. Old 7 product sessions
are untouched. A smoke success does not validate 95% or full optimization.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys

import v101_common_representative_equipment as gear
import v106_user_session_controller as ui
import v098_target_user_scenario_bootstrap as bootstrap
import v132_dps_source_batch_smoke as receipts
import v122_common_profile_format as fmt

SCHEMA="v136_v134_target334_one_native_smoke_v1"
REVISION="7bc1071"

class SmokeBlocked(ValueError):pass
def require(ok,why):
    if not ok:raise SmokeBlocked(why)

def keys():
    return tuple(sorted(gear.GENERIC_PENDING))

def plan(binary,out,key):
    require(key in keys(),"NOT_V134_CONNECTED_SPEC")
    case=out/("__".join(key))
    case.mkdir(parents=True,exist_ok=True)
    controls=ui.standard_controls(key)
    scenario=ui.user_scenario(controls)
    result=bootstrap.build(scenario,case/"session",binary,REVISION)
    require(result["native_calls"]==0,"UNEXPECTED_NATIVE_DURING_PLAN")
    profile=case/"session"/"profile.simc"
    original=profile.read_text(encoding="utf8")
    require(original.count("json2="+fmt.JSON2_PLACEHOLDER)==1,
            "PROFILE_JSON2_SEAL_NOT_READY")
    return case,original,result

def run(binary,out,max_new=2,iterations=35,timeout=180):
    require(binary.is_file(),"SIMC_BINARY_REQUIRED")
    require(0<=max_new<=len(keys()),"INVALID_MAX_NEW")
    require(1<=iterations<=200,"INVALID_ITERATIONS")
    require(1<=timeout<=900,"INVALID_TIMEOUT")
    bin_sha=receipts.digest(binary.read_bytes())
    used=0
    cases=[]
    for key in keys():
        dest,profile,product=plan(binary,out,key)
        target=dest/"result.json"
        input_path=dest/"native_input.simc"
        receipt=dest/"receipt.json"
        # Preserve the *exact* target-level gear + fixed source-owned APL.
        # Native's JSON2 path is unique; 35 iterations do NOT alter v098's
        # six-candidate manifest or durable session identity.
        source=receipts.smoke_input(profile,target,iterations)
        raw=source.encode("utf8")
        ident={"schema":SCHEMA,"binary_sha256":bin_sha,
               "profile_sha256":receipts.digest(profile.encode("utf8")),
               "native_input_sha256":receipts.digest(raw),
               "iterations":iterations}
        prior=json.loads(receipt.read_text("utf8")) if receipt.exists() else None
        if prior:
            require(prior.get("identity")==ident,"SMOKE_RECEIPT_IDENTITY_DRIFT:"+"/".join(key))
            require(input_path.is_file() and input_path.read_bytes()==raw,
                    "SMOKE_INPUT_DRIFT:"+"/".join(key))
            if prior.get("status")=="PASS_NATIVE_SMOKE":
                require(target.is_file() and receipts.digest(target.read_bytes())==
                        prior.get("json2_sha256"),"SMOKE_OUTPUT_DRIFT:"+"/".join(key))
                receipts.check_native_result(target.read_bytes())
                cases.append({"spec":"/".join(key),"status":"CACHED_VERIFIED_NATIVE"})
                continue
            cases.append({"spec":"/".join(key),"status":"PRIOR_FAILED_NOT_RETRIED"})
            continue
        require(not input_path.exists() and not target.exists(),
                "UNRECEIPTED_PREEXISTING_NATIVE:"+"/".join(key))
        if used>=max_new:
            cases.append({"spec":"/".join(key),"status":"NOT_RUN_LIMIT"})
            continue
        input_path.write_bytes(raw)
        used+=1
        status="FAIL_NATIVE"
        error=None
        try:
            proc=subprocess.run([str(binary.resolve()),str(input_path.resolve())],
                    cwd=dest,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                    timeout=timeout,check=False)
            (dest/"simc.log").write_text(proc.stdout.decode(
                    "utf8",errors="replace")[-100000:],encoding="utf8")
            if proc.returncode:
                error="SIMC_EXIT_"+str(proc.returncode)
            elif not target.exists():
                error="SIMC_JSON2_NOT_EMITTED"
            else:
                players=receipts.check_native_result(target.read_bytes())
                status="PASS_NATIVE_SMOKE"
        except (OSError,ValueError,subprocess.TimeoutExpired,json.JSONDecodeError) as exc:
            error=type(exc).__name__+":"+str(exc)
        note={"schema":SCHEMA,"identity":ident,"status":status,
              "error":error,"spec":"/".join(key)}
        if status=="PASS_NATIVE_SMOKE":
            note.update({"json2_sha256":receipts.digest(target.read_bytes()),
                         "sim_player_count":players})
        receipts.atomic_json(receipt,note)
        cases.append({"spec":"/".join(key),"status":status,"error":error})
        print("/".join(key),status,flush=True)
    # A partial two-spec pilot must never look like 16/16 Native acceptance.
    # These counts are derived from the recorded cases: no added SimC calls,
    # no altered profile/input identity, and NOT_RUN_LIMIT is not a PASS.
    accepted=sum(x["status"] in ("PASS_NATIVE_SMOKE","CACHED_VERIFIED_NATIVE")
                 for x in cases)
    deferred=sum(x["status"]=="NOT_RUN_LIMIT" for x in cases)
    failed=sum(x["status"] in ("FAIL_NATIVE","PRIOR_FAILED_NOT_RETRIED")
               for x in cases)
    require(accepted+deferred+failed==len(cases),"SMOKE_UNKNOWN_CASE_STATUS")
    complete=accepted==len(keys()) and failed==0
    report={"schema":SCHEMA,"new_native_calls":used,"total_connected":len(keys()),
            "cases":cases,"native_accepted_total":accepted,
            "not_run_limit_total":deferred,"failed_total":failed,
            "all_16_native_accepted":complete,
            "coverage_status":("ALL_16_NATIVE_ACCEPTED" if complete else
                               "FAILED_NATIVE_PRESENT" if failed else
                               "PARTIAL_NOT_RUN"),
            "all_attempted_pass":failed==0,
            "raw_original_sources_not_rerun":True,
            "not_an_adaptive_optimizer":True}
    receipts.atomic_json(out/"V136_TARGET_NATIVE_SMOKE_SUMMARY.json",report)
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--simc",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,
        default=pathlib.Path.home()/"SIMC_Secondary_Optimizer"/"target_smoke_v136")
    p.add_argument("--max-new",type=int,default=2)
    p.add_argument("--iterations",type=int,default=35)
    a=p.parse_args()
    try:
        result=run(a.simc,a.out,a.max_new,a.iterations)
        print("NATIVE_CALLS",result["new_native_calls"],
              "ATTEMPTED_PASS",result["all_attempted_pass"],
              "ACCEPTED",result["native_accepted_total"],
              "DEFERRED",result["not_run_limit_total"],
              "FAILED",result["failed_total"],
              "ALL_16_ACCEPTED",result["all_16_native_accepted"])
        code=0 if result["all_attempted_pass"] else 3
    except Exception as exc:
        print("V136_BLOCKED",type(exc).__name__,str(exc),file=sys.stderr)
        code=3
    print("RESULT_DIR:",a.out.resolve())
    if os.name=="nt" and a.out.exists():
        try:os.startfile(str(a.out.resolve()))
        except OSError:pass
    return code
if __name__=="__main__":
    sys.exit(main())
