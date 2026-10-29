"""P1 Windows one-click local web launcher; no subprocess/Native server."""
import pathlib
import sys
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v113_local_web_api as web

class WindowsLocalWebLauncherOffline(unittest.TestCase):
    def test_batch_has_readonly_adjacent_and_home_discovery_and_dependency_help(self):
        text=(ROOT/"START_SIMC_OPTIMIZER_WEB_WINDOWS.cmd").read_text(
            encoding="utf8")
        self.assertIn("..\\v147_batch",text)
        self.assertIn("%USERPROFILE%\\SIMC_Secondary_Optimizer\\v147_batch",text)
        self.assertIn("VIEW-ONLY",text)
        self.assertIn("where py",text)
        self.assertIn("where python",text)
        self.assertIn("requirements-web.txt",text)
        self.assertIn('"--check"',text)
        self.assertIn("--open-browser",text)
        self.assertIn('"%BATCH_ROOT%"',text)
        self.assertIn("Ctrl+C",text)
        self.assertNotIn("RUN_ALL_24",text)
        self.assertNotIn("--execute",text)
        self.assertNotIn("--max-new-physical",text)
        self.assertNotIn("git pull",text)
        self.assertNotIn("pip install -r requirements-web.txt\n",text)

    def test_original_cli_without_open_browser_keeps_original_uvicorn_entry(self):
        with mock.patch.object(web,"create_app",return_value="local_app") as make, \\
             mock.patch("uvicorn.run") as run, \\
             mock.patch("uvicorn.Server") as server, \\
             mock.patch.object(web.threading,"Thread") as thread:
            web.main(["--port","8766"])
            make.assert_called_once_with(batch_root=None)
            run.assert_called_once_with("local_app",
                host="127.0.0.1",port=8766,
                proxy_headers=False,access_log=False)
            server.assert_not_called()
            thread.assert_not_called()

    def test_browser_only_opens_for_own_server_after_started(self):
        with mock.patch.object(web,"create_app",return_value="local_app") as make, \\
             mock.patch("uvicorn.Server") as klass, \\
             mock.patch("uvicorn.Config") as config, \\
             mock.patch("uvicorn.run") as old_run, \\
             mock.patch.object(web.threading,"Thread") as thread, \\
             mock.patch("webbrowser.open") as browse:
            srv=klass.return_value
            srv.started=False
            srv.should_exit=True
            web.main(["--port","8767","--open-browser",
                      "--batch-root",r"C:\\Portable\\v147_batch"])
            old_run.assert_not_called()
            make.assert_called_once()
            self.assertTrue(str(make.call_args.kwargs["batch_root"]).endswith(
                "v147_batch"))
            config.assert_called_once_with("local_app",host="127.0.0.1",
                port=8767,proxy_headers=False,access_log=False)
            srv.run.assert_called_once_with()
            thread.assert_called_once()
            self.assertTrue(thread.call_args.kwargs["daemon"])
            cb=thread.call_args.kwargs["target"]
            # Port might be occupied by a DIFFERENT server; do not open it.
            cb()
            browse.assert_not_called()
            # Only THIS server's confirmed started state opens a browser.
            srv.started=True
            srv.should_exit=False
            cb()
            browse.assert_called_once_with("http://127.0.0.1:8767/",new=2)

    def test_non_loopback_host_and_low_ports_remain_blocked(self):
        with self.assertRaises(SystemExit):
            web.main(["--host","0.0.0.0","--open-browser"])
        with self.assertRaises(SystemExit):
            web.main(["--port","80","--open-browser"])

if __name__=="__main__":unittest.main()
