"""v181 portable Windows beta package: SHA/allowlist/immutable content tests."""
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
import zipfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"integration_probes"))
import v181_windows_beta_packager as pack

class WindowsBetaPackageOffline(unittest.TestCase):
    def test_minimum_sources_no_native_or_cache_and_deterministic_archive(self):
        with tempfile.TemporaryDirectory() as temp:
            one=pathlib.Path(temp)/"a.zip"
            two=pathlib.Path(temp)/"b.zip"
            manifest=pack.build(one)
            self.assertEqual(pack.build(two),manifest)
            self.assertEqual(hashlib.sha256(one.read_bytes()).digest(),
                             hashlib.sha256(two.read_bytes()).digest())
            self.assertGreaterEqual(manifest["file_count"],75)
            self.assertFalse(manifest["native_executable_bundled"])
            self.assertFalse(manifest["sessions_bundled"])
            self.assertFalse(manifest["historical_native_json2_bundled"])
            with zipfile.ZipFile(one) as archive:
                names=archive.namelist()
                self.assertEqual(len(names),len(set(names)))
                self.assertEqual(len(names),manifest["file_count"]+1)
                self.assertTrue(all(s.startswith(pack.PREFIX+"/") for s in names))
                self.assertFalse(any(s.endswith((".exe",".dll",".pyc",".db",".sqlite")) for s in names))
                self.assertFalse(any("/tests/" in s or "/docs/" in s or "/.git" in s
                                     or "/.github/" in s or "/runs/" in s
                                     for s in names))
                stored=json.loads(archive.read(pack.PREFIX+"/V181_PACKAGE_MANIFEST.json"))
                self.assertEqual(stored,manifest)
                required_p3c={
                    "runner/v208_internal_exact_special_L_hydrator.py",
                    "runner/v212_environment_manifest.py",
                    "runner/v217_stage_execution_engine.py",
                    "runner/v218_v098_profile_stage_adapter.py",
                }
                packaged_paths={row["path"] for row in stored["files"]}
                self.assertTrue(required_p3c.issubset(packaged_paths))
                for rel in required_p3c:
                    payload=archive.read(pack.PREFIX+"/"+rel)
                    record=next(row for row in stored["files"] if row["path"]==rel)
                    self.assertEqual(hashlib.sha256(payload).hexdigest(),
                                     record["sha256"],rel)
                self.assertIsNone(stored["source_catalog"])
                self.assertFalse(stored["historical_season_sources_bundled"])
                self.assertEqual(stored["package_variant"],"first_user_zero_history_candidate")
                self.assertFalse(any(pack.historical_season_source(rel) for rel in packaged_paths))
                for rec in stored["files"]:
                    source=archive.read(pack.PREFIX+"/"+rec["path"])
                    self.assertEqual(len(source),rec["size"],rec["path"])
                    self.assertEqual(hashlib.sha256(source).hexdigest(),
                                     rec["sha256"],rec["path"])
                self.assertIn(pack.PREFIX+"/runner/webui/index.html",names)
                self.assertNotIn(pack.PREFIX+"/data/current_season_product_gear_db.json",names)
                self.assertIn(pack.PREFIX+"/runner/v335_environment_official_ko_localization.py",names)
                self.assertNotIn(pack.PREFIX+"/data/current_season_source_to_catalog.json",names)

    def test_explicit_legacy_archive_preserves_verified_source_contract(self):
        if not (ROOT/"data/current_season_source_to_catalog.json").is_file():
            self.skipTest("Explicit historical compatibility source not supplied")
        with tempfile.TemporaryDirectory() as temp:
            target=pathlib.Path(temp)/"legacy.zip"
            manifest=pack.build(target,legacy_source_catalog=True)
            with zipfile.ZipFile(target) as archive:
                raw=archive.read(pack.PREFIX+"/data/current_season_source_to_catalog.json")
                self.assertEqual(manifest["source_catalog"]["artifact_sha256"],
                                 hashlib.sha256(raw).hexdigest())
                self.assertEqual(manifest["source_catalog"]["manifest_sha256"],
                                 json.loads(raw)["manifest_sha256"])
                self.assertFalse(manifest["source_catalog"]["automatic_ui_promotion"])
                self.assertIn(pack.PREFIX+"/data/current_season_gear_ko_KR_verified.json",
                              archive.namelist())


    def test_current_beta_file_list_is_derived_not_a_second_source_of_truth(self):
        """TXT is a snapshot of the same candidates used by ZIP, not READY."""
        with tempfile.TemporaryDirectory() as temp:
            target=pathlib.Path(temp)/"candidate_files.txt"
            paths=pack.write_file_list(target)
            source=pack.select()
            self.assertEqual(paths,sorted(source))
            lines=target.read_text(encoding="utf8").splitlines()
            self.assertTrue(lines[0].startswith(
                "# SIMC Secondary Optimizer: CURRENT_BETA_PACKAGE_CANDIDATES"))
            self.assertIn("# Not a finished-app readiness certificate; see 78-element tracker.",
                          lines)
            self.assertEqual([line for line in lines if not line.startswith("#")],
                             paths)
            self.assertEqual(len(paths),len(set(paths)))
            self.assertIn("runner/v113_local_web_api.py",paths)
            self.assertIn("runner/v645_simc_connection_prefs.py",paths)
            self.assertIn("runner/v216_environment_build_coordinator.py",paths)
            self.assertIn("runner/v155_season_api_probe.py",paths)
            self.assertIn("runner/webui/app.js",paths)
            self.assertFalse(any(pack.historical_season_source(p) for p in paths))
            self.assertNotIn("tests/test_v181_windows_beta_package_offline.py",paths)
            self.assertFalse(any(p.startswith("docs/") or p.endswith(".exe")
                                 for p in paths))
            with self.assertRaisesRegex(pack.PackageBlocked,
                                       "FILE_LIST_EXTENSION_REQUIRED"):
                pack.write_file_list(pathlib.Path(temp)/"bad.zip")

    def test_runtime_web_dependencies_exclude_test_only_httpx2(self):
        """User consent installs only server dependencies; test HTTP client is separate."""
        runtime=(ROOT/"requirements-web.txt").read_text("utf8")
        test_only=(ROOT/"requirements-web-test.txt").read_text("utf8")
        self.assertIn("fastapi>=",runtime)
        self.assertIn("uvicorn>=",runtime)
        self.assertNotIn("httpx2",runtime.lower())
        self.assertNotIn("httpx>=",runtime.lower())
        self.assertIn("-r requirements-web.txt",test_only)
        self.assertIn("httpx>=",test_only)

    def test_easy_start_stale_python_path_recovery_is_version_checked_and_opt_in(self):
        """v575: harmless absolute-path discovery after winget's stale CMD PATH."""
        batch=(ROOT/"START_HERE_AUTO_SETUP_AND_RUN.bat").read_text("utf8")
        self.assertIn('set "SYS_PY_EXE="',batch)
        for path in (
            r'%LOCALAPPDATA%\Programs\Python\Python312\python.exe',
            r'%ProgramFiles%\Python312\python.exe'
        ):
            self.assertIn('if exist "'+path+'"',batch)
            self.assertIn('if not errorlevel 1 set "SYS_PY_EXE='+path+'"',
                          batch)
        self.assertIn(
            'if not defined SYS_PY if not defined SYS_PY_EXE goto :python_missing',
            batch)
        self.assertIn('if defined SYS_PY_EXE (',batch)
        self.assertIn('"%SYS_PY_EXE%" -m venv "%VENV_DIR%"',batch)
        self.assertIn('if errorlevel 1 goto :venv_failed',batch)
        self.assertIn('sys.version_info.major == 3 and sys.version_info.minor >= 12',
                      batch)
        self.assertLess(
            batch.index('choice /C YN /N /M "Install or repair web libraries now?'),
            batch.index('"%SYS_PY_EXE%" -m venv "%VENV_DIR%"'))
        self.assertLess(
            batch.index('choice /C YN /N /M "Install official Python 3.12'),
            batch.index('winget install --id Python.Python.3.12'))
        self.assertIn('if errorlevel 2 goto :cancelled',batch)
        self.assertIn('if "%PYTHON_INSTALL_ATTEMPTED%"=="1" goto :manual_python',
                      batch)
        self.assertIn('if /I "%~1"=="--check" (',batch)

    def test_existing_user_runtime_precedes_python_discovery_and_install_consent(self):
        batch=(ROOT/"START_HERE_AUTO_SETUP_AND_RUN.bat").read_text("utf8")
        ready=batch.index('if not errorlevel 1 goto :start_app')
        self.assertLess(batch.index('set "VENV_DIR=%LOCALAPPDATA%'),ready)
        self.assertLess(ready,batch.index(':check_python'))
        self.assertLess(ready,batch.index('where py'))
        self.assertLess(ready,batch.index('choice /C YN /N /M "Install'))
        self.assertIn('import sys,fastapi,uvicorn,py7zr',batch[:ready])
        self.assertEqual(batch.count('set "VENV_DIR='),1)
        self.assertEqual(batch.count('set "VENV_PY='),1)

    def test_missing_critical_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(pack.PackageBlocked,"REQUIRED_FILE_MISSING"):
                pack.select(temp)

if __name__=="__main__":unittest.main()
