"""P3-FZ: existing SimC 70783 CLI may be reused exactly, never guessed."""
from __future__ import annotations
import hashlib
import pathlib
import tempfile
import unittest
from integration_probes import p3_fr_zero_base_t1_acceptance as p

class ExistingSimCArtifactContract(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.binary=pathlib.Path(self.temp.name)/"simc"
        self.binary.write_bytes(b"EXACT_PREBUILT_SIMC_TEST_BINARY")
        self.build="12.1.5.70783"
        self.config={
            "SIMC_PINNED_SOURCE_COMMIT":"c20e2ad52e4c33711f74272309a5748125175fe8",
            "SIMC_PINNED_GAME_BUILD":self.build,
            "SIMC_PINNED_BINARY_SHA256":
                hashlib.sha256(self.binary.read_bytes()).hexdigest(),
        }

    def check(self,environment=None,game_build=None):
        return p.verified_pinned_cli_source(
            binary_path=self.binary,
            live_game_build=game_build or self.build,
            environment=self.config if environment is None else environment)

    def test_exact_bytes_and_build_reuses_without_simc_or_http(self):
        a=self.check()
        self.assertEqual(a["status"],
            "EXISTING_P3_FW_CLI_SOURCE_AND_BYTES_ATTESTED")
        self.assertEqual(a["revision_hint"],self.config[
            "SIMC_PINNED_SOURCE_COMMIT"])
        self.assertEqual(a["binary_sha256"],self.config[
            "SIMC_PINNED_BINARY_SHA256"])
        self.assertFalse(a["environment_ready"])
        self.assertEqual(a["native_calls"],0)
        self.assertEqual(a["new_binary_compilations"],0)
        self.assertEqual(a["network_calls"],0)
        self.assertIsNone(self.check({}))

    def test_new_retail_build_blocks_before_wago_native(self):
        with self.assertRaisesRegex(
            p.ExactBinarySourcePending,
            "P3_FZ_CURRENT_RETAIL_BUILD_DIFFERS_FROM_PINNED_BINARY"):
            self.check(game_build="12.1.5.70784")

    def test_binary_bytes_mutation_blocks(self):
        self.binary.write_bytes(b"EXACT_PREBUILT_SIMC_TEST_BINARY_DRIFT")
        with self.assertRaisesRegex(
            p.ExactBinarySourcePending,"P3_FZ_PINNED_BINARY_SHA256_MISMATCH"):
            self.check()

    def test_invalid_revision_or_sha_is_not_a_source_pin(self):
        for field,value in [
            ("SIMC_PINNED_SOURCE_COMMIT","latest"),
            ("SIMC_PINNED_BINARY_SHA256","0"*63)]:
            with self.subTest(field=field),self.assertRaisesRegex(
                p.ExactBinarySourcePending,
                "P3_FZ_PINNED_SOURCE_IDENTITY_INVALID"):
                self.check({**self.config,field:value})

    def test_no_symlink_binary_can_be_attested(self):
        other=pathlib.Path(self.temp.name)/"source-link"
        other.symlink_to(self.binary)
        with self.assertRaisesRegex(
            p.ExactBinarySourcePending,"P3_FZ_PINNED_BINARY_NOT_REGULAR_FILE"):
            p.verified_pinned_cli_source(
                binary_path=other,live_game_build=self.build,
                environment=self.config)


if __name__=="__main__":
    unittest.main()
