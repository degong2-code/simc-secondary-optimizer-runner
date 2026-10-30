"""v193: offline official-nightly checks, safe 7z and management lifecycle."""
import hashlib,json,pathlib,subprocess,sys,tempfile,time,unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v193_simc_local_updater as mod

NAME="simc-1215-01-win64-710c240.7z"
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
                                    "LOCAL_WIN64_NIGHTLY_ARCHIVE_INVALID"):
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
        body=bytearray(b"MZ"+b"x"*200000)
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
