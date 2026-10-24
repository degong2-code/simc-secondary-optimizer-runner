import hashlib
import importlib.util
import json
import pathlib
import stat
import tempfile
import unittest
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('v036_source_gate', ROOT/'runner'/'v036_source_gate.py')
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)

class V036SourceGateTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root = pathlib.Path(self.t.name)
        self.archive = self.root/gate.EXPECTED_ARCHIVE

    def make(self, members=None):
        if members is None:
            members={'original-v032/'+gate.EXPECTED_SOURCE: b'# illustrative test fixture, NOT v032 original\n'}
        with zipfile.ZipFile(self.archive, 'w', zipfile.ZIP_DEFLATED) as z:
            for name, content in members.items():
                z.writestr(name, content)
        return self.archive

    def assert_code(self, code):
        with self.assertRaises(gate.GateRejected) as ctx: gate.inspect(self.archive)
        self.assertEqual(ctx.exception.code, code)

    def test_missing_source_fail_closed(self):
        self.assert_code('SOURCE_PACKAGE_REQUIRED')

    def test_archive_basename_exact(self):
        self.make()
        wrong=self.root/'renamed.zip';self.archive.rename(wrong)
        with self.assertRaisesRegex(gate.GateRejected,'UNEXPECTED_ARCHIVE_BASENAME'):gate.inspect(wrong)

    def test_candidate_not_original_validation(self):
        self.make()
        receipt=gate.inspect(self.archive)
        self.assertEqual(receipt['status'],'SOURCE_CANDIDATE_INSPECTED')
        self.assertFalse(receipt['v032_identity_proven'])
        self.assertFalse(receipt['v032_code_executed'])
        self.assertEqual(receipt['engine_entry']['path'],'original-v032/'+gate.EXPECTED_SOURCE)
        self.assertEqual(receipt['file_count'],1)

    def test_correct_pinned_hash_still_not_native(self):
        self.make(); sha=gate.digest_file(self.archive)
        r=gate.inspect(self.archive,sha)
        self.assertTrue(r['expected_hash_provided'])
        self.assertFalse(r['native_simc_run'])
        self.assertFalse(r['v032_regression_run'])

    def test_wrong_pin_rejected(self):
        self.make()
        with self.assertRaisesRegex(gate.GateRejected,'SOURCE_SHA256_MISMATCH'):gate.inspect(self.archive,'0'*64)

    def test_invalid_pin_rejected(self):
        self.make()
        with self.assertRaisesRegex(gate.GateRejected,'BAD_EXPECTED_SHA256'):gate.inspect(self.archive,'12345')

    def test_missing_engine_rejected(self):
        self.make({'v032/README.md':b'no engine'})
        self.assert_code('V032_ORIGINAL_ENGINE_ENTRY_NOT_UNIQUE')

    def test_multiple_engines_rejected(self):
        self.make({'v032/'+gate.EXPECTED_SOURCE:b'x','duplicate/'+gate.EXPECTED_SOURCE:b'y'})
        self.assert_code('V032_ORIGINAL_ENGINE_ENTRY_NOT_UNIQUE')

    def test_traversal_rejected(self):
        self.make({'../bad.py':b'no','ok/'+gate.EXPECTED_SOURCE:b'yes'})
        self.assert_code('UNSAFE_ARCHIVE_PATH')

    def test_backslash_rejected(self):
        self.make({'bad\\source.py':b'no','ok/'+gate.EXPECTED_SOURCE:b'yes'})
        self.assert_code('UNSAFE_ARCHIVE_PATH')

    def test_duplicate_canonical_path_rejected(self):
        self.make({'v032/'+gate.EXPECTED_SOURCE:b'first','v032/'+gate.EXPECTED_SOURCE.lower():b'second'})
        self.assert_code('DUPLICATE_NORMALIZED_ARCHIVE_PATH')

    def test_dot_env_rejected(self):
        self.make({'v032/'+gate.EXPECTED_SOURCE:b'x','v032/.env':b'SECRET=x'})
        self.assert_code('SENSITIVE_FILENAME_PRESENT')

    def test_private_key_rejected(self):
        self.make({'v032/'+gate.EXPECTED_SOURCE:b'x','v032/id_rsa':b'key'})
        self.assert_code('SENSITIVE_FILENAME_PRESENT')

    def test_binary_extension_rejected(self):
        self.make({'v032/'+gate.EXPECTED_SOURCE:b'x','v032/fake.exe':b'exe'})
        self.assert_code('UNEXPECTED_FILE_EXTENSION')

    def test_archive_crc_corrupted(self):
        with zipfile.ZipFile(self.archive, "w", compression=zipfile.ZIP_STORED) as z:
            z.writestr("v032/"+gate.EXPECTED_SOURCE, b"original v032 test payload")
        blob=bytearray(self.archive.read_bytes())
        # Flip source's compressed payload safely without changing the ZIP directory.
        with zipfile.ZipFile(self.archive) as z:
            i=z.infolist()[0]
            offset=i.header_offset+30+len(i.filename.encode())+len(i.extra)
        blob[offset]=blob[offset]^1
        self.archive.write_bytes(blob)
        self.assert_code('INVALID_ZIP_OR_CORRUPT_MEMBER')

    def test_symlink_rejected(self):
        with zipfile.ZipFile(self.archive,'w') as z:
            i=zipfile.ZipInfo('v032/'+gate.EXPECTED_SOURCE)
            i.create_system=3
            i.external_attr=(stat.S_IFLNK|0o777)<<16
            z.writestr(i,'/etc/passwd')
        self.assert_code('UNSAFE_ARCHIVE_ENTRY_TYPE')

    def test_cli_blocked_receipt_written(self):
        receipt=self.root/'out'/'receipt.json'
        self.assertEqual(gate.run(['--source',str(self.archive),'--receipt',str(receipt)]),3)
        v=json.loads(receipt.read_text())
        self.assertEqual(v['reason'],'SOURCE_PACKAGE_REQUIRED')
        self.assertFalse(v['native_simc_run'])

    def test_cli_inspected_receipt_written(self):
        self.make()
        receipt=self.root/'out'/'receipt.json'
        self.assertEqual(gate.run(['--source',str(self.archive),'--receipt',str(receipt)]),0)
        v=json.loads(receipt.read_text())
        self.assertEqual(v['status'],'SOURCE_CANDIDATE_INSPECTED')
        self.assertFalse(v['v032_identity_proven'])

if __name__ == '__main__': unittest.main()
