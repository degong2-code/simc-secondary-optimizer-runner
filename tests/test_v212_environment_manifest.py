import json
import shutil
import tempfile
import unittest
from pathlib import Path

from runner import v046_static_item_cache as item_cache
from runner import v062_static_budget_bridge as budget
from runner import v143_specialization_contracts as specs
from runner import v196_current_season_user_catalog as ui_catalog
from runner import v206_nonchmv_eagle_selection as eagle
from runner import v212_environment_manifest as p
from runner import v213_source_to_catalog as source_bridge
from tests.test_v213_source_to_catalog import SourceToCatalogTests


class EnvironmentManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_builder = SourceToCatalogTests()
        cls.source_builder.setUpClass()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        season, classification = self.source_builder.build_inputs()
        self.source_catalog = source_bridge.compile_catalog(
            season, "a" * 64, classification, "b" * 64)
        self.source_path = self.root / "v213_source_to_catalog.json"
        self.source_path.write_text(
            json.dumps(self.source_catalog, ensure_ascii=False,
                       sort_keys=True, indent=2) + "\n", encoding="utf8")
        self.source_catalog_sha = p.sha(self.source_path.read_bytes())
        self.ui = ui_catalog.public_options(self.source_path)
        self.ui_sha = p.sha(p.canonical(self.ui).encode("utf8"))
        self.binary = self.root / "simc_not_executed.bin"
        self.binary.write_bytes(b"SIMC_TEST_BINARY_NEVER_EXECUTED")
        self.target = self.root / "target"
        self.target.mkdir()
        self.selected = {
            "schema": eagle.SCHEMA,
            "choice": dict(eagle.CHOICE),
            "effect_family": "crit_effectiveness",
            "static_CHMV_E": dict(eagle.E_ZERO),
            "budget_policy":
                "NON_CHMV_NO_CHANGE_TO_REFERENCE_B_OR_FINAL_T",
            "native_static_scope":
                "ONE_WINDOWS_PALADIN334_STATIC_E_ZERO_NOT_ALL_DPS",
            "mechanics_owner": "SimC",
        }
        target_manifest = {
            "profile_simc": "profile.simc",
            "scenario_json": "scenario.json",
            "fillers_json": "fillers.json",
            "native_binary": str(self.binary),
            "native_revision": self.source_catalog["simc_revision"],
            "native_limit": 6,
            "weapon_layout": "one_hand_frill",
            "oil_hands": ["main_hand"],
            "flask_F": 165,
            "seed_targets_B": [
                {"crit_rating": 700, "haste_rating": 800,
                 "mastery_rating": 900, "versatility_rating": 750},
                {"crit_rating": 900, "haste_rating": 700,
                 "mastery_rating": 800, "versatility_rating": 750},
            ],
            "static_cache_json": None,
        }
        (self.target / "manifest.json").write_text(
            json.dumps(target_manifest), encoding="utf8")
        (self.target / "profile.simc").write_text(
            "spec=retribution\n"
            "finger1=selected_ring,id=240111,ilevel=334,enchant_id=7967\n",
            encoding="utf8")
        (self.target / "scenario.json").write_text(
            json.dumps({"equipment": {"special": []},
                        "character": {"class": "paladin",
                                      "spec": "retribution"},
                        "target": {"ilevel": 334}}),
            encoding="utf8")
        (self.target / "fillers.json").write_text("[]\n", encoding="utf8")
        self.bootstrap = {
            "schema": p.V098,
            "native_calls": 0,
            "status": "READY_INTERNAL_MANIFEST_ZERO_NATIVE",
            "current_season_product": True,
            "all_specs_ready": False,
            "supported_archetypes_now": 24,
            "template_archetype": "paladin/retribution",
            "target_ilevel": 334,
            "generated_manifest": str(self.target / "manifest.json"),
            "plan": {
                "class": "paladin", "spec": "retribution",
                "base_B": 3150, "final_T": 3182, "item_slots": 15,
                "fixed_O": {"crit_rating": 16, "haste_rating": 16,
                            "mastery_rating": 0, "versatility_rating": 0},
                "budget_source": "REFERENCE_B_PLUS_FIXED_O",
                "scenario_digest": "c" * 64,
                "source_profile_sha256": "d" * 64,
            },
            "selected_nonchmv_enchant": self.selected,
        }
        v191_hashes=self.source_catalog["source_provenance"]["v191"]["sha256_by_input"]
        self.bootstrap["profile_supplier_coverage"]={
            "schema":"v215_profile_supplier_coverage_v1",
            "status":"CURRENT_SEASON_PLAN_SUPPLIERS_26_OF_26",
            "supported_specializations":sorted(p.specs.CONTRACTS),
            "contract_count":26,"legacy_source_backed_count":24,
            "source_independent_count":2,"user_input_default_count":26,
            "starter_default_count":26,"season_catalog_count":26,
            "current_season_profile_supplier_count":26,
            "selected_specialization":"paladin/retribution",
            "selected_specialization_plan_supplier":True,
            "season_build":self.source_catalog["game_build"],
            "source_input_sha256":{k:v191_hashes[k]
                                   for k in ("gear","tier","budget")},
            "supplier_code_sha256":{
                "contracts":"c"*64,"profile_composer":"d"*64,
                "user_session":"e"*64,"season_stage":"f"*64},
            "all_specs_ready":False,
            "adaptive_native_evidence_complete":False,
            "native_calls":0,"network_calls":0,
        }

    def compile(self, receipt=None, previous=None):
        return p.compile_manifest(
            self.source_catalog, self.source_catalog_sha,
            self.ui, self.ui_sha, self.bootstrap, self.target, receipt,
            previous_environment_manifest=previous)

    def make_windows_package_manifest(self):
        package_root=self.root/"SIMC_SECONDARY_OPTIMIZER_WINDOWS_BETA"
        data=package_root/"data"
        data.mkdir(parents=True,exist_ok=True)
        source_path=data/"current_season_source_to_catalog.json"
        raw=self.source_path.read_bytes()
        source_path.write_bytes(raw)
        source_meta={
            "path":"data/current_season_source_to_catalog.json",
            "schema":self.source_catalog["schema"],
            "game_build":self.source_catalog["game_build"],
            "simc_revision":self.source_catalog["simc_revision"],
            "artifact_sha256":p.sha(raw),
            "manifest_sha256":self.source_catalog["manifest_sha256"],
            "native_calls":0,"network_calls":0,
            "automatic_ui_promotion":False,
        }
        package={
            "schema":p.WINDOWS_PACKAGE_SCHEMA,
            "archive_root":package_root.name,
            "files":[{"path":source_meta["path"],"size":len(raw),
                      "sha256":p.sha(raw)}],
            "file_count":1,
            "source_catalog":source_meta,
        }
        package_path=package_root/"V181_PACKAGE_MANIFEST.json"
        package_path.write_text(json.dumps(package,sort_keys=True,
            ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        return source_path,package_path

    def add_selected_special(self):
        row={"slot":"back","item_id":159288,"ilevel":334,"options":{}}
        scenario={
            "equipment":{"special":[row]},
            "character":{"class":"paladin","spec":"retribution"},
            "target":{"ilevel":334},
        }
        (self.target/"scenario.json").write_text(
            json.dumps(scenario),encoding="utf8")
        cache_path=self.root/"selected-static-cache.json"
        cache=item_cache.empty_cache()
        identity=budget.exact_identity(budget.undecorated_special(row))
        static={
            "secondary":{"crit_rating":0,"haste_rating":175,
                         "mastery_rating":0,"versatility_rating":0},
            "primary_other":{"strength":0,"agility":0,"intellect":0,
                             "stragiint":0,"stamina":0,"armor":0},
            "weapon_if_native":{},
        }
        record={
            "identity":identity,"static":static,
            "static_digest":item_cache.digest(static),
            "source_kind":"NATIVE_JSON2_RESOLVED_VARIANT",
            "item_name_observed":"Test Special",
            "observed_slot":"back","modifiers_present":False,
            "bare_item_stats_independently_attested":False,
            "metadata":{
                "native_revision":self.source_catalog["simc_revision"][:10],
                "native_json_sha256":"d"*64,
                "artifact":"V208_USER_LOCAL_EXACT_STATIC_L",
                "item_db_source":"test-fixture",
            },
            "not_user_selection":True,
            "dynamic_effect_values_cached":False,
            "eligible_for_gear_sum_only_in_exact_same_variant":True,
        }
        cache["variants"][item_cache.digest(identity)]=record
        item_cache.write_atomic(cache_path,cache)
        target_manifest=json.loads(
            (self.target/"manifest.json").read_text("utf8"))
        target_manifest["static_cache_json"]=str(cache_path)
        (self.target/"manifest.json").write_text(
            json.dumps(target_manifest),encoding="utf8")
        return row,cache_path,record

    def make_v208_receipt(self,row,cache_path,record):
        selected_identity=budget.exact_identity(row)
        bare_identity=budget.exact_identity(budget.undecorated_special(row))
        raw=cache_path.read_bytes()
        payload={
            "schema":"v208_selected_special_start_receipt_v1",
            "status":"VERIFIED",
            "source_catalog":{
                "schema":self.source_catalog["schema"],
                "artifact_sha256":self.source_catalog_sha,
                "manifest_sha256":self.source_catalog["manifest_sha256"],
                "game_build":self.source_catalog["game_build"],
                "simc_revision":self.source_catalog["simc_revision"],
            },
            "simc":{
                "revision":self.source_catalog["simc_revision"],
                "binary_sha256":p.sha(self.binary.read_bytes()),
            },
            "static_cache":{
                "basename":cache_path.name,"size_bytes":len(raw),
                "sha256":p.sha(raw),
            },
            "selected_special_count":1,
            "selected_specials":[{
                "selected_identity":selected_identity,
                "selected_identity_sha256":item_cache.digest(selected_identity),
                "bare_identity":bare_identity,
                "bare_identity_sha256":item_cache.digest(bare_identity),
                "cache_status":"HIT",
                "source_kind":"NATIVE_JSON2_RESOLVED_VARIANT",
                "static_digest":record["static_digest"],
                "measured_L":record["static"]["secondary"],
                "native_json2":{
                    "sha256":"d"*64,
                    "revision":self.source_catalog["simc_revision"][:10],
                    "source":"V208_USER_LOCAL_EXACT_STATIC_L",
                },
            }],
            "cache_summary":{"hits":1,"misses":0,
                             "native_calls_this_start":0},
            "native_calls_this_start":0,
            "native_json2_sha256s":["d"*64],
        }
        payload["receipt_sha256"]=p.sha(p.canonical(payload).encode("utf8"))
        return payload

    def test_v213_real_source_contract_and_exact_7967_approval(self):
        result = self.compile()
        self.assertTrue(source_bridge.verify_catalog(self.source_catalog))
        self.assertEqual(result["schema"], p.SCHEMA)
        self.assertEqual(result["status"], "READY_WITH_LIMITATIONS")
        self.assertEqual(result["native_calls"], 0)
        self.assertEqual(result["network_calls"], 0)
        self.assertEqual(result["source_catalog"]["artifact_sha256"],
                         self.source_catalog_sha)
        self.assertEqual(result["source_catalog"]["manifest_sha256"],
                         self.source_catalog["manifest_sha256"])
        self.assertEqual(result["approved_ui_catalog"]["selectable_enchant_ids"],
                         [7967])
        self.assertEqual(result["approved_ui_catalog"]["developer_only_enchant_ids"],
                         [8025])
        self.assertEqual(result["selected_nonchmv_enchant"]["selected_id"], 7967)
        self.assertEqual(result["selected_nonchmv_enchant"]["budget_increment"], 0)
        self.assertEqual(result["target_profile"]["base_B"], 3150)
        self.assertEqual(result["target_profile"]["final_T"], 3182)
        self.assertIn("ALL_26_ADAPTIVE_PROFILE_NATIVE_ACCEPTANCE",
                      result["unresolved_dependencies"])
        self.assertEqual(
            result["product_scope"]["profile_supplier_coverage"]
                ["current_season_profile_supplier_count"],26)
        self.assertEqual(result["v208_start_receipt"]["status"],
                         "NOT_REQUIRED_NO_SELECTED_SPECIAL")
        self.assertNotIn(
            "V208_SELECTED_SPECIAL_L_START_RECEIPT_NOT_YET_SERIALIZED_IN_ENVIRONMENT_MANIFEST",
            result["unresolved_dependencies"])

    def test_profile_supplier_source_hash_mismatch_blocks(self):
        self.bootstrap["profile_supplier_coverage"]["source_input_sha256"]["gear"]="0"*64
        with self.assertRaisesRegex(p.EnvironmentBlocked,
                                    "V098_PROFILE_SUPPLIER_SOURCE_INPUT_SHA_MISMATCH"):
            self.compile()

    def test_dependency_change_from_v208_receipt_preserves_static_cache(self):
        row,cache_path,record=self.add_selected_special()
        initial=self.compile()
        receipt=self.make_v208_receipt(row,cache_path,record)
        updated=self.compile(receipt,initial)
        change=updated["dependency_change"]
        self.assertEqual(change["status"],"DEPENDENCIES_CHANGED")
        self.assertEqual(change["changed_inputs"],["v208_start_receipt"])
        self.assertEqual(change["invalidated_components"],["environment_manifest"])
        self.assertTrue(change["static_item_cache_preserved"])
        self.assertTrue(change["historical_sessions_preserved"])
        self.assertEqual(change["cache_mutations"],0)
        self.assertEqual(change["native_calls"],0)

    def test_dependency_graph_same_inputs_and_source_change(self):
        first=self.compile()
        unchanged=p.compare_dependency_graphs(first,first["dependency_graph"])
        self.assertEqual(unchanged["status"],"UNCHANGED")
        changed_graph=dict(first["dependency_graph"])
        changed_graph["fingerprints"]=dict(first["dependency_graph"]["fingerprints"])
        changed_graph["fingerprints"]["v213_source_catalog"]="9"*64
        diff=p.compare_dependency_graphs(first,changed_graph)
        self.assertIn("v213_source_catalog",diff["changed_inputs"])
        self.assertIn("v098_profile",diff["invalidated_components"])
        self.assertIn("session_identity",diff["invalidated_components"])
        self.assertTrue(diff["static_item_cache_preserved"])
        self.assertEqual(diff["cache_mutations"],0)

    def test_same_inputs_produce_byte_stable_manifest(self):
        first = self.compile()
        second = self.compile()
        self.assertEqual(p.canonical(first), p.canonical(second))
        self.assertEqual(first["manifest_sha256"], second["manifest_sha256"])

    def test_same_profile_at_different_local_root_has_same_environment_digest(self):
        first = self.compile()
        other = self.root / "relocated-target"
        shutil.copytree(self.target, other)
        moved_bootstrap = dict(self.bootstrap)
        moved_bootstrap["generated_manifest"] = str(other / "manifest.json")
        moved = p.compile_manifest(
            self.source_catalog, self.source_catalog_sha,
            self.ui, self.ui_sha, moved_bootstrap, other)
        self.assertEqual(first["manifest_sha256"], moved["manifest_sha256"])

    def test_build_or_revision_mismatch_fails_closed(self):
        self.ui["season_build"] = "12.1.5.70576"
        with self.assertRaisesRegex(p.EnvironmentBlocked,
                                    "BUILD_OR_REVISION_MISMATCH"):
            self.compile()
        self.ui["season_build"] = self.source_catalog["game_build"]
        self.ui["simc_revision"] = "c" * 40
        with self.assertRaisesRegex(p.EnvironmentBlocked,
                                    "BUILD_OR_REVISION_MISMATCH"):
            self.compile()

    def test_wrong_or_expanded_approved_id_fails_closed(self):
        items = self.ui["enchant_candidates"]["items"]
        next(x for x in items if x["enchant_id"] == 7967)["ui_selectable"] = False
        next(x for x in items if x["enchant_id"] == 8025)["ui_selectable"] = True
        self.ui["enchant_candidates"]["selectable_count"] = 1
        with self.assertRaisesRegex(p.EnvironmentBlocked,
                                    "EXACT_APPROVED_ENCHANT_ID_MISMATCH"):
            self.compile()

    def test_bootstrap_cannot_select_developer_only_or_other_enchant(self):
        self.bootstrap["selected_nonchmv_enchant"] = {
            **self.selected, "choice": {"finger1": 8025}}
        with self.assertRaisesRegex(p.EnvironmentBlocked,
                                    "SELECTED_ENCHANT_NOT_EXACT_EXISTING_APPROVAL"):
            self.compile()

    def test_v213_digest_or_artifact_sha_mismatch_fails_closed(self):
        self.source_catalog["manifest_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError,
                                    "V213_CATALOG_DIGEST_MISMATCH"):
            self.compile()
        self.source_catalog["manifest_sha256"] = p.sha(
            p.canonical({k: v for k, v in self.source_catalog.items()
                         if k != "manifest_sha256"}).encode("utf8"))
        with self.assertRaisesRegex(p.EnvironmentBlocked,
                                    "ARTIFACT_FILE_SHA256_INVALID"):
            p.compile_manifest(self.source_catalog, "not-a-sha",
                               self.ui, self.ui_sha,
                               self.bootstrap, self.target)

    def test_profile_change_changes_environment_identity(self):
        first = self.compile()
        with (self.target / "profile.simc").open("a", encoding="utf8") as stream:
            stream.write("desired_targets=2\n")
        second = self.compile()
        self.assertNotEqual(first["manifest_sha256"], second["manifest_sha256"])

    def test_selected_special_requires_bound_static_cache_snapshot(self):
        scenario = {
            "equipment": {"special": [{
                "slot": "back", "item_id": 159288, "ilevel": 331,
                "options": {},
            }]},
            "character": {"class": "shaman", "spec": "elemental"},
            "target": {"ilevel": 331},
        }
        (self.target / "scenario.json").write_text(
            json.dumps(scenario), encoding="utf8")
        with self.assertRaisesRegex(p.EnvironmentBlocked,
                                    "SELECTED_SPECIAL_STATIC_L_CACHE_SNAPSHOT_MISSING"):
            self.compile()

    def test_selected_special_without_v208_receipt_remains_unresolved(self):
        self.add_selected_special()
        result=self.compile()
        self.assertEqual(result["v208_start_receipt"]["status"],"NOT_PROVIDED")
        self.assertIn(
            "V208_SELECTED_SPECIAL_L_START_RECEIPT_NOT_YET_SERIALIZED_IN_ENVIRONMENT_MANIFEST",
            result["unresolved_dependencies"])

    def test_exact_v208_start_receipt_is_bound_into_environment_manifest(self):
        row,cache_path,record=self.add_selected_special()
        receipt=self.make_v208_receipt(row,cache_path,record)
        result=self.compile(receipt)
        self.assertEqual(result["v208_start_receipt"]["status"],"VERIFIED")
        self.assertEqual(result["v208_start_receipt"]["receipt_sha256"],
                         receipt["receipt_sha256"])
        self.assertEqual(result["v208_start_receipt"]["cache_hits"],1)
        self.assertEqual(result["v208_start_receipt"]["cache_misses"],0)
        self.assertEqual(result["v208_start_receipt"]["native_calls_this_start"],0)
        self.assertNotIn(
            "V208_SELECTED_SPECIAL_L_START_RECEIPT_NOT_YET_SERIALIZED_IN_ENVIRONMENT_MANIFEST",
            result["unresolved_dependencies"])

    def test_v208_receipt_selected_identity_tamper_fails_closed(self):
        row,cache_path,record=self.add_selected_special()
        receipt=self.make_v208_receipt(row,cache_path,record)
        receipt["selected_specials"][0]["selected_identity"]["item_id"]=159289
        receipt["receipt_sha256"]=p.sha(p.canonical(
            {k:v for k,v in receipt.items() if k!="receipt_sha256"}).encode("utf8"))
        with self.assertRaisesRegex(p.EnvironmentBlocked,
                                    "V208_RECEIPT_SELECTED_SPECIAL_IDENTITY_MISMATCH"):
            self.compile(receipt)

    def test_augmentation_and_non_dps_contracts_are_not_accepted(self):
        self.bootstrap["template_archetype"] = "evoker/augmentation"
        with self.assertRaisesRegex(p.EnvironmentBlocked,
                                    "PRODUCT_DPS_26_SPECIALIZATION_CONTRACT_DRIFT"):
            self.compile()
        self.assertEqual(len(specs.CONTRACTS), 26)
        self.assertNotIn("evoker/augmentation", specs.CONTRACTS)

    def test_native_or_ui_promotion_in_source_artifact_fails_closed(self):
        self.source_catalog["native_calls"] = 1
        self.source_catalog["manifest_sha256"] = p.sha(
            p.canonical({k: v for k, v in self.source_catalog.items()
                         if k != "manifest_sha256"}).encode("utf8"))
        with self.assertRaisesRegex(ValueError,
                                    "V213_CATALOG_CONTRACT_INVALID"):
            self.compile()


    def test_windows_package_manifest_binds_exact_v213_source_file(self):
        source_path,package_path=self.make_windows_package_manifest()
        identity=p.verify_windows_package_manifest(
            package_path,source_path,self.source_catalog,self.source_catalog_sha)
        self.assertEqual(identity["status"],"VERIFIED")
        self.assertEqual(identity["source_catalog_sha256"],self.source_catalog_sha)
        self.assertEqual(identity["file_count"],1)

    def test_windows_package_source_bytes_tamper_fails_closed(self):
        source_path,package_path=self.make_windows_package_manifest()
        raw=source_path.read_bytes()
        source_path.write_bytes(raw[:-1]+(b" " if raw[-1:]!=b" " else b"\\t"))
        with self.assertRaisesRegex(p.EnvironmentBlocked,
                                    "WINDOWS_PACKAGE_SOURCE_CATALOG_BYTES_CHANGED"):
            p.verify_windows_package_manifest(
                package_path,source_path,self.source_catalog,self.source_catalog_sha)

    def test_compile_from_paths_marks_verified_default_windows_package(self):
        source_path,package_path=self.make_windows_package_manifest()
        bootstrap_path=self.root/"v098_bootstrap_result.json"
        bootstrap_path.write_text(json.dumps(self.bootstrap),encoding="utf8")
        result=p.compile_from_paths(
            source_path,bootstrap_path,self.target,
            package_manifest_path=package_path)
        self.assertEqual(result["windows_package"]["status"],"VERIFIED")
        self.assertEqual(result["windows_package"]["source_catalog_sha256"],
                         self.source_catalog_sha)
        self.assertNotIn("V213_WINDOWS_PACKAGE_MANIFEST_NOT_VERIFIED",
                         result["readiness_limitations"])
        self.assertNotIn("V213_WINDOWS_PACKAGE_MANIFEST_NOT_VERIFIED",
                         result["unresolved_dependencies"])
        self.assertIn(
            "WINDOWS_ONE_CLICK_ENVIRONMENT_BUILD_AND_START_NOT_INTEGRATED",
            result["unresolved_dependencies"])


if __name__ == "__main__":
    unittest.main()
