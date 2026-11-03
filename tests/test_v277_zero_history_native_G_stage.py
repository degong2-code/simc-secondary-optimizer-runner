"""P3-CG: reuse original v236/v234 one-Native G inside zero-history v216.

The SimC subprocess is mocked; actual v236.run/v234.observe/v222.rounding
execute with synthetic v046 JSON2. No new real Native or HTTP, no old budget.
"""
from __future__ import annotations

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
import v229_simc_only_source_seed as seed
import v277_zero_history_native_G_stage as stage
from tests.test_v229_simc_only_source_seed import raw_sources
from tests.test_v233_v234_source_native_G import SinglePhysicalNativeTests

REV="710c2408bfd3ae4df71b8cd55cdf01f63fd6c926"
BUILD="12.2.0.99999"


class OneGNativeReuse(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=pathlib.Path(tmp.name)/"entirely_empty_install"
        self.stage=self.root/"_fresh_season_sources"/("wago_"+BUILD)
        self.stage.mkdir(parents=True)
        self.fixture=SinglePhysicalNativeTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        # The existing v232 fixture without the v167 plain-gear source is
        # deliberately NOT physically eligible. Reuse the original v232
        # same-build candidate contract to make a valid synthetic G probe,
        # instead of forging any receipt's approved/verified flag.
        import v167_product_season_gear_adapter as provider
        import v232_simc_only_ordinary_representative as ordinary
        import v233_source_only_G_probe_profile as gprofile
        allowed={
            9020:(5,4,4),9028:(9,4,4),9021:(6,4,4),
            9022:(8,4,4),9023:(2,4,0),9024:(16,4,0),
            9012:(11,4,0),9025:(11,4,0),9010:(17,2,8)}
        rows=[{"item_id":iid,"name":f"candidate_{iid}",
               "category":"plain_representative_candidate",
               "inventory_type":inv,"class_id":kind,"subclass_id":sub,
               "allowed_class_mask":2,
               "source_kinds":["raid_journal"],"item_set_id":0}
              for iid,(inv,kind,sub) in sorted(allowed.items())]
        season={"schema":provider.SCHEMA,
                "status":"CURRENT_SEASON_CANDIDATE_SELECTION_ONLY",
                "no_old_catalog_seed":True,
                "season_build":BUILD,"item_count":len(rows),
                "role_counts":{"plain_representative_candidate":len(rows)},
                "items":rows,
                "not_certified":{"tier_four_set":True,
                                 "simc_item_effects":True},
                "new_native_calls":0,"new_api_calls":0}
        self.fixture.representative=ordinary.find_candidate(
            seed_directory=self.fixture.folder,
            tier_candidate=self.fixture.tier,target_ilevel=335,
            season_gear_db=season)
        self.fixture.text,self.fixture.prepared=gprofile.build(
            source_directory=self.fixture.folder,
            tier_candidate=self.fixture.tier,
            representative_candidate=self.fixture.representative,
            race=self.fixture.race,level=90,season_gear_db=season)
        self.assertTrue(self.fixture.prepared[
            "generic_G_physical_conditions_verified"])
        receipt=self.fixture.prepared
        receipt["simc_revision"]=REV
        receipt["game_build_declared_by_simc_source"]=BUILD
        receipt["receipt_sha256"]=seed.digest(seed.canonical({
            k:v for k,v in receipt.items() if k!="receipt_sha256"}).encode("utf8"))
        self.profile=self.stage/"G.simc"
        self.profile.write_bytes(self.fixture.text.encode("utf8"))
        self.profile_receipt=self.stage/"G_receipt.json"
        self.profile_receipt.write_text(json.dumps(receipt),encoding="utf8")
        self.binary=self.root/"simc_exe"
        self.binary.write_bytes(b"native binary fake, never executed directly")
        seed_dir=self.stage/"source"/"v229_pinned_generated"
        seed_dir.mkdir(parents=True)
        raw=raw_sources(build=BUILD)
        source=seed.inventory(raw,simc_revision=REV,expected_build=BUILD,
            previous_game_build=None,season_event="cold_start",
            expected_git_blob={k:seed.git_blob(v) for k,v in raw.items()})
        (seed_dir/seed.RECEIPT).write_text(json.dumps(source),encoding="utf8")
        self.collected={
            "expected_game_build":BUILD,
            "snapshot_receipt_path":str(self.stage/"wago"/"receipt.json"),
            "fresh_one_spec_physical_G_probe":{
                "profile_path":str(self.profile),
                "profile_receipt_path":str(self.profile_receipt)},
            "fresh_pinned_first_party_simc_source":{
                "source_dir":str(seed_dir),
                "source_stage":{"status":"EXECUTED_AND_SEALED"},
                "simc_receipt_sha256":source["receipt_sha256"]},
        }

    def call(self,binary=None):
        return stage.collect(sessions_root=self.root,collected=self.collected,
                             binary=self.binary if binary is None else binary)

    def fake_process(self,cmd,*,cwd,stdout,stderr,check,timeout):
        (pathlib.Path(cwd)/"native.json").write_text(json.dumps(
            self.fixture._fake_json2()),encoding="utf8")
        stdout.write(b"SimC generated local JSON2")
        return SimpleNamespace(returncode=0)

    def test_only_original_v236_process_one_time_then_cached_G_no_native(self):
        with mock.patch.object(stage.native.subprocess,"run",
                               side_effect=self.fake_process) as worker:
            first=self.call()
            again=self.call()
        self.assertEqual(worker.call_count,1)
        self.assertEqual(first["new_native_calls"],1)
        self.assertEqual(again["new_native_calls"],0)
        self.assertFalse(first["cache_reused"])
        self.assertTrue(again["cache_reused"])
        self.assertEqual(first["status"],
                         "G_NATIVE_NUMERIC_REFERENCE_OBSERVED_JFO_PENDING")
        self.assertEqual(first["standardized_G"],again["standardized_G"])
        self.assertEqual(first["observed_G_total"],
                         sum(first["observed_G_vector"].values()))
        self.assertGreater(first["standardized_G"],0)
        self.assertIsNone(first.get("B"))
        self.assertFalse(first["environment_ready"])
        self.assertFalse(first["full_G_approved"])
        self.assertEqual({x.name for x in self.root.iterdir()},
                         {"_fresh_season_sources","simc_exe"})

    def test_absent_binary_does_not_generate_or_guess_G(self):
        with mock.patch.object(stage.native.subprocess,"run",
                side_effect=AssertionError("NATIVE_NOT_ALLOWED")):
            result=stage.collect(sessions_root=self.root,
                                collected=self.collected,binary=None)
        self.assertEqual(result["status"],
                         "G_NATIVE_SOURCE_PROFILE_OR_BINARY_PENDING")
        self.assertEqual(result["new_native_calls"],0)
        self.assertIsNone(result["standardized_G"])

    def test_cached_tamper_blocks_without_relaunch(self):
        with mock.patch.object(stage.native.subprocess,"run",
                               side_effect=self.fake_process):
            first=self.call()
        (pathlib.Path(first["native_run_folder"])/"native.json").write_bytes(
            b"tampered data")
        with mock.patch.object(stage.native.subprocess,"run",
                side_effect=AssertionError("NATIVE_MUST_NOT_RERUN")):
            with self.assertRaisesRegex(
                  stage.GNativeStageBlocked,"V277_NATIVE_OUTPUT_SHA_DRIFT"):
                self.call()

    def test_simc_error_retained_verbatim_and_no_repeat_execution(self):
        def fail(cmd,*,cwd,stdout,stderr,check,timeout):
            stdout.write(b"SimC original error: item not available for source\n")
            return SimpleNamespace(returncode=9)
        with mock.patch.object(stage.native.subprocess,"run",
                               side_effect=fail) as worker:
            first=self.call()
            again=self.call()
        self.assertEqual(worker.call_count,1)
        self.assertEqual(first["new_native_calls"],1)
        self.assertEqual(again["new_native_calls"],0)
        self.assertEqual(first["status"],
                         "G_NATIVE_ATTEMPT_FAILED_NO_AUTOMATIC_RETRY")
        self.assertIn("SimC original error",
                      first["native_log_excerpt"])
        self.assertEqual(first["native_log_excerpt"],
                         again["native_log_excerpt"])
        self.assertIsNone(first["standardized_G"])

    def test_zero_history_normal_build_uses_single_numeric_G_result(self):
        # Verify same v216 entry, no v191 source/legacy G/J/F/T short-circuit.
        fake={
            "schema":"v216_fresh_source_stage_v1",
            "source_stage":{"status":"EXECUTED_AND_SEALED","reused":False},
            "environment_installed":False,"environment_ready":False,
            "native_calls":0,"G":None,"J":None,"F":None,"O":None,
            "B":None,"T":None}
        observed={
            "schema":stage.SCHEMA,
            "status":"G_NATIVE_NUMERIC_REFERENCE_OBSERVED_JFO_PENDING",
            "new_native_calls":1,"standardized_G":3100,
            "environment_ready":False}
        pending={
            "schema":"v274_v216_collected_to_v241_fresh_compile_inputs_v1",
            "status":"COLLECTED_COMPILER_INPUTS_PENDING",
            "missing":["J","F","O"],
            "network_calls":0}
        kwargs={
            "sessions_root":self.root,"session_folder":None,
            "user":None,"binary":self.binary,"revision":None,
            "static_cache":None,"source_catalog_path":None,
            "bootstrap_result":None,
            "fresh_collection_inputs":{
                "expected_game_build":BUILD,
                "representative_request":None,
                "g_probe_character":None,"simc_revision_hint":None}}
        with mock.patch.object(build,"collect_wago_new_season_source",
                               return_value=fake),\
             mock.patch.object(build.zero_history_G_native,"collect",
                               return_value=observed) as runner,\
             mock.patch.object(build.source_wiring,"compile_collected",
                               return_value=pending):
            result=build.build_environment(**kwargs)
        self.assertEqual(runner.call_count,1)
        self.assertEqual(result["native_calls"],1)
        self.assertEqual(result["zero_history_build"]["new_native_calls"],1)
        self.assertEqual(result["zero_history_build"][
            "G_numeric_reference_observed_unadmitted"],3100)
        self.assertNotIn("G_NATIVE_RATING_OBSERVATION_PENDING",
                         result["zero_history_build"]["requires"])
        self.assertIsNone(result["G"])
        self.assertIsNone(result["B"])
        self.assertIsNone(result["T"])
        self.assertFalse(result["zero_history_build"]["environment_ready"])


if __name__=="__main__":
    unittest.main()
