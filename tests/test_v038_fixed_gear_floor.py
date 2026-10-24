import copy
import hashlib
import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('v038',ROOT/'runner'/'v038_fixed_gear_floor.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

def bare(slot='head',item_id=900111,ilevel=334,encoding=None,stats=None):
    if encoding is None:encoding=f'synthetic_item,id={item_id},ilevel={ilevel},source=local'
    values={'crit_rating':150,'haste_rating':0,'mastery_rating':100,'versatility_rating':0}
    if stats is not None:values=stats
    gear={'name':'synthetic_special_TEST_ONLY','encoded_item':encoding,'ilevel':ilevel,**values}
    doc={'report_version':'2.0.0','git_revision':v.PINNED_SIMC,'sim':{'players':[{'gear':{slot:gear}}]}}
    data=json.dumps(doc,sort_keys=True).encode('utf-8')
    selected={'slot':slot,'item_id':item_id,'ilevel':ilevel,
              'selection_provenance':'USER_SELECTED_ITEM_EXPLICITLY',
              'native_json_sha256':hashlib.sha256(data).hexdigest(),
              'effect_classification':'SELECTED_SPECIAL_NONTRINKET_MANUALLY_REVIEWED'}
    return data,selected

class V038EvidenceTests(unittest.TestCase):
    def test_extract_synthetic_stats_not_real_authority(self):
        b,s=bare()
        x=v.collect_verified_floor([s],{s['native_json_sha256']:b})
        self.assertEqual(x['special_fixed_rating'],{'crit_rating':150,'haste_rating':0,'mastery_rating':100,'versatility_rating':0})
        self.assertFalse(x['nonstat_item_effects_verified'])
        self.assertFalse(x['real_product_authority_promoted'])
    def test_missing_selected_blocks(self):
        with self.assertRaisesRegex(v.AdmissionBlocked,'VERIFIED_SELECTION_REQUIRED'):
            v.collect_verified_floor([], {})
    def test_missing_evidence_blocks(self):
        b,s=bare()
        with self.assertRaisesRegex(v.AdmissionBlocked,'MISSING_INDEPENDENT_BARE_ITEM_JSON2'):
            v.collect_verified_floor([s], {})
    def test_tampered_bytes_blocks(self):
        b,s=bare()
        with self.assertRaisesRegex(v.AdmissionBlocked,'NATIVE_EVIDENCE_SHA_CHANGED'):
            v.collect_verified_floor([s], {s['native_json_sha256']:b+b' '})
    def test_wrong_item_id_blocks(self):
        b,s=bare();s['item_id']+=1
        with self.assertRaisesRegex(v.AdmissionBlocked,'SELECTED_ITEM_ID_MISMATCH'):
            v.collect_verified_floor([s],{s['native_json_sha256']:b})
    def test_wrong_ilevel_blocks(self):
        b,s=bare();s['ilevel']+=1
        with self.assertRaisesRegex(v.AdmissionBlocked,'SELECTED_ITEM_LEVEL_MISMATCH'):
            v.collect_verified_floor([s],{s['native_json_sha256']:b})
    def test_not_special_classified_blocks(self):
        b,s=bare();s['effect_classification']='STANDARD_FLEXIBLE'
        with self.assertRaisesRegex(v.AdmissionBlocked,'ITEM_NOT_REVIEWED_SPECIAL'):
            v.collect_verified_floor([s],{s['native_json_sha256']:b})
    def test_user_selection_not_attested_blocks(self):
        b,s=bare();s['selection_provenance']='INFERRED_AUTOMATIC'
        with self.assertRaisesRegex(v.AdmissionBlocked,'ITEM_SELECTION_NOT_ATTESTED'):
            v.collect_verified_floor([s],{s['native_json_sha256']:b})
    def test_trinket_not_in_optimizer_pool(self):
        b,s=bare(slot='trinket1')
        with self.assertRaisesRegex(v.AdmissionBlocked,'TRINKETS_ARE_EXTERNAL'):
            v.collect_verified_floor([s],{s['native_json_sha256']:b})
    def test_crafted_item_not_bare(self):
        b,s=bare(encoding='embellished,id=900111,ilevel=334,crafted_stats=49/36,source=local')
        with self.assertRaisesRegex(v.AdmissionBlocked,'BARE_ITEM_NOT_ISOLATED:crafted_stats'):
            v.collect_verified_floor([s],{s['native_json_sha256']:b})
    def test_gem_item_not_bare(self):
        b,s=bare(encoding='enhanced,id=900111,ilevel=334,gem_id=999,source=local')
        with self.assertRaisesRegex(v.AdmissionBlocked,'BARE_ITEM_NOT_ISOLATED:gem_id'):
            v.collect_verified_floor([s],{s['native_json_sha256']:b})
    def test_enchant_item_not_bare(self):
        b,s=bare(encoding='enhanced,id=900111,ilevel=334,enchant=foo,source=local')
        with self.assertRaisesRegex(v.AdmissionBlocked,'BARE_ITEM_NOT_ISOLATED:enchant'):
            v.collect_verified_floor([s],{s['native_json_sha256']:b})
    def test_duplicate_slot_blocks(self):
        b,s=bare()
        with self.assertRaisesRegex(v.AdmissionBlocked,'DUPLICATE_SELECTED_ITEM'):
            v.collect_verified_floor([s,s],{s['native_json_sha256']:b})
    def test_unexpected_fields_blocks(self):
        b,s=bare();s['grant_everything']=True
        with self.assertRaisesRegex(v.AdmissionBlocked,'ITEM_CONTRACT_SHAPE'):
            v.collect_verified_floor([s],{s['native_json_sha256']:b})
    def test_invalid_native_version_blocks(self):
        b,s=bare();doc=json.loads(b);doc['report_version']='1.0.0';b=json.dumps(doc).encode();s['native_json_sha256']=hashlib.sha256(b).hexdigest()
        with self.assertRaisesRegex(v.AdmissionBlocked,'NATIVE_REPORT_VERSION_CHANGED'):
            v.collect_verified_floor([s],{s['native_json_sha256']:b})
    def test_invalid_revision_blocks(self):
        b,s=bare();doc=json.loads(b);doc['git_revision']='wrong';b=json.dumps(doc).encode();s['native_json_sha256']=hashlib.sha256(b).hexdigest()
        with self.assertRaisesRegex(v.AdmissionBlocked,'NATIVE_SIMC_COMMIT_CHANGED'):
            v.collect_verified_floor([s],{s['native_json_sha256']:b})
    def test_unverified_gear_secondary_type_blocks(self):
        b,s=bare(stats={'crit_rating':150.5,'haste_rating':0,'mastery_rating':100,'versatility_rating':0});
        with self.assertRaisesRegex(v.AdmissionBlocked,'NATIVE_ITEM_STAT_INVALID'):
            v.collect_verified_floor([s],{s['native_json_sha256']:b})
    def test_2_nontrinket_items_sum_without_extra_budget(self):
        b,s=bare();b2,s2=bare('back',900112,334,stats={'crit_rating':0,'haste_rating':30,'mastery_rating':40,'versatility_rating':0})
        x=v.collect_verified_floor([s,s2],{s['native_json_sha256']:b,s2['native_json_sha256']:b2})
        self.assertEqual(x['special_fixed_rating'],dict(zip(v.STATS,(150,30,140,0))))
    def test_missing_evidence_does_not_treat_v037_gear_as_authority(self):
        b,s=bare(encoding='crafted,id=900111,ilevel=334,crafted_stats=49/36,gem_id=999')
        with self.assertRaises(v.AdmissionBlocked):
            v.collect_verified_floor([s],{s['native_json_sha256']:b})

class V038ConstraintTests(unittest.TestCase):
    def setUp(self):
        self.manual={'crit_rating':100,'haste_rating':200,'mastery_rating':100,'versatility_rating':100}
        self.lock={'crit_rating':150,'haste_rating':0,'mastery_rating':100,'versatility_rating':0}
        self.cfg=v.enforce_constraints(3284,self.manual,self.lock)
    def test_total_locked_in_budget_not_plus(self):
        self.assertEqual(self.cfg['target_total_rating'],3284)
        self.assertEqual(self.cfg['free_rating_after_fixed_special_and_oil'],3002)
    def test_effective_floor_max_manual_or_oil_and_special(self):
        self.assertEqual(self.cfg['effective_candidate_minimum'],dict(zip(v.STATS,(166,200,100,100))))
    def test_trinket_not_added(self):
        self.assertFalse(self.cfg['external_trinket_enchant_rating_added_to_total'])
    def test_valid_candidate(self):
        self.assertTrue(v.check_candidate((619,1176,1150,339),self.cfg))
    def test_reassign_fixed_crit_blocks(self):
        with self.assertRaisesRegex(v.AdmissionBlocked,'LOCKED_FLOOR_OR_CAP_BREACH'):
            v.check_candidate((165,1265,1150,704),self.cfg)
    def test_reassign_manual_haste_blocks(self):
        with self.assertRaisesRegex(v.AdmissionBlocked,'LOCKED_FLOOR_OR_CAP_BREACH'):
            v.check_candidate((619,199,1150,1316),self.cfg)
    def test_total_changed_blocks(self):
        with self.assertRaisesRegex(v.AdmissionBlocked,'CHMV_TOTAL_MISMATCH'):
            v.check_candidate((619,1176,1150,338),self.cfg)
    def test_50pct_cap_blocks(self):
        with self.assertRaisesRegex(v.AdmissionBlocked,'LOCKED_FLOOR_OR_CAP_BREACH'):
            v.check_candidate((1800,500,500,484),self.cfg)
    def test_bool_stat_blocks(self):
        with self.assertRaisesRegex(v.AdmissionBlocked,'CANDIDATE_INVALID'):
            v.check_candidate((True,1176,1150,338),self.cfg)
    def test_locked_greater_than_cap_blocks(self):
        bad=dict(self.lock,crit_rating=1800)
        with self.assertRaisesRegex(v.AdmissionBlocked,'FIXED_FLOOR_EXCEEDS_50PCT_CAP'):
            v.enforce_constraints(3284,self.manual,bad)
    def test_manual_minimum_infeasible_blocks(self):
        bad=dict.fromkeys(v.STATS,1400)
        with self.assertRaisesRegex(v.AdmissionBlocked,'FIXED_FLOOR_EXCEEDS_TOTAL'):
            v.enforce_constraints(3284,bad,self.lock)
    def test_wrong_rating_keys_blocks(self):
        bad=dict(self.lock,intellect_rating=100)
        with self.assertRaisesRegex(v.AdmissionBlocked,'SPECIAL_LOCK_KEYS_INVALID'):
            v.enforce_constraints(3284,self.manual,bad)
    def test_zero_special_vector_oil_only(self):
        c=v.enforce_constraints(3184,dict.fromkeys(v.STATS,0),dict.fromkeys(v.STATS,0))
        self.assertEqual(c['effective_candidate_minimum'],dict(zip(v.STATS,v.OIL)))
    def test_no_equipment_removal_or_slot_optimizer(self):
        self.assertEqual(self.cfg['special_item_locked_in_total']['crit_rating'],150)
        self.assertEqual(self.cfg['manual_minimum']['crit_rating'],100)

class V038NativeConformanceTests(unittest.TestCase):
    def test_native_same_candidate(self):
        cfg=v.enforce_constraints(3284,dict.fromkeys(v.STATS,0),dict(zip(v.STATS,(150,0,100,0))))
        vec=(619,1176,1150,339)
        doc={'report_version':'2.0.0','git_revision':v.PINNED_SIMC,'sim':{'players':[{'collected_data':{'buffed_stats':{'stats':dict(zip(v.STATS,vec))}}}]}}
        self.assertEqual(v.pinned_native_result(doc,vec,cfg)['status'],'PASS_CANDIDATE_CHMV_AND_FLOOR_ONLY')
    def test_native_stat_drift_blocks(self):
        cfg=v.enforce_constraints(3284,dict.fromkeys(v.STATS,0),dict(zip(v.STATS,(150,0,100,0))))
        doc={'report_version':'2.0.0','git_revision':v.PINNED_SIMC,'sim':{'players':[{'collected_data':{'buffed_stats':{'stats':dict(zip(v.STATS,(600,1195,1150,339)))}}}]}}
        with self.assertRaisesRegex(v.AdmissionBlocked,'NATIVE_FINAL_RATING_MISMATCH'):
            v.pinned_native_result(doc,(619,1176,1150,339),cfg)

class V038CLITests(unittest.TestCase):
    def test_unattested_selection_fail_closed(self):
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t)
            request={'schema':'v038_original_selected_special_floor_v1','manual_total':3284,'manual_minimum':dict.fromkeys(v.STATS,0),'selected_special_equipment':[]}
            inp=root/'req.json';inp.write_text(json.dumps(request))
            out=root/'rec.json'
            self.assertEqual(v.main(['--request',str(inp),'--output',str(out)]),3)
            record=json.loads(out.read_text())
            self.assertEqual(record['status'],'BLOCKED')
            self.assertFalse(record['real_item_fixed_floor_verification_complete'])
    def test_synthetic_fixture_cli_only_provisional(self):
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t);store=root/'evidence';store.mkdir()
            b,s=bare();(store/'item.json').write_bytes(b)
            req={'schema':'v038_original_selected_special_floor_v1','manual_total':3284,'manual_minimum':dict.fromkeys(v.STATS,0),'selected_special_equipment':[s]}
            inp=root/'req.json';inp.write_text(json.dumps(req));out=root/'receipt.json'
            self.assertEqual(v.main(['--request',str(inp),'--evidence-directory',str(store),'--output',str(out)]),0)
            obj=json.loads(out.read_text())
            self.assertEqual(obj['candidate_contract']['effective_candidate_minimum']['crit_rating'],166)
            self.assertFalse(obj['bare_item_evidence']['real_product_authority_promoted'])

if __name__=='__main__':unittest.main()
