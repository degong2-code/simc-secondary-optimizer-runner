"""P3-CL: exact on-use SpellEffect-to-SimC identity, no Native/UI."""
import io,json,pathlib,sys,tempfile,unittest
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v281_consumable_simc_relation as v281
import v280_consumable_item_use_spell_source as v280
BUILD="12.2.0.99999"
CSV=b"SpellID,DifficultyID,Effect,EffectMiscValue_0,EffectMiscValue_1,EffectIndex\n111,0,6,0,0,0\n211,0,54,8052,0,0\n212,0,54,9999,0,0\n999,0,54,8052,0,0\n"
TEMP=b"""// Temporary item enchants, wow build 12.2.0.99999
static constexpr std::array<temporary_enchant_entry_t, 2> __temporary_enchant_data { {
  { 8051, 1, 1237008, "thalassian_phoenix_oil" },
  { 8052, 2, 1237006, "thalassian_phoenix_oil" },
} };
"""
TMP=[{"enchant_id":8051,"quality_rank":1,"effect_spell_id":1237008,"simc_token":"thalassian_phoenix_oil"},
     {"enchant_id":8052,"quality_rank":2,"effect_spell_id":1237006,"simc_token":"thalassian_phoenix_oil"}]
FLASK=[{"item_id":501,"name":"Test Flask","crafting_quality":3,"class_id":0,"subclass_id":3}]
SOURCE={"schema":"v190_same_build_consumable_item_candidates_v1",
 "automatic_ui_promotion":False,"source":{"wago_snapshot_build":BUILD},
 "item_use_spell_join":{"schema":v280.SCHEMA},
 "items":[
 {"item_id":501,"kind":"flask","ui_selectable":False,"simc_token":"UNRESOLVED",
  "item_effect_source":{"on_use_spell_ids":[111],"status":"EXACT_DB2_ITEM_TO_ON_USE_SPELL_SOURCE_ONLY"}},
 {"item_id":601,"kind":"item_enhancement","ui_selectable":False,"simc_token":"UNRESOLVED",
  "weapon_oil_identity":"NOT_ESTABLISHED",
  "item_effect_source":{"on_use_spell_ids":[211],"status":"EXACT_DB2_ITEM_TO_ON_USE_SPELL_SOURCE_ONLY"}},
 {"item_id":602,"kind":"item_enhancement","ui_selectable":False,"simc_token":"UNRESOLVED",
  "weapon_oil_identity":"NOT_ESTABLISHED",
  "item_effect_source":{"on_use_spell_ids":[212],"status":"EXACT_DB2_ITEM_TO_ON_USE_SPELL_SOURCE_ONLY"}}]}
class Response(io.BytesIO):
    status=200
class ConsumptionRelation(unittest.TestCase):
    def rows(self,root):
        path=root/"effects.csv";path.write_bytes(CSV)
        return v281.scan_spell_effects(path,{111,211,212})
    def test_exact_enchant_and_item_id_without_publication(self):
        with tempfile.TemporaryDirectory() as td:
            doc=v281.correlate(SOURCE,self.rows(pathlib.Path(td)),TMP,
                               build=BUILD,flask_dbc_rows=FLASK)
        flask,oil,not_oil=doc["items"]
        self.assertEqual(flask["simc_flask_item_source"]["simc_flask_option_candidate"],"test_flask_3")
        self.assertFalse(flask["simc_flask_item_source"]["simc_option_native_verified"])
        match=oil["simc_temporary_enchant_source"]["exact_source_matches"][0]
        self.assertEqual((match["enchant_id"],match["simc_effect_spell_id"]),(8052,1237006))
        self.assertFalse(oil["simc_temporary_enchant_source"]["weapon_oil_identity_verified"])
        self.assertEqual(not_oil["simc_temporary_enchant_source"]["enchant_ids_without_simc_row"],[9999])
        self.assertEqual(doc["simc_relation_source"]["matched_temporary_enchant_source_items"],1)
        self.assertFalse(doc["simc_relation_source"]["highest_quality_verified"])
        self.assertFalse(doc["automatic_ui_promotion"])
        self.assertIsNone(doc["simc_relation_source"]["O"])
    def test_conflict_build_drift_and_unknown_db2_columns(self):
        with tempfile.TemporaryDirectory() as td:
            rows=self.rows(pathlib.Path(td))
        double=TMP+[dict(TMP[-1],quality_rank=3)]
        result=v281.correlate(SOURCE,rows,double,build=BUILD,flask_dbc_rows=FLASK)
        self.assertEqual(result["items"][1]["simc_temporary_enchant_source"]["status"],
                         "TEMP_ENCHANT_SIMC_RELATION_PENDING")
        with self.assertRaisesRegex(v281.SimCRelationBlocked,"EXACT_V280"):
            v281.correlate(SOURCE,rows,TMP,build="12.2.0.99998")
        with tempfile.TemporaryDirectory() as td:
            path=pathlib.Path(td)/"bad.csv"
            path.write_text("SpellID,DifficultyID,Effect,EffectIndex,Wrong\n211,0,54,0,8052\n")
            with self.assertRaisesRegex(v281.SimCRelationBlocked,"COLUMNS_DRIFT"):
                v281.scan_spell_effects(path,{211})
    def test_same_build_real_csv_fields_and_difficulty_are_not_confused(self):
        # The column spellings were read from live Wago Retail
        # 12.1.5.70575 HTTP 200, workflow #41657577279.
        rows=b"ID,SpellID,DifficultyID,EffectIndex,Effect,EffectMiscValue_0,EffectMiscValue_1\n1,211,0,0,54,8052,9999\n2,211,1,0,54,8051,9999\n"
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/"actual-shape.csv";p.write_bytes(rows)
            parsed=v281.scan_spell_effects(p,{211})
        self.assertEqual(len(parsed),2)
        self.assertEqual(parsed[0]["enchant_id"],8052)
        self.assertEqual(parsed[0]["difficulty_id"],0)
        self.assertEqual(parsed[1]["difficulty_id"],1)
        doc=v281.correlate(SOURCE,parsed,TMP,build=BUILD,flask_dbc_rows=FLASK)
        self.assertEqual(doc["items"][1]["simc_temporary_enchant_source"][
                         "exact_source_matches"][0]["enchant_id"],8052)
        self.assertNotIn(8051,[r["enchant_id"] for r in doc["items"][1][
                         "simc_temporary_enchant_source"]["exact_source_matches"]])
    def test_sealed_stage_one_fetch_then_zero_and_tamper_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td);(root/"source").mkdir()
            candidate=root/"source"/"v280.json"
            candidate.write_text(json.dumps(SOURCE))
            compiler=root/"simc";compiler.mkdir()
            (compiler/"temporary_enchant.inc").write_bytes(TEMP)
            src={"candidate_path":str(candidate),"source_stage":{
                  "status":"EXECUTED_AND_SEALED","receipt_sha256":"a"*64}}
            classifier={"source_dir":str(compiler),"source_stage":{
                  "status":"EXECUTED_AND_SEALED","receipt_sha256":"b"*64}}
            full={"source_dir":str(root/"full"),"source_stage":{
                  "status":"EXECUTED_AND_SEALED","receipt_sha256":"c"*64}}
            hits=[]
            def transport(req,timeout):
                hits.append(req.full_url);return Response(CSV)
            call=dict(stage_root=root,build=BUILD,consumables=src,
                      compiler_source=classifier,full_simc_item_source=full,
                      transport=transport)
            with mock.patch.object(v281,"_full_seed_identity",return_value="f"*64),\
                 mock.patch.object(v281,"_flask_from_sealed_item_data",
                                   return_value=(FLASK,"EXACT","f"*64)):
                first=v281.collect(**call)
                self.assertEqual(first["status"],"SIMC_CONSUMABLE_RELATIONS_SOURCE_ONLY",first)
                self.assertEqual(first["network_calls_by_stage"],1)
                second=v281.collect(**call)
                self.assertEqual(second["network_calls_by_stage"],0)
                self.assertEqual(second["source_stage"]["status"],"REUSED_VERIFIED")
                self.assertEqual(len(hits),1)
                pathlib.Path(first["candidate_path"]).write_text("tampered")
                blocked=v281.collect(**call)
                self.assertEqual(blocked["status"],"CONSUMABLE_SIMC_RELATION_SOURCE_PENDING")
                self.assertEqual(blocked["network_calls_by_stage"],0)
                self.assertEqual(len(hits),1)
    def test_missing_exact_sources_zero_network(self):
        with tempfile.TemporaryDirectory() as td:
            result=v281.collect(stage_root=td,build=BUILD,consumables={},
                                compiler_source={},full_simc_item_source={},
                                transport=lambda *_:self.fail("network"))
        self.assertIsNone(result["F"]);self.assertIsNone(result["O"])
        self.assertEqual(result["network_calls_by_stage"],0)
if __name__=="__main__":unittest.main()
