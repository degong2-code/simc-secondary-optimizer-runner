#!/usr/bin/env python3
"""Exactly two real Windows SimC static before/after calls for enchant 7967.

Use official pinned binary already downloaded in the Actions job; existing
v098 generated representative 334 profile and v198 native comparison engine.
Do not turn source-classified effect into an invented gear rating or proc.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,sys,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
sys.path.insert(0,str(ROOT/"integration_probes"))
import v106_user_session_controller as sessions
import v098_target_user_scenario_bootstrap as bootstrap
import v198_targeted_enchant_native_rating as comparison

SCHEMA="v206_one_eyes_of_eagle_nonchmv_native_rating_scope_v1"
ZERO=dict.fromkeys(("crit_rating","haste_rating","mastery_rating","versatility_rating"),0)

def require(ok,label):
    if not ok:raise RuntimeError("V206_"+label)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(binary,out):
    require(sys.platform=="win32","WINDOWS_NATIVE_ONLY")
    binary=binary.resolve()
    require(binary.name.lower()=="simc.exe" and binary.is_file(),"OFFICIAL_BINARY_REQUIRED")
    out=out.resolve();out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="v206-",dir=out) as tmp:
        folder=pathlib.Path(tmp)
        user=sessions.user_scenario(sessions.standard_controls(("paladin","retribution")))
        stage=bootstrap.build(user,folder/"generated",binary,"710c2408bf",
                              current_season_product=True)
        require(stage["native_calls"]==0 and stage["plan"]["base_B"]==3150,
                "BASELINE_PRODUCT_PLAN_DRIFT")
        base=folder/"generated"/"profile.simc"
        before_sha=digest(base)
        audit=comparison.run(base,binary,"710c2408bf","finger1",7967,
                             folder/"evidence",iterations=35,max_new=2,timeout=240)
        require(digest(base)==before_sha,"SOURCE_PROFILE_MUTATED")
        delta=audit["comparison"]["static_secondary"]
        require(delta==ZERO,"NON_CHMV_ENCHANT_ACTUALLY_CHANGES_RATING")
        require(audit["comparison"]["classification"]==
                "NO_PRECOMBAT_SECONDARY_RATING_DELTA_OBSERVED",
                "NON_CHMV_CLASSIFICATION_MISMATCH")
        require(audit["native_new_calls_this_request"]==2,"TWO_NEW_NATIVE_NOT_EXECUTED")
        require(audit["comparison"]["enchant_id"]==7967,"EXACT_EAGLE_ID_REQUIRED")
        proof={ "schema":SCHEMA,"status":"PASS_EAGLE_7967_ONE_WINDOWS_PROFILE_STATIC_E_ZERO",
          "binary_sha256":digest(binary),"source_revision":"710c2408bf",
          "scope":"paladin/retribution 334 v098 current season one ring finger1",
          "source_profile_sha256":before_sha,
          "source_quality":"pinned_simc_generated_7967_rank2",
          "native_new_calls":2,"static_CHMV_E":delta,
          "profile_before_sha256":audit["base_input_sha256"],
          "profile_after_sha256":audit["enchant_input_sha256"],
          "native_before_json2_sha256":audit["before_native_sha256"],
          "native_after_json2_sha256":audit["after_native_sha256"],
          "not_mechanics_or_DPS_proof":True,"not_general_26_specs_proof":True,
          "original_optimizer_not_rewritten":True}
        (out/"V206_EAGLE_EFFECT_STATIC_RECEIPT.json").write_text(
            json.dumps(proof,sort_keys=True,indent=2)+"\n",encoding="utf8")
        print("V206_EAGLE_EXACT_WINDOWS_TWO_NATIVE_ZERO_STATIC_RATING_PASS",json.dumps(
            {"new_native":2,"E":delta},sort_keys=True),flush=True)
        return 0

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--simc",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    a=p.parse_args()
    raise SystemExit(run(a.simc,a.out))
