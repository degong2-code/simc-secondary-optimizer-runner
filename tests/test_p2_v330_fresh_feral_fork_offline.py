"""Source-only fresh Feral and exact shared-history fork planner tests."""
import unittest
from unittest import mock
from integration_probes import p2_v330_fresh_feral_idea003_real_once as exp
from integration_probes import p2_v319_new_windwalker_v290_v318_real_once as fresh
class Fork(unittest.TestCase):
    def test_new_supported_spec_auto_T(self):
        case,controls=fresh.new_user_case(exp.CASE,exp.SPEC)
        self.assertEqual((case["character_class"],case["character_spec"]),exp.SPEC)
        self.assertIsNone(controls["final_T"])
        self.assertEqual(exp.TOTAL_ITER,4520)
    def test_prefix_diff_only_reserve(self):
        r={"index":0,"target":{"a":1},"iterations":35,"phase":"scout",
           "adaptive_stage":"global_reserve","region_id":None,
           "region_center":None,"region_radius_fraction":None,"hybrid_method":"reserve"}
        a=dict(r,target={"a":2})
        with mock.patch.object(exp.stratified,"next_plan",return_value={"next_request":a}):
            self.assertEqual(exp.matching_prefix([r],{})[0],0)
        with mock.patch.object(exp.stratified,"next_plan",return_value={"next_request":dict(a,adaptive_stage="regional")}):
            with self.assertRaisesRegex(RuntimeError,"NON_RESERVE_CHANGE"):
                exp.matching_prefix([r],{})
if __name__=="__main__":unittest.main()
