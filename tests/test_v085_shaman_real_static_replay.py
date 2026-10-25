"""v085 static-c reclassification: offline safety and legacy input equivalence.

Actual source and JSON2 evidence are used only by the GitHub workflow. These
tests never substitute synthetic JSON2 as Native proof.
"""
import json,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v085_shaman_real_static_replay as audit
import v078_elemental_first_native as original
import v063_numeric_injection as numeric
import v061_scenario_contract as scenario

SOURCE=ROOT/"integration_probes/fixtures/v078_upstream_mid2_shaman_elemental_reference.simc"
class V085ShamanCorrectedStaticWitness(unittest.TestCase):
    def test_missing_real_native_blocks_and_has_zero_new_simc(self):
        with tempfile.TemporaryDirectory() as d:
            out=pathlib.Path(d)
            rc=audit.run(out/"missing_first",out/"missing_official",out/"result")
            self.assertEqual(rc,3)
            result=json.loads((out/"result"/"V085_RECEIPT.json").read_text())
            self.assertEqual(result["status"],"BLOCKED_OR_PARTIAL")
            self.assertEqual(result["new_native_this_invocation"],0)

    def test_declared_F_is_crit_only_and_not_double_counted(self):
        self.assertEqual(audit.F,
            {"crit_rating":165,"haste_rating":0,
             "mastery_rating":0,"versatility_rating":0})
        self.assertEqual(sum(audit.F.values()),165)

    def test_legacy_native_input_bytes_equal_static_render_when_F_matches(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            ref,cfg,fill,_=original.spec_profile(SOURCE.read_text("utf8"),root)
            stable=numeric.input_parts(ref)["stable_sha256"]
            old={"schema":numeric.SCHEMA,
                "status":"TWO_NATIVE_NUMERIC_OFFSET_WITNESSES_AGREE",
                "stable_profile_sha256":stable,
                "net_input_to_json2_rating_offset":dict(audit.F)}
            c=dict(zip(scenario.STATS,(737,737,737,737)))
            location=root/"candidate"/"result.json"
            previous=numeric.render_candidate(ref,old,c,location,35)
            corrected=numeric.render_static_chmv_candidate(ref,c,
                                          audit.F,location,35)
        self.assertEqual(previous["input_sha256"],corrected["input_sha256"])
        self.assertEqual(previous["input"],corrected["input"])
        self.assertEqual(previous["raw_gear_override"],
                         corrected["raw_gear_override"])
        self.assertEqual(sum(previous["raw_gear_override"].values()),2783)

    def test_static_replay_never_changes_official_total_and_has_no_proc_gate(self):
        self.assertEqual(audit.SCHEMA,"v085_shaman_actual_legacy_static_chmv_replay_v1")
        self.assertNotIn("oil",audit.F)
        self.assertEqual(audit.sha(b"abc"),
                         "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

if __name__=="__main__":unittest.main()
