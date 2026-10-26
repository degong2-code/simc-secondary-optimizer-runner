"""v108 user consumables and head diamond preserve exact J/F and oil budgets.

Offline only. No synthetic Omnium token and no new Native simulation.
"""
import pathlib,sys,tempfile,unittest,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v106_user_session_controller as session
import v098_target_user_scenario_bootstrap as boot
import v108_native_consumable_inputs as consumer

class NativeConsumableUserFlow(unittest.TestCase):
    def setup(self,key=("paladin","retribution")):
        td=tempfile.TemporaryDirectory();self.addCleanup(td.cleanup)
        root=pathlib.Path(td.name)
        binary=root/"simc_fake";binary.write_bytes(b"NEVER_EXECUTE_NATIVE")
        defaults=session.standard_controls(key)
        return root,binary,defaults

    def build(self,controls):
        root,binary,_=self.setup()  # new temp/simc
        user=session.user_scenario(controls)
        receipt=boot.build(user,root/"out",binary,"7bc10711b5")
        cfg=json.loads((root/"out"/"scenario.json").read_text())
        profile=(root/"out"/"profile.simc").read_text()
        return user,receipt,cfg,profile

    def test_six_source_profiles_defaults_retain_334_B_and_138_165(self):
        for key in session.SUPPORTED:
            with self.subTest(key=key):
                root,binary,controls=self.setup(key)
                user=session.user_scenario(controls)
                result=boot.build(user,root/"out",binary,"7bc10711b5")
                cfg=json.loads((root/"out"/"scenario.json").read_text())
                source=(root/"out"/"profile.simc").read_text()
                self.assertEqual(result["plan"]["base_B"],
                                 3350 if key==("warrior","fury") else 3150)
                self.assertEqual(cfg["consumables"]["gem_budget_J"],138)
                self.assertEqual(cfg["consumables"]["flask_budget_F"],165)
                self.assertEqual(result["native_calls"],0)
                self.assertEqual(result["consumables_selected"]["flask"],
                                 cfg["consumables"]["flask"])
                self.assertIn("augmentation=",source)
                self.assertIn("temporary_enchant=",source)
                self.assertFalse((root/"out"/"simc_results").exists())

    def test_potion_food_augmentation_user_choice_is_exactly_once_in_simc_and_cache(self):
        root,binary,controls=self.setup()
        controls["consumable_choices"]={
            "flask":"source_default","food":"royal_roast",
            "potion":"lights_potential_2","augmentation":"disabled",
            "diamond_id":0}
        u=session.user_scenario(controls)
        a=session.store_session(u,root/"sessions",binary,"7bc10711b5")
        output=boot.build(u,a/"generated",binary,"7bc10711b5")
        cfg=json.loads((a/"generated"/"scenario.json").read_text())
        profile=(a/"generated"/"profile.simc").read_text()
        for needle in ("food=royal_roast","potion=lights_potential_2",
                       "augmentation=disabled"):
            self.assertEqual(sum(s==needle for s in profile.splitlines()),1)
        self.assertEqual(cfg["consumables"]["food"],"royal_roast")
        self.assertEqual(cfg["consumables"]["potion"],"lights_potential_2")
        self.assertEqual(cfg["consumables"]["flask_budget_F"],165)
        self.assertEqual((output["plan"]["base_B"],output["plan"]["final_T"]),
                         (3150,3182))
        self.assertEqual(output["native_calls"],0)
        other=session.standard_controls()
        normal=session.user_scenario(other)
        self.assertNotEqual(session.session_path(normal,root/"sessions",binary,
                             "7bc10711b5")[0],a)

    def test_primary_only_diamond_switch_no_secondary_J_or_F_drift(self):
        root,binary,controls=self.setup()
        controls["consumable_choices"]["diamond_id"]=240967
        cfg_user=session.user_scenario(controls)
        result=boot.build(cfg_user,root/"out",binary,"7bc10711b5")
        cfg=json.loads((root/"out"/"scenario.json").read_text())
        rows=[*cfg["equipment"]["tier"],*cfg["equipment"]["crafted"],
              *cfg["equipment"]["special"]]
        head=[x for x in rows if x["slot"]=="head"]
        self.assertEqual(len(head),1)
        self.assertEqual(head[0]["options"]["gem_id"],"240967")
        self.assertIn("gem_id=240967",
                      next(l for l in (root/"out"/"profile.simc").read_text().splitlines()
                           if l.startswith("head=")))
        self.assertEqual(cfg["consumables"]["special_gem_id"],240967)
        self.assertEqual(cfg["consumables"]["gem_budget_J"],138)
        self.assertEqual(cfg["consumables"]["flask_budget_F"],165)
        self.assertEqual(result["plan"]["final_T"],3182)

    def test_invalid_flask_or_invented_folio_protected_pre_native(self):
        root,binary,controls=self.setup()
        controls["consumable_choices"]["flask"]="flask_of_the_magisters_2"
        u=session.user_scenario(controls)
        with self.assertRaisesRegex(consumer.ConsumableBlocked,
                "ALTERNATE_FLASK_F_VECTOR_NOT_NATIVE_VERIFIED"):
            boot.build(u,root/"bad",binary,"7bc10711b5")
        self.assertFalse((root/"bad"/"simc_results").exists())
        controls["consumable_choices"]["flask"]="source_default"
        controls["consumable_choices"]["augmentation"]="omnium_folio_fake"
        with self.assertRaisesRegex(consumer.ConsumableBlocked,
                "UNVERIFIED_SIMC_TOKEN:augmentation"):
            boot.build(session.user_scenario(controls),root/"folio",
                       binary,"7bc10711b5")

    def test_legacy_v098_without_choices_still_supported(self):
        root,binary,controls=self.setup()
        old=session.user_scenario(controls)
        del old["consumable_choices"]
        out=boot.build(old,root/"out",binary,"7bc10711b5")
        self.assertEqual(out["plan"]["base_B"],3150)
        self.assertEqual(out["native_calls"],0)

if __name__=="__main__":unittest.main()
