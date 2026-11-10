#!/usr/bin/env python3
"""IDEA-006 retrospective local-quadratic screen, ONLY prior genuine SimC.

Verifies three original accepted journal byte SHA and 9906 unique scout35 /
48 distinct precision320 source identities through p2_v312 original reader.
All 48 precision target vectors (including their 35-iteration scout rows)
are omitted from fitting. Comparing local radius configurations ON these
48 is exploratory hyperparameter selection, not an independent winning
optimizer, a confidence statement, or an authorization for new Native.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import statistics

import numpy as np

from integration_probes import p2_v312_historical_9906_model_screen_offline as original
from runner import v312_model_guided_multiregion_policy as global_model

SCHEMA="p2_idea006_original9906_local_geometry_48precision_screen_v1"
B=3400
SIZES=(128,400,1200)
RADII=(.16,.22,.30,.40)
LAMBDA=.02
LOCAL_MIN=15


def need(ok,reason):
    if not ok:
        raise ValueError("IDEA006_"+reason)


def features(d):
    a,b,c=d.T
    return np.stack((a,b,c,a*a,b*b,c*c,a*b,a*c,b*c),axis=1)


def _fit_at(rows,center,radius,*,return_flat=False):
    x=np.asarray([original.v(r) for r in rows],dtype=float)/B
    y=np.asarray([r["dps_mean"] for r in rows],dtype=float)
    sem=np.asarray([r["dps_sem"] for r in rows],dtype=float)
    distances=np.sum(np.abs(x-center),axis=1)/2
    chosen=np.nonzero(distances<=radius)[0]
    if len(chosen)<LOCAL_MIN:
        return None,len(chosen),None
    dx=(x[chosen,:3]-center[:3])/radius
    design=np.concatenate(
        (np.ones((len(chosen),1)),features(dx)),axis=1)
    weights=(np.maximum(0.,1.-distances[chosen]/radius)**2
             /np.maximum(350.,sem[chosen])**2)
    weights/=np.mean(weights)
    centered=np.average(y[chosen],weights=weights)
    ridge=np.diag([1.e-6]+[LAMBDA]*3+[4*LAMBDA]*6)
    coeff=np.linalg.solve(
        design.T@(design*weights[:,None])+ridge,
        design.T@((y[chosen]-centered)*weights))
    pred=float(centered+coeff[0])
    need(math.isfinite(pred),"LOCAL_NONFINITE_PREDICTION")
    if not return_flat:
        return pred,len(chosen),None
    h=np.asarray((
        (2*coeff[4],coeff[7],coeff[8]),
        (coeff[7],2*coeff[5],coeff[9]),
        (coeff[8],coeff[9],2*coeff[6])),dtype=float)
    eig,orientation=np.linalg.eigh(h)
    flat=orientation[:,np.argmin(np.abs(eig))]
    return pred,len(chosen),flat


def rmse(pred,truth):
    return math.sqrt(statistics.fmean(
        (float(a)-float(b))**2 for a,b in zip(pred,truth)))


def direction_stability(rows):
    centers=[]
    for r in sorted(rows,key=lambda r:(
            -(r["dps_mean"]-.5*r["dps_sem"]),original.v(r))):
        x=np.asarray(original.v(r),dtype=float)/B
        if all(np.sum(np.abs(x-a))/2>=.10 for a in centers):
            centers.append(x)
            if len(centers)==8:
                break
    left,right=rows[::2],rows[1::2]
    cosines=[]
    local_counts=[]
    for center in centers:
        _,n1,v1=_fit_at(left,center,.30,return_flat=True)
        _,n2,v2=_fit_at(right,center,.30,return_flat=True)
        if v1 is None or v2 is None:
            continue
        cosines.append(abs(float(np.dot(v1,v2))))
        local_counts.append([n1,n2])
    return {
        "separated_training_selected_anchors":len(centers),
        "anchors_with_two_valid_independent_half_fits":len(cosines),
        "flat_eigenvector_hemisphere_cosines":[round(v,5) for v in cosines],
        "median_flat_eigenvector_abs_cosine":(
            round(statistics.median(cosines),5) if cosines else None),
        "count_abs_cosine_below_0_8":sum(v<.8 for v in cosines),
        "same_precision_holdout_never_used_for_anchor_selection":True,
        "direction_stability_not_native_optimization_evidence":True}


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--original11-compact",required=True)
    parser.add_argument("--original25-compact",required=True)
    parser.add_argument("--original50-compact",required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args(argv)
    source=[original.source(p,i) for i,p in enumerate((
        args.original11_compact,args.original25_compact,
        args.original50_compact))]
    scouts=[r for _,s,_,_ in source for r in s]
    precision=[r for _,_,p,_ in source for r in p]
    need(len(scouts)==9906 and len(precision)==48
         and len({original.v(r) for r in scouts})==9906
         and len({original.v(r) for r in precision})==48,
         "ORIGINAL_COHORT_CARDINALITY")
    heldout={original.v(r) for r in precision}
    need(heldout.issubset({original.v(r) for r in scouts}),
         "CONFIRMATION_VECTOR_MUST_HAVE_35_SCOUT")
    training=[r for r in scouts if original.v(r) not in heldout]
    need(len(training)==9858,"NO_320_TARGET_SCOUT_LEAKAGE")
    ordered=original.spatial_interleaved_pool(training)
    truth=[r["dps_mean"] for r in precision]
    controls=[]
    for size in SIZES:
        prefix=ordered[:size]
        records=tuple((original.v(r),float(r["dps_mean"]),
                       float(r["dps_sem"])) for r in prefix)
        global_fit=global_model._fit(records,B)
        global_predictions=[global_model._predict(
            global_fit,original.v(r),B) for r in precision]
        global_error=rmse(global_predictions,truth)
        variants=[]
        for radius in RADII:
            predictions=[]
            neighbors=[]
            for p in precision:
                estimated,n,_=_fit_at(
                    prefix,np.asarray(original.v(p),dtype=float)/B,radius)
                predictions.append(estimated)
                neighbors.append(n)
            valid=[i for i,e in enumerate(predictions) if e is not None]
            variants.append({
                "radius_fraction_of_B_L1_half":radius,
                "precision_holdout_prediction_count":len(valid),
                "median_training_neighbors":statistics.median(neighbors),
                "prediction_320_rmse_on_valid":(
                    round(rmse([predictions[i] for i in valid],
                               [truth[i] for i in valid]),3)
                    if valid else None)})
        complete=[v for v in variants
                  if v["precision_holdout_prediction_count"]==48]
        best=min(complete,key=lambda v:v["prediction_320_rmse_on_valid"]
                 ) if complete else None
        controls.append({
            "global_training_original_35_scouts":size,
            "original_global_cubic_precision48_rmse":round(global_error,3),
            "local_quadratic_candidates":variants,
            "best_local_radius_chosen_on_same_holdout_exploratory":best,
            "best_local_beats_global":bool(best and
                best["prediction_320_rmse_on_valid"]<global_error),
            "chosen_local_radius_is_not_independent_heldout_validation":True})
    stability=direction_stability(ordered[:1200])
    output={
        "schema":SCHEMA,
        "status":"OFFLINE_EXPLORATORY_SCREEN_COMPLETED",
        "source_profile_sha256":original.PROFILE,
        "simc_binary_sha256":original.BINARY,
        "revision":original.REVISION,
        "original_compact_sha256":[a[3] for a in source],
        "source_real_scout35_total":9906,
        "source_real_precision320_heldout":48,
        "excluded_all_48_confirmed_vector_scout_rows_from_training":True,
        "model_screen_by_budget":controls,
        "direction_stability_at_1200_training":stability,
        "new_real_native_calls":0,
        "model_predicted_dps_never_used_as_simc_observation":True,
        "local_quadratic_surrogate_better_optimizer_proven":False,
        "anisotropic_direction_candidate_improves_dps_proven":False,
        "independent_hyperparameter_selection":False,
        "different_spec_generalization_proven":False,
        "global_optimum_proven":False,"familywise_95_proven":False,
        "idea006_next_decision":"DO_NOT_PROMOTE_LOCAL_QUADRATIC_SOLELY_FROM_RMSE",
        "source_effects_reimplemented":False,
    }
    path=pathlib.Path(args.output)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(output,sort_keys=True,
            indent=2,ensure_ascii=False,allow_nan=False)+"\n")
    print("IDEA006_ORIGINAL_NATIVE_OFFLINE_SCREEN",json.dumps({
        "status":output["status"],
        "by_budget":[{
            "train":r["global_training_original_35_scouts"],
            "global_rmse":r["original_global_cubic_precision48_rmse"],
            "best_local":r["best_local_radius_chosen_on_same_holdout_exploratory"]}
            for r in controls],
        "direction_stability":stability,
        "new_native":0},sort_keys=True),flush=True)
    return output


if __name__=="__main__":
    main()
