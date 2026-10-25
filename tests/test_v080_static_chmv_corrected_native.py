"""v080 corrected STATIC c semantics. All examples here are synthetic only."""
import pathlib,sys,tempfile,unittest,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v063_numeric_injection as n
import v080_static_chmv_corrected_native as v080
import v079_hunter_ranged_generic_native as hunter
import v061_scenario_contract as scenario

UPSTREAM=ROOT/"integration_probes/fixtures/v079_upstream_mid2_hunter_beast_mastery_reference.simc"

class V080StaticCHMVContract(unittest.TestCase):
    def profile(self,folder):
        return hunter.source_profile(UPSTREAM.read_text("utf8"),folder)[0]
    def test_official_static_c_minus_declared_F_exact_not_talent_inverted(self):
        with tempfile.TemporaryDirectory() as d:
            profile=self.profile(d)
            target=dict(zip(scenario.STATS,(700,699,699,699)))
            f=dict(zip(scenario.STATS,(0,165,0,0)))
            rendered=n.render_static_chmv_candidate(
                profile,target,f,pathlib.Path(d)/"case"/"result.json",35)
        self.assertEqual(rendered["raw_gear_override"],{
            "crit_rating":700,"haste_rating":534,
            "mastery_rating":699,"versatility_rating":699})
        self.assertEqual(sum(rendered["raw_gear_override"].values()),2632)
        self.assertEqual(sum(target.values()),2797)
        self.assertFalse(rendered["buffed_stats_target_parity_required"])

    def test_apl_source_talents_and_gear_stable_hash_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            profile=self.profile(d)
            rendered=n.render_static_chmv_candidate(profile,
              dict(zip(scenario.STATS,(700,699,699,699))),
              dict(zip(scenario.STATS,(0,165,0,0))),
              pathlib.Path(d)/"r.json",35)
        a=n.input_parts(profile)["stable_sha256"]
        b=n.input_parts(rendered["input"])["stable_sha256"]
        self.assertEqual(a,b)

    def test_buffed_crit_differs_from_static_target_and_dps_is_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            profile=self.profile(d)
            raw=n.render_static_chmv_candidate(profile,
               dict(zip(scenario.STATS,(700,699,699,699))),
               dict(zip(scenario.STATS,(0,165,0,0))),
               pathlib.Path(d)/"r.json",35)
        doc={"report_version":"2.0.0","git_revision":"7bc10711b5",
             "sim":{"players":[{"collected_data":{
               "buffed_stats":{"stats":{"crit_rating":728,"haste_rating":699,
                     "mastery_rating":699,"versatility_rating":699}},
               "dps":{"count":34,"mean":190000.0,"mean_std_dev":750.0}}}]}}
        result=n.validate_static_native(doc,raw,"7bc10711b5")
        self.assertEqual(result["target_static_CHMV_c"]["crit_rating"],700)
        self.assertEqual(result["actual_buffed_stats_rating"]["crit_rating"],728)
        self.assertEqual(result["dps_mean"],190000.0)

    def test_missing_F_coverage_or_target_below_F_fails(self):
        with tempfile.TemporaryDirectory() as d:
            profile=self.profile(d)
            with self.assertRaisesRegex(n.InjectionError,
                    "STATIC_TARGET_BELOW_DECLARED_FLASK_VECTOR"):
                n.render_static_chmv_candidate(
                  profile,dict(zip(scenario.STATS,(700,100,800,1197))),
                  dict(zip(scenario.STATS,(0,165,0,0))),
                  pathlib.Path(d)/"r.json",35)

    def test_real_hunter_historical_artifact_required(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            ret=v080.run(UPSTREAM,root/"missing",root/"out")
            self.assertEqual(ret,3)
            status=json.loads((root/"out"/"V080_RECEIPT.json").read_text())
            self.assertEqual(status["status"],"BLOCKED_OR_PARTIAL")
            self.assertEqual(status["new_native_this_invocation"],0)

if __name__=="__main__":
    unittest.main()
