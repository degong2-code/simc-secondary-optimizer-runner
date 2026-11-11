"""v335: genuine source-only ko_KR Environment Build pipeline, no Native."""
import json
import pathlib
import tempfile
import unittest
from unittest import mock

from runner import v335_environment_official_ko_localization as loc
from runner import v332_blizzard_ko_item_labels as v332
from runner import v167_product_season_gear_adapter as gear
from runner import v113_local_web_api as web


def install(build="12.1.5.70783",id=280001):
    return {
        "game_build":build,"target_ilevel":334,
        "official_F_physical_source":{"physical_item_id":id},
        "official_O_physical_source":None,
        "published_verified_options":[]}


class EnvironmentKoTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        self.verify=mock.patch.object(
            loc.manifests,"verify_fresh_installed_environment",return_value=None)
        self.verify.start()
        self.addCleanup(self.verify.stop)

    def fake_get(self,url,*,headers=None):
        item_id=int(url.split("/data/wow/item/")[1].split("?")[0])
        self.assertTrue(headers["Authorization"].startswith("Bearer "))
        self.assertIn("locale=ko_KR",url)
        return {"id":item_id,"name":"공식 테스트 이름 "+str(item_id)}

    def test_incremental_reuses_prior_same_build_only_and_does_not_fetch_again(self):
        build="12.1.5.70783"
        base=install(build)
        with (mock.patch.dict("os.environ",{"BLIZZARD_ACCESS_TOKEN":"unit-token"}),
              mock.patch.object(loc.blizzard,"request_json",
                                side_effect=self.fake_get) as get):
            first=loc.build_from_verified_install(self.root,base,allow_network=True)
            self.assertEqual(first["status"],loc.STATUS_READY)
            self.assertEqual(first["new_official_name_records"],1)
            self.assertEqual(first["native_calls_now"],0)
            self.assertEqual(first["network_calls_now"],1)
            self.assertEqual(get.call_count,1)
            again=loc.build_from_verified_install(self.root,base,allow_network=True)
            self.assertEqual(again["new_official_name_records"],0)
            self.assertEqual(again["network_calls_now"],0)
            self.assertEqual(get.call_count,1)
            changed=dict(base)
            changed["published_verified_options"]=[
                {"item_id":280003,"ui_selectable":True}]
            partial=loc.build_from_verified_install(self.root,changed,
                                                   allow_network=True)
            self.assertEqual(partial["new_official_name_records"],1)
            self.assertEqual(get.call_count,2)
            self.assertEqual(partial["verified_names"],2)
            self.assertEqual(loc.read_names(self.root,build,{280001,280003}),{
                280001:"공식 테스트 이름 280001",
                280003:"공식 테스트 이름 280003"})
            not_reused=loc.read_names(self.root,"12.1.5.70999",{280001})
            self.assertEqual(not_reused,{})

    def test_gems_oils_and_user_published_only_not_raw_candidates(self):
        selected=install()
        selected["official_O_physical_source"]={
            "selected_oil_item_ids_by_hand":{"main_hand":280005,
                                             "off_hand":280006}}
        selected["published_verified_options"]=[
            {"item_id":280007,"ui_selectable":True},
            {"item_id":280008,"ui_selectable":False},
            {"item_id":280009,"ui_selectable":True}]
        layout={"ordinary_gem_ids":[280011,280012,280013,280014],
                "special_gem_id":None}
        roles=loc.verified_environment_items(selected,layout)
        self.assertEqual(roles[280001],["flask"])
        self.assertEqual(roles[280005],["weapon_oil"])
        self.assertEqual(roles[280014],["ordinary_gem"])
        self.assertEqual(roles[280009],["verified_enchant"])
        self.assertNotIn(280008,roles)
        result=loc.build_from_verified_install(
            self.root,selected,layout,allow_network=False)
        self.assertEqual(result["pending_names"],9)
        self.assertEqual(result["native_calls_now"],0)
        self.assertEqual(result["network_calls_now"],0)
        self.assertEqual(result["status"],loc.STATUS_PARTIAL)
        self.assertFalse(result["source_only_names_not_item_approval"] is False)

    def test_pinned_77_static_names_reused_without_network_or_new_approval(self):
        product=gear.public_options(gear.read())
        build=product["season_build"]
        source=install(build)
        source["official_F_physical_source"]=None
        with mock.patch.object(loc.blizzard,"request_json") as get:
            result=loc.build_from_verified_install(
                self.root,source,catalog=product,allow_network=False)
        ids={x["item_id"] for role in
            ("trinket","special_effect_gear_candidate")
            for x in product["choices"][role]}
        self.assertEqual(len(ids),77)
        self.assertEqual(result["verified_names"],77)
        self.assertGreaterEqual(result["selected_item_count"],77)
        self.assertIn(result["status"],(loc.STATUS_READY,loc.STATUS_PARTIAL))
        self.assertEqual(loc.read_names(self.root,build,{158367})[158367],
                         "메레크타의 송곳니")
        get.assert_not_called()

    def test_no_candidate_does_not_create_empty_cache(self):
        empty=install()
        empty["official_F_physical_source"]=None
        result=loc.build_from_verified_install(self.root,empty,
                                               allow_network=False)
        self.assertEqual(result["status"],"PENDING_VERIFIED_CHOICE_SOURCE")
        self.assertFalse(loc._path(self.root,empty["game_build"]).exists())

    def test_corrupted_cache_fails_closed_and_never_destroys_core_budget(self):
        b=install()
        loc.build_from_verified_install(self.root,b,allow_network=False)
        path=loc._path(self.root,b["game_build"])
        doc=json.loads(path.read_text(encoding="utf8"))
        doc["manifest_sha256"]="a"*64
        path.write_text(json.dumps(doc),encoding="utf8")
        self.assertEqual(loc.read_names(self.root,b["game_build"],{280001}),{})
        self.assertEqual(loc.cache_status(self.root,b["game_build"])["status"],
                         "OFFICIAL_KO_CACHE_INVALID")
        with self.assertRaises(loc.LocalizationBlocked):
            loc.build_from_verified_install(self.root,b,allow_network=False)
        jobs=web.LocalJobs(self.root)
        with mock.patch.object(loc,"build_for_environment",
                               side_effect=loc.LocalizationBlocked("bad")):
            result=jobs._with_verified_ko_localization(
                b["game_build"],334,{"environment_ready":True,"G":2850,
                    "J":92,"F":165,"B":3107,"T":3107})
        self.assertEqual(result["B"],3107)
        self.assertEqual(result["official_ko_localization"]["status"],
                         "OFFICIAL_KO_SOURCE_OR_CACHE_REQUIRES_REVIEW")

    def test_sealed_v212_bridge_is_not_a_user_item_admission_endpoint(self):
        doc=install()
        doc["manifest_sha256"]="a"*64
        source=self.root/"v212_installed_fake.json"
        source.write_text(json.dumps(doc),encoding="utf8")
        result={"environment_ready":True,"environment_installed":True,
                "source_compilation":{
                    "verified_environment_install":{
                        "stage_output_path":str(source),
                        "manifest_sha256":"a"*64}}}
        with mock.patch.object(loc,"exact_product_catalog",return_value=None):
            found=loc.build_for_environment(
                self.root,doc["game_build"],result,target_ilevel=334)
        self.assertEqual(found["selected_item_count"],1)
        self.assertEqual(found["status"],loc.STATUS_PARTIAL)
        with self.assertRaises(loc.LocalizationBlocked):
            loc.build_for_environment(
                self.root,doc["game_build"],result,target_ilevel=335)

    def test_readonly_endpoint_does_not_network_or_create_session(self):
        with mock.patch.object(loc.blizzard,"request_json") as get:
            client=web.create_app(root=self.root,token="v335-token")
            from fastapi.testclient import TestClient
            with TestClient(client,base_url="http://127.0.0.1:8765") as api:
                response=api.get(
                    "/api/v1/environment/official-ko-localization",
                    params={"game_build":"12.1.5.70783"},
                    headers={"x-simc-local-token":"v335-token",
                             "origin":"http://127.0.0.1:8765"})
            self.assertEqual(response.status_code,200,response.text)
            self.assertEqual(response.json()["status"],
                             "OFFICIAL_KO_CACHE_NOT_INSTALLED")
            self.assertEqual(response.json()["native_calls_now"],0)
            get.assert_not_called()

if __name__=="__main__":unittest.main()
