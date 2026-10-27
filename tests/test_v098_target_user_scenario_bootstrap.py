"""v098 target-level USER controls -> full internal v096 plan, offline only."""
import json,os,pathlib,re,subprocess,sys,tempfile,unittest
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
             "beast_mastery":("hunter","beast_mastery"),
             "subtlety":("rogue","subtlety"),
             "outlaw":("rogue","outlaw"),
             "elemental":("shaman","elemental"),
             "feral":("druid","feral")}
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
                             "beast_mastery":"troll",
                             "subtlety":"dwarf","outlaw":"dwarf",
                             "elemental":"tauren","feral":"night_elf"}[which],
                     "talents":talents},
        "target":{"ilevel":ilevel,"final_T":final_T},
        "trinkets":trinkets,"special_items":[],"embellishments":[],
        "oil_hands":["main_hand","off_hand"] if which in ("fury","subtlety","outlaw")
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

    def test_six_user_plans_keep_exact_seal_under_shared_source_emitter(self):
        # Full P1 user->source->gear->runtime->manifest parity. The first
        # build uses the pre-v128 source-emission algorithm and the second
        # invokes v128. The same immutable plan/identity must replay with
        # absolutely no new Native invocation or profile byte replacement.
        from unittest import mock
        import v128_common_source_profile_emitter as emitter
        from tests.test_v128_common_source_profile_emitter import prior_serializer
        for spec in ("fury","retribution","frost","beast_mastery",
                     "subtlety","elemental"):
            with self.subTest(spec=spec),tempfile.TemporaryDirectory() as td:
                root=pathlib.Path(td)
                binary=root/"dummy_simc.exe"
                binary.write_bytes(b"FAKE_NO_NATIVE")
                folder=root/"generated"
                user=case(spec)
                with mock.patch.object(emitter,"emit",
                                       side_effect=prior_serializer):
                    old=boot.build(user,folder,binary,"7bc1071")
                sealed_profile=(folder/"profile.simc").read_bytes()
                sealed_manifest=(folder/"manifest.json").read_bytes()
                fresh=boot.build(user,folder,binary,"7bc1071")
                self.assertEqual(fresh["plan"],old["plan"])
                self.assertEqual((folder/"profile.simc").read_bytes(),
                                 sealed_profile)
                self.assertEqual((folder/"manifest.json").read_bytes(),
                                 sealed_manifest)
                self.assertFalse((folder/"simc_results").exists())

    def test_new_rogue_outlaw_plan_uses_existing_common_native_free_pipeline(self):
        import v122_common_profile_format as fmt
        import v063_numeric_injection as numeric
        import v096_unified_product_entry as entry
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            binary=root/"simc_not_executed.exe"
            binary.write_bytes(b"OFFLINE_NOT_A_SIMC_BINARY")
            user=case("outlaw")
            user["consumable_choices"]={
                "flask":"source_default","food":"source_default",
                "potion":"source_default","augmentation":"source_default",
                "diamond_id":240967,"omnium_talents":"source_default"}
            folder=root/"generated"
            result=boot.build(user,folder,binary,"7bc1071")
            raw=(folder/"profile.simc").read_bytes()
            profile=raw.decode("utf8")
            self.assertEqual(result["native_calls"],0)
            self.assertEqual((result["plan"]["base_B"],
                              result["plan"]["final_T"]),(3150,3214))
            self.assertIn("json2="+fmt.JSON2_PLACEHOLDER,profile)
            self.assertIn("gem_id=240967",profile)
            self.assertIn("main_hand=selected_268209",profile)
            self.assertIn("off_hand=selected_275070",profile)
            import v101_common_representative_equipment as common
            ordinary=[]
            for line in profile.splitlines():
                slot,sep,value=line.partition("=")
                if sep and slot in numeric.STATS:
                    continue
                if sep and slot in boot.item_mod.SLOTS and slot!="head":
                    for token in value.split(","):
                        if token.startswith("gem_id="):
                            ordinary.extend(int(x) for x in
                                            token.partition("=")[2].split("/"))
            self.assertEqual(len(ordinary),6)
            self.assertEqual(set(common.SOURCE_GEM_COLOR[x]
                                 for x in ordinary),
                             set(common.FOUR_COLOR_GEMS))
            self.assertEqual(sum(1 for line in profile.splitlines()
                                 if line.startswith("json2=")),1)
            numeric.input_parts(profile)
            sealed=entry.source(folder/"manifest.json")
            self.assertEqual(len(sealed["seeds"]),2)
            self.assertTrue(all(seed["crit_rating"]>=133
                                for seed in sealed["seeds"]))
            again=boot.build(user,folder,binary,"7bc1071")
            self.assertEqual(again["plan"],result["plan"])
            self.assertEqual((folder/"profile.simc").read_bytes(),raw)
            self.assertFalse((folder/"simc_results").exists())

    def test_all_six_new_sessions_share_canonical_profile_and_runtime_format(self):
        import v122_common_profile_format as fmt
        import v063_numeric_injection as num
        for which in ("fury","frost","retribution",
                      "beast_mastery","subtlety","elemental"):
            with self.subTest(spec=which),tempfile.TemporaryDirectory() as td:
                root=pathlib.Path(td)
                binary=root/"dummy"
                binary.write_bytes(b"NO_NATIVE")
                folder=root/"generated"
                user=case(which)
                output=boot.build(user,folder,binary,"7bc1071")
                source=(folder/"profile.simc").read_text(encoding="utf8")
                lines=source.splitlines()
                slot_order=[s.partition("=")[0] for s in lines
                            if s.partition("=")[0] in fmt.SLOT_ORDER]
                self.assertEqual(slot_order,sorted(slot_order))
                self.assertEqual(sum(l.startswith("json2=") for l in lines),1)
                self.assertEqual(sum(l.startswith("iterations=") for l in lines),1)
                self.assertIn("json2="+fmt.JSON2_PLACEHOLDER,source)
                self.assertFalse(fmt.existing_profile_uses_legacy_format(
                    folder/"profile.simc"))
                self.assertEqual(len(slot_order),output["plan"]["item_slots"])
                num.input_parts(source)
                # Universal F/O feasibility is enforced at seed creation,
                # not introduced as a rogue-specific material workaround.
                manifest=json.loads((folder/"manifest.json").read_text())
                cfg=json.loads((folder/"scenario.json").read_text())
                fixed_F=boot.ARCHETYPES[
                    (user["character"]["class"],user["character"]["spec"])][3]
                fixed_O=cfg["consumables"]["weapon_temporary_fixed_rating"]
                for seed in manifest["seed_targets_B"]:
                    self.assertTrue(all(seed[k]+fixed_O[k]>=fixed_F[k]
                                        for k in num.STATS))
                self.assertFalse((folder/"simc_results").exists())
                self.assertEqual(boot.build(user,folder,binary,"7bc1071")
                                 ["plan"]["base_B"],output["plan"]["base_B"])
                self.assertEqual((folder/"profile.simc").read_text(
                    encoding="utf8"),source)

    def test_v104_240967_plan_generates_json2_native_request_without_mutating_seal(self):
        # Integrated source -> seeded v093 Native INPUT only, no SimC execution.
        # Source v104 lacked json2; all NEW sessions now use v122 canonical output.
        for spec in ("subtlety","elemental"):
            with self.subTest(spec=spec),tempfile.TemporaryDirectory() as td:
                root=pathlib.Path(td)
                binary=root/"dummy.exe"
                binary.write_bytes(b"NO_NATIVE")
                user=case(spec)
                user["consumable_choices"]={
                    "flask":"source_default","food":"source_default",
                    "potion":"source_default","augmentation":"source_default",
                    "diamond_id":240967,"omnium_talents":"source_default"}
                folder=root/"generated"
                plan=boot.build(user,folder,binary,"7bc1071")
                original=(folder/"profile.simc").read_bytes()
                self.assertEqual(sum(line.startswith(b"json2=")
                                     for line in original.splitlines()),1)
                self.assertEqual((plan["plan"]["base_B"],
                                  plan["plan"]["final_T"]),
                                 (3150,3214 if spec=="subtlety" else 3182))
                sealed=old.source(folder/"manifest.json")
                req=old.adaptive.request(
                    sealed["context"],sealed["seeds"][0],sealed["flask"],
                    root/"out"/"result.json",phase="seed")
                self.assertEqual(req["status"],"PROPOSED_STATIC_C_NO_NATIVE")
                self.assertEqual(sum(line.startswith("json2=")
                                     for line in req["input"].splitlines()),1)
                self.assertEqual(sum(line.startswith("iterations=")
                                     for line in req["input"].splitlines()),1)
                self.assertIn("gem_id=240967",req["input"])
                self.assertEqual((folder/"profile.simc").read_bytes(),original)
                self.assertFalse((folder/"simc_results").exists())

    def test_v104_old_and_new_processes_replay_same_immutable_240967_plan(self):
        # Simulate the OLD set-derived equipment order, then execute the
        # identical plan in a different Python process with a new hash seed.
        # No Native SimC binary is executed (fake executable file only).
        older=(
            "import pathlib,sys;"
            "sys.path.insert(0,sys.argv[1]);"
            "import v104_shared_pinned_rogue_shaman_composer as v104;"
            "import v098_target_user_scenario_bootstrap as v098;"
            "import v122_common_profile_format as v122;"
            "v104.ALL_SLOTS=tuple(reversed(v104.ALL_SLOTS));"
            "v122.order_rows=lambda rows,legacy: rows;"
            "v122.finalize=lambda profile,legacy: profile;"
            "v098.run(pathlib.Path(sys.argv[2]),pathlib.Path(sys.argv[3]),"
            "pathlib.Path(sys.argv[4]),sys.argv[5])"
        )
        for spec in ("subtlety","elemental"):
            with self.subTest(spec=spec),tempfile.TemporaryDirectory() as td:
                root=pathlib.Path(td)
                data=case(spec)
                data["consumable_choices"]={
                    "flask":"source_default","food":"source_default",
                    "potion":"source_default","augmentation":"source_default",
                    "diamond_id":240967,"omnium_talents":"source_default"}
                src=root/"user.json"
                src.write_text(json.dumps(data),encoding="utf8")
                fake=root/"simc.exe"
                fake.write_bytes(b"do not run")
                generated=root/"generated"
                args=[str(src),str(generated),str(fake),"7bc1071"]
                env={**os.environ,"PYTHONHASHSEED":"23"}
                old=subprocess.run(
                    [sys.executable,"-c",older,str(ROOT/"runner"),*args],
                    cwd=str(ROOT),env=env,capture_output=True,text=True)
                self.assertEqual(old.returncode,0,old.stderr)
                sealed=(generated/"profile.simc").read_bytes()
                other=subprocess.run(
                    [sys.executable,str(ROOT/"runner"/
                                   "v098_target_user_scenario_bootstrap.py"),
                     "--input",str(src),"--out",str(generated),
                     "--binary",str(fake),"--revision","7bc1071"],
                    cwd=str(ROOT),env={**os.environ,"PYTHONHASHSEED":"137"},
                    capture_output=True,text=True)
                self.assertEqual(other.returncode,0,other.stderr)
                self.assertEqual((generated/"profile.simc").read_bytes(),sealed)
                self.assertFalse((generated/"simc_results").exists())
        import v104_shared_pinned_rogue_shaman_composer as v104
        self.assertEqual(v104.ALL_SLOTS,tuple(sorted(v104.ALL_SLOTS)))

    def test_v104_existing_profile_content_drift_is_never_overwritten(self):
        user=case("subtlety")
        user["consumable_choices"]={
            "flask":"source_default","food":"source_default",
            "potion":"source_default","augmentation":"source_default",
            "diamond_id":240967,"omnium_talents":"source_default"}
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            binary=root/"dummy_simc.exe"
            binary.write_bytes(b"NEVER EXECUTE")
            folder=root/"generated"
            boot.build(user,folder,binary,"7bc1071")
            profile=folder/"profile.simc"
            original=profile.read_bytes()
            self.assertIn(b"desired_targets=1",original)
            changed=original.replace(b"desired_targets=1",
                                     b"desired_targets=2",1)
            profile.write_bytes(changed)
            with self.assertRaisesRegex(boot.UserScenarioBlocked,
                                        "EXISTING_BOOTSTRAP_FILE_CHANGED:profile.simc"):
                boot.build(user,folder,binary,"7bc1071")
            self.assertEqual(profile.read_bytes(),changed)
            self.assertFalse((folder/"simc_results").exists())

    def test_rogue_and_shaman_user_boot_produce_normalized_full_profiles(self):
        for name,role,weapon_form,secondary in (
            ("subtlety","attack","dual_one_hand",64),
            ("elemental","spell","one_hand_shield",32)):
            with self.subTest(spec=name):
                user=case(name)
                result,root=self.prepare(user)
                self.assertEqual(result["native_calls"],0)
                self.assertEqual(result["supported_archetypes_now"],24)
                self.assertEqual(result["plan"]["item_slots"],16)
                self.assertEqual(result["plan"]["base_B"],3150)
                self.assertEqual(result["plan"]["final_T"],3150+secondary)
                self.assertEqual(result["weapon_form"],weapon_form)
                self.assertEqual(len(result["effective_four_tier_slots"]),4)
                self.assertFalse(result["restored_tier_slots"])
                cfg=json.loads((root/"generated"/"scenario.json").read_text())
                self.assertEqual(cfg["character"]["role"],role)
                self.assertEqual(len(cfg["equipment"]["tier"]),4)
                self.assertEqual(len(cfg["equipment"]["trinkets"]),2)
                self.assertEqual(cfg["equipment"]["special"],[])
                p=(root/"generated"/"profile.simc").read_text()
                reference=(boot.FIXTURES/boot.ARCHETYPES[
                    (user["character"]["class"],user["character"]["spec"])][0]
                    ).read_text("utf8")
                self.assertEqual([x for x in p.splitlines()
                                  if x.startswith("actions")],
                                 [x for x in reference.splitlines()
                                  if x.startswith("actions")])
                self.assertNotIn("omitted_gear",p)
                self.assertEqual(sum(x.startswith("main_hand=") for x in p.splitlines()),1)
                self.assertEqual(sum(x.startswith("off_hand=") for x in p.splitlines()),1)
                self.assertEqual(sum(",ilevel=334" in x for x in p.splitlines()),16)
                self.assertFalse((root/"generated"/"simc_results").exists())

    def test_rogue_and_shaman_crafted_replaces_tier_and_restores_fifth(self):
        for name,fifth,fifth_id,crafted_id in (
            ("subtlety","chest",271513,244572),
            ("elemental","head",271483,244580)):
            with self.subTest(spec=name):
                user=case(name)
                user["embellishments"]=[{
                    "slot":"shoulders","item_id":crafted_id,
                    "options":{"crafted_stats":"49/36",
                               "embellishment":"arcanoweave_lining"}}]
                result,root=self.prepare(user)
                self.assertEqual(result["restored_tier_slots"],[fifth])
                self.assertIn(fifth,result["effective_four_tier_slots"])
                self.assertNotIn("shoulders",result["effective_four_tier_slots"])
                self.assertEqual(result["plan"]["item_slots"],16)
                cfg=json.loads((root/"generated"/"scenario.json").read_text())
                self.assertEqual(len(cfg["equipment"]["tier"]),4)
                self.assertEqual(next(x for x in cfg["equipment"]["tier"]
                                      if x["slot"]==fifth)["item_id"],fifth_id)

    def test_new_source_shaman_catalyst_fifth_and_crafted_tier_lock_once(self):
        user=case("elemental")
        user["special_items"]=[
          {"slot":"head","item_id":271483,
           "options":{"redirected_base_stats":"268231","bonus_id":"13848"}}]
        user["embellishments"]=[
          {"slot":"shoulders","item_id":244580,
           "options":{"crafted_stats":"49/36",
                      "embellishment":"arcanoweave_lining"}}]
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td);binary=root/"dummy";binary.write_bytes(b"NO_NATIVE")
            cache=boot.cache_mod.empty_cache()
            catalyst={"slot":"head","item_id":271483,"ilevel":334,
                      "options":{"redirected_base_stats":"268231",
                                 "bonus_id":"13848"}}
            fixed={"crit_rating":0,"haste_rating":175,
                   "mastery_rating":0,"versatility_rating":0}
            offline_record(cache,catalyst,fixed)
            fp=root/"static.json";boot.cache_mod.write_atomic(fp,cache)
            result=boot.build(user,root/"profile",binary,"7bc10711b5",
                              static_cache_path=fp)
            self.assertEqual(result["plan"]["base_B"],3150)
            self.assertEqual(result["plan"]["final_T"],3182)
            self.assertEqual(result["effective_four_tier_slots"],
                             ["chest","hands","head","legs"])
            self.assertEqual(result["catalyst_origin_items"],[
                {"slot":"head","tier_item_id":271483,"source_item_id":268231}])
            cfg=json.loads((root/"profile"/"scenario.json").read_text())
            self.assertEqual(cfg["equipment"]["catalyst_special_tier_slots"],
                             ["head"])
            fill=json.loads((root/"profile"/"fillers.json").read_text())
            budget=native_budget.compile_static_budget(scenario.normalize(cfg),
                                                        fill,cache)
            self.assertEqual(budget["locked_L_when_all_specials_observed"],fixed)
            self.assertEqual(budget["missing_special_fixed_static"],[])
            lines=(root/"profile"/"profile.simc").read_text().splitlines()
            head=[x for x in lines if x.startswith("head=")]
            self.assertEqual(len(head),1)
            self.assertIn("redirected_base_stats=268231",head[0])
            self.assertIn("bonus_id=13848",head[0])
            self.assertNotIn("temporary_enchant=main_hand:thalassian_phoenix_oil_2",
                             head[0])
            self.assertFalse((root/"profile"/"simc_results").exists())

    def test_new_source_rogue_catalyst_without_exact_L_not_falsely_zero(self):
        user=case("subtlety")
        user["special_items"]=[
            {"slot":"head","item_id":271510,
             "options":{"redirected_base_stats":"271875"}}]
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td);binary=root/"dummy";binary.write_bytes(b"NO_NATIVE")
            with self.assertRaisesRegex(Exception,
                    "SPECIAL_L_REQUIRES_EXACT_NATIVE_STATIC_VARIANT"):
                boot.build(user,root/"profile",binary,"7bc10711b5")
            self.assertFalse((root/"profile"/"manifest.json").exists())

    def test_new_specs_target_level_manual_final_and_unknown_spec_block(self):
        u=case("elemental",ilevel=321,final_T=3020)
        out,_=self.prepare(u)
        self.assertEqual((out["plan"]["base_B"],out["plan"]["final_T"]),
                         (2988,3020))
        u=case("subtlety",ilevel=321)
        out,_=self.prepare(u)
        self.assertEqual((out["plan"]["base_B"],out["plan"]["final_T"]),
                         (2980,3044))
        # Evoker remains unpinned despite Feral joining the beta route.
        u["character"]["class"]="evoker"
        u["character"]["spec"]="devastation"
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td);binary=root/"dummy";binary.write_bytes(b"NO_NATIVE")
            with self.assertRaisesRegex(boot.UserScenarioBlocked,
                                        "REPRESENTATIVE_ARCHETYPE_NOT_READY"):
                boot.build(u,root/"output",binary,"7bc10711b5")

    def test_feral_user_target334_connects_without_native_or_original_gear_budget(self):
        u=case("feral")
        result,root=self.prepare(u)
        self.assertEqual(result["native_calls"],0)
        self.assertEqual(result["supported_archetypes_now"],24)
        self.assertEqual(result["plan"]["base_B"],3150)
        self.assertEqual(result["plan"]["final_T"],3182)
        self.assertEqual(result["plan"]["item_slots"],15)
        self.assertEqual(len(result["effective_four_tier_slots"]),4)
        profile=(root/"generated"/"profile.simc").read_text(encoding="utf8")
        self.assertIn("head=selected_271528,id=271528,ilevel=334",profile)
        self.assertIn("gem_id=240983",next(x for x in profile.splitlines()
                                               if x.startswith("head=")))
        self.assertIn("gem_id=240914/240890",next(
            x for x in profile.splitlines() if x.startswith("neck=")))
        self.assertFalse((root/"generated"/"simc_results").exists())
        self.assertFalse((root/"generated"/"V094_RESULT.json").exists())

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

    def test_registered_ordinary_material_seed_coverage_reported_not_full_profile(self):
        for name,material,count in (
            ("fury","plate",3),("retribution","plate",3),
            ("frost","cloth",3),("beast_mastery","mail",4)):
            with self.subTest(spec=name):
                result,_=self.prepare(case(name))
                self.assertEqual(result["armor_family"],material)
                self.assertEqual(len(result["ordinary_armor_seed_slots_available"]),count)
                self.assertTrue(result["ordinary_armor_seed_pool_partial_not_full_set"])
                self.assertEqual(result["plan"]["base_B"],
                                 3350 if name=="fury" else 3150)
                self.assertEqual(result["native_calls"],0)

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
                            "CATALYST_REQUIRES_CLASS_TIER_SLOT"):
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

    def test_pre_v124_sealed_seed_pair_replays_without_native_or_manifest_rewrite(self):
        # Simulate a real user's historical plan: seed policies changed when
        # fixed F/O floors were introduced, but saved candidate identity did
        # not. Only deterministic old seeds which satisfy NEW bounds can replay.
        import copy
        from unittest import mock
        for name in ("subtlety","elemental"):
            with self.subTest(spec=name),tempfile.TemporaryDirectory() as td:
                root=pathlib.Path(td)
                binary=root/"fake.exe";binary.write_bytes(b"OFFLINE_ONLY")
                user=case(name)
                user["consumable_choices"]={
                    "flask":"source_default","food":"source_default",
                    "potion":"source_default","augmentation":"source_default",
                    "diamond_id":240967,"omnium_talents":"source_default"}
                folder=root/"generated"
                with mock.patch.object(
                    boot.scheduler,"budget_with_fixed_components",
                    side_effect=lambda norm,budget,F,O: copy.deepcopy(budget)):
                    first=boot.build(user,folder,binary,"7bc1071")
                sealed=(folder/"manifest.json").read_bytes()
                old_seeds=json.loads(sealed)["seed_targets_B"]
                plan=old.source(folder/"manifest.json")
                context=plan["context"]
                normalized=context["bundle"]["prepared"]["scenario"]
                static=context["bundle"]["prepared"]["static_budget"]
                new=boot.scheduler.budget_with_fixed_components(
                    normalized,static,plan["flask"],
                    context["identity"]["oil_vector"])
                B,lo,hi=boot.scheduler.bounds(normalized,new)
                new_seeds=boot.initial_seeds(B,lo,hi)
                self.assertNotEqual(new_seeds,old_seeds)
                again=boot.build(user,folder,binary,"7bc1071")
                self.assertEqual(again["plan"]["base_B"],first["plan"]["base_B"])
                self.assertEqual((folder/"manifest.json").read_bytes(),sealed)
                self.assertFalse((folder/"simc_results").exists())

    def test_native_session_seed_identity_prevents_manifest_repointing(self):
        # Synthetic sealed identity only; no Native calls or forged PASS.
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            binary=root/"fake.exe";binary.write_bytes(b"NO_NATIVE")
            folder=root/"generated"
            user=case("subtlety")
            boot.build(user,folder,binary,"7bc1071")
            original=(folder/"manifest.json").read_bytes()
            native=folder/"simc_results"
            native.mkdir()
            (native/"V094_SESSION_IDENTITY.json").write_text(
                json.dumps({"seed_base_targets":[]}),encoding="utf8")
            with self.assertRaisesRegex(boot.UserScenarioBlocked,
                 "EXISTING_MANIFEST_SEEDS_DISAGREE_WITH_NATIVE_IDENTITY"):
                boot.build(user,folder,binary,"7bc1071")
            self.assertEqual((folder/"manifest.json").read_bytes(),original)
            self.assertFalse((native/"V094_RESULT.json").exists())

    def test_modified_legacy_seed_pair_remains_fail_closed(self):
        import copy
        from unittest import mock
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            binary=root/"fake.exe";binary.write_bytes(b"OFFLINE_ONLY")
            folder=root/"generated"
            user=case("subtlety")
            with mock.patch.object(
                boot.scheduler,"budget_with_fixed_components",
                side_effect=lambda norm,budget,F,O: copy.deepcopy(budget)):
                boot.build(user,folder,binary,"7bc1071")
            manifest=folder/"manifest.json"
            altered=json.loads(manifest.read_text(encoding="utf8"))
            altered["seed_targets_B"][0]["crit_rating"]+=1
            altered["seed_targets_B"][0]["mastery_rating"]-=1
            manifest.write_text(json.dumps(altered),encoding="utf8")
            original=manifest.read_bytes()
            with self.assertRaisesRegex(
                boot.UserScenarioBlocked,
                "EXISTING_SESSION_SEEDS_UNRECOGNIZED_OR_CHANGED"):
                boot.build(user,folder,binary,"7bc1071")
            self.assertEqual(manifest.read_bytes(),original)

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
