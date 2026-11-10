"""v306 opt-in, pure deterministic seed-retaining multi-region escape policy.

A deliberately separate experiment from v305 and the production v290 default.
v304 owns global21 order, 15% global reserve, confirmation, and durable
stage history. v306's regional proposals protect high-scoring *measured*
global seeds from lower-scoring first local scouts, allocate uncommitted
regional calls using noisy seed-aware scores, and give bounded early 12/24%B
pairwise transfers an opportunity. This code never predicts DPS or claims
global optimality or familywise 95% superiority.
"""
from __future__ import annotations

import copy
import math

import v290_multiscale_adaptive_policy as base
import v303_adaptive_region_resource_policy as resource
import v304_v303_durable_adapter as durable
import v305_grid_pairwise_adaptive_hybrid as prior

SCHEMA = "v306_seed_retained_coarse_escape_regions_opt_in_v1"
GRID = "v306_measured_seed_grid"
PAIR12 = "v306_pairwise_12pct_B"
PAIR24 = "v306_pairwise_24pct_B"
PAIRFINE = "v306_pairwise_fine"
FALLBACK = "v306_seed_grid_fallback"
GLOBAL, RESERVE, CONFIRM = prior.GLOBAL, prior.RESERVE, prior.CONFIRM
PAIRS = frozenset((PAIR12, PAIR24, PAIRFINE))
REGIONAL = frozenset((GRID, FALLBACK, *PAIRS))
METHODS = frozenset((*REGIONAL, GLOBAL, RESERVE, CONFIRM))
STEPS = (.12, .24, .06, .03, .015, .0075, .003)


class PolicyBlocked(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise PolicyBlocked(reason)


def vector(row):
    return tuple(base.legacy.key(row["target"]))


def _measured_region_state(observations, *, total, initial_global_calls):
    globals_ = observations[:initial_global_calls]
    need(len(globals_) == initial_global_calls and
         all(r["adaptive_stage"] == "global_initial" for r in globals_),
         "V306_EXACT_GLOBAL_SEED_HISTORY")
    seeds = resource.initialize_regions([
        {"target": r["target"], "dps_mean": r["dps_mean"],
         "dps_sem": r["dps_sem"], "iterations": r["iterations"]}
        for r in globals_], total=total)["regions"]
    global_rows = {vector(r): r for r in globals_}
    result = {}
    for region in seeds:
        rid, origin = region["region_id"], tuple(region["center"])
        need(origin in global_rows, "V306_GLOBAL_SEED_NOT_MEASURED")
        local = [r for r in observations if
                 r["adaptive_stage"] == "regional" and
                 r["region_id"] == rid]
        candidates = [global_rows[origin]] + local
        best = max(candidates, key=lambda r: (
            resource.score(r), -r["dps_sem"], vector(r)))
        last = local[-1] if local else None
        radius = (last["region_radius_fraction"] if last else
                  region["radius_fraction"])
        need(resource.MIN_RADIUS <= radius <= resource.MAX_RADIUS,
             "V306_SEALED_RADIUS_OUT_OF_BOUNDS")
        result[rid] = {"seed": global_rows[origin], "best": best,
                       "local": local, "center": vector(best), "radius": radius}
    return result


def _seed_aware_selection(state, *, regional_budget):
    """Protect spent calls; retain a local-visit floor if affordable."""
    spent = {rid: len(info["local"]) for rid, info in state.items()}
    need(sum(spent.values()) < regional_budget,
         "V306_NO_REGIONAL_BUDGET_REMAINING")
    seed_floor = regional_budget >= len(state)
    if seed_floor:
        unvisited = [rid for rid, n in spent.items() if n == 0]
        if unvisited:
            # One scout per region first: prevents lock-in to a noisy seed.
            return min(unvisited, key=lambda rid: (
                -resource.score(state[rid]["seed"]), rid))
    leading = max((info["best"] for info in state.values()),
                  key=resource.score)
    leading_score = resource.score(leading)
    weights = {}
    for rid, info in state.items():
        candidate = info["best"]
        # z is a ranking heuristic, explicitly NOT a 95% decision.
        sem = math.hypot(leading["dps_sem"], candidate["dps_sem"])
        loss_z = max(0.0, (leading_score-resource.score(candidate)) /
                     max(sem, 1e-9))
        weights[rid] = 0.20 + 0.80 * math.exp(-0.60 * min(8.0, loss_z))
    floors = {rid: max(1, used) if seed_floor else used
              for rid, used in spent.items()}
    planned = resource._allocate(
        [{"region_id": rid} for rid in sorted(state)], weights,
        regional_budget, 0.40, already=floors)
    eligible = [rid for rid in state if planned[rid] > spent[rid]]
    need(bool(eligible), "V306_UNCOMMITTED_REGION_ALLOCATION_MISSING")
    return min(eligible, key=lambda rid: (
        -(planned[rid] - spent[rid]), -weights[rid], rid))


def _coarse_pair(observations, state, rid, *, total, lower, upper):
    info = state[rid]
    local = info["local"]
    pair_visits = sum(r["hybrid_method"] in PAIRS for r in local)
    frac = STEPS[min(pair_visits, len(STEPS) - 1)]
    desired = max(1, round(total * frac))
    seen = {vector(r) for r in observations if r["phase"] == "scout"}
    # Global seed is still a real Native measurement, not a predicted anchor.
    anchors = sorted([info["seed"]] + local, key=lambda r: (
        -resource.score(r), r["dps_sem"], vector(r)))[:4]
    chosen = None
    # Allow up to 24%B non-local escape from the best measured region center.
    # This is a move-distance guard, NOT an invented 24%-DPS assumption.
    extent = max(1, round(total * .24))
    for rank, anchor in enumerate(anchors):
        v = vector(anchor)
        for candidate, actual in base._bounded_fraction_neighbors(
                v, desired, total, lower, upper, seen):
            if base._distance(candidate, info["center"]) > extent:
                continue
            error = abs(math.log2(max(1, actual) / desired))
            novelty = min(base._distance(candidate, x) for x in seen)
            utility = (resource.score(anchor)
                       - 0.002 * anchor["dps_mean"] * error
                       + 0.00003 * anchor["dps_mean"] *
                         min(novelty / total, .10)
                       - 0.00002 * anchor["dps_mean"] * rank)
            value = (utility, actual / total, tuple(-x for x in candidate))
            if chosen is None or value > chosen[0]:
                chosen = value, candidate
    marker = PAIR12 if pair_visits == 0 else (
        PAIR24 if pair_visits == 1 else PAIRFINE)
    return (chosen[1], marker) if chosen is not None else (None, None)


def next_plan(observations, *, total, lower, upper, max_native_calls,
              scout_iterations, confirmation_iterations,
              initial_global_calls=160, confirmation_calls=8):
    need(type(observations) is list, "V306_HISTORY_LIST_REQUIRED")
    for row in observations:
        method, stage = row.get("hybrid_method"), row["adaptive_stage"]
        need(method in METHODS, "V306_HISTORY_METHOD_REQUIRED_OR_INVALID")
        valid = (method in REGIONAL if stage == "regional" else
                 method == {"global_initial": GLOBAL,
                            "global_reserve": RESERVE,
                            "confirmation": CONFIRM}.get(stage))
        need(valid, "V306_HISTORY_STAGE_METHOD_DRIFT")

    proposal = durable.next_plan(
        observations, total=total, lower=lower, upper=upper,
        max_native_calls=max_native_calls,
        scout_iterations=scout_iterations,
        confirmation_iterations=confirmation_iterations,
        initial_global_calls=initial_global_calls,
        confirmation_calls=confirmation_calls)
    if proposal["next_request"] is None:
        return dict(proposal, schema=SCHEMA)
    result = copy.deepcopy(proposal)
    req = result["next_request"]
    stage = req["adaptive_stage"]
    if stage == "regional":
        state = _measured_region_state(
            observations, total=total,
            initial_global_calls=initial_global_calls)
        budget = durable.options(max_native_calls,
                                 initial_global_calls,
                                 confirmation_calls)["regional_calls"]
        rid = _seed_aware_selection(state, regional_budget=budget)
        info = state[rid]
        local = info["local"]
        seen = {vector(r) for r in observations if r["phase"] == "scout"}
        candidate, method = None, GRID
        if len(local) % 3 != 0:
            candidate, method = _coarse_pair(
                observations, state, rid, total=total,
                lower=lower, upper=upper)
        if candidate is None:
            candidate, actual_radius = resource._candidate(
                total, lower, upper, info["center"], info["radius"], seen)
            need(candidate is not None, "V306_SEED_GRID_NO_FEASIBLE_CANDIDATE")
            method = GRID if len(local) % 3 == 0 else FALLBACK
            radius = min(resource.MAX_RADIUS, actual_radius / total)
        else:
            radius = info["radius"]
        req.update(target=base.legacy.to_target(candidate),
                   region_id=rid, region_center=list(info["center"]),
                   region_radius_fraction=radius, hybrid_method=method)
        result["decision"] = "V306_" + method.upper()
    elif stage == "global_initial":
        req["hybrid_method"] = GLOBAL
    elif stage == "global_reserve":
        req["hybrid_method"] = RESERVE
    elif stage == "confirmation":
        req["hybrid_method"] = CONFIRM
    else:
        raise PolicyBlocked("V306_UNKNOWN_STAGE")
    target = vector(req)
    need(base.legacy.eligible(target, total, lower, upper),
         "V306_PROPOSED_STAT_BOUNDS_OR_B_DRIFT")
    if stage != "confirmation":
        need(target not in {vector(r) for r in observations
                            if r["phase"] == "scout"},
             "V306_DUPLICATE_SCOUT")
    return dict(result, schema=SCHEMA)
