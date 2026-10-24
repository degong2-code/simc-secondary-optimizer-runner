#!/usr/bin/env python3
"""v038 single Native CHMV candidate: SYNTHETIC floor demo, not real item proof.

Reuses the unmodified original v032 runtime and the verified v037 adapter.
Strictly one 120-iteration SimC invocation; no new item/effect supported.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import pathlib
import sys

ROOT=pathlib.Path(__file__).resolve().parent

def load(name, filename):
    spec=importlib.util.spec_from_file_location(name,ROOT/filename)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

v037=load('v037_manual_budget_adapter','v037_manual_budget_adapter.py')
v038=load('v038_fixed_gear_floor','v038_fixed_gear_floor.py')
TEST_LOCK=dict(zip(v038.STATS,(150,0,100,0)))
TEST_MANUAL=dict.fromkeys(v038.STATS,0)


def run(runtime, binary, output):
    output.mkdir(parents=True,exist_ok=True)
    evidence={'schema':'v038_synthetic_floor_native_probe_v1','status':'STARTED',
              'synthetic_special_item_fixture_only':True,'real_selected_item_attested':False,
              'native_simc_invocations':0,'original_v032_source_modified':False,
              'no_actual_special_effect_validation':True,'no_global_optimum_claim':True}
    try:
        # Native calculation is permitted only under existing v035 SHA pin.
        assert binary.is_file() and hashlib.sha256(binary.read_bytes()).hexdigest()==v038.PINNED_BINARY, 'SIMC_BINARY_SHA_MISMATCH'
        contract=v038.enforce_constraints(3284,TEST_MANUAL,TEST_LOCK)
        assert contract['free_rating_after_fixed_special_and_oil']==3002
        cfg=json.loads((ROOT/'v037_request.json').read_text())
        cfg['minimum_target_rating']=contract['effective_candidate_minimum']
        cfg=v037.load_request(cfg)
        seeds=v037.seeds(cfg)
        for vec in seeds:v038.check_candidate(vec,contract)
        evidence['candidate_floor_contract']=contract
        evidence['seed_vectors']=[v038.objvec(vec) for vec in seeds]
        m,provenance=v037.configure_original(runtime,cfg,binary)
        src=m.native_source(rune='crit')
        vec=seeds[0]
        v038.check_candidate(vec,contract)
        evidence['native_simc_invocations']=1
        entry=m.run_case(binary,output/'NATIVE_01',src,vec,120,'crit')
        assert entry['status']=='NATIVE_STATS_AND_RUNE_PASS','ORIGINAL_V032_NATIVE_REJECTED'
        native_json=json.loads((output/'NATIVE_01'/'result.json').read_text())
        evidence['native_conformance']=v038.pinned_native_result(native_json,vec,contract)
        evidence['native_case']=entry
        evidence['original_v032_zip_sha256']=provenance['source_original_zip_sha256']
        evidence['status']='PASS_SYNTHETIC_FIXED_FLOOR_NATIVE_ONE_CASE_NOT_REAL_ITEM'
    except Exception as e:
        evidence['status']='BLOCKED'
        evidence['reason']=type(e).__name__+':'+str(e)
    (output/'V038_NATIVE_RECEIPT.json').write_text(json.dumps(evidence,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    print('V038_NATIVE_STATUS',evidence['status'],'calls',evidence['native_simc_invocations'])
    return 0 if evidence['status'].startswith('PASS_') else 3


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--runtime',type=pathlib.Path,required=True)
    p.add_argument('--binary',type=pathlib.Path,required=True)
    p.add_argument('--output',type=pathlib.Path,required=True)
    a=p.parse_args()
    return run(a.runtime.resolve(),a.binary.resolve(),a.output.resolve())

if __name__=='__main__':raise SystemExit(main())
