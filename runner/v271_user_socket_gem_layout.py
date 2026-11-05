#!/usr/bin/env python3
"""P3-BZ: opt-in physical socket/gem composition, never an admission gate.

Uses the existing v101 four-color ID selector. A caller must separately prove
which sockets and highest-quality gem IDs are valid for the current season.
This stage does not authenticate game eligibility or calculate DPS.
"""
from __future__ import annotations

import copy
import v101_common_representative_equipment as representative

SCHEMA = "v271_user_socket_gem_layout_stage_v1"
DIAMONDS = frozenset((240983, 240967))
FIELDS = frozenset(("socket_counts", "special_gem_id", "special_slot",
                    "ordinary_gem_ids"))


def arrange(rows, plan, need, *, observed_rating_per_ordinary=None):
    """Return independent physical rows and an explicitly UNADMITTED J preview.

    socket_counts maps chosen physical slots to final gem counts (zero allowed).
    It is a user override, not evidence that a socket can exist in the game.
    ordinary_gem_ids are actual source-observed physical IDs in slot order.
    The existing v101 selector replaces duplicated colors for 240967.
    """
    need(type(rows) is dict and rows, "SOCKET_ROWS_REQUIRED")
    need(type(plan) is dict and set(plan) == FIELDS,
         "SOCKET_PLAN_FIELDS")
    physical = set(rows) - {"trinket1", "trinket2"}
    counts = plan["socket_counts"]
    need(type(counts) is dict and bool(counts) and
         all(type(slot) is str and slot in physical and
             type(count) is int and 0 <= count <= 16
             for slot, count in counts.items()),
         "SOCKET_COUNTS_PHYSICAL_SLOTS_REQUIRED")
    total = sum(counts.values())
    need(1 <= total <= 64, "SOCKET_TOTAL_INPUT_BOUNDS")
    special = plan["special_gem_id"]
    where = plan["special_slot"]
    need(type(special) is int and special in DIAMONDS and
         type(where) is str and counts.get(where, 0) >= 1,
         "SOCKET_SINGLE_SPECIAL_GEM_POSITION_REQUIRED")
    ordinary = plan["ordinary_gem_ids"]
    source_colors = representative.SOURCE_GEM_COLOR
    need(type(ordinary) is list and len(ordinary) == total - 1 and
         all(type(g) is int and g in source_colors and
             g not in DIAMONDS for g in ordinary),
         "SOCKET_ORDINARY_GEMS_SOURCE_OBSERVED_AND_COUNTED")
    need(observed_rating_per_ordinary is None or
         (type(observed_rating_per_ordinary) is int and
          observed_rating_per_ordinary >= 0),
         "SOCKET_OBSERVED_GEM_RATING_INVALID")

    staged = copy.deepcopy(rows)
    for slot in physical:
        staged[slot]["options"].pop("gem_id", None)
    cursor = iter(ordinary)
    for slot in sorted(counts):
        chosen = []
        if slot == where:
            chosen.append(special)
        chosen.extend(next(cursor) for _ in
                      range(counts[slot] - (1 if slot == where else 0)))
        if chosen:
            staged[slot]["options"]["gem_id"] = "/".join(map(str, chosen))

    if special == 240967 and total - 1 >= 4:
        representative.ensure_representative_gem_colors(
            staged, special, need, ordinary_count=total - 1,
            diamond_slot=where, allow_partial=True)
    actual = []
    all_diamonds = 0
    for slot, row in staged.items():
        tokens = row["options"].get("gem_id", "").split("/")
        for index, token in enumerate(tokens):
            if not token:
                continue
            gem = int(token)
            all_diamonds += gem in DIAMONDS
            if slot == where and index == 0:
                need(gem == special, "SOCKET_SPECIAL_GEM_NOT_EQUIPPED")
            elif gem in DIAMONDS:
                need(False, "SOCKET_SECOND_SPECIAL_GEM")
            elif slot in physical:
                actual.append(gem)
    need(all_diamonds == 1 and len(actual) == total - 1,
         "SOCKET_ACTUAL_PHYSICAL_GEM_COUNT_DRIFT")
    colors = {source_colors[g] for g in actual}
    complete = special == 240967 and set(
        representative.FOUR_COLOR_GEMS).issubset(colors)
    return staged, {
        "schema": SCHEMA,
        "status": "PHYSICAL_GEMS_STAGED_SOURCE_AND_SOCKET_PROOFS_PENDING",
        "socket_counts": dict(counts),
        "socket_total": total,
        "ordinary_count": len(actual),
        "special_gem_id": special,
        "special_slot": where,
        "ordinary_gem_ids": list(actual),
        "ordinary_colors_observed": sorted(colors),
        "four_colors_physically_present": complete,
        "max_four_color_effect_claimed": False,
        "candidate_J_unadmitted": (
            None if observed_rating_per_ordinary is None else
            len(actual) * observed_rating_per_ordinary),
        "game_socket_applicability_verified": False,
        "highest_quality_gem_ids_verified_for_new_season": False,
        "CHMV_J_source_authenticated": False,
        "environment_ready": False,
        "native_calls": 0,
    }



def reconcile_observed_J(layout, per_gem_rating_by_id, need):
    """Match static J candidate against actual placed ordinary gem IDs.

    Only arithmetic; no independent item quality, source provenance, socket
    legality, or SimC buffed_stats +1 certification is performed here.
    """
    need(type(layout) is dict and layout.get("schema")==SCHEMA and
         layout.get("status")==
         "PHYSICAL_GEMS_STAGED_SOURCE_AND_SOCKET_PROOFS_PENDING",
         "GEM_J_PHYSICAL_LAYOUT_STAGE_REQUIRED")
    ids=layout.get("ordinary_gem_ids")
    counts=layout.get("socket_counts")
    need(type(ids) is list and
         all(type(gem) is int and gem in representative.SOURCE_GEM_COLOR
             for gem in ids) and
         type(counts) is dict and
         all(type(n) is int and n>=0 for n in counts.values()) and
         layout.get("ordinary_count")==len(ids) and
         layout.get("socket_total")==len(ids)+1 and
         sum(counts.values())==len(ids)+1 and
         layout.get("special_gem_id") in DIAMONDS and
         type(layout.get("special_slot")) is str and
         counts.get(layout["special_slot"],0)>=1,
         "GEM_J_LAYOUT_COUNTS_OR_IDS_DRIFT")
    need(type(per_gem_rating_by_id) is dict and
         set(per_gem_rating_by_id)=={str(gem) for gem in ids} and
         all(type(n) is int and 0<n<=10000
             for n in per_gem_rating_by_id.values()),
         "GEM_J_EXACT_PHYSICAL_ITEM_RATINGS_REQUIRED")
    return {
        "status":"PHYSICAL_GEM_J_ARITHMETIC_UNADMITTED",
        "source_layout_schema":SCHEMA,
        "ordinary_count":len(ids),
        "physical_gem_item_ids":list(ids),
        "J_candidate_unadmitted":sum(
            per_gem_rating_by_id[str(gem)] for gem in ids),
        "source_quality_and_applicability_authenticated_here":False,
        "game_socket_legality_verified_here":False,
        "environment_ready":False,
        "native_calls":0,
    }
