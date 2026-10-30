"""v197: exact same-effect group preference is orthogonal to source rank."""
from __future__ import annotations
import pathlib,sys,unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v196_current_season_user_catalog as catalog
import v197_enchant_effect_families as families
import v197_verified_effect_budget as budget

class SourceRingEffectFamilies(unittest.TestCase):
    def test_source_nine_rings_four_stronger_pairs_one_distinct_crit_effect(self):
        c=catalog.public_options()
        rows=c["enchant_candidates"]["items"]
        rings=[x for x in rows if x["kind"]=="ring"]
        self.assertEqual(len(rows),38)
        self.assertEqual(len(rings),9)
        self.assertEqual(c["enchant_candidates"]["same_effect_stronger_ring_enchants"],4)
        self.assertEqual(sum(x["superseded_by_stronger_same_effect"] for x in rings),4)
        self.assertEqual({x["effect_family"] for x in rings},
                         {"crit_rating","haste_rating","mastery_rating",
                          "versatility_rating","crit_effectiveness"})
        self.assertEqual({x["token"] for x in rings
                         if x["preferred_if_same_effect_source"]==
                           "STRONGER_VARIANT_REPORTED"},
                         {"enchant_ring__natures_fury",
                          "enchant_ring__silvermoons_alacrity",
                          "enchant_ring__silvermoons_tenacity",
                          "enchant_ring__zuljins_mastery"})
        for x in rings:
            self.assertFalse(x["ui_selectable"])
            self.assertFalse(x["simc_static_rating_verified"])
            self.assertTrue(x["display_name"].startswith("Enchant"))
            self.assertIn("rating",x["effect_description"]
                          if x["effect_family"]!="crit_effectiveness" else "rating")
        self.assertEqual(c["budget_effect_contract"]["schema"],budget.SCHEMA)
        self.assertTrue(c["budget_effect_contract"]["requires_exact_companion_native_receipt"])

    def test_unknown_ring_season_source_token_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"CURRENT_SEASON_RING_EFFECT_FAMILY_UNEXPECTED"):
            families.decorate([{"token":"enchant_ring__unknown_effect"}])
        with self.assertRaisesRegex(ValueError,"RING_SOURCE_EFFECT_FAMILIES_INCOMPLETE"):
            families.decorate([{"token":"enchant_ring__silvermoons_alacrity"}])
        with self.assertRaisesRegex(ValueError,"ENCHANT_TOKEN_DUPLICATE"):
            families.decorate([
                {"token":"enchant_ring__silvermoons_alacrity"},
                {"token":"enchant_ring__silvermoons_alacrity"}])

    def test_distinct_crit_effectiveness_does_not_get_dropped(self):
        c=catalog.public_options()
        item=next(x for x in c["enchant_candidates"]["items"]
                  if x["token"]=="enchant_ring__eyes_of_the_eagle")
        self.assertEqual(item["preferred_if_same_effect_source"],
                         "DISTINCT_EFFECT_NO_DOMINANCE")
        self.assertFalse(item["superseded_by_stronger_same_effect"])
        self.assertFalse(item["ui_selectable"])

if __name__=="__main__":unittest.main()
