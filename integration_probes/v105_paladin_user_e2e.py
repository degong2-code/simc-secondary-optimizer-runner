#!/usr/bin/env python3
"""v105 minimal real end-to-end acceptance: one existing Retribution Paladin.

Use only the existing v098 -> v096 -> v094 pipeline. Fixed source-backed
trinkets/talents are a deterministic INPUT EXAMPLE, not a new item database or
optimization algorithm. Exact Native SHA is independently checked in workflow.
Each new session is bounded by six Native requests, replay is cache-only.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,re,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"runner"))
import v098_target_user_scenario_bootstrap as userflow
import v096_unified_product_entry as entry

SCHEMA="v105_paladin_one_full_user_journey_v1"
SOURCE_KEY=("paladin","retribution")
REFERENCE_BINARY_SHA="64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e"
REFERENCE_REV="7bc10711b5"
STATS=("crit_rating","haste_rating","mastery_rating","versatility_rating")

def need(ok,reason):
    if not ok:raise ValueError("V105_"+reason)

def sample_user():
    """User-facing controls only; no hand-authored profile/fillers/seeds."""
    filename=userflow.ARCHETYPES[SOURCE_KEY][0]
    source=(userflow.FIXTURES/filename).read_text(encoding="utf8")
    talents=[r.partition("=")[2] for r in source.splitlines()
             if r.startswith("talents=")]
    need(len(talents)==1,"TALENTS_SOURCE_AMBIGUOUS")
    trinkets=[]
    for slot in ("trinket1","trinket2"):
        lines=[x for x in source.splitlines() if x.startswith(slot+"=")]
        need(len(lines)==1,"TRINKET_SOURCE_AMBIGUOUS:"+slot)
        m=re.search(r"(?:^|,)id=([1-9][0-9]*)(?:,|$)",lines[0])
        need(m is not None,"TRINKET_ID_ABSENT:"+slot)
        trinkets.append({"slot":slot,"item_id":int(m.group(1)),
                         "options":{}})
    return {"schema":userflow.SCHEMA,
            "character":{"class":"paladin","spec":"retribution",
                         "race":"blood_elf","talents":talents[0]},
            "target":{"ilevel":334,"final_T":None},
            "trinkets":trinkets,
            "special_items":[],"embellishments":[],
            "oil_hands":["main_hand"],
            "combat":{"targets":1,"duration_seconds":300,
                      "raid_buffs":True}}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def native_hashes(output):
    # Do not include auxiliary summaries/receipts in immutable Native hashes.
    return {str(p.relative_to(output)):sha(p.read_bytes())
            for p in sorted(output.rglob("result.json"))}

def check_plan(plan):
    need(plan["class"]=="paladin" and plan["spec"]=="retribution",
         "CLASS_OR_SPEC_DRIFT")
    need((plan["base_B"],plan["final_T"])==(3150,3182),
         "DEFAULT_334_B_O_T_DRIFT")
    need(plan["fixed_O"]=={"crit_rating":32,"haste_rating":0,
                           "mastery_rating":0,"versatility_rating":0},
         "OIL_FIXED_VECTOR_DRIFT")
    need(plan["item_slots"]==15,"PALADIN_PHYSICAL_SLOTS_DRIFT")
    need((plan["native_min_calls"],plan["native_limit"])==(6,6),
         "MAX_SIX_NATIVE_CONTRACT_DRIFT")
    need(not plan["native_called"],"PLAN_CALLED_NATIVE")

def check_user_result(data):
    need(data["status"].startswith("PASS"),
         "RUN_NOT_COMPLETED")
    need((data["base_B"],data["final_T"])==(3150,3182),
         "NATIVE_B_O_T_DRIFT")
    r=data["user_result"]
    need(r["confidence_level"]==0.95 and not r["global_optimum_proven"],
         "95_ONLY_AND_NO_GLOBAL_PROOF")
    need(r["confirmation_scope"]==
         "TWO_FRESH_SELECTED_CANDIDATES_ONLY_NOT_GLOBAL",
         "CONFIRMATION_SCOPE_DRIFT")
    best=r["observed_first_choice"]
    need(sum(best["absolute_rating_T"].values())==3182 and
         sum(best["base_rating_B"].values())==3150 and
         best["absolute_rating_T"]["crit_rating"]-
         best["base_rating_B"]["crit_rating"]==32,
         "OBSERVED_ABSOLUTE_RATING_O_DRIFT")
    need(best["observed_dps_mean"]>0 and best["simc_sem"]>=0,
         "NATIVE_DPS_SEM_MISSING")
    need(r["observed_unique_candidates"]>=2,
         "TOO_FEW_OBSERVED_CANDIDATES")
    for alt in r["material_near_alternatives"]:
        need(sum(alt["absolute_rating_T"].values())==3182 and
             alt["pairwise_95_label"] in (
               "OBSERVED_NEAR_BUT_LOWER_AT_95",
               "OBSERVED_NEAR_UNRESOLVED_AT_95"),
             "ALTERNATIVE_95_SCOPE_DRIFT")
    return best

def run(out,binary,*,execute=False,cache_replay=False):
    out=pathlib.Path(out).resolve()
    binary=pathlib.Path(binary).resolve()
    need(binary.is_file(),"SIMC_BINARY_NOT_FOUND")
    # Only the real Native mode requires this historical binary identity.
    if execute:
        need(sha(binary.read_bytes())==REFERENCE_BINARY_SHA,
             "PINNED_SIMC_ELF_SHA_MISMATCH")
    source=sample_user()
    out.mkdir(parents=True,exist_ok=True)
    user_path=out/"USER_SETTINGS.json"
    if user_path.exists():
        need(json.loads(user_path.read_text(encoding="utf8"))==source,
             "USER_SETTINGS_DRIFT")
    else:user_path.write_text(json.dumps(source,indent=2,ensure_ascii=False)+"\n",
                              encoding="utf8")
    prepared=userflow.build(source,out/"generated",binary,REFERENCE_REV)
    plan=prepared["plan"]
    check_plan(plan)
    need(prepared["effective_four_tier_slots"]==[
         "chest","hands","head","shoulders"],"TIER_4_SLOTS_DRIFT")
    need(prepared["native_calls"]==0,"PREPARE_CALLED_NATIVE")
    receipt={"schema":SCHEMA,"stage":"PLAN_ONLY" if not execute else
             "RUNNING_NATIVE","native_input_count_max":6,
             "plan":plan,"generated_manifest":prepared["generated_manifest"],
             "binary_sha256":sha(binary.read_bytes()),
             "user_inputs_omit_full_gear":True,
             "native_calls_completed_here":0}
    (out/"V105_PLAN_RECEIPT.json").write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False,sort_keys=True)+"\n",
        encoding="utf8")
    if not execute:return receipt
    manifest=pathlib.Path(prepared["generated_manifest"])
    fresh=entry.run_manifest(manifest)
    best=check_user_result(fresh)
    need(fresh["native_calls_cumulative"]==6,
         "NATIVE_CALLS_NOT_EXACT_SIX")
    result_path=pathlib.Path(fresh["result_path"])
    raw=entry.read_object(result_path)
    need(raw["status"].startswith("PASS") and
         len(raw["observations"])==6 and
         raw["new_native_attempts_cumulative"]==6,
         "DURABLE_OBSERVATIONS_OR_LEDGER_MISSING")
    before=native_hashes(result_path.parent)
    need(len(before)==6,"SIX_JSON2_NATIVE_RESULTS_REQUIRED")
    follow=None
    if cache_replay:
        follow=entry.run_manifest(manifest,cache_only=True)
        check_user_result(follow)
        need(follow["cache_hits_this_run"]==6 and
             follow["native_calls_cumulative"]==6,
             "CACHE_ONLY_REPLAY_DID_NOT_REUSE_SIX")
        need(native_hashes(result_path.parent)==before,
             "CACHED_NATIVE_REPORT_BYTES_CHANGED")
    progress=entry.read_object(result_path.parent/"V094_PROGRESS.json")
    need(progress["status"].startswith("PASS") and
         progress["progress_percent"]==100.0,
         "PROGRESS_NOT_COMPLETE")
    receipt.update({
        "stage":"PASS_REAL_USER_TO_NATIVE_TO_95_RESULT",
        "native_calls_completed_here":6,
        "native_json2_sha256":before,
        "native_cache_verified_hits_in_replay":
            follow["cache_hits_this_run"] if follow else None,
        "observed_dps_mean":best["observed_dps_mean"],
        "observed_sem":best["simc_sem"],
        "observed_95_pairwise_supported":
            fresh["user_result"]["confirmation_pair_direction_supported_at_95"],
        "alternatives_count":len(fresh["user_result"]["material_near_alternatives"]),
        "global_optimum_proven":False,
        "final_T":3182,"base_B":3150,
        "progress_percent":progress["progress_percent"],
        "actual_native_result":str(result_path),
        "replay_verified_no_new_native":bool(follow)})
    (out/"V105_REAL_E2E_RECEIPT.json").write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False,sort_keys=True)+"\n",
        encoding="utf8")
    return receipt

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True,type=pathlib.Path)
    ap.add_argument("--binary",required=True,type=pathlib.Path)
    ap.add_argument("--execute",action="store_true")
    ap.add_argument("--cache-replay",action="store_true")
    opt=ap.parse_args()
    try:
        print(json.dumps(run(opt.out,opt.binary,execute=opt.execute,
                             cache_replay=opt.cache_replay),
                         indent=2,sort_keys=True))
        return 0
    except Exception as e:
        print("V105_BLOCKED:",type(e).__name__,str(e),file=sys.stderr)
        return 3
if __name__=="__main__":sys.exit(main())
