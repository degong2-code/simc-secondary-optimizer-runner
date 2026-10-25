"""v081 static-c compatibility in existing v015 mirror and v066 preflight.

Synthetic tests never claim real Native; production action uses exact v080 JSON2.
"""
import pathlib,sys,tempfile,unittest,copy,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v065_v015_scheduler_adapter as search
import v066_profile_neutral_preflight as generic
import v064_adaptive_evaluator_port as port
import v081_static_generic_scout_native as v081
import v079_hunter_ranged_generic_native as hunter
import v046_static_item_cache as cache
from test_v065_v015_scheduler_adapter import AuthenticatedPolicyAdapter
from test_v063_numeric_injection import fake_doc

UPSTREAM=ROOT/"integration_probes/fixtures/v079_upstream_mid2_hunter_beast_mastery_reference.simc"
SIMC_SHA="64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e"

class StaticNativeSearch(unittest.TestCase):
    def test_no_original_actual_receipts_refuses_all(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)
            result=v081.run(UPSTREAM,p/"no_verified_native",p/"out")
            self.assertEqual(result,3)
            data=json.loads((p/"out"/"V081_RECEIPT.json").read_text())
            self.assertEqual(data["status"],"BLOCKED_OR_PARTIAL")
            self.assertEqual(data["new_native_this_invocation"],0)

    def test_hunter_fixture_ranged_input_still_preserves_all_apl(self):
        with tempfile.TemporaryDirectory() as d:
            src=UPSTREAM.read_text("utf8")
            result,cfg,fill,metadata=hunter.source_profile(src,d)
        self.assertNotIn("off_hand=",result)
        self.assertEqual(metadata["weapon_type"],"ranged_no_offhand")
        self.assertEqual([x for x in src.splitlines() if x.startswith("actions")],
                         [x for x in result.splitlines() if x.startswith("actions")])

    def test_scheduler_rejects_mixed_legacy_and_static_results(self):
        pilot=AuthenticatedPolicyAdapter()
        pilot.setUp()
        legacy=pilot.r1
        static=dict(legacy,status="PASS_NATIVE_DPS_AND_STATIC_CHMV_INPUT",
                    rating_semantics="STATIC_CHMV_C_V1",
                    static_rating_verified=legacy["target"])
        state=search.initial_state(pilot.c,pilot.b,[static],
                        step=100,scout_max=2)
        fake_request={"case_key":"unique-static",
                      "scenario_digest":pilot.c["scenario_digest"]}
        next_obs=dict(static,case_key="unique-static",
                      target=pilot.r2["target"])
        with self.assertRaisesRegex(search.SchedulerBlocked,
                                   "SCOUT_MIXED_STATIC_AND_BUFFED_SEMANTICS"):
            search.accept_scout(state,fake_request,dict(legacy,case_key="unique-static",
                                      target=pilot.r2["target"]))

    def test_static_records_require_explicit_target_parity(self):
        pilot=AuthenticatedPolicyAdapter()
        pilot.setUp()
        a=dict(pilot.r1,status="PASS_NATIVE_DPS_AND_STATIC_CHMV_INPUT",
               rating_semantics="STATIC_CHMV_C_V1",
               static_rating_verified=pilot.r2["target"])
        with self.assertRaisesRegex(search.SchedulerBlocked,
                                   "STATIC_C_OBSERVATION_NOT_VERIFIED"):
            search.observations_by_vector([a],1603,*search.bounds(pilot.c,pilot.b)[1:])

    def test_static_preflight_never_uses_legacy_numeric_calibrator(self):
        with tempfile.TemporaryDirectory() as d:
            profile,cfg,fill,_=hunter.source_profile(
                UPSTREAM.read_text("utf8"),d)
            with self.assertRaisesRegex(generic.PreflightBlocked,
                                       "NATIVE_EXACT_G_STATIC_BUDGET_REQUIRED"):
                generic.prepare_static(cfg,fill,cache.empty_cache(),
                       profile,[],SIMC_SHA,
                       {"crit_rating":0,"haste_rating":165,
                        "mastery_rating":0,"versatility_rating":0})

if __name__=="__main__":unittest.main()
