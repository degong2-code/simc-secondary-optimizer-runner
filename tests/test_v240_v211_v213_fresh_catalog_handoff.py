"""Fresh v211 → existing v213 source-to-catalog handoff: variable count.

Synthetic sources only. Same normal compiler functions, NO new parallel
Environment Builder, NO user UI admission, Native 0, network 0. This does
NOT certify current-season source retrieval, actual G/J/F/O or v196 readiness.
"""
from __future__ import annotations
import copy
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

from runner import v211_enchant_source_effect_classification as classifier
from runner import v213_source_to_catalog as join
from tests.test_v213_source_to_catalog import SourceToCatalogTests
from tests.test_v239_v211_fresh_season_dynamic_classifier import (
    BUILD,REV,fixture_source,put_sources)


class SameFreshCatalogChain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use existing fixture for all non-enchant v191 structural fields.
        # The new-season enchant identities and bytes are generated in-test.
        SourceToCatalogTests.setUpClass()

    def inputs(self,folder):
        old=SourceToCatalogTests()
        season,_old_classification=old.build_inputs()
        real_source,generated=fixture_source()
        manifest=put_sources(folder,generated)
        season["game_build"]=BUILD
        season["simc_revision"]=REV
        season["source_artifacts"]["v189"]["simc_commit"]=REV
        season["source_artifacts"]["v190"]["simc_revision"]=REV
        season["source_artifacts"]["v190"]["game_build"]=BUILD
        for record in season["simc_generated_sources"].values():
            record["source_build"]=BUILD
        season["enchants"].pop("current_season_midnight")
        season["enchants"]["current_season"]=real_source["enchants"]["current_season"]
        current=classifier.compile_fresh_season(season,folder,manifest)
        return season,current

    def test_join_variable_two_items_and_no_old_7967_8025_or_e(self):
        with tempfile.TemporaryDirectory() as d:
            season,classified=self.inputs(pathlib.Path(d))
            artifact=join.compile_catalog(
                season,"a"*64,classified,"b"*64)
            again=join.compile_catalog(
                season,"a"*64,classified,"b"*64)
        self.assertTrue(join.verify_catalog(artifact))
        self.assertEqual(artifact["manifest_sha256"],again["manifest_sha256"])
        self.assertEqual(artifact["catalog"]["enchants"]["count"],2)
        self.assertEqual(artifact["catalog_summary"]["enchants"][
                         "existing_user_approval_id"],None)
        self.assertEqual(artifact["catalog"]["enchants"]["selection_policy"][
                         "only_existing_native_scoped_choice"],None)
        self.assertEqual(artifact["catalog"]["enchants"]["selection_policy"][
                         "developer_only"],[])
        self.assertFalse(artifact["automatic_ui_promotion"])
        self.assertEqual(artifact["native_calls"],0)
        self.assertEqual(artifact["network_calls"],0)
        self.assertTrue(all(not x["ui_selectable"] for x
            in artifact["catalog"]["enchants"]["items"]))
        self.assertTrue(all(not x["approved"] for x
            in artifact["v196_enchant_source"]["rows"]))

    def test_same_v196_ui_bridge_shows_unapproved_fresh_catalog_without_old_data(self):
        import v196_current_season_user_catalog as ui
        with tempfile.TemporaryDirectory() as d:
            folder=pathlib.Path(d)
            season,classified=self.inputs(folder)
            artifact=join.compile_catalog(season,"a"*64,classified,"b"*64)
            p=folder/"fresh_v213.json"
            p.write_text(json.dumps(artifact,ensure_ascii=False),encoding="utf8")
            with (
                patch.object(ui.v188,"labels",side_effect=AssertionError(
                    "OLD_INSTALLED_SEASON_LABELS_FORBIDDEN")),
                patch.object(ui.observed_enchant,"read",side_effect=AssertionError(
                    "OLD_NATIVE_E_FORBIDDEN")),
            ):
                result=ui.public_options(p)
            self.assertEqual(result["season_build"],BUILD)
            self.assertEqual(result["simc_revision"],REV)
            self.assertEqual(result["enchant_candidates"]["total"],2)
            self.assertEqual(result["enchant_candidates"]["selectable_count"],0)
            policy=result["automatic_admission"]
            self.assertEqual(policy["schema"],
                "v220_exact_evidence_automatic_admission_policy_v1")
            self.assertEqual(policy["status"],
                "PENDING_EXACT_ITEM_AND_BUDGET_PROOFS")
            self.assertEqual(policy["approved_count"],0)
            self.assertEqual(policy["automatically_eligible"],0)
            self.assertEqual(policy["pending"],2)
            self.assertFalse(policy["selection_mutated"])
            self.assertEqual(
                len(policy["per_item_missing_reasons"]),2)
            self.assertTrue(all(
                {f"EVIDENCE_MISSING:{family}" for family in
                 ("source_relation","simc_input","product_input",
                  "chmv_budget")} <= set(reasons)
                for reasons in policy["per_item_missing_reasons"].values()))
            self.assertTrue(all(
                not row["ui_selectable"] and row["blocked_reason"]
                for row in result["enchant_candidates"]["items"]))
            self.assertEqual(result["existing_allowed_input_choices"],{})
            self.assertEqual(result["proven_armor_embellishments"],{})
            self.assertFalse(result["environment_ready"])
            self.assertFalse(result["new_approval_granted"])
            self.assertEqual(result["native_calls_now"],0)
            for key in ("G","J","F","O","B","T"):
                self.assertIsNone(result[key])
            self.assertTrue(all(not row["ui_selectable"] for row in
                                result["enchant_candidates"]["items"]))

    def test_internal_exact_receipts_do_not_publish_unresolved_slots(self):
        import v196_current_season_user_catalog as ui
        import v220_catalog_auto_admission as policy
        with tempfile.TemporaryDirectory() as td:
            folder=pathlib.Path(td)
            season,classified=self.inputs(folder)
            artifact=join.compile_catalog(season,"a"*64,classified,"b"*64)
            path=folder/"fresh_policy_a.json"
            path.write_text(json.dumps(artifact),encoding="utf8")
            original=ui.public_options(path)
            self.assertEqual(original["automatic_admission"]["pending"],2)
            candidate={"kind":"permanent_enchant","exact_id":91001,
                       "simc_token":"enchant_ring__new_haste",
                       "slot":"SOURCE_SLOT_UNRESOLVED",
                       "slot_status":"PENDING_EXACT_SLOT_OR_HAND",
                       "game_build":BUILD,"simc_revision":REV,
                       "catalog_sha256":artifact["manifest_sha256"]}
            identity=policy._identity(candidate)
            receipts={name:{"identity":identity,"status":status,
                            "evidence_sha256":str(i)*64}
                      for i,(name,status) in
                      enumerate(policy.PROOF_STATUSES.items(),1)}
            receipts["chmv_budget"].update({
                "no_double_count":True,"unknown_static_chmv":False})
            internal=ui.public_options(
                path,trusted_internal_receipts_by_id={91001:receipts})
            self.assertEqual(internal["automatic_admission"]["pending"],2)
            self.assertEqual(internal["automatic_admission"][
                "eligible_count_unpublished"],0)
            self.assertEqual(internal["automatic_admission"]["approved_count"],0)
            self.assertFalse(internal["automatic_admission"][
                "v212_install_or_user_selection_authorized"])
            self.assertIn("EXACT_PHYSICAL_SLOT_OR_HAND_RELATION_NOT_VERIFIED",
                internal["automatic_admission"]["per_item_missing_reasons"][
                    "91001"])
            self.assertEqual(internal["enchant_candidates"]["selectable_count"],0)
            self.assertEqual(internal["existing_allowed_input_choices"],{})
            self.assertFalse(internal["environment_ready"])
            # A caller cannot smuggle the internal evidence path into
            # the old installed-season catalog.
            with self.assertRaisesRegex(
                    ui.CatalogBlocked,
                    "LEGACY_SEASON_POLICY_A_INTERNAL_PROOFS_WRONG_PATH"):
                ui.public_options(trusted_internal_receipts_by_id={})

    def test_original_v191_v211_v213_v196_continuous_fresh_chain_without_budget(self):
        import v191_unified_season_data_update as merge
        import v196_current_season_user_catalog as ui
        with tempfile.TemporaryDirectory() as d:
            folder=pathlib.Path(d)
            season_stub,generated_source=fixture_source()
            manifest=put_sources(folder,generated_source)
            gear=copy.deepcopy(SourceToCatalogTests.gear_source)
            gear["season_build"]=BUILD
            tier=copy.deepcopy(SourceToCatalogTests.tier_source)
            tier["retail_build"]=BUILD
            effects={"schema":"v189_pinned_simc_effect_registration_candidates_v1",
                     "auto_promote_to_user_ui":False,
                     "source":{"commit":REV,"sha256":"a"*64},
                     "candidates":{"food":[],"potion":[],
                                   "embellishment_or_darkmoon":[]}}
            consumables={
              "schema":"v190_same_build_consumable_item_candidates_v1",
              "automatic_ui_promotion":False,
              "source":{"wago_snapshot_build":BUILD,"simc_revision":REV,
                        "simc_registration_sha256":"a"*64},
              "items":[{"item_id":8901,"kind":"food"},
                       {"item_id":8902,"kind":"potion"}]}
            candidates=season_stub["enchants"]["current_season"][
                "highest_rank_candidates"]
            generated={
              "permanent_enchant":{
                  "source_build":BUILD,"declared_rows":2,"sha256":"a"*64,
                  "rows":[{"enchant_id":r["enchant_id"],
                           "simc_token":r["simc_token"],
                           "quality_rank":r["quality_rank"],
                           "item_class":r["item_class"],
                           "inventory_type_mask":r["inventory_type_mask"],
                           "item_subclass_mask":r["item_subclass_mask"]}
                          for r in candidates]},
              "temporary_enchant":{"source_build":BUILD,"declared_rows":1,
                                   "sha256":"b"*64,
                                   "rows":[{"enchant_id":999001,"quality_rank":2,
                                            "effect_spell_id":999002,
                                            "simc_token":"oil_test"}]},
              "gem_property":{"source_build":BUILD,"declared_rows":1,
                              "sha256":"c"*64,
                              "rows":[{"gem_property_id":999003,
                                       "enchant_id":999004,
                                       "color_mask":2,"minimum_ilevel":0}]}}
            v191=merge.compile_catalog(gear,tier,None,effects,consumables,
                                       generated,event="season_change")
            # v191.main normally attaches hashes of actual freshly
            # downloaded input bytes; no prior budget file/hash exists here.
            v191["sha256_by_input"]={
                "gear":"1"*64,"tier":"2"*64,"budget":None,
                "v189":"3"*64,"v190":"4"*64}
            self.assertIsNone(v191["consumables"]["flask"]["reference"])
            self.assertIsNone(v191["consumables"]["general_gems"]["reference"])
            self.assertEqual(v191["source_budget_state"],
                             "NEW_SEASON_J_F_EVIDENCE_PENDING")
            v211=classifier.compile_fresh_season(v191,folder,manifest)
            v213=join.compile_catalog(v191,"a"*64,v211,"b"*64)
            self.assertTrue(join.verify_catalog(v213))
            p=folder/"same_build.json"
            p.write_text(json.dumps(v213,ensure_ascii=False),encoding="utf8")
            with patch.object(ui.v188,"labels",side_effect=AssertionError(
                    "PRIOR_APPROVED_LABELS_READ")), patch.object(
                    ui.observed_enchant,"read",side_effect=AssertionError(
                    "PRIOR_NATIVE_E_READ")):
                v196=ui.public_options(p)
        self.assertEqual(v196["enchant_candidates"]["total"],2)
        self.assertEqual(v196["enchant_candidates"]["selectable_count"],0)
        self.assertEqual(v196["automatic_admission"]["pending"],2)
        self.assertEqual(v196["automatic_admission"]["automatically_eligible"],0)
        self.assertFalse(v196["automatic_admission"]["selection_mutated"])
        self.assertFalse(v196["environment_ready"])
        self.assertEqual(v196["existing_allowed_input_choices"],{})
        self.assertEqual(v196["source_catalog"]["summary"]["tier"]["piece_count"],65)
        self.assertEqual(v196["source_catalog"]["summary"]["gear"]["count"],511)
        self.assertEqual(v196["native_calls_now"],0)

    def test_existing_v216_build_preflights_fresh_sources_without_session_writes(self):
        from runner import v216_environment_build_coordinator as build
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            src=root/"simc";src.mkdir()
            season,classified=self.inputs(src)
            # A previously generated fixture has an old known budget source.
            # The fresh Build preflight must reject that historical input.
            legacy=join.compile_catalog(season,"a"*64,classified,"b"*64)
            catalog=root/"fresh_v213.json"
            catalog.write_text(json.dumps(legacy,ensure_ascii=False),
                               encoding="utf8")
            with self.assertRaisesRegex(
                    build.EnvironmentBuildBlocked,
                    "V216_FRESH_NO_HISTORICAL_BUDGET_AND_SOURCE_PROOF_REQUIRED"):
                build.preflight_new_season_source(
                    source_catalog_path=catalog,expected_game_build=BUILD,
                    expected_simc_revision=REV)
            # Real new-season mode carries NULL J/F and NULL budget-file SHA.
            season["sha256_by_input"]["budget"]=None
            season["source_budget_state"]="NEW_SEASON_J_F_EVIDENCE_PENDING"
            season["consumables"]["flask"]["reference"]=None
            season["consumables"]["general_gems"]["reference"]=None
            artifact=join.compile_catalog(season,"a"*64,classified,"b"*64)
            catalog.write_text(json.dumps(artifact,ensure_ascii=False),
                               encoding="utf8")
            receipt=build.preflight_new_season_source(
                source_catalog_path=catalog,expected_game_build=BUILD,
                expected_simc_revision=REV)
            self.assertEqual(receipt["status"],
                "FRESH_SOURCE_CANDIDATES_VALID_GJFO_PENDING_NOT_INSTALLED")
            self.assertEqual(receipt["gear_candidates"],511)
            self.assertEqual(receipt["tier_pieces"],65)
            self.assertEqual(receipt["enchant_candidates"],2)
            self.assertIsNone(receipt["G"])
            self.assertIsNone(receipt["J"])
            self.assertIsNone(receipt["B"])
            self.assertIsNone(receipt["T"])
            self.assertFalse(receipt["environment_ready"])
            self.assertEqual(receipt["cache_mutations"],0)
            session=root/("f"*20);session.mkdir()
            prior_files={p.relative_to(root).as_posix():p.read_bytes()
                         for p in root.rglob("*") if p.is_file()}
            with self.assertRaisesRegex(
                    build.EnvironmentBuildBlocked,
                    "V216_FRESH_SOURCE_PROVENANCE_PASS_GJFO_NOT_READY"):
                build.build_environment(
                    sessions_root=root,session_folder=session,user={
                        "character":{"class":"paladin","spec":"retribution"},
                        "target":{"ilevel":334,"final_T":None}},
                    binary=root/"missing-simc.exe",revision=REV,
                    static_cache=root/"missing-cache.json",
                    source_catalog_path=catalog,bootstrap_result={
                        "schema":"v098"},expected_new_season_build=BUILD)
            # Missing independently requested new season/build is blocked
            # before interpreting the candidate's own self-declared build.
            with self.assertRaisesRegex(
                    build.EnvironmentBuildBlocked,
                    "V216_EXPLICIT_NEW_SEASON_BUILD_REQUIRED"):
                build.build_environment(
                    sessions_root=root,session_folder=session,user={
                        "character":{"class":"paladin","spec":"retribution"},
                        "target":{"ilevel":334,"final_T":None}},
                    binary=root/"missing-simc.exe",revision=REV,
                    static_cache=root/"missing-cache.json",
                    source_catalog_path=catalog,bootstrap_result={
                        "schema":"v098"})
            with self.assertRaisesRegex(
                    build.EnvironmentBuildBlocked,
                    "V216_FRESH_SEASON_BUILD_OR_SIMC_REVISION_MISMATCH"):
                build.build_environment(
                    sessions_root=root,session_folder=session,user={
                        "character":{"class":"paladin","spec":"retribution"},
                        "target":{"ilevel":334,"final_T":None}},
                    binary=root/"missing-simc.exe",revision=REV,
                    static_cache=root/"missing-cache.json",
                    source_catalog_path=catalog,bootstrap_result={
                        "schema":"v098"},
                    expected_new_season_build="12.2.0.88888")
            self.assertFalse((session/"generated").exists())
            self.assertEqual(prior_files,{
                p.relative_to(root).as_posix():p.read_bytes()
                for p in root.rglob("*") if p.is_file()})
            with self.assertRaisesRegex(
                    build.EnvironmentBuildBlocked,"BUILD_OR_SIMC_REVISION_MISMATCH"):
                build.preflight_new_season_source(
                    source_catalog_path=catalog,expected_game_build=BUILD,
                    expected_simc_revision="c"*40)
            modified=json.loads(catalog.read_text(encoding="utf8"))
            modified["catalog"]["gear"]["count"]=510
            catalog.write_text(json.dumps(modified,ensure_ascii=False),
                               encoding="utf8")
            with self.assertRaisesRegex(
                    build.EnvironmentBuildBlocked,"SOURCE_OR_UI_CONTRACT_BLOCKED"):
                build.preflight_new_season_source(
                    source_catalog_path=catalog,expected_game_build=BUILD,
                    expected_simc_revision=REV)


    def test_v216_uses_v217_reusable_fresh_source_stages_before_install(self):
        from runner import v216_environment_build_coordinator as build
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            source=root/"source";source.mkdir()
            workspace=root/"stages";workspace.mkdir()
            session=root/("f"*20);session.mkdir()
            season,_classified=self.inputs(source)
            _fixture,raw_sources=fixture_source()
            source_manifest=put_sources(source,raw_sources)
            season["sha256_by_input"]["budget"]=None
            season["source_budget_state"]="NEW_SEASON_J_F_EVIDENCE_PENDING"
            season["consumables"]["flask"]["reference"]=None
            season["consumables"]["general_gems"]["reference"]=None
            v191=root/"new_v191.json"
            manifest=root/"simc_manifest.json"
            v191.write_text(json.dumps(season),encoding="utf8")
            manifest.write_text(json.dumps(source_manifest),encoding="utf8")
            inputs={"stage_root":workspace,"v191_path":v191,
                    "simc_source_dir":source,"simc_manifest_path":manifest}
            from runner import v241_fresh_source_stage_adapter as adapter
            with patch("v211_enchant_source_effect_classification."
                       "compile_fresh_season",
                       wraps=classifier.compile_fresh_season) as compiled:
                first=adapter.compile_fresh_candidate(
                    **inputs, expected_game_build=BUILD,
                    expected_simc_revision=REV)
                second=adapter.compile_fresh_candidate(
                    **inputs, expected_game_build=BUILD,
                    expected_simc_revision=REV)
            self.assertEqual(compiled.call_count,1)
            self.assertEqual(first["v211_stage"]["status"],"EXECUTED_AND_SEALED")
            self.assertEqual(first["v213_stage"]["status"],"EXECUTED_AND_SEALED")
            self.assertEqual(second["v211_stage"]["status"],"REUSED_VERIFIED")
            self.assertEqual(second["v213_stage"]["status"],"REUSED_VERIFIED")
            self.assertEqual(second["v211_stage"]["receipt_writes"],0)
            self.assertEqual(second["v213_stage"]["receipt_writes"],0)
            self.assertFalse(first["environment_installed"])
            self.assertFalse(first["upstream_fetch_authenticated_by_adapter"])
            before={p.relative_to(root).as_posix():p.read_bytes()
                    for p in root.rglob("*") if p.is_file()}
            with self.assertRaisesRegex(
                    build.EnvironmentBuildBlocked,
                    "V216_FRESH_SOURCE_PROVENANCE_PASS_GJFO_NOT_READY"):
                build.build_environment(
                    sessions_root=root,session_folder=session,user={
                        "character":{"class":"paladin","spec":"retribution"},
                        "target":{"ilevel":334,"final_T":None}},
                    binary=root/"missing-simc",revision=REV,
                    static_cache=None,source_catalog_path=None,
                    bootstrap_result={"schema":"v098"},
                    expected_new_season_build=BUILD,
                    fresh_source_stage_inputs=inputs)
            self.assertFalse((session/"generated").exists())
            self.assertEqual(before,{
                p.relative_to(root).as_posix():p.read_bytes()
                for p in root.rglob("*") if p.is_file()})
            season["source_budget_state"]="OLD_INSTALLED"
            v191.write_text(json.dumps(season),encoding="utf8")
            with self.assertRaisesRegex(
                    ValueError,
                    "FRESH_STAGE_HISTORIC_BUDGET_FORBIDDEN"):
                adapter.compile_fresh_candidate(
                    **inputs,expected_game_build=BUILD,
                    expected_simc_revision=REV)


    def test_fresh_v191_compiles_from_explicit_sources_with_stage_reuse(self):
        from runner import v241_fresh_source_stage_adapter as adapter
        from tests.test_v191_unified_season_data_update import TEMP, GEMS
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            stage_root=root/"stages";stage_root.mkdir()
            simc=root/"simc";simc.mkdir()
            generated=root/"generated";generated.mkdir()
            _stub,raw_sources=fixture_source()
            source_manifest=put_sources(simc,raw_sources)
            body=raw_sources["permanent_enchant.inc"]
            generated_permanent=(
                "// Permanent item enchants, wow build "+BUILD+"\n"
                "static constexpr std::array<permanent_enchant_entry_t, 2> "
                "__permanent_enchant_data { {\n"+
                "\n".join(body.splitlines()[1:])+"\n} };\n")
            (generated/"permanent_enchant.inc").write_text(
                generated_permanent,encoding="utf8")
            (generated/"temporary_enchant.inc").write_bytes(
                TEMP.replace(b"12.1.5.70448",BUILD.encode()))
            (generated/"gem_data.inc").write_bytes(
                GEMS.replace(b"12.1.5.70448",BUILD.encode()))
            gear=copy.deepcopy(SourceToCatalogTests.gear_source)
            gear["season_build"]=BUILD
            tier=copy.deepcopy(SourceToCatalogTests.tier_source)
            tier["retail_build"]=BUILD
            v189={"schema":"v189_pinned_simc_effect_registration_candidates_v1",
                  "auto_promote_to_user_ui":False,
                  "source":{"commit":REV,"sha256":"a"*64},
                  "candidates":{"food":[],"potion":[],
                                "embellishment_or_darkmoon":[]}}
            v190={"schema":"v190_same_build_consumable_item_candidates_v1",
                  "automatic_ui_promotion":False,
                  "source":{"wago_snapshot_build":BUILD,"simc_revision":REV,
                            "simc_registration_sha256":"a"*64},
                  "items":[{"item_id":8901,"kind":"food"},
                           {"item_id":8902,"kind":"potion"}]}
            paths={}
            for name,data in (("gear",gear),("tier",tier),
                              ("v189",v189),("v190",v190)):
                p=root/(name+".json")
                p.write_text(json.dumps(data),encoding="utf8")
                paths[name]=p
            paths["simc_generated_folder"]=generated
            paths["event"]="season_change"
            manifest=root/"manifest.json"
            manifest.write_text(json.dumps(source_manifest),encoding="utf8")
            request={"stage_root":stage_root,
                     "fresh_v191_inputs":paths,
                     "simc_source_dir":simc,"simc_manifest_path":manifest,
                     "expected_game_build":BUILD,"expected_simc_revision":REV}
            first=adapter.compile_fresh_candidate(**request)
            again=adapter.compile_fresh_candidate(**request)
            self.assertEqual(first["v191_stage"]["status"],
                             "EXECUTED_AND_SEALED")
            self.assertEqual(first["v211_stage"]["status"],
                             "EXECUTED_AND_SEALED")
            self.assertEqual(first["v213_stage"]["status"],
                             "EXECUTED_AND_SEALED")
            for name in ("v191_stage","v211_stage","v213_stage"):
                self.assertEqual(again[name]["status"],"REUSED_VERIFIED")
                self.assertEqual(again[name]["receipt_writes"],0)
            season=json.loads((stage_root/"fresh_source"/
                               "v191_candidate.json").read_text())
            self.assertIsNone(season["sha256_by_input"]["budget"])
            self.assertIsNone(season["G"])
            self.assertIsNone(season["consumables"]["general_gems"]["reference"])
            self.assertIsNone(season["consumables"]["flask"]["reference"])
            self.assertFalse(first["environment_installed"])
            self.assertFalse(first["upstream_fetch_authenticated_by_adapter"])
            # P3-DN: ORIGINAL v217-sealed v191/v211/v213 receipts already
            # authenticate the exact source join, not quality/game slots.
            # Reuse that evidence as ONE Policy A family; no new Native.
            from runner import v216_environment_build_coordinator as build
            args={"source_catalog_path":first["source_catalog_path"],
                  "expected_game_build":BUILD,
                  "expected_simc_revision":REV}
            no_stage=build.preflight_new_season_source(**args)
            old=no_stage["optional_policy_A_evidence_unadmitted"]
            self.assertEqual(old["v217_source_relation_receipt_count"],0)
            self.assertEqual(old["pending"],2)
            self.assertTrue(all(
                "EVIDENCE_MISSING:source_relation" in missing
                for missing in old["per_item_missing_reasons"].values()))
            attest={"stage_root":str(stage_root),
                    "v191_stage":first["v191_stage"],
                    "v211_stage":first["v211_stage"],
                    "v213_stage":first["v213_stage"]}
            linked=build.preflight_new_season_source(
                **args,policy_A_v217_stages=attest)
            optional=linked["optional_policy_A_evidence_unadmitted"]
            self.assertEqual(optional["v217_source_relation_receipt_count"],2)
            self.assertEqual(optional["pending"],2)
            self.assertFalse(optional["verified_options_published"])
            self.assertFalse(optional["affects_verified_base_GJFO"])
            self.assertEqual(set(optional["per_item_missing_reasons"]),
                             {"91001","91002"})
            for missing in optional["per_item_missing_reasons"].values():
                self.assertNotIn("EVIDENCE_MISSING:source_relation",missing)
                self.assertTrue({"EVIDENCE_MISSING:simc_input",
                                 "EVIDENCE_MISSING:product_input",
                                 "EVIDENCE_MISSING:chmv_budget"} <= set(missing))
            self.assertIn(
                "EXACT_PHYSICAL_SLOT_OR_HAND_RELATION_NOT_VERIFIED",
                optional["per_item_missing_reasons"]["91001"])
            self.assertFalse(linked["environment_ready"])
            self.assertEqual(linked["approved_new_choices"],0)
            self.assertEqual(linked["native_calls"],0)
            self.assertEqual(linked["network_calls"],0)
            # T1: *one continuous ORIGINAL* v191 -> v211 -> v213
            # -> v216 preflight -> v212 -> v217 environment source unit.
            # The genuine v241 outputs above have original sealed receipts,
            # not caller-supplied fake evidence or a mocked installer.
            staged_input={
                **first,
                "status":"FRESH_V191_V211_V213_COMPILED_UNADMITTED",
                "stage_root":str(stage_root),
                "simc_revision":REV,
                "preflight_sha256":linked["preflight_sha256"],
                "environment_ready":False,
            }
            staged=build._stage_source_environment_only(
                compilation=staged_input,preflight=linked,target_ilevel=334)
            staged_input_reuse={
                **staged_input,
                "v191_stage":again["v191_stage"],
                "v211_stage":again["v211_stage"],
                "v213_stage":again["v213_stage"],
            }
            same_stage=build._stage_source_environment_only(
                compilation=staged_input_reuse,preflight=linked,
                target_ilevel=334)
            self.assertEqual(staged["stage_status"],"EXECUTED_AND_SEALED")
            self.assertEqual(same_stage["stage_status"],"REUSED_VERIFIED")
            self.assertEqual(staged["manifest_sha256"],
                             same_stage["manifest_sha256"])
            with pathlib.Path(staged["stage_output_path"]).open(
                    encoding="utf8") as stream:
                environment=json.load(stream)
            self.assertEqual(environment["schema"],
                             build.environment_manifest.FRESH_SEASON_STAGE_SCHEMA)
            self.assertTrue(build.environment_manifest.
                            verify_fresh_source_environment(environment))
            self.assertEqual(environment["target_ilevel"],334)
            self.assertEqual(environment["game_build"],BUILD)
            self.assertEqual(environment["simc_revision"],REV)
            self.assertEqual(environment["original_v217_stage_receipts"],
                             {name:first[name]["receipt_sha256"]
                              for name in ("v191_stage","v211_stage","v213_stage")})
            self.assertIsNone(environment["numeric_budget_preview_unadmitted"])
            self.assertTrue(environment["optional_policy_A_pending_separate"])
            self.assertFalse(environment["environment_ready"])
            self.assertFalse(environment["environment_installed"])
            self.assertFalse(environment["options_published"])
            self.assertFalse(environment["dps_optimization_required"])
            self.assertEqual(staged["new_native_calls"],0)
            self.assertEqual(staged["network_calls"],0)
            self.assertFalse((root/"generated"/"environment_manifest.json").exists())
            reused=build.preflight_new_season_source(
                **args,policy_A_v217_stages={
                    **attest,"v191_stage":again["v191_stage"],
                    "v211_stage":again["v211_stage"],
                    "v213_stage":again["v213_stage"]})
            self.assertEqual(
                reused["optional_policy_A_evidence_unadmitted"],
                optional)
            bad=copy.deepcopy(attest)
            bad["v213_stage"]={**bad["v213_stage"],
                               "receipt_sha256":"0"*64}
            with self.assertRaisesRegex(
                    build.EnvironmentBuildBlocked,
                    "V216_POLICY_A_V217_SOURCE_OUTPUT_SHA_DRIFT:v213"):
                build.preflight_new_season_source(
                    **args,policy_A_v217_stages=bad)
            missing=build.preflight_new_season_source(
                **args,policy_A_v217_stages={
                    **attest,"v191_stage":None})
            self.assertEqual(missing[
                "optional_policy_A_evidence_unadmitted"][
                "v217_source_relation_receipt_count"],0)
            self.assertFalse((root/"generated"/"manifest.json").exists())

    def test_reject_mismatched_source_and_false_old_enchant_approval(self):
        with tempfile.TemporaryDirectory() as d:
            season,classified=self.inputs(pathlib.Path(d))
            bad=copy.deepcopy(classified)
            bad["counts"]["locked"]=1
            with self.assertRaisesRegex(
                    join.CatalogBlocked,"CLASSIFICATION_COUNTS"):
                join.compile_catalog(season,"a"*64,bad,"b"*64)
            bad=copy.deepcopy(classified)
            bad["rows"][0]["selection_status"]="EXISTING_EAGLE_ONE_SCOPE_USER_CHOICE"
            with self.assertRaisesRegex(
                    join.CatalogBlocked,"CLASSIFICATION_COUNTS"):
                join.compile_catalog(season,"a"*64,bad,"b"*64)
            other=copy.deepcopy(season)
            other["simc_revision"]="f"*40
            with self.assertRaisesRegex(
                    join.CatalogBlocked,"SIMC_REVISION_MISMATCH"):
                join.compile_catalog(other,"a"*64,classified,"b"*64)


if __name__=="__main__":
    unittest.main()
