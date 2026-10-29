"""Profession discovery using ONLY synthetic Blizzard provider JSON; no historical DB."""
import json
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v157_blizzard_craft_probe as probe

class CraftedSourceFirstOffline(unittest.TestCase):
    def test_output_id_explicit_or_unknown(self):
        self.assertIsNone(probe.output_item_ids({"id":1,"name":"Test"}))
        self.assertEqual(probe.output_item_ids({"crafted_item":{"id":940001}}),
                         [940001])
        self.assertEqual(probe.output_item_ids({"crafted_items":[
            {"id":940003},{"id":940002},{"id":940003}]}),[940002,940003])

    def test_category_tree_from_official_recipe_refs(self):
        d={"categories":[{"recipes":[
            {"id":9001,"name":"New Garment"},
            {"id":9002,"name":"Other Gear"}],
            "sub_categories":[{"recipes":[
                {"id":9003,"name":"New Boots"}]}]}]}
        result=probe.categories_with_recipes(d)
        self.assertEqual([r["id"] for r in result["recipes"]],
                         [9001,9002,9003])
        self.assertEqual(probe.categories_with_recipes({})["status"],
                         "RECIPE_CATEGORIES_NOT_EXPOSED")

    def test_no_historical_item_input_one_profession_3_recipe_details(self):
        class Response:
            status=200
            def __init__(self,data):self.raw=json.dumps(data).encode()
            def __enter__(self):return self
            def __exit__(self,*a):return None
            def read(self,n):return self.raw
        urls=[]
        def transport(req,timeout):
            urls.append(req.full_url)
            if req.full_url.endswith("/token"):
                return Response({"access_token":"SECRET_DUMMY"})
            if "profession/index" in req.full_url:
                return Response({"professions":[
                    {"id":123,"name":"Tailoring"}]})
            if "profession/123/skill-tier/777" in req.full_url:
                return Response({"categories":[{"recipes":[
                    {"id":909,"name":"Future Robe"},
                    {"id":910,"name":"Future Gloves"},
                    {"id":911,"name":"Future Shoulder"},
                    {"id":912,"name":"Future Cape"}]}]})
            if "profession/123" in req.full_url:
                return Response({"skill_tiers":[
                    {"id":777,"name":"Future Expansion Tailoring"}]})
            if "recipe/909" in req.full_url:
                return Response({"id":909,"crafted_item":{"id":980000}})
            if "recipe/910" in req.full_url:
                return Response({"id":910,"name":"Missing output"})
            if "recipe/911" in req.full_url:
                return Response({"id":911,"crafted_items":[{"id":980001}]})
            raise AssertionError("UNEXPECTED_REQUEST")
        data=probe.gather("id","secret",profession="Tailoring",
            expansion="Future Expansion",transport=transport)
        self.assertEqual(len(urls),7) # OAuth + 3 metadata + 3 recipe details
        self.assertEqual(data["blizzard_game_data_requests"],6)
        self.assertEqual(len(data["discovered_recipe_references"]),4)
        self.assertEqual(data["sampled_recipe_details"][0]
                         ["crafted_output_item_ids"],[980000])
        self.assertIsNone(data["sampled_recipe_details"][1]
                          ["crafted_output_item_ids"])
        self.assertEqual(data["sampled_recipe_details"][2]
                         ["crafted_output_item_ids"],[980001])
        self.assertFalse(data["prior_item_data_used"])
        self.assertFalse(data["craftable_item_catalog_complete"])
        self.assertEqual(data["simc_native_calls"],0)
        self.assertNotIn("SECRET_DUMMY",json.dumps(data))

    def test_missing_profession_or_tier_not_guessed(self):
        self.assertEqual(probe.named([{"id":20,"name":"Alchemy"}],"Tailoring"),[])
        self.assertEqual(probe.named([{"id":22,"name":"Midnight Tailoring"}],
                                     "Midnight")[0]["id"],22)

    def test_duplicate_recipe_conflict(self):
        with self.assertRaises(probe.auth.ProbeBlocked):
            probe.categories_with_recipes({"categories":[{"recipes":[
                {"id":8,"name":"A"},{"id":8,"name":"B"}]}]})

if __name__=="__main__":
    unittest.main()
