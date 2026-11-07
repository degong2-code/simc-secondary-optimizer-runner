"""P3-GS: original v232 socket count vs prospective five-socket layout."""
import json
import pathlib
import sys
import tempfile
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"runner"))
import v216_environment_build_coordinator as v

class ProspectiveSocketStage(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=pathlib.Path(self.temp.name)
        (self.root/"source").mkdir()
        self.build="12.1.5.70783"
        self.original={"neck":1,"finger1":1,"finger2":1,
                       "head":0,"wrists":0,"waist":0}
        self.proposed={**self.original,"wrists":1,"waist":1}
        original={
            "schema":v.simc_representative.SCHEMA,
            "game_build":self.build,"target_ilevel":334,
            "selected_G_slot_ids":{
                k:900000+i for i,k in enumerate(sorted(self.original))},
            "selected_intrinsic_socket_count_by_slot_source_only":
                self.original,
            "environment_ready":False}
        original["receipt_sha256"]=v.simc_source.digest(
            v.simc_source.canonical(original).encode("utf8"))
        path=self.root/"source"/"v232.json"
        path.write_text(json.dumps(original),encoding="utf8")
        self.collected={
            "expected_game_build":self.build,
            "fresh_one_spec_simc_representative":{
                "status":"FRESH_ONE_SPEC_SIMC_G_SOURCE_CANDIDATE_PENDING_NATIVE",
                "candidate_path":str(path),
                "source_stage":{"status":"EXECUTED_AND_SEALED",
                                "receipt_sha256":"f"*64,
                                "output_paths":{"candidate":"source/v232.json"}},
                "selected_slot_count":len(self.original),
                "intrinsic_socket_total_source_only":3,
                "intrinsic_socket_counts_by_selected_slot_source_only":
                    self.original,
                "added_socket_bonus_and_game_permission_not_proven":True}}
        self.roles={"special_gem_id":311005,
                    "ordinary_gem_ids":[311001,311002,311003,311004]}

    def test_original_three_to_prospective_five_does_not_miscompare(self):
        staged=v._fresh_default_intrinsic_gem_layout_from_source(
            collected=self.collected,selected_roles=self.roles,
            target_ilevel=334,candidate_socket_counts=self.proposed)
        self.assertEqual(staged["socket_total"],5)
        self.assertEqual(staged["ordinary_count"],4)
        self.assertEqual(staged["ordinary_gem_ids"],
                         self.roles["ordinary_gem_ids"])
        self.assertEqual(sum(self.original.values()),3)
        self.assertEqual(self.collected[
            "fresh_one_spec_simc_representative"][
            "intrinsic_socket_counts_by_selected_slot_source_only"],
            self.original)
        self.assertFalse(staged["environment_ready"])
        preflight={"schema":v.FRESH_SOURCE_PREFLIGHT_SCHEMA,
                   "game_build":self.build,
                   "simc_revision":"abc1234",
                   "environment_ready":False,
                   "physical_gem_layout_unadmitted":staged}
        receipt=v._fresh_selected_J_intrinsic_socket_source(
            collected=self.collected,preflight=preflight,
            compilation={"simc_revision":"abc1234"})
        self.assertEqual(receipt["status"],
                         "J_ADDITIONAL_SOCKET_SOURCE_PROOF_PENDING")
        self.assertEqual(receipt[
            "additional_socket_proof_required_by_slot"],
            {"wrists":1,"waist":1})
        self.assertFalse(receipt["J_approved"])
        self.assertEqual(receipt["new_native_calls"],0)

    def test_no_prospective_sockets_keeps_original_legacy_behavior(self):
        selected={"special_gem_id":311005,
                  "ordinary_gem_ids":[311001,311002]}
        original=v._fresh_default_intrinsic_gem_layout_from_source(
            collected=self.collected,selected_roles=selected,
            target_ilevel=334)
        self.assertEqual(original["socket_total"],3)
        self.assertEqual(original["ordinary_count"],2)

    def test_unchanged_source_and_no_forged_bonus_counts(self):
        forged=[{**self.original,"neck":2,"wrists":0,"waist":0},
                {**self.original,"head":2,"wrists":0,"waist":0},
                {**self.original,"feet":1,"wrists":1,"waist":1},
                {**self.original,"wrists":1,"waist":0}]
        for plan in forged:
            with self.subTest(plan=plan):
                with self.assertRaisesRegex(
                    v.EnvironmentBuildBlocked,
                    "V216_FUTURE_SOCKET_PLAN_ORIGINAL_V232_DRIFT"):
                    v._fresh_default_intrinsic_gem_layout_from_source(
                        collected=self.collected,selected_roles=self.roles,
                        target_ilevel=334,candidate_socket_counts=plan)

if __name__=="__main__":
    unittest.main()
