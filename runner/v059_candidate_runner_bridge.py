#!/usr/bin/env python3
"""v059: thin selector -> bounded CHMV candidate -> SimC JSON2/DPS bridge.

SimC owns APL, trinket/embellishment effects, and DPS. The adapter owns only
stat budget/floors, item-input pass-through, cached candidate identity,
observed static CHMV and DPS+SEM extraction.

v059 Native trial is anchored to the v031r3/v036 Mage 334 representative
profile, not a general item-level or original v015/v016 product integration.
"""
from __future__ import annotations

import argparse, hashlib, json, math, pathlib, subprocess, sys
import pilot
import v046_static_item_cache as item_cache
import v055_simc_item_selection as selector

SCHEMA="v059_candidate_bridge_v1"
STATS=item_cache.STATS
BINARY_SHA="64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e"
OIL={"crit_rating":16,"haste_rating":16,"mastery_rating":0,"versatility_rating":0}
NATIVE_EXTRA={"crit_rating":0,"haste_rating":165,"mastery_rating":0,"versatility_rating":0}
# Bounded benchmark: v036 Native head=200, G nontrinket=2849.
# This is not universal G nor the latest v042 G=2850.
PINNED_G=2849
GEM_TOTAL=138
FLASK_TOTAL=165
PILOT_TOTAL=PINNED_G+GEM_TOTAL+FLASK_TOTAL+sum(OIL.values())
DEFAULT_SELECTED=[{"slot":"trinket1","item_id":250224,"ilevel":334,"options":{}}]
DEFAULT_TARGETS=[
 {"crit_rating":600,"haste_rating":1140,"mastery_rating":1115,"versatility_rating":329},
 {"crit_rating":750,"haste_rating":990,"mastery_rating":1115,"versatility_rating":329}]
MAX_ITERATIONS=120
MAX_CASES=2

class ScenarioBlocked(ValueError): pass
def require(ok,message):
    if not ok: raise ScenarioBlocked(message)

def stat_vector(obj, label):
    require(type(obj) is dict and set(obj)==set(STATS),label+"_SHAPE")
    require(all(type(obj[k]) is int and 0<=obj[k]<=100000 for k in STATS),
            label+"_INVALID")
    return obj

def project(proportions,total,floors,max_per_stat=None):
    """Tiny deterministic bounded-rating projector usable by an adaptive engine."""
    require(len(proportions)==4 and all(
            type(x) in (int,float) and math.isfinite(x) and x>=0 for x in proportions)
            and sum(proportions)>0,"PROJECT_WEIGHTS")
    require(type(total) is int and total>0,"TOTAL")
    stat_vector(floors,"FLOORS")
    cap=max_per_stat if max_per_stat is not None else total//2
    require(type(cap) is int and cap>=0 and
            sum(floors.values())<=total<=cap*4 and
            all(x<=cap for x in floors.values()),"INFEASIBLE_BOUNDS")
    ideal=[total*x/sum(proportions) for x in proportions]
    vals=[max(floors[k],min(cap,int(round(ideal[i])))) for i,k in enumerate(STATS)]
    while sum(vals)<total:
        pos=[i for i in range(4) if vals[i]<cap]
        require(bool(pos),"PROJECT_UP_FAILED")
        j=max(pos,key=lambda i:(ideal[i]-vals[i],-i))
        vals[j]+=1
    while sum(vals)>total:
        pos=[i for i in range(4) if vals[i]>floors[STATS[i]]]
        require(bool(pos),"PROJECT_DOWN_FAILED")
        j=max(pos,key=lambda i:(vals[i]-ideal[i],-i))
        vals[j]-=1
    out=dict(zip(STATS,vals))
    validate_target(out,total,floors,cap)
    return out

def validate_target(target,total,floor,max_per_stat):
    stat_vector(target,"CHMV_TARGET")
    stat_vector(floor,"CHMV_FLOOR")
    require(sum(target.values())==total,"CHMV_BUDGET_MISMATCH")
    require(all(floor[k]<=target[k]<=max_per_stat for k in STATS),
            "CHMV_FIXED_FLOOR_OR_CAP")
    return target

def plan(reference,selection,targets,iterations=60,
         G=PINNED_G,gems=GEM_TOTAL,flask=FLASK_TOTAL,oil=OIL,
         special_fixed=None,native_add=NATIVE_EXTRA):
    require(type(G) is int and G>=0 and type(gems) is int and gems>=0 and
            type(flask) is int and flask>=0,"INVALID_GJF_BUDGET")
    require(type(iterations) is int and 30<=iterations<=MAX_ITERATIONS,
            "ITERATION_BOUNDS")
    require(type(targets) is list and 1<=len(targets)<=MAX_CASES,
            "CANDIDATE_CALL_BOUND")
    special_fixed=special_fixed or dict.fromkeys(STATS,0)
    stat_vector(special_fixed,"SPECIAL_FIXED")
    stat_vector(oil,"OIL")
    stat_vector(native_add,"NATIVE_ADDITIONS")
    total=G+gems+flask+sum(oil.values())
    floor={k:special_fixed[k]+oil[k] for k in STATS}
    require(sum(special_fixed.values())<=G and all(x<=total//2 for x in floor.values()),
            "SPECIAL_FLOOR_UNSATISFIABLE")
    user_profile,selection_summary=selector.apply_selection(reference,selection)
    # Preserve all non-selected character/scenario lines verbatim.
    src_digest=hashlib.sha256(user_profile.encode()).hexdigest()
    inputs=[]
    for target in targets:
        validate_target(target,total,floor,total//2)
        require(all(target[k]>=native_add[k] for k in STATS),
                "NATIVE_CALIBRATION_CANNOT_INJECT_THIS_TARGET")
        overrides={k:target[k]-native_add[k] for k in STATS}
        require(sum(overrides.values())==total-sum(native_add.values()),
                "DOUBLE_ADDITION_IN_OVERRIDE")
        signature={"scenario_profile_sha256":src_digest,"target":target,
                   "iterations":iterations,"native_add":native_add,
                   "simc_binary_sha256":BINARY_SHA,
                   "fight_profile_unchanged":True}
        case_key=item_cache.digest(signature)
        inputs.append({"target":target,"overrides":overrides,
                       "case_key":case_key,"signature":signature})
    require(len(set(i["case_key"] for i in inputs))==len(inputs),
            "DUPLICATE_CANDIDATE")
    return {"schema":SCHEMA,"status":"BOUNDED_CANDIDATE_PLAN_NOT_FULL_OPTIMIZATION",
       "profile":user_profile,"profile_sha256":src_digest,
       "selection":selection_summary,"budget":{"G":G,"J":gems,"F":flask,
       "O":oil,"T":total,"special_fixed":special_fixed,
       "native_additions_calibration_for_this_profile_only":native_add,
       "external_trinket_static_not_in_G":True},
       "cases":inputs,"iterations":iterations,
       "proc_gate":False,"item_effects_owned_by_simc":True,
       "original_v015_v016_engine_integrated":False,
       "official_policy_promoted":False}

def compose_input(profile,case,output_path,iterations):
    require("json2=" not in profile,"EXISTING_JSON2_UNEXPECTED")
    lines=profile.splitlines()
    for stat,n in case["overrides"].items():
        key="gear_"+stat+"="
        found=[i for i,x in enumerate(lines) if x.startswith(key)]
        require(len(found)==1,"MISSING_OR_DUPLICATE_GEAR_OVERRIDE:"+stat)
        lines[found[0]]=key+str(n)
    it=[i for i,x in enumerate(lines) if x.startswith("iterations=")]
    require(len(it)==1,"ITERATION_INPUT_SHAPE")
    lines[it[0]]="iterations="+str(iterations)
    lines.append("json2="+str(output_path.resolve()))
    return "\n".join(lines)+"\n"

def observe_result(native,case):
    require(type(native) is dict and native.get("report_version")=="2.0.0",
            "SIMC_JSON2_INVALID")
    players=(native.get("sim") or {}).get("players") or []
    require(len(players)==1,"SIMC_PLAYER_COUNT")
    player=players[0]
    observed=player.get("collected_data",{}).get("buffed_stats",{}).get("stats",{})
    require(all(type(observed.get(k)) in (int,float) and math.isfinite(observed[k])
            for k in STATS),"NATIVE_CHMV_NOT_REPORTED")
    actual={k:int(round(observed[k])) for k in STATS}
    require(all(abs(actual[k]-observed[k])<=0.01 for k in STATS),
            "NATIVE_CHMV_NONINTEGER")
    require(actual==case["target"],"SIMC_FINAL_CHMV_MISMATCH")
    dps=player.get("collected_data",{}).get("dps",{})
    require(type(dps.get("count")) is int and dps["count"]>=20,"NO_DPS_SAMPLES")
    d,sem=dps.get("mean"),dps.get("mean_std_dev")
    require(type(d) in (float,int) and type(sem) in (float,int) and
            math.isfinite(d) and d>0 and math.isfinite(sem) and sem>=0,
            "DPS_OR_SEM_INVALID")
    return {"status":"PASS_NATIVE_CHMV_AND_DPS","case_key":case["case_key"],
            "target":case["target"],"actual_rating":actual,"dps_mean":d,
            "dps_sem":sem,"approx_ci95":[d-1.96*sem,d+1.96*sem],
            "native_dps_samples":dps["count"],
            "native_simc_revision":native.get("git_revision"),
            "trinket_static_gear_record_not_required":True,
            "native_effect_details_not_interpreted":True}

def compare(observations):
    require(type(observations) is list and len(observations)>=2,"NEED_TWO_DPS_SAMPLES")
    first,second=observations[0],observations[1]
    diff=second["dps_mean"]-first["dps_mean"]
    half=1.96*math.hypot(first["dps_sem"],second["dps_sem"])
    return {"status":"PAIRWISE_STATISTIC_ONLY_NOT_GLOBAL_OPTIMUM",
       "difference_second_minus_first_dps":diff,
       "approx_95pct_difference_halfwidth":half,
       "statistically_separated_approx95":abs(diff)>half,
       "overlapping_or_inconclusive":abs(diff)<=half,
       "winner_if_separated":"second" if diff>half else
                             "first" if diff< -half else None,
       "comparisons_are_the_adaptive_engine_interface":True}

def execute(binary,output,selection,targets,iterations):
    output.mkdir(parents=True,exist_ok=True)
    receipt={"schema":SCHEMA,"status":"BLOCKED","native_calls":0,
             "original_product_integrated":False,
             "independent_proc_gate":False,
             "official_policy_promoted":False}
    try:
        ref,_=pilot.source()
        scenario=plan(ref,selection,targets,iterations)
        receipt["scenario_profile_sha256"]=scenario["profile_sha256"]
        receipt["budget"]=scenario["budget"]
        receipt["selected_equipment"]=selection
        receipt["cases"]=[]
        require(binary.is_file() and hashlib.sha256(binary.read_bytes()).hexdigest()==BINARY_SHA,
                "SIMC_BINARY_SHA_CHANGED")
        for i,case in enumerate(scenario["cases"]):
            case_path=output/("case_%02d"%i)
            case_path.mkdir(exist_ok=True)
            result=case_path/"result.json"
            inputpath=case_path/"input.simc"
            receiptpath=case_path/"CASE_RECEIPT.json"
            prev=None
            if receiptpath.exists() and result.exists():
                prev=json.loads(receiptpath.read_text())
                require(prev.get("case_key")==case["case_key"],
                        "OLD_CASE_IDENTITY_CONFLICT")
                validated=observe_result(json.loads(result.read_text()),case)
                if prev.get("native_json_sha256")==hashlib.sha256(result.read_bytes()).hexdigest():
                    receipt["cases"].append(validated|{"source":"CACHED_VERIFIED_NATIVE"})
                    continue
                raise ScenarioBlocked("NATIVE_CACHE_DIGEST_CONFLICT")
            inp=compose_input(scenario["profile"],case,result,iterations)
            inputpath.write_text(inp,encoding="utf-8")
            receipt["native_calls"]+=1
            process=subprocess.run([str(binary),str(inputpath)],cwd=binary.parent,
                stdin=subprocess.DEVNULL,capture_output=True,timeout=300)
            (case_path/"stdout.txt").write_bytes(process.stdout)
            (case_path/"stderr.txt").write_bytes(process.stderr)
            require(process.returncode==0 and result.exists(),"SIMC_NATIVE_RUN_FAILED")
            observed=observe_result(json.loads(result.read_text()),case)
            observed["native_json_sha256"]=hashlib.sha256(result.read_bytes()).hexdigest()
            receiptpath.write_text(json.dumps(observed,indent=2,sort_keys=True)+"\n")
            receipt["cases"].append(observed|{"source":"NEW_NATIVE"})
            (output/"V059_PROGRESS.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
        if len(receipt["cases"])>=2:
            receipt["comparison"]=compare(receipt["cases"])
        receipt["status"]="PASS_BOUNDED_TWO_CANDIDATES_WITHOUT_PROC_GATE"
    except Exception as exc:
        receipt["error"]=type(exc).__name__+":"+str(exc)
    (output/"V059_RECEIPT.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print("V059",receipt["status"],"native_calls",receipt["native_calls"])
    return 0 if receipt["status"].startswith("PASS") else 3

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--binary",type=pathlib.Path,required=True)
    a.add_argument("--out",type=pathlib.Path,required=True)
    a.add_argument("--iterations",type=int,default=60)
    args=a.parse_args()
    return execute(args.binary.resolve(),args.out.resolve(),
                   DEFAULT_SELECTED,DEFAULT_TARGETS,args.iterations)
if __name__=="__main__":sys.exit(main())
