"""v229 strict SimC-generated cold-start source discovery, without legacy sources."""
from __future__ import annotations

import copy
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

from runner import v229_simc_only_source_seed as seed


REVISION = "a" * 40
BUILD = "12.2.0.99999"
OLD = "12.1.5.70575"


def raw_sources(build=BUILD):
    sets=(
        "// Set bonus data, wow build " + build + "\n"
        "static constexpr std::array<item_set_bonus_t, 3> __set_bonus_data { {\n"
        '  { "Plain class set", "season_token_test", "SYN1", 3, 1234, 2, 1, 71, -1, 4567, { 9001, 9002, 9003, 9004, 9005, 0 } },\n'
        '  { "Plain class set", "season_token_test", "SYN1", 3, 1234, 4, 1, 72, -1, 4568, { 9001, 9002, 9003, 9004, 9005, 0 } },\n'
        '  { "Short class set", "separate_option", "OLD", 1, 9876, 2, 2, 73, -1, 7654, { 4444, 5555, 0 } },\n'
        "} };\n"
    )
    gems=(
        "// Gem properties, wow build " + build + "\n"
        "static constexpr std::array<gem_property_data_t, 2> __gem_property_data { {\n"
        "  {    2,  2686, 0x00000002, 0 }, // +$k1 Strength\n"
        "  {    3,  2687, 0x00000008, 0 }, // +$k1 Agility\n"
        "} };\n"
    )
    oil=(
        "// Temporary item enchants, wow build " + build + "\n"
        "static constexpr std::array<temporary_enchant_entry_t, 2> __temporary_enchant_data { {\n"
        '  {  2713,  0,   29453, "test_oil" },\n'
        '  {  2714,  1,   29454, "test_oil" },\n'
        "} };\n"
    )
    return {"item_set_bonus.inc":sets.encode(),
            "gem_data.inc":gems.encode(),
            "temporary_enchant.inc":oil.encode()}


def inventory(raw=None, **opts):
    return seed.inventory(
        raw if raw is not None else raw_sources(),
        simc_revision=REVISION, expected_build=BUILD,
        previous_game_build=OLD, season_event="season_change",
        **opts)


class SimCOnlySeedTests(unittest.TestCase):
    def test_standalone_source_only_candidate_inventory(self):
        result=inventory()
        self.assertEqual(result["candidate_class_set_count"],2)
        self.assertEqual(result["set_bonus_source_rows"],3)
        self.assertEqual(result["gem_property_candidate_count"],2)
        self.assertEqual(result["temporary_enchant_candidate_count"],2)
        self.assertEqual(result["set_bonus_candidate_groups"][0][
            "observed_bonus_sizes"],[2,4] if result[
            "set_bonus_candidate_groups"][0]["set_opt"]=="season_token_test" else [2])
        self.assertIsNone(result["G"])
        self.assertIsNone(result["J"])
        self.assertIsNone(result["F"])
        self.assertIsNone(result["O"])
        self.assertIsNone(result["B"])
        self.assertIsNone(result["T"])
        self.assertFalse(result["environment_ready"])
        self.assertTrue(result["active_season_not_automatically_inferred"])
        self.assertFalse(result["provenance_tree_blob_authenticated"])
        self.assertEqual(result["native_calls"],0)

    def test_build_mismatch_is_never_reinterpreted_as_new_season(self):
        raw=raw_sources()
        raw["gem_data.inc"]=raw_sources(OLD)["gem_data.inc"]
        with self.assertRaisesRegex(seed.SimCSourceBlocked,
                                    "GENERATED_SIMC_COMPILED_BUILD_MISMATCH"):
            inventory(raw)
        with self.assertRaisesRegex(seed.SimCSourceBlocked,
                                    "NEW_SEASON_OLD_BUILD_REUSE_BLOCKED"):
            seed.inventory(raw_sources(OLD),simc_revision=REVISION,
                           expected_build=OLD,previous_game_build=OLD)

    def test_gem_and_oil_candidates_may_not_prove_quality_or_rating(self):
        result=inventory()
        self.assertEqual(result["source_files"]["temporary_enchant.inc"][
            "source_row_count"],2)
        self.assertTrue("GEM_ITEM_ID_QUALITY_SOCKET_J" in result[
            "missing_proofs"])
        self.assertTrue("WEAPON_OIL_ITEM_ID_HANDS_RATING_O" in result[
            "missing_proofs"])
        self.assertEqual(result["user_options_auto_admitted"],False)

    def test_full_git_blob_provenance_validates_exact_bytes(self):
        raw=raw_sources()
        blob={k:seed.git_blob(v) for k,v in raw.items()}
        result=inventory(raw,expected_git_blob=blob)
        self.assertTrue(result["provenance_tree_blob_authenticated"])
        self.assertEqual(result["source_files"]["gem_data.inc"][
            "git_blob_sha1"],blob["gem_data.inc"])
        blob["gem_data.inc"]="f"*40
        with self.assertRaisesRegex(seed.SimCSourceBlocked,
                                    "PINNED_SIMC_GIT_BLOB_MISMATCH"):
            inventory(raw,expected_git_blob=blob)

    def test_raw_set_bonuses_do_not_choose_current_season_by_name(self):
        result=inventory()
        values=result["set_bonus_candidate_groups"]
        self.assertEqual(len(values),2)
        self.assertEqual({v["set_opt"] for v in values},
                         {"season_token_test","separate_option"})
        self.assertTrue(result["active_season_not_automatically_inferred"])

    def test_set_bonus_conflicting_items_or_count_blocks(self):
        raw=raw_sources()
        raw["item_set_bonus.inc"]=raw["item_set_bonus.inc"].replace(
            b"4568, { 9001, 9002, 9003, 9004, 9005",
            b"4568, { 9001, 9002, 9003, 9004, 9999")
        with self.assertRaisesRegex(seed.SimCSourceBlocked,
                                    "SET_BONUS_CLASS_GROUP_CONFLICT"):
            inventory(raw)
        raw=raw_sources()
        raw["item_set_bonus.inc"]=raw["item_set_bonus.inc"].replace(
            b"item_set_bonus_t, 3",b"item_set_bonus_t, 4")
        with self.assertRaisesRegex(seed.SimCSourceBlocked,
                                    "SET_BONUS_ROW_COUNT_DRIFT"):
            inventory(raw)

    def test_optional_item_data_is_build_scoped_but_does_not_activate_G(self):
        raw=raw_sources()
        raw["item_data.inc"]=b"// Items, ilevel 1-1000, wow build "+BUILD.encode()+b"\n"
        result=inventory(raw)
        self.assertTrue(result["item_data_present"])
        self.assertIsNone(result["G"])
        raw["item_data.inc"]=b"// Items, ilevel 1-1000, wow build "+OLD.encode()+b"\n"
        with self.assertRaisesRegex(seed.SimCSourceBlocked,
                                    "ITEM_DATA_BUILT_FOR_DIFFERENT_GAME_BUILD"):
            inventory(raw)

    def test_source_file_scope_and_old_revision_untrusted(self):
        raw=raw_sources()
        raw["gear.json"]=b"{}"
        with self.assertRaisesRegex(seed.SimCSourceBlocked,
                                    "FIXED_SIMC_GENERATED_FILES_ONLY"):
            inventory(raw)
        with self.assertRaisesRegex(seed.SimCSourceBlocked,
                                    "PINNED_SIMC_REVISION_BUILD"):
            seed.inventory(raw_sources(),simc_revision="latest",
                           expected_build=BUILD,previous_game_build=OLD)

    def test_same_source_receipt_is_deterministic(self):
        a,b=inventory(),inventory()
        self.assertEqual(a,b)
        self.assertEqual(a["receipt_sha256"],seed.digest(
            seed.canonical({k:v for k,v in a.items()
                             if k!="receipt_sha256"}).encode("utf8")))


class FakeResponse:
    def __init__(self,data):
        self.data=data
        self.status=200
        self.offset=0
    def __enter__(self):return self
    def __exit__(self,*_):return False
    def read(self,n):
        chunk=self.data[self.offset:self.offset+n]
        self.offset+=len(chunk)
        return chunk


class SimCCollectorTests(unittest.TestCase):
    def setUp(self):
        self.raw=raw_sources()
        self.urls={}
        self.root_tree=REVISION
        children=[("engine","b"*40),("dbc","c"*40),
                  ("generated","d"*40)]
        for parent,(name,child) in zip(
            [REVISION, "b"*40, "c"*40],children):
            self.urls[seed.BASE+parent]=json.dumps({
                "tree":[{"path":name,"sha":child,"type":"tree"}]
            }).encode()
        self.urls[seed.BASE+"d"*40]=json.dumps({"tree":[
            {"path":name,"sha":seed.git_blob(raw),
             "size":len(raw),"type":"blob"}
            for name,raw in self.raw.items()] + [{
                "path":seed.OPTIONAL_ITEM_FILE, "sha":"e"*40,
                "size":1234,"type":"blob"}]}).encode()
        for name,raw in self.raw.items():
            self.urls[seed.RAW_BASE+REVISION+
                      "/engine/dbc/generated/"+name]=raw

    def fetch(self,request,timeout=None):
        url=request.full_url
        if url not in self.urls:
            raise ValueError("UNLISTED_URL:"+url)
        return FakeResponse(self.urls[url])

    def test_collect_pinned_sources_without_any_legacy_data(self):
        with tempfile.TemporaryDirectory() as td:
            path=pathlib.Path(td)/"fresh"
            result=seed.collect(
                revision=REVISION,expected_build=BUILD,
                previous_game_build=OLD,
                season_event="season_change",dest=path,
                transport=self.fetch)
            self.assertTrue(path.is_dir())
            self.assertTrue(result["provenance_tree_blob_authenticated"])
            self.assertEqual(result["candidate_class_set_count"],2)
            self.assertEqual({x.name for x in path.iterdir()},
                             set(self.raw)|{seed.RECEIPT})
            self.assertEqual(json.loads((path/seed.RECEIPT).read_text())[
                "receipt_sha256"],result["receipt_sha256"])
            with self.assertRaisesRegex(seed.SimCSourceBlocked,
                                        "DESTINATION_MUST_BE_NEW"):
                seed.collect(
                    revision=REVISION,expected_build=BUILD,
                    previous_game_build=OLD,
                    dest=path,transport=self.fetch)

    def test_blob_verification_catches_same_length_tampering(self):
        key=seed.RAW_BASE+REVISION+"/engine/dbc/generated/gem_data.inc"
        self.urls[key]=self.urls[key].replace(b"2686",b"2685",1)
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(seed.SimCSourceBlocked,
                                        "SOURCE_BLOB_CHANGED"):
                seed.collect(revision=REVISION,expected_build=BUILD,
                    previous_game_build=OLD,dest=pathlib.Path(td)/"fresh",
                    transport=self.fetch)
            self.assertFalse((pathlib.Path(td)/"fresh").exists())

    def test_collector_does_not_fetch_unrequested_full_item_data(self):
        with tempfile.TemporaryDirectory() as td:
            seed.collect(revision=REVISION,expected_build=BUILD,
                    previous_game_build=OLD,dest=pathlib.Path(td)/"fresh",
                    transport=self.fetch)
            self.assertNotIn(
                seed.RAW_BASE+REVISION+"/engine/dbc/generated/item_data.inc",
                self.urls)


if __name__=="__main__":
    unittest.main()
