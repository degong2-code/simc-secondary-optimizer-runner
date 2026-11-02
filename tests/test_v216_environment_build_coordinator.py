import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v212_environment_manifest as v212
import v216_environment_build_coordinator as v216


def sealed_manifest(*,dependency=None):
    payload={
        "schema":v212.SCHEMA,
        "status":"READY_WITH_LIMITATIONS",
        "source_catalog":{
            "artifact_sha256":"a"*64,
            "manifest_sha256":"b"*64,
            "game_build":"12.1.5.70575",
            "simc_revision":"c"*40,
            "v191":{"sha256":"d"*64,"sha256_by_input":{
                "gear":"1"*64,"tier":"2"*64,"budget":"3"*64}},
            "v211":{"sha256":"e"*64},
        },
        "approved_ui_catalog":{"normalized_sha256":"f"*64},
        "target_profile":{
            "normalized_result_sha256":"4"*64,
            "profile_files":{"profile.simc":{"sha256":"5"*64}},
            "static_cache":None,
            "profile_supplier_coverage_sha256":"6"*64,
        },
        "product_scope":{"profile_supplier_coverage":{
            "current_season_profile_supplier_count":26,
            "contract_count":26,
            "adaptive_native_evidence_complete":False}},
        "dependency_change":dependency or {
            "status":"INITIAL_ENVIRONMENT","changed_inputs":["v213_source_catalog"],
            "invalidated_components":["v098_profile","environment_manifest"],
            "cache_mutations":0,"native_calls":0},
        "readiness_limitations":["ALL_26_ADAPTIVE_PROFILE_NATIVE_ACCEPTANCE_NOT_COMPLETE"],
        "unresolved_dependencies":["ALL_26_ADAPTIVE_PROFILE_NATIVE_ACCEPTANCE"],
        "native_calls":0,"network_calls":0,
    }
    return {**payload,"manifest_sha256":
            v216.digest(v216.canonical(payload).encode("utf8"))}


def source_document(path):
    doc={"schema":"v213_current_season_source_to_catalog_v1",
         "manifest_sha256":"b"*64,"game_build":"12.1.5.70575",
         "simc_revision":"c"*40}
    path.write_text(json.dumps(doc),encoding="utf8")
    return doc


def make_receipt(session_id,scope,manifest_sha):
    payload={"schema":v216.SCHEMA,"session_id":session_id,
             "environment_scope_sha256":scope,
             "environment_manifest_sha256":manifest_sha,
             "native_calls":0,"network_calls":0,"cache_mutations":0,
             "historical_sessions_preserved":True}
    return {**payload,"receipt_sha256":
            v216.digest(v216.canonical(payload).encode("utf8"))}


class EnvironmentBuildCoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        self.binary=self.root/"simc.exe"
        self.binary.write_bytes(b"fake-binary-no-native")
        self.cache=self.root/"static-cache.json"
        self.cache.write_text("{}",encoding="utf8")
        self.user={"character":{"class":"paladin","spec":"retribution"},
                   "target":{"ilevel":334,"final_T":None}}
        self.revision="c"*40



    def test_blizzard_wcl_authenticated_stage_runs_before_wago_and_reuses(self):
        import io
        from urllib.parse import urlsplit
        from runner import v242_authenticated_season_source_stage as source
        calls=[]
        secret="SECRET_NEVER_PERSIST"
        creds={"BLIZZARD_CLIENT_ID":"blizzard-test",
               "BLIZZARD_CLIENT_SECRET":secret,
               "WCL_CLIENT_ID":"wcl-test",
               "WCL_CLIENT_SECRET":secret+"-WCL"}
        class Response(io.BytesIO):
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):self.close()
        def transport(req,timeout):
            url=req.full_url
            calls.append(url)
            if url.endswith("/token"):
                doc={"access_token":"PRIVATE_FAKE_BEARER"}
            elif "/api/v2/client" in url:
                payload=json.loads(req.data)
                if "expansions" in payload["query"]:
                    doc={"data":{"worldData":{"expansions":[
                        {"id":11,"name":"Midnight"}]}}}
                else:
                    doc={"data":{"worldData":{"zones":[
                        {"id":99,"name":"Synthetic Raid","frozen":False,
                         "encounters":[{"id":100,"name":"Boss",
                                        "journalID":200}]}]}}}
            elif "/season/index" in url:
                doc={"current_season":{"id":55}}
            else:
                doc={"items":[]}
            return Response(json.dumps(doc).encode())
        def fetch(req,timeout):
            calls.append(req.full_url)
            table=urlsplit(req.full_url).path.split("/")[-2]
            return Response(("ID,Name\n1,"+table+"\n").encode())
        folder=self.root/"live"
        first=v216.collect_wago_new_season_source(
            sessions_root=folder,expected_game_build="12.2.0.99999",
            fetch=fetch,credentials=creds,discovery_transport=transport)
        count=len(calls)
        self.assertEqual(count,18) # 2 OAuth, 4 Blizzard, 2 WCL + 10 Wago
        self.assertEqual(first["network_calls_by_stage"],18)
        self.assertEqual(first["season_discovery"]["status"],
                         "AUTHENTICATED_SOURCE_DISCOVERED_SEASON_JOIN_PENDING")
        self.assertFalse(first["season_discovery"]["current_season_membership_verified"])
        self.assertEqual(first["season_join"]["status"],
                         "LIVE_SEASON_SCOPE_AMBIGUOUS_PENDING")
        self.assertFalse(first["season_join"]["season_membership_verified"])
        self.assertFalse(first["environment_installed"])
        report=pathlib.Path(first["season_discovery"]["source_report_path"])
        data=report.read_text("utf8")
        self.assertNotIn(secret,data)
        self.assertNotIn("PRIVATE_FAKE_BEARER",data)
        second=v216.collect_wago_new_season_source(
            sessions_root=folder,expected_game_build="12.2.0.99999",
            fetch=fetch,credentials=creds,discovery_transport=transport)
        self.assertEqual(len(calls),count)
        self.assertEqual(second["network_calls_by_stage"],0)
        self.assertEqual(second["season_discovery"]["stage"]["status"],
                         "REUSED_VERIFIED")
        self.assertEqual(second["source_stage"]["status"],"REUSED_VERIFIED")
        self.assertTrue(report.is_file())


    def test_unique_authenticated_scope_executes_v163_once_and_reuses(self):
        import csv
        import io
        from urllib.parse import urlsplit
        from unittest import mock
        data={
            "JournalTierXInstance":[
                {"ID":1,"JournalTierID":505,"JournalInstanceID":1}],
            "JournalInstance":[
                {"ID":1,"Name_lang":"Synthetic Raid","MapID":100},
                {"ID":2,"Name_lang":"Synthetic Dungeon","MapID":200}],
            "JournalEncounter":[
                {"ID":11,"JournalInstanceID":1,"Name_lang":"Hydra"},
                {"ID":22,"JournalInstanceID":2,"Name_lang":"Dungeon Boss"}],
            "JournalEncounterItem":[
                {"ID":1,"JournalEncounterID":11,"ItemID":1001,
                 "DisplaySeasonID":0,"WorldStateExpressionID":0},
                {"ID":2,"JournalEncounterID":22,"ItemID":2001,
                 "DisplaySeasonID":37,"WorldStateExpressionID":0}],
            "MythicPlusSeasonTrackedMap":[
                {"ID":1,"MapChallengeModeID":9,"DisplaySeasonID":37}],
            "MapChallengeMode":[
                {"ID":9,"Name_lang":"Synthetic Dungeon","MapID":200}],
            "Map":[{"ID":100,"MapName_lang":"Synthetic Raid"},
                   {"ID":200,"MapName_lang":"Synthetic Dungeon"}],
            "CraftingData":[{"ID":1,"CraftedItemID":3001}],
            "ItemSparse":[
                {"ID":i,"Display_lang":str(i),"ExpansionID":11,
                 "OverallQualityID":4,"LimitCategory":0,
                 "StatModifier_bonusStat_0":24 if i==3001 else 0,
                 "StatModifier_bonusStat_1":25 if i==3001 else 0}
                for i in (1001,2001,3001)],
            "Item":[{"ID":i,"ClassID":4,"InventoryType":5}
                    for i in (1001,2001,3001)],
        }
        report={"schema":"v155_season_discovery_provider_probe_v1",
                "mode":"LIVE_AUTHENTICATED_BOUNDED",
                "blizzard":{"endpoints":{"keystone_season_index":{
                    "data":{"current_season_id":18}}}},
                "wcl":{"midnight_zones":[
                    {"zone_id":10,"zone_name":"Synthetic Raid",
                     "wcl_frozen":False,"encounters":[{"name":"Hydra"}]},
                    {"zone_id":11,"zone_name":"Mythic+ Test",
                     "wcl_frozen":False,
                     "encounters":[{"name":"Synthetic Dungeon"}]}]}}
        report_path=self.root/"synthetic_v155.json"
        report_path.write_text(json.dumps(report),encoding="utf8")
        encoded={}
        for table,rows in data.items():
            stream=io.StringIO()
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
            writer.writeheader();writer.writerows(rows)
            encoded[table]=stream.getvalue().encode("utf8")
        calls=[]
        class Response(io.BytesIO):
            status=200
            def __enter__(self):return self
            def __exit__(self,*a):self.close()
        def fetch(req,timeout):
            table=urlsplit(req.full_url).path.split("/")[-2]
            calls.append(table)
            return Response(encoded[table])
        fake_discovery={
            "schema":"v242_authenticated_season_discovery_stage_v1",
            "status":"AUTHENTICATED_SOURCE_DISCOVERED_SEASON_JOIN_PENDING",
            "source_report_path":str(report_path),
            "season_join_ready":True,
            "network_calls_by_stage":0,
        }
        with mock.patch.object(v216.discovery_stage,"collect",
                               return_value=fake_discovery), \
             mock.patch.object(v216.season_join,"build_index",
                               wraps=v216.season_join.build_index) as compiled:
            first=v216.collect_wago_new_season_source(
                sessions_root=self.root/"runtime",
                expected_game_build="12.2.0.99999",fetch=fetch,
                credentials={})
            second=v216.collect_wago_new_season_source(
                sessions_root=self.root/"runtime",
                expected_game_build="12.2.0.99999",fetch=fetch,
                credentials={})
        self.assertEqual(compiled.call_count,1)
        self.assertEqual(len(calls),10)
        self.assertEqual(first["season_join"]["status"],
                         "DB2_WCL_CANDIDATES_JOINED_SEASON_CONDITIONS_PENDING")
        self.assertEqual(first["season_join"]["stage"]["status"],
                         "EXECUTED_AND_SEALED")
        self.assertEqual(second["season_join"]["stage"]["status"],
                         "REUSED_VERIFIED")
        self.assertEqual(second["network_calls_by_stage"],0)
        self.assertFalse(first["season_join"]["season_membership_verified"])
        joined=json.loads(pathlib.Path(first["season_join"]["candidate_path"])
                          .read_text(encoding="utf8"))
        self.assertEqual(joined["auto_source_scope"]["expansion_id"],11)
        self.assertEqual(joined["collection_counts"]["raid_journal"],1)
        self.assertFalse(joined["full_season_completeness_confirmed"])
        self.assertFalse(first["environment_installed"])
        self.assertIsNone(first["G"])
        self.assertIsNone(first["T"])

    def test_partial_season_credentials_block_before_wago_fetch(self):
        calls=[]
        def fetch(req,timeout):
            calls.append(1)
            raise AssertionError("NO_WAGO_ON_INCOMPLETE_CREDENTIAL_PAIRS")
        with self.assertRaisesRegex(
                v216.EnvironmentBuildBlocked,
                "V242_INCOMPLETE_BLIZZARD_WCL_CREDENTIAL_PAIRS"):
            v216.collect_wago_new_season_source(
                sessions_root=self.root/"live",
                expected_game_build="12.2.0.99999",fetch=fetch,
                credentials={"BLIZZARD_CLIENT_ID":"x",
                             "BLIZZARD_CLIENT_SECRET":"",
                             "WCL_CLIENT_ID":"x",
                             "WCL_CLIENT_SECRET":"x"})
        self.assertEqual(calls,[])
        self.assertFalse((self.root/"live"/"_fresh_season_sources"/
                          "wago_12.2.0.99999"/"wago").exists())

    def test_live_collector_reuse_by_build_without_old_season_or_native(self):
        from urllib.parse import urlsplit, parse_qs
        from unittest import mock
        import io
        calls=[]
        class Response(io.BytesIO):
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):self.close()
        def fetch(req,timeout):
            url=urlsplit(req.full_url)
            self.assertEqual(url.hostname,"wago.tools")
            self.assertEqual(parse_qs(url.query)["build"],["12.2.0.99999"])
            table=url.path.split("/")[-2]
            self.assertIn(table,v216.wago_snapshot.TABLES)
            calls.append(table)
            return Response(("ID,Name\n1,"+table+"\n").encode())
        base=self.root/"user-sessions"
        with mock.patch.object(v216.stage_engine,"_snapshot",
                               wraps=v216.stage_engine._snapshot) as snapshots:
            a=v216.collect_wago_new_season_source(
                sessions_root=base,expected_game_build="12.2.0.99999",
                fetch=fetch)
            b=v216.collect_wago_new_season_source(
                sessions_root=base,expected_game_build="12.2.0.99999",
                fetch=fetch)
        self.assertEqual(len(calls),len(v216.wago_snapshot.TABLES))
        self.assertEqual(len(set(calls)),len(v216.wago_snapshot.TABLES))
        self.assertEqual(a["source_stage"]["status"],"EXECUTED_AND_SEALED")
        self.assertEqual(b["source_stage"]["status"],"REUSED_VERIFIED")
        self.assertEqual(b["source_stage"]["receipt_writes"],0)
        self.assertEqual(a["network_calls_by_stage"],10)
        self.assertEqual(b["network_calls_by_stage"],0)
        self.assertGreater(snapshots.call_count,1)
        self.assertFalse(a["environment_ready"])
        self.assertFalse(a["environment_installed"])
        self.assertFalse(a["source_season_verified"])
        self.assertIsNone(a["G"])
        self.assertIsNone(a["T"])
        self.assertEqual(list(base.iterdir())[0].name,
                         "_fresh_season_sources")
        folder=pathlib.Path(a["snapshot_receipt_path"]).parent
        self.assertFalse((folder/"db2-snapshot.zip").exists())
        receipt=json.loads((folder/"receipt.json").read_text("utf8"))
        self.assertEqual(receipt["fetched_at_utc"],a["fetched_at_utc"])
        self.assertEqual(len(receipt["tables"]),10)
        self.assertTrue(all(row["source_url"].startswith(
            "https://wago.tools/db2/") for row in receipt["tables"].values()))
        tampered=folder/"Item.csv"
        tampered.write_text("ID,Name\n1,changed\n",encoding="utf8")
        with self.assertRaisesRegex(
                v216.EnvironmentBuildBlocked,
                "V216_FRESH_WAGO_STAGE_BLOCKED:STAGE_OUTPUT_HASH_MISMATCH"):
            v216.collect_wago_new_season_source(
                sessions_root=base,expected_game_build="12.2.0.99999",
                fetch=fetch)
        self.assertEqual(len(calls),10)
        self.assertFalse((base/"generated").exists())

    def test_collector_wrong_build_and_symlink_fail_before_network(self):
        calls=[]
        def fetch(*args,**kwargs):
            calls.append(1)
            raise AssertionError("NETWORK_NOT_ALLOWED")
        with self.assertRaisesRegex(
                v216.EnvironmentBuildBlocked,
                "V216_EXPLICIT_NEW_SEASON_BUILD_REQUIRED"):
            v216.collect_wago_new_season_source(
                sessions_root=self.root,expected_game_build="old",
                fetch=fetch)
        root=self.root/"linked"
        actual=self.root/"real";actual.mkdir()
        root.symlink_to(actual,target_is_directory=True)
        with self.assertRaisesRegex(
                v216.EnvironmentBuildBlocked,
                "V216_SEASON_SOURCE_SESSION_ROOT_SYMLINK_BLOCKED"):
            v216.collect_wago_new_season_source(
                sessions_root=root,expected_game_build="12.2.0.99999",
                fetch=fetch)
        self.assertEqual(calls,[])

    def test_scope_identity_groups_same_user_across_dependency_versions(self):
        first=v216.environment_scope_identity(self.user)
        same=v216.environment_scope_identity(dict(self.user))
        changed_user=v216.environment_scope_identity(
            self.user|{"combat":{"targets":2}})
        self.assertEqual(first["scope_sha256"],same["scope_sha256"])
        self.assertNotEqual(first["scope_sha256"],changed_user["scope_sha256"])

    def test_previous_environment_lookup_requires_valid_receipt_and_manifest(self):
        scope="a"*64
        prior=self.root/("1"*20)
        generated=prior/"generated"
        generated.mkdir(parents=True)
        manifest=sealed_manifest()
        (generated/"environment_manifest.json").write_text(
            json.dumps(manifest),encoding="utf8")
        receipt=make_receipt(prior.name,scope,manifest["manifest_sha256"])
        (generated/"environment_build_receipt.json").write_text(
            json.dumps(receipt),encoding="utf8")
        current=self.root/("2"*20)
        current.mkdir()
        found=v216.find_previous_environment(self.root,current,scope)
        self.assertEqual(found["session_id"],prior.name)
        self.assertEqual(found["manifest"]["manifest_sha256"],
                         manifest["manifest_sha256"])
        receipt["native_calls"]=1
        (generated/"environment_build_receipt.json").write_text(
            json.dumps(receipt),encoding="utf8")
        self.assertIsNone(v216.find_previous_environment(
            self.root,current,scope))

    def test_receipt_digest_and_side_effect_contract_fail_closed(self):
        receipt=make_receipt("1"*20,"a"*64,"b"*64)
        self.assertTrue(v216.verify_receipt(receipt))
        corrupted=dict(receipt,native_calls=1)
        with self.assertRaises(v216.EnvironmentBuildBlocked):
            v216.verify_receipt(corrupted)

    def test_build_is_incremental_reuses_same_manifest_and_preserves_cache(self):
        source=self.root/"source.json"
        source_document(source)
        session=self.root/("3"*20)
        session.mkdir()
        first=sealed_manifest()
        calls=[]
        def compile_paths(*args,**kwargs):
            calls.append(args[5] if len(args)>5 else None)
            return first
        with mock.patch.object(v216.environment_manifest,
                               "compile_from_paths",side_effect=compile_paths):
            result1=v216.build_environment(
                sessions_root=self.root,session_folder=session,user=self.user,
                binary=self.binary,revision=self.revision,static_cache=self.cache,
                source_catalog_path=source,bootstrap_result={"schema":"v098"},
            )
            result2=v216.build_environment(
                sessions_root=self.root,session_folder=session,user=self.user,
                binary=self.binary,revision=self.revision,static_cache=self.cache,
                source_catalog_path=source,bootstrap_result={"schema":"v098"},
            )
            result3=v216.build_environment(
                sessions_root=self.root,session_folder=session,user=self.user,
                binary=self.binary,revision=self.revision,static_cache=self.cache,
                source_catalog_path=source,bootstrap_result={"schema":"v098"},
            )
        self.assertFalse(result1["manifest_reused"])
        self.assertTrue(result2["manifest_reused"])
        self.assertTrue(result3["manifest_reused"])
        self.assertEqual(calls[0],None)
        self.assertIsNone(calls[1])
        self.assertEqual(result3["receipt"]["native_calls"],0)
        self.assertEqual(result3["receipt"]["season_budget"]["status"],
                         "INSTALLED_REFERENCE_ONLY_GJFO_REFRESH_NOT_VERIFIED")
        self.assertIn("SEASON_GJFO_AUTO_REFRESH_NOT_VERIFIED",
                      result3["receipt"]["readiness"]["limitations"])
        self.assertEqual(result3["receipt"]["network_calls"],0)
        self.assertEqual(result3["receipt"]["cache_mutations"],0)
        self.assertTrue(result3["receipt"]["historical_sessions_preserved"])
        self.assertTrue(result3["receipt"]["cache_reuse"]["static_item_cache_preserved"])
        self.assertTrue(v216.verify_receipt(json.loads(
            (session/"generated"/"environment_build_receipt.json")
            .read_text(encoding="utf8"))))


if __name__=="__main__":
    unittest.main()
