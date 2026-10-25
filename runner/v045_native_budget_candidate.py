#!/usr/bin/env python3
"""v045 bounded core: derive G/J/F from pinned Native static evidence and inject
one CHMV candidate while keeping SimC responsible for effects and DPS.
No user-equipment attestation, automatic oil-budget policy or product integration.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,re,subprocess,sys
import pilot
import v039_venomkeeper_bare_probe as bare
import v041_catalyst_gem_proc_probe as v041

SCHEMA='v045_pinned_334_candidate_v1'
STATS=('crit_rating','haste_rating','mastery_rating','versatility_rating')
EVIDENCE_SHA256='fe54b8b4f557ff004ec81dd2dd0d76a62068e0dcd14f48ce923f96f34e7465aa'
NATIVE_SOURCE_SHA256='4367cfa9e911190af8e8441f44378cb0efab4d018fd059677e01fa054636ed55'
ARTIFACT_SOURCE_SHA256='eea36762a1d21db5e9ad5bcf72c6c94bff4d122fee28f3ea83cd700120b9dc7f'
TEST_TARGET=(600,1125,1100,328) # T=3153; test candidate, not optimized
FLASK=(0,165,0,0) # selected pinned sample flask only
class Blocked(ValueError): pass
def require(ok,code):
    if not ok:raise Blocked(code)
def sha(data):return hashlib.sha256(data).hexdigest()
def vector(obj):
    require(type(obj) is dict and set(obj)==set(STATS),'VECTOR_KEYS')
    require(all(type(obj[k]) is int and obj[k]>=0 for k in STATS),'VECTOR_VALUES')
    return tuple(obj[k] for k in STATS)

def load_evidence(payload):
    require(type(payload) is bytes and sha(payload)==EVIDENCE_SHA256,'EVIDENCE_BYTES_DRIFT')
    e=json.loads(payload)
    require(e.get('schema')=='v045_pinned_v042_static_334_v1' and
            e.get('native_json2_sha256')==NATIVE_SOURCE_SHA256 and
            e.get('artifact_sha256')==ARTIFACT_SOURCE_SHA256,'NATIVE_PROVENANCE_DRIFT')
    require(e.get('item_level')==334 and e.get('head_fixed_mastery_rating')==201
            and e.get('head_diagnostic_bonus_id')==13846 and e.get('head_special_gem_id')==240967,
            'ITEM_IDENTITY_DRIFT')
    require(e.get('general_gem_budget')==138 and e.get('flask_budget')==165,'J_F_POLICY_DRIFT')
    require(e.get('flask_name')=='flask_of_the_blood_knights_2'
            and e.get('flask_injection_stat')=='haste_rating'
            and e.get('temporary_enchant')=='main_hand:thalassian_phoenix_oil_2',
            'TRIAL_CONSUMABLE_DRIFT')
    require(e.get('user_selected_item_attested') is False and
            e.get('product_integrated') is False,'AUTHORITY_ESCALATION')
    ids=e.get('item_ids')
    require(type(ids) is dict and len(ids)==15 and
            all(type(v) is int and v>0 for v in ids.values()),'ITEM_IDS_INVALID')
    fixed=e.get('fixed_nontrinket_slots')
    require(type(fixed) is dict and len(fixed)==13 and 'head' in fixed and
            'trinket1' not in fixed and 'trinket2' not in fixed,'FIXED_SLOTS_INVALID')
    total=[0,0,0,0]
    for slot,data in fixed.items():
        require(slot in ids,'UNKNOWN_FIXED_SLOT')
        for i,n in enumerate(vector(data)):total[i]+=n
    require(vector(fixed['head'])==(0,0,201,0),'LOCKED_HEAD_CHANGED')
    require(sum(total)==2850,'NATIVE_G_SUM_DRIFT')
    return e,tuple(total)

def plan(evidence_bytes,desired=TEST_TARGET):
    e,gear=load_evidence(evidence_bytes)
    require(type(desired) is tuple and len(desired)==4 and
            all(type(x) is int and x>=0 for x in desired),'TARGET_INVALID')
    G=sum(gear);J=e['general_gem_budget'];F=e['flask_budget'];T=G+J+F
    require(sum(desired)==T,'TARGET_TOTAL_MISMATCH')
    require(all(x<=T//2 for x in desired),'TRIAL_STAT_CAP')
    require(desired[2]>=201,'LOCKED_FIXED_HEAD_BREACH')
    require(all(desired[i]>=FLASK[i] for i in range(4)),'FLASK_SUBTRACTION_NEGATIVE')
    injected=tuple(desired[i]-FLASK[i] for i in range(4))
    require(sum(injected)==G+J and injected[2]>=201,'INJECTED_BUDGET_INVALID')
    return {'schema':SCHEMA,'status':'PASS_BOUNDED_PLAN_NOT_PRODUCT',
            'G':G,'J':J,'F':F,'T':T,'head_fixed_mastery_floor':201,
            'target':dict(zip(STATS,desired)),
            'gear_override':dict(zip(STATS,injected)),
            'expected_flask_delta':dict(zip(STATS,FLASK)),
            'source_native_sha256':e['native_json2_sha256'],'item_ids':e['item_ids'],
            'oil_preserved_outside_T':True,'real_bonus_attested':False,
            'all_flasks_generalized':False,
            'product_code_integrated':False,'official_policy_promoted':False}

def build_profile(reference,result_path,case):
    # Keep original 14 other equipment slots, four-piece tier, effects and gems.
    source=v041.build_source(reference,result_path)
    lines=source.splitlines()
    for stat,amount in case['gear_override'].items():
        key='gear_'+stat+'='
        positions=[i for i,x in enumerate(lines) if x.startswith(key)]
        require(len(positions)==1,'OVERRIDE_COUNT_DRIFT:'+stat)
        lines[positions[0]]=key+str(amount)
    require(sum(x.startswith('json2=') for x in lines)==1,'JSON2_COUNT')
    require('head='+v041.HEAD.split('=',1)[1] in lines,'HEAD_IDENTITY_LOST')
    require('flask=flask_of_the_blood_knights_2' in lines,'FLASK_CHANGED')
    require('temporary_enchant=main_hand:thalassian_phoenix_oil_2' in lines,
            'TRIAL_OIL_CHANGED')
    return '\n'.join(lines)+'\n'

def audit_native(payload,case):
    # v041 baseline audit: head, gem, bonus, gloves, tier4, crit rune and proc.
    baseline=v041.audit_native(payload)
    player=json.loads(payload)['sim']['players'][0]
    data=player['collected_data']['buffed_stats']['stats']
    observed={}
    for s in STATS:
        value=data.get(s)
        require(type(value) in (float,int) and abs(value-round(value))<1e-8,
                'FINAL_RATING_INVALID:'+s)
        observed[s]=int(round(value))
    require(observed==case['target'],'FINAL_CHMV_MISMATCH')
    require(sum(observed.values())==case['T'],'FINAL_TOTAL_MISMATCH')
    gear=player['gear']
    require(set(gear)==set(case['item_ids']),'ITEM_SLOT_SET_DRIFT')
    stat_gear_total=0
    for slot,item_id in case['item_ids'].items():
        item=gear[slot]
        require(item.get('ilevel')==334,'ITEM_LEVEL_CHANGED:'+slot)
        encoded=item.get('encoded_item','')
        item_ids=re.findall(r'(?:^|,)id=(\d+)(?=,|$)',encoded)
        require(len(item_ids)==1 and int(item_ids[0])==item_id,'ITEM_ID_DRIFT:'+slot)
        if slot not in ('trinket1','trinket2'):
            for stat in STATS:
                n=item.get(stat,0)
                require(type(n) is int and n>=0,'ITEM_RATING_INVALID:'+slot)
                stat_gear_total+=n
    require(stat_gear_total==case['G'],'NATIVE_G_RECALIBRATION_DRIFT')
    require(baseline['head']['fixed_mastery_rating']==201,'HEAD_MASTERY_CHANGED')
    return {'status':'PASS_ONE_PINNED_NATIVE_EXACT_CHMV_NOT_OPTIMUM',
            'actual_rating':observed,'native_json2_sha256':sha(payload),
            'actual_static_nontrinket_G':stat_gear_total,'samples':baseline['sample_count'],
            'dps_optimum_proven':False,'dynamic_effect_computation_owned_by_simc':True}

def run(binary,evidence,output):
    output.mkdir(parents=True,exist_ok=True)
    r={'schema':SCHEMA,'status':'BLOCKED','test_success':False,
       'product_code_integrated':False,'official_policy_promoted':False,
       'native_max_calls':1,'native_calls_attempted':0,
       'product_admission':'BLOCKED_V016_LINEAGE_AND_GENERALIZATION'}
    try:
        require(binary.is_file() and sha(binary.read_bytes())==v041.prior.BIN_SHA,
                'PINNED_BINARY_INVALID')
        source,_=pilot.source()
        bare.verify_preconditions(source,binary)
        case=plan(evidence.read_bytes())
        r['plan']=case
        out=(output/'result.json').resolve()
        input_path=(output/'input.simc').resolve()
        input_path.write_text(build_profile(source,out,case),encoding='utf-8')
        r['input_sha256']=sha(input_path.read_bytes())
        r['native_calls_attempted']=1
        (output/'V045_PROGRESS.json').write_text(json.dumps(r,indent=2)+'\n')
        p=subprocess.run([str(binary),str(input_path)],cwd=binary.parent,
            stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=100)
        (output/'stdout.txt').write_bytes(p.stdout)
        (output/'stderr.txt').write_bytes(p.stderr)
        require(p.returncode==0,'NATIVE_EXIT_'+str(p.returncode))
        require(out.is_file(),'NATIVE_JSON2_ABSENT')
        r['native']=audit_native(out.read_bytes(),case)
        r['status']='PASS_ONE_NATIVE_3153_BUDGET_ATTRIBUTION_NOT_PRODUCT'
        r['test_success']=True
    except Exception as ex:
        r['error_code']=type(ex).__name__+':'+str(ex)
    (output/'V045_RECEIPT.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print('V045_STATUS',r['status'],'native_calls',r['native_calls_attempted'],flush=True)
    return 0 if r['test_success'] else 3

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--binary',required=True,type=pathlib.Path)
    ap.add_argument('--evidence',required=True,type=pathlib.Path)
    ap.add_argument('--output',required=True,type=pathlib.Path)
    opts=ap.parse_args()
    sys.exit(run(opts.binary.resolve(),opts.evidence.resolve(),opts.output.resolve()))
