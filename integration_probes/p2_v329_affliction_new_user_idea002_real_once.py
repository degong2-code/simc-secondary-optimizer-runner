#!/usr/bin/env python3
"""v329 one fresh Affliction user, actual IDEA-002 v306 vs v328 SimC Native.

Source is built only once by product P1 and shared by four independently sealed
policy arms. Region ablation v306/v328 has fixed equal 64 Native/4520 requested
iterations; original v290/v318 arms are background checks, not equal-iteration
comparators. Preselected top 2 each get independent holdout N640x2 without
sharing stale previous-profile DPS cache.
"""
from __future__ import annotations
import hashlib,json,math,os,pathlib,re,subprocess,time,zipfile

from integration_probes import p2_v319_new_windwalker_v290_v318_real_once as fresh
from integration_probes import p2_v324_balance_new_user_variable_n_real_once as native_input
from runner import v291_durable_multiscale_native_runner as durable
from runner import v306_seed_retained_coarse_escape_regions as baseline
from runner import v328_idea002_evidence_gated_radius as idea
from runner import v316_optin_case_time_trace as trace

CASE="affliction_warlock_4ordinary_auto_T"
SPEC=("warlock","affliction")
ROOT=pathlib.Path("out/p2_v329_new_affliction_idea002").resolve()
SCHEMA="p2_v329_new_affliction_idea002_native_ab_v1"
STATS=("crit_rating","haste_rating","mastery_rating","versatility_rating")
BUDGET=64
START_GLOBAL=16
CONFIRM=8
ITER_SCOUT=35
ITER_CONFIRM=320
FIXED_ITERATIONS=(BUDGET-CONFIRM)*ITER_SCOUT+CONFIRM*ITER_CONFIRM
ARMS=(("v306_seed_retained",baseline.SCHEMA,True,False),
      ("v328_idea002_radius",idea.SCHEMA,False,True))

class V329Blocked(RuntimeError):pass
def need(ok,reason):
    if not ok:raise V329Blocked("V329_"+reason)
def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def save(root,record):
    p=root/"IDEA002_PROGRESS.json"
    p.write_text(json.dumps(record,indent=2,sort_keys=True,
                            ensure_ascii=False,allow_nan=False)+"\n",
                 encoding="utf8")
def vector(row):
    return tuple(row["target"][k] for k in STATS)

def archive_folder(folder,out):
    with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,
                         compresslevel=5) as z:
        for p in sorted(folder.rglob("*")):
            if p.is_file() and not p.is_symlink():
                z.write(p,p.relative_to(folder))

def run_ab(doc,binary,root,context,flask):
    need(doc["status"] in
         ("COMPLETE_TWO_ARMS_EQUAL_CALLS_AND_ITERATIONS",
          "COMPLETE_TWO_ARMS_EQUAL_CALLS_ITERATIONS_UNEQUAL")
         and (doc["character"]["character_class"],
              doc["character"]["character_spec"])==SPEC
         and doc["manual_final_T"] is None
         and doc["fresh_profile_generated_once_for_both_arms"] is True
         and doc["source_from_old_completed_simc_profile"] is False
         and doc["historical_dps_native_cache_imported"] is False
         and doc["environment_native_calls"]<=3
         and doc["auto_final_T"]==doc["environment_budget"]["T"]
         and doc["environment_budget"]["B"]==
             sum(doc["environment_budget"][x] for x in ("G","J","F"))
         and doc["environment_budget"]["T"]>0
         and sha(binary)==doc["simc_binary_sha256"]==
             fresh.fresh.BINARY_SHA
         and doc["source_profile_sha256"]==
             context["identity"]["source_profile_sha256"],
         "NEW_AFFLICTION_P1_AUTO_GJFO_SOURCE_REQUIRED")
    report={"schema":SCHEMA,"status":"STARTED",
            "source_profile_sha256":doc["source_profile_sha256"],
            "binary_sha256":sha(binary),
            "manual_final_T":None,
            "actual_auto_T":doc["auto_final_T"],
            "environment_budget":doc["environment_budget"],
            "initial_global_calls":START_GLOBAL,
            "regional_and_global_reserve_calls":BUDGET-START_GLOBAL-CONFIRM,
            "confirmation_calls":CONFIRM,
            "scout_N":ITER_SCOUT,"confirmation_N":ITER_CONFIRM,
            "expected_iterations_per_region_policy":FIXED_ITERATIONS,
            "no_previous_completed_profile_or_DPS_cache":True,
            "arms":{},"holdout":{},
            "global_optimum_proven":False}
    save(root,report)
    all_rows={}
    for name,expected,old_flag,new_flag in ARMS:
        folder=root/name
        started=time.monotonic()
        result=durable.run(
            context,flask,binary,folder,max_native_calls=BUDGET,
            max_new_native_this_invocation=BUDGET,
            max_elapsed_seconds=1500,cache_only=False,
            case_timing_trace=True,
            adaptive_initial_global_calls=START_GLOBAL,
            adaptive_confirmation_calls=CONFIRM,
            seed_retained_coarse_escape_regions=old_flag,
            idea002_radius_optin=new_flag,open_folder=False)
        elapsed=time.monotonic()-started
        rows=durable._load_journal(folder/"V291_JOURNAL.jsonl")
        need(result["policy"]==expected and len(rows)==BUDGET
             and result["new_native_this_invocation"]==BUDGET
             and sum(r["iterations"] for r in rows)==FIXED_ITERATIONS
             and sum(r["phase"]=="precision" for r in rows)==CONFIRM
             and sum(r["phase"]=="scout" for r in rows)==BUDGET-CONFIRM
             and sum(r["adaptive_stage"]=="global_initial" for r in rows)==
                 START_GLOBAL
             and all(r["source"]=="NEW_NATIVE" and
                     r["samples"] in (r["iterations"]-1,r["iterations"])
                     and sum(r["target"].values())==doc["auto_final_T"]
                     and r["final_T"]==r["target"] for r in rows),
             "REGIONAL_REAL_NATIVE_CALLS_AND_EXACT_ITERATIONS_REQUIRED")
        for r in rows:
            inp=folder/"cases"/("case_%05d"%r["index"])/"native"/"input.simc"
            original=inp.parent/"result.json"
            need(sha(inp)==r["input_sha256"] and
                 sha(original)==r["native_sha256"],
                 "EACH_ORIGINAL_NATIVE_INPUT_JSON_SHA_DRIFT")
        times=trace.load(folder/trace.NAME,rows,
                         trace.identity_hash(folder/"V291_SESSION.json"))
        ck=trace.checkpoints(times,rows,ITER_CONFIRM)
        replay=durable.run(
            context,flask,binary,folder,max_native_calls=BUDGET,
            max_new_native_this_invocation=0,cache_only=True,
            case_timing_trace=True,
            adaptive_initial_global_calls=START_GLOBAL,
            adaptive_confirmation_calls=CONFIRM,
            seed_retained_coarse_escape_regions=old_flag,
            idea002_radius_optin=new_flag,open_folder=False)
        need(replay["new_native_this_invocation"]==0,
             "CACHE_ONLY_REPLAY_MUST_HAVE_NO_NATIVE")
        precision=sorted((r for r in rows if r["phase"]=="precision"),
                         key=lambda r:(-r["dps_mean"],r["case_key"]))
        report["arms"][name]={
            "policy":result["policy"],
            "complete_original_new_native":len(rows),
            "requested_total_iterations":sum(r["iterations"] for r in rows),
            "elapsed_policy_seconds":round(elapsed,6),
            "initial_global_vectors":[r["target"] for r in rows
                                      if r["adaptive_stage"]=="global_initial"],
            "regional_scout_calls":sum(r["adaptive_stage"]=="regional"
                                       for r in rows),
            "global_reserve_calls":sum(r["adaptive_stage"]=="global_reserve"
                                       for r in rows),
            "distinct_region_ids":len({r["region_id"] for r in rows
                                       if r["adaptive_stage"]=="regional"}),
            "unique_scout_CHMV":len({vector(r) for r in rows
                                    if r["phase"]=="scout"}),
            "best_confirmed_CHMV":precision[0]["target"],
            "best_confirmed_DPS":precision[0]["dps_mean"],
            "best_confirmed_SEM":precision[0]["dps_sem"],
            "320_confirmed_candidate_count":len(precision),
            "v316_native_timing_checkpoints":ck,
            "journal_sha256":sha(folder/"V291_JOURNAL.jsonl"),
            "session_sha256":sha(folder/"V291_SESSION.json"),
            "cache_only_new_native":0,
        }
        all_rows[name]=rows
        z=root/(name+"_original_native.zip")
        archive_folder(folder,z)
        report["arms"][name]["original_native_zip_sha256"]=sha(z)
        save(root,report)
        print("V329_IDEA002_REAL_NATIVE_ARM",json.dumps({
             "name":name,"new_native":len(rows),
             "iterations":FIXED_ITERATIONS,
             "confirmed_DPS":precision[0]["dps_mean"],
             "confirmed_CHMV":precision[0]["target"],
             "wall":round(elapsed,6)},sort_keys=True),flush=True)
    a,b=(report["arms"][x] for x,_,_,_ in ARMS)
    need(a["initial_global_vectors"]==b["initial_global_vectors"]
         and a["requested_total_iterations"]==
             b["requested_total_iterations"]==FIXED_ITERATIONS
         and a["complete_original_new_native"]==
             b["complete_original_new_native"]==BUDGET,
         "NOT_FAIR_EQUAL_INITIAL_CHMV_AND_ITERATION_BUDGET")
    different=sum(vector(x)!=vector(y) for x,y in
                  zip(all_rows[ARMS[0][0]],all_rows[ARMS[1][0]]))
    report["comparison"]={
        "same_exact_new_profile":True,
        "same_initial_global_CHMV_order":True,
        "equal_requests":True,"equal_requested_iterations":True,
        "first_different_case_index":next((
            i for i,(x,y) in enumerate(zip(
                all_rows[ARMS[0][0]],all_rows[ARMS[1][0]]))
            if vector(x)!=vector(y)),None),
        "different_CHMV_positions_of_64":different,
        "independent_simc_seeds_not_paired":True,
        "no_algorithm_quality_winner_yet":True}
    save(root,report)
    # Independently measure a preselected top-two shortlist from each arm;
    # common CHMV deduplicated, no duplicate Native at 640.
    selected={}
    for name,_,_,_ in ARMS:
        rows=all_rows[name]
        precision=sorted((r for r in rows if r["phase"]=="precision"),
                         key=lambda r:(-r["dps_mean"],r["case_key"]))
        for r in precision[:2]:
            selected.setdefault(vector(r),(name,r))
    holdroot=root/"holdout_new_native"
    holdroot.mkdir()
    for pos,(target,(arm,row)) in enumerate(sorted(selected.items())):
        original=(root/arm/"cases"/("case_%05d"%row["index"])/
                  "native"/"input.simc")
        need(sha(original)==row["input_sha256"],
             "HOLDOUT_MUST_USE_FRESH_320_SOURCE_INPUT")
        results=[]
        for rep in range(2):
            folder=holdroot/("candidate_%02d_rep_%d"%(pos,rep))
            folder.mkdir()
            output=folder/"result.json"
            from_source=native_input.update_input(
                original.read_text(encoding="utf8"),640,output,
                source_iterations=320,allowed_N=(640,))
            inp=folder/"input.simc"
            inp.write_text(from_source,encoding="utf8")
            started=time.monotonic()
            cp=subprocess.run([str(binary),str(inp.resolve())],
                   cwd=binary.parent,stdin=subprocess.DEVNULL,
                   stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                   timeout=240,check=False)
            wall=time.monotonic()-started
            (folder/"stdout.txt").write_bytes(cp.stdout)
            (folder/"stderr.txt").write_bytes(cp.stderr)
            need(cp.returncode==0 and output.is_file() and
                 0<output.stat().st_size<50_000_000,
                 "INDEPENDENT_HOLDOUT_NATIVE_FAILED")
            data=json.loads(output.read_bytes())
            version=data.get("git_revision")
            sim=data.get("sim") or {}
            players=sim.get("players") or []
            options=sim.get("options") or {}
            need(type(version) is str and len(version)>=10
                 and doc["revision"].startswith(version)
                 and options.get("iterations")==640 and len(players)==1
                 and str(players[0].get("specialization","")).lower()
                    in ("affliction","affliction warlock"),
                 "HOLDOUT_SOURCE_SPEC_SIMC_REVISION")
            dps=(players[0].get("collected_data") or {}).get("dps") or {}
            need(dps.get("count")==639
                 and type(dps.get("mean")) in (int,float)
                 and type(dps.get("mean_std_dev")) in (int,float)
                 and math.isfinite(dps["mean"]) and
                 math.isfinite(dps["mean_std_dev"]) and
                 dps["mean_std_dev"]>=0,
                 "REAL_HOLDOUT_NATIVE_SAMPLES_SEM_REQUIRED")
            results.append({
                "source_arm":arm,"CHMV":dict(zip(STATS,target)),
                "iterations":640,"samples":dps["count"],
                "DPS":dps["mean"],"SEM":dps["mean_std_dev"],
                "seed":options.get("seed"),"wall_seconds":round(wall,6),
                "native_sha256":sha(output),"input_sha256":sha(inp)})
        need(results[0]["seed"]!=results[1]["seed"] and
             all(type(r["seed"]) is int for r in results),
             "HOLDOUT_INDEPENDENT_SIMC_SEEDS_REQUIRED")
        report["holdout"]["/".join(map(str,target))]={
            "same_profile":True,"two_independent_native":results,
            "heldout_mean_DPS":sum(r["DPS"] for r in results)/2,
            "heldout_combined_SEM":
                math.hypot(*(r["SEM"] for r in results))/2}
        save(root,report)
    z=root/"independent_640_holdout_original.zip"
    archive_folder(holdroot,z)
    report["holdout_original_native_zip_sha256"]=sha(z)
    report["additional_holdout_native"]=2*len(selected)
    report["status"]="REAL_SAME_PROFILE_TWO_REGIONAL_POLICIES_AND_HOLDOUT_COMPLETE"
    report["global_optimum_proven"]=False
    report["familywise_95_superiority_proven"]=False
    save(root,report)
    print("V329_IDEA002_COMPLETE",json.dumps({
        "status":report["status"],"source_sha":doc["source_profile_sha256"],
        "total_regional_native":128,
        "holdout_native":report["additional_holdout_native"],
        "comparison":report["comparison"],
        "original_zip_sha":{k:report["arms"][k]["original_native_zip_sha256"]
                             for k in report["arms"]}},sort_keys=True),flush=True)
    return report

def main():
    need(os.getenv("P2_V329_IDEA002_FRESH_AFFLICTION_ONCE")=="1",
         "NEW_SPEC_NATIVE_ONCE_OPT_IN_REQUIRED")
    # v329's 267 Native receipts belong exclusively to v328-v1 source code.
    # v328-v2 must receive a fresh campaign id/new spec, never silently
    # reinterpret this historical, SHA-sealed pilot as a v2 experiment.
    need(idea.SCHEMA=="v328_idea002_evidence_gated_radius_optin_v1",
         "PILOT_V329_V1_EXACT_SOURCE_RETIRED")
    return fresh.main(
        case_id=CASE,expected_spec=SPEC,
        output_root=ROOT,receipt_path=ROOT/"receipt.json",
        campaign_schema=SCHEMA,
        required_env="P2_V329_IDEA002_FRESH_AFFLICTION_ONCE",
        post_run_context_hook=run_ab)
if __name__=="__main__":
    main()
