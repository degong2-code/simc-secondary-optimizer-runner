"""v204 offline: only selected, source-pinned enchant changes derived ilvl B/T.

No Native calls; reuses exact v084 unenchanted reference fixture and v202 proof.
The older v203 B=3150/T=3182 Native is historical, not re-labeled v204.
"""
import copy, pathlib, sys, tempfile, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v046_static_item_cache as static_cache
import v089_ilvl_chmv_budget_selector as reference
import v090_reference_total_native_candidate as native_plan
import v091_weapon_oil_external_adapter as oil
import v092_approved_inclusive_CHMV_policy as inclusive
import v204_selected_enchant_reference_budget as selected
import v065_v015_scheduler_adapter as scheduler
from test_v091_weapon_oil_external_adapter import frost

E={"crit_rating":0,"haste_rating":30,"mastery_rating":0,"versatility_rating":0}
O={"crit_rating":16,"haste_rating":16,"mastery_rating":0,"versatility_rating":0}

class SelectedEnchantReferenceBudget(unittest.TestCase):
    def fixture(self,td):
        profile,cfg,fillers=frost(td)
        base=reference.resolve(cfg,mode=reference.REFERENCE_MODE,
                               weapon_layout="one_hand_frill")
        return profile,cfg,fillers,base

    def test_unchosen_reference_and_hash_identity_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            profile,cfg,fillers,base=self.fixture(td)
            self.assertIs(selected.selected_reference(base),base)
            self.assertEqual(base["resolved_T"],3150)
            self.assertNotIn(selected.KEY,base)
            ready=native_plan.prepare(base,fillers,static_cache.empty_cache(),profile)
            self.assertEqual(ready["T"],3150)
            self.assertNotIn(selected.KEY,
                ready["static_budget"]["reference_budget_provenance"])

    def test_selected_reference_adds_exact_E_once_but_not_to_source_table(self):
        with tempfile.TemporaryDirectory() as td:
            profile,cfg,fillers,base=self.fixture(td)
            changed=selected.selected_reference(base,E)
            self.assertEqual((base["resolved_T"],changed["resolved_T"]),(3150,3180))
            self.assertEqual(changed["scenario_plan"]["budget"]["T"],3180)
            self.assertEqual(changed["reference_row"]["general"],3150)
            self.assertNotIn(selected.KEY,base)
            self.assertEqual(selected.expected_reference_B(changed,3150),3180)
            ready=native_plan.prepare(changed,fillers,static_cache.empty_cache(),profile)
            self.assertEqual(ready["T"],3180)
            self.assertEqual(ready["static_budget"]["reference_budget_provenance"]
                             [selected.KEY]["additional_B"],30)
            self.assertEqual(inclusive.calculate(ready["T"],O)["final_T"],3212)
            # L=0 fixture; E is a floor, not 30 additional rating beyond B.
            n=ready["scenario"]
            f={"crit_rating":165,"haste_rating":0,"mastery_rating":0,"versatility_rating":0}
            floored=scheduler.budget_with_fixed_components(
                n,ready["static_budget"],f,dict.fromkeys(O,0),fixed_enchant_E=E)
            self.assertGreaterEqual(floored["effective_floor_if_possible"]["haste_rating"],30)
            self.assertEqual(floored["budget"]["T_official"],3180)

    def test_manual_final_T_is_authoritative_with_same_fixed_E(self):
        with tempfile.TemporaryDirectory() as td:
            profile,cfg,fillers,_=self.fixture(td)
            configured=oil.configure(profile,cfg,"one_hand_frill",["main_hand"])
            converted=inclusive.approved_manual_total_to_legacy_B(
                configured["scenario"],3182,configured["declared_O"])
            manual=reference.resolve(converted["scenario"],
                        mode=reference.REFERENCE_MODE,weapon_layout="one_hand_frill")
            same=selected.selected_reference(manual,E,manual_final_T=3182)
            self.assertIs(same,manual)
            self.assertEqual(same["resolved_T"],3150)
            self.assertNotIn(selected.KEY,same)
            self.assertEqual(inclusive.calculate(3150,O)["final_T"],3182)

    def test_wrong_E_and_tampered_reference_proof_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            _,_,_,base=self.fixture(td)
            wrong=dict(E);wrong["haste_rating"]=31
            with self.assertRaisesRegex(Exception,"SELECTED_ENCHANT_E_NOT_EXACT"):
                selected.selected_reference(base,wrong)
            changed=selected.selected_reference(base,E)
            changed[selected.KEY]["additional_B"]=31
            with self.assertRaisesRegex(Exception,"ENCHANT_REFERENCE_PROVENANCE_DRIFT"):
                selected.expected_reference_B(changed,3150)

    def test_evidence_not_allowed_for_other_profile_or_unselected_user(self):
        with tempfile.TemporaryDirectory() as td:
            profile,cfg,fillers,_=self.fixture(td)
            with self.assertRaisesRegex(Exception,"SELECTED_ENCHANT_FULL_PROFILE_SHA"):
                oil.prepare(profile,cfg,fillers,static_cache.empty_cache(),
                            "one_hand_frill",["main_hand"],verified_enchant_E=E)
            baseline=oil.prepare(profile,cfg,fillers,static_cache.empty_cache(),
                                 "one_hand_frill",["main_hand"])
            self.assertEqual(baseline["approved_total"]["final_T"],3182)
            self.assertEqual(baseline["prepared"]["T"],3150)

if __name__=="__main__":unittest.main()
