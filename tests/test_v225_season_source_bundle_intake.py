"""New-season source bundle intake: pinned bytes, builds, origin roles, no budget publication."""
from __future__ import annotations
import copy
import json
import pathlib
import tempfile
import unittest

from runner import v225_season_source_bundle_intake as bundle
from tests.test_v224_season_gjfo_evidence_inventory import fixture


class BundleIntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        self.target_build = "12.2.0.99999"
        _, _, sources = fixture(event="season_change",
                                build=self.target_build)
        self.manifest = {
            "schema": bundle.SCHEMA,
            "event": "season_change",
            "game_build": self.target_build,
            "previous_game_build": "12.1.5.70575",
            "expansion_id": 11,
            "season": "synthetic_next_season_test_only",
            "simc_revision": "a" * 40,
            "sources": {},
        }
        for key, filename in bundle.SOURCE_FILES.items():
            path = self.root / filename
            path.write_text(json.dumps(sources[key][0], sort_keys=True) + "\n",
                            encoding="utf8")
            system = ("verified_public_item_source" if key == "budget"
                      else "wago_db2_build_snapshot")
            uri = ("https://www.wowhead.com/item=123456"
                   if key == "budget" else
                   "https://wago.tools/db2/ItemSparse/csv?build=" +
                   self.target_build)
            self.manifest["sources"][key] = {
                "filename": filename, "sha256": bundle.sha(path.read_bytes()),
                "source_system": system,
                "source_locator": uri, "source_build": self.target_build,
                "retrieval_receipt_sha256": "e" * 64,
            }
        self.write_manifest()

    def write_manifest(self):
        (self.root / "source_manifest.json").write_text(
            json.dumps(self.manifest, sort_keys=True) + "\n",
            encoding="utf8")

    def verify(self):
        return bundle.verify_bundle(
            folder=self.root, event="season_change",
            previous_game_build="12.1.5.70575", target_ilevel=335)

    def test_new_season_bytes_bound_but_GJFO_all_unverified(self):
        result = self.verify()
        self.assertEqual(result["game_build"],self.target_build)
        self.assertEqual(set(result["source_input_sha256"]),
                         {"gear","tier","budget"})
        self.assertEqual(result["missing_components"],["G","J","F","O"])
        self.assertTrue(all(result[key] is None for key in
                            ["G","J","F","O","B","T"]))
        self.assertFalse(result["ready"])
        self.assertFalse(result["source_origin_independently_authenticated"])
        self.assertEqual(result["native_calls"],0)
        raw = {k:v for k,v in result.items() if k!="receipt_sha256"}
        self.assertEqual(bundle.sha(bundle.canonical(raw).encode()),
                         result["receipt_sha256"])

    def test_fails_when_source_bytes_change_after_download(self):
        path=self.root/"gear.json"
        path.write_bytes(path.read_bytes()+b" ")
        with self.assertRaisesRegex(bundle.SourceBundleBlocked,
                                    "SOURCE_BYTES_CHANGED"):
            self.verify()

    def test_new_season_cannot_relabel_old_build(self):
        self.manifest["game_build"]="12.1.5.70575"
        for row in self.manifest["sources"].values():
            row["source_build"]="12.1.5.70575"
        self.write_manifest()
        with self.assertRaisesRegex(bundle.SourceBundleBlocked,
                                    "DB2_SOURCE_EXPLICIT_BUILD_REQUIRED"):
            self.verify()
        # Even if the declared DB2 source URL is also relabelled to
        # match the old build, the new-season request remains blocked.
        for row in self.manifest["sources"].values():
            row["source_locator"]=row["source_locator"].replace(
                "build=12.2.0.99999","build=12.1.5.70575")
        self.write_manifest()
        with self.assertRaisesRegex(bundle.SourceBundleBlocked,
                                    "CORE_SOURCE_PREFLIGHT_BLOCKED"):
            self.verify()

    def test_ambiguous_or_foreign_source_system_rejected(self):
        self.manifest["sources"]["gear"]["source_system"]="verified_public_item_source"
        self.write_manifest()
        with self.assertRaisesRegex(bundle.SourceBundleBlocked,
                                    "SOURCE_ORIGIN_DECLARATION"):
            self.verify()
        self.manifest["sources"]["gear"]["source_system"]="wago_db2_build_snapshot"
        self.manifest["sources"]["gear"]["source_locator"]="https://evil.example/db2/ItemSparse/csv?build="+self.target_build
        self.write_manifest()
        with self.assertRaisesRegex(bundle.SourceBundleBlocked,
                                    "ORIGIN_HOST_OR_PROTOCOL"):
            self.verify()

    def test_wago_build_and_blizzard_resource_locator_must_be_explicit(self):
        self.manifest["sources"]["tier"]["source_locator"]="https://wago.tools/db2/Item/csv"
        self.write_manifest()
        with self.assertRaisesRegex(bundle.SourceBundleBlocked,
                                    "DB2_SOURCE_EXPLICIT_BUILD"):
            self.verify()
        self.manifest["sources"]["tier"]["source_system"]="blizzard_game_data_api"
        self.manifest["sources"]["tier"]["source_locator"]="https://us.api.blizzard.com/data/wow/item/12345?namespace=static-us"
        self.write_manifest()
        self.assertFalse(self.verify()["ready"])

    def test_nonfixed_paths_and_manifest_fields_block(self):
        self.manifest["sources"]["gear"]["filename"]="../../gear.json"
        self.write_manifest()
        with self.assertRaisesRegex(bundle.SourceBundleBlocked,
                                    "SOURCE_ORIGIN_DECLARATION"):
            self.verify()
        self.manifest["sources"]["gear"]["filename"]="gear.json"
        self.manifest["extra"]="possibly_verified"
        self.write_manifest()
        with self.assertRaisesRegex(bundle.SourceBundleBlocked,
                                    "MANIFEST_FIELDS_INVALID"):
            self.verify()

    def test_missing_file_symlink_and_manifest_scope(self):
        (self.root/"tier.json").unlink()
        with self.assertRaisesRegex(bundle.SourceBundleBlocked,
                                    "UNSAFE_OR_MISSING"):
            self.verify()
        (self.root/"tier.json").write_text("{}",encoding="utf8")
        try:
            link=self.root/"symlink.json"
            link.symlink_to(self.root/"gear.json")
        except OSError:
            return
        self.manifest["sources"]["gear"]["filename"]="symlink.json"
        self.write_manifest()
        with self.assertRaisesRegex(bundle.SourceBundleBlocked,
                                    "SOURCE_ORIGIN_DECLARATION"):
            self.verify()

    def test_unrelated_event_request_blocked(self):
        with self.assertRaisesRegex(bundle.SourceBundleBlocked,
                                    "REQUEST_EVENT_OR_PREVIOUS_BUILD"):
            bundle.verify_bundle(
                folder=self.root,event="mid_patch",
                previous_game_build="12.1.5.70575",target_ilevel=335)

    def test_cli_result_and_failed_rewrite_preserves_previous_receipt(self):
        target=self.root/"receipt.json"
        args=["--bundle-dir",str(self.root),"--event","season_change",
              "--previous-game-build","12.1.5.70575",
              "--target-ilevel","335","--out",str(target)]
        self.assertEqual(bundle.main(args),0)
        original=target.read_bytes()
        self.manifest["sources"]["budget"]["sha256"]="d"*64
        self.write_manifest()
        with self.assertRaisesRegex(bundle.SourceBundleBlocked,
                                    "SOURCE_BYTES_CHANGED"):
            bundle.main(args)
        self.assertEqual(target.read_bytes(),original)


if __name__=="__main__":
    unittest.main()
