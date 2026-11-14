#!/usr/bin/env python3
"""v440 read-only replay of six *existing* v439 Native JSON2 receipts.

No SimC, no season HTTP or reoptimisation. Uses EXACT existing v065 95%
fresh confirmation and v094 observed-near-alternative policies. The caller
must supply original v439 GitHub Actions artifact and sealed compact proof.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import pathlib
import zipfile

import v065_v015_scheduler_adapter as policy95
import v094_durable_inclusive_adaptive_runner as adaptive

SCHEMA="p1_v440_v439_real_json2_existing_policy_audit_v1"
STATS=("crit_rating","haste_rating","mastery_rating","versatility_rating")
CASES=(
    "confirmations/confirm_00","confirmations/confirm_01",
    "search/material_00","search/scout_00","search/seed_00",
    "search/seed_01",
)
ORIGINAL_OUTER_SHA="ac5f41298515d22121e635e57531e599164acdd97f3b00193becc7bae5311d76"
ORIGINAL_INNER_SHA="fcffd42b5f818a0e4fac296cd715afec628ebef35426823f9b737dd50ccceb52"
class ExistingEvidenceBlocked(ValueError): pass

def need(ok,reason):
    if not ok: raise ExistingEvidenceBlocked("V440_"+reason)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def target_tuple(row):
    return tuple(row["target"][k] for k in STATS)

def same_float(a,b):
    return (type(a) in (int,float) and type(b) in (int,float)
        and math.isfinite(a) and math.isfinite(b)
        and math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-7))

def run(artifact,compact):
    artifact=pathlib.Path(artifact)
    proof=json.loads(pathlib.Path(compact).read_text(encoding="utf8"))
    need(type(proof) is dict and
         proof.get("schema")==
             "p1_v439_windows_70783_selected_four_tier_actual_native_compact_v1"
         and proof.get("evidence_status")==
             "PASS_REAL_70783_SELECTED_FOUR_TIER_DPS6_CACHE6"
         and proof.get("game_build")=="12.1.5.70783"
         and proof.get("character")=="hunter/survival"
         and proof.get("target_ilevel")==334
         and proof.get("artifact_outer_zip_sha256")==ORIGINAL_OUTER_SHA
         and proof.get("native_evidence_zip_sha256")==ORIGINAL_INNER_SHA,
         "ORIGINAL_70783_ARCHIVE_AND_COMPACT_SHA_REQUIRED")
    if artifact.is_dir():
        # Actions/download-artifact extracts the original ZIP but does not
        # preserve its outer container bytes. The pinned nested ZIP+static
        # snapshot SHA still authenticate every Native case exactly.
        nested=(artifact/"V439_B8_SIX_NATIVE_JSON2_EVIDENCE.zip").read_bytes()
        checked_outer_bytes=False
        need(sha((artifact/"selected_v046_snapshot.json").read_bytes())==
                 proof["static_cache_snapshot_sha256"],
             "EXTRACTED_ORIGINAL_V046_SNAPSHOT_SHA_DRIFT")
    else:
        raw=artifact.read_bytes()
        need(sha(raw)==ORIGINAL_OUTER_SHA,
             "OUTER_ORIGINAL_ARTIFACT_SHA_DRIFT")
        with zipfile.ZipFile(io.BytesIO(raw),"r") as outer:
            need(outer.testzip() is None,"OUTER_ZIP_CRC_FAILURE")
            nested=outer.read("V439_B8_SIX_NATIVE_JSON2_EVIDENCE.zip")
        checked_outer_bytes=True
    need(sha(nested)==ORIGINAL_INNER_SHA,"SIX_NATIVE_EVIDENCE_SHA_DRIFT")
    observations=[]
    verified={}
    with zipfile.ZipFile(io.BytesIO(nested),"r") as source:
        need(source.testzip() is None and
             set(source.namelist())=={
                 case+"/"+name for case in CASES
                 for name in ("input.simc","result.json","native_receipt.json")},
             "EXACT_SIX_ORIGINAL_CASES_AND_THREE_RECEIPTS_EACH_REQUIRED")
        for case in CASES:
            source_raw=source.read(case+"/input.simc")
            json_raw=source.read(case+"/result.json")
            saved=json.loads(source.read(case+"/native_receipt.json"))
            result=json.loads(json_raw)
            need(saved.get("schema")==
                "v064_external_adaptive_evaluator_port_v1"
                and saved.get("status")==
                    "PASS_NATIVE_DPS_AND_STATIC_CHMV_INPUT"
                and saved.get("rating_semantics")=="STATIC_CHMV_C_V1"
                and saved.get("native_revision")==proof["simc_revision"]
                and saved.get("simc_binary_sha256")==proof[
                    "simc_binary_sha256"]
                and saved.get("input_sha256")==sha(source_raw)
                and saved.get("native_json_sha256")==sha(json_raw)==
                    proof["DPS_native_json2_sha256"][case+"/result.json"]
                and saved.get("static_rating_verified")==saved.get("target"),
                "SAVED_NATIVE_SOURCE_JSON_SHA_OR_STATIC_RATING_DRIFT:"+case)
            # SimC JSON2 encodes the short revision ("de11f57");
            # v064's native receipt binds the full 40-character revision.
            native_rev=result.get("git_revision")
            need(result.get("report_version")=="2.0.0" and
                 type(native_rev) is str and len(native_rev)>=7 and
                 proof["simc_revision"].startswith(native_rev),
                 "JSON2_REPORT_OR_REVISION_NOT_PINNED:"+case)
            sim=result["sim"]
            need(type(sim.get("players")) is list and len(sim["players"])==1,
                 "JSON2_PLAYER_COUNT_NOT_ONE:"+case)
            actor=sim["players"][0]
            need(actor.get("specialization")=="Survival Hunter"
                 and sim["options"].get("seed")==saved.get("simc_seed")
                 and saved["simc_seed"] is not None,
                 "JSON2_SPECIALIZATION_OR_SEED_DRIFT:"+case)
            dps=actor["collected_data"]["dps"]
            need(same_float(dps["mean"],saved["dps_mean"]) and
                 same_float(dps["mean_std_dev"],saved["dps_sem"])
                 and dps["count"]==saved["dps_samples"]
                 and saved["iterations"]>=saved["dps_samples"]>=30,
                 "ACTUAL_JSON2_DPS_SEM_SAMPLES_NOT_SAVED:"+case)
            gear=actor["gear"]
            # Physical item effects and tier identity are checked against
            # original Native JSON2, not inferred from selected item catalogs.
            for slot,id_ in {**proof["tier_gear_item_ids"],
                             "head":244579}.items():
                row=gear[slot]
                enc=row["encoded_item"]
                need((",id="+str(id_)+",") in enc and
                     row["ilevel"]==334,
                     "JSON2_PHYSICAL_SELECTED_4PC_NOT_EXACT:"+case+":"+slot)
            need(sum(saved["target"].values())==proof["budget"]["T"]
                 and set(saved["target"])==set(STATS),
                 "B8_NATIVE_T_TARGET_MISMATCH:"+case)
            obs=dict(saved)
            obs["v092_base_target"]={
                k:saved["target"][k]-proof["budget"]["O"][k] for k in STATS}
            need(sum(obs["v092_base_target"].values())==proof["budget"]["B"],
                 "B8_NATIVE_B_BUDGET_MISMATCH:"+case)
            observations.append(obs)
            verified[case]={
                "dps_mean":saved["dps_mean"],"dps_sem":saved["dps_sem"],
                "iterations":saved["iterations"],
                "simc_seed":saved["simc_seed"],
                "target":saved["target"],
                "input_sha256":saved["input_sha256"],
                "native_json2_sha256":saved["native_json_sha256"]}
    first=next(o for o,c in zip(observations,CASES)
               if c=="confirmations/confirm_00")
    second=next(o for o,c in zip(observations,CASES)
                if c=="confirmations/confirm_01")
    k1=target_tuple(first)
    k2=target_tuple(second)
    need(k1!=k2,"CONFIRMATIONS_ARE_IDENTICAL_CANDIDATE")
    judge=policy95.fresh_confirmation_judgment(
        (k1,k2),{k1:first,k2:second})
    summary=adaptive._candidate_summary(
        observations,proof["budget"]["B"],proof["budget"]["O"])
    need(summary["observed_unique_targets"]>=2 and
         summary["observed_best_T"]==proof["observed_first"][
             "absolute_rating_T"] and
         same_float(summary["observed_best_dps"],
                    proof["observed_first"]["observed_dps_mean"]) and
         same_float(summary["observed_best_sem"],
                    proof["observed_first"]["simc_sem"]) and
         judge["distinct_simc_seeds_observed"] is True and
         judge["pairwise_direction_supported"] is True and
         judge["statistical_separation_approx95_without_seed_claim"] is True,
         "SOURCE_NATIVE_95_CONFIRMATION_OR_BEST_INCONSISTENT")
    return {
        "schema":SCHEMA,
        "status":"PASS_ORIGINAL_V439_SIX_JSON2_OBSERVATIONS_REUSED_NO_NATIVE",
        "original_artifact_sha256":ORIGINAL_OUTER_SHA,
        "original_outer_artifact_bytes_checked":checked_outer_bytes,
        "original_six_evidence_zip_sha256":ORIGINAL_INNER_SHA,
        "game_build":proof["game_build"],
        "source_v439_native_calls_reused":proof["new_native_calls"]["total"],
        "new_native_calls":0,"recomputed_dps_calls":0,
        "confidence_level":0.95,
        "confirmation":judge,
        "source_confirmations":{
            "confirm_00":verified["confirmations/confirm_00"],
            "confirm_01":verified["confirmations/confirm_01"]},
        "observed_best":{
            "absolute_rating_T":summary["observed_best_T"],
            "observed_dps_mean":summary["observed_best_dps"],
            "simc_sem":summary["observed_best_sem"]},
        "observed_unique_targets":summary["observed_unique_targets"],
        "material_near_alternatives":summary["material_alternatives"],
        "material_near_definition":{
            "minimum_B_fraction_moved":summary["material_threshold_B_fraction"],
            "maximum_observed_relative_DPS_loss":
                summary["near_loss_threshold"]},
        "no_material_alt_observed_not_nonexistence_proof":
            summary["no_material_alt_found"],
        "global_optimum_proven":False,
        "decision_source":"ORIGINAL_v065_fresh_confirmation_judgment_AND_v094_candidate_summary",
        "original_actual_user_E2E_not_full_26_dps":True,
        "official_78_B8_not_promoted_here":True,
    }

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-archive",type=pathlib.Path,required=True)
    p.add_argument("--v439-compact",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    a=p.parse_args(argv)
    report=run(a.original_archive,a.v439_compact)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2,
                                sort_keys=True,allow_nan=False)+"\n",
                     encoding="utf8")
    print("V440",report["status"],
          "unique",report["observed_unique_targets"],
          "95_supported",report["confirmation"]["pairwise_direction_supported"],
          "near_alternatives",len(report["material_near_alternatives"]),
          "new_native",report["new_native_calls"],flush=True)

if __name__=="__main__":
    main()
