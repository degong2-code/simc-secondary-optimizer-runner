"""v094 bounded runtime tests, all offline. Synthetic rows are never real Native."""
import pathlib,sys,tempfile,hashlib,json,unittest
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runner'),str(ROOT/'tests')]
import v094_durable_inclusive_adaptive_runner as runner
import v091_weapon_oil_external_adapter as oil
import v093_inclusive_adaptive_scheduler_bridge as adaptive
import v046_static_item_cache as cache
from test_v091_weapon_oil_external_adapter import fury,FURY_TARGET,REV
from test_v093_inclusive_adaptive_scheduler_bridge import OTHER

def ob(base,mean,sem,iteration=80):
    o={'crit_rating':32,'haste_rating':32,'mastery_rating':0,'versatility_rating':0}
    return {'v092_base_target':dict(base),
            'target':{k:base[k]+o[k] for k in o},
            'iterations':iteration,'case_key':str(mean),
            'dps_mean':mean,'dps_sem':sem}

class V094Durable(unittest.TestCase):
    def test_95_only_and_material_alternatives(self):
        a={'crit_rating':838,'haste_rating':838,'mastery_rating':837,'versatility_rating':837}
        b={'crit_rating':438,'haste_rating':1238,'mastery_rating':837,'versatility_rating':837}
        o={'crit_rating':32,'haste_rating':32,'mastery_rating':0,'versatility_rating':0}
        summary=runner._candidate_summary([ob(a,204530,522),ob(b,204200,487)],3350,o)
        self.assertEqual(summary['observed_best_B'],a)
        self.assertEqual(summary['final_T'],3414)
        self.assertEqual(len(summary['material_alternatives']),1)
        q=summary['material_alternatives'][0]
        self.assertEqual(q['base_rating_moved'],400)
        self.assertGreater(q['diff_95_halfwidth_approx'],0)
        self.assertEqual(q['label'],'OBSERVED_NEAR_UNRESOLVED_AT_95')
        self.assertNotIn('diff_97_halfwidth_approx',q)
        self.assertEqual(summary['confidence_for_decision_and_display'],0.95)
        self.assertFalse(any('97' in k for k in summary))
        self.assertFalse(summary['global_optimum_proven'])

    def test_not_claim_material_alt_for_only_100_move(self):
        a=FURY_TARGET;b=OTHER
        o={'crit_rating':32,'haste_rating':32,'mastery_rating':0,'versatility_rating':0}
        result=runner._candidate_summary([ob(a,204000,600),ob(b,203000,800)],3350,o)
        self.assertTrue(result['no_material_alt_found'])

    def context(self,folder):
        p,c,f=fury(folder)
        prep=oil.prepare(p,c,f,cache.empty_cache(),'dual_two_hand',['main_hand','off_hand'])
        binary=pathlib.Path(folder)/'dummy-simc'
        binary.write_bytes(b'fake executable only, no new native will be called')
        sha=hashlib.sha256(binary.read_bytes()).hexdigest()
        ctx=adaptive.prepare(prep,sha,REV,35,80)
        return ctx,binary

    def test_native_budget_fails_before_any_simc_call(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx,binary=self.context(folder)
            output=pathlib.Path(folder)/'new'
            with self.assertRaisesRegex(runner.DurableBlocked,
                             'NATIVE_LIMIT_TOO_SMALL'):
                runner.run(ctx,[FURY_TARGET,OTHER],
                    {'crit_rating':0,'haste_rating':165,'mastery_rating':0,'versatility_rating':0},
                    binary,output,scouts=1,native_limit=4,cache_only=True)
            self.assertFalse(output.exists())

    def test_cache_only_and_cancel_block_without_simc(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx,binary=self.context(folder)
            output=pathlib.Path(folder)/'resume'
            F={'crit_rating':0,'haste_rating':165,'mastery_rating':0,'versatility_rating':0}
            with self.assertRaisesRegex(Exception,'CACHE_ONLY_REFUSES_NEW_NATIVE'):
                runner.run(ctx,[FURY_TARGET,OTHER],F,binary,output,
                           scouts=0,native_limit=4,cache_only=True)
            progress=json.loads((output/'V094_PROGRESS.json').read_text())
            self.assertEqual(progress['native_limit'],4)
            self.assertEqual(progress['new_native_attempts'],0)
            self.assertEqual(progress['status'],'PARTIAL_OR_BLOCKED')
            with self.assertRaisesRegex(runner.DurableBlocked,'DURABLE_SESSION_DRIFT'):
                runner.run(ctx,[FURY_TARGET,OTHER],F,binary,output,
                           scouts=0,native_limit=4,step=99,cache_only=True)
            stop=pathlib.Path(folder)/'CANCEL';stop.write_text('x')
            with self.assertRaisesRegex(runner.DurableBlocked,'USER_CANCEL_FILE_PRESENT'):
                runner.run(ctx,[FURY_TARGET,OTHER],F,binary,output,
                           scouts=0,native_limit=4,cancel_file=stop,cache_only=True)

    def test_cancel_two_of_four_then_resume_only_missing_and_replay_zero_native(self):
        """Exercise real v094 durable control flow using a synthetic executor.

        The executor and evaluator are fakes: this proves bounded orchestration
        and per-phase reuse, NOT SimC results or real JSON2 validation.
        """
        with tempfile.TemporaryDirectory() as folder:
            ctx,binary=self.context(folder)
            output=pathlib.Path(folder)/'partial_then_resume'
            stop=pathlib.Path(folder)/'CANCEL'
            F={'crit_rating':0,'haste_rating':165,
               'mastery_rating':0,'versatility_rating':0}
            O=ctx['identity']['oil_vector']
            native_fakes=[]
            cached_fakes=[]
            def request(context,target,flask,json_path,phase='scout'):
                path=pathlib.Path(json_path)
                return {'case_key':phase+'_'+path.parent.name,
                    'v092_base_target':dict(target),
                    'v092_fixed_O':dict(O),
                    'v092_final_T':ctx['identity']['approved_final_T'],
                    'target':{s:target[s]+O[s] for s in target},
                    'iterations':80 if phase=='confirm' else 35,
                    'input_sha256':'SYNTHETIC_OFFLINE_INPUT_ID',
                    'json2_location':str(path)}
            def execute(req,calibration,simc,case,progress,**kwargs):
                case=pathlib.Path(case)
                case.mkdir(parents=True,exist_ok=True)
                native_file=case/'result.json'
                receipt=case/'native_receipt.json'
                if native_file.exists():
                    self.assertTrue(receipt.is_file())
                    cached_fakes.append(case.name)
                    raw=native_file.read_bytes()
                    self.assertEqual(json.loads(receipt.read_text())['sha256'],
                                     hashlib.sha256(raw).hexdigest())
                    return {'source':'CACHED_VERIFIED_NATIVE',
                        'native_json_sha256':hashlib.sha256(raw).hexdigest(),
                        'case_key':req['case_key']}
                self.assertFalse(receipt.exists())
                native_fakes.append(case.name)
                raw=json.dumps({'sim':{'options':{'seed':len(native_fakes)}}},
                               sort_keys=True).encode('utf8')
                native_file.write_bytes(raw)
                receipt.write_text(json.dumps({'sha256':hashlib.sha256(raw).hexdigest()}))
                progress['native_attempts']+=1
                runner.save(case.parent/'V065_PROGRESS.json',progress)
                if len(native_fakes)==2:stop.write_text('cancel',encoding='utf8')
                return {'source':'NEW_NATIVE',
                    'native_json_sha256':hashlib.sha256(raw).hexdigest(),
                    'case_key':req['case_key']}
            def ingest(req,doc,raw):
                # Stub the separate, already-tested v064/v091 Native validator.
                return {'native_json_sha256':hashlib.sha256(raw).hexdigest(),
                    'case_key':req['case_key'],
                    'target':dict(req['target']),
                    'iterations':req['iterations'],
                    'dps_mean':200000+(100 if req['v092_base_target']==FURY_TARGET else 0),
                    'dps_sem':100.0,'dps_samples':35,
                    'input_sha256':req['input_sha256']}
            def confirmations(context,state,flask,directory):
                return {'cases':[request(context,vec,flask,
                    pathlib.Path(directory)/('confirm_%02d'%i)/'result.json',
                    'confirm') for i,vec in enumerate((FURY_TARGET,OTHER))]}
            with mock.patch.object(runner.engine,'execute_one',side_effect=execute), \
                 mock.patch.object(runner.oil,'ingest_native',side_effect=ingest), \
                 mock.patch.object(runner.adaptive,'request',side_effect=request), \
                 mock.patch.object(runner.adaptive,'project_native_for_v065',
                     side_effect=lambda req,obs:{'target':dict(req['v092_base_target'])}), \
                 mock.patch.object(runner.adaptive,'start_scout',
                     return_value={'observations':[],
                                   'completed_new_scouts':0,'scout_max':0}), \
                 mock.patch.object(runner.adaptive,'confirmation_plan',
                                   side_effect=confirmations), \
                 mock.patch.object(runner.adaptive,'fresh_judgment',
                     return_value={'pairwise_direction_supported':True}), \
                 mock.patch.object(runner.extended,'precision_plan',
                     return_value={'confidence':0.95}):
                opts={'scouts':0,'material_scouts':0,'native_limit':4,
                      'cancel_file':stop}
                with self.assertRaisesRegex(runner.DurableBlocked,
                                            'USER_CANCEL_FILE_PRESENT'):
                    runner.run(ctx,[FURY_TARGET,OTHER],F,binary,output,**opts)
                partial=runner.read_json(output/'V094_PROGRESS.json')
                self.assertEqual((partial['completed_jobs'],
                                  partial['new_native_attempts']),(2,2))
                self.assertEqual(partial['status'],'PARTIAL_OR_BLOCKED')
                self.assertEqual(native_fakes,['seed_00','seed_01'])
                saved={(p.relative_to(output).as_posix()):p.read_bytes()
                    for p in output.rglob('*') if p.name in
                        ('result.json','native_receipt.json')}
                stop.unlink()  # Mirrors v113's explicit same-session resume.
                resumed=runner.run(ctx,[FURY_TARGET,OTHER],F,binary,output,**opts)
                self.assertEqual(resumed['status'],
                                 'PASS_BOUNDED_SEEDS_AND_FRESH_CONFIRM_NO_SCOUT')
                self.assertEqual(len(resumed['observations']),4)
                self.assertEqual(resumed['new_native_attempts_cumulative'],4)
                self.assertEqual(resumed['verified_cache_hits_this_run'],2)
                self.assertEqual(native_fakes,
                                 ['seed_00','seed_01','confirm_00','confirm_01'])
                self.assertEqual(cached_fakes,['seed_00','seed_01'])
                self.assertTrue(all((output/path).read_bytes()==raw
                                    for path,raw in saved.items()))
                replay=runner.run(ctx,[FURY_TARGET,OTHER],F,binary,output,**opts)
                self.assertEqual(replay['new_native_attempts_cumulative'],4)
                self.assertEqual(replay['verified_cache_hits_this_run'],4)
                self.assertEqual(len(native_fakes),4)

    def test_tampered_cache_attempt_counter_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx,binary=self.context(folder)
            F={'crit_rating':0,'haste_rating':165,'mastery_rating':0,'versatility_rating':0}
            output=pathlib.Path(folder)/'wrong'
            with self.assertRaises(Exception):
                runner.run(ctx,[FURY_TARGET,OTHER],F,binary,output,
                           scouts=0,native_limit=4,cache_only=True)
            phase=output/'search'/'V065_PROGRESS.json'
            runner.save(phase,{'native_attempts':-1})
            with self.assertRaisesRegex(runner.DurableBlocked,'DURABLE_NATIVE_ATTEMPTS_INVALID'):
                runner.run(ctx,[FURY_TARGET,OTHER],F,binary,output,
                           scouts=0,native_limit=4,cache_only=True)

if __name__=='__main__':unittest.main()
