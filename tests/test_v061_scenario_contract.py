"""v061 P1: generalized scenario contract; no real-item proc gate."""
import copy,hashlib,json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v061_scenario_contract as s

def item(slot,id_,ilevel=334,options=None):
    return {"slot":slot,"item_id":id_,"ilevel":ilevel,"options":options or {}}

def mage():
    return {
      "schema":s.SCHEMA,
      "character":{"class":"mage","spec":"arcane","race":"dwarf",
          "talents":"C4DAAAAAAAAAAAAAAAAAAAAAAYGGLzYmFMzQzMzMAAAGAwMz0sssMDAgNAAAzMDbWmxMLzYMzMzMzMAADAAwAMzAmBADzMD",
          "role":"spell"},
      "source":{"kind":"simc_standard","profile_sha256":None},
      "target":{"mode":"derived_ilevel","ilevel":334,
                "manual_total":None,"manual_total_scope":None},
      "equipment":{
        "tier":[item("head",271564),item("shoulders",271562),
                item("chest",271567),item("legs",271563)],
        "special":[],
        "crafted":[item("back",239656,334,{"crafted_stats":"49/36",
                                            "embellishment":"arcanoweave_lining"}),
                   item("wrists",239648,334,{"crafted_stats":"32/40",
                                             "embellishment":"arcanoweave_lining"})],
        "trinkets":[item("trinket1",250224),item("trinket2",281215)]},
      "consumables":{
        "gem_budget_J":138,"flask_budget_F":165,
        "special_gem_id":240967,
        "flask":"flask_of_the_blood_knights_2","food":"royal_roast",
        "potion":None,"weapon_temporary":"thalassian_phoenix_oil_2",
        "weapon_temporary_fixed_rating":{
          "crit_rating":16,"haste_rating":16,
          "mastery_rating":0,"versatility_rating":0}},
      "combat":{
        "fight_style":"Patchwerk","targets":1,"duration_seconds":300,
        "vary_combat_length_pct":0.0,"raid_buffs":True,
        "bloodlust":"on_pull","external_buffs":[],"events":[]},
      "constraints":{
        "min_fraction":{k:0.0 for k in s.STATS},
        "max_fraction":{k:0.5 for k in s.STATS},
        "minimum_rating":{k:0 for k in s.STATS}},
      "runtime":{"scout_iterations":120,"confirm_iterations":320,
                 "max_native_calls":8,"threads":1,"resume":True,"seed":7}
      }

def manual():
    p=mage()
    p["target"]={"mode":"manual_total","ilevel":331,
      "manual_total":3000,"manual_total_scope":s.MANUAL_TOTAL_SCOPE}
    p["equipment"]["crafted"][0]["ilevel"]=331
    p["equipment"]["crafted"][1]["ilevel"]=331
    return p

class ScenarioContract(unittest.TestCase):
    def test_reference_mage_is_input_only_no_native_g_assumptions(self):
        out=s.normalize(mage())
        self.assertEqual(out["status"],"VALID_SCENARIO_INPUT_NO_SIMC_EFFECT_GATE")
        self.assertIsNone(out["budget"]["G"])
        self.assertIsNone(out["budget"]["T"])
        self.assertEqual(out["budget"]["T_status"],"WAIT_NATIVE_G")
        self.assertEqual(out["equipment_count"],8)
        self.assertEqual(out["embellishment_count"],2)
        self.assertEqual(out["budget"]["external_temporary_rating"]["crit_rating"],16)
        self.assertEqual(out["budget"]["external_oil_policy"],s.OIL_POLICY)
        self.assertFalse(out["special_effect_pre_admission_gate"])
    def test_manual_total_is_inclusive_not_G_plus_J_F_again(self):
        out=s.normalize(manual())
        self.assertEqual(out["budget"]["T"],3000)
        self.assertEqual(out["budget"]["J"],138)
        self.assertEqual(out["budget"]["F"],165)
        self.assertEqual(s.derive_T(2849,138,165),3152)
        self.assertEqual(out["budget"]["T_status"],
                         "MANUAL_USER_SUPPLIED_INCLUDES_J_F")
    def test_mindpiercer_requires_no_static_record(self):
        x=s.normalize(mage())
        self.assertEqual(x["scenario"]["equipment"]["trinkets"][0]["item_id"],250224)
        self.assertFalse(x["budget"]["native_static_stat_record_required_for_trinkets"])
        self.assertTrue(x["user_trinkets_included_in_simc"])
    def test_nonstandard_manual_crafted_id_is_accepted(self):
        d=mage()
        d["equipment"]["crafted"][1]["item_id"]=999991
        out=s.normalize(d)
        self.assertIn("id=999991", "\n".join(s.selected_lines(out)))
    def test_all_classes_roles_not_bound_to_mage(self):
        for cls,role in (("warrior","tank"),("paladin","heal"),
                         ("druid","spell"),("shaman","attack"),
                         ("evoker","spell"),("deathknight","tank")):
            d=manual()
            d["character"].update({"class":cls,"spec":"simulation_spec","role":role})
            self.assertEqual(s.normalize(d)["budget"]["T"],3000)
    def test_two_trinket_exactness(self):
        d=mage();d["equipment"]["trinkets"].pop()
        with self.assertRaisesRegex(s.ScenarioInvalid,"TWO_TRINKETS_REQUIRED"):
            s.normalize(d)
        d=mage();d["equipment"]["trinkets"][1]["slot"]="trinket1"
        with self.assertRaisesRegex(s.ScenarioInvalid,"TRINKET_SLOTS_NOT_EXACT"):
            s.normalize(d)
    def test_tier_slot_cannot_be_replaced_by_crafted_or_special(self):
        d=mage();d["equipment"]["crafted"][0]["slot"]="chest"
        with self.assertRaisesRegex(s.ScenarioInvalid,"GEAR_SLOT_COLLISION"):
            s.normalize(d)
        d=mage();d["equipment"]["special"]=[item("head",230000)]
        with self.assertRaisesRegex(s.ScenarioInvalid,"GEAR_SLOT_COLLISION"):
            s.normalize(d)
    def test_explicit_catalyst_special_tier_tag_is_valid_and_count_neutral(self):
        doc=mage()
        doc["equipment"]["tier"][0]["options"]={"redirected_base_stats":"268222"}
        doc["equipment"]["catalyst_special_tier_slots"]=["head"]
        actual=s.normalize(doc)
        self.assertEqual(actual["equipment_count"],8)
        self.assertEqual(actual["scenario"]["equipment"]
                         ["catalyst_special_tier_slots"],["head"])
        self.assertEqual(actual["fixed_four_tier_slots"],
                         ["chest","head","legs","shoulders"])

    def test_catalyst_special_tag_requires_real_tier_with_origin(self):
        for tag,options in [
          (["feet"],{"redirected_base_stats":"268222"}),
          (["head"],{}),
          (["head","head"],{"redirected_base_stats":"268222"}),
          (["head"],{"redirected_base_stats":"271564"})]:
            doc=mage()
            doc["equipment"]["tier"][0]["options"]=options
            doc["equipment"]["catalyst_special_tier_slots"]=tag
            with self.subTest(tag=tag,options=options):
                with self.assertRaisesRegex(s.ScenarioInvalid,
                            "CATALYST_SPECIAL_TIER_SLOT_TAGS_INVALID|"
                            "CATALYST_LOCK_MUST_REFERENCE_EXACT_TIER_ORIGIN"):
                    s.normalize(doc)

    def test_duplicate_item_id_in_separate_slots_is_simc_owned(self):
        d=mage();d["equipment"]["crafted"][1]["item_id"]=239656
        out=s.normalize(d)
        self.assertEqual(out["equipment_count"],8)
        # SimC decides unique-equipped and combat rules; no local ruleset.
    def test_max_2_embellishments(self):
        d=mage();d["equipment"]["crafted"].append(item("waist",239649,334,
            {"crafted_stats":"49/36","embellishment":"arcanoweave_lining"}))
        with self.assertRaisesRegex(s.ScenarioInvalid,"MORE_THAN_TWO_EMBELLISHMENTS"):
            s.normalize(d)
    def test_do_not_move_embellishment_to_special(self):
        d=mage();d["equipment"]["special"]=[item("waist",242222,334,
                {"embellishment":"arcanoweave_lining"})]
        with self.assertRaisesRegex(s.ScenarioInvalid,"EMBELLISHMENTS_USE_CRAFTED_GEAR"):
            s.normalize(d)
    def test_missing_gear_same_slot_not_autogenerated(self):
        z=s.normalize(mage())
        lines=s.selected_lines(z)
        self.assertEqual(len(lines),8)
        self.assertEqual(sum(x.startswith("trinket1=") for x in lines),1)
        self.assertEqual(sum(x.startswith("main_hand=") for x in lines),0)
    def test_user_profile_sha_is_required(self):
        d=mage();d["source"]["kind"]="user_supplied"
        with self.assertRaisesRegex(s.ScenarioInvalid,"PROFILE_SHA"):
            s.normalize(d)
        d["source"]["profile_sha256"]="a"*64
        self.assertEqual(s.normalize(d)["scenario"]["source"]["profile_sha256"],"a"*64)
    def test_official_3152_excludes_the_oil(self):
        z=s.normalize(mage())
        self.assertEqual(s.derive_T(2849,z["budget"]["J"],z["budget"]["F"]),3152)
        self.assertEqual(sum(z["budget"]["external_temporary_rating"].values()),32)
        self.assertEqual(s.derive_T(2849,138,165),3152)
    def test_fraction_infeasible_for_manual_total(self):
        d=manual();d["constraints"]["minimum_rating"]["crit_rating"]=1600
        with self.assertRaisesRegex(s.ScenarioInvalid,"UNFEASIBLE_MANUAL_TOTAL_BOUNDS"):
            s.normalize(d)
        d=manual();d["constraints"]["min_fraction"]["crit_rating"]=0.8
        with self.assertRaisesRegex(s.ScenarioInvalid,"UNFEASIBLE_FRACTION_BOUNDS"):
            s.normalize(d)
    def test_malformed_user_input_cannot_smuggle_simc_override(self):
        d=mage();d["equipment"]["trinkets"][0]["options"]={"bonus_id":"5,gear_crit_rating=123"}
        with self.assertRaises(Exception):s.normalize(d)
        d=mage();d["combat"]["events"]=["a\ngear_crit_rating=999"]
        with self.assertRaisesRegex(s.ScenarioInvalid,"EXTRA_COMBAT_TOKEN"):s.normalize(d)
    def test_source_no_hidden_no_proc_fidelity_gate(self):
        x=s.normalize(mage())
        self.assertEqual(x["effect_modeling_owner"],"SIMC")
        self.assertFalse(x["gear_combination_search"])
        self.assertFalse(x["product_v016_integrated"])
    def test_cache_keys_static_separated_from_dps(self):
        a=s.normalize(mage())
        val={"crit_rating":800,"haste_rating":1000,
             "mastery_rating":800,"versatility_rating":552}
        k=s.result_cache_key(a,"a"*64,"b"*64,val,120)
        self.assertEqual(k,s.result_cache_key(a,"a"*64,"b"*64,val,120))
        self.assertNotEqual(k,s.result_cache_key(a,"c"*64,"b"*64,val,120))
        self.assertNotEqual(k,s.result_cache_key(a,"a"*64,"b"*64,val,320))
        b=s.normalize(manual())
        self.assertNotEqual(k,s.result_cache_key(b,"a"*64,"b"*64,val,120))
    def test_implicit_target_mode_is_not_allowed(self):
        d=mage();d["target"]["manual_total"]=3152
        with self.assertRaisesRegex(s.ScenarioInvalid,"DERIVED_MODE_MUST_WAIT_FOR_NATIVE_G"):
            s.normalize(d)
    def test_scenario_digest_is_order_insensitive_to_object_keys(self):
        d=mage()
        k=s.normalize(d)["scenario_digest"]
        d2={key:d[key] for key in reversed(list(d))}
        self.assertEqual(k,s.normalize(d2)["scenario_digest"])
    def test_wrong_tier_count_does_not_pass(self):
        d=mage();d["equipment"]["tier"].pop()
        with self.assertRaisesRegex(s.ScenarioInvalid,"TIER_MUST_BE_FOUR"):s.normalize(d)
    def test_target_331_supported_without_releveling_334_items(self):
        d=manual()
        z=s.normalize(d)
        self.assertEqual(z["scenario"]["target"]["ilevel"],331)
        self.assertEqual(z["scenario"]["equipment"]["tier"][0]["ilevel"],334)
        # Current P1 must NOT silently assume user's 334 tier is already 331.
if __name__=="__main__":unittest.main()
