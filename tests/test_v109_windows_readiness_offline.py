"""v109 diagnostic is a private-safe plan check, not a SimC Native test."""
import json,os,pathlib,sys,tempfile,unittest,zipfile
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v106_user_session_controller as ux
import v109_windows_readiness_diagnostic as doctor

class ReadinessOffline(unittest.TestCase):
    def fixture(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path=pathlib.Path(tmp.name)
        binary=path/("simc.exe" if os.name=="nt" else "simc.fake")
        binary.write_bytes(b"MZ\x00\x00FAKE_NOT_AN_EXECUTABLE")
        return path,binary

    def test_each_six_current_dps_specs_prepare_without_native(self):
        for key in ux.SUPPORTED:
            with self.subTest(key=key):
                root,binary=self.fixture()
                user=ux.user_scenario(ux.standard_controls(key))
                receipt=doctor.safe_receipt(user,binary,"7bc10711b5",
                    root=root/"runs")
                self.assertEqual(receipt["status"],"PASS_ZERO_NATIVE_PLAN_ONLY")
                self.assertEqual(receipt["new_native_calls"],0)
                self.assertEqual(receipt["maximum_native_calls_if_started"],6)
                self.assertEqual(receipt["minimum_native_calls_if_started"],6)
                self.assertEqual(receipt["final_T"],
                    receipt["base_B"]+receipt["oil_O_total"])
                self.assertFalse(receipt["revision_binary_match_verified"])
                self.assertFalse(receipt["Windows_real_SimC_executed"])
                self.assertFalse(receipt["resume_after_cancel_tested"])
                session_folder=root/"runs"/receipt["session_key"]
                self.assertTrue((session_folder/"generated"/"manifest.json").is_file())
                self.assertFalse((session_folder/"generated"/"simc_results").exists())
                self.assertFalse((session_folder/"V106_WORKER_STATE.json").exists())

    def test_zip_contains_no_talents_full_gear_or_absolute_binary_path(self):
        root,binary=self.fixture()
        controls=ux.standard_controls()
        user=ux.user_scenario(controls)
        report=doctor.safe_receipt(user,binary,"7bc10711b5",root=root/"runs")
        archive=doctor.archive_receipt(report,out=root/"export",open_folder=False)
        with zipfile.ZipFile(archive) as z:
            self.assertEqual(set(z.namelist()),
                {"V109_READINESS_RECEIPT.json","READ_ME_FIRST.txt"})
            payload="\n".join(z.read(x).decode("utf8") for x in z.namelist())
        self.assertNotIn(str(binary),payload)
        self.assertNotIn(controls["talents"],payload)
        self.assertNotIn("USER_SETTINGS.json",payload)
        self.assertNotIn("C:\\Users\\",payload)
        self.assertIn("PASS_ZERO_NATIVE_PLAN_ONLY",payload)

    def test_bogus_revision_does_not_silently_become_verified(self):
        root,binary=self.fixture()
        user=ux.user_scenario(ux.standard_controls())
        result=doctor.safe_receipt(user,binary,"not_a_revision",root=root/"runs")
        self.assertEqual(result["status"],"BLOCKED_NO_NATIVE")
        self.assertEqual(result["new_native_calls"],0)
        self.assertFalse(result["revision_binary_match_verified"])
        self.assertTrue(result["blocker_code"].startswith("V106_"))

    def test_archive_filename_is_only_source_hash_suggestion_not_binary_proof(self):
        self.assertEqual(
            doctor.revision_from_official_nightly_archive_name(
                "simc-1210-01-win64-7bd7371.7z"),"7bd7371")
        self.assertEqual(
            doctor.revision_from_official_nightly_archive_name(
                "simc-1215-02-win64-7BC10711B5.7z"),"7bc10711b5")
        for invalid in (
            "simc.exe","SimulationCraft.exe","12.1.5",
            "simc-1215-02-win64-notahash.7z",
            "simc-1215-02-win64-7bd7371.zip",
            "simc-1215-02-win64-7bd7371.7z.exe",
            "simc-1215-02-win64-7bd737.7z",
        ):
            with self.subTest(label=invalid):
                with self.assertRaisesRegex(
                    ValueError,"ARCHIVE_FILENAME_NOT_RECOGNIZED"):
                    doctor.revision_from_official_nightly_archive_name(invalid)

    def test_binary_missing_no_native_no_personal_path_in_blocker(self):
        root,binary=self.fixture()
        binary.unlink()
        user=ux.user_scenario(ux.standard_controls())
        result=doctor.safe_receipt(user,binary,"7bc10711b5",root=root/"runs")
        self.assertEqual(result["status"],"BLOCKED_NO_NATIVE")
        self.assertEqual(result["blocker_code"],"V106_SIMC_BINARY_NOT_FOUND")
        self.assertEqual(result["new_native_calls"],0)

    def test_generated_plan_never_runs_real_simc(self):
        root,binary=self.fixture()
        user=ux.user_scenario(ux.standard_controls())
        with mock.patch("v098_target_user_scenario_bootstrap.entry.run_manifest",
                        wraps=doctor.bootstrap.entry.run_manifest) as entry:
            receipt=doctor.safe_receipt(user,binary,"7bc10711b5",
                                        root=root/"runs")
        self.assertEqual(receipt["status"],"PASS_ZERO_NATIVE_PLAN_ONLY")
        self.assertEqual(entry.call_count,1)
        self.assertTrue(entry.call_args.kwargs["plan_only"])

if __name__=="__main__":unittest.main()
