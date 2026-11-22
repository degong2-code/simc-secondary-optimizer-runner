"""P3 v658: generic SimC Windows builder request/receipt unit tests (Native 0)."""
import json
import pathlib
import sys
import tempfile
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"integration_probes"))
import v658_generic_simc_win64_build as build
import v661_public_simc_cache as cache

REV="6924096820c0b5c9d7bfa9848ea48fe0cd15c7d7"
GAME="12.1.5.70961"
REQUEST={"schema":build.SCHEMA,"source_repo":build.REPO,
         "source_sha":REV,"game_build":GAME,
         "target":"windows-x64-cli","reason":"official_binary_unavailable"}

class GenericWindowsBuilder(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.folder=pathlib.Path(tmp.name)
        self.request_file=self.folder/"request.json"
        self.request_file.write_text(json.dumps(REQUEST),"utf8")
        self.src=self.folder/"src"
        generated=self.src/"engine/dbc/generated"
        generated.mkdir(parents=True)
        (generated/"client_data_version.inc").write_text(
            f'#define CLIENT_DATA_WOW_VERSION "{GAME}"\n',"utf8")
        for filename,prefix in build.SOURCE_HEADERS:
            (generated/filename).write_text(prefix+GAME+"\n","utf8")
        (self.src/"engine/config.hpp").write_text(
            '#define SC_MAJOR_VERSION "1210"\n'
            '#define SC_MINOR_VERSION "01"\n',"utf8")

    def test_request_rejects_unpinned_and_untrusted_inputs(self):
        self.assertEqual(build.read_request(self.request_file),REQUEST)
        for key,value in (
             ("source_repo","attacker/simc"),("source_sha","6924096"),
             ("source_sha","x"*40),("game_build","70961"),
             ("target","linux-x64"),("reason","arbitrary")):
            with self.subTest(key=key,value=value):
                altered=dict(REQUEST);altered[key]=value
                self.request_file.write_text(json.dumps(altered),"utf8")
                with self.assertRaises(build.BuildBlocked):
                    build.read_request(self.request_file)
        altered=dict(REQUEST);altered["command"]="echo injected"
        self.request_file.write_text(json.dumps(altered),"utf8")
        with self.assertRaisesRegex(build.BuildBlocked,"FIELDS_INVALID"):
            build.read_request(self.request_file)

    def test_source_revision_four_headers_and_series(self):
        result=build.source_identity(self.src,REQUEST,REV)
        self.assertEqual(result["source_headers_checked"],4)
        self.assertEqual(result["series"],"1210.01")
        self.assertFalse(result["binary_verified"])
        with self.assertRaisesRegex(build.BuildBlocked,"SHA_MISMATCH"):
            build.source_identity(self.src,REQUEST,"f"*40)
        (self.src/"engine/dbc/generated/gem_data.inc").write_text(
            "// Gem properties, wow build 12.1.5.70783\n","utf8")
        with self.assertRaisesRegex(build.BuildBlocked,"GENERATED_HEADER_MISMATCH"):
            build.source_identity(self.src,REQUEST,REV)

    def test_windows_checkout_crlf_does_not_change_generated_version(self):
        generated=self.src/"engine/dbc/generated"
        (generated/"client_data_version.inc").write_bytes(
            ('#define CLIENT_DATA_WOW_VERSION "'+GAME+'"\r\n').encode("utf8"))
        for name,prefix in build.SOURCE_HEADERS:
            (generated/name).write_bytes((prefix+GAME+"\r\n").encode("utf8"))
        self.assertEqual(build.source_identity(self.src,REQUEST,REV)["source_headers_checked"],4)

    def test_package_nonofficial_provenance_and_windows_x64(self):
        evidence=build.source_identity(self.src,REQUEST,REV)
        archive=self.folder/("simc-1210.01."+REV[:7]+"-win64.7z")
        archive.write_bytes(build.MAGIC+b"abcde"*25000)
        exe=self.folder/"simc.exe"
        raw=bytearray(b"MZ"+b"x"*120000)
        raw[0x3c:0x40]=(128).to_bytes(4,"little")
        raw[128:134]=b"PE\x00\x00\x64\x86"
        exe.write_bytes(raw)
        smoke=self.folder/"smoke.txt"
        smoke.write_text("SimulationCraft 12.1.5.70961\n","utf8")
        p=build.package_receipt(REQUEST,evidence,archive,exe,smoke)
        self.assertTrue(p["binary_embedded_build_verified"])
        self.assertFalse(p["official_release"])
        self.assertFalse(p["season_environment_ready"])
        self.assertEqual(p["native_dps_calls"],0)
        smoke.write_text("SimulationCraft 12.1.5.70783\n","utf8")
        with self.assertRaisesRegex(build.BuildBlocked,"REPORTED_BUILD_CONFLICT"):
            build.package_receipt(REQUEST,evidence,archive,exe,smoke)
        other=self.folder/"simc-1210.01.0d19401-win64.7z"
        archive.rename(other)
        with self.assertRaisesRegex(build.BuildBlocked,"WRONG_REVISION"):
            build.package_receipt(REQUEST,evidence,other,exe,smoke)

    def test_builder_workflow_is_source_general(self):
        wf=(ROOT/".github/workflows/p3_v658_generic_simc_windows_cli.yml").read_text("utf8")
        self.assertIn("build_requests/simc_win64_cli.json",wf)
        self.assertIn("ref: ${{ steps.request.outputs.source_sha }}",wf)
        self.assertIn("BUILD_GUI=OFF",wf)
        self.assertIn("CMAKE_BUILD_TYPE=Release",wf)
        self.assertIn("--target package",wf)
        self.assertNotIn("6924096",wf)
        self.assertNotIn("70961",wf)
        self.assertNotIn("SC_DEFAULT_APIKEY",wf)
        self.assertIn("retention-days: 14",wf)
        self.assertIn("v661_public_simc_cache.py status",wf)
        self.assertIn("v661_public_simc_cache.py package",wf)
        self.assertIn("gh release create",wf)
        self.assertIn("contents: write",wf)
        self.assertIn("if: steps.cache.outputs.hit != 'true'",wf)


    def test_v661_public_cache_miss_hit_and_malformed_existing_release(self):
        tag = "simc-cli-source-" + REV
        asset_name = "simc-win64-cli-" + REV[:7] + "-" + GAME + ".zip"
        release = {
            "tag_name": tag, "draft": False, "prerelease": True,
            "assets": [{
                "name": asset_name, "size": 120000, "state": "uploaded",
                "digest": "sha256:" + "f" * 64,
                "browser_download_url": (
                    "https://github.com/" + cache.REPO + "/releases/download/" +
                    tag + "/" + asset_name),
            }],
        }
        self.assertEqual(cache.cache_status(
            self.request_file, loader=lambda sha: None), "CACHE_MISS")
        self.assertEqual(cache.cache_status(
            self.request_file, loader=lambda sha: release), "CACHE_HIT")
        malformed = json.loads(json.dumps(release))
        malformed["assets"][0]["digest"] = "sha256:invalid"
        with self.assertRaisesRegex(cache.CacheBlocked, "ASSET_INVALID"):
            cache.cache_status(self.request_file, loader=lambda sha: malformed)
        malformed = json.loads(json.dumps(release))
        malformed["prerelease"] = False
        with self.assertRaisesRegex(cache.CacheBlocked, "UNTRUSTED"):
            cache.cache_status(self.request_file, loader=lambda sha: malformed)

    def test_v661_exact_four_member_packaging_and_no_silent_extra_input(self):
        proof = build.source_identity(self.src, REQUEST, REV)
        folder = self.folder / "build-out"
        folder.mkdir()
        archive = folder / ("simc-1210.01." + REV[:7] + "-win64.7z")
        archive.write_bytes(build.MAGIC + b"abcde" * 25000)
        exe = self.folder / "simc.exe"
        raw = bytearray(b"MZ" + b"x" * 120000)
        raw[0x3c:0x40] = (128).to_bytes(4, "little")
        raw[128:134] = b"PE\x00\x00\x64\x86"
        exe.write_bytes(raw)
        smoke = folder / "display_build.txt"
        smoke.write_text("SimulationCraft 12.1.5.70961 Live\n", "utf8")
        receipt = build.package_receipt(REQUEST, proof, archive, exe, smoke)
        (folder / "build_receipt.json").write_text(json.dumps(receipt), "utf8")
        (folder / "source_proof.json").write_text(json.dumps(proof), "utf8")
        target = self.folder / (
            "simc-win64-cli-" + REV[:7] + "-" + GAME + ".zip")
        cache_sha = cache.make_release_zip(self.request_file, folder, target)
        self.assertEqual(len(cache_sha), 64)
        from v659_simc_self_built_artifact import inspect_artifact
        info = inspect_artifact(target)
        self.assertEqual(info["source_sha"], REV)
        self.assertEqual(info["game_build"], GAME)
        self.assertEqual(info["artifact_sha256"], cache_sha)
        with self.assertRaisesRegex(cache.CacheBlocked, "COLLISION"):
            cache.make_release_zip(self.request_file, folder, target)
        (folder / "unexpected.txt").write_text("do not publish")
        second = self.folder / "other" / target.name
        with self.assertRaisesRegex(cache.CacheBlocked, "EXTRA_OR_MISSING"):
            cache.make_release_zip(self.request_file, folder, second)

if __name__=="__main__":
    unittest.main()
