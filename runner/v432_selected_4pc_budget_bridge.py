#!/usr/bin/env python3
"""B8 selected 4pc budget *preflight*: reuse v046/v101/v212/v222.

This is a pure, unadmitted bridge. It does not authorize a user session,
alter a v212 install, manufacture a G observation, or execute Native.
A v212 source owner must verify selected physical items and cache season
before this preliminary delta can be used by the v098/v096 runtime.
"""
from __future__ import annotations

import hashlib
import json

import v046_static_item_cache as static_cache
import v212_environment_manifest as installed_manifest
import v222_season_budget_contract as budget_contract

SCHEMA = "v432_b8_selected_four_tier_budget_preflight_v1"
STATS = budget_contract.STATS
NON_G_OPTIONS = frozenset(("gem_id", "enchant", "enchant_id"))


class SelectedBudgetBlocked(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise SelectedBudgetBlocked(reason)


def _sha(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, ensure_ascii=False,
        separators=(",", ":"), allow_nan=False).encode("utf8")).hexdigest()


def _bare(row, season):
    need(type(row) is dict and set(row) == {
        "slot", "item_id", "ilevel", "options"} and
        type(row["options"]) is dict and
        type(row["item_id"]) is int and row["item_id"] > 0 and
        type(row["ilevel"]) is int and row["ilevel"] > 0,
        "B8_PHYSICAL_ITEM_ROW_INVALID")
    return {
        "season": season,
        "slot": static_cache.normalize_slot(row["slot"]),
        "item_id": row["item_id"],
        "ilevel": row["ilevel"],
        "options": {k: v for k, v in row["options"].items()
                    if k not in NON_G_OPTIONS},
    }


def _native(cache, identity):
    key = static_cache.digest(identity)
    record = cache["variants"].get(key)
    if record is None:
        return None
    need(record.get("source_kind") in {
        "NATIVE_JSON2_RESOLVED_VARIANT",
        "USER_REQUESTED_MANUAL_CORRECTION"} and
        record.get("static_digest") ==
            static_cache.digest(record.get("static")),
        "B8_NATIVE_VARIANT_SOURCE_OR_STATIC_DIGEST_DRIFT")
    vector = record["static"]["secondary"]
    need(type(vector) is dict and set(vector) == set(STATS) and
         all(type(vector[k]) is int and vector[k] >= 0 for k in STATS),
         "B8_NATIVE_VARIANT_SECONDARY_INVALID")
    return {
        "rating": {k: vector[k] for k in STATS},
        "static_digest": record["static_digest"],
        "source_kind": record["source_kind"],
        "native_json_sha256": record.get("metadata", {}).get(
            "native_json_sha256"),
    }


def reconcile(*, baseline_rows, final_rows, final_groups,
              user, class_tier_five, baseline_slot_ids,
              installed_document, original_v191_link, native_cache,
              expected_cache_season):
    """Compute selected physical G delta and special L, without admission.

    The installed G may be a rounded same-season reference: its delta is
    exact *only for cache-attested changed variants*. The projected total
    must never be advertised as exact Native G. The sealed v212 installed
    budget and the 4pc overlay are not modified.
    """
    try:
        installed_manifest.verify_fresh_installed_environment(
            installed_document)
        static_cache.check_cache(native_cache)
    except (ValueError, KeyError, TypeError) as exc:
        raise SelectedBudgetBlocked(
            "B8_INSTALLED_OR_STATIC_CACHE_INVALID:" +
            type(exc).__name__) from exc
    need(type(expected_cache_season) is str and
         native_cache["season"] == expected_cache_season,
         "B8_STATIC_CACHE_SEASON_NOT_SOURCE_BOUND")
    doc = installed_document
    link = original_v191_link
    need(type(link) is dict and link.get("schema") ==
         "v098_v191_original_gear_tier_link_v1" and
         link.get("status") ==
         "ORIGINAL_GEAR_TIER_RAW_SHA_LINKED_PREVIEW_ONLY" and
         type(link.get("raw_source_sha256")) is dict and
         set(link["raw_source_sha256"]) == {"gear", "tier"} and
         all(type(x) is str and len(x) == 64 for x in
             link["raw_source_sha256"].values()) and
         link.get("source_catalog_manifest_sha256") ==
             doc["source_catalog_manifest_sha256"] and
         link.get("source_catalog_artifact_sha256") ==
             doc["source_catalog_artifact_sha256"],
         "B8_V191_AND_V212_ORIGINAL_SOURCE_IDENTITY_DRIFT")
    need(type(user) is dict and type(user.get("target")) is dict and
         type(user.get("special_items")) is list and
         type(user.get("embellishments")) is list and
         bool(user["special_items"] or user["embellishments"]) and
         user["target"].get("ilevel") == doc["target_ilevel"] and
         (user["target"].get("final_T") is None or
          type(user["target"]["final_T"]) is int),
         "B8_USER_SELECTED_VARIANT_AND_TARGET_REQUIRED")
    need(type(baseline_rows) is dict and
         type(final_rows) is dict and
         type(final_groups) is dict and
         type(baseline_slot_ids) is dict and
         set(baseline_rows) == set(final_rows) and
         all(row["slot"] == slot and
             row["ilevel"] == doc["target_ilevel"]
             for slot, row in baseline_rows.items()) and
         all(row["slot"] == slot and
             row["ilevel"] == doc["target_ilevel"]
             for slot, row in final_rows.items()),
         "B8_PROFILE_PHYSICAL_SLOTS_OR_LEVEL_DRIFT")
    base_ids = {
        slot: row["item_id"] for slot, row in baseline_rows.items()
        if not slot.startswith("trinket")}
    need(base_ids == baseline_slot_ids,
         "B8_V232_INSTALLED_G_BASELINE_ITEM_ID_DRIFT")
    need(type(class_tier_five) is dict and
         set(class_tier_five) == {
             "head", "shoulders", "chest", "hands", "legs"},
         "B8_CLASS_FIVE_TIER_SOURCE_REQUIRED")
    tier_slots = sorted(
        slot for slot, group in final_groups.items()
        if group == "tier")
    need(len(tier_slots) == 4 and
         all(slot in class_tier_five and
             final_rows[slot]["item_id"] == class_tier_five[slot]
             for slot in tier_slots),
         "B8_SELECTED_PHYSICAL_FOUR_TIER_DRIFT")

    original = doc["v222_reconciled_budget"]
    need(type(original) is dict and
         original.get("reference_G") == doc["official_G"] and
         original.get("effective_G") == doc["official_effective_G"] and
         original.get("J") == doc["official_J"] and
         original.get("F") == doc["official_F"] and
         original.get("fixed_O") == doc["official_O"] and
         original.get("base_B") == doc["official_B"] and
         doc["official_B"] == doc["official_effective_G"] +
             doc["official_J"] + doc["official_F"] and
         original.get("fixed_L") == {k: 0 for k in STATS},
         "B8_BASE_INSTALLED_BUDGET_OR_L_NOT_REBASABLE")
    fixed_E = budget_contract._vector(original.get("fixed_E"), "E")
    fixed_O = budget_contract._vector(doc["official_O"], "O")
    changed = []
    missing = []
    observed = {}
    season = native_cache["season"]

    def lookup(row):
        ident = _bare(row, season)
        key = static_cache.digest(ident)
        if key not in observed:
            found = _native(native_cache, ident)
            observed[key] = found
            if found is None:
                missing.append({
                    "slot": row["slot"], "item_id": row["item_id"],
                    "identity": ident})
        return observed[key]

    for slot in sorted(base_ids):
        before = _bare(baseline_rows[slot], season)
        after = _bare(final_rows[slot], season)
        if before != after:
            if (slot in ("main_hand", "off_hand") and
                    slot in user.get("oil_hands", [])):
                need(False,
                     "B8_SELECTED_WEAPON_OIL_APPLICABILITY_RECHECK_REQUIRED")
            old_rating = lookup(baseline_rows[slot])
            new_rating = lookup(final_rows[slot])
            changed.append({
                "slot": slot,
                "previous_id": baseline_rows[slot]["item_id"],
                "selected_id": final_rows[slot]["item_id"],
                "previous_static": old_rating,
                "selected_static": new_rating})
    L = {k: 0 for k in STATS}
    seen = set()
    for chosen in user["special_items"]:
        need(type(chosen) is dict and
             chosen.get("slot") in final_rows and
             chosen["slot"] not in seen and
             final_rows[chosen["slot"]]["item_id"] ==
                 chosen.get("item_id") and
             final_groups.get(chosen["slot"]) in ("special", "tier"),
             "B8_SELECTED_SPECIAL_PHYSICAL_PROFILE_DRIFT")
        seen.add(chosen["slot"])
        fixed = lookup(final_rows[chosen["slot"]])
        if fixed is not None:
            for stat in STATS:
                L[stat] += fixed["rating"][stat]
    need(len({x["slot"] for x in user["embellishments"]}) ==
         len(user["embellishments"]) and
         all(type(x) is dict and
             x.get("slot") in final_rows and
             final_rows[x["slot"]]["item_id"] == x.get("item_id") and
             final_groups.get(x["slot"]) == "crafted"
             for x in user["embellishments"]),
         "B8_CRAFTED_PHYSICAL_PROFILE_DRIFT")
    missing = sorted({static_cache.digest(x["identity"]): x
                      for x in missing}.values(),
                     key=lambda x: (x["slot"], x["item_id"]))
    base = {
        "schema": SCHEMA,
        "status": ("B8_EXACT_CHANGED_STATIC_VARIANTS_PENDING"
                   if missing else
                   "B8_SELECTED_PHYSICAL_G_L_RECONCILED_NOT_ADMITTED"),
        "game_build": doc["game_build"],
        "target_ilevel": doc["target_ilevel"],
        "installed_v212_manifest_sha256": doc["manifest_sha256"],
        "original_v191_raw_gear_tier_sha256":
            dict(link["raw_source_sha256"]),
        "static_cache_season": season,
        "four_tier_slots": tier_slots,
        "changed_physical_slots": changed,
        "missing_exact_native_variants": missing,
        "J": doc["official_J"],
        "F": doc["official_F"],
        "fixed_E": fixed_E,
        "fixed_O": fixed_O,
        "crafted_first_split_is_not_L": True,
        "changed_variants_need_no_new_native_when_cached": True,
        "installed_environment_unchanged": True,
        "native_calls": 0, "network_calls": 0,
        "runtime_native_authorized": False,
        "user_session_created": False,
    }
    if missing:
        return base
    delta = sum(
        sum(entry["selected_static"]["rating"].values()) -
        sum(entry["previous_static"]["rating"].values())
        for entry in changed)
    G = doc["official_G"] + delta
    effective_G = doc["official_effective_G"] + delta
    B = (effective_G + doc["official_J"] + doc["official_F"]
         if user["target"]["final_T"] is None else
         user["target"]["final_T"] - sum(fixed_O.values()))
    T = B + sum(fixed_O.values())
    need(G > 0 and effective_G >= sum(L.values()) +
         sum(fixed_E.values()) and
         B >= doc["official_J"] + doc["official_F"] +
              sum(L.values()) + sum(fixed_E.values()),
         "B8_G_L_E_OR_MANUAL_T_FIXED_MINIMA_INFEASIBLE")
    result = {**base,
              "G_projected_reference_not_native_exact": G,
              "effective_G_projected": effective_G,
              "changed_slots_exact_static_delta": delta,
              "fixed_L_in_G_once": L,
              "base_B": B, "final_T": T,
              "manual_final_T_authoritative":
                  user["target"]["final_T"] is not None,
              "reference_G_may_be_rounded": True}
    result["selected_budget_identity_sha256"] = _sha({
        "installed_v212_manifest_sha256":
            doc["manifest_sha256"],
        "original_v191_raw_gear_tier_sha256":
            link["raw_source_sha256"],
        "native_variants": changed,
        "selected_special_L": L,
        "target": user["target"],
        "G": G, "B": B, "T": T,
        "J": result["J"], "F": result["F"],
        "E": fixed_E, "O": fixed_O,
        "four_tier_slots": tier_slots})
    return result
