"""v526: original v106 ordinary worker must resolve exact installed v212 v213.

No physical SimC, Native, HTTP, item effects, or synthetic READY claims.
These are negative and path-identity checks; real Windows evidence is separate.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v106_user_session_controller as sessions


class OriginalInstalledWorkerSource(unittest.TestCase):
    BUILD = "12.1.5.70783"
    SHA = "a" * 64

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="v526-v106-")
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.folder = self.root / ("b"*20)
        self.folder.mkdir()
        self.scope = (self.root/"_fresh_season_sources"/
                      ("wago_"+self.BUILD)/"fresh_source")
        self.scope.mkdir(parents=True)
        self.catalog = self.scope/"v213_candidate_catalog.json"
        self.catalog.write_text("{}\n",encoding="utf8")
        self.identity = {
            "current_season_source_catalog":{
                "game_build":self.BUILD,"artifact_sha256":"c"*64},
            "fresh_v212_installed_manifest_sha256":self.SHA}

    def test_exact_installed_v213_catalog_is_replayed_not_old_package(self):
        path, package = sessions._installed_source_paths(
            self.identity,self.folder)
        self.assertEqual(path,self.catalog)
        self.assertIsNone(package)
        self.assertNotIn("data/current_season_source_to_catalog.json",
                         str(path))

    def test_install_missing_v213_catalog_fails_closed(self):
        self.catalog.unlink()
        with self.assertRaisesRegex(sessions.SessionBlocked,
                                    "V106_FRESH_INSTALLED_WORKER_CATALOG_MISSING"):
            sessions._installed_source_paths(self.identity,self.folder)

    def test_invalid_source_build_and_sha_reject(self):
        for bad in ("12.1.5.70784","12.1.5.xxx","../../source"):
            identity={**self.identity,
                      "current_season_source_catalog":{"game_build":bad}}
            with self.subTest(bad=bad):
                with self.assertRaises(sessions.SessionBlocked):
                    sessions._installed_source_paths(identity,self.folder)
        with self.assertRaisesRegex(sessions.SessionBlocked,
                                    "V106_FRESH_INSTALLED_WORKER_SOURCE_IDENTITY_INVALID"):
            sessions._installed_source_paths({
                **self.identity,
                "fresh_v212_installed_manifest_sha256":"0"*63},self.folder)

    def test_legacy_packaged_paths_unchanged(self):
        identity={"current_season_source_catalog":{
            "game_build":self.BUILD}}
        path, package = sessions._installed_source_paths(identity)
        self.assertEqual(path,ROOT/"data"/"current_season_source_to_catalog.json")
        self.assertIsNone(package)
        identity["current_season_source_catalog"]["package_manifest_sha256"]="d"*64
        _, package = sessions._installed_source_paths(identity)
        self.assertEqual(package,ROOT/"V181_PACKAGE_MANIFEST.json")

    def test_no_source_identity_retains_legacy_none(self):
        self.assertEqual(
            sessions._installed_source_paths({},self.folder),(None,None))


if __name__=="__main__":
    unittest.main()
