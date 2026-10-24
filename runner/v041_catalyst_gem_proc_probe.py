#!/usr/bin/env python3
"""v041 bounded pilot: same-slot catalyst preserves tier/static/effect/Omnium gem.

Not a real-game bonus assignment, item recommendation, or new budget policy.
Uses the validated 334 v040 trial profile and preserves the exact original head
Omnium gem option. Exactly one pinned native SimC request (60 iterations).
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys

import pilot
import v039_venomkeeper_bare_probe as bare
import v040_catalyst_redirect_probe as prior

CASE = 'bonus_13846_334'
OLD_GEM = 'gem_id=240967'
HEAD = prior.VARIANTS[CASE] + ',' + OLD_GEM
IDENTITY = 'v041_catalyst_gem_proc_334_v1'

class Refused(ValueError):
    pass

def require(value, reason):
    if not value:
        raise Refused(reason)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def build_source(reference, result_path):
    require(reference.count(bare.EXACT_OLD_HEAD) == 1, 'BASELINE_HEAD_CHANGED')
    require(OLD_GEM in bare.EXACT_OLD_HEAD, 'BASELINE_GEM_CHANGED')
    # The v040 input is accepted only after preserving the one original gem.
    src = prior.make_profile(reference, CASE, result_path)
    lines=src.splitlines()
    index=[i for i,x in enumerate(lines) if x.startswith('head=')]
    require(len(index)==1 and lines[index[0]] == prior.VARIANTS[CASE], 'BASELINE_CATALYST_CHANGED')
    lines[index[0]]=HEAD
    require(sum(x.startswith('head=') for x in lines)==1, 'HEAD_DUPLICATE')
    require(sum(x.startswith('json2=') for x in lines)==1, 'OUTPUT_DUPLICATE')
    require('redirected_base_stats=271874' in HEAD and 'bonus_id=13846' in HEAD, 'IDENTITY_LOST')
    require(OLD_GEM in HEAD, 'GEM_LOST')
    require(prior.MAGE_GLOVES in lines,'GLOVES_CHANGED')
    return '\n'.join(lines)+'\n'

def audit_native(payload):
    data=json.loads(payload)
    require(data.get('report_version')=='2.0.0' and str(data.get('git_revision','')).startswith(prior.SOURCE_REV), 'JSON2_REVISION_CHANGED')
    ps=data['sim']['players'];require(len(ps)==1,'PLAYER_COUNT')
    p=ps[0];head=p['gear']['head'];raw=head['encoded_item']
    require(prior._single_id(raw,'id')==271564,'TIER_ID_CHANGED')
    require(prior._single_id(raw,'redirected_base_stats')==271874,'ORIGIN_CHANGED')
    require(prior._single_id(raw,'ilevel')==334,'ILEVEL_CHANGED')
    require(prior._single_id(raw,'bonus_id')==13846,'BONUS_CHANGED')
    gem=[x.split('=',1)[1] for x in raw.split(',') if x.startswith('gem_id=')]
    require(gem==['240967'],'GEM_NOT_RETAINED_IN_JSON2')
    require(head.get('mastery_rating')==201,'BARE_MASTERY_CHANGED')
    require(all(head.get(k,0)==0 for k in ('crit_rating','haste_rating','versatility_rating')),'UNEXPECTED_HEAD_SECONDARY')
    require(prior._single_id(p['gear']['hands']['encoded_item'],'id')==268243,'ORIGINAL_GLOVES_CHANGED')
    buffs={x['name']:x for x in p['buffs']}
    require(prior.TIER_BUFF in buffs,'FOUR_PIECE_MISSING')
    require(prior.RUNE_BUFF in buffs and 'rune_of_burning_haste' not in buffs,'RUNE_INVALID')
    proc=buffs.get(prior.PROC_BUFF)
    require(proc is not None and proc.get('spell')==prior.PROC_SPELL and (proc.get('start_count') or 0)>0, 'VENOMCURSED_NOT_TRIGGERED')
    require(p['collected_data']['dps']['count']>=50,'NOT_ENOUGH_SAMPLES')
    return {
        'status':'PASS_PINNED_334_NATIVE_CATALYST_GEM_TIER_PROC',
        'head':{'tier_id':271564,'redirected_original_id':271874,'ilevel':334,'bonus_id':13846,'gem_id':240967,
                'fixed_mastery_rating':201},
        'tier4_buff':prior.TIER_BUFF,'crit_rune_buff':prior.RUNE_BUFF,
        'proc_buff':prior.PROC_BUFF,'proc_starts_mean':proc['start_count'],'proc_uptime_pct':proc['uptime'],
        'sample_count':p['collected_data']['dps']['count'],
        'native_json2_sha256':sha(payload),
        'special_effect_delta_ratings_proven':False,
        'real_game_catalyzed_334_bonus_proven':False,
        'total_budget_recalibrated':False,
        'gem_mechanical_effect_independently_proven':False,
        'dps_comparison_allowed':False,'user_gear_selection_claimed':False,
    }

def run(binary,output):
    output.mkdir(parents=True,exist_ok=True)
    record={'schema':IDENTITY,'status':'BLOCKED','native_attempts':0,'native_max_calls':1,
            'real_game_catalyst_bonus_attested':False,'user_gear_selection_attested':False,'dps_comparison_allowed':False}
    try:
        require(binary.is_file() and sha(binary.read_bytes())==prior.BIN_SHA,'PINNED_SIMC_BINARY_MISMATCH')
        ref,_=pilot.source()
        bare.verify_preconditions(ref,binary)
        result=(output/'result.json').resolve()
        input_=(output/'input.simc').resolve()
        input_.write_text(build_source(ref,result),encoding='utf-8')
        record['input_sha256']=sha(input_.read_bytes())
        record['native_attempts']=1
        (output/'V041_PROGRESS.json').write_text(json.dumps(record,indent=2)+'\n')
        p=subprocess.run([str(binary),str(input_)],cwd=binary.parent,stdin=subprocess.DEVNULL,
           stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=100)
        (output/'stdout.txt').write_text(p.stdout)
        (output/'stderr.txt').write_text(p.stderr)
        record['exit_code']=p.returncode
        require(p.returncode==0,'SIMC_EXIT_'+str(p.returncode))
        require(result.is_file(),'RESULT_MISSING')
        record['native']=audit_native(result.read_bytes())
        record['status']='PASS_ONE_PINNED_NATIVE_CATALYST_WITH_GEM_NOT_PRODUCT_COMPLETE'
    except Exception as e:
        record['error']=type(e).__name__+':'+str(e)
    (output/'V041_RECEIPT.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print('V041_STATUS',record['status'],'calls',record['native_attempts'],flush=True)
    return 0 if record['status'].startswith('PASS_') else 3

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--binary',type=pathlib.Path,required=True)
    ap.add_argument('--output',type=pathlib.Path,required=True)
    a=ap.parse_args();sys.exit(run(a.binary.resolve(),a.output.resolve()))
