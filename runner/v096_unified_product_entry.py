#!/usr/bin/env python3
"""v096 single manifest -> existing v091/093/094/095 source-locked product path.

No new solver, simulation mechanics, gear selection or Native gate.
Reference B is explicitly opt-in; exact-G and inclusive manual T remain open.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,sys
import v046_static_item_cache as item_cache
import v061_scenario_contract as contract
import v065_v015_scheduler_adapter as scheduler
import v091_weapon_oil_external_adapter as oil_adapter
import v093_inclusive_adaptive_scheduler_bridge as adaptive
import v094_durable_inclusive_adaptive_runner as durable

SCHEMA="v096_user_scenario_unified_entry_v1"
FIELDS={"schema","profile_simc","scenario_json","fillers_json",
        "static_cache_json","weapon_layout","oil_hands","flask_F",
        "seed_targets_B","native_binary","native_revision","output_dir",
        "scouts","material_scouts","native_limit","step","cancel_file"}
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
    need(type(user) is dict and set(user)==FIELDS
         and user.get("schema")==SCHEMA,"ENTRY_SCHEMA_OR_FIELDS")
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
                                 user["weapon_layout"],user["oil_hands"])
    context=adaptive.prepare(prepared,binary_sha,user["native_revision"])
    normalized=prepared["prepared"]["scenario"]
    B,lo,hi=scheduler.bounds(normalized,
                          prepared["prepared"]["static_budget"])
    need(all(scheduler.eligible(tuple(x[s] for s in contract.STATS),
                                B,lo,hi) for x in seeds)
         and seeds[0]!=seeds[1],"SEEDS_FAIL_BASE_B_L_BOUNDS")
    max_calls=normalized["scenario"]["runtime"]["max_native_calls"]
    minimum_calls=2+user["scouts"]+user["material_scouts"]+2
    need(minimum_calls<=user["native_limit"]<=max_calls,
         "SCENARIO_NATIVE_LIMIT_PRECHECK")
    need(sum(user["flask_F"].values())==normalized["budget"]["F"],
         "FLASK_F_TOTAL_MISMATCH")
    # The existing v090 reference track is a bounded, opt-in scenario path.
    # Do not silently call this proof the whole product's exact-G/manual-T route.
    need(prepared["prepared"]["static_budget"]["reference_budget_provenance"]
         ["schema"]=="v090_reference_budget_provenance_v1",
         "REFERENCE_B_ONLY_UNTIL_EXACT_G_AND_MANUAL_T_MERGE")
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
          "budget_source":"OPT_IN_ILVL_REFERENCE_BASE_B"}
    return {"manifest":user,"context":context,"seeds":seeds,
            "flask":user["flask_F"],"paths":paths,"plan":plan}

def run_manifest(manifest_path,*,plan_only=False,cache_only=False):
    ready=source(manifest_path)
    if plan_only:return ready["plan"]
    user=ready["manifest"];paths=ready["paths"]
    result=durable.run(ready["context"],ready["seeds"],ready["flask"],
           paths["native_binary"],paths["output_dir"],
           scouts=user["scouts"],material_scouts=user["material_scouts"],
           step=user["step"],native_limit=user["native_limit"],
           cache_only=cache_only,cancel_file=paths["cancel_file"],
           open_folder=True)
    return {"schema":SCHEMA,"status":result["status"],
        "result_path":str(paths["output_dir"]/"V094_RESULT.json"),
        "native_calls_cumulative":result["new_native_attempts_cumulative"],
        "cache_hits_this_run":result["verified_cache_hits_this_run"],
        "base_B":result["B"],"final_T":result["official_final_T"],
        "original_product_v015_v016_merged":False}

def main(argv=None):
    p=argparse.ArgumentParser(description="Source-locked CHMV scenario → existing Native solver")
    p.add_argument("--manifest",required=True)
    p.add_argument("--plan-only",action="store_true")
    p.add_argument("--cache-only",action="store_true")
    a=p.parse_args(argv)
    try:
        print(json.dumps(run_manifest(a.manifest,plan_only=a.plan_only,
                         cache_only=a.cache_only),ensure_ascii=False,
                         sort_keys=True,indent=2))
        return 0
    except Exception as e:
        print("V096_BLOCKED:",type(e).__name__,str(e),file=sys.stderr)
        return 3
if __name__=="__main__":sys.exit(main())
