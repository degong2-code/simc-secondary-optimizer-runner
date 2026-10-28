#!/usr/bin/env python3
"""P1 diagnostic: ONE explicitly selected source-free representative SimC physical smoke.

Never promotes a specialization to v098.PURE_PRODUCT_SPECS.  Never runs the
adaptive DPS optimizer, certifies a proc/4pc effect, or changes old Native caches.
A real user's v098 user.json (character/talents/trinkets) is the only input:
the previous full official SimC fixtures are NOT used or required.
Physical profile serialization is the already tested v140 logic.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import pathlib
import subprocess
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
sys.path.insert(0,str(ROOT/"integration_probes"))
import v140_pure_profile_physical_native_smoke as physical
import v063_numeric_injection as numeric
import v098_target_user_scenario_bootstrap as bootstrap
import v143_specialization_contracts as specs

SCHEMA="v145_one_spec_source_free_physical_diagnostic_v1"
DEFAULT_OUT=pathlib.Path.home()/"SIMC_Secondary_Optimizer"/"v145_targeted_physical"

class TargetedSmokeBlocked(ValueError):
    pass

def need(ok,code):
    if not ok:
        raise TargetedSmokeBlocked(code)

def canonical(doc):
    return json.dumps(doc,sort_keys=True,ensure_ascii=False,
                      separators=(",",":"),allow_nan=False)+"\n"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def put_once(path,data):
    data=data.encode("utf8") if isinstance(data,str) else data
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        need(path.read_bytes()==data,"IMMUTABLE_PREVIOUS_INPUT_DRIFT:"+path.name)
    else:
        path.write_bytes(data)

def user_key(user):
    need(type(user) is dict and
         "import_simc_profile" not in user and
         type(user.get("character")) is dict,
         "EXPLICIT_CHARACTER_INPUT_REQUIRED_NOT_OFFICIAL_PROFILE")
    ch=user["character"]
    need(type(ch.get("class")) is str and
         type(ch.get("spec")) is str,"CLASS_AND_SPEC_REQUIRED")
    key=ch["class"]+"/"+ch["spec"]
    need(specs.lookup(ch["class"],ch["spec"]) is not None,
         "NO_INDEPENDENT_COMPILER_CONTRACT")
    # The two existing source-free Native proofs have a separate v140 cache.
    # Do not spend another physical call on them without a changed purpose.
    need((ch["class"],ch["spec"]) not in bootstrap.PURE_PRODUCT_SPECS,
         "ALREADY_NATIVE_WITNESSED_USE_V140_EVIDENCE")
    need(user.get("target")=={"ilevel":334,"final_T":None} and
         user.get("oil_hands")==[],
         "PHYSICAL_ONLY_NEEDS_ILVL334_NO_FINAL_T_AND_NO_OIL")
    need(len(user.get("trinkets",[]))==2,
         "EXACTLY_TWO_USER_TRINKETS_REQUIRED")
    return key

def summary_from_json2(raw,revision):
    native=json.loads(raw)
    need(native.get("report_version")=="2.0.0",
         "JSON2_REPORT_VERSION_NOT_SUPPORTED")
    observed=native.get("git_revision")
    need(numeric.same_simc_commit_revision(observed,revision),
         "JSON2_SIMC_REVISION_MISMATCH:"+str(observed))
    result=physical.json2_summary(raw)
    mean=result["dps_mean"]
    need(type(mean) in (float,int) and math.isfinite(mean) and mean>0,
         "SIMC_DPS_NOT_POSITIVE_OR_APL_INACTIVE")
    return {"json2":result,"observed_git_revision":observed}

def run(user,binary,out,revision,*,iterations=1,timeout_seconds=180,
        max_new=1):
    key=user_key(user)
    need(type(iterations) is int and 1<=iterations<=35,
         "PHYSICAL_ITERATIONS_OUT_OF_BOUNDS")
    need(type(timeout_seconds) is int and 1<=timeout_seconds<=900,
         "NATIVE_TIMEOUT_OUT_OF_BOUNDS")
    need(type(max_new) is int and max_new in (0,1),
         "ONE_NATIVE_CALL_CAP_ONLY")
    need(type(revision) is str and len(revision)>=7,
         "SIMC_REVISION_REQUIRED")
    binary=pathlib.Path(binary).resolve()
    need(binary.is_file(),"SIMC_BINARY_MISSING")
    out=pathlib.Path(out).resolve()
    user_bytes=canonical(user).encode("utf8")
    user_sha=sha(user_bytes)
    # Distinct user inputs cannot silently repoint an existing Native receipt.
    folder=out/(key.replace("/","__")+"__"+user_sha[:16])
    stage=folder/"stage"
    folder.mkdir(parents=True,exist_ok=True)
    put_once(folder/"user.json",user_bytes)
    planned=bootstrap.build(user,stage,binary,revision,pure_stage=True)
    need(planned["status"]=="STAGED_INTERNAL_MANIFEST_NATIVE_NOT_AUTHORIZED" and
         planned["native_calls"]==0 and
         planned["template_archetype"]==key and
         planned["plan"]["item_slots"] in (15,16),
         "EXISTING_STAGE_NATIVE_SEAL_OR_PROFILE_INVALID")
    # Keep the original v140 physical meaning: remove ONLY injected CHMV
    # overrides, never modify source-free items, sockets, trinkets or APL.
    output_json=folder/"physical.json"
    input_file=folder/"physical.simc"
    receipt_file=folder/"receipt.json"
    input_text=physical.physical_input(
        (stage/"profile.simc").read_text(encoding="utf8"),output_json,iterations)
    raw=input_text.encode("utf8")
    binary_sha=sha(binary.read_bytes())
    identity={"user_sha256":user_sha,"simc_binary_sha256":binary_sha,
              "simc_revision":revision,"spec":key,
              "profile_sha256":sha((stage/"profile.simc").read_bytes()),
              "physical_sha256":sha(raw),"iterations":iterations,
              "CHMV_numeric_overrides_removed":True}
    previous=(json.loads(receipt_file.read_text(encoding="utf8"))
              if receipt_file.is_file() else None)
    if previous is not None:
        need(previous.get("identity")==identity,
             "PREVIOUS_NATIVE_IDENTITY_DRIFT")
        need(input_file.is_file() and input_file.read_bytes()==raw,
             "PREVIOUS_NATIVE_INPUT_BYTES_DRIFT")
        if previous.get("status")=="PASS_PHYSICAL_SIMC":
            need(output_json.is_file() and
                 sha(output_json.read_bytes())==previous.get("json2_sha256"),
                 "CACHED_JSON2_DRIFT")
            summary_from_json2(output_json.read_bytes(),revision)
            status="CACHED_VERIFIED_PHYSICAL_SIMC"
            attempted=0
            details=previous["native_json2"]
        else:
            # A failed receipt is immutable; retry in a separately selected
            # output directory, never overwrite failure evidence.
            status="PRIOR_FAILURE_RETAINED"
            attempted=0
            details=None
    elif max_new==0:
        need(not input_file.exists() and not output_json.exists(),
             "UNRECEIPTED_NATIVE_FILES")
        status="PREPARED_NO_NATIVE"
        attempted=0
        details=None
    else:
        need(not input_file.exists() and not output_json.exists(),
             "UNRECEIPTED_NATIVE_FILES")
        put_once(input_file,raw)
        log_file=folder/"simc.log"
        details=None
        status="FAIL_NATIVE_NOT_RETURNED"
        failure=None
        native_returncode=None
        try:
            # Stream output directly to disk: untruncated SimC errors and
            # bounded peak memory, regardless of lengthy diagnostics.
            with log_file.open("wb") as log:
                result=subprocess.run([str(binary),str(input_file)],
                    cwd=str(folder),stdout=log,stderr=subprocess.STDOUT,
                    timeout=timeout_seconds,check=False)
            native_returncode=result.returncode
            if result.returncode:
                status="FAIL_NATIVE_EXIT"
                failure="returncode="+str(result.returncode)
            elif not output_json.is_file():
                status="FAIL_NATIVE_JSON2_MISSING"
                failure="SimulationCraft did not emit physical.json"
            else:
                details=summary_from_json2(output_json.read_bytes(),revision)
                status="PASS_PHYSICAL_SIMC"
        except subprocess.TimeoutExpired:
            status="FAIL_NATIVE_TIMEOUT"
            failure="timeout_seconds="+str(timeout_seconds)
        except (OSError,ValueError,KeyError,TypeError) as exc:
            status="FAIL_NATIVE_JSON2_OR_EXEC"
            failure=type(exc).__name__+":"+str(exc)
        receipt={"schema":SCHEMA,"identity":identity,"spec":key,
                 "status":status,"native_calls":1,
                 "new_native_calls_this_run":1,
                 "native_returncode":native_returncode,
                 "error":failure,"raw_simc_log":str(log_file),
                 "native_json2":details,
                 "physical_sample_only":True,
                 "APL_proc_4pc_effect_certified":False,
                 "CHMV_optimization_completed":False,
                 "user_optimizer_ready":False}
        if output_json.exists():
            receipt["json2_sha256"]=sha(output_json.read_bytes())
        put_once(receipt_file,canonical(receipt))
        attempted=1
    summary={"schema":SCHEMA,"spec":key,"output_dir":str(folder),
             "status":status,"new_native_calls":attempted,
             "physical_input":str(input_file) if input_file.exists() else None,
             "raw_log":str(folder/"simc.log") if (folder/"simc.log").exists() else None,
             "native_json2":details,
             "receipt":str(receipt_file) if receipt_file.exists() else None,
             "user_optimizer_ready":False,
             "next_step":"REVIEW_PHYSICAL_JSON2_BEFORE_ANY_ADAPTIVE_PROMOTION"}
    # SUMMARY is an ephemeral latest-status view; evidence files above are
    # immutable. Do not create a second log, history store, or cache index.
    (folder/"SUMMARY.json").write_text(canonical(summary),encoding="utf8")
    return summary

def main(argv=None):
    p=argparse.ArgumentParser(description="One selected DPS source-independent physical SimC smoke; 0 or 1 new Native")
    user_source=p.add_mutually_exclusive_group(required=True)
    user_source.add_argument("--user-json",type=pathlib.Path,
        help="Real v098 user.json with chosen class/race/talents/trinkets")
    user_source.add_argument("--starter-spec",
        help="One of the 24 preview specs, e.g. rogue/subtlety; editable compact starter inputs, NO official full SimC")
    p.add_argument("--simc",type=pathlib.Path,required=True)
    p.add_argument("--revision",required=True)
    p.add_argument("--out",type=pathlib.Path,default=DEFAULT_OUT)
    p.add_argument("--iterations",type=int,default=1)
    p.add_argument("--timeout-seconds",type=int,default=180)
    p.add_argument("--max-new",type=int,choices=(0,1),default=0,
                   help="0: build/inspect only (default); 1: at most one actual SimC call")
    a=p.parse_args(argv)
    try:
        if a.user_json is not None:
            user=json.loads(a.user_json.read_text(encoding="utf8"))
        else:
            import v106_user_session_controller as sessions
            parts=a.starter_spec.split("/")
            need(len(parts)==2 and tuple(parts) in bootstrap.ARCHETYPES,
                 "STARTER_SPEC_MUST_BE_ONE_OF_24_UNPROMOTED_DPS")
            controls=sessions.standard_controls(tuple(parts))
            # An oil changes gear_* but is NOT a physical item acceptance
            # observation. Remove it from this exact one-shot scenario.
            controls["oil_hands"]=[]
            user=sessions.user_scenario(controls)
        result=run(user,a.simc,a.out,a.revision,
                   iterations=a.iterations,timeout_seconds=a.timeout_seconds,
                   max_new=a.max_new)
        print(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True))
        print("OUTPUT_DIR:",result["output_dir"])
        if os.name=="nt":
            try:
                os.startfile(result["output_dir"])
            except OSError:
                pass
        return 0 if result["status"] in ("PREPARED_NO_NATIVE",
                    "PASS_PHYSICAL_SIMC","CACHED_VERIFIED_PHYSICAL_SIMC") else 3
    except Exception as exc:
        print("V145_BLOCKED:",type(exc).__name__,str(exc),file=sys.stderr)
        return 3

if __name__=="__main__":
    raise SystemExit(main())
