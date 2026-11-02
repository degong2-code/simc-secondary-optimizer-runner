#!/usr/bin/env python3
"""v224 request-scoped season G/J/F/O source evidence inventory.

Read-only stage following EXISTING v191 -> v211 -> v213 source compilation.
Unlike a same-season historical reference, raw season DB/SimC candidate rows
do NOT prove representative absolute G, top-quality J/F, or applicable O.
This stage identifies exact source dependencies and independently missing
validation. It never invents amounts, declares the environment ready, admits
user options, reimplements effects or calls SimC Native.

The future source/Native validators can satisfy each reported dependency;
do not turn a self-declared 'verified' string into an authorization.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re

try:
    from . import v213_source_to_catalog as source_bridge
except ImportError:  # script entrypoint from runner/
    import v213_source_to_catalog as source_bridge

SCHEMA = "v224_season_gjfo_evidence_inventory_v1"
COMPONENTS = ("G", "J", "F", "O")
SOURCE = ("gear", "tier", "budget")
EVENTS = ("mid_patch", "season_change", "expansion_change")
BUILD = re.compile(r"[0-9]+(?:\.[0-9]+){3}\Z")
SHA = re.compile(r"[a-f0-9]{64}\Z")
MAX_SOURCE_BYTES = 12_000_000
REQUIREMENTS = {
    "G": (
        "REPRESENTATIVE_GEAR_WEAPON_TIER_IDS_AND_ILVL_VALIDATED",
        "SAME_BUILD_REPRESENTATIVE_CHMV_RATING_OR_NATIVE_REFERENCE",
        "G_WEAPON_LAYOUT_AND_EXCLUDED_TRINKET_OWNERSHIP_VERIFIED",
    ),
    "J": (
        "EXACT_GEM_ITEM_AND_GEM_PROPERTY_EFFECT_JOIN",
        "HIGHEST_QUALITY_EQUIVALENCE_AND_SOCKET_COUNT_VERIFIED",
        "J_STATIC_RATING_AND_SIMC_PROFILE_INPUT_VERIFIED",
    ),
    "F": (
        "EXACT_FLASK_ID_EFFECT_AND_SIMC_INPUT_JOIN",
        "HIGHEST_QUALITY_EFFECT_EQUIVALENCE_VERIFIED",
        "F_STATIC_RATING_AND_CONDITION_VERIFIED",
    ),
    "O": (
        "EXACT_WEAPON_OIL_ITEM_EFFECT_AND_SIMC_TOKEN_JOIN",
        "O_APPLICABLE_WEAPON_HANDS_AND_QUALITY_VERIFIED",
        "O_STATIC_RATING_AND_ONCE_ONLY_GEAR_OVERRIDE_VERIFIED",
    ),
}


class SeasonEvidenceBlocked(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise SeasonEvidenceBlocked(reason)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    path = pathlib.Path(path)
    need(path.is_file() and not path.is_symlink() and
         0 < path.stat().st_size <= MAX_SOURCE_BYTES,
         "V224_UNSAFE_MISSING_OR_OVERSIZED_SOURCE_FILE")
    raw = path.read_bytes()
    try:
        doc = json.loads(raw.decode("utf8"))
    except (UnicodeError, ValueError) as exc:
        raise SeasonEvidenceBlocked("V224_SOURCE_JSON_INVALID") from exc
    need(type(doc) is dict, "V224_SOURCE_OBJECT_REQUIRED")
    return doc, digest(raw)



def core_source_preflight(*, inputs, event, target_ilevel,
                          previous_game_build=None):
    """Preflight new-season gear/tier/consumable *source bytes* BEFORE v211/v213.

    Allows the mandatory G/J/F/O path to start even if unrelated new-season
    enchant/embellishment candidate classification is not implemented. A
    source row or a declared same-build label is not numeric verification.
    This never produces budgets or an approved environment.
    """
    need(event in EVENTS and type(target_ilevel) is int and
         target_ilevel > 0, "V224_CORE_EVENT_OR_ILVL_INVALID")
    need(type(inputs) is dict and set(inputs) == set(SOURCE),
         "V224_CORE_ALL_THREE_INPUTS_REQUIRED")
    rows = {}
    for name in SOURCE:
        pair = inputs[name]
        need(type(pair) is tuple and len(pair) == 2,
             "V224_CORE_EXACT_FILE_IDENTITY_REQUIRED")
        document, original_sha = pair
        need(type(document) is dict and type(original_sha) is str and
             SHA.fullmatch(original_sha) is not None,
             "V224_CORE_SOURCE_DOCUMENT_OR_HASH_INVALID")
        rows[name] = document
    gear, tier, budget = (rows[name] for name in SOURCE)
    build = gear.get("season_build")
    need(type(build) is str and BUILD.fullmatch(build) is not None and
         gear.get("schema") == "v167_product_season_gear_db_v1" and
         tier.get("schema") == "v168_source_first_class_tier_5pc_v1" and
         budget.get("schema") == "v165_current_season_chmv_consumables_v1" and
         tier.get("retail_build") == build and
         budget.get("retail_build") == build and
         gear.get("expansion_id") == tier.get("expansion_id") and
         type(gear.get("items")) is list and
         gear.get("item_count") == len(gear["items"]) and
         gear["item_count"] > 0 and
         type(tier.get("classes")) is dict and
         len(tier["classes"]) == 13 and
         type(tier.get("item_count")) is int and tier["item_count"] > 0,
         "V224_CORE_SAME_BUILD_REPRESENTATIVE_INPUTS_REQUIRED")
    need(previous_game_build is None or
         (type(previous_game_build) is str and
          BUILD.fullmatch(previous_game_build) is not None),
         "V224_CORE_PRIOR_BUILD_INVALID")
    # Client build history is optional; a live new season may even activate
    # without changing the client build. Never certify season membership from
    # the difference, and never require an old local record to collect source.
    output = {
        "schema": "v224_core_season_input_preflight_v1",
        "status": "CORE_SOURCE_PRESENT_GJFO_ALL_MANDATORY_EVIDENCE_PENDING",
        "update_event": event, "game_build": build,
        "previous_game_build": previous_game_build,
        "previous_build_record_status": (
            "NOT_RECORDED" if previous_game_build is None else "RECORDED"),
        "previous_build_is_not_season_proof": True,
        "target_ilevel": target_ilevel,
        "source_input_sha256": {name: inputs[name][1] for name in SOURCE},
        "source_bytes_verified_by_upstream_artifact": False,
        "component_state": {
            name: {
                "status": "BLOCKED_INDEPENDENT_SOURCE_AND_RATING_VERIFICATION",
                "missing_evidence": list(REQUIREMENTS[name]),
                "rating": None,
            } for name in COMPONENTS
        },
        "G": None, "J": None, "F": None, "O": None,
        "B": None, "T": None,
        "budget_can_be_published": False,
        "user_options_auto_admitted": False,
        "requires_v191_source_pinning": True,
        "requires_v213_catalog_join_for_user_options": True,
        "native_calls": 0, "network_calls": 0, "cache_mutations": 0,
    }
    return {**output,
            "receipt_sha256": digest(canonical(output).encode("utf8"))}


def compile_inventory(*, v191, v191_sha, v213, v213_sha,
                      inputs, event, target_ilevel,
                      previous_game_build=None):
    """Check source lineage only. All four components remain unapproved.

    This intentionally has no 'verified' boolean input. No candidate source
    row/handler/hash proves quantitative game effects or a correct SimC
    execution. Full verified G/J/F/O must later be supplied by independent
    source/static-Native evidence verifiers, then reconciled by v222.
    """
    need(event in EVENTS and
         type(target_ilevel) is int and target_ilevel > 0,
         "V224_UPDATE_EVENT_OR_ILVL_INVALID")
    need(type(v191) is dict and type(v213) is dict and
         all(type(x) is str and SHA.fullmatch(x) for x in
             (v191_sha, v213_sha)),
         "V224_CATALOG_IDENTITY_MISSING")
    try:
        source_bridge.verify_catalog(v213)
    except (ValueError, KeyError, TypeError) as exc:
        raise SeasonEvidenceBlocked("V224_V213_SEAL_INVALID") from exc
    need(v191.get("schema") ==
         "v191_unified_patch_season_expansion_data_candidates_v1" and
         v191.get("update_event") == event and
         v191.get("automatic_ui_promotion") is False and
         v191.get("native_calls") == 0,
         "V224_REQUEST_EVENT_NOT_MATCHING_V191")
    build = v191.get("game_build")
    rev = v191.get("simc_revision")
    need(type(build) is str and BUILD.fullmatch(build) is not None and
         type(rev) is str and re.fullmatch(r"[a-f0-9]{40}", rev) is not None and
         v213.get("game_build") == build and
         v213.get("simc_revision") == rev and
         v213.get("source_provenance", {}).get("v191", {}).get("sha256")
             == v191_sha,
         "V224_V191_V213_GAME_BUILD_OR_ARTIFACT_DRIFT")
    need(type(inputs) is dict and set(inputs) == set(SOURCE),
         "V224_ALL_THREE_CORE_SOURCE_BYTES_REQUIRED")
    originals = {}
    input_hashes = v191.get("sha256_by_input", {})
    provenance_hashes = (v213.get("source_provenance", {})
                         .get("v191", {}).get("sha256_by_input", {}))
    for key in SOURCE:
        doc, raw_sha = inputs[key]
        need(type(doc) is dict and type(raw_sha) is str and
             SHA.fullmatch(raw_sha) is not None and
             input_hashes.get(key) == raw_sha and
             provenance_hashes.get(key) == raw_sha,
             "V224_" + key.upper() + "_SOURCE_DIGEST_MISMATCH")
        originals[key] = doc
    gear, tier, budget = (originals[key] for key in SOURCE)
    need(gear.get("season_build") == build and
         tier.get("retail_build") == build and
         budget.get("retail_build") == build and
         gear.get("expansion_id") == tier.get("expansion_id") and
         v191.get("expansion_id") == gear.get("expansion_id") and
         type(gear.get("items")) is list and
         len(gear["items"]) == gear.get("item_count") and
         gear["item_count"] == v213.get("catalog", {}).get("gear", {}).get("count") and
         tier.get("item_count") ==
             v213.get("catalog", {}).get("tier", {}).get("piece_count"),
         "V224_CATALOG_BUILD_OR_REPRESENTATIVE_SOURCE_INVALID")
    need(previous_game_build is None or
         (type(previous_game_build) is str and
          BUILD.fullmatch(previous_game_build) is not None),
         "V224_PREVIOUS_BUILD_INVALID")
    # A source-only season change never licenses previous budget reuse, even
    # if a client build comparison is available. The event identity, Wago
    # source and independent tier/consumable proof must do that work.
    native_builds = v191.get("simc_generated_builds", {})
    need(type(native_builds) is dict and
         set(native_builds) ==
             {"permanent_enchant", "temporary_enchant", "gem_property"},
         "V224_SIMC_COMPILED_SOURCE_BUILD_IDENTITY_MISSING")
    if set(native_builds.values()) != {build}:
        source_warnings = ["SIMC_COMPILED_DBC_BUILD_MISMATCH_REQUIRES_REVIEW"]
    else:
        source_warnings = []
    # An item count and two consumable reference fields are DISCOVERY inputs,
    # never rating budgets or evidence of effect/quality equivalence.
    component_state = {}
    for component in COMPONENTS:
        component_state[component] = {
            "status": "BLOCKED_INDEPENDENT_SOURCE_AND_RATING_VERIFICATION",
            "missing_evidence": list(REQUIREMENTS[component]),
            "rating": None,
            "eligible_for_user_catalog": False,
        }
    state = {
        "schema": SCHEMA,
        "status": "BLOCKED_MANDATORY_GJFO_NOT_IN_V191_V213_RAW_SOURCES",
        "request_event": event,
        "game_build": build,
        "previous_game_build": previous_game_build,
        "previous_build_record_status": (
            "NOT_RECORDED" if previous_game_build is None else "RECORDED"),
        "previous_build_is_not_season_proof": True,
        "simc_revision": rev,
        "target_ilevel": target_ilevel,
        "v191_source_sha256": v191_sha,
        "v213_source_sha256": v213_sha,
        "v213_manifest_sha256": v213["manifest_sha256"],
        "core_input_sha256": {key: inputs[key][1] for key in SOURCE},
        "simc_compiled_builds": native_builds,
        "source_warnings": source_warnings,
        "component_state": component_state,
        "required_components": list(COMPONENTS),
        "verified_components": [],
        "G": None, "J": None, "F": None, "O": None,
        "B": None, "T": None,
        "budget_can_be_published": False,
        "automatic_ui_admission": False,
        "source_to_user_profile_integrated": False,
        "native_calls": 0, "network_calls": 0, "cache_mutations": 0,
    }
    return {**state, "receipt_sha256": digest(canonical(state).encode("utf8"))}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("gear", "tier", "budget", "out"):
        parser.add_argument("--" + name, type=pathlib.Path, required=True)
    parser.add_argument("--v191", type=pathlib.Path)
    parser.add_argument("--v213", type=pathlib.Path)
    parser.add_argument("--core-only", action="store_true")
    parser.add_argument("--event", choices=EVENTS, required=True)
    parser.add_argument("--target-ilevel", type=int, required=True)
    parser.add_argument("--previous-game-build")
    args = parser.parse_args(argv)
    inputs = {name: load(getattr(args, name)) for name in SOURCE}
    if args.core_only:
        need(args.v191 is None and args.v213 is None,
             "V224_CORE_ONLY_CANNOT_CLAIM_V191_V213_PROVENANCE")
        result = core_source_preflight(
            inputs=inputs, event=args.event,
            target_ilevel=args.target_ilevel,
            previous_game_build=args.previous_game_build)
    else:
        need(args.v191 is not None and args.v213 is not None,
             "V224_V191_V213_PINNED_ARTIFACT_REQUIRED")
        season, season_sha = load(args.v191)
        catalog, catalog_sha = load(args.v213)
        result = compile_inventory(
            v191=season, v191_sha=season_sha, v213=catalog,
            v213_sha=catalog_sha, inputs=inputs,
            event=args.event, target_ilevel=args.target_ilevel,
            previous_game_build=args.previous_game_build)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(
        result, sort_keys=True, ensure_ascii=False, indent=2) + "\n",
        encoding="utf8")
    print("V224_GJFO_ALL_MANDATORY_PROOFS_PENDING",
          result["game_build"], list(COMPONENTS),
          "NATIVE0_NOT_USER_READY", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
