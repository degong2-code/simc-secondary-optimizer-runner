"""P1 v584: real existing v191/v211/v213 parsers on synthetic extra gear.

No Wago HTTP, new SimC Native, effect reimplementation or user publication.
"""
from __future__ import annotations
import json
import copy
from pathlib import Path
import tempfile
import unittest

import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runner"))
import v191_unified_season_data_update as v191
import v584_supplemental_permanent_enchant_classification as v584
from tests.test_v239_v211_fresh_season_dynamic_classifier import (
    BUILD,REV,fixture_source,put_sources)


def fixture(root):
    _,data=fixture_source()
    old=data["permanent_enchant.inc"].splitlines()[1:]
    extras=[
        '{ 91003, 1, 4, 0x00000080, 0x0000001e, "synth_spellthread" },',
        '{ 91004, 2, 4, 0x00000080, 0x0000001e, "synth_spellthread" },',
    ]
    data["permanent_enchant.inc"]=(
        f"// Permanent item enchants, wow build {BUILD}\n"
        "static constexpr std::array<permanent_enchant_entry_t, 4> "
        "__permanent_enchant_data { {\n"
        +"\n".join(old+extras)+"\n} };\n")
    add=[
        '{ 91003, 0, 0, 0, 0, 0, 0, 0, 0, '
        '{ 5, 0, 0 }, { 10, 0, 0 }, { 36, 0, 0 }, '
        '{ 0.0000f, 0.0000f, 0.0000f }, 0, "Synthetic Legs" },',
        '{ 91004, 0, 0, 0, 0, 0, 0, 0, 0, '
        '{ 5, 0, 0 }, { 20, 0, 0 }, { 36, 0, 0 }, '
        '{ 0.0000f, 0.0000f, 0.0000f }, 0, "Synthetic Legs" },',
    ]
    data["spell_item_enchantment.inc"]+="\n".join(add)+"\n"
    manifest=put_sources(root,data)
    manifest_path=root/"manifest.json"
    manifest_path.write_text(json.dumps(manifest),encoding="utf8")
    simc_rows=[
        {"enchant_id":91003,"quality_rank":1,"item_class":4,
         "inventory_type_mask":0x80,"item_subclass_mask":0x1e,
         "simc_token":"synth_spellthread"},
        {"enchant_id":91004,"quality_rank":2,"item_class":4,
         "inventory_type_mask":0x80,"item_subclass_mask":0x1e,
         "simc_token":"synth_spellthread"}]
    sha=v191.parse_generated(
        "permanent_enchant",data["permanent_enchant.inc"].encode())["sha256"]
    relation={
        "status":"PERMANENT_ENCHANT_EXACT_WAGO_SIMC_SOURCE_ONLY",
        "game_build":BUILD,"source_only":True,
        "simc_generated_sha256":sha,
        "additional_dps_gear_highest_source_rank_candidate_ids":[91004],
        "additional_enchants_unadmitted":[
            {"enchant_id":r["enchant_id"],
             "scope":"DPS_EQUIPMENT_PERMANENT_CANDIDATE_UNADMITTED",
             "simc_source_rows":[r],
             "physical_items":[{"item_id":237001+idx,
                                "quality_rank_wago":13+idx}]}
            for idx,r in enumerate(simc_rows)]}
    return relation,manifest_path


class TestSupplementalV584(unittest.TestCase):
    def test_existing_source_classifiers_compare_highest_static_rank(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            relation,manifest=fixture(folder)
            result=v584.classify(relation=relation,source_dir=folder,
                                 manifest_path=manifest,
                                 game_build=BUILD,simc_revision=REV)
        self.assertEqual(result["status"],v584.COMPLETE,result)
        self.assertEqual(result["candidate_count"],1)
        self.assertEqual(result["slot_resolved_count"],1)
        self.assertEqual(result["weapon_hand_pending_count"],0)
        self.assertEqual(result["static_chmv_candidate_count"],1)
        self.assertEqual(result["quality_noninferior_source_count"],1)
        self.assertEqual(result["raw_static_component_nondecreasing_candidate_count"],1)
        component=result["rows"][0]["raw_rank_component_evidence"]
        self.assertTrue(component["source_same_component_types_and_ids"])
        self.assertTrue(component["source_raw_amount_and_coefficient_nondecreasing"])
        self.assertFalse(component["quality_noninferiority_runtime_verified"])
        self.assertFalse(component["ui_selectable"])
        row=result["rows"][0]
        self.assertEqual(row["enchant_id"],91004)
        self.assertEqual(row["physical_item_ids"],[237002])
        self.assertEqual(row["source_slot"]["slot_group"],"legs")
        self.assertEqual(row["effect_family"],"static_chmv_rating_haste_rating")
        self.assertFalse(row["ui_selectable"])
        self.assertEqual(row["static_E"],"NOT_MEASURED_IF_CHMV")
        self.assertEqual(row["static_E_source_status"],
                         "STATIC_CHMV_NUMERIC_MEASUREMENT_PENDING")
        self.assertFalse(result["source_quality_observations"][0][
            "policy_A_product_input_verified"])
        self.assertEqual(result["native_calls"],0)

    def test_original_v213_masks_armor_and_weapon_without_token_naming(self):
        armor={"item_class":4,"inventory_type_mask":0x80,
               "item_subclass_mask":0,"simc_token":"not_enchant_prefix"}
        weapon={**armor,"item_class":2,"inventory_type_mask":0,
                "item_subclass_mask":0x4000c}
        self.assertEqual(v584._slot(armor)["slot_group"],"legs")
        self.assertEqual(v584._slot(weapon)["status"],
                         "WEAPON_SUBCLASS_PENDING_EXACT_HAND_APPLICABILITY")
        self.assertEqual(v584._slot(weapon)["weapon_subclass_ids_from_source_mask"],
                         [2,3,18])
        self.assertEqual(v584._slot({**armor,"inventory_type_mask":1<<28})
                         ["status"],"ARMOR_MASK_EXACT_SLOT_UNRESOLVED")

    def test_missing_optional_pinned_source_is_not_base_blocker(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            relation,manifest=fixture(folder)
            result=v584.classify(relation=relation,source_dir=None,
                                 manifest_path=manifest,
                                 game_build=BUILD,simc_revision=REV)
        self.assertEqual(result["status"],v584.PENDING)
        self.assertFalse(result["ui_selectable"])
        self.assertEqual(result["native_calls"],0)

    def test_provenance_drift_never_promotes_item(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            relation,manifest=fixture(folder)
            relation["simc_generated_sha256"]="f"*64
            result=v584.classify(relation=relation,source_dir=folder,
                                 manifest_path=manifest,
                                 game_build=BUILD,simc_revision=REV)
        self.assertEqual(result["status"],v584.PENDING,result)
        self.assertIn("SHA_MISMATCH",result["reason"])

    def test_other_non_gear_sources_stay_outside_selected_gear_classifier(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            relation,manifest=fixture(folder)
            relation["additional_enchants_unadmitted"].append({
                "enchant_id":99993,
                "scope":"PROFESSION_TOOL_OUTSIDE_DPS_EQUIPMENT",
                "simc_source_rows":[],"physical_items":[]})
            result=v584.classify(relation=relation,source_dir=folder,
                                 manifest_path=manifest,
                                 game_build=BUILD,simc_revision=REV)
        self.assertEqual(result["candidate_count"],1,result)
        self.assertEqual(result["rows"][0]["enchant_id"],91004)

    def test_unknown_new_item_mod_is_recorded_not_guessed_or_promoted(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            relation,manifest_path=fixture(folder)
            db=folder/"spell_item_enchantment.inc"
            raw=db.read_bytes()
            changed=raw.replace(b"{ 36, 0, 0 }, { 0.0000f",
                                b"{ 999, 0, 0 }, { 0.0000f")
            self.assertNotEqual(raw,changed)
            db.write_bytes(changed)
            manifest=json.loads(manifest_path.read_text())
            manifest["files"]["spell_item_enchantment.inc"].update({
                "size_bytes":len(changed),
                "sha256":v584.effect.sha256(changed),
                "git_blob_sha1":v584.effect.git_blob_sha(changed)})
            manifest_path.write_text(json.dumps(manifest))
            result=v584.classify(relation=relation,source_dir=folder,
                                 manifest_path=manifest_path,
                                 game_build=BUILD,simc_revision=REV)
        self.assertEqual(result["status"],v584.COMPLETE,result)
        self.assertEqual(result["unknown_component_candidate_count"],1)
        self.assertEqual(result["static_chmv_candidate_count"],0)
        self.assertEqual(result["quality_noninferior_source_count"],0)
        self.assertEqual(result["rows"][0]["unknown_components"][0][
            "item_mod_or_spell_id"],999)
        self.assertFalse(result["rows"][0]["ui_selectable"])
        self.assertEqual(result["source_quality_observations"][0]["status"],
                         "UNKNOWN_STAT_COMPONENT_QUALITY_EFFECT_PENDING")

    def test_known_hybrid_primary_stat_is_nonchmv_without_E(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            relation,manifest_path=fixture(folder)
            db=folder/"spell_item_enchantment.inc"
            raw=db.read_bytes()
            changed=raw.replace(b"{ 36, 0, 0 }, { 0.0000f",
                                b"{ 72, 0, 0 }, { 0.0000f")
            self.assertNotEqual(raw,changed)
            db.write_bytes(changed)
            enums=folder/"data_enums.hh"
            parsed=enums.read_bytes()+b"\nITEM_MOD_STRENGTH_AGILITY = 72,\n"
            enums.write_bytes(parsed)
            manifest=json.loads(manifest_path.read_text())
            for name,contents in (("spell_item_enchantment.inc",changed),
                                  ("data_enums.hh",parsed)):
                manifest["files"][name].update({
                    "size_bytes":len(contents),
                    "sha256":v584.effect.sha256(contents),
                    "git_blob_sha1":v584.effect.git_blob_sha(contents)})
            manifest_path.write_text(json.dumps(manifest))
            result=v584.classify(relation=relation,source_dir=folder,
                                 manifest_path=manifest_path,
                                 game_build=BUILD,simc_revision=REV)
        self.assertEqual(result["status"],v584.COMPLETE,result)
        self.assertEqual(result["unknown_component_candidate_count"],0)
        self.assertEqual(result["static_chmv_candidate_count"],0)
        self.assertEqual(result["rows"][0]["effect_family"],
                         "static_nonchmv_item_mod")
        self.assertEqual(result["rows"][0]["static_E_source_status"],
                         "NO_STATIC_CHMV_COMPONENT_IN_SIMC_DBC")
        self.assertEqual(result["rows"][0]["static_components"][0]["item_mod"],
                         "strength_agility")
        self.assertFalse(result["rows"][0]["ui_selectable"])

    def test_pinned_resistance_type_is_not_chmv_or_unknown_effect(self):
        enum_string=(
            "ITEM_ENCHANTMENT_STAT=5,\n"
            "ITEM_ENCHANTMENT_EQUIP_SPELL=3,\n"
            "ITEM_ENCHANTMENT_RESISTANCE=4,\n"
            "ITEM_MOD_AGILITY=3,\nITEM_MOD_STRENGTH=4,\n"
            "ITEM_MOD_INTELLECT=5,\nITEM_MOD_STAMINA=7,\n"
            "ITEM_MOD_CRIT_RATING=32,\nITEM_MOD_HASTE_RATING=36,\n"
            "ITEM_MOD_VERSATILITY_RATING=40,\n"
            "ITEM_MOD_MASTERY_RATING=49,\nITEM_MOD_SPEED_RATING=61,\n"
            "ITEM_MOD_LEECH_RATING=62,\nITEM_MOD_AVOIDANCE_RATING=63,\n"
            "ITEM_MOD_STRENGTH_AGILITY_INTELLECT=71,\n")
        enums=v584.effect.parse_enums(enum_string)
        dbc={"dbc_name":"Synthetic Resistance Enchant",
             "ench_type":[4,0,0],"ench_amount":[0,0,0],
             "ench_prop":[0,0,0],"ench_coeff":[0.8028,0.0,0.0],
             "id_scaling":0}
        candidate={"enchant_id":91004,"token":"synth_spellthread",
                   "quality_rank":2,"item_class":4,
                   "inventory_type_mask":0x80,
                   "item_subclass_mask":0x1e}
        classified=v584.effect.classify_row(
            candidate,dbc,enums,{}, {},{},unknown_item_mods_pending=True)
        self.assertEqual(classified["unknown_components"],[])
        self.assertEqual(classified["static_components"][0]["category"],
                         "NON_CHMV_RESISTANCE")
        self.assertFalse(classified["static_chmv_rating_present_in_dbc"])

    def test_actual_weapon_subclass_labels_from_pinned_enum_without_id_whitelist(self):
        source=(
            "  ITEM_SUBCLASS_WEAPON_BOW = 2,\n"
            "  ITEM_SUBCLASS_WEAPON_GUN = 3,\n"
            "  ITEM_SUBCLASS_WEAPON_CROSSBOW = 18,\n"
            "  ITEM_SUBCLASS_WEAPON_WAND = 19,\n")
        result=v584.weapon_subclasses_from_pinned_source(0x4000c,source)
        self.assertEqual(result["source_item_subclass_ids"],[2,3,18])
        self.assertEqual(result["source_enum_names"],["BOW","GUN","CROSSBOW"])
        self.assertTrue(result["source_ranged_weapon_types_only"])
        self.assertFalse(result["hand_applicability_verified"])
        unknown=v584.weapon_subclasses_from_pinned_source(0x8000c,source)
        self.assertFalse(unknown["source_enum_all_ids_resolved"])
        self.assertFalse(unknown["source_ranged_weapon_types_only"])

    def test_source_scaled_static_coefficient_direction_is_evidence_only(self):
        dbc={
            91003:{"id_gem":0,"id_scaling":-7,
                "min_scaling_level":0,"max_scaling_level":80,
                "min_ilevel":120,"max_ilevel":0,"req_skill":0,
                "req_skill_value":0,"id_spell":12331,
                "ench_type":[5,5,0],"ench_prop":[5,7,0],
                "ench_amount":[0,0,0],"ench_coeff":[0.9515,2.0814,0.0]},
            91004:{"id_gem":0,"id_scaling":-7,
                "min_scaling_level":0,"max_scaling_level":80,
                "min_ilevel":120,"max_ilevel":0,"req_skill":0,
                "req_skill_value":0,"id_spell":12332,
                "ench_type":[5,5,0],"ench_prop":[5,7,0],
                "ench_amount":[0,0,0],"ench_coeff":[1.2191,3.4194,0.0]}}
        ordered=[{"enchant_id":91004,"quality_rank":2},
                 {"enchant_id":91003,"quality_rank":1}]
        enums={"ITEM_ENCHANTMENT_STAT":5,
               "ITEM_ENCHANTMENT_RESISTANCE":4}
        z=v584.effect.source_rank_component_comparison(
            ordered,dbc,91004,enums)
        self.assertEqual(z["status"],
                         "SOURCE_STATIC_COMPONENTS_RAW_NONDECREASING_UNADMITTED")
        self.assertTrue(z["source_same_scaling_and_use_conditions"])
        self.assertTrue(z["source_strictly_stronger_raw_component"])
        self.assertFalse(z["source_id_spell_identical"])
        self.assertFalse(z["same_effect_and_use_conditions_verified"])
        self.assertFalse(z["ui_selectable"])
        weaker=copy.deepcopy(dbc)
        weaker[91004]["ench_coeff"][0]=0.4
        fail=v584.effect.source_rank_component_comparison(
            ordered,weaker,91004,enums)
        self.assertEqual(fail["status"],
                         "SOURCE_SELECTED_RANK_RAW_COMPONENT_NOT_NONINFERIOR")
        self.assertFalse(fail["source_raw_amount_and_coefficient_nondecreasing"])

    def test_different_rank_driver_spell_never_claims_static_quality(self):
        common={"id_gem":0,"id_scaling":0,
                "min_scaling_level":0,"max_scaling_level":80,
                "min_ilevel":120,"max_ilevel":0,
                "req_skill":0,"req_skill_value":0,
                "ench_type":[3,0,0],"ench_amount":[0,0,0],
                "ench_coeff":[0.0,0.0,0.0]}
        dbc={
            81101:{**common,"id_spell":123,
                   "ench_prop":[456,0,0]},
            81102:{**common,"id_spell":124,
                   "ench_prop":[457,0,0]}}
        out=v584.effect.source_rank_component_comparison(
            [{"enchant_id":81102,"quality_rank":2},
             {"enchant_id":81101,"quality_rank":1}],
            dbc,81102,{"ITEM_ENCHANTMENT_STAT":5})
        self.assertEqual(out["status"],
                         "SOURCE_COMPONENT_KIND_OR_SPELL_DRIVER_NEEDS_REVIEW")
        self.assertFalse(out["source_all_components_known_static"])
        self.assertFalse(out["source_raw_amount_and_coefficient_nondecreasing"])


if __name__=="__main__":
    unittest.main()
