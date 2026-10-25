#!/usr/bin/env python3
"""v063: one bounded official-T native proof on existing 334 Arcane reference.

Loads prior v059 Native JSON2 as independent numeric witnesses, derives G
from the already executed Native gear static rows, builds v061/v062 contracts,
and evaluates at most two CHMV vectors in SimC. No proc/effect interpretation.
This is NOT a generic cross-spec product runner or original v016 merge.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,subprocess,sys

import v046_static_item_cache as itemcache
import v061_scenario_contract as scenario
import v062_static_budget_bridge as budget
import v063_numeric_injection as inject

BINARY_SHA="64089f2f917d552ab392ba311d128aa1b7ec559ead52b3546e2cc328ab479b8e"
TRIAL_TARGETS=[
  {"crit_rating":600,"haste_rating":1108,"mastery_rating":1115,"versatility_rating":329},
  {"crit_rating":750,"haste_rating":958,"mastery_rating":1115,"versatility_rating":329}]
TIER_SLOTS=("head","shoulders","chest","legs")
BUDGET_J=138
BUDGET_F=165
OIL_EXTERNAL={"crit_rating":16,"haste_rating":16,"mastery_rating":0,"versatility_rating":0}

def need(ok,msg):
    if not ok:raise inject.InjectionError(msg)

def parse_source_equip(source):
    import v055_simc_item_selection as selector
    equip={}
    for line in source.splitlines():
        key,sep,value=line.partition("=")
        if sep and key in selector.SLOTS:
            name,opts=itemcache.parse_encoded(value)
            equip[key]={"slot":key,"item_id":int(opts.pop("id")),
                        "ilevel":int(opts.pop("ilevel")),
                        "options":{k:v for k,v in opts.items() if k!="source"}}
    need(len(equip)==15,"REFERENCE_EXPECTED_15_EQUIPMENT_INPUTS")
    return equip

def scenario_for_bounded_reference(reference):
    """Exact v031r3/v059 test scenario; all IDs from actual Native input."""
    rows=parse_source_equip(reference)
    src={}
    for line in reference.splitlines():
        if "=" in line and not line.startswith("#"):
            k,_,v=line.partition("=")
            if k not in src:src[k]=v
    need("mage" in src and src.get("spec")=="arcane"
         and src.get("race")=="dwarf" and src.get("role")=="spell",
         "THIS_BOUNDED_SCENARIO_IS_ARCANE_MAGE_ONLY")
    need({r["ilevel"] for r in rows.values()}=={334},"PINNED_334_INPUT_REQUIRED")
    consume=src.get("temporary_enchant")
    need(consume=="main_hand:thalassian_phoenix_oil_2","OIL_REFERENCE_CHANGED")
    need(src.get("flask")=="flask_of_the_blood_knights_2",
         "FLASK_REFERENCE_CHANGED")
    need(src.get("food")=="royal_roast" and src.get("fight_style")=="Patchwerk"
         and src.get("desired_targets")=="1" and src.get("max_time")=="300"
         and src.get("optimal_raid")=="1","COMBAT_REFERENCE_CHANGED")
    used=set(TIER_SLOTS)|{"trinket1","trinket2"}
    crafted=[r for r in rows.values() if "embellishment" in r["options"]]
    need(len(crafted)==2 and {r["slot"] for r in crafted}=={"back","wrists"},
         "EXPECTED_2_REPRESENTATIVE_CRAFTS")
    used|={r["slot"] for r in crafted}
    chosen_tier=[rows[x] for x in TIER_SLOTS]
    chosen_trinkets=[rows[x] for x in ("trinket1","trinket2")]
    filler=[rows[x] for x in rows if x not in used]
    request={
      "schema":scenario.SCHEMA,
      "character":{"class":"mage","spec":src["spec"],"race":src["race"],
                   "talents":src["talents"],"role":src["role"]},
      "source":{"kind":"simc_standard","profile_sha256":None},
      "target":{"mode":"derived_ilevel","ilevel":334,"manual_total":None,
                "manual_total_scope":None},
      "equipment":{"tier":chosen_tier,"special":[],"crafted":crafted,
                   "trinkets":chosen_trinkets},
      "consumables":{"gem_budget_J":BUDGET_J,"flask_budget_F":BUDGET_F,
          "special_gem_id":240967,"flask":src["flask"],"food":src["food"],
          "potion":None,"weapon_temporary":"thalassian_phoenix_oil_2",
          "weapon_temporary_fixed_rating":OIL_EXTERNAL},
      "combat":{"fight_style":src["fight_style"],"targets":1,
         "duration_seconds":300,"vary_combat_length_pct":0.,
         "raid_buffs":True,"bloodlust":"simc_default",
         "external_buffs":[],"events":[]},
      "constraints":{"min_fraction":{k:0. for k in scenario.STATS},
           "max_fraction":{k:0.5 for k in scenario.STATS},
           "minimum_rating":{k:0 for k in scenario.STATS}},
      "runtime":{"scout_iterations":60,"confirm_iterations":60,
         "max_native_calls":2,"threads":1,"resume":True,"seed":None}
    }
    return scenario.normalize(request),filler

def read_evidence(dir_path):
    evidence=[]
    for suffix in ("00","01"):
        path=dir_path/("case_"+suffix)
        evidence.append({"input":(path/"input.simc").read_text(),
                         "native":json.loads((path/"result.json").read_text())})
    return evidence

def plan_from_previous(evidence):
    need(len(evidence)==2,"REQUIRE_TWO_PREVIOUS_REAL_JSON2")
    calibration=inject.calibrate(evidence)
    native_json=evidence[0]["native"]
    native_records=itemcache.native_records(
       json.dumps(native_json,sort_keys=True).encode("utf8"),
       artifact_id="V063_REUSE_EXISTING_V059_JSON2")
    local=itemcache.empty_cache()
    itemcache.merge_native(local,native_records)
    contract,filler=scenario_for_bounded_reference(evidence[0]["input"])
    static=budget.compile_static_budget(contract,filler,local)
    need(static["G_if_complete"]==2849 and
         static["budget"]["T_official"]==3152,
         "PINNED_NATIVE_G_OR_OFFICIAL_T_CHANGED")
    need(static["budget"]["ambiguous_gem_enchant_gear_rows"],
         "THIS_PROFILE_HAS_MODIFIER_ATTRIBUTION_TO_KEEP_EXPLICIT")
    need(calibration["net_input_to_json2_rating_offset"]==
         {"crit_rating":0,"haste_rating":165,"mastery_rating":0,"versatility_rating":0},
         "PINNED_MEASURED_NUMERIC_OFFSET_CHANGED")
    for target in TRIAL_TARGETS:inject.check_target(contract,static,target)
    return {"contract":contract,"static":static,"calibration":calibration,
            "reference":evidence[0]["input"]}

def execute(previous,out,binary=None,iterations=60):
    out.mkdir(parents=True,exist_ok=True)
    report={"schema":"v063_official_numeric_injection_pilot_v1","status":"BLOCKED",
            "native_calls_attempted":0,"official_policy":"T=G+J+F",
            "SimC_owns_items_APL_DPS":True,
            "independent_proc_effect_gate":False,
            "original_product_v016_integrated":False}
    try:
        data=plan_from_previous(read_evidence(previous))
        calib=data["calibration"];contract=data["contract"];static=data["static"]
        report.update({"status":"NUMERIC_PLAN_CREATED","G_native":static["G_if_complete"],
           "J":contract["budget"]["J"],"F":contract["budget"]["F"],
           "T_official":static["budget"]["T_official"],
           "external_oil_fixed_not_added_to_T":OIL_EXTERNAL,
           "measured_net_gear_to_json2_offset":calib["net_input_to_json2_rating_offset"],
           "reference_stable_profile_sha256":calib["stable_profile_sha256"],
           "static_attribution_flags":static["budget"]["ambiguous_gem_enchant_gear_rows"],
           "numeric_injection_not_all_external_attribution_proof":True,
           "candidates":[]})
        (out/"V063_PROGRESS.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
        need(30<=iterations<=120,"BOUNDED_ITERATIONS_ONLY")
        if binary is None:
            report["status"]="PASS_OFFLINE_NUMERIC_PLAN_NO_NATIVE_CALLS"
        else:
            need(binary.is_file() and hashlib.sha256(binary.read_bytes()).hexdigest()==BINARY_SHA,
                 "SIMC_BINARY_PIN_MISMATCH")
            for i,target in enumerate(TRIAL_TARGETS):
                case=out/("case_%02d"%i);case.mkdir(exist_ok=True)
                native_path=case/"result.json"
                rendered=inject.render_candidate(data["reference"],calib,
                                                   target,native_path,iterations)
                srcpath=case/"input.simc"
                key=itemcache.digest({"scenario":contract["scenario_digest"],
                    "input_stable":calib["stable_profile_sha256"],
                    "native_binary_sha":BINARY_SHA,"calibrated_revision":calib["native_revision"],
                    "target":target,"iterations":iterations})
                prior=case/"RESULT_RECEIPT.json"
                if prior.exists() and native_path.exists():
                    old=json.loads(prior.read_text())
                    need(old.get("case_key")==key
                         and old.get("input_sha256")==rendered["input_sha256"]
                         and old.get("native_json_sha256")==hashlib.sha256(native_path.read_bytes()).hexdigest(),
                         "PERSISTED_RESULT_IDENTITY_CONFLICT")
                    result=inject.validate_native(json.loads(native_path.read_text()),rendered,calib)
                    result["source"]="CACHED_VERIFIED_NATIVE"
                else:
                    srcpath.write_text(rendered["input"],encoding="utf8")
                    report["native_calls_attempted"]+=1
                    (out/"V063_PROGRESS.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
                    p=subprocess.run([str(binary),str(srcpath)],cwd=binary.parent,
                      stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,timeout=180)
                    (case/"stdout.txt").write_bytes(p.stdout)
                    (case/"stderr.txt").write_bytes(p.stderr)
                    need(p.returncode==0,
                         "SIMC_NATIVE_EXIT_"+str(p.returncode)+"; SEE STDERR_UNMODIFIED")
                    need(native_path.is_file(),"SIMC_NATIVE_JSON2_NOT_CREATED")
                    result=inject.validate_native(json.loads(native_path.read_text()),rendered,calib)
                    result["source"]="NEW_NATIVE"
                    receipt=result | {
                       "case_key":key,"input_sha256":rendered["input_sha256"],
                       "native_json_sha256":hashlib.sha256(native_path.read_bytes()).hexdigest()}
                    prior.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
                report["candidates"].append(result)
            report["comparison"]=inject.compare_pair(report["candidates"])
            report["status"]="PASS_TWO_REAL_NATIVE_OFFICIAL_T_3152_JSON2_RATING"
    except Exception as exc:
        report["status"]="BLOCKED_OR_PARTIAL"
        report["error"]=type(exc).__name__+":"+str(exc)
    (out/"V063_RECEIPT.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("V063",report["status"],"calls",report["native_calls_attempted"],flush=True)
    return 0 if report["status"].startswith("PASS") else 3

def main():
    args=argparse.ArgumentParser()
    args.add_argument("--previous-v059",type=pathlib.Path,required=True)
    args.add_argument("--out",type=pathlib.Path,required=True)
    args.add_argument("--binary",type=pathlib.Path)
    args.add_argument("--iterations",type=int,default=60)
    x=args.parse_args()
    return execute(x.previous_v059.resolve(),x.out.resolve(),
                  x.binary.resolve() if x.binary else None,x.iterations)

if __name__=="__main__":sys.exit(main())
