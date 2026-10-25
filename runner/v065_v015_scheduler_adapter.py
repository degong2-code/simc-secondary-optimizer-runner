#!/usr/bin/env python3
"""v065: v015-derived bounded adaptive scout policy for the v064 evaluator.

v015 authentic source SHA256 a44f73cf232c8204dbe958e79fe50f111e68654ac583a1170a283f16035c0ec3.
Its neighbors/choose_next/confirmation_pair/judge *decision principles* are
ported, not its Mage-only SimC input, rigid 3000-rating budget, +165 offset,
historical seven-sample loader, or one-shot execution harness.

Only v064 evaluates new SimC input/JSON2. This scheduler never computes any
item, embellishment, trinket, gem, or proc effect.
Original v015/v016 bytes are untouched and stored only in user handoff ZIP.
"""
from __future__ import annotations
import math
from collections import defaultdict
import v061_scenario_contract as contract
import v063_numeric_injection as injection
import v064_adaptive_evaluator_port as evaluator

STATS=contract.STATS
SCHEMA="v065_original_v015_policy_scheduler_v1"
SOURCE_V015_SHA256="a44f73cf232c8204dbe958e79fe50f111e68654ac583a1170a283f16035c0ec3"
SOURCE_V016_SHA256="7c49d7ca095e8864b673715d70d9851d676b44aeed99f8d769419492fcd14712"

class SchedulerBlocked(ValueError):pass

def need(ok,code):
    if not ok: raise SchedulerBlocked(code)

def key(target):
    contract.vector(target,"OBSERVED_TARGET")
    return tuple(target[k] for k in STATS)

def to_target(values):
    need(type(values) in (tuple,list) and len(values)==4,"VECTOR_FORMAT")
    return dict(zip(STATS,values))

def bounds(normalized,budget):
    need(normalized.get("schema")==contract.SCHEMA,
         "NORMALIZED_CONTRACT_REQUIRED")
    need(budget.get("schema")=="v062_representative_static_budget_v1" and
         budget.get("scenario_digest")==normalized["scenario_digest"],
         "BUDGET_BOUND_TO_OTHER_SCENARIO")
    total=budget["budget"]["T_official"]
    need(type(total) is int and total>0,"OFFICIAL_T_NOT_CALCULATED")
    floors=budget["effective_floor_if_possible"]
    need(type(floors) is dict,"STATIC_L_FLOOR_MISSING")
    caps={s:math.floor(total*normalized["scenario"]["constraints"]
                       ["max_fraction"][s]+1e-9) for s in STATS}
    lower=tuple(floors[s] for s in STATS)
    upper=tuple(caps[s] for s in STATS)
    need(all(0<=a<=b for a,b in zip(lower,upper)) and
         sum(lower)<=total<=sum(upper),"BOUNDS_NOT_FEASIBLE")
    return total,lower,upper

def eligible(vector,total,lower,upper):
    return (type(vector) is tuple and len(vector)==4
        and all(type(v) is int for v in vector)
        and sum(vector)==total
        and all(low<=v<=high for v,low,high in zip(vector,lower,upper)))

def neighbors(anchor,step,total,lower,upper,observed_vectors):
    """v015 neighbors: move step from each rating to each other rating."""
    need(type(step) is int and 1<=step<=total,
         "SCOUT_STEP_NOT_POSITIVE_INT")
    need(eligible(anchor,total,lower,upper),"ANCHOR_OUTSIDE_BUDGET_BOUNDS")
    found=[]
    for source in range(4):
        for dest in range(4):
            if source==dest:continue
            nxt=list(anchor);nxt[source]-=step;nxt[dest]+=step
            vector=tuple(nxt)
            if eligible(vector,total,lower,upper) and \
               vector not in observed_vectors and vector not in found:
                found.append(vector)
    return found

def observations_by_vector(records,total,lower,upper):
    need(type(records) is list,"OBSERVATION_ROWS")
    rows=defaultdict(list)
    for r in records:
        need(type(r) is dict and
             r.get("status")=="PASS_NATIVE_DPS_AND_RATING",
             "UNVERIFIED_NATIVE_STAT_RESULT")
        vector=key(r["target"])
        need(eligible(vector,total,lower,upper),
             "OBSERVATION_OUTSIDE_OFFICIAL_T_OR_L")
        need(type(r.get("dps_mean")) in (float,int) and
             math.isfinite(r["dps_mean"]) and r["dps_mean"]>0,
             "OBSERVATION_INVALID_DPS")
        need(type(r.get("dps_sem")) in (float,int) and
             math.isfinite(r["dps_sem"]) and r["dps_sem"]>=0,
             "OBSERVATION_INVALID_SEM")
        rows[vector].append(r)
    return dict(rows)

def last(obs):
    return obs[-1]

def leader(rows):
    need(bool(rows),"NO_NATIVE_SCOUT_ANCHOR")
    return max(rows,key=lambda v:(last(rows[v])["dps_mean"],
                                  tuple(-x for x in v)))

def score_direction(anchor,candidate,rows):
    """v015 mirrored DPS is ORDERING ONLY, not a performance estimator."""
    reflected=tuple(2*a-b for a,b in zip(anchor,candidate))
    if reflected in rows:
        return max(-2500.0,min(2500.0,
           last(rows[anchor])["dps_mean"] -
           last(rows[reflected])["dps_mean"]))
    return 0.0

def choose_next(rows,step,total,lower,upper):
    eligible_obs={vec:obs for vec,obs in rows.items()
                  if eligible(vec,total,lower,upper)}
    need(bool(eligible_obs),"NO_ELIGIBLE_HISTORICAL_ANCHOR")
    anchor=leader(eligible_obs)
    nexts=neighbors(anchor,step,total,lower,upper,set(rows))
    if not nexts:
        for vector in sorted(eligible_obs,
                             key=lambda v:last(eligible_obs[v])["dps_mean"],
                             reverse=True):
            nexts=neighbors(vector,step,total,lower,upper,set(rows))
            if nexts:anchor=vector;break
    need(bool(nexts),"NO_MORE_FEASIBLE_NEIGHBORS")
    nexts.sort(key=lambda vec:(-score_direction(anchor,vec,rows),vec))
    selected=nexts[0]
    return anchor,selected,{
        "method":"V015_LOCAL_MIRROR_FOR_SCOUT_ORDER_ONLY",
        "mirror_score_dps":score_direction(anchor,selected,rows),
        "observed_vector_count":len(rows),
        "source_sha256":SOURCE_V015_SHA256,
        "derived_new_module_not_original_v015":True}

def confirmation_pair(rows,total,lower,upper):
    eligible_obs={v:obs for v,obs in rows.items()
                  if eligible(v,total,lower,upper)}
    need(len(eligible_obs)>=2,"NEED_TWO_DISTINCT_FEASIBLE_TARGETS")
    return sorted(eligible_obs,
                  key=lambda v:last(eligible_obs[v])["dps_mean"],
                  reverse=True)[:2]

def fresh_confirmation_judgment(pair,independent):
    """Only new confirmation measurements; seed-difference evidence required."""
    need(type(pair) in (list,tuple) and len(pair)==2 and
         set(pair)==set(independent),"FRESH_CONFIRMATION_PAIR_REQUIRED")
    a,b=pair; r1,r2=independent[a],independent[b]
    need(all(r.get("status")=="PASS_NATIVE_DPS_AND_RATING"
             for r in (r1,r2)),"CONFIRM_NOT_NATIVE_VALIDATED")
    diff=r1["dps_mean"]-r2["dps_mean"]
    half=1.9599639854*math.hypot(r1["dps_sem"],r2["dps_sem"])
    s1=r1.get("simc_seed");s2=r2.get("simc_seed")
    distinct=s1 is not None and s2 is not None and s1!=s2
    return {"schema":"v065_two_fresh_confirmations_v1",
        "method":"V015_FRESH_SELECTED_PAIR_ONLY_NORMAL_APPROX",
        "first":to_target(a),"second":to_target(b),
        "first_minus_second_dps":diff,"approx_ci95_halfwidth":half,
        "distinct_simc_seeds_observed":distinct,
        "pairwise_direction_supported":abs(diff)>half and distinct,
        "statistical_separation_approx95_without_seed_claim":abs(diff)>half,
        "global_optimum_proven":False,
        "historical_pass_not_rerun":True}

def initial_state(normalized,budget,prior_observations,step=100,
                  scout_max=3,confirmation_runs=2):
    """Reusable state; no Native call or simulator invocation."""
    total,lower,upper=bounds(normalized,budget)
    need(type(scout_max) is int and 0<=scout_max<=3,
         "SCOUT_COUNT_LIMIT_V015_POLICY")
    need(confirmation_runs==2,"REQUIRE_TWO_FRESH_CONFIRMATIONS")
    need(type(step) is int and 1<=step<=total,
         "STEP_OUTSIDE_TARGET_BUDGET")
    rows=observations_by_vector(prior_observations,total,lower,upper)
    need(len(rows)>0,"NO_PRIOR_NATIVE_ANCHOR")
    return {"schema":SCHEMA,"scenario_digest":normalized["scenario_digest"],
        "official_total":total,"step":step,
        "minima":to_target(lower),"maxima":to_target(upper),
        "scout_max":scout_max,"confirmation_runs":2,
        "prior_native_observations":len(prior_observations),
        "observations":list(prior_observations),
        "completed_new_scouts":0,
        "awaiting_confirmation":False,
        "source_original_v015_sha256":SOURCE_V015_SHA256,
        "source_original_v016_sha256":SOURCE_V016_SHA256,
        "original_v015_v016_files_modified":False,
        "original_v015_v016_native_receipt_reused":False,
        "original_v015_v016_product_code_merged":False,
        "policy_adapted_to_current_v1_2":True,
        "new_native_attempts":0}

def next_scout(state,normalized,budget,calibration,reference,binary_sha,
               output_path,iterations):
    need(state.get("schema")==SCHEMA and
         state["scenario_digest"]==normalized["scenario_digest"],
         "SCOUT_STATE_OTHER_SCENARIO")
    need(state["completed_new_scouts"]<state["scout_max"],
         "SCOUT_BUDGET_EXHAUSTED")
    total,lo,hi=bounds(normalized,budget)
    need(total==state["official_total"],"CHMV_BUDGET_CHANGED")
    rows=observations_by_vector(state["observations"],total,lo,hi)
    anchor,chosen,hint=choose_next(rows,state["step"],total,lo,hi)
    proposal=evaluator.make_request(normalized,budget,calibration,reference,
                                    binary_sha,to_target(chosen),iterations,
                                    output_path)
    return {"status":"PROPOSED_SCOUT_NOT_RUN","anchor":to_target(anchor),
       "case":proposal,"decision":hint,
       "remaining_scour_runs_after_this":state["scout_max"]-state["completed_new_scouts"]-1}

def accept_scout(state,request,observation):
    """One successful v064-validated Native result, then plan anew."""
    need(state["completed_new_scouts"]<state["scout_max"],"SCOUT_BUDGET_EXHAUSTED")
    need(observation["status"]=="PASS_NATIVE_DPS_AND_RATING" and
         request["case_key"]==observation["case_key"],
         "SCOUT_IDENTITY_OR_NATIVE_RESULT_MISMATCH")
    need(request["scenario_digest"]==state["scenario_digest"],
         "SCOUT_SCENARIO_MISMATCH")
    prior={key(x["target"]) for x in state["observations"]}
    need(key(observation["target"]) not in prior,"SCOUT_REUSES_OLD_TARGET")
    out=dict(state)
    out["observations"]=list(state["observations"])+[observation]
    out["completed_new_scouts"]=state["completed_new_scouts"]+1
    out["awaiting_confirmation"]=out["completed_new_scouts"]>=out["scout_max"]
    return out

def pair_to_confirm(state,normalized,budget,calibration,reference,
                    binary_sha,output_dir,iterations):
    need(state["completed_new_scouts"]==state["scout_max"],
         "SCOUTS_NOT_COMPLETED")
    total,lo,hi=bounds(normalized,budget)
    rows=observations_by_vector(state["observations"],total,lo,hi)
    chosen=confirmation_pair(rows,total,lo,hi)
    cases=[evaluator.make_request(normalized,budget,calibration,reference,
       binary_sha,to_target(vec),iterations,
       str(output_dir)+"/confirm_%02d/result.json"%i)
       for i,vec in enumerate(chosen)]
    need(cases[0]["case_key"]!=cases[1]["case_key"],
         "CONFIRM_PAIR_DUPLICATED")
    return {"schema":"v065_confirmation_plan_v1",
        "status":"TWO_FRESH_CONFIRMATIONS_REQUIRED_NOT_RUN",
        "cases":cases,"original_v015_pair_selection_reused":True,
        "old_native_DPS_must_not_replace_fresh_confirmations":True,
        "global_optimum_proven":False}
