"""Optional v303 planning adapter for v291 journals: no Native execution.

Every plan is deterministic from its sealed configuration and accepted prior
observations. No unverified SimC results, effect models or 95% claims.
"""
from __future__ import annotations

import functools
import math

import v290_multiscale_adaptive_policy as base
import v302_weak_multiregion_zoom as geometry
import v303_adaptive_region_resource_policy as regions

SCHEMA = "v304_v303_v291_durable_adapter_v1"
STAGES = ("global_initial", "regional", "global_reserve", "confirmation")


class AdapterBlocked(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise AdapterBlocked(reason)


def options(max_native_calls, initial_global_calls, confirmation_calls):
    need(type(max_native_calls) is int and 8 <= max_native_calls <= 100000
         and type(initial_global_calls) is int and 4 <= initial_global_calls <= 512
         and type(confirmation_calls) is int and 1 <= confirmation_calls <= 32
         and initial_global_calls + confirmation_calls < max_native_calls,
         "V304_TYPED_CALL_BUDGET")
    post = max_native_calls - initial_global_calls - confirmation_calls
    minimum = min(8, max(1, math.ceil(post * .15)))
    reserve = min(post - 1, max(minimum, math.ceil(post * .15)))
    return {"initial_global_calls": initial_global_calls,
            "post_global_calls": post,
            "confirmation_calls": confirmation_calls,
            "regional_calls": post - reserve, "global_reserve_calls": reserve,
            "min_global_reserve": minimum}


@functools.lru_cache(maxsize=4)
def _global_order(total, lower, upper, count):
    """Compute v302 global21 order once per process/bounds, not per Native call."""
    center = base._apportion(total, lower, upper, (1, 1, 1, 1))
    pool = geometry.residual_lattice(total, lower, upper, 21)
    order = (center,) + geometry.bounded_farthest(
        pool, count - 1, seed=center, exclude=(center,))
    need(len(order) == count and len(set(order)) == count,
         "V304_GLOBAL_21_RESOLUTION_EXHAUSTED")
    return order


def _phase(row):
    return row["phase"] == ("precision" if row["adaptive_stage"] == "confirmation"
                            else "scout")


def _history(observations, *, total, lower, upper, opts, scout_iterations,
             confirmation_iterations):
    global_order = _global_order(total, tuple(lower), tuple(upper),
                                 opts["initial_global_calls"])
    observed_scouts, precision_vectors = set(), set()
    regions_at_seed = None
    regional_used = reserve_used = confirm_used = 0
    for index, row in enumerate(observations):
        need(type(row) is dict and row.get("adaptive_stage") in STAGES
             and _phase(row), "V304_HISTORY_STAGE_PHASE")
        target = tuple(base.legacy.key(row["target"]))
        need(base.legacy.eligible(target, total, lower, upper),
             "V304_HISTORY_TARGET_INFEASIBLE")
        expected_iterations = (confirmation_iterations
                               if row["adaptive_stage"] == "confirmation"
                               else scout_iterations)
        need(row["iterations"] == expected_iterations,
             "V304_HISTORY_ITERATION_IDENTITY")
        meta = (row.get("region_id"), row.get("region_center"),
                row.get("region_radius_fraction"))
        if row["adaptive_stage"] == "global_initial":
            need(index < opts["initial_global_calls"] and
                 target == global_order[index] and meta == (None, None, None),
                 "V304_GLOBAL_INITIAL_HISTORY_DRIFT")
        elif row["adaptive_stage"] in ("regional", "global_reserve"):
            need(index >= opts["initial_global_calls"] and
                 index < opts["initial_global_calls"] + opts["post_global_calls"],
                 "V304_POST_GLOBAL_ORDER_DRIFT")
            if regions_at_seed is None:
                seed = observations[:opts["initial_global_calls"]]
                initial = regions.initialize_regions([
                    dict(target=r["target"], dps_mean=r["dps_mean"],
                         dps_sem=r["dps_sem"], iterations=r["iterations"])
                    for r in seed], total=total)
                regions_at_seed = initial["regions"]
            if row["adaptive_stage"] == "regional":
                need(row["region_id"] in {r["region_id"] for r in regions_at_seed}
                     and type(row["region_center"]) is list
                     and base.legacy.eligible(tuple(row["region_center"]), total,
                                              lower, upper)
                     and type(row["region_radius_fraction"]) in (int, float)
                     and regions.MIN_RADIUS <= row["region_radius_fraction"]
                     <= regions.MAX_RADIUS, "V304_LOCAL_REGION_METADATA")
                regional_used += 1
            else:
                need(meta == (None, None, None), "V304_RESERVE_METADATA")
                reserve_used += 1
            need(regional_used <= opts["regional_calls"]
                 and reserve_used <= opts["global_reserve_calls"],
                 "V304_POST_GLOBAL_BUDGET_OVERSPENT")
        else:
            need(index >= opts["initial_global_calls"] + opts["post_global_calls"]
                 and index < opts["initial_global_calls"] +
                               opts["post_global_calls"] + opts["confirmation_calls"]
                 and meta == (None, None, None) and target in observed_scouts
                 and target not in precision_vectors,
                 "V304_CONFIRMATION_HISTORY_DRIFT")
            precision_vectors.add(target)
            confirm_used += 1
        if row["adaptive_stage"] != "confirmation":
            need(target not in observed_scouts, "V304_DUPLICATE_SCOUT_TARGET")
            observed_scouts.add(target)
    return (global_order, observed_scouts, regions_at_seed,
            regional_used, reserve_used, confirm_used)


def next_plan(observations, *, total, lower, upper, max_native_calls,
              scout_iterations, confirmation_iterations,
              initial_global_calls=160, confirmation_calls=8):
    need(type(observations) is list, "V304_OBSERVATIONS_LIST_REQUIRED")
    opts = options(max_native_calls, initial_global_calls, confirmation_calls)
    need(type(scout_iterations) is int and type(confirmation_iterations) is int
         and 1 <= scout_iterations < confirmation_iterations,
         "V304_NATIVE_ITERATIONS")
    need(type(lower) in (tuple, list) and type(upper) in (tuple, list)
         and len(lower) == len(upper) == 4 and
         all(type(x) is int for x in (*lower, *upper))
         and all(0 <= lo <= hi <= total for lo, hi in zip(lower, upper))
         and sum(lower) <= total <= sum(upper), "V304_INFEASIBLE_BOUNDS")
    (global_order, seen, seeds, local_used, reserve_used,
     confirm_used) = _history(
        observations, total=total, lower=lower, upper=upper, opts=opts,
        scout_iterations=scout_iterations,
        confirmation_iterations=confirmation_iterations)
    index = len(observations)
    if index >= max_native_calls:
        return {"schema": SCHEMA, "status": "BUDGET_EXHAUSTED",
                "next_request": None, "global_optimum_proven": False}
    def emit(stage, target, *, decision, region_id=None, region_center=None,
             region_radius_fraction=None):
        phase = "precision" if stage == "confirmation" else "scout"
        return {"schema": SCHEMA, "status": "NEXT_NATIVE_PROPOSED",
                "decision": decision, "global_optimum_proven": False,
                "next_request": {
                    "phase": phase, "iterations": confirmation_iterations if
                    phase == "precision" else scout_iterations,
                    "target": base.legacy.to_target(target),
                    "adaptive_stage": stage, "region_id": region_id,
                    "region_center": region_center,
                    "region_radius_fraction": region_radius_fraction,
                }}
    if index < opts["initial_global_calls"]:
        return emit("global_initial", global_order[index],
                    decision="V304_V302_GLOBAL21_INITIAL")
    post_done = local_used + reserve_used
    if post_done < opts["post_global_calls"]:
        reserve_due = (reserve_used < opts["global_reserve_calls"] and
            (local_used >= opts["regional_calls"] or
             reserve_used < round((post_done + 1) *
                                  opts["global_reserve_calls"] /
                                  opts["post_global_calls"])))
        next_local = None
        if local_used < opts["regional_calls"]:
            if seeds is None:
                initial = regions.initialize_regions([
                    dict(target=r["target"], dps_mean=r["dps_mean"],
                         dps_sem=r["dps_sem"], iterations=r["iterations"])
                    for r in observations[:opts["initial_global_calls"]]],
                    total=total)
                seeds = initial["regions"]
            # Continue from the last SEALED regional proposal, not from
            # the initial seed on every invocation. The accepted region
            # center/radius live in the authenticated v291 journal.
            state = {r["region_id"]: dict(r) for r in seeds}
            for old in observations[opts["initial_global_calls"]:]:
                if old["adaptive_stage"] == "regional":
                    item = state[old["region_id"]]
                    item["center"] = tuple(old["region_center"])
                    item["radius_fraction"] = old["region_radius_fraction"]
            seeds = [state[r["region_id"]] for r in seeds]
            local = regions.next_plan([
                {"target": r["target"], "sequence": i,
                 "phase": r["phase"], "iterations": r["iterations"],
                 "region_id": r.get("region_id"), "dps_mean": r["dps_mean"],
                 "dps_sem": r["dps_sem"]}
                for i, r in enumerate(observations)],
                total=total, lower=lower, upper=upper, regions=seeds,
                total_scout_calls=opts["post_global_calls"],
                scout_iterations=scout_iterations,
                confirmation_iterations=confirmation_iterations,
                global_scout_calls_used=reserve_used,
                min_global_reserve=opts["min_global_reserve"])
            next_local = local["next_request"]
        if reserve_due or next_local is None:
            if reserve_used < opts["global_reserve_calls"]:
                target = base._unobserved_global_maximin(
                    total, lower, upper, 64, seen)
                if target is not None:
                    return emit("global_reserve", target,
                                decision="V304_V290_GLOBAL_EXPLORATION_RESERVE")
        if next_local is not None:
            target = tuple(base.legacy.key(next_local["target"]))
            need(target not in seen, "V304_PROPOSAL_ALREADY_OBSERVED")
            return emit("regional", target, decision="V304_ADAPTIVE_LOCAL_RESOURCE",
                        region_id=next_local["region_id"],
                        region_center=list(next_local["center"]),
                        region_radius_fraction=next_local["radius_fraction"])
        return {"schema": SCHEMA, "status": "NO_NEW_FEASIBLE_POLICY_CANDIDATE",
                "next_request": None, "global_optimum_proven": False}

    # Confirm materially promising distinct observed vectors in one exact
    # fixed-iteration cohort. Never pretend this proves family-wise 95%.
    confirmed = {tuple(base.legacy.key(r["target"]))
                 for r in observations if r["adaptive_stage"] == "confirmation"}
    by_target = {tuple(base.legacy.key(r["target"])): r
                 for r in observations if r["adaptive_stage"] != "confirmation"}
    ranked = sorted(by_target, key=lambda v: (
        -regions.score(by_target[v]), v))
    for candidate in ranked:
        if candidate not in confirmed:
            return emit("confirmation", candidate,
                        decision="V304_SELECTED_CANDIDATE_FIXED_CONFIRM")
    return {"schema": SCHEMA, "status": "NO_NEW_FEASIBLE_POLICY_CANDIDATE",
            "next_request": None, "global_optimum_proven": False}
