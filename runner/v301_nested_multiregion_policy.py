#!/usr/bin/env python3
"""Opt-in nested percentage-grid refinement, preserving v298/v299/v300 seals.

Resolutions: 6 (20%), 11 (10%), 21 (5%), 41 (2.5%).
Each higher-resolution *integer B vector pool* includes every candidate
from the lower resolution. A fixed Native-call budget can still produce a
different proposal order, so stronger DPS is NOT guaranteed by nesting.
"""
from __future__ import annotations
from functools import lru_cache

import v290_multiscale_adaptive_policy as legacy
import v298_adaptive_percent_grid as grid
import v299_multiregion_percent_policy as regions
import v300_multiregion_throughput_resolution as throughput

SCHEMA="v301_nested_percentage_multiregion_experiment_v1"
LEVELS=(6,11,21,41)


@lru_cache(maxsize=16)
def nested_reference_pool(total, lower, upper, points=11):
    """Stable deduplicated final integer candidates, monotone by resolution.

    Each level is computed by the previously tested bounded proportional
    projection including exact integer sum, floors and caps. We explicitly
    UNION previous *final candidate vectors*, not merely raw reference
    coordinates, so changing the maximum-shell normalization cannot remove
    a lower-resolution candidate. No SimC is called here.
    """
    lower,upper=grid._bounds(total,lower,upper)
    grid._need(type(points) is int and points in LEVELS,
               "NESTED_PERCENT_GRID_LEVEL")
    all_vectors={}
    for level in LEVELS:
        if level>points:
            break
        for vector,index,count in grid.reference_pool(
                total,lower,upper,level,max_pool=2048):
            if vector not in all_vectors:
                all_vectors[vector]={
                    "first_level":level,"reference_index":index,
                    "provenance_count":count}
    return tuple((v,all_vectors[v]) for v in sorted(all_vectors))


def choose_points_from_throughput(native_scout_seconds, *,
                                  remaining_calls,seconds_available=None,
                                  confirmation_to_scout_iterations=1.0):
    """Measured-only, Nested 6/11/21/41 family.

    v300 history remains immutable for prior experimental session seals.
    Its provisional measured-throughput tiers are mapped to the nearest
    *lower* nested level; never invent Native timing.
    """
    previous=throughput.choose_points_from_throughput(
        native_scout_seconds,remaining_calls=remaining_calls,
        seconds_available=seconds_available,
        confirmation_to_scout_iterations=confirmation_to_scout_iterations)
    if previous<11:
        return 6
    if previous<21:
        return 11
    if previous<41:
        return 21
    return 41


def next_plan(observations, *, total,lower,upper,native_calls_used,
              max_native_calls,reference_points=11,**kwargs):
    """v299's multi-region local/precision; nested global survey candidates."""
    lower,upper=grid._bounds(total,lower,upper)
    grid._need(type(reference_points) is int and reference_points in LEVELS,
               "NESTED_PERCENT_GRID_LEVEL")
    proposed=regions.next_plan(
        observations,total=total,lower=lower,upper=upper,
        native_calls_used=native_calls_used,
        max_native_calls=max_native_calls,
        reference_points=reference_points,**kwargs)
    if proposed.get("decision")!="MULTIREGION_GLOBAL_COVERAGE":
        return proposed
    observed=set(legacy._best_by_vector(
        observations,total,lower,upper)[0])
    if not observed:
        return proposed
    # Retain v299's low-discrepancy/global point as a fair competitor. A
    # higher-resolution pool is a strict superset but the chosen request can
    # change when the budget/schedule is fixed.
    all_candidates={v for v,_ in nested_reference_pool(
        total,lower,upper,reference_points)}
    all_candidates.add(legacy.legacy.key(proposed["next_request"]["target"]))
    choices=all_candidates-observed
    if not choices:
        return proposed
    best=max(choices,key=lambda v:(
        min(legacy._distance(v,o) for o in observed),
        tuple(-k for k in v)))
    updated=dict(proposed)
    updated["decision"]="NESTED_MULTIREGION_GLOBAL_COVERAGE"
    updated["next_request"]=dict(
        proposed["next_request"],target=legacy.legacy.to_target(best))
    updated["grid_points_per_stat"]=reference_points
    updated["nested_levels_included"]=[
        lev for lev in LEVELS if lev<=reference_points]
    return updated
