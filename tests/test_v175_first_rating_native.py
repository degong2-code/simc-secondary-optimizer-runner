"""v175 one actual-seed pipeline. All subprocesses mocked in offline tests."""
import hashlib,json,pathlib,subprocess,sys,tempfile,unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"integration_probes")]
import v175_first_rating_native as first
import v098_target_user_scenario_bootstrap as bootstrap
import v106_user_session_controller as sessions
import v140_pure_profile_physical_native_smoke as physical

class OneExistingSeedNativeBridge(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=pathlib.Path(tmp.name)
        self.binary=self.root/"fake-simc"
        self.binary.write_bytes(b"OFFLINE_NO_NATIVE")
        self.sha=hashlib.sha256(self.binary.read_bytes()).hexdigest()
        self.pin=mock.patch.object(first,"EXPECTED_BINARY_SHA",self.sha)
        self.pin.start()
        self.addCleanup(self.pin.stop)
        controls=sessions.standard_controls(("paladin","retribution"))
        controls["oil_hands"]=[]
        user=sessions.user_scenario(controls)
        self.folder=self.root/"prior"/"paladin__retribution__source_first_v172__fake"
        self.folder.mkdir(parents=True)
        (self.folder/"user.json").write_text(first.canonical(user),encoding="utf8")
        bootstrap.build(user,self.folder/"stage",self.binary,first.EXPECTED_REV,
                        pure_stage=True,source_first_stage=True)
        profile=(self.folder/"stage"/"profile.simc").read_bytes()
        physical_text=physical.physical_input(profile.decode("utf8"),
                                  self.folder/"physical.json",35)
        (self.folder/"physical.simc").write_text(physical_text,encoding="utf8")
        witness={"report_version":"2.0.0","git_revision":first.EXPECTED_REV,
            "sim":{"players":[{"name":"target_retribution",
                "specialization":"Retribution Paladin",
                "collected_data":{"dps":{"mean":180000.0}}}]}}
        raw=json.dumps(witness).encode("utf8")
        (self.folder/"physical.json").write_bytes(raw)
        identity={"user_sha256":first.sha((self.folder/"user.json").read_bytes()),
            "simc_binary_sha256":self.sha,"simc_revision":first.EXPECTED_REV,
            "source_first_current_season_stage":True,
            "profile_sha256":first.sha(profile),
            "physical_sha256":first.sha(physical_text.encode("utf8")),
            "current_season_gear_snapshot_sha256":first.sha(
              bootstrap.source_first.gear.DEFAULT.read_bytes()),
            "current_season_tier_snapshot_sha256":first.sha(
              bootstrap.source_first.TIER_PATH.read_bytes())}
        receipt={"identity":identity,"status":"PASS_PHYSICAL_SIMC",
            "native_returncode":0,"new_native_calls_this_run":1,
            "spec":"paladin/retribution","json2_sha256":first.sha(raw)}
        (self.folder/"receipt.json").write_text(first.canonical(receipt))
        self.out=self.root/"new"

    def test_plan_only_native_zero_and_existing_v093_rating_sums(self):
        with mock.patch.object(first.engine.subprocess,"run") as native:
            result=first.run(self.folder,self.binary,self.out,max_new=0)
            native.assert_not_called()
        self.assertEqual(result["status"],"PLAN_ONLY_ZERO_NATIVE")
        self.assertEqual(result["base_B"],3150)
        self.assertEqual(result["final_T"],3150)
        self.assertEqual(sum(result["target"].values()),3150)
        self.assertEqual(sum(result["flask_F"].values()),165)
        self.assertEqual(sum(result["fixed_O"].values()),0)
        self.assertFalse((self.out/"seed_00"/"input.simc").exists())
        self.assertFalse((self.out/"seed_00"/"result.json").exists())

    def test_one_mocked_existing_v065_native_then_cache_and_static_rating_check(self):
        calls=[]
        def fake(cmd,*,cwd,stdin,stdout,stderr,timeout):
            calls.append(cmd)
            rendered=pathlib.Path(cmd[1]).read_text("utf8")
            self.assertIn("temporary_enchant=disabled",rendered)
            self.assertIn("default_actions=1",rendered)
            self.assertIn("gear_crit_rating=",rendered)
            path=pathlib.Path([x.split("=",1)[1] for x in
                 rendered.splitlines() if x.startswith("json2=")][0])
            native={"report_version":"2.0.0",
                "git_revision":first.EXPECTED_REV,
                "sim":{"players":[{"temporary_enchant":"disabled",
                    "collected_data":{"buffed_stats":{"stats":{
                        "crit_rating":1000,"haste_rating":1000,
                        "mastery_rating":1000,"versatility_rating":1000}},
                       "dps":{"mean":12000.0,"mean_std_dev":80.0,
                              "count":35}}}]}}
            path.write_text(json.dumps(native))
            return subprocess.CompletedProcess(cmd,0,b"simc stdout",b"")
        with mock.patch.object(first.engine.subprocess,"run",side_effect=fake):
            a=first.run(self.folder,self.binary,self.out,max_new=1)
            b=first.run(self.folder,self.binary,self.out,max_new=0)
        self.assertEqual(len(calls),1)
        self.assertEqual(a["status"],"PASS_ONE_STATIC_RATING_NATIVE")
        self.assertEqual(a["new_native_calls"],1)
        self.assertEqual(a["target_static_CHMV"],a["native_verified_static_CHMV"])
        self.assertEqual(a["dps_samples"],35)
        self.assertEqual(b["status"],"CACHED_VERIFIED_STATIC_RATING_NATIVE")
        self.assertEqual(b["new_native_calls"],0)
        self.assertEqual(a["native_json_sha256"],b["native_json_sha256"])
        self.assertFalse(a["95_percent_winner_proven"])

    def test_changed_prior_physical_witness_blocks_before_native(self):
        (self.folder/"physical.json").write_text('{"tampered":true}')
        with mock.patch.object(first.engine.subprocess,"run") as proc:
            with self.assertRaisesRegex(first.CandidateBlocked,
                                        "V174_IMMUTABLE"):
                first.run(self.folder,self.binary,self.out,max_new=1)
            proc.assert_not_called()

if __name__=="__main__":unittest.main()
