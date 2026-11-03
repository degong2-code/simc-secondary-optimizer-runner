"""P3-CE: original pinned Git files -> v217 -> original v211/v191 paths.

Offline deterministic Git-tree/raw responses, actual v217 receipt verification,
no game HTTP, Native, current equipment or existing season references.
"""
import io
import json
import pathlib
import sys
import tempfile
import unittest
from urllib.parse import urlsplit

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v189_simc_consumable_embellishment_discovery as handler
import v191_unified_season_data_update as v191
import v211_enchant_source_effect_classification as classifier
import v229_simc_only_source_seed as v229
import v274_zero_history_source_compiler_wiring as wiring
import v275_pinned_simc_compiler_inputs as v275
from tests.test_v229_simc_only_source_seed import raw_sources
from tests.test_v239_v211_fresh_season_dynamic_classifier import (
    BUILD,REV,fixture_source)


class MockResponse(io.BytesIO):
    status=200
    def __enter__(self):return self
    def __exit__(self,*exc):self.close()


class PinnedSimcInputs(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=pathlib.Path(tmp.name)/"brand-new-source-workspace"
        self.root.mkdir()
        self.folder=self.root/"source"/"v229_pinned_generated"
        self.folder.mkdir(parents=True)
        sources=raw_sources(build=BUILD)
        for name,raw in sources.items():
            (self.folder/name).write_bytes(raw)
        seed_doc=v229.inventory(
            sources,simc_revision=REV,expected_build=BUILD,
            previous_game_build=None,season_event="cold_start",
            expected_git_blob={name:v229.git_blob(raw)
                               for name,raw in sources.items()})
        (self.folder/v229.RECEIPT).write_text(json.dumps(seed_doc),encoding="utf8")
        self.pin={
            "source_dir":str(self.folder),
            "simc_receipt_sha256":seed_doc["receipt_sha256"],
            "source_stage":{
                "stage_id":"fresh-v229-pinned-simc-generated",
                "status":"EXECUTED_AND_SEALED",
                "receipt_sha256":"a"*64,
                "output_paths":{
                    **{name:"source/v229_pinned_generated/"+name
                       for name in sources},
                    v229.RECEIPT:"source/v229_pinned_generated/"+
                                 v229.RECEIPT}}}
        self.effect_root=self.root/"source"/"v258_same_season_consumable"
        self.effect_root.mkdir(parents=True)
        _,sources_v211=fixture_source()
        self.unique=sources_v211["unique_gear.cpp"].encode("utf8")
        (self.effect_root/"unique_gear_midnight.cpp").write_bytes(self.unique)
        handler_doc={"schema":handler.SCHEMA,
                     "source":{"sha256":v229.digest(self.unique),
                               "commit":REV}}
        (self.effect_root/"v189.json").write_text(
            json.dumps(handler_doc),encoding="utf8")
        self.consumables={
            "candidate_path":str(self.effect_root/"v190.json"),
            "source_stage":{
                "stage_id":"fresh-v189-v190-consumable-source",
                "status":"EXECUTED_AND_SEALED",
                "receipt_sha256":"b"*64,
                "output_paths":{
                    "v189":"source/v258_same_season_consumable/v189.json",
                    "simc_source":
                        "source/v258_same_season_consumable/unique_gear_midnight.cpp",
                }},
        }
        (self.effect_root/"v190.json").write_text("{}",encoding="utf8")
        body=sources_v211["permanent_enchant.inc"]
        permanent=(
            "// Permanent item enchants, wow build "+BUILD+"\n"
            "static constexpr std::array<permanent_enchant_entry_t, 2> "
            "__permanent_enchant_data { {\n"+
            "\n".join(body.splitlines()[1:])+"\n} };\n")
        self.remote={
            v275.COMPILER_INPUTS[name]:(
                permanent.encode("utf8") if name=="permanent_enchant.inc"
                else sources_v211[name].encode("utf8"))
            for name in v275.COMPILER_INPUTS}
        self.remote[handler.SOURCE]=self.unique
        tree_shas={
            "engine":"1"*40,"engine/dbc":"2"*40,
            "engine/dbc/generated":"3"*40,
            "engine/item":"4"*40,"engine/player":"5"*40}
        self.trees={REV:[{"path":"engine","type":"tree",
                         "sha":tree_shas["engine"]}]}
        for parent,child in (
            ("engine","dbc"),("engine/dbc","generated"),
            ("engine","item"),("engine","player")):
            key=REV if parent=="" else tree_shas[parent]
            self.trees.setdefault(key,[]).append({
                "path":child,"type":"tree",
                "sha":tree_shas[parent+"/"+child]})
        for file_path,raw in self.remote.items():
            folder,name=file_path.rsplit("/",1)
            self.trees.setdefault(tree_shas[folder],[]).append({
                "path":name,"type":"blob","sha":v229.git_blob(raw),
                "size":len(raw)})
        self.calls={"tree":0,"raw":0}

    def fetch(self,req,timeout):
        u=urlsplit(req.full_url)
        if u.hostname=="api.github.com":
            self.calls["tree"]+=1
            sha=u.path.split("/")[-1]
            assert sha in self.trees, sha
            return MockResponse(json.dumps({
                "tree":self.trees[sha],"truncated":False}).encode())
        if u.hostname=="raw.githubusercontent.com":
            self.calls["raw"]+=1
            path=u.path.split("/"+REV+"/",1)[-1]
            assert path in self.remote,path
            return MockResponse(self.remote[path])
        raise AssertionError("UNEXPECTED_URL: "+u.hostname)

    def collect(self):
        return v275.collect(
            stage_root=self.root,build=BUILD,pinned_simc=self.pin,
            consumables=self.consumables,transport=self.fetch)

    def test_empty_seed_producer_remains_pending_without_http(self):
        p=v275.collect(stage_root=self.root,build=BUILD,
                       pinned_simc={},consumables={},
                       transport=self.fetch)
        self.assertEqual(p["status"],v275.STATUS_PENDING)
        self.assertEqual(self.calls,{"tree":0,"raw":0})
        self.assertFalse(p["environment_ready"])

    def test_pinned_tree_verified_source_files_reused_without_http(self):
        one=self.collect()
        self.assertEqual(one["status"],
                         "PINNED_V211_AND_GENERATED_SOURCES_SEALED")
        self.assertEqual(one["source_stage"]["status"],"EXECUTED_AND_SEALED")
        self.assertEqual(self.calls["tree"],6)
        self.assertEqual(self.calls["raw"],5)
        self.assertEqual(one["network_calls_by_stage"],11)
        self.assertEqual(one["native_calls"],0)
        folder=pathlib.Path(one["source_dir"])
        manifest=json.loads(pathlib.Path(one["manifest_path"]).read_text())
        self.assertEqual(manifest["simc_revision"],REV)
        self.assertEqual(set(manifest["files"]),
                         set(classifier.FRESH_REQUIRED))
        self.assertEqual(manifest["files"]["unique_gear.cpp"]["source_path"],
                         handler.SOURCE)
        classifier.load_fresh_sources(folder,manifest,
                game_build=BUILD,simc_revision=REV)
        for kind,name in v191.GENERATED.items():
            self.assertEqual(v191.parse_generated(
                kind,(folder/name).read_bytes())["source_build"],BUILD)
        self.assertTrue((self.folder/v229.RECEIPT).is_file())
        self.assertFalse(one["environment_ready"])
        self.assertFalse(one["user_options_approved"])
        two=self.collect()
        self.assertEqual(two["source_stage"]["status"],"REUSED_VERIFIED")
        self.assertEqual(two["source_stage"]["receipt_writes"],0)
        self.assertEqual(two["network_calls_by_stage"],0)
        self.assertEqual(self.calls,{"tree":6,"raw":5})

        # Feed the actual sealed supplemental producer into the existing
        # v274 input selector: only TIER/G/F/O remain missing.
        report={"schema":"v216_fresh_source_stage_v1",
                "expected_game_build":BUILD,
                "snapshot_receipt_path":str(self.root/"wago"/"receipt.json"),
                "fresh_pinned_first_party_simc_source":self.pin,
                "fresh_pinned_v211_source":one,
                "simc_source_collection_context":{
                    "requested_game_event":"season_change"}}
        (self.root/"wago").mkdir()
        (self.root/"wago"/"receipt.json").write_text("{}")
        discover=wiring.discover(report)
        self.assertEqual(discover["status"],
                         "COLLECTED_COMPILER_INPUTS_PENDING")
        for solved in ("GENERATED_PERMANENT","GENERATED_TEMPORARY",
                       "GENERATED_GEM",
                       "SIMC_V211_SIX_SOURCE_FILES_AND_MANIFEST",
                       "PINNED_SIMC_REVISION"):
            self.assertIn(solved,discover["available"])
            self.assertNotIn(solved,discover["missing"])
        self.assertIn("TIER_V168",discover["missing"])
        self.assertFalse(discover["environment_ready"])

    def test_four_class_consumable_successor_reuses_original_simc_bytes(self):
        first=self.collect()
        before=dict(self.calls)
        self.consumables["source_stage"]["stage_id"]=(
            "fresh-v189-v190-consumable-physical-four-class")
        self.consumables["source_stage"]["receipt_sha256"]="d"*64
        second=self.collect()
        self.assertEqual(second["source_stage"]["status"],"REUSED_VERIFIED")
        self.assertEqual(second["source_stage"]["stage_id"],
                         first["source_stage"]["stage_id"])
        self.assertEqual(second["source_dir"],first["source_dir"])
        self.assertEqual(second["network_calls_by_stage"],0)
        self.assertEqual(self.calls,before)
        self.assertFalse(second["user_options_approved"])

    def test_four_class_from_empty_compiler_seals_successor(self):
        self.consumables["source_stage"]["stage_id"]=(
            "fresh-v189-v190-consumable-physical-four-class")
        self.consumables["source_stage"]["receipt_sha256"]="d"*64
        first=self.collect()
        self.assertEqual(first["source_stage"]["status"],"EXECUTED_AND_SEALED")
        self.assertEqual(first["source_stage"]["stage_id"],
                         "fresh-pinned-v211-from-four-subclass-consumables")
        second=self.collect()
        self.assertEqual(second["source_stage"]["status"],"REUSED_VERIFIED")
        self.assertEqual(second["network_calls_by_stage"],0)
        self.assertEqual(self.calls,{"tree":6,"raw":5})

    def test_tamper_sealed_source_blocks_without_http_retry(self):
        one=self.collect()
        pathlib.Path(one["source_dir"],"permanent_enchant.inc").write_bytes(
            b"tampered")
        before=dict(self.calls)
        with self.assertRaisesRegex(
                v275.SimCCompilerInputBlocked,"STAGE_OUTPUT_HASH_MISMATCH"):
            self.collect()
        self.assertEqual(self.calls,before)

    def test_wrong_pinned_git_blob_fails_closed(self):
        self.remote[v275.COMPILER_INPUTS["permanent_enchant.inc"]]=b"wrong"
        with self.assertRaisesRegex(v275.SimCCompilerInputBlocked,
                                    "V275_PINNED_SOURCE_BLOB_SHA_MISMATCH"):
            self.collect()
        self.assertFalse((self.root/v275.OUTPUTS["manifest"]).is_file())


if __name__=="__main__":
    unittest.main()
