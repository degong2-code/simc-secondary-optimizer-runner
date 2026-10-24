import importlib.util, pathlib, sys, unittest, json
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runner'))
import v039_venomkeeper_bare_probe as v039
import pilot
class V039Unit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.src,_=pilot.source()
    def test_id_and_ilevel(self): self.assertEqual((v039.ITEM_ID,v039.ITEM_ILVL),(271874,334))
    def test_isolated_head_swap(self):
        s=v039.make_bare(self.src,ROOT/'tmp.json')
        self.assertIn(v039.EXACT_NEW_HEAD,s)
        self.assertNotIn(v039.EXACT_OLD_HEAD,s)
        self.assertIn('shoulders=v020_shoulders_271562',s)
        self.assertIn('chest=v020_chest_271567',s)
        self.assertIn('legs=v020_legs_271563',s)
    def test_no_tier_four_claim(self):
        self.assertNotIn("'tier4_preserved':True",pathlib.Path(v039.__file__).read_text(encoding='utf8'))
    def test_no_bonus_in_bare_head(self):
        head=v039.make_bare(self.src,ROOT/'tmp.json').split('head=',1)[1].splitlines()[0]
        self.assertNotIn('bonus_id=',head)
        self.assertNotIn('gem_id=',head)
        self.assertNotIn('enchant=',head)
    def test_requires_exact_existing_head(self):
        with self.assertRaisesRegex(v039.ProbeBlocked,'REFERENCE_HEAD_CHANGED'):
            v039.make_bare(self.src.replace(v039.EXACT_OLD_HEAD,'head=other,id=0'),ROOT/'tmp.json')
    def test_iterations_are_bounded(self):
        with self.assertRaisesRegex(v039.ProbeBlocked,'ITERATIONS_OUT_OF_SCOPE'):
            v039.make_bare(self.src,ROOT/'tmp.json',100000)
    def test_bare_item_verification_native_only(self):
        fake={'report_version':'2.0.0','git_revision':'7bc10711b5','sim':{'players':[{'race':'dwarf','specialization':'Arcane Mage','gear':{
            'head':{'encoded_item':'venomkeepers_horrific_cowl,id=271874,ilevel=334,source=local','ilevel':334,'mastery_rating':201},
            'shoulders':{'encoded_item':'a,id=271562','ilevel':334},
            'chest':{'encoded_item':'a,id=271567','ilevel':334},
            'legs':{'encoded_item':'a,id=271563','ilevel':334}},
            'buffs':[],'collected_data':{'dps':{'count':59,'mean':200000}}}]}}
        obj=v039.read_bare_native(json.dumps(fake).encode());self.assertEqual(obj['bare_gear_chmv']['mastery_rating'],201)
        self.assertFalse(obj['cumulative_power_tier4_buff_present'])
    def test_reject_wrong_mastery_in_native(self):
        fake={'report_version':'2.0.0','git_revision':'7bc10711b5','sim':{'players':[{'race':'dwarf','specialization':'Arcane Mage','gear':{
            'head':{'encoded_item':'venomkeepers_horrific_cowl,id=271874,ilevel=334,source=local','ilevel':334,'mastery_rating':202},
            'shoulders':{'encoded_item':'a,id=271562','ilevel':334},
            'chest':{'encoded_item':'a,id=271567','ilevel':334},
            'legs':{'encoded_item':'a,id=271563','ilevel':334}},
            'buffs':[],'collected_data':{'dps':{'count':59,'mean':200000}}}]}}
        with self.assertRaisesRegex(v039.ProbeBlocked,'BARE_ITEM_STAT_NOT_EXPECTED'):
            v039.read_bare_native(json.dumps(fake).encode())
if __name__=='__main__':unittest.main()
