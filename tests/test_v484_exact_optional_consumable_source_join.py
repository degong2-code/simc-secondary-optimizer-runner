"""v484 exact food/potion source join; synthetic only, no new Native."""
from __future__ import annotations
import copy
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v217_stage_execution_engine as stages
import v484_exact_optional_consumable_source_join as subject

BUILD="12.1.5.70575"
REV="a"*40


class ExactConsumableSourceJoin(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root=pathlib.Path(temp.name)
        self.seed=self.root/"sealed-simc"
        self.seed.mkdir()
        self.original={
            "schema":"v190_same_build_consumable_item_candidates_v1",
            "status":"DB2_CONSUMABLE_CANDIDATES_PENDING_SIMC_DBC_JOIN",
            "automatic_ui_promotion":False,
            "source":{"wago_snapshot_build":BUILD,"simc_revision":REV},
            "items":[
                {"item_id":101,"kind":"food","item_class":0,
                 "item_subclass":5,"inventory_type":0,
                 "source":"SAME_BUILD_DB2_ITEM_AND_ITEMSPARSE",
                 "ui_selectable":False,"simc_token":"UNRESOLVED"},
                {"item_id":102,"kind":"potion","item_class":0,
                 "item_subclass":1,"inventory_type":0,
                 "source":"SAME_BUILD_DB2_ITEM_AND_ITEMSPARSE",
                 "ui_selectable":False,"simc_token":"UNRESOLVED"},
                {"item_id":103,"kind":"flask","item_class":0,
                 "item_subclass":3,"inventory_type":0,
                 "source":"SAME_BUILD_DB2_ITEM_AND_ITEMSPARSE",
                 "ui_selectable":False,"simc_token":"UNRESOLVED"}],
        }
        def write():
            for name,relative in subject.OUTPUTS.items():
                path=self.root/relative
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text(
                    json.dumps(self.original) if name=="candidate"
                    else "original stage source",encoding="utf8")
        self.stage=stages.execute_stage(
            root=self.root,stage_id=subject.STAGE_ID,
            stage_version=subject.STAGE_VERSION,
            inputs={"synthetic_source":"never_real_authority"},
            outputs=subject.OUTPUTS,execute=write)
        self.doc={
            "schema":"v230_simc_generated_exact_item_metadata_v1",
            "game_build":BUILD,"simc_revision":REV,
            "selection_mode":"EXACT_REQUESTED_IDS",
            "source_sha256":"c"*64,"source_receipt_sha256":"d"*64,
            "items":[
                {"item_id":101,"name":"Royal Roast",
                 "class_id":0,"subclass_id":5,"inventory_type":0,
                 "crafting_quality":0,
                 "source":"SIMC_GENERATED_ITEM_DATA_EXACT_ROW"},
                {"item_id":102,"name":"Potion of Recklessness",
                 "class_id":0,"subclass_id":1,"inventory_type":0,
                 "crafting_quality":2,
                 "source":"SIMC_GENERATED_ITEM_DATA_EXACT_ROW"}],
        }

    def match(self,ids=(101,102),stage=None,simc=None):
        with mock.patch.object(subject.item_metadata,"from_seed",
                               return_value=copy.deepcopy(
                                   self.doc if simc is None else simc)) as read:
            result=subject.match_selected_physical_items(
                stage_root=self.root,
                v190_stage=self.stage if stage is None else stage,
                simc_seed_dir=self.seed,game_build=BUILD,
                simc_revision=REV,selected_item_ids=ids)
        return result,read

    def test_exact_food_and_potion_are_unapproved_candidates(self):
        result,read=self.match()
        read.assert_called_once_with(
            directory=self.seed,item_ids=[101,102])
        self.assertEqual(result["candidate_count"],2)
        self.assertEqual(
            [row["simc_input_token_candidate"] for row in result["items"]],
            ["royal_roast","potion_of_recklessness_2"])
        self.assertEqual([row["crafting_quality_candidate"]
                          for row in result["items"]],[0,2])
        for row in result["items"]:
            self.assertTrue(row["exact_item_id_and_class_source_join"])
            self.assertTrue(row["source_only"])
            self.assertFalse(row["simc_token_native_verified"])
            self.assertFalse(row["same_effect_quality_group_verified"])
            self.assertFalse(row["chmv_budget_owner_verified"])
            self.assertFalse(row["ui_selectable"])
        self.assertFalse(result["user_selectable"])
        self.assertEqual((result["native_calls"],result["network_calls"],
                          result["source_files_written"]),(0,0,0))
        # Same sealed bytes, same result, no extra source fetch or writes.
        self.assertEqual(result,self.match()[0])

    def test_wrong_kind_missing_or_duplicate_id_rejects_before_simc_read(self):
        for ids,reason in (((103,),"SCOPE_MISMATCH"),
                           ((999,),"NOT_IN_SOURCE"),
                           ((101,101),"EXACT_ITEM_IDS_REQUIRED"),
                           ((),"EXACT_ITEM_IDS_REQUIRED")):
            with self.subTest(ids=ids),mock.patch.object(
                    subject.item_metadata,"from_seed",
                    side_effect=AssertionError("UNNEEDED_REPARSE")):
                with self.assertRaisesRegex(
                        subject.OptionalConsumableSourceBlocked,reason):
                    subject.match_selected_physical_items(
                        stage_root=self.root,v190_stage=self.stage,
                        simc_seed_dir=self.seed,game_build=BUILD,
                        simc_revision=REV,selected_item_ids=ids)

    def test_v217_output_tamper_and_stage_scope_reject(self):
        path=self.root/subject.OUTPUTS["candidate"]
        path.write_text("tampered",encoding="utf8")
        with self.assertRaisesRegex(
                subject.OptionalConsumableSourceBlocked,
                "V217_ORIGINAL_SOURCE_NOT_VERIFIED"):
            self.match()
        # A forged stage receipt SHA cannot be used as proof either.
        with self.assertRaisesRegex(
                subject.OptionalConsumableSourceBlocked,
                "ORIGINAL_STAGE_RECEIPT_DRIFT"):
            self.match(stage={**self.stage,"receipt_sha256":"f"*64})

    def test_wrong_simc_build_class_or_inventory_rejects(self):
        for field,value,reason in (
                ("game_build","12.1.5.70576","SIMC_ITEM_DATA_BUILD"),
                ("simc_revision","b"*40,"SIMC_ITEM_DATA_BUILD")):
            with self.subTest(field=field):
                wrong={**self.doc,field:value}
                with self.assertRaisesRegex(
                        subject.OptionalConsumableSourceBlocked,reason):
                    self.match(simc=wrong)
        for field,value in (("subclass_id",3),("inventory_type",20),
                            ("crafting_quality",-1)):
            with self.subTest(field=field):
                wrong=copy.deepcopy(self.doc)
                wrong["items"][0][field]=value
                with self.assertRaisesRegex(
                        subject.OptionalConsumableSourceBlocked,
                        "SAME_ID_ITEM_CLASS_OR_QUALITY_DRIFT"):
                    self.match(simc=wrong)

    def test_two_sources_agree_on_nonzero_equipment_slot_still_blocked(self):
        """Exact class/ID match never certifies an equipped item as food."""
        other=self.root/"wrong-inventory"
        other.mkdir()
        modified=copy.deepcopy(self.original)
        modified["items"][0]["inventory_type"]=20
        def write():
            for name,relative in subject.OUTPUTS.items():
                p=other/relative
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text(
                    json.dumps(modified) if name=="candidate"
                    else "original stage source",encoding="utf8")
        sealed=stages.execute_stage(
            root=other,stage_id=subject.STAGE_ID,
            stage_version=subject.STAGE_VERSION,
            inputs={"synthetic_source":"not-real-invalid-slot"},
            outputs=subject.OUTPUTS,execute=write)
        simc=copy.deepcopy(self.doc)
        simc["items"][0]["inventory_type"]=20
        with mock.patch.object(subject.item_metadata,"from_seed",
                               return_value=simc) as read:
            with self.assertRaisesRegex(
                    subject.OptionalConsumableSourceBlocked,
                    "SELECTED_PHYSICAL_ITEM_SCOPE_MISMATCH"):
                subject.match_selected_physical_items(
                    stage_root=other,v190_stage=sealed,
                    simc_seed_dir=self.seed,game_build=BUILD,
                    simc_revision=REV,selected_item_ids=[101])
            read.assert_not_called()

    def test_invalid_ascii_token_remains_unadmitted_without_guessing(self):
        wrong=copy.deepcopy(self.doc)
        wrong["items"][0]["name"]="특별 음식"
        found,_=self.match(simc=wrong)
        self.assertIsNone(found["items"][0]["simc_input_token_candidate"])
        self.assertFalse(found["items"][0]["policy_A_eligible"])




class SimcProfileDefaultExtraction(unittest.TestCase):
    def test_shared_observer_uses_supplied_level_and_one_process(self):
        import re
        import subprocess
        import v139_pure_target_profile_composer as representative
        season=copy.deepcopy(representative.catalog())
        season["character_level"]=89
        season["target_ilevel"]=330
        with tempfile.TemporaryDirectory() as td:
            binary=pathlib.Path(td)/"simc"
            binary.touch()
            def generate(argv,**kwargs):
                root=pathlib.Path(kwargs["cwd"])
                raw=(root/argv[1]).read_text(encoding="utf8")
                actors=re.findall(r"^spec=(\w+)\nlevel=89\n.*?^save=(defaults_\d+\.simc)$",
                                  raw,re.M|re.S)
                self.assertEqual(len(actors),26)
                self.assertIn("ilevel=330",raw)
                self.assertNotIn("\nfood=",raw)
                self.assertNotIn("\npotion=",raw)
                for spec,name in actors:
                    (root/name).write_text("spec="+spec+"\nlevel=89\n"
                        "food=synthetic_food\npotion=synthetic_potion\n",
                        encoding="utf8")
                return subprocess.CompletedProcess(argv,0,"Generating profiles","")
            receipt={}
            with mock.patch("subprocess.run",side_effect=generate) as run:
                observed=subject.extract_simc_profile_defaults(
                    binary=binary,season=season,receipt=receipt)
            run.assert_called_once()
            self.assertEqual(len(observed),26)
            self.assertEqual(receipt["profile_generation_processes"],1)
            self.assertEqual(receipt["dps_simulations"],0)
            self.assertEqual(receipt["character_level"],89)

    def test_shared_observer_rejects_incomplete_roster_before_process(self):
        with tempfile.TemporaryDirectory() as td:
            binary=pathlib.Path(td)/"simc"
            binary.touch()
            with mock.patch("subprocess.run") as run:
                with self.assertRaises(subject.OptionalConsumableSourceBlocked):
                    subject.extract_simc_profile_defaults(binary=binary,
                        season={"character_level":90,"target_ilevel":334,
                                "specializations":{}},receipt={})
            run.assert_not_called()

    def test_quality_scope_does_not_depend_on_default_lookup(self):
        with mock.patch.object(subject,"reviewed_apl_default_groups",
                               return_value={"food":{"future":"mage/fire"}}):
            self.assertFalse(subject._reviewed_quality_scope(BUILD,REV))
            self.assertTrue(subject._reviewed_quality_scope(
                "12.1.5.70961","9933ffb946fb55b1fa66657b848f519ac19006e1"))




class CurrentDefaultWeaponSource(unittest.TestCase):
    def sample(self):
        rows=[
            {"item_id":101,"name":"Two-handed sword","category":
             "plain_representative_candidate","inventory_type":17,
             "class_id":2,"subclass_id":8,"item_set_id":0,
             "allowed_class_mask":2,"source_kinds":["raid_journal"],
             "stat_modifier_codes":[4]},
            {"item_id":102,"name":"Wrong weapon","category":
             "plain_representative_candidate","inventory_type":17,
             "class_id":2,"subclass_id":8,"item_set_id":0,
             "allowed_class_mask":2,"source_kinds":["raid_journal"],
             "stat_modifier_codes":[5]},
            {"item_id":103,"name":"Trinket","category":"trinket",
             "inventory_type":12,"class_id":4,"subclass_id":0}]
        gear={"season_build":BUILD,"no_old_catalog_seed":True,"items":rows}
        metadata={"game_build":BUILD,"simc_revision":REV,
                  "source_receipt_sha256":"a"*64,"source_sha256":"b"*64,
                  "selection_mode":"EXACT_REQUESTED_IDS_ALLOW_MISSING",
                  "items":[dict(rows[0]),dict(rows[1])]}
        return gear,metadata

    def test_one_exact_parse_no_gear_or_native_for_all_specs(self):
        import v169_source_first_representative_stage as chooser
        gear,metadata=self.sample()
        with mock.patch.object(chooser.gear,"validate",return_value=gear), \
             mock.patch.object(subject.item_metadata,"from_seed",
                               return_value=metadata) as read:
            result=subject.current_source_profile_default_weapons(
                gear=gear,seed_directory="test",game_build=BUILD,
                simc_revision=REV)
        read.assert_called_once_with(directory="test",item_ids=[101,102],
                                     allow_missing=True)
        self.assertEqual(result["specializations"]["paladin/retribution"],
                         {"weapons":{"main_hand":101}})
        self.assertIn("mage/fire",result["missing_specializations"])
        self.assertEqual(len(result["specializations"])+
                         len(result["missing_specializations"]),26)
        self.assertEqual(result["native_calls"],0)

    def test_exact_metadata_disagreement_excludes_weapon(self):
        import v169_source_first_representative_stage as chooser
        gear,metadata=self.sample()
        metadata["items"][0]["subclass_id"]=18
        with mock.patch.object(chooser.gear,"validate",return_value=gear), \
             mock.patch.object(subject.item_metadata,"from_seed",
                               return_value=metadata):
            result=subject.current_source_profile_default_weapons(
                gear=gear,seed_directory="test",game_build=BUILD,
                simc_revision=REV)
        self.assertEqual(result["mismatched_item_ids"],[101])
        self.assertIn("paladin/retribution",result["missing_specializations"])

    def test_signed_db2_class_mask_preserves_simc_class_restrictions(self):
        import v169_source_first_representative_stage as chooser
        gear,metadata=self.sample()
        gear["items"][0]["allowed_class_mask"]=-1
        # DB2 all-class does not expand the SimC paladin-only mask.
        with mock.patch.object(chooser.gear,"validate",return_value=gear), \
             mock.patch.object(subject.item_metadata,"from_seed",
                               return_value=metadata):
            result=subject.current_source_profile_default_weapons(
                gear=gear,seed_directory="test",game_build=BUILD,
                simc_revision=REV)
        self.assertEqual(result["specializations"]["paladin/retribution"],
                         {"weapons":{"main_hand":101}})
        self.assertIn("warrior/arms",result["missing_specializations"])
        self.assertNotIn(101,result["mismatched_item_ids"])

    def test_signed_mask_other_bits_and_invalid_row_do_not_expand_pool(self):
        import v169_source_first_representative_stage as chooser
        gear,metadata=self.sample()
        # -3 has the paladin bit cleared; no intersection for 101.
        gear["items"][0]["allowed_class_mask"]=-3
        gear["items"][1]["allowed_class_mask"]=-((1<<31)+1)
        with mock.patch.object(chooser.gear,"validate",return_value=gear), \
             mock.patch.object(subject.item_metadata,"from_seed",
                               return_value=metadata):
            result=subject.current_source_profile_default_weapons(
                gear=gear,seed_directory="test",game_build=BUILD,
                simc_revision=REV)
        self.assertEqual(result["mismatched_item_ids"],[101,102])
        self.assertIn("paladin/retribution",result["missing_specializations"])

    def test_wrong_revision_does_not_authorize_weapon_pool(self):
        import v169_source_first_representative_stage as chooser
        gear,metadata=self.sample()
        metadata["simc_revision"]="f"*40
        with mock.patch.object(chooser.gear,"validate",return_value=gear), \
             mock.patch.object(subject.item_metadata,"from_seed",
                               return_value=metadata):
            with self.assertRaisesRegex(subject.OptionalConsumableSourceBlocked,
                                        "V787_CURRENT_WEAPON_SIMC_IDENTITY_DRIFT"):
                subject.current_source_profile_default_weapons(
                    gear=gear,seed_directory="test",game_build=BUILD,
                    simc_revision=REV)



class DirectQualitySource(unittest.TestCase):
    def fixture(self):
        from copy import deepcopy
        rows=[{"kind":"potion","physical_item_id":101,"simc_input_token":"test_1",
               "crafting_quality":1,"effect_identity":"simc:reviewed_apl_input:spell:1000",
               "use_condition_identity":"wago_on_use_0","name_enUS":"Test"},
              {"kind":"potion","physical_item_id":102,"simc_input_token":"test_2",
               "crafting_quality":2,"effect_identity":"simc:reviewed_apl_input:spell:1000",
               "use_condition_identity":"wago_on_use_0","name_enUS":"Test"}]
        metadata={"consumable_quality_physical_scopes":{"101":"a"*64,"102":"a"*64},
                  "items":[{"item_id":iid,"ilevel_unscaled":lvl,
                            "stat_modifier_codes":[],"item_set_id":0,
                            "intrinsic_socket_count_from_simc_source":0}
                           for iid,lvl in ((101,1),(102,2))]}
        def record(fields):
            return "{ "+", ".join(map(str,fields))+" },"
        spell=["0"]*56
        spell[0]='"Test"'
        spell[1]="1000"
        flags=["0"]*17
        flags[11]="4"
        spell[39]="{ "+", ".join(flags)+" }"
        spell[40]="{ 0, 0, 0, 0 }"
        spell[43]=spell[44]="{ 0, 0 }"
        spell[52]="1"
        effect=["0"]*31
        effect[:8]=["2000","1000","0","6","189","-7","0","2"]
        effect[16]="256"
        effect[18]="{ 0, 0, 0, 0 }"
        effect[28]="1"
        sources={
            "item_effect.inc":f"// Item effects, wow build {BUILD}\n"
                +"static constexpr std::array<item_effect_t, 2> __item_effect_data { {\n"
                +record([1,1000,101,0,0,1,300000,300000])+"\n"
                +record([2,1000,102,0,0,1,300000,300000])+"\n} };\n",
            "sc_spell_data.inc":f"// 1 spells, wow build level {BUILD}\n"
                +"static spell_data_t __spell_data[1] = {\n"+record(spell)+"\n};\n"
                +f"// 1 effects, wow build level {BUILD}\n"
                +"static spelleffect_data_t __spelleffect_data[1] = {\n"
                +record(effect)+"\n};\n",
            "rand_prop_points.inc":f"// Random property points for item levels 1-2, wow build {BUILD}\n"
                +"static constexpr std::array<random_prop_data_t, 2> __rand_prop_points_data { {\n"
                +"\n".join(record([lvl,10,10,*["{ "+", ".join([str(v)]*5)+" }"]*3])
                            for lvl,v in ((1,10),(2,20)))+"\n} };\n",
            "sc_scale_data.inc":f"// Combat rating multipliers for item level 1 - 2, wow build {BUILD}\n"
                +"static constexpr double __combat_ratings_mult_by_ilvl[][2] = {\n"
                +"\n".join("  // "+name+" Multiplier\n  {\n    1.5, 1.5,\n  },"
                            for name in ("Armor","Weapon","Trinket","Jewelry"))+"\n};\n"}
        return rows,metadata,{k:v.encode("utf8") for k,v in sources.items()}

    def extract(self,rows,meta,source):
        groups=subject.pending_direct_quality_families(rows,meta,None)
        return subject.direct_quality_source_families(game_build=BUILD,
            simc_revision=REV,rows=rows,metadata=meta,families=groups,
            source_bytes=source)

    def test_direct_static_quality_uses_source_budget_and_rating_multiplier(self):
        rows,meta,source=self.fixture()
        evidence=self.extract(rows,meta,source)
        self.assertEqual(len(evidence),1)
        self.assertEqual(evidence[0]["signed_components"],
                         {"101":{"spell_effect:2000:189:256":30.0},
                          "102":{"spell_effect:2000:189:256":60.0}})
        self.assertEqual(subject.signed_quality_family_winners(
            rows,evidence[0]["signed_components"]),[rows[1]])
        self.assertEqual(subject.pending_direct_quality_families(
            rows,meta,{"families":evidence}),[])

    def test_different_item_use_cooldown_or_scope_stays_pending(self):
        rows,meta,source=self.fixture()
        source["item_effect.inc"]=source["item_effect.inc"].replace(
            b"102, 0, 0, 1, 300000, 300000",b"102, 0, 0, 1, 300000, 200000")
        self.assertEqual(self.extract(rows,meta,source),[])
        meta["consumable_quality_physical_scopes"]["102"]="b"*64
        self.assertEqual(subject.pending_direct_quality_families(rows,meta,None),[])

    def test_no_source_reads_for_already_proven_family(self):
        rows,meta,source=self.fixture()
        known={"families":self.extract(rows,meta,source)}
        with mock.patch("v229_simc_only_source_seed.discover_generated_tree") as fetch:
            result,status=subject.collect_direct_quality_source(
                stage_root="unused",game_build=BUILD,simc_revision=REV,
                rows=rows,metadata=meta,known=known)
        self.assertEqual(result,known)
        self.assertEqual(status["network_calls"],0)
        fetch.assert_not_called()


if __name__=="__main__":
    unittest.main()
