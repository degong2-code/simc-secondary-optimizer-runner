"""v193: existing loopback security applies to updater, zero Native or HTTP."""
import pathlib,sys,tempfile,unittest
from unittest import mock
from fastapi.testclient import TestClient
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v113_local_web_api as web
import v193_simc_local_updater as update
class SimCUpdateWeb(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        self.app=web.create_app(root=self.root/"runs",token="v193-local-token",
                               update_root=self.root/"managed",
                               update_platform="win32")
        self.client=TestClient(self.app,base_url="http://127.0.0.1:8765")
        self.h={"x-simc-local-token":"v193-local-token",
                "origin":"http://127.0.0.1:8765"}
    def test_status_no_network_no_files_and_routes_auth(self):
        with mock.patch.object(update,"fetch_index",
            side_effect=AssertionError("MUST_NOT_FETCH_WHILE_STATUS")):
            self.assertEqual(self.client.get("/api/v1/simc-updates/status").status_code,403)
            resp=self.client.get("/api/v1/simc-updates/status",headers=self.h)
            self.assertEqual(resp.status_code,200,resp.text)
            self.assertIsNone(resp.json()["active_binary"])
        self.assertFalse((self.root/"managed").exists())
        self.assertEqual(self.client.post("/api/v1/simc-updates/check",
                         json={},headers=self.h|{"origin":"http://evil.test"}).status_code,403)
        self.assertEqual(self.client.post("/api/v1/simc-updates/install",
                         json={"filename":"x"},headers=self.h).status_code,422)
        self.assertEqual(self.client.post("/api/v1/simc-updates/rollback",
                         json={},headers=self.h).status_code,422)
    def test_explicit_post_check_install_no_autodownload_and_same_offer(self):
        html='<a href="simc-1215-01-win64-710c240.7z">Official</a>'
        with mock.patch.object(update,"fetch_index",return_value=html):
            status=self.client.post("/api/v1/simc-updates/check",
                                    json={},headers=self.h)
        self.assertEqual(status.status_code,200,status.text)
        self.assertTrue(status.json()["installation_requires_confirmation"])
        self.assertEqual(status.json()["candidate"]["revision_short"],"710c240")
        response=self.client.post("/api/v1/simc-updates/install",
                      json={"filename":"simc-1215-02-win64-710c241.7z"},headers=self.h)
        self.assertEqual(response.status_code,422,response.text)
        self.assertEqual(response.json()["detail"]["code"],
                         "EXPLICIT_RECENT_OFFICIAL_OFFER_REQUIRED")
        self.assertFalse((self.root/"managed"/"installed.json").exists())
    def test_local_install_endpoint_is_token_gated_and_bad_path_fails_closed(self):
        path="/api/v1/simc-updates/install-local"
        data={"archive_path":str(self.root/"not-official.zip")}
        self.assertEqual(self.client.post(path,json=data).status_code,403)
        res=self.client.post(path,json=data,headers=self.h)
        self.assertEqual(res.status_code,422,res.text)
        self.assertEqual(res.json()["detail"]["code"],
                         "LOCAL_WIN64_NIGHTLY_ARCHIVE_INVALID")
        self.assertFalse((self.root/"managed").exists())

    def test_native_worker_running_blocks_manage_actions(self):
        fake=mock.Mock();fake.poll.return_value=None
        self.app.state.jobs.children["a"*20]=fake
        for route in ("status","check"):
            method="get" if route=="status" else "post"
            response=getattr(self.client,method)("/api/v1/simc-updates/"+route,
                     headers=self.h,**({} if method=="get" else {"json":{}}))
            self.assertEqual(response.status_code,409,response.text)
            self.assertEqual(response.json()["detail"]["code"],
                             "ACTIVE_SIMC_JOB_UPDATE_BLOCKED")
if __name__=="__main__":unittest.main()
