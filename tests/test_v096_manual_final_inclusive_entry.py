"""v096 manual final T end-to-end offline: source, oil, legacy B, request.

Uses existing Fury/Frost source-locked fixtures; no new SimC execution.
"""
import json,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v096_unified_product_entry as entry
import v093_inclusive_adaptive_scheduler_bridge as adaptive
from test_v096_unified_product_entry import V096Unified
from test_v091_weapon_oil_external_adapter import FURY_TARGET, FROST_TARGET

class V096ManualFinalT(unittest.TestCase):
    def fixture(self,td,kind="fury",oil_hands=None):
        path,raw=V096Unified().fixture(td,kind)
        if oil_hands is not None:raw["oil_hands"]=oil_hands
        raw["manual_final_T"]=(3350 if kind=="fury" and raw["oil_hands"]==[] else
            3414 if kind=="fury" else 3182 if raw["oil_hands"] else 3150)
        path.write_text(json.dumps(raw),encoding="utf8")
        return path,raw

    def test_fury_manual_final_T_exact_B_and_one_oil_injection(self):
        with tempfile.TemporaryDirectory() as td:
            path,raw=self.fixture(td)
            ready=entry.source(path)
            plan=entry.run_manifest(path,plan_only=True)
            self.assertEqual((plan["base_B"],plan["final_T"]),(3350,3414))
            self.assertEqual(plan["user_manual_final_T"],3414)
            self.assertEqual(plan["legacy_v061_base_B"],3350)
            self.assertEqual(plan["budget_source"],"USER_MANUAL_FINAL_INCLUDING_OIL")
            self.assertIsNone(ready["context"]["identity"]["reference_source_sha256"])
            self.assertFalse(plan["native_called"])
            self.assertFalse((pathlib.Path(td)/"output").exists())
            req=adaptive.request(ready["context"],FURY_TARGET,raw["flask_F"],
                                 pathlib.Path(td)/"native.json",phase="seed")
            self.assertEqual(req["target"]["crit_rating"],870)
            self.assertEqual(req["target"]["haste_rating"],870)
            self.assertEqual(sum(req["target"].values()),3414)
            self.assertEqual(req["raw_gear_override"]["haste_rating"]+
                             raw["flask_F"]["haste_rating"],870)
            self.assertEqual(req["v092_base_B"],3350)
            self.assertEqual(req["v092_final_T"],3414)

    def test_manual_and_reference_same_B_different_cache_identity(self):
        with tempfile.TemporaryDirectory() as td:
            path,raw=V096Unified().fixture(td)
            ref=entry.source(path)
            raw["manual_final_T"]=3414
            path.write_text(json.dumps(raw),encoding="utf8")
            manual=entry.source(path)
            self.assertNotEqual(ref["context"]["identity"],manual["context"]["identity"])
            self.assertEqual(manual["context"]["identity"]["base_B"],3350)
            self.assertIsNone(manual["context"]["identity"]["reference_source_sha256"])

    def test_frost_one_oil_manual_final_T(self):
        with tempfile.TemporaryDirectory() as td:
            path,raw=self.fixture(td,"frost")
            ready=entry.source(path)
            self.assertEqual((ready["plan"]["base_B"],ready["plan"]["final_T"]),(3150,3182))
            req=adaptive.request(ready["context"],FROST_TARGET,raw["flask_F"],
                                 pathlib.Path(td)/"native.json",phase="seed")
            self.assertEqual(req["target"]["crit_rating"],916)
            self.assertEqual(req["target"]["haste_rating"],816)
            self.assertEqual(req["v091_expected_temporary_enchant"],
                             "main_hand:thalassian_phoenix_oil_2")

    def test_bad_user_T_blocks_without_output_or_native(self):
        with tempfile.TemporaryDirectory() as td:
            path,raw=self.fixture(td)
            for bad in (True, "3414", None, 0, 100001):
                raw["manual_final_T"]=bad
                path.write_text(json.dumps(raw),encoding="utf8")
                with self.subTest(bad=bad),self.assertRaisesRegex(entry.EntryBlocked,
                           "MANUAL_FINAL_T_REQUIRED"):
                    entry.run_manifest(path,plan_only=True)
            raw["manual_final_T"]=32
            path.write_text(json.dumps(raw),encoding="utf8")
            with self.assertRaisesRegex(Exception,"USER_TOTAL_LESS_THAN_FIXED_O"):
                entry.run_manifest(path,plan_only=True)
            self.assertFalse((pathlib.Path(td)/"output").exists())

    def test_manual_T_does_not_silently_override_legacy_manual(self):
        with tempfile.TemporaryDirectory() as td:
            path,raw=self.fixture(td)
            scenario=pathlib.Path(td)/"scenario.json"
            doc=json.loads(scenario.read_text(encoding="utf8"))
            doc["target"]={"mode":"manual_total","ilevel":334,
                "manual_total":3350,
                "manual_total_scope":"INCLUDES_G_J_F_EXCLUDES_EXTERNAL"}
            scenario.write_text(json.dumps(doc),encoding="utf8")
            with self.assertRaisesRegex(Exception,
                     "MANUAL_FINAL_T_REQUIRES_UNSET_LEGACY_TARGET"):
                entry.run_manifest(path,plan_only=True)
            self.assertFalse((pathlib.Path(td)/"output").exists())

if __name__=="__main__":unittest.main()
