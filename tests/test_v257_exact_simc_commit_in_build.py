"""P3-AY: exact first-party source commit pin for one requested DPS Build.
All HTTP mocked; a resolved source SHA is not executable-binary attestation.
"""
import io
import json
import pathlib
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v216_environment_build_coordinator as build
import v229_simc_only_source_seed as seed


class Response(io.BytesIO):
    status=200
    def __enter__(self):return self
    def __exit__(self,*args):self.close()


class ExactPin(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=pathlib.Path(self.temp.name)
        self.build="12.2.0.99999"
        self.revision="a"*40
        self.hint="a"*7
        self.gear={"candidate_path":"source/v167.json"}
        self.tier={"candidate_path":"source/v251.json"}
        self.urls=[]

    def fetch(self,request,timeout):
        self.urls.append(request.full_url)
        return Response(json.dumps({"sha":self.revision}).encode())

    def go(self,hint=None,gear=None,tier=None):
        return build._resolve_one_spec_simc_commit_stage(
            stage_root=self.root,build=self.build,
            gear=self.gear if gear is None else gear,
            tier=self.tier if tier is None else tier,
            revision_hint=self.hint if hint is None else hint,
            transport=self.fetch)

    def test_cold_start_pinned_small_source_sealed_once_without_prior_build(self):
        from tests.test_v229_simc_only_source_seed import (
            SimCCollectorTests,REVISION,BUILD)
        upstream=SimCCollectorTests(
            "test_collect_pinned_sources_without_any_legacy_data")
        upstream.setUp()
        first=build._collect_first_party_simc_seed_stage(
            stage_root=self.root,build=BUILD,revision=REVISION,
            previous_game_build=None,season_event="cold_start",
            transport=upstream.fetch)
        second=build._collect_first_party_simc_seed_stage(
            stage_root=self.root,build=BUILD,revision=REVISION,
            previous_game_build=None,season_event="cold_start",
            transport=upstream.fetch)
        self.assertEqual(first["status"],"SIMC_PINNED_SET_SOURCE_RECEIPT_READY")
        self.assertEqual(first["network_calls_by_stage"],7)
        self.assertEqual(second["network_calls_by_stage"],0)
        receipt=json.loads((pathlib.Path(first["source_dir"])/
                            seed.RECEIPT).read_text())
        self.assertIsNone(receipt["previous_game_build"])
        self.assertEqual(receipt["season_event"],"cold_start")
        self.assertTrue(receipt["provenance_tree_blob_authenticated"])
        self.assertFalse(receipt["environment_ready"])
        self.assertIsNone(receipt["G"])

    def test_game_event_is_not_local_previous_build_history(self):
        for game_event in ("season_change","expansion_change"):
            no_history=build._simc_source_collection_context(
                requested_event=game_event,previous_game_build=None)
            self.assertEqual(no_history["requested_game_event"],game_event)
            self.assertEqual(no_history["source_collection_mode"],"cold_start")
            self.assertEqual(no_history["previous_build_record_status"],
                             "NOT_RECORDED")
            self.assertTrue(no_history[
                "previous_game_build_is_not_a_season_proof"])
            recorded=build._simc_source_collection_context(
                requested_event=game_event,
                previous_game_build="12.1.5.70575")
            self.assertEqual(recorded["requested_game_event"],game_event)
            self.assertEqual(recorded["source_collection_mode"],game_event)
            self.assertEqual(recorded["previous_build_record_status"],
                             "RECORDED")
        self.assertEqual(build._simc_source_collection_context(
            requested_event="mid_patch",previous_game_build=None)[
                "source_collection_mode"],"mid_patch")
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,"V216_GAME_EVENT_INVALID"):
            build._simc_source_collection_context(
                requested_event="cold_start",previous_game_build=None)
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_PREVIOUS_GAME_BUILD_RECORD_INVALID"):
            build._simc_source_collection_context(
                requested_event="expansion_change",previous_game_build="unknown")

    def test_short_commit_resolved_once_and_sealed_reused_without_http(self):
        first=self.go()
        second=self.go()
        self.assertEqual(first["status"],"SIMC_SOURCE_COMMIT_EXACT_PIN_CANDIDATE")
        self.assertEqual(first["simc_revision"],self.revision)
        self.assertEqual(first["network_calls_by_stage"],1)
        self.assertEqual(second["network_calls_by_stage"],0)
        self.assertEqual(first["source_stage"]["status"],"EXECUTED_AND_SEALED")
        self.assertEqual(second["source_stage"]["status"],"REUSED_VERIFIED")
        self.assertEqual(self.urls,[
            "https://api.github.com/repos/simulationcraft/simc/commits/"+self.hint])
        self.assertFalse(first["binary_attested"])
        self.assertFalse(first["season_verified"])
        self.assertFalse(first["environment_ready"])

    def test_full_40_hex_commit_needs_no_lookup(self):
        got=self.go(hint=self.revision)
        self.assertEqual(got["simc_revision"],self.revision)
        self.assertEqual(got["network_calls_by_stage"],0)
        self.assertEqual(self.urls,[])
        self.assertFalse(got["binary_attested"])

    def test_missing_gear_or_tier_still_resolves_explicit_source_hint_once(self):
        # P3-FS source-only exact commit identity is independent of gear/tier.
        # It does NOT approve a representative profile or attest a binary.
        a=self.go(gear={"candidate_path":None})
        b=self.go(tier={"candidate_path":None})
        self.assertEqual(a["status"],"SIMC_SOURCE_COMMIT_EXACT_PIN_CANDIDATE")
        self.assertEqual(b["status"],"SIMC_SOURCE_COMMIT_EXACT_PIN_CANDIDATE")
        self.assertEqual(a["network_calls_by_stage"],1)
        self.assertEqual(b["network_calls_by_stage"],0)
        self.assertFalse(a["binary_attested"])
        self.assertFalse(b["season_verified"])
        self.assertEqual(len(self.urls),1)
        self.assertEqual(len(list(self.root.glob(
            "source/v257_exact_simc_commit_*.json"))),1)

    def test_revision_switch_preserves_previous_sealed_source(self):
        first=self.go()
        old=pathlib.Path(self.root/"source"/(
            "v257_exact_simc_commit_"+self.hint+".json"))
        original=old.read_bytes()
        self.revision="a"*40
        second=self.go(hint=self.revision)
        self.assertEqual(first["status"],"SIMC_SOURCE_COMMIT_EXACT_PIN_CANDIDATE")
        self.assertEqual(second["status"],"SIMC_SOURCE_COMMIT_EXACT_PIN_CANDIDATE")
        self.assertEqual(old.read_bytes(),original)
        self.assertEqual(len(list(self.root.glob("source/v257_exact_simc_commit_*.json"))),2)
        self.assertEqual(second["network_calls_by_stage"],0)

    def test_wrong_sha_or_invalid_json_stays_pending_no_season_certification(self):
        self.revision="b"*40
        wrong=self.go()
        self.assertEqual(wrong["status"],"SIMC_SOURCE_COMMIT_RESOLUTION_PENDING")
        self.assertEqual(wrong["reason"],"V229_REVISION_LOOKUP_IDENTITY_MISMATCH")
        self.assertIsNone(wrong["simc_revision"])
        self.assertFalse(wrong["environment_ready"])

    def test_invalid_revision_hint_blocked_before_stage(self):
        with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                    "V216_SOURCE_REVISION_HINT_INVALID"):
            self.go(hint="latest!")
        self.assertEqual(self.urls,[])

    def test_resolver_rejects_bad_prefix_and_full_sha_without_trusting_binary(self):
        self.assertEqual(seed.resolve_exact_commit(self.revision,transport=self.fetch),
                         self.revision)
        self.assertEqual(self.urls,[])
        with self.assertRaisesRegex(seed.SimCSourceBlocked,
                                    "V229_SOURCE_REVISION_HINT_INVALID"):
            seed.resolve_exact_commit("deadbeef!!",transport=self.fetch)
        self.assertEqual(self.urls,[])


if __name__=="__main__":
    unittest.main()
