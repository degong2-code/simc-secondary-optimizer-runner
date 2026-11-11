"""IDEA-002 v328 opt-in: evidence-gated radius for existing v306 regions.

Pure deterministic SimC-native-history policy. No source/profile inference,
DPS surrogate, statistics claim or new Native executor. Initial global seeds,
seed retention, global reserve and final confirmations stay owned by v306.
"""
from __future__ import annotations
import copy
import math
import v290_multiscale_adaptive_policy as base
import v303_adaptive_region_resource_policy as resources
import v306_seed_retained_coarse_escape_regions as previous

SCHEMA="v328_idea002_evidence_gated_radius_optin_v2"
class PolicyBlocked(ValueError):pass
def need(ok,why):
    if not ok:raise PolicyBlocked("V328_"+why)

def radius_decision(region,*,total):
    radius=region["radius"]
    local=region["local"]
    need(type(total) is int and total>0
         and type(radius) in (int,float)
         and resources.MIN_RADIUS<=radius<=resources.MAX_RADIUS
         and type(local) is list, "EXACT_MEASURED_RADIUS_REQUIRED")
    if len(local)<2:
        return radius,"BASELINE_NO_LOCAL_EVIDENCE"
    seed,best=region["seed"],region["best"]
    for row in (seed,best):
        need(all(type(row.get(k)) in (int,float)
             and math.isfinite(row[k]) and row[k]>=0
             for k in ("dps_mean","dps_sem")),"REAL_NATIVE_DPS_SEM_REQUIRED")
    gain=resources.score(best)-resources.score(seed)
    noise=math.hypot(seed["dps_sem"],best["dps_sem"])
    z=gain/max(noise,1e-9)
    center=region["center"]
    need(type(center) is tuple and len(center)==4
         and sum(center)==total and
         all(type(x) is int for x in center),
         "MEASURED_SEED_CENTER_BUDGET")
    origin=previous.vector(seed)
    edge=max(abs(a-b) for a,b in zip(center,origin))/max(1,total*radius)
    # A non-significant gain is not a reason to abandon a region: expand
    # a trial proposal instead of shrinking on noisy observations.
    if z<0.9:
        return min(resources.MAX_RADIUS,radius*1.6),"EXPAND_UNCERTAIN"
    if edge>=0.7:
        return min(resources.MAX_RADIUS,radius*1.6),"EXPAND_MEASURED_EDGE"
    if len(local)>=8 and z>=1.5 and edge<0.35:
        return max(resources.MIN_RADIUS,radius*.85),"CONTRACT_STABLE"
    return radius,"KEEP_COVERAGE"

def next_plan(observations,*,total,lower,upper,max_native_calls,
              scout_iterations,confirmation_iterations,
              initial_global_calls=160,confirmation_calls=8):
    proposal=previous.next_plan(
        observations,total=total,lower=lower,upper=upper,
        max_native_calls=max_native_calls,
        scout_iterations=scout_iterations,
        confirmation_iterations=confirmation_iterations,
        initial_global_calls=initial_global_calls,
        confirmation_calls=confirmation_calls)
    request=proposal.get("next_request")
    if request is None or request.get("adaptive_stage")!="regional":
        return dict(proposal,schema=SCHEMA)
    # v329-v1 changed pairwise methods into GRID during some expansions.
    # v2 preserves the existing v306 pairwise coordinates and method/cadence;
    # change ONLY genuine GRID/FALLBACK region proposals.
    if request.get("hybrid_method") in previous.PAIRS:
        return dict(proposal,schema=SCHEMA)
    need(request.get("hybrid_method") in
         (previous.GRID,previous.FALLBACK),
         "UNKNOWN_REGIONAL_METHOD_NOT_RADIUS_ABLATION")
    state=previous._measured_region_state(
        observations,total=total,initial_global_calls=initial_global_calls)
    rid=request["region_id"]
    need(rid in state,"REGION_ID_NOT_SOURCE_MEASURED")
    info=state[rid]
    radius,reason=radius_decision(info,total=total)
    if reason in ("BASELINE_NO_LOCAL_EVIDENCE","KEEP_COVERAGE") or math.isclose(
            radius,info["radius"],rel_tol=0,abs_tol=1e-12):
        return dict(proposal,schema=SCHEMA)
    seen={previous.vector(r) for r in observations if r["phase"]=="scout"}
    candidate,used_radius=resources._candidate(
        total,lower,upper,info["center"],radius,seen)
    if candidate is None:
        return dict(proposal,schema=SCHEMA)
    need(base.legacy.eligible(candidate,total,lower,upper)
         and candidate not in seen,"PROPOSED_CHMV_INVALID_OR_SEEN")
    new=copy.deepcopy(proposal)
    new["next_request"].update(
        target=base.legacy.to_target(candidate),region_id=rid,
        region_center=list(info["center"]),
        region_radius_fraction=min(resources.MAX_RADIUS,max(
            resources.MIN_RADIUS,used_radius/total)),
        hybrid_method=previous.GRID)
    new["decision"]="V328_IDEA002_"+reason
    return dict(new,schema=SCHEMA)
