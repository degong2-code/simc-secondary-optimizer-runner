#!/usr/bin/env python3
"""v213: deterministic v191 -> v211 -> v196 source/catalog handoff.

The v191 artifact is the sole current-season candidate source. v211 classifies
those exact rows from pinned SimC DBC/spell/handler sources. This module joins
the two by complete source identity and emits one versioned catalog artifact
that v196 can consume. Discovery/classification never grants user selection.
No Native calls, network calls, collectors, or optimizer execution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SCHEMA = "v213_current_season_source_to_catalog_v1"
V191 = "v191_unified_patch_season_expansion_data_candidates_v1"
V211 = "v211_current_season_enchant_effect_classification_v1"
V196_SOURCE = "v196_source_first_enchant_candidates_v1"

# InventoryType is the physical source enum. Unknown values are retained as
# UNKNOWN/PENDING; localized hints never override the source enum.
GEAR_INVENTORY_GROUPS = {
    1: "head", 2: "neck", 3: "shoulders", 5: "chest",
    6: "waist", 7: "legs", 8: "feet", 9: "wrists", 10: "hands",
    11: "finger", 12: "trinket", 13: "weapon_one_hand",
    14: "weapon_shield", 15: "weapon_ranged", 16: "back",
    17: "weapon_two_hand", 20: "chest", 23: "weapon_off_hand",
    26: "weapon_ranged",
}
ARMOR_ENCHANT_SLOTS = {
    1: "head", 3: "shoulders", 5: "chest", 20: "chest",
    8: "feet", 11: "finger1/finger2",
}
ENCHANT_CATEGORY_SLOT = {
    "boots": "feet", "chest": "chest", "helm": "head",
    "ring": "finger1/finger2", "shoulders": "shoulders",
    "weapon": "WEAPON_SUBCLASS_NOT_YET_USER_SLOT_CERTIFIED",
}
EXPECTED_ENCHANT_COUNTS = {
    "total": 38,
    "static_chmv_rating": 8,
    "static_nonchmv_only_or_mixed": 19,
    "spell_effects": 15,
    "native_E_measured": 2,
    "user_selectable_existing_scope": 1,
    "developer_only_exact_scope": 1,
    "locked": 36,
}


class CatalogBlocked(ValueError):
    pass


def need(condition, reason):
    if not condition:
        raise CatalogBlocked(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_json(path, max_bytes=25_000_000):
    path = Path(path)
    need(path.is_file() and 0 < path.stat().st_size <= max_bytes,
         "INPUT_FILE_MISSING_OR_SIZE_INVALID:" + path.name)
    raw = path.read_bytes()
    try:
        return json.loads(raw.decode("utf8")), sha(raw)
    except (UnicodeError, ValueError) as exc:
        raise CatalogBlocked("INPUT_JSON_INVALID:" + path.name) from exc


def _candidate_identity(row, token_key):
    return (
        row.get("enchant_id"),
        row.get(token_key),
        row.get("quality_rank"),
        row.get("item_class"),
        row.get("inventory_type_mask"),
        row.get("item_subclass_mask"),
    )


def _slot_group_for_gear(row):
    inventory_type = row.get("inventory_type")
    need(type(inventory_type) is int and inventory_type > 0,
         "GEAR_INVENTORY_TYPE_INVALID:" + str(row.get("item_id")))
    group = GEAR_INVENTORY_GROUPS.get(inventory_type)
    if group is None:
        return "UNKNOWN_INVENTORY_TYPE_" + str(inventory_type), "UNKNOWN_PENDING"
    hint = row.get("slot_hint")
    if hint is not None:
        need(type(hint) is str and hint == group,
             "GEAR_SLOT_HINT_CONFLICT:" + str(row.get("item_id")))
    return group, "SOURCE_INVENTORY_TYPE_RESOLVED"


def _compile_gear(season):
    gear = season.get("gear", {})
    rows = gear.get("candidates")
    need(type(rows) is list and len(rows) == gear.get("count"),
         "V191_GEAR_CANDIDATE_ROWS_MISSING_OR_COUNT_DRIFT")
    groups = {}
    ids = set()
    categories = {}
    unresolved = []
    for source in rows:
        need(type(source) is dict and
             type(source.get("item_id")) is int and source["item_id"] > 0 and
             source["item_id"] not in ids,
             "GEAR_ITEM_ID_INVALID_OR_DUPLICATE")
        ids.add(source["item_id"])
        for key in ("class_id", "subclass_id", "inventory_type",
                    "allowed_class_mask"):
            need(type(source.get(key)) is int,
                 "GEAR_SOURCE_MASK_FIELD_MISSING:" + key)
        group, status = _slot_group_for_gear(source)
        item = dict(source)
        item["slot_group"] = group
        item["slot_resolution_status"] = status
        item["user_selectable"] = False
        groups.setdefault(group, []).append(item)
        category = source.get("category")
        need(type(category) is str and bool(category),
             "GEAR_CATEGORY_MISSING")
        categories[category] = categories.get(category, 0) + 1
        if status == "UNKNOWN_PENDING":
            unresolved.append("GEAR_SLOT_UNKNOWN:" + str(source["item_id"]))
    ordered = {
        key: sorted(value, key=lambda x: x["item_id"])
        for key, value in sorted(groups.items())
    }
    return {
        "count": len(rows),
        "slot_group_counts": {key: len(value) for key, value in ordered.items()},
        "category_counts": dict(sorted(categories.items())),
        "slot_groups": ordered,
        "unresolved_count": len(unresolved),
        "unresolved": unresolved,
    }


def _compile_tier(season):
    tier = season.get("tier", {})
    classes = tier.get("classes")
    need(type(classes) is dict and len(classes) == tier.get("class_count") == 13,
         "V191_TIER_CLASS_ROWS_MISSING_OR_COUNT_DRIFT")
    slots = {"head", "shoulders", "chest", "hands", "legs"}
    seen = set()
    output = {}
    for class_name, source in sorted(classes.items()):
        pieces = source.get("pieces")
        need(type(pieces) is dict and set(pieces) == slots,
             "TIER_SLOT_SET_INVALID:" + class_name)
        need(type(source.get("allowed_class_mask")) is int and
             type(source.get("item_set_id")) is int,
             "TIER_CLASS_APPLICABILITY_MISSING:" + class_name)
        for slot, item_id in pieces.items():
            need(type(item_id) is int and item_id > 0 and item_id not in seen,
                 "TIER_ITEM_ID_INVALID_OR_DUPLICATE")
            seen.add(item_id)
        output[class_name] = {
            "allowed_class_mask": source["allowed_class_mask"],
            "item_set_id": source["item_set_id"],
            "names": dict(sorted(source.get("names", {}).items())),
            "pieces": dict(sorted(pieces.items())),
        }
    need(len(seen) == tier.get("piece_count") == 65,
         "TIER_PIECE_COUNT_DRIFT")
    return {"class_count": len(output), "piece_count": len(seen),
            "classes": output}


def _compile_enchants(season, classification):
    source = season.get("enchants", {}).get("current_season_midnight", {})
    candidates = source.get("highest_rank_candidates")
    rows = classification.get("rows")
    need(source.get("count") == 38 and type(candidates) is list
         and len(candidates) == 38,
         "V191_CURRENT_SEASON_ENCHANT_COUNT_INVALID")
    need(type(rows) is list and len(rows) == 38,
         "V211_CLASSIFICATION_ROW_COUNT_INVALID")
    by_identity = {}
    by_id = {}
    for row in rows:
        identity = _candidate_identity(row, "token")
        need(identity[0] not in by_id and identity not in by_identity,
             "V211_DUPLICATE_ENCHANT_CLASSIFICATION_IDENTITY")
        by_identity[identity] = row
        by_id[identity[0]] = row
    need(len(by_identity) == 38, "V211_CLASSIFICATION_IDENTITY_COUNT_INVALID")

    groups = {}
    joined = []
    candidate_ids = set()
    for candidate in candidates:
        need(type(candidate) is dict and
             candidate.get("user_selectable") is False,
             "V191_ENCHANT_CANDIDATE_SELECTION_DRIFT")
        identity = _candidate_identity(candidate, "simc_token")
        need(identity[0] not in candidate_ids,
             "V191_DUPLICATE_ENCHANT_CANDIDATE_ID")
        candidate_ids.add(identity[0])
        classified = by_identity.get(identity)
        need(classified is not None,
             "V191_V211_EXACT_ENCHANT_IDENTITY_JOIN_MISSING:" +
             str(candidate.get("enchant_id")))
        need(classified.get("simc_effect_owner") == "SIMC" and
             classified.get("simc_effect_reimplemented") is False and
             classified.get("unknown_components") == [],
             "V211_EFFECT_OWNERSHIP_OR_UNKNOWN_COMPONENT_DRIFT:" +
             str(candidate["enchant_id"]))

        token = candidate["simc_token"]
        prefix = token.split("__", 1)[0]
        category = prefix.replace("enchant_", "")
        expected_slot = ENCHANT_CATEGORY_SLOT.get(category)
        need(expected_slot is not None, "ENCHANT_CATEGORY_UNKNOWN:" + category)
        mask = candidate.get("inventory_type_mask")
        item_class = candidate.get("item_class")
        if item_class == 4:
            need(type(mask) is int and mask > 0,
                 "ARMOR_ENCHANT_MASK_MISSING:" + str(candidate["enchant_id"]))
            mask_types = [i for i in range(1, 31) if mask & (1 << i)]
            need(candidate.get("inventory_type_options") == mask_types,
                 "V191_ENCHANT_MASK_OPTIONS_DRIFT:" + str(candidate["enchant_id"]))
            need(mask_types and all(t in ARMOR_ENCHANT_SLOTS for t in mask_types),
                 "ENCHANT_SLOT_MASK_UNKNOWN_OR_MULTI_SLOT_CONFLICT:" +
                 str(candidate["enchant_id"]))
            resolved = sorted({ARMOR_ENCHANT_SLOTS[t] for t in mask_types})
            need(len(resolved) == 1,
                 "ENCHANT_SLOT_MASK_MULTI_SLOT_CONFLICT:" +
                 str(candidate["enchant_id"]))
            slot_group = resolved[0]
            need(slot_group == expected_slot,
                 "ENCHANT_CATEGORY_SLOT_MASK_CONFLICT:" +
                 str(candidate["enchant_id"]))
            slot_status = "SOURCE_MASK_RESOLVED"
        elif item_class == 2:
            need(category == "weapon" and mask == 0 and
                 type(candidate.get("item_subclass_mask")) is int and
                 candidate["item_subclass_mask"] > 0,
                 "WEAPON_ENCHANT_SUBCLASS_MASK_INVALID")
            slot_group = expected_slot
            slot_status = "WEAPON_SUBCLASS_PENDING_EXACT_HAND_APPLICABILITY"
        else:
            raise CatalogBlocked("ENCHANT_ITEM_CLASS_UNSUPPORTED:" +
                                 str(candidate.get("enchant_id")))

        item = {
            "token": token,
            "enchant_id": candidate["enchant_id"],
            "quality_rank": candidate["quality_rank"],
            "item_class": item_class,
            "inventory_type_mask": mask,
            "inventory_type_options": list(candidate.get(
                "inventory_type_options", [])),
            "item_subclass_mask": candidate["item_subclass_mask"],
            "slot_group": slot_group,
            "slot_resolution_status": slot_status,
            "selection_status": classified["selection_status"],
            "ui_selectable": False,
            "classification": classified,
        }
        groups.setdefault(category, []).append(item)
        joined.append(item)

    need(candidate_ids == set(by_id),
         "V191_V211_ENCHANT_CANDIDATE_SET_MISMATCH")
    counts = classification.get("counts", {})
    actual_counts = {
        "total": len(rows),
        "static_chmv_rating": sum(bool(x.get("static_chmv_rating_present_in_dbc"))
                                  for x in rows),
        "static_nonchmv_only_or_mixed": sum(
            bool(x.get("static_components")) and
            not x.get("static_chmv_rating_present_in_dbc", False) for x in rows),
        "spell_effects": sum(bool(x.get("spell_effects")) for x in rows),
        "native_E_measured": sum(
            x.get("native_E_evidence", {}).get("status") != "NOT_MEASURED"
            for x in rows),
        "user_selectable_existing_scope": sum(
            x.get("selection_status") == "EXISTING_EAGLE_ONE_SCOPE_USER_CHOICE"
            for x in rows),
        "developer_only_exact_scope": sum(
            x.get("selection_status") == "DEVELOPER_ONLY_EXACT_SCOPE"
            for x in rows),
        "locked": sum(
            x.get("selection_status") == "LOCKED_NO_GENERAL_USER_ADMISSION"
            for x in rows),
    }
    need(counts == EXPECTED_ENCHANT_COUNTS and actual_counts == counts,
         "V211_CLASSIFICATION_COUNTS_OR_SELECTION_BOUNDARY_DRIFT")
    need(classification.get("native_calls") == 0 and
         classification.get("automatic_ui_promotion") is False,
         "V211_CLASSIFIER_SIDE_EFFECT_OR_PROMOTION_INVALID")
    return {
        "count": len(joined),
        "group_counts": {key: len(value) for key, value in sorted(groups.items())},
        "items": sorted(joined, key=lambda x: x["enchant_id"]),
        "groups": {key: sorted(value, key=lambda x: x["enchant_id"])
                   for key, value in sorted(groups.items())},
        "selection_policy": {
            "classifier_grants_selection": False,
            "existing_user_approval_is_applied_by": "v196",
            "only_existing_native_scoped_choice": 7967,
            "developer_only": [8025],
            "all_other_candidates_remain_locked": True,
        },
    }


def _related_source_counts(season):
    counts = season.get("related_source_counts")
    need(type(counts) is dict and set(counts) == {
        "gear_item_candidates", "tier_piece_ids",
        "food_raw_item_candidates", "potion_raw_item_candidates",
        "food_handler_registrations", "potion_handler_registrations",
        "embellishment_darkmoon_registrations", "temporary_enchant_entries",
        "gem_property_records"
    }, "V191_RELATED_SOURCE_COUNTS_MISSING")
    return counts


def compile_catalog(season, season_sha, classification, classification_sha):
    need(season.get("schema") == V191 and
         season.get("source_first") is True and
         season.get("automatic_ui_promotion") is False and
         season.get("native_calls") == 0 and
         season.get("network_calls_by_compiler") == 0,
         "V191_SOURCE_CANDIDATE_CONTRACT_INVALID")
    need(classification.get("schema") == V211 and
         classification.get("candidate_source_schema") == V191 and
         classification.get("candidate_source_artifact_id") is None and
         classification.get("status") ==
         "SOURCE_CLASSIFIED_NOT_GENERAL_NATIVE_ACCEPTANCE_OR_UI_PROMOTION" and
         classification.get("simc_effect_reimplemented") is False and
         classification.get("automatic_ui_promotion") is False and
         classification.get("native_calls") == 0 and
         classification.get("network_calls_by_classifier") == 0,
         "V211_SOURCE_CLASSIFICATION_CONTRACT_INVALID")
    build = season.get("game_build")
    revision = season.get("simc_revision")
    need(type(build) is str and bool(build) and
         classification.get("season_game_build") == build,
         "SOURCE_CATALOG_GAME_BUILD_MISMATCH")
    need(type(revision) is str and len(revision) == 40 and
         classification.get("simc_commit") == revision,
         "SOURCE_CATALOG_SIMC_REVISION_MISMATCH")

    input_hashes = season.get("sha256_by_input", {})
    need(type(input_hashes) is dict and set(input_hashes) ==
         {"gear","tier","budget","v189","v190"} and
         all(type(value) is str and len(value)==64 and
             all(ch in "0123456789abcdef" for ch in value)
             for value in input_hashes.values()),
         "V191_INPUT_SOURCE_SHA256_MISSING_OR_INVALID")
    generated_sources = season.get("simc_generated_sources", {})
    need(type(generated_sources) is dict and set(generated_sources) ==
         {"permanent_enchant","temporary_enchant","gem_property"} and
         all(type(row) is dict and row.get("source_build") == build and
             type(row.get("declared_rows")) is int and row["declared_rows"] > 0 and
             type(row.get("sha256")) is str and len(row["sha256"]) == 64 and
             all(ch in "0123456789abcdef" for ch in row["sha256"])
             for row in generated_sources.values()),
         "V191_SIMC_GENERATED_SOURCE_SHA256_MISSING_OR_INVALID")
    source_artifacts = season.get("source_artifacts", {})
    v189 = source_artifacts.get("v189", {})
    v190 = source_artifacts.get("v190", {})
    need(v189.get("schema") == "v189_pinned_simc_effect_registration_candidates_v1"
         and v189.get("simc_commit") == revision
         and v190.get("schema") == "v190_same_build_consumable_item_candidates_v1"
         and v190.get("game_build") == build
         and v190.get("simc_revision") == revision,
         "V191_UPSTREAM_SOURCE_ARTIFACT_IDENTITY_MISMATCH")
    gear = _compile_gear(season)
    tier = _compile_tier(season)
    enchants = _compile_enchants(season, classification)
    related = _related_source_counts(season)
    need(related["gear_item_candidates"] == gear["count"] and
         related["tier_piece_ids"] == tier["piece_count"] and
         related["food_raw_item_candidates"] ==
             len(season["consumables"]["food"]["candidates"]) and
         related["potion_raw_item_candidates"] ==
             len(season["consumables"]["potion"]["candidates"]) and
         related["embellishment_darkmoon_registrations"] ==
             len(season["embellishments"]["registered_effects"]) and
         related["temporary_enchant_entries"] ==
             season["enchants"]["temporary"]["source_rows"] and
         related["gem_property_records"] == season["gem_properties"]["source_count"],
         "V191_RELATED_SOURCE_COUNT_JOIN_DRIFT")

    # v196's existing source-reader contract is embedded as a projection of
    # v191, not a second maintained candidate list. Approval remains false.
    v196_rows = [{
        "token": row["token"],
        "enchant_id": row["enchant_id"],
        "quality_rank": row["quality_rank"],
        "item_class": row["item_class"],
        "inventory_type_mask": row["inventory_type_mask"],
        "item_subclass_mask": row["item_subclass_mask"],
        "approved": False,
    } for row in enchants["items"]]
    v196_source = {
        "schema": V196_SOURCE,
        "status": "SOURCE_OBSERVED_NOT_NATIVE_BUDGET_VERIFIED",
        "season_game_build": build,
        "simc_commit": revision,
        "source_artifact_id": classification.get("candidate_source_artifact_id"),
        "user_selectable": False,
        "related_source_counts": related,
        "related_source_status": "EVIDENCE_ONLY_NO_NEW_USER_OPTIONS",
        "rows": v196_rows,
    }

    consumables = season.get("consumables", {})
    embellishments = season.get("embellishments", {})
    temporary = season.get("enchants", {}).get("temporary", {})
    gem_properties = season.get("gem_properties", {})
    summary = {
        "gear": {
            "count": gear["count"],
            "slot_group_counts": gear["slot_group_counts"],
            "category_counts": gear["category_counts"],
            "unknown_slot_count": gear["unresolved_count"],
        },
        "tier": {
            "class_count": tier["class_count"],
            "piece_count": tier["piece_count"],
        },
        "consumables": {
            "food": len(consumables.get("food", {}).get("candidates", [])),
            "potion": len(consumables.get("potion", {}).get("candidates", [])),
            "automatic_ui_promotion": False,
        },
        "enchants": {
            "total": enchants["count"],
            "groups": enchants["group_counts"],
            "classifier_selectable_count": 0,
            "existing_user_approval_id": 7967,
        },
        "embellishments": {
            "registered_effects": len(embellishments.get("registered_effects", [])),
            "resolved_item_ids": 0,
        },
        "temporary_enchants": {
            "source_rows": temporary.get("source_rows", 0),
            "highest_rank_candidates": len(temporary.get("highest_rank_candidates", [])),
            "slot_join_status": temporary.get("stage"),
        },
        "gem_properties": {
            "source_records": gem_properties.get("source_count", 0),
            "gem_item_ids_resolved": 0,
            "status": gem_properties.get("stage"),
        },
    }
    limitations = [
        "DB2 food/potion candidates are exact item IDs but remain evidence-only, not new user approvals.",
        "Embellishment effect registrations do not resolve crafted item IDs or physical slots.",
        "Temporary enchant tokens do not yet resolve exact user-selectable weapon-hand choices.",
        "Gem property rows are not gem item IDs; gem item/effect joins remain pending.",
        "Weapon enchant inventory mask zero does not certify exact hand or weapon-subclass eligibility.",
        "Static CHMV classification is not generalized exact Native E measurement.",
        "SimC owns all enchant/embellishment/consumable effect execution; this artifact does not reimplement effects.",
    ]
    payload = {
        "schema": SCHEMA,
        "status": "SOURCE_TO_CATALOG_JOINED_NOT_USER_PUBLISHED",
        "game_build": build,
        "expansion_id": season.get("expansion_id"),
        "simc_revision": revision,
        "source_provenance": {
            "v191": {
                "schema": V191,
                "sha256": season_sha,
                "source_artifacts": season.get("source_artifacts"),
                "sha256_by_input": season.get("sha256_by_input"),
                "simc_generated_sources": generated_sources,
            },
            "v211": {
                "schema": V211,
                "sha256": classification_sha,
                "source_files": classification.get("source_files"),
                "simc_item_enchant_pipeline":
                    classification.get("simc_item_enchant_pipeline"),
                "candidate_source_schema":
                    classification.get("candidate_source_schema"),
                "candidate_source_artifact_id":
                    classification.get("candidate_source_artifact_id"),
            },
        },
        "related_source_counts": related,
        "catalog": {
            "gear": gear,
            "tier": tier,
            "consumables": {
                "food": consumables.get("food"),
                "potion": consumables.get("potion"),
                "flask": consumables.get("flask"),
                "augmentation_rune": consumables.get("augmentation_rune"),
                "weapon_oils": consumables.get("weapon_oils"),
                "general_gems": consumables.get("general_gems"),
                "special_diamonds": consumables.get("special_diamonds"),
            },
            "enchants": enchants,
            "embellishments": embellishments,
            "temporary_enchants": temporary,
            "gem_properties": gem_properties,
        },
        "enchant_classification": {
            "schema": V211,
            "status": classification["status"],
            "counts": classification["counts"],
            "rows": classification["rows"],
        },
        "v196_enchant_source": v196_source,
        "catalog_summary": summary,
        "readiness_limitations": limitations,
        "native_calls": 0,
        "network_calls": 0,
        "automatic_ui_promotion": False,
        "selection_state_mutated": False,
        "simc_effect_reimplemented": False,
    }
    digest = sha(canonical(payload).encode("utf8"))
    return {**payload, "manifest_sha256": digest}


def verify_catalog(document):
    need(type(document) is dict and document.get("schema") == SCHEMA and
         document.get("status") == "SOURCE_TO_CATALOG_JOINED_NOT_USER_PUBLISHED" and
         document.get("native_calls") == 0 and
         document.get("network_calls") == 0 and
         document.get("automatic_ui_promotion") is False and
         document.get("selection_state_mutated") is False and
         document.get("simc_effect_reimplemented") is False,
         "V213_CATALOG_CONTRACT_INVALID")
    supplied = document.get("manifest_sha256")
    payload = {k: v for k, v in document.items() if k != "manifest_sha256"}
    need(type(supplied) is str and
         supplied == sha(canonical(payload).encode("utf8")),
         "V213_CATALOG_DIGEST_MISMATCH")
    source = document.get("v196_enchant_source", {})
    rows = source.get("rows")
    items = document.get("catalog", {}).get("enchants", {}).get("items")
    need(type(rows) is list and type(items) is list and
         len(rows) == len(items) == 38,
         "V213_V196_ENCHANT_PROJECTION_COUNT_INVALID")
    projected = {x.get("enchant_id"): x for x in rows}
    joined = {x.get("enchant_id"): x for x in items}
    need(len(projected) == len(joined) == 38,
         "V213_V196_ENCHANT_PROJECTION_DUPLICATE_ID")
    for item_id, row in projected.items():
        item = joined.get(item_id)
        need(item is not None and row.get("token") == item.get("token") and
             row.get("inventory_type_mask") == item.get("inventory_type_mask") and
             row.get("approved") is False and item.get("ui_selectable") is False,
             "V213_V196_ENCHANT_PROJECTION_DRIFT:" + str(item_id))
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--season-catalog", required=True, type=Path)
    parser.add_argument("--enchant-classification", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        season, season_sha = read_json(args.season_catalog)
        classification, classification_sha = read_json(args.enchant_classification)
        result = compile_catalog(season, season_sha, classification,
                                 classification_sha)
        verify_catalog(result)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("V213_SOURCE_TO_CATALOG_BLOCKED", type(exc).__name__, str(exc))
        return 3
    encoded = json.dumps(result, sort_keys=True, ensure_ascii=False,
                         indent=2, allow_nan=False) + "\n"
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        need(out.read_text("utf8") == encoded,
             "EXISTING_V213_CATALOG_CHANGED")
    else:
        out.write_text(encoded, encoding="utf8")
    print("V213_SOURCE_TO_CATALOG_PASS", result["status"],
          result["manifest_sha256"], "NATIVE_0", "NO_UI_PROMOTION",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
