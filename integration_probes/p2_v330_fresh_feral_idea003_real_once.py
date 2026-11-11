#!/usr/bin/env python3
"""v330 fresh Feral, one v306 baseline, one v330 counterfactual prefix fork.

Only current-campaign authenticated observations are shared. Original JSON2
bytes are revalidated against source and destination exact requests; only
json2 location changes, and imported rows have explicit portable provenance.
Logical per-arm budgets include the shared prefix; physical Native calls do not.
"""
from __future__ import annotations
import hashlib,json,math,os,pathlib,re,subprocess,time,zipfile
from integration_probes import p2_v319_new_windwalker_v290_v318_real_once as fresh
from integration_probes import p2_v324_balance_new_user_variable_n_real_once as native_input
from runner import v291_durable_multiscale_native_runner as durable
from runner import v306_seed_retained_coarse_escape_regions as baseline
from runner import v330_idea003_stratified_reserve as stratified
from runner import v316_optin_case_time_trace as trace
from runner import v063_numeric_injection as numeric

CASE="feral_druid_4ordinary_auto_T"
SPEC=("druid","feral")
ROOT=pathlib.Path("out/p2_v330_feral_idea003").resolve()
SCHEMA="p2_v330_fresh_feral_idea003_same_history_fork_v1"
CAP,INITIAL,CONFIRM=64,16,8
N_SCOUT,N_CONFIRM,N_HOLD=35,320,640
TOTAL_ITER=(CAP-CONFIRM)*N_SCOUT+CONFIRM*N_CONFIRM
KEYS=("index","target","iterations","phase",*durable.V304_METADATA,"hybrid_method")
STATS=baseline.base.STATS
def need(ok,reason):
    if not ok: raise RuntimeError("V330_"+reason)
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def file_sha(path):
    return sha(path.read_bytes())
def save(root,doc):
    durable.atomic(root/"IDEA003_PROGRESS.json",doc)
def vector(row):
    return tuple(row["target"][k] for k in STATS)
def archive(folder,dest):
    with zipfile.ZipFile(dest,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
        for p in sorted(folder.rglob("*")):
            if p.is_file() and not p.is_symlink():
                z.write(p,p.relative_to(folder))
    return file_sha(dest)
def opts(flag):
    return dict(max_native_calls=CAP,adaptive_initial_global_calls=INITIAL,
        adaptive_confirmation_calls=CONFIRM,seed_retained_coarse_escape_regions=not flag,
        idea003_stratified_reserve_optin=flag,open_folder=False,case_timing_trace=True)
def proposal_kwargs(seal):
    return dict(total=seal["B"],lower=tuple(seal["lower"][k] for k in STATS),
        upper=tuple(seal["upper"][k] for k in STATS),max_native_calls=CAP,
        scout_iterations=N_SCOUT,confirmation_iterations=N_CONFIRM,
        initial_global_calls=INITIAL,confirmation_calls=CONFIRM)

def matching_prefix(rows,kw):
    """Identify first changed proposal on exactly the same observations."""
    for i,row in enumerate(rows):
        result=stratified.next_plan(rows[:i],**kw)
        action=result["next_request"]
        need(action is not None,"ALTERNATE_POLICY_PREMATURE_STOP")
        if any(row[k]!=action[k] for k in KEYS if k!="index"):
            need(row["adaptive_stage"]==action["adaptive_stage"]=="global_reserve"
                 and all(row[k]==action[k] for k in KEYS
                         if k not in ("index","target")),
                 "NON_RESERVE_CHANGE_ON_IDENTICAL_HISTORY")
            return i,action
    return len(rows),None

def import_prefix(context,flask,binary,origin,dest,rows,prefix):
    """Research-only fork of a fresh, same-campaign v306 journal.
    Reuse the v292 acceptance/rekey pattern without admitting old profiles.
    """
    need(INITIAL<=prefix<=CAP and len(rows)==CAP and not dest.exists(),
         "SOURCE_PREFIX_OR_DESTINATION")
    pre=durable.run(context,flask,binary,dest,
          max_new_native_this_invocation=0,cache_only=True,**opts(True))
    need(pre["completed_cases"]==0 and pre["new_native_this_invocation"]==0,
         "NEW_SEALED_EMPTY_FORK_REQUIRED")
    original_seal=durable.read_json(origin/"V291_SESSION.json")
    new_seal=durable.read_json(dest/"V291_SESSION.json")
    normalized=json.loads(json.dumps(new_seal))
    need(normalized["experimental_adaptive_regions"].pop("idea003_v330",None)
         is not None and normalized==original_seal,
         "SOURCE_SESSION_IDENTITY_OTHER_THAN_POLICY_CHANGED")
    pending=dest/"V291_PENDING.json"
    need(pending.is_file() and all(durable.read_json(pending)[k]==rows[0][k]
                                  for k in KEYS),"FIRST_SHARED_PLAN_NOT_EQUAL")
    calibration={"native_revision":context["identity"]["revision"]}
    pending.unlink()
    for row in rows[:prefix]:
        plan={k:row[k] for k in KEYS}
        oldreq,oldfolder=durable._request(context,flask,origin,plan)
        actual,_=durable._verified_row(oldreq,binary,oldfolder,calibration,allow_cache=True)
        need(row["source"]=="NEW_NATIVE" and
             durable._compact(oldreq,actual,row["source"],plan)==row,
             "ORIGINAL_EXACT_CASE_JOURNAL_DRIFT")
        newreq,newfolder=durable._request(context,flask,dest,plan)
        raw=(oldfolder/"result.json").read_bytes()
        oldinput=(oldfolder/"input.simc").read_bytes()
        # Exact identity including all non-json2 bytes, stronger than
        # input_parts alone (which also excludes iteration and gear fields).
        def strip_json2(s):
            return re.sub(r"(?m)^json2=.+$","json2=PATH",s)
        need(sha(oldinput)==row["input_sha256"] and
             strip_json2(oldinput.decode())==strip_json2(newreq["input"])
             and numeric.input_parts(oldreq["input"])==numeric.input_parts(newreq["input"])
             and oldreq["case_key"]==newreq["case_key"]==row["case_key"]
             and oldreq["iterations"]==newreq["iterations"]==row["iterations"]
             and oldreq["target"]==newreq["target"]
             and sha(raw)==row["native_sha256"],"PATH_ONLY_REKEY_DRIFT")
        native_doc=json.loads(raw)
        newactual=durable.oil.ingest_native(newreq,native_doc,raw)
        receipt=durable.engine.evaluator.ingest_native(newreq,native_doc,calibration,raw)
        newactual["simc_seed"]=actual["simc_seed"]
        receipt["simc_seed"]=actual["simc_seed"]
        need(receipt["native_json_sha256"]==row["native_sha256"] and
             newactual["native_json_sha256"]==row["native_sha256"],
             "UNMODIFIED_JSON2_REVALIDATION_DRIFT")
        imported=durable._compact(newreq,newactual,"PORTABLE_REVALIDATED_NATIVE",plan)
        need(all(imported[k]==row[k] for k in row
                 if k not in ("source","input_sha256")),
             "SHARED_DPS_SEM_SEED_NOT_IDENTICAL")
        newfolder.mkdir(parents=True,exist_ok=True)
        (newfolder/"input.simc").write_bytes(newreq["input"].encode())
        (newfolder/"result.json").write_bytes(raw)
        durable.atomic(newfolder/"native_receipt.json",receipt)
        durable.atomic(newfolder.parent/"V065_PROGRESS.json",
            {"native_attempts":1,"status":"PORTABLE_VERIFIED_NATIVE_NO_NEW_SIMC"})
        durable.atomic(newfolder.parent/"V330_ORIGIN.json",{
            "source_campaign":"same_new_profile_current_baseline_only",
            "original_index":row["index"],"original_case_key":row["case_key"],
            "original_input_sha256":row["input_sha256"],
            "original_json2_sha256":row["native_sha256"],
            "original_receipt_sha256":file_sha(oldfolder/"native_receipt.json"),
            "new_input_sha256":newreq["input_sha256"],"native_reexecuted":False})
        durable._append_journal(dest/"V291_JOURNAL.jsonl",imported)
    # Native0; independent v291 validates every imported receipt and plans
    # the very first differing global reserve from identical history.
    replay=durable.run(context,flask,binary,dest,
            max_new_native_this_invocation=0,cache_only=True,**opts(True))
    need(replay["completed_cases"]==prefix and replay["new_native_this_invocation"]==0,
         "PREFIX_CACHE_REPLAY_NOT_EXACT")
    return replay

def arm_summary(root,folder,result,*,prefix,total):
    rows=durable._load_journal(folder/"V291_JOURNAL.jsonl")
    expected=baseline.SCHEMA if prefix==0 else stratified.SCHEMA
    # Baseline's prefix is zero. Stratified may theoretically share all rows.
    need(result["policy"]==expected and len(rows)==CAP
         and result["new_native_this_invocation"]==CAP-prefix
         and sum(r["iterations"] for r in rows)==TOTAL_ITER
         and all(r["source"]==("PORTABLE_REVALIDATED_NATIVE" if i<prefix
                               else "NEW_NATIVE") for i,r in enumerate(rows))
         and all(sum(r["target"].values())==total and r["target"]==r["final_T"]
                 and r["samples"] in (r["iterations"]-1,r["iterations"])
                 and type(r["simc_seed"]) is int for r in rows),
         "COMPLETE_TYPED_NATIVE_POLICY_LOGICAL_BUDGET")
    scouts=[r for r in rows if r["phase"]=="scout"]
    precision=sorted([r for r in rows if r["phase"]=="precision"],
                     key=lambda r:(-r["dps_mean"],vector(r)))
    need(len(scouts)==CAP-CONFIRM and len(precision)==CONFIRM
         and len({vector(r) for r in scouts})==len(scouts),
         "SCOUT_CONFIRM_CADENCE_OR_DUPLICATE")
    for r in rows:
        folder_case=durable.case_folder(folder,r["index"])
        need(file_sha(folder_case/"input.simc")==r["input_sha256"]
             and file_sha(folder_case/"result.json")==r["native_sha256"],
             "ORIGINAL_INPUT_JSON2_SHA_MISMATCH")
    times=trace.load(folder/trace.NAME,rows,trace.identity_hash(folder/"V291_SESSION.json"))
    if prefix==0:
        need(len(times)==CAP,"BASELINE_TRACE_MISSING")
    else:
        need(len(times)==CAP-prefix and all(t["index"]>=prefix for t in times),
             "FORK_TRACE_MUST_NOT_INVENT_SHARED_TIMINGS")
    seal=durable.read_json(folder/"V291_SESSION.json")
    kw=proposal_kwargs(seal)
    coverage=stratified.coverage(rows,total=kw["total"],lower=kw["lower"],upper=kw["upper"])
    best=precision[0]
    reserve=[r for r in scouts if r["adaptive_stage"]=="global_reserve"]
    summary={"policy":result["policy"],"logical_native":CAP,"new_native":CAP-prefix,
       "shared_verified_prefix":prefix,"logical_iterations":TOTAL_ITER,
       "actual_new_iterations":sum(r["iterations"] for r in rows[prefix:]),
       "scout_count":len(scouts),"confirmation_count":len(precision),
       "coverage":coverage,"reserve_CHMV":[list(vector(r)) for r in reserve],
       "best_confirmed":{"CHMV":list(vector(best)),"DPS":best["dps_mean"],"SEM":best["dps_sem"]},
       "top_two_confirmed":[list(vector(r)) for r in precision[:2]],
       "best_reserve_scout":list(vector(max(reserve,key=lambda r:r["dps_mean"]))) if reserve else None,
       "journal_sha256":file_sha(folder/"V291_JOURNAL.jsonl"),
       "seal_sha256":file_sha(folder/"V291_SESSION.json"),
       "original_native_zip_sha256":archive(folder,root/(folder.name+"_original_native.zip")),
       "global_optimum_proven":False}
    return rows,precision,reserve,times,summary

def holdout(doc,binary,root,arms):
    # Freeze 2 top confirmations and 1 top reserve scout per arm BEFORE
    # any holdout is observed. Same CHMV evaluated once per independent seed.
    chosen={}
    for name,(rows,precision,reserve,times,summary) in arms.items():
        shortlist=precision[:2]+([max(reserve,key=lambda r:r["dps_mean"])] if reserve else [])
        for row in shortlist:
            chosen.setdefault(vector(row),(name,row))
    path=root/"holdout"
    path.mkdir()
    result={}
    all_seeds={r["simc_seed"] for rows,*_ in arms.values() for r in rows}
    for idx,(v,(name,row)) in enumerate(sorted(chosen.items())):
        original=durable.case_folder(root/name,row["index"])/"input.simc"
        need(file_sha(original)==row["input_sha256"],"HOLDOUT_SOURCE_INPUT_DRIFT")
        reps=[]
        for rep in range(2):
            sub=path/("candidate_%02d_rep_%d"%(idx,rep))
            sub.mkdir()
            out=sub/"result.json";inp=sub/"input.simc"
            inp.write_text(native_input.update_input(original.read_text(),N_HOLD,out,
                            source_iterations=row["iterations"],allowed_N=(N_HOLD,)),
                           encoding="utf8")
            started=time.monotonic()
            cp=subprocess.run([str(binary),str(inp.resolve())],cwd=binary.parent,
                 stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                 timeout=240,check=False)
            wall=time.monotonic()-started
            (sub/"stdout.txt").write_bytes(cp.stdout);(sub/"stderr.txt").write_bytes(cp.stderr)
            need(cp.returncode==0 and out.is_file() and 0<out.stat().st_size<50_000_000,
                 "HOLDOUT_SIMC_NATIVE_FAILED")
            raw=out.read_bytes();d=json.loads(raw);sim=d["sim"];o=sim["options"];players=sim["players"]
            dps=players[0]["collected_data"]["dps"]
            seed=o.get("seed");rev=d.get("git_revision")
            need(type(rev) is str and len(rev)>=10 and doc["revision"].startswith(rev)
                 and o["iterations"]==N_HOLD and len(players)==1
                 and str(players[0].get("specialization","")).lower().startswith("feral")
                 and dps["count"]==N_HOLD-1 and type(seed) is int and seed not in all_seeds
                 and all(type(dps[k]) in (int,float) and math.isfinite(dps[k]) and dps[k]>=0
                         for k in ("mean","mean_std_dev")),
                 "HOLDOUT_NATIVE_SPEC_SEED_SAMPLES_DPS_DRIFT")
            all_seeds.add(seed)
            reps.append({"DPS":dps["mean"],"SEM":dps["mean_std_dev"],"seed":seed,
                         "iterations":N_HOLD,"samples":dps["count"],"wall_seconds":wall,
                         "input_sha256":file_sha(inp),"native_sha256":sha(raw)})
        result["/".join(map(str,v))]={"CHMV":list(v),"source_arm":name,
             "source_case_index":row["index"],"source_N":row["iterations"],"replicates":reps,
             "mean_DPS":sum(x["DPS"] for x in reps)/2,
             "combined_SEM":math.hypot(*(x["SEM"] for x in reps))/2}
        durable.atomic(root/"HOLDOUT_PROGRESS.json",result)
    return result,archive(path,root/"holdout_original_native.zip")

def run(doc,binary,root,context,flask):
    need(doc["status"]=="FRESH_PRODUCT_SOURCE_READY_NO_DPS_NATIVE"
         and not doc["arms"] and doc["manual_final_T"] is None
         and (doc["character"]["character_class"],doc["character"]["character_spec"])==SPEC
         and doc["auto_final_T"]==doc["environment_budget"]["T"]
         and doc["source_profile_sha256"]==context["identity"]["source_profile_sha256"],
         "FRESH_PRODUCT_SOURCE_ONLY_REQUIRED")
    total=doc["auto_final_T"]
    report={"schema":SCHEMA,"status":"STARTED","new_profile_sha256":doc["source_profile_sha256"],
            "budget":doc["environment_budget"],"initial_CHMV_count":INITIAL,
            "scout_iterations_per_CHMV":N_SCOUT,"confirm_iterations_per_CHMV":N_CONFIRM,
            "logical_per_arm":CAP,"logical_iterations_per_arm":TOTAL_ITER,"arms":{}}
    save(root,report)
    a=root/"v306_baseline";b=root/"v330_stratified"
    start=time.monotonic()
    a_result=durable.run(context,flask,binary,a,max_new_native_this_invocation=CAP,
                         max_elapsed_seconds=1200,**opts(False))
    a_elapsed=time.monotonic()-start
    old=arm_summary(root,a,a_result,prefix=0,total=total)
    report["arms"][a.name]=dict(old[-1],measured_full_wall_seconds=a_elapsed)
    save(root,report)
    kw=proposal_kwargs(durable.read_json(a/"V291_SESSION.json"))
    prefix,first=matching_prefix(old[0],kw)
    report["shared_prefix_count"]=prefix
    report["first_divergent_CHMV_index0"]=prefix if first else None
    report["first_divergent_old_CHMV"]=old[0][prefix]["target"] if first else None
    report["first_divergent_new_CHMV"]=first["target"] if first else None
    report["first_divergence_is_reserve_only_on_identical_history"]=bool(first)
    save(root,report)
    import_prefix(context,flask,binary,a,b,old[0],prefix)
    started=time.monotonic()
    b_result=durable.run(context,flask,binary,b,max_new_native_this_invocation=CAP-prefix,
                         max_elapsed_seconds=1200,**opts(True))
    b_elapsed=time.monotonic()-started
    new=arm_summary(root,b,b_result,prefix=prefix,total=total)
    need(new[0][:prefix] and all(
          all(x[k]==y[k] for k in x if k not in ("source","input_sha256"))
          for x,y in zip(old[0][:prefix],new[0][:prefix])),
          "FORK_ORIGINAL_DPS_SEM_SEED_PREFIX_CHANGED")
    report["arms"][b.name]=dict(new[-1],measured_fork_invocation_wall_seconds=b_elapsed)
    report["same_logical_native_iterations_budget"]=True
    report["actual_policy_new_native"]=2*CAP-prefix
    report["initial_shared_native_measurements_reused"]=prefix
    report["shared_seed_prefix_identical"]=True
    report["postfork_independent_seed_noise_remains"]=True
    # Comparable instrumented post-fork time only; do not pretend a shared
    # prefix replay is an independently measured complete optimizer runtime.
    prefix_elapsed=old[3][prefix-1]["invocation_elapsed_seconds"]
    report["wall"]={"baseline_full_trace_seconds":old[3][-1]["invocation_elapsed_seconds"],
       "baseline_postfork_trace_seconds":old[3][-1]["invocation_elapsed_seconds"]-prefix_elapsed,
       "stratified_postfork_trace_seconds":new[3][-1]["invocation_elapsed_seconds"] if new[3] else 0.,
       "shared_prefix_trace_seconds":prefix_elapsed,
       "not_independent_full_wall_comparison":True}
    for name,flag in ((a.name,False),(b.name,True)):
        replay=durable.run(context,flask,binary,root/name,
            max_new_native_this_invocation=0,cache_only=True,**opts(flag))
        need(replay["completed_cases"]==CAP and replay["new_native_this_invocation"]==0,
             "FINAL_CACHE_ONLY_REPLAY_NOT_ZERO_NATIVE")
        report["arms"][name]["cache_only_new_native"]=0
    save(root,report)
    data,zipsha=holdout(doc,binary,root,{a.name:old,b.name:new})
    best=max(x["mean_DPS"] for x in data.values())
    report["holdout"]={"shortlist":data,"original_zip_sha256":zipsha,
                       "new_native":2*len(data),"best_of_shortlist_DPS":best,
                       "operational_near_band":.005,"global_optimum_proven":False}
    for name,arm in ((a.name,old),(b.name,new)):
        observed={vector(r):r["index"] for r in arm[0] if r["phase"]=="scout"}
        good=[v for v,x in data.items() if x["mean_DPS"]>=best*.995
              and tuple(x["CHMV"]) in observed]
        discovered=[x for x in data.values() if tuple(x["CHMV"]) in observed]
        top=report["arms"][name]["best_confirmed"]["CHMV"]
        held=data["/".join(map(str,top))]
        report["arms"][name].update(
             holdout_of_320_observed_winner=held["mean_DPS"],
             winner_holdout_regret_pct=100*(best-held["mean_DPS"])/best,
             best_discovered_shortlist_holdout=max(x["mean_DPS"] for x in discovered),
             first_near_quality_scout_index0=min((observed[tuple(data[k]["CHMV"])] for k in good),default=None),
             reference_near_CHMV_discovered=len(good))
    report["actual_total_native_including_environment"]=doc["environment_native_calls"]+report["actual_policy_new_native"]+report["holdout"]["new_native"]
    report["status"]="COMPLETE_CURRENT_PROFILE_STRATIFIED_SAME_HISTORY_FORK"
    report["no_global_optimum_or_familywise_95_proof"]=True
    save(root,report)
    print("V330_IDEA003_COMPLETE",json.dumps(report,sort_keys=True),flush=True)
    return report

def main():
    return fresh.main(case_id=CASE,expected_spec=SPEC,output_root=ROOT,
         receipt_path=ROOT/"receipt.json",required_env="P2_V330_FRESH_FERAL_IDEA003_ONCE",
         campaign_schema=SCHEMA,source_only_context_hook=run)
if __name__=="__main__":main()
