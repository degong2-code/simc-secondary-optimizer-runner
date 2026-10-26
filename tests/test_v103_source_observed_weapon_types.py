"""v103 source-backed weapon type identity / permitted source shape only."""
import pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v101_common_representative_equipment as core
import v103_source_observed_weapon_types as weapons

class WeaponTypeSources(unittest.TestCase):
    @staticmethod
    def need(ok,reason):
        if not ok:raise ValueError(reason)

    def test_six_pinned_weapon_shapes_and_six_source_enabled(self):
        doc=weapons.verify_observed()
        self.assertEqual(doc["source_profile_shapes"],6)
        self.assertEqual(doc["executable_source_shapes"],6)
        self.assertEqual(doc["unique_item_ids"],8)
        self.assertTrue(doc["not_full_spec_weapon_legality"])
        self.assertEqual(doc["native_calls"],0)

    def test_all_six_item_hands_subtypes_are_type_differentiated(self):
        for key,items in weapons.OBSERVED.items():
            with self.subTest(key=key):
                desc=weapons.source_shape(key)
                self.assertEqual(set(desc["weapons"]),set(items))
                self.assertTrue(desc["all_other_weapon_forms_unassessed"])
                for hand,(id_,kind,primary) in items.items():
                    self.assertEqual(desc["weapons"][hand]["item_id"],id_)
                    self.assertEqual(desc["weapons"][hand]["subtype"],kind)
                    self.assertIn("item_reference",desc["weapons"][hand])

    def test_six_common_source_factories_keep_actual_exact_weapons(self):
        for key in core.ARCHETYPES:
            with self.subTest(key=key),tempfile.TemporaryDirectory() as td:
                _,_,rows,_,form,_=core.source_backed_gear(
                    key,pathlib.Path(td),334,self.need)
                self.assertTrue(weapons.validate_existing(key,rows,form))
                self.assertTrue(weapons.source_shape(key)["is_currently_executable"])

    def test_rogue_shaman_are_now_source_enabled_but_no_other_weapons_inferred(self):
        for key in (("rogue","subtlety"),("shaman","elemental")):
            with self.subTest(key=key):
                desc=weapons.source_shape(key)
                self.assertTrue(desc["is_currently_executable"])
                self.assertTrue(desc["all_other_weapon_forms_unassessed"])
                with self.assertRaisesRegex(weapons.WeaponSourceBlocked,
                                           "EXECUTABLE_SOURCE_WEAPON_ITEM_CHANGED"):
                    weapons.validate_existing(key,{},desc["form"])

    def test_wrong_source_weapon_item_and_form_are_refused(self):
        key=("warrior","fury")
        with tempfile.TemporaryDirectory() as td:
            _,_,rows,_,form,_=core.source_backed_gear(
                key,pathlib.Path(td),334,self.need)
            rows["off_hand"]["item_id"]=268213
            with self.assertRaisesRegex(weapons.WeaponSourceBlocked,
                                        "EXECUTABLE_SOURCE_WEAPON_ITEM_CHANGED"):
                weapons.validate_existing(key,rows,form)
            with self.assertRaisesRegex(weapons.WeaponSourceBlocked,
                                        "EXECUTABLE_WEAPON_FORM_NOT_SOURCE_BACKED"):
                weapons.validate_existing(key,rows,"single_two_hand")

    def test_spec_unsupported_fails_closed_not_as_all_weapon_form_permission(self):
        with self.assertRaisesRegex(weapons.WeaponSourceBlocked,
                                    "WEAPON_SPEC_SOURCE_NOT_AVAILABLE"):
            weapons.source_shape(("mage","arcane"))
        self.assertNotIn(("mage","arcane"),weapons.OBSERVED)
        self.assertIn(("shaman","elemental"),core.ARCHETYPES)
        self.assertNotIn(("priest","shadow"),core.ARCHETYPES)

if __name__=="__main__":unittest.main()
