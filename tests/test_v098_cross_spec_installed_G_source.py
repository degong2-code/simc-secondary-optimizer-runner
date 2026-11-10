"""Reproduction for fresh-installed Ret G reference -> different user spec.

v216/v212's general normal-track budget is not an installed Mage/Warrior
physical gear receipt. The source's SHA remains verified; v169 supplies actual
selected-spec gear from same-build original sources. No SimC or network.
"""
import unittest
import pathlib
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v098_target_user_scenario_bootstrap as user_product
import v232_simc_only_ordinary_representative as physical
import v229_simc_only_source_seed as source_seed


class CrossSpecInstalledPhysicalReference(unittest.TestCase):
    def fixture(self):
        item={
            "schema":physical.SCHEMA,
            "status":"SIMC_SOURCE_PHYSICAL_CANDIDATE_NOT_ACTUAL_SEASON_PROOF",
            "character":{"class":"paladin","spec":"retribution"},
            "game_build":"12.1.5.70783",
            "simc_revision":"c20e2ad52e4c33711f74272309a5748125175fe8",
            "target_ilevel":334,
            "selected_G_slot_ids":{"head":11111,"main_hand":22222},
            "native_calls":0,"environment_ready":False}
        item["receipt_sha256"]=source_seed.digest(
            source_seed.canonical(item).encode("utf8"))
        calculation={"game_build":item["game_build"],
                     "simc_revision":item["simc_revision"],
                     "target_ilevel":334}
        return item,calculation

    def test_original_same_spec_preserves_its_exact_measured_ids(self):
        candidate,calculation=self.fixture()
        actual,fallback=user_product._choose_user_specific_fresh_G_source(
            candidate,user={"character":{"class":"paladin","spec":"retribution"}},
            calculation=calculation)
        self.assertIs(actual,candidate)
        self.assertFalse(fallback)

    def test_new_mage_must_not_inherit_paladin_physical_G_items(self):
        candidate,calculation=self.fixture()
        actual,fallback=user_product._choose_user_specific_fresh_G_source(
            candidate,user={"character":{"class":"mage","spec":"frost"}},
            calculation=calculation)
        self.assertIsNone(actual)
        self.assertTrue(fallback)

    def test_original_source_sha_build_revision_or_ilvl_drift_fails(self):
        candidate,calculation=self.fixture()
        for mode in ("receipt","build","ilevel","revision"):
            broken=dict(candidate)
            if mode=="receipt":
                broken["receipt_sha256"]="0"*64
            elif mode=="build":
                broken["game_build"]="12.1.5.70784"
            elif mode=="ilevel":
                broken["target_ilevel"]=335
            else:
                broken["simc_revision"]="deadbeef"
            with self.subTest(mode=mode),self.assertRaisesRegex(
                    user_product.UserScenarioBlocked,
                    "FRESH_V232_REFERENCE_SOURCE_HASH_OR_SCOPE_DRIFT"):
                user_product._choose_user_specific_fresh_G_source(
                    broken,user={"character":{"class":"mage","spec":"frost"}},
                    calculation=calculation)


if __name__=="__main__":
    unittest.main()
