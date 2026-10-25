"""v045 bounded candidate: static G, approved J/F, no duplicate and fail-closed tests."""
import hashlib,json,pathlib,sys,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runner'))
import pilot
import v045_native_budget_candidate as v
EVIDENCE=ROOT/'integration_probes/evidence/v045_v042_native_static_334.json'

class V045Contract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=EVIDENCE.read_bytes()
        cls.case=v.plan(cls.data)
    def test_approved_budget_from_native(self):
        self.assertEqual([self.case[k] for k in ('G','J','F','T')],[2850,138,165,3153])
        self.assertEqual(sum(self.case['gear_override'].values()),2988)
        self.assertEqual(sum(self.case['target'].values()),3153)
        self.assertEqual(self.case['target']['haste_rating'],1125)
        self.assertEqual(self.case['gear_override']['haste_rating'],960)
    def test_no_oil_budget_promotion(self):
        self.assertTrue(self.case['oil_preserved_outside_T'])
        self.assertEqual(self.case['T'],2850+138+165)
        self.assertFalse(self.case['product_code_integrated'])
        self.assertFalse(self.case['official_policy_promoted'])
    def test_target_total_rejection(self):
        with self.assertRaisesRegex(v.Blocked,'TARGET_TOTAL_MISMATCH'):
            v.plan(self.data,(600,1125,1100,329))
    def test_special_head_floor_rejection(self):
        with self.assertRaisesRegex(v.Blocked,'LOCKED_FIXED_HEAD_BREACH'):
            v.plan(self.data,(600,1330,200,1023))
    def test_trial_cap_rejection(self):
        with self.assertRaisesRegex(v.Blocked,'TRIAL_STAT_CAP'):
            v.plan(self.data,(600,1700,525,328))
    def test_flask_double_subtraction_guard(self):
        with self.assertRaisesRegex(v.Blocked,'FLASK_SUBTRACTION_NEGATIVE'):
            v.plan(self.data,(1500,100,1200,353))
    def test_tampered_evidence_blocked(self):
        raw=bytearray(self.data);raw[14]^=1
        with self.assertRaisesRegex(v.Blocked,'EVIDENCE_BYTES_DRIFT'):
            v.plan(bytes(raw))
    def test_unapproved_selection_claim_blocked(self):
        d=json.loads(self.data);d['user_selected_item_attested']=True
        raw=json.dumps(d).encode()
        with patch.object(v,'EVIDENCE_SHA256',hashlib.sha256(raw).hexdigest()):
            with self.assertRaisesRegex(v.Blocked,'AUTHORITY_ESCALATION'):
                v.load_evidence(raw)
    def test_changed_head_mastery_blocked(self):
        d=json.loads(self.data);d['fixed_nontrinket_slots']['head']['mastery_rating']=402
        raw=json.dumps(d).encode()
        with patch.object(v,'EVIDENCE_SHA256',hashlib.sha256(raw).hexdigest()):
            with self.assertRaisesRegex(v.Blocked,'LOCKED_HEAD_CHANGED'):
                v.load_evidence(raw)
    def test_profile_items_unchanged(self):
        old,_=pilot.source()
        new=v.build_profile(old,pathlib.Path('/tmp/v045_unittest.json'),self.case)
        before=old.splitlines();after=new.splitlines()
        for slot in ('neck','shoulders','chest','waist','legs','feet','wrists',
                     'hands','finger1','finger2','trinket1','trinket2','back','main_hand'):
            self.assertEqual([l for l in before if l.startswith(slot+'=')],
                             [l for l in after if l.startswith(slot+'=')])
        self.assertIn('head='+v.v041.HEAD.split('=',1)[1],after)
        self.assertIn('flask=flask_of_the_blood_knights_2',after)
        self.assertIn('temporary_enchant=main_hand:thalassian_phoenix_oil_2',after)
    def test_one_override_line_per_stat(self):
        old,_=pilot.source()
        lines=v.build_profile(old,pathlib.Path('/tmp/v045_unittest.json'),self.case).splitlines()
        for stat,amount in self.case['gear_override'].items():
            self.assertEqual([l for l in lines if l.startswith('gear_'+stat+'=')],
                             ['gear_'+stat+'='+str(amount)])
    def test_wrong_native_rating_rejected(self):
        wrong={'sim':{'players':[{'collected_data':{'buffed_stats':{
             'stats':{**self.case['target'],'haste_rating':1126}}},'gear':{}}]}}
        with patch.object(v.v041,'audit_native',return_value={
               'head':{'fixed_mastery_rating':201}}):
            with self.assertRaisesRegex(v.Blocked,'FINAL_CHMV_MISMATCH'):
                v.audit_native(json.dumps(wrong).encode(),self.case)
    def test_plans_not_successful_native_evidence(self):
        self.assertEqual(self.case['status'],'PASS_BOUNDED_PLAN_NOT_PRODUCT')
        self.assertFalse(self.case['real_bonus_attested'])
        self.assertFalse(self.case['all_flasks_generalized'])

if __name__=='__main__': unittest.main()
