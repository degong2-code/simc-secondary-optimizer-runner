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
        for marker in ('function oilCompatibility()','function chosenCraft(slot,exactItemId=null)',
            'function selectedGear(nodeId, group)','row4_crit','row4_vers',
            'refreshSpecialSlots()', 'syncCraftRow(row)'):

            self.assertIn(marker,js)
        self.assertIn("label.hidden=isPrivate",js)
        self.assertIn("정확한 제작장비 ItemID (선택 · 비우면 자동)",js)
        self.assertIn('input.type="number";input.min="1";input.max="999999999";',js)
        self.assertIn('class="gear-section gear-trinkets"',html)
        self.assertIn('class="gear-section gear-special"',html)
        self.assertIn('class="gear-section gear-embellishments"',html)
        self.assertIn("Omnium Folio · 4열 스탯",html)


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
  return vm.runInNewContext(src.slice(a,b)+"\n"+name,{});
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
assert(diagnose(pending).firstMissing.includes("기존 원본 생산자: v275"));
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

if __name__=="__main__":unittest.main()
