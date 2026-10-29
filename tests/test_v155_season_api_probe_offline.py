"""Offline contract for opt-in v155 provider probe; no HTTP or secrets."""
import io
import json
from pathlib import Path
import sys
import unittest
from unittest import mock
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v155_season_api_probe as p

class SeasonProbeOffline(unittest.TestCase):
    def test_current_season_not_a_dungeon_rotation(self):
        s=p.summarize_blizzard({"current_season":{"id":16},
                                "seasons":[{"id":16},{"id":15}]})
        self.assertEqual(s["current_season_id"],16)
        self.assertFalse(s["season_rotation_dungeon_ids_verified"])
        self.assertEqual(s["list_sizes"]["seasons"],2)

    def test_wcl_journal_bridge_exact_ids(self):
        exps=p.parse_wcl_expansions({"data":{"worldData":{"expansions":[
            {"id":42,"name":"Midnight"},{"id":41,"name":"Dragonflight"}]}}})
        self.assertEqual(p.select_midnight_expansion(exps),42)
        zones=p.parse_wcl_zones({"data":{"worldData":{"zones":[
            {"id":100,"name":"Example Raid","frozen":False,
             "encounters":[{"id":200,"journalID":300,"name":"Example Boss"}]}
        ]}}})
        self.assertEqual(zones[0]["encounters"][0]
                         ["blizzard_journal_encounter_id"],300)

    def test_transport_restricts_url_and_credentials_never_printed(self):
        with self.assertRaises(p.ProbeBlocked):
            p.request_json("https://example.org/steal",transport=mock.Mock())
        with self.assertRaises(p.ProbeBlocked):
            p.run_probe("id","",transport=mock.Mock())
        with self.assertRaises(p.ProbeBlocked):
            p.run_probe("", "",transport=mock.Mock())
        self.assertNotIn("client_secret",p.summarize_blizzard({}))

    def test_live_probe_fixed_requests_and_missing_wcl_skips(self):
        urls=[]
        class Response:
            status=200
            def __init__(self,payload):
                self.payload=json.dumps(payload).encode("utf8")
            def __enter__(self):return self
            def __exit__(self,*args):return None
            def read(self,n):return self.payload[:n]
        def transport(req,timeout):
            urls.append(req.full_url)
            if req.full_url.endswith("/token"):
                return Response({"access_token":"FAKE_TOKEN_NOT_LOGGED"})
            if "season/index" in req.full_url:
                return Response({"current_season":{"id":1234}})
            return Response({"items":[]})
        report=p.run_probe("id","secret",transport=transport)
        self.assertEqual(report["blizzard"]["requests"],4)
        self.assertEqual(report["wcl"]["requests"],0)
        self.assertEqual(report["blizzard"]["endpoints"]
                         ["keystone_season_index"]["data"]
                         ["current_season_id"],1234)
        self.assertEqual(len(urls),5) # 1 OAuth + 4 data GET
        self.assertFalse(any("secret" in u for u in urls))
        self.assertNotIn("FAKE_TOKEN_NOT_LOGGED",json.dumps(report))
        self.assertEqual(report["native_simc_calls"],0)

    def test_optional_wcl_keeps_small_graphql_scope(self):
        queries=[]
        class Response:
            status=200
            def __init__(self,data):self.raw=json.dumps(data).encode()
            def __enter__(self):return self
            def __exit__(self,*args):return None
            def read(self,n):return self.raw
        def transport(req,timeout):
            if req.full_url.endswith("/token"):
                return Response({"access_token":"FAKE"})
            if req.full_url.endswith("/api/v2/client"):
                body=json.loads(req.data)
                queries.append(body)
                if "expansions" in body["query"]:
                    return Response({"data":{"worldData":{"expansions":[
                        {"id":11,"name":"Midnight"}]}}})
                return Response({"data":{"worldData":{"zones":[
                    {"id":1,"name":"Raid","frozen":False,"encounters":[
                        {"id":2,"name":"Boss","journalID":3}]}]}}})
            return Response({"current_season":{"id":14}})
        result=p.run_probe("bid","bsecret","wid","wsecret",
                           transport=transport)
        self.assertEqual(result["wcl"]["requests"],2)
        self.assertEqual(len(queries),2)
        self.assertEqual(result["wcl"]["midnight_zones"][0]["encounters"][0]
                         ["blizzard_journal_encounter_id"],3)
        self.assertEqual(result["blizzard"]["requests"],4)

if __name__=="__main__":
    unittest.main()
