#!/usr/bin/env python3
"""v331 final fixed scout N comparison on one NEW Unholy product profile.

Run unchanged v290 through v291/v093/v065 for five fixed scout values. All
arms share the exact reauthenticated scenario with research floor32, have
identical confirmation N320 and logical 64-call ceilings. Equal call counts
are not equal iterations: compare actual budget-truncated prefixes too.
No historical profile or DPS reuse. Independent two-seed N640 shortlist is
an imperfect discovery reference, not ground truth or 95% equivalence.
"""
from __future__ import annotations
import hashlib,json,math,os,pathlib,random,re,statistics,subprocess,time
from integration_probes import p2_v319_new_windwalker_v290_v318_real_once as fresh
from runner import v291_durable_multiscale_native_runner as durable
from runner import v063_numeric_injection as numeric
from runner import v316_optin_case_time_trace as trace

CASE="unholy_deathknight_4ordinary_auto_T"
SPEC=("deathknight","unholy")
ROOT=pathlib.Path("out/p2_v331_unholy_fixed_N").resolve()
SCHEMA="p2_v331_new_unholy_v290_fixed_scout_N_real_v1"
NS=(32,35,48,56,64)
CAP=64
CONFIRM=320
HOLD=640
BAND=.005
ARM_ORDER=tuple(random.Random(20261111).sample(NS,len(NS)))
STATS=tuple(durable.search.STATS)
def need(ok,why):
    if not ok:raise RuntimeError("V331_"+why)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def key(row):
    return tuple(row["target"][s] for s in STATS)
def persist(root,report):
    durable.atomic(root/"FIXED_N_PROGRESS.json",report)

def make_context(context,n):
    need(n in NS and context["identity"]["scout_iterations"]==32,
         "PREAUTHENTICATED_RESEARCH_FLOOR32_REQUIRED")
    old=context["identity"]
    new=durable.adaptive.prepare(context["bundle"],old["binary_sha256"],
          old["revision"],scout_iterations=n,confirm_iterations=CONFIRM)
    need(new["identity"]==dict(old,scout_iterations=n),
         "OTHER_PROFILE_SCENARIO_IDENTITY_CHANGED")
    return new

def select(rows,result):
    confirmed=sorted((r for r in rows if r["phase"]=="precision"),
                    key=lambda r:(-r["dps_mean"],key(r)))
    need(len(confirmed)>=2,"MINIMUM_TWO_CONFIRMATIONS")
    confirmed_keys={key(r) for r in confirmed}
    winner=tuple(result["summary"]["observed_best_T"][s] for s in STATS)
    best_by={}
    for r in rows:
        if key(r) not in best_by or r["iterations"]>best_by[key(r)]["iterations"]:
            best_by[key(r)]=r
    need(winner in best_by,"PRODUCT_OBSERVED_WINNER_NOT_IN_JOURNAL")
    chosen={key(r):r for r in confirmed[:2]}
    chosen.setdefault(winner,best_by[winner])
    # Include the actual product-selected winner, even if it is a noisy
    # scout; when already present, add best never-confirmed scout.
    if len(chosen)<3:
        remaining=sorted((r for v,r in best_by.items() if v not in confirmed_keys),
                         key=lambda r:(-r["dps_mean"],key(r)))
        if remaining:chosen.setdefault(key(remaining[0]),remaining[0])
    return chosen, winner, confirmed[0]

def held_input(original,n,output):
    need(n in NS+(CONFIRM,) and
         len(re.findall(r"(?m)^iterations="+str(n)+r"$",original))==1
         and len(re.findall(r"(?m)^json2=.+$",original))==1,
         "EXACT_CURRENT_NATIVE_INPUT_REQUIRED")
    s=re.sub(r"(?m)^iterations="+str(n)+r"$","iterations="+str(HOLD),original)
    s=re.sub(r"(?m)^json2=.+$",lambda _:"json2="+str(output.resolve()),s)
    norm=lambda x:re.sub(r"(?m)^(iterations|json2)=.+$",r"\1=PATH",x)
    need(norm(s)==norm(original) and
         numeric.input_parts(s)==numeric.input_parts(original),
         "HOLDOUT_CHANGED_PROFILE_BYTES")
    return s

def holdouts(contexts,flask,binary,root,doc,shortlist,seeds):
    dest=root/"holdout";dest.mkdir()
    out={}
    for index,(v,(n,row)) in enumerate(sorted(shortlist.items())):
        source=durable.case_folder(root/("N%d"%n),row["index"])/"input.simc"
        req,_=durable._request(contexts[n],flask,root/("N%d"%n),
             {k:row[k] for k in ("index","target","phase","iterations")})
        need(sha(source)==row["input_sha256"] and
             source.read_bytes()==req["input"].encode(),"HOLDOUT_EXACT_SOURCE_DRIFT")
        reps=[]
        for rep in range(2):
            folder=dest/("candidate_%02d_rep_%d"%(index,rep));folder.mkdir()
            native_path=folder/"result.json";inp=folder/"input.simc"
            inp.write_bytes(held_input(req["input"],row["iterations"],native_path).encode())
            begin=time.monotonic()
            cp=subprocess.run([str(binary),str(inp.resolve())],cwd=binary.parent,
                 stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                 timeout=240,check=False)
            elapsed=time.monotonic()-begin
            (folder/"stdout.txt").write_bytes(cp.stdout)
            (folder/"stderr.txt").write_bytes(cp.stderr)
            need(cp.returncode==0 and native_path.is_file() and
                 0<native_path.stat().st_size<50_000_000,
                 "HOLDOUT_NATIVE_EXIT_"+str(cp.returncode))
            d=json.loads(native_path.read_bytes());sim=d["sim"];o=sim["options"];p=sim["players"]
            rev=d.get("git_revision");seed=o.get("seed")
            need(type(rev) is str and len(rev)>=10 and doc["revision"].startswith(rev)
                 and o["iterations"]==HOLD and len(p)==1
                 and str(p[0].get("specialization","")).lower().startswith("unholy")
                 and type(seed) is int and seed not in seeds,
                 "HOLDOUT_NATIVE_REV_SPEC_ITER_SEED")
            # Same established static-rating reconciliation as v064, not
            # direct buffed_rating==target assumption for talent modifiers.
            static=numeric.validate_static_native(d,{
               "raw_gear_override":req["raw_gear_override"],
               "flask_component_in_T":req["static_flask_F_vector"],
               "expected_static_rating":req["target"]},req["native_revision"])
            need(static["verified_static_CHMV_c"]==row["final_T"] and
                 static["dps_samples"]==HOLD-1
                 and all(math.isfinite(static[k]) and static[k]>0 for k in ("dps_mean","dps_sem")),
                 "HOLDOUT_STATIC_DPS_SEM_SAMPLES_DRIFT")
            seeds.add(seed)
            reps.append({"DPS":static["dps_mean"],"SEM":static["dps_sem"],
                         "samples":static["dps_samples"],"seed":str(seed),
                         "iterations":HOLD,"wall_seconds":elapsed,
                         "input_sha256":sha(inp),"native_sha256":sha(native_path)})
        out["/".join(map(str,v))]={"CHMV":list(v),"source_N":n,
            "source_case_index":row["index"],"source_iterations":row["iterations"],
            "source_input_sha256":row["input_sha256"],"replicates":reps,
            "DPS":sum(r["DPS"] for r in reps)/2,
            "SEM":math.hypot(*(r["SEM"] for r in reps))/2}
        durable.atomic(root/"HOLDOUT_PROGRESS.json",out)
    return out

def prefix_metrics(rows,times,held,*,iterations=None,wall=None):
    count=0;spent=0;seen=set()
    for row,t in zip(rows,times):
        if iterations is not None and spent+row["iterations"]>iterations:break
        if wall is not None and t["invocation_elapsed_seconds"]>wall:break
        spent+=row["iterations"];count+=1
        if row["phase"]=="scout":seen.add(key(row))
    best=max(x["DPS"] for x in held.values())
    known=[held[v] for v in seen if v in held]
    best_seen=max((x["DPS"] for x in known),default=None)
    return {"completed_cases":count,"actual_iterations":spent,"distinct_scout_CHMV":len(seen),
            "best_discovered_heldout_DPS":best_seen,
            "discovery_regret_pct":None if best_seen is None else 100*(best-best_seen)/best,
            "near_reference_CHMV_discovered":sum(x["DPS"]>=best*(1-BAND) for x in known),
            "reference_is_selected_shortlist_not_global_truth":True}

def run(doc,binary,root,context,flask):
    need(doc["status"]=="FRESH_PRODUCT_SOURCE_READY_NO_DPS_NATIVE" and
         not doc["arms"] and doc["manual_final_T"] is None and
         (doc["character"]["character_class"],doc["character"]["character_spec"])==SPEC
         and doc["auto_final_T"]==doc["environment_budget"]["T"]
         and doc["source_profile_sha256"]==context["identity"]["source_profile_sha256"],
         "NEW_UNHOLY_PRODUCT_AUTO_T_REQUIRED")
    report={"schema":SCHEMA,"status":"STARTED","source_profile_sha256":doc["source_profile_sha256"],
            "budget":doc["environment_budget"],"scout_N":list(NS),"confirmation_N":CONFIRM,
            "arm_execution_order":list(ARM_ORDER),"max_native_calls_each":CAP,"arms":{},
            "candidate_shortlist_contract":"top2_320_plus_actual_product_winner_or_best_unconfirmed",
            "quality_band":BAND,"global_optimum_proven":False}
    persist(root,report)
    contexts={n:make_context(context,n) for n in NS}
    data={};shortlist={};seeds=set()
    for n in ARM_ORDER:
        folder=root/("N%d"%n);c=contexts[n];t0=time.monotonic()
        r=durable.run(c,flask,binary,folder,max_native_calls=CAP,
                      max_new_native_this_invocation=CAP,max_elapsed_seconds=1200,
                      case_timing_trace=True,open_folder=False)
        elapsed=time.monotonic()-t0
        rows=durable._load_journal(folder/"V291_JOURNAL.jsonl")
        need(r["policy"]==durable.search.SCHEMA and len(rows)==CAP and
             r["new_native_this_invocation"]==CAP and
             all(x["source"]=="NEW_NATIVE" and
                 x["iterations"]==(n if x["phase"]=="scout" else CONFIRM)
                 and x["target"]==x["final_T"] and
                 sum(x["target"].values())==doc["auto_final_T"] and
                 x["samples"]==x["iterations"]-1 and
                 type(x["simc_seed"]) is int for x in rows),
             "COMPLETE_UNCHANGED_V290_NATIVE_IDENTITY")
        for x in rows:
            case=durable.case_folder(folder,x["index"])
            need(sha(case/"input.simc")==x["input_sha256"] and
                 sha(case/"result.json")==x["native_sha256"] and
                 x["simc_seed"] not in seeds,
                 "ORIGINAL_NATIVE_BYTES_OR_SEED_DRIFT")
            seeds.add(x["simc_seed"])
        times=trace.load(folder/trace.NAME,rows,trace.identity_hash(folder/"V291_SESSION.json"))
        need(len(times)==CAP and len({t["invocation_id"] for t in times})==1,
             "COMPLETE_NATIVE_TRACE_REQUIRED")
        chosen,winner,confirmed=select(rows,r)
        for v,x in chosen.items():
            if v not in shortlist or x["iterations"]>shortlist[v][1]["iterations"]:
                shortlist[v]=(n,x)
        data[n]=(rows,times,winner,confirmed)
        sc=[x for x in rows if x["phase"]=="scout"]
        need(len({key(x) for x in sc})==len(sc),"DUPLICATE_SCOUT")
        report["arms"][str(n)]={"native_calls":CAP,"scout_CHMV_count":len(sc),
             "confirmation_count":CAP-len(sc),"actual_iterations":sum(x["iterations"] for x in rows),
             "wall_seconds":elapsed,"trace_seconds":times[-1]["invocation_elapsed_seconds"],
             "median_scout_engine_seconds":statistics.median(t["engine_execute_seconds"] for t in times if t["phase"]=="scout"),
             "first_eight_CHMV":[list(key(x)) for x in rows[:8]],
             "product_winner_CHMV":list(winner),"product_winner_observed_DPS":r["summary"]["observed_best_dps"],
             "confirmed_winner_CHMV":list(key(confirmed)),"confirmed_winner_DPS":confirmed["dps_mean"],
             "confirmed_winner_SEM":confirmed["dps_sem"],"shortlist_CHMV":[list(v) for v in chosen],
             "session_sha256":sha(folder/"V291_SESSION.json"),
             "journal_sha256":sha(folder/"V291_JOURNAL.jsonl")}
        replay=durable.run(c,flask,binary,folder,max_native_calls=CAP,
             max_new_native_this_invocation=0,cache_only=True,case_timing_trace=True)
        need(replay["completed_cases"]==CAP and replay["new_native_this_invocation"]==0,
             "CACHE_ONLY_REPEAT_NOT_ZERO_NATIVE")
        report["arms"][str(n)]["cache_only_new_native"]=0
        persist(root,report)
        print("V331_ARM",n,json.dumps(report["arms"][str(n)],sort_keys=True),flush=True)
    need(all(report["arms"][str(n)]["first_eight_CHMV"]==
             report["arms"]["35"]["first_eight_CHMV"] for n in NS),
         "SAME_INITIAL_GEOMETRY_REQUIRED")
    # Freeze shortlist before looking at any holdout DPS.
    report["frozen_shortlist"]=[list(v) for v in sorted(shortlist)]
    persist(root,report)
    held_raw=holdouts(contexts,flask,binary,root,doc,shortlist,seeds)
    held={tuple(x["CHMV"]):x for x in held_raw.values()}
    best=max(x["DPS"] for x in held.values())
    common_iters=min(a["actual_iterations"] for a in report["arms"].values())
    common_wall=min(a["trace_seconds"] for a in report["arms"].values())
    report["common_iterations_budget"]=common_iters
    report["common_wall_seconds"]=common_wall
    report["holdout"]={"N":HOLD,"reps":2,"unique_CHMV":len(held),"reference_best_DPS":best,
         "near_count":sum(x["DPS"]>=best*(1-BAND) for x in held.values()),"rows":held_raw}
    for n,(rows,times,winner,confirmed) in data.items():
        a=report["arms"][str(n)]
        good={v for v,x in held.items() if x["DPS"]>=best*(1-BAND)}
        hit=next(((row,t) for row,t in zip(rows,times) if row["phase"]=="scout" and key(row) in good),None)
        a.update(product_winner_holdout_DPS=held[winner]["DPS"],
                 product_winner_holdout_SEM=held[winner]["SEM"],
                 product_winner_regret_pct=100*(best-held[winner]["DPS"])/best,
                 confirmed_winner_holdout_DPS=held[key(confirmed)]["DPS"],
                 first_near_scout_case_1based=hit[0]["index"]+1 if hit else None,
                 first_near_scout_wall_seconds=hit[1]["invocation_elapsed_seconds"] if hit else None,
                 full=prefix_metrics(rows,times,held),
                 equal_iterations=prefix_metrics(rows,times,held,iterations=common_iters),
                 equal_wall=prefix_metrics(rows,times,held,wall=common_wall))
    report["actual_total_native"]=doc["environment_native_calls"]+CAP*len(NS)+2*len(held)
    report["status"]="COMPLETE_FIXED_N_REAL_V290_AND_INDEPENDENT_HOLDOUT"
    report["one_full_trajectory_per_N_not_universal_N_optimum"]=True
    report["no_familywise95_or_global_optimality"]=True
    persist(root,report)
    print("V331_COMPLETE",json.dumps({k:v for k,v in report.items() if k!="holdout"},sort_keys=True),flush=True)
    return report
def main():
    return fresh.main(case_id=CASE,expected_spec=SPEC,output_root=ROOT,
        receipt_path=ROOT/"receipt.json",required_env="P2_V331_FIXED_N_ONCE",
        campaign_schema=SCHEMA,source_only_context_hook=run,research_scout_floor=32)
if __name__=="__main__":main()
