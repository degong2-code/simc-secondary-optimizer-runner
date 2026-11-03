"""Offline smoke/regression for required development-record preflight."""
from __future__ import annotations
import importlib.util
import pathlib
import tempfile
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

    def test_append_only_old_note_may_be_replaced_as_latest_in_index(self):
        # The index must remain short when hundreds of valid notes accumulate.
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            folder=root/"docs"/"development"
            notes=folder/"notes"
            notes.mkdir(parents=True)
            template=(
                "# Synthetic task note\n"
                "- **Capability:** `TIER.SEASON`\n"
                "- **Keywords:** tier, season\n"
                "- **Prior evidence:** previous actual source receipt\n"
                "- **Decision:** `REUSE` — reuse existing evidence\n"
                "- **Changes:** DOCS_ONLY\n"
                "- **Verification:** REUSED_HISTORY; no Native\n"
                "- **Remaining:** product integration pending\n"
                "- **Efficiency:** no HTTP or Native\n"
            )
            for day,slug in (("2026-11-02","earlier"),
                             ("2026-11-03","newest")):
                (notes/(day+"_"+slug+".md")).write_text(
                    template,encoding="utf8")
            (folder/"INDEX.md").write_text(
                "# Index\n"
                "| Capability | Keywords | Evidence | Integration | Prior evidence | Last note |\n"
                "|---|---|---|---|---|---|\n"
                "| `TIER.SEASON` | tier | `SOURCE_CORROBORATED`"
                " | `NOT_INTEGRATED` | real source receipt"
                " | [latest](notes/2026-11-03_newest.md) |\n",
                encoding="utf8")
            self.assertEqual(ledger.validate(root), [])

    def test_note_without_capability_index_update_is_rejected(self):
        self.assertIn("TASK_NOTE_WITHOUT_INDEX_UPDATE",
                      ledger.check_changed_files([
                          "docs/development/notes/2026-11-03_example.md"
                      ]))
        self.assertIn("TASK_CHANGE_WITHOUT_DEVELOPMENT_NOTE",
                      ledger.check_changed_files([
                          "docs/CURRENT_PRODUCT_DEVELOPMENT_STATE.md"
                      ]))


if __name__ == "__main__":
    unittest.main()
