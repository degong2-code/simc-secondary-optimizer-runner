"""v139 -> existing v098/v091/v096 staged bridge; NO Native."""
from __future__ import annotations
import json,pathlib,sys,tempfile,unittest
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v098_target_user_scenario_bootstrap as boot

class PurePlanBridge(unittest.TestCase):
    def fixture(self,spec="balance",cl="druid",race="night_elf"):
        td=tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root=pathlib.Path(td.name)
        binary=root/"fake_simc.exe"
        binary.write_bytes(b"NOT_A_REAL_SIMC_BINARY")
        user={
          "schema":boot.SCHEMA,
          "character":{"class":cl,"spec":spec,"race":race,
                       "talents":"CAAAABBB11122"},
          "target":{"ilevel":334,"final_T":None},
          "trinkets":[
              {"slot":"trinket1","item_id":270175,"options":{}},
              {"slot":"trinket2","item_id":270173,"options":{}}],
          "special_items":[],"embellishments":[],"oil_hands":[],
          "combat":{"targets":1,"duration_seconds":300,"raid_buffs":True}}
        return root,binary,user

    def test_both_specs_flow_through_v098_existing_budget_without_native(self):
        for spec,cl,race in (
             ("balance","druid","night_elf"),
             ("devastation","evoker","dracthyr")):
            with self.subTest(spec=spec):
                root,binary,user=self.fixture(spec,cl,race)
                folder=root/"pilot"
                output=boot.build(user,folder,binary,"7bc10711b5",
                                  pure_stage=True)
                self.assertEqual(output["status"],
                      "STAGED_INTERNAL_MANIFEST_NATIVE_NOT_AUTHORIZED")
                self.assertTrue(output["pure_source_independent_stage"])
                self.assertFalse(output["user_optimizer_ready"])
                self.assertEqual(output["native_calls"],0)
                self.assertEqual(output["plan"]["item_slots"],16)
                self.assertEqual(output["supported_archetypes_now"],24)
                self.assertEqual(len(output["effective_four_tier_slots"]),4)
                self.assertGreater(output["plan"]["base_B"],0)
                prof=(folder/"profile.simc").read_text(encoding="utf8")
                self.assertIn("default_actions=1",prof)
                self.assertNotIn("actions.",prof)
                self.assertIn("omnium_talents=",prof)
                manifest=json.loads((folder/"manifest.json").read_text())
                self.assertEqual(manifest["native_limit"],6)
                self.assertIs(manifest[boot.entry.STAGE_FIELD],True)
                with mock.patch.object(boot.entry.durable,"run") as native:
                    with self.assertRaisesRegex(boot.entry.EntryBlocked,
                                                "UNVERIFIED_PURE_PROFILE_NATIVE_EXECUTION_BLOCKED"):
                        boot.entry.run_manifest(folder/"manifest.json")
                    native.assert_not_called()
                self.assertTrue((folder/"fillers.json").is_file())
                # Must not silently rewrite sealed plan/output on replay.
                self.assertEqual(
                    boot.build(user,folder,binary,"7bc10711b5",
                               pure_stage=True)["plan"]["base_B"],
                    output["plan"]["base_B"])

    def test_default_user_path_remains_strictly_24_and_aug_is_excluded(self):
        root,binary,user=self.fixture()
        with self.assertRaisesRegex(boot.UserScenarioBlocked,
                                    "REPRESENTATIVE_ARCHETYPE_NOT_READY"):
            boot.build(user,root/"default",binary,"7bc10711b5")
        user["character"]["class"]="evoker"
        user["character"]["spec"]="augmentation"
        user["character"]["race"]="dracthyr"
        with self.assertRaisesRegex(boot.UserScenarioBlocked,
                                    "REPRESENTATIVE_ARCHETYPE_NOT_READY"):
            boot.build(user,root/"aug",binary,"7bc10711b5",
                       pure_stage=True)
        self.assertFalse((root/"default").exists())
        self.assertFalse((root/"aug").exists())

    def test_pure_stage_native_executable_entry_is_rejected_before_any_simc(self):
        root,binary,user=self.fixture()
        userfile=root/"user.json"
        userfile.write_text(boot.canonical(user)+"\n",encoding="utf8")
        with mock.patch.object(boot.entry,"run_manifest") as run:
            with self.assertRaisesRegex(boot.UserScenarioBlocked,
                                        "PURE_STAGE_NATIVE_NOT_AUTHORIZED"):
                boot.run(userfile,root/"danger",binary,"7bc10711b5",
                         execute=True,pure_stage=True)
            run.assert_not_called()
        self.assertFalse((root/"danger").exists())

if __name__=="__main__":
    unittest.main()
