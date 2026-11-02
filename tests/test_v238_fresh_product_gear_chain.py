"""P1 cold-start product gear integration: existing v165→v166→v167, NO new engine.

Uses newly supplied *synthetic* same-build Wago/Localbots-like source data,
and deliberately removes access to the installed historic J/F source.
This is an offline vertical contract, NOT a real new-season fetch, SimC
Native measurement, whole-season completeness claim or final zero-history test.
"""
from __future__ import annotations

import csv
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from runner import v165_current_season_gear_pool as pool
from runner import v166_compact_product_gear_db as compact
from runner import v167_product_season_gear_adapter as product

BUILD="12.2.0.99999"
EXPANSION=12


def table(path,columns,rows):
    with path.open("w",encoding="utf8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def new_season_reports():
    return (
        {
            "schema":"v163_zero_seed_db2_join_v1",
            "source_provider":"WAGO_TOOLS_PINNED_DB2_WCL_LIVE",
            "build":BUILD,"db2_expansion_id":EXPANSION,
            "db2_display_season_id":91,
            "items":[
                {"item_id":4001,"name":"New plate chest","slot":5,
                 "acquisition_sources":[{"source":"raid_journal",
                    "season_evidence":"DB2_DISPLAY_SEASON_MATCH"}]},
                {"item_id":4002,"name":"New ring","slot":11,
                 "acquisition_sources":[{"source":"mplus_journal",
                    "season_evidence":"DB2_DISPLAY_SEASON_MATCH"}]},
                {"item_id":4003,"name":"New crafted waist","slot":6,
                 "acquisition_sources":[{"source":"selectable_stat_craft",
                    "season_evidence":"DB2_EXPANSION_MATCH"}]},
                {"item_id":4004,"name":"Old raid excluded","slot":5,
                 "acquisition_sources":[{"source":"mplus_journal",
                    "season_evidence":"UNKNOWN_WORLD_STATE_EXPRESSION",
                    "world_state_expression_id":100001}]},
            ],
        },
        {
            "schema":"v162_localbots_delve_source_v1",
            "source_provider":"Localbots / balovich-matje/localbots",
            "db2_build":BUILD,"db2_expansion_id":EXPANSION,
            "items":[{"item_id":4005,"name":"New delve cape",
                      "inventory_type":16,
                      "resolution":"LOCALBOTS_EXPLICIT_ID_DB2_VERIFIED"}],
        },
    )


def prepare_csv(root):
    rows=[
        (4001,5,EXPANSION,0,4,4,4),
        (4002,11,EXPANSION,0,4,4,0),
        (4003,6,EXPANSION,0,4,4,4),
        (4004,5,7,0,4,4,4),
        (4005,16,EXPANSION,0,4,4,1),
    ]
    item=root/"Item.csv"
    table(item,["ID","ClassID","SubclassID","InventoryType"],[
        {"ID":i,"ClassID":cl,"SubclassID":sub,"InventoryType":slot}
        for i,slot,ex,iset,quality,cl,sub in rows])
    sparse=root/"ItemSparse.csv"
    names=["ID","Display_lang","InventoryType","ExpansionID","ItemSet",
           "OverallQualityID","AllowableClass"]+[
               f"StatModifier_bonusStat_{i}" for i in range(10)]
    table(sparse,names,[
        {"ID":i,"Display_lang":f"discovered_{i}","InventoryType":slot,
         "ExpansionID":ex,"ItemSet":iset,"OverallQualityID":quality,
         "AllowableClass":-1,"StatModifier_bonusStat_0":5}
        for i,slot,ex,iset,quality,cl,sub in rows])
    effect=root/"ItemXItemEffect.csv"
    table(effect,["ID","ItemID","ItemEffectID"],[
        {"ID":1,"ItemID":4003,"ItemEffectID":100000}])
    return item,sparse,effect


class ExistingSingleGearPipeline(unittest.TestCase):
    def test_new_season_wago_to_product_catalog_without_old_jf_reference(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            item,sparse,effect=prepare_csv(root)
            wago,local=new_season_reports()
            # Old installed source deliberately *does not exist*. The real
            # v165-v166-v167 functions must never touch it on fresh Build.
            with patch.object(pool,"INSTALLED_BUDGET",
                              root/"FORBIDDEN_PREVIOUS_SEASON_BUDGET.json"):
                v165=pool.compile_pool(wago,local,sparse,effect,
                                       budget_source=None)
            v166=compact.build(v165,item,sparse)
            v167=product.from_v166(v166)
        self.assertEqual(v165["build"],BUILD)
        self.assertIsNone(v165["consumable_budget_reference"])
        self.assertEqual(v165["consumable_budget_source_mode"],
                         "NEW_SEASON_J_F_BUDGET_EVIDENCE_PENDING")
        self.assertEqual(v166["consumable_budget_source_mode"],
                         v165["consumable_budget_source_mode"])
        self.assertEqual(v167["consumable_budget_source_mode"],
                         v165["consumable_budget_source_mode"])
        self.assertTrue(v167["J_F_NUMERIC_AUTHENTICATION_NOT_IN_GEAR_COLLECTOR"])
        self.assertEqual(v167["season_build"],BUILD)
        self.assertEqual(v167["item_count"],3)
        self.assertEqual({x["item_id"] for x in v167["items"]},
                         {4001,4002,4005})
        # Selectable-stat craft classified as special; v165 original source
        # allows the source candidate. With direct ItemXItemEffect relation
        # the v166 product pool should also contain it.
        self.assertEqual(v166["current_candidate_count"],3)
        self.assertEqual(v166["conditional_count"],1)
        self.assertTrue(v167["not_certified"]["tier_four_set"])
        self.assertNotIn("G",v167)
        self.assertEqual(v167["new_native_calls"],0)
        self.assertEqual(v167["new_api_calls"],0)

    def test_source_budget_invalid_does_not_change_existing_files_or_gear(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            item,sparse,effect=prepare_csv(root)
            wago,local=new_season_reports()
            before={p.name:p.read_bytes() for p in (item,sparse,effect)}
            stale={"retail_build":"12.1.5.70575",
                   "ordinary_gem":{"slots":1,"highest_quality_bonus":[1],
                                   "total_J":1},
                   "flasks":{"total_F":1,
                             "single_secondary_highest_quality_rating":1,
                             "by_stat":{x:{"rating":1} for x in
                                 ("crit","haste","mastery","versatility")}}}
            with self.assertRaisesRegex(pool.CatalogBlocked,
                                        "CONSUMABLE_BUDGET_BUILD_MISMATCH"):
                pool.compile_pool(wago,local,sparse,effect,
                                  budget_source=stale)
            self.assertEqual(before,{p.name:p.read_bytes()
                                      for p in (item,sparse,effect)})


if __name__=="__main__":
    unittest.main()
