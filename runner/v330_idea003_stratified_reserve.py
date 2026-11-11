"""IDEA-003: replace ONLY v306's existing global-reserve coordinate selection.

Use the SAME v290 bounded global candidate pool, partitioned into deterministic
Voronoi cells in the feasible CHMV domain. Cell mass is a finite-pool
occupancy proxy, NOT an exact equal-volume simplex or DPS estimate. Existing
local moves, initial global order, reserve cadence and confirmation unchanged.
"""
from __future__ import annotations
import functools
from fractions import Fraction
import v290_multiscale_adaptive_policy as base
import v306_seed_retained_coarse_escape_regions as prior

SCHEMA="v330_idea003_stratified_global_reserve_optin_v1"
SETTINGS={"candidate_pool_count":192,"max_cells":12,
          "distance":"half_L1_rating","priority":"observed_count_over_pool_mass_then_maximin",
          "cell_mass_is_finite_pool_proxy":True}

def cell_for(v,centers):
    return min(range(len(centers)),key=lambda i:(base._distance(v,centers[i]),i))

@functools.lru_cache(maxsize=8)
def partition(total,lower,upper):
    pool=tuple(base._global_pool(total,lower,upper,SETTINGS["candidate_pool_count"]))
    if not pool:
        return (),(),()
    centers=[pool[0]]
    while len(centers)<min(SETTINGS["max_cells"],len(pool)):
        centers.append(max((v for v in pool if v not in centers),
            key=lambda v:(min(base._distance(v,c) for c in centers),
                          tuple(-x for x in v))))
    centers=tuple(centers)
    cells=tuple(tuple(v for v in pool if cell_for(v,centers)==i)
                for i in range(len(centers)))
    return pool,centers,cells

def coverage(observations,*,total,lower,upper):
    _,centers,cells=partition(total,tuple(lower),tuple(upper))
    counts=[0]*len(centers)
    seen={prior.vector(r) for r in observations if r["phase"]=="scout"}
    for v in seen: counts[cell_for(v,centers)]+=1
    return {"observed_unique_scouts":len(seen),"occupied_cells":sum(n>0 for n in counts),
            "counts":counts,"cell_pool_mass":[len(c) for c in cells],
            "cell_centers":[list(v) for v in centers]}

def choose(observations,*,total,lower,upper):
    _,centers,cells=partition(total,tuple(lower),tuple(upper))
    seen={prior.vector(r) for r in observations if r["phase"]=="scout"}
    if not seen: return None
    counts=[0]*len(centers)
    for v in seen: counts[cell_for(v,centers)]+=1
    available=[]
    for i,cell in enumerate(cells):
        fresh=[v for v in cell if v not in seen]
        if fresh:
            point=max(fresh,key=lambda v:(min(base._distance(v,x) for x in seen),
                                          tuple(-x for x in v)))
            distance=min(base._distance(point,x) for x in seen)
            available.append((Fraction(counts[i],len(cell)),-distance,i,point))
    if not available:return None
    return min(available)[-1]

def next_plan(observations,*,total,lower,upper,max_native_calls,
              scout_iterations,confirmation_iterations,
              initial_global_calls=160,confirmation_calls=8):
    proposal=prior.next_plan(observations,total=total,lower=lower,upper=upper,
        max_native_calls=max_native_calls,scout_iterations=scout_iterations,
        confirmation_iterations=confirmation_iterations,
        initial_global_calls=initial_global_calls,
        confirmation_calls=confirmation_calls)
    action=proposal.get("next_request")
    if action is None or action["adaptive_stage"]!="global_reserve":
        return dict(proposal,schema=SCHEMA)
    candidate=choose(observations,total=total,lower=lower,upper=upper)
    if candidate is None:
        return dict(proposal,schema=SCHEMA)
    seen={prior.vector(r) for r in observations if r["phase"]=="scout"}
    if not base.legacy.eligible(candidate,total,lower,upper) or candidate in seen:
        raise ValueError("V330_STRATIFIED_INVALID_OR_DUPLICATE_CHMV")
    return dict(proposal,schema=SCHEMA,decision="V330_STRATIFIED_GLOBAL_RESERVE",
                next_request=dict(action,target=base.legacy.to_target(candidate)))
