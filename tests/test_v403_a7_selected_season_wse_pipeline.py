"""A7 regression: opaque WSE cannot become a user item by crossing stages.

Synthetic season/build names/IDs only; this tests the existing product source
path v165->v166->v167 with no external API, no Native or gear recommendation.
"""
from __future__ import annotations
import csv
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v165_current_season_gear_pool as pool
import v166_compact_product_gear_db as compact
import v167_product_season_gear_adapter as product
import v332_blizzard_ko_item_labels as labels

BUILD="13.0.0.88888"
DISPLAY_SEASON=83

def origin(kind,season,wse=0):
    if wse:
        status="UNKNOWN_WORLD_STATE_EXPRESSION"
    elif season==DISPLAY_SEASON:
        status="DB2_DISPLAY_SEASON_MATCH"
    elif season==0:
        status="UNKNOWN_UNSCOPED_JOURNAL"
    else:
        status="UNKNOWN_OTHER_DISPLAY_SEASON"
    return {"source":kind,"season_evidence":status,
            "display_season_id":season,"world_state_expression_id":wse,
            "journal_encounter_id":201,"journal_instance_id":202,
            **({"challenge_mode_id":203} if kind=="mplus_journal" else {})}

def write(path,fields,rows):
    with path.open("w",encoding="utf8",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

class A7SelectedItemPipeline(unittest.TestCase):
    def test_exact_journal_evidence_reaches_public_choices_without_wse_leak(self):
        # The observed CURRENT raid is established separately by v163; only
        # individual ItemJournal conditions are varied in these exact rows.
        items=[
          {"item_id":110,"name":"Active Raid Trinket","slot":12,
           "acquisition_sources":[origin("raid_journal",0,0)]},
          {"item_id":111,"name":"Unresolved Raid Trinket","slot":12,
           "acquisition_sources":[origin("raid_journal",DISPLAY_SEASON,441)]},
          {"item_id":112,"name":"Active Dungeon Trinket","slot":12,
           "acquisition_sources":[origin("mplus_journal",DISPLAY_SEASON,0)]},
          {"item_id":113,"name":"Two Independent Item Sources","slot":12,
           "acquisition_sources":[
              origin("raid_journal",DISPLAY_SEASON,442),
              origin("mplus_journal",DISPLAY_SEASON,0)]},
          {"item_id":114,"name":"Conditional Plain Wrist","slot":9,
           "acquisition_sources":[
              origin("mplus_journal",DISPLAY_SEASON,443)]},
        ]
        source={"schema":"v163_zero_seed_db2_join_v1",
            "source_provider":"WAGO_TOOLS_PINNED_DB2_WCL_LIVE",
            "build":BUILD,"db2_expansion_id":27,
            "db2_display_season_id":DISPLAY_SEASON,
            "items":items}
        with tempfile.TemporaryDirectory() as tmp:
            d=pathlib.Path(tmp)
            sparse=d/"ItemSparse.csv";item=d/"Item.csv"
            effects=d/"ItemXItemEffect.csv"
            write(sparse,["ID","Display_lang","InventoryType","ExpansionID",
                    "ItemSet","OverallQualityID","AllowableClass",
                    "StatModifier_bonusStat_0"],[
                {"ID":r["item_id"],"Display_lang":r["name"],
                 "InventoryType":r["slot"],"ExpansionID":27,"ItemSet":0,
                 "OverallQualityID":4,"AllowableClass":-1,
                 "StatModifier_bonusStat_0":5} for r in items])
            write(item,["ID","ClassID","SubclassID","InventoryType"],[
                {"ID":r["item_id"],"ClassID":4,"SubclassID":0,
                 "InventoryType":r["slot"]} for r in items])
            write(effects,["ItemID","ItemEffectID"],[
                {"ItemID":110,"ItemEffectID":123}])
            original=pool.compile_pool(source,None,sparse,effects,
                                       budget_source=None)
            by_id={r["item_id"]:r for r in original["items"]}
            self.assertEqual([k for k,v in by_id.items()
                 if v["user_selectable_candidate"]],[110,112,113])
            self.assertEqual(by_id[111]["season_selection"],
                             "CONDITIONAL_SEASON_NOT_ESTABLISHED")
            self.assertFalse(by_id[114]["user_selectable_candidate"])
            self.assertEqual(original["consumable_budget_source_mode"],
                             "NEW_SEASON_J_F_BUDGET_EVIDENCE_PENDING")
            ready=compact.build(original,item,sparse)
            self.assertEqual([r["item_id"] for r in
                              ready["current_candidates"]],[110,112,113])
            self.assertEqual(ready["conditional_count"],2)
            self.assertEqual(ready["internal_conditional_mplus_plain_count"],1)
            internal=ready["internal_conditional_mplus_plain_candidates"][0]
            self.assertEqual(internal["item_id"],114)
            self.assertEqual(internal["selection_evidence"],
                             "CONDITIONAL_SEASON_NOT_ESTABLISHED")
            candidate=product.from_v166(ready)
            with mock.patch.object(labels,"installed_names",return_value={}) as no_labels:
                public=product.public_options(candidate)
            no_labels.assert_called_once()
            self.assertEqual(sorted(r["item_id"] for r in
                             public["choices"]["trinket"]),[110,112,113])
            self.assertEqual(public["choices"]["special_effect_gear_candidate"],[])
            self.assertFalse(public["ordinary_equipment_user_selectable"])
            self.assertFalse(public["full_season_completeness_confirmed"])
            self.assertEqual(candidate["internal_conditional_mplus_plain_count"],1)
            self.assertNotIn(111,{r["item_id"] for role in
                   public["choices"].values() for r in role})
            self.assertNotIn(114,{r["item_id"] for role in
                   public["choices"].values() for r in role})
            self.assertEqual(candidate["new_native_calls"],0)
            self.assertEqual(candidate["new_api_calls"],0)

if __name__=="__main__":
    unittest.main()
