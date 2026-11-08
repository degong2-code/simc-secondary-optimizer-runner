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



# Nominal ordinary secondary-stat types, not special-gem effects.
ORDINARY_FOUR_STATS = (
    "crit_rating", "haste_rating", "mastery_rating", "versatility_rating")


def ordinary_four_stat_default(*, observed_by_stat, socket_total,
                               special_gem_id, need):
    """Select 1 of each ordinary CHMV type from a sealed same-build join.

    v268 projects these nominal source-only candidates from v221/v266.
    SimC owns runtime effects; no special gem classification happens here.
    """
    need(type(socket_total) is int and 5<=socket_total<=64,
         "SOCKET_FOUR_ORDINARY_TYPES_NEED_FIVE_PHYSICAL_SOCKETS")
    need(type(special_gem_id) is int and special_gem_id>0,
         "SOCKET_EXISTING_SPECIAL_ID_REQUIRED")
    need(type(observed_by_stat) is dict and
         set(observed_by_stat)==set(ORDINARY_FOUR_STATS),
         "SOCKET_FOUR_ORDINARY_STAT_SOURCES_REQUIRED")
    ids=[]
    for stat in ORDINARY_FOUR_STATS:
        candidate=observed_by_stat[stat]
        need(type(candidate) is dict and
             set(candidate)=={"item_id","raw_nominal_points"} and
             type(candidate["item_id"]) is int and
             candidate["item_id"]>0 and
             candidate["item_id"]!=special_gem_id and
             candidate["item_id"] not in DIAMONDS and
             type(candidate["raw_nominal_points"]) is int and
             candidate["raw_nominal_points"]>0,
             "SOCKET_FOUR_ORDINARY_SOURCE_CANDIDATE_INVALID")
        ids.append(candidate["item_id"])
    need(len(set(ids))==4,"SOCKET_FOUR_ORDINARY_PHYSICAL_IDS_REQUIRED")
    # Fixed repeated order. The 26-DPS optimizer never chooses gem types.
    return [ids[i%4] for i in range(socket_total-1)]


def nominal_four_stat_from_season_source(*, source, game_build,
                                         socket_total, special_gem_id, need):
    """Project independently sourced ordinary gem TOTAL rating into existing J.

    The upstream season owner supplies four physical IDs and one nominal
    CHMV total per ID. The source may describe the two stats separately,
    but neither v266 EffectPointsMin nor a SimC delta is needed to sum J.
    A source SHA is an identity, NOT proof of quality or admission.
    """
    import re
    need(type(source) is dict and
         set(source)=={"game_build","source_sha256","by_stat"} and
         source.get("game_build")==game_build and
         type(source.get("source_sha256")) is str and
         re.fullmatch(r"[0-9a-f]{64}",source["source_sha256"]) is not None,
         "SOCKET_NOMINAL_J_SAME_BUILD_SOURCE_IDENTITY_REQUIRED")
    by_stat=source["by_stat"]
    need(type(by_stat) is dict and
         set(by_stat)==set(ORDINARY_FOUR_STATS) and
         all(type(row) is dict and set(row)=={"item_id","rating"} and
             type(row["item_id"]) is int and row["item_id"]>0 and
             type(row["rating"]) is int and 0<row["rating"]<=10000
             for row in by_stat.values()),
         "SOCKET_NOMINAL_J_FOUR_PHYSICAL_TOTALS_REQUIRED")
    normalized={stat:{"item_id":row["item_id"],
                      "raw_nominal_points":row["rating"]}
                for stat,row in by_stat.items()}
    ordinary=ordinary_four_stat_default(
        observed_by_stat=normalized,socket_total=socket_total,
        special_gem_id=special_gem_id,need=need)
    rating={str(row["item_id"]):row["rating"]
            for row in by_stat.values()}
    return {"ordinary_gem_ids":ordinary,
            "rating_by_id":rating,
            "J_candidate_unadmitted":sum(rating[str(i)] for i in ordinary),
            "season_source_sha256":source["source_sha256"],
            "source_build":game_build,
            "simc_gem_delta_required":False,
            "v266_raw_static_rating_required":False,
            "environment_ready":False,"native_calls":0}


def load_packaged_season_nominal_source(*, game_build, need,
                                        source_folder=None):
    """Return existing season item-tooltip TOTALS for v216's original J path.

    No HTTP or SimC execution. The exact source bytes are SHA-bound, while
    actual v221 same-build item ownership, quality and v220 admission remain
    the existing environment engine's responsibility. Absent season data
    is PENDING, never zero and never a historical-season substitution.
    """
    import hashlib
    import json
    import pathlib
    import re

    need(type(game_build) is str and
         re.fullmatch(r"[0-9]+(?:[.][0-9]+){3}", game_build) is not None,
         "SOCKET_NOMINAL_SEASON_GAME_BUILD_INVALID")
    folder=(pathlib.Path(source_folder) if source_folder is not None else
            pathlib.Path(__file__).resolve().parents[1]/
            "data"/"season_ordinary_gem_nominal")
    path=folder/(game_build+".json")
    if not path.exists():
        return None
    need(path.is_file() and not path.is_symlink() and
         0<path.stat().st_size<=50000,
         "SOCKET_NOMINAL_SEASON_SOURCE_FILE_INVALID")
    raw=path.read_bytes()
    try:
        payload=json.loads(raw.decode("utf8"))
    except (ValueError,UnicodeError) as exc:
        raise ValueError("SOCKET_NOMINAL_SEASON_JSON_INVALID") from exc
    need(type(payload) is dict and
         set(payload)=={"schema","game_build","season_key",
                        "by_stat","source_scope"} and
         payload["schema"]=="season_ordinary_gem_nominal_v1" and
         payload["game_build"]==game_build and
         type(payload["season_key"]) is str and
         bool(payload["season_key"]) and
         payload["source_scope"]=="STATIC_NOMINAL_SOURCE_ONLY_NOT_ADMISSION",
         "SOCKET_NOMINAL_SEASON_SOURCE_SCOPE_INVALID")
    by_stat=payload["by_stat"]
    need(type(by_stat) is dict and
         set(by_stat)==set(ORDINARY_FOUR_STATS),
         "SOCKET_NOMINAL_SEASON_FOUR_TYPES_REQUIRED")
    totals={}
    for stat in ORDINARY_FOUR_STATS:
        item=by_stat[stat]
        need(type(item) is dict and
             set(item)=={"item_id","quality_rank",
                         "secondary_components","evidence_url"} and
             type(item["item_id"]) is int and item["item_id"]>0 and
             type(item["quality_rank"]) is int and
             item["quality_rank"]>0 and
             type(item["evidence_url"]) is str and
             item["evidence_url"].startswith("https://") and
             len(item["evidence_url"])<=512,
             "SOCKET_NOMINAL_SEASON_ITEM_FIELDS_INVALID")
        components=item["secondary_components"]
        need(type(components) is dict and len(components)==2 and
             stat in components and
             set(components)<=set(ORDINARY_FOUR_STATS) and
             all(type(n) is int and 0<n<=10000
                 for n in components.values()) and
             components[stat]>min(components.values()),
             "SOCKET_NOMINAL_SEASON_DUAL_STAT_SOURCE_REQUIRED")
        totals[stat]={"item_id":item["item_id"],
                      "rating":sum(components.values())}
    need(len({row["item_id"] for row in totals.values()})==4,
         "SOCKET_NOMINAL_SEASON_DISTINCT_PHYSICAL_IDS_REQUIRED")
    return {"game_build":game_build,
            "source_sha256":hashlib.sha256(raw).hexdigest(),
            "by_stat":totals}


# Declared SimC gem_id placement: no socket-granting item or spell is needed.
FULL_SOCKET_SLOT_ORDER=("head","neck","finger1","finger2","wrists",
                        "waist","feet","hands","legs","shoulders","chest",
                        "back","main_hand","off_hand")

def declared_full_socket_counts(*,available_slots,socket_total,need):
    """Fixed gem_id positions over source-observed representative slot names.

    This is a profile declaration, not proof that equipment has sockets.
    Item IDs are still authenticated by the original v232 source path.
    """
    need(type(available_slots) in (list,tuple) and bool(available_slots)
         and all(type(s) is str for s in available_slots)
         and len(set(available_slots))==len(available_slots)
         and type(socket_total) is int and 5<=socket_total<=64,
         "SOCKET_DECLARED_TARGET_AND_PHYSICAL_SLOTS_REQUIRED")
    ordered=[s for s in FULL_SOCKET_SLOT_ORDER if s in available_slots]
    need(len(ordered)==len(available_slots) and
         socket_total<=3*len(ordered),
         "SOCKET_DECLARED_GEAR_SLOT_CAPACITY_EXCEEDED")
    planned={s:0 for s in sorted(available_slots)}
    missing=socket_total
    for layer in range(3):
        for s in ordered:
            if missing==0: break
            planned[s]+=1
            missing-=1
        if missing==0: break
    need(missing==0,"SOCKET_DECLARED_LAYOUT_COUNT_DRIFT")
    return planned


def intrinsic_source_plan(*, intrinsic_socket_counts, special_gem_id,
                          ordinary_gem_ids, source_observed_gem_item_ids,
                          need):
    """Reuse source-observed v232 slots; NEVER decide gem roles or approve J.

    The selection of a real special ID and ordinary IDs is a separate
    same-season source-owner decision. This only removes manual socket
    positioning from that selection. It consumes every intrinsic socket,
    adds NO socket bonus and keeps the exactly-one-special v271 contract.
    """
    counts=intrinsic_socket_counts
    need(type(counts) is dict and bool(counts) and
         all(type(slot) is str and bool(slot) and
             type(n) is int and 0<=n<=3 for slot,n in counts.items()),
         "SOCKET_INTRINSIC_SOURCE_COUNTS_INVALID")
    available={slot:n for slot,n in sorted(counts.items()) if n>0}
    total=sum(available.values())
    need(2<=total<=64, "SOCKET_INTRINSIC_ONE_SPECIAL_PLUS_ORDINARY_REQUIRED")
    need(type(special_gem_id) is int and special_gem_id>0 and
         type(ordinary_gem_ids) is list and
         len(ordinary_gem_ids)==total-1 and
         all(type(i) is int and i>0 and i!=special_gem_id
             and i not in DIAMONDS for i in ordinary_gem_ids),
         "SOCKET_INTRINSIC_SPECIAL_AND_ORDINARY_IDS_REQUIRED")
    observed=source_observed_gem_item_ids
    ids=sorted(set(ordinary_gem_ids)|{special_gem_id})
    need(type(observed) is list and observed==ids,
         "SOCKET_INTRINSIC_EXACT_SOURCE_ITEM_IDS_REQUIRED")
    # This is a stable position, NOT a head-only special requirement.
    position="head" if available.get("head",0)>0 else sorted(available)[0]
    return {"socket_counts":available,
            "special_gem_id":special_gem_id,
            "special_slot":position,
            "ordinary_gem_ids":list(ordinary_gem_ids),
            SOURCE_IDS_FIELD:list(ids)}


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
