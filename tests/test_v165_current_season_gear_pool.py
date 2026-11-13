"""v165: single small catalog, effect-presence status, not an effect engine."""
import csv
import json
from pathlib import Path
import tempfile
import unittest
from runner import v165_current_season_gear_pool as gear

def fixture():
    wago={"schema":"v163_zero_seed_db2_join_v1",
          "source_provider":"WAGO_TOOLS_PINNED_DB2_WCL_LIVE",
          "build":"12.1.5.70575","db2_expansion_id":11,"db2_display_season_id":37,
          "items":[
            {"item_id":1001,"name":"Boss ordinary","slot":5,"acquisition_sources":[
              {"source":"raid_journal","season_evidence":"UNKNOWN_UNSCOPED_JOURNAL",
               "world_state_expression_id":0,"display_season_id":0,
               "journal_encounter_id":11,"journal_instance_id":1}]},
            {"item_id":1002,"name":"Special boss sword","slot":13,"acquisition_sources":[
              {"source":"raid_journal","season_evidence":"UNKNOWN_UNSCOPED_JOURNAL",
               "world_state_expression_id":0,"display_season_id":0,
               "journal_encounter_id":11,"journal_instance_id":1}]},
            {"item_id":1003,"name":"New craft","slot":6,"acquisition_sources":[
              {"source":"selectable_stat_craft","classification":"PROVISIONAL_SIMC_BATCH_REVIEW"}]},
            {"item_id":1004,"name":"Previous expansion uncertain M+","slot":12,
             "acquisition_sources":[{"source":"mplus_journal",
               "season_evidence":"UNKNOWN_WORLD_STATE_EXPRESSION",
               "world_state_expression_id":52105}]}
          ]}
    local={"schema":"v162_localbots_delve_source_v1",
          "source_provider":"Localbots / balovich-matje/localbots",
          "db2_build":"12.1.5.70575","db2_expansion_id":11,
          "items":[{"item_id":1005,"name":"Delve Trinket","inventory_type":12,
                    "resolution":"LOCALBOTS_EXPLICIT_ID_DB2_VERIFIED"}]}
    return wago,local

class Roles(unittest.TestCase):
    def writecsv(self,path,header,rows):
        with path.open("w",encoding="utf8",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=header)
            writer.writeheader();writer.writerows(rows)

    def make(self,root,with_effects=True):
        sparse=root/"ItemSparse.csv"
        self.writecsv(sparse,["ID","Display_lang","InventoryType","ExpansionID",
                    "ItemSet","OverallQualityID"],[
             dict(ID=i,Display_lang="Item "+str(i),InventoryType=slot,ExpansionID=ex,
                  ItemSet=0,OverallQualityID=4)
             for i,slot,ex in ((1001,5,11),(1002,13,11),(1003,6,11),(1004,12,7),(1005,12,11))])
        fx=root/"ItemEffect.csv"
        self.writecsv(fx,["ID","ItemID","ItemEffectID"],[
              dict(ID=1,ItemID=1002,ItemEffectID=12345)])
        return sparse,fx if with_effects else None

    def test_roles_and_current_selection(self):
        with tempfile.TemporaryDirectory() as d:
            sparse,effect=self.make(Path(d))
            pool=gear.compile_pool(*fixture(),sparse,effect)
        by_id={x["item_id"]:x for x in pool["items"]}
        self.assertEqual(pool["item_count"],5)
        self.assertEqual(by_id[1001]["category"],"plain_representative_candidate")
        self.assertEqual(by_id[1002]["category"],"special_effect_gear_candidate")
        self.assertEqual(by_id[1003]["category"],"selectable_stat_craft")
        self.assertEqual(by_id[1004]["season_selection"],"CONDITIONAL_SEASON_NOT_ESTABLISHED")
        self.assertFalse(by_id[1004]["user_selectable_candidate"])
        self.assertEqual(by_id[1005]["category"],"trinket")
        self.assertTrue(by_id[1005]["user_selectable_candidate"])
        self.assertEqual(pool["consumable_budget_reference"]["ordinary_gem"]["total_J"],138)
        self.assertEqual(pool["consumable_budget_reference"]["flasks"]["total_F"],165)
        self.assertFalse(pool["fully_implemented_special_item_list_certified"])

    def test_a7_raid_world_state_and_other_seasons_are_never_current(self):
        import copy
        with tempfile.TemporaryDirectory() as d:
            sparse,effect=self.make(Path(d))
            w,l=fixture()
            raid=w["items"][0]["acquisition_sources"][0]
            self.assertTrue(gear._journal_origin_current(raid,37,raid=True))
            variants=[
                ("positive_world_state",{"world_state_expression_id":441,
                    "season_evidence":"UNKNOWN_WORLD_STATE_EXPRESSION",
                    "display_season_id":37}),
                ("other_display_season",{"world_state_expression_id":0,
                    "season_evidence":"UNKNOWN_OTHER_DISPLAY_SEASON",
                    "display_season_id":34}),
                ("missing_wse",{"world_state_expression_id":None}),
                ("wrong_journal_origin",{"journal_encounter_id":0}),
                ("unscoped_mplus_only",{"source":"mplus_journal",
                    "season_evidence":"UNKNOWN_UNSCOPED_JOURNAL"})
            ]
            for name,edits in variants:
                with self.subTest(name=name):
                    alternate=copy.deepcopy(w)
                    origin=alternate["items"][0]["acquisition_sources"][0]
                    origin.update(edits)
                    self.assertFalse(gear._journal_origin_current(
                        origin,37,raid=origin["source"]=="raid_journal"))
                    pool=gear.compile_pool(
                        alternate,l,sparse,effect,budget_source=None)
                    item=next(x for x in pool["items"]
                              if x["item_id"]==1001)
                    self.assertEqual(item["season_selection"],
                        "CONDITIONAL_SEASON_NOT_ESTABLISHED")
                    self.assertFalse(item["user_selectable_candidate"])
                    # A different, demonstrably unconditional current-season
                    # acquisition source may independently admit this ID.
                    if name=="positive_world_state":
                        alternate["items"][0]["acquisition_sources"].append({
                            "source":"mplus_journal",
                            "season_evidence":"DB2_DISPLAY_SEASON_MATCH",
                            "display_season_id":37,"world_state_expression_id":0,
                            "journal_encounter_id":23,"journal_instance_id":2})
                        linked=gear.compile_pool(
                            alternate,l,sparse,effect,budget_source=None)
                        chosen=next(x for x in linked["items"]
                                    if x["item_id"]==1001)
                        self.assertEqual(chosen["season_selection"],
                                         "CURRENT_CANDIDATE")
                        self.assertTrue(chosen["user_selectable_candidate"])
            self.assertTrue(gear._journal_origin_current({
                "source":"raid_journal","season_evidence":"DB2_DISPLAY_SEASON_MATCH",
                "display_season_id":37,"world_state_expression_id":0,
                "journal_encounter_id":11,"journal_instance_id":1
            },37,raid=True))
            self.assertFalse(gear._journal_origin_current(raid,42,raid=True)
                             and raid["display_season_id"]!=0)

    def test_no_effect_table_does_not_assert_plain(self):
        with tempfile.TemporaryDirectory() as d:
            sparse,_=self.make(Path(d))
            pool=gear.compile_pool(*fixture(),sparse)
        self.assertEqual(pool["status"],"EFFECT_TABLE_PENDING")
        self.assertEqual(pool["items"][0]["category"],"effect_classification_pending")
        self.assertFalse(pool["items"][0]["user_selectable_candidate"])

    def test_new_season_counts_are_not_fixed_and_build_is_gated(self):
        with tempfile.TemporaryDirectory() as d:
            sparse,effect=self.make(Path(d))
            w,l=fixture()
            l["items"]=l["items"][:0]
            pool=gear.compile_pool(w,l,sparse,effect)
            self.assertEqual(pool["item_count"],4)
            l["db2_build"]="12.1.5.70576"
            with self.assertRaises(gear.CatalogBlocked):
                gear.compile_pool(w,l,sparse,effect)

    def test_fresh_source_only_never_reads_installed_budget_and_reports_unknown(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d:
            sparse,effect=self.make(Path(d))
            w,l=fixture()
            w["build"]=l["db2_build"]="12.2.0.99999"
            with patch.object(gear,"INSTALLED_BUDGET",
                              Path(d)/"DELIBERATELY_ABSENT_OLD.json"):
                result=gear.compile_pool(
                    w,l,sparse,effect,budget_source=None)
            self.assertEqual(result["item_count"],5)
            self.assertEqual(result["consumable_budget_source_mode"],
                             "NEW_SEASON_J_F_BUDGET_EVIDENCE_PENDING")
            self.assertIsNone(result["consumable_budget_reference"])
            self.assertIsNone(result["G"])
            self.assertIsNone(result["B"])
            self.assertIsNone(result["T"])
            self.assertEqual(result["new_native_calls"],0)

    def test_newly_collected_same_build_budget_is_explicit_not_old_reference(self):
        with tempfile.TemporaryDirectory() as d:
            sparse,effect=self.make(Path(d))
            w,l=fixture()
            w["build"]=l["db2_build"]="12.2.0.99999"
            new_budget={
              "retail_build":"12.2.0.99999",
              "ordinary_gem":{"slots":6,"highest_quality_bonus":[12,13],
                              "total_J":150},
              "flasks":{"total_F":210,
                        "single_secondary_highest_quality_rating":210,
                        "by_stat":{k:{"rating":210} for k in
                                   ("crit","haste","mastery","versatility")}}}
            from unittest.mock import patch
            with patch.object(gear,"INSTALLED_BUDGET",
                              Path(d)/"ABSENT_INSTALLED.json"):
                result=gear.compile_pool(
                    w,l,sparse,effect,budget_source=new_budget)
            self.assertEqual(result["consumable_budget_reference"],new_budget)
            self.assertEqual(result["consumable_budget_source_mode"],
                "EXPLICIT_SAME_BUILD_NEW_SEASON_BUDGET_CANDIDATE")
            self.assertIsNone(result["G"])
            self.assertIsNone(result["B"])
            self.assertIsNone(result["T"])
            # A source-supplied number is a candidate, not an authenticated
            # new-season J/F quality or arithmetic approval.
            mismatch=dict(new_budget,retail_build="12.1.5.70575")
            with self.assertRaisesRegex(gear.CatalogBlocked,
                                        "CONSUMABLE_BUDGET_BUILD_MISMATCH"):
                gear.compile_pool(w,l,sparse,effect,budget_source=mismatch)
            incomplete=dict(new_budget,ordinary_gem={"total_J":150})
            with self.assertRaisesRegex(gear.CatalogBlocked,
                                        "CONSUMABLE_BUDGET_DATA_INCONSISTENT"):
                gear.compile_pool(w,l,sparse,effect,budget_source=incomplete)

    def test_missing_effect_columns_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            sparse,effect=self.make(Path(d))
            effect.write_text("ID,ItemEffectID\n1,12345\n")
            with self.assertRaises(gear.CatalogBlocked):
                gear.compile_pool(*fixture(),sparse,effect)

    def test_actual_saved_sources_when_available(self):
        import os
        p=os.getenv("SIMC_V163_JOIN_REPORT")
        q=os.getenv("SIMC_V162_REPORT")
        r=os.getenv("SIMC_V161_ITEMSPARSE")
        e=os.getenv("SIMC_V165_ITEM_EFFECT")
        if not (p and q and r and e):
            self.skipTest("real source artifacts not mounted")
        pool=gear.compile_pool(gear.read_json(p),gear.read_json(q),Path(r),Path(e))
        self.assertEqual(pool["item_count"],513)
        self.assertEqual(pool["build"],"12.1.5.70575")
        self.assertTrue(pool["item_x_item_effect_csv_sha256"])
        self.assertEqual(pool["new_native_calls"],0)
        self.assertTrue(any(x["season_selection"]==
             "CONDITIONAL_SEASON_NOT_ESTABLISHED" for x in pool["items"]))

if __name__=="__main__":unittest.main()
