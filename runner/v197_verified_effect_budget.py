#!/usr/bin/env python3
"""v197: CHMV invariant for source-verified fixed enchant rating candidates.

This is an offline, pure accounting primitive, not a proc model or a new
optimizer. Candidate stat effects become usable ONLY after exact SimC Native
stat evidence has populated the vector and its source profile identity. A
permanent enchant's static secondary contributes to already-budgeted G: it
is protected as a floor like selected special-item L, not appended to T.
All actual SimC effect mechanics and equipment compatibility stay with SimC.
"""
from __future__ import annotations
import re

STATS=("crit_rating","haste_rating","mastery_rating","versatility_rating")
SCHEMA="v197_fixed_enchant_inside_G_exact_native_only_v1"

class RatingEvidenceBlocked(ValueError):
    pass

def need(ok,code):
    if not ok:raise RatingEvidenceBlocked(code)

def vector(v,name):
    need(type(v) is dict and set(v)==set(STATS) and
         all(type(v[s]) is int and 0<=v[s]<=100000 for s in STATS),
         "INVALID_NONNEGATIVE_VECTOR:"+name)
    return dict(v)

def complete_native_evidence(record):
    """Evidence must carry exact Native provenance and observed stat delta.

    Caller, not this function, must independently verify companion JSON2
    receipt/SHA and matched base/change profile equipment identities. A row
    missing that verification cannot be handed to this function as 'verified'.
    """
    need(type(record) is dict and
         set(record)=={"enchant_id","slot","static_secondary",
                      "proof_kind","profile_before_sha256",
                      "profile_after_sha256","native_before_sha256",
                      "native_after_sha256","verified_receipt_sha256"},
         "NATIVE_ENCHANT_EVIDENCE_FIELDS")
    need(type(record["enchant_id"]) is int and record["enchant_id"]>0,
         "INVALID_ENCHANT_ID")
    need(type(record["slot"]) is str and record["slot"] in
         ("head","shoulders","chest","feet","finger1","finger2",
          "main_hand","off_hand"),"INVALID_ENCHANT_SLOT")
    need(record["proof_kind"]==
         "MATCHED_SIMC_NATIVE_JSON2_STATIC_SECONDARY_DELTA_VERIFIED",
         "ENCHANT_STATIC_NOT_NATIVE_VERIFIED")
    for k in ("profile_before_sha256","profile_after_sha256",
              "native_before_sha256","native_after_sha256",
              "verified_receipt_sha256"):
        need(type(record[k]) is str and bool(re.fullmatch(r"[a-f0-9]{64}",record[k])),
             "NATIVE_ENCHANT_PROVENANCE_SHA_MISSING:"+k)
    need(record["profile_before_sha256"]!=record["profile_after_sha256"],
         "NATIVE_ENCHANT_PROFILE_NOT_CHANGED")
    return vector(record["static_secondary"],"enchant_E")

def plan_locked_fixed_enchant_T(T,J,F,O,L,native_records):
    """Retain T=G+J+F+O, count exact enchant E once INSIDE G.

    J/F/O/L are already-existing non-free vectors. T is the sole final
    CHMV target. Reject overlapping slot and infeasible fixed components.
    This routine does not create a profile or mutate the running optimizer.
    """
    need(type(T) is int and 1<=T<=100000,"FINAL_T_INVALID")
    j,f,o,l=(vector(v,name) for v,name in
             ((J,"J"),(F,"F"),(O,"O"),(L,"L")))
    need(type(native_records) is list,"NATIVE_ENCHANT_RECORDS_MUST_BE_LIST")
    fixed_e=dict.fromkeys(STATS,0)
    slots=set();enchants=[]
    for record in native_records:
        e=complete_native_evidence(record)
        need(record["slot"] not in slots,"ENCHANT_SLOT_DUPLICATE")
        slots.add(record["slot"])
        for s in STATS:fixed_e[s]+=e[s]
        enchants.append({"slot":record["slot"],"enchant_id":record["enchant_id"],
                         "verified_receipt_sha256":record["verified_receipt_sha256"]})
    G=T-sum(sum(v.values()) for v in (j,f,o))
    need(G>=0,"FIXED_J_F_O_EXCEED_FINAL_T")
    Ltotal=sum(l.values());Etotal=sum(fixed_e.values())
    need(Ltotal+Etotal<=G,
         "NATIVE_FIXED_L_AND_ENCHANT_E_EXCEED_FREE_G")
    floors={s:j[s]+f[s]+o[s]+l[s]+fixed_e[s] for s in STATS}
    need(sum(floors.values())<=T,"FIXED_ENCHANT_PER_STAT_FLOORS_EXCEED_T")
    return {"schema":SCHEMA,"official_total_T":T,
            "gear_G_including_enchant_E":G,
            "fixed_enchant_E":fixed_e,
            "fixed_L_inside_G":l,
            "already_fixed_J":j,"already_fixed_F":f,
            "oil_O_counted_once":o,
            "minimum_final_per_stat":floors,
            "remaining_freely_distributable_gear_G":G-Ltotal-Etotal,
            "verified_enchant_slots":enchants,
            "new_enchant_added_to_total_T":False,
            "can_emit_native_candidate_without_profile_receipt":False}

def check_candidate(result,final):
    need(type(result) is dict and result.get("schema")==SCHEMA,
         "FIXED_ENCHANT_PLAN_NOT_APPROVED")
    actual=vector(final,"candidate_final_CHMV")
    need(sum(actual.values())==result["official_total_T"],
         "CANDIDATE_TOTAL_T_CHANGED")
    need(all(actual[s]>=result["minimum_final_per_stat"][s] for s in STATS),
         "CANDIDATE_UNDER_NATIVELY_VERIFIED_FIXED_ENCHANT_FLOOR")
    return True
