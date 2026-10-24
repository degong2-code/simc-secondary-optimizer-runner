#!/usr/bin/env python3
"""v037 isolated manual-total + candidate-minimum bounded SimC pilot.

Reuses the byte-preserved v032 source and v036 Linux provenance bridge.
No gear recommendations, no generic item-level budgeting, no global optimum.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import pathlib
import sys

STATS = ('crit_rating','haste_rating','mastery_rating','versatility_rating')
OIL = (16,16,0,0)
FLASK = 165
CALIBRATED_TOTAL = 3184
LINUX_SHA = '64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e'
SCHEMA = 'v037_manual_chmv_scenario_probe_v1'

class InvalidContract(ValueError): pass

def need(ok, msg):
    if not ok: raise InvalidContract(msg)

def load_request(obj):
    required = {'schema','scenario','budget_origin','target_total_rating','minimum_target_rating','omnium_rune','scout_iterations','confirm_iterations','maximum_native_calls'}
    need(isinstance(obj,dict) and set(obj)==required,'REQUEST_FIELD_SET_CHANGED')
    need(obj['schema']==SCHEMA,'REQUEST_SCHEMA_CHANGED')
    need(obj['scenario']=='v031r3_dwarf_arcane_fixed_gear','UNVERIFIED_SCENARIO')
    need(obj['budget_origin']=='MANUAL_TEST_TOTAL_NOT_ITEM_LEVEL_PROVEN','BUDGET_ORIGIN_UNATTESTED')
    need(obj['omnium_rune']=='crit','RUNE_SCOPE_CHANGED')
    total=obj['target_total_rating']
    need(type(total) is int and 2500<=total<=4000,'TOTAL_OUTSIDE_NATIVE_VERIFIED_INPUT_RANGE')
    low=obj['minimum_target_rating']
    need(isinstance(low,dict) and set(low)==set(STATS) and all(type(low[s]) is int for s in STATS),'INVALID_MINIMUM_RATING')
    need(all(0<=low[s]<=total//2 for s in STATS),'INVALID_MINIMUM_BOUNDS')
    need(sum(max(low[s],OIL[i]) for i,s in enumerate(STATS))<=total,'MINIMUM_SUM_INFEASIBLE')
    need(obj['scout_iterations']==120 and type(obj['scout_iterations']) is int,'SCOUT_ITERATIONS_UNAUTHORIZED')
    need(obj['confirm_iterations']==320 and type(obj['confirm_iterations']) is int,'CONFIRM_ITERATIONS_UNAUTHORIZED')
    need(obj['maximum_native_calls']==8 and type(obj['maximum_native_calls']) is int,'NATIVE_BUDGET_UNAUTHORIZED')
    return obj

def mins(config):
    return tuple(max(config['minimum_target_rating'][s],OIL[i]) for i,s in enumerate(STATS))

def valid(vec, total, floors, locked=(0,0,0,0)):
    return (type(vec) is tuple and len(vec)==4 and type(locked) is tuple and len(locked)==4
            and all(type(x) is int for x in vec+locked) and sum(vec)==total
            and all(vec[i]>=max(floors[i],OIL[i]+locked[i]) and vec[i]<=total//2 for i in range(4)))

def project(proportions,total,floors):
    """Deterministic integer projection onto total-budget/floor/50%-cap domain."""
    need(len(proportions)==4 and all(math.isfinite(float(x)) and x>=0 for x in proportions),'BAD_DESIRED_WEIGHTS')
    need(sum(proportions)>0,'ZERO_DESIRED_WEIGHTS')
    hi=total//2
    ideal=[total*float(x)/sum(proportions) for x in proportions]
    values=[max(floors[i],min(hi,round(ideal[i]))) for i in range(4)]
    # One point per iteration; max 4000, avoiding floating budget drifts.
    while sum(values)<total:
        possibilities=[i for i in range(4) if values[i]<hi]
        need(bool(possibilities),'NO_UPWARD_CAPACITY')
        k=max(possibilities,key=lambda i:(ideal[i]-values[i],-i))
        values[k]+=1
    while sum(values)>total:
        possibilities=[i for i in range(4) if values[i]>floors[i]]
        need(bool(possibilities),'NO_DOWNWARD_CAPACITY')
        k=max(possibilities,key=lambda i:(values[i]-ideal[i],-i))
        values[k]-=1
    out=tuple(values)
    need(valid(out,total,floors),'PROJECTED_VECTOR_INVALID')
    return out

def seeds(config):
    total=config['target_total_rating'];floor=mins(config)
    baseline=project((600,1140,1115,329),total,floor)
    chosen=[baseline]
    for i in range(4):
        # Original v032 43% directional seeds; minima retained in each axis.
        v=[1.0]*4;v[i]=2.2631578947
        candidate=project(v,total,floor)
        need(candidate not in chosen,'INSUFFICIENT_SEED_DIVERSITY_FOR_FLOORS')
        chosen.append(candidate)
    need(len(set(chosen))==5,'SCOUT_SEEDS_NOT_UNIQUE')
    return chosen

def integrity(config,vectors):
    floor=mins(config);total=config['target_total_rating']
    need(len(vectors)>=5 and len(set(vectors))==len(vectors),'DUPLICATE_SCOUT_RATINGS')
    for vec in vectors:need(valid(vec,total,floor),'OUTSIDE_USER_CHMV_CONSTRAINTS')

def make_plan(config):
    vs=seeds(config);integrity(config,vs)
    return {'schema':'v037_manual_chmv_plan_v1','status':'PASS_OFFLINE_ONLY',
            'reference_calibrated_total':CALIBRATED_TOTAL,
            'manual_total_not_physical_ilvl_proven':True,
            'target_total_rating':config['target_total_rating'],
            'floor':dict(zip(STATS,mins(config))),
            'seed_vectors':[dict(zip(STATS,x)) for x in vs],
            'native_calls_permitted_max':config['maximum_native_calls'],
            'rune':config['omnium_rune'],
            'original_v032_engine_modified_on_disk':False}

def configure_original(runtime,config,native):
    sys.path.insert(0,str(runtime.resolve()))
    import v036_cloud_bridge as bridge
    bridge.ROOT=runtime.resolve()
    # Restore in-memory pilot overrides when this function is called repeatedly
    # inside the same interpreter (e.g. regression tests). No source files changed.
    existing=sys.modules.get('SIMC_OMNIUM_CHMV_ADAPTIVE_v032')
    if existing is not None and hasattr(existing,'_v037_base_valid'):
        existing.TOTAL=CALIBRATED_TOTAL
        existing.valid=existing._v037_base_valid
        existing.seeds=existing._v037_base_seeds
    m,proof=bridge.configure()
    if not hasattr(m,'_v037_base_valid'):
        m._v037_base_valid=m.valid
        m._v037_base_seeds=m.seeds
    # Original v031R3 calibration provenance is always the reference 3184.
    reference=m.load_calibration_evidence()
    need(reference['final_total']==CALIBRATED_TOTAL,'ORIGINAL_CALIBRATION_CHANGED')
    original_valid=m.valid
    original_seeds=m.seeds
    total=config['target_total_rating'];floor=mins(config)
    # In-memory override only; 17 original source modules are hash-verified by bridge.
    m.TOTAL=total
    m.valid=lambda vec,locked=(0,0,0,0):valid(vec,total,floor,locked)
    m.seeds=lambda:seeds(config)
    if native:
        need(native.is_file() and bridge.hash_file(native)==LINUX_SHA,'UNTRUSTED_LINUX_BINARY')
        m.r3.EXPECTED_SIMC_SHA=LINUX_SHA
        need(m.r3.prev.EXPECTED_REV=='7bc1071','ORIGINAL_REVISION_LOCK_CHANGED')
        m.r3.prev.EXPECTED_REV=bridge.SIMC_COMMIT[:10]
    return m,proof

def summarize_confirm(first,second,config):
    a=tuple(first['target'][k] for k in STATS)
    b=tuple(second['target'][k] for k in STATS)
    distance=sum(abs(x-y) for x,y in zip(a,b))/2
    delta=second['dps']-first['dps']
    halfwidth=1.96*math.hypot(first['sem'],second['sem'])
    return {'difference_second_minus_first_dps':delta,
            'difference_ci95_halfwidth_approx':halfwidth,
            'statistically_separated_95pct_approx':abs(delta)>halfwidth,
            'rating_transfer_distance':distance,
            'materially_distinct_by_250_rating_pilot':distance>=250,
            'near_performance_unresolved':abs(delta)<=halfwidth,
            'global_optimum_proven':False}

def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf-8')

def run(config,runtime,output,binary,mode):
    plan=make_plan(config);write_json(output/'V037_PLAN.json',plan)
    if mode=='plan':return {'status':'PASS_OFFLINE_PLAN','plan':plan}
    need(binary is not None and mode=='native','NATIVE_EXECUTION_MODE_INVALID')
    m,provenance=configure_original(runtime,config,binary.resolve())
    src=m.native_source(rune=config['omnium_rune'])
    receipt={'schema':'v037_bounded_native_adaptive_v1','status':'STARTED',
             'input':config,'source_original_zip_sha256':provenance['source_original_zip_sha256'],
             'linux_simc_binary_sha256':LINUX_SHA,'reference_calibrated_total':CALIBRATED_TOTAL,
             'budget_is_manual_not_physical_gear_calibration':True,
             'original_v032_sources_byte_preserved':True,
             'native_calls_attempted':0,'scouts':[],'confirmations':[],
             'cache_kind':'PINNED_BINARY_ONLY_NOT_SIMC_RESULT_CACHE',
             'no_global_optimum_claim':True}
    write_json(output/'V037_RECEIPT.json',receipt)
    seen=set()
    try:
        planned=seeds(config)
        for i in range(6):
            if i<5:vec=planned[i]
            else:
                vec,rationale=m.choose_guided(receipt['scouts'])
                receipt['guided_rationale']=rationale
            need(valid(vec,config['target_total_rating'],mins(config)),'GUIDED_OUTSIDE_FLOORS')
            identity=(vec,config['scout_iterations'])
            need(identity not in seen,'DUPLICATE_NATIVE_SCOUT')
            seen.add(identity)
            need(receipt['native_calls_attempted']<config['maximum_native_calls'],'NATIVE_CALL_BUDGET_EXCEEDED')
            receipt['native_calls_attempted']+=1
            write_json(output/'V037_RECEIPT.json',receipt)
            entry=m.run_case(binary,output/f'SCOUT_{i+1:02d}',src,vec,config['scout_iterations'],config['omnium_rune'])
            need(entry['status']=='NATIVE_STATS_AND_RUNE_PASS','NATIVE_SCOUT_INVALID')
            receipt['scouts'].append(entry)
            write_json(output/'V037_RECEIPT.json',receipt)
        selections,method=m.confirm_seeds(receipt['scouts'])
        need(len(selections)==2,'CONFIRMATION_COUNT_CHANGED')
        receipt['confirmation_method']=method
        for i,vec in enumerate(selections):
            identity=(vec,config['confirm_iterations'])
            need(identity not in seen,'DUPLICATE_SAME_ITERATIONS')
            seen.add(identity)
            need(receipt['native_calls_attempted']<config['maximum_native_calls'],'NATIVE_CALL_BUDGET_EXCEEDED')
            receipt['native_calls_attempted']+=1
            write_json(output/'V037_RECEIPT.json',receipt)
            entry=m.run_case(binary,output/f'CONFIRM_{i+1:02d}',src,vec,config['confirm_iterations'],config['omnium_rune'])
            need(entry['status']=='NATIVE_STATS_AND_RUNE_PASS','NATIVE_CONFIRM_INVALID')
            receipt['confirmations'].append(entry)
            write_json(output/'V037_RECEIPT.json',receipt)
        receipt['comparison']=summarize_confirm(*receipt['confirmations'],config)
        receipt['status']='PASS_BOUNDED_NATIVE_MANUAL_BUDGET_NOT_GLOBAL_OPTIMUM'
    except Exception as e:
        receipt['status']='BLOCKED_OR_PARTIAL'
        receipt['error']=type(e).__name__+': '+str(e)
    receipt['completed_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
    write_json(output/'V037_RECEIPT.json',receipt)
    print('V037_NATIVE_STATUS',receipt['status'],'native_attempts',receipt['native_calls_attempted'],flush=True)
    return receipt

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument('--request',type=pathlib.Path,required=True)
    parser.add_argument('--runtime',type=pathlib.Path)
    parser.add_argument('--output',type=pathlib.Path,required=True)
    parser.add_argument('--mode',choices=['plan','native'],default='plan')
    parser.add_argument('--binary',type=pathlib.Path)
    args=parser.parse_args(argv)
    args.output.mkdir(parents=True,exist_ok=True)
    try:
        config=load_request(json.loads(args.request.read_text(encoding='utf-8')))
        res=run(config,args.runtime,args.output,args.binary,args.mode)
        if args.mode=='plan':print('V037_PLAN_PASS',config['target_total_rating'])
        return 0 if res['status'] in ('PASS_OFFLINE_PLAN','PASS_BOUNDED_NATIVE_MANUAL_BUDGET_NOT_GLOBAL_OPTIMUM') else 3
    except Exception as e:
        write_json(args.output/'V037_BLOCKED.json',{'status':'BLOCKED','reason':type(e).__name__+': '+str(e)})
        print('V037_BLOCKED',type(e).__name__,e,file=sys.stderr)
        return 3
if __name__=='__main__':raise SystemExit(main())
