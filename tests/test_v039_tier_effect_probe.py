import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runner'))
import v039_tier_effect_probe as v
import pilot
class ItemAndTier(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.src,_=pilot.source()
 def test_item_id(self):self.assertEqual(v.CANTRIP_HEAD.split('id=')[1].split(',')[0],'271874')
 def test_bonus_list_bounded(self):self.assertEqual(len(v.BONUSES.split('/')),7)
 def test_tier_gloves_id(self):self.assertIn('id=271565',v.TIER_HAND_NEW)
 def test_two_changed_gear_slots(self):
  s=v.make_profile(self.src,ROOT/'test.json')
  self.assertIn(v.CANTRIP_HEAD,s)
  self.assertIn(v.TIER_HAND_NEW,s)
  self.assertNotIn(v.TIER_HAND_OLD,s)
  self.assertNotIn(v.EXACT_OLD_HEAD if hasattr(v,'EXACT_OLD_HEAD') else 'head=v020_head_271564',s)
  self.assertIn('shoulders=v020_shoulders_271562',s)
  self.assertIn('chest=v020_chest_271567',s)
  self.assertIn('legs=v020_legs_271563',s)
 def test_crit_rune(self):
  s=v.make_profile(self.src,ROOT/'test.json')
  self.assertIn(v.bare.CRIT_RUNE,s);self.assertNotIn(v.bare.HASTE_RUNE,s)
 def test_wrong_hand_blocks(self):
  with self.assertRaisesRegex(v.CheckFailed,'ORIGINAL_HAND_CHANGED'):
   v.make_profile(self.src.replace(v.TIER_HAND_OLD,'hands=bad,id=1'),ROOT/'test.json')
 def test_original_head_changed_blocks(self):
  with self.assertRaisesRegex(v.CheckFailed,'ORIGINAL_HEAD_CHANGED'):
   v.make_profile(self.src.replace(v.bare.EXACT_OLD_HEAD,'head=bad,id=1'),ROOT/'test.json')
if __name__=='__main__':unittest.main()
