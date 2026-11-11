#!/usr/bin/env python3
"""IDEA-001 v320: offline SEM-aware iteration tier ADVISORY, never SimC execution.

A 120-iteration intermediate is a *hypothesis*, not a newly supported v291
phase.  v291 retains exact 35/320 identities and the v290 default.  Consumes
only actually measured JSON2 DPS mean, SEM and sample count; does not invent
new Native observations or make a selected-family 95% claim.
"""
from __future__ import annotations

import math

SCHEMA="v320_idea001_35_120_320_sem_tier_advisory_v1"
Z95=1.959963984540054
TIERS=(35,120,320)
STATS=("crit_rating","haste_rating","mastery_rating","versatility_rating")

class TierAdvisoryBlocked(ValueError):
    pass

def need(ok,reason):
    if not ok:
        raise TierAdvisoryBlocked(reason)

def _validate(row, name, minimum_iterations):
    need(type(row) is dict and set(row)>={
        "target","iterations","samples","dps_mean","dps_sem"},
        "V320_"+name+"_REAL_NATIVE_ROW_REQUIRED")
    target=row["target"]
    need(type(target) is dict and set(target)==set(STATS)
         and all(type(target[x]) is int and target[x]>=0 for x in STATS),
         "V320_"+name+"_CHMV_REQUIRED")
    need(type(row["iterations"]) is int
         and row["iterations"]>=minimum_iterations
         and type(row["samples"]) is int
         and 2<=row["samples"]<=row["iterations"],
         "V320_"+name+"_NATIVE_SAMPLE_COUNT_REQUIRED")
    need(all(type(row[x]) in (int,float)
                 and math.isfinite(row[x]) and row[x]>=0
                 for x in ("dps_mean","dps_sem")),
         "V320_"+name+"_FINITE_NATIVE_DPS_SEM_REQUIRED")

def _sem_at(row, n):
    """Fixed population-variance approximation; verified n-1 sample counts
    in v319 are used as a *projection*, not manufactured Native results.
    """
    need(type(n) is int and n>=row["iterations"],
         "V320_REQUESTED_N_AT_LEAST_CURRENT")
    return row["dps_sem"]*math.sqrt(row["samples"]/(n-1))

def recommend(candidate, confirmed_reference, *, tier_middle=120,
              tier_final=320):
    """Suggest a research tier for one UNCONFIRMED 35-iteration candidate.

    A 95%-style z=1.96 test is a ranking/triage heuristic only:
    no independent post-selection holdout, multiplicity correction, or
    global-optimum proof.  Reference is already confirmed at 320.
    """
    _validate(candidate,"CANDIDATE",35)
    _validate(confirmed_reference,"REFERENCE",320)
    need(candidate["iterations"]==35 and
         confirmed_reference["iterations"]>=tier_final and
         type(tier_middle) is int and type(tier_final) is int
         and 35<tier_middle<tier_final<=1000000,
         "V320_EXACT_35_TO_320_RESEARCH_TIERS")
    same_target=all(candidate["target"][k]==
                    confirmed_reference["target"][k] for k in STATS)
    delta=candidate["dps_mean"]-confirmed_reference["dps_mean"]
    variance=candidate["dps_sem"]**2+confirmed_reference["dps_sem"]**2
    half=Z95*math.sqrt(variance)
    # To make a fixed observed |delta| cross z=1.96, solve for candidate
    # samples at *unchanged* reference SEM.  This may be impossible even
    # with infinite candidate iterations if reference uncertainty dominates.
    denominator=(abs(delta)/Z95)**2-confirmed_reference["dps_sem"]**2
    needed=None
    if denominator>0 and candidate["dps_sem"]>0:
        needed=max(35, 1+math.ceil(
            candidate["samples"]*candidate["dps_sem"]**2/denominator))
    if same_target:
        action="SAME_TARGET_SEM_CALIBRATION_ONLY"
        tier=None
    elif delta < -half:
        action="SCREEN_LOWER_PRIORITY_NOT_95_EXCLUSION"
        tier=35
    elif delta > half:
        action="CONFIRM_APPARENT_NEW_LEADER_320"
        tier=tier_final
    elif needed is not None and 35<needed<=tier_middle:
        # This is only a *potentially* economic intermediate: a candidate
        # surviving the mid test would require an additional full 320 call.
        action="RESEARCH_120_POTENTIALLY_USEFUL"
        tier=tier_middle
    elif needed is not None and needed<=tier_final:
        action="DIRECT_CONFIRM_320_MORE_EFFICIENT_THAN_120"
        tier=tier_final
    else:
        action="CLOSE_PAIR_320_MAY_NOT_RESOLVE_RANKING"
        tier=tier_final
    return {
        "schema":SCHEMA,"decision":action,"suggested_iterations":tier,
        "requested_tier_is_executable_in_v291":tier in (35,320),
        "reference_target":dict(confirmed_reference["target"]),
        "candidate_target":dict(candidate["target"]),
        "candidate_requested_iterations":candidate["iterations"],
        "candidate_actual_samples":candidate["samples"],
        "reference_actual_samples":confirmed_reference["samples"],
        "observed_signed_dps_gap":delta,
        "nominal_95_difference_halfwidth":half,
        "estimated_required_candidate_iterations":needed,
        "projected_sem_120_not_native":_sem_at(candidate,tier_middle),
        "projected_sem_320_not_native":_sem_at(candidate,tier_final),
        "projected_mid_does_not_reduce_320_cost_if_promoted":True,
        "selection_multiplicity_95_proven":False,
        "global_optimum_proven":False,
        "interpretation":"PRIORITIZATION_ONLY_NATIVE_MECHANICS_STAY_IN_SIMC",
    }
