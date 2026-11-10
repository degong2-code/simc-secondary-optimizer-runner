"""SHA-correct repacked-but-incomplete original case archive must fail."""
import json
import pathlib
import sys
import tempfile
import unittest
import zipfile
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v308_dense_native_checkpoint as checkpoint
import v291_durable_multiscale_native_runner as runner
import test_p3_hx_durable_longrun_offline as fixture


class V308NoPartialTruth(unittest.TestCase):
    def test_all_accepted_journal_cases_require_original_json2_member(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx,binary,out=fixture.V291LongRun().fixture(folder,cap=24)
            with mock.patch.object(runner.engine,"execute_one",
                                   side_effect=fixture.fake_native), \
                 mock.patch.object(runner.oil,"ingest_native",
                                   side_effect=fixture.fake_ingest):
                runner.run(ctx,fixture.F,binary,out,max_native_calls=24,
                           dense_nested_grid_max_level=11,
                           max_new_native_this_invocation=2)
            zipfile_path=pathlib.Path(folder)/"verified.zip"
            original=checkpoint.export_checkpoint(out,zipfile_path)
            self.assertEqual(original["committed_cases"],2)
            missing="cases/case_00001/native/result.json"
            repacked=pathlib.Path(folder)/"repacked.zip"
            with zipfile.ZipFile(zipfile_path) as original_zip:
                manifest=json.loads(original_zip.read(
                    "V308_CHECKPOINT_MANIFEST.json"))
                dropped=[record for record in manifest["entries"]
                         if record["name"]==missing]
                self.assertEqual(len(dropped),1)
                manifest["entries"]=[item for item in manifest["entries"]
                                     if item["name"]!=missing]
                manifest["expanded_bytes"]-=dropped[0]["size"]
                with zipfile.ZipFile(repacked,"w",
                                     zipfile.ZIP_DEFLATED) as target:
                    for item in original_zip.infolist():
                        if item.filename==missing:
                            continue
                        data=(json.dumps(manifest).encode()
                              if item.filename=="V308_CHECKPOINT_MANIFEST.json"
                              else original_zip.read(item.filename))
                        target.writestr(item,data)
            # Attacker can update outer SHA, but cannot claim two exact Native
            # cases are preserved if one raw JSON2 file is absent.
            with self.assertRaisesRegex(
                    checkpoint.CheckpointBlocked,
                    "V308_MISSING_COMPLETE_ORIGINAL_RAW_CASE"):
                checkpoint.verify_checkpoint(
                    repacked,checkpoint.sha256(repacked))


if __name__=="__main__":
    unittest.main()
