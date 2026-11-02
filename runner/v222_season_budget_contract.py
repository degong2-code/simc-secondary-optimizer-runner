#!/usr/bin/env python3
"""Season G/J/F/O arithmetic adapter for the existing v216/v098 path.

This does NOT collect or authenticate source evidence, construct a profile,
admit user options, or run Native. The source validator must supply trusted,
same-build component receipts before this adapter can be used by production.
An internally consistent receipt alone is NOT proof that the source values
or oil applicability have been verified.
"""
from __future__ import annotations

import re

SCHEMA = "v222_season_gjfo_budget_contract_v1"
STATS = ("crit_rating", "haste_rating", "mastery_rating", "versatility_rating")
SHA = re.compile(r"[0-9a-f]{64}\Z")
REV = re.compile(r"[0-9a-f]{40}\Z")


class SeasonBudgetBlocked(ValueError):
    pass


def need(condition, reason):
    if not condition:
        raise SeasonBudgetBlocked(reason)


def _vector(value, name):
    need(type(value) is dict and set(value) == set(STATS),
         name + "_FOUR_RATING_VECTOR_REQUIRED")
    need(all(type(value[k]) is int and value[k] >= 0 for k in STATS),
         name + "_NONNEGATIVE_INTEGER_RATING_REQUIRED")
    return {k: value[k] for k in STATS}


def _component(proof, name, build, manifest_sha):
    need(type(proof) is dict and proof.get("game_build") == build and
         proof.get("source_catalog_manifest_sha256") == manifest_sha and
         type(proof.get("source_sha256")) is str and
         SHA.fullmatch(proof["source_sha256"]) is not None,
         "GJFO_" + name + "_SAME_BUILD_SOURCE_IDENTITY_REQUIRED")
    # A reported verification label is NOT an independent authentication
    # of the source or its relation to a physical SimC input.
    need(proof.get("source_verification") in
         ("EXACT_NATIVE", "VALID_SAME_SEASON_REFERENCE",
          "VALID_SAME_SEASON_SOURCE"),
         "GJFO_" + name + "_SOURCE_VERIFICATION_MISSING")
    return proof


def reconcile(*, source_catalog, source_artifact_sha256, evidence,
              plan, target_ilevel, manual_final_T=None):
    """Check numeric ownership and require agreement with an existing v098 plan.

    Evidence is internal-only, never copied from browser input. Verification
    labels and hashes are checked for identity/structure but source proofs
    must be independently authenticated by the existing source pipeline.
    """
    need(type(source_catalog) is dict and type(evidence) is dict and
         type(plan) is dict, "GJFO_CONTRACT_OBJECTS_REQUIRED")
    build = source_catalog.get("game_build")
    rev = source_catalog.get("simc_revision")
    manifest_sha = source_catalog.get("manifest_sha256")
    need(type(build) is str and bool(build) and
         type(rev) is str and REV.fullmatch(rev) is not None and
         type(manifest_sha) is str and SHA.fullmatch(manifest_sha) is not None and
         type(source_artifact_sha256) is str and
         SHA.fullmatch(source_artifact_sha256) is not None,
         "GJFO_CATALOG_SOURCE_IDENTITY_INVALID")
    need(evidence.get("schema") == SCHEMA and
         evidence.get("game_build") == build and
         evidence.get("simc_revision") == rev and
         evidence.get("source_catalog_manifest_sha256") == manifest_sha and
         evidence.get("source_catalog_artifact_sha256") ==
             source_artifact_sha256 and
         type(target_ilevel) is int and target_ilevel > 0 and
         evidence.get("target_ilevel") == target_ilevel,
         "GJFO_EVIDENCE_VERSION_OR_LEVEL_MISMATCH")
    proofs = evidence.get("components")
    need(type(proofs) is dict and set(proofs) == {"G", "J", "F", "O"},
         "GJFO_ALL_FOUR_COMPONENTS_REQUIRED")
    for name in ("G", "J", "F", "O"):
        _component(proofs[name], name, build, manifest_sha)
    amounts = {}
    for name in ("G", "J", "F"):
        amount = proofs[name].get("rating")
        need(type(amount) is int and amount >= (1 if name == "G" else 0),
             "GJFO_" + name + "_RATING_UNVERIFIED")
        amounts[name] = amount
    oil = _vector(proofs["O"].get("rating"), "O")
    hands = proofs["O"].get("applied_hands")
    need(type(hands) is list and len(hands) <= 2 and
         all(x in ("main_hand", "off_hand") for x in hands) and
         len(set(hands)) == len(hands),
         "GJFO_O_PHYSICAL_HANDS_REQUIRED")
    need(proofs["O"].get("weapon_applicability_verified") is True,
         "GJFO_O_WEAPON_APPLICABILITY_NOT_VERIFIED")
    if not hands:
        need(sum(oil.values()) == 0, "GJFO_O_UNSELECTED_NONZERO")
    else:
        need(sum(oil.values()) > 0, "GJFO_O_SELECTED_ZERO_OR_UNKNOWN")
    fixed_L = _vector(evidence.get("fixed_L"), "L")
    fixed_E = _vector(evidence.get("fixed_E"), "E")
    need(type(evidence.get("G_reference_excludes_selected_E")) is bool,
         "GJFO_E_BUDGET_OWNERSHIP_UNKNOWN")
    includes_E = not evidence["G_reference_excludes_selected_E"]
    need(includes_E or sum(fixed_L.values()) <= amounts["G"],
         "GJFO_L_EXCEEDS_BASE_G")
    g_effective = (amounts["G"] +
                   (sum(fixed_E.values()) if not includes_E else 0))
    need(sum(fixed_L.values()) + sum(fixed_E.values()) <= g_effective,
         "GJFO_L_E_EXCEEDS_EFFECTIVE_G")
    reference_B = g_effective + amounts["J"] + amounts["F"]
    O = sum(oil.values())
    need(manual_final_T is None or
         (type(manual_final_T) is int and manual_final_T > 0),
         "GJFO_MANUAL_FINAL_T_INVALID")
    B = reference_B if manual_final_T is None else manual_final_T - O
    T = B + O
    need(B >= amounts["J"] + amounts["F"] +
         sum(fixed_L.values()) + sum(fixed_E.values()),
         "GJFO_FIXED_MINIMA_EXCEED_TOTAL")
    need(type(plan.get("base_B")) is int and
         type(plan.get("final_T")) is int and
         plan["base_B"] == B and plan["final_T"] == T and
         plan.get("fixed_O") == oil,
         "GJFO_EXISTING_V098_PLAN_B_T_O_MISMATCH")
    return {
        "schema": SCHEMA,
        "status": "ARITHMETIC_RECONCILED_SOURCE_AUTHENTICATION_EXTERNAL",
        "game_build": build, "simc_revision": rev,
        "source_catalog_manifest_sha256": manifest_sha,
        "source_catalog_artifact_sha256": source_artifact_sha256,
        "target_ilevel": target_ilevel,
        "reference_G": amounts["G"], "effective_G": g_effective,
        "J": amounts["J"], "F": amounts["F"],
        "fixed_O": oil, "fixed_L": fixed_L, "fixed_E": fixed_E,
        "reference_B": reference_B, "base_B": B, "final_T": T,
        "manual_final_T_authoritative": manual_final_T is not None,
        "source_authentication_performed_here": False,
        "native_calls": 0, "network_calls": 0, "cache_mutations": 0,
    }
