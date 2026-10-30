"""v202: proof-conditioned E floor passes into existing original v065 scheduler."""
import copy,pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"runner"))
import v065_v015_scheduler_adapter as scheduler
import v061_scenario_contract as contract
STATS=contract.STATS
def v(c=0,h=0,m=0,ver=0): return dict(zip(STATS,(c,h,m,ver)))
class EnchantInsideLegacyBudget(unittest.TestCase):
    def context(self):
        normalized={"schema":contract.SCHEMA,"scenario_digest":"test-isolated",
            "scenario":{"constraints":{"max_fraction":v(.8,.8,.8,.8)}},
            "budget":{"F":165,"J":138,"external_temporary_rating":v(h=16)}}
        budget={"schema":"v062_representative_static_budget_v1",
                "scenario_digest":"test-isolated",
                "budget":{"T_official":3000},
                "effective_floor_if_possible":v(),
                "locked_L_when_all_specials_observed":v(h=40)}
        return normalized,budget
    def test_legacy_unchanged_and_verified_e_locked_once(self):
        n,b=self.context()
        old=scheduler.budget_with_fixed_components(n,b,v(h=165),v(h=16))
        self.assertEqual(old["effective_floor_if_possible"]["haste_rating"],149)
        new=scheduler.budget_with_fixed_components(
            n,b,v(h=165),v(h=16),fixed_enchant_E=v(h=30))
        self.assertEqual(new["budget"]["T_official"],3000)
        self.assertEqual(new["effective_floor_if_possible"]["haste_rating"],219)
        self.assertEqual(new["fixed_enchant_E_in_G_only"],v(h=30))
        self.assertTrue(new["enchant_E_not_added_to_B_or_T"])
        self.assertEqual(b["effective_floor_if_possible"],v())
        self.assertEqual(old["effective_floor_if_possible"]["haste_rating"],149)
    def test_enchant_only_higher_floor_and_feasibility(self):
        n,b=self.context()
        good=scheduler.budget_with_fixed_components(
            n,b,v(h=165),v(h=16),fixed_enchant_E=v(h=30))
        B,lo,hi=scheduler.bounds(n,good)
        self.assertEqual(B,3000)
        self.assertFalse(scheduler.eligible((200,218,500,2082),B,lo,hi))
        self.assertTrue(scheduler.eligible((200,219,700,1881),B,lo,hi))
        with self.assertRaisesRegex(Exception,"ENCHANT_E_EXCEEDS_AVAILABLE_G"):
            scheduler.budget_with_fixed_components(
                n,b,v(h=165),v(h=16),fixed_enchant_E=v(h=3000))
        with self.assertRaisesRegex(Exception,"INVALID_NONNEGATIVE_VECTOR"):
            scheduler.budget_with_fixed_components(
                n,b,v(h=165),v(h=16),fixed_enchant_E=v(h=-1))
if __name__=="__main__":unittest.main()
