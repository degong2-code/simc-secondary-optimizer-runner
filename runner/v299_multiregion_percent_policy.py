#!/usr/bin/env python3
"""Opt-in multi-region percentage-grid scout/refinement policy.

Pure deterministic proposal logic only. Does not simulate DPS, infer item
effects, or change original v290/v291 production defaults. All output targets
remain exact integer B inside the caller-verified lower/upper constraints.
"""
from __future__ import annotations

import itertools
import math

import v290_multiscale_adaptive_policy as base
import v298_adaptive_percent_grid as grid

SCHEMA="v299_multiregion_percentage_grid_experimental_v1"


def _diagonal_neighbors(anchor, desired_step, total, lower, upper, observed):
    """Move two distinct stats up and two down, not only pairwise axes."""
    emitted=set()
    for plus in itertools.combinations(range(4), 2):
        minus=tuple(i for i in range(4) if i not in plus)
        for source in (minus,minus[::-1]):
            moves=min(desired_step,
                      *(anchor[source[k]]-lower[source[k]]
                        for k in range(2)),
                      *(upper[plus[k]]-anchor[plus[k]]
                        for k in range(2)))
            if moves<=0:
                continue
            candidate=list(anchor)
            for i in range(2):
                candidate[plus[i]]+=moves
                candidate[source[i]]-=moves
            vec=tuple(candidate)
            if (vec not in observed and vec not in emitted and
                    base.legacy.eligible(vec,total,lower,upper)):
                emitted.add(vec)
                yield vec, 2*moves


def _regions(by_vector, *, total, max_regions=5):
    """Represent far-apart observed modes; each mode receives local budget.

    Score is measured Native mean - a small SEM term, NOT predicted true DPS.
    Regions deliberately preserve a lower observed mode if separated in CHMV.
    """
    ranked=sorted(by_vector, key=lambda v:(
        -(by_vector[v]["dps_mean"]-
          0.5*min(by_vector[v]["dps_sem"],
                  by_vector[v]["dps_mean"]*.02)),v))
    threshold=max(1,round(total*.10))
    result=[]
    for vec in ranked:
        if all(base._distance(vec, r)>=threshold for r in result):
            result.append(vec)
            if len(result)>=max_regions:
                break
    return result


def _local_region_proposal(anchor, observed, *, total, lower, upper,
                           reference_points):
    """Near-region directions include diagonal stat transfers.

    Use percentage scales and measured local coverage density, never a
    permanent absolute-rating step. Novelty tie-breaks are deterministic.
    """
    coverage=sum(base._distance(vec,anchor)<=total*.10
                 for vec in observed)
    index=min(len(base.SCALES)-1,int(math.log2(max(1,coverage//4)+1)))
    index_range=range(max(0,index-1),min(len(base.SCALES),index+2))
    candidates=set()
    for i in index_range:
        fraction=base.SCALES[i]
        desired=max(1,round(total*fraction))
        candidates.update(v for v,_ in base._bounded_fraction_neighbors(
            anchor,desired,total,lower,upper,observed))
        diagonal_step=max(1,round(desired/2))
        candidates.update(v for v,_ in _diagonal_neighbors(
            anchor,diagonal_step,total,lower,upper,observed))
    if not candidates:
        return None
    # Preserve coverage in the target region, but remain close enough that
    # measured improvements can form a finer follow-up anchor.
    return max(candidates,key=lambda v:(
        min(base._distance(v,o) for o in observed),
        -base._distance(v,anchor),tuple(-x for x in v)))


def next_plan(observations, *, total, lower, upper, native_calls_used,
              max_native_calls, reference_points=11,
              initial_global_calls=None, **kwargs):
    """Broad grid + low-discrepancy scout, then separate regional refinements.

    v290's precision/seed decisions remain in charge. The global phase
    assigns about 40% of calls (at most 200), not all lattice points.
    For tiny runs this stays close to original v290; no hard 200-call gate.
    """
    lower,upper=grid._bounds(total,lower,upper)
    grid._need(type(reference_points) is int and 3<=reference_points<=41,
               "PERCENT_GRID_RESOLUTION")
    grid._need(initial_global_calls is None or
               (type(initial_global_calls) is int and
                1<=initial_global_calls<max_native_calls),
               "MULTIREGION_INITIAL_GLOBAL_CALLS")
    original=base.next_plan(
        observations,total=total,lower=lower,upper=upper,
        native_calls_used=native_calls_used,
        max_native_calls=max_native_calls,**kwargs)
    if (original["status"]!="NEXT_NATIVE_PROPOSED" or
            original["next_request"]["phase"]=="precision"):
        return original
    by_vector,_=base._best_by_vector(observations,total,lower,upper)
    observed=set(by_vector)
    if not observed:
        return original
    global_target=(initial_global_calls
                   if initial_global_calls is not None else
                   min(200,max(8,int(max_native_calls*.40)),
                       max(8,max_native_calls-8)))
    # Retain periodic global exploration even after initial survey.
    global_due=(len(observed)<global_target or
                (len(observations)>global_target and
                 len(observations)%23==0))
    if global_due:
        # Sample across the actual feasible simplex AND normalized lattice.
        # A grid point never evicts the original v290 candidate before its
        # distance to all previously measured points has been compared.
        pool=set(v for v,_,_ in grid.reference_pool(
            total,lower,upper,reference_points))
        pool.update(base._global_pool(
            total,lower,upper,min(256,max(64,2*global_target))))
        pool.add(base.legacy.key(original["next_request"]["target"]))
        candidates=pool-observed
        if candidates:
            target=max(candidates,key=lambda v:(
                min(base._distance(v,o) for o in observed),
                tuple(-x for x in v)))
            result=dict(original)
            result["decision"]="MULTIREGION_GLOBAL_COVERAGE"
            result["next_request"]=dict(
                original["next_request"],
                phase="scout",target=base.legacy.to_target(target),
                iterations=kwargs.get("scout_iterations",64))
            result["grid_points_per_stat"]=reference_points
            return result
    centers=_regions(by_vector,total=total)
    if centers:
        # Best measured region is visited twice as often as each other
        # well-separated region. Round-robin avoids starving another mode.
        cycle=[0]+list(range(len(centers)))
        offset=max(0,native_calls_used-global_target)
        for attempt in range(len(cycle)):
            region=centers[cycle[(offset+attempt)%len(cycle)]]
            target=_local_region_proposal(
                region,observed,total=total,lower=lower,upper=upper,
                reference_points=reference_points)
            if target is None:
                continue
            result=dict(original)
            result["decision"]="MULTIREGION_LOCAL_PERCENT_DIAGONAL"
            result["next_request"]=dict(
                original["next_request"],phase="scout",
                target=base.legacy.to_target(target),
                iterations=kwargs.get("scout_iterations",64))
            result["regional_anchor"]=list(region)
            result["regional_center_count"]=len(centers)
            return result
    return original
