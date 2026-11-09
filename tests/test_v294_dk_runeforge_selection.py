"""DK explicit runeforge to SimC equipment option, offline and no Native."""
import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v294_dk_runeforge_selection as dk
import v055_simc_item_selection as items
import v106_user_session_controller as ux

class DKRuneforgeOffline(unittest.TestCase):
    def need(self,ok,reason):
        if not ok:raise ValueError(reason)
    def rows(self):
        return {"main_hand":{"slot":"main_hand","item_id":268209,
                             "ilevel":334,"options":{}},
                "off_hand":{"slot":"off_hand","item_id":268202,
                            "ilevel":334,"options":{}}}
    def test_frost_two_weapon_options_are_simc_enchant_ids(self):
        rows=self.rows()
        selected=dk.apply(rows=rows,selection={"main_hand":3368,
             "off_hand":3370},class_name="deathknight",
             weapon_form="dual_one_hand",need=self.need)
        self.assertEqual(selected,{"main_hand":3368,"off_hand":3370})
        self.assertIn("enchant_id=3368",items.equipment_line(**rows["main_hand"]))
        self.assertIn("enchant_id=3370",items.equipment_line(**rows["off_hand"]))
    def test_offhand_wrong_class_and_unknown_id_fail_closed(self):
        cases=[("deathknight","single_two_hand",{"off_hand":3370},
                "DK_RUNEFORGE_OFFHAND_REQUIRES_DUAL_WEAPON"),
               ("paladin","single_two_hand",{"main_hand":3368},
                "DK_RUNEFORGE_CLASS_ONLY"),
               ("deathknight","single_two_hand",{"main_hand":9999},
                "DK_RUNEFORGE_ID_UNSUPPORTED")]
        for cls,form,selected,code in cases:
            with self.subTest(code=code),self.assertRaisesRegex(ValueError,code):
                dk.apply(rows=self.rows(),selection=selected,class_name=cls,
                         weapon_form=form,need=self.need)
    def test_other_enchant_conflict_and_rune_replacement(self):
        rows=self.rows()
        rows["main_hand"]["options"]["enchant_id"]="9999"
        with self.assertRaisesRegex(ValueError,"DK_RUNEFORGE_OTHER_ENCHANT_CONFLICT"):
            dk.apply(rows=rows,selection={"main_hand":3368},
                     class_name="deathknight",weapon_form="dual_one_hand",
                     need=self.need)
        rows["main_hand"]["options"]["enchant_id"]="3847"
        dk.apply(rows=rows,selection={"main_hand":3368},
                 class_name="deathknight",weapon_form="dual_one_hand",
                 need=self.need)
        self.assertEqual(rows["main_hand"]["options"]["enchant_id"],"3368")
    def test_existing_session_user_bytes_and_choice_identity(self):
        c=ux.standard_controls(("deathknight","frost"));c["oil_hands"]=[]
        old=ux.user_scenario(c)
        self.assertNotIn("runeforge_by_hand",old)
        c["runeforge_by_hand"]={"main_hand":3368,"off_hand":3370}
        new=ux.user_scenario(c)
        self.assertEqual(new["runeforge_by_hand"],c["runeforge_by_hand"])
        self.assertNotEqual(ux.canonical(old),ux.canonical(new))
        c["class"]="paladin";c["spec"]="retribution"
        with self.assertRaisesRegex(ux.SessionBlocked,"DK_RUNEFORGE_CLASS_ONLY"):
            ux.user_scenario(c)
if __name__=="__main__":unittest.main()
