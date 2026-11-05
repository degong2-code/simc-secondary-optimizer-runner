#!/usr/bin/env python3
"""P3-BZ: opt-in physical socket/gem composition, never an admission gate.

Uses the existing v101 four-color ID selector. A caller must separately prove
how many sockets really exist on chosen equipment, and which gem IDs are
valid for the season. Any existing socket accepts an ordinary or special gem:
no gem-color/type-to-socket compatibility gate. This stage does not
authenticate real socket existence or calculate DPS.
"""
from __future__ import annotations

import copy
import v101_common_representative_equipment as representative

SCHEMA = "v271_user_socket_gem_layout_stage_v1"
DIAMONDS = frozenset((240983, 240967))
FIELDS = frozenset(("socket_counts", "special_gem_id", "special_slot",
                    "ordinary_gem_ids"))
# An opt-in list of physical IDs from the ORIGINAL, sealed v221 join.
# v216 MUST compare it with that exact same-build source before even a
# source-only J preview is used. This list itself grants no admission.
SOURCE_IDS_FIELD = "source_observed_gem_item_ids"


def arrange(rows, plan, need, *, observed_rating_per_ordinary=None):
    """Return independent physical rows and an explicitly UNADMITTED J preview.

    socket_counts maps chosen physical slots to final gem counts (zero allowed).
    It is a user override, not evidence that a socket can exist in the game.
    ordinary_gem_ids are actual source-observed physical IDs in slot order.
    The existing v101 selector replaces duplicated colors for 240967.
    """
    need(type(rows) is dict and rows, "SOCKET_ROWS_REQUIRED")
    source_mode=(type(plan) is dict and SOURCE_IDS_FIELD in plan)
    need(type(plan) is dict and
         (set(plan)==FIELDS or set(plan)==FIELDS|{SOURCE_IDS_FIELD}),
         "SOCKET_PLAN_FIELDS")
    source_ids=None
    if source_mode:
        selected=plan[SOURCE_IDS_FIELD]
        need(type(selected) is list and 1<=len(selected)<=64 and
             all(type(g) is int and g>0 for g in selected) and
             len(set(selected))==len(selected),
             "SOCKET_V221_SOURCE_ITEM_ID_SELECTION_INVALID")
        source_ids=set(selected)
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
    need(type(special) is int and special>0 and
         (special in source_ids if source_mode else special in DIAMONDS) and
         type(where) is str and counts.get(where, 0) >= 1,
         "SOCKET_SINGLE_SPECIAL_GEM_POSITION_REQUIRED")
    ordinary = plan["ordinary_gem_ids"]
    # SOURCE_GEM_COLOR is used only for the existing four-color special
    # effect; it is NOT a restriction on which open socket accepts a gem.
    source_colors = representative.SOURCE_GEM_COLOR
    need(type(ordinary) is list and len(ordinary) == total - 1 and
         all(type(g) is int and g!=special and g not in DIAMONDS and
             (g in source_ids if source_mode else g in source_colors)
             for g in ordinary) and
         (not source_mode or source_ids==set(ordinary)|{special}),
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

    # Existing Midnight four-color selection is valid ONLY for the
    # historically source-observed colored IDs. A new same-build ordinary
    # gem must not be rewritten into an old-season fallback item ID.
    if (special == 240967 and total - 1 >= 4 and
            all(g in source_colors for g in ordinary)):
        representative.ensure_representative_gem_colors(
            staged, special, need, ordinary_count=total - 1,
            diamond_slot=where, allow_partial=True)
    actual = []
    special_count = 0
    # In the new source-scoped mode, the physical J identity follows
    # sorted socket slots, matching the existing v098 reconciliation.
    # Keep legacy insertion-order receipts BYTE IDENTICAL.
    scan=(staged.items() if not source_mode else
          ((slot,staged[slot]) for slot in sorted(staged)))
    for slot, row in scan:
        tokens = row["options"].get("gem_id", "").split("/")
        for index, token in enumerate(tokens):
            if not token:
                continue
            gem = int(token)
            special_count += gem==special
            if slot == where and index == 0:
                need(gem == special, "SOCKET_SPECIAL_GEM_NOT_EQUIPPED")
            elif gem==special or gem in DIAMONDS:
                need(False, "SOCKET_SECOND_SPECIAL_GEM")
            elif slot in physical:
                actual.append(gem)
    need(special_count == 1 and len(actual) == total - 1,
         "SOCKET_ACTUAL_PHYSICAL_GEM_COUNT_DRIFT")
    colors = {source_colors[g] for g in actual if g in source_colors}
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
        **({SOURCE_IDS_FIELD: sorted(source_ids)}
           if source_mode else {}),
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
    source_ids=layout.get(SOURCE_IDS_FIELD)
    source_mode=source_ids is not None
    need(not source_mode or
         (type(ids) is list and type(source_ids) is list and
          1<=len(source_ids)<=64 and
          all(type(g) is int and g>0 for g in source_ids) and
          len(set(source_ids))==len(source_ids) and
          set(source_ids)==set(ids)|{layout.get("special_gem_id")}),
         "GEM_J_V221_SOURCE_ITEM_ID_SELECTION_DRIFT")
    need(type(ids) is list and
         all(type(gem) is int and gem not in DIAMONDS and
             (gem in source_ids if source_mode else
              gem in representative.SOURCE_GEM_COLOR)
             for gem in ids) and
         type(counts) is dict and
         all(type(n) is int and n>=0 for n in counts.values()) and
         layout.get("ordinary_count")==len(ids) and
         layout.get("socket_total")==len(ids)+1 and
         sum(counts.values())==len(ids)+1 and
         ((type(layout.get("special_gem_id")) is int and
           layout["special_gem_id"]>0 and
           layout["special_gem_id"] in source_ids) if source_mode else
          layout.get("special_gem_id") in DIAMONDS) and
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
