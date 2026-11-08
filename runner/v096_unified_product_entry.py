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
import v204_selected_enchant_reference_budget as enchant_reference
import v206_nonchmv_eagle_selection as nonchmv_enchant

SCHEMA="v096_user_scenario_unified_entry_v1"
FIELDS={"schema","profile_simc","scenario_json","fillers_json",
        "static_cache_json","weapon_layout","oil_hands","flask_F",
        "seed_targets_B","native_binary","native_revision","output_dir",
        "scouts","material_scouts","native_limit","step","cancel_file"}
MANUAL_FIELD="manual_final_T"
NATIVE_ENCHANT_FIELD="v202_verified_enchant_choice"
NONCHMV_ENCHANT_FIELD="v206_source_classified_nonchmv_enchant_choice"
SEASON_FIELD="admitted_season_budget_source"
SEASON_SCHEMA="v096_internal_admitted_season_budget_source_v1"
FRESH_SEASON_FIELD="installed_fresh_season_budget_source"
FRESH_SEASON_SCHEMA="v096_internal_installed_fresh_v212_source_v1"
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


def _admitted_season_source(*, manifest_path, season, revision,
                            user_scenario, flask_F, oil_hands):
    """Reuse v216's exact already-sealed v223-backed budget receipt.

    Internal season package path only. v222 labels or numeric preview alone
    never authorize a session. The v216-v223 source provenance remains the
    authority; this is the original v096 execution adapter, not a new effect
    or separate season certification engine.
    """
    need(type(season) is dict and
         set(season)=={
             "schema","environment_receipt_path",
             "environment_receipt_sha256","oil_by_hand"}
         and season["schema"]==SEASON_SCHEMA,
         "SEASON_BUDGET_INTERNAL_SOURCE_FIELDS")
    receipt_path=path_for(pathlib.Path(manifest_path).parent,
                          season["environment_receipt_path"])
    need(not receipt_path.is_symlink(),
         "SEASON_ENVIRONMENT_RECEIPT_SYMLINK_BLOCKED")
    import v216_environment_build_coordinator as environment
    try:
        receipt=environment.read_receipt(receipt_path)
    except (OSError,ValueError,KeyError,TypeError) as exc:
        raise EntryBlocked("SEASON_V216_EXISTING_RECEIPT_INVALID:"+
                           type(exc).__name__) from exc
    need(receipt.get("receipt_sha256")==season["environment_receipt_sha256"],
         "SEASON_ENVIRONMENT_RECEIPT_IDENTITY_MISMATCH")
    b=receipt.get("season_budget",{})
    src=receipt.get("source",{})
    need(type(b) is dict and type(src) is dict
         and b.get("source_links_verified_by_v223") is True
         and b.get("source_authentication_performed_here") is False
         and type(b.get("source_input_sha256")) is dict
         and all(type(v) is str and contract.HASH_RE.fullmatch(v) is not None
                 for v in b["source_input_sha256"].values())
         and set(b["source_input_sha256"])=={
             "gear","tier","budget","reference"}
         and b.get("source_catalog_manifest_sha256")==
             src.get("manifest_sha256")
         and b.get("source_catalog_artifact_sha256")==
             src.get("artifact_sha256")
         and b.get("game_build")==src.get("game_build")
         and b.get("simc_revision")==revision==
             src.get("simc_revision"),
         "SEASON_V223_ACTUAL_SOURCE_LINKS_NOT_VERIFIED")
    normalized=contract.normalize(user_scenario)
    budget=normalized["budget"]
    final=b.get("base_B")
    oil=b.get("fixed_O")
    need(type(final) is int and final>0 and
         type(oil) is dict and
         b.get("final_T")==final+sum(oil.values())
         and b.get("target_ilevel")==normalized["scenario"]["target"]["ilevel"]
         and normalized["scenario"]["target"]["mode"]=="manual_total"
         and normalized["scenario"]["target"]["manual_total"]==final
         and budget["T"]==final and budget["J"]==b.get("J")
         and budget["F"]==b.get("F")
         and budget["external_temporary_rating"] in (
             oil,{stat:0 for stat in contract.STATS})
         and sum(flask_F.values())==b.get("F")
         and all(b.get(k)=={stat:0 for stat in contract.STATS}
                 for k in ("fixed_L","fixed_E")),
         "SEASON_V222_TYPED_GJFO_B_T_F_O_DRIFT")
    by_hand=season["oil_by_hand"]
    need(type(by_hand) is dict and set(by_hand)==set(oil_hands)
         and all(type(v) is dict
                 and set(v)=={
                     "physical_item_id","simc_input_token",
                     "static_CHMV_vector"}
                 and type(v["physical_item_id"]) is int
                 and v["physical_item_id"]>0
                 for v in by_hand.values()),
         "SEASON_SELECTED_PHYSICAL_OIL_HANDS_DRIFT")
    exact_o={stat:0 for stat in contract.STATS}
    for hand,info in by_hand.items():
        vector=contract.vector(
            info["static_CHMV_vector"],"SEASON_V223_FIXED_O")
        for stat in contract.STATS:
            exact_o[stat]+=vector[stat]
    need(exact_o==oil,
         "SEASON_V223_PHYSICAL_OIL_STATIC_VECTOR_DRIFT")
    # Distinguish same-B profiles from different seasons and sources in
    # v093/v094 durable case keys. Do not invalidate old legacy identities.
    source_identity=hashlib.sha256(json.dumps(
        b["source_input_sha256"],sort_keys=True,
        separators=(",",":")).encode("utf8")).hexdigest()
    return {"season_budget":b,
            "season_source_identity":{
                "environment_build_receipt_sha256":receipt["receipt_sha256"],
                "environment_manifest_sha256":
                    receipt["environment_manifest_sha256"],
                "source_catalog_artifact_sha256":
                    src["artifact_sha256"],
                "source_input_sha256":source_identity},
            "oil_by_hand":by_hand}


def _admitted_fresh_season_source(*, manifest_path, season, revision,
                                  user_scenario, flask_F, oil_hands, profile):
    """Reuse ORIGINAL exact-build v216/v217/v212 installed source, never a preview.

    The caller does not authenticate source data or SimC effects. The existing
    v216 reusable installer lookup rechecks catalog bytes, stage hashes and
    both v217 stage receipts before any v094 runtime source is prepared.
    This first bridge supports the proven O=0 base; physical oils stay pending.
    """
    need(type(season) is dict and set(season)=={
        "schema","installed_environment_path","installed_manifest_sha256",
        "oil_by_hand"} and season["schema"]==FRESH_SEASON_SCHEMA,
        "FRESH_SEASON_INTERNAL_SOURCE_FIELDS")
    path=path_for(pathlib.Path(manifest_path).parent,
                  season["installed_environment_path"])
    need(not path.is_symlink() and path.is_file() and len(path.parents)>=4
         and path.parent.name=="fresh_source"
         and path.parents[2].name=="_fresh_season_sources"
         and path.name.startswith("v212_installed_"),
         "FRESH_SEASON_INSTALLED_PATH_REQUIRED")
    import v212_environment_manifest as installed_manifest
    import v216_environment_build_coordinator as environment
    try:
        doc,_=installed_manifest.read_json(path,environment.MAX_RECEIPT_BYTES)
        installed_manifest.verify_fresh_installed_environment(doc)
        need(path.parent.parent.name=="wago_"+doc["game_build"] and
             path.name=="v212_installed_"+doc["manifest_sha256"][:20]+".json"
             and season["installed_manifest_sha256"]==doc["manifest_sha256"],
             "FRESH_SEASON_INSTALLED_MANIFEST_IDENTITY_DRIFT")
        bound=environment.find_verified_installed_season_environment(
            path.parents[3],doc["target_ilevel"],
            expected_game_build=doc["game_build"])
    except (OSError,ValueError,TypeError,KeyError) as exc:
        if isinstance(exc,EntryBlocked):
            raise
        raise EntryBlocked("FRESH_SEASON_ORIGINAL_V217_V212_VERIFICATION_FAILED:"
                           +type(exc).__name__) from exc
    need(type(bound) is dict and bound.get("environment_ready") is True
         and bound.get("environment_installed") is True
         and bound.get("installed_manifest_sha256")==doc["manifest_sha256"],
         "FRESH_SEASON_V217_INSTALLED_PROOF_NOT_FOUND")
    normalized=contract.normalize(user_scenario)
    oil=doc["official_O"]
    zeros={stat:0 for stat in contract.STATS}
    physical_f=doc.get("official_F_physical_source")
    need(type(physical_f) is dict
         and physical_f.get("static_CHMV_vector")==flask_F
         and physical_f.get("F_rating")==doc["official_F"]
         and type(physical_f.get("simc_input_token")) is str
         and ("flask="+physical_f["simc_input_token"]) in
             profile.splitlines(),
         "FRESH_SEASON_SELECTED_PHYSICAL_F_PROFILE_DRIFT")
    need(season["oil_by_hand"]=={} and oil_hands==[] and oil==zeros
         and normalized["scenario"]["target"]["mode"]=="manual_total"
         and normalized["scenario"]["target"]["ilevel"]==
             doc["target_ilevel"]
         and normalized["scenario"]["target"]["manual_total"]==
             doc["official_B"]
         and normalized["budget"]["T"]==doc["official_B"]
         and normalized["budget"]["J"]==doc["official_J"]
         and normalized["budget"]["F"]==doc["official_F"]
         and normalized["budget"]["external_temporary_rating"]==zeros
         and doc["official_B"]+sum(oil.values())==doc["official_T"],
         "FRESH_SEASON_TYPED_GJFO_B_T_O_DRIFT")
    # Preserve v093/v094's exact durable session/cache identity shape.
    # The fresh installed v212 SHA occupies the former v216 receipt slot;
    # include the authenticated v217 stage receipt in source_input_sha256.
    identity={
        "environment_build_receipt_sha256":doc["manifest_sha256"],
        "environment_manifest_sha256":doc["manifest_sha256"],
        "source_catalog_artifact_sha256":
            doc["source_catalog_artifact_sha256"],
        "source_input_sha256":hashlib.sha256(json.dumps({
            "original_budget_source_identities":
                doc["trusted_budget_component_source_identities"],
            "original_v217_installed_stage_receipt_sha256":
                bound["stage_receipt_sha256"]},
            sort_keys=True,separators=(",",":")).encode("utf8")).hexdigest()}
    budget={"game_build":doc["game_build"],
            "simc_revision":doc["simc_revision"],
            "target_ilevel":doc["target_ilevel"],
            "base_B":doc["official_B"],"final_T":doc["official_T"],
            "fixed_O":dict(oil),"J":doc["official_J"],"F":doc["official_F"],
            "source_catalog_manifest_sha256":
                doc["source_catalog_manifest_sha256"],
            "source_catalog_artifact_sha256":
                doc["source_catalog_artifact_sha256"]}
    return {"season_budget":budget,"season_source_identity":identity,
            "oil_by_hand":{},"fresh_v212_installed":True}


def source(manifest_path):
    """Build the existing typed and SHA-locked Native context; zero SimC calls."""
    manifest_path=pathlib.Path(manifest_path).resolve()
    user=read_object(manifest_path)
    base_allowed=(FIELDS,FIELDS|{MANUAL_FIELD},FIELDS|{STAGE_FIELD},
                  FIELDS|{MANUAL_FIELD,STAGE_FIELD})
    allowed=(base_allowed+
             tuple(x|{NATIVE_ENCHANT_FIELD} for x in base_allowed)+
             tuple(x|{NONCHMV_ENCHANT_FIELD} for x in base_allowed)+
             tuple(x|{SEASON_FIELD} for x in (FIELDS,))+
             tuple(x|{FRESH_SEASON_FIELD} for x in (FIELDS,)))
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
    selected_fixed_E=(verified_enchant.read()[0]["static_enchant_E"]
                      if NATIVE_ENCHANT_FIELD in user else None)
    season_source=(
        _admitted_season_source(
            manifest_path=manifest_path,season=user[SEASON_FIELD],
            revision=user["native_revision"],user_scenario=doc,
            flask_F=user["flask_F"],oil_hands=user["oil_hands"])
        if SEASON_FIELD in user else
        _admitted_fresh_season_source(
            manifest_path=manifest_path,season=user[FRESH_SEASON_FIELD],
            revision=user["native_revision"],user_scenario=doc,
            flask_F=user["flask_F"],oil_hands=user["oil_hands"],
            profile=profile)
        if FRESH_SEASON_FIELD in user else None)
    prepared=oil_adapter.prepare(
        profile,doc,fillers,cache,
        user["weapon_layout"],user["oil_hands"],
        manual_final_T=manual_T,
        verified_enchant_E=selected_fixed_E,
        season_oil_by_hand=(
            season_source["oil_by_hand"] if season_source else None),
        season_base_B=(
            season_source["season_budget"]["base_B"]
            if season_source else None))
    if season_source is not None:
        need(prepared["approved_total"]["base_B"]==
                 season_source["season_budget"]["base_B"]
             and prepared["approved_total"]["final_T"]==
                 season_source["season_budget"]["final_T"]
             and prepared["oil"]["declared_O"]==
                 season_source["season_budget"]["fixed_O"],
             "SEASON_PHYSICAL_OIL_AND_V092_TOTAL_DRIFT")
        prepared["admitted_season_environment_identity"]=(
            season_source["season_source_identity"])
    if NONCHMV_ENCHANT_FIELD in user:
        # Source and exact Windows E=0 comparison have separate provenance;
        # neither creates new B/T nor certifies effect mechanics in every spec.
        approved_nonchmv=nonchmv_enchant.admit(
            user[NONCHMV_ENCHANT_FIELD],prepared["oil"]["profile"],
            prepared["prepared"]["scenario"])
    else:
        approved_nonchmv=None
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
    if season_source is not None:
        need(provenance["source"]=="user_manual_total"
             and provenance["total_T"]==
                 season_source["season_budget"]["base_B"]
             and context["identity"]["approved_final_T"]==
                 season_source["season_budget"]["final_T"]
             and context["identity"].get(
                 "admitted_season_environment_identity")==
                 season_source["season_source_identity"],
             "SEASON_ADMITTED_V090_V093_SOURCE_DRIFT")
    elif manual_T is None:
        need(provenance["source"]=="reference_rounded_opt_in",
             "REFERENCE_B_ONLY_UNTIL_EXACT_G_MERGE")
        if NATIVE_ENCHANT_FIELD in user:
            need(provenance.get(enchant_reference.KEY,{}).get("additional_B")
                 ==sum(selected_fixed_E.values()),
                 "VERIFIED_ENCHANT_REFERENCE_ADDITION_MISSING")
    else:
        need(provenance["source"]=="user_manual_total"
             and provenance["budget_entry_mode"]=="USER_MANUAL_FINAL_T_CONVERTED_TO_B"
             and context["identity"]["approved_final_T"]==manual_T
             and enchant_reference.KEY not in provenance,
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
          "budget_source":("ADMITTED_FRESH_SEASON_GJFO_V212_V217"
                          if season_source.get("fresh_v212_installed") else
                          "ADMITTED_SEASON_GJFO_V216_V223") if season_source
                          else "USER_MANUAL_FINAL_INCLUDING_OIL" if manual_T is not None
                          else ("OPT_IN_ILVL_REFERENCE_PLUS_VERIFIED_FIXED_E"
                                if NATIVE_ENCHANT_FIELD in user
                                else "OPT_IN_ILVL_REFERENCE_BASE_B")}
    if season_source is not None:
        plan["season_source_receipt_sha256"]=(
            season_source["season_source_identity"][
                "environment_build_receipt_sha256"])
        if season_source.get("fresh_v212_installed"):
            plan["source_links_verified_by_v217_v212"]=True
        else:
            plan["source_links_verified_by_v223"]=True
        plan["season_source_same_game_build"]=(
            season_source["season_budget"]["game_build"])
        plan["season_gjfo_source_is_NOT_policy_A_coverage"]=True
    if approved_nonchmv is not None:
        need(enchant_reference.KEY not in provenance,
             "NONCHMV_EFFECT_MUST_NOT_ADD_REFERENCE_B")
        plan["selected_nonchmv_enchant"]=approved_nonchmv
    if NATIVE_ENCHANT_FIELD in user:
        plan["selected_fixed_enchant_E"]=dict(selected_fixed_E)
        plan["selected_enchant_budget_policy"]=(
            "MANUAL_FINAL_T_UNCHANGED_FIXED_E" if manual_T is not None
            else "DERIVED_REFERENCE_B_PLUS_E_ONCE")
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
