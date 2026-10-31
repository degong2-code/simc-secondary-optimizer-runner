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
                source_raw=archive.read(
                    pack.PREFIX+"/data/current_season_source_to_catalog.json")
                source_doc=json.loads(source_raw)
                self.assertEqual(stored["source_catalog"]["schema"],
                                 "v213_current_season_source_to_catalog_v1")
                self.assertEqual(stored["source_catalog"]["artifact_sha256"],
                                 hashlib.sha256(source_raw).hexdigest())
                self.assertEqual(stored["source_catalog"]["manifest_sha256"],
                                 source_doc["manifest_sha256"])
                self.assertEqual(stored["source_catalog"]["native_calls"],0)
                self.assertEqual(stored["source_catalog"]["network_calls"],0)
                self.assertFalse(stored["source_catalog"]["automatic_ui_promotion"])
                for rec in stored["files"]:
                    source=archive.read(pack.PREFIX+"/"+rec["path"])
                    self.assertEqual(len(source),rec["size"],rec["path"])
                    self.assertEqual(hashlib.sha256(source).hexdigest(),
                                     rec["sha256"],rec["path"])
                self.assertIn(pack.PREFIX+"/runner/webui/index.html",names)
                self.assertIn(pack.PREFIX+"/data/current_season_product_gear_db.json",names)

    def test_missing_critical_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(pack.PackageBlocked,"REQUIRED_FILE_MISSING"):
                pack.select(temp)

if __name__=="__main__":unittest.main()
