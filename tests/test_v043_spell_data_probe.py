"""Offline contract checks only: never infer item scaling from spell_query."""
import pathlib
import sys
import unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runner'))
import v043_spell_data_probe as v

class V043SpellData(unittest.TestCase):
    def test_bounded_query_contract(self):
        self.assertEqual(v.MAX_QUERY_CALLS, 2)
        self.assertEqual(v.QUERIES, (("buff_1307922", 1307922), ("driver_1307923", 1307923)))
    def test_positive_capture_is_not_applied_effect(self):
        a = v.validate_output(b"Spell ID: 1307922\nEffects: sample text 363 -60\n", 1307922)
        self.assertTrue(a['spell_identifier_visible'])
        self.assertIsNone(a['applied_positive_rating'])
        self.assertIsNone(a['applied_negative_rating'])
        self.assertFalse(a['actual_334_item_proc_scaling_proven'])
    def test_mismatch_rejected(self):
        with self.assertRaisesRegex(v.Refused, 'DBC_SPELL_ID_NOT_FOUND'):
            v.validate_output(b"Spell ID: 1307922\nEffects: sample text 363 -60\n", 1307923)
    def test_malformed_rejected(self):
        with self.assertRaisesRegex(v.Refused, 'DBC_QUERY_OUTPUT_SIZE'):
            v.validate_output(b"1307923", 1307923)
    def test_explicit_query_error_rejected(self):
        with self.assertRaisesRegex(v.Refused, 'DBC_QUERY_ERROR'):
            v.validate_output(b"1307923\nError: invalid spell query as requested!\n", 1307923)
    def test_exact_binary_hash_required(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp)
            binary = p/'fake'
            binary.write_bytes(b'not a pinned simc')
            self.assertEqual(v.run(binary,p/'out'),3)
            self.assertEqual((p/'out'/'V043_RECEIPT.json').exists(),True)
            import json
            out = json.loads((p/'out'/'V043_RECEIPT.json').read_text())
            self.assertFalse(out['test_success'])
            self.assertEqual(out['spell_query_calls'],0)
            self.assertEqual(out['product_admission'], 'BLOCKED_MISSING_INDEPENDENT_EVIDENCE')
if __name__ == '__main__':unittest.main()
