"""v193: offline official-nightly checks, safe 7z and management lifecycle."""
import hashlib,json,pathlib,ssl,subprocess,sys,tempfile,time,unittest,urllib.error
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v193_simc_local_updater as mod

NAME="simc-1215-01-win64-710c240.7z"
OFFICIAL_GITHUB_NAME="simc-1210.01.710c240-win64.7z"
INDEX="""<html><a href="simc-1210-03-win64-7bc1071.7z">old</a>
<a href="simc-1215-01-win64-710c240.7z">latest</a>
<a href="https://evil.example/simc-9999-win64-fdef789.7z">bad</a>
<a href="../../evil.7z">bad</a>
<a href="simc-1215-01-winarm64-710c240.7z">wrong arch</a>
</html>"""
LIST="7-Zip 24.09\nPath = file.7z\nType = 7z\n\n----------\nPath = simc.exe\nSize = 200001\nAttributes = A\nEncrypted = -\n\nPath = profiles\nSize = 0\nAttributes = D\nEncrypted = -\n"
class SimCUpdateUnit(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.path=pathlib.Path(self.t.name)
        self.m=mod.SimCManager(self.path/"managed",platform="win32")

    def test_only_official_windows_nightly_and_no_arbitrary_url(self):
        selected=mod.candidate_urls(INDEX)
        self.assertEqual(len(selected),2)
        self.assertEqual(selected[0]["filename"],NAME)
        self.assertEqual(selected[0]["revision_short"],"710c240")
        for html in ['<a href="https://attacker.example/simc-1215-01-win64-710c240.7z">',
                     '<a href="simc-1215-01-win64-710c240.7z?evil=1">',
                     '<a href="http://download.simulationcraft.org/nightly/simc-1215-01-win64-710c240.7z">']:
            with self.subTest(html=html):
                self.assertEqual(mod.candidate_urls(html),[])

    def test_invalid_tls_is_reported_and_github_alternative_does_not_install(self):
        failure=urllib.error.URLError(ssl.SSLCertVerificationError("self-signed certificate"))
        self.assertEqual(mod.index_error_code(failure),
                         "OFFICIAL_NIGHTLY_TLS_CERTIFICATE_INVALID")
        alternative={"source":"OFFICIAL_SIMC_GITHUB_ACTIONS",
                     "run_id":40999844143,"artifact_id":12953786078,
                     "artifact_zip_url":"https://github.com/simulationcraft/simc-publish/actions/runs/40999844143/artifacts/12953786078"}
        with mock.patch.object(mod,"fetch_index",side_effect=failure),\
             mock.patch.object(mod,"fetch_github_nightly",return_value=alternative) as github:
            result=self.m.check()
        github.assert_called_once()
        self.assertIsNone(result["candidate"])
        self.assertFalse(result["direct_install_available"])
        self.assertTrue(result["manual_archive_required"])
        self.assertEqual(result["official_index_problem"],
                         "OFFICIAL_NIGHTLY_TLS_CERTIFICATE_INVALID")
        self.assertEqual(result["github_alternative"],alternative)
        self.assertIsNone(self.m.offer)
        self.assertFalse((self.path/"managed").exists())

    def test_official_github_artifact_found_even_if_nightly_run_failed(self):
        calls=[]
        def fake(url):
            calls.append(url)
            if url==mod.GITHUB_RUNS:
                return {"workflow_runs":[{"id":40999844143,"name":"Nightly",
                       "conclusion":"failure","created_at":"2026-10-30T03:53:23Z"}]}
            return {"artifacts":[{"id":12953786078,
                "name":"simc-nightly-win64-midnight","expired":False},
                {"id":12953786079,"name":"simc-nightly-winarm64-midnight",
                 "expired":False}]}
        with mock.patch.object(mod,"fetch_github_json",side_effect=fake):
            result=mod.fetch_github_nightly()
        self.assertEqual(result["artifact_id"],12953786078)
        self.assertIn("/40999844143/artifacts/12953786078",
                      result["artifact_zip_url"])
        self.assertFalse(result["direct_install_available"])
        self.assertEqual(len(calls),2)

    def test_official_and_github_network_failures_return_manual_instructions(self):
        with mock.patch.object(mod,"fetch_index",
                               side_effect=urllib.error.URLError("network down")),\
             mock.patch.object(mod,"fetch_github_nightly",
                               side_effect=urllib.error.URLError("network down")):
            response=self.m.check()
        self.assertEqual(response["official_index_problem"],
                         "OFFICIAL_NIGHTLY_CONNECTION_UNAVAILABLE")
        self.assertIsNone(response["github_alternative"])
        self.assertTrue(response["github_actions_url"].startswith("https://github.com/"))
        self.assertFalse(response["direct_install_available"])

    def test_real_official_github_actions_cpack_filename_is_accepted(self):
        # Grounded in real simc-publish Nightly Win64 artifact 12953786078:
        # simc-version + simc-1210.01.710c240-win64.7z (120946271 bytes).
        identity=mod.nightly_identity(OFFICIAL_GITHUB_NAME)
        self.assertEqual(identity,{"filename":OFFICIAL_GITHUB_NAME,
                                 "series":"1210.01",
                                 "revision_short":"710c240"})
        cases=[(NAME,"1215-01","710c240"),
               (OFFICIAL_GITHUB_NAME,"1210.01","710c240")]
        for name,series,revision in cases:
            with self.subTest(name=name):
                self.assertEqual(mod.nightly_identity(name)["series"],series)
                self.assertEqual(mod.nightly_identity(name)["revision_short"],revision)
        self.assertEqual(mod.candidate_urls(
            '<a href="'+OFFICIAL_GITHUB_NAME+'">official nightly</a>')[0]["filename"],
            OFFICIAL_GITHUB_NAME)
        for invalid in ("simc-1210.01.710c240-winarm64.7z",
                        "simc-1210.01.710c240-win64.zip",
                        "../simc-1210.01.710c240-win64.7z",
                        "simc-1210.01.not-a-hash-win64.7z"):
            if "/" not in invalid:
                self.assertIsNone(mod.nightly_identity(invalid))

    def test_local_install_accepts_real_github_7z_filename_without_rename(self):
        archive=self.path/OFFICIAL_GITHUB_NAME
        archive.write_bytes(mod.MAGIC+b"nightly"*20000)
        def extractor(source,stage,tool):
            exe=stage/"simc.exe"
            exe.write_bytes(b"MZ"+b"portable_fake_pe"*11000)
            return exe
        result=self.m.install_local(str(archive),extractor=extractor,
                                    sevenzip="mock7z")
        self.assertEqual(result["installed"]["filename"],OFFICIAL_GITHUB_NAME)
        self.assertEqual(result["installed"]["revision_short"],"710c240")
        self.assertTrue(result["active_binary"])
        self.assertTrue(result["manual_binary_never_modified"])

    def test_inventory_blocks_absolute_traversal_duplicates_links_and_bombs(self):
        self.assertEqual(mod.verify_inventory(LIST),["simc.exe","profiles"])
        for bad in [LIST.replace("simc.exe","../../outside.exe"),
                    LIST.replace("simc.exe","C:\\pwn\\simc.exe"),
                    LIST.replace("Attributes = A","Attributes = LA"),
                    LIST.replace("Encrypted = -","Encrypted = +"),
                    LIST.replace("Size = 200001","Size = 99999999999"),
                    LIST+"Path = simc.exe\nSize = 22\nAttributes = A\n\n",
                    "not a 7z listing"]:
            with self.subTest(bad=bad[:55]):
                with self.assertRaises(mod.UpdateBlocked):
                    mod.verify_inventory(bad)

    def test_status_read_only_offer_user_consent_install_and_first_rollback(self):
        self.assertFalse((self.path/"managed").exists())
        initial=self.m.status()
        self.assertIsNone(initial["active_binary"])
        self.assertFalse((self.path/"managed").exists())
        with self.assertRaisesRegex(mod.UpdateBlocked,"EXPLICIT_RECENT"):
            self.m.install(NAME,sevenzip="fake")
        self.m.check(INDEX)
        with self.assertRaisesRegex(mod.UpdateBlocked,"EXPLICIT_RECENT"):
            self.m.install("simc-1215-01-win64-badbad0.7z",sevenzip="fake")
        def downloader(url,archive):
            self.assertEqual(url,mod.BASE+NAME)
            archive.write_bytes(mod.MAGIC+b"abcd"*30000)
            return {"sha256":mod.sha256(archive),"bytes":archive.stat().st_size}
        def extractor(archive,stage,sevenzip):
            self.assertEqual(sevenzip,"fake")
            e=stage/"subdir"/"simc.exe";e.parent.mkdir()
            e.write_bytes(b"MZ"+b"SimC"*60000)
            return e
        result=self.m.install(NAME,downloader=downloader,
                              extractor=extractor,sevenzip="fake")
        self.assertEqual(result["status"],"NEW_MANAGED_SIMC_ACTIVATED")
        self.assertEqual(result["installed"]["revision_short"],"710c240")
        exe=pathlib.Path(result["active_binary"])
        self.assertTrue(exe.is_file())
        self.assertTrue(result["can_rollback"])
        self.assertEqual(mod.sha256(exe),result["installed"]["sha256"])
        self.assertEqual(self.m.status()["active_binary"],str(exe))
        self.assertEqual(self.m.rollback()["status"],
                         "MANAGED_SIMC_DEACTIVATED_USE_PREVIOUS_MANUAL_BINARY")
        self.assertIsNone(self.m.status()["active_binary"])
        self.assertTrue(exe.is_file())
        self.assertFalse(self.m.status()["can_rollback"])
        with self.assertRaisesRegex(mod.UpdateBlocked,"NO_MANAGED_SIMC"):
            self.m.rollback()
        self.assertIsNone(self.m.offer)

    def test_second_version_rollback_restores_exact_first_binary(self):
        def install(ver):
            self.m.check(INDEX.replace(NAME,ver))
            def d(url,archive):
                archive.write_bytes(mod.MAGIC+ver.encode()*8000)
                return {"sha256":mod.sha256(archive),"bytes":archive.stat().st_size}
            def x(a,folder,tool):
                exe=folder/"simc.exe";exe.write_bytes(b"MZ"+ver.encode()*14000)
                return exe
            return self.m.install(ver,downloader=d,extractor=x,sevenzip="fake")
        first=install(NAME)
        ver="simc-1215-02-win64-710c241.7z"
        second=install(ver)
        self.assertNotEqual(first["active_binary"],second["active_binary"])
        back=self.m.rollback()
        self.assertEqual(back["active_binary"],first["active_binary"])
        self.assertEqual(back["installed"]["filename"],NAME)
        self.assertTrue(pathlib.Path(second["active_binary"]).is_file())

    def test_failed_download_cannot_replace_existing_pointer_or_files(self):
        self.m.check(INDEX)
        def broken(*args):
            raise mod.UpdateBlocked("NIGHTLY_DOWNLOAD_INTERRUPTED")
        with self.assertRaisesRegex(mod.UpdateBlocked,"INTERRUPTED"):
            self.m.install(NAME,downloader=broken,sevenzip="fake")
        self.assertFalse((self.path/"managed"/"installed.json").exists())

    def test_local_7z_install_explicit_origin_not_authenticated(self):
        f=self.path/NAME
        f.write_bytes(mod.MAGIC+b"x"*150000)
        def extractor(archive,stage,sevenzip):
            exe=stage/"simc.exe"
            exe.write_bytes(b"MZ"+b"portable_fake_pe"*11000)
            return exe
        result=self.m.install_local(str(f),extractor=extractor,sevenzip="mock7z")
        self.assertEqual(result["installed"]["archive_source"],
                         "USER_LOCAL_FILE_ORIGIN_NOT_AUTHENTICATED")
        self.assertFalse(result["installed"]["upstream_signature_verified"])
        self.assertTrue(result["active_binary"])
        # An attacker can't inject remote URLs or arbitrary extensions.
        with self.assertRaisesRegex(mod.UpdateBlocked,
                                    "LOCAL_NIGHTLY_FILE_NOT_FOUND"):
            self.m.install_local(str(self.path/"evil.exe"),sevenzip="mock7z")

    def test_pe64_header_validation_blocks_mz_only_and_untrusted_architecture(self):
        with mock.patch.object(mod.subprocess,"run") as command:
            command.return_value=mock.Mock(returncode=0,stdout=LIST)
            root=self.path/"extract";root.mkdir()
            archive=self.path/"simc.7z";archive.write_bytes(mod.MAGIC)
            def fake_extract(*_args,**_kwargs):
                exe=root/"simc.exe"
                exe.write_bytes(b"MZ"+b"0"*199999)
                return mock.Mock(returncode=0,stdout="")
            command.side_effect=[
                mock.Mock(returncode=0,stdout=LIST),
                mock.Mock(returncode=0,stdout="")
            ]
            # Real archive parsing succeeds but the extracted invalid MZ
            # must fail before install and cannot touch the previous binary.
            (root/"simc.exe").write_bytes(b"MZ"+b"0"*199999)
            with self.assertRaisesRegex(mod.UpdateBlocked,"PE_OFFSET"):
                mod.extract_safe(archive,root,"mock7z")
            self.assertFalse((self.path/"managed").exists())

    @unittest.skipUnless(sys.platform=="win32","Windows actual 7-Zip subprocess required")
    def test_real_windows_7z_roundtrip_synthetic_pe_only(self):
        sevenzip=mod.find_sevenzip()
        if not sevenzip:self.skipTest("7-Zip executable not installed on runner")
        source=self.path/"input";source.mkdir()
        body=bytearray(b"MZ"+hashlib.shake_256(b"simc-v193-safe-test").digest(200000))
        body[0x3c:0x40]=(0x80).to_bytes(4,"little")
        body[0x80:0x86]=b"PE"+bytes((0,0,0x64,0x86))
        (source/"simc.exe").write_bytes(body)
        archive=self.path/NAME
        created=subprocess.run([sevenzip,"a","-t7z",str(archive),"simc.exe"],
               cwd=source,capture_output=True,text=True,timeout=30)
        self.assertEqual(created.returncode,0,created.stderr[-300:])
        result=self.m.install_local(str(archive),sevenzip=sevenzip)
        self.assertTrue(pathlib.Path(result["active_binary"]).is_file())
        self.assertEqual(result["installed"]["archive_source"],
                         "USER_LOCAL_FILE_ORIGIN_NOT_AUTHENTICATED")
        self.assertIsNone(self.m.rollback()["active_binary"])

    def test_linux_platform_install_not_supported(self):
        linux=mod.SimCManager(self.path/"linux",platform="linux")
        self.assertFalse(linux.status()["windows_supported"])
        with self.assertRaisesRegex(mod.UpdateBlocked,"WINDOWS_ONLY"):
            linux.check(INDEX)

if __name__=="__main__": unittest.main()
