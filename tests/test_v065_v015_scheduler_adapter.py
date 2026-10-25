"""v065 authentic v015 decision semantics adapted to v061-064 P1-P4.

Original 71/71 and 104/104 are HISTORICAL records, never relabeled as
reexecuted PASS. These tests execute *new v065* code only.
"""
import copy,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v065_v015_scheduler_adapter as p
import v064_adaptive_evaluator_port as port
from test_v064_adaptive_evaluator_port import (
    make_fixture,SIMC_SHA,CHMV1,CHMV2)
from test_v063_numeric_injection import fake_doc

class AuthenticatedPolicyAdapter(unittest.TestCase):
    def setUp(self):
        self.c,self.b,self.cal,self.source=make_fixture()
        self.r1=self.observed(CHMV1,190000)
        self.r2=self.observed(CHMV2,189000)
    def observed(self,target,dps):
        with tempfile.TemporaryDirectory() as d:
            request=port.make_request(self.c,self.b,self.cal,self.source,
                             SIMC_SHA,target,60,pathlib.Path(d)/"result.json")
            native=fake_doc(request["input"])
            native["sim"]["players"][0]["collected_data"]["dps"]["mean"]=dps
            return port.ingest_native(request,native,self.cal)
    def test_authentic_v015_trace_not_original_runtime(self):
        self.assertEqual(p.SOURCE_V015_SHA256,
            "a44f73cf232c8204dbe958e79fe50f111e68654ac583a1170a283f16035c0ec3")
        self.assertEqual(p.SOURCE_V016_SHA256,
            "7c49d7ca095e8864b673715d70d9851d676b44aeed99f8d769419492fcd14712")
        st=p.initial_state(self.c,self.b,[self.r1,self.r2],100,2)
        self.assertFalse(st["original_v015_v016_product_code_merged"])
        self.assertFalse(st["original_v015_v016_native_receipt_reused"])
        self.assertFalse(st["original_v015_v016_files_modified"])
        self.assertEqual(st["official_total"],1603)
    def test_old_source_neighbor_order_and_constant_T(self):
        total,lo,hi=p.bounds(self.c,self.b)
        original=(400,400,400,403)
        choices=p.neighbors(original,100,total,lo,hi,{original})
        self.assertEqual(len(choices),12)
        self.assertEqual(choices[0],(300,500,400,403))
        self.assertTrue(all(sum(x)==1603 for x in choices))
        self.assertTrue(all(p.eligible(x,total,lo,hi) for x in choices))
        self.assertEqual(len(set(choices)),len(choices))
    def test_local_mirror_difference_is_ordering_only(self):
        obs={(400,400,400,403):[self.r1],(230,570,400,403):[self.r2]}
        self.assertEqual(p.score_direction((400,400,400,403),
                         (500,300,400,403),obs),0)
        self.assertEqual(p.score_direction((400,400,400,403),
                         (570,230,400,403),obs),1000)
        self.assertEqual(p.choose_next(obs,100,1603,*(p.bounds(self.c,self.b)[1:]))[2]["method"],
              "V015_LOCAL_MIRROR_FOR_SCOUT_ORDER_ONLY")
    def test_two_observed_native_to_new_candidate_to_next_candidate(self):
        st=p.initial_state(self.c,self.b,[self.r1,self.r2],step=100,scout_max=2)
        with tempfile.TemporaryDirectory() as d:
            first=p.next_scout(st,self.c,self.b,self.cal,self.source,SIMC_SHA,
                   pathlib.Path(d)/"1.json",60)
            self.assertEqual(first["status"],"PROPOSED_SCOUT_NOT_RUN")
            self.assertNotIn(tuple(first["case"]["target"].values()),
                             (tuple(CHMV1.values()),tuple(CHMV2.values())))
            self.assertEqual(sum(first["case"]["target"].values()),1603)
            native=fake_doc(first["case"]["input"])
            native["sim"]["players"][0]["collected_data"]["dps"]["mean"]=192000.
            accepted=port.ingest_native(first["case"],native,self.cal)
            step1=p.accept_scout(st,first["case"],accepted)
            self.assertEqual(step1["completed_new_scouts"],1)
            second=p.next_scout(step1,self.c,self.b,self.cal,self.source,SIMC_SHA,
                   pathlib.Path(d)/"2.json",60)
            self.assertNotEqual(first["case"]["case_key"],second["case"]["case_key"])
            self.assertEqual(second["anchor"],first["case"]["target"])
            native2=fake_doc(second["case"]["input"])
            native2["sim"]["players"][0]["collected_data"]["dps"]["mean"]=193000.
            second_ob=port.ingest_native(second["case"],native2,self.cal)
            done=p.accept_scout(step1,second["case"],second_ob)
            self.assertTrue(done["awaiting_confirmation"])
            with self.assertRaisesRegex(p.SchedulerBlocked,"SCOUT_BUDGET_EXHAUSTED"):
                p.next_scout(done,self.c,self.b,self.cal,self.source,SIMC_SHA,
                             pathlib.Path(d)/"3.json",60)
            pair=p.pair_to_confirm(done,self.c,self.b,self.cal,
                self.source,SIMC_SHA,d,60)
            self.assertEqual(len(pair["cases"]),2)
            self.assertEqual(pair["cases"][0]["target"],second["case"]["target"])
            self.assertTrue(pair["old_native_DPS_must_not_replace_fresh_confirmations"])
            self.assertEqual(pair["status"],"TWO_FRESH_CONFIRMATIONS_REQUIRED_NOT_RUN")
    def test_fixed_L_and_fraction_bounds_are_respected(self):
        st=p.initial_state(self.c,self.b,[self.r1],100,1)
        target=st["observations"][0]["target"]
        self.assertGreaterEqual(target["crit_rating"],st["minima"]["crit_rating"])
        low=tuple(st["minima"][k] for k in p.STATS)
        high=tuple(st["maxima"][k] for k in p.STATS)
        x=p.neighbors((400,400,400,403),500,1603,low,high,{})
        self.assertEqual(x,[])  # all 500 transfers impossible from 400 base
    def test_external_fresh_judge_is_unconfirmed_when_seeds_missing(self):
        a=p.key(CHMV1);b=p.key(CHMV2)
        r=p.fresh_confirmation_judgment([a,b],{
            a:dict(self.r1,dps_mean=200000.,dps_sem=10.),
            b:dict(self.r2,dps_mean=190000.,dps_sem=10.)})
        self.assertTrue(r["statistical_separation_approx95_without_seed_claim"])
        self.assertFalse(r["pairwise_direction_supported"])
        self.assertFalse(r["distinct_simc_seeds_observed"])
        self.assertFalse(r["global_optimum_proven"])
    def test_confirm_fresh_distinct_simc_seeds_required(self):
        a=p.key(CHMV1);b=p.key(CHMV2)
        ra=dict(self.r1,dps_mean=200000.,dps_sem=10.,simc_seed=101)
        rb=dict(self.r2,dps_mean=190000.,dps_sem=10.,simc_seed=102)
        self.assertTrue(p.fresh_confirmation_judgment([a,b],{a:ra,b:rb})
                        ["pairwise_direction_supported"])
        rb["simc_seed"]=101
        self.assertFalse(p.fresh_confirmation_judgment([a,b],{a:ra,b:rb})
                         ["pairwise_direction_supported"])
    def test_no_fresh_confirmation_without_two_scouts(self):
        st=p.initial_state(self.c,self.b,[self.r1,self.r2],100,2)
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(p.SchedulerBlocked,"SCOUTS_NOT_COMPLETED"):
                p.pair_to_confirm(st,self.c,self.b,self.cal,
                                  self.source,SIMC_SHA,d,60)
    def test_cached_observations_not_global_optimum(self):
        st=p.initial_state(self.c,self.b,[self.r1,self.r2],100,0)
        with tempfile.TemporaryDirectory() as d:
            pair=p.pair_to_confirm(st,self.c,self.b,self.cal,
                                   self.source,SIMC_SHA,d,60)
            self.assertFalse(pair["global_optimum_proven"])
    def test_conflicting_observation_total_rejected(self):
        wrong=copy.deepcopy(self.r1);wrong["target"]["crit_rating"]=401
        with self.assertRaisesRegex(p.SchedulerBlocked,
                                    "OBSERVATION_OUTSIDE_OFFICIAL_T_OR_L"):
            p.initial_state(self.c,self.b,[wrong],100,2)
    def test_source_result_is_from_current_v064_evaluator(self):
        bad=copy.deepcopy(self.r1);bad["status"]="PASS_OFFLINE_ONLY"
        with self.assertRaisesRegex(p.SchedulerBlocked,"UNVERIFIED_NATIVE_STAT_RESULT"):
            p.initial_state(self.c,self.b,[bad],100,2)

if __name__=="__main__":unittest.main()
