"""v049 target bounded class-compatible Native recovery, offline safety."""
import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runner'))
import v049_class_compatible_recovery as v
import v047_full_scope_collector as s
import v046_static_item_cache as c

class Recovery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=s.parse_manifest(ROOT/'integration_probes/requests/v047_full_scope_manifest.json')
        cls.cases=v.expected_cases(cls.manifest)
    def test_exact_recovery_scope(self):
        self.assertEqual(len(self.cases),448)
        self.assertEqual(len({x['item_id'] for x,l in self.cases}),32)
        self.assertEqual(len({l for x,l in self.cases}),14)
        self.assertTrue(all(it['item_id'] in v.BAD_IDS for it,l in self.cases))
        self.assertFalse(any(it['slot']=='TRINKET' for it,l in self.cases))
    def test_profiles_respect_armor(self):
        for armor,expected in [('Plate','warrior'),('Leather','druid'),('Mail','hunter')]:
            item=next(x for x,l in self.cases if x.get('armor_type')==armor)
            raw=v.profile(item,334,pathlib.Path('/tmp/a.json'))
            self.assertTrue(raw.startswith(expected+'="V049StaticProbe"'))
            self.assertIn('iterations=1',raw)
            self.assertIn('actions=wait,sec=1',raw)
            self.assertNotIn('gear_crit_rating=',raw)
            self.assertNotIn('spell_query',raw)
    def test_bow(self):
        bow=next(x for x,l in self.cases if x['item_id']==268207)
        self.assertEqual(v.classify(bow),('hunter','marksmanship','main_hand'))
    def test_no_trinket_unsupported_promoted(self):
        self.assertFalse(250224 in v.BAD_IDS)
        self.assertFalse(250244 in v.BAD_IDS)
    def test_profile_only_one_item(self):
        item=self.cases[0][0]
        raw=v.profile(item,334,pathlib.Path('/tmp/a.json'))
        self.assertEqual(sum(',id=' in s for s in raw.splitlines()),1)
        self.assertEqual(sum(s.startswith('json2=') for s in raw.splitlines()),1)

if __name__=='__main__':unittest.main()
