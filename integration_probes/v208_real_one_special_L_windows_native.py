#!/usr/bin/env python3
"""v208 one Windows official SimC user-selected special-L hydration check.

One current-season source-listed neck special, 1 real physical Native maximum,
then exact cached v098/v096 plan (no DPS Native). Other special items/26 specs
are outside this audit.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v106_user_session_controller as session
import v208_internal_exact_special_L_hydrator as hydrator
import v098_target_user_scenario_bootstrap as bootstrap
import v046_static_item_cache as cache
import v062_static_budget_bridge as budget
import v167_product_season_gear_adapter as gear_db

def need(ok,why):
    if not ok:raise RuntimeError("V208_NATIVE_"+why)

def run(binary,out):
    binary=binary.resolve();out=out.resolve();out.mkdir(parents=True,exist_ok=True)
    need(sys.platform=="win32","REAL_WINDOWS_ONLY")
    need(binary.is_file() and binary.name.lower()=="simc.exe","EXACT_BINARY")
    need(hydrator.sha_file(binary)=="0ad16368cd1effb19c793dbce63518ccb72fec89c72f6ef75d9afca239a039e8",
         "OFFICIAL_EXE_SHA_CHANGED")
    found=[x for x in gear_db.read()["items"] if x["item_id"]==268250]
    need(len(found)==1 and
         found[0]["category"]=="special_effect_gear_candidate" and
         found[0]["slot_hint"]=="neck",
         "SOURCE_SEASON_NECK_NOT_VERIFIED")
    c=session.standard_controls(("shaman","elemental"))
    c["ilevel"]=331
    c["special_items"]=[{"slot":"neck","item_id":268250,"options":{}}]
    user=session.user_scenario(c)
    result=hydrator.hydrate(user,out/"runs",binary,"710c2408bf")
    need(result["native_new_calls"]==1 and
         result["observed_selected_variants"]==1,
         "ONE_EXACT_STATIC_NATIVE_REQUIRED")
    path=pathlib.Path(result["static_cache_path"])
    cache_data=cache.load(path)
    # The exact internal v098 selected row may include source-verified
    # item options even when the user-facing selector is only an ID.
    staged=bootstrap.build(user,out/"pure-source-no-write",binary,"710c2408bf",
                           current_season_product=True,
                           static_special_probe_only=True)
    need(len(staged["special_rows"])==1 and
         staged["special_rows"][0]["item_id"]==268250,
         "INTERNAL_EXACT_SELECTED_NECK_ID_CHANGED")
    actual=budget.exact_identity(staged["special_rows"][0])
    record=cache_data["variants"].get(cache.digest(actual))
    need(record is not None and
         record["source_kind"]=="NATIVE_JSON2_RESOLVED_VARIANT" and
         record["metadata"]["native_json_sha256"]==result["native_json2_sha256"],
         "EXACT_NATIVE_VARIANT_NOT_CACHED")
    stage=bootstrap.build(user,out/"planned",binary,"710c2408bf",path,
                          current_season_product=True)
    need(stage["native_calls"]==0 and
         stage["plan"]["final_T"]==3182 and
         stage["plan"]["base_B"]==3150,
         "PLAN_AFTER_STATIC_L_NOT_APPROVED")
    need(hydrator.source_cache(out/"runs",None)==path,
         "LATEST_POINTER_NOT_AT_NEW_SNAPSHOT")
    rehydrated=hydrator.hydrate(user,out/"runs",binary,"710c2408bf",
                                existing=path)
    need(rehydrated["native_new_calls"]==0 and
         rehydrated["static_cache_path"]==str(path),
         "SECOND_STATIC_NATIVE_MUST_NOT_REEXECUTE")
    receipt={"schema":"v208_real_windows_one_selected_static_L_v1",
        "status":"PASS_EXACT_ONE_NATIVE_SPECIAL_L_INTERNAL_AND_REUSED",
        "scope":"shaman/elemental 331 special neck item268250 no options",
        "source_gear_category":"special_effect_gear_candidate",
        "actual_native_variant_identity":actual,
        "source_profile_sha256":staged["source_profile_sha256"],
        "binary_sha256":hydrator.sha_file(binary),"revision":"710c2408bf",
        "native_json2_sha256":result["native_json2_sha256"],
        "observed_static_L":record["static"]["secondary"],
        "new_static_native_calls":1,"cache_replay_static_native_calls":0,
        "post_static_plan_native_calls":0,
        "B":3150,"T":3182,
        "old_preexisting_cache_mutated":False,
        "dps_optimization_native_run":False,
        "not_general_all_special_items_proof":True}
    (out/"V208_REAL_ONE_L_RECEIPT.json").write_text(
        json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print("V208_WINDOWS_EXACT_L_ONE_NATIVE_ONE_CACHE_PASS",json.dumps(
        {"L":receipt["observed_static_L"],"B":3150,"T":3182},sort_keys=True),
        flush=True)
    return 0

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--simc",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    args=p.parse_args()
    raise SystemExit(run(args.simc,args.out))
