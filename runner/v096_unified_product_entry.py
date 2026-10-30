#!/usr/bin/env python3
"""v096 single manifest -> existing v091/093/094/095 source-locked product path.

No new solver, simulation mechanics, gear selection or Native gate.
Reference B is explicitly opt-in. Inclusive user manual T uses approved v092
conversion to legacy B. Exact Native G remains open.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,sys
import v046_static_item_cache as item_cache
import v061_scenario_contract as contract
import v065_v015_scheduler_adapter as scheduler
import v091_weapon_oil_external_adapter as oil_adapter
import v093_inclusive_adaptive_scheduler_bridge as adaptive
import v094_durable_inclusive_adaptive_runner as durable
import v141_verified_pure_native_pilot as pure_pilot
import v202_one_enchant_admission as verified_enchant

SCHEMA="v096_user_scenario_unified_entry_v1"
FIELDS={"schema","profile_simc","scenario_json","fillers_json",
        "static_cache_json","weapon_layout","oil_hands","flask_F",
        "seed_targets_B","native_binary","native_revision","output_dir",
        "scouts","material_scouts","native_limit","step","cancel_file"}
MANUAL_FIELD="manual_final_T"
NATIVE_ENCHANT_FIELD="v202_verified_enchant_choice"
# Optional internal stage seal: no Native until physical SimC acceptance.
STAGE_FIELD="unverified_pure_profile_plan_only"
class EntryBlocked(ValueError):pass
def need(ok,reason):
    if not ok:raise EntryBlocked(reason)
def path_for(base,value,nullable=False):
    if nullable and value is None:return None
    need(type(value) is str and bool(value.strip()),"ENTRY_PATH_REQUIRED")
    p=pathlib.Path(value).expanduser()
    return (p if p.is_absolute() else base/p).resolve()
def read_object(path):
    need(path.is_file(),"ENTRY_INPUT_NOT_FOUND:"+path.name)
    return json.loads(path.read_text(encoding="utf8"))

def source(manifest_path):
    """Build the existing typed and SHA-locked Native context; zero SimC calls."""
    manifest_path=pathlib.Path(manifest_path).resolve()
    user=read_object(manifest_path)
    allowed=(FIELDS,FIELDS|{MANUAL_FIELD},FIELDS|{STAGE_FIELD},
             FIELDS|{MANUAL_FIELD,STAGE_FIELD})
    allowed=tuple(x|{NATIVE_ENCHANT_FIELD} for x in allowed)+allowed
    need(type(user) is dict and set(user) in allowed
         and user.get("schema")==SCHEMA,"ENTRY_SCHEMA_OR_FIELDS")
    if STAGE_FIELD in user:
        need(user[STAGE_FIELD] is True,"STAGED_PROFILE_SEAL_INVALID")
    manual_T=user.get(MANUAL_FIELD)
    if MANUAL_FIELD in user:
        need(type(manual_T) is int and 1<=manual_T<=100000,
             "MANUAL_FINAL_T_REQUIRED")
    paths={k:path_for(manifest_path.parent,user[k],
                     nullable=k in ("static_cache_json","cancel_file"))
           for k in ("profile_simc","scenario_json","fillers_json",
                     "static_cache_json","native_binary","output_dir",
                     "cancel_file")}
    profile=paths["profile_simc"].read_text(encoding="utf8")
    doc=read_object(paths["scenario_json"])
    fillers=read_object(paths["fillers_json"])
    need(type(fillers) is list,"EXACT_FILLER_ROWS_LIST")
    cache=(item_cache.empty_cache() if paths["static_cache_json"] is None
           else item_cache.load(paths["static_cache_json"]))
    contract.vector(user["flask_F"],"DECLARED_FLASK_VECTOR")
    need(type(user["oil_hands"]) is list,"OIL_HANDS_LIST")
    need(type(user["seed_targets_B"]) is list
         and len(user["seed_targets_B"])==2,
         "TWO_SEED_B_VECTORS_REQUIRED")
    seeds=[contract.vector(v,"EXACT_INITIAL_BASE_VECTOR")
           for v in user["seed_targets_B"]]
    need(type(user["scouts"]) is int and 0<=user["scouts"]<=2
         and type(user["material_scouts"]) is int
         and 0<=user["material_scouts"]<=2
         and type(user["native_limit"]) is int and user["native_limit"]>=1
         and type(user["step"]) is int and user["step"]>0,"RUN_BOUNDS_INVALID")
    need(paths["native_binary"].is_file(),"SIMC_BINARY_NOT_PRESENT")
    binary_sha=hashlib.sha256(paths["native_binary"].read_bytes()).hexdigest()
    prepared=oil_adapter.prepare(profile,doc,fillers,cache,
                                 user["weapon_layout"],user["oil_hands"],
                                 manual_final_T=manual_T)
    if NATIVE_ENCHANT_FIELD in user:
        # Internal-only opt-in, exact item/revision/binary and immutable v200/
        # v201 witness; no new numeric gear_* contribution is injected.
        verified=verified_enchant.admit(user[NATIVE_ENCHANT_FIELD],
                  prepared["oil"]["profile"],prepared["prepared"]["scenario"],
                  binary_sha,user["native_revision"])
        prepared["oil"]["v202_verified_enchant"]=verified
    context=adaptive.prepare(prepared,binary_sha,user["native_revision"])
    normalized=prepared["prepared"]["scenario"]
    B,lo,hi=scheduler.bounds(normalized,
                          adaptive.feasible_budget(context,user["flask_F"]))
    need(all(scheduler.eligible(tuple(x[s] for s in contract.STATS),
                                B,lo,hi) for x in seeds)
         and seeds[0]!=seeds[1],"SEEDS_FAIL_BASE_B_L_BOUNDS")
    max_calls=normalized["scenario"]["runtime"]["max_native_calls"]
    minimum_calls=2+user["scouts"]+user["material_scouts"]+2
    need(minimum_calls<=user["native_limit"]<=max_calls,
         "SCENARIO_NATIVE_LIMIT_PRECHECK")
    need(sum(user["flask_F"].values())==normalized["budget"]["F"],
         "FLASK_F_TOTAL_MISMATCH")
    provenance=prepared["prepared"]["static_budget"]["reference_budget_provenance"]
    need(provenance["schema"]=="v090_reference_budget_provenance_v1",
         "SOURCE_BUDGET_PROVENANCE_REQUIRED")
    if manual_T is None:
        need(provenance["source"]=="reference_rounded_opt_in",
             "REFERENCE_B_ONLY_UNTIL_EXACT_G_MERGE")
    else:
        need(provenance["source"]=="user_manual_total"
             and provenance["budget_entry_mode"]=="USER_MANUAL_FINAL_T_CONVERTED_TO_B"
             and context["identity"]["approved_final_T"]==manual_T,
             "MANUAL_FINAL_T_SOURCE_OR_TOTAL_DRIFT")
    plan={"schema":SCHEMA,
          "status":"READY_SOURCE_LOCKED_NATIVE_ENTRY_NOT_EXECUTED",
          "official_formula":"T=G+J+F+O","base_B":B,
          "fixed_O":context["identity"]["oil_vector"],
          "final_T":context["identity"]["approved_final_T"],
          "class":normalized["scenario"]["character"]["class"],
          "spec":normalized["scenario"]["character"]["spec"],
          "item_slots":len(prepared["prepared"]["static_budget"]
                            ["reference_exact_slot_identity"]),
          "source_profile_sha256":context["identity"]["source_profile_sha256"],
          "binary_sha256":binary_sha,
          "scenario_digest":context["identity"]["scenario_digest"],
          "native_min_calls":minimum_calls,
          "native_limit":user["native_limit"],
          "scouts":user["scouts"],"material_scouts":user["material_scouts"],
          "native_called":False,
          "original_product_v015_v016_merged":False,
          "budget_source":"USER_MANUAL_FINAL_INCLUDING_OIL" if manual_T is not None
                          else "OPT_IN_ILVL_REFERENCE_BASE_B"}
    if manual_T is not None:
        plan["user_manual_final_T"]=manual_T
        plan["legacy_v061_base_B"]=B
    return {"manifest":user,"context":context,"seeds":seeds,
            "flask":user["flask_F"],"paths":paths,"plan":plan}


def user_facing_result(report):
    """Expose existing v094 observations and 95%-only decisions; zero SimC."""
    need(type(report) is dict and report.get("status","").startswith("PASS")
         and report.get("official_formula")=="T=G+J+F+O",
         "NATIVE_RESULT_NOT_ACCEPTED")
    B=report["B"];T=report["official_final_T"]
    fixed=contract.vector(report["fixed_O"],"RESULT_FIXED_O")
    summary=report["alternatives"]
    confidence=report["confirmation"]
    need(type(B) is int and B>0 and T==B+sum(fixed.values())
         and summary["confidence_for_decision_and_display"]==0.95
         and summary["underlying_B"]==B
         and summary["final_T"]==T and summary["fixed_O"]==fixed,
         "RESULT_B_T_OR_CONFIDENCE_DRIFT")
    def candidate(base,final):
        b=contract.vector(base,"RESULT_BASE_TARGET")
        f=contract.vector(final,"RESULT_FINAL_TARGET")
        need(sum(b.values())==B and sum(f.values())==T
             and all(f[s]==b[s]+fixed[s] for s in contract.STATS),
             "RESULT_BASE_O_FINAL_RATING_DRIFT")
        return {"absolute_rating_T":f,
                "base_rating_B":b,
                "percent_of_final_T":{s:round(100*f[s]/T,2) for s in contract.STATS}}
    first=candidate(summary["observed_best_B"],summary["observed_best_T"])
    first.update({"observed_dps_mean":summary["observed_best_dps"],
                  "simc_sem":summary["observed_best_sem"],
                  "rank_basis":"HIGHEST_OBSERVED_MEAN_NOT_GLOBAL_OPTIMUM"})
    alternatives=[]
    for row in summary["material_alternatives"]:
        item=candidate(row["B"],row["T"])
        item.update({"observed_dps_mean":row["dps_mean"],
                     "simc_sem":row["dps_sem"],
                     "observed_dps_loss_pct":round(
                         100*row["observed_relative_dps_loss"],3),
                     "rating_moved_fraction_B":row["fraction_B_moved"],
                     "pairwise_95_label":row["label"]})
        alternatives.append(item)
    need(type(confidence["pairwise_direction_supported"]) is bool,
         "RESULT_95_PAIRWISE_STATUS_REQUIRED")
    return {"confidence_level":0.95,"official_formula":"T=G+J+F+O",
            "base_B":B,"fixed_O":fixed,"final_T":T,
            "observed_first_choice":first,
            "material_near_alternatives":alternatives,
            "observed_unique_candidates":summary["observed_unique_targets"],
            "confirmation_pair_direction_supported_at_95":
                confidence["pairwise_direction_supported"],
            "confirmation_scope":"TWO_FRESH_SELECTED_CANDIDATES_ONLY_NOT_GLOBAL",
            "global_optimum_proven":False}

def run_manifest(manifest_path,*,plan_only=False,cache_only=False,
                 physical_acceptance_root=None,open_folder=True):
    ready=source(manifest_path)
    if plan_only:return ready["plan"]
    staged=ready["manifest"].get(STAGE_FIELD) is True
    witness=None
    if staged:
        need(physical_acceptance_root is not None,
             "UNVERIFIED_PURE_PROFILE_NATIVE_EXECUTION_BLOCKED")
        witness=pure_pilot.verify(
            ready["paths"]["profile_simc"].read_text(encoding="utf8"),
            ready["plan"]["binary_sha256"],
            ready["manifest"]["native_revision"],
            ready["plan"]["class"]+"/"+ready["plan"]["spec"],
            physical_acceptance_root)
    else:
        need(physical_acceptance_root is None,
             "PURE_PHYSICAL_ACCEPTANCE_NOT_FOR_DEFAULT_PROFILES")
    user=ready["manifest"];paths=ready["paths"]
    result=durable.run(ready["context"],ready["seeds"],ready["flask"],
           paths["native_binary"],paths["output_dir"],
           scouts=user["scouts"],material_scouts=user["material_scouts"],
           step=user["step"],native_limit=user["native_limit"],
           cache_only=cache_only,cancel_file=paths["cancel_file"],
           open_folder=open_folder,
           recover_verified_partial=bool(witness))
    return {"schema":SCHEMA,"status":result["status"],
        **({"internal_pure_physical_acceptance":witness} if witness else {}),
        "result_path":str(paths["output_dir"]/"V094_RESULT.json"),
        "native_calls_cumulative":result["new_native_attempts_cumulative"],
        "cache_hits_this_run":result["verified_cache_hits_this_run"],
        "base_B":result["B"],"final_T":result["official_final_T"],
        "budget_source":ready["plan"]["budget_source"],
        "user_result":user_facing_result(result),
        "original_product_v015_v016_merged":False}

def main(argv=None):
    p=argparse.ArgumentParser(description="Source-locked CHMV scenario → existing Native solver")
    p.add_argument("--manifest",required=True)
    p.add_argument("--plan-only",action="store_true")
    p.add_argument("--cache-only",action="store_true")
    p.add_argument("--physical-acceptance-root",type=pathlib.Path,
                   help="Internal v140 exact physical acceptance reuse; staged profiles only")
    a=p.parse_args(argv)
    try:
        print(json.dumps(run_manifest(a.manifest,plan_only=a.plan_only,
                         cache_only=a.cache_only,
                         physical_acceptance_root=a.physical_acceptance_root),ensure_ascii=False,
                         sort_keys=True,indent=2))
        return 0
    except Exception as e:
        print("V096_BLOCKED:",type(e).__name__,str(e),file=sys.stderr)
        return 3
if __name__=="__main__":sys.exit(main())
