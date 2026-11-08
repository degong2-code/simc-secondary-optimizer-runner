"""P3-HAG portable Native: offline synthetic receipt and archive tests."""
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
import zipfile
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"tests")]
import v292_portable_native_case_cache as reuse
from test_p3_hx_durable_longrun_offline import V291LongRun,F,fake_native,fake_ingest


class PortableReuse(unittest.TestCase):
    def fixture(self, folder):
        context,binary,original=V291LongRun().fixture(folder,cap=12)
        with mock.patch.object(reuse.runner.engine,"execute_one",
                               side_effect=fake_native), \
             mock.patch.object(reuse.runner.oil,"ingest_native",
                               side_effect=fake_ingest):
            result=reuse.runner.run(context,F,binary,original,
                max_native_calls=12,max_new_native_this_invocation=4)
            self.assertEqual(result["completed_cases"],4)
        path=pathlib.Path(folder)/"native-cases.zip"
        with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as z:
            for name in ("V291_SESSION.json","V291_JOURNAL.jsonl"):
                z.write(original/name,name)
            for i in range(4):
                for name in ("input.simc","result.json",
                             "native_receipt.json"):
                    rel="cases/case_%05d/%s"%(i,name)
                    z.write(reuse.runner.case_folder(original,i)/name,rel)
        return context,binary,original,path,hashlib.sha256(
            path.read_bytes()).hexdigest()

    @staticmethod
    def old_verify(req,calibration,receipt,raw):
        assert req["case_key"]==receipt["case_key"]
        assert hashlib.sha256(raw).hexdigest()==receipt["native_json_sha256"]
        return {"case_key":req["case_key"]}

    @staticmethod
    def new_ingest(req,doc,calibration,raw):
        assert doc["case_key"]==req["case_key"]
        return {"case_key":req["case_key"],
                "native_json_sha256":hashlib.sha256(raw).hexdigest()}

    def patched(self):
        return (
            mock.patch.object(reuse.runner.engine,"execute_one",
                              side_effect=fake_native),
            mock.patch.object(reuse.runner.oil,"ingest_native",
                              side_effect=fake_ingest),
            mock.patch.object(reuse.runner.engine.evaluator,
                              "verify_disk_cache",side_effect=self.old_verify),
            mock.patch.object(reuse.runner.engine.evaluator,
                              "ingest_native",side_effect=self.new_ingest)
        )

    def test_import_four_and_replay_zero_native_with_rebased_sha(self):
        with tempfile.TemporaryDirectory() as folder:
            context,binary,original,archive,sha=self.fixture(folder)
            dest=pathlib.Path(folder)/"second-job-native"
            patches=self.patched()
            with patches[0],patches[1],patches[2],patches[3]:
                report=reuse.import_verified_archive(
                    context,F,binary,dest,archive,sha,max_native_calls=12)
                self.assertEqual(report["completed_cases"],4)
                self.assertEqual(report["new_native_this_invocation"],0)
                self.assertEqual(report["native_attempts_cumulative"],4)
                old=reuse.runner._load_journal(original/"V291_JOURNAL.jsonl")
                new=reuse.runner._load_journal(dest/"V291_JOURNAL.jsonl")
                self.assertEqual([x["case_key"] for x in old],
                                 [x["case_key"] for x in new])
                self.assertNotEqual(old[0]["input_sha256"],
                                    new[0]["input_sha256"])
                self.assertTrue(all(x["source"]=="PORTABLE_REVALIDATED_NATIVE"
                                    for x in new))
                self.assertEqual(reuse.runner.read_json(
                    dest/"V292_IMPORT.json")["new_native_executions"],0)
                replay=reuse.runner.run(context,F,binary,dest,
                    max_native_calls=12,max_new_native_this_invocation=0,
                    cache_only=True)
                self.assertEqual(replay["new_native_this_invocation"],0)
                with self.assertRaisesRegex(
                        reuse.runner.LongRunBlocked,
                        "PORTABLE_IMPORT_DESTINATION_MUST_BE_NEW"):
                    reuse.import_verified_archive(
                        context,F,binary,dest,archive,sha,max_native_calls=12)

    def test_tampered_digest_and_different_profile_fail_before_writing(self):
        with tempfile.TemporaryDirectory() as folder:
            context,binary,original,archive,sha=self.fixture(folder)
            dest=pathlib.Path(folder)/"must-not-exist"
            with self.assertRaisesRegex(reuse.runner.LongRunBlocked,
                                        "PORTABLE_ORIGINAL_ARCHIVE_SHA_MISMATCH"):
                reuse.import_verified_archive(
                    context,F,binary,dest,archive,"0"*64,max_native_calls=12)
            self.assertFalse(dest.exists())
            changed=dict(context)
            changed["identity"]={
                **context["identity"],"source_profile_sha256":"1"*64}
            with self.assertRaises(reuse.runner.LongRunBlocked):
                reuse.import_verified_archive(
                    changed,F,binary,dest,archive,sha,max_native_calls=12)
            self.assertFalse(dest.exists())

    def test_archive_extra_members_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            context,binary,original,archive,sha=self.fixture(folder)
            changed=pathlib.Path(folder)/"foreign.zip"
            with zipfile.ZipFile(archive) as a, zipfile.ZipFile(changed,"w") as b:
                for item in a.infolist():
                    b.writestr(item,a.read(item.filename))
                b.writestr("../escape","bad")
            digest=hashlib.sha256(changed.read_bytes()).hexdigest()
            with self.assertRaisesRegex(reuse.runner.LongRunBlocked,
                                        "PORTABLE_FOREIGN_OR_MISSING_ARCHIVE_MEMBERS"):
                reuse.import_verified_archive(
                    context,F,binary,pathlib.Path(folder)/"no",
                    changed,digest,max_native_calls=12)


if __name__=="__main__":
    unittest.main()
