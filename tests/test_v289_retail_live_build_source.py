"""Offline contract for dynamic Blizzard Retail version identity.

Does not fetch the public endpoint or assert that a test version is live.
"""
import pathlib
import sys
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v289_retail_live_build_source as source

RAW=(b"Region|BuildConfig|CDNConfig|KeyRing|BuildId|VersionsName|ProductConfig\n"
     b"US|a|b|c|70783|12.1.5.70783|d\n"
     b"KR|a|b|c|70783|12.1.5.70783|d\n"
     b"EU|a|b|c|70783|12.1.5.70783|d\n")

# The actual official CDN format is typed BPSV, lower-case region and
# a sequencing comment. These bytes are a fixture, NOT a future live default.
BPSV=(b"Region!STRING:0|BuildConfig!HEX:16|CDNConfig!HEX:16|"
      b"KeyRing!HEX:16|BuildId!DEC:4|VersionsName!String:0|"
      b"ProductConfig!HEX:16\n"
      b"## seqn = 4117315\n"
      b"us|a|b|c|70783|12.1.5.70783|d\n"
      b"kr|a|b|c|70783|12.1.5.70783|d\n"
      b"eu|a|b|c|70783|12.1.5.70783|d\n")

class Response:
    status=200
    def __init__(self,data):self.data=data
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self,n):return self.data[:n]

class RetailBuildDiscovery(unittest.TestCase):
    def test_kr_retail_from_official_versions_without_old_seed(self):
        found=source.parse(RAW)
        self.assertEqual(found["game_build"],"12.1.5.70783")
        self.assertEqual(found["region"],"KR")
        self.assertEqual(found["product"],"wow")
        self.assertFalse(found["environment_ready"])
        self.assertFalse(found["simc_binary_matched"])
        self.assertEqual(len(found["source_sha256"]),64)
        typed=source.parse(BPSV)
        self.assertEqual(typed["game_build"],found["game_build"])
        self.assertEqual(typed["region"],"KR")
        self.assertNotEqual(typed["source_sha256"],found["source_sha256"])
        got=source.discover(
            fetch=lambda req,timeout:Response(RAW))
        self.assertEqual(got,found)
    def test_generic_new_build_version_and_kr_region_are_source_driven(self):
        """A2: changing a season/build must not require a new source code ID."""
        # This synthetic alternative deliberately differs from the actual
        # current 70783 evidence; the KR row alone sets the build.
        other=BPSV.replace(
            b"kr|a|b|c|70783|12.1.5.70783|d",
            b"kr|a|b|c|88888|13.0.0.88888|d")
        self.assertNotEqual(other,BPSV)
        found=source.parse(other,region="KR")
        self.assertEqual(found["game_build"],"13.0.0.88888")
        self.assertEqual(found["region"],"KR")
        self.assertEqual(source.parse(other,region="US")["game_build"],
                         "12.1.5.70783")
        self.assertNotEqual(found["source_sha256"],
                            source.parse(BPSV)["source_sha256"])
        mismatch=other.replace(
            b"kr|a|b|c|88888|13.0.0.88888|d",
            b"kr|a|b|c|70783|13.0.0.88888|d")
        with self.assertRaisesRegex(
                source.RetailVersionBlocked,"BUILD_ID_MISMATCH"):
            source.parse(mismatch,region="KR")

    def test_fails_closed_on_absent_or_inconsistent_live_source(self):
        for payload in (
            RAW.replace(b"KR|",b"XX|"),
            RAW.replace(b"KR|a|b|c|70783",b"KR|a|b|c|70784"),
            RAW+RAW.splitlines(2)[2]+b"\n",
            b"<!DOCTYPE html><p>error</p>",
            b"x"*(source.MAX_RESPONSE+1),
            b"",
        ):
            with self.subTest(sample=payload[:20]):
                with self.assertRaises(source.RetailVersionBlocked):
                    source.parse(payload)
        with self.assertRaisesRegex(
                source.RetailVersionBlocked,"REGION_UNSUPPORTED"):
            source.discover(region="PTR",fetch=lambda req,timeout:Response(RAW))
        with self.assertRaisesRegex(
                source.RetailVersionBlocked,"LIVE_SOURCE_UNAVAILABLE"):
            source.discover(fetch=mock.Mock(side_effect=OSError("offline")))
    def test_malformed_http_is_never_a_previous_season_fallback(self):
        class BadResponse(Response):
            status=404
        with self.assertRaisesRegex(
                source.RetailVersionBlocked,"HTTP_STATUS_NOT_SUCCESS"):
            source.discover(fetch=lambda req,timeout:BadResponse(RAW))

if __name__=="__main__":
    unittest.main()
