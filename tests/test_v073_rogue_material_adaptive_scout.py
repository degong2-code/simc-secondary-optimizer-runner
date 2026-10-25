"""v073 bounded adaptive scout safety: synthetic data are not Native proof."""
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"runner"), str(ROOT/"tests")]
import v073_rogue_material_adaptive_scout as v073
import v065_v015_scheduler_adapter as scheduler
from test_v064_adaptive_evaluator_port import make_fixture, CHMV1, SIMC_SHA
from test_v063_numeric_injection import fake_doc
import v064_adaptive_evaluator_port as port


class V073MaterialScoutSafety(unittest.TestCase):
    def test_caps_and_policy(self):
        self.assertEqual(v073.STEP, 350)
        self.assertEqual(v073.SCOUT_MAX, 2)
        self.assertEqual(v073.SCOUT_ITERATIONS, 60)
        self.assertEqual(v073.MIN_MATERIAL_DISTANCE, 0.10)
        self.assertEqual(v073.NEAR_LOSS, 0.01)

    def test_rating_transfer_metric(self):
        first = {"crit_rating":813, "haste_rating":913,
                 "mastery_rating":712, "versatility_rating":712}
        moved = dict(first,crit_rating=463,versatility_rating=1062)
        self.assertEqual(v073.moved(first, moved), 350)
        self.assertGreaterEqual(v073.moved(first,moved), 315)

    def test_provisional_near_not_proven(self):
        a={"target":{"crit_rating":813,"haste_rating":913,
                     "mastery_rating":712,"versatility_rating":712},
           "dps_mean":223489.67,"dps_sem":367.88,"dps_samples":319}
        b=dict(a,target={"crit_rating":463,"haste_rating":913,
                         "mastery_rating":712,"versatility_rating":1062},
               dps_mean=222000,"dps_sem":1050,"dps_samples":59)
        res=v073.scout_summary([a],[b],3150)
        self.assertTrue(res["exploratory_results"][0]["may_warrant_fresh_confirmation"])
        self.assertFalse(res["material_alternative_proven"])
        self.assertTrue(res["different_iteration_counts_not_pooled"])
        self.assertFalse(res["exploratory_results"][0]["statistically_proven_near_best_alternative"])

    def test_old_policy_generates_350_step_without_new_scheduler(self):
        normalized, static, calibration, reference=make_fixture()
        with tempfile.TemporaryDirectory() as folder:
            request=port.make_request(normalized,static,calibration,reference,
                 SIMC_SHA,CHMV1,60,pathlib.Path(folder)/"old.json")
            observed=port.ingest_native(request,fake_doc(request["input"]),calibration)
            state=scheduler.initial_state(normalized,static,[observed],step=350,
                            scout_max=2,confirmation_runs=2)
            new=scheduler.next_scout(state,normalized,static,calibration,reference,
                          SIMC_SHA,pathlib.Path(folder)/"new.json",60)
            self.assertEqual(v073.moved(CHMV1,new["case"]["target"]),350)
            self.assertEqual(new["decision"]["method"],"V015_LOCAL_MIRROR_FOR_SCOUT_ORDER_ONLY")

    def test_missing_actual_artifact_refuses_native(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            code=v073.run(root/"bad069",root/"bad070",root/"bad071",
                          root/"bad072",root/"out")
            self.assertEqual(code,3)
            summary=json.loads((root/"out"/"V073_RECEIPT.json").read_text())
            self.assertEqual(summary["status"],"BLOCKED_OR_PARTIAL")
            self.assertEqual(summary["new_native_calls_this_invocation"],0)

if __name__=="__main__":
    unittest.main()
