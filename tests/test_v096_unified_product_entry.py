"""v096 unified single-manifest entry cross-archetype offline integration tests.

No SimC execution. Existing earlier Rogue/Shaman/Hunter/Fury/Paladin/Mage
Native evidence is historical and is NOT recast as new Native coverage.
"""
import json,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v096_unified_product_entry as entry
import v082_fury_plate_dual_twohand_native as fury_module
import v084_frost_cloth_1h_frill_native as frost_module
from test_v091_weapon_oil_external_adapter import (
    fury,frost,FURY_TARGET,FROST_TARGET,REV)

class V096Unified(unittest.TestCase):
    def fixture(self,td,kind="fury"):
        p,c,fill=(fury(td) if kind=="fury" else frost(td))
        root=pathlib.Path(td)
        (root/"profile.simc").write_text(p,encoding="utf8")
        (root/"scenario.json").write_text(json.dumps(c),encoding="utf8")
        (root/"fillers.json").write_text(json.dumps(fill),encoding="utf8")
        fake=root/"dummy-no-native"
        fake.write_bytes(b"NO_SIMC_EXECUTION_PLAN_ONLY")
        target=FURY_TARGET if kind=="fury" else FROST_TARGET
        other=dict(target)
        other["crit_rating"]+=100
        other["haste_rating"]-=100
        document={"schema":entry.SCHEMA,
            "profile_simc":"profile.simc","scenario_json":"scenario.json",
            "fillers_json":"fillers.json","static_cache_json":None,
            "weapon_layout":"dual_two_hand" if kind=="fury" else "one_hand_frill",
            "oil_hands":["main_hand","off_hand"] if kind=="fury" else ["main_hand"],
            "flask_F":fury_module.DECLARED_F if kind=="fury" else frost_module.F_DECLARED,
            "seed_targets_B":[target,other],
            "native_binary":str(fake),"native_revision":REV,"output_dir":"output",
            "scouts":0,"material_scouts":0,"native_limit":4,"step":100,
            "cancel_file":None}
        manifest=root/"manifest.json"
        manifest.write_text(json.dumps(document),encoding="utf8")
        return manifest,document
    def test_fury_dual_twohand_source_bound_common_entry(self):
        with tempfile.TemporaryDirectory() as td:
            path,_=self.fixture(td)
            plan=entry.run_manifest(path,plan_only=True)
            self.assertEqual((plan["base_B"],plan["final_T"]),(3350,3414))
            self.assertEqual((plan["class"],plan["spec"]),("warrior","fury"))
            self.assertEqual(plan["fixed_O"]["crit_rating"],32)
            self.assertEqual(plan["item_slots"],16)
            self.assertFalse((pathlib.Path(td)/"output").exists())
            self.assertFalse(plan["native_called"])
    def test_frost_frill_source_bound_common_entry(self):
        with tempfile.TemporaryDirectory() as td:
            path,_=self.fixture(td,"frost")
            plan=entry.run_manifest(path,plan_only=True)
            self.assertEqual((plan["base_B"],plan["final_T"]),(3150,3182))
            self.assertEqual((plan["class"],plan["spec"]),("mage","frost"))
            self.assertEqual(plan["fixed_O"]["crit_rating"],16)
            self.assertEqual(plan["item_slots"],16)
            self.assertFalse(plan["native_called"])
    def test_native_call_budget_refuses_extra_scout_without_side_effects(self):
        with tempfile.TemporaryDirectory() as td:
            path,raw=self.fixture(td)
            raw["scouts"]=1
            path.write_text(json.dumps(raw),encoding="utf8")
            with self.assertRaisesRegex(entry.EntryBlocked,
                                        "SCENARIO_NATIVE_LIMIT_PRECHECK"):
                entry.run_manifest(path,plan_only=True)
            self.assertFalse((pathlib.Path(td)/"output").exists())
    def test_original_profile_sha_guard_rejects_modifications(self):
        with tempfile.TemporaryDirectory() as td:
            path,_=self.fixture(td)
            p=pathlib.Path(td)/"profile.simc"
            p.write_text(p.read_text()+"\n# changed\n",encoding="utf8")
            with self.assertRaisesRegex(Exception,"USER_SOURCE_PROFILE_SHA_MISMATCH"):
                entry.run_manifest(path,plan_only=True)
    def test_bad_fields_fail_before_file_or_native_access(self):
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/"bad.json"
            p.write_text(json.dumps({"schema":entry.SCHEMA,"extra":True}))
            with self.assertRaisesRegex(entry.EntryBlocked,"ENTRY_SCHEMA_OR_FIELDS"):
                entry.run_manifest(p,plan_only=True)
if __name__=="__main__":unittest.main()
