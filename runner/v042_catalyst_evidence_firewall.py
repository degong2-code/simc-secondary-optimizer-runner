#!/usr/bin/env python3
"""v042 evidence firewall around the pinned v041 334 catalyst trial.

Bounded diagnostic only. The static item mastery rating cannot include runtime
Venomcursed proc deltas. No real-game 334 catalyst bonus attestation, physical
socket rule, automatic gear budget, user item selection, or DPS optimization.
This module does not mutate original v032/v041 modules or product state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

import v041_catalyst_gem_proc_probe as v041

SCHEMA = "v042_catalyst_evidence_firewall_v1"
PINNED_ITEM = {
    "tier_item_id": 271564,
    "original_stat_item_id": 271874,
    "diagnostic_effect_bonus_id": 13846,
    "ilevel": 334,
    "preserved_gem_id": 240967,
}
STATS = ("crit_rating", "haste_rating", "mastery_rating", "versatility_rating")
PENDING = (
    "REAL_GAME_334_CATALYST_BONUS_LIST_MISSING",
    "DYNAMIC_STAT_DELTAS_NOT_MEASURED",
    "ITEM_LEVEL_EFFECT_SCALING_UNVERIFIED",
    "PHYSICAL_SOCKET_AND_GEM_MECHANICS_UNVERIFIED",
    "REAL_G_AND_T_GEAR_BUDGET_NOT_RECALCULATED",
    "USER_SELECTED_ITEM_NOT_ATTESTED",
    "V016_TO_GITHUB_PRODUCT_INTEGRATION_NOT_ATTESTED",
)
class EvidenceBlocked(ValueError):
    pass

def require(condition, reason):
    if not condition:
        raise EvidenceBlocked(reason)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def audit(payload: bytes, *, promotion_claims=None) -> dict:
    """Fail closed on product assertions; trial PASS is not product acceptance."""
    require(type(payload) is bytes, "JSON2_BYTES_REQUIRED")
    require(promotion_claims is None or promotion_claims == {},
            "EXTERNAL_PRODUCT_OR_POLICY_CLAIMS_NOT_AUTHORIZED")
    prior = v041.audit_native(payload)  # independent of report self-description
    obj = json.loads(payload)
    player = obj["sim"]["players"][0]
    head = player["gear"]["head"]
    native_static = {}
    for stat in STATS:
        value = head.get(stat, 0)
        require(type(value) is int and value >= 0, "STATIC_STAT_NOT_INTEGRAL:" + stat)
        native_static[stat] = value
    require(tuple(native_static.values()) == (0, 0, 201, 0),
            "CATALYST_STATIC_CHMV_CHANGED")
    proc = [buff for buff in player["buffs"]
            if buff.get("name") == "venomcursed_mastery"]
    require(len(proc) == 1 and proc[0].get("spell") == 1307922,
            "PROC_EVIDENCE_AMBIGUOUS")
    require(prior["head"] == {
        "tier_id": PINNED_ITEM["tier_item_id"],
        "redirected_original_id": PINNED_ITEM["original_stat_item_id"],
        "ilevel": PINNED_ITEM["ilevel"],
        "bonus_id": PINNED_ITEM["diagnostic_effect_bonus_id"],
        "gem_id": PINNED_ITEM["preserved_gem_id"],
        "fixed_mastery_rating": 201
    }, "IDENTITY_CONTRACT_DRIFT")
    # JSON2 buff name/uptime proves a runtime proc; it does NOT prove a
    # static budget contribution or the actual +/- rating magnitudes.
    return {
        "schema": SCHEMA,
        "trial_status": "PASS_PINNED_NATIVE_EVIDENCE_BOUNDARY_ONLY",
        "test_success": True,
        "product_code_integrated": False,
        "official_policy_promoted": False,
        "source_identity": dict(PINNED_ITEM),
        "native_json2_sha256": digest(payload),
        "static_nontrinket_head_chmv": native_static,
        "static_mastery_201_counted_once_inside_gear_budget_if_RECALIBRATED": True,
        "proc_runtime": {
            "name": "venomcursed_mastery",
            "spell": 1307922,
            "starts_mean": proc[0].get("start_count"),
            "uptime_pct": proc[0].get("uptime"),
            "dynamic_not_static_chmv": True,
            "observed_positive_rating_delta": None,
            "observed_negative_rating_delta": None,
            "effect_amount_verified": False,
            "source_implementation_reference": "pinned SimC unique_gear_midnight.cpp venomcursed effectN(1)/effectN(2)"
        },
        "budget_attribution": {
            "actual_ilvl334_G": None,
            "actual_ilvl334_T": None,
            "3182_vs_3184_reconciled": False,
            "v1_0_vs_candidate_oil_formula_reconciled": False,
            "manual_3284_is_game_calibrated": False,
            "do_not_add_201_to_existing_total": True,
            "do_not_add_proc_delta_as_static_budget": True,
        },
        "product_admission": "BLOCKED_MISSING_INDEPENDENT_EVIDENCE",
        "unresolved": list(PENDING),
        "dps_comparison_authorized": False,
        "global_optimum_proven": False,
        "official_work_os_m0_not_run": True
    }

def run(binary: pathlib.Path, output: pathlib.Path) -> int:
    output.mkdir(parents=True, exist_ok=True)
    receipt = {
        "schema": SCHEMA,
        "status": "BLOCKED",
        "test_success": False,
        "product_code_integrated": False,
        "official_policy_promoted": False,
        "maximum_native_calls": 1,
        "native_calls_attempted": 0,
        "product_admission": "BLOCKED_MISSING_INDEPENDENT_EVIDENCE",
    }
    try:
        # The existing v041 wrapper already pins the binary, profile, item
        # identity, four-piece tier, rune, gem, and one Native call maximum.
        native_output = output / "native"
        code = v041.run(binary, native_output)
        previous = json.loads((native_output / "V041_RECEIPT.json").read_text())
        receipt["native_calls_attempted"] = previous.get("native_attempts", 0)
        require(receipt["native_calls_attempted"] <= 1, "NATIVE_CALL_LIMIT_EXCEEDED")
        require(code == 0 and previous.get("status", "").startswith("PASS_"),
                "V041_TRIAL_NOT_PASS")
        raw = (native_output / "result.json").read_bytes()
        receipt["evidence"] = audit(raw)
        require(receipt["evidence"]["product_admission"].startswith("BLOCKED_"),
                "PRODUCT_GATE_UNEXPECTEDLY_OPEN")
        receipt["test_success"] = True
        receipt["status"] = "PASS_BOUNDED_V042_FIREWALL_NOT_PRODUCT_ADMISSION"
    except Exception as exc:
        receipt["error_code"] = type(exc).__name__ + ":" + str(exc)
    (output / "V042_RECEIPT.json").write_text(
        json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8")
    print("V042_RESULT", receipt["status"], "native_attempts",
          receipt["native_calls_attempted"], flush=True)
    return 0 if receipt["test_success"] else 3

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    sys.exit(run(args.binary.resolve(), args.output.resolve()))
