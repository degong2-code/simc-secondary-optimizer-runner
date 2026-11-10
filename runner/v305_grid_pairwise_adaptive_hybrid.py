"""v305 experimental hybrid: v302 grid -> v290 pairwise, adaptive v304 regions.

Pure deterministic proposals, no Native. v304 owns global21, regional
allocation / radius / cross-region reserve / confirmation, preserving its
existing source and session seals. v305 selects each local proposal:
every third visit to a region uses the v302 6-level residual lattice; on
the intervening visits consider v290's seven B-relative pairwise shifts
around up to four well-measured regional anchors. Once a region cannot
supply an admissible pairwise vector, fall back to v304's 6-grid candidate.

No 95% superiority / global-optimum claim from this ranking heuristic.
"""
from __future__ import annotations

import copy
import math

import v290_multiscale_adaptive_policy as base
import v303_adaptive_region_resource_policy as adaptive
import v304_v303_durable_adapter as durable

SCHEMA = "v305_grid_v290_pairwise_adaptive_regions_opt_in_v1"
GRID = "v302_local6_grid"
PAIR = "v290_pairwise_neighbors"
FALLBACK = "v302_grid_pairwise_fallback"
GLOBAL = "v302_global21"
RESERVE = "v290_global_reserve"
CONFIRM = "fixed_confirm"
METHODS = frozenset((GRID, PAIR, FALLBACK, GLOBAL, RESERVE, CONFIRM))


class HybridBlocked(ValueError):
    pass


def need(condition, code):
    if not condition:
        raise HybridBlocked(code)


def _observed_target(row):
    return tuple(base.legacy.key(row["target"]))


def pairwise_local_candidate(observations, region_id, center, radius_fraction,
                             *, total, lower, upper):
    """Use actual v290 pair-transfer generator, rank only prior Native facts."""
    seen = {_observed_target(r) for r in observations}
    radius = max(1, round(total * radius_fraction * 1.5))
    local = [r for r in observations if r.get("region_id") == region_id and
             r["phase"] == "scout"]
    local_count = len(local)
    # Include the initial global scout at the selected region center as a
    # measured anchor; never invent a DPS response for the center.
    anchors = [r for r in observations
               if _observed_target(r) == tuple(center) or
               (r.get("region_id") == region_id and r["phase"] == "scout")]
    # Occasionally the most recent center has no exact measured point, e.g.
    # an expanded v303 radius. Nearby measured regional anchors remain valid.
    if not anchors:
        anchors = [r for r in observations if r["phase"] == "scout" and
                   base._distance(_observed_target(r), center) <= radius]
    anchors = sorted(anchors, key=lambda r: (
        -adaptive.score(r), -r["iterations"], _observed_target(r)))[:4]
    if not anchors:
        return None

    # Coarse-to-fine: early several visits retain v290's 6/3%-B moves,
    # later add 1.5/0.75/0.3%-B. 24/12%-B remain available if a region
    # radius actually expanded enough to allow such transfers.
    desired_fraction = (.06 if local_count < 6 else .03 if local_count < 14
                        else .015 if local_count < 24 else .0075)
    desired = max(1, round(total * desired_fraction))
    best = None
    for rank, anchor in enumerate(anchors):
        source = _observed_target(anchor)
        if not base.legacy.eligible(source, total, lower, upper):
            continue
        for fraction in base.SCALES:
            requested = max(1, round(total * fraction))
            for candidate, moved in base._bounded_fraction_neighbors(
                    source, requested, total, lower, upper, seen):
                if base._distance(candidate, center) > radius:
                    continue
                # v290: prioritize a promising incumbent and useful shift
                # magnitude; also lightly reward novel distance from prior
                # measurements, with no invented DPS prediction.
                scale_penalty = abs(math.log2(max(1, moved) / desired))
                novelty = min(base._distance(candidate, p) for p in seen)
                utility = (
                    adaptive.score(anchor)
                    - 0.0005 * anchor["dps_mean"] * scale_penalty
                    + 0.00003 * anchor["dps_mean"] * min(novelty / total, .10)
                    - .00002 * anchor["dps_mean"] * rank
                )
                score = (utility, moved / total, tuple(-x for x in candidate))
                if best is None or score > best[0]:
                    best = (score, candidate)
    return best[1] if best else None


def next_plan(observations, *, total, lower, upper, max_native_calls,
              scout_iterations, confirmation_iterations,
              initial_global_calls=160, confirmation_calls=8):
    """Return v304-compatible plan enriched with one v305 mode marker."""
    need(type(observations) is list, "V305_HISTORY_LIST_REQUIRED")
    for row in observations:
        if "hybrid_method" not in row:
            raise HybridBlocked("V305_HISTORY_METHOD_REQUIRED")
        need(row["hybrid_method"] in METHODS, "V305_HISTORY_METHOD_INVALID")
        if row["adaptive_stage"] == "regional":
            need(row["hybrid_method"] in (GRID, PAIR, FALLBACK),
                 "V305_REGION_METHOD_STAGE_DRIFT")
        else:
            expected = {
                "global_initial": GLOBAL,
                "global_reserve": RESERVE,
                "confirmation": CONFIRM,
            }[row["adaptive_stage"]]
            need(row["hybrid_method"] == expected,
                 "V305_NONREGION_METHOD_STAGE_DRIFT")

    proposal = durable.next_plan(
        observations, total=total, lower=lower, upper=upper,
        max_native_calls=max_native_calls, scout_iterations=scout_iterations,
        confirmation_iterations=confirmation_iterations,
        initial_global_calls=initial_global_calls,
        confirmation_calls=confirmation_calls)
    if proposal["next_request"] is None:
        return dict(proposal, schema=SCHEMA)
    plan = copy.deepcopy(proposal)
    req = plan["next_request"]
    stage = req["adaptive_stage"]
    if stage == "regional":
        region_id = req["region_id"]
        prior_local = sum(r.get("region_id") == region_id and
                          r["adaptive_stage"] == "regional" for r in observations)
        method = GRID
        # Ensure at least one grid investigation of each distinct region,
        # then interleave paired-stat moves. Never replace all multi-stat
        # regional grid scouts with pairwise-only moves.
        if prior_local % 3 != 0:
            candidate = pairwise_local_candidate(
                observations, region_id,
                tuple(req["region_center"]), req["region_radius_fraction"],
                total=total, lower=lower, upper=upper)
            if candidate is not None:
                req["target"] = base.legacy.to_target(candidate)
                method = PAIR
            else:
                method = FALLBACK
        req["hybrid_method"] = method
        plan["decision"] = "V305_" + method.upper()
    elif stage == "global_initial":
        req["hybrid_method"] = GLOBAL
    elif stage == "global_reserve":
        req["hybrid_method"] = RESERVE
    elif stage == "confirmation":
        req["hybrid_method"] = CONFIRM
    else:
        raise HybridBlocked("V305_UNKNOWN_STAGE")
    need(base.legacy.eligible(tuple(base.legacy.key(req["target"])),
                              total, lower, upper),
         "V305_TARGET_INFEASIBLE")
    need(tuple(base.legacy.key(req["target"])) not in {
        _observed_target(r) for r in observations
        if r["phase"] == "scout"} or stage == "confirmation",
         "V305_DUPLICATE_SCOUT")
    plan["schema"] = SCHEMA
    return plan
