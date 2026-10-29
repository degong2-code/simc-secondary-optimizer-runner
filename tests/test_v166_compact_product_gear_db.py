"""v166: only candidate-level product roster; no special effect certification."""
import csv
from pathlib import Path
import tempfile
import unittest
from runner import v166_compact_product_gear_db as db

def pool():
    return {"schema":"v165_current_season_gear_pool_v1",
        "status":"EFFECT_TABLE_OBSERVED_CANDIDATES",
        "no_legacy_catalog_seed":True,
        "item_x_item_effect_csv_sha256":"a"*64,
        "build":"12.1.5.70575","expansion_id":11,
        "db2_display_season_id":37,
        "consumable_budget_reference":{"ordinary_gem":{"total_J":138},
                                       "flasks":{"total_F":165}},
        "items":[{"item_id":1,"name":"Plate ordinary","inventory_type":5,
                  "item_set_id":0,"quality":4,
                  "category":"plain_representative_candidate",
                  "direct_item_effect_record":False,
                  "season_selection":"CURRENT_CANDIDATE",
                  "user_selectable_candidate":True,
                  "acquisition_sources":[{"source":"raid_journal"}]},
                 {"item_id":2,"name":"Old uncertain","inventory_type":12,
                  "item_set_id":0,"quality":4,"category":"trinket",
                  "direct_item_effect_record":True,
                  "season_selection":"CONDITIONAL_SEASON_NOT_ESTABLISHED",
                  "user_selectable_candidate":False,
                  "acquisition_sources":[{"source":"mplus_journal"}]}]}

class Compact(unittest.TestCase):
    def prepare(self,root):
        item=root/"Item.csv"; sparse=root/"ItemSparse.csv"
        with item.open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=["ID","ClassID","SubclassID","InventoryType"])
            w.writeheader()
            w.writerows([{"ID":1,"ClassID":4,"SubclassID":4,"InventoryType":5},
                         {"ID":2,"ClassID":4,"SubclassID":0,"InventoryType":12}])
        names=["ID","InventoryType","ExpansionID","AllowableClass","ItemSet"]+[
             f"StatModifier_bonusStat_{x}" for x in range(10)]
        with sparse.open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=names)
            w.writeheader()
            w.writerows([{"ID":i,"InventoryType":slot,"ExpansionID":11,
                         "AllowableClass":-1,"ItemSet":0,
                         "StatModifier_bonusStat_0":5}
                         for i,slot in ((1,5),(2,12))])
        return item,sparse

    def test_active_role_and_conditional_separate(self):
        with tempfile.TemporaryDirectory() as d:
            item,sparse=self.prepare(Path(d))
            result=db.build(pool(),item,sparse)
        self.assertEqual(result["current_candidate_count"],1)
        self.assertEqual(result["conditional_count"],1)
        self.assertEqual(result["current_role_counts"],{"plain_representative_candidate":1})
        self.assertEqual(result["current_candidates"][0]["subclass_id"],4)
        self.assertEqual(result["current_candidates"][0]["stat_modifier_codes"],[5])
        self.assertFalse(result["current_mplus_world_state_confirmed"])
        self.assertTrue(result["representative_selection_needs_primary_and_four_tier_resolution"])

    def test_wrong_item_slot_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            item,sparse=self.prepare(Path(d))
            inp=pool();inp["items"][0]["inventory_type"]=4
            with self.assertRaises(db.GearDbBlocked):
                db.build(inp,item,sparse)

    def test_unclassified_effect_pool_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            item,sparse=self.prepare(Path(d))
            inp=pool();inp["status"]="EFFECT_TABLE_PENDING"
            with self.assertRaises(db.GearDbBlocked):
                db.build(inp,item,sparse)

if __name__=="__main__":unittest.main()
