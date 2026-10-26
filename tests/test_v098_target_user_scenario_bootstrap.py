"""v098 target-level USER controls -> full internal v096 plan, offline only."""
import json,pathlib,re,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v098_target_user_scenario_bootstrap as boot
import v096_unified_product_entry as old

def case(which,*,ilevel=334,final_T=None):
    options={"fury":("warrior","fury"),
             "frost":("mage","frost"),
             "retribution":("paladin","retribution"),
             "beast_mastery":("hunter","beast_mastery")}
    key=options[which]
    filename=boot.ARCHETYPES[key][0]
    src=(boot.FIXTURES/filename).read_text(encoding="utf8")
    talents=[r.partition("=")[2] for r in src.splitlines()
             if r.startswith("talents=")][0]
    trinkets=[]
    for slot in ("trinket1","trinket2"):
        raw=[r for r in src.splitlines() if r.startswith(slot+"=")][0]
        match=re.search(r"(?:^|,)id=(\d+)(?:,|$)",raw)
        assert match is not None
        trinkets.append({"slot":slot,"item_id":int(match.group(1)),
                         "options":{}})
    return {"schema":boot.SCHEMA,
        "character":{"class":key[0],"spec":key[1],
                     "race":{"fury":"dwarf","frost":"human",
                             "retribution":"blood_elf",
                             "beast_mastery":"troll"}[which],
                     "talents":talents},
        "target":{"ilevel":ilevel,"final_T":final_T},
        "trinkets":trinkets,"special_items":[],"embellishments":[],
        "oil_hands":["main_hand","off_hand"] if which=="fury"
                    else ["main_hand"],
        "combat":{"targets":1,"duration_seconds":300,"raid_buffs":True}}

class UserTargetBootstrap(unittest.TestCase):
    def prepare(self,user):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root=pathlib.Path(self.tmp.name)
        binary=root/"dummy"
        binary.write_bytes(b"NOT_SIMC_EXECUTED")
        return boot.build(user,root/"generated",binary,"7bc10711b5"),root

    def test_fury_target_334_user_without_full_equipment_or_simc_profile(self):
        result,root=self.prepare(case("fury"))
        plan=result["plan"]
        self.assertEqual((plan["base_B"],plan["final_T"]),(3350,3414))
        self.assertEqual((plan["class"],plan["spec"]),("warrior","fury"))
        self.assertEqual(plan["item_slots"],16)
        self.assertEqual(plan["native_min_calls"],6)
        self.assertEqual(result["status"],"READY_INTERNAL_MANIFEST_ZERO_NATIVE")
        self.assertFalse((root/"generated"/"simc_results").exists())
        m=json.loads((root/"generated"/"manifest.json").read_text())
        self.assertEqual(m["scouts"],1)
        self.assertEqual(m["material_scouts"],1)
        self.assertNotIn("manual_final_T",m)
        self.assertEqual(m["seed_targets_B"][0].keys(),m["seed_targets_B"][1].keys())
        a,b=m["seed_targets_B"]
        moved=sum(abs(a[k]-b[k]) for k in a)//2
        self.assertGreaterEqual(moved,335)  # 10% of B, when unconstrained
        self.assertEqual(sum(a.values()),3350)
        self.assertEqual(sum(b.values()),3350)

    def test_retribution_source_backed_fifteen_slots_no_offhand(self):
        result,root=self.prepare(case("retribution"))
        self.assertEqual((result["plan"]["class"],result["plan"]["spec"]),
                         ("paladin","retribution"))
        self.assertEqual(result["plan"]["item_slots"],15)
        self.assertEqual(result["plan"]["base_B"],3150)
        self.assertEqual(result["plan"]["final_T"],3182)
        profile=(root/"generated"/"profile.simc").read_text()
        self.assertNotIn("\noff_hand=",profile)
        self.assertIn("\nrace=blood_elf\n",profile)
        self.assertEqual(len([x for x in profile.splitlines()
                              if re.match(r"^(?:head|shoulders|chest|hands)=",x)]),4)

    def test_beast_mastery_corrected_head_feet_and_pet_apl_retained(self):
        result,root=self.prepare(case("beast_mastery"))
        self.assertEqual((result["plan"]["class"],result["plan"]["spec"]),
                         ("hunter","beast_mastery"))
        self.assertEqual(result["plan"]["item_slots"],15)
        self.assertEqual((result["plan"]["base_B"],result["plan"]["final_T"]),
                         (3150,3182))
        profile=(root/"generated"/"profile.simc").read_text()
        self.assertIn("head=selected_249317,id=249317,ilevel=334",profile)
        self.assertIn("feet=selected_249320,id=249320,ilevel=334",profile)
        self.assertNotIn("head=selected_271441",profile)
        self.assertNotIn("feet=selected_271440",profile)
        self.assertNotIn("\noff_hand=",profile)
        self.assertGreater(sum(x.startswith("actions.") for x in
                               profile.splitlines()),1)

    def test_cross_archetype_level_321_manual_and_oil_no_native(self):
        for kind in ("fury","frost","retribution","beast_mastery"):
            with self.subTest(kind=kind):
                user=case(kind,ilevel=321)
                result,root=self.prepare(user)
                expected=3170 if kind=="fury" else 2980
                self.assertEqual(result["plan"]["base_B"],expected)
                self.assertEqual(result["plan"]["final_T"],
                                 expected+64 if kind=="fury" else expected+32)
                self.assertEqual(result["plan"]["item_slots"],
                                 16 if kind in ("fury","frost") else 15)
                profile=(root/"generated"/"profile.simc").read_text()
                self.assertEqual(len([x for x in profile.splitlines()
                                      if ",ilevel=321" in x]),
                                 result["plan"]["item_slots"])
                self.assertFalse((root/"generated"/"simc_results").exists())

    def test_frost_target_user_manual_final_T(self):
        user=case("frost",final_T=3182)
        result,root=self.prepare(user)
        plan=result["plan"]
        self.assertEqual((plan["base_B"],plan["final_T"]),(3150,3182))
        self.assertEqual(plan["user_manual_final_T"],3182)
        self.assertEqual(plan["budget_source"],"USER_MANUAL_FINAL_INCLUDING_OIL")
        text=(root/"generated"/"profile.simc").read_text()
        self.assertIn("race=human\n",text)
        self.assertEqual(sum(x.startswith("actions") for x in text.splitlines()),
                         sum(x.startswith("actions") for x in
                             (boot.FIXTURES/boot.ARCHETYPES[("mage","frost")][0])
                             .read_text().splitlines()))

    def test_changed_race_and_target_level_are_generated_not_profile_current_gear(self):
        user=case("fury",ilevel=321)
        user["character"]["race"]="orc"
        result,root=self.prepare(user)
        self.assertEqual(result["target_ilevel"],321)
        self.assertEqual(result["plan"]["base_B"],3170)
        text=(root/"generated"/"profile.simc").read_text()
        self.assertIn("\nrace=orc\n",text)
        self.assertEqual(len([x for x in text.splitlines() if ",ilevel=321" in x]),16)
        self.assertNotIn(",ilevel=334",text)

    def test_user_trinket_replacement_allowed_without_static_trinket_record(self):
        user=case("fury")
        user["trinkets"][0]["item_id"]=250224
        result,root=self.prepare(user)
        self.assertEqual(result["plan"]["base_B"],3350)
        self.assertIn("trinket1=selected_250224,id=250224,ilevel=334",
                      (root/"generated"/"profile.simc").read_text())

    def test_special_requires_exact_L_not_invented_zero(self):
        user=case("fury")
        user["special_items"]=[{"slot":"feet","item_id":271093,"options":{}}]
        with tempfile.TemporaryDirectory() as td:
            fake=pathlib.Path(td)/"binary";fake.write_bytes(b"NO_NATIVE")
            with self.assertRaisesRegex(Exception,
                      "SPECIAL_L_REQUIRES_EXACT_NATIVE_STATIC_VARIANT"):
                boot.build(user,pathlib.Path(td)/"build",fake,"7bc10711b5")
            self.assertFalse((pathlib.Path(td)/"build"/"manifest.json").exists())

    def test_reject_tier_overwrite_or_unsupported_archetype(self):
        user=case("fury")
        user["special_items"]=[{"slot":"head","item_id":123456,"options":{}}]
        with tempfile.TemporaryDirectory() as td:
            fake=pathlib.Path(td)/"binary";fake.write_bytes(b"NO_NATIVE")
            with self.assertRaisesRegex(boot.UserScenarioBlocked,
                                        "SPECIAL_OVERWRITES_TIER_OR_TRINKET"):
                boot.build(user,pathlib.Path(td)/"build",fake,"7bc10711b5")
        user=case("fury")
        user["character"]["class"]="shaman"
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(boot.UserScenarioBlocked,
                                        "REPRESENTATIVE_ARCHETYPE_NOT_READY"):
                boot.build(user,pathlib.Path(td)/"build",pathlib.Path(td)/"none",
                           "7bc10711b5")

    def test_offhand_oil_not_accepted_for_frost_frill(self):
        user=case("frost")
        user["oil_hands"]=["off_hand"]
        with tempfile.TemporaryDirectory() as td:
            fake=pathlib.Path(td)/"binary";fake.write_bytes(b"NO_NATIVE")
            with self.assertRaisesRegex(Exception,"NONWEAPON_OFFHAND_CANNOT_RECEIVE_OIL"):
                boot.build(user,pathlib.Path(td)/"build",fake,"7bc10711b5")

    def test_generated_plan_replay_without_new_native_or_replacement(self):
        result,root=self.prepare(case("fury"))
        ready=old.run_manifest(result["generated_manifest"],plan_only=True)
        self.assertEqual(ready["source_profile_sha256"],
                         result["plan"]["source_profile_sha256"])
        fake=root/"dummy"
        again=boot.build(case("fury"),root/"generated",fake,"7bc10711b5")
        self.assertEqual(again["plan"]["scenario_digest"],
                         result["plan"]["scenario_digest"])
        self.assertFalse((root/"generated"/"simc_results").exists())

if __name__=="__main__":unittest.main()
