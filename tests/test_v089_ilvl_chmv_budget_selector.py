"""v089 isolated opt-in ilvl→T bridge; no Native calls or policy promotion."""
import copy,json,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v089_ilvl_chmv_budget_selector as z
import v061_scenario_contract as contract
import v062_static_budget_bridge as bridge
import v046_static_item_cache as cache
from test_v061_scenario_contract import mage,manual,item
from test_v062_static_budget_bridge import fixture,record,FILLER

def at_level(level):
    d=mage()
    d["target"]["ilevel"]=level
    # Source accepts separate equipment ilvl; this test's equipment is scaled.
    for part in d["equipment"].values():
        for row in part:row["ilevel"]=level
    return d

class V089OptInTargetBudget(unittest.TestCase):
    def test_334_common_normalized_and_oil_excluded(self):
        p=z.resolve(mage(),mode=z.REFERENCE_MODE,weapon_layout="one_hand_frill")
        self.assertEqual(p["resolved_T"],3150)
        self.assertEqual(p["selected_track"],"general")
        self.assertEqual(p["status"],"READY_OPT_IN_REFERENCE_TOTAL_NOT_FULL_P3")
        self.assertEqual(p["scenario_plan"]["budget"]["T"],3150)
        self.assertEqual(p["scenario_plan"]["budget"]["J"],138)
        self.assertEqual(p["scenario_plan"]["budget"]["F"],165)
        self.assertEqual(p["external_O"],
            {"crit_rating":16,"haste_rating":16,
             "mastery_rating":0,"versatility_rating":0})
        self.assertFalse(p["T_includes_oil"])
        self.assertEqual(p["scenario_plan"]["scenario"]["equipment"],
                         contract.normalize(mage())["scenario"]["equipment"])
        self.assertEqual(p["native_calls"],0)
        self.assertFalse(p["original_product_integrated"])

    def test_fury_dual_twohand_334_and_321_independent_scaling(self):
        d=at_level(334)
        d["character"].update({"class":"warrior","spec":"fury","role":"attack"})
        f=z.resolve(d,mode=z.REFERENCE_MODE,weapon_layout="dual_two_hand")
        self.assertEqual(f["resolved_T"],3350)
        self.assertEqual(f["selected_track"],z.TRACK_FURY)
        b=at_level(321)
        b["character"].update({"class":"warrior","spec":"fury","role":"attack"})
        f2=z.resolve(b,mode=z.REFERENCE_MODE,weapon_layout="dual_two_hand")
        c=z.resolve(at_level(321),mode=z.REFERENCE_MODE,weapon_layout="ranged")
        self.assertEqual(f2["resolved_T"],3170)
        self.assertEqual(c["resolved_T"],2980)
        self.assertEqual(f2["resolved_T"]-c["resolved_T"],190)
        self.assertEqual(f["resolved_T"]-
                         z.resolve(mage(),mode=z.REFERENCE_MODE,
                                   weapon_layout="single_two_hand")["resolved_T"],200)

    def test_actual_manual_priority_without_reading_reference(self):
        d=manual()
        p=z.resolve(d,mode=z.REFERENCE_MODE,weapon_layout="single_two_hand",
                    reference_path=ROOT/"missing_registry.json")
        self.assertEqual(p["resolved_T"],3000)
        self.assertEqual(p["source_mode"],"user_manual_total")
        self.assertIsNone(p["reference_sha256"])
        self.assertEqual(p["scenario_plan"]["budget"]["T"],3000)
        self.assertEqual(p["native_calls"],0)

    def test_exact_g_mode_keeps_native_budget_waiting(self):
        p=z.resolve(mage(),mode=z.NATIVE_MODE,weapon_layout="one_hand_frill",
                    reference_path=ROOT/"missing_registry.json")
        self.assertEqual(p["status"],"WAIT_EXACT_NATIVE_G")
        self.assertIsNone(p["resolved_T"])
        self.assertIsNone(p["scenario_plan"]["budget"]["T"])
        self.assertEqual(p["scenario_plan"]["scenario"]["target"]["mode"],
                         "derived_ilevel")

    def test_reference_unverified_ilevel_not_fabricated(self):
        for level in (265,345):
            with self.subTest(level=level):
                with self.assertRaisesRegex(z.BudgetSelectionBlocked,
                    "ITEMLEVEL_OUTSIDE_VERIFIED_REFERENCE"):
                    z.resolve(at_level(level),mode=z.REFERENCE_MODE,
                              weapon_layout="ranged")

    def test_fury_layout_must_be_explicit_dual_twohand(self):
        d=mage();d["character"].update({"class":"warrior","spec":"fury",
                                        "role":"attack"})
        with self.assertRaisesRegex(z.BudgetSelectionBlocked,
                                  "FURY_REQUIRES_DUAL_2H"):
            z.resolve(d,mode=z.REFERENCE_MODE,weapon_layout="dual_one_hand")
        with self.assertRaisesRegex(z.BudgetSelectionBlocked,
                                  "ONLY_VALIDATED_FURY_HAS_DUAL_2H"):
            z.resolve(mage(),mode=z.REFERENCE_MODE,weapon_layout="dual_two_hand")

    def test_consumable_budget_mismatch_is_blocked(self):
        d=mage();d["consumables"]["flask_budget_F"]=166
        with self.assertRaisesRegex(z.BudgetSelectionBlocked,
                                  "REFERENCE_GEM_FLASK_BUDGET_MISMATCH"):
            z.resolve(d,mode=z.REFERENCE_MODE,weapon_layout="one_hand_frill")

    def test_registry_tampering_and_monotonicity_guard(self):
        reg,_=z.load_registry()
        with tempfile.TemporaryDirectory() as temp:
            f=pathlib.Path(temp)/"ref.json"
            reg["values"][334-266]["general"]=3140
            f.write_text(json.dumps(reg))
            with self.assertRaisesRegex(z.BudgetSelectionBlocked,
                                     "REFERENCE_334_ANCHOR_CHANGED"):
                z.load_registry(f)
            reg["values"][334-266]["general"]=3150
            reg["values"][340-266]["general"]=3000
            f.write_text(json.dumps(reg))
            with self.assertRaisesRegex(z.BudgetSelectionBlocked,
                                      "REFERENCE_STATS_NOT_MONOTONIC"):
                z.load_registry(f)

    def test_selected_special_L_stays_exact_required_and_not_double_added(self):
        d=mage()
        d["equipment"]["special"]=[item("neck",251001)]
        p=z.resolve(d,mode=z.REFERENCE_MODE,weapon_layout="one_hand_frill")
        n=p["scenario_plan"]
        normal=[x for x in FILLER if x["slot"]!="neck"]
        # Native cache for the selected special alone; no ordinary gear cache
        # fabricated.  v062 can hold exact L even with ordinary G missing.
        selected=copy.deepcopy(d["equipment"]["special"][0])
        c=cache.empty_cache()
        fixed={"crit_rating":0,"haste_rating":0,
               "mastery_rating":170,"versatility_rating":0}
        record(c,selected,fixed)
        result=bridge.compile_static_budget(n,normal,c)
        self.assertEqual(result["budget"]["T_official"],3150)
        self.assertEqual(result["locked_L_when_all_specials_observed"],fixed)
        self.assertEqual(result["effective_floor_if_possible"]["mastery_rating"],170)
        self.assertEqual(result["status"],"MANUAL_TARGET_READY_G_PARTIALLY_UNOBSERVED")
        self.assertIsNone(result["G_if_complete"])
        # A missing selected special is blocked, not guessed from common total.
        empty=bridge.compile_static_budget(n,normal,cache.empty_cache())
        self.assertEqual(empty["status"],"NEEDS_NATIVE_SPECIAL_FIXED_L")
        self.assertEqual(len(empty["missing_special_fixed_static"]),1)

    def test_known_trinket_missing_static_does_not_block_opt_in_total(self):
        p=z.resolve(mage(),mode=z.REFERENCE_MODE,weapon_layout="one_hand_frill")
        self.assertFalse(p["scenario_plan"]["budget"]
                         ["native_static_stat_record_required_for_trinkets"])
        self.assertEqual(len(p["scenario"]["equipment"]["trinkets"]),2)

    def test_noninteractive_cli_writes_separate_provenance(self):
        with tempfile.TemporaryDirectory() as temp:
            root=pathlib.Path(temp)
            src=root/"scenario.json";dst=root/"chosen.json"
            src.write_text(json.dumps(mage()))
            self.assertEqual(z.main(["--scenario",str(src),"--mode",z.REFERENCE_MODE,
                            "--weapon-layout","one_hand_frill","--out",str(dst)]),0)
            receipt=json.loads(dst.read_text())
            self.assertEqual(receipt["resolved_T"],3150)
            self.assertEqual(receipt["source_mode"],z.REFERENCE_MODE)
            self.assertTrue(len(receipt["reference_sha256"])==64)

if __name__=="__main__":unittest.main()
