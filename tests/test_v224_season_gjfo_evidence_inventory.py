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

    def test_same_client_build_does_not_claim_a_verified_new_season(self):
        season,catalog,inputs=fixture(event="season_change")
        result=inventory(season,catalog,inputs,event="season_change",
                         old="12.1.5.70575")
        self.assertEqual(result["previous_build_record_status"],"RECORDED")
        self.assertTrue(result["previous_build_is_not_season_proof"])
        self.assertEqual(result["request_event"],"season_change")
        self.assertFalse(result["budget_can_be_published"])
        self.assertIsNone(result["G"])

    def test_new_expansion_without_local_previous_build_still_collects_sources(self):
        season,catalog,inputs=fixture(event="expansion_change",
                                     build="13.0.0.99999")
        result=inventory(season,catalog,inputs,event="expansion_change")
        self.assertEqual(result["request_event"],"expansion_change")
        self.assertIsNone(result["previous_game_build"])
        self.assertEqual(result["previous_build_record_status"],"NOT_RECORDED")
        self.assertEqual(result["verified_components"],[])
        self.assertTrue(all(result[x] is None for x in ("G","J","F","O","B","T")))
        preview=p.core_source_preflight(inputs=inputs,event="expansion_change",
                                        target_ilevel=334)
        self.assertEqual(preview["previous_build_record_status"],"NOT_RECORDED")
        self.assertFalse(preview["source_bytes_verified_by_upstream_artifact"])

    def test_bad_previous_build_syntax_rejected_even_as_optional_field(self):
        season,catalog,inputs=fixture(event="season_change")
        with self.assertRaisesRegex(p.SeasonEvidenceBlocked,
                                    "PREVIOUS_BUILD_INVALID"):
            inventory(season,catalog,inputs,event="season_change",old="unknown")

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


    def test_new_season_core_only_runs_before_enchant_catalog_exists(self):
        _,_,originals=fixture(build="12.2.0.99999")
        result=p.core_source_preflight(
            inputs=originals,event="season_change",
            target_ilevel=335,previous_game_build="12.1.5.70575")
        self.assertEqual(result["game_build"],"12.2.0.99999")
        self.assertFalse(result["budget_can_be_published"])
        self.assertTrue(result["requires_v191_source_pinning"])
        self.assertEqual(set(result["component_state"]),set(p.COMPONENTS))
        self.assertIsNone(result["B"])
        self.assertIsNone(result["T"])
        self.assertEqual(result["native_calls"],0)

    def test_core_same_client_build_is_pending_and_mixed_sources_rejected(self):
        _,_,core=fixture()
        source_only=p.core_source_preflight(
            inputs=core,event="season_change",target_ilevel=334,
            previous_game_build="12.1.5.70575")
        self.assertEqual(source_only["previous_build_record_status"],"RECORDED")
        self.assertFalse(source_only["budget_can_be_published"])
        self.assertIsNone(source_only["G"])
        _,_,new=fixture(build="12.2.0.99999")
        changed=dict(new)
        old_budget=core["budget"]
        changed["budget"]=old_budget
        with self.assertRaisesRegex(p.SeasonEvidenceBlocked,
                                    "SAME_BUILD_REPRESENTATIVE"):
            p.core_source_preflight(
                inputs=changed,event="season_change",target_ilevel=335,
                previous_game_build="12.1.5.70575")

    def test_core_only_cli_accepts_future_input_without_v213_or_budget_ready(self):
        _,_,core=fixture(build="12.2.0.99999")
        with tempfile.TemporaryDirectory() as td:
            folder=pathlib.Path(td)
            args=["--core-only","--event","season_change",
                  "--previous-game-build","12.1.5.70575",
                  "--target-ilevel","335"]
            for key in p.SOURCE:
                path=folder/(key+".json")
                path.write_text(p.canonical(core[key][0])+"\n",encoding="utf8")
                args.extend(("--"+key,str(path)))
            target=folder/"core_gjfo_inventory.json"
            args.extend(("--out",str(target)))
            self.assertEqual(p.main(args),0)
            result=json.loads(target.read_text(encoding="utf8"))
            self.assertFalse(result["budget_can_be_published"])
            self.assertFalse(result["user_options_auto_admitted"])
            self.assertEqual(result["native_calls"],0)
            self.assertTrue(result["requires_v213_catalog_join_for_user_options"])

    def test_real_file_cli_compiles_sealed_v191_v213_source_gap_receipt(self):
        season,catalog,inputs=fixture()
        with tempfile.TemporaryDirectory() as td:
            folder=pathlib.Path(td)
            paths={}
            for key in p.SOURCE:
                path=folder/(key+".json")
                path.write_text(p.canonical(inputs[key][0])+"\n",encoding="utf8")
                paths[key]=path
                season["sha256_by_input"][key]=p.digest(path.read_bytes())
            # Pin an actual v191 file SHA in the v213 manifest, not an
            # invented token. Compiler must authenticate the exact file.
            v191=folder/"v191.json"
            v191.write_text(p.canonical(season)+"\n",encoding="utf8")
            actual_v191_sha=p.digest(v191.read_bytes())
            classification=SourceToCatalogTests()
            classification.setUpClass()
            _,class_doc=classification.build_inputs()
            catalog=catalog_bridge.compile_catalog(
                season,actual_v191_sha,class_doc,"b"*64)
            v213=folder/"v213.json"
            v213.write_text(p.canonical(catalog)+"\n",encoding="utf8")
            output=folder/"inventory.json"
            self.assertEqual(p.main([
                "--v191",str(v191),"--v213",str(v213),
                "--gear",str(paths["gear"]),"--tier",str(paths["tier"]),
                "--budget",str(paths["budget"]),
                "--event","mid_patch","--target-ilevel","334",
                "--out",str(output)]),0)
            result=json.loads(output.read_text(encoding="utf8"))
            self.assertEqual(result["v191_source_sha256"],actual_v191_sha)
            self.assertEqual(result["verified_components"],[])
            self.assertIsNone(result["B"])
            self.assertFalse(result["budget_can_be_published"])
            # An actual on-disk byte drift fails without modifying output.
            raw=output.read_bytes()
            paths["budget"].write_bytes(paths["budget"].read_bytes()+b" ")
            with self.assertRaisesRegex(p.SeasonEvidenceBlocked,
                                        "BUDGET_SOURCE_DIGEST_MISMATCH"):
                p.main([
                    "--v191",str(v191),"--v213",str(v213),
                    "--gear",str(paths["gear"]),
                    "--tier",str(paths["tier"]),
                    "--budget",str(paths["budget"]),
                    "--event","mid_patch","--target-ilevel","334",
                    "--out",str(output)])
            self.assertEqual(output.read_bytes(),raw)


if __name__=="__main__":
    unittest.main()
