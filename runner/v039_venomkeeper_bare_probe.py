#!/usr/bin/env python3
"""v039: bounded REAL item ID 271874 bare-item native evidence probe.

This is a DEVELOPMENT TEST ITEM, not an asserted user selection. No claims
about tier four-piece preservation, effect implementation, DPS comparison,
correct final target CHMV or globally optimal stat distribution.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, re, subprocess, sys, time
import pilot
import v038_fixed_gear_floor as floor

ITEM_ID = 271874
ITEM_ILVL = 334
ITEM_SLOT = 'head'
EXPECTED_BARE_MASTERY = 201  # external in-game tooltip observation; verify native
PINNED_BIN_SHA256 = '64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e'
EXACT_OLD_HEAD = 'head=v020_head_271564,id=271564,ilevel=334,source=local,gem_id=240967'
EXACT_NEW_HEAD = 'head=venomkeepers_horrific_cowl,id=271874,ilevel=334,source=local'
HASTE_RUNE='omnium_talents=136822:1/136817:1/136821:1/136814:1'
CRIT_RUNE='omnium_talents=136822:1/136817:1/136815:1/136814:1'
SCHEMA='v039_real_item_bare_stat_native_v1'

class ProbeBlocked(RuntimeError): pass

def need(condition, reason):
    if not condition: raise ProbeBlocked(reason)

def verify_preconditions(source_text: str, binary: pathlib.Path):
    need(source_text.count(EXACT_OLD_HEAD)==1, 'REFERENCE_HEAD_CHANGED')
    need('head=venomkeepers_horrific_cowl' not in source_text, 'ITEM_ALREADY_IN_BASELINE')
    need(binary.is_file(), 'SIMC_BINARY_NOT_FOUND')
    need(floor.source_sha(binary.read_bytes())==PINNED_BIN_SHA256, 'PINNED_BINARY_SHA_MISMATCH')

def make_bare(source_text: str, output: pathlib.Path, iterations:int=60):
    need(type(iterations) is int and iterations==60, 'ITERATIONS_OUT_OF_SCOPE')
    need(source_text.count(EXACT_OLD_HEAD)==1, 'REFERENCE_HEAD_CHANGED')
    need(source_text.count(HASTE_RUNE)==1 and source_text.count(CRIT_RUNE)==0, 'RUNE_SOURCE_IDENTITY_CHANGED')
    body=source_text.replace(EXACT_OLD_HEAD,EXACT_NEW_HEAD).replace(HASTE_RUNE,CRIT_RUNE)
    need(body.count(EXACT_NEW_HEAD)==1, 'ITEM_HEAD_REPLACEMENT_FAILED')
    need(body.count(CRIT_RUNE)==1 and HASTE_RUNE not in body,'CRIT_RUNE_NOT_SELECTED')
    lines=body.splitlines()
    lines=['iterations=60' if line.startswith('iterations=') else line for line in lines]
    need(sum(line.startswith('iterations=') for line in lines)==1, 'ITERATIONS_NOT_UNIQUE')
    need(sum(line.startswith('head=') for line in lines)==1, 'HEAD_NOT_UNIQUE')
    # User's original four-tier profile becomes a **three-piece** test profile.
    # Deliberately preserve other baseline equipment; NEVER report DPS parity.
    lines.append('json2='+str(output.resolve()))
    s='\n'.join(lines)+'\n'
    need(s.count('json2=')==1,'OUTPUT_NOT_UNIQUE')
    need('bonus_id=' not in s.split('head=',1)[1].split('\n',1)[0], 'BARE_HAS_BONUS')
    return s

def read_bare_native(json_bytes: bytes):
    doc=json.loads(json_bytes)
    item={'slot':ITEM_SLOT,'item_id':ITEM_ID,'ilevel':ITEM_ILVL}
    stats=floor.bare_item_stats(json_bytes,floor.source_sha(json_bytes),item)
    need(stats=={'crit_rating':0,'haste_rating':0,'mastery_rating':EXPECTED_BARE_MASTERY,'versatility_rating':0},
         'BARE_ITEM_STAT_NOT_EXPECTED:'+str(stats))
    p=doc['sim']['players'][0]
    head=p['gear']['head']
    need(head.get('ilevel')==334, 'HEAD_ITEM_LEVEL_CHANGED')
    need(re.search(r'(?:^|,)id=271874(?:,|$)',head['encoded_item']) is not None, 'HEAD_ID_CHANGED')
    for slot,item_id in (('shoulders',271562),('chest',271567),('legs',271563)):
        gear=p['gear'].get(slot,{})
        need(re.search(fr'(?:^|,)id={item_id}(?:,|$)',gear.get('encoded_item','')) is not None,
             'OTHER_TIER_PIECES_CHANGED:'+slot)
    need(p.get('specialization')=='Arcane Mage' and p.get('race')=='dwarf','CHARACTER_IDENTITY_CHANGED')
    need(doc.get('report_version')=='2.0.0','NOT_JSON2')
    dps=p.get('collected_data',{}).get('dps',{})
    need(int(dps.get('count',0))>=50,'INSUFFICIENT_PROBE_SAMPLES')
    buffs=[a.get('name','') for a in p.get('buffs',[])]
    need('rune_of_critical_power' in buffs and 'rune_of_burning_haste' not in buffs, 'CRIT_RUNE_BUFF_NOT_NATIVE')
    return {'bare_gear_chmv':stats,'item_id':ITEM_ID,'item_ilevel':ITEM_ILVL,
            'dps_diagnostic_not_comparable':dps.get('mean'),
            'dps_samples':dps.get('count'), 'buff_names':buffs,
            'cumulative_power_tier4_buff_present':'cumulative_power' in buffs,
            'venomcursed_effect_supported':None, # NOT proved by static item capture
            'other_baseline_tier_ids_preserved':True,
            'native_revision':doc.get('git_revision'),
            'result_sha256':floor.source_sha(json_bytes)}

def run(binary:pathlib.Path, output:pathlib.Path)->int:
    output.mkdir(parents=True,exist_ok=True)
    receipt={'schema':SCHEMA, 'status':'BLOCKED','item_id':ITEM_ID,'item_ilevel':ITEM_ILVL,
             'test_only_not_user_selection':True, 'tier4_preserved':False,
             'special_effect_supported_proven':False,'native_invocations':0,
             'global_optimum_claim':False,'dps_comparison_allowed':False,
             'nonstat_effect_model_verified':False}
    try:
        source_text, fixture=pilot.source()
        verify_preconditions(source_text,binary)
        native_out=(output/'bare_item.json').resolve()
        inp=(output/'bare_item.simc').resolve()
        inp.write_text(make_bare(source_text,native_out),encoding='utf-8')
        receipt['source_input_sha256']=floor.source_sha(inp.read_bytes())
        receipt['baseline_profile_sha256']=fixture['portable_input_sha256']
        receipt['binary_sha256']=PINNED_BIN_SHA256
        receipt['native_invocations']=1
        proc=subprocess.run([str(binary),str(inp)], cwd=binary.parent,stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=90,check=False)
        (output/'stdout.txt').write_text(proc.stdout)
        (output/'stderr.txt').write_text(proc.stderr)
        receipt['exit_code']=proc.returncode
        need(proc.returncode==0,'NATIVE_SIMC_EXIT_'+str(proc.returncode))
        need(native_out.is_file() and native_out.stat().st_size>1000,'NATIVE_JSON2_ABSENT')
        native=read_bare_native(native_out.read_bytes())
        receipt['native']=native
        receipt['status']='PASS_NATIVE_BARE_ITEM_STATIC_ONLY_EFFECT_AND_TIER_UNVERIFIED'
    except Exception as ex:
        receipt['error']=type(ex).__name__+': '+str(ex)
    (output/'V039_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('V039_STATUS',receipt['status'],'native_invocations',receipt['native_invocations'],flush=True)
    return 0 if receipt['status'].startswith('PASS_NATIVE') else 3

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--binary',type=pathlib.Path,required=True)
    ap.add_argument('--output',type=pathlib.Path,required=True)
    args=ap.parse_args()
    raise SystemExit(run(args.binary.resolve(),args.output.resolve()))
