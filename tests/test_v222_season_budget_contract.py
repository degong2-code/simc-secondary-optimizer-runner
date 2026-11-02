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

    def test_v098_actual_plan_mismatch_blocks_before_publication(self):
        catalog, proof, plan = fixture()
        plan["base_B"] = 3151
        with self.assertRaisesRegex(p.SeasonBudgetBlocked, "V098_PLAN"):
            resolve(catalog, proof, plan)


if __name__ == "__main__":
    unittest.main()
