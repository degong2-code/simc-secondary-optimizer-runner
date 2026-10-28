"""P1 source-free staged profile generator: offline, SimC 0."""
from __future__ import annotations
import copy,hashlib,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v139_pure_target_profile_composer as pure

TRINKETS=[
 {"slot":"trinket1","item_id":270175,"options":{}},
 {"slot":"trinket2","item_id":270173,"options":{}}]

class PureProfileComposer(unittest.TestCase):
    def build(self,key,race):
        cl,spec=key.split("/")
        return pure.compose({"class":cl,"spec":spec,"race":race,
                             "talents":"CAAAABBB11122"},
                            copy.deepcopy(TRINKETS))

    def test_two_missing_specs_stage_full_physical_profiles_without_upstream_sources(self):
        for key,race in (("druid/balance","night_elf"),
                         ("evoker/devastation","dracthyr")):
            with self.subTest(key=key):
                profile,meta,rows,group=self.build(key,race)
                self.assertEqual(meta["status"],"STAGED_NOT_USER_READY")
                self.assertEqual(meta["spec"],key)
                self.assertEqual((meta["physical_slots"],len(rows)),(16,16))
                self.assertEqual(len(group),4)
                self.assertEqual(meta["ordinary_gems"],6)
                self.assertEqual(set(meta["four_tier_slots"]),group)
                self.assertEqual(meta["weapon_form"],"one_hand_frill")
                self.assertEqual(meta["primary"],"intellect")
                self.assertIn("default_actions=1\n",profile)
                self.assertNotIn("load_default_gear=1",profile)
                self.assertNotIn("actions.",profile)
                self.assertEqual(sum(x.startswith("gear_") for x in
                                     profile.splitlines()),4)
                for s in pure.SLOT_ORDER:
                    self.assertEqual(sum(x.startswith(s+"=")
                                         for x in profile.splitlines()),1)
                self.assertTrue(all(rows[s]["ilevel"]==334 for s in rows))
                self.assertEqual(rows["trinket1"]["item_id"],270175)
                self.assertEqual(rows["trinket2"]["item_id"],270173)
                self.assertFalse(meta["source_profile_read"])
                self.assertEqual(meta["native_calls"],0)
                self.assertFalse(meta["exact_static_rating_verified"])
                self.assertFalse(meta["chmv_budget_ready"])
                self.assertFalse(meta["user_optimizer_ready"])

    def test_actual_class_tier_ids_come_from_data_not_other_spec_profile(self):
        _,_,d,g=self.build("druid/balance","night_elf")
        self.assertEqual({s:d[s]["item_id"] for s in g},
             {"head":271528,"shoulders":271526,
              "hands":271529,"legs":271527})
        self.assertEqual(d["chest"]["item_id"],251159)
        _,_,e,g=self.build("evoker/devastation","dracthyr")
        self.assertEqual({s:e[s]["item_id"] for s in g},
             {"shoulders":271499,"chest":271504,
              "hands":271502,"legs":271500})
        self.assertEqual(e["head"]["item_id"],271441)
        self.assertEqual(e["main_hand"]["item_id"],271092)
        self.assertEqual(e["off_hand"]["item_id"],268197)
        self.assertEqual(pure.catalog()["specializations"].keys(),
              {"druid/balance","evoker/devastation","mage/frost",
               "paladin/retribution"})

    def test_frost_mage_third_pure_catalog_staging_is_not_native_promotion(self):
        profile,meta,rows,tier=self.build("mage/frost","human")
        self.assertEqual(meta["status"],"STAGED_NOT_USER_READY")
        self.assertEqual(meta["family"],"cloth")
        self.assertEqual(meta["primary"],"intellect")
        self.assertEqual(meta["weapon_form"],"one_hand_frill")
        self.assertEqual(tier,{"shoulders","chest","hands","legs"})
        self.assertEqual({slot:rows[slot]["item_id"] for slot in tier},
                         {"shoulders":271562,"chest":271567,
                          "hands":271565,"legs":271563})
        self.assertEqual(rows["head"]["item_id"],271874)
        self.assertEqual((rows["wrists"]["item_id"],
                          rows["waist"]["item_id"],
                          rows["feet"]["item_id"]),(251154,268257,268255))
        self.assertEqual((rows["main_hand"]["item_id"],
                          rows["off_hand"]["item_id"]),(271092,245769))
        self.assertEqual(len(rows),16)
        self.assertIn("default_actions=1\n",profile)
        self.assertNotIn("actions.",profile)
        self.assertFalse(meta["source_profile_read"])
        self.assertFalse(meta["user_optimizer_ready"])
        self.assertEqual(meta["native_calls"],0)

    def test_retribution_single_twohand_shared_compiler_fifteen_slots(self):
        profile,meta,rows,tier=self.build("paladin/retribution","blood_elf")
        self.assertEqual(meta["status"],"STAGED_NOT_USER_READY")
        self.assertEqual((meta["family"],meta["primary"],meta["weapon_form"]),
                         ("plate","strength","single_two_hand"))
        self.assertEqual(tier,{"head","shoulders","chest","hands"})
        self.assertEqual({s:rows[s]["item_id"] for s in tier},
             {"head":271465,"shoulders":271463,"chest":271468,"hands":271466})
        self.assertEqual((rows["legs"]["item_id"],rows["wrists"]["item_id"],
                         rows["waist"]["item_id"],rows["feet"]["item_id"]),
                         (271878,268239,268259,268260))
        self.assertEqual(rows["main_hand"]["item_id"],268213)
        self.assertNotIn("off_hand",rows)
        self.assertNotIn("off_hand=",profile)
        self.assertIn("role=attack\n",profile)
        self.assertIn("default_actions=1\n",profile)
        self.assertNotIn("actions.",profile)
        self.assertEqual(len(rows),15)
        self.assertFalse(meta["source_profile_read"])
        self.assertFalse(meta["user_optimizer_ready"])
        self.assertEqual(meta["native_calls"],0)

    def test_user_race_talents_trinkets_and_combat_affect_output(self):
        a,_,_,_=self.build("druid/balance","night_elf")
        changed={"class":"druid","spec":"balance",
                 "race":"tauren","talents":"CAAAABBB11123"}
        t=copy.deepcopy(TRINKETS);t[0]["item_id"]=250224
        b,_,rows,_=pure.compose(changed,t,combat={
            "targets":3,"duration_seconds":240,"raid_buffs":False})
        self.assertNotEqual(hashlib.sha256(a.encode()).digest(),
                            hashlib.sha256(b.encode()).digest())
        self.assertIn("race=tauren\n",b)
        self.assertIn("talents=CAAAABBB11123\n",b)
        self.assertIn("desired_targets=3\n",b)
        self.assertIn("max_time=240\n",b)
        self.assertIn("optimal_raid=0\n",b)
        self.assertEqual(rows["trinket1"]["item_id"],250224)

    def test_season_switch_changes_data_not_profile_compiler(self):
        data=copy.deepcopy(pure.catalog())
        data["season"]="future_test_only"
        data["target_ilevel"]=321
        data["character_level"]=91
        data["default_consumables"]["food"]="disabled"
        data["specializations"]["druid/balance"]["ordinary"]["feet"]=268240
        actor={"class":"druid","spec":"balance","race":"night_elf",
               "talents":"CAAAABBB11122"}
        profile,meta,rows,_=pure.compose(
            actor,copy.deepcopy(TRINKETS),target_ilevel=321,season=data)
        self.assertEqual(meta["season"],"future_test_only")
        self.assertEqual(rows["feet"]["ilevel"],321)
        self.assertEqual(rows["feet"]["item_id"],268240)
        self.assertIn("ilevel=321",profile)
        self.assertIn("level=91\n",profile)
        self.assertIn("food=disabled\n",profile)
        # This is a serialization test, not evidence that a future item
        # exists or that two slots accept the same model in real SimC.
        self.assertFalse(meta["user_optimizer_ready"])

    def test_aug_not_exposed_and_invalid_input_cannot_inject_simc_lines(self):
        actor={"class":"evoker","spec":"augmentation","race":"dracthyr",
               "talents":"CAAAABBB11122"}
        with self.assertRaisesRegex(pure.ProfileStageBlocked,
                                    "SOURCE_INDEPENDENT_SPEC_NOT_STAGED"):
            pure.compose(actor,copy.deepcopy(TRINKETS))
        actor["spec"]="devastation"
        actor["talents"]="ABC\ngear_crit_rating=999999"
        with self.assertRaisesRegex(Exception,"TOKEN"):
            pure.compose(actor,copy.deepcopy(TRINKETS))
        actor["talents"]="CAAAABBB11122"
        with self.assertRaisesRegex(pure.ProfileStageBlocked,
                                    "SEASON_TARGET_LEVEL_NOT_GROUNDED"):
            pure.compose(actor,copy.deepcopy(TRINKETS),target_ilevel=321)
        with self.assertRaisesRegex(pure.ProfileStageBlocked,
                                    "EXACT_TWO_USER_TRINKETS"):
            pure.compose(actor,[])
        actor["race"]="night_elf"
        with self.assertRaisesRegex(pure.ProfileStageBlocked,
                                    "EVOKER_RACE_NOT_VERIFIED"):
            pure.compose(actor,copy.deepcopy(TRINKETS))

if __name__=="__main__":
    unittest.main()
