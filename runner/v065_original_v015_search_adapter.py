#!/usr/bin/env python3
"""v065 — original v015 local-neighbor/choose_next policy adapted to v064.

Source provenance: CHMV_ADAPTIVE_v015.py, byte SHA256
a44f73cf232c8204dbe958e79fe50f111e68654ac583a1170a283f16035c0ec3.
Original file itself is NOT modified, executed, or falsely called a new
71/71 PASS. This module ports ONLY the proposal policy (directed stat
transfer, duplicate rejection, observed-mean anchoring, mirrored ordering,
fallback anchor, independent top-two confirmation selection).

v061/v062 own budget and floors, v063/v064 own selected input and Native
DPS/SEM. No v015 virtual 3000, hardcoded Mage, SimC version or +165 offset.
"""
from __future__ import annotations
import math
import v046_static_item_cache as cache
import v061_scenario_contract as contract
import v063_numeric_injection as injection

STATS=contract.STATS
SCHEMA="v065_v015_lineage_proposal_v1"
SOURCE_V015_SHA256="a44f73cf232c8204dbe958e79fe50f111e68654ac583a1170a283f16035c0ec3"
class SearchBlocked(ValueError):pass
def need(ok,msg):
    if not ok:raise SearchBlocked(msg)

def vector_tuple(doc):
    contract.vector(doc,"CHMV_VECTOR")
    return tuple(doc[k] for k in STATS)

def named(vec):
    return dict(zip(STATS,vec))

def feasible(target,budget,normalized):
    """Integer target feasible in official current budget, locked L, user caps."""
    try:injection.check_target(normalized,budget,named(target))
    except (ValueError,TypeError,KeyError):return False
    return True

def neighbors(anchor,step,already,budget,normalized):
    """v015 original 4x3 directed transfer ordering; one step moved each time."""
    need(step in (100,200),"V015_LINEAGE_STEPS_ONLY")
    result=[]
    for source in range(4):
        for dest in range(4):
            if source==dest:continue
            v=list(anchor);v[source]-=step;v[dest]+=step
            v=tuple(v)
            if v not in already and v not in result and feasible(v,budget,normalized):
                result.append(v)
    return result

def latest_by_rating(observations):
    records={}
    for x in observations:
        need(x.get("status")=="PASS_NATIVE_DPS_AND_RATING","NATIVE_RESULT_REQUIRED")
        rating=vector_tuple(x["target"])
        need(type(x.get("dps_mean")) in (int,float) and
             math.isfinite(x["dps_mean"]) and x["dps_mean"]>0,"DPS_INVALID")
        need(type(x.get("dps_sem")) in (int,float) and
             math.isfinite(x["dps_sem"]) and x["dps_sem"]>=0,"SEM_INVALID")
        records[rating]=x
    need(records,"NO_OBSERVATIONS_TO_EXPLORE")
    return records

def leader(observed):
    """Exact v015 raw-mean search anchor; NOT claim of statistical best."""
    return max(observed,key=lambda v:(observed[v]["dps_mean"],
                                    tuple(-x for x in v)))

def mirror_score(anchor,candidate,observed):
    opposite=tuple(2*a-b for a,b in zip(anchor,candidate))
    if opposite not in observed:return 0.0
    return max(-2500.0,min(2500.0,
         observed[anchor]["dps_mean"]-observed[opposite]["dps_mean"]))

def propose_scout(observations,normalized,budget,step=200,
                  reserved_vectors=()):
    observed=latest_by_rating(observations)
    eligible={v:x for v,x in observed.items()
              if feasible(v,budget,normalized)}
    need(bool(eligible),"NO_ELIGIBLE_SEARCH_ANCHOR")
    # Never re-evaluate an already-seen vector at same exploration stage,
    # even when its DPS was previously cached under another iteration count.
    seen=set(observed)|set(reserved_vectors)
    primary=leader(eligible)
    anchors=[primary]+[v for v in sorted(
        eligible,key=lambda vec:eligible[vec]["dps_mean"],reverse=True)
        if v!=primary]
    for anchor in anchors:
        candidates=neighbors(anchor,step,seen,budget,normalized)
        if candidates:
            candidates.sort(key=lambda v:(-mirror_score(anchor,v,observed),v))
            chosen=candidates[0]
            return {"phase":"SCOUT","target":named(chosen),
              "anchor":named(anchor),"iterations":normalized["scenario"]["runtime"]["scout_iterations"],
              "ordering":"V015_MIRRORED_NEIGHBOR_FOR_PRIORITY_ONLY",
              "mirror_order_score":mirror_score(anchor,chosen,observed),
              "lineage_source_sha256":SOURCE_V015_SHA256,
              "requested_step":step,"global_optimum_proven":False}
    raise SearchBlocked("NO_NEW_FEASIBLE_NEIGHBORS")

def confirmation_pair(observations,normalized,budget):
    """v015's top TWO distinct exploratory means, not stochastic winner proof."""
    observed=latest_by_rating(observations)
    eligible={v:x for v,x in observed.items()
              if feasible(v,budget,normalized)}
    need(len(eligible)>=2,"TWO_DISTINCT_FEASIBLE_RATINGS_REQUIRED")
    return sorted(eligible,key=lambda v:eligible[v]["dps_mean"],
                  reverse=True)[:2]

def confirmation_proposals(observations,normalized,budget):
    pair=confirmation_pair(observations,normalized,budget)
    it=normalized["scenario"]["runtime"]["confirm_iterations"]
    return [{"phase":"CONFIRM","target":named(v),"iterations":it,
         "comparison_policy":"V015_FRESH_PAIR_SAME_ITERATIONS",
         "lineage_source_sha256":SOURCE_V015_SHA256} for v in pair]

def judge_confirmed(confirmations):
    """Only new confirmed pair; independence can be claimed only with seeds."""
    need(type(confirmations) is list and len(confirmations)==2,"NEED_TWO_CONFIRM_RESULTS")
    for o in confirmations:
        need(o.get("status")=="PASS_NATIVE_DPS_AND_RATING","CONFIRM_NATIVE_INVALID")
    a,b=confirmations
    need(a["target"]!=b["target"],"CONFIRM_PAIR_NOT_DISTINCT")
    d=a["dps_mean"]-b["dps_mean"]
    half=1.9599639854*math.hypot(a["dps_sem"],b["dps_sem"])
    seeds=[x.get("native_seed") for x in confirmations]
    independent=(None not in seeds and seeds[0]!=seeds[1])
    return {"schema":"v065_pairwise_fresh_confirm_v1",
      "first_target":a["target"],"second_target":b["target"],
      "first_minus_second_dps":d,"ci95_halfwidth_approx":half,
      "distinct_native_seeds":independent,
      "pairwise_direction_supported":independent and abs(d)>half,
      "uncertainty_unresolved":not(independent and abs(d)>half),
      "global_optimum_proven":False,
      "selected_pair_only_not_all_candidates_multiple_comparison_corrected":True}

def seed_state(observations,normalized,budget,scouts_limit=3,
               confirmations_limit=2,step=200):
    need(type(observations) is list and len(observations)>=2,
         "HISTORICAL_TWO_RESULTS_REQUIRED")
    need(type(scouts_limit) is int and 0<=scouts_limit<=3,"SCOUT_LIMIT")
    need(confirmations_limit==2,"V015_CONFIRM_PAIR_LIMIT")
    need(step in (100,200),"STEP")
    need(budget.get("scenario_digest")==normalized["scenario_digest"],
         "SCENARIO_BUDGET_DRIFT")
    total=budget["budget"]["T_official"]
    need(type(total) is int and total>0,"OFFICIAL_T_UNKNOWN")
    # Historical observations MUST originate from this exact scenario.
    for o in observations:
        need(o.get("scenario_digest")==normalized["scenario_digest"],
             "HISTORICAL_NATIVE_SCENARIO_DRIFT")
        need(feasible(vector_tuple(o["target"]),budget,normalized),
             "HISTORICAL_NATIVE_BOUNDS_DRIFT")
    need(len({x["case_key"] for x in observations})==len(observations),
         "DUPLICATE_HISTORICAL_CASE")
    return {"schema":SCHEMA,"status":"SCOUT_PENDING",
        "scenario_digest":normalized["scenario_digest"],"total":total,
        "source_v015_sha256":SOURCE_V015_SHA256,
        "historical":list(observations),"scouts":[],"confirmations":[],
        "max_scouts":scouts_limit,"max_confirmations":2,
        "step":step,"pending":None,"attempted_new_native_calls":0,
        "max_native_calls":normalized["scenario"]["runtime"]["max_native_calls"],
        "global_optimum_proven":False,
        "original_source_modified":False}

def next_proposal(state,normalized,budget):
    need(state["schema"]==SCHEMA and
         state["scenario_digest"]==normalized["scenario_digest"]==
         budget["scenario_digest"],"STATE_SCENARIO_CHANGED")
    need(state["pending"] is None,"PENDING_NATIVE_EVALUATION_MUST_RESOLVE")
    need(state["attempted_new_native_calls"]<state["max_native_calls"],
         "NATIVE_CALL_LIMIT_REACHED")
    allobserved=state["historical"]+state["scouts"]
    if len(state["scouts"])<state["max_scouts"]:
        p=propose_scout(allobserved,normalized,budget,step=state["step"])
    else:
        need(len(state["confirmations"])<2,"SEARCH_FINISHED")
        p=confirmation_proposals(allobserved,normalized,budget)[len(state["confirmations"])]
    return p

def reserve(state,proposal,request):
    """Return successor checkpoint; never mutate caller's saved state."""
    need(state["pending"] is None,"ALREADY_PENDING")
    need(proposal["target"]==request["target"] and
         proposal["iterations"]==request["iterations"],"PROPOSAL_AND_PORT_DISAGREE")
    need(request["scenario_digest"]==state["scenario_digest"],"SCENARIO_DRIFT")
    updated=dict(state)
    updated["pending"]={"phase":proposal["phase"],"request_key":request["case_key"],
                        "target":proposal["target"],"iterations":proposal["iterations"]}
    updated["attempted_new_native_calls"]=state["attempted_new_native_calls"]+1
    updated["status"]="NATIVE_RESULT_PENDING"
    return updated

def complete(state,observation):
    need(state["pending"] is not None,"NO_PENDING_EVALUATION")
    p=state["pending"]
    need(observation["case_key"]==p["request_key"] and
         observation["target"]==p["target"] and
         observation["iterations"]==p["iterations"],
         "NATIVE_RECEIPT_DOES_NOT_MATCH_PENDING")
    need(observation["status"]=="PASS_NATIVE_DPS_AND_RATING",
         "ONLY_VALIDATED_NATIVE_RESULTS_ACCEPTED")
    new=dict(state);new["pending"]=None
    if p["phase"]=="SCOUT":
        new["scouts"]=state["scouts"]+[observation]
    else:
        new["confirmations"]=state["confirmations"]+[observation]
    new["status"]="FINISHED_WITH_PAIR" if len(new["confirmations"])==2 \
          else "CONFIRM_PENDING" if len(new["scouts"])==state["max_scouts"] \
          else "SCOUT_PENDING"
    return new
