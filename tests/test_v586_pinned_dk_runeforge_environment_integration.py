"""v586: Real pinned 70783 SimC-only DK rune source → existing user weapon path.

No Wago, season membership gate, item catalog, independent effect validation,
static secondary rating E assay, simulation, or new rune implementation.
"""
from __future__ import annotations
from pathlib import Path
import copy
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v055_simc_item_selection as equipment
import v212_environment_manifest as environment
import v294_dk_runeforge_selection as rune
import v295_season_runeforge_source as source
import v106_user_session_controller as sessions
import v098_target_user_scenario_bootstrap as bootstrap

RAW=(ROOT/"tests/fixtures/p1_v586_pinned_simc_dk_runeforge_enum_70783.txt").read_bytes()
REV="de11f57df75dda668bae6ac7043a43b98831fa96"
BUILD="12.1.5.70783"


def require(ok,code):
    if not ok:
        raise ValueError(code)


def weapons():
    return {
        "main_hand":{"slot":"main_hand","item_id":268209,
                     "ilevel":334,"options":{}},
        "off_hand":{"slot":"off_hand","item_id":268202,
                    "ilevel":334,"options":{}}}


class RealPinnedDKRunePath(unittest.TestCase):
    def test_original_simc_seven_options_come_from_current_revision(self):
        installed=source.compile_source(RAW,game_build=BUILD,simc_revision=REV)
        self.assertTrue(source.verify(installed,game_build=BUILD,simc_revision=REV))
        self.assertEqual(installed["source_path"],
            "engine/class_modules/sc_death_knight.cpp")
        self.assertEqual(installed["class_scope"],"deathknight")
        self.assertTrue(installed["simc_owns_rune_effects"])
        self.assertEqual(installed["count"],7)
        self.assertEqual({x["enchant_id"] for x in installed["items"]},
                         {3368,3370,3847,6241,6242,6244,6245})
        self.assertEqual(installed["native_calls"],0)
        self.assertFalse(installed["source_profile_gear_copied"])

    def test_existing_installed_source_and_weapon_serializer_only(self):
        doc=source.compile_source(RAW,game_build=BUILD,simc_revision=REV)
        installed={**doc,"source_stage_receipt_sha256":"a"*64}
        checked=environment._project_season_dk_runes(
            installed,game_build=BUILD,simc_revision=REV)
        self.assertEqual(checked,installed)
        dynamic_ids={x["enchant_id"] for x in checked["items"]}
        for eid in sorted(dynamic_ids):
            with self.subTest(enchant_id=eid):
                rows=weapons()
                before=copy.deepcopy(rows)
                chosen=rune.apply(rows=rows,selection={"main_hand":eid},
                    class_name="deathknight",weapon_form="single_two_hand",
                    need=require,admitted_ids=dynamic_ids)
                self.assertEqual(chosen,{"main_hand":eid})
                self.assertEqual(rows["main_hand"]["item_id"],
                                 before["main_hand"]["item_id"])
                self.assertEqual(rows["off_hand"],before["off_hand"])
                self.assertEqual(rows["main_hand"]["ilevel"],334)
                self.assertEqual(rows["main_hand"]["options"],{
                    "enchant_id":str(eid)})
                self.assertIn("enchant_id="+str(eid),
                    equipment.equipment_line(**rows["main_hand"]))
                # Only a SimC weapon enchant option has changed; no user
                # input budget/B/T, oil O, gemstone, or E calculation occurs.
                self.assertEqual(set(rows["main_hand"]["options"]),
                                 {"enchant_id"})

    def test_dual_wield_and_other_permanent_enchant_conflicts(self):
        dynamic={x["enchant_id"] for x in
                 source.compile_source(
                     RAW,game_build=BUILD,simc_revision=REV)["items"]}
        rows=weapons()
        result=rune.apply(rows=rows,selection={"main_hand":3368,
            "off_hand":3370},class_name="deathknight",
            weapon_form="dual_one_hand",need=require,admitted_ids=dynamic)
        self.assertEqual(result,{"main_hand":3368,"off_hand":3370})
        self.assertIn("enchant_id=3370",
                      equipment.equipment_line(**rows["off_hand"]))
        for class_name,form,selection,reason in (
            ("warrior","dual_one_hand",{"main_hand":3368},"DK_RUNEFORGE_CLASS_ONLY"),
            ("deathknight","single_two_hand",{"off_hand":3370},
             "DK_RUNEFORGE_OFFHAND_REQUIRES_DUAL_WEAPON"),
            ("deathknight","dual_one_hand",{"main_hand":999999},
             "DK_RUNEFORGE_ID_UNSUPPORTED"),
        ):
            with self.subTest(reason=reason),self.assertRaisesRegex(
                    ValueError,reason):
                rune.apply(rows=weapons(),selection=selection,
                           class_name=class_name,weapon_form=form,
                           need=require,admitted_ids=dynamic)
        rows=weapons()
        rows["main_hand"]["options"]["enchant_id"]="7999"
        with self.assertRaisesRegex(ValueError,"DK_RUNEFORGE_OTHER_ENCHANT_CONFLICT"):
            rune.apply(rows=rows,selection={"main_hand":3368},
                       class_name="deathknight",weapon_form="dual_one_hand",
                       need=require,admitted_ids=dynamic)

    def test_new_simc_enum_not_blocked_by_old_historical_id_list(self):
        future=RAW.replace(b"RUNEFORGE_ID_APOCALYPSE         = 6245",
                           b"RUNEFORGE_ID_APOCALYPSE         = 999245")
        self.assertNotEqual(future,RAW)
        doc=source.compile_source(
            future,game_build="12.2.0.71000",simc_revision=REV)
        admitted={x["enchant_id"] for x in doc["items"]}
        self.assertIn(999245,admitted)
        self.assertNotIn(999245,rune.RUNE_IDS)
        rows=weapons()
        rune.apply(rows=rows,selection={"main_hand":999245},
                   class_name="deathknight",weapon_form="dual_two_hand",
                   need=require,admitted_ids=admitted)
        self.assertEqual(rows["main_hand"]["options"]["enchant_id"],"999245")
        # New build list is SimC-only; no Wago item ID/source assumption.
        self.assertNotIn("physical_item_id",doc["items"][0])


    def test_fresh_user_rune_requires_installed_simc_not_legacy_fallback(self):
        controls=sessions.standard_controls(("deathknight","frost"))
        controls["oil_hands"]=[]
        controls["runeforge_by_hand"]={"main_hand":3368}
        user=sessions.user_scenario(controls)
        self.assertIn("runeforge_by_hand",user)
        with self.assertRaisesRegex(
                bootstrap.UserScenarioBlocked,
                "FRESH_DK_RUNEFORGE_SOURCE_NOT_INSTALLED"):
            bootstrap.build(
                user,ROOT/"tests"/"not_created",ROOT/"tests"/"no_binary",
                REV,current_season_product=True)


if __name__=="__main__":
    unittest.main()
