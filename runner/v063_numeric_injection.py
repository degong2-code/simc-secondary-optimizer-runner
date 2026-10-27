#!/usr/bin/env python3
"""v063 P3: measured numeric gear_* -> JSON2 rating reconciliation.

No SimC proc/effect/APL logic is reproduced or gated here. A calibration
is valid ONLY for the exact full profile (except gear_* ratings, iterations,
and JSON2 location) and one pinned SimC binary revision. Other profiles
require their own observed numeric offset, not the Mage's +165 assumption.
"""
from __future__ import annotations
import hashlib,json,math,pathlib,re
from fractions import Fraction

import v046_static_item_cache as cache
import v061_scenario_contract as scenario

STATS=scenario.STATS
GEAR_PREFIX="gear_"
EXCLUDE_PREFIXES=("json2=","iterations=")
SCHEMA="v063_numeric_json2_offset_v1"

class InjectionError(ValueError):pass

def need(x,reason):
    if not x:raise InjectionError(reason)

def sha(data):
    return hashlib.sha256(data.encode("utf8") if isinstance(data,str) else data).hexdigest()

def read_rating(player):
    s=(player.get("collected_data") or {}).get("buffed_stats",{}).get("stats",{})
    need(all(type(s.get(k)) in (int,float) and math.isfinite(s[k])
             and abs(s[k]-round(s[k]))<0.0001 for k in STATS),
         "NATIVE_RATING_UNOBSERVED")
    return {k:int(round(s[k])) for k in STATS}

def input_parts(source,*,allow_missing_json2_template=False):
    """Allow missing json2= only for stored templates, never Native inputs.

    This explicit mode leaves duplicate rejection and 1-output Native
    candidate enforcement intact, even for legacy v104 source profiles.
    """
    need(type(source) is str,"INPUT_SOURCE_NOT_TEXT")
    lines=source.splitlines()
    collected={}; locations={}
    for i,s in enumerate(lines):
        for stat in STATS:
            if s.startswith(GEAR_PREFIX+stat+"="):
                need(stat not in locations,"DUPLICATE_GEAR_STAT_OVERRIDE:"+stat)
                part=s.partition("=")[2]
                need(re.fullmatch(r"[0-9]{1,6}",part)!=None,
                     "GEAR_OVERRIDE_NOT_NONNEGATIVE:"+stat)
                locations[stat]=i
                collected[stat]=int(part)
    need(set(locations)==set(STATS),"FOUR_GEAR_RATINGS_REQUIRED")
    for prefix in EXCLUDE_PREFIXES:
        found=sum(s.startswith(prefix) for s in lines)
        need(found in ((0,1) if allow_missing_json2_template and
                       prefix=="json2=" else (1,)),
             "MISSING_OR_DUPLICATE_INPUT:"+prefix)
    # The only mutable bytes are gear_* numeric targets, iterations and
    # JSON2 destination. In particular ALL selected IDs/options, gems,
    # consumables, tiers, talents, combat and APL stay bit-for-bit intact.
    stable="\n".join(s for s in lines if not (
       any(s.startswith(GEAR_PREFIX+k+"=") for k in STATS)
       or any(s.startswith(prefix) for prefix in EXCLUDE_PREFIXES)))+"\n"
    return {"gear_override":collected,"stable_sha256":sha(stable),
            "stable_lines":stable}

def from_native(source,native):
    need(type(native) is dict and native.get("report_version")=="2.0.0",
         "NATIVE_REPORT_INVALID")
    players=(native.get("sim") or {}).get("players",[])
    need(type(players) is list and len(players)==1,"PLAYER_COUNT_INVALID")
    part=input_parts(source)
    rating=read_rating(players[0])
    return {"source":part,"final_native":rating,
            "offset":{k:rating[k]-part["gear_override"][k] for k in STATS},
            "native_revision":native.get("git_revision"),
            "static_gear_slots_reported":sorted(players[0].get("gear",{})),
            "native_report_sha256":sha(cache.canonical(native))}

def calibrate(two_evidence):
    """Two existing real Native inputs/JSON2, no new calls."""
    need(type(two_evidence) is list and len(two_evidence)==2,
         "TWO_NUMERIC_WITNESSES_REQUIRED")
    out=[from_native(x["input"],x["native"]) for x in two_evidence]
    need(out[0]["source"]["stable_sha256"]==
         out[1]["source"]["stable_sha256"],"NOT_SAME_SCENARIO")
    need(out[0]["native_revision"]==out[1]["native_revision"]
         and isinstance(out[0]["native_revision"],str)
         and len(out[0]["native_revision"])>=7,
         "NATIVE_REVISION_DRIFT")
    need(out[0]["offset"]==out[1]["offset"],
         "NONCONSTANT_NUMERIC_INJECTION_OFFSET")
    need(out[0]["source"]["gear_override"]!=out[1]["source"]["gear_override"],
         "NO_DISTINCT_NUMERIC_WITNESS")
    return {"schema":SCHEMA,"status":"TWO_NATIVE_NUMERIC_OFFSET_WITNESSES_AGREE",
       "stable_profile_sha256":out[0]["source"]["stable_sha256"],
       "net_input_to_json2_rating_offset":out[0]["offset"],
       "native_revision":out[0]["native_revision"],
       "baseline_native_sha256s":[r["native_report_sha256"] for r in out],
       "witnesses":2,"no_item_effect_inspection":True,
       "offset_transfer_to_other_profiles":False}

def calibrate_affine(observed):
    """Empirical INPUT→JSON2 per-stat affine reconciliation, not an item/effect model.

    All four rating dimensions must have at least two DISTINCT native input
    values. A third (or more) real measured witness can cover previously
    unvaried dimensions. Actual candidate JSON2 must STILL match exactly;
    extrapolation never constitutes a Native PASS.
    """
    need(type(observed) is list and 3<=len(observed)<=12,
         "AFFINE_THREE_OR_MORE_REAL_WITNESSES_REQUIRED")
    evidence=[from_native(z["input"],z["native"]) for z in observed]
    stable=evidence[0]["source"]["stable_sha256"]
    revision=evidence[0]["native_revision"]
    need(type(revision) is str and len(revision)>=7,
         "NATIVE_REVISION_REQUIRED")
    need(all(e["source"]["stable_sha256"]==stable for e in evidence),
         "AFFINE_NOT_SAME_PROFILE")
    need(all(e["native_revision"]==revision for e in evidence),
         "AFFINE_NATIVE_REVISION_DRIFT")
    coefficients={}
    for stat in STATS:
        pairs=sorted({(e["source"]["gear_override"][stat],
                       e["final_native"][stat]) for e in evidence})
        unique_x=sorted({p[0] for p in pairs})
        need(len(unique_x)>=2,
             "AFFINE_UNOBSERVED_STAT_VARIATION:"+stat)
        lo=min(pairs,key=lambda z:z[0]);hi=max(pairs,key=lambda z:z[0])
        slope=Fraction(hi[1]-lo[1],hi[0]-lo[0])
        need(slope>0 and slope<Fraction(5),
             "AFFINE_NONPOSITIVE_OR_UNREASONABLE_SCALE:"+stat)
        intercept=Fraction(lo[1])-slope*lo[0]
        need(all(abs(float(slope*x+intercept-y))<=1.0 for x,y in pairs),
             "AFFINE_MEASURED_POINTS_NOT_AFFINE:"+stat)
        coefficients[stat]={"slope_numerator":slope.numerator,
                 "slope_denominator":slope.denominator,
                 "intercept_numerator":intercept.numerator,
                 "intercept_denominator":intercept.denominator,
                 "measured_input_min":unique_x[0],
                 "measured_input_max":unique_x[-1]}
    baseline=evidence[0]
    return {"schema":SCHEMA,
        "status":"EMPIRICAL_PER_PROFILE_NUMERIC_AFFINE_WITNESSES",
        "stable_profile_sha256":stable,"native_revision":revision,
        "net_input_to_json2_rating_offset":baseline["offset"],
        "empirical_affine_transfer":coefficients,
        "baseline_native_sha256s":[e["native_report_sha256"] for e in evidence],
        "witnesses":len(evidence),
        "no_item_effect_inspection":True,
        "offset_transfer_to_other_profiles":False,
        "affine_extrapolation_is_not_native_proof":True}

def affine_gear_for_target(calibration,target):
    coefficients=calibration["empirical_affine_transfer"]
    need(set(coefficients)==set(STATS),"AFFINE_FOUR_DIMENSIONS_REQUIRED")
    raw={}
    for stat in STATS:
        c=coefficients[stat]
        scale=Fraction(c["slope_numerator"],c["slope_denominator"])
        intercept=Fraction(c["intercept_numerator"],c["intercept_denominator"])
        best_center=round((Fraction(target[stat])-intercept)/scale)
        alternatives=[x for x in range(max(0,best_center-4),best_center+5)]
        feasible=[x for x in alternatives
                  if round(scale*x+intercept)==target[stat]]
        need(bool(feasible),
             "AFFINE_TARGET_RATING_NOT_REPRESENTABLE:"+stat)
        raw[stat]=min(feasible,key=lambda x:(abs(x-best_center),x))
    return raw

def check_target(contract,budget,target):
    need(contract.get("schema")==scenario.SCHEMA and
         budget.get("schema")=="v062_representative_static_budget_v1",
         "P1_P2_CONTRACT_REQUIRED")
    need(budget["scenario_digest"]==contract["scenario_digest"],
         "P1_P2_SCENARIO_DRIFT")
    total=budget["budget"]["T_official"]
    need(type(total) is int and total>0,"OFFICIAL_BUDGET_UNKNOWN")
    need(budget["G_if_complete"] is not None,
         "NATIVE_G_REQUIRED_FOR_THIS_P3_REFERENCE")
    need(not budget["missing_nontrinket_static"],
         "EXACT_VARIANTS_MISSING")
    need(budget["effective_floor_if_possible"] is not None,
         "STATIC_FLOOR_UNKNOWN")
    scenario.vector(target,"TARGET_CHMV")
    need(sum(target.values())==total,"OFFICIAL_T_TARGET_MISMATCH")
    lows=budget["effective_floor_if_possible"]
    caps=contract["scenario"]["constraints"]["max_fraction"]
    need(all(lows[k]<=target[k]<=int(math.floor(total*caps[k]+1e-9))
             for k in STATS),"TARGET_OUTSIDE_SPECIAL_FLOOR_OR_CAP")
    return total

def render_candidate(reference,calibration,target,path,iterations):
    need(calibration.get("schema")==SCHEMA and
         calibration.get("status") in (
           "TWO_NATIVE_NUMERIC_OFFSET_WITNESSES_AGREE",
           "EMPIRICAL_PER_PROFILE_NUMERIC_AFFINE_WITNESSES"),
         "NUMERIC_CALIBRATION_NOT_VALIDATED")
    part=input_parts(reference,allow_missing_json2_template=True)
    need(part["stable_sha256"]==calibration["stable_profile_sha256"],
         "CANDIDATE_PROFILE_DIFFERS_FROM_CALIBRATION")
    scenario.vector(target,"CHMV_TARGET")
    need(type(iterations) is int and 30<=iterations<=100000,
         "ITERATIONS_OUT_OF_RANGE")
    if calibration.get("status")=="EMPIRICAL_PER_PROFILE_NUMERIC_AFFINE_WITNESSES":
        raw=affine_gear_for_target(calibration,target)
    else:
        additive=calibration["net_input_to_json2_rating_offset"]
        raw={k:target[k]-additive[k] for k in STATS}
    need(all(type(raw[k]) is int and raw[k]>=0 for k in STATS),
         "NEGATIVE_GEAR_RATING_AFTER_RECONCILIATION")
    lines=reference.splitlines()
    output=pathlib.Path(path).resolve()
    for i,s in enumerate(lines):
        for k in STATS:
            if s.startswith("gear_"+k+"="):
                lines[i]="gear_"+k+"="+str(raw[k])
        if s.startswith("iterations="):
            lines[i]="iterations="+str(iterations)
        if s.startswith("json2="):
            lines[i]="json2="+str(output)
    if not any(line.startswith("json2=") for line in lines):
        lines.append("json2="+str(output))
    written="\n".join(lines)+"\n"
    need(input_parts(written)["stable_sha256"]==
         calibration["stable_profile_sha256"],
         "SIMC_PROFILE_UNINTENTIONAL_MODIFICATION")
    return {"input":written,"raw_gear_override":raw,
            "expected_json2_rating":target,
            "stable_profile_sha256":part["stable_sha256"],
            "input_sha256":sha(written)}

def validate_native(native,rendered,calibration):
    need(native.get("report_version")=="2.0.0","SIMC_REPORT_VERSION")
    need(native.get("git_revision")==calibration["native_revision"],
         "SIMC_REVISION_CHANGED_RECALIBRATE")
    players=(native.get("sim") or {}).get("players") or []
    need(len(players)==1,"SIMC_SINGLE_PLAYER_REQUIRED")
    actual=read_rating(players[0])
    need(actual==rendered["expected_json2_rating"],
         "FINAL_NUMERIC_RATING_MISMATCH")
    dps=(players[0].get("collected_data") or {}).get("dps",{})
    count=dps.get("count");mean=dps.get("mean");sem=dps.get("mean_std_dev")
    need(type(count) is int and count>=20,"DPS_SAMPLE_COUNT")
    need(type(mean) in (float,int) and type(sem) in (float,int)
         and math.isfinite(mean) and mean>0 and math.isfinite(sem) and sem>=0,
         "DPS_MEAN_SEM_MISSING")
    return {"status":"PASS_NATIVE_NUMERIC_RATING_AND_DPS",
        "actual_buffed_stats_rating":actual,
        "requested_json2_rating":rendered["expected_json2_rating"],
        "raw_gear_override":rendered["raw_gear_override"],
        "dps_mean":mean,"dps_sem":sem,"dps_samples":count,
        "approx_dps_ci95":[mean-1.96*sem,mean+1.96*sem],
        "native_revision":native["git_revision"],
        "native_trinket_static_record_not_required":True,
        "external_component_source_attribution_not_claimed":True,
        "item_effects_owned_by_simc":True}

def render_static_chmv_candidate(reference,target,flask_vector,path,iterations):
    """Inject STATIC c=G+J+F, without inverting talent-inflated buffed_stats.

    gear_* encodes the controllable G+J vector; the caller's externally
    established flask vector F is subtracted ONCE from c. No attribution
    from buffed_stats and no subclass/talent effects model.
    """
    scenario.vector(target,"STATIC_CHMV_C")
    scenario.vector(flask_vector,"STATIC_FLASK_F_VECTOR")
    need(type(iterations) is int and 30<=iterations<=100000,
         "ITERATIONS_OUT_OF_RANGE")
    raw={k:target[k]-flask_vector[k] for k in STATS}
    need(all(type(raw[k]) is int and raw[k]>=0 for k in STATS),
         "STATIC_TARGET_BELOW_DECLARED_FLASK_VECTOR")
    parts=input_parts(reference,allow_missing_json2_template=True)
    lines=reference.splitlines()
    output=pathlib.Path(path).resolve()
    for i,line in enumerate(lines):
        for k in STATS:
            if line.startswith(GEAR_PREFIX+k+"="):
                lines[i]=GEAR_PREFIX+k+"="+str(raw[k])
        if line.startswith("iterations="):
            lines[i]="iterations="+str(iterations)
        if line.startswith("json2="):
            lines[i]="json2="+str(output)
    if not any(line.startswith("json2=") for line in lines):
        lines.append("json2="+str(output))
    content="\n".join(lines)+"\n"
    rewritten=input_parts(content)
    need(rewritten["stable_sha256"]==parts["stable_sha256"]
         and rewritten["gear_override"]==raw,
         "STATIC_C_SOURCE_OR_GEAR_OVERRIDE_DRIFT")
    return {"input":content,"input_sha256":sha(content),
        "raw_gear_override":raw,"expected_static_rating":dict(target),
        "flask_component_in_T":dict(flask_vector),
        "stable_profile_sha256":parts["stable_sha256"],
        "buffed_stats_target_parity_required":False}

def validate_static_native(native,rendered,revision):
    """Check stat injection *before talents*, observe buffed output separately."""
    need(native.get("report_version")=="2.0.0","SIMC_REPORT_VERSION")
    need(native.get("git_revision")==revision,"SIMC_REVISION_CHANGED")
    players=(native.get("sim") or {}).get("players") or []
    need(len(players)==1,"SIMC_SINGLE_PLAYER_REQUIRED")
    raw=rendered["raw_gear_override"]
    fixed=rendered["flask_component_in_T"]
    target=rendered["expected_static_rating"]
    need(all(raw[k]+fixed[k]==target[k] for k in STATS),
         "STATIC_C_COMPONENT_SUM_MISMATCH")
    observed=read_rating(players[0])
    dps=(players[0].get("collected_data") or {}).get("dps",{})
    count=dps.get("count");mean=dps.get("mean");sem=dps.get("mean_std_dev")
    need(type(count) is int and count>=20,"DPS_SAMPLE_COUNT")
    need(type(mean) in (int,float) and type(sem) in (int,float)
         and math.isfinite(mean) and mean>0 and math.isfinite(sem) and sem>=0,
         "DPS_MEAN_SEM_MISSING")
    return {"status":"PASS_NATIVE_DPS_AND_STATIC_CHMV_INPUT",
        "target_static_CHMV_c":dict(target),
        "verified_static_CHMV_c":{k:raw[k]+fixed[k] for k in STATS},
        "actual_buffed_stats_rating":observed,
        "flask_F_component":dict(fixed),
        "raw_gear_override":dict(raw),
        "dps_mean":mean,"dps_sem":sem,"dps_samples":count,
        "native_revision":revision,
        "simc_talents_procs_APL_and_DPS_owned_by":"SimC",
        "buffed_rating_is_not_static_target":True}

def compare_pair(results):
    need(len(results)==2,"TWO_RESULT_COMPARISON")
    x,y=results
    delta=y["dps_mean"]-x["dps_mean"]
    half=1.96*math.hypot(x["dps_sem"],y["dps_sem"])
    return {"second_minus_first_dps":delta,
            "approx_95pct_halfwidth":half,
            "statistically_separated_approx95":abs(delta)>half,
            "winner_if_separated":"second" if delta>half
               else "first" if delta < -half else None,
            "global_optimum_proven":False}
