import copy
import json
import pathlib
import sys
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runner'))
import pilot
import v041_catalyst_gem_proc_probe as v

class CatalystGem(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.src,_=pilot.source()
 def test_gem_retained_input(self):
  inp=v.build_source(self.src,ROOT/'v041_test.json')
  head=next(s for s in inp.splitlines() if s.startswith('head='))
  self.assertEqual(head,v.HEAD)
  self.assertIn('gem_id=240967',head)
  self.assertIn('bonus_id=13846',head)
 def test_rest_baseline_unchanged(self):
  inp=v.build_source(self.src,ROOT/'v041_test.json')
  for slot in ['neck','shoulders','chest','hands','legs','trinket1','trinket2','main_hand']:
   old=next(x for x in self.src.splitlines() if x.startswith(slot+'='))
   self.assertIn(old,inp.splitlines())
 def test_rune_crit(self):
  inp=v.build_source(self.src,ROOT/'v041_test.json')
  self.assertIn(v.bare.CRIT_RUNE,inp)
  self.assertNotIn(v.bare.HASTE_RUNE,inp)
 def test_v040_replaced_head_only_once(self):
  inp=v.build_source(self.src,ROOT/'v041_test.json')
  self.assertEqual(sum(line.startswith('head=') for line in inp.splitlines()),1)
 def test_invalid_baseline_gem_blocked(self):
  with self.assertRaisesRegex(v.Refused,'BASELINE_HEAD_CHANGED'):
   v.build_source(self.src.replace('gem_id=240967','gem_id=240983'),ROOT/'x.json')
 def test_json2_native_fixture_positive(self):
  src=copy.deepcopy(self.minimal_native())
  self.assertEqual(v.audit_native(json.dumps(src).encode())['head']['gem_id'],240967)
 def test_missing_gem_fails(self):
  d=self.minimal_native();d['sim']['players'][0]['gear']['head']['encoded_item']=d['sim']['players'][0]['gear']['head']['encoded_item'].replace(',gem_id=240967','')
  with self.assertRaisesRegex(v.Refused,'GEM_NOT_RETAINED_IN_JSON2'):v.audit_native(json.dumps(d).encode())
 def test_missing_proc_fails(self):
  d=self.minimal_native();d['sim']['players'][0]['buffs']=[b for b in d['sim']['players'][0]['buffs'] if b['name']!='venomcursed_mastery']
  with self.assertRaisesRegex(v.Refused,'VENOMCURSED_NOT_TRIGGERED'):v.audit_native(json.dumps(d).encode())
 def test_missing_tier_fails(self):
  d=self.minimal_native();d['sim']['players'][0]['buffs']=[b for b in d['sim']['players'][0]['buffs'] if b['name']!='cumulative_power']
  with self.assertRaisesRegex(v.Refused,'FOUR_PIECE_MISSING'):v.audit_native(json.dumps(d).encode())
 def test_wrong_bonus_fails(self):
  d=self.minimal_native();h=d['sim']['players'][0]['gear']['head'];h['encoded_item']=h['encoded_item'].replace('bonus_id=13846','bonus_id=13848')
  with self.assertRaisesRegex(v.Refused,'BONUS_CHANGED'):v.audit_native(json.dumps(d).encode())
 def test_wrong_redirection_fails(self):
  d=self.minimal_native();h=d['sim']['players'][0]['gear']['head'];h['encoded_item']=h['encoded_item'].replace('redirected_base_stats=271874','redirected_base_stats=1')
  with self.assertRaisesRegex(v.Refused,'ORIGIN_CHANGED'):v.audit_native(json.dumps(d).encode())
 def test_static_mismatch_fails(self):
  d=self.minimal_native();d['sim']['players'][0]['gear']['head']['mastery_rating']=402
  with self.assertRaisesRegex(v.Refused,'BARE_MASTERY_CHANGED'):v.audit_native(json.dumps(d).encode())
 @staticmethod
 def minimal_native():
  return {'report_version':'2.0.0','git_revision':'7bc10711b5',
      'sim':{'players':[{'gear':{'head':{'encoded_item':v.HEAD.split('=',1)[1],'mastery_rating':201},
          'hands':{'encoded_item':'hands,id=268243'}},
          'buffs':[{'name':'cumulative_power'},{'name':'rune_of_critical_power'},
                   {'name':'venomcursed_mastery','spell':1307922,'start_count':7,'uptime':37.5}],
          'collected_data':{'dps':{'count':59}}}]}}
if __name__=='__main__':unittest.main()
