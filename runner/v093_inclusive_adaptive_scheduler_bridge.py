#!/usr/bin/env python3
"""v093: bounded original-v015-derived search decisions with v092 inclusive oil.

No second optimizer. v065 owns scout selection, material neighbors, pair and
statistics. v091/v092 own the exact Native rating target T=B+O. An observation
from Native T is projected to the v065 legacy B coordinate system only AFTER
exact v064/v091 acceptance. Full native T evidence is retained unchanged.
"""
from __future__ import annotations
import copy,hashlib,json,pathlib
import v046_static_item_cache as itemcache
import v061_scenario_contract as scenario
import v063_numeric_injection as numerical
import v065_v015_scheduler_adapter as policy
import v091_weapon_oil_external_adapter as oilpath
import v092_approved_inclusive_CHMV_policy as totals

SCHEMA="v093_inclusive_oil_v015_policy_bridge_v1"
class AdaptiveBridgeBlocked(ValueError):pass
def need(ok,reason):
    if not ok:raise AdaptiveBridgeBlocked(reason)

def identity(bundle,binary_sha,revision,scout_iterations,confirm_iterations):
    need(type(bundle) is dict and bundle.get("schema")==oilpath.SCHEMA
         and bundle.get("status")=="READY_V091_STATIC_C_CANDIDATE",
         "OIL_INCLUSIVE_PREPARED_BUNDLE_REQUIRED")
    approved=bundle["approved_total"]
    prepared=bundle["prepared"]; o=bundle["oil"]
    need(approved["schema"]==totals.SCHEMA
         and approved["base_B"]==prepared["T"]
         and approved["final_T"]==prepared["T"]+sum(o["declared_O"].values())
         and approved["fixed_O"]==o["declared_O"],
         "B_O_T_CONTRACT_MISMATCH")
    normalized=prepared["scenario"]
    runtime=normalized["scenario"]["runtime"]
    need(type(scout_iterations) is int and
         runtime["scout_iterations"]<=scout_iterations<=runtime["confirm_iterations"]
         and type(confirm_iterations) is int and
         scout_iterations<=confirm_iterations<=runtime["confirm_iterations"],
         "ADAPTIVE_ITERATION_POLICY")
    need(type(binary_sha) is str and
         scenario.HASH_RE.fullmatch(binary_sha) is not None
         and type(revision) is str and len(revision)>=7,
         "NATIVE_BINARY_VERSION_IDENTITY")
    return {"schema":SCHEMA,"scenario_digest":normalized["scenario_digest"],
        "source_profile_sha256":o["profile_sha256"],
        "reference_source_sha256":prepared["reference_sha256"],
        "exact_slots_digest":itemcache.digest(prepared["static_budget"]["reference_exact_slot_identity"]),
        "base_B":approved["base_B"],"oil_vector":dict(approved["fixed_O"]),
        "approved_final_T":approved["final_T"],
        "oil_hands":list(o["applied_hands"]),
        "oil_temporary_enchant":o["expected_simc_temporary_enchant"],
        "binary_sha256":binary_sha,"revision":revision,
        "scout_iterations":scout_iterations,
        "confirm_iterations":confirm_iterations,
        "threads":runtime["threads"],
        "simc_mechanics_owner":"SimC",
        "policy_v065_original_v015_source_sha":policy.SOURCE_V015_SHA256}

def prepare(bundle,binary_sha,revision,scout_iterations=None,confirm_iterations=None):
    runtime=bundle["prepared"]["scenario"]["scenario"]["runtime"]
    scout=scout_iterations or runtime["scout_iterations"]
    confirm=confirm_iterations or runtime["confirm_iterations"]
    bound=identity(bundle,binary_sha,revision,scout,confirm)
    return {"schema":SCHEMA,"status":"READY_TO_SELECT_B_SCOUT_WITH_FINAL_T_NATIVE",
        "identity":bound,"bundle":bundle,"native_calls":0,
        "original_product_v015_v016_fully_integrated":False}

def feasible_budget(context,flask_vector):
    """Only search constraints change: B+O must cover F on every stat."""
    prepared=context["bundle"]["prepared"]
    return policy.budget_with_fixed_components(
        prepared["scenario"],prepared["static_budget"],
        flask_vector,context["identity"]["oil_vector"])

def request(context,base_target,flask_vector,json2_path,phase="scout"):
    """v091 owns request, including oil selection and final static T."""
    need(context.get("schema")==SCHEMA and
         context.get("status")=="READY_TO_SELECT_B_SCOUT_WITH_FINAL_T_NATIVE",
         "V093_CONTEXT_REQUIRED")
    bound=context["identity"]
    need(phase in ("seed","scout","confirm"),"PHASE_IDENTITY_INVALID")
    iterations=bound["confirm_iterations"] if phase=="confirm" else bound["scout_iterations"]
    normalized=context["bundle"]["prepared"]["scenario"]
    feasible=feasible_budget(context,flask_vector)
    B,lo,hi=policy.bounds(normalized,feasible)
    need(policy.eligible(policy.key(base_target),B,lo,hi),
         "BASE_TARGET_BELOW_FIXED_COMPONENT_FLOOR")
    req=oilpath.propose(context["bundle"],base_target,flask_vector,
         bound["binary_sha256"],bound["revision"],iterations,json2_path)
    need(req["v092_base_B"]==bound["base_B"]
         and req["v092_final_T"]==bound["approved_final_T"]
         and req["v092_fixed_O"]==bound["oil_vector"]
         and req["v091_expected_temporary_enchant"]==bound["oil_temporary_enchant"],
         "ADAPTIVE_FINAL_T_O_PROFILE_IDENTITY")
    need(req["scenario_digest"]==bound["scenario_digest"] and
         req["profile_stable_sha256"]==numerical.input_parts(
             context["bundle"]["oil"]["profile"],
             allow_missing_json2_template=True)["stable_sha256"],
         "ADAPTIVE_SOURCE_PROFILE_IDENTITY")
    req["v093_phase"]=phase
    req["v093_session_digest"]=itemcache.digest(bound)
    return req

def project_native_for_v065(req,native_observation):
    """Only a fully Native-validated final-T result enters legacy B policy.

    The scheduler's observation target is B; the Native observation returned
    by v064 remains final T with immutable native JSON SHA and version.
    """
    need(req.get("v092_formula")=="T=G+J+F+O"
         and req.get("v093_session_digest"),
         "APPROVED_FINAL_REQUEST_REQUIRED")
    obs=native_observation
    need(type(obs) is dict and
         obs.get("status")=="PASS_NATIVE_DPS_AND_STATIC_CHMV_INPUT" and
         obs.get("rating_semantics")=="STATIC_CHMV_C_V1" and
         obs.get("case_key")==req["case_key"]
         and obs.get("input_sha256")==req["input_sha256"]
         and obs.get("target")==req["target"]
         and obs.get("static_rating_verified")==req["target"]
         and obs.get("simc_binary_sha256")==req["simc_binary_sha256"]
         and obs.get("native_revision")==req["native_revision"]
         and obs.get("iterations")==req["iterations"]
         and obs.get("scenario_digest")==req["scenario_digest"],
         "NATIVE_T_NOT_VERIFIED_FOR_REQUEST")
    need(obs.get("oil_reported_by_native")==
         req["v091_expected_temporary_enchant"],
         "NATIVE_OIL_INPUT_NOT_VERIFIED")
    base=req["v092_base_target"]
    need(sum(base.values())==req["v092_base_B"] and
         all(obs["target"][s]==base[s]+req["v092_fixed_O"][s]
             for s in scenario.STATS),
         "NATIVE_FINAL_T_TO_BASE_B_PROJECTION_FAILED")
    projected=copy.deepcopy(obs)
    projected["target"]=dict(base)
    projected["static_rating_verified"]=dict(base)
    projected["v093_projection"]="POLICY_ONLY_B_FROM_NATIVE_VALIDATED_FINAL_T"
    projected["v093_native_final_T_target"]=dict(obs["target"])
    projected["v093_fixed_O"]=dict(req["v092_fixed_O"])
    projected["v093_user_final_total_T"]=req["v092_final_T"]
    projected["v093_base_B"]=req["v092_base_B"]
    projected["v093_full_native_json_sha256"]=obs["native_json_sha256"]
    return projected

def start_scout(context,anchors,step=100,scout_max=1,flask_vector=None):
    need(type(anchors) is list and len(anchors)>=1,
         "NATIVE_ANCHORS_REQUIRED")
    bound=context["identity"]
    feasible=(feasible_budget(context,flask_vector) if flask_vector is not None
              else context["bundle"]["prepared"]["static_budget"])
    state=policy.initial_state(context["bundle"]["prepared"]["scenario"],
         feasible,anchors,
         step=step,scout_max=scout_max,confirmation_runs=2)
    need(state["official_total"]==bound["base_B"],
         "SCHEDULER_MUST_USE_BASE_B")
    return state

def next_scout(context,state,flask_vector,json2_path):
    bound=context["identity"]
    need(state.get("scenario_digest")==bound["scenario_digest"]
         and state["completed_new_scouts"]<state["scout_max"],
         "SCOUT_STATE_IDENTITY_OR_CAP")
    B,lower,upper=policy.bounds(
         context["bundle"]["prepared"]["scenario"],
         feasible_budget(context,flask_vector))
    rows=policy.observations_by_vector(state["observations"],B,lower,upper)
    anchor,candidate,hint=policy.choose_next(rows,state["step"],B,lower,upper)
    chosen=policy.to_target(candidate)
    req=request(context,chosen,flask_vector,json2_path,phase="scout")
    return {"schema":SCHEMA,"status":"SCOUT_PROPOSED_NOT_RUN",
        "policy":"v065_original_v015_choose_next",
        "anchor_B":policy.to_target(anchor),"candidate_B":chosen,
        "candidate_final_T":req["target"],
        "request":req,"decision":hint,
        "remaining_scouts":state["scout_max"]-state["completed_new_scouts"]-1}

def accept_scout(context,state,req,native_observation):
    bound=context["identity"]
    need(req.get("v093_session_digest")==itemcache.digest(bound),
         "SCOUT_ANOTHER_SESSION")
    obs=project_native_for_v065(req,native_observation)
    return policy.accept_scout(state,req,obs)

def confirmation_plan(context,state,flask_vector,outdir):
    need(state["completed_new_scouts"]==state["scout_max"],
         "SCOUTS_NOT_COMPLETE")
    prepared=context["bundle"]["prepared"]
    total,low,high=policy.bounds(
        prepared["scenario"],feasible_budget(context,flask_vector))
    rows=policy.observations_by_vector(state["observations"],total,low,high)
    pair=policy.confirmation_pair(rows,total,low,high)
    requests=[request(context,policy.to_target(candidate),flask_vector,
             pathlib.Path(outdir)/("confirm_%02d"%i)/"result.json",
             phase="confirm") for i,candidate in enumerate(pair)]
    need(requests[0]["case_key"]!=requests[1]["case_key"],
         "CONFIRM_CASE_KEYS_IDENTICAL")
    return {"schema":SCHEMA,
        "status":"TWO_INDEPENDENT_FRESH_NATIVE_CONFIRMATIONS_REQUIRED",
        "policy":"v065_original_v015_confirmation_pair",
        "base_pair":[policy.to_target(x) for x in pair],
        "final_pair":[r["target"] for r in requests],
        "cases":requests,
        "global_optimum_proven":False}

def fresh_judgment(confirmed_requests,confirmed_native):
    """Existing v065 statistical policy, only after independent Native receipt."""
    need(len(confirmed_requests)==2 and len(confirmed_native)==2,
         "TWO_CONFIRMATIONS_REQUIRED")
    paired={}
    names=[]
    for req,obs in zip(confirmed_requests,confirmed_native):
        projected=project_native_for_v065(req,obs)
        b=policy.key(projected["target"])
        need(b not in paired,"FRESH_PAIR_DUPLICATE_BASE_B")
        paired[b]=projected;names.append(b)
    out=policy.fresh_confirmation_judgment(names,paired)
    out["official_final_T"]=confirmed_requests[0]["v092_final_T"]
    out["fixed_O"]=confirmed_requests[0]["v092_fixed_O"]
    out["underlying_free_allocation_B"]=confirmed_requests[0]["v092_base_B"]
    out["global_optimum_proven"]=False
    return out
