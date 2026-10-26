"""v098 target-level USER controls -> full internal v096 plan, offline only."""
import json,pathlib,re,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
sys.path.insert(0,str(ROOT/"tests"))
import v098_target_user_scenario_bootstrap as boot
import v096_unified_product_entry as old
import v062_static_budget_bridge as native_budget
import v061_scenario_contract as scenario
from test_v062_static_budget_bridge import record as offline_record

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

    def test_four_tier_recovers_fifth_with_one_crafted_tier_replacement(self):
        examples={"fury":(237835,"legs",271455,16),
                  "retribution":(237835,"legs",271464,15),
                  "frost":(239650,"head",271564,16),
                  "beast_mastery":(244580,"head",271492,15)}
        for kind,(crafted_id,fifth,tier_id,slots) in examples.items():
            with self.subTest(archetype=kind):
                user=case(kind)
                user["embellishments"]=[
                    {"slot":"shoulders","item_id":crafted_id,
                     "options":{"crafted_stats":"49/36",
                                "embellishment":"arcanoweave_lining"}}]
                result,root=self.prepare(user)
                self.assertEqual(result["restored_tier_slots"],[fifth])
                self.assertEqual(result["plan"]["item_slots"],slots)
                self.assertEqual(len(result["effective_four_tier_slots"]),4)
                self.assertNotIn("shoulders",result["effective_four_tier_slots"])
                self.assertIn(fifth,result["effective_four_tier_slots"])
                cfg=json.loads((root/"generated"/"scenario.json").read_text())
                self.assertEqual(len(cfg["equipment"]["tier"]),4)
                self.assertEqual(len(cfg["equipment"]["crafted"]),
                                 3 if kind in ("fury","frost","beast_mastery") else 2)
                fifth_row=next(x for x in cfg["equipment"]["tier"]
                               if x["slot"]==fifth)
                self.assertEqual(fifth_row["item_id"],tier_id)
                profile=(root/"generated"/"profile.simc").read_text()
                self.assertEqual(sum(x.startswith(fifth+"=")
                                     for x in profile.splitlines()),1)
                self.assertIn("id="+str(tier_id),next(x for x
                                  in profile.splitlines() if x.startswith(fifth+"=")))
                self.assertFalse((root/"generated"/"simc_results").exists())

    def test_two_crafted_tier_positions_cannot_preserve_four_set(self):
        user=case("frost")
        user["embellishments"]=[
           {"slot":"shoulders","item_id":239650,
            "options":{"crafted_stats":"49/36",
                       "embellishment":"arcanoweave_lining"}},
           {"slot":"head","item_id":239652,
            "options":{"crafted_stats":"32/49",
                       "embellishment":"arcanoweave_lining"}}]
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td);binary=root/"dummy";binary.write_bytes(b"NO_NATIVE")
            with self.assertRaisesRegex(boot.UserScenarioBlocked,
                  "FOUR_TIER_UNAVAILABLE_SELECTED_FIFTH_OR_UNKNOWN_SOURCE"):
                boot.build(user,root/"output",binary,"7bc10711b5")
            self.assertFalse((root/"output"/"manifest.json").exists())

    def test_catalyzed_fifth_tier_and_crafted_existing_tier_are_counted_once(self):
        user=case("fury")
        user["special_items"]=[
          {"slot":"legs","item_id":271455,
           "options":{"redirected_base_stats":"271878"}}]
        user["embellishments"]=[
          {"slot":"shoulders","item_id":237835,
           "options":{"crafted_stats":"49/36",
                      "embellishment":"arcanoweave_lining"}}]
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td);binary=root/"dummy";binary.write_bytes(b"NO_NATIVE")
            cache=boot.cache_mod.empty_cache()
            row={"slot":"legs","item_id":271455,"ilevel":334,
                 "options":{"redirected_base_stats":"271878"}}
            offline_record(cache,row,
                {"crit_rating":0,"haste_rating":140,
                 "mastery_rating":0,"versatility_rating":0})
            path=root/"cache.json";boot.cache_mod.write_atomic(path,cache)
            result=boot.build(user,root/"out",binary,"7bc10711b5",
                              static_cache_path=path)
            self.assertEqual(result["restored_tier_slots"],[])
            self.assertEqual(result["effective_four_tier_slots"],
                             ["chest","hands","head","legs"])
            self.assertEqual(result["catalyst_origin_items"],
                [{"slot":"legs","tier_item_id":271455,"source_item_id":271878}])
            cfg=json.loads((root/"out"/"scenario.json").read_text())
            self.assertEqual(cfg["equipment"]["catalyst_special_tier_slots"],["legs"])
            self.assertEqual(len(cfg["equipment"]["tier"]),4)
            self.assertNotIn("shoulders",result["effective_four_tier_slots"])
            self.assertFalse((root/"out"/"simc_results").exists())

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
                                        "CATALYST_CLASS_TIER_ID_AND_ORIGIN_REQUIRED"):
                boot.build(user,pathlib.Path(td)/"build",fake,"7bc10711b5")
        user=case("fury")
        user["character"]["class"]="shaman"
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(boot.UserScenarioBlocked,
                                        "REPRESENTATIVE_ARCHETYPE_NOT_READY"):
                boot.build(user,pathlib.Path(td)/"build",pathlib.Path(td)/"none",
                           "7bc10711b5")

    def test_catalyst_special_tier_preserves_origin_and_one_physical_slot(self):
        # Synthetic cache variant tests code accounting, not actual Native item
        # effects or a new same-season canonical static measurement.
        user=case("fury")
        user["special_items"]=[{"slot":"chest","item_id":271459,
            "options":{"redirected_base_stats":"268222","bonus_id":"13848"}}]
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            fake=root/"dummy";fake.write_bytes(b"NO_NATIVE_CALLED")
            c=boot.cache_mod.empty_cache()
            converted={"slot":"chest","item_id":271459,"ilevel":334,
               "options":{"redirected_base_stats":"268222","bonus_id":"13848"}}
            fixed={"crit_rating":0,"haste_rating":0,
                   "mastery_rating":170,"versatility_rating":0}
            offline_record(c,converted,fixed)
            cachefile=root/"synth_static.json"
            boot.cache_mod.write_atomic(cachefile,c)
            result=boot.build(user,root/"generated",fake,"7bc10711b5",
                              static_cache_path=cachefile)
            self.assertEqual(result["plan"]["item_slots"],16)
            self.assertEqual((result["plan"]["base_B"],result["plan"]["final_T"]),
                             (3350,3414))
            self.assertEqual(result["catalyst_origin_items"],
                [{"slot":"chest","tier_item_id":271459,"source_item_id":268222}])
            profile=(root/"generated"/"profile.simc").read_text()
            chest=[l for l in profile.splitlines() if l.startswith("chest=")]
            self.assertEqual(len(chest),1)
            self.assertIn("id=271459",chest[0])
            self.assertIn("redirected_base_stats=268222",chest[0])
            self.assertIn("bonus_id=13848",chest[0])
            cfg=json.loads((root/"generated"/"scenario.json").read_text())
            self.assertEqual(len(cfg["equipment"]["tier"]),4)
            self.assertEqual(cfg["equipment"]["catalyst_special_tier_slots"],["chest"])
            self.assertEqual(cfg["equipment"]["special"],[])
            self.assertIn(271459,[r["item_id"] for r in cfg["equipment"]["tier"]])
            fillers=json.loads((root/"generated"/"fillers.json").read_text())
            budget=native_budget.compile_static_budget(scenario.normalize(cfg),
                                                        fillers,c)
            self.assertEqual(budget["locked_L_when_all_specials_observed"],fixed)
            self.assertEqual(len(budget["missing_special_fixed_static"]),0)
            self.assertFalse((root/"generated"/"simc_results").exists())

    def test_catalyst_tier_fails_closed_without_exact_native_static(self):
        user=case("fury")
        user["special_items"]=[{"slot":"chest","item_id":271459,
           "options":{"redirected_base_stats":"268222"}}]
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td);fake=root/"dummy";fake.write_bytes(b"NO_NATIVE")
            with self.assertRaisesRegex(Exception,
                       "SPECIAL_L_REQUIRES_EXACT_NATIVE_STATIC_VARIANT"):
                boot.build(user,root/"generated",fake,"7bc10711b5")
            self.assertFalse((root/"generated"/"manifest.json").exists())

    def test_catalyst_wrong_tier_id_or_non_tier_slot_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td);fake=root/"dummy";fake.write_bytes(b"NO_NATIVE")
            cases=[
              {"slot":"chest","item_id":271465,
               "options":{"redirected_base_stats":"268222"}},
              {"slot":"chest","item_id":271459,
               "options":{"redirected_base_stats":"271459"}},
              {"slot":"feet","item_id":271459,
               "options":{"redirected_base_stats":"268222"}}]
            for selected in cases:
                user=case("fury");user["special_items"]=[selected]
                with self.subTest(case=selected):
                    with self.assertRaisesRegex(boot.UserScenarioBlocked,
                            "CATALYST_CLASS_TIER_ID_AND_ORIGIN_REQUIRED|" +
                            "CATALYST_REQUIRES_EXISTING_CLASS_TIER_SLOT"):
                        boot.build(user,root/"generated",fake,"7bc10711b5")
            self.assertFalse((root/"generated"/"manifest.json").exists())

    def test_offhand_oil_not_accepted_for_frost_frill(self):
        user=case("frost")
        user["oil_hands"]=["off_hand"]
        with tempfile.TemporaryDirectory() as td:
            fake=pathlib.Path(td)/"binary";fake.write_bytes(b"NO_NATIVE")
            with self.assertRaisesRegex(Exception,"NONWEAPON_OFFHAND_CANNOT_RECEIVE_OIL"):
                boot.build(user,pathlib.Path(td)/"build",fake,"7bc10711b5")

    def test_optional_simc_import_reads_character_only_ignores_current_gear(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            fake=root/"dummy";fake.write_bytes(b"NOT_NATIVE")
            raw=case("fury")
            original=(boot.FIXTURES/boot.ARCHETYPES[("warrior","fury")][0]
                      ).read_text("utf8")
            # Imported currently worn head is an arbitrary non-target item.
            changed=re.sub(r"^head=.*$", "head=current_worn,id=999999,ilevel=280",
                           original,count=1,flags=re.MULTILINE)
            self.assertNotEqual(changed,original)
            (root/"current.simc").write_text(changed,encoding="utf8")
            raw["character"]=None
            raw["import_simc_profile"]="current.simc"
            (root/"user.json").write_text(json.dumps(raw),encoding="utf8")
            result=boot.run(root/"user.json",root/"generated",fake,"7bc10711b5")
            self.assertEqual(result["plan"]["class"],"warrior")
            self.assertEqual(result["plan"]["spec"],"fury")
            output=(root/"generated"/"profile.simc").read_text("utf8")
            self.assertNotIn("id=999999",output)
            self.assertNotIn("ilevel=280",output)
            self.assertEqual(result["plan"]["item_slots"],16)
            self.assertFalse((root/"generated"/"simc_results").exists())
            self.assertNotIn("import_simc_profile",
                             (root/"generated"/"manifest.json").read_text())

    def test_optional_import_ambiguity_and_incomplete_character_block(self):
        user=case("frost")
        source=(boot.FIXTURES/boot.ARCHETYPES[("mage","frost")][0]
                ).read_text("utf8")
        with tempfile.TemporaryDirectory() as td:
            fake=pathlib.Path(td)/"dummy";fake.write_bytes(b"NO_NATIVE")
            user["import_simc_profile"]="some.simc"
            with self.assertRaisesRegex(boot.UserScenarioBlocked,
                                        "SIMC_IMPORT_AND_MANUAL_CHARACTER_AMBIGUOUS"):
                boot.build(user,pathlib.Path(td)/"generate",fake,
                           "7bc10711b5",imported_profile_text=source)
            user["character"]=None
            for bad in (source+"\nrace=human\n",
                        re.sub(r"^talents=.*$", "",source,count=1,flags=re.MULTILINE),
                        source+"\nwarrior=another\n"):
                with self.subTest(bad=bad[-30:]):
                    with self.assertRaisesRegex(boot.UserScenarioBlocked,
                                   "SIMC_IMPORT_CHARACTER_INCOMPLETE_OR_AMBIGUOUS"):
                        boot.build(user,pathlib.Path(td)/"generate",fake,
                                   "7bc10711b5",imported_profile_text=bad)
            self.assertFalse((pathlib.Path(td)/"generate"/"manifest.json").exists())

    def test_import_character_missing_file_fails_without_internal_output(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            fake=root/"dummy";fake.write_bytes(b"NO_NATIVE")
            user=case("fury");user["character"]=None
            user["import_simc_profile"]="missing.simc"
            (root/"user.json").write_text(json.dumps(user))
            with self.assertRaisesRegex(boot.UserScenarioBlocked,
                                        "SIMC_IMPORT_NOT_FOUND"):
                boot.run(root/"user.json",root/"generate",fake,"7bc10711b5")
            self.assertFalse((root/"generate").exists())

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
