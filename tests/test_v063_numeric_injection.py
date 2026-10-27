"""v063: only numeric stat input/output, no proc/emulation."""
import copy,json,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v063_numeric_injection as p

BASE="""mage="NumericTrial"
source=default
spec=arcane
head=sample_head,id=100,ilevel=334,source=local
trinket1=sample_trinket,id=250224,ilevel=334,source=local
temporary_enchant=main_hand:thalassian_phoenix_oil_2
flask=flask_of_the_blood_knights_2
iterations=60
gear_crit_rating=600
gear_haste_rating=975
gear_mastery_rating=1115
gear_versatility_rating=329
json2=/tmp/report.json
"""
BASE2=BASE.replace("gear_crit_rating=600","gear_crit_rating=750").replace(
"gear_haste_rating=975","gear_haste_rating=825")
OFFSET={"crit_rating":0,"haste_rating":165,"mastery_rating":0,"versatility_rating":0}
def fake_doc(source,offset=None,revision="7bc10711b5"):
    inp=p.input_parts(source)
    offset=offset or OFFSET
    final={k:inp["gear_override"][k]+offset[k] for k in p.STATS}
    return {"report_version":"2.0.0","git_revision":revision,
            "sim":{"players":[{"collected_data":{
            "buffed_stats":{"stats":final},
            "dps":{"count":59,"mean":190000.,"mean_std_dev":750.}},
            "gear":{}}]}}
def witness():
    return [{"input":BASE,"native":fake_doc(BASE)},
            {"input":BASE2,"native":fake_doc(BASE2)}]
class NumericInjection(unittest.TestCase):
    def test_duplicate_or_missing_gear_rejected(self):
        with self.assertRaisesRegex(p.InjectionError,"DUPLICATE_GEAR_STAT_OVERRIDE"):
            p.input_parts(BASE+"gear_crit_rating=200\n")
        with self.assertRaisesRegex(p.InjectionError,"FOUR_GEAR_RATINGS_REQUIRED"):
            p.input_parts(BASE.replace("gear_mastery_rating=1115\n",""))
    def test_legacy_template_without_json2_emits_one_strict_native_destination(self):
        template=BASE.replace("json2=/tmp/report.json\n","")
        self.assertNotIn("json2=",template)
        with self.assertRaisesRegex(p.InjectionError,
                                    "MISSING_OR_DUPLICATE_INPUT:json2="):
            p.input_parts(template)
        bare=p.input_parts(template,allow_missing_json2_template=True)
        pinned=p.input_parts(BASE)
        self.assertEqual(bare["stable_sha256"],pinned["stable_sha256"])
        target={"crit_rating":600,"haste_rating":1140,
                "mastery_rating":1115,"versatility_rating":329}
        flask={"crit_rating":0,"haste_rating":165,
               "mastery_rating":0,"versatility_rating":0}
        with tempfile.TemporaryDirectory() as td:
            folder=pathlib.Path(td)
            generated=p.render_static_chmv_candidate(
                template,target,flask,folder/"static.json",35)
            self.assertEqual(sum(s.startswith("json2=")
                                 for s in generated["input"].splitlines()),1)
            self.assertIn("json2="+str((folder/"static.json").resolve()),
                          generated["input"])
            self.assertEqual(p.input_parts(generated["input"])["stable_sha256"],
                             bare["stable_sha256"])
            cal=p.calibrate(witness())
            result=p.render_candidate(template,cal,target,
                                      folder/"candidate.json",60)
            self.assertEqual(sum(s.startswith("json2=")
                                 for s in result["input"].splitlines()),1)
            self.assertEqual(p.input_parts(result["input"])["stable_sha256"],
                             bare["stable_sha256"])

    def test_template_output_duplicate_and_missing_iterations_still_block(self):
        for source in (BASE+"json2=/tmp/another.json\n",
                       BASE.replace("iterations=60\n","")):
            with self.subTest(case=source[-40:]):
                with self.assertRaisesRegex(
                    p.InjectionError,"MISSING_OR_DUPLICATE_INPUT"):
                    p.input_parts(source,allow_missing_json2_template=True)

    def test_numeric_offset_from_two_independent_settings(self):
        cal=p.calibrate(witness())
        self.assertEqual(cal["net_input_to_json2_rating_offset"],OFFSET)
        self.assertEqual(cal["witnesses"],2)
        self.assertTrue(cal["no_item_effect_inspection"])
    def test_nonconstant_numeric_offset_refused(self):
        data=witness(); data[1]["native"]["sim"]["players"][0][
          "collected_data"]["buffed_stats"]["stats"]["haste_rating"]+=2
        with self.assertRaisesRegex(p.InjectionError,"NONCONSTANT_NUMERIC"):
            p.calibrate(data)
    def test_single_witness_not_allowed(self):
        with self.assertRaisesRegex(p.InjectionError,"TWO_NUMERIC_WITNESSES"):
            p.calibrate(witness()[:1])
    def test_different_simc_revision_refused(self):
        data=witness();data[1]["native"]["git_revision"]="abababab"
        with self.assertRaisesRegex(p.InjectionError,"NATIVE_REVISION_DRIFT"):
            p.calibrate(data)
    def test_equipment_line_or_consumable_changed_refused(self):
        data=witness()
        data[1]["input"]=data[1]["input"].replace("id=250224","id=250244")
        with self.assertRaisesRegex(p.InjectionError,"NOT_SAME_SCENARIO"):
            p.calibrate(data)
    def test_official_T_3152_is_not_oil_included(self):
        target={"crit_rating":600,"haste_rating":1108,
                "mastery_rating":1115,"versatility_rating":329}
        self.assertEqual(sum(target.values()),3152)
        cal=p.calibrate(witness())
        with tempfile.TemporaryDirectory() as d:
            output=p.render_candidate(BASE,cal,target,
                 pathlib.Path(d)/"report.json",60)
            self.assertEqual(output["raw_gear_override"]["haste_rating"],943)
            self.assertEqual(sum(output["expected_json2_rating"].values()),3152)
            self.assertIn("temporary_enchant=main_hand:thalassian_phoenix_oil_2",
                          output["input"])
            self.assertIn("id=250224",output["input"])
            self.assertEqual(output["stable_profile_sha256"],
                             cal["stable_profile_sha256"])
    def test_intentionally_changed_profile_does_not_reuse_other_offset(self):
        cal=p.calibrate(witness())
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(p.InjectionError,
                   "CANDIDATE_PROFILE_DIFFERS_FROM_CALIBRATION"):
                p.render_candidate(BASE.replace("id=250224","id=250244"),cal,
                  {"crit_rating":600,"haste_rating":1108,
                   "mastery_rating":1115,"versatility_rating":329},
                   pathlib.Path(d)/"result.json",60)
    def test_final_native_target_and_dps(self):
        cal=p.calibrate(witness())
        target={"crit_rating":600,"haste_rating":1108,
                "mastery_rating":1115,"versatility_rating":329}
        with tempfile.TemporaryDirectory() as d:
            rendered=p.render_candidate(BASE,cal,target,
                pathlib.Path(d)/"report.json",60)
            native=fake_doc(rendered["input"])
            r=p.validate_native(native,rendered,cal)
            self.assertEqual(r["status"],"PASS_NATIVE_NUMERIC_RATING_AND_DPS")
            self.assertEqual(r["actual_buffed_stats_rating"],target)
            self.assertTrue(r["external_component_source_attribution_not_claimed"])
    def test_mismatched_json2_rating_refused_even_when_dps_present(self):
        cal=p.calibrate(witness())
        target={"crit_rating":600,"haste_rating":1108,
                "mastery_rating":1115,"versatility_rating":329}
        with tempfile.TemporaryDirectory() as d:
            rendered=p.render_candidate(BASE,cal,target,
                pathlib.Path(d)/"report.json",60)
            native=fake_doc(rendered["input"])
            native["sim"]["players"][0]["collected_data"]["buffed_stats"]["stats"]["crit_rating"]+=1
            with self.assertRaisesRegex(p.InjectionError,"FINAL_NUMERIC_RATING_MISMATCH"):
                p.validate_native(native,rendered,cal)
    def test_separate_result_statistical_uncertainty(self):
        r=p.compare_pair([{"dps_mean":190000,"dps_sem":700},
                          {"dps_mean":190050,"dps_sem":800}])
        self.assertFalse(r["statistically_separated_approx95"])
        self.assertIsNone(r["winner_if_separated"])
        self.assertFalse(r["global_optimum_proven"])
    def test_negative_raw_override_blocked(self):
        cal=p.calibrate(witness())
        target={"crit_rating":5,"haste_rating":10,
                "mastery_rating":1000,"versatility_rating":1500}
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(p.InjectionError,
                    "NEGATIVE_GEAR_RATING"):
                p.render_candidate(BASE,cal,target,pathlib.Path(d)/"r.json",60)
    def test_output_path_mutation_is_allowed_but_stat_case_not_mutable(self):
        cal=p.calibrate(witness())
        target={"crit_rating":600,"haste_rating":1108,
                "mastery_rating":1115,"versatility_rating":329}
        with tempfile.TemporaryDirectory() as d:
            r=p.render_candidate(BASE,cal,target,pathlib.Path(d)/"r.json",120)
            self.assertIn("iterations=120",r["input"])
            self.assertEqual(p.input_parts(r["input"])["stable_sha256"],
                             cal["stable_profile_sha256"])

if __name__=="__main__":unittest.main()
