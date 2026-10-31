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
            self.assertEqual(x["ui_selectable"],x["enchant_id"]==7967)
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

    def test_all_38_source_effects_are_classified_without_generalizing_native_or_ui(self):
        c=catalog.public_options()
        enc=c["enchant_candidates"]
        rows=enc["items"]
        self.assertEqual(enc["source_classified_count"],38)
        self.assertEqual(enc["effect_classification_status"],
            "PINNED_SIMC_DBC_SPELLTEXT_AND_HANDLER_CLASSIFIED_NOT_NATIVE_GENERALIZED")
        self.assertEqual(enc["source_classification_counts"],{
            "static_chmv_rating":8,"static_nonchmv_only_or_mixed":19,
            "spell_effects":15,"native_E_measured":2})
        self.assertEqual(sum(x["ui_selectable"] for x in rows),1)
        self.assertEqual({x["enchant_id"] for x in rows if x["ui_selectable"]},{7967})
        by_id={x["enchant_id"]:x for x in rows}
        # Lynx's Dexterity is source DBC avoidance+stamina, not agility.
        lynx=by_id[7963]["source_effect_classification"]
        self.assertEqual(lynx["static_components"],["avoidance_rating","stamina"])
        # A weapon mastery enchant is a dynamic SimC proc, not fixed E.
        arcane=by_id[8041]
        self.assertFalse(arcane["source_static_chmv_rating_present"])
        self.assertEqual(arcane["source_dynamic_chmv_proc_roles"],
                         ["TEMPORARY_MASTERY_RATING_PROC"])
        self.assertEqual(arcane["source_simc_custom_handlers"],
                         ["stat_weapon_enchant"])
        # Cradle's effect text is a healing-triggered target barrier.
        cradle=by_id[8007]["source_effect_classification"]
        self.assertEqual(cradle["spell_effect_roles"],["ABSORB_OR_DEFENSIVE_PROC"])
        # The two existing Native facts remain strictly scope-limited.
        eagle=by_id[7967]
        self.assertEqual(eagle["source_native_E_status"],
                         "MEASURED_ZERO_ONE_WINDOWS_PALADIN_334_PROFILE")
        haste=by_id[8025]
        self.assertEqual(haste["source_native_E_one_scope"]["haste_rating"],30)
        self.assertEqual(haste["source_native_E_status"],
                         "MEASURED_ONE_LINUX_FROST_334_PROFILE")
        self.assertFalse(haste["ui_selectable"])
        self.assertTrue(all(x["simc_static_rating_verified"] is False for x in rows))

    def test_source_classification_manifest_tamper_fails_closed(self):
        import json,tempfile
        source=families.read_source_classification()
        self.assertEqual(len(source),38)
        doc=json.loads(families.SOURCE_CLASSIFICATION_PATH.read_text("utf8"))
        doc["simc_commit"]="0"*40
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/"bad.json"
            p.write_text(json.dumps(doc),encoding="utf8")
            with self.assertRaisesRegex(ValueError,"PROVENANCE_INVALID"):
                families.read_source_classification(p)

    def test_distinct_crit_effectiveness_does_not_get_dropped(self):
        c=catalog.public_options()
        item=next(x for x in c["enchant_candidates"]["items"]
                  if x["token"]=="enchant_ring__eyes_of_the_eagle")
        self.assertEqual(item["preferred_if_same_effect_source"],
                         "DISTINCT_EFFECT_NO_DOMINANCE")
        self.assertFalse(item["superseded_by_stronger_same_effect"])
        self.assertTrue(item["ui_selectable"])

if __name__=="__main__":unittest.main()
