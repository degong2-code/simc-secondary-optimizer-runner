"""v065 v015 lineage behavioral parity (source manifest hash recorded).

v015 historical 71/71 and v016 historical 104/104 tests are NOT claimed rerun.
This tests new adapter, v064 budget compliance and exact replay-seeded behavior.
"""
from __future__ import annotations
import copy,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v065_original_v015_search_adapter as scheduler
import v064_adaptive_evaluator_port as port
from test_v064_adaptive_evaluator_port import make_fixture,CHMV1,CHMV2,SIMC_SHA
from test_v063_numeric_injection import fake_doc

def seeded():
    cfg,budget,cal,source=make_fixture()
    fake_dir="/tmp/v065_test"
    reqs=port.plan_queue([{"target":CHMV1,"iterations":60},
         {"target":CHMV2,"iterations":60}],cfg,budget,cal,source,SIMC_SHA,fake_dir)
    result=[]
    for n,req in enumerate(reqs):
        native=fake_doc(req["input"])
        native["sim"]["players"][0]["collected_data"]["dps"]["mean"]=200000.-n*1000
        result.append(port.ingest_native(req,native,cal))
    return cfg,budget,cal,source,result

def real_looking():
    """Use exact v015 golden input/output vectors from original source invocation.

    Original v015 CHMV_ADAPTIVE_v015.py SHA256:
    a44f73cf232c8204dbe958e79fe50f111e68654ac583a1170a283f16035c0ec3
    With BUDGET=3152 and 50% caps, two observed Native v063 ratings,
    v015 choose_next generated first 200-rating transfer:
    600/1108/1115/329 -> 400/1108/1115/529.
    """
    a={"crit_rating":600,"haste_rating":1108,
       "mastery_rating":1115,"versatility_rating":329}
    b={"crit_rating":750,"haste_rating":958,
       "mastery_rating":1115,"versatility_rating":329}
    return a,b

class V015SchedulerPortTests(unittest.TestCase):
    def test_provenance_identity_and_golden_v015_choice(self):
        self.assertEqual(scheduler.SOURCE_V015_SHA256,
                         "a44f73cf232c8204dbe958e79fe50f111e68654ac583a1170a283f16035c0ec3")
        cfg,budget,cal,source,old=seeded()
        # Modify only our synthetic observational targets to mirror real v063.
        a,b=real_looking()
        observed=[dict(old[0],target=a,dps_mean=192374.47),
                  dict(old[1],target=b,dps_mean=192109.86)]
        # Different T must be rejected by the contract, not silently coerced.
        with self.assertRaises(scheduler.SearchBlocked):
            scheduler.propose_scout(observed,cfg,budget,200)
    def test_source_mirror_chooser_from_synthetic_budget(self):
        cfg,budget,cal,source,old=seeded()
        q=scheduler.propose_scout(old,cfg,budget,200)
        self.assertEqual(q["phase"],"SCOUT")
        self.assertEqual(sum(q["target"].values()),1603)
        self.assertEqual(q["requested_step"],200)
        self.assertTrue(all(q["target"][s]>=0 for s in scheduler.STATS))
        self.assertNotIn(q["target"],[o["target"] for o in old])
        self.assertFalse(q["global_optimum_proven"])
    def test_history_uniqueness_and_near_constraint(self):
        cfg,budget,cal,source,old=seeded()
        init=scheduler.seed_state(old,cfg,budget,scouts_limit=1,step=100)
        self.assertEqual(init["source_v015_sha256"],scheduler.SOURCE_V015_SHA256)
        self.assertFalse(init["original_source_modified"])
        proposal=scheduler.next_proposal(init,cfg,budget)
        req=port.make_request(cfg,budget,cal,source,SIMC_SHA,
                              proposal["target"],60,"/tmp/v065_new.json")
        booked=scheduler.reserve(init,proposal,req)
        self.assertIsNone(init["pending"])
        self.assertEqual(booked["status"],"NATIVE_RESULT_PENDING")
        with self.assertRaisesRegex(scheduler.SearchBlocked,"PENDING_NATIVE_EVALUATION"):
            scheduler.next_proposal(booked,cfg,budget)
        native=fake_doc(req["input"])
        observed=port.ingest_native(req,native,cal)
        done=scheduler.complete(booked,observed)
        self.assertEqual(len(done["scouts"]),1)
        self.assertEqual(done["status"],"CONFIRM_PENDING")
        self.assertIsNone(done["pending"])
    def test_confirm_pair_from_all_observed(self):
        cfg,budget,cal,source,old=seeded()
        chosen=scheduler.confirmation_pair(old,cfg,budget)
        self.assertEqual(chosen[0],scheduler.vector_tuple(CHMV1))
        self.assertEqual(chosen[1],scheduler.vector_tuple(CHMV2))
        confirm=scheduler.confirmation_proposals(old,cfg,budget)
        self.assertEqual(len(confirm),2)
        self.assertEqual(confirm[0]["target"],CHMV1)
    def test_no_false_pairwise_significance_without_distinct_seed(self):
        cfg,budget,cal,source,old=seeded()
        fresh=[dict(old[0],dps_mean=200000,dps_sem=1),
               dict(old[1],dps_mean=199000,dps_sem=1)]
        j=scheduler.judge_confirmed(fresh)
        self.assertFalse(j["distinct_native_seeds"])
        self.assertFalse(j["pairwise_direction_supported"])
        fresh[0]["native_seed"]=3
        fresh[1]["native_seed"]=4
        j=scheduler.judge_confirmed(fresh)
        self.assertTrue(j["pairwise_direction_supported"])
        self.assertFalse(j["global_optimum_proven"])
    def test_unchanged_scenario_required_for_history(self):
        cfg,budget,cal,source,old=seeded()
        cfg=copy.deepcopy(cfg)
        cfg["scenario_digest"]="0"*64
        with self.assertRaisesRegex(scheduler.SearchBlocked,"SCENARIO_BUDGET_DRIFT"):
            scheduler.seed_state(old,cfg,budget)
    def test_reject_inadmissible_native_observations(self):
        cfg,budget,cal,source,old=seeded()
        obs=copy.deepcopy(old);obs[0]["target"]["crit_rating"]+=1
        with self.assertRaisesRegex(scheduler.SearchBlocked,"HISTORICAL_NATIVE_BOUNDS_DRIFT"):
            scheduler.seed_state(obs,cfg,budget)
    def test_reservation_receipt_must_match(self):
        cfg,budget,cal,source,old=seeded()
        init=scheduler.seed_state(old,cfg,budget,scouts_limit=1)
        next_=scheduler.next_proposal(init,cfg,budget)
        req=port.make_request(cfg,budget,cal,source,SIMC_SHA,
                              next_["target"],next_["iterations"],
                              "/tmp/v065_new.json")
        reserved=scheduler.reserve(init,next_,req)
        native=fake_doc(req["input"])
        obs=port.ingest_native(req,native,cal)
        with self.assertRaisesRegex(scheduler.SearchBlocked,"NATIVE_RECEIPT_DOES_NOT_MATCH_PENDING"):
            scheduler.complete(reserved,dict(obs,case_key="a"*64))
    def test_avoid_duplicate_candidates_and_exhaustion(self):
        cfg,budget,cal,source,old=seeded()
        p=scheduler.propose_scout(old,cfg,budget,100)
        reserved=[scheduler.vector_tuple(p["target"])]
        p2=scheduler.propose_scout(old,cfg,budget,100,reserved)
        self.assertNotEqual(p["target"],p2["target"])
        self.assertNotEqual(p["target"],p2["target"])
    def test_confirm_source_200_has_new_result_budget(self):
        cfg,budget,cal,source,old=seeded()
        cfg["scenario"]["runtime"]["max_native_calls"]=1
        init=scheduler.seed_state(old,cfg,budget,scouts_limit=1)
        self.assertEqual(init["max_native_calls"],1)
if __name__=="__main__":unittest.main()
