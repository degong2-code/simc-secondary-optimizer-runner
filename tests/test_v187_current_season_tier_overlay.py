"""v187: selected items + current-season 4 of 5 tier slot reconciliation.

Offline-only real season DB and fake selected item overlays. Not SimC Native,
not an independent proc/catalyst eligibility certification.
"""
from __future__ import annotations
import copy,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v101_common_representative_equipment as common
import v139_pure_target_profile_composer as pure
import v169_source_first_representative_stage as season
import v106_user_session_controller as sessions

class CurrentSeasonTierReconciliation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.map=season.load_tier()["classes"]["mage"]["pieces"]
    def setup_rows(self):
        user=sessions.user_scenario(sessions.standard_controls(("mage","frost")))
        scope=season.season_scope()
        _,_,rows,groups,*_=pure.v098_inputs(
            user["character"],user["trinkets"],target_ilevel=334,
            combat=user["combat"],season_override=scope)
        return user,rows,groups
    def apply(self,user,rows,groups):
        return common.apply_user_equipment(
            ("mage","frost"),rows,groups,user,334,
            lambda v,code:self.fail(code) if not v else None,
            tier_override=self.map,
            fifth_override=("chest",self.map["chest"],159257),
            flexible_current_tier=True)
    def assert_four(self,rows,groups):
        tier={slot for slot in common.TIER_FIVE if groups.get(slot)=="tier"}
        self.assertEqual(len(tier),4)
        self.assertTrue(all(rows[s]["item_id"]==self.map[s] for s in tier))
        self.assertEqual(len(set(x["item_id"] for x in rows.values())),
                         len(rows))

    def test_unselected_baseline_four_and_both_crafted_non_tier(self):
        u,rows,groups=self.setup_rows()
        u["embellishments"]=[
            {"slot":"back","item_id":239656,
             "options":{"crafted_stats":"32/36","embellishment":"arcanoweave_lining"}},
            {"slot":"feet","item_id":239654,
             "options":{"crafted_stats":"32/36","embellishment":"arcanoweave_lining"}}]
        # These two user-visible slots are outside five tier positions.
        self.apply(u,rows,groups)
        self.assert_four(rows,groups)
        self.assertEqual(set(s for s in common.TIER_FIVE if groups.get(s)=="tier"),
                         {"head","shoulders","hands","legs"})

    def test_one_crafted_head_restores_exact_fifth_chest(self):
        u,rows,groups=self.setup_rows()
        diamond=rows["head"]["options"].get("gem_id")
        u["embellishments"]=[{"slot":"head","item_id":239652,
          "options":{"crafted_stats":"32/36","embellishment":"arcanoweave_lining"}}]
        restored,catalyst=self.apply(u,rows,groups)
        self.assertEqual(restored,["chest"])
        self.assertEqual(catalyst,[])
        self.assertEqual(groups["head"],"crafted")
        self.assertEqual(groups["chest"],"tier")
        self.assertEqual(rows["head"]["item_id"],239652)
        self.assertEqual(rows["head"]["options"]["gem_id"],diamond)
        self.assert_four(rows,groups)

    def test_two_crafted_inside_five_are_explicitly_impossible(self):
        for slots in (("head","shoulders"),("head","chest"),
                      ("hands","legs")):
            with self.subTest(slots=slots):
                u,rows,groups=self.setup_rows()
                source={"head":239652,"shoulders":239650,"chest":239655,
                        "hands":239653,"legs":239651}
                u["embellishments"]=[{"slot":slot,"item_id":source[slot],
                    "options":{"crafted_stats":"32/36",
                               "embellishment":"arcanoweave_lining"}}
                                  for slot in slots]
                with self.assertRaisesRegex(AssertionError,
                        "FOUR_TIER_IMPOSSIBLE_USER_OCCUPIES_TOO_MANY_SLOTS"):
                    self.apply(u,rows,groups)

    def test_selected_catalyst_fifth_demotes_one_internal_tier(self):
        u,rows,groups=self.setup_rows()
        u["special_items"]=[{"slot":"chest","item_id":self.map["chest"],
                             "options":{"redirected_base_stats":"159257"}}]
        restored,catalyst=self.apply(u,rows,groups)
        self.assertEqual(restored,[])
        self.assertEqual(groups["chest"],"tier")
        self.assertEqual(rows["chest"]["item_id"],self.map["chest"])
        self.assertEqual(catalyst,[{"slot":"chest",
                  "tier_item_id":self.map["chest"],"source_item_id":159257}])
        self.assertNotIn("legs",groups)
        self.assertIn("legs",rows)
        self.assertNotEqual(rows["legs"]["item_id"],self.map["legs"])
        self.assert_four(rows,groups)
        equipment,fillers=common.physical_gear_groups(rows,groups,catalyst)
        self.assertEqual(len(equipment["tier"]),4)
        self.assertEqual(equipment["catalyst_special_tier_slots"],["chest"])
        self.assertEqual(len([x for x in fillers if x["slot"]=="legs"]),1)

    def test_catalyst_head_and_crafted_chest_still_four(self):
        u,rows,groups=self.setup_rows()
        u["special_items"]=[{"slot":"head","item_id":self.map["head"],
                             "options":{"redirected_base_stats":"159236"}}]
        u["embellishments"]=[{"slot":"chest","item_id":239655,
          "options":{"crafted_stats":"32/36","embellishment":"arcanoweave_lining"}}]
        restored,catalyst=self.apply(u,rows,groups)
        self.assertEqual(restored,[])
        self.assertEqual(catalyst[0]["slot"],"head")
        self.assertEqual(groups["chest"],"crafted")
        self.assert_four(rows,groups)

    def test_wrong_class_tier_catalyst_id_rejected(self):
        u,rows,groups=self.setup_rows()
        u["special_items"]=[{"slot":"head","item_id":271555,
                             "options":{"redirected_base_stats":"159236"}}]
        with self.assertRaisesRegex(AssertionError,
                             "CATALYST_CLASS_TIER_ID_AND_ORIGIN_REQUIRED"):
            self.apply(u,rows,groups)

    def test_only_real_season_special_role_can_overlay_tier(self):
        u,rows,groups=self.setup_rows()
        # 159236 is plain cloth head, NOT user-selectable special effect.
        u["special_items"]=[{"slot":"head","item_id":159236,"options":{}}]
        with self.assertRaisesRegex(AssertionError,
                  "CURRENT_SEASON_SELECTED_ITEM_NOT_IN_APPROVED_ROLE:head"):
            self.apply(u,rows,groups)

    def test_special_item_wrong_slot_and_wrong_primary_rejected(self):
        u,rows,groups=self.setup_rows()
        # Current-season special cloak 159288 must not be slotted as head.
        u["special_items"]=[{"slot":"head","item_id":159288,"options":{}}]
        with self.assertRaisesRegex(AssertionError,
                  "CURRENT_SEASON_SELECTED_ITEM_WRONG_PHYSICAL_SLOT:head"):
            self.apply(u,rows,groups)
        u,rows,groups=self.setup_rows()
        # Agility dagger 271093 is not a mage intellect weapon.
        u["special_items"]=[{"slot":"main_hand","item_id":271093,"options":{}}]
        with self.assertRaisesRegex(AssertionError,
                  "CURRENT_SEASON_SPECIAL_WEAPON_WRONG_PRIMARY:main_hand"):
            self.apply(u,rows,groups)

    def test_selected_crafted_wrong_family_and_slot_rejected(self):
        u,rows,groups=self.setup_rows()
        u["embellishments"]=[{"slot":"head","item_id":237832,
           "options":{"crafted_stats":"32/36",
                      "embellishment":"arcanoweave_lining"}}]
        # 237832 is plate head; mage requires cloth.
        with self.assertRaisesRegex(AssertionError,
                  "CURRENT_SEASON_SELECTED_ITEM_WRONG_ARMOR_FAMILY:head"):
            self.apply(u,rows,groups)
        u,rows,groups=self.setup_rows()
        u["embellishments"]=[{"slot":"legs","item_id":239652,
           "options":{"crafted_stats":"32/36",
                      "embellishment":"arcanoweave_lining"}}]
        with self.assertRaisesRegex(AssertionError,
                  "CURRENT_SEASON_SELECTED_ITEM_WRONG_PHYSICAL_SLOT:legs"):
            self.apply(u,rows,groups)

if __name__=="__main__":unittest.main()
