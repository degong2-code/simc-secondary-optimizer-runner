#!/usr/bin/env python3
"""Opt-in percentage-reference candidates for the v290/v291 DPS engine.

Pure geometry/selection: never estimates DPS, changes G/J/F/O, or calls SimC.
The existing v290 default remains unchanged until measured evidence warrants
promotion. A point count is a resolution setting, NOT a hard-coded rating step.
"""
from __future__ import annotations

from bisect import bisect_right
from functools import lru_cache
import heapq
import math
import statistics

import v290_multiscale_adaptive_policy as current

STATS = current.STATS
SCHEMA = "v298_percentage_reference_grid_experimental_v1"


def _need(condition, code):
    if not condition:
        raise current.PolicyBlocked(code)


def _bounds(total, lower, upper):
    _need(type(total) is int and 1 <= total <= 100000 and
          type(lower) in (list, tuple) and type(upper) in (list, tuple)
          and len(lower) == len(upper) == 4 and
          all(type(x) is int for x in (*lower, *upper)) and
          all(0 <= lo <= hi <= total for lo, hi in zip(lower, upper)) and
          sum(lower) <= total <= sum(upper), "PERCENT_GRID_BOUNDS")
    return tuple(lower), tuple(upper)


def bounded_proportional(total, lower, upper, weights):
    """Exact integer B with bounded water filling and largest remainders.

    weights encode *base* CHMV ratios, not final T/O or proc-derived DPS.
    Saturated coordinates are pinned; leftover capacity is reallocated among
    positive-weight axes. Zero-weight axes receive only their required floors
    unless the positive axes cannot absorb the total (deterministic fallback).
    """
    lower, upper = _bounds(total, lower, upper)
    _need(len(weights) == 4 and all(type(w) in (int, float) and
          math.isfinite(w) and w >= 0 for w in weights),
          "PERCENT_GRID_WEIGHTS")
    positive = [i for i, weight in enumerate(weights) if weight > 0]
    zeros = [i for i in range(4) if i not in positive]
    values = [float(v) for v in lower]
    positive_max = sum(upper[i] for i in positive)
    zero_min = sum(lower[i] for i in zeros)
    if not positive or total >= positive_max + zero_min:
        for i in positive:
            values[i] = float(upper[i])
        remainder = total - sum(values)
        floors = sum(lower[i] for i in zeros)
        capacity = sum(upper[i] - lower[i] for i in zeros)
        _need(floors <= remainder <= floors + capacity,
              "PERCENT_GRID_REMAINDER_CAPACITY")
        extra = remainder - floors
        for i in zeros:
            values[i] = lower[i] + (
                extra * (upper[i] - lower[i]) / capacity if capacity else 0)
    else:
        target = total - zero_min
        low = 0.0
        high = max(upper[i] / weights[i] for i in positive) + 1.0
        for _ in range(68):
            lam = (low + high) / 2
            amount = sum(max(lower[i], min(upper[i],
                             lam * weights[i])) for i in positive)
            if amount < target:
                low = lam
            else:
                high = lam
        for i in positive:
            values[i] = max(lower[i], min(upper[i],
                                high * weights[i]))
    # Exact integer total with bound-safe deterministic largest remainder.
    rounded = [max(lower[i], min(upper[i], int(math.floor(v))))
               for i, v in enumerate(values)]
    left = total - sum(rounded)
    if left > 0:
        order = sorted(range(4),
                       key=lambda i: (-(values[i] - rounded[i]), i))
        while left:
            changed = False
            for i in order:
                if rounded[i] < upper[i]:
                    rounded[i] += 1
                    left -= 1
                    changed = True
                    if not left:
                        break
            _need(changed, "PERCENT_GRID_INTEGER_FILL_BLOCKED")
    elif left < 0:
        order = sorted(range(4), key=lambda i:
                       ((values[i] - rounded[i]), i))
        while left < 0:
            changed = False
            for i in order:
                if rounded[i] > lower[i]:
                    rounded[i] -= 1
                    left += 1
                    changed = True
                    if not left:
                        break
            _need(changed, "PERCENT_GRID_INTEGER_REDUCE_BLOCKED")
    result = tuple(rounded)
    _need(current.legacy.eligible(result, total, lower, upper),
          "PERCENT_GRID_POST_ROUND_INELIGIBLE")
    return result


def _priority(index):
    """Version-stable deterministic spatial sampling without Python hash salt."""
    h = 0xCBF29CE484222325
    for i, value in enumerate(index):
        h ^= ((value + 1) * (i + 11) * 0x9E3779B1) & ((1 << 64) - 1)
        h = (h * 0x100000001B3) & ((1 << 64) - 1)
    return h


@lru_cache(maxsize=16)
def reference_pool(total, lower, upper, points=11, max_pool=2048):
    """Return (B-vector, reference-index, provenance-count), deduplicated.

    Levels use exact integer numerators over (points-1), so odd rating totals
    do not drift due to floating grid arithmetic. A two-pair sum lookup finds
    the maximal feasible shell in O(points^2 log(points)); asymmetrical
    grids expand to nearby lower shells only as needed for candidate diversity.
    No full 4D Cartesian product is materialized.
    """
    lower, upper = _bounds(total, lower, upper)
    _need(type(points) is int and 3 <= points <= 41 and
          type(max_pool) is int and 32 <= max_pool <= 8192,
          "PERCENT_GRID_RESOLUTION")
    denominator = points - 1
    levels = []
    for i in range(4):
        if lower[i] == upper[i]:
            levels.append(((0, lower[i] * denominator),))
        else:
            levels.append(tuple(
                (k, lower[i] * denominator + (upper[i] - lower[i]) * k)
                for k in range(points)))
    first, second = {}, {}
    for a, aval in levels[0]:
        for b, bval in levels[1]:
            first.setdefault(aval + bval, []).append((a, b, aval, bval))
    for c, cval in levels[2]:
        for d, dval in levels[3]:
            second.setdefault(cval + dval, []).append((c, d, cval, dval))
    second_sums = sorted(second)
    limit = total * denominator
    # Merge each first-pair's descending feasible second-pair sums. Avoid
    # materializing an O(points^4) Cartesian product or all possible shells.
    frontier = []
    for amount in first:
        pos = bisect_right(second_sums, limit - amount) - 1
        if pos >= 0:
            heapq.heappush(frontier, (-(amount + second_sums[pos]),
                                      amount, pos))
    _need(bool(frontier), "PERCENT_GRID_EMPTY_SHELL")
    unique = {}
    # A mathematically exact top shell may contain just ONE lattice point
    # when the four ranges differ; that is not acceptable global coverage.
    # Use the largest shell first, then widen only until a useful diversity
    # floor is reached. For the symmetric T2000/m11 example the first shell
    # already provides hundreds of candidates and no widening is needed.
    diversity_goal = min(max_pool, max(32, points * points // 2))
    raw_attempts = 0
    # Even pathological asymmetric caps must not consume unlimited CPU in a
    # large 41-point grid. Reuse existing v290 coverage if this pool is thin.
    raw_limit = max_pool * 8
    while (frontier and len(unique) < diversity_goal and
           raw_attempts < raw_limit):
        shell = -frontier[0][0]
        shell_pairs = []
        while frontier and -frontier[0][0] == shell:
            _, fst, pos = heapq.heappop(frontier)
            snd = second_sums[pos]
            shell_pairs.append((fst, snd))
            if pos > 0:
                heapq.heappush(frontier,
                               (-(fst + second_sums[pos - 1]), fst, pos - 1))
        # Rank raw grid indices with stable hashing when a thick shell has
        # more options than the memory bound; don't prefer lexicographic axes.
        sampled = heapq.nsmallest(
            min(max_pool, raw_limit - raw_attempts),
            ((_priority((a, b, c, d)), (a, b, c, d),
              (aval, bval, cval, dval))
             for fst, snd in shell_pairs
             for a, b, aval, bval in first[fst]
             for c, d, cval, dval in second[snd]),
            key=lambda record: (record[0], record[1]))
        for _, index, raw in sampled:
            raw_attempts += 1
            vector = bounded_proportional(total, lower, upper, raw)
            if vector in unique:
                old_index, count = unique[vector]
                unique[vector] = (old_index, count + 1)
            elif len(unique) < max_pool:
                unique[vector] = (index, 1)
        if len(unique) == max_pool:
            break
    if not unique:
        # For the degenerate all-zero shell, use the existing feasible
        # center rather than dividing by a zero sum or stopping a session.
        center = current._apportion(total, lower, upper, (1, 1, 1, 1))
        return ((center, (0, 0, 0, 0), 1),)
    return tuple((vector, index, count)
                 for vector, (index, count) in sorted(unique.items()))


def choose_points_from_throughput(native_scout_seconds, *,
                                   remaining_calls, seconds_available=None,
                                   confirmation_to_scout_iterations=1.0):
    """Opt-in resolution based on actual fresh-scout wall time and headroom.

    Eleven is the initial *number of normalized per-stat reference points*,
    not eleven Native candidates. A fast 200-call session may choose 22,
    without exhausting all lattice candidates. Missing actual timings or a
    wall-time budget never authorizes an artificial speed-up.
    """
    _need(type(remaining_calls) is int and remaining_calls >= 0,
          "PERCENT_GRID_REMAINING_CALLS")
    _need(seconds_available is None or
          (type(seconds_available) in (int, float) and
           math.isfinite(seconds_available) and seconds_available > 0),
          "PERCENT_GRID_WALL_BUDGET")
    _need(type(confirmation_to_scout_iterations) in (int, float) and
          math.isfinite(confirmation_to_scout_iterations) and
          confirmation_to_scout_iterations >= 1,
          "PERCENT_GRID_ITERATION_RATIO")
    sample = [float(t) for t in native_scout_seconds
              if type(t) in (int, float) and math.isfinite(t) and t > 0]
    if len(sample) < 3 or seconds_available is None:
        return 11
    if remaining_calls < 24:
        return 7
    # Median reduces single-call process startup spikes. Confirmation calls
    # are typically much longer than scout; reserve an explicit 20% of the
    # remaining call budget at the *requested* higher iteration count.
    scout_time = statistics.median(sample[-11:])
    forecast = (scout_time * remaining_calls *
                (0.8 + 0.2 * confirmation_to_scout_iterations))
    headroom = seconds_available / max(forecast, 1.e-9)
    if headroom < 0.50:
        return 5
    if headroom < 0.85:
        return 7
    if headroom < 1.40:
        return 11
    if headroom < 2.25:
        return 15
    if headroom < 4.00:
        return 22
    if remaining_calls >= 120 and headroom >= 7.00:
        return 41
    if remaining_calls >= 80:
        return 31
    return 22


def next_plan(observations, *, total, lower, upper, native_calls_used,
              max_native_calls, reference_points=11, **kwargs):
    """Opt-in v290-compatible plan. Existing precision/local policy retained.

    Replace only a v290 *global* proposal with a reference-grid maximin
    candidate when its observed-distance score is at least as good; the
    original maximin candidate remains in the comparison. No candidate
    consumes a Native call until the unchanged v291 executor accepts it.
    """
    lower, upper = _bounds(total, lower, upper)
    base = current.next_plan(
        observations, total=total, lower=lower, upper=upper,
        native_calls_used=native_calls_used,
        max_native_calls=max_native_calls, **kwargs)
    if base["status"] != "NEXT_NATIVE_PROPOSED" or (
            base["next_request"]["phase"] != "scout") or (
            "GLOBAL" not in base["decision"]):
        return base
    observed = {current.legacy.key(row["target"]) for row in observations}
    if not observed:  # preserve the meaningful initial balanced baseline
        return base
    original = current.legacy.key(base["next_request"]["target"])
    scored = [(original, None)]
    scored += [(v, idx) for v, idx, _ in
               reference_pool(total, lower, upper, reference_points)
               if v not in observed and v != original]
    best, index = max(
        scored,
        key=lambda row: (min(current._distance(row[0], x) for x in observed),
                         tuple(-v for v in row[0])))
    if index is None:
        return base
    updated = dict(base)
    updated["decision"] = "GLOBAL_PERCENT_GRID_MAXIMIN"
    updated["next_request"] = dict(base["next_request"],
                                   target=current.legacy.to_target(best))
    updated["grid_points_per_stat"] = reference_points
    updated["grid_reference_index"] = list(index)
    return updated
