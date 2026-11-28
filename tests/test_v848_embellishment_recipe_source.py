"""Two arbitrary builds/expansions: no historical item, recipe or slot IDs."""
import csv
import pathlib
import sys
import tempfile
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v848_embellishment_recipe_source as engine

class GenericRecipeSourceTests(unittest.TestCase):
    def test_arbitrary_build_and_expansion_exact_outputs_and_pending(self):
        for build,exp,base in (("13.0.0.80001",12,810000),
                               ("14.1.0.90002",13,920000)):
            with self.subTest(build=build), tempfile.TemporaryDirectory() as td:
                root=pathlib.Path(td)
                paths={}
                def table(name,fields,rows):
                    path=root/(name+".csv")
                    with path.open("w",newline="",encoding="utf8") as f:
                        w=csv.writer(f);w.writerow(fields);w.writerows(rows)
                    paths[name]=path
                table("SpellEffect",["SpellID","Effect","EffectIndex","EffectMiscValue_0","DifficultyID"],
                    [(base+1,301,0,base+11,0),(base+2,301,0,base+12,0),
                     (base+3,301,0,base+13,0),(base+3,301,1,base+11,0),
                     (base+4,54,0,base+11,0),(base+5,301,0,base+11,1)])
                table("CraftingData",["ID","Type","CraftedItemID"],
                    [(base+11,0,base+21),(base+12,0,base+22),(base+13,0,base+23)])
                table("Item",["ID","ClassID","SubclassID","InventoryType"],
                    [(base+21,4,1,5),(base+22,4,1,6),(base+23,2,7,13)])
                table("ItemSparse",["ID","ExpansionID","InventoryType","Display_lang"],
                    [(base+21,exp,5,"New robe"),(base+22,exp-1,6,"Old belt"),
                     (base+23,exp,13,"New sword")])
                match={"simc_rows":[],"physical_rows":[],"bonus_types":[23],
                    "recipe_slot_sources":[{"slot":{"ID":"7","PlayerConditionID":"9"},
                        "recipe_spell_ids":[base+i for i in range(1,7)]}]}
                result=engine.recipe_outputs([match],paths,game_build=build,
                    simc_revision="a"*40,expansion_id=exp)
                self.assertEqual(result["exact_recipe_spell_count"],1)
                self.assertEqual(result["pending_recipe_spell_count"],5)
                slot=result["matches"][0]["recipe_slot_sources"][0]
                self.assertEqual(slot["exact_recipe_outputs"][0]["item_id"],base+21)
                self.assertEqual(slot["exact_recipe_outputs"][0]["recipe_spell_id"],base+1)
                self.assertFalse(slot["slot_condition_resolved"])
                self.assertFalse(result["matches"][0]["ui_selectable"])
                self.assertFalse(result["ui_promotion"])
                self.assertEqual(result["native_calls"],0)
                self.assertEqual(result["game_build"],build)
                self.assertEqual(result["expansion_id"],exp)
    def test_generated_table_is_build_and_blob_bound_not_fixture_bound(self):
        for build,bonus in (("13.0.0.80001",80001),("14.1.0.90002",90002)):
            raw=(f"// Embellishment data, wow build {build}\n"
                 "static constexpr std::array<embellishment_data_t, 1> __embellishment_data { {\n"
                 f'  {{ "New reagent", {bonus}, 800, 900 }},\n'
                 "} };\n").encode()
            sha=engine.seed.git_blob(raw)
            self.assertEqual(engine.read_simc(raw,build,sha)[0]["bonus_id"],bonus)
            with self.assertRaises(ValueError):
                engine.read_simc(raw,"1.2.3.4",sha)
            with self.assertRaises(ValueError):
                engine.read_simc(raw,build,"f"*40)
