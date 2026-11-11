"""v329 new Affliction source-first opt-in IDEA002, Native0 offline."""
import os,unittest
from unittest import mock
from integration_probes import p2_v329_affliction_new_user_idea002_real_once as study
from integration_probes import p2_v319_new_windwalker_v290_v318_real_once as p1
from runner import v306_seed_retained_coarse_escape_regions as old
from runner import v328_idea002_evidence_gated_radius as new

class Idea002E2EOffline(unittest.TestCase):
    def test_fresh_dps_profile_and_auto_final_T_only(self):
        case,controls=p1.new_user_case(study.CASE,study.SPEC)
        self.assertEqual((case["character_class"],case["character_spec"]),
                         ("warlock","affliction"))
        self.assertEqual(case["target_ilevel"],334)
        self.assertIsNone(case["final_T"])
        self.assertIsNone(controls["final_T"])
        self.assertEqual(case["sockets"],4)
        self.assertNotIn(study.SPEC,{
            ("monk","windwalker"),("priest","shadow"),
            ("druid","balance"),("evoker","devastation"),
            ("demonhunter","havoc"),("warlock","destruction")})
    def test_equal_budget_regional_ablation_is_exact_4520(self):
        self.assertEqual(study.BUDGET,64)
        self.assertEqual(study.START_GLOBAL,16)
        self.assertEqual(study.CONFIRM,8)
        self.assertEqual(study.FIXED_ITERATIONS,4520)
        self.assertEqual(study.ARMS[0][1],old.SCHEMA)
        self.assertEqual(study.ARMS[1][1],new.SCHEMA)
        self.assertNotEqual(study.ARMS[0][1],study.ARMS[1][1])
    def test_explicit_native_guard(self):
        with mock.patch.dict(os.environ,
            {"P2_V329_IDEA002_FRESH_AFFLICTION_ONCE":"0"}):
            with self.assertRaisesRegex(study.V329Blocked,
                                        "NEW_SPEC_NATIVE_ONCE_OPT_IN"):
                study.main()
if __name__=="__main__":
    unittest.main()
