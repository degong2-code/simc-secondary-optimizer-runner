"""Read-only portable v147 -> v113 result viewing. NO SimC subprocess."""
from __future__ import annotations
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

from fastapi.testclient import TestClient

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v148_local_batch_results as batch
import v113_local_web_api as web

class CopiedWindowsNativeEvidenceOffline(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=pathlib.Path(tmp.name)/"copied_v147_batch"
        self.root.mkdir()
        self.binary_sha=hashlib.sha256(b"real_binary_sha_stored_only").hexdigest()
        self.revision="7bc1071"
        self.batchid="simc_"+self.binary_sha[:16]+"_"+self.revision
        self.folder=self.root/self.batchid
        self.folder.mkdir()
        self.key="mage/frost"
        self.user={
            "schema":"v098_user_target_scenario_v1",
            "character":{"class":"mage","spec":"frost",
                         "race":"dwarf","talents":"CAAAABBB11122"},
            "target":{"ilevel":334,"final_T":None},
            "oil_hands":[],
            "trinkets":[{"slot":"trinket1","item_id":270175,"options":{}},
                        {"slot":"trinket2","item_id":270173,"options":{}}],
            "special_items":[],"embellishments":[],
            "combat":{"targets":1,"duration_seconds":300,"raid_buffs":True}}
        self.user_bytes=(json.dumps(self.user,sort_keys=True,
                        ensure_ascii=False,separators=(",",":"),
                        allow_nan=False)+"\n").encode()
        self.user_sha=batch.sha(self.user_bytes)
        self.basename="mage__frost__"+self.user_sha[:16]
        self.physical=self.folder/"physical"/self.basename
        self.adaptive=self.folder/"adaptive"/self.basename
        (self.physical/"stage").mkdir(parents=True)
        (self.adaptive/"simc_results").mkdir(parents=True)
        (self.physical/"user.json").write_bytes(self.user_bytes)
        self.profile=b"mage=example\nspec=frost\njson2=@PLACEHOLDER@\n"
        (self.physical/"stage"/"profile.simc").write_bytes(self.profile)
        self.native={"report_version":"2.0.0","git_revision":"7bc10711b5",
                     "sim":{"players":[{"collected_data":{
                       "dps":{"mean":1000}}}]}}
        self.native_raw=json.dumps(self.native).encode()
        (self.physical/"physical.json").write_bytes(self.native_raw)
        self.receipt={
            "schema":"v145_one_spec_source_free_physical_diagnostic_v1",
            "status":"PASS_PHYSICAL_SIMC","native_calls":1,
            "physical_sample_only":True,
            "json2_sha256":batch.sha(self.native_raw),
            "identity":{"user_sha256":self.user_sha,
                "spec":self.key,
                "simc_binary_sha256":self.binary_sha,
                "simc_revision":self.revision,
                "CHMV_numeric_overrides_removed":True,
                "profile_sha256":batch.sha(self.profile)}}
        self.receipt_path=self.physical/"receipt.json"
        self.receipt_path.write_text(json.dumps(self.receipt))
        self.result={"confidence_level":0.95,
                     "global_optimum_proven":False,
                     "final_T":3150,
                     "observed_first_choice":{
                         "absolute_rating_T":{"crit_rating":500,
                              "haste_rating":1000,"mastery_rating":800,
                              "versatility_rating":850},
                         "percent_of_final_T":{"crit_rating":15.87,
                              "haste_rating":31.75,"mastery_rating":25.4,
                              "versatility_rating":26.98},
                         "observed_dps_mean":1000.0,"simc_sem":10.0},
                     "base_B":3150,
                     "fixed_O":{"crit_rating":0,"haste_rating":0,
                          "mastery_rating":0,"versatility_rating":0},
                     "confirmation_pair_direction_supported_at_95":False,
                     "material_near_alternatives":[]}
        self.report={
            "schema":"v094_generic_durable_inclusive_adaptive_v1",
            "status":"PASS_BOUNDED_GENERIC_NATIVE_SEARCH_AND_CACHE",
            "global_optimum_proven":False,
            "observations":[{} for _ in range(6)],
            "new_native_attempts_cumulative":6,
            "official_final_T":3150,
            "test_result_only":self.result}
        self.report_path=self.adaptive/"simc_results"/"V094_RESULT.json"
        self.report_path.write_text(json.dumps(self.report))
        self.row={"spec":self.key,"status":"ADAPTIVE_PASS",
                  "physical_status":"PASS_PHYSICAL_SIMC",
                  "adaptive_status":"PASS_BOUNDED_GENERIC_NATIVE_SEARCH_AND_CACHE",
                  "physical_output":r"C:\OldPC\Home\v147_batch\physical\"
                     +self.basename,
                  "user_result":self.result}
        self.summary={"schema":"v147_24_dps_source_free_batch_v1",
                      "status":"FINISHED_WITH_PER_SPEC_RESULTS",
                      "binary_sha256":self.binary_sha,
                      "revision":self.revision,
                      "results":[self.row]}
        self.summary_path=self.folder/"SUMMARY.json"
        self.summary_path.write_text(json.dumps(self.summary))
        self.app=web.create_app(root=self.root/"web_sessions",
                                batch_root=self.root,
                                token="local-test-token")
        self.client=TestClient(self.app,base_url="http://127.0.0.1:8765")
        self.headers={"x-simc-local-token":"local-test-token"}

    def view(self):
        # Stub ONLY the v096 pure presentation converter; this test is not
        # claiming 6 simulated DPS observations were actually measured.
        with mock.patch.object(batch.entry,"user_facing_result",
                    side_effect=lambda report:report["test_result_only"]):
            return batch.view_batch(self.root,self.batchid)

    def test_copied_evidence_uses_local_files_not_old_windows_paths(self):
        self.assertTrue(batch.find_batches(self.root))
        with mock.patch("subprocess.run") as subprocess_call:
            viewed=self.view()
            subprocess_call.assert_not_called()
        self.assertEqual(viewed["matched_read_only_results"],1)
        self.assertFalse(viewed["execution_ready_from_relocated_cache"])
        self.assertEqual(viewed["native_calls_now"],0)
        self.assertEqual(viewed["results"][0]["user_result"],self.result)
        self.assertNotIn("OldPC",json.dumps(viewed))
        self.assertNotIn("OldPC",json.dumps(batch.find_batches(self.root)))

    def test_modified_physical_native_json2_is_not_trusted(self):
        (self.physical/"physical.json").write_text('{"corrupted":true}')
        result=self.view()
        self.assertEqual(result["matched_read_only_results"],0)
        self.assertEqual(result["results"][0]["status"],
                         "LOCAL_EVIDENCE_NOT_MATCHED")

    def test_changed_summary_dps_does_not_trust_a_copied_report(self):
        self.summary["results"][0]["user_result"]["observed_first_choice"][
            "observed_dps_mean"]=99999
        self.summary_path.write_text(json.dumps(self.summary))
        viewed=self.view()
        self.assertEqual(viewed["matched_read_only_results"],0)

    def test_inconsistent_receipt_binary_and_revision_are_refused(self):
        self.receipt["identity"]["simc_binary_sha256"]="f"*64
        self.receipt_path.write_text(json.dumps(self.receipt))
        self.assertEqual(self.view()["matched_read_only_results"],0)
        self.receipt["identity"]["simc_binary_sha256"]=self.binary_sha
        self.receipt_path.write_text(json.dumps(self.receipt))
        self.native["git_revision"]="deadbeef"
        raw=json.dumps(self.native).encode()
        (self.physical/"physical.json").write_bytes(raw)
        self.receipt["json2_sha256"]=batch.sha(raw)
        self.receipt_path.write_text(json.dumps(self.receipt))
        self.assertEqual(self.view()["matched_read_only_results"],0)

    def test_batch_filename_and_symlink_escape_never_used_as_path(self):
        with self.assertRaisesRegex(batch.BatchViewBlocked,"BATCH_ID_INVALID"):
            batch.view_batch(self.root,"../../Windows")
        invalid=self.folder/"physical"/self.basename
        # No need for malicious filesystem mutation: path from SUMMARY is
        # only used as expected basename and never opened directly.
        self.summary["results"][0]["physical_output"]="/tmp/secret"
        self.summary_path.write_text(json.dumps(self.summary))
        self.assertEqual(self.view()["matched_read_only_results"],0)
        self.assertTrue(invalid.is_dir())

    def test_web_requires_loopback_token_and_exposes_no_filesystem_paths(self):
        unauthorized=self.client.get(
            "/api/v1/native-batches/"+self.batchid+"/results")
        self.assertEqual(unauthorized.status_code,403)
        listings=self.client.get("/api/v1/native-batches",
                                 headers=self.headers)
        self.assertEqual(listings.status_code,200)
        self.assertEqual(len(listings.json()["batches"]),1)
        with mock.patch.object(batch.entry,"user_facing_result",
                    side_effect=lambda report:report["test_result_only"]), \
             mock.patch("subprocess.run") as subprocess_call:
            result=self.client.get("/api/v1/native-batches/"+self.batchid+
                                   "/results",headers=self.headers)
            subprocess_call.assert_not_called()
        self.assertEqual(result.status_code,200,result.text)
        data=result.json()
        self.assertEqual(data["matched_read_only_results"],1)
        self.assertNotIn("OldPC",result.text)
        self.assertNotIn(str(self.root),result.text)
        self.assertFalse(data["execution_ready_from_relocated_cache"])
        self.assertEqual(data["native_calls_now"],0)

if __name__=="__main__":
    unittest.main()
