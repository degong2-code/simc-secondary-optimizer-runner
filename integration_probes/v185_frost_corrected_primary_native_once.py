#!/usr/bin/env python3
"""v185: ONE frost-mage ilvl 334 corrected primary-weapon, six candidate Native.

Reuses approved v106 -> v098 -> v094; no new optimizer, item effects or budget
logic. One bounded session in GitHub Actions; original outputs retained.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,sys,traceback

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
import v106_user_session_controller as session
import v098_target_user_scenario_bootstrap as bootstrap
import v169_source_first_representative_stage as representative

SCHEMA="v185_corrected_frost_334_one_native_session_v1"
REV="7bc10711b5"
BINARY_SHA="64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e"
REQUIRED_TIER={"head":271564,"shoulders":271562,
               "hands":271565,"legs":271563}
EXPECTED_WEAPONS={"main_hand":159137,"off_hand":159667}
EXPECTED_POLICY="v184_db2_primary_with_hybrid_71_74_v1"

def check(condition,why):
    if not condition:raise RuntimeError("V185_"+why)
def save(path,obj):
    path.write_text(json.dumps(obj,sort_keys=True,indent=2,
                       ensure_ascii=False)+"\n",encoding="utf8")
def item_id_from_profile(profile,slot):
    lines=[line for line in profile.splitlines()
           if line.startswith(slot+"=")]
    check(len(lines)==1,"PROFILE_SLOT_MISSING_OR_DUPLICATE_"+slot)
    marker=",id="
    value=lines[0]
    check(marker in value,"PROFILE_NO_ID_"+slot)
    return int(value.split(marker,1)[1].split(",",1)[0])
def json2_items_from_real_outputs(folder):
    root=folder/"generated"/"simc_results"
    paths=sorted(root.rglob("result.json"))
    # Exact existing v094 layout, with 2 seeds, 1 scout, 1 material and
    # 2 confirmations; also validate every Native case actually exists.
    check(len(paths)==6,"EXACT_SIX_NATIVE_JSON2_OUTPUTS_REQUIRED")
    summary=[]
    for path in paths:
        doc=json.loads(path.read_text(encoding="utf8"))
        check(doc.get("git_revision")==REV,
              "JSON2_NATIVE_REVISION_MISMATCH")
        players=doc.get("sim",{}).get("players",[])
        check(len(players)==1,"JSON2_EXACT_SINGLE_PLAYER_REQUIRED")
        player=players[0]
        gear=player.get("gear",{})
        check(type(gear) is dict,"JSON2_GEAR_MISSING")
        for slot,iid in {**REQUIRED_TIER,**EXPECTED_WEAPONS}.items():
            actual=gear.get(slot,{})
            check(type(actual) is dict and
                  ",id="+str(iid)+"," in
                  str(actual.get("encoded_item",""))+",",
                  "JSON2_ITEM_ID_MISMATCH_"+slot)
        main=gear["main_hand"]
        check(main.get("intellect",0)>0 and
              main.get("agility",0)==0 and main.get("strength",0)==0,
              "JSON2_MAGE_MAIN_WEAPON_NOT_INTELLECT")
        summary.append({"path":str(path.relative_to(folder)),
                        "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                        "main_hand_intellect":main["intellect"],
                        "weapon_ids":dict(EXPECTED_WEAPONS),
                        "tier_ids":dict(REQUIRED_TIER)})
    return summary

def run(binary,out):
    binary=pathlib.Path(binary).resolve()
    check(binary.is_file(),"SIMC_BINARY_MISSING")
    check(hashlib.sha256(binary.read_bytes()).hexdigest()==BINARY_SHA,
          "PINNED_SIMC_SHA_MISMATCH")
    check(representative.WEAPON_SELECTION_POLICY==EXPECTED_POLICY,
          "WEAPON_SELECTION_POLICY_DRIFT")
    out=pathlib.Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    report={"schema":SCHEMA,"status":"IN_PROGRESS",
            "spec":"mage/frost","target_ilevel":334,
            "simc_revision":REV,"binary_sha256":BINARY_SHA,
            "native_limit":6,"new_native_calls_confirmed":0,
            "cache_only_new_native_calls":0}
    report_path=out/"V185_FROST_PRIMARY_RETEST_SUMMARY.json"
    save(report_path,report)
    try:
        controls=session.standard_controls(("mage","frost"))
        controls["ilevel"]=334
        u=session.user_scenario(controls)
        check(u["target"]=={"ilevel":334,"final_T":None},"TARGET_DRIFT")
        folder=session.store_session(u,out,binary,REV,
                                     current_season_product=True)
        report["session_id"]=folder.name
        report["session_folder"]=str(folder)
        report["default_controls"]={
             "trinket_ids":[x["item_id"] for x in u["trinkets"]],
             "oil_hands":u["oil_hands"],"combat":u["combat"],
             "consumable_choices":u.get("consumable_choices")}
        identity=json.loads((folder/"V106_SESSION_IDENTITY.json").read_text())
        check(identity.get("current_season_weapon_selection_policy")==
              EXPECTED_POLICY,"CORRECTED_SESSION_POLICY_MISSING")
        # Plan only: prove actual new input and class-specific tier BEFORE
        # authorizing any Native call. Do not substitute a previous input.
        plan=bootstrap.run(folder/"user.json",folder/"generated",binary,REV,
                           current_season_product=True,execute=False)
        check(plan["native_calls"]==0,"PLAN_MUST_USE_ZERO_NATIVE")
        profile=(folder/"generated"/"profile.simc").read_text(encoding="utf8")
        planned={slot:item_id_from_profile(profile,slot)
                 for slot in {**REQUIRED_TIER,**EXPECTED_WEAPONS}}
        check(planned=={**REQUIRED_TIER,**EXPECTED_WEAPONS},
              "CORRECTED_PHYSICAL_ITEM_IDS_NOT_APPLIED")
        report.update({"status":"PREFLIGHT_4PC_INT_WEAPON_PASS",
                       "planned_item_ids":planned,
                       "profile_sha256":hashlib.sha256(
                           profile.encode("utf8")).hexdigest(),
                       "tier_slots":plan["effective_four_tier_slots"]})
        save(report_path,report)
        # Existing adaptive 6-candidate engine; NO additional Native calls.
        report["status"]="RUNNING_REAL_NATIVE"
        save(report_path,report)
        exit_code=session.worker(folder,binary,REV)
        progress=session.progress(folder)
        report["worker_exit"]=exit_code
        report["new_native_calls_confirmed"]=progress["native_attempts"]
        report["progress"]=progress
        save(report_path,report)
        check(exit_code==0,"NATIVE_WORKER_EXIT_"+str(exit_code))
        check(progress["native_attempts"]==6,"EXACT_SIX_NATIVE_REQUIRED")
        final=json.loads(session.paths(folder)["final"].read_text("utf8"))
        check(final["status"].startswith("PASS"),"FINAL_NOT_PASS")
        check(final["native_calls_cumulative"]==6,"NATIVE_COUNT_DRIFT")
        value=final["user_result"]
        check(value["confidence_level"]==0.95 and
              value["global_optimum_proven"] is False,"STATISTICS_DRIFT")
        check(value["final_T"]==value["base_B"]+
              sum(value["fixed_O"].values()),"T_B_O_DRIFT")
        report["json2_physical"]=json2_items_from_real_outputs(folder)
        hashes=session.native_json2_hashes(folder)
        check(len(hashes)==6,"SIX_JSON2_SHA_RECEIPTS_MISSING")
        report["native_json2_hashes"]=hashes
        report["observed_dps_mean"]=value["observed_first_choice"]["observed_dps_mean"]
        report["observed_sem"]=value["observed_first_choice"]["simc_sem"]
        report["observed_first_choice"]=value["observed_first_choice"]
        report["confidence_95_direction"]=value["confirmation_pair_direction_supported_at_95"]
        report["base_B"]=value["base_B"]
        report["final_T"]=value["final_T"]
        report["fixed_O"]=value["fixed_O"]
        report["status"]="RUNNING_CACHED_REPLAY"
        save(report_path,report)
        # SHA-verbatim cache-only replay. Must incur ZERO additional Native.
        cache_exit=session.worker(folder,binary,REV,cache_only=True)
        replay=json.loads(session.paths(folder)["final"].read_text("utf8"))
        check(cache_exit==0 and replay["cache_hits_this_run"]==6
              and replay["native_calls_cumulative"]==6 and
              replay["user_result"]==value and
              session.native_json2_hashes(folder)==hashes,
              "CACHE_ONLY_SHA_REPLAY_FAILED")
        report["verified_cache_hits"]=6
        report["cache_only_new_native_calls"]=0
        report["status"]="PASS_FROST_334_CORRECTED_SIX_NATIVE_SIX_CACHE"
        save(report_path,report)
        return report
    except Exception as error:
        report["status"]="FAILED_OR_BLOCKED"
        report["error"]=type(error).__name__+":"+str(error)
        report["traceback"]=traceback.format_exc(limit=5)
        save(report_path,report)
        raise

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--simc",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    args=p.parse_args(argv)
    try:
        result=run(args.simc,args.out)
        print("V185_FROST_STATUS",result["status"],flush=True)
        print("V185_FROST_DPS",result["observed_dps_mean"],flush=True)
        print("V185_FROST_SEM",result["observed_sem"],flush=True)
        print("V185_FROST_B_T_O",result["base_B"],result["final_T"],
              result["fixed_O"],flush=True)
        print("V185_FROST_NATIVE",result["new_native_calls_confirmed"],
              "CACHE",result["verified_cache_hits"],flush=True)
        return 0
    except Exception as error:
        print("V185_FROST_BLOCKED",type(error).__name__,str(error),
              file=sys.stderr,flush=True)
        return 3
if __name__=="__main__":raise SystemExit(main())
