#!/usr/bin/env python3
"""v095 observed-distance exploration and SEM-driven precision, 95% only.

This is a bounded *decision adapter*, not a new optimizer. Feasible neighbors,
statistical judgment and source/native execution stay with v065/v093/SimC.
"""
from __future__ import annotations
import math
import v061_scenario_contract as contract
import v065_v015_scheduler_adapter as policy

SCHEMA="v095_observed_material_and_precision_plan_v1"
Z95=1.959963984540054
class PlanBlocked(ValueError): pass
def need(ok,reason):
    if not ok:raise PlanBlocked(reason)

def material_neighbor(normalized,budget,observations,fraction=0.10):
    """Reuse v065 transfer neighbors; require real B-distance from leader.

    Original policy chooses next normal scout; here we merely supply an
    explicitly wider v065-compatible step for a distinct *measured* alternative.
    No result is declared near-performing until Native DPS evidence exists.
    """
    need(type(fraction) in (int,float) and 0<fraction<=0.5,
         "MATERIAL_FRACTION_RANGE")
    B,lo,hi=policy.bounds(normalized,budget)
    rows=policy.observations_by_vector(observations,B,lo,hi)
    need(rows,"NATIVE_OBSERVED_ANCHOR_REQUIRED")
    leader=policy.leader(rows)
    moved=int(math.ceil(B*fraction-1e-12))
    have=set(rows)
    choices=policy.neighbors(leader,moved,B,lo,hi,have)
    need(bool(choices),"NO_NEW_FEASIBLE_MATERIAL_NEIGHBOR")
    # Same deterministic v065 local mirrored score, no separate optimization.
    choices.sort(key=lambda v:(-policy.score_direction(leader,v,rows),v))
    chosen=choices[0]
    need(sum(abs(a-b) for a,b in zip(leader,chosen))/2 >= B*fraction-1,
         "MATERIAL_TRANSFER_DID_NOT_MOVE_REQUESTED_AMOUNT")
    return {"schema":SCHEMA,"status":"MATERIAL_SCOUT_TARGET_NOT_RUN",
        "source":"v065.neighbors_and_score_direction",
        "base_B":B,"anchor_B":policy.to_target(leader),
        "candidate_B":policy.to_target(chosen),
        "rating_transferred":moved,
        "fraction_B":moved/B,"native_observed":False,
        "near_DPS_not_proven":True}

def precision_plan(first,second,max_iterations,confidence=0.95):
    """95%-only conditional confirmation extension, with explicit stop reasons.

    Uses already measured Native means/SEM; does not change them or interpolate
    DPS. New request must be a new SimC run at a distinct iteration identity.
    """
    need(confidence==0.95,"ONLY_USER_APPROVED_CONFIDENCE_95")
    for x in (first,second):
        need(type(x) is dict and
             x.get("status")=="PASS_NATIVE_DPS_AND_STATIC_CHMV_INPUT"
             and type(x.get("iterations")) is int and x["iterations"]>0
             and type(x.get("dps_mean")) in (float,int) and math.isfinite(x["dps_mean"])
             and type(x.get("dps_sem")) in (float,int) and
             math.isfinite(x["dps_sem"]) and x["dps_sem"]>=0,
             "REAL_NATIVE_STAT_RECEIPT_REQUIRED")
    need(type(max_iterations) is int and max_iterations>0,
         "MAX_ITERATIONS_INT_REQUIRED")
    baseline=max(first["iterations"],second["iterations"])
    need(max_iterations>=baseline,"PRECISION_MAX_LT_CURRENT")
    half=Z95*math.hypot(first["dps_sem"],second["dps_sem"])
    delta=abs(first["dps_mean"]-second["dps_mean"])
    separated=delta>half
    if separated:
        reason="95_PERCENT_ALREADY_SEPARATED"
        target=baseline
    elif max_iterations<=baseline:
        reason="TYPED_ITERATION_LIMIT_REACHED"
        target=baseline
    else:
        # SEM~1/sqrt(n), an approximate future budget estimate only.
        # Avoid spending a huge quota based on a nearly zero observed gap:
        # cap via scenario, do not call SimC without explicit user budget.
        factor=(half/max(delta,1.0))**2
        estimate=math.ceil(baseline*max(1.,factor))
        target=min(max_iterations,max(baseline+1,estimate))
        reason="UNRESOLVED_AT_95_PERCENT_REQUEST_NEW_INDEPENDENT_CONFIRMATIONS"
    return {"schema":SCHEMA,"confidence":0.95,
        "current_difference":delta,"current_95_halfwidth":half,
        "current_separated_at_95":separated,
        "current_max_iterations":baseline,
        "suggested_new_iterations_each":target,
        "requires_two_fresh_simc_runs":target>baseline,
        "reason":reason,"global_optimum_proven":False,
        "accuracy_claim":"ESTIMATED_EXTRA_SAMPLES_NOT_GUARANTEED"}

