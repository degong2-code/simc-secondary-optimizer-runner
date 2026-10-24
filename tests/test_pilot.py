import importlib.util
import json
import pathlib
import tempfile
import unittest
from copy import deepcopy

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pilot', ROOT/'runner'/'pilot.py')
pilot=importlib.util.module_from_spec(spec);spec.loader.exec_module(pilot)

class V033Contract(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.src,cls.ref=pilot.source()
 def test_reference_pinned_and_nonnative_paths_omitted(self):
  self.assertNotIn('json2=',self.src)
  self.assertIn('race=dwarf\n',self.src)
  self.assertEqual(self.ref['reference_total'],3184)
 def test_source_does_not_contain_personal_filesystem_path(self):
  self.assertNotIn('C:\\',self.src)
 def test_haste_rune_exact(self):
  with tempfile.TemporaryDirectory() as d:
   s=pilot.generate(self.src,pathlib.Path(d)/'a.json','haste',60)
   self.assertIn('omnium_talents=136822:1/136817:1/136821:1/136814:1',s)
 def test_critical_rune_exact_and_other_omnium_unchanged(self):
  with tempfile.TemporaryDirectory() as d:
   s=pilot.generate(self.src,pathlib.Path(d)/'a.json','crit',60)
   self.assertIn('omnium_talents=136822:1/136817:1/136815:1/136814:1',s)
   self.assertNotIn('136821:1',s)
 def test_rune_switch_has_only_one_line_difference(self):
  with tempfile.TemporaryDirectory() as d:
   u=pilot.generate(self.src,pathlib.Path(d)/'x.json','crit',60).splitlines()
   v=pilot.generate(self.src,pathlib.Path(d)/'x.json','haste',60).splitlines()
   self.assertEqual([i for i,(a,b) in enumerate(zip(u,v)) if a!=b],[7])
 def test_keeps_two_linings_and_all_four_gear_overrides(self):
  with tempfile.TemporaryDirectory() as d:
   s=pilot.generate(self.src,pathlib.Path(d)/'a.json','crit',320)
   self.assertEqual(s.count('embellishment=arcanoweave_lining'),2)
   for k in pilot.STAT_KEYS:self.assertEqual(s.count('gear_'+k+'='),1)
   self.assertIn('food=royal_roast',s)
   self.assertIn('iterations=320',s)
 def test_reject_unexpected_rune(self):
  with self.assertRaises(pilot.PilotError):pilot.generate(self.src,pathlib.Path('out.json'),'mastery',60)
 def test_reject_large_iterations(self):
  with self.assertRaises(pilot.PilotError):pilot.generate(self.src,pathlib.Path('out.json'),'crit',10000)
 def test_reject_modified_reference(self):
  with self.assertRaises(pilot.PilotError):pilot.generate(self.src.replace('136821','0000'),pathlib.Path('out.json'),'crit',60)
 def native_fixture(self):
  gear={}
  ids={'head':271564,'shoulders':271562,'chest':271567,'legs':271563,'back':239656,'wrists':239648,'trinket1':270164,'trinket2':281215}
  for slot,id in ids.items():gear[slot]={'encoded_item':'abc,id='+str(id)+',ilevel=334'+(',embellishment=arcanoweave_lining' if slot in ('back','wrists') else ''),'ilevel':334}
  return {'report_version':'2.0.0','git_revision':'7bc1071','version':'1210-01','sim':{
   'options':{'fight_style':'Patchwerk','desired_targets':1,'max_time':300.0},
   'players':[{'race':'dwarf','specialization':'Arcane Mage','food':'royal_roast','gear':gear,
               'buffs':[{'name':x} for x in ('cumulative_power','arcanoweave_insight','rune_of_burning_haste')],
               'collected_data':{'dps':{'mean':194000,'mean_std_dev':1200,'count':60},
                                 'buffed_stats':{'stats':dict(pilot.EXPECTED_VECTOR)}}}]}}
 def test_native_json2_haste(self):
  obj=self.native_fixture()
  self.assertEqual(pilot.report_native(obj,'haste',60)['chmv_total'],3184)
 def test_native_json2_critical_must_show_critical_rune(self):
  obj=self.native_fixture()
  with self.assertRaisesRegex(pilot.PilotError,'RUNE_BUFF_ABSENT'):pilot.report_native(obj,'crit',60)
  obj['sim']['players'][0]['buffs'][-1]={'name':'rune_of_critical_power'}
  self.assertEqual(pilot.report_native(obj,'crit',60)['rune_buff'],'rune_of_critical_power')
 def test_reject_chmv_mismatch(self):
  obj=self.native_fixture();obj['sim']['players'][0]['collected_data']['buffed_stats']['stats']['crit_rating']+=1
  with self.assertRaisesRegex(pilot.PilotError,'FINAL_CHMV_MISMATCH'):pilot.report_native(obj,'haste',60)
 def test_reject_missing_tier(self):
  obj=self.native_fixture();obj['sim']['players'][0]['buffs']=obj['sim']['players'][0]['buffs'][1:]
  with self.assertRaisesRegex(pilot.PilotError,'TIER4_BUFF_ABSENT'):pilot.report_native(obj,'haste',60)
 def test_reject_extra_rune(self):
  obj=self.native_fixture();obj['sim']['players'][0]['buffs'].append({'name':'rune_of_critical_power'})
  with self.assertRaisesRegex(pilot.PilotError,'OPPOSITE_RUNE_BUFF_PRESENT'):pilot.report_native(obj,'haste',60)
 def test_mock_linux_process_two_runes_receipts(self):
  # This tests orchestration only; not a claim of native SimC execution.
  import os
  if os.name=='nt':self.skipTest('mock executable uses POSIX shebang')
  with tempfile.TemporaryDirectory() as folder:
   root=pathlib.Path(folder);fake=root/'mock_simc'
   fixture=self.native_fixture()
   mock_code="""#!/usr/bin/env python3
import json,sys,pathlib
fixture=__FIXTURE__
src=pathlib.Path(sys.argv[1]).read_text()
json2=next(x.split('=',1)[1] for x in src.splitlines() if x.startswith('json2='))
iterations=int(next(x.split('=',1)[1] for x in src.splitlines() if x.startswith('iterations=')))
if '136815:1' in src:
 fixture['sim']['players'][0]['buffs'][-1]['name']='rune_of_critical_power'
fixture['sim']['players'][0]['collected_data']['dps']['count']=iterations
pathlib.Path(json2).write_text(json.dumps(fixture))
print('SYNTHETIC_MOCK_ONLY')
"""
   fake.write_text(mock_code.replace('__FIXTURE__',repr(fixture)),encoding='utf8');fake.chmod(0o755)
   rc=pilot.launch(fake,['haste','crit'],60,root/'out')
   receipt=json.loads((root/'out'/'RUN_RECEIPT_v033.json').read_text())
   self.assertEqual(rc,0)
   self.assertEqual(receipt['status'],'PASS_ALL_NATIVE')
   self.assertEqual(set(receipt['runs']),{'haste','crit'})
   self.assertTrue((root/'out'/'haste'/'result.json').exists())
   self.assertTrue((root/'out'/'crit'/'CASE_RECEIPT_v033.json').exists())
 def test_unverified_dps_not_global_optimum(self):
  self.assertEqual(self.ref['guarantee'],'Previous Windows reference only; Linux result unverified')

if __name__=='__main__':unittest.main()
