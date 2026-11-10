"""v308 complete original Native bytes roundtrip and SHA fail-closed (offline)."""
import hashlib
import io
import json
import pathlib
import shutil
import sys
import tempfile
import unittest
import zipfile
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]

import v308_dense_native_checkpoint as checkpoint
import v291_durable_multiscale_native_runner as runner
import test_p3_hx_durable_longrun_offline as fixtures


class V308RawCheckpoint(unittest.TestCase):
    def test_24_native_byte_archive_restore_exact_path_then_v291_cache_reauth(self):
        with tempfile.TemporaryDirectory() as home:
            ctx,binary,out=fixtures.V291LongRun().fixture(home,cap=24)
            archive=pathlib.Path(home)/"exact_original.zip"
            with mock.patch.object(runner.engine,"execute_one",
                                   side_effect=fixtures.fake_native), \
                 mock.patch.object(runner.oil,"ingest_native",
                                   side_effect=fixtures.fake_ingest):
                original=runner.run(
                    ctx,fixtures.F,binary,out,max_native_calls=24,
                    dense_nested_grid_max_level=11,
                    dense_nested_grid_full_scan=True,
                    max_new_native_this_invocation=24)
                self.assertEqual(original["status"],"BUDGET_EXHAUSTED")
                emitted=checkpoint.export_checkpoint(out,archive)
                self.assertEqual(emitted["committed_cases"],24)
                self.assertEqual(checkpoint.verify_checkpoint(
                    archive,emitted["sha256"])["committed_cases"],24)
                self.assertGreaterEqual(emitted["archived_files"],24*4+2)
                with self.assertRaisesRegex(checkpoint.CheckpointBlocked,
                                            "V308_RESTORE_EXACT_EMPTY_OUTPUT_REQUIRED"):
                    checkpoint.restore_same_absolute_path(
                        archive,emitted["sha256"],out)
                shutil.rmtree(out)
                same=checkpoint.restore_same_absolute_path(
                    archive,emitted["sha256"],out)
                self.assertTrue(same["v291_reauthentication_required"])
                verified=runner.run(
                    ctx,fixtures.F,binary,out,max_native_calls=24,
                    dense_nested_grid_max_level=11,
                    dense_nested_grid_full_scan=True,cache_only=True)
                self.assertEqual(verified["status"],"BUDGET_EXHAUSTED")
                self.assertEqual(verified["new_native_this_invocation"],0)
                self.assertEqual(verified["completed_cases"],24)
                with self.assertRaisesRegex(checkpoint.CheckpointBlocked,
                                            "V308_RESTORE_EXACT_EMPTY_OUTPUT_REQUIRED|V308_RESTORE_EXACT_EMPTY_OUTPUT_REQUIRED"):
                    checkpoint.restore_same_absolute_path(
                        archive,emitted["sha256"],out)

    def test_outer_sha_and_member_sha_reject_mutated_archive(self):
        with tempfile.TemporaryDirectory() as home:
            ctx,binary,out=fixtures.V291LongRun().fixture(home,cap=24)
            archive=pathlib.Path(home)/"source.zip"
            with mock.patch.object(runner.engine,"execute_one",
                                   side_effect=fixtures.fake_native), \
                 mock.patch.object(runner.oil,"ingest_native",
                                   side_effect=fixtures.fake_ingest):
                runner.run(ctx,fixtures.F,binary,out,max_native_calls=24,
                           dense_nested_grid_max_level=11,
                           max_new_native_this_invocation=2)
                created=checkpoint.export_checkpoint(out,archive)
                with self.assertRaisesRegex(checkpoint.CheckpointBlocked,
                                            "V308_ORIGINAL_ARCHIVE_SHA_DRIFT"):
                    checkpoint.verify_checkpoint(archive,"0"*64)
                mutated=pathlib.Path(home)/"mutated.zip"
                with zipfile.ZipFile(archive) as inp, \
                     zipfile.ZipFile(mutated,"w",zipfile.ZIP_DEFLATED) as dst:
                    for item in inp.infolist():
                        data=inp.read(item.filename)
                        if item.filename=="cases/case_00000/native/result.json":
                            data+=b"\\n"
                        dst.writestr(item,data)
                with self.assertRaisesRegex(checkpoint.CheckpointBlocked,
                                            "V308_MEMBER_SHA_DRIFT|V308_MEMBER_BOUND_OR_IDENTITY"):
                    checkpoint.verify_checkpoint(
                        mutated,checkpoint.sha256(mutated))
                # Same original archive remains independently verifiable.
                self.assertEqual(checkpoint.verify_checkpoint(
                    archive,created["sha256"])["committed_cases"],2)


if __name__=="__main__":
    unittest.main()
