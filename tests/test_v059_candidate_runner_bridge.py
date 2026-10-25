"""v059 selected equipment -> candidate -> SimC Native stat/DPS only."""
import copy,hashlib,json,pathlib,sys,unittest,math,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import pilot
import v059_candidate_runner_bridge as m

class ScenarioBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference,_=pilot.source()
        cls.plan=m.plan(cls.reference,m.DEFAULT_SELECTED,m.DEFAULT_TARGETS)
    def test_baseline_total_and_two_target_floors(self):
        s=self.plan
        self.assertEqual(s["budget"]["G"],2849)
        self.assertEqual(s["budget"]["T"],3184)
        self.assertEqual(s["budget"]["O"]["crit_rating"],16)
        self.assertEqual(s["budget"]["O"]["haste_rating"],16)
        self.assertEqual(len(s["cases"]),2)
        self.assertEqual(len({x["case_key"] for x in s["cases"]}),2)
        self.assertFalse(s["proc_gate"])
        self.assertFalse(s["original_v015_v016_engine_integrated"])
    def test_trinket_without_json2_stat_is_an_allowed_selection(self):
        self.assertIn("trinket1=selected_250224,id=250224,ilevel=334,source=local",self.plan["profile"])
        self.assertTrue(self.plan["selection"]["trinket_static_cache_required"] is False)
        self.assertTrue(self.plan["budget"]["external_trinket_static_not_in_G"])
    def test_original_tier_gems_flask_gear_and_two_embellishments_survive(self):
        s=self.plan["profile"]
        self.assertEqual(s.count("embellishment=arcanoweave_lining"),2)
        self.assertEqual(s.count("temporary_enchant=main_hand:thalassian_phoenix_oil_2"),1)
        self.assertIn("food=royal_roast",s)
        self.assertIn("flask=flask_of_the_blood_knights_2",s)
        self.assertIn("head=v020_head_271564",s)
        self.assertIn("gem_id=240967",s)
        self.assertEqual(sum(x.startswith("trinket2=") for x in s.splitlines()),1)
    def test_native_input_has_exact_overrides_once(self):
        for x in self.plan["cases"]:
            with tempfile.TemporaryDirectory() as d:
                src=m.compose_input(self.plan["profile"],x,pathlib.Path(d)/"native.json",60)
                self.assertEqual(src.count("json2="),1)
                self.assertIn("gear_haste_rating="+str(x["target"]["haste_rating"]-165),src)
                self.assertEqual(sum(v.startswith("gear_haste_rating=") for v in src.splitlines()),1)
                self.assertIn("iterations=60",src)
    def test_infeasible_lower_than_calibrated_flask_rejected(self):
        target=dict(m.DEFAULT_TARGETS[0]);target["haste_rating"]=100
        target["crit_rating"]+=1040
        # would breach 50% anyway; ensure calibration condition is independently
        # detected on a feasible distribution.
        target={"crit_rating":1050,"haste_rating":100,"mastery_rating":1000,"versatility_rating":1034}
        with self.assertRaisesRegex(m.ScenarioBlocked,"NATIVE_CALIBRATION_CANNOT_INJECT_THIS_TARGET"):
            m.plan(self.reference,m.DEFAULT_SELECTED,[target])
    def test_double_count_total_refused(self):
        invalid=dict(m.DEFAULT_TARGETS[0]);invalid["haste_rating"]+=165
        with self.assertRaisesRegex(m.ScenarioBlocked,"CHMV_BUDGET_MISMATCH"):
            m.plan(self.reference,m.DEFAULT_SELECTED,[invalid])
    def test_manual_special_floor_is_within_G_not_extra_rating(self):
        fixed={"crit_rating":0,"haste_rating":0,"mastery_rating":201,"versatility_rating":0}
        p=m.plan(self.reference,m.DEFAULT_SELECTED,m.DEFAULT_TARGETS,special_fixed=fixed)
        self.assertEqual(p["budget"]["T"],3184)
        self.assertEqual(p["budget"]["special_fixed"]["mastery_rating"],201)
        bad=copy.deepcopy(m.DEFAULT_TARGETS[0])
        bad["mastery_rating"]=200;bad["crit_rating"]+=915
        with self.assertRaises(m.ScenarioBlocked): m.plan(self.reference,m.DEFAULT_SELECTED,[bad],special_fixed=fixed)
    def test_adaptive_projection_sum_floor_cap(self):
        minimum={"crit_rating":166,"haste_rating":16,"mastery_rating":201,"versatility_rating":0}
        v=m.project([1,3,2,1],3184,minimum)
        self.assertEqual(sum(v.values()),3184)
        self.assertTrue(all(minimum[k]<=v[k]<=1592 for k in m.STATS))
    def test_source_hash_part_of_case_cache_identity(self):
        a=self.plan
        b=m.plan(self.reference,m.DEFAULT_SELECTED,m.DEFAULT_TARGETS)
        self.assertEqual(a["cases"][0]["case_key"],b["cases"][0]["case_key"])
        r=copy.deepcopy(m.DEFAULT_SELECTED);r[0]["item_id"]=281215
        c=m.plan(self.reference,r,m.DEFAULT_TARGETS)
        self.assertNotEqual(a["cases"][0]["case_key"],c["cases"][0]["case_key"])
    def test_sample_only_json2_has_mean_sem_and_static_not_proc(self):
        case=self.plan["cases"][0]
        d={"report_version":"2.0.0","git_revision":"abc",
           "sim":{"players":[{"collected_data":{
             "buffed_stats":{"stats":{k:float(v) for k,v in case["target"].items()}},
             "dps":{"count":59,"mean":230000.0,"mean_std_dev":750.0}}}]}}
        x=m.observe_result(d,case)
        self.assertEqual(x["status"],"PASS_NATIVE_CHMV_AND_DPS")
        self.assertFalse(x["native_effect_details_not_interpreted"] is False)
        self.assertEqual(x["dps_sem"],750)
    def test_native_wrong_final_rating_fails_even_when_dps_present(self):
        case=self.plan["cases"][0]
        d={"report_version":"2.0.0",
           "sim":{"players":[{"collected_data":{
             "buffed_stats":{"stats":{k:float(v) for k,v in case["target"].items()}},
             "dps":{"count":59,"mean":200000.0,"mean_std_dev":1000.0}}}]}}
        d["sim"]["players"][0]["collected_data"]["buffed_stats"]["stats"]["haste_rating"]+=1
        with self.assertRaisesRegex(m.ScenarioBlocked,"SIMC_FINAL_CHMV_MISMATCH"):
            m.observe_result(d,case)
    def test_comparison_is_uncertainty_not_false_global_optimum(self):
        data=[{"dps_mean":210000,"dps_sem":700},
              {"dps_mean":210100,"dps_sem":700}]
        comparison=m.compare(data)
        self.assertTrue(comparison["overlapping_or_inconclusive"])
        self.assertIsNone(comparison["winner_if_separated"])
        self.assertEqual(comparison["status"],"PAIRWISE_STATISTIC_ONLY_NOT_GLOBAL_OPTIMUM")
    def test_no_silent_proc_checks_in_adapter(self):
        self.assertTrue(self.plan["item_effects_owned_by_simc"])
        self.assertFalse(self.plan["official_policy_promoted"])
        self.assertEqual(len(self.plan["selection"]["selected"]),1)
    def test_nonallowed_expensive_iteration_rejected(self):
        with self.assertRaisesRegex(m.ScenarioBlocked,"ITERATION_BOUNDS"):
            m.plan(self.reference,m.DEFAULT_SELECTED,m.DEFAULT_TARGETS,iterations=2000)

if __name__=="__main__":unittest.main()
