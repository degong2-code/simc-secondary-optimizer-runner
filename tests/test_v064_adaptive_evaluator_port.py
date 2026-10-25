"""v064: scheduler-neutral SimC candidate port / real JSON2 replay contract."""
import copy,json,pathlib,sys,tempfile,unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v046_static_item_cache as native
import v055_simc_item_selection as selector
import v062_static_budget_bridge as sb
import v063_numeric_injection as calibration
import v063_official_T_two_native as ref_runner
import v064_adaptive_evaluator_port as port
from test_v062_static_budget_bridge import record
from test_v063_numeric_injection import fake_doc

SIMC_SHA="a"*64
CHMV1={"crit_rating":400,"haste_rating":400,"mastery_rating":400,"versatility_rating":403}
CHMV2={"crit_rating":230,"haste_rating":570,"mastery_rating":400,"versatility_rating":403}

def make_fixture():
    original=(ROOT/"inputs"/"v031r3_reference.simc").read_text()
    modified,_=selector.apply_selection(original,[
        {"slot":"trinket1","item_id":250224,"ilevel":334,"options":{}}])
    modified+="json2=/tmp/old_result.json\n"
    contract,standard=ref_runner.scenario_for_bounded_reference(modified)
    local=native.empty_cache()
    items=standard+sum(
      (contract["scenario"]["equipment"][k] for k in ("tier","special","crafted")),[])
    for row in items:record(local,row)
    budget=sb.compile_static_budget(contract,standard,local)
    # Two numeric witnesses differ ONLY in gear_* rating, not selected items.
    second=modified.replace("gear_crit_rating=600","gear_crit_rating=750").replace(
        "gear_haste_rating=975","gear_haste_rating=825")
    cal=calibration.calibrate([
        {"input":modified,"native":fake_doc(modified)},
        {"input":second,"native":fake_doc(second)}])
    return contract,budget,cal,modified

class AdaptivePort(unittest.TestCase):
    def setUp(self):
        self.c,self.b,self.k,self.profile=make_fixture()
    def test_valid_external_scheduler_candidate(self):
        with tempfile.TemporaryDirectory() as folder:
            req=port.make_request(self.c,self.b,self.k,self.profile,SIMC_SHA,
                                  CHMV1,60,pathlib.Path(folder)/"native.json")
            self.assertEqual(req["status"],"PROPOSED_VALID_NO_NATIVE_YET")
            self.assertEqual(req["official_total"],1603)
            self.assertEqual(req["profile_binding"]["slots_bound"],15)
            self.assertTrue(req["profile_binding"]["two_trinkets_bound"])
            self.assertIn("id=250224",req["input"])
            self.assertIn("embellishment=arcanoweave_lining",req["input"])
            self.assertEqual(req["raw_gear_override"]["haste_rating"],235)
    def test_real_profile_selection_integrity(self):
        with tempfile.TemporaryDirectory() as folder:
            altered=self.profile.replace("id=250224","id=250244")
            # Unchanged numeric offset alone must not validate altered gear.
            with self.assertRaisesRegex(port.PortBlocked,"PROFILE_GEAR_ID_LEVEL_OPTIONS_DRIFT"):
                port.make_request(self.c,self.b,self.k,altered,SIMC_SHA,
                                  CHMV1,60,pathlib.Path(folder)/"x.json")
            altered=self.profile.replace("flask_of_the_blood_knights_2",
                                         "other_flask")
            with self.assertRaisesRegex(port.PortBlocked,"PROFILE_CONSUMABLE_DRIFT"):
                port.make_request(self.c,self.b,self.k,altered,SIMC_SHA,
                                  CHMV1,60,pathlib.Path(folder)/"x.json")
    def test_input_to_json2_exact_native_numeric_passthrough(self):
        with tempfile.TemporaryDirectory() as folder:
            req=port.make_request(self.c,self.b,self.k,self.profile,SIMC_SHA,
                                  CHMV1,60,pathlib.Path(folder)/"json2.json")
            doc=fake_doc(req["input"])
            raw=json.dumps(doc,sort_keys=True).encode()
            observed=port.ingest_native(req,doc,self.k,raw)
            self.assertEqual(observed["dps_mean"],190000)
            self.assertEqual(observed["rating_actual"],CHMV1)
            self.assertTrue(observed["no_simc_effect_independent_validation"])
            self.assertEqual(port.verify_disk_cache(req,self.k,observed,raw),observed)
    def test_forged_cache_or_changed_json2_digest_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            req=port.make_request(self.c,self.b,self.k,self.profile,SIMC_SHA,
                                  CHMV1,60,pathlib.Path(folder)/"json2.json")
            doc=fake_doc(req["input"])
            raw=json.dumps(doc,sort_keys=True).encode()
            obs=port.ingest_native(req,doc,self.k,raw)
            corrupt=copy.deepcopy(obs);corrupt["dps_mean"]=999999
            with self.assertRaisesRegex(port.PortBlocked,"CACHE_RESULT_CHANGED"):
                port.verify_disk_cache(req,self.k,corrupt,raw)
            with self.assertRaisesRegex(port.PortBlocked,"CACHE_NATIVE_BYTES_DIGEST_MISMATCH"):
                port.verify_disk_cache(req,self.k,obs,raw+b"x")
            wrong=copy.deepcopy(req);wrong["case_key"]="b"*64
            with self.assertRaisesRegex(port.PortBlocked,"CACHE_IDENTITY_MISMATCH"):
                port.verify_disk_cache(wrong,self.k,obs,raw)
    def test_missing_native_rating_rejected_not_fake_zero(self):
        with tempfile.TemporaryDirectory() as folder:
            req=port.make_request(self.c,self.b,self.k,self.profile,SIMC_SHA,
                                  CHMV1,60,pathlib.Path(folder)/"json2.json")
            doc=fake_doc(req["input"])
            del doc["sim"]["players"][0]["collected_data"]["buffed_stats"]["stats"]["haste_rating"]
            with self.assertRaisesRegex(calibration.InjectionError,"NATIVE_RATING_UNOBSERVED"):
                port.ingest_native(req,doc,self.k)
    def test_bad_proposed_budget_or_floor_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            wrong=dict(CHMV1,crit_rating=401)
            with self.assertRaisesRegex(calibration.InjectionError,"OFFICIAL_T_TARGET_MISMATCH"):
                port.make_request(self.c,self.b,self.k,self.profile,SIMC_SHA,
                                  wrong,60,pathlib.Path(folder)/"x.json")
            wrong={"crit_rating":1000,"haste_rating":200,
                   "mastery_rating":200,"versatility_rating":203}
            with self.assertRaisesRegex(calibration.InjectionError,"TARGET_OUTSIDE_SPECIAL_FLOOR_OR_CAP"):
                port.make_request(self.c,self.b,self.k,self.profile,SIMC_SHA,
                                  wrong,60,pathlib.Path(folder)/"x.json")
    def test_iteration_and_queue_bounded_by_scenario(self):
        with tempfile.TemporaryDirectory() as folder:
            queue=port.plan_queue(
              [{"target":CHMV1,"iterations":60},{"target":CHMV2,"iterations":60}],
              self.c,self.b,self.k,self.profile,SIMC_SHA,folder)
            self.assertEqual(len(queue),2)
            self.assertNotEqual(queue[0]["case_key"],queue[1]["case_key"])
            with self.assertRaisesRegex(port.PortBlocked,"DUPLICATE_PROPOSED_EVALUATION"):
                port.plan_queue([{"target":CHMV1,"iterations":60}]*2,
                  self.c,self.b,self.k,self.profile,SIMC_SHA,folder)
            with self.assertRaisesRegex(port.PortBlocked,"PROPOSALS_EXCEED_CONFIGURED_NATIVE_BUDGET"):
                port.plan_queue([{"target":CHMV1,"iterations":60}]*3,
                  self.c,self.b,self.k,self.profile,SIMC_SHA,folder)
            with self.assertRaisesRegex(port.PortBlocked,"ITERATION_OUTSIDE_SCENARIO_POLICY"):
                port.make_request(self.c,self.b,self.k,self.profile,SIMC_SHA,
                                  CHMV1,61,pathlib.Path(folder)/"z.json")
    def test_cache_revision_or_profile_change_does_not_reuse_result(self):
        with tempfile.TemporaryDirectory() as folder:
            k1=port.make_request(self.c,self.b,self.k,self.profile,SIMC_SHA,
                                  CHMV1,60,pathlib.Path(folder)/"a.json")["case_key"]
            k2=port.make_request(self.c,self.b,self.k,self.profile,"b"*64,
                                  CHMV1,60,pathlib.Path(folder)/"b.json")["case_key"]
            k3=port.make_request(self.c,self.b,self.k,self.profile,SIMC_SHA,
                                  CHMV1,60,pathlib.Path(folder)/"c.json")["case_key"]
            self.assertNotEqual(k1,k2)
            self.assertEqual(k1,k3) # JSON2 filesystem path is not in key.
    def test_materially_distinct_near_alternative_if_large_move(self):
        with tempfile.TemporaryDirectory() as folder:
            requests=port.plan_queue(
              [{"target":CHMV1,"iterations":60},{"target":CHMV2,"iterations":60}],
              self.c,self.b,self.k,self.profile,SIMC_SHA,folder)
            observations=[]
            for n,req in enumerate(requests):
                native_doc=fake_doc(req["input"])
                native_doc["sim"]["players"][0]["collected_data"]["dps"]["mean"]-=n*500
                observations.append(port.ingest_native(req,native_doc,self.k))
            summ=port.summarize(observations,1603)
            self.assertEqual(summ["evaluated"],2)
            self.assertEqual(len(summ["materially_distinct_near_performing"]),1)
            self.assertEqual(summ["materially_distinct_near_performing"][0]["rating_moved"],170)
            self.assertFalse(summ["global_optimum_proven"])
            self.assertFalse(summ["selection_engine_connected"])
    def test_insufficient_rating_distance_no_forced_alternative(self):
        with tempfile.TemporaryDirectory() as folder:
            small={"crit_rating":430,"haste_rating":370,"mastery_rating":400,"versatility_rating":403}
            rq=port.plan_queue(
              [{"target":CHMV1,"iterations":60},{"target":small,"iterations":60}],
              self.c,self.b,self.k,self.profile,SIMC_SHA,folder)
            observations=[port.ingest_native(x,fake_doc(x["input"]),self.k) for x in rq]
            result=port.summarize(observations,1603)
            self.assertEqual(result["materially_distinct_near_performing"],[])
    def test_scenario_digest_mismatch_cannot_mix_budget(self):
        with tempfile.TemporaryDirectory() as folder:
            cfg=copy.deepcopy(self.c);cfg["scenario_digest"]="0"*64
            with self.assertRaisesRegex(calibration.InjectionError,"P1_P2_SCENARIO_DRIFT"):
                port.make_request(cfg,self.b,self.k,self.profile,SIMC_SHA,
                                  CHMV1,60,pathlib.Path(folder)/"x.json")

if __name__=="__main__":unittest.main()
