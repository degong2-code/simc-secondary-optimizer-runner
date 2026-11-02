"""No Native/network: new-season G/J/F/O source inventory fails closed."""
import copy
import hashlib
import json
import pathlib
import tempfile
import unittest

from runner import v213_source_to_catalog as catalog_bridge
from runner import v224_season_gjfo_evidence_inventory as p
from tests.test_v213_source_to_catalog import SourceToCatalogTests

ROOT=pathlib.Path(__file__).resolve().parents[1]


def fixture(*,event="mid_patch",build="12.1.5.70575"):
    source=SourceToCatalogTests()
    source.setUpClass()
    season, classification=source.build_inputs()
    gear=copy.deepcopy(source.gear_source)
    tier=copy.deepcopy(source.tier_source)
    budget=json.loads((ROOT/"data/current_season_chmv_consumables.json").read_text("utf8"))
    gear["season_build"]=tier["retail_build"]=budget["retail_build"]=build
    season["game_build"]=classification["season_game_build"]=build
    season["source_artifacts"]["v190"]["game_build"]=build
    season["update_event"]=event
    season["simc_generated_builds"]={
        name:build for name in ("permanent_enchant","temporary_enchant","gem_property")}
    for name in season["simc_generated_sources"]:
        season["simc_generated_sources"][name]["source_build"]=build
    files={"gear":gear,"tier":tier,"budget":budget}
    hashes={key:hashlib.sha256(p.canonical(val).encode("utf8")).hexdigest()
            for key,val in files.items()}
    season["sha256_by_input"].update(hashes)
    catalog=catalog_bridge.compile_catalog(season,"a"*64,classification,"b"*64)
    catalog_bridge.verify_catalog(catalog)
    return season,catalog,{
        key:(files[key],hashes[key]) for key in files}


def inventory(season,catalog,inputs,*,event="mid_patch",
              old=None,ilvl=334):
    return p.compile_inventory(
        v191=season,v191_sha="a"*64,v213=catalog,v213_sha="d"*64,
        inputs=inputs,event=event,target_ilevel=ilvl,
        previous_game_build=old)


class SeasonGjfoInventoryTests(unittest.TestCase):
    def test_midpatch_observed_sources_are_not_quantitative_certification(self):
        season,catalog,inputs=fixture()
        result=inventory(season,catalog,inputs)
        self.assertEqual(result["verified_components"],[])
        self.assertEqual(result["required_components"],["G","J","F","O"])
        self.assertTrue(all(row["rating"] is None for row in
            result["component_state"].values()))
        self.assertIsNone(result["B"])
        self.assertIsNone(result["T"])
        self.assertFalse(result["budget_can_be_published"])
        self.assertFalse(result["automatic_ui_admission"])
        self.assertEqual(result["native_calls"],0)
        payload={k:v for k,v in result.items() if k!="receipt_sha256"}
        self.assertEqual(p.digest(p.canonical(payload).encode("utf8")),
                         result["receipt_sha256"])

    def test_season_change_has_new_build_but_does_not_reuse_old_values(self):
        season,catalog,inputs=fixture(event="season_change",
                                     build="12.2.0.99999")
        result=inventory(season,catalog,inputs,event="season_change",
                         old="12.1.5.70575",ilvl=335)
        self.assertEqual(result["game_build"],"12.2.0.99999")
        self.assertEqual(result["target_ilevel"],335)
        self.assertEqual(result["status"],
                         "BLOCKED_MANDATORY_GJFO_NOT_IN_V191_V213_RAW_SOURCES")
        self.assertEqual(set(result["component_state"]),{"G","J","F","O"})
        self.assertNotIn("138",p.canonical(result))
        self.assertNotIn("165",p.canonical(result))

    def test_existing_build_relabelled_new_season_must_fail(self):
        season,catalog,inputs=fixture(event="season_change")
        with self.assertRaisesRegex(p.SeasonEvidenceBlocked,
                                    "CANNOT_REUSE_PREVIOUS_GAME_BUILD"):
            inventory(season,catalog,inputs,event="season_change",
                      old="12.1.5.70575")

    def test_new_season_missing_previous_build_must_fail(self):
        season,catalog,inputs=fixture(event="expansion_change",
                                     build="13.0.0.99999")
        with self.assertRaisesRegex(p.SeasonEvidenceBlocked,
                                    "REQUIRES_PREVIOUS_BUILD"):
            inventory(season,catalog,inputs,event="expansion_change")

    def test_source_hash_mismatch_blocks(self):
        season,catalog,inputs=fixture()
        tampered=dict(inputs)
        tampered["budget"]=(dict(inputs["budget"][0]),"d"*64)
        with self.assertRaisesRegex(p.SeasonEvidenceBlocked,
                                    "BUDGET_SOURCE_DIGEST_MISMATCH"):
            inventory(season,catalog,tampered)

    def test_build_drift_does_not_reinterpret_gear_as_native_G(self):
        season,catalog,inputs=fixture()
        bad=dict(inputs)
        bad["gear"]=(dict(inputs["gear"][0],season_build="13.0.0.9"),
                     inputs["gear"][1])
        with self.assertRaisesRegex(p.SeasonEvidenceBlocked,
                                    "CATALOG_BUILD_OR_REPRESENTATIVE"):
            inventory(season,catalog,bad)

    def test_wrong_requested_event_or_v191_digest_blocks(self):
        season,catalog,inputs=fixture()
        with self.assertRaisesRegex(p.SeasonEvidenceBlocked,
                                    "REQUEST_EVENT_NOT_MATCHING"):
            inventory(season,catalog,inputs,event="season_change",
                      old="12.1.5.70575")
        catalog2=copy.deepcopy(catalog)
        catalog2["source_provenance"]["v191"]["sha256"]="b"*64
        with self.assertRaisesRegex(p.SeasonEvidenceBlocked,"V213_SEAL_INVALID"):
            inventory(season,catalog2,inputs)

    def test_simc_compiled_build_mismatch_stays_warning_not_ready(self):
        season,catalog,inputs=fixture()
        season["simc_generated_builds"]["gem_property"]="12.1.5.70448"
        result=inventory(season,catalog,inputs)
        self.assertIn("SIMC_COMPILED_DBC_BUILD_MISMATCH_REQUIRES_REVIEW",
                      result["source_warnings"])
        self.assertFalse(result["budget_can_be_published"])

    def test_file_reader_rejects_symlinks_and_missing(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            missing=root/"absent.json"
            with self.assertRaisesRegex(p.SeasonEvidenceBlocked,"UNSAFE"):
                p.load(missing)
            original=root/"original.json"
            original.write_text('{"game_build":"new"}',encoding="utf8")
            obj,sha=p.load(original)
            self.assertEqual(obj["game_build"],"new")
            self.assertEqual(sha,p.digest(original.read_bytes()))
            try:
                link=root/"link.json"
                link.symlink_to(original)
            except OSError:
                return
            with self.assertRaisesRegex(p.SeasonEvidenceBlocked,"UNSAFE"):
                p.load(link)


if __name__=="__main__":
    unittest.main()
