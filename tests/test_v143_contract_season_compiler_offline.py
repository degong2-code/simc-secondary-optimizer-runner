"""P1 stable contracts / replaceable season compiler, ZERO Native SimC."""
from __future__ import annotations
import copy
import hashlib
import pathlib
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v139_pure_target_profile_composer as pure
import v098_target_user_scenario_bootstrap as bootstrap
import v143_specialization_contracts as specs
from integration_probes.v140_pure_profile_physical_native_smoke import user_for

# Observed user Windows V094_SESSION_IDENTITY source-profile fingerprints for
# the two 2026-10-28 real 6/6 Native adaptive trials. These are evidence
# anchors, never loaded as runtime templates or complete user profiles.
VERIFIED_SOURCE_SHA={
    "druid/balance":"a00d8241d5bda2f07b5486a50c29edc9befb4b1853bbdc0ecffd3a73f1f77548",
    "evoker/devastation":"60b669d15ff1ef950debd447ed7af5a8d8b5829d441c52638b46c8b5d43c0d06",
}

class IndependentSeasonCompiler(unittest.TestCase):
    def test_contract_is_stable_and_season_records_contain_only_items(self):
        self.assertTrue(specs.validate_contracts())
        season=pure.catalog()
        self.assertEqual(set(season["specializations"]),set(specs.CONTRACTS))
        self.assertEqual(season["schema"],"v144_representative_season_items_v1")
        self.assertEqual(season["target_ilevel"],334)
        for key,item in season["specializations"].items():
            self.assertEqual(set(item),{"tier_ids","four_tier_slots",
                                        "ordinary","weapons"})
            cl,sp=key.split("/")
            contract=specs.lookup(cl,sp)
            self.assertEqual(contract["simc_class"],cl)
            self.assertEqual(contract["simc_spec"],sp)
            self.assertNotIn("tier_ids",contract)
            self.assertNotIn("main_hand",contract)
        self.assertIsNone(specs.lookup("evoker","augmentation"))

    def test_no_rewrite_of_native_proven_source_profile_bytes(self):
        for key,sha in VERIFIED_SOURCE_SHA.items():
            with self.subTest(key=key):
                user=user_for(key)
                text,meta,rows,tier=pure.compose(
                    user["character"],user["trinkets"],
                    target_ilevel=334,combat=user["combat"])
                self.assertEqual(meta["native_calls"],0)
                self.assertFalse(meta["source_profile_read"])
                self.assertEqual(len(tier),4)
                self.assertEqual(len(rows),16)
                # The real Native identity hashes the FINAL v098 emitter
                # output (including validated selected gear/consumables),
                # not v139's intermediate string.
                with tempfile.TemporaryDirectory() as td:
                    root=pathlib.Path(td)
                    binary=root/"simc.mock"
                    binary.write_bytes(b"OFFLINE_NO_NATIVE_SIMC")
                    folder=root/"stage"
                    result=bootstrap.build(user,folder,binary,"7bc10711b5",
                                           pure_stage=True)
                    self.assertEqual(result["native_calls"],0)
                    profile=(folder/"profile.simc").read_bytes()
                    self.assertEqual(hashlib.sha256(profile).hexdigest(),sha)
                    self.assertEqual(hashlib.sha256(profile).hexdigest(),
                                     result["plan"]["source_profile_sha256"]
                                     if "source_profile_sha256" in result["plan"]
                                     else hashlib.sha256(profile).hexdigest())

    def test_only_season_data_changes_for_future_season_mock(self):
        user=user_for("druid/balance")
        base=pure.catalog()
        future=copy.deepcopy(base)
        future["season"]="future_mock_not_real_items"
        future["target_ilevel"]=345
        future["character_level"]=91
        future["specializations"]["druid/balance"]["ordinary"]["feet"]=123456
        future["default_consumables"]["food"]="disabled"
        before=copy.deepcopy(specs.CONTRACTS)
        text,meta,rows,_=pure.compose(
            user["character"],user["trinkets"],
            target_ilevel=345,combat=user["combat"],season=future)
        self.assertEqual(specs.CONTRACTS,before)
        self.assertEqual(meta["season"],"future_mock_not_real_items")
        self.assertEqual(rows["feet"]["item_id"],123456)
        self.assertEqual(rows["feet"]["ilevel"],345)
        self.assertIn("food=disabled\n",text)
        self.assertIn("level=91\n",text)
        self.assertIn("default_actions=1\n",text)
        # A synthetic future item is not evidence of accepted real SimC IDs.
        self.assertFalse(meta["user_optimizer_ready"])

    def test_bad_contract_in_season_cannot_silently_become_runtime_code(self):
        season=pure.catalog()
        user=user_for("druid/balance")
        for bad in ("family","role","primary","weapon_form","simc_class"):
            with self.subTest(field=bad):
                changed=copy.deepcopy(season)
                changed["specializations"]["druid/balance"][bad]="incorrect"
                with self.assertRaisesRegex(pure.ProfileStageBlocked,
                       "SEASON_CONTAINS_STABLE_CONTRACT_FIELDS"):
                    pure.compose(user["character"],user["trinkets"],
                                 season=changed,combat=user["combat"])
        missing=copy.deepcopy(season)
        missing["specializations"]["evoker/augmentation"]={
            "tier_ids":{},"four_tier_slots":[],
            "ordinary":{},"weapons":{}}
        with self.assertRaisesRegex(pure.ProfileStageBlocked,
                                   "SEASON_SPEC_HAS_NO_STABLE_CONTRACT"):
            pure.compose(user["character"],user["trinkets"],season=missing)

if __name__=="__main__":
    unittest.main()
