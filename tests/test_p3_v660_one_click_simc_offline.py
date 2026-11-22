"""v660 generic one-click SimC update, clean-cache/local/official/release offline.

No downloader or GitHub token is required for unit tests. Native SimC DPS = 0.
"""
import hashlib
import io
import json
import pathlib
import shutil
import sys
import tempfile
import unittest
import zipfile
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v193_simc_local_updater as updater
import v660_simc_one_click_provision as provision

REV="6924096820c0b5c9d7bfa9848ea48fe0cd15c7d7"
LIVE="12.1.5.70961"
LIVE_RESULT={"status":"LIVE_RETAIL_BUILD_SOURCE_OBSERVED","region":"KR",
             "game_build":LIVE,"source_url":"https://us.version.battle.net/wow/versions",
             "source_sha256":"c"*64}
URL="https://github.com/"+provision.REPO+"/releases/download/simc-cli-source-"+REV+"/simc-win64-cli-"+REV[:7]+"-"+LIVE+".zip"

def sha(raw): return hashlib.sha256(raw).hexdigest()
class FakeManager:
    platform="win32"
    def __init__(self):
        self.active=None
        self.installed=None
        self.checks=0
        self.installs=0
        self.selected_sevenzip=None
    def status(self):
        return {"active_binary":self.active,"installed":self.installed}
    def check_for_retail_compatibility(self,**kwargs):
        self.checks+=1
        return {"candidate":None,
                "retail_compatibility":{
                    "status":"MATCHING_SOURCE_REQUIRES_BUILD",
                    "source_only_candidate":{
                        "revision_full":REV,"source_build":LIVE,
                        "source_headers_checked":3,
                        "downloadable_binary_verified":False}}}
    def _candidate_source_proof(self,revision,target,source_loader=None):
        return {"source_revision":revision,"source_build":target,
                "source_headers_checked":3}
    def install_self_built(self,path,sevenzip=None,probe=None):
        self.installs+=1
        self.selected_sevenzip=sevenzip
        from v659_simc_self_built_artifact import inspect_artifact
        info=inspect_artifact(path)
        assert info["source_sha"]==REV and info["game_build"]==LIVE
        return {"active_binary":"C:/managed/simc.exe",
                "installed":{"revision_short":REV[:7],
                             "source_game_build":LIVE,
                             "source_revision_full":REV}}

class AutoProvision(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.root=pathlib.Path(temp.name)
        self.manager=FakeManager()
        self.live=lambda region: LIVE_RESULT
        payload={
          "schema":"p3_v658_windows_cli_build_receipt_v1",
          "origin":"SELF_BUILT_UPSTREAM_SIMC_NOT_OFFICIAL_BINARY",
          "source_repo":"simulationcraft/simc",
          "source_sha":REV,"source_game_build":LIVE,
          "archive_name":"simc-1210.01."+REV[:7]+"-win64.7z",
          "cli_sha256":"a"*64,"cli_bytes":132000,
          "cli_smoke":"PASS","binary_embedded_build_verified":True,
          "observed_game_build":LIVE,"official_release":False,
          "season_environment_ready":False,"native_dps_calls":0}
        inner=updater.MAGIC+hashlib.shake_256(b"v660-release-archive").digest(140000)
        payload["archive_sha256"]=sha(inner)
        payload["archive_bytes"]=len(inner)
        proof={"schema":"p3_v658_source_proof_v1","source_sha":REV,
               "game_build":LIVE,"source_headers_checked":4,
               "series":"1210.01","source_verified":True,
               "binary_verified":False,"environment_ready":False}
        self.example=self.root/"build.zip"
        with zipfile.ZipFile(self.example,"w",zipfile.ZIP_DEFLATED) as z:
            z.writestr("build_receipt.json",json.dumps(payload))
            z.writestr("source_proof.json",json.dumps(proof))
            z.writestr("display_build.txt",
                       "SimulationCraft 1210-01 for World of Warcraft "+LIVE+" Live")
            z.writestr(payload["archive_name"],inner)
        self.blob=self.example.read_bytes()
        self.asset={
            "name":"simc-win64-cli-"+REV[:7]+"-"+LIVE+".zip",
            "browser_download_url":URL,
            "digest":"sha256:"+sha(self.blob),
            "size":len(self.blob),"state":"uploaded","id":123}
        self.release={"tag_name":"simc-cli-source-"+REV,
                      "draft":False,"prerelease":True,"assets":[self.asset]}

    def test_published_cache_matching_source_sha_and_build(self):
        a=provision.published_candidates(LIVE,
                       release_loader=lambda url:[self.release])
        self.assertEqual(len(a),1)
        self.assertEqual(a[0]["source_sha"],REV)
        self.assertEqual(a[0]["artifact_sha256"],sha(self.blob))
        self.assertEqual(a[0]["archive_url"],URL)

    def test_untrusted_urls_digests_and_drafts_are_not_candidates(self):
        for field,value in [
          ("digest","sha256:bad"),("browser_download_url","http://example.com/evil"),
          ("size",-1),("state","pending"),("name","bad.zip")]:
            with self.subTest(field=field):
                asset=dict(self.asset);asset[field]=value
                release=dict(self.release);release["assets"]=[asset]
                self.assertEqual(provision.published_candidates(
                    LIVE,release_loader=lambda url:[release]),[])
        draft=dict(self.release);draft["draft"]=True
        self.assertEqual(provision.published_candidates(
            LIVE,release_loader=lambda url:[draft]),[])
        self.assertEqual(provision.published_candidates(
            "12.1.5.70783",release_loader=lambda url:[self.release]),[])

    def test_download_exact_digest_and_refuse_modified_public_bytes(self):
        candidate=provision.published_candidates(LIVE,
            release_loader=lambda url:[self.release])[0]
        class Response:
            status=200
            def __init__(self,body,url):
                self.body=io.BytesIO(body);self.url=url
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def geturl(self):return self.url
            def read(self,n):return self.body.read(n)
        output=self.root/"download.zip"
        fn=lambda request,timeout:Response(self.blob,URL)
        self.assertEqual(provision.download_release_zip(candidate,output,
                            open_url_override=fn),str(output))
        self.assertEqual(output.read_bytes(),self.blob)
        bad=lambda request,timeout:Response(self.blob+b"corrupted",URL)
        with self.assertRaisesRegex(provision.ProvisionBlocked,"DIGEST_MISMATCH"):
            provision.download_release_zip(candidate,output,
                                           open_url_override=bad)
        redirected=lambda request,timeout:Response(self.blob,"http://127.0.0.1/internal")
        with self.assertRaisesRegex(provision.ProvisionBlocked,"URL_UNTRUSTED"):
            provision.download_release_zip(candidate,output,
                                           open_url_override=redirected)

    def test_cached_managed_binary_reuse_does_not_discover_or_download(self):
        self.manager.active="C:/managed/simc.exe"
        self.manager.installed={"source_game_build":LIVE,
                                "source_revision_full":REV}
        calls=[]
        def checked(binary,*,expected_build):
            calls.append((binary,expected_build))
            return True
        result=provision.prepare_one_click(self.manager,
                live_loader=self.live,cli_probe=checked,
                release_loader=lambda url:self.fail("cached binary should be reused"))
        self.assertEqual(result["status"],"ALREADY_COMPATIBLE_MANAGED")
        self.assertEqual(calls,[("C:/managed/simc.exe",LIVE)])
        self.assertEqual(self.manager.checks,0)

    def test_official_candidate_download_uses_embedded_live_build_check(self):
        class Official(FakeManager):
            def check_for_retail_compatibility(self,**kw):
                return {"retail_compatibility":{
                        "status":"SOURCE_BUILD_MATCHED_BINARY_UNVERIFIED"},
                        "candidate":{"filename":"simc-1210.01.6924096-win64.7z"}}
            def install(self,filename,*,sevenzip=None,probe=None):
                self.installs+=1
                probe("C:/managed/simc.exe")
                return {"installed":{"revision_short":REV[:7]},
                        "active_binary":"C:/managed/simc.exe"}
        tested=[]
        result=provision.prepare_one_click(Official(),live_loader=self.live,
              cli_probe=lambda binary,*,expected_build:tested.append(expected_build))
        self.assertEqual(result["status"],"OFFICIAL_BINARY_INSTALLED")
        self.assertEqual(tested,[LIVE])

    def test_public_release_auto_install_and_no_compilation(self):
        def downloaded(candidate,output):
            shutil.copy2(self.example,output)
            return str(output)
        result=provision.prepare_one_click(self.manager,live_loader=self.live,
          release_loader=lambda url:[self.release],
          archive_loader=downloaded)
        self.assertEqual(result["status"],"PUBLIC_SELF_BUILT_BINARY_INSTALLED")
        self.assertEqual(result["installed"]["source_revision_full"],REV)
        self.assertEqual(self.manager.installs,1)
        self.assertFalse(result["new_compilation"])
        self.assertEqual(result["native_dps_calls_now"],0)

    def test_auto_install_prefers_bounded_python_extractor_over_detected_external_7z(self):
        def downloaded(candidate,output):
            shutil.copy2(self.example,output)
            return str(output)
        # Reproduce a Windows machine with 7z.exe available, without using it.
        with mock.patch.object(updater,'find_sevenzip',return_value='C:/7-Zip/7z.exe'), \
             mock.patch.object(provision.importlib.util,'find_spec',return_value=object()):
            result=provision.prepare_one_click(self.manager,live_loader=self.live,
                release_loader=lambda url:[self.release],archive_loader=downloaded)
        self.assertEqual(result['status'],'PUBLIC_SELF_BUILT_BINARY_INSTALLED')
        self.assertEqual(self.manager.selected_sevenzip,updater.PY7ZR_TOOL)
        self.assertEqual(self.manager.installs,1)

    def test_auto_install_preserves_explicit_extractor_override(self):
        def downloaded(candidate,output):
            shutil.copy2(self.example,output)
            return str(output)
        with mock.patch.object(provision.importlib.util,'find_spec',return_value=object()):
            result=provision.prepare_one_click(self.manager,live_loader=self.live,
                release_loader=lambda url:[self.release],archive_loader=downloaded,
                sevenzip='C:/7-Zip/7z.exe')
        self.assertEqual(result['status'],'PUBLIC_SELF_BUILT_BINARY_INSTALLED')
        self.assertEqual(self.manager.selected_sevenzip,'C:/7-Zip/7z.exe')
    def test_release_unavailable_report_remote_service_missing_without_key(self):
        result=provision.prepare_one_click(self.manager,live_loader=self.live,
                release_loader=lambda url:[])
        self.assertEqual(result["status"],"SOURCE_BUILD_REQUIRES_REMOTE_BUILDER")
        self.assertFalse(result["server_build_trigger_available"])
        self.assertEqual(result["reason"],"NO_ANONYMOUS_GITHUB_ACTIONS_DISPATCH")
        self.assertEqual(self.manager.installs,0)

    def test_wrong_source_proof_never_installs_release(self):
        self.manager._candidate_source_proof=lambda *a,**k:{
           "source_revision":REV,"source_build":"12.1.5.70783",
           "source_headers_checked":3}
        result=provision.prepare_one_click(self.manager,live_loader=self.live,
                release_loader=lambda url:[self.release],
                archive_loader=lambda *a: self.fail("stale source should not download"))
        self.assertEqual(result["status"],"SOURCE_BUILD_REQUIRES_REMOTE_BUILDER")
        self.assertEqual(self.manager.installs,0)

    def test_local_authenticated_api_and_ui_implement_single_action(self):
        api=(ROOT/"runner/v113_local_web_api.py").read_text("utf8")
        ui=(ROOT/"runner/webui/app.js").read_text("utf8")
        html=(ROOT/"runner/webui/index.html").read_text("utf8")
        self.assertIn('/api/v1/simc-updates/prepare-auto',api)
        self.assertIn("simc_one_click.prepare_one_click(updater)",api)
        self.assertIn('/api/v1/simc-updates/prepare-auto',ui)
        self.assertIn('id="simc-auto-prepare-btn"',html)
        self.assertNotIn("workflow_dispatch",ui[ui.index("async function autoPrepareSimc()"):
                                              ui.index("async function checkSimcUpdater()")])

if __name__=="__main__":unittest.main()
