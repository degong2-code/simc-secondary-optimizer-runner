"""v051: crafted equipment coverage, fixed embellishments, flexible stat budget."""
import copy,json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v046_static_item_cache as v46
import v051_crafted_embellishment_bridge as v51

CAT=ROOT/"integration_probes/catalog/v051_crafted_armor_weapon_reference.json"
def fresh():
    c=v46.empty_cache()
    a={"identity":{"season":v46.SEASON,"item_id":239648,"ilevel":331,
       "slot":"wrists","options":{"crafted_stats":"49/36"}},
       "static":{"secondary":{"crit_rating":0,"haste_rating":56,
            "mastery_rating":56,"versatility_rating":0},
            "primary_other":{"strength":0,"agility":0,"intellect":103,"stragiint":0,
                             "stamina":2124,"armor":0},
            "weapon_if_native":{}},
       "source_kind":"NATIVE_JSON2_RESOLVED_VARIANT"}
    a["static_digest"]=v46.digest(a["static"])
    c["variants"][v46.digest(a["identity"])]=a
    return c

class CraftedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.catalog=v51.load_reference(CAT)
    def test_all_armor_families_and_weapons_have_id_examples(self):
        xs=list(self.catalog[1].values())
        self.assertEqual(set(x["armor_family"] for x in xs if x["armor_family"] in v51.ARMORS),set(v51.ARMORS))
        self.assertTrue(any(x["weapon_role"]=="one_hand_axe" for x in xs))
        self.assertTrue(any(x["weapon_role"]=="two_hand_staff" for x in xs))
        self.assertTrue(any(x["weapon_role"]=="offhand" for x in xs))
        self.assertFalse(self.catalog[0]["completeness"].startswith("COMPLETE"))
    def test_two_ornaments_keep_tier_and_special_slots(self):
        pieces=[
            {"item_id":239648,"item_level":331,"slot":"wrists","crafted_stats":"49/36",
             "embellishment":"arcanoweave_lining"},
            {"item_id":239656,"item_level":331,"slot":"back","crafted_stats":"49/36",
             "embellishment":"arcanoweave_lining"}]
        r=v51.validate_two_slots(pieces,"cloth",self.catalog,
           tier_slots=("head","shoulders","chest","hands"),
           special_slots=("legs",))
        self.assertEqual(r["embellishment_count"],2)
        self.assertEqual(r["selected_slots"],["back","wrists"])
        self.assertFalse(r["secondary_pair_treated_as_fixed_floor"])
        self.assertEqual(r["status"],"PLAN_ONLY_NEEDS_SIMC_EFFECT_VALIDATION")
        self.assertFalse(r["product_code_integrated"])
        self.assertFalse(r["official_policy_promoted"])
    def test_missing_or_third_embellishment_rejected(self):
        obj={"item_id":239648,"item_level":331,"slot":"wrists",
             "crafted_stats":"49/36","embellishment":"arcanoweave_lining"}
        with self.assertRaisesRegex(v46.CacheBlocked,"EXACTLY_TWO_EMBELLISHED_PIECES"):
            v51.validate_two_slots([obj],"cloth",self.catalog)
        with self.assertRaisesRegex(v46.CacheBlocked,"EXACTLY_TWO_EMBELLISHED_PIECES"):
            v51.validate_two_slots([obj]*3,"cloth",self.catalog)
    def test_duplicate_slot_rejected(self):
        obj={"item_id":239648,"item_level":331,"slot":"wrists",
             "crafted_stats":"49/36","embellishment":"arcanoweave_lining"}
        with self.assertRaisesRegex(v46.CacheBlocked,"CRAFT_SLOT_OVERLAP"):
            v51.validate_two_slots([obj,obj],"cloth",self.catalog)
    def test_wrong_class_armor_rejected(self):
        a={"item_id":244584,"item_level":331,"slot":"wrists",
           "crafted_stats":"49/36","embellishment":"arcanoweave_lining"}
        b={"item_id":239656,"item_level":331,"slot":"back",
           "crafted_stats":"49/36","embellishment":"arcanoweave_lining"}
        with self.assertRaisesRegex(v46.CacheBlocked,"WRONG_ARMOR_CLASS"):
            v51.validate_two_slots([a,b],"cloth",self.catalog)
    def test_tier_overlap_rejected(self):
        a={"item_id":239648,"item_level":331,"slot":"wrists",
           "crafted_stats":"49/36","embellishment":"arcanoweave_lining"}
        b={"item_id":239656,"item_level":331,"slot":"back",
           "crafted_stats":"49/36","embellishment":"arcanoweave_lining"}
        with self.assertRaisesRegex(v46.CacheBlocked,"CRAFT_SLOT_OVERLAP"):
            v51.validate_two_slots([a,b],"cloth",self.catalog,tier_slots=("wrists",))
    def test_stat_token_is_not_numeric_rating(self):
        self.assertEqual(v51.crafted_token("49/36"),"49/36")
        for token in ("49/49","16/7","49/400","49","a/b"):
            with self.assertRaises(v46.CacheBlocked):v51.crafted_token(token)
    def test_native_50_50_is_only_budget_not_fixed_lock(self):
        d=v51.native_crafted_budget(fresh(),239648,331,"wrists","49/36")
        self.assertEqual(d["native_static_CHMV_total"],112)
        self.assertEqual(d["observed_base_split_for_DIAGNOSTICS_ONLY"]["haste_rating"],56)
        self.assertTrue(all(x==0 for x in d["free_allocation_floor_from_base_split"].values()))
        self.assertTrue(d["requires_real_SimC_item_embl_effect_check"])
        self.assertFalse(d["native_itemlevel_reachability_attested"])
    def test_no_native_variant_must_not_infer_simc_stats(self):
        with self.assertRaisesRegex(v46.CacheBlocked,"SIMC_NATIVE_CRAFTED_VARIANT_NOT_COLLECTED"):
            v51.native_crafted_budget(fresh(),237834,331,"wrists","49/36")
    def test_split_with_rounding_one_is_valid(self):
        c=fresh()
        v=next(iter(c["variants"].values()))
        v["static"]["secondary"]["mastery_rating"]=55
        v["static_digest"]=v46.digest(v["static"])
        d=v51.native_crafted_budget(c,239648,331,"wrists","49/36")
        self.assertEqual(d["native_static_CHMV_total"],111)
    def test_native_asymmetry_greater_than_one_fails(self):
        c=fresh()
        v=next(iter(c["variants"].values()))
        v["static"]["secondary"]["mastery_rating"]=45
        v["static_digest"]=v46.digest(v["static"])
        with self.assertRaisesRegex(v46.CacheBlocked,"CRAFTED_50_50_NATIVE_ASSUMPTION_NOT_MET"):
            v51.native_crafted_budget(c,239648,331,"wrists","49/36")
    def test_source_catalog_does_not_autopopulate_native_stats(self):
        self.assertTrue(all(x["itemlevel_reachability_attested"] is False for x in self.catalog[1].values()))
        self.assertTrue(all(x["embellishment_applicability_to_item_attested"] is False for x in self.catalog[1].values()))

if __name__=="__main__":unittest.main()
