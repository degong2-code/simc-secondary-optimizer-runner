#!/usr/bin/env python3
"""v065: bounded ORIGINAL-v015-policy -> v064 Native evaluator integration.

Two previously executed real v063 Native JSON2 are input anchors. Up to
2 new adaptive scouts (each 60 iterations) and 2 *fresh* 320-iteration
confirmations may run. Every candidate is proposed by v015-derived policy
and executed/validated by v064/v063 P3 official G+J+F contract.

This is a pilot bridge, not merging legacy v015 executables/v016 schema,
not a season gear optimizer, not a proc gate and not a proven optimum.
"""
from __future__ import annotations
import argparse,hashlib,json,os,pathlib,subprocess,sys,tempfile

import v046_static_item_cache as static_cache
import v061_scenario_contract as scenario
import v062_static_budget_bridge as budget
import v063_numeric_injection as injection
import v063_official_T_two_native as native063
import v064_adaptive_evaluator_port as evaluator
import v065_v015_scheduler_adapter as scheduler

BINARY_SHA=native063.BINARY_SHA
RUN_SCHEMA="v065_bounded_legacy_policy_native_integration_v1"
SCOUT_MAX=2
SCOUT_ITERATIONS=60
CONFIRM_ITERATIONS=320
NEW_NATIVE_MAX=4

class PipelineBlocked(ValueError):pass
def need(ok,code):
    if not ok:raise PipelineBlocked(code)

def write_atomic(dest,obj):
    dest=pathlib.Path(dest);dest.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=dest.parent,prefix=".v065-",suffix=".tmp")
    try:
        with os.fdopen(fd,"w",encoding="utf8") as f:
            json.dump(obj,f,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)
            f.write("\n");f.flush();os.fsync(f.fileno())
        os.replace(tmp,dest)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def integration_plan(previous):
    """Real native offsets and G, but new *wrapper* runtime budget."""
    witnesses=native063.read_evidence(previous)
    prev=native063.plan_from_previous(witnesses)
    # Re-normalize only the runtime budget, never mutate old v063 evidence.
    new_scenario=json.loads(json.dumps(prev["contract"]["scenario"]))
    new_scenario["runtime"].update({
       "scout_iterations":SCOUT_ITERATIONS,
       "confirm_iterations":CONFIRM_ITERATIONS,
       "max_native_calls":NEW_NATIVE_MAX})
    normalized=scenario.normalize(new_scenario)
    ref=prev["reference"]
    _,remaining=native063.scenario_for_bounded_reference(ref)
    payload=json.dumps(witnesses[0]["native"],sort_keys=True).encode("utf8")
    static=static_cache.empty_cache()
    static_cache.merge_native(static,static_cache.native_records(
      payload,artifact_id="EXISTING_V063_NATIVE_READ_ONLY"))
    measured_budget=budget.compile_static_budget(normalized,remaining,static)
    need(measured_budget["budget"]["T_official"]==3152 and
         measured_budget["G_if_complete"]==2849,
         "SCOPED_OFFICIAL_GJF_TOTAL_CHANGED")
    calibrated=prev["calibration"]
    observations=[]
    for i,w in enumerate(witnesses):
        # Reconstruct external interface request with *new scenario* identity.
        target=injection.read_rating(w["native"]["sim"]["players"][0])
        req=evaluator.make_request(normalized,measured_budget,calibrated,ref,
             BINARY_SHA,target,SCOUT_ITERATIONS,
             pathlib.Path(previous)/("case_%02d"%i)/"result.json")
        source_parts=injection.input_parts(w["input"])
        generated_parts=injection.input_parts(req["input"])
        need(source_parts["gear_override"]==generated_parts["gear_override"]
             and source_parts["stable_sha256"]==generated_parts["stable_sha256"],
             "PRIOR_REAL_NATIVE_INPUT_NOT_REPRODUCIBLE")
        raw=(pathlib.Path(previous)/("case_%02d"%i)/"result.json").read_bytes()
        obs=evaluator.ingest_native(req,w["native"],calibrated,raw)
        obs["simc_seed"]=(w["native"]["sim"].get("options") or {}).get("seed")
        observations.append(obs)
    return normalized,measured_budget,calibrated,ref,observations

def execute_one(req,calibration,binary,case_folder,progress,cancel_file=None,cache_only=False):
    """Persist before Native call; resume only when receipt and bytes verify."""
    case_folder=pathlib.Path(case_folder)
    case_folder.mkdir(parents=True,exist_ok=True)
    source_file=case_folder/"input.simc"
    native_file=case_folder/"result.json"
    receipt_file=case_folder/"native_receipt.json"
    need(pathlib.Path(req["json2_location"]).resolve()==native_file.resolve(),
         "RESULT_DESTINATION_NOT_EQUAL_CASE")
    if native_file.exists() or receipt_file.exists():
        need(native_file.is_file() and receipt_file.is_file(),
             "PARTIAL_NATIVE_OUTPUT_REQUIRES_EXPLICIT_RECOVERY")
        expected=json.loads(receipt_file.read_text(encoding="utf8"))
        raw=native_file.read_bytes()
        validated=evaluator.verify_disk_cache(req,calibration,expected,raw)
        need(source_file.is_file() and
             hashlib.sha256(source_file.read_bytes()).hexdigest()==req["input_sha256"],
             "CACHED_NATIVE_INPUT_MISSING_OR_MODIFIED")
        # Seed is observation metadata only; measured SimC version/actual rating is
        # independently checked by v064; no seed is fabricated.
        validated["simc_seed"]=expected.get("simc_seed")
        validated["source"]="CACHED_VERIFIED_NATIVE"
        return validated
    if cache_only:
        raise PipelineBlocked("CACHE_ONLY_REFUSES_NEW_NATIVE")
    if cancel_file and pathlib.Path(cancel_file).exists():
        raise PipelineBlocked("USER_CANCEL_FILE_PRESENT")
    need(progress["native_attempts"]<NEW_NATIVE_MAX,"NATIVE_CALL_BUDGET_EXCEEDED")
    source_file.write_text(req["input"],encoding="utf8")
    need(hashlib.sha256(source_file.read_bytes()).hexdigest()==req["input_sha256"],
         "WRITTEN_SIMC_INPUT_SHA_CHANGED")
    progress["native_attempts"]+=1
    progress["status"]="RUNNING_NATIVE"
    write_atomic(case_folder.parent/"V065_PROGRESS.json",progress)
    proc=subprocess.run([str(binary),str(source_file)],
         cwd=binary.parent,stdin=subprocess.DEVNULL,
         stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=240)
    (case_folder/"stdout.txt").write_bytes(proc.stdout)
    (case_folder/"stderr.txt").write_bytes(proc.stderr)
    need(proc.returncode==0,
         "SIMC_NATIVE_EXIT_"+str(proc.returncode)+"_SEE_UNMODIFIED_STDERR")
    need(native_file.is_file() and 0<native_file.stat().st_size<50_000_000,
         "SIMC_JSON2_ABSENT_OR_TOO_LARGE")
    raw=native_file.read_bytes();doc=json.loads(raw)
    checked=evaluator.ingest_native(req,doc,calibration,raw)
    checked["simc_seed"]=(doc.get("sim") or {}).get("options",{}).get("seed")
    write_atomic(receipt_file,checked)
    return checked | {"source":"NEW_NATIVE"}

def start(previous,out,binary=None,cancel_file=None,prepared=None,cache_only=False):
    out=pathlib.Path(out);out.mkdir(parents=True,exist_ok=True)
    progress={"schema":RUN_SCHEMA,"status":"STARTING","native_attempts":0,
              "new_native_max":NEW_NATIVE_MAX,
              "old_original_v015_tests_recorded":"71/71_NOT_RERUN",
              "old_original_v016_tests_recorded":"104/104_NOT_RERUN",
              "original_source_bytes_modified":False,
              "product_v015_v016_original_directly_merged":False,
              "official_budget":"T=G+J+F",
              "owns_item_effects":"SIMC","scouts":[],"confirmations":[]}
    receiptpath=out/"V065_RECEIPT.json"
    try:
        if prepared is None:
            normalized,static,calibration,reference,history=integration_plan(previous)
            scoped_binary_sha=BINARY_SHA
        else:
            # Explicit external scenario bundle from v066. Do not import
            # any Mage-only v063 profile builder or calibrate a new class
            # with another character's numeric offset.
            need(type(prepared) is dict and set(prepared)=={
                "normalized","budget","calibration","profile",
                "prior_observations","summary"},"GENERIC_PREPARED_FIELDS")
            normalized=prepared["normalized"]
            static=prepared["budget"]
            calibration=prepared["calibration"]
            reference=prepared["profile"]
            history=prepared["prior_observations"]
            meta=prepared["summary"]
            scoped_binary_sha=meta["simc_binary_sha256"]
            need(meta["status"]=="READY_NUMERIC_PROFILE_SCOPED"
                 and meta["scenario_digest"]==normalized["scenario_digest"]
                 and meta["T_official"]==static["budget"]["T_official"]
                 and meta["profile_sha256"]==hashlib.sha256(
                     reference.encode("utf8")).hexdigest()
                 and meta["simc_revision"]==calibration["native_revision"]
                 and type(scoped_binary_sha) is str
                 and len(scoped_binary_sha)==64
                 and all(ch in "0123456789abcdef" for ch in scoped_binary_sha),
                 "GENERIC_PREPARED_BINDING_MISMATCH")
            # An externally supplied context must have been normalized
            # from our active v061 contract; exact gear and combat binding
            # remains v064's responsibility for each proposed evaluation.
        progress.update({"status":"PLAN_READY",
           "prior_real_native_count":len(history),
           "scenario_digest":normalized["scenario_digest"],
           "official_T":static["budget"]["T_official"],
           "G":static["G_if_complete"],"J":normalized["budget"]["J"],
           "F":normalized["budget"]["F"],
           "scoped_simc_binary_sha256":scoped_binary_sha,
           "calibration_offset":calibration["net_input_to_json2_rating_offset"],
           "source_original_v015_sha256":scheduler.SOURCE_V015_SHA256,
           "source_original_v016_sha256":scheduler.SOURCE_V016_SHA256})
        # Preserve bounded Native-call accounting across process restarts.
        # A pre-existing attempt cannot be silently reset to zero.
        history_file=out/"V065_PROGRESS.json"
        if not history_file.exists() and receiptpath.exists():
            history_file=receiptpath
        if history_file.exists():
            previous=json.loads(history_file.read_text(encoding="utf8"))
            old_sha=previous.get("scoped_simc_binary_sha256")
            # Original v065 PASS receipts predated the scoped binary-SHA
            # field. A read-only historical replay may recover them ONLY
            # with the full 4-attempt quota already spent and all four
            # case receipts subsequently independently revalidated through
            # v064's binary-keyed JSON2 cache. This migration can never
            # authorize even one fresh Native call or a new-profile switch.
            legacy_cache_only=(
                cache_only is True and old_sha is None
                and previous.get("native_attempts")==NEW_NATIVE_MAX
                and previous.get("new_native_max")==NEW_NATIVE_MAX
                and previous.get("official_budget")=="T=G+J+F")
            need(previous.get("schema")==RUN_SCHEMA and
                 previous.get("scenario_digest")==progress["scenario_digest"]
                 and previous.get("official_T")==progress["official_T"]
                 and (old_sha==scoped_binary_sha or legacy_cache_only)
                 and previous.get("source_original_v015_sha256")==progress["source_original_v015_sha256"]
                 and previous.get("source_original_v016_sha256")==progress["source_original_v016_sha256"]
                 and previous.get("calibration_offset")==progress["calibration_offset"]
                 and type(previous.get("native_attempts")) is int
                 and 0<=previous["native_attempts"]<=NEW_NATIVE_MAX,
                 "DURABLE_PROGRESS_IDENTITY_OR_BUDGET_CONFLICT")
            progress["native_attempts"]=previous["native_attempts"]
            progress["prior_attempts_recovered"]=previous["native_attempts"]
            progress["legacy_cache_only_replay_requires_each_native_sha"]=legacy_cache_only
        state=scheduler.initial_state(normalized,static,history,
                    step=100,scout_max=SCOUT_MAX)
        write_atomic(out/"V065_PROGRESS.json",progress)
        if binary is not None:
            binary=pathlib.Path(binary).resolve()
            need(binary.is_file() and hashlib.sha256(binary.read_bytes()).hexdigest()==scoped_binary_sha,
                 "NATIVE_BINARY_SHA_NOT_PINNED")
        for i in range(SCOUT_MAX):
            folder=out/("scout_%02d"%i)
            proposal=scheduler.next_scout(state,normalized,static,calibration,
               reference,scoped_binary_sha,folder/"result.json",SCOUT_ITERATIONS)
            row={"target":proposal["case"]["target"],
                 "anchor":proposal["anchor"],
                 "case_key":proposal["case"]["case_key"],
                 "decision":proposal["decision"]}
            if binary is None:
                row["status"]="OFFLINE_PLAN_ONLY"
                progress["scouts"].append(row)
                progress["status"]="PASS_OFFLINE_SCOUT_PLAN_ONLY"
                break
            observed=execute_one(proposal["case"],calibration,binary,folder,
                                 progress,cancel_file,cache_only=cache_only)
            row.update({"status":"PASS_NATIVE","result":observed})
            progress["scouts"].append(row)
            state=scheduler.accept_scout(state,proposal["case"],observed)
            write_atomic(out/"V065_PROGRESS.json",progress)
        if binary is not None:
            pair=scheduler.pair_to_confirm(state,normalized,static,calibration,
                  reference,scoped_binary_sha,out,CONFIRM_ITERATIONS)
            progress["confirmation_selected_from_scout_means"]=[
                c["target"] for c in pair["cases"]]
            write_atomic(out/"V065_PROGRESS.json",progress)
            fresh={}
            for i,req in enumerate(pair["cases"]):
                folder=out/("confirm_%02d"%i)
                obs=execute_one(req,calibration,binary,folder,progress,cancel_file,cache_only=cache_only)
                fresh[scheduler.key(obs["target"])]=obs
                progress["confirmations"].append(obs)
                write_atomic(out/"V065_PROGRESS.json",progress)
            vectors=[scheduler.key(req["target"]) for req in pair["cases"]]
            progress["fresh_confirmation_judgment"]=scheduler.fresh_confirmation_judgment(
                vectors,fresh)
            progress["native_json2_stat_parity_pass"]=True
            progress["status"]="PASS_BOUNDED_ADAPTIVE_SCOUT_AND_FRESH_CONFIRM"
            progress["global_optimum_proven"]=False
    except Exception as exc:
        progress["status"]="BLOCKED_OR_PARTIAL"
        progress["error"]=type(exc).__name__+":"+str(exc)
    write_atomic(receiptpath,progress)
    print("V065",progress["status"],"native_attempts",progress["native_attempts"],flush=True)
    return 0 if progress["status"].startswith("PASS") else 3

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("--previous-v063",type=pathlib.Path,required=True)
    ap.add_argument("--output",type=pathlib.Path,required=True)
    ap.add_argument("--binary",type=pathlib.Path)
    ap.add_argument("--cancel-file",type=pathlib.Path)
    a=ap.parse_args(argv)
    return start(a.previous_v063.resolve(),a.output.resolve(),
       a.binary.resolve() if a.binary else None,a.cancel_file)

if __name__=="__main__":
    sys.exit(main())
