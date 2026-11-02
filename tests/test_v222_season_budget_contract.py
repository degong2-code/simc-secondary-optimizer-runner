import copy
import unittest

from runner import v222_season_budget_contract as p


def fixture():
    build = "12.1.5.70575"
    catalog = {
        "game_build": build, "simc_revision": "c" * 40,
        "manifest_sha256": "b" * 64,
    }
    def component(rating, digest):
        return {
            "rating": rating, "game_build": build,
            "source_catalog_manifest_sha256": "b" * 64,
            "source_sha256": digest * 64,
            "source_verification": "VALID_SAME_SEASON_REFERENCE",
        }
    oil = {"crit_rating": 16, "haste_rating": 16,
           "mastery_rating": 0, "versatility_rating": 0}
    zero = {key: 0 for key in p.STATS}
    e = {
        "schema": p.SCHEMA, "game_build": build, "simc_revision": "c" * 40,
        "source_catalog_manifest_sha256": "b" * 64,
        "source_catalog_artifact_sha256": "a" * 64,
        "target_ilevel": 334,
        "components": {
            "G": component(2847, "1"),
            "J": component(138, "2"),
            "F": component(165, "3"),
            "O": component(oil, "4"),
        },
        "fixed_L": dict(zero), "fixed_E": dict(zero),
        "G_reference_excludes_selected_E": True,
    }
    e["components"]["O"]["applied_hands"] = ["main_hand"]
    e["components"]["O"]["weapon_applicability_verified"] = True
    plan = {"base_B": 3150, "final_T": 3182, "fixed_O": oil}
    return catalog, e, plan


def resolve(catalog, evidence, plan, manual=None):
    return p.reconcile(
        source_catalog=catalog, source_artifact_sha256="a" * 64,
        evidence=evidence, plan=plan, target_ilevel=334,
        manual_final_T=manual,
    )


class SeasonBudgetContractTests(unittest.TestCase):
    def test_preprofile_budget_does_not_require_a_v098_plan(self):
        catalog, proof, plan = fixture()
        result = p.preprofile_budget(
            source_catalog=catalog,
            source_artifact_sha256="a" * 64,
            evidence=proof, target_ilevel=334)
        self.assertEqual(result["base_B"], 3150)
        self.assertEqual(result["final_T"], 3182)
        self.assertEqual(result, resolve(catalog, proof, plan))
        self.assertFalse(result["source_authentication_performed_here"])
        self.assertEqual((result["network_calls"], result["native_calls"],
                          result["cache_mutations"]), (0, 0, 0))
        self.assertNotIn("READY", result["status"])

    def test_preprofile_manual_T_and_oil_exactly_once(self):
        catalog, proof, _ = fixture()
        result = p.preprofile_budget(
            source_catalog=catalog,
            source_artifact_sha256="a" * 64,
            evidence=proof, target_ilevel=334, manual_final_T=3270)
        self.assertEqual((result["reference_B"], result["base_B"],
                          result["final_T"]), (3150, 3238, 3270))
        self.assertTrue(result["manual_final_T_authoritative"])

    def test_preprofile_rejects_missing_and_foreign_season_proofs(self):
        catalog, proof, _ = fixture()
        del proof["components"]["J"]
        with self.assertRaisesRegex(p.SeasonBudgetBlocked, "ALL_FOUR"):
            p.preprofile_budget(
                source_catalog=catalog, source_artifact_sha256="a" * 64,
                evidence=proof, target_ilevel=334)
        catalog, proof, _ = fixture()
        proof["components"]["G"]["game_build"] = "12.2.0.1"
        with self.assertRaisesRegex(p.SeasonBudgetBlocked, "SAME_BUILD"):
            p.preprofile_budget(
                source_catalog=catalog, source_artifact_sha256="a" * 64,
                evidence=proof, target_ilevel=334)

    def test_fresh_source_preflight_retains_unadmitted_budget_barrier(self):
        from unittest import mock
        from runner import v216_environment_build_coordinator as build
        catalog, proof, _ = fixture()
        catalog = {
            **catalog, "schema": "fresh-fixture",
            "source_provenance": {
                "v191": {"sha256_by_input": {"budget": None}}},
            "enchant_classification": {
                "source_manifest_sha256": "d" * 64},
            "catalog": {"consumables": {
                "flask": {"reference": None},
                "general_gems": {"reference": None}},
                "gear": {"count": 13}, "tier": {"piece_count": 5}},
        }
        ui = {
            "season_build": catalog["game_build"],
            "simc_revision": catalog["simc_revision"],
            "status": "FRESH_SEASON_CANDIDATES_UNAPPROVED_NOT_ENVIRONMENT_READY",
            "enchant_candidates": {"selectable_count": 0, "total": 0},
            "existing_allowed_input_choices": {}, "environment_ready": False,
            "G": None, "J": None, "F": None, "O": None, "B": None, "T": None,
            "native_calls_now": 0, "game_db_recollection_now": 0,
            "optimizer_or_cache_mutated": False,
        }
        with mock.patch.object(build.environment_manifest, "read_json",
                               return_value=(catalog, "a" * 64)), \
             mock.patch.object(build.source_to_catalog, "verify_catalog"), \
             mock.patch.object(build.user_catalog, "public_options",
                               return_value=ui), \
             mock.patch.object(build.pathlib.Path, "is_file",
                               return_value=True), \
             mock.patch.object(build.pathlib.Path, "is_symlink",
                               return_value=False):
            preview = build.preflight_new_season_source(
                source_catalog_path="candidate.json",
                expected_game_build=catalog["game_build"],
                expected_simc_revision=catalog["simc_revision"],
                budget_evidence=proof, target_ilevel=334)
        self.assertEqual(preview["status"],
                         "FRESH_SOURCE_CANDIDATES_VALID_GJFO_PENDING_NOT_INSTALLED")
        self.assertEqual(preview["G"], None)
        self.assertFalse(preview["environment_ready"])
        self.assertEqual(preview["proposed_budget_arithmetic_unadmitted"][
            "final_T"], 3182)
        self.assertIn("INDEPENDENT_GJFO_SOURCE_ORIGIN_AND_RATING_AUTHENTICATION",
                      preview["requires"])

    def test_current_season_reconciles_without_native_or_ready_claim(self):
        catalog, proof, plan = fixture()
        result = resolve(catalog, proof, plan)
        self.assertEqual((result["reference_G"], result["reference_B"],
                          result["base_B"], result["final_T"]),
                         (2847, 3150, 3150, 3182))
        self.assertFalse(result["source_authentication_performed_here"])
        self.assertEqual(result["native_calls"], 0)

    def test_manual_final_T_overrides_reference_without_double_O(self):
        catalog, proof, plan = fixture()
        plan.update(base_B=3238, final_T=3270)
        result = resolve(catalog, proof, plan, manual=3270)
        self.assertEqual(result["reference_B"], 3150)
        self.assertEqual(result["base_B"], 3238)
        self.assertTrue(result["manual_final_T_authoritative"])

    def test_one_time_static_E_on_enchant_free_reference(self):
        catalog, proof, plan = fixture()
        proof["fixed_E"]["haste_rating"] = 30
        plan.update(base_B=3180, final_T=3212)
        result = resolve(catalog, proof, plan)
        self.assertEqual((result["effective_G"], result["final_T"]),
                         (2877, 3212))

    def test_reference_already_includes_E_never_adds_again(self):
        catalog, proof, plan = fixture()
        proof["components"]["G"]["rating"] = 2877
        proof["fixed_E"]["haste_rating"] = 30
        proof["G_reference_excludes_selected_E"] = False
        plan.update(base_B=3180, final_T=3212)
        self.assertEqual(resolve(catalog, proof, plan)["final_T"], 3212)

    def test_missing_G_or_stale_build_fails_closed(self):
        catalog, proof, plan = fixture()
        del proof["components"]["G"]
        with self.assertRaisesRegex(p.SeasonBudgetBlocked, "ALL_FOUR"):
            resolve(catalog, proof, plan)
        catalog, proof, plan = fixture()
        proof["components"]["F"]["game_build"] = "12.2.0.1"
        with self.assertRaisesRegex(p.SeasonBudgetBlocked, "SAME_BUILD"):
            resolve(catalog, proof, plan)

    def test_manual_T_below_L_E_J_F_is_rejected(self):
        catalog, proof, plan = fixture()
        proof["fixed_L"]["mastery_rating"] = 2700
        plan.update(base_B=300, final_T=332)
        with self.assertRaisesRegex(p.SeasonBudgetBlocked, "FIXED_MINIMA"):
            resolve(catalog, proof, plan, manual=332)

    def test_oil_hands_and_eligibility_are_not_inferred(self):
        catalog, proof, plan = fixture()
        proof["components"]["O"]["weapon_applicability_verified"] = False
        with self.assertRaisesRegex(p.SeasonBudgetBlocked, "APPLICABILITY"):
            resolve(catalog, proof, plan)
        catalog, proof, plan = fixture()
        proof["components"]["O"]["applied_hands"] = []
        with self.assertRaisesRegex(p.SeasonBudgetBlocked, "UNSELECTED"):
            resolve(catalog, proof, plan)

    def test_no_oil_and_two_weapons_are_distinct(self):
        catalog, proof, plan = fixture()
        zero = {k: 0 for k in p.STATS}
        proof["components"]["O"]["rating"] = zero
        proof["components"]["O"]["applied_hands"] = []
        plan.update(fixed_O=zero, final_T=3150)
        self.assertEqual(resolve(catalog, proof, plan)["final_T"], 3150)
        catalog, proof, plan = fixture()
        proof["components"]["O"]["rating"] = {
            "crit_rating": 32, "haste_rating": 32,
            "mastery_rating": 0, "versatility_rating": 0}
        proof["components"]["O"]["applied_hands"] = [
            "main_hand", "off_hand"]
        plan.update(fixed_O=proof["components"]["O"]["rating"], final_T=3214)
        self.assertEqual(resolve(catalog, proof, plan)["final_T"], 3214)

    def test_v216_installed_build_reconciles_internal_proof_without_native(self):
        import json
        import pathlib
        import tempfile
        from unittest import mock
        from runner import v216_environment_build_coordinator as build
        from tests.test_v216_environment_build_coordinator import sealed_manifest
        catalog, proof, plan = fixture()
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            source_path = root / "v213_source.json"
            source_path.write_text(json.dumps(catalog), encoding="utf8")
            proof["source_catalog_artifact_sha256"] = build.digest(
                source_path.read_bytes())
            session = root / ("3" * 20)
            session.mkdir()
            bootstrap = {"schema": "v098", "target_ilevel": 334,
                         "plan": plan}
            with mock.patch.object(
                    build.environment_manifest, "compile_from_paths",
                    return_value=sealed_manifest()):
                result = build.build_environment(
                    sessions_root=root, session_folder=session,
                    user={"target": {"final_T": None}},
                    binary=root / "unused_simc", revision="c" * 40,
                    static_cache=None, source_catalog_path=source_path,
                    bootstrap_result=bootstrap, season_budget_evidence=proof)
                self.assertEqual(
                    result["receipt"]["season_budget"]["base_B"], 3150)
                self.assertFalse(
                    result["receipt"]["season_budget"][
                        "source_authentication_performed_here"])
                self.assertIn(
                    "SEASON_GJFO_AUTO_REFRESH_NOT_VERIFIED",
                    result["receipt"]["readiness"]["limitations"])
                proof["components"]["J"]["rating"] = 139
                with self.assertRaisesRegex(
                        build.EnvironmentBuildBlocked,
                        "V216_SEASON_BUDGET_PROOF_OR_ARITHMETIC_BLOCKED"):
                    build.build_environment(
                        sessions_root=root, session_folder=session,
                        user={"target": {"final_T": None}},
                        binary=root / "unused_simc", revision="c" * 40,
                        static_cache=None, source_catalog_path=source_path,
                        bootstrap_result=bootstrap,
                        season_budget_evidence=proof)

    def test_v098_actual_plan_mismatch_blocks_before_publication(self):
        catalog, proof, plan = fixture()
        plan["base_B"] = 3151
        with self.assertRaisesRegex(p.SeasonBudgetBlocked, "V098_PLAN"):
            resolve(catalog, proof, plan)


if __name__ == "__main__":
    unittest.main()
