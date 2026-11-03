"""Offline smoke/regression for required development-record preflight."""
from __future__ import annotations
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "dev_ledger_guard", ROOT / "tools" / "check_development_ledger.py")
ledger = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ledger)


class DevelopmentLedgerGuardTests(unittest.TestCase):
    def test_actual_index_and_note_links_are_consistent(self):
        self.assertEqual(ledger.validate(ROOT), [])

    def test_index_has_distinct_evidence_and_integration_status(self):
        entries, errors = ledger._index(ROOT)
        self.assertFalse(errors, errors)
        self.assertEqual(entries["TIER.SEASON"][2], "`SOURCE_CORROBORATED`")
        self.assertEqual(entries["TIER.SEASON"][3], "`NOT_INTEGRATED`")
        self.assertIn("P3-AQ", entries["TIER.SEASON"][4])
        self.assertIn("P3-AR", entries["TIER.SEASON"][4])
        self.assertIn("P3-AT", entries["TIER.SEASON"][4])

    def test_code_change_without_note_must_fail_fast(self):
        self.assertIn("TASK_CHANGE_WITHOUT_DEVELOPMENT_NOTE",
                      ledger.check_changed_files(["runner/v216.py"]))
        self.assertEqual(ledger.check_changed_files([
            "runner/v216.py",
            "docs/development/notes/2026-11-03_example.md",
            "docs/development/INDEX.md",
        ]), [])

    def test_note_without_capability_index_update_is_rejected(self):
        self.assertIn("TASK_NOTE_WITHOUT_INDEX_UPDATE",
                      ledger.check_changed_files([
                          "docs/development/notes/2026-11-03_example.md"
                      ]))
        self.assertEqual(ledger.check_changed_files([
            "docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md"
        ]), [])


if __name__ == "__main__":
    unittest.main()
