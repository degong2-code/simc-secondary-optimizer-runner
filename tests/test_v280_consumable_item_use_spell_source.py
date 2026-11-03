"""P3-CK: same-build item-effect FK join and v217 reuse; zero Native."""
import io
import json
import pathlib
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v280_consumable_item_use_spell_source as v280

BUILD="12.2.0.99999"
REL=b"ItemID,ItemEffectID\n101,11\n102,12\n102,13\n103,0\n999,15\n"
EFFECT=b"ID,SpellID,TriggerType\n11,501,0\n12,601,0\n13,602,1\n15,999,0\n"
SOURCE={
    "schema":"v190_same_build_consumable_item_candidates_v1",
    "source":{"wago_snapshot_build":BUILD},
    "automatic_ui_promotion":False,
    "items":[
        {"item_id":101,"kind":"flask","ui_selectable":False,
         "simc_token":"UNRESOLVED"},
        {"item_id":102,"kind":"item_enhancement","ui_selectable":False,
         "simc_token":"UNRESOLVED","weapon_oil_identity":"NOT_ESTABLISHED"},
        {"item_id":103,"kind":"item_enhancement","ui_selectable":False,
         "simc_token":"UNRESOLVED","weapon_oil_identity":"NOT_ESTABLISHED"},
        {"item_id":104,"kind":"potion","ui_selectable":False,
         "simc_token":"UNRESOLVED"}],
}

class Response(io.BytesIO):
    status=200

class ItemSpellTests(unittest.TestCase):
    def test_exact_fk_trigger_and_non_promotion(self):
        result=v280.join(SOURCE,REL,EFFECT,build=BUILD,
                         relation_sha256=v280.sha(REL),
                         effect_sha256=v280.sha(EFFECT))
        flask,oil,unknown,potion=result["items"]
        self.assertEqual(flask["item_effect_source"]["on_use_spell_ids"],[501])
        self.assertEqual(oil["item_effect_source"]["on_use_spell_ids"],[601])
        self.assertEqual(oil["item_effect_source"]["observed_effects"][1][
            "trigger_type"],1)
        self.assertEqual(unknown["item_effect_source"]["on_use_spell_ids"],[])
        self.assertNotIn("item_effect_source",potion)
        self.assertEqual(oil["weapon_oil_identity"],"NOT_ESTABLISHED")
        self.assertEqual(result["item_use_spell_join"]["exact_on_use_source_count"],2)
        self.assertEqual(result["item_use_spell_join"]["pending_count"],1)
        self.assertFalse(result["item_use_spell_join"]["highest_quality_verified"])
        self.assertFalse(result["item_use_spell_join"][
            "simc_effect_token_join_verified"])
        self.assertTrue(all(x["ui_selectable"] is False for x in result["items"]))
        self.assertEqual(result["item_use_spell_join"]["native_calls"],0)

    def test_missing_effect_ambiguity_and_source_integrity(self):
        incomplete=b"ID,SpellID,TriggerType\n11,501,0\n"
        result=v280.join(SOURCE,REL,incomplete,build=BUILD,
                         relation_sha256=v280.sha(REL),
                         effect_sha256=v280.sha(incomplete))
        self.assertEqual(result["items"][1]["item_effect_source"]["status"],
                         "ITEM_USE_SPELL_RELATION_PENDING")
        self.assertEqual(result["items"][1]["item_effect_source"][
                         "missing_item_effect_ids"],[12,13])
        with self.assertRaisesRegex(v280.ItemSpellBlocked,"SHA_MISMATCH"):
            v280.join(SOURCE,REL,EFFECT,build=BUILD,
                      relation_sha256="f"*64,
                      effect_sha256=v280.sha(EFFECT))
        bad=b"ID,Spell,TriggerType\n11,501,0\n"
        with self.assertRaisesRegex(v280.ItemSpellBlocked,"EFFECT_COLUMNS_MISSING"):
            v280.join(SOURCE,REL,bad,build=BUILD,
                      relation_sha256=v280.sha(REL),
                      effect_sha256=v280.sha(bad))
        with self.assertRaisesRegex(v280.ItemSpellBlocked,"SAME_BUILD"):
            v280.join(SOURCE,REL,EFFECT,build="12.3.0.88888",
                      relation_sha256=v280.sha(REL),
                      effect_sha256=v280.sha(EFFECT))

    def test_v217_one_additional_fetch_then_reuse_then_tamper_blocks(self):
        with tempfile.TemporaryDirectory() as temp:
            root=pathlib.Path(temp)
            relation=root/"source"/"v254_ItemXItemEffect.csv"
            relation.parent.mkdir(parents=True)
            relation.write_bytes(REL)
            candidate=root/"source"/"v279_v190_items.json"
            candidate.write_text(json.dumps(SOURCE),encoding="utf8")
            gear={"source_stage":{
                "status":"EXECUTED_AND_SEALED",
                "receipt_sha256":"a"*64,
                "output_paths":{"effect":"source/v254_ItemXItemEffect.csv"}}}
            cons={"candidate_path":str(candidate),"source_stage":{
                "status":"EXECUTED_AND_SEALED","receipt_sha256":"b"*64}}
            calls=[]
            def transport(req,timeout):
                calls.append(req.full_url)
                return Response(EFFECT)
            kwargs={"stage_root":root,"build":BUILD,
                    "fresh_gear":gear,"consumables":cons,
                    "transport":transport}
            first=v280.collect(**kwargs)
            self.assertEqual(first["status"],
                             "ITEM_USE_SPELL_SOURCE_JOINED_UNADMITTED",first)
            self.assertEqual(first["network_calls_by_stage"],1)
            self.assertEqual(first["counts"]["exact_on_use_source_count"],2)
            self.assertFalse(first["environment_ready"])
            second=v280.collect(**kwargs)
            self.assertEqual(second["network_calls_by_stage"],0)
            self.assertEqual(second["source_stage"]["status"],"REUSED_VERIFIED")
            self.assertEqual(len(calls),1)
            self.assertEqual(json.loads(candidate.read_text()),SOURCE)
            pathlib.Path(first["candidate_path"]).write_text("tampered")
            blocked=v280.collect(**kwargs)
            self.assertEqual(blocked["status"],"ITEM_USE_SPELL_SOURCE_PENDING")
            self.assertEqual(blocked["network_calls_by_stage"],0)
            self.assertEqual(len(calls),1)

    def test_real_other_source_uses_new_immutable_v283_stage(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            relation=root/"source"/"v254_ItemXItemEffect.csv"
            relation.parent.mkdir(parents=True)
            relation.write_bytes(REL)
            candidate=root/"source"/"v282_v190_items.json"
            candidate.write_text(json.dumps(SOURCE),encoding="utf8")
            gear={"source_stage":{"status":"EXECUTED_AND_SEALED",
                "receipt_sha256":"a"*64,
                "output_paths":{"effect":"source/v254_ItemXItemEffect.csv"}}}
            consumables={"candidate_path":str(candidate),"source_stage":{
                "status":"EXECUTED_AND_SEALED","receipt_sha256":"b"*64,
                "stage_id":"fresh-v189-v190-consumable-physical-other"}}
            calls=[]
            def transport(req,timeout):
                calls.append(req.full_url)
                return Response(EFFECT)
            args=dict(stage_root=root,build=BUILD,fresh_gear=gear,
                      consumables=consumables,transport=transport)
            first=v280.collect(**args)
            self.assertEqual(first["source_stage"]["stage_id"],
                             "fresh-consumable-item-use-spell-source-other")
            self.assertIn("v283_",first["candidate_path"])
            self.assertEqual(first["network_calls_by_stage"],1)
            again=v280.collect(**args)
            self.assertEqual(again["network_calls_by_stage"],0)
            self.assertEqual(len(calls),1)

    def test_no_valid_sources_does_not_attempt_http(self):
        with tempfile.TemporaryDirectory() as temp:
            result=v280.collect(stage_root=temp,build=BUILD,
                                fresh_gear={},consumables={},
                                transport=lambda *_:self.fail("HTTP"))
        self.assertEqual(result["status"],"ITEM_USE_SPELL_SOURCE_PENDING")
        self.assertIsNone(result["F"])
        self.assertIsNone(result["O"])

if __name__=="__main__":
    unittest.main()
