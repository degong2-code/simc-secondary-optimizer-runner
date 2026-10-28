#!/usr/bin/env python3
"""v094 generic bounded B-search -> final T+O Native workflow.

Orchestrates EXISTING v093/v091/v092/v065. This does not implement a new
optimizer, item-effect model, or full Windows UI. Receipts are SHA-verified by
v065/v064, plus v091 Native oil; interrupted partial Native outputs fail closed.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, pathlib, sys
import v046_static_item_cache as static_cache
import v061_scenario_contract as scenario
import v065_original_scheduler_native_bridge as engine
import v065_v015_scheduler_adapter as policy
import v091_weapon_oil_external_adapter as oil
import v093_inclusive_adaptive_scheduler_bridge as adaptive
import v095_material_precision_policy as extended

SCHEMA='v094_generic_durable_inclusive_adaptive_v1'
Z95=1.959963984540054
class DurableBlocked(ValueError): pass
def need(ok,reason):
    if not ok: raise DurableBlocked(reason)
def digest(obj):
    return static_cache.digest(obj)
def read_json(path):
    return json.loads(pathlib.Path(path).read_text(encoding='utf8'))
def save(path,obj):
    engine.write_atomic(path,obj)
def _recover_attempts(path,limit):
    p=path/'V065_PROGRESS.json'
    if not p.exists(): return 0
    value=read_json(p)
    need(type(value) is dict and type(value.get('native_attempts')) is int
         and 0<=value['native_attempts']<=limit,
         'DURABLE_NATIVE_ATTEMPTS_INVALID')
    return value['native_attempts']
def _candidate_summary(observations, B, O, near_loss=0.01, material=0.10):
    """Report only actually observed samples at the user-selected 95%."""
    need(type(observations) is list and bool(observations),'NO_NATIVE_OBSERVATIONS')
    need(type(B) is int and B>0 and type(O) is dict,'BAD_B_O')
    # Repeated high-iteration confirmation supersedes lower-iteration scout
    # for the same base vector; keep every native receipt separately on disk.
    by_base={}
    for r in observations:
        b=r['v092_base_target']; k=policy.key(b)
        need(sum(k)==B and sum(r['target'].values())==B+sum(O.values())
             and all(r['target'][s]==b[s]+O[s] for s in scenario.STATS),
             'SAMPLED_B_TO_T_DRIFT')
        current=by_base.get(k)
        if current is None or (r['iterations'],r['case_key'])>(current['iterations'],current['case_key']):
            by_base[k]=r
    rows=sorted(by_base.values(),key=lambda v:(-v['dps_mean'],v['case_key']))
    best=rows[0]
    alts=[]
    for r in rows[1:]:
        moved=sum(abs(best['v092_base_target'][s]-r['v092_base_target'][s])
                  for s in scenario.STATS)/2
        delta=best['dps_mean']-r['dps_mean']
        combined=math.hypot(best['dps_sem'],r['dps_sem'])
        distance=moved/B
        loss=delta/best['dps_mean']
        if distance>=material and loss<=near_loss:
            alts.append({'B':r['v092_base_target'],'T':r['target'],
                 'dps_mean':r['dps_mean'],'dps_sem':r['dps_sem'],
                 'base_rating_moved':moved,'fraction_B_moved':distance,
                 'observed_relative_dps_loss':loss,
                 'diff_95_halfwidth_approx':Z95*combined,
                 'difference_95_separated':delta>Z95*combined,
                 'label':('OBSERVED_NEAR_BUT_LOWER_AT_95' if delta>Z95*combined
                          else 'OBSERVED_NEAR_UNRESOLVED_AT_95')})
    return {'schema':'v094_observed_candidates_nonoptimal_v1',
        'official_formula':'T=G+J+F+O','underlying_B':B,
        'fixed_O':dict(O),'final_T':B+sum(O.values()),
        'observed_unique_targets':len(rows),
        'observed_best_B':best['v092_base_target'],
        'observed_best_T':best['target'],
        'observed_best_dps':best['dps_mean'],
        'observed_best_sem':best['dps_sem'],
        'confidence_for_decision_and_display':0.95,
        'material_alternatives':alts,'material_threshold_B_fraction':material,
        'near_loss_threshold':near_loss,
        'no_material_alt_found':not bool(alts),
        'global_optimum_proven':False}

def run(context, seed_targets, flask_vector, binary, output, *,
        step=100, scouts=1, material_scouts=0, native_limit=None, cache_only=False,
        cancel_file=None, open_folder=False,recover_verified_partial=False):
    """One bounded deterministic session, resumable by same identity.

    Native limit is enforced across seeds+scouts+fresh confirmations. Caller
    may change scenario runtime.max_native_calls explicitly, but never exceed
    that typed contract by passing native_limit.
    """
    output=pathlib.Path(output).resolve()
    binary=pathlib.Path(binary).resolve()
    need(type(seed_targets) in (tuple,list) and len(seed_targets)==2,
         'TWO_DISTINCT_SEED_TARGETS_REQUIRED')
    need(type(scouts) is int and 0<=scouts<=2,'BOUNDED_SCOUT_COUNT_0_TO_2')
    need(type(material_scouts) is int and 0<=material_scouts<=2,
         'BOUNDED_MATERIAL_SCOUT_COUNT_0_TO_2')
    need(type(step) is int and step>0,'SCOUT_STEP_REQUIRED')
    cfg=context['bundle']['prepared']['scenario']
    runtime=cfg['scenario']['runtime']
    max_calls=runtime['max_native_calls']
    budget=max_calls if native_limit is None else native_limit
    need(type(budget) is int and 0<=budget<=max_calls,
         'NEW_NATIVE_LIMIT_MUST_NOT_EXCEED_TYPED_SCENARIO')
    need(binary.is_file(),'SIMC_BINARY_NOT_FOUND')
    need(hashlib.sha256(binary.read_bytes()).hexdigest()==context['identity']['binary_sha256'],
         'SIMC_BINARY_SHA_CHANGED')
    expected=adaptive.identity(context['bundle'],context['identity']['binary_sha256'],
        context['identity']['revision'],context['identity']['scout_iterations'],
        context['identity']['confirm_iterations'])
    need(expected==context['identity'],'ADAPTIVE_CONTEXT_IDENTITY_DRIFT')
    scenario.vector(flask_vector,'V094_STATIC_F')
    need(sum(flask_vector.values())==cfg['budget']['F'],'FLASK_F_NOT_SCENARIO')
    seeds=[dict(v) for v in seed_targets]
    need(all(sum(v.values())==context['identity']['base_B'] for v in seeds)
         and policy.key(seeds[0])!=policy.key(seeds[1]),
         'SEED_BASE_B_NOT_DISTINCT_OR_INVALID')
    B=context['identity']['base_B'];O=context['identity']['oil_vector']
    seed_identity={'schema':SCHEMA,'policy_context':context['identity'],
       'seed_base_targets':seeds,'flask_F_vector':dict(flask_vector),
       'step':step,'scout_limit':scouts,
       'material_scout_limit':material_scouts,'native_limit':budget,
       'stat_confidence_for_decision':0.95}
    # Fail before any SimC attempt if a brand-new session lacks enough
    # permitted calls for two seeds, requested scouts and confirmations.
    if not output.exists() or not any(output.iterdir()):
        need(2+scouts+material_scouts+2<=budget,
             'NATIVE_LIMIT_TOO_SMALL_FOR_SEEDS_SCOUTS_CONFIRMATIONS')
    output.mkdir(parents=True,exist_ok=True)
    seal=output/'V094_SESSION_IDENTITY.json'
    if seal.exists():need(read_json(seal)==seed_identity,'DURABLE_SESSION_DRIFT')
    else:
        need(not any(output.iterdir()),'UNSEALED_OUTPUT_IS_NOT_EMPTY')
        save(seal,seed_identity)
    main_folder=output/'search'
    confirm_folder=output/'confirmations'
    main_folder.mkdir(exist_ok=True);confirm_folder.mkdir(exist_ok=True)
    progress_path=output/'V094_PROGRESS.json'
    report_path=output/'V094_RESULT.json'
    progress={'schema':SCHEMA,'identity_sha256':digest(seed_identity),
       'status':'STARTED','new_native_attempts':0,
       'native_limit':budget,'stages_completed':[],'cache_verified_hits':0}
    if progress_path.exists():
        prev=read_json(progress_path)
        need(prev.get('identity_sha256')==progress['identity_sha256']
             and prev.get('native_limit')==budget,
             'DURABLE_PROGRESS_IDENTITY_CHANGED')
        progress=prev
    # Per-invocation cache count, not an accumulating historical total.
    progress['cache_verified_hits']=0
    all_observations=[];projected=[]
    try:
        def checkpoint(status):
            progress['status']=status
            progress['new_native_attempts']=_recover_attempts(main_folder,4)+_recover_attempts(confirm_folder,4)
            progress['completed_jobs']=len(all_observations)
            progress['planned_jobs']=2+scouts+material_scouts+2
            progress['progress_percent']=round(100*len(all_observations)/(2+scouts+material_scouts+2),1)
            save(progress_path,progress)
            print('[v094]',status,'native',progress['new_native_attempts'],'/',budget,
                  'cache',progress['cache_verified_hits'],flush=True)
        def native(req,folder,phase):
            if cancel_file and pathlib.Path(cancel_file).exists():
                raise DurableBlocked('USER_CANCEL_FILE_PRESENT')
            used_main=_recover_attempts(main_folder,4)
            used_confirm=_recover_attempts(confirm_folder,4)
            used=used_main+used_confirm
            have_cached=(folder/'result.json').is_file() and (folder/'native_receipt.json').is_file()
            if not have_cached and used>=budget:
                raise DurableBlocked('APPROVED_NATIVE_CALL_BUDGET_EXHAUSTED')
            phase_progress={'native_attempts':_recover_attempts(folder.parent,4),
                 'status':'RUNNING','phase':phase}
            direct=engine.execute_one(req,{'native_revision':context['identity']['revision']},
                   binary,folder,phase_progress,cancel_file=cancel_file,
                   cache_only=cache_only,
                   recover_verified_partial=recover_verified_partial)
            raw=(folder/'result.json').read_bytes()
            full=oil.ingest_native(req,json.loads(raw),raw)
            need(direct['native_json_sha256']==full['native_json_sha256']
                 and direct['case_key']==full['case_key'],
                 'EXISTING_NATIVE_AND_OIL_RECEIPT_DISAGREE')
            full['simc_seed']=(json.loads(raw).get('sim') or {}).get('options',{}).get('seed')
            full['v092_base_target']=req['v092_base_target']
            full['v092_fixed_O']=req['v092_fixed_O']
            full['v092_final_T']=req['v092_final_T']
            full['v093_phase']=phase
            full['source']=direct['source']
            if direct['source']=='CACHED_VERIFIED_NATIVE':
                progress['cache_verified_hits']+=1
            all_observations.append(full)
            checkpoint(phase+'_VERIFIED')
            return full
        checkpoint('SESSION_IDENTITY_VERIFIED')
        for i,t in enumerate(seeds):
            folder=main_folder/('seed_%02d'%i)
            req=adaptive.request(context,t,flask_vector,folder/'result.json','seed')
            obs=native(req,folder,'SEED_%02d'%i)
            projected.append(adaptive.project_native_for_v065(req,obs))
        state=adaptive.start_scout(context,projected,step=step,
                                   scout_max=scouts,flask_vector=flask_vector)
        for i in range(scouts):
            folder=main_folder/('scout_%02d'%i)
            plan=adaptive.next_scout(context,state,flask_vector,folder/'result.json')
            obs=native(plan['request'],folder,'SCOUT_%02d'%i)
            state=adaptive.accept_scout(context,state,plan['request'],obs)
        # Material candidates are deliberately farther in CHMV-space.
        # Selection itself is v065.neighbors with a larger user-visible step;
        # do not declare a near-DPS alternative until Native measurement.
        material_proposals=[]
        for i in range(material_scouts):
            pp=extended.material_neighbor(cfg,adaptive.feasible_budget(context,flask_vector),
                 state['observations'],fraction=0.10)
            folder=main_folder/('material_%02d'%i)
            req=adaptive.request(context,pp['candidate_B'],flask_vector,
                 folder/'result.json','scout')
            obs=native(req,folder,'MATERIAL_%02d'%i)
            projected_native=adaptive.project_native_for_v065(req,obs)
            state['observations'].append(projected_native)
            material_proposals.append({
                'base_B':pp['candidate_B'], 'native_T':req['target'],
                'rating_transferred':pp['rating_transferred'],
                'measured_dps':obs['dps_mean'], 'measured_sem':obs['dps_sem']})
        pair=adaptive.confirmation_plan(context,state,flask_vector,confirm_folder)
        confirmed=[]
        for i,req in enumerate(pair['cases']):
            folder=confirm_folder/('confirm_%02d'%i)
            obs=native(req,folder,'CONFIRM_%02d'%i)
            confirmed.append(obs)
        confidence=adaptive.fresh_judgment(pair['cases'],confirmed)
        summary=_candidate_summary(all_observations,B,O)
        # 95% alone: more precision can be requested only within explicitly
        # typed scenario iteration ceiling and separately authorized calls.
        ceiling=cfg['scenario']['runtime']['confirm_iterations']
        precision=extended.precision_plan(confirmed[0],confirmed[1],ceiling)
        status=('PASS_BOUNDED_GENERIC_NATIVE_SEARCH_AND_CACHE' if scouts else
                'PASS_MATERIAL_SCOUT_AND_FRESH_CONFIRM' if material_scouts else
                'PASS_BOUNDED_SEEDS_AND_FRESH_CONFIRM_NO_SCOUT')
        report={'schema':SCHEMA,'status':status,
                'policy_source':'v065_v015_derived_in_B',
                'official_formula':'T=G+J+F+O','B':B,'fixed_O':O,
                'official_final_T':B+sum(O.values()),
                'observations':[{'phase':r.get('v093_phase'),
                      'base_B':r['v092_base_target'],'final_T':r['target'],
                      'dps_mean':r['dps_mean'],'dps_sem':r['dps_sem'],
                      'samples':r['dps_samples'],'input_sha256':r['input_sha256'],
                      'native_sha256':r['native_json_sha256'],
                      'case_key':r['case_key'],'source':r['source']}
                     for r in all_observations],
                'confirmation':confidence,'alternatives':summary,
                'precision_next_step':precision,
                'material_scouts_measured':material_proposals,
                'new_native_attempts_cumulative':_recover_attempts(main_folder,4)+_recover_attempts(confirm_folder,4),
                'verified_cache_hits_this_run':progress['cache_verified_hits'],
                'global_optimum_proven':False,
                'scouts_completed':scouts,
                'material_scouts_completed':material_scouts,
                'original_v015_v016_product_integrated':False}
        save(report_path,report)
        progress.pop('error',None)
        checkpoint(status)
        return report
    except Exception as exc:
        progress['error']=type(exc).__name__+':'+str(exc)
        checkpoint('PARTIAL_OR_BLOCKED')
        raise
    finally:
        if open_folder and os.name=='nt':
            try:os.startfile(str(output))
            except Exception:pass

def main(argv=None):
    ap=argparse.ArgumentParser(description='Bounded approved oil-inclusive CHMV Native adaptive runner')
    ap.add_argument('--context-json',required=True)
    ap.add_argument('--seeds-json',required=True)
    ap.add_argument('--flask-json',required=True)
    ap.add_argument('--simc',required=True)
    ap.add_argument('--output',required=True)
    ap.add_argument('--scouts',type=int,default=1)
    ap.add_argument('--material-scouts',type=int,default=0)
    ap.add_argument('--step',type=int,default=100)
    ap.add_argument('--max-native',type=int)
    ap.add_argument('--cancel-file')
    ap.add_argument('--cache-only',action='store_true')
    args=ap.parse_args(argv)
    try:
        result=run(read_json(args.context_json),read_json(args.seeds_json),
              read_json(args.flask_json),args.simc,args.output,
              scouts=args.scouts,material_scouts=args.material_scouts,
              step=args.step,native_limit=args.max_native,
              cancel_file=args.cancel_file,cache_only=args.cache_only,open_folder=True)
        print(json.dumps({'status':result['status'],'result':str(pathlib.Path(args.output).resolve()/'V094_RESULT.json')},ensure_ascii=False))
        return 0
    except Exception as exc:
        print('V094_BLOCKED_OR_PARTIAL:',type(exc).__name__,str(exc),file=sys.stderr)
        print('Result folder:',pathlib.Path(args.output).resolve(),file=sys.stderr)
        return 3
if __name__=='__main__':sys.exit(main())
