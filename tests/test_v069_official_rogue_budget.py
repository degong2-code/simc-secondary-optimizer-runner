"""v069 official user Rogue static budget / label-preserving safeguards."""
import copy,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v068_rogue_user_profile as u
import v069_rogue_official_budget_native as p
import v064_adaptive_evaluator_port as port
SOURCE=u.REFERENCE.read_text(encoding="utf8")

class ReconcilerOffline(unittest.TestCase):
    def test_new_back_crafted_stat_identity_and_not_embellished(self):
        with tempfile.TemporaryDirectory() as folder:
            x,_=u.assemble(SOURCE,pathlib.Path(folder)/"json2.json",35)
        gear=p.parse_exact_input(x)
        self.assertEqual(gear["back"]["item_id"],239656)
        self.assertEqual(gear["back"]["options"]["crafted_stats"],"36/49")
        self.assertNotIn("embellishment",gear["back"]["options"])
        self.assertEqual(sum("embellishment" in r["options"] for r in gear.values()),2)
    def test_user_equipment_slot_categories_match_contract(self):
        with tempfile.TemporaryDirectory() as folder:
            x,_=u.assemble(SOURCE,pathlib.Path(folder)/"out.json",35)
        g=p.parse_exact_input(x)
        self.assertEqual(set(p.TIER),{"shoulders","chest","hands","legs"})
        self.assertEqual(set(p.SPECIAL),{"head","main_hand"})
        self.assertEqual(set(p.CRAFTED),{"wrists","off_hand"})
        self.assertEqual(set(p.TRINKETS),{"trinket1","trinket2"})
        self.assertEqual(set(g),u.ALL_SLOTS)
        self.assertTrue(all(g[k]["ilevel"]==334 for k in g))
    def test_parse_does_not_treat_trinket_missing_as_zero(self):
        with tempfile.TemporaryDirectory() as folder:
            x,_=u.assemble(SOURCE,pathlib.Path(folder)/"out.json",35)
        g=p.parse_exact_input(x)
        self.assertEqual(g["trinket2"]["item_id"],281215)
        self.assertNotIn("static_rating_assumed_zero",g["trinket2"])
    def test_duplicate_gear_slot_blocked(self):
        with tempfile.TemporaryDirectory() as folder:
            x,_=u.assemble(SOURCE,pathlib.Path(folder)/"out.json",35)
        with self.assertRaisesRegex(p.ReconcileBlocked,"DUPLICATE_SIMC_SLOT"):
            p.parse_exact_input(x+"\nhead=another,id=271875,ilevel=334\n")
    def test_no_fabricated_G_and_L_in_offline_builder(self):
        with tempfile.TemporaryDirectory() as folder:
            x,receipt=u.assemble(SOURCE,pathlib.Path(folder)/"out.json",35)
        self.assertIsNone(receipt["item_static_G"])
        self.assertIsNone(receipt["locked_special_L"])
        self.assertIsNone(receipt["official_T"])
    def test_wrong_binary_identity_not_permitted(self):
        with self.assertRaisesRegex(p.ReconcileBlocked,"PINNED_NATIVE_BINARY_CHANGED"):
            p.prepare("/nonexistent/path","0"*64)
    def test_v064_dual_weapon_temp_binding_source_changed(self):
        source=pathlib.Path(ROOT/"runner/v064_adaptive_evaluator_port.py").read_text()
        self.assertIn('dual=single+"/off_hand:"+temp',source)
        self.assertIn("PROFILE_TEMPORARY_DRIFT",source)
    def test_apl_remains_wholly_simc_owned(self):
        with tempfile.TemporaryDirectory() as folder:
            source,_=u.assemble(SOURCE,pathlib.Path(folder)/"out.json",35)
        self.assertEqual([x for x in source.splitlines() if x.startswith("actions")],
                         [x for x in SOURCE.splitlines() if x.startswith("actions")])

if __name__=="__main__":unittest.main()
