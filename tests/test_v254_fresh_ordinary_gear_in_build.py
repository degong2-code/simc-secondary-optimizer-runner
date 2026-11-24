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
from unittest import mock

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
                            "season_evidence":"DB2_DISPLAY_SEASON_MATCH",
                             "display_season_id":47,
                             "journal_instance_id":301,
                             "journal_encounter_id":302}]}]}
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
            return Response(b"ID,ItemID,ItemEffectID\n")
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

    def test_v697_reuses_sealed_effect_and_adds_only_public_delve_loot(self):
        linked=self.source()
        original=json.loads(Path(linked["candidate_path"]).read_text())
        original["full_season_completeness_confirmed"]=False
        Path(linked["candidate_path"]).write_text(json.dumps(original),"utf8")
        extra=[(299902,"Delve trinket",12),(299903,"Delve effect ring",11),
               (299904,"Delve plain armor",5)]
        with (self.wago/"Item.csv").open("a",encoding="utf8",newline="") as f:
            csv.writer(f).writerows([[iid,4,0,slot] for iid,_,slot in extra])
        with (self.wago/"ItemSparse.csv").open("a",encoding="utf8",newline="") as f:
            csv.writer(f).writerows([[iid,name,slot,11,0,4,-1,4]
                                    for iid,name,slot in extra])
        args=dict(stage_root=self.root,wago_folder=self.wago,build=self.BUILD,
                  linked=linked)
        calls=[]
        def old_transport(req,timeout):
            calls.append(req.full_url)
            return Response(b"ID,ItemID,ItemEffectID\n1,299903,12345\n")
        first=build._fresh_ordinary_gear_source_stage(**args,transport=old_transport)
        self.assertEqual(first["network_calls_by_stage"],1)
        old_path=Path(first["candidate_path"])
        old_bytes=old_path.read_bytes()
        def supplement(req,timeout):
            calls.append(req.full_url)
            self.assertEqual(req.full_url,build.delve_provider.SOURCE_URL)
            return Response(json.dumps({"items":[{"id":iid,"name":name}
                for iid,name,_ in extra]}).encode("utf8"))
        new=build._fresh_ordinary_gear_source_stage(
            **args,transport=supplement,include_delve=True)
        self.assertEqual(new["network_calls_by_stage"],1)
        self.assertEqual(new["supplementary_delve_resolved_count"],3)
        self.assertEqual(new["plain_candidate_count"],1)
        self.assertTrue(new["a7_auto_source_choice_provenance"][
                        "candidate_provenance_verified"],new)
        data=json.loads(Path(new["candidate_path"]).read_text())
        self.assertEqual({r["item_id"]:r["category"] for r in data["items"]},
            {self.item_id:"plain_representative_candidate",
             299902:"trinket",299903:"special_effect_gear_candidate"})
        self.assertEqual(old_path.read_bytes(),old_bytes)
        def no_fetch(req,timeout):
            self.fail("NO_REPEAT_SOURCE_FETCH")
        second=build._fresh_ordinary_gear_source_stage(
            **args,transport=no_fetch,include_delve=True)
        self.assertEqual(second["network_calls_by_stage"],0)
        self.assertEqual(second["candidate_path"],new["candidate_path"])
        self.assertEqual(len(calls),2)
        # A new classifier generation consumes exactly the same sealed
        # upstream bytes. No DB2 or provider HTTP, no old output mutation.
        old_generation=Path(new["candidate_path"])
        original_generation=old_generation.read_bytes()
        fingerprint=build.stage_engine.module_dependency_fingerprint
        def changed(entries):
            result=fingerprint(entries)
            if Path(entries[0]).name=="v165_current_season_gear_pool.py":
                return {**result,"sha256":"f"*64}
            return result
        with mock.patch.object(build.stage_engine,
                "module_dependency_fingerprint",side_effect=changed):
            upgraded=build._fresh_ordinary_gear_source_stage(
                **args,transport=no_fetch,include_delve=True)
            reused=build._fresh_ordinary_gear_source_stage(
                **args,transport=no_fetch,include_delve=True)
        self.assertEqual(upgraded["network_calls_by_stage"],0)
        self.assertEqual(upgraded["native_calls"],0)
        self.assertNotEqual(upgraded["candidate_path"],new["candidate_path"])
        self.assertEqual(Path(upgraded["candidate_path"]).read_bytes(),
                         original_generation)
        self.assertEqual(old_generation.read_bytes(),original_generation)
        self.assertEqual(reused["candidate_path"],upgraded["candidate_path"])
        self.assertEqual(reused["source_stage"]["status"],"REUSED_VERIFIED")

    def test_partial_delve_keeps_resolved_choices_and_unresolved_count(self):
        linked=self.source()
        original=json.loads(Path(linked["candidate_path"]).read_text())
        original["full_season_completeness_confirmed"]=False
        Path(linked["candidate_path"]).write_text(json.dumps(original),"utf8")
        with (self.wago/"Item.csv").open("a",encoding="utf8",newline="") as f:
            csv.writer(f).writerow([299902,4,0,12])
        with (self.wago/"ItemSparse.csv").open("a",encoding="utf8",newline="") as f:
            csv.writer(f).writerow([299902,"Delve trinket",12,11,0,4,-1,4])
        def transport(req,timeout):
            if req.full_url==build.delve_provider.SOURCE_URL:
                return Response(json.dumps({"items":[
                    {"id":299902,"name":"Delve trinket"},
                    {"id":299999,"name":"Unresolved item"}]}).encode("utf8"))
            return Response(b"ID,ItemID,ItemEffectID\n")
        args=dict(stage_root=self.root,wago_folder=self.wago,build=self.BUILD,
                  linked=linked,include_delve=True)
        result=build._fresh_ordinary_gear_source_stage(**args,transport=transport)
        self.assertEqual(result["supplementary_delve_status"],
                         "SUPPLEMENTARY_SOURCE_PARTIAL")
        self.assertEqual(result["supplementary_delve_unresolved_count"],1)
        self.assertTrue(result["a7_auto_source_choice_provenance"][
                        "candidate_provenance_verified"],result)
        data=json.loads(Path(result["candidate_path"]).read_text("utf8"))
        self.assertIn(299902,{r["item_id"] for r in data["items"]})
        def no_fetch(*args,**kwargs):
            self.fail("NO_REPEAT_SOURCE_FETCH")
        again=build._fresh_ordinary_gear_source_stage(**args,transport=no_fetch)
        self.assertEqual(again["network_calls_by_stage"],0)
        self.assertEqual(again["supplementary_delve_status"],
                         "SUPPLEMENTARY_SOURCE_PARTIAL")

    def test_v697_optional_provider_failure_keeps_raid_mplus(self):
        linked=self.source()
        def transport(req,timeout):
            if req.full_url==build.delve_provider.SOURCE_URL:
                return Response(b"invalid source JSON")
            return Response(b"ID,ItemID,ItemEffectID\n")
        result=build._fresh_ordinary_gear_source_stage(
            stage_root=self.root,wago_folder=self.wago,build=self.BUILD,
            linked=linked,transport=transport,include_delve=True)
        self.assertEqual(result["status"],"FRESH_GEAR_PLAIN_CANDIDATES_SOURCE_ONLY")
        self.assertEqual(result["supplementary_delve_status"],
                         "SUPPLEMENTARY_SOURCE_PENDING")
        self.assertEqual(result["plain_candidate_count"],1)
        prior=Path(result["candidate_path"])
        old=prior.read_bytes()
        def recovered(req,timeout):
            self.assertEqual(req.full_url,build.delve_provider.SOURCE_URL)
            return Response(json.dumps({"items":[{"id":self.item_id,
                "name":"Source plain sword"}]}).encode("utf8"))
        ready=build._fresh_ordinary_gear_source_stage(
            stage_root=self.root,wago_folder=self.wago,build=self.BUILD,
            linked=linked,transport=recovered,include_delve=True)
        self.assertEqual(ready["network_calls_by_stage"],1)
        self.assertEqual(ready["supplementary_delve_status"],
                         "SUPPLEMENTARY_SOURCE_OBSERVED")
        self.assertEqual(ready["plain_candidate_count"],1)
        self.assertNotEqual(ready["candidate_path"],result["candidate_path"])
        self.assertEqual(prior.read_bytes(),old)
        def no_fetch(*args,**kwargs):
            self.fail("NO_REPEAT_SOURCE_FETCH")
        again=build._fresh_ordinary_gear_source_stage(
            stage_root=self.root,wago_folder=self.wago,build=self.BUILD,
            linked=linked,transport=no_fetch,include_delve=True)
        self.assertEqual(again["network_calls_by_stage"],0)
        self.assertEqual(again["candidate_path"],ready["candidate_path"])

    def test_existing_source_refresh_is_independent_of_installed_budget(self):
        linked=self.source()
        # Recreate the original two local source receipts using the same
        # v217 engine, not a fake bypass of their output checks.
        original=json.loads(Path(linked["candidate_path"]).read_text("utf8"))
        original["full_season_completeness_confirmed"]=False
        raw=json.dumps(original).encode("utf8")
        rel="source/v163_unapproved_candidates_token_provenance.json"
        target=self.root/rel
        def write_join():
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(raw)
        build.stage_engine.execute_stage(root=self.root,
            stage_id="fresh-v163-token-provenance",stage_version="test",
            inputs={"game_build":self.BUILD},outputs={"candidate":rel},
            execute=write_join)
        content={k:(self.wago/(k+".csv")).read_bytes()
                 for k in ("Item","ItemSparse")}
        for k in content:(self.wago/(k+".csv")).unlink()
        # A separate budget sentinel represents an untouched original owner.
        budget=self.root/"original_installed_budget.json"
        budget.write_bytes(b"original budget bytes")
        def write_wago():
            for k,v in content.items():(self.wago/(k+".csv")).write_bytes(v)
            (self.wago/"receipt.json").write_text(json.dumps({
                "schema":"v161_wago_zero_seed_csv_snapshot_v1","build":self.BUILD,
                "locale":"enUS","tables":{k:{"sha256":build.digest(v),
                    "bytes":len(v)} for k,v in content.items()}}),"utf8")
        build.stage_engine.execute_stage(root=self.root,stage_id="fresh-wago-db2",
            stage_version="test",inputs={"game_build":self.BUILD},
            outputs={"receipt":"wago/receipt.json","Item":"wago/Item.csv",
                     "ItemSparse":"wago/ItemSparse.csv"},execute=write_wago)
        calls=[]
        def transport(req,timeout):
            calls.append(req.full_url)
            if req.full_url==build.delve_provider.SOURCE_URL:
                return Response(json.dumps({"items":[{"id":self.item_id,
                    "name":"Source plain sword"}]}).encode("utf8"))
            return Response(b"ID,ItemID,ItemEffectID\n")
        first=build.refresh_existing_season_gear_source(stage_root=self.root,
                    build=self.BUILD,transport=transport)
        self.assertEqual(first["network_calls"],2)
        self.assertEqual(first["native_calls"],0)
        second=build.refresh_existing_season_gear_source(stage_root=self.root,
                    build=self.BUILD,transport=transport)
        self.assertEqual(second["network_calls"],0)
        self.assertEqual(second["source_generation_sha256"],
                         first["source_generation_sha256"])
        self.assertEqual(len(calls),2)
        self.assertEqual(budget.read_bytes(),b"original budget bytes")
        self.assertEqual(target.read_bytes(),raw)
        (self.wago/"ItemSparse.csv").write_bytes(b"changed")
        with self.assertRaisesRegex(build.EnvironmentBuildBlocked,
                                   "SEASON_GEAR_REFRESH_ORIGINAL_SOURCE_DRIFT"):
            build.refresh_existing_season_gear_source(stage_root=self.root,
                    build=self.BUILD,transport=transport)
        self.assertEqual(len(calls),2)

    def test_pinned_raid_extra_loot_and_fixed_craft_are_public_only(self):
        linked=self.source()
        original=json.loads(Path(linked["candidate_path"]).read_text("utf8"))
        original["full_season_completeness_confirmed"]=False
        extra=[(299902,"Extra raid trinket",12),(299903,"Fixed craft ring",11),
               (299904,"Craft trinket",12),(299905,"Other raid",12),
               (299906,"Craft ordinary",5)]
        with (self.wago/"Item.csv").open("a",encoding="utf8",newline="") as f:
            csv.writer(f).writerows([[iid,4,0,slot] for iid,_,slot in extra])
        with (self.wago/"ItemSparse.csv").open("a",encoding="utf8",newline="") as f:
            csv.writer(f).writerows([[iid,name,slot,11,0,4,-1,4]
                                    for iid,name,slot in extra])
        self.write_csv("JournalEncounter.csv",["ID","JournalInstanceID","Name_lang"],[
            {"ID":303,"JournalInstanceID":301,"Name_lang":"Extra journal"},
            {"ID":403,"JournalInstanceID":401,"Name_lang":"Other raid"}])
        self.write_csv("JournalEncounterItem.csv",[
            "ID","JournalEncounterID","ItemID","DisplaySeasonID"],[
            {"ID":1,"JournalEncounterID":303,"ItemID":299902,"DisplaySeasonID":47},
            {"ID":2,"JournalEncounterID":403,"ItemID":299905,"DisplaySeasonID":47},
            {"ID":3,"JournalEncounterID":303,"ItemID":299999,"DisplaySeasonID":47}])
        self.write_csv("CraftingData.csv",["ID","CraftedItemID"],[
            {"ID":i,"CraftedItemID":iid} for i,iid in enumerate(
                (299903,299904,299906),1)])
        tables={p.stem:{"sha256":build.digest(p.read_bytes()),
                         "bytes":p.stat().st_size} for p in self.wago.glob("*.csv")}
        self.assertEqual(set(tables),{"JournalEncounter","JournalEncounterItem",
                                     "CraftingData","Item","ItemSparse"})
        receipt=json.dumps({"build":self.BUILD,"locale":"enUS","tables":tables}).encode()
        (self.wago/"receipt.json").write_bytes(receipt)
        original["snapshot_receipt_sha256"]=build.digest(receipt)
        raw=json.dumps(original).encode()
        Path(linked["candidate_path"]).write_bytes(raw)
        def transport(req,timeout):
            if req.full_url==build.delve_provider.SOURCE_URL:
                return Response(json.dumps({"items":[{"id":self.item_id,
                    "name":"Source plain sword"}]}).encode())
            return Response(b"ID,ItemID,ItemEffectID\n1,299903,12345\n")
        args=dict(stage_root=self.root,wago_folder=self.wago,build=self.BUILD,
                  linked=linked,include_delve=True)
        # Exercise the actual extension directly first; any source/parser
        # failure should report its exception, not a later missing dict key.
        effect=self.root/"direct_effect_fixture.csv"
        effect.write_bytes(b"ID,ItemID,ItemEffectID\n1,299903,12345\n")
        direct=build.source_gear_pool.expand_selectable_source(
            original,self.wago,effect)
        self.assertEqual(direct["selectable_source_extension"]["additional_candidate_ids"],
                         [299902,299903,299904])
        first=build._fresh_ordinary_gear_source_stage(**args,transport=transport)
        self.assertTrue(first.get("candidate_path"),first)
        self.assertTrue(first.get("a7_auto_source_choice_provenance",{}).get(
            "candidate_provenance_verified"),first)
        self.assertEqual(first["plain_candidate_count"],1)
        data=json.loads(Path(first["candidate_path"]).read_text("utf8"))
        self.assertEqual({x["item_id"]:x["category"] for x in data["items"]},
            {self.item_id:"plain_representative_candidate",299902:"trinket",
             299903:"special_effect_gear_candidate",299904:"trinket"})
        extension=first["selectable_source_extension"]
        self.assertEqual(extension["additional_candidate_ids"],[299902,299903,299904])
        self.assertEqual(extension["unresolved_join_rows"][0]["item_id"],299999)
        self.assertEqual(Path(linked["candidate_path"]).read_bytes(),raw)
        def no_fetch(*args,**kwargs):self.fail("NO_REPEAT_SOURCE_FETCH")
        second=build._fresh_ordinary_gear_source_stage(**args,transport=no_fetch)
        self.assertEqual(second["network_calls_by_stage"],0)
        self.assertEqual(second["candidate_path"],first["candidate_path"])
        self.assertEqual(second["selectable_source_extension"],extension)

    def test_rotation_trinkets_and_registered_extra_bosses_only(self):
        linked=self.source()
        original=json.loads(Path(linked["candidate_path"]).read_text("utf8"))
        original.update(full_season_completeness_confirmed=False,
            auto_source_scope={"wcl_expansion_id":15,"raid_zone":"Raid",
                               "mplus_zone":"Rotation"},
            wcl_zone_ids={"raid":1,"mplus":2})
        extra=[(299902,"Rotated old-expansion trinket",12,7),
               (299903,"Unscoped trinket",12,7),
               (299904,"Other season trinket",12,7),
               (299905,"Registered boss trinket",12,11),
               (299906,"Unregistered field boss trinket",12,11),
               (299907,"Unscoped ordinary",5,11),
               (299908,"Conflicting season trinket",12,7),
               (299909,"Current dungeon special ring",11,11),
               (299910,"Unscoped direct cloak",16,7),
               (299911,"Conflicting direct sword",17,7),
               (299912,"Unscoped direct unsupported type",19,11),
               (299913,"Unscoped plain armor",9,11),
               (299914,"Registered unscoped indirect head",1,11),
               (299915,"Unregistered unscoped indirect legs",7,11),
               (299916,"Registered conflicting indirect chest",5,11)]
        with (self.wago/"Item.csv").open("a",encoding="utf8",newline="") as f:
            csv.writer(f).writerows([[iid,4,0,slot] for iid,_,slot,_ in extra])
        with (self.wago/"ItemSparse.csv").open("a",encoding="utf8",newline="") as f:
            csv.writer(f).writerows([[iid,name,slot,exp,0,4,-1,4]
                                    for iid,name,slot,exp in extra])
        self.write_csv("JournalInstance.csv",["ID","MapID","Name_lang"],[
            {"ID":401,"MapID":100,"Name_lang":"Alternate journal name"},
            {"ID":501,"MapID":200,"Name_lang":"World bosses"}])
        self.write_csv("MapChallengeMode.csv",["ID","MapID","Name_lang"],[
            {"ID":71,"MapID":100,"Name_lang":"Rotation dungeon"},
            {"ID":72,"MapID":101,"Name_lang":"Missing dungeon"}])
        self.write_csv("MythicPlusSeasonTrackedMap.csv",
            ["DisplaySeasonID","MapChallengeModeID"],[
            {"DisplaySeasonID":47,"MapChallengeModeID":71},
            {"DisplaySeasonID":47,"MapChallengeModeID":72}])
        self.write_csv("JournalEncounter.csv",["ID","JournalInstanceID","Name_lang"],[
            {"ID":402,"JournalInstanceID":401,"Name_lang":"Dungeon boss"},
            {"ID":502,"JournalInstanceID":501,"Name_lang":"Registered boss"},
            {"ID":503,"JournalInstanceID":501,"Name_lang":"Unregistered field boss"}])
        self.write_csv("JournalEncounterItem.csv",
            ["ID","JournalEncounterID","ItemID","DisplaySeasonID"],[
            {"ID":i,"JournalEncounterID":eid,"ItemID":iid,"DisplaySeasonID":sid}
            for i,(eid,iid,sid) in enumerate([
                (402,299902,47),(402,299903,0),(402,299904,46),
                (502,299905,47),(503,299906,47),(402,299907,0),
                (402,299908,0),(402,299908,46),(402,299909,47),
                (402,299910,0),(402,299911,0),(402,299911,46),
                (402,299912,0),(402,299913,0),(502,299914,0),
                (503,299915,0),(502,299916,0),(502,299916,46)],1)])
        self.write_csv("CraftingData.csv",["ID","CraftedItemID"],[])
        tables={p.stem:{"sha256":build.digest(p.read_bytes()),
                         "bytes":p.stat().st_size} for p in self.wago.glob("*.csv")}
        receipt=json.dumps({"build":self.BUILD,"locale":"enUS","tables":tables}).encode()
        (self.wago/"receipt.json").write_bytes(receipt)
        original["snapshot_receipt_sha256"]=build.digest(receipt)
        raw=json.dumps(original).encode()
        Path(linked["candidate_path"]).write_bytes(raw)
        report={"schema":"v155_season_discovery_provider_probe_v1",
            "mode":"LIVE_AUTHENTICATED_BOUNDED","wcl":{"zones":[
                {"zone_id":i,"zone_name":name,"wcl_frozen":False,
                 "expansion_id":15,"encounters":[{"name":boss}]}
                for i,name,boss in [(1,"Raid","Raid boss"),(2,"Rotation","Rotation dungeon"),
                                    (3,"Extra bosses","Registered boss")]]}}
        def write_wcl():
            target=self.root/"source/season_api_report.json"
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(json.dumps(report),"utf8")
        build.stage_engine.execute_stage(root=self.root,stage_id="fresh-v155",
            stage_version="test",inputs={"build":self.BUILD},
            outputs={"report":"source/season_api_report.json"},execute=write_wcl)
        def transport(req,timeout):
            if req.full_url==build.delve_provider.SOURCE_URL:
                return Response(json.dumps({"items":[{"id":self.item_id,
                    "name":"Source plain sword"}]}).encode())
            return Response(b"ID,ItemID,ItemEffectID\n1,299909,12345\n2,299910,12346\n3,299911,12347\n4,299912,12348\n")
        args=dict(stage_root=self.root,wago_folder=self.wago,build=self.BUILD,
                  linked=linked,include_delve=True)
        first=build._fresh_ordinary_gear_source_stage(**args,transport=transport)
        self.assertTrue(first.get("candidate_path"),first)
        self.assertTrue(first.get("a7_auto_source_choice_provenance",{}).get(
            "candidate_provenance_verified"),first)
        self.assertEqual(first["plain_candidate_count"],1)
        data=json.loads(Path(first["candidate_path"]).read_text("utf8"))
        self.assertEqual({x["item_id"] for x in data["items"]},
                         {self.item_id,299902,299903,299905,299909,299910})
        rows=first["mplus_trinket_coverage"]
        self.assertEqual(rows[0]["registered_current_trinket_ids"],[299902])
        self.assertEqual(rows[0]["unscoped_only_trinket_ids"],[299903,299908])
        self.assertEqual(rows[0]["other_season_trinket_ids"],[299904,299908])
        self.assertEqual(rows[0]["rotation_unscoped_admitted_trinket_ids"],[299903])
        self.assertEqual(rows[0]["registered_rotation_trinket_ids"],[299902,299903])
        self.assertEqual(rows[0]["missing_rotation_trinket_ids"],[])
        self.assertEqual(rows[0]["unscoped_unresolved_trinket_ids"],[299908])
        recovered=next(x for x in data["items"] if x["item_id"]==299903)
        self.assertTrue(any(
            x["display_season_id"]==0 and
            x["active_rotation_display_season_id"]==47 and
            x["season_evidence"]=="DB2_ACTIVE_ROTATION_UNSCOPED_TRINKET"
            for x in recovered["source_evidence"]))
        special=next(x for x in data["items"] if x["item_id"]==299910)
        self.assertEqual(special["category"],"special_effect_gear_candidate")
        self.assertTrue(any(x["season_evidence"]=="DB2_ACTIVE_ROTATION_UNSCOPED_DIRECT_SPECIAL"
            and x["display_season_id"]==0 and x["active_rotation_display_season_id"]==47
            for x in special["source_evidence"]))
        extension=first["selectable_source_extension"]
        self.assertEqual(extension["indirect_review_item_ids"],[299907,299913,299914])
        review_rows={r["item_id"]:r for r in extension["effect_review_rows"]}
        self.assertNotIn(299915,review_rows)
        self.assertTrue(review_rows[299914]["source_review_only"])
        self.assertFalse(review_rows[299914]["variant_applicability_verified"])
        self.assertEqual(review_rows[299914]["acquisition_sources"][0]["journal_encounter_id"],502)
        self.assertEqual(review_rows[299914]["acquisition_sources"][0]["display_season_id"],0)
        self.assertFalse(review_rows[299916]["acquisition_sources"])
        self.assertTrue(review_rows[299916]["conflicting_source_occurrences"])
        raw_rotation=first["selectable_source_extension"]["mplus_dungeon_review"][0]
        self.assertEqual(raw_rotation["unscoped_direct_special_ids"],[299910,299911])
        self.assertEqual(raw_rotation["rotation_unscoped_admitted_special_ids"],[299910])
        self.assertEqual(rows[0]["missing_current_trinket_ids"],[])
        self.assertEqual(rows[1]["status"],"DUNGEON_JOURNAL_UNRESOLVED")
        self.assertEqual(first["selectable_source_extension"][
            "supplementary_wcl_boss_review"]["registered_extra_encounters"],1)
        self.assertEqual(Path(linked["candidate_path"]).read_bytes(),raw)
        def no_fetch(*args,**kwargs):self.fail("NO_REPEAT_SOURCE_FETCH")
        second=build._fresh_ordinary_gear_source_stage(**args,transport=no_fetch)
        self.assertEqual(second["network_calls_by_stage"],0)
        self.assertEqual(second["mplus_trinket_coverage"],rows)
        # Seal the same v163 bytes under the real parent stage path, then
        # prove the derived catalog is readable after process restart.
        parent_rel="source/v163_unapproved_candidates_token_provenance.json"
        def write_parent():
            (self.root/parent_rel).write_bytes(raw)
        build.stage_engine.execute_stage(root=self.root,
            stage_id="fresh-v163-token-provenance",stage_version="test",
            inputs={"build":self.BUILD},outputs={"candidate":parent_rel},
            execute=write_parent)
        restored=build.read_sealed_selectable_gear_generation(
            stage_root=self.root,build=self.BUILD)
        self.assertIsNotNone(restored)
        self.assertEqual(restored["candidate"],data)
        self.assertEqual(restored["network_calls"],0)
        self.assertEqual(restored["native_calls"],0)
        self.assertEqual(restored["source_generation_sha256"],
                         first["source_stage"]["receipt_sha256"])
        import v098_target_user_scenario_bootstrap as bootstrap
        base=dict(data)
        base["items"]=[r for r in data["items"] if r["item_id"] not in (299909,299910)]
        user={"special_items":[{"slot":"finger1","item_id":299909,"options":{}},
                               {"slot":"back","item_id":299910,"options":{}}]}
        selected,binding=bootstrap._selected_refresh_special_source(
            user=user,gear=base,stage_root=self.root)
        self.assertEqual([r["item_id"] for r in selected],[299909,299910])
        self.assertEqual(binding["source_generation_sha256"],
                         first["source_stage"]["receipt_sha256"])
        self.assertEqual(bootstrap._selected_refresh_special_source(
            user=user,gear=base,stage_root=self.root,pinned=binding),(selected,binding))
        self.assertEqual(bootstrap._selected_refresh_special_source(
            user={"special_items":[]},gear=base,stage_root=self.root),([],None))
        # A tampered candidate must never be added by a read-only GET.
        Path(first["candidate_path"]).write_bytes(b"{}")
        with self.assertRaisesRegex(bootstrap.UserScenarioBlocked,
                                    "SELECTED_REFRESH_PINNED_SOURCE_UNAVAILABLE"):
            bootstrap._selected_refresh_special_source(
                user=user,gear=base,stage_root=self.root,pinned=binding)
        self.assertIsNone(build.read_sealed_selectable_gear_generation(
            stage_root=self.root,build=self.BUILD))

    def test_bonus_raw_header_parser_accepts_multiline_and_rejects_invalid(self):
        validator=build.bonus_effect_review.valid_raw_table
        self.assertTrue(validator(b"ItemID,ItemBonusTreeID\r\n1,2\r\n3,4\r\n","ItemXBonusTree"))
        self.assertTrue(validator(b"\xef\xbb\xbfItemID,ItemBonusTreeID\n1,2\n","ItemXBonusTree"))
        self.assertFalse(validator(b"ID,Unknown\n1,2\n","ItemXBonusTree"))
        self.assertFalse(validator(b"","ItemXBonusTree"))

    def test_context_free_effect_lists_and_conditional_alternatives(self):
        review=build.bonus_effect_review
        node_header=("ID,ParentItemBonusTreeID,ChildItemBonusTreeID,ChildItemBonusListID,"
            "ChildItemBonusListGroupID,"+",".join(review.NODE_CONTEXT_FIELDS)+"\n")
        def leaf(n,tree,bonus,context=0,child=0,group=0):
            return ",".join(map(str,[n,tree,child,bonus,group,context,0,0,0,0,0,0]))+"\n"
        raw={
            "ItemXBonusTree":"ItemID,ItemBonusTreeID\n1,100\n2,200\n3,300\n4,400\n5,500\n6,600\n7,700\n",
            "ItemBonusTreeNode":node_header+leaf(1,100,701)+leaf(2,200,701,context=3)
                +leaf(3,300,702)+leaf(4,400,703)+leaf(5,500,701)+leaf(6,500,702)
                +leaf(7,600,0,child=100)+leaf(8,700,0,group=88),
            "ItemBonusListGroupEntry":"ItemBonusListGroupID,ItemBonusListID\n88,701\n",
            "ItemBonus":"ParentItemBonusListID,Type,Value_0\n701,4,33\n701,23,81\n"
                "702,23,82\n702,1,5\n703,50,701\n"}
        paths={}
        for name,data in raw.items():
            paths[name]=self.root/(name+".csv")
            paths[name].write_text(data,"utf8")
        out=review.discover(set(range(1,8)),paths)
        self.assertEqual(out["candidate_item_count"],7)
        self.assertEqual(out["context_free_effect_bonus_candidate_count"],1)
        self.assertEqual(out["conditional_or_mixed_bonus_candidate_count"],6)
        self.assertEqual(out["context_free_effect_bonus_candidates"][0]["item_id"],1)
        self.assertEqual(out["context_free_effect_bonus_candidates"][0]["bonus_ids"],[701])
        self.assertEqual(out["context_free_effect_bonus_candidates"][0]["bonus_effects"][0]["roots"],[
            {"root_tree_id":100,"node_ids":[1]}])
        self.assertEqual(out["items"][3]["bonus_effects"],[{"bonus_id":703,"item_effect_ids":[81]}])
        self.assertFalse(out["automatic_bonus_attachment"])
        self.assertFalse(out["itemlevel_and_acquisition_admission_verified"])

    def test_effect_input_join_preserves_scoped_source_and_pending(self):
        review=build.bonus_effect_review
        origin={"source":"raid_journal","journal_encounter_id":12,
                "journal_instance_id":34,"display_season_id":0}
        def row(i,**kw):
            return dict({"item_id":i,"name":"Source "+str(i),"slot":1,
                "direct_item_effect_record":False,"acquisition_sources":[dict(origin)]},**kw)
        def proof(i):
            return {"item_id":i,"bonus_ids":[101,102],"bonus_effects":[
                {"bonus_id":101,"item_effect_ids":[91]},
                {"bonus_id":102,"item_effect_ids":[92]}]}
        observed={"schema":review.SCHEMA,"items":[{"item_id":i} for i in range(1,6)],
                  "context_free_effect_bonus_candidates":[proof(i) for i in (1,3,4,5)]}
        result=review.reconcile_effect_options(observed,[
            row(1),row(2),row(3,direct_item_effect_record=True),
            row(4,acquisition_sources=[dict(origin,display_season_id=46)])],
            season_id=47)
        self.assertEqual(result["effect_option_candidate_count"],1)
        option=result["effect_option_candidates"][0]
        self.assertEqual(option["required_options"],{"bonus_id":"101/102"})
        self.assertEqual(option["acquisition_sources"],[origin])
        self.assertFalse(option["explicit_current_season_origin"])
        self.assertFalse(option["itemlevel_and_acquisition_admission_verified"])
        self.assertEqual({r["item_id"]:r["reason"] for r in result["effect_option_pending"]},
            {2:"CONDITIONAL_OR_MIXED_EFFECT_BONUS",3:"DIRECT_OR_UNKNOWN_EFFECT_SOURCE_REQUIRES_MERGE",
             4:"NO_SCOPED_JOURNAL_ORIGIN",5:"NO_SCOPED_PHYSICAL_SOURCE_ROW"})
        with self.assertRaisesRegex(review.BonusReviewBlocked,"DUPLICATE"):
            review.reconcile_effect_options(observed,[row(1),row(1)],season_id=47)

    def test_bonus_review_reuses_tier_raw_and_caches_missing_two_tables(self):
        linked=self.source()
        original=json.loads(Path(linked["candidate_path"]).read_text("utf8"))
        original["full_season_completeness_confirmed"]=False
        Path(linked["candidate_path"]).write_text(json.dumps(original),"utf8")
        def transport(req,timeout):
            if req.full_url==build.delve_provider.SOURCE_URL:
                return Response(json.dumps({"items":[{"id":self.item_id,
                    "name":"Source plain sword"}]}).encode())
            return Response(b"ID,ItemID,ItemEffectID\n")
        gear=build._fresh_ordinary_gear_source_stage(
            stage_root=self.root,wago_folder=self.wago,build=self.BUILD,
            linked=linked,transport=transport,include_delve=True)
        self.assertTrue(gear.get("candidate_path"),gear)
        # Use a real v217 receipt and same-build v250 raw bytes, not a
        # mock bypass of source identity checks.
        raw={"ItemXBonusTree":(
            "ItemID,ItemBonusTreeID\n"+str(self.item_id)+",100\n999999,100\n").encode(),
            "ItemBonusTreeNode":b"ParentItemBonusTreeID,ChildItemBonusTreeID,ChildItemBonusListID,ChildItemBonusListGroupID\n100,200,0,0\n200,100,701,88\n"}
        output={k:"source/v250_bonus_"+k+".csv" for k in raw}
        output["result"]="source/v250_raid_bonus_corroboration.json"
        def write_tier_raw():
            for k,v in raw.items():(self.root/output[k]).write_bytes(v)
            (self.root/output["result"]).write_text(json.dumps({
                "schema":build.raid_bonus.SCHEMA,"game_build":self.BUILD,
                "source_evidence":{k+"_sha256":build.digest(v) for k,v in raw.items()}}),"utf8")
        build.stage_engine.execute_stage(root=self.root,
            stage_id="fresh-v250-raid-bonus-corroboration",stage_version="test",
            inputs={"game_build":self.BUILD},outputs=output,execute=write_tier_raw)
        calls=[]
        def bonus_transport(req,timeout):
            calls.append(req.full_url)
            if "/ItemBonusListGroupEntry/" in req.full_url:
                return Response(b"ItemBonusListGroupID,ItemBonusListID\n88,702\n88,703\n")
            self.assertIn("/ItemBonus/",req.full_url)
            return Response(b"ParentItemBonusListID,Type,Value_0\n701,23,81\n702,23,82\n703,1,83\n")
        args=dict(stage_root=self.root,build=self.BUILD,gear=gear,
                  transport=bonus_transport)
        first=build._review_selectable_bonus_effects(**args)
        self.assertEqual(first["status"],"POTENTIAL_BONUS_EFFECT_LINKS_OBSERVED",first)
        self.assertEqual(first["network_calls_by_stage"],2)
        self.assertEqual(first["candidate_item_count"],1)
        data=json.loads(Path(first["candidate_path"]).read_text("utf8"))
        self.assertEqual(data["items"],[{"item_id":self.item_id,
            "bonus_effects":[{"bonus_id":701,"item_effect_ids":[81]},
                             {"bonus_id":702,"item_effect_ids":[82]}],
            "applicable_variant_verified":False}])
        self.assertFalse(data["automatic_bonus_attachment"])
        second=build._review_selectable_bonus_effects(**args)
        self.assertEqual(second["network_calls_by_stage"],0)
        self.assertEqual(second["candidate_path"],first["candidate_path"])
        self.assertEqual(len(calls),2)
        for k,v in raw.items():self.assertEqual((self.root/output[k]).read_bytes(),v)

    def test_unauthenticated_join_has_zero_network(self):
        result=build._fresh_ordinary_gear_source_stage(
            stage_root=self.root,wago_folder=self.wago,
            build=self.BUILD,linked={"candidate_path":None})
        self.assertEqual(result["network_calls_by_stage"],0)
        self.assertIsNone(result["candidate_path"])


if __name__=="__main__":
    unittest.main()
