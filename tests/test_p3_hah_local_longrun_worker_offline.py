"""P3-HAH v293 pure local worker tests; no web dependency or Native."""
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v293_local_longrun_session as service


class LocalLongRunWorkerOffline(unittest.TestCase):
    def test_worker_uses_original_lock_and_bounded_v291_without_native(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=pathlib.Path(tmp)/("a"*20)
            folder.mkdir()
            budget=12
            manifest=folder/"generated"/"manifest.json"
            manifest.parent.mkdir()
            manifest.write_text("{}")
            doc={"schema":service.SCHEMA,"native_budget":budget,
                 "manifest_sha256":hashlib.sha256(
                     manifest.read_bytes()).hexdigest()}
            service.durable.atomic(service.config_path(folder),doc)
            binary=folder/"dummy"
            binary.write_bytes(b"test")
            output=service.stage_path(folder,budget)/"simc_results"
            cancel=service.stage_path(folder,budget)/"CANCEL"
            prepared={"context":{},"flask":{},"paths":{
                "output_dir":output,"cancel_file":cancel,
                "native_binary":binary}}
            fake_result={"status":"PAUSED_INVOCATION_NATIVE_BUDGET",
                         "new_native_this_invocation":2}
            with mock.patch.object(service,"prepare",return_value=prepared), \
                 mock.patch.object(service.durable,"run",
                                   return_value=fake_result) as executor:
                ok=service.run_worker(folder,12,2)
                self.assertEqual(ok,0)
                self.assertEqual(executor.call_args.kwargs[
                    "max_new_native_this_invocation"],2)
                self.assertFalse(executor.call_args.kwargs["cache_only"])
                self.assertEqual(service.run_worker(folder,12,2,continuous=True),0)
                self.assertIsNone(executor.call_args.kwargs["max_new_native_this_invocation"])
                state=service.durable.read_json(
                    service.worker_state_path(folder))
                self.assertEqual(state["status"],"PAUSED_INVOCATION_NATIVE_BUDGET")
                self.assertEqual(state["new_native_this_invocation"],2)
                with service.sessions.worker_lock(folder):
                    denied=service.run_worker(folder,12,2)
                self.assertEqual(denied,3)
                self.assertEqual(service.durable.read_json(
                    service.worker_state_path(folder)),state)

    def test_result_adapter_never_claims_global_optimum(self):
        base={"crit_rating":1,"haste_rating":1552,
              "mastery_rating":1553,"versatility_rating":1}
        report={"status":"PAUSED_INVOCATION_NATIVE_BUDGET",
            "confidence_for_display":0.95,
            "no_global_optimum_proof":True,
            "summary":{
                "final_T":3107,"underlying_B":3107,
                "fixed_O":{k:0 for k in base},
                "observed_best_T":base,
                "observed_best_dps":185438.66,
                "observed_best_sem":280.53,
                "observed_unique_targets":8,
                "material_alternatives":[]},
            "confirmed_selected_pair_95":{
                "pairwise_direction_supported":True},
            "native_attempts_cumulative":10,
            "verified_cache_cases_this_invocation":10}
        result=service.user_result(report)
        self.assertEqual(result["confidence_level"],0.95)
        self.assertFalse(result["global_optimum_proven"])
        self.assertFalse(result["selection_multiplicity_corrected"])
        self.assertTrue(result["confirmation_pair_direction_supported_at_95"])
        self.assertEqual(sum(result["observed_first_choice"][
            "percent_of_final_T"].values()),100.0)
        report["no_global_optimum_proof"]=False
        with self.assertRaises(service.LocalLongRunBlocked):
            service.user_result(report)



if __name__=="__main__":
    unittest.main()
