"""v055: effects delegated to SimC, no zero-static trinket rejection."""
import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runner'))
import pilot
import v046_static_item_cache as c
import v055_simc_item_selection as p

class ItemPassThrough(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref,_=pilot.source()
    def test_mindpiercer_trinket_without_static_is_allowed(self):
        s,summary=p.apply_selection(self.ref,[
            {"slot":"trinket1","item_id":250224,"ilevel":334,"options":{}}])
        self.assertIn("trinket1=selected_250224,id=250224,ilevel=334,source=local",s)
        self.assertTrue(summary["trinket_static_cache_required"] is False)
        self.assertTrue(summary["simc_effect_mechanics_owned_by_simc"])
        self.assertFalse(summary["product_code_integrated"])
        budget=p.static_budget_lookup(c.empty_cache(),"trinket1",250224,334,{})
        self.assertIsNone(budget["static_chmv_if_native"])
        self.assertEqual(budget["G_contribution"],0)
        self.assertEqual(budget["static_chmv_status"],"NOT_REPORTED_UNKNOWN_NOT_ZERO")
        self.assertTrue(budget["selection_allowed"])
    def test_explicit_permafrost_selection_is_supported_but_not_default(self):
        _,s=p.apply_selection(self.ref,[
           {"slot":"trinket2","item_id":250244,"ilevel":334,"options":{}}])
        self.assertTrue(s["selected"][0]["excluded_default_but_user_explicit_selection"])
    def test_two_user_chosen_trinkets_keep_other_options(self):
        altered,s=p.apply_selection(self.ref,[
          {"slot":"trinket1","item_id":250224,"ilevel":334,"options":{"bonus_id":"13846"}},
          {"slot":"trinket2","item_id":281215,"ilevel":331,"options":{}}])
        self.assertIn("trinket1=selected_250224,id=250224,ilevel=334,source=local,bonus_id=13846",altered)
        self.assertIn("trinket2=selected_281215,id=281215,ilevel=331,source=local",altered)
        self.assertEqual(sum(x.startswith("trinket1=") for x in altered.splitlines()),1)
        self.assertEqual(sum(x.startswith("trinket2=") for x in altered.splitlines()),1)
        self.assertEqual(sum(x.startswith("gear_") for x in altered.splitlines()),
                         sum(x.startswith("gear_") for x in self.ref.splitlines()))
    def test_two_embellishments_and_crafted_items(self):
        altered,r=p.apply_selection(self.ref,[
            {"slot":"back","item_id":239656,"ilevel":331,
             "options":{"crafted_stats":"49/36","embellishment":"arcanoweave_lining"}},
            {"slot":"wrists","item_id":239648,"ilevel":331,
             "options":{"crafted_stats":"32/49","embellishment":"arcanoweave_lining"}}])
        self.assertEqual(r["user_selected_embellishment_count"],2)
        self.assertIn("embellishment=arcanoweave_lining",altered)
        self.assertIn("crafted_stats=32/49",altered)
        self.assertIn("head=",altered)
        self.assertIn("trinket2=",altered)
    def test_unlisted_crafted_item_allowed_and_marked(self):
        altered,s=p.apply_selection(self.ref,[
            {"slot":"feet","item_id":999999,"ilevel":331,"options":{"crafted_stats":"49/36"}}])
        self.assertEqual(s["unlisted_crafted_ids_allowed"],[999999])
        self.assertIn("feet=selected_999999,id=999999,ilevel=331,source=local,crafted_stats=49/36",altered)
    def test_do_not_conflate_crafted_stats_token_and_rating(self):
        self.assertEqual(p.equipment_line("waist",239649,331,{"crafted_stats":"32/49"}),
                         "waist=selected_239649,id=239649,ilevel=331,source=local,crafted_stats=32/49")
    def test_more_than_two_effect_modifiers_refused(self):
        with self.assertRaisesRegex(c.CacheBlocked,"EMBELLISHMENT_LIMIT_EXCEEDED"):
            p.inspect_selection([
                {"slot":slot,"item_id":300+i,"ilevel":331,
                 "options":{"embellishment":"arcanoweave_lining"}}
                for i,slot in enumerate(("back","wrists","waist"))])
    def test_duplicate_slot_refused(self):
        x={"slot":"trinket1","item_id":250224,"ilevel":334,"options":{}}
        with self.assertRaisesRegex(c.CacheBlocked,"SLOT_DUPLICATE_OR_UNSUPPORTED"):
            p.inspect_selection([x,x])
    def test_catalyst_origin_id_survives_exact_item_serialization(self):
        item=p.equipment_line("chest",271459,334,
               {"bonus_id":"13848","redirected_base_stats":"268222"})
        self.assertIn(",id=271459,ilevel=334,source=local,",item)
        self.assertIn("redirected_base_stats=268222",item)
        self.assertIn("bonus_id=13848",item)
        for invalid in ("0","-1","abc","12/34","",str(10**10)):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(c.CacheBlocked,
                        "CATALYST_ORIGIN_ITEM_ID_INVALID|ITEM_OPTION_VALUE_INVALID"):
                    p.equipment_line("chest",271459,334,
                                     {"redirected_base_stats":invalid})

    def test_malformed_options_refused(self):
        with self.assertRaisesRegex(c.CacheBlocked,"ITEM_OPTION_VALUE_INVALID"):
            p.equipment_line("trinket1",250224,334,{"bonus_id":"11;delete_all"})
        with self.assertRaisesRegex(c.CacheBlocked,"ITEM_OPTIONS_NOT_SUPPORTED"):
            p.equipment_line("trinket1",250224,334,{"arbitrary":"1"})
    def test_trinket_not_crafted_with_this_contract(self):
        with self.assertRaisesRegex(c.CacheBlocked,"TRINKET_CRAFT_OPTION_NOT_THIS_CONTRACT"):
            p.inspect_selection([{"slot":"trinket1","item_id":250224,"ilevel":334,
                      "options":{"crafted_stats":"49/36"}}])
    def test_nontrinket_static_missing_not_inferred(self):
        with self.assertRaisesRegex(c.CacheBlocked,"NON_TRINKET_G_MISSING_NATIVE_STATIC"):
            p.static_budget_lookup(c.empty_cache(),"head",237832,331)
    def test_known_trinket_with_fixed_static_remains_outside_G(self):
        ca=c.empty_cache()
        ident={"season":c.SEASON,"item_id":250224,"ilevel":334,
               "slot":"trinket","options":{}}
        v={"identity":ident,"static":{
           "secondary":{"crit_rating":0,"haste_rating":88,"mastery_rating":0,
                        "versatility_rating":0}},
           "source_kind":"NATIVE_JSON2_RESOLVED_VARIANT"}
        ca["variants"][c.digest(ident)]=v
        d=p.static_budget_lookup(ca,"trinket1",250224,334)
        self.assertEqual(d["static_chmv_if_native"]["haste_rating"],88)
        self.assertEqual(d["G_contribution"],0)
    def test_catalog_larger_than_original_sampling(self):
        db=p.load_advisory_catalog()
        self.assertEqual(len(db),51)
        self.assertIn(240949,db)
        self.assertIn(237828,db)
        for x in (239652,244570,244580,237830,237831,237837,240950,245770):
            self.assertIn(x,db)
        self.assertNotIn(271440,db) # No proof this is a crafted recipe
        self.assertNotIn(271441,db)
    def test_selected_crafted_pieces_cannot_displace_reserved_four_set(self):
        with self.assertRaisesRegex(c.CacheBlocked,"CRAFTED_PIECE_REPLACES_RESERVED_TIER_OR_SPECIAL"):
            p.apply_selection(self.ref,[{"slot":"head","item_id":239652,"ilevel":331,
                         "options":{"crafted_stats":"49/36","embellishment":"arcanoweave_lining"}}],
                         reserved_tier_slots=("head","shoulders","chest","legs"))
    def test_extended_recipe_item_id_is_not_a_gear_budget_claim(self):
        changed,plan=p.apply_selection(self.ref,[{"slot":"waist","item_id":237830,
              "ilevel":331,"options":{"crafted_stats":"49/36","embellishment":"arcanoweave_lining"}}])
        self.assertIn("waist=selected_237830,id=237830,ilevel=331,source=local",changed)
        self.assertEqual(plan["unlisted_crafted_ids_allowed"],[])
        with self.assertRaisesRegex(c.CacheBlocked,"NON_TRINKET_G_MISSING_NATIVE_STATIC"):
            p.static_budget_lookup(c.empty_cache(),"waist",237830,331,{"crafted_stats":"49/36"})
    def test_no_native_proc_gate_claim(self):
        s=p.inspect_selection([{"slot":"trinket1","item_id":250224,
                                "ilevel":334,"options":{}}])
        self.assertTrue(s["effect_support_prior_screen_not_required"])
        self.assertEqual(s["status"],"SELECTION_INPUT_READY_NO_EFFECT_GATE")
        self.assertFalse(s["official_policy_promoted"])

if __name__=="__main__":unittest.main()
