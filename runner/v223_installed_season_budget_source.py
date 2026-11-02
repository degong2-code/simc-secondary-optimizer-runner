#!/usr/bin/env python3
"""Read-only, same-season source-to-budget evidence for the existing v222 contract.

Reuses v213's sealed candidate catalog, v191's exact source input hashes,
v089's native-derived rounded same-season reference, and v091's existing oil
serialization. This is NOT a new collector, exact G Native measurement,
highest-quality item admission, or general new-season refresh.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import v089_ilvl_chmv_budget_selector as reference
import v091_weapon_oil_external_adapter as oil
import v213_source_to_catalog as catalog_contract
import v222_season_budget_contract as contract

SCHEMA = "v223_installed_same_season_budget_source_receipt_v1"
MAX_BYTES = 12_000_000


class SourceBudgetBlocked(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise SourceBudgetBlocked(reason)


def _load(path, max_size=MAX_BYTES):
    path = Path(path)
    need(path.is_file() and not path.is_symlink() and
         0 < path.stat().st_size <= max_size,
         "SOURCE_FILE_MISSING_UNSAFE_OR_TOO_LARGE")
    raw = path.read_bytes()
    try:
        doc = json.loads(raw.decode("utf8"))
    except (UnicodeError, ValueError) as exc:
        raise SourceBudgetBlocked("SOURCE_FILE_NOT_VALID_JSON") from exc
    need(type(doc) is dict, "SOURCE_FILE_ROOT_NOT_OBJECT")
    return doc, hashlib.sha256(raw).hexdigest()


def _component(value, sha, catalog, category):
    return {
        "rating": value,
        "game_build": catalog["game_build"],
        "source_catalog_manifest_sha256": catalog["manifest_sha256"],
        "source_sha256": sha,
        "source_verification": category,
    }


def produce(*, catalog, catalog_sha, source_paths, user, bootstrap,
            physical_profile):
    """Derive a v222 receipt only for an already-installed same-season snapshot.

    Fail closed when the exact v191 budget/gear/tier files are unavailable,
    when reference season differs, or when the existing v098 physical profile
    has not already serialized the expected oil hands. Source paths are
    trusted runtime/package paths, never user-supplied HTTP input.
    """
    need(type(catalog) is dict and type(source_paths) is dict and
         set(source_paths) == {"gear", "tier", "budget", "reference"} and
         type(user) is dict and type(bootstrap) is dict and
         type(physical_profile) is str,
         "INTERNAL_SOURCE_INPUT_CONTRACT_REQUIRED")
    try:
        catalog_contract.verify_catalog(catalog)
    except (ValueError, KeyError, TypeError) as exc:
        raise SourceBudgetBlocked("V213_CATALOG_NOT_SEALED") from exc
    need(type(catalog_sha) is str and
         contract.SHA.fullmatch(catalog_sha) is not None,
         "V213_ARTIFACT_SHA_MISSING")
    provenance = catalog.get("source_provenance", {}).get("v191", {})
    source_hashes = provenance.get("sha256_by_input", {})
    need(type(source_hashes) is dict and
         {"gear", "tier", "budget"} <= set(source_hashes),
         "V191_SOURCE_HASH_LINKS_MISSING")
    documents = {}
    digests = {}
    for name in ("gear", "tier", "budget"):
        documents[name], digests[name] = _load(source_paths[name])
        need(digests[name] == source_hashes[name],
             "V191_" + name.upper() + "_SOURCE_BYTES_NOT_INSTALLED_ARTIFACT")
    gear, tier, budget = (documents[k] for k in ("gear", "tier", "budget"))
    build = catalog["game_build"]
    need(gear.get("schema") == "v167_product_season_gear_db_v1" and
         gear.get("season_build") == build and
         tier.get("schema") == "v168_source_first_class_tier_5pc_v1" and
         tier.get("retail_build") == build and
         budget.get("schema") == "v165_current_season_chmv_consumables_v1" and
         budget.get("retail_build") == build and
         gear.get("item_count") == catalog["catalog"]["gear"]["count"] and
         tier.get("item_count") == catalog["catalog"]["tier"]["piece_count"],
         "SOURCE_SAME_BUILD_OR_REPRESENTATIVE_GEAR_TIER_DRIFT")
    try:
        reg, reference_sha = reference.load_registry(source_paths["reference"])
    except (ValueError, OSError, KeyError, TypeError) as exc:
        raise SourceBudgetBlocked("G_REFERENCE_NOT_VALIDATED_BY_V089") from exc
    need(tier.get("season") == reg["season"],
         "G_REFERENCE_AND_TIER_SEASON_MISMATCH")
    gem = budget.get("ordinary_gem", {})
    flask = budget.get("flasks", {})
    J, F = gem.get("total_J"), flask.get("total_F")
    bonuses = gem.get("highest_quality_bonus")
    stats = flask.get("by_stat")
    need(type(J) is int and J > 0 and
         type(F) is int and F > 0 and
         type(gem.get("slots")) is int and
         type(bonuses) is list and len(bonuses) == 2 and
         all(type(x) is int and x > 0 for x in bonuses) and
         J == gem["slots"] * sum(bonuses) and
         type(stats) is dict and
         set(stats) == {"crit", "haste", "mastery", "versatility"} and
         all(type(row) is dict and type(row.get("item_id")) is int and
             row["item_id"] > 0 and row.get("rating") == F
             for row in stats.values()) and
         len({row["item_id"] for row in stats.values()}) == 4 and
         budget.get("source_status") ==
             "PUBLIC_ITEM_PAGES_MATCH_APPROVED_CHMV_BUDGET" and
         reg.get("J") == J and reg.get("F") == F,
         "J_F_HIGHEST_QUALITY_REFERENCE_NOT_RECONCILED")
    need(budget.get("oil_accounting") ==
         "FIXED_O_PER_APPLIED_WEAPON_CRIT16_HASTE16_NO_DOUBLE_COUNT",
         "O_CURRENT_SEASON_ACCOUNTING_SOURCE_MISSING")
    target = user.get("target", {})
    character = user.get("character", {})
    level = bootstrap.get("target_ilevel")
    weapon_layout = bootstrap.get("weapon_form")
    need(type(target) is dict and target.get("ilevel") == level and
         type(level) is int and 266 <= level <= 344 and
         type(character) is dict and
         character.get("class") and character.get("spec"),
         "G_TARGET_OR_CHARACTER_NOT_SEALED")
    need(not user.get("special_items") and not user.get("embellishments") and
         not user.get("verified_enchant"),
         "FIXED_L_E_REQUIRE_EXACT_INDEPENDENT_NATIVE_PROOFS")
    try:
        track = reference.pick_track(character, weapon_layout)
    except (ValueError, KeyError, TypeError) as exc:
        raise SourceBudgetBlocked("G_REFERENCE_WEAPON_TRACK_UNVERIFIED") from exc
    row = reg["values"][level - 266]
    need(row.get("ilevel") == level and
         type(row.get(track)) is int and row[track] > J + F,
         "G_REFERENCE_LEVEL_OR_TOTAL_MISSING")
    G = row[track] - J - F  # rounded same-season reference, NOT exact G
    hands = user.get("oil_hands")
    need(type(hands) is list and len(hands) <= 2 and
         len(set(hands)) == len(hands) and
         set(hands) <= oil.HANDS and
         (not hands or "main_hand" in hands) and
         weapon_layout in oil.SINGLE_LAYOUTS | oil.DUAL_LAYOUTS,
         "O_SELECTED_HANDS_OR_LAYOUT_INVALID")
    if weapon_layout in oil.SINGLE_LAYOUTS:
        need("off_hand" not in hands, "O_SINGLE_WEAPON_OFFHAND_NOT_ALLOWED")
    else:
        need("off_hand" in hands or hands == ["main_hand"] or not hands,
             "O_DUAL_HANDS_INVALID")
    try:
        slots = oil._profile_slots(physical_profile)
    except (ValueError, TypeError) as exc:
        raise SourceBudgetBlocked("O_ACTUAL_PHYSICAL_SLOTS_INVALID") from exc
    need(all(hand in slots for hand in hands),
         "O_SELECTED_HAND_NOT_IN_PHYSICAL_PROFILE")
    expected = ("/".join(hand + ":" + oil.OIL for hand in
                          ("main_hand", "off_hand") if hand in hands)
                if hands else "disabled")
    temp_lines = [line for line in physical_profile.splitlines()
                  if line.startswith("temporary_enchant=")]
    need(temp_lines == ["temporary_enchant=" + expected],
         "O_PROFILE_SERIALIZATION_DIFFERENT_FROM_SELECTED_HANDS")
    O = {key: oil.PER_WEAPON[key] * len(hands) for key in contract.STATS}
    fixed_zero = {key: 0 for key in contract.STATS}
    evidence = {
        "schema": contract.SCHEMA,
        "game_build": build,
        "simc_revision": catalog["simc_revision"],
        "source_catalog_manifest_sha256": catalog["manifest_sha256"],
        "source_catalog_artifact_sha256": catalog_sha,
        "target_ilevel": level,
        "components": {
            "G": _component(G, reference_sha, catalog,
                            "VALID_SAME_SEASON_REFERENCE"),
            "J": _component(J, digests["budget"], catalog,
                            "VALID_SAME_SEASON_SOURCE"),
            "F": _component(F, digests["budget"], catalog,
                            "VALID_SAME_SEASON_SOURCE"),
            "O": {**_component(O, digests["budget"], catalog,
                               "VALID_SAME_SEASON_SOURCE"),
                  "applied_hands": [x for x in ("main_hand", "off_hand")
                                    if x in hands],
                  "weapon_applicability_verified": True},
        },
        "fixed_L": fixed_zero, "fixed_E": fixed_zero,
        "G_reference_excludes_selected_E": True,
    }
    return {
        "schema": SCHEMA,
        "status": "CURRENT_SEASON_REFERENCE_SOURCE_LINKS_VERIFIED_NOT_REFRESHED",
        "evidence": evidence,
        "reference_track": track,
        "reference_rounded": True,
        "source_input_sha256": {**digests, "reference": reference_sha},
        "source_not_native_effect_or_highest_quality_admission": True,
        "native_calls": 0, "network_calls": 0,
    }
