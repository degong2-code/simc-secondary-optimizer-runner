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
        for ids,reason in (((103,),"NOT_IN_SOURCE"),
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

    def test_invalid_ascii_token_remains_unadmitted_without_guessing(self):
        wrong=copy.deepcopy(self.doc)
        wrong["items"][0]["name"]="특별 음식"
        found,_=self.match(simc=wrong)
        self.assertIsNone(found["items"][0]["simc_input_token_candidate"])
        self.assertFalse(found["items"][0]["policy_A_eligible"])


if __name__=="__main__":
    unittest.main()
