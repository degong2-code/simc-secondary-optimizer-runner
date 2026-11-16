"""v531: exact 70783 per-user E+ source checks and v222 arithmetic isolation.

Synthetic budget fixtures below are purely deterministic unit tests; they
are NOT sealed original v212 evidence or a product Native acceptance.
"""
from __future__ import annotations
import copy,json,pathlib,sys,tempfile,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner")]
import v531_current_season_positive_E_bridge as e
import v529_current_season_eagle_E0_bridge as prior
import v106_user_session_controller as sessions

def fake_install():
    return {
      "game_build":prior.BUILD,"simc_revision":prior.REVISION,
      "target_ilevel":334,"official_G":2850,"official_J":92,
      "official_F":165,"official_B":3107,"official_T":3107,
      "official_O":dict(prior.ZERO),"manifest_sha256":"a"*64}
def fake_retarget(manual):
    return {"base_B":3107 if manual is None else manual,
            "final_T":3107 if manual is None else manual,
            "fixed_E":dict(prior.ZERO),"fixed_L":dict(prior.ZERO),
            "effective_G":2850,"reference_B":3107}

class PositiveSeasonEnchants(unittest.TestCase):
    def test_v528_exact_physical_native_e_and_sha(self):
        self.assertEqual(e.check_choice({"finger1":8025})[1]["haste_rating"],30)
        self.assertEqual(e.check_choice({"finger1":7965})[1]["mastery_rating"],26)
        for key in (8025,7965):
            row=e.ENCHANTS[key]
            self.assertEqual(len(row["before"]),64)
            self.assertEqual(len(row["after"]),64)
            self.assertNotEqual(row["before"],row["after"])
        self.assertEqual(e.original.evidence()["simc_binary_sha256"],e.original.BIN_SHA)

    def test_unverified_enchant_ids_or_options_fail_closed(self):
        for row in ({"finger1":7967},{"finger1":9999},
                    {"finger2":8025},{"finger1":"8025"},
                    {"finger1":8025,"finger2":7965},{}):
            with self.subTest(row=row),self.assertRaisesRegex(
                  e.PositiveEnchantBlocked,"UNVERIFIED_POSITIVE_ENCHANT_ID"):
                e.check_choice(row)
        with self.assertRaisesRegex(
             e.PositiveEnchantBlocked,"CURRENT_V213_SOURCE_REQUIRED"):
             e.source({"finger1":8025},None)

    def test_original_native_E_sha_tamper_is_not_admitted(self):
        with tempfile.TemporaryDirectory() as t:
            p=pathlib.Path(t)/"fake.json"
            original=prior.evidence()
            source=next(r for r in original["enchant_scope"]["scoped_results"]
                        if r["id"]==8025)
            source["per_profile_E"]["haste_rating"]=31
            p.write_text(json.dumps(original),encoding="utf8")
            with patch.object(prior,"PROOF",p):
                with self.assertRaisesRegex(
                     e.PositiveEnchantBlocked,"EXACT_V528_NATIVE_POSITIVE_E_SHA_OR_AMOUNT_DRIFT"):
                    e.check_choice({"finger1":8025})

    def test_existing_v222_user_budget_reference_plus_E_once(self):
        for item,delta in ((8025,30),(7965,26)):
            with self.subTest(item=item), patch.object(
                    e.budget,"retarget_verified_install",
                    side_effect=lambda **kw:fake_retarget(kw["manual_final_T"])):
                calculated=e.project(fake_install(),{"finger1":item})
                self.assertEqual(calculated["reference_B"],3107+delta)
                self.assertEqual(calculated["base_B"],3107+delta)
                self.assertEqual(calculated["final_T"],3107+delta)
                self.assertEqual(calculated["effective_G"],2850+delta)
                self.assertEqual(calculated["user_E_added_to_auto_B_once"],delta)
                self.assertFalse(calculated["user_T_manual_unchanged"])
                # Manual T is authoritative in the v534 user path: E stays
                # a fixed floor, NEVER a second addition to explicit T.
                fixed=e.project(fake_install(),{"finger1":item},
                                manual_final_T=3200)
                self.assertEqual(fixed["final_T"],3200)
                self.assertEqual(fixed["user_E_added_to_auto_B_once"],0)
                self.assertTrue(fixed["user_T_manual_unchanged"])

    def test_current_user_scope_is_one_v528_native_witness(self):
        controls=sessions.standard_controls(("hunter","survival"))
        controls.update(race="human",oil_hands=[],trinket_ids=[270175,270173])
        user=sessions.user_scenario(controls)
        e.user_scope(user)
        manual=copy.deepcopy(user)
        manual["target"]["final_T"]=3200
        e.user_scope(manual)
        self.assertEqual(manual["target"]["final_T"],3200)
        for bad in (True,1.5,0,-1,"3200"):
            changed=copy.deepcopy(manual)
            changed["target"]["final_T"]=bad
            with self.subTest(invalid_manual=bad),self.assertRaisesRegex(
                    e.PositiveEnchantBlocked,
                    "MANUAL_FINAL_T_POSITIVE_INTEGER_REQUIRED"):
                e.user_scope(changed)
        for field,value in (("target",{"ilevel":335,"final_T":None}),
                            ("oil_hands",["main_hand"]),
                            ("trinkets",[{"slot":"trinket1","item_id":270169,"options":{}},
                                         {"slot":"trinket2","item_id":270174,"options":{}}])):
            other=copy.deepcopy(user);other[field]=value
            with self.subTest(field=field),self.assertRaises(
                 prior.SourceBlocked):
                e.user_scope(other)

    def test_manual_T_keeps_E_floor_and_rejects_fixed_budget_underflow(self):
        for item,extra in ((8025,30),(7965,26)):
            with self.subTest(item=item),patch.object(
                  e.budget,"retarget_verified_install",
                  side_effect=lambda **kw:fake_retarget(kw["manual_final_T"])):
                amount=e.project(fake_install(),{"finger1":item},
                                 manual_final_T=3200)
                self.assertEqual(amount["base_B"],3200)
                self.assertEqual(amount["final_T"],3200)
                self.assertEqual(amount["reference_B"],3107+extra)
                self.assertEqual(amount["fixed_E"],e.ENCHANTS[item]["E"])
                self.assertEqual(amount["user_E_added_to_auto_B_once"],0)
                with self.assertRaisesRegex(
                    e.PositiveEnchantBlocked,
                    "FIXED_E_OR_MANUAL_T_FEASIBILITY_INVALID"):
                    e.project(fake_install(),{"finger1":item},
                              manual_final_T=200)

    def test_source_pair_cannot_be_wrong_profile_or_binary(self):
        normalized={"scenario":{"character":{"class":"hunter","spec":"survival"},
                     "equipment":{"special":[],"crafted":[]}}}
        profile="finger1=ring,id=268266,ilevel=334,source=local,enchant_id=8025\n"
        with self.assertRaisesRegex(
             e.PositiveEnchantBlocked,"EXACT_V528_WINDOWS_SIMC_BINARY_REVISION_REQUIRED"):
            e.admit({"finger1":8025},profile,normalized,"wrong",prior.REVISION)
        with self.assertRaisesRegex(
             e.PositiveEnchantBlocked,"UNENCHANTED_NATIVE_PROFILE_SHA_DRIFT"):
            e.admit({"finger1":8025},profile,normalized,prior.BIN_SHA,prior.REVISION)

if __name__=="__main__":
    unittest.main()
