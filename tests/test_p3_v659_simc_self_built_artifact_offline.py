"""v659 generic local self-built SimC ZIP import: no network/Native DPS."""
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
import zipfile
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v193_simc_local_updater as updater
import v659_simc_self_built_artifact as artifact

FULL="6924096820c0b5c9d7bfa9848ea48fe0cd15c7d7"
BUILD="12.1.5.70961"
ARCHIVE="simc-1210.01.6924096-win64.7z"
def sha(data):return hashlib.sha256(data).hexdigest()
def pe_fake():
    data=bytearray(b"MZ"+hashlib.shake_256(b"v659-local-pe").digest(190000))
    data[0x3c:0x40]=(128).to_bytes(4,"little")
    data[128:134]=b"PE\x00\x00\x64\x86"
    return bytes(data)

class SelfBuiltArtifactOffline(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root=pathlib.Path(temp.name)
        self.archive=updater.MAGIC+hashlib.shake_256(b"v659-archive").digest(140000)
        self.exe=pe_fake()
        self.zip=self.root/"simc-win64-cli-artifact.zip"
        self.manager=updater.SimCManager(self.root/"managed",platform="win32")
        self.docs=self.make_docs()
        self.write_zip()

    def make_docs(self):
        proof={"schema":"p3_v658_source_proof_v1",
               "source_sha":FULL,"game_build":BUILD,"series":"1210.01",
               "source_headers_checked":4,"source_verified":True,
               "binary_verified":False,"environment_ready":False}
        receipt={"schema":"p3_v658_windows_cli_build_receipt_v1",
                 "source_repo":"simulationcraft/simc","source_sha":FULL,
                 "source_game_build":BUILD,"archive_name":ARCHIVE,
                 "archive_sha256":sha(self.archive),"archive_bytes":len(self.archive),
                 "cli_sha256":sha(self.exe),"cli_bytes":len(self.exe),
                 "cli_smoke":"PASS","binary_embedded_build_verified":True,
                 "observed_game_build":BUILD,
                 "origin":"SELF_BUILT_UPSTREAM_SIMC_NOT_OFFICIAL_BINARY",
                 "official_release":False,"season_environment_ready":False,
                 "native_dps_calls":0}
        return {"source_proof.json":json.dumps(proof).encode(),
                "build_receipt.json":json.dumps(receipt).encode(),
                "display_build.txt":(
                  "SimulationCraft 1210-01 for World of Warcraft "+BUILD+
                  " Live (hotfix 2026-11-17/70961)\n").encode(),
                ARCHIVE:self.archive}

    def write_zip(self,docs=None):
        with zipfile.ZipFile(self.zip,"w",compression=zipfile.ZIP_DEFLATED) as out:
            for name,data in (docs or self.docs).items():
                out.writestr(name,data)

    def test_valid_receipt_archive_and_exact_digest_import(self):
        result=artifact.inspect_artifact(self.zip)
        self.assertEqual(result["source_sha"],FULL)
        self.assertEqual(result["game_build"],BUILD)
        self.assertEqual(result["cli_sha256"],sha(self.exe))
        self.assertFalse(result["origin_authenticated"])
        final=self.root/"copy.7z"
        proof=artifact.copy_inner_archive(self.zip,final,result)
        self.assertEqual(proof["sha256"],sha(self.archive))
        self.assertEqual(final.read_bytes(),self.archive)

    def test_source_owners_revision_embedded_build_and_hash_fail_closed(self):
        for key,value in (
            ("source_sha","f"*40),("source_game_build","12.1.5.70783"),
            ("observed_game_build","12.1.5.70783"),
            ("archive_name","simc-1210.01.0d19401-win64.7z"),
            ("archive_sha256","0"*64),("archive_bytes",1),
            ("cli_sha256","not-sha"),("binary_embedded_build_verified",False),
            ("origin","OFFICIAL_RELEASE"),("official_release",True)):
            with self.subTest(key=key):
                current=dict(self.docs)
                parsed=json.loads(current["build_receipt.json"])
                parsed[key]=value
                current["build_receipt.json"]=json.dumps(parsed).encode()
                self.write_zip(current)
                with self.assertRaises(artifact.ArtifactBlocked):
                    artifact.inspect_artifact(self.zip)

    def test_missing_or_injected_zip_member_and_wrong_smoke_fail_closed(self):
        for name,data in [
            ("../escape.exe",b"x"),
            ("extra.exe",b"x")]:
            current=dict(self.docs);current[name]=data
            self.write_zip(current)
            with self.assertRaises(artifact.ArtifactBlocked):
                artifact.inspect_artifact(self.zip)
        current=dict(self.docs)
        current["display_build.txt"]=b"SimulationCraft 12.1.5.70783 Live"
        self.write_zip(current)
        with self.assertRaisesRegex(artifact.ArtifactBlocked,"SMOKE_MISMATCH"):
            artifact.inspect_artifact(self.zip)

    def test_modified_zip_after_preflight_rejected(self):
        info=artifact.inspect_artifact(self.zip)
        with self.zip.open("ab") as f:f.write(b"changed")
        with self.assertRaisesRegex(artifact.ArtifactBlocked,"ZIP_CHANGED"):
            artifact.copy_inner_archive(self.zip,self.root/"out.7z",info)

    def test_install_reuses_managed_pointer_and_rollback_without_user_mutation(self):
        def extracted(_archive,folder,_sevenzip):
            exe=folder/"simc.exe"
            exe.write_bytes(self.exe)
            return exe
        result=self.manager.install_self_built(
            str(self.zip),extractor=extracted,sevenzip="7z-test",probe=lambda exe:True)
        self.assertEqual(result["status"],"NEW_MANAGED_SIMC_ACTIVATED")
        self.assertEqual(result["installed"]["source_revision_full"],FULL)
        self.assertEqual(result["installed"]["source_game_build"],BUILD)
        self.assertFalse(result["installed"]["source_origin_authenticated"])
        self.assertEqual(result["installed"]["archive_source"],
            "USER_SELECTED_SELF_BUILT_RECEIPT_UNAUTHENTICATED")
        self.assertEqual(result["installed"]["sha256"],sha(self.exe))
        self.assertEqual(result["dps_native_calls_now"],0)
        self.assertTrue(pathlib.Path(result["active_binary"]).is_file())
        self.assertIsNone(self.manager.rollback()["active_binary"])
        self.assertTrue(pathlib.Path(result["active_binary"]).is_file())

    def test_bad_cli_hash_never_switches_orphan_pointer(self):
        def wrong(_archive,folder,_sevenzip):
            f=folder/"simc.exe";f.write_bytes(pe_fake()+b"different");return f
        with self.assertRaisesRegex(updater.UpdateBlocked,"CLI_SHA_MISMATCH"):
            self.manager.install_self_built(
                str(self.zip),extractor=wrong,sevenzip="mock7z",probe=lambda e:True)
        self.assertFalse((self.root/"managed"/"installed.json").exists())
        self.assertIsNone(self.manager.offer)

    def test_os_and_missing_file_and_non_zip_rejected(self):
        with self.assertRaisesRegex(updater.UpdateBlocked,"ZIP_INVALID"):
            self.manager.install_self_built(str(self.root/"missing.zip"))
        linux=updater.SimCManager(self.root/"linux",platform="linux")
        with self.assertRaisesRegex(updater.UpdateBlocked,"WINDOWS_ONLY"):
            linux.install_self_built(str(self.zip))

    def test_real_cli_probe_requires_observed_build_not_just_simc_name(self):
        fake=mock.Mock(returncode=0,stdout=b"SimulationCraft 12.1.5.70783 Live",stderr=b"")
        with mock.patch.object(updater.subprocess,"run",return_value=fake):
            with self.assertRaisesRegex(updater.UpdateBlocked,
                                         "EMBEDDED_BUILD_NOT_MATCHED"):
                updater.probe_cli(self.root/"simc.exe",expected_build=BUILD)
        fake.stdout=b"SimulationCraft 12.1.5.70961 Live"
        with mock.patch.object(updater.subprocess,"run",return_value=fake):
            self.assertTrue(updater.probe_cli(self.root/"simc.exe",expected_build=BUILD))

    def test_secure_api_and_ui_linkage_without_remote_auto_install(self):
        api=(ROOT/"runner/v113_local_web_api.py").read_text("utf8")
        js=(ROOT/"runner/webui/app.js").read_text("utf8")
        html=(ROOT/"runner/webui/index.html").read_text("utf8")
        self.assertIn('/api/v1/simc-updates/install-self-built',api)
        self.assertIn('updater.install_self_built(request.artifact_path)',api)
        self.assertIn('/api/v1/simc-updates/install-self-built',js)
        self.assertIn('id="simc-self-built-artifact"',html)
        self.assertIn("source_origin_authenticated", (ROOT/"runner/v193_simc_local_updater.py").read_text("utf8"))
        self.assertNotIn("setInterval(",js[js.index("async function installSelfBuiltSimcUpdater()"):js.index("async function rollbackSimcUpdater()")])

if __name__=="__main__":
    unittest.main()
