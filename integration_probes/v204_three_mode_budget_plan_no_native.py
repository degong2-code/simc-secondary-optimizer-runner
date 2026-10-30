#!/usr/bin/env python3
"""v204 no-Native paired plan: none, selected automatic, selected manual final T.

Use exact cached v203 Linux binary only to bind identity; never invoke SimC.
"""
import json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v106_user_session_controller as sessions
import v098_target_user_scenario_bootstrap as bootstrap
import v096_unified_product_entry as entry
import v204_selected_enchant_reference_budget as adjustment

def make(binary,root,kind):
    controls=sessions.standard_controls(("mage","frost"))
    user=sessions.user_scenario(controls)
    if kind!="absent":
        user["verified_enchant"]={"finger1":8025}
    if kind=="manual":
        user["target"]["final_T"]=3182
    elif kind not in ("absent","auto"):
        raise ValueError("UNKNOWN_CASE")
    staged=bootstrap.build(user,root/kind,binary,"710c2408bf",
                           current_season_product=True)
    manifest=pathlib.Path(staged["generated_manifest"])
    plan=entry.run_manifest(manifest,plan_only=True)
    assert staged["native_calls"]==0 and plan["native_called"] is False
    assert not (manifest.parent/"simc_results").exists()
    return plan,entry.source(manifest)["context"]["identity"]

def main(binary,folder):
    binary=binary.resolve()
    folder.mkdir(parents=True,exist_ok=True)
    none,none_id=make(binary,folder,"absent")
    auto,auto_id=make(binary,folder,"auto")
    manual,manual_id=make(binary,folder,"manual")
    assert (none["base_B"],none["final_T"])==(3150,3182)
    assert (auto["base_B"],auto["final_T"])==(3180,3212)
    assert (manual["base_B"],manual["final_T"])==(3150,3182)
    assert none["budget_source"]=="OPT_IN_ILVL_REFERENCE_BASE_B"
    assert auto["budget_source"]=="OPT_IN_ILVL_REFERENCE_PLUS_VERIFIED_FIXED_E"
    assert manual["budget_source"]=="USER_MANUAL_FINAL_INCLUDING_OIL"
    assert auto["selected_enchant_budget_policy"]=="DERIVED_REFERENCE_B_PLUS_E_ONCE"
    assert manual["selected_enchant_budget_policy"]=="MANUAL_FINAL_T_UNCHANGED_FIXED_E"
    assert "selected_fixed_enchant_E" not in none
    assert auto["selected_fixed_enchant_E"]==manual["selected_fixed_enchant_E"]=={
        "crit_rating":0,"haste_rating":30,
        "mastery_rating":0,"versatility_rating":0}
    assert none_id["source_profile_sha256"]!=auto_id["source_profile_sha256"]
    assert auto_id["source_profile_sha256"]==manual_id["source_profile_sha256"]
    assert len({none_id["scenario_digest"],auto_id["scenario_digest"],
                manual_id["scenario_digest"]})==3
    assert all("v202_verified_enchant" not in i for i in [none_id])
    assert "v202_verified_enchant" in auto_id and "v202_verified_enchant" in manual_id
    assert "v204_selected_verified_enchant_reference_addition_v1" not in none_id
    assert manual_id["approved_final_T"]==none_id["approved_final_T"]==3182
    assert auto_id["approved_final_T"]==3212
    report={"schema":"v204_three_modes_real_full_profile_plan_no_native_v1",
      "status":"PASS_ABSENT_AUTO_MANUAL_SCOPE_AND_B_T_PROOF",
      "absent":{"B":none["base_B"],"T":none["final_T"]},
      "auto":{"B":auto["base_B"],"T":auto["final_T"]},
      "manual":{"B":manual["base_B"],"T":manual["final_T"]},
      "source_profile_selected_is_same_auto_and_manual":True,
      "three_distinct_scenario_digests":True,
      "fresh_native_calls":0}
    (folder/"plan_receipt.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("V204_THREE_MODE_REAL_PROFILE_PLAN_NO_NATIVE_PASS",json.dumps(report,sort_keys=True),flush=True)

if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("python v204...py <binary> <output-dir>")
    main(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))
