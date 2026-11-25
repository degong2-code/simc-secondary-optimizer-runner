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
import v113_local_web_api as web_api

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

    def test_70961_simc_parser_spelling_drops_punctuation_instead_of_underscores(self):
        # Same-revision consumable.cpp/util.cpp: punctuation is removed,
        # spaces are underscores and only a one-digit rank is parsed.
        token=fresh_build.optional_source_join.candidate_token
        self.assertEqual(token("Sweet-and-Sour Skewers",3),
                         "sweetandsour_skewers_3")
        self.assertEqual(token("Loa's Gathering",2),"loas_gathering_2")
        self.assertEqual(token("Mana-Infused Stew",1),"manainfused_stew_1")
        self.assertIsNone(token("SimC + symbol",3))
        self.assertIsNone(token("A two-digit rank",12))
        self.assertIsNone(token("Unranked Name 1",0))
        self.assertEqual(fresh_build.optional_source_join.parser_name_stem(
            "Old Royal Roást"),"old_royal_rost")
        # Spelling is only a candidate: actual SimC input acceptance and
        # numerical quality dominance remain distinct, unproven boundaries.

    def test_same_effect_and_use_condition_requires_numeric_quality_comparison(self):
        # Rank alone cannot prove dominance. Hold that family, while
        # different effects and different use scopes remain selectable.
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
            [x["item_id"] for x in f["options"]],[13,14])
        self.assertEqual(f["quality_comparison_pending_item_ids"],[11,12])
        self.assertEqual(f["status"],"SOURCE_BACKED_OPTIONS_READY")
        self.assertEqual([x["item_id"] for x in
                          built["categories"]["potion"]["options"]],[15])
        self.assertEqual(built["source_receipt_sha256"],SHA)
        self.assertTrue(built["optional_items_do_not_block_base"])

    def test_simc_consumable_substring_parser_omits_shadowed_known_item(self):
        # Actual same-revision consumable.cpp uses str_in_str_ci(full, needle).
        # A shorter name can match another item of the SAME subclass/quality
        # even when effect identities and exact tokens differ.
        built=self.registry([
            exact_row("food",201,"royal_roast_3",3,"spell:111"),
            exact_row("food",202,"impossibly_royal_roast_3",3,"spell:222"),
            exact_row("food",203,"royal_roast_2",2,"spell:333"),
            exact_row("potion",204,"other_potion_3",3,"spell:444")])
        options=built["categories"]["food"]["options"]
        self.assertEqual([r["item_id"] for r in options],[202,203])
        self.assertEqual([r["item_id"] for r in
                          built["categories"]["potion"]["options"]],[204])
        self.assertTrue(built["optional_items_do_not_block_base"])
        # This guard is deliberately limited to source-known rows.
        # Do not claim complete SimC DBC uniqueness or Native acceptance.

    def test_v779_ordered_source_projection_does_not_repeat_unordered_guard(self):
        rows=[exact_row("food",201,"royal_roast",0,"spell:111"),
              exact_row("food",202,"old_royal_roast",0,"spell:222")]
        source={**self.source(rows),
                "parser_first_match_item_ids":{"201":201,"202":202},
                "parser_shadowed_item_ids":[]}
        projected=manifest.project_fresh_optional_consumables(
            game_build=BUILD,simc_revision=REV,source=source)
        self.assertEqual([r["item_id"] for r in
                          projected["categories"]["food"]["options"]],[201,202])
        source["parser_first_match_item_ids"]["201"]=202
        with self.assertRaisesRegex(manifest.EnvironmentBlocked,
                                    "OPTIONAL_SOURCE_FIRST_MATCH_SHADOW_CONFLICT"):
            manifest.project_fresh_optional_consumables(
                game_build=BUILD,simc_revision=REV,source=source)
        source["parser_shadowed_item_ids"]=[201]
        projected=manifest.project_fresh_optional_consumables(
            game_build=BUILD,simc_revision=REV,source=source)
        self.assertEqual([r["item_id"] for r in
                          projected["categories"]["food"]["options"]],[202])

    def test_v764_unranked_token_can_match_rank_one_but_not_rank_two(self):
        built=self.registry([
            exact_row("food",301,"royal_roast",0,"spell:301"),
            exact_row("food",302,"old_royal_roast_1",1,"spell:302"),
            exact_row("food",303,"other_roast",0,"spell:303"),
            exact_row("food",304,"old_other_roast_2",2,"spell:304")])
        self.assertEqual([r["item_id"] for r in
                          built["categories"]["food"]["options"]],[302,303,304])

    def test_same_effect_equal_quality_ambiguous_is_not_auto_picked(self):
        # Identical parser name/rank is ambiguous; separate names with a
        # shared spell are not automatically the same physical effect.
        separate=self.registry([
            exact_row("food",11,"food_a_3",3,"spell:111"),
            exact_row("food",12,"food_b_3",3,"spell:111")])
        self.assertEqual([r["item_id"] for r in
                          separate["categories"]["food"]["options"]],[11,12])
        built=self.registry([
            exact_row("food",11,"food_a_3",3,"spell:111"),
            exact_row("food",12,"food_a_3",3,"spell:111")])
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

    def test_v775_default_recommendations_require_reviewed_revision_and_exact_menu(self):
        doc={"game_build":BUILD,
             "simc_revision":"9933ffb946fb55b1fa66657b848f519ac19006e1"}
        approved={"food":["source_default","harandar_celebration",
                          "silvermoon_parade","blooming_feast","royal_roast"],
                  "potion":["source_default","lights_potential_2",
                            "potion_of_recklessness_2","liquid_luster_2"]}
        selected=web_api._v775_source_optional_defaults(doc,approved)
        self.assertEqual(len(selected),26)
        self.assertTrue(all(set(row)=={"food","potion"}
                            for row in selected.values()))
        self.assertEqual(selected["mage/frost"],
            {"food":"silvermoon_parade","potion":"potion_of_recklessness_2"})
        self.assertEqual(selected["warlock/affliction"]["potion"],"liquid_luster_2")
        self.assertNotIn("evoker/augmentation",selected)
        self.assertEqual(web_api._v775_source_optional_defaults(
            {**doc,"simc_revision":"a"*40},approved),{})
        self.assertEqual(web_api._v775_source_optional_defaults(
            doc,{"food":["source_default"],"potion":["source_default"]}),{})
        missing=web_api._v775_source_optional_defaults(
            doc,{**approved,"potion":["source_default","lights_potential_2"]})
        self.assertEqual(missing["mage/frost"],{"food":"silvermoon_parade"})

    def test_v777_generic_dbc_default_is_revision_scoped_not_arbitrary_name(self):
        """Exact physical source + generated DBC + reviewed APL input."""
        rev="9933ffb946fb55b1fa66657b848f519ac19006e1"
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            candidates=root/"physical.json"
            handlers=root/"handlers.json"
            ids=[501,502,503,504]
            candidates.write_text(json.dumps({
                "game_build":BUILD,"source_only":True,
                "items":[{"item_id":i,"kind":"potion","on_use_spell_ids":[i+1000],
                    "source_status":"EXACT_DB2_ITEM_TO_ON_USE_SPELL_SOURCE_ONLY"}
                    for i in ids]}),encoding="utf8")
            collected={
                "expected_game_build":BUILD,
                "fresh_optional_food_potion_wago_effects":{
                    "status":"FOOD_POTION_WAGO_USE_SPELLS_SOURCE_READY",
                    "candidate_path":str(candidates),
                    "source_stage":{"receipt_sha256":"1"*64}},
                "fresh_food_potion_item_sources":{
                    "simc_effect_source_receipt_path":str(handlers),
                    "source_stage":{"receipt_sha256":"2"*64}},
                "fresh_lazy_full_pinned_simc_item_source":{
                    "source_dir":str(root),"receipt_sha256":"3"*64}}
            for revision in (rev,REV):
                handlers.write_text(json.dumps({
                    "schema":fresh_build.simc_effect_candidates.SCHEMA,
                    "source":{"commit":revision},"candidates":{}}),encoding="utf8")
                meta={"game_build":BUILD,"simc_revision":revision,
                      "source_receipt_sha256":"4"*64,
                      "selection_mode":"EXACT_REQUESTED_IDS_ALLOW_MISSING",
                      "items":[{"item_id":i,"name":name,
                           "class_id":0,"subclass_id":1,"inventory_type":0,
                           "crafting_quality":rank}
                        for i,name,rank in (
                           (501,"Light's Potential",2),
                           (502,"Random Mana Potion",2),
                           (503,"Light's Potential",1),
                           (504,"Liquid Luster",2))]}
                meta["consumable_parser_name_rows"]=[
                    {k:row[k] for k in ("item_id","name","subclass_id",
                                        "crafting_quality")}
                    for row in meta["items"]]
                with mock.patch.object(fresh_build.simc_item_metadata,
                                      "from_seed",return_value=meta):
                    source=fresh_build._fresh_v680_source_owned_food_potion_uncached(
                        collected=collected,compilation={
                            "stage_root":str(root),"simc_revision":revision})
                self.assertEqual([row["physical_item_id"] for row in source["rows"]],
                                 [501,504] if revision==rev else [])
                if revision==rev:
                    self.assertEqual(source["rows"][0]["effect_identity"],
                                     "simc:reviewed_apl_input:spell:1501")
                    self.assertEqual(source["rows"][0]["simc_input_token"],
                                     "lights_potential_2")

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
const a=raw.indexOf('function applyOptionalAutoDefaults(){');
const b=raw.indexOf('function refreshDefaultConsumableSummaries()',a);
assert(a>=0&&b>a);
nodes.spec={value:'mage/frost'};
const apply=new Function('state','$','field',
 raw.slice(a,b)+'return applyOptionalAutoDefaults;')(state,$,field);
const refreshDefaultConsumableSummaries=()=>apply();
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
  recommended_tokens_by_spec:{'mage/frost':{food:'food_3',potion:'potion_3'}},
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
state.optionalAuto={food:true,potion:true};
f(exact);
assert(nodes.food.value==='food_3'&&nodes.potion.value==='potion_3');
state.optionalAuto.food=false;
nodes.food.value='source_default';
f(exact);
assert(nodes.food.value==='source_default'&&nodes.potion.value==='potion_3');
nodes.spec.value='mage/fire';
apply();
assert(nodes.potion.value==='source_default');
nodes.spec.value='mage/frost';
apply();
assert(nodes.potion.value==='potion_3'&&nodes.food.value==='source_default');
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
            # Real new raw-source seal, not a fabricated effect output
            # on the derived gear receipt.
            from urllib.parse import urlencode
            from runner import v217_stage_execution_engine as stages
            raw_path=root/"source/raw_gear_effect.csv"
            raw_stage=stages.execute_stage(
                root=root,stage_id="season-gear-effect-raw",
                stage_version="same-build-raw-v1",
                inputs={"game_build":BUILD,"source_url":
                    "https://wago.tools/db2/ItemXItemEffect/csv?"+urlencode(
                        {"build":BUILD,"locale":"enUS"})},
                outputs={"raw":"source/raw_gear_effect.csv"},
                execute=lambda:raw_path.write_bytes(relation))
            gear={"source_stage":{"status":"EXECUTED_AND_SEALED",
                "receipt_sha256":"1"*64,
                "output_paths":{"candidate":"source/catalog.json"}},
                "item_effect_relation_source_receipt_sha256":raw_stage["receipt_sha256"]}
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
            raw_path.write_bytes(relation+b"tampered")
            blocked=wago_effects.collect(
                stage_root=root,build=BUILD,fresh_gear=gear,
                consumables=consumables,transport=original_transport)
            self.assertEqual(blocked["status"],"ITEM_USE_SPELL_SOURCE_PENDING")
            self.assertEqual(blocked["reason"],"STAGE_OUTPUT_HASH_MISMATCH")
            self.assertEqual(len(fetched),1)

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
                     "source_status":"EXACT_DB2_ITEM_TO_ON_USE_SPELL_SOURCE_ONLY"},
                    {"item_id":204,"kind":"potion","on_use_spell_ids":[6002],
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
                "selection_mode":"EXACT_REQUESTED_IDS_ALLOW_MISSING",
                "missing_item_ids":[204],
                "source_matched_item_count":3,
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
            meta["consumable_parser_name_rows"]=[
                {k:row[k] for k in ("item_id","name","subclass_id","crafting_quality")}
                for row in meta["items"]]
            with mock.patch.object(fresh_build.simc_item_metadata,
                                   "from_seed",return_value=meta) as lookup:
                source=fresh_build._fresh_v680_source_owned_food_potion(
                    collected=collected,compilation=comp)
            lookup.assert_called_once_with(
                directory=str(root),item_ids=[201,202,203,204],
                allow_missing=True,include_consumable_parser_names=True)
            # Same sealed Wago/SimC identities: reuse the compact output,
            # never read the large pinned item_data.inc a second time.
            with mock.patch.object(fresh_build.simc_item_metadata,
                                   "from_seed",
                                   side_effect=AssertionError("NO_REPARSE")):
                again=fresh_build._fresh_v680_source_owned_food_potion(
                    collected=collected,compilation=comp)
            self.assertEqual(source,again)
            self.assertEqual(len(source["rows"]),3,
                             "one missing SimC DBC item must not erase three")
            self.assertEqual(
                sorted(r["physical_item_id"] for r in source["rows"]),
                [201,202,203])
            ready=manifest.project_fresh_optional_consumables(
                game_build=BUILD,simc_revision=REV,source=source)
            self.assertEqual(ready["categories"]["food"]["options"],[])
            self.assertEqual(ready["categories"]["food"][
                "quality_comparison_pending_item_ids"],[201,202])
            self.assertEqual(
                [r["item_id"] for r in
                 ready["categories"]["potion"]["options"]],[203])
            self.assertTrue(ready["optional_items_do_not_block_base"])
            # A generated DBC item outside the Wago active-season list
            # can still shadow the new option in SimC's substring parser.
            # The name-only index is transient; the sealed projection
            # excludes that item without discarding independent options.
            # A later matching name cannot shadow the earlier exact row.
            meta["consumable_parser_name_rows"].append({
                "item_id":999,"name":"Old Royal Roast","subclass_id":5,
                "crafting_quality":3})
            with mock.patch.object(fresh_build.simc_item_metadata,
                                   "from_seed",return_value=meta):
                later=fresh_build._fresh_v680_source_owned_food_potion_uncached(
                    collected=collected,compilation=comp)
            self.assertEqual(later["parser_shadowed_item_ids"],[])
            self.assertEqual(later["parser_first_match_item_ids"]["202"],202)
            # Move the same candidate before the selected item: true shadow.
            meta["consumable_parser_name_rows"].insert(
                0,meta["consumable_parser_name_rows"].pop())
            with mock.patch.object(fresh_build.simc_item_metadata,
                                   "from_seed",return_value=meta) as scan:
                shadowed=fresh_build._fresh_v680_source_owned_food_potion_uncached(
                    collected=collected,compilation=comp)
            scan.assert_called_once()
            self.assertEqual(
                sorted(r["physical_item_id"] for r in shadowed["rows"]),
                [201,202,203])
            self.assertEqual(shadowed["parser_shadowed_item_ids"],[202])
            self.assertEqual(shadowed["parser_first_match_item_ids"]["202"],999)
            projected=manifest.project_fresh_optional_consumables(
                game_build=BUILD,simc_revision=REV,source=shadowed)
            self.assertEqual(projected["categories"]["food"]["options"],[],
                             "Do not replace a shadowed top quality with lower rank")
            self.assertEqual([r["item_id"] for r in
                             projected["categories"]["potion"]["options"]],[203])

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
