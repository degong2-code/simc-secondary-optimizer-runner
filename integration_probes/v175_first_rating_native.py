#!/usr/bin/env python3
"""v175: ONE existing v093/v091/v092 seed on v174 physical-PASS profile.

No new optimizer, stat engine, or effect certification. The source-first v174
physical JSON2 and exact profile are REQUIRED; the old proof is never re-run
or modified. Existing v065 owns Native call/cache and v091 owns oil/stat checks.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runner"))
sys.path.insert(0,str(ROOT/"integration_probes"))
import v063_numeric_injection as numeric
import v065_original_scheduler_native_bridge as engine
import v091_weapon_oil_external_adapter as oil
import v093_inclusive_adaptive_scheduler_bridge as adaptive
import v096_unified_product_entry as entry
import v145_targeted_pure_physical_native as physical

SCHEMA="v175_existing_v093_first_seed_single_native_v1"
EXPECTED_SPEC="paladin/retribution"
EXPECTED_REV="7bc10711b5"
EXPECTED_BINARY_SHA="64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e"

class CandidateBlocked(ValueError):pass
def need(ok,why):
    if not ok:raise CandidateBlocked(why)
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def canonical(obj):
    return json.dumps(obj,sort_keys=True,ensure_ascii=False,
                      separators=(",",":"),allow_nan=False)+"\n"
def prior_physical(folder,binary,revision):
    """Confirm exactly the already successful v174 physical witness."""
    folder=pathlib.Path(folder).resolve()
    binary=pathlib.Path(binary).resolve()
    receipt=json.loads((folder/"receipt.json").read_text(encoding="utf8"))
    identity=receipt["identity"]
    need(receipt["status"]=="PASS_PHYSICAL_SIMC"
         and receipt["native_returncode"]==0
         and receipt["new_native_calls_this_run"]==1
         and receipt["spec"]==EXPECTED_SPEC
         and identity["source_first_current_season_stage"] is True,
         "V174_REAL_PHYSICAL_PASS_RECEIPT_REQUIRED")
    need(revision==EXPECTED_REV
         and identity["simc_revision"]==revision
         and identity["simc_binary_sha256"]==EXPECTED_BINARY_SHA
         and binary.is_file() and sha(binary.read_bytes())==EXPECTED_BINARY_SHA,
         "SIMC_PINNED_BINARY_IDENTITY_CHANGED")
    profile=(folder/"stage"/"profile.simc").read_bytes()
    original=(folder/"physical.simc").read_bytes()
    native=(folder/"physical.json").read_bytes()
    need(sha(profile)==identity["profile_sha256"]
         and sha(original)==identity["physical_sha256"]
         and sha(native)==receipt["json2_sha256"]
         and identity["user_sha256"]==sha((folder/"user.json").read_bytes()),
         "V174_IMMUTABLE_PROFILE_OR_JSON2_SHA_CHANGED")
    need(identity["current_season_gear_snapshot_sha256"]==
         sha(physical.bootstrap.source_first.gear.DEFAULT.read_bytes())
         and identity["current_season_tier_snapshot_sha256"]==
         sha(physical.bootstrap.source_first.TIER_PATH.read_bytes()),
         "V174_SEASON_GEAR_OR_TIER_SNAPSHOT_CHANGED")
    checked=physical.summary_from_json2(native,revision)
    need(checked["json2"]["specialization"]=="Retribution Paladin"
         and checked["json2"]["dps_mean"]>0,
         "V174_PHYSICAL_WITNESS_INVALID")
    user=json.loads((folder/"user.json").read_text(encoding="utf8"))
    need(user["target"]=={"ilevel":334,"final_T":None}
         and user["character"]["class"]=="paladin"
         and user["character"]["spec"]=="retribution"
         and user["oil_hands"]==[]
         and user["special_items"]==[]
         and user["embellishments"]==[],
         "PHYSICAL_USER_INPUT_NOT_THE_SAME")
    return folder

def prepared_request(physical_folder,binary,out,revision):
    folder=prior_physical(physical_folder,binary,revision)
    stage=folder/"stage"
    plan=entry.source(stage/"manifest.json")
    need(plan["plan"]["class"]=="paladin"
         and plan["plan"]["spec"]=="retribution"
         and plan["plan"]["base_B"]==3150
         and plan["plan"]["final_T"]==3150
         and plan["plan"]["item_slots"]==15,
         "EXISTING_V098_B_T_OR_SLOT_CONTRACT_CHANGED")
    need(plan["manifest"].get(entry.STAGE_FIELD) is True,
         "SOURCE_FIRST_UNVERIFIED_STAGE_SEAL_LOST")
    B=plan["plan"]["base_B"]
    need(len(plan["seeds"])==2
         and sum(plan["seeds"][0].values())==B
         and sum(plan["flask"].values())==165
         and sum(plan["context"]["identity"]["oil_vector"].values())==0,
         "SEED_F_OR_NO_OIL_DRIFT")
    output=pathlib.Path(out).resolve()/"seed_00"
    request=adaptive.request(plan["context"],plan["seeds"][0],
                 plan["flask"],output/"result.json",phase="seed")
    need(request["iterations"]==35 and request["v092_base_B"]==B
         and request["v092_final_T"]==B
         and request["v092_base_target"]==plan["seeds"][0]
         and all(x==0 for x in request["v092_fixed_O"].values()),
         "EXACT_FIRST_SEED_NOT_V175_SCOPE")
    bound=numeric.input_parts((stage/"profile.simc").read_text(encoding="utf8"),
                              allow_missing_json2_template=True)
    actual=numeric.input_parts(request["input"])
    need(actual["stable_sha256"]==bound["stable_sha256"]
         and request["profile_stable_sha256"]==bound["stable_sha256"]
         and all(request["raw_gear_override"][k]+plan["flask"][k]==
                 request["target"][k] for k in numeric.STATS),
         "INPUT_CHANGED_BEYOND_STATIC_C_OR_F")
    return output,request

def run(physical_folder,binary,out,*,revision=EXPECTED_REV,max_new=0):
    need(type(max_new) is int and max_new in (0,1),
         "NATIVE_CAP_MUST_BE_ZERO_OR_ONE")
    output,request=prepared_request(physical_folder,binary,out,revision)
    cache=(output/"result.json").is_file() or (output/"native_receipt.json").is_file()
    if max_new==0 and not cache:
        return {"schema":SCHEMA,"status":"PLAN_ONLY_ZERO_NATIVE",
          "new_native_calls":0,"target":request["target"],
          "base_B":request["v092_base_B"],"final_T":request["v092_final_T"],
          "fixed_O":request["v092_fixed_O"],
          "flask_F":request["static_flask_F_vector"],
          "profile_stable_sha256":request["profile_stable_sha256"],
          "input_sha256":request["input_sha256"],
          "native_physical_witness_reused":True,
          "user_optimizer_ready":False}
    progress={"native_attempts":0,"status":"PREPARED"}
    obs=engine.execute_one(request,{"native_revision":revision},binary,
            output,progress,cache_only=(max_new==0))
    raw=(output/"result.json").read_bytes()
    extra=oil.ingest_native(request,json.loads(raw),raw)
    need(obs["native_json_sha256"]==extra["native_json_sha256"]
         and obs["static_rating_verified"]==request["target"]
         and extra["static_rating_verified"]==request["target"]
         and extra["oil_reported_by_native"]=="disabled"
         and extra["total_T_including_O"]==3150,
         "EXISTING_NATIVE_STATIC_C_O_OR_JSON2_CONSISTENCY_DRIFT")
    result={"schema":SCHEMA,"status":"PASS_ONE_STATIC_RATING_NATIVE"
            if obs["source"]=="NEW_NATIVE" else "CACHED_VERIFIED_STATIC_RATING_NATIVE",
         "new_native_calls":1 if obs["source"]=="NEW_NATIVE" else 0,
         "target_static_CHMV":dict(request["target"]),
         "native_verified_static_CHMV":dict(extra["static_rating_verified"]),
         "raw_gear_override":dict(request["raw_gear_override"]),
         "base_B":request["v092_base_B"],"final_T":request["v092_final_T"],
         "fixed_O":request["v092_fixed_O"],"flask_F":request["static_flask_F_vector"],
         "iterations":request["iterations"],"dps_mean":extra["dps_mean"],
         "dps_sem":extra["dps_sem"],"dps_samples":extra["dps_samples"],
         "buffed_stats_native":extra["rating_actual"],
         "binary_sha256":request["simc_binary_sha256"],
         "profile_stable_sha256":request["profile_stable_sha256"],
         "native_json_sha256":obs["native_json_sha256"],
         "native_physical_witness_reused":True,
         "native_effects_owned_by_simc":True,
         "user_optimizer_ready":False,"95_percent_winner_proven":False}
    summary=pathlib.Path(out).resolve()/"V175_RESULT.json"
    summary.write_text(canonical(result),encoding="utf8")
    return result

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--v174-physical",required=True,type=pathlib.Path)
    p.add_argument("--simc",required=True,type=pathlib.Path)
    p.add_argument("--out",required=True,type=pathlib.Path)
    p.add_argument("--revision",default=EXPECTED_REV)
    p.add_argument("--max-new",type=int,choices=(0,1),default=0)
    a=p.parse_args(argv)
    try:
        result=run(a.v174_physical,a.simc,a.out,
                   revision=a.revision,max_new=a.max_new)
        print(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2))
        return 0
    except Exception as exc:
        print("V175_BLOCKED:",type(exc).__name__,str(exc),file=sys.stderr)
        return 3
if __name__=="__main__":raise SystemExit(main())
