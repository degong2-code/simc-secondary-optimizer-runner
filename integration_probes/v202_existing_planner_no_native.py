#!/usr/bin/env python3
"""One developer-only opt-in end-to-end stage/plan, no SimC invocation."""
import copy,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v106_user_session_controller as user
import v098_target_user_scenario_bootstrap as bootstrap
import v096_unified_product_entry as entry
import v093_inclusive_adaptive_scheduler_bridge as adaptive
import v065_v015_scheduler_adapter as scheduler

def check(binary,out):
    original=user.user_scenario(user.standard_controls(("mage","frost")))
    selected=copy.deepcopy(original)
    selected["verified_enchant"]={"finger1":8025}
    base=bootstrap.build(original,out/"base",binary,"710c2408bf",
                         current_season_product=True)
    tested=bootstrap.build(selected,out/"proved",binary,"710c2408bf",
                           current_season_product=True)
    a=entry.source(base["generated_manifest"])
    b=entry.source(tested["generated_manifest"])
    proof=b["context"]["identity"]["v202_verified_enchant"]
    assert "v202_verified_enchant" not in a["context"]["identity"]
    assert proof["fixed_E"]=={"crit_rating":0,"haste_rating":30,
         "mastery_rating":0,"versatility_rating":0}
    assert a["plan"]["base_B"]==b["plan"]["base_B"]
    assert a["plan"]["final_T"]==b["plan"]["final_T"]
    old=adaptive.feasible_budget(a["context"],a["flask"])
    new=adaptive.feasible_budget(b["context"],b["flask"])
    B,low,high=scheduler.bounds(b["context"]["bundle"]["prepared"]["scenario"],new)
    assert new["fixed_enchant_E_in_G_only"]["haste_rating"]==30
    assert B==a["plan"]["base_B"]
    target=b["seeds"][0]
    proposed=adaptive.request(b["context"],target,b["flask"],out/"one.json")
    original_req=adaptive.request(a["context"],target,a["flask"],out/"zero.json")
    assert proposed["raw_gear_override"]==original_req["raw_gear_override"]
    assert proposed["target"]==original_req["target"]
    assert "enchant_id=8025" in proposed["input"]
    assert "enchant_id=8025" not in original_req["input"]
    assert proposed["case_key"]!=original_req["case_key"]
    assert proposed["v093_session_digest"]!=original_req["v093_session_digest"]
    print(json.dumps({"status":"V202_NATIVE_ZERO_END_TO_END_PLAN_PASS",
        "B":B,"enchant_E":proof["fixed_E"],
        "base_floor":old["effective_floor_if_possible"],
        "enchant_floor":new["effective_floor_if_possible"],
        "new_native":0},sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("usage: <simc-binary> <test-output-dir>")
    check(pathlib.Path(sys.argv[1]).resolve(),pathlib.Path(sys.argv[2]).resolve())
