"""v657 generic SimC updater: multi-archive discovery and source-only provenance.

All checks offline; never compile or execute Native SimC.
"""
import pathlib,sys,tempfile,unittest,urllib.error
from unittest import mock
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v193_simc_local_updater as mod

LIVE={"status":"LIVE_RETAIL_BUILD_SOURCE_OBSERVED","region":"KR",
      "game_build":"12.1.5.70961","source_url":"https://us.version.battle.net/wow/versions",
      "source_sha256":"a"*64}
INDEX='''<a href="simc-1210.01.0d19401-win64.7z">old</a>
<a href="simc-1210.01.9933ffb-win64.7z">match</a>
<a href="simc-1210.01.6924096-win64.7z">also match</a>'''
class GenericDiscovery(unittest.TestCase):
    def setUp(self):
        d=tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        self.manager=mod.SimCManager(pathlib.Path(d.name)/"managed",platform="win32")

    def test_same_series_git_hash_is_not_chronological(self):
        found=mod.candidate_urls(INDEX)
        self.assertEqual([x["revision_short"] for x in found],
                         ["0d19401","9933ffb","6924096"])

    def test_scans_beyond_stale_first_archive_and_offers_matching_file(self):
        seen=[]
        def source(rev):
            seen.append(rev)
            return {"source_revision":rev,
                    "source_build":"12.1.5.70783" if rev=="0d19401" else "12.1.5.70961",
                    "source_headers_checked":3}
        with mock.patch.object(mod,"fetch_index",return_value=INDEX):
            r=self.manager.check_for_retail_compatibility(
                live_loader=lambda region: LIVE,source_loader=source)
        self.assertEqual(seen,["0d19401","9933ffb"])
        self.assertEqual(r["candidate"]["revision_short"],"9933ffb")
        self.assertEqual(self.manager.offer["revision_short"],"9933ffb")
        self.assertEqual(r["retail_compatibility"]["official_candidates_checked"],2)
        self.assertEqual(r["retail_compatibility"]["status"],
                         "SOURCE_BUILD_MATCHED_BINARY_UNVERIFIED")
        self.assertFalse(r["retail_compatibility"]["binary_embedded_build_verified"])

    def test_unverified_first_candidate_does_not_block_valid_next_candidate(self):
        def source(rev):
            if rev=="0d19401":
                raise urllib.error.URLError("temporary failure")
            return {"source_revision":rev,"source_build":"12.1.5.70961",
                    "source_headers_checked":3}
        with mock.patch.object(mod,"fetch_index",return_value=INDEX):
            r=self.manager.check_for_retail_compatibility(
                live_loader=lambda region: LIVE,source_loader=source)
        self.assertEqual(r["candidate"]["revision_short"],"9933ffb")

    def test_all_stale_fails_closed_even_with_multiple_archives(self):
        def source(rev):
            return {"source_revision":rev,"source_build":"12.1.5.70783",
                    "source_headers_checked":3}
        with mock.patch.object(mod,"fetch_index",return_value=INDEX):
            r=self.manager.check_for_retail_compatibility(
                live_loader=lambda region: LIVE,source_loader=source)
        self.assertEqual(r["retail_compatibility"]["status"],"SIMC_SOURCE_BUILD_MISMATCH")
        self.assertEqual(r["retail_compatibility"]["official_candidates_checked"],3)
        self.assertIsNone(r["candidate"])
        self.assertIsNone(self.manager.offer)

    def test_source_head_without_binary_is_never_installable(self):
        sha="9933ffb946fb55b1fa66657b848f519ac19006e1"
        with mock.patch.object(mod,"fetch_index",return_value=""):
            r=self.manager.check_for_retail_compatibility(
                live_loader=lambda region: LIVE,
                source_loader=lambda rev: {"source_revision":rev,
                          "source_build":"12.1.5.70961","source_headers_checked":3},
                head_loader=lambda: sha)
        comp=r["retail_compatibility"]
        self.assertEqual(comp["status"],"MATCHING_SOURCE_REQUIRES_BUILD")
        self.assertEqual(comp["source_only_candidate"]["revision_full"],sha)
        self.assertFalse(comp["source_only_candidate"]["downloadable_binary_verified"])
        self.assertFalse(r["direct_install_available"])
        self.assertIsNone(r["matching_download_url"])
        self.assertIsNone(self.manager.offer)

    def test_fast_prefilter_reduces_header_calls_and_caches_revision(self):
        with mock.patch.object(mod,"quick_source_build",return_value="12.1.5.70783") as fast, \
             mock.patch.object(mod,"generated_source_build") as full:
            result=self.manager._candidate_source_proof("0d19401","12.1.5.70961")
            self.assertEqual(result["source_headers_checked"],0)
            self.manager._candidate_source_proof("0d19401","12.1.5.70961")
        fast.assert_called_once()
        full.assert_not_called()

    def test_matching_prefilter_requires_three_generated_headers(self):
        with mock.patch.object(mod,"quick_source_build",return_value="12.1.5.70961"), \
             mock.patch.object(mod,"generated_source_build",return_value={
                    "source_revision":"9933ffb","source_build":"12.1.5.70961",
                    "source_headers_checked":3}) as three:
            result=self.manager._candidate_source_proof("9933ffb","12.1.5.70961")
            self.assertEqual(result["source_headers_checked"],3)
        three.assert_called_once()

    def test_quick_source_and_official_head_redirects_fail_closed(self):
        class Fake:
            status=200
            def __init__(self,url,body):self.url=url;self.body=body
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def geturl(self):return self.url
            def read(self,n):return self.body[:n]
        s="9933ffb"
        request_url=mod.SOURCE_BASE+s+"/engine/dbc/generated/client_data_version.inc"
        correct=b'#define CLIENT_DATA_WOW_VERSION "12.1.5.70961"\n'
        ok=lambda request,timeout: Fake(request.full_url,correct)
        self.assertEqual(mod.quick_source_build(s,open_url=ok),"12.1.5.70961")
        bad=lambda request,timeout: Fake("https://evil.example/mirror",correct)
        with self.assertRaisesRegex(mod.UpdateBlocked,"SIMC_SOURCE_REDIRECT"):
            mod.quick_source_build(s,open_url=bad)
        json_bytes=(b'{"ref":"refs/heads/midnight","object":{"type":"commit",'
                    b'"sha":"9933ffb946fb55b1fa66657b848f519ac19006e1"}}')
        self.assertEqual(mod.official_source_head_revision(open_url=lambda request,timeout:
                         Fake(request.full_url,json_bytes)),
                         "9933ffb946fb55b1fa66657b848f519ac19006e1")
        with self.assertRaisesRegex(mod.UpdateBlocked,"SIMC_HEAD_SOURCE_UNVERIFIED"):
            mod.official_source_head_revision(open_url=lambda request,timeout:
                        Fake("https://evil.example",json_bytes))

    def test_concurrent_older_check_cannot_reoffer_stale_candidate(self):
        first="0d19401"
        calls=0
        def source(rev):
            nonlocal calls
            calls+=1
            if calls==1:
                with mock.patch.object(mod,"fetch_index",return_value=""):
                    newer=self.manager.check_for_retail_compatibility(
                        live_loader=lambda region: LIVE,
                        source_loader=lambda r: {"source_revision":r,
                            "source_build":"12.1.5.70961","source_headers_checked":3})
                self.assertIsNone(newer["candidate"])
            return {"source_revision":rev,"source_build":"12.1.5.70961",
                    "source_headers_checked":3}
        with mock.patch.object(mod,"fetch_index",return_value=INDEX):
            older=self.manager.check_for_retail_compatibility(
                live_loader=lambda region: LIVE,source_loader=source)
        self.assertEqual(older["retail_compatibility"]["status"],
                         "SIMC_UPDATE_CHECK_SUPERSEDED")
        self.assertIsNone(older["candidate"])
        self.assertIsNone(self.manager.offer)

if __name__=="__main__":unittest.main()
