#!/usr/bin/env python3
"""One exact Linux Frost334 + ring8025 session: six SimC max, then cache-only."""
import hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v106_user_session_controller as sessions
import v098_target_user_scenario_bootstrap as bootstrap
import v096_unified_product_entry as entry

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main(binary,root):
    root.mkdir(parents=True,exist_ok=True)
    u=sessions.user_scenario(sessions.standard_controls(("mage","frost")))
    assert "verified_enchant" not in u
    u["verified_enchant"]={"finger1":8025}
    p=bootstrap.build(u,root/"candidate",binary,"710c2408bf",
                      current_season_product=True)
    manifest=pathlib.Path(p["generated_manifest"])
    plan=entry.source(manifest)
    assert plan["plan"]["base_B"]==3150
    assert plan["plan"]["final_T"]==3182
    assert plan["context"]["identity"]["v202_verified_enchant"]["fixed_E"]["haste_rating"]==30
    first=entry.run_manifest(manifest,open_folder=False)
    result=json.loads(pathlib.Path(first["result_path"]).read_text())
    assert first["status"]=="PASS_BOUNDED_GENERIC_NATIVE_SEARCH_AND_CACHE"
    assert first["native_calls_cumulative"]==6
    assert first["cache_hits_this_run"]==0
    assert first["user_result"]["confidence_level"]==0.95
    assert first["user_result"]["global_optimum_proven"] is False
    assert result["official_formula"]=="T=G+J+F+O"
    assert result["B"]==3150 and result["official_final_T"]==3182
    assert len(result["observations"])==6
    out=manifest.parent/"simc_results"
    native={str(f.relative_to(out)):digest(f) for f in out.rglob("result.json")}
    assert len(native)==6
    for obs in result["observations"]:
        assert obs["base_B"]["haste_rating"]>=30
        assert obs["final_T"]["haste_rating"]>=46
    second=entry.run_manifest(manifest,cache_only=True,open_folder=False)
    again={str(f.relative_to(out)):digest(f) for f in out.rglob("result.json")}
    assert native==again
    assert second["cache_hits_this_run"]==6
    assert second["native_calls_cumulative"]==6
    assert second["user_result"]==first["user_result"]
    receipt={"schema":"v203_exact_one_ring_full_adaptive_cache_v1",
       "status":"PASS_SIX_NATIVE_THEN_SIX_VERIFIED_CACHE_HITS_ZERO_NEW_NATIVE",
       "scope":"mage/frost ilvl334 finger1 item158366 enchant8025",
       "binary_sha256":digest(binary),"source_profile_sha256":plan["context"]["identity"]["source_profile_sha256"],
       "proof_sha256":plan["context"]["identity"]["v202_verified_enchant"]["evidence_sha256"],
       "fixed_E":{"crit_rating":0,"haste_rating":30,"mastery_rating":0,"versatility_rating":0},
       "B":result["B"],"T":result["official_final_T"],
       "first_native_calls":6,"cache_replay_native_calls":0,"verified_hits":6,
       "native_output_sha256":native,"rating_floor_enforced":True,
       "global_optimum_proven":False,"confidence_level":0.95,
       "case_keys":[x["case_key"] for x in result["observations"]]}
    (root/"audit_receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print("V203_FULL_SIX_NATIVE_AND_CACHE_ONLY_REPLAY_PASS",json.dumps(
          {"B":result["B"],"T":result["official_final_T"],"Native":6,
           "cache_hits":6,"unique_ratings":first["user_result"]["observed_unique_candidates"]}),flush=True)
if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("exactly binary and output root required")
    main(pathlib.Path(sys.argv[1]).resolve(),pathlib.Path(sys.argv[2]).resolve())
