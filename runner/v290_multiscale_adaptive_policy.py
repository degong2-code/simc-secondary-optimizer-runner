#!/usr/bin/env python3
"""Opt-in scalable CHMV search POLICY for long-running SimC optimization.

This is a pure proposal module. It never executes SimC, predicts an item's
effects, alters G/J/F/O accounting, or asserts a global optimum. A separate
durable executor must honor exact (candidate, iterations, profile) identities
and the user's Native/CPU budget. The bounded v094/v065 path stays unchanged.
"""
from __future__ import annotations

import itertools
import math

import v065_v015_scheduler_adapter as legacy

STATS = legacy.STATS
SCHEMA = "v290_multiscale_noisy_simplex_policy_v1"
Z95 = 1.959963984540054
SCALES = (0.24, 0.12, 0.06, 0.03, 0.015, 0.0075, 0.003)


class PolicyBlocked(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise PolicyBlocked(reason)


def _halton(index, base):
    result, factor = 0.0, 1.0 / base
    while index:
        result += factor * (index % base)
        index //= base
        factor /= base
    return result


def _apportion(total, lower, upper, weights):
    """Bounded four-stat integer simplex projection; exact T and each floor."""
    rest = total - sum(lower)
    capacities = [hi - lo for lo, hi in zip(lower, upper)]
    need(0 <= rest <= sum(capacities), "INFEASIBLE_BOUNDED_SIMPLEX")
    if rest == 0:
        return tuple(lower)
    need(len(weights) == 4 and all(math.isfinite(w) and w > 0
                                  for w in weights), "INVALID_PROPOSAL_WEIGHTS")
    high = max(c / w for c, w in zip(capacities, weights)) + 1.
    low = 0.
    for _ in range(62):
        mid = (low + high) / 2.
        if sum(min(c, w * mid) for c, w in zip(capacities, weights)) < rest:
            low = mid
        else:
            high = mid
    floats = [min(c, w * high) for c, w in zip(capacities, weights)]
    inc = [min(c, int(math.floor(v))) for c, v in zip(capacities, floats)]
    left = rest - sum(inc)
    need(0 <= left <= 4, "BOUNDED_SIMPLEX_ROUNDING_DRIFT")
    order = sorted(range(4), key=lambda i: (-(floats[i] - inc[i]), i))
    while left:
        progressed = False
        for i in order:
            if inc[i] < capacities[i]:
                inc[i] += 1
                left -= 1
                progressed = True
                if left == 0:
                    break
        need(progressed, "BOUNDED_SIMPLEX_REMAINDER_BLOCKED")
    candidate = tuple(lo + extra for lo, extra in zip(lower, inc))
    need(legacy.eligible(candidate, total, lower, upper),
         "BOUNDED_SIMPLEX_PROJECTION_INELIGIBLE")
    return candidate


def _global_pool(total, lower, upper, count):
    """Deterministic extreme and low-discrepancy 3D-simplex coverage."""
    need(type(count) is int and 8 <= count <= 512,
         "GLOBAL_POOL_COUNT")
    seen = set()
    center = _apportion(total, lower, upper, (1, 1, 1, 1))
    yield center
    seen.add(center)
    remaining = total - sum(lower)
    capacities = [hi - lo for lo, hi in zip(lower, upper)]
    for order in itertools.permutations(range(4)):
        nxt = list(lower)
        residual = remaining
        for i in order:
            amount = min(capacities[i], residual)
            nxt[i] += amount
            residual -= amount
        candidate = tuple(nxt)
        if candidate not in seen:
            seen.add(candidate)
            yield candidate
    for n in range(1, count + 1):
        weights = tuple(-math.log(max(1.e-12, _halton(n, p)))
                        for p in (2, 3, 5, 7))
        candidate = _apportion(total, lower, upper, weights)
        if candidate not in seen:
            seen.add(candidate)
            yield candidate


def _row(row, total, lower, upper):
    need(type(row) is dict and type(row.get("target")) is dict,
         "MEASURED_TARGET_REQUIRED")
    target = legacy.key(row["target"])
    need(legacy.eligible(target, total, lower, upper),
         "MEASURED_TARGET_OUTSIDE_BOUNDS")
    for key in ("dps_mean", "dps_sem"):
        v = row.get(key)
        need(type(v) in (float, int) and math.isfinite(v) and v >= 0,
             "INVALID_NATIVE_" + key.upper())
    iterations = row.get("iterations")
    need(type(iterations) is int and 1 <= iterations <= 10000000,
         "EXACT_SIMC_REQUEST_ITERATIONS_REQUIRED")
    return target


def _best_by_vector(observations, total, lower, upper):
    """No interpolation or invented native samples; retain best precision."""
    newest = {}
    identities = set()
    for row in observations:
        vec = _row(row, total, lower, upper)
        pair = (vec, row["iterations"])
        need(pair not in identities, "DUPLICATE_TARGET_ITERATION_IDENTITY")
        identities.add(pair)
        old = newest.get(vec)
        if old is None or row["iterations"] > old["iterations"]:
            newest[vec] = row
    return newest, identities


def _distance(first, second):
    return sum(abs(a - b) for a, b in zip(first, second)) / 2


def _closest_challenger(by_vector, incumbent):
    remaining = [v for v in by_vector if v != incumbent]
    if not remaining:
        return None
    # Conservative incumbent; optimistic challengers are prioritization
    # heuristics, NOT family-wise 95% proof of global ranking.
    return max(remaining,
               key=lambda v: (by_vector[v]["dps_mean"] +
                              Z95 * by_vector[v]["dps_sem"], v))


def _precision_action(by_vector, identities, *, scout_iterations,
                      confirmation_iterations, max_iterations):
    if len(by_vector) < 2:
        return None
    incumbent = max(by_vector,
                    key=lambda v:(by_vector[v]["dps_mean"], v))
    challenger = _closest_challenger(by_vector, incumbent)
    if challenger is None:
        return None
    a, b = by_vector[incumbent], by_vector[challenger]
    half = Z95 * math.hypot(a["dps_sem"], b["dps_sem"])
    gap = abs(a["dps_mean"] - b["dps_mean"])
    separated = gap > half
    # No blind SEM polishing once a selected pair already separates at 95%.
    for vec in (incumbent, challenger):
        latest = by_vector[vec]["iterations"]
        if separated and latest >= confirmation_iterations:
            continue
        target_iters = (confirmation_iterations if latest < confirmation_iterations
                        else min(max_iterations, max(latest + 1, latest * 2)))
        if (target_iters > latest and target_iters <= max_iterations and
                (vec, target_iters) not in identities):
            return {"phase": "precision", "target": legacy.to_target(vec),
                    "iterations": target_iters,
                    "observed_pair_gap": round(gap, 8),
                    "selected_pair_95_halfwidth": round(half, 8),
                    "selected_pair_95_separated": separated,
                    "interpretation": "SELECTION_HEURISTIC_NOT_GLOBAL_PROOF"}
    return None


def next_plan(observations, *, total, lower, upper, native_calls_used,
              max_native_calls, scout_iterations=64,
              confirmation_iterations=320, max_iterations=5120):
    """Plan one exact SimC request, permitting budgets well beyond 6 calls.

    Native results, observation order and requested iteration identity are
    supplied by the caller. No session writes, subprocesses or Native here.
    """
    need(type(total) is int and 1 <= total <= 100000 and
         type(lower) in (tuple, list) and type(upper) in (tuple, list)
         and len(lower) == len(upper) == 4 and
         all(type(x) is int for x in (*lower, *upper)) and
         all(0 <= a <= b <= total for a, b in zip(lower, upper)) and
         sum(lower) <= total <= sum(upper), "OPTIMIZER_BOUNDS")
    lower, upper = tuple(lower), tuple(upper)
    need(type(native_calls_used) is int and native_calls_used >= 0 and
         type(max_native_calls) is int and 1 <= max_native_calls <= 100000,
         "EXPLICIT_NATIVE_CALL_BUDGET_REQUIRED")
    need(type(scout_iterations) is int and
         type(confirmation_iterations) is int and
         type(max_iterations) is int and
         1 <= scout_iterations < confirmation_iterations <= max_iterations,
         "ITERATION_BUDGET_ORDER")
    need(type(observations) is list, "NATIVE_OBSERVATIONS_LIST")
    by_vector, identities = _best_by_vector(
        observations, total, lower, upper)
    if native_calls_used >= max_native_calls:
        return {"schema": SCHEMA, "status": "BUDGET_EXHAUSTED",
                "native_calls_used": native_calls_used,
                "global_optimum_proven": False, "next_request": None}
    unique = len(by_vector)
    desired_global = min(64, max(8, math.ceil(2 * math.sqrt(max_native_calls))))
    # Small typed sessions need a selected-pair confirmation *before*
    # exhausting their Native-call budget. Keep the established long-run
    # exploration/precision cadence unchanged.
    small_budget_precision_due = (
        10 <= max_native_calls <= 16
        and unique >= max(8, max_native_calls - 4))
    periodic_precision_due = (
        len(observations) % 16 in (14, 15)
        and unique >= min(32, max(8, desired_global // 2)))
    if small_budget_precision_due or periodic_precision_due:
        precision = _precision_action(
            by_vector, identities, scout_iterations=scout_iterations,
            confirmation_iterations=confirmation_iterations,
            max_iterations=max_iterations)
        if precision is not None:
            return {"schema": SCHEMA, "status": "NEXT_NATIVE_PROPOSED",
                    "decision": "UNCERTAINTY_AWARE_REMEASURE",
                    "next_request": precision,
                    "native_calls_used": native_calls_used,
                    "global_optimum_proven": False}
    observed = set(by_vector)
    # v063 normalizes only genuine JSON2 add_non_zero omissions to zero,
    # while still requiring real Native stats and exact rating reconciliation.
    # Explore the actual feasible floor, including a legal zero boundary.
    global_due = unique < desired_global or (
        len(observations) % 23 == 0 and len(observations) > desired_global)
    candidate = None
    decision = None
    if global_due:
        if not observed:
            # Maximin without an observed center is undefined/informationally
            # tied; a balanced baseline is the useful first measurement.
            candidate = _apportion(total, lower, upper, (1,1,1,1))
            decision = "GLOBAL_BALANCED_BASELINE_FIRST"
        else:
            pool = [v for v in _global_pool(
                        total, lower, upper,
                        min(256, max(32, desired_global * 3)))
                    if v not in observed]
            if pool:
                candidate = max(pool, key=lambda v:(
                    min(_distance(v, x) for x in observed),
                    tuple(-k for k in v)))
                decision = "GLOBAL_MAXIMIN_SIMPLEX_COVERAGE"
    if candidate is None and observed:
        ranked = sorted(by_vector, key=lambda v:(
            -(by_vector[v]["dps_mean"] -
              min(by_vector[v]["dps_sem"],
                  by_vector[v]["dps_mean"] * .02) * .5), v))
        anchor_count = min(16, max(3, math.ceil(math.sqrt(unique))))
        # Scan the observations once. Re-scanning all historical candidates
        # inside every (anchor, step, neighbor) would make a 2,000-case
        # session spend avoidable CPU on proposal generation.
        minima = tuple(min(v[i] for v in observed) for i in range(4))
        maxima = tuple(max(v[i] for v in observed) for i in range(4))
        before = tuple(maxima[i] - minima[i] for i in range(4))
        target_level = min(len(SCALES) - 1,
                           int(math.log2(max(1, unique // 24) + 1)))
        best = None
        for anchor in ranked[:anchor_count]:
            row = by_vector[anchor]
            parent_score = row["dps_mean"] - .5 * min(
                row["dps_sem"], row["dps_mean"] * .02)
            for level, fraction in enumerate(SCALES):
                step = max(1, min(total, round(total * fraction)))
                for nxt in legacy.neighbors(
                        anchor, step, total, lower, upper, observed):
                    gained_axes = sum(
                        before[i] == 0 and
                        (nxt[i] < minima[i] or nxt[i] > maxima[i])
                        for i in range(4))
                    utility = (parent_score +
                               .003 * row["dps_mean"] * gained_axes -
                               .0005 * row["dps_mean"] *
                               abs(level - target_level))
                    score = (utility, _distance(nxt, anchor), nxt)
                    if best is None or score > best[0]:
                        best = (score, nxt)
        if best is not None:
            candidate = best[1]
            decision = "NOISE_AWARE_MULTISCALE_FEASIBLE_NEIGHBOR"
    if candidate is None:
        # All step candidates may be exhausted. Never forge a result.
        return {"schema": SCHEMA, "status": "NO_NEW_FEASIBLE_POLICY_CANDIDATE",
                "native_calls_used": native_calls_used,
                "global_optimum_proven": False, "next_request": None}
    need(legacy.eligible(candidate, total, lower, upper)
         and candidate not in observed, "PROPOSED_CANDIDATE_NOT_NEW_AND_FEASIBLE")
    return {"schema": SCHEMA, "status": "NEXT_NATIVE_PROPOSED",
            "decision": decision,
            "next_request": {"phase": "scout", "target": legacy.to_target(candidate),
                             "iterations": scout_iterations,
                             "interpretation": "UNMEASURED_NATIVE_CANDIDATE"},
            "observed_unique_candidates": unique,
            "native_calls_used": native_calls_used,
            "global_optimum_proven": False}
