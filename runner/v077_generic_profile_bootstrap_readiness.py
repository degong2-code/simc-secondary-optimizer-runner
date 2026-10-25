#!/usr/bin/env python3
"""v077: profile-neutral first-use readiness + bounded two-witness input plan.

Consumes exact caller-supplied SimC profile, scenario, actual selected gear and
same-season native static cache. No inventory recommendation, no full item DB,
no APL/proc or weapon legality model. Generates INPUT ONLY, never Native PASS.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import sys

import v046_static_item_cache as cache
import v055_simc_item_selection as items
import v061_scenario_contract as contract
import v062_static_budget_bridge as budget
import v063_numeric_injection as numeric
import v064_adaptive_evaluator_port as evaluator
import v065_original_scheduler_native_bridge as engine

SCHEMA="v077_generic_profile_bootstrap_readiness_v1"
BOOT_ITERATIONS=35
TRANSFER=50

class ReadinessBlocked(ValueError):
    pass

def need(x,reason):
    if not x:
        raise ReadinessBlocked(reason)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def input_item_map(normalized,standard,profile):
    """Exact source→scenario binding before P2 cache is complete.

    Unlike a gear compatibility engine this checks only user-selected input
    and slot identity; whether an item is equipable is SimC's responsibility.
    """
    cfg=normalized["scenario"]
    selected=sum((cfg["equipment"][k] for k in
                  ("tier","special","crafted","trinkets")),[])
    expected={r["slot"]:r for r in selected+standard}
    settings={}
    active=set(expected)
    for line in profile.splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        key,value=line.split("=",1)
        if key in active:
            need(key not in settings,"DUPLICATE_EQUIPMENT_ROW:"+key)
            _,encoded=cache.parse_encoded(value)
            actual={"slot":key,"item_id":int(encoded["id"]),
                    "ilevel":int(encoded["ilevel"]),
                    "options":{k:v for k,v in encoded.items()
                               if k not in ("id","ilevel","source")}}
            need(actual==expected[key],"EXACT_ITEM_VARIANT_MISMATCH:"+key)
            settings[key]=value
    need(set(settings)==active,"PROFILE_GEAR_SLOTS_MISSING_OR_ADDED")
    # Exclude actions+= commands: APL append can correctly repeat.
    ordinary={}
    for line in profile.splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        key,value=line.split("=",1)
        if key.startswith("actions") or key in active:
            continue
        need(key not in ordinary,"DUPLICATE_PROFILE_OPTION:"+key)
        ordinary[key]=value
    char=cfg["character"]
    need(any(line.startswith(char["class"]+"=")
             for line in profile.splitlines()),"PROFILE_CLASS_DRIFT")
    for k in ("spec","race","role","talents"):
        need(ordinary.get(k)==char[k],"PROFILE_CHARACTER_DRIFT:"+k)
    combat=cfg["combat"]
    for k,v in (("fight_style",combat["fight_style"]),
                ("desired_targets",str(combat["targets"])),
                ("max_time",str(combat["duration_seconds"])),
                ("optimal_raid","1" if combat["raid_buffs"] else "0")):
        need(ordinary.get(k)==v,"PROFILE_COMBAT_DRIFT:"+k)
    for k in ("flask","food"):
        val=cfg["consumables"][k]
        if val is not None:
            need(ordinary.get(k)==val,"PROFILE_CONSUMABLE_DRIFT:"+k)
    return {"exact_item_slots":len(settings),
            "trinkets_present":all(k in settings for k in ("trinket1","trinket2")),
            "profile_character_and_combat_matched":True,
            "item_eligibility_delegated_to_simc":True}

def paired_input(reference,folder,iterations=BOOT_ITERATIONS,transfer=TRANSFER):
    """Generate two RAW gear_* variants with identical total for first-use calibration.

    Raw profile rating totals need not yet equal official JSON2 total: the
    native offset must be measured. Do not call these official P3 targets.
    """
    need(type(iterations) is int and 30<=iterations<=100000,
         "BOOT_ITERATIONS_OUTSIDE_P3")
    need(type(transfer) is int and 1<=transfer<=1000,
         "INVALID_TRANSFER")
    root=pathlib.Path(folder)
    parts=numeric.input_parts(reference)
    raw=parts["gear_override"]
    donors=sorted((k for k in contract.STATS if raw[k]>=transfer),
                  key=lambda k:(-raw[k],k))
    need(bool(donors),"NO_GEARRATING_DONOR_FOR_SECOND_WITNESS")
    donor=donors[0]
    recipient=next(k for k in contract.STATS if k!=donor)
    other=dict(raw)
    other[donor]-=transfer
    other[recipient]+=transfer
    need(sum(raw.values())==sum(other.values()),
         "BOOT_PROFILE_RATING_TOTAL_DRIFT")
    rows=[]
    for i,values in enumerate((raw,other)):
        destination=(root/("case_%02d"%i)/"result.json").resolve()
        lines=[]
        for line in reference.splitlines():
            key,sep,_=line.partition("=")
            field=key.removeprefix("gear_")
            if sep and field in contract.STATS and key.startswith("gear_"):
                line=key+"="+str(values[field])
            elif key=="iterations":
                line="iterations="+str(iterations)
            elif key=="json2":
                line="json2="+str(destination)
            lines.append(line)
        source="\n".join(lines)+"\n"
        generated=numeric.input_parts(source)
        need(generated["stable_sha256"]==parts["stable_sha256"]
             and generated["gear_override"]==values,
             "BOOT_PROFILE_STABLE_IDENTITY_DRIFT")
        rows.append({"index":i,"input":source,
                     "input_sha256":sha(source.encode("utf8")),
                     "raw_rating":values,"iterations":iterations,
                     "intended_json2_path":str(destination),
                     "stable_profile_sha256":parts["stable_sha256"]})
    return rows

def prepare(scenario_doc,fillers,cache_doc,profile,folder):
    normalized=contract.normalize(scenario_doc)
    need(type(profile) is str and len(profile)>0,
         "PROFILE_SOURCE_REQUIRED")
    if scenario_doc["source"]["kind"]=="user_supplied":
        need(sha(profile.encode("utf8"))==scenario_doc["source"]["profile_sha256"],
             "USER_SOURCE_PROFILE_SHA_CHANGED")
    standard=budget.check_filler(fillers,
             sum((normalized["scenario"]["equipment"][x] for x in
                  ("tier","special","crafted","trinkets")),[]))
    item_binding=input_item_map(normalized,standard,profile)
    present=budget.compile_static_budget(normalized,fillers,cache_doc)
    inputs=paired_input(profile,folder)
    need(present["budget"]["oil_stays_OUTSIDE_T"] is True
         and present["budget"]["official_formula"]=="T=G+J+F",
         "OFFICIAL_BUDGET_POLICY_CHANGED")
    # Manual totals can appear despite unresolved native G and must never be
    # interpreted as native-static-validated official optimization readiness.
    missing=present["missing_nontrinket_static"]
    locked_missing=present["missing_special_fixed_static"]
    ready=(not missing and not locked_missing and
           present["G_if_complete"] is not None and
           present["budget"]["T_official"] is not None and
           present["effective_floor_if_possible"] is not None)
    if ready:
        # v064 verification reuses the real Native-derived cache, never a fake
        # placeholder for non-trinket stats.
        binding=evaluator.verify_profile_binding(normalized,present,profile)
        need(binding["two_trinkets_bound"],"TRINKET_BINDING_CHANGED")
    else:
        binding=None
    unique_missing={cache.digest(x["identity"]):x["identity"]
                    for x in missing}
    return {"schema":SCHEMA,
       "status":("READY_FOR_TWO_NATIVE_CALIBRATION_WITNESSES"
                 if ready else "BLOCKED_EXACT_NATIVE_STATIC_VARIANTS_MISSING"),
       "normalized_scenario_digest":normalized["scenario_digest"],
       "class":normalized["scenario"]["character"]["class"],
       "spec":normalized["scenario"]["character"]["spec"],
       "race":normalized["scenario"]["character"]["race"],
       "profile_sha256":sha(profile.encode("utf8")),
       "stable_profile_sha256":inputs[0]["stable_profile_sha256"],
       "source_kind":scenario_doc["source"]["kind"],
       "selected_and_filler_binding":item_binding,
       "full_native_static_binding":binding,
       "G_native_if_complete":present["G_if_complete"],
       "T_official_if_available":present["budget"]["T_official"],
       "J":normalized["budget"]["J"],"F":normalized["budget"]["F"],
       "locked_special_L_if_complete":
                       present["locked_L_when_all_specials_observed"],
       "missing_exact_native_variant_count":len(unique_missing),
       "missing_exact_native_variant_identities":list(unique_missing.values()),
       "trinket_static_missing_does_not_block":True,
       "profile_scoped_two_native_witnesses_required":True,
       "numeric_offset_known":False,
       "two_native_witness_inputs":[{
          "index":x["index"],"input_sha256":x["input_sha256"],
          "raw_rating":x["raw_rating"],"iterations":x["iterations"],
          "intended_json2_path":x["intended_json2_path"],
          "stable_profile_sha256":x["stable_profile_sha256"]}
          for x in inputs],
       "calibration_inputs_generated_but_NOT_executed":True,
       "native_success_claimed":False,
       "stat_cache_revision_invalidation":False,
       "new_native_calls":0,
       "game_effects_and_APL_owned_by":"SimC",
       "official_budget_formula":"T=G+J+F",
       "global_optimum_proven":False}

def run(scenario_file,filler_file,cache_file,profile_file,out):
    # Read-only source/cache: only store a bounded proposal. An incomplete
    # native-stat profile may still have input plans, but must not be run by
    # generic v067 as if official budget/calibration were already verified.
    out=pathlib.Path(out)
    target=out/"V077_BOOTSTRAP_READINESS.json"
    result={"schema":SCHEMA,"status":"BLOCKED_NO_NATIVE",
            "new_native_calls":0}
    try:
        scenario_doc=json.loads(pathlib.Path(scenario_file).read_text(encoding="utf8"))
        fillers=json.loads(pathlib.Path(filler_file).read_text(encoding="utf8"))
        stored=cache.load(pathlib.Path(cache_file))
        profile=pathlib.Path(profile_file).read_text(encoding="utf8")
        planned=paired_input(profile,out/"witnesses")
        result=prepare(scenario_doc,fillers,stored,profile,out/"witnesses")
        # Never overwrite prior input or Native evidence: rerunning requires
        # an empty output directory or byte-for-byte identical inputs.
        for entry in planned:
            directory=out/"witnesses"/("case_%02d"%entry["index"])
            source_path=directory/"input.simc"
            need(not (directory/"result.json").exists(),
                 "NATIVE_JSON2_ALREADY_PRESENT_USE_REAL_WITNESS_IMPORT")
            need(not (directory/"native_receipt.json").exists(),
                 "PREEXISTING_NATIVE_RECEIPT_REFUSED")
            if source_path.exists():
                need(source_path.read_bytes()==entry["input"].encode("utf8"),
                     "PREEXISTING_BOOTSTRAP_SOURCE_CHANGED")
            else:
                directory.mkdir(parents=True,exist_ok=True)
                source_path.write_text(entry["input"],encoding="utf8")
    except Exception as exc:
        result={"schema":SCHEMA,"status":"BLOCKED_NO_NATIVE",
                "error":type(exc).__name__+":"+str(exc),
                "new_native_calls":0}
    engine.write_atomic(target,result)
    print("V077",result["status"],"native",0,flush=True)
    return 0 if result["status"]=="READY_FOR_TWO_NATIVE_CALIBRATION_WITNESSES" else 3

def main(argv=None):
    p=argparse.ArgumentParser()
    for name in ("scenario","filler","static-cache","profile","out"):
        p.add_argument("--"+name,required=True,type=pathlib.Path)
    x=p.parse_args(argv)
    return run(x.scenario,x.filler,x.static_cache,x.profile,x.out)

if __name__=="__main__":
    sys.exit(main())
