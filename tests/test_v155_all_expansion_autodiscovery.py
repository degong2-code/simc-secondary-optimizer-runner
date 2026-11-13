"""A1: WCL source-driven expansion candidate discovery, zero seed, zero Native.

Contract tests: only the existing v155 bounded API adapter is called; there
is NO new season/expansion name/ID seed, network access or installation.
"""
from __future__ import annotations

import pathlib
import sys
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v155_season_api_probe as probe


def zone(zone_id, name, expansion_id, encounters, *, frozen=False):
    return {"id":zone_id, "name":name, "frozen":frozen,
            "expansion":{"id":expansion_id},
            "encounters":[{"id":x+1000,"name":name, "journalID":x}
                          for x,name in encounters]}


class AllExpansionSourceTests(unittest.TestCase):
    def test_source_zone_parser_keeps_expansion_provenance(self):
        raw={"data":{"worldData":{"zones":[
            zone(101,"Unrelated Historical",10,[(1,"Old Boss")],frozen=True),
            zone(901,"Future Name Without Runtime Seed",47,
                 [(102,"New Boss")])]}}}
        rows=probe.parse_wcl_zones(raw,require_expansion=True)
        self.assertEqual([x["expansion_id"] for x in rows],[10,47])
        self.assertEqual(rows[1]["zone_name"],
                         "Future Name Without Runtime Seed")
        self.assertEqual(rows[1]["encounters"][0][
                         "blizzard_journal_encounter_id"],102)
        for bad in (
            {"data":{"worldData":{"zones":[
                {"id":901,"name":"No Expansion","frozen":False,
                 "encounters":[]}]}}},
            {"data":{"worldData":{"zones":[
                zone(4,"One",47,[]),zone(4,"Duplicated",47,[])]}}},
            {"data":{"worldData":{"zones":[
                zone(4,"Zero Expansion",0,[])]}}}
        ):
            with self.subTest(bad=bad),self.assertRaises(probe.ProbeBlocked):
                probe.parse_wcl_zones(bad,require_expansion=True)

    def test_unrelated_old_zone_optional_metadata_does_not_block_scope(self):
        """All-expansion discovery cannot require unused historical fields."""
        old=zone(101,"Historical Zone",7,[(1,"Old Boss")])
        old["frozen"]=None
        old["encounters"][0]["journalID"]=None
        current=zone(401,"New Current Zone",41,[(77,"New Boss")])
        raw={"data":{"worldData":{"zones":[old,current]}}}
        parsed=probe.parse_wcl_zones(raw,require_expansion=True)
        self.assertIsNone(parsed[0]["wcl_frozen"])
        self.assertIsNone(parsed[0]["encounters"][0][
                          "blizzard_journal_encounter_id"])
        self.assertFalse(parsed[0]["journal_id_fields_complete"])
        self.assertTrue(parsed[1]["journal_id_fields_complete"])
        self.assertEqual(parsed[1]["expansion_id"],41)
        # Unknown frozen does not count as a proven active zone; v163
        # already uses identity comparison, never a fallback to active.
        self.assertEqual([x["zone_id"] for x in parsed
                          if x["wcl_frozen"] is False],[401])
        # Real authenticated v389 all-expansion source had a signed
        # Journal ID sentinel: source schema Int is not guaranteed
        # to be a positive valid Blizzard encounter ID in old zones.
        for sentinel in (0,-1):
            historical=zone(88,"Irrelevant Historical",7,
                            [(12,"Historical Encounter")],frozen=True)
            historical["encounters"][0]["journalID"]=sentinel
            rows=probe.parse_wcl_zones({"data":{"worldData":{
                "zones":[historical,current]}}},require_expansion=True)
            self.assertEqual(rows[0]["encounters"][0][
                "blizzard_journal_encounter_id"],sentinel)
            self.assertFalse(rows[0]["journal_id_fields_complete"])
            self.assertTrue(rows[1]["journal_id_fields_complete"])
        invalid=zone(101,"Invalid",7,[(1,"Bad")])
        invalid["encounters"][0]["journalID"]="garbled"
        with self.assertRaisesRegex(
                probe.ProbeBlocked,"WCL_JOURNAL_ID_INVALID"):
            probe.parse_wcl_zones({"data":{"worldData":{"zones":[invalid]}}},
                                  require_expansion=True)

    def test_wcl_zone_source_shape_is_aggregate_only(self):
        old_frozen=zone(7,"Secret Name Unused",1,[])
        old_frozen["expansion"]=None
        old_frozen["frozen"]=True
        unscoped=zone(8,"Unknown New Content",999,[])
        unscoped["expansion"]={"id":0}
        valid=zone(9,"Active Named",31,[])
        payload={"data":{"worldData":{
            "zones":[old_frozen,unscoped,valid]}}}
        shape=probe.summarize_wcl_zone_shape(payload)
        self.assertEqual(shape["total_zones"],3)
        self.assertEqual(shape["zone_groups"],{
            "FROZEN_MISSING_ID":1,
            "UNFROZEN_NONPOSITIVE_ID":1,
            "UNFROZEN_POSITIVE_ID":1,
        })
        self.assertNotIn("Secret Name Unused",str(shape))
        self.assertNotIn("Unknown New Content",str(shape))

    def test_authenticated_probe_uses_two_bounded_wcl_requests_not_named_seed(self):
        requests=[]
        exps={"data":{"worldData":{"expansions":[
            {"id":7,"name":"A Historical Expansion"},
            {"id":41,"name":"Unknown New Expansion Name"}]}}}
        zones={"data":{"worldData":{"zones":[
            zone(40,"Old Zone",7,[(10,"Old Boss")],frozen=True),
            zone(41,"New Zone",41,[(11,"New Boss")])]}}}
        def local_request(url,*,method="GET",headers=None,data=None,
                          transport=None):
            requests.append((url,method,data))
            if url.startswith(probe.BLIZZARD_BASE+"/"):
                return {"current_season":{"id":991}}
            if url.endswith("/api/v2/client"):
                if b"expansions" in data:return exps
                if b"zones" in data:
                    self.assertNotIn(b"midnight",data.lower())
                    self.assertIn(b"expansion",data)
                    return zones
            raise AssertionError("UNEXPECTED_REQUEST "+url)
        with mock.patch.object(probe,"oauth_token",return_value="test-token"),\
             mock.patch.object(probe,"request_json",side_effect=local_request):
            report=probe.run_probe("b-id","b-secret","w-id","w-secret")
        self.assertEqual(report["blizzard"]["requests"],4)
        self.assertEqual(report["wcl"]["requests"],2)
        self.assertEqual(report["wcl"]["status"],
                         "ZONES_WITH_JOURNAL_IDS_RETURNED")
        self.assertEqual(report["wcl"]["zone_source_scope"],
                         "ALL_WCL_EXPANSIONS")
        self.assertEqual({x["expansion_id"] for x in report["wcl"]["zones"]},
                         {7,41})
        self.assertNotIn("midnight_zones",report["wcl"])
        self.assertNotIn("midnight_expansion_id",report["wcl"])
        self.assertTrue(report["interpretation"][
                        "wcl_all_expansions_are_candidates_not_active_season"])
        self.assertFalse(report["item_catalog_generated"])
        self.assertEqual(report["native_simc_calls"],0)
        self.assertNotIn("b-secret",str(report))
        self.assertNotIn("w-secret",str(report))
        self.assertEqual(len(requests),6)

    def test_unindexed_wcl_expansion_is_not_silently_promoted(self):
        def local_request(url,*,method="GET",headers=None,data=None,
                          transport=None):
            if url.startswith(probe.BLIZZARD_BASE+"/"):
                return {"current_season":{"id":991}}
            if b"expansions" in data:
                return {"data":{"worldData":{"expansions":[
                    {"id":7,"name":"Original"}]}}}
            return {"data":{"worldData":{"zones":[
                zone(99,"Unexpected",41,[(900,"Boss")])]}}}
        with mock.patch.object(probe,"oauth_token",return_value="test-token"),\
             mock.patch.object(probe,"request_json",side_effect=local_request):
            report=probe.run_probe("b-id","b-secret","w-id","w-secret")
        self.assertEqual(report["wcl"]["status"],"NOT_VERIFIED")
        self.assertEqual(report["wcl"]["error_code"],
                         "WCL_ZONE_EXPANSION_NOT_IN_SOURCE_INDEX")
        self.assertEqual(report["native_simc_calls"],0)


if __name__=="__main__":
    unittest.main()
