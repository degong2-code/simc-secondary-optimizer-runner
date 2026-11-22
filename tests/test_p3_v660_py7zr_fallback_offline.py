"""v660 Python-managed 7z fallback: no external 7z.exe, no Native DPS."""
import importlib
import pathlib
import sys
import tempfile
import unittest
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v193_simc_local_updater as updater

class Python7zFallback(unittest.TestCase):
    def setUp(self):
        import py7zr
        self.py7zr=py7zr
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root=pathlib.Path(temp.name)
        self.exe=self.root/"simc.exe"
        data=bytearray(b"MZ"+b"x"*140000)
        data[0x3c:0x40]=(128).to_bytes(4,"little")
        data[128:134]=b"PE\x00\x00\x64\x86"
        self.exe.write_bytes(data)
        self.archive=self.root/"simc.7z"
        with py7zr.SevenZipFile(self.archive,"w") as z:
            z.write(self.exe,arcname="simc.exe")

    def test_python_extractor_detected_without_installed_sevenzip(self):
        with mock.patch.object(updater,"find_sevenzip",return_value=None):
            self.assertEqual(updater.find_extractor(),updater.PY7ZR_TOOL)
        out=self.root/"unpacked";out.mkdir()
        result=updater.extract_safe(self.archive,out,updater.PY7ZR_TOOL)
        self.assertEqual(result.read_bytes(),self.exe.read_bytes())
        self.assertEqual(result.parent,out)

    def test_corrupt_archive_fails_closed_before_touching_install(self):
        invalid=self.root/"corrupt.7z"
        invalid.write_bytes(updater.MAGIC+b"invalid"*200)
        dest=self.root/"corrupt_extracted";dest.mkdir()
        with self.assertRaises(updater.UpdateBlocked):
            updater.extract_safe(invalid,dest,updater.PY7ZR_TOOL)
        self.assertFalse((dest/"simc.exe").exists())

    def test_extracted_wrong_windows_arch_is_blocked(self):
        data=bytearray(self.exe.read_bytes())
        data[132:134]=b"\x4c\x01" # Intel x86 instead of x64
        self.exe.write_bytes(data)
        with self.py7zr.SevenZipFile(self.archive,"w") as z:
            z.write(self.exe,arcname="simc.exe")
        dest=self.root/"wrongarch";dest.mkdir()
        with self.assertRaisesRegex(updater.UpdateBlocked,"NOT_AMD64"):
            updater.extract_safe(self.archive,dest,updater.PY7ZR_TOOL)

    def test_duplicate_or_traversal_member_is_rejected(self):
        # A direct unit test for archive path metadata checks avoids trying to
        # manufacture an unsafe 7z using a library that rejects unsafe names.
        class Entry:
            def __init__(self,name):
                self.filename=name;self.is_file=True;self.is_directory=False
                self.is_symlink=False;self.uncompressed=100000
        class Reader:
            def __init__(self,names):
                self.names=names
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def needs_password(self):return False
            def list(self):return [Entry(n) for n in self.names]
            def extract(self,**kwargs):
                raise AssertionError("Unsafe archive must never extract")
        for names,err in [
          (["../outside/simc.exe"],"UNSAFE_ARCHIVE_ENTRY"),
          (["simc.exe","SIMC.EXE"],"DUPLICATE_ARCHIVE_ENTRY"),
          (["C:/simc.exe"],"UNSAFE_ARCHIVE_ENTRY")]:
            with self.subTest(names=names):
                with mock.patch.object(self.py7zr,"SevenZipFile",return_value=Reader(names)):
                    with self.assertRaisesRegex(updater.UpdateBlocked,err):
                        updater.extract_py7zr_safe(self.archive,self.root/"unsafe")
if __name__=="__main__":unittest.main()
