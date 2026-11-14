"""P1-WEB-1 FastAPI HTTP boundary; all tests OFFLINE, never execute SimC."""
import copy
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

from fastapi.testclient import TestClient

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v113_local_web_api as web
import v106_user_session_controller as sessions
from tests.test_v106_user_session_controller import fake_native
from tests.test_v213_source_to_catalog import SourceToCatalogTests
import v213_source_to_catalog as source_bridge

class LocalWebAPIOffline(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        self.binary=self.root/"fake_simc.exe"
        self.binary.write_bytes(b"FAKE_SIMC_BINARY_ZERO_NATIVE")
        self.controls=sessions.standard_controls()
        self.payload={"controls":self.controls,"binary":str(self.binary),
                      "revision":"7bc1071","static_cache":None}
        self.app=web.create_app(root=self.root/"runs",token="offline-only-token")
        self.client=TestClient(self.app,base_url="http://127.0.0.1:8765")
        self.headers={"x-simc-local-token":"offline-only-token",
                      "origin":"http://127.0.0.1:8765"}
        self.postheaders=self.headers|{"content-type":"application/json"}

    def post(self,path,data=None):
        return self.client.post(path,json=data if data is not None else {},
                                headers=self.postheaders)

    def plan(self):
        r=self.post("/api/v1/sessions/plan",self.payload)
        self.assertEqual(r.status_code,200,r.text)
        return r.json()



    def test_v463_sealed_saved_season_options_do_not_use_active_or_packaged(self):
        """Read-only installed v212 runeforge/enchants bound to exact v213 SHA."""
        build="12.1.5.70783"
        digest="b"*64
        docs=self.app.state.jobs.root/"_fresh_season_sources"/(
            "wago_"+build)/"fresh_source"
        docs.mkdir(parents=True)
        (docs/("v212_installed_"+digest[:20]+".json")).write_text("{}")
        (docs/"v213_candidate_catalog.json").write_text("{}")
        doc={"manifest_sha256":digest,"game_build":build,
             "target_ilevel":334,
             "source_catalog_artifact_sha256":"c"*64,
             "source_catalog_manifest_sha256":"a"*64,
             "official_O_physical_source":None,
             "published_verified_options":[{
                 "enchant_id":91234,"slot":"boots",
                 "simc_token":"enchant_boots__example",
                 "highest_verified_quality_rank":3,"ui_selectable":True}],
             "verified_DK_runeforges":{
                 "items":[{"enchant_id":3370,"class":"deathknight",
                           "weapon_hands":["main_hand"],
                           "display_name":"룬"}],
                 "source_sha256":"d"*64,"manifest_sha256":"e"*64,
                 "game_build":build}}
        catalog={"manifest_sha256":"a"*64,"game_build":build}
        published={"schema":web.ui_catalog.SCHEMA,
                   "status":"SOURCE_COMBINED_WITH_CLEAR_APPROVAL_BOUNDARY",
                   "season_build":build,
                   "source_catalog":{"manifest_sha256":"a"*64}}
        url=("/api/v1/season-option-catalog?game_build="+build+
             "&target_ilevel=334&installed_manifest_sha256="+digest)
        with (mock.patch.object(web.environment_manifest,"read_json",
                 side_effect=[(doc,"ignored"),(catalog,"c"*64)]),
              mock.patch.object(web.environment_manifest,
                 "verify_fresh_installed_environment"),
              mock.patch.object(web.environment_build,
                 "find_verified_installed_season_environment",
                 return_value={"installed_manifest_sha256":digest}) as found,
              mock.patch.object(web.source_to_catalog,"verify_catalog"),
              mock.patch.object(web.ui_catalog,"public_options",
                 return_value=published) as options,
              mock.patch.object(web.subprocess,"Popen",
                 side_effect=AssertionError("NO_NATIVE"))):
            response=self.client.get(url,headers=self.headers)
        self.assertEqual(response.status_code,200,response.text)
        data=response.json()
        self.assertEqual(data["source_scope"],
                         "VERIFIED_INSTALLED_V212_OPTION_CATALOG")
        self.assertEqual(data["installed_manifest_sha256"],digest)
        registered=data["verified_installed_enchant_registrations"]
        self.assertEqual(registered["installed_manifest_sha256"],digest)
        self.assertEqual(registered["status"],
                         "INSTALLED_POLICY_A_REGISTRATIONS_RUNTIME_BINDING_PENDING")
        self.assertEqual(registered["items"],[{
            "enchant_id":91234,"slot":"boots",
            "simc_token":"enchant_boots__example",
            "highest_verified_quality_rank":3}])
        self.assertFalse(registered["runtime_selectable"])
        self.assertFalse(registered["new_approval_granted"])
        self.assertEqual(data["verified_weapon_enhancements"][
                         "dk_runeforges"]["items"][0]["enchant_id"],3370)
        self.assertEqual(found.call_args.kwargs[
                         "expected_installed_manifest_sha256"],digest)
        self.assertEqual(options.call_args.args[0],
                         docs/"v213_candidate_catalog.json")
        self.assertEqual(self.client.get(
            "/api/v1/season-option-catalog?game_build="+build,
            headers=self.headers).status_code,422)
        mismatch=self.client.get(url.replace(digest,"f"*64),
                                 headers=self.headers)
        self.assertEqual(mismatch.status_code,200)
        self.assertEqual(mismatch.json()["status"],
                         "SOURCE_OPTION_CATALOG_UNAVAILABLE")
        self.assertEqual(mismatch.json()[
            "verified_weapon_enhancements"] if
            "verified_weapon_enhancements" in mismatch.json() else {},{})
        self.assertEqual(self.client.get(url).status_code,403)

    def test_v460_installed_v212_gear_candidates_source_bound_and_fail_closed(self):
        """Existing v212/v213 sealed candidate catalogue only, zero Native."""
        build="12.1.5.70783"
        digest="b"*64
        catalog_sha="c"*64
        docs=self.app.state.jobs.root/"_fresh_season_sources"/("wago_"+build)/"fresh_source"
        docs.mkdir(parents=True)
        (docs/("v212_installed_"+digest[:20]+".json")).write_text("{}")
        (docs/"v213_candidate_catalog.json").write_text("{}")
        doc={"manifest_sha256":digest,"game_build":build,
             "target_ilevel":334,
             "source_catalog_artifact_sha256":catalog_sha,
             "source_catalog_manifest_sha256":"a"*64,
             "official_O_physical_source":None}
        row={"item_id":269999,"name":"Current-season trinket","category":"trinket",
             "user_selectable":False,"inventory_type":12,"class_id":4,
             "subclass_id":0,"slot_hint":None}
        catalog={"manifest_sha256":"a"*64,"game_build":build,
                 "catalog":{"gear":{"count":1,"slot_groups":{"trinket":[row]}}}}
        url=("/api/v1/season-gear?game_build="+build+
             "&target_ilevel=334&installed_manifest_sha256="+digest)
        with (mock.patch.object(web.environment_manifest,"read_json",
                 side_effect=[(doc,"source"),(catalog,catalog_sha)]),
              mock.patch.object(web.environment_manifest,
                 "verify_fresh_installed_environment",return_value=True),
              mock.patch.object(web.environment_build,
                 "find_verified_installed_season_environment",
                 return_value={"installed_manifest_sha256":digest}) as find,
              mock.patch.object(web.source_to_catalog,"verify_catalog",
                 return_value=True),
              mock.patch.object(web.official_ko_env,"read_names",
                 return_value={269999:"현 시즌 장신구"}),
              mock.patch.object(web.season_gear,"read",
                 side_effect=AssertionError("packaged v167 fallback forbidden"))):
            result=self.client.get(url,headers=self.headers)
        self.assertEqual(result.status_code,200,result.text)
        payload=result.json()
        self.assertEqual(payload["season_build"],build)
        self.assertEqual(payload["installed_manifest_sha256"],digest)
        self.assertEqual(payload["source_scope"],
                         "VERIFIED_INSTALLED_V212_SOURCE_V213_CANDIDATES")
        self.assertEqual(payload["choices"]["trinket"][0]["item_id"],269999)
        self.assertEqual(payload["choices"]["trinket"][0]["name_ko"],
                         "현 시즌 장신구")
        self.assertFalse(payload["full_season_completeness_confirmed"])
        self.assertEqual(payload["native_calls_now"],0)
        self.assertEqual(find.call_args.kwargs[
                         "expected_installed_manifest_sha256"],digest)
        self.assertEqual(self.client.get(url.replace(
            digest,"9"*64),headers=self.headers).json()["choices"]["trinket"],[])
        self.assertEqual(self.client.get(url.replace(
            "target_ilevel=334","target_ilevel=335"),
            headers=self.headers).json()["choices"]["trinket"],[])
        self.assertEqual(self.client.get(
            "/api/v1/season-gear?game_build="+build,
            headers=self.headers).status_code,422)
        self.assertEqual(self.client.get(url).status_code,403)

    def test_verified_installed_oil_loadouts_are_read_only_and_empty(self):
        got=self.client.get("/api/v1/verified-oil-loadouts?ilevel=334",
                            headers=self.headers)
        self.assertEqual(got.status_code,200,got.text)
        self.assertEqual(got.json()["items"],[])
        self.assertEqual(got.json()["native_calls"],0)
        self.assertEqual(got.json()["network_calls"],0)
        self.assertEqual(
            self.client.get("/api/v1/verified-oil-loadouts?ilevel=334").status_code,
            403)

    def test_verified_flask_choices_reuse_same_v212_installs_and_zero_o(self):
        """Read-only verified F from a sealed O=0 installation, not DB2."""
        build="12.1.5.70783"
        docs=self.app.state.jobs.root/"_fresh_season_sources"/("wago_"+build)/"fresh_source"
        docs.mkdir(parents=True)
        digest="d"*64
        (docs/("v212_installed_"+digest[:20]+".json")).write_text("{}")
        (docs/("v113_profile_"+digest[:20]+".json")).write_text("{}")
        physical={"physical_item_id":241326,"simc_input_token":"flask_example_3",
                  "crafting_quality":3,"F_rating":165}
        doc={"manifest_sha256":digest,"game_build":build,"target_ilevel":334,
             "official_F_physical_source":physical,
             "official_O_physical_source":None}
        proof={"installed_manifest_sha256":digest}
        with (mock.patch.object(web.environment_manifest,"read_json",
                                return_value=(doc,"sha")),
              mock.patch.object(web.environment_manifest,
                                "verify_fresh_installed_environment",
                                return_value=True) as verifier,
              mock.patch.object(web.environment_build,
                                "find_verified_installed_season_environment",
                                return_value=proof) as finder,
              mock.patch.object(web.subprocess,"Popen",
                                side_effect=AssertionError("NO_NATIVE"))):
            res=self.client.get(
                "/api/v1/verified-oil-loadouts?ilevel=334&game_build="+build,
                headers=self.headers)
        self.assertEqual(res.status_code,200,res.text)
        self.assertEqual(res.json()["items"],[])
        self.assertEqual(res.json()["verified_flasks"],[physical])
        self.assertEqual(res.json()["native_calls"],0)
        self.assertEqual(res.json()["network_calls"],0)
        verifier.assert_called_once_with(doc)
        finder.assert_called_once_with(
            self.app.state.jobs.root,334,expected_game_build=build,
            selected_oil_item_ids_by_hand={},
            expected_installed_manifest_sha256=digest)
        proof["installed_manifest_sha256"]="e"*64
        with (mock.patch.object(web.environment_manifest,"read_json",
                                return_value=(doc,"sha")),
              mock.patch.object(web.environment_manifest,
                                "verify_fresh_installed_environment",return_value=True),
              mock.patch.object(web.environment_build,
                                "find_verified_installed_season_environment",
                                return_value=proof)):
            mismatched=self.client.get(
                "/api/v1/verified-oil-loadouts?ilevel=334&game_build="+build,
                headers=self.headers)
        self.assertEqual(mismatched.json()["verified_flasks"],[])
        (docs/("v113_profile_"+digest[:20]+".json")).unlink()
        self.assertEqual(self.client.get(
            "/api/v1/verified-oil-loadouts?ilevel=334&game_build="+build,
            headers=self.headers).json()["verified_flasks"],[])
        self.assertEqual(self.client.get(
            "/api/v1/verified-oil-loadouts?ilevel=334").status_code,403)

    def test_oil_loadout_only_if_exact_installed_and_profile_saved(self):
        build="12.1.5.70783"
        docs=(self.app.state.jobs.root/"_fresh_season_sources"/
              ("wago_"+build)/"fresh_source")
        docs.mkdir(parents=True)
        sha="a"*64
        (docs/("v212_installed_"+sha[:20]+".json")).write_text("{}")
        profile=docs/("v113_profile_"+sha[:20]+".json")
        profile.write_text("{}")
        physical={"selected_oil_item_ids_by_hand":{"main_hand":243734},
                  "oil_by_hand":{"main_hand":{
                     "physical_item_id":243734,
                     "simc_input_token":"main_hand:thalassian_phoenix_oil_2"}}}
        doc={"manifest_sha256":sha,"game_build":build,
             "target_ilevel":334,"official_O_physical_source":physical}
        proof={"installed_manifest_sha256":sha}
        with (mock.patch.object(web.environment_manifest,"read_json",
                                return_value=(doc,"sha")),
              mock.patch.object(web.environment_manifest,
                                "verify_fresh_installed_environment",
                                return_value=True) as verifier,
              mock.patch.object(web.environment_build,
                                "find_verified_installed_season_environment",
                                return_value=proof) as finder):
            result=self.client.get(
                "/api/v1/verified-oil-loadouts?ilevel=334&game_build="+build,
                headers=self.headers)
        self.assertEqual(result.status_code,200,result.text)
        choices=result.json()
        self.assertEqual(choices["status"],"VERIFIED_INSTALLED_OIL_LOADOUTS")
        self.assertEqual(len(choices["items"]),1)
        self.assertEqual(choices["items"][0]["selected_oil_item_ids_by_hand"],
                         {"main_hand":243734})
        verifier.assert_called_once_with(doc)
        finder.assert_called_once_with(
            self.app.state.jobs.root,334,expected_game_build=build,
            selected_oil_item_ids_by_hand={"main_hand":243734},
            expected_installed_manifest_sha256=sha)
        # No source verification, no list. Never turn a raw ID into an option.
        proof["installed_manifest_sha256"]="b"*64
        with (mock.patch.object(web.environment_manifest,"read_json",
                                return_value=(doc,"sha")),
              mock.patch.object(web.environment_manifest,
                                "verify_fresh_installed_environment",
                                return_value=True),
              mock.patch.object(web.environment_build,
                                "find_verified_installed_season_environment",
                                return_value=proof)):
            rejected=self.client.get(
                "/api/v1/verified-oil-loadouts?ilevel=334&game_build="+build,
                headers=self.headers)
        self.assertEqual(rejected.json()["items"],[])
        profile.unlink()
        self.assertEqual(self.client.get(
            "/api/v1/verified-oil-loadouts?ilevel=334&game_build="+build,
            headers=self.headers).json()["items"],[])

    def test_v469_exact_oil_and_two_flasks_selects_only_matching_v212(self):
        """One O map can own two F variants; never pick whichever was newest."""
        build="12.1.5.70783"
        ids={"main_hand":243734}
        directory=(self.app.state.jobs.root/"_fresh_season_sources"/
                   ("wago_"+build)/"fresh_source")
        directory.mkdir(parents=True)
        installed={}
        for suffix,flask_id in (("a",241326),("b",241327)):
            digest=suffix*64
            (directory/("v212_installed_"+digest[:20]+".json")).write_text("{}")
            (directory/("v113_profile_"+digest[:20]+".json")).write_text(
                json.dumps({"environment_result":{}}))
            installed[digest[:20]]={
                "manifest_sha256":digest,"game_build":build,
                "target_ilevel":334,
                "official_O_physical_source":{
                    "selected_oil_item_ids_by_hand":dict(ids)},
                "official_F_physical_source":{"physical_item_id":flask_id}}
        checked=[]
        def read_installed(path,*_args):
            digest=pathlib.Path(path).stem.split("_")[-1]
            return installed[digest],"mock original bytes"
        def exact_finder(root,ilevel,*,expected_game_build,
                         selected_oil_item_ids_by_hand,
                         expected_installed_manifest_sha256=None):
            self.assertEqual(root,self.app.state.jobs.root)
            self.assertEqual((ilevel,expected_game_build),(334,build))
            self.assertEqual(selected_oil_item_ids_by_hand,ids)
            # No first-match same-oil lookup may bypass the selected F.
            self.assertIsNotNone(expected_installed_manifest_sha256)
            checked.append(expected_installed_manifest_sha256)
            return {"installed_manifest_sha256":
                    expected_installed_manifest_sha256}
        jobs=self.app.state.jobs
        selection={"target_ilevel":334,"explicit_build":build,
                   "selected_oil_hands":["main_hand"],
                   "selected_oil_item_ids_by_hand":ids}
        with (mock.patch.object(web.environment_manifest,"read_json",
                                side_effect=read_installed),
              mock.patch.object(web.environment_manifest,
                                "verify_fresh_installed_environment"),
              mock.patch.object(web.environment_build,
                                "find_verified_installed_season_environment",
                                side_effect=exact_finder),
              mock.patch.object(jobs,"restore_verified_fresh_profile",
                                return_value={"status":"EXACT_USER_PROFILE"}) as restore,
              mock.patch.object(web.subprocess,"Popen",
                                side_effect=AssertionError("NO_NATIVE"))):
            result=jobs.load_fresh_profile_for_user(
                **selection,selected_flask_item_id=241327)
            self.assertEqual(result["status"],"EXACT_USER_PROFILE")
            restore.assert_called_once_with(
                target_ilevel=334,game_build=build,
                selected_oil_item_ids_by_hand=ids,
                expected_installed_manifest_sha256="b"*64,
                required_gem_layout=None)
            self.assertEqual(checked,["b"*64])
            restore.reset_mock()
            checked.clear()
            with self.assertRaisesRegex(
                    web.environment_manifest.EnvironmentBlocked,
                    "WEB_USER_VARIANT_NOT_INSTALLED_OR_AMBIGUOUS"):
                jobs.load_fresh_profile_for_user(**selection)
            restore.assert_not_called()
            self.assertEqual(set(checked),{"a"*64,"b"*64})
            checked.clear()
            with self.assertRaisesRegex(
                    web.environment_manifest.EnvironmentBlocked,
                    "WEB_USER_VARIANT_NOT_INSTALLED_OR_AMBIGUOUS"):
                jobs.load_fresh_profile_for_user(
                    **selection,selected_flask_item_id=999999)
            restore.assert_not_called()
            self.assertEqual(checked,[])

    def test_v472_no_oil_unqualified_request_never_picks_newest_fj(self):
        """An API caller omitting F/J may not guess a saved same-O variant."""
        build="12.1.5.70783"
        directory=(self.app.state.jobs.root/"_fresh_season_sources"/
                   ("wago_"+build)/"fresh_source")
        directory.mkdir(parents=True)
        originals={}
        for suffix,flask_id in (("a",241326),("b",241327)):
            digest=suffix*64
            (directory/("v212_installed_"+digest[:20]+".json")).write_text("{}")
            (directory/("v113_profile_"+digest[:20]+".json")).write_text(
                json.dumps({"environment_result":{}}))
            originals[digest[:20]]={
                "manifest_sha256":digest,"game_build":build,
                "target_ilevel":334,
                "official_O_physical_source":None,
                "official_F_physical_source":{"physical_item_id":flask_id}}
        inspected=[]
        def original_read(path,*_args):
            digest=pathlib.Path(path).stem.split("_")[-1]
            return originals[digest],"mock original bytes"
        def exact_source(root,ilevel,*,expected_game_build,
                         selected_oil_item_ids_by_hand=None,
                         expected_installed_manifest_sha256=None,
                         **kwargs):
            self.assertEqual((ilevel,expected_game_build),(334,build))
            self.assertEqual(selected_oil_item_ids_by_hand,{})
            # A physical O=0 map alone cannot choose a unique F/J source.
            self.assertIsNotNone(expected_installed_manifest_sha256)
            inspected.append(expected_installed_manifest_sha256)
            return {"installed_manifest_sha256":
                    expected_installed_manifest_sha256}
        jobs=self.app.state.jobs
        with (mock.patch.object(web.environment_manifest,"read_json",
                                side_effect=original_read),
              mock.patch.object(web.environment_manifest,
                                "verify_fresh_installed_environment"),
              mock.patch.object(web.environment_build,
                                "find_verified_installed_season_environment",
                                side_effect=exact_source),
              mock.patch.object(jobs,"restore_verified_fresh_profile",
                                return_value={"status":"ONE_EXACT_SOURCE"}) as restore,
              mock.patch.object(web.subprocess,"Popen",
                                side_effect=AssertionError("NO_NATIVE"))):
            with self.assertRaisesRegex(
                    web.environment_manifest.EnvironmentBlocked,
                    "WEB_USER_VARIANT_NOT_INSTALLED_OR_AMBIGUOUS"):
                jobs.load_fresh_profile_for_user(
                    334,build,selected_oil_hands=[])
            restore.assert_not_called()
            self.assertEqual(set(inspected),{"a"*64,"b"*64})
            inspected.clear()
            chosen=jobs.load_fresh_profile_for_user(
                334,build,selected_oil_hands=[],
                selected_flask_item_id=241327)
            self.assertEqual(chosen["status"],"ONE_EXACT_SOURCE")
            restore.assert_called_once_with(
                target_ilevel=334,game_build=build,
                selected_oil_item_ids_by_hand={},
                expected_installed_manifest_sha256="b"*64,
                required_gem_layout=None)
            self.assertEqual(inspected,["b"*64])
        # One uniquely verified O=0 installation remains usable by default.
        (directory/("v212_installed_"+("a"*20)+".json")).unlink()
        (directory/("v113_profile_"+("a"*20)+".json")).unlink()
        inspected.clear()
        with (mock.patch.object(web.environment_manifest,"read_json",
                                side_effect=original_read),
              mock.patch.object(web.environment_manifest,
                                "verify_fresh_installed_environment"),
              mock.patch.object(web.environment_build,
                                "find_verified_installed_season_environment",
                                side_effect=exact_source),
              mock.patch.object(jobs,"restore_verified_fresh_profile",
                                return_value={"status":"ONE_EXACT_SOURCE"}) as restore,
              mock.patch.object(web.subprocess,"Popen",
                                side_effect=AssertionError("NO_NATIVE"))):
            self.assertEqual(jobs.load_fresh_profile_for_user(
                334,build,selected_oil_hands=[])["status"],
                "ONE_EXACT_SOURCE")
            restore.assert_called_once()
            self.assertEqual(inspected,["b"*64])

    def test_v465_same_build_same_oils_distinct_verified_flasks_visible(self):
        """Each F variant must verify its own v212 SHA, not the newest oil match."""
        build="12.1.5.70783"
        directory=(self.app.state.jobs.root/"_fresh_season_sources"/
                   ("wago_"+build)/"fresh_source")
        directory.mkdir(parents=True)
        manifests={}
        for digest,flask_id in (("a"*64,241326),("b"*64,241327)):
            (directory/("v212_installed_"+digest[:20]+".json")).write_text("{}")
            (directory/("v113_profile_"+digest[:20]+".json")).write_text("{}")
            manifests[digest[:20]]={
                "manifest_sha256":digest,"game_build":build,
                "target_ilevel":334,
                "official_O_physical_source":{
                    "selected_oil_item_ids_by_hand":{"main_hand":243734},
                    "oil_by_hand":{"main_hand":{
                        "physical_item_id":243734,
                        "simc_input_token":"main_hand:thalassian_phoenix_oil_2"}}},
                "official_F_physical_source":{
                    "physical_item_id":flask_id,
                    "simc_input_token":"flask_example_3",
                    "crafting_quality":3,"F_rating":165}}
        calls=[]
        def installed_read(path,*args):
            digest=pathlib.Path(path).stem.split("_")[-1]
            return manifests[digest],"source sha"
        def exact_find(root,target_ilevel,*,expected_game_build,
                       selected_oil_item_ids_by_hand,
                       expected_installed_manifest_sha256=None):
            calls.append(expected_installed_manifest_sha256)
            if expected_installed_manifest_sha256 is None:
                return None  # The previous ambiguous same-oil search fails.
            return {"installed_manifest_sha256":
                    expected_installed_manifest_sha256}
        with (mock.patch.object(web.environment_manifest,"read_json",
                                side_effect=installed_read),
              mock.patch.object(web.environment_manifest,
                                "verify_fresh_installed_environment"),
              mock.patch.object(web.environment_build,
                                "find_verified_installed_season_environment",
                                side_effect=exact_find),
              mock.patch.object(web.subprocess,"Popen",
                                side_effect=AssertionError("NO_NATIVE"))):
            res=self.client.get(
                "/api/v1/verified-oil-loadouts?ilevel=334&game_build="+build,
                headers=self.headers)
        self.assertEqual(res.status_code,200,res.text)
        data=res.json()
        self.assertEqual([v["physical_item_id"]
                          for v in data["verified_flasks"]],[241326,241327])
        self.assertEqual(len(data["items"]),1,  # same oil hand is one choice
                         data["items"])
        self.assertEqual(set(calls),{"a"*64,"b"*64})
        self.assertEqual(len(calls),2)
        self.assertEqual(data["native_calls"],0)
        self.assertEqual(data["network_calls"],0)

    def test_v466_more_than_sixty_four_installs_do_not_hide_verified_choices(self):
        """All 70 local F/O variants remain visible; zero Native/network."""
        build="12.1.5.70783"
        docs=(self.app.state.jobs.root/"_fresh_season_sources"/
              ("wago_"+build)/"fresh_source")
        docs.mkdir(parents=True)
        installed={}
        for index in range(70):
            digest=f"{index+1:020x}"+"f"*44
            oil_id=243734+index
            flask_id=241326+index
            path=docs/("v212_installed_"+digest[:20]+".json")
            path.write_text("{}",encoding="utf8")
            (docs/("v113_profile_"+digest[:20]+".json")).write_text(
                "{}",encoding="utf8")
            installed[path.name]={
                "manifest_sha256":digest,"game_build":build,
                "target_ilevel":334,
                "official_O_physical_source":{
                    "selected_oil_item_ids_by_hand":{"main_hand":oil_id},
                    "oil_by_hand":{"main_hand":{
                        "physical_item_id":oil_id,
                        "simc_input_token":"main_hand:synthetic_test_oil"}}},
                "official_F_physical_source":{
                    "physical_item_id":flask_id,
                    "simc_input_token":"synthetic_test_flask",
                    "crafting_quality":3,"F_rating":165}}
        observed=[]
        def read_receipt(path,*_args):
            return installed[pathlib.Path(path).name],"synthetic raw sha"
        def verify_exact(root,level,*,expected_game_build,
                         selected_oil_item_ids_by_hand,
                         expected_installed_manifest_sha256=None):
            self.assertEqual(root,self.app.state.jobs.root)
            self.assertEqual(level,334)
            self.assertEqual(expected_game_build,build)
            digest=expected_installed_manifest_sha256
            self.assertIsNotNone(digest)
            row=installed["v212_installed_"+digest[:20]+".json"]
            self.assertEqual(
                row["official_O_physical_source"][
                    "selected_oil_item_ids_by_hand"],
                selected_oil_item_ids_by_hand)
            observed.append(digest)
            return {"installed_manifest_sha256":digest}
        with (mock.patch.object(web.environment_manifest,"read_json",
                  side_effect=read_receipt),
              mock.patch.object(web.environment_manifest,
                  "verify_fresh_installed_environment"),
              mock.patch.object(web.environment_build,
                  "find_verified_installed_season_environment",
                  side_effect=verify_exact),
              mock.patch.object(web.official_ko_env,"read_names",
                  return_value={}),
              mock.patch.object(web.subprocess,"Popen",
                  side_effect=AssertionError("NO_NATIVE"))):
            response=self.client.get(
                "/api/v1/verified-oil-loadouts?ilevel=334&game_build="+build,
                headers=self.headers)
        self.assertEqual(response.status_code,200,response.text)
        result=response.json()
        self.assertEqual(len(result["items"]),70)
        self.assertEqual(len(result["verified_flasks"]),70)
        self.assertEqual(len(set(observed)),70)
        self.assertEqual(
            {entry["selected_oil_item_ids_by_hand"]["main_hand"]
             for entry in result["items"]},
            {243734+i for i in range(70)})
        self.assertEqual(
            {row["physical_item_id"] for row in result["verified_flasks"]},
            {241326+i for i in range(70)})
        self.assertEqual(result["native_calls"],0)
        self.assertEqual(result["network_calls"],0)

    def test_controlled_cold_start_web_real_collector_and_rebuild(self):
        """P3-DS T0: web -> original v216/v161/v217 in a virgin workspace.

        Replace external Wago transport only. Real source compilation,
        budget PENDING and source-stage receipt behaviors remain unmocked.
        """
        import io
        import socket
        from urllib.parse import parse_qs, urlsplit

        build="12.2.0.99999"  # Synthetic identity, NOT live season evidence.
        workspace=self.root/"runs"
        self.assertFalse(workspace.exists())
        calls=[]

        class Response(io.BytesIO):
            status=200
            def __enter__(self):return self
            def __exit__(self,*exc):self.close()

        def fixture_fetch(req,timeout):
            url=urlsplit(req.full_url)
            self.assertEqual(url.hostname,"wago.tools")
            self.assertEqual(parse_qs(url.query)["build"],[build])
            self.assertEqual(parse_qs(url.query)["locale"],["enUS"])
            table=url.path.split("/")[-2]
            self.assertIn(table,web.environment_build.wago_snapshot.TABLES)
            calls.append(table)
            return Response(("ID,Name\n1,"+table+"\n").encode("utf8"))

        # Preserve the real original collector, insert its *documented*
        # internal-only external fixture seam, never a synthetic stage result.
        original=web.environment_build.collect_wago_new_season_source
        def controlled_external_only(**kwargs):
            return original(
                **kwargs,fetch=fixture_fetch,
                credentials={key:"" for key in
                             web.environment_build.discovery_stage.FIELDS})

        # Windows asyncio Proactor uses loopback socketpair() internally.
        # Restrict only non-loopback sockets; do not break TestClient itself.
        original_connect=socket.socket.connect
        def local_only_connect(sock,address):
            if (sock.family in (socket.AF_INET,socket.AF_INET6) and
                (not isinstance(address,tuple) or
                 address[0] not in ("127.0.0.1","::1","localhost"))):
                raise AssertionError("NETWORK_ESCAPE_FORBIDDEN")
            return original_connect(sock,address)
        with (
            mock.patch.object(
                web.environment_build,"collect_wago_new_season_source",
                side_effect=controlled_external_only) as collector,
            mock.patch.object(socket.socket,"connect",new=local_only_connect),
            mock.patch.object(
                self.app.state.jobs,"plan",
                side_effect=AssertionError("DPS_PLAN_FORBIDDEN")),
        ):
            first=self.post("/api/v1/environment/season-build",
                            {"game_build":build,"target_ilevel":334})
            second=self.post("/api/v1/environment/season-build",
                             {"game_build":build,"target_ilevel":334})
            self.assertEqual(collector.call_count,2)

        self.assertEqual(first.status_code,200,first.text)
        self.assertEqual(second.status_code,200,second.text)
        one,two=first.json(),second.json()
        self.assertEqual(len(calls),len(web.environment_build.wago_snapshot.TABLES))
        self.assertEqual(set(calls),set(web.environment_build.wago_snapshot.TABLES))
        self.assertEqual(one["source_stage"]["status"],"EXECUTED_AND_SEALED")
        self.assertEqual(two["source_stage"]["status"],"REUSED_VERIFIED")
        self.assertEqual(one["network_calls_by_stage"],
                         len(web.environment_build.wago_snapshot.TABLES))
        self.assertEqual(two["network_calls_by_stage"],0)
        self.assertEqual(one["snapshot_receipt_path"],
                         two["snapshot_receipt_path"])
        for result in (one,two):
            self.assertTrue(result["normal_build_entry"])
            scope=result["web_environment_scope"]
            self.assertFalse(scope["dps_optimization_started"])
            self.assertFalse(scope["user_character_or_trinkets_required"])
            self.assertFalse(scope["environment_installed"])
            self.assertFalse(scope["environment_ready"])
            self.assertEqual(result["native_calls"],0)
            self.assertTrue(result["zero_history_build"]["requires"])
            self.assertFalse(result["zero_history_build"]["user_session_created"])
        self.assertFalse((workspace/"manifest.json").exists())
        self.assertFalse((workspace/"data").exists())
        self.assertFalse((workspace/"runs").exists())
        stage=workspace/"_fresh_season_sources"/("wago_"+build)
        self.assertTrue((stage/".stage_receipts"/"fresh-wago-db2.json").is_file())
        self.assertEqual(len(list(stage.rglob("*.csv"))),
                         len(web.environment_build.wago_snapshot.TABLES))

    def test_v338_required_db2_missing_mid_fetch_fail_closed_then_recovery(self):
        """Real v161+v217+v216+web path, injected external Wago response only.

        A missing mandatory table never becomes READY, an interrupted RUNNING
        receipt is not cache approval, recovery refetches and seals all tables,
        and a third identical request is a zero-fetch source reuse.
        """
        import io
        import socket
        from urllib.parse import parse_qs, urlsplit
        build="12.2.0.99999"  # fixture-only identity, NOT real season proof
        missing="MapChallengeMode"
        attempts=[]
        fault=[True]
        class Response(io.BytesIO):
            def __init__(self,data,status=200):
                super().__init__(data)
                self.status=status
            def __enter__(self):return self
            def __exit__(self,*args):self.close()
        def external(req,timeout):
            url=urlsplit(req.full_url)
            self.assertEqual(url.hostname,"wago.tools")
            self.assertEqual(parse_qs(url.query)["build"],[build])
            table=url.path.split("/")[-2]
            self.assertIn(table,web.environment_build.wago_snapshot.TABLES)
            attempts.append(table)
            if fault[0] and table==missing:
                return Response(b"",503)
            return Response(("ID,Name\n1,"+table+"\n").encode("utf8"))
        original=web.environment_build.collect_wago_new_season_source
        def collector(**kwargs):
            return original(
                **kwargs,fetch=external,
                credentials={name:"" for name in
                             web.environment_build.discovery_stage.FIELDS})
        original_connect=socket.socket.connect
        def block_nonloopback(sock,address):
            if sock.family in (socket.AF_INET,socket.AF_INET6) and (
                not isinstance(address,tuple) or
                address[0] not in ("127.0.0.1","::1","localhost")):
                raise AssertionError("NO_EXTERNAL_NETWORK_IN_NEGATIVE_TEST")
            return original_connect(sock,address)
        with (mock.patch.object(web.environment_build,
                                "collect_wago_new_season_source",
                                side_effect=collector),
              mock.patch.object(socket.socket,"connect",
                                new=block_nonloopback),
              mock.patch.object(self.app.state.jobs,"plan",
                                side_effect=AssertionError("NO_DPS_PLAN"))):
            first=self.post("/api/v1/environment/season-build",
                            {"game_build":build,"target_ilevel":334})
            self.assertEqual(first.status_code,422,first.text)
            self.assertEqual(first.json()["detail"]["code"],
                             "V216_FRESH_WAGO_SOURCE_FETCH_UNAVAILABLE")
            root=self.root/"runs"/"_fresh_season_sources"/("wago_"+build)
            stage=root/".stage_receipts"/"fresh-wago-db2.json"
            self.assertTrue(stage.is_file())
            self.assertEqual(json.loads(stage.read_text())["status"],"RUNNING")
            self.assertFalse((root/"wago"/"receipt.json").exists())
            self.assertEqual(len(attempts),
                             web.environment_build.wago_snapshot.TABLES.index(
                                 missing)+1)
            self.assertFalse(list(root.glob("fresh_source/v212_installed_*.json")))
            self.assertFalse(list(root.glob("fresh_source/v113_profile_*.json")))
            self.assertFalse((self.root/"runs"/"manifest.json").exists())
            fault[0]=False
            before=len(attempts)
            second=self.post("/api/v1/environment/season-build",
                             {"game_build":build,"target_ilevel":334})
            self.assertEqual(second.status_code,200,second.text)
            self.assertEqual(len(attempts)-before,
                             len(web.environment_build.wago_snapshot.TABLES))
            body=second.json()
            self.assertEqual(body["source_stage"]["status"],
                             "EXECUTED_AND_SEALED")
            self.assertFalse(body["environment_ready"])
            self.assertFalse(body["environment_installed"])
            self.assertEqual(body["native_calls"],0)
            self.assertTrue(body["zero_history_build"]["requires"])
            self.assertEqual(json.loads(stage.read_text())["status"],"COMPLETE")
            before=len(attempts)
            third=self.post("/api/v1/environment/season-build",
                            {"game_build":build,"target_ilevel":334})
            self.assertEqual(third.status_code,200,third.text)
            self.assertEqual(third.json()["source_stage"]["status"],
                             "REUSED_VERIFIED")
            self.assertEqual(len(attempts),before)
            self.assertEqual(third.json()["native_calls"],0)
            self.assertFalse(third.json()["environment_ready"])
            self.assertFalse(list(root.glob("fresh_source/v212_installed_*.json")))
            correction=self.post("/api/v1/environment/season-build",
                {"game_build":build,"target_ilevel":334,
                 "refresh_reason":"item_content_change"})
            self.assertEqual(correction.status_code,422,correction.text)
            self.assertEqual(correction.json()["detail"]["code"],
                "SAME_BUILD_CONTENT_CHANGE_EXACT_SOURCE_CORRECTION_REQUIRED")
            self.assertEqual(len(attempts),before)
            self.assertEqual(json.loads(stage.read_text())["status"],"COMPLETE")

    def test_controlled_cold_start_corrupted_source_not_silently_refetched(self):
        """P3-DS T0 tamper: original v217 must reject changed source bytes."""
        import io
        import socket
        from urllib.parse import urlsplit

        build="12.2.0.99999"
        calls=[]

        class Response(io.BytesIO):
            status=200
            def __enter__(self):return self
            def __exit__(self,*exc):self.close()

        def fixture_fetch(req,timeout):
            table=urlsplit(req.full_url).path.split("/")[-2]
            self.assertIn(table,web.environment_build.wago_snapshot.TABLES)
            calls.append(table)
            return Response(("ID,Name\n1,"+table+"\n").encode("utf8"))

        original=web.environment_build.collect_wago_new_season_source
        def controlled_external_only(**kwargs):
            return original(
                **kwargs,fetch=fixture_fetch,
                credentials={key:"" for key in
                             web.environment_build.discovery_stage.FIELDS})

        original_connect=socket.socket.connect
        def local_only_connect(sock,address):
            if (sock.family in (socket.AF_INET,socket.AF_INET6) and
                (not isinstance(address,tuple) or
                 address[0] not in ("127.0.0.1","::1","localhost"))):
                raise AssertionError("NETWORK_ESCAPE_FORBIDDEN")
            return original_connect(sock,address)
        with (
            mock.patch.object(
                web.environment_build,"collect_wago_new_season_source",
                side_effect=controlled_external_only),
            mock.patch.object(socket.socket,"connect",new=local_only_connect),
        ):
            first=self.post("/api/v1/environment/season-build",
                            {"game_build":build,"target_ilevel":334})
            self.assertEqual(first.status_code,200,first.text)
            artifact=(self.root/"runs"/"_fresh_season_sources"/
                      ("wago_"+build)/"wago"/"Item.csv")
            self.assertTrue(artifact.is_file())
            artifact.write_bytes(b"CORRUPTED_SOURCE")
            second=self.post("/api/v1/environment/season-build",
                             {"game_build":build,"target_ilevel":334})

        self.assertEqual(second.status_code,422,second.text)
        self.assertEqual(second.json()["detail"]["code"],
                         "V216_FRESH_WAGO_STAGE_BLOCKED")
        self.assertEqual(len(calls),len(web.environment_build.wago_snapshot.TABLES))
        self.assertEqual(artifact.read_bytes(),b"CORRUPTED_SOURCE")

    def test_v350_user_socket_and_flask_variants_fail_closed_before_session(self):
        """An uninstalled individual layout may not reuse a historical v213 B/T."""
        inputs=(
            ({"user_socket_total":8},"WEB_USER_VARIANT_REQUIRES_VERIFIED_SEASON_INSTALL"),
            ({"user_socket_total":5,"user_special_gem_id":240983},
             "WEB_USER_VARIANT_REQUIRES_VERIFIED_SEASON_INSTALL"),
            ({"user_socket_total":4,"selected_flask_item_id":241326},
             "WEB_USER_VARIANT_REQUIRES_VERIFIED_SEASON_INSTALL"),
            ({"user_socket_total":4,"user_special_gem_id":240983},
             "WEB_USER_TOTAL_SOCKETS_INCLUDE_SPECIAL_INVALID"),
        )
        with mock.patch.object(web.subprocess,"Popen",
                               side_effect=AssertionError("NATIVE_FORBIDDEN")):
            for choice,expected in inputs:
                reply=self.post("/api/v1/sessions/plan",
                                {**self.payload,"current_season_product":True,
                                 **choice})
                self.assertEqual(reply.status_code,422,reply.text)
                self.assertEqual(reply.json()["detail"]["code"],expected)
        self.assertFalse((self.root/"runs").exists())

    def test_v350_verified_gem_snapshot_exact_socket_special_match(self):
        """A source gem layout is not a universal season-wide J/SimC profile."""
        observed={"source_compilation":{"physical_gem_layout_unadmitted":{
            "schema":"v271_user_socket_gem_layout_stage_v1",
            "status":"PHYSICAL_GEMS_STAGED_SOURCE_AND_SOCKET_PROOFS_PENDING",
            "socket_total":8,"special_gem_id":240983,
            "ordinary_gem_ids":[201,202,203,204,201,202,203]}}}
        checker=web._verified_snapshot_gem_layout_matches
        self.assertTrue(checker(observed,special_gem_id=240983,
                                socket_total=8))
        for want in ({"special_gem_id":None,"socket_total":8},
                     {"special_gem_id":240983,"socket_total":7},
                     {"special_gem_id":None,"socket_total":4}):
            self.assertFalse(checker(observed,**want))
        self.assertFalse(checker({},special_gem_id=None,socket_total=4))

    def test_web_season_environment_build_no_dps_inputs_and_no_native(self):
        payload={"game_build":"12.2.0.99999","target_ilevel":334}
        source={"status":"FRESH_WAGO_DB2_COLLECTED_MORE_SOURCES_PENDING",
                "environment_ready":False,"environment_installed":False,
                "native_calls":0,"source_stage":{"status":"REUSED_VERIFIED"},
                "source_compilation":{"status":"SOURCE_COMPILER_PENDING"},
                "zero_history_build":{"requires":["GJFO_PENDING"],
                                      "environment_ready":False}}
        with mock.patch.object(web.environment_build,"build_environment",
                               return_value=source) as stage, \
             mock.patch.object(self.app.state.jobs,"plan",
                               side_effect=AssertionError("DPS_PLAN_FORBIDDEN")):
            response=self.post("/api/v1/environment/season-build",payload)
        self.assertEqual(response.status_code,200,response.text)
        result=response.json()
        self.assertEqual(result["status"],source["status"])
        self.assertFalse(result["web_environment_scope"]["environment_ready"])
        self.assertFalse(result["web_environment_scope"]["environment_installed"])
        self.assertFalse(result["web_environment_scope"]["dps_optimization_started"])
        self.assertFalse(result["web_environment_scope"]["user_character_or_trinkets_required"])
        self.assertFalse(result["web_environment_scope"]["local_native_G_requested"])
        self.assertTrue(result["web_environment_scope"]["four_stat_ordinary_source_requested"])
        self.assertTrue(result["web_environment_scope"]["four_stat_ordinary_default_requested"])
        kwargs=stage.call_args.kwargs
        self.assertIsNone(kwargs["user"])
        self.assertIsNone(kwargs["binary"])
        self.assertIsNone(kwargs["session_folder"])
        self.assertIsNone(kwargs["bootstrap_result"])
        self.assertEqual(kwargs["fresh_collection_inputs"],{
            "expected_game_build":"12.2.0.99999",
            "representative_request":{"class":"paladin","spec":"retribution",
                                      "target_ilevel":334},
            "g_probe_character":{"race":"dwarf"},"simc_revision_hint":None,
            "auto_native_F_requested":False,
            "auto_native_O_requested":False,
            "auto_native_G_requested":False,
            "auto_four_stat_source_requested":True,
            "source_selected_gem_roles":{
                "special_gem_id":None,"ordinary_gem_ids":None},
            "source_target_socket_count":4})
        self.assertFalse((self.root/"runs").exists())


    def test_normal_four_gems_refuse_old_special_profile_reuse(self):
        """A matching build/ilevel/O does not prove a matching gem layout."""
        def snapshot(special, count, ids):
            return {"source_compilation":{"physical_gem_layout_unadmitted":{
                "schema":"v271_user_socket_gem_layout_stage_v1",
                "status":"PHYSICAL_GEMS_STAGED_SOURCE_AND_SOCKET_PROOFS_PENDING",
                "special_gem_id":special,"socket_total":count,
                "ordinary_gem_ids":ids}}}
        good=snapshot(None,4,[101,102,103,104])
        legacy=snapshot(240967,5,[101,102,103,104])
        self.assertTrue(web._verified_snapshot_gem_layout_matches(
            good,special_gem_id=None,socket_total=4))
        self.assertFalse(web._verified_snapshot_gem_layout_matches(
            legacy,special_gem_id=None,socket_total=4))
        self.assertFalse(web._verified_snapshot_gem_layout_matches(
            good,special_gem_id=None,socket_total=6))
        self.assertTrue(web._verified_snapshot_gem_layout_matches(
            legacy,special_gem_id=240967,socket_total=5))
        # The older variant HAS a saved profile; it must not be treated as
        # a four-ordinary default when its authenticated socket layout differs.
        profile=(self.app.state.jobs.root/"_fresh_season_sources"/
                 "wago_12.2.0.99999"/"fresh_source"/
                 ("v113_profile_"+("a"*20)+".json"))
        profile.parent.mkdir(parents=True,exist_ok=True)
        profile.write_text("OLD_SPECIAL_PROFILE",encoding="utf8")
        source={"status":"SOURCE_ONLY_PENDING","environment_ready":False,
                "environment_installed":False,"native_calls":0}
        installed={"status":"VERIFIED_INSTALLED_SAME_SEASON_SOURCE_REUSED",
                   "environment_ready":True,"environment_installed":True,
                   "installed_manifest_sha256":"a"*64}
        with mock.patch.object(web.environment_build,
                "find_verified_installed_season_environment",
                return_value=installed), mock.patch.object(
                self.app.state.jobs,"restore_verified_fresh_profile",
                return_value=None) as restore, mock.patch.object(
                web.environment_build,"build_environment",
                return_value=source) as original_build:
            response=self.post("/api/v1/environment/season-build",{
                "game_build":"12.2.0.99999","target_ilevel":334})
        self.assertEqual(response.status_code,200,response.text)
        self.assertFalse(response.json()["web_environment_scope"][
            "environment_ready"])
        restore.assert_called_once_with(
            target_ilevel=334,game_build="12.2.0.99999",
            required_gem_layout={"special_gem_id":None,"socket_total":4})
        original_build.assert_called_once()

    def test_p1_first_install_core_reuses_original_g_f_stages(self):
        """Automatic cold-start selection calls original Build, not a new engine."""
        payload={"game_build":"12.2.0.99999","target_ilevel":334,
                 "auto_initial_core_build":True,
                 "auto_initial_core_simc_binary":str(self.binary)}
        source={"status":"SOURCE_ONLY_PENDING","environment_ready":False,
                "environment_installed":False,"native_calls":0}
        with mock.patch.object(web.environment_build,"build_environment",
                               return_value=source) as build:
            response=self.post("/api/v1/environment/season-build",payload)
        self.assertEqual(response.status_code,200,response.text)
        params=build.call_args.kwargs
        self.assertEqual(params["binary"],self.binary.resolve())
        self.assertIsNone(params["user"])
        fresh=params["fresh_collection_inputs"]
        self.assertTrue(fresh["auto_native_G_requested"])
        self.assertTrue(fresh["auto_native_F_requested"])
        self.assertTrue(fresh["auto_select_observed_F_no_oil"])
        self.assertTrue(fresh["auto_four_stat_source_requested"])
        self.assertNotIn("selected_budget_items",fresh)
        self.assertTrue(response.json()["web_environment_scope"][
            "auto_initial_core_build_requested"])
        self.assertFalse(response.json()["web_environment_scope"][
            "environment_ready"])

        with mock.patch.object(
                web.environment_build,"find_verified_installed_season_environment",
                return_value={
                    "status":"VERIFIED_INSTALLED_SAME_SEASON_SOURCE_REUSED",
                    "environment_ready":True,"environment_installed":True,
                    "installed_manifest_sha256":"a"*64}) as prior, \
             mock.patch.object(
                 self.app.state.jobs,"restore_verified_fresh_profile",
                 return_value={"status":"REUSED"}) as restore, \
             mock.patch.object(
                 web.environment_build,"build_environment",
                 side_effect=AssertionError("NO_SOURCE_NATIVE_OR_DPS")) as build:
            cached=self.post("/api/v1/environment/season-build",{
                **payload,"auto_initial_core_simc_binary":
                    str(self.root/"missing.exe")})
        self.assertEqual(cached.status_code,200,cached.text)
        self.assertTrue(cached.json()["web_environment_scope"][
            "auto_initial_core_native_skipped_existing_ready"])
        build.assert_not_called()
        prior.assert_called_once()
        restore.assert_called_once()

        for update in (
            {"auto_initial_core_simc_binary":None},
            {"auto_initial_core_simc_binary":str(self.root/"missing.exe")},
            {"selected_flask_item_id":241326},
            {"auto_native_F_requested":True}):
            with self.subTest(update=update),mock.patch.object(
                    web.environment_build,"build_environment",
                    side_effect=AssertionError("NO_SOURCE")) as stage:
                rejected=self.post("/api/v1/environment/season-build",
                                   {**payload,**update})
                self.assertEqual(rejected.status_code,422,rejected.text)
                stage.assert_not_called()
        with mock.patch.object(web.environment_build,"build_environment",
                               side_effect=AssertionError("NO_SOURCE")) as stage:
            stray=self.post("/api/v1/environment/season-build",{
                "game_build":"12.2.0.99999",
                "auto_initial_core_simc_binary":str(self.binary)})
            self.assertEqual(stray.status_code,422,stray.text)
            stage.assert_not_called()

    def test_p1_explicit_installed_build_separate_from_source_collection(self):
        """Exact build is carried through short and long-run plans, no Native.

        Build X must not silently use in-memory/default Y or packaged legacy.
        The existing fresh_season_build field remains source-collection-only.
        """
        jobs=self.app.state.jobs
        build="12.1.5.70529"
        rejected=self.post("/api/v1/sessions/plan",{
            **self.payload,"installed_season_game_build":build})
        self.assertEqual(rejected.status_code,422,rejected.text)
        self.assertEqual(rejected.json()["detail"]["code"],
                         "WEB_INSTALLED_SEASON_SELECTION_REQUIRES_CURRENT_PRODUCT")
        self.assertEqual(self.post("/api/v1/sessions/plan",{
            **self.payload,"current_season_product":True,
            "installed_season_game_build":"broken"}).status_code,422)
        # A user-requested installed build must fail closed when there is
        # no matching v113/v212 snapshot; cannot fall back to packaged.
        pinned={**self.payload,"current_season_product":True,
                "installed_season_game_build":build}
        with (mock.patch.object(jobs,"load_fresh_profile_for_user",
                                return_value=None) as loader,
              mock.patch.object(web.retail_build_source,"discover",
                                side_effect=AssertionError("NO_LIVE_LOOKUP")),
              mock.patch.object(web.subprocess,"Popen",
                                side_effect=AssertionError("NO_NATIVE"))):
            missing=self.post("/api/v1/sessions/plan",pinned)
        self.assertEqual(missing.status_code,422,missing.text)
        self.assertEqual(missing.json()["detail"]["code"],
                         "WEB_SELECTED_INSTALLED_SEASON_BUILD_NOT_FOUND")
        loader.assert_called_once_with(
            self.controls["ilevel"],build,
            selected_oil_hands=self.controls["oil_hands"],
            selected_oil_item_ids_by_hand=None)
        # Long-running prepare must forward the same explicit build rather
        # than dropping it when mapping to the shared UserRequest.
        long_request={**pinned,"max_native_calls":12}
        with (mock.patch.object(jobs,"load_fresh_profile_for_user",
                                return_value=None) as long_loader,
              mock.patch.object(web.retail_build_source,"discover",
                                side_effect=AssertionError("NO_LIVE_LOOKUP")),
              mock.patch.object(web.subprocess,"Popen",
                                side_effect=AssertionError("NO_NATIVE"))):
            long_missing=self.post("/api/v1/longrun/prepare",long_request)
        self.assertEqual(long_missing.status_code,422,long_missing.text)
        self.assertEqual(long_missing.json()["detail"]["code"],
                         "WEB_SELECTED_INSTALLED_SEASON_BUILD_NOT_FOUND")
        long_loader.assert_called_once_with(
            self.controls["ilevel"],build,
            selected_oil_hands=self.controls["oil_hands"],
            selected_oil_item_ids_by_hand=None)
        self.assertEqual(self.post("/api/v1/sessions/plan",{
            **pinned,"fresh_season_build":build}).status_code,422)

    def test_p3_fy_web_reuse_requires_exact_request_or_live_build(self):
        installed={"status":"VERIFIED_INSTALLED_SAME_SEASON_SOURCE_REUSED",
                   "environment_ready":True,"environment_installed":True,
                   "installed_source_game_build":"12.1.5.70529",
                   "installed_source_simc_revision":"a"*40,
                   "G":2800,"J":140,"F":170,"O":{},
                   "B":3110,"T":3110,"native_calls":0,"network_calls":0}
        # Explicit pinned build: sealed source reuse requires NO remote
        # version lookup and reuses the original static season identity.
        with mock.patch.object(web.environment_build,
                "find_verified_installed_season_environment",
                return_value=installed) as reuse, \
             mock.patch.object(web.retail_build_source,"discover",
                side_effect=AssertionError("NO_POLL_FOR_EXPLICIT_BUILD")), \
             mock.patch.object(web.environment_build,"build_environment",
                side_effect=AssertionError("DO_NOT_RECOLLECT_ON_REUSE")):
            response=self.post("/api/v1/environment/season-build",{
                "game_build":"12.1.5.70529"})
        self.assertEqual(response.status_code,200,response.text)
        self.assertTrue(response.json()["environment_ready"])
        self.assertEqual(response.json()["web_environment_scope"][
            "game_build_source"],"PREVIOUS_V217_VERIFIED_INSTALL")
        self.assertEqual(response.json()["web_environment_scope"][
            "game_build_resolution"],"EXPLICIT_GAME_BUILD")
        self.assertEqual(response.json()["web_environment_scope"][
            "network_calls"],0)
        reuse.assert_called_once_with(
            self.app.state.jobs.root,334,expected_game_build="12.1.5.70529")
        # Normal user with no build gets the exact live build identity first.
        live={"game_build":"12.1.5.70529","source_sha256":"a"*64}
        with mock.patch.object(web.retail_build_source,"discover",
                return_value=live) as discovery, \
             mock.patch.object(web.environment_build,
                "find_verified_installed_season_environment",
                return_value=installed) as reuse, \
             mock.patch.object(web.environment_build,"build_environment",
                side_effect=AssertionError("NO_RECOLLECTION_ON_SAME_BUILD")):
            current=self.post("/api/v1/environment/season-build",{})
        self.assertEqual(current.status_code,200,current.text)
        discovery.assert_called_once_with(region="KR")
        reuse.assert_called_once_with(
            self.app.state.jobs.root,334,expected_game_build="12.1.5.70529")
        current_scope=current.json()["web_environment_scope"]
        self.assertTrue(current_scope["active_season_reverified_in_this_lookup"])
        self.assertEqual(current_scope["retail_version_network_calls"],1)
        self.assertEqual(current_scope["retail_build_source_sha256"],"a"*64)
        self.assertEqual(current.json()["network_calls"],1)
        with mock.patch.object(web.environment_build,
                "find_verified_installed_season_environment",
                side_effect=AssertionError("REFRESH_CANNOT_REUSE")), \
             mock.patch.object(web.environment_build,"build_environment",
                return_value={"status":"SOURCE_PENDING","environment_ready":False}):
            fresh=self.post("/api/v1/environment/season-build",{
                "game_build":"12.1.5.70783",
                "refresh_reason":"season_change"})
        self.assertEqual(fresh.status_code,200,fresh.text)
        self.assertFalse(fresh.json()["web_environment_scope"][
            "environment_ready"])
        with mock.patch.object(web.environment_build,
                "find_verified_installed_season_environment",
                side_effect=AssertionError("SELECTED_F_CANNOT_REUSE")), \
             mock.patch.object(web.environment_build,"build_environment",
                return_value={"status":"SOURCE_PENDING","environment_ready":False}):
            item=self.post("/api/v1/environment/season-build",{
                "game_build":"12.1.5.70783","selected_flask_item_id":241326})
        self.assertEqual(item.status_code,200,item.text)
        self.assertEqual(self.post("/api/v1/environment/season-build",{
            "refresh_reason":"simc_update"}).status_code,422)
        receipt=(self.app.state.jobs.root/"_fresh_season_sources"/
                 "wago_12.1.5.70783"/".stage_receipts"/"fresh-wago-db2.json")
        receipt.parent.mkdir(parents=True)
        receipt.write_text("SEALED_HISTORY",encoding="utf8")
        with mock.patch.object(web.environment_build,"build_environment",
                side_effect=AssertionError("NO_STALE_SNAPSHOT")):
            changed=self.post("/api/v1/environment/season-build",{
                "game_build":"12.1.5.70783",
                "refresh_reason":"item_content_change"})
        self.assertEqual(changed.status_code,422,changed.text)
        self.assertEqual(changed.json()["detail"]["code"],
                         "SAME_BUILD_CONTENT_CHANGE_EXACT_SOURCE_CORRECTION_REQUIRED")

    def test_a1_same_build_season_expansion_refresh_never_reuses_prior_source(self):
        """A1: event identity cannot silently reuse an old sealed build-only stage.

        No external HTTP, no Native, no source overwrite. A genuinely new
        game build must still enter the existing v216 cold source path.
        """
        build="12.1.5.70783"
        stage=(self.app.state.jobs.root/"_fresh_season_sources"/
               ("wago_"+build)/".stage_receipts"/"fresh-wago-db2.json")
        stage.parent.mkdir(parents=True)
        original=b'PRIOR_SEALED_SEASON_SOURCE_RECEIPT_UNTOUCHED'
        stage.write_bytes(original)
        for event in ("season_change","expansion_change"):
            with self.subTest(event=event), \
                 mock.patch.object(web.environment_build,"build_environment",
                     side_effect=AssertionError("STALE_BUILD_SOURCE_NOT_REUSED")) as b, \
                 mock.patch.object(web.retail_build_source,"discover",
                     side_effect=AssertionError("EXPLICIT_BUILD_NO_DISCOVERY")):
                resp=self.post("/api/v1/environment/season-build",{
                    "game_build":build,"refresh_reason":event})
            self.assertEqual(resp.status_code,422,resp.text)
            self.assertEqual(resp.json()["detail"]["code"],
                "SAME_BUILD_SEASON_EVENT_EXACT_SOURCE_REFRESH_REQUIRED")
            b.assert_not_called()
            self.assertEqual(stage.read_bytes(),original)
        pending={"status":"SOURCE_PENDING","environment_ready":False,
                 "environment_installed":False,"native_calls":0}
        changed_build="12.1.5.70784"
        with mock.patch.object(web.environment_build,"build_environment",
                               return_value=pending) as b:
            fresh=self.post("/api/v1/environment/season-build",{
                "game_build":changed_build,"refresh_reason":"season_change"})
        self.assertEqual(fresh.status_code,200,fresh.text)
        self.assertFalse(fresh.json()["web_environment_scope"][
            "environment_ready"])
        self.assertEqual(b.call_args.kwargs["fresh_collection_inputs"][
            "expected_game_build"],changed_build)
        self.assertEqual(stage.read_bytes(),original)

    def test_p3_hl_different_active_build_cannot_reuse_cached_environment(self):
        """A new live patch must enter the existing season builder, not old READY."""
        current={"game_build":"12.1.5.70783","source_sha256":"c"*64}
        fresh={"status":"FRESH_SOURCE_PENDING",
               "environment_ready":False,
               "environment_installed":False,"native_calls":0}
        with mock.patch.object(web.retail_build_source,"discover",
                               return_value=current) as discover, \
             mock.patch.object(web.environment_build,
                 "find_verified_installed_season_environment",
                 return_value=None) as reuse, \
             mock.patch.object(web.environment_build,"build_environment",
                               return_value=fresh) as build:
            response=self.post("/api/v1/environment/season-build",{})
        self.assertEqual(response.status_code,200,response.text)
        discover.assert_called_once_with(region="KR")
        reuse.assert_called_once_with(self.app.state.jobs.root,334,
            expected_game_build="12.1.5.70783")
        self.assertEqual(build.call_args.kwargs["fresh_collection_inputs"][
            "expected_game_build"],"12.1.5.70783")
        self.assertFalse(response.json()["environment_ready"])
        self.assertEqual(response.json()["web_environment_scope"][
            "retail_version_network_calls"],1)
        # Explicit pinned build allows an offline check but never scans or
        # reuses the numerically closest or most recent installed patch.
        with mock.patch.object(web.retail_build_source,"discover",
                side_effect=AssertionError("EXPLICIT_NO_DISCOVERY")), \
             mock.patch.object(web.environment_build,
                "find_verified_installed_season_environment",
                return_value=None) as reuse, \
             mock.patch.object(web.environment_build,"build_environment",
                return_value=fresh):
            pinned=self.post("/api/v1/environment/season-build",{
                "game_build":"12.1.5.70783"})
        self.assertEqual(pinned.status_code,200,pinned.text)
        reuse.assert_called_once_with(self.app.state.jobs.root,334,
            expected_game_build="12.1.5.70783")
        self.assertFalse(pinned.json()["environment_ready"])

    def test_p3_fr_zero_base_build_auto_retail_version_from_public_source(self):
        # No user-supplied game_build, historical ID, or client secrets.
        observed={"status":"FRESH_SOURCE_PENDING","environment_ready":False,
                  "environment_installed":False,"native_calls":0}
        discovered={"game_build":"12.1.5.70783",
                    "source_sha256":"5"*64}
        with mock.patch.object(web.retail_build_source,"discover",
                               return_value=discovered) as source, \
             mock.patch.object(web.environment_build,"build_environment",
                               return_value=observed) as build:
            result=self.post("/api/v1/environment/season-build",{
                "target_ilevel":334})
        self.assertEqual(result.status_code,200,result.text)
        source.assert_called_once_with(region="KR")
        args=build.call_args.kwargs
        self.assertEqual(args["fresh_collection_inputs"][
            "expected_game_build"],"12.1.5.70783")
        self.assertIsNone(args["binary"])
        self.assertEqual(args["fresh_collection_inputs"][
            "source_selected_gem_roles"],{
                "special_gem_id":None,"ordinary_gem_ids":None})
        self.assertEqual(args["fresh_collection_inputs"][
            "source_target_socket_count"],4)
        self.assertNotIn("selected_budget_items",
                         args["fresh_collection_inputs"])
        scope=result.json()["web_environment_scope"]
        self.assertEqual(scope["game_build"],"12.1.5.70783")
        self.assertEqual(scope["game_build_source"],
                         "BLIZZARD_PUBLIC_RETAIL_KR")
        self.assertEqual(scope["retail_build_source_sha256"],"5"*64)
        self.assertFalse(scope["environment_ready"])
        with mock.patch.object(web.retail_build_source,"discover",
               side_effect=web.retail_build_source.RetailVersionBlocked(
                   "RETAIL_VERSION_LIVE_SOURCE_UNAVAILABLE")) as source, \
             mock.patch.object(web.environment_build,"build_environment",
                               side_effect=AssertionError("NEVER_RUN")) as build:
            fail=self.post("/api/v1/environment/season-build",{})
        self.assertEqual(fail.status_code,422,fail.text)
        self.assertEqual(fail.json()["detail"]["code"],
                         "RETAIL_VERSION_LIVE_SOURCE_UNAVAILABLE")
        build.assert_not_called()
        source.assert_called_once()
        with mock.patch.object(web.retail_build_source,"discover",
                  side_effect=AssertionError("NOT_FOR_EXPLICIT")):
            with mock.patch.object(web.environment_build,"build_environment",
                                   return_value=observed):
                explicit=self.post("/api/v1/environment/season-build",{
                    "game_build":"12.2.0.99999"})
            self.assertEqual(explicit.status_code,200,explicit.text)
            self.assertEqual(explicit.json()["web_environment_scope"][
                "game_build_source"],"EXPLICIT_GAME_BUILD")

    def test_p3_fo_web_reuses_existing_special_for_four_ordinary_no_effect_gate(self):
        payload={"game_build":"12.2.0.99999","target_ilevel":334,
                 "existing_special_gem_id":311200}
        stub={"status":"SOURCE_ONLY_PENDING","environment_ready":False,
              "environment_installed":False,"native_calls":0}
        with mock.patch.object(web.environment_build,"build_environment",
                               return_value=stub) as build:
            response=self.post("/api/v1/environment/season-build",payload)
        self.assertEqual(response.status_code,200,response.text)
        kwargs=build.call_args.kwargs
        self.assertIsNone(kwargs["user"])
        self.assertIsNone(kwargs["binary"])
        self.assertEqual(kwargs["fresh_collection_inputs"][
            "source_selected_gem_roles"],{
                "special_gem_id":311200,"ordinary_gem_ids":None})
        self.assertTrue(response.json()["web_environment_scope"][
            "four_stat_ordinary_default_requested"])
        self.assertFalse(response.json()["web_environment_scope"][
            "special_gem_effect_verified_here"])
        self.assertFalse(response.json()["web_environment_scope"][
            "environment_ready"])
        for bad in (0,-1,"not-an-id",1000000000):
            response=self.post("/api/v1/environment/season-build",{
                **payload,"existing_special_gem_id":bad})
            self.assertEqual(response.status_code,422,response.text)

    def test_p3_hj_web_build_automatically_supplies_same_build_nominal_J(self):
        """Source-only item totals enter original v216, never user input."""
        stub={"status":"SOURCE_ONLY_PENDING","environment_ready":False,
              "environment_installed":False,"native_calls":0}
        with mock.patch.object(web.environment_build,"build_environment",
                               return_value=stub) as build:
            response=self.post("/api/v1/environment/season-build",{
                "game_build":"12.1.5.70783",
                "existing_special_gem_id":240967,
                "source_target_socket_count":7})
        self.assertEqual(response.status_code,200,response.text)
        inputs=build.call_args.kwargs["fresh_collection_inputs"]
        nominal=inputs["source_ordinary_nominal_by_stat"]
        self.assertEqual(nominal["game_build"],"12.1.5.70783")
        self.assertEqual({row["rating"] for row in
                          nominal["by_stat"].values()},{23})
        scope=response.json()["web_environment_scope"]
        self.assertTrue(scope["ordinary_nominal_source_only_not_approved"])
        self.assertEqual(scope["ordinary_nominal_source_sha256"],
                         nominal["source_sha256"])
        self.assertFalse(scope["environment_ready"])
        with mock.patch.object(web.environment_build,"build_environment",
                               return_value=stub) as future:
            next_build=self.post("/api/v1/environment/season-build",{
                "game_build":"12.2.0.99999",
                "existing_special_gem_id":240967})
        self.assertEqual(next_build.status_code,200,next_build.text)
        self.assertNotIn("source_ordinary_nominal_by_stat",
                         future.call_args.kwargs["fresh_collection_inputs"])
        self.assertIsNone(next_build.json()["web_environment_scope"][
            "ordinary_nominal_source_sha256"])
    def test_p3_gy_declared_socket_count_web_to_original_v216(self):
        """The web passes user N to v216, without inferring socket proofs."""
        stub={"status":"J_SIMC_DECLARED_FULL_GEM_PROFILE_SOURCE_ONLY",
              "environment_ready":False,"environment_installed":False,
              "native_calls":0}
        for n in (5,7,8,64):
            with self.subTest(n=n), mock.patch.object(
                    web.environment_build,"build_environment",
                    return_value=stub) as build:
                response=self.post("/api/v1/environment/season-build",{
                    "game_build":"12.1.5.70783",
                    "existing_special_gem_id":311200,
                    "source_target_socket_count":n})
                self.assertEqual(response.status_code,200,response.text)
                inputs=build.call_args.kwargs["fresh_collection_inputs"]
                self.assertEqual(inputs["source_target_socket_count"],n)
                self.assertEqual(inputs["source_selected_gem_roles"],{
                    "special_gem_id":311200,"ordinary_gem_ids":None})
                scope=response.json()["web_environment_scope"]
                self.assertEqual(scope["source_target_socket_count"],n)
                self.assertFalse(scope["declared_gem_profile_native_verified_here"])
                self.assertFalse(scope["environment_ready"])
        with mock.patch.object(web.environment_build,"build_environment",
                               return_value=stub) as build:
            default=self.post("/api/v1/environment/season-build",{
                "game_build":"12.1.5.70783",
                "existing_special_gem_id":311200})
            self.assertEqual(default.status_code,200,default.text)
            self.assertEqual(build.call_args.kwargs["fresh_collection_inputs"][
                "source_target_socket_count"],5)
        for bad in (0,4,65,-1,True,"bad"):
            with self.subTest(bad=bad), mock.patch.object(
                    web.environment_build,"build_environment",
                    side_effect=AssertionError("MUST_NOT_COLLECT")) as build:
                response=self.post("/api/v1/environment/season-build",{
                    "game_build":"12.1.5.70783",
                    "existing_special_gem_id":311200,
                    "source_target_socket_count":bad})
                self.assertEqual(response.status_code,422,response.text)
                build.assert_not_called()
        with mock.patch.object(web.environment_build,"build_environment",
                               return_value=stub) as build:
            ordinary_only=self.post("/api/v1/environment/season-build",{
                "game_build":"12.1.5.70783",
                "source_target_socket_count":4})
            self.assertEqual(ordinary_only.status_code,200,ordinary_only.text)
            self.assertEqual(build.call_args.kwargs["fresh_collection_inputs"][
                "source_selected_gem_roles"],{
                    "special_gem_id":None,"ordinary_gem_ids":None})
            self.assertEqual(build.call_args.kwargs["fresh_collection_inputs"][
                "source_target_socket_count"],4)

    def test_p3_fq_exact_F_and_four_stat_j_share_normal_web_build(self):
        payload={"game_build":"12.2.0.99999","target_ilevel":334,
                 "selected_flask_item_id":241326,
                 "existing_special_gem_id":311200,
                 "auto_native_F_requested":True,
                 "consumable_native_binary":str(self.binary)}
        source={"status":"SOURCE_ONLY_PENDING","environment_ready":False,
                "environment_installed":False,"native_calls":0}
        with mock.patch.object(web.environment_build,"build_environment",
                               return_value=source) as build_stage:
            response=self.post("/api/v1/environment/season-build",payload)
        self.assertEqual(response.status_code,200,response.text)
        kw=build_stage.call_args.kwargs
        self.assertIsNone(kw["user"])
        self.assertEqual(kw["binary"],self.binary.resolve())
        f=kw["fresh_collection_inputs"]
        self.assertTrue(f["auto_native_F_requested"])
        self.assertFalse(f["auto_native_G_requested"])
        self.assertEqual(f["selected_budget_items"],{
            "flask_item_id":241326,"oil_item_ids_by_hand":{}})
        self.assertEqual(f["source_selected_gem_roles"],{
            "special_gem_id":311200,"ordinary_gem_ids":None})
        scope=response.json()["web_environment_scope"]
        self.assertEqual(scope["selected_flask_item_id"],241326)
        self.assertTrue(scope["four_stat_ordinary_default_requested"])
        self.assertFalse(scope["special_gem_effect_verified_here"])
        self.assertFalse(scope["environment_ready"])
        with mock.patch.object(web.environment_build,"build_environment",
                               side_effect=AssertionError("MUST_NOT_RUN")) as no:
            result=self.post("/api/v1/environment/season-build",{
                **payload,"auto_select_observed_F_no_oil":True})
            self.assertEqual(result.status_code,422,result.text)
            no.assert_not_called()

    def test_p3_fg_web_flask_selection_reaches_real_source_verifier_only(self):
        payload={"game_build":"12.2.0.99999",
                 "target_ilevel":334,"selected_flask_item_id":241326}
        result={"status":"SOURCE_ONLY_PENDING",
                "environment_ready":False,"environment_installed":False,
                "native_calls":0}
        with mock.patch.object(web.environment_build,"build_environment",
                               return_value=result) as stage:
            response=self.post("/api/v1/environment/season-build",payload)
        self.assertEqual(response.status_code,200,response.text)
        inputs=stage.call_args.kwargs["fresh_collection_inputs"]
        self.assertEqual(inputs["selected_budget_items"],{
            "flask_item_id":241326,"oil_item_ids_by_hand":{}})
        self.assertNotIn("same_build_budget_evidence",inputs)
        self.assertNotIn("verified_install_input_provider",inputs)
        self.assertIsNone(stage.call_args.kwargs["user"])
        self.assertFalse(response.json()["web_environment_scope"][
            "environment_ready"])
        self.assertEqual(response.json()["web_environment_scope"][
            "selected_flask_item_id"],241326)
        self.assertTrue(response.json()["web_environment_scope"][
            "explicit_no_oil_with_selected_flask"])
        # The same season Build must also pass an explicit hand-selected
        # physical item ID to the original v216 source-owner engine.
        # HTTP never supplies an O rating, trusted receipt, or SimC token.
        oil_choice={"main_hand":243734}
        with mock.patch.object(web.environment_build,"build_environment",
                               return_value=result) as with_oil:
            positive=self.post("/api/v1/environment/season-build",{
                **payload,"selected_oil_item_ids_by_hand":oil_choice})
        self.assertEqual(positive.status_code,200,positive.text)
        self.assertEqual(with_oil.call_args.kwargs["fresh_collection_inputs"][
            "selected_budget_items"],{
                "flask_item_id":241326,
                "oil_item_ids_by_hand":oil_choice})
        self.assertFalse(positive.json()["web_environment_scope"][
            "explicit_no_oil_with_selected_flask"])
        self.assertEqual(positive.json()["web_environment_scope"][
            "selected_oil_item_ids_by_hand"],oil_choice)
        self.assertEqual(self.post("/api/v1/environment/season-build",
            {**payload,"selected_oil_item_ids_by_hand":{
                "offhand":243734}}).status_code,422)
        self.assertEqual(self.post("/api/v1/environment/season-build",
            {"game_build":"12.2.0.99999",
             "selected_oil_item_ids_by_hand":oil_choice}).status_code,422)
        self.assertEqual(self.post("/api/v1/environment/season-build",
            {**payload,"selected_flask_item_id":0}).status_code,422)
        self.assertEqual(self.post("/api/v1/environment/season-build",
            {**payload,"selected_flask_item_id":"invalid"}).status_code,422)


    def test_p3_fh_web_auto_flask_choice_never_injects_rating_proof(self):
        payload={"game_build":"12.2.0.99999","target_ilevel":334,
                 "consumable_native_binary":str(self.binary),
                 "auto_native_F_requested":True,
                 "auto_select_observed_F_no_oil":True}
        with mock.patch.object(web.environment_build,"build_environment",
                               return_value={"status":"SOURCE_ONLY_PENDING",
                                   "environment_ready":False,
                                   "environment_installed":False}) as stage:
            response=self.post("/api/v1/environment/season-build",payload)
        self.assertEqual(response.status_code,200,response.text)
        args=stage.call_args.kwargs["fresh_collection_inputs"]
        self.assertIsNone(stage.call_args.kwargs["user"])
        self.assertTrue(args["auto_select_observed_F_no_oil"])
        self.assertTrue(args["auto_native_F_requested"])
        self.assertNotIn("selected_budget_items",args)
        self.assertNotIn("same_build_budget_evidence",args)
        self.assertTrue(response.json()["web_environment_scope"][
            "auto_select_observed_F_no_oil"])
        with mock.patch.object(web.environment_build,"build_environment",
                               side_effect=AssertionError("MUST_NOT_COLLECT")) as collect:
            bads=[
                {**payload,"auto_native_F_requested":False},
                {**payload,"auto_native_O_requested":True},
                {**payload,"selected_flask_item_id":241326}]
            for bad in bads:
                result=self.post("/api/v1/environment/season-build",bad)
                self.assertEqual(result.status_code,422,result.text)
                self.assertEqual(result.json()["detail"]["code"],
                    "SEASON_AUTO_F_REQUIRES_EXPLICIT_F_NATIVE_AND_NO_OIL")
            collect.assert_not_called()

    def test_web_season_environment_build_native_only_explicit_and_validated(self):
        payload={"game_build":"12.2.0.99999","target_ilevel":341,
                 "native_G_binary":str(self.binary),
                 "simc_revision_hint":"7bc1071"}
        with mock.patch.object(web.environment_build,"build_environment",
                               return_value={"status":"SOURCE_ONLY_PENDING",
                                             "environment_ready":False,
                                             "environment_installed":False}) as stage:
            response=self.post("/api/v1/environment/season-build",payload)
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(stage.call_args.kwargs["binary"],self.binary.resolve())
        self.assertEqual(stage.call_args.kwargs["fresh_collection_inputs"]
                         ["representative_request"]["target_ilevel"],341)
        self.assertTrue(response.json()["web_environment_scope"]["local_native_G_requested"])
        self.assertFalse(response.json()["web_environment_scope"]["auto_native_F_requested"])
        self.assertFalse(response.json()["web_environment_scope"]["auto_native_O_requested"])
        with mock.patch.object(web.environment_build,"build_environment",
                               return_value={"status":"SOURCE_ONLY_PENDING",
                                             "environment_ready":False,
                                             "environment_installed":False}) as auto:
            opted=self.post("/api/v1/environment/season-build",
                            {**payload,"auto_native_F_requested":True,
                             "auto_native_O_requested":True})
        self.assertEqual(opted.status_code,200,opted.text)
        self.assertTrue(auto.call_args.kwargs["fresh_collection_inputs"][
            "auto_native_F_requested"])
        self.assertTrue(opted.json()["web_environment_scope"][
            "auto_native_F_requested"])
        self.assertTrue(auto.call_args.kwargs["fresh_collection_inputs"][
            "auto_native_O_requested"])
        self.assertTrue(opted.json()["web_environment_scope"][
            "auto_native_O_requested"])
        with mock.patch.object(web.environment_build,"build_environment",
                               side_effect=AssertionError("MUST_BLOCK_BEFORE_SOURCE")) as stage:
            invalid=self.post("/api/v1/environment/season-build",
                              {**payload,"native_G_binary":str(self.root/"missing.exe")})
        self.assertEqual(invalid.status_code,422,invalid.text)
        self.assertEqual(invalid.json()["detail"]["code"],
                         "SEASON_NATIVE_G_BINARY_INVALID")
        stage.assert_not_called()
        self.assertEqual(self.post("/api/v1/environment/season-build",
                                   {"game_build":"12.2.0.99999",
                                    "controls":{"class":"paladin"}}).status_code,422)
        self.assertEqual(self.post("/api/v1/environment/season-build",
                                   {"game_build":"../../bad"}).status_code,422)
        self.assertEqual(self.post("/api/v1/environment/season-build",
                                   {"game_build":"12.2.0.99999",
                                    "target_ilevel":1001}).status_code,422)
        self.assertEqual(self.client.post("/api/v1/environment/season-build",
                         json={"game_build":"12.2.0.99999"},
                         headers={"content-type":"application/json"}).status_code,403)

    def test_season_oil_static_source_only_without_executable(self):
        # v296 reuses the season's pinned SimC compiler data, not v269's
        # talent-buffed O Native. An O-only Build must require no executable.
        payload={"game_build":"12.2.0.99999","target_ilevel":334,
                 "auto_native_O_requested":True}
        source={"status":"SOURCE_ONLY_PENDING",
                "environment_ready":False,"environment_installed":False,
                "native_calls":0}
        with mock.patch.object(web.environment_build,"build_environment",
                               return_value=source) as stage:
            response=self.post("/api/v1/environment/season-build",payload)
        self.assertEqual(response.status_code,200,response.text)
        self.assertIsNone(stage.call_args.kwargs["binary"])
        args=stage.call_args.kwargs["fresh_collection_inputs"]
        self.assertTrue(args["auto_native_O_requested"])
        self.assertFalse(args["auto_native_F_requested"])
        self.assertFalse(args["auto_native_G_requested"])
        self.assertFalse(response.json()["environment_ready"])

    def test_web_F_O_only_native_uses_existing_binary_without_G_probe(self):
        payload={"game_build":"12.2.0.99999","target_ilevel":334,
                 "consumable_native_binary":str(self.binary),
                 "auto_native_F_requested":True,
                 "auto_native_O_requested":True}
        source={"status":"SOURCE_ONLY_PENDING",
                "environment_ready":False,"environment_installed":False,
                "native_calls":0}
        with mock.patch.object(web.environment_build,"build_environment",
                               return_value=source) as stage:
            response=self.post("/api/v1/environment/season-build",payload)
        self.assertEqual(response.status_code,200,response.text)
        scope=response.json()["web_environment_scope"]
        self.assertFalse(scope["local_native_G_requested"])
        self.assertTrue(scope["F_O_native_binary_configured"])
        self.assertTrue(scope["auto_native_F_requested"])
        self.assertTrue(scope["auto_native_O_requested"])
        self.assertFalse(scope["environment_ready"])
        kwargs=stage.call_args.kwargs
        self.assertEqual(kwargs["binary"],self.binary.resolve())
        self.assertFalse(kwargs["fresh_collection_inputs"][
            "auto_native_G_requested"])
        self.assertTrue(kwargs["fresh_collection_inputs"][
            "auto_native_O_requested"])
        self.assertIsNone(kwargs["user"])
        self.assertIsNone(kwargs["session_folder"])
        with mock.patch.object(web.environment_build,"build_environment",
                               side_effect=AssertionError("NO_COLLECTION")) as stage:
            bad=self.post("/api/v1/environment/season-build",
                          {**payload,"consumable_native_binary":
                              str(self.root/"missing_simc")})
            self.assertEqual(bad.status_code,422,bad.text)
            self.assertEqual(bad.json()["detail"]["code"],
                             "SEASON_NATIVE_F_O_BINARY_INVALID")
            not_opted=self.post("/api/v1/environment/season-build",
                                {**payload,"auto_native_F_requested":False,
                                 "auto_native_O_requested":False})
            self.assertEqual(not_opted.status_code,422,not_opted.text)
            self.assertEqual(not_opted.json()["detail"]["code"],
                             "SEASON_F_O_BINARY_WITHOUT_MEASUREMENT_SELECTION")
            alternate=self.root/"alternate_simc.exe"
            alternate.write_bytes(b"NOT_EXECUTED")
            mixed=self.post("/api/v1/environment/season-build",
                            {**payload,"native_G_binary":str(alternate)})
            self.assertEqual(mixed.status_code,422,mixed.text)
            self.assertEqual(mixed.json()["detail"]["code"],
                             "SEASON_NATIVE_G_F_O_BINARY_MISMATCH")
            stage.assert_not_called()

    def test_environment_build_fresh_source_routes_before_old_plan(self):
        payload={**self.payload,"current_season_product":False,
                 "fresh_season_build":"12.2.0.99999"}
        fake={"schema":"v216_fresh_source_stage_v1",
              "status":"FRESH_WAGO_DB2_COLLECTED_MORE_SOURCES_PENDING",
              "environment_ready":False,"environment_installed":False,
              "network_calls_by_stage":10,"native_calls":0,
              "source_stage":{"status":"EXECUTED_AND_SEALED",
                              "reused":False}}
        with mock.patch.object(
                web.environment_build,"collect_wago_new_season_source",
                return_value=fake) as acquire, mock.patch.object(
                self.app.state.jobs,"plan",
                side_effect=AssertionError("PRIOR_SEASON_PLAN_FORBIDDEN")):
            response=self.post("/api/v1/environment/build",payload)
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()["status"],fake["status"])
        self.assertTrue(response.json()["normal_build_entry"])
        phase=response.json()["zero_history_build"]
        self.assertEqual(phase["entrypoint"],"v216.build_environment")
        self.assertFalse(phase["history_dependency_required"])
        self.assertFalse(phase["environment_ready"])
        self.assertFalse(phase["user_session_created"])
        validated=sessions.user_scenario(self.controls)
        acquire.assert_called_once_with(
            sessions_root=(self.root/"runs").resolve(),
            expected_game_build="12.2.0.99999",
            representative_request={
                "class":validated["character"]["class"],
                "spec":validated["character"]["spec"],
                "target_ilevel":validated["target"]["ilevel"]},
            g_probe_character={
                "race":validated["character"]["race"],
                "talents":validated["character"]["talents"]},
            simc_revision_hint=self.payload["revision"])
        self.assertFalse((self.root/"runs").exists())
        for endpoint in ("/api/v1/sessions/plan","/api/v1/sessions/start"):
            forbidden=self.post(endpoint,payload)
            self.assertEqual(forbidden.status_code,422,forbidden.text)
            self.assertEqual(forbidden.json()["detail"]["code"],
                             "FRESH_SOURCE_NOT_INSTALLED")
        wrong=self.post("/api/v1/environment/build",
                        {**payload,"fresh_season_build":"../../other"})
        self.assertEqual(wrong.status_code,422)
        self.assertFalse((self.root/"runs").exists())
        unauthorized=self.client.post(
            "/api/v1/environment/build",json=payload,
            headers={"content-type":"application/json"})
        self.assertEqual(unauthorized.status_code,403)

    def test_web_environment_build_fills_optional_character_defaults(self):
        payload={**self.payload,"current_season_product":False,
                 "fresh_season_build":"12.2.0.99999"}
        controls=dict(self.controls)
        controls.pop("race");controls.pop("talents")
        payload["controls"]=controls
        with mock.patch.object(
                web.environment_build,"collect_wago_new_season_source",
                return_value={"schema":"v216_fresh_source_stage_v1",
                              "source_stage":{"status":"EXECUTED_AND_SEALED",
                                              "reused":False},
                              "environment_ready":False,
                              "environment_installed":False,
                              "native_calls":0}
                ) as called:
            response=self.post("/api/v1/environment/build",payload)
        self.assertEqual(response.status_code,200,response.text)
        request=called.call_args.kwargs
        self.assertEqual(request["g_probe_character"]["race"],"dwarf")
        self.assertEqual(request["g_probe_character"]["talents"],
                         sessions.source_defaults(
                             ("paladin","retribution"))["talents"])
        self.assertEqual(request["representative_request"]["target_ilevel"],334)

    def test_packaged_v213_catalog_path_is_detected_and_missing_path_falls_back(self):
        jobs=web.LocalJobs(self.root/"runs")
        expected=(pathlib.Path(web.__file__).resolve().parents[1]/
                  "data"/"current_season_source_to_catalog.json")
        original=pathlib.Path.is_file
        def only_catalog_present(path):
            if path.resolve()==expected.resolve():
                return True
            return original(path)
        with mock.patch.object(pathlib.Path,"is_file",only_catalog_present):
            self.assertEqual(jobs.source_catalog_path(),expected)
        def catalog_absent(path):
            if path.resolve()==expected.resolve():
                return False
            return original(path)
        with mock.patch.object(pathlib.Path,"is_file",catalog_absent):
            self.assertIsNone(jobs.source_catalog_path())


    def test_v337_sealed_snapshot_restores_ko_gem_worklist(self):
        """Core v212 reuse without v113 gem context must not shrink names."""
        jobs=web.LocalJobs(self.root/"runs")
        build="12.1.5.70783"
        prior={"environment_ready":True,"environment_installed":True,
               "G":2850,"J":92,"F":165,"B":3107,"T":3107,
               "installed_manifest_sha256":"a"*64}
        sealed_compilation={
            "verified_environment_install":{
                "stage_output_path":"/test/verified-v212.json",
                "manifest_sha256":"a"*64},
            "physical_gem_layout_unadmitted":{
                "ordinary_gem_ids":[280011,280012,280013,280014],
                "special_gem_id":None}}
        def observe(root,game_build,source,*,target_ilevel):
            self.assertEqual(game_build,build)
            self.assertEqual(target_ilevel,334)
            self.assertEqual(source["installed_manifest_sha256"],"a"*64)
            self.assertEqual(source["source_compilation"][
                "physical_gem_layout_unadmitted"]["ordinary_gem_ids"],
                [280011,280012,280013,280014])
            return {"schema":web.official_ko_env.SCHEMA,
                    "status":"VERIFIED_OFFICIAL_NAMES_COMPLETE",
                    "selected_item_count":5,"verified_names":5,
                    "network_calls_now":0,"native_calls_now":0}
        with mock.patch.object(web.official_ko_env,
                               "build_for_environment",
                               side_effect=observe) as checked:
            result=jobs._with_verified_ko_localization(
                build,334,prior,verified_profile_compilation=sealed_compilation)
        checked.assert_called_once()
        self.assertNotIn("source_compilation",result)
        self.assertEqual(result["T"],3107)
        self.assertEqual(result["official_ko_localization"][
                         "selected_item_count"],5)
        self.assertEqual(result["official_ko_localization"][
                         "network_calls_now"],0)

    def test_v335_environment_localization_is_additive_and_read_only(self):
        from runner import v335_environment_official_ko_localization as locale
        build="12.1.5.70783"
        with mock.patch.object(web.official_ko_env,
                               "build_for_environment",
                               side_effect=web.official_ko_env.LocalizationBlocked(
                                   "SIMULATED_OFFICIAL_ITEM_SOURCE_FAILURE")):
            jobs=web.LocalJobs(self.root)
            core={"environment_ready":True,"environment_installed":True,
                  "G":2850,"J":92,"F":165,"B":3107,"T":3107}
            result=jobs._with_verified_ko_localization(build,334,core)
        self.assertEqual(result["B"],3107)
        self.assertTrue(result["environment_ready"])
        self.assertEqual(result["official_ko_localization"]["status"],
                         "OFFICIAL_KO_SOURCE_OR_CACHE_REQUIRES_REVIEW")
        with mock.patch.object(web.official_ko_env.blizzard,
                               "request_json") as request:
            status=self.client.get(
                "/api/v1/environment/official-ko-localization",
                params={"game_build":build},headers=self.headers)
        self.assertEqual(status.status_code,200,status.text)
        self.assertEqual(status.json()["status"],
                         "OFFICIAL_KO_CACHE_NOT_INSTALLED")
        self.assertEqual(status.json()["native_calls_now"],0)
        request.assert_not_called()


    def test_v336_official_game_terms_is_readonly_and_never_changes_user_controls(self):
        from runner import v336_environment_ko_playable_terms as term
        app=web.create_app(root=self.root,token="offline-only-token")
        with mock.patch.object(web.official_playable_terms,"build_for_environment",
                               return_value={"schema":term.SCHEMA,
                                 "status":"CREDENTIALS_UNAVAILABLE_TERMS_PENDING",
                                 "network_calls_now":0,"native_calls_now":0}) as collect:
            jobs=app.state.jobs
            payload=jobs._with_verified_ko_localization(
                "12.1.5.70783",334,
                {"environment_ready":True,"environment_installed":True,
                 "G":2850,"J":92,"F":165,"B":3107,"T":3107,
                 "official_ko_localization":{"schema":web.official_ko_env.SCHEMA,
                                            "status":"VERIFIED_OFFICIAL_NAMES_COMPLETE"}})
        self.assertEqual(payload["T"],3107)
        self.assertEqual(payload["official_ko_terms"]["status"],
                         "CREDENTIALS_UNAVAILABLE_TERMS_PENDING")
        collect.assert_called_once()
        with TestClient(app,base_url="http://127.0.0.1:8765") as client:
            ok=client.get("/api/v1/environment/official-game-terms",
                params={"game_build":"12.1.5.70783"},
                headers={"x-simc-local-token":"offline-only-token",
                         "origin":"http://127.0.0.1:8765"})
            self.assertEqual(ok.status_code,200,ok.text)
            self.assertEqual(len(ok.json()["names"]["spec"]),26)
            self.assertEqual(ok.json()["names"]["spec"]["demonhunter/devourer"],"포식")
            self.assertEqual(ok.json()["native_calls_now"],0)
            denied=client.get("/api/v1/environment/official-game-terms",
                params={"game_build":"../../other"},
                headers={"x-simc-local-token":"offline-only-token",
                         "origin":"http://127.0.0.1:8765"})
            self.assertEqual(denied.status_code,422)

    def test_bootstrap_health_and_all_26_dps_defaults_no_simc(self):
        health=self.client.get("/api/v1/health")
        self.assertEqual(health.status_code,200)
        self.assertEqual(health.json()["supported_dps"],26)
        boot=self.client.get("/api/v1/bootstrap").json()
        self.assertEqual(boot["session_token"],"offline-only-token")
        self.assertEqual(len(boot["supported"]),26)
        defaults=self.client.get("/api/v1/defaults",headers=self.headers)
        self.assertEqual(defaults.status_code,200)
        status_counts={}
        for row in defaults.json()["archetypes"]:
            self.assertEqual(len(row["trinket_ids"]),2)
            self.assertEqual(row["ilevel"],334)
            self.assertEqual(len(row["consumable_choices"]),6)
            scope=row["representative_scope"]
            status_counts[scope]=status_counts.get(scope,0)+1
            expected=("SOURCE_INDEPENDENT_SEASON_CATALOG"
                      if (row["class"],row["spec"]) in
                          web.bootstrap.PURE_PRODUCT_SPECS
                      else "SOURCE_INDEPENDENT_TARGET334_VALIDATED_BATCH")
            self.assertEqual(scope,expected)
        self.assertEqual(status_counts,{
            "SOURCE_INDEPENDENT_TARGET334_VALIDATED_BATCH":24,
            "SOURCE_INDEPENDENT_SEASON_CATALOG":2})
        by_key={(x["class"],x["spec"]):x for x in defaults.json()["archetypes"]}
        self.assertEqual(by_key[("druid","balance")]["race"],"night_elf")
        self.assertEqual(by_key[("evoker","devastation")]["race"],"dracthyr")
        restrictions=defaults.json()["allowed_races_by_spec"]
        self.assertEqual(restrictions["evoker/devastation"],
                         ["dracthyr","dracthyr_visage"])
        self.assertNotIn("mage/frost",restrictions)
        self.assertTrue(all("allowed_races" not in row
                            for row in defaults.json()["archetypes"]))
        self.assertFalse((self.root/"runs").exists())

    def test_web_remains_usable_with_no_legacy_complete_simc_fixtures(self):
        # In a package without the old 24 full SimC source fixtures, the
        # ready/default UI list must still expose both Native-proven pure
        # paths, but may not claim the unavailable legacy paths work.
        original_text=pathlib.Path.read_text
        original_bytes=pathlib.Path.read_bytes
        original_is_file=pathlib.Path.is_file
        seen=[]
        checked=[]
        def is_legacy(path):
            return ("/integration_probes/fixtures/" in
                    str(path).replace(chr(92),"/") and
                    str(path).endswith(".simc"))
        def absent_text(path,*args,**kwargs):
            if is_legacy(path):
                seen.append(str(path))
                raise FileNotFoundError("LEGACY_SOURCE_PROFILE_NOT_INSTALLED")
            return original_text(path,*args,**kwargs)
        def absent_bytes(path,*args,**kwargs):
            if is_legacy(path):
                seen.append(str(path))
                raise FileNotFoundError("LEGACY_SOURCE_PROFILE_NOT_INSTALLED")
            return original_bytes(path,*args,**kwargs)
        def absent_is_file(path,*args,**kwargs):
            if is_legacy(path):
                checked.append(str(path))
                return False
            return original_is_file(path,*args,**kwargs)
        with mock.patch.object(pathlib.Path,"read_text",absent_text), \
             mock.patch.object(pathlib.Path,"read_bytes",absent_bytes), \
             mock.patch.object(pathlib.Path,"is_file",absent_is_file):
            response=self.client.get("/api/v1/defaults",headers=self.headers)
            self.assertEqual(response.status_code,200,response.text)
            data=response.json()
            visible={(r["class"],r["spec"]) for r in data["archetypes"]}
            self.assertEqual(visible,set(sessions.SUPPORTED))
            missing={(r["class"],r["spec"]) for r in
                     data["unavailable_missing_legacy_fixtures"]}
            self.assertEqual(missing,set())
            self.assertEqual(len(checked),0)
            self.assertEqual(seen,[])
            # Character/talent/trinket defaults for all 26 are now
            # available independently; only actual legacy EXECUTION is
            # unavailable when those complete historical files are absent.
            for key in sessions.SUPPORTED:
                source=sessions.standard_controls(key)
                self.assertEqual((source["class"],source["spec"]),key)
            self.assertEqual(seen,[])
            for spec in sorted(visible):
                with self.subTest(spec=spec):
                    payload={**self.payload,
                             "controls":sessions.standard_controls(spec)}
                    with mock.patch.object(web.subprocess,"Popen") as spawn:
                        plan=self.post("/api/v1/sessions/plan",payload)
                        self.assertEqual(plan.status_code,200,plan.text)
                        self.assertEqual(plan.json()["native_calls"],0)
                        spawn.assert_not_called()

    def test_two_pure_local_web_plans_reuse_normal_session_without_native(self):
        for key in sorted(web.bootstrap.PURE_PRODUCT_SPECS):
            with self.subTest(spec=key):
                params={**self.payload,"controls":sessions.standard_controls(key)}
                with mock.patch.object(web.bootstrap,"build",
                                       wraps=web.bootstrap.build) as profile_build:
                    with mock.patch.object(web.subprocess,"Popen") as spawn:
                        response=self.post("/api/v1/sessions/plan",params)
                        spawn.assert_not_called()
                    self.assertEqual(response.status_code,200,response.text)
                    body=response.json()
                    self.assertEqual(body["plan"]["final_T"],3150)
                    self.assertEqual(body["profile_stage"]["status"],
                                     "EXECUTED_AND_SEALED")
                    self.assertTrue(body["profile_stage"]["executed"])
                    folder=self.root/"runs"/body["session_id"]/"generated"
                    self.assertIn("default_actions=1",
                                  (folder/"profile.simc").read_text())
                    self.assertNotIn(web.bootstrap.entry.STAGE_FIELD,
                             json.loads((folder/"manifest.json").read_text()))
                    again=self.post("/api/v1/sessions/plan",params)
                    self.assertEqual(again.status_code,200,again.text)
                    self.assertEqual(again.json()["session_id"],body["session_id"])
                    self.assertEqual(again.json()["profile_stage"]["status"],
                                     "REUSED_VERIFIED")
                    self.assertTrue(again.json()["profile_stage"]["reused"])
                    self.assertFalse(again.json()["profile_stage"]["executed"])
                    self.assertEqual(profile_build.call_count,1)

    def test_legacy_session_without_stage_receipt_remains_resumable(self):
        user=sessions.user_scenario(self.controls)
        _,identity=sessions.session_key(user,self.binary,"7bc1071")
        legacy=dict(identity)
        legacy.pop("profile_stage")
        legacy_key=sessions.sha(sessions.canonical(legacy).encode("utf8"))[:20]
        folder=self.root/"runs"/legacy_key
        generated=folder/"generated"
        generated.mkdir(parents=True)
        (folder/"user.json").write_text(
            sessions.canonical(user)+"\n",encoding="utf8")
        (folder/"V106_SESSION_IDENTITY.json").write_text(
            sessions.canonical(legacy)+"\n",encoding="utf8")
        (generated/"manifest.json").write_text(json.dumps({
            "native_binary":str(self.binary),
            "native_revision":"7bc1071",
            "static_cache_json":None}),encoding="utf8")
        self.assertEqual(self.app.state.jobs.args_for_existing(folder),
                         (self.binary.resolve(),"7bc1071",None))

    def test_host_rebinding_foreign_origin_token_and_cross_site_all_denied(self):
        for host in ("attacker.example:8765","localhost:8765",
                     "127.0.0.1.evil.example:8765"):
            r=self.client.get("/api/v1/bootstrap",headers={"host":host})
            self.assertEqual(r.status_code,403,host)
        self.assertEqual(self.client.get("/api/v1/defaults").status_code,403)
        r=self.client.get("/api/v1/defaults",headers={
            **self.headers,"x-simc-local-token":"incorrect"})
        self.assertEqual(r.status_code,403)
        r=self.client.get("/api/v1/defaults",headers={
            **self.headers,"origin":"http://evil.example"})
        self.assertEqual(r.status_code,403)
        r=self.client.get("/api/v1/defaults",headers={
            **self.headers,"sec-fetch-site":"cross-site"})
        self.assertEqual(r.status_code,403)
        r=self.client.post("/api/v1/sessions/plan",data="hello",
            headers=self.headers|{"content-type":"text/plain"})
        self.assertEqual(r.status_code,415)
        self.assertFalse((self.root/"runs").exists())

    def test_a8_binary_alias_reuses_same_sha_bound_plan_without_native(self):
        original=self.plan()
        alias=self.root/"user_binary_alias.exe"
        try:
            alias.symlink_to(self.binary)
        except (OSError,NotImplementedError) as exc:
            self.skipTest("symlink unavailable: "+str(exc))
        with mock.patch.object(web.subprocess,"Popen",
                side_effect=AssertionError("NATIVE_MUST_NOT_START")) as worker:
            response=self.post("/api/v1/sessions/plan",
                {**self.payload,"binary":str(alias)})
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()["session_id"],original["session_id"])
        self.assertEqual(response.json()["native_calls"],0)
        worker.assert_not_called()

    def test_a8_alias_planned_session_resumes_without_rebuilding(self):
        alias=self.root/"saved_binary_alias.exe"
        try:
            alias.symlink_to(self.binary)
        except (OSError,NotImplementedError) as exc:
            self.skipTest("symlink unavailable: "+str(exc))
        with mock.patch.object(web.subprocess,"Popen",
                side_effect=AssertionError("NATIVE_MUST_NOT_START")) as worker:
            response=self.post("/api/v1/sessions/plan",
                               {**self.payload,"binary":str(alias)})
            self.assertEqual(response.status_code,200,response.text)
            folder=self.root/"runs"/response.json()["session_id"]
            saved=json.loads((folder/"generated"/"manifest.json")
                             .read_text(encoding="utf8"))
            self.assertEqual(pathlib.Path(saved["native_binary"]),
                             self.binary.resolve())
            recovered=self.app.state.jobs.args_for_existing(folder)
        self.assertEqual(recovered,(self.binary.resolve(),"7bc1071",None))
        worker.assert_not_called()

    def test_plan_builds_real_pinned_paladin_manifest_without_native(self):
        with mock.patch.object(web.subprocess,"Popen") as spawn:
            planned=self.plan()
            spawn.assert_not_called()
        self.assertEqual(planned["status"],"READY_ZERO_NATIVE")
        self.assertEqual(planned["native_calls"],0)
        self.assertEqual(planned["plan"]["base_B"],3150)
        self.assertEqual(sum(planned["plan"]["fixed_O"].values()),32)
        self.assertEqual(planned["plan"]["final_T"],3182)
        self.assertFalse(planned["plan"]["native_called"])
        path=(self.root/"runs"/planned["session_id"])
        self.assertTrue((path/"generated"/"manifest.json").is_file())
        self.assertFalse((path/"generated"/"simc_results").exists())
        self.assertFalse((path/"V106_WORKER_STATE.json").exists())
        status=self.client.get(
            "/api/v1/sessions/"+planned["session_id"]+"/status",
            headers=self.headers)
        self.assertEqual(status.status_code,200)
        self.assertEqual(status.json()["progress"]["completed_jobs"],0)
        self.assertFalse(status.json()["active"])

    def test_current_season_plan_seals_packaged_v212_environment_manifest_zero_native(self):
        builder=SourceToCatalogTests()
        builder.setUpClass()
        season,classification=builder.build_inputs()
        # The source artifact must bind the exact current-season input bytes
        # consumed by the v098 profile supplier and the v181 package.
        for key,name in (("gear","current_season_product_gear_db.json"),
                         ("tier","current_season_tier_itemsets.json"),
                         ("budget","current_season_chmv_consumables.json")):
            season["sha256_by_input"][key]=source_bridge.sha(
                (ROOT/"data"/name).read_bytes())
        source=source_bridge.compile_catalog(
            season,"a"*64,classification,"b"*64)
        package_root=self.root/"SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA"
        data=package_root/"data"
        data.mkdir(parents=True,exist_ok=True)
        source_path=data/"current_season_source_to_catalog.json"
        raw=json.dumps(source,sort_keys=True,ensure_ascii=False,
                       indent=2).encode("utf8")+b"\n"
        source_path.write_bytes(raw)
        source_sha=source_bridge.sha(raw)
        source_meta={
            "path":"data/current_season_source_to_catalog.json",
            "schema":source["schema"],"game_build":source["game_build"],
            "simc_revision":source["simc_revision"],
            "artifact_sha256":source_sha,
            "manifest_sha256":source["manifest_sha256"],
            "native_calls":0,"network_calls":0,
            "automatic_ui_promotion":False,
        }
        package={
            "schema":"v181_windows_local_web_beta_source_package_v1",
            "archive_root":package_root.name,
            "files":[{"path":source_meta["path"],"size":len(raw),
                      "sha256":source_sha}],
            "file_count":1,"source_catalog":source_meta,
        }
        package_path=package_root/"V181_PACKAGE_MANIFEST.json"
        package_path.write_text(json.dumps(package,sort_keys=True,
            ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        jobs=self.app.state.jobs
        payload={**self.payload,"revision":source["simc_revision"],
                 "current_season_product":True}
        with mock.patch.object(jobs,"source_catalog_path",return_value=source_path), \
             mock.patch.object(jobs,"package_manifest_path",return_value=package_path):
            with mock.patch.object(web.subprocess,"Popen") as spawn:
                response=self.post("/api/v1/sessions/plan",payload)
                spawn.assert_not_called()
            self.assertEqual(response.status_code,200,response.text)
            body=response.json()
            environment=body["environment_manifest"]
            self.assertEqual(environment["status"],"READY_WITH_LIMITATIONS")
            self.assertEqual(environment["windows_package_status"],"VERIFIED")
            self.assertEqual(environment["source_catalog_sha256"],source_sha)
            self.assertEqual(environment["native_calls"],0)
            self.assertEqual(environment["network_calls"],0)
            self.assertIn("ALL_26_ADAPTIVE_PROFILE_NATIVE_ACCEPTANCE",
                          environment["unresolved_dependencies"])
            self.assertEqual(
                environment["profile_supplier_coverage"]
                    ["current_season_profile_supplier_count"],26)
            self.assertFalse(environment["profile_supplier_coverage"]["all_specs_ready"])
            folder=self.root/"runs"/body["session_id"]
            saved=json.loads((folder/"generated"/"environment_manifest.json")
                             .read_text(encoding="utf8"))
            self.assertEqual(saved["manifest_sha256"],environment["manifest_sha256"])
            status=self.client.get("/api/v1/sessions/"+body["session_id"]+"/status",
                                   headers=self.headers)
            self.assertEqual(status.status_code,200,status.text)
            self.assertEqual(status.json()["environment_manifest"],environment)
            self.assertEqual(status.json()["progress"]["native_attempts"],0)
            # Same season and exact source bytes, updated SimC balance binary
            # revision: normal HTTP plan should create a NEW DPS identity
            # without any source recollection or previous session mutation.
            prior_bytes=(folder/"generated"/"environment_manifest.json").read_bytes()
            next_revision="f"*40
            updated=self.post("/api/v1/sessions/plan",
                              {**payload,"revision":next_revision})
            self.assertEqual(updated.status_code,200,updated.text)
            newer=updated.json()
            self.assertNotEqual(newer["session_id"],body["session_id"])
            new_folder=self.root/"runs"/newer["session_id"]
            new_manifest=json.loads((new_folder/"generated"/
                                     "environment_manifest.json").read_text("utf8"))
            self.assertEqual(new_manifest["source_catalog"]["simc_revision"],
                             source["simc_revision"])
            self.assertEqual(new_manifest["dependency_graph"]["fingerprints"][
                             "simc_revision"],next_revision)
            self.assertEqual((folder/"generated"/
                              "environment_manifest.json").read_bytes(),prior_bytes)
            self.assertEqual(source_path.read_bytes(),raw)
            self.assertEqual(newer["environment_manifest"]["native_calls"],0)
            # A changed packaged source invalidates Start/Resume before a
            # worker process is spawned; the status read itself is non-mutating.
            source_path.write_bytes(raw[:-1]+b" ")
            with mock.patch.object(web.subprocess,"Popen") as spawn:
                stale=self.post("/api/v1/sessions/"+body["session_id"]+"/resume")
                spawn.assert_not_called()
            self.assertEqual(stale.status_code,422,stale.text)
            self.assertEqual(stale.json()["detail"]["code"],
                             "V213_SOURCE_CATALOG_CHANGED_AFTER_PLAN")

    def test_environment_build_api_reuses_installed_source_and_seals_incremental_receipt(self):
        builder=SourceToCatalogTests()
        builder.setUpClass()
        season,classification=builder.build_inputs()
        for key,name in (("gear","current_season_product_gear_db.json"),
                         ("tier","current_season_tier_itemsets.json"),
                         ("budget","current_season_chmv_consumables.json")):
            season["sha256_by_input"][key]=source_bridge.sha(
                (ROOT/"data"/name).read_bytes())
        source=source_bridge.compile_catalog(
            season,"a"*64,classification,"b"*64)
        package_root=self.root/"SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA"
        data=package_root/"data"
        data.mkdir(parents=True,exist_ok=True)
        source_path=data/"current_season_source_to_catalog.json"
        raw=json.dumps(source,sort_keys=True,ensure_ascii=False,
                       indent=2).encode("utf8")+b"\n"
        source_path.write_bytes(raw)
        source_sha=source_bridge.sha(raw)
        source_meta={
            "path":"data/current_season_source_to_catalog.json",
            "schema":source["schema"],"game_build":source["game_build"],
            "simc_revision":source["simc_revision"],
            "artifact_sha256":source_sha,
            "manifest_sha256":source["manifest_sha256"],
            "native_calls":0,"network_calls":0,
            "automatic_ui_promotion":False,
        }
        package={
            "schema":"v181_windows_local_web_beta_source_package_v1",
            "archive_root":package_root.name,
            "files":[{"path":source_meta["path"],"size":len(raw),
                      "sha256":source_sha}],
            "file_count":1,"source_catalog":source_meta,
        }
        package_path=package_root/"V181_PACKAGE_MANIFEST.json"
        package_path.write_text(json.dumps(package,sort_keys=True,
            ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        jobs=self.app.state.jobs
        payload={**self.payload,"revision":source["simc_revision"],
                 "current_season_product":True}
        with mock.patch.object(jobs,"source_catalog_path",return_value=source_path), \
             mock.patch.object(jobs,"package_manifest_path",return_value=package_path):
            with mock.patch.object(web.bootstrap,"build",
                                   wraps=web.bootstrap.build) as profile_build:
                with mock.patch.object(web.subprocess,"Popen") as spawn:
                    first=self.post("/api/v1/environment/build",payload)
                    spawn.assert_not_called()
                self.assertEqual(first.status_code,200,first.text)
                first_body=first.json()
                self.assertEqual(first_body["status"],"READY_ZERO_NATIVE")
                self.assertEqual(first_body["environment_build"]["status"],
                                 "READY_WITH_LIMITATIONS")
                self.assertEqual(first_body["environment_build"]["source"]["mode"],
                                 "INSTALLED_VERSIONED_ARTIFACT_ONLY")
                self.assertFalse(first_body["environment_build"]["source"]["refresh_performed"])
                self.assertEqual(first_body["environment_build"]["native_calls"],0)
                self.assertEqual(first_body["environment_build"]["network_calls"],0)
                self.assertEqual(first_body["environment_build"]["cache_mutations"],0)
                self.assertEqual(first_body["profile_stage"]["status"],
                                 "EXECUTED_AND_SEALED")
                self.assertEqual(first_body["environment_build"]["profile_stage"]["status"],
                                 "EXECUTED_AND_SEALED")
                self.assertEqual(first_body["environment_build"]["cache_reuse"]
                                 ["installed_v213_artifact_hits"],1)
                self.assertEqual(first_body["environment_build"]["readiness"]
                                 ["profile_plan_suppliers"]["count"],26)
                components={row["component"]:row["status"]
                            for row in first_body["environment_build"]["steps"]}
                self.assertEqual(components["v191_source_collection"],"REUSED_EMBEDDED")
                self.assertEqual(components["v211_simc_effect_classification"],
                                 "REUSED_EMBEDDED")
                self.assertEqual(components["v213_source_to_catalog"],
                                 "REUSED_PACKAGED_ARTIFACT")
                self.assertEqual(components["v098_target_profile"],
                                 "EXECUTED_AND_SEALED")
                session_id=first_body["session_id"]
                folder=self.root/"runs"/session_id
                receipt_path=folder/"generated"/"environment_build_receipt.json"
                self.assertTrue(receipt_path.is_file())
                saved=json.loads(receipt_path.read_text(encoding="utf8"))
                self.assertEqual(saved["source"]["artifact_sha256"],source_sha)
                self.assertEqual(saved["historical_sessions_preserved"],True)

                second=self.post("/api/v1/environment/build",payload)
                self.assertEqual(second.status_code,200,second.text)
                self.assertEqual(second.json()["session_id"],session_id)
                self.assertEqual(second.json()["profile_stage"]["status"],
                                 "REUSED_VERIFIED")
                self.assertEqual(second.json()["environment_build"]["profile_stage"]["status"],
                                 "REUSED_VERIFIED")
                second_steps={row["component"]:row["status"]
                              for row in second.json()["environment_build"]["steps"]}
                self.assertEqual(second_steps["v098_target_profile"],
                                 "REUSED_VERIFIED_ARTIFACTS")
                third=self.post("/api/v1/environment/build",payload)
                self.assertEqual(third.status_code,200,third.text)
                self.assertEqual(profile_build.call_count,1)
                self.assertEqual(third.json()["environment_build"]["dependency_change"]
                                 ["status"],"INITIAL_ENVIRONMENT")
                self.assertEqual(third.json()["environment_build"]["steps"][-1]["status"],
                                 "COMPILED_IDENTICAL_NO_WRITE")
                self.assertEqual(jobs.args_for_existing(folder),
                                 (self.binary.resolve(),source["simc_revision"],None))
                # Exact worker handoff: no second v098 generator call and
                # the existing v096 runner receives the stage-sealed manifest.
                from tests.test_v106_user_session_controller import fake_native
                with mock.patch.object(
                    sessions,"_installed_source_paths",
                    return_value=(source_path,package_path)
                ), mock.patch.object(
                    web.bootstrap.entry,"run_manifest",
                    return_value=fake_native(0)
                ) as existing_optimizer, mock.patch.object(
                    web.bootstrap,"build",
                    side_effect=AssertionError("V098_BUILD_MUST_BE_SKIPPED")
                ) as duplicate_builder:
                    if hasattr(sessions.os,"startfile"):
                        folder_open=mock.patch.object(sessions.os,"startfile")
                    else:
                        from contextlib import nullcontext
                        folder_open=nullcontext()
                    with folder_open:
                        self.assertEqual(
                            sessions.worker(folder,self.binary,
                                            source["simc_revision"]),0)
                    duplicate_builder.assert_not_called()
                    existing_optimizer.assert_called_once()
                    self.assertEqual(
                        existing_optimizer.call_args.args[0].resolve(),
                        (folder/"generated"/"manifest.json").resolve())
                    self.assertEqual(existing_optimizer.call_args.kwargs,
                                     {"cache_only":False})
                    self.assertTrue((folder/"V106_USER_RESULT.json").exists()
                                    or sessions.paths(folder)["final"].is_file())

                    # Tampering after Plan is blocked by the child before
                    # the optimizer can consume a different profile.
                    profile_file=folder/"generated"/"profile.simc"
                    profile_file.write_bytes(profile_file.read_bytes()+b"\n#tampered")
                    existing_optimizer.reset_mock()
                    self.assertEqual(
                        sessions.worker(folder,self.binary,
                                        source["simc_revision"]),3)
                    existing_optimizer.assert_not_called()
                    self.assertIn("STAGE_OUTPUT_HASH_MISMATCH",
                        json.loads(sessions.paths(folder)["state"].read_text())
                        ["reason"])
                status=self.client.get("/api/v1/environment/"+session_id,
                                        headers=self.headers)
                self.assertEqual(status.status_code,200,status.text)
                self.assertEqual(status.json()["environment_build"]["receipt_sha256"],
                                 third.json()["environment_build"]["receipt_sha256"])
                session_status=self.client.get(
                    "/api/v1/sessions/"+session_id+"/status",headers=self.headers)
                self.assertEqual(session_status.status_code,200,session_status.text)
                self.assertEqual(session_status.json()["environment_build"]["status"],
                                 "READY_WITH_LIMITATIONS")
        blocked_build=self.post("/api/v1/environment/build",{
            **payload,"current_season_product":False})
        self.assertEqual(blocked_build.status_code,422,blocked_build.text)
        self.assertEqual(blocked_build.json()["detail"]["code"],
                         "ENVIRONMENT_BUILD_CURRENT_SEASON_ONLY")

    def test_selected_special_start_seals_v208_receipt_before_worker_launch(self):
        jobs=self.app.state.jobs
        controls=copy.deepcopy(self.controls)
        controls["special_items"]=[{
            "slot":"back","item_id":159288,"options":{}}]
        params=web.UserRequest(
            controls=controls,binary=str(self.binary),revision="7bc1071",
            static_cache=None,current_season_product=True)
        session_id="a"*20
        folder=self.root/"runs"/session_id
        generated=folder/"generated"
        generated.mkdir(parents=True,exist_ok=True)
        (generated/"v098_bootstrap_result.json").write_text(
            json.dumps({"schema":"test"}),encoding="utf8")
        cache_path=self.root/"static-cache.json"
        cache_path.write_text("{}",encoding="utf8")
        receipt_info={
            "schema":"v208_selected_special_start_receipt_v1",
            "path":"start-receipts/v208-start-test.json",
            "receipt_sha256":"a"*64,"native_calls_this_start":0,
            "selected_special_count":1,
        }
        order=[]
        def seal(receipt_folder,bootstrap_result,receipt_path=None,profile_stage_receipt=None):
            self.assertEqual(receipt_folder,folder)
            self.assertEqual(receipt_path,folder/receipt_info["path"])
            self.assertEqual(bootstrap_result,{"schema":"test"})
            order.append("seal")
            return {"status":"READY_WITH_LIMITATIONS",
                    "v208_start_receipt_status":"VERIFIED"}
        def launch(launch_folder):
            self.assertEqual(launch_folder,folder)
            self.assertEqual(order,["seal"])
            order.append("launch")
            return {"session_id":session_id,"status":"WORKER_STARTED"}
        with mock.patch.object(web.exact_L,"hydrate",return_value={
                 "static_cache_path":str(cache_path),"start_receipt":{},
                 "native_new_calls":0,"cache_reused":1}), \
             mock.patch.object(web.exact_L,"write_start_receipt",
                               return_value=receipt_info), \
             mock.patch.object(jobs,"plan",return_value={
                 "session_id":session_id,"environment_manifest":None}), \
             mock.patch.object(jobs,"folder",return_value=folder), \
             mock.patch.object(jobs,"_seal_environment_manifest",side_effect=seal), \
             mock.patch.object(jobs,"launch",side_effect=launch):
            result=jobs.start_with_internal_special_L(params)
        self.assertEqual(order,["seal","launch"])
        self.assertEqual(result["static_L_start_receipt"],receipt_info)
        self.assertEqual(result["environment_manifest"]["v208_start_receipt_status"],
                         "VERIFIED")
        pointer=json.loads((folder/"V208_START_RECEIPT_REF.json").read_text("utf8"))
        self.assertEqual(pointer["receipt_sha256"],"a"*64)

    def test_internal_variant_resume_uses_sealed_identity_not_browser_defaults(self):
        # Developer stage only: browser plan/defaults still expose no variant.
        user=sessions.user_scenario(sessions.standard_controls(
             ("demonhunter","havoc")))
        # Reconstruct a pre-v217 sealed variant, which had no profile-stage
        # receipt. Current v217 sessions MUST require that receipt.
        _, current_identity=sessions.session_key(
            user,self.binary,"7bc1071",
            ordinary_variant="mid2_havoc_leather_feet_v1")
        legacy_identity=dict(current_identity)
        legacy_identity.pop("profile_stage")
        legacy_key=sessions.sha(
            sessions.canonical(legacy_identity).encode("utf8"))[:20]
        folder=self.root/"runs"/legacy_key
        folder.mkdir(parents=True)
        (folder/"user.json").write_text(
            sessions.canonical(user)+"\n",encoding="utf8")
        (folder/"V106_SESSION_IDENTITY.json").write_text(
            sessions.canonical(legacy_identity)+"\n",encoding="utf8")
        web.bootstrap.build(user,folder/"generated",self.binary,"7bc1071",
            ordinary_variant="mid2_havoc_leather_feet_v1")
        jobs=web.LocalJobs(self.root/"runs")
        binary,rev,static=jobs.args_for_existing(folder)
        self.assertEqual(binary,self.binary.resolve())
        self.assertEqual(rev,"7bc1071")
        self.assertIsNone(static)
        self.assertFalse((folder/"generated"/"simc_results").exists())
        browser=self.client.get("/api/v1/defaults",headers=self.headers).json()
        self.assertTrue(all("ordinary_variant" not in r
                            for r in browser["archetypes"]))
        self.assertNotIn("ordinary_variant",self.controls)

    def test_existing_app_local_exact_static_cache_auto_used_only_for_specials(self):
        # Synthetic exact record tests local cache discovery only. This is
        # NOT SimC-validated stat authority or item-effect certification.
        from tests.test_v062_static_budget_bridge import record
        cache=web.bootstrap.cache_mod.empty_cache()
        item={"slot":"chest","item_id":271486,"ilevel":331,
              "options":{"bonus_id":"13848",
                         "redirected_base_stats":"268231"}}
        record(cache,item,{"crit_rating":0,"haste_rating":175,
                           "mastery_rating":0,"versatility_rating":0})
        default=self.root/"static-item-cache.json"
        web.bootstrap.cache_mod.write_atomic(default,cache)
        controls=sessions.standard_controls(("shaman","elemental"))
        controls["ilevel"]=331
        controls["special_items"]=[{k:v for k,v in item.items()
                                   if k!="ilevel"}]
        payload={**self.payload,"controls":controls}
        with mock.patch.object(web.subprocess,"Popen") as launch:
            result=self.post("/api/v1/sessions/plan",payload)
            launch.assert_not_called()
        self.assertEqual(result.status_code,200,result.text)
        data=result.json()
        self.assertTrue(data["static_cache_auto_used"])
        self.assertEqual(data["native_calls"],0)
        folder=self.root/"runs"/data["session_id"]
        manifest=json.loads((folder/"generated"/"manifest.json").read_text())
        self.assertTrue(pathlib.Path(manifest["static_cache_json"])
                        .samefile(default))
        seal=json.loads((folder/"V106_SESSION_IDENTITY.json").read_text())
        self.assertEqual(seal["static_cache_sha256"],
                         sessions.sha(default.read_bytes()))
        self.assertEqual(self.post("/api/v1/sessions/plan",payload)
                         .json()["session_id"],data["session_id"])
        restored=self.client.get("/api/v1/sessions/"+
            data["session_id"]+"/inputs",headers=self.headers)
        self.assertEqual(restored.status_code,200,restored.text)
        self.assertTrue(pathlib.Path(restored.json()["static_cache"])
                        .samefile(default))
        # Manual override remains the exact prior contract.
        explicit=self.root/"explicit-cache.json"
        web.bootstrap.cache_mod.write_atomic(explicit,cache)
        override=self.post("/api/v1/sessions/plan",
                    {**payload,"static_cache":str(explicit)})
        self.assertEqual(override.status_code,200,override.text)
        self.assertFalse(override.json()["static_cache_auto_used"])
        # Same bytes use the exact same sealed identity; a changed PATH
        # must not silently create a new run or rewrite its manifest.
        self.assertEqual(data["session_id"],
                         override.json()["session_id"])
        self.assertEqual(json.loads((folder/"generated"/"manifest.json")
                         .read_text())["static_cache_json"],
                         manifest["static_cache_json"])
        # If no special was selected, NEVER inject any cache / alter the
        # ordinary user's historical sealed session identity.
        ordinary=self.post("/api/v1/sessions/plan",
                    {**payload,"controls":{**controls,"special_items":[]}})
        self.assertEqual(ordinary.status_code,200,ordinary.text)
        self.assertFalse(ordinary.json()["static_cache_auto_used"])
        self.assertIsNone(json.loads((self.root/"runs"/
            ordinary.json()["session_id"]/"generated"/"manifest.json")
            .read_text())["static_cache_json"])

    def test_default_static_cache_missing_exact_L_fails_closed_without_native(self):
        from tests.test_v062_static_budget_bridge import record
        cache=web.bootstrap.cache_mod.empty_cache()
        record(cache,{"slot":"chest","item_id":271486,"ilevel":331,
            "options":{"bonus_id":"13848","redirected_base_stats":"268231"}},
            {"crit_rating":0,"haste_rating":175,
             "mastery_rating":0,"versatility_rating":0})
        web.bootstrap.cache_mod.write_atomic(
            self.root/"static-item-cache.json",cache)
        controls=sessions.standard_controls(("shaman","elemental"))
        controls["ilevel"]=344
        controls["special_items"]=[{"slot":"chest","item_id":271486,
            "options":{"bonus_id":"13848","redirected_base_stats":"268231"}}]
        with mock.patch.object(web.subprocess,"Popen") as launch:
            response=self.post("/api/v1/sessions/plan",
                {**self.payload,"controls":controls})
            launch.assert_not_called()
        self.assertEqual(response.status_code,422,response.text)
        self.assertEqual(response.json()["detail"]["code"],
                         "SPECIAL_L_REQUIRES_EXACT_NATIVE_STATIC_VARIANT")

    def test_exact_special_L_precheck_returns_only_known_safe_codes(self):
        reference=web.bootstrap.oil_mod.reference_path
        expected=(
            reference.ReferenceNativeBlocked(
                "SPECIAL_L_REQUIRES_EXACT_NATIVE_STATIC_VARIANT"),
            reference.ReferenceNativeBlocked(
                "REFERENCE_FIXED_L_CONSTRAINT_UNRESOLVED"),
            reference.statics.BudgetBlocked(
                "SELECTED_SPECIAL_FLOOR_UNFEASIBLE"),
        )
        for exc in expected:
            with self.subTest(code=str(exc)):
                response=web.blocked(exc)
                self.assertEqual(response.status_code,422)
                self.assertEqual(response.detail,{"code":str(exc)})
        secret=reference.ReferenceNativeBlocked(
            "UNEXPECTED_PATH_C:/private/profile.simc")
        safe=web.blocked(secret)
        self.assertEqual(safe.status_code,409)
        self.assertEqual(safe.detail["code"],"LOCAL_SESSION_PRECHECK_BLOCKED")
        self.assertNotIn("private",str(safe.detail))

    def test_invalid_user_rejected_without_new_native_or_extra_session(self):
        data=copy.deepcopy(self.payload)
        data["controls"]["spec"]="protection"
        response=self.post("/api/v1/sessions/plan",data)
        self.assertEqual(response.status_code,422)
        self.assertEqual(response.json()["detail"]["code"],
                         "V106_DPS_ARCHETYPE_NOT_READY")
        self.assertFalse((self.root/"runs").exists())
        data=self.payload|{"unexpected":"not_allowed"}
        self.assertEqual(self.post("/api/v1/sessions/plan",data).status_code,422)

    def test_start_resume_duplicate_guard_and_deferred_cancel_no_real_simc(self):
        planned=self.plan()
        sid=planned["session_id"]
        child=mock.Mock()
        child.poll.return_value=None
        with mock.patch.object(web.subprocess,"Popen",return_value=child) as spawn:
            r=self.post("/api/v1/sessions/"+sid+"/resume")
            self.assertEqual(r.status_code,200,r.text)
            self.assertEqual(r.json()["status"],"WORKER_STARTED")
            self.assertEqual(r.json()["native_attempt_ceiling_cumulative"],6)
            self.assertTrue(r.json()["new_native_execution_permitted"])
            argv=spawn.call_args.args[0]
            self.assertEqual(argv[0],sys.executable)
            self.assertIn("v106_user_session_controller.py",argv[1])
            self.assertIn("--session",argv)
            self.assertNotIn("--cache-only",argv)
            self.assertEqual(self.post("/api/v1/sessions/"+sid+"/resume").status_code,
                             409)
            state=self.client.get("/api/v1/sessions/"+sid+"/status",
                                  headers=self.headers).json()
            self.assertTrue(state["active"])
            cancel=self.post("/api/v1/sessions/"+sid+"/cancel")
            self.assertEqual(cancel.status_code,200)
            self.assertIn("AFTER_CURRENT_NATIVE",cancel.json()["status"])
            self.assertTrue((self.root/"runs"/sid/"generated"/"CANCEL").is_file())
            spawn.assert_called_once()
        child.poll.return_value=0
        self.assertEqual(self.post("/api/v1/sessions/"+sid+"/cancel").status_code,409)

    def test_result_reads_previous_six_case_user_result_without_native(self):
        sid=self.plan()["session_id"]
        folder=self.root/"runs"/sid
        example=fake_native(hits=6)
        sessions.paths(folder)["final"].write_text(
            json.dumps(example),encoding="utf8")
        with mock.patch.object(web.subprocess,"Popen") as spawn:
            r=self.client.get("/api/v1/sessions/"+sid+"/result",
                              headers=self.headers)
            spawn.assert_not_called()
        self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(r.json()["final_T"],3182)
        self.assertEqual(r.json()["cache_hits_this_run"],6)
        self.assertFalse(r.json()["user_result"]["global_optimum_proven"])
        self.assertIn("95%",r.json()["display_text"])
        example["user_result"]["confidence_level"]=0.99
        sessions.paths(folder)["final"].write_text(json.dumps(example))
        self.assertEqual(self.client.get(
            "/api/v1/sessions/"+sid+"/result",headers=self.headers).status_code,422)

    def test_cache_only_never_launches_with_missing_real_json2_and_receipts(self):
        sid=self.plan()["session_id"]
        with mock.patch.object(web.subprocess,"Popen") as spawn:
            r=self.post("/api/v1/sessions/"+sid+"/cache-only")
            self.assertEqual(r.status_code,422,r.text)
            spawn.assert_not_called()
        self.assertIn("CACHE_ONLY_REQUIRES_COMPLETED_REAL_SESSION",
                      r.text)
        self.assertEqual(self.client.get("/api/v1/sessions/../../etc/status",
                          headers=self.headers).status_code,404)
        self.assertEqual(self.client.get(
            "/api/v1/sessions/1234/status",headers=self.headers).status_code,404)

    def test_legacy_windows_case_not_modified_by_health_or_results(self):
        self.plan()
        before={str(p.relative_to(self.root)):p.read_bytes()
                for p in (self.root/"runs").rglob("*") if p.is_file()}
        self.client.get("/api/v1/health")
        for p in self.root.joinpath("runs").iterdir():
            self.client.get("/api/v1/sessions/"+p.name+"/status",
                            headers=self.headers)
        after={str(p.relative_to(self.root)):p.read_bytes()
               for p in (self.root/"runs").rglob("*") if p.is_file()}
        self.assertEqual(before,after)

if __name__=="__main__":
    unittest.main()
