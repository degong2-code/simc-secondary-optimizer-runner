"""v071 new read-only safety regressions; no simulated result is Native PASS."""
import pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v071_rogue_adaptive_first_scout as runner
import v065_v015_scheduler_adapter as scheduler
from test_v064_adaptive_evaluator_port import make_fixture,CHMV1,SIMC_SHA
import v064_adaptive_evaluator_port as port
from test_v063_numeric_injection import fake_doc

class RogueV071Bounded(unittest.TestCase):
    def test_v071_receipt_policy_preserves_one_call_cap(self):
        self.assertEqual(runner.SCHEMA,"v071_real_user_rogue_adaptive_first_native_scout_v1")
        self.assertEqual(runner.probe.BIN_SHA,"64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e")
    def test_no_globally_optimal_claim_in_one_candidate_plan(self):
        normalized,budget,cal,reference=make_fixture()
        with tempfile.TemporaryDirectory() as tmp:
            req=port.make_request(normalized,budget,cal,reference,SIMC_SHA,
                                  CHMV1,60,pathlib.Path(tmp)/"sample.json")
            doc=fake_doc(req["input"])
            obs=port.ingest_native(req,doc,cal)
            state=scheduler.initial_state(normalized,budget,[obs],step=100,
                                          scout_max=1,confirmation_runs=2)
            nxt=scheduler.next_scout(state,normalized,budget,cal,
                reference,SIMC_SHA,pathlib.Path(tmp)/"result.json",60)
            self.assertNotEqual(nxt["case"]["target"],CHMV1)
            self.assertEqual(sum(nxt["case"]["target"].values()),
                             budget["budget"]["T_official"])
            self.assertFalse(nxt["case"]["global_optimum_proven"])
            self.assertEqual(nxt["decision"]["method"],
                "V015_LOCAL_MIRROR_FOR_SCOUT_ORDER_ONLY")
    def test_missing_witness_and_prior_source_blocks_no_native(self):
        with tempfile.TemporaryDirectory() as tmp:
            x=runner.run(pathlib.Path(tmp)/"none",
                pathlib.Path(tmp)/"none",pathlib.Path(tmp)/"out")
            self.assertEqual(x,3)
            import json
            report=json.loads((pathlib.Path(tmp)/"out"/"V071_RECEIPT.json").read_text())
            self.assertEqual(report["new_native_calls"],0)
            self.assertEqual(report["status"],"BLOCKED_OR_PARTIAL")
            self.assertFalse(report["rogue_global_optimum_proven"])
if __name__=="__main__":unittest.main()
