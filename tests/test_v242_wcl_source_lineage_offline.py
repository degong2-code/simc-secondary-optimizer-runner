"""A5 WCL authenticated GraphQL source ownership: exact two-response SHA.

Only in-memory synthetic HTTP bytes, real v155/v242/v217 code and stage cache.
No Wago/SimC calls, real HTTP, historical season ID or manual current name.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v155_season_api_probe as probe
import v242_authenticated_season_source_stage as stage


class FakeResponse:
    status=200
    def __init__(self,raw):self.raw=raw
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self,n):return self.raw[:n]


def wire(doc):
    return json.dumps(doc,sort_keys=True,separators=(",",":")).encode("utf8")


class FixedSourceTransport:
    def __init__(self):
        self.calls=[]
        self.wcl_bodies={}
        self.graphql_requests={}
    def __call__(self,request,timeout):
        url=request.full_url
        data=request.data or b""
        self.calls.append((url,timeout))
        if url==probe.BLIZZARD_TOKEN_URL or url==probe.WCL_BASE+"/oauth/token":
            return FakeResponse(wire({"access_token":"SECRET_SHOULD_NOT_BE_LOGGED"}))
        if url.startswith(probe.BLIZZARD_BASE+"/data/wow/"):
            return FakeResponse(wire({"current_season":{"id":840}}))
        if url==probe.WCL_BASE+"/api/v2/client":
            payload=json.loads(data)
            query=payload["query"]
            if "expansions" in query:
                key="expansion_index"
                doc={"data":{"worldData":{"expansions":[
                    {"id":7,"name":"Completely Old Content"},
                    {"id":49,"name":"Arbitrary Future Title"}]}}}
            else:
                key="all_expansion_zones"
                doc={"data":{"worldData":{"zones":[
                    {"id":51,"name":"Old Zone","frozen":True,
                     "expansion":{"id":7},"encounters":[]},
                    {"id":901,"name":"Different Active Zone","frozen":False,
                     "expansion":{"id":49},"encounters":[
                         {"id":11,"name":"Boss of new source",
                          "journalID":2024}]}
                ]}}}
            raw=wire(doc)
            self.wcl_bodies[key]=raw
            self.graphql_requests[key]=data
            return FakeResponse(raw)
        raise AssertionError("UNEXPECTED_NETWORK_SOURCE "+url)


class WCLOriginalSourceLineage(unittest.TestCase):
    def credentials(self):
        return {
            "BLIZZARD_CLIENT_ID":"bl-id",
            "BLIZZARD_CLIENT_SECRET":"bl-private-not-logged",
            "WCL_CLIENT_ID":"wcl-id",
            "WCL_CLIENT_SECRET":"wcl-private-not-logged"}

    def test_v155_wcl_two_exact_request_response_hashes(self):
        fake=FixedSourceTransport()
        c=self.credentials()
        report=probe.run_probe(
            c["BLIZZARD_CLIENT_ID"],c["BLIZZARD_CLIENT_SECRET"],
            c["WCL_CLIENT_ID"],c["WCL_CLIENT_SECRET"],transport=fake)
        info=stage.wcl_source_lineage(report)
        self.assertEqual(len(fake.calls),8) # two OAuth, four Blizzard, two WCL
        self.assertEqual(report["wcl"]["requests"],2)
        self.assertEqual(report["wcl"]["status"],
                         "ZONES_WITH_JOURNAL_IDS_RETURNED")
        self.assertTrue(info["wcl_original_graphql_bodies_verified"])
        self.assertEqual(set(info["queries"]),set(stage.WCL_GRAPHQL_SOURCE_ROLES))
        for key in info["queries"]:
            row=info["queries"][key]
            self.assertEqual(row["response_bytes"],len(fake.wcl_bodies[key]))
            self.assertEqual(row["response_sha256"],
                             hashlib.sha256(fake.wcl_bodies[key]).hexdigest())
            self.assertEqual(row["request_body_sha256"],
                             hashlib.sha256(fake.graphql_requests[key]).hexdigest())
        self.assertEqual(info["zone_candidates"],2)
        self.assertEqual(info["unfrozen_zone_candidates"],1)
        self.assertTrue(info["exact_same_build_db2_join_required"])
        self.assertFalse(info["season_membership_certified_here"])
        self.assertFalse(info["all_items_current_season_approved"])
        self.assertFalse(info["wcl_namespace_equals_db2_expansion_id"])
        self.assertEqual(info["native_calls"],0)
        self.assertEqual(info["additional_graphql_requests"],0)
        text=json.dumps(report)
        for secret in (c["BLIZZARD_CLIENT_SECRET"],
                       c["WCL_CLIENT_SECRET"],"SECRET_SHOULD_NOT_BE_LOGGED"):
            self.assertNotIn(secret,text)

    def test_old_or_partial_receipt_not_claimed_as_two_source_proofs(self):
        report={"wcl":{"requests":2,
                       "status":"ZONES_WITH_JOURNAL_IDS_RETURNED",
                       "zones":[]}}
        self.assertFalse(stage.wcl_source_lineage(report)[
                         "wcl_original_graphql_bodies_verified"])
        report["wcl"]["original_graphql_http_bodies"]={
            "expansion_index":{
                "request_body_sha256":"1"*64,
                "raw_response_sha256":"2"*64,
                "raw_response_bytes":10}}
        missing=stage.wcl_source_lineage(report)
        self.assertFalse(missing["wcl_original_graphql_bodies_verified"])
        self.assertIsNone(missing["queries"]["all_expansion_zones"][
                          "response_sha256"])
        report["wcl"]["original_graphql_http_bodies"][
            "all_expansion_zones"]={
                "request_body_sha256":"g"*64,
                "raw_response_sha256":"3"*64,
                "raw_response_bytes":10}
        self.assertFalse(stage.wcl_source_lineage(report)[
                         "wcl_original_graphql_bodies_verified"])

    def test_v242_seals_and_reuses_exact_same_stage_without_graphql(self):
        fake=FixedSourceTransport()
        c=self.credentials()
        with tempfile.TemporaryDirectory() as tmp:
            first=stage.collect(
                stage_root=tmp,expected_game_build="13.0.0.88888",
                credentials=c,transport=fake)
            self.assertEqual(first["network_calls_by_stage"],8)
            self.assertTrue(first["wcl_source_lineage"][
                            "wcl_original_graphql_bodies_verified"])
            self.assertTrue(first["season_join_ready"])
            self.assertFalse(first["current_season_membership_verified"])
            self.assertEqual(first["native_calls"],0)
            raw=pathlib.Path(first["source_report_path"]).read_bytes()
            self.assertNotIn(b"wcl-private-not-logged",raw)
            self.assertNotIn(b"SECRET_SHOULD_NOT_BE_LOGGED",raw)
            self.assertEqual(len(fake.calls),8)
            with mock.patch.object(stage.probe,"run_probe",
                                   side_effect=AssertionError("NO_REFETCH")):
                second=stage.collect(
                    stage_root=tmp,expected_game_build="13.0.0.88888",
                    credentials=c)
            self.assertEqual(second["network_calls_by_stage"],0)
            self.assertEqual(first["stage"]["receipt_sha256"],
                             second["stage"]["receipt_sha256"])
            self.assertTrue(second["wcl_source_lineage"][
                            "wcl_original_graphql_bodies_verified"])


if __name__=="__main__":
    unittest.main()
