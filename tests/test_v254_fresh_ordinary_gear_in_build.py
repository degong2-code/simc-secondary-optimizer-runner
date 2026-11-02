"""P3-AU: one source-only ordinary gear join in the normal Environment Build.

These tests use synthetic CSV/HTTP, not live Wago or actual Native G.
"""
import csv
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v216_environment_build_coordinator as build


class Response(io.BytesIO):
    status=200
    def __enter__(self):
        return self
    def __exit__(self,*exc):
        self.close()


class FreshOrdinaryGearSource(unittest.TestCase):
    BUILD="12.2.0.99999"

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.wago=self.root/"wago"
        self.wago.mkdir()
        self.item_id=299901

    def write_csv(self,name,fields,rows):
        with (self.wago/name).open("w",encoding="utf8",newline="") as stream:
            writer=csv.DictWriter(stream,fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def source(self,expansion=11,inventory=13):
        row={"schema":"v163_zero_seed_db2_join_v1",
             "source_provider":"WAGO_TOOLS_PINNED_DB2_WCL_LIVE",
             "build":self.BUILD,"db2_expansion_id":11,
             "db2_display_season_id":47,
             "old_item_catalog_imported":False,
             "items":[{"item_id":self.item_id,
                       "name":"Current raid plain one-hand sword",
                       "slot":inventory,
                       "acquisition_sources":[
                           {"source":"raid_journal",
                            "season_evidence":"UNKNOWN_UNSCOPED_JOURNAL"}]}]}
        path=self.root/"v163_source.json"
        path.write_text(json.dumps(row),encoding="utf8")
        self.write_csv("Item.csv",
                       ["ID","ClassID","SubclassID","InventoryType"],
                       [{"ID":self.item_id,"ClassID":4 if inventory==12 else 2,
                         "SubclassID":0 if inventory==12 else 7,
                         "InventoryType":inventory}])
        self.write_csv("ItemSparse.csv",
                       ["ID","Display_lang","InventoryType","ExpansionID",
                        "ItemSet","OverallQualityID","AllowableClass",
                        "StatModifier_bonusStat_0"],
                       [{"ID":self.item_id,"Display_lang":"Source plain sword",
                         "InventoryType":inventory,"ExpansionID":expansion,
                         "ItemSet":0,"OverallQualityID":4,
                         "AllowableClass":-1,
                         "StatModifier_bonusStat_0":4}])
        return {"candidate_path":str(path),
                "stage":{"receipt_sha256":"a"*64}}

    def test_same_build_source_join_sealed_and_reused_zero_http(self):
        linked=self.source()
        urls=[]
        def transport(request,timeout):
            urls.append(request.full_url)
            self.assertEqual(timeout,75)
            self.assertIn("ItemXItemEffect/csv",request.full_url)
            self.assertIn("12.2.0.99999",request.full_url)
            return Response(b"ID,ItemID,ItemEffectID\n")
        args={"stage_root":self.root,"wago_folder":self.wago,
              "build":self.BUILD,"linked":linked,"transport":transport}
        first=build._fresh_ordinary_gear_source_stage(**args)
        second=build._fresh_ordinary_gear_source_stage(**args)
        self.assertEqual(first["status"],"FRESH_GEAR_PLAIN_CANDIDATES_SOURCE_ONLY")
        self.assertEqual(first["network_calls_by_stage"],1)
        self.assertEqual(first["plain_candidate_count"],1)
        self.assertEqual(first["plain_weapon_candidate_count"],1)
        self.assertEqual(second["network_calls_by_stage"],0)
        self.assertEqual(len(urls),1)
        self.assertEqual(first["source_stage"]["status"],"EXECUTED_AND_SEALED")
        self.assertEqual(second["source_stage"]["status"],"REUSED_VERIFIED")
        self.assertFalse(first["season_representative_verified"])
        self.assertFalse(first["seasonal_G_verified"])
        candidate=json.loads(Path(first["candidate_path"]).read_text())
        self.assertEqual(candidate["item_count"],1)
        self.assertEqual(candidate["items"][0]["item_id"],self.item_id)
        self.assertEqual(candidate["items"][0]["category"],
                         "plain_representative_candidate")
        pool=json.loads((self.root/"source"/
                         "v254_fresh_ordinary_gear_v165_pool.json").read_text())
        self.assertIsNone(pool["consumable_budget_reference"])
        self.assertIsNone(pool["G"])
        self.assertIsNone(pool["B"])
        self.assertIsNone(pool["T"])
        self.assertEqual(pool["supplementary_localbots_status"],
                         "OPTIONAL_SOURCE_NOT_COLLECTED")

    def test_old_expansion_or_wrong_v163_build_never_becomes_gear(self):
        linked=self.source(expansion=7)
        calls=[]
        def transport(request,timeout):
            calls.append(request.full_url)
            return Response(b"ID,ItemID,ItemEffectID\n")
        result=build._fresh_ordinary_gear_source_stage(
            stage_root=self.root,wago_folder=self.wago,
            build=self.BUILD,linked=linked,transport=transport)
        self.assertEqual(result["status"],"FRESH_GEAR_SOURCE_OR_JOIN_PENDING")
        self.assertIsNone(result["candidate_path"])
        self.assertFalse(result["season_representative_verified"])
        self.assertEqual(len(calls),1)
        linked=self.source()
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_FRESH_GEAR_V163_SOURCE_MISMATCH"):
            build._fresh_ordinary_gear_source_stage(
                stage_root=self.root,wago_folder=self.wago,
                build="12.2.0.99998",linked=linked,transport=transport)
        self.assertEqual(len(calls),1)

    def test_trinket_only_source_stays_pending_not_ordinary_pool(self):
        linked=self.source(inventory=12)
        calls=[]
        def transport(request,timeout):
            calls.append(request.full_url)
            return Response(b"ID,ItemID,ItemEffectID\\n")
        result=build._fresh_ordinary_gear_source_stage(
            stage_root=self.root,wago_folder=self.wago,
            build=self.BUILD,linked=linked,transport=transport)
        self.assertEqual(result["status"],
                         "FRESH_GEAR_PLAIN_CANDIDATES_NOT_FOUND_PENDING")
        self.assertEqual(result["item_count"],1)
        self.assertEqual(result["plain_candidate_count"],0)
        self.assertEqual(result["plain_weapon_candidate_count"],0)
        self.assertEqual(result["plain_armor_candidate_count"],0)
        self.assertIsNotNone(result["candidate_path"])
        self.assertFalse(result["season_representative_verified"])
        self.assertEqual(len(calls),1)

    def test_unauthenticated_join_has_zero_network(self):
        result=build._fresh_ordinary_gear_source_stage(
            stage_root=self.root,wago_folder=self.wago,
            build=self.BUILD,linked={"candidate_path":None})
        self.assertEqual(result["network_calls_by_stage"],0)
        self.assertIsNone(result["candidate_path"])


if __name__=="__main__":
    unittest.main()
