#!/usr/bin/env python3
"""v065: actual v063 Native JSON2 -> v015 lineage next CHMV -> v064 SimC port.

No raw original file is altered, no v015 historic tests are reclassified.
Offline mode runs zero SimC; native mode runs one bounded new candidate.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,subprocess,sys
import v046_static_item_cache as itemcache
import v063_numeric_injection as numeric
import v063_official_T_two_native as old
import v064_adaptive_evaluator_port as port
import v065_original_v015_search_adapter as adaptive

EXPECTED_NEW={"crit_rating":400,"haste_rating":1108,
              "mastery_rating":1115,"versatility_rating":529}
SCHEMA="v065_original_v015_to_v064_native_next_once_v1"
class RunnerBlocked(RuntimeError):pass

def need(x,reason):
    if not x:raise RunnerBlocked(reason)

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")

def prepare(prev_v059, prev_v063, output):
    evidence=old.read_evidence(prev_v059)
    basis=old.plan_from_previous(evidence)
    normalized=basis["contract"];budget=basis["static"]
    calibration=basis["calibration"];reference=basis["reference"]
    previous=old.read_evidence(prev_v063)
    observations=[]
    for idx,pair in enumerate(previous):
        target=numeric.read_rating(pair["native"]["sim"]["players"][0])
        request=port.make_request(normalized,budget,calibration,reference,
            old.BINARY_SHA,target,60,output/("historic_%02d.json"%idx))
        # Require same immutable source (selected gear, talents, etc.) and
        # identical numerical gear override from the actual previous Native run.
        source=numeric.input_parts(pair["input"])
        generated=numeric.input_parts(request["input"])
        need(source["stable_sha256"]==generated["stable_sha256"] and
             source["gear_override"]==generated["gear_override"],
             "HISTORICAL_REAL_NATIVE_INPUT_NOT_THE_SAME")
        raw=(prev_v063/("case_%02d"%idx)/"result.json").read_bytes()
        need(json.loads(raw)==pair["native"],"HISTORICAL_JSON2_BYTES_NOT_SAME")
        obs=port.ingest_native(request,pair["native"],calibration,raw)
        observations.append(obs)
    state=adaptive.seed_state(observations,normalized,budget,scouts_limit=1,
                              confirmations_limit=2,step=200)
    proposal=adaptive.next_proposal(state,normalized,budget)
    need(proposal["target"]==EXPECTED_NEW,
         "ORIGINAL_V015_GOLDEN_200_TRANSFER_DRIFT")
    request=port.make_request(normalized,budget,calibration,reference,
          old.BINARY_SHA,proposal["target"],proposal["iterations"],
          output/"guided_01"/"result.json")
    need(sum(request["target"].values())==3152,"OFFICIAL_GJF_CHANGED")
    need(request["profile_binding"]["slots_bound"]==15,
         "NATIVE_PROFILE_EQUIPMENT_COUNT_CHANGED")
    return {"state":state,"proposal":proposal,"request":request,
            "calibration":calibration,"observations":observations}

def run(prev_v059,prev_v063,output,binary=None):
    output.mkdir(parents=True,exist_ok=True)
    receipt={"schema":SCHEMA,"status":"BLOCKED","new_native_calls":0,
        "source_v015_sha256":adaptive.SOURCE_V015_SHA256,
        "historical_v015_71_of_71_not_reexecuted":True,
        "historical_v016_104_of_104_not_reexecuted":True,
        "official_budget":"T=G+J+F","original_files_modified":False,
        "original_product_v016_merged":False,
        "simc_effects_owned_by_simc":True}
    try:
        prepared=prepare(prev_v059,prev_v063,output)
        state=prepared["state"];request=prepared["request"]
        proposal=prepared["proposal"];calibration=prepared["calibration"]
        write(output/"V065_GUIDED_PLAN.json",{
            "source_v015_sha256":adaptive.SOURCE_V015_SHA256,
            "official_T":3152,"candidate":request["target"],
            "iterations":request["iterations"],
            "case_key":request["case_key"],"state_status":state["status"],
            "previous_real_native_reused":2,
            "confirmed_v015_golden_direction":True,
            "new_native_calls_in_plan":0})
        receipt["status"]="PASS_OFFLINE_V015_LINEAGE_TO_V064_PORT"
        receipt["candidate"]=request["target"]
        receipt["old_native_reused"]=2
        receipt["case_key"]=request["case_key"]
        receipt["source_v015_policy_only_not_original_runtime"]=True
        if binary is not None:
            need(binary.is_file() and
                 hashlib.sha256(binary.read_bytes()).hexdigest()==old.BINARY_SHA,
                 "SIMC_BINARY_SHA_CHANGED")
            case=output/"guided_01";case.mkdir(exist_ok=True)
            input_file=case/"input.simc"
            native_file=case/"result.json"
            cache_receipt=case/"OBSERVED_NATIVE.json"
            if cache_receipt.exists() and native_file.exists():
                obs=port.verify_disk_cache(
                    request,calibration,json.loads(cache_receipt.read_text()),
                    native_file.read_bytes())
                receipt["native_source"]="CACHED_REAL_JSON2"
            else:
                input_file.write_text(request["input"])
                receipt["new_native_calls"]+=1
                write(output/"V065_PROGRESS.json",receipt)
                proc=subprocess.run([str(binary),str(input_file)],
                     cwd=binary.parent,stdin=subprocess.DEVNULL,
                     capture_output=True,timeout=180,check=False)
                (case/"stdout.txt").write_bytes(proc.stdout)
                (case/"stderr.txt").write_bytes(proc.stderr)
                need(proc.returncode==0,"SIMC_EXIT_"+str(proc.returncode)+
                     "_SEE_UNMODIFIED_STDERR")
                need(native_file.is_file(),"SIMC_JSON2_NOT_PRODUCED")
                raw=native_file.read_bytes()
                obs=port.ingest_native(request,json.loads(raw),calibration,raw)
                write(cache_receipt,obs)
                receipt["native_source"]="NEW_NATIVE"
            final=adaptive.complete(adaptive.reserve(state,proposal,request),obs)
            write(output/"V065_SEARCH_CHECKPOINT.json",final)
            receipt["observation"]=obs
            receipt["scout_done"]=len(final["scouts"])
            receipt["status"]="PASS_ONE_REAL_GUIDED_NATIVE_CHMV_AND_DPS"
    except Exception as e:
        receipt["status"]="BLOCKED_OR_PARTIAL"
        receipt["error"]=type(e).__name__+":"+str(e)
    write(output/"V065_RECEIPT.json",receipt)
    print("V065",receipt["status"],"new_native_calls",receipt["new_native_calls"])
    return 0 if receipt["status"].startswith("PASS_") else 3

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--previous-v059",required=True,type=pathlib.Path)
    p.add_argument("--previous-v063",required=True,type=pathlib.Path)
    p.add_argument("--output",required=True,type=pathlib.Path)
    p.add_argument("--binary",type=pathlib.Path)
    a=p.parse_args()
    return run(a.previous_v059.resolve(),a.previous_v063.resolve(),
               a.output.resolve(),a.binary.resolve() if a.binary else None)

if __name__=="__main__":sys.exit(main())
