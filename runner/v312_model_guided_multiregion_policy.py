#!/usr/bin/env python3
"""v312 experiment: cubic response-surface + multi-region diverse proposals.

This is a pure, source-agnostic *proposal heuristic* above the existing
SimC executor, not a second DPS engine, an effect simulator, or a 95% test.
Real 35/320-iteration DPS and SEM remain owned by the original v065/v291
Native pipeline. Explicit opt-in; never changes the v290 product default.

Unlike v307/v309, 11-/21-level grids are ONLY a cheap set of potential
candidate coordinates. They are NOT exhaustively simulated. The optimizer
trains a regularized degree-3 CHMV response model on actual previously
measured values, uses independent best-measured region anchors, and reserves
a portion of each 16-scout epoch for uncertainty/distance exploration.
The model is an acquisition ranking approximation, never an observed DPS
or accepted SimC cache entry.
"""
from __future__ import annotations

import functools
import itertools
import math
import statistics

import v290_multiscale_adaptive_policy as base
import v307_dense_nested_coverage_grid as finite_grid

SCHEMA="v312_model_guided_multiregion_native_proposal_v1"
METADATA=("surrogate_stage","surrogate_epoch","surrogate_rank","surrogate_method")
STAGES=frozenset(("global","adaptive","confirmation"))
BATCH=16
MODEL_SCALE=10000.0
CONFIRM_PER_SESSION=16
REGION_LIMIT=8
MODEL_SAMPLE_21=2048
GLOBAL_SEEDS=128
EXPONENTS=tuple(sorted(
    (ex for ex in itertools.product(range(4),repeat=3) if sum(ex)<=3),
    key=lambda x:(sum(x),x)))
PAIRS=(.12,.06,.03,.015,.0075,.003,.0015)
METHODS=frozenset(("balanced_global_maximin","global_maximin",
                   "model_ucb","measured_region","global_uncertainty",
                   "source_native_confirmation"))


class ProposalBlocked(ValueError):
    pass


def need(ok,reason):
    if not ok:
        raise ProposalBlocked(reason)


def options(max_native_calls,*,initial_global_calls=GLOBAL_SEEDS,
            confirmation_calls=CONFIRM_PER_SESSION):
    need(type(max_native_calls) is int and 400<=max_native_calls<=2400
         and type(initial_global_calls) is int and
         64<=initial_global_calls<=256 and
         initial_global_calls % BATCH == 0 and
         type(confirmation_calls) is int and
         8<=confirmation_calls<=32 and
         max_native_calls>=initial_global_calls+confirmation_calls+128 and
         (max_native_calls-confirmation_calls-initial_global_calls)%BATCH==0,
         "V312_EXPLICIT_BATCH_NATIVE_CAP_OR_CONFIRM_BUDGET")
    return {"total_native_calls":max_native_calls,
            "global_scouts":initial_global_calls,
            "adaptive_scouts":max_native_calls-confirmation_calls-
                initial_global_calls,
            "precision_calls":confirmation_calls,
            "total_scouts":max_native_calls-confirmation_calls,
            "batch_size":BATCH,"max_confirm_iterations_in_source":None,
            "user_time_cap_owned_by_v291":True,
            "no_global_optimum_proof":True}


def _vector(row):
    return tuple(base.legacy.key(row["target"]))


def _validated(row,total,lower,upper):
    v=_vector(row)
    need(base.legacy.eligible(v,total,lower,upper),
         "V312_HISTORY_OUTSIDE_VERIFIED_BOUNDS")
    need(type(row.get("iterations")) is int and
         1<=row["iterations"]<=10_000_000 and
         all(type(row.get(x)) in (float,int) and
             math.isfinite(row[x]) and row[x]>=0
             for x in ("dps_mean","dps_sem")),
         "V312_HISTORY_REQUIRES_GENUINE_NATIVE_SUMMARY")
    return v


def _feat(v,total):
    x=tuple(float(n)/total for n in v[:3])
    powers=tuple((1.0,z,z*z,z*z*z) for z in x)
    return tuple(powers[0][a]*powers[1][b]*powers[2][c]
                 for a,b,c in EXPONENTS)


def _solve(matrix,rhs):
    """Small 20x20 regularized Gaussian solve, no ML dependency."""
    n=len(rhs)
    a=[list(matrix[i])+[rhs[i]] for i in range(n)]
    for i in range(n):
        pivot=max(range(i,n),key=lambda j:abs(a[j][i]))
        need(abs(a[pivot][i])>1e-12,
             "V312_REGULARIZED_FIT_SINGULAR")
        a[i],a[pivot]=a[pivot],a[i]
        div=a[i][i]
        for k in range(i,n+1):
            a[i][k]/=div
        for j in range(i+1,n):
            ratio=a[j][i]
            if ratio==0:
                continue
            for k in range(i,n+1):
                a[j][k]-=ratio*a[i][k]
    result=[0.0]*n
    for i in range(n-1,-1,-1):
        result[i]=a[i][n]-sum(a[i][j]*result[j]
                              for j in range(i+1,n))
    return tuple(result)


def _fit(records,total):
    need(len(records)>=64,"V312_NO_GLOBAL_TRAINING_MEASUREMENTS")
    center=statistics.fmean(row[1] for row in records)
    size=len(EXPONENTS)
    matrix=[[0.0]*size for _ in range(size)]
    right=[0.0]*size
    for v,dps,sem in records:
        features=_feat(v,total)
        # The SEM determines a weight, not an invented precision claim.
        weight=min(5.0,max(.2,(650.0/max(300.0,sem))**2))
        residual=(dps-center)/MODEL_SCALE
        for i,feature in enumerate(features):
            wf=weight*feature
            right[i]+=wf*residual
            for j in range(i+1):
                matrix[i][j]+=wf*features[j]
    for i,ex in enumerate(EXPONENTS):
        degree=sum(ex)
        matrix[i][i]+={0:1e-8,1:1e-4,2:5e-4,3:1e-3}[degree]
        for j in range(i):
            matrix[j][i]=matrix[i][j]
    fit=_solve(matrix,right)
    need(all(math.isfinite(x) for x in fit),
         "V312_MODEL_COEFFICIENTS_NONFINITE")
    return (center,fit)


def _predict(model,v,total):
    center,coef=model
    return center+MODEL_SCALE*sum(a*b for a,b in
                                    zip(coef,_feat(v,total)))


@functools.lru_cache(maxsize=4)
def _global_order(total,lower,upper,count):
    lower,upper=finite_grid._params(total,lower,upper,21)
    pool=tuple(dict.fromkeys(base._global_pool(
        total,lower,upper,min(512,max(count*2,256)))))
    need(len(pool)>=count,"V312_INSUFFICIENT_FEASIBLE_GLOBAL_SEEDS")
    chosen=[pool[0]]
    remaining=set(pool[1:])
    while len(chosen)<count:
        point=max(remaining,
                  key=lambda v:(min(base._distance(v,c) for c in chosen),
                                tuple(-x for x in v)))
        chosen.append(point)
        remaining.remove(point)
    return tuple(chosen)


@functools.lru_cache(maxsize=3)
def _static_pool(total,lower,upper):
    lower,upper=finite_grid._params(total,lower,upper,21)
    coarse=finite_grid.lattice(total,lower,upper,11)
    fine=finite_grid.lattice(total,lower,upper,21)
    chosen=sorted(fine,key=lambda v:(finite_grid._hash(v),v))[
        :MODEL_SAMPLE_21]
    pool=set(coarse)|set(chosen)
    pool.update(_global_order(total,lower,upper,GLOBAL_SEEDS))
    need(all(base.legacy.eligible(v,total,lower,upper) for v in pool),
         "V312_STATIC_PROPOSAL_POOL_INVALID")
    return tuple(sorted(pool))


def _records(rows,total,lower,upper):
    values=[]
    seen=set()
    for row in rows:
        v=_validated(row,total,lower,upper)
        identity=(v,row["iterations"])
        need(identity not in seen,
             "V312_DUPLICATE_NATIVE_ITERATION_IDENTITY")
        seen.add(identity)
        values.append((v,float(row["dps_mean"]),
                       float(row["dps_sem"])))
    return tuple(values)


def _regions(records,model,total):
    # Retain multiple spatially distinct high-response *measured* anchors.
    ranked=sorted(records,key=lambda r:(
        -(_predict(model,r[0],total)+
          .18*max(-2000.,min(2000.,r[1]-_predict(model,r[0],total)))
          -.12*r[2]),r[0]))
    chosen=[]
    minimum=max(1,total*.055)
    for record in ranked:
        if all(base._distance(record[0],r[0])>=minimum
               for r in chosen):
            chosen.append(record)
            if len(chosen)>=REGION_LIMIT:
                break
    # When many candidates lie in the same region, still retain the best.
    return tuple(chosen)


def _local_candidates(regions,total,lower,upper,seen):
    local=set()
    for center,_,_ in regions:
        for fraction in PAIRS:
            step=max(1,round(total*fraction))
            for point,_ in base._bounded_fraction_neighbors(
                    center,step,total,lower,upper,seen):
                local.add(point)
    return local


def _plan_batch(total,lower,upper,records):
    """One fixed 16-case batch planned only from earlier accepted Native rows.

    This can be reconstructed byte-for-byte after restart. No pending case
    is allowed to retroactively change any earlier batch's model.
    """
    rows=[(tuple(v),float(dps),float(sem)) for v,dps,sem in records]
    model=_fit(rows,total)
    seen={r[0] for r in rows}
    region=_regions(rows,model,total)
    local=_local_candidates(region,total,lower,upper,seen)
    pool=set(_static_pool(total,lower,upper))|local
    # Local fine moves around the *surrogate* peaks, retaining measured
    # anchors independently; neither is treated as native evidence.
    predicted_peaks=sorted(
        (v for v in _static_pool(total,lower,upper) if v not in seen),
        key=lambda v:(-_predict(model,v,total),v))
    peak_region=[]
    for point in predicted_peaks:
        if all(base._distance(point,old)>=total*.055
               for old in peak_region):
            peak_region.append(point)
            if len(peak_region)==6:
                break
    for center in peak_region:
        for fraction in (.03,.015,.0075,.003):
            step=max(1,round(total*fraction))
            for candidate,_ in base._bounded_fraction_neighbors(
                    center,step,total,lower,upper,seen):
                local.add(candidate)
                pool.add(candidate)
    pool.difference_update(seen)
    need(len(pool)>=BATCH,"V312_GLOBAL_LOCAL_PROPOSAL_POOL_EXHAUSTED")
    # Approximate spatial uncertainty via independent chronological
    # coreset, recent points and measured regional winners.
    stride=max(1,len(rows)//144)
    anchors=list(dict.fromkeys(
        [r[0] for r in rows[::stride]]+
        [r[0] for r in rows[-24:]]+
        [r[0] for r in region]))
    best_observed=max(r[1] for r in rows)
    candidates=[]
    for v in pool:
        predicted=min(best_observed+2500.,_predict(model,v,total))
        novelty=min(base._distance(v,p) for p in anchors)/total
        novelty=min(.22,novelty)
        candidates.append((v,predicted,novelty,v in local))
    selected=[]
    selected_points=[]
    # Three complementary acquisitions per batch, not a single
    # noisy 35-iteration winner. Mode scheduling is deterministic.
    modes=("model_ucb",)*8+("measured_region",)*5+(
        "global_uncertainty",)*3
    for mode in modes:
        ranked=(c for c in candidates if c[0] not in selected_points
                and (mode!="measured_region" or c[3]))
        def utility(item):
            v,pred,novelty,is_local=item
            diversity=min((base._distance(v,p)/total
                           for p in selected_points),default=1.0)
            penalty=1250.0*math.exp(-diversity/.024)
            if mode=="model_ucb":
                return pred+1100.0*novelty-penalty
            if mode=="measured_region":
                return pred+1650.0*novelty-penalty
            return pred+4100.0*novelty-penalty
        pick=max(ranked,key=lambda c:(utility(c),
                                     tuple(-x for x in c[0])),default=None)
        # No local feasible proposal: use globally selected pool.
        if pick is None:
            pick=max((c for c in candidates
                      if c[0] not in selected_points),
                     key=lambda c:(utility(c),
                                   tuple(-x for x in c[0])),default=None)
        need(pick is not None,"V312_BATCH_CANDIDATE_POOL_EXHAUSTED")
        selected_points.append(pick[0])
        selected.append((pick[0],mode))
    need(len(set(selected_points))==BATCH and
         all(base.legacy.eligible(v,total,lower,upper)
             for v in selected_points),
         "V312_BATCH_UNIQUE_NATIVE_BOUNDS")
    return tuple(selected)


@functools.lru_cache(maxsize=3)
def _cached_batch(total,lower,upper,records):
    return _plan_batch(total,lower,upper,records)


def _confirm_order(rows,total,lower,upper,count):
    records=_records(rows,total,lower,upper)
    model=_fit(records,total)
    pool=sorted(records,key=lambda r:(
        -(_predict(model,r[0],total)
          +.22*max(-2500.,min(2500.,r[1]-_predict(model,r[0],total)))
          -.10*r[2]),r[0]))
    picked=[]
    used=set()
    # First half protects independent nearby peaks; second half fills
    # highest-quality remaining candidates, regardless of location.
    spacing=max(1,total*.018)
    for record in pool:
        v=record[0]
        if v not in used and all(base._distance(v,old)>=spacing
                                 for old in picked):
            picked.append(v)
            used.add(v)
            if len(picked)>=count//2:
                break
    for record in pool:
        v=record[0]
        if v not in used:
            picked.append(v)
            used.add(v)
            if len(picked)==count:
                break
    need(len(picked)==count,"V312_NOT_ENOUGH_NATIVE_CONFIRM_TARGETS")
    return tuple(picked)


def next_plan(observations, *,total,lower,upper,max_native_calls,
              scout_iterations,confirmation_iterations,
              initial_global_calls=GLOBAL_SEEDS,confirmation_calls=16):
    lower,upper=finite_grid._params(total,lower,upper,21)
    settings=options(max_native_calls,
                     initial_global_calls=initial_global_calls,
                     confirmation_calls=confirmation_calls)
    need(type(observations) is list and
         type(scout_iterations) is int and
         type(confirmation_iterations) is int and
         1<=scout_iterations<confirmation_iterations,
         "V312_TYPED_SIMC_ITERATION_CONTRACT")
    count=len(observations)
    if count>=max_native_calls:
        return {"schema":SCHEMA,"status":"BUDGET_EXHAUSTED",
                "next_request":None,"global_optimum_proven":False}
    if count<settings["global_scouts"]:
        order=_global_order(total,lower,upper,settings["global_scouts"])
        v=order[count]
        stage,epoch,rank,method="global",0,count,(
            "balanced_global_maximin" if count==0 else "global_maximin")
        phase,iters="scout",scout_iterations
    elif count<settings["total_scouts"]:
        start=settings["global_scouts"]+(
            (count-settings["global_scouts"])//BATCH)*BATCH
        position=count-start
        records=_records(observations[:start],total,lower,upper)
        picks=_cached_batch(total,lower,upper,records)
        v,method=picks[position]
        stage,epoch,rank="adaptive",(start-settings["global_scouts"])//BATCH,position
        phase,iters="scout",scout_iterations
    else:
        order=_confirm_order(
            observations[:settings["total_scouts"]],
            total,lower,upper,settings["precision_calls"])
        rank=count-settings["total_scouts"]
        v=order[rank]
        stage,epoch,method="confirmation",-1,"source_native_confirmation"
        phase,iters="precision",confirmation_iterations
    need(base.legacy.eligible(v,total,lower,upper)
         and (phase=="precision" or v not in {
             _vector(r) for r in observations}),
         "V312_NONUNIQUE_SCOUT_OR_OUT_OF_BOUNDS")
    return {"schema":SCHEMA,"status":"NEXT_NATIVE_PROPOSED",
            "decision":"V312_"+method.upper(),
            "next_request":{
                "phase":phase,"target":base.legacy.to_target(v),
                "iterations":iters,"surrogate_stage":stage,
                "surrogate_epoch":epoch,"surrogate_rank":rank,
                "surrogate_method":method},
            "observed_unique_candidates":len(observations),
            "global_optimum_proven":False,
            "model_prediction_is_not_observed_native_dps":True}


def audit_recorded_history(rows, *,total,lower,upper,max_native_calls,
                           scout_iterations,confirmation_iterations,
                           initial_global_calls=GLOBAL_SEEDS,
                           confirmation_calls=CONFIRM_PER_SESSION):
    """Original Native JSON2/receipts are authenticated upstream by v291.

    Reconstruct every proposal from only the PREVIOUS measured rows.
    Check the exact policy order and metadata; no lookahead or forecast
    may silently become an accepted DPS observation.
    """
    need(type(rows) is list and len(rows)<=max_native_calls,
         "V312_ACCEPTED_HISTORY_EXCEEDS_BOUND")
    for i,row in enumerate(rows):
        proposal=next_plan(rows[:i],total=total,lower=lower,upper=upper,
            max_native_calls=max_native_calls,scout_iterations=scout_iterations,
            confirmation_iterations=confirmation_iterations,
            initial_global_calls=initial_global_calls,
            confirmation_calls=confirmation_calls)
        req=proposal["next_request"]
        need(req is not None and
             all(k in row for k in METADATA) and
             row["phase"]==req["phase"] and
             row["iterations"]==req["iterations"] and
             row["target"]==req["target"] and
             all(row[k]==req[k] for k in METADATA),
             "V312_RECORDED_SURROGATE_PLAN_OR_STAGE_DRIFT")
    return {"history_rows":len(rows),
            "model_predictions_not_native_receipts":True,
            "original_native_byte_authentication_owned_by_v291":True}


def coverage(rows, *,max_native_calls,initial_global_calls=GLOBAL_SEEDS,
             confirmation_calls=CONFIRM_PER_SESSION):
    settings=options(max_native_calls,
                     initial_global_calls=initial_global_calls,
                     confirmation_calls=confirmation_calls)
    stages={s:0 for s in STAGES}
    for row in rows:
        stage=row["surrogate_stage"]
        need(stage in stages,"V312_UNEXPECTED_SURROGATE_STAGE")
        stages[stage]+=1
    return {"schema":SCHEMA,"total_budget":max_native_calls,
            "completed":len(rows),"stage_counts":stages,
            "planned_global":settings["global_scouts"],
            "planned_adaptive":settings["adaptive_scouts"],
            "planned_confirmations":settings["precision_calls"],
            "model_predictions_not_observed_native":True,
            "global_optimum_proven":False,
            "familywise_95_proven":False}
