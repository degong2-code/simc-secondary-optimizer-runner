import copy
import importlib.util
import json
import os
import pathlib
import sys
import tempfile
import unittest

HERE=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('v037',HERE/'runner'/'v037_manual_budget_adapter.py')
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
CANON=json.loads((HERE/'runner'/'v037_request.json').read_text())

class V037ManualBudgetContract(unittest.TestCase):
    def req(self,**overrides):
        x=copy.deepcopy(CANON);x.update(overrides)
        return x
    def test_exact_input(self):
        self.assertEqual(v.load_request(self.req())['target_total_rating'],3284)
    def test_unknown_fields_refused(self):
        with self.assertRaisesRegex(v.InvalidContract,'FIELD_SET'):v.load_request(self.req(secret='abc'))
    def test_missing_fields_refused(self):
        x=self.req();x.pop('budget_origin')
        with self.assertRaisesRegex(v.InvalidContract,'FIELD_SET'):v.load_request(x)
    def test_invalid_rune_refused(self):
        with self.assertRaisesRegex(v.InvalidContract,'RUNE_SCOPE'):v.load_request(self.req(omnium_rune='haste'))
    def test_scenario_refused(self):
        with self.assertRaisesRegex(v.InvalidContract,'UNVERIFIED_SCENARIO'):v.load_request(self.req(scenario='blood_dk'))
    def test_budget_origin_refused(self):
        with self.assertRaisesRegex(v.InvalidContract,'BUDGET_ORIGIN'):v.load_request(self.req(budget_origin='ILVL334_VERIFIED'))
    def test_bool_total_refused(self):
        with self.assertRaisesRegex(v.InvalidContract,'TOTAL_OUTSIDE'):v.load_request(self.req(target_total_rating=True))
    def test_out_of_range_total_refused(self):
        with self.assertRaisesRegex(v.InvalidContract,'TOTAL_OUTSIDE'):v.load_request(self.req(target_total_rating=4001))
    def test_min_floor_outside_cap_refused(self):
        f=copy.deepcopy(CANON['minimum_target_rating']);f['crit_rating']=2200
        with self.assertRaisesRegex(v.InvalidContract,'MINIMUM_BOUNDS'):v.load_request(self.req(minimum_target_rating=f))
    def test_min_floor_negative_refused(self):
        f=copy.deepcopy(CANON['minimum_target_rating']);f['haste_rating']=-1
        with self.assertRaisesRegex(v.InvalidContract,'MINIMUM_BOUNDS'):v.load_request(self.req(minimum_target_rating=f))
    def test_min_floor_wrong_fields_refused(self):
        f=copy.deepcopy(CANON['minimum_target_rating']);f['intellect_rating']=500
        with self.assertRaisesRegex(v.InvalidContract,'INVALID_MINIMUM'):v.load_request(self.req(minimum_target_rating=f))
    def test_min_floor_bool_refused(self):
        f=copy.deepcopy(CANON['minimum_target_rating']);f['haste_rating']=True
        with self.assertRaisesRegex(v.InvalidContract,'INVALID_MINIMUM'):v.load_request(self.req(minimum_target_rating=f))
    def test_min_sum_impossible_refused(self):
        f=dict.fromkeys(v.STATS,1500)
        with self.assertRaisesRegex(v.InvalidContract,'MINIMUM_SUM'):v.load_request(self.req(minimum_target_rating=f))
    def test_scout_iter_refused(self):
        with self.assertRaisesRegex(v.InvalidContract,'SCOUT_ITERATIONS'):v.load_request(self.req(scout_iterations=10000))
    def test_confirm_iter_refused(self):
        with self.assertRaisesRegex(v.InvalidContract,'CONFIRM_ITERATIONS'):v.load_request(self.req(confirm_iterations=10000))
    def test_call_budget_refused(self):
        with self.assertRaisesRegex(v.InvalidContract,'NATIVE_BUDGET'):v.load_request(self.req(maximum_native_calls=200))
    def test_plan_scoped_flag(self):
        p=v.make_plan(v.load_request(self.req()))
        self.assertTrue(p['manual_total_not_physical_ilvl_proven'])
        self.assertFalse(p['original_v032_engine_modified_on_disk'])
        self.assertEqual(p['native_calls_permitted_max'],8)
    def test_seed_distinct_and_floors(self):
        cfg=v.load_request(self.req());s=v.seeds(cfg)
        self.assertEqual(len(s),5);self.assertEqual(len(set(s)),5)
        self.assertTrue(all(sum(x)==3284 for x in s))
        self.assertTrue(all(v.valid(x,3284,v.mins(cfg)) for x in s))
    def test_seed_at_original_total(self):
        cfg=v.load_request(self.req(target_total_rating=3184))
        s=v.seeds(cfg)
        self.assertEqual(len(set(s)),5)
        self.assertEqual(sum(s[0]),3184)
    def test_oil_lower_bound_enforced(self):
        cfg=v.load_request(self.req(minimum_target_rating=dict.fromkeys(v.STATS,0)))
        self.assertEqual(v.mins(cfg),v.OIL)
        self.assertFalse(v.valid((0,16,1634,1634),3284,v.mins(cfg)))
    def test_50pct_cap(self):
        cfg=v.load_request(self.req())
        self.assertFalse(v.valid((1800,400,600,484),3284,v.mins(cfg)))
    def test_reject_boolean_rating(self):
        cfg=v.load_request(self.req())
        self.assertFalse(v.valid((True,1200,1200,883),3284,v.mins(cfg)))
    def test_projection_integer_reproducible(self):
        cfg=v.load_request(self.req());low=v.mins(cfg)
        first=v.project((600,1140,1115,329),3284,low)
        self.assertEqual(first,v.project((600,1140,1115,329),3284,low))
        self.assertEqual(first,(619,1176,1150,339))
    def test_guided_function_with_original_after_adaptation(self):
        runtime=pathlib.Path(os.environ.get('V037_RUNTIME_DIR', '__NO_V037_RUNTIME__'))
        if not runtime.exists():self.skipTest('local v036 fixture not present')
        cfg=v.load_request(self.req())
        m,_=v.configure_original(runtime,cfg,None)
        fake=[{'target':dict(zip(v.STATS,x)),'dps':190000+i*300,'sem':900.0} for i,x in enumerate(v.seeds(cfg))]
        vec,meta=m.choose_guided(fake)
        self.assertTrue(v.valid(vec,3284,v.mins(cfg)))
        self.assertNotIn(vec,v.seeds(cfg))
        self.assertIn('estimated_gain_for_experiment_order_only',meta)
    def test_native_profile_3k2_total(self):
        runtime=pathlib.Path(os.environ.get('V037_RUNTIME_DIR', '__NO_V037_RUNTIME__'))
        if not runtime.exists():self.skipTest('local v036 fixture not present')
        cfg=v.load_request(self.req());m,_=v.configure_original(runtime,cfg,None)
        source=m.native_source(rune='crit')
        with tempfile.TemporaryDirectory() as t:
            for vec in v.seeds(cfg):
                profile,meta=m.make_profile(source,pathlib.Path(t)/'output.json',vec,120)
                self.assertEqual(meta['target'],dict(zip(v.STATS,vec)))
                self.assertEqual(sum(int(x.split('=')[1]) for x in profile.splitlines() if x.startswith('gear_'))+165,3284)
                self.assertIn('omnium_talents=136822:1/136817:1/136815:1/136814:1',profile)
    def test_confirm_unresolved_preserves_uncertainty(self):
        p={'target':dict(zip(v.STATS,(600,1200,1200,284))),'dps':195000,'sem':500}
        q={'target':dict(zip(v.STATS,(700,1300,800,484))),'dps':195800,'sem':530}
        z=v.summarize_confirm(p,q,self.req())
        self.assertFalse(z['statistically_separated_95pct_approx'])
        self.assertTrue(z['near_performance_unresolved'])
        self.assertTrue(z['materially_distinct_by_250_rating_pilot'])
        self.assertFalse(z['global_optimum_proven'])
    def test_confirm_strong_difference_not_equivalent(self):
        p={'target':dict(zip(v.STATS,(600,1200,1200,284))),'dps':195000,'sem':50}
        q={'target':dict(zip(v.STATS,(700,1300,800,484))),'dps':200000,'sem':50}
        z=v.summarize_confirm(p,q,self.req())
        self.assertTrue(z['statistically_separated_95pct_approx'])
        self.assertFalse(z['near_performance_unresolved'])
    def test_offline_cli_receipt(self):
        with tempfile.TemporaryDirectory() as t:
            p=pathlib.Path(t)
            req=p/'request.json';req.write_text(json.dumps(CANON))
            rc=v.main(['--mode','plan','--request',str(req),'--output',str(p/'out')])
            self.assertEqual(rc,0)
            self.assertEqual(json.loads((p/'out'/'V037_PLAN.json').read_text())['target_total_rating'],3284)
    def test_fail_closed_cli_receipt(self):
        with tempfile.TemporaryDirectory() as t:
            p=pathlib.Path(t)
            req=p/'request.json';req.write_text('{"bad":"request"}')
            rc=v.main(['--mode','plan','--request',str(req),'--output',str(p/'out')])
            self.assertEqual(rc,3)
            self.assertIn('REQUEST_FIELD_SET_CHANGED',(p/'out'/'V037_BLOCKED.json').read_text())
if __name__=='__main__':unittest.main()