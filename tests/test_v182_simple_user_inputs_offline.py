"""v182: user-friendly controls, source-first gear, no SimC Native."""
import json,pathlib,sys,tempfile,unittest
from unittest import mock
from fastapi.testclient import TestClient
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v108_native_consumable_inputs as consumables
import v106_user_session_controller as sessions
import v098_target_user_scenario_bootstrap as bootstrap
import v167_product_season_gear_adapter as seasons
import v113_local_web_api as web

class SimpleUserInputs(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=pathlib.Path(tmp.name)
        self.binary=self.root/"NO_NATIVE";self.binary.write_bytes(b"NO_ACTUAL_SIMC")
        self.revision="7bc10711b5"

    def test_all_26_weapon_forms_disable_incompatible_offhand(self):
        doc=seasons.public_options(seasons.read())
        self.assertEqual(len(doc["weapon_forms"]),26)
        self.assertEqual(doc["weapon_forms"]["mage/frost"],"one_hand_frill")
        self.assertEqual(doc["weapon_forms"]["warrior/fury"],"dual_two_hand")
        for key,form in doc["weapon_forms"].items():
            cl,sp=key.split("/")
            controls=sessions.standard_controls((cl,sp))
            controls["oil_hands"]=["main_hand","off_hand"]
            if form in sessions.DUAL_FORMS:
                self.assertEqual(len(sessions.user_scenario(controls)["oil_hands"]),2)
            else:
                with self.assertRaisesRegex(sessions.SessionBlocked,
                    "OIL_HANDS_INCOMPATIBLE_WITH_SOURCE_WEAPON_FORM"):
                    sessions.user_scenario(controls)

    def test_public_selected_slot_contract_matches_backend_for_all_26_specs(self):
        import v143_specialization_contracts as contracts
        doc=seasons.public_options(seasons.read())
        self.assertTrue(contracts.validate_contracts())
        self.assertEqual(set(doc["selected_slot_inventory"]),set(contracts.WEAPON_FORMS))
        for spec,form in doc["weapon_forms"].items():
            actual=doc["selected_slot_inventory"][form]
            self.assertEqual(actual,{slot:list(types) for slot,types in
                                     contracts.selected_slot_inventory(form).items()})
            self.assertEqual(actual["finger1"],[11])
            self.assertEqual(actual["finger2"],[11])
            self.assertEqual(tuple(s for s in actual if s in contracts.WEAPON_SLOTS),
                             contracts.WEAPON_FORMS[form])
        self.assertEqual(doc["selected_slot_inventory"]["ranged"]["main_hand"],[15,26])
        self.assertEqual(doc["selected_slot_inventory"]["one_hand_frill"]["off_hand"],[23])
        self.assertEqual(doc["selected_slot_inventory"]["dual_two_hand"]["off_hand"],[17])
        js=(ROOT/"runner/webui/app.js").read_text("utf8")
        self.assertIn("specialAllowedSlots(item,spec)",js)
        self.assertIn("state.seasonGear?.selected_slot_inventory?.[form]",js)

    def test_four_stat_runes_leave_source_rows_except_fourth(self):
        # An actual pinned-SimC execution rejected the invented name
        # rune_of_versatile_warrior; the source-observed numeric token
        # 136820:1 passed in a one-case corrective Native measurement.
        self.assertEqual(consumables.OMNIUM_ROW4_BY_STAT["row4_vers"],
                         "136820:1")
        self.assertNotIn("rune_of_versatile_warrior",
                         consumables.OMNIUM_ROW4_BY_STAT.values())
        for base in (
          "136822:1/136816:1/136817:1/136815:1/136814:1",
          "136822:1/136817:1/136821:1/136814:1",
          "rune_of_unleashed_fire/rune_of_lynxlike_reflexes/rune_of_lingering/rune_of_burning_haste/rune_of_overload",
        ):
            for stat in consumables.OMNIUM_ROW4_BY_STAT:
                with self.subTest(base=base,stat=stat):
                    updated=consumables.change_row_four(base,stat)
                    self.assertEqual(len(base.split("/")),len(updated.split("/")))
                    self.assertEqual(sum(a!=b for a,b in zip(base.split("/"),updated.split("/"))),int(consumables.OMNIUM_ROW4_BY_STAT[stat] not in base.split("/")))
                    self.assertIn(consumables.OMNIUM_ROW4_BY_STAT[stat],updated)
        with self.assertRaisesRegex(consumables.ConsumableBlocked,
                                    "OMNIUM_SOURCE_ROW4_AMBIGUOUS"):
            consumables.change_row_four("bad:1/invalid:1","row4_crit")

    def test_real_334_season_profile_four_stats_and_distinct_session_ids(self):
        keys=[]
        for stat in consumables.OMNIUM_ROW4_BY_STAT:
            controls=sessions.standard_controls(("mage","frost"))
            controls["consumable_choices"]["omnium_talents"]=stat
            user=sessions.user_scenario(controls)
            sid,_=sessions.session_key(user,self.binary,self.revision,
                                       current_season_product=True)
            keys.append(sid)
            with mock.patch.object(bootstrap.entry.durable,"run") as native:
                prepared=bootstrap.build(user,self.root/stat,self.binary,
                                          self.revision,current_season_product=True)
                native.assert_not_called()
            profile=(self.root/stat/"profile.simc").read_text("utf8")
            self.assertIn(consumables.OMNIUM_ROW4_BY_STAT[stat],profile)
            self.assertEqual(prepared["plan"]["native_limit"],6)
        self.assertEqual(len(set(keys)),4)

    def test_current_season_craft_base_is_source_derived_and_explicit_id_safe(self):
        options=seasons.public_options(seasons.read())["choices"]
        crafts=options["selectable_stat_craft"]
        self.assertEqual(len(crafts),106)
        self.assertTrue(all("class_id" in x and "subclass_id" in x for x in crafts))
        for family in (1,2,3,4):
            self.assertTrue(any(x["class_id"]==4 and
                      x["subclass_id"]==family and x["slot_hint"]=="wrists"
                      for x in crafts))
        self.assertTrue(any(x["item_id"]==239656 for x in crafts))
        controls=sessions.standard_controls(("mage","frost"))
        controls["embellishments"]=[{"slot":"back","item_id":239656,
              "options":{"crafted_stats":"32/36","embellishment":"arcanoweave_lining"}}]
        scenario=sessions.user_scenario(controls)
        self.assertEqual(scenario["embellishments"][0]["item_id"],239656)
        with mock.patch.object(bootstrap.entry.durable,"run") as native:
            prepared=bootstrap.build(scenario,self.root/"craft",
                            self.binary,self.revision,current_season_product=True)
            native.assert_not_called()
        profile=(self.root/"craft"/"profile.simc").read_text("utf8")
        self.assertIn("embellishment=arcanoweave_lining",profile)
        self.assertIn("crafted_stats=32/36",profile)
        js=(ROOT/"runner/webui/app.js").read_text("utf8")
        html=(ROOT/"runner/webui/index.html").read_text("utf8")
        for marker in ('function oilCompatibility()','function chosenCraft(slot,exactItemId=null,token=null)',
            'function selectedGear(nodeId, group)','row4_crit','row4_vers',
            'refreshSpecialSlots()', 'syncCraftRow(row)'):

            self.assertIn(marker,js)
        self.assertIn("label.hidden=isPrivate",js)
        self.assertIn("정확한 제작장비 ItemID (선택 · 비우면 자동)",js)
        self.assertIn('input.type="number";input.min="1";input.max="999999999";',js)
        self.assertIn('class="gear-section gear-trinkets"',html)
        self.assertIn('class="gear-section gear-special"',html)
        self.assertIn('class="gear-section gear-embellishments profile-embellishments"',html)
        self.assertLess(html.index('id="crafted-rows"'),html.index('id="conditions-title"'))
        self.assertIn("Omnium Folio · 4열 스탯",html)


    def test_v852_actual_craft_choice_respects_recipe_item_and_weapon_form(self):
        import shutil,subprocess
        node=shutil.which("node")
        if node is None:self.skipTest("node unavailable")
        script=r"""
const fs=require("fs"),assert=require("assert");
const raw=fs.readFileSync(process.argv[1],"utf8");
const a=raw.indexOf("function craftSlot(");
const b=raw.indexOf("// Restored hidden options",a);
assert(a>=0&&b>a);
let spec="mage/frost";
const state={options:{embellishments:{legacy:{slots:["head"]}}},
 seasonGear:{embellishments:{lining:{item_ids:[102,103,104]}},
 weapon_forms:{"mage/frost":"one_hand_frill","warrior/fury":"dual_two_hand"},
 selected_slot_inventory:{one_hand_frill:{head:[1],main_hand:[13],off_hand:[23]},
 dual_two_hand:{main_hand:[17],off_hand:[17]}},
 choices:{selectable_stat_craft:[
 {item_id:101,class_id:4,subclass_id:1,inventory_type:1,compatible_dps_specs:["mage/frost"]},
 {item_id:102,class_id:4,subclass_id:1,inventory_type:1,compatible_dps_specs:["mage/frost"]},
 {item_id:103,class_id:2,subclass_id:7,inventory_type:13,compatible_dps_specs:["mage/frost"]},
 {item_id:104,class_id:2,subclass_id:8,inventory_type:17,compatible_dps_specs:["warrior/fury"]}]}}};
const choose=Function("state","field","classArmor",raw.slice(a,b)+"\nreturn {chosenCraft,craftMetadata};")(
 state,()=>spec,{mage:1,warrior:4});
assert.equal(choose.chosenCraft("head",null,"lining").item_id,102);
assert.equal(choose.chosenCraft("head",101,"lining"),null);
assert.equal(choose.chosenCraft("main_hand",null,"lining").item_id,103);
assert.equal(choose.chosenCraft("off_hand",null,"lining"),null);
spec="warrior/fury";
assert.equal(choose.chosenCraft("main_hand",null,"lining").item_id,104);
assert.equal(choose.chosenCraft("off_hand",104,"lining").item_id,104);
state.seasonGear.embellishments={};
assert.deepStrictEqual(choose.craftMetadata(),{});
assert.equal(choose.chosenCraft("main_hand",104,"lining"),null);
console.log("V852_EXACT_CRAFT_CHOICE_PASS");
"""
        result=subprocess.run([node,"-e",script,str(ROOT/"runner/webui/app.js")],
                              cwd=ROOT,capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn("V852_EXACT_CRAFT_CHOICE_PASS",result.stdout)

    def test_loot_role_display_and_metadata_only_refresh_preserve_all_items(self):
        import shutil, subprocess
        if shutil.which("node") is None:
            self.skipTest("node unavailable")
        code=r"""
const fs=require("fs"),vm=require("vm"),assert=require("assert");
const src=fs.readFileSync("runner/webui/app.js","utf8");
const a=src.indexOf("function trinketLootRoleLabel(");
const b=src.indexOf("function inlineEquipmentCard(",a);
assert(a>=0&&b>a);
const helpers=vm.runInNewContext(src.slice(a,b)+"\n({trinketLootRoleLabel,mergeTrinketRoleMetadata})");
const make=(status,roles)=>({source:"SAME_BUILD_DB2_EXPLICIT_LOOT_SPEC_OVERRIDE",status,roles});
const tank=make("EXPLICIT_NON_DPS_ROLES_ONLY",["TANK"]);
const shared=make("EXPLICIT_SHARED_WITH_DPS",["HEALER","DPS"]);
const unknown=make("NO_EXPLICIT_OVERRIDE_UNKNOWN",[]);
const items=[{item_id:1,name:"Tank"},{item_id:2,name:"Shared"},{item_id:3,name:"Unknown"}];
assert(helpers.mergeTrinketRoleMetadata(items,{"1":tank,"2":shared,"3":unknown,"4":tank}));
assert.equal(helpers.trinketLootRoleLabel(items[0]),"획득: 탱커");
assert.equal(helpers.trinketLootRoleLabel(items[1]),"획득: 딜러·힐러");
assert.equal(helpers.trinketLootRoleLabel(items[2]),"");
assert.equal(helpers.trinketLootRoleLabel({}),"");
assert.equal(helpers.trinketLootRoleLabel({loot_spec_metadata:make("OVERRIDE_REFERENCE_OR_ROLE_PENDING",["DPS"])}),"");
assert.deepStrictEqual(items.map(x=>x.item_id),[1,2,3]);
assert(!helpers.mergeTrinketRoleMetadata(items,{"1":tank,"2":shared,"3":unknown}));
assert(src.includes("if(rolesChanged||corrections.size)refreshEquipmentSelectionUI();"));
assert(src.includes("gear.loot_spec_source_status===\"TRINKET_LOOT_SPEC_SOURCE_OBSERVED\""));
"""
        completed=subprocess.run(["node","-e",code],cwd=ROOT,
                                 capture_output=True,text=True)
        self.assertEqual(completed.returncode,0,completed.stdout+"\n"+completed.stderr)

    def test_season_source_missing_owner_and_skipped_g_are_diagnostic_only(self):
        # Execute the existing two pure JS projections, without DOM, HTTP,
        # source collection, Native, AI or creating an environment manifest.
        import shutil, subprocess
        if shutil.which("node") is None:
            self.skipTest("node unavailable")
        code=r"""
const fs=require("fs"),vm=require("vm"),assert=require("assert");
const src=fs.readFileSync("runner/webui/app.js","utf8");
function section(start,end,name){
  const a=src.indexOf(start),b=src.indexOf(end,a);
  assert(a>=0&&b>a,"source function boundary "+name);
  // This pure projection now calls a separate UI navigation helper.
  // Keep the diagnostic regression isolated from DOM and navigation logic.
  return vm.runInNewContext(src.slice(a,b)+"\n"+name,
    {seasonBuildRecoveryPlan:()=>null});
}
const receipt=section("function compactSeasonBuildReceipt(",
  "async function copySeasonBuildDiagnostic", "compactSeasonBuildReceipt");
const diagnose=section("function diagnoseSeasonBuildEvidence(",
  "function showSeasonEnvironmentBuild(", "diagnoseSeasonBuildEvidence");
const pending={
  web_environment_scope:{game_build:"13.0.0.70000",target_ilevel:345,
    environment_ready:false,environment_installed:false},
  source_compilation:{
    status:"COLLECTED_COMPILER_INPUTS_PENDING",
    missing:["GENERATED_PERMANENT"],
    compiler_input_impact:{catalog_input_missing:[{
      input:"GENERATED_PERMANENT",existing_producer:"v275",
      catalog_role:"OPTIONAL_PERMANENT_ENCHANT_CATALOG"}]}},
  zero_history_build:{
    default_G_native_skipped_missing_compiler_inputs:["GENERATED_PERMANENT"],
    native_G_status:"G_NATIVE_PENDING",requires:["G_NATIVE_RATING_OBSERVATION_PENDING"]}
};
const report=JSON.parse(receipt(pending));
assert.deepStrictEqual(Array.from(report.compiler_missing),
  ["GENERATED_PERMANENT"]);
assert.deepStrictEqual(JSON.parse(JSON.stringify(report.compiler_missing_existing_producers)),
  [{input:"GENERATED_PERMANENT",existing_producer:"v275"}]);
assert.deepStrictEqual(Array.from(report.default_G_native_skipped_missing_compiler_inputs),
  ["GENERATED_PERMANENT"]);
assert.strictEqual(report.environment_ready,false);
assert.strictEqual(report.verified_budget,null);
assert(diagnose(pending).firstMissing.includes("영구 마부 원본"));
assert.strictEqual(diagnose(pending).compilerMissingCount,1);
const cached=JSON.parse(receipt({
  web_environment_scope:{game_build:"12.1.5.70783",target_ilevel:334,
    environment_ready:true,environment_installed:true}
}));
assert.strictEqual(cached.compiler_missing,null);
assert.strictEqual(cached.compiler_missing_existing_producers,null);
assert.strictEqual(cached.default_G_native_skipped_missing_compiler_inputs,null);
const malicious=JSON.parse(receipt({
  source_compilation:{compiler_input_impact:{catalog_input_missing:[
    {input:"GENERATED_PERMANENT",existing_producer:"/home/secrets/key"}]}}
}));
assert.deepStrictEqual(malicious.compiler_missing_existing_producers,[]);
assert(!diagnose({source_compilation:{missing:["GENERATED_PERMANENT"],
  compiler_input_impact:{catalog_input_missing:[
    {input:"GENERATED_PERMANENT",existing_producer:"/home/secrets/key"}]}}}
  ).firstMissing.includes("/home/"));
"""
        completed=subprocess.run(["node","-e",code],cwd=ROOT,
                                 capture_output=True,text=True)
        self.assertEqual(completed.returncode,0,
                         completed.stdout+"\\n"+completed.stderr)


class SelectedOilPreparationRouting(unittest.TestCase):
    def test_oil_name_selection_is_outside_expert_itemid_panel(self):
        from pathlib import Path
        html=(Path(__file__).resolve().parents[1]/"runner/webui/index.html").read_text("utf8")
        start=html.index('id="conditions-title"')
        expert=html.index('id="optimizer-season-itemid-expert"',start)
        prepare=html.index('id="user-variant-prepare-btn"',start)
        for ident in ("env-oil-options","optimizer-oil-loadout",
                      "oil-preparation-main","oil-preparation-off"):
            marker='id="'+ident+'"'
            self.assertEqual(html.count(marker),1,ident+" duplicate DOM ID")
            self.assertLess(html.index(marker,start),prepare,
                            ident+" must be before ordinary preparation action")
            self.assertLess(html.index(marker,start),expert,
                            ident+" must not require expert ItemID panel")
        self.assertGreater(html.index('id="season-oil-main-id"',start),expert)


    def test_actual_build_consumable_flags_are_scoped_to_selected_variant(self):
        import shutil, subprocess
        from pathlib import Path
        node=shutil.which("node")
        if node is None:self.skipTest("Node required")
        raw=Path(__file__).resolve().parents[1]/"runner/webui/app.js"
        script=r"""
const fs=require("fs"),assert=require("assert");
const src=fs.readFileSync(process.argv[1],"utf8");
const start=src.indexOf("async function buildSeasonEnvironment(forUserVariant=false)");
const a=src.indexOf("let reference_G_track=",start);
const b=src.indexOf("const existingSpecial=",a);
assert(start>=0&&a>start&&b>a,"missing Build request source");
const nodes={},$=id=>nodes[id]??=({value:"",checked:false});
const field=id=>String($(id).value).trim();
const run=Function("$","field","forUserVariant",src.slice(a,b)+
 "return {selected_flask_item_id,selected_oil_item_ids_by_hand,auto_native_F_requested,auto_native_O_requested,auto_select_observed_F_no_oil};");
$("season-auto-f-no-oil").checked=true;
$("season-native-f").checked=true;
$("season-selected-flask-id").value="241324";
$("season-oil-main-id").value="243734";
$("optimizer-oil-main-id").value="243734";
const selected=run($,field,true);
assert.equal(selected.selected_flask_item_id,241324,"explicit F retained");
assert.deepStrictEqual(selected.selected_oil_item_ids_by_hand,{main_hand:243734},"selected oil");
assert.equal(selected.auto_native_O_requested,true,"selected O measured");
assert.equal(selected.auto_select_observed_F_no_oil,false,"base no-oil flag must not leak");
const baseline=run($,field,false);
assert.equal(baseline.selected_flask_item_id,null,"default Build not user F");
assert.deepStrictEqual(baseline.selected_oil_item_ids_by_hand,{},"default Build not user oil");
assert.equal(baseline.auto_select_observed_F_no_oil,true,"default F flag retained");
assert.equal(baseline.auto_native_O_requested,false,"base O flag retained");
$("season-oil-main-id").value="";$("optimizer-oil-main-id").value="";
$("season-native-o").checked=true;
const noOil=run($,field,true);
assert.equal(noOil.auto_native_O_requested,false,"base O flag must not leak");
assert.equal(noOil.auto_select_observed_F_no_oil,false,"explicit F not auto-selected");
$("season-selected-flask-id").value="";
const autoF=run($,field,true);
assert.equal(autoF.auto_select_observed_F_no_oil,true,"selected no-F/no-O fallback");
$("season-oil-main-id").value="243734";
assert.throws(()=>run($,field,true),/정확한 영약 ItemID/,"missing F not guessed");
$("optimizer-oil-main-id").value="999999";
assert.throws(()=>run($,field,true),/서로 다릅니다/,"different IDs not silently replaced");
"""
        result=subprocess.run([node,"-e",script,str(raw)],capture_output=True,
                              text=True,encoding="utf8",timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+"\n"+result.stderr)


    def test_v832_named_special_gem_preparation_preserves_socket_intent(self):
        import shutil,subprocess
        from pathlib import Path
        node=shutil.which("node")
        if node is None:self.skipTest("Node required")
        raw=Path(__file__).resolve().parents[1]/"runner/webui/app.js"
        code=r"""
const fs=require("fs"),assert=require("assert");
const src=fs.readFileSync(process.argv[1],"utf8");
const a=src.indexOf("async function chooseVerifiedGem()");
const b=src.indexOf("function runeCompatibility()",a);
const nodes={},$=id=>nodes[id]??=({value:""});
const field=id=>String($(id).value).trim(),valueInt=id=>Number(field(id));
const state={oilCatalog:{gem_preparation_source:{status:"SOURCE_IDENTIFIED_PREPARATION_ONLY",
 items:[{physical_item_id:240983,user_selectable:false,status:"SOURCE_IDENTIFIED_PREPARATION_ONLY"}]}},
 verifiedExistingBudget:{},seasonGearTargetIlevel:334};
let calls=0;
const run=Function("$","field","valueInt","state","installedConsumableScopeMatches",
 "matchingInstalledGemVariants","reuseVerifiedGemVariant","updateSeasonSocketBreakdown",
 "updateBudgetPreview","setNotice","renderVerifiedGemChoices",
 src.slice(a,b)+"return chooseVerifiedGem();");
const execute=()=>run($,field,valueInt,state,()=>true,()=>[],async()=>{calls++;return false;},
 ()=>{},()=>{},()=>{},()=>{});
(async()=>{
 $("season-verified-special-gem").value="prepare:240983";
 $("season-target-socket-count").value="7";
 await execute();
 assert.equal(field("season-existing-special-gem-id"),"240983");
 assert.equal(valueInt("season-target-socket-count"),7);
 assert.equal(state.verifiedExistingBudget,null);
 assert.equal(state.seasonGearTargetIlevel,null);
 $("season-target-socket-count").value="4";
 await execute();assert.equal(valueInt("season-target-socket-count"),5);
 $("season-verified-special-gem").value="prepare:240967";
 await execute();assert.equal(calls,2);
 assert.equal(field("season-existing-special-gem-id"),"240983");
})().catch(e=>{console.error(e);process.exitCode=1;});
"""
        result=subprocess.run([node,"-e",code,str(raw)],capture_output=True,
                              text=True,encoding="utf8",timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+"\n"+result.stderr)

    def test_v831_actual_js_expanded_socket_scope_and_fury_track(self):
        import shutil,subprocess
        from pathlib import Path
        node=shutil.which("node")
        if node is None:self.skipTest("Node required")
        raw=Path(__file__).resolve().parents[1]/"runner/webui/app.js"
        code=r"""
const fs=require("fs"),assert=require("assert");
const src=fs.readFileSync(process.argv[1],"utf8");
const start=src.indexOf("async function buildSeasonEnvironment(forUserVariant=false)");
const a=src.indexOf("let reference_G_track=",start);
const b=src.indexOf("if(auto_select_observed_F_no_oil&&(!auto_native_F_requested",a);
assert(start>=0&&a>start&&b>a);
const nodes={},$=id=>nodes[id]??=({value:"",checked:false});
const field=id=>String($(id).value).trim(),valueInt=id=>Number(field(id));
const run=Function("$","field","valueInt","forUserVariant",src.slice(a,b)+
 "return {reference_G_track,socket_profile_spec,source_target_socket_count};");
$("spec").value="mage/fire";$("season-target-socket-count").value="5";
assert.deepStrictEqual(run($,field,valueInt,true),{
 reference_G_track:"general",socket_profile_spec:"mage/fire",source_target_socket_count:5});
$("spec").value="warrior/fury";$("final_T").value="4000";
assert.deepStrictEqual(run($,field,valueInt,true),{
 reference_G_track:"fury_dual_2h",socket_profile_spec:"warrior/fury",source_target_socket_count:5});
assert.deepStrictEqual(run($,field,valueInt,false),{
 reference_G_track:"general",socket_profile_spec:null,source_target_socket_count:4});
$("season-target-socket-count").value="4";
assert.deepStrictEqual(run($,field,valueInt,true),{
 reference_G_track:"general",socket_profile_spec:null,source_target_socket_count:4});
"""
        result=subprocess.run([node,"-e",code,str(raw)],capture_output=True,
                              text=True,encoding="utf8",timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+"\n"+result.stderr)

    def test_actual_js_select_and_start_reuse_or_build_selected_only(self):
        import shutil, subprocess
        from pathlib import Path
        node=shutil.which("node")
        if node is None:self.skipTest("Node required")
        raw=Path(__file__).resolve().parents[1]/"runner/webui/app.js"
        script=r"""
const fs=require("fs"),assert=require("assert");
const src=fs.readFileSync(process.argv[1],"utf8");
const block=(a,b)=>{
 const start=src.indexOf(a),end=src.indexOf(b,start+a.length);
 assert(start>=0&&end>start,"missing JS block: "+a);return src.slice(start,end);
};
const sections=[
 block("function chooseOilPreparationCandidate(hand) {","function renderInstalledOilLoadouts(data)"),
 block("function explicitOilPreparationRequested() {","function buildRequest()")
].join("\n");
const nodes={},$=id=>nodes[id]??=( {value:"",checked:false} );
const field=id=>String($(id).value).trim();
const sha="a".repeat(64);
const state={seasonGearTargetIlevel:334,verifiedExistingBudget:{sha},
 verifiedBaseFlaskInstalls:[],oilCatalog:{oil_preparation_source:{
 status:"OIL_PREPARATION_SOURCE_IDENTIFIED",items:[{physical_item_id:243734,
 status:"SOURCE_IDENTIFIED_PREPARATION_ONLY",user_selectable:false}]}}};
$("season-verified-budget").value=sha;
$("season-selected-flask-id").value="241324";
$("oil-preparation-main").value="243734";
$("ilevel").value="334";
$("season-target-socket-count").value="4";
const calls=[];let reusable=false,match=false,valid=true;
const run=Function("state","$","field","installedConsumableScopeMatches",
 "oilNeedsOffhand","syncOilUseToggle","updateBudgetPreview","buttonState",
 "setNotice","reuseVerifiedGemVariant","buildSeasonEnvironment",
 "prepareSelectedExistingEnvironment","validTargetIlevel",
 "verifiedInstalledGearScopeMatchesRun","switchView",
 "let oilUseIntent=true;"+sections+"\nreturn {chooseOilPreparationCandidate,prepareUserSelectedEnvironment,prepareSeasonBeforeOptimizerStart};"
)(state,$,field,()=>valid,()=>false,()=>{},()=>{},()=>{},()=>{},
 async()=>{calls.push("reuse");if(reusable)match=true;return reusable;},
 async selected=>{calls.push("build:"+selected);match=true;return {web_environment_scope:{environment_ready:true,environment_installed:true}};},
 async()=>{calls.push("old-budget");match=true;},()=>true,()=>match,()=>{});
(async()=>{
 run.chooseOilPreparationCandidate("main");
 assert.equal(field("optimizer-oil-main-id"),"243734","physical oil intent");
 assert.equal(field("season-oil-main-id"),"243734","Build physical oil");
 assert.equal(field("season-selected-flask-id"),"241324","explicit F preserved");
 assert.equal(field("season-verified-budget"),"","old O=0 SHA cleared");
 assert.equal(state.verifiedExistingBudget,null,"old budget object cleared");
 assert.equal(state.seasonGearTargetIlevel,null,"old ready scope revoked");
 assert.equal(await run.prepareSeasonBeforeOptimizerStart(),true);
 assert.deepStrictEqual(calls,["reuse","build:true"],"selected-only Build on real miss");
 calls.length=0;match=false;reusable=true;
 assert.equal(await run.prepareSeasonBeforeOptimizerStart(),true);
 assert.deepStrictEqual(calls,["reuse"],"exact existing layout, no Build");
 calls.length=0;match=false;valid=false;
 $("oil-preparation-main").value="999999";
 run.chooseOilPreparationCandidate("main");
 assert.equal(field("optimizer-oil-main-id"),"243734","stale catalog cannot replace intent");
 assert.deepStrictEqual(calls,[]);
})().catch(e=>{console.error(e.stack);process.exit(1)});
"""
        result=subprocess.run([node,"-e",script,str(raw)],capture_output=True,
                              text=True,encoding="utf8",timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+"\n"+result.stderr)

if __name__=="__main__":unittest.main()
