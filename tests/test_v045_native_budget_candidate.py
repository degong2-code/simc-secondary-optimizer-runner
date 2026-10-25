"""v045: Native equipment and oil-floor constraints; no product promotion."""
import json,pathlib,sys,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runner'))
import pilot
import v044_static_budget_attribution as v044
import v045_native_budget_candidate as v
import test_v044_static_budget_attribution as f

def inventory_fixture():
    doc=f.fixture(); gear=doc['sim']['players'][0]['gear']
    for g in gear.values():g['name']=g['encoded_item'].split(',')[0]
    inp='\n'.join(slot+'='+gear[slot]['encoded_item'] for slot in v044.SLOTS).encode()
    base={'static_nontrinket_gear_sum_all_stats':2850,
          'trinket_gear_secondary_external':dict.fromkeys(v.STATS,0),
          'final_minus_gear_override':dict(zip(v.STATS,(0,165,0,0)))}
    return inp,json.dumps(doc).encode(),base

class V045Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        x,y,z=inventory_fixture()
        with patch.object(v044,'analyze',return_value=z):
            cls.inv=v.audit_inventory(x,y)
        cls.case=v.make_plan(cls.inv)
    def test_native_all_slots(self):
        self.assertEqual(self.inv['slots_checked'],15)
        self.assertEqual(len(self.inv['items']),15)
        self.assertFalse(self.inv['json_item_hints_used_for_identity_only'])
        self.assertTrue(all(not x['external_name_canonicality_verified'] for x in self.inv['items']))
    def test_oil_and_policy_separate(self):
        c=self.case
        self.assertEqual([c[k] for k in ('G','J','F','v1_0_official_T','bounded_trial_T')],[2850,138,165,3153,3185])
        self.assertEqual([c['required_static_floor'][k] for k in v.STATS],[16,16,201,0])
        self.assertEqual(sum(c['candidate'].values()),3185)
        self.assertEqual(sum(c['gear_override'].values()),3020)
        self.assertEqual(c['gear_override']['haste_rating'],975)
        self.assertFalse(c['official_policy_promoted'])
        self.assertFalse(c['product_code_integrated'])
    def test_stat_total_fail_closed(self):
        with self.assertRaisesRegex(v.Blocked,'CHMV_TOTAL_MISMATCH'):
            v.make_plan(self.inv,(600,1140,1115,329))
    def test_floor_fail_closed(self):
        with self.assertRaisesRegex(v.Blocked,'CANDIDATE_FIXED_FLOOR_OR_CAP_BREACH'):
            v.make_plan(self.inv,(700,1200,200,1085))
    def test_cap_fail_closed(self):
        with self.assertRaisesRegex(v.Blocked,'CANDIDATE_FIXED_FLOOR_OR_CAP_BREACH'):
            v.make_plan(self.inv,(1700,600,600,285))
    def test_native_item_id_drift_fail_closed(self):
        src,raw,m=inventory_fixture()
        data=json.loads(raw)
        data['sim']['players'][0]['gear']['neck']['encoded_item']=data['sim']['players'][0]['gear']['neck']['encoded_item'].replace('id=210001','id=999999')
        with patch.object(v044,'analyze',return_value=m):
            with self.assertRaisesRegex(v.Blocked,'SIMC_OPTION_MISMATCH:neck:id'):
                v.audit_inventory(src,json.dumps(data).encode())
    def test_native_name_drift_fail_closed(self):
        src,raw,m=inventory_fixture()
        data=json.loads(raw);data['sim']['players'][0]['gear']['neck']['name']='wrong'
        with patch.object(v044,'analyze',return_value=m):
            with self.assertRaisesRegex(v.Blocked,'NATIVE_ITEM_NAME_FIELD_DRIFT:neck'):
                v.audit_inventory(src,json.dumps(data).encode())
    def test_native_static_drift_fail_closed(self):
        src,raw,m=inventory_fixture()
        data=json.loads(raw);data['sim']['players'][0]['gear']['head']['mastery_rating']=202
        with patch.object(v044,'analyze',return_value=m):
            with self.assertRaisesRegex(v.Blocked,'HEAD_FIXED_MASTERY_CHANGED'):
                v.audit_inventory(src,json.dumps(data).encode())
    def test_candidate_changes_only_overrides(self):
        source,_=pilot.source()
        old=v.v041.build_source(source,pathlib.Path('/tmp/v045-test.json'))
        new=v.build_profile(source,pathlib.Path('/tmp/v045-test.json'),self.case)
        for slot in v044.SLOTS:
            self.assertEqual(v.parse_slots(old)[slot],v.parse_slots(new)[slot])
        for k,val in self.case['gear_override'].items():
            self.assertIn('gear_'+k+'='+str(val),new)
        self.assertEqual(sum(x.startswith('json2=') for x in new.splitlines()),1)

if __name__=='__main__':unittest.main()
