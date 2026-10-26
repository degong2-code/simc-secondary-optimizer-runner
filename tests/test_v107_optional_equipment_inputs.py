"""v107 advanced optional user equipment → existing v098 exact static L contract.

All tests are offline with explicitly synthetic cache records; never claim
a manufactured static item is an actual observed Native SimC variant.
"""
import copy,json,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
sys.path.insert(0,str(ROOT/"tests"))
import v106_user_session_controller as ux
import v098_target_user_scenario_bootstrap as boot
import v061_scenario_contract as contract
import v062_static_budget_bridge as static_budget
from test_v062_static_budget_bridge import record as synthetic_native_record

def special_form():
    return [{"slot":"head","item_id":"271483",
             "bonus_id":"13848","redirected_base_stats":"268231"}]

def crafted_form():
    return [{"slot":"shoulders","item_id":"244580",
             "crafted_stats":"49/36","embellishment":"arcanoweave_lining",
             "bonus_id":""}]

class AdvancedEquipmentUserJourney(unittest.TestCase):
    def fake_env(self):
        td=tempfile.TemporaryDirectory();self.addCleanup(td.cleanup)
        root=pathlib.Path(td.name)
        binary=root/"not_simc";binary.write_bytes(b"OFFLINE_NO_NATIVE")
        return root,binary

    def test_empty_and_partial_form_fail_closed_no_native(self):
        fields=ux.selected_rows_from_form(
          [{"slot":"","item_id":"","bonus_id":"","redirected_base_stats":""}],
          [{"slot":"","item_id":"","crafted_stats":"",
            "embellishment":"","bonus_id":""}])
        self.assertEqual(fields,{"special_items":[],"embellishments":[]})
        with self.assertRaisesRegex(ux.SessionBlocked,
                                    "ADVANCED_FORM_SLOT_AND_ITEM_REQUIRED"):
            ux.selected_rows_from_form(
              [{"slot":"head","item_id":"","bonus_id":"",
                "redirected_base_stats":""}],[])
        with self.assertRaisesRegex(ux.SessionBlocked,"ADVANCED_FORM_MAX_TWO"):
            ux.selected_rows_from_form(special_form()*3,[])

    def test_selected_catalyst_and_embellishment_wired_to_v098_not_new_gear_search(self):
        fields=ux.selected_rows_from_form(special_form(),crafted_form())
        controls=ux.standard_controls(("shaman","elemental"))
        u=ux.user_scenario({**controls,**fields})
        self.assertEqual(len(u["special_items"]),1)
        self.assertEqual(len(u["embellishments"]),1)
        self.assertEqual(u["special_items"][0]["options"],
                         {"bonus_id":"13848",
                          "redirected_base_stats":"268231"})
        self.assertEqual(u["embellishments"][0]["options"],
                         {"crafted_stats":"49/36",
                          "embellishment":"arcanoweave_lining"})
        root,binary=self.fake_env()
        with self.assertRaisesRegex(ux.SessionBlocked,
                                    "SPECIAL_EQUIPMENT_REQUIRES_EXACT_STATIC_CACHE"):
            ux.store_session(u,root,binary,"7bc10711b5")
        cache=boot.cache_mod.empty_cache()
        row={"slot":"head","item_id":271483,"ilevel":334,
             "options":{"bonus_id":"13848",
                        "redirected_base_stats":"268231"}}
        fixed={"crit_rating":0,"haste_rating":175,
               "mastery_rating":0,"versatility_rating":0}
        synthetic_native_record(cache,row,fixed)
        cp=root/"exact_synthetic_test_only.json"
        boot.cache_mod.write_atomic(cp,cache)
        folder=ux.store_session(u,root/"sessions",binary,"7bc10711b5",cp)
        plan=boot.build(u,folder/"generated",binary,"7bc10711b5",
                        static_cache_path=cp)
        self.assertEqual(plan["plan"]["base_B"],3150)
        self.assertEqual(plan["plan"]["final_T"],3182)
        self.assertEqual(plan["restored_tier_slots"],[])
        self.assertEqual(plan["effective_four_tier_slots"],
                         ["chest","hands","head","legs"])
        self.assertEqual(plan["catalyst_origin_items"],[
            {"slot":"head","tier_item_id":271483,"source_item_id":268231}])
        scenario=json.loads((folder/"generated"/"scenario.json").read_text())
        fill=json.loads((folder/"generated"/"fillers.json").read_text())
        stats=static_budget.compile_static_budget(
            contract.normalize(scenario),fill,cache)
        self.assertEqual(stats["locked_L_when_all_specials_observed"],fixed)
        self.assertEqual(stats["missing_special_fixed_static"],[])
        profile=(folder/"generated"/"profile.simc").read_text()
        self.assertEqual(sum(x.startswith("head=") for x in
                             profile.splitlines()),1)
        self.assertIn("redirected_base_stats=268231",profile)
        self.assertIn("crafted_stats=49/36",profile)
        self.assertIn("embellishment=arcanoweave_lining",profile)
        self.assertNotIn("simc_dps",ux.canonical(u))
        self.assertFalse((folder/"generated"/"simc_results").exists())

    def test_same_user_and_binary_but_cache_bytes_changed_split_session(self):
        root,binary=self.fake_env()
        controls=ux.standard_controls(("shaman","elemental"))
        fields=ux.selected_rows_from_form(special_form(),[])
        user=ux.user_scenario({**controls,**fields})
        p=root/"cache.json";p.write_text('{"schema":"1"}')
        a=ux.store_session(user,root/"sessions",binary,"7bc10711b5",p)
        p.write_text('{"schema":"2"}')
        b=ux.store_session(user,root/"sessions",binary,"7bc10711b5",p)
        self.assertNotEqual(a,b)

    def test_crafted_piece_changes_user_session_without_static_L(self):
        root,binary=self.fake_env()
        standard=ux.standard_controls(("paladin","retribution"))
        original=ux.user_scenario(standard)
        item={"slot":"waist","item_id":"244580",
              "crafted_stats":"36/49","embellishment":"arcanoweave_lining",
              "bonus_id":""}
        crafted=ux.selected_rows_from_form([],[item])
        selected=ux.user_scenario({**standard,**crafted})
        self.assertEqual(selected["embellishments"][0]["options"],
                         {"crafted_stats":"36/49",
                          "embellishment":"arcanoweave_lining"})
        self.assertNotEqual(ux.session_path(original,root,binary,"7bc10711b5")[0],
                            ux.session_path(selected,root,binary,"7bc10711b5")[0])
        self.assertEqual(ux.store_session(selected,root,binary,
                                         "7bc10711b5").name,
                         ux.session_path(selected,root,binary,"7bc10711b5")[0].name)

    def test_conflict_crafted_and_special_same_slot_does_not_get_silent_override(self):
        c=ux.standard_controls(("shaman","elemental"))
        same=ux.selected_rows_from_form(
            special_form(),[{
                "slot":"head","item_id":"244580",
                "crafted_stats":"49/36","embellishment":"arcanoweave_lining",
                "bonus_id":""}])
        with self.assertRaisesRegex(ux.SessionBlocked,
                                    "SELECTED_SPECIAL_AND_CRAFTED_SLOT_CONFLICT"):
            ux.user_scenario({**c,**same})

    def test_catalyst_invalid_option_and_unsupported_item_shaped_inputs_block(self):
        c=ux.standard_controls(("paladin","retribution"))
        bad=copy.deepcopy(c)
        bad["special_items"]=[{"slot":"head","item_id":271465,
                                "options":{"crafted_stats":"49/36"}}]
        with self.assertRaisesRegex(ux.SessionBlocked,"SPECIAL_CANNOT_BE_CRAFTED"):
            ux.user_scenario(bad)
        bad=copy.deepcopy(c)
        bad["embellishments"]=[{"slot":"waist","item_id":244580,
                                "options":{"crafted_stats":"49/36"}}]
        with self.assertRaisesRegex(ux.SessionBlocked,"CRAFTED_NEEDS_EMBELLISHMENT"):
            ux.user_scenario(bad)
        bad=copy.deepcopy(c)
        bad["special_items"]=[{"slot":"trinket1","item_id":268231,"options":{}}]
        with self.assertRaisesRegex(ux.SessionBlocked,"NONTRINKET_SLOT"):
            ux.user_scenario(bad)

if __name__=="__main__":unittest.main()
