#!/usr/bin/env python3
"""v079B: fix measured nonlinear rating injection WITHOUT modeling WoW effects.

Reuses the two actual v079 Hunter JSON2 cases with exact bytes/SHAs; one
additional Native witness varies the formerly unobserved mastery/vers stats.
Empirically measured per-stat affine transfer is used to create TWO official
T candidates for the existing v066/v064/v065 Native route and one adaptive
candidate. Every JSON2 target must match exactly; no effect/proc inspection.
At most 4 NEW 35-iteration Native calls, original two never rerun.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,subprocess,sys
import v046_static_item_cache as cache
import v061_scenario_contract as scenario
import v062_static_budget_bridge as budgets
import v063_numeric_injection as numeric
import v064_adaptive_evaluator_port as port
import v065_original_scheduler_native_bridge as engine
import v066_profile_neutral_preflight as preflight
import v077_generic_profile_bootstrap_readiness as readiness
import v078b_elemental_official_generic_native as official
import v079_hunter_ranged_generic_native as hunter
import v068_rogue_two_native_probe as pinned

SCHEMA="v079b_hunter_measured_affine_native_generic_route_v1"
ITERATIONS=35
FRESH_MAX=4

class Blocked(ValueError):pass
def need(x,reason):
    if not x:raise Blocked(reason)
def sha(x):return hashlib.sha256(x).hexdigest()
def read(p):return json.loads(pathlib.Path(p).read_text("utf8"))

def history(root,stable):
    root=pathlib.Path(root)
    old=read(root/"V079_RECEIPT.json")
    need(old["status"]=="BLOCKED_OR_PARTIAL"
         and "NONCONSTANT_NUMERIC_INJECTION_OFFSET" in old["error"]
         and old["new_native_this_invocation"]==2
         and old["origin"]["weapon_type"]=="ranged_no_offhand",
         "ORIGINAL_HUNTER_NONCONSTANT_TWO_NATIVE_NOT_PROVEN")
    prior=[]
    for i in range(2):
        p=root/"raw"/("case_%02d"%i)
        source=(p/"input.simc").read_bytes()
        raw=(p/"result.json").read_bytes()
        r=read(p/"native_receipt.json")
        need(sha(source)==r["input_sha256"] and
             sha(raw)==r["native_json_sha256"] and
             r["binary_sha256"]==pinned.BIN_SHA and
             sha(source)==old["raw_input_sha256s"][i],
             "OLD_NATIVE_RAW_JSON2_OR_INPUT_SHA_DRIFT")
        doc=json.loads(raw)
        obs=numeric.from_native(source.decode("utf8"),doc)
        need(obs["source"]["stable_sha256"]==stable,
             "REUSED_NATIVE_OTHER_PROFILE")
        need(len(doc["sim"]["players"])==1 and
             (doc["sim"]["players"][0].get("collected_data") or {}).get("dps",{}).get("count",0)>=20,
             "PRIOR_NATIVE_DPS_NOT_PRESENT")
        prior.append({"input":source.decode("utf8"),"native":doc,
           "raw_native_json":raw,"input_sha256":r["input_sha256"],
           "native_json_sha256":r["native_json_sha256"]})
    return prior

def make_third(reference,out):
    """Change exactly mastery and versatility, same raw CHMV total as prior."""
    original=numeric.input_parts(reference)
    raw=original["gear_override"]
    need(all(raw[k]==700 for k in scenario.STATS),
         "THIRD_WITNESS_BASE_NOT_700_EACH")
    target=dict(raw)
    target["mastery_rating"]-=50
    target["versatility_rating"]+=50
    lines=[]
    for line in reference.splitlines():
        key,sep,_=line.partition("=")
        stat=key.removeprefix("gear_")
        if sep and key.startswith("gear_") and stat in scenario.STATS:
            line=key+"="+str(target[stat])
        elif key=="json2":
            line="json2="+str((pathlib.Path(out)/"result.json").resolve())
        elif key=="iterations":
            line="iterations="+str(ITERATIONS)
        lines.append(line)
    source="\n".join(lines)+"\n"
    parsed=numeric.input_parts(source)
    need(parsed["stable_sha256"]==original["stable_sha256"]
         and parsed["gear_override"]==target
         and sum(target.values())==2800,
         "THIRD_WITNESS_PROFILE_OR_BUDGET_DRIFT")
    return source

def official_case(normalized,stat,cal,reference,out,requested,seen):
    """Find a neighboring exactly invertible rating TOTAL without new SimC."""
    errors=[]
    for delta in (0,1,-1,2,-2,3,-3,4,-4):
        target=dict(requested)
        target["crit_rating"]+=delta
        target["haste_rating"]-=delta
        if target in seen:continue
        try:
            proposal=port.make_request(normalized,stat,cal,reference,
                                  pinned.BIN_SHA,target,ITERATIONS,out)
            return proposal
        except numeric.InjectionError as exc:
            need("AFFINE_TARGET_RATING_NOT_REPRESENTABLE" in str(exc),
                 "OFFICIAL_TARGET_CALIBRATION_ERROR:"+str(exc))
            errors.append(str(exc))
    raise Blocked("NO_REPRESENTABLE_OFFICIAL_CHMV_NEAR_REQUEST:"+repr(errors))

def run(upstream,prior_dir,out,binary=None,cache_only=False):
    out=pathlib.Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    receipt=out/"V079B_RECEIPT.json"
    summary={"schema":SCHEMA,"status":"BLOCKED_OR_PARTIAL",
        "historical_original_real_native_reused":0,
        "fresh_native_calls_this_invocation":0,
        "fresh_native_cap":FRESH_MAX,"global_optimum_proven":False,
        "official_formula":"T=G+J+F"}
    try:
        source=pathlib.Path(upstream).read_text("utf8")
        ref,cfg,fill,origin=hunter.source_profile(source,out)
        stable=numeric.input_parts(ref)["stable_sha256"]
        prior=history(prior_dir,stable)
        summary.update({"status":"PASS_OLD_TWO_NATIVE_SHA_AND_AFFINE_BOOT_PLAN",
            "historical_original_real_native_reused":2,
            "original_native_json_sha256s":[x["native_json_sha256"] for x in prior],
            "profile_stable_sha256":stable,
            "race":cfg["character"]["race"],"weapon":origin["weapon_type"]})
        extra_dir=out/"extra_witness"
        third=make_third(ref,extra_dir)
        summary["third_witness_input_sha256"]=sha(third.encode("utf8"))
        if binary is None:
            engine.write_atomic(receipt,summary)
            return 0
        binary=pathlib.Path(binary).resolve()
        need(binary.is_file() and sha(binary.read_bytes())==pinned.BIN_SHA,
             "SIMC_BINARY_SHA_DRIFT")
        identity={"schema":SCHEMA,"prior_raw_sha":summary["original_native_json_sha256s"],
            "new_witness_input":summary["third_witness_input_sha256"],
            "binary_sha":pinned.BIN_SHA,"stable_profile":stable}
        seal=out/"V079B_IDENTITY.json"
        if seal.exists():need(read(seal)==identity,"DURABLE_V079B_IDENTITY_CHANGED")
        else:
            need(not extra_dir.exists() and not (out/"official").exists(),
                 "UNSEALED_PREEXISTING_NATIVE_DATA")
            engine.write_atomic(seal,identity)
        extra_dir.mkdir(exist_ok=True)
        inputpath=extra_dir/"input.simc"
        nativefile=extra_dir/"result.json"
        native_receipt=extra_dir/"native_receipt.json"
        if inputpath.exists():
            need(inputpath.read_bytes()==third.encode("utf8"),
                 "EXTRA_WITNESS_INPUT_CHANGED")
        else:inputpath.write_text(third,"utf8")
        attempt=out/"EXTRA_PROGRESS.json"
        progress={"schema":SCHEMA,"identity":identity,"native_attempts":0}
        if attempt.exists():
            old=read(attempt)
            need(old.get("schema")==SCHEMA and old.get("identity")==identity
                 and old.get("native_attempts") in (0,1),
                 "EXTRA_WITNESS_PROGRESS_TAMPER")
            progress["native_attempts"]=old["native_attempts"]
        else:engine.write_atomic(attempt,progress)
        if nativefile.exists() or native_receipt.exists():
            need(nativefile.is_file() and native_receipt.is_file(),
                 "PARTIAL_UNVERIFIED_THIRD_WITNESS")
            raw=nativefile.read_bytes()
            old=read(native_receipt)
            need(old["input_sha256"]==summary["third_witness_input_sha256"]
                 and old["native_json_sha256"]==sha(raw)
                 and old["binary_sha256"]==pinned.BIN_SHA,
                 "THIRD_NATIVE_CACHE_SHA_MISMATCH")
        else:
            need(not cache_only,"CACHE_ONLY_BLOCKS_NEW_THIRD_WITNESS")
            need(progress["native_attempts"]==0,"THIRD_NATIVE_ATTEMPT_EXHAUSTED")
            progress["native_attempts"]=1
            engine.write_atomic(attempt,progress)
            summary["fresh_native_calls_this_invocation"]+=1
            run=subprocess.run([str(binary),str(inputpath.resolve())],
                  cwd=binary.parent,stdin=subprocess.DEVNULL,
                  stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=240)
            (extra_dir/"stdout.txt").write_bytes(run.stdout)
            (extra_dir/"stderr.txt").write_bytes(run.stderr)
            need(run.returncode==0,"THIRD_SIMC_NATIVE_EXIT_"+str(run.returncode)+
                 "_SEE_UNMODIFIED_STDERR")
            need(nativefile.is_file(),"THIRD_NATIVE_JSON2_MISSING")
            raw=nativefile.read_bytes()
            engine.write_atomic(native_receipt,{
                 "input_sha256":summary["third_witness_input_sha256"],
                 "native_json_sha256":sha(raw),"binary_sha256":pinned.BIN_SHA})
        newdoc=json.loads(raw)
        numeric.from_native(third,newdoc)
        all_real=prior+[{"input":third,"native":newdoc,"raw_native_json":raw,
               "input_sha256":summary["third_witness_input_sha256"],
               "native_json_sha256":sha(raw)}]
        affine=numeric.calibrate_affine(all_real)
        summary["empirical_transfer"]=affine["empirical_affine_transfer"]
        summary["empirical_transfer_status"]=affine["status"]
        stat_cache=cache.empty_cache()
        for i,w in enumerate(all_real):
            cache.merge_native(stat_cache,cache.native_records(
                w["raw_native_json"],artifact_id="V079B_HUNTER_REAL_NATIVE_%02d"%i))
        normalized=scenario.normalize(cfg)
        stat=budgets.compile_static_budget(normalized,fill,stat_cache)
        need(stat["G_if_complete"] is not None
             and not stat["missing_nontrinket_static"]
             and not stat["missing_special_fixed_static"]
             and stat["budget"]["oil_stays_OUTSIDE_T"],
             "EMPIRICAL_TRANSFER_STATIC_G_UNKNOWN")
        T=stat["budget"]["T_official"]
        need(T==stat["G_if_complete"]+138+165,"OFFICIAL_T_FORMULA")
        summary.update({"G":stat["G_if_complete"],"J":138,"F":165,"T":T})
        off=out/"official";off.mkdir(exist_ok=True)
        options=official.targets(T,stat)
        requests=[]
        for i,t in enumerate(options):
            requests.append(official_case(normalized,stat,affine,ref,
                   off/("case_%02d"%i)/"result.json",t,
                   [req["target"] for req in requests]))
        off_identity={"schema":SCHEMA,"calibration":affine,
            "binary_sha":pinned.BIN_SHA,
            "case_keys":[r["case_key"] for r in requests]}
        off_seal=off/"OFFICIAL_IDENTITY.json"
        if off_seal.exists():
            need(read(off_seal)==off_identity,"OFFICIAL_AFFINE_IDENTITY_DRIFT")
        else:
            need(not any((off/("case_%02d"%i)).exists() for i in range(2))
                 and not (off/"adaptive").exists(),"UNSEALED_OFFICIAL_RESULT")
            engine.write_atomic(off_seal,off_identity)
        ledger=off/"V065_PROGRESS.json"
        progress={"schema":SCHEMA,"identity":off_identity,"native_attempts":0}
        if ledger.exists():
            old=read(ledger)
            need(old.get("schema")==SCHEMA and old.get("identity")==off_identity
                 and type(old.get("native_attempts")) is int
                 and 0<=old["native_attempts"]<=3,
                 "AFFINE_OFFICIAL_PROGRESS_TAMPER")
            progress["native_attempts"]=old["native_attempts"]
        else:engine.write_atomic(ledger,progress)
        scored=[]
        for i,req in enumerate(requests):
            obs=engine.execute_one(req,affine,binary,
                      off/("case_%02d"%i),progress,cache_only=cache_only)
            need(obs["target"]==obs["rating_actual"]
                 and obs["dps_samples"]>=20,"NATIVE_EMPIRICAL_TARGET_CHANGED")
            summary["fresh_native_calls_this_invocation"]+=int(
                obs["source"]=="NEW_NATIVE")
            scored.append(obs)
            summary["status"]="PARTIAL_OFFICIAL_AFFINE_NATIVE"
            summary["official_native_completed"]=len(scored)
            engine.write_atomic(receipt,summary)
        official_actual=[]
        for i,obs in enumerate(scored):
            folder=off/("case_%02d"%i)
            raw=(folder/"result.json").read_bytes()
            official_actual.append({"input":(folder/"input.simc").read_text("utf8"),
                "native":json.loads(raw),"raw_native_json":raw,
                "input_sha256":obs["input_sha256"],
                "native_json_sha256":obs["native_json_sha256"]})
        pre=preflight.prepare(cfg,fill,stat_cache,ref,
              official_actual,pinned.BIN_SHA,calibration_override=affine)
        need(pre["summary"]["status"]=="READY_NUMERIC_PROFILE_SCOPED"
             and pre["summary"]["T_official"]==T,
             "EMPIRICAL_AFFINE_V066_OFFICIAL_PREFLIGHT_NOT_READY")
        selected=preflight.propose_next(pre,ITERATIONS,
                       off/"adaptive"/"result.json",step=100)
        proposal=selected["case"]
        need(proposal["target"] not in [r["target"] for r in requests],
             "AFFINE_SCHEDULER_DUPLICATE_TARGET")
        new=engine.execute_one(proposal,affine,binary,
                  off/"adaptive",progress,cache_only=cache_only)
        need(new["target"]==new["rating_actual"]
             and new["dps_samples"]>=20,
             "AFFINE_ADAPTIVE_NATIVE_FINAL_RATING_DRIFT")
        summary["fresh_native_calls_this_invocation"]+=int(
             new["source"]=="NEW_NATIVE")
        summary.update({"status":"PASS_HUNTER_EMPIRICAL_AFFINE_FULL_GENERIC_NATIVE",
           "new_native_attempts_total_durable":progress["native_attempts"]+
               read(attempt)["native_attempts"],
           "historical_native_reused":2,
           "official_results":[{"target":z["target"],"rating_actual":z["rating_actual"],
               "dps_mean":z["dps_mean"],"dps_sem":z["dps_sem"],
               "dps_samples":z["dps_samples"],"source":z["source"],
               "native_json_sha256":z["native_json_sha256"]} for z in scored],
           "adaptive_result":{"target":new["target"],"rating_actual":new["rating_actual"],
               "dps_mean":new["dps_mean"],"dps_sem":new["dps_sem"],
               "dps_samples":new["dps_samples"],"source":new["source"],
               "native_json_sha256":new["native_json_sha256"]},
           "v066_preflight":pre["summary"]["status"],
           "previous_constant_calibration_failure_preserved":True,
           "cache_only_replay":cache_only,"global_optimum_proven":False})
    except Exception as e:
        summary["status"]="BLOCKED_OR_PARTIAL"
        summary["error"]=type(e).__name__+":"+str(e)
    engine.write_atomic(receipt,summary)
    print("V079B",summary["status"],"new_native",
          summary["fresh_native_calls_this_invocation"],
          "error",summary.get("error"),flush=True)
    return 0 if summary["status"].startswith("PASS") else 3

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",required=True,type=pathlib.Path)
    p.add_argument("--original-failed-native",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    p.add_argument("--binary",type=pathlib.Path)
    p.add_argument("--cache-only",action="store_true")
    a=p.parse_args(argv)
    return run(a.upstream,a.original_failed_native,a.out,a.binary,a.cache_only)

if __name__=="__main__":sys.exit(main())
