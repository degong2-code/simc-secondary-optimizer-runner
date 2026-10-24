import json
import pathlib
import sys
import unittest
from copy import deepcopy
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runner'))
import pilot
import v040_catalyst_redirect_probe as v

class CatalystRedirectContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.source,_=pilot.source()
    def test_two_bounded_variants(self): self.assertEqual(set(v.VARIANTS), {'minimal_334','bonus_13846_334'})
    def test_base_tier_and_source_ids(self):
        self.assertEqual((v.TIER_HEAD,v.ORIGINAL_SPECIAL_HEAD),(271564,271874))
    def test_334_not_copied_official_344(self):
        for name,head in v.VARIANTS.items():
            self.assertIn('ilevel=334',head)
            self.assertNotIn('ilevel=344',head)
            self.assertNotIn('13335/13668/13846/13848',head)
    def test_344_is_reference_not_executed(self): self.assertIn('ilevel=344',v.UPSTREAM_344_HEAD)
    def test_exact_334_head(self):
        for name,head in v.VARIANTS.items():
            text=v.make_profile(self.source,name,ROOT/'fake.json')
            self.assertEqual([x for x in text.splitlines() if x.startswith('head=')],[head])
    def test_old_gloves_kept(self):
        for name in v.VARIANTS:
            text=v.make_profile(self.source,name,ROOT/'fake.json')
            self.assertIn(v.MAGE_GLOVES,text)
            self.assertNotIn('id=271565',text)
    def test_three_other_tier_slots(self):
        for name in v.VARIANTS:
            x=v.make_profile(self.source,name,ROOT/'x.json')
            for s in ('shoulders=v020_shoulders_271562','chest=v020_chest_271567','legs=v020_legs_271563'):
                self.assertIn(s,x)
    def test_correct_crit_rune(self):
        s=v.make_profile(self.source,'minimal_334',ROOT/'x.json')
        self.assertIn(v.prior.CRIT_RUNE,s)
        self.assertNotIn(v.prior.HASTE_RUNE,s)
    def test_output_and_iterations(self):
        s=v.make_profile(self.source,'minimal_334',ROOT/'x.json')
        self.assertEqual(s.count('json2='),1)
        self.assertEqual(s.count('iterations=60'),1)
    def test_reject_changed_reference(self):
        with self.assertRaisesRegex(v.Refused,'BASELINE_HEAD_CHANGED'):
            v.make_profile(self.source.replace(v.prior.EXACT_OLD_HEAD,'head=else,id=1'),'minimal_334',ROOT/'x.json')
    def test_reject_bad_variant(self):
        with self.assertRaisesRegex(v.Refused,'UNAUTHORIZED_VARIANT'):
            v.make_profile(self.source,'unknown',ROOT/'x.json')
    def test_reject_wrong_gloves(self):
        with self.assertRaisesRegex(v.Refused,'BASELINE_GLOVES_CHANGED'):
            v.make_profile(self.source.replace(v.MAGE_GLOVES,'hands=bad,id=1'),'minimal_334',ROOT/'x.json')
    def test_reject_changed_rune(self):
        with self.assertRaisesRegex(v.Refused,'BASELINE_RUNE_CHANGED'):
            v.make_profile(self.source.replace(v.prior.HASTE_RUNE,v.prior.CRIT_RUNE),'minimal_334',ROOT/'x.json')
    def test_reject_334_bonus_in_minimal(self):
        self.assertNotIn('bonus_id=',v.VARIANTS['minimal_334'])
    def test_bonus_variant_only_13846(self):
        self.assertIn('bonus_id=13846,',v.VARIANTS['bonus_13846_334'])
    def test_binary_sha_is_prior_pin(self):self.assertEqual(v.BIN_SHA,v.prior.PINNED_BIN_SHA256)
    def test_id_parse(self):
        self.assertEqual(v._single_id('head,id=271564,ilevel=334,redirected_base_stats=271874','redirected_base_stats'),271874)
    def test_ambiguous_id_rejected(self):
        with self.assertRaisesRegex(v.Refused,'ENCODED_ID_NOT_UNIQUE'):
            v._single_id('head,id=271564,id=271874','id')
    def fake_json(self, *, proc=True, mastery=201, tier=True, redirected=271874):
        head='crown_of_the_primal_leywarden,id=271564,ilevel=334,source=local,redirected_base_stats='+str(redirected)
        buff=[{'name':'rune_of_critical_power'}]
        if tier:buff.append({'name':'cumulative_power'})
        if proc:buff.append({'name':'venomcursed_mastery','spell':1307922,'start_count':6,'uptime':25.0})
        return json.dumps({'report_version':'2.0.0','git_revision':'7bc10711b5',
            'sim':{'players':[{'specialization':'Arcane Mage','race':'dwarf',
            'gear':{'head':{'ilevel':334,'encoded_item':head,'mastery_rating':mastery},
            'hands':{'encoded_item':'hands,id=268243'},
            'shoulders':{'encoded_item':'shoulders,id=271562'},
            'chest':{'encoded_item':'chest,id=271567'},
            'legs':{'encoded_item':'legs,id=271563'}},'buffs':buff}]}}).encode()
    def test_synthetic_complete_accepts_only_observed_semantics(self):
        x=v.inspect_json2(self.fake_json(),'minimal_334')
        self.assertTrue(x['proc_buff_observed_and_triggered'])
        self.assertFalse(x['effect_dynamic_rating_magnitudes_validated'])
    def test_synthetic_missing_proc_not_promoted(self):
        x=v.inspect_json2(self.fake_json(proc=False),'minimal_334')
        self.assertFalse(x['proc_buff_observed_and_triggered'])
    def test_synthetic_missing_tier_blocked(self):
        with self.assertRaisesRegex(v.Refused,'NO_TIER_4PC_NATIVE_BUFF'):
            v.inspect_json2(self.fake_json(tier=False),'minimal_334')
    def test_synthetic_wrong_stats_or_redirect_blocked(self):
        with self.assertRaisesRegex(v.Refused,'REDIRECT_MASTERY_NOT_EQUAL_BARE_201'):
            v.inspect_json2(self.fake_json(mastery=200),'minimal_334')
        with self.assertRaisesRegex(v.Refused,'REDIRECT_ID_MISSING'):
            v.inspect_json2(self.fake_json(redirected=271565),'minimal_334')
    def test_json_not_trusted_from_labels(self):
        with self.assertRaises((json.JSONDecodeError,TypeError)):
            v.inspect_json2(b'not-json','minimal_334')

if __name__=='__main__':unittest.main()
