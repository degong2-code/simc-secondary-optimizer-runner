"""v094 bounded runtime tests, all offline. Synthetic rows are never real Native."""
import pathlib,sys,tempfile,hashlib,json,unittest
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
