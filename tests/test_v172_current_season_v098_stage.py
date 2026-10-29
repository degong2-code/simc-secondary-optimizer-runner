"""v172 source-first -> existing v098 stage. Offline: NO Native/HTTP."""
from __future__ import annotations
import json,pathlib,sys,tempfile,unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v098_target_user_scenario_bootstrap as boot
import v106_user_session_controller as sessions
import v139_pure_target_profile_composer as pure
import v143_specialization_contracts as specs
import v169_source_first_representative_stage as current

TRINKETS=[
    {"slot":"trinket1","item_id":270175,"options":{}},
    {"slot":"trinket2","item_id":270173,"options":{}}
]

class SourceFirstToEstablishedP1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope=current.season_scope()
        cls.source=current.build_all(
            current.gear.read(),current.load_tier())
        assert cls.source["dps_specs"]==26

    def character(self,key):
        cl,sp=key
        contract=specs.lookup(cl,sp)
        return {"class":cl,"spec":sp,
                "race":(contract["allowed_races"] or ["human"])[0],
                "talents":"abc123456789"}

    def user(self,key):
        data=sessions.standard_controls(key)
        data["trinket_ids"]=[x["item_id"] for x in TRINKETS]
        return sessions.user_scenario(data)

    def test_all_26_same_existing_adapter_with_current_tier_and_consume_B(self):
        for key in sessions.SUPPORTED:
            with self.subTest(spec="/".join(key)):
                ch=self.character(key)
                profile,cfg,rows,groups,weapon_form,F,tier_data,fifth=(
                    pure.v098_inputs(ch,TRINKETS,season_override=self.scope))
                old=self.source["specializations"]["/".join(key)]
                self.assertEqual(set(groups.values()),{"tier","trinkets"})
                self.assertEqual(len(groups),6)
                self.assertEqual(
                    {s:rows[s]["item_id"] for s in current.FOUR},
                    {s:old["tier_ids"][s] for s in current.FOUR})
                self.assertEqual(
                    {s:rows[s]["item_id"] for s in old["weapons"]},
                    old["weapons"])
                self.assertEqual({s:rows[s]["item_id"] for s in current.ORDINARY},
                                 old["ordinary"])
                self.assertEqual(cfg["consumables"]["gem_budget_J"],138)
                self.assertEqual(cfg["consumables"]["flask_budget_F"],165)
                self.assertEqual(sum(F.values()),165)
                self.assertEqual(weapon_form,old["weapon_form"])
                self.assertIn("default_actions=1",profile)
                self.assertEqual(fifth[0],"chest")
        self.assertEqual(self.scope["target_ilevel"],334)

    def test_true_v098_complete_plan_reuses_B_T_O_and_manifest_no_native(self):
        # Four weapon forms and armor families; avoid 26 repeated manifest builds.
        for key in (("paladin","retribution"),("mage","frost"),
                    ("hunter","marksmanship"),("demonhunter","havoc")):
            with self.subTest(spec=key),tempfile.TemporaryDirectory() as temp:
                root=pathlib.Path(temp)
                binary=root/"fake_simc.exe"
                binary.write_bytes(b"offline-only-not-native")
                user=self.user(key)
                with mock.patch.object(boot.entry,"run_manifest",
                                       wraps=boot.entry.run_manifest) as runner:
                    staged=boot.build(user,root/"source_first",binary,"7bc1071",
                        pure_stage=True,source_first_stage=True)
                    runner.assert_called_once()
                    self.assertEqual(runner.call_args.kwargs.get("plan_only"),True)
                self.assertEqual(staged["status"],
                                 "STAGED_INTERNAL_MANIFEST_NATIVE_NOT_AUTHORIZED")
                self.assertEqual(staged["native_calls"],0)
                self.assertTrue(staged["source_first_stage"])
                self.assertTrue(staged["new_season_equipment_not_native_accepted"])
                self.assertTrue(staged["v098_user_default_unchanged"])
                self.assertEqual(staged["plan"]["base_B"]+
                     sum(staged["plan"]["fixed_O"].values()),
                     staged["plan"]["final_T"])
                self.assertEqual(len(staged["effective_four_tier_slots"]),4)
                manifest=json.loads((root/"source_first"/"manifest.json").read_text())
                self.assertIs(manifest[boot.entry.STAGE_FIELD],True)
                self.assertFalse((root/"source_first"/"simc_results").exists())
                self.assertEqual(
                    boot.build(user,root/"source_first",binary,"7bc1071",
                        pure_stage=True,source_first_stage=True)["plan"],
                    staged["plan"])
                base=boot.build(user,root/"default",binary,"7bc1071")
                original=(root/"default"/"profile.simc").read_bytes()
                changed=(root/"source_first"/"profile.simc").read_bytes()
                self.assertNotEqual(original,changed)
                self.assertEqual(base["plan"]["base_B"],staged["plan"]["base_B"])
                self.assertEqual(base["plan"]["final_T"],staged["plan"]["final_T"])
                self.assertEqual((root/"default"/"profile.simc").read_bytes(),
                                 original)
                self.assertFalse((root/"default"/"simc_results").exists())

    def test_stage_only_and_non334_rejections_are_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            fake=root/"not_simc.exe"
            fake.write_bytes(b"NEVER_RUN")
            user=self.user(("paladin","retribution"))
            with self.assertRaisesRegex(boot.UserScenarioBlocked,
                                        "SOURCE_FIRST_STAGE_ONLY_334_PURE_PLAN"):
                boot.build(user,root/"bad1",fake,"7bc1071",
                           source_first_stage=True)
            user["target"]["ilevel"]=333
            with self.assertRaisesRegex(boot.UserScenarioBlocked,
                                        "SOURCE_FIRST_STAGE_ONLY_334_PURE_PLAN"):
                boot.build(user,root/"bad2",fake,"7bc1071",
                           pure_stage=True,source_first_stage=True)

    def test_simc_execution_not_authorized_even_with_external_acceptance(self):
        with self.assertRaisesRegex(boot.UserScenarioBlocked,
                                    "SOURCE_FIRST_STAGE_NATIVE_NOT_AUTHORIZED"):
            boot.run("/nonexistent/user.json","/nonexistent/out",
                     "/nonexistent/simc","7bc1071",
                     pure_stage=True,source_first_stage=True,
                     physical_acceptance_root="/unused",execute=True)

if __name__=="__main__":
    unittest.main()
