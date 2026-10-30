"""v178 real cancel/resume harness preconditions; offline, zero SimC calls."""
from __future__ import annotations
import pathlib,sys,tempfile,unittest
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"runner"),str(ROOT/"integration_probes")]
import v178_real_user_cancel_resume as diag

class CancelResumeDiagnosticOffline(unittest.TestCase):
    def test_real_run_guard_refuses_fake_simc_binary_before_any_native(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            binary=root/"not-real-simc";binary.write_bytes(b"NOT_REAL_NATIVE")
            with mock.patch.object(diag.durable.engine.subprocess,"run") as native:
                with self.assertRaisesRegex(AssertionError,
                                            "V178_PINNED_SIMC_BINARY_CHANGED"):
                    diag.run(binary,root/"out")
                native.assert_not_called()
            self.assertFalse((root/"out").exists())

    def test_exclusive_real_program_targets_one_new_product_session(self):
        self.assertEqual(diag.REVISION,"7bc10711b5")
        self.assertEqual(diag.SIMC_SHA,
            "64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e")
        self.assertEqual(diag.SCHEMA,"v178_one_current_season_real_cancel_resume_v1")

if __name__=="__main__":unittest.main()
