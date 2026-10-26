"""v101 common class-armor / source-backed weapon / 4-of-5-tier tests.

No real SimC native execution, downloaded season DB or new proc mechanics.
"""
import pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v101_common_representative_equipment as core

class RepresentativeCatalog(unittest.TestCase):
    @staticmethod
    def need(ok,why):
        if not ok:raise ValueError(why)

    def test_13_classes_partition_exactly_across_four_armor_families(self):
        expected={"cloth":3,"leather":4,"mail":3,"plate":3}
        self.assertEqual({k:len(v) for k,v in core.ARMOR_CLASSES.items()},
                         expected)
        self.assertEqual(len(core.CLASS_ARMOR),13)
        self.assertEqual({c for values in core.ARMOR_CLASSES.values()
                          for c in values},set(core.CLASS_ARMOR))
        self.assertEqual(core.CLASS_ARMOR["warrior"],"plate")
        self.assertEqual(core.CLASS_ARMOR["paladin"],"plate")
        self.assertEqual(core.CLASS_ARMOR["mage"],"cloth")
        self.assertEqual(core.CLASS_ARMOR["hunter"],"mail")
        # No unverified tier item IDs generated for other classes.
        self.assertEqual(set(core.CLASS_TIER_ITEMS),
                         {"warrior","paladin","mage","hunter"})

    def test_weapon_topologies_separate_from_class_identity(self):
        self.assertEqual(len(core.WEAPON_FORMS),7)
        self.assertEqual(len(core.ARCHETYPES),4)
        self.assertEqual(set(core.WEAPON_FORMS["dual_two_hand"]),
                         {"main_hand","off_hand"})
        self.assertEqual(core.WEAPON_FORMS["ranged"],("main_hand",))
        self.assertEqual(core.WEAPON_FORMS["single_two_hand"],("main_hand",))
        self.assertIn("one_hand_shield",core.WEAPON_FORMS)
        self.assertIn("dual_one_hand",core.WEAPON_FORMS)

    def test_four_source_bound_builders_share_exact_class_tier_and_weapon_contract(self):
        for key in core.ARCHETYPES:
            with self.subTest(key=key),tempfile.TemporaryDirectory() as td:
                base,cfg,rows,groups,form,F=core.source_backed_gear(
                    key,pathlib.Path(td),334,self.need)
                self.assertEqual(cfg["character"]["class"],key[0])
                self.assertEqual(cfg["character"]["spec"],key[1])
                self.assertEqual({s for s in rows
                                  if s in ("main_hand","off_hand")},
                                 set(core.WEAPON_FORMS[form]))
                self.assertEqual({s:rows[s]["item_id"] for s,g in groups.items()
                                  if g=="tier"},
                                 {s:id_ for s,id_ in
                                  core.CLASS_TIER_ITEMS[key[0]].items()
                                  if s!=core.FIFTH_TIER[key][0]})
                self.assertEqual(len(rows),16 if key[1] in ("fury","frost") else 15)
                self.assertIn("actions=",base)
                self.assertEqual(sum(F.values()),165)
                self.assertTrue(all(r["ilevel"]==334 for r in rows.values()))

    def test_target_level_is_internal_gear_relevel_not_user_current_gear(self):
        for key in core.ARCHETYPES:
            with self.subTest(key=key),tempfile.TemporaryDirectory() as td:
                _,cfg,rows,groups,_,_=core.source_backed_gear(
                    key,pathlib.Path(td),321,self.need)
                self.assertTrue(all(r["ilevel"]==321 for r in rows.values()))
                self.assertEqual(sum(g=="tier" for g in groups.values()),4)

    def test_four_set_allocation_is_source_anchored_and_no_separate_gear_row(self):
        key=("mage","frost")
        with tempfile.TemporaryDirectory() as td:
            _,cfg,rows,groups,_,_=core.source_backed_gear(
                key,pathlib.Path(td),334,self.need)
            before=len(rows)
            user={"trinkets":[{"slot":slot,"item_id":250224+i,
                               "options":{}} for i,slot in
                              enumerate(("trinket1","trinket2"))],
                  "special_items":[],
                  "embellishments":[{"slot":"shoulders","item_id":239650,
                                    "options":{"crafted_stats":"49/36",
                                               "embellishment":"test_effect"}}]}
            added,catalyst=core.apply_user_equipment(
                key,rows,groups,user,334,self.need)
            equip,fill=core.physical_gear_groups(rows,groups,catalyst)
            self.assertEqual(added,["head"])
            self.assertEqual(catalyst,[])
            self.assertEqual(len(equip["tier"]),4)
            self.assertEqual(len(rows),before)
            self.assertEqual(rows["head"]["item_id"],271564)
            self.assertEqual(len(equip["crafted"]),3)
            self.assertEqual(sum(len(equip[k]) for k in
                                 ("tier","special","crafted","trinkets"))+len(fill),
                             before)

    def test_unsupported_source_only_fails_before_any_archetype_inference(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,
                                        "REPRESENTATIVE_ARCHETYPE_NOT_READY"):
                core.source_backed_gear(("shaman","elemental"),
                    pathlib.Path(td),334,self.need)

if __name__=="__main__":unittest.main()
