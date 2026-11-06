"""P3-GJ: audit-only existing Native bytes, no Native or source retrieval."""
import hashlib
import json
import pathlib
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from integration_probes import p3_fr_zero_base_t1_acceptance as probe


class ExistingNativeCaseArchive(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=pathlib.Path(self.temp.name)/"workspace"
        self.root.mkdir()
        self.dest=pathlib.Path(self.temp.name)/"native-audit.zip"

    def case(self, name="v278_baseline_"+"a"*32, changed=False):
        folder=self.root/"stage"/"source"/name
        folder.mkdir(parents=True)
        data={"input.simc":b"simulation profile\n",
              "native.json":b'{"sim":true}',
              "simc.log":b"simc ok\n"}
        manifest={"schema":"v278_original_simc_precombat_native_pair_v1",
                  "identity":{"profile_sha256":"a"*64},
                  "input_sha256":hashlib.sha256(data["input.simc"]).hexdigest(),
                  "native_json2_sha256":hashlib.sha256(data["native.json"]).hexdigest(),
                  "log_sha256":hashlib.sha256(data["simc.log"]).hexdigest(),
                  "status":"NATIVE_JSON2_CAPTURED","new_native_calls":1}
        for key,value in data.items():
            (folder/key).write_bytes(b"tampered" if changed and key=="native.json"
                                     else value)
        (folder/"receipt.json").write_text(json.dumps(manifest),encoding="utf8")
        return folder

    def test_archive_keeps_exact_existing_bytes_not_cache_admission(self):
        folder=self.case()
        result=probe.archive_existing_native_attempts(self.root,self.dest)
        self.assertEqual(result["case_count"],1)
        self.assertEqual(result["file_count"],4)
        self.assertEqual(result["new_native_calls"],0)
        self.assertFalse(result["portable_cache"])
        with zipfile.ZipFile(self.dest) as archive:
            audit=json.loads(archive.read("native_evidence_inventory.json"))
            self.assertEqual(audit["case_count"],1)
            self.assertFalse(audit["zero_history_inputs_reused"])
            self.assertEqual(archive.read(
                (folder/"native.json").relative_to(self.root).as_posix()),
                b'{"sim":true}')
        self.assertEqual(hashlib.sha256(self.dest.read_bytes()).hexdigest(),
                         result["archive_sha256"])

    def test_tampered_native_is_never_archived_as_trusted(self):
        self.case(changed=True)
        with self.assertRaisesRegex(ValueError,"P3_GJ_NATIVE_FILE_SHA_MISMATCH"):
            probe.archive_existing_native_attempts(self.root,self.dest)

    def test_no_native_means_no_archive_or_new_calls(self):
        result=probe.archive_existing_native_attempts(self.root,self.dest)
        self.assertEqual(result["status"],"NO_NATIVE_CASES_TO_ARCHIVE")
        self.assertFalse(self.dest.exists())

    def test_bounded_archive_rejects_oversized_original(self):
        self.case()
        with patch.object(probe,"MAX_NATIVE_FILE_BYTES",1):
            with self.assertRaisesRegex(ValueError,"P3_GJ_NATIVE_FILE_UNSAFE"):
                probe.archive_existing_native_attempts(self.root,self.dest)


if __name__=="__main__":
    unittest.main()
