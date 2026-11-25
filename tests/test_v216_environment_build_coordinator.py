import copy
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




    def test_auto_j_source_candidates_reuse_v221_and_v230_without_native(self):
        """75 same-build raw-unresolved gems yield bounded metadata, not J."""
        build="12.2.0.99999"
        rev="a"*40
        root=self.root/"fresh-j"
        item_folder=root/"source"/"v256_full_pinned_simc"
        items=root/"fresh_source"
        items.mkdir(parents=True)
        item_folder.mkdir(parents=True)
        ids=list(range(300001,300076))  # above former 64 selected-item cap
        rows=[{"item_id":iid,"gem_property_id":iid-200000,
               "enchant_id":iid+1000,"color_mask":2,
               "minimum_ilevel":300,"expansion_id":12,
               "status":"EXACT_DB2_ITEMSPARSE_GEM_PROPERTY_RELATION",
               "ui_selectable":False} for iid in ids]
        v221={
            "schema":v216.gem_item_join.SCHEMA,
            "status":"SOURCE_ITEM_PROPERTY_LINKS_ONLY_NOT_USER_ADMITTED",
            "game_build":build,"simc_revision":rev,
            "simc_generated_gem_source_build":build,
            "exact_link_count":len(rows),"joins":rows}
        source_file=items/"v221_new_season_gem_item_candidates.json"
        source_file.write_text(json.dumps(v221),encoding="utf8")
        receipt={
            "schema":v216.simc_source.SCHEMA,
            "provenance_tree_blob_authenticated":True,
            "item_data_present":True,
            "simc_generated_build":build,"simc_revision":rev,
            "source_files":{"item_data.inc":{"sha256":"c"*64}},
            "receipt_sha256":"b"*64}
        (item_folder/v216.simc_source.RECEIPT).write_text(
            json.dumps(receipt),encoding="utf8")
        def original_metadata(*,directory,item_ids):
            self.assertEqual(pathlib.Path(directory).resolve(),
                             item_folder.resolve())
            self.assertEqual(item_ids,ids)
            return {"schema":v216.simc_item_metadata.SCHEMA,
                    "game_build":build,"simc_revision":rev,
                    "requested_item_count":len(ids),
                    "source_receipt_sha256":"b"*64,
                    "source_sha256":"c"*64,
                    "items":[{"item_id":iid,"quality":4,
                              "name":"Source Gem "+str(iid),
                              "ilevel_unscaled":300,
                              "crafting_quality":2,"class_id":
                                  v216.gem_item_join.GEM_CLASS,
                              "subclass_id":0} for iid in ids]}
        runs=[]
        def stage_once(**kw):
            runs.append(kw["stage_id"])
            kw["execute"]()
            output=root/kw["outputs"]["quality"]
            self.assertTrue(kw["validate"]({"quality":output}))
            return {"receipt_sha256":"d"*64,"status":"EXECUTED_AND_SEALED"}
        compiled={"stage_root":str(root),"simc_revision":rev}
        gem_source={"candidate_path":str(source_file),
                    "source_stage":{"receipt_sha256":"e"*64}}
        collected={"expected_game_build":build,
                   "fresh_lazy_full_pinned_simc_item_source":{
                       "source_dir":str(item_folder)}}
        with mock.patch.object(v216.simc_item_metadata,"from_seed",
                               side_effect=original_metadata), \
             mock.patch.object(v216.stage_engine,"execute_stage",
                               side_effect=stage_once):
            found=v216._fresh_same_build_ordinary_gem_metadata_candidates(
                compiled=compiled,gem_source=gem_source,collected=collected)
        self.assertEqual(len(runs),1)
        self.assertEqual(found["candidate_count"],75)
        self.assertEqual(found["candidates_unadmitted"][0]["item_id"],ids[0])
        self.assertEqual(found["candidates_unadmitted"][-1]["crafting_quality"],2)
        self.assertEqual(found["v221_stage_receipt_sha256"],"e"*64)
        self.assertFalse(found["highest_quality_verified"])
        self.assertFalse(found["numeric_four_stat_rating_measured"])
        self.assertIsNone(found["J"])
        self.assertFalse(found["environment_ready"])
        self.assertEqual((found["native_calls"],found["network_calls"]),(0,0))
        absent=v216._fresh_same_build_ordinary_gem_metadata_candidates(
            compiled=compiled,gem_source=gem_source,
            collected={"expected_game_build":build,
                       "fresh_lazy_full_pinned_simc_item_source":{
                           "source_dir":None}})
        self.assertEqual(absent["status"],
            "SAME_BUILD_ORDINARY_GEM_METADATA_SOURCE_PENDING")
        self.assertIsNone(absent["J"])
        v221["simc_revision"]="f"*40
        source_file.write_text(json.dumps(v221),encoding="utf8")
        with self.assertRaisesRegex(
                v216.EnvironmentBuildBlocked,
                "V216_GEM_SOURCE_METADATA_V221_SAME_BUILD_REQUIRED"):
            v216._fresh_same_build_ordinary_gem_metadata_candidates(
                compiled=compiled,gem_source=gem_source,collected=collected)

    def test_v549_reuse_original_v296_dbc_for_static_four_stat_j(self):
        build="12.2.0.99999"
        rev="a"*40
        props=(32,36,49,40)
        rows=[];cpp=[]
        for i in range(4):
            for rank in (2,3):
                iid=330000+i*10+rank
                eid=8100+i*10+rank
                rows.append({"item_id":iid,"enchant_id":eid,
                   "gem_property_id":eid+100,"color_mask":2,
                   "minimum_ilevel":320,"expansion_id":13,
                   "quality":4,"crafting_quality":rank})
                cpp.append("{ "+str(eid)+", 0, 0, 0, 0, 0, 0, 0, 0, "
                    "{ 5, 5, 0 }, { "+str(12 if rank==2 else 16)+", 7, 0 }, "
                    "{ "+str(props[i])+", "+str(props[(i+1)%4])+", 0 }, "
                    '{ 0, 0, 0 }, 0, "Test" },')
        raw="// spell item enchantments, wow build "+build+"\n"+(
            "\n".join(cpp))+"\n"
        static=v216.oil_raw_source.extract(
            generated_text=raw,game_build=build,simc_revision=rev,
            enchant_ids={x["enchant_id"] for x in rows})
        candidate={"status":"SAME_BUILD_GEM_ITEM_QUALITY_CANDIDATES_UNADMITTED",
          "game_build":build,"simc_revision":rev,
          "v221_stage_receipt_sha256":"1"*64,
          "v230_stage_receipt_sha256":"2"*64,
          "v230_original_item_data_sha256":"3"*64,
          "candidate_count":len(rows),"candidates_unadmitted":rows}
        kwargs=dict(candidates=candidate,stage_root=self.root,
          simc_revision=rev,collected={"expected_game_build":build,
           "fresh_pinned_v211_source":{
              "status":"PINNED_V211_AND_GENERATED_SOURCES_SEALED"}})
        with mock.patch.object(v216.oil_raw_source,"from_v275",
                               return_value=static) as fetch:
            found=v216._fresh_pinned_dbc_ordinary_gem_j_source(**kwargs)
        self.assertEqual(fetch.call_count,1)
        self.assertEqual(found["J_candidate_unadmitted"],92)
        self.assertEqual(len(found["rating_by_id"]),4)
        self.assertEqual(found["native_calls"],0)
        self.assertFalse(found["highest_quality_verified"])
        self.assertFalse(found["environment_ready"])
        mismatch={**candidate,"game_build":"12.1.5.70783"}
        with self.assertRaisesRegex(v216.EnvironmentBuildBlocked,
                    "V216_GEM_DBC_ORIGINAL_BUILD_AND_SHA_REQUIRED"):
            v216._fresh_pinned_dbc_ordinary_gem_j_source(
                **{**kwargs,"candidates":mismatch})
        # Another partner stat for the same leading stat changes the effect.
        # Approved selection: same C-leading quality, higher J wins even
        # if its partner is M instead of H.
        other={**rows[0],"item_id":349991,"enchant_id":8991,
               "crafting_quality":3}
        alternate=v216.oil_raw_source.extract(
            generated_text=raw+'{ 8991, 0, 0, 0, 0, 0, 0, 0, 0, '
                '{ 5, 5, 0 }, { 17, 7, 0 }, { 32, 49, 0 }, '
                '{ 0, 0, 0 }, 0, "Other" },\n',
            game_build=build,simc_revision=rev,
            enchant_ids={x["enchant_id"] for x in rows}|{8991})
        with mock.patch.object(v216.oil_raw_source,"from_v275",
                               return_value=alternate):
            chosen=v216._fresh_pinned_dbc_ordinary_gem_j_source(
                **{**kwargs,"candidates":{**candidate,
                   "candidate_count":len(rows)+1,
                   "candidates_unadmitted":rows+[other]}})
        self.assertEqual(chosen["J_candidate_unadmitted"],93)
        self.assertEqual(chosen["by_stat"]["crit_rating"]["item_id"],349991)
        self.assertEqual(chosen["native_calls"],0)
        self.assertFalse(chosen["environment_ready"])
        # A lower craft rank can provide greater nominal J. This is not
        # a UI quality equivalence decision.
        lower_rank={**other,"crafting_quality":1}
        with mock.patch.object(v216.oil_raw_source,"from_v275",
                               return_value=alternate):
            lower=v216._fresh_pinned_dbc_ordinary_gem_j_source(
                **{**kwargs,"candidates":{**candidate,
                   "candidate_count":len(rows)+1,
                   "candidates_unadmitted":rows+[lower_rank]}})
        self.assertEqual(lower["J_candidate_unadmitted"],93)
        self.assertEqual(lower["by_stat"]["crit_rating"]["item_id"],349991)
        self.assertFalse(lower["highest_quality_verified"])
        self.assertEqual(lower["native_calls"],0)
        # Same quality and same J: smallest physical ID wins.
        tied=v216.oil_raw_source.extract(
            generated_text=raw+'{ 8991, 0, 0, 0, 0, 0, 0, 0, 0, '
                '{ 5, 5, 0 }, { 16, 7, 0 }, { 32, 49, 0 }, '
                '{ 0, 0, 0 }, 0, "Other" },\n',
            game_build=build,simc_revision=rev,
            enchant_ids={x["enchant_id"] for x in rows}|{8991})
        with mock.patch.object(v216.oil_raw_source,"from_v275",
                               return_value=tied):
            same=v216._fresh_pinned_dbc_ordinary_gem_j_source(
                **{**kwargs,"candidates":{**candidate,
                   "candidate_count":len(rows)+1,
                   "candidates_unadmitted":rows+[other]}})
        self.assertEqual(same["by_stat"]["crit_rating"]["item_id"],330003)
        self.assertEqual(same["J_candidate_unadmitted"],92)
        # Scaling stays unobserved instead of treating base DBC points as J.
        scaled=raw.replace("{ 8102, 0, 0, 0, 0, 0, 0, 0, 0, ",
                           "{ 8102, 0, -7, 0, 80, 120, 0, 0, 0, ")
        unscaled=v216.oil_raw_source.extract(
            generated_text=scaled,game_build=build,simc_revision=rev,
            enchant_ids={x["enchant_id"] for x in rows})
        with mock.patch.object(v216.oil_raw_source,"from_v275",
                               return_value=unscaled):
            pending=v216._fresh_pinned_dbc_ordinary_gem_j_source(**kwargs)
        self.assertEqual(pending["J_candidate_unadmitted"],92)
        self.assertGreater(pending["unresolved_item_count"],0)
        self.assertFalse(pending["highest_quality_verified"])
        self.assertFalse(pending["environment_ready"])

    def test_v551_static_j_original_owner_repeats_and_rejects_drift(self):
        """Existing v271 repeated J is preserved without quality admission."""
        build="12.2.0.99999"
        rev="a"*40
        stats=list(v216.physical_gems.ORDINARY_FOUR_STATS)
        ids=[330003,330013,330023,330033]
        four={str(i):23 for i in ids}
        preview={"status":"PINNED_SIMC_DBC_FOUR_STAT_J_STATIC_UNADMITTED",
                 "game_build":build,"simc_revision":rev,
                 "source_sha256":"d"*64,
                 "by_stat":{s:{"item_id":i,"raw_nominal_points":23}
                            for s,i in zip(stats,ids)},
                 "rating_by_id":four,"J_candidate_unadmitted":92}
        ordinary=ids+ids[:2]
        layout={"ordinary_gem_ids":ordinary,
                "socket_total":6,"special_gem_id":None}
        link={"same_build_gem_item_join_only":True,
              "special_gem_item_id":None,
              "v221_stage_receipt_sha256":"1"*64,
              "selected_item_ids":sorted(ids)}
        self.assertEqual(v216._fresh_match_pinned_dbc_ordinary_j(
            preview=preview,layout=layout,ratings=four,link=link,
            game_build=build,simc_revision=rev),ordinary)
        j={"status":"PHYSICAL_GEM_J_ARITHMETIC_UNADMITTED",
           "rating_origin":"PINNED_SIMC_DBC_STATIC_TWO_SECONDARY",
           "physical_gem_item_ids":ordinary,
           "J_candidate_unadmitted":138,
           "J_accounting_policy":"SUM_SELECTED_ORDINARY_GEM_RATINGS",
           "special_gem_count_in_J":0,
           "source_v221_stage_receipt_sha256":"1"*64,
           "source_v275_enchant_sha256":"d"*64}
        preflight={"schema":v216.FRESH_SOURCE_PREFLIGHT_SCHEMA,
                   "environment_ready":False,
                   "game_build":build,"simc_revision":rev,
                   "source_catalog_manifest_sha256":"4"*64,
                   "physical_gem_J_arithmetic_unadmitted":j,
                   "physical_gem_layout_unadmitted":layout,
                   "selected_v221_gem_item_relation_unadmitted":link}
        candidate={"status":"SAME_BUILD_GEM_ITEM_QUALITY_CANDIDATES_UNADMITTED",
                   "game_build":build,"simc_revision":rev,
                   "v221_stage_receipt_sha256":"1"*64,
                   "v230_stage_receipt_sha256":"2"*64,
                   "v230_original_item_data_sha256":"3"*64}
        compilation={"status":"FRESH_V191_V211_V213_COMPILED_UNADMITTED",
                     "simc_revision":rev,
                     "four_stat_pinned_dbc_j_source_unadmitted":preview,
                     "ordinary_gem_v221_v230_source_candidates_unadmitted":
                         candidate}
        numeric=v216._fresh_source_owner_selected_J_F_numeric(
            preflight=preflight,compilation=compilation,
            selected_physical_items=None)
        self.assertEqual(numeric["J"]["rating"],138)
        self.assertEqual(numeric["J"]["ordinary_gem_item_ids"],ordinary)
        self.assertEqual(numeric["J"]["per_item_nominal_rating"],four)
        self.assertEqual(numeric["J"]["numeric_source_owner"],
                         "PINNED_SIMC_DBC_STATIC_TWO_SECONDARY")
        self.assertFalse(numeric["J"]["highest_available_quality_verified"])
        self.assertFalse(numeric["environment_ready"])
        self.assertIsNone(numeric["F"])
        self.assertEqual(numeric["new_native_calls"],0)
        with self.assertRaisesRegex(v216.EnvironmentBuildBlocked,
                                    "V216_PINNED_DBC_J_SELECTED_IDS_OR_RATINGS_DRIFT"):
            v216._fresh_match_pinned_dbc_ordinary_j(
                preview=preview,
                layout={**layout,"ordinary_gem_ids":ordinary[::-1]},
                ratings=four,link=link,
                game_build=build,simc_revision=rev)
        with self.assertRaisesRegex(v216.EnvironmentBuildBlocked,
                                    "V216_JF_OWNER_PINNED_DBC_SAME_BUILD_J_DRIFT"):
            v216._fresh_source_owner_selected_J_F_numeric(
                preflight={**preflight,
                           "physical_gem_J_arithmetic_unadmitted":
                               {**j,"J_candidate_unadmitted":137}},
                compilation=compilation,selected_physical_items=None)

    def test_v559_original_simc_gear_j_owner_source_and_quality_bridge(self):
        """Use four real-format sealed Native receipts, not buffed or packaged J."""
        build="12.2.0.99999"
        rev="a"*40
        stats=list(v216.physical_gems.ORDINARY_FOUR_STATS)
        ids=[330011,330021,330031,330041]
        root=self.root/"native-j-sealed"
        source=root/"source"
        source.mkdir(parents=True)
        observations=[]
        case_map={}
        for item in ids:
            receipts=[]
            for variant in ("baseline","active"):
                case=source/("v278_"+variant+"_"+str(item))
                case.mkdir()
                native=case/"native.json"
                native.write_bytes(("{\"gem_id\":"+str(item)+"}").encode())
                native_sha=v216.native_effect_pair.file_sha(native)
                original={"status":"NATIVE_JSON2_CAPTURED",
                          "identity":{"variant":variant,
                                      "simc_revision":rev,
                                      "binary_sha256":"b"*64,
                                      "source_profile_sha256":"c"*64},
                          "native_json2_sha256":native_sha}
                receipt=case/"receipt.json"
                receipt.write_text(json.dumps(original),encoding="utf8")
                receipts.append({
                    "variant":variant,"receipt_path":str(receipt),
                    "receipt_sha256":v216.native_effect_pair.file_sha(receipt),
                    "cache_reused":variant=="baseline"})
            case_map[str(item)]=receipts
            index=ids.index(item)
            vector={key:0 for key in stats}
            vector[stats[index]]=16
            vector[stats[(index+1)%4]]=7
            observations.append({
                "ordinary_gem_id":item,
                "status":"SIMC_ORDINARY_GEM_TWO_STAT_OBSERVED_UNADMITTED",
                "binary_sha256":"b"*64,
                "source_profile_sha256":"c"*64,
                "simc_effective_two_stat_rating_unadmitted":23,
                "simc_effective_two_stat_vector_unadmitted":vector,
                "observed":{"source":
                    "SIMC_JSON2_ACTUAL_GEM_ID_AND_BUFFED_STATS"},
                "native_case_receipts":receipts})
        ratings={str(item):23 for item in ids}
        preview={
            "status":"FOUR_STAT_SIMC_NATIVE_RATINGS_OBSERVED_UNADMITTED",
            "game_build":build,"simc_revision":rev,
            "source_sha256":"d"*64,
            "v221_stage_receipt_sha256":"1"*64,
            "v230_stage_receipt_sha256":"2"*64,
            "v230_original_item_data_sha256":"3"*64,
            "by_stat":{
                stat:{"item_id":item,"raw_nominal_points":23}
                for stat,item in zip(stats,ids)},
            "rating_by_id":ratings,"J_candidate_unadmitted":92,
            "highest_quality_candidate_count":4,
            "measured_candidate_ids":ids,
            "native_observations_unadmitted":observations,
            "native_case_receipts_by_id":case_map,
            "source_selected_tier_candidate_ids":ids,
            "sample_numeric_signatures_by_item_id":{
                str(item):["SIMC_SCALED",-7,.15+index,.35+index]
                for index,item in enumerate(ids)},
            "selected_numeric_source_proofs_by_item_id":{
                str(item):{
                    "item_id":item,
                    "representative_item_id":item,
                    "numeric_source":"EXACT_CONTROLLED_SIMC_NATIVE_DELTA",
                    "source_coefficient_signature":[
                        "SIMC_SCALED",-7,.15+index,.35+index],
                    "resolved_two_secondary_vector":{
                        stat:(16 if stat==stats[index]
                              else 7 if stat==stats[(index+1)%4] else 0)
                        for stat in stats}}
                for index,item in enumerate(ids)}}
        layout={"ordinary_gem_ids":ids,
                "socket_total":4,"special_gem_id":None}
        link={"same_build_gem_item_join_only":True,
              "special_gem_item_id":None,
              "v221_stage_receipt_sha256":"1"*64,
              "selected_item_ids":ids}
        chosen=v216._fresh_match_simc_native_ordinary_j(
            preview=preview,layout=layout,ratings=ratings,
            link=link,game_build=build,simc_revision=rev)
        self.assertEqual(chosen,ids)
        candidate={"status":"SAME_BUILD_GEM_ITEM_QUALITY_CANDIDATES_UNADMITTED",
                   "game_build":build,"simc_revision":rev,
                   "v221_stage_receipt_sha256":"1"*64,
                   "v230_stage_receipt_sha256":"2"*64,
                   "v230_original_item_data_sha256":"3"*64,
                   "candidates_unadmitted":[{
                       "item_id":item,"crafting_quality":2}
                       for item in ids]}
        j={"status":"PHYSICAL_GEM_J_ARITHMETIC_UNADMITTED",
           "rating_origin":"SIMC_NATIVE_CONTROLLED_TWO_SECONDARY",
           "physical_gem_item_ids":ids,
           "J_candidate_unadmitted":92,
           "J_accounting_policy":"SUM_SELECTED_ORDINARY_GEM_RATINGS",
           "special_gem_count_in_J":0,
           "source_v221_stage_receipt_sha256":"1"*64,
           "source_v296_static_source_sha256":"d"*64}
        preflight={"schema":v216.FRESH_SOURCE_PREFLIGHT_SCHEMA,
                   "environment_ready":False,
                   "game_build":build,"simc_revision":rev,
                   "source_catalog_manifest_sha256":"4"*64,
                   "physical_gem_J_arithmetic_unadmitted":j,
                   "physical_gem_layout_unadmitted":layout,
                   "selected_v221_gem_item_relation_unadmitted":link}
        compilation={"status":"FRESH_V191_V211_V213_COMPILED_UNADMITTED",
                     "simc_revision":rev,
                     "four_stat_simc_native_j_source_unadmitted":preview,
                     "ordinary_gem_v221_v230_source_candidates_unadmitted":
                         candidate}
        result=v216._fresh_source_owner_selected_J_F_numeric(
            preflight=preflight,compilation=compilation,
            selected_physical_items=None)
        self.assertEqual(result["J"]["rating"],92)
        self.assertEqual(result["J"]["numeric_source_owner"],
                         "SIMC_NATIVE_CONTROLLED_GEM_DELTA")
        self.assertEqual(result["J"]["per_item_nominal_rating"],ratings)
        self.assertEqual(result["J"]["observed_quality_rank_by_id"],
                         {str(i):2 for i in ids})
        self.assertFalse(result["environment_ready"])
        # Full 75-source and selected-4 v230 receipts have DIFFERENT SHAs:
        # both are sealed for their own IDs, never incorrectly equate them.
        selected_original={
            "quality_source_authenticated":True,
            "v230_stage_receipt_sha256":"9"*64,
            "game_build":build,"simc_revision":rev,
            "selected_item_ids":ids,
            "selected_item_quality_unadmitted":[
                {"item_id":item,"crafting_quality":2}
                for item in ids]}
        selected_comparison={
            "schema":"v216_selected_gem_quality_policy_A_preview_v1",
            "game_build":build,"simc_revision":rev,
            "quality_source_groups_unadmitted":[]}
        source_preflight={**preflight,
            "selected_v221_gem_item_relation_unadmitted":{
                **link,
                "selected_simc_gem_quality_source_unadmitted":
                    selected_original,
                "gem_policy_A_source_and_quality_unadmitted":
                    selected_comparison}}
        quality=v216._fresh_source_owner_observed_J_F_quality(
            preflight=source_preflight,compilation=compilation,
            owner_numeric=result)
        self.assertIsNotNone(quality["J"])
        self.assertEqual(len(quality["J"][
            "same_enchant_quality_groups_source_only"]),4)
        self.assertFalse(quality["environment_ready"])
        socket={
            "status":"J_INTRINSIC_COUNTS_BOUND_SOURCE_ONLY",
            "additional_socket_proof_required_by_slot":{},
            "observed_J_unadmitted":92,
            "v232_stage_receipt_sha256":"5"*64,
            "selected_socket_counts":{"neck":3,"finger1":1}}
        components=v216._fresh_source_owner_original_J_F_components(
            preflight=source_preflight,
            compilation={**compilation,
                "selected_J_intrinsic_socket_origin_unadmitted":socket,
                "physical_gem_layout_unadmitted":layout},
            staged={"status":"FRESH_SEASON_ENVIRONMENT_STAGED_NOT_INSTALLED",
                    "stage_status":"EXECUTED_AND_SEALED",
                    "stage_receipt_sha256":"7"*64},
            owner_numeric=result,quality_scope=quality,
            effect_observations=[])
        self.assertEqual(components["J"]["rating"],92)
        self.assertEqual(components["J"]["effect_quality_policy"],
                         "BEST_DISCOVERED_COMPARABLE")
        with self.assertRaisesRegex(v216.EnvironmentBuildBlocked,
                                    "V216_NATIVE_J_IDS_RATING_VECTOR_DRIFT"):
            v216._fresh_match_simc_native_ordinary_j(
                preview=preview,
                layout={**layout,"ordinary_gem_ids":list(reversed(ids))},
                ratings=ratings,link=link,
                game_build=build,simc_revision=rev)
        altered={**preview,"native_case_receipts_by_id":{
            **case_map,str(ids[0]):[
                {**case_map[str(ids[0])][0],"receipt_sha256":"f"*64},
                case_map[str(ids[0])][1]]}}
        with self.assertRaisesRegex(v216.EnvironmentBuildBlocked,
                                    "V216_NATIVE_J_SOURCE_REPRESENTATIVE_RATING_OR_ID_DRIFT"):
            v216._fresh_match_simc_native_ordinary_j(
                preview=altered,layout=layout,ratings=ratings,
                link=link,game_build=build,simc_revision=rev)

    def test_v753_named_tiers_keep_incomparable_source_conditions(self):
        def row(i,name,level,minimum=310):
            return {"item_id":i,"enchant_id":i,"gem_property_id":i,
                    "color_mask":2,"minimum_ilevel":minimum,
                    "expansion_id":13,"quality":4,"crafting_quality":3,
                    "item_name":name,"item_ilevel_unscaled":level}
        def source(major,minor,scale=-7,base=0):
            return {"source_reason_codes":["SIMC_ITEM_ENCHANT_SCALING_REQUIRED"],
                    "unresolved_simc_scaled_static_stats":{
                        "crit_rating":{"simc_scaling_id":scale,
                                       "dbc_base_amount":base,
                                       "simc_coefficient":major},
                        "haste_rating":{"simc_scaling_id":scale,
                                        "dbc_base_amount":base,
                                        "simc_coefficient":minor}},
                    "static_CHMV_vector":None,
                    "source_min_ilevel":0,"source_max_ilevel":0}
        rows=[row(1,"High ilvl",350),row(2,"Tradeoff",330),
              row(3,"Other restriction",330,300),
              row(4,"Other scale",330),row(5,"Dominated",330),
              row(6,"Same numeric",320),row(7,"Other base",330)]
        sources={1:source(.6,.2),2:source(.5,.3),3:source(.4,.1),
                 4:source(.4,.1,-8),5:source(.4,.1),
                 6:source(.6,.2),7:source(.4,.1,base=1)}
        plan=v216._fresh_two_stat_gem_named_tier_measurement_plan(
            rows=rows,by_enchant=sources)
        self.assertEqual(plan["status"],
                         "NAMED_TIER_AND_INNER_QUALITY_PLAN_UNADMITTED")
        self.assertEqual([x["item_id"] for x in plan["selected_tier_candidates"]],
                         [1,2,3,4,6,7])
        # Existing signature reuse is preserved (same numeric signature
        # can represent more than one candidate); no Native here.
        self.assertEqual(plan["sample_count"],5)
        by_id={x["item_id"]:x["signature"]
               for x in plan["selected_tier_candidates"]}
        self.assertEqual(by_id[1],by_id[6])
        self.assertNotEqual(by_id[3],by_id[7])

    def test_v560_dynamic_12_gem_directions_and_named_tier_rank_steps(self):
        """48/72 source items -> 24/36 higher-name-tier rows -> 2/3 samples."""
        stats=list(v216.physical_gems.ORDINARY_FOUR_STATS)
        for inner_rank_count in (2,3):
            rows=[];source={};ident=600000
            for lead in stats:
                for partner in stats:
                    if lead==partner:continue
                    for named_tier in (1,2):
                        for rank in range(1,inner_rank_count+1):
                            ident+=1
                            major=(.20 if named_tier==1 else .40)+rank*.01
                            minor=(.06 if named_tier==1 else .12)+rank*.01
                            rows.append({
                                "item_id":ident,"enchant_id":ident+1000,
                                "gem_property_id":ident+2000,"color_mask":2,
                                "minimum_ilevel":310,"expansion_id":13,
                                "quality":4,"crafting_quality":rank,
                                "item_name":f"Gem tier {named_tier} {lead} {partner}",
                                # Inner crafting ranks change item level;
                                # the named-tier ordering still uses the
                                # original exact scaling-strength comparison.
                                "item_ilevel_unscaled":333+rank})
                            source[ident+1000]={
                                "enchant_id":ident+1000,
                                "source_reason_codes":[
                                    "SIMC_ITEM_ENCHANT_SCALING_REQUIRED"],
                                "unresolved_simc_scaled_static_stats":{
                                    lead:{"simc_scaling_id":-7,
                                          "dbc_base_amount":0,
                                          "simc_coefficient":major},
                                    partner:{"simc_scaling_id":-7,
                                             "dbc_base_amount":0,
                                             "simc_coefficient":minor}},
                                "static_CHMV_vector":None,
                                "source_min_ilevel":0,"source_max_ilevel":0}
            plan=v216._fresh_two_stat_gem_named_tier_measurement_plan(
                rows=rows,by_enchant=source)
            self.assertEqual(
                plan["status"],"NAMED_TIER_AND_INNER_QUALITY_PLAN_UNADMITTED")
            self.assertEqual(len(rows),12*2*inner_rank_count)
            self.assertEqual(plan["observed_direction_count"],12)
            self.assertEqual(
                plan["selected_tier_candidate_count"],12*inner_rank_count)
            self.assertEqual(plan["sample_count"],inner_rank_count)
            self.assertTrue(all(
                "Gem tier 2 " in row["item_name"]
                for row in plan["selected_tier_candidates"]))
            self.assertTrue(all(
                len(row["internal_crafting_qualities"])==inner_rank_count
                for row in plan["observed_tier_structure"]))

    def test_v558_native_rating_uses_source_signatures_not_four_effects(self):
        """8 physical item effects, 2 rank signatures -> only 2 Native pairs."""
        build="12.2.0.99999";rev="a"*40
        root=self.root/"new-season-j";root.mkdir()
        profile=root/"source_only_G.simc"
        profile.write_text("paladin=test\nhead=source,id=33221\n",
                           encoding="utf8")
        binary=root/"simc_fake";binary.write_bytes(b"fake-binary")
        stats=list(v216.physical_gems.ORDINARY_FOUR_STATS)
        items=[{"item_id":330001+i,"enchant_id":7001+i,
                "gem_property_id":9001+i,"color_mask":2,
                "minimum_ilevel":320,"expansion_id":13,
                "quality":4,"crafting_quality":(i%2)+1,
                "item_name":"Gem "+str(i//2),
                "item_ilevel_unscaled":333}
               for i in range(8)]
        candidate={"status":"SAME_BUILD_GEM_ITEM_QUALITY_CANDIDATES_UNADMITTED",
            "candidate_count":len(items),"candidates_unadmitted":items,
            "game_build":build,"simc_revision":rev,
            "v221_stage_receipt_sha256":"1"*64,
            "v230_stage_receipt_sha256":"2"*64,
            "v230_original_item_data_sha256":"3"*64}
        collected={"expected_game_build":build,
                   "fresh_pinned_v211_source":{
                       "status":"PINNED_V211_AND_GENERATED_SOURCES_SEALED"},
                   "fresh_one_spec_physical_G_probe":{
                       "profile_path":str(profile)}}
        def original_source(**kwargs):
            result=[]
            for i in kwargs["enchant_ids"]:
                k=(i-7001)//2
                higher=i%2==0
                result.append({
                    "enchant_id":i,
                    "source_reason_codes":[
                        "SIMC_ITEM_ENCHANT_SCALING_REQUIRED"],
                    "unresolved_simc_scaled_static_stats":{
                        stats[k]:{"simc_scaling_id":-7,"dbc_base_amount":0,
                                  "simc_coefficient":.35 if not higher else .25},
                        stats[(k+1)%4]:{"simc_scaling_id":-7,"dbc_base_amount":0,
                                        "simc_coefficient":.15 if not higher else .10}},
                    "static_CHMV_vector":None,
                    "source_min_ilevel":0,"source_max_ilevel":0})
            return {"items":result,"source_sha256":"4"*64,
                    "game_build":build,"simc_revision":rev}
        called=[]
        def one_gem(**kwargs):
            idx=kwargs["ordinary_gem_id"]-330001
            called.append(idx)
            lead=stats[idx//2]
            partner=stats[(idx//2+1)%4]
            vector={s:0 for s in stats}
            vector[lead]=16 if idx%2 else 12
            vector[partner]=7 if idx%2 else 5
            return {
               "status":"SIMC_ORDINARY_GEM_TWO_STAT_OBSERVED_UNADMITTED",
               "simc_effective_two_stat_vector_unadmitted":vector,
               "simc_effective_two_stat_rating_unadmitted":sum(vector.values()),
               "observed":{"source":
                   "SIMC_JSON2_ACTUAL_GEM_ID_AND_BUFFED_STATS"},
               "ordinary_gem_id":kwargs["ordinary_gem_id"],
               "native_case_receipts":[],
               "new_native_calls":2 if idx==0 else 1}
        args=dict(candidates=candidate,collected=collected,
                  stage_root=root,binary=binary,simc_revision=rev,
                  native_G_status="G_NATIVE_NUMERIC_REFERENCE_OBSERVED_JFO_PENDING")
        with mock.patch.object(v216.oil_raw_source,"from_v275",
                               side_effect=original_source), \
             mock.patch.object(v216.native_effect_pair,
                               "measure_ordinary_gem",
                               side_effect=one_gem) as execution:
            actual=v216._fresh_four_stat_simc_observed_j_preview(**args)
            self.assertEqual(execution.call_count,2)
        self.assertEqual(called,[0,1])
        self.assertEqual(actual["status"],
                         "FOUR_STAT_SIMC_NATIVE_RATINGS_OBSERVED_UNADMITTED")
        self.assertEqual(actual["J_candidate_unadmitted"],92)
        self.assertEqual(actual["new_native_calls"],3)
        self.assertEqual(actual["numeric_signature_count"],2)
        self.assertEqual(actual["source_effect_family_count"],4)
        self.assertEqual(set(actual["by_stat"]),set(stats))
        self.assertEqual(
            len(actual["selected_numeric_source_proofs_by_item_id"]),4)
        self.assertTrue(any(
            proof["same_signature_not_independently_native_measured"]
            for proof in actual[
                "selected_numeric_source_proofs_by_item_id"].values()))
        self.assertIsNone(actual.get("J"))
        self.assertFalse(actual["environment_ready"])
        with self.assertRaisesRegex(v216.EnvironmentBuildBlocked,
                "V216_GEM_FOUR_FAMILY_SOURCE_IDENTITY_DRIFT"):
            v216._fresh_four_stat_simc_observed_j_preview(
                **{**args,"candidates":{
                    **candidate,"game_build":"12.1.5.70783"}})
        with mock.patch.object(v216.oil_raw_source,"from_v275",
                               side_effect=original_source), \
             self.assertRaisesRegex(v216.EnvironmentBuildBlocked,
                "V216_GEM_FOUR_FAMILY_NATIVE_PROFILE_STAGE_DRIFT"):
            v216._fresh_four_stat_simc_observed_j_preview(
                **{**args,"collected":{
                    **collected,
                    "fresh_one_spec_physical_G_probe":{
                        "profile_path":str(self.root/"outside.simc")}}})

    def test_p3_hl_reuse_requires_exact_game_build_even_with_verified_manifest(self):
        """Exact build selection is structural, not extra SimC validation."""
        stage_root=self.root/"season-cache"
        base=stage_root/"_fresh_season_sources"
        for build,mtime,revision in (
                ("12.1.5.70575",40,"a"*40),
                ("12.1.5.70783",30,"b"*40)):
            root=base/("wago_"+build)
            docs=root/"fresh_source"
            docs.mkdir(parents=True)
            key=("1"*64 if build.endswith("70575") else "2"*64)
            stage_sha="3"*64
            installed={
                "manifest_sha256":key,"game_build":build,
                "target_ilevel":334,"simc_revision":revision,
                "source_catalog_artifact_sha256":"4"*64,
                "source_catalog_manifest_sha256":"5"*64,
                "staged_source_environment_sha256":stage_sha,
                "trusted_budget_evidence_sha256":"6"*64,
                "original_v196_prepared_options_sha256":"7"*64,
                "official_G":2800,"official_J":92,"official_F":165,
                "official_O":{},"official_B":3057,"official_T":3057,
                "published_verified_options":[],
                "published_verified_option_count":0}
            file=docs/("v212_installed_"+key[:20]+".json")
            file.write_text(json.dumps(installed),encoding="utf8")
            (docs/"v213_candidate_catalog.json").write_text(
                json.dumps({"game_build":build,"simc_revision":revision,
                  "manifest_sha256":"5"*64}),encoding="utf8")
            (docs/("v212_environment_"+stage_sha[:20]+".json")).write_text(
                json.dumps({"manifest_sha256":stage_sha,
                    "source_catalog_artifact_sha256":"4"*64,
                    "target_ilevel":334,
                    "original_v216_preflight_sha256":"8"*64}),
                encoding="utf8")
            import os
            os.utime(file,(mtime,mtime))
        def source_json(p,max_bytes=25000000):
            val=json.loads(pathlib.Path(p).read_text(encoding="utf8"))
            # Source catalog SHA comes from sealed artifact bytes in the
            # real environment; this fixture records identity without
            # recreating an unrelated v217 stage engine.
            return val,("4"*64 if p.name=="v213_candidate_catalog.json"
                        else "0"*64)
        with mock.patch.object(v216.environment_manifest,"read_json",
                side_effect=source_json), \
             mock.patch.object(
                v216.environment_manifest,"verify_fresh_installed_environment"), \
             mock.patch.object(
                v216.environment_manifest,"verify_fresh_source_environment"), \
             mock.patch.object(v216.source_to_catalog,"verify_catalog"), \
             mock.patch.object(v216.stage_engine,"verify_stage",
                return_value={"receipt_sha256":"9"*64}):
            get=lambda b:v216.find_verified_installed_season_environment(
                stage_root,334,expected_game_build=b)
            latest=get("12.1.5.70783")
            self.assertEqual(latest["installed_source_game_build"],
                             "12.1.5.70783")
            self.assertEqual(latest["installed_source_simc_revision"],"b"*40)
            self.assertEqual(get("12.1.5.70575")[
                "installed_source_game_build"],"12.1.5.70575")
            self.assertIsNone(get("12.2.0.99999"))
            self.assertEqual(
                v216.find_verified_installed_season_environment(
                    stage_root,334,expected_game_build="12.1.5.70783",
                    expected_installed_manifest_sha256="2"*64)[
                        "installed_manifest_sha256"],"2"*64)
            self.assertIsNone(
                v216.find_verified_installed_season_environment(
                    stage_root,334,expected_game_build="12.1.5.70783",
                    expected_installed_manifest_sha256="1"*64))
            self.assertIsNone(v216.find_verified_installed_season_environment(
                stage_root,335,expected_game_build="12.1.5.70783"))
        for b in (None,"../70575","12.1.5.70783/..","broken"):
            with self.subTest(b=b),self.assertRaisesRegex(
                    v216.EnvironmentBuildBlocked,
                    "V216_REUSE_EXACT_GAME_BUILD_REQUIRED"):
                v216.find_verified_installed_season_environment(
                    stage_root,334,expected_game_build=b)

    def test_v488_unqualified_base_multiple_verified_FJ_never_select_newest(self):
        """Same season/ilevel/O=0 still needs a unique F/J install owner.

        Verify source catalog, staged environment, and original stage
        receipt through existing contract entry points (mocked receipt
        cryptography only). This check does not create source/Native.
        """
        build="12.2.0.99999"
        root=self.root/"two-fj-variants"
        docs=root/"_fresh_season_sources"/("wago_"+build)/"fresh_source"
        docs.mkdir(parents=True)
        stage_sha="3"*64
        (docs/"v213_candidate_catalog.json").write_text(json.dumps({
            "game_build":build,"simc_revision":"b"*40,
            "manifest_sha256":"5"*64}),encoding="utf8")
        (docs/("v212_environment_"+stage_sha[:20]+".json")).write_text(
            json.dumps({"manifest_sha256":stage_sha,
                "source_catalog_artifact_sha256":"4"*64,
                "target_ilevel":334,
                "original_v216_preflight_sha256":"8"*64}),encoding="utf8")
        keys=["a"*64,"b"*64]
        for key,flask,gem in zip(keys,[241326,241327],[92,120]):
            (docs/("v212_installed_"+key[:20]+".json")).write_text(
                json.dumps({
                    "manifest_sha256":key,"game_build":build,
                    "target_ilevel":334,"simc_revision":"b"*40,
                    "source_catalog_artifact_sha256":"4"*64,
                    "source_catalog_manifest_sha256":"5"*64,
                    "staged_source_environment_sha256":stage_sha,
                    "trusted_budget_evidence_sha256":"6"*64,
                    "original_v196_prepared_options_sha256":"7"*64,
                    "official_G":2850,"official_J":gem,"official_F":165,
                    "official_O":{},"official_B":2850+gem+165,
                    "official_T":2850+gem+165,
                    "official_F_physical_source":{"physical_item_id":flask},
                    "published_verified_options":[],
                    "published_verified_option_count":0}),encoding="utf8")
        def read_json(path,max_bytes=25000000):
            path=pathlib.Path(path)
            return json.loads(path.read_text("utf8")),(
                "4"*64 if path.name=="v213_candidate_catalog.json"
                else "0"*64)
        with (mock.patch.object(v216.environment_manifest,"read_json",
                    side_effect=read_json),
              mock.patch.object(v216.environment_manifest,
                    "verify_fresh_installed_environment"),
              mock.patch.object(v216.environment_manifest,
                    "verify_fresh_source_environment"),
              mock.patch.object(v216.source_to_catalog,"verify_catalog"),
              mock.patch.object(v216.stage_engine,"verify_stage",
                    return_value={"receipt_sha256":"9"*64})):
            # Existing explicit-identity/legacy lookups are unchanged.
            legacy=v216.find_verified_installed_season_environment(
                root,334,expected_game_build=build)
            self.assertIn(legacy["installed_manifest_sha256"],keys)
            with self.assertRaisesRegex(v216.EnvironmentBuildBlocked,
                    "V216_UNQUALIFIED_MULTIPLE_INSTALLED_FJ_VARIANTS_SELECT_EXACT_SHA"):
                v216.find_verified_installed_season_environment(
                    root,334,expected_game_build=build,
                    require_unique_unqualified=True)
            selected=v216.find_verified_installed_season_environment(
                root,334,expected_game_build=build,
                expected_installed_manifest_sha256=keys[1])
            self.assertEqual(selected["installed_manifest_sha256"],keys[1])
            (docs/("v212_installed_"+keys[0][:20]+".json")).unlink()
            unique=v216.find_verified_installed_season_environment(
                root,334,expected_game_build=build,
                require_unique_unqualified=True)
            self.assertEqual(unique["installed_manifest_sha256"],keys[1])

    def test_v413_oil_variant_after_64_is_reused_by_source_and_exact_sha(self):
        build="12.2.0.99999"
        root=self.root/"many-variants"
        docs=root/"_fresh_season_sources"/("wago_"+build)/"fresh_source"
        docs.mkdir(parents=True)
        key="f"*64
        stage_sha="3"*64
        (docs/"v213_candidate_catalog.json").write_text(
            json.dumps({"game_build":build,"simc_revision":"b"*40,
                        "manifest_sha256":"5"*64}),encoding="utf8")
        (docs/("v212_environment_"+stage_sha[:20]+".json")).write_text(
            json.dumps({"manifest_sha256":stage_sha,
                        "source_catalog_artifact_sha256":"4"*64,
                        "target_ilevel":334,
                        "original_v216_preflight_sha256":"8"*64}),
            encoding="utf8")
        for digest,oil in [(f"{i+1:020x}"+"b"*44,{})
                           for i in range(65)]+[
                           (key,{"main_hand":998877})]:
            doc={"manifest_sha256":digest,"game_build":build,
                 "target_ilevel":334,"simc_revision":"b"*40,
                 "source_catalog_artifact_sha256":"4"*64,
                 "source_catalog_manifest_sha256":"5"*64,
                 "staged_source_environment_sha256":stage_sha,
                 "trusted_budget_evidence_sha256":"6"*64,
                 "original_v196_prepared_options_sha256":"7"*64,
                 "official_G":2800,"official_J":92,"official_F":165,
                 "official_O":{},"official_B":3057,"official_T":3057,
                 "official_O_physical_source":{
                     "selected_oil_item_ids_by_hand":oil},
                 "published_verified_options":[],
                 "published_verified_option_count":0}
            (docs/("v212_installed_"+digest[:20]+".json")).write_text(
                json.dumps(doc),encoding="utf8")
        reads=[]
        def read_json(path,max_bytes=25000000):
            path=pathlib.Path(path)
            reads.append(path.name)
            return json.loads(path.read_text("utf8")),(
                "4"*64 if path.name=="v213_candidate_catalog.json"
                else "0"*64)
        with mock.patch.object(v216.environment_manifest,"read_json",
                 side_effect=read_json), \
             mock.patch.object(v216.environment_manifest,
                 "verify_fresh_installed_environment"), \
             mock.patch.object(v216.environment_manifest,
                 "verify_fresh_source_environment"), \
             mock.patch.object(v216.source_to_catalog,"verify_catalog"), \
             mock.patch.object(v216.stage_engine,"verify_stage",
                 return_value={"receipt_sha256":"9"*64}):
            selected=v216.find_verified_installed_season_environment(
                root,334,expected_game_build=build,
                selected_oil_item_ids_by_hand={"main_hand":998877})
            self.assertEqual(selected["installed_manifest_sha256"],key)
            reads.clear()
            selected=v216.find_verified_installed_season_environment(
                root,334,expected_game_build=build,
                expected_installed_manifest_sha256=key,
                selected_oil_item_ids_by_hand={"main_hand":998877})
        self.assertEqual(selected["installed_manifest_sha256"],key)
        self.assertEqual(len(reads),3) # install, catalog, staged; no Native

    def test_reuse_sealed_tier_source_in_normal_build_without_new_certifier(self):
        from tests.test_v251_db2_raid_tier_simc_bridge import (
            fixture,pinned_thirteen_class_source,BUILD)
        root=self.root/"tier-reuse"
        root.mkdir()
        tier,corroboration=fixture(root)
        tier_path=root/"tier.json"
        corr_path=root/"corr.json"
        tier_path.write_text(json.dumps(tier),encoding="utf8")
        corr_path.write_text(json.dumps(corroboration),encoding="utf8")
        physical=v216.tier_simc_bridge.build_stage(
            stage_root=root,db2_candidate_path=tier_path,
            bonus_candidate_path=corr_path,
            db2_receipt="a"*64,bonus_receipt="b"*64)
        source=json.loads(pathlib.Path(physical["candidate_path"]).read_text("utf8"))
        pinned_thirteen_class_source(root,source)
        matched=v216.tier_simc_bridge.build_first_party_match_stage(
            stage_root=root,physical_candidate_path=physical["candidate_path"],
            physical_stage_receipt=physical["source_stage"]["receipt_sha256"],
            seed_directory=root)
        requested={"class":"paladin","spec":"retribution","target_ilevel":334}
        selected=v216._reuse_existing_tier_source_stage(
            build=BUILD,tier_bridge=physical,first_party=matched,
            request=requested)
        self.assertTrue(selected["source_evidence_reused"])
        self.assertEqual(selected["native_calls"],0)
        self.assertEqual(selected["network_calls_by_stage"],0)
        self.assertEqual(selected["selected_for_request"]["spec"],"retribution")
        self.assertEqual(len(selected["selected_for_request"]["four_piece_item_ids"]),4)
        self.assertEqual(set(selected["source_stage_receipts"]),
                         {"raid_correlated_physical","simc_exact_13_class"})
        self.assertFalse(selected["environment_ready"])
        self.assertFalse(selected["season_membership_verified"])
        same=v216._reuse_existing_tier_source_stage(
            build=BUILD,tier_bridge=physical,first_party=matched)
        self.assertTrue(same["source_evidence_reused"])
        self.assertIsNone(same["selected_for_request"])
        drift=v216._reuse_existing_tier_source_stage(
            build="12.9.9.99999",tier_bridge=physical,
            first_party=matched,request=requested)
        self.assertEqual(drift["status"],"TIER_EXISTING_SOURCE_REUSE_PENDING")
        self.assertEqual(drift["reason"],"V216_TIER_REUSE_GAME_BUILD_DRIFT")
        pending=v216._reuse_existing_tier_source_stage(
            build=BUILD,tier_bridge=physical,first_party={})
        self.assertFalse(pending["source_evidence_reused"])
        # Sealed metadata cannot be used for source reuse when actual
        # first-party IDs or status are absent.
        corrupted=json.loads(pathlib.Path(matched["candidate_path"]).read_text("utf8"))
        corrupted["classes"]["paladin"]["item_set_id"]+=1
        bad_path=root/"corrupted_simc_exact.json"
        bad_path.write_text(json.dumps(corrupted),encoding="utf8")
        altered={**matched,"candidate_path":str(bad_path)}
        self.assertEqual(v216._reuse_existing_tier_source_stage(
            build=BUILD,tier_bridge=physical,first_party=altered)["status"],
            "TIER_EXISTING_SOURCE_REUSE_PENDING")

    def test_v233_G_probe_is_staged_reused_and_tamper_rejected_without_native(self):
        # Exercise actual v229 + v231 + v232 + v233 replay, not a new
        # equipment calculator. Only the existing v251 roster bridge is
        # mocked, as this unit tests the v216 probe output integration.
        from tests.test_v232_simc_only_ordinary_representative import make_fixture
        from tests.test_v229_simc_only_source_seed import (
            BUILD, OLD, REVISION)
        source_root=self.root/"simc_source"
        source_root.mkdir()
        raws=make_fixture()
        for name,raw in raws.items():
            (source_root/name).write_bytes(raw)
        receipt=v216.simc_source.inventory(
            raws,simc_revision=REVISION,expected_build=BUILD,
            previous_game_build=OLD,
            expected_git_blob={
                k:v216.simc_source.git_blob(v) for k,v in raws.items()})
        (source_root/v216.simc_source.RECEIPT).write_text(
            json.dumps(receipt),encoding="utf8")
        tier=v216.tier_simc_bridge.simc_tier.select(
            seed_directory=source_root,cls="paladin",
            spec="retribution",set_option="season_token_test")
        from runner import v167_product_season_gear_adapter as provider
        allowed={
            9020:(5,4,4),9011:(9,4,4),9021:(6,4,4),
            9022:(8,4,4),9023:(2,4,0),9024:(16,4,0),
            9012:(11,4,0),9025:(11,4,0),9010:(17,2,8)}
        items=[{"item_id":iid,"name":f"season_{iid}",
            "category":"plain_representative_candidate",
            "inventory_type":inv,"class_id":cls,"subclass_id":sub,
            "allowed_class_mask":2,"item_set_id":0,
            "source_kinds":["raid_journal"]}
            for iid,(inv,cls,sub) in sorted(allowed.items())]
        catalog={"schema":provider.SCHEMA,
            "status":"CURRENT_SEASON_CANDIDATE_SELECTION_ONLY",
            "season_build":BUILD,"no_old_catalog_seed":True,
            "item_count":len(items),
            "role_counts":{"plain_representative_candidate":len(items)},
            "items":items,
            "not_certified":{"tier_four_set":True,"simc_item_effects":True},
            "new_native_calls":0,"new_api_calls":0}
        rep=v216.simc_representative.find_candidate(
            seed_directory=source_root,tier_candidate=tier,
            target_ilevel=334,season_gear_db=catalog)
        self.assertTrue(rep["generic_G_physical_conditions_verified"])
        self.assertFalse(rep["generic_G_current_season_membership_required"])
        candidate=self.root/"source_candidate.json"
        candidate.write_text(json.dumps(rep),encoding="utf8")
        gear=self.root/"v167.json"
        gear.write_text(json.dumps(catalog),encoding="utf8")
        bridge=self.root/"v251.json"
        bridge.write_text(json.dumps({
            "schema":v216.tier_simc_bridge.SCHEMA,
            "game_build":BUILD}),encoding="utf8")
        stage_root=self.root/"stage"
        stage_root.mkdir()
        kwargs={"stage_root":stage_root,"build":BUILD,
            # Independent candidate: no v217 producer seal was created.
            # Full source replay remains required for this path.
            "one_spec":{"candidate_path":str(candidate)},
            "fresh_gear":{"candidate_path":str(gear)},
            "tier_bridge":{"candidate_path":str(bridge)},
            "seed_directory":source_root,
            "character":{"race":"human"}}
        fake_stage={**kwargs["one_spec"],"source_stage":{"receipt_sha256":"a"*64}}
        with mock.patch.object(v216.g_probe_profile,"_render_verified_candidate") as render:
            rejected=v216._one_spec_source_G_probe_stage(
                **dict(kwargs,one_spec=fake_stage,
                       character={"race":"human","talents":"fake_seal_test"}))
            self.assertEqual(rejected["status"],
                "FRESH_G_PROBE_SOURCE_OR_CHARACTER_PENDING")
            self.assertEqual(rejected["reason"],"STAGE_RECEIPT_MISSING_OR_TOO_LARGE")
            render.assert_not_called()
        with mock.patch.object(v216.tier_simc_bridge,"select_for_simc",
                               return_value={"v231_candidate":tier}) as match:
            first=v216._one_spec_source_G_probe_stage(**kwargs)
            second=v216._one_spec_source_G_probe_stage(**kwargs)
            other=v216._one_spec_source_G_probe_stage(
                **dict(kwargs,character={"race":"dwarf"}))
        self.assertEqual(first["status"],
            "FRESH_ONE_SPEC_PHYSICAL_G_PROFILE_PREPARED_NATIVE_PENDING",
            str(first))
        self.assertEqual(other["status"],
            "FRESH_ONE_SPEC_PHYSICAL_G_PROFILE_PREPARED_NATIVE_PENDING",
            str(other))
        self.assertNotEqual(other["profile_path"],first["profile_path"])
        self.assertEqual(other["source_stage"]["status"],"EXECUTED_AND_SEALED")
        self.assertEqual(match.call_count,2)
        self.assertEqual(first["source_stage"]["status"],
                         "EXECUTED_AND_SEALED")
        self.assertEqual(second["source_stage"]["status"],
                         "REUSED_VERIFIED")
        self.assertEqual(second["source_stage"]["receipt_writes"],0)
        self.assertEqual(second["native_calls"],0)
        self.assertEqual(second["network_calls_by_stage"],0)
        self.assertTrue(second["generic_G_physical_conditions_verified"])
        self.assertFalse(second["generic_G_current_season_membership_required"])
        self.assertIsNone(second["G"])
        self.assertFalse(second["environment_ready"])
        raw=pathlib.Path(first["profile_path"]).read_text(encoding="utf8")
        self.assertIn("chest=simc_source_9020,id=9020,ilevel=334",raw)
        self.assertIn("race=human",raw)
        self.assertFalse(any(line.startswith("level=")
                             for line in raw.splitlines()))
        self.assertNotIn("trinket1=",raw)
        proof=json.loads(pathlib.Path(
            first["profile_receipt_path"]).read_text(encoding="utf8"))
        self.assertEqual(proof["physical_profile_sha256"],
                         first["physical_profile_sha256"])
        self.assertFalse(proof["current_season_membership_certified"])
        self.assertTrue(proof["generic_G_physical_conditions_verified"])
        self.assertFalse(proof["generic_G_current_season_membership_required"])
        self.assertIsNone(proof["level"])
        self.assertEqual(proof["level_mode"],"SIMC_COMPILED_MAX_LEVEL")
        from runner import v234_source_only_one_native_G as native_probe
        # No real subprocess here: v234 must replay the same selected
        # source-only v167 catalog and prepare its Native JSON2 command.
        # max_new=0 makes actual SimC execution forbidden by design.
        with mock.patch.object(native_probe.subprocess,"run",
                               side_effect=AssertionError(
                                   "NATIVE_EXECUTION_FORBIDDEN")) as run:
            plan=native_probe.execute(
                source_directory=source_root,
                tier_candidate=tier,
                representative_candidate=rep,
                race="human",talents=None,
                binary=self.binary,
                expected_binary_sha256=v216.digest(self.binary.read_bytes()),
                output_dir=self.root/"native_plan",
                max_new=0,season_gear_db=catalog)
        run.assert_not_called()
        self.assertEqual(plan["status"],"PREPARED_NATIVE_NOT_EXECUTED")
        self.assertEqual(plan["new_native_calls"],0)
        self.assertIsNone(plan["G"])
        self.assertFalse(plan["environment_ready"])
        self.assertEqual(plan["identity"]["profile_receipt_sha256"],
                         proof["receipt_sha256"])
        self.assertIn("json2=",(
            self.root/"native_plan"/"native.simc").read_text("utf8"))
        # Missing the source DB must never silently mutate a
        # season-selected representative into an old/default gear profile.
        with self.assertRaisesRegex(native_probe.compiler.ProbeBlocked,
                                    "REPLAY_DRIFT"):
            native_probe.execute(
                source_directory=source_root,tier_candidate=tier,
                representative_candidate=rep,race="human",
                talents=None,binary=self.binary,
                expected_binary_sha256=v216.digest(self.binary.read_bytes()),
                output_dir=self.root/"missing_v167_plan",
                max_new=0)

        pathlib.Path(first["profile_path"]).write_text(
            "tampered",encoding="utf8")
        rejected=v216._one_spec_source_G_probe_stage(**kwargs)
        self.assertEqual(rejected["status"],
                         "FRESH_G_PROBE_SOURCE_OR_CHARACTER_PENDING")
        self.assertIn("STAGE_OUTPUT_HASH_MISMATCH",rejected["reason"])
        self.assertIsNone(rejected["G"])

    def test_G_probe_character_context_rejected_before_fetch(self):
        args={"sessions_root":self.root/"unused_network",
              "expected_game_build":"12.2.0.99999",
              "g_probe_character":{"race":"human","level":90}}
        with self.assertRaisesRegex(v216.EnvironmentBuildBlocked,
                                    "V216_G_PROBE_CHARACTER_CONTEXT_INVALID"):
            v216.collect_wago_new_season_source(**args)
        self.assertFalse(args["sessions_root"].exists())
        args["representative_request"]={
            "class":"paladin","spec":"retribution",
            "target_ilevel":334}
        args["g_probe_character"]={"race":"###","level":90}
        with self.assertRaisesRegex(v216.EnvironmentBuildBlocked,
                                    "V216_G_PROBE_CHARACTER_CONTEXT_INVALID"):
            v216.collect_wago_new_season_source(**args)
        args["g_probe_character"]={"race":"human","level":True}
        with self.assertRaisesRegex(v216.EnvironmentBuildBlocked,
                                    "V216_G_PROBE_CHARACTER_CONTEXT_INVALID"):
            v216.collect_wago_new_season_source(**args)
        self.assertFalse(args["sessions_root"].exists())


    def test_p3_ge_live_source_read_timeout_preserves_first_owner_boundary(self):
        # No network/Native, no invented season data. A failed external read
        # must preserve its first owner in the existing T1 error receipt.
        args={"sessions_root":self.root/"timeout_phase",
              "expected_game_build":"12.2.0.99999"}
        with mock.patch.object(v216.discovery_stage,"collect",
                               side_effect=TimeoutError("secret endpoint")):
            with self.assertRaisesRegex(
                v216.EnvironmentBuildBlocked,
                "^V216_AUTHENTICATED_SEASON_DISCOVERY_TIMEOUT$"):
                v216.collect_wago_new_season_source(**args)
        synthetic={"status":"AUTHENTICATED_SEASON_CREDENTIALS_MISSING",
                   "season_join_ready":False,"network_calls_by_stage":0}
        with mock.patch.object(v216.discovery_stage,"collect",
                               return_value=synthetic):
            with mock.patch.object(v216.stage_engine,"execute_stage",
                                   side_effect=TimeoutError("long csv read")):
                with self.assertRaisesRegex(
                    v216.EnvironmentBuildBlocked,
                    "^V216_FRESH_WAGO_SOURCE_TIMEOUT$"):
                    v216.collect_wago_new_season_source(**args)
        # No unconditional cleanup/purge of same-build or previous receipts.
        self.assertFalse((args["sessions_root"]/"_fresh_season_sources"/
                          "wago_12.2.0.99999"/".stage_receipts"/
                          "fresh-wago-db2.json").exists())

    def test_optional_character_level_is_not_resolved_from_season_sources(self):
        # Source-only actual collector must not block on expansion cap.
        # User level is not a normal control; SimC's compiled MAX_LEVEL is.
        args={"sessions_root":self.root/"level_native_default",
              "expected_game_build":"12.2.0.99999",
              "representative_request":{"class":"paladin",
                   "spec":"retribution","target_ilevel":334},
              "g_probe_character":{"race":"human",
                                   "talents":"CAAa"}}
        with mock.patch.object(v216.discovery_stage,"collect",
                               side_effect=RuntimeError("PREFLIGHT_PASSED")):
            with self.assertRaisesRegex(RuntimeError,"PREFLIGHT_PASSED"):
                v216.collect_wago_new_season_source(**args)
        self.assertTrue(args["sessions_root"].exists())
        # No expansion-to-level lookup exists. This is intentionally a
        # Native source-only plan until exact build/items are observed.
        self.assertFalse(hasattr(v216,"_source_expansion_level"))

    def test_fresh_gem_item_relation_reuses_existing_db2_and_v213(self):
        from tests.test_v221_gem_item_db2_relation import (
            GemPropertyRelationTests)
        GemPropertyRelationTests.setUpClass()
        sample = GemPropertyRelationTests(
            "test_exact_two_items_may_share_one_gem_property_no_admission")
        sample.setUp()
        self.addCleanup(sample.doCleanups)
        catalog_path = self.root / "new_v213_catalog.json"
        catalog_path.write_text(
            json.dumps(sample.catalog), encoding="utf8")
        stage_root = self.root / "new_gem_source_stage"
        stage_root.mkdir()
        opts = dict(stage_root=stage_root, wago_folder=sample.folder,
                    source_catalog_path=catalog_path,
                    expected_game_build="12.1.5.70575")
        first = v216._fresh_gem_item_source_stage(**opts)
        second = v216._fresh_gem_item_source_stage(**opts)
        self.assertEqual(first["physical_gem_item_links"], 2)
        self.assertEqual(first["source_stage"]["status"],
                         "EXECUTED_AND_SEALED")
        self.assertEqual(second["source_stage"]["status"],
                         "REUSED_VERIFIED")
        self.assertEqual(second["source_stage"]["receipt_writes"], 0)
        self.assertEqual(second["network_calls_by_stage"], 0)
        self.assertEqual(second["native_calls"], 0)
        self.assertIsNone(second["J"])
        self.assertFalse(second["highest_quality_J_verified"])
        self.assertFalse(second["environment_ready"])
        evidence = json.loads(
            pathlib.Path(second["candidate_path"]).read_text("utf8"))
        self.assertFalse(evidence["automatic_ui_promotion"])
        self.assertTrue(all(not x["ui_selectable"] for x in
                            evidence["joins"]))

    def test_fresh_gem_item_source_hash_drift_blocks_on_cache_hit(self):
        from tests.test_v221_gem_item_db2_relation import (
            GemPropertyRelationTests)
        GemPropertyRelationTests.setUpClass()
        sample = GemPropertyRelationTests(
            "test_exact_two_items_may_share_one_gem_property_no_admission")
        sample.setUp()
        self.addCleanup(sample.doCleanups)
        source_path = self.root / "source_v213.json"
        source_path.write_text(json.dumps(sample.catalog), encoding="utf8")
        stage_root = self.root / "source_stage"
        stage_root.mkdir()
        args = dict(stage_root=stage_root, wago_folder=sample.folder,
                    source_catalog_path=source_path,
                    expected_game_build="12.1.5.70575")
        v216._fresh_gem_item_source_stage(**args)
        with (sample.folder / "ItemSparse.csv").open("ab") as stream:
            stream.write(b"\\n")
        with self.assertRaisesRegex(
                v216.EnvironmentBuildBlocked, "V216_FRESH_GEM_DB2_SOURCE_INVALID"):
            v216._fresh_gem_item_source_stage(**args)

    def test_fresh_gem_snapshot_build_mismatch_never_promotes_J(self):
        from tests.test_v221_gem_item_db2_relation import (
            GemPropertyRelationTests)
        GemPropertyRelationTests.setUpClass()
        sample = GemPropertyRelationTests(
            "test_exact_two_items_may_share_one_gem_property_no_admission")
        sample.setUp()
        self.addCleanup(sample.doCleanups)
        source_path = self.root / "source_v213.json"
        source_path.write_text(json.dumps(sample.catalog), encoding="utf8")
        stage_root = self.root / "source_stage"
        stage_root.mkdir()
        with self.assertRaisesRegex(
                v216.EnvironmentBuildBlocked,
                "V216_FRESH_GEM_V213_GAME_BUILD_MISMATCH"):
            v216._fresh_gem_item_source_stage(
                stage_root=stage_root, wago_folder=sample.folder,
                source_catalog_path=source_path,
                expected_game_build="12.1.5.70576")
        receipt_path = sample.folder / "receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf8"))
        receipt["build"] = "12.1.5.70576"
        receipt_path.write_text(json.dumps(receipt), encoding="utf8")
        with self.assertRaisesRegex(
                v216.EnvironmentBuildBlocked,
                "V216_FRESH_GEM_DB2_SOURCE_INVALID"):
            v216._fresh_gem_item_source_stage(
                stage_root=stage_root, wago_folder=sample.folder,
                source_catalog_path=source_path,
                expected_game_build="12.1.5.70575")

    def test_normal_fresh_build_reaches_gem_source_preflight_before_session(self):
        stage_root = self.root / "fresh_catalog_stage"
        stage_root.mkdir()
        snapshot = self.root / "existing_wago_snapshot"
        snapshot.mkdir()
        catalog = self.root / "fresh_catalog.json"
        catalog.write_text("{}", encoding="utf8")
        missing_session = self.root / ("a" * 20)
        inputs = {"stage_root":stage_root,
                  "v191_path":self.root / "new_v191.json",
                  "simc_source_dir":self.root / "new_simc_source",
                  "simc_manifest_path":self.root / "new_simc_manifest.json",
                  "wago_snapshot_folder":snapshot}
        candidate = {"enchant_classification":{
            "source_manifest_sha256":"f" * 64}}
        with (mock.patch.object(v216.fresh_stage,
                                "compile_fresh_candidate",
                                return_value={"source_catalog_path":str(catalog)})
                  as compile_stage,
              mock.patch.object(v216.environment_manifest, "read_json",
                                return_value=(candidate,"b" * 64)),
              mock.patch.object(v216, "preflight_new_season_source",
                                return_value={"preflight_sha256":"c" * 64})
                  as preflight):
            with self.assertRaisesRegex(v216.EnvironmentBuildBlocked,
                                        "FRESH_SOURCE_PROVENANCE_PASS_GJFO_NOT_READY"):
                v216.build_environment(
                    sessions_root=self.root,session_folder=missing_session,
                    user=self.user,binary=self.binary,revision=self.revision,
                    static_cache=None,source_catalog_path=None,
                    bootstrap_result={},
                    expected_new_season_build="12.1.5.70575",
                    fresh_source_stage_inputs=inputs)
        self.assertFalse(missing_session.exists())
        self.assertNotIn("wago_snapshot_folder", compile_stage.call_args.kwargs)
        self.assertEqual(preflight.call_args.kwargs["source_snapshot_folder"],
                         snapshot)
        self.assertEqual(preflight.call_args.kwargs["source_stage_root"],
                         stage_root)
        self.assertEqual(preflight.call_args.kwargs["expected_game_build"],
                         "12.1.5.70575")

    def test_normal_build_reuses_existing_v229_simc_source_collector_only_once(self):
        from tests.test_v229_simc_only_source_seed import (
            SimCCollectorTests,REVISION,BUILD,OLD)
        fake=SimCCollectorTests("test_collect_pinned_sources_without_any_legacy_data")
        fake.setUp()
        calls=[]
        def transport(req,timeout):
            calls.append(req.full_url)
            return fake.fetch(req,timeout=timeout)
        root=self.root/"new_simc_source"
        root.mkdir()
        empty=v216._collect_first_party_simc_seed_stage(
            stage_root=root,build=BUILD)
        self.assertEqual(empty["network_calls_by_stage"],0)
        self.assertEqual(empty["status"],
                         "SIMC_PINNED_REVISION_NOT_AVAILABLE_PENDING")
        options=dict(stage_root=root,build=BUILD,revision=REVISION,
                     previous_game_build=OLD,transport=transport)
        first=v216._collect_first_party_simc_seed_stage(**options)
        second=v216._collect_first_party_simc_seed_stage(**options)
        self.assertEqual(first["status"],
                         "SIMC_PINNED_SET_SOURCE_RECEIPT_READY")
        self.assertEqual(len(calls),7) # four immutable Git tree + 3 small raw
        self.assertEqual(first["network_calls_by_stage"],7)
        self.assertEqual(second["network_calls_by_stage"],0)
        self.assertEqual(first["source_stage"]["status"],"EXECUTED_AND_SEALED")
        self.assertEqual(second["source_stage"]["status"],"REUSED_VERIFIED")
        path=pathlib.Path(first["source_dir"])
        self.assertEqual(set(x.name for x in path.iterdir()),
                         set(v216.simc_source.SOURCE_FILES)|
                         {v216.simc_source.RECEIPT})
        self.assertFalse((path/"item_data.inc").exists())
        receipt=json.loads((path/v216.simc_source.RECEIPT).read_text())
        self.assertEqual(first["simc_receipt_sha256"],receipt["receipt_sha256"])
        self.assertTrue(receipt["provenance_tree_blob_authenticated"])
        self.assertIsNone(receipt["G"])
        self.assertFalse(receipt["environment_ready"])

    def test_v613_v583_expansion_uses_authenticated_v163_public_scope(self):
        # Real v612: all upstream source stages were SEALED, but v583
        # received None because the collector read an internal source-file
        # key from the outward v163 join instead of its source_scope.
        joined={"status":
            "DB2_WCL_CANDIDATES_JOINED_SEASON_CONDITIONS_PENDING",
            "source_scope":{"expansion_id":11,
                            "source_basis":"WCL_PLUS_WAGO_SEALED"},
            "auto_source_scope":{"expansion_id":999}}
        self.assertEqual(
            v216._original_v163_enchant_expansion_id(joined),11)
        self.assertIsNone(v216._original_v163_enchant_expansion_id({
            "status":"AUTHENTICATED_SEASON_JOIN_NOT_READY"}))
        self.assertIsNone(v216._original_v163_enchant_expansion_id({}))
        self.assertIsNone(v216._original_v163_enchant_expansion_id(None))

    def test_fresh_v189_v190_exact_consumables_reuse_existing_wago_and_simc(self):
        from tests.test_v229_simc_only_source_seed import raw_sources
        from tests.test_v189_simc_choice_discovery import SOURCE
        from tests.test_v190_consumable_item_snapshot_join import prepare
        import io
        build="12.1.5.70575"; revision="a"*40
        folder=self.root/"v258_consumable"
        folder.mkdir()
        wago=folder/"wago";wago.mkdir()
        prepare(wago)
        seed_dir=folder/"simc"
        seed_dir.mkdir()
        raw=raw_sources(build)
        receipt=v216.simc_source.inventory(
            raw,simc_revision=revision,expected_build=build,
            previous_game_build=None,season_event="cold_start",
            expected_git_blob={
                key:v216.simc_source.git_blob(data)
                for key,data in raw.items()})
        (seed_dir/v216.simc_source.RECEIPT).write_text(
            json.dumps(receipt),encoding="utf8")
        pinned={"source_dir":str(seed_dir),
                "simc_receipt_sha256":receipt["receipt_sha256"]}
        scope={"expansion_id":11,"source_basis":
               "LIVE_WCL_ACTIVE_ZONES_AND_SAME_BUILD_DB2"}
        source_path=folder/"v163.json"
        source_path.write_text(json.dumps({
            "schema":v216.season_join.SCHEMA,
            "build":build,
            "source_provider":"WAGO_TOOLS_PINNED_DB2_WCL_LIVE",
            "auto_source_scope":scope}),encoding="utf8")
        linked={"status":
                "DB2_WCL_CANDIDATES_JOINED_SEASON_CONDITIONS_PENDING",
                "candidate_path":str(source_path),
                "source_scope":scope,
                "stage":{"receipt_sha256":"a"*64}}
        calls=[]
        class Response(io.BytesIO):
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):self.close()
        def transport(req,timeout):
            calls.append(req.full_url)
            self.assertEqual(req.full_url,
                v216.simc_effect_candidates.URL_PREFIX+revision+"/"+
                v216.simc_effect_candidates.SOURCE)
            return Response(SOURCE.encode("utf8"))
        args={"stage_root":folder,"wago_folder":wago,
              "build":build,"linked":linked,
              "pinned_simc":pinned,"transport":transport}
        first=v216._fresh_consumable_item_source_stage(**args)
        second=v216._fresh_consumable_item_source_stage(**args)
        self.assertEqual(first["status"],
            "FRESH_FOOD_POTION_FLASK_ENHANCEMENT_DB2_CANDIDATES_NOT_USER_ADMITTED",
            str(first))
        self.assertEqual(first["food_item_count"],1)
        self.assertEqual(first["potion_item_count"],1)
        self.assertEqual(first["flask_physical_item_count"],1)
        self.assertEqual(first["item_enhancement_candidate_count"],2)
        self.assertEqual(first["network_calls_by_stage"],1)
        self.assertEqual(second["network_calls_by_stage"],0)
        self.assertEqual(len(calls),1)
        self.assertEqual(first["source_stage"]["status"],
                         "EXECUTED_AND_SEALED")
        self.assertEqual(second["source_stage"]["status"],
                         "REUSED_VERIFIED")
        self.assertEqual(second["source_stage"]["receipt_writes"],0)
        self.assertEqual((first["J"],first["F"],first["O"]),
                         (None,None,None))
        self.assertFalse(first["environment_ready"])
        candidate=json.loads(pathlib.Path(
            first["candidate_path"]).read_text(encoding="utf8"))
        self.assertEqual({row["item_id"] for row in candidate["items"]},
                         {101,102,105,106,109})
        self.assertEqual(first["source_stage"]["stage_id"],
                         "fresh-v189-v190-consumable-physical-other")
        self.assertFalse(candidate["automatic_ui_promotion"])
        self.assertTrue(all(row["ui_selectable"] is False
                            for row in candidate["items"]))
        self.assertTrue(all(row["simc_token"]=="UNRESOLVED"
                            for row in candidate["items"]))
        # Different physical v163 source bytes must not relabel a cached
        # output or repeat a network fetch; receipt identity blocks it.
        changed=json.loads(source_path.read_text("utf8"))
        changed["suspicious_source_mutation"]=True
        source_path.write_text(json.dumps(changed),encoding="utf8")
        bad=v216._fresh_consumable_item_source_stage(**args)
        self.assertEqual(bad["status"],
            "FRESH_CONSUMABLE_HANDLER_OR_DB2_JOIN_PENDING")
        self.assertIn("STAGE_INPUT",bad["reason"])
        self.assertEqual(bad["network_calls_by_stage"],0)
        self.assertEqual(len(calls),1)

    def test_fresh_v189_v190_without_exact_credible_season_is_pending(self):
        result=v216._fresh_consumable_item_source_stage(
            stage_root=self.root,wago_folder=self.root/"missing",
            build="12.2.0.99999",
            linked={"status":"AUTHENTICATED_SEASON_JOIN_NOT_READY"},
            pinned_simc={"source_dir":None})
        self.assertEqual(result["status"],
                         "FRESH_CONSUMABLE_SAME_BUILD_SOURCE_PENDING")
        self.assertIsNone(result["F"])
        self.assertIsNone(result["O"])
        self.assertEqual(result["network_calls_by_stage"],0)

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
                         "AUTHENTICATED_SOURCE_INCOMPLETE_SEASON_JOIN_PENDING")
        self.assertFalse(first["season_discovery"]["current_season_membership_verified"])
        # Incomplete authenticated provider bodies never reach season
        # ambiguity resolution; the join correctly remains NOT_READY.
        self.assertEqual(first["season_join"]["status"],
                         "AUTHENTICATED_SEASON_JOIN_NOT_READY")
        self.assertFalse(first["season_join"]["season_membership_verified"])
        self.assertFalse(first["environment_installed"])
        # Missing optional permanent-enchant source cannot enlarge an injected
        # Wago transport or block the existing base season source collection.
        self.assertEqual(first["fresh_permanent_enchant_item_source"]["status"],
                         "PERMANENT_ENCHANT_SOURCE_PENDING")
        self.assertEqual(first["fresh_permanent_enchant_item_source"]
                         ["network_calls_by_stage"],0)
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
                 "StatModifier_bonusStat_1":25 if i==3001 else 0,
                 "InventoryType":5,"ItemSet":0,"AllowableClass":0,
                 "ItemLevel":219 if i==1001 else 197}
                for i in (1001,2001,3001)],
            "Item":[{"ID":i,"ClassID":4,"InventoryType":5,"SubclassID":4}
                    for i in (1001,2001,3001)],
        }
        from runner import v168_current_season_tier_discovery as physical
        from runner import v245_db2_first_tier_discovery as db2_tier
        extra_sets=[];extra_spells=[];extra_specs=[]
        for n,(cl,sub) in enumerate(sorted(physical.FAMILY.items())):
            cid=db2_tier.CLASS_IDS[cl]
            for i in (0,1):
                extra_specs.append({"ID":10000+10*n+i,"ClassID":cid})
            for wave in (0,1):
                sid=500+n+100*wave
                iids=[]
                for pos,inv in enumerate((1,3,20,10,7)):
                    iid=910000+100*n+pos if wave==0 else 820000+100*n+pos
                    iids.append(iid)
                    data["ItemSparse"].append({
                        "ID":iid,"Display_lang":"Opaque item "+str(iid),
                        "ExpansionID":11,"OverallQualityID":4,
                        "LimitCategory":0,"StatModifier_bonusStat_0":0,
                        "StatModifier_bonusStat_1":0,
                        "InventoryType":inv,"ItemSet":sid,
                        "AllowableClass":1<<(cid-1),
                        "ItemLevel":197 if wave==0 else 219})
                    data["Item"].append({"ID":iid,"ClassID":4,
                                         "InventoryType":inv,"SubclassID":sub})
                extra_sets.append({"ID":sid,"Name_lang":"Unsearched set "+str(sid),
                    **{"ItemID_"+str(i):iids[i] if i<5 else 0
                       for i in range(17)}})
                for i in (0,1):
                    for th in (2,4):
                        extra_spells.append({"ID":len(extra_spells)+1,
                            "ItemSetID":sid,"ChrSpecID":10000+10*n+i,
                            "Threshold":th,"SpellID":100000+100*n+10*i+th})
        extra_sources={}
        def extra_csv(rs):
            stream=io.StringIO()
            wr=csv.DictWriter(stream,fieldnames=list(rs[0]))
            wr.writeheader();wr.writerows(rs)
            return stream.getvalue().encode("utf8")
        extra_sources["ItemSet"]=extra_csv(extra_sets)
        extra_sources["ItemSetSpell"]=extra_csv(extra_spells)
        extra_sources["ChrSpecialization"]=extra_csv(extra_specs)
        bonus_xrefs=[]
        for wave in (0,1):
            for n in range(len(physical.FAMILY)):
                for pos in range(5):
                    iid=(910000 if wave==0 else 820000)+100*n+pos
                    bonus_xrefs.append({"ID":len(bonus_xrefs)+1,"ItemID":iid,
                       "ItemBonusTreeID":900+wave})
        bonus_xrefs.append({"ID":len(bonus_xrefs)+1,
                           "ItemID":1001,"ItemBonusTreeID":901})
        bonus_nodes=[]
        for wave in (0,1):
            for pos in range(5):
                bonus_nodes.append({"ID":len(bonus_nodes)+1,
                    "ParentItemBonusTreeID":900+wave,
                    "ChildItemBonusTreeID":0,
                    "ChildItemBonusListID":0,
                    "ChildItemBonusListGroupID":
                        (608 if wave==0 else 614)+pos})
        bonus_sources={"ItemXBonusTree":extra_csv(bonus_xrefs),
                       "ItemBonusTreeNode":extra_csv(bonus_nodes)}
        bonus_calls=[]
        def bonus_transport(req,timeout):
            table=urlsplit(req.full_url).path.split("/")[-2]
            bonus_calls.append(table)
            return Response(bonus_sources[table])
        tier_calls=[]
        def tier_transport(req,timeout):
            table=urlsplit(req.full_url).path.split("/")[-2]
            tier_calls.append(table)
            return Response(extra_sources[table])
        report={"schema":"v155_season_discovery_provider_probe_v1",
                "mode":"LIVE_AUTHENTICATED_BOUNDED",
                "blizzard":{"endpoints":{"keystone_season_index":{
                    "data":{"current_season_id":18}}}},
                "wcl":{"midnight_zones":[
                    {"zone_id":10,"zone_name":"Synthetic Raid",
                     "wcl_frozen":False,"encounters":[{"name":"Hydra"}]},
                    {"zone_id":11,"zone_name":"Mythic+ Season 2",
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
                credentials={},tier_transport=tier_transport,
                bonus_transport=bonus_transport)
            second=v216.collect_wago_new_season_source(
                sessions_root=self.root/"runtime",
                expected_game_build="12.2.0.99999",fetch=fetch,
                credentials={},tier_transport=tier_transport,
                bonus_transport=bonus_transport)
            from tests.test_v251_db2_raid_tier_simc_bridge import (
                pinned_thirteen_class_source)
            seed_folder=self.root/"pinned_simc_v229";seed_folder.mkdir()
            tier_candidate=json.loads(pathlib.Path(
                first["fresh_tier_simc_candidate_bridge"]["candidate_path"])
                .read_text(encoding="utf8"))
            pinned_thirteen_class_source(seed_folder,tier_candidate)
            simc_revision="e"*40
            simc_source=v216.simc_source
            source_files={name:(seed_folder/name).read_bytes()
                for name in simc_source.SOURCE_FILES}
            simc_responses={}
            for parent,child in ((simc_revision,("engine","b"*40)),
                                 ("b"*40,("dbc","c"*40)),
                                 ("c"*40,("generated","d"*40))):
                name,tree=child
                simc_responses[simc_source.BASE+parent]=json.dumps({
                    "tree":[{"path":name,"sha":tree,"type":"tree"}]
                }).encode("utf8")
            simc_responses[simc_source.BASE+"d"*40]=json.dumps({
                "tree":[{"path":name,
                         "sha":simc_source.git_blob(raw),
                         "size":len(raw),"type":"blob"}
                        for name,raw in source_files.items()]
                       +[{"path":"item_data.inc","sha":"f"*40,
                          "size":1000,"type":"blob"}]
                }).encode("utf8")
            for name,raw in source_files.items():
                simc_responses[simc_source.RAW_BASE+simc_revision+
                  "/engine/dbc/generated/"+name]=raw
            # An optional v189/v190 stage is now part of the one-spec
            # source acquisition: 1 small pinned effect file, reusing the
            # SAME existing Wago Item/ItemSparse CSV and revision.
            from tests.test_v189_simc_choice_discovery import SOURCE as V189
            simc_responses[
                v216.simc_effect_candidates.URL_PREFIX+simc_revision+
                "/"+v216.simc_effect_candidates.SOURCE
                ]=V189.encode("utf8")
            simc_calls=[]
            def simc_transport(req,timeout):
                simc_calls.append(req.full_url)
                return Response(simc_responses[req.full_url])
            third=v216.collect_wago_new_season_source(
                sessions_root=self.root/"runtime",
                expected_game_build="12.2.0.99999",fetch=fetch,
                credentials={},tier_transport=tier_transport,
                bonus_transport=bonus_transport,
                simc_revision=simc_revision,
                previous_game_build="12.1.5.70575",
                simc_transport=simc_transport)
            fourth=v216.collect_wago_new_season_source(
                sessions_root=self.root/"runtime",
                expected_game_build="12.2.0.99999",fetch=fetch,
                credentials={},tier_transport=tier_transport,
                bonus_transport=bonus_transport,
                simc_revision=simc_revision,
                previous_game_build="12.1.5.70575",
                simc_transport=simc_transport)
        self.assertEqual(len(simc_calls),8)
        self.assertEqual(third["fresh_food_potion_item_sources"]["status"],
            "FRESH_FOOD_POTION_FLASK_ENHANCEMENT_DB2_CANDIDATES_NOT_USER_ADMITTED")
        self.assertEqual(third["fresh_food_potion_item_sources"]
                         ["network_calls_by_stage"],1)
        self.assertEqual(fourth["fresh_food_potion_item_sources"]
                         ["network_calls_by_stage"],0)
        self.assertFalse(third["fresh_food_potion_item_sources"]
                         ["environment_ready"])
        self.assertIsNone(third["fresh_food_potion_item_sources"]["F"])
        self.assertEqual(third["fresh_pinned_first_party_simc_source"]["status"],
                         "SIMC_PINNED_SET_SOURCE_RECEIPT_READY")
        self.assertEqual(third["fresh_pinned_first_party_simc_source"]
                         ["network_calls_by_stage"],7)
        self.assertEqual(fourth["fresh_pinned_first_party_simc_source"]
                         ["network_calls_by_stage"],0)
        self.assertEqual(third["fresh_tier_first_party_simc_options"]["status"],
            "EXACT_13_CLASS_SIMC_SET_OPTIONS_MATCHED_SEASON_PENDING")
        self.assertEqual(third["fresh_tier_selected_from_existing_evidence"]["status"],
            "EXISTING_ACTIVE_RAID_SIMC_EXACT_TIER_SOURCE_REUSED")
        self.assertTrue(third["fresh_tier_selected_from_existing_evidence"]
                        ["source_evidence_reused"])
        self.assertFalse(third["fresh_tier_selected_from_existing_evidence"]
                         ["environment_ready"])
        self.assertEqual(third["fresh_tier_selected_from_existing_evidence"]
                         ["observed_base_item_level"],219)
        self.assertNotIn("DB2_CLASS_TIER_SEASON_MEMBERSHIP_PROOF",
                         third["requires"])
        self.assertEqual(fourth["fresh_tier_selected_from_existing_evidence"]
                         ["network_calls_by_stage"],0)
        self.assertEqual(third["fresh_tier_first_party_simc_options"]
            ["source_stage"]["status"],"EXECUTED_AND_SEALED")
        self.assertEqual(fourth["fresh_tier_first_party_simc_options"]
            ["source_stage"]["status"],"REUSED_VERIFIED")
        self.assertEqual(third["fresh_tier_first_party_simc_options"]
                         ["class_count"],13)
        self.assertFalse(third["fresh_tier_first_party_simc_options"]
                         ["season_membership_verified"])
        self.assertEqual(third["network_calls_by_stage"],8)
        self.assertEqual(fourth["network_calls_by_stage"],0)
        self.assertEqual(second["fresh_tier_first_party_simc_options"]["status"],
            "FIRST_PARTY_SIMC_PINNED_SOURCE_PENDING")
        self.assertEqual(compiled.call_count,1)
        self.assertEqual(len(calls),10)
        self.assertEqual(tier_calls,list(db2_tier.TABLES))
        self.assertEqual(bonus_calls,
                         ["ItemXBonusTree","ItemBonusTreeNode"])
        self.assertEqual(first["fresh_tier"]["network_calls_by_stage"],3)
        bonus=first["fresh_tier_raid_bonus_corroboration"]
        self.assertEqual(bonus["status"],
            "UNIQUE_RAID_BONUS_CORRELATED_TIER_COHORT_SEASON_PENDING")
        self.assertEqual(bonus["observed_leading_cohort"]
                         ["observed_base_item_level"],219)
        self.assertEqual(bonus["observed_leading_cohort"]
                         ["physical_items"],65)
        self.assertEqual(bonus["network_calls_by_stage"],2)
        self.assertEqual(second["fresh_tier_raid_bonus_corroboration"]
                         ["network_calls_by_stage"],0)
        self.assertFalse(bonus["source_season_verified"])
        bridge=first["fresh_tier_simc_candidate_bridge"]
        self.assertEqual(bridge["status"],
            "OBSERVED_CURRENT_RAID_CORRELATED_65_PIECE_TIER_CANDIDATE")
        self.assertEqual(bridge["class_count"],13)
        self.assertEqual(bridge["piece_count"],65)
        self.assertEqual(bridge["source_stage"]["status"],"EXECUTED_AND_SEALED")
        self.assertEqual(second["fresh_tier_simc_candidate_bridge"]
                         ["source_stage"]["status"],"REUSED_VERIFIED")
        self.assertFalse(bridge["season_membership_verified"])
        self.assertFalse(bridge["simc_source_verified"])
        self.assertFalse(bridge["environment_ready"])
        self.assertEqual(second["fresh_tier"]["network_calls_by_stage"],0)
        self.assertEqual(first["fresh_tier"]["status"],
                         "DB2_CLASS_TIER_CANDIDATES_SEASON_PENDING")
        self.assertEqual(first["fresh_tier"]["candidate_set_count"],26)
        self.assertFalse(first["fresh_tier"]["used_publisher_names"])
        self.assertFalse(first["fresh_tier"]["source_season_verified"])
        self.assertEqual(first["tier_discovery_mode"],
                         "DB2_FIRST_NO_PUBLISHER_NAME_LOOKUP")
        self.assertEqual(first["fresh_tier"]["source_stage"]["status"],
                         "EXECUTED_AND_SEALED")
        self.assertEqual(second["fresh_tier"]["source_stage"]["status"],
                         "REUSED_VERIFIED")
        self.assertTrue(pathlib.Path(
            first["fresh_tier"]["candidate_path"]).is_file())
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

    def test_unscoped_db2_tier_discovery_no_blizzard_wcl_credentials(self):
        """New build raw source must not depend on hardcoded Midnight v155."""
        import io
        from urllib.parse import urlsplit
        from tests.test_v245_db2_first_tier_discovery import arrange
        from runner import v245_db2_first_tier_discovery as tierdb
        from runner import v161_wago_db2_snapshot as snapshot
        source=self.root/"source_fixture"
        source.mkdir()
        tier_sources=arrange(source)
        class Response(io.BytesIO):
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):self.close()
        requests=[]
        def fetch(req,timeout):
            table=urlsplit(req.full_url).path.split("/")[-2]
            requests.append(("primary",table))
            if table in ("ItemSparse","Item"):
                return Response((source/(table+".csv")).read_bytes())
            return Response(("ID,Name\n1,"+table+"\n").encode("utf8"))
        def tier_fetch(req,timeout):
            table=urlsplit(req.full_url).path.split("/")[-2]
            requests.append(("tier",table))
            return Response(tier_sources[table])
        args={"sessions_root":self.root/"unscoped_no_credentials",
              "expected_game_build":"12.2.0.99999",
              "fetch":fetch,"tier_transport":tier_fetch,
              "credentials":{k:"" for k in v216.discovery_stage.FIELDS}}
        first=v216.collect_wago_new_season_source(**args)
        second=v216.collect_wago_new_season_source(**args)
        self.assertEqual(len(requests),len(snapshot.TABLES)+len(tierdb.TABLES))
        self.assertEqual(first["network_calls_by_stage"],13)
        self.assertEqual(second["network_calls_by_stage"],0)
        self.assertEqual(first["season_join"]["status"],
                         "AUTHENTICATED_SEASON_JOIN_NOT_READY")
        self.assertEqual(first["fresh_tier"]["candidate_set_count"],26)
        self.assertEqual(first["fresh_tier"]["candidate_counts_by_expansion_id"],
                         {"11":26})
        self.assertFalse(first["fresh_tier"]["source_season_verified"])
        self.assertEqual(first["fresh_tier"]["expansion_selection_source"],
                         "UNSCOPED_OBSERVED_EXPANSIONS_ONLY")
        self.assertIsNone(first["G"])
        self.assertIsNone(first["T"])
        self.assertFalse(first["environment_ready"])
        self.assertFalse(first["environment_installed"])

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


class OriginalPolicyARingFamilyIdentityTests(unittest.TestCase):
    """Exercise original v216 source_relation producer, not a forged browser proof."""

    def test_v217_sealed_source_relation_matches_v220_ring_family(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            (root/"fresh_source").mkdir()
            stamps={"v191":"1"*64,"v211":"2"*64,"v213":"3"*64}
            outputs={"v191":("candidate","fresh_source/v191_candidate.json",
                              "a"*64),
                     "v211":("classification",
                              "fresh_source/v211_classification.json","b"*64),
                     "v213":("candidate",
                              "fresh_source/v213_candidate_catalog.json","c"*64)}
            attest={"stage_root":str(root)}
            receipts={}
            for key,(name,relative,file_sha) in outputs.items():
                attest[key+"_stage"]={
                    "status":"EXECUTED_AND_SEALED",
                    "stage_id":"fresh-"+key,
                    "receipt_sha256":stamps[key]}
                receipts["fresh-"+key]={
                    "stage_id":"fresh-"+key,"stage_version":"1",
                    "status":"COMPLETE","receipt_sha256":stamps[key],
                    "output_paths":{name:relative},
                    "outputs":{name:{"sha256":file_sha,"path":relative}}}
            ring={"enchant_id":7967,
                  "token":"enchant_ring__eyes_of_the_eagle",
                  "quality_rank":2,"slot_group":"finger1/finger2",
                  "slot_resolution_status":"SOURCE_MASK_RESOLVED",
                  "item_class":4,"inventory_type_mask":1<<11,
                  "item_subclass_mask":0}
            classified={**ring,
                        "simc_effect_owner":"SIMC",
                        "simc_effect_reimplemented":False}
            ring={**ring,"classification":classified}
            catalog={"game_build":"12.1.5.70783",
                     "simc_revision":"d"*40,
                     "manifest_sha256":"e"*64,
                     "source_provenance":{
                         "v191":{"sha256":"a"*64},
                         "v211":{"sha256":"b"*64,
                                 "simc_item_enchant_pipeline":{
                                     "static_stat_path":"ITEM_ENCHANTMENT_STAT",
                                     "spell_effect_path":"ITEM_ENCHANTMENT_EQUIP_SPELL",
                                     "passive_spell_path":"passive_enchant",
                                     "owner":"SIMC",
                                     "source_file":"engine/item/enchants.cpp"}}},
                     "enchant_classification":{
                         "status":"SOURCE_CLASSIFIED_NOT_GENERAL_NATIVE_ACCEPTANCE_OR_UI_PROMOTION",
                         "source_manifest_sha256":"3"*64,
                         "rows":[classified]},
                     "catalog":{"enchants":{"items":[ring]}},
                     "v196_enchant_source":{"rows":[{
                         "enchant_id":7967,
                         "token":ring["token"],
                         "inventory_type_mask":1<<11}]}}
            public={"enchant_id":7967,"token":ring["token"],
                    "source_slots":["finger1/finger2"],
                    "highest_source_quality_rank":2}
            def receipt_for(path):
                return receipts[path.stem]
            with mock.patch.object(
                    v216.stage_engine,"_read_receipt",
                    side_effect=receipt_for) as reader:
                produced=v216._v217_policy_A_source_relation_receipts(
                    catalog=catalog,artifact_sha256="c"*64,
                    catalog_path=root/"fresh_source"/
                        "v213_candidate_catalog.json",
                    stage_attestations=attest,public_rows=[public])
            self.assertEqual(reader.call_count,3)
            witness=produced[7967]["source_relation"]
            self.assertEqual(witness["status"],"EXACT_SOURCE_RELATION_VERIFIED")
            self.assertEqual(witness["identity"]["slot"],"finger1/finger2")
            self.assertEqual(witness["identity"]["exact_id"],7967)
            self.assertEqual(witness["identity"]["catalog_sha256"],"e"*64)
            # Exact pinned SimC source/DBC and profile enchant_id syntax
            # attest input only. No effect, quality or E claims are created.
            input_proof=produced[7967]["simc_input"]
            self.assertEqual(input_proof["status"],"SIMC_INPUT_ACCEPTED")
            self.assertEqual(input_proof["input_field"],"enchant_id=7967")
            self.assertFalse(input_proof["gameplay_or_native_effect_attested"])
            import v220_catalog_auto_admission as policy
            candidate=policy.candidate_from_source_enchant(
                {"game_build":catalog["game_build"],
                 "simc_revision":catalog["simc_revision"],
                 "manifest_sha256":catalog["manifest_sha256"]},
                public,original_source_row=ring)
            result=policy.decide(candidate,produced[7967])
            self.assertFalse(result["eligible"])
            self.assertNotIn("EVIDENCE_MISSING:simc_input",result["missing"])
            self.assertIn("EVIDENCE_MISSING:product_input",result["missing"])
            self.assertIn("EVIDENCE_MISSING:chmv_budget",result["missing"])
            # An obsolete v211 source or missing SimC pipeline cannot grant
            # syntax evidence. Sealed source_relation remains available.
            for mismatch in (
                    {"enchant_classification":{"status":"SOURCE_ONLY",
                                                "rows":[classified]}},
                    {"source_provenance":{
                        **catalog["source_provenance"],
                        "v211":{"sha256":"b"*64}}},
                    {"enchant_classification":{
                        **catalog["enchant_classification"],
                        "rows":[{**classified,"token":"enchant_ring__other"}]}}):
                altered={**catalog,**mismatch}
                with mock.patch.object(
                    v216.stage_engine,"_read_receipt",
                    side_effect=receipt_for):
                    pending=v216._v217_policy_A_source_relation_receipts(
                        catalog=altered,artifact_sha256="c"*64,
                        catalog_path=root/"fresh_source"/
                            "v213_candidate_catalog.json",
                        stage_attestations=attest,public_rows=[public])
                self.assertNotIn("simc_input",pending[7967])
                self.assertIn("source_relation",pending[7967])



    def test_v606_exact_static_nonchmv_source_produces_E0_not_quality(self):
        """Sealed v211 component types may prove E0, not item usability."""
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            (root/"fresh_source").mkdir()
            stamps={"v191":"1"*64,"v211":"2"*64,"v213":"3"*64}
            files={"v191":("candidate","fresh_source/v191_candidate.json",
                           "a"*64),
                   "v211":("classification",
                           "fresh_source/v211_classification.json","b"*64),
                   "v213":("candidate",
                           "fresh_source/v213_candidate_catalog.json","c"*64)}
            receipts={}
            att={"stage_root":str(root)}
            for name,(output,path,sha) in files.items():
                att[name+"_stage"]={"status":"REUSED_VERIFIED",
                    "stage_id":"fresh-"+name,"receipt_sha256":stamps[name]}
                receipts["fresh-"+name]={"stage_id":"fresh-"+name,
                    "stage_version":"1","status":"COMPLETE",
                    "receipt_sha256":stamps[name],
                    "output_paths":{output:path},
                    "outputs":{output:{"sha256":sha,"path":path}}}
            slot="feet"
            row={"enchant_id":91010,"token":"enchant_boots__static_stamina",
                 "quality_rank":2,"slot_group":slot,
                 "slot_resolution_status":"SOURCE_MASK_RESOLVED",
                 "item_class":4,"inventory_type_mask":1<<8,
                 "item_subclass_mask":0}
            component={"component_index":1,"item_mod_id":7,
                       "item_mod":"stamina","category":"NON_CHMV_STAT",
                       "dbc_amount":120,"scaling_id":0,"coefficient":0.0}
            category={
                **{k:row[k] for k in ("enchant_id","token","quality_rank",
                   "item_class","inventory_type_mask","item_subclass_mask")},
                "simc_effect_owner":"SIMC",
                "simc_effect_reimplemented":False,
                "effect_family":"static_nonchmv_item_mod",
                "effect_source_status":"DBC_STAT_AND_SPELLTEXT_SOURCE_CLASSIFIED",
                "budget_policy":
                    "NO_STATIC_CHMV_COMPONENT_IN_DBC_ROW; DYNAMIC_EFFECTS_STAY_WITH_SIMC",
                "static_components":[component],
                "static_chmv_rating_present_in_dbc":False,
                "static_chmv_stats":[],"spell_effects":[],
                "unknown_components":[],
                "dynamic_chmv_proc_present_in_spell_text":False,
                "dynamic_chmv_proc_roles":[],"simc_custom_handlers":[],
                "simc_generic_or_unregistered_spell_count":0,
                "native_E_evidence":{"status":"NOT_MEASURED_NEW_BUILD",
                    "static_E":None,"ui_selectable":False,"source_file":None},
                "selection_status":
                    "LOCKED_PENDING_CURRENT_SEASON_ITEM_EFFECT_PROOF"}
            public={"enchant_id":91010,"token":row["token"],
                    "source_slots":[slot],
                    "highest_source_quality_rank":2}
            cat={"game_build":"12.1.5.70783","simc_revision":"d"*40,
                 "manifest_sha256":"e"*64,
                 "source_provenance":{
                     "v191":{"sha256":"a"*64},
                     "v211":{"sha256":"b"*64,
                         "simc_item_enchant_pipeline":{
                             "owner":"SIMC",
                             "source_file":"engine/item/enchants.cpp",
                             "static_stat_path":"ITEM_ENCHANTMENT_STAT",
                             "spell_effect_path":"ITEM_ENCHANTMENT_EQUIP_SPELL",
                             "passive_spell_path":"passive_enchant"}}},
                 "enchant_classification":{
                     "status":
                         "SOURCE_CLASSIFIED_NOT_GENERAL_NATIVE_ACCEPTANCE_OR_UI_PROMOTION",
                     "source_manifest_sha256":"f"*64,
                     "rows":[category]},
                 "catalog":{"enchants":{"items":[{
                     **row,"classification":category}]}},
                 "v196_enchant_source":{"rows":[{
                     "enchant_id":91010,"token":row["token"],
                     "inventory_type_mask":1<<8}]}}
            def produce(c):
                with mock.patch.object(v216.stage_engine,"_read_receipt",
                                       side_effect=lambda p:receipts[p.stem]):
                    return v216._v217_policy_A_source_relation_receipts(
                        catalog=c,artifact_sha256="c"*64,
                        catalog_path=root/"fresh_source"/
                            "v213_candidate_catalog.json",
                        stage_attestations=att,public_rows=[public])
            proof=produce(cat)[91010]
            self.assertEqual(set(proof),
                             {"source_relation","simc_input","chmv_budget"})
            self.assertEqual(proof["chmv_budget"]["fixed_E"],
                             dict.fromkeys(v216.season_budget_contract.STATS,0))
            self.assertEqual(proof["chmv_budget"]["status"],
                             "CHMV_ACCOUNTING_VERIFIED")
            self.assertFalse(proof["chmv_budget"][
                "gameplay_or_native_effect_attested"])
            import v220_catalog_auto_admission as policy
            item=policy.candidate_from_source_enchant(
                {"game_build":cat["game_build"],
                 "simc_revision":cat["simc_revision"],
                 "manifest_sha256":cat["manifest_sha256"]},
                public,original_source_row=row)
            decision=policy.decide(item,proof)
            self.assertFalse(decision["eligible"])
            self.assertEqual(decision["missing"],
                             ["EVIDENCE_MISSING:product_input"])
            # v608: static gear rating E0 is independent from SimC-owned
            # passive spells, dynamic CHMV procs and custom handlers.
            proc={"component_index":2,"driver_spell_id":12345,
                  "effect_role":"TEMPORARY_HASTE_RATING_PROC",
                  "simc_custom_handler":"source_provided_handler"}
            for spell_only in (False,True):
                with self.subTest(spell_only=spell_only):
                    spell_cls={**category,
                        "effect_family":("simc_spell_effect" if spell_only
                                         else "static_nonchmv_plus_simc_spell"),
                        "static_components":([] if spell_only else [component]),
                        "spell_effects":[proc],
                        "dynamic_chmv_proc_present_in_spell_text":True,
                        "dynamic_chmv_proc_roles":["TEMPORARY_HASTE_RATING_PROC"],
                        "simc_custom_handlers":["source_provided_handler"]}
                    sp={**cat,"enchant_classification":{
                        **cat["enchant_classification"],"rows":[spell_cls]},
                        "catalog":{"enchants":{"items":[{
                            **row,"classification":spell_cls}]}}}
                    allowed=produce(sp)[91010]
                    self.assertIn("chmv_budget",allowed)
                    self.assertEqual(allowed["chmv_budget"]["fixed_E"],
                                     dict.fromkeys(v216.season_budget_contract.STATS,0))
                    self.assertFalse(allowed["chmv_budget"][
                        "gameplay_or_native_effect_attested"])
            # Unknown static item mods or present static CHMV must not be
            # silently represented by E0; malformed spell rows also fail.
            for changed in (
                {"spell_effects":[{"component_index":2,
                                   "driver_spell_id":None}]},
                {"unknown_components":[{"item_mod_or_spell_id":99}]},
                {"static_chmv_rating_present_in_dbc":True},
                {"static_chmv_stats":["haste_rating"]},
                {"budget_policy":"STATIC_E_REQUIRES_EXACT_MATCHED_NATIVE_PROFILE_AND_IS_FIXED_INSIDE_G"},
                {"static_components":[{**component,
                     "category":"CHMV_SECONDARY_RATING"}]},
                {"native_E_evidence":{**category["native_E_evidence"],
                     "status":"MEASURED_ONE_OTHER_SCOPE"}},
            ):
                with self.subTest(changed=changed):
                    cls={**category,**changed}
                    tampered={**cat,"enchant_classification":{
                        **cat["enchant_classification"],"rows":[cls]},
                        "catalog":{"enchants":{"items":[{
                            **row,"classification":cls}]}}}
                    limited=produce(tampered)[91010]
                    self.assertNotIn("chmv_budget",limited)
                    self.assertIn("simc_input",limited)
                    self.assertFalse(policy.decide(item,limited)["eligible"])
            # The first v212 staging consumer transfers only signed E0
            # and never treats a client-submitted proof as authoritative.
            preflight={
                "schema":v216.FRESH_SOURCE_PREFLIGHT_SCHEMA,
                "game_build":cat["game_build"],
                "simc_revision":cat["simc_revision"],
                "source_catalog_manifest_sha256":cat["manifest_sha256"],
                "source_artifact_sha256":"c"*64,
                "preflight_sha256":"d"*64,"environment_ready":False,
                "optional_policy_A_evidence_unadmitted":{
                    "original_v217_source_relation_receipts_internal":{
                        91010:proof},
                    "v217_source_relation_scoped_only":True,
                    "v217_source_relation_receipt_count":1,
                    "source_catalog_manifest_sha256":cat["manifest_sha256"],
                    "source_catalog_artifact_sha256":"c"*64}}
            staged={"status":"FRESH_SEASON_ENVIRONMENT_STAGED_NOT_INSTALLED",
                    "original_v216_preflight_sha256":"d"*64,
                    "stage_status":"REUSED_VERIFIED"}
            merged=v216._fresh_source_owner_merge_policy_A_original_source_relation(
                preflight=preflight,staged=staged,
                trusted_policy_A_receipts_by_id={})
            self.assertEqual(set(merged[91010]),set(proof))
            forged=copy.deepcopy(preflight)
            forged["optional_policy_A_evidence_unadmitted"] =copy.deepcopy(
                preflight["optional_policy_A_evidence_unadmitted"])
            forged["optional_policy_A_evidence_unadmitted"][
                "original_v217_source_relation_receipts_internal"][91010][
                    "chmv_budget"]["fixed_E"]["haste_rating"]=5
            with self.assertRaisesRegex(
                    v216.EnvironmentBuildBlocked,
                    "V216_POLICY_A_ORIGINAL_STATIC_E0_SOURCE_PROOF_DRIFT"):
                v216._fresh_source_owner_merge_policy_A_original_source_relation(
                    preflight=forged,staged=staged,
                    trusted_policy_A_receipts_by_id={})


class OriginalOptionalEnchantSnapshotSourceTests(unittest.TestCase):
    """The verified v113 user profile keeps only a source locator, not DB bytes."""

    def test_original_optional_enchant_reference_is_bounded_and_replayable(self):
        candidate={"status":"PERMANENT_ENCHANT_EXACT_WAGO_SIMC_SOURCE_ONLY",
                   "candidate_path":"/source/fresh_source/v583.json",
                   "source_stage":{
                       "stage_id":"v583","receipt_sha256":"a"*64,
                       "output_paths":{"candidate":"fresh_source/v583.json",
                                       "other":"large-unneeded"},
                       "large_data_should_not_copy":["x"*1000]},
                   "enchant_items":[{"item_id":i} for i in range(32)]}
        extracted=v216.original_optional_enchant_source_reference({
            "fresh_permanent_enchant_item_source":candidate})
        self.assertEqual(extracted,{
            "status":"PERMANENT_ENCHANT_EXACT_WAGO_SIMC_SOURCE_ONLY",
            "candidate_path":"/source/fresh_source/v583.json",
            "source_stage":{"stage_id":"v583","receipt_sha256":"a"*64,
                            "output_paths":{"candidate":"fresh_source/v583.json"}}})
        self.assertNotIn("enchant_items",extracted)
        self.assertNotIn("large_data_should_not_copy",extracted["source_stage"])

    def test_missing_unselected_source_stays_optional_no_native_or_fetch(self):
        self.assertIsNone(v216.original_optional_enchant_source_reference({}))
        self.assertIsNone(v216.original_optional_enchant_source_reference({
            "fresh_permanent_enchant_item_source":{"status":"PENDING"}}))
        self.assertIsNone(v216.original_optional_enchant_source_reference({
            "fresh_permanent_enchant_item_source":{
                "status":"PERMANENT_ENCHANT_EXACT_WAGO_SIMC_SOURCE_ONLY",
                "candidate_path":"/source/v583.json",
                "source_stage":{"stage_id":"v583",
                                "receipt_sha256":"NOT_A_SHA",
                                "output_paths":{"candidate":"source/v583.json"}}}}))


class FirstSealedEnchantScopeBridgeTests(unittest.TestCase):
    """No real source download or Native; actual v216 -> v196 consumer call."""

    def test_missing_optional_enchant_does_not_block_base(self):
        out=v216._fresh_first_sealed_representative_enchant_mask_preview(
            collected={},compilation={})
        self.assertEqual(out["status"],
                         "SEALED_REPRESENTATIVE_ENCHANT_SCOPE_PENDING")
        self.assertFalse(out["ui_selectable"])
        self.assertEqual((out["native_calls"],out["network_calls"]),(0,0))

    def test_v584_supplement_requires_original_wago_identity_and_same_revision(self):
        revision="d"*40
        source_row={"enchant_id":7939,
                    "simc_token":"bright_linen_spellthread",
                    "quality_rank_simc":2,
                    "source_class_and_masks":{
                        "item_class":4,"inventory_type_mask":1<<7,
                        "item_subclass_mask":0x1e},
                    "physical_item_ids":[240133],
                    "selection_status":
                        "SUPPLEMENTAL_SOURCE_ONLY_NOT_USER_PUBLISHED",
                    "ui_selectable":False,
                    "raw_rank_component_evidence":{
                        "quality_noninferiority_runtime_verified":False}}
        join={
            "game_build":"12.1.5.70783",
            "additional_enchants_unadmitted":[{
                "enchant_id":7939,
                "scope":"DPS_EQUIPMENT_PERMANENT_CANDIDATE_UNADMITTED",
                "simc_source_rows":[{
                    "enchant_id":7939,
                    "simc_token":"bright_linen_spellthread",
                    "quality_rank":2,"item_class":4,
                    "inventory_type_mask":1<<7,
                    "item_subclass_mask":0x1e}],
                "physical_items":[{"item_id":240133}]}],
            "supplemental_gear_effects_source_only":{
                "status":"SUPPLEMENTAL_DPS_ENCHANT_EFFECTS_CLASSIFIED_UNADMITTED",
                "game_build":"12.1.5.70783",
                "simc_revision":revision,"candidate_count":1,
                "source_only":True,"ui_selectable":False,
                "rows":[source_row]}}
        matched=v216._v216_reuse_sealed_v584_selected_supplemental(
            join,7939,revision)
        self.assertEqual(matched["enchant_id"],7939)
        self.assertEqual(matched["physical_items"][0]["item_id"],240133)
        self.assertFalse(matched["supplemental_source"]["ui_selectable"])
        self.assertIsNone(v216._v216_reuse_sealed_v584_selected_supplemental(
            join,7939,"a"*40))
        from copy import deepcopy
        swapped=deepcopy(join)
        swapped["supplemental_gear_effects_source_only"]["rows"][0][
            "physical_item_ids"]=[999999]
        self.assertIsNone(v216._v216_reuse_sealed_v584_selected_supplemental(
            swapped,7939,revision))
        self.assertIsNone(v216._v216_reuse_sealed_v584_selected_supplemental(
            join,999999,revision))


    def test_existing_v232_v230_v583_source_calls_v196_without_admission(self):
        build="12.1.5.70783"
        revision="d"*40
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            def staged(folder, name, payload, stamp):
                relative=folder+"/"+name+".json"
                path=root/relative
                path.parent.mkdir(parents=True,exist_ok=True)
                raw=json.dumps(payload,sort_keys=True).encode("utf8")
                path.write_bytes(raw)
                return {"candidate_path":str(path),"source_stage":{
                    "stage_id":name,"output_paths":{"candidate":relative},
                    "receipt_sha256":stamp}},raw
            representative={
                "game_build":build,"simc_revision":revision,
                "source_seed_receipt_sha256":"b"*64,
                "item_data_sha256":"e"*64,
                "selected_G_slot_ids":{"finger1":268266}}
            rep,rep_raw=staged("source","v232",representative,"c"*64)
            join={"game_build":build,
                  "status":"PERMANENT_ENCHANT_EXACT_WAGO_SIMC_SOURCE_ONLY",
                  "matches":[{"enchant_id":8025,
                              "physical_items":[{"item_id":244444}],
                              "simc_rank_rows":[{
                                  "enchant_id":8025,"item_class":4,
                                  "inventory_type_mask":1<<11,
                                  "item_subclass_mask":0}]}],
                  "additional_enchants_unadmitted":[{
                      "enchant_id":7939,
                      "scope":"DPS_EQUIPMENT_PERMANENT_CANDIDATE_UNADMITTED",
                      "simc_source_rows":[{
                          "enchant_id":7939,
                          "simc_token":"bright_linen_spellthread",
                          "quality_rank":2,"item_class":4,
                          "inventory_type_mask":1<<7,
                          "item_subclass_mask":0x1e}],
                      "physical_items":[{"item_id":240133}]}],
                  "supplemental_gear_effects_source_only":{
                      "status":"SUPPLEMENTAL_DPS_ENCHANT_EFFECTS_CLASSIFIED_UNADMITTED",
                      "game_build":build,"simc_revision":revision,
                      "candidate_count":1,
                      "source_only":True,"ui_selectable":False,
                      "rows":[{
                          "enchant_id":7939,
                          "simc_token":"bright_linen_spellthread",
                          "quality_rank_simc":2,
                          "source_class_and_masks":{
                              "item_class":4,
                              "inventory_type_mask":1<<7,
                              "item_subclass_mask":0x1e},
                          "physical_item_ids":[240133],
                          "source_slot":{"status":"SOURCE_MASK_RESOLVED"},
                          "selection_status":
                              "SUPPLEMENTAL_SOURCE_ONLY_NOT_USER_PUBLISHED",
                          "ui_selectable":False,
                          "static_E_source_status":
                              "NO_STATIC_CHMV_COMPONENT_IN_SIMC_DBC",
                          "raw_rank_component_evidence":{
                              "same_effect_and_use_conditions_verified":False,
                              "quality_noninferiority_runtime_verified":False}
                      }]}}
            wago,join_raw=staged("fresh_source","v583",join,"f"*64)
            def read_receipt(path):
                name=path.stem
                contents=rep_raw if name=="v232" else join_raw
                stamp="c"*64 if name=="v232" else "f"*64
                return {"receipt_sha256":stamp,
                        "output_paths":{"candidate":(
                            "source/v232.json" if name=="v232" else
                            "fresh_source/v583.json")},
                        "outputs":{"candidate":{"sha256":
                            v216.digest(contents)}}}
            source={"game_build":build,"simc_revision":revision,
                    "manifest_sha256":"a"*64,
                    "v196_enchant_source":{"rows":[{
                        "enchant_id":8025,"item_class":4,
                        "inventory_type_mask":1<<11,
                        "item_subclass_mask":0}]}}
            metadata={"game_build":build,"simc_revision":revision,
                      "source_sha256":"e"*64,
                      "source_receipt_sha256":"b"*64,
                      "items":[{"item_id":268266,"class_id":4,
                                "subclass_id":0,"inventory_type":11}]}
            collected={
                "expected_game_build":build,
                "fresh_one_spec_simc_representative":{
                    "status":"FRESH_ONE_SPEC_SIMC_G_SOURCE_CANDIDATE_PENDING_NATIVE",
                    **rep},
                "fresh_permanent_enchant_item_source":{
                    "status":"PERMANENT_ENCHANT_EXACT_WAGO_SIMC_SOURCE_ONLY",
                    **wago},
                "fresh_lazy_full_pinned_simc_item_source":{
                    "source_dir":str(root/"source"/"v256_full_pinned_simc")}}
            compiled={"stage_root":str(root),"simc_revision":revision,
                      "source_catalog_path":str(root/"fresh_source"/"v213.json")}
            with (mock.patch.object(v216.stage_engine,"_read_receipt",
                                    side_effect=read_receipt),
                  mock.patch.object(v216.simc_item_metadata,"from_seed",
                                    side_effect=lambda directory,item_ids:{
                                        **metadata,"items":[{
                                            **metadata["items"][0],
                                            "item_id":item_ids[0],
                                            "inventory_type":(
                                                7 if item_ids[0]==268268 else 11),
                                            "subclass_id":(
                                                4 if item_ids[0]==268268 else 0)
                                        }]}) as parsed,
                  mock.patch.object(v216.environment_manifest,"read_json",
                                    return_value=(source,"hash")),
                  mock.patch.object(v216.user_catalog.source_bridge,
                                    "verify_catalog")):
                out=v216._fresh_first_sealed_representative_enchant_mask_preview(
                    collected=collected,compilation=compiled)
                # Final user item differs from the G reference ring; exactly
                # one additional item is resolved, not a gear-market scan.
                actual=v216._fresh_first_sealed_representative_enchant_mask_preview(
                    collected=collected,compilation=compiled,
                    selected_user_item={"slot":"finger1","item_id":268267},
                    selected_enchant_id=8025)
                wrong=v216._fresh_first_sealed_representative_enchant_mask_preview(
                    collected=collected,compilation=compiled,
                    selected_user_item={"slot":"feet","item_id":268267},
                    selected_enchant_id=8025)
                missing=v216._fresh_first_sealed_representative_enchant_mask_preview(
                    collected=collected,compilation=compiled,
                    selected_user_item={"slot":"finger1","item_id":268267},
                    selected_enchant_id=999999)
                supplemental=v216._fresh_first_sealed_representative_enchant_mask_preview(
                    collected=collected,compilation=compiled,
                    selected_user_item={"slot":"legs","item_id":268268},
                    selected_enchant_id=7939)
            # Missing physical enchant never triggers an extra v230 scan.
            self.assertEqual(parsed.call_count,4)
            self.assertTrue(supplemental["matched"],supplemental)
            self.assertTrue(supplemental["supplemental_v583_v584_source_only"])
            self.assertEqual(supplemental["selected_slot"],"legs")
            self.assertEqual(supplemental["enchant_id"],7939)
            self.assertEqual(supplemental["source_observed_static_E_status"],
                             "NO_STATIC_CHMV_COMPONENT_IN_SIMC_DBC")
            self.assertFalse(supplemental["fixed_E_or_no_E_verified"])
            self.assertFalse(supplemental["same_effect_and_highest_quality_verified"])
            self.assertFalse(supplemental["ui_selectable"])
            self.assertEqual(missing["status"],
                             "SEALED_REPRESENTATIVE_ENCHANT_SCOPE_PENDING")
            self.assertTrue(actual["matched"],actual)
            self.assertEqual(actual["selected_representative_item_id"],268267)
            self.assertFalse(actual["reference_representative_not_user_equipment"])
            self.assertTrue(actual["actual_user_item_from_v098_final_rows"])
            self.assertFalse(actual["ui_selectable"])
            self.assertFalse(actual["policy_A_product_input_verified"])
            self.assertEqual(wrong["status"],"SOURCE_MASK_OR_HAND_NOT_MATCHED")
            self.assertFalse(wrong["matched"])
            self.assertTrue(out["matched"],out)
            self.assertEqual(out["selected_representative_item_id"],268266)
            self.assertEqual(out["wago_physical_enchant_item_id"],244444)
            self.assertEqual(out["selected_slot"],"finger1")
            self.assertTrue(out["reference_representative_not_user_equipment"])
            self.assertFalse(out["policy_A_product_input_verified"])
            self.assertFalse(out["ui_selectable"])
            self.assertEqual((out["native_calls"],out["network_calls"]),(0,0))


if __name__=="__main__":
    unittest.main()
