"""P3-BD optional SimC balance update: metadata diff only, 0 Native/DB2."""
import copy
import json
import unittest
from runner import v229_simc_only_source_seed as seed
from runner import v258_simc_update_source_delta as review
from tests.test_v229_simc_only_source_seed import (
    BUILD,REVISION,OLD,SimCCollectorTests,raw_sources)


def previous(*,full=False):
    raws=raw_sources()
    if full:
        raws["item_data.inc"]=(
            b"// Items, ilevel 1-1000, wow build "+BUILD.encode()+b"\n")
    return seed.inventory(raws,simc_revision=REVISION,expected_build=BUILD,
                          previous_game_build=OLD,season_event="mid_patch",
                          expected_git_blob={
                              name:seed.git_blob(raw) for name,raw in raws.items()})


class UpdateDiff(unittest.TestCase):
    def setUp(self):
        self.http=SimCCollectorTests(
            "test_collect_pinned_sources_without_any_legacy_data")
        self.http.setUp()
        self.calls=[]
    def transport(self,req,timeout):
        self.calls.append(req.full_url)
        return self.http.fetch(req,timeout=timeout)
    def tree_revision(self,rev):
        self.http.urls[seed.BASE+rev]=self.http.urls[seed.BASE+REVISION]
    def tree_item(self,data):
        url=seed.BASE+"d"*40
        doc=json.loads(self.http.urls[url])
        for r in doc["tree"]:
            if r["path"]=="item_data.inc":
                r.update({"sha":seed.git_blob(data),"size":len(data)})
        self.http.urls[url]=json.dumps(doc).encode()

    def test_same_exact_revision_zero_http_and_no_season_invalidation(self):
        result=review.compare(previous_receipt=previous(full=True),
                              next_revision_hint=REVISION,
                              transport=self.transport)
        self.assertEqual(result["requests_used"],0)
        self.assertEqual(self.calls,[])
        self.assertEqual(result["changed_files"],[])
        self.assertFalse(result["environment_rebuild_required_by_revision_change_alone"])
        self.assertFalse(result["static_environment_mutated"])
        self.assertFalse(result["dps_cache_reuse_across_distinct_binaries"])
        self.assertFalse(result["full_simc_equivalence_proven"])

    def test_new_simc_revision_four_metadata_queries_no_item_download(self):
        nxt="f"*40
        self.tree_revision(nxt)
        item=b"// Items, ilevel 1-1000, wow build "+BUILD.encode()+b"\n"
        self.tree_item(item)
        result=review.compare(previous_receipt=previous(full=True),
                              next_revision_hint=nxt,transport=self.transport)
        self.assertEqual(result["requests_used"],4)
        self.assertEqual(len(self.calls),4)
        self.assertTrue(all(x.startswith(seed.BASE) for x in self.calls))
        self.assertEqual(result["changed_files"],[])
        self.assertEqual(result["unobserved_files"],[])
        self.assertEqual(result["body_downloads"],0)
        self.assertEqual(result["native_calls"],0)
        self.assertFalse(result["full_simc_equivalence_proven"])
        self.assertFalse(result["season_membership_verified_by_this_check"])

    def test_three_file_seed_does_not_assume_item_data_is_unchanged(self):
        nxt="f"*40
        self.tree_revision(nxt)
        result=review.compare(previous_receipt=previous(),
                              next_revision_hint=nxt,transport=self.transport)
        self.assertEqual(result["unobserved_files"],["item_data.inc"])
        self.assertEqual(result["changed_files"],[])
        self.assertEqual(result["status"],
                         "TRACKED_ITEM_DATA_NOT_PREVIOUSLY_PINNED")
        self.assertEqual(result["requests_used"],4)

    def test_changed_gem_blob_only_warns_selected_source_not_rebuild(self):
        nxt="f"*40
        self.tree_revision(nxt)
        self.tree_item(
            b"// Items, ilevel 1-1000, wow build "+BUILD.encode()+b"\n")
        url=seed.BASE+"d"*40
        data=json.loads(self.http.urls[url])
        for row in data["tree"]:
            if row["path"]=="gem_data.inc":
                row["sha"]="e"*40
        self.http.urls[url]=json.dumps(data).encode()
        result=review.compare(previous_receipt=previous(full=True),
                              next_revision_hint=nxt,transport=self.transport)
        self.assertEqual(result["changed_files"],["gem_data.inc"])
        self.assertIn("GEM_PROPERTY_J",result["potentially_affected_sources"][
            "gem_data.inc"])
        self.assertFalse(result["static_environment_mutated"])
        self.assertFalse(result["environment_rebuild_required_by_revision_change_alone"])
        self.assertEqual(result["body_downloads"],0)

    def test_short_hint_resolution_one_call_when_same_commit(self):
        hint=REVISION[:7]
        lookup="https://api.github.com/repos/simulationcraft/simc/commits/"+hint
        self.http.urls[lookup]=json.dumps({"sha":REVISION}).encode()
        result=review.compare(previous_receipt=previous(),
                              next_revision_hint=hint,
                              transport=self.transport)
        self.assertEqual(result["requests_used"],1)
        self.assertEqual(self.calls,[lookup])

    def test_tampered_or_unpinned_prior_source_rejected_before_http(self):
        previous_doc=previous()
        previous_doc["source_files"]["gem_data.inc"]["git_blob_sha1"]="f"*40
        with self.assertRaisesRegex(
                seed.SimCSourceBlocked,"V258_PRIOR_RECEIPT_DIGEST_MISMATCH"):
            review.compare(previous_receipt=previous_doc,
                           next_revision_hint=REVISION,
                           transport=self.transport)
        unpinned=seed.inventory(raw_sources(),simc_revision=REVISION,
                                expected_build=BUILD,previous_game_build=OLD,
                                season_event="mid_patch")
        with self.assertRaisesRegex(
                seed.SimCSourceBlocked,"V258_PRIOR_GIT_PINNED_SOURCE_RECEIPT_REQUIRED"):
            review.compare(previous_receipt=unpinned,
                           next_revision_hint=REVISION,
                           transport=self.transport)
        self.assertEqual(self.calls,[])

    def test_simc_revision_generated_build_not_assumed_to_equal_old_build(self):
        nxt="f"*40
        self.tree_revision(nxt)
        result=review.compare(previous_receipt=previous(),
                              next_revision_hint=nxt,transport=self.transport)
        self.assertEqual(result["previous_generated_game_build"],BUILD)
        self.assertEqual(result["new_generated_game_build"],
                         "NOT_FETCHED_METADATA_ONLY")
        self.assertFalse(result["environment_rebuild_required_by_revision_change_alone"])


if __name__=="__main__":
    unittest.main()
