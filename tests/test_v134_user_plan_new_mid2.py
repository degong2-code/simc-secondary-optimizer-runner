"""Real v106 controls → v098 plan → existing v096 contract, Native0.

All new MID2 source classes share one v134 adapter. No independent optimizer
and no actual SimC or unverified standalone Native success claim.
"""
from __future__ import annotations
import pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v101_common_representative_equipment as common
import v106_user_session_controller as controller
import v098_target_user_scenario_bootstrap as bootstrap
import v134_shared_mid2_profile_adapter as generic
import v132_dps_source_batch_smoke as sources
import v122_common_profile_format as profile_format

class NewMid2ProductEntry(unittest.TestCase):
    def test_seventeen_pinned_new_specs_use_exact_same_v098_plan_and_resume(self):
        self.assertEqual(set(common.GENERIC_PENDING),
                         {tuple(x.split("/")) for x in sources.NEW})
        self.assertIn(("druid","feral"),common.ARCHETYPES)
        self.assertEqual(len(common.GENERIC_PENDING),17)
        for key in sorted(common.GENERIC_PENDING):
            with self.subTest(key=key),tempfile.TemporaryDirectory() as td:
                base=pathlib.Path(td)
                binary=base/"fake_simc.exe"
                binary.write_bytes(b"FAKE_NEVER_NATIVE")
                controls=controller.standard_controls(key)
                user=controller.user_scenario(controls)
                folder=base/"session"
                result=bootstrap.build(user,folder,binary,"7bc1071")
                self.assertEqual(result["native_calls"],0)
                self.assertEqual(result["target_ilevel"],334)
                self.assertEqual(result["weapon_form"],
                                 common.ARCHETYPES[key][2])
                self.assertEqual(len(result["effective_four_tier_slots"]),4)
                self.assertEqual(result["supported_archetypes_now"],24)
                self.assertEqual(result["plan"]["base_B"],3150)
                self.assertEqual(result["plan"]["final_T"],
                                 3150+32*len(controls["oil_hands"]))
                p=(folder/"profile.simc").read_bytes()
                self.assertIn(("json2="+profile_format.JSON2_PLACEHOLDER).encode(),p)
                self.assertIn(b"actions=",p)
                self.assertFalse((folder/"simc_results").exists())
                replay=bootstrap.build(user,folder,binary,"7bc1071")
                self.assertEqual(replay["plan"],result["plan"])
                self.assertEqual((folder/"profile.simc").read_bytes(),p)

    def test_existing_seven_byte_source_registry_and_native_cache_unmodified(self):
        import v127_dps_source_metadata as registry
        self.assertEqual(len(registry.BY_SPEC),7)
        self.assertEqual(set(registry.BY_SPEC),
                         set(common.ARCHETYPES)-set(common.GENERIC_PENDING))
        self.assertEqual(len(common.ARCHETYPES),24)
        self.assertTrue(common.validate_source_registry())
        self.assertEqual(controller.standard_controls(("druid","feral"))["spec"],
                         "feral")
        for absent in (("druid","balance"),("evoker","devastation"),
                       ("evoker","augmentation")):
            with self.subTest(absent=absent):
                with self.assertRaisesRegex(controller.SessionBlocked,
                                             "V106_DPS_ARCHETYPE_NOT_READY"):
                    controller.standard_controls(absent)

if __name__=="__main__":
    unittest.main()
