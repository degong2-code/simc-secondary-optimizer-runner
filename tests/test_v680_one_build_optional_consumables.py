"""v680: one-build installed source registry, no guessed SimC tokens or Native."""
from __future__ import annotations

import copy
import io
import json
import tempfile
import pathlib
import shutil
import subprocess
import sys
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v212_environment_manifest as manifest
import v218_v098_profile_stage_adapter as profile
import v106_user_session_controller as sessions
import v280_consumable_item_use_spell_source as wago_effects
import v216_environment_build_coordinator as fresh_build

BUILD="12.1.5.70961"
REV="a"*40
SHA="b"*64


def exact_row(kind,item_id,token,quality,effect,condition="normal"):
    return {"kind":kind,"physical_item_id":item_id,
            "simc_input_token":token,"crafting_quality":quality,
            "effect_identity":effect,
            "use_condition_identity":condition,
            "name_enUS":"Example consumable "+str(item_id)}


class OneBuildOptionalChoices(unittest.TestCase):
    def source(self,rows):
        return {"game_build":BUILD,"simc_revision":REV,
                "source_receipt_sha256":SHA,"rows":rows}

    def registry(self,rows):
        return manifest.project_fresh_optional_consumables(
            game_build=BUILD,simc_revision=REV,source=self.source(rows))

    def test_same_effect_and_use_condition_best_quality_is_only_one_option(self):
        # Same spell/use family: lower rank excluded. Different effects and
        # different use conditions remain independently selectable.
        rows=[
            exact_row("food",11,"food_a_1",1,"spell:111"),
            exact_row("food",12,"food_a_3",3,"spell:111"),
            exact_row("food",13,"food_b_2",2,"spell:222"),
            exact_row("food",14,"food_a_4",4,"spell:111","arena"),
            exact_row("potion",15,"potion_x_3",3,"spell:333")
        ]
        built=self.registry(rows)
        self.assertTrue(manifest.verify_fresh_optional_consumables(
            built,game_build=BUILD,simc_revision=REV))
        f=built["categories"]["food"]
        self.assertEqual(
            [x["item_id"] for x in f["options"]],[12,13,14])
        self.assertEqual(f["status"],"SOURCE_BACKED_OPTIONS_READY")
        self.assertEqual([x["item_id"] for x in
                          built["categories"]["potion"]["options"]],[15])
        self.assertEqual(built["source_receipt_sha256"],SHA)
        self.assertTrue(built["optional_items_do_not_block_base"])

    def test_same_effect_equal_quality_ambiguous_is_not_auto_picked(self):
        # Do not pick either a tie or a guessed text token.
        built=self.registry([
            exact_row("food",11,"food_a_3",3,"spell:111"),
            exact_row("food",12,"food_b_3",3,"spell:111")])
        self.assertEqual(built["categories"]["food"]["options"],[])
        self.assertEqual(built["categories"]["food"]["status"],
                         "SOURCE_OPTIONS_UNAVAILABLE")
        with self.assertRaisesRegex(manifest.EnvironmentBlocked,
                                     "OPTIONAL_SOURCE_EXACT"):
            self.registry([exact_row("food",11,"source_default",3,"s")])
        with self.assertRaisesRegex(manifest.EnvironmentBlocked,
                                     "OPTIONAL_SOURCE_SAME_BUILD"):
            manifest.project_fresh_optional_consumables(
                game_build=BUILD,simc_revision=REV,
                source={**self.source([]),"game_build":"12.1.5.70575"})

    def test_conflicting_optional_parser_tokens_do_not_block_base(self):
        rows=[
            exact_row("food",33,"same_token_3",3,"spell:33"),
            exact_row("food",34,"same_token_3",3,"spell:34"),
            exact_row("potion",35,"safe_potion_3",3,"spell:35")]
        result=self.registry(rows)
        self.assertTrue(manifest.verify_fresh_optional_consumables(
            result,game_build=BUILD,simc_revision=REV))
        self.assertEqual(result["categories"]["food"]["options"],[])
        self.assertEqual(result["categories"]["potion"]["options"][0][
                         "simc_token"],"safe_potion_3")
        self.assertTrue(result["optional_items_do_not_block_base"])

    def test_source_missing_keeps_base_and_original_disabled_default(self):
        built=manifest.project_fresh_optional_consumables(
            game_build=BUILD,simc_revision=REV)
        self.assertTrue(manifest.verify_fresh_optional_consumables(
            built,game_build=BUILD,simc_revision=REV))
        self.assertEqual(built["categories"]["food"]["status"],
                         "SOURCE_NOT_YET_RESOLVED")
        with mock.patch.object(profile.installed_manifest,
                               "verify_fresh_installed_environment",
                               return_value=True):
            expected=profile.current_season_approved_optional_choices(
                {"installed_optional_consumables":built})
        self.assertEqual(expected,{"food":["source_default"],
                                   "potion":["source_default"],
                                   "augmentation":["source_default"]})
        user=sessions.user_scenario(
            sessions.standard_controls(("mage","frost")))
        self.assertEqual(profile._verified_fresh_season_consumables(user),
                         {"food":"disabled","potion":"disabled",
                          "augmentation":"disabled"})

    def test_ui_and_runtime_consumers_share_same_installed_projection(self):
        built=self.registry([
            exact_row("food",101,"food_1",1,"spell:11"),
            exact_row("food",102,"food_3",3,"spell:11"),
            exact_row("potion",103,"potion_3",3,"spell:22")])
        doc={"installed_optional_consumables":built}
        with mock.patch.object(profile.installed_manifest,
                               "verify_fresh_installed_environment",
                               return_value=True):
            approved=profile.current_season_approved_optional_choices(doc)
            self.assertEqual(approved["food"],["source_default","food_3"])
            self.assertEqual(approved["potion"],["source_default","potion_3"])
            controls=sessions.standard_controls(("mage","frost"))
            controls["consumable_choices"]={
                **controls["consumable_choices"],
                "food":"food_3","potion":"potion_3"}
            user=sessions.user_scenario(controls)
            self.assertEqual(
                profile._verified_fresh_season_consumables(
                    user,installed_environment=doc),
                {"food":"food_3","potion":"potion_3",
                 "augmentation":"disabled"})
            invalid=copy.deepcopy(user)
            invalid["consumable_choices"]["food"]="food_1"
            with self.assertRaisesRegex(
                    Exception,"FRESH_SEASON_OPTIONAL_CONSUMABLE_NOT_INSTALLED"):
                profile._verified_fresh_season_consumables(
                    invalid,installed_environment=doc)

    def test_actual_user_ui_consumes_only_the_exact_installed_source(self):
        node=shutil.which("node")
        if node is None:
            self.skipTest("node is not installed")
        script=r"""
const fs=require('fs'),assert=require('assert');
const raw=fs.readFileSync(process.argv[1],'utf8');
const begin=raw.indexOf('function syncInstalledOptionalConsumables(catalog){');
const end=raw.indexOf('function renderSeasonOptionCatalog(catalog)',begin);
assert(begin>=0&&end>begin);
const nodes={};
for(const name of ['food','potion','augmentation'])
 nodes[name]={value:'source_default',options:[],textContent:''};
const state={options:{current_season_product_choices:null},
 defaultOptionalChoices:{food:['source_default'],potion:['source_default'],
  augmentation:['source_default']}};
const $=name=>nodes[name];
const field=name=>nodes[name].value;
const populateSelect=(name,allowed,label)=>{
 nodes[name].options=allowed.map(token=>({value:token,label:label(token)}));
 nodes[name].value=allowed[0];
};
const refreshDefaultConsumableSummaries=()=>{};
const f=new Function('state','$','field','populateSelect',
 'refreshDefaultConsumableSummaries',
 raw.slice(begin,end)+'return syncInstalledOptionalConsumables;'
)(state,$,field,populateSelect,refreshDefaultConsumableSummaries);
const sha='a'.repeat(64);
const exact={
 source_scope:'VERIFIED_INSTALLED_V212_OPTION_CATALOG',
 installed_manifest_sha256:sha,
 installed_optional_consumable_choices:{
  schema:'v113_current_season_optional_consumables_v1',
  installed_manifest_sha256:sha,
  source_default_simc_token:'disabled',
  food:['source_default','food_3'],
  potion:['source_default','potion_3'],
  augmentation:['source_default'],
  items:[
    {kind:'food',simc_token:'food_3',label:'영웅의 식사'},
    {kind:'potion',simc_token:'potion_3',label:'특급 전투 물약'}]
 }
};
f(exact);
assert.deepStrictEqual(nodes.food.options.map(x=>x.value),['source_default','food_3']);
assert(nodes.food.options[1].label==='영웅의 식사');
assert.deepStrictEqual(state.options.current_season_product_choices.potion,
 ['source_default','potion_3']);
nodes.food.value='food_3';
f({...exact,installed_manifest_sha256:'b'.repeat(64)});
assert.deepStrictEqual(nodes.food.options.map(x=>x.value),['source_default']);
assert(nodes.food.value==='source_default');
console.log('V680_OPTION_SAME_INSTALLED_SOURCE_UI_PASS');
"""
        p=subprocess.run([node,"-e",script,
                          str(ROOT/"runner/webui/app.js")],
                         cwd=ROOT,capture_output=True,text=True,timeout=15)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn("V680_OPTION_SAME_INSTALLED_SOURCE_UI_PASS",p.stdout)

    def test_zero_new_http_optional_use_spell_source_reuses_original_wago(self):
        class Response(io.BytesIO):
            status=200
        relation=b"ItemID,ItemEffectID\n201,11\n202,12\n"
        effects=b"ID,SpellID,TriggerType\n11,5001,0\n12,6002,0\n"
        source={
            "schema":"v190_same_build_consumable_item_candidates_v1",
            "source":{"wago_snapshot_build":BUILD},
            "automatic_ui_promotion":False,
            "items":[{
                "item_id":201,"kind":"food","name_enUS":"Royal Roast",
                "ui_selectable":False,"simc_token":"UNRESOLVED"},{
                "item_id":202,"kind":"potion",
                "name_enUS":"Potion of Recklessness",
                "ui_selectable":False,"simc_token":"UNRESOLVED"}]
        }
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            (root/"source").mkdir()
            (root/"source/v254_ItemXItemEffect.csv").write_bytes(relation)
            candidate=root/"source/v282_v190_items.json"
            candidate.write_text(json.dumps(source),encoding="utf8")
            gear={"source_stage":{"status":"EXECUTED_AND_SEALED",
                "receipt_sha256":"1"*64,
                "output_paths":{"effect":"source/v254_ItemXItemEffect.csv"}}}
            consumables={"candidate_path":str(candidate),"source_stage":{
                "status":"EXECUTED_AND_SEALED","receipt_sha256":"2"*64,
                "stage_id":"fresh-v189-v190-consumable-physical-other"}}
            fetched=[]
            def original_transport(req,timeout):
                fetched.append(req.full_url)
                return Response(effects)
            old=wago_effects.collect(
                stage_root=root,build=BUILD,fresh_gear=gear,
                consumables=consumables,transport=original_transport)
            self.assertEqual(old["status"],
                "ITEM_USE_SPELL_SOURCE_JOINED_UNADMITTED")
            fresh=wago_effects.collect_optional_food_potion_from_existing(
                stage_root=root,build=BUILD,fresh_gear=gear,
                consumables=consumables,item_effect_stage=old)
            self.assertEqual(fresh["status"],
                "FOOD_POTION_WAGO_USE_SPELLS_SOURCE_READY",fresh)
            doc=json.loads(pathlib.Path(fresh["candidate_path"]).read_text())
            self.assertEqual([r["on_use_spell_ids"] for r in doc["items"]],
                             [[5001],[6002]])
            self.assertFalse(fresh["user_choices_installed"])
            self.assertEqual(fresh["network_calls_by_stage"],0)
            self.assertEqual(fresh["native_calls"],0)
            reused=wago_effects.collect_optional_food_potion_from_existing(
                stage_root=root,build=BUILD,fresh_gear=gear,
                consumables=consumables,item_effect_stage=old)
            self.assertEqual(reused["source_stage"]["status"],
                             "REUSED_VERIFIED")
            self.assertEqual(len(fetched),1,
                             "The original v280 fetched once; optional bridge none")

    def test_one_original_environment_build_links_wago_and_pinned_simc_source(self):
        """Synthetic zero-source seam: Wago IDs/spells + SimC handlers/DBC.

        This tests generic source wiring, not a real 70961 SimC item
        acceptance receipt or permission to invent an effect family.
        """
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            (root/"source").mkdir()
            observed={"schema":"v680_optional_food_potion_wago_source_v1",
                "game_build":BUILD,"source_only":True,
                "items":[
                    {"item_id":201,"kind":"food","on_use_spell_ids":[5001],
                     "source_status":"EXACT_DB2_ITEM_TO_ON_USE_SPELL_SOURCE_ONLY"},
                    {"item_id":202,"kind":"food","on_use_spell_ids":[5001],
                     "source_status":"EXACT_DB2_ITEM_TO_ON_USE_SPELL_SOURCE_ONLY"},
                    {"item_id":203,"kind":"potion","on_use_spell_ids":[6002],
                     "source_status":"EXACT_DB2_ITEM_TO_ON_USE_SPELL_SOURCE_ONLY"}]}
            src=root/"source"/"wago-optional.json"
            src.write_text(json.dumps(observed),encoding="utf8")
            handlers={"schema":fresh_build.simc_effect_candidates.SCHEMA,
                      "source":{"commit":REV},
                      "candidates":{
                        "food":[{"spell_ids":[5001],
                                 "handler":"consumables::food_a",
                                 "implemented":True,
                                 "minimum_game_version":[12,0,0]}],
                        "potion":[{"spell_ids":[6002],
                                   "handler":"consumables::potion_a",
                                   "implemented":True,
                                   "minimum_game_version":[12,0,0]}]}}
            h=root/"source"/"simc-handlers.json"
            h.write_text(json.dumps(handlers),encoding="utf8")
            collected={
                "expected_game_build":BUILD,
                "fresh_optional_food_potion_wago_effects":{
                    "status":"FOOD_POTION_WAGO_USE_SPELLS_SOURCE_READY",
                    "candidate_path":str(src),
                    "source_stage":{"receipt_sha256":"1"*64}},
                "fresh_food_potion_item_sources":{
                    "simc_effect_source_receipt_path":str(h),
                    "source_stage":{"receipt_sha256":"3"*64}},
                "fresh_lazy_full_pinned_simc_item_source":{
                    "source_dir":str(root),
                    "receipt_sha256":"4"*64}}
            comp={"stage_root":str(root),"simc_revision":REV}
            meta={"game_build":BUILD,"simc_revision":REV,
                "source_receipt_sha256":"2"*64,
                "selection_mode":"EXACT_REQUESTED_IDS",
                "items":[
                    {"item_id":201,"name":"Royal Roast",
                     "class_id":0,"subclass_id":5,"inventory_type":0,
                     "crafting_quality":1},
                    {"item_id":202,"name":"Royal Roast",
                     "class_id":0,"subclass_id":5,"inventory_type":0,
                     "crafting_quality":3},
                    {"item_id":203,"name":"Potion of Recklessness",
                     "class_id":0,"subclass_id":1,"inventory_type":0,
                     "crafting_quality":3}]}
            with mock.patch.object(fresh_build.simc_item_metadata,
                                   "from_seed",return_value=meta) as lookup:
                source=fresh_build._fresh_v680_source_owned_food_potion(
                    collected=collected,compilation=comp)
            lookup.assert_called_once_with(
                directory=str(root),item_ids=[201,202,203])
            # Same sealed Wago/SimC identities: reuse the compact output,
            # never read the large pinned item_data.inc a second time.
            with mock.patch.object(fresh_build.simc_item_metadata,
                                   "from_seed",
                                   side_effect=AssertionError("NO_REPARSE")):
                again=fresh_build._fresh_v680_source_owned_food_potion(
                    collected=collected,compilation=comp)
            self.assertEqual(source,again)
            self.assertEqual(len(source["rows"]),3)
            ready=manifest.project_fresh_optional_consumables(
                game_build=BUILD,simc_revision=REV,source=source)
            self.assertEqual(
                [r["item_id"] for r in
                 ready["categories"]["food"]["options"]],[202])
            self.assertEqual(
                [r["item_id"] for r in
                 ready["categories"]["potion"]["options"]],[203])
            self.assertTrue(ready["optional_items_do_not_block_base"])

    def test_no_native_and_no_separate_approval_engine(self):
        with mock.patch("subprocess.Popen",
                        side_effect=AssertionError("NO_NATIVE")):
            self.registry([exact_row("potion",22,"potion_3",3,"spell:22")])
        code=(ROOT/"runner"/"v216_environment_build_coordinator.py").read_text("utf8")
        self.assertIn("source_owned_optional_consumables",code)
        self.assertIn("source_optional_consumables=compilation.get(",code)
        api=(ROOT/"runner"/"v113_local_web_api.py").read_text("utf8")
        self.assertIn("installed_optional_consumable_choices",api)
        self.assertIn("_v680_preflight_optional_consumables",api)


if __name__=="__main__":
    unittest.main()
