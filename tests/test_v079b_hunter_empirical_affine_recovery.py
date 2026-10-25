"""v079B synthetic numerical affine transfer + original constant regression.

No synthetic data is reported as real Native; only Actions source-reused JSON2
can establish actual Hunter cross-class acceptance.
"""
import pathlib,sys,tempfile,unittest,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v063_numeric_injection as numeric
import v079b_hunter_empirical_affine_recovery as recovery
from test_v063_numeric_injection import witness as constant_witness

SOURCE='''hunter="EmpiricalTest"
spec=beast_mastery
race=troll
gear_crit_rating=700
gear_haste_rating=700
gear_mastery_rating=700
gear_versatility_rating=700
iterations=35
json2=/tmp/ref.json
'''
def text_of(c,h,m,v):
    t=SOURCE
    for k,n in (("crit",c),("haste",h),("mastery",m),("versatility",v)):
        t=t.replace("gear_"+k+"_rating=700","gear_"+k+"_rating="+str(n))
    return t
def fake(source):
    p=numeric.input_parts(source)["gear_override"]
    output={k:p[k] for k in numeric.STATS}
    output["crit_rating"]=round(1.04*p["crit_rating"])
    output["haste_rating"]=p["haste_rating"]+165
    return {"report_version":"2.0.0","git_revision":"7bc10711b5",
      "sim":{"players":[{"collected_data":{
      "buffed_stats":{"stats":output},
      "dps":{"count":34,"mean":190000.0,"mean_std_dev":800.0}}}]}}
def three():
    cases=[text_of(700,700,700,700),
           text_of(650,750,700,700),
           text_of(700,700,650,750)]
    return [{"input":x,"native":fake(x)} for x in cases]

class MeasuredRatingTransfer(unittest.TestCase):
    def test_prior_constant_calibration_remains_byte_compatible(self):
        result=numeric.calibrate(constant_witness())
        self.assertEqual(result["status"],"TWO_NATIVE_NUMERIC_OFFSET_WITNESSES_AGREE")
        self.assertNotIn("empirical_affine_transfer",result)

    def test_real_shape_three_witnesses_identify_four_numerical_axes(self):
        result=numeric.calibrate_affine(three())
        self.assertEqual(result["witnesses"],3)
        self.assertTrue(result["no_item_effect_inspection"])
        crit=result["empirical_affine_transfer"]["crit_rating"]
        self.assertEqual((crit["slope_numerator"],crit["slope_denominator"]),(26,25))
        haste=result["empirical_affine_transfer"]["haste_rating"]
        self.assertEqual(haste["intercept_numerator"],165)
        self.assertEqual(haste["slope_numerator"],1)

    def test_affine_target_render_and_strict_native_json2(self):
        result=numeric.calibrate_affine(three())
        raw=text_of(709,720,650,721)
        target=numeric.read_rating(fake(raw)["sim"]["players"][0])
        with tempfile.TemporaryDirectory() as d:
            rendered=numeric.render_candidate(SOURCE,result,target,
                pathlib.Path(d)/"result.json",35)
            observed=fake(rendered["input"])
            checked=numeric.validate_native(observed,rendered,result)
        self.assertEqual(checked["requested_json2_rating"],target)
        self.assertEqual(checked["actual_buffed_stats_rating"],target)

    def test_affine_one_unobserved_axis_cannot_claim_complete_calibration(self):
        with self.assertRaisesRegex(numeric.InjectionError,
                                   "AFFINE_THREE_OR_MORE"):
            numeric.calibrate_affine(three()[:2])
        bad=three()
        bad[2]["input"]=text_of(700,700,700,700)
        bad[2]["native"]=fake(bad[2]["input"])
        with self.assertRaisesRegex(numeric.InjectionError,
                                   "AFFINE_UNOBSERVED_STAT_VARIATION"):
            numeric.calibrate_affine(bad)

    def test_no_original_genuine_artifact_blocks_new_native(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            rc=recovery.run(ROOT/"integration_probes/fixtures/v079_upstream_mid2_hunter_beast_mastery_reference.simc",
                            root/"missing",root/"out")
            self.assertEqual(rc,3)
            receipt=json.loads((root/"out"/"V079B_RECEIPT.json").read_text())
            self.assertEqual(receipt["status"],"BLOCKED_OR_PARTIAL")
            self.assertEqual(receipt["fresh_native_calls_this_invocation"],0)

if __name__=="__main__":unittest.main()
