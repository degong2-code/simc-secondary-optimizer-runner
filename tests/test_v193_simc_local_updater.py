"""v193: offline official-nightly checks, safe 7z and management lifecycle."""
import hashlib,json,pathlib,sys,tempfile,time,unittest
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
                     '<a href="http://downloads.simulationcraft.org/nightly/simc-1215-01-win64-710c240.7z">']:
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

    def test_linux_platform_install_not_supported(self):
        linux=mod.SimCManager(self.path/"linux",platform="linux")
        self.assertFalse(linux.status()["windows_supported"])
        with self.assertRaisesRegex(mod.UpdateBlocked,"WINDOWS_ONLY"):
            linux.check(INDEX)

if __name__=="__main__": unittest.main()
