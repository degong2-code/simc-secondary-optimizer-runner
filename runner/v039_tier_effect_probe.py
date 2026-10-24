#!/usr/bin/env python3
"""v039-B: one real cantrip-head + four-tier configuration smoke, not DPS optimization.

The item's authoritative fixed CHMV is separately documented by v039 bare-item
JSON2; this test explicitly inspects tier four-piece and possible on-use/proc
cues. Bonus IDs are copied from public official SimulationCraft MID2 profiles;
confirmation of the full item effect remains evidence-gated.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, re, subprocess
import pilot
import v039_venomkeeper_bare_probe as bare

TIER_HAND_OLD='hands=v020_hands_268243,id=268243,ilevel=334,source=local'
TIER_HAND_NEW='hands=primal_leywardens_manashapers,id=271565,ilevel=334,source=local'
BONUSES='40/13335/13663/13695/13696/13846/13848'
CANTRIP_HEAD='head=venomkeepers_horrific_cowl,id=271874,ilevel=334,source=local,bonus_id='+BONUSES

class CheckFailed(RuntimeError):pass

def require(b, reason):
    if not b: raise CheckFailed(reason)

def make_profile(source: str, json_output: pathlib.Path):
    require(source.count(bare.EXACT_OLD_HEAD)==1,'ORIGINAL_HEAD_CHANGED')
    require(source.count(TIER_HAND_OLD)==1,'ORIGINAL_HAND_CHANGED')
    require(source.count(bare.HASTE_RUNE)==1,'ORIGINAL_RUNE_CHANGED')
    x=source.replace(bare.EXACT_OLD_HEAD,CANTRIP_HEAD).replace(TIER_HAND_OLD,TIER_HAND_NEW).replace(bare.HASTE_RUNE,bare.CRIT_RUNE)
    lines=['iterations=60' if a.startswith('iterations=') else a for a in x.splitlines()]
    require(sum(a.startswith('head=') for a in lines)==1,'HEAD_DUPLICATED')
    require(sum(a.startswith('hands=') for a in lines)==1,'HANDS_DUPLICATED')
    require(sum(a.startswith('iterations=') for a in lines)==1,'ITERATIONS_NOT_UNIQUE')
    lines.append('json2='+str(json_output.resolve()))
    return '\n'.join(lines)+'\n'

def inspect(doc: dict):
    require(doc.get('report_version')=='2.0.0','JSON2_CHANGED')
    require(str(doc.get('git_revision','')).startswith('7bc10711b5'),'PINNED_SIMC_CHANGED')
    people=(doc.get('sim') or {}).get('players') or []
    require(len(people)==1,'PLAYER_COUNT_CHANGED')
    p=people[0];g=p['gear']
    head=g.get('head',{});hands=g.get('hands',{})
    require(head.get('ilevel')==334 and re.search(r'(?:^|,)id=271874(?:,|$)',head.get('encoded_item','')) is not None,'CANTRIP_ID_OR_ILEVEL_CHANGED')
    require(hands.get('ilevel')==334 and re.search(r'(?:^|,)id=271565(?:,|$)',hands.get('encoded_item','')) is not None,'TIER_HAND_ID_CHANGED')
    require(int(head.get('mastery_rating',0))==201,'CANTRIP_FIXED_MASTERY_CHANGED')
    for k in ('crit_rating','haste_rating','versatility_rating'):
        require(int(head.get(k,0))==0,'CANTRIP_UNEXPECTED_STATIC_STAT:'+k)
    buffs=[b.get('name','') for b in p.get('buffs',[])]
    require('rune_of_critical_power' in buffs and 'rune_of_burning_haste' not in buffs,'CRIT_RUNE_LOST')
    require('cumulative_power' in buffs,'FOUR_TIER_SET_BUFF_NOT_PRESENT')
    proc_cues=[b for b in buffs if ('venom' in b or 'venomcurs' in b or 'dreadfang' in b)]
    logs=doc.get('logs',[])
    warnings=[x.get('message','') for x in logs if x.get('level') in ('error','warning')]
    return {'actual_cantrip_head':head,'actual_tier_gloves':hands,'fixed_head_mastery':head['mastery_rating'],
       'confirmed_tier4_buff':'cumulative_power','confirmed_crit_rune':'rune_of_critical_power',
       'possible_special_proc_buff_names':proc_cues,
       'nonstat_special_effect_fully_verified':False,
       'special_effect_implementation_status':'PROC_EVIDENCE_REQUIRES_FURTHER_SEMANTIC_VALIDATION',
       'json2_warning_messages':warnings,'samples':p.get('collected_data',{}).get('dps',{}).get('count'),
       'dps_diagnostic_not_comparable':p.get('collected_data',{}).get('dps',{}).get('mean')}

def run(binary:pathlib.Path,output:pathlib.Path)->int:
    output.mkdir(parents=True,exist_ok=True)
    r={'schema':'v039_real_cantrip_tier_effect_probe_v1','status':'BLOCKED',
       'native_calls':0,'dps_comparison_allowed':False,'item_id':271874,
       'item_ilevel':334,'tier_4pc_verified':False,'item_effect_fully_verified':False,
       'user_item_selection_claimed':False,'global_optimum_claim':False}
    try:
        source,_=pilot.source()
        bare.verify_preconditions(source,binary)
        path=output/'probe.json';inp=output/'probe.simc'
        inp.write_text(make_profile(source,path),encoding='utf-8')
        r['input_sha256']=hashlib.sha256(inp.read_bytes()).hexdigest()
        r['native_calls']=1
        proc=subprocess.run([str(binary),str(inp.resolve())],cwd=binary.parent,stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=90)
        (output/'stdout.txt').write_text(proc.stdout)
        (output/'stderr.txt').write_text(proc.stderr)
        r['exit_code']=proc.returncode
        require(proc.returncode==0,'SIMC_EXIT_'+str(proc.returncode))
        require(path.exists() and path.stat().st_size>1000,'NATIVE_JSON2_NOT_WRITTEN')
        doc=json.loads(path.read_text(encoding='utf-8'))
        r['native']=inspect(doc)
        r['result_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        r['tier_4pc_verified']=True
        r['status']='PASS_REAL_HEAD_STATIC_AND_4PC_EFFECT_NOT_FULLY_PROVEN'
    except Exception as e:r['error']=type(e).__name__+': '+str(e)
    (output/'V039B_RECEIPT.json').write_text(json.dumps(r,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    print('V039B_STATUS',r['status'],'calls',r['native_calls'],flush=True)
    return 0 if r['status'].startswith('PASS_') else 3

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--binary',type=pathlib.Path,required=True);a.add_argument('--output',type=pathlib.Path,required=True)
    x=a.parse_args();raise SystemExit(run(x.binary.resolve(),x.output.resolve()))
