"""P3-AX: lazy v229 full item_data extension, no duplicate 3 small HTTPs.

All upstream HTTP and SimC data are synthetic; G and environment remain null.
"""
import json
import pathlib
import sys
import tempfile
import unittest
from urllib.error import HTTPError

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v216_environment_build_coordinator as build
import v229_simc_only_source_seed as source
from tests.test_v229_simc_only_source_seed import (
    BUILD,OLD,REVISION,SimCCollectorTests,FakeResponse)


class LazyFullPinnedSource(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=pathlib.Path(self.temp.name)
        self.fake=SimCCollectorTests("test_collect_pinned_sources_without_any_legacy_data")
        self.fake.setUp()
        self.small=self.root/"small"
        source.collect(revision=REVISION,expected_build=BUILD,
                       previous_game_build=OLD,dest=self.small,
                       transport=self.fake.fetch)
        self.item=b"// Items, ilevel 1-1000, wow build "+BUILD.encode()+b"\n"
        tree_url=source.BASE+"d"*40
        tree=json.loads(self.fake.urls[tree_url])
        entry=next(x for x in tree["tree"] if x["path"]=="item_data.inc")
        entry["sha"]=source.git_blob(self.item)
        entry["size"]=len(self.item)
        self.fake.urls[tree_url]=json.dumps(tree).encode()
        self.item_url=(source.RAW_BASE+REVISION+
                       "/engine/dbc/generated/item_data.inc")
        self.fake.urls[self.item_url]=self.item
        self.calls=[]
        self.gear={"candidate_path":"/synthetic/not_read_gear.json"}
        self.tier={"candidate_path":"/synthetic/not_read_tier.json"}
        self.request={"class":"paladin","spec":"retribution",
                      "target_ilevel":334}

    def fetch(self,req,timeout):
        self.calls.append(req.full_url)
        return self.fake.fetch(req,timeout=timeout)

    def run_stage(self):
        return build._lazy_full_pinned_simc_item_stage(
            stage_root=self.root,build=BUILD,small_seed_dir=self.small,
            gear_candidate=self.gear,tier_bridge=self.tier,
            request=self.request,transport=self.fetch)

    def test_five_http_first_run_zero_reuse_and_original_small_unchanged(self):
        old=(self.small/source.RECEIPT).read_bytes()
        first=self.run_stage()
        second=self.run_stage()
        self.assertEqual(first["status"],
                         "FRESH_FULL_PINNED_SIMC_ITEM_DATA_SOURCE_ONLY")
        self.assertEqual(first["network_calls_by_stage"],5)
        self.assertEqual(second["network_calls_by_stage"],0)
        self.assertEqual(first["source_stage"]["status"],"EXECUTED_AND_SEALED")
        self.assertEqual(second["source_stage"]["status"],"REUSED_VERIFIED")
        self.assertEqual(self.calls.count(self.item_url),1)
        self.assertEqual(len(self.calls),5)
        self.assertTrue(all("item_data.inc" in x or
                            x.startswith(source.BASE) for x in self.calls))
        self.assertEqual((self.small/source.RECEIPT).read_bytes(),old)
        self.assertFalse((self.small/"item_data.inc").exists())
        full=pathlib.Path(first["source_dir"])
        self.assertEqual((full/"item_data.inc").read_bytes(),self.item)
        self.assertTrue(all((full/name).read_bytes()==(self.small/name).read_bytes()
                            for name in source.SOURCE_FILES))
        receipt=json.loads((full/source.RECEIPT).read_text())
        self.assertTrue(receipt["item_data_present"])
        self.assertTrue(receipt["provenance_tree_blob_authenticated"])
        self.assertEqual(receipt["source_files"]["item_data.inc"]["git_blob_sha1"],
                         source.git_blob(self.item))
        self.assertIsNone(first["G"])
        self.assertFalse(first["environment_ready"])
        self.assertEqual(first["native_calls"],0)

    def test_no_eligible_candidate_or_no_request_causes_zero_http(self):
        self.gear={"candidate_path":None}
        row=self.run_stage()
        self.assertEqual(row["network_calls_by_stage"],0)
        self.assertIsNone(row["source_dir"])
        self.assertFalse(row["environment_ready"])
        self.gear={"candidate_path":"x"}
        self.request=None
        row=self.run_stage()
        self.assertEqual(row["network_calls_by_stage"],0)
        self.assertEqual(self.calls,[])

    def test_tampered_small_source_fails_before_http(self):
        path=self.small/"gem_data.inc"
        path.write_bytes(path.read_bytes()+b"tamper")
        with self.assertRaisesRegex(
                build.EnvironmentBuildBlocked,
                "V216_FULL_SIMC_SMALL_SOURCE_CHANGED"):
            self.run_stage()
        self.assertEqual(self.calls,[])

    def test_git_tree_item_blob_mismatch_remains_pending_not_installed(self):
        self.fake.urls[self.item_url]=self.item+b"changed"
        result=self.run_stage()
        self.assertEqual(result["status"],
                         "FRESH_FULL_PINNED_SIMC_SOURCE_PENDING")
        self.assertEqual(result["reason"],
                         "V216_FULL_SIMC_ITEM_DATA_GIT_BLOB_MISMATCH")
        self.assertEqual(result["network_calls_by_stage"],5)
        self.assertFalse(result["environment_ready"])
        self.assertIsNone(result["source_dir"])


    def test_lazy_full_item_raw_403_uses_same_tree_blob_and_reuses_receipt(self):
        api=source.GIT_BLOB_BASE+source.git_blob(self.item)
        self.fake.urls[api]=self.item
        def fetch(req,timeout):
            self.calls.append(req.full_url)
            if req.full_url==self.item_url:
                raise HTTPError(self.item_url,403,"Forbidden",{},None)
            return self.fake.fetch(req,timeout=timeout)
        self.fetch=fetch
        result=self.run_stage()
        again=self.run_stage()
        self.assertEqual(result["status"],
                         "FRESH_FULL_PINNED_SIMC_ITEM_DATA_SOURCE_ONLY")
        self.assertEqual(result["network_calls_by_stage"],6)
        self.assertEqual(again["network_calls_by_stage"],0)
        self.assertEqual(self.calls.count(api),1)
        self.assertEqual(self.calls.count(self.item_url),1)
        self.assertEqual((pathlib.Path(result["source_dir"])/"item_data.inc"
                         ).read_bytes(),self.item)
        self.assertFalse(result["environment_ready"])

    def test_lazy_full_raw_403_api_wrong_sha_stays_pending(self):
        api=source.GIT_BLOB_BASE+source.git_blob(self.item)
        self.fake.urls[api]=self.item+b"MALFORMED"
        def fetch(req,timeout):
            self.calls.append(req.full_url)
            if req.full_url==self.item_url:
                raise HTTPError(self.item_url,403,"Forbidden",{},None)
            return self.fake.fetch(req,timeout=timeout)
        self.fetch=fetch
        result=self.run_stage()
        self.assertEqual(result["status"],
                         "FRESH_FULL_PINNED_SIMC_SOURCE_PENDING")
        self.assertEqual(result["reason"],
                         "V229_EXACT_GIT_BLOB_API_CONTENT_INVALID")
        self.assertEqual(result["network_calls_by_stage"],6)
        self.assertFalse(result["environment_ready"])

    def test_item_data_from_other_build_cannot_complete_source(self):
        self.fake.urls[self.item_url]=(self.item.replace(
            BUILD.encode(),OLD.encode()))
        self.fake.urls[source.BASE+"d"*40]=json.dumps({
            "tree":[*(json.loads(self.fake.urls[source.BASE+"d"*40])["tree"][:-1]),
                {"path":"item_data.inc","sha":
                 source.git_blob(self.fake.urls[self.item_url]),
                 "size":len(self.fake.urls[self.item_url]),"type":"blob"}]
        }).encode()
        result=self.run_stage()
        self.assertEqual(result["status"],
                         "FRESH_FULL_PINNED_SIMC_SOURCE_PENDING")
        self.assertEqual(result["reason"],
                         "V229_ITEM_DATA_BUILT_FOR_DIFFERENT_GAME_BUILD")
        self.assertEqual(result["network_calls_by_stage"],5)
        self.assertFalse(result["environment_ready"])


if __name__=="__main__":
    unittest.main()
