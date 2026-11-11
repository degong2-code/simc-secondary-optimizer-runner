"""v321 new Shadow 120 Native experiment guard; synthetic/offline Native0."""
from __future__ import annotations
import os
import pathlib
import tempfile
import unittest
from unittest import mock

from integration_probes import p2_v321_shadow_priest_new_user_sem120_real_once as p
from integration_probes import p2_v319_new_windwalker_v290_v318_real_once as h

class V321ShadowNewUser(unittest.TestCase):
    def test_new_supported_spec_not_v313_v314_or_v319(self):
        case,ctl=h.new_user_case(
             p.CASE,expected_spec=p.EXPECTED)
        self.assertEqual((case["character_class"],case["character_spec"]),
                         ("priest","shadow"))
        self.assertEqual(case["target_ilevel"],334)
        self.assertIsNone(case["final_T"])
        self.assertIsNone(ctl["final_T"])
        self.assertEqual((ctl["targets"],ctl["duration_seconds"]),(1,300))

    def test_stable_new_simc_120_source_only_two_typed_edits(self):
        original=("priest=new\nspec=shadow\niterations=320\n"
                  "gear_crit_rating=100\ngear_haste_rating=200\n"
                  "flask=flask_of_thalassian_resistance_2\n"
                  "json2=/original.json\n")
        changed=p.exact_new_simc_120_input(original,"/another/result.json")
        self.assertEqual(changed,original.replace(
            "iterations=320","iterations=120").replace(
            "/original.json","/another/result.json"))
        with self.assertRaises(p.ShadowTierBlocked):
            p.exact_new_simc_120_input(
                original.replace("iterations=320","iterations=35"),
                "/another/result.json")

    def test_oneshot_guard_blocks_before_new_environment_and_native(self):
        with mock.patch.dict(os.environ,
                             {"P2_V321_NEW_SHADOW_SEM120_ONCE":"0"}):
            with self.assertRaisesRegex(
                     p.ShadowTierBlocked,"EXPLICIT_NEW_SHADOW_NATIVE_ONCE"):
                p.main()

    def test_v319_existing_default_new_profile_case_still_same(self):
        case,ctl=h.new_user_case()
        self.assertEqual((case["character_class"],case["character_spec"]),
                         ("monk","windwalker"))
        self.assertIsNone(ctl["final_T"])

if __name__=="__main__":
    unittest.main()
