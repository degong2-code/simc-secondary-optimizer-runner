"""Offline v042 boundary tests: never convert diagnostic evidence into product policy."""
import copy
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runner"))
import v042_catalyst_evidence_firewall as v
import v041_catalyst_gem_proc_probe as prior


def fixture():
    return {
        "report_version": "2.0.0",
        "git_revision": "7bc10711b5",
        "sim": {
            "players": [{
                "gear": {
                    "head": {
                        "encoded_item": prior.HEAD.split("=", 1)[1],
                        "mastery_rating": 201,
                        "crit_rating": 0,
                        "haste_rating": 0,
                        "versatility_rating": 0,
                    },
                    "hands": {"encoded_item": "hands,id=268243"},
                },
                "buffs": [
                    {"name": "cumulative_power"},
                    {"name": "rune_of_critical_power"},
                    {"name": "venomcursed_mastery", "spell": 1307922,
                     "start_count": 7, "uptime": 40.5},
                ],
                "collected_data": {"dps": {"count": 59}}
            }]
        }
    }


def blob(doc):
    return json.dumps(doc).encode("utf-8")


class V042Boundary(unittest.TestCase):
    def test_bounded_native_identity_stays_diagnostic(self):
        proof = v.audit(blob(fixture()))
        self.assertTrue(proof["test_success"])
        self.assertFalse(proof["product_code_integrated"])
        self.assertFalse(proof["official_policy_promoted"])
        self.assertEqual(proof["source_identity"]["diagnostic_effect_bonus_id"], 13846)
        self.assertEqual(proof["source_identity"]["preserved_gem_id"], 240967)
        self.assertEqual(proof["product_admission"], "BLOCKED_MISSING_INDEPENDENT_EVIDENCE")
        self.assertFalse(proof["dps_comparison_authorized"])

    def test_static_201_only_once(self):
        proof = v.audit(blob(fixture()))
        self.assertEqual(proof["static_nontrinket_head_chmv"], dict(zip(v.STATS, (0, 0, 201, 0))))
        self.assertTrue(proof["budget_attribution"]["do_not_add_201_to_existing_total"])
        self.assertIsNone(proof["budget_attribution"]["actual_ilvl334_G"])
        self.assertIsNone(proof["budget_attribution"]["actual_ilvl334_T"])

    def test_runtime_proc_not_static_budget(self):
        proof = v.audit(blob(fixture()))
        proc = proof["proc_runtime"]
        self.assertTrue(proc["dynamic_not_static_chmv"])
        self.assertIsNone(proc["observed_positive_rating_delta"])
        self.assertIsNone(proc["observed_negative_rating_delta"])
        self.assertFalse(proc["effect_amount_verified"])
        self.assertTrue(proof["budget_attribution"]["do_not_add_proc_delta_as_static_budget"])

    def test_budget_conflicts_unresolved_not_decided(self):
        a = v.audit(blob(fixture()))["budget_attribution"]
        self.assertFalse(a["3182_vs_3184_reconciled"])
        self.assertFalse(a["v1_0_vs_candidate_oil_formula_reconciled"])
        self.assertFalse(a["manual_3284_is_game_calibrated"])

    def test_promotion_claim_rejected(self):
        for claim in (
            {"real_game_334_catalyst_bonus_attested": True},
            {"product_code_integrated": True},
            {"official_policy_promoted": True},
            {"actual_ilvl334_T": 3184},
        ):
            with self.subTest(claim=claim), self.assertRaisesRegex(v.EvidenceBlocked, "NOT_AUTHORIZED"):
                v.audit(blob(fixture()), promotion_claims=claim)

    def test_non_bytes_blocked(self):
        with self.assertRaisesRegex(v.EvidenceBlocked, "JSON2_BYTES_REQUIRED"):
            v.audit("{}")

    def test_changed_gem_blocked(self):
        d = fixture()
        d["sim"]["players"][0]["gear"]["head"]["encoded_item"] = d["sim"]["players"][0]["gear"]["head"]["encoded_item"].replace("240967", "240983")
        with self.assertRaisesRegex(prior.Refused, "GEM_NOT_RETAINED"):
            v.audit(blob(d))

    def test_missing_proc_blocked(self):
        d = fixture()
        d["sim"]["players"][0]["buffs"].pop()
        with self.assertRaisesRegex(prior.Refused, "VENOMCURSED_NOT_TRIGGERED"):
            v.audit(blob(d))

    def test_double_static_mastery_blocked(self):
        d = fixture()
        d["sim"]["players"][0]["gear"]["head"]["mastery_rating"] = 402
        with self.assertRaisesRegex(prior.Refused, "BARE_MASTERY_CHANGED"):
            v.audit(blob(d))

    def test_bad_bonus_blocked(self):
        d = fixture()
        h = d["sim"]["players"][0]["gear"]["head"]
        h["encoded_item"] = h["encoded_item"].replace("bonus_id=13846", "bonus_id=13848")
        with self.assertRaisesRegex(prior.Refused, "BONUS_CHANGED"):
            v.audit(blob(d))

    def test_changed_rune_blocked(self):
        d = fixture()
        d["sim"]["players"][0]["buffs"][1]["name"] = "rune_of_burning_haste"
        with self.assertRaisesRegex(prior.Refused, "RUNE_INVALID"):
            v.audit(blob(d))

    def test_proc_runtime_fields_cannot_prove_scaling(self):
        d = fixture()
        d["sim"]["players"][0]["buffs"][-1]["stat_delta"] = 363
        proof = v.audit(blob(d))
        self.assertIsNone(proof["proc_runtime"]["observed_positive_rating_delta"])
        self.assertFalse(proof["proc_runtime"]["effect_amount_verified"])

if __name__ == "__main__":
    unittest.main()
