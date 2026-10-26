#!/usr/bin/env python3
"""v092 official user-approved CHMV formula B=G+J+F; T=B+O.

The existing v061-v090 runtime still has legacy field names T/T_official for B.
This module is the authoritative final-total bridge and does NOT change the
unchanged v087 base reference table or treat oil as fungible stat budget.
No separate SimC effect or proc verification is implemented.
"""
from __future__ import annotations
import hashlib,copy
import v061_scenario_contract as scenario
import v046_static_item_cache as itemcache
import v063_numeric_injection as numerical

SCHEMA="v092_approved_oil_inclusive_total_v1"
FORMULA="T=G+J+F+O"
BASE_FORMULA="B=G+J+F"
MANUAL_SCOPE="INCLUDES_G_J_F_O"
class TotalPolicyBlocked(ValueError):pass
def need(ok,reason):
    if not ok:raise TotalPolicyBlocked(reason)

def calculate(B,oil):
    need(type(B) is int and B>0,"BASE_B_POSITIVE_INT_REQUIRED")
    vector=scenario.vector(oil,"APPROVED_FIXED_O_VECTOR")
    O=sum(vector.values())
    T=B+O
    need(T>0 and T<=100000,"FINAL_TOTAL_OUT_OF_BOUNDS")
    return {"schema":SCHEMA,"approved":True,"base_B":B,
            "fixed_O":dict(vector),"oil_sum_O":O,"final_T":T,
            "base_formula":BASE_FORMULA,"total_formula":FORMULA,
            "oil_fungible":False,"final_goal_includes_oil_once":True}

def effective_candidate(base,accounting):
    scenario.vector(base,"BASE_OPTIMIZED_C")
    need(type(accounting) is dict and accounting.get("schema")==SCHEMA,
         "APPROVED_OIL_INCLUSIVE_ACCOUNTING_REQUIRED")
    need(sum(base.values())==accounting["base_B"],
         "BASE_CHMV_SUM_MISMATCH")
    o=accounting["fixed_O"]
    out={s:base[s]+o[s] for s in scenario.STATS}
    need(sum(out.values())==accounting["final_T"],
         "FINAL_CHMV_SUM_MISMATCH")
    return out

def adjust_native_request(request,accounting,base):
    """Rebuild a v090 static-c Native proposal with exact oil-inclusive gear_*.

    v090 first enforces locked special L / max fractions on B and creates the
    fully SHA-bound SimC candidate.  Since SimC gear_* replaces the numeric
    gear/gem/oil aggregate, add o ONLY to the four gear_* override values.
    Oil remains an exact fixed per-stat component and MUST NOT become another
    scheduler/free-distribution dimension.
    """
    need(type(request) is dict and
         request.get("status")=="PROPOSED_STATIC_C_NO_NATIVE"
         and request.get("rating_semantics")=="STATIC_CHMV_C_V1",
         "V090_STATIC_C_REQUEST_REQUIRED")
    need(type(accounting) is dict and accounting.get("schema")==SCHEMA,
         "APPROVED_TOTAL_POLICY_REQUIRED")
    need(request.get("official_total")==accounting["base_B"]
         and request.get("target")==base,
         "BASE_STATIC_INPUT_IDENTITY_DRIFT")
    final=effective_candidate(base,accounting)
    declared_F=request["static_flask_F_vector"]
    scenario.vector(declared_F,"DECLARED_STATIC_FLASK_F")
    prior=request["raw_gear_override"]
    need(all(prior[s]+declared_F[s]==base[s] for s in scenario.STATS),
         "BASE_GEARRATING_AND_F_MISMATCH")
    raw={s:prior[s]+accounting["fixed_O"][s] for s in scenario.STATS}
    need(all(raw[s]+declared_F[s]==final[s] for s in scenario.STATS),
         "OIL_INCLUSION_NUMERIC_DUPLICATION_OR_MISSING")
    lines=request["input"].splitlines()
    seen={s:0 for s in scenario.STATS}
    updated=[]
    for line in lines:
        key,sep,_=line.partition("=")
        if sep and key.startswith("gear_") and key[5:] in seen:
            st=key[5:]
            seen[st]+=1
            updated.append(key+"="+str(raw[st]))
        else:updated.append(line)
    need(all(count==1 for count in seen.values()),
         "REQUIRES_EXACTLY_ONE_OF_EACH_GEAR_OVERRIDE")
    full="\n".join(updated).rstrip()+"\n"
    parts=numerical.input_parts(full)
    need(parts["gear_override"]==raw
         and parts["stable_sha256"]==request["profile_stable_sha256"],
         "SIMC_PROFILE_CHANGED_BEYOND_OIL_STATIC_INPUT")
    new=copy.deepcopy(request)
    old_case=request["case_key"]
    new.update({"input":full,
        "input_sha256":hashlib.sha256(full.encode("utf8")).hexdigest(),
        "case_key":itemcache.digest({"schema":SCHEMA,
            "unmodified_v090_case_key":old_case,
            "static_base_B":accounting["base_B"],
            "fixed_O":accounting["fixed_O"],"final_T":accounting["final_T"],
            "final_target":final,
            "full_stable_profile_sha256":parts["stable_sha256"],
            "native_binary_sha256":request["simc_binary_sha256"],
            "native_revision":request["native_revision"],
            "iterations":request["iterations"]}),
        "target":final,"official_total":accounting["final_T"],
        "raw_gear_override":raw,
        "v092_formula":FORMULA,"v092_base_B":accounting["base_B"],
        "v092_fixed_O":dict(accounting["fixed_O"]),
        "v092_final_T":accounting["final_T"],
        "v092_base_target":dict(base),
        "v092_budget_policy":"USER_APPROVED_INCLUDING_OIL",
        "oil_fungible":False,
        "bufstats_equals_static_rating_not_universally_required":True})
    return new

def approved_manual_total_to_legacy_B(doc,manual_final_T,oil):
    """Explicit user final-inclusive manual target -> old typed B.

    Avoid silently reinterpreting older v061 manual_total (its documented
    meaning excluded oil).  New user-interface callers must explicitly opt
    into this conversion and show both B and T.
    """
    need(type(manual_final_T) is int and 1<=manual_final_T<=100000,
         "USER_INCLUSIVE_TOTAL_REQUIRED")
    o=scenario.vector(oil,"APPROVED_MANUAL_O")
    B=manual_final_T-sum(o.values())
    need(B>0,"USER_TOTAL_LESS_THAN_FIXED_O")
    copied=copy.deepcopy(doc)
    copied["target"]={"mode":"manual_total",
        "ilevel":doc["target"]["ilevel"],
        "manual_total":B,
        "manual_total_scope":scenario.MANUAL_TOTAL_SCOPE}
    plan=scenario.normalize(copied)
    accounting=calculate(B,o)
    need(accounting["final_T"]==manual_final_T,
         "USER_INCLUSIVE_TOTAL_CONVERSION_DRIFT")
    return {"schema":SCHEMA,"manual_total_scope":MANUAL_SCOPE,
        "user_entered_total_T":manual_final_T,
        "legacy_v061_base_B":B,
        "normalized_legacy_B":plan,"scenario":copied,
        "approved_accounting":accounting}
