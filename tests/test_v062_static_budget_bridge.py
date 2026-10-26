"""v062 native-static G and L assembly, with no proc-effects logic."""
import copy,json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
sys.path.insert(0,str(ROOT/"tests"))
import v046_static_item_cache as native
import v061_scenario_contract as scenario
import v062_static_budget_bridge as p
from test_v061_scenario_contract import mage,item,manual

FILLER=[
 item("neck",251142),item("hands",268243),item("waist",268257),
 item("feet",268218),item("finger1",158366),item("finger2",159459),
 item("main_hand",268205)]

def record(c,slot_item,secondary=None):
    native_id=p.exact_identity(slot_item)
    stat=secondary or {"crit_rating":100,"haste_rating":0,
                       "mastery_rating":0,"versatility_rating":0}
    snapshot={"secondary":stat,"primary_other":dict.fromkeys(native.PRIMARY,0),
              "weapon_if_native":{}}
    c["variants"][native.digest(native_id)]={
      "identity":native_id,"static":snapshot,
      "static_digest":native.digest(snapshot),
      "source_kind":"NATIVE_JSON2_RESOLVED_VARIANT"}
    return c

def fixture(src=None,filler=None):
    doc=src or mage()
    selected=doc["equipment"]
    filler=copy.deepcopy(filler if filler is not None else FILLER)
    cache=native.empty_cache()
    for row in sum((selected[k] for k in ("tier","crafted","special")),[])+filler:
        record(cache,row)
    return scenario.normalize(doc),filler,cache

class NativeBudget(unittest.TestCase):
    def test_complete_13_slots_derived_budget_and_external_oil(self):
        plan,fill,cache=fixture()
        r=p.compile_static_budget(plan,fill,cache)
        self.assertEqual(r["status"],"STATIC_BUDGET_COMPILED_NEEDS_P3_NATIVE_RECONCILIATION")
        self.assertEqual(r["G_if_complete"],1300)
        self.assertEqual(r["budget"]["T_official"],1603)
        self.assertEqual(r["budget"]["J"],138)
        self.assertEqual(r["budget"]["F"],165)
        self.assertEqual(r["standard_filler_count"],7)
        self.assertEqual(r["gear_items_total"],15)
        self.assertEqual(len(r["selected_trinkets"]),2)
        self.assertTrue(r["budget"]["oil_stays_OUTSIDE_T"])
        self.assertEqual(r["budget"]["external_temporary_rating"]["crit_rating"],16)
        self.assertIsNone(r["selected_trinkets"][0]["native_static_if_reported"])
    def test_t_with_no_native_g_remains_unresolved(self):
        plan,fill,cache=fixture()
        key=native.digest(p.exact_identity(fill[0]));del cache["variants"][key]
        r=p.compile_static_budget(plan,fill,cache)
        self.assertEqual(r["status"],"NEEDS_NATIVE_G_FOR_DERIVED_TARGET")
        self.assertIsNone(r["G_if_complete"])
        self.assertIsNone(r["budget"]["T_official"])
        self.assertEqual(len(r["missing_nontrinket_static"]),1)
        self.assertEqual(r["missing_nontrinket_static"][0]["item_id"],251142)
    def test_manual_total_still_usable_with_missing_ordinary_G(self):
        cfg=manual()
        plan,fill,cache=fixture(cfg,[
            dict(item_,ilevel=331) for item_ in FILLER])
        del cache["variants"][native.digest(p.exact_identity(fill[0]))]
        r=p.compile_static_budget(plan,fill,cache)
        self.assertEqual(r["status"],"MANUAL_TARGET_READY_G_PARTIALLY_UNOBSERVED")
        self.assertEqual(r["budget"]["T_official"],3000)
        self.assertIsNone(r["G_if_complete"])
    def test_fixed_special_locked_L_is_only_counted_once_in_G(self):
        cfg=mage()
        cfg["equipment"]["special"]=[item("neck",251001)]
        filler=[x for x in FILLER if x["slot"]!="neck"]
        plan,fill,cache=fixture(cfg,filler)
        lock={"crit_rating":0,"haste_rating":0,
              "mastery_rating":170,"versatility_rating":0}
        record(cache,cfg["equipment"]["special"][0],lock)
        r=p.compile_static_budget(plan,fill,cache)
        self.assertEqual(r["G_if_complete"],1370)
        self.assertEqual(r["budget"]["T_official"],1673)
        self.assertEqual(r["locked_L_when_all_specials_observed"],lock)
        self.assertEqual(r["effective_floor_if_possible"]["mastery_rating"],170)
    def test_catalyzed_tier_is_one_slot_and_locked_original_fixed_L(self):
        cfg=mage()
        source=cfg["equipment"]["tier"][0]
        source["options"]={"redirected_base_stats":"268222"}
        cfg["equipment"]["catalyst_special_tier_slots"]=["head"]
        plan,fill,c=fixture(cfg)
        stats={"crit_rating":0,"haste_rating":0,
               "mastery_rating":170,"versatility_rating":0}
        record(c,source,stats)
        out=p.compile_static_budget(plan,fill,c)
        self.assertEqual(len(cfg["equipment"]["tier"]),4)
        self.assertEqual(len(cfg["equipment"]["special"]),0)
        self.assertEqual(out["locked_L_when_all_specials_observed"],stats)
        self.assertEqual(out["G_if_complete"],1370)
        self.assertEqual(out["budget"]["T_official"],1673)
        self.assertEqual(out["effective_floor_if_possible"]["mastery_rating"],170)
        self.assertEqual(out["gear_items_total"],15)

    def test_unselected_redirected_tier_does_not_lock_any_L(self):
        cfg=mage()
        cfg["equipment"]["tier"][0]["options"]={"redirected_base_stats":"268222"}
        plan,fill,c=fixture(cfg)
        result=p.compile_static_budget(plan,fill,c)
        self.assertEqual(sum(result["locked_L_when_all_specials_observed"].values()),0)
        self.assertEqual(result["G_if_complete"],1300)
        self.assertEqual(result["budget"]["T_official"],1603)

    def test_catalyzed_tier_missing_exact_source_variant_is_not_zero(self):
        cfg=mage()
        source=cfg["equipment"]["tier"][0]
        source["options"]={"redirected_base_stats":"268222"}
        cfg["equipment"]["catalyst_special_tier_slots"]=["head"]
        plan,fill,c=fixture(cfg)
        del c["variants"][native.digest(p.exact_identity(source))]
        out=p.compile_static_budget(plan,fill,c)
        self.assertEqual(out["status"],"NEEDS_NATIVE_SPECIAL_FIXED_L")
        self.assertEqual(len(out["missing_special_fixed_static"]),1)
        self.assertIsNone(out["locked_L_when_all_specials_observed"])
        self.assertIsNone(out["effective_floor_if_possible"])

    def test_missing_selected_special_requires_exact_native_floor(self):
        cfg=mage();cfg["equipment"]["special"]=[item("neck",251001)]
        filler=[x for x in FILLER if x["slot"]!="neck"]
        plan,fill,cache=fixture(cfg,filler)
        del cache["variants"][native.digest(p.exact_identity(cfg["equipment"]["special"][0]))]
        r=p.compile_static_budget(plan,fill,cache)
        self.assertEqual(r["status"],"NEEDS_NATIVE_SPECIAL_FIXED_L")
        self.assertIsNone(r["locked_L_when_all_specials_observed"])
        self.assertIsNone(r["budget"]["T_official"])
        self.assertEqual(len(r["missing_special_fixed_static"]),1)
    def test_duplicate_filler_over_selected_slot_rejected(self):
        plan,fill,cache=fixture()
        fill.append(item("back",239656))
        with self.assertRaisesRegex(p.BudgetBlocked,"FILLER_OVERWRITES_SELECTED_GEAR"):
            p.compile_static_budget(plan,fill,cache)
    def test_no_filler_missing_required_main_hand_is_reported(self):
        plan,fill,cache=fixture()
        fill=[r for r in fill if r["slot"]!="main_hand"]
        with self.assertRaisesRegex(p.BudgetBlocked,"REPRESENTATIVE_GEAR_SLOTS_UNFILLED"):
            p.compile_static_budget(plan,fill,cache)
    def test_two_trinkets_may_have_known_static_and_still_zero_G_contribution(self):
        plan,fill,cache=fixture()
        record(cache,plan["scenario"]["equipment"]["trinkets"][0],
               {"crit_rating":0,"haste_rating":90,"mastery_rating":0,"versatility_rating":0})
        p1=p.compile_static_budget(plan,fill,cache)
        self.assertEqual(p1["G_if_complete"],1300)
        self.assertEqual(p1["selected_trinkets"][0]["native_static_if_reported"]["haste_rating"],90)
        self.assertFalse(p1["selected_trinkets"][0]["included_in_G"])
        self.assertEqual(p1["selected_trinkets"][1]["native_static_status"],
                         "UNREPORTED_UNKNOWN_NOT_ZERO")
    def test_crafted_stats_pair_treated_as_free_G_not_L(self):
        plan,fill,cache=fixture()
        r=p.compile_static_budget(plan,fill,cache)
        self.assertEqual(sum(r["locked_L_when_all_specials_observed"].values()),0)
        self.assertEqual(r["native_gear_stats"]["wrists"]["sum"],100)
        self.assertEqual(r["native_gear_stats"]["back"]["sum"],100)
    def test_special_with_gem_modifier_needs_numeric_separation_not_proc_gate(self):
        cfg=mage();cfg["equipment"]["special"]=[item("neck",251001,
                                           options={"gem_id":"240967"})]
        filler=[x for x in FILLER if x["slot"]!="neck"]
        plan,fill,cache=fixture(cfg,filler)
        with self.assertRaisesRegex(p.BudgetBlocked,"SPECIAL_LOCK_NEEDS_UNDECORATED_NUMERIC_VARIANT"):
            p.compile_static_budget(plan,fill,cache)
    def test_filler_with_gem_option_marks_pending_p3(self):
        cfg=mage();filler=copy.deepcopy(FILLER)
        filler[0]["options"]={"gem_id":"240967"}
        plan,fill,cache=fixture(cfg,filler)
        r=p.compile_static_budget(plan,fill,cache)
        self.assertEqual(r["status"],"STATIC_BUDGET_COMPILED_NEEDS_P3_NATIVE_RECONCILIATION")
        self.assertEqual(len(r["budget"]["ambiguous_gem_enchant_gear_rows"]),1)
        self.assertEqual(r["budget"]["ambiguous_gem_enchant_gear_rows"][0]["slot"],"neck")
    def test_native_cache_tampering_refused(self):
        plan,fill,cache=fixture()
        row=next(iter(cache["variants"].values()))
        row["static"]["secondary"]["haste_rating"]=5
        with self.assertRaises(native.CacheBlocked):
            p.compile_static_budget(plan,fill,cache)
    def test_user_defined_fraction_bound_with_locked_special_conflict(self):
        cfg=mage();cfg["equipment"]["special"]=[item("neck",251001)]
        filler=[x for x in FILLER if x["slot"]!="neck"]
        plan,fill,cache=fixture(cfg,filler)
        lock={"crit_rating":0,"haste_rating":0,"mastery_rating":2200,"versatility_rating":0}
        record(cache,cfg["equipment"]["special"][0],lock)
        with self.assertRaisesRegex(p.BudgetBlocked,"SELECTED_SPECIAL_FLOOR_UNFEASIBLE"):
            p.compile_static_budget(plan,fill,cache)
    def test_status_no_simc_calls_and_no_effect_gate(self):
        plan,fill,cache=fixture()
        r=p.compile_static_budget(plan,fill,cache)
        self.assertEqual(r["native_simc_calls"],0)
        self.assertTrue(r["item_effects_owned_by_simc"])
        self.assertFalse(r["original_product_integrated"])

if __name__=="__main__":unittest.main()
