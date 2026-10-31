"""v211 source-derived enchant classification; offline and zero Native."""
from __future__ import annotations
import json,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v211_enchant_source_effect_classification as v

ENUMS="""
ITEM_ENCHANTMENT_EQUIP_SPELL = 3,
ITEM_ENCHANTMENT_STAT = 5,
ITEM_MOD_AGILITY = 3,
ITEM_MOD_STRENGTH = 4,
ITEM_MOD_INTELLECT = 5,
ITEM_MOD_STAMINA = 7,
ITEM_MOD_CRIT_RATING = 32,
ITEM_MOD_HASTE_RATING = 36,
ITEM_MOD_VERSATILITY_RATING = 40,
ITEM_MOD_MASTERY_RATING = 49,
ITEM_MOD_SPEED_RATING = 61,
ITEM_MOD_LEECH_RATING = 62,
ITEM_MOD_AVOIDANCE_RATING = 63,
ITEM_MOD_STRENGTH_AGILITY_INTELLECT = 71,
"""
class V211SourceClassification(unittest.TestCase):
    def test_pinned_source_blob_hash_and_size_are_checked(self):
        raw=b"abc"
        self.assertEqual(v.git_blob_sha(raw),"f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f")
        self.assertEqual(v.sha256(raw),
                         "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
    def test_item_mod_and_enchant_type_enum_values_are_explicit(self):
        parsed=v.parse_enums(ENUMS)
        self.assertEqual(parsed["ITEM_ENCHANTMENT_STAT"],5)
        self.assertEqual(parsed["ITEM_ENCHANTMENT_EQUIP_SPELL"],3)
        self.assertEqual(parsed["ITEM_MOD_HASTE_RATING"],36)
        with self.assertRaisesRegex(v.SourceBlocked,"ENUM_DRIFT"):
            v.parse_enums(ENUMS.replace("ITEM_MOD_HASTE_RATING = 36",
                                        "ITEM_MOD_HASTE_RATING = 37"))
    def test_exact_dbc_rows_distinguish_static_rating_from_spell(self):
        rows="""{ 8025, 0, -7, 0, 80, 120, 0, 0, 0, { 5, 0, 0 }, { 0, 0, 0 }, { 36, 0, 0 }, { 0.8623f, 0.0000f, 0.0000f }, 0, "Enchant Ring - Silvermoon" },
{ 7967, 0, -7, 0, 80, 120, 0, 0, 0, { 3, 0, 0 }, { 0, 0, 0 }, { 1236701, 0, 0 }, { 0.0000f, 0.0000f, 0.0000f }, 0, "Enchant Ring - Eyes" },
"""
        parsed=v.parse_dbc_rows(rows,{8025,7967})
        self.assertEqual(parsed[8025]["ench_prop"],[36,0,0])
        self.assertEqual(parsed[7967]["ench_prop"],[1236701,0,0])
        self.assertEqual(parsed[8025]["ench_coeff"][0],0.8623)
    def test_spelltext_reference_resolves_and_handler_registration_is_pinned(self):
        texts={1236708:"$@spelldesc445322",
               445322:"Permanently enchants chestpiece to increase Intellect and mana pool."}
        self.assertEqual(v.resolve_spelltext(1236708,texts),texts[445322])
        duplicates='''{ 9, "Human-readable effect description", 0, 0 },
{ 9, "$rolemult=helper expression", 0, 0 },'''
        parsed=v.parse_spelltexts(duplicates)
        self.assertEqual(parsed[9],"Human-readable effect description")
        src="""
register_special_effect( { 1236741, 1236742 }, enchants::stat_weapon_enchant );
register_special_effect( { 1236733, 1236734 }, enchants::strength_of_halazzi );
register_special_effect( 1236701, enchants::eyes_of_the_eagle, false, true );
"""
        handlers=v.parse_custom_handlers(src)
        self.assertEqual(handlers[1236742],"stat_weapon_enchant")
        self.assertEqual(handlers[1236734],"strength_of_halazzi")
        self.assertEqual(handlers[1236701],"eyes_of_the_eagle")
    def test_static_CHMV_is_not_confused_with_dynamic_weapon_proc(self):
        enums=v.parse_enums(ENUMS)
        spelltexts={1236721:"Permanently enchants a weapon to sometimes grant Mastery for 10 sec."}
        handlers={1236721:"stat_weapon_enchant"}
        ring={"enchant_id":8025,"token":"enchant_ring__silvermoons_alacrity",
              "quality_rank":2,"item_class":4,"inventory_type_mask":2048,
              "item_subclass_mask":31}
        weapon={"enchant_id":8041,"token":"enchant_weapon__arcane_mastery",
                "quality_rank":2,"item_class":2,"inventory_type_mask":0,
                "item_subclass_mask":966655}
        ring_dbc={"id":8025,"id_gem":0,"id_scaling":-7,
          "ench_type":[5,0,0],"ench_amount":[0,0,0],
          "ench_prop":[36,0,0],"ench_coeff":[0.8623,0.0,0.0],
          "dbc_name":"Silvermoon Alacrity"}
        weapon_dbc={"id":8041,"id_gem":0,"id_scaling":0,
          "ench_type":[3,0,0],"ench_amount":[0,0,0],
          "ench_prop":[1236721,0,0],"ench_coeff":[0.0,0.0,0.0],
          "dbc_name":"Arcane Mastery"}
        evidence={8025:{"status":"MEASURED_ONE_LINUX_FROST_334_PROFILE",
                         "static_E":{"crit_rating":0,"haste_rating":30,
                                     "mastery_rating":0,"versatility_rating":0},
                         "ui_selectable":False},
                  7967:{"status":"MEASURED_ZERO_ONE_WINDOWS_PALADIN_334_PROFILE",
                         "static_E":{"crit_rating":0,"haste_rating":0,
                                     "mastery_rating":0,"versatility_rating":0},
                         "ui_selectable":True}}
        r=v.classify_row(ring,ring_dbc,enums,spelltexts,handlers,evidence)
        w=v.classify_row(weapon,weapon_dbc,enums,spelltexts,handlers,evidence)
        self.assertTrue(r["static_chmv_rating_present_in_dbc"])
        self.assertEqual(r["static_chmv_stats"],["haste_rating"])
        self.assertFalse(w["static_chmv_rating_present_in_dbc"])
        self.assertTrue(w["dynamic_chmv_proc_present_in_spell_text"])
        self.assertEqual(w["dynamic_chmv_proc_roles"],["TEMPORARY_MASTERY_RATING_PROC"])
        self.assertFalse(w["native_E_evidence"]["ui_selectable"])
        self.assertFalse(w["simc_effect_reimplemented"])
    def test_candidate_manifest_keeps_38_ids_and_existing_selection_boundary(self):
        data=json.loads((ROOT/"data/current_season_simc_enchant_candidates.json").read_text())
        self.assertEqual(len(data["rows"]),38)
        self.assertEqual(data["simc_commit"],v.SIMC_COMMIT)
        eagle=v.verify_evidence(ROOT/"data/v206_eagle_7967_windows_E0_proof.json","7967")
        haste=v.verify_evidence(ROOT/"data/v202_verified_enchant_8025_source.json","8025")
        self.assertTrue(eagle["ui_selectable"])
        self.assertFalse(haste["ui_selectable"])
        self.assertEqual(haste["static_E"]["haste_rating"],30)
if __name__=="__main__":unittest.main()
