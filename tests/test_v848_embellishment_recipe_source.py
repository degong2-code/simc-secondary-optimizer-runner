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
                    [(base+1,288,0,base+11,0),(base+2,288,0,base+12,0),
                     (base+3,288,0,base+13,0),(base+3,288,1,base+11,0),
                     (base+4,54,0,base+11,0),(base+5,288,0,base+11,1),(base+7,301,0,base+11,0),
                     (base+8,288,0,base+14,0)])
                table("CraftingData",["ID","Type","CraftedItemID"],
                    [(base+11,0,base+21),(base+12,0,base+22),(base+13,0,base+23),(base+14,3,base+21)])
                table("Item",["ID","ClassID","SubclassID","InventoryType"],
                    [(base+21,4,1,5),(base+22,4,1,6),(base+23,2,7,13)])
                table("ItemSparse",["ID","ExpansionID","InventoryType","Display_lang"],
                    [(base+21,exp,5,"New robe"),(base+22,exp-1,6,"Old belt"),
                     (base+23,exp,13,"New sword")])
                match={"simc_rows":[],"physical_rows":[],"bonus_types":[23],
                    "recipe_slot_sources":[{"slot":{"ID":"7","PlayerConditionID":"9"},
                        "recipe_spell_ids":[base+i for i in range(1,9)]}]}
                result=engine.recipe_outputs([match],paths,game_build=build,
                    simc_revision="a"*40,expansion_id=exp)
                self.assertEqual(result["exact_recipe_spell_count"],1)
                self.assertEqual(result["pending_recipe_spell_count"],7)
                slot=result["matches"][0]["recipe_slot_sources"][0]
                self.assertEqual(slot["exact_recipe_outputs"][0]["item_id"],base+21)
                self.assertEqual(slot["exact_recipe_outputs"][0]["recipe_spell_id"],base+1)
                self.assertEqual(slot["exact_recipe_outputs"][0]["effect_code"],288)
                reasons={r["spell_id"]:r for r in slot["pending_recipe_spells"]}
                self.assertEqual(reasons[base+7]["observed_effect_codes"],[301])
                self.assertEqual(reasons[base+8]["reason"],"CRAFTING_DATA_TYPE_NOT_EQUIPMENT_OUTPUT")
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


    def test_normal_build_owner_reuses_raw_across_simc_revisions(self):
        import io,json
        from unittest.mock import patch
        import v216_environment_build_coordinator as env
        stages=engine.stages
        build="13.0.0.80001"; exp=12
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            def seal(stage,files):
                outputs={k:"fixture/"+stage+"/"+k for k in files}
                def execute():
                    for key,data in files.items():
                        stages._atomic_write(root/outputs[key],data)
                return stages.execute_stage(root=root,stage_id=stage,
                    stage_version="fixture-v1",inputs={"game_build":build},
                    outputs=outputs,execute=execute)
            wago=seal("fixture-wago",{
                "receipt":json.dumps({"build":build}).encode(),
                "Item":b"ID,ClassID,SubclassID,InventoryType,CraftingQualityID\n101,0,0,0,14\n201,4,1,5,0\n",
                "ItemSparse":b"ID,Display_lang,ExpansionID,ModifiedCraftingReagentItemID,InventoryType\n101,New reagent,12,301,0\n201,New robe,12,0,5\n",
                "CraftingData":b"ID,Type,CraftedItemID\n401,0,201\n"})
            spell=seal("fixture-spell",{
                "candidate":json.dumps({"simc_relation_source":{"game_build":build}}).encode(),
                "spell_effect":b"SpellID,Effect,EffectIndex,EffectMiscValue_0,DifficultyID\n501,288,0,401,0\n"})
            def simc(rev):
                return seal("fixture-simc-"+rev,{
                    engine.seed.RECEIPT:json.dumps({"schema":engine.seed.SCHEMA,
                        "simc_generated_build":build,"simc_revision":rev,
                        "provenance_tree_blob_authenticated":True}).encode()})
            data={
                "ItemBonus":b"ParentItemBonusListID,Type,Value_0\n601,23,701\n",
                "ItemBonusTreeNode":b"ID,ParentItemBonusTreeID,ChildItemBonusListID,ChildItemBonusTreeID,ChildItemBonusListGroupID\n1,801,601,0,0\n",
                "ModifiedCraftingReagentItem":b"ID,ModifiedCraftingCategoryID,ItemBonusTreeID\n301,901,801\n",
                "ModifiedCraftingReagentSlot":b"ID,Name_lang,Flags,PlayerConditionID,ReagentType\n1001,Add Embellishment,0,0,1\n",
                "MCRSlotXMCRCategory":b"ID,ModifiedCraftingCategoryID,ModifiedCraftingReagentSlotID\n1,901,1001\n",
                "ModifiedCraftingSpellSlot":b"ID,SpellID,ModifiedCraftingReagentSlotID,Slot,ReagentCount\n1,501,1001,0,1\n"}
            raw=(f"// Embellishment data, wow build {build}\n"
                 "static constexpr std::array<embellishment_data_t, 1> __embellishment_data { {\n"
                 '  { "New reagent", 601, 701, 1101 },\n} };\n').encode()
            class Response(io.BytesIO):
                status=200
            calls=[]
            def transport(req,timeout):
                url=req.full_url
                if "/db2/" in url:
                    table=url.split("/db2/")[1].split("/")[0]
                    calls.append(table)
                    return Response(data[table])
                self.assertTrue(url.endswith(engine.DEFINITION_PATH))
                calls.append("simc-definition")
                return Response(raw)
            # Tree walking itself is the existing v275 tested owner; mock only
            # its immutable blob metadata, not the real v848/v217 stage.
            def tree(**kw):
                return {engine.DEFINITION:{"sha":engine.seed.git_blob(raw),
                                           "size":len(raw)}}
            def collect(s,**kw):
                return env._fresh_embellishment_source(stage_root=root,build=build,
                    expansion_id=kw.get("expansion_id",exp),wago_stage=wago,
                    spell_stage=kw.get("spell_stage",spell),simc_stage=s,transport=transport)
            with patch.object(engine.pinned,"pinned_git_blobs",side_effect=tree) as pin:
                sa=simc("a"*40)
                first=collect(sa)
                self.assertEqual(first["status"],"RECIPE_OUTPUT_SOURCE_PROJECTED",first)
                self.assertEqual(first["exact_recipe_spell_count"],1)
                self.assertEqual(first["matched_effect_count"],1)
                self.assertEqual(first["network_calls_by_stage"],7)
                original=pathlib.Path(first["candidate_path"]).read_bytes()
                before=len(calls)
                second=collect(sa)
                self.assertEqual(second["source_stage"]["status"],"REUSED_VERIFIED")
                self.assertEqual(second["network_calls_by_stage"],0)
                self.assertEqual(len(calls),before)
                third=collect(simc("b"*40))
                self.assertEqual(third["status"],"RECIPE_OUTPUT_SOURCE_PROJECTED",third)
                self.assertEqual(third["network_calls_by_stage"],1)
                self.assertEqual(calls[before:],["simc-definition"])
                self.assertEqual(pin.call_count,2)
                self.assertNotEqual(first["candidate_path"],third["candidate_path"])
                self.assertEqual(pathlib.Path(first["candidate_path"]).read_bytes(),original)
                self.assertFalse(third["automatic_ui_promotion"])
                self.assertEqual(third["native_calls"],0)
                fourth=collect(sa,spell_stage=None)
                self.assertEqual(fourth["status"],"EMBELLISHMENT_SOURCE_PENDING")
                self.assertEqual(fourth["network_calls_by_stage"],0)
                # A corrupt same-build cached raw is never silently fetched
                # again or published. Core Build can retain its own result.
                (root/"source/raw_ModifiedCraftingReagentItem.csv").write_text("bad",encoding="utf8")
                bad=collect(sa)
                self.assertEqual(bad["status"],"EMBELLISHMENT_SOURCE_PENDING")
                self.assertEqual(bad["network_calls_by_stage"],0)
                self.assertFalse(bad["automatic_ui_promotion"])
