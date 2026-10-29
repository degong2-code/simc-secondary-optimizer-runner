"""API-only small Delve REST probe; never loads legacy item IDs."""
import json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v159_blizzard_delve_rest_probe as probe

class DelveSourceFirstOffline(unittest.TestCase):
    def test_journal_index_is_not_a_delve_season_list(self):
        result,_=probe.summarize_index({"instances":[
            {"id":123,"name":"An ordinary dungeon"},
            {"id":222,"name":"Test Delve","type":"delve"}]})
        self.assertEqual(result["total_journal_instances"],2)
        self.assertEqual(result["delve_explicitly_labeled_count"],1)
        self.assertEqual(result["delve_explicitly_labeled_rows"][0]["id"],222)

    def test_no_labeled_delves_never_implies_empty_loot(self):
        s,_=probe.summarize_index({"instances":[{"id":333,
                    "name":"Unknown category instance"}]})
        self.assertEqual(s["delve_explicitly_labeled_count"],0)
        self.assertTrue(s["unlabeled_delves_excluded_from_diagnosis"])

    def test_bounded_probe_continues_on_unknown_rest_routes(self):
        from urllib.error import HTTPError
        class Response:
            status=200
            def __init__(self,d):self.raw=json.dumps(d).encode()
            def __enter__(self):return self
            def __exit__(self,*a):pass
            def read(self,n):return self.raw[:n]
        calls=[]
        def transport(req,timeout):
            calls.append(req.full_url)
            if req.full_url.endswith("/token"):
                return Response({"access_token":"DUMMY_NOT_EMITTED"})
            if "/journal-instance/index?" in req.full_url:
                return Response({"instances":[{"id":33,"name":"Season Delve",
                                                "type":"Delve"}]})
            if "/journal-instance/33?" in req.full_url:
                return Response({"id":33,"encounters":[]})
            if "/delve/" in req.full_url:
                raise HTTPError(req.full_url,404,"not found",None,None)
            raise AssertionError("Unexpected test URL")
        result=probe.run_probe("id","secret",transport=transport)
        self.assertEqual(result["blizzard_game_data_requests"],4)
        self.assertEqual(len(calls),5)
        self.assertEqual(result["api_route_results"]
                         ["candidate_delve_index"]["error_code"],"HTTP_404")
        self.assertEqual(result["one_journal_detail"]["encounter_count"],0)
        self.assertEqual(result["item_ids_discovered"],[])
        self.assertFalse(result["delve_loot_pool_identified"])
        self.assertTrue(result["no_previous_item_db_used"])
        self.assertNotIn("DUMMY_NOT_EMITTED",json.dumps(result))

if __name__=="__main__":
    unittest.main()
