"""P3-CH: v269 exact SimC F/O delta, shared baseline, no double Native.

The process is mocked, but original v269.prepare/compare and real immutable
profile/json/log/receipts run, not mocked delta or self-declared fixed values.
"""
import json
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))

import v216_environment_build_coordinator as build
import v278_sealed_simc_consumable_native_pair as pair
from tests.test_v269_simc_chmv_effect_snapshot import PROFILE,report

REV="a"*40
FLASK="flask_of_the_magisters_2"
OIL="main_hand:thalassian_phoenix_oil_2"


class TwoNativeOptions(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=pathlib.Path(tmp.name)/"fresh_source"
        self.root.mkdir()
        self.profile=self.root/"representative_profile.simc"
        self.profile.write_text(PROFILE,encoding="utf8")
        self.binary=self.root/"simc_fake"
        self.binary.write_bytes(b"mocked binary, no actual SimC execution")
        self.commands=[]

    def execute(self,cmd,*,cwd,stdout,stderr,check,timeout):
        source=pathlib.Path(cmd[1]).read_text(encoding="utf8")
        self.commands.append(source)
        opts={}
        for key in ("flask","food","temporary_enchant"):
            lines=[row for row in source.splitlines()
                   if row.startswith(key+"=")]
            self.assertEqual(len(lines),1)
            opts[key]=lines[0].split("=",1)[1]
        self.assertTrue(all(opts[k]=="disabled" for k in
            ("food",) if opts["flask"]!= "disabled"))
        crit=2500
        haste=1300
        if opts["flask"]==FLASK:crit+=108
        if opts["temporary_enchant"]==OIL:
            crit+=16
            haste+=16
        dest=pathlib.Path(cwd)/"native.json"
        dest.write_bytes(report(opts,crit=crit,haste=haste))
        stdout.write(b"original SimC test stdout\n")
        return SimpleNamespace(returncode=0)

    def measure(self,kind="flask",token=FLASK,binary=None):
        return pair.measure(stage_root=self.root,
             source_profile_path=self.profile,
             binary=self.binary if binary is None else binary,
             simc_revision=REV,kind=kind,token=token)

    def test_original_v269_measure_first_two_native_second_zero(self):
        with mock.patch.object(pair.subprocess,"run",
                               side_effect=self.execute) as run:
            one=self.measure()
            two=self.measure()
        self.assertEqual(run.call_count,2)
        self.assertEqual(one["new_native_calls"],2)
        self.assertEqual(two["new_native_calls"],0)
        self.assertEqual(one["F_candidate_unadmitted"],108)
        self.assertEqual(one["static_CHMV_candidate"]["crit_rating"],108)
        self.assertFalse(one["quality_or_slot_verified"])
        self.assertFalse(one["budget_owner_verified"])
        self.assertFalse(one["environment_ready"])
        self.assertEqual(one["status"],
                 "SIMC_STATIC_CHMV_EFFECT_OBSERVED_NOT_ADMITTED")
        self.assertEqual(len(two["native_case_receipts"]),2)
        self.assertTrue(all(v["cache_reused"]
                            for v in two["native_case_receipts"]))

    def test_flask_and_oil_share_original_disabled_baseline_only_once(self):
        with mock.patch.object(pair.subprocess,"run",
                               side_effect=self.execute) as run:
            flask=self.measure()
            oil=self.measure("temporary_enchant",OIL)
            reused=self.measure("temporary_enchant",OIL)
        self.assertEqual(run.call_count,3)
        self.assertEqual(flask["new_native_calls"],2)
        self.assertEqual(oil["new_native_calls"],1)
        self.assertEqual(reused["new_native_calls"],0)
        self.assertEqual(oil["O_candidate_unadmitted"],{
            "crit_rating":16,"haste_rating":16,
            "mastery_rating":0,"versatility_rating":0})
        self.assertIsNone(oil["F_candidate_unadmitted"])
        self.assertTrue(oil["native_case_receipts"][0]["cache_reused"])
        self.assertEqual(len(set(x["baseline_profile_sha256"]
                            for x in (flask["observed"],oil["observed"]))),1)

    def test_failure_keeps_real_log_and_no_automatic_retry(self):
        def fail(cmd,*,cwd,stdout,stderr,check,timeout):
            stdout.write(b"SimC real original diagnostic: unknown consumable\n")
            return SimpleNamespace(returncode=8)
        with mock.patch.object(pair.subprocess,"run",side_effect=fail) as run:
            one=self.measure()
            two=self.measure()
        self.assertEqual(run.call_count,1)
        self.assertEqual(one["new_native_calls"],1)
        self.assertEqual(two["new_native_calls"],0)
        self.assertEqual(one["status"],
                         "SIMC_CONSUMABLE_NATIVE_FAILED_NO_AUTO_RETRY")
        self.assertIn("original diagnostic",one["native_log_excerpt"])
        self.assertEqual(two["native_log_excerpt"],one["native_log_excerpt"])

    def test_tamper_cached_json_fails_before_relaunch(self):
        with mock.patch.object(pair.subprocess,"run",side_effect=self.execute):
            one=self.measure()
        receipt=pathlib.Path(one["native_case_receipts"][0]["receipt_path"])
        (receipt.parent/"native.json").write_bytes(b"MODIFIED")
        with mock.patch.object(pair.subprocess,"run",
                    side_effect=AssertionError("NEW_NATIVE_FORBIDDEN")):
            with self.assertRaisesRegex(pair.NativePairBlocked,
                     "V278_CACHED_NATIVE_OUTPUT_TAMPERED"):
                self.measure()

    def test_unsealed_source_and_oil_gear_override_block(self):
        outsider=self.root.parent/"outside.simc"
        outsider.write_text(PROFILE,encoding="utf8")
        with self.assertRaisesRegex(pair.NativePairBlocked,
                                    "V278_SOURCE_PROFILE_NOT_FROM_THIS_STAGE"):
            pair.measure(stage_root=self.root,source_profile_path=outsider,
                binary=self.binary,simc_revision=REV,kind="flask",token=FLASK)
        self.profile.write_text(PROFILE+"gear_crit_rating=350\n",
                                encoding="utf8")
        with mock.patch.object(pair.subprocess,"run",
                               side_effect=AssertionError("NO_PROCESS")):
            with self.assertRaisesRegex(pair.NativePairBlocked,
                        "V269_OIL_BASELINE_CANNOT_USE_GEAR_RATING_OVERRIDE"):
                self.measure("temporary_enchant",OIL)

    def test_missing_local_binary_remains_pending_without_fake_zero_F(self):
        with mock.patch.object(pair.subprocess,"run",
                 side_effect=AssertionError("NO_PROCESS")):
            pending=pair.measure(stage_root=self.root,
                    source_profile_path=self.profile,binary=None,
                    simc_revision=REV,kind="flask",token=FLASK)
        self.assertEqual(pending["status"],
                         "SIMC_CONSUMABLE_SOURCE_OR_BINARY_PENDING")
        self.assertEqual(pending["new_native_calls"],0)
        self.assertIsNone(pending["static_CHMV_candidate"])

    def test_original_v216_normal_build_reaches_measured_F_O_without_ready(self):
        source={"schema":"v216_fresh_source_stage_v1",
            "source_stage":{"status":"EXECUTED_AND_SEALED","reused":False},
            "environment_installed":False,"environment_ready":False,
            "native_calls":0,"G":None,"J":None,"F":None,"O":None,
            "B":None,"T":None}
        source["expected_game_build"]="12.2.0.99999"
        source["snapshot_receipt_path"]=str(self.root/"wago"/"receipt.json")
        compiled={"status":"FRESH_V191_V211_V213_COMPILED_UNADMITTED",
                  "stage_root":str(self.root),"simc_revision":REV,
                  "source_catalog_path":str(self.root/"catalog.json"),
                  "missing":[]}
        p={"expected_game_build":"12.2.0.99999",
           "representative_request":None,"g_probe_character":None,
           "simc_revision_hint":None,
           "effect_probe_requests":[{
                "source_profile_path":str(self.profile),
                "kind":"flask","token":FLASK},
                {"source_profile_path":str(self.profile),
                 "kind":"temporary_enchant","token":OIL}]}
        with mock.patch.object(build,"collect_wago_new_season_source",
                               return_value=source),\
             mock.patch.object(build.source_wiring,"compile_collected",
                               return_value=compiled),\
             mock.patch.object(build,"preflight_new_season_source",
                               return_value={"preflight_sha256":"f"*64,
                                   "status":"FRESH_SOURCE_UNADMITTED"}),\
             mock.patch.object(build.zero_history_G_native,"collect",
                               return_value={"status":"PENDING",
                                             "new_native_calls":0}),\
             mock.patch.object(pair.subprocess,"run",
                               side_effect=self.execute) as native_run:
            actual=build.build_environment(sessions_root=self.root,
                  session_folder=None,user=None,binary=self.binary,
                  revision=None,static_cache=None,
                  source_catalog_path=None,bootstrap_result=None,
                  fresh_collection_inputs=p)
        self.assertEqual(native_run.call_count,3)
        self.assertEqual(actual["native_calls"],3)
        self.assertEqual(len(actual[
            "native_effect_numeric_sources_unadmitted"]),2)
        self.assertEqual(actual["zero_history_build"]["new_native_calls"],3)
        self.assertEqual(actual["zero_history_build"][
            "F_O_effect_numeric_candidates_unadmitted"]["F"],[108])
        self.assertEqual(actual["zero_history_build"][
            "F_O_effect_numeric_candidates_unadmitted"]["O"][0][
               "crit_rating"],16)
        self.assertIsNone(actual["G"])
        self.assertIsNone(actual["J"])
        self.assertIsNone(actual["F"])
        self.assertIsNone(actual["O"])
        self.assertFalse(actual["zero_history_build"]["environment_ready"])

    def test_v216_does_not_use_effect_requests_before_verified_compiler(self):
        source={"schema":"v216_fresh_source_stage_v1",
            "source_stage":{"status":"EXECUTED_AND_SEALED","reused":False},
            "environment_installed":False,"environment_ready":False,
            "native_calls":0,"G":None,"J":None,"F":None,"O":None,
            "B":None,"T":None}
        p={"expected_game_build":"12.2.0.99999",
           "representative_request":None,"g_probe_character":None,
           "simc_revision_hint":None,
           "effect_probe_requests":[{
                "source_profile_path":str(self.profile),
                "kind":"flask","token":FLASK}]}
        with mock.patch.object(build,"collect_wago_new_season_source",
                               return_value=source),\
             mock.patch.object(build.source_wiring,"compile_collected",
                     return_value={"status":"COLLECTED_COMPILER_INPUTS_PENDING",
                                   "missing":["V189"],"network_calls":0}),\
             mock.patch.object(build.zero_history_G_native,"collect",
                               return_value={"status":"PENDING",
                                             "new_native_calls":0}),\
             mock.patch.object(pair.subprocess,"run",
                 side_effect=AssertionError("NATIVE_TOO_EARLY")):
            actual=build.build_environment(sessions_root=self.root,
                session_folder=None,user=None,binary=self.binary,
                revision=None,static_cache=None,
                source_catalog_path=None,bootstrap_result=None,
                fresh_collection_inputs=p)
        self.assertEqual(actual["native_calls"],0)
        self.assertIn("F_O_SIMC_EFFECT_PROBES_WAIT_FOR_SAME_BUILD_CATALOG",
                      actual["zero_history_build"]["requires"])


if __name__=="__main__":
    unittest.main()
