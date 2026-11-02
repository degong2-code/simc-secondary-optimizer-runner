#!/usr/bin/env python3
"""v227: resolve request-specific G observations from existing v046 cache.

No new static calculator or Native runner. v226 selects the physical source
gear; v046 owns exact static item variants, revision-insensitive inside the
same season. Numeric sums are observations, not independently authenticated
new-build G until build/profile/equipment Native evidence is connected.
Never interpret missing variant as 0, and NEVER inherit J138/F165 from the
historical cache's convenience sum.
"""
from __future__ import annotations
import argparse
import json
import pathlib
import re

try:
    from . import v046_static_item_cache as static_cache
    from . import v226_representative_native_g_work_order as planner
except ImportError:
    import v046_static_item_cache as static_cache
    import v226_representative_native_g_work_order as planner

SCHEMA = "v227_exact_variant_cached_G_observation_v1"
SHA = re.compile(r"[a-f0-9]{64}\Z")
REV = re.compile(r"[a-f0-9]{7,40}\Z")


class GObservationBlocked(ValueError):
    pass


def need(condition,code):
    if not condition:
        raise GObservationBlocked(code)


def observe(*, work_order, cache):
    """Read-only; enough data to request ONLY missing exact Native variants."""
    need(type(work_order) is dict and
         work_order.get("schema") == planner.SCHEMA and
         work_order.get("status") ==
             "WAIT_EXACT_SOURCE_PROFILE_AND_NATIVE_STATIC_G" and
         work_order.get("environment_ready") is False and
         work_order.get("verified_G") is False and
         work_order.get("G") is None,
         "V227_SOURCE_G_WORK_ORDER_REQUIRED")
    original = {k:v for k,v in work_order.items() if k != "receipt_sha256"}
    need(work_order.get("receipt_sha256") == planner.digest(original),
         "V227_WORK_ORDER_SHA_DRIFT")
    native = work_order["measurement_request"]["native_input"]
    need(planner.digest(native) == work_order["work_identity_sha256"] and
         native.get("season") == work_order["season"] and
         native.get("game_build") == work_order["game_build"] and
         native.get("slot_item_ids") == work_order["selected_source_slots"] and
         native.get("target_ilevel") == work_order["target_ilevel"] and
         native.get("excluded_slot_rules") == [
             "TRINKET_FIXED_STATS_OUTSIDE_G",
             "NO_J_F_OR_TEMPORARY_OIL_IN_G",
             "NO_USER_CURRENT_EQUIPMENT",
         ],
         "V227_MEASUREMENT_REQUEST_CHANGED")
    need(type(cache) is dict, "V227_CACHE_OBJECT_REQUIRED")
    try:
        static_cache.check_cache(cache)
    except (static_cache.CacheBlocked, KeyError, TypeError, ValueError) as exc:
        raise GObservationBlocked(
            "V227_EXISTING_V046_CACHE_INVALID") from exc
    need(cache["season"] == work_order["season"],
         "V227_STATIC_CACHE_SEASON_DRIFT")
    slots = work_order["selected_source_slots"]
    need(type(slots) is dict and len(slots) in (13,14),
         "V227_REPRESENTATIVE_SLOTS_INCOMPLETE")
    looked_up = []
    missing = []
    for slot,item_id in sorted(slots.items()):
        identity = {
            "season": work_order["season"], "slot":
                static_cache.normalize_slot(slot),
            "item_id": item_id, "ilevel": work_order["target_ilevel"],
            "options": {},
        }
        entry=cache["variants"].get(static_cache.digest(identity))
        if entry is None:
            missing.append({
                "slot":slot, "item_id":item_id,
                "ilevel":work_order["target_ilevel"],
                "reason":"EXACT_NATIVE_VARIANT_CACHE_MISS_NOT_ZERO",
            })
            continue
        need(entry.get("source_kind")=="NATIVE_JSON2_RESOLVED_VARIANT" and
             entry.get("identity")==identity and
             entry.get("modifiers_present") is False and
             entry.get("eligible_for_gear_sum_only_in_exact_same_variant") is True,
             "V227_NON_NATIVE_OR_MODIFIED_VARIANT_NOT_G_BASELINE")
        metadata = entry.get("metadata")
        need(type(metadata) is dict and
             type(metadata.get("native_json_sha256")) is str and
             SHA.fullmatch(metadata["native_json_sha256"]) is not None and
             type(metadata.get("native_revision")) is str and
             REV.fullmatch(metadata["native_revision"]) is not None,
             "V227_NATIVE_ORIGIN_RECORD_INCOMPLETE")
        looked_up.append((identity,entry))
    status = ("WAIT_EXACT_NATIVE_STATIC_VARIANTS" if missing else
              "EXACT_NATIVE_STATIC_CACHE_G_OBSERVED_PENDING_BUILD_PROOF")
    g_vec = None
    g_total = None
    if not missing:
        # Reuse existing v046's invariant, and deliberately ignore its
        # original-Midnight J/F convenience fields.
        try:
            summary=static_cache.selected_gear_sum(
                cache,[ident for ident,_ in looked_up])
        except (static_cache.CacheBlocked, KeyError,TypeError) as exc:
            raise GObservationBlocked(
                "V227_EXISTING_G_SUM_CONTRACT_BLOCKED") from exc
        g_vec=summary["G_vector"]
        g_total=summary["G_native_static_including_selected_modifiers"]
        need(g_total == sum(g_vec.values()) and
             g_total > 0 and
             all(type(g_vec[k]) is int and g_vec[k] >= 0
                 for k in static_cache.STATS),
             "V227_STATIC_G_ARITHMETIC_INVALID")
    result = {
        "schema": SCHEMA,
        "status": status,
        "work_identity_sha256": work_order["work_identity_sha256"],
        "source_work_receipt_sha256": work_order["receipt_sha256"],
        "game_build": work_order["game_build"],
        "season": work_order["season"],
        "target_ilevel": work_order["target_ilevel"],
        "required_static_variants": len(slots),
        "exact_native_cache_variants_found": len(looked_up),
        "missing_variant_requests": missing,
        "observed_G_vector_if_complete": g_vec,
        "observed_G_total_if_complete": g_total,
        "G": None,
        "J": None, "F": None, "O": None, "B": None, "T": None,
        "why_G_not_approved": [
            "V046_ITEM_CACHE_DOES_NOT_ATTEST_GAME_BUILD_BY_VARIANT",
            "REPRESENTATIVE_PROFILE_NATIVE_PROOF_NOT_BOUND",
            "J_F_O_NEW_SEASON_RATINGS_STILL_UNPROVEN",
        ],
        "static_cache_revision_change_alone_does_not_invalidate": True,
        "native_calls": 0,
        "cache_mutations": 0,
        "environment_ready": False,
    }
    return {**result, "receipt_sha256": planner.digest(result)}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bundle-dir",type=pathlib.Path,required=True)
    p.add_argument("--event",required=True,choices=("season_change","expansion_change","mid_patch"))
    p.add_argument("--previous-game-build",required=True)
    p.add_argument("--target-ilevel",type=int,required=True)
    p.add_argument("--class",dest="cls",required=True)
    p.add_argument("--spec",required=True)
    p.add_argument("--static-cache",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    args=p.parse_args(argv)
    work=planner.make_work_order(
        bundle_dir=args.bundle_dir, event=args.event,
        previous_game_build=args.previous_game_build,
        target_ilevel=args.target_ilevel,
        character_class=args.cls, specialization=args.spec)
    try:
        cache=static_cache.load(args.static_cache,season=work["season"])
    except (static_cache.CacheBlocked, ValueError, OSError) as exc:
        raise GObservationBlocked(
            "V227_EXISTING_STATIC_CACHE_LOAD_FAILED") from exc
    result=observe(work_order=work,cache=cache)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(
        result,indent=2,sort_keys=True,ensure_ascii=False)+"\n",
        encoding="utf8")
    print("V227_G_STATIC_REUSE",
          result["status"],
          result["exact_native_cache_variants_found"],
          result["required_static_variants"],
          "G_NOT_PROMOTED_NATIVE0",flush=True)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
