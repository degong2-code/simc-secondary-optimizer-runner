"""v436: selected v217/v212 replay admission + v098 writer (NO Native).

The receipt/layout fixture is synthetic and original v098 replay is mocked
where specified; these tests do not prove 70783 selected item DPS.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v046_static_item_cache as static
import v061_scenario_contract as scenario
import v096_unified_product_entry as entry
import v098_target_user_scenario_bootstrap as bootstrap
import v212_environment_manifest as installed
import v216_environment_build_coordinator as coordinator
from test_p3_ho_fresh_v212_user_bridge import FreshInstalledV096Bridge

def canonical(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,
                      separators=(",",":"),allow_nan=False)

class SelectedV436Receipt(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=pathlib.Path(self.temp.name)
        base=FreshInstalledV096Bridge()
        (self.installed,self.doc,self.cfg,self.flask,self.profile,
         self.unselected,self.attested)=base.make_case(self.root)
        self.key="f"*20
        self.folder=self.root/self.key/"generated"
        self.folder.mkdir(parents=True)
        self.binary=self.root/"native-not-used.exe"
        self.binary.write_bytes(b"TEST-NO-SIMC")
        self.cache=self.root/"static.json"
        self.cache.write_text(canonical(static.empty_cache())+"\n")
        self.digest=hashlib.sha256(self.profile.encode("utf8")).hexdigest()
        self.cfg["source"]["profile_sha256"]=self.digest
        self.user={"character":{"class":"mage","spec":"frost"},
                   "target":{"ilevel":334,"final_T":None},
                   "special_items":[],
                   "embellishments":[{"slot":"head","item_id":239652}],
                   "oil_hands":[]}
        self.future="e"*64
        self.computed={
            "schema":"v433_v098_selected_user_physical_budget_preflight_v1",
            "status":"B8_SELECTED_V096_COMPLETE_PROFILE_BUDGET_NOT_ADMITTED",
            "fresh_installed_v212_source_reused":True,
            "final_source_identity_sha256":"d"*64,
            "source_profile_sha256":self.digest,
            "profile_simc":self.profile,
            "scenario_source_only":self.cfg,
            "selected_fillers_source_only":[],
            "selected_weapon_layout_source_only":"single_two_hand",
            "v096_typed_input_unadmitted":{
                "scenario":self.cfg,"base_B":3150,
                "final_T":3150,"flask_F":self.flask},
            "seed_targets_B_unadmitted":[{
                "crit_rating":750,"haste_rating":800,
                "mastery_rating":800,"versatility_rating":800},{
                "crit_rating":850,"haste_rating":700,
                "mastery_rating":800,"versatility_rating":800}],
            "budget_preflight":{
                "installed_v212_manifest_sha256":self.doc["manifest_sha256"],
                "base_B":3150,"final_T":3150,
                "fixed_O":self.doc["official_O"],
                "selected_budget_identity_sha256":"7"*64},
            "v096_selected_source_only_preflight":{
                "base_B":3150,"final_T":3150,
                "flask_F":self.flask,"fixed_O":self.doc["official_O"]},
            "v435_future_v106_session_key_unadmitted":{
                "identity_sha256":self.future,
                "session_key_preview":self.key,
                "native_execution_authorized":False,
                "runtime_manifest_created":False,
                "session_folder_created":False},
        }
        self.env={"source_compilation":{
            "verified_environment_install":{
                "stage_output_path":str(self.installed),
                "manifest_sha256":self.doc["manifest_sha256"]},
            "v098_source_only_profile_inputs_unadmitted":{
                "oil_by_hand":{}}}}
        self.replay={"schema":"v436_selected_fresh_v098_replay_v1",
                     "user":self.user,"environment_result":self.env,
                     "season_controls":None,
                     "selected_final_source_sha256":"d"*64,
                     "selected_v435_identity_sha256":self.future}
        self.receipt=self.folder/"v436_selected_source_replay.json"
        self.receipt.write_text(canonical(self.replay)+"\n",encoding="utf8")
        self.season={
            "schema":entry.SELECTED_FRESH_SEASON_SCHEMA,
            "installed_environment_path":str(self.installed),
            "installed_manifest_sha256":self.doc["manifest_sha256"],
            "selected_replay_file":self.receipt.name,
            "selected_replay_sha256":hashlib.sha256(
                self.receipt.read_bytes()).hexdigest(),
            "oil_by_hand":{},
            "selected_v435_identity_sha256":self.future}
        self.args={
            "manifest_path":self.folder/"manifest.json",
            "season":self.season,
            "revision":self.doc["simc_revision"],
            "user_scenario":self.cfg,
            "flask_F":self.flask,"oil_hands":[],
            "profile":self.profile,"fillers":[],
            "cache_path":self.cache,
            "binary":self.binary,
            "seed_targets":self.computed["seed_targets_B_unadmitted"],
            "weapon_layout":"single_two_hand"}

    def invoke(self):
        with (mock.patch.object(coordinator,
             "find_verified_installed_season_environment",
             return_value=self.attested) as v217,
              mock.patch.object(bootstrap,"preview_from_environment_build",
                                return_value=self.computed) as replayer):
            result=entry._admitted_selected_fresh_source(**self.args)
        return result,v217,replayer

    def test_v217_installed_owner_and_v098_replay_rebind_selected_budget(self):
        result,v217,replayer=self.invoke()
        self.assertEqual(result["season_budget"]["base_B"],3150)
        self.assertEqual(result["season_budget"]["final_T"],3150)
        self.assertTrue(result["fresh_selected_v436_admitted"])
        self.assertEqual(result["selected_session_identity_sha256"],self.future)
        self.assertEqual(result["season_source_identity"][
            "environment_build_receipt_sha256"],self.doc["manifest_sha256"])
        v217.assert_called_once()
        self.assertEqual(replayer.call_count,1)
        self.assertEqual(replayer.call_args.kwargs[
            "selected_static_cache_path"],self.cache)
        self.assertFalse((self.folder/"V094_RESULT.json").exists())

    def test_modified_replay_bytes_rejected_before_rebuilding(self):
        self.receipt.write_bytes(self.receipt.read_bytes()+b"\n")
        with self.assertRaisesRegex(entry.EntryBlocked,"REPLAY_BYTES_SHA_CHANGED"):
            self.invoke()

    def test_replay_origin_drift_is_rejected(self):
        self.computed["final_source_identity_sha256"]="0"*64
        with self.assertRaisesRegex(entry.EntryBlocked,
                                    "RECOMPUTED_PHYSICAL_PROFILE_OR_BUDGET"):
            self.invoke()

    def test_installed_receipt_drift_not_accepted_by_replay(self):
        self.season["installed_manifest_sha256"]="9"*64
        with self.assertRaisesRegex(entry.EntryBlocked,
                                    "INSTALLED_MANIFEST_IDENTITY"):
            self.invoke()

    def test_bare_user_supplied_oil_without_v212_source_fails(self):
        self.season["oil_by_hand"]={"main_hand":{
            "physical_item_id":11,"simc_input_token":"main_hand:fake",
            "static_CHMV_vector":{"crit_rating":0,"haste_rating":16,
                "mastery_rating":0,"versatility_rating":0}}}
        with self.assertRaisesRegex(entry.EntryBlocked,
                                    "SAME_INSTALLED_F_O_B_T"):
            self.invoke()

    def test_changed_seed_or_weapon_layout_fails_before_native(self):
        self.args["seed_targets"]=[]
        with self.assertRaisesRegex(entry.EntryBlocked,
                                    "RECOMPUTED_PHYSICAL_PROFILE_OR_BUDGET"):
            self.invoke()
        self.args["seed_targets"]=self.computed["seed_targets_B_unadmitted"]
        self.args["weapon_layout"]="dual_two_hand"
        with self.assertRaisesRegex(entry.EntryBlocked,
                                    "RECOMPUTED_PHYSICAL_PROFILE_OR_BUDGET"):
            self.invoke()

    def test_changing_session_folder_disallows_old_v106_key(self):
        self.args["manifest_path"]=(
            self.root/("a"*20)/"generated"/"manifest.json")
        with self.assertRaisesRegex(entry.EntryBlocked,
                                    "SEPARATE_FUTURE_SESSION_FOLDER"):
            # Need a valid replay at the newly supplied location.
            alt=self.args["manifest_path"].parent
            alt.mkdir(parents=True)
            (alt/self.receipt.name).write_bytes(self.receipt.read_bytes())
            self.invoke()

    def test_writer_creates_only_source_locked_manifest_and_plan(self):
        future=self.computed["v435_future_v106_session_key_unadmitted"]
        with (mock.patch.object(bootstrap,"preview_from_environment_build",
              return_value={**self.computed,
                 "v435_future_v106_session_key_unadmitted":future}) as preview,
              mock.patch.object(bootstrap.entry,"run_manifest",
              return_value={"budget_source":
                  "ADMITTED_SELECTED_FRESH_SEASON_B8_V436",
                  "base_B":3150,"final_T":3150,
                  "source_profile_sha256":self.digest,
                  "selected_v435_identity_sha256":self.future}) as run):
            result=bootstrap.materialize_selected_verified_environment(
                user=self.user,folder=self.folder,binary=self.binary,
                revision=self.doc["simc_revision"],
                environment_result=self.env,
                selected_static_cache_path=self.cache)
        self.assertEqual(result["status"],
            "READY_SELECTED_SOURCE_LOCKED_V096_MANIFEST_ZERO_NATIVE")
        self.assertEqual(result["new_native_calls"],0)
        self.assertEqual(preview.call_count,1)
        self.assertTrue(run.call_args.kwargs["plan_only"])
        manifest=json.loads((self.folder/"manifest.json").read_text())
        self.assertEqual(manifest["static_cache_json"],str(self.cache))
        self.assertIn(entry.SELECTED_FRESH_SEASON_FIELD,manifest)
        self.assertTrue((self.folder/"profile.simc").is_file())
        self.assertTrue((self.folder/"v436_selected_source_replay.json").is_file())

    def test_writer_rejects_legacy_session_folder_without_writes(self):
        with mock.patch.object(bootstrap,"preview_from_environment_build",
                               return_value=self.computed):
            wrong=self.root/("a"*20)/"generated"
            with self.assertRaisesRegex(
                bootstrap.UserScenarioBlocked,
                "SOURCE_REPLAY_OR_SESSION_ID_REQUIRED"):
                bootstrap.materialize_selected_verified_environment(
                    user=self.user,folder=wrong,binary=self.binary,
                    revision=self.doc["simc_revision"],
                    environment_result=self.env,
                    selected_static_cache_path=self.cache)
            self.assertFalse(wrong.exists())

if __name__=="__main__":unittest.main()
