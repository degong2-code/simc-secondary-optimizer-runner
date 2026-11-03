"""Synthetic ilvl rows reuse v222 without old-season values or Native."""
import copy
import unittest

from runner import v262_standardized_ilevel_budget_rows as standard
from runner import v222_season_budget_contract as budget
from tests.test_v222_season_budget_contract import fixture


def source_level(*, observed, level, track="ordinary_two_hand"):
    catalog, proof, _ = fixture()
    proof = copy.deepcopy(proof)
    proof["target_ilevel"] = level
    proof["components"]["G"]["source_sha256"] = (str(level)[-1])*64
    details = budget.standardize_representative_G(
        observed_G_total=observed, target_ilevel=level,
        source_observation_sha256=proof["components"]["G"]["source_sha256"])
    proof["components"]["G"]["rating"] = details["standardized_G"]
    proof["components"]["G"]["standardization"] = details
    proof["components"]["G"]["reference_track"] = track
    return catalog, proof


class StandardizedIlevelBudgetRowsTests(unittest.TestCase):
    def test_only_measured_levels_are_standardized_with_the_same_budget_math(self):
        catalog, first = source_level(observed=2847,level=334)
        _, second = source_level(observed=2853,level=335)
        _, third = source_level(observed=2861,level=336)
        result = standard.build(
            source_catalog=catalog,source_artifact_sha256="a"*64,
            evidence_by_ilevel={336:third,334:first,335:second},
            reference_track="ordinary_two_hand")
        self.assertEqual([x["ilevel"] for x in result["rows"]],
                         [334,335,336])
        self.assertEqual([x["G_standard"] for x in result["rows"]],
                         [2850,2850,2860])
        self.assertEqual([x["B"] for x in result["rows"]],
                         [3153,3153,3163])
        self.assertEqual([x["T"] for x in result["rows"]],
                         [3185,3185,3195])
        self.assertEqual([x["G_rounding_delta"] for x in result["rows"]],
                         [3,-3,-1])
        self.assertFalse(result["environment_ready"])
        self.assertFalse(result["source_authentication_performed_here"])
        self.assertTrue(result["manual_final_T_overrides_reference_on_session"])
        self.assertEqual((result["native_calls"],result["network_calls"]), (0,0))
        # Actual user T remains authoritative in the existing v222 engine.
        manual=budget.preprofile_budget(
            source_catalog=catalog,source_artifact_sha256="a"*64,
            evidence=first,target_ilevel=334,manual_final_T=3301)
        self.assertEqual((manual["base_B"],manual["final_T"]),(3269,3301))
        self.assertEqual(result["rows"][0]["T"],3185)

    def test_no_unmeasured_level_or_mixed_source_track_is_invented(self):
        catalog, first=source_level(observed=2847,level=334)
        _, second=source_level(observed=2861,level=335)
        bad=copy.deepcopy(second)
        bad["components"]["G"]["reference_track"]="titan_grip"
        with self.assertRaisesRegex(budget.SeasonBudgetBlocked,"TRACK_PROOF"):
            standard.build(source_catalog=catalog,source_artifact_sha256="a"*64,
                           evidence_by_ilevel={334:first,335:bad},
                           reference_track="ordinary_two_hand")
        bad=copy.deepcopy(second)
        bad["components"]["F"]["rating"]+=1
        with self.assertRaisesRegex(budget.SeasonBudgetBlocked,"MIXED_J_F_O"):
            standard.build(source_catalog=catalog,source_artifact_sha256="a"*64,
                           evidence_by_ilevel={334:first,335:bad},
                           reference_track="ordinary_two_hand")
        bad=copy.deepcopy(second)
        bad["components"]["G"]["standardization"]=None
        with self.assertRaisesRegex(budget.SeasonBudgetBlocked,"STANDARD_G"):
            standard.build(source_catalog=catalog,source_artifact_sha256="a"*64,
                           evidence_by_ilevel={334:first,335:bad},
                           reference_track="ordinary_two_hand")
        with self.assertRaisesRegex(budget.SeasonBudgetBlocked,"MEASURED_LEVELS"):
            standard.build(source_catalog=catalog,source_artifact_sha256="a"*64,
                           evidence_by_ilevel={},reference_track="ordinary_two_hand")
        with self.assertRaisesRegex(budget.SeasonBudgetBlocked,"MEASURED_LEVELS"):
            standard.build(source_catalog=catalog,source_artifact_sha256="a"*64,
                           evidence_by_ilevel={True:first},
                           reference_track="ordinary_two_hand")


if __name__=="__main__":
    unittest.main()
