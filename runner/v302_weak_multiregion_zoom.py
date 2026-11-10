#!/usr/bin/env python3
"""Experimental weak-shortlist / multi-region six-level grid policy primitives.

Pure geometry and selection, NO SimC, no item-effect model and no replacement
of v290. Tested on one historical real profile; production promotion requires
more same-cost multi-spec evidence. Each CHMV vector is an exact integer B.
"""
from __future__ import annotations

import itertools
import math

import v290_multiscale_adaptive_policy as base
import v298_adaptive_percent_grid as bounds

SCHEMA="v302_weak_multiregion_six_level_zoom_experimental_v1"
GLOBAL_LEVELS=(11,21,41)


def _level(lo, hi, index, count):
    """Exact rational grid; m21 includes m11 raw coordinates."""
    return lo + ((hi-lo)*index*2 + count-1)//(2*(count-1))


def residual_lattice(total, lower, upper, points=21, *,
                     center=None, radius=None):
    """Feasible simplex grid, rotate the exact residual axis.

    A local 6-level lattice is in a radius-limited 4D bounding box, with the
    4th rating calculated exactly from B rather than accepting rounding drift.
    Multiple dependent-axis orientations avoid bias against versatility.
    This does not require a special gem, no-O or a 60% cap: caller owns bounds.
    """
    lower, upper=bounds._bounds(total, lower, upper)
    bounds._need(type(points) is int and points in (*GLOBAL_LEVELS,6),
                 "P2_ZOOM_RESOLUTION")
    if center is None:
        bounds._need(points in GLOBAL_LEVELS and radius is None,
                     "P2_ZOOM_GLOBAL_PARAMETERS")
    else:
        bounds._need(type(center) in (list,tuple) and len(center)==4
                     and all(type(x) is int for x in center)
                     and base.legacy.eligible(center,total,lower,upper)
                     and type(radius) is int and 1<=radius<=total
                     and points==6, "P2_ZOOM_LOCAL_PARAMETERS")
    axes=[]
    for i in range(4):
        lo=lower[i] if center is None else max(lower[i],center[i]-radius)
        hi=upper[i] if center is None else min(upper[i],center[i]+radius)
        axes.append(tuple(sorted(set(
            _level(lo,hi,k,points) for k in range(points)))))
    result=set()
    if center is not None:
        result.add(tuple(center))
    for residual_axis in range(4):
        free=tuple(i for i in range(4) if i!=residual_axis)
        for vals in itertools.product(*(axes[i] for i in free)):
            remaining=total-sum(vals)
            if not lower[residual_axis]<=remaining<=upper[residual_axis]:
                continue
            if (center is not None and
                    abs(remaining-center[residual_axis])>radius):
                continue
            vec=[0]*4
            for i,value in zip(free,vals):
                vec[i]=value
            vec[residual_axis]=remaining
            result.add(tuple(vec))
    return tuple(sorted(result))


def bounded_farthest(pool, count, *, seed, exclude=()):
    """Deterministic maximin scheduling with incremental nearest distances.

    O(N*scheduled) rather than recomputing distances to all old choices.
    The set of generated points may be large; only scheduled candidates cause
    actual Native work. No arbitrary candidate is "95% better" here.
    """
    bounds._need(type(count) is int and count>=0 and
                 type(seed) in (tuple,list) and len(seed)==4,
                 "P2_ZOOM_GLOBAL_SCHEDULE")
    chosen=[]
    excluded=set(exclude)
    feasible=tuple(p for p in pool if p not in excluded)
    nearest=[base._distance(p,seed) for p in feasible]
    marked=[False]*len(feasible)
    for _ in range(min(count,len(feasible))):
        best=max((i for i in range(len(feasible)) if not marked[i]),
                 key=lambda i:(nearest[i],tuple(-x for x in feasible[i])),
                 default=None)
        if best is None:
            break
        vec=feasible[best]
        chosen.append(vec)
        marked[best]=True
        for i,p in enumerate(feasible):
            if not marked[i]:
                near=base._distance(vec,p)
                if near<nearest[i]:
                    nearest[i]=near
    return tuple(chosen)


def loose_regions(scout_observations, *, total, max_regions=8,
                  relative_loss=.03, minimum_distance_fraction=.08):
    """Broad optimistic screening, then preserve spatially different modes.

    This uses measurement uncertainty for *exploration eligibility* only.
    It does NOT claim frequentist global/family-wise 95% confirmation.
    """
    bounds._need(type(max_regions) is int and 1<=max_regions<=32 and
                 type(relative_loss) in (int,float) and
                 .0<=relative_loss<=.20 and
                 type(minimum_distance_fraction) in (int,float) and
                 .0<=minimum_distance_fraction<=1,
                 "P2_ZOOM_LOOSE_REGION_PARAMETERS")
    rows={}
    for r in scout_observations:
        vec=tuple(r["vector"] if "vector" in r
                  else base.legacy.key(r["target"]))
        mean,sem=r["dps_mean"],r["dps_sem"]
        bounds._need(type(mean) in (int,float) and mean>0 and
                     math.isfinite(mean) and type(sem) in (int,float)
                     and sem>=0 and math.isfinite(sem),
                     "P2_ZOOM_NATIVE_STATS_REQUIRED")
        if vec not in rows or r.get("iterations",0)>rows[vec].get("iterations",0):
            rows[vec]=r
    bounds._need(bool(rows),"P2_ZOOM_NO_OBSERVATIONS")
    ranked=sorted(rows, key=lambda v:(-rows[v]["dps_mean"],v))
    leader=rows[ranked[0]]
    cutoff=leader["dps_mean"]-max(
        relative_loss*leader["dps_mean"],1.96*leader["dps_sem"])
    eligible=[v for v in ranked
              if rows[v]["dps_mean"]+1.96*rows[v]["dps_sem"]>=cutoff]
    selected=[]
    mindist=total*minimum_distance_fraction
    for v in eligible:
        if all(base._distance(v,old)>=mindist for old in selected):
            selected.append(v)
        if len(selected)==max_regions:
            break
    return {
        "centers":tuple(selected),
        "eligible_count":len(eligible),
        "cutoff":cutoff,
        "highest_scout_mean":leader["dps_mean"],
        "95_percent_claim":False,
    }


def region_candidates(total, lower, upper, centers, *,
                      local_points=6, radius_fraction=.065,
                      exclude=(), per_region=12):
    """Small local grids in each selected mode; preserve boundary/floor.

    A radius is relative to B, not to a fixed rating or an individual item
    level. Uses the same four-axis residual grid construction as global.
    """
    bounds._need(type(local_points) is int and local_points==6
                 and type(radius_fraction) in (int,float)
                 and 0<radius_fraction<=.50
                 and type(per_region) is int and 1<=per_region<=512,
                 "P2_ZOOM_LOCAL_GRID_PARAMETERS")
    radius=max(1,round(total*radius_fraction))
    used=set(exclude)
    plans=[]
    for index,center in enumerate(centers):
        pool=residual_lattice(total,lower,upper,6,
                              center=center,radius=radius)
        selected=bounded_farthest(pool,per_region,seed=center,exclude=used)
        for vec in selected:
            plans.append({"region_index":index,"anchor":tuple(center),
                          "target":vec,"radius":radius})
            used.add(vec)
    return tuple(plans)
