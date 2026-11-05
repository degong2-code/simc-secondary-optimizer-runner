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
import hashlib
import json

SCHEMA = "v222_season_gjfo_budget_contract_v1"
STATS = ("crit_rating", "haste_rating", "mastery_rating", "versatility_rating")
SHA = re.compile(r"[0-9a-f]{64}\Z")
REV = re.compile(r"[0-9a-f]{40}\Z")


NO_OIL_SOURCE = "EXPLICIT_NO_OIL_SELECTION"

G_ROUNDING_SCHEMA = "v222_aggregate_G_nearest_10_half_up_v1"
G_ROUNDING_UNIT = 10


def standardize_representative_G(*, observed_G_total, target_ilevel,
                                 source_observation_sha256):
    """Round the WHOLE observed G once, never each item or CHMV component.

    This produces a deterministic numerical transformation and provenance,
    NOT a claim that the underlying Native or current-season source was
    independently validated. That belongs upstream of preprofile_budget().
    The fixed 10-rating unit is the approved standard-reference policy.
    """
    need(type(observed_G_total) is int and observed_G_total > 0,
         "G_STANDARD_REFERENCE_OBSERVED_TOTAL_REQUIRED")
    need(type(target_ilevel) is int and target_ilevel > 0,
         "G_STANDARD_REFERENCE_TARGET_ILEVEL_REQUIRED")
    need(type(source_observation_sha256) is str and
         SHA.fullmatch(source_observation_sha256) is not None,
         "G_STANDARD_REFERENCE_SOURCE_OBSERVATION_REQUIRED")
    standard = ((observed_G_total + G_ROUNDING_UNIT // 2) //
                G_ROUNDING_UNIT) * G_ROUNDING_UNIT
    return {
        "schema": G_ROUNDING_SCHEMA,
        "observed_G_total": observed_G_total,
        "standardized_G": standard,
        "rounding_delta": standard - observed_G_total,
        "rounding_unit": G_ROUNDING_UNIT,
        "target_ilevel": target_ilevel,
        "source_observation_sha256": source_observation_sha256,
    }


class SeasonBudgetBlocked(ValueError):
    pass


def need(condition, reason):
    if not condition:
        raise SeasonBudgetBlocked(reason)


def explicit_no_oil_component(*, game_build, source_catalog_manifest_sha256,
                              selected_oil_item_ids_by_hand):
    """Exact empty oil selection: no applied weapon exists to authenticate.

    This pure v222 input adapter does NOT certify game sources or default oil
    availability; the normal Build must supply the explicit selection.
    """
    need(type(game_build) is str and bool(game_build) and
         type(source_catalog_manifest_sha256) is str and
         SHA.fullmatch(source_catalog_manifest_sha256) is not None,
         "GJFO_NO_OIL_SOURCE_CATALOG_REQUIRED")
    need(type(selected_oil_item_ids_by_hand) is dict and
         not selected_oil_item_ids_by_hand,
         "GJFO_NO_OIL_EXPLICIT_EMPTY_HAND_SELECTION_REQUIRED")
    seed = json.dumps({
        "schema":SCHEMA, "game_build":game_build,
        "source_catalog_manifest_sha256":source_catalog_manifest_sha256,
        "selection":"EXPLICIT_NO_OIL", "oil_item_ids_by_hand":{}
    },sort_keys=True,separators=(",",":"),ensure_ascii=False)
    return {
        "rating":{stat:0 for stat in STATS},
        "game_build":game_build,
        "source_catalog_manifest_sha256":source_catalog_manifest_sha256,
        "source_sha256":hashlib.sha256(seed.encode("utf8")).hexdigest(),
        "source_verification":NO_OIL_SOURCE,
        "selected_oil_item_ids_by_hand":{},
        "applied_hands":[],
        "weapon_applicability_verified":False,
        "proof_not_required_reason":"NO_APPLIED_OIL_ITEM_OR_WEAPON_HAND",
    }


def _vector(value, name):
    need(type(value) is dict and set(value) == set(STATS),
         name + "_FOUR_RATING_VECTOR_REQUIRED")
    need(all(type(value[k]) is int and value[k] >= 0 for k in STATS),
         name + "_NONNEGATIVE_INTEGER_RATING_REQUIRED")
    return {k: value[k] for k in STATS}


def _component(proof, name, build, manifest_sha, numeric_preview_only=False):
    need(type(proof) is dict and proof.get("game_build") == build and
         proof.get("source_catalog_manifest_sha256") == manifest_sha and
         type(proof.get("source_sha256")) is str and
         SHA.fullmatch(proof["source_sha256"]) is not None,
         "GJFO_" + name + "_SAME_BUILD_SOURCE_IDENTITY_REQUIRED")
    # A selected NONE is not a missing oil source. Bind exact empty hands
    # to this source catalog before waiving irrelevant weapon applicability.
    if name == "O" and proof.get("source_verification") == NO_OIL_SOURCE:
        expected = explicit_no_oil_component(
            game_build=build,
            source_catalog_manifest_sha256=manifest_sha,
            selected_oil_item_ids_by_hand={})
        need(proof == expected, "GJFO_O_EXPLICIT_NONE_SELECTION_DRIFT")
        return proof
    # A reported verification label is NOT an independent authentication
    # of the source or its relation to a physical SimC input.
    allowed = (("UNADMITTED_NUMERIC_OBSERVATION",)
               if numeric_preview_only else
               ("EXACT_NATIVE", "VALID_SAME_SEASON_REFERENCE",
                "VALID_SAME_SEASON_SOURCE"))
    need(proof.get("source_verification") in allowed,
         "GJFO_" + name + "_SOURCE_VERIFICATION_MISSING")
    return proof


def preprofile_budget(*, source_catalog, source_artifact_sha256, evidence,
                      target_ilevel, manual_final_T=None,
                      numeric_preview_only=False):
    """Calculate the candidate season budget BEFORE v098 profile creation.

    This is a pure accounting boundary, not evidence authentication or
    environment admission. Upstream collectors must independently verify
    every source/component; the caller must not promote this result to READY.
    It never fetches source data, runs Native, or changes caches.
    """
    need(type(source_catalog) is dict and type(evidence) is dict,
         "GJFO_CONTRACT_OBJECTS_REQUIRED")
    need(type(numeric_preview_only) is bool,
         "GJFO_NUMERIC_PREVIEW_MODE_BOOL_REQUIRED")
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
        _component(proofs[name], name, build, manifest_sha,
                   numeric_preview_only=numeric_preview_only)
    amounts = {}
    for name in ("G", "J", "F"):
        amount = proofs[name].get("rating")
        need(type(amount) is int and amount >= (1 if name == "G" else 0),
             "GJFO_" + name + "_RATING_UNVERIFIED")
        amounts[name] = amount
    # Optional new-season standardized G reference: verify arithmetic and
    # bind its observed source identity. The existing exact/legacy G contracts
    # remain unchanged. A matching SHA or caller label is not source approval.
    g_standardization = proofs["G"].get("standardization")
    if g_standardization is not None:
        need(type(g_standardization) is dict and
             set(g_standardization)=={
                 "schema", "observed_G_total", "standardized_G",
                 "rounding_delta", "rounding_unit", "target_ilevel",
                 "source_observation_sha256"},
             "GJFO_G_STANDARDIZATION_FIELDS_INVALID")
        expected = standardize_representative_G(
            observed_G_total=g_standardization["observed_G_total"],
            target_ilevel=target_ilevel,
            source_observation_sha256=proofs["G"]["source_sha256"])
        need(g_standardization==expected and
             amounts["G"]==expected["standardized_G"],
             "GJFO_G_ROUNDING_OR_SOURCE_DRIFT")
    oil = _vector(proofs["O"].get("rating"), "O")
    hands = proofs["O"].get("applied_hands")
    explicit_none = proofs["O"].get("source_verification") == NO_OIL_SOURCE
    need(type(hands) is list and len(hands) <= 2 and
         all(x in ("main_hand", "off_hand") for x in hands) and
         len(set(hands)) == len(hands),
         "GJFO_O_PHYSICAL_HANDS_REQUIRED")
    if explicit_none:
        # No oil was selected, so no weapon/hand needs an applicability proof.
        need(hands == [] and sum(oil.values()) == 0,
             "GJFO_O_EXPLICIT_NONE_MUST_BE_ZERO")
    elif numeric_preview_only:
        # Source-only v286's same-build representative weapon mask is
        # arithmetic eligibility, NOT full item-level/use validation.
        # v222.reconcile and production preprofile calls cannot accept
        # this downgraded input mode by default.
        need(proofs["O"].get("weapon_applicability_verified") is False
             and proofs["O"].get("source_mask_matches_all_selected_only")
                 is True,
             "GJFO_O_SOURCE_ONLY_MASK_INPUT_REQUIRED")
    else:
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
    return {
        "schema": SCHEMA,
        "status": ("NUMERIC_PREVIEW_UNADMITTED_NO_SOURCE_AUTHENTICATION"
                   if numeric_preview_only else
                   "ARITHMETIC_RECONCILED_SOURCE_AUTHENTICATION_EXTERNAL"),
        "game_build": build, "simc_revision": rev,
        "source_catalog_manifest_sha256": manifest_sha,
        "source_catalog_artifact_sha256": source_artifact_sha256,
        "target_ilevel": target_ilevel,
        "reference_G": amounts["G"], "effective_G": g_effective,
        "J": amounts["J"], "F": amounts["F"],
        "fixed_O": oil, "fixed_L": fixed_L, "fixed_E": fixed_E,
        "reference_B": reference_B, "base_B": B, "final_T": T,
        "manual_final_T_authoritative": manual_final_T is not None,
        **({"O_weapon_proof_not_required_reason":
            "NO_APPLIED_OIL_ITEM_OR_WEAPON_HAND"} if explicit_none else {}),
        **({"G_standardization":dict(g_standardization)}
           if g_standardization is not None else {}),
        "source_authentication_performed_here": False,
        **({"numeric_preview_only":True,"environment_ready":False}
           if numeric_preview_only else {}),
        "native_calls": 0, "network_calls": 0, "cache_mutations": 0,
    }


def reconcile(*, source_catalog, source_artifact_sha256, evidence,
              plan, target_ilevel, manual_final_T=None):
    """Recheck an already generated v098 plan against the same accounting.

    Uses the pre-profile calculator as the only source of B/T arithmetic,
    so the user profile and the season engine cannot silently diverge.
    """
    need(type(plan) is dict, "GJFO_CONTRACT_OBJECTS_REQUIRED")
    resolved = preprofile_budget(
        source_catalog=source_catalog,
        source_artifact_sha256=source_artifact_sha256,
        evidence=evidence, target_ilevel=target_ilevel,
        manual_final_T=manual_final_T)
    need(type(plan.get("base_B")) is int and
         type(plan.get("final_T")) is int and
         plan["base_B"] == resolved["base_B"] and
         plan["final_T"] == resolved["final_T"] and
         plan.get("fixed_O") == resolved["fixed_O"],
         "GJFO_EXISTING_V098_PLAN_B_T_O_MISMATCH")
    return resolved
