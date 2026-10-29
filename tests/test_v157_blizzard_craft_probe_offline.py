"""v157 crafting API reconciling synthetic response and v057 real reference; zero HTTP."""
import json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v157_blizzard_craft_probe as probe
class CraftedProbeOffline(unittest.TestCase):
    def test_existing_51_and_no_assumed_recipe_ids(self):
        ids,names=probe.source_reference()
        self.assertEqual(len(ids),51)
        self.assertTrue(names)
        self.assertFalse(any(i<=0 for i in ids))
    def test_explicit_items_unknown_if_absent(self):
        self.assertIsNone(probe.output_item_ids({"id":123,"name":"Test"}))
        self.assertEqual(probe.output_item_ids({
            "crafted_item":{"id":239648}}),[239648])
        self.assertEqual(probe.output_item_ids({
            "crafted_items":[{"id":1},{"id":1},{"id":2}]}),[1,2])
    def test_reference_name_matching_never_implies_recipe_proof(self):
        ids,names=probe.source_reference()
        self.assertIn(239656,ids)
        for n in ("Adherent's Silken Shroud","Martyr's Crown","Martyr's Gloves"):
            self.assertIn(n,names)

    def test_actual_sample_shape_contract(self):
        d={"categories":[{"name":"Armor","recipes":[
            {"id":9,"name":"Martyr's Crown"},
            {"id":10,"name":"Something Else"}],
            "sub_categories":[{"recipes":[{"id":11,"name":"Martyr's Gloves"}]}]}]}
        row=probe.categories_with_recipes(d)
        self.assertEqual(row["status"],"EXPLICIT_RECIPE_REFS")
        self.assertEqual({r["id"] for r in row["recipes"]},{9,10,11})
        self.assertEqual(probe.categories_with_recipes({})["status"],
                         "RECIPE_CATEGORIES_NOT_EXPOSED")
    def test_no_guessing_midnight_profession_tier(self):
        self.assertEqual(probe.named([{"id":197,"name":"Tailoring"}],"Tailoring"),
                         [{"id":197,"name":"Tailoring"}])
        self.assertEqual(probe.named([{"id":100,"name":"Dragonflight Tailoring"}],
                          "Midnight"),[])
if __name__=="__main__":unittest.main()
