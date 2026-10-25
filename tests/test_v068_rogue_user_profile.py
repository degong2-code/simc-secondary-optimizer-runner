"""v068 real USER selection input-contract regressions, no old PASS relabel."""
import pathlib,re,sys,tempfile,unittest,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v068_rogue_user_profile as u
import v068_rogue_two_native_probe as n
SOURCE=u.REFERENCE.read_text(encoding="utf8")

class RogueInputFixture(unittest.TestCase):
    def assembled(self,p="A"):
        with tempfile.TemporaryDirectory() as folder:
            return u.assemble(SOURCE,pathlib.Path(folder)/"result.json",35,p)
    def test_pinned_reference_and_entire_apl_unchanged(self):
        self.assertTrue(len(SOURCE)>8000)
        a,b=self.assembled()
        origin=[x for x in SOURCE.splitlines() if x.startswith("actions")]
        result=[x for x in a.splitlines() if x.startswith("actions")]
        self.assertEqual(origin,result)
        self.assertIn("action",SOURCE)
        self.assertEqual(b["native_calls"],0)
        self.assertFalse(b["native_json2_dps_verified"])
    def test_user_rogue_race_custom_talent_exact(self):
        x,r=self.assembled()
        self.assertIn("race=void_elf",x)
        self.assertIn("talents="+u.USER_TALENTS,x)
        self.assertIn("rogue=",x)
        self.assertIn("spec=subtlety",x)
    def test_omnium_mastery_explicit_fixed_not_fourth_rating(self):
        a,r=self.assembled()
        om=[x for x in a.splitlines() if x.startswith("omnium_talents=")]
        self.assertEqual(len(om),1)
        self.assertIn("rune_of_masterful_cunning",om[0])
        self.assertEqual(r["user"]["omnium_column_4"],"mastery")
        self.assertIsNone(r["official_T"])
    def test_equipment_exact_16_slots_and_specific_ids(self):
        a,r=self.assembled()
        slots={}
        for ln in a.splitlines():
            k,_,rest=ln.partition("=")
            if k in u.ALL_SLOTS:
                self.assertNotIn(k,slots)
                slots[k]=rest
        self.assertEqual(len(slots),16)
        for slot,id in (u.SPECIAL|u.TIER|u.TRINKETS).items():
            self.assertIn(f"id={id}",slots[slot])
            self.assertIn("ilevel=334",slots[slot])
        self.assertIn("id=237837",slots["off_hand"])
        self.assertIn("id=244576",slots["wrists"])
    def test_four_tier_remains_outside_selected_head(self):
        a,r=self.assembled()
        self.assertEqual(set(r["user"]["tier_four"]),{"shoulders","chest","hands","legs"})
        self.assertEqual(r["user"]["special"]["head"],271875)
        self.assertNotIn("head",r["user"]["tier_four"])
    def test_two_independent_crafted_effects_and_no_locked_stats(self):
        a,r=self.assembled()
        self.assertIn("embellishment=arcanoweave_lining",a)
        self.assertIn("embellishment=hunters_ritual_stone",a)
        self.assertEqual(a.count("embellishment="),2)
        self.assertEqual(r["user"]["embellishment_1"]["slot"],"off_hand")
        self.assertEqual(r["user"]["embellishment_2"]["slot"],"wrists")
        self.assertIsNone(r["special_static_L"])
        self.assertIsNone(r["item_static_G"])
    def test_special_b_one_six_normal_gems(self):
        a,_=self.assembled()
        gears=[x for x in a.splitlines() if x.split("=",1)[0] in u.ALL_SLOTS]
        whole="\n".join(gears)
        self.assertEqual(whole.count("240967"),1)
        self.assertEqual(whole.count("240900"),6)
    def test_official_combat_duration_and_no_item_proc_parser(self):
        a,_=self.assembled()
        for term in ("fight_style=Patchwerk","desired_targets=1","max_time=300",
                     "optimal_raid=1","fixed_time=1","iterations=35"):
            self.assertIn("\n"+term+"\n",a)
        self.assertFalse(hasattr(u,"proc_supported"))
    def test_two_numeric_witnesses_vary_only_four_raw_gear_stats(self):
        a,r=self.assembled("A")
        b,s=self.assembled("B")
        def stable(x):
            return "\n".join(line for line in x.splitlines() if
                not line.startswith("gear_") and
                not line.startswith("json2="))
        self.assertEqual(stable(a),stable(b))
        self.assertNotEqual(r["probe_raw_gear_override"],s["probe_raw_gear_override"])
        self.assertEqual(sum(r["probe_raw_gear_override"].values()),
                         sum(s["probe_raw_gear_override"].values()))
    def test_probe_rejects_bad_iterations(self):
        with self.assertRaisesRegex(u.ProfileBlocked,"NATIVE_PROBE_ITERATIONS_CAP"):
            u.assemble(SOURCE,"/tmp/probe.json",5)
    def test_bad_upstream_profile_refused(self):
        with self.assertRaisesRegex(u.ProfileBlocked,"NOT_ROGUE_SUBTLETY_REFERENCE"):
            u.assemble("mage=old\nspec=arcane\n","/tmp/probe.json")
    def test_protect_pin_from_wrong_binary_no_native(self):
        with tempfile.TemporaryDirectory() as d:
            missing=pathlib.Path(d)/"simc"
            missing.write_bytes(b"not-the-pinned-simc")
            self.assertEqual(n.execute(missing,pathlib.Path(d)/"results"),3)
            self.assertFalse((pathlib.Path(d)/"results"/"case_00").exists())
    def test_provenance_reference_blob_is_expected(self):
        self.assertEqual(u.UPSTREAM_GIT_BLOB_SHA,
          "b704e6326959432a82d14a6b774c79183d5b2af4")
        self.assertEqual(u.SPECIAL["main_hand"],271093)
        self.assertEqual(u.TRINKETS["trinket1"],270175)
        self.assertEqual(u.TRINKETS["trinket2"],281215)

if __name__=="__main__":
    unittest.main()
