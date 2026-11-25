"""v583 original v216 source join: exact physical IDs, caching, and fail-closed."""
import csv
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runner"))
import v217_stage_execution_engine as stage
import v583_permanent_enchant_physical_source as v583


BUILD="12.1.5.70783"
EXPANSION=11


def csv_bytes(columns, rows):
    buf=io.StringIO()
    writer=csv.DictWriter(buf,fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode()


def fake_stage(root,stage_id,files):
    outputs={key:path for key,(path,_) in files.items()}
    def execute():
        for path,raw in files.values():
            target=root/path
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(raw)
    return stage.execute_stage(
        root=root,stage_id=stage_id,stage_version="fixture-v1",
        inputs={"fixture":stage_id},outputs=outputs,execute=execute)


class Resp:
    def __init__(self,content):
        self.status=200
        self.buf=io.BytesIO(content)
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self,n=-1):return self.buf.read(n)


class TestV583(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        wago_files={
            "Item":csv_bytes(("ID","ClassID","SubclassID"),[
                {"ID":244014,"ClassID":8,"SubclassID":0},
                {"ID":244015,"ClassID":8,"SubclassID":0},
                {"ID":244016,"ClassID":8,"SubclassID":0}]),
            "ItemSparse":csv_bytes(("ID","ExpansionID","Display_lang"),[
                {"ID":244014,"ExpansionID":11,"Display_lang":"Lesser enchant"},
                {"ID":244015,"ExpansionID":11,"Display_lang":"Greater enchant"},
                {"ID":244016,"ExpansionID":10,"Display_lang":"Old enchant"}]),
            "CraftingData":csv_bytes(("ID","Type"),[
                {"ID":3828,"Type":3},{"ID":3829,"Type":3}])}
        receipt={"schema":"v161_wago_zero_seed_csv_snapshot_v1",
                 "source":"wago.tools/db2","build":BUILD,
                 "tables":{key:{"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
                           for key,raw in wago_files.items()}}
        self.wago=fake_stage(self.root,"fake-wago",{
            **{key:("wago/"+key+".csv",raw) for key,raw in wago_files.items()},
            "receipt":("wago/receipt.json",json.dumps(receipt).encode())})
        self.gear=fake_stage(self.root,"fake-gear",{
            "effect":("source/fake_ItemXItemEffect.csv",
                csv_bytes(("ItemID","ItemEffectID"),[
                    {"ItemID":244014,"ItemEffectID":100},
                    {"ItemID":244015,"ItemEffectID":101},
                    {"ItemID":244016,"ItemEffectID":102}]))})
        self.item_effect=fake_stage(self.root,"fake-item-effects",{
            "item_effect":("source/fake_ItemEffect.csv",
                csv_bytes(("ID","SpellID","TriggerType"),[
                    {"ID":100,"SpellID":777,"TriggerType":5},
                    {"ID":101,"SpellID":778,"TriggerType":5},
                    {"ID":102,"SpellID":779,"TriggerType":0}]))})
        self.spell_effect=fake_stage(self.root,"fake-spell-effects",{
            "spell_effect":("source/fake_SpellEffect.csv",
                csv_bytes(("SpellID","Effect","EffectIndex",
                           "EffectMiscValue_0","DifficultyID"),[
                    {"SpellID":777,"Effect":301,"EffectIndex":0,
                     "EffectMiscValue_0":3828,"DifficultyID":0},
                    {"SpellID":778,"Effect":301,"EffectIndex":0,
                     "EffectMiscValue_0":3829,"DifficultyID":0},
                    {"SpellID":779,"Effect":301,"EffectIndex":0,
                     "EffectMiscValue_0":3829,"DifficultyID":0}]))})
        self.simc_source=fake_stage(self.root,"fake-simc",{
            "permanent_enchant.inc":("source/fake_permanent_enchant.inc",b"fixture")})
        self.quality=csv_bytes(("ID","Rank","SpellItemEnchantmentID",
                                "ItemID","CraftingDataID"),[
            {"ID":1,"Rank":13,"SpellItemEnchantmentID":8024,
             "ItemID":244014,"CraftingDataID":3828},
            {"ID":2,"Rank":14,"SpellItemEnchantmentID":8025,
             "ItemID":244015,"CraftingDataID":3829}])
        self.args={"stage_root":self.root,"build":BUILD,"expansion_id":EXPANSION,
                   "wago_stage":self.wago,
                   "fresh_gear":{"source_stage":self.gear},
                   "item_spells":{"source_stage":self.item_effect},
                   "simc_effects":{"source_stage":self.spell_effect},
                   "pinned_simc":{"source_stage":self.simc_source,
                                  "simc_revision":"a"*40}}
        self.rows=[
            {"enchant_id":8024,"quality_rank":1,"item_class":4,
             "inventory_type_mask":0x800,"item_subclass_mask":0,
             "simc_token":"enchant_ring__alacrity"},
            {"enchant_id":8025,"quality_rank":2,"item_class":4,
             "inventory_type_mask":0x800,"item_subclass_mask":0,
             "simc_token":"enchant_ring__alacrity"}]
        self.parse=mock.patch.object(v583.simc,"parse_generated",
            return_value={"source_build":BUILD,"declared_rows":2,
                          "sha256":"0"*64,"rows":self.rows})
        self.top=mock.patch.object(v583.simc,"current_season_enchant_candidates",
            return_value=[self.rows[1]])
        self.parse.start();self.top.start()
        self.addCleanup(self.parse.stop);self.addCleanup(self.top.stop)

    def test_join_exact_high_and_low_quality_and_exclude_other_expansion(self):
        calls=[]
        def fetch(request,timeout):
            calls.append(request.full_url)
            return Resp(self.quality)
        first=v583.collect(**self.args,transport=fetch)
        self.assertEqual(first["status"],"PERMANENT_ENCHANT_EXACT_WAGO_SIMC_SOURCE_ONLY",first)
        self.assertEqual(first["network_calls_by_stage"],1)
        self.assertEqual(len(calls),1)
        self.assertEqual(first["counts"]["highest_simc_candidate_linked"],1)
        self.assertEqual(first["counts"]["all_rank_simc_id_linked"],2)
        self.assertEqual(first["counts"]["physical_item_ids_linked"],2)
        doc=json.loads(Path(first["candidate_path"]).read_text())
        self.assertEqual(doc["highest_simc_candidate_missing_ids"],[])
        self.assertEqual(doc["matches"][1]["physical_items"][0]["item_id"],244015)
        self.assertEqual(doc["matches"][1]["physical_items"][0]["quality_rank_wago"],14)
        self.assertFalse(doc["automatic_ui_promotion"])

    def test_v770_independent_raw_relation_feeds_permanent_enchant_join(self):
        from urllib.parse import urlencode
        raw=self.root/"source/raw_gear_effect.csv"
        original=(self.root/self.gear["output_paths"]["effect"]).read_bytes()
        relation=stage.execute_stage(
            root=self.root,stage_id="season-gear-effect-raw",
            stage_version="same-build-raw-v1",
            inputs={"game_build":BUILD,"source_url":
                "https://wago.tools/db2/ItemXItemEffect/csv?"+urlencode(
                    {"build":BUILD,"locale":"enUS"})},
            outputs={"raw":"source/raw_gear_effect.csv"},
            execute=lambda:raw.write_bytes(original))
        gear=fake_stage(self.root,"derived-gear",{
            "candidate":("source/derived-gear.json",b"{}")})
        args={**self.args,"fresh_gear":{"source_stage":gear,
            "item_effect_relation_source_receipt_sha256":relation["receipt_sha256"]}}
        result=v583.collect(**args,transport=lambda *_,**__:Resp(self.quality))
        self.assertEqual(result["status"],"PERMANENT_ENCHANT_EXACT_WAGO_SIMC_SOURCE_ONLY",result)
        doc=json.loads(Path(result["candidate_path"]).read_text())
        self.assertEqual(doc["source_stage_receipts"]["gear"],relation["receipt_sha256"])
        self.assertEqual(result["counts"]["all_rank_simc_id_linked"],2)
        again=v583.collect(**args,transport=lambda *_,**__:self.fail("NO_HTTP"))
        self.assertEqual(again["source_stage"]["status"],"REUSED_VERIFIED")

    def test_unchanged_build_reuses_quality_and_projection_with_no_network(self):
        first=v583.collect(**self.args,transport=lambda *_, **__:Resp(self.quality))
        self.assertIsNotNone(first["candidate_path"])
        def never(*args,**kwargs):
            raise AssertionError("unexpected second Wago download")
        second=v583.collect(**self.args,transport=never)
        self.assertEqual(second["network_calls_by_stage"],0,second)
        self.assertEqual(second["quality_source_stage"]["status"],"REUSED_VERIFIED")
        self.assertEqual(second["source_stage"]["status"],"REUSED_VERIFIED")
        self.assertEqual(second["candidate_path"],first["candidate_path"])

    def test_missing_optional_sources_never_fetch_or_block_base(self):
        params={**self.args,"simc_effects":{}}
        result=v583.collect(**params,transport=lambda *_:(_ for _ in ()).throw(
            AssertionError("no optional fetch permitted")))
        self.assertEqual(result["status"],"PERMANENT_ENCHANT_SOURCE_PENDING")
        self.assertEqual(result["network_calls_by_stage"],0)
        self.assertFalse(result["environment_ready"])

    def test_new_simc_revision_reuses_static_wago_quality(self):
        first=v583.collect(**self.args,transport=lambda *_, **__:Resp(self.quality))
        self.assertIsNotNone(first["candidate_path"])
        second_stage=fake_stage(self.root,"fake-simc-new",{
            "permanent_enchant.inc":("source/fake_permanent_new.inc",b"fixture")})
        args={**self.args,"pinned_simc":{"source_stage":second_stage,
                                       "simc_revision":"b"*40}}
        second=v583.collect(**args,transport=lambda *_:(_ for _ in ()).throw(
            AssertionError("SimC revision should not redownload Wago")))
        self.assertEqual(second["network_calls_by_stage"],0,second)
        self.assertEqual(second["quality_source_stage"]["status"],"REUSED_VERIFIED")
        self.assertNotEqual(second["candidate_path"],first["candidate_path"])

    def test_quality_item_id_must_match_actual_physical_item(self):
        wrong=csv_bytes(("ID","Rank","SpellItemEnchantmentID","ItemID",
                         "CraftingDataID"),[
            {"ID":1,"Rank":14,"SpellItemEnchantmentID":8025,
             "ItemID":244014,"CraftingDataID":3829}])
        result=v583.collect(**self.args,transport=lambda *_, **__:Resp(wrong))
        self.assertEqual(result["counts"]["highest_simc_candidate_linked"],0,result)
        self.assertEqual(result["counts"]["highest_simc_candidate_missing_ids"],[8025])

    def test_failed_wago_request_counts_attempt_and_keeps_optional_pending(self):
        attempts=[]
        def broken(request,timeout):
            attempts.append(request.full_url)
            raise OSError("simulated offline source outage")
        result=v583.collect(**self.args,transport=broken)
        self.assertEqual(result["status"],"PERMANENT_ENCHANT_SOURCE_PENDING")
        self.assertEqual(result["network_calls_by_stage"],1)
        self.assertEqual(len(attempts),1)
        self.assertFalse(result["environment_ready"])

    def test_additional_scope_does_not_depend_on_token_prefix_or_name(self):
        row={"enchant_id":7939,"quality_rank":2,
             "item_class":4,"inventory_type_mask":0x80,
             "item_subclass_mask":0x1e,
             "simc_token":"bright_linen_spellthread"}
        armor=v583._additional_scope_from_original_simc([row])
        self.assertEqual(armor["scope"],
                         "DPS_EQUIPMENT_PERMANENT_CANDIDATE_UNADMITTED")
        self.assertEqual(armor["gear_kind"],"armor")
        weapon=v583._additional_scope_from_original_simc([
            {**row,"item_class":2,"inventory_type_mask":0,
             "item_subclass_mask":0x4000c,
             "simc_token":"farstriders_hawkeye"}])
        self.assertEqual(weapon["gear_kind"],"weapon")
        tool=v583._additional_scope_from_original_simc([
            {**row,"item_class":19,"inventory_type_mask":0x20000000,
             "simc_token":"enchant_tool__haranir_finesse"}])
        self.assertEqual(tool["scope"],"PROFESSION_TOOL_OUTSIDE_DPS_EQUIPMENT")
        self.assertEqual(v583._additional_scope_from_original_simc([])["scope"],
                         "SIMC_PERMANENT_EQUIPMENT_SCOPE_UNRESOLVED")

    def test_additional_same_expansion_gear_is_discovered_not_auto_approved(self):
        # Reuse exactly the source-only v583 chain; no extra CSV GET/Native.
        row={"enchant_id":7939,"quality_rank":2,"item_class":4,
             "inventory_type_mask":0x80,"item_subclass_mask":0x1e,
             "simc_token":"bright_linen_spellthread"}
        self.rows.append(row)
        # Patch returns list by reference. Appending to self.rows also extends
        # generated["rows"], while the old enchant_ highest subset remains 8025.
        root=self.root
        def write(name,fields,rows):
            (root/name).write_bytes(csv_bytes(fields,rows))
        write("wago/Item.csv",("ID","ClassID","SubclassID"),[
            {"ID":244014,"ClassID":8,"SubclassID":0},
            {"ID":244015,"ClassID":8,"SubclassID":0},
            {"ID":240157,"ClassID":8,"SubclassID":8},
            {"ID":244016,"ClassID":8,"SubclassID":0}])
        write("wago/ItemSparse.csv",("ID","ExpansionID","Display_lang"),[
            {"ID":244014,"ExpansionID":11,"Display_lang":"Lesser enchant"},
            {"ID":244015,"ExpansionID":11,"Display_lang":"Greater enchant"},
            {"ID":240157,"ExpansionID":11,"Display_lang":"Any localized spellthread"},
            {"ID":244016,"ExpansionID":10,"Display_lang":"Old enchant"}])
        write("source/fake_ItemXItemEffect.csv",("ItemID","ItemEffectID"),[
            {"ItemID":244014,"ItemEffectID":100},
            {"ItemID":244015,"ItemEffectID":101},
            {"ItemID":240157,"ItemEffectID":103}])
        write("source/fake_ItemEffect.csv",("ID","SpellID","TriggerType"),[
            {"ID":100,"SpellID":777,"TriggerType":0},
            {"ID":101,"SpellID":778,"TriggerType":0},
            {"ID":103,"SpellID":780,"TriggerType":0}])
        write("source/fake_SpellEffect.csv",
              ("SpellID","Effect","EffectIndex","EffectMiscValue_0","DifficultyID"),[
            {"SpellID":777,"Effect":301,"EffectIndex":0,
             "EffectMiscValue_0":3828,"DifficultyID":0},
            {"SpellID":778,"Effect":301,"EffectIndex":0,
             "EffectMiscValue_0":3829,"DifficultyID":0},
            {"SpellID":780,"Effect":53,"EffectIndex":0,
             "EffectMiscValue_0":7939,"DifficultyID":0}])
        raw=root/"source"/"test_quality_extra.csv"
        raw.write_bytes(self.quality)
        result=v583.join_existing_sources(
            item=root/"wago/Item.csv",sparse=root/"wago/ItemSparse.csv",
            crafting=root/"wago/CraftingData.csv",
            relation=root/"source/fake_ItemXItemEffect.csv",
            effect=root/"source/fake_ItemEffect.csv",
            spell_effect=root/"source/fake_SpellEffect.csv",
            quality=raw,simc_enchants=root/"source/fake_permanent_enchant.inc",
            build=BUILD,expansion_id=EXPANSION)
        self.assertEqual(result["all_rank_simc_id_linked"],2)
        self.assertEqual(result["additional_dps_gear_candidate_count"],1)
        self.assertEqual(result["additional_dps_gear_highest_source_rank_candidate_ids"],
                         [7939])
        self.assertEqual(result["additional_wago_id_classification_counts"],{
            "DPS_EQUIPMENT_PERMANENT_CANDIDATE_UNADMITTED":1})
        x=result["additional_enchants_unadmitted"][0]
        self.assertEqual(x["physical_items"][0]["item_id"],240157)
        self.assertFalse(x["ui_selectable"])


if __name__=="__main__":
    unittest.main()
