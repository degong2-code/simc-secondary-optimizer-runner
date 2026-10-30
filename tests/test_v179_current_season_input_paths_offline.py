"""v179: current-season v177 user input -> existing v098/v096 plan, NO SimC.

Only test actually supported user options; no inventing static-L or forcing
a proc mechanism. Changes to user T/oil/trinkets/combat must affect the
exact profile, durable session ID and budget, not existing old caches.
"""
from __future__ import annotations
import copy,json,pathlib,sys,tempfile,unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v098_target_user_scenario_bootstrap as bootstrap
import v106_user_session_controller as sessions
import v108_native_consumable_inputs as consumer

class CurrentSeasonInputPathsOffline(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root=pathlib.Path(temp.name)
        self.binary=self.root/"simc-fake"
        self.binary.write_bytes(b"NO_NATIVE")
        self.revision="7bc10711b5"

    def make(self,key,tag,mutate=None):
        controls=sessions.standard_controls(key)
        if mutate is not None:mutate(controls)
        user=sessions.user_scenario(controls)
        folder=self.root/tag
        with mock.patch.object(bootstrap.entry.durable,"run") as actual_simc:
            created=bootstrap.build(user,folder,self.binary,self.revision,
                                    current_season_product=True)
            actual_simc.assert_not_called()
        self.assertTrue((folder/"manifest.json").is_file())
        self.assertFalse((folder/"simc_results").exists())
        return controls,user,created,folder

    def test_manual_final_T_oil_0_and_oil_fixed_once_single_and_dual(self):
        for name,key in (("paladin",("paladin","retribution")),
                         ("fury",("warrior","fury"))):
            with self.subTest(name=name):
                def manual_only(c):
                    c["oil_hands"]=[]
                    c["final_T"]=3500
                _,_,zero,folder_zero=self.make(key,name+"_no_oil",manual_only)
                self.assertEqual(zero["plan"]["base_B"],3500)
                self.assertEqual(zero["plan"]["final_T"],3500)
                self.assertEqual(sum(zero["plan"]["fixed_O"].values()),0)
                def manual_oil(c):
                    c["final_T"]=3500
                _,_,oiled,folder_oil=self.make(key,name+"_oiled",manual_oil)
                expected=64 if name=="fury" else 32
                self.assertEqual(oiled["plan"]["final_T"],3500)
                self.assertEqual(oiled["plan"]["base_B"],3500-expected)
                self.assertEqual(sum(oiled["plan"]["fixed_O"].values()),expected)
                self.assertEqual(json.loads(
                    (folder_oil/"manifest.json").read_text())["manual_final_T"],3500)
                self.assertNotEqual((folder_zero/"manifest.json").read_bytes(),
                                    (folder_oil/"manifest.json").read_bytes())
                self.assertEqual(oiled["plan"]["budget_source"],
                                 "USER_MANUAL_FINAL_INCLUDING_OIL")

    def test_changed_trinkets_combat_and_consumables_in_profile_and_identity(self):
        key=("paladin","retribution")
        old,old_user,old_result,old_folder=self.make(key,"default")
        def change(c):
            c["trinket_ids"]=[250215,281215]
            c["targets"]=2
            c["duration_seconds"]=180
            c["raid_buffs"]=False
            c["consumable_choices"]={
               **c["consumable_choices"],
               "food":"harandar_celebration",
               "potion":"potion_of_recklessness_2",
               "augmentation":"disabled"}
        changed,user,result,folder=self.make(key,"altered",change)
        profile=(folder/"profile.simc").read_text()
        self.assertIn("trinket1=selected_250215,id=250215,ilevel=334",profile)
        self.assertIn("trinket2=selected_281215,id=281215,ilevel=334",profile)
        self.assertIn("desired_targets=2",profile)
        self.assertIn("max_time=180",profile)
        self.assertIn("optimal_raid=0",profile)
        for token in ("food=harandar_celebration",
                      "potion=potion_of_recklessness_2","augmentation=disabled"):
            self.assertIn(token,profile)
        self.assertNotEqual((old_folder/"profile.simc").read_bytes(),
                            (folder/"profile.simc").read_bytes())
        o1=sessions.session_key(old_user,self.binary,self.revision,
                               current_season_product=True)[0]
        o2=sessions.session_key(user,self.binary,self.revision,
                               current_season_product=True)[0]
        self.assertNotEqual(o1,o2)
        self.assertEqual(result["plan"]["native_limit"],6)
        self.assertEqual(result["plan"]["item_slots"],15)
        self.assertEqual(len(result["effective_four_tier_slots"]),4)

    def test_selected_season_special_without_exact_L_does_not_guess_zero(self):
        key=("paladin","retribution")
        controls=sessions.standard_controls(key)
        controls["special_items"]=[{"slot":"finger1","item_id":268249,
                                   "options":{}}]
        user=sessions.user_scenario(controls)
        # Existing exact-L safety checks require a Native static record.
        # No static cache is supplied, and no default zero substitute allowed.
        with mock.patch.object(bootstrap.entry.durable,"run") as native:
            with self.assertRaisesRegex(Exception,
                     "SPECIAL_L_REQUIRES_EXACT_NATIVE_STATIC_VARIANT"):
                bootstrap.build(user,self.root/"missing_L",self.binary,
                       self.revision,current_season_product=True)
            native.assert_not_called()
        self.assertFalse((self.root/"missing_L"/"manifest.json").exists())

if __name__=="__main__":unittest.main()
